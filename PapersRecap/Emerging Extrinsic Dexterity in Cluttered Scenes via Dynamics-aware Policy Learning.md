---
tags:
  - paper
  - manipulation
  - non-prehensile
  - extrinsic-dexterity
  - representation-learning
  - dynamics
aliases:
  - DAPL
  - Emerging Extrinsic Dexterity
  - Dynamics-Aware Policy Learning
paper-year: 2026
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ComputationalGeometry]]"
---

# Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning

> [!abstract] 核心贡献
> DAPL 把 cluttered non-prehensile manipulation 的核心从“静态几何避障”改写为“接触后物体会怎样动”的动力学表征学习：先用点级 physical world model 学 $(p,m,v)\rightarrow(p^+,v^+)$，再把冻结的 dynamics feature 条件化 PPO policy，使策略能选择性利用或避开环境接触；在 Clutter6D Dense track 上 DAPL 44.56% success rate，约为 CORN 22.22% 的 2 倍。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — $x_i=(p_i,m_i,v_i)$ 是离散多体动力学的最小局部状态近似；质量和速度决定接触冲量后的运动响应。
> - [[ContactMechanics]] — extrinsic dexterity 本质是选择性利用接触链：推、滑、翻、借重物作 pivot，而不是回避所有碰撞。
> - [[RepresentationLearning]] — 预训练目标不是 reconstruction，而是 point-level future dynamics prediction；表征好坏由下游接触策略验证。
> - [[ReinforcementLearning]] — world model 不直接做 MPC，而是作为 frozen dynamics encoder 条件化 actor-critic / PPO。
> - [[ComputationalGeometry]] — point-level dense representation 保留局部接触几何，object-level 6DoF pose 过粗，Sparse SR 只有 16.88%。
>
> **核心技术**: Dynamics-Aware Policy Learning, Point-level World Model, Velocity Variance Regularization, Curriculum World-Model Refinement, PPO with Dynamics Tokens, Teacher-Student Sim-to-Real

## 0. 阅读定位与范本价值

这篇论文应该放在 PDDM 之后读。PDDM 用 learned dynamics 做 online planning；DAPL 不用 world model 直接规划，而是把 world model 压成一个给 policy 用的 dynamics representation。这是一个很重要的转向：

$$
\text{PDDM}: \hat{p}_\theta(s'\mid s,a)\rightarrow \text{MPC}
$$

$$
\text{DAPL}: \hat{p}_\theta(P_{t+\Delta t},V_{t+\Delta t}\mid P_t,V_t,a_t)\rightarrow f_{dy}\rightarrow \pi_\phi(a_t\mid f_{dy},s_{robot},g)
$$

它对 WMTS 的价值是：world model 未必只能用于 planning 或 rollout，它也可以作为**策略条件化表征**，把“当前场景中哪些接触可利用、哪些会造成扰动”编码成 latent prior，帮助 PPO/Diffusion generalist 更快学到 extrinsic dexterity。

但这篇也必须批判地读。它的 “zero-shot sim-to-real” 并不是无感知假设：真实系统用了 SAM2/XMem/FoundationPose、GPT-5 mass estimation、EKF velocity filtering、teacher-student distillation、Cartesian action clipping。这些工程栈是成功条件，不是旁枝。

| 四支柱 | 本文必须回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么几何表征在 clutter 中不够？ | §1：contact outcome 取决于 dynamics，不只取决于 shape |
| 原理与理论 | 为什么 $p,m,v$、point-level、variance loss 是必要的？ | §2：从接触冲量、Markov state、point dynamics、PPO conditioning 推导 |
| 实验与验证 | 哪些数字证明“dynamics-aware”而非“更大网络”有效？ | §3：Table I/II/III、curriculum、mass perturbation 因果解释 |
| 未来与结合 | 如何迁移到 LinkerHand/WMTS，哪里不能外推？ | §5-§7：tactile/contact token、actuator-aware dynamics、Sim-to-Real 边界 |

## 1. 问题设定与动机

### 1.1 一句话核心

DAPL 的一句话核心是：**cluttered non-prehensile manipulation 的关键不是“哪里有障碍物”，而是“接触后哪个物体会滑、会倒、会成为支点、会把目标卡住”**；因此 policy 需要 dynamics-aware representation，而不只是 point-cloud geometry representation。

### 1.2 直观隐喻

几何方法像只看台球桌上球的位置；DAPL 像还估计每个球的质量、速度、碰撞后会怎么传递动量。只看位置时，你只能“避开球”；理解动力学后，你可以“借一个重球当墙，把目标球弹出来”。

这个隐喻的可证伪点是：如果把质量和速度拿掉，策略应该显著退化；如果只做静态 point reconstruction 而不预测未来运动，也应该退化。Table II 正好给出这两个证据。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 在 cluttered extrinsic dexterity 中的局限 |
|---|---|---|
| Prehensile grasp + motion planning | 目标最终要被抓起；路径尽量 collision-free | Dense clutter 中 grasp pose/approach path 被遮挡；很多任务必须先推/滑/翻出可抓姿态 |
| CORN / UniCORN 几何表征 | contact-centric geometry / point cloud feature | 能看到“哪里可接触”，但不知道“接触后谁会动、谁能当 anchor、谁会被扰乱” |
| 端到端 RL | 直接从 observation 学 policy | contact exploration 稀疏且代价高；容易把 contact physics 当作黑盒反复试错 |
| Model-based planning / hand-crafted primitives | 显式接触模式、轨迹/技能模板 | 需要精确位姿和手工 contact mode；多物体 clutter 下模式组合不可扩 |
| 静态 reconstruction / contrastive pretraining | 学 shape/geometry latent | 表征目标与 manipulation outcome 不对齐；重建静态点云不等于理解 momentum transfer |

### 1.4 Delta 分析

DAPL 的 delta 有三层：

1. **Representation delta**：从 geometry-only $(x,y,z)$ 到 physical point feature $(p,m,v)$。
2. **Objective delta**：从 reconstruction / pose prediction 到 point-level future dynamics prediction。
3. **Policy delta**：world model 不做 online MPC，而是提供 $f_{dy}$ 给 actor-critic policy，使 extrinsic dexterity 在 RL 中涌现。

因此它不是“多加了一个 Transformer encoder”这么简单。论文通过 fair setup 强调：learning-based baselines 使用 comparable policy networks，差别主要在 encoder 输入和 pretraining target；Table II 再证明 point-level dynamics + velocity + physical features 才是关键。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $p_i$ | $\mathbb{R}^3$ | object/environment/EE point cloud | world model 训练中作为输入；无梯度 label | 第 $i$ 个点的位置 | 是环境坐标，不是 object-local canonical point |
| $m_i$ | scalar | object mass distributed to sampled points | 输入，无梯度 | 每点质量 proxy，$m_i=M/N$ | 不是真实局部密度；是让网络区分重/轻物体 |
| $v_i$ | $\mathbb{R}^3$ | sim state；real via pose difference + EKF | 输入/label，无梯度 | 点速度，决定未来趋势 | real velocity 很 noisy；论文用 distillation under perturbation 适配 |
| $x_i=(p_i,m_i,v_i)$ | $\mathbb{R}^7$ | scene representation | 输入 | dynamics-aware point feature | 旧稿常写成 $(p,m,v)$，但 appendix 明确是 $(x,y,z,m,v_x,v_y,v_z)$ |
| $P^o$ | $\mathbb{R}^{512\times 7}$ | target object point cloud | 输入 | 目标物体物理点云 | 目标和环境分开采样，避免语义污染 |
| $P^e$ | $\mathbb{R}^{512\times 7}$ | nearest environmental obstacle points | 输入 | clutter 点云 | 只取 target 附近 512 点，不处理全背景 |
| $P^{ee}$ | $\mathbb{R}^{256\times 7}$ | end-effector mesh points | 输入 | robot contact geometry | 不是 robot proprioception；是几何接触表面 |
| $Z_t$ | $\mathbb{R}^{P\times D}$, $P=40,D=128$ | dynamics encoder | 带梯度于 world model 训练；policy 阶段 frozen | patch-level dynamics token | token 来自 16 target + 16 obstacle + 8 EE patches |
| $\hat{P}_{t+\Delta t},\hat{V}_{t+\Delta t}$ | point-level future state | decoder output | world model 训练中带梯度 | future position/velocity prediction | $\Delta t=0.1s$ |
| $f_{dy}$ | latent dynamics feature | pre-trained/frozen dynamics encoder | PPO 阶段通常 frozen | policy condition | 不是直接 rollout simulator；是 representation |
| $s_{env}$ | goal + robot states + physics + previous action | policy input | PPO 中 observation | task-conditioned query | real deployment 缺少 privileged physics，需 student distillation |
| $\Delta q_t$ | $\mathbb{R}^7$ | actor output | PPO actor 带梯度 | 7-DoF arm joint residual | 不是末端 SE(3) action；经 Jacobian clipping 后 impedance 执行 |
| $r_{contact},r_{goal},r_{success}$ | scalar rewards | reward computation | PPO 中无梯度 reward | proximity、goal tracking、success/disturbance | reward 不复杂，但并非 sparse-only |

### 2.2 为什么 extrinsic dexterity 需要动力学，而不只是几何

几何表征回答：

$$
\text{where are objects?}
$$

DAPL 要回答：

$$
\text{what will happen if I touch here with this action?}
$$

从最简接触动力学看，一个物体受到接触冲量 $J$ 后速度变化为：

$$
v^+=v^-+\frac{J}{m}.
$$

若考虑转动，还需要：

$$
\omega^+=\omega^-+I^{-1}(r\times J).
$$

所以同一几何接触点，在不同 $m,I,v,\omega$ 下会产生不同结果。几何-only encoder 看到“pie 和 can 的位置一样”，但不知道谁重、谁轻、谁适合当 anchor。DAPL 把 mass 和 velocity 注入 point feature，本质上是在给 policy 提供“接触后状态转移”的条件变量。

这解释了 Table II：World Model Point-level without velocity/physical features 的 Sparse SR 是 42.00%；加 velocity 变 58.25%；再加 physical features 变 71.88%。提升不是装饰性的，而是动力学状态从欠定变得更接近 Markov。

### 2.3 Physical scene representation：从 object/scene/EE 到 $x_i$

主文 Eq.(1)：

$$
x_i=(p_i,m_i,v_i),
$$

其中：

$$
p_i\in\mathbb{R}^3,\quad m_i\in\mathbb{R},\quad v_i\in\mathbb{R}^3.
$$

附录进一步写成：

$$
f_i=[x,y,z,m,v_x,v_y,v_z].
$$

质量按物体总质量分到点：

$$
m_i=\frac{M}{N}.
$$

这个设计不是在声称每个点真的具有独立物理质量，而是给每个点附带所属物体的 inertial prior。网络看到一组点时，可以把“这个局部几何属于重物体”与“接触后更可能作为稳定支点”关联起来。

采样结构：

| 组成 | 点数 | 角色 |
|---|---:|---|
| Target object $P^o$ | 512 | 被重排物体 |
| Environment obstacles $P^e$ | 512 | target 周围最相关 clutter |
| End-effector $P^{ee}$ | 256 | 机器人接触几何 |
| Total | 1280 | world model 输入 |

tokenization 不是普通随机点云 transformer。附录说明 semantic-aware sampling：

| patch 来源 | patch 数 | kNN |
|---|---:|---:|
| target object | 16 | 32 |
| environment obstacles | 16 | 32 |
| end-effector | 8 | 32 |
| total | 40 | 32 |

这个语义分组是关键工程细节：如果一开始就把 EE、target、obstacle 混在同一 patch，局部 token 会混淆“谁主动施力、谁被移动、谁是背景支点”。

### 2.4 World model architecture：point dynamics, not object pose

World model 做：

$$
(P_t,V_t,a_t)\rightarrow (\hat{P}_{t+\Delta t},\hat{V}_{t+\Delta t}),\quad \Delta t=0.1s.
$$

结构链条是：

| 步骤 | 作用 | 为什么需要 |
|---|---|---|
| FPS + kNN patches | 生成局部 patch | 保留局部接触几何 |
| PointNet-style patch encoder | patch 内置换不变聚合 | 点顺序不应影响特征 |
| sinusoidal positional embedding | 恢复全局空间位置 | patch normalization 会丢 global relation |
| ViT encoder, 12 blocks, 8 heads, hidden 128 | 建模多物体耦合 | contact chain 可能跨物体传播 |
| action token cross-attention | 注入 robot action / EE flow | 同一场景不同动作导致不同未来 |
| unpatchify scatter + point MLP | 回到 point-level prediction | 让监督对齐局部接触运动 |

Point-level 是论文的硬判断。Object-level 6DoF pose prediction 在 Table II 中即便有 velocity/physical features，Sparse SR 也只有 16.88%；point-level world model + velocity + physical features 是 71.88%。这说明在 cluttered contact 中，6D pose 太粗：它抹掉局部接触点、局部变形/遮挡、物体间碰撞传播的细粒度信息。

### 2.5 World model objective：为什么需要 velocity variance regularization

主文写出 dense point-level dynamics loss：

$$
\mathcal{L}_{dyn}
=
\sum_i
\|\hat{p}_i^{t+1}-p_i^{t+1}\|_2^2
+
\lambda\|\hat{v}_i^{t+1}-v_i^{t+1}\|_2^2.
$$

问题是 clutter 中大部分点不动。若只最小化 point-wise velocity MSE，模型有一个坏的捷径：

$$
\hat{v}_i^{t+1}\approx 0 \quad \forall i.
$$

因为静止点占多数，这个预测能拿到低 MSE，却完全丢掉少数接触点的运动信号。DAPL 的修正是匹配速度场的统计分布。主文写成 standard deviation matching：

$$
\mathcal{L}_{var}
=
\left\|
\mathrm{Std}\{\hat{v}_i^{t+1}\}_i
-
\mathrm{Std}\{v_i^{t+1}\}_i
\right\|_2^2.
$$

附录实现写成 variance matching：

$$
\mathcal{L}_{var}
=
\|\mathrm{Var}(\hat{V}_{t+\Delta t})-\mathrm{Var}(V_{t+\Delta t})\|_2^2.
$$

最终：

$$
\mathcal{L}
=
\lambda_{pos}\mathcal{L}_{pos}
+
\lambda_{vel}\mathcal{L}_{vel}
+
\lambda_{var}\mathcal{L}_{var},
$$

其中附录给出：

$$
\lambda_{pos}=1.0,\quad \lambda_{vel}=1.0,\quad \lambda_{var}=100.0.
$$

注意这里的 $\mathcal{L}_{var}$ 不是为了让每个点速度更准，而是防止整体速度分布坍缩。它在理论上是在告诉 world model：“你至少要知道场景里有多少运动、运动分布多分散”，否则 policy 得不到 contact-induced motion prior。

### 2.6 Policy learning：world model feature 如何进入 PPO

DAPL policy observation 有三部分：

1. dynamics-aware scene representation $f_{dy}$；
2. robot proprioceptive state；
3. relative task goal。

附录 MDP 组件：

| 组件 | 符号 | 维度 | 含义 |
|---|---|---:|---|
| Object point cloud | $P^o$ | $\mathbb{R}^{512\times 7}$ | target object points with $(x,y,z,m,v_x,v_y,v_z)$ |
| Environment point cloud | $P^e$ | $\mathbb{R}^{512\times 7}$ | obstacle points with mass/velocity |
| End-effector point cloud | $P^{ee}$ | $\mathbb{R}^{256\times 7}$ | EE mesh points with mass/velocity |
| Hand/EE state | $s_t^{EE}$ | $\mathbb{R}^9$ | EE position + 6D rotation |
| Robot state | $s_t^q$ | $\mathbb{R}^{14}$ | 7 joint positions + 7 joint velocities |
| Relative goal pose | $T_g$ | $\mathbb{R}^9$ | target pose relative to current object pose |
| Physics parameters | $\rho$ | $\mathbb{R}^5$ | mass, object friction, hand friction, ground friction, restitution; sim only |
| Previous action | $a_{t-1}$ | $\mathbb{R}^7$ | previous joint residual |
| Action | $\Delta q_t$ | $\mathbb{R}^7$ | relative joint command, $q_{target}=q_t+\Delta q_t$ |

Policy architecture:

- dynamics encoder outputs patch tokens $Z\in\mathbb{R}^{P\times D}$；
- $s_{env}$ aggregates goal, robot states, physics parameters, previous action；
- $s_{env}$ is projected into a query token and cross-attends over $Z$；
- fused feature passes through MLP [512, 256, 128]；
- Actor/Critic are two-layer MLPs with hidden dim 64；
- actor outputs Gaussian mean with learnable log std。

PPO details:

| Hyperparameter | Value |
|---|---:|
| parallel environments | 2048 |
| hardware | 8 x L40 GPU cluster |
| value loss coefficient | 0.5 |
| clipped value loss | True |
| clip parameter $\epsilon$ | 0.3 |
| entropy coefficient | 0.006 |
| learning epochs | 8 |
| mini-batches | 8 |
| learning rate | $5.0\times 10^{-5}$ |
| LR schedule | Adaptive |
| discount factor $\gamma$ | 0.99 |
| GAE $\lambda$ | 0.95 |
| desired KL | 0.016 |
| max gradient norm | 1.0 |

关键边界：dynamics encoder 在 PPO 阶段 loaded with pre-trained weights and remains frozen。也就是说，policy 不是一边通过 RL loss 改写 world model；curriculum refinement 是在 policy rollout 后更新 world model，再重用 refined encoder。

### 2.7 Reward：并非复杂 shaping，但也不是纯 sparse

主文说 reward 没有 complex engineering，但它仍包括 contact、goal、success/disturbance 三类。

End-effector proximity：

$$
d_{ee}=\min(\|p_{obj}-p_{ee,L}\|,\|p_{obj}-p_{ee,R}\|),
$$

$$
r_{contact}=1-\tanh\left(\frac{d_{ee}}{\sigma_{contact}}\right),
\quad \sigma_{contact}=0.1.
$$

goal reward gated by contact proximity：

$$
I_{near}=
\begin{cases}
1,&d_{ee}<d_{th}\\
0,&\text{otherwise}
\end{cases},
\quad d_{th}=0.1m.
$$

pose error:

$$
d_p=\|p_{des}-p_{obj}\|,
\quad
d_r=2\arccos(|q_{obj}\cdot q_{des}|),
$$

$$
d=d_p+\frac{d_r}{5}.
$$

coarse/fine goal terms:

$$
r_{goal}=I_{near}\left(1-\tanh\left(\frac{d}{0.6}\right)\right),
$$

$$
r_{goal-fine}=I_{near}\left(1-\tanh\left(\frac{d}{0.3}\right)\right).
$$

success uses both target success and clutter disturbance penalty. Let success mask:

$$
m=I(d_{pos}<\tau_p)\wedge I(d_{rot}<\tau_r).
$$

Obstacle motion score:

$$
m_{motion}=\frac{\hat{d}+\hat{\theta}}{2}.
$$

success scaling:

$$
s=\mathrm{clip}(1-0.5m_{motion},0.5,1.0),
$$

final success:

$$
r_{success}=r_0\cdot s.
$$

Reward weights:

| Term | Weight |
|---|---:|
| $r_{contact}$ | 1.0 |
| $r_{goal}$ | 5.0 |
| $r_{goal-fine}$ | 16.0 |
| $r_{success}$ | 2000.0 |
| $\sigma_{coarse}$ | 0.6 |
| $\sigma_{fine}$ | 0.3 |

这解释了 DAPL 的“no complex reward shaping”应该怎么读：它不手写接触模式和技能 primitive，但仍有相当强的 goal/contact/success shaping；不能把成功完全归因于 representation。

### 2.8 Curriculum：policy rollout 反过来修 world model

DAPL 不依赖固定 offline dataset。流程是：

| 阶段 | 数据分布 | 作用 |
|---|---|---|
| 初始 policy | 无 dynamics pretraining，从 scratch 学到 basic task coverage | 产生第一批真实 policy-induced contacts |
| rollout collection | 约 60k interaction steps | 包含 random collisions 和 suboptimal behavior |
| world model refinement | 用 rollout 更新 dynamics encoder | 学到 policy 真会访问的接触分布 |
| policy retraining/conditioning | 用 refined encoder 条件化 PPO | 更稳定地学习 extrinsic dexterity |

这个 curriculum 的 insight 很好：world model 不是越“通用”越好，而是要覆盖 policy 将访问的 contact distribution。随机数据可能覆盖广但不 task-relevant；policy rollout 失败样本反而能暴露关键接触链。

## 3. 训练、数据与实验

### 3.1 Clutter6D benchmark 设置

Clutter6D 是 6D object rearrangement benchmark，强调 full 6D pose、multi-object contact、dynamic coupling，而不是单纯 planar pushing 或 collision avoidance。

| Track | Object count | 说明 |
|---|---:|---|
| Sparse | 4 objects | target + lower clutter density |
| Moderate | 8 objects | more interaction constraints |
| Dense | 12 objects | contact chain frequent, collision-free path rare |

数据：

- Sparse track: 1,024 training scenes；
- each track: 128 held-out evaluation scenes；
- evaluation success: target reaches desired pose within 0.05 m and 0.1 rad；
- episode ends on success, object drop, or 300 simulation steps；
- non-target disturbance measured by Chamfer-distance mean offset (M.O., cm)。

环境工程：

- IsaacLab / PhysX；
- Objaverse assets，mesh simplification and convex decomposition via PaMO / CoACD；
- 10K tabletop-scale assets；
- task-oriented scene graph controls object relations；
- goal pose requires at least 0.15 m planar displacement in appendix generation。

### 3.2 Simulation main results: Table I

| Method | Action Type | Sparse SR | Sparse M.O. | Moderate SR | Moderate M.O. | Dense SR | Dense M.O. |
|---|---|---:|---:|---:|---:|---:|---:|
| Teleoperation | Mixed | 50.0 | 3.13 | 40.0 | 7.49 | 20.0 | 21.34 |
| GraspGen + CuRobo | Prehensile | 26.6 | - | 15.6 | - | 3.13 | - |
| Point2Vec | Non-prehensile | 6.89 | 5.09 | 1.95 | 3.36 | 0.78 | 5.35 |
| Concerto | Non-prehensile | 3.13 | 1.65 | 1.56 | 2.90 | 0.39 | 7.56 |
| CORN | Non-prehensile | 46.63 | 3.15 | 45.83 | 5.51 | 22.22 | 17.43 |
| CORN-multi | Non-prehensile | 35.93 | 2.73 | 15.38 | 3.92 | 11.83 | 12.06 |
| UniCORN | Non-prehensile | 20.61 | 1.71 | 11.67 | 4.13 | 5.81 | 9.79 |
| DAPL | Non-prehensile | **71.88** | **2.59** | **51.04** | **2.7** | **44.56** | **12.65** |

因果解释：

- Sparse: DAPL 71.88 vs CORN 46.63，说明即便 clutter 低，dynamics representation 也给了更高 task success。
- Dense: DAPL 44.56 vs CORN 22.22，差距变大，说明 dynamics 的价值随 contact coupling 增强而增强。
- M.O. 不能只看越低越好。Point2Vec/Concerto M.O. 低是因为几乎不成功、少动；DAPL 同时保持最高 SR 和较低 disturbance，这才是“选择性接触”的证据。
- GraspGen + CuRobo Dense 只有 3.13，说明 prehensile collision-free pipeline 在 dense clutter 中不是主解。

### 3.3 Dynamics representation ablation: Table II

Sparse track ablation：

| Pretrain Task | Granularity | Velocity | Phys. | P.E. | S.R. | M.O. |
|---|---|---|---|---:|---:|---:|
| Reconstruction | Point-level | no | no | - | 11.75 | 1.31 |
| Reconstruction | Point-level | yes | yes | - | 29.63 | 2.63 |
| World Model | Object-level | no | no | 3.1 | 14.13 | 3.27 |
| World Model | Object-level | yes | yes | 3.2 | 16.88 | 3.84 |
| World Model | Point-level | no | no | 4.1 | 42.00 | 4.91 |
| World Model | Point-level | yes | no | 5.1 | 58.25 | 4.86 |
| World Model | Point-level | yes | yes | 4.6 | **71.88** | **2.59** |

Ablation 因果链：

| 改动 | 结果 | 因果机制 | 结论 |
|---|---|---|---|
| Reconstruction instead of dynamics | 11.75 / 29.63 SR | 静态重建学 shape，不学 contact outcome | 好 geometry latent 不等于好 manipulation latent |
| Object-level 6DoF world model | 14.13 / 16.88 SR | pose supervision 太粗，局部 contact propagation 被平均掉 | cluttered contact 需要 point-level supervision |
| Remove velocity | 71.88 → 42.00 when phys also absent; velocity-only path 58.25 | 缺少一阶运动状态，未来预测不满足 Markov | velocity 是 dynamics state，不是附加特征 |
| Remove physical features | 58.25 without phys vs 71.88 with phys | 不知道 mass/friction 等物理属性，无法判断重物 anchor / 轻物扰动 | physical prior 是 extrinsic dexterity 的条件变量 |
| No variance preservation | 论文说明会出现 near-zero velocity collapse | 大多数点静止，MSE 鼓励预测零速度 | $\mathcal{L}_{var}$ 是反 collapse 机制 |

这张表是论文最硬的理论证据。它证明 DAPL 的增益不是来自“点云 Transformer 更强”，而是来自 dynamics objective + physical features + point-level granularity 的合取。

### 3.4 Training efficiency and curriculum

Fig.4 显示 DAPL 在前 $10^4$ training iterations 内达到约 70% success rate，而 CORN/UniCORN 等几何表征收敛更慢或性能更低。这个趋势说明 dynamics representation 是 sample-efficiency prior：policy 不需要从 reward 中重新发现“推轻物会跑、推重物能撑住”。

Fig.7 curriculum 数字：

| Iteration | SR |
|---|---:|
| iter-0 | 61.3% |
| iter-1 | 62.8% |
| iter-2 | 65.1% |
| iter-3 | 71.8% |
| iter-4 | 70.2% |

因果解释：前几轮 policy 产生的 imperfect contact trajectories 让 world model 看到 task-relevant failures；到 iter-3 达峰，iter-4 略降说明 curriculum 不是无限增益，过多交替可能引入噪声或收益饱和。

### 3.5 Adaptive behavior: mass perturbation

论文固定同一初始/目标几何，只交换 pie 和 Pringles can 的质量：heavy = 100x，light = 0.1x。

| 情况 | policy 行为 | 机制解释 |
|---|---|---|
| Heavy pie, light can | 利用 pie 作 stable mechanical anchor，避开 light can | 重物高惯量，接触后稳定；轻物易被扰乱 |
| Light pie, heavy can | 转而利用 Pringles can 作 support，避开 now-light pie | 行为随物理属性而非几何位置变化 |

这组 qualitative 证据很重要，因为它排除了“policy 只是记住某个几何路线”的解释。相同几何、不同质量导致不同路径，说明 $m_i$ 的确进入策略决策。

### 3.6 Real-world experiments: Table III

真实系统：

| 项 | 设置 |
|---|---|
| Robot | Franka Research 3 |
| Cameras | three Intel RealSense |
| Segmentation/tracking | SAM2 initialization + XMem online tracking |
| Pose estimation | FoundationPose |
| Mass prior | GPT-5 zero-shot mass estimation |
| Velocity | temporal pose difference + EKF filtering |
| Sim-to-real | teacher-student distillation with Gaussian noise $\mu=0,\sigma=0.05$ |
| Safety/action mapping | action scale curriculum 0.1 → 0.01 + Cartesian clipping via Jacobian |
| Success | target pose error < 0.05 m and < 0.1 rad within 90 s |
| Trials | 10 scenes, 5 trials each |

Average result:

| Method | Avg SR | Mean execution time |
|---|---:|---:|
| Teleop / FACTR baseline | 52% | 55.9 s |
| DAPL | 48% | 42.6 s |

逐场景有输有赢：DAPL 在 S5/S6/S8 比 teleop 更高，在 S2 明显低。这意味着论文不能被解读为“超过人类”，而应解读为“接近 human teleoperation，且平均更快”。真实世界成功依赖感知、质量估计、velocity filtering 与 safe action mapping；这些工程条件必须被纳入复现实验。

### 3.7 Grocery retrieval application

Galbot G1 shelf grocery retrieval 展示的是系统整合价值：VLM planner (SoFar) 把自然语言命令转成 6D target poses；DAPL policy 作为 pre-grasping skill，把目标从 clutter 中滑出或重定向成可抓状态；下游 grasping module 完成抓取。

这不是主 benchmark 证据，而是应用 demo。它证明 DAPL 可作为“抓取前 rearrangement skill”，但没有提供与完整 VLA/GraspVLA 管线的严格对照实验。

## 4. 核心洞见

### 4.1 论文真正的 insight

DAPL 的真正 insight 是：**在 cluttered contact 中，表征的任务不是重建场景，而是预测 interaction outcome**。

这句话解释了所有设计：

- 加 mass/velocity，因为 outcome 取决于动力学状态；
- 用 point-level prediction，因为 outcome 从局部接触点传播；
- 用 variance regularization，因为少数运动点携带 outcome；
- 用 curriculum，因为 outcome distribution 由 policy 访问的 contact 决定；
- 用 frozen dynamics encoder，因为 RL 需要的是“接触后果先验”，不是从零通过 reward 发现物理。

### 4.2 为什么这个设计有效

它有效的机制链是：

$$
(p,m,v)\ \text{point cloud}
\rightarrow
\text{future point dynamics prediction}
\rightarrow
f_{dy}\ \text{encodes contact outcome}
\rightarrow
\pi_\phi \ \text{chooses useful vs harmful contacts}
\rightarrow
\text{extrinsic dexterity emerges}.
$$

实验正好沿着这条链验证：

- Table II 验证 $(p,m,v)$ 和 point dynamics 是必要输入/目标；
- Fig.7 验证 policy-induced data 能继续改善 $f_{dy}$；
- Fig.8 验证 $f_{dy}$ 真的影响 contact choice；
- Table I/III 验证这种 contact choice 提高 simulation/real performance。

### 4.3 什么时候会失效

DAPL 的失败边界也很清楚：

- 物理属性不可得或严重错误：mass/velocity 是核心输入，估计错会直接误导 contact choice；
- 非刚体/液体/布料：point velocity prediction 不再能由简单 rigid-body mass prior 支撑；
- 长程多阶段任务：DAPL 是 policy-level rearrangement skill，不含 high-level task decomposition；
- 高维灵巧手接触：Franka parallel/gripper-like EE 的 7D residual action 不等价于 20+ DoF 灵巧手；
- 遮挡导致 FoundationPose/segmentation drift：$v_i$ 和 $p_i$ 错会让 dynamics encoder 学/用错状态；
- sim physics 与真实接触摩擦差异大：teacher-student noise 能抗观测噪声，不等于解决系统性动力学 gap。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 为什么重要 | 对用户研究的含义 |
|---|---|---|
| $m_i=M/N$ 是粗 physical prior | 真实质量分布、惯量张量、摩擦、接触法向都被压缩 | 转笔需要质心/惯量/摩擦，而不只是 total mass |
| 点速度来自 pose difference | 遮挡/pose jitter 会放大 velocity noise | LinkerHand 应引入 tactile slip / visual-inertial filter |
| point-level world model 仍非显式接触模型 | 没有强制非穿透、摩擦锥、冲量守恒 | 高风险接触任务需 safety/contact consistency loss |
| dynamics encoder frozen during PPO | 表征不会被当前 policy gradient 端到端修正 | 优点是稳定，缺点是 task-specific adaptation 慢 |

### 5.2 算法维度

| 替代方案 | 优点 | 相对 DAPL 的问题 |
|---|---|---|
| PDDM-style online planning | 可显式评估 candidate action 后果 | real-time 成本高；DAPL 更适合作为 amortized policy |
| Geometry-only CORN/UniCORN | 简洁，不需要 mass/velocity | Dense clutter SR 明显掉；不能区分 anchor vs disturbance |
| End-to-end PPO | 无需预训练 world model | contact exploration 样本效率低，难学接触链 |
| Object-level pose dynamics | 状态紧凑 | Table II 证明太粗，Sparse SR 只有 16.88 |
| Diffusion/Flow action policy | 多模态动作表达强 | 仍需 dynamics-aware condition，否者可能生成几何合理但动力学错误的动作 |

### 5.3 工程/实验维度

- 真实世界使用 SAM2/XMem/FoundationPose/GPT-5/EKF，不是 raw point cloud 端到端。
- 人类基线是 teleoperation/FACTR-style，DAPL 平均成功率 48% 低于 52%，只是更快。
- Clutter6D 是 rigid tabletop object rearrangement，不覆盖 articulated/deformable/soft contact。
- 真实实验每个 scene 5 trials，规模仍有限。
- Galbot grocery retrieval 是 application demo，不是严格 benchmark。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移

DAPL 给 WMTS 的最直接启发是：world model 可以输出**任务条件化表征**而不直接 rollout。

| DAPL 组件 | WMTS 中的可迁移形式 | 具体实验 |
|---|---|---|
| $(p,m,v)$ physical point feature | hand-object-contact token: $(p,n,v,m,I,\mu,h_{tactile})$ | 比较 geometry-only vs dynamics-token policy |
| point-level future dynamics objective | ensemble world model 的 contact outcome prediction | 预测 3-5 steps 后接触点、slip、object twist |
| $\mathcal{L}_{var}$ anti-collapse | 稀疏 contact event 的 distribution preservation | 防止模型把所有 tactile/contact velocity 预测为 0 |
| frozen dynamics encoder -> PPO | PPO Oracle conditioned on learned contact latent | 让 PPO 不从零探索接触链 |
| curriculum with policy rollout | Solve/Probe/Reject loop | 用 policy 失败样本更新 world model blind spots |
| teacher-student under perturbation | sim privileged state -> real partial observation distillation | teacher 用 full sim state，student 用 tactile/vision/proprioception |

对 WMTS 最该保留的是“dynamics representation 作为 policy condition”。最不该照搬的是“把 task/goal 标签直接注入 dynamics model 让它学任务相关转移”。根据 WMTS 物理因果约束，dynamics encoder 应建模环境接触后果，task goal 进入 policy/query，而不是改写 physics。

### 6.2 对 LinkerHand / 转笔的具体改造

转笔的 DAPL-like representation 不能直接用 tabletop object point cloud；它应该变成 hand-object local contact field：

| DAPL 变量 | 转笔对应 | 必须新增 |
|---|---|---|
| object point $p_i$ | pen surface/contact candidate points | pen pose/axis/phase estimator |
| mass $m_i$ | pen mass distribution / center of mass / inertia | 不要只用总质量，需 $I$ 或至少 CoM offset |
| velocity $v_i$ | pen linear/angular velocity + fingertip relative velocity | high-speed vision / IMU / differentiable filter |
| EE point cloud | fingertip surface points | LinkerHand fingertip geometry + tactile taxels |
| obstacle point cloud | other fingers/palm/environment | non-contact fingers也可能成为未来 contact surface |
| point dynamics label | next pen twist/contact/slip | tactile slip and contact transition supervision |

一个可验证实验：

1. 在仿真中采集同一转笔任务的两类 observation：geometry-only hand/pen points vs dynamics-augmented points；
2. 预训练 world model 预测 $\Delta$ pen pose、pen twist、contact mode、slip event；
3. 用 frozen encoder 条件化 PPO Oracle；
4. 比较 sample efficiency、drop rate、contact transition success、sim-to-real robustness；
5. 加 ablation：去掉 angular velocity、去掉 tactile slip、object-level pose 替代 point/contact-level representation。

如果 dynamics-token PPO 明显降低 drop rate，而 geometry-only 只会学到局部推挤，这就说明 DAPL 的 insight 对转笔成立。

### 6.3 与当前知识库的组合

DAPL 可以和几条已有线组合：

| 相关 recap | 组合方式 |
|---|---|
| [[PapersRecap/Deep Dynamics Models for Learning Dexterous Manipulation|Deep Dynamics Models for Learning Dexterous Manipulation]] | PDDM 用 model 做 MPC；DAPL 用 model 做 representation，二者可构成 “planner teacher + policy condition” |
| [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]] | Tacmap 的 penetration map 可作为 DAPL 的 contact geometry/velocity 输入扩展 |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] | CGP 生成 contact-consistent action；DAPL 提供 contact outcome latent |
| [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] | CyberDemo 生成 physically plausible demos；DAPL 可筛选 demo 中的 dynamics-relevant contact patterns |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] | DexNDM joint-wise dynamics 可补 DAPL 缺少 actuator/joint dynamics 的部分 |

### 6.4 不应过度外推的点

- DAPL 是 Franka/tabletop clutter，不是多指手内操作。
- 论文依赖粗质量估计，但转笔对惯量和摩擦更敏感，粗 mass 可能不够。
- Real-world 48% 不是 production-level success；它仍低于 teleop 52%。
- Dynamics feature 解决的是 contact outcome prior，不解决 high-level task planning。
- 对 WMTS 来说，DAPL 应是 representation module，而不是替换 PPO Oracle 或 Diffusion generalist 的完整算法。

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

DAPL 把离散动力学从全局状态 $s$ 改写成点级物理场：

$$
X_t=\{(p_i,m_i,v_i)\}_{i=1}^{N}
\quad\Rightarrow\quad
\hat{X}_{t+\Delta t}.
$$

这不是严格 Newton-Euler，但它把 Newtonian 必要变量嵌入了学习表征：位置决定接触几何，质量决定冲量响应，速度决定一阶未来趋势。

### 7.2 与 [[ContactMechanics]] 的联系

Extrinsic dexterity 的核心不是“避免接触”，而是区分：

- useful contact：重物 anchor、pivot、barrier traversal；
- harmful contact：轻物扰动、contact chain 失控、目标卡住。

DAPL 的贡献是让 policy 从 dynamics feature 中学这个区分，而不是手写 contact mode rule。

### 7.3 与 [[RepresentationLearning]] 的联系

Table II 是 representation learning 的好范本：它没有只报告下游高分，而是比较了 pretext task granularity。结论非常清晰：

$$
\text{reconstruction} < \text{object-level dynamics} < \text{point-level dynamics + velocity + phys}.
$$

这说明好的 robot representation 不是“最通用的视觉特征”，而是与控制因果变量对齐的特征。

### 7.4 与 [[ReinforcementLearning]] 的联系

DAPL 是 representation-conditioned PPO：

$$
\pi_\phi(\Delta q_t\mid f_{dy}(P_t),s_{robot},g,a_{t-1}).
$$

它不是 model-based RL 的 planning 分支，而是“model-pretrained RL”。这和 WMTS 的 PPO Oracle 兼容：先用 dynamics encoder 提供 contact prior，再让 PPO 学 task-specific control。

### 7.5 与 [[ComputationalGeometry]] 的联系

Point-level representation 的必要性来自局部接触几何：6DoF pose 只描述刚体整体位姿，不能表达哪个边、角、曲面 patch 会接触并传递力。DAPL 的 point patches 保留了这些局部几何结构，再用 dynamics objective 把它们变成 action-relevant features。

> [!note] 簇内补链 · Foundation 精确锚点 · 暗线
> **簇内互链 + Delta**：
> - vs 阻抗/力控簇（[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]] / [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]] / [[Minimalist Compliance Control|MCC]]）：本簇多数论文解决"接触时**怎么施力/多软硬**"（$K(s)$、$m_a(s)$）；DAPL 解决更上游的"接触**后果**是什么"——用 $(p,m,v)$ point world model 预测 $v^+=v^-+J/m$，把接触结果编码成 policy 条件。二者串联：DAPL 选"碰谁"、阻抗控制器定"多软地碰"。
> - vs [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization|PhysicsGen]]：都强调"几何可行 ≠ 动力学可行"——PhysicsGen 用 trajopt 在**数据侧**保证动力学，DAPL 用 frozen dynamics encoder 在**表征侧**注入接触后果先验。
>
> **Foundation 精确锚点**：接触冲量 $v^+=v^-+J/m$、$\omega^+=\omega^-+I^{-1}(r\times J)$ = [[ContactMechanics#5.1 互补条件与 LCP 的构建|ContactMechanics §5.1]] 的接触动力学；$\Delta q_t$ 经 Jacobian clipping 后由阻抗执行 = [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|ControlTheory §3.2]]。
>
> **暗线 · 接触的非光滑性**：extrinsic dexterity 的本质是**选择性利用接触链**（推/滑/翻/借重物作 pivot），而 useful↔harmful contact 的分界正是接触把动力学撕成混合系统的地方——DAPL 让 policy 从 dynamics feature 学这个非光滑分界，而非手写 contact mode（[[ContactMechanics#6.1 不连续性的挑战|ContactMechanics §6.1]]）。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “DAPL 相比 CORN 到底多了什么？” | 不是只多 mass/velocity 输入，而是 dynamics pretext + point-level future prediction + policy conditioning；Dense SR 44.56 vs 22.22 是核心证据 |
| “为什么 object-level pose prediction 不够？” | Table II：object-level world model + velocity/phys 只有 16.88 SR；局部接触传播被 6DoF pose 平均掉 |
| “为什么速度方差正则重要？” | 大多数点静止，MSE 会让 $\hat{v}\to0$；variance/std matching 保留少数运动点的分布信号 |
| “真实世界是不是 zero-shot？” | policy sim-trained zero-shot deployed，但依赖 SAM2/XMem/FoundationPose/GPT-5 mass/EKF velocity/distillation/action clipping；不是无工程 sim-to-real |
| “对 WMTS 怎么用？” | 把 world model feature 作为 PPO/Diffusion condition；保持 dynamics task-agnostic，goal 进入 policy query |
| “对转笔能直接用吗？” | 不能直接用 tabletop point cloud；要改成 pen-finger-contact dynamics token，加入 angular velocity、tactile slip、inertia/CoM |
| “实验如何证明 story？” | Table I 证明 dense clutter 中 dynamics-aware policy 最稳；Table II 证明 dynamics pretext/velocity/phys/point-level 必要；Fig.8 证明质量改变会改变策略路径 |

## References

- [[PapersRecap/Deep Dynamics Models for Learning Dexterous Manipulation|Deep Dynamics Models for Learning Dexterous Manipulation]]
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]]
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]]
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]]
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]
