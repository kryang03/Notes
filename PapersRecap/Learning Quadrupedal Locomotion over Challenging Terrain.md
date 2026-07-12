---
tags:
  - paper
  - sim-to-real
  - privileged-learning
  - curriculum-learning
aliases:
  - Challenging Terrain Locomotion
  - Proprioceptive TCN Locomotion
paper-year: 2020
read-date: 2026-04-26
venue: Science Robotics
paper-pdf: "[[Papers/Learning Quadrupedal Locomotion over Challenging Terrain.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
---

# Learning Quadrupedal Locomotion over Challenging Terrain

> [!abstract] 核心贡献
> 该工作通过 privileged teacher、proprioceptive TCN student 与 particle-filter terrain curriculum，使 ANYmal 仅凭本体感觉在泥地、雪地、碎石、植被等未见自然环境中零样本鲁棒行走。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — privileged teacher 降低仿真探索难度；teacher-student 蒸馏
> - [[ControlTheory]] — student 输出 residual/position targets 调制底层运动 primitive
> - [[SignalProcessing]] — proprioceptive 时序编码替代显式接触阈值检测
> - [[RepresentationLearning]] — TCN 将历史传感序列压缩为隐式地形/接触状态
>
> **核心技术**: Privileged Teacher-Student, Proprioceptive TCN History, Particle-Filter Terrain Curriculum

## 1. 问题设定与动机

### 1.1 核心洞察

在复杂自然环境中，外感知不一定可靠，反而高频本体感觉最稳定。策略不需要显式估计接触/打滑，只要给它足够长的 proprioceptive history，TCN 可以隐式推断接触事件与地形响应。

### 1.2 现有方法局限

- 手写状态机/反射控制器会随着场景增加而复杂化，阈值在泥、雪、水中脆弱。
- 直接用 RL 训练 rough-terrain policy 信号稀疏，训练难度高。
- 仅在固定随机化 terrain 上训练，课程无法始终停留在“刚好困难”的边界。

## 2. 核心方法/理论

### 2.0 变量来源追踪

枢纽：**teacher 用特权信息（terrain/contact 仿真可见）、student 只用本体历史**——这是后来 HORA RMA 的范式原型。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $o^{prop}$ | 本体感觉 | 观测（真机可得） | 否 | 关节/IMU | student 唯一输入源 |
| $o^{priv}$ | terrain/contact | **特权**（仿真可见） | 否 | 地形剖面/接触状态 | 真机不可得 → 只给 teacher |
| $\pi_T$ | MLP | RL 学习（用特权） | 是 | teacher | 快速学粗糙地形策略 |
| $\pi_S$ | TCN | 蒸馏（本体历史） | 是 | student（可部署） | **隐式推断接触/打滑** |
| $o^{prop}_{t-N:t}$ | 历史窗口 | 观测序列 | 否 | proprioceptive history | 长度须含时间导数/延迟 |
| $\eta_i$ | terrain 粒子 | 课程 | 否 | 地形参数 | particle filter 维护 |
| $w_i\propto e^{-(\hat p_{succ}-p^*)^2/2\sigma^2}$ | 权重 | 计算 | 否 | 中等难度权重 | **围绕 $p^*$ 而非最难** |

### 2.1 Delta 分析

1. privileged teacher：利用仿真可见的地形和接触信息快速学会粗糙地形策略。
2. proprioceptive student：TCN 只看真机可得的关节/IMU 历史，通过 imitation 蒸馏 teacher。
3. adaptive terrain curriculum：用 particle filtering 维护中等难度地形参数分布。

### 2.2 数学框架

Teacher policy：

$$
a_t^T=\pi_T(o_t^{prop}, o_t^{priv}),
$$

其中 $o_t^{priv}$ 包含 terrain profile、接触状态等仿真特权变量。

Student policy：

$$
a_t^S=\pi_S(o_{t-N:t}^{prop}),
$$

其中 $o_{t-N:t}^{prop}$ 是 proprioceptive history。蒸馏损失：

$$
\mathcal{L}_{distill}=\sum_t \|a_t^S-a_t^T\|_2^2+\lambda\|\ell_t^S-\ell_t^T\|_2^2,
$$

其中 $\ell_t$ 可表示 teacher 输出的中间运动 primitive/residual。课程用粒子 $\eta_i$ 表示 terrain 参数，目标是让训练分布集中在成功率中等的地形：

$$
w_i \propto \exp\left(-\frac{(\hat{p}_{succ}(\eta_i)-p^*)^2}{2\sigma^2}\right),\quad \eta_i\sim\text{Resample}(\{\eta_i,w_i\}).
$$

### 2.3 核心伪代码

```python
# teacher training in simulation
teacher_obs = torch.cat([proprioception, terrain_profile, contact_state], dim=-1)
teacher_action = teacher_policy(teacher_obs)
teacher_reward = locomotion_reward(sim_step(teacher_action))
ppo_update(teacher_policy, teacher_reward)

# student distillation
prop_history = rollout_buffer.proprioception.unfold(time_dim, history_len)
student_action = tcn_student(prop_history)
with torch.no_grad():
    target_action = teacher_policy(torch.cat([proprioception, privileged], dim=-1))
loss = ((student_action - target_action) ** 2).mean()
loss.backward()

# particle-filter curriculum
weights = medium_difficulty_score(success_rate_by_terrain)
terrain_particles = resample_and_jitter(terrain_particles, weights)
```

**物理量来源**：privileged terrain/contact 只来自仿真；student 输入关节编码器与 IMU 历史，真机可得；课程权重来自当前策略在地形粒子上的 rollout 成败。

### 2.4 概念边界与符号陷阱

- **teacher 用特权（terrain/contact）、student 只用本体历史**：RMA 范式核心；student 真机可部署。
- **TCN history 隐式推断接触/打滑**：不显式估计 contact/slip，靠历史时序。
- **particle curriculum 维持中等难度 $p^*$**：非单调追求最难地形（否则学习信号不稳）。
- **student 模仿 teacher → 继承 teacher 仿真偏差**（§5 算法局限）。
- **proprioceptive history 长度须够**：含地形响应的时间导数/延迟信息。
- **teacher-student 无 OOD terrain 形式化保证**（§5 理论局限）。

## 3. 训练与实验细节

### 3.1 训练设定

- Teacher：MLP，使用地形和接触特权信息，经 RL 训练。
- Student：TCN，输入本体感觉序列，经 imitation learning 蒸馏 teacher。
- 课程：程序生成 rigid terrain，particle filtering 自动选择适中难度。

### 3.2 关键结果

- 同一 proprioceptive controller 在两代 ANYmal 上部署，覆盖泥、雪、碎石、厚植被、流水等未见自然环境。
- 不显式使用 contact/slip estimator，却能通过历史隐式处理打滑和动态 foothold。
- 可携带 10 kg payload，并在不同 step height 上保持更高成功率。

### 3.3 Ablation 因果链

| 设计 | 去掉后的风险 | 机制 |
|---|---|---|
| TCN history | 不能可靠处理滑移/接触突变 | 单帧 proprioception 不含地形响应的时间导数与延迟信息 |
| privileged teacher | rough-terrain RL 难以起步 | 稀疏成败信号被 teacher 的地形/接触先验密集化 |
| adaptive curriculum | 训练地形过易或过难 | 固定随机化不能持续停在能力边界，学习信号不稳定 |

## 4. 工程关键细节

- 不要把显式 contact/slip threshold 当作核心状态机；阈值在真机自然环境中容易失效。
- History encoder 比直接展平更稳，TCN 以有限感受野提取局部接触事件。
- 课程采样应围绕 medium difficulty，而不是单调追求最难环境。

## 5. 核心洞见

### 5.1 理论局限性

- **理论**：teacher-student distillation 缺乏对 OOD terrain 的形式化保证。
- **算法**：student 只模仿 teacher，可能继承 teacher 在仿真中特有的偏差。
- **工程**：terrain curriculum 的成功度估计依赖大量 rollout，训练成本不低。

### 5.2 与 WMTS 的启发

[[Final_WMTS]] 的 Oracle-Generalist 可以吸收这条路线：Oracle 拥有特权接触力/摩擦/物体姿态，Generalist 只看触觉、本体感觉与历史。尤其在灵巧手上，TCN/1D-CNN history encoder 应成为 Actuator Model 和 tactile encoder 的默认结构，而不是可选工程细节。

> [!note] privileged teacher-student：贯穿 locomotion × in-hand 的元范式（本文为根）
> 这篇(2020) 是知识库 **privileged teacher-student 范式的根**——仿真特权训 teacher（降探索难度）、proprioceptive history 蒸馏 student（真机可部署）。这个范式从 locomotion 扩散到整个 in-hand rotation 簇：
>
> | 论文 | 特权信息（teacher） | student 观测 |
> |------|----------------|------------|
> | 本文（locomotion） | terrain/contact profile | proprioceptive TCN history |
> | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] | 物体参数 extrinsics | 本体历史（**RMA = 把本文范式迁到手**） |
> | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] / [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing\|Robot Synesthesia]] | 物体位姿/几何 | 触觉/点云 |
> | [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | （关节级动力学） | RMA 下放到关节 |
> | [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation\|CSR]] | 完整观测（critic） | 渐进缩减（actor） |
>
> **领域级 insight**：HORA 的 RMA、AnyRotate/Robot Synesthesia 的 teacher-student、CSR 的 asymmetric AC、DexNDM 的关节级辨识——**都是本文"privileged teacher → proprioceptive student"范式在灵巧手上的变体**。这条范式从 ANYmal(2020) 到 Shadow/Allegro Hand(2022–2024) 的迁移，是 sim-to-real 的一条主动脉。而 **particle-filter curriculum（维持中等难度 $p^*$）** 是另一条线，与 AnyRotate 自适应课程、[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] 的 auto-curriculum 同源——§7 提议改为"接触模式粒子课程"用于转笔。

## 6. 与知识体系的联系

- [[ReinforcementLearning]]：privileged teacher 是仿真中降低探索难度的 RL 训练技巧。
- [[ControlTheory]]：student 输出 residual/position targets，本质上调制底层运动 primitive。
- [[SignalProcessing]]：proprioceptive stream 的时序编码替代显式接触阈值检测。
- [[RepresentationLearning]]：TCN 将历史传感序列压缩为隐式地形/接触状态。

## 7. 局限与未来方向

对转笔任务，particle-filter curriculum 可改写为“接触模式粒子课程”：粒子不是地形参数，而是转轴、接触手指集合、摩擦/质量参数和任务速度，目标仍是维持在通才刚好可学习的边界。

## 8. 簇内关联与暗线锚点

> [!abstract] 运动技能/表征簇内定位
> - **vs [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]]**：两者都靠**蒸馏**得可扩展策略，但监督源不同——本文是 privileged teacher（terrain/contact 特权）→ proprioceptive student，OmniXtreme 是 multi-motion experts → Flow Matching student（DAgger）。Delta：跨地形单策略泛化（模仿单 teacher）vs 跨运动生成式统一（蒸馏多专家为分布）。
> - **vs [[Learning Agile and Dynamic Motor Skills for Legged Robots|Learning Agile]]**：同 ANYmal 的两条 sim-to-real 主线——Learning Agile 治 **actuator gap**（前向物理，$\Delta_T$），本文治 **perception gap**（privileged→proprioceptive，$\Delta_S$/$\Delta_O$）。两者正交互补，可叠加成完整管线（结构化 WM + 特权蒸馏）。
> - **vs [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]**：都以"降低探索难度"为目标——本文用 teacher 把稀疏成败信号密集化，PDDM 用短 horizon dense transition supervision + ensemble；两者都指向 WMTS 的 Oracle-Generalist 与 uncertainty-driven 课程。

> [!tip] 暗线：Continuation / 同伦 / 平滑化（课程维持"刚好困难"）
> particle-filter curriculum 用权重 $w_i\propto e^{-(\hat p_{succ}-p^*)^2/2\sigma^2}$ 把训练分布锁在中等难度 $p^*$——正是本库 **Continuation/课程暗线**"先解平滑近凸子问题、再逐步引真难度"的具身版。精确锚点：
> - [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间]] — 本文课程是该谱系（Learning Progress / Regret / ADR / POET）的地形版原型
> - [[SignalProcessing#5.2 演进脉络：KF → EKF → UKF → PF → 因子图]] — 课程用的 particle filter 与状态估计 PF 同源；student 的 TCN history 隐式做接触事件时序推断
> - [[RepresentationLearning#4.6 序列与注意力表征：从无序集合到有序序列]] — TCN 把 proprioceptive history 压成隐式地形/接触状态
