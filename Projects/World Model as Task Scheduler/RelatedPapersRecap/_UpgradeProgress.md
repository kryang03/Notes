# Recap 升级进度 (Gold-Standard Upgrade Progress)

> [!important] 目的与模式
> 把所有论文 recap 升级到 `Example/Rodrigues Network for Learning Robot Actions.md` 的颗粒度，按四支柱组织：**逻辑与价值 / 原理与理论 / 实验与验证 / 未来与结合**。
> 工作模式：**主线程串行，一次一篇**（不开高并发 Agent、不频繁检索）。每篇读 PDF + 旧稿 → 重写到位 → 在此翻一个勾。
> 原则源：`.github/skills/paper-recap-insight/SKILL.md` + `references/taste-rubric.md`。
> 判定标准：四支柱齐全、变量来源表 + 无跳步推导、真实实验表 + 因果解释、3 维 limitation + 具体 WMTS/灵巧手迁移、无 generic filler / 无 LaTeX 损坏。

**最后更新**: 2026-06-15 — 完成 41 篇范本级。已处理 41/47（RelatedPapers）。课程：+LBS（Bayesian surprise 抗 NoisyTV；Probe 求 epistemic 非 aleatoric）。剩余：CMA-ES、cmaes（优化工具 2）→ 表征/理论 5。
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
- [ ] The CMA Evolution Strategy: A Tutorial
- [ ] cmaes- A Simple yet Practical Python Library for CMA-ES

### Representation / Latent / Rotation / Theory
- [ ] FLD: Fourier Latent Dynamics ...
- [ ] IS ATTENTION REQUIRED FOR ICL? ...
- [ ] On the Continuity of Rotation Representations in Neural Networks
- [ ] The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook
- [ ] Transformers as Meta-Learners for Implicit Neural Representations

## B. Papers（主库，86 篇）→ PapersRecap/

待 A 部分推进后按相同顺序处理（灵巧/触觉/RL 控制优先）。逐篇在此补勾，避免一次性载入。

> [!note] 处理顺序原则
> 1. 与当前研究直接相关（灵巧手、Sim-to-Real、PPO、课程、触觉/接触、world model）。
> 2. Foundation 高频引用的基础工作。
> 3. 其余按主题聚类逐篇。
>
> Papers/ 清单见 `PapersRecap/_PapersIndex.base`；每篇完成后在本节追加 `- [x] <basename> ✅ 日期`。

（B 部分逐篇勾选区——首篇开始时填充）
