---
tags:
  - paper
  - dexterous-manipulation
  - visuotactile
  - in-hand-manipulation
  - transformer
aliases:
  - RotateIt
paper-year: 2023
read-date: 2026-02-01
venue: CoRL 2023
paper-pdf: "[[Papers/General In-Hand Object Rotation with Vision and Touch.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
---

# RotateIt: General In-Hand Object Rotation with Vision and Touch

> [!abstract] 核心贡献
> 针对"纯本体策略只能绕阻力最小的 z 轴旋转、无法处理多轴与复杂形状"这一瓶颈，提出 **Visuotactile Transformer**：把视觉(深度)+触觉(接触位置)+本体的历史序列融合，在线推断物体形状 $z^{shape}$ 与物理属性 $z^{phys}$ 这组 extrinsics，用单一策略实现 x/y/z 多轴手内旋转。结构性洞见：**多轴旋转的真正瓶颈是"几何可观测性"——非 z 轴旋转强依赖物体形状，必须显式编码而非寄望隐式适应。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 从特权信息到 extrinsics 编码
> - [[RepresentationLearning]] - PointNet 编码物体形状
> - [[SignalProcessing#5. 状态估计：从局部触觉到全局语义]] - Transformer 融合多模态时序信息
> - [[RepresentationLearning]] - 前景物体深度作为视觉表示
>
> **核心技术**: Visuotactile Transformer, Object Shape Encoding via PointNet, Multi-axis Rotation with Extrinsics

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
通过 Visuotactile Transformer 融合视觉、触觉、本体感觉的历史序列，在线推断物体形状和物理属性，实现多轴手内旋转。

### 直观隐喻
就像人类在旋转一个新物体时，会同时通过眼睛观察形状、手指感受接触点，并结合历史经验快速适应——RotateIt 用 Transformer 实现了这种多感官融合与时序推理。

### 领域定位
```
HORA (2023): 本体感觉 + 隐式物理属性推断 (仅 z 轴)
    ↓
RotateIt (2023): 视觉 + 触觉 + Transformer (多轴旋转) ← 本文
    ↓
Robot Synesthesia (2024): 点云触觉统一表示
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | RotateIt 突破 |
|---------|------|--------------|
| HORA | 仅本体感觉 | 视觉 + 触觉多模态 |
| Chen et al. | 仅视觉 | 加入触觉提升性能 |
| 多数工作 | 仅 z 轴旋转 | x/y/z 三轴旋转 |
| MLP 编码器 | 无时序建模 | Visuotactile Transformer |

### 关键贡献点
1. **显式形状编码**: 用 PointNet 将物体形状编码为 $z_t^{shape}$，这是多轴旋转的关键
2. **Visuotactile Transformer**: 处理多模态时序流，推断特权信息的表示 $\hat{z}_t$
3. **统一框架**: 一个策略处理多种物体的多轴旋转

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.0 变量来源追踪

理解全文的钥匙：Oracle 用**特权真值** $z_t$ 训练，Student 部署时只能用 Visuotactile Transformer 的**预测** $\hat{z}_t$ 代替——这一对区分是整个 Teacher-Student 框架存在的理由（与 [[Lessons from Learning to Spin Pens|Spin Pens]] 的"特权 vs 本体"同构，但 RotateIt 走"预测 extrinsics"、Spin Pens 走"开环回放"，见 §7）。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $q_t$ | $\mathbb{R}^{16}$，取 $q_{t-2:t}$ | 观测（本体） | 否（输入） | 关节角历史 | 是位置非速度；与动作历史拼成 $\mathbb{R}^{96}$ |
| $a_{t-1}$ | $\mathbb{R}^{16}$，取 $a_{t-3:t-1}$ | 网络上一步输出 | 否（作输入） | PD 位置目标 | 动作是 target pose，**非力矩** |
| $o_t^{depth}$ | 深度图 | 观测（视觉） | 经 ConvNet 带梯度 | 物体前景深度 | 归一化到**手掌参考系**消相机外参；用深度非 RGB 减 gap |
| $o_t^{touch}$ | $\mathbb{R}^{N_c\times9}$ | 观测（触觉） | 经 MLP 带梯度 | 接触位置(8 维 one-hot)+手指索引 | **one-hot 离散**非连续坐标——换噪声鲁棒 |
| $z_t^{phys}$ | $\mathbb{R}^8$ | **特权**（仿真真值） | 否 | 质量/质心/摩擦/尺度/恢复系数+位姿 | 真机不可观测 |
| $z_t^{shape}$ | $\mathbb{R}^{c_p}$ | **特权**几何→PointNet | PointNet 参数带梯度 | 物体形状编码 | 部署靠 $\hat{z}_t$ 预测代偿 |
| $\hat{z}_t$ | $\mathbb{R}^{\dim z}$ | Visuotactile Transformer 输出 | 是 | 预测的 extrinsics $[z^{phys},z^{shape}]$ | **部署用 $\hat{z}_t$ 代替特权 $z_t$**——T-S 信息瓶颈 |
| $k$ | $\mathbb{R}^3$ unit | 任务指令 | 否 | 期望旋转轴 | $k$ 是指令轴，$\neq$ 实际角速度 $\omega$ |
| $\omega$ | $\mathbb{R}^3$ | **特权**（仿真真值） | 否 | 物体角速度 | 进入奖励 $r_{rotr},r_{rotp}$，真机不可直接测 |

### 3.1 Oracle Policy Training

**特权信息编码**:
$$
z_t = [z_t^{phys}, z_t^{shape}]
$$

- $z_t^{phys} \in \mathbb{R}^8$: 物体物理属性（质量、质心、摩擦、尺度、恢复系数）+ 位姿
- $z_t^{shape} \in \mathbb{R}^{c_p}$: PointNet 编码的物体形状

> [!important] 形状编码的重要性
> 显式编码物体形状是 RotateIt 相比 HORA 的关键差异，对复杂物体的操作至关重要。

**观测与输出**:
- 输入: $p_t = [q_{t-2:t}, a_{t-3:t-1}] \in \mathbb{R}^{96}$（关节位置 + 动作历史）
- 输出: PD 控制器目标 $a_t \in \mathbb{R}^{16}$

**奖励函数**:
$$
r = r_{\text{rotr}} + \lambda_{\text{rotp}} r_{\text{rotp}} + \lambda_{\text{pose}} r_{\text{pose}} + \lambda_{\text{linvel}} r_{\text{linvel}} + \lambda_{\text{work}} r_{\text{work}} + \lambda_{\text{torque}} r_{\text{torque}}
$$

- $r_{\text{rotr}} = \max(\min(\omega \cdot k, r_{\max}), r_{\min})$: 沿期望轴的角速度
- $r_{\text{rotp}} = -\|\omega \times k\|_1$: **关键设计** — 惩罚非期望轴的角速度

### 3.2 Visuotactile Transformer

```
输入流:
├── 物体深度 o_t^{depth} → 3-layer ConvNet → f_t^{depth}
├── 触觉接触位置 o_t^{touch} → MLP → f_t^{touch}  
├── 关节位置 q_t
└── 上一步动作 a_{t-1}

    ↓ Concatenate
f_t = [f_t^{depth}, f_t^{touch}, q_t, a_{t-1}]

    ↓ Transformer φ
f_T = {f_{t-k}, ..., f_{t-1}, f_t}

    ↓ Output
ẑ_t = φ(f_T)  // 预测的 extrinsics 编码
```

**训练目标**:
$$
\mathcal{L} = \|z_t - \hat{z}_t\|_2^2 + \|a_t - \hat{a}_t\|_2^2
$$

### 3.3 触觉表示

**Sim-to-Real 策略**:
- 仿真: 直接使用模拟器提供的接触位置
- 真实: 从全向视觉触觉传感器追踪高亮像素运动

**离散化接触位置**:
$$
o_t^{touch} \in \mathbb{R}^{N_c \times 9}
$$
- $N_c$: 接触点数量
- 9 维: 8 维离散位置 one-hot + 手指索引

### 3.4 视觉表示

**为什么用深度而非 RGB**:
1. 深度是物体形状的良好抽象
2. RGB 的 sim-to-real gap 更大
3. 通过 Segment Anything 分割前景物体减小 gap

### 3.5 前置理论从零推导：为什么非 z 轴旋转更难、形状为何必须显式编码

范本要求把"形状编码有效"从经验观察推到物理必然。根在刚体旋转的惯性张量与陀螺项。

**第 1 步——刚体旋转的欧拉方程。** 物体角动量 $L=I\omega$（$I$ 为惯性张量，依赖物体几何与质量分布）。欧拉方程：
$$I\dot{\omega} + \omega\times(I\omega) = \tau,$$
$\tau$ 是各手指接触力矩之和。

**第 2 步——绕主轴 vs 非主轴。** 当 $\omega$ 平行于惯性主轴时 $I\omega\parallel\omega$，陀螺项 $\omega\times(I\omega)=0$，旋转"自然稳定"、所需力矩小。当 $\omega$ 偏离主轴，$\omega\times(I\omega)\neq 0$ 产生进动力矩，必须由手指额外补偿才能维持定轴旋转。

**第 3 步——主轴方向由形状决定 ⇒ 形状不可省。** 惯性张量 $I$ 完全由物体几何决定。对细长/不规则物体，绕 x/y 轴旋转就是绕**非主轴**旋转，所需补偿力矩依赖 $I$，而 $I$ 只能从**形状**推出。这正是 PointNet 显式编码 $z^{shape}$ 的物理必然——它给策略提供推算陀螺项所需的几何先验（直接解释 §4 消融"去形状→x/y 轴 RotR 掉 ~30%、z 轴几乎不受影响"）。

**第 4 步——$r_{\text{rotp}}$ 的物理含义。** $r_{\text{rotp}}=-\|\omega\times k\|_1$ 惩罚角速度对指令轴 $k$ 的偏离，本质是**抑制陀螺进动导致的轴漂移**；没有它策略会滑向阻力最小的主轴（通常 z 轴），即 §4 消融"去 $r_{\text{rotp}}$→非目标轴严重偏离"。

**第 5 步——extrinsics 即隐式系统辨识。** $z^{phys}$（质量/摩擦/质心）真机不可观测，Visuotactile Transformer 从历史 $(q,a,o^{depth},o^{touch})$ 序列回归出 $\hat{z}_t$，等价于在线 system ID。这与 [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] 的 RMA 同源（[[ReinforcementLearning|RL §5]] 特权学习），差别是 RotateIt 加了视触觉输入、用 Transformer 做时序辨识。

**退化情形（解释 HORA 为何 z 轴够用）。** 球/立方体惯性张量近各向同性、主轴退化，无显著形状依赖——故 HORA 纯本体在 z 轴 RotR 99.83 已够好，但一到 x/y 轴（79–82）就被 RotateIt（118–125）拉开。

### 3.6 概念边界与符号陷阱

- **特权 $z_t$ vs 预测 $\hat{z}_t$**：性能上界由 Oracle（用真值 $z_t$）决定，sim-to-real gap 由 $\hat{z}_t$ 预测质量决定——Teacher-Student 的根本切分。
- **$k$（指令轴）vs $\omega$（实际角速度）**：奖励 $r_{\text{rotr}},r_{\text{rotp}}$ 的作用就是把 $\omega$ 对齐到 $k$。
- **触觉 one-hot 离散 vs 连续坐标**：刻意的信息瓶颈，牺牲定位分辨率换 sim-to-real 鲁棒。
- **深度图归一化到手掌参考系**：消除相机外参偏差，否则视觉 sim-to-real gap 不可控。
- **策略 ~10 Hz vs PD 1 kHz**：动作是低频位置目标，由高频 PD 跟踪，避免在力矩空间直接迁移。
- **每轴独立策略**：x/y/z 分别训练而非单一任意轴策略——这是与 [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]（真正任意轴）的关键区别，也是 §5 算法局限的来源。

## 4. 实验与验证 (Experiments)

### 训练设置
- **仿真**: IsaacGym, 4096 并行环境
- **算法**: PPO (Asymmetric Actor-Critic)
- **控制频率**: 策略 ~10 Hz，PD 控制器 1 kHz
- **域随机化**: 物体质量/摩擦/尺度 + 各物理参数

### 关键结果

| 方法 | x-axis RotR | y-axis RotR | z-axis RotR |
|------|------------|------------|------------|
| HORA | 79.13 | 82.25 | 99.83 |
| w/o shape | 85.10 | 99.92 | 129.38 |
| **Oracle** | **125.23** | **118.26** | **140.90** |

**核心发现**:
1. 形状编码显著提升性能（尤其是 x/y 轴）
2. 视觉和触觉都对性能有贡献
3. 学到的表示能恢复 3D 形状

### Ablation 因果链

| 移除组件 | 效果变化 | 因果机制 |
|---------|---------|--------|
| 去掉 PointNet 形状编码 | x/y 轴 RotR 下降 ~30% | 非 z 轴旋转强依赖物体几何，无形状信息策略只能学到"平均"手势 |
| 去掉触觉 | RotR 下降 ~15%，掉落率上升 | 触觉提供接触状态实时反馈，缺失后无法感知滑动/脱手 |
| 去掉视觉深度 | 性能下降但弱于去触觉 | 深度主要贡献形状先验（与 PointNet 冗余），触觉提供不可替代的实时物理信号 |
| MLP 替换 Transformer | 性能下降 ~20% | MLP 仅处理当前帧，无法利用时序一致性推断时变物理属性 |
| 去掉 $r_{\text{rotp}}$ 惩罚 | 非目标轴旋转严重偏离 | 无交叉轴惩罚时策略倾向于绕阻力最小轴（z 轴）旋转 |

### 工程关键细节 (Engineering Tricks)

- **前景分割**: SAM 分割真实深度图前景物体，消除背景深度噪声对 sim-to-real 的干扰
- **触觉离散化**: 接触位置 one-hot 而非连续坐标 → 对传感器定位误差更鲁棒
- **深度归一化**: 深度图归一化到手掌参考系，消除相机外参偏差
- **PD 控制**: 低频策略 (~10 Hz) + 高频 PD (1 kHz)，避免力矩空间的 sim-to-real gap
- **每轴独立**: 虽限制通用性，但避免多目标旋转的模式坍缩

## 5. 批判性分析 (Critical Analysis)

### 5.1 理论局限性三维度分析

| 维度 | 局限性 | 替代方案 |
|------|--------|--------|
| **理论** | Transformer 时序建模无物理先验——隐式推断无法保证收敛到真实物理参数 | 引入 [[Dynamics]] 惯性矩阵结构约束 extrinsics 空间 |
| **算法** | 每轴独立策略无法处理任意姿态轨迹；Teacher-Student 蒸馏存在 $\hat{z}_t$ 信息瓶颈 | 多轴统一课程（如 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]）|
| **工程** | SAM 分割增加 ~50ms 延迟；4 个全向触觉传感器成本高；触觉 sim-to-real gap 显著 | 轻量化分割 + 低成本触觉（如 [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] 的 ALLSIGHT）|

### 5.2 与灵巧手转笔的可迁移启发

> [!tip] 对 PPO 转笔方案的具体启发
> 1. **形状编码**: 笔杆近圆柱体时 PointNet 可能冗余，但泛化到不规则笔形时显式形状编码成为关键
> 2. **$r_{\text{rotp}}$ 惩罚**: 转笔也面临非目标轴偏移，可直接借鉴交叉轴角速度惩罚设计
> 3. **触觉降维**: binary 触觉在 sim-to-real 上比连续量更鲁棒，对转笔触觉 reward shaping 有参考价值
> 4. **时序融合**: 若引入触觉/视觉应考虑 Transformer backbone 替代 MLP 拼接
> 5. **分阶段课程**: 每轴独立→融合的路线可迁移为转笔课程（先水平旋转→竖直轴→任意轴）

## 6. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- PPO + Teacher-Student：Oracle 在特权信息 $z_t$ 下训练 → Student 通过 Transformer 从历史观测推断 $\hat{z}_t$，对应 [[ReinforcementLearning|Sim-to-Real 特权学习]]
- 奖励工程：$r = r_{\text{rotr}} + \lambda_{\text{rotp}} r_{\text{rotp}} + ...$ 是典型多目标奖励分解

### 与 [[SignalProcessing]] 的联系
- Transformer 自注意力 $\text{Attn}(Q,K,V) = \text{softmax}(QK^T/\sqrt{d})V$ 本质是多传感器信号的自适应滤波
- 触觉 one-hot 编码类似空间量化，牺牲分辨率换取噪声鲁棒性

### 与 [[RepresentationLearning]] 的联系
- PointNet 形状编码：permutation-invariant $z_t^{shape} = \text{MaxPool}(\text{MLP}(p_i))$
- Teacher-Student 蒸馏是从特权表征到感知表征的信息压缩

### 与 [[ContactMechanics]] 的联系
- 触觉传感器捕获的接触位置直接编码了接触点几何信息

## 7. 跨方法对比与 in-hand rotation 领域定位

### 7.1 跨方法结构性对比

| 维度 | RotateIt | HORA | AnyRotate | Touch Dexterity | [[Lessons from Learning to Spin Pens\|Spin Pens]] |
|------|----------|------|-----------|----------------|-----------|
| **感知模态(部署)** | 视觉+触觉+本体 | 仅本体 | 稠密触觉+本体 | 纯触觉+本体 | 纯本体 |
| **旋转轴** | x/y/z（分别训练） | 仅 z | 任意轴(重力不变) | z | z(多圈) |
| **物体/支撑** | 多形状(有支撑) | 多形状(有支撑) | 多形状(任意朝向) | 多形状 | **笔(无支撑)** |
| **物体编码** | PointNet 显式 | 隐式适应 | 隐式+子目标 | 无 | 点云(特权) |
| **时序模型** | Transformer | MLP+RMA | TCN | LSTM | Temporal Transformer |
| **Sim-to-Real 路线** | SAM+蒸馏 $\hat{z}_t$ | 在线适应 RMA | DR+触觉蒸馏 | 二值化触觉 | **Open-loop Replay** |

### 7.2 演进脉络

```
前置: OpenAI Dactyl(2019) 视觉+DR  →  HORA(2023) 本体+RMA
                                          ↓
本文 RotateIt(2023): Visuotactile Transformer + 显式形状编码 + 多轴
                                          ↓
后续: AnyRotate 任意轴+稠密触觉 · Robot Synesthesia 点云触觉统一 · Touch Dexterity 纯触觉
```

> [!note] 领域级 insight（与 [[Lessons from Learning to Spin Pens#7.2 in-hand rotation 领域级综述（本篇的横向坐标）|Spin Pens §7.2 领域综述]] 互参）
> RotateIt 在领域里的独特贡献是回答了"**多轴**旋转缺什么"——答案是 §3.5 论证的**几何可观测性**：用惯性张量把"显式形状编码"确立为非 z 轴旋转的必要条件，这是 HORA 隐式适应路线触及不到的维度。把本篇放进 Spin Pens §7.2 的三轴坐标系：RotateIt 占据"⟨有支撑⟩×⟨多轴⟩×⟨视触觉可观测⟩"格，它与 AnyRotate 的差距正是"分别训练 x/y/z" vs "单一任意轴"。沿这条线，领域空白仍是"**无支撑+任意轴+纯本体**"——RotateIt 的形状编码 + Spin Pens 的无支撑数据引擎，是攻这格的两块拼图。
