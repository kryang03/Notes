---
tags:
  - paper
  - locomotion
  - sim-to-real
  - domain-randomization
  - actuator-model
  - latency
  - WMTS
aliases:
  - Sim-to-Real Agile Locomotion
paper-year: 2018
read-date: 2026-06-15
venue: RSS 2018 (Google Brain / DeepMind; Jie Tan, Hafner)
paper-pdf: "[[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# Sim-to-Real: Learning Agile Locomotion For Quadruped Robots

> [!abstract] 核心贡献
> 奠基性 sim-to-real 四足（Minitaur trot/gallop，Google，RSS 2018，含 Hafner）。确立**两路并进的 sim-to-real 配方**：(1) **提升 sim 保真**——system identification + **精确 actuator model** + **latency 仿真**；(2) **鲁棒策略**——dynamics randomization + 扰动力 + **紧凑观测空间**。sim 训零样本迁真机 trot/gallop；可选 open-loop 参考步态作人类引导（可控性谱）。**对 WMTS：这是 "actuator model + latency 建模 + DR" 配方的源头——后续 [[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]]（学习式 actuator）、[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]（ADR）都是其精化；其显式 latency 仿真 + 紧凑观测是 WMTS LAAA（延迟适应）与观测设计的早期先例。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — deep RL 学步态；DR 鲁棒化。
> - [[ControlTheory]] — actuator model + latency；接触切换碎裂控制空间。
> - [[EmbodiedAI]] — sim-to-real 两路配方（提保真 + 鲁棒策略）。
> - [[Final_WMTS]] — **actuator model + latency + DR 配方源头**；latency 仿真 + 紧凑观测 = WMTS LAAA/观测设计先例。
>
> **核心技术**: System Identification, Actuator Model, Latency 仿真, Dynamics Randomization, 扰动力, 紧凑观测空间, open-loop 参考步态, Minitaur trot/gallop

## 0. 阅读定位与范本价值

这是知识库里 **sim-to-real 配方的"源头"论文**（2018，比 DeXtreme/Hwangbo/ASAP 都早）。它确立的两路配方——**提 sim 保真（sys-ID + actuator model + latency）+ 鲁棒策略（DR + 扰动 + 紧凑观测）**——是后续所有 sim-to-real 工作的母板。对 WMTS 的价值：(1) 它是 **actuator model + latency 建模**的早期先例，[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]] 是其学习式精化；(2) **显式 latency 仿真**直接是 WMTS **LAAA（latency-conditioned 适应）**的祖先；(3) **紧凑观测空间**是观测设计原则。含 Hafner（Dreamer 作者），Google Brain 系。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
四足敏捷步态设计需大量专家手调；deep RL 可从零学但 sim 策略迁真机差（reality gap，尤其 locomotion 接触切换放大模型误差）；真机学又危险慢。本文在 sim 学、迁真机，用"提 sim 保真 + 鲁棒策略"两路缩 gap。

### 1.2 直观隐喻
reality gap 像"sim 这张地图画得不准"。两条对策并用：(1) **把地图画准**（sys-ID 校参数、actuator model 建电机真实响应、latency 建延迟）；(2) **练成不怕地图错的策略**（DR 随机化、扰动、只看关键信息的紧凑观测）。可证伪含义：两路配方在"gap 可由保真提升 + 鲁棒化覆盖"时有效；gap 太大或结构性时需更强方法（WM/残差）。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 经典控制 + 手调 | 专家步态 | 费力、专家依赖 |
| 纯 sim RL（理想 sim） | deep RL | reality gap（locomotion 放大） |
| 真机学 | 真实交互 | 危险、慢、难重置 |
| **本文** | **sys-ID + actuator model + latency + DR + 紧凑观测** | Minitaur 8-DOF（简单）；手工 actuator model（Hwangbo 学习式精化） |

### 1.4 Delta 分析
精确增量（2018 当时）：把 sim-to-real 系统化为**两路配方**——提保真（sys-ID + actuator model + latency）+ 鲁棒（DR + 扰动 + 紧凑观测），实现 Minitaur 零样本 trot/gallop。确立后续工作的母板。

## 2. 核心方法（原理与方法：两路配方）

### 2.1 提 sim 保真（无跳步）
- **System Identification**：找正确 sim 参数。
- **Actuator Model**：建电机命令→力矩的真实响应（手工模型；Hwangbo 后改学习式 net）。
- **Latency 仿真**：显式模拟传感/控制延迟——locomotion 敏捷动作对延迟敏感。

### 2.2 鲁棒策略（无跳步）
- **Dynamics Randomization**：随机化物理参数 → 策略对参数不确定鲁棒。
- **扰动力**：训练加扰 → 抗扰。
- **紧凑观测空间**：只用关键观测 → 减少 sim-real 观测分布差、防过拟合 sim 特有信号。

### 2.3 可控性谱
从"完全自学"到"指定 open-loop 参考步态"——参考引导下保持步态接近参考、同时平衡/提速/节能。

### 2.4 概念边界与符号陷阱
- 两路是**互补**：保真减小 gap，鲁棒覆盖残余 gap。
- actuator model 手工（Hwangbo 学习式精化）。
- latency 显式仿真（LAAA 先例）。
- Minitaur 8-DOF locomotion，非 in-hand。

## 3. 实验与验证
- Minitaur 真机 trot + gallop，sim 零样本迁移。**因果**：actuator model + latency 提保真 + DR/扰动/紧凑观测鲁棒化 → 跨 gap。
- 可选参考步态控制 gait。
- 边界：8-DOF locomotion；手工 actuator model。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**sim-to-real 应两路并进：提 sim 保真（sys-ID + actuator model + latency）让 sim 更准，鲁棒策略（DR + 扰动 + 紧凑观测）覆盖残余 gap——二者结合实现敏捷步态零样本迁移。** 一句话：**把 sim 画准 + 把策略练得不怕错，两路缩 reality gap。**

### 4.2 为什么有效
(1) actuator model + latency 抓住 locomotion 敏感的执行器/延迟 gap；(2) sys-ID 校参数；(3) DR/扰动鲁棒化；(4) 紧凑观测防过拟合 sim。

### 4.3 什么时候会失效
- gap 结构性（sim 建不了的现象）→ 两路不够（需 WM/残差）。
- 手工 actuator model 不够准（Hwangbo 学习式改进）。
- 接触极复杂（in-hand）超出简单 locomotion。

## 5. 替代方案与局限（未来与结合）
- 后续精化：[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo]]（学习式 actuator net）、[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]（ADR）、[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]（delta-action）。
- 局限：手工 actuator model、8-DOF、locomotion。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | 本文对应 | 迁移设计 |
|---|---|---|
| **LAAA（latency 适应）** | latency 显式仿真 | WMTS 显式建 CAN/控制延迟、latency-conditioned 适应（本文是源头） |
| 结构化 WM actuator | actuator model | WMTS 用 Hwangbo 学习式 actuator net（本文手工版的精化） |
| sim-to-real 两路 | 提保真 + 鲁棒 | WMTS：结构化 WM（保真）+ ensemble/DR（鲁棒） |
| 观测设计 | 紧凑观测 | WMTS 观测设计含触觉但避冗余 sim 特有信号 |

**核心论证（critical thinking）**：这篇是 WMTS sim-to-real 思路的**历史源头与最小配方**。它确立的"**提 sim 保真 + 鲁棒策略**"两路，正是 WMTS 的骨架：WMTS 的**结构化 WM（actuator net + Lagrangian + 接触力）= "提保真"路的现代极致**，**ensemble/DR = "鲁棒"路**。尤其它的**显式 latency 仿真**是 WMTS **LAAA（latency-conditioned 适应）的直接祖先**——WMTS 要建 CAN 1Mbps 控制延迟并让策略/WM 条件于延迟适应。它的 **actuator model** 被 [[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]] 升级为学习式（WMTS 取后者），**紧凑观测**是观测设计原则（WMTS 含触觉但避冗余）。**定位**：作为 2018 奠基作，它的具体方法已被后续（Hwangbo/DeXtreme/ASAP/SSRL）精化超越，WMTS 应取其**配方框架**（两路 + latency + actuator）而非具体手工实现；含 Hafner（Dreamer），是 Google Brain sim-to-real → world model 的早期一环。Minitaur 8-DOF locomotion 远简于转笔，接触侧需 SSRL/触觉补。

### 6.2 可验证实验建议
- LAAA latency：WMTS 显式建 CAN 延迟 + latency-conditioned 适应，对照无 latency 建模（复刻本文 latency 仿真价值）。
- 两路配方：WMTS 结构化 WM（保真）+ ensemble（鲁棒）的组合消融。

### 6.3 不应过度外推的点
- 8-DOF locomotion 远简于 in-hand 转笔。
- 手工 actuator model 已被学习式（Hwangbo）超越。
- 两路配方对结构性 gap 不够（需 WM/残差）。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
deep RL 学步态；DR 鲁棒化；sim 训零样本迁移。

### 与 [[ControlTheory]] 的联系
actuator model + latency 仿真；接触切换碎裂控制空间、放大模型误差。

### 与 [[EmbodiedAI]] 的联系
sim-to-real 两路配方（提保真 + 鲁棒策略）的奠基；Minitaur trot/gallop。

### 与 [[Final_WMTS]] 的联系
actuator model + latency + DR 配方源头；latency 仿真 = LAAA 先例；actuator model 被 Hwangbo 学习式精化（WMTS 取后者）；紧凑观测 = 观测设计原则。

## References
- 原始 PDF：[[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots.pdf]]（Google，RSS 2018）
- 精化后继：[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]]、[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]（ADR）、[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]、[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]
- 项目入口：[[Final_WMTS]]
