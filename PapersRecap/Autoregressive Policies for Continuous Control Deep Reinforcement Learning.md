---
tags:
  - paper
  - reinforcement-learning
  - exploration
  - temporal-coherence
  - autoregressive
aliases:
  - ARP
  - Autoregressive Policy
paper-year: 2019
read-date: 2026-01-31
venue: ICLR 2020
paper-pdf: "[[Papers/Autoregressive Policies for Continuous Control Deep Reinforcement Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[SignalProcessing]]"
  - "[[ControlTheory]]"
---

# Autoregressive Policies for Continuous Control Deep Reinforcement Learning

> [!abstract] 核心贡献
> ARP 把连续控制中 Gaussian policy 的 i.i.d. 白噪声探索项替换成 **边缘分布仍为标准正态、但时间上相关的平稳 AR-p 高斯过程**，使策略在不改变确定性均值策略表达能力的前提下，产生更平滑、更安全、更适合高 action-rate 机器人控制的探索轨迹。

> [!tip] 与理论基础的关联
> - [[StochasticProcess]]：从 AR-p 平稳性、characteristic roots、Yule-Walker 方程构造单位方差 Gaussian process。
> - [[ReinforcementLearning]]：把 history-dependent policy 写成扩展 MDP $\tilde M^p$ 中的 Markov Gaussian policy，因此可接 PPO/TRPO 等现成算法。
> - [[SignalProcessing]]：ARP 等价于给探索噪声加入可调 temporal spectrum，而不是对最终动作做黑箱低通滤波。
> - [[ControlTheory]]：高频白噪声在速度/力矩控制中会导致原地抖动和硬件风险；时间相关探索更符合机械系统带宽。
>
> **核心技术**: stationary AR-p Gaussian process, temporally coherent exploration, history-dependent Gaussian policy, extended MDP, PPO-compatible log-prob, action-rate robustness

> [!note] 精确锚点与探索子簇定位
> - [[ReinforcementLearning#5.4.1 时间一致探索：从白噪声到自回归过程]] — 本文正是该节讲述的「时间一致探索」原型：只把 Gaussian policy 的白噪声 $\epsilon_t$ 换成平稳 AR-p 过程 $X_t\sim\mathcal{N}(0,1)$，边缘不变、时间相关 $\mathrm{corr}(X_t,X_{t-k})\ne0$。
> - [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功]] — ARP 的价值在高 action-rate/稀疏奖励下：白噪声步间抵消→原地抖动，AR 噪声让多步动作朝相近方向累积形成可执行运动。
> - **簇内 Delta（探索子簇三元组）**：与 [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]] 的 Delta——后者给探索方差 $\sigma^*$ 的 LQ 最优**幅度**（单步边缘），ARP 给探索噪声的**时间结构**（跨步自相关），二者正交可叠加；与 [[Dynamic Reinforcement Learning for Actors|Dynamic RL]] 的 Delta——ARP 是显式外部 AR 噪声，Dynamic RL 是 RNN 内生混沌，都在追求「探索有时间结构」。

## 0. 阅读定位与范本价值

这篇论文容易被误读成“给动作加平滑滤波”。它真正的区别在于：作者没有把最终动作 $a_t$ 做 moving average，而是只替换 Gaussian policy 里的 **探索噪声分量**。确定性均值 $\mu_\theta(s_t)$ 仍然可以表达任意 Markov deterministic policy；被时间相关化的是 $\epsilon_t$ 这部分随机探索。

这个 distinction 对机器人很重要。动作低通滤波会改变 MDP 的 action semantics：策略说“动一下”，环境实际执行的是过去多个动作的混合，学习问题会变得部分可观测。ARP 则把历史依赖显式放进 policy distribution，在扩展 state 里仍然是普通 Gaussian policy，可以继续用 PPO/TRPO 训练。

对当前 WMTS/灵巧手知识库，ARP 的价值不是“解决高维手控制”，而是一个探索分布设计原则：高频连续控制下，i.i.d. Gaussian noise 很可能只产生抖动，无法推动状态进入有奖励区域；探索需要与机械系统带宽、控制频率和任务尺度匹配。

| 四支柱 | 本文需要读出的颗粒度 | 在本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么白噪声探索在高频机器人控制中失效，ARP 相对 OU/action smoothing 的 delta 在哪里 | §1, §4 |
| 原理与理论 | AR-p 平稳过程、Yule-Walker、扩展 MDP、ARP log-prob 如何无跳步连接 | §2 |
| 实验与验证 | toy sparse reward、MuJoCo dense reward、UR5 real robot 如何分别支撑或限制故事 | §3 |
| 未来与结合 | 如何迁移到 PPO Oracle/LinkerHand，哪些地方不能过度外推 | §5-§7 |

## 1. 问题设定与动机

### 1.1 一句话核心

标准连续控制策略通常写成对角 Gaussian：均值随状态平滑变化，但噪声每步独立；在高 action-rate、速度/力矩控制和稀疏奖励任务中，这种白噪声探索会变成局部抖动而不是有效状态空间探索。ARP 的结构性赌注是：**保持每步边缘分布不变，只改变噪声的时间相关结构**。

### 1.2 直观隐喻

Gaussian 探索像一个人每 10 毫秒随机决定下一步往哪推，方向完全不记得上一刻；ARP 像一个人保持一个短时意图，连续几步朝相近方向探索，然后逐渐改变。前者在高频控制下常常原地抖，后者能形成一段可产生位移的探索片段。

这个隐喻可证伪：如果任务有 dense reward 且不需要通过平滑运动发现奖励，ARP 不应显著优于 Gaussian；如果 action rate 提高而动作是低层 velocity/torque，Gaussian 应该急剧恶化，而 ARP 可通过提高 $\alpha$ 恢复探索尺度。论文实验正是这样组织的。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 | ARP 的 Delta |
|---|---|---|---|
| Gaussian policy | 每步 action 独立采样，边缘分布简单可微 | 白噪声不产生持续运动；action rate 越高越像原地震动 | 保留标准正态边缘，但让噪声跨时间相关 |
| Action low-pass / moving average | 最终动作平滑 | 改变环境实际 action，若 agent 不知道滤波器会造成部分可观测和 credit mismatch | 平滑项显式在 policy 中，学习发生在扩展 MDP |
| Derivative action / higher-order control | action 表示高阶导数，天然平滑 | 改变 action space，最优策略可能不再对应原 MDP | 原始 action semantics 保留 |
| Motor primitives | 安全、平滑、低维 | 需要专家设计 primitive class，限制策略表达 | 不限定最终 deterministic policy class，只约束探索噪声结构 |
| OU noise | 一阶 temporally correlated Gaussian process | 只有 AR-1；高平滑时长程相关太强，容易变成近似常数 | 任意阶 AR-p，给定相邻平滑度时高阶过程长程相关衰减更快 |
| Parameter noise | 参数空间扰动产生 episode-level consistency | 与 action-space exploration 互补，但仍可能需要动作层平滑 | ARP 可叠加在参数噪声/curiosity/reward shaping 上 |

### 1.4 Delta 分析

ARP 的最干净 delta 是：

$$
a_t=\mu_\theta(s_t)+\sigma_\theta(s_t)\epsilon_t,
\quad \epsilon_t\sim\mathcal{N}(0,I)
$$

替换为：

$$
a_t=\mu_\theta(s_t)+\sigma_\theta(s_t)X_t,
\quad X_t\sim\text{stationary AR-p},\quad X_t\sim\mathcal{N}(0,I)\ \forall t.
$$

网络输出的均值/标准差接口不变；每个时刻的 noise marginal 也不变；变的是 $\mathrm{corr}(X_t,X_{t-k})$。因此它不是“让策略更保守”，而是“让相同幅度的随机性在时间上形成可执行运动”。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $s_t$ | 原始 MDP state / observation | environment | 无梯度；policy/value 输入 | 当前环境信息 | 论文形式写 state，实际 RL 也可用 observation |
| $a_t$ | 连续动作向量 | policy sample | 对 policy log-prob/gradient 有依赖 | 速度、力矩或 target command | ARP 不改变 action space |
| $\mu_\theta(s)$ | action 维均值向量 | policy network | 对 $\theta$ 有梯度 | deterministic mean policy | 最优 deterministic Markov policy 在 $\sigma\to0$ 时仍可表达 |
| $\sigma_\theta(s)$ | action 维标准差向量 | policy network | 对 $\theta$ 有梯度 | exploration scale | 不能和 AR innovation variance $\tilde\sigma_Z^2$ 混淆 |
| $\epsilon_t$ | i.i.d. $\mathcal{N}(0,I)$ | sampling noise | reparameterization/score function | Gaussian policy 白噪声 | 白噪声问题在时间维度，不是边缘方差太小 |
| $X_t$ | AR-p process observation | stochastic process | 不直接带环境梯度 | temporally coherent noise | $X_t$ 每步边缘仍为 $\mathcal{N}(0,1)$ |
| $p$ | integer AR order | method hyperparameter | 固定 | 历史长度 | 高阶不是更平滑本身，而是在相同 $\rho_1$ 下减少长程粘滞 |
| $\alpha$ | $[0,1)$ smoothing parameter | method hyperparameter | 固定 | temporal coherence 强度 | 最优 $\alpha$ 依赖 action rate 和任务尺度 |
| $\tilde\phi_k$ | AR coefficients | coefficient construction | 固定 | history terms 权重 | 一般 $p>1$ 的 innovation variance 不能简单写成 $\prod(1-\alpha_k^2)$ |
| $\tilde\sigma_Z^2$ | innovation variance | Yule-Walker solve | 固定 | 保证 stationary variance 为 1 | 对 $p=1$ 才有 $1-\alpha^2$ 简式 |
| $f_\theta(\tilde s_t)$ | normalized AR history term | past states/actions + current params | 对 $\theta$ 有梯度，因为含过去 $\mu_\theta,\sigma_\theta$ | exploration mean offset | 它形式上在 Gaussian mean 里，但语义上是探索分量 |
| $h_t^p$ | $(s_{t-p},a_{t-p},...,s_{t-1},a_{t-1})$ | rollout history | 无梯度数据；policy log-prob 使用 | ARP 所需历史 | 每个并行 env 必须维护独立 history |
| $\tilde M^p$ | extended MDP | theoretical construction | 不带梯度 | 让 history-dependent policy 变 Markov | critic 可只看 $s_t$，作者经验上更稳定 |

### 2.2 从标准 Gaussian policy 到问题根源

连续控制中常用对角 Gaussian policy：

$$
\pi_\theta(a_t|s_t)
=
\mathcal{N}(\mu_\theta(s_t),\sigma_\theta^2(s_t)I).
$$

采样可写成：

$$
a_t=\mu_\theta(s_t)+\sigma_\theta(s_t)\epsilon_t,
\qquad
\epsilon_t\sim\mathcal{N}(0,I).
$$

如果环境连续状态变化平滑，$\mu_\theta(s_t)$ 通常也随时间平滑。但在训练早期，$\mu_\theta$ 近似随机小值，真正推动探索的是 $\epsilon_t$。i.i.d. $\epsilon_t$ 的自相关是：

$$
\mathrm{corr}(\epsilon_t,\epsilon_{t+k})=0,\quad k\ne0.
$$

在速度/力矩控制中，连续两步动作方向无关会相互抵消。action rate 越高，每步时间 $\Delta t$ 越小，同样时长内噪声反复正负切换，物体/机器人状态移动得更少，硬件却承受高频抖动。

### 2.3 AR-p 平稳高斯过程从零构造

AR-p 过程定义为：

$$
X_t=\sum_{k=1}^{p}\phi_kX_{t-k}+Z_t,
\qquad
Z_t\sim \mathrm{WN}(0,\sigma_Z^2).
$$

平稳性要求均值不随 $t$ 变，协方差只依赖 lag：

$$
\mathbb{E}[X_t]=\mu,\qquad
\mathrm{cov}(X_t,X_{t-\tau})=\gamma_\tau.
$$

AR-p 的 characteristic polynomial：

$$
P(z)=z^p-\sum_{i=1}^{p}\phi_i z^{p-i}.
$$

若所有根都在单位圆内，过程平稳。作者从反方向构造：先选根 $\alpha_k\in[0,1)$，再令 polynomial 为：

$$
P(z)=\prod_{i=1}^{p}(z-\alpha_i).
$$

展开后得到 AR coefficients：

$$
\tilde\phi_k
=
(-1)^{k+1}
\sum_{1\le i_1<\cdots<i_k\le p}
\alpha_{i_1}\cdots\alpha_{i_k},
\qquad k=1,\ldots,p.
$$

因为所有 $\alpha_i$ 在单位圆内，所以这个 AR 过程平稳。接着用 Yule-Walker 方程解 $\gamma_1,\ldots,\gamma_p,\tilde\sigma_Z^2$，并固定 $\gamma_0=1$：

$$
\begin{bmatrix}
\gamma_1\\
\gamma_2\\
\vdots\\
\gamma_p
\end{bmatrix}
=
\begin{bmatrix}
1&\gamma_1&\cdots&\gamma_{p-1}\\
\gamma_1&1&\cdots&\gamma_{p-2}\\
\vdots&\vdots&\ddots&\vdots\\
\gamma_{p-1}&\gamma_{p-2}&\cdots&1
\end{bmatrix}
\begin{bmatrix}
\tilde\phi_1\\
\tilde\phi_2\\
\vdots\\
\tilde\phi_p
\end{bmatrix},
$$

并满足：

$$
1=\sum_{i=1}^{p}\tilde\phi_i\gamma_i+\tilde\sigma_Z^2.
$$

这样构造出的 $X_t$ 是 zero-mean、unit-variance Gaussian stationary process：

$$
X_t\sim\mathcal{N}(0,1)\quad \forall t.
$$

对 $p=1$，它退化为熟悉的一阶 AR：

$$
X_t=\alpha X_{t-1}+\sqrt{1-\alpha^2}\epsilon_t,
\qquad
\epsilon_t\sim\mathcal{N}(0,1).
$$

对 $p>1$，不要把 innovation variance 简单写成 $\prod_k(1-\alpha_k^2)$。论文是通过 Yule-Walker 线性系统求 $\tilde\sigma_Z^2$；appendix 只给了 AR-3 的闭式例子。

### 2.4 为什么需要高阶 AR，而不是只把 $\alpha$ 调大

单看相邻平滑度：

$$
\rho_1=\mathrm{corr}(X_t,X_{t+1})
$$

可以通过增大 $\alpha$ 让 AR-1 非常平滑。但 AR-1 在 $\rho_1$ 很高时，长程 autocorrelation 也衰减很慢，探索轨迹会长时间像常数一样漂。

论文 Fig. 2 固定 $\rho_1=0.99$ 比较不同阶数：$p=1,\alpha=0.99$ 的样本几乎是慢慢漂移的常值函数；$p=3,\alpha=0.79$、$p=5,\alpha=0.69$ 在相邻时间仍平滑，但远距离 lag 的相关更快下降，轨迹更有探索多样性。作者因此在后续实验固定 $p=3$，只调 $\alpha$。

### 2.5 从 AR process 到 AR policy

用 AR noise 替换 Gaussian white noise：

$$
a_t=\mu_\theta(s_t)+\sigma_\theta(s_t)X_t.
$$

展开 $X_t$：

$$
X_t=\sum_{k=1}^{p}\tilde\phi_k X_{t-k}+\tilde\sigma_Z\epsilon_t.
$$

又因为：

$$
X_{t-k}
=
\frac{a_{t-k}-\mu_\theta(s_{t-k})}{\sigma_\theta(s_{t-k})}.
$$

代回：

$$
a_t
=
\mu_\theta(s_t)
+
\sigma_\theta(s_t)
\sum_{k=1}^{p}\tilde\phi_k
\frac{a_{t-k}-\mu_\theta(s_{t-k})}{\sigma_\theta(s_{t-k})}
+
\sigma_\theta(s_t)\tilde\sigma_Z\epsilon_t.
$$

定义 history term：

$$
f_\theta(\tilde s_t)
=
\sum_{k=1}^{p}\tilde\phi_k
\frac{a_{t-k}-\mu_\theta(s_{t-k})}{\sigma_\theta(s_{t-k})}.
$$

于是 policy distribution 写成：

$$
\pi_\theta(a_t|\tilde s_t)
=
\mathcal{N}
\left(
\mu_\theta(s_t)+\sigma_\theta(s_t)f_\theta(\tilde s_t),
\sigma_\theta^2(s_t)\tilde\sigma_Z^2I
\right).
$$

这就是 ARP 的关键：它还是一个 Gaussian policy，只是 mean 中多了一个显式历史项，variance 中乘上 innovation variance。log-prob 可解析，PPO/TRPO 能直接用。

### 2.6 扩展 MDP 与最优性边界

因为 policy 依赖过去 $p$ 个 state-action pair，它在原 MDP $M$ 中不是 Markov policy。作者定义扩展 state：

$$
\tilde s_t=(s_{t-p},a_{t-p},\ldots,s_{t-1},a_{t-1},s_t).
$$

于是扩展 MDP：

$$
\tilde S=(S\times A)^p\times S,
\qquad
\tilde A=A.
$$

扩展环境的 transition 只是把历史窗口向前滚动，并把原 MDP 的 transition 放在最后一项。这样，ARP 在 $\tilde M^p$ 中是 Markov Gaussian policy，policy gradient theorem 和 PPO/TRPO 的使用条件仍然成立。

一个重要边界是 deterministic limit：

$$
\sigma_\theta(s_t)\rightarrow0
\Rightarrow
a_t=\mu_\theta(s_t).
$$

因此 ARP 不会排除原 MDP 中的 Markov deterministic policies。相比 action averaging，ARP 只平滑 exploration component，不限制最终 deterministic policy 的表达。

### 2.7 实现细节与符号陷阱

| 细节 | 正确做法 | 为什么重要 |
|---|---|---|
| episode 初始 $t<p$ | 只使用已有历史项，相当于缺失 $X_{t-k}=0$ | 避免任意初始化造成大 spike |
| 并行环境 | 每个 env 维护独立 $h_t^p$ | AR history 串 env 会污染 log-prob |
| update 发生在 episode 中 | 下一段 $p$ 步对 update 前的历史项使用旧 $\mu,\sigma$ normalization | 参数突然变更会让 $f_\theta$ 瞬间失真，产生 temporal spike |
| critic 输入 | 理论上可看 $\tilde s_t$，作者经验上只看 $s_t$ 更稳定 | critic 网络大小不随 $p$ 增长 |
| $\tilde\sigma_Z^2$ | 通过 Yule-Walker solve 保证 unit variance | 随便设会让边缘方差变，混淆“平滑”和“噪声幅度” |
| action bounds | 高斯/ARP 采样后仍可能被 clip | 增大 Gaussian variance 不能解决探索，因为多数动作会被边界截断 |

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设定 |
|---|---|
| 主算法 | OpenAI Baselines PPO |
| 附录验证 | TRPO，趋势类似但 Square sparse reward 中 PPO 更好 |
| AR order | 后续实验固定 $p=3$ |
| 对比 | conventional Gaussian policy vs ARP with different $\alpha$ |
| 网络/超参 | Gaussian 与 ARP 使用相同网络结构和算法超参 |
| Hyperparameter search | 没有为 ARP 单独搜索；作者刻意在 Gaussian tuned setting 下测试 |
| PPO $\gamma,\lambda$ | 0.995 |
| PPO clip | 0.2 |
| Hidden layers | 2 layers, hidden size 64 |
| Batch scaling | 高 action-rate 环境按模拟时间等比例放大 batch/optimization batch |

### 3.2 Fig. 2：高阶 AR 的必要性

Fig. 2 固定 $\rho_1=0.99$。AR-1 的 autocorrelation 随 lag 衰减最慢，sample path 近似常值；AR-3/AR-5 在保持相邻平滑的同时，远距离相关更快下降。

因果解释：平滑探索不是“越粘越好”。高 $\alpha$ 的 AR-1 会让探索长时间朝一个方向或停在一个模式上；高阶 AR 给出更短记忆、更丰富的曲线形状，因此作者选择 $p=3$ 作为平滑性和探索多样性的折中。

### 3.3 Square toy sparse reward：action rate 是白噪声探索的放大镜

Square 环境：2D state bounded in a $10\times10$ square，agent 控制 dot 的 velocity，初始在中心；target 随机在直径 5 的圆上；每步 reward 是 $-1$ 乘 time-step duration；靠近 target 到 0.5 内结束；action bounded in $[-1,1]^2$。

| 实验 | 关键信息 | 结论 |
|---|---|---|
| Random exploration, 10M simulated seconds | $\mu\approx0,\sigma\approx1$；比较 Gaussian 与 ARP $(p=3)$ | Gaussian 随 action rate 上升 average time-to-target 急剧恶化；ARP 可通过提高 $\alpha$ 恢复覆盖 |
| 10s trajectories at 10Hz vs 100Hz | Gaussian 100Hz 轨迹覆盖面积显著变小 | 高频白噪声相互抵消，状态空间探索变局部抖动 |
| Gaussian $\sigma=1$ vs $\sigma=10$ | 高方差多数动作被 clip 到边界 | 增大方差不能解决 bounded action space 中的探索尺度问题 |
| Learning, 50,000 simulated seconds, 5 seeds | 10Hz/20Hz/50Hz 三种控制频率 | action rate 越高，需要越大的 $\alpha$；ARP 初始随机行为回报显著高于 Gaussian |

因果解释：这组 toy 实验最直接证明 Pillar-1 故事。Gaussian 的问题不是方差不够，而是 temporal incoherence；在高频速度控制中，独立噪声的积分位移随频率上升变小。ARP 通过时间相关噪声让多步 action 朝相近方向累积，因此更可能到达稀疏 reward 区域。

### 3.4 MuJoCo dense rewards：ARP 不是万能增益

MuJoCo 任务包括 Reacher-v2、Swimmer-v2、Hopper-v2、Walker2d-v2、HalfCheetah-v2。这些任务 reward dense，因此 exploration coherence 不是主要瓶颈。

论文观察是：ARP overall 与 Gaussian 持平或略优；Swimmer-v2 上 ARP 明显更好，可能因为该任务本身奖励平滑推进；但某些 $\alpha$ 选择会伤害任务表现，例如过强平滑在需要快速动作变化的任务上会变慢或退化。

因果解释：这组结果是本文最重要的边界条件。ARP 的优势在 sparse reward/high action-rate/low-level control 中最强；在 dense reward benchmark 中，它不是免费提升器。正确使用方式是把它当 exploration prior，而不是普适 policy architecture。

### 3.5 UR5 real robot：物理硬件上的关键证据

真实机器人实验是 UR5 Reacher 2D sparse reward：每步 reward 为 $-1$ 乘 time-step duration；距离 target 小于 0.05 结束；episode 时长扩到 8 秒。比较 25Hz 和 125Hz velocity control，每条曲线平均 4 个 random seeds。

| Action rate | Gaussian | ARP |
|---|---|---|
| 25Hz | 能学习但较慢/不稳定 | $\alpha=0.5$ 明显更快，$\alpha=0.8$ 也有效 |
| 125Hz | 5 小时限制内未学到有效策略 | ARP 在 50% runs 中找到有效策略；更高 $\alpha$ 在高 action-rate 更有效 |

因果解释：这是真实硬件上最贴近论文 claim 的证据。125Hz 下 Gaussian 白噪声对硬件表现为抖动，既不安全也难以探索到 target；ARP 的平滑 exploration 能在真实时间内形成 reach 行为。注意作者没有声称 100% runs 成功，50% runs 有效说明该方法仍受超参/随机性影响。

### 3.6 Ablation 因果链

| 改动 | 结果/现象 | 因果机制 | 使用含义 |
|---|---|---|---|
| Gaussian white noise | 高频 sparse reward 学习失败或很慢 | 噪声步间抵消，状态覆盖小，硬件 jerk | 高 control frequency 不能默认用 i.i.d. Gaussian |
| AR-1 + 极高 $\alpha$ | sample path 近似常数，长程粘滞 | 相邻相关高时长程相关也高 | 高平滑不等于好探索 |
| AR-p, $p=3$ | 平滑且更有轨迹多样性 | 保持高 $\rho_1$，但高 lag 相关更快下降 | 用阶数控制 spectrum shape |
| Dense reward MuJoCo | 持平或小幅提升 | 探索不是主要瓶颈，reward 已提供方向 | 不要把 ARP 当 universal benchmark booster |
| 高 action-rate UR5 | ARP 明显优于 Gaussian | 机械系统需要连续方向的低频探索 | 最适合真实机器人低层控制 |

## 4. 核心洞见

### 4.1 论文真正的 insight

最大熵 RL 常说“提高 entropy 促进探索”，但这句话只约束每个 state 的 action distribution，不保证跨时间的行为覆盖。对连续控制，尤其是速度/力矩控制，探索的基本单位不是单个动作，而是一段时间内的 action trajectory。

ARP 的 insight 是把 exploration 的统计结构从：

$$
\text{marginal variance}
$$

提升到：

$$
\text{marginal variance}+\text{temporal autocorrelation}.
$$

同样的边缘方差，白噪声会抖，AR noise 会走。

### 4.2 为什么这个设计有效

它同时满足三个条件：

1. **边缘分布不变**：$X_t\sim\mathcal{N}(0,1)$，所以不混淆噪声幅度和时间结构。
2. **探索项显式历史依赖**：policy 知道历史项，log-prob 解析，PPO/TRPO 可用。
3. **确定性策略空间不被限制**：$\sigma\to0$ 时回到 $a=\mu(s)$，不像 action averaging 改写最终控制语义。

这三者让 ARP 比“在动作后面加滤波器”更干净。

### 4.3 什么时候会失效

ARP 会在以下情形变弱：

1. reward dense 且不需要探索连续运动，MuJoCo 结果说明收益有限。
2. 任务需要高频快速变向，过大的 $\alpha$ 会让探索太粘。
3. action 是高层 waypoint/action chunk，而不是低层 velocity/torque，i.i.d. noise 的高频抖动问题会被上层抽象削弱。
4. 主要难点是跨动作维度协调，而不是时间平滑；ARP 的默认 vector form 是各维独立 AR，不能表达手指间相关。
5. 系统有强 action clipping/safety filter，ARP 的实际轨迹可能被底层过滤器改写，需要和控制层共同设计。

## 5. 替代方案与理论局限

### 5.1 理论维度

ARP 的 $\alpha$ 和 $p$ 固定，不随状态、接触模式或学习阶段变化。但机器人探索的合适平滑度显然是状态依赖的：自由空间接近目标时可以平滑大步探索，接触/插入时可能需要小幅修正，动态转笔释放瞬间又需要快速变化。

此外，ARP 只建模时间相关，不建模动作维度相关。对灵巧手，拇指、食指、中指之间的相关结构可能比单关节时间平滑更重要。单独 ARP 不能替代低秩 covariance、normalizing flow、diffusion policy 或 hand-structured action prior。

### 5.2 算法维度

ARP 依赖 log-prob 中的历史项，因此 replay/off-policy 使用时要非常小心历史一致性。论文主要用 PPO/TRPO；虽然作者说可以用于 off-policy，但如果 replay buffer 中没有完整 history 或参数更新后重新计算旧 log-prob，会破坏 distribution 解释。

对 PPO 来说，ARP 是可接入的，但实现上要保证 rollout buffer 保存足够的 $(s,a)$ history 和当时的 normalization term，不能只保存当前 $s_t,a_t,\log\pi_t$ 后事后重算。

### 5.3 工程/实验维度

| 局限 | 具体表现 | 对机器人系统的影响 |
|---|---|---|
| 超参敏感 | 最优 $\alpha$ 随 action rate 和环境尺度变化 | 控制频率换了就要重新标定 |
| 初始化/更新 spike | appendix 专门处理 $t<p$ 和参数更新后的历史项 | 真实机器人上 spike 可能危险 |
| 只处理探索 | 学成后的 deterministic policy 不一定更平滑，除非仍保留 stochastic/regularization | 需要和 action smoothing/controller 一起验证 |
| 实验规模有限 | UR5 只有 sparse reaching，4 seeds，ARP 125Hz 有效 runs 为 50% | 不能泛化为所有真实机器人任务必然提升 |
| 无 tactile/contact | 没有接触丰富灵巧操作 | 对转笔/抓握只能作为探索噪声模块，不是接触策略 |

## 6. 对用户研究的启发

### 6.1 对 WMTS / PPO Oracle 的迁移

WMTS 默认 PPO Oracle 可以把 diagonal Gaussian actor head 改成 ARP head，尤其用于高频连续控制仿真：

| PPO 组件 | 标准做法 | ARP 改造 |
|---|---|---|
| actor output | $\mu_\theta(s),\sigma_\theta(s)$ | 保持不变 |
| action sample | $\mu+\sigma\epsilon_t$ | $\mu+\sigma X_t$ |
| rollout buffer | 当前 $s,a,r,\log\pi$ | 额外保存每个 env 的 past $(s,a)$ 或 AR normalized terms |
| policy log-prob | 当前 Gaussian | history-conditioned Gaussian |
| critic | $V(s_t)$ | 仍可只用 $V(s_t)$，先复现论文经验 |

最适合测试的场景不是 dense reward locomotion，而是 sparse/long-horizon contact discovery，例如转笔初期找到可持续推动-接住循环，或真实 fine-tuning 中安全探索小范围动作。

### 6.2 对 LinkerHand / DNPM 的具体改造

LinkerHand 的 16+5 DOF 高维动作不应简单给每个维度同一个 $\alpha$。更合理的是按功能组或接触状态设不同平滑度：

| 动作组 | 可能的 ARP 设计 |
|---|---|
| 稳定支撑指 | 高 $\alpha$，避免抖动破坏接触 |
| 推动/拨动指 | 中等 $\alpha$，保留连续发力但允许改变方向 |
| 释放/接住阶段 | 状态依赖降低 $\alpha$，允许快速相位切换 |
| 腕/掌姿态 | 高 $\alpha$ 或低频 action chunk |

更进一步，可以让 $\alpha$ 由 state/contact mode 预测：

$$
\alpha_t=\alpha_\psi(h_t^{tactile},h_t^{object},h_t^{phase}),
$$

但这已经超出原论文，需要重新处理 stationarity 和 log-prob。可先从固定 $\alpha$ 分组 ablation 开始。

### 6.3 可验证实验建议

1. **PPO diagonal Gaussian vs ARP-PPO**：在同一 LinkerHand 仿真任务上比较成功率、探索状态覆盖、action jerk、关节温升代理、接触丢失次数。若 ARP 只降低 jerk 不提高探索，说明瓶颈不在 temporal coherence。
2. **control frequency scaling**：固定任务，把 control decimation 从 20Hz/50Hz/100Hz/200Hz 改变。若 Gaussian 随频率升高掉得更快，而 ARP 可通过 $\alpha$ 恢复，说明论文机制在手上成立。
3. **per-joint vs grouped ARP**：每关节独立 AR、按手指共享 $\alpha$、按功能角色共享 $\alpha$。若 grouped ARP 更好，说明动作维相关不能忽视。
4. **ARP + safety filter**：测 ARP 输出经过 actuator/command limiter 后的实际谱。若底层 limiter 已经强低通，ARP 的额外收益可能很小。

### 6.4 不应过度外推的点

ARP 不会自动解决灵巧手的高维协调、接触建模、奖励稀疏、Sim-to-Real 或 actuator delay。它只解决一件事：让 stochastic exploration 在时间上更像可执行运动。对 WMTS，它应作为 PPO Oracle/exploration head 的一个可替换模块，而不是主算法故事。

## 7. 与知识体系的联系

### 与 [[StochasticProcess]] 的联系

本文是 AR-p 平稳过程在 RL policy distribution 中的直接应用。数学链条是：

$$
\text{unit-circle roots}
\rightarrow
\text{stationary AR coefficients}
\rightarrow
\text{Yule-Walker unit variance}
\rightarrow
X_t\sim\mathcal{N}(0,1)
\rightarrow
\text{Gaussian policy noise replacement}.
$$

它最值得复刻的不是公式本身，而是“先保持边缘分布不变，再改变时间结构”的实验控制思想。

### 与 [[SignalProcessing]] 的联系

ARP 是对探索噪声谱的设计。$\alpha$ 和 $p$ 改变 autocorrelation function，也就改变动作噪声的频谱。相比后处理 low-pass filter，ARP 把频谱约束纳入 policy distribution，使 log-prob 和 learning objective 一致。

### 与 [[ControlTheory]] 的联系

高频白噪声在真实机器人上不是“更多探索”，而是激发机械系统不想要的高频响应。论文的 UR5 结果说明，控制频率越高，探索分布越要考虑物理带宽。对 LinkerHand，这可以和 actuator latency、CAN bandwidth、servo command smoothing 放在同一条线审视。

### 与 [[ReinforcementLearning]] 的联系

ARP 对最大熵 RL 的提醒是：entropy 是 state-wise distribution property，不等于 trajectory-wise exploration quality。一个策略可以每步 entropy 很高，却在状态空间里几乎不移动。探索应看 trajectory distribution，而不是只看 $\mathcal{H}(\pi(\cdot|s_t))$。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| ARP 相对 Gaussian policy 的精确 delta 是什么？ | 只替换 $\epsilon_t$ 为 stationary AR-p $X_t$，保持 $X_t\sim\mathcal{N}(0,1)$，不改变均值策略表达。 |
| 为什么不是简单 action smoothing？ | action smoothing 改变最终 action semantics；ARP 把历史项写进 policy distribution，在扩展 MDP 中可用 PPO/TRPO。 |
| AR-p 如何保证边缘标准正态？ | roots $\alpha_i$ 在单位圆内保证平稳，再用 Yule-Walker 设 $\gamma_0=1$ 解 $\tilde\sigma_Z^2$。 |
| 高阶 AR 为什么有用？ | 同样 $\rho_1$ 下，AR-1 长程相关太强，高阶 AR 远距离相关衰减更快，既平滑又不粘滞。 |
| 实验如何证明故事？ | Square/UR5 sparse reward 和高 action-rate 最支持；MuJoCo dense reward 只持平/略优，是边界条件。 |
| 对灵巧手怎么用？ | 作为 PPO exploration head；按手指/接触角色设 $\alpha$；验证 jerk、状态覆盖、接触丢失，而不是只看 return。 |

## References

- Korenkevych, Dmytro, A. Rupam Mahmood, Gautham Vasan, and James Bergstra. 2019. *Autoregressive Policies for Continuous Control Deep Reinforcement Learning*. arXiv:1903.11524.
- Brockwell, Peter J., Richard A. Davis, and Matthew V. Calder. 2002. *Introduction to Time Series and Forecasting*.
- Schulman, John et al. 2017. *Proximal Policy Optimization Algorithms*.
- Lillicrap, Timothy P. et al. 2015. *Continuous Control with Deep Reinforcement Learning*.
