---
tags:
  - paper
  - dexterous-manipulation
  - reinforcement-learning
  - knowledge-transfer
  - sim-to-real
  - hindsight-experience-replay
aliases:
  - Dexterous RL with KT
  - RRC 2021
  - TriFinger DDPG HER KT
paper-year: 2023
read-date: 2026-06-25
venue: arXiv / Real Robot Challenge
paper-pdf: "[[Papers/Dexterous Robotic Manipulation using Deep Reinforcement.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[Dynamics]]"
---

# Dexterous Robotic Manipulation using Deep Reinforcement Learning and Knowledge Transfer

> [!abstract] 核心贡献
> 这篇论文用 DDPG+HER 在 TriFinger / RRC 2021 上赢得 position-trajectory 操作任务，并进一步提出 Knowledge Transfer：先在 position-only 任务学会移动 cube，再把 actor+critic 迁移到 position+orientation 扩展任务，显著降低 sparse-reward 下从零探索的难度。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 目标条件 DDPG+HER 的实战案例：如何把 sparse goal reward 改造成可学习信号，以及为什么 HER 不能无脑作用到所有维度。
> - [[Optimization]] — Knowledge Transfer 是优化初值设计：用源任务的 actor/critic 参数把目标任务训练从“盲探索”移动到有用策略邻域。
> - [[Dynamics]] — Sim-to-real 依赖先 nominal simulation 学策略、再 domain randomization fine-tune；但真实 contact/friction gap 仍是主要限制。
> - [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RL §9.2]] — NDR→DR-tune 的 staged DR 是"三味药"里 **DR（增覆盖）** 一味的正确用法：先学 nominal 技能再加鲁棒，Table 3 证明 DR-from-scratch 反而最差。
> - [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]] — **电流≠关节力矩**暗线的反面样本：TriFinger action 是 9D **直接 torque**（不经 PD 位置层），执行器/摩擦 gap 直接暴露给策略，正是"无 real fine-tune 时真机 gap 残留"的物理来源之一；与 HORA/Spin Pens 的 position-target+PD 接口形成对照。
>
> **核心技术**: DDPG, HER, sparse+dense reward mixing, staged domain randomization, actor-critic knowledge transfer, TriFinger manipulation

## 0. 阅读定位与范本价值

这篇不是 OpenAI Shadow Hand 那条路线，而是 Real Robot Challenge / TriFinger 平台上的 goal-conditioned DRL 工作。它在知识库里的价值有三点：

| 四支柱 | 本文要看清的点 | 本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么 DDPG+HER 能赢 RRC，KT 又解决什么新增瓶颈？ | §1 说明 position-only 到 position+orientation 的 curriculum/transfer 逻辑 |
| 原理与理论 | HER、奖励分解、DR schedule、KT 三种实现如何推导？ | §2 从 MDP、score、reward、HER 作用维度、teacher/student 权重迁移展开 |
| 实验与验证 | 哪些数字证明 reward/HER/DR/KT 的机制？ | §3 用 Table 1-4 解释 pinching、DR fine-tune、ACTOR-CRITIC KT |
| 未来与结合 | 对转笔/WMTS 有什么启发和边界？ | §5-§7 把“先粗后精”的 KT 迁移到 DNPM，同时指出 DDPG/DR/无真机 fine-tune 的限制 |

它和 HIL-SERL 的对照很有价值：HIL-SERL 是真实在线 RL + 人类纠正；本文是仿真离线训练 + DR + 远程真机评估。两者都想解决真实灵巧操作，但数据与反馈来源完全不同。

## 1. 问题设定与动机

### 1.1 一句话核心

本文的核心判断是：在 sparse reward dexterous manipulation 中，**先学会容易探索的子能力，再迁移到更难目标**，比从零探索完整任务更有效。

具体来说：

$$
\text{Move Cube on Trajectory}
\quad \to \quad
\text{Move Cube on Trajectory Pro}.
$$

前者只要求 cube 跟随位置轨迹；后者还要求保持目标姿态。Position-only 任务可以通过 pushing/cradling/pinching 学到“怎么控制 cube 的位置”；Pro 任务需要在这个基础上探索 orientation control。KT 的价值是把“位置控制”作为已有技能迁移过去，让 orientation 探索不再从随机动作开始。

### 1.2 直观隐喻

这像先学会“把球拿到指定位置”，再学“把球拿到指定位置并让 logo 朝上”。第二个任务不是完全新任务：抓、托、推、夹的基本控制技能仍然有用；新增的是旋转/姿态维度。如果从零学，机器人要同时发现如何搬运和如何旋转，探索空间太大。

可证伪点：如果 position skill 真的可迁移，那么 Pro 任务中 KT 方法应该比 SCRATCH 好；如果只迁移 actor 就够，ACTOR 应该表现好；如果 value landscape 也可迁移，ACTOR-CRITIC 应最好。Table 4 的结果正是：ACTOR-CRITIC 最好，SCRATCH 最差，ACTOR 反而很差。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 | 本文增量 |
|---|---|---|---|
| 传统 IK / motion primitives | 手工运动结构、几何解 | 多接触 dexterity 中工程复杂、泛化弱 | 直接从状态到 torque action 学 manipulation strategy |
| Sparse reward RL from scratch | 最少 reward engineering | 正反馈太稀，早期盲探索无效 | DDPG+HER + reward 分解 |
| Dense distance reward | 每步都有几何信号 | 容易只优化距离而不学真正 goal-conditioned skill | 稀疏 $xy$/orientation + dense $z$ 的混合 |
| Domain randomization from scratch | 早期就学鲁棒策略 | 随机化使最优策略学习更难 | 先 non-DR 学会，再 DR fine-tune |
| Full Pro task from scratch | 不做手工 curriculum | position+orientation 同时探索太难 | KT 从 position-only teacher 迁移 |

### 1.4 Delta 分析

本文的 delta 不是“DDPG+HER 很新”，而是三个 pragmatic choices 的组合：

1. HER 只重标注适合 hindsight 的目标维度，不重标注会误导 lifting 的 $z$；
2. sim-to-real 不从 DR 开始，而是 nominal training → DR tuning；
3. KT 不只是用 teacher 收数据，最强版本是 actor+critic 权重一起迁移。

这三点都体现一个共同 insight：**不要把复杂度一次性放进训练初期。先让策略在较干净的子问题上形成可用控制结构，再逐步加入鲁棒性、姿态和真实物理差异。**

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $s_t$ | 44/48D observation | simulator/real robot | 对网络输入可反传 | joints, cube pose, pose delta, goal | position-only 44D，Pro 加 orientation goal 到 48D |
| $a_t$ | 9D continuous torque | actor output | 是 | TriFinger 三指各 3 个电机 torque | 不是 EE twist，是 pure torque control |
| $g_t$ | goal | task generator | 否 | 当前 active goal | 训练时把 $g_{t+1}=g_t$，避免 goal change 增加 Q 不确定性 |
| $g'_{xy},g'_z,g'_o$ | achieved goal components | cube pose | 否 | 实际 xy/z/orientation | HER 对不同维度处理不同 |
| $r_{xy}$ | sparse scalar | reward | 否 | xy within 2 cm gives 0 else -1 | reward 越接近 0 越好，不是 1/0 |
| $r_z$ | dense scalar | reward | 否 | 引导 lifting | cube above goal 惩罚减半，鼓励 lifting |
| $r_{ori}$ | sparse scalar | reward | 否 | orientation within 22 deg gives 0 else -1 | 只在 Pro 任务使用 |
| $\pi(s,g)$ | actor | DDPG | 是 | deterministic goal-conditioned policy | 输出 action 后乘 max action ratio |
| $Q(s,g,a)$ | critic | DDPG | 是 | goal-conditioned action value | KT 中 critic 是否迁移是核心变量 |
| $\hat g$ | HER relabeled goal | replay sampling | 否 | future achieved goal | 只从当前 active goal 时间段内采样 |
| DR parameters | simulator physics | domain randomization | 否 | mass, damping, friction, noise 等 | 只用于 position-only sim-to-real，且后期 fine-tune |
| teacher | trained position-only agent | KT | 是/固定初始化 | 给 Pro student 提供 position manipulation skill | teacher 选 80% success，避免过强 position bias |
| ACTOR-CRITIC | KT strategy | Pro training | 是 | student actor+critic 初始化为 teacher weights | 论文结果最佳，旧稿中“critic 重置更好”是错的 |
| ACTOR | KT strategy | Pro training | 是 | 只迁移 actor，critic 随机 | 表现差，因为 random critic 与 trained actor 不兼容 |
| COLLECT | KT strategy | Pro training | 否/间接 | teacher 早期帮助收集经验，权重不迁移 | 好于 scratch，但不如 actor-critic |

### 2.2 RRC 任务与评分

**Move Cube on Trajectory**：TriFinger 要把 cube 按目标 3D position trajectory 移动。最终评估每个 episode 120,000 steps，有 10 个目标位置，目标在指定 step 切换。

Position score:

$$
s_{pos}
=
-
\frac{1}{2}
\left(
\frac{\|g'_{xy}-g_{xy}\|}{2d_r}
+
\frac{\|g'_z-g_z\|}{d_h}
\right).
$$

分数是负的，越接近 0 越好。

**Move Cube on Trajectory Pro**：在位置轨迹基础上加入 orientation target：

$$
s_{pos+ori}
=
-
\left\|
\left(R(g'_o)\right)^{-1}R(g_o)
\right\|
+
s_{pos}.
$$

这比 position-only 难得多，因为 agent 不只要抓/推/托 cube，还要同时控制姿态。

### 2.3 DDPG in goal-conditioned MDP

Goal-conditioned MDP:

$$
(\mathcal{S},\mathcal{A},\mathcal{G},p,r,\gamma,\rho_0).
$$

DDPG 维护：

$$
\pi:\mathcal{S}\times\mathcal{G}\to\mathcal{A},
$$

$$
Q:\mathcal{S}\times\mathcal{G}\times\mathcal{A}\to\mathbb{R}.
$$

Critic target:

$$
y_t
=
r_t
+
\gamma Q(s_{t+1},g_{t+1},\pi(s_{t+1},g_{t+1})).
$$

Critic loss:

$$
\mathcal{L}_c
=
\mathbb{E}
\left[
\left(
Q(s_t,g_t,a_t)-y_t
\right)^2
\right].
$$

Actor loss:

$$
\mathcal{L}_a
=
-
\mathbb{E}_s
\left[
Q(s,g,\pi(s,g))
\right].
$$

DDPG 本身并不新；它的价值在于与 HER、reward decomposition、DR schedule 和 KT 组合成可赢 RRC 的 pipeline。

### 2.4 Reward decomposition：为什么 $xy$ 稀疏、$z$ 稠密

Sparse $xy$ reward:

$$
r_{xy}
=
\begin{cases}
0,& \|g'_{xy}-g_{xy}\|\le 2\text{ cm}\\
-1,& \text{otherwise}
\end{cases}.
$$

Dense $z$ reward:

$$
r_z
=
\begin{cases}
-a\|z_{cube}-z_{goal}\|,& z_{cube}<z_{goal}\\
-\frac{a}{2}\|z_{cube}-z_{goal}\|,& z_{cube}>z_{goal}
\end{cases},
\quad a=20.
$$

Orientation reward for Pro:

$$
r_{ori}
=
\begin{cases}
0,& \|(R(g'_o))^{-1}R(g_o)\|\le0.384\text{ rad}\\
-1,& \text{otherwise}
\end{cases}.
$$

Final Pro reward:

$$
r=r_{xy}+r_z+r_{ori}.
$$

设计逻辑：

- $xy$ 可以用 HER 学，因为 cube 在地面上的 achieved future positions 很多；
- $z$ 不适合早期 HER，因为早期 cube 多数在地面，若把低 $z$ achieved state 当目标，会惩罚偶然 lifting，反而阻碍学会抬 cube；
- $z$ 用 dense reward 且高于目标惩罚减半，是为了鼓励探索 lifting；
- orientation 在 Pro 中稀疏，并使用 HER，因为目标 orientation 本身难探索，需要 hindsight 信号。

这是一篇很适合提醒自己的论文：HER 不是“对所有 goal 维度重标注”。HER 的合法性取决于 relabeled goal 是否会扭曲你真正想学的子技能。

### 2.5 HER 在多目标轨迹里的边界

HER 将 transition：

$$
(s_t,g_t,a_t,r_t,s_{t+1},g_{t+1})
$$

改成：

$$
(s_t,\hat g_t,a_t,\hat r_t,s_{t+1},\hat g_{t+1}),
$$

其中 $\hat g$ 是 episode 后续实际达到的 goal。

但本文有两个关键限制：

1. 只从当前 active goal 对应时间段内采 future achieved goals；
2. policy update 中总设 $g_{t+1}=g_t$，即使真实 episode 中下一步目标切换了。

原因是：agent 不需要知道未来 trajectory，只需要对当前 active goal 做闭环控制。把 goal switching 暴露给 critic 会增加 DDPG value estimate 的不确定性，论文经验上显著伤害 performance。

### 2.6 Exploration vs exploitation：为什么把 evaluation rollouts 放进 buffer

Plappert-style DDPG-HER 使用很强探索：

- 30% probability uniform random action；
- policy action 上加 Gaussian noise。

这对早期探索有利，但后期会反复把 cube 掉下来，妨碍精细策略。论文没有做复杂 annealing，而是把 evaluation episodes 也加入 replay buffer：

$$
90\%\text{ exploratory rollouts}
+
10\%\text{ exploitation rollouts}.
$$

这个小技巧把 simulation success 从 70-80% 提到 >90%。机制上，它给 replay buffer 注入了无噪声/低噪声下的高质量执行轨迹，让 critic/actor 不只学习 noisy exploratory behavior。

### 2.7 Domain randomization schedule

DR 用于 position-only Move Cube on Trajectory 的 sim-to-real：

1. 先在 non-DR simulation 训练 300 epochs；
2. 再在 DR simulation tune 100 epochs；
3. 部署到真实 TriFinger。

直接从 DR 开始不推荐，因为 randomized dynamics 会妨碍 early optimal policy acquisition。Table 3 支持这一点：Scratch(DR) 在 sim/real 都差，non-DR+DR tune 最好。

这和后来很多 sim-to-real 论文的经验一致：**先学会任务，再学会鲁棒**，而不是第一天就把世界随机成地狱。

### 2.8 Knowledge Transfer：四种策略

Pro 任务探索难，因为 agent 必须同时 lift、move、rotate cube。论文先训练 position-only teacher，再训练 Pro student。

为了避免 teacher 对 position-only 太偏，作者：

- 选择 success rate 约 80% 的较弱 teacher；
- early training 增加 action noise。

四种策略：

| Strategy | 做法 | 预期/结果 |
|---|---|---|
| ACTOR-CRITIC | student actor 和 critic 都加载 teacher weights | 最好：position skill 和 value landscape 都迁移 |
| ACTOR | 只加载 actor，critic 随机 | 最差 KT：random critic 的反馈与 trained actor 不兼容，actor performance 被破坏 |
| COLLECT | student 权重随机，teacher 早期帮收集 experience，参与逐渐衰减 | 好于 scratch，但不如 ACTOR-CRITIC |
| SCRATCH | 完全从零训练 Pro | 失败，position/orientation reward 都低 |

最容易犯错的理解是“critic 因 reward 变了必须重置”。这篇的结果恰恰相反：ACTOR-CRITIC 最好。虽然 Pro reward 多了 orientation，但 position manipulation 的 value structure 仍然足够有用，迁移 critic 比随机 critic 更稳定。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项 | 设置 |
|---|---|
| Robot | TriFinger, 3 fingers × 3 motorized joints |
| Action | 9D continuous torque |
| Control/update | 20 Hz, each step 0.05 s |
| Observation | joint position/velocity/torque, cube pose and pose delta, current goal pose |
| Position-only obs dim | 44 |
| Pro obs dim | 48 |
| Training episode | 90 steps, 3 goals, goal changes every 30 steps |
| Real eval episode | 120,000 steps, 10 goals |
| Algorithm | DDPG + HER |
| Actor/Critic LR | 0.001 / 0.001 |
| Discount | 0.98 |
| Batch size | 256 |
| Replay buffer | 1,000,000 |
| HER strategy | future |
| Parallelism | 8 RL agents on 8 processors, weights averaged after updates; experiences not shared |
| Position-only training | 300 epochs, 21.6M env steps total |
| Pro training | 500 epochs, proportional parameters |

### 3.2 Phase 1: position-only RRC 2021

Simulation learned three strategies:

| Strategy | Behavior | Sim score | Real score |
|---|---|---:|---:|
| Pushing | push cube on floor | -20,399 ± 3,799 | -22,137 ± 3,671 |
| Cradling | cradle cube with forearms | -6,349 ± 1,039 | -14,207 ± 2,160 |
| Pinching | pinch with two fingertips, support with third | -6,198 ± 1,840 | -11,489 ± 3,790 |

Scores are negative; closer to zero is better. Pinching was submitted to RRC Phase 1 final evaluation and won.

因果解释：

- Pushing avoids lifting, so it cannot track $z$ well; sim/real both poor.
- Cradling/pinching learn actual dexterous lifting/carrying.
- Pinching transfers better to real than cradling, likely because fingertip pinch gives more stable object control under real friction/slip.

### 3.3 Seed sensitivity

Table 2 shows three seeds:

| Seed | Sim score | Real robot average |
|---|---:|---:|
| 0 | -5447 | -11129 |
| 123 | -6376 | -9417 |
| 200 | -7277 | -15045 |
| Average | -6367 ± 920 | -11864 ± 3181 |

关键解释：

- Best sim seed is not best real seed. Seed 0 has best sim score but worse real than seed 123.
- Seed 200 is bad in both.
- 论文讨论指出 reward varies by about ±27% of mean across seeds。

这提醒我们：sim validation 不能直接选出 best real policy。对于 WMTS，ensemble of policies / seed selection / real-world validation 必须进入流程。

### 3.4 Domain randomization: staged beats from-scratch

Table 3 的 average over seeds：

| Training type | Simulation | Real robot |
|---|---:|---:|
| Scratch(DR) | -9913 ± 1866 | -15936 ± 749 |
| Scratch(NDR) | -6367 ± 920 | -11864 ± 3181 |
| Scratch(NDR) + Tune(DR) | -6075 ± 250 | -8162 ± 1132 |

因果链：

`DR from scratch → early learning faces too many dynamics variations → cannot easily discover dexterous strategy → poor sim and real.`

`NDR from scratch → learns strong nominal manipulation → real gap remains.`

`NDR then DR tune → preserves learned strategy while widening robustness → best real score, near simulator-level for seed 123.`

这个结果是对“domain randomization 越早越好”的反例。对复杂接触任务，DR 是 fine-tuning regularizer，不一定是从零训练环境。

### 3.5 Pro task: Knowledge Transfer

Table 4:

| Method | Avg position deviation (m) | Avg orientation deviation |
|---|---:|---:|
| ACTOR-CRITIC | 0.023 | 75.8° |
| ACTOR | 0.066 | 98.6° |
| COLLECT | 0.031 | 84.9° |
| SCRATCH | 0.134 | 142.2° |
| TEACHER | 0.024 | 126.2° |

因果解释：

- SCRATCH 完全失败：position 和 orientation 都差，说明 Pro 的 sparse reward/exploration 太难。
- TEACHER position 很好但 orientation 差，说明 position-only skill 不能自动解决 orientation。
- COLLECT 好于 scratch，说明 teacher-collected early experience 有帮助。
- ACTOR-only 反而差，说明 trained actor 被 random critic 错误反馈破坏，actor/critic 不匹配会造成 negative transfer。
- ACTOR-CRITIC 最好，说明在 Pro 中保留 position-task 的 value landscape 是有价值的；新增 orientation reward 可以在此基础上继续学习。

这张表是本文最有 insight 的结果：迁移不是“复制策略就行”，而是要迁移与策略匹配的价值评估结构。

## 4. 核心洞见

### 4.1 论文真正的 insight

本文真正的 insight 是：**在 sparse reward dexterous RL 中，课程不一定要通过任务生成器实现，也可以通过 actor-critic 参数初始化实现。**

Position-only teacher 相当于一个手工 curriculum stage。它已经学会 lift/pinch/cradle/push 等基础 contact strategies；Pro student 不需要重新发现这些，只需要在这些策略附近探索 orientation control。

### 4.2 为什么 HER 需要维度选择

HER 的常见说法是“把失败轨迹改成成功轨迹”。本文告诉我们要更细：对 $xy$ 和 orientation，这合理；对 $z$，早期 achieved $z$ 多数在地面，把它当目标会削弱 lifting incentive。

因此正确抽象是：

$$
\text{HER only on dimensions where hindsight goals preserve desired skill pressure.}
$$

对转笔也是如此：可以 relabel achieved rotation angle，但不能轻易 relabel “掉落前的短暂角度”为成功，否则会奖励不稳定转动。

### 4.3 什么时候会失效

| 失效条件 | 为什么 | 对用户项目含义 |
|---|---|---|
| 源/目标任务共享结构弱 | KT warm start 变成 negative transfer | 转笔 coarse/fine stages 要设计成同一 contact strategy family |
| Critic 与 actor 不匹配 | ACTOR-only 结果差 | 迁移 policy 时也要迁移或重建 matched value/world model |
| DR 过早过强 | early learning 学不会 nominal skill | LinkerHand 先 nominal PPO/DP，再逐步 randomize friction/latency |
| 无真实 fine-tune | sim contact gap 留在真实 | 本文讨论承认缺 real data 是主要限制 |
| DDPG 不稳定 | overestimation / seed sensitivity | 现代实现应优先 SAC/TD3/PPO+curriculum 或 RLPD |

## 5. 替代方案与理论局限

### 5.1 理论维度

**KT 没有任务相似性界。** ACTOR-CRITIC 有效是因为 Pro 任务包含 position-only 子结构。若目标任务改变接触模式，迁移 critic 可能误导。

**Sparse+dense reward mix 不可自动泛化。** 作者也承认还不清楚如何 general engineer optimal sparse/dense mix。这个 reward 是 TriFinger lifting 的经验结果。

**HER 在 $SO(3)$ 上仍粗糙。** Orientation reward 用 rotation matrix difference threshold 22°，结果最好的 orientation deviation 仍 75.8°。这说明 HER 能帮探索，但没有真正精确解决姿态控制。

### 5.2 算法维度

| 局限 | 论文证据 | 替代方向 |
|---|---|---|
| DDPG sample inefficient | position-only 约 10M steps / 6 days simulated experience 收敛 | SAC/TD3/RLPD/model-based RL |
| Seed sensitivity | real score std 3181，seed 排名 sim/real 不一致 | multi-seed ensemble, policy selection, robust validation |
| No real fine-tune | 作者称主要限制是 absence of real-robot data | HIL-SERL/DexNDM/GAT 类 real adaptation |
| Contact simulation limited | friction/texture/deformation rendering 基础 | tactile/contact sensing + better simulator/world model |

### 5.3 工程/实验维度

- TriFinger 是标准化平台，真实 robot gap 小于 LinkerHand/多指转笔。
- Evaluation 是远程真实 robot，但 training 全在 simulation。
- Pro task 只在 simulator evaluation 中报告，没有 real robot Pro 部署。
- DR 参数与 stuck recovery heuristic 仍含工程手调。
- 任务是 cube manipulation，不是任意复杂物体/工具使用。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移

这篇给 WMTS 的主要启发是“任务阶梯 + 参数迁移”的形式：

| 本文设计 | WMTS 对应 |
|---|---|
| position-only teacher | coarse task / parent skill / easier latent task |
| Pro student | precise orientation/contact-rich child task |
| ACTOR-CRITIC KT | policy + value/world-model joint transfer |
| NDR then DR tune | nominal specialist → robust specialist |
| HER active-goal interval | task scheduler 中只在同一 subtask phase 内 relabel |

如果 WMTS 用 PPO Oracle，KT 可以表现为：

- 使用 easier task 的 policy 初始化 harder task policy；
- 使用 easier task value 初始化 harder task value，但要允许新 reward head 适配；
- 对 diffusion/flow generalist，使用 coarse task rollouts 作为 warm-start distribution；
- 用 world model 检测 source/target MDP 是否足够相似，避免 negative transfer。

### 6.2 对转笔/DNPM 的具体设计

> 这套 coarse-to-fine 课程在转笔簇里已有两种互补实现：[[Lessons from Learning to Spin Pens|Spin Pens]] 用 **oracle replay 数据引擎** 代替参数迁移（本文迁 actor+critic 权重，Spin Pens 迁真机可 replay 的动作序列）；[[Learning Human-like Finger Gaiting on an Anthropomorphic Hand|FingerGaiting]] 用 **transition waypoint 重塑 $\rho_0$** 代替 teacher warm-start——三者都在解同一个"稀疏奖励下如何进入成功盆地"，只是把 curriculum 分别落在参数空间 / 数据空间 / 初始状态空间。

转笔可以设计类似 curriculum：

| Stage | 目标 | 类比本文 |
|---|---|---|
| Stage 1 | 保持笔不掉，移动到可控接触位置 | position-only teacher |
| Stage 2 | 粗略转动 90°/180°，不要求精确相位 | intermediate teacher |
| Stage 3 | 完整 360°，指定 spin axis / terminal grasp | Pro student |
| Stage 4 | 连续多圈 + 速度/风格控制 | beyond Pro |

HER relabeling 可用但要谨慎：

- 可以把 achieved rotation angle 当 hindsight goal；
- 不应把掉落前的瞬时角度当完整成功；
- 不应 relabel 触觉/contact stability 约束，否则会奖励不稳定策略；
- relabel 必须限制在同一 contact phase 内，类似本文只在 active goal interval 采样。

### 6.3 与 HIL-SERL / PhysicsGen 的组合

三篇可以形成一个真实灵巧操作训练栈：

| 论文 | 作用 |
|---|---|
| PhysicsGen | 从 human/VR demo 生成动态可行 contact trajectories |
| Dexterous RL + KT | 用粗到细任务 curriculum 和 actor-critic transfer 学仿真 specialist |
| HIL-SERL | 真机上用 human intervention 修补 failure boundary |

对 LinkerHand，合理路线不是只选一种，而是：

$$
\text{PhysicsGen seed data}
\to
\text{KT curriculum specialist}
\to
\text{DR robustification}
\to
\text{HIL real correction}
\to
\text{WMTS generalist distillation}.
$$

### 6.4 不应过度外推的点

- 不要把 RRC success 读成一般 sim-to-real 已解决。作者明确说无 real data fine-tune 是主要限制。
- 不要把 ACTOR-only 说成正确 KT；Table 4 显示 ACTOR-CRITIC 最好。
- 不要把 DR from scratch 当默认；本文恰好说明 staged DR 更好。
- 不要把 HER 当万能稀疏奖励解法；HER 维度选择至关重要。
- 不要忽略 Pro orientation 仍有 75.8° deviation，姿态控制远未精确。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

本文是 goal-conditioned off-policy RL 的典型案例：

$$
\pi(a|s,g),\quad Q(s,g,a).
$$

HER 的本质是改变 replay distribution 中的 goal label，让失败轨迹产生可学习 reward。但本文的 nuance 是：HER 不是越多越好，而是必须保持目标维度的技能压力。

### 7.2 与 [[Optimization]] 的联系

KT 是 optimization warm start：

$$
\theta_{student}^{0}
\leftarrow
\theta_{teacher}^{\star}.
$$

ACTOR-CRITIC 有效说明不仅 policy landscape 可复用，value landscape 也可复用。ACTOR-only 失败说明 actor 和 critic 是耦合系统：一个 trained actor 遇到 random critic，会收到不一致梯度，导致性能退化。

### 7.3 与 [[Dynamics]] 的联系

Sim-to-real 成功来自 staged robustness：

$$
\text{learn nominal contact strategy}
\to
\text{fine-tune under randomized physics}
\to
\text{deploy}.
$$

真实失败主要来自 cube slipping、fingertip pressing cube into wall、视觉 pose estimation 被磨损污染等。这些都是 contact/dynamics/estimation gap，不是纯 RL 算法问题。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “KT 具体迁移了什么？” | 四种：ACTOR-CRITIC、ACTOR、COLLECT、SCRATCH；最强是 actor+critic 同迁移，不是只迁移 actor |
| “HER 为什么不作用到 z？” | 早期 achieved z 多在地面，relabel z 会惩罚偶然 lift；所以只 HER xy，z 用 dense reward |
| “DR 怎么用？” | 先 non-DR 300 epochs 学 nominal，再 DR tune 100；DR from scratch 最差 |
| “实验最关键数字？” | Table 3 real -11864→-8162；Table 4 scratch 0.134m/142° vs ACTOR-CRITIC 0.023m/75.8° |
| “对转笔怎么迁移？” | 设计 coarse-to-fine skill teacher，phase-aware HER，只在同一 contact phase relabel，actor+value/world-model 一起迁移 |

## References

- Qiang Wang, Francisco Roldan Sanchez, Robert McCarthy, David Cordova Bulens, Kevin McGuinness, Noel O'Connor, Manuel Wuthrich, Felix Widmaier, Stefan Bauer, Stephen J. Redmond. **Dexterous Robotic Manipulation using Deep Reinforcement Learning and Knowledge Transfer for Complex Sparse Reward-based Tasks**. arXiv 2023.
