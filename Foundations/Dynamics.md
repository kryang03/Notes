---
tags:
  - foundation
  - dynamics
  - dexterous-manipulation
  - multibody
aliases:
  - 动力学
  - 多体动力学
  - RNEA
  - ABA
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[Actuation]]"
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
  - "[[StochasticProcess]]"
  - "[[ReinforcementLearning]]"
  - "[[WorldModels]]"
---

# 灵巧操作动力学：从能量原理到实时多体与接触求解

# Dexterous Manipulation Dynamics: From Energy Principles to Real-Time Multibody & Contact Solving

> [!tip] 相关领域
> - [[ControlTheory]] — 动力学方程是控制律的设计对象；操作空间动力学是阻抗控制的根
> - [[Actuation]] — 操作器方程右端的 $\tau$ 不是凭空施加的，而是电机+FOC+减速器的输出；腱耦合矩阵 $P$（§8）与传动雅可比同源，神经动力学（§9）与 actuator net 同思想
> - [[ContactMechanics]] — 接触动力学（LCP）是动力学与接触力学的交汇；Delassus 矩阵两处共用
> - [[Optimization]] — iLQR/DDP/MPC 依赖高效动力学求解；变分积分器与最优控制同源
> - [[StochasticProcess]] — GP/ensemble 动力学学习补偿模型残差
> - [[ReinforcementLearning]] — 动力学模型即 Model-Based RL 的世界模型；ABA 是仿真器内核
>
> **贯穿母题**：**灵巧手握持并挥转一支偏心（配重偏心）螺丝刀，最后让刀头精确停在螺钉上**。这一个动作把动力学六层大厦全部点亮：挥动→多体递推与科氏力；握持→闭链有效惯量与内力；对准→操作空间控制；触到螺钉→接触动力学；腱驱动的手→腱网络动力学；真机偏差→可微物理。

## 0. 母题与理论大厦构建路线：从能量原理到实时多体求解

> [!abstract] 为什么用"挥转偏心螺丝刀"做母题？
> 一支配重偏心的螺丝刀是动力学最好的"教具"：
> - 偏心质量让**科氏力/离心力**在快速挥动时显著到肉眼可见（刀头会"甩偏"）；
> - 它的位姿活在 **SE(3)** 上，挥动轨迹是构型流形上的曲线；
> - 要 1kHz 算出"该给每个关节多大力矩"，必须用 **RNEA**；要在仿真里挥它，必须用 **ABA**；
> - 手一握紧，系统从开链变**闭链**，物体的**有效惯量**突变、还要控**内力**别让它脱手；
> - 刀头触到螺钉，进入**接触动力学**（LCP）；
> - 想让仿真里的螺丝刀和真机一样甩，需要**可微物理 / 神经动力学**辨识它的真实惯量。
>
> 全讲每引入一个概念，都回到这支螺丝刀：**"挥它时哪一项力在作怪？握它时惯量变了多少？仿真为什么甩得不对？"**

动力学 Foundation 的主线，要从"$F=ma$"逐级升级为"**约束流形上的能量、动量、接触冲量，以及让它们能实时计算的递推算法**"。六层大厦，每层回答一个更尖锐的问题：

| 层级 | 关键问题 | 理论对象 | 螺丝刀母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **几何层** | 构型如何表示？ | SE(3)、广义坐标、指数坐标 | 螺丝刀位姿、手的构型流形 | §2 |
| **能量层** | 方程从哪来？ | Lagrangian、Hamilton 原理、质量矩阵 | 惯量、科氏力、重力为何长这样 | §3 |
| **约束层** | 接触/闭链如何进入？ | Lagrange 乘子、Pfaffian、KKT | 接触力不是补丁，是约束反力 | §4 |
| **算法层** | 如何实时计算？ | RNEA、ABA、空间向量代数 | 让高 DoF 手在 kHz 闭环求解 | §5 |
| **仿真层** | 接触如何数值稳定？ | LCP、PGS、soft constraint、隐式积分 | 决定策略学到真物理还是仿真伪影 | §6 |
| **适配层** | 真机差异如何补偿？ | actuator model、神经动力学、system ID | 把刚体理论与传动/CAN/温漂分开建模 | §7–§9 |

> [!important] 阅读标准
> 本文每个动力学概念都要能回答三件事：**它从哪条物理原理推出来、在数值算法中如何计算、在灵巧操作失败模式里对应什么现象**。

> [!note] 本讲在知识图谱中的位置
> ```
> 【几何层 SE(3)】──指数坐标──> [[ControlTheory|手雅可比]] / [[ContactMechanics|Montana]]
>        │
> 【能量层 Lagrangian】──线性参数化──> [[ControlTheory|自适应控制]]；──Hamilton──> [[Optimization|最优控制/Pontryagin]]
>        │
> 【约束层 Lagrange 乘子】──Delassus──> [[ContactMechanics|LCP]]
>        │
> 【算法层 ABA】──仿真内核──> [[ReinforcementLearning|世界模型/Sim-to-Real]] / [[EmbodiedAI|仿真器]]
>        │
> 【适配层 可微物理】──解析梯度──> [[Optimization|System ID]] / [[StochasticProcess|GP 残差]]
> ```

## 1. 序言：动力学——灵巧操作的"暗物质"

> [!tip] 本节四拍
> **直觉**（动力学看不见，却主宰一切物理交互）→ **推导**（FD 与 ID 两个核心映射）→ **对比**（把物理引擎当黑盒为何危险）→ **落点**（六层大厦的任务）。

感知让系统"看见"、规划给出"决策"，但唯有**动力学**才是连接数字世界与物理实体的桥。对一只 20+ DoF 的灵巧手（Shadow/Allegro），动力学是限制性能的"暗物质"——看不见，却主宰从指尖微调到强力抓取的一切。我们要的两个核心映射：

1. **正向动力学 (FD)**：$\tau\to\ddot q$，给定力矩算加速度——**仿真**的基础（挥动螺丝刀时它怎么动）。
2. **逆向动力学 (ID)**：$q,\dot q,\ddot q\to\tau$，给定运动算力矩——**基于模型的控制**的基础（要让刀头走这条轨迹，每个关节该出多大力）。

> [!warning] 把物理引擎当黑盒，为何在灵巧操作中危险
> 通用物理引擎为通用性在接触求解器里做了大量妥协（soft constraint、摩擦锥线性化）。这些数学妥协在仿真里表现为"穿透/漂移"，在真机上对应的就是"**抓取失败/电机过热**"。灵巧操作的 mN 级力控误差、ms 级接触延迟都可能让螺丝刀脱手——所以必须打开黑盒，理解六层大厦每一层的取舍。

---

## 2. 几何层：构型流形与刚体变换

> [!tip] 本节四拍
> **直觉**（螺丝刀的位姿、手的构型都活在弯曲的流形上）→ **推导**（SO(3)/SE(3) 李群、Rodrigues、指数坐标）→ **对比**（指数坐标 PoE vs DH 参数）→ **联系**（twist↔[[ContactMechanics|Montana 旋量]]、空间向量↔§5 RNEA）。

### 2.1 构型空间流形与"质量矩阵即度量"

灵巧手的构型空间 (C-space) 是黎曼流形。**广义坐标** $q\in\mathbb R^n$ 是描述状态的最小变量集。**质量矩阵 $M(q)$ 定义了这个流形上的度量 (metric)**——它不只是"质量"，更是"系统在当前构型下沿不同方向运动的惯性阻力"。

> [!important] 母题里的惯量突变（贯穿 §7）
> 手指接触并握紧螺丝刀的**瞬间**，系统拓扑从**开链**变**闭链**，整个手+刀的有效质量矩阵的秩与特征值剧烈变化。理解这一点，是理解冲击 (impact) 动力学与 §7 有效惯量的钥匙——同一支螺丝刀，握前握后"挥起来的手感"完全不同。

### 2.2 旋转群 SO(3)、李代数 so(3) 与 Rodrigues 公式

旋转矩阵 $R\in SO(3)=\{R\in\mathbb R^{3\times3}:R^TR=I,\det R=+1\}$ 既是群又是光滑流形（李群）。其李代数 $so(3)=\{S:S^T=-S\}$ 是反对称矩阵集，与 $\mathbb R^3$ 一一对应：$\hat\omega v=\omega\times v$。

> [!theorem] Rodrigues 旋转公式
> 单位轴 $\omega$（$\|\omega\|=1$）转 $\theta$ 的旋转矩阵：
> $$R=e^{\hat\omega\theta}=I+\hat\omega\sin\theta+\hat\omega^2(1-\cos\theta).$$
> **证明思路**：从 $\dot q(t)=\omega\times q(t)$ 出发，用 $\hat\omega^3=-\|\omega\|^2\hat\omega$ 展开 Taylor 级数。

逆映射（对数）：$\theta=\cos^{-1}\frac{\mathrm{tr}(R)-1}{2}$，$\omega=\frac{1}{2\sin\theta}(r_{32}-r_{23},r_{13}-r_{31},r_{21}-r_{12})^T$。指数映射 $\exp:so(3)\to SO(3)$ 把"轴×角"直观参数化转成旋转矩阵，是轴角表示的数学根。

> [!abstract] 前沿应用：Neural Rodrigues Operator
> [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] 保留 Rodrigues 的 $1,\sin\theta,\cos\theta$ 基底，把机器人结构决定的固定系数放宽为可学习权重，将经典正运动学递推改造成动作网络中的结构化 message passing。

### 2.3 SE(3)、twist 与指数积公式 (PoE)

刚体运动 = 旋转 + 平移，由**特殊欧氏群** $SE(3)=\{g=\begin{bmatrix}R&p\\0&1\end{bmatrix}\}$ 统一描述。其李代数 $se(3)$ 由 **twist（旋量）** 组成：$\xi=(v,\omega)\in\mathbb R^6$。

为什么指数坐标对灵巧操作至关重要（四条）：
1. **运动学建模**：**指数积公式 (PoE)** $g_{st}(\theta)=e^{\hat\xi_1\theta_1}\cdots e^{\hat\xi_n\theta_n}g_{st}(0)$ 比 DH 参数更简洁、几何意义更清晰；
2. **雅可比计算**：空间/物体雅可比可直接由 twist 导出（见 [[ControlTheory#2.2 手雅可比 $J_h$：从关节到接触|手雅可比]]）；
3. **接触约束建模**：[[ContactMechanics#2.2 Montana 接触运动学方程|Montana 方程]]用相对旋量描述接触点演化——挥转螺丝刀时刀头在螺钉面上的接触演化正用这套语言；
4. **轨迹插值**：$SE(3)$ 上的测地线插值（SLERP 的 6D 推广）保证刚体运动的物理合理性。

> [!tip] 与空间向量代数的关系（伏笔 §5）
> Featherstone 的空间向量代数（§5.1）就是 $se(3)$ 的工程实现：空间速度 $\nu=(\omega,v)$ 对应 twist，空间惯量张量对应李代数上的度量。**记住这条对应，§5 的 6D 递推就不再神秘。**

---

## 3. 能量层：从 Hamilton 原理到操作器方程

> [!tip] 本节四拍
> **直觉**（挥动偏心螺丝刀时那股"甩偏"的力从哪来？）→ **推导**（Hamilton 最小作用量→Euler-Lagrange→操作器方程）→ **对比**（Lagrangian / Hamiltonian / Newton-Euler 三种等价形式）→ **联系**（线性参数化→[[ControlTheory|自适应控制]]，变分→[[Optimization|最优控制]]）。

### 3.1 操作器方程：$M(q)\ddot q+C(q,\dot q)\dot q+N(q)=\tau$

对 $n$ 连杆开链，总动能 $T=\frac12\dot\theta^TM(\theta)\dot\theta$（$M=\sum_iJ_i^TM_iJ_i$），势能 $V=\sum_im_igh_i$，Lagrangian $L=T-V$。代入 Lagrange 方程得**操作器方程**：

$$M(\theta)\ddot\theta+\underbrace{C(\theta,\dot\theta)\dot\theta}_{\text{科氏/离心}}+\underbrace{N(\theta)}_{\text{重力}}=\tau.$$

> [!theorem] Christoffel 符号：科氏项的来历
> $$C_{ij}=\sum_k\Gamma_{ijk}\dot\theta_k,\quad \Gamma_{ijk}=\tfrac12\Big(\tfrac{\partial M_{ij}}{\partial\theta_k}+\tfrac{\partial M_{ik}}{\partial\theta_j}-\tfrac{\partial M_{kj}}{\partial\theta_i}\Big).$$
> $\Gamma_{ijk}\dot\theta_j\dot\theta_k$ 中 $j=k$ 为**离心力**、$j\ne k$ 为**科氏力**。

> [!tip] 母题直觉：偏心螺丝刀为什么"甩偏"
> 偏心配重让 $M(\theta)$ **强烈依赖构型**——快速挥动时 $\dot M$ 大，科氏/离心项 $C\dot\theta$ 随之显著。若控制器（如计算力矩控制）忽略此项，刀头就跟不上期望轨迹、"甩偏"撞不上螺钉。工业机械臂低速时这项常被当干扰忽略，但灵巧手的**快速重构型 (in-hand)** 中它不可或缺。

### 3.2 变分起源：Hamilton 原理（为什么是 $L=T-V$）

操作器方程不是凭空写出，而是 **Hamilton 最小作用量原理**的推论。定义作用量 $S=\int_{t_0}^{t_1}L\,dt$。Hamilton 原理断言：端点固定下，真实轨迹使 $S$ 取驻值 $\delta S=0$。对 $\delta q$ 变分、分部积分，端点项消失，由 $\delta q$ 任意性即得 **Euler–Lagrange 方程** $\frac{d}{dt}\frac{\partial L}{\partial\dot q_i}-\frac{\partial L}{\partial q_i}=\Upsilon_i$。

> [!tip] 为什么变分形式重要（三条跨领域射线）
> 1. **统一框架**：同一个 Hamilton 原理推出场论、广义相对论、乃至 RL 的 path-integral；
> 2. **数值保结构**：变分积分器 (DMOC/RATTLE) 在离散积分中保辛结构、近似守恒能量，远优于 Forward Euler——MuJoCo 的隐式积分器即属此族（伏笔 §6）；
> 3. **最优控制桥梁**：Pontryagin 极小值原理本质是 Hamilton 原理在控制变分 $\delta u$ 上的推广，与 [[Optimization#6.1 iLQR/DDP：动态规划结构上的 Gauss-Newton|iLQR/DDP]] 共享变分根基。**力学与最优控制，同一个变分母体。**

### 3.3 反对称性与无源性：$\dot M-2C$ 的礼物

> [!important] $\dot M(\theta)-2C(\theta,\dot\theta)$ 是反对称的
> 这是 **Passivity-based Control** 的数学基础：取 Lyapunov 函数 $V=\frac12\dot\theta^TM\dot\theta$，有 $\dot V=\dot\theta^T(\tau-N)$（能量守恒结构）。它直接连到 [[ControlTheory#10. 稳定性理论的统一基石|无源性控制]]——挥转螺丝刀的能量注入/耗散可被精确记账，保证人-机-环境闭环稳定。

> [!theorem] 逐符号证明：为什么 $\dot M-2C$ 恰好反对称（不跳步）
> 记斜对称候选矩阵 $\Xi(\theta,\dot\theta):=\dot M-2C$，逐元素展开。三个已知事实：
> - $M$ **对称**：$M_{ij}=M_{ji}$（动能是二次型，Hessian 对称）；
> - $\dot M$ 的元素由链式法则：$\dot M_{ij}=\sum_k\dfrac{\partial M_{ij}}{\partial\theta_k}\dot\theta_k$（$\theta_k$ [rad]，$\dot\theta_k$ [rad/s]，$\dfrac{\partial M_{ij}}{\partial\theta_k}$ [kg·m²/rad]）；
> - $C$ 由 §3.1 的 Christoffel 定义：$C_{ij}=\sum_k\Gamma_{ijk}\dot\theta_k=\dfrac12\sum_k\Big(\dfrac{\partial M_{ij}}{\partial\theta_k}+\dfrac{\partial M_{ik}}{\partial\theta_j}-\dfrac{\partial M_{kj}}{\partial\theta_i}\Big)\dot\theta_k$。
>
> **第一步** 代入相减，把 $\dot M_{ij}$ 那一项和 $2C_{ij}$ 里第一项 $\partial M_{ij}/\partial\theta_k$ 抵消：
> $$\Xi_{ij}=\sum_k\dfrac{\partial M_{ij}}{\partial\theta_k}\dot\theta_k-\sum_k\Big(\dfrac{\partial M_{ij}}{\partial\theta_k}+\dfrac{\partial M_{ik}}{\partial\theta_j}-\dfrac{\partial M_{kj}}{\partial\theta_i}\Big)\dot\theta_k=\sum_k\Big(\dfrac{\partial M_{kj}}{\partial\theta_i}-\dfrac{\partial M_{ik}}{\partial\theta_j}\Big)\dot\theta_k.$$
> **第二步** 交换下标 $i\leftrightarrow j$ 得 $\Xi_{ji}=\sum_k\big(\partial M_{ki}/\partial\theta_j-\partial M_{jk}/\partial\theta_i\big)\dot\theta_k$。用 $M$ 对称（$M_{ki}=M_{ik}$、$M_{jk}=M_{kj}$）改写：
> $$\Xi_{ji}=\sum_k\Big(\dfrac{\partial M_{ik}}{\partial\theta_j}-\dfrac{\partial M_{kj}}{\partial\theta_i}\Big)\dot\theta_k=-\Xi_{ij}.\qquad\blacksquare$$
> **物理落点**：$\Xi^T=-\Xi\Rightarrow\dot\theta^T\Xi\dot\theta=0$ 对任意 $\dot\theta$ 成立——**科氏/离心力对系统不做净功，只在各自由度间"搬运"动能**。这才是"礼物"：挥转螺丝刀时，无论构型如何剧变，科氏项都不会凭空注入或抽走能量。

> [!note] 由反对称直接推出无源性（补全 $\dot V=\dot\theta^T(\tau-N)$ 那一步）
> $\dfrac{d}{dt}\big(\tfrac12\dot\theta^TM\dot\theta\big)=\dot\theta^TM\ddot\theta+\tfrac12\dot\theta^T\dot M\dot\theta$。代入操作器方程 $M\ddot\theta=\tau-N-C\dot\theta$：
> $$\dot V=\dot\theta^T(\tau-N)-\dot\theta^TC\dot\theta+\tfrac12\dot\theta^T\dot M\dot\theta=\dot\theta^T(\tau-N)+\tfrac12\dot\theta^T\underbrace{(\dot M-2C)}_{=\Xi,\ \text{斜对称}}\dot\theta=\dot\theta^T(\tau-N).$$
> 最后一项被反对称性精确抹掉——**能量的账只由输入 $\tau$ 与重力 $N$ 结算**。这是把 [[ControlTheory#10. 稳定性理论的统一基石|无源性/Lyapunov]] 用于人-机-环境闭环的前提，也与 [[ReinforcementLearning#8.2 奖励工程：最危险的自由度|能量型奖励塑形]]共享同一"能量记账"直觉。

### 3.4 惯量参数线性性：通往自适应控制的桥

> [!important] 操作器方程对惯量参数 $\pi$ 线性（Slotine–Li 1987）
> $$M(\theta)\ddot\theta+C\dot\theta+N=\mathbf Y(\theta,\dot\theta,\ddot\theta)\,\pi=\tau,$$
> 其中 regressor 矩阵 $\mathbf Y$ **只依赖运动学量、与参数 $\pi$ 无关**。原因：$T,V$ 对每个连杆的 10 个标准惯量参数仿射，Lagrange 是线性算子。

直接后果——**Slotine–Li 自适应律**：设误差 $e=\theta-\theta_d$、参考速度 $\dot\theta_r=\dot\theta_d-\Lambda e$、滑动变量 $s=\dot\theta-\dot\theta_r$，则
$$\tau=\mathbf Y\hat\pi-K_Ds,\qquad \dot{\hat\pi}=-\Gamma\,\mathbf Y^Ts.$$
用 $\dot M-2C$ 反对称 + Lyapunov $V=\frac12s^TMs+\frac12\tilde\pi^T\Gamma^{-1}\tilde\pi$ 可证 $s\to0$（详见 [[ControlTheory#12. 自适应控制与确定性等价|ControlTheory §12]]）。

> [!tip] 母题里的 System ID
> 把 1 秒挥动螺丝刀的真机轨迹送入最小二乘 $\hat\pi=(\mathbf Y^T\mathbf Y)^{-1}\mathbf Y^T\tau_{meas}$，就能在线辨识这支偏心螺丝刀（连同手）的全部惯量参数（前提：轨迹满足**持续激励 PE** 条件）。这也给 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|域随机化]]提供了理论替代——不必盲目随机化所有惯量，只需保证 $\mathbf Y$ 在训练分布上行满秩。

### 3.5 Hamiltonian 形式与三种等价视角

Legendre 变换给出广义动量 $p=M\dot q$ 与 Hamiltonian $H=\frac12p^TM^{-1}p+V=T+V$，正则方程 $\dot q=M^{-1}p,\ \dot p=-\partial H/\partial q+\tau$。换到 Hamiltonian 的三个理由：相空间辛几何（symplectic integrator 长期保能量）、Pontryagin（最优控制 Hamiltonian 同构、LQR 的 Riccati 由 $\partial H^*/\partial u=0$ 推出，见 [[ControlTheory#11. 线性二次最优控制 (LQR)|LQR]]）、energy-shaping（IDA-PBC 保无源）。

> [!important] 三种形式，一套物理（记忆锚点）
> | 形式 | 状态 | 适用场景 |
> |:--|:--|:--|
> | **Lagrangian** $(q,\dot q)$ | 配置+速度 | 推导、Sim-to-Real（变量易测） |
> | **Hamiltonian** $(q,p)$ | 配置+动量 | 长期仿真（辛积分）、最优控制 |
> | **Newton–Euler (spatial)** $(\nu,f)$ | 6D 旋量 | 实时计算（RNEA $O(N)$，§5） |
>
> 现代引擎（MuJoCo/Drake）的隐式积分器实际在 Hamiltonian 上做隐式中点法以保结构稳定。

### 3.6 小振动线性化：平衡点附近为何会"震"

平衡点只意味着一阶广义力为零（$\partial V/\partial q=0$），不意味着没有惯性。设扰动 $\eta=q-q_0$，二阶展开 $T\approx\frac12\dot\eta^TM_0\dot\eta$、$V\approx V(q_0)+\frac12\eta^TK_0\eta$（$K_0=\partial^2V/\partial q^2|_{q_0}$），得线性振动 $M_0\ddot\eta+K_0\eta=0$，固有频率由广义特征值 $K_0\phi_i=\omega_i^2M_0\phi_i$ 给出（单自由度退化为 $\omega_n=\sqrt{k/m}$）。

> [!important] 灵巧操作解读：刚度悖论的动力学版
> 刀头触到螺钉后的微小振动不是"噪声"，而是局部质量阵与接触/传动刚度共同决定的模态响应。高 $K_p$ 位置控制等价于增大 $K_0$、抬高自然频率，更易激发未建模柔性——这正是 [[ControlTheory#3.1 刚度悖论与计算力矩控制的诱惑|刚度悖论]]的动力学根源。

---

## 4. 约束层：接触与闭链如何进入动力学

> [!tip] 本节四拍
> **直觉**（手握紧螺丝刀=新约束，刀头触螺钉=新约束——约束力不是外加补丁）→ **推导**（Pfaffian→Lagrange 乘子→KKT 系统）→ **对比**（完整 vs 非完整；坐标降维 vs 乘子）→ **联系**（KKT 矩阵的 Delassus 算子↔[[ContactMechanics|LCP]]）。

### 4.1 Pfaffian 约束与完整/非完整之分

> [!note] 教科书参考
> 本节基于 Murray et al. Ch. 6。

一般速度约束写成 **Pfaffian 形式** $A(q)\dot q=0$（$A\in\mathbb R^{k\times n}$）。对多指手，约束矩阵有特殊结构 $A(q)=[\,J_h(q)\ \ -G^T(q)\,]$（$J_h$ 手雅可比、$G$ 抓取矩阵——又见 [[ContactMechanics#2.3 接触雅可比与对偶性：连接关节空间|对偶性]]）。

**可积性判别完整/非完整**：若存在 $h(q)$ 使 $A\dot q=0\Leftrightarrow\frac{\partial h}{\partial q}\dot q=0$，则约束**可积**、等价于完整约束 $h(q)=0$；**不可积的 Pfaffian 约束就是非完整约束**。

> [!tip] 母题里的非完整：滚动 = "平行泊车"
> 刀头或指尖在物体表面**纯滚动**（rolling without slipping）是非完整约束的典型——它限制瞬时速度方向却不降低 C-space 维数。后果：你不能让接触点"侧向平移"，必须靠一串滚动机动来重定位（**finger gaiting**），就像平行泊车。这把动力学与 [[ContactMechanics#2.2 Montana 接触运动学方程|Montana 滚动]]、[[ControlTheory#6. 接触非线性：Montana 接触运动学|非完整控制]]缝在一起。

### 4.2 约束动力学：Lagrange 乘子与约束反力

受 Pfaffian 约束的系统，运动方程加一项约束反力：
$$M(q)\ddot q+C\dot q+N+A^T(q)\lambda=F,$$
$\lambda\in\mathbb R^k$ 是 **Lagrange 乘子**。对约束求时间导数代入，解出
$$\lambda=(AM^{-1}A^T)^{-1}\big[AM^{-1}(F-C\dot q-N)+\dot A\dot q\big].$$

> [!theorem] 逐步推导（1）为什么反力是 $A^T\lambda$ 而非 $A\lambda$
> **虚功原理 / d'Alembert**：理想约束力对任何**可行速度**不做功。可行速度满足 $A\dot q=0$，即 $\dot q\in\ker A$（约束把速度锁在这个 $n-k$ 维零空间里）。对 $\ker A$ 处处零功的广义力，必落在其正交补 $(\ker A)^\perp=\mathrm{row}(A)=\mathrm{range}(A^T)$——> 所以约束力**只能**写成 $A^T\lambda$。每个 $\lambda_l$ 是第 $l$ 条约束的反力**大小**（法向接触约束 $\Rightarrow$ 力 [N]；姿态约束 $\Rightarrow$ 力矩 [N·m]），方向由 $A$ 的第 $l$ 行给定。
> **优化视角——$\lambda$ 就是 KKT 乘子/影子价格**：把约束动力学写成"每步求 $\ddot q$ 使加速度能量最小、s.t. $A\ddot q=-\dot A\dot q$"的等式约束 QP，其一阶最优性 (KKT) 恰好给出 $M\ddot q-A^T\lambda=\tau-C\dot q-N$——**力学里的"约束反力"与优化里的"拉格朗日乘子"是同一个 $\lambda$**。$\lambda_l$ 作为**影子价格**的读法：把第 $l$ 条约束松动一个单位（允许 $\phi_l$ 违反 $\delta$），系统的广义力代价随之变化的斜率就是 $\lambda_l$——约束"越顶得紧"、影子价格越高。这把动力学接上了 [[Optimization#2.3 KKT 条件：约束最优的"语法"|KKT 条件]]（"价值即 Lyapunov / 对偶即价格"的优化侧语法）。
> **这正是"对偶性 $J/G/P$"暗线的根**：$G^Tf$（抓取内力）、$J_h^T f_c$（接触力→关节力矩）、$P^Tf$（腱张力→关节力矩）与 $A^T\lambda$ 是**同一个虚功论证**的四个化身，见 [[ControlTheory#2.1 虚功原理与对偶性|虚功原理与对偶性]]、[[ContactMechanics#2.3 接触雅可比与对偶性：连接关节空间|接触雅可比对偶]]。

> [!theorem] 逐步推导（2）$\lambda$ 与 Delassus 算子 $AM^{-1}A^T$ 从哪来
> **加速度层约束**：位置约束 $A\dot q=0$ 只约束速度，求解 $\ddot q$ 需再微分一次。对 $A(q)\dot q=0$ 求时间导（$A$ 依赖 $q$，故有 $\dot A$ 项）：
> $$\frac{d}{dt}(A\dot q)=\dot A\dot q+A\ddot q=0\ \Rightarrow\ A\ddot q=-\dot A\dot q.\tag{$\star$}$$
> **从 EOM 解出 $\ddot q$**：$\ddot q=M^{-1}\big(F-C\dot q-N-A^T\lambda\big)$。代入 ($\star$)：
> $$AM^{-1}\big(F-C\dot q-N\big)-\underbrace{AM^{-1}A^T}_{\text{Delassus }\mathcal D}\,\lambda=-\dot A\dot q.$$
> 移项即得上式的 $\lambda$。**逐符号读 $\mathcal D=AM^{-1}A^T$**：$M^{-1}$ 是关节空间的**柔度**（力→加速度，单位 $1/(\text{kg·m}^2)$）；$A^T$ 把约束乘子"撑"进关节空间；$A$ 再把关节加速度"压"回约束空间。合起来 $\mathcal D$ 是**"在约束方向上，单位反力产生多少约束加速度"**——即约束点的**有效逆惯量**（$\mathcal D^{-1}$ 才是有效惯量 [kg·m²]）。$\mathcal D$ 病态（$A$ 行接近相关，如冗余抓取过约束）时 $\lambda$ 数值爆炸，这正是 §6.1 PGS 收敛慢、幽灵力的根。

> [!important] 一处推导，三个领域共用（Delassus 主线 + 接触非光滑暗线）
> - **$\mathcal D=AM^{-1}A^T$ 就是 §7.3 Khatib 操作空间惯量 $\Lambda^{-1}=JM^{-1}J^T$ 的同一构造**（把约束雅可比 $A$ 换成任务雅可比 $J$）——约束反力与任务惯量是**同一套数学**，见下文 §7.3 推导。
> - 把 ($\star$) 的**等式**换成**互补不等式** $\lambda\ge0,\ (A\ddot q+\dot A\dot q)\ge0,\ \lambda^\top(\cdot)=0$（接触只推不拉），KKT 系统就退化为 [[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]]，$\mathcal D$ 即 LCP 的主矩阵——**接触把光滑等式约束撕成非光滑互补**，这是 [[Optimization#3.1 互补约束：接触把可行域撕成"坐标轴的并集"|优化景观被接触毁掉]]的动力学来源。
> - $\mathcal D$ 也是 [[Optimization#2.3 KKT 条件：约束最优的"语法"|KKT 条件]]里约束块的 Schur 补——约束动力学本质是一个每步都在解的等式约束 QP。

> [!important] 三层物理含义
> - **$AM^{-1}A^T$ = 约束空间的有效质量矩阵**（即 §5 要分解的 **Delassus 算子**，也即 [[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]] 里的 $A$ 矩阵——一处推导，两个领域共用）；
> - **$\lambda$ = 接触力/内力的大小**；
> - **d'Alembert 原则**：约束力不做功 $\lambda^TA\dot q=0$。
>
> 抓取控制常需**同时控位置与力**——沿约束面移动（位置控制）的同时调法向力（力控制），这正是 [[ControlTheory#5. 力/位混合控制：正交分解任务空间|混合位置/力控制]]的数学基础。

### 4.3 约束 Lagrangian：闭链与接触的统一处理

存在 $k$ 个 holonomic 约束 $\phi(q)=0$（如双指捏合成闭链、握住螺丝刀的固定接触）时，两条等价路径：

- **路径 A — 坐标降维 (embedding)**：求 $n-k$ 个独立坐标使 $\phi$ 自动成立。代价：接触点随时变的灵巧操作里，实时重定义坐标极难。
- **路径 B — Lagrange 乘子 (DAE)**：保留全坐标，引入乘子，合并成 **index-3 微分代数方程**，对约束二次微分后得 **KKT 系统**：
$$\begin{bmatrix}M & -A^T\\ A & 0\end{bmatrix}\begin{bmatrix}\ddot q\\ \lambda\end{bmatrix}=\begin{bmatrix}\tau-C\dot q-N\\ -\dot A\dot q\end{bmatrix}.$$

约束反力 $f_c=A^T\lambda$。对接触约束，$\lambda$ 即法向力大小；与 [[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]]的互补条件 $\lambda\ge0,\ \phi(q)\ge0,\ \lambda\cdot\phi=0$ 联立即得完整接触动力学。

> [!tip] 与 §6 接触求解器的关系
> 路径 B 的 KKT 矩阵正是 §6 LCP 求解器要分解的 **Delassus 算子** $AM^{-1}A^T$ 的来源。Convex-MuJoCo 用 soft constraint 把硬 KKT 中的 $\lambda$ 替换为弹簧-阻尼实现 $\lambda=-k\phi-d\dot\phi$——这就是"硬约束 vs 软约束"的分野（§6 详述）。**灵巧操作里实时重定义坐标不可行，所以乘子法（约束嵌入）是主流。**

---

## 5. 算法层：$O(N)$ 递推的"工业革命"

> [!tip] 本节四拍
> **直觉**（24 DoF 手要 1kHz 闭环，复杂度是死敌）→ **推导**（利用运动链的局部性做递推）→ **对比**（Lagrangian $O(N^3)$ vs RNEA/ABA $O(N)$）→ **联系**（ABA 是 [[ReinforcementLearning|RL 仿真器]]/[[EmbodiedAI|物理引擎]]内核）。

计算复杂度是实时控制的死敌。纯 Lagrangian 展开 $M(q)$ 需 $O(N^2\sim N^3)$、科氏项更是三角函数求导的灾难——24 DoF 的 Shadow Hand 符号方程项数指数爆炸，1980 年代以前实时解算（<1ms）不可能。突破口是**动力学的局部性**：连杆 $i$ 只与 $i\pm1$ 相连，天然适合递推。

### 5.1 空间向量代数：6D 统一平动与转动

Featherstone 把 $v\in\mathbb R^3$ 与 $\omega\in\mathbb R^3$ 合并为 6D 空间向量（即 §2.3 的 twist 工程实现）：
- **空间速度** $\nu=(\omega,v)\in M^6$、**空间力** $f=(n,f)\in F^6$；
- **空间惯量** $I$（$6\times6$ 对称正定，含质量、质心、转动惯量）；
- **空间叉乘** $\nu\times$（运动）与 $\nu\times^*$（力，对偶），用于 $f=Ia+v\times^*Iv$。

> [!theorem] 把 6D 运算写全（不跳步：每个 $6\times6$ 块的来历与单位）
> **(a) 运动空间 $M^6$ 与力空间 $F^6$ 是一对对偶空间。** 空间速度 $\nu=(\omega,v)$：$\omega$ [rad/s] 角速度、$v$ [m/s] 是刚体上**过原点那一点**的线速度（Plücker 约定，不是质心速度）。空间力 $f=(n,f_{lin})$：$n$ [N·m] 力矩、$f_{lin}$ [N] 合力。二者的**自然配对是功率**：
> $$\langle f,\nu\rangle=f^T\nu=n^T\omega+f_{lin}^Tv\quad[\text{W}].$$
> 运动量顶标平动在上、力量顶标力矩在上——顺序相反，正是为了让这个点积恰好是功率。**这条对偶配对就是"对偶性 $J/G/P$"暗线的最底层根**：手雅可比 $J_h$（§8.1）、抓取矩阵 $G$、约束 $A$（§4.2）之所以"力用转置、速度用原矩阵"，本质都是这一个 $F^6\!-\!M^6$ 对偶在不同坐标下的投影，见 [[ControlTheory#2.1 虚功原理与对偶性|虚功原理与对偶性]]。
>
> **(b) Plücker 坐标变换 $X$**（把 §2.3 的 $SE(3)$ 作用具体成矩阵）。父系 $p$ 到子系 $i$ 的位姿为 $(R,r)$（$R\in SO(3)$ 旋转、$r$ [m] 平移），则运动向量的变换
> $${}^iX_p=\begin{bmatrix}R&0\\-R\,\hat r&R\end{bmatrix}\in\mathbb R^{6\times6},\qquad \nu_i={}^iX_p\,\nu_p+S_i\dot q_i.$$
> 左下角 $-R\hat r$ 就是"平移把角速度耦合进线速度"（$v_i$ 里多出 $\omega\times r$ 那一截），这是 §5.2 外向趟递推 $\nu_i=X_i\nu_{i-1}+S_i\dot q_i$ 里 $X_i$ 的真身，**无量纲**（纯几何变换）。力向量用**对偶变换** ${}^iX_p^*=({}^pX_i)^T$（力和运动变换互为逆转置，保证功率 $f^T\nu$ 坐标无关）。
>
> **(c) 空间叉乘的两张脸**（$6\times6$ 显式）。运动叉乘 $\nu\times$ 作用在运动量上、力叉乘 $\nu\times^*$ 作用在力量上，二者差一个转置与符号：
> $$\nu\times=\begin{bmatrix}\hat\omega&0\\\hat v&\hat\omega\end{bmatrix},\qquad \nu\times^*=-(\nu\times)^T=\begin{bmatrix}\hat\omega&\hat v\\0&\hat\omega\end{bmatrix}.$$
> **物理落点——陀螺力（科氏力的 6D 版）**：$f^{bias}=\nu\times^*I\nu$ [N; N·m] 就是"高速旋转刚体自己产生的、与加速度无关的力"，偏心螺丝刀甩起来那股拧手的力矩正是它。这一项与 §3.1 用 Christoffel 符号 $\Gamma_{ijk}$ 辛苦算的 $C\dot\theta$ 是**同一个科氏/离心力的两种记法**——符号法 $O(N^3)$、6D 叉乘 $O(N)$（§5.2 详证）。
>
> **(d) 空间惯量 $I$** 是 $M^6\to F^6$ 的线性映射（"给速度还力"）：$I=\begin{bmatrix}\bar I_c+m\hat c\hat c^T&m\hat c\\m\hat c^T&mE_3\end{bmatrix}$，$m$ [kg] 质量、$c$ [m] 质心位置、$\bar I_c$ [kg·m²] 绕质心转动惯量、$E_3$ 单位阵。它把 $f=Ia$ 从"$3\times3$ 转动 + 标量平动"升级为统一的 $6\times6$ 正定映射——**§5.3 ABA 的 articulated inertia $I^A$ 就是在这个空间里被子链逐级修正的对象**。

### 5.2 RNEA：$O(N)$ 逆动力学（控制的基石）

> [!important] 两趟递推（记住这条链就记住了 RNEA）
> - **外向趟 (Base→Tip, 运动学)**：传播速度与加速度，$\nu_i=X_i\nu_{i-1}+S_i\dot q_i$；
> - **内向趟 (Tip→Base, 动力学)**：传播力与力矩，$f_i=f_i^{net}+\sum_{child}X^Tf_{child}$，关节力矩 $\tau_i=S_i^Tf_i$。
> **复杂度 $O(N)$**——这是机器人控制的里程碑：无论多少关节，计算时间线性增长，使 1kHz 计算力矩控制成为可能。

> [!theorem] 为什么恰好是"两趟、且方向相反"（把递推讲透）
> 关键是两个**方向相反的因果依赖**：
> 1. **运动学依赖朝外**：连杆 $i$ 的速度 = 父连杆速度 + 关节 $i$ 自己的贡献。逐符号读 $\nu_i=X_i\nu_{i-1}+S_i\dot q_i$：$\nu_i=(\omega_i,v_i)\in\mathbb R^6$ 是连杆 $i$ 的 6D 空间速度（[rad/s; m/s]）；$X_i\in\mathbb R^{6\times6}$ 是把父坐标系旋量搬到 $i$ 系的 Plücker 变换（无量纲）；$S_i\in\mathbb R^6$ 是关节运动子空间/轴（转动关节沿轴，无量纲），$\dot q_i$ 是关节速率 [rad/s]。**不知道父的运动，就算不出子的运动**——所以必须从已知的基座（固定或浮动基状态）向指尖流。这一趟纯运动学，**一个力都用不到**。
> 2. **动力学依赖朝内**：连杆 $i$ 上的力平衡（Newton–Euler）$f_i=\underbrace{I_i a_i+\nu_i\times^*I_i\nu_i}_{f_i^{net}\text{：惯性力+陀螺力}}+\sum_{child}X^Tf_{child}$，需要**所有子连杆对它的反作用力**（牛顿第三定律）。指尖没有子连杆，力**完全确定**；于是每个父连杆把子连杆的反力累加上来——信息只能从指尖流回基座。
> **为什么不能合成一趟？** 连杆 $i$ 的加速度取决于**父**（要外向流），而它受的力取决于**子**（要内向流），两个依赖指向相反，逻辑上无法在一趟里同时满足。**为什么是 $O(N)$ 而非 $O(N^3)$？** 每趟里每个连杆只和它的直接邻居做常数次 6D 运算，$N$ 个连杆 $\Rightarrow$ 线性——这就是"利用运动链局部性"的兑现。

> [!tip] RNEA 免费送出科氏项：与 §3.1 Christoffel 对账
> 外向趟里加速度 $a_i=X_ia_{i-1}+S_i\ddot q_i+\underbrace{\nu_i\times S_i\dot q_i}_{\text{科氏 bias}}$——微分 $X_i\nu_{i-1}$ 时冒出的 $\nu\times$ 项，**正是 §3.1 用 Christoffel 符号 $\Gamma_{ijk}$（$O(N^3)$ 符号求导）辛苦算出的 $C\dot\theta$**。把 $\ddot q=0,\ g=0$ 喂进 RNEA，输出就是纯 $C(\theta,\dot\theta)\dot\theta$；把 $\dot q=0,\ \ddot q=e_j$ 喂进去，第 $j$ 次调用输出 $M$ 的第 $j$ 列。**同一个科氏力，符号法 $O(N^3)$、递推法 $O(N)$——这是"算法层工业革命"最锋利的一刀。**

> [!warning] RNEA 的 $\tau$ 是"刚体理想力矩"，不是电机电流（电流≠关节力矩暗线）
> RNEA 输出的 $\tau_i$ 是**关节轴上理应施加的力矩**；真机要靠 电机→[[Actuation#2. 驱动层：FOC 磁场定向控制——把三相交流当直流控|FOC]]→[[Actuation#8. 机械层 II：减速器——背隙、摩擦、弹性的来源|减速器]] 这条链实现，中间隔着 reflected inertia、背隙、摩擦、温漂。仿真把 $\tau$ 当输入直接施加、真机 $\tau$ 是传动链输出——这个**身份错位**就是 [[Actuation#9.2 完整力矩传递链模型|力矩传递链]] gap 的物理来源，也是 [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦|WMTS 把 Actuator 与 Rigid 解耦]]的动机：刚体部分（本节 RNEA/ABA）可解析、可辨识，非线性只集中在执行器侧。

```python
def rnea_inverse_dynamics(model, gravity_vec):
    """给定 q, dq, ddq → 求 tau。复杂度 O(N)。Featherstone RNEA。"""
    # --- 1. 外向趟（运动学）Base → Tip ---
    # 技巧：把"重力"实现为基座以 9.81 m/s² 向上加速，
    # 从而把重力当惯性力自然处理，无需在每个连杆显式加重力项。
    model.base.v = np.zeros(6)
    model.base.a = -gravity_vec
    for link in model.links[1:]:
        v_J = link.S * link.dq
        link.v = link.X_parent @ link.parent.v + v_J
        coriolis = spatial_cross_motion(link.v, v_J)          # 科氏项 v × v_J
        link.a = link.X_parent @ link.parent.a + link.S * link.ddq + coriolis
        # Newton-Euler: f_net = I a + v ×* (I v)，第二项为陀螺力（spatial bias force）
        link.f_net = link.I @ link.a + spatial_cross_force(link.v, link.I @ link.v)
    # --- 2. 内向趟（力）Tip → Base ---
    taus = np.zeros(model.num_links)
    for link in reversed(model.links[1:]):
        f_children = sum(c.X_parent.T @ c.f for c in link.children)  # 力按 X^T 反向传播
        link.f = link.f_net + f_children
        taus[link.idx] = np.dot(link.S, link.f)               # 投影到关节轴：tau = S^T f
    return taus
```

**局限**：RNEA 算的是逆动力学。要做仿真（正向动力学求 $\ddot q$），传统做法是用 RNEA 组装 $M(q)$ 再求逆——又回到 $O(N^3)$。这就需要 ABA。

### 5.3 ABA：$O(N)$ 正向动力学（仿真的圣杯）

Featherstone (1983) 的核心概念是 **Articulated Inertia（关节惯量）** $I^A$：当一个连杆连着一串"松弛"子链时，从它看去感受到的等效惯量。

> [!tip] "鞭子 vs 铁棍"直觉
> 挥动一根鞭子（软连接）和一根铁棍（刚连接）——鞭子末端滞后，你感受到的惯量小于铁棍。ABA 递归计算这种"被子链修正后"的等效惯量，**无需显式求逆大矩阵**就能直接解出加速度。更新规则：
> $$I^A_{parent}=I_{parent}+\Big(I^A_{child}-\frac{I^A_{child}SS^TI^A_{child}}{S^TI^A_{child}S}\Big).$$
> 减号那项是"因关节自由度而泄露掉的惯量"——关节锁死（$S=0$）时它消失、惯量直接相加。这一步把多体系统等效为变换后的单刚体。

> [!theorem] ABA 三趟递推各在算什么（把"为什么恰好三趟"讲透）
> RNEA 两趟就够（§5.2），ABA 却要**三趟**——多出来的一趟正是"求逆的替身"。逐趟读物理意义：
> 1. **第一趟 外向（Base→Tip）：只算速度相关量。** 此时 $\ddot q$ 还未知，但速度 $\nu_i$ 与两个 bias 项已可定：bias 加速度 $c_i=\nu_i\times S_i\dot q_i$（[rad/s²; m/s²]，关节转动带来的科氏偏置）、刚体 bias 力 $p_i=\nu_i\times^*I_i\nu_i$（[N; N·m]，§5.1(c) 的陀螺力）。**为什么必须先做**：articulated inertia 的修正只依赖构型与速度、不依赖 $\ddot q$，所以可以在不知加速度时就备好。
> 2. **第二趟 内向（Tip→Base）：把"松弛子链"的等效惯量与力逐级折叠回来。** 对每个连杆算 $I^A_i$（articulated inertia，[kg·m²]，"从这里往外看整条软子链的等效惯量"）与 $p^A_i$（articulated bias force，子链在零关节力矩下会自己产生的力）。关键的减号项 $-\frac{I^A SS^TI^A}{S^TI^AS}$ 把"子关节能自由转动的那个方向"的惯量**扣掉**——因为那个方向的力会被子关节"让开"、传不回父连杆。**这一趟就是 ABA 相对 RNEA 多出来的核心**：它用 $O(N)$ 的递归折叠，替代了"组装 $M$ 再求逆"的 $O(N^3)$。
> 3. **第三趟 外向（Base→Tip）：自顶向下解出加速度。** 基座加速度已知（固定基为 $-g$、浮动基由上一步定），每个关节按 $\ddot q_i=D_i^{-1}(u_i-U_i^Ta'_i)$ 解出——$u_i$ 是"投影到关节轴的净驱动力"、$U_i^Ta'_i$ 是"父连杆运动经惯性耦合传来的反抗"，$D_i=S_i^TI^A_iS_i$ 是**关节轴向的标量有效惯量**。物理上：只有父的运动定了，子关节"该转多快"才唯一确定，所以必须再外向一趟。
>
> **一句话记忆**：外向铺速度 → 内向折惯量（省掉求逆）→ 外向落加速度。$O(N)$ 的本质仍是"运动链局部性 + 两个方向相反的因果依赖"（§5.2），只是正向动力学比逆向多了一层"惯量必须先折叠、加速度才能解"的耦合。

> [!warning] ABA 把 $\tau$ 当"干净输入"直接施加——这正是 Sim-to-Real gap 的埋点
> ABA 第三趟里 $u_i=\tau_i-S_i^Tp^A_i$ 默认 $\tau_i$ 就是理想关节力矩，无损地进入加速度求解。但真机的 $\tau$ 是电机→FOC→减速器的**输出**、隔着 reflected inertia / 背隙 / 摩擦 / 温漂（"电流≠关节力矩"暗线）。因此 [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦|WMTS 把世界模型拆成 Actuator + Rigid 两段]]的合理性，恰恰建立在"**ABA 描述的刚体段可解析、可辨识，非线性只集中在执行器段**"这一事实上——本节的 $O(N)$ 递推正是那个可信的 Rigid 段内核，也是 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|Sim-to-Real]] 里 Transition 项被拆分治理的物理依据。

```python
def articulated_body_algorithm(model, taus):
    """给定 q, dq, tau → 求 ddq。复杂度 O(N)。物理引擎 step() 的内核。"""
    # 1. 初始化：算速度相关的 bias（此时还不知道 ddq）
    for link in model.links[1:]:
        v_J = link.S * link.dq
        link.v = link.X_parent @ link.parent.v + v_J
        link.c = spatial_cross_motion(link.v, v_J)              # bias 加速度
        link.p = spatial_cross_force(link.v, link.I @ link.v)   # 刚体 bias 力
        link.Ia, link.pa = link.I.copy(), link.p.copy()
    # 2. 内向趟：算 articulated inertia (Ia) 与 bias force (pa)
    for link in reversed(model.links[1:]):
        U = link.Ia @ link.S
        D_inv = 1.0 / np.dot(link.S, U)                          # 关节轴向标量惯量之逆
        u = taus[link.idx] - np.dot(link.S, link.pa)            # 可用于加速的净力
        link.U, link.D_inv, link.u = U, D_inv, u
        if link.parent:
            Ia_rel = link.Ia - np.outer(U, U) * D_inv           # 减去"自由方向"惯量
            link.parent.Ia += link.X_parent.T @ Ia_rel @ link.X_parent
            bias_rel = link.pa + link.Ia @ link.c + U * D_inv * u
            link.parent.pa += link.X_parent.T @ bias_rel
    # 3. 外向趟：算加速度
    for link in model.links[1:]:
        a_prime = link.X_parent @ link.parent.a + link.c
        link.ddq = link.D_inv * (link.u - np.dot(link.U, a_prime))  # (净力 − 基座运动惯性力)/关节惯量
        link.a = a_prime + link.S * link.ddq
    return [link.ddq for link in model.links]
```

ABA 让数十关节灵巧手的仿真在微秒级完成，为 Sim-to-Real RL 提供算力基础，是 MuJoCo/Dart/RBDL/Brax 的核心。

### 5.4 三法对比与选型

| 维度 | Lagrangian | RNEA | ABA |
|:--|:--|:--|:--|
| 理论基础 | 能量 $L=T-V$ | 牛顿-欧拉力平衡 | 关节惯量递推 |
| 计算问题 | ID 与 FD 皆可 | 主要 ID | 主要 FD |
| 复杂度 | $O(N^3)$（符号） | $O(N)$ | $O(N)$ |
| 约束处理 | Lagrange 乘子（系统化） | 需虚拟切断+投影 | 原生支持树形 |
| 灵巧操作用途 | 稳定性分析、自适应 | 1kHz 计算力矩控制 | Sim-to-Real 数据生成 |

> [!tip] 选型指南
> 串联+实时控制 → **RNEA**；仿真+RL 训练 → **ABA**（MuJoCo/Brax 内核）；理论推导+控制器设计 → **Lagrangian**（$\dot M-2C$ 反对称）；闭链/并联/非完整 → **Lagrangian + 乘子**。

---

## 6. 仿真层：接触动力学的深水区

> [!tip] 本节四拍
> **直觉**（刀头触螺钉=间歇、冗余、非线性摩擦三重困难）→ **推导**（LCP 互补 vs 凸优化软约束）→ **对比**（Bullet/ODE 的 LCP vs MuJoCo 的凸优化）→ **联系**（软接触梯度平滑→[[ReinforcementLearning|可微物理/RL 训练]]）。

灵巧操作的接触有三个折磨人的特点：**间歇性**（make/break 毫秒切换→非光滑）、**约束冗余**（多指抓握过/欠定→矩阵奇异）、**摩擦锥**（非线性 $\|f_t\|\le\mu f_n$）。两大流派：LCP（Bullet/ODE）与凸优化（MuJoCo）。

### 6.1 LCP 流派

非穿透建为线性互补：$a=M^{-1}(f_{ext}+J^T\lambda)$，$Ja+\zeta\ge0$（不穿透），$\lambda\ge0$（只推不拉），$\lambda^T(Ja+\zeta)=0$（互补）。**摩擦锥线性化**：库伦二阶锥近似为多棱锥，引入各向异性（沿对角 vs 沿轴滑动阻力不同）。**求解器** PGS：对灵巧手这种轻量高刚度系统收敛慢，迭代不足→残差表现为**穿透**或**幽灵力**（仿真里手指"插进"螺丝刀）。

### 6.2 凸优化流派（MuJoCo）：放弃硬约束

Todorov 的洞见：放弃"刚体绝对不可穿透"，允许微小穿透并产生基于势能的恢复力（**soft constraint**），把接触动力学建为**凸 QP**：
$$\min_{\ddot q}\ \tfrac12\ddot q^TM\ddot q+\text{Potential(穿透)}\quad\text{s.t. 摩擦锥}.$$
三大 value-add：① **可逆性**——即便接触状态下动力学也良态，逆动力学仍可用（对 [[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|基于模型的控制]]是福音）；② **平滑性**——软接触让梯度平滑，对**可微物理与 RL 训练至关重要**（呼应 [[ContactMechanics#6. 可微接触物理：让接触进入梯度优化|可微接触]]）；③ **稳定性**——避免 LCP 在大质量比（灵巧手捏薄纸）时的数值爆炸。

### 6.3 PGS 核心循环（实时引擎的心脏）

```python
def solve_contact_lcp_pgs(J, M_inv, bias, mu, iterations=50):
    """解 (J M⁻¹ Jᵀ) λ = -bias，约束于摩擦锥（投影高斯-赛德尔）。"""
    A = J @ M_inv @ J.T            # Delassus 算子：接触点的有效逆质量（= §4.2 的 AM⁻¹Aᵀ）
    n_contacts = len(bias) // 3    # 每接触 3 DOF：1 法向 + 2 切向
    lam = np.zeros(len(bias)); inv_diag = 1.0 / np.diag(A)
    for _ in range(iterations):
        for i in range(n_contacts):
            n, t1, t2 = 3*i, 3*i+1, 3*i+2
            # 法向：高斯-赛德尔一步后投影到 ≥0（只能排斥）
            res_n = bias[n] + A[n] @ lam - A[n, n]*lam[n]
            lam[n] = max(0.0, -res_n * inv_diag[n])
            # 切向：摩擦上限取决于当前法向力 lam[n]
            limit = mu * lam[n]
            lt1 = -(bias[t1] + A[t1] @ lam - A[t1,t1]*lam[t1]) * inv_diag[t1]
            lt2 = -(bias[t2] + A[t2] @ lam - A[t2,t2]*lam[t2]) * inv_diag[t2]
            mag = np.hypot(lt1, lt2)               # 投影进摩擦圆：超限则缩回
            if mag > limit and mag > 1e-8:
                lt1 *= limit/mag; lt2 *= limit/mag
            lam[t1], lam[t2] = lt1, lt2
    return lam
```

> [!note] 数值稳定三技巧
> **Warm Starting**（用上帧接触力作初值，呼应 [[ContactMechanics#5.2 两类求解器：直接 vs 迭代|SI]] 与 [[Optimization|MPC warm start]]）、**Baumgarte 稳定化**（把位置违反映射为补偿加速度）、**摩擦锥投影**（切向脉冲实时按法向力限幅）。

### 6.4 仿真伪影：策略学到的是真物理还是 bug？

> [!example] L25NS 实测案例：MuJoCo 默认 `solimp` 使 `frictionloss` 退化成弱阻尼、默认 `impratio` 造成摩擦锥内蠕变——见 [[MuJoCo_Sim2Real_Params]]。

| 伪影 | 现象 | 原因 |
|:--|:--|:--|
| **Drift（漂移）** | 静止物体缓慢滑动 | PGS 迭代不足、或 Baumgarte 系数不当引入"幽灵速度" |
| **Jitter（抖动）** | 接触点在表面跳动 | 网格法向不连续→$J$ 突变→冲量尖峰 |
| **Tunneling（穿隧）** | 高速物体直接穿过障碍 | 时间步过大；需启用 CCD（连续碰撞检测） |

> [!important] 为什么这关乎 RL
> 策略会**利用**仿真伪影——若仿真允许穿透或幽灵力转笔/转刀更易成功，策略就学到这些非物理捷径，一上真机即崩。这是 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|sim-to-real]] gap 中 Transition 项的微观来源。

---

## 7. 闭链与操作空间动力学：握住螺丝刀之后

> [!tip] 本节四拍
> **直觉**（手一握紧，系统从开链变闭链，"挥起来"的手感突变）→ **推导**（有效惯量、约束漂移、内力、操作空间质量阵）→ **对比**（动力学一致伪逆 vs Moore-Penrose 伪逆）→ **联系**（操作空间↔[[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|阻抗控制]]）。

### 7.1 拓扑突变与有效惯量

握紧螺丝刀的瞬间，系统从**开链**变**闭链**（回扣 §2.1 的惯量突变）。物体不再是单纯负载——手指惯量经雅可比投射到物体上：

$$M_{eff}=M_{obj}+G^TM_{fingers}G.$$

> [!theorem] 逐步推导 $M_{eff}=M_{obj}+G^TM_{fingers}G$（能量投影，不跳步）
> 目标：闭链后"从物体这一点看去"有多大惯量。用**动能守恒 + 抓取约束**四步导出。
> 1. **两块动能**：系统总动能 = 物体动能 + 手指动能，$T=\tfrac12\dot x_{obj}^TM_{obj}\dot x_{obj}+\tfrac12\dot\theta^TM_{fingers}\dot\theta$。符号：$\dot x_{obj}\in\mathbb R^6$ 物体空间速度 [rad/s; m/s]，$M_{obj}\in\mathbb R^{6\times6}$ 物体空间惯量 [kg·m²/kg]（§5.1(d)），$\dot\theta\in\mathbb R^n$ 手指关节速度 [rad/s]，$M_{fingers}\in\mathbb R^{n\times n}$ 手指关节质量阵 [kg·m²]。
> 2. **抓取约束把手指运动"锁"到物体上**：刚性握持时接触点不滑，手指关节速度被物体运动完全决定。记这个运动学映射为 $G$：$\dot\theta=G\,\dot x_{obj}$（$G\in\mathbb R^{n\times6}$ 由抓取矩阵与手雅可比合成，无量纲/长度倒数）。**这一步是"闭链"的数学定义**——原本 $n+6$ 个独立速度被压到只剩 $6$ 个。
> 3. **消去 $\dot\theta$**：把约束代入手指动能，$\tfrac12\dot\theta^TM_{fingers}\dot\theta=\tfrac12\dot x_{obj}^T\big(G^TM_{fingers}G\big)\dot x_{obj}$——手指惯量被**同一个虚功对偶**（$G$ 前乘速度、$G^T$ 前乘力，§8.1 三矩阵同构）投影到物体空间。
> 4. **合并**：$T=\tfrac12\dot x_{obj}^T\underbrace{(M_{obj}+G^TM_{fingers}G)}_{M_{eff}}\dot x_{obj}$。$\blacksquare$ 由动能的二次型系数即读出有效惯量。**逐符号读 $G^TM_{fingers}G$**：$G$ 把物体运动"下发"给关节、$M_{fingers}$ 给出关节惯性阻力、$G^T$ 再把关节力"上收"回物体——与 §4.2 Delassus $\mathcal D=AM^{-1}A^T$、§7.3 $\Lambda^{-1}=JM^{-1}J^T$ 是**同一个 $(\cdot M\cdot)$ 投影三明治**，只是这里投影的是惯量本身而非其逆。
>
> **为什么叫"突变"（接触非光滑性暗线）**：握持发生在**一个时刻**——前一刻 $G$ 不存在、有效惯量就是 $M_{obj}$，后一刻约束瞬间生效、有效惯量跳到 $M_{obj}+G^TM_{fingers}G$，质量矩阵的秩与特征值**不连续跳变**。这正是接触把动力学撕成**混合系统 (hybrid system)** 的一个缩影：模式切换点上状态方程本身改变，梯度在此断裂。它与 [[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 视角的"接触流形 + 混合动力学"两副面孔]]是同一现象——策略梯度在这类切换点高方差、解析控制器需要接触状态机，根子都在这个惯量突变。冲击 (impact) 时若物体已有速度，还会伴随动量的瞬时再分配（$M_{eff}$ 突增 → 广义动量守恒下速度突降）。

> [!important] 控制洞察
> 若只补偿物体重力而忽略 $M_{eff}$ 的变化，控制器会变"软"、响应迟钝。手指接近伸直（奇异附近）时 $M_{fingers}$ 沿某些方向趋于无穷，物体表观惯量剧增——挥转螺丝刀时若手指构型不当，刀头会异常"沉重"难以加速。$G$ 与有效惯量见 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|抓取矩阵]]。

### 7.2 约束漂移与内力

**约束漂移**：数值积分中 $\phi(q)=0$ 的闭链会因精度误差逐渐"断开"（两手合十算着算着分开了）。**Baumgarte 稳定化**要求 $\ddot C+2\alpha\dot C+\beta^2C=0$，引入人为恢复力拉回——$\alpha,\beta$ 整定是门艺术（太小拉不回、太大刚性发散）。

**内力 (Internal Forces)**：多指抓握自由度冗余，存在零空间 $\tau=J^TF_{motion}+(I-J^TJ^\#)\tau_{int}$。$\tau_{int}$ 不产生运动、只产生**挤压 (squeeze)**——必须主动控内力维持力闭合：太小螺丝刀脱手、太大损坏物体或浪费能量（与 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|内力/$\mathrm{Null}(G)$]] 是同一对象）。

### 7.3 操作空间动力学 (Khatib)：在任务空间直接设计

> [!note] 教科书参考
> Khatib 1987 "A Unified Approach for Motion and Force Control" + Murray Ch. 4。

任务定义在笛卡尔空间（刀头位姿），而非关节空间。把动力学投影到任务空间，得**操作空间质量矩阵**与控制律：

$$\Lambda(x)=(JM^{-1}J^T)^{-1},\qquad \tau=J^TF=J^T\big[\Lambda(x)\ddot x_d+\mu+p\big]+\tau_{null}.$$

> [!theorem] 逐步推导 $\Lambda=(JM^{-1}J^T)^{-1}$（不跳步）
> 目标：把关节空间动力学**投影**到任务空间，看刀头"感受到"多大惯量。四步：
> 1. **关节空间 EOM**（暂略约束）：$M\ddot q+C\dot q+N=\tau$。符号：$q\in\mathbb R^n$ 关节角 [rad]，$\tau\in\mathbb R^n$ 关节力矩 [N·m]，$M\in\mathbb R^{n\times n}$ 关节质量阵 [kg·m²]。
> 2. **任务变量与其加速度**：$x=f(q)\in\mathbb R^m$（刀头位姿），$\dot x=J\dot q$，再微分一次得 $\ddot x=J\ddot q+\dot J\dot q$（$J=\partial f/\partial q\in\mathbb R^{m\times n}$ [无量纲/长度]，$\dot J\dot q$ 是"雅可比随构型变化"带来的加速度偏置）。
> 3. **力的来源**：任务力 $F\in\mathbb R^m$（[N; N·m]）经**同一虚功对偶**产生关节力矩 $\tau=J^TF$（又见上 §4.2 的 $A^T\lambda$——$J^T$ 与 $A^T$ 同构）。代入 EOM 解 $\ddot q=M^{-1}(J^TF-C\dot q-N)$，回代第 2 步：
> $$\ddot x=\underbrace{JM^{-1}J^T}_{=\Lambda^{-1}}F-JM^{-1}(C\dot q+N)+\dot J\dot q.$$
> 4. **解出 $F$**：令 $\Lambda:=(JM^{-1}J^T)^{-1}$，移项
> $$F=\Lambda\ddot x+\underbrace{\big(\Lambda JM^{-1}C\dot q-\Lambda\dot J\dot q\big)}_{\mu\text{：任务空间科氏/离心}}+\underbrace{\Lambda JM^{-1}N}_{p\text{：任务空间重力}}.$$
> 与上面给出的 $F=\Lambda\ddot x_d+\mu+p$ 逐项吻合。**逐符号读 $\Lambda$**：$JM^{-1}J^T$ 把任务力映成任务加速度（有效**逆**惯量，$1/\text{kg}$），其逆 $\Lambda$ 就是刀头的**表观惯量** [kg 或 kg·m²]——"在刀头这一点上，推动它单位加速度需要多大力"。

> [!important] $\Lambda$ 与 §4.2 Delassus $\mathcal D^{-1}$ 是同一构造（Delassus 主线闭环）
> $$\underbrace{\Lambda=(JM^{-1}J^T)^{-1}}_{\text{任务惯量, }J=\text{任务雅可比}}\quad\Longleftrightarrow\quad\underbrace{\mathcal D^{-1}=(AM^{-1}A^T)^{-1}}_{\text{约束有效惯量, }A=\text{约束雅可比}}$$
> **一个公式，两副面孔**：约束反力（§4.2）与任务表观惯量（此处）是同一套 $(\cdot M^{-1}\cdot^T)^{-1}$，也正是 §6.3 PGS 里 $JM^{-1}J^T$ 的接触有效逆质量。记住这条，就把"约束—接触—任务控制"缝成一体。
> **奇异性直觉**：手指接近伸直时 $J$ 掉秩 $\Rightarrow JM^{-1}J^T$ 奇异 $\Rightarrow\Lambda$ 沿某方向 $\to\infty$——刀头在该方向"表观无穷重"、推不动。这就是 §7.1"手指伸直时刀头异常沉重"的严格来源，也是 [[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|操作空间控制]]必须监测可操作度的原因。

冗余系统（$n>m$）需**动力学一致性伪逆** $\bar J=M^{-1}J^T\Lambda$，满足 $J\bar J=I$，零空间投影 $N=I-\bar JJ$。

> [!important] $\bar J$ 不是 Moore–Penrose 伪逆
> $\bar J$ 保证**零空间力矩不影响操作空间运动**（这才是"动力学一致"）。完整层级控制律按优先级嵌套零空间：
> ```
> Priority 1: 刀头轨迹跟踪  →零空间→  Priority 2: 抓取内力维持  →零空间→  Priority 3: 关节限位规避
> ```
> $\tau=J_1^TF_1+(I-J_1^T\bar J_1^T)[J_2^TF_2+(I-J_2^T\bar J_2^T)\tau_0]$。

> [!tip] 工程洞察：操作空间是阻抗控制的根
> 在操作空间定义期望的质量-阻尼-刚度，机器人即可柔顺交互——这正是 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]的动力学基础。挥转螺丝刀对准螺钉时，我们要的恰是"刀头在接触方向软、在跟踪方向硬"的任务空间阻抗。

---

## 8. 腱驱动与冗余动力学：真实灵巧手的传动

> [!tip] 本节四拍
> **直觉**（Shadow/Faive 等类人手靠腱传动，腱只能拉不能推）→ **推导**（耦合矩阵 $P$、弹性腱、力闭合）→ **对比**（腱网络 $P$ 与抓取矩阵 $G$ 完全同构）→ **联系**（冗余、自运动、可操作度椭球）。

### 8.1 腱网络运动学：耦合矩阵 $P$

第 $i$ 根腱伸长 $h_i(\theta)=l_i+\sum_jr_{ij}\theta_j$（$r_{ij}$ 为力臂半径，正负取决于绕线方向）。**耦合矩阵** $P(\theta)=(\partial h/\partial\theta)^T$ 给出 $\tau=P(\theta)f$（$f$ 为腱张力），对偶地 $\dot h=P^T\dot\theta$。

> [!important] $P$ 与抓取矩阵 $G$、手雅可比 $J_h$ 三矩阵同构（一套工具，三处复用）
> | 映射对象 | 力的映射 | 速度的对偶 |
> |:--|:--|:--|
> | 接触→关节（手雅可比 $J_h$） | $\tau_{joint}=J_h^Tf_{contact}$ | $\dot x_c=J_h\dot\theta$ |
> | 接触→物体（抓取矩阵 $G$） | $F_{object}=Gf_{contact}$ | $\dot x_c=G^T\dot x_{obj}$ |
> | 腱→关节（耦合矩阵 $P$） | $\tau_{joint}=Pf_{tendon}$ | $\dot h=P^T\dot\theta$ |
> 三者都是"力用 $M^T$ 前乘、速度用 $M$ 前乘"的**虚功对偶**（$J/G/P$ 的转置成对出现），因此**抓取分析的全部工具——力闭合、冗余、零空间——可原样搬到腱网络**。其严格定义与内力零空间 $\mathrm{Null}(G)$ 的完整推导，见 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|抓取矩阵的严格定义]]（那里对 $G$ 讲的每一步，把 $G\to P$ 逐字替换即得腱网络版本）。这是本讲"对偶性 $J/G/P$"暗线在 §4.2 约束反力 $A^T\lambda$、§7.3 任务力 $J^TF$ 之外的第三处落地。

### 8.2 弹性腱与力闭合

弹性腱张力由位移决定 $f_i=k_i(e_i+h_i(0)-h_i(\theta))$，动力学多出刚度项 $S(\theta)=PK(h(\theta)-h(0))$ 与新耦合矩阵 $Q=PK$（执行器位置→关节力矩）。

> [!warning] 腱的单向性：只能拉不能推（$f_i>0$）
> 这是与刚性连杆的根本区别。**腱网络力闭合**：对任意 $\tau$ 存在 $f>0$ 使 $Pf=\tau$。充要条件（与抓取力闭合完全类比）：$P$ 行满秩 + 存在严格正内力 $f_N>0$ 使 $Pf_N=0$。腱数界限（Carathéodory/Steinitz，又见 [[ContactMechanics#3.3 最小接触点数：Caratheodory、Steinitz 与"例外曲面"|§3.3]]）：$n$ 关节**下界 $n+1$ 根、上界 $2n$ 根**。两种配置：N+1（1 共享腱+$n$ 拮抗腱）、2N（每关节 2 拮抗腱）。

腱力控制：$f=P^+\tau+f_N$，并优化最小张力 $\min\|f_N\|^2$ s.t. $f\ge\epsilon\mathbf 1$（保证全正张力）。

### 8.3 冗余、自运动与可操作度

**运动学冗余**（$n>p$）：零空间 $\ker(J_h)$ 是不影响末端的关节运动。**自运动**：末端固定时手臂仍可改形 $\dot q=\bar Jv_x+N\alpha$——用于避障、关节限位规避、能量最小化（挥转螺丝刀时手肘可在不动刀头的前提下避开桌沿）。**可操作度椭球** $w=\sqrt{\det(J_hJ_h^T)}$，$w\to0$ 接近奇异；运动椭球与力椭球互为转置——**对偶性的又一次现身**。

---

## 9. 适配层：可微物理与神经动力学

> [!tip] 本节四拍
> **直觉**（仿真里的螺丝刀和真机甩得不一样，Sim-to-Real 的痛点是 System ID）→ **推导**（解析梯度 vs 神经动力学）→ **对比**（全系统模型 vs 关节级分解）→ **联系**（可微物理↔[[ContactMechanics#6. 可微接触物理：让接触进入梯度优化|可微接触]]、↔[[Optimization|System ID]]）。

**解析梯度**：新一代引擎（Dojo/Brax/Nimble）支持链式法则直接算 $\partial s_{t+1}/\partial\theta$，于是可用**梯度下降自动调摩擦/质量/惯量**使仿真轨迹匹配真机——比盲目域随机化更高效精准（与 [[ContactMechanics#6.2 实现可微的三条路径|隐函数定理解析梯度]]同源）。

**物理先验网络**：LNN/HNN 把物理结构嵌入架构——LNN 学 Lagrangian $L_\theta(q,\dot q)$、自动微分得 Euler–Lagrange，保证能量守恒（但对传感器噪声敏感）。

> [!tip] 关节级神经动力学（[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]]）
> 不建模整个手-物系统，而为每关节学独立的"净效应"动力学 $\hat q^{(j)}_{t+1}=f_\theta^{(j)}(q_t^{(j)},\dot q_t^{(j)},a_t^{(j)})$，隐式吸收关节耦合、接触力、未建模摩擦/间隙。优势：**数据高效**（3→1 低维）、**零样本泛化**（跨物体/腕姿）、**自主采数**（只需编码器）。与**残差策略** $\pi_{real}=\pi_{sim}+\Delta\pi$ 结合——仿真策略给基线、残差补动力学误差（呼应 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RMA/残差迁移]]）。其本质是 §3.4"刚体对惯量参数线性、只有 actuator 非线性需神经网络补"的兑现。

---

## 10. 知识回扣与记忆图：一支螺丝刀串起动力学六层

> [!abstract] 用一支螺丝刀把全讲复述一遍（刻意复述，为记忆）
> 我们要让灵巧手挥转一支偏心螺丝刀、精确对准螺钉。**(§2)** 螺丝刀位姿活在 SE(3) 上，质量矩阵 $M(q)$ 是构型流形的度量。**(§3)** 由 Hamilton 最小作用量推出操作器方程 $M\ddot q+C\dot q+N=\tau$——偏心配重让 $M(q)$ 强依赖构型，快速挥动时科氏项 $C\dot\theta$ 显著（刀头"甩偏"）；操作器方程对惯量参数线性，使我们能用 1 秒轨迹辨识它的惯量。**(§4)** 手一握紧、刀头一触螺钉，都是约束——约束反力 $A^T\lambda$ 不是补丁，$AM^{-1}A^T$ 这个 Delassus 算子贯穿后续。**(§5)** 要 1kHz 算力矩用 RNEA、要仿真用 ABA，靠的是动力学的局部性与 6D 空间向量。**(§6)** 仿真里接触用 LCP 或 MuJoCo 凸优化求解，当心漂移/抖动/穿隧这些会被策略利用的伪影。**(§7)** 握住螺丝刀后系统变闭链，有效惯量 $M_{obj}+G^TM_{fingers}G$ 突变，还要控内力别脱手；在操作空间直接设计刀头的任务阻抗。**(§8)** 真实的腱驱动手里，耦合矩阵 $P$ 和抓取矩阵 $G$ 同构、只能拉不能推。**(§9)** 最后用可微物理/神经动力学把仿真的螺丝刀校准到真机。**一支螺丝刀，挥遍了动力学六层大厦。**

> [!important] 一张表记住全篇
> | 层 | 核心问题 | 关键工具 | 螺丝刀的哪一环 |
> |:--|:--|:--|:--|
> | §2 几何 | 构型如何表示 | SE(3)、指数坐标 | 位姿与构型流形 |
> | §3 能量 | 方程从哪来 | Hamilton 原理、$M/C/N$、线性参数化 | 甩偏的科氏力、惯量辨识 |
> | §4 约束 | 接触如何进入 | Pfaffian、Lagrange 乘子、Delassus | 握持/触螺钉的约束反力 |
> | §5 算法 | 如何实时算 | RNEA/ABA、空间向量 | kHz 力矩、微秒仿真 |
> | §6 仿真 | 接触如何稳 | LCP/MuJoCo/PGS、伪影 | 仿真为何甩不对 |
> | §7 闭链 | 握住之后 | 有效惯量、操作空间、$\bar J$ | 握后手感突变、任务阻抗 |
> | §8 腱驱/冗余 | 真实传动 | 耦合矩阵 $P$、自运动 | 类人手、避桌沿 |
> | §9 适配 | 真机校准 | 可微物理、神经动力学 | 校准到真螺丝刀 |

> [!tip] 五条贯穿全讲的"暗线"
> 1. **对偶性 $J/G/P$**：手雅可比、抓取矩阵、腱耦合矩阵共享同一套力闭合/冗余/零空间分析——一套工具贯穿 §4/§7/§8，并外连 [[ContactMechanics]]/[[ControlTheory]]。
> 2. **Delassus 主线** $AM^{-1}A^T$：从约束乘子（§4.2）到 KKT（§4.3）到 PGS 的接触有效逆质量（§6.3），是动力学与 [[ContactMechanics|LCP]]/[[Optimization|QP]] 的枢纽。
> 3. **三种等价形式**：Lagrangian（推导/Sim2Real）、Hamiltonian（辛积分/最优控制）、Newton–Euler（实时 RNEA）——同一物理、三种语言（§3.5）。
> 4. **线性参数化→自适应**：操作器方程对惯量参数线性（§3.4），直通 [[ControlTheory#12. 自适应控制与确定性等价|自适应控制]]与 [[ReinforcementLearning|System ID]]。
> 5. **变分母体**：Hamilton 原理同时生出力学、辛积分器、与 [[Optimization|Pontryagin/iLQR]]——力学与最优控制本是一家（§3.2）。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[ContactMechanics]]**：LCP/Delassus（§4/§6）、抓取矩阵与有效惯量（§7）、可微接触（§9）。
> - **↔ [[ControlTheory]]**：操作器方程是控制对象；操作空间↔阻抗（§7）；线性参数化↔自适应（§3.4）；无源性（§3.3）；小振动↔刚度悖论（§3.6）。
> - **↔ [[Optimization]]**：变分↔Pontryagin/iLQR（§3.2/§3.5）；动力学求解是 MPC 内循环；可微物理↔System ID（§9）。
> - **↔ [[ReinforcementLearning]]**：ABA 是仿真器内核（§5.3）；动力学模型=世界模型；仿真伪影=sim-to-real gap 之源（§6.4）。
> - **↔ [[StochasticProcess]]**：GP/ensemble 动力学学习补偿残差（§9）。

---

## 11. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及动力学的核心主题。

### 神经动力学与模型学习
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] — 关节级神经动力学
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] — 快速电机自适应
- [[Lessons from Learning to Spin Pens]] — 转笔经验教训
- [[Deep Dynamics Models for Learning Dexterous Manipulation]] — Ensemble dynamics + MPC 的样本高效模型学习

### 轨迹优化与规划
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 轨迹优化数据生成
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 轨迹跟踪
- [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] — 演示数据生成

### 物理角色动画与仿人
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]] — 物理角色模仿
- [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] — 仿人手指步态
- [[Learning Agile and Dynamic Motor Skills for Legged Robots]] — 解析刚体动力学 + 学习型 Actuator Network 的结构化 Sim-to-Real

### Sim-to-Real 与动力学迁移
- [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation]] — 残差动力学补偿
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率动力学控制
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] — Actuation-aware 动力学建模：torque-speed envelope 约束策略在执行器物理极限内
- [[A Survey of Sim-to-Real Methods in RL]] — MDP 四要素分类框架（Transition 即动力学域差异）
- [[Part-Guided 3D RL for Sim2Real Articulated Object Manipulation]] — 铰接物体动力学的 Sim2Real
- [[sim2real|硬件 Sim-to-Real Gap 分析]] — 力矩传递链完整建模 $\tau_{joint}=\eta\,i\,K_tI-\tau_{friction}-k(\theta)\theta$

### 物理感知预训练
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]] — Dynamics-lifted 几何预训练：粒子动力学统一为 transport equation $\partial\rho/\partial t+\nabla\cdot(v\rho)=0$
- [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] — 把 Rodrigues 公式改造为可学习的结构化动作算子

### 执行器建模与关节传动
> [!note] Foundation 交叉
> 操作器方程右端 $\tau$ 的物理实现——电机模型、FOC、减速器背隙/摩擦/弹性、reflected inertia $i^2J_m$、力矩传递链 $\tau_{joint}=\eta iK_tI-\tau_{fric}-k\theta$ 与 actuator net——完整展开见 [[Actuation|执行器与驱动系统]]。
- [[谐波减速器与RV减速器选型核心区分依据|谐波 vs RV 减速器]] — 谐波柔轮弹性对 sim-to-real gap 的影响
- [[Minimalist Compliance Control|MCC]] — 方向相关效率模型：谐波减速器传动效率 70–90% 的非线性补偿

### 动力学感知策略学习
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 世界模型预测接触诱导动力学，条件化 RL 策略

### 项目级真机动力学 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-002-Latency-Aware-Actuator|LAAA]] — CAN 延迟 + 温漂 conditioned actuator FiLM，5min 真机自适应
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-007-Implicit-Explicit-Contact-WM|IECW]] — 解析刚体动力学 + 触觉门控接触 patch 残差网络
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-014-WM-Gradient-Adaptive-DR|WG-ADR]] — 用 WM 输入梯度量化各动力学参数敏感度，自适应分配 DR 方差预算

---

## 12. 结论

灵巧操作的动力学早已不是简单的 $F=ma$，而是一门在**计算受限、接触不确定、拓扑动态变化**下求最优策略的艺术。从 SE(3) 几何（§2）、Hamilton 变分（§3）、约束乘子（§4），到 RNEA/ABA 的 $O(N)$ 递推（§5）、接触求解器的二元取舍（§6）、闭链与操作空间（§7）、腱驱动与冗余（§8），最终落到可微物理与神经动力学（§9）：**掌握 RNEA/ABA 是入门，理解接触求解器是进阶，能驾驭可微物理/神经动力学则是通向 Sim-to-Real 未来的钥匙。** 而贯穿始终的，是对偶性（$J/G/P$）、Delassus 算子、与变分母体这几条把动力学、接触、控制、优化缝在一起的暗线。
