---
tags:
  - paper
  - articulated-manipulation
  - sim-to-real
  - point-cloud
  - reinforcement-learning
aliases:
  - Part-Guided 3D RL
paper-year: 2024
read-date: 2026-02-01
related:
  - "[[ReinforcementLearning]]"
  - "[[ComputationalGeometry]]"
  - "[[RepresentationLearning]]"
---

# Part-Guided 3D RL for Sim2Real Articulated Object Manipulation

> [!abstract] 核心概要
> 提出部件引导的 3D RL 框架，结合 2D 分割和 3D 点云学习无需演示的关节物体操作策略，通过 Frame-consistent Uncertainty-aware Sampling 实现稳定 Sim2Real 迁移。

> [!note] 教科书背景
> 本文的 **不确定性感知采样 (Uncertainty-aware Sampling)** 与 Model-Based RL 中的不确定性建模有相同理论根源。
> 详见 [[ReinforcementLearning#2.6 Model-Based RL (MBRL): 样本效率与世界模型]]：
> - **Aleatoric 不确定性**：分割噪声（本文用熵 $H$ 度量）
> - **Epistemic 不确定性**：帧间不一致（本文用时序滤波缓解）

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] - 基于点云的策略学习
> - [[RepresentationLearning#4. Point Cloud Representation: 3D 几何的深度学习基础 (Deep Learning on 3D Geometry)]] - PointNet 几何特征提取
> - [[RepresentationLearning#3. Implementation: 核心算法实现与物理逻辑 (Core Algorithmic Implementation and Physical Logic)]] - 2D 部件分割预训练
>
> **核心技术**: Part Segmentation, Frame-consistent Uncertainty-aware Sampling (FUS), Versatile RL Policy

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
用 2D 分割网络识别关节物体的部件，将部件信息投射到 3D 点云中引导 RL 策略学习，通过不确定性感知采样实现稳定的 sim-to-real 迁移。

### 直观隐喻
就像人类在开抽屉时会自然地关注把手和抽屉面板——Part-Guided 3D RL 让机器人学会"看"部件结构，而不是被整体形状淹没。

### 领域定位
```
视觉 Affordance 学习 (UMPNet, FlowBot3D): 预测动作点
    ↓
端到端视觉 RL: 样本效率低
    ↓
Part-Guided 3D RL: 部件分割 + 3D 点云 + 高效 RL ← 本文
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | Part-Guided 3D RL 突破 |
|---------|------|----------------------|
| Affordance 学习 | 需要人工设计执行策略 | 端到端 RL |
| 图像 RL | 2D 信息不足、样本效率低 | 3D 点云 + 部件引导 |
| 关键点方法 | 鲁棒性差 | 部件级采样点更稳定 |
| 单任务策略 | 需分别训练 | **多任务统一策略** |

### 关键贡献点
1. **2D 分割 + 3D RL**: 利用 2D 分割的效率 + 3D 点云的空间推理
2. **Frame-consistent Uncertainty-aware Sampling (FUS)**: 解决分割噪声和帧间不一致
3. **多任务统一策略**: 一个策略处理 OpenDoor/OpenDrawer/TurnFaucet

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 框架概览

```
RGB-D Image I
    ↓ Part Segmentation Network
Part Mask S ∈ {0,1}^{C×H×W}
    ↓ Depth → 3D Transform
Part-masked Points p
    ↓ FUS Sampling
Sampled Points p̂ (Ns per part)
    ↓ PointNet
Geometric Features F̂
    ↓ Concat with Robot State g
    ↓ RL Policy
Action a
```

### 3.2 部件定义

采用与 GAPartNet 类似的通用部件表示:

| 物体类型 | 部件 |
|---------|------|
| 柜门/抽屉 | 固定把手、门/抽屉面板、固定底座 |
| 水龙头 | 把手、固定底座 |

> [!note] 设计理由
> 部件定义与 affordance 对齐——把手用于抓取，面板用于推/拉。

### 3.3 Frame-consistent Uncertainty-aware Sampling (FUS)

**问题**: 合成数据训练的分割网络在真实场景有噪声，噪声点会干扰策略。

**解决方案**: 两类权重的加权采样

#### 3.3.1 不确定性权重 (Uncertainty Weights)

使用 Test-Time Augmentation (TTA) + MC Dropout 估计:
$$
P_c = \frac{1}{K} \sum_k P_k^c, \quad U = -\sum_c P_c \log P_c
$$

不确定性高的点 → 低采样权重

#### 3.3.2 一致性权重 (Consistency Weights)

```python
# 维护历史采样点队列 Q (长度 T_fc)
for each part c:
    d_c = min_{q_j ∈ Q_c} ||p_i - q_j||  # 到历史点的最小距离
    w_c^{fc} = 2^{-K^{fc} * d_c}  # 距离小 → 权重大
```

**直觉**: 稳定的点（每帧出现在相似位置）更可靠。

#### 3.3.3 组合权重

$$
w_c = w_c^{fc} \circ w_c^{ua}
$$

元素乘法组合，然后按权重采样 $N_s$ 个点。

### 3.4 多任务奖励设计

$$
r = r_{\text{approach}} + r_{\text{direction}} + r_{\text{position}} + r_{\text{visibility}} + r_{\text{grasp}}
$$

| 奖励项 | 含义 |
|-------|------|
| Approach | 接近可动部件 |
| Direction | 沿正确方向操作 |
| Position | 移动到目标位置 |
| Visibility | 保持视觉接触 |
| Grasp | 抓住把手（门/抽屉任务） |

### 3.5 训练细节

- **视角**: Hand-centric camera（减少遮挡）
- **点云编码**: PointNet
- **RL 算法**: PPO
- **Domain Randomization**: 材质、纹理、背景、深度噪声

## 4. 实验与验证 (Experiments)

### 任务设置
- **OpenDoor**: 打开各种柜门
- **OpenDrawer**: 拉开各种抽屉  
- **TurnFaucet**: 旋转各种水龙头

### 仿真结果

| 方法 | OpenDoor | OpenDrawer | TurnFaucet |
|-----|----------|------------|------------|
| UMPNet | 低 | 低 | 低 |
| Where2Act | 中 | 中 | - |
| **Ours** | **高** | **高** | **高** |

### Sim2Real 迁移
- 无需真实数据，Zero-shot 迁移
- FUS 显著提升真实环境稳定性

### 消融实验

| 配置 | 成功率 |
|-----|-------|
| 无部件分割 | 低 |
| 均匀采样 | 中 |
| FPS 采样 | 中 |
| **FUS 采样** | **高** |

## 5. 批判性分析 (Critical Analysis)

### 优势
- **无需演示**: 纯 RL 学习，可扩展
- **多任务统一**: 一个策略多种任务
- **稳定迁移**: FUS 解决分割噪声问题
- **3D 空间推理**: 比 2D 特征更适合操作

### 局限性
- 依赖准确的部件分割
- 仅考虑刚性关节物体
- 把手形状需相对标准

### 未来方向
- 复杂关节结构（多级门、连杆）
- 可变形物体
- 触觉辅助

## 6. 对灵巧操作的启发 (Implications)

1. **部件级思维**: 将复杂物体分解为有意义的部件简化学习
2. **2D+3D 结合**: 2D 分割高效，3D 点云利于空间推理
3. **不确定性感知**: 预训练模型的噪声需要显式处理
4. **时序一致性**: 帧间稳定性对控制很重要

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── UMPNet/FlowBot3D: Affordance 学习 + 启发式执行
├── 3D RL: 点云输入的策略学习
└── GAPartNet: 通用部件分割

本论文: Part-Guided 3D RL
├── 2D 分割 → 3D 点云 → RL
├── FUS 采样策略
└── 多任务统一策略

后续影响:
├── 更复杂关节物体
├── 部件级接触推理
└── 灵巧手关节物体操作
```

## 8. 核心算法伪代码

```python
# Algorithm 1: Part-guided articulation manipulation policy
def policy_forward(I, theta):
    # Step 1: Part segmentation
    S = f_theta(I)  # C×H×W part masks
    
    # Step 2: Point transform
    p = PointTransform(I, S)  # Per-part 3D points
    
    # Step 3: FUS sampling
    w_c = compute_fus_weights(p, history_queue)
    p_hat = WeightSampling(p, w_c)  # Ns points per part
    
    # Step 4: Feature extraction
    F_hat = PointNet(concat(p_hat))
    
    # Step 5: Action prediction
    a = Actor(concat(F_hat, robot_state))
    
    return a
```

## 9. 与 Affordance 方法的对比

| 方面 | Affordance (UMPNet等) | Part-Guided 3D RL |
|-----|----------------------|-------------------|
| 动作表示 | 预测接触点 + 方向 | 端到端 RL |
| 执行方式 | 启发式/规划 | 学习策略 |
| 泛化方式 | 视觉 affordance 泛化 | 部件结构泛化 |
| 反馈 | 开环 | 闭环 RL |
| 适应性 | 需重新规划 | 策略自适应 |
