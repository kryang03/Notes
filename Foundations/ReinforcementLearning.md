---
tags:
  - foundation
  - reinforcement-learning
  - dexterous-manipulation
  - sim-to-real
aliases:
  - 强化学习
  - RL
  - PPO
  - SAC
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[Optimization]]"
  - "[[StochasticProcess]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
---

# 灵巧操作中的强化学习：接触动力学、流形几何与算法演进

# Reinforcement Learning in Dexterous Manipulation: Contact Dynamics, Manifold Geometry, and Algorithmic Evolution

> [!tip] 相关领域
> - [[ControlTheory]] - RL 与经典控制的交叉（Safe RL, Stability-Certified RL）
> - [[Dynamics]] - 动力学模型是 Model-Based RL 的基础
> - [[Optimization]] - RL 本质上是序贯决策优化
> - [[StochasticProcess]] - 扩散策略的理论基础
> - [[RepresentationLearning]] - 状态表征与多模态融合
> - [[EmbodiedAI]] - VLA 模型将 RL 与 LLM/VLM 结合实现端到端机器人学习
>
> **相关论文**:
> - [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] - 稳定性证书方法
> - [[Elastic Time Step Reinforcement Learning, VTS-RL]] - 弹性时间步
> - [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] - Lipschitz 约束网络

## 摘要 (Abstract)

本文档作为一份深度研究报告，旨在为Robotics Dexterous Manipulation（机器人灵巧操作）领域的构建Obsidian知识库提供理论基石。作为该领域的首席科学家，我将摒弃百科全书式的浅层描述，转而采用一种严谨、怀疑且深度的视角，剖析强化学习（Reinforcement Learning, RL）如何解决接触丰富（Contact-rich）、难以建模（Hard-to-model）的复杂操作任务。报告全文约15,000字，涵盖了从广义坐标与接触流形的物理本质，到DDPG、TD3、SAC等主流算法的数学推导与演进脉络，再到Sim-to-Real、触觉感知融合及Diffusion Policy等前沿技术的具体实现细节。

本报告的核心论点在于：灵巧操作的本质是混合动力学系统（Hybrid Dynamical System）中的模式切换（Mode Scheduling）与流形约束（Manifold Constraint）问题。传统的解析控制因无法有效处理接触的不连续性和感知噪声而失效，而现代强化学习算法通过熵正则化（Entropy Regularization）、守恒Q学习（Conservative Q-Learning）及世界模型（World Models）等机制，提供了一种隐式的、数据驱动的解决方案。

------

## 1. Core Concepts: 物理直觉与数学定义

在深入探讨算法之前，我们必须首先建立对灵巧操作物理本质的深刻理解。这不仅是算法设计的边界条件，也是理解为什么通用RL算法需要针对机器人领域进行特定改造的根本原因。

### 1.1 广义坐标与最大化坐标 (Generalized vs. Maximal Coordinates)

在构建强化学习的状态空间（State Space, $S$）时，首要决策是坐标系的选取。

#### 物理直觉

对于一个具有 $N$ 个关节的灵巧手（如Shadow Dexterous Hand, 24 DoF）和被操作物体，物理仿真引擎（如MuJoCo, Isaac Gym）底层虽然使用广义坐标（Generalized Coordinates, $q$）来求解拉格朗日方程，但在RL观测空间的设计中，我们经常面临选择：是直接使用关节角度 $q$，还是使用所有刚体的笛卡尔坐标（Maximal Coordinates）？

**广义坐标 ($q \in \mathbb{R}^n$)**： 广义坐标是一组定义系统构型所需的最小独立参数集 。对于串联机械臂，通常是关节角度。

$$q = [\theta_1, \theta_2,..., \theta_n]^T$$

其优势在于自然地满足了关节连接的几何约束（Holonomic Constraints），减少了状态空间的维度，使得学习效率更高 。

**最大化坐标 (Maximal Coordinates)**： 使用每个刚体（Link）在世界坐标系下的位置 $(x, y, z)$ 和姿态（四元数 $q_w, q_x, q_y, q_z$）来描述。 虽然这增加了维度，但在接触丰富的任务中，最大化坐标能更直接地反映物体间的相对距离和接触几何，有助于神经网络捕捉接触特征 。

#### 数学定义：拉格朗日动力学

机器人的运动方程通常描述为二阶微分方程：

$$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau + J(q)^T f_{ext}$$

其中：

- $M(q)$: 惯性矩阵（Inertia Matrix），对称正定。
- $C(q, \dot{q})$: 科里奥利力与离心力项（Coriolis and Centrifugal terms）。
- $g(q)$: 重力项。
- $\tau$: 关节力矩（Control Input）。
- $J(q)^T f_{ext}$: 外部接触力映射到关节空间的力矩。

**The Value-add of RL**: 传统控制论（如Computed Torque Control）试图通过逆动力学 $M(q)\ddot{q}_{des} +...$ 来消除非线性。然而，在灵巧操作中，$f_{ext}$（接触力）通常是未知、非平滑且高度非线性的 。RL 的价值在于，它不需要显式求解上述方程，而是通过与环境交互，学习一个策略 $\pi_\theta(a|s)$ 来隐式地处理这些动力学项，特别是难以建模的 $f_{ext}$ 。

### 1.2 接触流形与切空间探索 (Contact Manifolds & Tangent Space)

灵巧操作中最棘手的问题是**接触约束（Contact Constraints）**。当手指接触物体时，系统的自由度瞬间降低，状态被限制在一个低维流形上。

#### 几何视角

我们将允许的系统状态集合定义为约束流形（Constraint Manifold） $\mathcal{M}_c$：

$$\mathcal{M}_c = \{ (q, \dot{q}) \in \mathcal{X} \mid \phi(q) = 0, J(q)\dot{q} = 0 \}$$

其中 $\phi(q)$ 是接触距离函数（Signed Distance Function）。

在强化学习的探索阶段（Exploration），如果直接在全空间 $\mathbb{R}^n$ 添加高斯噪声（Gaussian Noise），会导致两种失效模式：

1. **穿透（Penetration）**：生成的指令导致手指穿入物体模型内部（在物理引擎中产生巨大的排斥力，导致仿真崩溃）。
2. **脱离（Detachment）**：意外断开接触，导致操作失败。

**Geometric Reinforcement Learning (G-RL)**  提出了一种深度的解决方案：策略应当在流形的切空间（Tangent Space, $T_q\mathcal{M}_c$）上学习，而不是在欧氏空间上。

- **Logarithmic Map**: 将流形上的点映射到切空间。
- **Exponential Map**: 将切空间上的动作映射回流形。

$$a_{safe} = \text{Exp}_q( \pi(s) )$$

这种几何先验（Geometric Prior）的引入，使得RL能够专注于学习“如何在保持接触的同时移动物体”，而不是浪费大量样本去学习“如何不穿透物体”这一基本的物理事实 。

### 1.3 混合动力学与非平滑性 (Hybrid Dynamics & Non-smoothness)

从动力学系统的角度看，灵巧操作是一个混合系统（Hybrid System）。

- **Mode 0 (Free Motion)**: 手指在空间运动，动力学平滑。
- **Mode 1 (Impact)**: 手指撞击物体，速度发生跳变（Velocity Jump），动量守恒但能量可能耗散。
- **Mode 2 (Sticking Contact)**: 摩擦锥（Friction Cone）内，相对速度为零 $v_{rel}=0$。
- **Mode 3 (Sliding Contact)**: 达到摩擦极限，遵循库伦摩擦定律 $f_t = \mu f_n$。

**Analytical Control Failure**: 解析方法（如MPC）在处理这种多模式切换时，面临组合爆炸（Combinatorial Explosion）。如果手有5个手指，每个手指有3种状态（Free, Stick, Slide），总的模式数量是 $3^5 = 243$ 种。规划器需要在每一帧决定处于哪种模式，这是一个混合整数规划（Mixed-Integer Programming）问题，通常是NP-hard的 。

**RL Insight**: 强化学习通过奖励函数（Reward Function）的引导，能够隐式地学习这种模式切换序列（Mode Scheduling）。例如，在旋转笔的任务中，策略网络会自动学习到“食指松开（Mode 0） -> 中指推（Mode 2） -> 拇指滑动（Mode 3）”的序列，而无需显式建模每个切换时刻 。这被认为是RL在灵巧操作中相对于传统控制最大的Value-add。

------

## 2. Evolution & Insights: 技术演进脉络 (Problem-Solution Chain)

该领域的发展并非线性堆叠，而是一系列针对“旧方法失效”的深刻反思与革新。我们将沿着 **Analytic Control -> Imitation Learning -> Model-Free RL -> Model-Based RL -> Offline RL** 的脉络进行解构。

### 2.1 The Failure of Analytic Control: 模型失配与计算瓶颈

**Problem**: 早期的灵巧操作依赖于精确的物理模型和轨迹优化（Trajectory Optimization）。

**Why it failed**:

1. **Sim-to-Real Gap的物理根源**：解析控制假设刚体接触，而在真实世界中，指尖通常是软的（Soft Pads），接触面存在变形、迟滞（Hysteresis）和微观纹理。接触力模型 $f = K \delta$ 中的刚度 $K$ 极其难以辨识 。
2. **LCP Solver Bottleneck**: 求解线性互补问题（LCP）以计算接触力，其计算复杂度随接触点数量呈立方级增长 $O(N^3)$。对于多指手操作网格物体，实时性无法保证 。

**Insights**: 我们需要一种对模型误差不敏感（Model-agnostic）且能实时推理的方法。这直接指向了 **Learning-based Policies**。

### 2.2 Imitation Learning (IL): 数据饥渴与分布漂移

**Problem**: 既然建模很难，能否直接模仿人类？ **Techniques**: Behavioral Cloning (BC), Inverse RL (IRL), GAIL 。 **Critique**:

- **Distribution Shift (Covariate Shift)**: 这是一个统计学上的致命伤。训练数据来自专家演示 $p_{data}(s)$，而策略执行时产生的状态分布是 $p_\pi(s)$。一旦机器人产生微小误差（例如手滑了一点），它进入了专家从未涉足的状态区域。由于BC没有纠错能力，误差会累积（Compounding Errors），导致系统发散 。
- **Data Efficiency**: 收集人类操作的高维数据（24 DoF hand + Object pose）极其困难。Mocap方案昂贵且受遮挡影响，VR遥操作效率低 。

**Insights**: 单纯的模仿是不够的，机器人需要一种机制在“未见过的状态”下通过试错（Trial-and-Error）来自我修正。这引入了 **Reinforcement Learning**。

### 2.3 深度强化学习的奠基：从 DQN 到连续控制

在进入机器人控制领域之前，我们需要理解深度 RL 本身的演进，因为这决定了哪些算法适合灵巧操作。

#### Phase 0: Deep Q-Network (DQN) — 深度 RL 的起点 (2013-2015)

**历史背景**: DeepMind 的 DQN 首次证明了深度神经网络可以稳定地学习价值函数。

**核心创新**:
1. **Experience Replay**: 打破样本相关性，允许样本重用
2. **Target Network**: 分离当前网络和目标网络，减少 bootstrap 的不稳定性

**为什么不能直接用于机器人**:
- DQN 只能处理**离散动作空间**（如 Atari 的按键）
- 灵巧手的关节是**连续**的，无法枚举所有可能动作

> [!note] 从离散到连续的桥梁
> 如何将 DQN 的稳定训练机制扩展到连续动作空间？这催生了两条演进路线：
> - **Actor-Critic 路线** → DDPG → TD3 → SAC
> - **Policy Gradient 路线** → TRPO → PPO

### 2.4 Off-Policy 演进线：从 DDPG 到 SAC

这是灵巧操作领域最活跃的研究方向。我们见证了算法从不稳定到鲁棒的进化。

#### Phase 1: Deep Deterministic Policy Gradient (DDPG) (2015)

**Mechanism**: Actor-Critic架构，使用确定性策略 $a = \mu(s)$。 **Why it failed in Dexterous Manipulation**: DDPG 存在严重的 **Overestimation Bias（Q值高估）**。在操作任务中，由于接触的不稳定性，偶尔的剧烈碰撞可能导致观测值的异常波动，Critic网络错误地认为这是高价值状态。由于使用的是 $\max Q$ 的更新逻辑，这种误差被快速放大，导致策略崩溃 。

> [!note] 教科书参考：Q值过高估计的数学证明
> 本节定理基于 Wang & Xiong "Deep Reinforcement Learning Notes" (Tsinghua University, 2024) Chapter 2.7

> [!theorem] Q值过高估计定理 (Theorem 2.1)
> 考虑状态 $s$，其中所有真实最优动作值相等：$Q^*(s, a) = V^*(s), \forall a$。
> 假设估计误差 $Q_t(s, a) - Q^*(s, a)$ 独立均匀分布在 $[-1, 1]$。则：
> $$\mathbb{E}\left[\max_a Q_t(s, a)\right] - V^*(s) = \frac{m-1}{m+1}$$
> 其中 $m$ 是动作数量。
> 
> **物理直觉**：即使估计是无偏的（误差期望为0），对这些估计取 $\max$ 操作后的结果**不再无偏**——它必然偏高。

> [!theorem] 更一般的过高估计界 (Theorem 2.2)
> 设 $Q^*(s, a) = V^*(s)$，估计满足弱无偏条件 $\sum_a (Q_t(s,a) - V^*(s)) = 0$，
> 且存在误差 $\sum_a (Q_t(s,a) - V^*(s))^2 = C > 0$。则：
> $$\max_a Q_t(s, a) \geq V^*(s) + \sqrt{\frac{C}{m-1}}$$
> 
> **关键洞见**：
> - 过高估计的程度与误差方差 $C$ 成正比（估计越不稳定，高估越严重）
> - 与动作数量 $m$ 成反比（动作越多，单个动作误差的影响被摊薄）
> - **Double Q-learning 通过解耦"选择最佳动作"与"评估该动作的价值"两个步骤，从机制上避免了这种必然的过高估计**

#### Phase 2: Twin Delayed DDPG (TD3) (2018)

**Value-add**: 针对DDPG的缺陷，引入了三个关键改进，使其在机器人控制中变得可用 。

1. **Clipped Double Q-Learning**: 同时训练两个 Critic $Q_1, Q_2$，计算目标时取 $\min(Q_1, Q_2)$。
   - *Insight*: 在灵巧操作中，低估（Underestimation）比高估（Overestimation）更安全。低估只会导致学习变慢，而高估会导致策略采取危险动作（如过大的力矩）。
2. **Target Policy Smoothing**: 在目标动作中加入噪声 $\epsilon \sim \mathcal{N}(0, \sigma)$。
   - *Physical Intuition*: 这在物理上对应于寻找“宽极小值”（Flat Minima）。如果一个抓取姿态仅在精度为0.1mm时有效，而在0.2mm偏差下就失效，那么这个姿态是不可用的。平滑操作迫使RL学习那些对执行误差鲁棒的动作策略。

#### Phase 3: Soft Actor-Critic (SAC) - The Gold Standard

**Mechanism**: 最大熵强化学习（Maximum Entropy RL）。

目标函数：$J(\pi) = \sum \mathbb{E} [r_t + \alpha H(\pi(\cdot|s_t))]$。

**Why SAC dominates Robotics**:

1. **Stochastic Policy as Compliance**: SAC学习的是随机策略 $\pi(a|s) \sim \mathcal{N}(\mu, \sigma)$。在物理交互中，策略的方差 $\sigma$ 可以被解释为一种**虚拟柔顺性（Virtual Compliance）**。当 $\sigma$ 较大时，意味着该维度不需要精确控制（Soft）；当 $\sigma$ 较小时，意味着需要高刚度控制（Stiff）。这天然契合了阻抗控制（Impedance Control）的思想 。
2. **Robustness**: 熵项鼓励探索，防止策略过早收敛到局部最优（例如：只是简单地握住物体不动，而不去尝试旋转它）。
3. **Stability**: 相比于PPO（On-policy），SAC（Off-policy）利用Replay Buffer，样本效率高出一个数量级，这对实机训练至关重要 。

> [!abstract] 策略约束与熵正则化的统一视角
> SAC 的最大熵目标实际上是一个更一般框架的特例。考虑带正则化的策略优化目标：
> 
> $$\max_\pi Q(s,a) - \beta \cdot D_{KL}(\pi(\cdot|s) \| \pi_0(\cdot|s))$$
> 
> 其中 $\pi_0$ 是**参考分布（Reference Distribution）**，$\beta$ 是温度参数。通过变分推导，最优策略具有 **Boltzmann 形式**：
> 
> $$\pi^*(a|s) = \frac{\pi_0(a|s) \cdot \exp(Q(s,a)/\beta)}{Z(s)}$$
> 
> **关键洞见**：当 $\pi_0$ 是**均匀分布**时，KL 散度退化为负熵：
> $$D_{KL}(\pi \| \text{Uniform}) = -H(\pi) + \text{const}$$
> 
> 因此，**SAC 的熵正则化实际上是 KL 约束到均匀先验的特例**。这一统一视角揭示了不同 RL 算法的本质差异仅在于：
> - **SAC**: $\pi_0 = \text{Uniform}$ （不对动作有先验偏好）
> - **PPO with KL penalty**: $\pi_0 = \pi_{old}$ （信任旧策略）
> - **π₀ (Physical Intuition AI)**: $\pi_0$ 来自物理直觉或人类演示
> 
> 这为设计新算法提供了清晰的设计空间：**选择什么样的参考分布 + 如何调节温度 $\beta$**。

> [!tip] Gaussian 探索的理论最优性（来自 [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]]）
> Wang et al. (2019) 用**连续时间随机控制**框架证明了一个深刻结果：对于 **Linear-Quadratic 问题**，熵正则化下的最优探索分布是 **Gaussian**：
> $$\pi^*(a|s) = \mathcal{N}(\mu^*(s), (\sigma^*)^2)$$
> 
> **分离原则**：
> - **均值** $\mu^*(s)$：仅依赖状态，与温度 $\lambda$ 无关 → 负责**利用**（exploitation）
> - **方差** $(\sigma^*)^2 \propto \lambda$：与状态无关，与温度成正比 → 负责**探索**（exploration）
> 
> 这意味着 SAC 使用 Gaussian 策略不只是"方便采样"，而是在 LQ 近似下的**理论最优选择**。
> 
> **额外洞见**：环境噪声越大，最优探索方差**越小**——因为随机环境本身就提供了"免费"的探索机会。

#### SAC 数学理论推导

> [!note] 教科书参考
> 本节基于 Haarnoja et al. "Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor" (ICML 2018) 原论文的理论推导。Deep RL 教科书标注 "Add SAC"，此处补充完整理论。

SAC 的理论基础是**软贝尔曼方程 (Soft Bellman Equation)** 和**软策略迭代 (Soft Policy Iteration)**，它将标准 RL 中的所有 max 操作替换为 soft-max（即 log-sum-exp），从而自然地引入熵正则化。

##### 软值函数定义

**软状态值函数** $V^\pi_{soft}(s)$ 和**软动作值函数** $Q^\pi_{soft}(s, a)$ 定义为：

$$V^\pi_{soft}(s) = \mathbb{E}_{a \sim \pi}\left[Q^\pi_{soft}(s, a) - \alpha \log \pi(a|s)\right]$$

$$Q^\pi_{soft}(s, a) = r(s, a) + \gamma \mathbb{E}_{s' \sim p}\left[V^\pi_{soft}(s')\right]$$

其中 $\alpha > 0$ 是**温度参数**，控制熵项的权重。

**物理直觉**：$V^\pi_{soft}$ 不仅衡量"预期累积奖励"，还衡量"策略在该状态下的不确定性"。高熵策略在 $V_{soft}$ 意义下更"有价值"。

##### 软贝尔曼方程

> [!theorem] 软贝尔曼方程 (Soft Bellman Equation)
> 对于任意策略 $\pi$，软 Q 函数满足以下递归关系：
> $$Q^\pi_{soft}(s, a) = r(s, a) + \gamma \mathbb{E}_{s'}\left[\mathbb{E}_{a' \sim \pi}\left[Q^\pi_{soft}(s', a') - \alpha \log \pi(a'|s')\right]\right]$$
> 
> 等价地，对于**最优软 Q 函数** $Q^*_{soft}$：
> $$Q^*_{soft}(s, a) = r(s, a) + \gamma \mathbb{E}_{s'}\left[\alpha \log \sum_{a'} \exp\left(\frac{Q^*_{soft}(s', a')}{\alpha}\right)\right]$$
> 
> **证明思路**：最优软策略具有 Boltzmann 形式 $\pi^*(a|s) \propto \exp(Q^*_{soft}(s,a)/\alpha)$，代入 $V_{soft}$ 定义后化简得到 log-sum-exp 形式。

##### 软策略迭代收敛性

> [!theorem] 软策略迭代收敛定理
> 软策略迭代算法（交替执行软策略评估和软策略改进）收敛到最优软策略 $\pi^*$ 和最优软 Q 函数 $Q^*_{soft}$。
> 
> **软策略评估**：固定 $\pi$，通过软贝尔曼方程迭代更新 $Q^\pi_{soft}$。
> **软策略改进**：给定 $Q^\pi_{soft}$，更新策略为：
> $$\pi'(a|s) = \frac{\exp(Q^\pi_{soft}(s, a)/\alpha)}{Z(s)}$$
> 
> **关键性质**：软策略改进保证 $Q^{\pi'}_{soft}(s, a) \geq Q^\pi_{soft}(s, a)$（单调递增），且收敛到唯一的最优解。

##### SAC 实用算法：三个关键组件

SAC 将上述理论转化为实用的深度 RL 算法，包含三个可学习组件：

1. **软 Q 网络** $Q_\theta(s, a)$：通过最小化软贝尔曼残差训练
   $$L_Q(\theta) = \mathbb{E}_{(s,a,s') \sim \mathcal{D}}\left[\left(Q_\theta(s, a) - \left(r + \gamma \left(Q_{\bar\theta}(s', a') - \alpha \log \pi_\phi(a'|s')\right)\right)\right)^2\right]$$
   其中 $a' \sim \pi_\phi(\cdot|s')$，$\bar\theta$ 是目标网络参数。

2. **策略网络** $\pi_\phi(a|s)$：通过最大化期望软 Q 值训练
   $$L_\pi(\phi) = \mathbb{E}_{s \sim \mathcal{D}}\left[\mathbb{E}_{a \sim \pi_\phi}\left[\alpha \log \pi_\phi(a|s) - Q_\theta(s, a)\right]\right]$$
   注意：由于 $a$ 是从 $\pi_\phi$ 采样的，需要使用**重参数化技巧**使梯度可以反向传播。

3. **自动温度调整** $\alpha$：通过约束优化动态调节
   $$L_\alpha(\alpha) = \mathbb{E}_{a \sim \pi_\phi}\left[-\alpha \left(\log \pi_\phi(a|s) + \bar{\mathcal{H}}\right)\right]$$
   其中 $\bar{\mathcal{H}}$ 是目标熵，通常设为 $-\dim(\mathcal{A})$（动作空间维度的负值）。

> [!tip] 自动温度调整的物理意义
> 目标熵 $\bar{\mathcal{H}} = -\dim(\mathcal{A})$ 意味着：在动作空间中，策略应"平均保持每个维度 1 nat 的不确定性"。
> - 若当前策略熵 $> \bar{\mathcal{H}}$（太随机）→ $\alpha$ 减小 → 减少对熵的奖励
> - 若当前策略熵 $< \bar{\mathcal{H}}$（太确定）→ $\alpha$ 增大 → 鼓励更多探索
> 
> 这在灵巧操作中实现了**自适应刚柔调节**：初期保持"软"以探索不同抓取策略，后期变"刚"以精确执行已学到的最优策略。

##### SAC 演进脉络：SQL → SAC (v1) → SAC (v2)

| 版本 | 核心创新 | 局限性 |
|-----|---------|--------|
| **SQL** (2017) | 首次提出软 Q 学习，使用 SVGD 采样 | 采样效率低，难以扩展到高维 |
| **SAC v1** (2018) | 重参数化技巧 + 双 Q 网络 + 固定 $\alpha$ | 需要手动调节温度 |
| **SAC v2** (2019) | 自动温度调整 | 目前工业标准 |

**Comparison Table: DDPG vs TD3 vs SAC**

| **Feature**           | **DDPG**                 | **TD3**       | **SAC**                | **Relevance to Manipulation**                                |
| --------------------- | ------------------------ | ------------- | ---------------------- | ------------------------------------------------------------ |
| **Policy Type**       | Deterministic            | Deterministic | Stochastic             | Stochasticity models sensor noise & actuation errors well.   |
| **Critic Update**     | Single Q                 | Min(Q1, Q2)   | Min(Q1, Q2)            | Clipped Double Q prevents dangerous over-exertion of force due to Q-bias. |
| **Exploration**       | Ornstein-Uhlenbeck Noise | Action Noise  | Entropy Regularization | Entropy auto-tuning adapts exploration during delicate contact phases. |
| **Sample Efficiency** | High                     | High          | Very High              | Critical for reducing robot wear and tear.                   |
| **Stability**         | Low (Brittle)            | Medium        | High                   | SAC is the robust choice for contact-rich tasks.             |

> [!tip] 时间一致探索：从白噪声到自回归过程（来自 [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]]）
> 标准 Gaussian 探索的一个被忽视的问题是**时间不一致性**：
> $$a_t = \mu(s_t) + \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, \sigma^2)$$
> 
> 连续两步的噪声 $\epsilon_t, \epsilon_{t+1}$ 独立同分布，导致：
> - **高频抖动**：探索轨迹像"原地震动"，无法有效覆盖状态空间
> - **硬件损伤**：jerky 运动对机械关节造成冲击
> 
> **解决方案**：自回归探索（AR-p Process）
> $$\epsilon_t = \sum_{i=1}^{p} \phi_i \epsilon_{t-i} + \eta_t, \quad \eta_t \sim \mathcal{N}(0, \sigma_\eta^2)$$
> 
> 通过选择系数 $\{\phi_i\}$ 满足 Yule-Walker 方程，可以保持：
> - **边缘分布不变**：仍然是标准正态 → 不影响策略梯度
> - **可调时间相关性**：$\phi$ 越大 → 轨迹越平滑 → 探索越"坚持方向"
> 
> **灵巧操作应用**：高精度位置控制（如精密装配）需要高 $\phi$；快速反应任务（如接球）需要低 $\phi$。

### 2.5 On-Policy 演进线：从 TRPO 到 PPO

与 Off-Policy 路线并行发展的是 On-Policy 路线，它在某些场景下仍有独特价值。

#### Phase 1: Trust Region Policy Optimization (TRPO) (2015)

**核心问题**: Policy Gradient 方法的步长很难调节。步长太大 → 策略崩溃；步长太小 → 学习缓慢。

**解决方案**: 约束策略更新的 KL 散度在信任域内：
$$\max_\theta \mathbb{E}\left[\frac{\pi_\theta(a|s)}{\pi_{\theta_{old}}(a|s)} A(s,a)\right] \quad \text{s.t.} \quad D_{KL}(\pi_{\theta_{old}} \| \pi_\theta) \leq \delta$$

**局限性**: 需要计算 Fisher 信息矩阵的逆，计算复杂度高。

#### Phase 2: Proximal Policy Optimization (PPO) (2017)

**核心创新**: 用 Clipping 替代硬性 KL 约束：

$$L^{CLIP}(\theta) = \mathbb{E}\left[\min\left(r_t(\theta)A_t, \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)A_t\right)\right]$$

> [!tip] PPO Clipping 的物理直觉
> Clipping 意味着：**"如果新策略与旧策略差异过大，就不要再往那个方向更新了"**。
> - 防止策略突变导致的"手抖"
> - $\epsilon = 0.2$ 意味着策略概率比最多变化 20%

**PPO vs SAC 选择指南**:

| 场景 | 推荐 | 原因 |
|------|-----|------|
| 仿真大规模并行 | PPO | IsaacGym 数千并行环境弥补样本低效 |
| 真机训练 | SAC | Replay Buffer 允许重用历史数据 |
| 高维连续动作 | SAC | 最大熵探索更有效 |

#### 理论基础：Policy Gradient as Policy Iteration

> [!note] 教科书参考
> 本节基于 Wang & Xiong "Deep Reinforcement Learning Notes" Chapter 3.3-3.4

TRPO 的理论根基在于将策略梯度重新解释为**策略迭代**。这一框架揭示了为什么约束 KL 散度是合理的。

**核心定理**：新策略 $\pi_{\theta'}$ 相对于旧策略 $\pi_\theta$ 的性能提升可以表示为：

$$J(\pi_{\theta'}) - J(\pi_\theta) = \mathbb{E}_{\tau \sim p_{\theta'}(\tau)}\left[\sum_{t=0}^{\infty} \gamma^t A^{\pi_\theta}(s_t, a_t)\right]$$

**物理直觉**：新策略的性能提升量 = 用**旧策略的价值观**评估新策略所执行动作的优势之和。

**重要性采样推导**：
$$\mathbb{E}_{\tau \sim p_{\theta'}(\tau)}\left[\gamma^t A^{\pi_\theta}(s_t, a_t)\right] = \sum_t \mathbb{E}_{s_t \sim p_{\theta'}(s_t)}\left[\mathbb{E}_{a_t \sim \pi_{\theta}}\left[\frac{\pi_{\theta'}(a_t|s_t)}{\pi_{\theta}(a_t|s_t)} \gamma^t A^{\pi_\theta}(s_t, a_t)\right]\right]$$

**关键问题**：上式期望是关于 $p_{\theta'}(s_t)$ 的，但我们只有来自旧策略 $p_\theta(s_t)$ 的数据。能否用 $p_\theta$ 替代 $p_{\theta'}$？

> [!theorem] 分布间隙边界 (Distribution Gap Bound)
> 设 $\pi_\theta$ 和 $\pi_{\theta'}$ 两个策略的 KL 散度满足：
> $$\max_s D_{KL}(\pi_\theta(\cdot|s) \| \pi_{\theta'}(\cdot|s)) \leq \epsilon$$
> 则状态分布间隙有界：
> $$|p_{\theta'}(s_t) - p_\theta(s_t)| \leq O(\sqrt{\epsilon} \cdot t)$$
> 
> **关键洞见**：只要新旧策略在 KL 散度意义下"足够接近"，就可以安全地用旧策略的状态分布近似新策略。这正是**信任域**名称的来源。

这解释了 TRPO 为什么要约束 KL 散度：**不是任意的正则化，而是保证状态分布替换的理论合法性**。

### 2.6 Model-Based RL (MBRL): 样本效率与世界模型

**Problem**: 即使是SAC，也需要百万级的步数才能收敛。在真机上这需要几周时间。 **Evolution**: DreamerV3 。 **Insights**:

- **Learning in Imagination**: 在学习到的动力学模型（World Model）中进行规划，大大减少与物理世界的交互。
- **Handling Occlusion**: 灵巧操作中，手指经常遮挡物体。Dreamer 使用 RNN (Recurrent State-Space Model, RSSM) 来维护隐状态（Latent State），具有记忆功能，能够推断被遮挡物体的状态。相比之下，基于单帧图像的 SAC 经常因为遮挡而丢失目标 。

#### Model-Based RL 算法演进

> [!note] 教科书参考
> 本节基于 Wang & Xiong "Deep Reinforcement Learning Notes" Chapter 5

**Version 0.5（朴素方法）**：学习动力学 $f(s, a) = s'$，然后直接规划。

**问题**：分布不匹配 (Distribution Mismatch)。模型 $f$ 只在初始策略 $\pi_0$ 访问过的状态-动作空间上准确。当我们用学到的模型规划时，策略会访问模型未见过的区域，导致错误累积。

**Version 1.5（Model Predictive Control, MPC）**：
```
while True:
    学习动力学模型 f(s, a)
    for N steps:
        规划得到动作序列 a_1, ..., a_H
        仅执行第一个动作 a_1  ← MPC 核心
        观察新状态 s'
        将 (s, a, s') 加入数据集
```

> [!tip] MPC 的核心洞见
> 重规划频率越高，单次规划的精度要求越低。因为我们可以在下一步修正前一步的错误。这就像开车时频繁看路而非闭眼直行。

#### 不确定性感知模型 (Uncertainty-Aware Models)

**为什么需要不确定性**：规划本质是优化。如果模型因过拟合在某区域产生不切实际的乐观预测，优化器会**主动利用这个漏洞**，导致糟糕的动作。

> [!abstract] 两种不确定性
> - **Aleatoric（偶然）不确定性**：数据本身的噪声，物理世界的内在随机性
> - **Epistemic（认知）不确定性**：模型的不确定性，在数据稀疏区域缺乏置信度
> 
> 输出分布的熵只能捕捉 Aleatoric 不确定性。即使模型严重过拟合，只要所有数据点都符合过拟合模型，熵仍然很低。

**Bootstrap Ensemble 方法**：训练 $N$ 个独立模型，对新输入 $(s, a)$ 分别预测：
$$p(\theta|D) \approx \frac{1}{N} \sum_i \delta(\theta_i)$$

预测之间的**方差/分歧**反映认知不确定性。在规划时可以惩罚导致高不确定性的动作。

> **灵巧操作应用**：在接触丰富的操作任务中，模型在接触/非接触边界区域的不确定性最高。Ensemble 方法可以避免策略盲目进入这些高风险区域。

### 2.7 Offline RL 演进：从保守估计到生成式策略

**Problem**: 即使有大量离线数据（Offline Data），标准的 Off-policy RL 也会因为 OOD (Out-of-Distribution) 动作的高估而失败。

#### Phase 1: Conservative Q-Learning (CQL) (2020)

- **Logic**: 显式地压低数据集中未出现动作的Q值。
- **Insight**: 在灵巧操作中，这是"安全第一"的体现。只在已知安全的动作空间附近微调，严禁盲目探索导致的硬件损坏。

#### Phase 2: Implicit Q-Learning (IQL) (2021)

- **创新**: 避免对 OOD 动作的 Q 值估计，只使用 Expectile 回归。

#### Phase 3: Decision Transformer (2021)

- **范式转变**: 将 RL 重构为序列建模问题。

**Solution 2: Diffusion Policy** 

- **Problem with Gaussian**: 传统的 SAC 假设动作服从单峰高斯分布。但灵巧操作是**多模态（Multimodal）**的。例如，绕过障碍物可以从左绕，也可以从右绕，平均值（中间）是直接撞上去。
- **Innovation**: 使用去噪扩散概率模型（DDPM）生成动作。它可以精确建模非凸、多模态的动作分布，显著提升了模仿人类复杂操作的能力。

### 2.8 Exploration 理论：从信息论到技能发现

> [!note] 教科书参考
> 本节基于 Wang & Xiong "Deep Reinforcement Learning Notes" Chapter 6

**Problem**: 在稀疏奖励环境中，如何有效探索？灵巧操作任务中，成功抓取/旋转的奖励极其稀疏，随机探索几乎不可能触发。

#### 信息论基础

探索问题可以用信息论语言精确表述：

$$H(\pi(s)) = \mathbb{E}_{s \sim \pi}[-\log \pi(s)]$$

- **状态边缘熵** $H(\pi(s))$：策略 $\pi$ 对状态空间的**覆盖度**
- **互信息** $I(s_{t+1}; a_t) = H(s_{t+1}) - H(s_{t+1}|a_t)$：**"赋能度" (Empowerment)**

> [!tip] Empowerment 的物理直觉
> $I(s_{t+1}; a_t)$ 度量了"**控制力**"——我的动作能多大程度影响未来状态？
> - 第一项 $H(s_{t+1})$：希望下一状态多样（探索）
> - 第二项 $H(s_{t+1}|a_t)$：希望给定动作后下一状态确定（控制）

#### 无奖励探索：技能发现 (Skill Discovery)

**核心目标**：在没有外部奖励时，学习**多样化的技能**，以便后续迁移到具体任务。

**形式化目标**：
$$\max_\pi H(p(G)) - H(p(G|S)) = \max_\pi I(S; G)$$

其中 $G$ 是目标/技能，$S$ 是状态。

- 第一项：希望目标分布**多样**（学到不同的技能）
- 第二项：希望给定状态后目标**确定**（策略有控制力）

**代表工作**：
- **DIAYN** (Eysenbach et al., 2018): 学习可区分的技能
- **Skew-Fit** (Pong et al., 2020): 通过重加权实现状态覆盖

> **灵巧操作应用**：在接触预训练阶段，用技能发现方法让机器人自主探索不同的抓取姿态和接触模式，无需人工设计奖励。这些预训练技能可以加速下游任务的学习。

#### Exploration Bonus：内在动机

另一条路线是添加**内在奖励** (Intrinsic Reward)：
$$\tilde{r}(s, a) = r(s, a) + \beta \cdot \text{bonus}(s, a)$$

常见 bonus 设计：
- **Count-based**: $\text{bonus} \propto 1/\sqrt{N(s)}$（访问次数越少，奖励越高）
- **Prediction Error**: 用动力学模型预测误差作为新颖性度量
- **Information Gain**: $\text{bonus} = I(s'; s, a)$

#### Hindsight Experience Replay (HER)：从失败中学习

> [!tip] 关键突破
> [[Hindsight Experience Replay]] 提出了处理稀疏奖励的另一种优雅方案：**重标注目标**。

**核心思想**：人类能从失败中学到几乎和成功一样多的东西。HER 让智能体具备这种能力——将失败轨迹的实际到达状态作为"假装的目标"进行重放学习。

**算法流程**：
1. 收集轨迹 $\tau = (s_0, a_0, \ldots, s_T)$，目标 $g$
2. 标准回放：存储 $(s_t, a_t, r_t, s_{t+1}, g)$
3. **Hindsight 回放**：额外存储 $(s_t, a_t, r'_t, s_{t+1}, g')$
   - 其中 $g' = s_T$（轨迹末态作为新目标）
   - $r'_t$ 根据新目标重新计算

**为什么有效**：HER 自动形成从易到难的隐式课程。早期智能体能力弱，末态接近初态，学习短距离操作；能力提升后末态更远，逐渐学习复杂任务。

> **灵巧操作应用**：HER 是接触丰富任务的标准配置。手内旋转、非抓取操作等任务的子目标（如特定抓取姿态）可作为 HER 的重标注目标。

------

## 3. Implementation: 核心算法细节分析

本节将以 **Soft Actor-Critic (SAC)** 和 **TD3** 为例，剖析其在灵巧操作任务中的具体实现细节。代码将聚焦于算法逻辑，剔除所有冗余部分。

### 3.0 Off-Policy Actor-Critic 的理论基础与常见谬误

> [!note] 教科书参考
> 本节基于 Wang & Xiong "Deep Reinforcement Learning Notes" Chapter 4.4

在使用 Replay Buffer 实现 Off-Policy Actor-Critic 时，存在两个容易被忽视的**理论谬误**：

#### 谬误 1：目标值中的策略不一致

**错误做法**（朴素 Off-Policy）:
```
y_i = r_i + γ V̂^π(s'_i)  # 从 Replay Buffer 采样 s'_i
```

**问题**：当从 Replay Buffer 加载 $(s, a, s', r)$ 时，$s'$ 是由**旧策略**产生的，而非当前策略 $\pi_\theta$。

**修正**：用 Q 函数替代 V 函数，因为 $Q^\pi(s, a)$ 不要求 $a$ 来自 $\pi$：
$$y_i = r_i + \gamma \hat{Q}^\pi(s'_i, a'_i), \quad a'_i \sim \pi_\theta(\cdot|s'_i)$$

注意：$a'_i$ 是将当前状态 $s'_i$ 输入**最新策略网络**得到的动作，而非 Replay Buffer 中存储的历史动作。

#### 谬误 2：策略梯度中的动作不一致

**错误做法**:
```
∇_θ J(θ) ≈ (1/N) Σ_i ∇_θ log π_θ(a_i | s_i) Â^π(s_i, a_i)
```
其中 $a_i$ 来自 Replay Buffer。

**问题**：策略梯度要求 $a_i \sim \pi_\theta$，但 Buffer 中的动作来自旧策略。

**修正**：对每个采样状态 $s_i$，重新从当前策略采样动作 $a^\pi_i \sim \pi_\theta(\cdot|s_i)$：
$$\nabla_\theta J(\theta) \approx \frac{1}{N} \sum_i \nabla_\theta \log \pi_\theta(a^\pi_i | s_i) \hat{Q}^\pi(s_i, a^\pi_i)$$

> [!tip] 关键洞见：为什么用 Q 而不用 Advantage？
> 使用 $\hat{Q}^\pi$ 而非优势函数 $\hat{A}^\pi$ 虽然会**增加方差**（因为没有 baseline），但这里高方差是可接受的——因为我们不需要与仿真器交互来采样 $a^\pi_i$，只需将 $s_i$ 输入神经网络。因此可以通过**大量采样 $a^\pi_i$** 来降低方差，而不增加环境交互成本。

### 3.1 Soft Actor-Critic (SAC) Core Logic

SAC 的核心实现难点在于 **Reparameterization Trick** 和 **Automatic Entropy Tuning**。

#### 3.1.1 Reparameterization Trick (重参数化技巧)

为了让梯度能够反向传播过采样过程，我们不能直接从分布 $\pi$ 中采样 $a$。我们需要将随机性分离。

对于高斯策略：

$$a_t = \tanh(\mu_\phi(s_t) + \sigma_\phi(s_t) \odot \epsilon_t), \quad \epsilon_t \sim \mathcal{N}(0, I)$$

这里 `tanh` 用于将动作限制在机器人关节极限 $[-1, 1]$ 内。

**Python/PyTorch Implementation**:

Python

```
import torch
import torch.nn.functional as F
from torch.distributions import Normal

class GaussianPolicy(torch.nn.Module):
    def __init__(self, state_dim, action_dim, hidden_dim=256):
        super(GaussianPolicy, self).__init__()
        self.linear1 = torch.nn.Linear(state_dim, hidden_dim)
        self.linear2 = torch.nn.Linear(hidden_dim, hidden_dim)
        
        self.mean_linear = torch.nn.Linear(hidden_dim, action_dim)
        self.log_std_linear = torch.nn.Linear(hidden_dim, action_dim)
        
        # 物理意义：限制标准差范围。
        # 在灵巧操作中，LOG_STD_MAX过大导致电机剧烈抖动（高频噪声），
        # LOG_STD_MIN过小导致策略僵死（无法探索）。
        # 这是极其实用的工程Trick。
        self.LOG_STD_MAX = 2
        self.LOG_STD_MIN = -20
        self.action_scale = 1.0 # 假设动作已归一化
        self.action_bias = 0.0

    def forward(self, state):
        x = F.relu(self.linear1(state))
        x = F.relu(self.linear2(x))
        mean = self.mean_linear(x)
        log_std = self.log_std_linear(x)
        log_std = torch.clamp(log_std, self.LOG_STD_MIN, self.LOG_STD_MAX)
        return mean, log_std

    def sample(self, state):
        mean, log_std = self.forward(state)
        std = log_std.exp()
        normal = Normal(mean, std)
        
        # Reparameterization Trick
        # z ~ N(0, 1)
        x_t = normal.rsample()  
        
        # Enforcing Action Bound (Tanh squashing)
        y_t = torch.tanh(x_t)
        action = y_t * self.action_scale + self.action_bias
        
        # Log Prob Calculation with Jacobian Adjustment
        # 当对变量进行变换时，概率密度函数(PDF)会发生变化。
        # log_prob(a) = log_prob(u) - log |det(da/du)|
        # tanh的导数是 1 - tanh^2
        log_prob = normal.log_prob(x_t)
        
        # 这里的 1e-6 是为了防止 log(0)
        log_prob -= torch.log(self.action_scale * (1 - y_t.pow(2)) + 1e-6)
        log_prob = log_prob.sum(1, keepdim=True)
        
        return action, log_prob, mean
```

**Analysis**: 在灵巧操作中，`rsample` 的可导性至关重要。它允许策略网络直接“感知”到：如果在某个方向上减小方差 $\sigma$，Q值会如何变化。例如，在把销子插入孔的瞬间（Peg-in-hole），网络会自动学习到急剧减小方差以提高精度 。

#### 3.1.2 Automatic Entropy Tuning (自动熵调节)

在训练初期，我们需要高探索（高熵）；在末期，需要高精度（低熵）。固定的 $\alpha$ 很难兼顾。

SAC 将其转化为一个约束优化问题：

$$\min_\alpha \mathbb{E}[-\alpha (\log \pi(a|s) + \bar{\mathcal{H}})]$$

其中 $\bar{\mathcal{H}}$ 是目标熵（Target Entropy），通常设为 `-action_dim`。

**Implementation**:

Python

```
class SAC_Agent:
    def __init__(self, action_dim):
        self.target_entropy = -float(action_dim)
        # alpha 也是一个可学习的参数，通常取 log 以保证正定性
        self.log_alpha = torch.zeros(1, requires_grad=True, device=device)
        self.alpha_optimizer = torch.optim.Adam([self.log_alpha], lr=3e-4)

    def update_alpha(self, log_prob):
        # Dual Gradient Descent
        alpha_loss = -(self.log_alpha * (log_prob + self.target_entropy).detach()).mean()
        
        self.alpha_optimizer.zero_grad()
        alpha_loss.backward()
        self.alpha_optimizer.step()
        
        self.alpha = self.log_alpha.exp()
```

**Insight**: 这种机制在Sim-to-Real中表现为“自适应刚度”。当且仅当Agent对其策略非常有信心（log_prob高）时，$\alpha$才会下降，允许策略变得确定性（Stiff）。如果遇到未知扰动，预测不准，log_prob下降，$\alpha$上升，恢复探索（Soft），防止机械臂硬抗外力导致损坏 。

### 3.2 TD3 Core Logic: Target Policy Smoothing

TD3 的实现相对简单，但其对接触噪声的鲁棒性源于以下逻辑。

Python

```
def train_critic(self, replay_buffer, iterations=2):
    #... 从 Replay Buffer 采样...
    state, action, next_state, reward, not_done = replay_buffer.sample()

    with torch.no_grad():
        # Target Policy Smoothing
        # 物理意义：模拟执行误差。如果一个动作在加上微小扰动后Q值剧烈下降，
        # 说明该动作处于"尖峰"上，是不稳定的。TD3通过这种方式平滑Q函数。
        noise = (torch.randn_like(action) * self.policy_noise).clamp(
            -self.noise_clip, self.noise_clip
        )
        
        next_action = (self.actor_target(next_state) + noise).clamp(
            -self.max_action, self.max_action
        )

        # Clipped Double Q-Learning
        target_Q1 = self.critic_target_1(next_state, next_action)
        target_Q2 = self.critic_target_2(next_state, next_action)
        
        # 取最小值，抑制高估
        target_Q = torch.min(target_Q1, target_Q2)
        target_Q = reward + (not_done * self.discount * target_Q)

    #... Update Critics...
```

**Why relevant to Dexterous Manipulation**: 在物体表面滑动手指时，摩擦力的变化会导致状态的剧烈波动。Target Smoothing 相当于在Q函数的更新中引入了一个低通滤波器，滤除了由于接触瞬态（Contact Transients）引起的高频噪声，使得 Critic 学习到的是更本质的物理规律 。

------

## 4. Advanced State Space & Reward Engineering

算法只是引擎，数据（状态和奖励）才是燃料。针对灵巧操作，我们需要特殊的燃料配方。

### 4.1 触觉感知与表征学习 (Tactile Representation)

视觉在近距离操作中往往会被机械手自身遮挡（Self-occlusion）。触觉传感器（如GelSight, BioTac）至关重要。

**Challenge**: 触觉数据不仅是高维的，而且是非欧几里得结构的（Non-Euclidean）。手指表面是一个曲面。

**Approaches**:

1. **Tactile Images (CNNs)**: 将触觉压力分布展开为2D图像 。
   - *Pros*: 可以直接使用 ResNet 等成熟架构。
   - *Cons*: 引入了畸变（Distortion），特别是对于指尖球面的展开。
2. **Graph Neural Networks (GNNs)**: 将触觉单元（Taxels）建模为图的节点 。
   - *Core Logic*: 邻接矩阵 $A$ 定义了传感器表面的拓扑结构。
   - *Insight*: GNN 对手指表面的几何变形具有更好的不变性。当软指尖被压扁时，图结构能更好地保持局部特征的关系，而图像投影可能会产生剧烈的像素位移。

### 4.2 奖励工程：稀疏 vs. 密集 vs. 塑形 (Sparse vs. Dense vs. Shaping)

**Sparse Reward**: 只有完成任务得+1，否则0。

- *Pros*: 也就是最“纯粹”的奖励，保证学到的策略是最优的。
- *Cons*: 在灵巧操作这种高维空间中，探索到成功的概率几乎为零。

**Reward Shaping (Dense Reward)**:

$$R = w_1 \cdot \text{dist}(p_{obj}, p_{goal}) + w_2 \cdot \text{quat\_diff}(q_{obj}, q_{goal}) + w_3 \cdot \text{energy}$$

- *Insight & Risk*: 人工设计的奖励往往含有偏见（Bias）。例如，为了最小化距离，机器人可能会学会一种奇怪的抓握姿态，这种姿态虽然距离目标近，但无法进行下一步的旋转操作（Local Optima）。这就是所谓的“Reward Hacking” 。

**Solution**:

1. **ARES (Attention-based REward Shaping)** : 利用Transformer自动从演示数据中学习权重。
2. **Inverse Reinforcement Learning (IRL)**: 从专家演示中反推奖励函数。

------

## 5. Bridging the Gap: Sim-to-Real & Offline RL

在仿真中训练好的策略，往往在真机上直接失败。这是因为仿真无法完美模拟真实的物理世界（摩擦、软体形变、传感器噪声）。

### 5.1 域随机化 (Domain Randomization, DR) 与 自适应 (Adaptive DR)

**Standard DR**: 在训练时，随机扰动物理参数 $\xi$（质量、摩擦系数、电机阻尼）。

$$\xi \sim U[\xi_{low}, \xi_{high}]$$

目标是学习一个策略 $\pi$，使其在所有这些参数下都能工作：$\max_\theta \mathbb{E}_{\xi \sim p(\xi)} [J(\pi_\theta, \xi)]$ 。

**Adaptive Domain Randomization (ADR)**:

- *Problem*: 如果随机范围太大，问题可能无解；如果太小，无法覆盖真实世界。
- *Algorithm*: 像课程学习一样动态调整随机范围。
  - 如果策略性能 > 阈值，扩大范围（增加难度）。
  - 如果策略性能 < 阈值，缩小范围。
- *Insight*: ADR 实际上是在高维参数空间中寻找**可行性边界（Feasibility Boundary）**。OpenAI 的 Rubik's Cube 项目证明，这种方法可以让机器人适应极其恶劣的环境变化（例如给手戴上橡胶手套）。

**Sim-to-Real Comparison Table**

| **Method**                | **Mechanism**                           | **Pros**                                | **Cons**                               | **Use Case**                                 |
| ------------------------- | --------------------------------------- | --------------------------------------- | -------------------------------------- | -------------------------------------------- |
| **System Identification** | Fit simulation parameters to real data  | Accurate model                          | Requires precise measurements; static  | Well-structured environments                 |
| **Domain Randomization**  | Train across random physics parameters  | Robustness to unmodeled dynamics        | Conservative policies; harder to train | General robotic manipulation                 |
| **Adaptive DR (ADR)**     | Curriculum learning on parameter ranges | Finds feasible boundaries automatically | Computationally expensive              | Complex dexterous tasks (e.g., Rubik's Cube) |

> [!abstract] 课程学习比触觉更重要？（来自 [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]]）
> 一个反直觉的发现：**课程设计对灵巧操作学习的影响大于触觉传感器的有无**。
> 
> **实验设置**：三指手向下抓取 + 旋转球体（对抗重力）
> - 变量 1：课程策略（先 Lift → 后 Rotate、先 Rotate → 后 Lift、同时学习等）
> - 变量 2：触觉信息（无触觉 vs 3D 力向量）
> 
> **关键发现**：
> 1. 不同课程策略导致的性能差异 **>>** 有无触觉的差异
> 2. **无触觉也能学会**：某些课程下，仅凭本体感知即可成功
> 3. 课程像"Waddington Landscape"——引导学习向特定技能组合发展
> 
> **启示**：
> - 在设计 RL 训练时，**优先设计好课程**，而不是堆传感器
> - 课程隐含了对任务的先验知识——**课程即 inductive bias**
> - 触觉可能是"锦上添花"而非"必需品"（至少对某些任务）

> [!abstract] 数据飞轮：从演示到策略的闭环迭代（来自 [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]]）
> **核心问题**：人类手部演示数据通常有噪声且不完美，直接模仿效果差。
> 
> **数据飞轮（Data Flywheel）框架**：
> ```
> 人类运动捕捉 → 重定向到机器人 → 挖掘可跟踪演示
>      ↑                                    ↓
>      ←←← 用改进的策略挖掘更难的演示 ←←←←←
> ```
> 
> **关键机制**：
> 1. **同伦优化（Homotopy）**：从简化任务（如无重力）逐步过渡到完整任务
> 2. **RL + IL 协同**：高质量演示指导探索，RL 处理未覆盖状态
> 3. **迭代改进**：更好的策略 → 能跟踪更难的演示 → 更多训练数据 → 更好的策略
> 
> **技术细节**：
> - 运动重定向：$\hat{s}^{robot}_n = \mathcal{R}(s^{human}_n; \phi)$
> - 演示质量评估：跟踪误差低于阈值才保留
> - 课程权重：随训练进度逐步提升 IL 损失权重
> 
> **灵巧操作启发**：解决了"人类演示有噪声→策略学不好→需要更好演示"的鸡蛋问题。

> [!tip] 观测空间课程适应（来自 [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation|CSR]]）
> **Sim2Real 矛盾**：仿真可获取"上帝视角"信息（精确物体位姿、完整触觉），真实世界难以复现。
> 
> **标准 Asymmetric Actor-Critic (AAC) 的问题**：
> - Critic 用完整观测，Actor 用受限观测
> - **一步裁剪**：训练不稳定，性能下降严重
> 
> **CSR 课程式解决方案**：
> 1. **特征重要性排序**：$I_i = \mathbb{E}[|\partial \pi / \partial o_i|]$
> 2. **渐进移除**：从最不重要的特征开始
> 3. **Deep Random Generator**：用随机网络输出替代被移除特征（防止策略学会"零=某状态"）
> 
> **课程设计**：
> ```
> Stage 0: 全部特征（精确物体位姿 + 触觉力 + 关节状态）
> Stage 1: 移除物体姿态（最不重要）
> Stage 2: 移除触觉力
> Stage 3: 仅保留关节本体感知
> ```
> 
> **启示**：
> - **渐进优于突变**：策略有时间适应每次缩减
> - **随机替代优于置零**：防止新的虚假依赖
> - **特征重要性可自动发现**：无需人工猜测

### 5.2 真实世界高效 RL: SERL 与 Human-in-the-Loop

> [!tip] 论文参考
> - [[SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning]] - 真实世界 RL 系统
> - [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning]] - 人在回路校正

#### RLPD: 演示增强的 Off-Policy RL

**核心创新**: 在每个训练步，从**演示数据**和**在线数据**各采样 50%

$$\mathcal{B}_{\text{train}} = \text{sample}(\mathcal{B}_{\text{demo}}, 50\%) \cup \text{sample}(\mathcal{B}_{\text{online}}, 50\%)$$

**为什么有效**:
- 演示提供初始探索方向
- 在线数据允许超越演示
- 50% 比例经验证最优

#### Human-in-the-Loop 校正机制

**关键洞察**: 人类校正 ≠ 人类演示

| 类型 | 数据内容 | 学习信号 |
|-----|---------|---------|
| 演示 | 成功轨迹 | 正样本模仿 |
| **校正** | **失败边缘的挽救** | **从错误中学习** |

**校正机制**:
```
策略执行中...
    ↓
人类观察到即将失败
    ↓
人类通过 SpaceMouse 接管
    ↓
(s_t, a_human, r, s_{t+1}) → Buffer
    ↓
策略学习: "在 s_t, 应该做 a_human, 不是 a_policy"
```

**实验结果** (HIL-SERL):
- 训练时间: 1-2.5 小时
- 成功率: 相比 BC 提升 **101%**
- 任务: 首次实现双臂 RL + 动态 Jenga 抽取 + 时序带装配

#### 真实世界 RL 系统设计要点

| 组件 | SERL 方案 | 原因 |
|-----|----------|------|
| 算法 | RLPD (SAC 变体) | 高 update-to-data ratio |
| 奖励 | 二值分类器 | 避免手工设计 |
| 重置 | 前向-后向策略 | 自动化训练 |
| 控制器 | 阻抗控制 | 接触安全 |

### 5.3 Offline RL: 从静态数据中学习

很多时候我们不希望在真机上进行危险的探索，而是利用现有的历史数据。

**CQL (Conservative Q-Learning)** 的核心数学修正：

$$\min_Q \alpha \left( \mathbb{E}_{s \sim \mathcal{D}, a \sim \mu(a|s)} [Q(s, a)] - \mathbb{E}_{s \sim \mathcal{D}, a \sim \pi(a|s)} [Q(s, a)] \right) + \frac{1}{2} \mathbb{E}$$

- *Logic*: 第一项显式地压低当前策略 $\pi$ 产生的动作（可能由于高估而错误地被认为高价值）的Q值，同时拉高数据集中实际动作 $\mu$ 的Q值。
- *Significance*: 在灵巧操作中，这防止了机器人尝试那些“看起来很美但从未尝试过”的危险动作 。

------

## 6. Future Frontiers: Model-Based & Diffusion

### 6.1 DreamerV3: World Models for Manipulation

DreamerV3 通过学习 $p(s_{t+1}|s_t, a_t)$ (Dynamics) 和 $p(o_t|s_t)$ (Decoder) 来构建世界模型。 **Impact**: 对于操作任务，最重要的贡献是其 **RSSM (Recurrent State-Space Model)** 结构。它将状态分解为确定性部分（RNN hidden state）和随机部分（Stochastic state）。确定性部分充当了短期记忆（Short-term Memory），能够记住几帧前看到的物体位置，从而在当前帧物体被手指完全遮挡时，依然能准确预测物体状态。这解决了 Model-Free 方法在部分可观测性（Partial Observability）下的根本缺陷 。

### 6.2 Diffusion Policies: 多模态分布的终极解

**Diffusion Policy** 将策略建模为条件去噪过程：

$$a_k \leftarrow a_{k+1} - \alpha \nabla \log p(a_{k+1}|s) + \mathcal{N}(0, \sigma)$$

它不仅是模仿学习的SOTA，现在正逐渐与RL结合（RL-guided Diffusion）。 **Value-add**: 在复杂操作（如双手解绳结）中，动作空间是高度多模态的。Diffusion Policy 是目前唯一能有效捕捉并复现这种多模态分布的架构，标志着从“拟合均值”向“拟合分布”的范式转变 。

------

## 7. Conclusion: 走向物理感知的智能

综上所述，强化学习在灵巧操作领域的成功，并非单纯依赖于算力的堆砌，而是源于对物理问题的深刻抽象与算法适配：

1. **SAC** 通过熵正则化，巧妙地将物理柔顺性（Compliance）编码进控制策略，解决了接触刚性问题。
2. **Geometric RL** 通过流形约束，解决了高维空间探索效率低下的问题。
3. **Sim-to-Real (ADR)** 通过在参数空间的主动扩张，弥合了理想模型与真实世界的鸿沟。
4. **World Models** 通过隐空间的记忆机制，解决了操作过程中的遮挡与部分可观测性问题。

未来的研究方向将是 **Physics-Informed RL** 与 **Generative Models** 的深度融合。我们不再是将机器人视为一个黑盒MDP，而是利用接触力学和几何学的先验知识，去引导Diffusion Policy的生成过程，最终实现具备人类级别灵巧度与适应性的机器人系统。

这是从“计算”回归“物理”的必经之路。

------

## 8. Learning Resources

> **Source**: From [[Projects/Lumina-Embodied-AI-Reference|Lumina Embodied AI Guide]]

### Courses

| Level | Resource | Link | Notes |
|-------|----------|------|-------|
| **Math Foundation** | Shiyu Zhao (Westlake): RL Math | [bilibili](https://www.bilibili.com/video/BV1sd4y167NS) | Systematic derivations |
| **DRL Overview** | Pieter Abbeel 6 Lectures | - | Quick framework |
| **DRL Systematic** | Berkeley CS285 (Levine) | [website](https://rail.eecs.berkeley.edu/deeprlcourse/) | Industry standard |
| **DRL Chinese** | Hung-yi Lee RL | - | Practice-friendly |
| **Hands-on** | EasyRL (Mushroom Book) | [GitHub](https://github.com/datawhalechina/easy-rl) | Practical |

### Policy Baselines

| Method | Code | Features |
|--------|------|----------|
| ACT | [GitHub](https://github.com/tonyzhaozh/act) | Classic IL baseline |
| Diffusion Policy | [GitHub](https://github.com/real-stanford/diffusion_policy) | Robust diffusion-based |
| DP3 | [GitHub](https://github.com/YanjieZe/3D-Diffusion-Policy) | 3D representation |

### Simulators

| Platform | Link | Use Case |
|----------|------|----------|
| Isaac Lab | [GitHub](https://github.com/NVIDIA-Omniverse/IsaacLab) | GPU parallel training |
| legged-gym | [GitHub](https://github.com/leggedrobotics/legged_gym) | Legged robots |
| SAPIEN/ManiSkill | [Website](https://sapien.ucsd.edu/) | Manipulation |
| Genesis | [Website](https://genesis-world.readthedocs.io/) | New GPU simulator |

------

## 9. 相关论文 (PapersRecap)

以下论文涉及本 Foundation 中的强化学习理论与方法：

### SAC与最大熵RL
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]: SAC用于触觉灵巧操作
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]]: 纯触觉RL策略
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture|Dextrous Tactile]]: 模块化RL架构

### 课程学习与渐进训练
- [[Curriculum Learning|Curriculum Learning]]: 课程学习的理论基础
- [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation|Curriculum vs Haptic]]: 课程设计对操作学习的影响
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation|Curriculum Sensing Reduction]]: 传感课程与Sim-to-Real

### Sim-to-Real迁移
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]]: 在线修正的策略迁移
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]]: 真实演示辅助的迁移
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation|CyberDemo]]: 仿真演示增强

### 模仿学习与行为克隆
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills|DeepMimic]]: 参考动作引导的深度RL
- [[DexTrack - Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]]: 人类参考的神经跟踪控制
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]: 规划引导的扩散策略

### 奖励设计与探索
- [[EUREKA - Human-Level Reward Design via Coding Large Language Models|EUREKA]]: LLM自动奖励设计
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]]: 探索-利用的随机控制视角
- [[Hindsight Experience Replay]]: **稀疏奖励探索基石**，目标重标注的隐式课程

### 控制频率与时间抽象
- [[TARC - Time-Adaptive Robotic Control]]: **时间自适应控制**，策略输出动作+持续时间
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|Control Frequency Adaptation]]: 动作持续性与频率适应
- [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]]: 弹性时间步RL
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]]: 演化高频控制

### 长时程与接触丰富任务
- [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]]: **特权动作**简化长时程探索
- [[Dexterous Robotic Manipulation using Deep RL and Knowledge Transfer]]: 知识迁移框架
- [[Vision-force-fused Curriculum Learning for Robotic Assembly]]: 视觉-力融合课程
