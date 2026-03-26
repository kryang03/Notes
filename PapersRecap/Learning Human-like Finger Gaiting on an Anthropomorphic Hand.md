---
tags:
  - paper
  - finger-gaiting
  - pen-spinning
  - non-prehensile-manipulation
  - reinforcement-learning
  - anthropomorphic-hand
  - waypoint-guidance
date: 2025-02-02
paper-year: 2025
read-date: 2026-03-16
venue: ICIRA 2025
aliases:
  - FingerGaiting
  - ICIRA25-FingerGaiting
paper-pdf: "[[Papers/Learning Human-like Finger Gaiting.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[EmbodiedAI]]"
---

# Learning Human-like Finger Gaiting on an Anthropomorphic Hand

> [!abstract] 核心贡献
> 提出路径点引导初始化 + 归一化接触力特权信息的 RL 框架，首次在 21-DoF 仿人手上实现动态 finger gaiting 涌现，仅 1.5h 训练即完成转笔任务——核心洞察是**手部形态决定策略类型**：细长仿人指尖催生动态步态而非静态平衡。

> [!note] Foundation 关联
> - **[[ReinforcementLearning]]**: PPO + 课程学习
> - **[[ContactMechanics#3. 接触建模演变：从点模型到软体模型]]**: 动态接触与手指步态
> - **[[Dynamics]]**: 多体动力学与物体平衡
> - **[[EmbodiedAI]]**: 仿人手操作系统

> **摘要**: 本文研究在仿人手上学习动态手指步态（finger gaiting）——连续重新定位手指以实现物体持续运动的能力。以转笔任务为测试平台，该任务要求精确的多指时序协调而无稳定抓取。先前受限于手部形态的工作通常产生依赖指尖平衡的简单策略。本文框架采用基于路径点的引导初始化，并在训练中利用归一化接触力作为特权信息。仿真结果展示了动态手指步态的涌现，仅需1.5小时训练即可高效执行转笔任务。

---

## 1. 理论深潜 (Theoretical Deep Dive)

### 1.1 核心洞察（一句话 + 直观隐喻）

> 手指步态就像「多人接力赛」——每个手指在「支撑→推进→重新就位」的循环中交替上场，关键不在于互不干扰，而是**时序协调的精确交接棒**。低 DoF 手像「单人托举」（指尖平衡），高 DoF 仿人手才能实现这种「接力赛」式动态步态。

### 1.2 现有方法的局限

| 方法 | 局限 |
|------|------|
| 低 DoF 手 + 标准 RL | 形态限制导致只能指尖平衡，无法涌现动态步态 |
| 高 DoF 手 + 随机探索 | 状态空间过大，随机采样几乎无法发现有效初始接触状态 |
| 人类全轨迹模仿 | 转笔的接触过渡极其复杂，独立跟踪全部轨迹点不实际 |
| 二值接触信息 | 仅知有无接触不足以区分支撑/推进/引导触碰，策略无法学习精细力调制 |

### 核心挑战: 高自由度手的非抓持操作

**Finger Gaiting 定义**:
手指的序列性重新定位，通过交替的支撑和推进阶段维持对物体的持续控制——一种超越静态抓取范式的生物启发方法。

### 手部形态与策略涌现

关键观察（Fig.1）:
| 手部类型 | 典型策略 | 原因 |
|---------|---------|-----|
| 低自由度/宽指尖 | Fingertip Balancing | 接触面同质，稳定性优先 |
| 高自由度仿人手 | Dynamic Finger Gaiting | 细长指尖，多样接触面 |

**Linker Hand**: 21 DoF 五指手，细长指尖，类人手掌面

### RL 学习的双重挑战

**挑战 1: 高维空间探索失效**
- 随机关节采样难以发现有效起始状态
- 转笔需要特定初始接触才能开始
- 需要引导式探索进入有效状态空间区域

**挑战 2: 复杂感觉运动信息解读**
- 高维本体感知和接触数据流
- 需区分支撑力 vs 推进力
- 实时处理噪声数据生成精确运动命令

---

## 2. 方法论剖析 (Methodology Dissection)

### 2.1 强化学习框架

**基本设定**:
- 算法: PPO
- 控制器: PD 控制将 $\Delta q_{tgt}$ 转换为关节力矩

**观测空间**:
- 本体感知 $O_{pro}$: 关节角度 $q$、速度 $\dot{q}$、前一目标关节角
- 特权信息 $O_{pri}$: 指尖位置、3D 净接触力、物体位姿/速度、物体点云

**奖励函数**:
$$R_{tot} = w_{rot}r_{rot} + w_{sta}r_{sta} + w_{smo}r_{smo} + w_{vel}r_{vel} + w_{way}r_{way}$$

| 奖励项 | 含义 |
|--------|------|
| $r_{rot}$ | 鼓励持续旋转 |
| $r_{sta}$ | 惩罚高度/姿态偏差 |
| $r_{smo}$ | 促进平滑运动 |
| $r_{vel}$ | 抑制过高速度 |
| $r_{way}$ | 路径点稀疏奖励 |

### 2.1.1 Delta 分析：与 SOTA 的增量

| 维度 | Lessons from Spin Pens (Wang et al. 2024) | **本文** |
|------|-------|------|
| 手部形态 | 低 DoF 手（宽指尖） | 21 DoF 仿人手（细长指尖） |
| 涌现策略 | Fingertip balancing | Dynamic finger gaiting |
| 探索引导 | 僅奖励塑形 | 路径点初始化 + 稀疏奖励 |
| 接触信息 | 二值接触 | 3D 净接触力（归一化） |
| 关键增量 | — | ① 仿人手形态催生 gaiting ② 路径点采样初始化 ③ 迭代归一化 |

### 2.2 路径点引导强化学习

**核心思想**: 利用人类示范解决探索问题

**路径点提取流程**:
1. 从人类转笔轨迹提取关键过渡状态
2. 应用扰动并评估稳定性/鲁棒性
3. 得分高于阈值的配置作为训练初始点
4. 从路径点周围高斯分布采样初始状态

**双重作用**:
- 初始化引导: 偏置探索到动态相关区域
- 稀疏奖励: 鼓励策略通过关键过渡阶段

### 2.3 特权接触信息预处理

**为什么需要 3D 净接触力**:
- 二值接触信息不足以学习细腻交互
- Finger gaiting 需区分: 支撑触碰 vs 推进触碰 vs 引导触碰

**力向量归一化**:

*方案 1: 线性裁剪归一化*
$$F'_c = \frac{\text{clip}(F_c, F_{min}, F_{max}) - F_{min}}{F_{max} - F_{min}}$$

*方案 2: tanh 归一化*
$$F_{norm,i} = \tanh(k \cdot F_i)$$

**迭代超参数优化**: 基于训练性能反馈调整归一化参数

### 2.4 核心伪代码（PyTorch tensor ops）

```python
# === Waypoint-Guided Initialization ===
# waypoints: [N_wp, NDoF] 从人类转笔轨迹提取的关键过渡状态
# sigma_init: 高斯采样标准差
def sample_initial_states(waypoints, num_envs, sigma_init=0.05):
    wp_idx = torch.randint(0, len(waypoints), (num_envs,))
    q0 = waypoints[wp_idx]  # [num_envs, NDoF]
    q0 += sigma_init * torch.randn_like(q0)  # 高斯扰动
    return q0

# === Contact Force Normalization ===
# raw_forces: [num_envs, 5, 3]  — 五指 × 3D净力
def normalize_contact_forces(raw_forces, F_min, F_max):
    # 方案1: 线性裁剪归一化 → [0,1]
    clamped = torch.clamp(raw_forces, F_min, F_max)
    return (clamped - F_min) / (F_max - F_min + 1e-8)

def normalize_contact_tanh(raw_forces, k=0.1):
    # 方案2: tanh归一化 → [-1,1]
    return torch.tanh(k * raw_forces)

# === Observation Assembly ===
def build_obs(q, q_dot, q_tgt_prev, fingertip_pos, contact_forces,
              obj_pose, obj_vel, obj_pcd, F_min, F_max):
    O_pro = torch.cat([q, q_dot, q_tgt_prev], dim=-1)      # 本体感知
    F_norm = normalize_contact_forces(
        contact_forces.view(-1, 15), F_min, F_max)           # 归一化接触力
    O_pri = torch.cat([fingertip_pos.view(-1, 15), F_norm,
                       obj_pose, obj_vel, obj_pcd], dim=-1)  # 特权信息
    return torch.cat([O_pro, O_pri], dim=-1)

# === PD Controller: Action → Torque ===
# action: Δq_tgt ∈ R^{NDoF}
def pd_control(q, q_dot, action, q_tgt_prev, kp, kd):
    q_tgt = q_tgt_prev + action        # 增量目标
    tau = kp * (q_tgt - q) - kd * q_dot  # PD力矩
    return tau, q_tgt

# === Sparse Waypoint Reward ===
def waypoint_reward(obj_angle, waypoint_angles, threshold=0.1):
    # 物体旋转角度是否经过路径点
    dists = (obj_angle.unsqueeze(-1) - waypoint_angles).abs()
    reached = (dists < threshold).any(dim=-1).float()
    return reached
```

---

## 3. 实验验证与结果

### 实验设置

| 参数 | 值 |
|------|-----|
| 仿真环境 | Isaac Gym |
| GPU | NVIDIA RTX 4090 |
| 物理时间步 | 5 ms |
| 控制频率 | 20 Hz (即每 4 个物理步执行 1 次策略) |
| 手部模型 | Linker Hand (21 DoF, 五指仿人手) |
| 物体 | 圆柱笔 (r=12mm, L=120mm, m=60g) |
| RL 算法 | PPO (原文未公开 lr/batch 等超参) |
| 动作空间 | $\Delta q_{tgt} \in \mathbb{R}^{21}$（增量目标关节角）|
| 训练时长 | ~1.5 h（含迭代优化归一化参数）|
| 路径点数 | 3（人类转笔轨迹关键过渡态）|
| 最优结果 | 平均 1.95 rotations |

### 初始化策略对比

| 初始化方法 | 接触归一化 | 平均旋转次数 |
|-----------|-----------|-------------|
| 3 路径点(人类轨迹) | 迭代优化 | **1.95** |
| 3 路径点 | 固定参数 | ~1.5 |
| 6 静态平衡姿态 | 迭代优化 | 0.21 |
| 随机初始化 | - | 失败 |

### 关键发现

1. **路径点质量 > 数量**: 3 个关键过渡路径点优于 6 个静态平衡姿态
2. **动态路径点 vs 静态姿态**: 过渡状态而非静态姿态更有效引导
3. **迭代归一化重要**: 固定参数归一化效果较差
4. **训练效率**: 仅需 1.5 小时达到复杂手指步态

### Ablation 因果链

```
去掉路径点初始化（随机初始化）
  → 策略完全无法学习转笔 (0 rotations)
  → 因为: 21-DoF 空间太大，随机采样几乎不可能命中有效初始接触
  → 根因: 非抓持任务无稳定吸引域，必须引导进入有效状态子空间

将 3 个动态过渡路径点替换为 6 个静态平衡姿态
  → 性能从 1.95 骤降至 0.21 rotations
  → 因为: 静态平衡态处于"稳定陷阱"，策略优先保持平衡而非探索动态步态
  → 根因: 路径点必须位于接触过渡区而非稳态区才能引导动态行为

去掉接触力归一化
  → 性能从 1.95 降至 0.69 rotations
  → 因为: 原始力信号尺度差异大，策略难以区分支撑力/推进力
  → 根因: 力向量的物理尺度不一致阻碍了策略网络的特征提取

固定归一化参数 vs 迭代优化
  → 性能从 1.95 降至 0.73 rotations
  → 因为: 策略演化过程中力分布会变化，固定参数无法适应
  → 根因: 力归一化参数需与策略共进化才能提供有效学习信号

用二值接触替代 3D 净接触力
  → 性能显著下降
  → 因为: 二值信号只编码"有无接触"，丢失力方向/大小信息
  → 根因: finger gaiting 的核心是力调制而非接触检测
```

---

## 4. 工程关键细节 (Engineering Tricks)

- **迭代力归一化协议**: 不一次性确定 $F_{min}, F_{max}$，而是在训练中观测力分布后迭代调整——类似"训练中的 domain adaptation"，确保归一化范围匹配策略当前施力水平
- **路径点筛选**: 对候选路径点施加扰动，评估扰动后的接触稳定性/鲁棒性，仅保留得分高于阈值的配置；这避免了脆性初始状态导致的训练不稳定
- **高斯采样初始化**: 从路径点周围高斯分布采样 $q_0 \sim \mathcal{N}(q_{wp}, \sigma^2 I)$，而非精确复制路径点——增加多样性同时保持动态相关性
- **PD 控制器作为动作空间**: 输出 $\Delta q_{tgt}$ 而非直接力矩 $\tau$，由 PD 控制器负责低层力矩生成 $\tau = k_p(q_{tgt}-q) - k_d\dot{q}$——降低策略复杂度同时保持顺应性
- **数值稳定性**: 线性裁剪归一化中 $F_{max} - F_{min}$ 分母需加 $\epsilon$ 避免除零；tanh 归一化中 $k$ 过大会导致梯度消失
- **稀疏路径点奖励时机**: $r_{way}$ 仅在物体旋转角度穿越路径点附近时触发，避免密集奖励引发的奖励黑客

---

## 5. 批判性分析 (Critical Analysis)

### 创新贡献

1. **手部形态-策略关系洞察**: 首次系统论证仿人手形态与 finger gaiting 涌现的关系
2. **路径点引导 RL**: 解决高维非抓持任务的探索难题
3. **接触力预处理**: 特权信息的有效利用策略
4. **快速训练**: 1.5h 即可学习复杂协调技能

### 局限性

**理论层面**:
- 未建立 finger gaiting 的形式化接触状态机模型——仅通过奖励隐式引导涌现，难以保证涌现行为的可解释性和可控性
- 路径点选择依赖人类直觉，缺乏最优路径点集合的理论保证

**算法层面**:
- 特权信息依赖：部署时 3D 净接触力在物理世界中难以精确获取，需要 teacher-student distillation 或触觉传感器替代
- 单一任务泛化：仅验证转笔，未探索 finger gaiting 在其他非抓持任务（翻转、滚动）的迁移性
- 局部最优陷阱：Fig.6 显示策略易陷入无法继续旋转的局部最优

**工程层面**:
- 仅限仿真验证，未进行 Sim-to-Real 迁移
- 训练超参数（PPO lr, batch size 等）未公开，可复现性受限
- 路径点提取需人工参与，自动化程度不足

**替代方案对比**:

| 策略 | 适用场景 | vs 本文 |
|------|---------|---------|
| Teacher-Student Distillation | 解决特权信息部署问题 | 本文未实现，是必要后续 |
| 自动课程学习（如 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]]） | 自动生成路径点序列 | 可替代人工路径点提取 |
| 触觉传感替代特权力 | 物理部署 | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] 已验证触觉替代方案 |
| 分层策略（高层选择阶段+低层执行） | 复杂长时序操作 | 可提供更强可解释性 |

### 开放问题

- 是否可通过触觉传感器替代特权接触力？
- 路径点能否自动从视频中提取？
- 其他非抓持任务（如物体翻转）是否适用？

### 5.1 与用户研究的启发（灵巧手转笔 / Sim-to-Real）

> [!tip] 对转笔项目的直接启发
> 1. **路径点引导可直接复用**: 本文的路径点初始化策略可迁移到用户的转笔项目中——从人类示范视频提取 3-5 个关键接触过渡帧作为训练初始状态，避免从零探索
> 2. **形态决定策略类型**: 如果用户使用高 DoF 仿人手（如 Linker Hand 类似），应期望涌现 finger gaiting 而非 balancing；奖励设计应鼓励手指重定位而非静态稳定
> 3. **接触力归一化是 Sim-to-Real 的隐患**: 迭代归一化依赖仿真中的精确力数据，迁移时需使用 [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] 类似的触觉替代方案或 teacher-student 蒸馏
> 4. **$\Delta q_{tgt}$ 动作空间 + PD 控制器是安全底线**: 物理部署时 PD 控制器天然提供顺应性保护，避免直接力矩输出导致的硬件损伤
> 5. **训练效率启示**: 1.5h 训练时间说明精准的初始化引导比长时间随机探索更有效——对算力有限的实验室环境极具价值

---

## 5. 相关文献网络

**上游工作**:
- [[Lessons from Learning to Spin Pens]]（转笔任务基础）
- OpenAI Rubik's Cube（灵巧操作里程碑）

**同期工作**:
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]（任意轴旋转）
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]]（人类参考轨迹追踪）

**技术相关**:
- [[ReinforcementLearning#2.8 Exploration 理论：从信息论到技能发现]]
- [[Dynamics#5. Contact Dynamics: 灵巧操作的深水区 (The Deep Waters of Contact)]]

---

## 6. 关键概念索引

### Finger Gaiting

```
定义: 通过序列性手指重定位维持物体持续控制
       ↓
分解为: 支撑阶段 + 推进阶段 + 过渡阶段
       ↓
vs Fingertip Balancing: 静态稳定 vs 动态控制
```

### 非抓持操作分类

| 类型 | 示例 | 特点 |
|-----|------|-----|
| Fingertip Balancing | 指尖平衡物体 | 静态稳定 |
| Finger Gaiting | 转笔 | 动态协调 |
| Rolling | 掌上滚球 | 持续接触 |
| Pivoting | 物体枢转 | 单点支撑 |

---

## 7. 演化脉络 (Evolution Context)

**灵巧操作技能习得演进**:
```
基于模型控制 → 端到端 RL → 示范引导 RL → 路径点引导 RL
                              ↓
                     从"模仿轨迹"到"模仿关键状态"
```

**手部设计与算法协同进化**:
```
简单夹爪 → 多指手 → 仿人手
    ↓           ↓          ↓
抓取规划   稳定操作   动态 gaiting
```

---

## 6. 与本仓库基础理论联系

### 与 [[ReinforcementLearning]] 的联系

本文使用 [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO|PPO]] 作为核心算法。路径点引导初始化本质上是 [[ReinforcementLearning#2.8 Exploration 理论：从信息论到技能发现|探索引导]] 的实例——通过偏置初始状态分布 $\rho_0$ 改变探索方向：

$$\rho_0(s) = \sum_{i=1}^{N_{wp}} \frac{1}{N_{wp}} \mathcal{N}(s \mid s_{wp,i}, \sigma^2 I)$$

这将 PPO 的策略梯度从全空间探索压缩到路径点邻域，有效提升信噪比。

### 与 [[ContactMechanics]] 的联系

Finger gaiting 的核心是 [[ContactMechanics#3. 接触建模演变：从点模型到软体模型|接触力建模]]。本文将五指净接触力 $\mathbf{f}_{tip,i} = (F_x, F_y, F_z)_i \in \mathbb{R}^3$ 作为特权信息，归一化后输入策略网络。这与接触力学中的力平衡方程直接对应：

$$\sum_{i=1}^{5} \mathbf{f}_{tip,i} + m\mathbf{g} = m\ddot{\mathbf{x}}_{obj}$$

策略需隐式学习此力平衡约束，使支撑力抵消重力、推进力提供旋转力矩。

### 与 [[Dynamics]] 的联系

转笔涉及 [[Dynamics#5. Contact Dynamics: 灵巧操作的深水区 (The Deep Waters of Contact)|接触动力学]] 中的多体系统。手-笔系统的运动方程为：

$$M(q)\ddot{q} + C(q,\dot{q})\dot{q} + g(q) = \tau + J_c^T \mathbf{f}_c$$

其中 $J_c^T \mathbf{f}_c$ 是接触力对关节空间的映射。PD 控制器在关节空间生成 $\tau = k_p(q_{tgt}-q) - k_d\dot{q}$，隐式实现了动力学约束的满足。

### 与 [[Optimization]] 的联系

路径点筛选过程可视为一个鲁棒优化问题——对候选路径点施加扰动 $\delta \sim \mathcal{U}(-\epsilon, \epsilon)$，评估扰动下的稳定性得分 $S(q_{wp} + \delta)$，保留 $\mathbb{E}_\delta[S(q_{wp}+\delta)] > \theta$ 的路径点。这与 [[Optimization#2.4 凸优化基础与对偶性理论 (Convex Optimization Foundations & Duality)|鲁棒优化]] 中的最坏情况思想一致。

---

## 7. 跨方法对比 (Cross-Method Comparison)

| 维度 | [[Lessons from Learning to Spin Pens\|Spin Pens]] | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] | [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References\|DexTrack]] | **本文 (FingerGaiting)** |
|------|-----------|-----------|----------|----------|
| **手部形态** | 低 DoF (宽指尖) | Allegro Hand (16 DoF) | Allegro/LEAP | Linker Hand (21 DoF) |
| **核心技能** | 转笔 (fingertip balancing) | 任意轴旋转 | 通用轨迹跟踪 | 转笔 (finger gaiting) |
| **人类参考** | 无 | 无 | 人类手-物轨迹 | 路径点 (3个过渡态) |
| **触觉/力** | 二值接触 | 触觉传感器 | 无 | 3D 净接触力 (特权) |
| **Sim-to-Real** | ❌ | ✅ | ✅ | ❌ |
| **探索策略** | 奖励塑形 | 课程学习 | 同伦优化+数据飞轮 | 路径点初始化+稀疏奖励 |
| **关键创新** | 任务定义 | 重力不变性 | 数据飞轮迭代 | 形态-策略涌现关系 |
| **训练时间** | 较长 | 数小时 | 数小时 | 1.5h |

---

## References

- Yang et al. ICIRA 2025
- Hardware: Linker Hand (21 DoF anthropomorphic hand)
- Simulator: Isaac Gym (NVIDIA)
