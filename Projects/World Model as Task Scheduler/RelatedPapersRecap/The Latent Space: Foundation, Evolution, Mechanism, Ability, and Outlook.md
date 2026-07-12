---
tags:
  - paper
  - latent-space
  - survey
  - taxonomy
  - WMTS
aliases:
  - Latent Space Survey
paper-year: 2026
read-date: 2026-06-16
venue: arXiv 2604.02029 (survey, NUS/Fudan/Tsinghua 等)
paper-pdf: "[[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook.pdf]]"
related:
  - "[[RepresentationLearning]]"
  - "[[WorldModels]]"
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook

> [!abstract] 核心贡献（综述）
> 一篇**以语言模型为中心**的 latent space 大综述，主张 **latent space 是计算的"原生基底"**：许多内部过程（推理、规划）在**连续 latent 空间**比在人类可读的显式 token 轨迹里更自然——显式空间有语言冗余、离散化瓶颈、序列低效、语义损失。按五视角组织：**Foundation**（什么是 latent space；vs 显式/verbal 空间；vs 生成式视觉模型）、**Evolution**（prototype→formation→expansion→outbreak）、**Mechanism**（Architecture/Representation/Computation/Optimization）、**Ability**（Reasoning/Planning/Modeling/Perception/Memory/Collaboration/**Embodiment**）、**Outlook**。**对 WMTS：它是 latent 计算的坐标系——可定位 WMTS 的 latent WM、latent planning、embodiment；但其"纯 latent 为原生基底"的主张与 WMTS 的结构化物理方向（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]/[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]）形成关键张力：WMTS 走"结构化 + latent 残差"，不全押纯 latent。**

> [!tip] 与理论基础的关联
> - [[RepresentationLearning#3.1 降维思想的统一主线]] — latent space 即"表征"主题本身；综述的 Representation 分类是该主线的展开。
> - [[WorldModels#1. 表征层：把高维观测压成"可预测"的状态]] — 机器人 latent WM 是本综述 Modeling/Embodiment 能力的具身落点。
> - [[EmbodiedAI]] — latent space 的 Embodiment 能力（具身 latent 计算）。
> - [[ReinforcementLearning]] — latent planning/modeling（latent 内规划、世界建模）。
> - [[StochasticProcess]] — latent 表示（VAE/diffusion/transformer）。
> - [[Final_WMTS]] — **latent 计算坐标系**；latent-vs-显式张力（WMTS=结构化+latent 残差）。

## 0. 阅读定位与价值（综述/地图）

> [!note] 综述类 recap 适配
> 无单一方法，故"原理"→分类框架（§2），"实验"→领域概念证据（§3）。这是**语言中心**的 latent 综述，对 WMTS 的相关部分是 **Modeling / Planning / Embodiment** 能力 + latent-vs-显式框架；大宗（LLM latent reasoning）较 tangential。它与库内两篇 WM 综述（[[A Step Toward World Models- A Survey on Robotic Manipulation|操作 WM]]、[[Learning to Model the World: A Survey of World|全 AI WM]]）互补：那两篇分类 WM，本篇分类 latent space 本身。

WMTS 的 WM 在 latent 内 rollout，本综述给"latent 计算"的通用框架。但 WMTS 的核心张力恰是**latent vs 结构化物理**——本综述champions latent，WMTS 选结构化+latent 残差，读它要带着这个批判视角。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
语言模型多用显式 token 轨迹（人类可读）做内部计算，但显式空间有**语言冗余、离散化瓶颈、序列低效、语义损失**。越来越多工作表明推理/规划等过程在**连续 latent 空间**更自然。本综述统一梳理 latent space 的定义、分类与研究。

### 1.2 直观隐喻
显式 token 推理像"凡事都要先翻译成人话再想"——啰嗦、丢精度、串行慢。latent 推理像"直接在脑内连续概念空间里想，不必逐字说出来"——快、信息密、无语义损失。本综述给这片"脑内空间"画地图。可证伪含义：latent 优势在"过程不需人类可读、且连续表示更紧致"时显著；需可解释/可验证处显式仍有价值（WMTS 安全相关处正需可解释）。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 计算空间 | 特点 | 关键局限 |
|---|---|---|
| 显式/verbal（token 轨迹） | 人类可读、可解释 | 语言冗余、离散瓶颈、序列低效、语义损失 |
| 生成式视觉 latent | 像素/视觉 latent | 偏感知重构、非语言推理基底 |
| **本综述聚焦的语言 latent** | 连续、紧致、可推理 | 不可解释（高风险控制需谨慎）；语言中心 |

### 1.4 Delta 分析（综述自身贡献）
首个**统一**梳理语言模型 latent space 的综述：五视角（Foundation/Evolution/Mechanism/Ability/Outlook）+ Mechanism 四线（Architecture/Representation/Computation/Optimization）+ Ability 七维（含 Embodiment）。把碎片化的 latent 研究组织成可导航地图。

## 2. 分类框架（原理 → 综述的 Mechanism/Ability 分类）

### 2.1 五视角结构
- **Foundation**：latent space 概念；vs 显式/verbal 空间（表征属性 + 功能能力）；vs 生成式视觉模型。
- **Evolution**：prototype → formation → expansion → **outbreak**（latent 计算的发展史）。
- **Mechanism**：见 §2.2。
- **Ability**：见 §2.3。
- **Outlook**：perspective / challenge / future。

### 2.2 Mechanism 四线（latent 怎么工作）
| 线 | 子类 | 含义 |
|---|---|---|
| **Architecture** | Backbone / Component / Auxiliary | 承载 latent 的网络结构 |
| **Representation** | Internal / External / Learnable / Hybrid | latent 表示形式（模型内部激活 vs 外部记忆 vs 可学 vs 混合） |
| **Computation** | Compressed / Expanded / Adaptive / Interleaved | latent 计算模式（压缩/扩展/自适应/与显式交错） |
| **Optimization** | Pre-training / Post-training / Inference | 何时塑造 latent |

### 2.3 Ability 七维（latent 使能什么）
Reasoning、Planning、Modeling、Perception、Memory、Collaboration、**Embodiment**——latent 支撑的能力谱。对 WMTS 最相关：**Modeling（世界建模）、Planning（latent 规划）、Embodiment（具身）**。

### 2.4 概念边界与符号陷阱
- 语言中心：多数指 LLM 的 latent reasoning；WMTS 关心的是机器人 latent WM（Modeling/Embodiment 子集）。
- "latent 原生基底"是 thesis，非定论；可解释/安全处显式仍有价值。
- latent（连续、不可解释）vs 显式物理（可解释、可验证）是 WMTS 的核心取舍。
- 下式给一般 latent 计算视角（编码-解码/动力学）：
$$
z = E_\phi(x, c),
\quad \hat y = D_\theta(z, q),
\quad \text{or}\quad z_{t+1}=F_\theta(z_t,a_t)
$$
WMTS 的 WM 即 $z_{t+1}=F_\theta(z_t,a_t)$ 的结构化版（$F$ 含 actuator+rigid 物理 + latent 残差）。

### 2.5 信息流（综述视角）
观测/token → latent 表示（Representation）→ latent 计算（Computation，可与显式 Interleaved）→ 解码/行动；Optimization 在 pre/post-training/inference 各阶段塑造 latent；Ability 是其下游表现。

## 3. 领域证据与挑战（实验 → 概念证据）

### 3.1 证据性质
综述无实验，证据是**概念框架 + 跨领域案例**（latent reasoning/planning/modeling 的代表工作）。统一了此前碎片化的 latent 研究（机制/模态/任务各异，缺统一视角）。

### 3.2 关键论点
- 显式 token 计算的结构性局限（冗余/离散/串行/语义损失）驱动 latent 转向。
- latent 从早期 latent reasoning 扩到 planning/modeling/perception/memory/collaboration/embodiment。
- Mechanism 四线 + Ability 七维给统一坐标。

### 3.3 对照因果链
- `显式 token 推理 → 语言冗余/串行 → 低效 + 语义损失`。
- `latent 推理 → 连续紧致 → 高效但不可解释`。
- `latent 只优化重构 → 丢控制变量；加 dynamics/reward → 偏可行动结构`（与 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] reward-driven latent 一致）。

### 3.4 边界
- 语言中心；机器人 latent 是 Modeling/Embodiment 子集。
- 不可解释 → 高风险控制需谨慎。
- 综述广而不深；具体回单篇。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**latent space 不只是 encoder 输出，而是计算的"原生基底"：许多内部过程（推理/规划/建模/具身）在连续 latent 比在显式 token 轨迹更自然、更高效、无语义损失；可按 Mechanism（架构/表示/计算/优化）× Ability（推理…具身）统一组织。** 一句话：**把 latent 当计算基底而非中间向量，并按机制/能力分类。**

### 4.2 为什么这个框架有用（对 WMTS）
给 WMTS 的 latent WM 一个定位坐标（Representation 形式、Computation 模式、Modeling/Embodiment 能力），并明确 latent-vs-显式的权衡——这正是 WMTS 选"结构化+latent 残差"的决策维度。

### 4.3 综述的局限
- 语言中心，机器人/接触着墨少。
- "纯 latent 原生基底"是 thesis，与 WMTS 结构化方向有张力。
- 广而不深。

## 5. 替代视角与局限（未来与结合）
- 与两篇 WM 综述（[[A Step Toward World Models- A Survey on Robotic Manipulation|操作 WM]]、[[Learning to Model the World: A Survey of World|全 AI WM]]）互补：本篇分类 latent space，那两篇分类 WM。
- latent（本篇）vs 结构化物理（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]）vs semi-structured（[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]）——WMTS 取后两者倾向。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | 本综述对应 | 设计 |
|---|---|---|
| **latent WM 定位** | Representation/Computation 分类 | 给 WMTS WM latent 定位（结构化 hybrid 表示 + adaptive 计算） |
| latent planning | Planning 能力 | WMTS WM 内 latent rollout 规划 |
| Embodiment | Embodiment 能力 | 具身 latent（含触觉/接触） |
| latent vs 显式 | Foundation 对比 | WMTS 决策：安全/可解释处用显式物理，效率处用 latent |

**核心论证（critical thinking）**：本综述给 WMTS 一个**latent 计算的坐标系**，但更重要的是它把 WMTS 的**核心设计张力**摆上台面：**latent vs 显式**。综述champions"latent 是原生基底"（连续、高效、无语义损失），这对 LLM 推理成立；但 **WMTS 的 WM 处理的是物理接触动力学，恰恰需要可解释、可验证、无 model-exploitation 的结构**——所以 WMTS **不全押纯 latent**，而走 **结构化物理（actuator+rigid，[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo]]/[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]）+ latent 残差** 的中间路线（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] 显式极、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] 纯 latent 极，WMTS 居中）。综述的价值是：(1) 用其 Representation（hybrid）/Computation（adaptive）分类**精确描述 WMTS WM 的 latent 部分**；(2) 提醒 WMTS 在**效率敏感处**（高频 rollout）可更 latent、在**安全/可解释处**（接触力安全、Reject 判定）必须显式/结构化。**定位**：语言中心的广survey，对 WMTS 是 latent 计算的概念地图 + latent-vs-结构化决策框架，非技术方法；与两篇 WM 综述构成"WM 分类 + latent 分类"的双坐标。

### 6.2 可行动项
- 用 Representation/Computation 分类标注 WMTS WM 的 latent 设计（hybrid 结构化+残差、adaptive 计算）。
- 明确 latent-vs-显式分工表：效率处 latent、安全/可解释处显式物理。

### 6.3 不应过度依赖的点
- 语言中心；机器人接触动力学需结构化，勿全押纯 latent。
- 广而不深；具体回单篇 + 结构化 WM 论文。

## 7. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
latent space 的 Embodiment 能力；具身 latent 计算（含感知/记忆/协作）。

### 与 [[ReinforcementLearning]] 的联系
latent Planning/Modeling（latent 内规划与世界建模）；与 Dreamer 系 latent imagination 一脉。

### 与 [[StochasticProcess]] 的联系
latent 表示的生成式基础（VAE/diffusion/transformer）；Representation/Computation 分类。

### 与 [[Final_WMTS]] 的联系
latent 计算坐标系定位 WMTS WM latent（hybrid 结构化+残差、adaptive）；latent-vs-显式张力 → WMTS 选结构化+latent 残差；与两篇 WM 综述构成双坐标。

### 与 [[RepresentationLearning]] / [[WorldModels]] 的联系
本综述是"表征作计算基底"这一命题的最广展开：其 Representation 分类（Internal/External/Learnable/Hybrid）对应 [[RepresentationLearning#3.1 降维思想的统一主线]] 的降维/编码主线；其 Modeling/Planning/Embodiment 能力落到机器人身上即 [[WorldModels#1. 表征层：把高维观测压成"可预测"的状态]] 与 [[WorldModels#2. 预测层：在 latent 里推演未来]]——WMTS 的 $z_{t+1}=F_\theta(z_t,a_t)$ 结构化 WM 就是综述 Modeling 能力的"物理知情"实例。

### 暗线：POMDP → belief → latent
本综述其实给这条暗线的"终点"做了地图：**部分可观 → belief（充分统计量）→ latent 计算基底**。综述主张"latent 是原生计算基底"，恰是把 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|POMDP 的 belief]]、[[StochasticProcess#2.3 马尔可夫性：它如何在推冰球里被破坏，又如何被"信念"救回|信念更新]] 抬升为"可在其中直接推理/规划的空间"。但对 WMTS 有关键分歧：belief 在接触物理里需可解释、可验证，故 WMTS 让 latent 只承担残差，主体交给结构化物理（见 §6.1）。

### 与本簇论文的关联（Delta 对比）
- **vs [[Transformers as Meta-Learners for Implicit Neural Representations|Trans-INR]]**：综述是坐标系、Trans-INR 是一个点——后者"amortized 生成一段 latent 表示（INR）"正落在综述 Representation（Learnable）× Computation（Expanded）格子里。
- **vs [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|ICL 架构研究]]**：综述把 in-context 计算归入 Computation（Interleaved/Adaptive）；ICL 论文从下往上证"这种 in-context 适应架构无关"——综述给标签、ICL 给机制证据。
- **vs [[On the Continuity of Rotation Representations in Neural Networks|6D 旋转表示]]**：表征谱的两端——本综述管**内部隐式 latent 作计算基底**，6D 论文管**输出侧显式物理量（SO(3)）的连续编码**；WMTS 两头都要（内部 latent 残差 + 输出旋转用 6D/9D）。

## References
- 原始 PDF：[[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook.pdf]]（多机构，arXiv 2604.02029）
- 互补综述：[[A Step Toward World Models- A Survey on Robotic Manipulation|操作 WM 综述]]、[[Learning to Model the World: A Survey of World|全 AI WM 综述]]
- 本簇（表征/几何/ICL/元学习）关联：[[Transformers as Meta-Learners for Implicit Neural Representations|Trans-INR]]、[[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|ICL 架构研究]]、[[On the Continuity of Rotation Representations in Neural Networks|6D 旋转表示]]
- latent-vs-结构化谱：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer（latent）]]、[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL（semi-structured）]]、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2（显式）]]
- 项目入口：[[Final_WMTS]]
