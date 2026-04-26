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
> - [[Deep Dynamics Models for Learning Dexterous Manipulation]] - model-based RL 在 Shadow Hand 上的高效真机学习
> - [[Learning Quadrupedal Locomotion over Challenging Terrain]] - privileged teacher-student + adaptive curriculum 的 sim-to-real RL

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
> - **Policy Gradient 路线** → REINFORCE → TRPO → PPO

### 2.3.5 策略梯度定理与 REINFORCE (Policy Gradient Theorem & REINFORCE)

> [!note] 教科书参考
> 本节基于 Wang & Xiong **Deep Reinforcement Learning Notes** Chapter 3.1，
> 以及 Sutton & Barto 策略梯度定理的经典推导。

策略梯度是连续控制的理论根基。在转入 Actor-Critic 和 PPO 之前，必须掌握策略梯度定理的严格推导。

#### 物理直觉

策略梯度的核心问题：如何对一个**随机过程的期望回报**求关于策略参数的梯度？

目标函数：

$$J(\pi_\theta) = \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=1}^{T} r(s_t, a_t) \right] = \int p_\theta(\tau) r(\tau) \, d\tau$$

#### 形式化推导

> [!theorem] 策略梯度定理 (Policy Gradient Theorem)
> $$\nabla_\theta J(\pi_\theta) = \mathbb{E}_{\tau \sim p_\theta(\tau)} \left[ \sum_{t=1}^{T} \nabla_\theta \log \pi_\theta(a_t \mid s_t) \cdot \left( \sum_{t'=t}^{T} r(s_{t'}, a_{t'}) \right) \right]$$
> 
> **证明关键**：利用对数导数恒等式 (log-derivative trick)：
> $$\nabla_\theta p_\theta(\tau) = p_\theta(\tau) \nabla_\theta \log p_\theta(\tau)$$
> 
> 展开 $\log p_\theta(\tau)$：
> $$\log p_\theta(\tau) = \log p(s_1) + \sum_{t=1}^{T} \left[ \log \pi_\theta(a_t \mid s_t) + \log p(s_{t+1} \mid s_t, a_t) \right]$$
> 
> 环境转移概率 $p(s_{t+1} \mid s_t, a_t)$ 与 $\theta$ 无关，对 $\theta$ 求导后消失。这是策略梯度能够在**不知道环境模型**的情况下估计梯度的根本原因。

**因果性修正 (Reward-to-go)**：时刻 $t$ 的策略不影响时刻 $t' < t$ 的奖励。因此用 $\hat{Q}^\pi_{t} = \sum_{t'=t}^{T} r(s_{t'}, a_{t'})$（reward-to-go）替代全轨迹奖励可降低方差而不引入偏差。

#### REINFORCE 算法

基于策略梯度定理的最简实现：

1. 用当前策略 $\pi_\theta$ 采样 $N$ 条轨迹
2. 估计梯度：$\nabla_\theta J \approx \frac{1}{N} \sum_{i=1}^{N} \sum_{t=1}^{T} \nabla_\theta \log \pi_\theta(a_{i,t} \mid s_{i,t}) \cdot \hat{Q}^\pi_{i,t}$
3. 梯度上升更新：$\theta \leftarrow \theta + \alpha \nabla_\theta J$

#### 方差控制：基线技巧 (Baseline)

> [!tip] 基线不改变期望，但大幅降低方差
> 减去一个与动作无关的基线 $b(s)$：
> $$\nabla_\theta J = \mathbb{E}\left[\nabla_\theta \log \pi_\theta(a \mid s) \cdot (\hat{Q}^\pi - b(s))\right]$$
> 
> **无偏性证明**：$\mathbb{E}[\nabla_\theta \log \pi_\theta(a \mid s) \cdot b(s)] = b(s) \int \nabla_\theta \pi_\theta(a \mid s) \, da = b(s) \nabla_\theta 1 = 0$
> 
> 最常用基线：$b(s) = V^\pi(s)$（状态价值函数），此时 $\hat{Q}^\pi - V^\pi = \hat{A}^\pi$（**优势函数**），这正是 Actor-Critic 框架的雏形。

**REINFORCE 的局限性**：
- **高方差**：即使使用基线，蒙特卡洛估计的方差仍然很大
- **On-Policy**：采样的数据只能用一次（不能重用），样本效率极低
- **步长敏感**：步长过大导致策略崩溃，过小导致收敛缓慢

这些局限性直接催生了两条演进路线：
- Actor-Critic（用 Critic 替代蒙特卡洛回报估计 → DDPG/TD3/SAC）
- Trust Region（约束策略更新幅度 → TRPO/PPO）

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

##### PPO 完整损失函数分解

PPO 的总损失由三部分组成——策略损失、价值损失、熵正则项：

$$L_{t}^{CLIP+VF+S}(\theta) = \hat{\mathbb{E}}_{t} \left[L_{t}^{CLIP}(\theta) - c_1 L_{t}^{VF}(\theta) + c_2 S[\pi_\theta](s_t)\right]$$

| 组成部分 | 对应网络 | 输出 | 拟合目标 | 核心作用 |
|---------|---------|------|---------|---------|
| **Policy Loss** $L^{CLIP}$ | Actor | $\pi_\theta(a\|s)$ | 优势函数 $\hat{A}_t$ | 提升高回报动作概率，Clip 保证训练稳健 |
| **Value Loss** $L^{VF}$ | Critic | $V_\theta(s_t)$ | 实际回报 $G_t^{target}$ | 提供准确基线，减少策略梯度方差 |
| **Entropy Bonus** $S$ | Actor | $\pi_\theta(a\|s)$ | 最大化分布随机性 | 维持探索能力，防止陷入局部最优 |

##### PPO 三阶段数据流与梯度属性

> [!warning] 核心洞察
> 损失函数中的变量产生于**不同时间阶段**，且具有**不同的梯度属性**（detached 常量 vs 可导变量）。理解这一点是正确实现 PPO 的关键。

**阶段 1: Rollout（数据收集）** — 参数固定为 $\theta_{old}$，所有产出为 **detached tensors**：
- $s_t$: 环境观测（关节角/物体位置/速度）
- $a_t$: 从 $\mathcal{N}(\mu_{\theta_{old}}(s_t), \sigma)$ 中**采样**
- $\log \pi_{\theta_{old}}(a_t|s_t)$: 采样时立刻保存（网络更新后无法再获得旧分布值）
- $V_{\theta_{old}}(s_t)$: Critic 基线评估
- $r_t, d_t$: 环境反馈的奖励与终止标志

**阶段 2: Advantage 计算（后处理）** — 离线计算，仍为常量：
- $\hat{A}_t$: 通过 GAE 反向遍历 Rollout Buffer 计算
- $G_t^{target} = \hat{A}_t + V_{\theta_{old}}(s_t)$: Critic 拟合目标

**阶段 3: Network Update** — 重新激活计算图，参数 $\theta$ 开始更新：
- $\pi_\theta(a_t|s_t)$: 将缓存的 $s_t$ 输入**更新中的** Actor，计算旧动作 $a_t$ 在新分布下的概率
- $r_t(\theta) = \exp(\log \pi_\theta - \log \pi_{\theta_{old}})$: 利用 log-exp 技巧避免概率直除的数值不稳定
- $V_\theta(s_t)$: 更新中的 Critic 输出（带梯度）
- $S[\pi_\theta]$: 当前分布的信息熵

```python
# PPO Update — 核心张量操作 (PyTorch)
def compute_ppo_loss(obs, actions, old_log_probs, advantages, returns,
                     actor_critic, clip_param=0.2, c1=0.5, c2=0.01):
    # 阶段3: 重新前向传播，建立计算图
    action_dist, new_values = actor_critic(obs)
    new_log_probs = action_dist.log_prob(actions).sum(dim=-1)  # ⚠️ 多维动作必须在 dim=-1 求和
    entropy = action_dist.entropy().sum(dim=-1).mean()
    
    # Policy Loss
    ratio = torch.exp(new_log_probs - old_log_probs)  # log-exp 技巧
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1.0 - clip_param, 1.0 + clip_param) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()
    
    # Value Loss + 组装
    value_loss = (returns - new_values.squeeze(-1)).pow(2).mean()
    total_loss = policy_loss + c1 * value_loss - c2 * entropy
    return total_loss
```

> [!warning] 灵巧操作工程避坑
> 1. **维度陷阱**: 24-DoF 灵巧手的 `log_prob` 必须在动作维度求和（联合概率 = 各维度 log 概率之和）。漏掉 `.sum(dim=-1)` 会导致张量广播错误，网络默默学出无用策略
> 2. **Advantage 归一化**: Minibatch 级别 `(adv - mean) / (std + 1e-8)` 是必须的，否则策略更新步长不受控，Actor 极易崩溃
> 3. **$c_2$（熵系数）敏感性**: 灵巧操作中 $c_2$ 过小 → 手部动作迅速陷入无效颤动；$c_1$ 不合适 → 优势估计偏差放大导致 Actor 失效

##### PPO 的单峰高斯局限与多峰分布讨论

PPO 默认输出对角高斯 $\mathcal{N}(\mu(s), \sigma)$，对于多模态动作分布（如"绕左或绕右"）会拟合到均值导致无效动作。替代方案的困难在于：

| 替代方案 | 理论障碍 |
|---------|---------|
| **Diffusion Models** | 无法精确计算 $\log p_\theta(a_t\|s_t)$（只能算 ELBO 或用代价高昂的 ODE 求解器），$r_t(\theta)$ 引入巨大偏差 |
| **GMM** | 高维空间中混合高斯概率密度数值下溢严重，梯度爆炸 |
| **Normalizing Flows** | 理论上可行（有精确 log-prob），但雅可比行列式计算开销大 |

> [!tip] 实践中的解决路线
> 灵巧操作领域目前绕开此问题的方式：
> - **Diffusion Policy**（[[RepresentationLearning#2.2 深度解析：扩散策略 (Diffusion Policy) 的物理与数学基础|扩散策略]]）: 放弃 PPO 框架，直接用条件扩散模型做行为克隆
> - **Curriculum + Reward Shaping**: 用课程学习引导策略避开多模态区域
> - **层级策略**: 高层离散选择模态，低层单峰高斯执行

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

#### 统一梯度视角：SFT、蒸馏与 RL 的深层联系

> [!abstract] 从梯度角度统一四种训练范式
> SFT、Off-Policy Distillation、RL、On-Policy Distillation 四种训练目标看似不同，但从策略梯度角度可以统一到同一个框架中。将所有梯度通过重要性采样转换到 On-Policy 分布后：
>
> | 方法 | 梯度形式 | 加权方式 | 稀疏/稠密 |
> |------|---------|---------|----------|
> | **SFT** | $\nabla_\theta \log \pi_\theta(a\|s)$ 加权 by $\frac{\pi_\theta}{\pi_{data}} \cdot \mathbf{1}[a=a^*]$ | 指示函数（one-hot） | 稀疏 |
> | **Off-Policy Distillation** | $\nabla_\theta \log \pi_\theta(a\|s)$ 加权 by $\frac{\pi_\theta}{\pi_{data}} \cdot \pi_{teacher}(a\|s)$ | 教师分布 | 稠密 |
> | **RL (GRPO)** | $\nabla_\theta \log \pi_\theta(a\|s)$ 加权 by $\hat{A}(s,a)$ | 优势估计（reward） | 稀疏 |
> | **On-Policy Distillation** | $\nabla_\theta \log \pi_\theta(a\|s)$ 加权 by $\pi_{teacher}(a\|s)$ | 教师分布 | 稠密 |
>
> **关键洞见**：
> - **SFT 可视为奖励模型是指示函数的稀疏 RL**（$R(a) = \mathbf{1}[a=a^*]$）
> - RL 与 On-Policy Distillation 都是 On-Policy 的，区别在于 RL 用 reward 做稀疏加权，蒸馏用教师分布做稠密加权
> - On-Policy 方法（RL、On-Policy Distillation）比 Off-Policy 方法（SFT、Off-Policy Distillation）更优，因为避免了分布偏移
>
> **与灵巧操作的关联**：
> - 在 Sim-to-Real 中，教师策略（仿真中的专家）向学生策略蒸馏时，On-Policy Distillation 的稠密梯度信号比 RL 的稀疏 reward 信号更高效
> - 对于 [[Dynamic Non-Prehensile Manipulation|DNPM]] 中的长因果链问题，稠密的教师信号可部分缓解 credit assignment 困难
> - GRPO 算法（用于 LLM-RL）的组内优势估计思想可推广到机器人 RL 中的 episode-level 优势估计

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


> [!theorem] Potential-Based Reward Shaping (PBRS) — 保策略不变的奖励变换定理
> **来源**: Ng, Harada & Russell, 1999 — *“Policy Invariance Under Reward Transformations”*
>
> **定理（充要条件）**：对于折扣 MDP（$\gamma < 1$），shaped reward $R' = R + F(s, a, s')$ 保持所有最优策略不变 **当且仅当** 存在势函数 $\Phi: S \to \mathbb{R}$ 使得：
>
> $$F(s, a, s') = \gamma \Phi(s') - \Phi(s)$$
>
> 其中：
> - $\Phi(s)$：状态势函数，可理解为“状态 $s$ 距目标还有多远”的估计
> - $\gamma \Phi(s') - \Phi(s)$：只依赖状态差，不依赖动作 $a$
>
> **直觉**：PBRS 是一种“重新定义零点”的操作 — 类似物理学中的势能参考面选择，不改变力的方向（即不改变最优策略）。
>
> **为什么非 PBRS 的 shaping 会导致 reward hacking**：
> - 当 $F$ 不满足 PBRS 条件时，shaping reward **改变了最优策略**
> - 策略会学习最大化 $F$（shaping 信号）而非 $R$（任务目标）
> - **每增加一个非 PBRS 的 shaping term，就引入一个新的 hacking 通道**
> - 多个 shaping term 的叠加使得联合 $F$ 偏离 PBRS 条件的程度**超线性增长**
>
> **与 DNPM Exp2 的对应**：Heavy 配置的 6 个 shaping term 中，velocity、energy、contact force 等 term 几乎不可能满足 PBRS 的势函数差分形式，因此策略找到了最大化这些 shaping 信号的“捷径”，导致 SR=0。

**Solution**:

1. **ARES (Attention-based REward Shaping)** : 利用Transformer自动从演示数据中学习权重。
2. **Inverse Reinforcement Learning (IRL)**: 从专家演示中反推奖励函数。
3. **Mediator-Based Surrogate Reward**: 利用因果结构中的中介变量构造低方差替代奖励。

> [!tip] Mediator-Based Reward Design — 利用因果结构降低奖励方差
> 当原始奖励信号噪声很大时（如接触丰富的操作任务中成功/失败的二值奖励），可以利用因果 DAG 中的**中介变量（Mediator）**构造替代奖励：
>
> **因果结构**: $\text{Action} \xrightarrow{a} \text{Mediator} \xrightarrow{b} \text{Reward}$
>
> **替代奖励定义**: $\tilde{R}(m, s) = \mathbb{E}[R_t \mid M_t = m, S_t = s]$
>
> **核心定理（无偏性 + 方差降低）**: 在 surrogacy 假设（$R_t \perp A_t \mid M_t, S_t$）下：
> - $\mathbb{E}[\tilde{R}(M_t, S_t) \mid A_t, S_t] = \mathbb{E}[R_t \mid A_t, S_t]$（无偏）
> - $\text{Var}(\tilde{R}) \leq \text{Var}(R)$（严格更低方差），源于全方差公式
>
> **与灵巧操作的关联**：
> - 在 [[Dynamic Non-Prehensile Manipulation|DNPM]] 的长因果链（发力→惯性→接触力→摩擦力→抗重力）中，中间状态（如接触力大小、物体角速度）可作为 mediator
> - 用 mediator 构造的替代奖励可显著降低 credit assignment 的方差
> - 在线学习 mediator-reward 映射时，奖励的非平稳性可通过对抗性 bandit oracle 处理
> - 即使 surrogacy 假设不完全成立（如 mediator 只捕获 56% 的因果效应），仍可观察到性能提升
>
> **实践启发**：对于 EUREKA 等自动奖励设计方法，可将因果中介变量自动识别纳入奖励搜索空间，构造"因果感知"的奖励函数。

> [!warning] 实验证据：Reward Shaping Term 数量与 Reward Hacking 的定量关系（DNPM Exp2, 2026-02）
> 在 [[Dynamic Non-Prehensile Manipulation|DNPM]] 转笔任务的系统性奖励搜索实验中，发现了 shaping term 数量与 reward hacking 严重程度之间的**剂量-反应关系**：
>
> | 奖励配置 | Shaping Terms | TA Success Rate | TP Success Rate |
> |---------|--------------|-----------------|------------------|
> | **Heavy** | 6 (dist + rot + vel + energy + contact + bonus) | **0.00** | **0.00** |
> | **Medium** | 4 (dist + rot + vel + energy) | 0.31~0.72 | **0.86** |
> | **Light** | 3 (dist + rot + bonus) | **0.83** | 0.66~0.81 |
> | **Reduced** | 2 (dist + rot) | 0.17~0.75 | 0.21~0.74 |
>
> **关键洞见**：
> 1. Heavy 配置 **100% 失败**（SR=0），强证据表明过多 shaping term 导致策略找到 reward hacking 捷径
> 2. **最简洁的 Light 配置在 TA 上最优**（SR=0.83），说明"少即是多"
> 3. Shaping term 的边际效用**严格递减且可能为负** — 每增加一个 term 都引入新的 hacking 通道
> 4. **任务特异性**：TA 偏好 Light（3 terms），TP 偏好 Medium（4 terms），说明最优 shaping 复杂度取决于任务动力学
>
> **理论解释**：多 shaping term 的联合优化景观中，梯度方向被 shaping reward 主导，策略学会最大化 shaping 信号而非完成任务。这与 [[Optimization#2.6 非凸优化景观理论 (Nonconvex Optimization Landscapes)|非凸优化景观]] 中的鞍点逃逸失败一致 — shaping reward 创造了更深的局部极小值。

------

## 5. Bridging the Gap: Sim-to-Real & Offline RL

在仿真中训练好的策略，往往在真机上直接失败。这是因为仿真无法完美模拟真实的物理世界（摩擦、软体形变、传感器噪声）。

> [!abstract] Sim-to-Real 失败分类学（基于 [[A Survey of Sim-to-Real Methods in RL|MDP 四要素分类框架]]）
> 从 MDP 四元素 $(S, A, T, R)$ 的视角，Sim-to-Real Gap 来源可分为：
>
> | MDP 元素 | Gap 来源 | 典型例子 | 主要解决手段 |
> |---------|---------|---------|------------|
> | **State $S$** | 感知差异 | 渲染逼真度、传感器噪声 | 视觉域适应、随机纹理 |
> | **Action $A$** | 执行差异 | 电机延迟、齿槽效应、减速器背隙 | Action smoothing、[[sim2real\|硬件建模]] |
> | **Transition $T$** | 动力学差异 | 摩擦、弹性、质量分布 | DR、系统辨识、残差模型 |
> | **Reward $R$** | 奖励差异 | 仿真观测 vs 真机传感器 | Learned reward、人类反馈 |
>
> 对于灵巧操作，**$T$ (Transition) 和 $A$ (Action) 是主要瓶颈**——接触力学非线性 + 执行器非理想性共同构成 Gap 的核心。

### 5.0 系统辨识与在线参数学习 (System Identification & Online Adaptation)

在 DR 之前，系统辨识 (System ID) 是弥合 Sim-to-Real Gap 的传统方法。两种范式互补：

#### 离线系统辨识（Offline System ID）

通过真机上的诊断实验，估计物理参数 $\xi^* = \arg\min_\xi \|f_{sim}(s,a;\xi) - f_{real}(s,a)\|^2$：

- **刚体参数**：质量、惯性矩、质心 → 激励轨迹 + 最小二乘 ([[Dynamics]])
- **接触参数**：摩擦系数、恢复系数 → 碰撞实验 ([[ContactMechanics]])
- **执行器参数**：电机常数 $K_t$、减速器效率 $\eta$、Stribeck 摩擦 → 力矩-速度特性曲线 ([[sim2real|硬件Gap分析]])

**局限**：静态辨识无法捕捉温度漂移、磨损等时变效应。

#### 在线自适应（Online Adaptation）

运行时持续校正 Sim-Real 差异：

| 方法 | 机制 | 代表工作 |
|-----|------|---------|
| **Rapid Motor Adaptation (RMA)** | 环境编码器 $z = f(h_t)$ 从历史观测序列推断隐式物理参数 | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] |
| **Neural Dynamics Model** | 关节级残差神经网络补偿 Sim-Real 动力学差异 | [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] |
| **Online Correction** | 人类在线修正 → 学习修正模型 $\Delta a = g(s, a_{sim})$ | [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction\|TRANSIC]] |
| **Grounded Action Transform** | 学习 $a_{real} = h(s, a_{sim})$ 映射修正仿真动作 | [[Grounded Action Transformation\|GAT]] |

> [!tip] DR vs. System ID 的互补关系
> - **System ID**：减小 $\mathbb{E}[\|T_{sim} - T_{real}\|]$（减小均值偏差）
> - **Domain Randomization**：增大 $\text{Var}[T_{sim}]$（增大覆盖范围）
> - **最佳实践**：先做 System ID 缩小中心偏差，再用 DR 覆盖残余不确定性
> - **灵巧手场景**：关节执行器参数（$K_t$, $\eta$, 背隙角度）适合 System ID；接触摩擦适合 DR

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

> [!warning] 实验证据：课程学习的任务特异性 — TWC 对不同任务效果不对称（DNPM Exp2, 2026-02）
> 在 [[Dynamic Non-Prehensile Manipulation|DNPM]] 的 Time-Warped Curriculum (TWC, α-scaling) 实验中：
>
> | 任务 | BASE SR | TWC SR | TWC 效果 | TWC 方差变化 |
> |------|---------|--------|----------|-------------|
> | **TA (Thumbaround)** | **0.83** | 0.72 | ❌ **负效果** | 方差更大 |
> | **TP (Triangle Pass)** | 0.66 | **0.86** | ✅ **决定性正效果** | 降 19× |
>
> **关键洞见**：
> 1. **同一课程策略对不同任务效果可以完全相反** — TWC 帮助 TP 但伤害 TA
> 2. TWC 的物理轴课程（重力 ×α²、速度 ×α）对 TP 有效，可能因为 TP 的核心挑战是克服重力势垒，而 TWC 提供渐进的重力适应
> 3. TA 的核心挑战可能是**探索空间**而非物理难度 — TA 需要的是状态空间课程（δ轴），而非物理参数课程（α轴）
> 4. 这支持了 [[Idea-007-Dual Orthogonal Curriculum|DOC]] 的核心假设：物理难度和状态难度是**正交维度**，不同任务需要不同维度的课程
>
> **与课程学习理论的联系**：Continuation Method 保证了沿单一参数轴的连续性，但**多任务场景中不同任务对参数轴的响应面（response surface）不同**。这意味着通用课程不存在，需要任务感知的课程设计。

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

#### VLA 在线精细化: RL Tokens

> [!tip] 论文参考
> [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT (Physical Intelligence, 2026)]]

**核心思想**: 大型 VLA 模型在部署时难以端到端微调，但精密操作阶段（如螺丝对准、插线）仍需在线改进。RLT 的解决方案是**不微调 VLA**，而是：

1. **RL Token 提取**: 在 VLA 中训练一个编码器-解码器 Transformer，将 VLA 内部 embedding 压缩为单个紧凑 token（信息瓶颈）
2. **轻量级 Actor-Critic**: 仅对 RL token 训练极小的 actor-critic 网络，在机器人本地以每秒数百次更新的速度训练
3. **残差动作编辑**: Actor 接收 VLA 预测动作作为输入，学习 $\Delta a$ 修正（而非替代），正则化约束不远离 VLA 先验

$$a = \pi_\theta(z_{\text{RL\_token}}, a_{\text{VLA}}) = a_{\text{VLA}} + \Delta a_\theta$$

**关键工程技巧**: Reference-action dropout 防止 actor 退化为恒等映射；Action chunk 结构与 VLA 对齐保持时序一致性。

**实验结果**: 仅 15 分钟真实数据 → 精密操作 3× 加速，执行速度超越人类遥操作。

**与灵巧操作的关联**: 灵巧手的精密接触阶段（转笔关键接触切换点）可用 RLT 架构实现部署时在线精细化，避免重训全 VLA。与 [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|残差学习]] 形成呼应。

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


> [!tip] Denoising Sub-MDP: 扩散策略的 RL 微调框架 ([[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]])
> 扩散策略的 RL 微调面临核心矛盾：去噪过程的多步推理与 RL 的 MDP 框架不兼容。RL-100 提出将**每一步去噪**视为一个独立的 sub-MDP 步骤：
>
> 1. **Denoising Sub-MDP**: 将 $K$ 步去噪展开为 $K$ 步 MDP，每步状态包含 $(s_\text{env}, a_k, k)$，策略在去噪步 $k$ 的输出即为 denoiser 的预测
> 2. **Consistency Distillation**: 通过一致性蒸馏将 $K$-step DDPM 压缩为 1-step 生成，消除推理延迟（100ms → 10ms），使 RL 梯度可直接通过单步 denoiser 传播
> 3. **IL→Offline RL→Online RL 三阶段流水线**: BC 预训练 → 离线 RL（CRR loss）消除非最优行为 → 在线 RL 细化
>
> **与灵巧操作的关联**: 若采用扩散策略架构，denoising sub-MDP 提供了从模仿到强化学习的完整迁移路径。RL-100 在 7 个真实任务上实现 900/900（100%）成功率。

------

### 6.3 RL Scaling Laws: 计算最优的训练资源分配

> [!abstract] IsoCompute Playbook — RL 训练中的采样计算最优分配
> 在 On-Policy RL（如 GRPO）训练中，给定固定的采样计算预算 $C = n \times B_{problem} \times M$（并行采样数 × 问题数 × 迭代次数），如何最优地分配这三个维度？
>
> **核心发现**：
>
> | 发现 | 描述 | 与灵巧操作的关联 |
> |------|------|-----------------|
> | **最优并行采样数随预算增长** | $n^*(C)$ 呈 sigmoid 增长 | 训练预算充足时应增大并行环境数（如 IsaacGym） |
> | **Easy/Hard 问题：相似趋势，不同机制** | Easy: 大 $n$ 锐化策略（改善 worst@k）；Hard: 大 $n$ 扩展覆盖（改善 best@k） | DNPM 中 quasi-static（easy）vs dynamic（hard）任务需不同策略 |
> | **熵控制策略因难度而异** | Easy 任务需 KL/熵约束防止过早坍缩；Hard 任务去除正则化反而更优 | HDC 课程从 easy（$\alpha$ 小）到 hard（$\alpha=1$）的迁移过程中应动态调整熵正则 |
> | **学习率应随 batch size 平方根缩放** | $\text{lr} \propto \sqrt{B}$，而非固定 | 大规模并行仿真训练的超参数指导 |
>
> **"健康" RL 配方的特征**：
> - 稳定的熵动态（避免 entropy collapse 或 divergence）
> - 严格 on-policy（避免 staleness），限制 off-policy 重用
> - 根据问题难度分布调整正则化策略
>
> **与 [[Dynamic Non-Prehensile Manipulation|DNPM]] HDC 的直接关联**：
> - HDC 的 $\alpha$ 课程从 easy（慢速空间）渐进到 hard（真实速度），正好对应 scaling law 中 easy→hard 的不同机制转换
> - HDC 课程迁移判据（success rate 阈值）可参考 IsoCompute 中 easy 问题饱和点的定义来优化
> - 并行环境数 $n$ 的选择应根据当前 $\alpha$ 值动态调整——低 $\alpha$（easy）时可用更大 $B_{problem}$，高 $\alpha$（hard）时增大 $n$ 以扩展覆盖

### 6.4 Test-Time RL: 部署时在线学习新发现

> [!abstract] TTT-Discover — 测试时通过 RL 持续训练发现新方案
> **核心思想**：在部署/测试阶段对单个问题继续执行 RL 训练，让模型从特定问题的经验中持续改进，而非仅依赖训练阶段的泛化能力。
>
> **与标准 RL 的关键区别**：
> - 标准 RL: 优化**期望**奖励，策略需在多个环境中泛化
> - TTT-Discover: 只需找到**单个**最优解（最大而非期望），且只需解决**当前**问题
>
> **Entropic Objective** — 偏好最大奖励动作的学习目标：
> $$J_\beta(\theta) = \mathbb{E}_{s \sim \text{reuse}(H)} \left[ \log \mathbb{E}_{a \sim \pi_\theta(\cdot|s)} \left[ e^{\beta(s) R(s,a)} \right] \right]$$
>
> 其策略梯度为 softmax 加权形式：
> $$w_{\beta(s)}(a) = \frac{e^{\beta(s) R(s,a)}}{\mathbb{E}_{\pi_\theta}[e^{\beta(s) R(s,a)}]}$$
>
> 当 $\beta \to \infty$ 时退化为 argmax（纯贪婪）；$\beta \to 0$ 时退化为标准策略梯度（均匀加权）。
>
> **State Reuse 机制**：维护历史解的缓冲区 $H_i$，通过启发式采样复用高奖励解作为初始状态，有效延长搜索视野。
>
> **与灵巧操作的潜在关联**：
> - **在线适应**: 将操作策略部署到新环境（新物体、新摩擦系数）时，可在测试时对该特定物体执行 TTT-Discover，发现针对性的操作策略
> - **与 [[Optimization#5.3 基于采样的 MPC (Sampling-based MPC)|Sampling-based MPC]] 的对比**: TTT-Discover 的 state reuse + entropic objective 可视为"带学习的 MPC"——MPPI 在每步重新采样，TTT 则通过参数更新积累经验
> - **探索-利用权衡**: Entropic objective 的 $\beta$ 参数控制探索-利用权衡，类似 [[ReinforcementLearning#2.4 Off-Policy 演进线：从 DDPG 到 SAC|SAC]] 中的温度参数 $\alpha$

------
### 6.5 World Model-Based Policy Optimization for VLA (WMPO)

> [!abstract] 像素空间世界模型 + GRPO 对 VLA 的 RL Post-Training
> [[WMPO - World Model-based Policy Optimization for VLA|WMPO]] 提出在 VLA 上执行 RL post-training，核心创新在于**像素空间**世界模型与分组相对策略优化的结合。

**关键设计选择**：

| 维度 | WMPO 选择 | 传统方法 | 优势 |
|------|----------|---------|------|
| **世界模型空间** | 像素空间视频生成 | 隐空间 (DreamerV3) | 与 VLA 预训练视觉特征对齐 |
| **RL 算法** | GRPO (Group Relative PO) | PPO / REINFORCE | 无需 value network，组内比较更稳定 |
| **奖励来源** | VLM-as-Judge | 手工设计 | 可扩展到开放任务 |
| **数据来源** | On-policy rollout in WM | Real-world interaction | 零真实交互成本 |

**GRPO 数学形式**：
$$\mathcal{L}_{GRPO} = -\frac{1}{G}\sum_{i=1}^{G} \min\left(r_i(\theta) \hat{A}_i, \text{clip}(r_i(\theta), 1\pm\epsilon)\hat{A}_i\right)$$

其中优势函数通过组内归一化计算：$\hat{A}_i = \frac{R_i - \text{mean}(R_{1:G})}{\text{std}(R_{1:G})}$

**与灵巧操作的关联**：
- **Dynamic Sampling Strategy**: WMPO 的动态采样策略（筛除"全失败"或"全成功"的 prompt 组）对 [[Dynamic Non-Prehensile Manipulation|DNPM]] 的稀疏奖励问题有直接借鉴——可在课程学习中动态调整 $\alpha$ 分布
- **VLM-as-Judge**: 为复杂操作任务提供了超越手工奖励的评估路径
- **与 §6.1 DreamerV3 的对比**: DreamerV3 在隐空间 imagination-based planning；WMPO 在像素空间生成完整视频并用 VLM 评分——后者更适合 VLA 架构


### 6.6 RL 算法统一分类框架

> [!abstract] On/Off-Policy 的统一视角
> [[Unified Policy Evaluation and Improvement - On Off-Policy Classification|Unified Policy]] 提出通过 **evaluation** 和 **improvement** 两个维度对 RL 算法进行统一分类，揭示 PPO、SAC、BRAC 等算法的本质差异仅在于 update schedule 的选择。

**统一策略评估公式**：
$$Q^{\pi_E}(s,a) = r(s,a) + \gamma \mathbb{E}_{s' \sim P}\left[V^{\pi_E}(s')\right]$$

**统一策略改进公式**：
$$\pi_I(a|s) = \arg\max_\pi \mathbb{E}_{a \sim \pi}\left[Q^{\pi_E}(s,a)\right] - \alpha D_{KL}(\pi \| \pi_{ref})$$

**Update Schedule 三状态分类**：

| 状态 | $\pi_E$ (评估) | $\pi_I$ (改进) | 代表算法 |
|:---:|:---:|:---:|:---:|
| Pure On-Policy | $\pi_I$ (最新) | $\pi_I$ (最新) | PPO |
| Pure Off-Policy | $\pi_E$ (旧) | $\pi_I$ (最新) | BRAC |
| Cross-Policy | $\pi_E$ (连续更新) | $\pi_I$ (最新) | SAC |

**与灵巧操作的关联**：该框架为用户的 PPO 转笔策略选择提供理论支撑——PPO 的 Pure On-Policy 特性意味着 rollout 数据即时使用，天然适合 IsaacGym 大规模并行；而转向 SAC 时需要 replay buffer 的 staleness 管理。详见 [[Unified Policy Evaluation and Improvement - On Off-Policy Classification|完整论文笔记]]。

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

> **Source**: From [[Books/lumina-eai-guide.pdf|Lumina Embodied AI Guide]]

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
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]]: 人类参考的神经跟踪控制
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]: 规划引导的扩散策略

### 奖励设计与探索
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models|EUREKA]]: LLM自动奖励设计
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

### 扩散策略的 RL 微调与 World Model RL
- [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]: **Denoising Sub-MDP** 框架，IL→Offline RL→Online RL 三阶段流水线，consistency distillation 加速推理
- [[WMPO - World Model-based Policy Optimization for VLA|WMPO]]: **像素空间世界模型 + GRPO** 对 VLA 进行 RL post-training，VLM-as-Judge 奖励
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]]: **Flow Matching 预训练 + 残差 RL 后训练**，actuation-aware 动力学建模

### 物理感知预训练与几何表征
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]]: **Dynamics-lifted 几何预训练**，transport equation 统一粒子动力学范式

### Sim-to-Real 综述与经典方法
- [[A Survey of Sim-to-Real Methods in RL]]: **MDP 四要素分类框架** (State/Action/Transition/Reward)，首个覆盖 Foundation Model 时代的 sim-to-real 综述
- [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer|Tiwari et al. Survey]]: 执行器级建模视角的 sim-to-real 综述
- [[Grounded Action Transformation|GAT]]: **仿真器 grounding 经典方法**，学习动作映射函数修正 sim-real 差异 (AAAI 2017)

### 非紧握操作与外在灵巧性
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]]: **动力学感知策略学习**，世界模型条件化 RL 实现杂乱场景外在灵巧性

### 触觉与多模态推理
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|SToLa]]: MoE 触觉-语言融合框架

### 数据生成与双臂操作
- [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation|RoboTwin 2.0]]: MLLM 驱动的双臂数据自动生成 + 5 轴域随机化

### 课程学习进阶
- [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]: **示范引导自动课程** — ZVF+手动初始化 state curriculum，LEAP Hand 旋转物体 Sim2Real
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]: **熵引导演示加速** — 倍速专家演示 + H(π) 控制
- [[Vision-force-fused Curriculum Learning for Robotic Assembly]]: 视觉-力多模态课程的阶梯式训练

### 长时程操作与特权学习
- [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]]: **特权动作**简化长时程任务的探索
- [[Part-Guided 3D RL for Sim2Real Articulated Object Manipulation]]: 3D 部件引导 RL 跨铰接物体 Sim2Real

### 灵巧手 Sim-to-Real 专项
- [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]]: 首个 arm-hand VLA 人在回路 post-training
- [[sim2real|硬件 Sim-to-Real Gap 分析]]: 电机/减速器/传动方案对 RL 策略迁移的系统影响

### VLA 在线精细化与人形运动
- [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]]: **RL Token 信息瓶颈** — 冻结 VLA + 轻量级 actor-critic 在线精细化，15 分钟真实数据实现 3× 加速
- [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]]: **Physics-prefix 引导的运动生成** — 课程 MoE + 262D 机器人原生扩散 + PPO 闭环微调，解决长尾敏捷运动
