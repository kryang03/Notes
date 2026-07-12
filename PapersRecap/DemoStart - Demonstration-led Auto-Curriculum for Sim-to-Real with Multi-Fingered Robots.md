---
tags:
  - paper
  - manipulation
  - curriculum-learning
  - sim-to-real
  - dexterous
  - reinforcement-learning
  - distillation
aliases:
  - DemoStart
  - Demonstration-led Auto-Curriculum
paper-year: 2024
read-date: 2026-02-08
venue: arXiv (Google DeepMind)
paper-pdf: "[[Papers/DemoStart: Demonstration-led auto-curriculum applied to sim-to-real with multi-fingered robots.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
---

# DemoStart: Demonstration-led Auto-Curriculum Applied to Sim-to-Real with Multi-Fingered Robots

> [!abstract] 核心贡献
> DemoStart 把少量仿真演示从“动作监督数据”重新解释成“可 reset 的状态课程”：从演示轨迹中抽取起始状态 task parameters，用 Zero-Variance Filtering 选择当前策略有时成功、有时失败的状态训练，再将 privileged teacher 蒸馏成 RGB+proprioception student，实现多指手复杂任务的高成功率仿真学习和 zero-shot sim-to-real。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功|ReinforcementLearning §7]]：ZVF 在稀疏二值奖励下自动寻找“既非全败也非全胜”的探索边界。
> - [[ReinforcementLearning#4. 策略梯度：在不可微世界中更新策略|ReinforcementLearning §4]]：DemoStart 不改 MPO/RL update rule，而是改 actor 侧采样分布 $p(\psi)$。
> - [[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家|ReinforcementLearning §5.4.2]]：teacher policy 用 privileged features 学，student 用 BC 蒸馏到视觉观测。
> - [[Optimization#奖励与课程优化|Optimization: reward/curriculum optimization]]：把训练预算集中到二值成功率方差非零的 task parameters，是一种低成本 adaptive sampling。
> **核心技术**: demonstration state resets, task parameters, zero-variance filtering, MPO, sparse binary rewards, PAC distillation, domain randomization, photorealistic rendering.

---

## 0. 阅读定位与范本价值

DemoStart 是 curriculum-learning 簇里非常适合 WMTS 的一篇，因为它回答了一个很具体的问题：

> 如果我只有很少、甚至不完整、动作空间也不匹配的 demonstrations，能不能不用它做 BC，而是用它生成一条自动难度课程？

这和上一篇 [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] 的关系很自然：

- Curriculum vs Haptic 说明 curriculum 会改变 PPO 的 learning basin；
- DemoStart 进一步问：curriculum 能不能不用人工 C1-C5，而是从 demonstration state 自动产生？

它的关键 value add 是把“演示”从 action label 变成 reset distribution。这个转变对灵巧手很重要，因为高质量动作演示很难采，但“状态轨迹”往往更容易利用。

| 范本要求 | 本文应回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | DemoStart 相比 BC、SAC-X、PLR/PAIRED 的 delta 是什么？ | §1 写清 demonstration-as-reset 而非 demonstration-as-action |
| 原理与理论 | ZVF 为什么等价于寻找 sparse reward 下的信息边界？ | §2 从 MDP task parameters、二项方差、采样分布推导 |
| 实验与验证 | Table I-IV 的 99.6/99.0/64/17 等数字如何支撑 story？ | §3 逐表解释 simulation、real、distillation ablation |
| 未来与结合 | 如何接入 WMTS 的 latent task generation / PPO Oracle / generalist distillation？ | §6 给出 ZVF-Solve/Probe/Reject 和转笔 reset curriculum |

---

## 1. 问题设定与动机

### 1.1 一句话核心

DemoStart 的核心是：把少量仿真 demonstration 切成从易到难的 reset states，再用当前策略在这些 states 上的 success variance 自动决定该练哪里，从而用 sparse binary reward 学出比 demonstration 更强、更平滑、更容易蒸馏和迁移的 dexterous policy。

### 1.2 直观隐喻

普通 BC 像让学生逐字模仿老师的每个动作；DemoStart 像教练把老师完成任务的视频剪成很多“从这里开始接着做”的练习题。

学生已经会最后一步，就把起点往前推；学生完全不会当前题，就先退回更靠近终点的题；学生有时成功有时失败，就说明这题刚好卡在能力边界，最值得练。

这个隐喻的可证伪点是：

- 如果只把演示状态均匀混进训练，不做 ZVF，应该也能提升；Table I 显示 Mechanism 1 alone 是 0%。
- 如果只用“出现成功就训练”的 success filter 够了，ZVF 不应有优势；Table I 显示 Success Filter 仍是 0%。
- 如果 demonstrations 的动作才是关键，那么 action-space mismatch / incomplete demos 应该无法利用；论文显示 DemoStart 不用 demonstration actions，仍能学 plug insertion。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| Vanilla sparse-reward RL | 从目标环境初始分布直接探索 | 插入/抓取这类长 horizon 稀疏奖励几乎撞不到成功 |
| SAC-X / auxiliary rewards | 人工子任务奖励帮助探索 | 需要 domain expertise；teacher 行为可能 jerky，多峰，蒸馏后崩 |
| Behavior cloning from teleop | 人类动作提供直接监督 | 真机 teleop 成本高，数据多样/暂停/风格差异导致 student 难拟合 |
| Offline RL from demonstrations | 复用演示动作和状态分布 | 演示动作空间必须匹配；低质量或 incomplete demos 会污染 replay |
| PLR / PAIRED 式 auto-curriculum | 自动挑选困难 levels | 往往需要额外 level generator / centralized controller，接入复杂 |
| Hand-designed reset curriculum | 人工指定从近终点到远终点 | 不可扩展到每个新任务，且难知道当前策略能力边界 |

### 1.4 Delta 分析

| 维度 | 旧路线 | DemoStart 增量 | 真正 value add |
|---|---|---|---|
| Demonstration 用途 | 动作监督 / replay data | 只用 full environment state 作为 reset TP | 动作质量差、动作空间不匹配也可用 |
| Curriculum 生成 | 人工设计难度 schedule | demo trajectory chunks 形成从难到易的 TP 序列 | 课程来自任务成功轨迹本身 |
| 难度选择 | 固定阈值、uniform sampling、success-only filter | ZVF：只训练 $0<\hat p<1$ 的 TP | 稀疏 reward 下自动找 learning frontier |
| RL update | 改 algorithm 或加 auxiliary reward | 不改 learner，只改 actor 侧数据生成 | 易接入 distributed actor-learner |
| Sim-to-real | 手写 perception / markers / state estimation | teacher privileged → PAC visual student | 不依赖固定 state estimator |
| 数据效率 | thousands real demos | 5-60 sim demos depending task | plug insertion 20 sim demos vs 2753 real teleop demos baseline |

---

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $s_t$ | state | simulator / rollout | 否，rollout data | 当前 MDP 状态 | teacher 使用 privileged features，student 不直接用 |
| $a_t$ | $\mathbb{R}^{18}$ | policy output | actor 输出带梯度；rollout detached | 6D arm Cartesian velocity + 12D finger joint positions | demonstration action 可不同，不被 DemoStart 使用 |
| $r_t$ | $\{0,1\}$ | sparse success detector | 否 | 二值成功奖励 | DemoStart 假设 success detector 易得 |
| $\psi$ | task parameter | sampled TP | 否 | 起始状态、环境设置、目标规格 | 不是 task label；它参数化一个 episode distribution |
| $s_0$ | state | $\psi$ component | 否 | episode reset state | 需要仿真器能保存/恢复状态 |
| $T_{target}$ | distribution over TPs | target environment | 否 | 真实评估初始分布 | DemoStart 最终要回到这个分布 |
| $D_i$ | demonstration trajectory | simulation teleop / scripted | 否 | 状态序列来源 | actions 不进入 replay，也不做 BC |
| $K$ | 8 | hyperparameter | 否 | 每条 demonstration 分成 8 个 chunks | 旧稿常误写 10；论文实验用 $K=8$ |
| $T$ | 4 rollouts | ZVF probe | 否 | 估计一个 TP 的 success variance | 太小有噪声，太大会浪费 actor compute |
| $M$ | 50 episodes | selected TP training | 否 | 一旦 TP 通过 ZVF，生成训练数据量 | 这些数据才送 replay buffer |
| $\hat p(\psi)$ | scalar | $T$ 次 probe 统计 | 否 | 当前策略在 TP 上经验成功率 | $0$ 全败，$1$ 全胜，二者都不训练 |
| ZVF | boolean | actor-side filter | 否 | 是否选择该 TP 训练 | variance 可能被环境随机性误导 |
| $\pi_T$ | teacher policy | MPO in simulation | 是，参数 | privileged state policy | teacher 不是视觉策略 |
| $\pi_S$ | student policy | BC distillation | 是，参数 | RGB + proprioception policy | real deployment 用 student |
| PAC | neural architecture | student model | 是 | Perceiver-Actor-Critic, used only for BC here | 虽叫 Actor-Critic，但本文蒸馏只用 BC |
| DR | randomization | sim training/rendering | 否 | physics/visual/perturbation randomization | demo-state episodes 不用 perturbation/physics DR |

### 2.2 Task parameters：把“任务”变成可采样分布

论文从标准 MDP 开始：

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},P,R,\gamma)
$$

每个时间步：

$$
a_t\sim \pi_\theta(\cdot\mid s_t)
$$

$$
r_{t+1}=R(s_t,a_t)\in\mathbb{R}
$$

$$
s_{t+1}\sim p(\cdot\mid s_t,a_t)
$$

DemoStart 在 MDP 外面加一个 task parameter：

$$
\psi=(s_0,\xi,g)
$$

其中：

- $s_0$ 是 episode 初始状态；
- $\xi$ 是 environment settings，例如物理/视觉参数；
- $g$ 是 goal specification，例如 cube 目标朝向。

于是训练不只是采样状态动作，而是先采样一个 TP：

$$
\psi\sim p(\psi)
$$

再在该 TP 对应的 episode distribution 上 rollout。

目标环境的 TP 分布记为：

$$
T_{target}
$$

这对应真实评估时的正常初始状态分布。DemoStart 的关键动作是扩展这个分布：用 demonstration 中间状态构造更容易、更有学习信号的 reset states。

### 2.3 Mechanism 1：demonstration state as reset curriculum

给定一条 demonstration：

$$
D=(s_0^D,s_1^D,\dots,s_N^D)
$$

普通 BC 使用：

$$
(o_t^D,a_t^D)
$$

DemoStart 不使用 $a_t^D$，而是把 $s_t^D$ 保存成可 reset 的 start state。

直觉：

- 靠近 demonstration 末端的 state 离成功近，通常更容易；
- 靠近 demonstration 开头的 state 离成功远，通常更难；
- 如果按从末端到开头逐步练，就形成 backward curriculum。

但 DemoStart 实现时并不是简单从末端开始。它会构造一个从 target initial distribution 和 demonstration chunks 混合而来的 TP 序列，并从“更难/更接近目标评估”的端开始 probe；如果太难就向更容易的 demonstration state 后退。

这保留了一个重要 bias：只要当前策略能在更靠前的状态获得训练信号，就不要长期停留在靠近成功的 demonstration 末端。

### 2.4 Mechanism 2：Zero-Variance Filtering

对某个 TP $\psi$，当前策略 rollout $T$ 次，得到 binary success：

$$
z_i(\psi)=\mathbb{1}[\tau_i\text{ succeeds}],\qquad i=1,\dots,T
$$

经验成功率：

$$
\hat p(\psi)=\frac{1}{T}\sum_{i=1}^{T}z_i(\psi)
$$

因为 $z_i$ 是 Bernoulli variable，经验方差近似：

$$
\widehat{\mathrm{Var}}[z]
=
\hat p(\psi)(1-\hat p(\psi))
$$

ZVF 的判断是：

$$
\mathrm{ZVF}(\psi)=1
\iff
0<\hat p(\psi)<1
$$

也就是 $T=4$ 次 probe 中，既出现成功又出现失败。

为什么这和学习信号有关？

| 情况 | $\hat p$ | 解释 | 是否训练 |
|---|---:|---|---|
| 全失败 | 0 | sparse reward 下没有正例，policy 不知道哪一步有用 | 不训练，换更容易 TP |
| 全成功 | 1 | 当前策略已掌握，继续训练信息量小 | 不训练，重新采样 |
| 有成有败 | $(0,1)$ | 同一 TP 附近存在可强化行为差异 | 训练，生成 $M=50$ episodes |

这就是 DemoStart 的核心 insight：**在二值稀疏奖励下，训练最有价值的不是最难任务，也不是最容易任务，而是当前 policy 的 success boundary。**

### 2.5 Mechanism 3：偏向更少 demonstration bias 的状态

demonstration 中后段状态常常包含不自然的中间状态，例如：

- 物体已经被不稳定地抓住；
- 插头已经被人类 teleop 调到接近 socket；
- 手处在一个 skilled policy 未必会经过的姿态。

如果长期从这些状态训练，policy 可能学会“修补演示里的坏 grasp”，而不是从目标初始状态学会正确 grasp。

DemoStart 的第三个机制是：在满足 ZVF 的前提下，优先选择更靠前、更接近目标评估分布的 TP。因为 actor 从序列前端开始 probe：

1. 先试 $T_{target}$ 或更早的 demonstration chunk；
2. 如果全失败，再退到更容易的 chunk；
3. 只在有成有败处训练。

这样它会自然从“靠近成功的 state”推进到“更接近真实初始分布的 state”。

### 2.6 DemoStart actor 侧流程

每个 actor 反复执行：

| Step | 操作 | 关键参数 | 是否进 replay |
|---|---|---:|---|
| 1 | sample TP sequence $(\psi_0,\dots,\psi_K)$ | $K=8$ | 否 |
| 2 | 对每个 TP probe $T$ 次 | $T=4$ | 否，这些 probe 不送训练 |
| 3 | 若 ZVF 通过，在该 TP rollout | $M=50$ | 是，送 replay buffer |
| 4 | learner 用 replay 更新 teacher policy | MPO | 是 |

论文明确说：probe episodes 不发送训练。只有 selected TP 上的 $M$ episodes 进入 replay。

这很重要，因为 DemoStart 的训练数据分布不是“所有演示 reset 的 rollout”，而是经过 ZVF 过滤后的 frontier distribution。

### 2.7 Distillation：privileged teacher 到 RGB student

DemoStart 的 teacher 是 feature-based policy，在仿真中用 privileged observations 学出来。真实部署不使用这个 teacher，而是蒸馏：

1. 用 teacher 生成 offline trajectories；
2. student 输入 RGB camera images + proprioception；
3. 用 behavior cloning 训练 student；
4. 结合 domain randomization 和 photorealistic rendering；
5. zero-shot transfer 到真实 Kuka + DEX-EE。

student 使用 PAC architecture，但本文只用它做 BC：

$$
\min_{\theta_S}
\mathbb{E}_{(o,a_T)\sim \mathcal{D}_{teacher}}
\left[
\ell(\pi_S(o),a_T)
\right]
$$

其中 $a_T$ 是 teacher action。

三类 domain randomization：

| DR 类型 | 内容 |
|---|---|
| Perturbations | 对未固定物体施加外力扰动 |
| Physics | 随机化 friction、mass、inertia |
| Visual | 随机化 camera pose、lighting、object colors |

plug insertion 还使用 Filament photorealistic images；Table IV 显示这对 real transfer 很关键。

---

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 论文设置 |
|---|---|
| Robot | Kuka LBR iiwa 14 + DEX-EE three-finger hand |
| Real cells | 6 robot cells, square basket with slanted walls |
| Cameras | two basket corner cameras + two wrist cameras |
| Action space | 18D: 6D Cartesian velocity for arm + 12 finger joint targets |
| Simulator | MuJoCo |
| Teacher RL | MPO with sparse binary success reward |
| Student | PAC, behavior cloning from teacher data |
| Real evaluation | zero-shot, no real fine-tuning |
| Evaluation success | episode contains at least one successful step; plug lift requires held for at least 1 s |

Task/demo counts：

| Task | Demonstrations used by DemoStart |
|---|---:|
| Plug lifting | 5 sim demos |
| Plug insertion | 20 sim demos: 12 upright insertion + 8 flip-to-upright incomplete demos |
| Cube reorientation | 2 unstructured interaction demos |
| Nut and bolt threading | 60 demos: 20 full, 20 lifts, 20 nut-to-top |
| Screwdriver in cup | 20 demos |

这张表本身就体现了 DemoStart 的优势：它不要求每条 demonstration 都完整成功。plug insertion 中 8 条只是把 plug 翻到 upright；DemoStart 仍能把这些中间状态当课程材料。

### 3.2 Simulation baselines：三机制的因果证据

Table I 是 plug insertion simulation 的关键消融：

| Method | Plug Insertion |
|---|---:|
| Vanilla RL | 0% |
| Vanilla RL + Mechanism 1 | 0% |
| Vanilla RL + Mechanism 1 + Success Filter | 0% |
| Vanilla RL + Mechanisms 1 & 2 | 97.2% |
| DemoStart (Mechanisms 1, 2 & 3) | 99.6% |
| SAC-X | 99.2% |
| DemoStart + BC distillation | 99.0% |
| SAC-X + BC distillation | 20.4% |

**因果解释**：

`Vanilla RL 0% -> sparse reward + long horizon exploration cannot find success`

`Mechanism 1 alone 0% -> demonstration reset states without filtering still wastes training on too-hard/too-easy states`

`Success Filter 0% -> "any success" includes states that are already easy; it does not enforce boundary learning`

`Mechanism 1+2 97.2% -> ZVF finds states with mixed success/failure, restoring useful gradient signal`

`Mechanism 3 97.2% -> 99.6% -> bias toward earlier/less demo-biased states improves final target-distribution performance`

`SAC-X 99.2% but distills to 20.4% -> auxiliary-reward RL can solve sim but produces jerky/diverse behavior that visual BC cannot imitate well`

The last line is especially important: **a teacher being successful in simulation is not enough; the teacher must generate a behavior distribution that is distillable.**

### 3.3 Simulation all-task performance

Table II shows DemoStart on all tasks:

| Task | DemoStart simulation success |
|---|---:|
| Plug Insertion | 99.6% |
| Plug Lift | 99.7% |
| Cube Reorientation | 99.9% |
| Nut and Bolt | 99.8% |
| Screwdriver in cup | 98.6% |

The strongest evidence here is not just “all above 98%”. It is that these tasks differ in horizon, precision, contact, and object configuration, yet the same sparse-reward + demo-reset + ZVF recipe works.

The screwdriver-in-cup qualitative result is also revealing: DemoStart’s emergent curriculum starts near the end of the demonstration, then shifts backward toward grasping the screwdriver, holding the cup, and eventually handling the cup being upside down. This is the visual proof that ZVF is not just filtering data; it is moving the initial-state distribution over training.

### 3.4 Real-world transfer：zero-shot 能成，但 contact gap 仍明显

Table III reports real robot performance:

| Method | Plug Lift | Plug Insertion | Cube Reorientation |
|---|---:|---:|---:|
| DemoStart distillation | 97% | 64% | 97% |
| SAC-X distillation | 20% | 1% | Not evaluated |
| BC from real teleop | 64% | 2% | Not evaluated |

Important data context：

- DemoStart plug insertion uses 20 simulation demonstrations, about half an hour of collection time.
- Real teleop baseline uses 2067 successful insertion demonstrations and 2116 lift demonstrations; including failures, 2753 demonstrations amount to about 27 hours non-stop data collection.

**因果解释**：

DemoStart beats real teleop BC not because simulation is magically real, but because DemoStart uses demonstrations to shape RL exploration and then lets RL improve beyond demonstration quality. Real teleop BC inherits human pauses, diverse styles, suboptimal motions, and distributional noise.

Plug insertion remains the hard case: 99.6% sim to 64% real. That drop is the contact-precision gap. Insertion has small clearances, friction, contact normals, jamming, and repeated attempts; DR helps but does not eliminate contact mismatch.

### 3.5 Distillation ablations：sim success hides real perception fragility

Table IV ablates the distillation pipeline for plug insertion:

| Method | Plug Insertion Sim | Plug Insertion Real |
|---|---:|---:|
| DemoStart distillation | 99.0% | 64% |
| without photorealistic data | 97.0% | 29% |
| with fingertip Cartesian poses | 98.6% | 50% |
| with 3 cameras | 99.3% | 51% |
| with 2 cameras | 98.1% | 42% |
| with 1 camera, no wrist camera | 97.0% | 17% |

**因果解释**：

Simulation numbers barely move, but real performance collapses when photorealistic rendering or camera coverage is removed. This is a clean warning: in sim-to-real, a student policy can look solved in sim while relying on visual features that do not transfer.

The camera result is also aligned with HATO: wrist/near-hand views are crucial for dexterous contact tasks. Third-person view alone is not enough for precise insertion.

### 3.6 What the experiments prove, and what they do not prove

They prove:

- demonstration states can generate a useful curriculum without demonstration actions;
- ZVF is the key component, not simply demonstration reset;
- DemoStart teacher behavior is more distillable than SAC-X behavior;
- vision distillation + DR can transfer some multi-fingered tasks zero-shot.

They do not prove:

- plug insertion sim-to-real is solved;
- arbitrary dynamic manipulation can be handled by reset-state curriculum;
- sparse binary rewards are always enough;
- ZVF is compute efficient;
- real robot data is unnecessary for final-mile improvement.

---

## 4. 核心洞见

### 4.1 论文真正的 insight

DemoStart 的真正 insight 是：

> Demonstrations are not only trajectories to imitate; they are ordered samples of task difficulty.

Once this is accepted, a demonstration becomes a curriculum substrate:

$$
D=(s_0,\dots,s_N)
\quad\Rightarrow\quad
\{\psi_1,\dots,\psi_K\}
$$

and ZVF supplies the missing adaptive rule:

$$
0<\hat p(\psi)<1
$$

Together, they convert a sparse-reward exploration problem into a frontier-sampling problem.

### 4.2 为什么 DemoStart 比 BC 更适合少量/低质 demonstrations

BC requires action correctness:

$$
\pi_\theta(o_t)\approx a_t^D
$$

If $a_t^D$ comes from a SpaceMouse, a human teleoperator, a different action space, or a suboptimal partial demonstration, BC either cannot use it or learns bad style.

DemoStart only needs state usefulness:

$$
s_t^D \rightarrow \text{reset state}
$$

As long as the state lies on or near a feasible path to success, RL can discover a better action than the demonstrator. This explains why DemoStart can use incomplete plug flipping demos and still solve full insertion.

### 4.3 什么时候会失效

| Failure condition | Why DemoStart struggles |
|---|---|
| Cannot reset simulator to demonstration states | Mechanism 1 disappears |
| Demonstrations pass through unnatural/unrecoverable states | ZVF may train on bad frontier states |
| Binary success variance caused by environment stochasticity | ZVF mistakes noise for learning signal |
| Task has no smooth backward curriculum | Demo chunks do not form a useful difficulty chain |
| Real contact gap dominates | teacher learns behavior that relies on wrong sim contact |
| Student observation lacks necessary information | distillation succeeds in sim but fails in real |
| Highly dynamic non-prehensile manipulation | reset states may be physically hard to initialize and action timing dominates |

---

## 5. 替代方案与理论局限

### 5.1 理论维度

ZVF is not a theorem that maximizes policy gradient norm. It is a practical proxy.

For binary reward, variance is:

$$
\mathrm{Var}[z]=p(1-p)
$$

This is maximal at:

$$
p=0.5
$$

ZVF only checks:

$$
0<p<1
$$

With $T=4$, it cannot distinguish $p=0.25$, $p=0.5$, and $p=0.75$ very reliably, and it can be fooled by randomness. Its strength is simplicity, not statistical optimality.

### 5.2 算法维度

| Alternative | Advantage | DemoStart trade-off |
|---|---|---|
| PLR | Prioritize levels by learning progress | Requires a level framework; DemoStart uses demo states directly |
| PAIRED | Generates adversarial curricula | Needs additional agents/controllers |
| SAC-X | Auxiliary rewards solve sparse exploration | Requires reward engineering; distillation can fail |
| BC / ACT / Diffusion Policy | Simple supervised training | Needs many high-quality demonstrations |
| Offline RL from demos | Can improve over behavior data | Needs action-space-compatible, reliable replay data |
| Self-paced curriculum | Smooth adaptation | Needs progress metrics; DemoStart uses sparse success variance |

### 5.3 工程/实验维度

1. **Compute intensive**：ZVF drops most actor data, and sparse reward rollouts are expensive.
2. **State reset dependence**：real robots cannot reset to arbitrary demonstration states; this is simulation-first.
3. **Contact sim-to-real gap**：plug insertion drops from 99.6% sim to 64% real.
4. **Vision transfer fragility**：without photorealistic data, real plug insertion drops to 29%; with one camera/no wrist, 17%.
5. **Teacher privileged information**：student must relearn perception by imitation; any teacher state not visually inferable becomes a distillation bottleneck.
6. **Predictable dynamics assumption**：authors expect DemoStart to work best for manipulation tasks with predictable dynamics.
7. **No online real improvement**：the paper suggests real-robot data in second phase as future work; current results are zero-shot.

---

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / DNPM 转笔的直接迁移

DemoStart should be treated as a reset-curriculum generator, not as an imitation method.

| DemoStart concept | DNPM / LinkerHand equivalent | Practical use |
|---|---|---|
| demonstration state $s_t^D$ | state along successful/partial pen-spin trajectory | reset curriculum in simulation |
| near-end states | pen already caught / stable post-spin | easy TP |
| early states | pre-snap / launch / first contact | hard TP |
| ZVF | success variance over $T$ attempts | choose current training frontier |
| $T=4$ probe | few rollouts per candidate reset | cheap frontier estimate |
| $M=50$ training episodes | batch after selected reset | generate PPO/MPO training data |
| no demo actions | use poor teleop or mocap state only | avoid action-space mismatch |

For pen spinning, a possible demonstration-state curriculum:

| Segment | Reset state | Why useful |
|---|---|---|
| S8 | pen already caught after spin | learn final stabilization |
| S7 | pen about to contact catching finger | learn catch timing |
| S6 | pen mid-flight/rolling between fingers | learn recovery |
| S5 | release just happened | learn post-release control |
| S4 | snap force just before release | learn launch |
| S3 | preloaded grasp | learn energy storage |
| S2 | canonical initial grasp | learn setup |
| S1 | target initial distribution | full task |

The risk is that real LinkerHand cannot reset to arbitrary mid-spin states. Therefore DemoStart is most directly useful in simulation and for task generation; real transfer still needs robust initialization controllers or a world model.

### 6.2 对 WMTS 五模块的具体接法

WMTS pipeline：latent task generation → PPO Oracle specialist → Diffusion/Flow generalist → Ensemble World Model → real robot fine-tuning。

| WMTS 模块 | DemoStart transfer | Required modification |
|---|---|---|
| latent task generation | Treat demo states as task parameters $\psi$ | Add ZVF-like success-variance frontier selection |
| PPO Oracle specialist | Train on selected frontier states | PPO can replace MPO, but sampling logic is the key |
| Diffusion/Flow generalist | Distill oracle trajectories, not human actions | Include reset/curriculum metadata as conditioning |
| Ensemble World Model | Estimate whether a TP is solve/probe/reject | Use uncertainty + success probability, not task labels in dynamics |
| real robot fine-tuning | Add real data to distillation/second phase | Paper explicitly leaves this as future work |

A WMTS version of ZVF:

$$
\hat p(\psi)=
\frac{1}{T}
\sum_{i=1}^{T}
\mathbb{1}[\text{success}(\tau_i)]
$$

Decision:

| $\hat p(\psi)$ | WMTS interpretation | Action |
|---:|---|---|
| 0 | Reject / too hard now | sample easier reset or decompose task |
| $(0,1)$ | Probe / high training signal | train PPO Oracle and collect data |
| 1 | Solve / mastered | move toward harder or target distribution |

This matches the cross-paper ensemble insight already in the WMTS graph: Solve / Probe / Reject is not only an uncertainty heuristic; DemoStart gives a sparse-reward operationalization.

### 6.3 可验证实验建议

| Experiment | Baselines | Metrics | What it tests |
|---|---|---|---|
| ZVF vs fixed threshold for pen-spin resets | ZVF, success>70%, uniform demo reset | success, sample efficiency, reset frontier progression | Whether variance is better than absolute success |
| Demo state only vs demo action BC | BC, DemoStart-style reset, BC+RL | real/sim success, smoothness, recovery | Whether state curriculum beats action imitation |
| K/T/M ablation | $K\in\{4,8,16\}$, $T\in\{2,4,8\}$, $M\in\{25,50,100\}$ | compute, success, false frontier rate | Practical operating point for LinkerHand |
| Distillability of teachers | PPO Oracle, SAC-X-like auxiliary teacher, DemoStart teacher | BC loss, rollout success, action jerk | Whether smooth frontier-trained teachers distill better |
| Contact-gap stress | plug insertion / pen catch with increasing clearance/friction randomization | sim-real drop, ensemble uncertainty | Whether world model/DR captures contact precision |

### 6.4 不应过度外推的点

- DemoStart is not a real-robot reset method; arbitrary mid-trajectory reset is a simulator privilege.
- It is not proof that sparse rewards are always enough; the demonstrations encode much of the task structure.
- It does not solve contact sim-to-real: plug insertion real is 64%, not near 100%.
- It does not mean human demonstrations are obsolete; they become curriculum substrates instead of action labels.
- It does not remove the need for visual transfer engineering; Table IV shows perception choices dominate real performance.

---

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

DemoStart modifies the task distribution:

$$
J(\theta)
=
\mathbb{E}_{\psi\sim p(\psi)}
\mathbb{E}_{\tau\sim \pi_\theta(\cdot\mid\psi)}
\left[
\sum_t \gamma^t r_t
\right]
$$

Vanilla RL samples:

$$
\psi\sim T_{target}
$$

DemoStart samples:

$$
\psi\sim p_{ZVF}(\psi;\pi_\theta,D)
$$

where $p_{ZVF}$ concentrates probability mass on TPs with nonzero success variance. This is curriculum learning as adaptive task-distribution shaping, not reward shaping.

### 7.2 与 [[Optimization]] 的联系

For binary success, ZVF uses:

$$
\hat p(1-\hat p)
$$

as a cheap proxy for informativeness. In optimization language, this is adaptive sampling near the decision boundary. It is not exact gradient-norm sampling, but it cheaply avoids two bad regions:

- solved region: no improvement needed;
- impossible region: sparse reward gives no gradient.

### 7.3 与 [[RepresentationLearning]] 的联系

Teacher-student distillation is the representation bottleneck:

$$
\pi_T(s^{privileged})
\rightarrow
\pi_S(I^{RGB},q)
$$

The real ablation shows that student perception is the limiting factor even when teacher behavior is solved. Photorealistic rendering and wrist cameras are not cosmetic; they determine whether the student can infer the contact-relevant state.

### 7.4 与 [[ContactMechanics]] 的联系

Plug insertion is the contact bottleneck. The sim-to-real drop:

$$
99.6\%\ \text{sim}
\rightarrow
64\%\ \text{real}
$$

is a contact-mechanics warning. Small-clearance insertion depends on friction, jamming, compliance, contact normals, and repeated corrective attempts. DemoStart solves exploration, but it does not eliminate physical mismatch.

### 7.5 与相关 recaps 的关系

| Related recap | Relationship |
|---|---|
| [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] | Manual curriculum schedule vs demonstration-derived automatic curriculum |
| [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] | Both manipulate training distribution; CSR removes sensing, DemoStart shifts reset states |
| [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] | DemoSpeedup changes temporal speed of demos; DemoStart changes reset distribution |
| [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] | HATO collects real demonstrations for BC; DemoStart uses few sim demonstrations as reset states |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | Touch Dexterity uses tactile for policy observability; DemoStart currently relies on RGB/proprio distillation |

---

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “DemoStart 的真正创新是什么？” | demonstration state reset + ZVF frontier selection；不是 BC，也不是单纯 replay demos |
| “ZVF 为什么有效？” | binary success variance $\hat p(1-\hat p)$ 在 $0<\hat p<1$ 时非零，说明当前策略在该 TP 有可强化差异 |
| “三机制哪个最重要？” | Table I：Mechanism 1 alone 0%，Success Filter 0%，Mechanism 1+2 97.2%，Full 99.6%；ZVF 是关键，bias 是补强 |
| “为什么 SAC-X 仿真强但蒸馏差？” | auxiliary reward teacher 行为更 jerky/多样，BC student 难拟合；DemoStart teacher 更平滑一致 |
| “对 WMTS 最直接的启发？” | 把 latent task generation 写成 ZVF 的 Solve/Probe/Reject frontier，而不是固定难度阈值 |
| “最大风险？” | 任意状态 reset 是仿真特权；真实转笔不能直接 reset 到 mid-spin，需要 sim curriculum + real fine-tuning |

### 7.6 暗线锚定：ZVF 是"认知不确定性三用"的稀疏奖励操作化

> [!abstract] 暗线锚定：认知不确定性（该学处）+ Continuation（反向 reset 课程）
> 本库暗线"**认知不确定性三用**"是说：ensemble 分歧 = epistemic 不确定性 = 信息增益，它在规划里当护栏、探索里当罗盘、**课程里当"该学处"**。DemoStart 的 ZVF（$0<\hat p(\psi)<1$，二值 success variance $\hat p(1-\hat p)$）正是这条暗线**课程分支**的一个**稀疏奖励可计算**版本：全败（$\hat p=0$）= 当前策略认知外，全胜（$\hat p=1$）= 已掌握，两端都无学习信号；只有 variance 非零处才是"该学处"。这与 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WorldModels §6.3 无知即课程]] 同构——只是 §6.3 用 ensemble disagreement 度量"无知"，DemoStart 用 rollout success variance 度量。两者都把"最该练的任务 = 认知边界任务"。

**补充 Foundation 锚点**（已 grep 验证，补 §7.1–7.4 之外）：

- [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WorldModels §6.3 无知即课程]]：ZVF frontier = §6.3 的"该学处"，用 success variance 代替 ensemble disagreement。这给 §6.2 已写的 Solve/Probe/Reject 提供了**理论出处**：Reject（$\hat p=0$）/ Probe（$0<\hat p<1$）/ Solve（$\hat p=1$）三档正是 §6.3 认知不确定性课程的稀疏化。
- [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3 自动课程]]：ZVF 对应 §7.3 的 Learning-Progress 分支（进步速度自指路）——variance≈能力边界；而 demonstration-as-reset 是 §7.3 Phase 1 手工课程的**自动化替代**（课程材料来自演示状态而非人工设计）。

**簇内互链 + Delta**（补 §7.5 表）：

| 簇内论文 | 关系 | Delta |
|:--|:--|:--|
| [[Curriculum Learning\|Curriculum Learning]] | DemoStart 把其人工 `difficulty_fn` 自动化 | Bengio 需人工排序难度；DemoStart 用 ZVF success-variance **自动**选 frontier，是 continuation 谱系的 Phase 2/3 自动化端 |
| [[Hindsight Experience Replay\|HER]] | 二者都靠"achieved/reset 状态"造课程，互补 | HER 用 achieved-goal 造 hindsight 目标（值利用侧）；DemoStart 用 demonstration state 造 reset 起点（探索桥侧）。§7.5 已述"DemoStart 打开探索桥，HER 复用失败 outcome" |
| [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills\|DeepMimic]] | **reset 分布是同一杠杆** | DeepMimic 的 RSI（$\rho_0^{RSI}=\frac1T\sum\delta(s=\hat s_\tau)$）与 DemoStart 的 demonstration-as-reset 是**同一思想**：把长链探索拆成从中间相位起步的短问题。Delta：RSI 均匀采整条 reference 相位；DemoStart 用 ZVF **自适应**只在 frontier reset，且不用演示动作 |

> [!tip] 一句话记忆锚
> **DemoStart = 用 success-variance 当"认知不确定性"、把演示状态当"可 reset 的难度轴"。** 它是 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|无知即课程]] 的稀疏奖励落地，也是 DeepMimic RSI 的自适应升级版。

## References

- Bauza, Maria, Jose Enrique Chen, Valentin Dalibard, Nimrod Gileadi, Roland Hafner, Murilo F. Martins, Joss Moore, Rugile Pevceviciute, Antoine Laurens, Dushyant Rao, Martina Zambelli, Martin Riedmiller, Jon Scholz, Konstantinos Bousmalis, Francesco Nori, and Nicolas Heess. "DemoStart: Demonstration-led auto-curriculum applied to sim-to-real with multi-fingered robots." arXiv:2409.06613, 2024.
- [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]]
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]]
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]]
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
