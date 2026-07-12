---
tags:
  - paper
  - world-model
  - offline-rl
  - offline-to-online
  - real-world-adaptation
  - ensemble
  - WMTS
aliases:
  - FOWM
  - Finetuning Offline World Models
paper-year: 2023
read-date: 2026-06-15
venue: CoRL 2023 (UCSD / Tsinghua; Hansen, Xiaolong Wang)
paper-pdf: "[[Finetuning Offline World Models in the Real World.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# FOWM: Finetuning Offline World Models in the Real World

> [!abstract] 核心贡献
> 取离线 + 在线两者之长：**用真机离线数据预训练 world model（TD-MPC），再用极少在线交互（≤20 trials）微调**。核心难点是离线 WM 在规划时被查询到未见 state-action → **extrapolation 误差**（不止值高估，连 latent 动力学、reward 预测都外推失真）。FOWM 的关键招是**规划时的测试期不确定性正则**：用一个轻量 **Q-ensemble** 估 epistemic uncertainty $u_t=\mathrm{std}\{Q_\theta^{(i)}\}$，把规划回报改成 $\hat R=\gamma^h(Q-\lambda u_h)+\sum_t\gamma^t(R-\lambda u_t)$（Eq 4，**即 LCB**），惩罚高不确定动作。真机 xArm 视觉任务上把离线 WM 的成功率 **20 trials 内从 22%→67%**（pick + 未见干扰物），是首个真机 offline-to-online MBRL 微调工作。**它几乎就是 WMTS world-model 模块的精确配方：离线预训 WM + ≤1h 在线微调 + 规划时 LCB；Eq 4 就是 WMTS reliability head 的实现，且"微调中不确定性自然下降→保守度自适应"正合 WMTS 的真机适配。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — offline RL（extrapolation/overestimation）+ offline-to-online；IQL in-sample backup + AWR。
> - [[ControlTheory]] — TD-MPC 的 MPPI 规划（receding-horizon）；测试期在规划目标上加正则。
> - [[Optimization]] — expectile 回归（Eq 3）、AWR、MPPI 采样；LCB 风险正则（Eq 4）。
> - [[EmbodiedAI]] — 真机 xArm 像素输入、≤20 trials 少样本微调到未见任务。
> - [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] / [[WorldModels#6.4 真机在线适配]] — Q-ensemble 的 std 当 epistemic 不确定性，规划时 LCB（Eq 4）抑制 extrapolation；微调中不确定性自然下降 → 保守度自适应，正是 [[WorldModels#6.4 真机在线适配]] 的曲线（**认知不确定性三用** 暗线）。
> - [[Final_WMTS]] — **WMTS WM 模块的精确配方**：离线预训 + ≤1h 微调 + 规划 LCB；Eq 4 = reliability head；Q-ensemble 轻量选项。
>
> **核心技术**: TD-MPC 骨架, Q-ensemble epistemic uncertainty, 测试期 LCB 正则 (Eq 4), IQL in-sample TD-backup (Eq 3 expectile), AWR 策略, 平衡采样 (offline+online buffer)

## 0. 阅读定位与范本价值

FOWM 是 **WMTS world-model 模块最贴近的"完整配方"论文**——离线预训 WM + 少量在线微调 + 规划时不确定性正则，正是 WMTS"用离线数据训 WM、再用 ≤1h 真机数据微调、并在 WM-ranking 时按可靠性打分"的镜像。它与 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] 同属 Hansen/TD-MPC 系不确定性感知 MBRL，三者构成 WMTS reliability head 的演化：

- **PDDM**（2019）：ensemble 动力学，reward 取 ensemble **mean**（隐式抗乐观）。
- **MoDem-V2**（2024）：actor-critic ensemble，**显式 LCB**（$w_1\mathrm{mean}+w_2\mathrm{std}$），online-from-scratch + 保守探索。
- **FOWM**（2023）：**Q-ensemble LCB（Eq 4）**，**offline→online 微调** + IQL in-sample。

读它要抓两件事：(1) **为什么 offline WM 规划会崩**（extrapolation 不止在值，还在动力学/reward）；(2) **为什么"规划时加 LCB 正则"优于"训练时硬塞保守"**——因为规划是**非参数的、可在测试期优化任意目标**，且**微调中不确定性自然下降**，保守度自适应。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
RL 真机太费数据；offline RL 用固定数据集但有 state-action 分布偏移 → extrapolation 误差 → 被迫学过度保守策略，且难适应新任务。FOWM：**离线预训 WM，再用极少在线数据微调**——在线交互提供"自校准"（执行高估动作收到负反馈即修正），而 MBRL 规划的非参数性让我们能在测试期加不确定性正则抑制 extrapolation。

### 1.2 直观隐喻
离线 WM 像"只读过旧地图就上路"——遇到地图没标的路（OOD）会自信地瞎指（extrapolation）。FOWM 给规划器配一个"**几位专家投票的分歧度**（Q-ensemble std）"，分歧大的路就**扣分绕开**（LCB）；每跑一趟新路、把它补进地图（微调），分歧自然变小、胆子自然变大。可证伪含义：增益应集中在"**离线数据有限、需少样本适应新任务**"；数据已全覆盖时正则无用。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 在线 RL（含 TD-MPC） | 从交互学 | 真机数据海量；20 trials 从零学不动（实测 0%） |
| offline RL（CQL/IQL 等） | 固定数据集 + 训练时保守 | 分布偏移 → 过度保守、难适应新任务 |
| 纯 offline WM（TD-MPC 直接用） | latent WM + 规划 | **规划查 OOD → 动力学/reward/值全外推失真 → 不收敛** |
| **FOWM** | offline WM + 在线微调 + 规划 LCB | xArm 准静态（非灵巧）；Q-ensemble 仅值不确定性；TD-MPC latent 无结构/触觉 |

### 1.4 Delta 分析
精确增量 = **offline-to-online WM 微调** + **测试期 Q-ensemble LCB 正则（Eq 4）** + IQL in-sample backup（Eq 3）+ AWR + 平衡采样。相对 offline RL（训练时硬塞保守）：FOWM 把保守放到**规划测试期**（非参数、可自适应），微调中不确定性下降 → 自动从保守转探索。这是"规划 + 不确定性正则"相对"训练时保守"的结构性优势。

## 2. 核心方法与理论（原理与理论：TD-MPC + 离线修正 + LCB 规划）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $z=h_\theta(s)$ | latent | 编码 | learned | TD-MPC 表示 | decoder-free |
| $z'=d_\theta(z,a)$ | latent | 动力学 | learned | 预测下一 latent | 规划时查 OOD 会外推 |
| $\hat r=R_\theta,\hat q=Q_\theta,\hat a=\pi_\theta$ | 标量/动作 | 三头 | learned | reward/value/policy prior | — |
| $V_\theta(z)$ | 标量 | IQL 估计 | learned | state-conditional value | **in-sample**，避 OOD 动作 |
| $\tau$ | $(0,1)$ | expectile | 固定 | 越→1 越逼近 max | 小则更保守 (Eq 3) |
| $\{Q_\theta^{(i)}\}_{i=1}^N$ | N 个 | Q-ensemble | learned | epistemic uncertainty 代理 | 轻量（仅值，非全模型 ensemble） |
| $u_t=\mathrm{std}\{Q^{(i)}\}$ | 标量 | ensemble std | 计算 | 不确定性 | OOD 越大 |
| $\lambda$ | 系数 | 设计 | 固定 | LCB 正则强度 | offline/online 可不同 |
| $B_{off},B_{on}$ | replay | 双 buffer | — | 平衡采样 | 在线早期超采 |

### 2.2 TD-MPC 骨架（Eq 1-2）
五件套：表示 $z=h_\theta(s)$、latent 动力学 $z'=d_\theta(z,a)$、reward $\hat r=R_\theta$、终端值 $\hat q=Q_\theta$、policy prior $\hat a=\pi_\theta$。联合损失（Eq 1）含 latent 一致性 + reward + value(TD) + action。规划用 **MPPI** 采样动作序列，估计回报（Eq 2）$\hat R=\gamma^h Q_\theta(z_h,a_h)+\sum_t\gamma^t R_\theta(z_t,a_t)$，迭代拟合时变高斯最大化回报；一部分序列由 $\pi_\theta$ 生成作 behavioral prior。

### 2.3 离线修正：in-sample backup（Eq 3）+ AWR
离线时 TD-target $q=r+\gamma Q_\phi(z',\pi_\theta(z'))$ 会查 **out-of-sample 动作** $\pi_\theta(z')$ → 高估。借 IQL：引入 state-conditional $V_\theta$，TD-target 改为 $q_t=r_t+\gamma V_\theta(z'_t)$，用 **expectile 回归**（Eq 3）$L_V=|\tau-\mathbb 1_{\{Q-V<0\}}|(Q_\phi-V_\theta)^2$ 优化（$\tau\to1$ 逼近 max，小则保守）——**只用数据集内动作**。策略学习用 **AWR**（advantage weighted regression）同样避 OOD。

### 2.4 测试期 LCB 正则（Eq 4，核心）
即便值学得保守，规划（Eq 2）仍会在 OOD state-action 上查动力学/reward/值 → extrapolation。FOWM 用**轻量 Q-ensemble** $\{Q^{(i)}\}_{i=1}^N$ 的 std 当 epistemic uncertainty，把规划回报改为：
$$
\hat R=\gamma^h\big(Q_\theta(z_h,a_h)-\lambda u_h\big)+\sum_{t=0}^{h-1}\gamma^t\big(R_\theta(z_t,a_t)-\lambda u_t\big),\quad u_t=\mathrm{std}\{Q_\theta^{(i)}(z_t,a_t)\}_{i=1}^N.
$$
**这就是 LCB**：惩罚高不确定（OOD）动作、优先可靠高回报。妙处：(1) 规划**非参数**，可在测试期加任意目标、无需重训；(2) **微调中 epistemic uncertainty 自然下降** → 保守度自适应（早保守、后探索），同时适合 few-shot 与持续微调。平衡采样：$B_{off}+B_{on}$ 等比 mini-batch，在线数据早期超采，加速信息传播。

### 2.5 概念边界与符号陷阱
- LCB 用的是 **Q-ensemble**（仅值），不是全模型 ensemble——轻量、可真机实时，但只度量值不确定性（dynamics/reward 不确定性未直接 ensemble）。
- 保守度放在**规划测试期**（自适应），非训练时硬塞——与 CQL/IQL 的训练时保守不同。
- TD-MPC latent、decoder-free；xArm 像素输入；准静态。
- $\lambda$ offline/online 可不同（探索-利用平衡）。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
仿真（D4RL 等）+ 真机 **xArm** 视觉控制（raw pixels）：Reach / Pick / Kitchen + 未见任务变体（干扰物、物体形状/颜色）。离线预训 + ≤20 在线 trials 微调。对照 online TD-MPC、offline-to-online TD-MPC（无正则）、SOTA offline/online RL。18 trials × 2 seeds。

### 3.2 关键结果与因果解释（Table 1-2）
- **online TD-MPC 从零 = 0%**（20 trials 学不动）→ 印证少样本真机必须 offline 预训。
- **offline-to-online + LCB（Ours）最佳**：Reach 0 trial 72%→20 trial **94%**（vs 无正则 50→78）；Kitchen 11→**78%**；Pick 0→50%。**因果**：LCB 抑制规划 extrapolation，让少样本微调稳定收敛。
- **22%→67%（abstract）**：real visual pick + 未见干扰物，20 trials。
- **未见任务迁移（Table 2）**：Reach 干扰物 22→62、物体形状 44→78、Kitchen 干扰物 0→67——少样本适应新变体（也有失败：Pick 物体颜色 0%）。

### 3.3 Ablation / 对照因果链
- `去 LCB 正则 → 规划查 OOD → extrapolation → 不收敛/低成功`。
- `去 in-sample backup（用 OOD 动作 TD-target）→ 值高估`。
- `online from scratch（无 offline 预训）→ 20 trials 学不动（0%）`。
- `去平衡采样 → 在线信息传播慢`。

### 3.4 工程约束与实验边界
- xArm 视觉操作，**准静态、非灵巧 in-hand**。
- Q-ensemble 仅值不确定性（非全模型）。
- TD-MPC latent，无结构化/触觉。
- 个别任务（物体颜色）迁移失败。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**离线预训 WM + 少量在线微调时，规划会因 OOD 查询而 extrapolation 崩溃；用轻量 Q-ensemble 的不确定性在规划测试期做 LCB 正则（惩罚高不确定动作），既抑制 extrapolation 又自适应（微调中不确定性自然下降），从而真机 ≤20 trials 少样本适应到（未见）任务。** 一句话：**把保守放到非参数规划的测试期、并用 ensemble 不确定性自适应调节，优于训练时硬塞保守。**

### 4.2 为什么这个设计有效
(1) offline 预训给少样本起点；(2) in-sample backup + AWR 避训练时值高估；(3) Q-ensemble LCB 在规划时惩罚 OOD（extrapolation 的真正发生处）；(4) 非参数规划可测试期加正则、无需重训；(5) 微调中不确定性下降 → 保守度自适应；(6) 平衡采样加速在线信息传播。

### 4.3 什么时候会失效
- 任务远超离线数据 + 在线 ≤20 trials 覆盖（如物体颜色迁移失败）。
- Q-ensemble 只度量值不确定性，dynamics/reward 的 OOD 未直接覆盖。
- λ 过大过度保守、过小回到 extrapolation。
- 高速接触/灵巧：xArm 准静态不能外推。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
FOWM 是 offline-to-online MBRL：性能受离线覆盖 + 在线少样本 + 不确定性代理质量限。LCB 用 Q-ensemble std 近似 epistemic uncertainty（轻量但不完整）；无形式化保证。规划非参数性是加测试期正则的理论基础。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 FOWM 关系 |
|---|---|---|---|
| CQL/IQL（offline，训练时保守） | 稳 | 过度保守、难适应 | FOWM 借 IQL backup，但保守放规划期 |
| online TD-MPC | 数据高效 | 从零真机学不动 | FOWM 的对照（0%） |
| [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]（ensemble mean） | 灵巧、无梯度 | mean 抗乐观弱 | FOWM 用显式 LCB |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]（AC-ensemble LCB） | 真机灵巧、保守探索 | online-from-scratch | **姊妹**：FOWM 是 offline→online 版 |

### 5.3 工程/实验维度
离线覆盖、Q-ensemble 规模、λ 调参、TD-MPC latent 表达、xArm 准静态是主要边界；灵巧高速接触、触觉、dynamics-ensemble 未覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / 灵巧手的迁移

| WMTS 模块 | FOWM 对应 | 迁移设计 |
|---|---|---|
| **WM 模块完整配方** | offline 预训 + ≤20 trials 微调 + LCB 规划 | **WMTS WM 模块的镜像**：离线训 WM + ≤1h 真机微调 + WM-ranking 时 LCB |
| **Reliability head** | Eq 4 LCB（$Q-\lambda\,\mathrm{std}$） | **直接实现**：对 task/chunk 的预测回报减 ensemble std 惩罚 |
| 不确定性来源 | 轻量 Q-ensemble | WMTS 可选 Q-ensemble（轻、实时）或 dynamics-ensemble（更全，含接触不确定性） |
| 真机适配 | 微调中不确定性自适应下降 | WMTS LAAA：早保守、随真机数据增多放开 |
| 避训练时硬保守 | 规划非参数、测试期加正则 | WMTS 在 WM-planning/ranking 时加 LCB，不必把保守烤进策略 |

**核心论证（critical thinking）**：FOWM 是 **WMTS world-model 模块最完整的现成配方**——"离线预训 WM → 少量真机微调 → 规划时 LCB 抑制 extrapolation"几乎逐字对应 WMTS。其 Eq 4 的 $\hat R=\sum\gamma^t(R-\lambda u_t)$ 就是 WMTS reliability head 的实现，且揭示一个 WMTS 该吸收的关键洞见：**保守度该放在非参数规划的测试期、用 ensemble 不确定性自适应调节，而非训练时硬塞**——这样微调中随真机数据增多、不确定性下降，WMTS 能从"早期保守"平滑过渡到"后期放开探索"，正是 LAAA 想要的真机适配曲线。需补强两处：(1) FOWM 用 **Q-ensemble（仅值不确定性）**，灵巧手接触密集时 **dynamics/reward 的 OOD 更危险**，WMTS 宜上 **dynamics-ensemble**（PDDM 路线）或两者兼用；(2) FOWM 是 **xArm 准静态像素**，转笔高速接触的 extrapolation 更剧烈，λ 与 ensemble 设计要更强。它与姊妹作 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 正好覆盖 WMTS 两种真机模式：FOWM = offline→online 微调，MoDem-V2 = online-from-scratch 保守探索。

### 6.2 可验证实验建议
- 复刻 FOWM 配方到转笔：离线训 WM + ≤1h 真机微调 + Eq 4 LCB，对照无正则，测 extrapolation 与少样本适应。
- Q-ensemble vs dynamics-ensemble：在接触密集任务测两种不确定性代理对 model-exploitation 的抑制差异。
- λ 自适应曲线：测微调中不确定性下降是否带来"保守→探索"的平滑过渡（LAAA）。

### 6.3 不应过度外推的点
- xArm 准静态像素成功**不能**外推到高速转笔接触。
- Q-ensemble 仅值不确定性，灵巧手需 dynamics/reward 不确定性。
- ≤20 trials 适应有上限（颜色迁移失败），WMTS 需评估转笔的样本预算。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
offline RL（extrapolation/overestimation）+ offline-to-online 微调；借 IQL in-sample backup（Eq 3 expectile）+ AWR 避 OOD；TD-MPC MBRL 骨架。

### 与 [[ControlTheory]] 的联系
TD-MPC 的 MPPI 规划（receding-horizon）；在规划目标上加测试期不确定性正则（Eq 4）。

### 与 [[Optimization]] 的联系
expectile 回归（asymmetric ℓ2）、AWR、MPPI 采样优化；LCB 风险正则（$Q-\lambda\,\mathrm{std}$）。

### 与 [[EmbodiedAI]] 的联系
真机 xArm 像素输入、≤20 trials 少样本微调到 seen/unseen 任务；offline 真机数据预训 + 在线自校准。

### 与 [[WorldModels]] 的联系
FOWM 把 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] 的思想做进**规划测试期**：Eq 4 的 $\hat R=\sum\gamma^t(R-\lambda u_t)$（$u_t=\mathrm{std}\{Q^{(i)}\}$）就是 LCB，惩罚 OOD 高不确定动作——**认知不确定性三用** 暗线（护栏）的 offline→online 版。它揭示 [[WorldModels#6.4 真机在线适配]] 的关键机理：把保守放在非参数规划的测试期、随微调中不确定性下降而自适应放开（早保守、后探索），正是 WMTS LAAA 想要的适配曲线。与姊妹作 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 覆盖 offline→online 与 online-from-scratch 两种真机模式。

### 与 [[Final_WMTS]] 的联系
WMTS WM 模块最完整的现成配方（离线预训 + ≤1h 微调 + 规划 LCB）；Eq 4 = reliability head；"保守放测试期 + 不确定性自适应下降"= LAAA；与 MoDem-V2 覆盖 offline→online 与 online-from-scratch 两模式。

## References
- 原始 PDF：[[Finetuning Offline World Models in the Real World.pdf]]（UCSD/Tsinghua，CoRL 2023）
- 骨架：TD-MPC；借 IQL（in-sample backup）、AWR
- 姊妹/同系：[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]（online-from-scratch LCB）、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]（ensemble 源头）
- 项目入口：[[Final_WMTS]]、WMTS_Reliability_Extensions
