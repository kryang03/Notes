---
tags:
  - paper
  - dexterous-manipulation
  - in-hand-manipulation
  - sim-to-real
  - reinforcement-learning
  - rapid-adaptation
aliases:
  - HORA
  - Rapid Motor Adaptation
paper-year: 2022
read-date: 2026-02-01
venue: CoRL 2022
paper-pdf: "[[Papers/In-Hand Object Rotation via Rapid Motor Adaptation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[RepresentationLearning]]"
---

# In-Hand Object Rotation via Rapid Motor Adaptation (HORA)

> [!abstract] 核心贡献
> HORA 把 legged RMA 的“隐式在线系统辨识”迁移到 dexterous in-hand rotation：先在仿真中把 9 维物体属性 $e_t$ 编码成 8 维 task-relevant extrinsics $z_t=\mu(e_t)$，训练条件策略 $\pi(o_t,z_t)$；再训练 adaptation module $\phi$ 从 proprioception/action history 估计 $\hat z_t$，使真实 AllegroHand 在无视觉、无触觉、无真机微调的情况下，仅靠本体感觉旋转 30+ 个未见物体。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — context-conditioned PPO：策略不是学一个平均动作，而是学 $\pi(a_t\mid o_t,z_t)$ 这族按物体 context 切换的子策略。
> - [[RepresentationLearning]] — learned extrinsics：$z_t$ 不是真实物理量，而是由任务监督塑造出的低维充分统计量。
> - [[Dynamics]] — hidden object parameters：mass、friction、CoM、scale 通过接触动力学影响 proprioception/action history。
> - [[ControlTheory]] — adaptive control / system identification：$\phi$ 是摊还式在线辨识器，但没有 classical adaptive control 的可辨识性/稳定性保证。
>
> **核心技术**: Rapid Motor Adaptation, learned extrinsics, proprioception-only adaptation, PPO, teacher/adaptation two-stage training

## 0. 阅读定位与范本价值

HORA 是 in-hand rotation 这一簇的逻辑原点。后面的 RotateIt、Robot Synesthesia、Touch Dexterity、AnyRotate 都可以被读成对 HORA 的补洞：

| 后续论文 | 补 HORA 的哪个洞 |
|---|---|
| [[RotateIt - General In-Hand Object Rotation with Vision and Touch]] | HORA 只靠 proprioception、主要 z-axis；RotateIt 加 vision/touch/shape 做多轴 |
| [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] | HORA 不知道接触点；Robot Synesthesia 把触觉投成 3D contact geometry |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | HORA 无触觉；Touch Dexterity 证明 sparse contact 可显著改进 blind rotation |
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | HORA 主要 z-axis；AnyRotate 走任意轴 + dense tactile |

它最值得保留的核心判断是：

> Domain randomization 让策略“不要崩”，online adaptation 让策略“对当前物体更接近最优”。

这个判断对 WMTS 很重要。一个 world model / policy 如果只在随机化分布上学一个 average behavior，它会稳但慢；如果能在线估计当前 context，就能在保持鲁棒的同时更积极地利用物体属性。

最低标准：

| 支柱 | 本文必须讲清的问题 | 本 recap 的位置 |
|---|---|---|
| 逻辑与价值 | HORA 相对纯 DR / SysID /视觉方法的 value add 是什么？ | §1, §4 |
| 原理与理论 | $e_t\to z_t\to\hat z_t$ 为什么是 POMDP 下的摊还辨识？ | §2 |
| 实验与验证 | Table 1 / Fig.3 / Fig.4 / appendix ablation 如何证明“adaptation beats robust average”？ | §3 |
| 未来与结合 | 对转笔/LinkerHand/WMTS 哪些能迁移，哪些因接触点不可观测会失败？ | §5-§6 |

## 1. 问题设定与动机

### 1.1 一句话核心

HORA 要做的是：

> 仅用 Allegro Hand 的 joint positions 和 previous actions，在没有视觉、没有 tactile array、没有真实在线学习的情况下，把多种真实物体用 fingertips 绕 hand/world z-axis 持续旋转。

任务设置有三个关键信息：

- 训练只用 simulation 中的 cylindrical objects；
- 部署到真实世界时不做 fine-tuning；
- 真实物体直径约 4.5-7.5 cm、质量 5g-200g，包括 porous / non-rigid / irregular objects。

所以它的故事不是“仿真里学会旋转圆柱”，而是：

> 能否把圆柱随机化中学到的交互响应，压缩成一个可从本体历史估计的 object context，从而迁移到看起来完全不同、但触觉/动力学上相似的真实物体。

### 1.2 直观隐喻

HORA 像闭眼捏着一个物体转：你不知道它的外观，也没有接触传感器告诉你具体接触点，但你能从“我刚才怎么动手指，它怎么反馈”推断它重不重、大不大、滑不滑。

这个隐喻的可证伪点是：如果任务需要知道精确 contact patch 或 object pose，而这些不能从 proprioception/action history 推断，HORA 就会失败。论文自己的 failure analysis 正是：多数失败来自 incorrect contact points，因为纯本体 policy 不知道物体和指尖的精确接触位置。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| 外部视觉 / object tracking | 直接观测 object pose | 遮挡、光照、标定、部署复杂；不能直接测 mass/friction |
| 纯 domain randomization | 学一个覆盖随机分布的 robust policy | 稳但慢；对当前物体无法最优，DR baseline 真实表里保守 |
| 显式 SysID | 估计真实物理参数 $e_t$ | 参数精确估计困难且不必要；Table 1 / real results 都低于 learned extrinsics |
| action replay / periodic gait | 复用 expert trajectory | 只能在极窄初始/物体条件下工作，无法适应对象变化 |
| direct high-history policy | 把长历史直接喂给 PPO | appendix Table 4 显示 MLP/LSTM 长历史 DR 优化困难 |
| 触觉/视觉多模态 | 可获得更直接 object/contact 信息 | 传感器成本和 sim-real gap 更高；HORA 选择最小感知路径 |

### 1.4 Delta 分析

HORA 的 delta 不是“用了一个 adaptation module”这么简单，而是三步：

1. **学 task-relevant extrinsics**：不把真实物理参数直接给 policy，而是学 $z_t=\mu(e_t)\in\mathbb{R}^8$。
2. **学 context-conditioned policy**：policy 变成 $\pi(o_t,z_t)$，不是一个平均策略。
3. **部署时在线估计 context**：$\hat z_t=\phi(q_{t-k:t},a_{t-k-1:t-1})$，用 proprioception/action discrepancy 做摊还辨识。

这个 design 的 insight 是：

> 对一个具体任务来说，“真实物理参数”未必是最好的 adaptation target；更好的 target 是能让 policy 选对动作的低维 task-sufficient latent。

SysID baseline 低于 HORA，正好证明这一点。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_t$ | $\mathbb{R}^{16}$ | Allegro joint positions | policy input | 当前手姿态 | actor 不看 object pose |
| $a_{t-1}$ | $\mathbb{R}^{16}$ | previous policy command | policy input | 上一步 PD target | action 是 position target，不是 torque |
| $o_t$ | $\mathbb{R}^{96}$ | computed history | policy input | $(q_{t-2:t},a_{t-3:t-1})$ | 3 帧 joint + 3 帧 action，提供 velocity/acceleration clues |
| $e_t$ | $\mathbb{R}^9$ | simulator privileged object properties | encoder input | position, size/scale, mass, friction, CoM 等 | 真实部署不可观测 |
| $\mu$ | MLP $[256,128,8]$ | learned encoder | Stage 1 learned | $e_t\to z_t$ | 和 policy jointly optimized，不是独立物理编码 |
| $z_t$ | $\mathbb{R}^8$ | $z_t=\mu(e_t)$ | Stage 1 policy input / Stage 2 label | task-relevant extrinsics | 不是 exact physical parameters |
| $\hat z_t$ | $\mathbb{R}^8$ | adaptation module output | Stage 2 learned / deployment input | estimated extrinsics | 部署时替代 $z_t$ |
| $\phi$ | MLP pair encoder + 1D conv | adaptation module | supervised learned | history → extrinsics | 最终用 30-step history |
| $k$ / $\hat{k}$ | unit z-axis | reward definition | fixed | desired rotation axis | 本文主任务只用 z-axis |
| $\omega$ | object angular velocity | simulation privileged | reward/eval | rotation speed | real world 难准确测，改用 net rotations |
| $\tau$ | commanded torque | PD controller | penalty/eval | energy/effort | 由 20 Hz position target 经 300 Hz PD 产生 |
| $v$ | object linear velocity | simulation privileged | reward/eval | object stability | real world 不直接测 |
| TTF | normalized duration | eval | metric | time-to-fall | sim max 20s, real max 30s |

### 2.2 Hidden-context MDP：为什么需要 extrinsics

设物体属性为 hidden context：

$$
e=(\text{mass},\text{scale},\text{friction},\text{CoM},\ldots).
$$

如果 $e$ 已知，transition 可以写成：

$$
s_{t+1}\sim P_e(s_{t+1}\mid s_t,a_t).
$$

最优策略是 context-conditioned：

$$
\pi^*(a_t\mid o_t,e).
$$

但真实部署时 $e$ 不可观测，只能看到 history：

$$
h_t=(q_{1:t},a_{1:t-1}).
$$

这就是 POMDP / hidden-parameter MDP。原则上应维护 belief：

$$
b_t(e)=p(e\mid h_t).
$$

HORA 不显式做贝叶斯滤波，而是假设存在一个低维任务充分统计量：

$$
z=\mu(e)\in\mathbb{R}^8
$$

使得：

$$
\pi^*(a_t\mid o_t,e)\approx \pi_\theta(a_t\mid o_t,z).
$$

这句话是理解 HORA 的理论核心：$z$ 不是“真实物理参数”，而是“对 z-axis fingertip rotation 这个任务足够的 context code”。

### 2.3 为什么 learned $z$ 比 exact SysID 更合理

显式 SysID 试图估计：

$$
\hat e_t\approx e_t.
$$

HORA 估计：

$$
\hat z_t\approx z_t=\mu(e_t).
$$

两者差异很大：

- exact $e_t$ 包含对控制不重要的细节；
- 不同 $e_t$ 可能对当前任务产生相同最优动作；
- 有些参数组合不可辨识，例如 mass/friction 可能在短期 proprio history 中产生相似响应；
- learned $z$ 可以把“对动作等价”的物体压到一起。

这解释了为什么 SysID baseline 在 Table 1 和真实实验中都不如 HORA。HORA 学的是 task-equivalence class，而不是物理实验室里的参数表。

### 2.4 Stage 1：Base policy learning

privileged vector：

$$
e_t\in\mathbb{R}^{9}.
$$

extrinsics encoder：

$$
z_t=\mu(e_t)\in\mathbb{R}^{8}.
$$

base policy：

$$
a_t=\pi(o_t,z_t),
\qquad
o_t=(q_{t-2:t},a_{t-3:t-1})\in\mathbb{R}^{96}.
$$

policy output：

$$
a_t\in\mathbb{R}^{16}
$$

是 PD controller target，不是 torque。硬件/仿真执行：

- position command at 20 Hz；
- PD controller at 300 Hz；
- $K_p=3.0,\ K_d=0.1$。

Stage 1 用 PPO joint optimize policy $\pi$ 和 encoder $\mu$。这意味着 $\mu$ 不是预定义物理编码器，而是被 PPO reward 反向塑造出的 control-useful representation。

### 2.5 Reward：为什么不是“越快转越好”

reward：

$$
r=
r_{\text{rot}}
\lambda_{\text{pose}}r_{\text{pose}}
\lambda_{\text{linvel}}r_{\text{linvel}}
\lambda_{\text{work}}r_{\text{work}}
\lambda_{\text{torque}}r_{\text{torque}}.
$$

各项：

$$
r_{\text{rot}}=
\max(\min(\omega\cdot\hat{k},r_{\max}),r_{\min}),
\quad
r_{\max}=0.5,\ r_{\min}=-0.5,
$$

$$
r_{\text{pose}}=-\|q-q_{\text{init}}\|_2^2,
\qquad
r_{\text{torque}}=-\|\tau\|_2^2,
$$

$$
r_{\text{work}}=-\tau^\top \dot q,
\qquad
r_{\text{linvel}}=-\|v\|_2^2.
$$

appendix 给出权重：

$$
\lambda_{\text{pose}}=-0.3,\quad
\lambda_{\text{torque}}=-0.1,\quad
\lambda_{\text{work}}=-2.0,\quad
\lambda_{\text{linvel}}=-0.3.
$$

论文文字的语义是：pose、torque、work、linear velocity 都作为 penalty/regularizer，避免策略为了旋转速度把物体甩飞或用过大 torque 过拟合仿真。

两个关键设计：

- rotation reward 被 clipping，否则 policy 会只追求快转而破坏稳定；
- 没有显式 fingertip contact heuristic，stable finger gait 从 pose/energy/stability constraint 中涌现。

### 2.6 Stage 2：Adaptation module as amortized inference

部署时没有 $e_t$，也没有 $z_t$。adaptation module 估计：

$$
\hat z_t=\phi(q_{t-k:t},a_{t-k-1:t-1}).
$$

训练过程不是一次性 offline regression，而是迭代：

1. 用当前 $\phi$ 预测 $\hat z_t$；
2. rollout policy：

$$
a_t=\pi(o_t,\hat z_t);
$$

3. 同时存 ground-truth $z_t$；
4. 用 Adam 最小化：

$$
\mathcal{L}_\phi=\|\hat z_t-z_t\|_2^2.
$$

最终 history length：

$$
T=30\ \text{steps}=1.5\text{ s at 20 Hz}.
$$

architecture：

- 每个 timestep 的 $(q,a)$ pair 先经 two-layer MLP $[32,32]$ 编成 32-d；
- 时间维上用三层 1D conv：
  - $[32,32,9,2]$；
  - $[32,32,5,1]$；
  - $[32,32,5,1]$；
- flatten CNN output 后 linear projection 到 $\hat z_t$；
- Adam learning rate $3\times10^{-4}$。

从理论上看，$\phi$ 是摊还式推断器：

$$
\phi(h_t)\approx \mathbb{E}_{p(z\mid h_t)}[z],
$$

但它没有显式 uncertainty，也没有可辨识性证明。这一点对转笔非常重要。

### 2.7 为什么 proprioception history 里有物体属性信息

低层 PD 近似：

$$
\tau_t\approx K_p(a_t-q_t)-K_d\dot q_t.
$$

同样的 action $a_t$，如果物体更重、更滑、CoM 更偏，实际 $q_{t+1}$ 和接触反馈会不同。也就是说，history：

$$
(q_{t-k:t},a_{t-k-1:t-1})
$$

包含“我施加了什么命令，手和物体如何响应”的 input-output relation。adaptation module 正是从这个 relation 中读出 object context。

这和 classical system identification 的关系是：

- SysID 估计 exact physical parameters；
- HORA 估计 control-useful latent；
- 两者都利用 input-output history，但 HORA 的 target 是被 policy reward 学出来的。

### 2.8 Domain randomization 与 adaptation 的关系

HORA 不是不用 DR。相反，它依赖 DR 生成足够多的 object contexts：

| Parameter | Train Range | Test Range |
|---|---:|---:|
| Object Shape | Cylindrical | Cylindrical, Cube, Sphere |
| Object Scale | $[0.70,0.86]$ | $[0.66,0.90]$ |
| Mass | $[0.01,0.25]$ kg | $[0.01,0.30]$ kg |
| Center of Mass | $[-1.00,1.00]$ cm | $[-1.25,1.25]$ cm |
| Friction | $[0.3,3.0]$ | $[0.2,3.5]$ |
| External Disturbance | $(2,0.25)$ | $(4,0.25)$ |
| PD Stiffness | $[2.9,3.1]$ | $[2.6,3.4]$ |
| PD Damping | $[0.09,0.11]$ | $[0.08,0.12]$ |

DR 的作用是让训练分布覆盖变化；adaptation 的作用是让 policy 知道当前 episode 落在分布哪里。

所以最准确的表述是：

> HORA = domain randomization supplies variation; extrinsics learning organizes variation; adaptation estimates current variation online.

### 2.9 概念边界与符号陷阱

- **$e_t$ vs $z_t$**：$e_t$ 是 9 维 simulator property vector；$z_t$ 是 learned 8 维 extrinsics，不是 exact parameter。
- **$z_t$ vs $\hat z_t$**：Stage 1 用 $z_t$；部署用 $\hat z_t$。
- **history length**：最终是 30 steps / 1.5s，不是 50。
- **actor observation**：actor 不看 object pose；critic/teacher/encoder 的 privileged info 不能当部署输入。
- **主任务是 z-axis**：appendix 只给 multi-axis preliminary qualitative，不能把 HORA 写成完整 SO(3) reorientation。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设置 |
|---|---|
| Robot | Wonik Allegro Hand, 16 DoF |
| Command frequency | 20 Hz position control |
| Low-level PD | 300 Hz, $K_p=3.0$, $K_d=0.1$ |
| Simulator | IsaacGym |
| Parallel environments | 16,384 |
| Simulation frequency | 120 Hz |
| Control frequency | 20 Hz |
| Episode length | 400 control steps = 20 s |
| PPO per iteration | 16,384 envs × 8 agent steps = 0.4 s |
| PPO optimization | 5 epochs, batch 32,768, LR $5\times10^{-3}$ |
| Total training | 100,000 gradient updates, about 500M agent steps |
| Equivalent real time | about 7,000 hours |
| Adaptation LR | $3\times10^{-4}$ |

Training objects are cylinders with radius 8 cm and discretized height list:

$$
[0.8,0.85,0.9,0.95,1.0,1.05,1.1,1.15,1.2]\text{ cm}
$$

then scaled by object scale randomization.

### 3.2 Table 1：simulation baseline comparison

| Method | WTD RotR | WTD TTF | WTD ObjVel | WTD Torque | OOD RotR | OOD TTF | OOD ObjVel | OOD Torque |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Expert | $233.71\pm25.24$ | $0.85\pm0.01$ | $0.28\pm0.05$ | $1.24\pm0.19$ | $165.07\pm15.65$ | $0.71\pm0.04$ | $0.42\pm0.06$ | $1.24\pm0.16$ |
| Periodic | $43.62\pm2.52$ | $0.44\pm0.12$ | $0.72\pm0.21$ | $1.77\pm0.49$ | $22.45\pm0.59$ | $0.34\pm0.08$ | $1.11\pm0.19$ | $1.41\pm0.54$ |
| NoAdapt | $90.89\pm4.85$ | $0.65\pm0.07$ | $0.44\pm0.11$ | $1.34\pm0.12$ | $54.50\pm3.91$ | $0.51\pm0.06$ | $0.63\pm0.13$ | $1.34\pm0.11$ |
| DR | $176.12\pm26.47$ | $0.81\pm0.02$ | $0.34\pm0.05$ | $1.42\pm0.06$ | $140.80\pm17.51$ | $0.63\pm0.02$ | $0.64\pm0.06$ | $1.48\pm0.20$ |
| SysID | $174.42\pm23.31$ | $0.81\pm0.02$ | $0.32\pm0.03$ | $1.29\pm0.72$ | $132.56\pm17.42$ | $0.62\pm0.09$ | $0.50\pm0.09$ | $1.26\pm0.17$ |
| Ours | $222.27\pm21.20$ | $0.82\pm0.02$ | $0.29\pm0.05$ | $1.20\pm0.19$ | $160.60\pm10.22$ | $0.68\pm0.07$ | $0.47\pm0.07$ | $1.20\pm0.17$ |

因果解释：

- Ours 接近 Expert：说明 $\hat z$ 能恢复大部分 privileged context 的控制价值；
- DR 稳但慢，且 OOD ObjVel 高：说明 robust average policy 无法对当前物体选择最优 gait；
- SysID 不如 Ours：说明 exact physical parameter prediction 比 learned task latent 更难、更没必要；
- NoAdapt 低：说明必须 continuous online update，不是一开始估一次就够；
- Periodic 失败：说明任务不是固定 gait replay，而是 object/context-dependent control。

### 3.3 Real heavy objects：Figure 3

真实 heavy objects：6 个物体，质量都大于 100g，20 initial grasps，每 episode 最大 30 s。

| Method | Rotations | TTF | Torque |
|---|---:|---:|---:|
| DR | $9.67\pm4.33$ | $0.72\pm0.34$ | $2.03\pm0.36$ |
| SysID | $10.36\pm2.32$ | $0.61\pm0.33$ | $1.88\pm0.38$ |
| NoAdapt | N.A. | $0.35\pm0.20$ | N.A. |
| Ours | $23.96\pm3.16$ | $0.98\pm0.08$ | $1.84\pm0.24$ |

因果解释：

- Ours rotation 是 DR 的约 2.5 倍，同时 TTF 也更高；
- SysID 转得比 DR 略多但更不稳定；
- NoAdapt 真实部署失败，说明 online update 是真机必要条件；
- Ours torque 低于 DR，说明 adaptation 不是靠更大力硬转，而是更合适地调 gait。

### 3.4 Real irregular objects：Figure 4

irregular set 包含 moving COM container、concave objects、cylindrical kiwi、shuttlecock、holes、cube toy 等。

| Method | Rotations | TTF | Torque |
|---|---:|---:|---:|
| DR | $6.59\pm3.71$ | $0.66\pm0.41$ | $1.85\pm0.37$ |
| SysID | $8.16\pm3.39$ | $0.46\pm0.36$ | $1.70\pm0.40$ |
| NoAdapt | N.A. | $0.12\pm0.05$ | N.A. |
| Ours | $19.22\pm4.08$ | $0.78\pm0.27$ | $1.48\pm0.30$ |

因果解释：

- Ours 在 irregular objects 上仍明显优于 DR/SysID；
- DR 的 TTF 还可以但 Rotations 低，说明它通过保守动作换稳定；
- SysID 角速度更积极但掉得更快；
- HORA 的优势是“既转得动，又不靠高 torque 乱推”。

### 3.5 33-object qualitative / per-object analysis

论文网站和 appendix 报告 33 个真实物体：

- 直径 4.5-7.5 cm；
- 质量 5g-200g；
- 包含 porous、non-rigid、high CoM、irregular objects；
- 22/33 个物体实现几乎完美的稳定连续 rotation；
- cube、large aspect ratio heavy objects、small objects 可以维持约 10-20 s；
- failure 主要来自 object falling from fingertips due to incorrect contact positions。

这里最关键的反面证据是：

> HORA 的失败不是“没估出 mass/scale”，而是“不知道精确接触点”。

这直接解释为什么后续 Touch Dexterity / Robot Synesthesia / RotateIt 要引入 tactile/vision。

### 3.6 Extrinsics analysis：Figure 5 / 6 / 7

Figure 5：连续 run 中每 30 s 换一个物体，虽然训练时从不在 episode 中换物体，$\hat z$ 仍会随物体变化：

- $z_{t,0}$ 响应 object diameter，小直径值更低，大直径值更高；
- $z_{t,2}$ 响应 object mass，轻物体更高，重物体更低。

Figure 6：t-SNE 显示不同 size/weight objects 的 estimated extrinsics 分布在不同区域。

Figure 7：commanded torque 与 object mass 近似线性相关；更轻的物体，policy command smaller torque for energy efficiency。

这三者共同证明：

- $\hat z$ 不是任意 latent；
- 它确实编码了与控制相关的 object properties；
- 但它是 coarse/task-relative 的，不是 exact SysID。

### 3.7 Ablation：No randomization

| Method | WTD RotR | WTD TTF | WTD ObjVel | WTD Torque | OOD RotR | OOD TTF | OOD ObjVel | OOD Torque |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| No Rand | $171.96\pm20.63$ | $0.63\pm0.07$ | $0.48\pm0.07$ | $1.94\pm0.32$ | $88.02\pm14.27$ | $0.37\pm0.06$ | $0.98\pm0.16$ | $2.26\pm0.29$ |
| Ours | $222.27\pm21.20$ | $0.82\pm0.02$ | $0.29\pm0.05$ | $1.20\pm0.19$ | $160.60\pm10.22$ | $0.68\pm0.07$ | $0.47\pm0.07$ | $1.20\pm0.17$ |

因果链：

`remove physical randomization → OOD RotR 160.60→88.02, TTF 0.68→0.37 → adaptation module never sees enough context variation → learned z cannot organize unseen physical properties.`

### 3.8 Ablation：history length

| Method | WTD RotR | WTD TTF | OOD RotR | OOD TTF |
|---|---:|---:|---:|---:|
| Ours-T10 | $215.81\pm17.55$ | $0.80\pm0.02$ | $150.58\pm7.07$ | $0.61\pm0.05$ |
| Ours-T20 | $220.46\pm19.72$ | $0.82\pm0.02$ | $157.22\pm8.11$ | $0.64\pm0.04$ |
| Ours-T30 | $222.27\pm21.20$ | $0.82\pm0.02$ | $160.60\pm10.22$ | $0.68\pm0.07$ |

因果链：

`longer history → better OOD performance until T=30 → because object properties require enough action-response evidence → but saturates, so longer history is not automatically better.`

### 3.9 Ablation：long-history DR is not adaptation

Appendix Table 4 tests whether simply feeding longer history to a robust DR policy can replace HORA. It cannot.

Key trend:

- DR-MLP-T3 OOD RotR = 140.80；
- DR-MLP-T20 OOD RotR = 60.21；
- DR-MLP-T30 OOD RotR = 36.33；
- DR-LSTM-T10 OOD RotR = 73.60；
- Ours OOD RotR = 160.60。

结论：

> 给 PPO 一个长历史，不等于它会学出好的在线辨识；显式把 history regression target 设成 $z_t$，把“辨识”和“控制”分开，是 HORA 的关键。

这也是为什么 old-style “just use recurrent policy” 不是足够严肃的 baseline。

## 4. 核心洞见

### 4.1 真正的 insight：低维 latent 不是压缩物理，而是压缩控制需求

HORA 最深的 insight 是：

$$
e_t\to z_t
$$

这一步不是 autoencoder 式压缩，也不是 system identification。它是把物理参数按“对当前控制任务是否等价”重新编码。

两个真实物体外观完全不同，但如果在 fingertip rotation 中呈现类似 mass/diameter/contact response，它们可以有相近 $z$。论文 §5.3 明说：real objects seemingly different may look similar in extrinsics space。

这就是为什么只用 cylinders 训练却能泛化到 irregular objects：不是 policy 理解了外观，而是它学到了 fingertips perceived dynamics 的低维组织方式。

### 4.2 为什么它有效

它有效需要四个条件：

1. **任务不需要精确 object pose**：z-axis continuous rotation 可以靠接触响应闭环。
2. **object context 可从 proprio history 辨识**：mass/size/friction 会影响 action-response。
3. **仿真 randomization 覆盖了 relevant dynamics**：否则 $\mu$ 和 $\phi$ 没见过足够 variation。
4. **低层 PD 接口稳定**：position target + PD controller 缓和 sim-real torque gap。

如果任务变成 peg insertion、tool use、pen catching 或 arbitrary SO(3) pose tracking，这些条件会被破坏。

### 4.3 什么时候会失效

论文自己给出的 failure modes：

- incorrect contact points → unstable force closure；
- object diameter < 4.0 cm → fingers collide, grasp balance difficult；
- more extreme/sophisticated shapes harder；
- no real experience used for improvement。

抽象成机制：

> HORA 可以估计“这个物体像什么动力学 context”，但它不知道“此刻到底在哪里接触”。当 contact geometry 变成 bottleneck，纯 proprioception 就不够。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 根因 | 影响 |
|---|---|---|
| 可辨识性无保证 | 不同 $e$ 可能产生相同 proprio/action history | $\phi$ 可能输出混淆 latent |
| $z$ 只对当前任务充分 | 学于 z-axis rotation reward | 不能保证迁移到 precision pose/control |
| 没有 uncertainty | $\hat z$ 是 point estimate | policy 不知道自己是否估错 context |
| no contact location | 纯本体历史间接反映 contact | contact point 错时无法纠正 |
| no stability proof | 非 classical adaptive control | 只能靠实验验证在线 adaptation 稳定性 |

### 5.2 算法维度

| 替代路线 | 优势 | 相对 HORA 的风险 |
|---|---|---|
| pure DR policy | 简单、部署稳定 | robust average，慢且保守 |
| exact SysID | 物理解释强 | 参数难估、没必要、实验更差 |
| recurrent policy | 端到端，无两阶段 | PPO 长历史优化困难，appendix 已显示 |
| DPF/belief filter | 可表达 uncertainty/multimodal | 需要定义 state 和 likelihood，更复杂 |
| visuotactile policy | 可直接知道 contact/shape | sensor gap、标定、latency 更高 |

### 5.3 工程/实验维度

- 主任务只绕 z-axis；multi-axis 只在 appendix/project website 做 preliminary qualitative。
- 训练消耗 500M agent steps，相当于 7000 hours real time，依赖 GPU simulation。
- 真实评估无 real fine-tuning。
- policy 依赖 initial stable precision grasp；不是从任意抓取启动。
- 使用 Allegro/PD settings，迁移到 LinkerHand 要重做 action interface 和 actuator randomization。
- 对 tiny / extreme shapes / precise contact geometry 失败。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔的直接迁移

HORA 给转笔的最大启发是：

> 不必把所有笔的物理属性显式测出来；可以学习一个“对转笔控制足够”的 pen extrinsics latent，并从动作-本体-触觉历史中在线估计。

可能的转笔 extrinsics：

| HORA object context | 转笔 context |
|---|---|
| mass | 笔总质量 |
| scale/diameter | 笔长度、半径、握持位置 |
| CoM | 笔帽/笔尖造成的重心偏移 |
| friction | 笔身材料与手指摩擦 |
| hidden shape response | 是否有笔帽、橡胶 grip、非对称段 |
| action-response history | 给定拨动后角速度/滑移/接触持续时间 |

但转笔比 HORA 难：

- 需要 pen phase / angular velocity；
- 接触位置和滑移非常关键；
- 可能有 aerial phase；
- 高速动态下 1.5s history 可能太慢；
- 纯本体可能无法辨识笔的相位。

因此推荐的迁移不是 “HORA-only”，而是：

$$
\hat z_t=\phi(q,\dot q,a,\text{motor current},\text{tactile contact/shear},\text{optional vision history})
$$

再给 PPO Oracle / diffusion generalist 使用。

### 6.2 对 WMTS 的结合

| WMTS 模块 | HORA 启发 | 具体做法 |
|---|---|---|
| latent task generation | task context 不只来自指令，也来自 object/dynamics latent | scheduler 根据 $\hat z$ 选择 skill difficulty / subgoal |
| PPO Oracle | privileged context-conditioned training | sim 中用 true pen state/physics 训 $\pi(o,z)$ |
| Diffusion/Flow generalist | distill context-conditioned trajectories | condition on estimated extrinsics, not raw object ID |
| Ensemble World Model | model uncertainty over $z$ and dynamics | ensemble disagreement 判断 adaptation 是否可靠 |
| real fine-tuning | HORA 没做，需要补 | 收集 real failure 更新 $\phi$ 或 residual dynamics |

关键设计判断：

> WMTS 不应该只做 one-size-fits-all generalist。先训练 context-conditioned specialists/oracles，再学 deployable context estimator，是更稳的路径。

### 6.3 可验证实验建议

| 实验 | Baselines | 指标 | 证伪标准 |
|---|---|---|---|
| Pen extrinsics 是否可从 history 辨识 | pure DR vs HORA-style latent | spin duration, phase error, drop rate | latent 不提升则 pen context 不可从 history 估计 |
| exact SysID vs learned latent | predict true mass/CoM/friction vs learned $z$ | control success, latent probe | exact SysID 更好则 learned latent 非必要 |
| tactile 是否必要 | proprio-only $\phi$ vs proprio+tactile $\phi$ | contact phase recovery | tactile 不提升则 proprio 足够 |
| history length | 5/10/20/30 steps | early adaptation speed | 长 history 拖慢高速控制则需短窗/多尺度 |
| uncertainty-aware adaptation | point $\hat z$ vs ensemble/variance $\hat z$ | recovery after slip | uncertainty 无提升则 point estimate 足够 |

### 6.4 不应过度外推的点

- HORA 成功不代表“视觉/触觉不需要”；它失败模式正指向 contact point 不可观测。
- HORA z-axis 不等于 arbitrary SO(3) manipulation。
- Learned extrinsics 可解释但不是可证明物理参数。
- 纯本体适应在高速转笔中可能无法观测 phase。
- DR 仍是 HORA 的基础；没有 broad randomization，adaptation 没有组织对象差异的材料。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

HORA 是 conditional PPO：

$$
\pi_\theta(a_t\mid o_t,z_t),
\qquad
z_t=\mu(e_t).
$$

PPO 不再学一个平均 policy，而是学一个 context-indexed policy family。adaptation module 负责部署时提供 context estimate。

### 7.2 与 [[Dynamics]] 的联系

物体参数通过接触动力学影响响应：

$$
M_o(e)\ddot q_o+C_o(e,q_o,\dot q_o)\dot q_o+g_o(e,q_o)
=
J_c^\top f_c.
$$

HORA 不显式建模 $M,C,g$，而是通过动作-本体历史估计一个控制有用的 latent $z$。这是 dynamics-aware representation learning。

### 7.3 与 [[ControlTheory]] 的联系

HORA 类似 adaptive control：

$$
\text{estimate context}\ \hat z_t
\quad\to\quad
\text{adapt controller}\ \pi(o_t,\hat z_t).
$$

但它缺少 classical adaptive control 的 persistent excitation / parameter convergence / Lyapunov stability 证明。因此它是工程上有效的 learned adaptive control，而不是有证明的自适应控制器。

### 7.4 与 [[RepresentationLearning]] 的联系

$\mu(e)$ 学到的是 task-aligned representation。Figure 5/6/7 说明它和 diameter/mass/torque 有相关结构，但不是完全解耦。好的分析方式不是问“每个维度对应哪个物理量”，而是问：

> 这个 latent 是否把对控制等价的物体放近，把需要不同 gait 的物体分开？

### 7.5 与 in-hand rotation 簇的联系

HORA 占据：

$$
\langle\text{有支撑/指尖保持},\ z\text{-axis},\ \text{pure proprioception}\rangle
$$

这个原点格。后续论文基本都在扩展某个维度：

- RotateIt：多轴 + vision/touch shape/extrinsics；
- Robot Synesthesia：contact geometry point cloud；
- Touch Dexterity：binary tactile blind rotation；
- AnyRotate：dense tactile arbitrary-axis；
- Spin Pens：无支撑、动态笔。

因此 HORA 是评估新方法的基准线：新方法必须说明它相对 HORA 到底解决了哪个不可观测变量，而不是只说“更强感知”。

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “extrinsics 是真实物理参数吗？” | 不是，是 $e_t$ 经 $\mu$ 学出的 task-relevant 8-d latent |
| “为什么 SysID 更差？” | exact parameter 难估且不一定控制相关；learned latent 聚合任务等价物体 |
| “HORA 和 DR 的本质区别？” | DR 学 robust average；HORA 估当前 context 并切换子策略 |
| “为什么 NoAdapt 失败？” | object/contact context episode 内会变化，初始估计不能持续有效 |
| “真实实验最强证据？” | heavy objects: 23.96 rotations / TTF 0.98；irregular: 19.22 / 0.78 |
| “最大 limitation？” | 纯本体不知道 precise contact points，tiny/extreme shapes 容易失败 |
| “对转笔能直接用吗？” | 不能直接；应作为 latent adaptation template，并补 tactile/phase/shear |

## References

- Haozhi Qi, Ashish Kumar, Roberto Calandra, Yi Ma, Jitendra Malik. *In-Hand Object Rotation via Rapid Motor Adaptation*. CoRL 2022.
- Ashish Kumar et al. *RMA: Rapid Motor Adaptation for Legged Robots*. RSS 2021.
