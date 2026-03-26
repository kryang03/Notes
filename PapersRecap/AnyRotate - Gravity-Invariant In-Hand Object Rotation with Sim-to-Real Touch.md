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
venue: CoRL 2024
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

### 现有方法的局限
- **HORA**: 仅使用本体感觉 + RMA 适应器，缺乏触觉反馈导致无法检测滑移前兆，palm-down 场景失败率高
- **Touch Dexterity**: 引入触觉但仅支持 z 轴旋转（单自由度），且触觉表示为离散二值接触
- 多数手内操作方法仅在 palm-up 验证，回避了重力对抓取稳定性的破坏性影响
- 现有触觉 sim-to-real 多端到端迁移原始触觉图像，domain gap 大

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

### 3.7 核心代码逻辑（精简 PyTorch）

**触觉特征预测 CNN**:
```python
# 触觉图像 → 稠密接触特征
class TactileEncoder(nn.Module):
    def __init__(self):
        self.cnn = nn.Sequential(
            nn.Conv2d(3, 32, 3, stride=2), nn.ReLU(),
            nn.Conv2d(32, 64, 3, stride=2), nn.ReLU(),
            nn.AdaptiveAvgPool2d(1), nn.Flatten()
        )
        self.head_pose = nn.Linear(64, 2)    # 接触姿态 (Rx, Ry)
        self.head_force = nn.Linear(64, 1)   # 力幅度 ||F||

    def forward(self, tactile_img):  # (B, 4, 3, H, W) 4 fingers
        feats = [self.cnn(tactile_img[:, i]) for i in range(4)]
        feats = torch.stack(feats, dim=1)  # (B, 4, 64)
        P = torch.tanh(self.head_pose(feats))  # (B, 4, 2) ∈ S^2
        F_mag = F.softplus(self.head_force(feats))  # (B, 4, 1) ≥ 0
        return P, F_mag  # 稠密触觉特征
```

**Student 蒸馏损失**:
```python
# Teacher latent → Student latent 对齐 + 动作分布匹配
z_teacher = teacher.encode(privileged_obs)  # 特权信息编码
z_student = student.tcn_encode(obs_history)  # TCN 编码历史序列

loss_latent = F.mse_loss(z_student, z_teacher.detach())

mu_t, std_t = teacher.policy(z_teacher)
mu_s, std_s = student.policy(z_student)
loss_action = -Normal(mu_t, std_t).log_prob(mu_s).mean()  # NLL

loss = loss_latent + loss_action
```

**Auxiliary Goal 生成逻辑**:
```python
# 关键点距离判断是否达标 → 生成下一个旋转增量目标
kp_dist = (obj_keypoints - goal_keypoints).norm(dim=-1)  # (B, N_kp)
goal_reached = (kp_dist < d_tol).all(dim=-1)  # (B,)

# 达标后沿旋转轴 k_hat 旋转 delta_theta 生成新目标
new_goal_quat = axis_angle_to_quat(k_hat * delta_theta)  # (B, 4)
current_goal[goal_reached] = quat_mul(new_goal_quat, current_goal)[goal_reached]
```

## 4. 实验与验证 (Experiments)

### 实验设置
- **硬件**: 16-DoF Allegro Hand + UR5 + 4 个视觉触觉传感器
- **任务**: 6 种手朝向（palm up/down, thumb up/down, base up/down）× 多旋转轴
- **测试物体**: 10 种未见过的真实世界物体

### 训练细节
- **仿真器**: IsaacGym, 4096 并行环境
- **算法**: [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO|PPO]]，学习率 $5 \times 10^{-4}$，Horizon 16，Mini-batches 4
- **训练规模**: Teacher ~5000 iterations，Student ~2000 iterations
- **域随机化**: 物体质量 ±50%，摩擦系数 0.4–1.5，重力方向扰动 ±5°
- **触觉 CNN 训练**: 仿真中收集 ~50k 对 (触觉图像, 接触姿态+力) 配对，监督学习预训练
- **控制频率**: 20 Hz 关节位置指令

### 关键结果

| 消融条件 | 平均连续旋转数 | 相对完整系统 |
|---------|--------------|------------|
| 完整系统（稠密触觉） | **~15 rotations** (palm-up) | 100% |
| 仅二值接触 | ~8 rotations | ~53% |
| 无触觉（仅本体感觉） | ~3 rotations | ~20% |
| 无 Auxiliary Goal | 训练不收敛 | — |
| 无自适应课程 $\lambda_{\text{rew}}$ | ~6 rotations | ~40% |

**Sim-to-Real 迁移**: 10 种未见物体上 zero-shot 迁移成功，palm-up/down 均可完成多轴旋转。

### Ablation 因果链分析

| 去除组件 A | 效果 B | 因果机制 C |
|-----------|--------|----------|
| 去除稠密触觉 → 仅二值接触 | 旋转数降至 ~53% | 二值接触无法检测滑移前兆（力幅度变化），策略无法提前调整抓取力 |
| 去除所有触觉 | 旋转数降至 ~20%，palm-down 几乎完全失败 | 无接触反馈 → 无法感知物体在指尖上的漂移，尤其重力对抗场景 |
| 去除 Auxiliary Goal → 直接角速度奖励 | 训练不收敛 | 连续旋转的角速度奖励梯度稀疏，策略容易陷入"静止抓持"局部最优 |
| 去除自适应课程 $\lambda_{\text{rew}}$ | 旋转数降至 ~40% | 过早施加旋转奖励 → 策略在学会稳定抓取前就尝试旋转 → 频繁掉落 |
| 去除 Teacher-Student → 直接端到端 | Sim-to-Real 失败 | 端到端依赖特权信息（物体姿态），真实世界无法获取；蒸馏提供可部署的感知接口 |

**发现**: 稠密触觉能检测不稳定抓取并触发反应性行为，提高策略鲁棒性。

## 4.5 工程关键细节 (Engineering Tricks)

1. **触觉特征归一化**: 接触姿态 $(R_x, R_y)$ 归一化到 $[-1, 1]$，力幅度使用 softplus 保证非负性，避免网络输出异常值导致策略不稳定
2. **Auxiliary Goal 的 $\delta\theta$ 选择**: 过小导致目标切换过频（策略抖动），过大导致单步不可达（奖励稀疏）；论文取 $\delta\theta \approx 15°$ 作为 sweet spot
3. **自适应课程的线性调度**: $\lambda_{\text{rew}}$ 与平均旋转数线性挂钩而非固定 schedule，自动适配不同难度的手朝向
4. **TCN 历史窗口**: Student 使用 TCN 编码最近 50 步观测历史（2.5s @ 20Hz），提供隐式速度/加速度估计
5. **关键点选择**: 使用物体表面 8 个关键点而非质心/四元数作为旋转度量，避免四元数双覆盖问题和万向节锁
6. **域随机化的接触参数**: 摩擦系数范围 [0.4, 1.5] 覆盖从光滑金属到粗糙橡胶，确保策略不依赖单一摩擦条件
7. **早终止条件**: 物体掉落 OR 旋转轴偏离 > 30° → 立即终止并给大惩罚，加速无效 trajectory 的淘汰

## 5. 批判性分析 (Critical Analysis)

### 优势
- **首次重力不变**: 6 种手朝向的统一策略
- **Zero-shot Sim-to-Real**: 无需真实世界微调
- **稠密触觉的价值**: 实验证明比离散触觉更有效

### 理论层面局限
- [[ContactMechanics|接触模型]]假设刚体接触 + Coulomb 摩擦，未建模软体指垫的粘弹性和面接触分布
- Auxiliary Goal Formulation 隐含"旋转可分解为离散子目标"的假设，对连续高速旋转（如转笔的 aerial phase）不适用
- 重力不变性通过暴力枚举 6 个离散朝向实现，而非从 SE(3) 对称性出发的结构化方法

### 算法层面局限
- Teacher-Student 两阶段训练引入信息瓶颈：Student 的 TCN 编码能力限制了可迁移的特权信息量
- [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO|PPO]] 的 on-policy 采样效率低，4096 环境并行仍需数千 iteration
- 触觉 CNN 需要仿真中的监督数据对，假设仿真触觉渲染足够真实

### 工程层面局限
- 触觉传感器标定和维护成本高（4 个视觉触觉传感器）
- 20Hz 控制频率可能不足以应对高速动态操作
- 仅在 Allegro Hand（16-DoF）上验证，未迁移至其他灵巧手

### 替代方案对比
| 替代方案 | 优势 | 劣势 |
|---------|------|------|
| 端到端触觉图像策略 | 无需特征工程 | Domain gap 大，sim-to-real 困难 |
| Model-based + 接触力估计 | 可解释性强 | 高维灵巧手建模复杂 |
| 纯视觉方案（如 [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]]） | 无需触觉硬件 | 遮挡严重时性能退化 |
| [[ControlTheory\|阻抗控制]] + 力反馈 | 稳定性保证 | 需精确力传感器，难以自适应 |

### 未来方向
- 扩展到 finger-gaiting 操作
- 结合视觉进行物体追踪
- 更复杂的力控制策略

## 6. 与知识体系的联系 (Knowledge Graph Links)

### 与 [[ReinforcementLearning]] 的联系
- **Auxiliary Goal Formulation** 对应 [[ReinforcementLearning#4.2 奖励工程：稀疏 vs. 密集 vs. 塑形 (Sparse vs. Dense vs. Shaping)|奖励塑形]]思想：将稀疏的"持续旋转"奖励转化为密集的"子目标到达"奖励
- **Teacher-Student Distillation** 对应 [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL|Sim-to-Real]]中的特权学习范式：
  $$\mathcal{L}_{\text{distill}} = \underbrace{\|z_s - z_t\|^2}_{\text{latent alignment}} + \underbrace{-\log \pi_t(a_s | z_t)}_{\text{action NLL}}$$
- **自适应课程** $\lambda_{\text{rew}}$ 是[[Curriculum Learning|课程学习]]在奖励权重维度的实例化

### 与 [[ContactMechanics]] 的联系
- 稠密触觉特征 $(P, F)$ 是 [[ContactMechanics#3.2 软指接触模型 (Soft Finger Contact)|软指接触模型]]的简化参数化：
  $$\text{Full Contact State} = (p_c, n_c, f_n, f_t, \tau) \xrightarrow{\text{降维}} (R_x, R_y, \|F\|)$$
  接触姿态 $(R_x, R_y)$ 编码了接触法线方向，力幅度 $\|F\|$ 是法向力 $f_n$ 的标量近似
- 关键点距离度量 $K(\|k_o^i - k_g^i\|)$ 与 [[ContactMechanics#2.6 抓取品质度量 (Grasp Quality Metrics)|抓取品质度量]]在精神上一致

### 与 [[SignalProcessing]] 的联系
- 触觉图像 → 接触特征的 CNN 是 [[SignalProcessing#3.1 光度立体视觉（Photometric Stereo）：从光影到微米级形貌|光度立体视觉]]的学习版本：从 marker 变形图像反演接触几何
- TCN 编码历史观测对应 [[SignalProcessing#4.1 早期滑移（Incipient Slip）检测算法|滑移检测]]的时序推理：通过力幅度的时间变化趋势判断滑移风险

### 与 [[RepresentationLearning]] 的联系
- 稠密触觉表征是 [[RepresentationLearning#5. Multimodal Fusion & Tactile Intelligence: 触觉与视觉的交响 (Symphony of Vision and Touch in Multimodal Fusion)|多模态触觉智能]]的实例化：从高维触觉图像提取低维但物理可解释的接触特征
- 这种"先提取显式特征再输入策略"的范式体现了 [[RepresentationLearning#1.3 学习目标的物理重构 (Physical Reconstruction of Learning Objectives)|物理重构]]原则

### 启发总结
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
```

### 跨方法结构性对比

| 维度 | AnyRotate | [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | HORA | PPO Baseline |
|-----|-----------|-----------|------|-------------|
| **感知模态** | 本体感觉 + 稠密触觉 | 本体感觉 + 视觉 | 本体感觉 + RMA | 本体感觉 |
| **旋转自由度** | 多轴 (任意 $\hat{k}$) | 多轴 | z 轴为主 | 单轴 |
| **重力不变** | ✅ 6 种朝向 | ❌ palm-up 为主 | ❌ palm-up | ❌ |
| **Sim-to-Real 策略** | Teacher-Student + 稠密触觉特征 | 课程 + 演示引导 | RMA 适应器 | 域随机化 |
| **奖励设计** | Auxiliary Goal（子目标到达） | 任务奖励 + 课程 | 角速度奖励 | 角速度奖励 |
| **课程机制** | 自适应 $\lambda_{\text{rew}}$ | 演示引导自动课程 | 无显式课程 | 无 |
| **关键优势** | 触觉 sim-to-real 闭环 | 演示加速探索 | 在线适应 | 简单 |
| **关键劣势** | 触觉硬件成本 | 依赖高质量演示 | 无触觉反馈 | 泛化差 |

> [!tip] 与 PPO 转笔策略的对比启发
> PPO 转笔中常用角速度奖励 → AnyRotate 实验证明这导致探索困难。**Auxiliary Goal Formulation** 将连续旋转离散化为子目标序列，为转笔的"指间传递"阶段提供了替代奖励设计思路：每个手指接触阶段定义一个中间目标姿态。

## 8. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

**直接可迁移的思想**：
1. **Gravity-Invariant Framework**: 转笔任务中手的姿态变化导致重力对笔的作用方向不断变化，可借鉴本文的重力不变性训练策略，在[[ReinforcementLearning#5.1 域随机化 (Domain Randomization, DR) 与 自适应 (Adaptive DR)|域随机化]]中加入手部姿态随机化
2. **Auxiliary Goal Formulation**: 将「转笔角速度维持」和「接触力稳定」作为辅助目标而非直接的奖励信号，可能比精心设计的 dense reward 更鲁棒。具体地，转笔可分解为："指1→指2传递"、"aerial phase"、"指2 catch" 三个子目标
3. **触觉信号处理**: 本文将触觉抽象为姿态+力的稠密特征，对于转笔中指腹触觉传感器的 sim-to-real 对齐有参考价值。关键洞察：**不迁移原始触觉图像，而是迁移物理可解释的接触中间表征**
4. **自适应课程 $\lambda_{\text{rew}}$**: 转笔训练中可类似地设计——初期重点学习稳定抓持，平均旋转数达标后逐步增加旋转速度奖励权重

**局限性对比**:
- AnyRotate 处理的是**准静态旋转**（20Hz 控制 + 低角速度），转笔是**动态高速操作**（需 ≥50Hz + 惯性效应显著）
- AnyRotate 的 Auxiliary Goal 假设每个子目标间有充分的控制余量，但转笔 aerial phase 中手指完全脱离物体，子目标范式需本质性修改
- AnyRotate 的触觉特征在持续接触场景有效，但转笔涉及频繁的接触-脱离切换，[[ContactMechanics#5.1 梯度的不连续性挑战|接触不连续性]]更严重
