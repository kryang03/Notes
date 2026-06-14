# Recap 升级进度 (Gold-Standard Upgrade Progress)

> [!important] 目的与模式
> 把所有论文 recap 升级到 `Example/Rodrigues Network for Learning Robot Actions.md` 的颗粒度，按四支柱组织：**逻辑与价值 / 原理与理论 / 实验与验证 / 未来与结合**。
> 工作模式：**主线程串行，一次一篇**（不开高并发 Agent、不频繁检索）。每篇读 PDF + 旧稿 → 重写到位 → 在此翻一个勾。
> 原则源：`.github/skills/paper-recap-insight/SKILL.md` + `references/taste-rubric.md`。
> 判定标准：四支柱齐全、变量来源表 + 无跳步推导、真实实验表 + 因果解释、3 维 limitation + 具体 WMTS/灵巧手迁移、无 generic filler / 无 LaTeX 损坏。

**最后更新**: 2026-06-15 — 完成 Diffusion Policy、Dreamer、DayDreamer、SafeDreamer、DiWA（均范本级）。已处理 5/47（RelatedPapers）。
**读取方法**: 默认 `pdftotext -layout`（轻量、文本）；仅当抽取乱码或公式/表格不清时回退 Read 工具按页渲染。**每篇流程**: pdftotext 取正文 → Read 旧稿取 frontmatter（Write 前必须 Read）→ Write 重写。

## A. RelatedPapers（WMTS 项目，47 篇）→ RelatedPapersRecap/

优先级：World Model 核心 → 灵巧 Sim-to-Real → Diffusion/IL → 探索/课程 → 表征/理论 → locomotion/control。

### World Model / Model-Based RL
- [ ] A Step Toward World Models- A Survey on Robotic Manipulation
- [x] **DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION (Dreamer)** ✅ 2026-06-15 (范本级)
- [x] **DayDreamer- World Models for Physical Robot Learning** ✅ 2026-06-15 (范本级)
- [ ] Deep Dynamics Models for Learning Dexterous Manipulation (PDDM)
- [ ] DexSim2Real2 - Building Explicit World Model ...
- [x] **DiWA- Diffusion Policy Adaptation with World Models** ✅ 2026-06-15 (范本级)
- [ ] DyWA: Dynamics-adaptive World Action Model
- [ ] Finetuning Offline World Models in the Real World
- [ ] Learning to Model the World: A Survey of World
- [ ] MoDem-V2- Visuo-Motor World Models ...
- [ ] Model-Based Lookahead Reinforcement Learning for in-hand manipulation
- [ ] Robotic World Model: A Neural Network Simulator
- [x] **SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL** ✅ 2026-06-15 (范本级)
- [ ] STORM: Efficient Stochastic Transformer based World Models for RL
- [ ] World Models Computing the Uncomputable
- [ ] World4RL- Diffusion World Models for Policy Refinement ...

### Diffusion / Imitation / VLA
- [x] **Diffusion Policy: Visuomotor Policy** ✅ 2026-06-15 (范本级)
- [ ] Beyond Human Demonstrations- Diffusion-Based RL to Generate Data for VLA
- [ ] HG-DAgger- Interactive Imitation Learning with Human Experts

### Dexterous Manipulation / Sim-to-Real
- [ ] DEXTERITYGEN- Foundation Controller for Unprecedented Dexterity
- [ ] DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality
- [ ] DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning
- [ ] DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts
- [ ] From Simple to Complex Skills- The Case of In-Hand Object Reorientation
- [ ] Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning
- [ ] LIGHTNING GRASP ... PROCEDURAL GRASP SYNTHESIS WITH CONTACT FIELDS
- [ ] SOLVING RUBIK'S CUBE WITH A ROBOT HAND
- [ ] UniDexGrasp++- ... Geometry-aware Curriculum and Iterative GSL
- [ ] ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation
- [ ] World Models for Learning Dexterous Hand-Object Interactions from Human Videos

### Locomotion / Sim-to-Real / Control
- [ ] ANYmal parkour Learning agile navigation for quadrupedal robots
- [ ] ASAP- Aligning Simulation and Real-World Physics ...
- [ ] Learning Agile and Dynamic Motor Skills for Legged Robots
- [ ] Learning a Unified Policy for Position and Force
- [ ] Learning to Walk from Three Minutes of Real-World Data ...
- [ ] Sim-to-Real: Learning Agile Locomotion For Quadruped Robots

### Exploration / Curriculum / Optimization
- [ ] Curiosity-Driven Exploration via Latent Bayesian Surprise
- [ ] Curious Exploration via Structured World Models ...
- [ ] Improving Policy Optimization with Generalist-Specialist Learning
- [ ] Paired Open-Ended Trailblazer (POET)- ...
- [ ] Prioritized Level Replay
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
