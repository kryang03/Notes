# Recap 升级进度 (Gold-Standard Upgrade Progress)

> [!important] 目的与模式
> 把所有论文 recap 升级到 `Example/Rodrigues Network for Learning Robot Actions.md` 的颗粒度，按四支柱组织：**逻辑与价值 / 原理与理论 / 实验与验证 / 未来与结合**。
> 工作模式：**主线程串行，一次一篇**（不开高并发 Agent、不频繁检索）。每篇读 PDF + 旧稿 → 重写到位 → 在此翻一个勾。
> 原则源：`.github/skills/paper-recap-insight/SKILL.md` + `references/taste-rubric.md`。
> 判定标准：四支柱齐全、变量来源表 + 无跳步推导、真实实验表 + 因果解释、3 维 limitation + 具体 WMTS/灵巧手迁移、无 generic filler / 无 LaTeX 损坏。

**最后更新**: 2026-06-16 — **Part A 全部 48 篇达范本级**（+The Latent Space：latent 计算坐标系综述，latent-vs-结构化张力定位 WMTS）。**新增工作线**：(1) ✅ 萃取 `insight-chat-tmp.md`（ViserDex 深度对话）入 ViserDex recap——SH 函数 / K-means 簇内 DR / **EMA 动作平滑(α 随机化) ↔ [[Idea-002-Latency-Aware-Actuator]]** / belief-RNN 蒸馏；Turn 2-3 用户核心 insight → 新建 [[Rationale-Planner-Follower-Task-Definition]]；(2) ✅ 已建 [[_CrossPaperInsights]]（13 条论证线 + 🔑keystone + 跨线张力 + 速查矩阵；含 specialist→generalist、安全-cost、WM 神经主干、任务生成-课程、适应多级），并在 [[_RelatedPapersIndex]] 加导航指针。**待办**：`insight-chat-tmp.md` 内容已全萃取，可清（用户确认）；Bash 恢复后跑 `.github/scan_links.py`；Part B（PapersRecap 86 篇）未启动。
**二次审计 (2026-06-16)**: 实读细查 15/48 篇（前述 11 + STORM + Hwangbo + CMA-ES + POET，覆盖 WM/灵巧/locomotion/优化-课程 四簇、最长 338→最短 122 行），均确认范本级——行数无关，最短的 World Models Uncomputable 是"愿景随笔文体判定 + 批判隔离"的范本。[[_CrossPaperInsights]] 新增 🔑 **keystone**：一个 ensemble → Solve/Probe/Reject 三读法，统一线 1（避不确定/LCB）/线 4（求不确定/Probe）/线 11（判不确定/Reject）。又补线 12（WM 神经主干 Transformer vs RNN，STORM）+ 线 2 组件分解（命令→actuator net(Hwangbo)→力矩→Lagrangian(SSRL)→运动 + 接触力 + 增益(DexCtrl)，白箱拼装）。
**适应机制谱（WMTS LAAA 完整）**：FiLM 单向量(DyWA/DexCtrl,轻但瓶颈) / hypernetwork 全权重(Trans-INR,表达力高) / 梯度微调(FOWM,慢) / 隐式 ICL(Rubik/ICL-paper) / 控制器增益(DexCtrl) / 动力学嵌入(DyWA-RMA)。按"适应幅度×算力×速度"选。
**注**: dontAsk 模式 Write 被拒、Edit 可用 → Read 全文草稿后用两个 Edit（frontmatter + body）全文替换。PDF 抽取：Bash(pdftotext) classifier 时有不可用 → 回退 Read 工具读 PDF 页。
**WM-core 论证线**: (1) **ensemble/不确定性线**：PDDM（2019 奠基：ensemble 动力学 + mean reward）→ MoDem-V2（AC-ensemble 显式 LCB, online-from-scratch）→ FOWM（Q-ensemble LCB Eq4, offline→online 微调）+ DiWA/World4RL/RWM/Model-Based Lookahead（单 WM/无 ensemble 的反面）→ WMTS 必须 ensemble+显式 LCB。FOWM+MoDem-V2 覆盖真机两模式。(2) **结构化光谱**：DexSim2Real2（显式刚体孪生）↔ DexWM（神经 latent，"latent 不足需结构化监督"）→ WMTS 取中间。(3) **无梯度规划**：PDDM/Model-Based Lookahead/DexSim2Real2/FOWM(MPPI)。(4) **安全**：SafeDreamer(cost)+MoDem-V2(保守探索)。(5) **降维**：eigengrasp+filtering。(6) **DNPM 经典先例**：PDDM 书写/Baoding。
**读取方法**: 默认 `pdftotext -layout`（轻量、文本）；仅当抽取乱码或公式/表格不清时回退 Read 工具按页渲染。**每篇流程**: pdftotext 取正文 → Read 旧稿取 frontmatter（Write 前必须 Read）→ Write 重写。

## A. RelatedPapers（WMTS 项目，47 篇）→ RelatedPapersRecap/

优先级：World Model 核心 → 灵巧 Sim-to-Real → Diffusion/IL → 探索/课程 → 表征/理论 → locomotion/control。

### World Model / Model-Based RL
- [x] **A Step Toward World Models- A Survey on Robotic Manipulation** ✅ 2026-06-15 (范本级/导航图)
- [x] **DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION (Dreamer)** ✅ 2026-06-15 (范本级)
- [x] **DayDreamer- World Models for Physical Robot Learning** ✅ 2026-06-15 (范本级)
- [x] **Deep Dynamics Models for Learning Dexterous Manipulation (PDDM)** ✅ 2026-06-15 (范本级)
- [x] **DexSim2Real2 - Building Explicit World Model ...** ✅ 2026-06-15 (范本级)
- [x] **DiWA- Diffusion Policy Adaptation with World Models** ✅ 2026-06-15 (范本级)
- [x] **DyWA: Dynamics-adaptive World Action Model** ✅ 2026-06-15 (范本级)
- [x] **Finetuning Offline World Models in the Real World (FOWM)** ✅ 2026-06-15 (范本级)
- [x] **Learning to Model the World: A Survey of World** ✅ 2026-06-15 (范本级/导航图)
- [x] **MoDem-V2- Visuo-Motor World Models ...** ✅ 2026-06-15 (范本级)
- [x] **Model-Based Lookahead Reinforcement Learning for in-hand manipulation** ✅ 2026-06-15 (范本级)
- [x] **Robotic World Model: A Neural Network Simulator** ✅ 2026-06-15 (范本级)
- [x] **SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL** ✅ 2026-06-15 (范本级)
- [x] **STORM: Efficient Stochastic Transformer based World Models for RL** ✅ 2026-06-15 (范本级)
- [x] **World Models Computing the Uncomputable** ✅ 2026-06-15 (范本级/愿景随笔批判)
- [x] **World4RL- Diffusion World Models for Policy Refinement ...** ✅ 2026-06-15 (范本级)

### Diffusion / Imitation / VLA
- [x] **Diffusion Policy: Visuomotor Policy** ✅ 2026-06-15 (范本级)
- [x] **Beyond Human Demonstrations- Diffusion-Based RL to Generate Data for VLA** ✅ 2026-06-15 (范本级)
- [x] **HG-DAgger- Interactive Imitation Learning with Human Experts** ✅ 2026-06-15 (范本级)

### Dexterous Manipulation / Sim-to-Real
- [x] **DEXTERITYGEN- Foundation Controller for Unprecedented Dexterity** ✅ 2026-06-15 (范本级)
- [x] **DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality** ✅ 2026-06-15 (范本级)
- [x] **DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning** ✅ 2026-06-15 (范本级)
- [x] **DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts** ✅ 2026-06-15 (范本级)
- [x] **From Simple to Complex Skills- The Case of In-Hand Object Reorientation** ✅ 2026-06-15 (范本级)
- [x] **Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning** ✅ 2026-06-15 (范本级)
- [x] **LIGHTNING GRASP ... PROCEDURAL GRASP SYNTHESIS WITH CONTACT FIELDS** ✅ 2026-06-15 (范本级)
- [x] **SOLVING RUBIK'S CUBE WITH A ROBOT HAND** ✅ 2026-06-15 (范本级)
- [x] **UniDexGrasp++- ... Geometry-aware Curriculum and Iterative GSL** ✅ 2026-06-15 (范本级)
- [x] **ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation** ✅ 2026-06-15 (范本级)
- [x] **World Models for Learning Dexterous Hand-Object Interactions from Human Videos (DexWM)** ✅ 2026-06-15 (范本级)

### Locomotion / Sim-to-Real / Control
- [x] **ANYmal parkour Learning agile navigation for quadrupedal robots** ✅ 2026-06-15 (范本级)
- [x] **ASAP- Aligning Simulation and Real-World Physics ...** ✅ 2026-06-15 (范本级)
- [x] **Learning Agile and Dynamic Motor Skills for Legged Robots** ✅ 2026-06-15 (范本级)
- [x] **Learning a Unified Policy for Position and Force** ✅ 2026-06-15 (范本级)
- [x] **Learning to Walk from Three Minutes of Real-World Data ...** ✅ 2026-06-15 (范本级/WM 架构蓝图)
- [x] **Sim-to-Real: Learning Agile Locomotion For Quadruped Robots** ✅ 2026-06-15 (范本级)

### Exploration / Curriculum / Optimization
- [x] **Curiosity-Driven Exploration via Latent Bayesian Surprise** ✅ 2026-06-15 (范本级)
- [x] **Curious Exploration via Structured World Models ...** ✅ 2026-06-15 (范本级)
- [x] **Improving Policy Optimization with Generalist-Specialist Learning** ✅ 2026-06-15 (范本级)
- [x] **Paired Open-Ended Trailblazer (POET)- ...** ✅ 2026-06-15 (范本级)
- [x] **Prioritized Level Replay** ✅ 2026-06-15 (范本级)
- [x] **The CMA Evolution Strategy: A Tutorial** ✅ 2026-06-16 (范本级)
- [x] **cmaes- A Simple yet Practical Python Library for CMA-ES** ✅ 2026-06-16 (范本级)

### Representation / Latent / Rotation / Theory
- [x] **FLD: Fourier Latent Dynamics ...** ✅ 2026-06-16 (范本级)
- [x] **IS ATTENTION REQUIRED FOR ICL? ...** ✅ 2026-06-16 (范本级)
- [x] **On the Continuity of Rotation Representations in Neural Networks** ✅ 2026-06-16 (范本级)
- [x] **The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook** ✅ 2026-06-16 (范本级/latent 计算坐标系综述；latent-vs-结构化张力)
- [x] **Transformers as Meta-Learners for Implicit Neural Representations** ✅ 2026-06-16 (范本级)

## B. Papers（主库，86 篇）→ PapersRecap/

待 A 部分推进后按相同顺序处理（灵巧/触觉/RL 控制优先）。逐篇在此补勾，避免一次性载入。

> [!note] 处理顺序原则
> 1. 与当前研究直接相关（灵巧手、Sim-to-Real、PPO、课程、触觉/接触、world model）。
> 2. Foundation 高频引用的基础工作。
> 3. 其余按主题聚类逐篇。
>
> Papers/ 清单见 `PapersRecap/_PapersIndex.base`；每篇完成后在本节追加 `- [x] <basename> ✅ 日期`。

（B 部分逐篇勾选区——首篇开始时填充）
