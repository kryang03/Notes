---
tags:
  - paper
  - humanoid
  - sim-to-real
  - whole-body-control
  - residual-action
  - WMTS
aliases:
  - ASAP
paper-year: 2025
read-date: 2026-06-15
venue: arXiv 2502.01143 (CMU / NVIDIA; Guanya Shi, Yuke Zhu, Jim Fan)
paper-pdf: "[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# ASAP: Aligning Simulation and Real-World Physics for Agile Humanoid Skills

> [!abstract] 核心贡献
> 解决 sim-real **动力学 mismatch** 的两阶段框架，让 Unitree G1 人形做敏捷全身技能（Ronaldo 庆祝转体、Kobe 后仰跳投、1.5m 跳）。核心是 **delta（residual）action model**：(1) 用 retarget 的人类动作在 sim 预训练 motion tracking 策略，部署真机收集真实轨迹；(2) 训一个 **delta action 模型**，使"sim 在原动作 + delta 后的状态"逼近真实状态（最小化 sim 态与真实态差）；(3) **冻结 delta 模型嵌进 simulator 对齐真实物理**，在校正后的 sim 里 fine-tune 策略；(4) 部署时**去掉 delta 模型**直接上真机。**对 WMTS：delta-action 是继 DR（[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]] 盲随机化）、full-WM（[[Finetuning Offline World Models in the Real World|FOWM]]/[[DayDreamer- World Models for Physical Robot Learning|DayDreamer]] 学动力学）之后的第三条 sim-to-real 哲学——保留物理 sim、用学到的残差动作吸收 gap，再在校正 sim 里微调；轻量、可与 WMTS 结构化 WM 结合。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — sim 预训练 motion tracking + 校正 sim 内 fine-tune。
> - [[ControlTheory]] — delta action = 对 sim 动力学的残差校正（学习式 sim 对齐）。
> - [[EmbodiedAI]] — 人形全身 sim-to-real；retarget 人类动作。
> - [[Final_WMTS]] — **第三条 sim-to-real 哲学（delta-action 对齐 sim）**；可与结构化 WM 结合；亦关联用户 Humanoid Locomotion 项目。
>
> **核心技术**: Delta (residual) Action Model, 两阶段 (sim 预训→真实数据→对齐→微调), 人类动作 retarget, motion tracking, 部署去 delta, Unitree G1

> [!note] 簇内定位（运动迁移 sim-to-real 簇）与精确锚点
> **本篇 = sim-to-real 第三条哲学：保留物理 sim、学 delta-action 残差对齐。** 精确 Foundation 锚点：
> - [[Dynamics#9. 适配层：可微物理与神经动力学]] — delta-action = 对已知物理 sim 动力学的**神经残差校正**（不重建、只对齐）。
> - [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）]] — delta-action 是"动态校正"这味药的学习式实现：用神经残差替 sys-ID 的参数标定。
>
> **簇内 Delta：**
> - vs [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]]：都"物理结构 + 学习残差"，但本篇残差在**动作通道** $a+\Delta a$ 且**部署去除**，SSRL 残差在**接触力通道** $F^e$ 且**永久作 WM**——本篇只为训练期对齐 sim，SSRL 的残差长期供规划/想象。
> - vs [[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]]：都学残差弥合 gap，但 Hwangbo 残差挂**执行器力矩**（物理量、永久嵌 sim），本篇挂**动作**（部署去除）——残差挂哪个物理量 + 是否保留，是分野。
> - vs [[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots|Jie Tan 2018]]：都"提 sim 保真"，但 Jie Tan 靠静态 sys-ID/手工 actuator model，本篇靠**学习 delta-action 动态对齐**——静态先验 → 数据驱动残差。

## 0. 阅读定位与范本价值

ASAP 在知识库里是 **sim-to-real "第三条哲学" 的代表**，补全 sim-real gap 的处理谱系：

- **DR（[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]/[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]]）**：盲随机化覆盖真实分布。
- **full-WM（[[Finetuning Offline World Models in the Real World|FOWM]]/[[DayDreamer- World Models for Physical Robot Learning|DayDreamer]]）**：学一个动力学模型，在其内训。
- **ASAP delta-action**：**保留物理 sim，学一个残差动作模型吸收 sim-real gap**，在校正后的 sim 里微调。

读它要抓 delta-action 的巧思：不重建动力学（WM）、不盲随机化（DR），而是**学最小残差让现有 sim 匹配真实**——前提是 sim 大体正确（残差小）。它与用户的 **Humanoid Locomotion 项目**直接相关，也与 [[Robotic World Model: A Neural Network Simulator|RWM]]（ETH 学 NN 仿真器）形成"学残差 vs 学整模型"的对照。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
人形敏捷全身技能受 sim-real 动力学 mismatch 限。SysID/DR 费力或过保守（牺牲敏捷）。ASAP 用 delta-action 模型从真实数据学一个残差校正，把 sim 物理对齐真实，再在校正 sim 里微调策略 → 敏捷且可迁移。

### 1.2 直观隐喻
sim 像"一张略有偏差的地图"。DR 是"在地图上到处加噪练到对任何偏差都不怕"（盲、保守）；full-WM 是"重画一张地图"（重）；ASAP 是"**学一个小修正量贴在旧地图上让它准**"（delta action），然后在修正后的准地图上精修路线。修好后上路（真机）就不用修正量了。可证伪含义：delta-action 有效要求 **sim 大体正确、gap 可由动作残差吸收**；若 gap 来自 sim 无法表达的结构（如未建的接触），残差吸收不了。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法                                                                               | 注入的先验                                                    | 关键局限                                   |             |                      |
| -------------------------------------------------------------------------------- | -------------------------------------------------------- | -------------------------------------- | ----------- | -------------------- |
| SysID                                                                            | 校准 sim 参数                                                | 费力；real 超出建模分布时失效                      |             |                      |
| DR（[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality | DeXtreme]]）                                              | 盲随机化                                   | 过保守牺牲敏捷；调参多 |                      |
| full-WM（[[Finetuning Offline World Models in the Real World                      | FOWM]]/[[Robotic World Model: A Neural Network Simulator | RWM]]）                                 | 学整动力学       | 重；model-exploitation |
| **ASAP delta-action**                                                            | 残差校正现有 sim                                               | 需 sim 大体正确；gap 须可由动作残差吸收；全身（非 in-hand） |             |                      |

### 1.4 Delta 分析
精确增量：**delta (residual) action model**——从真实 rollout 学一个残差动作，使"sim(动作+delta)"的状态轨迹逼近真实，从而**对齐 sim 物理而不重建它**；冻结后嵌 sim 微调策略，部署去除。把"随机化/重建动力学"换成"学最小残差对齐"。

## 2. 核心方法（原理与方法：delta-action 四阶段）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| 人类动作 retarget | motion | 人类视频→G1 | 数据 | tracking 目标 | imitation goal |
| $a_t$ | 动作 | 策略 | learned | 名义动作 | — |
| $a_t'=a_t+\text{delta}$ | 校正动作 | delta 模型 | learned | 残差校正后动作 | 仅训练期用 |
| $s_t$ vs $s_t^r$ | sim 态 / 真实态 | sim / 真机 | observed | 对齐目标 | 最小化 $\|s_t-s_t^r\|$ |
| delta action 模型 | 残差 | 真实数据训 | learned | 吸收 sim-real gap | 训练后**冻结**，部署**去除** |

### 2.2 四阶段（无跳步，ASAP Fig 2）
1. **Motion tracking 预训练 + 真实轨迹收集**：retarget 人类动作 → sim 预训练多个 tracking 策略 → 真机 rollout 收集真实轨迹 $(s^r,a^r)$。
2. **Delta action 模型训练**：基于真实 rollout，训 delta 模型使 **sim 在 $a_t'=a_t+\text{delta}$ 下的状态 $s_t$ 逼近真实 $s_t^r$**（最小化差）——即让 sim 动力学经残差校正后匹配真实。
3. **策略 fine-tune**：**冻结 delta 模型嵌进 simulator**（此时 sim 物理已对齐真实），在校正 sim 里 fine-tune 预训练 tracking 策略。
4. **真实部署**：部署 fine-tuned 策略，**不再用 delta 模型**（策略已适应校正后的真实物理）。

### 2.3 概念边界与符号陷阱
- delta-action **对齐 sim**，不重建 sim（≠ WM）也不盲随机化（≠ DR）。
- delta 模型**只在训练期用**（校正 sim），部署去除——这是它与"在 WM 里部署"的关键区别。
- 前提：**sim 大体正确、gap 可由动作残差吸收**；sim 无法表达的结构性 gap（未建接触）吸收不了。
- 全身敏捷（G1），非 in-hand 接触。

## 3. 实验与验证
- Unitree G1 敏捷全身技能（Ronaldo 转体、Kobe 跳投、1.5m 跳、单腿平衡）真机成功。**因果**：delta-action 对齐 sim 物理，微调策略迁移敏捷动作。
- 胜 SysID/DR：更敏捷（不过保守）、更省调参。
- 边界：全身（非 in-hand）；需 sim 大体正确。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**与其盲随机化（DR）或重建动力学（WM），不如从真实数据学一个 delta（residual）action 模型，让现有物理 sim 经残差校正后匹配真实，再在校正 sim 里微调策略——部署时去除 delta，得到敏捷且可迁移的全身技能。** 一句话：**学最小残差对齐 sim，比盲随机化或重建动力学更轻更敏捷。**

### 4.2 为什么有效
(1) delta 吸收 sim-real gap 而不牺牲敏捷（DR 的过保守）；(2) 保留物理 sim 的结构（不像 WM 从零学）；(3) 校正 sim 内微调 → 策略适应真实物理；(4) 部署去 delta → 无额外推理负担。

### 4.3 什么时候会失效
- sim 无法表达的结构性 gap（未建接触/形变）→ 残差吸收不了。
- sim 偏差太大（残差非小量）→ delta 模型难学。
- 真实数据不足以覆盖技能状态空间。

## 5. 替代方案与局限（未来与结合）

### 5.1 理论维度
delta-action 是"学习式 sim 对齐"：假设真实动力学 ≈ sim 动力学 + 动作残差校正。比 SysID（参数校准）更灵活、比 DR（分布覆盖）更精准、比 WM（重建）更轻——但受限于"残差可吸收 gap"的假设。

### 5.2 算法维度（sim-to-real 三哲学，对 WMTS 关键）
| 哲学 | 代表 | 机制 |
|---|---|---|
| **DR（盲覆盖）** | [[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]/[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]] | 随机化覆盖真实 |
| **full-WM（重建）** | [[Finetuning Offline World Models in the Real World|FOWM]]/[[Robotic World Model: A Neural Network Simulator|RWM]] | 学动力学、其内训 |
| **delta-action（对齐）** | 本文 ASAP | 残差校正现有 sim |

### 5.3 工程/实验维度
sim 保真前提、真实数据覆盖、残差可吸收性、全身 vs in-hand 是主要边界；接触密集、触觉未覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM / Humanoid Locomotion 的迁移

| 模块 | ASAP 对应 | 迁移设计 |
|---|---|---|
| **sim-to-real（WMTS）** | delta-action 对齐 sim | WMTS 可用 delta-action 校正物理 sim（替/补 full-WM）：真实数据学残差、校正 sim 微调 Oracle/generalist |
| 与结构化 WM 结合 | 残差 on 物理 sim | WMTS 的 actuator+rigid 结构化 sim + delta-action 残差 = 结构先验 + 学习残差（呼应 DexSim2Real2 显式 + 残差） |
| Humanoid Locomotion 项目 | G1 全身敏捷 | 用户 Humanoid 项目可直接用 ASAP 范式 |
| 部署 | 去 delta | 微调期校正、部署轻量 |

**核心论证（critical thinking）**：ASAP 给 WMTS 补上 **sim-to-real 的"第三条哲学"**。WMTS 默认走 full-WM（学动力学 + 在其内训/精炼），但 ASAP 提示一个更轻的选项：**保留 actuator+rigid 物理 sim，只学一个 delta-action 残差吸收 sim-real gap，在校正 sim 里微调，部署去除残差**。这与我在 [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] recap 提的"结构化先验 + 学习残差"完全合流——**WMTS 的理想形态可能不是纯神经 WM，而是"结构化物理 sim + delta-action/残差 + ensemble 不确定性"**：结构先验保物理正确性（无 model-exploitation）、delta 残差吸收 sim 建不准的部分、ensemble 量化残差不确定。**但对转笔的关键警示**：ASAP 的前提是 **sim 大体正确、gap 可由动作残差吸收**——而转笔的高速接触动力学恰恰是 **sim 难建准、gap 可能是结构性的（接触模式 sim 根本没有）**，此时 delta-action 残差吸收不了（它假设状态空间对、只是动作偏），可能仍需 full-WM 或结构化 WM 补结构性 gap。ASAP 是全身敏捷（G1），非 in-hand 接触——delta-action 对相对光滑的全身动力学有效，对接触切换密集的转笔需验证。它也直接服务用户的 **Humanoid Locomotion 项目**。

### 6.2 可验证实验建议
- delta-action vs full-WM：转笔上对照"结构化 sim + delta-action 残差微调" vs "full-WM 内微调"，测 sim-real gap 闭合与敏捷度。
- 残差可吸收性测试：测转笔的 sim-real gap 是动作残差可吸收（ASAP 适用）还是结构性（需 WM）。
- 三哲学组合：结构化 sim + delta-action + ensemble-LCB 的叠加。

### 6.3 不应过度外推的点
- 全身敏捷成功不能外推 in-hand 接触；转笔 gap 可能结构性、残差吸收不了。
- delta-action 假设 sim 大体正确；转笔 sim 难建准。
- 部署去 delta 依赖策略已适应校正物理。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
sim 预训练 motion tracking + 校正 sim 内 fine-tune；retarget 人类动作作 imitation goal。

### 与 [[ControlTheory]] 的联系
delta action = 对 sim 动力学的学习式残差校正（sim 对齐），与 SysID/自适应控制一脉但用神经残差。

### 与 [[EmbodiedAI]] 的联系
人形全身 sim-to-real；从人类视频 retarget 敏捷动作；G1 真机敏捷技能。

### 与 [[Final_WMTS]] 的联系
sim-to-real 第三哲学（delta-action 对齐 sim）；WMTS 可"结构化 sim + delta 残差 + ensemble"组合；但转笔结构性 gap 可能需 full-WM；直接服务用户 Humanoid Locomotion 项目。

## References
- 原始 PDF：[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills.pdf]]（CMU/NVIDIA，arXiv 2502.01143）
- sim-to-real 三哲学：[[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality|DeXtreme]]（DR）、[[Finetuning Offline World Models in the Real World|FOWM]]/[[Robotic World Model: A Neural Network Simulator|RWM]]（full-WM）、本文（delta-action）
- 结构化+残差呼应：[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]
- 项目入口：[[Final_WMTS]]、Humanoid Locomotion 项目
