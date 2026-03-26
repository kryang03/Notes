---
tags:
  - paper
  - dexterous-manipulation
  - pen-spinning
  - sim-to-real
  - reinforcement-learning
  - PPO
aliases:
  - Lessons from Pen Spinning
  - Pen Spinning
read-date: 2026-01-31
venue: CoRL 2024
paper-year: 2024
authors:
  - Jun Wang
  - Ying Yuan
  - Haichuan Che
  - Haozhi Qi
  - Yi Ma
  - Jitendra Malik
  - Xiaolong Wang
institution: UC San Diego, CMU, UC Berkeley
paper-pdf: "[[Papers/Lessons from Learning to Spin Pens.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
---

# Lessons from Learning to Spin "Pens"

> [!note] Foundation 关联
> - **[[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL]]**: 三阶段 Sim-to-Real 流程
> - **[[ContactMechanics#3. 接触建模演变：从点模型到软体模型]]**: 动态接触与 finger gaiting
> - **[[Dynamics]]**: 笔状物体的动态平衡控制
> - **[[ControlTheory#3. 技术演进：从刚性位置控制到柔顺力控制]]**: PD 位置控制与刚度-柔顺权衡
> - **[[EmbodiedAI]]**: 灵巧操作系统集成

> [!abstract] 核心贡献
> 首个实现**连续旋转笔状物体**的学习系统。通过 Oracle Policy + Open-loop Replay + Real-world Fine-tuning 的三阶段流程，仅用 **<50 条真实轨迹** 成功跨越 sim-to-real gap，实现 10+ 种不同物理属性的笔状物体多圈旋转。

## 1. 问题定位

### 1.1 为什么笔状物体如此困难？

**与传统 in-hand manipulation 的区别**：
- 立方体/球体有**自然支撑**（手掌、桌面、重力）
- 笔状物体需要**动态平衡** + **复杂手指协调**
- 需要 **finger gaiting**（手指交替接触/脱离）

**现有方法的失败原因**：

| 方法 | 问题 |
|------|------|
| 经典控制 | 需要精确模型，无法泛化 |
| Teleoperation + IL | 延迟太大，无法收集动态演示 |
| 纯 Sim-to-Real | Gap 太大，策略无法迁移 |

### 1.2 核心洞见

> [!tip] 关键思路（直觉隐喻）
> **Oracle 轨迹如同乐谱**——即使演奏者（真机）与作曲家（仿真）的乐器音色不同，照谱演奏（Open-loop Replay）仍能奏出旋律（成功轨迹）。成功的演奏录音再反哺训练即兴演奏（闭环策略），实现以极少真实数据跨越 sim-to-real gap。
>
> 仿真中的 Oracle 轨迹可以作为 Open-loop Controller 直接在真机上执行
> 
> 成功的真实轨迹 → 高质量演示数据 → Fine-tune 本体感知策略

---

## 2. 方法框架

```
(A) Oracle Policy Training (RL)
         ↓
    Sim Dataset
         ↓
(B) Pre-training Student Policy in Sim
         ↓
(C) Open-loop Replay → 真实成功轨迹
         ↓
(D) Fine-tuning with Real-world Data
```

### 2.1 Oracle Policy 设计

**PPO 训练目标**（[[ReinforcementLearning#3. Implementation: 核心算法细节分析|PPO 算法细节]]）：

Oracle Policy 通过 PPO 的 clipped surrogate objective 优化：
$$L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t\left[\min\left(r_t(\theta)\hat{A}_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon)\hat{A}_t\right)\right]$$
其中 $r_t(\theta) = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{\text{old}}}(a_t|s_t)}$ 为重要性采样比率，$\hat{A}_t$ 为 GAE 优势函数。在 4096 并行环境下训练 ~10B 步，使 Oracle 充分探索 finger gaiting 模式空间。

**观测空间**（特权信息）：
- 关节位置 $q_t$（历史 3 帧）
- 前一动作目标 $a_{t-1}$
- 二值触觉信号 $c_t$（每指尖 5 个传感器）
- 指尖位置 $p_t$
- 笔的位姿和角速度 $w_t$
- **点云** $\in \mathbb{R}^{100 \times 3}$（PointNet 编码）
- 物理属性（质量、质心、摩擦系数、尺寸）

**奖励函数**：
$$r = r_{\text{rot}} + \lambda_z r_z + \lambda_{\text{energy}} r_{\text{energy}}$$

> [!important] 关键设计：$r_z$ 惩罚
> 惩罚笔最高点和最低点的高度差，**强制笔保持水平**
> 
> 没有这个惩罚 → 笔倾斜 → 仿真可行但真机不稳定

**初始状态设计**：

```
⚠️ 不能随机采样！
```

人类启发的 **6 种 Canonical Grasp**：
- 每个是 finger gaiting 循环中的关键帧
- 每种加入噪声生成稳定初始状态集

![[pen_canonical_grasp.png]]

### 2.2 Sensorimotor Policy

**为什么不能用 DAgger 蒸馏？**
- 视觉触觉策略：sim-to-real gap 太大
- 纯本体感知策略：仿真中就无法收敛

**解决方案**：
1. 用 Oracle rollout 收集 $(s_t, a_t)$ 数据集
2. 预训练本体感知策略（获得 motion prior）
3. 用真实轨迹 fine-tune 适应真实动力学

**网络架构**：
- 输入：30 步 $q_t$, $a_{t-1}$ 历史
- Temporal Transformer 提取序列特征
- MLP 输出动作

### 2.3 Open-loop Replay

**流程**：
1. 选取 15 条持续 >800 步的仿真轨迹
2. 直接在真机上回放动作序列
3. Human-in-the-loop 筛选成功轨迹
4. 成功轨迹用于 fine-tuning

**为什么有效？**
- Open-loop controller 对 in-hand manipulation 出奇地鲁棒
- 虽然不能 zero-shot 迁移策略，但可以迁移**动作序列**

### 2.4 Delta 分析

| 维度 | 前人 (OpenAI Dactyl / HORA) | 本文 |
|-----|------|------|
| 物体类型 | 立方体/球体（有自然支撑面） | **笔状物体**（无支撑，需动态平衡） |
| 感知模态 | 视觉追踪 / 纯本体感觉 | 点云+触觉+本体(Oracle) → 纯本体(部署) |
| Sim-to-Real | Zero-shot DR / RMA 在线适应 | **三阶段**: 预训练→Open-loop Replay→Real Fine-tune |
| 真实数据需求 | 0（纯零样本）或大量遥操作 | **<50 条**（由 Open-loop 自动产生） |
| 核心新颖性 | DR 覆盖 / 适应模块 | Canonical Grasp 初始化 + Open-loop 数据引擎 |

### 2.5 核心代码逻辑

```python
# Oracle Policy 观测构建（维度注释）
obs = torch.cat([
    joint_pos_history,    # (B, 3, 16) — 3帧关节位置历史
    prev_action,          # (B, 16)    — 前一步动作目标
    binary_tactile,       # (B, 20)    — 4指×5传感器二值触觉
    fingertip_pos,        # (B, 12)    — 4指尖xyz
    pen_pose,             # (B, 7)     — 笔位姿(pos+quat)
    pen_angular_vel,      # (B, 3)     — 笔角速度
    pointnet_feat,        # (B, 64)    — PointNet编码点云
    phys_params,          # (B, 5)     — 质量/质心/摩擦/尺寸
], dim=-1)               # 总维度 ~143

# 奖励计算（r_z 是 sim-to-real 的关键）
r_rot = angular_velocity_z * dt          # 绕z轴旋转奖励
r_z = -lambda_z * (z_max - z_min)        # 惩罚笔倾斜
r_energy = -lambda_e * torque.pow(2).sum(-1)
reward = r_rot + r_z + r_energy

# Open-loop Replay 数据引擎
finetune_data = []
for traj in sim_trajectories[:15]:       # 15条>800步仿真轨迹
    real_obs = replay_openloop(traj.actions, robot)
    if human_judges_success(real_obs):   # 人工筛选
        finetune_data.append((real_obs, traj.actions))
# len(finetune_data) < 50 → 微调纯本体策略
```

---

## 3. 实验结果

### 3.1 仿真消融

| 方法 | Episode Reward | 备注 |
|------|----------------|------|
| **Ours** | ~100 | 完整设计 |
| Single Canonical Pose | 不稳定 | 无 finger gaiting |
| No Tactile | 下降 | 触觉重要 |
| No Point Cloud | 下降 | 几何信息重要 |
| No Privileged Info | 下降 | 物理属性重要 |

### 3.2 真机性能

**指标**：
- **RR (Rotation Revolutions)**: 旋转圈数
- **Suc (Success Rate)**: 成功率

| 方法 | Object A | Object B | Object C |
|------|----------|----------|----------|
| Replay | 2.80/38% | 3.37/54% | 2.65/30% |
| V. Distill | 1.85/18% | - | - |
| P. Distill | 1.57/0% | 1.57/0% | 1.57/0% |
| **Ours** | **3.43/55%** | **3.38/70%** | **3.50/68%** |

**泛化到未见物体**（不同质量、摩擦、尺寸）：
- 成功率 50-80%
- 仅用 <50 条真实轨迹

### 3.3 训练设定

| 项目 | 细节 |
|------|------|
| 仿真环境 | IsaacGym, 4096 并行环境 |
| Oracle Policy 算法 | PPO, ~10B 环境步训练 |
| 感知策略架构 | Temporal Transformer (30步历史) + MLP |
| 预训练数据 | 100K+ Oracle rollout $(s_t, a_t)$ 对 |
| Fine-tune 数据 | **<50 条**真实轨迹 |
| 控制频率 | 30 Hz PD 位置控制 |
| 硬件 | Allegro Hand (16 DoF) + 5×4 二值触觉 |
| 物体 | 10+ 种笔状物体（不同质量/摩擦/尺寸） |

### 3.4 消融因果链分析

| 移除组件 | 效果 | 因果机制 |
|---------|------|----------|
| 多 Canonical Pose → 单一姿态 | 不稳定 | 单一 pose 无法覆盖 finger gaiting 完整循环，策略永远探索不到手指交替模式 |
| 触觉信号 | 性能下降 | 失去接触/脱离精确时机感知，手指协调退化为纯本体隐式估计 |
| 点云 | 性能下降 | Oracle 缺少物体几何信息，无法为不同形状笔选择最优旋转轨迹 |
| 特权物理信息 | 性能下降 | 策略无法区分轻/重、高/低摩擦物体，被迫用单一保守策略 |
| $r_z$ 水平惩罚 | 仿真可行→真机失败 | 仿真完美模拟重力对倾斜笔的影响，但真机接触误差放大导致倾斜后不可恢复 |

---

## 4. 核心 Lessons

> [!quote] Lesson 1: 初始状态分布是关键
> 单一初始姿态无法学习 finger gaiting；需要人类启发的 canonical grasp 设计

> [!quote] Lesson 2: 水平约束 ($r_z$) 至关重要
> 没有显式惩罚笔倾斜，仿真中可行的行为在真机上会失败

> [!quote] Lesson 3: Open-loop Replay 出奇有效
> Oracle 轨迹作为 open-loop controller 可以产生高质量真实演示

> [!quote] Lesson 4: 仿真预训练提供 Motion Prior
> 使得策略可以用极少真实数据（<50 条）适应真实动力学

## 4.5 工程关键细节 (Engineering Tricks)

- **Canonical Grasp 验证**：每种 grasp 必须经物理验证（仿真 1000 步不掉落），无效初始状态会浪费 rollout
- **$r_z$ 权重**：$\lambda_z \in [0.5, 1.0]$ 为最佳区间——过小则策略倾斜（真机不鲁棒）、过大则限制旋转自由度
- **Open-loop 轨迹长度阈值**：>800 步——更短轨迹因初始化误差累积在真机上容易失败
- **PD 增益 sim-to-real 调整**：真机 PD 增益需略低于仿真以补偿关节摩擦和腱弹性
- **Temporal Transformer 历史长度**：30 步（~1s@30Hz）是性能与推理延迟的最佳权衡
- **PointNet 采样**：100 点采样即可捕获笔形状；更多点不提升性能但增加计算代价

---

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系

- 使用 **PPO** 训练 Oracle Policy
- **Domain Randomization** 应用于感知输入和物理参数
- 体现了 **Imitation + RL** 的混合范式

**数学对应**：PPO 的 clipped objective $L^{\text{CLIP}}$ 在本文 Oracle 训练中的关键作用——4096 并行环境使 $\hat{A}_t$ 的方差估计充分降低，clip 范围 $\epsilon$ 保证 finger gaiting 这类长horizon多模态策略的训练稳定性。三阶段流程对应 [[ReinforcementLearning#5. Bridging the Gap: Sim-to-Real & Offline RL]] 中 sim-to-real 的"仿真预训练 → 真实微调"范式，但用 Open-loop Replay 替代了传统 Domain Randomization 的 zero-shot 路线。

### 与 [[Dynamics]] 的联系

- 笔旋转是典型的**混合动力学系统**（contact mode switching）
- Finger gaiting 涉及**滚动、滑动、脱离**的模式切换
- 验证了 RL 隐式学习模式调度的能力

**数学对应**：笔旋转的动力学可建模为切换系统 $\dot{x} = f_{\sigma(t)}(x, u)$，其中模式 $\sigma(t) \in \{\text{contact}_i, \text{slide}_j, \text{release}_k\}$ 由各手指的接触状态决定。6 种 Canonical Grasp 对应 finger gaiting 循环中的关键模式切换点，笔的旋转动力学 $I\dot{\omega} = \sum_i \tau_{\text{contact},i}$ 需要至少 2 指同时提供力矩才能维持稳定旋转。

### 与 [[ContactMechanics]] 的联系

- Finger gaiting 的本质是**接触模式的有序切换**：每个手指在旋转周期中经历 接触→滑动→脱离→重新接触 的循环
- 二值触觉信号 $c_t \in \{0,1\}^{20}$ 提供离散接触状态观测，对应 [[ContactMechanics#3. 接触建模演变：从点模型到软体模型]] 中硬指接触模型的简化形式
- $r_z$ 惩罚的物理本质：笔倾斜时重力矩 $\tau_g = mgl\sin\theta$ 需要更大的接触法向力补偿，超出真机摩擦锥 $f_t \leq \mu f_n$ 约束后笔滑落

### 与 [[ControlTheory]] 的联系

- 部署策略输出 PD 位置目标，底层为 [[ControlTheory#3. 技术演进：从刚性位置控制到柔顺力控制|PD 位置控制]]：$\tau = K_p(q_{\text{target}} - q) + K_d(\dot{q}_{\text{target}} - \dot{q})$
- 30 Hz 控制频率是**刚度-柔顺权衡**的结果：更高频率需要更精确的动力学模型，更低频率则无法跟踪 finger gaiting 的快速切换
- 真机 PD 增益需低于仿真——对应阻抗控制中"降低虚拟刚度以容忍模型误差"的经典策略

### 与 Dynamic Non-Prehensile Manipulation 的联系

- 笔旋转本质上是**动态操作**（依赖惯性和动量）
- 不是静态抓取，而是持续的平衡和协调
- 是 [[Dynamic Non-Prehensile Manipulation]] 的重要 benchmark

### 与 [[Optimization]] 的联系

- 奖励函数 $r = r_{\text{rot}} + \lambda_z r_z + \lambda_e r_{\text{energy}}$ 的多目标权衡本质上是 [[Optimization#2. 核心概念：物理直觉与数学定义 (Core Concepts: Physics & Mathematics)|多目标优化]] 问题
- Open-loop Replay 的轨迹筛选可视为 [[Optimization#3. 技术演进脉络与深度洞察 (Evolution & Insights)|采样优化]] 的一种形式

## 5.5 核心洞见 (Insights)

### 5.5.1 理论局限性三维分析

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | Open-loop Replay 无收敛保证——有效轨迹数量取决于 sim-to-real gap 大小，无理论下界 | 引入域适应理论（$\mathcal{H}\Delta\mathcal{H}$-divergence）量化可迁移性 |
| **算法** | 三阶段线性管线，错误不可回溯——Open-loop 失败率高则 Fine-tune 数据不足 | 闭环迭代：Fine-tune 策略再收集数据反哺 |
| **工程** | Human-in-the-loop 筛选难以规模化；Canonical Grasp 需手工设计 | 自动成功检测（力/位阈值）+ 课程化初始状态生成 |

### 5.5.2 对灵巧手转笔 / Sim-to-Real 的启发

> [!tip] 与用户研究的直接关联——PPO 转笔方案

1. **三阶段范式直接可复用**：PPO 转笔策略可按同一流程——特权 Oracle → Open-loop 回放真机 → 成功轨迹 Fine-tune 纯本体策略。比 zero-shot DR 更安全
2. **Canonical Grasp → 转笔关键帧**：Thumbaround 同样有周期性关键帧（snap 发力 → 滑过食指 → 收手），可定义 4-6 个 canonical 初始状态覆盖完整旋转周期
3. **$r_z$ 约束的迁移**：限制笔轴偏离水平面的角度可能是 Sim-to-Real 成功关键——仿真中"花哨"但不鲁棒的旋转在真机上会失败
4. **<50 条数据效率**：说明仿真 motion prior 极重要，应优先保证仿真预训练质量，而非追求大量真实数据
5. **Open-loop 成功率作为 Gap 诊断指标**：若成功率极低，应改善仿真而非增加 DR 强度

---

## 6. 局限与未来

1. **仍需 Human-in-the-loop**：筛选成功的 open-loop 轨迹
2. **对象范围有限**：仅限笔状物体
3. **无 SO(3) 全姿态控制**：仅绕 z 轴旋转
4. **硬件要求**：Allegro Hand + 触觉传感器

## 6.5 跨方法结构性对比

| 维度 | 本文 | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] | 用户 PPO 转笔方案 |
|------|------|------|------|------|
| 物体 | 笔状（无自然支撑） | 多种形状（指尖上） | 多种形状（多手朝向） | 笔（动态旋转） |
| Sim-to-Real | 3阶段+<50条真实数据 | Zero-shot RMA | Zero-shot 蒸馏 | DR+课程 $\alpha$ |
| 感知 | 本体(部署) | 纯本体 | 本体+触觉 | 本体+触觉(规划) |
| 旋转自由度 | z轴多圈 | z轴 | 任意轴 | z轴(Thumbaround) |
| 课程策略 | Canonical Grasp | DR 范围 | 辅助奖励 $\lambda$ | HDC $\alpha$+状态初始化 |
| 核心创新 | Open-loop Replay 数据引擎 | RMA extrinsics | Gravity-invariant+稠密触觉 | $\alpha$-课程+非紧握动力学 |

---

## References

- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — 同样研究笔旋转任务
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 追踪人类参考的灵巧操作
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — RL 中的阻抗控制
