---
tags:
  - paper
  - curriculum-learning
  - reinforcement-learning
  - level-replay
  - task-scheduling
  - WMTS
aliases:
  - PLR
paper-year: 2021
read-date: 2026-06-15
venue: ICML 2021 (FAIR / UCL; Minqi Jiang, Rocktäschel)
paper-pdf: "[[Prioritized Level Replay.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# Prioritized Level Replay (PLR)

> [!abstract] 核心贡献
> 在程序生成内容（PCG）环境里，**按"学习潜力"选择下一个训练 level（任务实例）**——而非均匀采样。关键：**TD-error 有效估计一个 level 未来的学习潜力**，用它加权采样，**自发涌现"由易到难"的课程**。在 Procgen 上显著提升样本效率与泛化（结合此前最优方法，测试回报较基线提升 76%+）。**对 WMTS：这是最直接的 "task scheduler" 先例——scheduler 按学习潜力（TD-error/regret）选下一个训练任务，自发课程化；正是 "World Model as Task Scheduler" 的调度准则，且与 Solve/Probe/Reject 三队列契合（优先调度高学习潜力的 Probe 任务）。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — TD-error 作学习潜力信号；课程 RL；PCG 泛化。
> - [[Optimization]] — 按 score（学习潜力 + staleness）的选择性采样（active learning 式）。
> - [[Final_WMTS]] — **task scheduler 调度准则**（学习潜力选任务、涌现课程）；契合 Solve/Probe/Reject。
> - [[Dynamic Non-Prehensile Manipulation]] — 转笔配置 = PCG level；按学习潜力调度配置。
>
> **核心技术**: 学习潜力（TD-error）打分, staleness 加权, 选择性 level 采样, 涌现课程, PCG 泛化, Procgen

## 0. 阅读定位与范本价值

PLR 是知识库里 **最直接的 "task scheduler" 先例**。库内其它"scheduler"是**空间上**选技能（[[From Simple to Complex Skills- The Case of In-Hand Object Reorientation|From-Simple]]/[[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts|DexReMoE]]/[[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]]），而 PLR 是**训练时间上**选任务（哪个 level 现在最值得练）——这正是 WMTS "World Model as Task **Scheduler**" 的字面含义：一个调度器决定训练流里下一个练什么任务。读它要抓**调度准则**：TD-error = 学习潜力，高潜力优先 → 涌现课程。它与 [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]（共演化任务）、curiosity 探索、[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|ADR]]（自动课程）同属课程/探索基。

## 1. 问题设定与价值（逻辑与价值）

### 1.1 一句话核心
PCG 环境每个 level 是一个任务实例（factors of variation 的配置）；能从一个 level 学到多少**取决于当前策略**，但既往默认均匀采样。PLR：**按 level 的学习潜力（TD-error 估计）选择性采样**，自发涌现由易到难课程，提升样本效率与泛化。

### 1.2 直观隐喻
均匀采样像"不管学生水平，所有题随机出"——简单题做腻、难题做不动，效率低。PLR 像"自适应出题系统"：估计每道题"现在做最能涨分"（学习潜力 = TD-error），优先出这些 → 自动从易到难。可证伪含义：学习潜力调度的收益在"**任务多样且共享结构、不同任务对当前策略价值不同**"时最大；任务同质则均匀采样即可。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 均匀 level 采样 | 无偏覆盖 | 不管学习价值、效率低 |
| 改架构/算法/观测 | 各自 | 仍均匀采样 level |
| 控制生成过程的课程 | 强假设（控制生成） | 需控制生成器 |
| **PLR** | **TD-error 学习潜力 + staleness 选择采样** | 假设 level 共享 latent dynamics；PCG 游戏（非真机） |

### 1.4 Delta 分析
精确增量：(1) **TD-error 作 level 未来学习潜力的有效估计**；(2) 用其 + staleness（防陈旧）**加权选择采样**下一 level；(3) 证明这**自发涌现难度课程**、提泛化。把"均匀采样"换成"学习潜力驱动的自适应课程"，且**只需 blackbox 生成器**（不需控制生成过程）。

## 2. 核心方法（原理与方法：学习潜力打分 + 采样）

### 2.1 核心机制（无跳步）
- **学习潜力打分**：用每个 level 上的 **TD-error**（绝对值/GAE 幅度）估计该 level 未来重访的学习潜力——TD-error 大 = 策略在此还有很多没学好 = 高潜力。
- **staleness 加权**：久未采的 level 加权（防分数陈旧、保覆盖）。
- **选择性采样**：下一 level 按"学习潜力 + staleness"混合分布采样（或从未见 level 采）。
- **涌现课程**：随策略进步，高 TD-error 的 level 从简单转向更难 → 自发由易到难。

### 2.2 概念边界与符号陷阱
- TD-error = 学习潜力代理（非难度本身；难度太高 TD-error 也可能低如果学不动）。
- staleness 防止只刷少数高分 level。
- 只需 blackbox 生成器（给 id 返 level），不控制生成。
- PCG 游戏 level；任务实例的时间调度。

## 3. 实验与验证
- **Procgen**：显著提样本效率 + 泛化；结合此前最优，测试回报较基线 **+76%**。**因果**：学习潜力调度把训练算力投在最有价值的 level → 涌现课程 → 更好泛化。
- 可与其它方法组合。
- 边界：PCG 游戏；假设 level 共享 latent dynamics。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**能从一个任务实例学到多少取决于当前策略；用 TD-error 估计每个实例的"学习潜力"并优先采样高潜力实例，会自发涌现由易到难的课程，大幅提升样本效率与泛化——无需控制任务生成过程。** 一句话：**按学习潜力调度任务，自动课程化。**

### 4.2 为什么有效
(1) TD-error 准估学习潜力；(2) 优先高潜力 → 算力投在最有价值处；(3) staleness 保覆盖；(4) 随策略进步自发课程化。

### 4.3 什么时候会失效
- 任务同质 → 均匀即可。
- TD-error 不反映潜力（如不可学的任务 TD-error 也高 → 浪费；需配可行性判断）。
- 任务不共享结构 → 课程无迁移。

## 5. 替代方案与局限（未来与结合）
- 课程/探索族：[[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]（共演化任务+智能体）、[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|ADR]]（自动扩随机化）、curiosity 探索。
- PLR 是 level-replay 式（选已有 level）；POET 生成新任务。
- 局限：PCG 游戏、TD-error 代理、需共享结构。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| WMTS 模块 | PLR 对应 | 迁移设计 |
|---|---|---|
| **Task Scheduler（时间调度）** | 学习潜力（TD-error）选 level | WMTS scheduler 按学习潜力（TD-error/regret/WM 不确定）选下一个转笔配置训练 |
| 涌现课程 | 由易到难 | scheduler 自发从易转笔配置到难 |
| Solve/Probe/Reject | 高潜力优先 | **Probe 队列 = 高学习潜力任务**；但需配可行性（Reject 不可学的） |
| 任务表示 | level id/config | 转笔配置（笔参/初始姿态/目标相位） |

**核心论证（critical thinking）**：PLR 是 WMTS "task scheduler" 的**最直接调度准则来源**。WMTS 的核心是"用 WM 当 task scheduler"——而调度的关键问题是"**下一个该练哪个任务**"，PLR 给出答案：**按学习潜力（TD-error）优先**，并证明这自发涌现课程、提泛化。WMTS 的 scheduler 应把这个准则**升级**：(1) 学习潜力信号除 TD-error 外，可用 **WM 预测的 regret / ensemble disagreement**（WM 在哪不确定 = 哪有学习潜力）；(2) **配可行性判断**——PLR 的盲点是"TD-error 高但不可学"的任务会被浪费（转笔的极难配置可能 TD-error 高却学不动），WMTS 的 **Solve/Probe/Reject** 正好补上：高潜力且可行→Probe，高潜力但不可行→Reject（呼应 [[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]] 的 capability-aware、[[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]] 的失败区预测）。所以 **WMTS scheduler = PLR 学习潜力调度 + 能力/可行性过滤 + WM 不确定性信号**。**边界**：PLR 是 PCG 游戏 level，转笔配置的"学习潜力"需在接触动力学下重新定义；且 PLR 假设 level 共享 latent dynamics（转笔配置确实共享手-笔动力学，成立）。

### 6.2 可验证实验建议
- WMTS scheduler 用 PLR 准则：按 TD-error/WM-regret 选转笔配置训练，对照均匀采样，测样本效率 + 涌现课程。
- 学习潜力信号对比：TD-error vs WM ensemble disagreement vs regret 哪个更准。
- Solve/Probe/Reject：学习潜力 + 可行性双信号划三队列，测是否避开"高 TD-error 但不可学"的浪费。

### 6.3 不应过度外推的点
- PCG 游戏 level ≠ 转笔接触配置；学习潜力需重定义。
- TD-error 高 ≠ 可学；需可行性过滤（WMTS Reject）。
- 假设共享结构（转笔成立）。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
TD-error 作学习潜力信号；课程 RL；PCG 泛化（过拟合训练经验的对策）。

### 与 [[Optimization]] 的联系
按 score（学习潜力 + staleness）的选择性采样，是 active learning 式的任务选择优化。

### 与 [[Final_WMTS]] 的联系
WMTS task scheduler 的调度准则（学习潜力选任务、涌现课程）；WMTS 升级为 WM-regret/ensemble 信号 + Solve/Probe/Reject 可行性过滤。

## References
- 原始 PDF：[[Prioritized Level Replay.pdf]]（FAIR/UCL，ICML 2021，arXiv 2010.03934）
- 课程/探索族：[[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]、[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|ADR]]
- 可行性/能力：[[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]]、[[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
