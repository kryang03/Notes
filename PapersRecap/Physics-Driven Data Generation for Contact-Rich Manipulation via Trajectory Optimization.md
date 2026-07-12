---
tags:
  - paper
  - trajectory-optimization
  - data-generation
  - contact-rich
  - cross-embodiment
  - diffusion-policy
aliases:
  - PhysicsGen
  - Physics-Driven Data Generation
paper-year: 2025
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization.pdf]]"
related:
  - "[[Optimization]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
---

# Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization

> [!abstract] 核心贡献
> PhysicsGen 把少量 VR 人手演示作为 contact-rich task 的全局接触时序提示，先经运动学重定向适配到目标机器人，再用带动力学约束的轨迹优化在不同物理参数和初始条件下局部细化，生成可训练 diffusion policy 的动态可行数据。

> [!tip] 与理论基础的关联
> - [[Optimization]] — 核心是两级非凸优化：逐时刻 kinematic retargeting + 轨迹级 dynamics-constrained optimization；demo 提供 warm start，优化负责 feasibility。
> - [[Dynamics]] — 生成数据必须满足 $x_{t+1}=f(x_t,u_t,\theta_t)$，这正是 MimicGen 式几何重放在接触任务上不够的地方。
> - [[ContactMechanics]] — 论文没有把 contact force 显式写进 recap 可滥用的互补公式，而是通过 physics engine time-stepping 和 non-penetration constraints 处理 contact；重点是 making/breaking contact 的动态可行性。
> - [[ReinforcementLearning]] — 最终仍是 imitation learning / diffusion policy；轨迹优化不是最终 policy，而是高质量离线数据生成器。
>
> **核心技术**: VR hand demonstration, kinematic retargeting, demonstration-guided trajectory optimization, physical-parameter randomization, cross-embodiment data generation, state-based diffusion policy

## 0. 阅读定位与范本价值

这篇论文是 data-generation 簇里从 “几何复用” 走向 “动力学可行生成” 的关键一步。MimicGen 的核心公式保持 object-relative end-effector pose；PhysicsGen 的核心公式进一步要求轨迹满足系统动力学：

$$
x_{t+1}=f(x_t,u_t,\theta_t).
$$

| 四支柱 | 本文要回答的问题 | 本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么仅靠 kinematic replay 不够，trajectory optimization 的 value add 在哪里？ | §1 对比 MimicGen/CyberDemo/CITO/RL，指出本文把 demo 当作 global contact prior |
| 原理与理论 | retargeting 和 trajopt 公式如何从零理解？ | §2 从对应点匹配、非穿透、joint limit、dynamics constraint、物理参数随机化逐步推导 |
| 实验与验证 | 哪些数字证明“动力学可行”而不是“数据更多”是关键？ | §3 用 Table II、Fig. 8、硬件 6/23→17/23 解释 causal chain |
| 未来与结合 | 它能否给 LinkerHand 转笔/WMTS 直接造数据？ | §5-§7 区分可迁移的 demo-guided optimization 与仍缺的 tactile/latency/visuomotor/远 OOD recovery |

对用户的 WMTS 来说，这篇的关键 insight 是：**人类 demo 不需要精确到能直接模仿；它可以只提供“接触何时发生、在哪里发生、任务大致怎么走”的全局引导，剩下的局部物理一致性由 trajectory optimizer / world model 修正。**

## 1. 问题设定与动机

### 1.1 一句话核心

MimicGen 解决了 “demo 太少” 的几何复用问题；PhysicsGen 解决的是更难的一层：**contact-rich task 中，几何上像 demo 的轨迹不等于动力学上能执行的轨迹**。

论文的结构性赌注是：

$$
\text{human demo}
\xrightarrow{\text{global contact/motion prior}}
\text{trajectory optimization}
\xrightarrow{\text{local dynamic feasibility}}
\text{large contact-rich dataset}.
$$

人类 demo 擅长给出全局策略：何时接触、从哪个方向推/翻/扶、如何完成长程任务；trajectory optimization 擅长局部修正：让轨迹满足动力学、非穿透、关节/速度/输入约束，并适配不同质量、摩擦、尺寸和机器人 embodiment。

### 1.2 直观隐喻

PhysicsGen 像“人画草图，工程师做受力校核”：

- 人类 demo 是草图：它告诉系统“这里该接触、那里该翻转、这个阶段要扶住物体”；
- kinematic retargeting 把草图缩放/映射到目标机器人；
- trajectory optimization 做结构校核：动作是否可达、是否穿透、是否能保持接触、换质量/摩擦后是否仍可行。

这个隐喻的可证伪点是：如果轨迹优化只是锦上添花，kinematic retargeted demo 应该已经有不错成功率；但 Table II 中原始 retargeted replay 只有 4/24、5/24、6/24，trajectory optimization 在 3000 个扰动样本中成功 2164、2252、2462 次，说明动态可行性是核心 bottleneck。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 | PhysicsGen 的增量 |
|---|---|---|---|
| 大规模真实 teleoperation | 真实 robot contact 数据最可信 | contact-rich / bimanual / dexterous teleop 成本高，硬件延迟和 embodiment gap 大 | 用 VR simulation 快速采少量 embodiment-flexible demos |
| MimicGen / DexMimicGen | object-centric kinematic replay | 对 making/breaking contact、摩擦、质量变化不够；open-loop replay 容易丢接触 | 用 trajectory optimization 让生成轨迹满足 dynamics |
| Contact-implicit / sampling-based planning | 可搜索 contact-rich trajectory | 长程接触任务全局搜索难，需要好 initial guess | demo 提供全局 contact prior / warm start |
| RL + demonstrations | policy 可通过 reward 优化全局目标 | 高维策略搜索样本成本高，需要 reward shaping | 直接在 trajectory space 局部优化生成数据，再做 IL |
| Cross-embodiment datasets | 多机器人数据促进泛化 | 真实跨机器人采集昂贵，且 end-effector 不同会卡住 | 同一 VR hand demo 可 retarget 到 Allegro、iiwa、Panda |

### 1.4 Delta 分析

本文的精确 delta 可以写成：

$$
\text{kinematic data augmentation}
\quad \to \quad
\text{physics-constrained contact data generation}.
$$

它不是简单把 MimicGen 的 $SE(3)$ 变换换成更复杂的插值，而是改变了数据生成的判据：

| 判据 | MimicGen 类方法 | PhysicsGen |
|---|---|---|
| 轨迹是否合理 | EE target 相对 object frame 保持、执行成功 | 满足 dynamics rollout、non-penetration、state/input bounds，并接近 retargeted demo |
| demo 的作用 | 提供可变换 segment | 提供 global initial guess / contact schedule |
| 主要风险 | 插值穿障碍、success bias | 物理模型误差、局部优化 vicinity、state-only policy |
| 适用任务 | 准静态刚体、单臂/夹爪 | 多接触、bimanual、dexterous contact-rich，但仍主要在 demo vicinity |

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $x^{demo}_{0:T}$ | human/demo state trajectory | VR data collection | 否 | 人手在仿真中的演示轨迹 | 与目标 robot state 维度可不同 |
| $q^{retarget}_t$ | robot configuration | kinematic retargeting | 优化变量，不是 policy 参数 | 第 $t$ 步目标机器人关节配置 | 逐时刻求解，非整段 dynamics-feasible |
| $\psi_i(q)$ | point map | robot kinematics | 对优化变量可求导/近似 | robot 上第 $i$ 个对应点 | 对应点由人手工定义，不是自动学出 |
| $\tilde{\psi}_i(x^{demo}_t)$ | point map | demo state | 否 | human demo 上第 $i$ 个对应点 | 与 $\psi_i$ 输出同空间，但输入维度不同 |
| $w_i$ | positive scalar | retargeting weights | 否 | 对应点匹配权重 | 论文称对权重选择相对 robust，但不是无影响 |
| $\phi_j(q)$ / $\phi_j(x)$ | signed distance | collision geometry | 约束函数 | 非穿透约束 | $\phi\ge0$ 是几何非穿透，不是接触力互补变量 |
| $x^{retarget}_{0:T}$ | robot+object state trajectory | from retargeted robot + demo object state | 否 | trajectory optimization 的参考轨迹 | 运动学可行不等于动力学可行 |
| $x_t,u_t$ | system state/input | trajectory optimization | 优化变量 | 真实生成轨迹和控制输入 | 最终 dataset 的 state-action 轨迹来自这里 |
| $f(x_t,u_t,\theta_t)$ | dynamics time stepper | physics simulator | 固定模型 | 动态约束 | $\theta_t$ 随机化物理参数；不是 learned world model |
| $Q_t,R_t,Q_T$ | cost matrices | optimization design | 否 | 跟踪 retargeted state 与控制 effort 权衡 | object state entries 权重更高，鼓励精确追踪物体 |
| $\rho$ | distribution | domain randomization | 否 | 物理参数/初始条件扰动分布 | 决定生成数据覆盖范围 |
| $\theta_{0:T}$ | physical parameters | sampled from $\rho$ | 否 | object size/mass/friction/initial pose 等 | 真实硬件 gap 不一定被这些参数完全覆盖 |
| $N$ | augmentation number | data generation | 否 | 每条 demo 生成多少 trajectory | 数据多不保证单调更好，硬件 500 gen > 1000 gen |
| $\pi_\theta$ | diffusion policy | BC training | 是 | 从生成数据学习的 state-based policy | 论文主要训练 state policy，不是视觉 policy |

### 2.2 VR demo collection：为什么是 embodiment-flexible

论文用 Apple Vision Pro 追踪人手 pose，并通过 Drake physics simulator 模拟手与物体接触，实时把 object pose 回传到 Vision Pro 用 Vuer 可视化。实际采集效率很高：约 7 分钟收集 24 条 long-horizon demos。

它考虑两类 target embodiments：

| Embodiment | 设置 | demo 如何对应 |
|---|---|---|
| Floating Allegro Hand | 22-DOF free-floating Allegro hand 操作桌上 cube | VR 中限制右手四指，对应 Allegro 四指 |
| Bimanual iiwa / Panda arms | 两个 7-DOF 固定基双臂操作大 box | 人用两个 index fingers 操作小 cube，再按尺寸缩放到双臂/大 box |

这个设计的价值是降低 demonstration 成本：人不需要直接 teleop 两个真实机械臂翻大箱子，也不需要面对硬件延迟。demo 只需要提供“任务怎么做”的全局接触模式，目标机器人细节交给 retargeting + optimization。

### 2.3 运动学重定向 Eq. (1)：从对应点匹配开始

给定每个时刻的 human demo state $x^{demo}_t$，目标是找到 robot configuration $q^{retarget}_t$，使 robot 上若干对应点接近 human demo 上对应点。

论文的逐时刻非凸优化：

$$
q_{t}^{retarget\star}
=
\arg\min_{q_t^{retarget}}
\sum_{i=0}^{N}
w_i
\left\|
\psi_i(q_t^{retarget})
-
\tilde{\psi}_i(x_t^{demo})
\right\|^2
$$

subject to:

$$
\phi_j(q_t^{retarget})\ge0,\quad \forall j,
$$

$$
q_{min}\le q_t^{retarget}\le q_{max}.
$$

每一项的来源：

- $\psi_i(q)$：robot FK 映射，比如双臂系统中左臂 end-effector position；
- $\tilde{\psi}_i(x^{demo})$：human demo landmark，比如左手 index fingertip；
- $\phi_j(q)\ge0$：collision pair 的 signed distance 非负，避免 penetration；
- joint limits 保证 retargeted configuration 可执行。

无跳步理解：这不是要求人手和机器人 DoF 一样，而是要求它们在某些 task-relevant points 上对齐。只要 $\psi_i$ 和 $\tilde{\psi}_i$ 输出同一空间向量，$q$ 和 $x^{demo}$ 可以完全不同维。

### 2.4 为什么 retargeting 还不够

Retargeting 输出的是：

$$
q_{0:T}^{retarget\star}.
$$

它解决的是“姿态像不像”，不是“动力学能不能做到”。接触-rich 任务中，即使每一帧几何姿态看起来合理，rollout 时也可能：

- contact force 不足，物体滑走；
- 初始 pose 稍变，手/臂错过接触；
- 质量/摩擦变化，原动作无法维持旋转；
- 关节速度/输入约束导致时序跟不上；
- 多接触模式切换失败。

Table II 直接说明这一点：原始 24 条 demos 只 retarget/replay，Floating Allegro 4/24、iiwa 5/24、Panda 6/24；一旦扰动物体尺寸、初始平移或初始姿态，成功率更低。换句话说，retargeting 是必要 warm start，不是可训练数据的最终形态。

### 2.5 Demonstration-guided trajectory optimization Eq. (2)

将 retargeted trajectory 转成 state reference：

$$
x^{retarget}_{0:T}.
$$

Trajectory optimization 求：

$$
x_{0:T}^{\star},u_{0:T-1}^{\star}
=
\arg\min_{x_t,u_t}
\left\|x_T-x_T^{retarget}\right\|^2_{Q_T}
+
\sum_{t=0}^{T-1}
\left(
\left\|x_t-x_t^{retarget}\right\|^2_{Q_t}
+
\left\|u_t\right\|^2_{R_t}
\right)
$$

subject to:

$$
x_{t+1}=f(x_t,u_t),
$$

$$
\phi_j(x_t)\ge0,\quad \forall j,
$$

$$
x_{min}\le x_t\le x_{max},
\quad
u_{min}\le u_t\le u_{max}.
$$

这不是在让轨迹盲目贴人类 demo。目标函数有两股力：

| 项 | 作用 | 直觉 |
|---|---|---|
| $\|x_t-x_t^{retarget}\|^2_{Q_t}$ | 保持 demo 的全局路径/接触时序 | 不要让 optimizer 搜到完全不同的局部解 |
| $\|u_t\|^2_{R_t}$ | 控制 effort 正则 | 不要用不可部署的大动作硬追 |
| dynamics constraint | 保证 time-stepping 物理一致 | 数据不是 kinematic fantasy |
| non-penetration/state/input bounds | 保证几何和执行约束 | 避免穿透、越界、不可执行 |

论文还强调对 object state 对应的 $Q_t$ entries 给更高权重，目的是精确跟踪物体轨迹。对 contact-rich manipulation，最终评估看的是 object 是否被翻到目标 pose，而不是手/臂姿态是否复刻人类。

### 2.6 物理参数随机化：从一条 demo 到一族动态系统

为了生成 diverse dataset，论文采样：

$$
\theta_{0:T}\sim\rho,
$$

并把 dynamics 改写成：

$$
x_{t+1}=f(x_t,u_t,\theta_t).
$$

Algorithm 1 的核心循环：

1. 对 demo $x^{demo}_{0:T}$ 求 $q^{retarget}_{0:T}$；
2. 对第 $n$ 个 augmentation，采样 $\theta_{0:T}\sim\rho$；
3. 用 $x^{retarget}_{0:T}$ 作 guidance，解 Eq. (2)；
4. 保存 $(x^\star_{0:T},u^\star_{0:T-1})$。

Table I 的随机化范围：

| Parameter | Floating Allegro Hand | Bimanual Robot Arms |
|---|---:|---:|
| Initial object translation perturbation | $[\pm1.5,\pm1.5,0]$ cm | $[\pm5,\pm5,0]$ cm |
| Initial object yaw perturbation | $[0,0,\pm0.3]$ rad | $[0,0,\pm0.3]$ rad |
| Object side length | 5.8-6.2 cm | 28-32 cm |
| Object mass | 0.1-0.3 kg | 0.25-0.75 kg |
| Friction coefficients | 0.7-1.3 | 0.2-0.4 |
| Task horizon reported | 25 | 50 / 260 (Panda / iiwa) |

这张表说明本文不是只在一个 nominal simulator 上优化，而是在一族局部物理系统上生成轨迹。对 sim-to-real 重要的不是“最准确的一条仿真轨迹”，而是“覆盖真实硬件附近的动态可行轨迹族”。

### 2.7 概念边界与符号陷阱

- $\phi_j\ge0$ 在论文公式里是 signed-distance non-penetration constraint；不要擅自把本文主公式改写成含 $\lambda$ 的 contact complementarity 公式。CITO 是相关背景，本文实际写出的 Eq. (2) 通过 physics time-stepper $f$ 和 non-penetration/state bounds 表达。
- $x^{retarget}$ 是 reference，不是 hard constraint。Optimizer 可以为了动力学可行偏离 demo。
- 本文训练的是 state-based diffusion policies。不要把它直接说成 visuomotor sim-to-real；作者明确把 synthetic rendering/visuomotor extension 留给 future work。
- Zero-shot hardware 只在 bimanual iiwa arms 上展示，不是 Allegro hand 硬件。
- 生成 1000 条不一定比 500 条硬件更好：Fig. 8b 中 500 generated 是 17/23，1000 generated 是 16/23。

## 3. 训练、数据与实验

### 3.1 任务与评估设置

| 项 | 设置 |
|---|---|
| Human demos | 24 条 VR demos，约 7 分钟采集 |
| Embodiments | Floating Allegro hand, bimanual Kuka LBR iiwa arms, bimanual Franka Panda arms |
| Task | 在桌面上把 cube/box 操作到 target pose，需要频繁 make/break contact |
| Allegro success | object within 3 cm and 0.2 rad of target pose |
| Bimanual arms success | object within 10 cm and 0.2 rad of target pose |
| Trajectory optimizer | CEM used to solve Eq. (2) over sampled physical parameters/initial conditions |
| Policy | state-based diffusion policy |
| Simulation eval | 48 rollouts per embodiment |
| Hardware eval | bimanual iiwa arms, 23 trials; OptiTrack estimates object pose |

### 3.2 Trajectory optimization 是否真的必要

Table II 是全文最关键的机制表：

| Perturbation / method | Allegro Hand | iiwa Arms | Panda Arms |
|---|---:|---:|---:|
| Original demo replay after retargeting | 4 / 24 | 5 / 24 | 6 / 24 |
| Object size perturbation | 2 / 24 | 1 / 24 | 4 / 24 |
| Initial object translation perturbation | 1 / 24 | 3 / 24 | 2 / 24 |
| Initial object orientation perturbation | 2 / 24 | 3 / 24 | 3 / 24 |
| Trajectory optimization under random perturbations | 2164 / 3000 | 2252 / 3000 | 2462 / 3000 |

因果解释：

`kinematic retargeting only → robot lightly touches / misses / loses contact → object moves out of reach → success 4-6/24 → visual plausibility is not dynamic feasibility.`

`demo-guided trajectory optimization → optimizer increases contact area, recruits second arm, adjusts actions for mass/friction/pose → success ~72%-82% over 3000 randomized trials → trajectory optimization is doing the contact-feasibility work.`

图 4 的 qualitative 证据也支持这一点：Allegro retargeted trajectory 会轻触 cube 后丢失接触；trajopt 后手会增加接触面积形成稳定 grasp。iiwa retargeted demo 倾向单臂翻箱，trajopt 后另一只臂参与扶持，尤其对更重、更小、低摩擦物体有帮助。

### 3.3 生成数据训练 diffusion policy

论文用原始 24 demos、500 generated trajectories、1000 generated trajectories 分别训练 state-based diffusion policies。

| Embodiment | Baseline: 24 demos | Generated-data policy | 机制解释 |
|---|---:|---:|---|
| Floating Allegro | 10/48 = 21% | up to 39/48 = 81% | 生成数据覆盖更多 object orientations/translations，policy 能 missed contact 后重新建立接触 |
| Bimanual iiwa | 27/48 = 56% | up to 44/48 = 92% | 速度限制使 baseline 较准静态但仍抖；生成数据学到更平滑 contact maintenance |
| Bimanual Panda | 14/48 = 29% | up to 42/48 = 87.5% | Panda 约束更松、行为更动态，原 demo 更难泛化；trajopt 数据显著扩展可恢复状态 |

Ablation 因果链：

`train only on 24 demos → policy encounters OOD object pose/contact deviation → jitter/missing contact/stuck on object surface → success low.`

`train on generated trajectories → dataset contains physically feasible recoveries around demo manifold → diffusion policy learns smoother multimodal actions → success rises to 81-92%.`

这里的重点不是 diffusion policy 本身，而是数据分布。Diffusion policy 能表示多模态动作，但如果只有 24 demos，仍然缺少 contact-rich recovery states；trajectory optimization 才是把这些状态补出来的机制。

### 3.4 Zero-shot hardware deployment

硬件部署在 bimanual iiwa arms 上完成，任务是翻转 30 cm cube/box 到目标 pose。

| Policy training data | Hardware success |
|---|---:|
| 24 original demos | 6/23 = 26% |
| 500 generated trajectories | 17/23 = 74% |
| 1000 generated trajectories | 16/23 = 70% |

因果解释：

- Baseline 的成功 rollout 多数是短程 1-2 次旋转；失败主要是偏离 demo 后手臂撞到 box 表面，或 box 滑动后进入未见状态。
- Generated-data policies 能用一只臂更牢地扶住对侧，恢复 undesired sliding，说明 trajectory optimization 学到的 contact maintenance 能迁移到硬件。
- 1000 条略低于 500 条提醒我们：更多生成数据不自动更好。硬件失败有 unmodeled collision geometries，数据量无法补偿模型错误；生成分布质量和 sim-to-real coverage 比数量更关键。

这是真正支持论文 value add 的硬件证据：不是只在仿真中“轨迹优化成功”，而是从生成数据训练出的 state policy 可以 zero-shot 提升真实双臂成功率。

### 3.5 工程边界与失败模式

| 观察 | 论文证据 | 解释 |
|---|---|---|
| Original demo baseline 抖动明显 | Fig. 7 | 24 demos 覆盖窄，policy 一离开 demo manifold 就 jitter/miss contact |
| Generated policy 仍会失败 | Fig. 10c | iiwa unmodeled collision geometry 导致 undesired yaw motion |
| Generated policy 可恢复部分滑移 | Fig. 10d | trajopt 找到更 firm grasp / bimanual support strategy |
| 主要是 state-based policy | Limitations | 没有解决视觉域迁移；synthetic rendering 留给 future |
| 远离 demo 的 catastrophic states 仍难恢复 | Limitations | Trajopt 在 demonstration vicinity 强，远 OOD 需要迭代数据收集/更强规划 |

## 4. 核心洞见

### 4.1 论文真正的 insight

PhysicsGen 的真正 insight 是：**在 contact-rich manipulation 中，demo 的价值不是提供可直接复制的动作，而是提供 trajectory optimizer 最缺的全局接触结构。**

接触任务的搜索难点是 combinatorial contact mode sequence：什么时候接触、用哪一侧接触、何时换手、怎样防止物体滑走。纯 trajectory optimization 没有 good initial guess 容易陷入局部最优；纯 human/VR demo 又缺动态可行性。两者结合刚好互补。

### 4.2 为什么它比 MimicGen 更适合 contact-rich 任务

MimicGen 保持：

$$
T_{O'}^{C'}=T_O^C.
$$

PhysicsGen 进一步要求：

$$
x_{t+1}=f(x_t,u_t,\theta_t).
$$

这一个约束改变了方法类别。对 pick-and-place，object-relative pose 可能已经足够；对 box flipping / cube reorientation，接触力、摩擦、速度、惯性和多臂协调决定成败。因此 PhysicsGen 是 MimicGen line 在 contact-rich 方向上的自然升级，而不是简单替代。

### 4.3 什么时候会失效

| 失效条件 | 原因 | 对 WMTS/转笔含义 |
|---|---|---|
| 真实物理模型与仿真差距大 | Trajopt 数据满足错误的 $f$ | LinkerHand actuator latency/tactile/friction 需实测校准或 ensemble WM |
| 任务需要远离 demo 的 recovery | Local refinement 在 demo vicinity 强，远 OOD 弱 | 转笔掉落前后的 recovery 不能只靠 24 demos 邻域 |
| 目标机器人能力与人手 demo 策略不匹配 | VR hand demo 可能没利用目标 robot 独特 kinematics | LinkerHand 连续旋转/欠驱/耦合结构需 embodiment-aware demo 或 planner |
| 需要视觉闭环 | 当前主要 state-based | 真实转笔需要视觉/触觉观测融合 |
| 接触模式高速切换/aerial phase | Time-stepping + local trajopt 可能难覆盖冲击/飞行段 | Pen spinning 的 aerial/catch 阶段要额外建模 |

## 5. 替代方案与理论局限

### 5.1 理论维度

**它不是从零解决 contact planning。** Demo 提供的 $x^{retarget}$ 是强先验。如果没有 demo，Eq. (2) 的局部优化仍可能卡在无进展局部最优。

**物理一致性只相对于仿真模型成立。** 轨迹满足：

$$
x_{t+1}=f_{\mathrm{sim}}(x_t,u_t,\theta_t),
$$

不等于满足真实：

$$
x_{t+1}^{real}=f_{\mathrm{real}}(x_t,u_t).
$$

Domain randomization 缩小差距，但无法覆盖未建模碰撞几何、柔性、传感延迟和控制器误差。硬件中 unmodeled collision geometry 已经造成 failure。

**State-only policy 限制了感知闭环结论。** 如果 policy 依赖 object pose from OptiTrack，那么它证明的是 state-policy contact control，而不是视觉/触觉端到端 policy。

### 5.2 算法维度

| 替代路线 | 优点 | 相对 PhysicsGen 的差别 |
|---|---|---|
| MimicGen | 简单、规模化、适合准静态几何复用 | 对动态接触不够；无 dynamics constraint |
| Pure CITO / sampling planner | 可直接优化物理轨迹 | 没有 demo guidance 时长程接触搜索难 |
| RL from demos | 最终可优化 policy objective | 高维探索和 reward shaping 成本大 |
| CyberDemo | 更直接面向真实 dexterous sim-to-real fine-tune | 不像 PhysicsGen 显式用 trajopt 保证 contact dynamics |
| Offline diffusion policy on raw demos | 算法简单 | 24 demos 覆盖不足，接触 recovery 学不到 |

### 5.3 工程/实验维度

- 需要高质量 robot/object geometry 和 physics simulator。
- 每条 trajectory optimization 有计算成本，规模不像纯 replay 那么便宜。
- 仅在 iiwa 硬件 zero-shot；Allegro hand 硬件未展示。
- 物理参数随机化范围是人工设定，真实系统偏差若超出范围会失败。
- VR hand demos 可能无法表达目标 robot 的特殊动作能力。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的直接迁移

PhysicsGen 给 WMTS 的核心启发是：**PPO Oracle / trajectory optimizer / world model 不应该从空白搜索任务；它们应该以 human/demo/legacy trajectory 作为 global prior，再局部生成动态可行数据。**

| PhysicsGen 模块 | WMTS 改造版本 | 为什么有价值 |
|---|---|---|
| VR human demos | 少量 human/retargeted/PPO seed trajectories | 提供全局 contact schedule |
| Kinematic retargeting | embodiment-aware trajectory initialization for LinkerHand | 把人手/其他手数据映射到 LinkerHand 初始轨迹 |
| Eq. (2) trajectory optimization | simulator/ensemble-WM-guided local refinement | 生成满足 dynamics/contact/actuator constraints 的轨迹 |
| $\theta\sim\rho$ | mass/friction/tactile/latency/domain randomization | 覆盖真实硬件参数不确定性 |
| state-based diffusion policy | Diffusion/Flow generalist + tactile/contact state | 从生成数据学可恢复的多模态控制 |
| hardware failures | real fine-tune / residual dynamics grounding | 用真实失败修正未建模碰撞和控制器 gap |

更具体地，WMTS 可以把 trajectory optimization 的输出当作 PPO Oracle 的 curriculum seed，而不是直接当最终数据。PPO 可以继续在生成轨迹附近探索更鲁棒策略，world model 负责识别哪些局部扰动仍在可信物理范围内。

### 6.2 对 LinkerHand 转笔/DNPM 的实验建议

一个可落地的转笔版本：

1. 用 VR/MoCap/视频估计采集少量人手转笔 phase demonstrations；
2. 通过对应点映射 $\psi_i,\tilde{\psi}_i$ retarget 到 LinkerHand fingertip/contact frames；
3. 把状态从单纯 pose 扩展为：

$$
x_t = [q_t,\dot q_t, T^{pen}_t, v^{pen}_t,\omega^{pen}_t, c_t, h_t^{tactile}],
$$

其中 $c_t$ 是 contact mode，$h_t^{tactile}$ 是触觉 latent；

4. 用 trajectory optimization 或 learned ensemble world model 细化 contact force / timing；
5. 随机化 pen mass distribution、surface friction、finger pad stiffness、actuator latency；
6. 训练 diffusion/flow policy，并在真机少量 fine-tune。

关键对照实验：

| Baseline | 预期作用 |
|---|---|
| Raw retargeted demos only | 检验纯运动学是否像 Table II 一样失败 |
| Retarget + dynamics trajopt | 检验动态可行性提升 |
| Retarget + trajopt + tactile/latency randomization | 检验真实 LinkerHand gap 是否来自未建模触觉/执行器 |
| PPO Oracle seeded by trajopt | 检验 RL 能否超越局部 demo vicinity |

如果 raw retarget 在转笔上完全失败，而 trajopt 也只能短程成功，说明转笔 bottleneck 可能超出局部 trajectory optimization，需要 hybrid contact-mode planning 或 world-model imagination。

### 6.3 与 MimicGen / CyberDemo 的组合定位

| 方法 | 生成数据的物理层级 | 适合的任务 |
|---|---|---|
| MimicGen | kinematic object-relative segment | 准静态、刚体、物体坐标系复用 |
| CyberDemo | sim replay + visual/kinematic/geometric augmentation + real fine-tune | 面向真实灵巧操作 deployment |
| PhysicsGen | dynamics-constrained contact-rich trajectory optimization | 多接触、跨具身、需要动态可行轨迹 |

组合顺序可以是：

$$
\text{MimicGen segment structure}
\to
\text{PhysicsGen dynamic refinement}
\to
\text{CyberDemo-style real fine-tune / visual augmentation}
\to
\text{WMTS ensemble world model scheduling}.
$$

这条链比单篇论文更接近用户项目：先解决“长程任务怎么拆/复用”，再解决“接触轨迹是否物理可行”，最后解决“真实视觉/触觉/执行器 gap”。

### 6.4 不应过度外推的点

- 不要把 trajectory optimization success 当作 policy success；Table II 是生成轨迹成功，Fig. 8 才是 policy rollout。
- 不要说它已经解决 visuomotor policy；作者明确说主要验证 state-based policies。
- 不要忽略 500 generated 在硬件略高于 1000 generated；生成数据质量、分布和模型误差比数量更关键。
- 不要把 VR hand demo 视为自动跨所有机器人最优；它可能没利用目标机器人独特能力。
- 不要把它当成无需真实数据的最终方案；硬件 failure 已显示 unmodeled geometry 和 sim-to-real gap。

## 7. 与知识体系的联系

### 7.1 与 [[Optimization]] 的联系

本文是 “demo-warmstarted constrained trajectory optimization” 的典型范式。Retargeting Eq. (1) 是逐时刻非凸匹配；trajectory optimization Eq. (2) 是带 dynamics/state/input constraints 的轨迹级非凸优化。

最值得抽象的不是具体 solver，而是搜索空间分工：

$$
\text{demo handles global mode sequence},
\quad
\text{optimizer handles local feasibility}.
$$

这也是所有 contact-rich optimizer 的常见痛点：没有 mode prior 时全局搜索爆炸；有 demo prior 时局部优化突然变得可用。

### 7.2 与 [[Dynamics]] 的联系

PhysicsGen 相对 MimicGen 的升级可以浓缩为一个约束：

$$
x_{t+1}=f(x_t,u_t,\theta_t).
$$

这里 $f$ 是 simulation time-stepper，不是 learned dynamics。对 WMTS 来说，一个自然延伸是用 ensemble world model 近似或校正 $f$：

$$
x_{t+1}\sim p_\phi(x_{t+1}\mid x_t,u_t),
$$

并用 uncertainty 决定哪些 generated trajectories 可进入训练集。

### 7.3 与 [[ContactMechanics]] 的联系

论文没有显式推导接触互补条件，但现象层面全在接触：miss contact、lose contact、stuck on surface、firmer grasp、second arm support。它说明 contact-rich data generation 的核心不是让机器人“像 demo”，而是让接触模式在物理上可持续。

对转笔，这意味着数据生成必须显式关心：

- 接触点是否存在；
- 法向力是否足够；
- 切向力是否越过摩擦锥；
- stick/slip/release/catch phase 是否正确；
- 触觉观测是否能区分这些模式。

### 7.4 与 [[ReinforcementLearning]] 的联系

PhysicsGen 最终仍是 imitation learning pipeline：generated trajectories 训练 diffusion policy。它和 RL 的关系是互补而非替代。RL 适合在 generated data 附近继续搜索 policy improvement；trajectory optimization 适合把少量 demo 快速扩展成高质量 offline dataset。

> [!note] 簇内补链 · Foundation 精确锚点 · 暗线
> **簇内互链 + Delta**：
> - vs [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|Residual LfD]]：同属"**全局 demo 先验 + 局部细化**"——本文用 trajopt 补动力学可行性、rLfD 用 RL residual 补接触搜索；本文离线**造数据**、rLfD 在线**学策略**，可级联（先 PhysicsGen 造 base chunk 再叠 rLfD residual）。
> - vs 阻抗/力控簇（[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]] / [[Minimalist Compliance Control|MCC]]）：本簇多数论文解决"接触时**怎么控**"，PhysicsGen 解决上游"接触数据**从哪来**"——生成的 $(x_t,u_t)$ 最终仍要由阻抗/力控器执行。
>
> **Foundation 精确锚点**：Eq.(2) 带 $x_{t+1}=f(x_t,u_t,\theta_t)$ 的轨迹级非凸优化 = [[Optimization#5. 演进脉络：从模态预设到接触隐式（修复梯度流的四个阶段）|Optimization §5]] 接触隐式轨迹优化谱；非穿透 $\phi_j\ge0$ 与接触互补 = [[Optimization#3.1 互补约束：接触把可行域撕成"坐标轴的并集"|Optimization §3.1]]；physics time-stepper $f$ = [[Dynamics#6. 仿真层：接触动力学的深水区|Dynamics §6]]。
>
> **暗线 · 接触的非光滑性**：contact-rich 任务的核心难点是 **combinatorial contact mode sequence**（何时接触、哪侧接触、何时换手）——正是接触把优化景观撕成非凸/非光滑（[[ContactMechanics#5.1 互补条件与 LCP 的构建|ContactMechanics §5.1]]）。demo 提供全局模式先验、trajopt 做局部可行，正是应对"纯全局搜索因非光滑爆炸"的标准解法。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “它相对 MimicGen 的 value add 是什么？” | MimicGen 保持 $SE(3)$ 相对 pose；PhysicsGen 增加 dynamics constraint $x_{t+1}=f(x_t,u_t,\theta)$，解决 contact-rich retargeting 动态不可行 |
| “Eq. (1) 的变量从哪来？” | $\psi_i(q)$ 是 robot 对应点 FK，$\tilde\psi_i(x^{demo})$ 是 human demo landmark，$\phi_j\ge0$ 是非穿透，joint limits 保证可执行 |
| “Eq. (2) 为什么不是单纯 imitation loss？” | 它同时追踪 retargeted demo、惩罚控制 effort、满足 dynamics/nonpenetration/state/input constraints；demo 是 reference，不是硬标签 |
| “哪个实验最能证明故事？” | Table II：kinematic replay 4-6/24 vs trajopt 2164-2462/3000；Fig. 8：policy 从 21/56/29% 到 81/92/87.5%；hardware：6/23 到 17/23 |
| “能直接用于转笔吗？” | 不能直接；要把 state 扩展到 pen angular velocity/contact/tactile/latency，并用 world model 或 contact optimizer 处理高动态 phase |

## References

- Lujie Yang, H.J. Terry Suh, Tong Zhao, Bernhard Paus Græsdal, Tarik Kelestemur, Jiuguang Wang, Tao Pang, Russ Tedrake. **Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization**. arXiv 2025.
