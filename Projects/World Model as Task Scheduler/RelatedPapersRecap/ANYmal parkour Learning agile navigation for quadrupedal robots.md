---
tags:
  - paper
  - locomotion
  - sim-to-real
  - parkour
  - hierarchical
  - WMTS
aliases:
  - ANYmal Parkour
paper-year: 2024
read-date: 2026-06-15
venue: Science Robotics 2024 (ETH Zurich; Hoeller, Rudin, Hutter)
paper-pdf: "[[ANYmal parkour Learning agile navigation for quadrupedal robots.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# ANYmal Parkour: Learning Agile Navigation for Quadrupedal Robots

> [!abstract] 核心贡献
> 全学习式四足 parkour（ETH，Science Robotics 2024）：**三模块分层**——感知（点云/LiDAR→地形重建，处理遮挡噪声）、运动（技能库：走/跳/爬/蹲）、导航（**高层策略选择并控制技能**）。关键：**导航策略"知道每个技能的能力"**，据场景自适应选技能 + 给中间命令。无需 expert demo、离线计算、环境先验、显式接触建模。sim 训、真机迁移、2 m/s 过连续障碍。**对 WMTS：又一个 scheduler-over-skills 范式（与 From-Simple-to-Complex、DexReMoE、UniDexGrasp++ 同族），独特点是"高层感知低层技能的能力（capability-aware）"——正对应 WMTS scheduler 需要一个技能能力/可行性模型来做 Solve/Probe/Reject。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 分层 RL：高层选技能、低层技能策略；sim 训。
> - [[ControlTheory]] — 敏捷动态运动、接触多变；技能库 + 高层调度。
> - [[EmbodiedAI]] — sim-to-real 分层导航；遮挡感知重建。
> - [[Final_WMTS]] — **capability-aware 分层 scheduler**：高层知技能能力→选技能；对应 WMTS Solve/Probe/Reject。
>
> **核心技术**: 三模块（感知/运动/导航）, 技能库（走/跳/爬/蹲）, capability-aware 高层导航策略, 遮挡感知重建, sim-to-real, 无 demo/无显式接触

> [!note] 簇内定位（运动迁移 sim-to-real 簇）与精确锚点
> **本篇 = 把 sim-to-real 复杂度放在"任务分解/技能调度"侧（而非动力学建模侧）的代表。** 精确 Foundation 锚点：
> - [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机]] — 全 sim 训、零样本迁真机的分层策略。
> - [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间]]、[[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成]] — **capability-aware 高层"知道每个技能能干什么" = 认知不确定性三用之"课程用"**（在能力边界处选/学、不选超能力技能）；挂**认知不确定性三用**暗线。
>
> **簇内 Delta：**
> - vs [[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots|Jie Tan 2018]]：Jie Tan 是**单策略** trot/gallop（用 actuator model+latency+DR 隐式缩 gap），本篇是**分层技能库 + capability-aware 调度**攻克离散障碍拓扑——复杂度从"缩 reality gap"转到"任务分解/可行性调度"。
> - vs [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]：SSRL 把复杂度放在**动力学建模**（3 分钟真机学 semi-structured WM），本篇放在**技能调度**（全 sim、无 WM）——两条正交路线，WMTS 二者皆需（SSRL 供 WM、本篇供 scheduler）。
> - vs [[FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning|FLD]]：两者都做**可行性感知的目标/技能筛选**——本篇 capability-aware 在**离散技能库**上选可行技能，FLD 的 fallback 在**连续 Fourier 运动 latent** 上拒危险/不可学目标；WMTS 的 Solve/Probe/Reject 可两者结合。

## 0. 阅读定位与范本价值

ANYmal Parkour 对 WMTS 的价值是 **scheduler-over-skills 范式的又一实证 + "capability-aware" 关键 nuance**。库内已有 [[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|From-Simple-to-Complex]]（高层选轴+residual）、[[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts|DexReMoE]]（软 router）、[[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]]（GiGSL）——本篇加上"**高层导航策略知道每个技能的能力、据此选技能**"这一点，正是 WMTS scheduler 做 **Solve/Probe/Reject** 所需的"技能能力/可行性模型"。它是 ETH Hutter 系（[[Robotic World Model: A Neural Network Simulator|RWM]]/[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]]/[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo]] 同组）的分层导航代表。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
四足 parkour 要在快速变化、接触多变、感知受限下，理解场景、选可行路径 + 动作序列。本文用三模块分层（感知/运动/导航）全学习式攻克：技能库覆盖各障碍，高层据"技能能力"选技能，sim 训真机迁移。

### 1.2 直观隐喻
像跑酷运动员：有一套基本功（走/跳/爬/蹲，运动模块），大脑（导航模块）**知道自己每个动作能干什么**，看到障碍就选合适的动作并精确发令。可证伪含义：分层有效要求"**技能库覆盖所需 + 高层准确知道技能能力**"；技能缺或高层误判能力则失败。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 单体策略 | 端到端 | 难覆盖多样障碍 + 高层规划 |
| 显式规划 + 接触 | 接触建模 | 接触不可预设、离线计算贵 |
| 需 expert demo / 环境先验 | 示范/地图 | 不可扩展 |
| **ANYmal Parkour** | **技能库 + capability-aware 高层** | locomotion（非 in-hand）；感知靠视觉/LiDAR |

### 1.4 Delta 分析
精确增量：(1) **技能库（走/跳/爬/蹲）+ capability-aware 高层导航**（高层知技能能力、选技能 + 中间命令）；(2) **遮挡感知重建**（噪声/遮挡点云→地形）；(3) 无 demo/无离线/无环境先验/无显式接触。把"端到端或显式规划"换成"分层 + 能力感知调度"。

## 2. 核心方法（原理与方法：三模块分层）

### 2.1 三模块（无跳步）
1. **感知模块**：onboard 相机 + LiDAR 点云 → 周围地形估计；**从遮挡/噪声数据重建**障碍（场景理解）。
2. **运动模块**：**技能库**——走/跳/爬/蹲，每个克服特定地形（分别 RL 训）。
3. **导航模块（高层）**：**选择激活哪个技能 + 给中间命令**；**感知每个技能的能力**，据场景自适应。
全部 sim 训、sim-to-real。

### 2.2 capability-aware 高层（关键 nuance）
导航策略**知道每个技能能干什么**（capability-aware）→ 在障碍前选可行技能、不选超出能力的。这是分层不脆的关键（呼应 [[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|From-Simple-to-Complex]] 的低层反馈）：高层基于能力做可行选择。

### 2.3 概念边界与符号陷阱
- 高层是**技能选择器 + 能力模型**，非端到端。
- 感知靠视觉/LiDAR（遮挡重建）——WMTS 用触觉。
- locomotion 技能（地形），非 in-hand。
- 无显式接触建模（locomotion 接触较简单）。

## 3. 实验与验证
- 真机过连续障碍、2 m/s、窄如足印的箱子、高障碍全幅运动。**因果**：技能库覆盖 + capability-aware 高层选可行技能 + 准感知重建。
- sim-only 训、sim-to-real，高频地图更新、快速下重建准。
- 边界：locomotion；视觉/LiDAR 感知。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**复杂敏捷导航可由"技能库 + capability-aware 高层调度"全学习式解决：低层技能覆盖各障碍，高层知道每个技能的能力、据场景选技能并发中间命令，配遮挡感知重建，sim 训真机迁移。** 一句话：**高层调度要知道低层技能的能力边界，才能选得对。**

### 4.2 为什么有效
(1) 技能库分解复杂任务；(2) capability-aware 高层选可行技能；(3) 感知重建给场景理解；(4) sim 训 + 高效 → 真机实时。

### 4.3 什么时候会失效
- 技能库未覆盖的障碍。
- 高层误判技能能力。
- 感知重建在极端遮挡/噪声失败。

## 5. 替代方案与局限（未来与结合）
- 分层 scheduler 族：[[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|From-Simple-to-Complex]]（硬选+residual）、[[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts|DexReMoE]]（软 router）、[[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]]（GiGSL）——本篇加 capability-aware。
- 局限：locomotion、视觉感知、技能库覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | ANYmal Parkour 对应 | 迁移设计 |
|---|---|---|
| **Scheduler（Solve/Probe/Reject）** | capability-aware 高层选技能 | WMTS scheduler 需**技能能力/可行性模型**：知每个转笔子技能能力→选/Probe/Reject |
| 技能库 | 走/跳/爬/蹲 | WMTS 转笔子技能库（不同相位/抓握） |
| 感知 | 遮挡重建（视觉/LiDAR） | WMTS 用触觉+本体（转笔遮挡更甚） |
| sim-to-real | 全 sim 训迁移 | 配 actuator net/结构化 WM |

**核心论证（critical thinking）**：ANYmal Parkour 给 WMTS scheduler 补上一个关键设计原则——**capability-awareness**。库内 scheduler 族（From-Simple/DexReMoE/UniDexGrasp++）讲"怎么选/组合技能"，本篇讲"**高层必须知道每个技能的能力边界才能选得对**"——这正是 WMTS 的 **Solve/Probe/Reject 三队列**所需：scheduler 要对每个转笔任务/子技能有一个**能力/可行性/可靠性模型**（哪些能直接 Solve、哪些不确定需 Probe、哪些超能力须 Reject）。结合 [[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]] 的 uncertainty 阈值、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]] 的 ensemble-LCB，WMTS scheduler 的能力模型可由 **WM 预测 + ensemble 不确定性 + 技能能力先验**构成。**边界**：这是 locomotion 地形导航，技能能力相对易刻画（能跨多高、多宽）；转笔子技能的"能力"更难量化（高速接触成功率），且感知是视觉/LiDAR（WMTS 用触觉）。它是 ETH Hutter 系，与 actuator net、RWM 一脉，方法可借。

### 6.2 可验证实验建议
- WMTS scheduler capability 模型：为每个转笔子技能学能力/可行性预测（WM+ensemble），驱动 Solve/Probe/Reject，测三队列准确率。
- 技能库 + capability-aware 调度 vs 单体 generalist 在转笔难配置上的对比。

### 6.3 不应过度外推的点
- locomotion 技能能力易刻画，转笔子技能能力难量化。
- 视觉/LiDAR 感知 → WMTS 用触觉。
- 技能库覆盖决定上限。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
分层 RL：高层技能选择 + 低层技能策略；sim 训、无 demo。

### 与 [[ControlTheory]] 的联系
敏捷动态运动、接触多变；技能库 + 高层调度替显式规划。

### 与 [[EmbodiedAI]] 的联系
sim-to-real 分层导航；遮挡/噪声感知重建场景理解。

### 与 [[Final_WMTS]] 的联系
capability-aware 高层调度 = WMTS scheduler 需技能能力/可行性模型做 Solve/Probe/Reject；与 ensemble-LCB/uncertainty 结合构成能力模型。

## References
- 原始 PDF：[[ANYmal parkour Learning agile navigation for quadrupedal robots.pdf]]（ETH，Science Robotics 2024）
- scheduler 族：[[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|From-Simple-to-Complex]]、[[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts|DexReMoE]]、[[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]]
- 能力/可靠性 + uncertainty：[[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]]、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]
- ETH 系：[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]]、[[Robotic World Model: A Neural Network Simulator|RWM]]
- 项目入口：[[Final_WMTS]]
