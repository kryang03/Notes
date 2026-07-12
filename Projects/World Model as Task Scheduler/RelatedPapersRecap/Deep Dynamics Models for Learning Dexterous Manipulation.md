---
tags:
  - paper
  - model-based-rl
  - dexterous-manipulation
  - dynamics-model
  - ensemble
  - mpc
  - WMTS
aliases:
  - PDDM
  - Deep Dynamics Models Dexterous
paper-year: 2019
read-date: 2026-06-15
venue: CoRL 2019 (Google Brain; Levine / Vikash Kumar)
paper-pdf: "[[Deep Dynamics Models for Learning Dexterous Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# PDDM: Deep Dynamics Models for Learning Dexterous Manipulation

> [!abstract] 核心贡献
> 灵巧 model-based RL 的**奠基作**：把 (a) **不确定性感知的 bootstrap ensemble 神经动力学模型** 与 (b) **无梯度轨迹优化（改进版 MPPI）**结合成在线规划（PDDM），在 **24-DoF Shadow Hand 真机上仅用 ~4 小时真实数据**就学会接触密集灵巧技能——转两个自由 **Baoding 球**、**用铅笔写字（handwriting）**、转阀、手内重定向，**无需任何 demo**。关键论点：动力学模型的进步 + 在线 MPC 的进步，足以让 model-based RL 把灵巧任务复杂度推到真机精细接触；**ensemble 是使能因素**——无 ensemble 的高容量模型会过拟合、过度自信、产生有害动作。**它是 WMTS "ensemble 动力学 + 无梯度规划 + 不确定性感知" 的源头，也是 DNPM（转笔）最直接的经典先例（已做铅笔书写与 Baoding 球这类动态手内接触）。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — model-based RL；学 $\hat p_\theta(s'|s,a)$ 用于在线规划（非学策略）。
> - [[ControlTheory]] — 在线 MPC（receding-horizon，每步重规划）闭环控制。
> - [[Optimization]] — 无梯度轨迹优化：random shooting → CEM → **MPPI 式 reward-weighted + 时间相关滤波**（Eq 1-4）。
> - [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] — PDDM 的 bootstrap ensemble 动力学是 PETS 同宗的 epistemic-uncertainty 源头（"无 ensemble 高容量模型过度自信→有害动作"）；用 ensemble 内规划属 [[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]] 的**规划动作（MPC）**一支。挂 **认知不确定性三用** 暗线（ensemble 分歧当护栏）。
> - [[Final_WMTS]] — **WMTS ensemble 动力学 + disagreement + 无梯度规划的源头**；filtering 降维 ≈ eigengrasp；WMTS 升级为结构化+触觉 WM + scheduler 角色。
> - [[Dynamic Non-Prehensile Manipulation]] — **最直接经典先例**：handwriting（铅笔）+ Baoding 球 = 动态手内接触，DNPM/转笔的近亲。
>
> **核心技术**: Bootstrap Ensemble 动力学 (epistemic uncertainty), 无梯度 MPC, MPPI reward-weighted 更新 (Eq 2), 时间相关 filtering (Eq 3-4), ensemble-mean reward (disagreement-aware), 24-DoF Shadow Hand 真机 4h

## 0. 阅读定位与范本价值

PDDM 是知识库里**灵巧 model-based RL 的奠基锚点**，几乎是 WMTS 方法论的直系祖先：它早于 Dreamer 系应用于灵巧，就确立了"**ensemble 动力学 + 无梯度采样 MPC + 真机灵巧 + 4h 数据 + 无 demo**"这套组合。读它要抓三件对 WMTS/DNPM 决定性的事：

1. **ensemble 的源头论证**——"ensemble 是使能因素，无 ensemble 的高容量模型会过拟合并产生过度自信有害动作"。这是 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] ensemble-LCB、[[Robotic World Model: A Neural Network Simulator|RWM]]、整条 WM-core 论证线的**最早实验依据**。
2. **无梯度规划**——接触不可微，PDDM 用 MPPI 式采样优化而非穿动力学反传，正是 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] recap §6 给 WMTS 的结论（用 PPO/采样不用 analytic 梯度）的灵巧先例。
3. **任务直指 DNPM**——铅笔书写、Baoding 球是动态手内接触，是 [[Dynamic Non-Prehensile Manipulation|DNPM]]/转笔的近亲。

它与 [[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]（同 lookahead + 降维）、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（同采样 MPC + 灵巧降维）一脉，但 PDDM 是**最早、最经典、用 ensemble 的**那个。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
灵巧手要协调众多关节、反复建立/断开接触、控制欠驱动物体——解析法需精确物理模型（接触建模算力指数爆炸）、model-free RL 需海量数据且难真机、model-based RL 此前未 scale 到这种复杂度。PDDM 证明：**改进的学习动力学（ensemble）+ 改进的在线 MPC（MPPI 滤波）足以在真机灵巧手上高效学会精细接触技能**。

### 1.2 直观隐喻
PDDM 像"在脑内用一组（ensemble）略有分歧的物理直觉快速推演几条动作序列，挑分高的、但当几个直觉分歧大时就保守"。无梯度采样 = "试很多条、按回报加权平均"，而非"求导找最优"——因为接触处求导不可靠。MPC 每步重规划 = "走一步看一步、随时纠偏"，抵消模型误差累积。可证伪含义：成功应集中在"**模型能从少量真机数据学得够准 + 任务需要灵活重规划**"；动力学太难学或太快时退化。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 解析/接触模型规划 | 精确物理 + 接触模式 | 算力随接触数指数爆炸；难 scale |
| Model-free RL (SAC/NPG) | 从交互学策略 | 数据海量、难真机；高灵活任务（书写）吃力 |
| 单一 NN 动力学 + MPC | 高容量模型 | **过拟合、过度自信、外推有害**（无不确定性） |
| 假设已知动力学的规划 | 完美模型 | 真机不可得 |
| **PDDM** | **ensemble 动力学 + MPPI 滤波 MPC** | 在线 MPC 算力；需状态/物体位姿；replan-every-step |

### 1.4 Delta 分析
精确增量 = **bootstrap ensemble 动力学** ⊕ **MPPI 式 reward-weighted + 时间相关 filtering 优化器**的"特定组合"。单独组件都来自前作，但论文证明**组合是新且关键的**：ensemble 让高容量模型不过拟合（使能因素），filtering 让高维动作可搜且平滑。相对 model-free：样本效率高（每个 transition 都是密集监督、可用 off-policy 数据）；相对 CEM/random shooting：MPPI 滤波在协调 + 精度任务上远胜。

## 2. 核心方法与理论（原理与理论：ensemble 动力学 + 无梯度 MPC）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $s,a$ | 状态（关节+物体位姿）/动作 | 真机/sim | observed/选择 | MDP 状态动作 | 需物体位姿估计 |
| $\hat p_\theta(s'|s,a)=\mathcal N(\hat f_\theta(s,a),\Sigma)$ | 高斯动力学 | 学习 | learned | 预测下一状态 | 预测**状态差** $\hat s_{t+1}=f+\hat s_t$ |
| $\{\theta_i\}_{i=1}^E$ | E 个模型 | bootstrap ensemble | learned | 近似后验 $p(\theta|D)$ | 不同随机初始化 + 不同数据批即可（无需重采样） |
| $A^i=\{a_0^i\dots a_{H-1}^i\}$ | 动作序列 | 采样 | — | 候选轨迹 | H 步 horizon |
| $R_k$ | 标量 | **ensemble 均值回报** | — | 轨迹回报 | **跨 ensemble 取均值 → disagreement 影响选择** |
| $\mu_t$ | 动作分布均值 | MPPI 更新 (Eq 2) | 计算 | reward-weighted | 软更新整合所有样本 |
| $n_t^i$ | 滤波噪声 | Eq 3-4 | 计算 | 时间相关平滑 | $\beta$ 耦合时间步、降有效维 |
| $\gamma,\beta$ | reward 权 / 滤波系数 | 超参 | 固定 | MPPI 温度 / 平滑 | — |

### 2.2 学习动力学：bootstrap ensemble（无跳步）
用 NN 表示 $\hat p_\theta(s'|s,a)=\mathcal N(\hat f_\theta(s,a),\Sigma)$（$\Sigma$ 可学但实测非必需）。**关键：bootstrap ensemble** 近似后验 $p(\theta|D)$ 用 E 个模型，每个**不同随机初始化 + 每步不同数据批**（深度模型无需 bootstrap 重采样）。**为什么必须 ensemble**：高容量模型易在训练集过拟合、在分布外**错误外推**；ensemble 捕捉 epistemic uncertainty，避免过度自信。model-based 比 model-free 更省数据，因每个 transition 都给密集监督、且可用全部（含 off-policy）数据。

### 2.3 在线规划：无梯度优化器三级递进
**① Random Shooting**：采 N 条随机动作序列，选预测回报最高的 $i^*=\arg\max_i\sum_{t'} r(\hat s_{t'},a_{t'}^i)$。缺点：随动作维/horizon 维灾、随机序列难成有意义行为。

**② Iterative Random-Shooting / CEM（Eq 1）**：迭代 M 次，每次取 top-J elites 更新采样分布 $\mu_t^{m+1}=\alpha\,\mathrm{mean}(A_{elites})+(1-\alpha)\mu_t^m$（方差同理）。比 random shooting 强，但仍随维灾、协调+精度任务难。

**③ PDDM：Filtering + Reward-Weighted Refinement（Eq 2-4，核心）**：
- **MPPI 软更新（Eq 2）**：$\mu_t=\dfrac{\sum_{k=0}^N(e^{\gamma R_k})(a_t^{(k)})}{\sum_j e^{\gamma R_j}}$——用 reward 指数加权**整合所有样本**（非只取 elites），并考虑时间步间协方差。
- **时间相关 filtering（Eq 3-4）**：$a_t^i=n_t^i+\mu_t$，$n_t^i=\beta u_t^i+(1-\beta)n_{t-1}^i$（$u_t^i\sim\mathcal N(0,\Sigma)$）——**耦合时间步产生平滑动作序列**，降低搜索空间的有效维度 → 高维灵巧手可搜。

### 2.4 整体与符号陷阱
每条序列的回报 $R_k$ = **跨 ensemble 所有模型的预测回报均值** → **model disagreement 影响所选动作**（这就是 WMTS 的 disagreement/uncertainty 思想雏形）。MPC：只执行第一动作 $a_t^{*}$、收新状态、重规划 → 缓解模型误差累积。可在测试期**随时换 reward/目标**（规划的灵活性优势）。
- 符号陷阱：模型预测**状态差**（$\hat s_{t+1}=f_\theta+\hat s_t$）；无梯度——**不穿动力学反传**；ensemble-mean reward 让分歧大处被自然回避（但 PDDM 用 mean 而非显式 LCB，MoDem-V2 才显式 $-\lambda\,\mathrm{std}$）。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
任务套件：9-DoF 三指手转阀 → 24-DoF 拟人手手内重定向、**铅笔书写**、**Baoding 球**（两自由球）。sim + 真机。真机 Shadow Hand 24-DoF，**~2-4 小时真实数据，无 demo**。对照 model-free（SAC、NPG）与 prior model-based。

### 3.2 关键结果与因果解释
- **真机 4h 学会 Baoding/书写**：24-DoF 手内接触密集任务、无先验动力学知识。**因果**：ensemble 动力学 + MPPI 规划把稀缺真机数据用足。
- **ensemble 是使能因素（核心消融）**：无 ensemble 的模型**早期严重过拟合、过度自信、产生有害行为**；ensemble 让高容量模型可用。**这是 WMTS ensemble 论证的最早实验依据。**
- **PDDM 优化器 >> CEM/random shooting**：action smoothing + soft update 大幅胜出。**因果**：filtering 降有效维 + MPPI 整合更多样本 → 高维协调+精度任务可解。
- **胜 model-free 与 prior model-based**：尤其高灵活任务（书写要跟任意笔画）model-free 吃力。

### 3.3 Ablation / 对照因果链
- `去 ensemble → 高容量模型过拟合、过度自信 → 有害动作`（ensemble 使能）。
- `random shooting / CEM 替 PDDM 优化器 → 高维协调精度任务搜不好`。
- `去 filtering（无时间平滑）→ 有效维高、动作不平滑 → 难执行`。
- `model-free（SAC/NPG）→ 数据海量、高灵活任务（书写）吃力`。

### 3.4 工程约束与实验边界
- 在线 MPC 每步重规划 → 计算成本。
- 需状态（含物体位姿）估计。
- Baoding/书写是动态手内接触，但**未达竞技转笔的高速**。
- ensemble 用 mean reward（隐式抗乐观），非显式 LCB。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**ensemble 不确定性感知动力学 + 无梯度 MPPI 滤波在线 MPC 的特定组合，足以让 model-based RL 在真机 24-DoF 灵巧手上、仅 4h 数据、无 demo 学会接触密集精细技能（书写、Baoding）；ensemble 是让高容量模型不过拟合、不产生过度自信有害动作的使能因素。** 一句话：**灵巧 model-based RL 要 work，动力学必须 ensemble（抗过度自信），规划必须无梯度 + 平滑（抗维灾 + 不可微接触）。**

### 4.2 为什么这个设计有效
(1) ensemble 捕捉 epistemic uncertainty、抗过拟合/过度自信；(2) reward 取 ensemble 均值 → disagreement 自然影响选择；(3) MPPI 软更新整合所有样本；(4) 时间相关 filtering 降有效维 + 平滑可执行；(5) MPC 重规划抗误差累积；(6) model-based 密集监督 + off-policy 数据 → 样本高效。

### 4.3 什么时候会失效
- 动力学太难学准（更高速/更复杂接触）→ ensemble 也救不回。
- 在线 MPC 算力不够高频实时。
- 需精确物体位姿估计，真机感知误差影响。
- mean-reward 抗乐观弱于显式 LCB。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
PDDM 是 ensemble model-based RL + 无梯度 MPC：性能受动力学保真 + 规划质量限。ensemble 给 epistemic uncertainty 的近似（bootstrap），但用 mean reward 而非显式风险度量；无 analytic gradient（接触不可微下是优点）。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 PDDM 关系 |
|---|---|---|---|
| Model-free (SAC/NPG) | 无模型误差 | 数据海量、高灵活任务弱 | PDDM 的对照 |
| 单 NN + MPC | 简单 | 过拟合/过度自信 | PDDM 加 ensemble 修复 |
| CEM/random shooting | 简单 | 维灾、协调精度差 | PDDM 用 MPPI 滤波超越 |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] | 显式 LCB、视觉 | latent | PDDM 的后继，mean→LCB |
| [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] | analytic grad、latent | 接触不可微失真 | PDDM 用无梯度避开 |

### 5.3 工程/实验维度
在线 MPC 算力、物体位姿估计、ensemble 规模、filtering/温度调参是主要边界；超高速接触、触觉、sim-to-real gap 未深入。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM / 灵巧手的迁移

| WMTS/DNPM 模块 | PDDM 对应 | 迁移设计 |
|---|---|---|
| **Ensemble world model** | bootstrap ensemble 动力学 | **直接源头**：WMTS ensemble WM 抗过度自信；升级为结构化+触觉 + 显式 LCB（mean→$\mathrm{mean}-\lambda\,\mathrm{std}$） |
| 规划/Oracle | 无梯度 MPPI MPC | 接触不可微 → 用采样/PPO 而非 analytic 梯度；MPPI 可做 chunk 筛选 |
| 高 DOF 可搜 | 时间相关 filtering | 平滑 + 降有效维；与 eigengrasp 互补用于 21-DoF LinkerHand |
| DNPM 转笔 | handwriting + Baoding | **最近经典先例**：先复刻 PDDM 书写/Baoding，再推到高速转笔 |
| 样本效率 | 4h 真机无 demo | WMTS "≤1h 真机 + WM" 的可行性背书（PDDM 4h 更宽松） |

**核心论证（critical thinking）**：PDDM 是 WMTS 方法论的**直系祖先**——它最早用实验证明"**灵巧 model-based RL 必须 ensemble**（无 ensemble 高容量模型过度自信、产生有害动作）"和"**接触不可微 → 用无梯度采样规划**"，这两条正是 WMTS 的地基。WMTS 在其上做三处明确升级：(1) ensemble reward 从 **mean → 显式 LCB**（$\mathrm{mean}-\lambda\,\mathrm{std}$，[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 的进步）以更强抗乐观；(2) 动力学从纯黑箱 NN → **结构化 actuator+rigid + 触觉**（PDDM 无触觉、需物体位姿）；(3) WM 角色从纯 MPC 仿真器 → **task scheduler + 安全过滤 + 精炼 DP**（更主动）。对 **DNPM**：PDDM 的**铅笔书写 + Baoding 球**是转笔最直接的经典先例，DNPM 应先复刻这两个（验证 ensemble 动力学 + 无梯度规划在笔/球接触上 work），再把动力学体制推到竞技转笔的高速动量主导区——后者 PDDM 未达，是 DNPM 的真正难点。filtering 降维与 [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] 的 eigengrasp 互补，都为高 DOF 规划服务。

### 6.2 可验证实验建议
- 复刻 PDDM 到转笔最小环境：ensemble 动力学 + MPPI 规划，对照 mean-reward vs LCB（$-\lambda\,\mathrm{std}$），测过度自信与掉笔率。
- ensemble 必要性：单 NN vs ensemble 在笔接触动力学上的过拟合/有害动作（直接复刻 PDDM 核心消融）。
- filtering + eigengrasp 联合降维：21-DoF LinkerHand 上测高速转笔规划的可搜性与平滑度。

### 6.3 不应过度外推的点
- 书写/Baoding 的成功**不能**直接外推到竞技高速转笔（动量主导、更快接触）。
- mean-reward 抗乐观弱 → WMTS 用显式 LCB。
- 无触觉、需物体位姿 → WMTS 加触觉一等输入。
- 在线 MPC 算力对高频实时是约束。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
model-based RL：学 $\hat p_\theta(s'|s,a)$（ensemble）用于在线规划而非学策略；密集监督 + off-policy 数据 → 比 model-free 样本高效。

### 与 [[ControlTheory]] 的联系
在线 MPC（receding-horizon，每步重规划执行首动作）闭环控制；可测试期换 reward/目标。

### 与 [[Optimization]] 的联系
无梯度轨迹优化三级：random shooting → CEM（Eq 1）→ MPPI reward-weighted 软更新（Eq 2）+ 时间相关 filtering（Eq 3-4）；后者降有效维、平滑、整合全样本。

### 与 [[Final_WMTS]] 的联系
WMTS ensemble 动力学 + disagreement + 无梯度规划的**源头**；WMTS 升级 mean→LCB、黑箱→结构化+触觉、MPC仿真器→scheduler；filtering 降维服务 21-DoF 规划。

### 与 [[WorldModels]] 的联系
PDDM 是 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] 在**灵巧手真机**上的最早实证——"ensemble 是使能因素，无 ensemble 的高容量模型过拟合、过度自信、产生有害动作"就是本库 **认知不确定性三用** 暗线（ensemble 分歧=epistemic 不确定性=规划护栏）的源头实验。它把 WM 当 [[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]] 里的**规划动作（MPPI-MPC）**而非训练策略，因为接触不可微必须用无梯度采样。WMTS 在其上把 reward 从 ensemble-mean 升级为显式 LCB（见 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]]），并把黑箱 NN 换成 [[WorldModels#5. 结构层：怎么让想象"物理真实"]] 的结构化物理 WM。

### 与 [[Dynamic Non-Prehensile Manipulation]] 的联系
铅笔书写 + Baoding 球 = 动态手内接触，DNPM/转笔最直接的经典先例；DNPM 应先复刻再推向高速。

## References
- 原始 PDF：[[Deep Dynamics Models for Learning Dexterous Manipulation.pdf]]（Google Brain，CoRL 2019）
- 后继（ensemble→LCB、真机灵巧）：[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]
- 同 lookahead/降维：[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（eigengrasp）
- 对照 analytic-grad WM：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
