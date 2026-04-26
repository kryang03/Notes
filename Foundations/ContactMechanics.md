---
tags:
  - foundation
  - contact-mechanics
  - dexterous-manipulation
  - friction
  - LCP
aliases:
  - 接触力学
  - Contact
  - 摩擦锥
  - Friction Cone
created: 2026-01-31
related:
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[ComputationalGeometry]]"
---

# 机器人灵巧操作中的高级接触力学：从几何运动学到可微物理

> [!tip] 相关领域
> - [[Dynamics]] - 接触动力学与多体动力学的耦合
> - [[ControlTheory]] - 力/位混合控制依赖接触模型
> - [[Optimization]] - LCP/QP 求解器是接触仿真的核心
> - [[ComputationalGeometry]] - SDF 用于碰撞检测
>
> **相关论文**:
> - [[GenDexGrasp - Generalizable Dexterous Grasping]] - 以 contact map 作为跨手型抓取表征，并用 force closure 合成 MultiDex
> - [[Deep Dynamics Models for Learning Dexterous Manipulation]] - contact-rich MPC 在多指手任务中的经验验证

## 1. 执行摘要与引言

本报告旨在为Robotics Dexterous Manipulation（机器人灵巧操作）领域的知识库构建提供详尽的理论支撑与技术分析。作为该领域的首席科学家，本报告将超越基础教科书的陈述，深入探讨接触力学（Contact Mechanics）在现代机器人学中的核心地位。分析路径将严格遵循从微观的接触点几何演化（点接触）到宏观的软指变形（软指接触），以及从经典的库伦摩擦模型到现代计算动力学中的线性互补问题（LCP）与凸优化求解策略。

灵巧操作的本质在于通过接触界面管理力与运动的传递。与传统的工业机器人抓取（仅关注刚性闭合）不同，灵巧操作要求机器人能够主动利用接触点的滚动（Rolling）、滑动（Sliding）甚至受控的扭转（Torsional friction）来调整物体姿态。这要求我们不仅要建立精确的运动学模型来描述接触点在流形表面的演化，还必须构建数值稳定的动力学求解器来处理接触引入的非光滑性（Non-smoothness）和硬约束。

本报告将分为四个主要部分：首先深入剖析基于微分几何的接触运动学，重点推导并解析Montana方程；其次，探讨从单点刚性接触到多点软接触的物理建模演变，特别是软指接触中的极限曲面概念；第三，详细阐述计算接触动力学的核心算法，对比分析LCP求解器、迭代求解器（PGS/Sequential Impulses）与基于位置的动力学（XPBD）；最后，针对当前基于学习的控制策略，分析可微物理引擎中的梯度计算方法及其在Sim2Real（仿真到现实）迁移中的关键作用。

------

## 2. 接触几何运动学：流形上的演化

在灵巧操作中，手指与物体之间的接触不再是一个静态的连接，而是一个随时间变化的动态过程。理解接触点如何在两个曲面上移动，是实现“手内操作”（In-Hand Manipulation）的理论基础。

### 2.1 表面微分几何基础

为了数学化地描述接触，我们将相互作用的两个物体——物体1（如机器人手指）和物体2（如被操作物体）——视为三维欧几里得空间中的光滑曲面。在接触点局部，我们需要建立坐标系来描述表面的几何性质。

#### 2.1.1 高斯标架 (Gauss Frame) 与度量张量

对于任意曲面 $i \in \{1, 2\}$，我们在接触点建立局部正交坐标系，称为高斯标架 $\{x, y, z\}$。其中 $z$ 轴严格沿曲面外法线方向，$x, y$ 轴位于切平面内。设曲面由参数坐标 $u_i = (u, v)$ 参数化，即 $f_i: \mathbb{R}^2 \to \mathbb{R}^3$。

表面的局部“伸缩”性质由**第一基本形式**（即度量张量，Metric Tensor）$M_i$ 描述。度量张量定义了参数空间速度 $(\dot{u}, \dot{v})$ 到切平面线速度 $v_{tan}$ 的映射关系 ：

$$v_{tan} = M_i \dot{u}_i$$

如果参数化是正交的，则 $M_i$ 为对角矩阵：

$$M_i = \begin{bmatrix} ||\partial f_i / \partial u|| & 0 \\ 0 & ||\partial f_i / \partial v|| \end{bmatrix}$$

#### 2.1.2 曲率张量与挠率

表面的弯曲程度由**第二基本形式**描述，结合度量张量，我们要关注的是**曲率张量** (Curvature Tensor) $K_i$。曲率张量描述了当你沿着表面移动时，表面法线 $z$ 的变化率。数学上，它是法向量对切向位移的梯度的投影 。

$$\dot{n}_i = -M_i K_i \dot{u}_i$$

其中 $K_i$ 的特征值对应于主曲率。例如，对于半径为 $R$ 的球体，$K = \text{diag}(1/R, 1/R)$；对于平面，$K=0$。

此外，**挠率张量** (Torsion Tensor) $T_i$ 描述了高斯标架自身关于法线的旋转（即坐标系的“扭曲”）。这在处理非测地线运动时尤为重要。

### 2.2 Montana接触运动学方程

David Montana在1988年提出的接触运动学方程是灵巧操作领域的里程碑。这些方程建立了物体间的**相对刚体运动**（Relative Rigid Body Motion）与**接触点在各自表面上的演化速度**（Contact Point Evolution）之间的微分关系 。

设两个物体间的接触保持闭合（即法向距离为0），定义接触点在两个物体局部坐标系中的演化率为 $\dot{u}_1, \dot{u}_2$，以及两个高斯标架 $x$ 轴之间的相对夹角 $\psi$ 的变化率 $\dot{\psi}$。物体1相对于物体2的局部平移速度为 $(v_x, v_y, v_z)$，角速度为 $(\omega_x, \omega_y, \omega_z)$。注意，对于持续接触，$v_z=0$。

Montana方程组如下：

**1. 接触点在物体1表面的运动速度：**

$$\dot{u}_1 = M_1^{-1} (K_1 + R_\psi K_2 R_\psi^T)^{-1} \left( \begin{bmatrix} -\omega_y \\ \omega_x \end{bmatrix} - R_\psi K_2 \begin{bmatrix} v_x \\ v_y \end{bmatrix} \right)$$

**2. 接触点在物体2表面的运动速度：**

$$\dot{u}_2 = M_2^{-1} R_\psi^T (K_1 + R_\psi K_2 R_\psi^T)^{-1} \left( \begin{bmatrix} -\omega_y \\ \omega_x \end{bmatrix} + K_1 \begin{bmatrix} v_x \\ v_y \end{bmatrix} \right)$$

**3. 接触角的演化速度：**

$$\dot{\psi} = \omega_z + T_1 M_1 \dot{u}_1 + T_2 M_2 \dot{u}_2$$

其中，$R_\psi$ 是关于角度 $\psi$ 的二维旋转矩阵。

#### 2.2.1 物理洞察与高阶分析

- **相对曲率项的重要性**：方程中的核心项 $(K_1 + R_\psi K_2 R_\psi^T)^{-1}$ 代表了**相对曲率**的逆。
  - 如果两个物体是**共形的**（conformal），例如一个半径为 $R$ 的球在一个半径为 $R$ 的球窝中旋转，则相对曲率矩阵接近奇异（零矩阵），其逆趋于无穷大。这意味着接触点的速度变得不确定——这在物理上对应于面接触而非点接触。因此，Montana方程仅适用于非共形的点接触情形 。
  - **曲率估计与主动感知**：在未知环境中，机器人可以通过测量自身的关节运动（从而推算 $\omega, v$）以及利用触觉传感器测量接触点的移动速度 $\dot{u}_1$，反向求解上述方程中的 $K_2$。这使得机器人能够通过“抚摸”物体来重建其局部几何形状，这被称为**基于本体感知的曲率估计** 。
- **纯滚动 vs. 纯滑动**：
  - **纯滚动 (Pure Rolling)**：当切向相对速度 $v_x = v_y = 0$ 时，接触点的移动完全由相对角速度 $(\omega_x, \omega_y)$ 驱动。滚动接触是**非完整约束**（Non-holonomic Constraint）的典型例子——路径依赖性意味着你不能仅通过改变位置变量回到原点，必须考虑路径积分。这在规划手内操作（如在手指间转动笔）时引入了复杂的控制挑战 。
  - **纯滑动 (Pure Sliding)**：当 $\omega_x = \omega_y = 0$ 时，接触点的移动仅由切向速度驱动。此时，接触点在物体表面的轨迹取决于切向力的方向和物体表面的几何特性。

### 2.3 接触雅可比矩阵 (Contact Jacobian)

在构建多指抓取系统时，我们需要将上述接触层面的运动学与机器人的关节空间联系起来。

**手部雅可比 (Hand Jacobian, $J_h$)** 将关节速度 $\dot{q}$ 映射到手指末端的高斯标架速度。而**抓取矩阵 (Grasp Matrix, $G$)** 则描述了接触点处的力如何传递到物体的质心（COM）产生合力和合力矩 。

$$V_{contact} = J_h \dot{q}$$

$$W_{object} = G V_{contact}$$

其中 $W_{object}$ 是施加在物体上的旋量（Wrench）。重要的是，抓取矩阵 $G$ 的结构直接取决于所采用的**接触模型**（点接触、硬指、软指）。对于软指接触，$G$ 矩阵不仅包含力的传递块，还必须包含力矩传递块，这增加了系统的可控自由度，使得某些在点接触模型下不可控的操作（如原地旋转物体）成为可能 。

### 2.4 抓取矩阵的严格数学定义 (Formal Definition of Grasp Matrix)

> [!note] 教科书参考
> 本节严格遵循 Murray, Li & Sastry 《A Mathematical Introduction to Robotic Manipulation》Chapter 5-6 的定义体系。

设有 $k$ 个接触点 $\{p_1, ..., p_k\}$，每个接触点相对于物体质心的位置向量为 $r_i$，接触法向为 $n_i$。

#### 2.4.1 单点接触旋量 (Single Contact Wrench)

对于第 $i$ 个接触点，施加的力 $f_i \in \mathbb{R}^3$ 在物体质心产生的旋量为：

$$w_i = \begin{bmatrix} f_i \\ r_i \times f_i \end{bmatrix} = \begin{bmatrix} I_{3 \times 3} \\ \hat{r}_i \end{bmatrix} f_i$$

其中 $\hat{r}_i$ 是 $r_i$ 的反对称矩阵（叉乘矩阵）。

#### 2.4.2 完整抓取矩阵 (Full Grasp Matrix)

将所有接触点的贡献组合，抓取矩阵 $G \in \mathbb{R}^{6 \times 3k}$（对于点接触）定义为：

$$G = \begin{bmatrix} I & I & \cdots & I \\ \hat{r}_1 & \hat{r}_2 & \cdots & \hat{r}_k \end{bmatrix}$$

合成旋量为：
$$w_{total} = G \cdot f = \sum_{i=1}^{k} w_i$$

其中 $f = [f_1^T, f_2^T, ..., f_k^T]^T \in \mathbb{R}^{3k}$ 是所有接触力的堆叠向量。

#### 2.4.3 Wrench Space 与抓取能力

**物理意义**：$G$ 的列空间 $\text{Range}(G)$ 表示通过当前接触配置能够施加的所有可能旋量的集合。如果 $\text{rank}(G) = 6$，则理论上可以施加任意方向的力和力矩（完全约束）。

**Null Space 的意义**：$G$ 的零空间 $\text{Null}(G)$ 对应于**内力 (Internal Forces)**——施加这些接触力不会改变物体的运动状态，但会影响抓取的稳定性（如挤压力）。

$$f_{internal} \in \text{Null}(G) \Rightarrow G \cdot f_{internal} = 0$$

### 2.5 力闭合与形闭合：抓取稳定性的数学条件 (Force & Form Closure)

> [!important] 核心概念
> **力闭合 (Force Closure)** 是灵巧抓取的核心数学条件：能够通过接触力抵抗任意方向的外扰动。

#### 2.5.1 形闭合 (Form Closure)

**定义**：物体在接触约束下**几何上完全固定**，即使没有摩擦也无法移动。

数学条件：
$$\text{rank}(G) = 6 \quad \text{且} \quad \text{Null}(G_{velocity}) = \{0\}$$

**物理意义**：物体被接触点的几何形状"锁死"。例如，将一个正方体卡在 V 形槽中。

**局限性**：纯形闭合在灵巧操作中很少使用，因为它依赖于精确的几何配合，缺乏灵活性。

#### 2.5.2 力闭合 (Force Closure)

**定义**：通过**摩擦约束内**的接触力，能够抵抗施加在物体上的**任意方向**的旋量。

数学条件（几何解释）：旋量空间的原点必须位于**可达旋量锥 (Wrench Cone)** 的内部。

$$0 \in \text{int}(\text{ConvexHull}(\mathcal{W}))$$

其中 $\mathcal{W} = \{w : w = G f, f \in \mathcal{FC}\}$，$\mathcal{FC}$ 是所有接触点的摩擦锥约束。

**等价条件 (Murray 定理 5.4)**：
设 $W_i$ 为第 $i$ 个接触点的 primitive wrench（单位接触力产生的旋量），则力闭合当且仅当：
$$\nexists \lambda \neq 0 : \lambda^T W_i \geq 0, \forall i \quad \text{(No common half-space)}$$

> [!tip] 物理直觉
> **力闭合就像"手指把物体团团围住"**：无论外力从哪个方向来，总有某些手指能够推回去。如果所有手指的力都只能指向某个半空间，那么反方向的扰动将无法抵抗。

#### 2.5.3 力闭合的充分条件：最小接触点数

> [!note] 教科书参考
> 本节基于 Murray, Li & Sastry 《A Mathematical Introduction to Robotic Manipulation》Chapter 5, Section 3-4。

**关键定理（凸分析）**：

**Caratheodory 定理**：若向量集 $X = \{v_1, ..., v_k\}$ 正生成 (positively span) $\mathbb{R}^p$，则 $k \geq p + 1$。

**Steinitz 定理**：若 $S \subset \mathbb{R}^p$ 且 $q \in \text{int}(\text{co}(S))$，则存在 $X = \{v_1, ..., v_k\} \subset S$ 使得 $q \in \text{int}(\text{co}(X))$ 且 $k \leq 2p$。

**应用到抓取**：
- **下界 (Caratheodory)**：力闭合抓取至少需要 $p + 1$ 个接触点
- **上界 (Steinitz)**：对于非例外曲面，至多需要 $2p$ 个接触点即可实现力闭合

| 接触模型 | 2D 最小接触点 | 3D 最小接触点 |
|---------|--------------|--------------|
| **无摩擦点接触** | 4 | 7 |
| **有摩擦点接触** | 2 | 3 |
| **软指接触** | 2 | 2 |

**例外曲面 (Exceptional Surface)**：若物体表面 $\Sigma$ 的可达旋量集 $\Lambda(\Sigma)$ 的凸包不包含原点的邻域，则该物体**永远无法**用无摩擦点接触实现力闭合。典型例子：球体（所有法向量通过球心）。

**洞察**：软指模型的优势在于更少的接触点就能实现力闭合，这对于高自由度灵巧手至关重要——更少的接触点意味着更简单的协调控制。

### 2.6 抓取品质度量 (Grasp Quality Metrics)

评估一个抓取"有多好"需要量化指标。以下是最常用的度量体系。

#### 2.6.1 Ferrari-Canny Q1 Metric (Largest Inscribed Ball)

**定义**：在归一化的旋量空间中，可达旋量集合（Wrench Set）内接最大球的半径。

$$Q_1 = \max_r \{ r : B(0, r) \subseteq \mathcal{W} \}$$

**物理意义**：能够抵抗的最大**均匀**外扰动。$Q_1 > 0$ 等价于力闭合。

**计算方法**：转化为线性规划 (LP) 或二阶锥规划 (SOCP)。

#### 2.6.2 Grasp Wrench Space Volume

**定义**：可达旋量集合的体积（或超体积）。

$$Q_2 = \text{Volume}(\mathcal{W})$$

**特点**：考虑了各向异性——某些方向可能能施加更大的力。

#### 2.6.3 Minimum Singular Value of G

**定义**：抓取矩阵的最小奇异值。

$$Q_3 = \sigma_{\min}(G)$$

**物理意义**：抓取配置的"病态程度"。$\sigma_{\min}$ 越大，力从接触空间到旋量空间的传递越有效率。

> [!note] 工程选择
> 在实际的抓取规划中，通常使用 **Ferrari-Canny Q1** 作为主要指标，因为它直接对应于鲁棒性，且计算相对高效。

------

## 3. 接触建模演变：从点模型到软体模型

物理仿真和控制策略的有效性，极其依赖于对物理接触界面的数学抽象。

### 3.1 理想点接触与硬指模型 (Hard Finger)

这是刚体动力学中最基础的模型，假设接触发生在一个无面积的几何点上。

- **无摩擦点接触 (Frictionless Point Contact)**：仅能沿法线方向施加推力 $f_n \ge 0$。切向力为零。这种模型仅用于理论上的形式闭合（Form Closure）分析，实际应用极少 。

- **有摩擦点接触 (Point Contact with Friction / Hard Finger)**：除了法向力，还允许施加切向摩擦力 $f_t$。其约束条件遵循库伦摩擦定律：

  $$||f_t|| \le \mu f_n$$

  这一约束在几何上定义了一个**摩擦锥 (Friction Cone)**。在硬指模型中，接触点不能传递任何力矩。这意味着手指就像一个球铰链，物体可以绕接触点自由转动，除非被多个手指约束 。

### 3.2 软指接触模型 (Soft Finger Contact)

在真实的灵巧操作中，指尖通常覆盖有橡胶或硅胶等软材料。在受压时，接触点会扩展为一个接触斑（Contact Patch）。

- **扭转摩擦 (Torsional Friction)**：由于接触斑的存在，手指不仅能施加切向力，还能施加绕法线的扭转力矩 $\tau_n$。经典模型（如Murray & Sastry所述）通常假设切向摩擦和扭转摩擦是解耦的，或者遵循一个椭球形的极限曲面 ：

  $$\frac{f_t^2}{\mu^2} + \frac{\tau_n^2}{\gamma^2} \le f_n^2$$

  其中 $\gamma$ 是扭转摩擦系数。这种能力对于单指转动开关或调整物体姿态至关重要。

### 3.3 超越Hertz理论：大变形与软体抓取

当涉及软体机器人（Soft Robotics）或大变形指尖时，经典的Hertz接触理论面临失效。Hertz理论建立在小应变和线性弹性的假设之上，预测接触半径 $a \propto F^{1/3}$。

- **大变形下的非线性**：对于软指抓取，当压缩量较大时，材料的超弹性（Hyperelasticity）和几何非线性（如指尖软层的厚度效应）会导致接触刚度急剧增加（Hardening），偏离Hertz预测。研究表明，在大变形下（压缩量达50%），接触力和接触半径遵循基于降维法（Method of Dimensionality Reduction, MDR）推导出的特定缩放定律，这对于精确控制软抓手至关重要 。
- **有限元 (FEM) 与代理模型**：为了获得真实的接触应力分布，有限元方法（FEM）是金标准，但其计算成本极高（非实时）。在机器人控制中，常采用**多点代理模型 (Multipoint Proxy)** 或 **顺应性连接模型**。例如，将软指尖建模为一组通过弹簧连接的刚性微球，这样既能利用快速的刚体求解器，又能模拟出接触斑的抗扭特性 。

| **模型类型**     | **自由度约束**     | **力矩传递** | **适用场景**            | **计算复杂度** |
| ---------------- | ------------------ | ------------ | ----------------------- | -------------- |
| **无摩擦点接触** | 1 (法向)           | 无           | 形式闭合分析            | 极低           |
| **硬指接触**     | 3 (法向+切向)      | 无           | 金属/硬塑接触，精密装配 | 低             |
| **软指接触**     | 4 (法向+切向+扭转) | 有 (法向轴)  | 橡胶指尖，手内操作      | 中             |
| **有限元/多点**  | 6+ (分布力)        | 有 (任意轴)  | 软体机器人，大变形抓取  | 高             |

------

## 4. 计算动力学与求解器：从LCP到凸优化

掌握了运动学和接触模型后，核心挑战在于：**给定当前的接触状态和外力，如何计算出下一时刻的系统状态？** 这就是约束求解器（Constraint Solver）的任务。

### 4.1 线性互补问题 (LCP) 的构建

对于刚体接触，非穿透约束（Non-penetration）本质上是一个互补条件：

1. 间距 $d \ge 0$（不能穿透）。
2. 法向力 $f_n \ge 0$（只能推不能拉）。
3. $d \cdot f_n = 0$（若分离则无力，若受力则接触）。

结合离散化的动力学方程（如牛顿-欧拉方程），这一问题可以被转化为标准的**线性互补问题 (Linear Complementarity Problem, LCP)**。

#### 4.1.1 Stewart-Trinkle 时间步进算法

早期的动力学仿真常在加速度层面上求解，容易导致Painlevé悖论（即解不存在或不唯一）。Stewart和Trinkle在1996年提出了一种基于速度-冲量（Velocity-Impulse）层面的时间步进算法，彻底解决了存在性问题。该算法与 [[Dynamics#4.1 空间向量代数 (Spatial Vector Algebra) 基础|空间向量代数]] 中的空间向量表示紧密配合。

在Stewart-Trinkle公式中，系统状态更新被写作：

$$M(v^{t+1} - v^t) = h(f_{ext} + J_n^T \lambda_n + J_t^T \lambda_t)$$

其中 $h$ 是时间步长，$\lambda$ 是约束冲量。这被重写为 LCP 标准形式：

$$w = A z + q$$

$$0 \le w \perp z \ge 0$$

矩阵 $A$（Delassus矩阵）反映了系统在接触点的有效逆质量。

#### 4.1.2 摩擦锥的多面体线性化

标准的库伦摩擦锥 $\sqrt{f_x^2 + f_y^2} \le \mu f_n$ 是二阶锥（非线性）。为了将其纳入**线性**互补问题，必须将其近似为多面体（Polyhedron）。通常使用四棱锥或八棱锥来内接或外切于圆锥。

- **影响**：这种线性化引入了**各向异性**。物体在沿着棱锥边缘方向滑动的阻力与沿着面方向滑动的阻力不同。这也是为什么在某些物理引擎中，物体旋转时会表现出轻微的“卡顿” 。

### 4.2 直接求解器与迭代求解器

求解上述 $w=Az+q$ 的算法主要分为两类。

#### 4.2.1 直接法：Lemke算法

Lemke算法是一种类似于线性规划中单纯形法（Simplex Method）的枢轴算法（Pivoting Algorithm）。它通过在基变量之间进行交换，寻找满足互补条件的解 。

- **优点**：如果存在解，它能找到精确解（在机器精度范围内）。对于高精度的机器人抓取稳定性分析，这是首选。
- **缺点**：在最坏情况下，时间复杂度是指数级的。虽然在实际物理模拟中很少遇到，但在处理大量接触（如一堆沙砾）时，计算量会急剧上升且难以并行化。

#### 4.2.2 迭代法：投影高斯-赛德尔 (PGS) 与 顺序冲量 (SI)

这是现代游戏物理引擎（如Bullet, Box2D, PhysX）和部分机器人仿真器（如PyBullet, Dart）的主流选择。Box2D的作者Erin Catto提出的**顺序冲量 (Sequential Impulses, SI)** 方法在数学上等价于对对偶问题应用投影高斯-赛德尔迭代 。

**SI算法逻辑**：

1. **预计算**：施加重力等外力，得到预测速度 $v^*$。
2. **热启动 (Warm Starting)**：利用上一帧计算出的冲量 $\lambda^{t-1}$ 作为初值应用到当前帧。这利用了物理系统的时间相干性，极大地减少了收敛所需的迭代次数（对于堆叠物体，从几百次减少到几十次）。
3. **迭代循环**：
   - 对每个接触点，计算消除穿透所需的法向冲量 $\Delta \lambda_n$。
   - 更新累计冲量 $\lambda_n \leftarrow \lambda_n + \Delta \lambda_n$，并投影到 $\ge 0$。
   - 计算消除滑动所需的切向冲量 $\Delta \lambda_t$。
   - 更新累计切向冲量，并投影到摩擦锥 $| \lambda_t | \le \mu \lambda_n$ 内（Box Clamping）。
   - 将冲量变化应用到刚体速度上。
4. **重复**：直到满足收敛标准或达到最大迭代次数。

- **特点**：$O(N)$ 线性复杂度，极易实现，且天然处理过约束系统（Over-constrained systems）。缺点是解是近似的，接触表现出一种非物理的“软度”（Compliance），其刚度与迭代次数和时间步长有关。

### 4.3 凸优化方法：MuJoCo范式

MuJoCo (Multi-Joint dynamics with Contact) 采用了一种完全不同的路径。Emanuel Todorov指出，如果我们允许约束有微小的变形（即软约束），接触动力学问题可以被建模为一个**凸优化 (Convex Optimization)** 问题，具体是一个二次规划（QP）问题 。

MuJoCo通过定义接触势能函数，将非穿透的硬约束转化为罚函数形式。由于问题是凸的：

1. 保证了全局最优解的唯一性。
2. 可以使用牛顿法（Newton Method）或共轭梯度法（CG）进行求解。牛顿法具有二阶收敛速度，比PGS的一阶收敛快得多，因此MuJoCo在处理复杂机器人（如类人机器人）时极其高效且稳定。
3. **逆动力学 (Inverse Dynamics)**：由于约束是软的且通过凸优化求解，MuJoCo在数学上定义良好的逆动力学，即使在有接触的情况下也能解析地计算控制力矩，这对于基于模型的控制（Model-Based Control）是巨大的优势。

### 4.4 基于位置的动力学 (XPBD)

XPBD (Extended Position Based Dynamics) 跳过了速度层面的求解，直接在位置层面投影约束。

- **稳定性**：对于软体、布料、绳索以及机器人的柔性抓手，XPBD具有无与伦比的稳定性。它不会因为速度层面的数值误差积累而导致系统“爆炸”。
- **物理意义**：传统的PBD刚度依赖于时间步长，而XPBD引入了顺应性参数 $\alpha = 1 / (k \cdot h^2)$，使得模拟的材料刚度与迭代次数和时间步长解耦，从而具备了物理真实性 。

------

## 5. 可微接触物理：梯度的奥秘

在强化学习（RL）和轨迹优化中，如果物理引擎是**可微的**，我们就可以直接计算状态关于控制输入的梯度 $\partial s_{t+1} / \partial u_t$，从而使用高效的基于梯度的优化算法（如GD, L-BFGS）来替代低效的无梯度算法（如PPO, ES）。

### 5.1 梯度的不连续性挑战

接触物理本质上是不连续的。一个微小的动作改变可能导致接触发生或消失（Make or Break contact）。这种“非黑即白”的跳变导致梯度要么为零（无接触时），要么未定义（撞击瞬间）。

### 5.2 实现可微性的路径

#### 5.2.1 零阶技术：平滑化与随机化

这并不是真正的可微物理，但在Sim2Real中广泛使用。通过对物理参数（摩擦、质量）引入噪声，或者使用“软”接触模型（Spring-Damper），可以在期望值层面上平滑损失函数曲面，使得梯度方向变得有意义 。

#### 5.2.2 隐函数定理 (Implicit Function Theorem) 及其解析梯度

这是当前最前沿的方法（如DiffTaichi, Nimble, MuJoCo的解析梯度）。

与其尝试通过PGS求解器的数百次迭代进行反向传播（这会导致计算图过深、内存爆炸且梯度不稳定），不如直接对**求解结果**进行微分。

假设LCP求解器找到了解 $z^*$ 满足平衡方程 $R(z^*, \theta) = 0$（其中 $\theta$ 是物理参数）。根据隐函数定理：

$$\frac{\partial z^*}{\partial \theta} = - \left( \frac{\partial R}{\partial z} \right)^{-1} \frac{\partial R}{\partial \theta}$$

这意味着我们只需要在求解结束后，求解一个线性方程组，就能一次性得到解关于所有参数的梯度。这种方法不仅速度快，而且梯度精度与前向求解的迭代次数无关，具有极高的数值稳定性 。

#### 5.2.3 碰撞时间 (Time-of-Impact, TOI) 梯度

传统的固定时间步长仿真器无法捕捉“碰撞发生时刻”对参数的敏感度。如果改变一个参数导致碰撞提前了0.01秒，固定步长仿真器可能完全忽略这一变化。**TOI-Velocity** 方法通过连续碰撞检测（CCD）计算碰撞发生的精确时刻 $t_c$，并推导碰撞后速度关于 $t_c$ 的导数。这对于优化高速运动和精密操作轨迹至关重要，因为它填补了时间维度上的梯度信息 。

| **可微方法**                  | **原理**                 | **优点**             | **缺点**                  | **典型引擎**                |
| ----------------------------- | ------------------------ | -------------------- | ------------------------- | --------------------------- |
| **软化/平滑 (Smoothing)**     | 弹簧阻尼替代硬约束       | 易于实现，梯度连续   | 物理失真（穿透、振荡）    | Brax (早期), System ID      |
| **展开 (Unrolling)**          | 通过求解器迭代步反向传播 | 适用于任意可微操作   | 内存消耗大，梯度爆炸/消失 | DiffTaichi (部分案例)       |
| **解析梯度 (Analytical/IFT)** | 利用KKT条件/隐函数定理   | 极快，精度高，内存小 | 需推导特定模型的导数      | Nimble, MuJoCo (新版), Dojo |

------

## 6. 仿真到现实 (Sim2Real) 与工程实现

在构建知识库时，理论必须服务于现实。接触力学的Sim2Real鸿沟（Reality Gap）是阻碍灵巧操作落地的最大障碍。

### 6.1 域随机化 (Domain Randomization) 的接触策略

仅仅随机化摩擦系数是不够的。为了实现鲁棒的灵巧操作，必须对接触动力学的多个维度进行随机化 ：

1. **摩擦系数 ($\mu$)**：不仅是数值大小，还应包括滚动摩擦和扭转摩擦的系数。
2. **接触刚度与阻尼 (Stiffness/Damping)**：在MuJoCo中即 `solref` 和 `solimp` 参数。这模拟了物体表面的软硬程度变化。
3. **延迟 (Latency)**：从接触发生到力传感器读数，以及从指令下达到力矩生效的时间差。
4. **接触几何**：对碰撞体（Collision Mesh）进行微小的顶点扰动，或者使用“凸分解”时的不同近似精度，以模拟真实物体的几何误差。

**部分渐进式随机化 (Curriculum Randomization)**：研究表明，从确定的物理环境开始，随着策略的学习逐渐增加随机化幅度，比一开始就进行大幅度全域随机化收敛效果更好 。

### 6.2 在线系统辨识 (Online System Identification)

利用可微物理引擎的优势，机器人可以在与物体交互的过程中（比如手指轻轻滑动物体表面），实时利用观测数据计算摩擦系数的梯度 $\nabla_\mu \text{Loss}$，并在线更新物理参数。这使得机器人能够像人类一样，通过“试探”来适应未知的接触特性，实现自适应控制 。

------

## 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及接触力学的核心主题

### 手内操作与接触建模
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] — 重力无关旋转
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] — 纯触觉旋转
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] — 视触觉联觉
- [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] — 手指步态

### 接触丰富的学习
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 物理驱动数据生成
- [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation]] — 残差 DMP
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 接触丰富任务的阻抗控制

### 触觉感知与抓取
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] — 视触觉遥操作
- [[Proximity Perception-Based Grasping Intelligence (P2GI)]] — 近距离感知抓取
- [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] — 触觉反馈与课程学习
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] — 穿透深度作为域不变触觉表征，zero-shot sim-to-real

### 接触丰富的非抓取操作
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 杂乱场景中选择性利用环境接触的 extrinsic dexterity

### 视触觉策略生成
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]]: **接触 grounding 扩散策略**，耦合状态-触觉扩散 + 接触一致性映射
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]: **穿透深度图**作为统一触觉 sim-to-real 表征

### 柔顺控制与力学建模
- [[Minimalist Compliance Control|MCC]]: **无传感器柔顺控制**，利用电机电流估计接触力，方向相关效率模型

------

## 7. 结论与建议

接触力学是机器人灵巧操作的基石。从Montana方程揭示的几何演化规律，到MuJoCo和XPBD提供的强大计算工具，再到可微物理开启的学习新范式，这一领域正在经历深刻的变革。

针对您的Obsidian知识库构建，我们提出以下核心建议：

1. **分层架构**：将知识库分为“几何原理”、“物理建模”、“求解算法”和“学习应用”四个层级。Montana方程属于几何原理，LCP属于求解算法。
2. **关注软体趋势**：随着软体抓手的普及，应重点收录关于**超弹性接触**和**XPBD**的内容，因为刚体LCP模型在处理软接触时存在局限性。
3. **算法实现的二元性**：在记录求解器时，明确区分**高精度仿真**（倾向于Lemke/Newton）与**实时游戏/RL环境**（倾向于PGS/SI）的区别。前者追求真理，后者追求速度和稳定性。
4. **可微物理的前瞻性**：重点关注**隐函数定理**在接触梯度计算中的应用，这是连接传统力学与现代深度学习的桥梁。

通过深入理解并结构化这些知识，您将构建出一个不仅包含公式，更包含物理洞察与工程智慧的顶级机器人学知识库。