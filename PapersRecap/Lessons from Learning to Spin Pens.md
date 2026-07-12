---
tags:
  - paper
  - dexterous-manipulation
  - pen-spinning
  - in-hand-manipulation
  - sim-to-real
  - reinforcement-learning
  - PPO
aliases:
  - Lessons from Pen Spinning
  - Pen Spinning
  - Spin Pens
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

> [!abstract] 核心贡献
> 这篇论文不是提出一个新 policy backbone，而是给 pen-like object spinning 建立了一条可落地的 sim-to-real 数据路线：先用 privileged oracle PPO 在仿真中探索出可转笔的动作轨迹，再用这些轨迹预训练纯本体 sensorimotor policy，并把筛选出的 oracle 动作序列在真机 open-loop replay，收集每个训练物体 15 条、共 45 条成功轨迹来 fine-tune policy；最终在 3 个训练物体和 7 个未见 pen-like objects 上实现多圈 z-axis pen spinning。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — pen spinning 是 contact mode switching + rigid-body angular momentum control；finger gaiting 必须交替供矩与复位。
> - [[ContactMechanics]] — $r_z$ 约束笔保持水平，本质是避免倾斜后重力矩和摩擦锥限制把仿真可行解变成真机滑落。
> - [[ReinforcementLearning]] — PPO oracle 解决探索，behavior cloning / fine-tuning 解决部署；direct DAgger distillation 在该任务上失败。
> - [[ControlTheory]] — 20 Hz neural joint-position target + 333 Hz PD controller，动作是位置目标而不是 torque。
> - [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]] — oracle rollout → sim pretrain → open-loop replay 筛真机数据 → fine-tune，是"模仿×强化"缝合线的一个数据引擎实例：真机成功轨迹当 BC 目标，而非真机在线 RL。
> - [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]] — **电流≠关节力矩**暗线：action=20 Hz position target 经 333 Hz PD 转 torque，且训练加 action noise 提升 actuator robustness；open-loop replay 之所以能筛出可迁移轨迹，正因 $r_z$ 剔除了那些"仿真力精确、真机执行器 gap 下必滑落"的解。
> - [[EmbodiedAI]] — 这是一条 simulation skill discovery → real trajectory adaptation 的 embodied data engine。
>
> **核心技术**: privileged oracle PPO, six canonical grasps, horizontal $r_z$ reward, open-loop trajectory replay, proprioceptive temporal-transformer student, real-world fine-tuning

## 0. 阅读定位与范本价值

这篇是用户 DNPM / 灵巧手转笔方向的直接母本。它回答的问题不是“如何总结一个 in-hand rotation paper”，而是：

> 当目标物是细长笔状物、无自然支撑、失败后几乎不可恢复、teleoperation 又采不到高速演示时，怎样从 simulation 里挖出真实可用的数据？

论文的答案有强烈的方法论意义：

1. **仿真仍然有用**，但不是直接 zero-shot policy transfer，而是用来发现 feasible motion。
2. **sim-to-real gap 对动态接触任务太大**，不能指望 DR 或 direct distillation 直接跨过去。
3. **open-loop replay 可以把 sim trajectory 的可迁移性变成可测量信号**。
4. **少量真机成功轨迹足够 fine-tune**，前提是 policy 已经从大规模 simulation pretraining 获得 motion prior。

最低标准：

| 支柱 | 本文必须讲清的问题 | 本 recap 的位置 |
|---|---|---|
| 逻辑与价值 | 为什么 pen spinning 比 HORA/RotateIt 更难？为什么 open-loop replay 是关键转向？ | §1 |
| 原理与理论 | finger gaiting、$r_z$、canonical grasp 如何从接触动力学推出？ | §2 |
| 实验与验证 | Table 1/2/3 如何证明 replay、pretraining、fine-tuning 缺一不可？ | §3 |
| 未来与结合 | 如何直接迁移到 LinkerHand 转笔 / WMTS real fine-tuning？ | §5-§6 |

## 1. 问题设定与动机

### 1.1 一句话核心

本文要学的是：

> Allegro Hand 仅靠本体感觉，把 pen-like objects 绕 z-axis 连续旋转多圈；训练期 oracle 可用笔姿态、角速度、点云、触觉和物理属性，但最终部署 policy 只用 30 步 joint positions 和 previous joint targets。

它比一般 in-hand rotation 难在：

- 物体细长，没有稳定支撑面；
- finger gaiting 必须动态交替接触；
- 姿态一旦倾斜，重力矩和摩擦锥限制会让错误快速放大；
- 高速动作 teleoperation 难以采集高质量演示；
- direct sim-to-real 的 physics gap 在动态接触下比 cube/ball rotation 更明显。

### 1.2 直观隐喻

Oracle 轨迹像“乐谱”：

- simulation RL 负责编曲：找到人很难 teleoperate 出来的 finger-gaiting sequence；
- open-loop replay 负责试奏：哪些乐谱在真实乐器上也能奏出旋律；
- fine-tuned student 学会即兴：在真实动力学下用本体反馈闭环修正。

这个隐喻的可证伪点很明确：如果真机动力学差到 open-loop replay 几乎全失败，就收集不到成功轨迹，整套 pipeline 会断。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 对 pen spinning 的关键局限 |
|---|---|---|
| Teleoperation + imitation | 人类示教 | 通信延迟和 retargeting error 对高速动态转笔太致命 |
| classical / trajectory optimization | 精确模型、接触序列 | 需要很准的笔-指接触模型和摩擦，真实物体差异大 |
| Zero-shot DR | 随机化覆盖真实 | 动态接触 gap 太大，extensive DR alone 不够 |
| HORA / RMA | 本体历史估计 extrinsics | pen spinning 失败窗口小，且接触 phase/姿态更难从本体中稳定辨识 |
| Direct DAgger distillation | oracle → sensorimotor policy | visuotactile sim-real gap 大；proprio-only policy 在仿真里都不收敛 |
| More real demos | 用真机数据补 gap | 没 simulation pretraining 时易 overfit，unseen objects 差 |

### 1.4 Delta 分析

本文相对前作的 delta：

1. **物体 delta**：从 cube/ball/short object 转到 pen-like long object。
2. **任务 delta**：从相对稳定的 rotation/reorientation 转到无支撑动态平衡 + finger gaiting。
3. **训练 delta**：不是直接 distill oracle，而是 oracle rollout → simulation pretraining → real open-loop replay → fine-tune。
4. **数据 delta**：真机数据不是 teleoperation 来的，而是仿真轨迹在真机上的成功 replay 自动筛出来。
5. **评估 delta**：在 3 个训练物体 + 7 个未见物体上报告 RR/Suc，而不是只展示视频。

一句话：

> Spin Pens 的 value add 是把“仿真不能直接迁移”的失败，转化成“仿真仍能产生候选动作序列，真机负责筛选和微调”的数据生成范式。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_t$ | $\mathbb{R}^{16}$ | Allegro joint positions | policy input | 当前关节位置 | oracle stack 3 historical states；student uses 30-step history |
| $a_{t-1}$ | $\mathbb{R}^{16}$ | previous joint target | policy input | 上一步 PD target | action 是 target position，不是 torque |
| $c_t$ | binary tactile signals | oracle simulation input | oracle input | 20 tactile sensors, 5 per fingertip | final deployable student 不用 tactile |
| $p_t$ | $\mathbb{R}^{4\times3}$ | fingertip positions | oracle input | 4 个指尖 xyz | FK/hand frame dependent |
| $w_t$ | pose/angular velocity | simulator privileged | oracle input | pen current pose and angular velocity | real deployment 不可用 |
| PointCloud | $\mathbb{R}^{100\times3}$ | mesh + ground-truth pose | PointNet input | pen shape/current geometry | real student 不用 point cloud |
| physical properties | mass, CoM, friction, size | simulator parameters | oracle input | object-specific dynamics | real world 不可直接测 |
| $f(o_t)$ | policy output | oracle/student network | learned | relative joint target command | low-level PD converts to torque |
| $a_t$ | $\mathbb{R}^{16}$ | scaled/integrated command | control target | joint position target | paper writes $a_t=\eta f(o_t)+a_{t-1}$ |
| $r_z$ | scalar penalty | reward | no gradient to state | pen high-low point height difference penalty | $z$ is world vertical, not pen axis |
| RR | radians over z-axis | real metric | eval | real rotation amount | not “success”; success uses threshold |
| Suc. | percentage | real metric | eval | rotate at least 180 degrees | roughly one finger-gaiting circle |

### 2.2 从接触动力学推导：为什么 pen spinning 必须 finger gaiting

把笔近似成细长刚体，绕目标 z-axis 转动。角动量：

$$
L_z = I_z\omega_z.
$$

指尖 $i$ 在接触点 $r_i$ 施加接触力 $f_i$，对 z-axis 的力矩是：

$$
\tau_z = \sum_i (r_i\times f_i)\cdot \hat z.
$$

持续旋转需要长期有正的平均力矩：

$$
\frac{d}{dt}(I_z\omega_z)=\tau_z-\tau_{\text{loss}}.
$$

但每个接触力受 Coulomb friction cone 限制：

$$
f_{i,n}\ge 0,\qquad \|f_{i,t}\|\le \mu f_{i,n}.
$$

并且单根手指的工作空间有限：一根手指推过一段角度后就必须复位。于是持续旋转只能靠 contact mode switching：

$$
\sigma(t)\subseteq\{\text{thumb,index,middle,ring}\},
\qquad
\dot x=f_{\sigma(t)}(x,u).
$$

这就是 finger gaiting：一部分手指供矩，另一部分手指脱离并复位，再重新接触。它不是视觉上像人手的动作，而是由“单指不能无限供矩 + 接触只能推不能拉 + 工作空间有限”推出的必然结构。

### 2.3 为什么 canonical grasp 是探索先验

如果初始状态只在一个 stable grasp 附近采样，PPO 会学到局部动作：保持接触、轻微转动，但无法探索完整接触模式周期。论文 Figure 4/5 证实 Single Canonical Pose training 不稳定，finger gaiting 不涌现。

因此作者设计了 6 个 canonical hand poses，覆盖人类转笔周期中可能出现的关键 grasp patterns，再加噪声生成 stable initial states。

理论解释：

> canonical grasp 不是数据增强，而是把探索分布放到接触模式切换流形附近，让 PPO 能从多个 gait phase 开始学习，而不是从一个 phase 慢慢撞到下一个 phase。

### 2.4 为什么 $r_z$ 是 sim-to-real reward，不只是姿态美观

论文新增：

$$
r_z = \text{pen high-low point height-difference penalty}.
$$

它鼓励笔在旋转时保持近似水平。物理原因是，若笔倾斜角为 $\theta$，重力矩近似：

$$
\tau_g \approx mgl\sin\theta.
$$

倾斜越大，手指需要提供的补偿越大；一旦所需切向力超过摩擦锥：

$$
\|f_t\|>\mu f_n,
$$

笔就会滑落。仿真中 policy 可能利用精确 contact 维持某些倾斜构型，但真机摩擦/接触误差会让这些构型不可迁移。

所以 $r_z$ 的真正作用是：

> 把仿真里“看起来会转但真机危险”的解从策略空间中剔除。

Figure 5(b) 的 without z-reward 可视化正好支持这一点：轨迹表面相似，但某些构型 pen tilted，real replay unstable。

### 2.5 Oracle policy：特权观测不是部署方案，而是轨迹生成器

oracle observation 包含：

- joint positions $q_t$；
- previous joint target $a_{t-1}$；
- binary tactile $c_t$；
- fingertip positions $p_t$；
- pen pose and angular velocity $w_t$；
- pen point cloud $\mathbb{R}^{100\times3}$ via mesh + ground-truth pose；
- physical properties: mass, CoM, friction, object size。

policy action:

$$
a_t=\eta f(o_t)+a_{t-1}.
$$

它输出 relative target position，经 low-level PD 变成 torque。

关键判断：

> oracle 的目的不是部署，而是解决“高质量转笔轨迹从哪里来”的问题。

teleoperation 给不了，direct sensorimotor RL 学不动，因此先用 privileged simulation RL 把 skill 挖出来。

### 2.6 Sensorimotor pretraining：为什么不用 DAgger rollout student

传统做法可能是 oracle → DAgger → student。但论文发现：

- visuotactile student 在仿真可学到 reasonable behavior，但 real image/touch distribution gap 太大；
- proprioception-only 最可靠，但在仿真中 direct DAgger/proprio policy 不收敛，前几步就掉物体。

因此他们改为：

$$
\text{roll out oracle in simulation}
\to
\{(s_t,a_t)\}
\to
\text{BC pretrain proprioceptive student}.
$$

student 输入：

$$
q_{t-29:t},\quad a_{t-30:t-1}
$$

共 30 steps history，用 temporal transformer + MLP。

这一步不期待 zero-shot real transfer。它只是让 student 获得 motion prior：知道 finger gaiting 大致长什么样、遇到 diverse simulation states 该怎么响应。

### 2.7 Open-loop replay：把可迁移性变成真实数据筛选

流程：

1. oracle policy 在 simulation 中用不同 initial poses rollout；
2. 选 15 条在 simulation 中持续超过 800 timesteps 的 trajectories；
3. 记录 action sequences；
4. 在真实机器人上对 3 个 training objects open-loop replay；
5. 每次随机选一条 trajectory；
6. 若真实物体旋转超过 $2\pi$，存入 dataset；
7. 每个 training object 收 15 条成功轨迹，共 45 条。

这一步非常关键，因为它把“sim trajectory 是否可迁移”从理论问题变成真机测量：

$$
\text{trajectory transferable?}
\quad\Leftrightarrow\quad
\text{open-loop replay rotates } >2\pi.
$$

成功轨迹包含真实动力学下的 proprioception/action 对，最终用于 fine-tune student。

### 2.8 训练与控制细节

| 项目 | 设置 |
|---|---|
| Hardware | Allegro Hand, 4 fingers, 16 DoF |
| Network command | joint position target at 20 Hz |
| Low-level PD | 333 Hz |
| Simulator | Isaac Gym |
| Sim control frequency | 20 Hz |
| Sim frequency | 200 Hz |
| Oracle PPO envs | 8192 |
| PPO steps/env | 12 |
| PPO total agent steps | 500M |
| PPO LR | $5\times10^{-3}$ |
| PPO clip | 0.2 |
| PPO $\gamma,\lambda$ | 0.99, 0.95 |
| Student BC envs | 48 |
| Student steps | 512 |
| Student epochs | 2000 |
| Student LR | $10^{-3}$ |

Domain randomization:

| Parameter | Range |
|---|---|
| Object Scale | $\times[0.95,1.05]$ |
| Mass | $[0.01,0.03]$ kg |
| Center of Mass | $[-0.1,0.1]$ cm |
| Friction, object/fingertip | $[0.3,3.0]$ |
| External Disturbance | $(0.2,0.25)$ |
| PD Stiffness | $[2.5,3.5]$ |
| PD Damping | $[0.09,0.11]$ |
| Observation Noise | $\mathcal{N}(0,0.02)$ rad |
| Action Noise | $\mathcal{N}(0,0.01)$ rad |

Real objects A-J:

| Object | Mass | Length | Contact Part Diameter |
|---|---:|---:|---:|
| A | 16.7 g | 22.21 cm | 34.66 mm |
| B | 10.8 g | 14.41 cm | 27.34 mm |
| C | 21.4 g | 17.43 cm | 34.73 mm |
| D | 29.6 g | 18.30 cm | 35.50 mm |
| E | 32.4 g | 19.12 cm | 29.73 mm |
| F | 36.3 g | 19.00 cm | 31.17 mm |
| G | 22.3 g | 20.09 cm | 36.88 mm |
| H | 21.5 g | 14.89 cm | 31.81 mm |
| I | 26.0 g | 15.00 cm | 37.93 mm |
| J | 49.7 g | 15.75 cm | 35.80 mm |

## 3. 训练、数据与实验

### 3.1 评价设置

真实世界指标：

- **RR**：radians of rotation over z-axis；
- **Suc.**：能否至少转 180 degrees，对应通常完成一圈 finger gaiting 中每个手指 break/re-establish contact。

数据划分：

- Training objects: A/B/C，用于收集 real trajectories，也用于 evaluation；
- Unseen objects: D/E/F/G/H/I/J，只用于 evaluation。

### 3.2 Table 1：不同 deployable systems 的真实结果

| Method | A RR/Suc | B RR/Suc | C RR/Suc | D RR/Suc | E RR/Suc | F RR/Suc | G RR/Suc | H RR/Suc | I RR/Suc | J RR/Suc |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Replay | 2.80 / 37.62 | 3.37 / 54.29 | 2.65 / 29.52 | 3.83 / 78.21 | 3.44 / 67.09 | 2.47 / 51.49 | 2.93 / 44.35 | 3.53 / 41.51 | 2.65 / 30.99 | 2.56 / 34.38 |
| V. Distill | 1.85 / 17.65 | 1.57 / 0.00 | 1.70 / 8.33 | 1.57 / 0.00 | 1.57 / 0.00 | 1.57 / 0.00 | 1.57 / 0.00 | 1.57 / 0.00 | 1.57 / 0.00 | 1.57 / 0.00 |
| Ours | 3.43 / 54.93 | 3.38 / 70.00 | 3.62 / 57.55 | 4.10 / 80.65 | 3.50 / 68.18 | 2.71 / 53.33 | 4.47 / 78.02 | 4.63 / 75.79 | 3.64 / 46.60 | 3.49 / 60.47 |

P. Distill is reported as N.A. because proprioceptive distillation fails to converge even in simulation.

因果解释：

- Replay 已经不错：说明 oracle trajectories 被 $r_z$ 和 canonical initialization 塑造成了真实可 replay 的动作序列。
- Replay 仍低于 Ours：说明 open-loop 缺少反馈纠偏；fine-tuned student 利用 real proprioception/action data 补上了闭环适应。
- V. Distill 多数固定在 1.57/0：论文解释为固定失败模式，thumb/index 能转约 90 degrees 后掉落。
- P. Distill N.A.：纯本体直接蒸馏在仿真都不收敛，证明 pretraining/fine-tuning pipeline 不是多余工程。

### 3.3 Random stable grasp evaluation

Table 1 的设置让 initial configuration 来自 replay trajectory dataset，对 Replay baseline 有利。论文又做 random stable grasp：

- 10 random grasps；
- 每个 grasp 5 trials；
- 每个 random grasp 在 simulation 里跑 oracle，从 1000 simulated environments 中选 best trajectory 给 replay。

结果：

| Object | Replay → Ours success improvement |
|---|---:|
| D | 54% → 78.0%, +22.0% |
| E | 46% → 82%, +36% |
| F | 34% → 74%, +40% |

这说明 Ours 的优势不是初始状态偏置造成的；simulation pretraining 让 student 见过更多 diverse data，因此 random grasp 下掉得没有 replay baseline 多。

### 3.4 Table 2：pretraining 和 fine-tuning 缺一不可

| Method | A RR/Suc | B RR/Suc | C RR/Suc | D RR/Suc | E RR/Suc | F RR/Suc |
|---|---:|---:|---:|---:|---:|---:|
| Only Pretrain | 1.89 / 15.15 | 2.44 / 44.87 | 1.70 / 8.11 | 1.74 / 6.86 | 2.13 / 29.35 | 1.98 / 21.05 |
| No Pretrain | 2.62 / 53.66 | 2.34 / 36.84 | 2.29 / 30.00 | 1.92 / 16.53 | 1.88 / 19.61 | 1.90 / 16.42 |
| Ours | 3.43 / 54.93 | 3.38 / 70.00 | 3.62 / 57.55 | 4.10 / 80.65 | 3.50 / 68.18 | 2.71 / 53.33 |

核心因果链：

`Only Pretrain` 失败，因为 sim-to-real physics gap 大；

`No Pretrain` 在 training objects 上有一定效果，但 unseen objects 很差，因为 45 条 real trajectories 不足以覆盖多物体分布；

`Ours` 同时有 simulation diversity 和 real dynamics correction，所以 training/unseen 都更强。

### 3.5 Table 3：更多 real demos 不能替代 simulation pretraining

| Method | #Demo | A Suc | B Suc | C Suc | D Suc | E Suc | F Suc |
|---|---:|---:|---:|---:|---:|---:|---:|
| No Pretrain | 15 | 14.29 | 15.79 | 0.00 | 11.11 | 13.04 | 0.00 |
| No Pretrain | 45 | 53.66 | 36.84 | 30.00 | 16.53 | 19.61 | 16.42 |
| No Pretrain | 75 | 76.67 | 40.00 | 43.33 | 26.67 | 23.33 | 15.00 |
| Ours | 45 | 54.93 | 70.00 | 57.55 | 80.65 | 68.18 | 53.33 |

因果解释：

- No Pretrain 从 15→75 demos 会提升 training objects；
- 但 unseen D/E/F 仍远低于 Ours 45 demos；
- 这说明 simulation pretraining 带来的 diversity 不是简单增加 real demos 可以替代的，至少在这一级别 demo 数下不行。

### 3.6 Oracle training ablations

论文用 Figure 4 / 5 回答三个问题：

| 变化 | 观察 | 因果解释 |
|---|---|---|
| Single Canonical Pose | reward 曲线可上升，但 finger gaiting 不涌现 | 单一初始相位覆盖不到完整接触模式周期 |
| No tactile / no point cloud / no privileged object info | oracle policy performance 不够，甚至不收敛 | pen spinning 需要接触、形状和物理信息帮助 simulation exploration |
| No $r_z$ | simulation 中看似能转，但 pen 会在某些构型倾斜 | 真机 replay unstable，无法作为 data engine |

这组 ablation 支撑的是：

> oracle policy 的目标不是“仿真最高 reward”，而是“产生真实可 replay 的 high-quality trajectories”。

### 3.7 实验边界

- quantitative evaluation 是 10 个 real objects，更多 qualitative videos 在 project website；
- final policy 只做 z-axis spinning；
- stable grasp 是前提；
- final deployment policy 是 proprioceptive，vision/touch 主要用于 oracle training / ablation；
- real data collection 需要 replay 试错，45 条是成功轨迹数，不等于无成本。

## 4. 核心洞见

### 4.1 真正的 insight：simulation 是 skill discovery，不是 final policy

这篇最有价值的转向是：

> 对 dynamic contact-rich tasks，simulation policy 不一定能直接迁移，但 simulation 仍然可以生成真实世界很难获得的 skill trajectories。

它把 simulation 的角色从 “train deployable policy” 改成 “discover feasible motion + provide action-labeled demonstrations”。这对转笔尤其关键，因为人类 teleoperation 受 latency 和 retargeting error 限制，难以直接采集高质量示教。

### 4.2 为什么 open-loop replay 会有用

open-loop replay 有用需要三个条件：

1. oracle trajectory 被 $r_z$ / energy penalties 塑造成 smooth and realistic；
2. in-hand contact system 对某些动作序列有自然的局部吸引/容错；
3. replay 成功阈值筛掉了 gap 过大的 trajectories。

所以 open-loop replay 不是“开环控制万能”，而是一个 real-world filter：

$$
\text{sim trajectory pool}
\xrightarrow{\text{real replay}}
\text{transferable trajectory subset}.
$$

### 4.3 为什么 final student 仍优于 replay

Replay 只执行动作序列，不看当前真实状态。Fine-tuned student 则从真实 proprioception history 中学习：

- 真实 actuator delay/friction；
- 真实接触导致的 joint response；
- 某些初始偏差下如何微调动作。

因此 Ours 通常有更高 RR/Suc。Table 1 的 D/G/H 等 unseen objects 上 especially obvious。

### 4.4 什么时候会失效

- open-loop replay 成功率太低，收不到 real trajectories；
- real-world object 超出 simulation trajectory 的 contact regime；
- 稳定初始抓取无法获得；
- 任务需要实时外部扰动恢复，而 open-loop data 不覆盖；
- 多轴/翻转超出 z-axis reward 和 canonical grasps。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 根因 | 影响 |
|---|---|---|
| open-loop replay 无成功率下界 | sim-real gap 没有被形式化 | 45 条成功轨迹不是可保证数字 |
| $r_z$ 是 hand-designed constraint | 根据物理直觉写出 | 其他技能需要重新找“仿真可行但真机危险”的约束 |
| final policy 只用 proprioception | 最稳定但观测有限 | 不知道真实 pen pose/contact phase |
| only z-axis | reward/initial states 都围绕 z-axis | 不能直接得到 arbitrary pen trick |
| stable grasp assumption | 初始状态已放好 | 没解决 grasp-to-spin 的完整任务 |

### 5.2 算法维度

| 替代路线 | 可能优势 | 相对本文的问题 |
|---|---|---|
| zero-shot DR | 不需要真机数据 | dynamic contact gap 太大，论文明确否定 |
| direct visuotactile distillation | 可观测 pen pose/contact | real distribution gap 大，V. Distill 失败 |
| proprio-only DAgger | 部署传感稳定 | 仿真里都不收敛，P. Distill N.A. |
| pure real imitation | 不依赖仿真 | teleoperation 难、75 demos 仍不如 Ours 45 |
| world-model planning | 可筛 trajectory | 需要足够可信的 contact model，否则会重演 sim gap |

### 5.3 工程/实验维度

- 需要手工 canonical grasps。
- 需要真实 replay 尝试来筛成功轨迹。
- 没有自动说明如何检测所有失败模式。
- 物体是 pen-like objects，不是任意工具。
- hardware 是 Allegro；LinkerHand 的 actuator latency、stiffness、tactile layout 需要重标定。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / DNPM 的直接迁移

这篇对用户项目的直接模板：

| Spin Pens 设计 | LinkerHand / DNPM 迁移 |
|---|---|
| Oracle with privileged pen pose/point cloud/physics/tactile | Isaac/MuJoCo 中给 PPO Oracle privileged pen state、contact、mass/CoM/friction |
| Six canonical grasps | Thumbaround/charge/sonic 等技能相位的 canonical initial states |
| $r_z$ horizontal penalty | 对 pen axis plane、tilt、slip 的真机稳定性约束 |
| Open-loop replay | 用仿真 oracle action sequences 在 LinkerHand 真机筛成功数据 |
| 45 successful trajectories | 作为第一轮 real fine-tune target，而不是从零 RL |
| Proprioceptive temporal student | 部署用 $q,\dot q,a$ history + optional tactile contact tokens |

### 6.2 WMTS 结合点

WMTS 可以比原论文更进一步：

| WMTS 模块 | 如何接入 Spin Pens |
|---|---|
| latent task generation | 生成 canonical grasp / skill phase / replay candidate class |
| PPO Oracle | 学 privileged pen-spinning specialists |
| Diffusion/Flow generalist | 对成功 replay + sim rollout 做 action-sequence modeling |
| Ensemble World Model | 在真机 replay 前预测哪些 sim trajectories 更可能 transfer |
| real-robot fine-tuning | 继承 open-loop replay 数据引擎，减少人工筛选 |

关键建议：

> 第一版不要追求 zero-shot world-model transfer。先复刻“oracle trajectory pool → real replay filter → fine-tune deployable policy”，再用 ensemble world model 提高 replay filter 的样本效率。

### 6.3 可验证实验建议

| 实验 | Baseline | 指标 | 证伪点 |
|---|---|---|---|
| canonical phase 是否必要 | single grasp vs multi canonical grasps | sim gait emergence, open-loop success | 若 single grasp 也能学 gaiting，则 phase coverage 不是瓶颈 |
| $r_z$ / tilt penalty 是否必要 | no tilt penalty vs with tilt penalty | real replay success, drop mode | 若 no penalty 同样可 replay，则 tilt/friction mechanism 不成立 |
| tactile 是否该进入 student | proprio-only vs proprio+tactile student | unseen pens Suc/RR | tactile 不提升则继续 pure proprio |
| world model prefilter | random sim replay vs ensemble-ranked replay | real trials per success trajectory | 若无提升，WM uncertainty 没抓住 transfer gap |
| real data scaling | 15/45/75 trajectories with and without sim pretrain | unseen success | 复验 Table 3 是否在 LinkerHand 上成立 |

### 6.4 不应过度外推的点

- “<50 trajectories” 是在 strong simulation prior + pen-like object + stable grasp 下成立。
- 论文没有解决 grasp acquisition。
- 论文没有解决 multi-axis pen trick。
- open-loop replay 会消耗真机试错，不是纯离线。
- 视觉/触觉不是没用，论文只是说当前动态任务中它们的 sim-to-real bottleneck 尚未解决。

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

Pen spinning 是 hybrid contact dynamics：

$$
\dot x=f_{\sigma(t)}(x,u),
\qquad
\sigma(t)\in 2^{\{\text{fingers}\}}.
$$

finger gaiting 就是对 $\sigma(t)$ 的周期性控制。canonical grasps 是对这个周期的初始相位覆盖。

### 7.2 与 [[ContactMechanics]] 的联系

$r_z$ 的物理根是倾斜导致重力矩：

$$
\tau_g\approx mgl\sin\theta,
$$

以及摩擦锥：

$$
\|f_t\|\le \mu f_n.
$$

当倾斜太大，真机接触误差会让所需补偿超过摩擦锥，因此“仿真能转”不等于“真机可 replay”。

### 7.3 与 [[ReinforcementLearning]] 的联系

PPO oracle 用 privileged state 做 skill discovery；student 用 BC/fine-tuning 做 deployable policy。这里 simulation pretraining 的角色和 ACT/IL 很像，但数据源不是人类，而是 oracle policy。

### 7.4 与 [[ControlTheory]] 的联系

动作是 20 Hz joint-position targets，经 333 Hz PD controller 执行。真实部署时需要调 P/D gain，使空手 finger gaiting trajectory 的 sim-real joint tracking error 尽量小，并加入 action noise 提升 actuator robustness。

### 7.5 in-hand rotation 领域坐标

| Paper | Object/support | Axis | Deployment sensing | Sim-to-real route |
|---|---|---|---|---|
| HORA | diverse objects, fingertip support | z-axis | proprioception | RMA adaptation |
| RotateIt | diverse objects | x/y/z | vision + touch + proprio | privileged distillation |
| Robot Synesthesia | object(s), point-cloud geometry | z / multi benchmark | vision + tactile point cloud | teacher-student |
| AnyRotate | diverse objects | arbitrary axis | tactile + proprio | touch sim-to-real |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | diverse, multi-wrist | multi-axis | proprioception | joint-wise neural dynamics + residual |
| **Spin Pens** | pen-like, no natural support | z-axis | proprioception | oracle replay + real fine-tune |

领域空白：

> 无支撑 pen-like object + multi-axis / trick-level rotation + low-latency tactile/proprio deployment。

这正是 DNPM/WMTS 可以切入的位置。

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “这篇真正新在哪里？” | 不是 backbone，而是 oracle trajectory → open-loop replay → real fine-tune 的数据路线 |
| “为什么不用 DAgger 直接蒸馏？” | visuotactile sim-real gap 大；proprio-only student 仿真不收敛 |
| “$r_z$ 为什么重要？” | 它排除仿真可行但真机倾斜滑落的解 |
| “45 条真机轨迹怎么来的？” | 每个训练物体 15 条，来自 open-loop replay 超过 $2\pi$ 的成功轨迹 |
| “Ours 比 Replay 强在哪？” | replay 无反馈，fine-tuned student 用 real proprioception 闭环纠偏 |
| “对 LinkerHand 应先做什么？” | 先建 privileged PPO oracle + canonical phase 初始分布 + real replay filter |
| “最大风险是什么？” | open-loop replay 成功率过低，收不到可 fine-tune 数据 |

## References

- Jun Wang, Ying Yuan, Haichuan Che, Haozhi Qi, Yi Ma, Jitendra Malik, Xiaolong Wang. *Lessons from Learning to Spin "Pens"*. CoRL 2024.
- Haozhi Qi et al. *In-Hand Object Rotation via Rapid Motor Adaptation*. CoRL 2022.
- Nakatani and Yamakawa. *Dynamic manipulation like normal-type pen spinning by a multifingered hand*. 2006.
