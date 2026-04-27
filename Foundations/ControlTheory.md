---
tags:
  - foundation
  - control-theory
  - dexterous-manipulation
aliases:
  - 控制理论
  - Control
  - 阻抗控制
  - Impedance Control
created: 2026-01-31
related:
  - "[[Dynamics]]"
  - "[[Optimization]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
---

# 灵巧操作控制理论深度研究报告：从位置控制范式到接触隐式非线性动力学

# Deep Research Report on Control Theory for Dexterous Manipulation: From Position Control Paradigms to Contact-Implicit Nonlinear Dynamics

> [!tip] 相关领域
> - [[Dynamics]] - 动力学方程是控制设计的基础
> - [[ContactMechanics]] - 接触力学决定了力控制的约束
> - [[Optimization]] - MPC 与轨迹优化是现代控制的核心工具
> - [[ReinforcementLearning]] - 数据驱动控制的替代范式
> - [[EmbodiedAI]] - 分层 VLA 系统中低层控制器的设计
>
> **相关论文**:
> - [[Learning Agile and Dynamic Motor Skills for Legged Robots]] - action-to-torque Actuator Network 近似低层闭环控制链路
> - [[Learning Quadrupedal Locomotion over Challenging Terrain]] - proprioceptive student policy 调制底层运动 primitive

## 1. 引言：灵巧操作的物理本质与控制挑战

## 1. Introduction: The Physical Essence and Control Challenges of Dexterous Manipulation

机器人灵巧操作（Dexterous Manipulation）代表了机器人学皇冠上的明珠。它不仅要求机械手具备多指协调的运动能力，更深层的挑战在于如何在一个高度非线性、非结构化且充满不确定性的物理世界中，通过断续的接触（Intermittent Contact）来改变环境的状态。作为该领域的首席科学家，构建Obsidian知识库的核心任务不仅是罗列公式，更是要梳理出控制理论如何从简单的刚性位置追踪，演进为能够处理复杂接触动力学的现代范式。

本报告将以一种详尽的叙事方式，剖析控制理论在灵巧操作中的演变。我们将从最基础的运动学与静力学对偶性出发，深入探讨为什么传统的位置控制在接触任务中会失效，进而引出阻抗控制、力/位混合控制以及操作空间公式化（Operational Space Formulation, OSF）等解决方案。随后，我们将进入非线性控制的深水区，探讨滑模控制（Sliding Mode Control）在处理模型不确定性中的作用，以及Montana接触运动学在处理滚动接触时的几何本质。最后，我们将目光投向最前沿的接触隐式模型预测控制（Contact-Implicit MPC），揭示其如何通过数学松弛技术解决非平滑动力学难题。

这不仅是一份技术报告，更是一条从“几何约束”到“力学顺应”，再到“优化决策”的思想演进链条（Problem-Solution Chain）。

> [!note] 入门直觉：控制理论为什么是工程共同语言
> 本段整合自 `MergeBuffer/HoverNotes/Untitl.md` 的控制理论入门笔记。控制系统的最小定义是：**选择输入，使系统未来状态趋向期望状态**。这同一件事同时出现在开关电源的电压调节、自动增益控制、机械隔振、建筑阻尼、机器人装配线 PID、飞机颤振抑制中。
>
> - **开环控制**：输入不依赖输出，例如固定油门位置或固定清洗时间；环境变化（上坡、负载变化、餐具脏污程度）会直接造成输出漂移。
> - **闭环控制**：传感器测量输出，与参考信号比较得到误差，再由控制器调整输入；这就是负反馈，也是 [[SignalProcessing|状态估计]]、[[Dynamics|动力学建模]] 与 [[Optimization|控制优化]] 汇合的接口。
> - **阻尼直觉**：手指触摸振动酒杯会让声响更快消失，因为你改变了系统的能量耗散路径。灵巧手接触物体时的阻抗控制，本质上也是在设计“该吸收多少能量、该反弹多少能量”。

------

## 2. 核心概念：灵巧操作的运动学与静力学基础

## 2. Core Concepts: Kinematics & Statics Foundations in Dexterous Manipulation

在深入控制算法之前，必须建立描述灵巧手与物体交互的数学基石。与传统的单臂抓取不同，灵巧操作涉及多指协调（Multi-fingered Coordination），这要求我们不仅关注单个指尖的运动，更要关注接触点力与运动在物体层面的映射关系。这种映射关系集中体现在两个核心矩阵上：**抓取矩阵（Grasp Matrix, $G$）** 与 **手雅可比矩阵（Hand Jacobian, $J_h$）**。这些概念的详细几何推导参见 [[ContactMechanics#2.3 接触雅可比矩阵 (Contact Jacobian)|接触雅可比矩阵]]。

### 2.1 虚功原理与对偶性 (Virtual Work Principle & Duality)

在机器人力学中，最深刻的洞察之一是力与运动空间的**对偶性（Duality）**。这种对偶性源于虚功原理（Principle of Virtual Work）：在一个静态平衡系统中，所有外力在虚位移上所做的虚功之和为零。

对于灵巧手抓取系统，我们定义两个空间：

1. **关节空间（Joint Space）**：由关节位置 $q$、关节速度 $\dot{q}$ 和关节力矩 $\tau$ 组成。
2. **接触空间（Contact Space）**：由接触点的笛卡尔速度 $v_c$ 和接触力 $f_c$ 组成。
3. **物体空间（Object Space）**：由物体的位姿 $x_o$、速度 $v_o$ 和合外力（Wrench）$F_o$ 组成。

数学上，这种对偶性表现为雅可比矩阵的转置关系。如果一个矩阵 $A$ 将速度从空间 $X$ 映射到空间 $Y$（即 $v_y = A v_x$），那么其转置 $A^T$ 必然将力从空间 $Y$ 映射回空间 $X$（即 $f_x = A^T f_y$）。这一性质是理解抓取矩阵和手雅可比矩阵物理意义的关键 。

### 2.2 手雅可比矩阵：从关节到接触 (Hand Jacobian: From Joints to Contacts)

**手雅可比矩阵（Hand Jacobian, $J_h$）**描述了机械手关节空间的广义速度如何传递到指尖接触点的笛卡尔空间。对于一个拥有 $n_q$ 个关节的灵巧手，假设其与物体有 $k$ 个接触点。

$$J_h \in \mathbb{R}^{n' \times n_q}$$

其中 $n'$ 是所有接触点约束维度的总和。

- 对于点接触（Point Contact without Friction），每个接触点约束 1 个法向自由度。
- 对于硬指接触（Hard Finger, Point Contact with Friction），每个接触点约束 3 个平移自由度。
- 对于软指接触（Soft Finger），每个接触点约束 3 个平移 + 1 个法向扭转自由度。

**物理意义深度剖析：**

$J_h$ 的每一行实际上代表了一个螺旋（Screw）轴在空间中的分布。当我们将关节速度 $\dot{q}$ 左乘 $J_h$ 时，得到的是接触点在接触坐标系下的扭转（Twist）。

更重要的是其逆向物理意义：$J_h^T$ 将接触点受到的力映射回关节空间的负载力矩：

$$\tau = J_h^T f_{contact}$$

这意味着，如果 $J_h$ 在某个位姿下奇异（秩亏），机械手将失去在某些方向上施加力或产生运动的能力。这直接影响了操作的**可操作度（Manipulability）**。在灵巧操作规划中，我们通常希望最大化 $\sqrt{\det(J_h J_h^T)}$ 以远离奇异位形 。

### 2.3 抓取矩阵：从接触到物体 (Grasp Matrix: From Contacts to Object)

**抓取矩阵（Grasp Matrix, $G$）** 是灵巧操作的另一个核心支柱。它描述了施加在各个接触点上的局部力 $f_c$ 如何合成作用在物体质心上的合外力（Wrench, $F_o$）。

$$F_o = G f_c$$

$$G \in \mathbb{R}^{n \times n'}$$

其中 $n$ 是物体的自由度（平面为3，空间为6）。

**矩阵构造与物理洞察：**

$G$ 的列向量由每个接触点的**Plücker坐标**组成。对于第 $i$ 个接触点，其在物体坐标系中的位置为 $r_i$，接触力方向基向量为 $B_i$（取决于接触模型）。

$$G_i = \begin{bmatrix} R_i B_i \\ S(r_i) R_i B_i \end{bmatrix}$$

这里 $S(r_i)$ 是位置向量 $r_i$ 的反对称矩阵（Skew-symmetric matrix），用于计算力臂产生的力矩。

**从力到运动的对偶性：**

如果 $G$ 将接触力映射为物体力，那么 $G^T$ 必然描述了物体运动如何引起接触点的运动：

$$v_{contact} = G^T v_{object}$$

这个公式的物理含义极其深刻且常被忽视：它定义了**约束的一致性**。如果物体以速度 $v_{object}$ 运动，为了保持接触不分离且不穿透（Rigid Contact Assumption），接触点必须具备 $G^T v_{object}$ 的速度。如果手指实际速度与此不符，就会发生滑移（Sliding）或物理形变（Deformation）。

| **矩阵**           | **维度**        | **正向映射 (Forward Mapping)**                | **逆向/转置映射 (Transpose Mapping)**      | **物理本质** |
| ------------------ | --------------- | --------------------------------------------- | ------------------------------------------ | ------------ |
| **手雅可比 $J_h$** | $n' \times n_q$ | 关节速度 $\to$ 接触速度 ($v_c = J_h \dot{q}$) | 接触力 $\to$ 关节力矩 ($\tau = J_h^T f_c$) | 机构传动特性 |
| **抓取矩阵 $G$**   | $n \times n'$   | 接触力 $\to$ 物体力 ($F_o = G f_c$)           | 物体速度 $\to$ 接触速度 ($v_c = G^T v_o$)  | 物体几何约束 |

### 2.4 代码实现：空间抓取矩阵的构建

以下C++代码展示了如何利用Eigen库构建空间抓取矩阵，体现了上述理论的工程落地。

C++

```
/**
 * @file GraspMatrix.cpp
 * @brief Implementation of Grasp Matrix calculation for Spatial Hard Finger contacts.
 * Uses Eigen for linear algebra operations.
 */

#include <Eigen/Dense>
#include <vector>
#include <iostream>

using namespace Eigen;

class GraspMatrixCalculator {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    GraspMatrixCalculator(const Vector3d& center_of_mass) 
        : com_(center_of_mass) {}

    /**
     * @brief Computes the skew-symmetric matrix for cross product.
     * S(v) * u = v x u
     */
    Matrix3d skewSymmetric(const Vector3d& v) {
        Matrix3d S;
        S << 0, -v(2), v(1),
             v(2), 0, -v(0),
             -v(1), v(0), 0;
        return S;
    }

    /**
     * @brief Adds a Hard Finger (Point contact with friction) contact.
     * Hard Finger transmits 3 forces, 0 moments.
     * 
     * @param contact_point The position of contact in world frame.
     * @param contact_normal The inward normal of the contact surface.
     * @return MatrixXd The 6x3 partial grasp matrix for this contact.
     */
    MatrixXd computePartialGraspMatrix(const Vector3d& contact_point) {
        // Vector from COM to contact point
        Vector3d r = contact_point - com_;
        
        // For a hard finger contact, forces can be applied in any 3D direction.
        // The local contact frame usually aligns with normal/tangents, but 
        // the Grasp Matrix maps the 3D force vector directly to the object frame.
        // Assuming the contact force is already expressed in the object frame (or world frame).
        
        // G_i = [ I_3 ]  <- Force part: Force translates directly
        //        <- Moment part: Torque = r x F
        
        MatrixXd G_i(6, 3);
        G_i.block<3, 3>(0, 0) = Matrix3d::Identity();
        G_i.block<3, 3>(3, 0) = skewSymmetric(r);
        
        return G_i;
    }

    /**
     * @brief Assembles the full Grasp Matrix G.
     */
    MatrixXd buildFullGraspMatrix(const std::vector<Vector3d>& contact_points) {
        int n_contacts = contact_points.size();
        MatrixXd G(6, 3 * n_contacts);
        
        for(int i=0; i<n_contacts; ++i) {
            G.block<6, 3>(0, 3*i) = computePartialGraspMatrix(contact_points[i]);
        }
        return G;
    }

private:
    Vector3d com_;
};

int main() {
    Vector3d com(0, 0, 0);
    GraspMatrixCalculator calculator(com);
    
    std::vector<Vector3d> contacts;
    contacts.push_back(Vector3d(1, 0, 0));  // Finger 1
    contacts.push_back(Vector3d(-1, 0, 0)); // Finger 2
    
    MatrixXd G = calculator.buildFullGraspMatrix(contacts);
    
    std::cout << "Full Grasp Matrix G (" << G.rows() << "x" << G.cols() << "):\n" << G << std::endl;
    
    // Insight:
    // With two opposing fingers, check the rank. 
    // Rank < 6 means the grasp cannot resist all disturbances (not Force Closure).
    FullPivLU<MatrixXd> lu_decomp(G);
    std::cout << "Rank of G: " << lu_decomp.rank() << std::endl;
    
    return 0;
}
```

------

## 3. 技术演进：从刚性位置控制到柔顺力控制

## 3. Technical Evolution: From Rigid Position Control to Compliant Force Control

工业机器人的早期发展由**位置控制（Position Control）**主导。这种控制范式假设机器人是在自由空间中运动，没有任何环境接触。然而，当我们将应用场景转移到灵巧操作——如装配、打磨或擦拭——时，位置控制暴露出了其致命的缺陷。这一章节将深入分析这一从“刚”到“柔”的技术演变过程 。

### 3.1 问题链：刚度悖论与接触失效 (The Problem Chain: Stiffness Paradox & Contact Failure)

在经典的PID位置控制中，控制力矩 $\tau$ 与位置误差 $e = q_d - q$ 成正比：

$$\tau = K_p e + K_d \dot{e} + \tau_{gravity}$$

为了实现高精度的轨迹跟踪，工程师通常会将比例增益 $K_p$ 设得极高。这在自由运动中是有效的，但在接触任务中引发了**刚度悖论（Stiffness Paradox）**。

**深度物理分析：**

1. **环境误差的不可避免性：** 在现实世界中，环境的位置模型永远存在误差 $\delta x$。
2. **巨大的接触力：** 当机器人试图移动到一个被环境（如墙壁）占据的位置时，高增益控制器会将其视为位置误差。由于 $K_p$ 很大，控制器会输出极大的力 $F = K_p \delta x$ 试图消除误差。
3. **系统破坏：** 这种“不妥协”的行为会导致力迅速饱和，甚至损坏机械臂或物体。更严重的是，由于环境本身具有刚度 $K_e$，闭环系统的总刚度 $K_{total} \approx K_p + K_e$ 变得极大，导致系统自然频率升高，极易激发未建模的高频动力学（如齿轮箱柔性），引发剧烈的**接触不稳定性（Contact Instability）** 。


#### 3.1.1 从 PID 到计算力矩：精确线性化的诱惑与局限 (From PID to Computed Torque)

> [!note] 教科书参考
> 本节基于 Murray, Li & Sastry, *A Mathematical Introduction to Robotic Manipulation*, Chapter 4 §5.2-5.3 (Proposition 4.8)

PID 控制的一个直接改进思路是**计算力矩控制（Computed Torque Control, CTC）**，也称为反馈线性化（Feedback Linearization）。核心思想：用全状态反馈**精确消去所有非线性**。

$$\tau = M(q)\left[\ddot{q}_d - K_v \dot{e} - K_p e\right] + C(q, \dot{q})\dot{q} + N(q, \dot{q})$$

代入动力学方程后，由于 $M(q)$ 正定，误差动力学化简为**纯线性系统**：

$$\ddot{e} + K_v \dot{e} + K_p e = 0$$

**Proposition 4.8 (Murray)**：若 $K_p, K_v \in \mathbb{R}^{n \times n}$ 为对称正定矩阵，则上述控制律保证**指数级轨迹跟踪**。

**CTC 的结构分解**：

$$\tau = \underbrace{M(q)\ddot{q}_d + C\dot{q} + N}_{\tau_{ff} \text{ (前馈：补偿非线性)}} + \underbrace{M(q)(-K_v \dot{e} - K_p e)}_{\tau_{fb} \text{ (反馈：误差校正)}}$$

**为什么 CTC 不适合灵巧操作？**

1. **模型依赖性**：CTC 需要精确的 $M(q)$、$C(q,\dot{q})$、$N(q,\dot{q})$。模型误差 $\Delta M$ 导致线性化不完全，残余非线性引发性能退化（详见 §7 鲁棒控制）。在高动态非紧握任务中（如 [[Dynamic Non-Prehensile Manipulation]]），接触切换导致动力学剧变，使模型误差尤为严重。
2. **环境交互的缺失**：CTC 将 $F_{ext}$ 视为扰动并试图消除。但在灵巧操作中，接触力 $F_{ext}$ 是任务的核心——我们需要**调节**与环境的交互，而非**消除**它。
3. **PD 的本质局限**：PD 控制 $\tau = -K_v \dot{e} - K_p e$ 是 CTC 的"穷人版本"——没有前馈项 $\tau_{ff}$。Murray 明确指出：*"PD 控制永远无法实现非平凡轨迹的精确跟踪。"* 这解释了 [[Dynamic Non-Prehensile Manipulation|DNPM]] 项目中的现象：PD 将位置目标转化为力矩，但力矩 pattern 受限于固定 $K_p, K_d$，无法表达动态任务所需的**时变刚度**。

> [!warning] 实验证据：$K_p$ 对灵巧操作成功率的极端敏感性（DNPM 历史数据 + Exp2, 2026-02）
> 在 [[Dynamic Non-Prehensile Manipulation|DNPM]] 的 TP (Triangle Pass) 任务中，100+ 组历史实验的 $K_p$ 网格搜索显示：
>
> - **最优 $K_p$ 区间 = 3.5 ~ 8.5**，区间外性能急剧衰退
> - $K_p$ 过低（< 3）：力矩不足，无法驱动笔完成翻转
> - $K_p$ 过高（> 10）：系统"僵硬"，接触阶段无法顺从，导致笔弹飞
> - 最优 $K_d$ 尚未独立搜索（当前与 $K_p$ 耦合）
>
> **理论意义**：
> 1. 窄最优区间（~2.4× 范围）证实了"刚度悖论"在灵巧操作中的严重性 — 固定 $K_p$ 无法同时满足运动相和接触相的需求
> 2. 不同操作相位（snap vs spin vs release）可能各自有最优 $K_p$，但全局固定值只能折中  — 这正是 [[Idea-001-Phase-Adaptive Impedance|PAI]] 相位自适应阻抗的核心动机
> 3. Exp2 最优基线 TP Medium TWC SR=0.86（$K_p$ 在最优区间内）为后续变阻抗实验提供了对照

> [!tip] 与 DNPM 项目的直接联系
> DNPM ideas.md §3.1 观察到"实际关节位置几乎不动，$q_{target}$ 变化主要被 PD 转化为力矩"。从 CTC 视角看，策略在用 PD 近似力矩控制，但**缺失了前馈项和时变增益**。这正是方向 A（变阻抗 / [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]] 参考模型跟踪）的理论动机来源。

**演进逻辑**：PID 在接触时失稳 → CTC 消除非线性但忽略环境交互 → 需要一种能**主动调节机器人与环境交互动态关系**的控制范式 → **阻抗控制**。

### 3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系

**Hogan** 提出的阻抗控制并不是直接控制力或位置，而是控制力与位置之间的**动态关系（Dynamic Relationship）** 。

其核心思想是将机器人“伪装”成一个质量-弹簧-阻尼系统（Mass-Spring-Damper System）。目标动力学方程为：

$$M_d (\ddot{x} - \ddot{x}_d) + B_d (\dot{x} - \dot{x}_d) + K_d (x - x_d) = F_{ext}$$

其中 $M_d, B_d, K_d$ 是我们期望机器人表现出的惯量、阻尼和刚度矩阵。

**因果性洞察 (Causality Insight):**

阻抗控制采用了**阻抗因果性（Impedance Causality）**：

- **输入**：位移（环境推动机器人）

- **输出**：力（机器人回弹）

- **物理本质**：$F = Z(x)$。

  这使得阻抗控制在与**刚性环境**（Stiff Environment）交互时非常稳定。因为环境通常表现为导纳（Admittance，输入力，输出位移），两个物理系统的耦合应当是“阻抗+导纳”，而非“阻抗+阻抗”或“导纳+导纳”。
> [!note] 被动性与稳定性证明 (Passivity-Based Stability)
> 阻抗控制的稳定性可以通过**被动性理论 (Passivity Theory)** 严格证明。定义能量储存函数（Lyapunov Candidate）：
> 
> $$V = \frac{1}{2}\tilde{x}^T K_d \tilde{x} + \frac{1}{2}\dot{\tilde{x}}^T M_d \dot{\tilde{x}}$$
> 
> 其中 $\tilde{x} = x - x_d$ 为位置误差。对 $V$ 求导：
> 
> $$\dot{V} = \dot{\tilde{x}}^T (K_d \tilde{x} + M_d \ddot{\tilde{x}}) = \dot{\tilde{x}}^T (F_{ext} - B_d \dot{\tilde{x}}) = \dot{\tilde{x}}^T F_{ext} - \dot{\tilde{x}}^T B_d \dot{\tilde{x}}$$
> 
> **关键结论**：当无外力 $F_{ext} = 0$ 时，$\dot{V} = -\dot{\tilde{x}}^T B_d \dot{\tilde{x}} \leq 0$（负半定）。由 LaSalle 不变原理，系统渐近稳定收敛至 $\tilde{x} = 0$。
> 
> **物理意义**：阻尼矩阵 $B_d$ 耗散能量。只要 $B_d > 0$，系统就像一个"漏气"的气球，无论初始状态如何，最终都会回归平衡点。这是阻抗控制在接触任务中天然稳定的**数学保证**。

> [!abstract] 价值函数即 Lyapunov 函数 (来自 [[Safe Model-based Reinforcement Learning with Stability Guarantees]])
> 一个深刻的洞见是：**RL 中的价值函数天然是 Lyapunov 函数**。
> 
> 对于严格正定的代价函数 $r(x, u) > 0$（除原点外）且 $r(0, 0) = 0$，价值函数定义为：
> $$V^\pi(x) = r(x, \pi(x)) + V^\pi(f(x, \pi(x)))$$
> 
> 重排后：
> $$V^\pi(f(x, \pi(x))) = V^\pi(x) - r(x, \pi(x)) < V^\pi(x)$$
> 
> 这恰好满足 Lyapunov 下降条件！因此：
> - **价值函数**定义了系统的**吸引域 (Region of Attraction)**
> - **策略优化**等价于**扩大吸引域**
> - 这为 Safe RL 提供了控制理论的数学基础

> [!tip] 通过网络结构实现稳定性 (来自 [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]])
> 另一种将 Lyapunov 稳定性融入 RL 的方法是**结构约束**而非软惩罚。
> 
> **核心定理**：对于摇摆方程等系统，若控制器 $u(\omega)$ 满足：
> 1. **单调递增**：$\omega_1 > \omega_2 \Rightarrow u(\omega_1) > u(\omega_2)$
> 2. **过原点**：$u(0) = 0$
> 
> 则系统存在唯一平衡点且**局部指数稳定**。
> 
> **实现方式**：Stacked-ReLU 网络
> $$u(\omega) = \sum_{k=1}^K \alpha_k \cdot \text{ReLU}(\omega - \beta_k), \quad \alpha_k > 0$$
> 
> 正系数确保单调性，偏置选择确保过原点。这是将物理先验（无源性条件 $\omega \cdot u(\omega) \geq 0$）直接编码进网络架构的范例。

> [!abstract] 可达性分析与最大可行集（来自 [[Reachability Constrained Reinforcement Learning]]）
> **核心问题**：传统约束 RL 使用期望累积代价 $\mathbb{E}[\sum_t \gamma^t c(s_t)] \leq \epsilon$，但这可能在期望安全的同时**单步违约**。
> 
> **可达性视角**：定义**安全价值函数**：
> $$V_c^{\max}(s) = \max_{\pi} \mathbb{E}\left[\max_{t \geq 0} \gamma^t c(s_t) \mid s_0 = s\right]$$
> 
> 这捕捉的是"从状态 $s$ 出发，最坏情况下能遇到的最大代价"。
> 
> **最大可行集定义**：
> $$\mathcal{F} = \{s : V_c^{\max}(s) \leq d\}$$
> 
> 其中 $d$ 是安全阈值。$\mathcal{F}$ 是**理论上最大的可控不变集**——只要留在 $\mathcal{F}$ 内，就永远能保持安全。
> 
> **对比 CBF**：
> | | Control Barrier Function | RCRL 可达性 |
> |---|---|---|
> | 可行集 | 保守估计（可能过小） | 最大理论可行集 |
> | 计算 | 需要手工设计 $h(x)$ | 学习 $V_c^{\max}$ |
> | 性能牺牲 | 可能较大 | 最小化 |
> 
> **灵巧操作启示**：在高速 in-hand manipulation 中，RCRL 的"最大可行集"可以允许更激进的动作，只要能保证"最终能稳住"。

> [!abstract] 数据驱动阻抗辨识（来自 [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Prosthesis VI]]）
> **问题**：传统阻抗控制需要手工调节 $K$, $B$, $\theta_{eq}$ 参数，耗时且难以适应任务变化。
> 
> **解决方案**：将阻抗参数建模为**相位、任务变量的连续函数**：
> $$K(\phi, v, \alpha) = \sum_{i,j,k} c^K_{ijk} B_i(\phi) P_j(v) P_k(\alpha)$$
> 
> 其中 $B_i$ 是 B-spline 基函数，$P_j$, $P_k$ 是多项式基。
> 
> **凸优化关键洞察**：固定平衡角 $\theta_{eq}$ 时，力矩误差关于 $K$, $B$ 是**线性**的！
> $$\tau = -K(\theta - \theta_{eq}) - B\dot{\theta} \quad \Rightarrow \quad \tau = \Phi(\theta, \dot{\theta}, \phi, v, \alpha) \cdot c$$
> 
> **两步凸优化**：
> 1. 先从运动学数据估计 $\theta_{eq}(\phi, v, \alpha)$
> 2. 再凸优化 $K$, $B$ 的系数（保证全局最优）
> 
> **灵巧操作启发**：用人类操作演示替代健康人步态数据，可学习手指刚度如何随操作相位/物体属性变化。

> [!tip] 可变阻抗作为 RL 动作空间（来自 [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]]）
> **核心创新**：让 RL 策略直接输出阻抗参数，而非底层力矩/位置。
> 
> **VICES 动作空间**：
> $$a = (\Delta x, K_{\text{diag}})$$
> - $\Delta x \in \mathbb{R}^6$：末端位姿增量
> - $K_{\text{diag}} \in \mathbb{R}^6$：对角刚度增益
> 
> **任务适应性**：
> | 任务类型 | 刚度配置 |
> |---------|----------|
> | 自由运动 | 高刚度（精确跟踪） |
> | 门把手操作 | 约束方向低刚度 |
> | 表面擦拭 | 法向低刚度 + 切向高刚度 |
> 
> **理论优势**：
> 1. **解耦**：任务学习与底层动力学补偿分离
> 2. **迁移性**：策略可迁移到不同机器人（同样的"软/硬"语义）
> 3. **安全性**：低刚度设置自然限制接触力

> [!abstract] 阻抗参考模型跟踪：从"控制阻抗"到"跟踪阻抗轨迹"（来自 [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]）
> **核心创新**：不直接让 RL 输出阻抗参数，而是让 RL 策略**跟踪一个虚拟阻抗参考模型生成的轨迹**。
> 
> **参考模型动力学**：
> $$m\ddot{x}_{ref} = K_p(x_{des} - x_{ref}) + K_d(\dot{x}_{des} - \dot{x}_{ref}) + f_{ext}$$
> 
> RL 策略和参考模型都经历相同的外力 $f_{ext}$，但参考模型额外受虚拟弹簧力约束。训练目标是让 $x_{sim} \approx x_{ref}$。
> 
> **统一控制接口** $(x_{des}, K_p, K_d)$：
> - $K_p = 0$：机器人零抗力被牵着走（运动学示教）
> - $K_p$ 中等：柔顺跟随（碰撞冲击降低 80%）
> - $K_p$ 高：精确定位或大力拖拽
> 
> **时间平滑技术**：混合从不同历史时刻积分的参考轨迹，平衡开环精度和闭环适应性：
> $$r_t = \frac{1}{M}\sum_{t'} \exp(-\|x_{sim}(t) - x^{t'}_{ref}(t)\|^2) + \exp(-\|\dot{x}_{sim}(t) - \dot{x}^{t'}_{ref}(t)\|^2)$$
> 
> **与 VICES 的关键区别**：
> | | VICES | FACET |
> |---|---|---|
> | RL 输出 | $(\Delta x, K)$ 直接作为阻抗参数 | $(x_{des}, K_p, K_d)$ 作为参考模型输入 |
> | 跟踪目标 | 静态平衡点 | **动态参考轨迹** |
> | 力自适应 | 通过低刚度被动顺从 | 通过参考模型**主动响应** $f_{ext}$ |
> | 适用场景 | 接触丰富操作 | 大冲击/力自适应 + 操作 |
> 
> **灵巧操作启发**：
> 1. 为每个手指/关节定义独立阻抗参考模型 → 实现关节级时变阻抗
> 2. 在动态非紧握操作中：snap 阶段高 $K_p$（发力）→ 旋转阶段低 $K_p$（柔顺滑动）→ catch 阶段中 $K_p$（精确接住）
> 3. 多体扩展：arm 和 hand 分别定义参考模型，通过力传导参数 $a \in [0,1]$ 控制耦合程度

> [!note] 教科书参考
> Control Barrier Function 理论源自 Ames et al. (2017) 和控制理论经典文献。
> 参考 [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints|LatentCBF 论文]] 的数学背景部分。

> [!important] Control Barrier Function (CBF) 形式化定义
> **CBF 是 Lyapunov 方法在安全约束上的对偶**——Lyapunov 保证稳定性（吸引到目标），CBF 保证安全性（不进入危险集）。
> 
> #### 安全集与屏障函数
> 
> **安全集定义**：设连续可微函数 $h: \mathbb{R}^n \to \mathbb{R}$，定义安全集：
> $$\mathcal{C} = \{x \in \mathbb{R}^n : h(x) \geq 0\}$$
> 
> 其中 $h(x) > 0$ 在安全集内部，$h(x) = 0$ 在边界，$h(x) < 0$ 在危险区域。
> 
> #### Control Barrier Function 定义
> 
> 对于控制仿射系统 $\dot{x} = f(x) + g(x)u$，函数 $h(x)$ 是 **Control Barrier Function** 当且仅当存在扩展类 $\mathcal{K}_\infty$ 函数 $\alpha$ 使得：
> 
> $$\sup_{u \in \mathcal{U}} \left[ L_f h(x) + L_g h(x) \cdot u \right] \geq -\alpha(h(x)), \quad \forall x \in \mathcal{C}$$
> 
> 其中 $L_f h = \nabla h \cdot f$ 和 $L_g h = \nabla h \cdot g$ 是 Lie 导数。
> 
> #### CBF-QP 安全滤波器
> 
> 给定名义控制器 $u^{\text{nom}}$，CBF 安全过滤求解：
> 
> $$u^* = \argmin_{u \in \mathcal{U}} \|u - u^{\text{nom}}\|^2$$
> $$\text{s.t.} \quad L_f h(x) + L_g h(x) \cdot u \geq -\alpha(h(x))$$
> 
> 这是一个 **QP (Quadratic Program)**，可实时求解。
> 
> #### CBF 与 Lyapunov 的对偶性
> 
> | | Lyapunov (CLF) | Barrier (CBF) |
> |---|---|---|
> | 保证 | 收敛到目标 | 永不进入危险 |
> | 不变集 | 吸引域 | 安全集 $\mathcal{C}$ |
> | 约束 | $\dot{V} \leq -\alpha(V)$ | $\dot{h} \geq -\alpha(h)$ |
> | 方向 | 能量下降 | 屏障函数上升/不下降 |
> 
> #### Hamilton-Jacobi 可达性与 CBF 的联系
> 
> HJ 可达性分析求解值函数：
> $$V(x, t) = \min_u \max_d \left[ \ell(x) + \int_t^T L(x, u, d) ds \right]$$
> 
> 其中 $\ell(x)$ 是边界代价（margin function）。零等值面 $V(x) = 0$ 定义了**后向可达管道**的边界。
> 
> **关键洞察**（来自 LatentCBF）：
> - 值函数的光滑性**线性依赖**于 margin function 的光滑性
> - 分类器作为 margin function 会导致梯度饱和，CBF 无法区分动作安全性
> - WGAN 梯度惩罚可学习光滑 margin function
> 
> **灵巧操作应用**：在手内操作中，安全约束可定义为"不掉落物体"——但这难以解析表达。LatentCBF 在 world model 的潜空间中学习 CBF，无需显式状态表示。

### 3.3 解决方案 II：导纳控制 (Admittance Control) —— 位置内环的策略

与阻抗控制相反，导纳控制采用**导纳因果性（Admittance Causality）** 。

- **输入**：力（通过力传感器测量）
- **输出**：位移（机器人运动）
- **物理本质**：$x = Y(F)$。

**工作机理：**

导纳控制器首先根据测量的力 $F_{meas}$ 和目标导纳模型，计算出机器人“应该”处于的位置 $x_{ref}$，然后将这个 $x_{ref}$ 发送给底层的刚性位置控制器去执行。

$$M_d \ddot{x}_{ref} + B_d \dot{x}_{ref} + K_d x_{ref} = F_{meas}$$

**对比与选择 (Comparison & Selection):**

| **特性**       | **阻抗控制 (Impedance)**                          | **导纳控制 (Admittance)**                  |
| -------------- | ------------------------------------------------- | ------------------------------------------ |
| **底层控制环** | 力矩控制 (Torque Control)                         | 位置/速度控制 (Position/Velocity Control)  |
| **硬件要求**   | 直驱/准直驱电机，低摩擦 (e.g., Franka, KUKA iiwa)（参见 [[传动#3. 直驱 (Direct Drive)|直驱]] / [[传动#4. 准直驱 (Quasi-Direct Drive, QDD)|QDD]]） | 通用工业机器人，高减速比 (e.g., UR, Fanuc)（参见 [[减速器]]） |
| **适应环境**   | 刚性环境 (Stiff Environment)                      | 自由空间或柔性环境 (Soft Environment)      |
| **劣势**       | 在自由空间的位置精度受摩擦力影响大                | 与刚性环境接触时容易发生接触不稳定性       |

**深度见解 (Deep Insight):**

导纳控制实际上是在“硬”的位置环外包了一层“软”的力环。其最大的风险在于**接触不稳定性**。当环境很硬时，极小的位移会导致巨大的力变化。如果导纳参数 $M_d, B_d$ 设定不当，测量到的力突变会导致 $x_{ref}$ 剧烈波动，而底层的刚性位置环会忠实地执行这个波动，导致系统像锤子一样反复敲击表面。因此，导纳控制在接触刚性表面时必须非常小心地调节参数。

### 3.4 解决方案 III：统一阻抗与导纳架构 (Unified Architecture)

为了结合两者的优点，**统一阻抗与导纳控制（Unified Impedance and Admittance Control）**架构被提出 。该架构通过一个混合系统（Hybrid System）框架，允许控制器在阻抗因果性和导纳因果性之间连续切换或插值。

> [!tip] 多速率控制与强化学习（来自 [[Reinforcement Learning for Control with Multiple Frequencies|AP-AC]]）
> 在机器人系统中，不同变量有不同的**自然时间尺度**：
> - **关节力矩**：需要高频控制（~1kHz）以维持稳定
> - **抓手开合**：低频即可（~10Hz）
> - **运动规划**：更低频（~1Hz）
> 
> **问题**：标准 RL 假设单一控制频率，强制高频控制 → 轨迹过长 → 探索低效。
> 
> **AP-AC 解决方案**：引入**周期性非平稳策略**：
> $$\pi(a|s, t) = \prod_{j=1}^{m} \pi_j(a^j | s, t \mod T_j)$$
> 
> 其中 $T_j$ 是第 $j$ 个动作变量的持续周期。每个变量按自己的节奏更新，形成**多速率采样系统**。
> 
> **灵巧操作应用**：
> - 手臂末端位置：中频控制（50Hz）
> - 手指关节：高频控制（500Hz）
> - 抓握力参考：低频调整（10Hz）

**机制：**

引入一个占空比参数 $\alpha \in $ 或切换逻辑。

- 在接触刚性环境时，倾向于阻抗模式（$\alpha \to 1$），利用力矩控制的自然顺应性。
- 在自由运动或接触软环境时，倾向于导纳模式（$\alpha \to 0$），利用位置控制的高精度。
- **平滑过渡：** 关键在于保证切换瞬间的状态连续性，通过特定的状态映射矩阵 $S_1, S_2$ 计算过渡状态下的 $x_d$ 和 $\dot{x}_d$，防止控制量的跳变。

------

## 4. 操作空间公式化 (Operational Space Formulation)

## 4. Operational Space Formulation (OSF)

斯坦福大学的 Oussama Khatib 教授提出的**操作空间公式化 (OSF)** 是灵巧操作控制理论的分水岭 。在此之前，机器人控制主要在关节空间（Joint Space）进行。OSF 的革命性在于：它不仅将运动学投影到任务空间，更是将**动力学（Dynamics）**直接投影到任务空间，实现了真正的动态解耦。

### 4.1 动力学投影与解耦 (Dynamic Projection & Decoupling)

考虑关节空间动力学方程：

$$M(q)\ddot{q} + b(q, \dot{q}) + g(q) = \tau$$

其中 $M(q)$ 是关节惯量矩阵，$b(q, \dot{q})$ 包含科里奥利力与离心力，$g(q)$ 是重力项。

我们希望控制末端执行器在笛卡尔空间的行为，其动力学形式为：

$$\Lambda(q) \ddot{x} + \mu(q, \dot{q}) \dot{x} + p(q) = F_{op}$$

**核心推导 (Derivation):**

利用雅可比关系 $\dot{x} = J\dot{q}$ 和 $\ddot{x} = J\ddot{q} + \dot{J}\dot{q}$，我们可以推导出操作空间参数与关节空间参数的精确映射：

1. **操作空间惯量矩阵 (Operational Space Inertia Matrix, $\Lambda$):**

   $$\Lambda(q) = (J(q) M^{-1}(q) J^T(q))^{-1}$$

   **物理意义：** $\Lambda(q)$ 代表了末端执行器在笛卡尔空间各个方向上感受到的“等效质量”。它不仅取决于机器人的质量分布，还取决于当前的姿态。在奇异点附近，$\Lambda$ 的某些分量会趋于无穷大（因为 $J$ 秩亏，$J M^{-1} J^T$ 不可逆），意味着在奇异方向上无法产生加速度。

2. **操作空间离心力/科里奥利力 ($\mu$) 与重力 ($p$):**

   $$\mu(q, \dot{q}) = \Lambda(q) J(q) M^{-1}(q) b(q, \dot{q}) - \Lambda(q) \dot{J}(q) \dot{q}$$

   $$p(q) = \Lambda(q) J(q) M^{-1}(q) g(q)$$

### 4.2 动态一致性广义逆 (Dynamically Consistent Generalized Inverse)

在冗余自由度系统（$n > m$）中，从操作空间力 $F_{op}$ 反解关节力矩 $\tau$ 存在无穷多解。传统的伪逆 $J^\dagger = J^T(JJ^T)^{-1}$ 虽然最小化了关节力矩的范数，但它没有考虑机械臂的物理质量分布。

Khatib 引入了**动态一致性广义逆 ($\bar{J}$)** ：

$$\bar{J}(q) = M^{-1}(q) J^T(q) \Lambda(q)$$

或者展开形式：

$$\bar{J} = M^{-1} J^T (J M^{-1} J^T)^{-1}$$

**深刻洞察 (Deep Insight):**

$\bar{J}$ 的构造中包含了 $M^{-1}$，这意味着它在分配任务时，会自动“惩罚”那些大惯量的关节。

- **直观理解：** 如果你想让指尖快速移动，算法会倾向于驱动手指和手腕等轻量级关节，而不是驱动沉重的肩部或基座。
- **解耦特性：** 通过 $\bar{J}$ 计算出的关节力矩 $\tau = J^T F_{op}$ 能够保证末端产生的加速度正是 $\ddot{x} = M^{-1} \tau$ 在任务空间的投影，没有任何多余的耦合分量干扰。

### 4.3 零空间控制与多任务优先级 (Null Space Control & Task Prioritization)

利用 $\bar{J}$，我们可以定义唯一的**动态一致性零空间投影矩阵 (Null Space Projection Matrix, $N$)** ：

$$N(q) = I - \bar{J}(q) J(q)$$

控制律变为：

$$\tau = J^T(q) F_{task} + N^T(q) \tau_{null}$$

**物理意义分析：**

- **主任务 ($F_{task}$):** 负责执行末端操作（如写字）。
- **零空间任务 ($\tau_{null}$):** 在不干扰主任务的前提下执行次级目标。
- **正交性：** 这里的“不干扰”是指**动态不干扰**。由于 $J M^{-1} N^T = 0$，这意味着 $\tau_{null}$ 产生的关节加速度在映射回操作空间时为零加速度。这是比运动学零空间（只保证速度为零）更强的保证。

**应用场景：**

1. **避障：** 在抓取物体的同时，利用手肘避开障碍物。
2. **奇异回避：** 调整构型以最大化可操作度。
3. **姿态优化：** 在保持指尖位置不变的情况下，调整手掌姿态以获得更有利的抓取角度。

### 4.4 代码实现：动态一致性逆与零空间投影

以下C++代码实现了上述核心算法，展示了如何在实时控制循环中计算 $\bar{J}$ 和 $N$。

C++

```
/**
 * @file OSFController.cpp
 * @brief Implementation of Operational Space Formulation core components.
 * Computes Lambda, J_bar, and Null Space Projector N.
 */

#include <Eigen/Dense>
#include <iostream>

using namespace Eigen;

class OperationalSpaceDynamics {
public:
    EIGEN_MAKE_ALIGNED_OPERATOR_NEW

    /**
     * @brief Computes the Operational Space Inertia Matrix Lambda.
     * Lambda = (J * M^-1 * J^T)^-1
     * 
     * @param J Jacobian matrix (m x n)
     * @param M Joint Space Inertia Matrix (n x n)
     * @return MatrixXd Lambda (m x m)
     */
    MatrixXd computeLambda(const MatrixXd& J, const MatrixXd& M) {
        // Efficient computation using LLT decomposition for SPD matrices
        // In practice, M is always symmetric positive definite.
        
        // Step 1: Compute M_inv
        // For large n, utilize specific solvers, but explicit inverse shown for clarity.
        MatrixXd M_inv = M.inverse();
        
        // Step 2: Compute J * M_inv * J^T
        MatrixXd JMInvJT = J * M_inv * J.transpose();
        
        // Step 3: Compute Lambda = (JMInvJT)^-1
        // Adding small damping for numerical stability near singularities
        double damping = 1e-4;
        JMInvJT += damping * MatrixXd::Identity(J.rows(), J.rows());
        
        return JMInvJT.inverse();
    }

    /**
     * @brief Computes the Dynamically Consistent Generalized Inverse J_bar.
     * J_bar = M^-1 * J^T * Lambda
     */
    MatrixXd computeJBar(const MatrixXd& J, const MatrixXd& M, const MatrixXd& Lambda) {
        MatrixXd M_inv = M.inverse();
        return M_inv * J.transpose() * Lambda;
    }

    /**
     * @brief Computes the Null Space Projection Matrix N.
     * N = I - J_bar * J
     */
    MatrixXd computeNullSpaceProjector(const MatrixXd& J, const MatrixXd& J_bar, int n_dof) {
        MatrixXd I = MatrixXd::Identity(n_dof, n_dof);
        return I - J_bar * J;
    }
};

int main() {
    int n = 7; // 7 DOF arm
    int m = 6; // 6D Task Space
    
    OperationalSpaceDynamics osf;
    
    // Mock data
    MatrixXd J = MatrixXd::Random(m, n);
    MatrixXd M = MatrixXd::Random(n, n);
    M = M * M.transpose() + 0.1 * MatrixXd::Identity(n, n); // Ensure SPD
    
    // 1. Compute Lambda
    MatrixXd Lambda = osf.computeLambda(J, M);
    std::cout << "Lambda:\n" << Lambda << "\n\n";
    
    // 2. Compute J_bar
    MatrixXd J_bar = osf.computeJBar(J, M, Lambda);
    std::cout << "J_bar:\n" << J_bar << "\n\n";
    
    // 3. Compute N
    MatrixXd N = osf.computeNullSpaceProjector(J, J_bar, n);
    std::cout << "Null Space Projector N:\n" << N << "\n\n";
    
    // Validation: J * N should be Zero matrix (Kinematically/Dynamically decoupled)
    std::cout << "Validation ||J * N||: " << (J * N).norm() << std::endl;
    
    return 0;
}
```

------

## 5. 力/位混合控制 (Hybrid Force/Position Control)

## 5. Hybrid Force/Position Control

虽然阻抗控制提供了一种稳定的交互方式，但在某些工业应用中，我们需要在特定方向上施加精确的力（例如恒力打磨），而在正交方向上严格跟踪位置（例如沿着复杂的曲线轨迹）。这种需求催生了**力/位混合控制（Hybrid Force/Position Control）** 。

### 5.1 正交分解原理与选择矩阵 (Orthogonal Decomposition & Selection Matrix)

混合控制的核心假设是：任何任务都可以分解为两个正交的子空间——**位置控制子空间**和**力控制子空间**。这种分解通过**选择矩阵 (Selection Matrix, $S$)** 来实现 。

在任务坐标系（Constraint Frame, $\{C\}$）中，定义对角矩阵 $S = \text{diag}(s_1,..., s_6)$，其中 $s_i \in \{0, 1\}$。

- $s_i = 1$：该方向被环境约束，需要进行**力控制**。
- $s_i = 0$：该方向自由运动，需要进行**位置控制**。

**典型案例：擦拭黑板 (Wiping a Blackboard)**

假设黑板法线方向为 $Z$ 轴，擦拭运动在 $X-Y$ 平面。

- $Z$ 轴：由于黑板是刚性的，位置被固定，必须控制压力。 -> $s_z = 1$
- $X, Y$ 轴：需要沿着板面移动。 -> $s_x = 0, s_y = 0$
- 旋转：通常要保持板擦贴合。 -> $s_{\theta x} = 1, s_{\theta y} = 1$

### 5.2 控制架构与不一致性挑战 (Architecture & Inconsistency Challenges)

混合控制律通常表示为：

$$\tau = J^T \left$$

其中 $u_{pos}$ 是位置控制器的输出（如PID计算出的加速度），$u_{force}$ 是力控制器的输出。

**技术瓶颈：几何不一致性 (Geometric Inconsistency)** 尽管 Mason 和 Raibert 的理论非常优雅，但在实际应用中，混合控制面临巨大的挑战，即**运动学不稳定性（Kinematic Instability）** 。 如果人为定义的选择矩阵 $S$ 对应的坐标系与环境真实的几何约束不完全对齐（例如，黑板是弯曲的，或者机器人估计的法线有 $5^\circ$ 的误差），那么：

1. **位置控制器**可能会在实际受限的方向上尝试运动，导致巨大的冲突力。
2. **力控制器**可能会在实际自由的方向上施加力，导致机器人意外加速飞出（Runaway）。

**现代解决方案：** 为了解决这一问题，现代研究转向了**自适应混合控制**或**并行力/位控制（Parallel Force/Position Control）**，甚至结合学习算法（Learning from Demonstration）来动态估计和调整选择矩阵 $S$ 的方向 。

------

## 6. 处理接触非线性：Montana 接触运动学

## 6. Handling Contact Nonlinearities: Montana's Contact Kinematics

在简单的抓取中，接触点通常被假定为固定的。但在高级灵巧操作（In-hand Manipulation）中，如手中转球，手指必须在物体表面**滚动（Rolling）**。这种滚动引入了高度非线性的几何约束，由微分几何描述。David Montana 在1988年推导出的接触运动学方程是该领域的黄金标准 。

### 6.1 局部几何描述 (Local Geometric Description)

定义接触状态 $q = (u_1, v_1, u_2, v_2, \psi)$。

- $(u_1, v_1)$：指尖表面的局部高斯坐标。
- $(u_2, v_2)$：物体表面的局部高斯坐标。
- $\psi$：接触角，即两个表面切平面坐标系之间的相对转角。

我们需要引入两个微分几何量：

1. **度量张量 (Metric Tensor, $M$)**：描述曲面上的微小距离如何映射到参数空间。$d s^2 = \dot{u}^T M \dot{u}$。
2. **曲率张量 (Curvature Form, $K$)**：描述曲面的弯曲程度。对于球体，曲率是常数；对于任意曲面，它是位置的函数。

### 6.2 Montana 方程：闭环形式 (The Contact Equations)

接触运动学方程建立了一阶微分关系，将**接触点的演化速度** ($\dot{u}, \dot{v}, \dot{\psi}$) 与物体间的**相对刚体速度** ($v_{rel}, \omega_{rel}$) 联系起来。

$$\begin{bmatrix} M_1 \dot{U}_1 \\ M_2 \dot{U}_2 \\ \dot{\psi} \end{bmatrix} =  \mathcal{H}^{-1} (K_1, K_2, \psi) \begin{bmatrix} v_{x} \\ v_{y} \\ \omega_{n} \end{bmatrix} $$

其中 $\mathcal{H}$ 是一个包含相对曲率 $(K_1 + R_\psi K_2 R_\psi^T)$ 的矩阵。

**物理洞察：相对曲率的决定性作用**

在纯滚动（$v_{x}=v_{y}=0$ at contact point）情形下，方程显示接触点在表面上的移动速度与相对曲率成反比。

$$\dot{U} \propto (K_{rel})^{-1} \omega_{rel}$$

这意味着：

- 如果两个物体曲率差别很大（如手指按在平桌上），滚动是稳定的，接触点移动速度适中。
- 如果两个物体曲率非常接近（如一个球在与其半径几乎相同的球窝里滚动），相对曲率接近零，接触点移动速度趋于无穷大。这种**自旋（Spinning）**现象在控制上极难处理，类似于奇异点，需要轨迹规划层予以规避。

### 6.3 非完整约束的控制含义 (Non-holonomic Implications)

纯滚动接触是经典的**非完整约束（Non-holonomic Constraint）** 。这意味着系统的状态（接触点位置）不能仅仅通过对控制输入（滚动速度）的简单代数关系求得，而必须依赖于路径积分。

- **后果：** 就像平行泊车一样，为了让手指从物体表面点 A 移动到点 B 而不发生滑动，我们不能直接直线移动，而可能需要执行复杂的、类似“S”形的机动轨迹（Lie Bracket motions）。这使得基于Montana方程的灵巧操作规划成为一个极具挑战的非线性控制问题。

------

## 7. 鲁棒控制：对抗模型不确定性

## 7. Robust Control: Combatting Model Uncertainty

在OSF和混合控制中，我们通常假设拥有完美的动力学模型 $M(q), b(q, \dot{q})$。然而，真实世界中充满了摩擦、未建模负载和传感器噪声。**计算力矩控制（Computed Torque Control, CTC）** 是一种基于精确线性化的方法，一旦模型存在误差 $\Delta M$，其实际性能会迅速退化，导致稳态误差 。

为了解决这一问题，**滑模控制（Sliding Mode Control, SMC）** 被引入灵巧操作领域。

### 7.1 滑模控制原理 (Principles of SMC)

SMC 的核心思想是将系统状态强行约束在一个设计的**滑模面（Sliding Surface, $s$）** 上。

定义滑模面为跟踪误差的函数：

$$s = \dot{e} + \lambda e = 0, \quad \lambda > 0$$

如果我们将状态保持在 $s=0$ 上，这就意味着 $\dot{e} = -\lambda e$，误差将以指数速率收敛到零，与系统具体的动力学参数无关。

控制律由两部分组成：

$$u = u_{eq} + u_{dis}$$

1. **等效控制 (Equivalent Control, $u_{eq}$)**：基于名义模型计算，用于维持 $s=0$。

2. **切换控制 (Switching Control, $u_{dis}$)**：用于处理不确定性。

   $$u_{dis} = -k \cdot \text{sgn}(s)$$

   只要增益 $k$ 大于模型不确定性的上界，系统就能保证稳定性。

### 7.2 抖振现象与边界层平滑 (Chattering & Boundary Layer)

**问题：** 理想的 SMC 需要以无限高的频率切换符号函数 $\text{sgn}(s)$。在实际数字控制系统中，由于离散采样和执行器带宽限制，这会导致控制信号在 $s=0$ 附近剧烈震荡，称为**抖振（Chattering）**。抖振会引起电机过热、齿轮磨损，并激发机械结构的高频共振 。

**解决方案：饱和函数 (Saturation Function)** 为了消除抖振，我们在滑模面附近引入一个厚度为 $\phi$ 的**边界层（Boundary Layer）**。在边界层内，将硬切换的 $\text{sgn}(s)$ 替换为连续的**饱和函数 $\text{sat}(s/\phi)$** ：

$$\text{sat}\left(\frac{s}{\phi}\right) = \begin{cases} \text{sgn}(s) & |s| > \phi \\ s/\phi & |s| \le \phi \end{cases}$$

**权衡 (Trade-off):**

这实际上将边界层内的控制律变成了一个高增益的PD控制器。虽然消除了抖振，但我们也牺牲了完美的滑模不变性（Invariance），最终误差不再收敛到零，而是收敛到以 $\phi$ 为界的各种小区域内。这在工程上通常是可以接受的妥协。

### 7.2 接触状态机与控制模式切换

> [!abstract] 混合系统视角
> 灵巧操作是典型的**混合动力系统 (Hybrid Dynamical System)**，其动力学在不同接触模式间离散切换。

#### 7.2.1 接触状态定义

灵巧操作中指尖与物体的交互可划分为以下离散状态：

| 状态 | 物理条件 | 动力学特征 |
|------|----------|------------|
| **Free (游离)** | $\phi(q) > 0$ | 自由运动，无接触力 |
| **Contact (接触)** | $\phi(q) = 0, \dot{\phi} = 0$ | 法向约束激活 |
| **Sliding (滑移)** | $\|f_t\| = \mu f_n$ | 切向力达摩擦锥边界 |
| **Rolling (滚动)** | $v_{contact} = 0, \omega \neq 0$ | 纯滚动无滑移 |
| **Sticking (粘滞)** | $\|f_t\| < \mu f_n$ | 摩擦锥内部，静摩擦 |

#### 7.2.2 状态机与控制切换

**状态转移图**：

```
         approach           contact           increase f_t
  Free ──────────► Contact ──────────► Sticking ──────────► Sliding
    ▲                 │                    │                    │
    │                 │ release            │ reduce f_t         │
    └─────────────────┴────────────────────┴────────────────────┘
```

**切换触发条件**：

| 转移 | 触发条件 | 检测方法 |
|------|----------|----------|
| Free → Contact | $\phi(q) \leq \epsilon$ 且 $f_n > f_{th}$ | 距离 + 力传感器 |
| Contact → Sliding | $\|f_t\| \geq (\mu - \delta) f_n$ | 摩擦锥余量监测 |
| Sliding → Free | $f_n < f_{th}$ | 力下降检测 |

**控制律切换策略**：

```python
if state == FREE:
    # 位置控制模式：快速接近目标
    u = K_p * (x_d - x) + K_d * (v_d - v)
elif state == CONTACT:
    # 阻抗控制模式：顺应性接触
    u = K_imp * (x_d - x) + B_imp * (v_d - v) + f_d
elif state == SLIDING:
    # 力控制模式：维持法向力，限制切向速度
    u = K_f * (f_d - f) + damping_tangent
```

> [!warning] Bumpless Transfer
> 模式切换瞬间必须保证控制量连续，否则会产生冲击力导致物体掉落或硬件损坏。

### 7.3 滑移检测与闭环防滑控制

> [!tip] 灵巧操作的核心安全约束
> 稳定夹持的本质是保持接触力始终在**摩擦锥内部**，滑移意味着接触约束即将失效。

#### 7.3.1 滑移检测方法

**1. 基于触觉传感器的直接检测**

| 传感器类型 | 检测原理 | 典型信号 |
|------------|----------|----------|
| **视触觉 (DIGIT/GelSight)** | 标记点位移 / 光流 | 切向形变场 |
| **6D 力矩传感器** | 摩擦锥余量计算 | $\gamma = \mu f_n - \|f_t\|$ |
| **压阻/电容阵列** | 接触面积变化率 | $\dot{A}_{contact}$ |

**2. 摩擦锥余量 (Friction Cone Margin)**

定义滑移风险指标：

$$\gamma = \mu f_n - \|f_t\| = \mu f_n - \sqrt{f_x^2 + f_y^2}$$

- $\gamma > 0$：安全（摩擦锥内部）
- $\gamma \approx 0$：临界滑移
- $\gamma < 0$：已滑移（物理上不可能，力模型失效）

**滑移概率估计**：

$$P_{slip} = \sigma\left(\frac{\gamma_{th} - \gamma}{\tau}\right)$$

其中 $\sigma$ 是 Sigmoid 函数，$\gamma_{th}$ 是安全阈值，$\tau$ 是温度参数。

#### 7.3.2 闭环防滑策略

**分层防滑架构**：

```
┌─────────────────────────────────────────────────────────┐
│  高层策略 (RL/MPC, 10-50Hz)                              │
│  • 接触状态机管理                                        │
│  • 操作相位规划（接触→稳定→操作→再抓）                   │
│  • 损失函数加入接触保持项                                 │
└───────────────────────────┬─────────────────────────────┘
                            │ 目标力/位姿
                            ▼
┌─────────────────────────────────────────────────────────┐
│  低层控制 (阻抗/力控, 100-1000Hz)                        │
│  • 维持法向力: f_n ≥ f_{n,min}                           │
│  • 限制切向速度: |v_t| ≤ v_{t,max}                       │
│  • 限制切向加速度/jerk 防止冲击                          │
└───────────────────────────┬─────────────────────────────┘
                            │ γ < γ_th 触发
                            ▼
┌─────────────────────────────────────────────────────────┐
│  紧急响应 (Reflex, <1ms)                                 │
│  • 立即增加法向力 Δf_n                                   │
│  • 短时提高摩擦裕度                                      │
│  • 触发再定位/再抓策略                                   │
└─────────────────────────────────────────────────────────┘
```

**法向力自适应律**：

当检测到滑移风险上升时，自适应增加夹持力：

$$\dot{f}_n^{ref} = K_{adapt} \cdot \max(0, \gamma_{th} - \gamma)$$

**材质自适应**：

不同材质（玻璃/金属/纸盒）的摩擦系数差异显著，需要在线估计或查表：

| 材质 | 典型 $\mu$ | $\gamma_{th}$ 建议 |
|------|------------|-------------------|
| 橡胶-橡胶 | 0.8-1.2 | 0.3 $f_n$ |
| 硅胶-塑料 | 0.5-0.8 | 0.2 $f_n$ |
| 硅胶-玻璃 | 0.3-0.5 | 0.15 $f_n$ |
| 硅胶-金属 | 0.2-0.4 | 0.1 $f_n$ |

------

## 8. 现代前沿：接触隐式模型预测控制

## 8. Modern Frontiers: Contact-Implicit MPC

直到最近，大多数灵巧操作控制都依赖于预先定义的接触序列（例如：先用食指接触，再用拇指接触）。然而，在复杂的在手操作中，接触的建立与断开（Making and Breaking Contact）极其频繁且难以预知。现代控制理论的前沿正在向**接触隐式（Contact-Implicit）**方法转移。

### 8.1 线性互补问题 (Linear Complementarity Problem, LCP)

接触动力学的本质可以用**互补约束**来描述：

$$0 \le \lambda \perp \phi(q) \ge 0$$

这里 $\lambda$ 是接触力（法向力），$\phi(q)$ 是接触距离（Gap function）。

- 如果 $\phi(q) > 0$（分离），则必须 $\lambda = 0$（无力）。
- 如果 $\lambda > 0$（受力），则必须 $\phi(q) = 0$（接触）。

这种约束是非凸、非光滑（Non-smooth）的，这使得基于梯度的优化算法（如 DDP, iLQR）难以直接应用，因为梯度在接触瞬间未定义或为零。

### 8.2 平滑化与松弛技术 (Smoothing & Relaxation)

为了在MPC框架中处理接触，最新的研究（如 **Contact-Implicit MPC** ）采用**Sigmoid松弛**技术。 我们将严格的互补约束 $\lambda \phi(q) = 0$ 松弛为：

$$\lambda \phi(q) \le \epsilon$$

或者使用Sigmoid函数构造一个连续可导的接触力模型：

$$F_{contact} \approx \frac{F_{max}}{1 + e^{-k \phi(q)}}$$

**技术优势：**

这种平滑化使得优化器（Optimizer）能够计算通过接触事件的梯度。这意味着MPC可以“感觉”到即将到来的接触，并自动规划出最佳的接触序列，而不需要人工指定何时接触。这使得机器人能够自主发现复杂的策略，例如利用环境来重新调整物体姿态（Extrinsic Dexterity）。

### 8.3 分层控制架构 (Hierarchical Architecture)

在实际部署中（如OpenAI或TRI的演示），通常采用分层架构来平衡长时程规划与高频响应 ：

1. **高层规划 (High-Level, 10-50Hz):** 运行 Contact-Implicit MPC。它基于简化的动力学模型，规划未来几秒内的接触序列和物体轨迹。
2. **底层控制 (Low-Level, 1kHz):** 运行全身控制（Whole-Body Control, WBC）或阻抗控制器。它接收高层的参考轨迹和接触力指令，利用高频的力反馈（Tactile/Force Feedback）来稳定当前的接触状态，并补偿高层模型忽略的高频动态。

这种架构代表了目前灵巧操作控制的最高水平：既具备优化的智能决策能力，又具备反馈控制的物理鲁棒性。

------

## 9. 数据驱动控制理论：从模型到数据的范式转移

## 9. Data-Driven Control Theory: The Paradigm Shift from Models to Data

> [!abstract] 核心洞察
> 传统控制依赖于精确的系统模型。**数据驱动控制**的革命性在于：直接从输入-输出数据设计控制器，绕过系统辨识步骤。其理论基石是 **Willems 基本引理 (Fundamental Lemma)**，它建立了数据与所有可能轨迹之间的等价关系。

### 9.1 Willems 基本引理 (The Fundamental Lemma)

> [!tip] 参考资料
> 详见 [[Books/Data-based linear systems and control theory.pdf]] Chapter 1.2.1 与 Chapter 11。

#### 9.1.1 问题设置

考虑线性时不变 (LTI) 系统：

$$x(t+1) = A_{true} x(t) + B_{true} u(t)$$
$$y(t) = C_{true} x(t) + D_{true} u(t)$$

其中 $x \in \mathbb{R}^{n_{true}}$ 是状态，$u \in \mathbb{R}^m$ 是输入，$y \in \mathbb{R}^p$ 是输出。**系统矩阵 $(A, B, C, D)$ 未知**，但我们有状态维度的上界 $N \geq n_{true}$。

**目标**：仅用输入-输出数据 $(u_{[0,T-1]}, y_{[0,T-1]})$ 来仿真或控制系统。

#### 9.1.2 Hankel 矩阵

给定长度为 $T$ 的数据序列，构造深度为 $L$ 的 **Hankel 矩阵**：

$$\mathcal{H}_L\begin{pmatrix} u_{[0,T-1]} \\ y_{[0,T-1]} \end{pmatrix} = \begin{bmatrix} u(0) & u(1) & \cdots & u(T-L) \\ \vdots & \vdots & \ddots & \vdots \\ u(L-1) & u(L) & \cdots & u(T-1) \\ y(0) & y(1) & \cdots & y(T-L) \\ \vdots & \vdots & \ddots & \vdots \\ y(L-1) & y(L) & \cdots & y(T-1) \end{bmatrix}$$

**物理意义**：Hankel 矩阵的每一列是长度为 $L$ 的受限输入-输出轨迹。由于系统的线性性，列向量的任意线性组合也是合法轨迹。

#### 9.1.3 持续激励 (Persistent Excitation)

**定义 (PE of order $k$)**：输入序列 $u_{[0,T-1]}$ 称为 **$k$ 阶持续激励**，如果其 Hankel 矩阵 $\mathcal{H}_k(u_{[0,T-1]})$ 行满秩。

**数据长度要求**：为满足 $(N+L)$ 阶 PE，需要：

$$T \geq (m+1)(N+L) - 1$$

#### 9.1.4 基本引理 (Theorem 1.2, Willems et al. 2005)

> [!important] Willems 基本引理
> 假设 $(A_{true}, B_{true})$ 可控，且输入 $u_{[0,T-1]}$ 是 $(N+L)$ 阶持续激励。则：
> 
> **(a) 秩条件**：矩阵 $\begin{bmatrix} X_{[0,T-L]} \\ \mathcal{H}_L(u_{[0,T-1]}) \end{bmatrix}$ 行满秩。
> 
> **(b) 轨迹表示**：$(\bar{u}_{[0,L-1]}, \bar{y}_{[0,L-1]})$ 是系统在 $[0, L-1]$ 上的合法轨迹 **当且仅当** 存在 $g \in \mathbb{R}^{T-L+1}$ 使得：
> $$\begin{pmatrix} \bar{u}_{[0,L-1]} \\ \bar{y}_{[0,L-1]} \end{pmatrix} = \begin{pmatrix} \mathcal{H}_L(u_{[0,T-1]}) \\ \mathcal{H}_L(y_{[0,T-1]}) \end{pmatrix} g$$

**核心洞察**：Hankel 矩阵的列空间**精确等于**所有长度为 $L$ 的合法轨迹空间。数据本身就是系统行为的非参数化表示。

### 9.2 数据信息性框架 (Data Informativity Framework)

> [!tip] 参考资料
> 详见 [[Books/Data-based linear systems and control theory.pdf]] Chapter 2。

#### 9.2.1 核心概念

**模型类 $\mathcal{M}$**：所有可能的系统模型集合（如所有 $n$ 阶 LTI 系统）。

**数据一致集 $\Sigma_D$**：给定数据 $D$，所有能生成该数据的系统：

$$\Sigma_D := \{(A, B) \in \mathcal{M} \mid X_+ = A X_- + B U_-\}$$

**性质集 $\Sigma_P$**：具有某性质 $P$（如稳定性、可镇定性）的系统集合。

#### 9.2.2 分析问题的信息性 (Informativity for Analysis)

**定义**：数据 $D$ 对性质 $P$ 是**信息充分的 (informative)**，如果 $\Sigma_D \subseteq \Sigma_P$。

即：所有与数据一致的系统都具有性质 $P$ → 可以从数据断言真实系统具有性质 $P$。

```
┌───────────────────────────────────────┐
│  模型类 M                              │
│    ┌─────────────────┐                │
│    │  Σ_P (稳定系统)  │                │
│    │   ┌───────┐     │                │
│    │   │ Σ_D   │     │  ← 数据信息充分 │
│    │   │  (S)  │     │    Σ_D ⊆ Σ_P   │
│    │   └───────┘     │                │
│    └─────────────────┘                │
└───────────────────────────────────────┘
```

#### 9.2.3 控制问题的信息性 (Informativity for Control)

**定义**：数据 $D$ 对控制目标 $O$ 是**信息充分的**，如果存在控制器 $K$ 使得 $\Sigma_D(K) \subseteq \Sigma_O$。

即：存在一个**单一控制器**能镇定所有与数据一致的系统。

**状态反馈镇定示例**：

控制目标 $O$："闭环系统稳定"
$$\Sigma_O = \{A' \in \mathbb{R}^{n \times n} \mid A' \text{ 是稳定的}\}$$

对于状态反馈 $K$，闭环系统集合：
$$\Sigma_D(K) = \{A + BK \mid (A, B) \in \Sigma_D\}$$

数据信息充分 ⟺ 存在 $K$ 使得 $A + BK$ 对所有 $(A, B) \in \Sigma_D$ 稳定。

### 9.3 数据驱动 LQR 与镇定

> [!note] 直接数据驱动控制
> 不需要先辨识系统，直接从数据计算控制器。

#### 9.3.1 无噪声情形的数据驱动镇定

给定输入-状态数据 $(U_-, X)$，定义：

$$X_- = X_{[0,T-1]}, \quad X_+ = X_{[1,T]}$$

则有 $X_+ = A_{true} X_- + B_{true} U_-$。

**定理 (数据驱动镇定)**：如果 $\begin{bmatrix} X_- \\ U_- \end{bmatrix}$ 行满秩（数据信息充分），则存在镇定状态反馈。控制器可通过求解 LMI 获得：

存在 $G \in \mathbb{R}^{(T) \times n}$ 和 $P \succ 0$ 使得：

$$\begin{bmatrix} P & X_+ G \\ G^T X_+^T & P \end{bmatrix} \succ 0$$

镇定控制器为 $K = U_- G P^{-1}$。

#### 9.3.2 带噪声数据的鲁棒镇定

> [!note] 教科书参考
> 本节基于 [[Books/Data-based linear systems and control theory.pdf]] Chapter 3.6-3.7（noisy input-state data 的 quadratic stability / quadratic stabilizability）、Chapter 6.3（quadratic stabilization using noisy data）、Appendix A.2-A.3（quadratic matrix inequalities 与 Matrix S-lemma / Finsler lemma）。

当数据受扰动 $w(t)$ 影响时，系统不再满足精确方程，而是：

$$
x(t+1)=A_{true}x(t)+B_{true}u(t)+w(t),\quad X_+=A_{true}X_-+B_{true}U_-+W_-.
$$

噪声先验用一个**二次矩阵不等式（Quadratic Matrix Inequality, QMI）**表达：

$$
\begin{bmatrix} I \\ W_-^\top \end{bmatrix}^\top
\Phi
\begin{bmatrix} I \\ W_-^\top \end{bmatrix} \succeq 0,
\quad
\Phi = \begin{bmatrix}\Phi_{11} & \Phi_{12} \\ \Phi_{21} & \Phi_{22}\end{bmatrix},
\quad \Phi_{22} \prec 0.
$$

逐点能量界 $\|w(t)\|_2^2 \leq \epsilon$ 可以聚合为 $W_- W_-^\top \preceq T\epsilon I$，这是上述 QMI 的一个特例。

因此数据一致集变为：

$$\Sigma_D = \{(A, B) \mid X_+ = A X_- + B U_- + W_-, \; \|w(t)\|^2 \leq \epsilon\}$$

**二次镇定**：寻找使所有一致系统具有共同 Lyapunov 函数 $V(x) = x^T Q x$ 的控制器。

#### 9.3.3 Matrix S-lemma：从无限多个模型到一个 LMI

噪声数据的难点在于 $\Sigma_D$ 通常包含无穷多个系统。鲁棒镇定要求一个控制器或证书同时覆盖所有 $(A,B)\in\Sigma_D$，形式上是：

$$
P - A P A^\top + B B^\top \succ 0,\quad \forall (A,B)\in\Sigma_D.
$$

这看起来是无穷多个不等式。Data-based control 的关键 insight 是：**一致系统集合本身由 QMI 描述，而 Lyapunov 条件也可写成 QMI；QMI 蕴含关系可由 Matrix S-lemma / Finsler lemma 转成有限维 LMI。**

设

$$
N =
\begin{bmatrix}
I & X_+ \\
0 & -X_- \\
0 & -U_-
\end{bmatrix}
\Phi
\begin{bmatrix}
I & X_+ \\
0 & -X_- \\
0 & -U_-
\end{bmatrix}^{\top}.
$$

> [!theorem] Theorem 3.19（噪声数据的二次可稳定性）
> 若 $\Phi_{22}\prec 0$ 且数据满足相应满秩条件，则 $(U_-,X)$ 对**二次可稳定性**信息充分，当且仅当存在 $P\succ0$ 与 $\alpha\ge0$ 使得：
> $$
> \begin{bmatrix}
> P & 0 & 0 \\
> 0 & -P & 0 \\
> 0 & 0 & I
> \end{bmatrix} - \alpha N \succ 0.
> $$
>
> **证明思路**：将“一致系统满足 Lyapunov QMI”写为集合包含关系 $Z_{n+m}(N)\subseteq Z_{n+m}^{+}(M)$，再用 Matrix S-lemma 把 QMI 蕴含等价为 $M-\alpha N\succ0$。

进一步，Corollary 3.20 将该条件化简为一个 $2n\times2n$ 的 LMI：

$$
\begin{bmatrix}
P & 0 \\
0 & -P
\end{bmatrix}
-
\begin{bmatrix}
I & X_+ \\
0 & -X_-
\end{bmatrix}
\Phi
\begin{bmatrix}
I & X_+ \\
0 & -X_-
\end{bmatrix}^{\top}
\succ 0.
$$

#### 9.3.4 灵巧操作应用：把短真机轨迹变成稳定性证书

对 [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS Actuator Model]] 和 [[Actuator2RigidDynamicsModel_gap|L25 执行器 gap]]，可以把局部状态定义为

$$
x_t=[\phi_t,\dot\phi_t,T_t,z_{\delta,t}],\quad u_t=a_t,
$$

其中 $z_{\delta,t}$ 编码 CAN latency / 总线相位差。短时 scripted 真机轨迹给出 $(U_-,X_-,X_+)$，噪声项 $W_-$ 吸收 CAN 抖动、温度漂移、触觉估计误差与未建模摩擦。

**工程用法**：
1. 用 5-10 分钟真机激励轨迹检查 $\begin{bmatrix}X_-\\U_-\end{bmatrix}$ 是否足够满秩（PE 条件）。
2. 设定噪声 QMI（例如 $W_-W_-^\top\preceq T\epsilon I$，或按温度/latency 分块设定各向异性 $\Phi$）。
3. 求解上面的 LMI。若可行，$P$ 是覆盖所有一致 actuator 模型的共同 Lyapunov 证书。
4. 若不可行，说明数据或噪声界不足：要么收集更丰富的激励，要么缩小策略输出灵敏度（见 [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective|Stability-Certified RL]] 的偏导数界 SDP）。

这给 [[Idea-002-Latency-Aware-Actuator|Latency-Aware Actuator]] 的 “5 分钟适配” 增加了一个古典控制理论判据：不是只看 validation MSE，而是检查**所有与真机短数据一致的局部执行器模型是否共享同一个稳定性证书**。

### 9.4 Data-Enabled Predictive Control (DeePC)

> [!abstract] 核心思想
> 将 Willems 引理嵌入 MPC 框架：用数据 Hankel 矩阵替代显式系统模型。

**DeePC 优化问题**：

$$\min_{g, \sigma} \sum_{k=0}^{N-1} \|\bar{y}(k) - y_{ref}\|_Q^2 + \|\bar{u}(k)\|_R^2 + \lambda_\sigma \|\sigma\|^2$$

约束：
$$\begin{pmatrix} U_p \\ Y_p \\ U_f \\ Y_f \end{pmatrix} g = \begin{pmatrix} u_{ini} \\ y_{ini} + \sigma \\ \bar{u} \\ \bar{y} \end{pmatrix}$$

其中 $U_p, Y_p$ 是过去数据的 Hankel 矩阵（用于匹配初始条件），$U_f, Y_f$ 是未来预测的 Hankel 矩阵。

**松弛项 $\sigma$**：处理测量噪声导致的不一致性。

### 9.5 与灵巧操作的联系

> [!warning] 局限性
> 数据驱动控制主要针对 **LTI 系统**。灵巧操作涉及非线性、混合动力学，需要扩展：
> - **Koopman 算子提升**：将非线性系统提升到无限维线性空间
> - **分段线性逼近**：在不同接触模式下分别应用
> - **与 RL 结合**：数据驱动提供初始策略，RL 在线精调

**潜在应用**：
1. **接触力学的线性化区域**：小变形下的阻抗模型近似 LTI
2. **遥操作数据的利用**：人类示教数据构建行为 Hankel 矩阵
3. **安全约束嵌入**：在 DeePC 约束中加入摩擦锥约束

------

## 10. 稳定性理论的统一基石 (Unified Foundations of Stability Theory)

> [!important] 章节定位
> §3-§9 已分别介绍阻抗、OSF、混合控制、SMC、CIO-MPC、数据驱动控制等控制器设计范式。本节回到**所有这些方法共享的底层数学骨架**——Lyapunov 稳定性理论。它统一了：
> - §3.2 阻抗控制的被动性证明
> - §4 OSF 的零空间收敛性
> - 与 [[Safe Model-based Reinforcement Learning with Stability Guarantees|RL 中价值即 Lyapunov]] 的桥梁（§3.2 已引用）
> - §3.3 [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints|CBF]] 的对偶推导
> - §11 LQR 的代价收敛
> - §12 自适应控制的参数收敛
>
> 灵巧操作研究者必须掌握这套语言——它是评判任何控制器（古典 / RL / Diffusion）是否"真正可靠"的唯一通用尺度。

### 10.1 自治系统的 Lyapunov 直接法 (Lyapunov's Direct Method)

> [!note] 教科书参考
> 本节基于 Khalil "Nonlinear Systems" Chapter 4 与 Murray Ch.4 的标准结果。

#### 物理直觉

**能量守恒 → 能量耗散 → 收敛**。若能找到一个标量"能量函数" $V(x)$，它在平衡点取最小值，且系统轨迹沿 $V$ 单调下降，那么轨迹必然被吸引到平衡点。无需求解 ODE，仅靠能量代数即可断言稳定性——这是 Lyapunov 1892 年留下的最优雅遗产。

#### 形式化定义

考虑自治系统 $\dot x = f(x)$，$f(0) = 0$，$x \in \mathcal{D} \subset \mathbb{R}^n$。

**定义（Lyapunov 函数候选）**：连续可微函数 $V: \mathcal{D} \to \mathbb{R}$ 称为 Lyapunov 函数候选当：
- $V(0) = 0$，且 $V(x) > 0,\ \forall x \in \mathcal{D} \setminus \{0\}$（**正定**）
- $V$ 在 $\mathcal{D}$ 上径向无界（在全局结果中需要）

沿系统轨迹的导数：

$$\dot V(x) = \nabla V(x)^\top f(x).$$

> [!theorem] Theorem 10.1（Lyapunov 直接法）
> 设 $V$ 为 Lyapunov 函数候选。
> 1. 若 $\dot V(x) \leq 0,\ \forall x \in \mathcal{D}$，则 $x = 0$ 是**Lyapunov 稳定**的（轨迹有界）。
> 2. 若 $\dot V(x) < 0,\ \forall x \in \mathcal{D} \setminus \{0\}$，则 $x = 0$ 是**渐近稳定**的（$x(t) \to 0$）。
> 3. 若进一步存在 $\alpha > 0$ 使 $\dot V(x) \leq -\alpha V(x)$，则**指数稳定**（$\|x(t)\| \leq C e^{-\alpha t/2} \|x(0)\|$，对应 $V \sim \|x\|^2$）。
>
> **证明思路**：对 $V(x(t))$ 应用比较引理（Comparison Lemma），利用 $V$ 的正定性夹逼 $\|x(t)\|$。

#### 灵巧操作应用

| 控制范式 | Lyapunov 函数选择 | 收敛指标 |
|---------|-------------------|---------|
| **PD + 重力补偿** | $V = \tfrac{1}{2} \dot q^\top M(q) \dot q + \tfrac{1}{2} (q-q_d)^\top K_p (q-q_d)$ | 关节空间渐近稳定 |
| **阻抗控制**（§3.2） | 见 §3.2 callout 的 $V = \tfrac{1}{2} \dot{\tilde x}^\top M_d \dot{\tilde x} + \tfrac{1}{2} \tilde x^\top K_d \tilde x$ | 任务空间被动 |
| **OSF + Null Space**（§4） | $V = \tfrac{1}{2} \dot{\tilde x}^\top \Lambda \dot{\tilde x} + \cdots$ + null-space 子项 | 任务优先收敛 |
| **CBF**（§3.3） | $h(x)$ 作为安全 barrier，对偶 Lyapunov | 安全集前向不变 |

### 10.2 LaSalle 不变集原理 (LaSalle's Invariance Principle)

> [!theorem] Theorem 10.2（LaSalle 不变集原理）
> 设 $\Omega \subset \mathcal{D}$ 是紧致正不变集，$V: \Omega \to \mathbb{R}$ 连续可微，$\dot V(x) \leq 0$ 在 $\Omega$ 上成立。设 $E = \{x \in \Omega : \dot V(x) = 0\}$，$M$ 为 $E$ 内**最大不变集**。则任意 $x(0) \in \Omega$ 的轨迹满足 $x(t) \to M$。

#### 为何重要

许多机械系统的 $\dot V$ **半负定**（如 $\dot V = -\dot q^\top D \dot q$ 仅在 $\dot q = 0$ 处为零），定理 10.1 仅给出 Lyapunov 稳定，无法断言渐近稳定。LaSalle 弥补了这一缺口：通过分析"$\dot V = 0$ 的最大不变集"是否仅含平衡点，即可推出渐近稳定。

#### 灵巧操作典型用法

PD + 重力补偿控制器 $\tau = -K_p \tilde q - K_d \dot q + g(q)$ 下，$\dot V = -\dot q^\top K_d \dot q \leq 0$。$\dot V = 0 \Leftrightarrow \dot q = 0$，代入闭环动力学得 $\ddot q = -M^{-1} K_p \tilde q$，故 $\dot q \equiv 0 \Rightarrow \tilde q = 0$。LaSalle 给出全局渐近稳定。

### 10.3 输入-状态稳定性 (Input-to-State Stability, ISS)

> [!note] 教科书参考
> Sontag (1989) 提出的 ISS 概念，是连接古典 Lyapunov 与现代鲁棒控制的桥梁。

#### 形式化定义

非线性系统 $\dot x = f(x, u)$ 是 **ISS** 当存在 $\mathcal{KL}$ 函数 $\beta$ 与 $\mathcal{K}$ 函数 $\gamma$ 使：

$$\|x(t)\| \leq \beta(\|x(0)\|, t) + \gamma\left(\sup_{0 \leq \tau \leq t} \|u(\tau)\|\right).$$

> [!theorem] Theorem 10.3（ISS-Lyapunov 函数）
> 系统 ISS 当且仅当存在光滑径向无界正定 $V$ 与 $\mathcal{K}_\infty$ 函数 $\alpha_3, \chi$ 使：
> $$\|x\| \geq \chi(\|u\|) \;\Longrightarrow\; \dot V(x, u) \leq -\alpha_3(\|x\|).$$
>
> **物理含义**：当状态范数大于扰动幅值的某个非线性增益时，能量严格下降——系统对**所有有界扰动**给出有界响应。

#### 灵巧操作应用

- **未建模动力学**（摩擦、迟滞、电缆张力）作为输入扰动 $u = \Delta(x, t)$，ISS 保证策略不会因小扰动发散。
- **Sim-to-real gap** 视为有界外部输入，ISS-Lyapunov 函数给出**仿真控制器在真机上仍稳定的充分条件**——这是 [[Idea-002-Latency-Aware-Actuator]] frozen-rigid 适配能成立的理论根据。
- **RL 策略的鲁棒性证书**：将策略嵌入闭环动力学后，若能学得 ISS-Lyapunov 函数（参考 [[Safe Model-based Reinforcement Learning with Stability Guarantees]]），即可在部署前给出安全保证。

### 10.4 被动性、Passivity-Based Control 与 RL 价值函数

§3.2 已展示阻抗控制的被动性证明。一般地：

> [!important] 被动性的统一表述
> 系统 $\Sigma: u \to y$ 是**被动的**当存在储能函数 $H(x) \geq 0$ 使 $\dot H \leq u^\top y$。
>
> **关键性质**：
> - 两个被动系统的反馈互联仍被动（**被动性定理**）
> - 严格输出被动 + 零状态可观 ⇒ 渐近稳定
>
> **与 RL 的统一**：负优势函数 $-A^\pi(s, a)$ 在最优策略下满足类似 $\dot V \leq 0$ 的关系——这就是 §3.2 引用的"价值即 Lyapunov"洞见的根源。Bellman 算子的压缩性等价于一种离散时间被动性。

------

## 11. 线性二次最优控制 (Linear Quadratic Regulator, LQR)

> [!note] 教科书参考
> 本节基于 Anderson & Moore "Optimal Control: Linear Quadratic Methods" 与 Bertsekas "Dynamic Programming and Optimal Control" Vol. I 的标准推导。它是 §8 CIO-MPC 中 iLQR/DDP 的**线性原型**，也是 §9.3 数据驱动 LQR 的**模型已知 baseline**。

### 11.1 连续时间无限时域 LQR

考虑 LTI 系统 $\dot x = A x + B u$，二次代价

$$J = \int_0^\infty (x^\top Q x + u^\top R u)\, dt,\quad Q \succeq 0,\ R \succ 0.$$

> [!theorem] Theorem 11.1（连续 ARE 与最优反馈）
> 若 $(A, B)$ 可镇定且 $(A, Q^{1/2})$ 可观测，则**代数 Riccati 方程**
> $$A^\top P + P A - P B R^{-1} B^\top P + Q = 0$$
> 存在唯一正定解 $P^* \succ 0$。最优反馈律
> $$u^*(t) = -K x(t),\qquad K = R^{-1} B^\top P^*$$
> 使闭环 $A - BK$ Hurwitz，最优代价 $J^* = x_0^\top P^* x_0$。
>
> **证明骨架**：对 $V(x) = x^\top P x$ 应用 HJB 方程 $\min_u \{x^\top Q x + u^\top R u + \nabla V \cdot (Ax + Bu)\} = 0$，对 $u$ 求导得到 $u^* = -R^{-1} B^\top P x$，回代即得 ARE。

### 11.2 离散时间有限时域 LQR：Riccati 递推

离散系统 $x_{k+1} = A x_k + B u_k$，代价 $J = x_N^\top Q_N x_N + \sum_{k=0}^{N-1} (x_k^\top Q x_k + u_k^\top R u_k)$。

> [!theorem] Theorem 11.2（DRE 后向递推）
> 令 $P_N = Q_N$。则
> $$P_k = Q + A^\top P_{k+1} A - A^\top P_{k+1} B (R + B^\top P_{k+1} B)^{-1} B^\top P_{k+1} A.$$
> 最优反馈律 $u_k^* = -K_k x_k$，$K_k = (R + B^\top P_{k+1} B)^{-1} B^\top P_{k+1} A$。
>
> **复杂度**：$O(N (n_x^3 + n_u^3))$——这正是 [[Optimization#4.1 核心算法：iLQR / DDP|iLQR]] 的 Backward Pass 的线性化原型。

### 11.3 LQR 与 iLQR / 数据驱动 LQR / RL 的统一

| 方法 | 模型来源 | 解法 | 适用范围 |
|------|---------|------|---------|
| **LQR**（§11.1） | 已知 LTI $(A, B)$ | ARE 一次性求解 | 线性系统精确解 |
| **iLQR / DDP**（[[Optimization#4.1 核心算法：iLQR / DDP|Optim §4.1]]） | 非线性 + 线性化 | 后向 Riccati + 前向滚动 | 接触前的非线性 MPC |
| **数据驱动 LQR**（§9.3） | Hankel 矩阵 (PE 数据) | LMI / SDP | 模型未知的 LTI |
| **DDPG / SAC** | 神经网络拟合 $Q_\phi$ | 随机梯度 | 高维非线性 + 探索 |

> [!tip] 灵巧操作中的 LQR 价值
> 真机调试时常用 LQR 作为**接触前阶段的 baseline 控制器**：在 pre-grasp 段 $A, B$ 由刚体动力学线性化得到，LQR 给出最优反馈增益，避免手工调 PD。一旦进入接触段切换到 §3.2 阻抗或 §5 hybrid。这种"分段线性 + 模式切换"是工业级灵巧操作的实用骨架。

------

## 12. 自适应控制与确定性等价原理 (Adaptive Control & Certainty Equivalence)

> [!note] 教科书参考
> 本节基于 Ioannou & Sun "Robust Adaptive Control" 与 Åström & Wittenmark "Adaptive Control" 的经典框架。

### 12.1 问题设定

被控对象 $\dot x = f(x, u, \theta)$，$\theta \in \mathbb{R}^p$ 是**未知但常值**参数（如负载惯量、摩擦系数、电缆刚度）。目标：同时**辨识 $\theta$** 与**控制 $x$**。

### 12.2 模型参考自适应控制 (MRAC) 框架

参考模型 $\dot x_m = A_m x_m + B_m r$ 给出期望响应。控制律 $u = \theta_x^\top x + \theta_r^\top r$ 由可调参数 $\hat\theta(t)$ 实现。误差 $e = x - x_m$。

**MIT 规则 / 梯度自适应律**：

$$\dot{\hat\theta} = -\Gamma e^\top P B \cdot \phi(x, r),\quad \Gamma \succ 0.$$

> [!theorem] Theorem 12.1（MRAC 稳定性）
> 在匹配条件（Matching Condition）成立下，选取 $V = e^\top P e + \tilde\theta^\top \Gamma^{-1} \tilde\theta$，则 $\dot V = -e^\top Q e \leq 0$（半负定）。LaSalle 给出 $e \to 0$。
>
> **关键**：$V$ 包含 $\tilde\theta = \hat\theta - \theta^*$ 项，意味着**参数误差进入能量函数**——这是自适应控制与固定增益控制最本质的区别。

### 12.3 确定性等价原理 (Certainty Equivalence)

> [!important] 确定性等价原理
> 设若 $\theta$ 已知，最优控制律为 $u^* = \pi^*(x; \theta)$。**确定性等价**控制器是：
> $$u_{CE}(t) = \pi^*\big(x(t); \hat\theta(t)\big).$$
>
> 即"用当前估计 $\hat\theta$ 替代真实 $\theta$"。
>
> **何时可证收敛**：当辨识误差 $\tilde\theta \to 0$ 足够快（**持续激励条件**，§9.1.3），且 $\pi^*$ 关于 $\theta$ 连续，则 $u_{CE}$ 渐近达到最优。

### 12.4 PE 与参数收敛的桥梁

> [!theorem] Theorem 12.2（PE → 参数收敛）
> 若回归向量 $\phi(t)$ 满足 $\exists\, \alpha, T > 0$:
> $$\alpha I \preceq \int_t^{t+T} \phi(\tau) \phi(\tau)^\top d\tau,\quad \forall t \geq 0,$$
> 则 MRAC 的参数估计 $\hat\theta(t) \to \theta^*$ **指数收敛**。
>
> **物理含义**：仅当输入"足够丰富"（在 $T$ 内激发所有模式），辨识才能区分真实参数与等价参数。

PE 条件正是 §9.1.3 Hankel 矩阵满秩条件的连续时间对偶。

### 12.5 灵巧操作中的自适应控制

| 不确定参数 | 自适应方法 | WMTS 关联 |
|----------|-----------|----------|
| **电机摩擦/惯量漂移** | MRAC + Lyapunov 适应律 | [[Idea-002-Latency-Aware-Actuator]]（FiLM 隐变量替代经典 $\hat\theta$） |
| **接触刚度未知** | 阻抗参考自适应（[[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]） | §3.2 callout 已引用 |
| **物体质量未知** | 在线 mass identification + 重力补偿更新 | [[Idea-007-Implicit-Explicit-Contact-WM]] 隐式残差等效"在线 $\hat\theta$" |
| **环境摩擦系数** | RMA 隐变量推断 | [[ReinforcementLearning#5.0 系统辨识与在线参数学习 (System Identification & Online Adaptation)|RL §5.0]] |

> [!tip] 现代视角：自适应控制 ≈ Meta-RL
> RMA、Latent Adapter、FiLM Conditioning 本质上都是**学习版的确定性等价控制器**：神经网络替代解析的 $\pi^*(x; \theta)$，隐变量 $z$ 替代经典的 $\hat\theta$。Lyapunov 自适应律的数学保证（PE → 收敛）为这些深度自适应方法提供了**为何能在小数据下工作**的理论解释。

### 12.6 鲁棒 vs 自适应：何时选择

| 维度 | 鲁棒控制 (§7 SMC, $H_\infty$) | 自适应控制 (§12) |
|------|-------------------------------|-----------------|
| **不确定性** | 范数有界，最坏情况 | 参数化，慢时变 |
| **代价** | 保守（牺牲性能换稳定） | 暂态可能差 |
| **数据需求** | 无需在线辨识 | 需要 PE |
| **灵巧操作场景** | 接触瞬时冲击、未建模高频动力学 | 任务相关参数（物体质量、表面摩擦） |
| **现代趋势** | 与 CBF 结合 → 安全 RL | 与 Meta-RL 结合 → Latent Adapter |

> [!important] 理论大厦的整合视角
> **Lyapunov（§10）+ LQR（§11）+ Adaptive（§12）+ Data-Driven（§9）+ CBF（§3.3）= 现代灵巧操作控制理论的完整底座**。
> - 任何古典控制器：用 Lyapunov 证稳定 + LQR 设最优 + Adaptive 处理未知参数 + CBF 加安全约束
> - 任何 RL 控制器：将策略视为参数化控制律 → 价值函数即 Lyapunov 函数 → PE 类比为 exploration 充分性 → safe RL = Lyapunov + CBF
> - 数据驱动控制（§9）则是"跳过参数辨识，直接从轨迹构造等价控制律"的现代变体——其本质仍是 PE 条件保证的可识别性

------

## 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及控制理论的核心主题

### 阻抗控制与变刚度
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 阻抗控制作为 RL 动作空间
- [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking]] — 数据驱动阻抗辨识
- [[FACET - Force-Adaptive Control via Impedance Reference Tracking]] — **阻抗参考模型跟踪**：RL 跟踪虚拟弹簧-质量-阻尼轨迹实现力自适应

### Safe RL 与稳定性
- [[Reachability Constrained Reinforcement Learning]] — 可达性约束
- [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] — 潜在空间 CBF
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] — Lipschitz 约束网络
- [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]] — 鲁棒 RL

### 控制频率与时间步
- [[TARC - Time-Adaptive Robotic Control]] — **时间自适应控制**：策略输出动作+持续时间，自动调节控制频率
- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 弹性时间步
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks]] — 高频控制进化
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多速率采样
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — 动作持续性

### 轨迹跟踪与模仿
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 神经跟踪控制
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]] — 物理角色动画

### Actuation-Aware 建模与高动态控制
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] — **Torque-speed envelope** 建模执行器物理极限，power-safety 正则化，actuation-aware 残差 RL 后训练

### 顺应控制与导纳控制
- [[Minimalist Compliance Control|MCC]] — **方向相关效率 + 系列弹性元件**：最小模型辨识的力控框架，谐波减速器非对称效率补偿
- [[Path-Constrained Haptic Motion Guidance via Admittance Control]] — **路径约束导纳控制**：自适应相位导纳实现触觉引导

### Sim-to-Real 迁移中的控制挑战
- [[sim2real|硬件 Sim-to-Real Gap 分析]] — 电机/减速器/传动方案对控制策略迁移的系统影响分析
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]] — 接触基准策略：力-触觉反馈闭环的 sim-to-real 对齐

### 项目级真机控制 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-002-Latency-Aware-Actuator|LAAA]]：CAN 延迟与温度漂移 conditioned actuator FiLM
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-013-Stick-Slip-Mode-Switching|SSMS]]：stick-slip 模态识别的双子策略 (slow/burst) 切换控制

------

## 13. 结论 (Conclusion)

从早期的高增益位置控制，到引入顺应性的阻抗控制，再到处理冗余度的操作空间公式化，控制理论的演进主线是对**物理交互本质的尊重**。我们不再试图强行命令机器人去违反物理约束，而是通过数学工具（如抓取矩阵、动态一致性逆、Montana方程）去建模和利用这些约束。

当前的非线性控制与接触隐式MPC更是将这一理念推向极致：我们将接触不再视为一种干扰，而是视为一种可以优化利用的资源。对于知识库的构建，建议将“对偶性”、“动态解耦”和“接触松弛”作为三大核心支柱，串联起这一宏大的技术图谱。

------

**参考文献引用 (References Cited Inline):** .