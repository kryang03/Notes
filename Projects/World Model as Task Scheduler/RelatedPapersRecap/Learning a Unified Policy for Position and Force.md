---
tags:
  - paper
  - force-control
  - loco-manipulation
  - force-estimation
  - WMTS
aliases:
  - Unified Position-Force Policy
paper-year: 2025
read-date: 2026-06-15
venue: CoRL 2025 (BIGAI / BUPT; Siyuan Huang)
paper-pdf: "[[Learning a Unified Policy for Position and Force.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# Learning a Unified Policy for Position and Force Control in Legged Loco-Manipulation

> [!abstract] 核心贡献
> 首个为腿式机器人**联合建模力 + 位置控制、且无需力传感器**的统一策略。在 Isaac Gym 里 RL 训练：模拟多样的位置+力命令 + 外部扰动力，学一个策略**从历史机器人状态估计力**、并通过位置/速度调整补偿之 → 支持位置跟踪、施力、力跟踪、柔顺交互。更关键：学到的**力估计模块给 IL 提供"力感知示范"**，在 4 个接触密集任务上**比纯位置控制 +39.5% 成功率（无外部力传感器）**。**对 WMTS：印证两件 WMTS 核心事项——(1) 接触力可从本体历史估计（无需力传感器，呼应 SSRL 外力残差）；(2) 力感知数据对接触密集 IL 至关重要（+39.5%，呼应 DexWM HC-loss、Beyond Human Demonstrations 数据质量）。WMTS 有真触觉，可比"估计"更进一步。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 统一力/位置控制；柔顺交互（compliance）；力补偿。
> - [[ReinforcementLearning]] — RL 训统一策略；多样力+位置命令 + 扰动力 DR。
> - [[EmbodiedAI]] — 腿式 loco-manipulation；力感知 IL 数据。
> - [[Final_WMTS]] — **接触力可从本体历史估计 + 力感知数据对 IL 关键**；WMTS 用真触觉更强。
> - [[Dynamic Non-Prehensile Manipulation]] — 转笔需力/柔顺控制 + 力感知数据。
>
> **核心技术**: 统一力-位置策略, 力估计器 (本体历史→力, 无力传感器), 位置/速度补偿, 力+位置命令 + 扰动力 DR, 力感知 IL 数据 (+39.5%)

## 0. 阅读定位与范本价值

这篇对 WMTS 的价值聚焦在**接触力主题**，与 [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]（外力残差估计）、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]（接触监督）、[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]]（增益自适应）共同构成"**接触力是关键、且可学/可估**"的论证群。它的两条独特贡献：(1) **无力传感器、从本体历史估力**（与 SSRL 互证）；(2) **力感知数据显著提升接触密集 IL**（+39.5%，量化了"接触信息对 IL 的价值"）。出自 **BIGAI（Siyuan Huang）**，与 [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]] 同生态。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
腿式 loco-manipulation 接触密集，需联合建模接触力 + 位置，但缺力传感硬件；现有 visuomotor 策略多只学位置或力、不共学，且 IL 数据多是纯轨迹（无接触信息）→ 连擦黑板这种基本接触任务都学不好。本文学一个**无力传感器的统一力-位置策略**，并用其力估计给 IL 补接触信息。

### 1.2 直观隐喻
纯位置控制像"只按计划走位、不管推没推到墙"——擦黑板会要么没碰到、要么压太狠。统一力-位置策略像"边走位边感知手上的力（从历史动作-状态反推）、并据此调整压多大"——这就是柔顺。力感知示范像"教学员时不仅记手的位置、还记用了多大力"，学员（IL）学得更好。可证伪含义：力建模的收益集中在**接触密集 + 需柔顺/力控**任务；纯自由空间运动收益小。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 纯位置控制 RL | 位置跟踪 + DR | 接触密集/柔顺任务不行 |
| 纯轨迹 IL 数据 | 位置轨迹 | 缺接触信息→接触任务学不好 |
| 独立力/位置控制 | 分开处理 | 不共学、切换不顺 |
| 需力传感器 | 硬件测力 | 多数腿式机器人无力传感 |
| **本文统一策略** | **力+位置共学 + 本体估力 + 力感知数据** | 腿式 loco-manip（非多指 in-hand）；估力非真测 |

### 1.4 Delta 分析
精确增量：(1) **首个统一力-位置策略**（共学，非独立）；(2) **从本体历史估力、无需力传感器**；(3) **力估计模块给 IL 补接触信息** → +39.5%。把"纯位置 + 纯轨迹数据"换成"力-位置共学 + 力感知数据"。

## 2. 核心方法（原理与方法：统一策略 + 力估计）

### 2.1 核心机制（无跳步）
- **训练**：Isaac Gym RL，模拟**多样位置+力命令组合 + 外部扰动力**（DR）。
- **力估计器**：从**历史机器人状态**估计当前所受力（无力传感器）。
- **统一控制**：策略据估计力，通过**位置/速度调整**补偿/施加力 → 位置跟踪 / 施力 / 力跟踪 / 柔顺交互（按命令）。
- **力感知 IL 数据**：用该策略采数据时，其力估计模块给示范**附上接触力信息** → 训接触密集 IL 策略，无需外部力传感器。

### 2.2 概念边界与符号陷阱
- 力是**估计**（从本体历史），非真测——WMTS 有真触觉，可超越。
- 统一策略按命令在位置/力/柔顺间切换。
- 力感知数据 = 轨迹 + 估计接触力。
- 腿式 loco-manip（足/臂接触），非多指 in-hand。

## 3. 实验与验证
- **统一策略**实现位置跟踪/施力/力跟踪/柔顺（quadruped manipulator + humanoid）。
- **力感知 IL +39.5%**（4 接触密集任务，如擦黑板）vs 纯位置控制，**无外部力传感器**。**因果**：接触力信息让 IL 策略知道"用多大力"。
- 边界：腿式（非 in-hand）；力估计非真测。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**接触密集 loco-manipulation 需联合建模力+位置，而接触力可从本体历史估计（无需力传感器）；用这个力估计统一控制并给 IL 数据补接触信息，可在接触任务上大幅提升（+39.5%）。** 一句话：**力可估、力共学、力感知数据关键——接触任务别只用位置。**

### 4.2 为什么有效
(1) 力+位置共学 → 柔顺/力控；(2) 本体历史估力 → 免力传感器；(3) 扰动力 DR → 鲁棒；(4) 力感知数据 → IL 知道接触力。

### 4.3 什么时候会失效
- 力估计在本体历史信息不足时不准。
- 多指高维 in-hand 接触力比足-地复杂。
- 纯自由空间任务力建模收益小。

## 5. 替代方案与局限（未来与结合）
- 与 [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]（外力残差给 WM）互补：本文力估计给**控制 + IL 数据**，SSRL 给 **WM 预测**。
- 与 [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]]（增益自适应）、[[DyWA: Dynamics-adaptive World Action Model|DyWA]]（变阻抗）同属力/接触控制族。
- 局限：估力非真测（WMTS 有触觉）；腿式非 in-hand。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | 本文对应 | 迁移设计 |
|---|---|---|
| **接触力建模** | 本体历史估力 | WMTS 用**触觉 + 本体**估/测接触力（比纯本体估更准） |
| **Oracle 数据** | 力感知示范 (+39.5%) | WMTS Oracle 产**力/触觉感知数据**（非纯轨迹）训 generalist |
| 柔顺控制 | 统一力-位置 | 转笔需力控/柔顺（接触力调节） |
| WM 输入 | 力估计 | 与 SSRL 外力残差互补：WM 用触觉测接触力 |

**核心论证（critical thinking）**：这篇为 WMTS 的**接触力主题**加两条实证。(1) **接触力可从本体历史估计（无需力传感器）**——与 [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]] 的外力残差估计互证，说明即便没有触觉，力也是可学的潜变量；而 **WMTS 有真触觉阵列（5×12×6）**，所以可以做得更准——用触觉直接观测接触力，而非从本体历史反推。(2) **力感知数据对接触密集 IL 价值巨大（+39.5%）**——这量化了"接触信息对 IL 的重要性"，与 [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]] 的 HC-loss（latent 不够、需结构化接触监督）、[[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Beyond Human Demonstrations]]（数据质量）合流，共同指向：**WMTS 的 Oracle 必须产出力/触觉感知的数据（而非纯位置轨迹）来训 DP generalist**，否则转笔这种接触主导任务的 generalist 会像"纯轨迹 IL 擦黑板"一样失败。**边界**：腿式足-地接触相对低维，转笔多指接触高维；本文是**估力**，WMTS 应**用触觉测力**更可靠。出自 BIGAI（Siyuan Huang），与 UniDexGrasp++ 同生态，资产可复用。

### 6.2 可验证实验建议
- 力感知 vs 纯位置数据：转笔上对照"Oracle 产力/触觉感知数据" vs "纯轨迹数据"训 generalist，测成功率（对标 +39.5%）。
- 触觉测力 vs 本体估力：WMTS 用触觉直接测接触力 vs 本体历史估，测精度。
- 柔顺控制：转笔接触力调节用统一力-位置思路。

### 6.3 不应过度外推的点
- 足-地接触（低维）不能直接外推多指 in-hand（高维）。
- 估力非真测；WMTS 用触觉更准。
- 力建模收益在接触密集任务，自由空间小。

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
统一力/位置控制、柔顺交互（compliance）；从历史估力并经位置/速度补偿——学习式力控。

### 与 [[ReinforcementLearning]] 的联系
RL 训统一策略；多样力+位置命令 + 扰动力 DR；力感知数据增强 IL。

### 与 [[EmbodiedAI]] 的联系
腿式 loco-manipulation；无力传感器的力估计；接触密集任务（擦黑板等）。

### 与 [[Final_WMTS]] 的联系
接触力可从本体历史估计（WMTS 用触觉更准）；力感知数据对接触 IL 关键（+39.5%）→ WMTS Oracle 须产力/触觉感知数据；与 SSRL 外力残差互补。

## References
- 原始 PDF：[[Learning a Unified Policy for Position and Force.pdf]]（BIGAI/BUPT，CoRL 2025，arXiv 2505.20829）
- 力/接触主题群：[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]（外力残差）、[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]]（增益）、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]（接触监督）
- 数据质量呼应：[[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Beyond Human Demonstrations]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
