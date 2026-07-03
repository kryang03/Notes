---
tags:
  - paper
  - dexterous-manipulation
  - tactile-sensing
  - sim-to-real
  - reinforcement-learning
  - in-hand-manipulation
aliases:
  - Touch Dexterity
  - Rotating without Seeing
paper-year: 2023
read-date: 2026-02-01
venue: ICRA 2023
paper-pdf: "[[Papers/Touch Dexterity - Rotating without Seeing.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ContactMechanics]]"
  - "[[ControlTheory]]"
---

# Touch Dexterity: Rotating without Seeing - Towards In-hand Dexterity through Touch

> [!abstract] 核心贡献
> Touch Dexterity 提出一种低成本、低 sim-to-real gap 的触觉灵巧手系统：在 Allegro Hand 的 palm、finger links、fingertips 上布置 16 个 Force-Sensing Resistor (FSR) 二值接触传感器，用 no-vision 的本体+触觉闭环 PPO 学习 in-hand object rotation。它的关键不是高分辨率触觉，而是用全手覆盖的 1-bit contact mode 明确观测物体在手中的接触拓扑；二值化把难以对齐的连续力值压成 touch/no-touch，从而让仿真和真实的触觉模式在局部时间窗内足够相似，实现对未见真实物体的 zero-shot transfer。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 用 PPO 训练 MLP policy，critic 使用 asymmetric privileged observations；policy 本身只用本体、二值触觉、上一目标和旋转轴。
> - [[SignalProcessing]] — 触觉输入是 1-bit threshold quantization；它牺牲力幅值，换取更小 sim-to-real observation gap。
> - [[ContactMechanics]] — 16-bit contact vector 是接触模式 $\sigma(t)$ 的显式观测，告诉策略哪些手指/掌心区域在接触。
> - [[RepresentationLearning]] — 全手二值触觉通过空间覆盖 + 历史堆叠隐式编码 object pose/shape，比单点高精触觉更适合低成本闭环。
> - [[ControlTheory]] — policy 输出相对关节位置目标，经 EMA 平滑后由 10Hz PD control 执行；不是 torque-level tactile control。
>
> **核心技术**: Binary Tactile Sensing, Full-Hand Contact Coverage, PPO, Domain Randomization, Asymmetric Critic, Touch-Only In-Hand Rotation

## 0. 阅读定位与范本价值

Touch Dexterity 是触觉 in-hand rotation 演进线里的“低成本极点”。它和 AnyRotate / Tacmap 的关系非常清楚：

- Touch Dexterity：用 16 个二值接触点让 sim/real contact mode 尽量一致；
- AnyRotate：用 contact pose + force magnitude 增加触觉密度和重力不变性；
- Tacmap：用 penetration depth map 对齐更连续的触觉几何。

这篇论文的价值不在于它最强，而在于它提出了一个反直觉原则：**对 sim-to-real，低保真但鲁棒的触觉表征有时比高保真但难对齐的连续触觉更有效。**

对你的 LinkerHand / WMTS / 转笔项目，它提供一个非常好的 baseline 思路：先把触觉压成 contact mask / contact mode，检验这是否已经能显著提升策略；再逐步加入 force、pose、shear、Tacmap-style geometry。不要一开始就默认高维触觉一定更好。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 本文的 insight 是“全手低维接触模式 + 二值化”比少量高精触觉更适合低成本 sim-to-real |
| 原理与理论 | §2 | 从 FSR threshold、contact mode、MDP、EMA action、reward、asymmetric critic 推导 |
| 实验与验证 | §3 | Table I-IV/V 证明触觉、全手覆盖、二值化和多轴 rotation 的作用 |
| 未来与结合 | §5-§7 | 对转笔可作为 contact-mode baseline，但缺力幅值、切向滑移和高速时序建模 |

## 1. 问题设定与动机

### 1.1 一句话核心

Touch Dexterity 要证明：即使没有视觉、没有高分辨率触觉图像，只要全手覆盖的二值接触信号足够稳定，RL policy 也能学会把未见物体在手内旋转。

### 1.2 直观隐喻

在黑暗中洗锅，你不需要知道每个接触点的精确牛顿值；你需要知道锅在不在掌心、哪根手指碰到了边、是否快滑出手。Touch Dexterity 把这个思路工程化：不用昂贵 GelSight，只用 16 个“碰到/没碰到”的开关铺在手上，让策略从接触模式变化中推断物体位置和运动。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 |
|---|---|---|
| Vision-based dexterous manipulation | 相机提供 object pose/shape | 手内操作遮挡严重，硬件布置复杂 |
| 高精指尖触觉 | 局部精细几何/力信息 | 贵、覆盖小、触觉图像/连续力 sim-to-real gap 大 |
| 纯本体 in-hand rotation | 从关节误差隐式推断接触 | 接触状态间接且不稳定，未见物体泛化弱 |
| Continuous tactile force | 保留力幅值 | 仿真力和真实电压/力标定难对齐，策略易过拟合 sim distribution |
| Open-loop replay | 不需要感知闭环 | 物体位置一偏就无法恢复 |

### 1.4 Delta 分析

| 维度 | 常见做法 | Touch Dexterity |
|---|---|---|
| 传感器 | 少量高精传感器或无触觉 | 16 个低成本 FSR，覆盖 palm + finger links + fingertips |
| 触觉表示 | 连续力/图像/局部触觉 | 1-bit binary contact |
| sim-to-real 策略 | 精确模拟传感器输出或域适应 | 阈值化，把连续 force gap 截断成 contact mode gap |
| policy 输入 | 视觉/本体/隐式接触 | 本体 + 二值触觉 + previous target + target axis，堆叠 3 历史状态 |
| critic | 普通 observation | asymmetric observation with privileged object/contact information |

论文故事最强的地方是：它不是说二值触觉信息更多，而是说二值触觉**更容易对齐**。当 real/sim continuous force 不准时，binary contact 反而可能是更好的 policy input。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $q_t$ | $\mathbb R^{16}$ | Allegro joint encoder | 否 | 当前关节位置 | policy 可见 |
| $\tilde q_t$ | $\mathbb R^{16}$ | previous position target | 否 | 上一步目标关节位置 | 不是 object target |
| $o_t$ | $\{0,1\}^{16}$ | 16 FSR threshold / sim contact threshold | 否 | 二值接触模式 | 论文用 $o_t$ 表示 sensor observation，不是完整 observation |
| $F_i$ | $\mathbb R^3$ or scalar norm | sim net contact force / FSR analog proxy | 否 | 第 $i$ 个传感器对应接触力 | continuous force 不直接输入 policy |
| $\theta_{\mathrm{th}}$ | scalar | threshold calibration | 否 | 真实端二值化阈值 | 仿真用 $\tilde\theta_{\mathrm{th}}=0.01N$ |
| $k$ | $S^2$ | task command | 否 | 目标旋转轴 x/y/z 或任意轴 | 指令轴，不等于瞬时 object angular velocity |
| $a_t$ | $\mathbb R^{16}$ | policy output | 是 | 相对关节位置 command | 经 EMA 后才成为 target update |
| $\tilde a_t$ | $\mathbb R^{16}$ | action smoothing | 计算图中间量 | 平滑动作 | $\eta=0.8$ |
| $\tau$ | $\mathbb R^{16}$ | PD controller torque | 否 | work/torque penalty 计算 | policy 不直接输出 torque |
| $\Delta\theta$ | scalar | object rotation finite difference | 否 | 沿目标轴的旋转进度 | 不是 simulator angular velocity |
| $s_t^{V}$ | privileged critic input | simulation only | 否 | object pose, physical params, contact forces 等 | 只给 value network，不给 policy |

### 2.2 传感器模型：为什么 1-bit 能减小 gap

真实 FSR 输出连续 analog voltage，但论文不把它当连续力输入，而是 threshold：

$$
b_i
=
\mathbf 1[\mathrm{FSR}_i>\theta_{\mathrm{th}}].
$$

仿真中把每个 contact sensor 建成固定 link，读取该 link 的 net contact force：

$$
F_i=[F_x,F_y,F_z],
$$

再取 norm 并阈值化：

$$
b_i^{\mathrm{sim}}
=
\mathbf 1[\|F_i\|>\tilde\theta_{\mathrm{th}}],
\qquad
\tilde\theta_{\mathrm{th}}=0.01N.
$$

若 sim force 和 real sensor voltage/force 的连续值有偏差，只要它们落在 threshold 同侧：

$$
b_i^{\mathrm{sim}}=b_i^{\mathrm{real}}.
$$

这就是二值化的价值：它不会让 sim-to-real gap 消失，但会把 gap 集中到 threshold boundary 附近。Figure 7 也说明，sim contact signals 比 real 略 dense/rich，一些传感器更常激活，但整体时序模式相似，足以支持 transfer。

### 2.3 信息量：16 个二值传感器不是一个传感器

单个 1-bit 传感器只提供 contact/free。但 16 个传感器覆盖 palm、links、fingertips，形成 contact mode：

$$
b_t=(b_{t,1},\dots,b_{t,16})\in\{0,1\}^{16}.
$$

最多有：

$$
2^{16}=65536
$$

种 instantaneous contact patterns。

但更关键的是时间窗。Policy 输入不是单步，而是堆叠当前状态和 3 个历史状态。因此它能看到短时间 contact mode transitions：

$$
(b_{t-3},b_{t-2},b_{t-1},b_t).
$$

这让低维二值信号可以表达：

- 物体是在 palm 中央还是滑向边缘；
- 哪根手指正在推；
- 关键 contact 是否丢失；
- contact pattern 是否进入卡住/掉落前兆。

### 2.4 MDP 与 policy observation

论文定义：

$$
\mathcal M=(\mathcal S,\mathcal A,\mathcal R,\mathcal P).
$$

Policy state 由：

$$
s_t=[q_t,\ o_t,\ \tilde q_t,\ k]
$$

及 3 个历史状态 stack 而成。

动作：

$$
a_t\in\mathbb R^{16}.
$$

target joint update 原始形式：

$$
\tilde q_{t+1}
=
\tilde q_t+a_t.
$$

为了平滑，实际使用 EMA：

$$
\tilde a_t
=
\eta a_t+(1-\eta)\tilde a_{t-1},
\qquad
\eta=0.8,
$$

$$
\tilde q_{t+1}
=
\tilde q_t+\tilde a_t.
$$

控制频率：仿真和真实都是 10Hz。旧稿写 20Hz 不符合 PDF。

### 2.5 旋转奖励：不用 noisy angular velocity

主奖励：

$$
r_t
=
w_1r_{\mathrm{rot}}
+w_2r_{\mathrm{vel}}
+w_3r_{\mathrm{fall}}
+w_4r_{\mathrm{work}}
+w_5r_{\mathrm{torque}}
+w_6r_{\mathrm{dist}}.
$$

其中 rotation reward 不是直接用 simulator angular velocity。论文指出复杂接触下 angular velocity 很 noisy，容易导致 object 振动在某个姿态附近。

它改用 finite-difference rotation angle：

1. 在 rotation axis $k$ 的 normal plane $\Pi$ 中采样 unit vector $v$；
2. 想象 $v$ 固定在 object 上；
3. 下一状态得到 $v'$，投影到 $\Pi$ 得到 $v'_p$；
4. 计算 $v$ 到 $v'_p$ 关于轴 $k$ 的 signed angle：

$$
\Delta\theta\in[-\pi,\pi).
$$

Rotation reward：

$$
r_{\mathrm{rot}}
=
\mathrm{clip}(\Delta\theta,-0.157,0.157).
$$

其他项：

| Term | 公式/含义 |
|---|---|
| $r_{\mathrm{vel}}$ | $-\|v_t\|$，惩罚 object 线速度，提升稳定性 |
| $r_{\mathrm{fall}}$ | $-50.0$，object 掉出 palm 的 penalty |
| $r_{\mathrm{work}}$ | $-\langle|\tau|,|\dot q_t|\rangle$ |
| $r_{\mathrm{torque}}$ | $-\|\tau\|$ |
| $r_{\mathrm{dist}}$ | 鼓励 fingertips 靠近 object |

权重：

| 权重 | 值 |
|---|---:|
| $w_1$ | 20.0 |
| $w_2$ | 0.1 |
| $w_3$ | 1.0 |
| $w_4$ | 0.0003 |
| $w_5$ | 0.0003 |
| $w_6$ | 0.1 |

### 2.6 PPO 与 asymmetric critic

Policy/value 都是 MLP，PPO 训练。Policy 只看可部署 observation；value network 额外看 privileged information：

- contact force over each link；
- object ground-truth pose；
- physical parameters。

这叫 asymmetric observation。它提高训练时 value estimation，但不会把 privileged object state 泄漏给真实 policy。

PPO 超参：

| 参数 | 值 |
|---|---:|
| horizon length | 16 |
| $\gamma$ | 0.99 |
| GAE $\tau$ | 0.95 |
| clip $\epsilon$ | 0.2 |
| policy MLP | [512,256,256], ELU |
| policy LR | $10^{-4}$ |
| value MLP | [512,512,256,256], ELU |
| value LR | $5\times10^{-4}$ |
| minibatch size | 16384 |
| gradient norm | 1.0 |
| adaptive KL | policy 0.02, value 0.016 |
| envs | 8192 parallel envs |
| sim dt | 0.01667s, 2 substeps |

### 2.7 Domain randomization

Table VI：

| 类别 | 参数 |
|---|---|
| Object mass | [0.2,0.6] kg |
| Object friction | [0.3,3.0] |
| Object shape | $\times U(0.95,1.05)$ |
| Object initial position | $+U(-0.015,0.015)$ cm scale as reported |
| Hand friction | [0.3,3.0] |
| PD P gain | $\times U(0.66,1.33)$ |
| PD D gain | $\times U(0.80,1.20)$ |
| Sensor lag probability | 0.25 |
| Sensor drop rate | 0.1 |
| Random force scale | 0.2 |
| Random force probability | [0.2,0.25] |
| Random force decay | 0.99 every 0.1s |
| Joint obs noise | $+U(-0.05,0.05)$ |
| Action noise | $+U(-0.06,0.06)$ |

论文还做了 system identification：调整 PD coefficients，使仿真和真实控制器对 impulse / sinusoidal inputs 的响应对齐。作者明确说这一步对 sim-to-real 很关键。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项 | 设置 |
|---|---|
| Hardware | XArm robot arm + 16-DoF Allegro Hand |
| Tactile | 16 FSR sensors over one side of hand |
| Microcontroller | STM32F collects analog voltage and forwards digital signals |
| Task | rotate object around x/y/z axis without vision |
| Simulation | IsaacGym |
| Training objects | object set A / B with artificial cuboids, cylinders, balls, irregular objects |
| Real test | object set C, 10 seen/unseen real objects including rubber duck, tomato, apple, orange, soupcan |
| Metrics | CRR in sim, CRA in real, TTF/duration |

注意：题目说 “Rotating without Seeing”，不是 “without proprioception”。Policy 仍然使用 joint position、previous target 和 target axis。

### 3.2 Table II：单物体 physics shift

| Method | Seen Physics CRR | Seen TTF | Unseen Physics CRR | Unseen TTF |
|---|---:|---:|---:|---:|
| No-Sensor | 689.3±141.5 | 33.3±4.7 | 369.0±129.1 | 23.5±6.1 |
| Sensor | **963.8±377.8** | **42.2±4.1** | **919.3±338.0** | **40.0±4.3** |
| DS-Sensor | 904.2±408.6 | 39.1±6.3 | 615.5±293.2 | 31.2±8.0 |
| LS-Sensor | 860.0±348.7 | 38.8±6.9 | 796.5±366.7 | 37.4±8.4 |

因果解释：

- Sensor 在 seen/unseen physics 下 CRR 几乎不掉，说明二值触觉对摩擦/质量 shift 有鲁棒性。
- DS-Sensor 是训练时有 tactile、评估禁用 tactile，unseen physics 下明显掉到 615.5，说明 policy 真正在使用 tactile input，而不是只靠训练 regularization。
- LS-Sensor 在单物体 physics shift 下还不错，说明低敏触觉仍能帮助稳定；但后面多物体训练它失败，说明高敏触觉对更复杂 contact variation 必要。

### 3.3 Table III：多物体泛化

| Method | Seen Object CRR | Seen TTF | Unseen Object CRR | Unseen TTF |
|---|---:|---:|---:|---:|
| Sensor | **976.1±86.5** | **42.1±0.6** | **594.4±63.2** | **28.2±2.7** |
| DS-Sensor | 351.5±28.0 | 18.6±0.7 | 186.5±16.1 | 10.7±1.4 |

因果解释：

- 多物体训练/测试中，禁用 tactile 后 seen 和 unseen 都大幅下降。
- 这比单物体更有说服力：object shape/pose 变化时，二值接触模式提供了 object-in-hand state 的关键信息。

### 3.4 Table I：真实机器人 seen/unseen objects

Table I 很大。下面把每类 5 个物体的平均 CRA/TTF 从表中汇总：

| Method | Seen Avg CRA | Seen Avg TTF | Unseen Avg CRA | Unseen Avg TTF |
|---|---:|---:|---:|---:|
| Open-loop | 0.55 | 14.86s | 0.65 | 18.00s |
| No-Sensor | 0.27 | 10.94s | 0.30 | 8.87s |
| CT-Sensor | 1.72 | 18.60s | 1.28 | 20.26s |
| Ours binary Sensor | **3.43** | **29.07s** | **2.48** | **28.73s** |

代表性真实物体：

| Object | Ours CRA | Ours TTF |
|---|---:|---:|
| Seen C1 | 4.91±0.52 | 30.00±0.00 |
| Seen C4 | 4.50±1.73 | 30.00±0.00 |
| Tomato | 1.08±0.14 | 27.33±4.62 |
| Apple | 2.67±1.04 | 30.00±0.00 |
| Orange | 3.00±1.32 | 30.00±0.00 |
| Soupcan | 4.25±1.56 | 27.33±4.62 |
| Rubber Duck | 1.42±0.38 | 29.00±1.73 |

因果解释：

- Binary Sensor 的 seen/unseen 平均 TTF 都接近完整 30s，说明它不是只会在训练物体上短暂转几下。
- CT-Sensor 连续信号比 No-Sensor 好，但低于 binary sensor 且 object variance 大，支持论文观点：连续力信号 sim-to-real gap 更难。
- Open-loop 有时能维持较长 TTF，但 CRA 低，说明没有闭环触觉时很难持续推动旋转。

### 3.5 Table IV：哪些传感器重要

| Method | Cuboid CRR | Cuboid TTF | Rubber Duck CRR | Rubber Duck TTF |
|---|---:|---:|---:|---:|
| Sensor | **4.91±0.52** | **30.00±0.00** | **1.42±0.38** | **29.00±1.73** |
| DS-Sensor | 0.25±0.25 | 7.67±6.80 | 0.33±0.29 | 20.00±17.32 |
| No-Fingertip | 0.17±0.29 | 3.33±5.77 | 0.42±0.14 | 17.00±2.64 |
| No-Palm | 0.42±0.38 | 17.00±14.73 | 0.42±0.14 | 16.67±11.72 |

因果解释：

- 去掉 fingertip 或 palm 都接近 DS-Sensor，证明“全手覆盖”不是装饰。
- Palm sensors 提供 object 在手心位置；fingertip sensors 提供推动旋转时的关键 contact。两类缺一不可。

### 3.6 Shape understanding：触觉是否真的编码形状

论文用 z-axis rotation policy 收集 55000 rollouts，每个 rollout 200 control steps，训练 temporal-CNN 从 rollout 预测 object shape。

| Input | Shape reconstruction MSE |
|---|---:|
| w/o touch | 0.45 |
| w/ touch | **0.22** |

这说明二值触觉不只是帮助控制，还在 rollout 时序中包含 object shape 信息。它不是显式 pose estimator，但 contact mode sequence 让网络能反推形状。

### 3.7 Table V：x/y/z 轴旋转

| Rotation | Seen Obj CRR | Seen TTF | Unseen Obj CRR | Unseen TTF |
|---|---:|---:|---:|---:|
| x-axis | 1.68±0.78 | 24.13±6.04 | **2.71±1.37** | 18.2±9.19 |
| y-axis | 1.88±0.38 | 22.46±4.81 | 1.05±0.56 | 23.13±3.01 |
| z-axis | **3.43±1.22** | **29.06±1.45** | 2.48±1.27 | **28.73±1.34** |

因果解释：

- z-axis 最稳定；x/y 可行但更困难。
- 这说明论文的“x/y/z rotation primitives”成立，但不是任意轴统一高性能。
- 与 AnyRotate 相比，这篇更像单轴/分轴 primitive，AnyRotate 后续把它扩展到 arbitrary axis + gravity-invariant setting。

### 3.8 Figure 7：sim/real 接触模式对齐

Figure 7 比较了 cuboid rotation 中 400 steps 的 sim 和 real contact signals。论文观察：

- sim 信号在时间轴上略 dense；
- sim 在 sensor 轴上略 richer；
- 部分 sensors（如 1 和 10）在 sim 中更容易激活；
- 但总体 pattern 相似。

这正是二值化 transfer 的证据边界：不是 exact match，而是 policy 在 0.4s local windows 里看到的模式分布足够接近。

## 4. 核心洞见

### 4.1 Touch Dexterity 的真正 insight

Touch Dexterity 的核心 insight 是：

$$
\text{tactile information for control}
\neq
\text{high-resolution tactile measurement}.
$$

对 in-hand rotation，策略首先需要稳定知道：

- object 在 palm 哪里；
- 哪些 fingertips 正在接触；
- 推动 finger 是否真的碰到了 object；
- object 是否滑向危险区域。

这些信息可以由全手二值接触模式提供。

### 4.2 为什么 binary touch 比 continuous touch 迁移更好

Continuous tactile signal 把 force calibration error 直接喂给策略：

$$
F^{\mathrm{sim}}\ne F^{\mathrm{real}}.
$$

Binary touch 只关心：

$$
\mathbf 1[F>\theta].
$$

因此当误差没有跨过 threshold，policy 的 observation 完全一致。这就是为什么 CT-Sensor 在真实中虽然比 No-Sensor 好，但泛化和方差不如 binary Sensor。

### 4.3 “Less is more”的边界

二值触觉不是永远更好。它适合：

- contact-rich，但不需要精细力幅值控制；
- 目标是维持/切换接触模式；
- sim continuous force 不可信；
- 传感器成本和覆盖优先于分辨率。

它不适合：

- 易碎物体；
- 精密力控；
- 需要剪切/滑移方向；
- 多接触点精确几何估计；
- 高速动态接触。

## 5. 替代方案与理论局限

### 5.1 理论维度

二值触觉观测的是 contact mode：

$$
\sigma_t
=
\{i:b_{t,i}=1\}.
$$

这对应接触力学中的 active contact constraints，但它没有提供：

$$
f_n,\quad f_t,\quad \tau,\quad \mu,\quad \delta,\quad \dot\delta.
$$

因此它能帮策略做 mode switching，但不能精细调节接触力。

### 5.2 算法维度

| 局限 | 影响 |
|---|---|
| MLP + 3-history stack | 时序建模有限，不如 TCN/RNN/Transformer 显式估计状态 |
| Policy 无 object pose | 只能通过 contact mode 间接推断，复杂物体可能失败 |
| 需要大量 DR 和 system ID | 二值化不是替代全部 sim-to-real 工程 |
| x/y axis 较弱 | 三轴 primitive 可行，但性能不均衡 |
| CT-Sensor 结果不稳定 | 连续触觉若无良好表征/标定，反而引入 gap |

### 5.3 工程/实验维度

- FSR 成本低，但耐久性、安装一致性、阈值漂移是现实问题。
- 只覆盖 hand 的一侧，换 sensor layout 需要重新训练。
- 控制频率 10Hz，对高速转笔不够。
- 任务是 object on palm 的 in-hand rotation，不是 free-space aerial manipulation。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔的直接迁移

Touch Dexterity 给 LinkerHand 的第一个建议不是“上复杂触觉模型”，而是建立最低强 baseline：

$$
\tau_{\mathrm{raw}}
\rightarrow
b_t=\mathbf 1[\tau_{\mathrm{raw}}>\theta]
\rightarrow
\pi(a_t|q_t,\dot q_t,b_{t-H:t},a_{t-1},\hat k).
$$

如果这个 baseline 已经显著提升 PPO exploration，那么高维 tactile model 的价值就可以被更严格地评估。

### 6.2 对 WMTS 的结合

| WMTS 模块 | Touch Dexterity 启发 |
|---|---|
| latent task generation | 生成不同 contact mode sequence 的子任务 |
| PPO Oracle | 用 binary contact mask 提升早期接触探索 |
| Diffusion/Flow generalist | 将 contact mask history 作为 action generation condition |
| Ensemble World Model | 预测下一步 contact mode $\sigma_{t+1}$ 和掉落风险 |
| real fine-tuning | 通过 threshold calibration 降低 tactile observation gap |

最有价值的是把 contact mode 变成显式可预测变量。世界模型不只预测 object pose，还应预测：

$$
p(b_{t+1}|b_{\le t},q_{\le t},a_t).
$$

### 6.3 对转笔任务的必要扩展

转笔比 Touch Dexterity 更难，因为：

- 物体不是稳定躺在 palm；
- 有 aerial phase；
- 接触时间更短；
- 切向速度和冲击更强；
- 需要更高频控制。

因此二值触觉可以作为：

| 用法 | 价值 |
|---|---|
| contact/no-contact event detector | 判断 catch 是否成功 |
| phase boundary detector | push/release/catch/regrasp 切换 |
| safety trigger | 检测 object lost contact |
| sparse reward source | contact event shaping |

但它不能替代：

- force magnitude；
- slip direction；
- contact patch geometry；
- high-frequency tactile dynamics。

### 6.4 可验证实验建议

| 实验 | 设计 | 证伪条件 |
|---|---|---|
| binary tactile baseline | LinkerHand PPO 加/不加 threshold contact mask | 二值触觉不提升 sample efficiency 或 sim-to-real |
| sensor coverage ablation | fingertip-only、palm-only、full-hand | full-hand 不显著优于局部，说明布局不是瓶颈 |
| binary vs continuous | raw force/taxel vs threshold mask vs dense learned features | continuous 更稳，说明标定足够好，无需二值化 |
| contact-mode world model | 预测下一步 contact mask / object loss | 预测 contact 与真实失败无关 |
| high-frequency requirement | 10/20/50Hz tactile-control loop 比较 | 低频无法 catch/recover，需硬件升级 |

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

本文是 PPO + asymmetric critic 的经典 sim-to-real 例子。关键不是复杂算法，而是把 observation 设计成更容易 transfer 的 binary contact mode。Policy gradient 学到的是接触模式到关节位置增量的闭环映射。

### 7.2 与 [[SignalProcessing]] 的联系

二值化是 1-bit quantization。它牺牲 amplitude resolution，但极大降低 calibration demand。对噪声和 domain shift 的鲁棒性来自 threshold invariance，而不是来自更强神经网络。

### 7.3 与 [[ContactMechanics]] 的联系

Contact mode $\sigma_t$ 是 hybrid contact dynamics 的离散状态。Touch Dexterity 的传感器让策略直接观察这个离散状态的一部分，从而能在 finger gaiting 中切换动作。

### 7.4 与 [[RepresentationLearning]] 的联系

这篇论文的表征思想是：不要把 tactile representation 的好坏只等同于分辨率；coverage、稳定性、sim-to-real invariance 也是表征质量的一部分。16 个 1-bit sensors 在控制任务中可能比少量高维但局部/难对齐传感器更有用。

### 7.5 与 [[ControlTheory]] 的联系

Policy 输出位置目标，PD controller 执行。EMA action smoothing 和 work/torque penalties 都是在让 learned policy 更像可部署控制器，而不是只在仿真中追求旋转奖励。

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “它真的是只靠触觉吗？” | 无视觉，但仍用本体、previous target、rotation axis；触觉是 binary contact |
| “二值化为什么能 sim-to-real？” | continuous force gap 被 threshold 吸收；Figure 7 显示 sim/real pattern 相似但非完全一致 |
| “全手覆盖重要吗？” | Table IV：No-Fingertip / No-Palm 都接近失败，palm 和 fingertip 都必要 |
| “连续力为什么不更好？” | CT-Sensor 比 No-Sensor 好，但真实泛化和方差不如 binary，说明 continuous force gap 更大 |
| “对转笔怎么用？” | 作为 contact event / phase detector baseline；不够处理 shear、force magnitude 和高速 aerial phase |

## References

- Yin, Z.-H., Huang, B., Qin, Y., Chen, Q., Wang, X. **Rotating without Seeing: Towards In-hand Dexterity through Touch**. ICRA 2023.
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]]
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]]
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]]
- [[ReinforcementLearning]]
- [[SignalProcessing]]
- [[ContactMechanics]]
- [[RepresentationLearning]]
- [[ControlTheory]]
