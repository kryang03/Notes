---
tags:
  - paper
  - dexterous-manipulation
  - tactile-sensing
  - sim-to-real
  - in-hand-manipulation
aliases:
  - AnyRotate
paper-year: 2024
read-date: 2026-02-01
paper-pdf: "[[Papers/AnyRotate Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
---

# AnyRotate: Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch

> [!abstract] 核心概要
> 提出 AnyRotate 系统，首次实现重力不变的多轴手内物体旋转，使用稠密特征化 sim-to-real 触觉感知实现 zero-shot 迁移。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL]] - 教师-学生策略蒸馏
> - [[ContactMechanics]] - 稠密接触特征表示
> - [[SignalProcessing]] - 触觉感知模型预测接触姿态与力
> - [[RepresentationLearning#5. Multimodal Fusion & Tactile Intelligence: 触觉与视觉的交响 (Symphony of Vision and Touch in Multimodal Fusion)]] - 触觉图像到接触特征的表征
>
> **核心技术**: Dense Featured Tactile Representation, Gravity-Invariant RL, Auxiliary Goal Formulation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
训练统一策略实现任意手方向、任意旋转轴的手内物体旋转，通过稠密触觉特征实现 zero-shot sim-to-real 迁移。

### 直观隐喻
就像人类可以在闭眼情况下通过手指触觉感知物体位置并完成旋转——AnyRotate 让机器人手具备了这种"盲操作"能力，无论手掌朝上还是朝下。

### 领域定位
```
HORA (2023): 本体感觉 + RMA 适应
    ↓
Touch Dexterity (2023): 纯触觉 z 轴旋转
    ↓
AnyRotate (2024): 稠密触觉 + 重力不变多轴旋转 ← 本文
    ↓
未来: 触觉驱动的任意手内操作
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | AnyRotate 突破 |
|---------|------|---------------|
| HORA | 仅本体感觉 | 稠密触觉特征 |
| Touch Dexterity | 仅 z 轴旋转 | 任意旋转轴 |
| 多数工作 | 仅 palm-up | 重力不变（6 种手朝向） |
| 离散触觉 | 二值接触/位置离散化 | 连续接触姿态+力幅度 |

### 关键贡献点
1. **Auxiliary Goal Formulation**: 将多轴旋转问题转化为移动目标重定向问题，避免角速度奖励的探索困难
2. **Dense Tactile Representation**: 接触姿态 (Rx, Ry) + 接触力幅度 ||F|| 的稠密表示
3. **Sim-to-Real Touch**: 训练 CNN 从触觉图像预测显式接触特征，实现 zero-shot 迁移
4. **Gravity-Invariant Training**: 通过随机初始化手朝向实现重力不变性

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 MDP 建模

$$
\mathcal{M} = (\mathcal{S}, \mathcal{A}, \mathcal{R}, \mathcal{P}, \mathcal{G})
$$

**观测空间** $O_t$：
- 当前/目标关节位置 $q_t, \bar{q}_t \in \mathbb{R}^{16}$
- 指尖位置/姿态 $ft_p \in \mathbb{R}^{12}, ft_r \in \mathbb{R}^{16}$
- 二值接触 $c_t \in \{0,1\}^4$
- **稠密触觉**: 接触姿态 $P_t \in S^8$，接触力幅度 $F_t \in \mathbb{R}^4$
- 期望旋转轴 $\hat{k} \in S^2$

**动作空间**: 相对关节位置 $\Delta\theta \in [-0.026, 0.026]^{16}$ rad，20Hz 控制

### 3.2 Auxiliary Goal Formulation

> [!important] 核心设计
> 将连续旋转问题转化为到达移动目标的问题

$$
\text{Goals}: \quad g_i = R(\hat{k}, i \cdot \delta\theta) \cdot q_0
$$

- 当达到当前目标时，生成新目标（沿旋转轴再转 $\delta\theta$）
- 使用关键点距离定义目标到达：$K(||k_o^i - k_g^i||) < d_{tol}$

### 3.3 稠密触觉表示

```
触觉图像 I_tactile
    ↓ CNN
接触特征 (P, F)
    ├── 接触姿态 P = (Rx, Ry) ∈ S^2  // 球坐标：极角+方位角
    └── 接触力幅度 ||F|| ∈ R
```

**为什么有效**：
- 接触姿态捕获物体在指尖上的位置（比二值接触更精确）
- 力幅度反映抓取稳定性（检测滑动前兆）

### 3.4 奖励设计

$$
r = r_{\text{rotation}} + r_{\text{contact}} + r_{\text{stable}} + r_{\text{terminate}}
$$

| 奖励项 | 含义 |
|-------|------|
| $r_{\text{rotation}}$ | 关键点距离 + 目标达成 bonus + 增量旋转 |
| $r_{\text{contact}}$ | 最大化指尖接触，惩罚非指尖接触 |
| $r_{\text{stable}}$ | 角速度惩罚 + 姿态偏差 + 做功/力矩惩罚 |
| $r_{\text{terminate}}$ | 掉落或旋转轴偏离的早终止惩罚 |

### 3.5 自适应课程

$$
\text{Total Reward} = r_{\text{rotation}} + \lambda_{\text{rew}}(r_{\text{contact}} + r_{\text{stable}})
$$

- $\lambda_{\text{rew}}$ 随平均旋转数线性增长
- 避免在"稳定抓取但不旋转"的局部最优中卡住

### 3.6 Teacher-Student Distillation

```
Stage 1: Teacher (Privileged Info)
├── 物体位置/姿态/角速度
├── 重力方向
└── 当前目标姿态

Stage 2: Student (Real-World Obs)
├── 本体感觉 + 触觉
├── TCN Encoder 处理历史序列
└── MSE(z_t, z̄_t) + NLL(a_t, ā_t) 损失
```

## 4. 实验与验证 (Experiments)

### 实验设置
- **硬件**: 16-DoF Allegro Hand + UR5 + 4 个视觉触觉传感器
- **任务**: 6 种手朝向（palm up/down, thumb up/down, base up/down）× 多旋转轴
- **测试物体**: 10 种未见过的真实世界物体

### 关键结果

| 消融条件 | 旋转性能 |
|---------|---------|
| 无触觉 | 显著下降 |
| 仅二值接触 | 中等性能 |
| 稠密触觉 | **最佳** |

**发现**: 稠密触觉能检测不稳定抓取并触发反应性行为，提高策略鲁棒性。

## 5. 批判性分析 (Critical Analysis)

### 优势
- **首次重力不变**: 6 种手朝向的统一策略
- **Zero-shot Sim-to-Real**: 无需真实世界微调
- **稠密触觉的价值**: 实验证明比离散触觉更有效

### 局限性
- 需要预训练的触觉感知模型（数据收集成本）
- 仅在精确抓取（precision grasp）场景验证
- 物体形状需相对规则（凸/近似凸）

### 未来方向
- 扩展到 finger-gaiting 操作
- 结合视觉进行物体追踪
- 更复杂的力控制策略

## 6. 对灵巧操作的启发 (Implications)

1. **稠密触觉很重要**: 不要过早将触觉信息降维到二值接触
2. **重力不变性**: 通过手朝向随机化实现，而非显式建模重力补偿
3. **Auxiliary Goal > 角速度奖励**: 目标到达比持续旋转更容易学习
4. **Sim-to-Real Touch**: 显式接触特征（姿态+力）比端到端触觉图像更易迁移

## 7. 演进脉络定位 (Evolution Context)

```
前置工作: 
├── OpenAI Rubik's Cube (2019): 视觉 + Domain Randomization
├── HORA (2023): 本体感觉 + RMA
└── Touch Dexterity (2023): 纯触觉 z 轴

本论文: AnyRotate
├── 稠密触觉特征（姿态+力）
├── 重力不变多轴旋转
└── Auxiliary Goal Formulation

## 8. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

**直接可迁移的思想**：
1. **Gravity-Invariant Framework**: 转笔任务中手的姿态变化导致重力对笔的作用方向不断变化，可借鉴本文的重力不变性训练策略，在域随机化中加入手部姿态随机化
2. **Auxiliary Goal Formulation**: 将「转笔角速度维持」和「接触力稳定」作为辅助目标而非直接的奖励信号，可能比精心设计的 dense reward 更鲁棒
3. **触觉信号处理**: 本文将触觉抽象为姿态+力的稠密特征，对于转笔中指腹触觉传感器的 sim-to-real 对齐有参考价值

**局限性对比**: AnyRotate 处理的是准静态旋转，转笔是动态高速操作，其接触模式切换更频繁、惯性效应更显著。
```
