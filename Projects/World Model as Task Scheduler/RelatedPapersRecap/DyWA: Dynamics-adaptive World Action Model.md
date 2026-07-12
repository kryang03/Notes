---
tags:
  - paper
  - world-action-model
  - dynamics-adaptation
  - non-prehensile-manipulation
  - teacher-student
  - sim-to-real
  - WMTS
aliases:
  - DyWA
  - Dynamics-Adaptive World Action Model
paper-year: 2025
read-date: 2026-06-15
venue: arXiv 2503.16806 (PKU-EPIC / Galbot)
paper-pdf: "[[DyWA: Dynamics-adaptive World Action Model.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# DyWA: Dynamics-adaptive World Action Model

> [!abstract] 核心贡献
> 在**单视角点云、无位姿跟踪**的最难设定下做可泛化的 6D 非抓取重排（推/拨/翻/滑）。诊断出 teacher→student 蒸馏掉点的三因（单视角部分可观、Markovian student 只学到跨物理的"平均行为"、传统蒸馏只监督 latent+动作信号太弱），对症下三招：(1) **Dynamics Adaptation Module**（RMA 式，用历史 obs-action 估计动力学嵌入，补回缺失的几何+物理）；(2) **World Action Model**（动作头与"下一任务状态"预测头联合训练，多一路监督信号）；(3) 用 **FiLM** 把动力学嵌入调制进 world action model。仿真最难赛道比基线 **+31.5%** 成功率，真机 10 物体 **68% vs CORN 36%**，且零样本 sim-to-real、对摩擦/质量分布变化鲁棒。**它是用户 DNPM（动态非抓取/转笔）的同域工作、也是 WMTS "teacher→generalist + 动力学自适应" 的现成骨架——但其"world model"是最弱义的（仅辅助下一状态回归，无 rollout/无 ranking），与 WMTS 需要的"world model 当调度器"不是一回事。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度]] — PPO 训 privileged teacher；DAgger 蒸馏 student；RMA 式 domain adaptation（历史编码器≈在线系统辨识）。
> - [[ControlTheory]] — 变阻抗控制（variable impedance）做接触力调节；阻尼最小二乘 IK 把 EE 残差解成关节目标。
> - [[RepresentationLearning#4.5 面向学习的旋转表示：为什么神经网络回归旋转要用 6D]] — 任务状态用 9D 连续旋转表示回归下一状态（呼应 [[On the Continuity of Rotation Representations in Neural Networks]]）。
> - [[EmbodiedAI]] — teacher-student（privileged→partial）sim-to-real、domain randomization、单相机部署。
> - [[Final_WMTS]] — teacher→generalist 蒸馏范式 + **动力学自适应嵌入**正对应 WMTS 的 Oracle→DP generalist 与 **LAAA**（延迟/温漂条件化适配）；FiLM 是注入 actuator/上下文的轻量手段。
> - [[Dynamic Non-Prehensile Manipulation]] — **同一任务族**：DyWA 是桌面准静态非抓取，DNPM/转笔是手内高速**动态**非抓取；DyWA 的框架可借，动力学体制不同（见 §6）。
>
> **核心技术**: Teacher-Student Distillation (PPO+DAgger), RMA Dynamics Adaptation, World Action Model (joint action + next-state), FiLM 条件化, Variable Impedance Control, 9D 旋转表示, DexGraspNet 资产 + IsaacGym

## 0. 阅读定位与范本价值

这篇在知识库里身兼两职。对 [[Dynamic Non-Prehensile Manipulation|DNPM]]：它就是非抓取操作的同域 SOTA，给出"如何在 single-view + 无 tracking 下把接触密集的推翻任务做泛化"的完整配方。对 [[Final_WMTS|WMTS]]：它的 teacher→student + 动力学自适应骨架，几乎是 WMTS "PPO Oracle → DP generalist + 真机适配" 的镜像。

但**最关键的阅读任务是辨名**：DyWA 把方法叫 "World **Action** Model"，与用户项目 "World Model as Task **Scheduler**" 只差一词，极易混淆。读它必须看清——DyWA 的 "world model" 是**最弱义**的：一个与动作头并联的"下一任务状态回归头"，**不做 rollout、不做想象、不做 ranking、不参与规划**。这与 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] 的 latent imagination、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]] 的 dream-MDP 都不同。看清这点，才能正确判断 DyWA 哪些能搬进 WMTS、哪些不能。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
非抓取 6D 重排在仿真里用 privileged RL teacher（全点云+任务状态+物理参数）能做得很好，但蒸馏成**真机可用的 student（单视角部分点云、无位姿跟踪）**后成功率暴跌。DyWA 系统诊断这次掉点的三因并逐一修复，把 student 在最难赛道从 ~50% 拉回 ~82%。

### 1.2 直观隐喻
teacher 是"开了上帝视角（知道物体全貌、质量、摩擦）的老手"；student 只有"单眼瞄一眼 + 摸过去的历史手感"。直接抄老手的动作（传统蒸馏）学不会，因为 student 缺两样东西：**看不全的几何**和**摸不到的物理**。DyWA 让 student 做两件补救：(a) 从**过去几步的手感序列**反推"这次的物体大概多重、多滑"（dynamics adaptation）；(b) 不只抄动作，还**预判这一推之后物体会到哪**（world action model）——逼它把"动作→后果"的因果学进表征。

可证伪含义：优势应集中在"**部分可观 + 物理变化大**"的设定；若给全点云+已知位姿（easy 赛道），三招带来的增益应当很小——Table 1 正是如此（easy 赛道大家都 ~87，难赛道才拉开）。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| Planning-based（接触模式松弛/互补约束） | 显式接触力学 + 已知物理 | 需 mass/friction/CAD 先验；真实未知物体不适用 |
| HACMan（primitive + 表面点 RL） | 在物体表面选接触点+方向、执行原语 | 开环原语、对复杂几何/物理适应差；6D 目标下成功率极低 |
| CORN（closed-loop teacher-student） | RL teacher + 点云 student、闭环 | **单视角+未知状态**下从 ~80 跌到 ~30/50（部分可观+物理变化） |
| RMA（仅 dynamics adaptation） | 历史 obs-action → 动力学嵌入 | 单用只 +5.7%：缺结构化学习目标，嵌入学不深 |
| 仅 World Model（仅 next-state 预测） | 联合预测下一状态 | 单用只 +1.7%：缺动力学输入，无法推理交互效果 |
| **DyWA** | 三者协同 + FiLM 桥接 + 变阻抗 | 仅点云模态：对称/透明/镜面物体失效；准静态、非动态高速 |

### 1.4 Delta 分析
精确增量 = **RMA ⊕ 辅助下一状态预测 ⊕ FiLM**，且关键在"⊕"不是"+"：单加 world model（+1.7）或单加 dynamics adaptation（+5.7）都**只是边际**；两者**合用**才从 59.9→73.3 跳变，FiLM 再 +8.9 到 82.2。论文把这点明说成"non-trivial yet highly effective design choice"——**协同性（complementarity）本身就是核心卖点**，不是堆三个模块。

## 2. 核心方法与理论（原理与理论：从 teacher-student 到协同损失）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $P_t,J_t,E_t$ | 部分点云 / 关节 / EE 位姿 | 单相机 + 本体 | observed | student 的真实观测 | 单视角→几何残缺，是掉点根因之一 |
| $O_t=\{f_t^P,f_t^J,f_t^E\}$ | 编码后嵌入 | PointNet++ / MLP | learned | 观测嵌入 | $f_t^P$ 来自简化 PointNet++ |
| $P_G=G\,P_0$ | 点云 | 把初始点云变换到目标位姿 | computed | **视觉目标表示** | 用它**绕开未知任务状态** $S_t$ 作为输入 |
| $S_t$ | 相对 6D 变换 | 仿真/定义 | 监督目标 | 当前物体位姿→目标位姿 | 它是**预测目标**不是输入（真机未知） |
| $z_t$ | 动力学嵌入 | 1D CNN over $L$ 步历史 (Eq 3) | learned | 从历史 obs-action 估计的动力学上下文 | RMA 式；短历史→未探索接触模式滞后 |
| $f_t^{Geo},f_t^{Phy}$ | teacher 嵌入 | privileged 全点云 + 物理参数 | teacher 侧 | 蒸馏目标（监督 $z_t$） | 仅训练期可得，真机无 |
| $\gamma,\beta$ | FiLM 调制参数 | 两层 MLP(动力学嵌入) | learned | 逐特征缩放/平移 (Eq 5) | 只在**早层**密集插入，末层不调制 |
| $A_t$ | 动作=EE 残差 $\Delta T_{ee}\in SE(3)$ + 阻抗 $(P,\rho)\in\mathbb R^{7}$ | world action model | learned | 子目标残差 + 关节阻抗 | **不是力矩**；经变阻抗+IK 落地 |
| $\hat S_{t+1}=(\hat T_{t+1},\hat R_{t+1})$ | $\mathbb R^3\times SO(3)$ | world model 头 | learned | 预测下一任务状态 | **无 rollout**：只预测一步，不向前 imagine |

### 2.2 前置理论从零搭：privileged teacher-student 蒸馏

非抓取重排难拿专家示范，所以走 **teacher-student**：
1. **Teacher（PPO，200K 迭代）**：在 IsaacGym 里用**特权信息**（全物体点云、任务状态 $S_t$、物理参数 mass/friction/restitution）训一个 state-based RL 策略（reward 沿用 CORN）。特权信息让它在各种动力学下都强。
2. **Student（DAgger，500K 迭代）**：只用真机可得的 $\{P_t,J_t,E_t\}$ + 视觉目标 $P_G$，在 teacher 监督下蒸馏。DAgger 一开始用 teacher 动作执行、逐渐换上 student 动作（Fig 3 显示初始 loss 快速下降）。

**为什么会掉点（三因，逻辑链）**：
- **因(1) 部分可观**：单视角点云丢关键几何 → 动作学习缺线索。
- **因(2) Markovian 平均**：student 只看当前观测、无动力学记忆 → 对不同 mass/friction 只能学一个"平均动作"，哪个都不最优。
- **因(3) 蒸馏信号弱**：传统蒸馏只对齐 latent 特征 + 最终动作，**不足以**让 student 学到接触动作背后的动力学。

### 2.3 三招的无跳步推导

**招(1) Dynamics Adaptation（治因 1、2）**：在每个 $t$，把观测嵌入 $f_t^O$ 与上一步动作嵌入 $f_{t-1}^A$ 拼接，取 $L$ 个历史元组喂 1D CNN，得动力学嵌入（Eq 3）：
$$
z_t=\mathrm{Embed}\Big(\{\mathrm{concat}(f_{t-i-1}^{O},\,f_{t-i-2}^{A})\}_{i=1}^{L}\Big).
$$
为让 $z_t$ 学到"对的东西"，用 teacher 的特权嵌入做监督（Eq 4）：
$$
\mathcal L_{adapt}=\big\|\,z_t^{Geo,Phy}-\mathrm{concat}(f_t^{Geo},f_t^{Phy})\,\big\|_2 .
$$
即把 teacher 的**全点云几何 + 物理参数**蒸进一个**只靠历史**就能算的嵌入——真机没有特权信息时，靠"摸过的历史手感"补回来。这就是 RMA（Rapid Motor Adaptation）的核心思想。

**招(2) World Action Model（治因 3）**：让同一网络在出动作 $A_t$ 的同时，预测下一任务状态 $\hat S_{t+1}$。任务状态用 9D 旋转表示（[Zhou et al.]，连续可学，呼应 [[On the Continuity of Rotation Representations in Neural Networks]]），world model 损失（Eq 1）：
$$
\mathcal L_{world}=\|T_{t+1}-\hat T_{t+1}\|_2^2+\|R_{t+1}-\hat R_{t+1}\|_1 ,
$$
ground truth $(\hat T_{t+1},\hat R_{t+1})$ 取自仿真执行动作后的真实结果。动作头则用对 teacher 的模仿损失（Eq 2）：
$$
\mathcal L_{imitation}=\|A_t^{s}-A_t^{t}\|_2 .
$$
**为什么联合预测下一状态会帮动作学习**：next-state 回归给共享表征加了一路**超出 teacher 动作标签**的监督，逼表征把"动作→后果"的因果编码进去；Fig 3 实测——加 world modeling 后**模仿 loss 收敛更快**（即论文说的 synergy）。注意：这是**辅助多任务训练**，不是 Dreamer 式"在模型里 rollout 再算价值"。

**招(3) FiLM 桥接**：把动力学嵌入解码后，用 FiLM（Eq 5）调制 world action model 的中间特征：
$$
\mathrm{FiLM}(f\mid\gamma,\beta)=\gamma f+\beta ,
$$
$\gamma,\beta$ 由"两层 MLP(动力学嵌入)"产生，**密集插在早层、末层不调制**。比直接 concat 更结构化（RMA+FiLM：65.6→70.0；三件套：→82.2）。

**总目标（Eq 7）**：$\;\mathcal L=\mathcal L_{imitation}+\mathcal L_{world}+\mathcal L_{adapt}.$

### 2.4 动作落地：变阻抗 + IK（接触密集的关键）
动作空间 = EE 子目标残差 $\Delta T_{ee}\in SE(3)$ + 关节空间阻抗（位置增益 $P\in\mathbb R^7$、阻尼因子 $\rho\in\mathbb R^7$，速度增益 $D=\rho\sqrt{P}$）。用阻尼最小二乘 IK 解关节目标（Eq 6）：
$$
q_d=q_t+\mathrm{IK}(\Delta T_{ee}),
$$
再交关节空间阻抗控制器（Polymetis API）生成命令。**变阻抗是接触密集操作能调节交互力的关键**——这点对灵巧手直接相关。

### 2.5 概念边界与符号陷阱（对 WMTS 命名极重要）
- **"world model" 的三种义项**，库里要分清：
  1. [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]：latent imagination rollout + analytic value gradient（**训策略**）。
  2. [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]/[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]：在 WM 内构 MDP 做 RL/规划（**rollout + 价值/成本**）。
  3. **DyWA**：与动作头并联的**一步下一状态回归头**，无 rollout、无价值、无 ranking——最弱义。
  WMTS 要的是义项 1/2 的"rollout 当调度器/筛选器"，**DyWA 这层不提供**（见 §6 批判）。
- $S_t$（任务状态）是**预测目标**不是 student 输入——真机未知，所以用 $P_G=GP_0$ 视觉目标替代。
- $A_t$ 是 **EE 残差 + 阻抗**，经变阻抗+IK 落地，不是直接力矩。
- $z_t$ 由**短历史**估计：遇到未探索的接触模式会**滞后**（§4.3 失效点）。
- world model 预测的是**物体级任务状态**，非像素、非 latent——object-centric，让策略聚焦任务相关动力学。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
IsaacGym + DexGraspNet **323 训练物体**；测试集 10 个几何多样物体 × 5 尺寸 = **50 评测物体**。全程随机化 mass/scale/friction/restitution；student 训练再注入 torque/点云/目标位姿扰动以助 sim-to-real。基准建在 CORN 之上，**三赛道**：Known State(3 view) / Unknown State(3 view) / **Unknown State(1 view，最现实最难)**。成功判据：终位姿距目标 < 0.05 m 且 < 0.1 rad。基线 HACMan（primitive）、CORN、CORN(PN++ 增强版)。

### 3.2 关键结果与因果解释（Table 1）

| 方法 | 类型 | Known(3v) Seen/Unseen | Unknown(3v) Seen/Unseen | **Unknown(1v) Seen/Unseen** |
|---|---|---|---|---|
| HACMan | primitive | 3.8 / 5.7 | 3.0 / 4.1 | 1.5 / 2.9 |
| CORN | closed-loop | 86.8 / 79.9 | 46.0 / 47.8 | 29.0 / 29.8 |
| CORN (PN++) | closed-loop | 87.3 / 84.3 | 76.1 / 75.7 | 50.7 / 49.4 |
| **Ours (DyWA)** | closed-loop | **87.9 / 85.0** | **85.8 / 82.3** | **82.2 / 75.0** |

**因果解释（最重要的一张表）**：在 easy 赛道（已知状态、3 视角）所有强基线都 ~87，**DyWA 并不更高**——因为此时几何+状态已给全，三招无用武之地。一旦进入 **Unknown(1view)**，CORN 跌到 ~30、增强版 CORN(PN++) 跌到 ~50，而 DyWA 仅微降到 **82.2/75.0**。**正是"部分可观 + 物理变化"咬人的地方，动力学建模把别人跌掉的 30+ 个点接住了**（≥ +31.5%）。这条"easy 不分高下、hard 拉开差距"的对照，精确证伪/证实了 §1.2 的故事。

### 3.3 Ablation 因果链（Table 2，最难赛道 Unknown-1view，Seen/Unseen）

| W.M. | D.A. | FiLM | Seen | Unseen | 读法 |
|:--:|:--:|:--:|:--:|:--:|---|
| ✘ | ✘ | ✘ | 59.9 | 57.5 | DAgger 裸蒸馏（下界） |
| ✔ | ✘ | ✘ | 61.6 | 59.4 | 单 world model：**仅 +1.7** |
| ✘ | ✔ | ✘ | 65.6 | 57.9 | 单 RMA：**仅 +5.7** |
| ✘ | ✔ | ✔ | 70.0 | 63.7 | RMA+FiLM |
| ✔ | ✔ | ✘ | 73.3 | 59.4 | W.M.+D.A.（无 FiLM）：**跳到 73.3** |
| ✔ | ✔ | ✔ | **82.2** | **75.0** | 全开：FiLM 再 +8.9 |

**协同的因果链（论文核心论证）**：`单 W.M.(+1.7) 或单 D.A.(+5.7) 都只边际 → 因为 world model 没有动力学输入就无法推理交互效果，dynamics adaptation 没有结构化学习目标就学不深 → 两者合用互补 → 59.9 跳到 73.3 → FiLM 提供比 concat 更结构化的条件化 → 82.2`。要点：**这是 1+1≫2 的协同，不是模块叠加**——移除任一支柱，另一支柱也跟着失效。

### 3.4 真机结果与因果（Table 3 / Table 4）
- **Table 3（10 物体×5 次）**：DyWA **34/50 (68%)** vs CORN(带 tracking) **18/50 (36%)**。差距最大处恰是**打滑**（YCB-Bottle 0/5→3/5）与**非均匀质量**（半满水瓶 0/5→4/5）——CORN 的外置 tracking 在单视角遮挡+真实位姿误差下崩，DyWA 无需 tracking。
- **Table 4（4 级摩擦 μ1<μ2<μ3<μ4）**：去掉 D.A. 时执行时间随摩擦**失控膨胀**（65→81→96→124 s），成功率也抖；带 D.A. 则**成功率与时间双双稳定**（4/5；45/50/49/51 s）。**因果**：动力学自适应让策略按当前摩擦实时调整接触策略，而非用"平均动作"硬怼——这正是 §1.2"摸出手感"的真机证据。

### 3.5 工程约束与实验边界
- 准静态桌面重排，非动态高速；Franka 单臂 + RealSense D435 侧视。
- 仅点云模态（见 §5 局限）。
- teacher 用特权信息训，student 蒸馏——真机零样本、无 fine-tune。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**把 teacher-student 蒸馏的掉点拆成"看不全的几何 + 摸不到的物理 + 监督信号太弱"三因，并证明：用历史估计动力学（RMA）与联合预测下一状态（辅助 world modeling）这两件单独都只边际有用的事，合在一起（FiLM 桥接）会产生强协同**——在部分可观、物理多变的真实设定下把成功率拉回特权 teacher 水平。

### 4.2 为什么这个设计有效
(1) dynamics adaptation 把真机缺失的特权信息从"历史手感"里反推回来；(2) next-state 预测给共享表征加了一路因果监督，让动作头不只是模仿、还理解后果（Fig 3 收敛更快）；(3) FiLM 让动力学上下文以结构化方式逐特征调制，比 concat 更有效；(4) 变阻抗给接触密集动作真正的力调节能力。

### 4.3 什么时候会失效（含论文自陈局限）
- **仅点云**：对称物体几何歧义、透明/镜面物体深度残缺 → 失败（论文明列）。
- **短历史动力学嵌入**：遇到训练未覆盖的接触模式会滞后，需主动试探动作校准。
- **准静态假设**：方法在桌面低速接触验证；高速动态接触（转笔级）未涉及。
- **"world model" 无 rollout**：只能预测一步后果，不能前瞻多步做规划/安全过滤。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
DyWA 不是 model-based planning，也不是 latent imagination；它是**多任务监督学习**（模仿 + 下一状态回归 + 特权蒸馏）。因此没有 Dreamer/DiWA 的"在模型里优化策略"的能力，也没有 SafeDreamer 的成本前瞻。它的泛化来自 domain randomization + 历史自适应的**统计覆盖**，而非显式物理或 rollout——分布外的接触体制无保证。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 DyWA 关系 |
|---|---|---|---|
| HACMan（primitive RL） | 接触点可解释 | 开环原语、6D 差 | DyWA 的闭环+变阻抗胜之 |
| CORN（teacher-student） | 闭环点云 | 单视角/未知态崩 | DyWA 的直接前作与主对照 |
| RMA（纯 adaptation） | 历史估动力学 | 无结构目标、单用弱 | DyWA 招(1) 的来源 |
| Dreamer/DiWA（rollout WM） | 可在想象里训策略 | 需可信 rollout/可微 | **DyWA 不做 rollout**，互补 |

### 5.3 工程/实验维度
点云模态局限、短历史滞后、变阻抗调参、teacher 特权 reward 设计（沿用 CORN）是主要工程点；高速动态接触、触觉、灵巧手多指未覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 DNPM（转笔/动态非抓取）的迁移
DyWA 与 [[Dynamic Non-Prehensile Manipulation|DNPM]] **同任务族**，是最该精读的结构范本，但要分清体制差异：

| 维度 | DyWA（桌面准静态） | DNPM/转笔（手内动态高速） | 迁移设计 |
|---|---|---|---|
| 接触体制 | 低速、准静态推翻 | 高速、动量主导、频繁接触建立/断开 | 框架可借；需把 next-state 预测换成**短时动力学 + 触觉**目标 |
| 动力学自适应 | 历史 obs-action → $z_t$ | 笔质量/重心/指面摩擦/温漂 | 直接复用 RMA 思路，输入加**触觉序列** |
| 动作落地 | EE 残差 + 变阻抗 | 多指关节 + 力/阻抗 | 变阻抗思想可移到指尖力调节 |
| 目标表示 | $P_G=GP_0$ 视觉目标 | 笔的目标姿态/旋转相位 | 用相位/姿态目标替代点云目标 |

### 6.2 对 WMTS 的迁移（含关键批判）

| WMTS 模块 | DyWA 对应 | 迁移设计 |
|---|---|---|
| **PPO Oracle → DP generalist** | PPO teacher → DAgger student | 蒸馏范式直接对应；teacher 用 sim 特权状态、generalist 用真机部分观测 |
| **真机适配 / LAAA** | Dynamics Adaptation Module | 用历史(含触觉)估 actuator 延迟/温漂/笔参，FiLM 注入 generalist——**LAAA 的现成实现** |
| 上下文注入 | FiLM 条件化 | 把 latency/thermal/object-id 上下文以 FiLM 调制进 DP/PPO，比 concat 更结构化 |
| **world model 调度** | ✘（DyWA 无 rollout） | **DyWA 这层不能用**：WMTS 需要 ensemble rollout + ranking + uncertainty（来自 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]/[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]） |

**核心论证（critical thinking）**：DyWA 给 WMTS 的真正价值在**前半段**（teacher→generalist 蒸馏 + 动力学自适应 + FiLM），它把"如何在真机部分观测下保住特权 teacher 的能力"做成了可复制的配方，正对应 WMTS 的 Oracle→generalist + LAAA。但**后半段必须警惕命名陷阱**：DyWA 的 "World Action Model" 只是一步 next-state 回归的辅助头，**没有 rollout、没有 ranking、没有不确定性**——而 WMTS 的 "World Model as Task **Scheduler**" 立身之本恰恰是"用 WM 前瞻 rollout 给任务/动作块排序并做安全过滤"。所以正确组合是：**用 DyWA 的蒸馏+自适应骨架训出 generalist，再叠上 Dreamer/DiWA/SafeDreamer 的 ensemble-rollout 调度与安全层**——两半拼起来才是完整的 WMTS，单靠 DyWA 不够。

### 6.3 可验证实验建议
- **LAAA 复刻**：在手内任务上实现 DyWA 式 dynamics adaptation（输入加触觉序列），FiLM 注入 DP generalist；对照"无适配 / concat 注入 / FiLM 注入"，测温漂/延迟注入后的恢复速度与成功率（直接对标 Table 4 的时间稳定性）。
- **协同性验证**：在转笔最小环境复刻 Table 2 的 2×2×2 消融，确认"辅助 next-state 预测 × dynamics adaptation"的协同在高速接触下是否仍成立（很可能需把 next-state 换成触觉/相位目标才成立）。
- **辨名实验**：对比 DyWA 式一步 next-state 头 vs Dreamer 式多步 rollout 在手内任务的调度价值，量化"无 rollout 的 world model"在 WMTS 调度上的不足。

### 6.4 不应过度外推的点
- 桌面准静态成功**不能**外推到手内高速动态接触；动力学体制不同。
- DyWA 的 "world model" 不是 WMTS 意义上的调度器，**不要**因同名而直接挪用。
- 仅点云模态在灵巧手上不够，需触觉/力作为一等输入。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
PPO 训 privileged teacher + DAgger 蒸馏 student 的 teacher-student RL（[[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度]]）；RMA 式 domain adaptation 把"在线系统辨识"压成历史编码器，是 sim-to-real RL 的主流范式之一。

### 与 [[ControlTheory]] 的联系
变阻抗控制（按任务实时调交互力）+ 阻尼最小二乘 IK（Eq 6）把 EE 残差解成关节目标——接触密集操作的底层控制接口；阻抗参数作为动作的一部分被策略输出。

### 与 [[EmbodiedAI]] 的联系
privileged→partial 蒸馏 + domain randomization + 单相机零样本 sim-to-real，是具身操作 sim-to-real 的代表配方；并展示与 VLM（SoFar）结合做语言条件目标、与抓取模型互补做 pre-grasping。

### 与 [[Final_WMTS]] 的联系
前半段（teacher→generalist 蒸馏 + dynamics adaptation + FiLM）= WMTS 的 Oracle→DP generalist + LAAA 现成骨架；后半段的 "world model" 不等于 WMTS 调度器，需叠加 Dreamer/DiWA/SafeDreamer 的 rollout/ranking/safety（§6.2）。

### 与 [[Dynamic Non-Prehensile Manipulation]] 的联系
同一任务族（非抓取重排）的桌面准静态 SOTA；DNPM/转笔是其动态高速版，框架可借、动力学体制需替换为短时+触觉建模（§6.1）。

## References
- 原始 PDF：[[DyWA: Dynamics-adaptive World Action Model.pdf]]（PKU-EPIC / Galbot，arXiv 2503.16806）
- 直接前作/对照：CORN、HACMan、RMA（dynamics adaptation 来源）
- 旋转表示：[[On the Continuity of Rotation Representations in Neural Networks]]（9D 旋转表示）
- 对照的"真 world model"：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
