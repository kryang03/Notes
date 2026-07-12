---
tags:
  - paper
  - semi-structured-dynamics
  - model-based-rl
  - locomotion
  - real-world-data
  - ensemble
  - WMTS
aliases:
  - SSRL
  - Three-Minute Semi-Structured Dynamics
paper-year: 2024
read-date: 2026-06-15
venue: CoRL 2024 (UT Austin / UW; Fridovich-Keil)
paper-pdf: "[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# SSRL: Learning to Walk from 3 Minutes of Real Data with Semi-structured Dynamics

> [!abstract] 核心贡献
> **WMTS world model 架构的"蓝图级"先例**：提出 **semi-structured dynamics model**——把**已知第一性原理（Lagrangian 刚体动力学）**与**黑箱自回归模型**无缝结合。具体：用**一组概率模型（ensemble）估计外部/接触力** $\hat\tau^e$（条件于历史 obs+action），再通过**已知 Lagrangian ODE** $M(q)\ddot q+\dots=B\tau+F^e$ 积分 + 学习噪声项 → 概率单步预测 → 自回归多步。如此用**远少于以往**的数据做准长程预测。配套 **SSRL**（semi-structured RL，Dyna 式：真实数据 + 想象短 rollout + model-free RL）在真机 Unitree Go1 上**从零、用 3 分钟真实数据**学会硬地与软地（记忆海绵）动态步态。**对 WMTS：这几乎就是 WMTS WM 该有的样子——已知 actuator+rigid 结构（Lagrangian）+ ensemble 估计接触力残差（从触觉/历史）+ 自回归 + Dyna RL；它解决了 [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（纯显式建不了形变/接触）与神经 WM（无结构、要大数据）的张力，且 3 分钟样本效率让 WMTS 的"≤1h 真机"显得宽裕。**

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — Lagrangian 刚体动力学 $M(q)\ddot q+C\dot q+g=B\tau+F^e$；已知结构 + 未知外力。
> - [[ReinforcementLearning]] — Dyna 式 MBRL（真实数据 + 想象 rollout + model-free 更新）。
> - [[EmbodiedAI]] — 真机从零学步态、3 分钟数据、硬/软地泛化。
> - [[Final_WMTS]] — **WMTS WM 架构蓝图**：结构化 Lagrangian + ensemble 接触力残差 + 自回归 + Dyna。
> - [[Dynamic Non-Prehensile Manipulation]] — 转笔同理：已知手/笔刚体 + 学多指接触力残差。
>
> **核心技术**: Semi-structured dynamics (Lagrangian + 黑箱), Ensemble 概率外力估计 $\hat\tau^e$, 自回归多步预测, 学习噪声项, SSRL (Dyna), 3 分钟真机数据, Go1 硬/软地

> [!note] 簇内定位（运动迁移 sim-to-real 簇）与精确锚点
> **本篇 = "结构（刚体）已知 + 残差（接触力）学习"的 WM 架构蓝图。** 精确 Foundation 锚点：
> - [[Dynamics#9. 适配层：可微物理与神经动力学]] — semi-structured 正是"已知 Lagrangian 刚体 + 神经残差"的神经动力学落地。
> - [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦]] — 本篇是该"结构+残差"决策的最贴合先例。
> - [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]] — ensemble 估外力残差 → disagreement = **认知不确定性三用**（规划护栏 / 探索罗盘 / 课程"该学处"）；挂该暗线。
> - [[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习]] — 只学外力残差 $F^e$，是"系统辨识→残差回归"的 ensemble 版（对照 GP 版）。
>
> **簇内 Delta：**
> - vs [[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo actuator net]]：**互补拼图**——Hwangbo 建**执行器侧**（命令→力矩），本篇建**刚体侧 Lagrangian**（力矩→加速度）+ **接触力残差**；串起 = WMTS 完整结构化动力学。
> - vs [[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]：都"物理结构 + 学习残差"，但本篇残差在**接触力通道** $F^e$（显式物理量、永久作 WM 一部分、供 Dyna 想象），ASAP 残差在**动作通道**且**部署去除**——本篇残差长期供规划，ASAP 只为训练期对齐 sim。
> - vs [[Sim-to-Real: Learning Agile Locomotion For Quadruped Robots|Jie Tan 2018]]：Jie Tan 全 sim 零样本（先验标定 + DR），本篇**3 分钟真机数据**在自学的 semi-structured WM 内 Dyna 训——sim-first 零样本 vs real-data model-based。

## 0. 阅读定位与范本价值

SSRL 是知识库里 **与 WMTS world model 架构最贴合的一篇**——它把我前面反复论证的"**结构化先验 + 学习残差 + ensemble**"在真机 contact-rich 系统上落地并证明极致样本效率（3 分钟）。它精确收束两条对立路线：

- **纯显式物理（[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]）**：刚体可重建、但建不了形变/复杂接触。
- **纯神经 WM（[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[Robotic World Model: A Neural Network Simulator|RWM]]）**：通用、但无结构、需大数据、有 model-exploitation。
- **SSRL semi-structured**：**已知部分用第一性原理（Lagrangian），难建的接触力用 ensemble 黑箱估计残差**——两全。

读它要抓核心方程结构：$M,B$ 已知（几何/惯量），只学 $F^e$（外部/接触力）。这正是 WMTS 该对手-笔系统做的：刚体/actuator 已知、学多指接触力残差。它与 [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]（ensemble 黑箱动力学）、[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]（残差对齐）、[[Robotic World Model: A Neural Network Simulator|RWM]]（自回归）密切相关，但**结构化程度恰到好处**。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
MBRL 用黑箱神经网络建动力学，但数据稀缺时不泛化、不胜 model-free；纯结构化物理模型高效但**建不了接触**（开放难题），且常需特权状态（精确知道何时何地接触）。SSRL 问：**能否用已知结构 + 板载传感、轻量地建 contact-rich 动力学？** 答案：semi-structured——Lagrangian 已知 + ensemble 估外力残差，3 分钟真机学会走路。

### 1.2 直观隐喻
纯神经 WM 像"完全不懂物理、纯靠海量数据猜"（数据贵、不泛化）；纯显式物理像"懂刚体但一遇到脚踩软泥（接触）就抓瞎"。SSRL 像"懂刚体力学（Lagrangian 算好骨架运动），只把'地面给脚多大反力'这件难事交给一组学生（ensemble）从手感历史去估"——骨架精确、难点学习、且因骨架已知，学得又快又准。可证伪含义：semi-structured 的样本效率优势依赖"**结构（刚体）确实已知且主导**，残差（接触力）虽难但可从历史估"；若结构本身错，残差补不回。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 黑箱神经 MBRL（[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[Robotic World Model: A Neural Network Simulator|RWM]]） | NN 灵活逼近 | 数据稀缺不泛化、不胜 model-free |
| 纯结构化物理 | 第一性原理 | **建不了接触**；需特权状态（何时何地接触） |
| 物理信息 NN（PINN） | 软物理约束 | 不 scale 到真机 contact-rich |
| 显式接触（需 SDF/特权） | 接触面表示 | 板载传感难可靠估计 |
| **SSRL semi-structured** | **Lagrangian + ensemble 外力残差** | 需结构主导；quadruped 足-地接触（非多指 in-hand） |

### 1.4 Delta 分析
精确增量：**semi-structured = Lagrangian 刚体（已知 $M,B$）+ ensemble 概率外力估计 $\hat\tau^e$（黑箱，条件历史）+ 自回归 + 学习噪声**。相对黑箱：注入刚体结构 → 样本效率暴增（3 分钟）；相对纯结构化：把"建不了的接触"交给 ensemble 残差，且只用板载传感（不需特权接触状态）。

## 2. 核心方法（原理与方法：Lagrangian + ensemble 外力残差）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $q,\dot q$ | 广义坐标/速度 | 状态 | observed | 机器人构型 | — |
| $M(q),B$ | 惯量/分配矩阵 | **已知**（几何/惯量） | 固定 | 第一性原理结构 | a priori，不学 |
| $\tau$ | 电机力矩 | 策略 | 选择 | 关节力矩 | 经 $B$ 分配 |
| $F^e/\tau^e$ | 外部/接触力 | **未知** | — | 环境给的力 | **要学的难点** |
| $\hat\tau^e$ | 估计外力 | **ensemble 概率模型** | learned | 黑箱残差，条件历史 $h_t$ | ensemble → 不确定性 |
| 噪声项 | 学习 | — | learned | 概率单步预测 | — |
| $h_t$ | 历史 obs+action | replay | 条件 | 自回归依据 | 喂回 $\hat\tau^e$ |

### 2.2 Semi-structured 动力学（无跳步，核心）
Lagrangian 运动方程：
$$
M(q)\ddot q + C(q,\dot q)\dot q + g(q) = B\tau + F^e,
$$
其中 $M,B$（及 $C,g$）由**已知几何/惯量**确定，$F^e$ = 环境接触力（未知、难建）。SSRL：
1. **ensemble 外力估计**：$\hat\tau^e$ = 一组**确定性外力估计器**（ensemble），条件于历史 $h_t$（obs+action）；
2. **结构积分**：把 $\hat\tau^e$ 代入 Lagrangian ODE 积分 + 加**学习噪声**项 → **概率 1-step 预测** $p_s(s_{t+1}\mid s_t,a_t)$；
3. **自回归**：预测喂回 $h_t$ → 多步预测；
4. **拟合**：用真实数据拟合这个 semi-structured 表示。

**关键**：只学 $F^e$（接触力残差），刚体部分用第一性原理 → 极少数据即准长程。

### 2.3 SSRL（Dyna 式 RL）
- **确定性策略**在真机收集数据；
- **随机策略 + 学到的 semi-structured 模型** hallucinate **短想象 rollout**（从真实数据分支）；
- **model-free RL** 用合成数据更新策略。
（这是 Dyna/MBPO 结构，同 [[Robotic World Model: A Neural Network Simulator|RWM]]/[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]。）

### 2.4 概念边界与符号陷阱
- semi-structured：**结构（Lagrangian）已知 + 残差（外力）学习**——不是纯黑箱也不是纯物理。
- ensemble 在**外力残差**上（非整动力学）→ 轻量 + 不确定性。
- 只用**板载传感**，不需特权接触状态（何时何地接触）。
- quadruped 足-地接触（相对低维），非多指 in-hand 接触（高维）。

## 3. 实验与验证
- **Go1 从零、3 分钟真机数据**学会硬地 + 记忆海绵（软地）动态步态。**因果**：刚体结构已知 → 只学外力残差 → 极少数据即准。
- **胜近期方法**（更快、更动态）。**因果**：黑箱 MBRL 数据不够、纯物理建不了软地接触；semi-structured 两全。
- 软地泛化：ensemble 外力估计适应不同地面接触。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**把动力学拆成"已知第一性原理结构（Lagrangian 刚体）+ 难建的残差（外部/接触力，用 ensemble 概率模型从历史估）"，能用极少真机数据（3 分钟）做准长程预测并学会 contact-rich 步态——结构提供样本效率，ensemble 残差吸收接触这个开放难题，且只需板载传感。** 一句话：**结构化骨架 + 学习接触力残差 + ensemble = 样本高效的 contact-rich WM。**

### 4.2 为什么有效
(1) 已知刚体结构大幅降样本复杂度；(2) ensemble 外力残差吸收难建的接触；(3) 自回归 + 学习噪声 → 概率长程预测；(4) Dyna 想象 rollout 放大数据；(5) 只用板载传感、不需特权接触状态。

### 4.3 什么时候会失效
- 结构本身错（刚体假设不成立）→ 残差补不回。
- 接触力维度极高/极复杂（多指 in-hand）→ ensemble 残差更难。
- 历史不足以推断当前接触状态。

## 5. 替代方案与局限（未来与结合）

### 5.1 理论维度
semi-structured = 物理结构 + 黑箱残差的混合模型：样本效率来自结构降维、表达力来自残差。比纯物理灵活、比纯黑箱省数据；受限于"结构主导且正确"。ensemble 给残差不确定性。

### 5.2 算法维度（WM 结构化谱系，对 WMTS 决定性）
| WM 类型 | 代表 | 结构化程度 |
|---|---|---|
| 纯显式物理孪生 | [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]] | 全结构（建不了形变） |
| **semi-structured** | **本文 SSRL** | **结构 + 残差（恰当）** |
| 黑箱（结构化训练） | [[Robotic World Model: A Neural Network Simulator|RWM]]/[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]] | 弱结构 + ensemble |
| 纯 latent | [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] | 无物理结构 |

### 5.3 工程/实验维度
结构正确性、外力维度、历史长度、Dyna rollout 长度是主要边界；多指高维接触、触觉未覆盖（但正是 WMTS 要补的输入）。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移（WM 架构蓝图）

| WMTS 模块 | SSRL 对应 | 迁移设计 |
|---|---|---|
| **WM 架构** | semi-structured（Lagrangian + ensemble 外力） | **直接采用**：WMTS WM = 已知手/笔 actuator+rigid Lagrangian + ensemble 估**多指接触力残差** |
| ensemble/不确定性 | ensemble 外力估计 | 接触力残差 ensemble → disagreement/LCB（呼应 PDDM/MoDem-V2/FOWM） |
| 触觉输入 | 历史 obs（板载） | WMTS 把**触觉 5×12×6** 作残差估计器的关键输入（SSRL 只用本体，WMTS 加触觉更强） |
| 样本效率 | 3 分钟真机 | WMTS "≤1h 真机" 很宽裕；结构让数据需求骤降 |
| imagination | Dyna 短 rollout | WMTS WM 短 rollout + PPO/model-free |

**核心论证（critical thinking）**：SSRL 是 **WMTS world model 模块的架构蓝图**——它把我贯穿多篇 recap 论证的"结构化先验 + 学习残差 + ensemble"在真机 contact-rich 系统上**证明可行且极致样本高效（3 分钟）**。WMTS 的 WM 几乎应直接照此设计：**已知手指/笔的 actuator+rigid Lagrangian 动力学（$M,B$ 由 LinkerHand 几何/惯量给定）+ 一组 ensemble 概率模型估计多指-笔接触力残差 $F^e$（条件于触觉 + 本体历史）+ 自回归多步 + Dyna 想象 rollout 配 PPO**。这一架构同时解决前面所有张力：(1) 对 [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（纯显式建不了接触/形变）——把接触交给残差；(2) 对纯神经 WM（无结构、大数据、model-exploitation）——注入刚体结构降数据、ensemble 控 exploitation；(3) 对 [[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]（delta-action 假设结构性 gap 小）——SSRL 显式把接触力建成残差通道，比 ASAP 的动作残差更贴合"结构性接触 gap"。**WMTS 的增量**：SSRL 只用本体感觉估足-地外力（低维），**WMTS 应把触觉阵列作为接触力残差估计器的一等输入**（多指接触高维，触觉直接观测接触），这正是 [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]] HC-loss 洞见（latent 不够、需结构化接触监督）的落点。**唯一需验证**：足-地接触相对低维，转笔多指接触维度高、变化快，ensemble 残差估计能否同样高效是 WMTS 的核心实验。

### 6.2 可验证实验建议
- WMTS WM 蓝图实现：LinkerHand+笔的 Lagrangian（已知 $M,B$）+ ensemble 接触力残差（触觉+本体条件）+ 自回归，测转笔长程预测样本效率（对标 3 分钟）。
- 触觉 vs 纯本体残差估计：测加触觉对接触力残差精度的提升。
- 结构化 vs 纯神经 WM：转笔上对照 semi-structured vs Dreamer-latent 的样本效率与 model-exploitation。

### 6.3 不应过度外推的点
- 足-地接触（低维）成功不能直接外推多指 in-hand（高维接触）。
- semi-structured 依赖刚体结构正确；笔接触建模需准。
- ensemble 残差在高维快变接触上的效率需实测。

## 7. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
Lagrangian 刚体动力学 $M(q)\ddot q+C\dot q+g=B\tau+F^e$；已知结构 + 未知外力的经典分解，用 ensemble 学外力。

### 与 [[ReinforcementLearning]] 的联系
Dyna 式 MBRL：真实数据 + semi-structured 模型想象短 rollout + model-free 更新；ensemble 概率预测。

### 与 [[EmbodiedAI]] 的联系
真机从零学步态、3 分钟数据、硬/软地泛化、仅板载传感——极致样本效率的具身学习。

### 与 [[Final_WMTS]] 的联系
WMTS WM 架构蓝图：actuator+rigid Lagrangian + ensemble 接触力残差（触觉条件）+ 自回归 + Dyna；解决显式/神经 WM 张力；3 分钟样本效率印证结构化的价值。

## References
- 原始 PDF：[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models.pdf]]（UT Austin/UW，CoRL 2024，arXiv 2410.09163）
- WM 结构化谱系：[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（全结构）、[[Robotic World Model: A Neural Network Simulator|RWM]]/[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]（黑箱+ensemble）、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]（latent）
- 残差对照：[[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]（动作残差）
- 触觉/接触监督呼应：[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
