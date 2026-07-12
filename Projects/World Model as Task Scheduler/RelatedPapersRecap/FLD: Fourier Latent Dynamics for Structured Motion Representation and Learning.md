---
tags:
  - paper
  - latent-dynamics
  - fourier
  - motion-representation
  - periodic-motion
  - WMTS
aliases:
  - FLD
paper-year: 2024
read-date: 2026-06-16
venue: ICLR 2024 (MIT; Chenhao Li, Sangbae Kim)
paper-pdf: "[[FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning.pdf]]"
related:
  - "[[StochasticProcess]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
  - "[[Dynamic Non-Prehensile Manipulation]]"
---

# FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning

> [!abstract] 核心贡献
> 自监督的**结构化运动表示 + 生成**方法（MIT，ICLR 2024），针对**周期/准周期运动**。核心：在**连续参数化的 latent 空间**里用**频域（Fourier）**抽取时空关系，并**强制 latent 动力学**（预测 latent 随时间演化）——这是对 Periodic Autoencoder (PAE) 的关键扩展（PAE 只静态编码、不预测；FLD 加预测结构）。运动控制器由 latent 参数化驱动，可**在线跟踪大范围运动含训练未见目标**；配 **fallback 机制**——动态调整跟踪策略、**对潜在危险目标拒绝并退到安全动作**；在 open-ended 学习里长期导航新目标、**避开 unlearnable 区域**。**对 WMTS/DNPM：转笔本质是周期/准周期运动，FLD 的 Fourier latent 可紧凑参数化转笔相位/风格并平滑插值/泛化；其 fallback（拒危险/不可学目标→安全）正是 WMTS 的 Solve/Probe/Reject + 安全过滤；作者 Chenhao Li 即 [[Robotic World Model: A Neural Network Simulator|RWM]] 作者。**

> [!tip] 与理论基础的关联
> - [[StochasticProcess]] — 频域 latent + 连续参数化；latent 动力学预测。
> - [[ControlTheory]] — 相位/频率/幅值驱动的运动控制（CPG 思想）；fallback 安全。
> - [[EmbodiedAI]] — 结构化运动表示用于 locomotion/控制；open-ended 学习。
> - [[Final_WMTS]] — **转笔周期运动的 latent 参数化 + fallback=Solve/Probe/Reject+安全**；RWM 同作者。
> - [[Dynamic Non-Prehensile Manipulation]] — 转笔=周期/准周期运动，FLD 是其运动表示候选。
>
> **核心技术**: Fourier latent dynamics (扩展 PAE), 连续参数化 latent, 频域时空结构, latent 动力学预测, 运动控制器在线跟踪, fallback 机制 (拒危险→安全), open-ended 学习

> [!note] 簇内定位（运动迁移 sim-to-real 簇）与精确锚点
> **本篇 = 周期运动的频域结构化表示 + fallback 安全筛选。** 精确 Foundation 锚点：
> - [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间]] — open-ended 学习"避开 unlearnable 区域" = 在运动 latent 空间上的自动课程。
> - [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成]] — fallback 拒"不可学目标" ≈ **认知不确定性三用之课程用**（避开学不了处）；挂该暗线。
>
> **簇内 Delta：**
> - vs [[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]]：两者都做**可行性感知的目标/技能筛选**——本篇 fallback 在**连续 Fourier 运动 latent** 上拒危险/不可学目标，ANYmal capability-aware 在**离散技能库**上选可行技能；WMTS 的 Reject 队列可两者结合（连续参数 + 离散技能）。
> - vs [[ASAP- Aligning Simulation and Real-World Physics for Learning Agile Humanoid Whole-Body Skills|ASAP]]：两者都源自 motion-tracking 谱系，但处理的轴不同——ASAP 学 **sim-real 物理残差**（动力学对齐），本篇学 **运动本身的频域结构表示**（相位/频率/幅值参数化）；WMTS 可组合：FLD 参数化转笔任务 latent、ASAP/结构化 WM 对齐物理。

## 0. 阅读定位与价值

FLD 在知识库里是**周期运动结构化表示**的代表，对 **DNPM/转笔**有独特价值——**转笔是周期/准周期运动**（笔绕指循环），而 FLD 正是为此类运动设计。它有两条对 WMTS 直击的线：(1) **Fourier latent 参数化**——把转笔的相位/频率/幅值显式参数化，比让 scheduler 从离散 token 猜周期更结构化、可插值；(2) **fallback 机制**——控制器识别危险/不可学目标并退到安全动作，正是 WMTS 的 **Reject 队列 + 安全过滤**。作者 Chenhao Li 也是 [[Robotic World Model: A Neural Network Simulator|RWM]] 作者，两篇可对读（FLD 给运动表示，RWM 给 WM）。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
参考轨迹（动捕）数据稀疏、覆盖不全；策略只会复制数据、不学底层动力学结构，导致插值/迁移差。FLD 用频域结构化 latent + latent 动力学，把周期运动的时空规律显式参数化，增强插值/泛化，并能在线跟踪未见目标、对危险目标 fallback。

### 1.2 直观隐喻
普通 latent 把运动当"一长串高维状态死记"——没覆盖的动作就不会。FLD 像"用傅里叶把运动拆成频率/相位/幅值的乐谱"——会了几支曲子就能**改调、变速、插值出新曲**（连续参数化），且乐谱本身带"接下来怎么走"（latent 动力学）。遇到弹不了的曲子（unlearnable/危险）就**退回安全的弹法**（fallback）。可证伪含义：结构化收益在"运动有**周期/相位结构**"时最大；纯非周期/突发运动 Fourier 表示不足（需 phase reset/contact token）。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| 原始轨迹模仿 | 复制动捕 | 数据稀疏、不学动力学、插值/迁移差 |
| 黑箱 latent dynamics（Dreamer 等） | 紧凑 latent | 周期结构混在高维、可控性差 |
| CPG / 解析周期控制器 | 正弦/中央模式发生器 | 需先验物理、表达受限 |
| **PAE（Periodic Autoencoder）** | 频域 latent | **静态、不预测、不充分表达整体运动** |
| **FLD** | **Fourier latent + 动力学预测 + 连续参数化 + fallback** | 非周期/突发接触表示不足；locomotion 验证 |

### 1.4 Delta 分析
精确增量（相对 PAE）：(1) **强制 latent 动力学**——latent 不只静态编码，还预测演化（PAE 缺）；(2) **连续参数化 latent**——平滑插值/泛化到未见运动；(3) **运动控制器 + fallback**——在线跟踪未见目标、拒危险目标退安全。把"静态频域编码"升级为"可预测、可插值、可安全跟踪的结构化运动动力学"。

## 2. 核心方法（原理与方法：Fourier latent + 动力学 + fallback）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源 | 性质 | 意义 | 陷阱 |
|---|---|---|---|---|---|
| 运动轨迹 | 高维状态序列 | 动捕/sim | observed | 原始运动 | 稀疏、覆盖不全 |
| Fourier latent params | 频率/相位/幅值 | 频域编码 | learned | 结构化运动参数 | 周期假设 |
| latent 动力学 | $z_{t+1}=F(z_t)$ | 预测结构 | learned | latent 演化 | 扩展 PAE 的关键 |
| 连续参数 | latent 流形 | 参数化 | computed | 插值/泛化坐标 | 平滑→非周期失效 |
| 控制器 | 策略 | latent 参数化驱动 | learned | 在线跟踪 | 含 fallback |
| fallback 判据 | 风险/可学性 | 控制器 | computed | 拒危险→安全 | =Reject/安全 |

### 2.2 核心机制（无跳步）
1. **频域结构化编码**：把运动轨迹编码到**频域 latent**（频率/相位/幅值），抓周期时空结构（承自 PAE）。
2. **latent 动力学**：强制 latent 随时间**可预测演化**（$z_{t+1}=F(z_t)$）——FLD 对 PAE 的核心扩展，使 latent 服务预测/控制而非仅重构。
3. **连续参数化**：latent 连续 → 平滑插值/泛化到未见运动。
4. **运动控制器 + fallback**：控制器由 latent 参数化驱动在线跟踪目标运动；**fallback** 动态调整跟踪、识别危险/不可学目标并退到安全动作。
5. **open-ended 学习**：配自适应目标采样，长期导航新目标、避开 unlearnable 区域。

### 2.3 概念边界与符号陷阱
- FLD latent 是**频域结构化 + 预测**，不是黑箱 latent。
- 连续参数化 → 插值；但**非周期/突发接触**（如掉笔瞬间）平滑 Fourier 表示不足 → 需 phase reset / contact event token。
- fallback = 拒危险/不可学目标（Reject + 安全）。
- locomotion（MIT Sangbae Kim）验证。

## 3. 训练、数据与实验（实验与验证）
- 运动重构、skill transfer、locomotion 在线跟踪含**未见目标**；open-ended 长期学习导航新目标、避 unlearnable。
- **频域结构消融**：去 Fourier 结构 → latent 仍能重构但**可控性、长 horizon 稳定性下降**（周期规律未参数化）。
- fallback：对危险目标退安全，提升安全跟踪。
- 边界：locomotion 周期运动；非周期突发接触表示不足。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 真正的 insight
**周期/准周期运动应在频域 latent 里结构化表示并强制 latent 动力学（可预测演化）+ 连续参数化（可插值泛化）；配 fallback 机制对危险/不可学目标退安全——如此可在线跟踪未见目标并在 open-ended 学习中避开 unlearnable 区域。** 一句话：**把周期运动拆成可预测、可插值的频域结构，并对学不了的目标安全 fallback。**

### 4.2 为什么有效
(1) 频域抓周期时空结构；(2) latent 动力学使其可预测/可控（胜 PAE 静态）；(3) 连续参数化插值泛化；(4) fallback 保安全、避 unlearnable。

### 4.3 什么时候会失效
- 非周期/突发接触切换（掉笔）→ 平滑 Fourier 不足，需 phase reset/contact token。
- 运动无周期结构 → Fourier 偏置不适用。
- locomotion→in-hand 接触的迁移需验证。

## 5. 替代方案与局限（未来与结合）
- PAE（静态频域）、黑箱 latent dynamics（Dreamer）、CPG（解析周期）。FLD 取"频域 + 预测 + 连续 + fallback"。
- 局限：非周期接触、locomotion 验证。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / DNPM 的迁移

| 模块 | FLD 对应 | 迁移设计 |
|---|---|---|
| **转笔运动表示** | Fourier latent（频率/相位/幅值） | 转笔=周期运动 → FLD latent 参数化转笔相位/风格，平滑插值不同转速/手型 |
| **scheduler 任务参数化** | 连续参数化 latent | scheduler 在连续转笔 latent 上选/生成任务（vs 离散 token） |
| **Reject + 安全** | fallback（拒危险→安全） | 对危险/不可学转笔目标 fallback 到安全动作（=Solve/Probe/Reject 的 Reject） |
| open-ended 课程 | 避 unlearnable 区域 | 与 POET/PLR 结合，导航可学转笔区 |
| WM 对读 | 同作者 RWM | FLD（运动表示）+ RWM（WM）组合 |

**核心论证（critical thinking）**：FLD 对 **DNPM/转笔**是少有的"**任务本质匹配**"论文——转笔是**周期/准周期**运动（笔绕指循环旋转），而 FLD 正为此设计。两点直接可用：(1) **用 Fourier latent 参数化转笔**——把转笔的相位、转速（频率）、幅度显式参数化，使 WMTS scheduler 在**连续运动 latent** 上选择/生成/插值转笔任务（不同转速、不同手指接力风格），远胜从离散 token 猜周期；这也给 [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]/[[Prioritized Level Replay|PLR]] 的任务生成/选择一个结构化的参数空间。(2) **fallback = WMTS 的 Reject + 安全**——FLD 控制器识别"危险/不可学目标"并退到安全动作，正是 WMTS Solve/Probe/Reject 里 **Reject 队列**的机制（呼应 [[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]] capability-aware、[[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]] 失败区、[[Curiosity-Driven Exploration via Latent Bayesian Surprise|LBS]] 避不可学）。**关键警示（draft 已点出，保留）**：转笔有**非周期/突发接触事件**（掉笔、接力切换、打滑），**平滑 Fourier 表示捕捉不了**——必须加 **phase reset / contact event token**（接触事件离散标记）补充连续频域 latent。**额外价值**：作者 Chenhao Li 也是 [[Robotic World Model: A Neural Network Simulator|RWM]] 作者，FLD（周期运动表示）+ RWM（autoregressive WM）可组合成 WMTS 的"结构化运动 latent + WM"。locomotion→in-hand 接触迁移需验证。

### 6.2 可验证实验建议
- 转笔 Fourier latent：用 FLD 风格频域 latent 参数化转笔，测插值不同转速/手型的泛化，对照离散 token。
- fallback/Reject：对危险转笔目标 fallback 安全 vs 无 fallback，测掉笔/超力率。
- phase reset + contact token：在 Fourier latent 上加接触事件标记，测非周期接触（接力/打滑）的捕捉。

### 6.3 不应过度外推的点
- 平滑 Fourier 表示不了非周期突发接触 → 需 phase reset/contact token。
- locomotion 周期运动 ≠ in-hand 高速接触（接触事件更密）。
- 需运动有周期结构（转笔成立，但接力/恢复阶段非周期）。

## 7. 与知识体系的联系

### 与 [[StochasticProcess]] 的联系
频域（Fourier）latent + 连续参数化 + latent 动力学预测——结构化随机/确定性运动表示。

### 与 [[ControlTheory]] 的联系
相位/频率/幅值驱动的运动控制（CPG 思想的学习式版本）；fallback 安全跟踪。

### 与 [[EmbodiedAI]] 的联系
结构化运动表示用于 locomotion/控制；在线跟踪未见目标 + open-ended 学习。

### 与 [[Final_WMTS]] 的联系
转笔周期运动的 Fourier latent 参数化（scheduler 任务空间）+ fallback=Reject+安全；非周期接触需 phase reset/contact token；与同作者 RWM（WM）组合。

## References
- 原始 PDF：[[FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning.pdf]]（MIT，ICLR 2024，arXiv 2402.13820）
- 基础：PAE（Periodic Autoencoder, Starke et al.）
- 同作者 WM：[[Robotic World Model: A Neural Network Simulator|RWM]]（Chenhao Li）
- 课程/Reject 呼应：[[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]、[[Prioritized Level Replay|PLR]]、[[ANYmal parkour Learning agile navigation for quadrupedal robots|ANYmal Parkour]]
- 项目入口：[[Final_WMTS]]、[[Dynamic Non-Prehensile Manipulation]]
