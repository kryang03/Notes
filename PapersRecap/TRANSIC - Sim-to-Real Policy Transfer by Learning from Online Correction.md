---
tags:
  - paper
  - sim-to-real
  - human-in-the-loop
  - residual-learning
  - manipulation
aliases:
  - TRANSIC
paper-year: 2024
read-date: 2026-02-01
paper-pdf: "[[Papers/TRANSIC Sim-to-Real Policy Transfer by Learning from Online Correction.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[ComputationalGeometry]]"
---

# TRANSIC: Sim-to-Real Policy Transfer by Learning from Online Correction

> [!abstract] 核心概要
> 提出一种人在回路的 sim-to-real 迁移方法：人类观察并在线校正仿真策略的失误，收集校正数据训练残差策略，从而 holistically 解决各种 sim-to-real gap。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 人类干预与在线校正框架
> - [[ControlTheory]] - 残差策略补偿未建模动态
> - [[RepresentationLearning#4. Point Cloud Representation: 3D 几何的深度学习基础 (Deep Learning on 3D Geometry)]] - 点云作为视觉输入减小感知 gap
>
> **核心技术**: Residual Policy, Online Human Correction, Action Space Distillation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
让人类在线监督和校正机器人执行，从人类校正数据中学习残差策略，以数据驱动方式整体性解决各类 sim-to-real gap。

### 直观隐喻
就像驾校教练坐在副驾——当学员（仿真策略）要出错时，教练会接管方向盘纠正。通过记录这些"接管"数据，学员能学会自己避免同样的错误。

### 领域定位
```
传统 Sim-to-Real:
├── System Identification: 需要领域知识
├── Domain Randomization: 盲目覆盖
└── Real-World Adaptation: 需要精确建模

TRANSIC:
└── Human-in-the-Loop + Residual Learning: 领域无关的整体性解决
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | TRANSIC 突破 |
|---------|------|-------------|
| Domain Randomization | 需要知道什么需要随机化 | 人类隐式识别 gap |
| System Identification | 需要精确建模 | 数据驱动 |
| 直接微调 | 灾难性遗忘 | 残差策略保留基策略 |
| 从头 IL | 需要大量真实数据 | 利用仿真策略 |

### 关键贡献点
1. **Action Space Distillation**: 先用 OSC 训练 teacher，再蒸馏到关节空间 student
2. **Residual Policy from Correction**: 从人类校正数据学习残差动作 $a^R = q^{post} \ominus q^{pre}$
3. **Gated Residual**: 学习门控函数决定何时应用残差

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 整体框架

```
Phase 1: Simulation Training
├── Teacher Policy: RL with OSC (操作空间控制)
└── Student Policy: BC from teacher (关节位置控制)
                    ↓
Phase 2: Human-in-the-Loop Data Collection
├── Deploy base policy π^B
├── Human monitors and intervenes when needed
└── Collect correction dataset D^H
                    ↓
Phase 3: Residual Policy Learning
├── Train π^R from D^H
└── Integrate: π^deployed = π^B ⊕ 𝟙_g π^R
```

### 3.2 为什么需要 Action Space Distillation

> [!important] 控制器 gap 是核心问题
> OSC (Operational Space Control) 需要精确的机器人参数（摩擦、质量、惯量），在真实机器人上难以实现。

$$
\text{Teacher: } a^{\text{OSC}} \xrightarrow{\text{Relabel}} a^{\text{joint}} \xrightarrow{\text{BC}} \text{Student}
$$

**训练目标**:
$$
\mathcal{L}^{\text{student}} = -\mathbb{E}_{\mathcal{D}^{\text{teacher}}}[\log \pi_\theta^{\text{student}}] + \beta \mathbb{E}_{\mathcal{D}^{\text{pcd}}}[\|\phi(P^{\text{real}}) - \phi(P^{\text{sim}})\|^2]
$$

第二项是点云编码器的对齐正则化。

### 3.3 人类校正数据收集

**协议**:
```
at each timestep t:
    a_t^B ~ π^B  # base policy action
    execute a_t^B
    
    if human_decides_to_intervene:
        1^H_t = 1
        human takes control via teleoperation
        record (q^{pre}_t, q^{post}_t)  # 干预前后状态
    else:
        1^H_t = 0
    
    D^H ← D^H ∪ {(1^H_t, q^{pre}_t, q^{post}_t)}
```

### 3.4 残差策略学习

**为什么用残差而不是直接微调？**
- 人类校正通常是非马尔可夫的（依赖历史）
- 直接微调会导致大幅动作变化和模型崩溃
- 残差是小的补偿，更稳定

**残差动作定义**:
$$
a^R = q^{post} \ominus q^{pre}
$$

- 连续变量: 数值差
- 离散变量（如 gripper）: 异或

**训练目标**:
$$
\mathcal{L}^{\text{residual}} = -\mathbb{E}_{\mathcal{D}^H}[\log \pi_\psi^R(a^R | \cdot)]
$$

### 3.5 Gated Residual Policy

```python
# 推理时
if g_ψ(observation) > threshold:  # 门控函数
    a_deployed = a_B + a_R  # 应用残差
else:
    a_deployed = a_B  # 仅基策略
```

门控函数与残差策略共享编码器，通过分类损失联合训练。

### 3.6 任务分解

四个基础技能组成家具组装:
1. **Stabilize**: 稳定桌腿
2. **Reach and Grasp**: 到达并抓取
3. **Insert**: 插入对齐
4. **Screw**: 旋转拧紧

## 4. 实验与验证 (Experiments)

### 实验设置
- **仿真**: Isaac Gym
- **任务**: FurnitureBench 家具组装（高精度接触丰富）
- **人类数据**: SpaceMouse 遥操作

### 关键对比

| 方法 | Stabilize | Insert | Screw | 数据需求 |
|-----|-----------|--------|-------|---------|
| Domain Randomization | 低 | 低 | 低 | 0 真实 |
| BC (从头) | 中 | 中 | 中 | 大量真实 |
| **TRANSIC** | **高** | **高** | **高** | **少量校正** |

### Scaling 特性

> [!note] 人类努力的扩展性
> TRANSIC 性能随人类干预数据量单调提升，表现出良好的数据效率。

## 5. 批判性分析 (Critical Analysis)

### 优势
- **领域无关**: 不需要知道具体 gap 是什么
- **数据高效**: 比从头 IL 需要更少真实数据
- **保留仿真策略优势**: 残差学习不破坏已学知识
- **整体性**: 同时解决感知、控制、动力学多种 gap

### 局限性
- 需要人类在线参与（虽然数据量较少）
- 门控函数可能学得不够精确
- 高精度任务（如 Screw）仍需较多校正

### 未来方向
- 自动检测需要干预的状态
- 主动学习选择最有价值的校正
- 多任务残差策略共享

## 6. 对灵巧操作的启发 (Implications)

1. **Action Space 选择**: OSC 易于学习但难迁移，关节空间蒸馏是折中方案
2. **残差 > 微调**: 对于分布外数据，残差学习更稳定
3. **人类知识的隐式传递**: 人类无需明确知道 gap 是什么，只需能纠正
4. **点云视觉**: 相比 RGB，点云在 sim-to-real 中更鲁棒

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── HIL-SERL (2024): 人在回路 RL
├── RialTo (2024): Real-to-Sim-to-Real
└── 残差学习: Residual DMP, Residual RL

本论文: TRANSIC
├── Action Space Distillation (OSC → Joint)
├── Residual from Human Correction
└── Gated Deployment

后续影响:
├── 自动干预检测
├── 主动人类反馈请求
└── 通用 sim-to-real 框架
```

## 8. 与 HIL-SERL 的对比

| 方面 | HIL-SERL | TRANSIC |
|-----|----------|---------|
| 基策略来源 | 真实世界 BC | 仿真 RL |
| 人类角色 | 在线 RL 反馈 | 校正数据收集 |
| 核心思想 | 人类引导 RL 探索 | 人类校正学残差 |
| 数据需求 | 持续在线参与 | 一次性收集后离线 |
| 适用场景 | 真实世界策略改进 | Sim-to-Real 迁移 |
