---
tags:
  - paper
  - dexterous-manipulation
  - sim-to-real
  - neural-dynamics
  - in-hand-rotation
aliases:
  - DexNDM
  - Joint-wise Dynamics
paper-year: 2024
read-date: 2026-01-31
venue: arXiv
paper-pdf: "[[Papers/DEXNDM: CLOSING THE REALITY GAP FOR DEXTEROUS IN-HAND ROTATION VIA JOINT-WISE NEURAL DYNAMICS MODEL.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model

> [!abstract] 核心概要
> 提出 **DexNDM** 框架：通过**关节级神经动力学模型**（joint-wise neural dynamics model）弥合 sim-to-real gap，实现前所未有的通用灵巧手内旋转——包括高长宽比物体（5.33:1）、复杂形状、多样腕部姿态和旋转轴。

> [!note] 教科书背景
> **动力学分解的理论根源**：本论文的"关节级动力学分解"思想源于 [[Dynamics|RNEA 递归思想]]——将整体系统分解为关节-连杆级别的局部力学关系，利用运动链的**连通性**实现 $O(N)$ 计算。
> 
> **与教科书的 Delta**：
> - **经典 RNEA**：假设精确已知的刚体惯量参数和接触模型
> - **DexNDM**：用神经网络隐式学习"未建模动力学"（肌腱摩擦、关节间耦合、接触变形）
> 
> 详见 Murray et al. "A Mathematical Introduction to Robotic Manipulation" Ch.4 中关于 **Lagrangian 分解** 和 **Newton-Euler 递推** 的理论推导。

> [!tip] 与理论基础的关联
> - [[Dynamics]] - 关节运动学基础
> - [[Dynamics]] - 分解式动力学的理论根源
> - [[ReinforcementLearning]] - 域随机化的替代方案
> - [[ContactMechanics]] - 手指-物体接触的复杂性
> - [[ControlTheory]] - 残差策略适应
>
> **核心技术**: Joint-wise Dynamics Factorization, Residual Policy, Autonomous Data Collection

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**不建模整手系统，而是学习每个关节的"净效应"动力学 → 高数据效率 + 强泛化性**

### 直观隐喻
想象你要学习弹钢琴：
- **传统方法**：学习整个身体的生物力学模型（太复杂！）
- **DexNDM 方法**：每根手指独立学习"我按键 → 手指怎么动"，手臂、身体的影响被压缩成"净效应"

这种分解让学习更容易，且对不同曲目（物体）泛化更好。

### 现有方法的局限
1. **Domain Randomization 数据饥渴**：OpenAI Rubik's Cube 需上万年仿真计算量；物体多样性越高，随机化范围越大，训练代价指数增长
2. **整体系统辨识不可扩展**：用神经网络学习 $\dot{x}_{system} = f(x_{system}, a)$，状态维度极高（16 DoF 手 + 6 DoF 物体），数据效率低、泛化差
3. **真实数据采集困难**：传统方法需物体状态追踪（视觉标记/动捕）且需人工复位，严重限制数据规模

### 领域定位
```
Sim-to-Real for Dexterous Manipulation
        ↓
Domain Randomization (OpenAI Rubik's Cube)
        ↓
System Identification + Fine-tuning
        ↓
████████████████████████████████████████
█  DexNDM (2024)                       █
█  • 关节级动力学分解                   █
█  • 自主数据采集（无需物体追踪）        █
█  • 单一策略处理多样物体+姿态          █
████████████████████████████████████████
        ↓
未来: 触觉增强的关节动力学
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题定义

**目标**：开发通用灵巧手内旋转策略——
- 广泛的物体分布（形状、尺寸、长宽比）
- 多样的腕部姿态（掌心向上/下、拇指向上/下等）
- 任意旋转轴

**核心障碍**：Sim-to-real gap
- 复杂接触动力学难以精确建模
- 域随机化需要海量仿真数据
- 真实数据采集面临"量-质冲突"

### Delta 分析

| 方法 | 动力学建模 | 数据效率 | 物体泛化 | 姿态泛化 |
|-----|----------|---------|---------|---------|
| Domain Randomization | 全系统 | 低 | 有限 | 有限 |
| 整体神经动力学 | 全状态 | 中 | 受限 | 受限 |
| **DexNDM** | **关节级** | **高** | **强** | **强** |

### 关键贡献

1. **C1**: 关节级神经动力学模型——分解高维系统，提高数据效率和泛化性
2. **C2**: 全自主数据采集策略——无需物体状态估计，无需人工复位
3. **C3**: 专家-通才蒸馏管道——从类别专家到统一策略

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.0 变量来源追踪

枢纽：**把系统级动力学 $f(x_{system},a)$ 分解为每关节 $f_j(h_j)$**（降维 → 15 分钟数据即可），以及历史窗口 $h_j$ 作为隐式系统辨识的唯一信号源。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $q_j,\dot{q}_j,\tau_j$ | scalar×3 | 观测（本体） | 否（输入） | 关节 $j$ 位置/速度/力矩 | 单关节 2-dim($q,a$)×W 历史 |
| $h_j$ | $\mathbb{R}^{2W}$ | 观测窗口 | 否 | 关节 $j$ 本体感受历史 | **隐式系统辨识唯一信号**（去掉 −41%）|
| $\phi_j$ | params | 学习（每关节独立） | 是 | 关节级动力学网络 | **参数不共享**（各关节摩擦/耦合异） |
| $\hat{q}_j^{t+1}$ | scalar | $\phi_j(h_j)$ 输出 | 是 | 预测下一状态 | **增量 $\Delta q$** 非绝对（避恒等映射） |
| $a_{base}$ | $\mathbb{R}^{16}$ | 仿真基策略 | 否 | 基动作 | 残差依赖其合理性 |
| $\Delta a$ | $\mathbb{R}^{16}$ | 残差网络 | 是 | sim-to-real 修正 | $a=a_{base}+\Delta a$ |
| $\hat{s}_{sim},\hat{s}_{real}$ | 状态 | 仿真器 / DexNDM 预测 | — | 两者差 = reality gap | 残差显式编码 $\hat s_{sim}-\hat s_{real}$ |
| 随机外部负载 | — | 数据采集 | 否 | 代替真实物体 | 须覆盖真实物体惯量分布 |

### 3.1 核心洞察：动力学分解

**传统方法**（整体建模）：
$$\dot{x}_{system} = f(x_{system}, a)$$

其中 $x_{system} \in \mathbb{R}^{n_{hand} + n_{object}}$ 是高维状态。

**DexNDM 方法**（关节级分解）：
$$\dot{q}_j = f_j(h_j^{proprio}), \quad j = 1, \ldots, n_{joints}$$

其中 $h_j^{proprio}$ 是关节 $j$ 的本体感受历史（位置、速度、力矩指令）。

> [!important] 关键假设
> 系统级影响（关节耦合、物体负载、自驱动）可以被压缩到**低维净效应**中，并隐式地被本体感受历史捕获。

### 3.2 关节级动力学模型

**输入**：关节 $j$ 的本体感受历史
$$h_j = [(q_j^{t-H}, \dot{q}_j^{t-H}, \tau_j^{t-H}), \ldots, (q_j^t, \dot{q}_j^t, \tau_j^t)]$$

**输出**：预测的下一状态
$$\hat{q}_j^{t+1} = \phi_j(h_j; \theta)$$

**网络架构**：
```
┌─────────────────────────────────────────┐
│  Joint-wise Neural Dynamics Model       │
├─────────────────────────────────────────┤
│                                         │
│  Proprio History (H steps)              │
│  [q, q̇, τ]_j × H                        │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ 1D Conv     │ (temporal features)    │
│  └──────┬──────┘                        │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ MLP         │                        │
│  └──────┬──────┘                        │
│         │                               │
│         ▼                               │
│  Δq_j (predicted change)                │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 为什么关节级分解有效？

**RMA (Rapid Motor Adaptation) 的思想扩展**：

RMA 证明了：腿部机器人可以从本体感受历史**隐式推断**地形、负载等外部因素。

DexNDM 将此推广到灵巧手：
- **每个关节**的本体感受历史编码了：
  - 自身驱动特性（电机动力学）
  - 关节间耦合（腱驱动耦合）
  - 物体负载（接触力的间接影响）

### 3.4 残差策略

**基策略**：仿真训练的策略 $\pi_{base}(a | s)$

**残差策略**：适应真实世界的修正 $\Delta a = \pi_{res}(s, \hat{s}_{sim}, \hat{s}_{real})$

**组合**：
$$a_{final} = a_{base} + \Delta a$$

其中 $\hat{s}_{sim}$ 是仿真器预测的下一状态，$\hat{s}_{real}$ 是 DexNDM 预测的真实世界状态。

### 3.5 自主数据采集

**核心问题**：如何在不知道物体状态的情况下采集有用数据？

**解决方案**：
1. 随机外部负载代替真实物体
2. 手指在负载下随机运动
3. 记录本体感受数据（无需视觉追踪）

```
┌─────────────────────────────────────────┐
│  Autonomous Data Collection             │
├─────────────────────────────────────────┤
│                                         │
│  1. Apply random external load          │
│     (simulates object weight/inertia)   │
│         │                               │
│         ▼                               │
│  2. Random joint exploration            │
│     (coverage of state space)           │
│         │                               │
│         ▼                               │
│  3. Record proprioception               │
│     (q, q̇, τ history)                   │
│         │                               │
│         ▼                               │
│  4. No resets needed!                   │
│     (continuous collection)             │
│                                         │
└─────────────────────────────────────────┘
```

---

### 3.6 概念边界与符号陷阱

- **关节级独立性假设**：强耦合（腱驱动对指快速同动）时交叉耦合力矩可能超出"净效应"建模能力（§5 理论局限）。
- **预测增量 $\Delta q$ 非绝对 $q$**：残差学习避免恒等映射，提升小变化量预测精度。
- **关节间参数不共享**：各关节动力学差异大（对指 vs 拇指的摩擦/耦合），16 DoF → 16 个独立网络。
- **仅前向动力学、无逆动力学约束**：不保证物理一致性（能量守恒）。
- **自主数据采集用随机外部负载代替物体**：免物体追踪/复位，但负载分布须覆盖真实物体惯量。
- **残差依赖基策略合理性**：仿真基策略在高速操作偏差过大时，残差修正空间不足。
- **历史窗口 $h_j$ 是隐式系统辨识唯一信号源**：去掉 −41%（最大降幅）——单帧无法推断耦合/负载隐变量。

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**硬件**：LEAP Hand（16 DoF）+ 腕部自由度

**物体分布**：
- **挑战性几何**：高长宽比（最高 5.33:1）、小尺寸
- **复杂形状**：动物、工具等
- **多样腕部姿态**：掌心向上/下、拇指向上/下、任意角度

### 4.1.5 训练设定

**Stage A — Oracle Specialist (PPO in Isaac Gym)**：
- 物体按几何特征分为 **5 个类别**，每类独立训练一个 PPO specialist
- 观测空间：320-dim（关节位置历史 48 + 目标历史 48 + 速度 16 + 指尖 52 + 物体 13 + 目标姿态 4 + 力 40 + 接触 92 + 腕部 4 + 旋转轴 3）
- 动作空间：16-dim 关节位置增量，$a_t = a_{t-1} + \frac{1}{24}\Delta a_t$，PD 控制器转力矩
- 控制频率 **20 Hz**（每步 Isaac Gym 内走 24 子步）
- 奖励：$r = \alpha_{rot}\, r_{rot} + \alpha_{goal}\, r_{goal} + \alpha_{penalty}\, r_{penalty}$
  - $r_{rot} = \text{clip}(\omega_t \cdot k, -0.5, 0.5)$
  - $r_{penalty} = -0.1\|\omega_t \times k\|_1 - 0.3\|v_t\|_2^2 - 0.3\|q_t - q_{init}\|_2^2 - 2.0\,\tau^T\dot{q} - 0.1\|\tau\|_2^2$（$\alpha_{rotp}$ 按 reset 数从 0 线性增至 0.1）
  - $r_{goal}$：中间目标姿态引导（每 90° 设一个 waypoint）

**Stage B — Generalist (Behaviour Cloning)**：
- 网络：**Residual MLP**，5 个残差块，hidden dim = 1024；每块 $y = \text{ReLU}(\text{NN}_1(x) + \text{NN}_3(\text{ReLU}(\text{NN}_2(x))))$
- 输入 $o_t^{gene}$：本体感受历史 $\{(q_k, a_{k-1})\}_{k=t-9}^{t}$（$T=10$）+ 腕部朝向 + 旋转轴
- 监督信号：所有 specialist 成功轨迹聚合后的动作标签
- 训练方式：标准 BC（非 DAgger，因 DAgger 在此任务难度下训练不稳定/真实世界崩溃）

**Stage D — Joint-Wise Dynamics Model**：
- 输入：每关节 $W$-步 state–action 历史 $h_t^i = \{q_j^i, a_j^i\}_{j=t-W+1}^{t}$（单关节 2-dim × $W$）
- 输出：$\hat{q}_{t+1}^i$（增量预测 $\Delta q$）
- 损失函数：$\mathcal{L}_{dyn} = \|\hat{q}^{(t+1)} - q^{(t+1)}\|_2$
- 预训练：Isaac Gym 仿真数据初始化
- 微调：真实世界 Chaos Box 数据，**4000 轨迹/类别**（5 类 → 共 ~20,000 轨迹），仅需 **~15 分钟**采集
- 训练硬件：**8× A10 GPU**，batch size 64，**2 epochs**，约 2 天

**Stage E — Residual Policy**：
- 输入：$[o_t^{gene},\; a_t^{base},\; \hat{q}_{t+1}^{sim},\; \hat{q}_{t+1}^{real}]$
- 损失函数：$\mathcal{L}_{res} = \|q_{t+1}^{sim} - \hat{q}_{t+1}^{res}\|_2$（学习让真实世界下一状态匹配仿真器）
- 训练数据：Stage B 的 BC 训练集中的仿真轨迹
- 训练：监督学习，**2 epochs**，约 **13 小时**

### 4.2 主要结果

| 设置 | Domain Rand | 整体神经动力学 | **DexNDM** |
|-----|-------------|--------------|----------|
| 简单立方体 | 78% | 82% | **95%** |
| 高长宽比 | 23% | 31% | **76%** |
| 复杂形状 | 18% | 25% | **68%** |
| 多样腕部姿态 | 35% | 42% | **81%** |

### 4.3 消融研究

| 变体 | 成功率下降 |
|-----|----------|
| 无关节级分解 | -35% |
| 无残差策略 | -28% |
| 有限训练数据 | -22% |
| 无历史信息 | -41% |

**因果机制分析**：
- **去掉关节级分解 → 成功率 -35%** → 因为全系统建模输入维度从 $3$（每关节）激增到 $3 \times 16 = 48$，相同数据量下拟合质量骤降
- **去掉残差策略 → 成功率 -28%** → 因为仅靠动力学模型修正仿真状态无法弥补策略层面的行为偏移，需策略级残差校正动作分布
- **去掉历史信息 → 成功率 -41%（最大降幅）** → 因为单帧本体感受无法推断关节耦合、物体负载等隐变量，历史窗口是隐式系统辨识的唯一信号源
- **减少训练数据 → 成功率 -22%** → 关节级分解的高数据效率使即使数据减少性能下降也相对可控

### 4.4 数据效率

**惊人发现**：仅需 **15 分钟**真实世界数据即可训练有效的关节级动力学模型！

对比：
- 整体神经动力学：需要 2+ 小时
- Domain Randomization：无需真实数据但性能差

---

## 4.5 工程关键细节 (Engineering Tricks)

- **1D Conv 时序编码**：使用 1D 卷积而非 LSTM/Transformer 处理本体感受历史，推理延迟更低（< 1ms/关节），适合 kHz 级控制频率
- **关节间参数不共享**：每个关节独立网络，因腱驱动系统中各关节动力学特性差异显著（对指关节 vs 拇指关节的摩擦/耦合完全不同）
- **增量预测**：模型预测 $\Delta q_j$ 而非绝对 $q_j^{t+1}$，利用残差学习避免学习恒等映射，提升小变化量的预测精度
- **无需精确时钟同步**：自主数据采集仅记录本体感受流，不涉及外部传感器同步，降低系统复杂度
- **随机负载多样化**：采集时施加的随机外部负载覆盖不同质量/惯量，使关节动力学模型对未知物体隐式鲁棒

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **数据效率卓越**：15 分钟真实数据
- **泛化性强**：单一策略处理多样物体和姿态
- **无需物体追踪**：自主数据采集
- **模块化**：关节动力学可独立更新

### 局限性

**理论层面**：
- 关节级独立性假设在强耦合系统（如腱驱动的对指运动）中可能失效——多关节同时快速运动时交叉耦合力矩可能超出"净效应"建模能力
- 仅建模前向动力学，缺乏逆动力学约束，无法保证预测的物理一致性（如能量守恒）

**算法层面**：
- 残差策略依赖基策略的合理性——若仿真策略在高速操作下偏差过大，残差修正空间不足
- 仅限旋转任务，未验证在位移、滑动等其他操作技能上的可迁移性

**工程层面**：
- 仍需高质量仿真器训练基策略（MuJoCo/Isaac Gym）
- 关节独立模型数量 = 关节自由度数，16 DoF 需 16 个网络（可通过参数共享+条件化缓解）
- 仅使用本体感受，无触觉反馈；未扩展到双手协作

**替代方案**：域随机化在简单任务上更简洁（无需真实数据）；整体式 world model（如 DayDreamer）在低维系统上可同时建模全局动力学

### 对转笔/Sim-to-Real 的启发

> [!tip] 可迁移到转笔任务的关键 Ideas
> 1. **关节级动力学直接用于转笔 Sim-to-Real**：转笔中灵巧手的腱驱动摩擦、关节弹性是最大 sim-to-real gap 来源，DexNDM 仅需 15 分钟数据即可建模，可直接集成到 PPO 管道
> 2. **自主数据采集启发**：转笔的手部数据采集可以不追踪笔状态——手指在不同负载下自由运动即可建模真实关节动力学
> 3. **残差策略作为 Sim-to-Real 微调**：仿真训练 PPO 转笔策略后，用 DexNDM 预测真实关节响应，训练残差网络修正动作，避免完全重训练
> 4. **从旋转到转笔的自然扩展**：DexNDM 的物体旋转与转笔运动学结构相似（绕轴旋转），但转笔需更精细的相位控制和非接触惯性飞行阶段估计

### 与其他方法的对比

| 方法 | 适用场景 | 数据需求 | 泛化范围 |
|-----|---------|---------|---------|
| Domain Rand | 简单任务 | 无真实数据 | 窄 |
| System ID | 特定系统 | 专门数据 | 极窄 |
| 整体神经动力学 | 单一任务 | 大量数据 | 中 |
| **DexNDM** | **通用旋转** | **少量数据** | **宽** |

---

## 6. 对灵巧操作的启发 (Implications)

### 关节级分解的普适性

```
DexNDM 的核心思想可扩展到：

1. 其他操作技能
   In-hand translation, Tool use, Fine manipulation
   
2. 其他机器人系统
   Humanoid hands, Soft grippers, Tendon-driven robots
   
3. 其他感知模态
   Joint-wise + Tactile-wise 联合分解
```

### 与其他论文的联系

- **DEXTRACK**：DexNDM 提供动力学模型，DEXTRACK 提供跟踪控制器
- **EUREKA**：LLM 生成的奖励 + DexNDM 的 sim-to-real = 更强的技能学习
- **Residual LfD**：DexNDM 的残差策略思想与 rLfD 一致

---

## 7. 演进脉络定位 (Evolution Context)

```
Sim-to-Real for Manipulation
        ↓
Domain Randomization (Tobin, 2017)
├── Parameter randomization
└── Visual randomization
        ↓
OpenAI Rubik's Cube (2019)
├── ADR (Automatic Domain Randomization)
└── Extensive simulation training
        ↓
Neural Dynamics for Locomotion
├── RMA (2021): Implicit adaptation
└── DayDreamer (2023): World models
        ↓
██████████████████████████████████████
█  DexNDM (2024)                     █
█  • Joint-wise factorization        █
█  • Autonomous data collection      █
█  • Single policy, broad objects    █
██████████████████████████████████████
        ↓
未来: Multi-modal sensing + Joint dynamics
```

---

## 8. 核心代码逻辑

```python
class JointwiseDynamicsModel:
    """关节级神经动力学模型"""
    
    def __init__(self, n_joints, history_len=50):
        self.n_joints = n_joints
        self.history_len = history_len
        self.models = [JointModel() for _ in range(n_joints)]
        
    def predict_next_state(self, proprio_history):
        """
        proprio_history: [batch, n_joints, history_len, 3]
                         3 = (q, q_dot, tau)
        """
        predictions = []
        for j in range(self.n_joints):
            h_j = proprio_history[:, j]  # [batch, history_len, 3]
            delta_q_j = self.models[j](h_j)
            predictions.append(delta_q_j)
        return torch.stack(predictions, dim=1)


class ResidualPolicy:
    """残差策略：弥合 sim-to-real gap"""
    
    def __init__(self, base_policy, dynamics_model):
        self.base_policy = base_policy  # 仿真训练
        self.dynamics = dynamics_model  # DexNDM
        self.residual_net = MLP(...)
        
    def get_action(self, state, proprio_history):
        # 1. 基策略动作
        a_base = self.base_policy(state)
        
        # 2. 仿真器预测 vs DexNDM 预测
        s_sim = self.simulate_step(state, a_base)
        s_real = self.dynamics.predict_next_state(proprio_history)
        
        # 3. 残差修正
        delta_a = self.residual_net(
            torch.cat([state, s_sim, s_real, a_base], dim=-1)
        )
        
        return a_base + delta_a


# 自主数据采集
def autonomous_data_collection(hand, duration_minutes=15):
    """无需物体、无需人工复位的数据采集"""
    data = []
    for t in range(duration_minutes * 60 * control_freq):
        # 随机负载（模拟物体）
        if t % reset_interval == 0:
            apply_random_load(hand)
        
        # 随机动作
        action = sample_random_action()
        hand.apply_action(action)
        
        # 记录本体感受（无需视觉！）
        proprio = hand.get_proprioception()  # (q, q_dot, tau)
        data.append(proprio)
    
    return data
```

---

## 9. 与知识体系的联系 (Foundation Links)

### 与 [[Dynamics]] 的数学对应
- DexNDM 的 $\dot{q}_j = f_j(h_j^{proprio})$ 是经典 Newton-Euler 递推 $\tau_j = I_j \ddot{q}_j + \text{bias}_j$ 的数据驱动化：用神经网络替代解析的惯量矩阵 $I_j$ 和偏置力矩
- 历史窗口 $h_j$ 隐式实现了经典[[Dynamics|系统辨识]]——提供等效于惯量参数和接触力的信息

### 与 [[ReinforcementLearning]] 的数学对应
- 残差策略 $a = \pi_{base}(s) + \pi_{res}(s, \hat{s}_{sim}, \hat{s}_{real})$ 中，动力学差异 $(\hat{s}_{sim} - \hat{s}_{real})$ 显式编码 reality gap
- 与 [[ReinforcementLearning|RMA 的 adaptation module]] 一脉相承：从"推断环境参数"推广到"预测状态差异"

### 与 [[ContactMechanics]] 的数学对应
- 手指-物体接触的复杂性（摩擦力、接触形变、非光滑切换）被压缩到关节级 $f_j$ 中隐式建模
- 这是对经典"接触模式枚举"的数据驱动替代——通过学习免去模式切换的组合爆炸

### 跨方法对比

| 维度 | Domain Rand | System ID | RMA | **DexNDM** |
|------|------------|-----------|-----|-----------|
| 真实数据需求 | 0 | 中等 | 少量 | **15 min** |
| 物体泛化 | 需重训 | 不适用 | 有限 | **单策略多物体** |
| 计算成本 | 极高 | 低 | 中 | **低** |
| 理论保证 | 无 | 有 | 无 | 无 |
| 触觉需求 | 无 | 可选 | 无 | 无 |

> [!note] 跨簇定位：$\Delta_T$ 修正的"粒度谱" + RMA 的关节级下放（连接 sim-to-real × in-hand rotation 两簇）
> DexNDM 是 **sim-to-real 簇 × in-hand rotation 簇**的交汇点。在 [[A Survey of Sim-to-Real Methods in RL|Survey]] 的 MDP 四元素里属 $\Delta_T$（转移 gap），但它揭示 **$\Delta_T$ 修正存在"粒度谱"**：
>
> | 粒度 | 代表 | 修正对象 |
> |------|------|----------|
> | 系统级 | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] | 一个 extrinsics $z$（物体参数） |
> | 动作级 | [[Grounded Action Transformation\|GAT]] | 动作映射 $a_{sim}\to a_{real}$ |
> | **关节级** | **DexNDM** | 每关节 $f_j$（净效应动力学） |
>
> 越细粒度 → 数据效率越高（DexNDM **15 分钟** vs DR 上万年仿真）、泛化越强（单策略多物体）。
> **新 insight——关节级分解 = "RMA 的降维"**：[[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] 用 RMA 学**系统级** extrinsics，DexNDM 把 RMA **下放到关节级**（每关节本体历史推断净效应）——"用运动链分解的结构先验放松数据/泛化代价"，与跨簇 meta-insight"用结构先验放松保守约束"同源。它给出与 [[Lessons from Learning to Spin Pens|Spin Pens]]（open-loop replay）、[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]（蒸馏）并列的第三条 in-hand rotation sim-to-real 路线：关节级动力学 grounding。
