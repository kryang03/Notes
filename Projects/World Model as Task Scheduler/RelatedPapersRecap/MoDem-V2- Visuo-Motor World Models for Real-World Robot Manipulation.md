---
tags:
  - paper
  - world-model
  - visuomotor
  - real-robot
  - dexterous-manipulation
  - safe-exploration
  - ensemble
  - WMTS
aliases:
  - MoDem-V2
paper-year: 2024
read-date: 2026-06-15
venue: ICRA 2024 (arXiv 2309.14236, Meta AI / UCSD)
paper-pdf: "[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# MoDem-V2: Visuo-Motor World Models for Real-World Robot Manipulation

> [!abstract] 核心贡献
> 首个**直接在真实世界**训练成功的"demo 增强视觉 MBRL"系统，学会接触密集操作（推、抓、**手内重定向**），只用原始视觉 + 本体感觉 + **稀疏奖励**。它把根因锁定为**不安全探索 + 过度乐观**：基线 MoDem（TD-MPC + demo）在真机上一开始就违反扭矩限、faults 硬件、学不动。MoDem-V2 在 MoDem 的规划里加三味药——**policy centering**（动作从 BC 策略采、不从全动作空间）、**agency transfer**（用 $\alpha:0\to1$ 从执行 BC 动作渐变到短程 MPC）、**actor-critic ensembles 的不确定性感知规划**（$\phi=w_1\,\mathrm{mean}(\phi^{1:M})+w_2\,\mathrm{std}(\phi^{1:M})$，$w_2<0$，即 **LCB** 惩罚过度乐观轨迹）——既保住样本效率又大幅降安全违例。**它对 WMTS 是分量最重的一篇：其 ensemble + LCB 几乎就是 WMTS reliability head 的实现原型，且是真机 10-DOF 手内重定向的最近灵巧先例。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — demo 增强 MBRL（TD-MPC/MoDem）；actor-critic ensemble 抗 overestimation；epistemic uncertainty。
> - [[ControlTheory]] — 短程 MPC（latent 空间）+ 价值终端；agency transfer 是 MPC 与 BC 的混合调度。
> - [[Optimization]] — MPPI 式轨迹加权采样（$\Omega=e^{\tau\phi}$ 更新 $\mu,\sigma$）；带不确定性惩罚的目标。
> - [[EmbodiedAI]] — 真机视觉 MBRL 数据飞轮；10-DOF D'Manus 手内重定向、Franka 推抓。
> - [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] / [[WorldModels#6.1 世界模型作安全调度器（Look-ahead Safety Filter）]] — actor-critic ensemble 的 $w_1\mathrm{mean}+w_2\mathrm{std}$（$w_2{<}0$）就是 LCB，把 epistemic 不确定性当规划护栏 + 安全过滤（**认知不确定性三用** 暗线的真机灵巧实证）。
> - [[Final_WMTS]] — **WMTS reliability head / 抗 model-exploitation 的实现原型**（ensemble + LCB）；安全靠保守探索（补 SafeDreamer）；demo-bootstrap + agency handover 对应 Oracle→generalist。
>
> **核心技术**: TD-MPC 无解码 latent WM (Eq 1), Policy Centering, Agency Transfer ($\alpha$ schedule), Actor-Critic Ensembles + LCB ($w_2{<}0$), MPPI 规划, 稀疏奖励 + demo BC

## 0. 阅读定位与范本价值

MoDem-V2 是 WMTS 的**安全与可靠性模块、以及真机灵巧落地**的最重要参照。它把贯穿 [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]/[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]/[[Robotic World Model: A Neural Network Simulator|RWM]] 的 **model-exploitation/过度乐观**主题，第一次在**真机接触密集 + 手内操作**上用 **ensemble + LCB** 正面解决——而前三篇要么没 ensemble（RWM 靠精度）、要么只在桌面/仿真（DiWA/World4RL）。

读它要抓两条线：(1) **可靠性机制**——actor-critic ensemble 的 $w_1\,\mathrm{mean}+w_2\,\mathrm{std}$（$w_2<0$）就是 LCB，是 WMTS reliability head / disagreement penalty 的现成实现；(2) **真机安全工程**——为什么硬限幅 + 扭矩惩罚不够（Fig 2），而"保守探索（policy centering + agency transfer）"够。它与 [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]（cost critic + 规划）形成**安全的两条互补路线**：SafeDreamer 显式建 cost、MoDem-V2 限制探索。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
真机视觉 MBRL 想免去仿真/状态估计/dense reward，但在接触密集高维空间里、仅靠稀疏视觉奖励探索，会产生**危险动作**（超扭矩、超接触力、硬件 fault）。MoDem-V2 主张：**保守探索**能在尊重真机安全约束的同时仍快而有效地学——关键是消除 MoDem 的"不安全探索 + 价值过度乐观"。

### 1.2 直观隐喻
MoDem 像"刚学车就在全油门范围乱试"——在还没见过的动作区域，world model/value 乱估，一脚下去就撞（超扭矩 fault）。MoDem-V2 改成"**先贴着教练示范开（BC 动作），随车技长进再逐步放开自主规划（agency transfer），且对没把握的路线主动减速（ensemble LCB 惩罚不确定）**"。可证伪含义：保守探索的收益应集中在"**安全约束硬、OOD 动作代价大**"的真机接触任务；纯仿真无安全代价时优势收窄。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| Sim-to-Real（DR/系统辨识） | 物理仿真 + 随机化 | 接触密集仿真难建难标定 |
| 硬限幅（torque/vel/acc 限） | 人设安全边界 | 静态、任务相关、太紧学不会/太松不安全（Fig 2） |
| 扭矩惩罚 | reward 里罚力矩 | **事后**、不阻止 onset 的危险动作（Fig 2 右，10⁻²~⁻⁴ 都失败） |
| MoDem（TD-MPC + demo） | 无解码 latent WM + MPC + demo BC | 探索激进：真机 onset 即超扭矩、faults、学不动 |
| **MoDem-V2** | MoDem + 三味药 | 仍需 demo；D'Manus 10-DOF reorientation 非高速；视觉 + 稀疏奖励 |

### 1.4 Delta 分析
精确增量（相对 MoDem）= **policy centering + agency transfer + actor-critic ensembles（LCB）**三者注入规划过程（Algorithm 1），把"激进、易 fault 的 MoDem"变成"保守、安全、仍样本高效的 MoDem-V2"。核心因果主张：**真机 MBRL 的瓶颈不在模型表达力，而在 onset 探索的安全与价值过度乐观**——三味药分别治"探索范围""自主权交接节奏""乐观估计"。

## 2. 核心方法与理论（原理与理论：TD-MPC 基座 + 三味药）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $s=(x,q)$ | 堆叠 RGB + 本体 | 真机相机/编码器 | observed | 高维观测（非真状态） | 物体位姿不可观，靠 $(x,q)$ 近似 |
| $z=h_\theta(s)$ | latent | 状态编码 | learned | TD-MPC 无解码 latent | **decoder-free**，不重构像素 |
| $z'=d_\theta(z,a)$ | latent | 动力学 | learned | latent 转移 | 联合嵌入预测学习 |
| $\hat r=R_\theta(z,a)$ | 标量 | reward 头 | learned | 稀疏奖励预测 | — |
| $\hat q=Q_\theta(z,a)$ | 标量 | 终端价值 | learned | TD 学习的价值 | 有 overestimation 偏差 |
| $\pi_\theta(z)$ | 动作 | policy guide | learned | 确定性策略（最大化 Q） | $\pi_\theta^{BC}$ = BC 预训练版 |
| $\alpha$ | $[0,1]$ | agency transfer | 调度 | 用 MPC rollout 的概率 | 0→1 线性增；agency handover |
| $\phi_\Gamma$ | 标量 | 轨迹价值 | computed | 轨迹累计回报 + 终端值 | 见 §2.3 LCB |
| $\phi^{1:M}_\Gamma$ | M 个 | ensemble 终端值 | computed | M 个独立价值估计 | std 即 epistemic uncertainty |
| $w_1{>}0,w_2{<}0$ | 权重 | 设计 | 固定 | **LCB**：均值奖、方差罚 | $w_2<0$ 是关键号 |
| $\Omega,\mu,\sigma,\tau$ | MPPI | 规划迭代 | 计算 | 轨迹加权采样分布 | $\Omega=e^{\tau\phi}$ |

### 2.2 基座：MoDem = TD-MPC + demonstrations（Eq 1）
TD-MPC 的**无解码 latent world model** 五件套：
$$
\text{编码 } z{=}h_\theta(s),\ \text{动力学 } z'{=}d_\theta(z,a),\ \text{奖励 } \hat r{=}R_\theta(z,a),\ \text{终端价值 } \hat q{=}Q_\theta(z,a),\ \text{策略 } \hat a{=}\pi_\theta(z).
$$
用 joint-embedding 预测 + reward 预测 + TD 学习端到端训（**不重构像素**，区别 STORM/World4RL）。MoDem 三阶段：① demo BC 预训练 $h_\theta,\pi_\theta$；② 用 $\pi_\theta\circ h_\theta$ seed 模型（注高斯噪声探索）；③ 在线交互 + 在所有数据（demo+seed+online）上迭代优化。规划 = latent 空间短程 MPC（用 $d_\theta,R_\theta,Q_\theta$）。

### 2.3 三味药（Algorithm 1，无跳步）
**药①：Policy centering**——不从整个动作空间采样，而是从学到的 BC 策略 $\pi_\theta^{BC}$ 采动作。`保守 → 减少 WM/value 在未见区域的评估 → 它们能更好分辨动作质量`。

**药②：Agency transfer（BC→MPC）**——onset 时 WM/value 只见过 BC 附近数据，立刻多步 MPC 会把 agent 带进不可恢复的未探索区。解法：用超参 $\alpha$（0→1 线性增）**从执行 BC 动作渐变到短程 MPC**：以概率 $1-\alpha$ 走 BC-centered（critic 评 $Q^{BC}_\theta$），以概率 $\alpha$ 走 policy ensemble + dynamics 规划。

**药③：Actor-critic ensembles + LCB**——两重作用：(i) 缓解 overestimation——**只用"非直接优化该 critic 的策略"产生的动作去评该 critic**（避免 actor 专门刷高自己的 critic）；(ii) M 个独立价值估计给出 epistemic uncertainty。融合（Algorithm 1 第 16 行）：
$$
\phi_\Gamma=w_1\,\mathrm{mean}(\phi^{1:M}_\Gamma)+w_2\,\mathrm{std}(\phi^{1:M}_\Gamma),\quad w_1>0,\ w_2<0,
$$
即 **LCB（lower confidence bound）**：奖均值、**罚不确定性** → 回避过度乐观的轨迹。最后 MPPI 加权（第 17-18 行）：$\Omega=e^{\tau\phi}$，更新 $\mu=\frac{\sum\Omega_i\Gamma_i}{\sum\Omega_i}$、$\sigma$，返回 $a\sim\mathcal N(\mu,I\sigma^2)$。

### 2.4 概念边界与符号陷阱
- **decoder-free latent WM**：TD-MPC 不重构观测，只在 latent 预测 reward/value/dynamics——又一种 "world model" 义项（≠ DyWA 状态回归、≠ World4RL 像素扩散、≠ RWM 观测高斯）。
- $w_2<0$ 是 LCB 的灵魂：把方差当**惩罚**而非奖励——这正是 WMTS 要的"对 WM 不确定处保守"。
- agency transfer 的 $\alpha$ 是**自主权交接**调度，不是探索噪声。
- 安全违例定义：真机 = 需人工干预的硬件 fault；仿真 = 超扭矩 或 接触力 >100N。
- 仍是稀疏奖励 + demo BC，不是 reward-free / demo-free。

### 2.5 信息流/算法机制（无代码）
观测 $(x,q)$ → $z_0=h_\theta$ → 以 $\alpha$ 决定 BC-centered 还是 ensemble 规划 → N 条轨迹在 latent rollout（$d_\theta$）累计 $R_\theta$ + 终端 $Q^{1:M}_\theta$ → LCB 融合 $\phi$ → MPPI 加权出动作 → 真机执行 → 数据入 replay → 更新 WM + ensemble critics + policy。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
硬件：Franka Panda 臂；推/抓用 Robotiq 二指夹爪；**手内重定向用 ROBEL 的 10-DOF D'Manus 手**；3 个 RealSense D435。4 任务（Planar/Inclined Pushing、Bin Picking、In-Hand Reorientation）sim + real。仅视觉 + 本体 + 稀疏奖励。基线 BC、MoDem、DAPG(state)、FERM。

### 3.2 关键结果与因果解释
- **Fig 2（核心）**：真机上 **MoDem onset 即违反扭矩限、学不动**；MoDem-V2 保守探索完成任务。仿真进一步显示**单纯扭矩惩罚（10⁻²/⁻³/⁻⁴）不能阻止安全违例**——因为它是事后惩罚，不阻止 onset 危险动作。
- **安全 + 样本效率兼得**：MoDem-V2 violations 显著低于 MoDem/baselines，同时保留 MoDem 的样本效率（四任务 success 曲线）。
- **真机学会接触密集 + 手内**：pushing/picking/in-hand reorientation 直接在真机学成——首个真机 demo 增强视觉 MBRL 成功案例。

### 3.3 Ablation / 对照因果链（三味药各自的贡献）
- `去 policy centering（全空间采样）→ WM/value 评 OOD 动作不准 → 选到危险/低质动作`。
- `去 agency transfer（onset 即 MPC）→ 多步规划把 agent 带进不可恢复未探索区`。
- `去 ensemble LCB（$w_2{=}0$）→ overestimation/过度乐观 → 选过度乐观动作`。
- `用扭矩惩罚替代保守探索 → 事后惩罚无效（Fig 2）`。

### 3.4 工程约束与实验边界
- 仍需 demo（BC 预训练 + seeding）。
- D'Manus 10-DOF 手内重定向是接触密集但**非高速动态**（≠ 转笔）。
- 视觉 + 稀疏奖励；decoder-free latent 对接触/力非显式建模。
- 安全违例靠定义（扭矩/接触力），非形式化证书。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**真机视觉 MBRL 的核心障碍是"不安全探索 + 价值过度乐观"，而非模型容量；用 policy centering（限探索范围）+ agency transfer（缓交接自主权）+ actor-critic ensemble LCB（罚不确定/过度乐观）三味保守探索药，就能在真机接触密集任务上既安全又样本高效地学。**

### 4.2 为什么这个设计有效
(1) policy centering 把探索关在 demo 附近、让 WM/value 评估可靠；(2) agency transfer 随 WM 覆盖增长再放权，避免 onset 进入不可恢复区；(3) ensemble LCB 显式惩罚 epistemic 不确定（过度乐观）轨迹；(4) MPPI 在保守候选里挑高（LCB）回报动作。

### 4.3 什么时候会失效
- 无 demo / demo 覆盖差时 policy centering 失去锚点。
- 高速动态接触（转笔）：D'Manus 慢速 reorientation 不能外推。
- 稀疏奖励仍需任务可定义的成功信号。
- LCB 权重 $w_2$ 过大过度保守、学不动；过小回到过度乐观。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
MoDem-V2 是 demo 增强 MBRL + 不确定性感知规划：安全是**经验性保守**（限探索 + LCB），非形式化安全集/CBF 证书。LCB 用 ensemble std 近似 epistemic uncertainty，质量取决于 ensemble 多样性。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 MoDem-V2 关系 |
|---|---|---|---|
| MoDem（TD-MPC+demo） | 样本高效 | 探索激进、真机 fault | MoDem-V2 的基座 |
| [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]] | 显式 cost critic + 规划 | 需定义 cost | **互补**：MoDem-V2 限探索、SafeDreamer 建 cost |
| DAPG/FERM | demo 增强 | 安全/样本逊于 V2 | 对照基线 |
| 硬限幅/扭矩惩罚 | 简单 | 静态/事后无效（Fig 2） | V2 用保守探索替代 |

### 5.3 工程/实验维度
demo 依赖、LCB 权重调参、ensemble 规模与多样性、decoder-free latent 对接触的表达、D'Manus 速度局限是主要边界；高速动态接触未覆盖。

## 6. 对用户研究的启发（未来与结合：WMTS 可靠性与安全的实现原型）

### 6.1 对 WMTS / 灵巧手的迁移

| WMTS 模块 | MoDem-V2 对应 | 迁移设计 |
|---|---|---|
| **Reliability head / 抗 model-exploitation** | actor-critic ensemble + LCB（$w_2{<}0$） | **直接采用**：ensemble WM/critic 的 $\mathrm{mean}-\lambda\,\mathrm{std}$ 给 task/chunk 打分，罚不确定 |
| **Safety filter** | 保守探索（policy centering + agency transfer） | 限制 PPO/DP 探索在 generalist 附近 + 随 WM 覆盖渐放权；补 SafeDreamer 的 cost 路线 |
| Oracle→generalist | demo BC 预训练 + seeding | PPO Oracle 当 demo 源 seed WM 与 generalist |
| 自主权调度 | agency transfer $\alpha:0\to1$ | 从 Oracle/DP 执行渐变到 WM-planning，随 ensemble 置信度调 $\alpha$ |
| 真机灵巧落地 | D'Manus 10-DOF 手内重定向 | 最近的真机灵巧 MBRL 先例（但需升到高速 + 21-DOF + 触觉） |

**核心论证（critical thinking）**：在所有 WM 论文里，MoDem-V2 给 WMTS 的**可靠性机制最具体**——它的 $\phi=w_1\,\mathrm{mean}(\phi^{1:M})+w_2\,\mathrm{std}(\phi^{1:M})$（$w_2<0$）就是 WMTS reliability head 想要的 ensemble-LCB，且**已在真机接触密集任务验证有效**。这与 [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]/[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]（单 WM 软肋）、[[Robotic World Model: A Neural Network Simulator|RWM]]（靠精度无 ensemble）形成闭环论证：**四篇共同指向"WMTS 必须用 ensemble + 不确定性惩罚"，而 MoDem-V2 是唯一把它在真机灵巧上做成的**。其次，MoDem-V2 的安全是"**限制探索**"，与 SafeDreamer 的"**显式 cost 规划**"互补——WMTS safety filter 宜两者叠加：ensemble-LCB 罚不确定 + cost critic 罚物理违例 + 保守探索限范围。**但要警惕外推**：D'Manus 10-DOF 准静态重定向 ≠ LinkerHand 21-DOF 高速转笔；decoder-free latent 对接触/力不显式，WMTS 要结构化 + 触觉。

### 6.2 可验证实验建议
- 在手内任务上实现 ensemble-LCB 排序：对 PPO/DP chunk 用 $\mathrm{mean}-\lambda\,\mathrm{std}$ 打分，对照 $w_2{=}0$（无 LCB），测 model-exploitation 与真机违例。
- agency transfer 复刻：$\alpha:0\to1$ 从 Oracle 执行渐变到 WM-planning，测 onset 安全与最终成功率。
- 保守探索 vs SafeDreamer cost：在超接触力/掉笔风险下对照两条安全路线及其叠加。

### 6.3 不应过度外推的点
- 真机成功在准静态接触（推/抓/慢速 reorientation），**不能**外推到高速转笔。
- LCB 用 ensemble std 近似 uncertainty，需保证 ensemble 多样性才可信。
- decoder-free latent 对接触/力弱，灵巧手需结构化 + 触觉一等输入。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
demo 增强 MBRL（TD-MPC/MoDem，Eq 1）；actor-critic ensemble 抗 overestimation（用非对应策略评 critic）；epistemic uncertainty 感知规划。

### 与 [[ControlTheory]] 的联系
latent 空间短程 MPC + 终端价值；agency transfer 是 BC 与 MPC 的混合调度（receding-horizon 思想）。

### 与 [[Optimization]] 的联系
MPPI 式轨迹加权采样（$\Omega=e^{\tau\phi}$ 更新 $\mu,\sigma$），目标含 LCB 不确定性惩罚——带正则的进化式规划优化。

### 与 [[EmbodiedAI]] 的联系
真机视觉 MBRL 数据飞轮；Franka + 10-DOF D'Manus 手内重定向，仅视觉 + 本体 + 稀疏奖励，最小人工干预。

### 与 [[WorldModels]] 的联系
MoDem-V2 是 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] 的 epistemic 不确定性在**真机接触密集**上的落地：$\phi=w_1\mathrm{mean}+w_2\mathrm{std}$（$w_2{<}0$）即 LCB，把 ensemble 分歧当规划护栏——这是 **认知不确定性三用** 暗线（护栏一用）的现成实现，也是 [[WorldModels#6.1 世界模型作安全调度器（Look-ahead Safety Filter）]] 的一条路线（保守探索限范围，与 SafeDreamer 的显式 cost 互补）。相对 [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] 的 ensemble-mean，它把抗乐观显式化为 std 惩罚。

### 与 [[Final_WMTS]] 的联系
WMTS reliability head（ensemble-LCB）与 safety filter（保守探索）的实现原型；与 DiWA/World4RL/RWM 共同论证"WMTS 必须 ensemble + 不确定性"，且 MoDem-V2 是唯一真机灵巧落地者；demo-bootstrap + agency handover 对应 Oracle→generalist 交接。

## References
- 原始 PDF：[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation.pdf]]（Meta AI / UCSD，arXiv 2309.14236）
- 基座：MoDem（TD-MPC + demo）、TD-MPC；对照 DAPG、FERM
- 安全互补：[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]
- 同主题（ensemble/抗 exploitation）：[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[Robotic World Model: A Neural Network Simulator|RWM]]
- 项目入口：[[Final_WMTS]]、WMTS_Reliability_Extensions
