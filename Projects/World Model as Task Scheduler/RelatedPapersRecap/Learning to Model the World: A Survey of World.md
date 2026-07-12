---
tags:
  - paper
  - world-model
  - survey
  - taxonomy
  - evaluation
  - WMTS
aliases:
  - World Model Survey
  - Learning to Model the World
paper-year: 2026
read-date: 2026-06-15
venue: TechRxiv 2026 (survey, MBZUAI/CAS 等)
paper-pdf: "[[Learning to Model the World: A Survey of World.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# Learning to Model the World: A Survey of World Models in AI

> [!abstract] 核心贡献
> 一篇**跨全 AI 领域**的 world model 大综述（机器人、自动驾驶、科学发现、游戏仿真、GUI agent、可解释性/可信性）。与 [[A Step Toward World Models- A Survey on Robotic Manipulation|操作领域综述]]（能力导向、三范式、限于 manipulation）互补，它的差异化在三点：(1) **带形式化数学公式的四分支分类**——observation-level generative / latent space / RL-based / object-centric；(2) **系统的 benchmark / 评测指标 / 仿真平台 / 横评**（操作综述缺的"评测"维度）；(3) **跨域视角**——把驾驶/游戏/科学的 WM 技术拉进同一框架。**对 WMTS 它补两样操作综述没给的：一套可借的 WM 评测指标/基准（衡量长程一致性、泛化、可信性），与"object-centric WM"这一显式分支（DyWA 一类的归属）。**

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — WM 作为连接感知-认知-控制的通用智能系统。
> - [[ReinforcementLearning]] — 四分支之一 RL-based WM（Dreamer 系）。
> - [[StochasticProcess]] — latent space / observation-level generative 分支（生成式/隐变量）。
> - [[WorldModels]] — 四分支（observation-generative / latent / RL-based / object-centric）与本库 [[WorldModels]] 六层互补：RL-based↔[[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]]，其评测/可信性维度补足 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]] 的度量端。
> - [[Final_WMTS]] — **WMTS 的评测与跨域参照**：四分支定位 + benchmark/metric 选型 + object-centric 分支归属。
>
> **核心框架**: 四分支形式化分类 (observation-generative / latent / RL-based / object-centric), benchmark+metric+仿真平台横评, 跨域应用, 可信性/可解释性, 挑战 (长程一致性/泛化)

## 0. 阅读定位与范本价值

这是 RelatedPapers 里**第二张地图**，且与 [[A Step Toward World Models- A Survey on Robotic Manipulation|第一张（操作领域）]]**刻意互补**——所以本 recap **不重复 landscape**，只补第一篇没给的三件事：**形式化四分支**、**评测体系**、**跨域视角**。读它的价值是：(1) 用带公式的四分支给库内论文一个更"数学"的归类；(2) 拿它的 benchmark/metric 给 WMTS 选评测标准；(3) 从驾驶/游戏/科学 WM 里借可迁移技术。

> [!note] 综述类 recap 适配（同第一篇）
> 无单一方法，故"原理与理论"→形式化分类框架（§2），"实验与验证"→评测体系（§3）。与 [[A Step Toward World Models- A Survey on Robotic Manipulation|操作综述]] 交叉引用，避免重复。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
WM 研究碎片化（范式/领域/评测各异）。本综述系统梳理全 AI 的 WM，**用形式化四分支统一**，并补齐**评测（benchmark/metric/平台）**与**跨域应用**，做成一个可比较、可推进的统一参照（含持续更新的 GitHub）。

### 1.2 与第一篇综述的分工（关键）
| 维度 | [[A Step Toward World Models- A Survey on Robotic Manipulation|操作综述]] | **本篇（全 AI）** |
|---|---|---|
| 范围 | 仅 robotic manipulation | 全 AI（机器人+驾驶+科学+游戏+GUI） |
| 分类 | 能力导向，三范式 | **形式化四分支（带公式）** |
| 评测 | 弱（无横评） | **强（benchmark/metric/平台/横评）** |
| 对 WMTS | 定位坐标 + 七挑战自检 | **评测选型 + object-centric 归属 + 跨域借鉴** |

### 1.3 Delta（综述自身增量）
相对前序 WM 综述：(1) 跨更广领域；(2) **形式化四分支公式**；(3) 系统 benchmark/metric/仿真平台 + 横评；(4) 含可信性/可解释性。

## 2. 形式化四分支分类与库内归位（原理与理论 → 分类框架）

| 分支 | 形式化要点 | 库内归位 |
|---|---|---|
| **Observation-level Generative** | 直接预测未来观测 $o_{t+1}=f(o_{\le t},a_t)$（像素/视频） | [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]（像素扩散）；DexWM 的 NWM/PEVA 对照 |
| **Latent Space** | 编码到 latent、在 latent 预测（高效、抽象） | [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]、[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]、[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]、[[Robotic World Model: A Neural Network Simulator|RWM]]、TD-MPC([[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]/[[Finetuning Offline World Models in the Real World|FOWM]]) |
| **RL-based** | WM 服务 RL 训练/规划 | [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[DayDreamer- World Models for Physical Robot Learning|DayDreamer]]、[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]、[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]] |
| **Object-centric** | 用对象级嵌入表示环境，跨场景/任务推理泛化 | [[DyWA: Dynamics-adaptive World Action Model|DyWA]]（动力学+物体中心倾向）；操作任务天然 object-centric |

**WMTS 的归位**：主体在 **Latent Space + RL-based** 交叉（latent 动力学 + 服务 PPO/调度），并向 **object-centric**（物体/接触中心）与显式物理倾斜——是四分支的**混合体**。

### 2.1 概念边界与符号陷阱
- 四分支**非互斥**：World4RL 既 observation-generative 又服务 RL；Dreamer 既 latent 又 RL-based。分类是主轴非硬墙。
- object-centric 是本综述**显式独立的一支**（第一篇未单列）——对操作（物体为中心）尤其相关。
- 形式化公式给统一记号，但不同分支的 $f$、latent、reward 语义不同（呼应我各 recap 的"WM 多义项"）。

## 3. 评测体系与领域横评（实验与验证 → 评测体系）

这是本综述对 WMTS **最独特的贡献**——第一篇缺的评测维度：
- **Benchmark**：预训练视频基准 + 下游任务基准（§4.1.1-2）。
- **评测指标**：为 WM 设计的通用指标，衡量**泛化、因果推理、长程一致性**（§4.1.3）；预测保真（FVD/FID/LPIPS，见 [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] Table I）+ 下游任务成功率。
- **仿真平台/物理引擎**（§4.2）：IsaacGym/Isaac Lab 等（库内 DyWA/Model-Based Lookahead/RWM 用）。
- **横评**（§4.3）：跨 WM 比较结果。
- **挑战**：长程一致性、泛化（贯穿库内 STORM/RWM 的 autoregressive 误差累积主题）。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 综述真正的 insight
**把碎片化的 WM 研究用形式化四分支（observation-generative / latent / RL-based / object-centric）统一，并补齐评测体系与跨域视角，使 WM 可比较、可推进。** object-centric 被提为独立一支，评测被系统化——这是它相对能力导向综述的方法论增量。

### 4.2 为什么这张地图有用（对 WMTS）
(1) 形式化四分支给库内论文更精确归类；(2) 评测体系让 WMTS 有**可借的指标/基准**（长程一致性、泛化、保真度）；(3) 跨域（驾驶/游戏/科学 WM）提供可迁移技术池；(4) object-centric 分支提示 WMTS 的物体/接触中心表示有独立方法论支撑。

### 4.3 综述的局限
- 跨域广但每域浅；灵巧高速接触不是重点。
- 四分支重叠、边界软。
- TechRxiv 预印本、非同行评审、持续更新中。

## 5. 替代视角与局限（未来与结合）
- 与 [[A Step Toward World Models- A Survey on Robotic Manipulation|操作综述]] 配对使用：本篇给评测+四分支+跨域，操作综述给操作专属能力+七挑战。
- 具体机制仍回单篇（PDDM/MoDem-V2/FOWM 的 ensemble-LCB；DexWM HC-loss；DexSim2Real2 显式物理）。
- 评测指标需针对灵巧接触定制（综述的通用指标不够细）。

## 6. 对用户研究的启发（未来与结合：WMTS 评测与归类）

### 6.1 对 WMTS 的迁移

| WMTS 需求 | 本综述提供 | 用法 |
|---|---|---|
| **WM 评测标准** | benchmark/metric/平台/横评 | 选长程一致性 + 泛化 + 保真度 + 下游成功率作 WMTS WM 评测；用 IsaacGym 平台 |
| **文献归类** | 形式化四分支 | WMTS = Latent+RL-based+object-centric 混合，写进定位图 |
| object-centric | 独立分支 | WMTS 物体/接触中心表示有方法论支撑 |
| 跨域借鉴 | 驾驶/游戏 WM | 借自动驾驶 WM 的长程一致性、游戏 WM 的交互生成技术 |
| 可信性 | §3.6 | WMTS reliability head 对应"可信 WM"主题 |

**核心论证（critical thinking）**：两篇综述对 WMTS 是**互补的双地图**。第一篇（操作）给 WMTS 的是**定位 + 设计自检（七挑战）**；本篇（全 AI）给 WMTS 的是**评测 + 归类 + 跨域**——这恰是 WMTS 写论文时"如何衡量我的 WM 好不好"的答案来源：用综述的通用指标（长程一致性、泛化、保真度）+ 下游任务成功率 + 我自定的灵巧接触指标（触觉预测误差、掉笔率）。其次，本篇把 **object-centric WM 列为独立分支**，给 WMTS/DyWA 一类"物体/接触中心"表示提供方法论靠山——WMTS 的接触中心结构化 WM 不是孤例。**但务必注意**：两篇综述都**广而不深**，且都不深入灵巧高速接触；WMTS 的核心创新（结构化物理 + 触觉 + ensemble-LCB 调度）在综述里只是"未来方向/挑战"，**没有现成方案**——这既是机会也是风险，WMTS 必须原创而非综述里抄。

### 6.2 可行动项
- 建 WMTS 评测套件：长程一致性 + 泛化 + 保真度（综述指标）+ 灵巧专属（触觉预测误差、掉笔率、model-exploitation gap）。
- 用四分支 + 第一篇三范式做 WMTS 双轴定位图。
- 扫描综述的驾驶/游戏 WM，挑长程一致性技术试用于转笔 WM。

### 6.3 不应过度依赖的点
- 综述广而浅；灵巧接触无现成方案，需原创。
- 通用评测指标不足以衡量灵巧接触，需定制。

## 7. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
WM 作为连接感知-认知-控制的通用智能系统，跨机器人/驾驶/游戏等具身与交互域。

### 与 [[ReinforcementLearning]] 的联系
四分支之一 RL-based WM（Dreamer 系）；WM 提样本效率、补 model-free 泛化弱。

### 与 [[StochasticProcess]] 的联系
observation-level generative（视频扩散）与 latent space 分支是生成式/隐变量序列模型。

### 与 [[WorldModels]] 的联系
本篇的**形式化四分支**给本库 [[WorldModels]] 大厦一个更"数学"的外部归类：latent space↔[[WorldModels#2. 预测层：在 latent 里推演未来]]，RL-based↔[[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"]]。它独有的**评测体系**（长程一致性/泛化/保真度指标）填补了 [[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"]] 缺的度量端——WMTS 衡量自己 WM 好坏时可直接借这些指标 + 灵巧定制项（触觉预测误差、掉笔率）。与 [[A Step Toward World Models- A Survey on Robotic Manipulation|操作综述]] 构成 WMTS 双地图。

### 与 [[Final_WMTS]] 的联系
WMTS 的评测选型（长程一致性/泛化/保真度 + 灵巧定制）+ 四分支归类（Latent+RL-based+object-centric 混合）+ 跨域借鉴；与操作综述构成 WMTS 双地图。

## References
- 原始 PDF：[[Learning to Model the World: A Survey of World.pdf]]（TechRxiv 2026，MBZUAI/CAS 等）
- 互补综述：[[A Step Toward World Models- A Survey on Robotic Manipulation|A Step Toward World Models（操作领域）]]
- 被归位的库内 WM 论文：见 §2 表（四分支）
- 项目入口：[[Final_WMTS]]
