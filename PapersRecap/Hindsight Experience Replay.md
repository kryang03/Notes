---
tags:
  - paper
  - reinforcement-learning
  - sparse-reward
  - exploration
aliases:
  - HER
paper-year: 2017
read-date: 2026-02-02
venue: NeurIPS
paper-pdf: "[[Papers/Hindsight Experience Replay.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
---

# Hindsight Experience Replay

> [!abstract] 核心贡献
> HER 把失败轨迹重新解释为“成功完成了另一个 goal”的 off-policy replay 样本：只要环境 dynamics 不依赖 goal，且存在从 achieved state 到 goal 的映射 $m:S\to G$，同一条轨迹就可以用多个 relabeled goals 重新计算 sparse binary reward，从而让 DDPG/DQN 在几乎没有原始成功样本时仍能学习 goal-conditioned policy。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]]：HER 是 UVFA/goal-conditioned value function $Q(s,a,g)$ 与 off-policy replay 的组合。
> - [[Optimization]]：HER 形成隐式课程，目标分布从 agent 当前能达到的 outcomes 逐渐扩展到更难 goals。
>
> **核心技术**: goal-conditioned RL, UVFA, off-policy replay, achieved-goal relabeling, sparse binary rewards, implicit curriculum

## 0. 阅读定位与范本价值

HER 是 sparse reward robot learning 的基础方法，但它经常被一句“从失败中学习”讲浅。更精确地说，HER 不是把失败说成成功，而是改变问题条件：这条动作序列没有达到原目标 $g$，但它确实达到了某个状态 $s_T$；如果把目标换成 $m(s_T)$，它就是一条有效的成功经验。

它成立有三个必要条件：

1. 策略和值函数必须以 goal 为条件，即 $\pi(s,g)$ 和 $Q(s,a,g)$。
2. goal 不能改变环境 dynamics，只改变 reward 解释。
3. 必须能从状态中抽取一个已达成 goal，即存在 $m:S\to G$ 且 $f_{m(s)}(s)=1$。

对当前知识库，HER 是“失败数据再利用”和“目标/任务生成”的经典模板。它对 WMTS 的启发不在于直接替换 PPO，而在于：失败 rollout 仍可变成 achieved-outcome 数据，用于训练 goal-conditioned critic、world model、diffusion generalist 或 latent task curriculum。

| 四支柱 | 本文需要读出的颗粒度 | 在本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么 sparse binary reward 下标准 replay 失效，HER 的 counterfactual relabeling 如何补正 | §1, §4 |
| 原理与理论 | UVFA、goal predicate、mapping $m$、Bellman 更新与 off-policy 条件 | §2 |
| 实验与验证 | bit-flipping、Fetch 三任务、reward shaping、goal-sampling ablation、real robot | §3 |
| 未来与结合 | 目标空间假设、on-policy/PPO 边界、WMTS/DNPM 的 achieved-goal 设计 | §5-§7 |

## 1. 问题设定与动机

### 1.1 一句话核心

HER 的核心判断是：在 sparse binary reward 中，失败轨迹不是没有信息，而是相对原 goal 没有正 reward；如果任务是 goal-conditioned 且 off-policy，失败轨迹可以被重新标注为另一个 goal 下的成功或部分成功，从而把 replay buffer 从“全是 -1”变成有 Bellman 学习信号的数据集。

### 1.2 直观隐喻

练习射门时，球没进原来的球门。标准 RL 只记住“这串动作失败”。HER 会补一句：“如果球门在球实际落点，这串动作就是成功。”这不是自欺欺人，因为动作确实导致了那个 outcome。它学习的是从当前状态到 achieved outcome 的控制规律，再通过函数逼近泛化到 desired outcome。

这个隐喻的边界也要明确：如果“球门位置”改变了物理 dynamics，例如风场、摩擦、对手行为也随 goal 变，那同一轨迹就不能随便 relabel。HER 的数学前提是 goal 只进入 reward/policy input，不进入 transition $p(s'|s,a)$。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 | HER 的 Delta |
|---|---|---|---|
| Sparse binary reward + standard replay | 只按原始 goal 评价经验 | replay buffer 几乎全是 $-1$，critic 学不到差异 | 用 achieved goals 重新计算 reward，制造有效 Bellman targets |
| Dense reward shaping | 人类设计距离/方向/接触奖励 | 容易优化 surrogate 而非最终成功；需要 domain knowledge | 直接优化 binary success/failure |
| Count-based / curiosity | 鼓励访问新状态 | bit-flipping 这类任务不是缺状态多样性，而是缺可解释正样本 | relabel 已访问状态为 goals，使访问变成监督信号 |
| Explicit curriculum | 人为控制目标难度 | 需要设计目标分布和调度 | achieved-goal 分布自然随能力扩张 |
| Demonstrations | 提供成功轨迹 | 需要人类/专家数据 | HER 不需要成功 demo，但需要可重标注 goal |

### 1.4 Delta 分析

标准 replay 存：

$$
(s_t\|g,\ a_t,\ r(s_t,a_t,g),\ s_{t+1}\|g).
$$

HER 额外存：

$$
(s_t\|g',\ a_t,\ r(s_t,a_t,g'),\ s_{t+1}\|g'),
\qquad
g'\in S(\text{episode}),
$$

其中 $g'$ 通常来自同一 episode 中实际达到的某个未来状态。增量不是“多采样”，而是 **改变 Bellman backup 的条件变量**。同一 $(s,a,s')$ 在不同 $g$ 下对应不同 reward 和不同 $Q(s,a,g)$。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $S,A$ | state/action space | environment | 无梯度 | 原始 MDP 空间 | HER 不改变 dynamics |
| $G$ | goal space | task design | 无梯度 | 想达成的目标集合 | $G$ 可以是状态子空间，不一定等于 $S$ |
| $g$ | desired goal | episode sampling | 作为 policy/critic 输入 | 原始任务目标 | goal 固定一整个 episode |
| $f_g:S\to\{0,1\}$ | predicate | reward definition | 无梯度 | 判断 state 是否满足 goal | reward 依赖 $s'$ 是否满足 $g$ |
| $m:S\to G$ | achieved-goal mapping | environment/task interface | 无梯度 | 把状态转成该状态已满足的 goal | HER 必要接口；不是所有任务都有 |
| $r(s,a,g)$ | scalar | reward recomputation | critic target 数值 | binary/sparse reward | 论文用 $-1/0$，不是 $0/1$ |
| $\tau=(s_0,a_0,\ldots,s_T)$ | episode trajectory | rollout | detached data | 可被多个 goals 重新解释 | 行为 action 是按原 goal 产生的，因此需要 off-policy |
| $g'$ | hindsight goal | sampled from episode/buffer | 无梯度 | relabeled desired goal | 常用 future/final/episode/random 策略 |
| $k$ | integer | HER hyperparameter | 固定 | 每个 transition 增加的 hindsight goals 数 | 太大稀释原始 goal 数据 |
| $R$ | replay buffer | storage | 无梯度 | 存原始和 relabeled transitions | 可存时 relabel，也可采样时动态 relabel |
| $Q(s,a,g)$ | scalar | critic/value approximator | 对网络参数有梯度 | goal-conditioned value | 不同 goal 下同一 transition 的 reward/target 不同 |
| $\pi(s,g)$ | action | actor/policy | 对 actor 参数有梯度 | goal-conditioned policy | policy 必须看到 goal，否则 relabel 无意义 |

### 2.2 从 UVFA 到 HER

多目标 RL 中，每个 goal $g\in G$ 对应一个 reward function $r_g$。策略和值函数都以 goal 为输入：

$$
\pi:S\times G\to A,
\qquad
Q^\pi:S\times A\times G\to\mathbb{R}.
$$

Bellman equation 变成：

$$
Q^\pi(s_t,a_t,g)
=
r(s_t,a_t,g)
+
\gamma
\mathbb{E}_{s_{t+1}}
\left[
Q^\pi(s_{t+1},\pi(s_{t+1},g),g)
\right].
$$

off-policy critic 学习只需要 transition $(s,a,s')$ 和目标 $g$ 下的 reward。因为 dynamics：

$$
p(s'|s,a)
$$

不依赖 $g$，同一个 transition 可以服务于不同 goals。HER 正是利用这个条件：

$$
(s_t,a_t,s_{t+1})
\quad\text{固定，}
\qquad
g\ \text{可替换，}
\qquad
r(s_t,a_t,g)\ \text{重新计算。}
$$

### 2.3 Goal predicate 与 achieved-goal mapping

论文假设每个 goal 有 predicate：

$$
f_g(s)\in\{0,1\}.
$$

若 goal 被满足，$f_g(s)=1$。稀疏 reward 写成：

$$
r_g(s,a)=-[f_g(s')=0],
$$

也就是未达到给 $-1$，达到给 $0$。这个符号很重要：失败是负回报，成功是 0，而不是成功 +1。

HER 还需要一个映射：

$$
m:S\to G,
\qquad
f_{m(s)}(s)=1.
$$

例如 Fetch 任务里：

$$
G=\mathbb{R}^3,
\qquad
m(s)=s_{object},
$$

即把当前物体位置当作 achieved goal。bit-flipping 中 $G=S=\{0,1\}^n$，$m$ 是 identity。

这就是 HER 的理论大门：如果不能从状态中抽取 meaningful achieved goal，就不能做标准 HER。

### 2.4 Algorithm 1 的无跳步机制

给定 episode：

$$
s_0,a_0,s_1,a_1,\ldots,s_T.
$$

对每个 transition $t$，先存原 goal：

$$
r_t=r(s_t,a_t,g),
$$

$$
(s_t\|g,\ a_t,\ r_t,\ s_{t+1}\|g)\in R.
$$

然后用策略 $S$ 采样额外 goals：

$$
G'_t=S(s_0,\ldots,s_T,t).
$$

对每个 $g'\in G'_t$：

$$
r'_t=r(s_t,a_t,g'),
$$

$$
(s_t\|g',\ a_t,\ r'_t,\ s_{t+1}\|g')\in R.
$$

最后 off-policy 算法从 replay buffer 采样 minibatch，做普通 Bellman 更新。HER 本身不是新 optimizer；它是 replay data transformation。

### 2.5 四种 hindsight goal 策略

| 策略 | 定义 | 机制直觉 | 实验结论 |
|---|---|---|---|
| final | 用 episode 最终状态 $m(s_T)$ | 最简单；每条轨迹至少有一个达成 goal | 能解 push/pick，slide 较弱 |
| future | 对 transition $t$，采样同 episode 中 $t$ 之后的 $k$ 个 states | 这些 goals 是当前动作之后真实会达成的，credit assignment 最贴近 | $k=4$ 或 $8$ 最好，唯一几乎完美解决 sliding |
| episode | 采样同 episode 任意 states | 比 random 更接近当前能力分布 | 通常有效，但不如 future |
| random | 从训练至今所有 states 随机采样 | 多样但常与当前 transition 无关 | 效果差，尤其 average success 很低 |

为什么 future 最好？因为对 $s_t,a_t$ 的 Bellman target 来说，未来 achieved goals 与当前 transition 的因果链更近。random goals 虽然可达，但可能与当前 transition 无关，导致 reward 仍稀疏或 credit 模糊。

### 2.6 HER 是隐式课程，但不是万能课程

早期随机 policy 只能到达初始状态附近，HER relabel 的 goals 也简单。随着策略变强，episode 达到的状态更远，relabel goals 自然变难：

$$
p_{\text{HER}}(g)
\approx
p_{\text{achieved}}(g;\pi_t).
$$

这个 achieved-goal distribution 随策略能力更新，因此构成隐式课程：

$$
\text{easy achieved goals}
\rightarrow
\text{medium achieved goals}
\rightarrow
\text{desired-goal region}.
$$

但它不是万能课程。如果早期探索永远无法触及关键中间状态，例如从未把物体抓起来，那么 HER 只能学习“如何达到桌面上的位置”，不能凭空生成空中 grasp 成功。论文 pick-and-place 就使用了一个 recorded grasped state，让一半 episode 从 grasped state 开始；这说明 HER 仍需要某种 exploration bridge。

## 3. 训练、数据与实验

### 3.1 Bit-flipping：最小反例

环境：$S=\{0,1\}^n$，动作 $i$ 翻转第 $i$ 个 bit，目标也是 bit vector，reward：

$$
r_g(s,a)=-[s\ne g].
$$

episode length 等于 bit 数。标准 DQN 在 $n>40$ 时几乎永远看不到成功奖励；论文 Fig. 1 显示 DQN without HER 只能解到 $n\le13$，DQN+HER 能解到 $n=50$。

因果解释：bit-flipping 不是缺探索多样性。随机动作当然会访问很多 states；问题是几乎没有访问到指定目标。HER 把访问到的 states 变成目标，使 replay buffer 中出现非全 $-1$ 的目标条件训练样本。

### 3.2 Fetch manipulation setup

| 项目 | 设定 |
|---|---|
| 机器人 | 7-DOF Fetch arm, parallel gripper, MuJoCo simulation |
| 任务 | pushing, sliding, pick-and-place |
| Goal | object desired position $g\in\mathbb{R}^3$ |
| achieved-goal mapping | $m(s)=s_{object}$ |
| sparse reward | $r(s,a,g)=-[|g-s'_{object}|>\epsilon]$ |
| success threshold | pushing/pick-and-place 7cm；sliding 20cm |
| action | 4D: desired relative gripper position (3D) + desired finger distance |
| episode length | 50 environment timesteps |
| workers | 8 workers |
| actor/critic | 3 hidden layers, 64 units, ReLU; actor tanh output rescaled to $[-5\mathrm{cm},5\mathrm{cm}]$ |
| training | 200 epochs; each epoch 50 cycles; each cycle 16 episodes + 40 optimization steps |
| minibatch | 128 |
| replay buffer | $10^6$ transitions |
| target update | decay coefficient 0.95 |
| optimizer | Adam, lr 0.001 |
| discount | $\gamma=0.98$ |
| exploration | 20% random valid action; otherwise policy action + Gaussian noise at 5% of action range |
| training time | pushing/pick-and-place about 2.5h; sliding about 6h on 8 CPU cores |

### 3.3 Main result：HER 是否让 sparse binary reward 可学

Fig. 3 比较 DDPG、DDPG+count-based exploration、DDPG+HER(final)、DDPG+HER(future, $k=4$)。每个 epoch = 800 episodes = $800\times50$ timesteps，结果 5 seeds。

| 任务 | DDPG | DDPG + count-based | DDPG + HER(final) | DDPG + HER(future, k=4) |
|---|---|---|---|---|
| pushing | 基本 0% | 基本 0% | 接近 100%，但较慢 | 接近 100%，更快 |
| sliding | 基本 0% | 有一些进展，约二三成 | 中等进展 | 接近 90%-100% |
| pick-and-place | 基本 0% | 基本 0% | 接近 100% | 接近 100% |

因果解释：count-based exploration 在 sliding 有些帮助，但无法系统解决三个任务，因为 sparse reward 的核心不是“不访问新状态”，而是“访问到的状态没有被当成有用目标”。HER 直接改变 replay 里的目标条件，使几乎所有 episode 都能提供至少某些 successful goal 的学习信号。

### 3.4 Single-goal 实验

Fig. 4 把目标固定为同一个 goal，测试 HER 是否只适用于 multi-goal 训练。结果显示 DDPG+HER 仍显著优于 DDPG。但比较 Fig. 3 和 Fig. 4，multi-goal setup 学得更快。

因果解释：即使最终只关心一个 goal，训练时引入多 goal 也有价值。HER 的课程来自 achieved-goal 分布；如果只训练单一 goal，hindsight goals 的多样性和对 policy 的泛化帮助会变弱。

### 3.5 Reward shaping 反直觉结果

作者测试 shaped reward：

$$
r(s,a,g)=\lambda|g-s_{object}|^p-|g-s'_{object}|^p,
\qquad
\lambda\in\{0,1\},\ p\in\{1,2\}.
$$

Fig. 5 显示最好的 shaped reward $-|g-s'_{object}|^2$ 下，DDPG 和 DDPG+HER 都无法解决三项任务。

因果解释：

1. shaped reward 优化的是距离 surrogate，不一定对应最终 binary success。
2. 距离惩罚会惩罚“暂时朝错方向探索”的动作，可能让 agent 学会不碰物体。
3. 对接触任务，真正好的 dense reward 往往很复杂；简单 domain-agnostic shaping 不可靠。

这支持 HER 的价值叙事：与其设计一个错的 dense proxy，不如保持最终指标为 binary success，并用 relabeling 改善样本效率。

### 3.6 Goal sampling ablation

Fig. 6 比较 final、future、episode、random，以及 $k\in\{1,2,4,8,16,\text{all}\}$。

| 结论 | 证据 |
|---|---|
| random strategy 最差 | highest/average success 在三任务中明显低，pick-and-place 尤其差 |
| final/episode/future 都能解决 pushing 和 pick-and-place | top-row highest success 接近 1.0 |
| sliding 最依赖 future | future with $k=4$ 或 $8$ 最好，几乎完美；final/episode 明显弱 |
| $k$ 太大反而退化 | $k>8$ 时 normal replay 数据比例太低，all 策略下降 |

因果解释：future goals 是“从当前 transition 之后真实会达成”的目标，因此对当前 action 的 credit assignment 最强。random goals 虽然来自已访问状态，但可能和当前 transition 因果无关。

### 3.7 Real robot deployment

作者把 simulator 中 pick-and-place、future strategy $k=4$ 训练出的 policy 直接部署到真实 Fetch 机器人，无 finetuning。物体位置由单独训练的 CNN 从 Fetch head camera raw images 预测，CNN 只用 MuJoCo renderer images 训练，并通过 domain randomization 泛化到真实图像。

| 训练设置 | 真实成功率 |
|---|---:|
| perfect simulation state training | 2 / 5 |
| training with Gaussian observation noise std = 1cm | 5 / 5 |

因果解释：HER 本身没有解决 perception Sim-to-Real。第一次 2/5 的失败来自 policy 对 box position estimation error 不鲁棒；加入 1cm observation noise 后 5/5，说明部署成功依赖 state estimation robustness/domain randomization。HER 解决 sparse reward learning，Sim-to-Real 还需要感知噪声建模。

## 4. 核心洞见

### 4.1 论文真正的 insight

HER 的 insight 是把“成功”从一个固定目标的稀有事件，改写成状态空间中大量可达 outcomes 的监督信号。标准 RL 问：

$$
\text{这条轨迹是否达到原目标 }g?
$$

HER 追加问：

$$
\text{这条轨迹实际达到了什么 goal }m(s)?
$$

这第二个问题几乎每条轨迹都有答案。于是 sparse reward 不再意味着 replay buffer 没信号。

### 4.2 为什么这个设计有效

HER 同时利用了三个结构：

| 结构 | 作用 |
|---|---|
| Goal-conditioned value | 同一 state-action 可在不同 goal 下有不同价值 |
| Off-policy replay | 行为轨迹不必由当前 relabeled goal 的 policy 产生 |
| Achieved-goal mapping | 每个 visited state 都能成为一个已完成目标 |

缺一不可。如果没有 goal-conditioned value，relabeled data 无处输入；如果算法 on-policy，换 goal 后 trajectory distribution 不匹配；如果没有 $m(s)$，失败状态无法变成目标。

### 4.3 什么时候会失效

HER 会在以下情况下失效或变弱：

1. goal 不能从状态中抽取，例如“动作要优雅”“保持安全边界”这类非状态 outcome。
2. goal 改变 dynamics，例如不同目标对应不同工具、不同环境配置或不同对手行为。
3. 任务需要未探索到的关键中间事件，HER 无法从未访问状态生成经验。
4. reward 依赖轨迹历史而非终态 predicate，例如“连续旋转三圈且不掉落”不能只用单个 achieved pose relabel。
5. on-policy PPO 不能直接重放 relabeled transitions，必须另设 off-policy critic/pretraining 或数据生成用途。

## 5. 替代方案与理论局限

### 5.1 理论维度

HER 的理论干净性来自 off-policy Bellman consistency，但它没有解决 coverage。它只能学习如何到达已经被探索到的 achieved goals，再靠函数逼近泛化到 desired goals。如果 achieved-goal distribution 与 desired-goal distribution 不连通，HER 也无能为力。

此外，HER 改变 replay buffer 的目标分布。$k$ 太大会让训练分布偏离原始 desired goals，Fig. 6 中 $k>8$ 下降正是这个问题。

### 5.2 算法维度

HER 主要适配 DQN/DDPG/NAF/SDQN 这类 off-policy 算法。对 PPO 这类 on-policy Oracle，不能简单把旧 trajectory 换 goal 后当 on-policy 样本更新 policy ratio。可行路径是：

| 路径 | 用法 |
|---|---|
| off-policy auxiliary critic | 用 HER 训练 goal-conditioned critic 或 value model，PPO 仍按 on-policy actor 更新 |
| behavior cloning / diffusion data | 把 relabeled goal-trajectory pair 当 supervised data |
| world model training | 用 achieved outcome relabel 训练 conditional transition/outcome predictor |
| task curriculum | 用 achieved goals 估计当前能力边界，生成下一批 goals |

### 5.3 工程/实验维度

| 局限 | 论文中的迹象 | 对真实系统的影响 |
|---|---|---|
| 需要 achieved_goal 接口 | Fetch 用 object position，bit-flip 用 state identity | 真实灵巧任务要先定义可测 outcome |
| 需要 sparse reward 可重算 | $r(s,a,g')$ 必须可离线计算 | 如果 reward 来自人类偏好/视觉判别器，relabel 成本更高 |
| 需要探索 bridge | pick-and-place 用 grasped initial state 技巧 | 长时程抓取/转笔仍需课程或 demo |
| sim-to-real 另需感知鲁棒 | 真实 2/5 -> 加 1cm noise 后 5/5 | HER 不是 domain randomization 替代品 |
| buffer 比例敏感 | $k>8$ 下降 | relabeled data 与 original-goal data 要平衡 |

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移

HER 对 WMTS 的最大启发是：每条失败 rollout 都应记录 achieved outcome，并用于训练其他条件任务。

| WMTS 模块 | HER 式改造 |
|---|---|
| latent task generation | 用 achieved goals 建立当前能力分布，选择 frontier goals |
| PPO Oracle | 不直接 on-policy relabel；可用 HER critic/pretraining 或生成 oracle 子任务 |
| Diffusion/Flow generalist | 训练条件为 desired/achieved outcome 的 trajectory model，把失败轨迹变成“达到中间 outcome”的正样本 |
| Ensemble World Model | 学习 $(s,a,g)\to$ success probability / distance-to-goal，并估计 relabeled goals 的不确定性 |
| real-robot fine-tuning | 把每次真实失败转成 achieved-goal data，减少真实样本浪费 |

这和 WMTS 的 Solve/Probe/Reject 可以衔接：Solve 目标由 desired goals 给出；Probe 产生失败/偏差轨迹；HER 把 Probe 结果变成 achieved-goal supervision；Reject 用 ensemble 判断哪些 achieved outcomes 不能安全外推。

### 6.2 对灵巧手转笔 / DNPM 的具体设计

转笔不能只把 achieved_goal 定义为笔的角度。若只用角度，HER 会把“笔短暂转到 90 度但即将掉落”的状态当成成功目标，学到错误接触模式。更合理的 achieved goal 应包含：

| achieved-goal 分量 | 原因 |
|---|---|
| pen orientation / phase | 表示旋转进度 |
| angular velocity | 区分静态摆到角度 vs 动态旋转 |
| contact mode / tactile pattern | 区分可持续接触 vs 即将滑落 |
| hand posture margin | 避免不可恢复的极限关节姿态 |
| drop/safety flag | 防止 relabel 危险状态为正样本 |

因此 DNPM-HER 应该是 phase-contact-conditioned HER，而不是 naive angle HER。

### 6.3 可验证实验建议

1. **Angle-only HER vs phase-contact HER**：同一转笔仿真，比较 achieved_goal 只含角度、角度+角速度、角度+角速度+触觉接触。若 angle-only 学到不可持续状态，说明目标定义不足。
2. **PPO Oracle + HER auxiliary critic**：PPO actor on-policy 不 relabel，另训练 HER goal critic，观察是否改善 value shaping 或 task selection。
3. **HER for world model task generator**：把失败 rollouts 的 achieved outcomes 加入 latent task pool，比较是否比随机 curriculum 更快覆盖技能边界。
4. **k-ratio ablation**：复现 HER 的关键 lesson，比较 $k=1,4,8,16$ 以及 original-goal 数据比例，避免 relabeled data 淹没真实目标。

### 6.4 不应过度外推的点

HER 不会自动解决 exploration 到关键事件的问题。论文 pick-and-place 仍需要 grasped initial state trick；真实部署仍需要 observation noise/domain randomization。对转笔这种动态接触任务，HER 只能放大已有探索结果的价值，不能替代动作先验、课程、触觉状态估计和安全控制。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系

HER 是 UVFA + off-policy Bellman backup 的典型组合：

$$
Q(s,a,g)
=
r(s,a,g)+\gamma Q(s',\pi(s',g),g).
$$

它的关键不是 Bellman 公式变了，而是 replay buffer 中同一个 transition 可以产生多个 $g$ 下的 Bellman targets。这个思想对所有 goal-conditioned off-policy learning 都是基础。

### 与 [[Optimization]] 的联系

HER 的 implicit curriculum 可以写成目标分布迭代：

$$
p_{\text{train}}(g)
=
(1-\lambda)p_{\text{desired}}(g)
+
\lambda p_{\text{achieved}}(g;\pi_t).
$$

随着 $\pi_t$ 改善，$p_{\text{achieved}}$ 的支持集扩大。优化上，这等价于把训练目标从不可达的稀疏点，连续拉回当前能力边界附近。

### 与 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]] 的联系

DemoStart 用 demonstration states 构造课程起点，HER 用 achieved states 构造 hindsight goals。二者互补：DemoStart 解决“怎么到达有学习信号的区域”，HER 解决“到达任何区域后如何最大化利用”。对灵巧手，先用 demo/curriculum 打开探索桥，再用 HER 复用失败 outcomes，比单独 HER 更现实。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| HER 为什么不是简单把失败当成功？ | 解释 goal 条件改变：原 goal 失败，但 achieved goal 成功；dynamics 不依赖 goal，所以 off-policy Bellman 合法。 |
| HER 需要什么前提？ | $\pi(s,g),Q(s,a,g)$；off-policy algorithm；映射 $m:S\to G$；reward 可对 $g'$ 离线重算。 |
| future strategy 为什么最好？ | future goals 与当前 transition 的因果链近，credit assignment 更强；random goals 与当前 transition 常无关。 |
| 实验如何证明故事？ | DQN bit-flip n≤13 vs HER n=50；Fetch DDPG 无 HER 失败，HER 接近满成功；shaped reward 反而失败；real 2/5 -> noise 后 5/5。 |
| PPO 能不能直接用 HER？ | 不能直接按 on-policy ratio 更新；可做 auxiliary critic、BC/diffusion data、world model task relabeling。 |
| 转笔如何设计 achieved_goal？ | 不能只用角度；要包含 phase、angular velocity、contact/tactile mode、安全/掉落状态。 |

## References

- Andrychowicz, Marcin, Filip Wolski, Alex Ray, Jonas Schneider, Rachel Fong, Peter Welinder, Bob McGrew, Josh Tobin, Pieter Abbeel, and Wojciech Zaremba. 2017. *Hindsight Experience Replay*. NeurIPS.
- Schaul, Tom, Daniel Horgan, Karol Gregor, and David Silver. 2015. *Universal Value Function Approximators*.
- Lillicrap, Timothy P. et al. 2015. *Continuous Control with Deep Reinforcement Learning*.
