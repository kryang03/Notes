---
tags:
  - paper
  - world-model
  - curiosity
  - epistemic-uncertainty
  - object-centric
  - WMTS
aliases:
  - Structured WM Curiosity
  - CEE-US
paper-year: 2022
read-date: 2026-06-15
venue: NeurIPS 2022 (MPI Tübingen; Sancaktar, Martius)
paper-pdf: "[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# CEE-US: Curious Exploration via Structured World Models Yields Zero-Shot Manipulation

> [!abstract] 核心贡献
> 用**结构化 world model（GNN，关系归纳偏置）+ ensemble 估 epistemic uncertainty**，在 WM 内**规划朝向最大新颖性/不确定性（信息增益）**做内在动机的"好奇自由玩耍"——早期就与物体交互、逐渐复杂。自强化循环（好模型↔好探索）。**纯内在、任务无关探索后，用 model-based planning 零样本解 stacking/flipping/pick&place/throwing，并泛化到未见物体数/排列**。**对 WMTS：它给出 ensemble 不确定性的"探索（Probe）一面"——规划朝高 epistemic 不确定（GNN 集成 disagreement）去采信息丰富数据、降不确定、改进 WM；这正是 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]] 的 LCB（避不确定、安全 exploit）的对偶。WMTS scheduler 的 Solve/Probe/Reject 由同一 ensemble 不确定性驱动：Probe 求不确定（CEE-US）、Solve 避不确定（LCB）。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 内在动机 RL；model-based planning；探索-利用。
> - [[StochasticProcess]] — ensemble GNN 的 epistemic uncertainty；信息增益。
> - [[EmbodiedAI]] — 多物体操作；自由玩耍 → 零样本下游任务。
> - [[Final_WMTS]] — **ensemble 不确定性的探索面（Probe）**，LCB（Solve）的对偶；结构化（关系）WM。
>
> **核心技术**: 结构化 WM (GNN 关系归纳偏置), ensemble GNN epistemic uncertainty, 规划朝最大新颖性/信息增益, 内在动机自由玩耍, 零样本 model-based planning

## 0. 阅读定位与范本价值

CEE-US 给 WMTS 的 ensemble 不确定性补上**"探索（Probe）一面"**。库内 ensemble 论文（[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]/[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]]）多用 ensemble disagreement 做 **LCB——避开不确定（安全 exploit）**；CEE-US 反过来——**规划朝向高不确定（好奇 explore）去主动采集信息、降不确定、改进 WM**。这是同一 ensemble 信号的两面，正对应 WMTS scheduler 的 **Probe（求不确定以学习）vs Solve（避不确定以稳）**。它还是**结构化（关系 GNN）WM**的代表，与 SSRL/DexSim2Real2 的结构化主题呼应。MPI Martius 组。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
内在动机探索（好奇）在多物体操作上难样本高效——关键信息在稀疏的 agent-物体/物体-物体交互里，而"新颖刺激 ≠ 有用信息"。CEE-US 用结构化 WM（GNN）+ ensemble 不确定性，在 WM 内规划朝信息增益，做交互丰富的自由玩耍，并零样本解下游任务。

### 1.2 直观隐喻
像好奇的孩子自由玩：不是随机乱动（新颖≠有用），而是**朝"我还不懂的地方"去玩**（最大 epistemic 不确定 = 最大信息增益），玩过就懂了（降不确定），越玩越会。结构化 WM（关系 GNN）让它懂"物体间关系"，所以早早去摆弄物体。可证伪含义：好奇探索的样本效率依赖"**不确定性度量准（ensemble）+ 结构化偏置抓住交互**"；无结构或不确定性差则退化为无用新颖。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 新颖性内在奖励（无结构） | 新颖=奖励 | 新颖≠有用；多物体交互稀疏难探 |
| 用 model 只算内在奖励 | model→reward | 没用 model 做规划/零样本 |
| 非结构化 WM | 黑箱 | 缺关系偏置、样本低效 |
| **CEE-US** | **结构化 GNN WM + ensemble + 规划信息增益** | 仿真多物体；GNN 关系假设 |

### 1.4 Delta 分析
精确增量：(1) **结构化 WM（GNN 关系偏置）**抓多物体交互；(2) **规划朝最大 epistemic 不确定（ensemble GNN disagreement）= 信息增益**（不只算内在奖励，还规划）；(3) **自强化循环 + 零样本下游 planning**（探索副产物是可用 WM）。把"非结构新颖奖励"换成"结构化 WM + 信息增益规划 + 零样本复用"。

## 2. 核心方法（原理与方法：结构化 WM + 信息增益规划）

### 2.1 核心机制（无跳步）
- **结构化 WM**：GNN（关系归纳偏置）建多物体动力学；**ensemble of GNNs** 估 epistemic uncertainty。
- **信息增益规划**：在 WM 内**规划动作朝最大 epistemic 不确定（ensemble 预测 disagreement）**——即去最不懂的地方。
- **主动数据 + 更新**：执行该计划采数据 → 更新 WM → 不确定性下降（信息增益）。
- **自强化循环**：好模型 → 好探索 → 更好模型。
- **零样本下游**：探索后的 WM 直接 model-based planning 解 stacking/flipping/pick&place/throwing，泛化未见物体数/排列。

### 2.2 概念边界与符号陷阱
- 规划朝**高**不确定（explore），与 LCB 朝**低**不确定（exploit）相反——同信号两用。
- 结构化 = 关系 GNN（多物体），非 latent 黑箱。
- 内在阶段**任务无关**；下游零样本（无额外训练）。
- 仿真多物体（非真机灵巧）。

## 3. 实验与验证
- 内在自由玩耍：早交互物体、渐复杂。**因果**：结构化 WM + 信息增益规划聚焦有用交互。
- **零样本下游**：stacking/flipping/pick&place/throwing，泛化未见物体数/排列。**因果**：好奇探索副产一个能 planning 的好 WM。
- 边界：仿真多物体；GNN 关系假设。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**用结构化 WM（关系 GNN）+ ensemble epistemic uncertainty，在 WM 内规划朝最大信息增益（不确定性）做好奇探索，不仅样本高效地交互多物体，其副产的 WM 还能零样本 planning 解下游任务——好模型与好探索自强化。** 一句话：**朝"最不懂处"规划探索，副产一个能零样本解任务的 WM。**

### 4.2 为什么有效
(1) 结构化 GNN 抓多物体交互；(2) ensemble 估 epistemic 不确定准；(3) 规划朝信息增益（非随机新颖）；(4) 自强化循环；(5) WM 可零样本复用。

### 4.3 什么时候会失效
- 不确定性度量差 → 探无用新颖。
- 无关系结构 → GNN 偏置不适用。
- 真机/接触密集高维（仿真多物体相对简单）。

## 5. 替代方案与局限（未来与结合）
- ensemble 不确定性两面：**explore（本文，求不确定）vs exploit-LCB（[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]]，避不确定）**。
- 好奇/学习潜力：[[Prioritized Level Replay|PLR]]（TD-error 学习潜力）、[[Curiosity-Driven Exploration via Latent Bayesian Surprise|Latent Bayesian Surprise]]（surprise）。
- 局限：仿真、GNN 关系假设。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | CEE-US 对应 | 迁移设计 |
|---|---|---|
| **Scheduler Probe 队列** | 规划朝 epistemic 不确定 | WMTS Probe = 朝高 ensemble disagreement 的转笔配置探索、采信息 |
| ensemble 双用 | explore（求不确定） | 与 LCB（避不确定，Solve）对偶；同 ensemble 驱动 Solve/Probe/Reject |
| 结构化 WM | GNN 关系 | WMTS 接触关系可用 GNN（手指-笔接触图）或 actuator+rigid |
| WM 自改进 | 好奇采数据降不确定 | WMTS 真机微调阶段主动 Probe 降 WM 不确定 |

**核心论证（critical thinking）**：CEE-US 给 WMTS 的 ensemble 不确定性补上**关键的"探索面"**，与之前的"利用面"合成完整图景。库内 [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]/[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]] 用 ensemble disagreement 做 **LCB——避开不确定区以安全利用**；CEE-US 用同一信号**反向——朝不确定区规划以好奇探索、采集信息、改进 WM**。这两面正是 WMTS scheduler 的 **Solve/Probe/Reject** 的核心机制：**同一个 ensemble 不确定性，Solve 时避（LCB 安全 exploit）、Probe 时求（信息增益 explore）、Reject 时判（不可学/不安全则弃）**。结合 [[Prioritized Level Replay|PLR]] 的学习潜力（高不确定=高学习潜力，与 CEE-US 一致），WMTS scheduler 的 Probe 队列就是"朝 WM 最不确定的转笔配置去探索以最快改进 WM"。CEE-US 还示范**结构化 WM（关系 GNN）**——WMTS 的接触可建成手指-笔接触关系图（GNN），或用 SSRL 的 actuator+rigid——两种结构化路线。**边界**：CEE-US 仿真多物体（关系相对清晰），转笔是高速接触（关系图变化快），GNN 能否实时捕捉需验证；且其零样本是 planning（WMTS 接触不可微宜配 PPO）。

### 6.2 可验证实验建议
- WMTS Probe：scheduler 朝 ensemble disagreement 高的转笔配置探索，对照随机/均匀，测 WM 改进速度。
- ensemble 双用：同 ensemble 做 Solve(LCB) + Probe(信息增益)，测 Solve/Probe/Reject 划分。
- 结构化 WM：GNN 接触图 vs actuator+rigid，测转笔预测。

### 6.3 不应过度外推的点
- 仿真多物体（关系清晰）≠ 高速转笔接触。
- 零样本 planning，转笔不可微宜配 PPO。
- GNN 关系假设需适配手-笔接触。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
内在动机 RL（信息增益）；model-based planning；探索-利用以 ensemble 不确定性统一。

### 与 [[StochasticProcess]] 的联系
ensemble GNN 的 epistemic uncertainty；规划朝信息增益（不确定性最大化）。

### 与 [[EmbodiedAI]] 的联系
多物体操作的好奇自由玩耍 → 零样本下游任务（stacking 等），泛化未见排列。

### 与 [[Final_WMTS]] 的联系
ensemble 不确定性的探索面（Probe，求不确定）= LCB（Solve，避不确定）的对偶；同 ensemble 驱动 Solve/Probe/Reject；结构化（关系 GNN）WM 路线。

## References
- 原始 PDF：[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation.pdf]]（MPI Tübingen，NeurIPS 2022）
- ensemble 利用面（对偶）：[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]、[[Finetuning Offline World Models in the Real World|FOWM]]（LCB）
- 学习潜力/好奇：[[Prioritized Level Replay|PLR]]、[[Curiosity-Driven Exploration via Latent Bayesian Surprise|Latent Bayesian Surprise]]
- 结构化 WM：[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]
- 项目入口：[[Final_WMTS]]
