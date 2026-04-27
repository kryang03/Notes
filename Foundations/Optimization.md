---
tags:
  - foundation
  - optimization
  - dexterous-manipulation
  - MPC
  - trajectory-optimization
aliases:
  - 优化理论
  - Optimization
  - iLQR
  - MPC
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
---

# 灵巧操作中的优化理论：从接触隐式轨迹优化到实时模型预测控制

> [!tip] 相关领域
> - [[ControlTheory]] - MPC 是控制理论的实时实现
> - [[Dynamics]] - 动力学模型是轨迹优化的约束
> - [[ContactMechanics]] - LCP/互补约束的处理
> - [[ReinforcementLearning]] - 优化与RL的融合

## 1. 领域全景与首席科学家视角的执行摘要

灵巧操作（Dexterous Manipulation）代表了机器人学中物理交互的最高形式。不同于简单的二值化抓取（Grasping），灵巧操作要求机器人手部与物体之间发生受控的相对运动，涉及频繁的接触状态切换（Making/Breaking Contact）、滚动（Rolling）与滑动（Sliding）。从控制论的角度来看，这是一个极具挑战性的高维、欠驱动、混合动力学（Hybrid Dynamics）系统问题。作为该领域的首席科学家，我们必须摒弃对“端到端”黑盒学习的盲目崇拜，转而深入剖析**轨迹优化（Trajectory Optimization, TrajOpt）**与**模型预测控制（Model Predictive Control, MPC）**在处理接触不连续性时的数学困境与工程妥协。

本报告的核心论点在于：灵巧操作的本质是**通过接触力的调制来重塑系统的状态空间流形（State Space Manifold）**。物体本身是欠驱动的，其状态演化完全依赖于接触约束提供的外力。因此，优化问题的核心不在于规划关节轨迹，而在于规划**接触力的序列**。

传统的运动规划算法（如RRT）因割裂了动力学而失效；早期的轨迹优化因无法处理接触突变而陷入局部极小值。现代方法的突破口在于两个方向的数学重构：一是**接触隐式优化（Contact-Implicit Trajectory Optimization, CITO）**，即在数学上将接触力作为决策变量，允许求解器自动发现接触模式；二是**可微物理（Differentiable Physics）**，通过平滑化接触模型使得梯度流（Gradient Flow）能够穿越接触边界，从而赋能基于梯度的快速求解器（如iLQR/DDP）。我们将以严谨的数学推导和物理直觉，解构这一技术演进过程。

------

## 2. 核心概念：物理直觉与数学定义 (Core Concepts: Physics & Mathematics)

在深入具体的优化算法之前，我们必须建立一套严谨的数学语言来描述灵巧操作。这不仅仅是符号的堆砌，而是对物理现实的数学抽象。

### 2.1 广义坐标与欠驱动流形 (Generalized Coordinates & Underactuated Manifold)

在灵巧操作中，系统的状态 $x$ 不能仅仅包含机器人的关节状态，必须显式包含物体的状态。我们将系统定义在一个广义坐标系中。

定义配置空间（Configuration Space）向量 $q \in \mathbb{R}^{n_q}$：

$$q = \begin{bmatrix} q_{hand} \\ q_{object} \end{bmatrix}$$

其中：

- $q_{hand} \in \mathbb{R}^{n_a}$：全驱动（Fully Actuated）的手部关节坐标。对于 Shadow Hand 这样的高维手，这通常涉及 20-24 个自由度。
- $q_{object} \in \mathbb{SE}(3)$：**浮动基（Floating Base）**的物体坐标。由于物体没有固定基座，其位置和姿态必须通过 $\mathbb{R}^3 \times \mathbb{SO}(3)$ 来描述（通常使用四元数或旋转矩阵）。

状态向量 $x$ 通常定义为配置及其时间导数：

$$x = \begin{bmatrix} q \\ v \end{bmatrix} \in \mathbb{R}^{2n_q}$$

**物理意义的深度剖析**： 灵巧操作的根本困难在于 $q_{object}$ 是**欠驱动（Underactuated）**的。没有电机直接连接在物体上。物体加速度 $\dot{v}_{object}$ 只能通过接触约束力（Contact Forces, $\lambda$）间接产生 。这意味着系统不能在状态空间中任意移动，必须遵循动力学约束定义的流形。

动力学方程通常写为操纵器方程形式（Manipulator Equation）：

$$M(q)\dot{v} + C(q, v)v + g(q) = B u + J_c(q)^T \lambda$$

- $M(q)$：广义惯性矩阵（Generalized Mass Matrix），它是分块对角矩阵，分别包含手和物体的惯性特性。
- $C(q, v)$：科里奥利力与离心力项（Coriolis and Centrifugal terms）。
- $B$：驱动矩阵（Actuation Matrix），它将电机力矩映射到广义力空间。注意，对应于 $q_{object}$ 的行是全零的，这数学上刻画了欠驱动特性。
- $J_c(q)$：接触雅可比矩阵（Contact Jacobian）。这是连接机器人与物体的桥梁，它将笛卡尔空间的接触力 $\lambda$ 映射到广义力空间。
- $\lambda$：接触力（Contact Forces）。这是系统最核心的非线性源头，也是优化的关键决策变量。

**Insight**：在优化问题中，我们不仅要寻找控制输入 $u$（电机力矩），更本质的是在寻找一个可行的 $\lambda$ 序列。如果 $\lambda$ 为零，物体就不受控。优化的本质是在寻找 $J_c(q)^T \lambda$ 能够抵消物体动态项的时刻。

### 2.2 混合动力学与线性互补问题 (Hybrid Dynamics & LCP)

接触之所以难以优化，是因为它引入了**互补约束（Complementarity Constraints）**。对于刚体接触，物理世界要求满足 Signorini 条件（非穿透）和 Coulomb 摩擦定律。

在无摩擦的最简形式下，线性互补问题（Linear Complementarity Problem, LCP）定义为（详见 [[ContactMechanics#4.1 线性互补问题 (LCP) 的构建]]）：

$$0 \le \phi(q) \perp \lambda_n \ge 0$$

这包含三个条件：

1. **非穿透约束** $\phi(q) \ge 0$：$\phi(q)$ 是有向距离函数（Signed Distance Function, SDF）。物体之间不能重叠，距离必须非负。
2. **单边力约束** $\lambda_n \ge 0$：接触力只能是排斥力（推力），不能是吸引力（拉力，除非是吸盘）。
3. **互补性** $\phi(q) \lambda_n = 0$：这是最关键的逻辑约束。要么分离（距离 $>0$，力 $=0$），要么接触（距离 $=0$，力 $\ge 0$）。二者不能同时非零。

当引入摩擦时，问题变得更加复杂。库伦摩擦锥（Friction Cone）定义为：

$$\mathcal{K}(\mu) = \{ (\lambda_n, \lambda_t) \mid \|\lambda_t\| \le \mu \lambda_n, \lambda_n \ge 0 \}$$

在最大耗散原理（Maximum Dissipation Principle）下，摩擦力 $\lambda_t$ 的方向必须与切向相对速度 $v_t$ 相反，且当 $v_t = 0$ 时（Sticking），摩擦力可以在锥内任意取值。

**为什么这是优化的噩梦？**

对于基于梯度的优化器（Gradient-based Optimizer）而言，互补约束 $\phi(q) \lambda = 0$ 是**非凸的（Non-convex）\**且\**非光滑的（Non-smooth）**。

- **非凸性**：可行域是坐标轴的并集，而不是一个凸集。
- **梯度消失/爆炸**：在非接触状态下，力关于位置的梯度 $\frac{\partial \lambda}{\partial q}$ 恒为零；在接触瞬间，梯度理论上为无穷大（刚体碰撞）。这导致标准的反向传播算法无法获得有效的梯度指引。
- **模态分裂**：状态空间被分割成指数级数量的离散“模态（Modes）”（例如：手指1接触/手指2分离/手指3滑动...）。在模态切换的瞬间，动力学方程发生突变 。

### 2.3 抓取稳定性与力封闭 (Grasp Stability & Force Closure)

优化的目标函数（Cost Function）通常包含抓取指标，用于引导系统进入稳定的状态。最经典的是 **Ferrari-Canny Metric**，它度量了抓取构型抵抗外部扰动的能力。

其数学定义基于抓取矩阵 $G$（由接触位置和法向量决定）和摩擦锥约束：

$$Q_{FC} = \min_{w_{ext}, \|w_{ext}\|=1} \max_{\lambda \in FC} \alpha \quad \text{s.t.} \quad G\lambda = \alpha w_{ext}$$

物理直觉是：在所有可能的单位外力扰动 $w_{ext}$ 中，找到那个最“难”抵抗的方向（Worst-case direction），该方向上系统能提供的最大抵抗力 $\alpha$ 就是抓取质量。

**现代视角的批判**：

传统的 Ferrari-Canny 计算是一个嵌套优化问题（Nested Optimization），通常涉及计算凸包（Convex Hull），这在数学上是**不可微的（Non-differentiable）**。这意味着我们不能直接将其放入 Trajectory Optimization 的 Cost Function 中并对其求导。如果强行使用，优化器将无法知道如何调整关节角 $q$ 来提高抓取质量。

近期的研究致力于构建**可微的抓取质量评估（Differentiable Grasp Quality）**。例如，通过 Log-Barrier 近似摩擦锥，或者学习一个 Neural Signed Distance Field (SDF) 来平滑地引导手指走向稳定构型。这使得我们能够计算 $\nabla_q Q_{FC}$，从而在轨迹优化中直接优化抓取稳定性 。

### 2.4 凸优化基础与对偶性理论 (Convex Optimization Foundations & Duality)

> [!note] 教科书参考
> 本节基于 **Optimization in Theory and Practice** (Wright 2025) Section 2, 5 以及
> 优化教材 (Opt_book) Chapter 3-4 (Convex Sets/Functions) 和 Chapter 6 (Optimality Conditions & Duality)

灵巧操作中的许多子问题（力分配 QP、抓取规划、MPC 子问题）都是凸优化问题或可松弛为凸问题。掌握凸集/凸函数的严格定义和对偶性理论，是理解这些算法计算高效性的根基。

#### 2.4.1 凸集 (Convex Sets)

**定义**：集合 $C \subseteq \mathbb{R}^n$ 是**凸集**，当且仅当对任意 $x, y \in C$ 和 $\theta \in [0, 1]$：

$$\theta x + (1 - \theta) y \in C$$

**关键凸集类型**：

| 凸集 | 定义 | 灵巧操作中的对应 |
|------|------|---|
| **超平面** | $\{x \mid a^T x = b\}$ | 接触约束的线性化 |
| **半空间** | $\{x \mid a^T x \leq b\}$ | 摩擦锥的多面体线性化 |
| **多面体** | $\{x \mid Ax \preceq b\}$ | 力分配可行域 |
| **椭球** | $\{x \mid (x - x_c)^T P^{-1}(x - x_c) \leq 1\}$ | 不确定性椭球 (估计) |
| **二阶锥** | $\{(x, t) \mid \|x\| \leq t\}$ | 摩擦锥 $\|\lambda_t\| \leq \mu \lambda_n$ |

**保凸运算**：凸集在**交集**、**仿射映射**、**透视函数**下封闭。这意味着：
- 多个接触约束的交集仍是凸集
- 抓取矩阵 $G$ 对摩擦锥的线性映射保持凸性

#### 2.4.2 凸函数 (Convex Functions)

**定义（一阶条件）**：若 $f$ 可微，则 $f$ 是凸函数当且仅当 $\text{dom}\, f$ 是凸集且：

$$f(x + s) \geq f(x) + \nabla f(x)^T s, \quad \forall x, s$$

**物理直觉**：凸函数在任意点的切平面都是全局下界。这意味着**一阶驻点即为全局最优**。

**强凸函数**（模 $\mu > 0$）：

$$f(x + s) \geq f(x) + \nabla f(x)^T s + \frac{\mu}{2} \|s\|^2$$

等价条件（二阶）：$\nabla^2 f(x) \succeq 0$（凸），$\nabla^2 f(x) \succeq \mu I$（$\mu$-强凸）。

**凸函数的保持性**：
- 非负加权和：$\alpha f + \beta g$（$\alpha, \beta \geq 0$）
- 仿射复合：$f(Ax + b)$
- 逐点上确界：$\sup_{y \in A} f(x, y)$（支撑函数即为此结构）

> [!tip] 灵巧操作中的凸性
> - 力分配问题的目标函数 $\|f_c\|^2$（最小力范数）是强凸的
> - 摩擦锥约束 $\|\lambda_t\| \leq \mu \lambda_n$ 定义了**二阶锥约束**，对应 SOCP
> - Ferrari-Canny 度量的不可微性正是因为它是凸包运算（逐点上确界）的结果

#### 2.4.3 拉格朗日对偶理论 (Lagrangian Duality)

考虑一般非线性规划（NLP）：

$$\min_{x} f_0(x) \quad \text{s.t.} \quad f_i(x) \leq 0, \; i = 1, \ldots, m, \quad h_j(x) = 0, \; j = 1, \ldots, p$$

**拉格朗日函数**：

$$L(x, \lambda, \nu) = f_0(x) + \sum_{i=1}^{m} \lambda_i f_i(x) + \sum_{j=1}^{p} \nu_j h_j(x)$$

其中 $\lambda_i \geq 0$ 是不等式约束的拉格朗日乘子，$\nu_j$ 是等式约束的乘子。

**拉格朗日对偶函数**：

$$g(\lambda, \nu) = \inf_{x \in \mathcal{D}} L(x, \lambda, \nu)$$

> [!theorem] 弱对偶性 (Weak Duality)
> 对任意 $\lambda \geq 0$ 和任意 $\nu$：$g(\lambda, \nu) \leq p^*$
> 
> **证明思路**：设 $\tilde{x}$ 为原始可行点，则 $\sum \lambda_i f_i(\tilde{x}) \leq 0$，故 $L(\tilde{x}, \lambda, \nu) \leq f_0(\tilde{x})$，取 $\inf$ 后结论成立。

**对偶问题**：

$$\max_{\lambda, \nu} g(\lambda, \nu) \quad \text{s.t.} \quad \lambda \geq 0$$

对偶问题**始终是凸优化**（即使原始问题非凸），因为 $g$ 是仿射函数族的逐点下确界，因此是凹函数。

**对偶间隙**：$p^* - d^* \geq 0$。当 $p^* = d^*$ 时，称为**强对偶性**。

> [!theorem] Slater 条件与强对偶性
> 若原始问题是凸的（$f_0, f_i$ 凸，$h_j$ 仿射），且存在**严格可行点** $\tilde{x}$：
> $$f_i(\tilde{x}) < 0, \quad i = 1, \ldots, m$$
> 则**强对偶性成立**：$p^* = d^*$。
> 
> **灵巧操作含义**：Slater 条件在力分配 QP 中几乎总是满足的（只要存在某个严格在摩擦锥内部的力分配），因此可以放心使用对偶方法。

#### 2.4.4 KKT 条件 (Karush-Kuhn-Tucker Conditions)

> [!note] 教科书参考
> 本节基于 Opt_book Chapter 6, Proposition 98 (Karush-Kuhn-Tucker conditions)

对于一般 NLP，KKT 条件是约束优化的一阶必要条件（在适当约束规范条件下）：

$$\nabla f_0(x^*) + \sum_{i=1}^{m} \lambda_i^* \nabla f_i(x^*) + \sum_{j=1}^{p} \nu_j^* \nabla h_j(x^*) = 0 \quad \text{(驻点性)}$$
$$f_i(x^*) \leq 0, \quad h_j(x^*) = 0 \quad \text{(原始可行性)}$$
$$\lambda_i^* \geq 0 \quad \text{(对偶可行性)}$$
$$\lambda_i^* f_i(x^*) = 0, \quad \forall i \quad \text{(互补松弛性)}$$

**互补松弛性的物理意义**：在最优解处，要么约束不活跃（$f_i < 0$，此时 $\lambda_i = 0$），要么约束恰好活跃（$f_i = 0$，此时 $\lambda_i > 0$）。

**约束规范条件层级**：

| 约束规范 | 缩写 | 含义 | 强度 |
|---------|------|------|------|
| Slater | SCQ | 存在严格可行点（凸约束） | 较弱 |
| Mangasarian-Fromovitz | MFCQ | 活跃约束梯度允许严格下降方向 | 中等 |
| 线性独立 | LICQ | 活跃约束梯度线性无关 | 较强 |

关系链：LICQ $\Rightarrow$ MFCQ $\Rightarrow$ ACQ（Abadie）。

> [!abstract] 凸问题的 KKT：充要条件
> 当原始问题是凸的且 Slater 条件满足时，KKT 条件是全局最优的**充分且必要条件**。这是使得凸优化可以高效求解的根本原因。
>
> **灵巧操作应用**：
> - 力分配 QP 中，KKT 条件等价于 $G f_c = w_d$（力平衡）+ $f_c \in \mathcal{K}(\mu)$（摩擦锥）+ 互补松弛
> - 内点法的每步迭代本质上是在求解一个扰动的 KKT 系统（将互补条件松弛为 $\lambda_i f_i = -\mu$）
> - 接触力学中的 LCP 条件 $0 \leq \phi \perp \lambda \geq 0$ 正是 KKT 互补松弛的特殊形式（详见 [[ContactMechanics#4.1 线性互补问题 (LCP) 的构建]]）

### 2.5 优化算法的复杂度理论基础

> [!tip] 参考资料
> 详见 [[Books/Optimization in Theory and Practice.pdf]] (Wright 2025)。

本小节建立优化算法复杂度分析的理论框架，这些概念对于理解 MPC 和轨迹优化的计算瓶颈至关重要。

#### 2.5.1 近似最优性条件 (Approximate Optimality)

对于无约束优化 $\min_x f(x)$：

**一阶必要条件**：$\nabla f(x^*) = 0$（驻点）

**近似一阶条件**：$\|\nabla f(x^*)\| \leq \epsilon_g$

**近似二阶条件**：额外要求 $\nabla^2 f(x^*) \succeq -\epsilon_H I$

**Oracle 复杂度模型**：定义"信息单元"（oracle）如 $(f(x), \nabla f(x))$，算法复杂度用达到 $\epsilon$-近似解所需的 oracle 调用次数衡量。

#### 2.5.2 梯度下降的收敛率

设 $f$ 是 $L$-Lipschitz 光滑函数（$\|\nabla f(x) - \nabla f(y)\| \leq L \|x - y\|$）。

**凸函数收敛率**：

$$f(x_k) - f^* \leq \frac{L \|x_0 - x^*\|^2}{2k} = O(1/k)$$

**强凸函数 ($\mu$-强凸) 收敛率**：

$$f(x_k) - f^* \leq \left(1 - \frac{\mu}{L}\right)^k (f(x_0) - f^*) = O\left((1 - \kappa^{-1})^k\right)$$

其中 $\kappa = L/\mu$ 是**条件数 (Condition Number)**。

| 问题类型 | 收敛率 | Oracle 复杂度 |
|----------|--------|---------------|
| 凸，光滑 | $O(1/k)$ | $O(L/\epsilon)$ |
| 强凸，光滑 | 线性 $(1-\mu/L)^k$ | $O(\kappa \log(1/\epsilon))$ |
| 非凸，光滑 | $O(1/\sqrt{k})$ → 驻点 | $O(1/\epsilon^2)$ |

#### 2.5.3 Nesterov 加速与下界

> [!important] Nesterov 加速梯度法
> 对于凸光滑函数，最优一阶方法的复杂度为：
> $$f(x_k) - f^* \leq O\left(\frac{L \|x_0 - x^*\|^2}{k^2}\right) = O(1/k^2)$$
> 
> 这是**最优的**：存在匹配的下界，证明任何一阶方法都不能做得更好。

**灵巧操作应用**：轨迹优化中的代价函数通常是非凸的（由于接触约束），但在接触模式固定的局部区域内近似强凸。加速方法在这些局部区域内能显著加速收敛。

#### 2.5.3.1 牛顿法与拟牛顿法 (Newton & Quasi-Newton Methods)

**核心思想**：利用二阶信息（Hessian）构建局部二次模型，实现**超线性/二次收敛**：

$$x_{k+1} = x_k - [\nabla^2 f(x_k)]^{-1} \nabla f(x_k)$$

| 方法 | 信息需求 | 每步复杂度 | 收敛速率 | 适用场景 |
|------|---------|-----------|---------|---------|
| **Newton** | Hessian $\nabla^2 f$ | $O(n^3)$（求逆） | 二次 | 小规模精确优化 |
| **BFGS** | 仅梯度 | $O(n^2)$（秩2更新） | 超线性 | 中等规模无约束 |
| **L-BFGS** | 仅梯度 | $O(mn)$（$m$ 对历史） | 超线性 | 大规模无约束 |
| **Gauss-Newton** | 雅可比 $J$ | $O(n^2)$（$J^TJ$ 近似） | 超线性 | 最小二乘/轨迹优化 |

> [!tip] 灵巧操作中的二阶方法
> - **iLQR/DDP** 本质上是 Gauss-Newton 在动态规划结构上的特化（见 [[Optimization#4.1 核心算法：iLQR / DDP|iLQR 章节]]）
> - **SQP** 在每个迭代步求解一个 QP 子问题，QP 的 Hessian 近似来自 BFGS 更新
> - **内点法** 在每个迭代步求解一个 Newton 系统（见下节）
> 
> 因此，Newton 法是几乎所有高阶轨迹优化算法的**计算内核**。

#### 2.5.4 线性规划：单纯形法 vs 内点法

> [!abstract] LP 复杂度对比
> | 方法 | 最坏情况复杂度 | 典型实践性能 |
> |------|---------------|-------------|
> | **单纯形法** | 指数级 $O(2^n)$ | 多项式（$\sim n$ 次迭代） |
> | **椭球法** | $O(m^2 \log(1/\epsilon))$ | 理论意义大于实用 |
> | **内点法** | $O(\sqrt{n} \log(1/\epsilon))$ 迭代 | 大规模问题首选 |

**内点法核心**：每次迭代求解 $O(n)$ 维线性系统，总复杂度 $O(n^{3.5} \log(1/\epsilon))$。

**平滑分析 (Spielman-Teng)**：单纯形法在随机扰动下的期望迭代次数是多项式的，解释了其实践中的良好表现。

#### 2.5.4.1 原始-对偶内点法详解 (Primal-Dual Interior Point Methods)

> [!note] 教科书参考
> 本节基于 Wright "Optimization in Theory and Practice" (2025) Section 4

**LP 标准形式与最优性条件 (KKT)**:

$$\min_x c^T x \quad \text{s.t.} \quad Ax = b, \; x \geq 0$$

KKT 条件（充要）:
$$A^T \lambda + s = c, \quad Ax = b, \quad (x, s) \geq 0, \quad x_i s_i = 0, \; \forall i$$

其中 $\lambda$ 是等式约束的拉格朗日乘子，$s$ 是对偶松弛变量。

**中心路径 (Central Path)**:

内点法的核心思想是追踪**中心路径**——满足以下条件的点的集合：
$$A^T \lambda + s = c, \quad Ax = b, \quad (x, s) > 0, \quad x_i s_i = \mu, \; \forall i$$

参数 $\mu > 0$ 称为**屏障参数**。当 $\mu \to 0$ 时，中心路径收敛到最优解。

**路径追踪算法 (Path-Following)**:

每次迭代求解牛顿系统：
$$\begin{pmatrix} 0 & A^T & I \\ A & 0 & 0 \\ S & 0 & X \end{pmatrix} \begin{pmatrix} \Delta x \\ \Delta \lambda \\ \Delta s \end{pmatrix} = \begin{pmatrix} 0 \\ 0 \\ \mu \mathbf{1} - XS\mathbf{1} \end{pmatrix}$$

其中 $X = \text{diag}(x)$，$S = \text{diag}(s)$。

> [!theorem] 内点法复杂度定理
> 长步路径追踪算法 (LPF) 在 $O(n \log(1/\epsilon))$ 次迭代内找到 $\epsilon$-近似解，每次迭代代价为 $O(n^3)$ 的线性系统求解。
> 
> **Mehrotra 预测-校正法**：通过自适应参数选择和二阶校正，在实践中显著快于理论界。

> **灵巧操作应用**：内点法在求解抓取规划的二次规划子问题（如力分配 QP）中是首选方法。其对初始点不敏感、收敛快速的特性非常适合 MPC 的实时需求。

#### 2.5.5 接触优化的复杂度困境

**为什么接触优化特别难？**

1. **非凸性**：互补约束 $\phi(q) \lambda = 0$ 定义的可行域是非凸的
2. **非光滑性**：接触力关于位置的梯度在接触瞬间不连续
3. **组合性**：$N$ 个接触点有 $3^N$ 种模式（分离/粘滞/滑动）

**松弛策略的复杂度-精度权衡**：

| 松弛方法 | 光滑性 | 精度损失 | 计算开销 |
|----------|--------|----------|----------|
| **Sigmoid 松弛** | $C^\infty$ | $O(\epsilon)$ | 低 |
| **Fischer-Burmeister** | $C^1$ | 精确（极限） | 中 |
| **Randomized Smoothing** | 期望意义 | $O(\sigma)$ | 高 |

### 2.6 非凸优化景观理论 (Nonconvex Optimization Landscapes)

> [!note] 教科书参考
> 本节基于 Arora et al. "Theory of Deep Learning" Chapter 6-7

深度学习和轨迹优化都涉及非凸损失函数。理解非凸景观的几何结构对于设计高效算法和分析收敛性至关重要。

#### 2.6.1 关键障碍的形式化定义

**全局/局部极小值 (Global/Local Minimum)**:

设 $f(w): \mathbb{R}^d \to \mathbb{R}$ 为目标函数：
- **全局极小值**: $w^*$ 使得 $\forall w: f(w^*) \leq f(w)$
- **局部极小值**: $\exists \epsilon > 0$ 使得 $\forall \|w' - w\| \leq \epsilon: f(w) \leq f(w')$
- **临界点 (Critical Point)**: $\nabla f(w) = 0$ 的点

**虚假局部极小值 (Spurious Local Minimum)**:

$$w \text{ 是虚假局部极小 } \Leftrightarrow w \text{ 是局部极小且 } f(w) > f(w^*)$$

这是基于局部搜索的优化算法（如梯度下降）无法逃离的陷阱。

**鞍点 (Saddle Point)**:

$$w \text{ 是鞍点 } \Leftrightarrow \nabla f(w) = 0 \text{ 且 } \nabla^2 f(w) \text{ 有正负特征值}$$

> [!example] 最简鞍点示例
> $f(w_1, w_2) = w_1^2 - w_2^2$ 在原点 $(0, 0)$ 是鞍点：
> - 沿 $(±1, 0)$ 方向函数值增加
> - 沿 $(0, ±1)$ 方向函数值减少

**二阶充分条件 (Hessian 判据)**:

设 $w$ 是临界点 ($\nabla f(w) = 0$)：
- $\nabla^2 f(w) \succ 0$ $\Rightarrow$ 局部极小
- $\nabla^2 f(w) \prec 0$ $\Rightarrow$ 局部极大
- $\nabla^2 f(w)$ 有正负特征值 $\Rightarrow$ 鞍点

#### 2.6.2 良好景观的特征：无虚假局部极小

许多非凸目标函数虽然不是凸的，但具有"良好"的景观结构——所有局部极小都是全局极小。

**Polyak-Łojasiewicz (PL) 条件**:

$$\|\nabla f(w)\|^2 \geq \mu (f(w) - f(w^*))$$

PL 条件意味着：梯度非零 $\Rightarrow$ 距最优仍有差距。满足 PL 条件的函数可用梯度下降以线性速率收敛。

**弱拟凸 (Weakly-Quasi-Convex)**:

$$\langle \nabla f(w), w - w^* \rangle \geq \tau (f(w) - f(w^*))$$

梯度方向与"指向最优解"的方向正相关。

**受限割线不等式 (RSI, Restricted Secant Inequality)**:

$$\langle \nabla f(w), w - w^* \rangle \geq \mu \|w - w^*\|^2$$

> [!theorem] 收敛性定理
> 若目标函数满足 PL、弱拟凸或 RSI 条件之一，且 $L$-光滑，则梯度下降以**几何（线性）速率**收敛到全局极小。

**灵巧操作应用**：在接触模式固定的局部区域内，轨迹优化目标函数通常满足 RSI 条件，这解释了为什么 iLQR 在"模式内"收敛很快。

#### 2.6.3 对称性与鞍点的必然性

神经网络和许多物理系统具有**置换对称性**。考虑两层网络 $h_\theta(x) = \sum_{i=1}^k \sigma(\langle w_i, x \rangle)$：

- 对任意神经元置换 $\pi$，有 $f(\theta) = f(\pi(\theta))$
- 若全局极小 $\theta^*$ 的神经元权重不全相同，则 $\pi(\theta^*)$ 也是全局极小

> [!important] 对称性导致非凸性
> 设 $\bar{\theta} = \frac{1}{k!} \sum_{\pi} \pi(\theta^*)$ 是所有置换的平均。
> 若 $f$ 是凸的，则 $\bar{\theta}$ 也应是全局极小。但 $\bar{\theta}$ 等价于单神经元网络，通常不能达到最优——矛盾！
> 
> **结论**：具有对称性的函数必然是非凸的，且必然有鞍点。

**二阶驻点 (Second-Order Stationary Point, SOSP)**:

$$\nabla f(w) = 0 \text{ 且 } \nabla^2 f(w) \succeq 0$$

这是"好的"临界点——不是鞍点。优化目标应是找 SOSP 而非任意临界点。

#### 2.6.4 鞍点逃逸：扰动梯度下降

> [!theorem] 鞍点逃逸定理 (Ge et al. 2015)
> **扰动梯度下降 (Perturbed GD)**：
> $$w_{t+1} = w_t - \eta \nabla f(w_t) + \xi_t, \quad \xi_t \sim \mathcal{N}(0, \sigma^2 I)$$
> 
> 对于 $L$-光滑、$\rho$-Hessian Lipschitz 的函数，扰动 GD 在 $\tilde{O}(1/\epsilon^2)$ 迭代内找到 $\epsilon$-近似 SOSP：
> $$\|\nabla f(w)\| \leq \epsilon, \quad \lambda_{\min}(\nabla^2 f(w)) \geq -\sqrt{\rho \epsilon}$$

**逃逸机制的物理直觉**：

在鞍点附近，Hessian 有负特征值对应的"逃逸方向"。随机扰动有 $\Omega(1/d)$ 概率落在逃逸方向的锥内，使迭代沿负曲率方向快速逃离。

**Stuck Region 的有限宽度**：

设 $\lambda_{\min}(\nabla^2 f(w)) = -\gamma < 0$（负曲率），则轨迹在该区域停留不超过 $O(\log(d)/\gamma)$ 步后必然逃离。

> **灵巧操作应用**：在 RL for manipulation 中，策略梯度方法经常遇到鞍点（如对称抓取姿态）。熵正则化（如 SAC 的 $-\alpha \mathcal{H}(\pi)$）相当于隐式添加了扰动，有助于鞍点逃逸。

#### 2.6.5 深度学习景观的经验发现

虽然深度网络的损失景观理论分析仍是开放问题，实验发现了以下规律：

| 现象 | 描述 | 对灵巧操作的启示 |
|------|------|-----------------|
| **无虚假局部极小** | 过参数化网络几乎所有局部极小都是全局极小 | 策略网络足够大时，RL 训练更稳定 |
| **鞍点占主导** | 高维空间中驻点几乎都是鞍点 | 随机初始化 + 噪声很重要 |
| **连通性** | 不同全局极小通过低损失路径连接 | 模式平均 (Mode Averaging) 有效 |
| **平坦极小泛化好** | $\nabla^2 f$ 特征值小的极小泛化性能更好 | SAM (Sharpness-Aware Minimization) |

#### 2.6.6 与表征理论的桥梁：NTK 区间下的凸化

> [!tip] 跨领域链接
> 当神经网络足够宽时，训练动力学退化为关于预测向量 $u$ 的**线性 ODE**，损失对 $u$ 是凸二次型，全局收敛有保证。这是非凸景观分析的一个**特殊但重要的 tractable subclass**。
>
> 严格的 NTK 推导（Lemma 9.2.2 / 9.2.3、特征分解收敛速率、Rademacher 泛化界 Eq. 9.11）见 [[RepresentationLearning#6.3.7 神经正切核 (Neural Tangent Kernel, NTK)|RepresentationLearning §6.3.7]]。
>
> **WMTS 关联**：NTK lazy regime 给出了"为何过参数化 WM 可以从 < 1h 真机数据稳定微调"（[[Idea-002-Latency-Aware-Actuator]]、[[Idea-012-WPTE-Tactile-Encoder]]）的理论保证。

------

## 3. 技术演进脉络与深度洞察 (Evolution & Insights)

要真正理解当前的 SOTA 方法，我们必须回顾技术演进的 Problem-Solution Chain。这不仅是历史的回顾，更是对“为什么旧方法失效”和“新方法引入了什么 Value-add”的深刻剖析。

### 3.1 阶段一：模态预设与几何规划 (The Pre-specified Mode Era)

**代表方法**：RRT (Rapidly-exploring Random Tree) + Quasi-static Grasping。

**核心逻辑**：

早期的灵巧操作被视为一个纯几何问题。规划器（如 RRT 或 PRM）首先在配置空间中搜索一条无碰撞路径将手移动到预抓取点（Pre-grasp pose），然后闭合手指。操作过程通常假设是准静态的（Quasi-static），即忽略惯性项 $M(q)\ddot{q}$。

**为什么失效？**

1. **割裂了过程与结果**：灵巧操作的核心在于 In-hand Manipulation（如转笔、调整握姿），这要求手指与物体在接触的同时发生相对运动。静态规划无法处理动态的 Rolling/Sliding，因为它无法预测接触力的演化。
2. **概率零陷阱**：在高维空间中，随机采样（Sampling-based）方法极难采样到满足接触约束的状态。接触流形（Contact Manifold）是配置空间中的一个低维子流形（体积为零）。RRT 在没有引导的情况下，采样点落在接触面上的概率为零 。
3. **不仅是几何问题**：仅仅几何上接触并不意味着物理上可行。物体可能会滑落，需要动力学一致性（Dynamics Consistency）验证。

### 3.2 阶段二：混合整数规划与模态调度 (Hybrid Zero Dynamics & Mode Scheduling)

**代表方法**：MIQP (Mixed-Integer Quadratic Programming)。

**核心逻辑**：

为了处理接触的离散性，研究者引入了整数变量 $z \in \{0, 1\}$ 来表示接触状态（0=分离，1=接触）。动力学约束被写成“大M法（Big-M Formulation）”形式：

$$\lambda \le M z$$

$$\phi(q) \le M (1-z)$$

这样，整个问题变成了一个混合整数规划问题。

**Value-add**：

提供了数学上严谨的全局最优解（在离散化精度下）。能够处理硬接触约束。

**失效原因**：

**组合爆炸（Combinatorial Explosion）**。对于一个有 $N_c$ 个潜在接触点的系统，每一步的模态组合数是 $2^{N_c}$。对于 $T$ 步的轨迹，总的离散状态数是 $(2^{N_c})^T$。对于灵巧手（$N_c$ 很大，如指尖、指腹、手掌），这在计算上是不可行的（NP-hard）。

### 3.3 阶段三：接触隐式轨迹优化 (Contact-Implicit Trajectory Optimization, CITO)

**关键人物**：Michael Posa, Russ Tedrake (MIT)。

**突破点**： 提出了一种直接方法（Direct Method），打破了模态预设的限制。 CITO 不再使用整数变量，而是将接触力 $\lambda$ 作为连续决策变量，并将 LCP 约束直接加入非线性规划（NLP）中。

**核心逻辑**：

将整个轨迹离散化（通常使用 Backward Euler 或 Runge-Kutta），构建一个巨大的 NLP：

$$\min_{x_{1:T}, u_{1:T}, \lambda_{1:T}} \sum_{t=1}^T \text{Cost}(x_t, u_t)$$

$$\text{s.t. } \text{Dynamics}(x_t, u_t, \lambda_t) = 0$$

$$0 \le \phi(q_t) \perp \lambda_t \ge 0 \quad (\text{LCP Constraints})$$

**Value-add**：

- **无需预设接触序列**：算法会自动“发现”何时接触、何时分离。机器人可以利用环境（如桌面）来辅助操作（Extrinsic Dexterity）。
- **统一框架**：规划与控制在同一数学框架下完成，能够生成利用动力学特性的复杂动作（如抛掷、滑动）。

**缺陷（Skeptical View）**：

- **数学规划的噩梦**：带有互补约束的数学规划（MPCC）违反了标准的约束规范（Constraint Qualifications, LICQ）。这意味着在最优解处，拉格朗日乘子可能无界。
- **局部极小值**：求解器（如 SNOPT, IPOPT）经常卡在不可行的局部极小值，或者需要极其精确的初值（Warm-start）。
- **无法实时**：求解一次可能需要几秒到几分钟，无法直接用于实时 MPC。

### 3.4 阶段四：可微物理与平滑化 (The Differentiable Physics & Smoothing Era)

**关键人物**：Emanuel Todorov (Mujoco), Sergey Levine, Zachary Manchester。

**问题**：为了使用极速的求解器（如 iLQR/DDP），我们需要动力学方程 $f(x,u)$ 是二阶可微的。刚体接触破坏了这一条件。

**解决方案**：**Contact Smoothing / Soft Contact**。

这一流派认为，与其死守 LCP 的硬约束，不如在物理模型上做妥协，换取优化的平滑性。

将硬接触的 LCP 约束松弛为平滑函数。例如，使用 Sigmoid 或 Log-Barrier 函数来近似接触力：

$$\lambda \approx k_p \cdot \text{sigmoid}(-\frac{\phi(q)}{\epsilon})$$

或者在 Cost Function 中使用 Barrier Term 惩罚穿透 。

**Insight**： 通过平滑化，接触不再是一个突变的“开关”，而是一个陡峭的“坡”。这使得梯度信息（Gradient Information）能够**穿透**接触事件。例如，当手指还没碰到物体时，距离 $\phi(q)$ 的微小变化会引起力的微小变化，从而产生非零梯度。这直接告诉优化器：“再靠近一点，力就会增加”。这赋能了基于梯度的算法（如 DDP）在灵巧操作中的应用 。

**Variational Integrators (Manchester)**: 另一种思路是使用变分积分器 。这种方法从离散拉格朗日量出发，通过离散变分原理导出运动方程。它在处理接触时具有更好的能量守恒特性，并且能够提供更稳定的梯度。

---

> [!important] 🔬 同伦优化在灵巧操作中的应用 (Homotopy Optimization)
> 
> **来源**：[[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack (ICLR 2025)]] — 数据飞轮与同伦方法
> 
> **核心思想**：当优化问题存在严重的局部极小值时，**同伦方法（Continuation Method）**构造一条从"简单问题"到"目标问题"的连续路径，逐步逼近目标。
> 
> **在灵巧操作中的应用**：
> 如果直接优化复杂的手部操作轨迹（如 pen spinning）失败，先优化简化版本：
> 
> $$H(\lambda) = (1-\lambda) \cdot \text{简单问题} + \lambda \cdot \text{目标问题}, \quad \lambda: 0 \to 1$$
> 
> **简化路径示例**：
> ```
> 原始: 复杂 pen spinning (大幅度旋转 + 手指换位)
>     ↑ λ = 1.0
> 层3: 小幅度 pen rotation
>     ↑ λ = 0.7
> 层2: pen translation only
>     ↑ λ = 0.3
> 层1: static grasping
>     ↑ λ = 0.0
> ```
> 
> **与思维链的类比**：同伦优化类似于推理中的 Chain-of-Thought，通过中间步骤降低问题的非凸性。
> 
> **灵巧操作的意义**：接触隐式优化（CITO）经常陷入局部极小值。同伦方法通过渐进增加接触复杂度（先无接触→稳定接触→动态接触）实现突破。

---

> [!important] 🔬 阻抗参数的凸辨识 (Convex Impedance Identification)
> 
> **来源**：[[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Prosthesis VI (IEEE TRO 2022)]] — 数据驱动阻抗控制
> 
> **问题**：阻抗控制中的参数 $(K, B, \theta_{eq})$ 如何自动确定？传统方法需要专家数小时手工调参。
> 
> **关键洞察**：固定平衡角 $\theta_{eq}$ 后，阻抗方程 $\tau = -K(\theta - \theta_{eq}) - B\dot{\theta}$ 关于 $(K, B)$ 是**线性**的！
> 
> **两步凸优化**：
> 1. **Step 1**：从运动学数据估计 $\theta_{eq}$ 的参数化形式
> 2. **Step 2**：凸优化求解 $K(\phi, v, \alpha)$, $B(\phi, v, \alpha)$
>    $$\min_{c^K, c^B} \sum_n \| \tau_n^{data} - \tau_n^{model} \|^2 \quad \text{(凸二次规划)}$$
> 
> **参数化技巧**：将阻抗参数表示为相位变量 $\phi$、速度 $v$、任务参数 $\alpha$ 的连续函数：
> $$K(\phi, v, \alpha) = \sum_{i,j,k} c^K_{ijk} B_i(\phi) P_j(v) P_k(\alpha)$$
> 其中 $B_i$ 是 B-spline 基函数。
> 
> **灵巧操作的意义**：手部接触控制中的刚度/阻尼设计可以借鉴此方法——从演示数据自动学习"抓取力应该如何随操作相位变化"。

------

## 4. 核心算法实现：轨迹优化 (Implementation: Trajectory Optimization)

作为首席科学家，我要求你不仅理解概念，还要能实现核心算法。本节聚焦于基于 Differentiable Physics 的轨迹优化。我们将重点放在 **Iterative Linear Quadratic Regulator (iLQR)** 及其在处理接触时的变体。

### 4.1 核心算法：iLQR / DDP

iLQR 是 Differential Dynamic Programming (DDP) 的一种变体（通常忽略二阶动力学项以加速计算）。它利用 Bellman 最优性原理，通过前向（Forward Pass）和后向（Backward Pass）迭代，具有二阶收敛速度 。

> [!note] 线性原型
> iLQR 在每次迭代中将非线性动力学线性化为 $\delta x_{k+1} = A_k \delta x_k + B_k \delta u_k$，并用二次代价近似——此时**Backward Pass 退化为标准的离散时间 Riccati 递推**。其线性闭式解、稳定性证明与最优反馈律见 [[ControlTheory#11.2 离散时间有限时域 LQR：Riccati 递推|ControlTheory §11.2 (Theorem 11.2)]]。理解 LQR 是理解 iLQR/DDP 收敛性的前提。

#### 4.1.1 物理直觉与复杂度

iLQR 的本质是在当前轨迹附近进行**局部二次近似**。它问的问题是：“如果我在某个时刻 $t$ 稍微改变一点状态 $\delta x$ 或控制 $\delta u$，总的 Cost 会如何变化？”

计算复杂度为 $O(T \cdot (n_x^3 + n_u^3))$，这比直接求解 NLP 的 $O((T n_x)^3)$ 要快得多，因为它利用了问题的时序结构（Riccati Recursion）。

#### 4.1.2 核心逻辑代码 (Core Logic - Python)

以下代码展示了 iLQR 的核心迭代逻辑，**去除了所有防御性代码**，聚焦于数学运算。

Python

```
import numpy as np

class iLQR_Core:
    def __init__(self, model, cost_func, T, dt):
        """
        model: Differentiable Physics Model (must support derivatives)
        cost_func: Quadratic Cost Function approximation
        T: Horizon length
        dt: Time step
        """
        self.model = model
        self.cost = cost_func
        self.T = T
        self.dt = dt

    def backward_pass(self, x_seq, u_seq, lamb_reg):
        """
        Backward Pass: Compute gains k, K by solving Riccati equations backwards.
        lamb_reg: Levenberg-Marquardt regularization factor to ensure Quu > 0
        """
        n_x = x_seq.shape
        n_u = u_seq.shape
        
        k_seq = np.zeros((self.T, n_u)) # Feedforward gains
        K_seq = np.zeros((self.T, n_u, n_x)) # Feedback gains
        
        # Initialize Value Function derivatives at terminal step
        # V(x_T) = Cost_final(x_T)
        Vx, Vxx = self.cost.terminal_derivatives(x_seq[-1])
        
        for t in range(self.T - 1, -1, -1):
            x, u = x_seq[t], u_seq[t]
            
            # 1. Linearize Dynamics (f_x, f_u) & Quadratize Cost (l_x, l_u,...)
            # CRITICAL: This is where Differentiable Physics enters.
            # fx, fu must capture the gradient THROUGH contact.
            fx, fu = self.model.derivatives(x, u, self.dt) 
            lx, lu, lxx, luu, lux = self.cost.step_derivatives(x, u)
            
            # 2. Q-function expansion (Action-Value function)
            # Q(dx, du) approx Cost + V(next_state)
            Qx  = lx + fx.T @ Vx
            Qu  = lu + fu.T @ Vx
            Qxx = lxx + fx.T @ Vxx @ fx
            Quu = luu + fu.T @ Vxx @ fu
            Qux = lux + fu.T @ Vxx @ fx
            
            # 3. Regularization (Levenberg-Marquardt) 
            # In contact-rich tasks, Quu often becomes indefinite (negative eigenvalues).
            # This step is physically equivalent to adding damping to the update.
            Quu_reg = Quu + lamb_reg * np.eye(n_u)
            
            # 4. Compute Optimal Gains via Cholesky/Inverse
            # u* = argmin Q(dx, du) => u* = -Quu^-1 (Qu + Qux dx) = k + K dx
            # Box-QP can be used here for control limits (not shown for brevity)
            try:
                Quu_inv = np.linalg.inv(Quu_reg)
            except np.linalg.LinAlgError:
                # Fallback or increase lambda in outer loop
                return None 

            k = -Quu_inv @ Qu
            K = -Quu_inv @ Qux
            
            # 5. Update Value Function for next step (t-1)
            # Vx = Qx + K.T @ Quu @ k + K.T @ Qu + Qux.T @ k
            # Using the optimal condition Qu + Quu k = 0 simplifies terms
            Vx  = Qx + K.T @ Quu @ k + K.T @ Qu
            Vxx = Qxx + K.T @ Quu @ K + K.T @ Qux + Qux.T @ K
            
            # Symmetrize Vxx to avoid numerical drift
            Vxx = 0.5 * (Vxx + Vxx.T)
            
            k_seq[t] = k
            K_seq[t] = K
            
        return k_seq, K_seq

    def forward_pass(self, x_seq, u_seq, k_seq, K_seq, alpha=1.0):
        """
        Forward Pass: Rollout new trajectory with computed gains.
        alpha: Line search parameter (backtracking)
        """
        x_new = [x_seq]
        u_new =
        
        for t in range(self.T):
            # Calculate control deviation from nominal trajectory
            dx = x_new[-1] - x_seq[t]
            
            # Apply control law: u = u_nom + alpha*k + K*dx
            du = alpha * k_seq[t] + K_seq[t] @ dx
            u_applied = u_seq[t] + du
            
            u_new.append(u_applied)
            
            # Step dynamics (Nonlinear rollout)
            x_next = self.model.step(x_new[-1], u_applied, self.dt)
            x_new.append(x_next)
            
        return np.array(x_new), np.array(u_new)
```

### 4.2 处理接触的关键技术细节 (Critical Implementation Details)

在上述代码中，`model.derivatives(x, u)` 是最棘手的部分。如果直接使用刚体物理引擎（如 Bullet/ODE），梯度往往是错误的或零。以下是三种主流的解决方案：

#### 4.2.1 方案 A：平滑接触模型 (Smoothed Contact Model)

这是目前最实用的方法。我们用一个连续可微的函数近似 Signorini 条件。

假设接触距离为 $\phi(q)$，法向力 $\lambda_n$ 可以建模为：

$$\lambda_n(\phi) = \frac{k}{1 + \exp(\beta \cdot \phi(q))}$$

这是一个 Sigmoid 函数。当 $\phi(q)$ 为正（分离）时，力以指数速度衰减但不为零。

**梯度分析**：

$$\frac{\partial \lambda_n}{\partial q} = \frac{\partial \lambda_n}{\partial \phi} \frac{\partial \phi}{\partial q}$$

由于 Sigmoid 的导数处处非零，这就提供了一个“力场”，引导手指去接触物体。参数 $\beta$ 控制了硬度。$\beta$ 越大越接近刚体，但优化越不稳定（Stiff Gradients）。

#### 4.2.2 方案 B：隐式微分 (Implicit Differentiation)

如果坚持使用 LCP（硬接触）以保证物理真实性，我们可以使用隐式微分定理。

在最优解处，LCP 的解 $\lambda^*$ 满足残差方程 $R(q, u, \lambda^*) = 0$。我们可以通过隐函数定理计算 $\frac{\partial \lambda^*}{\partial u}$，而无需通过迭代求解器进行反向传播。

$$\frac{\partial \lambda^*}{\partial u} = - \left( \frac{\partial R}{\partial \lambda} \right)^{-1} \frac{\partial R}{\partial u}$$

这在 Posa 的工作中被广泛提及 。 **问题**：当接触状态发生变化（Active set changes）时，矩阵 $\frac{\partial R}{\partial \lambda}$ 是奇异的或不可逆的。这需要复杂的广义雅可比（Generalized Jacobian）处理。

#### 4.2.3 方案 C：随机平滑 (Randomized Smoothing)

通过在动力学参数或状态上加入噪声，然后取期望，可以使得原本非光滑的 Cost Function 变得光滑。这通常用于 **MPPI** 或 **Evolutionary Strategies**。

------

## 5. 实时控制：模型预测控制 (Real-Time Control: MPC)

轨迹优化通常作为离线规划器（Offline Planner）。要在真实机器人上执行，必须将其通过 Receding Horizon Control (RHC) 转化为 MPC。

### 5.1 实时性的挑战 (The Latency Challenge)

灵巧操作的接触事件发生极快（~1-5ms）。相比之下，四足机器人的步态周期可能是 500ms，而机械臂抓取可能是数秒。 在灵巧操作中，如果 MPC 的求解时间超过 20-30ms，机器人就会出现“盲区”。例如，当手指滑过物体边缘时，如果控制器反应不及，物体就会弹飞。这就是所谓的 **Sim-to-Real Gap** 在时间维度上的体现 。

### 5.2 线性化与 SQP (Linearization & SQP)

为了加速 MPC，现代框架（如 OCS2, Acados）通常使用 **Sequential Quadratic Programming (SQP)**。

其核心思想是：不每次都重新求解完整的非线性问题，而是只做一次 QP 近似（Real-Time Iteration, RTI）。

**Warm-Starting 策略**：

利用上一时刻的解 $x^*(t)$ 作为当前时刻的初值。公式如下：

$$x_{init}^{k+1} = \text{Shift}(x_{sol}^k)$$

由于物理世界的连续性，这通常非常有效。但在接触发生的瞬间（Impact），解会发生跳变，Warm-Start 可能失效，导致求解器发散。

**Insight**：在灵巧操作 MPC 中，必须对接触事件进行特殊处理。 一种方法是 **Contact Schedule Smoothing**：在 MPC 预测时域内，不强制要求在某一特定时刻发生接触，而是允许接触时间在一定范围内浮动（通过松弛互补约束实现）。

### 5.3 基于采样的 MPC (Sampling-based MPC)

鉴于梯度的局限性（容易陷入局部极小），基于采样的 MPC（如 MPPI - Model Predictive Path Integral）在灵巧操作中正重新获得关注。

**核心思想**：

利用 GPU 的大规模并行能力，同时模拟数千条轨迹。

$$u_t^* = \frac{\sum_{k=1}^K w_k u_t^{(k)}}{\sum_{k=1}^K w_k}$$

权重 $w_k$ 由该轨迹的 Cost 决定：$w_k = \exp(-\frac{1}{\lambda} S(u^{(k)}))$。

**优势**：

1. **不需要梯度**：可以直接使用不可微的 Cost Function（如二值化的抓取成功率）。
2. **处理多模态**：采样自然地覆盖了多种接触可能性。
3. **鲁棒性**：对模型误差不那么敏感。

**劣势**： **维数灾难（Curse of Dimensionality）**。对于 24-DoF 的灵巧手，纯随机采样几乎不可能采样到“手指尖正好捏住笔尖”这种低概率高精度事件。 **混合方案（Hybrid Approach）**：使用 iLQR 生成一条 Nominal Trajectory，然后在该轨迹附近进行 MPPI 采样，以增强鲁棒性 。

------

## 6. 深度专题：可微抓取合成 (Differentiable Grasp Synthesis)

优化不仅控制运动，还需要知道“什么是好的抓取”。我们需要将离散的抓取指标转化为可微的 Loss Function。

### 6.1 传统指标的不可微性

Ferrari-Canny $\epsilon$-metric 涉及计算 6D Wrench Space 的凸包（Convex Hull），然后计算原点到凸包表面的最短距离。这是一个纯几何算法，难以对关节角 $q$ 求导。

### 6.2 可微力封闭能量 (Differentiable Force Closure Energy)

我们可以定义一个能量函数 $E(q)$，当且仅当形成力封闭时 $E(q)$ 最小。 构造如下 Loss Function ：

$$L(q) = w_{dist} \sum_{i} \|p_i(q) - p_{obj}\|^2 + w_{force} E_{FC}(n_i, p_i) + w_{pen} E_{pen}(q)$$

- **接触引导项**：利用 Signed Distance Function (SDF) 引导指尖靠近物体表面。
- **力封闭项**：$E_{FC}$ 惩罚接触法向量 $n_i$ 无法抵消外力的情况。理想情况下，接触法向量的和应该能覆盖整个单位球。可以近似为：最小化法向量均值的模长，同时最大化法向量之间的夹角方差。
- **穿透惩罚**：$E_{pen} = \sum \text{ReLU}(-\phi(q))$。

**代码逻辑：基于梯度的抓取姿态优化**

Python

```
import torch

def optimize_grasp_pose(hand_model, object_sdf, initial_q):
    """
    Optimize joint angles q to maximize grasp quality using gradient descent.
    Using PyTorch for auto-differentiation.
    """
    q = initial_q.clone().detach().requires_grad_(True)
    optimizer = torch.optim.Adam([q], lr=0.01)
    
    for _ in range(100):
        # Forward Kinematics (Differentiable)
        # Returns contact point positions and surface normals at those points
        contact_points, normals = hand_model.forward_kinematics(q)
        
        # 1. Contact Term: Minimize distance to surface
        # object_sdf returns signed distance. 
        dists = object_sdf(contact_points)
        dist_loss = torch.sum(dists**2)
        
        # 2. Force Closure Term (Simplified Differentiable Proxy)
        # We want normals to oppose each other.
        # Sum of normals should be close to zero (equilibrium)
        center_force = torch.mean(normals, dim=0)
        equilibrium_loss = torch.norm(center_force) 
        
        # We also want spread (to resist torques). 
        # Maximize variance of contact points relative to object center
        spread_loss = -torch.var(contact_points, dim=0).sum()

        # 3. Penetration Term (Constraint)
        # Penalize if distance is negative
        pen_loss = torch.sum(torch.relu(-dists))
        
        # Weighted Sum
        total_loss = 1.0 * dist_loss + 10.0 * equilibrium_loss + 0.1 * spread_loss + 100.0 * pen_loss
        
        optimizer.zero_grad()
        total_loss.backward()
        optimizer.step()
        
    return q.detach()
```

此方法的关键在于利用 **SDF 的可微性质**，将几何约束转化为平滑的势能场。这使得我们可以在没有接触的情况下，就让梯度“拉动”手指到达最优位置。

------

## 7. 数据与比较分析 (Comparisons & Data)

为了更直观地理解各方法的优劣，我们提供以下对比分析。

### 表 1：主流灵巧操作优化方法对比

| **特性维度**   | **Posa's CITO (Direct Method)**  | **iLQR / DDP (Shooting Method)**   | **MPPI (Sampling Method)**     |
| -------------- | -------------------------------- | ---------------------------------- | ------------------------------ |
| **接触建模**   | LCP (Hard Constraints)           | Soft / Smooth Contact (Sigmoid)    | Any (Blackbox / Sim)           |
| **梯度处理**   | 互补约束处理 (MPCC)              | 解析梯度 (Analytical Derivatives)  | 无需梯度 (Zeroth-order)        |
| **求解器**     | IPOPT / SNOPT (NLP)              | Riccati Recursion (Linear Algebra) | Parallel Rollouts (GPU)        |
| **计算复杂度** | 极高 (Non-polynomial worst case) | $O(T N^3)$ (Quadratic Convergence) | $O(K T)$ (Linear with samples) |
| **局部极小值** | 严重 (经常卡死)                  | 中等 (依赖初值)                    | 较好 (具有探索性)              |
| **实时性**     | 无法实时 (>1s)                   | 可实时 (10-50ms)                   | 可实时 (10-50ms, need GPU)     |
| **适用场景**   | 离线生成复杂动作库，理论研究     | 实时 MPC，接触相对平滑的任务       | 高不确定性环境，非光滑 Cost    |

### 表 2：接触模型对梯度的影响

| **模型类型**         | **物理真实性**          | **梯度特性**                  | **优化难度**              |
| -------------------- | ----------------------- | ----------------------------- | ------------------------- |
| **刚体 (LCP)**       | 高 (无穿透，库伦摩擦)   | 0 (非接触) 或 $\infty$ (碰撞) | 极难 (需特殊求解器)       |
| **罚函数 (Penalty)** | 低 (类似于弹簧，有穿透) | 线性或二次增长                | 易 (但刚度过大会导致震荡) |
| **Log-Barrier**      | 中 (渐进不可穿透)       | 平滑非线性                    | 中 (需调节 Barrier 参数)  |
| **Sigmoid/Soft**     | 中 (允许微小变形)       | Sigmoid 形状，提供远距离引导  | 较易 (适合 DDP)           |

------

## 8. 结论与展望 (Conclusion & Outlook)

灵巧操作的优化理论正处于从“几何规划”向“物理兼容的动态规划”转型的关键期。我们不再满足于规划一个静态的抓取姿态，而是追求在时域上连续控制接触力的演化。

1. **物理建模的 Paradigm Shift**：从追求绝对精确的 LCP 硬接触模型，转向追求优化友好的 Differentiable Soft Contact 模型。我们意识到，**在优化循环中，错误的梯度比没有梯度要好，只要它指向正确的方向**。平滑化不仅仅是数学技巧，更是物理先验的注入。
2. **算法融合 (Algorithm Fusion)**：未来的主流架构将是 **iLQR/DDP (产生高精度轨迹)** + **MPPI (处理多模态与不确定性)** 的结合。iLQR 提供精准的“手术刀”式的控制，而 MPPI 提供鲁棒的“大锤”式的探索。
3. **硬件与算力**：随着 GPU 物理仿真（如 Isaac Gym, Brax, Dojo）的普及，能够并行求解数万个优化问题的能力将彻底改变 MPC 的实时性瓶颈。我们正从 Single-Shooting 走向 Massive-Parallel-Shooting。

**首席科学家视角的最终建议**：

------

## 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及优化理论的核心主题

### 轨迹优化与 MPC
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 同伦优化轨迹跟踪
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 轨迹优化数据生成
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] — 规划引导扩散

### 阻抗参数优化
- [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking]] — 凸阻抗辨识
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 阻抗空间优化

### 奖励与课程优化
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — LLM 奖励设计
- [[Curriculum Learning]] — 课程学习理论（continuation method 与凸→非凸渐进）
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] — 熵引导示范加速

### 约束优化与对偶方法
- [[Reachability Constrained Reinforcement Learning]] — PPO/SAC-Lagrangian（拉格朗日对偶分解安全约束）
- [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]] — 单调性约束的凸优化
- [[Safe Model-based Reinforcement Learning with Stability Guarantees]] — CLF-CBF 对偶框架

### 稀疏与可解释优化
- [[Weight-sparse transformers have interpretable circuits]] — $L_0$ 稀疏优化

在构建 Obsidian 知识库时，不要被复杂的数学名词（如 Complementarity Constraints, Variational Integrators）吓倒。核心要抓住“梯度是如何穿过接触点”这一物理图像。所有的算法变体（Soft Contact, Randomized Smoothing, Implicit Differentiation）本质上都是为了修复断裂的梯度流，使得优化器能够“感觉”到接触的存在。理解了这一点，你就掌握了灵巧操作优化的钥匙。