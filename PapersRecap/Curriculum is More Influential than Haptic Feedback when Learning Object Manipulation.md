---
tags:
  - paper
  - curriculum-learning
  - dexterous-manipulation
  - tactile-sensing
  - in-hand-manipulation
  - reinforcement-learning
aliases:
  - Curriculum > Haptic
  - Curriculum vs Haptic
  - Curriculum is More Influential than Haptic Feedback
paper-year: 2025
read-date: 2026-03-16
venue: Science Advances
paper-pdf: "[[Papers/Curriculum is more influential than haptic feedbackwhen learning object manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[RepresentationLearning]]"
---

# Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation

> [!abstract] 核心贡献
> 本文用一个受控的 $5\times2$ 因子实验表明：在 MuJoCo 三指手向下抓持球并学习 lift+rotate 的任务里，PPO 的 curriculum 设计比 fingertip 3D-force tactile information 更强地塑造学习路径和最终能力；但正确读法不是“触觉无用”，而是“在这个低维、仿真、球体、奖励可直接访问物体状态的任务中，课程是更强的 optimization prior，触觉的作用是改变路径和边界条件，而不是必然 gate 成功”。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#4. 策略梯度：在不可微世界中更新策略|ReinforcementLearning §4]]：curriculum 改变 reward，从而改变 advantage 与策略梯度方向。
> - [[ReinforcementLearning#5.1.2 PPO：用 clip 把硬约束"软化"|ReinforcementLearning §5.1.2]]：PPO 是本文默认 RL backbone；curriculum-based learning-rate scheduler 是围绕 PPO phase switch 做的优化。
> - [[ReinforcementLearning#8.2 奖励工程：最危险的自由度|ReinforcementLearning §8.2]]：本文最核心的变量不是传感器，而是 reward coefficients $c_R,c_L$ 的时间调度。
> - [[ContactMechanics#2.3 接触雅可比与对偶性：连接关节空间|ContactMechanics §2.3]]：无触觉仍可学习的原因之一是手部运动学和接触结果之间存在动力学耦合，但这不是完整接触可观测性的证明。
> **核心技术**: PPO, curriculum learning, reward scheduling, 3D fingertip force vs no-tactile, downward-facing in-hand manipulation, piecewise learning-rate scheduler.

---

## 0. 阅读定位与范本价值

这篇 paper 很容易被误读成一句标题党：“触觉不重要，课程更重要。”范本级 recap 必须更精确：

1. 它比较的不是所有 haptic feedback，而是**policy observation 中是否加入 fingertip 3D-force vector**。
2. 它的任务不是真实灵巧手转笔，而是**仿真三指手、向下抓持、球体被限制在 $x$-$z$ 平移 + $\theta_y$ 旋转**。
3. 它的核心贡献不是否定触觉，而是把 curriculum 解释成一种**会塑造 PPO 梯度场与 learning basin 的强先验**。
4. 它和 HATO / Touch Dexterity / AnyRotate 形成张力：那些论文显示触觉在 rare contact state、真实部署、接触相位中关键；本文显示在某些低维受控任务中，好的课程能让本体/运动学信息承担更多工作。

| 范本要求 | 本文应回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么“课程 > 触觉”是一个有价值但不能过度外推的结论？ | §1 拆出任务约束、传感定义和 story 边界 |
| 原理与理论 | curriculum 如何进入 PPO？为什么它能改变学习终点？ | §2 从 MDP、PPO、reward coefficients、gradient vector field 推导 |
| 实验与验证 | C1-C5、no-tactile vs 3D-force、60 trials、2000 episodes、Fig.2-7 如何支持 claim？ | §3 用实验矩阵、learning path、scheduler 和 object generalization 串证据 |
| 未来与结合 | 对 LinkerHand 转笔/WMTS 的启发是什么，什么地方不能照搬？ | §5-7 给出课程设计、触觉 ablation 和 PPO Oracle 迁移 |

---

## 1. 问题设定与动机

### 1.1 一句话核心

本文的核心是：在一个可控的仿真 in-hand manipulation 任务里，课程不是“训练技巧”，而是决定 PPO 先进入哪个技能 basin 的结构先验；相比之下，3D-force tactile information 只是在某些 curriculum 和 object condition 下改变路径，而不是稳定主导最终性能。

### 1.2 直观隐喻

同一个“多能”的初始学生可以被不同训练路线塑造成不同选手：先练稳定托举，会更偏向保持高度；先练旋转，会更偏向滚动；一开始同时练 lift+rotate，反而不一定比“先单目标再复合”更难。

触觉在这个故事里像额外辅导资料：它能改变学习路径，但如果课程本身把学生推向了某个山谷，辅导资料未必能把他带到另一个山谷。

这个隐喻的可证伪点是：

- 如果课程只是加速器，最终 endpoint 应该趋同；论文显示不同 curriculum 有不同 endpoint。
- 如果触觉是必要条件，no-tactile 条件应无法学会；论文显示 no-tactile 也能学习 lift+rotate。
- 如果触觉总是有益，3D-force 应在所有 C1-C5 中占优；论文显示并不一致，cube 上才更显出触觉价值。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| 传统接触/控制理论 | 精确动力学、接触模型、稳定性条件 | 难处理 intermittent/deformable contact、摩擦不确定和多指协调 |
| 视觉主导的 RL manipulation | object pose 可观测、视觉闭环 | 计算重、遮挡敏感；很多工作依赖 upward-facing palm 或视觉 tracking |
| 触觉优先观点 | 认为 fine manipulation 需要 tactile feedback | 容易把“触觉在人类/真实任务中重要”外推成“每个 RL 学习任务都必须有触觉” |
| 传统 progressive curriculum | 从单目标/简单任务逐步到复合任务 | 假设“先简单后复杂”总是最好，未检查 multiobjective-first 是否更优 |
| 只比较最终成功率 | endpoint 作为唯一证据 | 忽略 learning path：同样终点可能来自不同机制，不同 curriculum 可能塑造不同技能组合 |

### 1.4 Delta 分析

| 维度 | 常见做法 | 本文增量 | 真正 value add |
|---|---|---|---|
| 研究问题 | 证明加触觉/加视觉提升操作 | 正交比较 curriculum 和 tactile condition | 把“训练经验”与“传感能力”拆成两个可实验变量 |
| 任务设置 | upward palm / 物体有支撑 / 视觉可用 | downward-facing hand, gravity always matters, no direct vision | 更接近动态 prehensile manipulation，而不是静态 grasp |
| Curriculum | 单一 reward 或渐进式直觉设计 | 5 种 L/R 两阶段课程：C1-C5 | 显示 curriculum 不只加速，还改变最终 skill trade-off |
| Tactile | 默认视为必要输入 | no-tactile vs 3D-force fingertip sensing | 给出“无触觉也可学”的 existence proof |
| PPO schedule | 普通 constant / linear LR | reward switch 时 piecewise LR reset/decay | 将 learning-rate schedule 与 curriculum phase 对齐 |
| 解释框架 | 工程调参 | Waddington Landscape 类比 | 把 curriculum 解释成从 pluripotent 初态进入不同 basin 的发育路径 |

---

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_1,\dots,q_6$ | 6 joint angles | simulated hand state | 否，observation | 三指手每指 2 个 flexion/extension joints | 三指手，不是 Allegro/Shadow/LinkerHand |
| $\dot q_1,\dots,\dot q_6$ | 6 joint velocities | simulated hand state | 否 | 手指角速度 | no-tactile 时这是接触结果的重要间接线索 |
| $z_h,\dot z_h$ | 2 scalars | palm vertical actuator state | 否 | 手掌高度及速度 | 论文 reward 里写 $z_h$，但 lift metric 语义指向 ball desired height |
| $s_b$ | 6D | simulator ball state | 奖励计算用 | 球的 $x,z,\theta_y$ 及速度 | policy observation 并不等价于完整 ball state |
| $s_{h,f}$ | null or $\mathbb{R}^{9}$ | tactile condition | 否，observation | 三个 fingertip 的 3D force | 每指 3 维：两个 tangential + 一个 normal |
| no-tactile | $s_{h,f}=0$ | ablation condition | 否 | policy 没有 fingertip force 输入 | 不是没有接触物理，MuJoCo 仍有接触动力学 |
| 3D-force | $\mathbb{R}^{9}$ | MuJoCo force sensors | 否 | fingertip tactile information | 是 idealized simulated force，不是真实噪声触觉 |
| $R$ | scalar | reward | 否 | rotation objective | 论文中 $R$ 既可能指 rotation，也可能指 reward，需看上下文 |
| $L$ | scalar objective | reward component | 否 | lift objective / height penalty | $L$ 不是 loss function |
| $c_R,c_L$ | coefficients | curriculum schedule | 否 | 激活 rotation/lift 的 reward 权重 | curriculum 的真正控制旋钮 |
| $r_t^{\mathcal C}$ | scalar | reward at step $t$ | 否 | 当前 curriculum 下的 PPO reward | 改变 $c_R,c_L$ 就改变 advantage |
| $\pi_\theta$ | policy | PPO actor | 是，参数 | 输出 hand/palm action | PPO 参数带梯度，rollout 数据不带梯度 |
| $V_\phi$ | value function | PPO critic | 是，参数 | 估计 return / advantage | critic 也受 curriculum reward 影响 |
| $e$ | episode index | training loop | 否 | 1-2000 episodes | curriculum phase 在 1000 episodes 切换，不是按成功率切换 |
| $n$ | sample number | LR scheduler | 否 | piecewise LR 的横轴 | $n=1{,}000{,}000$ 对应 phase switch |

### 2.2 从 MDP 开始：触觉和课程分别改了什么

标准强化学习问题可以写成 MDP：

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},P,r,\gamma)
$$

policy 的目标是最大化：

$$
J(\theta)=
\mathbb{E}_{\tau\sim \pi_\theta}
\left[
\sum_{t=0}^{T}\gamma^t r(s_t,a_t)
\right]
$$

本文比较的两个因素分别作用在不同位置。

**触觉信息**改变 observation：

$$
o_t^{no\ tactile} =
\left[
q_t,\dot q_t,z_{h,t},\dot z_{h,t}
\right]
$$

$$
o_t^{3D-force} =
\left[
q_t,\dot q_t,z_{h,t},\dot z_{h,t},s_{h,f,t}
\right]
$$

其中：

$$
s_{h,f,t}=
\left[
f_{t1}^{(1)}, f_{t2}^{(1)}, f_n^{(1)},
f_{t1}^{(2)}, f_{t2}^{(2)}, f_n^{(2)},
f_{t1}^{(3)}, f_{t2}^{(3)}, f_n^{(3)}
\right]
\in\mathbb{R}^{9}
$$

**课程**改变 reward：

$$
r_t^{\mathcal{C}}=
c_R^{\mathcal{C}}(e)\dot{\theta}_{y,t}
-
c_L^{\mathcal{C}}(e)\left|z_{h,t}-z_d\right|
$$

论文中的公式写的是：

$$
Reward_t = c_R \dot{\theta}_{y,t} - c_L |z_{h,t}-z_d|
$$

并给出基础权重：

$$
c_R=0.51,\qquad c_L=0.49
$$

这里有一个重要符号陷阱：正文说 desired height 是 ball center 的目标高度，结果指标也是 ball height 是否在 $[21,29]$ mm 范围内；但公式里写成 $z_h$。我不擅自改写论文符号，而是把它理解为“height penalty term”，并在使用时说明它对应 lift objective。

关键在于：触觉改变的是输入空间，课程改变的是 reward landscape。对 PPO 来说，后者会直接改变 advantage。

### 2.3 PPO 中 curriculum 如何改变梯度方向

PPO 的 clipped surrogate objective 可写成：

$$
L^{CLIP}(\theta)=
\mathbb{E}_t
\left[
\min
\left(
\rho_t(\theta)\hat A_t,
\mathrm{clip}(\rho_t(\theta),1-\epsilon,1+\epsilon)\hat A_t
\right)
\right]
$$

其中：

$$
\rho_t(\theta)=
\frac{\pi_\theta(a_t\mid o_t)}
{\pi_{\theta_{old}}(a_t\mid o_t)}
$$

advantage 由当前 reward 决定。用一阶 TD 写：

$$
\hat A_t^{\mathcal C}
\approx
r_t^{\mathcal C}
\gamma V_\phi(o_{t+1})
-V_\phi(o_t)
$$

代入 curriculum reward：

$$
\hat A_t^{\mathcal C}
\approx
c_R^{\mathcal C}(e)\dot{\theta}_{y,t}
-
c_L^{\mathcal C}(e)|z_{h,t}-z_d|
\gamma V_\phi(o_{t+1})
-V_\phi(o_t)
$$

所以 C1-C5 不是标签不同，而是每个 phase 里把“哪些 action 被 advantage 加强”改掉了。

策略梯度近似为：

$$
\nabla_\theta J_{\mathcal C}(\theta)
\approx
\mathbb{E}
\left[
\nabla_\theta\log\pi_\theta(a_t\mid o_t)
\hat A_t^{\mathcal C}
\right]
$$

当 $c_R=0,c_L=0.49$ 时，梯度主要强化维持高度；当 $c_R=0.51,c_L=0$ 时，梯度主要强化旋转；当两者都开时，梯度强化能同时带来旋转和高度接近目标的动作。

这就是 Waddington Landscape 类比的数学版本：

$$
\frac{d\theta}{d\eta}
\approx
\nabla_\theta J_{\mathcal C_e}(\theta)
$$

不同 curriculum schedule $\mathcal C_e$ 在前 1000 episodes 和后 1000 episodes 施加不同向量场。由于 neural policy optimization 是非凸的，早期向量场会把参数推入不同 basin；后续 reward switch 不一定能完全离开这个 basin。

### 2.4 C1-C5：课程定义不是“先简单后复杂”这么粗

每个 trial 2000 episodes，每个 episode 10 s。前 1000 episodes 是 phase 1，后 1000 episodes 是 phase 2。

| Curriculum | Phase 1 | Phase 2 | 系数写法 |
|---|---|---|---|
| C1 | Lift only | Lift + Rotation | $[L\mid L+R]$ |
| C2 | Rotation only | Lift + Rotation | $[R\mid L+R]$ |
| C3 | Lift + Rotation | Lift + Rotation | $[L+R\mid L+R]$ |
| C4 | Lift + Rotation | Rotation only | $[L+R\mid R]$ |
| C5 | Lift + Rotation | Lift only | $[L+R\mid L]$ |

这个设计故意测试两个问题：

1. **single-objective first 是否必然更好？** C1/C2 先学单项，再学组合。
2. **multiobjective first 是否会过难？** C3/C4/C5 一开始就同时奖励 lift 和 rotation。

论文的反直觉结果是：一开始奖励 lift+rotation 并不一定阻碍学习，反而能让 C4/C5 在第二阶段更好地 transfer/adapt 到单项技能；而 C1/C2 这种只奖励单项起步的课程，在第二阶段学习另一个 skill 时反而不够高效。

### 2.5 为什么 no-tactile 也能学：不是“无接触”，而是“无显式触觉观测”

no-tactile 条件下，MuJoCo 仍然有接触动力学。agent 只是没有 fingertip force vector 输入。它还能看到手部关节角/角速度、palm position/velocity 等本体状态。

从接触力学看，接触会通过动力学影响关节状态：

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)
=
\tau+J_c(q)^\top\lambda
$$

即使 policy 不直接观测 $\lambda$，接触是否发生、是否稳定，仍可能通过 $q,\dot q,z_h,\dot z_h$ 和 reward 反馈间接影响学习。再加上本文任务有强约束：

- object 是球，主实验 50 g / 35 mm radius；
- ball motion 被限制为 $x,z$ 平移和 $\theta_y$ 旋转；
- reward 直接基于高度和旋转；
- 环境是仿真，接触/摩擦没有真实传感噪声和延迟；
- 每个 curriculum 有 60 independent trials。

因此，no-tactile 可以学习是一个重要 existence proof，但不是“真实灵巧操作不需要触觉”的普遍定理。

### 2.6 Curriculum-based learning-rate scheduler

普通 linear LR 在整个训练中一路衰减，会遇到一个问题：当第 1000 episodes reward 改变时，学习率可能已经太低，policy 难以适应新 objective。

本文使用 piecewise schedule，在 phase switch 处重新给第二阶段足够学习率：

$$
LR(n)=
\begin{cases}
\phi\left(1-\frac{n}{1{,}000{,}000}\right), & n\leq1{,}000{,}000\\
\eta\left(1-\frac{n}{2{,}000{,}000}\right), & n>1{,}000{,}000
\end{cases}
$$

经验参数：

$$
\phi=1,\qquad \eta=0.98
$$

注意这里是 normalized schedule，实际优化器学习率由实现再缩放。机制上，它让第一阶段探索/收敛后，在 reward switch 时给第二阶段重新学习的能力。

论文在 C5 $[L+R\mid L]$ 上比较 scheduler，successful trials 中 reward switch 后达到目标高度的平均收敛 episode 数：

| Scheduler | Convergence after reward switch |
|---|---:|
| Constant learning rate | about 1000 episodes |
| Linear learning rate | about 450 episodes |
| Piecewise curriculum-based LR | about 250 episodes |

这说明 curriculum 的效果不只来自 reward 设计，也和 optimizer schedule 配套。换 reward 但不重置学习能力，可能会把“课程不好”误判成“策略能力不足”。

---

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 论文设置 |
|---|---|
| Simulator | MuJoCo |
| Robot hand | bio-inspired three-finger hand, each finger 2 joints |
| Palm motion | vertical palm actuator $z_h$ |
| Main object | ball, 50 g, 35 mm radius |
| Object DOF | constrained to $x,z$ translation + $\theta_y$ rotation |
| Orientation | downward-facing hand, object must be held against gravity |
| Algorithm | PPO actor-critic |
| Trial length | 2000 episodes |
| Episode length | 10 s |
| Simulated time per trial | 5 h 33 min |
| Curriculum switch | after 1000 episodes |
| Tactile conditions | no-tactile vs 3D-force |
| Trials | 60 independent trials per curriculum per tactile condition |
| Main factorial design | 5 curricula × 2 tactile conditions × 60 trials = 600 runs |

Evaluation metrics：

| Metric | 定义 |
|---|---|
| Lift success | final 10 s 中 ball 在 desired height range $[21,29]$ mm 的时间比例 |
| Mean height | ball height trajectory mean |
| Rotation | completed rotations; Fig.2 中 negative rotations set to zero |
| Cumulative reward | Eq.1 reward over episode/training |

### 3.2 Curriculum 主效应：路径和终点都被改变

Fig.2 把每个 curriculum 的 learning path 画成“lift success vs completed rotations”的轨迹，每个点是 60 trials 的均值，并标注 episode 50/100/250/1000/1250/2000。

关键观察：

| 观察 | 机制解释 |
|---|---|
| 不同 curriculum 走向不同 endpoint | 早期 reward 改变 PPO 梯度方向，把 policy 推入不同 basin |
| 多数技能在每个 phase 的前 250 episodes 内快速变化 | curriculum effect 很早形成，不只是最后慢慢收敛 |
| C3 $[L+R\mid L+R]$ 第二阶段趋于饱和 | 同一 reward 持续训练时，固定容量 PPO 难继续吸收新能力 |
| C4/C5 从 $L+R$ 切到单项后，能保留部分未奖励技能 | 存在 transfer/adaptation，未出现完全 catastrophic forgetting |
| C1/C2 先单项后组合，学习第二技能不如直觉预期高效 | “先简单后复杂”不是普遍最优 |

**因果解释**：

这支持 Pillar-1 的核心 story：curriculum 不只是降低难度的脚手架，而是决定最终技能组合的路径约束。一个从 $L$ 开始的 policy，早期会强化“保持球在目标高度”的动作；一个从 $R$ 开始的 policy，会强化“让球转起来”的动作；一个从 $L+R$ 开始的 policy，会更早接触两者 trade-off。后续 reward switch 是在已有策略分布上微调，不是在空白状态重来。

### 3.3 Tactile 结果：不是必要条件，但会改变路径

论文最反直觉的结果是：no-tactile 条件也能学习 manipulation，3D-force 不总是更好。

具体 nuance：

| Curriculum / 情况 | tactile effect |
|---|---|
| C1 $[L\mid L+R]$ | 3D-force 在最终 lift 上比 no-tactile 更好 |
| C3 $[L+R\mid L+R]$ | no-tactile 在 lift 上反而比 3D-force 更有效 |
| C4 $[L+R\mid R]$ | tactile information 对 endpoint 影响不大 |
| C5 $[L+R\mid L]$ | tactile information 对 endpoint 影响不大 |
| Cube supplementary | no-tactile 的 cumulative reward 低于 3D-force，差异更明显 |

**因果解释**：

3D-force 增加了 observation 信息，但也增加了输入维度和需要学习的映射。若任务可以通过手部运动学和 reward feedback 学到，额外 tactile 未必带来稳定收益；若形状更复杂，例如 cube，接触位置/力方向更难从运动学间接推断，触觉的边际价值就上升。

所以本文对触觉的结论应写成：

> 在受控球体任务中，触觉不是学习的必要门槛；但 tactile condition 会改变 learning path，而且在更复杂形状上可能更重要。

这和 HATO 的 Table II/III 并不矛盾。HATO 处理真实双手 tool-use 和 rare initialization，触觉在关键接触相位决定 success；本文处理仿真低维球体，课程对 basin 的作用更强。

### 3.4 Scheduler ablation：课程需要优化器配合

Fig.7 在 C5 $[L+R\mid L]$ 上比较三种 learning-rate schedule 的 mean height：

| Scheduler | Mean-height behavior | Convergence number reported |
|---|---|---:|
| Constant LR | 长期低于 desired height，学习慢 | about 1000 episodes |
| Linear LR | 比 constant 好，但 reward switch 后适应仍慢 | about 450 episodes |
| Piecewise LR | 最接近 desired height，reward switch 后最快适应 | about 250 episodes |

**因果链**：

`reward changes at episode 1000 -> old gradient target no longer matches new objective -> if LR already decayed too much, policy cannot adapt -> piecewise LR resets second-phase plasticity -> faster convergence`

这对用户非常重要：如果 WMTS/PPO Oracle 使用 curriculum，但 optimizer schedule 没有配合 phase switch，就可能误判 curriculum 设计，而实际问题是学习率太低或策略容量饱和。

### 3.5 Object generalization：球体上结论稳，cube 暴露触觉边界

论文还测试了四种球：

| Weight | Radius |
|---:|---:|
| 50 g | 35 mm |
| 50 g | 30 mm |
| 5 g | 35 mm |
| 5 g | 30 mm |

总体结论：不同 weight/size 下，learning paths 和 reward switch effect 保持一致，说明 curriculum effect 不是单一球参数的偶然。

更关键的是补充实验中的 soft ball 和 cube：

- soft ball / balls：curriculum pattern 仍大体保持；
- cube：no-tactile 的 cumulative reward 更低，3D-force 的优势更明显，且两种 tactile condition 下 reward dispersion 都更大。

**因果解释**：

球的接触几何更规则，旋转与高度控制可以通过运动学和 reward feedback 学到；cube 的接触法向、边角、姿态变化更复杂，接触状态更难被本体感知间接推断，因此 tactile information 更可能成为瓶颈。

这正是本文不能外推成“触觉不重要”的核心证据。

### 3.6 和 state of the art 的定位

论文强调它做的是 dynamic dexterous manipulation，而不是 grasp 或 pick-and-place：

- downward-facing hand；
- object always at risk of falling；
- full gravity from start；
- no direct vision；
- curriculum learning over lift/rotation objectives；
- PPO model-free RL，而不是 demonstration-heavy imitation。

这个定位的 value 在于：它把“grasp”与“manipulation”切开。抓住一个物体不是 dexterous manipulation；在重力下持续改变物体状态，同时保持不掉落，才是本文要讨论的技能。

---

## 4. 核心洞见

### 4.1 论文真正的 insight

本文真正的 insight 是：

> 在接触丰富 RL 中，课程是一个会改变策略发育轨迹的 optimization prior；传感器是 observation prior。两者不是同一类变量，所以不能只问“加触觉是否提升平均性能”，还要问“课程把策略推向了哪个 basin，触觉在那个 basin 中是否有边际价值”。

这比“课程更重要”更准确。

### 4.2 为什么 curriculum 会比 tactile 更强

在本文任务中，curriculum 更强有三个原因：

1. **直接作用于 reward/advantage**：$c_R,c_L$ 改变每一步 PPO 更新的方向。
2. **早期路径依赖**：前 250 episodes 内 skill trajectory 已经明显分化，后续优化在已有 basin 中进行。
3. **任务低维且仿真可控**：球体 + constrained DOF + clean dynamics 让无触觉 policy 可以通过运动学和 reward feedback 学到有效动作。

触觉只改变 observation，如果 reward/任务结构本身已经让 policy 找到可行解，额外 observation 未必能改变 basin。

### 4.3 什么时候触觉会重新成为瓶颈

| 条件 | 为什么触觉更可能关键 |
|---|---|
| cube / non-spherical / pen-like object | 接触法向和边角状态难从本体间接推断 |
| real hardware | 摩擦、传感噪声、执行器延迟和接触模型误差破坏仿真规律 |
| high-speed release/catch | 接触事件短，运动学滞后，必须直接感知接触相位 |
| partial observability stronger | 无法从 reward 或 kinematics 间接恢复物体状态 |
| task requires slip control | 3D-force 甚至还不够，需要 shear/slip/contact patch |
| online recovery | 失败边界处的 correction 依赖触觉反馈 |

---

## 5. 替代方案与理论局限

### 5.1 理论维度

本文的 Waddington Landscape 类比很有启发，但不是严格定理。若要数学化，需要把 curriculum 看成时间变化的目标函数：

$$
J_{\mathcal C_e}(\theta)
=
\mathbb{E}_{\tau\sim\pi_\theta}
\left[
\sum_t \gamma^t r_{\mathcal C_e}(s_t,a_t)
\right]
$$

策略更新是非自治动力系统：

$$
\theta_{k+1}
=
\theta_k+\alpha_k
\widehat{\nabla_\theta J_{\mathcal C_e}}(\theta_k)
$$

不同 curriculum 的本质差异是 $\mathcal C_e$ 的序列不同。要预测哪个 curriculum 最好，仅靠 Waddington 隐喻不够，需要分析：

- reward components 是否冲突；
- early phase 是否覆盖后续 phase 的必要状态分布；
- policy capacity 是否会饱和；
- phase switch 时 optimizer 是否仍有足够 plasticity；
- observation 是否足以区分关键状态。

### 5.2 算法维度

| 替代方案 | 可能优势 | 本文未覆盖的问题 |
|---|---|---|
| automatic curriculum learning | 不手工枚举 C1-C5 | 如何定义搜索空间和安全约束 |
| self-paced curriculum | 根据 learning progress 自适应切换 | 本文固定 1000 episodes switch，可能浪费训练 |
| task generator / PLR / POET | 自动发现难度递增任务 | 本文只在 lift/rotation 两个子目标内变化 |
| multi-objective RL / Pareto front | 显式处理 lift-rotation trade-off | 本文用线性 reward 加权，未画 Pareto frontier |
| recurrent policy / belief state | 在 no-tactile 下利用历史推断接触 | 本文重点不在 memory architecture |
| model-based RL | 规划不同 curriculum 的可达性 | 本文用 model-free PPO，不解释 dynamics |

### 5.3 工程/实验维度

1. **Simulation only**：MuJoCo 接触比真实触觉/执行器干净，不能替代真机证据。
2. **三指手低维**：每指 2 joints + palm vertical actuator，远低于 LinkerHand/Shadow 的策略空间。
3. **对象运动被约束**：球被限制在 $x,z,\theta_y$，不是完整 6-DoF free object。
4. **触觉是 idealized 3D-force**：没有真实传感器噪声、漂移、校准、latency、contact patch 形变。
5. **无视觉是人为设置**：论文证明“无 direct vision 也能在该任务学”，不是证明视觉不重要。
6. **curriculum 手工枚举**：只测试 5 种 reward sequence，不能保证最优。
7. **reward uses privileged object state**：学习时 reward 知道 ball height/rotation，真实系统如何稳定获得这些量仍是工程问题。
8. **标题中的 haptic feedback 容易误导**：本文不是给人类操作者 force feedback，而是给 RL policy 添加 fingertip force observation。

---

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / DNPM 转笔的直接迁移

这篇 paper 对转笔最重要的启发不是“少用触觉”，而是：**课程顺序是一个和传感器同等甚至更基础的实验变量，必须显式设计和消融。**

| 本文变量 | 转笔对应变量 | 迁移建议 |
|---|---|---|
| Lift $L$ | 保持笔不掉、维持可控接触高度/姿态 | 作为 early safety curriculum，但不能长期只训练 hold |
| Rotation $R$ | 笔绕目标轴角速度/圈数 | 不能太晚引入，否则 policy basin 可能过度保守 |
| C1 $[L\mid L+R]$ | 先稳定夹持，再加入旋转 | 安全但可能抑制 release/recontact |
| C2 $[R\mid L+R]$ | 先追求旋转，再补稳定 | 可能学会甩动但掉笔率高 |
| C3 $[L+R\mid L+R]$ | 从一开始 joint reward | 可作为 baseline，不应默认过难 |
| C4 $[L+R\mid R]$ | 先完整任务，再专门放大旋转 | 可用于提升转速，但可能牺牲稳定性 |
| C5 $[L+R\mid L]$ | 先完整任务，再专门恢复稳定 | 可用于 fine-tune 抓回/接住能力 |
| no-tactile vs 3D-force | no tactile / binary tactile / full tactile | 不要只做有无触觉；要看不同 curriculum 下触觉是否改变 basin |

一个更适合 DNPM 的 reward family：

$$
r_t =
c_\omega \omega^{pen}_t
c_s \mathbb{1}[\text{no drop}]
c_c \mathrm{ContactPhaseScore}_t
-c_d d(\text{pen pose}, \text{target manifold})
-c_u\|a_t\|^2
$$

curriculum 不只是调权重大小，而是调哪些项在什么时候激活：

| Curriculum phase | 激活项 | 目的 |
|---|---|---|
| Phase A | no drop + canonical grasp | 学会不掉笔 |
| Phase B | no drop + small angular progress | 学会慢速可控滚动 |
| Phase C | angular velocity + contact phase | 学会指间相位切换 |
| Phase D | recovery + random perturbation | 学会失败边界修正 |
| Phase E | speed/generalization | 学会不同笔、不同初始相位 |

### 6.2 对 WMTS 五模块的具体接法

WMTS pipeline：latent task generation → PPO Oracle specialist → Diffusion/Flow generalist → Ensemble World Model → real robot fine-tuning。

| WMTS 模块 | 本文启发 | 具体改造 |
|---|---|---|
| latent task generation | 任务不是静态采样点，而是 curriculum path | 生成 task sequence，而不是单个目标 |
| PPO Oracle specialist | PPO 对 reward schedule 高度敏感 | 每个 Oracle 训练必须记录 curriculum ID 和 phase |
| Diffusion/Flow generalist | demonstration distribution 受 curriculum 塑造 | 蒸馏时把 curriculum phase/contact phase 作为 condition 或 metadata |
| Ensemble World Model | 区分“任务太难”和“观测不够” | 对 no-tactile vs tactile 的 transition uncertainty 做对比 |
| real robot fine-tuning | phase switch 需要 optimizer plasticity | 真机 fine-tune 时可借 piecewise LR / KL reset |

一个直接可用的 WMTS 实验 formulation：

$$
\mathcal{D}_{oracle}
=
\left\{
(o_t,a_t,r_t,z^{curr},\phi^{phase},h^{tactile}_t)
\right\}
$$

其中 $z^{curr}$ 是 curriculum identity，$\phi^{phase}$ 是当前任务阶段。训练 generalist 时比较：

1. 不给 $z^{curr},\phi^{phase}$；
2. 给 $z^{curr}$；
3. 给 $\phi^{phase}$；
4. 给两者 + tactile。

如果 2/3/4 明显提升，说明 curriculum 不只是训练过程变量，而是策略分布中的隐变量。

### 6.3 可验证实验建议

| 实验 | 条件 | 关键指标 | 能证伪什么 |
|---|---|---|---|
| 转笔 $5\times3$ factorial | 5 curricula × {no tactile, binary tactile, full tactile} | success、drop rate、completed rotations、contact phase F1 | 检验 curriculum 是否比 tactile 更主导 |
| Phase switch LR ablation | constant / linear / piecewise LR | switch 后恢复 episode、PPO KL、success | 检验 scheduler 是否影响 curriculum 结论 |
| Object shape boundary | ball-like pen cap / cylinder pen / hex pen / cube | tactile marginal gain | 检验“触觉在复杂形状更重要” |
| No-tactile hidden contact test | 禁用 tactile 但保留/去除 actuator torque/proprio | success + uncertainty | 检验本体是否间接编码接触 |
| Curriculum metadata distillation | generalist with/without curriculum phase | imitation loss + rollout success | 检验 curriculum 是否成为 latent mode |

### 6.4 不应过度外推的点

- 不要用本文否定 HATO/Touch Dexterity/AnyRotate 中触觉的价值；那些任务的接触复杂度和真实噪声完全不同。
- 不要把“no-tactile 可以学”理解成“无接触信息可以学”。no-tactile 仍有手部运动学、奖励反馈和仿真接触动力学。
- 不要默认“先稳定再旋转”就是最优转笔 curriculum；本文反而提醒 multiobjective-first 可能更好。
- 不要把 Waddington Landscape 当作数学证明；它是解释路径依赖的隐喻。
- 不要忽略 reward privileged information：真实转笔如何获得 pen height/orientation/rotation，需要视觉/触觉/状态估计解决。

---

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

本文是 PPO + reward engineering 的强案例。它说明在接触任务中，reward coefficients 的时间调度会改变策略梯度：

$$
\nabla_\theta J_{\mathcal C}(\theta)
\propto
\mathbb{E}
\left[
\nabla_\theta\log \pi_\theta(a_t\mid o_t)
\left(
c_R\dot\theta_y-c_L|z_h-z_d|
\right)
\right]
$$

因此 curriculum 不是训练外壳，而是目标函数本身的一部分。对 WMTS/PPO Oracle，必须把 curriculum 作为实验变量记录，而不是只记录最终 reward。

### 7.2 与 [[ContactMechanics]] 的联系

本文的 no-tactile 结果不能解释为“接触力学不重要”。接触力仍在 MuJoCo dynamics 中决定状态转移：

$$
s_{t+1}\sim P(s_{t+1}\mid s_t,a_t;\lambda_t)
$$

no-tactile 只是不把 $\lambda_t$ 直接给 policy。policy 仍然可以通过接触后的运动学变化和 reward 反馈学到策略。真正的边界是 cube：当接触几何更复杂，no-tactile 的 reward 更低，说明直接接触观测的边际价值上升。

### 7.3 与 [[RepresentationLearning]] 的联系

本文和 visuotactile representation papers 的关系是反向校准：

- HATO / Visual-tactile Pretraining 强调触觉输入能改善真实策略；
- 本文强调在某些任务里，representation 增量不如 reward/curriculum 增量大；
- 因此知识库里不应形成“多模态一定赢”的单调叙事。

更准确的判断式是：

$$
\Delta Performance
=
f(\text{task geometry},\text{partial observability},\text{reward path},\text{sensor reliability})
$$

触觉只是其中一项。

### 7.4 与相关 recaps 的张力图

| 相关 recap | 支持/张力 |
|---|---|
| [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] | HATO 显示触觉在 rare init / Steak Serving success 中关键；本文说明这依赖任务边界 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | Touch Dexterity 是“触觉足以支撑旋转”的证据；本文是“课程可降低触觉必要性”的证据 |
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | AnyRotate 的真实触觉 sim-to-real 与本文仿真 3D-force 形成现实差距 |
| [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] | 两者都说明课程可以塑造 sensing dependence；CSR 更接近 sim-to-real sensing reduction |
| [[Lessons from Learning to Spin Pens]] | 转笔任务更高速、非球体、接触相位更尖锐，不能直接套用“触觉不必要” |

---

### 7.5 课程学习簇坐标：curriculum 是 basin 选择器，也是 continuation 的一支

> [!abstract] 暗线锚定：Continuation + 认知不确定性（basin↔该学处）
> 本文的 C1–C5（两阶段 $c_R,c_L$ 时序）是 continuation 暗线的一个特例：不同 phase-1 reward 把 PPO 早期梯度推入不同 basin（§2.3），本质是"先解某个平滑子目标、再引入复合难度"。但本文给出一个**反直觉修正**：continuation 未必"先简单后复杂"最优——multiobjective-first（C3/C4/C5）反而常优于 single-objective-first（C1/C2）。这提醒 [[Curriculum Learning#3.2 与 Continuation Method 的联系|Bengio 2009 的 $Q_0\to Q_1$]] 单调难度假设有边界。而"curriculum 决定进入哪个 basin"与 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WorldModels §6.3 无知即课程]]"用认知不确定性反向选任务"是一体两面：前者说明**路径塑造终点**，后者给出**如何自动选路径**。

**补充 Foundation 锚点**（已 grep 验证，补 §7.1–7.3）：

- [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WorldModels §6.3 无知即课程]]：本文手工枚举 C1–C5 证明"课程时序主导 learning basin"；§6.3 与 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart ZVF]] 则回答"如何**自动**找到最优时序"——本文的手工枚举正是它们要替代的对象。
- [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3 自动课程]]：本文停在 §7.3 Phase 1（手工课程）；其 §5.2 列的 automatic curriculum / self-paced / PLR / POET 正是 §7.3 Phase 2–5 的自动化路线。

**簇内互链 + Delta**（补 §7.4 张力表的 continuation 视角）：

| 簇内论文 | 关系 | Delta |
|:--|:--|:--|
| [[Curriculum Learning\|Curriculum Learning]] | 本文是其 continuation 思想在**任务子目标维**的实例，并给出反例 | 本文课程轴 = reward 系数时序 $c_R,c_L$；且证明"先简单后复杂"非普遍最优（multiobjective-first 常更好） |
| [[EUREKA: Human-Level Reward Design via Coding Large Language Models\|EUREKA]] | 都用 PPO 学转笔、都靠 reward 塑造 | 本文**手工**调 $c_R,c_L$ 时序证明其威力；EUREKA **自动**进化 reward 组合。二者结合 = 让 LLM 进化 $c_R,c_L$ 的**课程 schedule** |
| [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]] | 手工 vs 自动课程的直接对照 | 本文固定 1000-episode 硬切换、人工 5 课程；DemoStart 用 ZVF success-variance 自适应选 frontier（§5.2 已列为本文替代方案） |

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “它是不是证明触觉不重要？” | 不是。它证明在仿真三指手低维球体任务中，curriculum 对 PPO learning path 的影响更强；cube/真实/高速接触可能相反 |
| “课程为什么会改变最终能力？” | 因为 $c_R,c_L$ 改变 advantage，从而改变 PPO 早期梯度方向和 basin |
| “C1-C5 到底是什么？” | C1=[L\|L+R]，C2=[R\|L+R]，C3=[L+R\|L+R]，C4=[L+R\|R]，C5=[L+R\|L] |
| “这和 HATO 的触觉结论冲突吗？” | 不冲突。HATO 的真实 rare contact/tool-use 让触觉成为闭环 success 变量；本文的仿真球任务让 curriculum 更支配 |
| “对转笔最该复刻什么实验？” | 做 curricula × tactile factorial，而不是只比较有/无触觉或只调 reward |
| “最危险的外推是什么？” | 把 no-tactile in simulation with constrained ball 外推到 real pen spinning |

## References

- Ojaghi, Pegah, Romina Mir, Ali Marjaninejad, Andrew Erwin, Michael Wehner, and Francisco J. Valero-Cuevas. "Curriculum is more influential than haptic feedback when learning object manipulation." Science Advances 11, eadp8407, 2025.
- [[Curriculum Learning]]
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]]
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]
- [[Lessons from Learning to Spin Pens]]
