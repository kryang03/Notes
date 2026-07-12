---
tags:
  - paper
  - world-model
  - robotic-manipulation
  - survey
  - taxonomy
  - WMTS
aliases:
  - WM Survey Manipulation
  - A Step Toward World Models
paper-year: 2025
read-date: 2026-06-15
venue: arXiv 2511.02097 (survey, Tongji)
paper-pdf: "[[A Step Toward World Models- A Survey on Robotic Manipulation.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# A Step Toward World Models: A Survey on Robotic Manipulation

> [!abstract] 核心贡献
> 一篇 2025 的**操作领域 world model 综述**，不强行定义 WM，而是**按"是否具备 world model 的核心能力"**来梳理操作方法。它给出一张可用的地图：**三问**（世界是什么 / 为什么建模 / 怎么建模 / 离"完全体"多远）+ **三范式**（Implicit World Modeling、Latent Dynamics Modeling、Video Generation）+ **两功能**（Decision Support 决策支持 / Training Facilitation 训练促进）+ **架构**（Flat / Hierarchical）+ **七挑战**（数据、感知表征、长程推理、时空一致性、泛化、**物理感知**、记忆）。理论锚点引 Richens et al.：**任何能泛化解多步任务的 agent 必隐式学到一个预测性世界模型**。**对 WMTS 它不是方法而是坐标系——能把我已 recap 的所有 WM 论文归位、并精确定位 WMTS 在 "Latent Dynamics + Training Facilitation + 物理感知 + 灵巧" 的位置与它要填的空白。**

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — 具身智能：WM 让 agent 理解上下文、想象后果、规划行动。
> - [[ReinforcementLearning]] — WM 的两功能之一 Decision Support（规划/价值）；Richens"泛化⟹隐式 WM"。
> - [[StochasticProcess]] — Latent Dynamics Modeling 范式（RSSM/JEPA/扩散）。
> - [[WorldModels]] — 本综述的三范式/两功能/七挑战正是本库 [[WorldModels]] 大厦六层的外部坐标系：Training Facilitation↔[[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]]、物理感知挑战↔[[WorldModels#5. 结构层：怎么让想象"物理真实"]]、长程/一致性↔[[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]]。
> - [[Final_WMTS]] — **WMTS 的领域坐标系**：定位 WMTS = Latent Dynamics + Decision Support&Training Facilitation + Physics-informed + 灵巧；其"物理感知 / 长程 / 记忆"挑战正是 WMTS 卖点。
>
> **核心框架**: 三范式 (Implicit / Latent Dynamics / Video Generation), 两功能 (Decision Support / Training Facilitation), 架构 (Flat/Hierarchical), 七挑战, Richens 定理

## 0. 阅读定位与范本价值

这是 RelatedPapers 里**唯一的"地图"类论文**——不提供方法，而提供**坐标系**。它的范本价值不在某个公式，而在：把我已逐篇 recap 的 WM 论文（Dreamer/STORM/RWM/DiWA/World4RL/DexWM/DexSim2Real2/PDDM/MoDem-V2/FOWM…）**归到统一分类**，并据此**定位 WMTS 与识别空白**。因此本 recap 刻意做成**导航图**：用综述的轴把库内论文排好，再标出 WMTS 的位置与它要填的洞。

> [!note] 综述类 recap 的结构适配
> 综述无单一方法/公式，故本文不套"变量来源表 + 无跳步推导"，而把"原理与理论"替换为**分类框架 + 库内论文归位**（§2），把"实验与验证"替换为**领域经验状态/挑战证据**（§3）。这是对 recap 方法的合理适配，非偷懒。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
WM 的定义/范围/架构/能力至今含混；综述不锁死定义，而是**审视"展现 WM 核心能力"的操作方法**（感知-预测-控制），提炼一个完全体 WM 应有的组件/能力/功能，给出领域地图与未来方向。

### 1.2 关键框架（地图四问）
1. **世界是什么**：对象（物理/agent/环境/虚拟）× 属性（形状/尺寸/重量/材料）× 空间关系（拓扑/方向/距离）× 时间关系（顺序/同时/**因果**）。
2. **为什么建模**：Richens et al.——**任何能泛化解多步任务的 agent 必隐式学一个预测性 WM**（WM 不是可选，是泛化的必要条件）。
3. **怎么建模**：三范式（见 §2.1）。
4. **离完全体多远**：七挑战 + 未来方向（§3）。

### 1.3 竞争视角（领域分歧）
- **Video generation 派**（Wang 等）：用视频生成模型当 WM，编码海量世界知识、按观测/动作预测未来帧。
- **Latent/abstract state 派**（LeCun/JEPA）：建抽象 latent 世界状态，不重构像素。
- **VLA 派**（Zitkovich/RT）：不显式生成未来状态，靠 vision-language-action 隐式建模。

### 1.4 Delta（综述自身的增量）
不限于"自称 WM"的方法，而按**核心能力**纳入更广方法；给出操作领域**comprehensive taxonomy + 核心组件/能力定义 + 未来方向**。这把零散工作组织成可导航的地图。

## 2. 分类框架与库内论文归位（原理与理论 → 分类框架）

### 2.1 三范式（Paradigms）
| 范式 | 含义 | 库内归位 |
|---|---|---|
| **Implicit World Modeling** | 不显式生成未来状态，靠动作预测隐式建模（VLA 类） | （库内偏少；VLA 相关在 Diffusion/IL 簇） |
| **Latent Dynamics Modeling** | 高维→紧凑 latent，预测 latent 动力学 | [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]、[[Robotic World Model: A Neural Network Simulator|RWM]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]](TD-MPC)、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] |
| **Video Generation** | 生成未来帧作为 WM | [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]（像素扩散）；DexWM 的 NWM/PEVA 对照 |
| （超出三范式）**显式物理** | 物理仿真器/数字孪生 | [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] |

### 2.2 两功能（Functions）
- **Decision Support**（决策支持）：WM 配 value/planner 做规划——[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]、[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]、[[Finetuning Offline World Models in the Real World|FOWM]]。
- **Training Facilitation**（训练促进）：WM 当仿真器/想象训策略——[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[DayDreamer- World Models for Physical Robot Learning|DayDreamer]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]。
- **WMTS 同时用两者**：WM 做 task scheduling/ranking/safety（Decision Support）+ 精炼 DP generalist（Training Facilitation）。

### 2.3 架构与世界表示
- **Flat vs Hierarchical**（System 2 解释环境 + System 1 执行）：WMTS 的"scheduler（高层选任务）+ PPO/DP（低层执行）"是**层级架构**。
- **世界表示维度/视角**：2D/3D、ego/外视、latent/显式——WMTS 取 actuator+rigid 结构化 + 触觉（偏显式物理 + latent 残差）。

### 2.4 概念边界与符号陷阱
- "world model" 在综述里是**能力束**（编码状态 + 捕捉动力学 + 预测/规划/推理），不是单一架构——呼应我在各 recap 反复区分的"WM 多义项"。
- Richens 定理是**存在性**论证（泛化⟹隐式 WM），不保证学到的 WM 准确或可规划。
- 三范式有重叠（World4RL 像素扩散兼具 Latent/Video-gen 特征）。

## 3. 领域经验状态与挑战（实验与验证 → 挑战证据）

综述无实验，但**七挑战**刻画了领域的经验天花板，且每条都直接对应 WMTS 的设计应力点：

| 挑战 | 领域现状 | 对 WMTS 的意义 |
|---|---|---|
| 数据限制 | 灵巧数据稀缺 | WMTS 用 sim Oracle + ≤1h 真机 + 人类视频先验（[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]） |
| 感知与表征 | latent 不一定含任务关键信息 | [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]] HC-loss 证 latent 不足→WMTS 加触觉/接触 |
| 长程推理 | autoregressive 误差累积 | [[Robotic World Model: A Neural Network Simulator|RWM]] autoregressive 训练 / [[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]] 随机性 抗累积 |
| 时空一致性 | 生成漂移 | WMTS rollout horizon 受限 + ensemble |
| 泛化 | 跨物体/物理差 | [[DyWA: Dynamics-adaptive World Action Model|DyWA]] 动力学自适应 |
| **物理感知** | 多数 WM 不显式建物理 | **WMTS 卖点**：actuator+rigid 结构化 + 触觉（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] 显式物理一极） |
| 记忆 | 长时依赖 | Transformer WM（[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]）/历史编码（[[Robotic World Model: A Neural Network Simulator|RWM]]/[[DyWA: Dynamics-adaptive World Action Model|DyWA]]） |

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 综述真正的 insight
**WM 不该由"是否自称 WM"或单一架构定义，而该由核心能力（编码状态、捕捉动力学、支持预测/规划/推理）定义；操作领域的 WM 可沿三范式 × 两功能 × 架构 × 七挑战组织；且 Richens 定理给出强理论动机——泛化解多步任务必隐式需要 WM。** 这把零散工作收进一张可导航的地图。

### 4.2 为什么这张地图有用（对 WMTS）
它让我能：(1) 把库内每篇 WM 论文**归位**（§2）；(2) **定位 WMTS** = Latent Dynamics（+显式物理残差）× Decision Support&Training Facilitation × Hierarchical × 主打物理感知/长程/记忆；(3) 据七挑战**核对 WMTS 是否每条都有对策**（数据/感知/长程/一致性/泛化/物理/记忆——逐条对得上）。

### 4.3 综述的局限（什么时候这张地图不够）
- 初版、偏分类不偏深度评测；无统一 benchmark 横评。
- 三范式有重叠、边界模糊。
- 对**灵巧高速接触**这一具体硬场景着墨有限（survey 覆盖广但不深）。
- Richens 定理是存在性，不给可学性/可规划性保证。

## 5. 综述自身的局限与替代（未来与结合）
- **替代视角**：另一篇 [[Learning to Model the World: A Survey of World|Learning to Model the World 综述]]（更偏通用 WM 方法论）与本篇（偏操作领域）互补。
- **深度 vs 广度**：survey 给广度，具体设计仍需回到单篇（PDDM/MoDem-V2/FOWM 给 ensemble-LCB 细节；DexWM 给 HC-loss；DexSim2Real2 给显式物理）。
- **物理感知**被列为关键未来方向但综述未给成熟方案——正是 WMTS 要原创贡献处。

## 6. 对用户研究的启发（未来与结合：定位 WMTS）

### 6.1 WMTS 在地图上的坐标
| 维度 | WMTS 的选择 | 综述依据 |
|---|---|---|
| 范式 | Latent Dynamics + 显式物理残差 | 介于 Latent（[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]）与显式（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]）之间 |
| 功能 | Decision Support（调度/ranking/安全）+ Training Facilitation（精炼 DP） | 综述两功能 WMTS 全占 |
| 架构 | Hierarchical（scheduler + PPO/DP） | System2/System1 |
| 主攻挑战 | **物理感知 + 长程 + 记忆 + 数据** | 七挑战里 WMTS 的差异化集中在物理感知（触觉/接触/actuator） |

**核心论证（critical thinking）**：这篇综述给 WMTS 最大的价值是**确认 WMTS 不是在重复某一范式，而是在三范式交叉处填一个具体空白**——用**结构化物理 + latent 残差**的 WM，**同时做决策支持（task scheduler）与训练促进（精炼 generalist）**，主攻综述列为关键未来方向却无成熟方案的**物理感知**（灵巧接触/触觉）。综述的七挑战恰好是一张 WMTS 设计自检表：数据（sim Oracle+人类视频+≤1h 真机）、感知表征（触觉补 latent，呼应 DexWM HC-loss）、长程（autoregressive 训练 + ensemble，呼应 RWM）、一致性（ensemble）、泛化（动力学自适应，呼应 DyWA）、物理感知（结构化+触觉，WMTS 原创）、记忆（Transformer/历史编码）——**逐条都有对策即说明 WMTS 设计完备；缺哪条即暴露风险**。同时 Richens 定理给 WMTS 一个理论靠山：要让 generalist 泛化到多步转笔，隐式 WM 是必要的，WMTS 把它显式化、结构化、可调度。

### 6.2 可行动项
- 用本综述的分类表做 WMTS 文献定位图（把库内论文按范式/功能/挑战排成矩阵，标 WMTS 坐标与空白）。
- 按七挑战做 WMTS 设计自检 checklist（每条列 WMTS 对策 + 风险）。
- 引 Richens 定理作 WMTS 动机段的理论支撑。

### 6.3 不应过度依赖的点
- survey 是地图非深度评测；具体机制回单篇。
- 物理感知方向综述未给方案，WMTS 不能指望照搬，需原创。

## 7. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
WM 作为具身智能的内部表示，支撑理解上下文、想象后果、规划行动；操作领域 WM 的能力地图。

### 与 [[ReinforcementLearning]] 的联系
两功能之一 Decision Support = 规划/价值；Richens"泛化解多步任务⟹隐式 WM"为 model-based RL 提供理论动机。

### 与 [[StochasticProcess]] 的联系
Latent Dynamics Modeling 范式（RSSM/JEPA/扩散）是随机隐变量序列模型在操作上的实例。

### 与 [[WorldModels]] 的联系
本综述给出的**三范式 × 两功能 × 架构 × 七挑战**是本库 [[WorldModels]] 六层大厦的外部对照地图：Latent Dynamics↔[[WorldModels#2. 预测层：在 latent 里推演未来]]、两功能之 Training Facilitation↔[[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]]、**物理感知**挑战↔[[WorldModels#5. 结构层：怎么让想象"物理真实"]]（WMTS 的 actuator+rigid 解耦所在）、长程/时空一致性↔[[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]]。Richens 定理（泛化⟹隐式 WM）为整座大厦提供理论动机。

### 与 [[Final_WMTS]] 的联系
WMTS 的领域坐标系：定位 WMTS 在 Latent+显式物理残差 × 双功能 × 层级 × 物理感知；七挑战 = WMTS 设计自检表；Richens 定理 = WMTS 理论动机。

## References
- 原始 PDF：[[A Step Toward World Models- A Survey on Robotic Manipulation.pdf]]（Tongji，arXiv 2511.02097）
- 互补综述：[[Learning to Model the World: A Survey of World|Learning to Model the World]]
- 被归位的库内 WM 论文：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[Robotic World Model: A Neural Network Simulator|RWM]]、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] 等
- 项目入口：[[Final_WMTS]]
