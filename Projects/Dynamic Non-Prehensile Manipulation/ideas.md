---
tags:
  - project
  - non-prehensile
  - dynamic-manipulation
  - research-roadmap
aliases:
  - DNPM Research Roadmap
  - 动态非紧握研究路线图
created: 2026-01-31
updated: 2026-02-07
status: active
related:
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
  - "[[SignalProcessing]]"
  - "[[InformationTheory]]"
---

# Dynamic Non-Prehensile Manipulation: Research Roadmap

> [!abstract] 本文件定位
> 本文件是整个 DNPM 研究的**顶层思想文档**，组织为三个递进的研究方向：
> 1. **Big Picture** — 定义任务类别、阐明意义与动力学本质困难
> 2. **HDC 算法** — 当前通过缩放物理演化速度优化 Value Landscape 的具体工作
> 3. **未来突破方向** — 可独立成文的若干研究切入点
>
> 技术细节文档见 [[Dynamic Non-Prehensile Manipulation]]；会议纪要见 `HDC-元宝纪要.txt`；汇报材料见 `RSS26.pdf`。

---

## 一、Big Picture：动态非紧握操作的任务定义、意义与本质困难

### 1.1 从动力学角度对灵巧操作的分类

灵巧操作任务可以沿两个正交维度进行分类，形成一个 $2 \times 2$ 的矩阵：

|  | **Force Closure（力闭合）** | **Non-Prehensile（非紧握）** |
|---|---|---|
| **Quasi-Static（准静态）** | 夹持搬运、螺丝拧紧 | 缓慢推动、手内缓慢重定向 |
| **Dynamic（动态）** | 英伟达快速转笔（力闭合下的高速重定向） | **This Work：Thumbaround、颠锅、陀螺** |

这两个维度的物理含义如下：

**维度一：Force Closure vs. Non-Prehensile — 自由度的可控性**

在力闭合状态下，末端执行器对物体的所有自由度都具有完全的控制能力。系统可以在任意时刻对物体施加任意方向的力和力矩（受限于摩擦锥约束, 详见 [[ContactMechanics]]）。这意味着系统始终能够产生一个用于抵消重力的分力 $F_1$ 和一个用于控制目标轨迹的分力 $F_2$：

$$F = F_1 + F_2, \quad F_1 = g(q)$$

而在非紧握状态下，系统**无法直接控制物体的全部自由度**。例如，在 Thumbaround 动作中，笔绕拇指背侧旋转时，仅靠拇指背侧的单边接触维持，缺乏持续的力闭合约束。系统不能在任意时刻产生任意方向的力——特别是，**不总能产生用于抵消重力的分力**。

**维度二：Quasi-Static vs. Dynamic — 惯性项的显著性**

准静态范式假定加速度近似为零 $\ddot{q} \approx 0$，因此动力学方程退化为静力学平衡：

$$g(q) = F$$

系统只需学习如何在当前构型下平衡重力即可。惯性项 $M(q)\ddot{q} + C(q, \dot{q})\dot{q}$ 被视为扰动或直接忽略。

而在动态范式下，完整的 Euler-Lagrange 方程不可简化（详见 [[Dynamics]]）：

$$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau$$

惯性项不可忽视，科里奥利力和离心力项（详见 [[Dynamics#2.2 Coriolis & Centrifugal Forces (科里奥利力与离心力)]]）成为系统行为的主导因素。

**本研究的定位：Dynamic $\times$ Non-Prehensile**

当这两个维度叠加时——系统既不能完全控制物体的自由度，又处于惯性项不可忽视的高速运动状态——任务的动力学复杂度发生了质变。这正是本研究所定义和聚焦的任务类别。

### 1.2 任务的现实意义：不是为了难而生造

动态非紧握操作不是为了追求学术上的高难度而人为构造的任务。它具有极高的现实生活意义，体现在两个层面：

#### 1.2.1 Action Acceleration — 加速已有任务的执行

对于机器人已经能够在准静态框架下完成的任务，引入动态非紧握操作能够显著提高执行速度：

- **拧瓶盖**：当前机器人拧瓶盖的速度远低于人类（参见 [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]]）。若系统能在非完全力闭合的状态下利用惯性力辅助旋转，可大幅提升拧瓶盖的速度。
- **托盘搬运（Tray Balancing and Transportation）**：像服务生一样把物体放在托盘上快速搬运。通过微微倾斜托盘，基于达朗贝尔原理（D'Alembert's Principle）产生表观加速度 $\mathbf{g}_{eff} = \mathbf{g} - \mathbf{a}$，使物品不倾倒的同时提高传输速度。这需要一个先加速后减速的过程，过程中物品处于非紧握状态，完全依靠惯性力和摩擦力维持平衡。

#### 1.2.2 Task Space Broadening — 解锁全新的任务空间

更重要的是，动态非紧握操作拓展的不仅是动作空间（action space），而是**任务空间（task space）**——系统一旦具备了这样的能力，能解锁一整类在准静态框架下根本不可能完成的任务：

- **颠锅（Wok Tossing）**：锅与锅内食物（如煎蛋）之间是非紧握关系——锅在此任务中近似等价于末端执行器。如果不主动注入速度和加速度让食物进入高惯性状态（飞行相），食物就**无法实现翻转**——这在准静态框架下逻辑上不可能实现，因为锅只能从下方支撑食物，缺乏翻转食物所需的对称力。
- **旋转陀螺（Top Spinning）**：一个更极端的例子。在旋转的过程中，陀螺不仅仅是非紧握——它**根本不受末端执行器的控制**。在这样的状态下，必须在之前的阶段就给陀螺注入一个高惯性状态，利用转动惯量实现陀螺的动态平衡（进动与章动, 详见 [[Dynamics#2.2 Coriolis & Centrifugal Forces (科里奥利力与离心力)]]）。
- **Thumbaround 和 Triangle Pass**：花式转笔动作。在笔绕拇指旋转的 Spin 阶段，笔与手指的接触是单边的、非力闭合的。系统必须先给笔注入足够的角动量，使笔能够利用惯性力产生接触力、再通过接触力产生摩擦力来对抗重力，同时完成预期的旋转轨迹。

> [!note] 意义分类对照
> | 任务 | Action Acceleration | Task Space Broadening |
> |------|:---:|:---:|
> | 拧瓶盖 | ✅ | |
> | 托盘搬运 | ✅ | |
> | 颠锅 | | ✅ |
> | 旋转陀螺 | | ✅ |
> | Thumbaround / Triangle Pass | | ✅ |

### 1.3 动力学本质困难：长因果链与不可归因的高惯性状态

动态非紧握操作的本质困难来自于**自由度不完全可控的高惯性状态在动力学角度自带的高复杂度**。

#### 1.3.1 动力学因果长链条

以 Thumbaround 动作为例（详见 RSS26.pdf 第4页）。在笔绕拇指旋转的阶段：

1. **拇指的支持力不足以抗衡重力**：由于非紧握状态下接触点的几何限制，拇指背侧的法向力方向无法直接提供竖直向上的分量来平衡重力。
2. **系统必须利用惯性力**：高速旋转产生的离心力将笔压向拇指侧，产生法向接触力。
3. **接触力再产生摩擦力**：这个法向接触力通过摩擦（[[ContactMechanics#3. 接触建模演变：从点模型到软体模型|接触建模演变]]）产生一个切向摩擦力分量。
4. **摩擦力对抗重力**：正是这个摩擦力分量最终平衡了重力，使笔不坠落。

因此，系统需要学习的动力学因果链条是：

$$\boxed{\text{主动发力} \rightarrow \text{高惯性状态} \rightarrow \text{广义惯性力} \rightarrow \text{惯性力作用于环境产生接触力} \rightarrow \text{接触力产生摩擦力} \rightarrow \text{对抗重力并完成演化}}$$

这条链条的每一步都涉及非线性动力学耦合，而最终的"对抗重力"效果距离最初的"主动发力"决策隔了多个物理中间步骤。这使得**因果链极长、归因极难**。

#### 1.3.2 高惯性状态的不可归因性

由于因果链条长且高度非线性，一个核心困难随之浮现：**很难用一个通用的（非 task-specific 的）标准来评判怎样的高惯性状态是"好的"、怎样的是"坏的"。**

- 对于 **model-based 方法**：动力学方程的高非线性使得多步前向预测误差呈指数级增长，尤其在接触切换点。即使精确地知道所有物理参数，多步链式因果关系的解析表达也是 intractable 的（详见 [[Dynamics#5. Contact Dynamics: 灵巧操作的深水区 (The Deep Waters of Contact)]]中关于 LCP 求解的讨论）。
- 对于 **learning-based 方法**：强化学习需要通过试错来发现好的策略。但当因果链条长到一定程度后，credit assignment（信用分配）变得极其困难——系统在 $t_0$ 时刻发力的"好坏"可能要在 $t_0 + \Delta t$ 之后才能通过最终的成功/失败来判断，而中间经过的所有高惯性状态都是混淆因素（详见 [[ReinforcementLearning#2.8 Exploration 理论：从信息论到技能发现]]）。

#### 1.3.3 对各任务的动力学难度解析

| 任务 | 长因果链条 | 高惯性状态的危险性 | 不可归因性 |
|------|:---:|:---:|:---:|
| **Thumbaround** | ✅ 发力→离心力→接触力→摩擦力→抗重力 | ✅ 力度不当笔飞出 | ✅ snap力度→旋转质量→最终稳定 |
| **Triangle Pass** | ✅ 发力→高角速度→换指窗口→新接触建立 | ✅ 连续旋转中任一时刻失控即失败 | ✅ 连续成功难定义 |
| **颠锅** | ✅ 锅运动→食物抛出→飞行相→接住 | ✅ 食物抛出后不可控 | 中等（飞行相物理较简单） |
| **旋转陀螺** | ✅ 发力→高转速→进动+章动→动态平衡 | ✅ 脱手后完全不可控 | ✅ 初始条件极其敏感 |
| **托盘搬运** | 中等（达朗贝尔原理较直接） | ✅ 加速过大物品倾倒 | 较低（表观重力可解析） |

> [!tip] Big Picture 的叙事要点
> 1. 先分类（2×2矩阵），再解释每个象限的物理含义
> 2. 意义不是"难"，而是"有用"——Action Acceleration + Task Space Broadening
> 3. 难度不是人为设定的，而是物理本质决定的——长因果链 + 不可归因的高惯性状态
> 4. 这个困难同时影响 model-based 和 learning-based 方法，是任务内禀的

---

## 二、HDC 算法：通过缩放物理演化速度优化 Value Landscape

> [!warning] 本文的 Scope 限定
> HDC（Homotopic Dynamics Curriculum）这篇文章**单纯解决一个问题**：如何通过缩放物理演化速度来优化强化学习的 Value Landscape，使策略能在动态非紧握任务中有效探索和收敛。
>
> 虽然在研究过程中发现了 PD Controller 参数（$K_p$, $K_d$）、初始化设计、力矩 pattern 上限等问题，但**这些问题应当在后续工作中单独解决**，不纳入本文。

### 2.1 问题：Delayed Reward 与崎岖的 Value Landscape

动态非紧握任务对强化学习带来的核心困难可以从 reward design 的角度来理解。其本质困难是 **Delayed Reward**（延迟奖励），而非简单的 sparse reward。

#### 2.1.1 为什么是 Delayed Reward 而非 Sparse Reward

Sparse reward 指的是系统只在极少数状态获得非零奖励。Delayed reward 则更深层——即使试图给予 dense 的 shaping reward，也无法有效引导学习，因为**因果链条太长**，中间状态的即时评估本身就是不可靠的。

以具体任务为例：

- **Triangle Pass**：连续高速转笔。如果想 sparse 地给出成功奖励，应该是完成了很高的圈数并且奖励完成速度。但这意味着不能对每个时刻的转速进行 shaping reward——因为短暂的高转速并不代表最终能成功完成多圈。
- **Thumbaround**：成功相对好定义——转够两圈后稳稳停在收手式。但从初始的 snap 动作到最终的收手式，中间的每个高惯性状态都难以用即时奖励准确评估其对最终成功的贡献。

这正是因果链长度带来的本质困难：当前时刻的"好"可能在未来导致"坏"，反之亦然。

#### 2.1.2 崎岖的 Value Landscape

这种 delayed reward 的结构性困难在强化学习中表现为**极其崎岖的 Value Landscape**（见 RSS26.pdf 第5-6页）。具体而言：

- **Starting Plains（起始平原）**：策略在初始状态附近获得的 value 较低且平坦——系统还未进入有意义的动力学过程。
- **Initiation Ridge（Snap 山脊）**：策略需要越过一个"能量壁垒"来发起 snap 动作，进入高惯性状态。
- **High-Inertia Abyss（高惯性深渊）**：一旦进入高惯性状态，系统处于不完全可控的危险区域。大量的高惯性状态会导致失败（笔飞出），形成一片 value 极低的"深渊"。
- **Sparse Sampling Stepping Stones（稀疏踏脚石）**：只有极少数特定的高惯性状态能通向成功。这些"安全通道"在广阔的高惯性状态空间中极其稀疏。
- **Catch Spire（成功尖峰）**：成功完成任务的 value 极高但区域极小——全局最优是一个尖峰。
- **Hacking Plateau（Reward Hacking 高原）**：如果使用 rotation reward 等 shaping reward，策略容易收敛到"永久高速旋转但不收手"的状态——获得持续的旋转奖励但永远不完成任务。

这个 landscape 导致了两个对称的失败模式：

1. **Risk Aversion（风险规避）**：策略不敢进入高惯性状态，停留在安全但低 value 的起始平原。
2. **Reward Hacking（奖励黑客）**：策略进入高惯性状态后，收敛到 hacking plateau 而非真正的成功。

> [!note] 与 [[ReinforcementLearning]] 的联系
> 这里的 value landscape 崎岖性可以用 [[Optimization#2.6 非凸优化景观理论 (Nonconvex Optimization Landscapes)|非凸优化景观理论]] 中的框架来分析：
> - Risk Aversion 对应虚假局部极小值（spurious local minimum）
> - Hacking Plateau 对应鞍点区域
> - 稀疏踏脚石对应 PL 不等式（[[Optimization#2.6.2 良好景观的特征：无虚假局部极小|良好景观特征]]）不成立的区域

### 2.2 方法：Homotopic Dynamics Curriculum（HDC）

#### 2.2.1 核心思想：让物理世界慢下来

HDC 的核心思想是：**创造一个与真实物理空间同构但速度放慢的仿真空间**。在这个慢速世界中：

- 高惯性状态演化得更慢→策略有更多的决策机会→Value Landscape 被"拉伸"
- 拉伸后的 landscape 更平滑→稀疏踏脚石变得更容易被探索到
- 策略能在不那么 risk averse 的条件下主动进入高惯性状态
- 同时能更容易区分好的高惯性状态和坏的高惯性状态

#### 2.2.2 数学框架：速度缩放与动力学方程的平衡

引入速度缩放因子 $\alpha \in (0, 1]$。将系统的广义速度缩放为 $\dot{q}' = \alpha \dot{q}$，为了保持动力学方程的平衡，需要同步缩放：

原始动力学方程：
$$M(q)\ddot{q} + C(q, \dot{q})\dot{q} + g(q) = \tau$$

速度缩放后，科里奥利/离心力项变为（利用 $C$ 的双线性性质, 详见 [[Dynamics#2.2 Coriolis & Centrifugal Forces (科里奥利力与离心力)]]）：
$$C(q, \dot{q}')\dot{q}' = C(q, \alpha\dot{q}) \cdot (\alpha\dot{q}) = \alpha^2 [C(q, \dot{q})\dot{q}]$$

因此加速度项和重力项也需要同步缩放为 $\alpha^2$ 倍，才能保持方程的平衡。这意味着在缩放空间中：
- 重力变为 $\alpha^2 g$（物理世界"变轻"了）
- 加速度变为 $\alpha^2 \ddot{q}$
- 动力学方程保持自洽

#### 2.2.3 课程迁移：从慢速空间到真实空间

HDC 采用连续的迁移策略：
1. 在初始慢速空间 $\alpha = 0.5$ 中训练策略
2. 利用 $\alpha$ 的**连续性**和动力学方程的**平衡性（同构性）**，将策略逐步迁移至 $\alpha = 1.0$（真实物理空间）
3. 迁移判据：当前 $\alpha$ 下成功率达到阈值（当前使用 70%）后递增 $\alpha$

> [!note] Homotopy 的数学含义
> $\alpha$ 从 0.5 到 1.0 的连续变化构成了一个**同伦（Homotopy）** — 在参数空间中，慢速世界的最优策略可以连续形变到真实世界的最优策略，而不需要跨越不连续的策略壁垒。
> 
> 这正是"Homotopic"一词的来源，也是与离散频率调整方法的核心区别。

### 2.3 HDC vs. Control Frequency Curriculum（CFC）

根据会议纪要中的讨论，HDC 与简单地改变控制频率（Decimation）高度相关。当前需要将改变控制频率也纳入 HDC 框架，并明确 HDC 相比 CFC 的优势。

#### 2.3.1 CFC 的机制

Control Frequency Curriculum（CFC）通过改变 Decimation（策略观察和决策间隔对应的仿真步数 / PD Controller 运行次数）来调整策略的决策频率。例如：
- 目标频率 10Hz（Decimation = 20）
- 训练时先从 Decimation = 10（等效 20Hz）开始
- 逐步增加 Decimation 至目标值

这等效于让策略在更高频率下决策，从而相对于采样频率拉伸了 Value Landscape。

#### 2.3.2 HDC 的优势

1. **连续性**：HDC 的 $\alpha$ 参数是连续的，可以任意精细地调整。CFC 只能调节离散的 Decimation 值（整数）。从 Decimation = 10 跳到 Decimation = 20 意味着策略的决策频率从 20Hz 骤降到 10Hz，这是一个不连续的跳变。
2. **动力学同构性**：HDC 通过同步缩放所有物理参数来保持动力学方程的平衡。CFC 改变频率时，底层 PD Controller 的行为也随之改变——更低的频率意味着 PD Controller 的响应特性发生变化（力矩输出被冻结更长时间），这引入了混淆因素。
3. **仿真特性**：在 $\alpha < 1$ 的慢速空间中，物理引擎的接触模型表现得更接近刚体特性（穿透深度更小），这可能有助于早期探索阶段的策略学习。

#### 2.3.3 还需要明确的问题

- HDC 和 CFC 在数学上的精确等价/不等价关系是什么？
- 是否存在一个统一框架？$\alpha$ scaling 是否可以视为 "连续频率调整 + 物理参数补偿"？
- 实验上，在**相同的等效决策频率**下，HDC 是否仍然优于 CFC？这是关键的控制变量实验。

### 2.4 已完成的实验

| 设置 | Subject | 成功率 | 训练时间 |
|------|---------|--------|----------|
| Thumbaround 20Hz | HDC | 97% | 3.2h |
| Thumbaround 20Hz | Baseline | 93% | 5.9h |
| Thumbaround 10Hz Exp.1 | HDC | 73% | 22.7h |
| Thumbaround 10Hz Exp.1 | Baseline | 0% | \ |
| Thumbaround 10Hz Exp.2 | HDC | 72% | 15.7h |
| Thumbaround 10Hz Exp.2 | Baseline | 42% | 26h |
| Triangle Pass 20Hz | HDC | 81% | 1.8h |
| Triangle Pass 20Hz | Baseline | 62% | 11h |

**当前实验结论：**
1. HDC 策略能收敛到期望的任务模式
2. HDC 达到更高的最终成功率
3. HDC 收敛更快（包含课程时间）
4. 在 10Hz 的低频条件下优势更明显——Baseline 在 Exp.1 中完全无法探索到目标轨迹

### 2.5 需要补充的实验

根据会议纪要和当前研究状态，以下实验是 HDC 这篇文章亟需完成的：

#### 2.5.1 频率对齐消融实验（最关键）

**目的**：消除 "HDC 的优势仅来自等效更高频率" 的质疑。

**设计**：在**相同的等效控制频率**下，对比 HDC（$\alpha=0.5$, Decimation不变）与 CFC（$\alpha=1.0$, Decimation 减半）。确保两者的 agent 在相同的真实物理时间内做出相同次数的决策。

#### 2.5.2 不同 $\alpha$ 值的系统性评估

**目的**：绘制成功率关于 $\alpha$ 的完整曲线（当前仅有 $\alpha=0.5 \rightarrow 1.0$ 的课程实验）。

**设计**：分别在 $\alpha \in \{0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0\}$ 下直接训练（无课程），记录最高成功率。这将直接展示 Value Landscape 的变化趋势。

#### 2.5.3 Reward 工程灵敏度实验

**目的**：证明 HDC 的优势不依赖于特定的 reward function 设计（回应会议中的核心质疑）。

**设计**：三组 reward 工程方案的对比：
- **Heavy**：完整的 shaping reward（rotation reward + waypoints + pretension + catch reward）
- **Medium**：保留 rotation reward + sparse catch reward
- **Light**：仅保留 sparse 的最终成功 reward

在每组 reward 下，分别对比 HDC 和 Baseline。HDC 应当在 reward 越稀疏时优势越明显——如果 HDC 在 Light reward 下任然能有效探索而 Baseline 不能，这才是 "解决探索困难" 的有力证据。

> [!tip] 与 [[Hindsight Experience Replay]] 的关系
> 在 Light reward 场景下，可以进一步引入 HER 作为额外的 exploration baseline。如果 HDC 在 HER 基础上仍有额外收益，这将极大加强论文的论证力度。

> [!tip] Mediator-Based Surrogate Reward 的潜在应用
> DNPM 的长因果链（发力→惯性→接触力→摩擦力→抗重力）天然存在**因果中介变量**。利用 mediator-based reward design 的思想：
> - **候选 Mediator**: 物体角速度、接触力大小、接触点位置等中间物理量
> - **优势**: 用 $\tilde{R}(m, s) = \mathbb{E}[R|M=m, S=s]$ 替代最终的 sparse success reward，可显著降低 credit assignment 方差
> - **与 HDC 的协同**: HDC 通过拉伸 value landscape 改善探索，mediator reward 通过降低方差改善梯度信号质量，两者互补
> - **实验设计**: 可在 Light reward 组中对比 (a) pure sparse, (b) sparse + HER, (c) sparse + mediator surrogate, (d) HDC + mediator
> - 参见 [[ReinforcementLearning#4.2 奖励工程：稀疏 vs. 密集 vs. 塑形 (Sparse vs. Dense vs. Shaping)]]

#### 2.5.4 课程迁移判据的优化

**目的**：当前仅使用 success threshold = 70% 作为 $\alpha$ 递增的判据，这可能导致过早迁移。

**设计**：测试更丰富的迁移判据：
- 达到 success threshold **且** Critic Loss 变化低于阈值
- 基于 success rate 的滑动平均稳定性
- 考虑 value function 的方差而不仅是均值

> [!tip] RL Scaling Laws 对 HDC 课程设计的指导
> IsoCompute Playbook 的 RL 缩放定律研究揭示了与 HDC 课程设计直接相关的规律：
>
> **1. Easy/Hard 问题的不同机制**：
> - Easy（$\alpha$ 小，慢速空间）：大并行 $n$ 主要**锐化策略**（改善 worst-case），此时可优先增大 $B_{problem}$
> - Hard（$\alpha$ 大，接近真实速度）：大并行 $n$ 主要**扩展覆盖**（发现稀疏成功轨迹），此时应增大 $n$ 以探索更多可能
>
> **2. 熵控制应随课程阶段动态调整**：
> - 低 $\alpha$ 阶段（easy）：保留 entropy/KL 正则化防止过早坍缩
> - 高 $\alpha$ 阶段（hard）：移除正则化以允许更激进的探索
> - 这可直接集成到 HDC 的 $\alpha$ 递增逻辑中
>
> **3. 迁移判据优化**：
> - Easy 问题存在明确的"饱和点"（reward 不再随 $n$ 增加而显著提升）
> - 可用类似的饱和检测作为 $\alpha$ 递增的触发条件，替代当前的固定 70% success threshold
>
> 参见 [[ReinforcementLearning#6.3 RL Scaling Laws: 计算最优的训练资源分配]]

### 2.6 探索阶段的关键参数分析

> [!warning] Scope 声明
> 以下参数问题在本文中**仅做分析和记录**，不作为 HDC 方法的一部分解决。它们将在未来工作中独立处理。

在当前的 RL + PD Controller 框架下，有三个参数对初始探索的影响极大：

1. **PPO 高斯 $\sigma$ 的初始值**：当前使用 $\log\sigma_0 = 0$（即 $\sigma_0 = 1$）。根据高斯分布，探索初期有约 32% 的采样值落在 $[-1, 1]$ 之外，被 clamp 到边界。这限制了探索的多样性。
2. **Action Scale**：缩放因子将 RL 输出的 $[-1, 1]$ 映射到实际的关节位置增量。过小的 action scale 限制了力矩幅度；过大的 action scale 导致 PD Controller 饱和。
3. **$K_p$ 值**：PD Controller 的比例增益直接决定了位置误差转化为力矩的比例，即 $\tau = K_p(q_{des} - q) - K_d\dot{q}$。$K_p$ 与 action scale 共同决定了策略最终能输出的力矩大小和 pattern。

这三个参数形成了一个耦合系统，且当前普遍的做法是对真机的 PD 参数进行系统辨识后直接用于仿真训练，缺乏针对动态非紧握任务的优化。

---

## 三、未来突破方向

> [!abstract] 方向概览
> 以下每个方向都可以独立组织为论文。在设计时，尝试将**任务特性**（第一部分中的 Big Picture 特征）与**算法洞见**进行匹配。

### 3.1 方向 A：Low-Level Controller 优化 — 突破力矩表达的上限

#### 3.1.1 问题定义

当前普遍的的灵巧操作强化学习流程采用双层控制架构：
- **高层**：低频 RL 策略（如 10Hz PPO）输出关节位置目标 $q_{target}$
- **低层**：高频 PD Controller（如 200Hz）跟踪 $q_{target}$，产生力矩 $\tau = K_p(q_{target} - q) - K_d\dot{q}$ 与环境交互

然而，通过观察训练后的位控图和力矩图（见 RSS26.pdf 第15页），一个关键现象浮现：**实际的关节位置变化几乎可以忽略不计**。也就是说，$q_{current}$ 几乎不动，而 $q_{target}$ 的变化主要被 PD Controller 转化为力矩输出。

这意味着：**当前策略的实际控制目标几乎就是力矩，而非让末端执行器严格到达预期位置**。但通过位置控制器来间接输出具有动力学特征的力矩，这个逻辑链条本身是不通顺的。

> [!important] 代码级 action 传播链
> 当前仿真代码中的 action 不是直接写入关节角，也不是直接作为真实力矩，而是经历以下链路：
>
> $$
> \text{ActorCritic}(o_t) \to a_t \to \text{env.step}(a_t) \to \text{pre\_physics\_step} \to q^{target}_t \to \text{PD/IsaacGym drive}.
> $$
>
> 在 `pre_physics_step` 中，目标角通常按增量形式生成：
> $$
> q^{target}_t=\operatorname{clip}(q^{target}_{t-1}+\text{action\_scale}\cdot a_t,
> q_{min},q_{max}).
> $$
> 一个高层 action 会在 `controlFrequencyInv` 个物理子步中保持为同一个目标；每个子步调用 low-level control 并执行一次 `gym.simulate`。若 `torque_control=True`，代码显式计算 $\tau=K_p(q^{target}-q)-K_d\dot q$ 并施加 effort；若 `False`，则把 $q^{target}$ 交给 Isaac Gym 内置位置驱动器，其 stiffness/damping 仍然等价于一个内部 PD。
>
> **研究含义**：改变 control frequency 不只是改变“策略多久决策一次”，也改变了同一个 $q^{target}$ 被低层 PD 冻结并反复执行的时间长度。因此 CFC/HDC 的对照实验必须把 `controlFrequencyInv`、`action_scale`、$K_p/K_d$ 和物理 `dt` 一起报告，否则很难区分算法增益与低层控制器增益。

#### 3.1.2 控制架构的系统梳理

要解决这个问题，需要把当前框架放在更广泛的控制体系中理解（详见 [[ControlTheory]]）：

**按 RL 策略输出类型分类：**

| RL 输出类型 | 底层控制器 | 特点 | 代表方法 |
|---|---|---|---|
| 关节位置增量 $\Delta q$ | PD 位置控制器 | 简单、credit assignment 容易，但力矩 pattern 受限 | **当前方法** |
| 关节力矩 $\tau$ | 直通（无底层控制器） | 力矩表达自由，但搜索空间极大、探索困难 | 部分学术工作 |
| 末端位置 + 刚度 $(x, K)$ | 阻抗控制器 | 自然适应接触任务，参考 [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks\|VICES]] | Martin et al. |
| 力指令 $F$ → 期望运动 $x_d$ | 导纳控制器 | 力输入→运动输出因果性，适合力传感丰富的真机 | 工业协作机器人 |
| Latent Action $z$ | 学习的底层控制器 | 底层控制器本身被训练为适应任务 | 待探索 |

**PD Controller 在当前框架中的实际作用：**

PD Controller 起到的最大作用是在探索初期**简化了 credit assignment**。以运动总时长为 1 秒、策略频率 10Hz 为例：实际上只有 10 个时间步在做决策，其余全部由固定的 PD Controller 代理。这大幅缩小了搜索空间（action space 维度从 200 步 × 关节数降到了 10 步 × 关节数），使早期探索更容易找到有意义的策略。

但**最优的情况应该是所有可以做决策的机会都被充分利用**，输出可能带有微调的力矩序列。固定 $K_p$ 和 $K_d$ 的 PD Controller 严重限制了力矩的表达 pattern——例如，它无法表达"先软后硬"或"振荡式"的力矩序列，而这些可能恰恰是动态非紧握任务所需要的。

#### 3.1.3 研究方向

**核心问题**：如何针对动态非紧握任务优化底层控制器，既保留 RL 初期探索时 credit assignment 的简单性（小搜索空间），又让力矩表达的上限 pattern 匹配任务需求？

**可能的方案：**

1. **变阻抗控制**：让 RL 同时输出位置目标和刚度/阻尼参数 $(q_{target}, K_p, K_d)$，使 PD Controller 的特性能随时间变化。参考 [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]]。
2. **阻抗参考模型跟踪** ⭐（来自 [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]]）：更进一步，不是让 RL 直接控制 PD 参数，而是让 RL 输出 $(x_{des}, K_p, K_d)$ 作为一个虚拟弹簧-质量-阻尼系统的参数，策略跟踪该参考模型生成的**动态轨迹**。与方案 1 的关键区别：
   - 参考模型能**主动响应外力** $f_{ext}$，而非被动柔顺
   - 时间平滑技术混合多个时间尺度的跟踪目标，天然处理开环/闭环权衡
   - 统一控制接口无需在力控和位控之间切换
   - **对 DNPM 的核心价值**：snap 阶段高 $K_p$（最大发力）→ 旋转阶段低 $K_p$（柔顺滑动，允许笔在接触中自然演化）→ catch 阶段中 $K_p$（精确但不硬撞），**这种时变阻抗曲线可以被策略自然学习**
3. **变频控制**：让 RL 决定何时需要高频控制（接触切换阶段）、何时低频即可（惯性飞行阶段）。参考 [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]]、[[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|Action Persistence]]、[[Reinforcement Learning for Control with Multiple Frequencies|AP-AC]]。
4. **Latent Action + 学习的底层控制器**：上层输出一种 latent action，底层用一个针对高动态任务训练的控制器来 follow。这保持了小搜索空间，同时释放了力矩表达的自由度。
5. **方案 2 + 方案 3 的融合** ⭐⭐：阻抗参考模型 + 时间自适应。RL 输出 $(x_{des}, K_p, K_d, \Delta t)$，其中 $\Delta t$ 控制动作持续时间（参考 [[TARC - Time-Adaptive Robotic Control|TARC]]）。这统一了力矩 pattern 优化和频率自适应：
   - snap 阶段：高 $K_p$, 短 $\Delta t$（高频精确发力）
   - 旋转惯性阶段：低 $K_p$, 长 $\Delta t$（低频柔顺，节省决策预算）
   - catch 阶段：中 $K_p$, 短 $\Delta t$（高频精确接住）
   - 多体扩展：UR5 和灵巧手各指分别定义参考模型，通过力传导参数 $a \in [0,1]$ 控制耦合

> [!tip] 任务-算法匹配
> - **Thumbaround / Triangle Pass**：需要"先爆发后精细"的力矩 pattern → 阻抗参考模型跟踪（FACET 方案 2）最匹配。snap 阶段高 $K_p$，旋转阶段低 $K_p$，catch 阶段中 $K_p$
> - **颠锅**：需要先加速后减速的连续相位 → 方案 5（阻抗参考模型 + 时间自适应）最匹配。加速相高频高刚度，飞行相低频低刚度
> - **陀螺**：Snap 阶段需要极高的瞬时力矩 → 方案 2 的高 $K_p$ 直接提供，无需直接力矩输出
> - **托盘搬运**：需要精确的姿态微调 → 方案 2 的统一接口天然适配（低 $K_p$ 柔顺搬运 + 高 $K_p$ 精确定位）

#### 3.1.4 知识库关联

- [[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]] — 阻抗控制的理论基础
- [[ControlTheory#3.3 解决方案 II：导纳控制 (Admittance Control) —— 位置内环的策略]] — 另一种因果性的控制范式
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — VICES 框架（方案 1）
- [[FACET - Force-Adaptive Control via Impedance Reference Tracking]] — ⭐ **阻抗参考模型跟踪**（方案 2），时变 $K_p$ 直接匹配 snap/spin/catch 相位
- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 弹性时间步 RL
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — 动作持续
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率 RL (AP-AC)
- [[TARC - Time-Adaptive Robotic Control]] — 连续时间自适应控制（方案 5 的频率自适应组件）

---

### 3.2 方向 B：高惯性状态的通用表征 — 基于凸包的 Bootstrapping

#### 3.2.1 问题定义

当前的 HDC 训练中，**没有显式地告诉系统怎样的高惯性状态是好的、怎样的是坏的**。系统只能通过最终的成功/失败信号来隐式学习。而如果只用 shaping reward（如奖励高转速），系统无法显式区分"导向成功的高转速"和"导向失败的高转速"之间的区别——它们在当前状态下看起来可能完全一样。

需要的是一种**通用的方式**来传达哪些高惯性状态是好的。

#### 3.2.2 凸包假设

**核心假设**：如果某个高惯性状态 $(q, \dot{q}, [F])$ 最终导致了成功，那么这个状态的**邻居**很大概率也会导致成功。进一步地，成功的高惯性状态在状态空间中能组成一个**近似凸包（Convex Hull）**。

这个假设的物理直觉是：
- 成功的状态意味着物体在相空间中处于一条"安全通道"上
- 这些安全通道在局部是连续的、平滑的
- 因此成功状态的邻域仍然属于安全区域
- 多条安全通道的凸组合仍然是安全的（因为物理演化在局部是近似线性的）

#### 3.2.3 算法思路

1. **收集成功经验**：在训练初期（哪怕靠运气），收集所有导致最终成功的轨迹上经过的高惯性状态 $(q_i, \dot{q}_i)$
2. **构建凸包**：在这些状态点上构建凸包（或使用核密度估计等软版本）
3. **Bootstrapping**：利用这个凸包来：
   - 作为辅助 reward：处于凸包内的高惯性状态获得 bonus
   - 作为探索引导：鼓励策略探索凸包边界。凸包之外的状态显得更危险（不安全）
   - 逐步扩展：随着更多成功经验的积累，凸包逐渐扩展

4. **与 shaping reward 的区别**：纯 shaping reward（如奖励高转速）只能区分"高转速 vs. 低转速"，无法区分"安全的高转速 vs. 危险的高转速"。凸包方法利用了成功经验的结构性信息，能做到这一点。

> [!note] 与 [[Hindsight Experience Replay]] 的联系
> HER 通过 goal relabeling 将失败轨迹转化为成功经验，从而隐式地构建了一个"可达状态集"。凸包假设可以看作 HER 在**连续状态空间**中的几何推广——HER 构建的是目标空间的覆盖集，凸包方法构建的是高惯性状态空间的安全集。

#### 3.2.4 任务-算法匹配

| 任务 | 凸包假设是否成立 | 预期效果 |
|------|:---:|------|
| **Thumbaround** | ✅ 安全的 snap 力度和角度应在局部连续 | 利用成功 snap 经验加速 exploration |
| **Triangle Pass** | 部分成立（连续旋转中相位空间可能非凸） | 需要分段凸包 |
| **陀螺** | ✅ 成功的初始旋转速度和角度应在局部连续 | 极其适合——初始条件敏感，凸包能大幅缩小搜索范围 |

---

### 3.3 方向 C：进入高惯性状态的准备阶段 — 初始化设计与课程学习

#### 3.3.1 问题定义

当前的 Thumbaround 训练中，即使设计了 pretension 奖励来鼓励策略在 snap 之前做好准备，策略仍然会**急着进入高惯性状态**。原因是 RL 的折扣因子 $\gamma$ 使策略对时间非常敏感——它希望尽快进入高奖励状态，而不愿意花时间在低奖励的准备阶段。

然而，"如何进入高惯性状态"可能比"在高惯性状态中如何行动"更重要。一个不好的初始条件（笔的位置、手指的构型）可能使得无论怎样 snap 都不可能安全地完成旋转。

#### 3.3.2 当前初始化方案及其局限

当前的初始化方式（参考 Xiaolong Wang、EUREKA 等做法，见 [[EUREKA: Human-Level Reward Design via Coding Large Language Models|EUREKA]]）：
1. 人为指定任务开始时对应的先验几何位置（如转笔的标准起手式）
2. 对先验位置施加随机扰动
3. 筛选出 10000 个扰动后能存活 0.1 秒的状态作为初始化

**局限性**：
- 这 10000 个初始化状态是通过几何先验和短时稳定性筛选得到的，不代表策略真正学会了从任意状态调整到适合发力的状态
- 策略只学会了"从这些特定的初始化出发如何成功"，而非"如何调整到适合成功的初始化"

#### 3.3.3 改进方案：凸包式初始化扩展课程

1. **初始阶段**：用当前 10000 个筛选点围成的**凸包**作为初始化分布（均匀采样凸包内部，而非仅使用这 10000 个点）
2. **课程扩展**：随着训练进行，逐步扩展凸包：
   - 在凸包边界外采样新的初始化点
   - 如果策略能从这些点成功完成任务，将它们纳入凸包
   - 哪怕这些新点**脱离了几何先验**——这意味着策略真正学会了初始状态的微调
3. **学会 Pre-injection Adjustment**：通过不断扩展初始化凸包，策略被迫学习从"不太理想"的初始状态调整到"适合发力"的状态。这等价于让策略学会在进入高惯性状态之前主动调整手部构型。

#### 3.3.4 与 $\gamma$ discount 的对抗

策略急着进入高惯性状态的根本原因是折扣因子 $\gamma$ 带来的时间压力。可能的对策：
- 在准备阶段使用更高的 $\gamma$（接近 1），减少时间折扣的压力
- 设计专门的 "readiness reward"，奖励策略在 snap 之前达到理想的预紧构型
- 使用 options framework 或 hierarchical RL，将准备阶段和执行阶段分离为不同的子策略

> [!tip] 任务-算法匹配
> - **Thumbaround**：预紧构型→snap→旋转→收手式。准备阶段至关重要。
> - **陀螺**：需要精确的抓握角度和拉绳/发力方向。初始化决定一切。
> - **颠锅**：需要合适的锅倾角和食物分布。准备阶段可类比为"loading phase"。
> - **托盘搬运**：需要物品在托盘上的稳定初始布局。初始化直接影响上限。

---

### 3.4 方向 D：计划中的新任务及完整任务图谱

#### 3.4.1 已训练/测试的任务

| 任务            | 状态    | 意义类别                  | 动力学特征               |
| ------------- | ----- | --------------------- | ------------------- |
| Thumbaround   | ✅ 已训练 | Task Space Broadening | 长因果链 + 危险高惯性 + 不可归因 |
| Triangle Pass | ✅ 已训练 | Task Space Broadening | 连续模式中的持续不可控         |

#### 3.4.2 计划训练/测试的任务

| 任务       | 意义类别                  | 长因果链 |   高惯性危险性   |   不可归因性   | 最匹配的算法方向            |
| -------- | --------------------- | :--: | :--------: | :-------: | ------------------- |
| **旋转陀螺** | Task Space Broadening |  ✅   | ✅ 脱手后完全不可控 | ✅ 初始条件极敏感 | 方向 B（凸包）+ 方向 C（初始化） |
| **颠锅**   | Task Space Broadening |  ✅   |  ✅ 飞行相不可控  |    中等     | 方向 A（变频控制）          |
| **托盘搬运** | Action Acceleration   |  中等  |  ✅ 加速过大倾倒  |    较低     | 方向 A（变阻抗）           |
| **开瓶盖**  | Action Acceleration   |      |            |           |                     |

#### 3.4.3 任务-算法-Big Picture 特征的三角对应

```
Big Picture 特征          算法方向              适配任务
─────────────────────────────────────────────────────────
长因果链 → Delayed Reward   → HDC (Value Landscape)  → 全部任务
高惯性危险 → Risk Aversion  → 方向 B (凸包 Bootstrapping) → 陀螺、Thumbaround
不可归因性 → Credit Assignment → 方向 A (Controller 优化) → 颠锅、托盘
进入条件敏感 → 准备阶段      → 方向 C (初始化课程)      → 陀螺、Thumbaround
```

---

## 四、知识库关联索引

### 4.1 Foundations 关联

| Foundation | 关联章节 | 与 DNPM 的联系 |
|------------|--------|-------------|
| [[Dynamics]] | 2.2 科里奥利力与离心力 | 高惯性状态的广义力来源 |
| [[Dynamics]] | 2.3 接触约束（Pfaffian） | 非紧握状态下的约束动力学 |
| [[Dynamics]] | 3.1 Lagrangian 公式 | $M\ddot{q}+C\dot{q}+g=\tau$ 的速度缩放推导基础 |
| [[Dynamics]] | 5 接触动力学 | LCP 求解中的接触切换 |
| [[ControlTheory]] | 3.2 阻抗控制 | PD Controller 作为阻抗控制的特例；变阻抗的理论框架 |
| [[ControlTheory]] | 3.3 导纳控制 | 力输入→运动输出的另一种控制因果性 |
| [[ControlTheory]] | 7.3 接触状态机 | 非紧握操作中的模式切换 |
| [[ReinforcementLearning]] | 2.5 PPO | 当前策略优化算法 |
| [[ReinforcementLearning]] | 2.8 Exploration 理论 | Risk aversion、intrinsic motivation |
| [[ReinforcementLearning]] | 4.2 奖励工程 | Mediator-based surrogate reward 降低 credit assignment 方差 |
| [[ReinforcementLearning]] | 6.3 RL Scaling Laws | 计算预算分配、easy/hard 熵控制策略 |
| [[ReinforcementLearning]] | 6.4 Test-Time RL | 部署时在线适应新环境的潜在范式 |
| [[ContactMechanics]] | 3 接触建模演变 | 摩擦锥、滑移检测 |
| [[Optimization]] | 2.5 非凸优化景观理论 | Value Landscape 崎岖性的数学框架 |
| [[InformationTheory]] | 5.0 率失真理论 | 压缩-去噪对偶性指导状态表征设计 |
| [[InformationTheory]] | 6.1 Empowerment | 高惯性状态下的可控性度量 |
| [[SignalProcessing]] | 触觉信号处理 | 接触切换的实时检测 |

### 4.2 PapersRecap 关联

**频率与时间自适应：**
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] — HDC vs CFC 对比的理论基础
- [[Elastic Time Step Reinforcement Learning, VTS-RL]] — 弹性时间步，方向 A 的候选方法
- [[Reinforcement Learning for Control with Multiple Frequencies]] — 多频率 RL，方向 A 的理论框架
- [[TARC - Time-Adaptive Robotic Control]] — 连续时间自适应，方向 A 的核心参考

**变阻抗与接触控制：**
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 阻抗参数化（方案 1）
- [[FACET - Force-Adaptive Control via Impedance Reference Tracking]] — ⭐ **阻抗参考模型跟踪**（方案 2），时变阻抗直接匹配动态操作相位

**稀疏奖励与长时程探索：**
- [[Hindsight Experience Replay]] — HDC 的 sparse reward baseline；方向 B 的理论先驱
- [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] — 特权动作简化探索

**转笔与灵巧操作：**
- [[Lessons from Learning to Spin Pens]] — 转笔任务设计的直接参考；初始化设计的启发

**奖励设计：**
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — LLM 辅助 reward design
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]] — 探索与利用的随机控制理论

**Sim-to-Real：**
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] — 真机部署的参考框架
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 在线修正的参考

### 4.3 与汇报材料和会议纪要的对应

| 内容 | 来源 | 本文位置 |
|------|------|---------|
| 2×2 分类矩阵 | RSS26.pdf 第2-3页 | 1.1 节 |
| Thumbaround 动力学分析 | RSS26.pdf 第4页 | 1.3.1 节 |
| Value Landscape 图 | RSS26.pdf 第5-6页 | 2.1.2 节 |
| 速度缩放数学 | RSS26.pdf 第7页 | 2.2.2 节 |
| 实验结果 | RSS26.pdf 第11页 | 2.4 节 |
| HDC vs CFC 讨论 | RSS26.pdf 第12页 + 会议纪要 | 2.3 节 |
| PD Controller 问题 | RSS26.pdf 第15-16页 + 会议纪要 | 2.6 节 + 3.1 节 |
| Reward 设计讨论 | 会议纪要 | 2.5.3 节 |
| 频率对齐实验需求 | 会议纪要 | 2.5.1 节 |
