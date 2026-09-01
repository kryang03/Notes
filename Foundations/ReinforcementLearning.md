---
tags:
  - foundation
  - reinforcement-learning
  - dexterous-manipulation
  - sim-to-real
aliases:
  - 强化学习
  - RL
  - PPO
  - SAC
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[Actuation]]"
  - "[[WorldModels]]"
  - "[[Optimization]]"
  - "[[StochasticProcess]]"
  - "[[RepresentationLearning]]"
  - "[[InformationTheory]]"
  - "[[EmbodiedAI]]"
---

# 灵巧操作中的强化学习：从 Bellman 递推到真机闭环

# Reinforcement Learning in Dexterous Manipulation: From Bellman Recursion to Real-World Closed-Loop Learning

> [!tip] 相关领域
> - [[ControlTheory]] — RL 与最优控制本是一家：Bellman 方程↔HJB、LQR↔值迭代、SAC 熵↔阻抗柔顺、Safe RL↔稳定性证书
> - [[Dynamics]] — 动力学模型是 Model-Based RL 的世界模型；接触非光滑性是策略梯度高方差的物理根源
> - [[Actuation]] — Sim-to-Real 的 Action/Transition gap 有明确物理来源：仿真"关节虚拟力矩"假设在真机被电机+FOC+减速器+传动打破；本讲 §9 的 DR 参数、action space 选择都由执行器特性决定
> - [[Optimization]] — RL 本质是序贯决策优化；策略梯度↔随机优化，信任域↔近端算法
> - [[StochasticProcess]] — 扩散策略、belief-MDP、MPPI 的理论母体
> - [[RepresentationLearning]] — 状态表征决定泛化；触觉/视觉 latent 是策略的"感官"
> - [[InformationTheory]] — 探索的本质是信息获取；熵正则、empowerment、技能发现
> - [[EmbodiedAI]] — VLA 把 RL 嵌入"视觉-语言-动作"端到端闭环
>
> **贯穿母题（本讲的"主角"）**：**指间转笔 (in-hand pen-spinning / finger-gaiting)**。我们将让这一个任务把整本讲稿的每一个算法、每一条公式都"演"一遍。

---

## 0. 母题与理论大厦构建路线：从 Bellman 递推到真机闭环学习

> [!abstract] 为什么用"指间转笔"做贯穿母题？
> 灵巧操作的研究任务很多——拧瓶盖、插 USB、叠衣服——但**指间转笔**有一个独一无二的好处：它**同时**触发了强化学习每一层理论的核心难点。一支笔在手指间翻转一圈，需要：
> - **指步序列（finger gait）**＝一连串接触模式的离散切换 → 这是**混合动力学与信用分配**问题；
> - **左转 or 右转**两种同样合法的策略 → 这是**多峰动作分布**问题；
> - 只有"转满一圈"才算成功、中途无明显奖励 → 这是**稀疏奖励与探索**问题；
> - 真笔的重心、摩擦、柔软指尖都与仿真不同 → 这是 **sim-to-real** 问题。
>
> 全讲中，每当引入一个新算法，我们都回到这支笔：**"它会如何转这支笔？它在转笔的哪个环节比上一个算法更强？"** 这是本讲的记忆主线。

强化学习 Foundation 的主线，必须从"最大化奖励"这句口号，细化为一句工程命题：**如何在未知、非平滑、部分可观测的物理系统中，构造一个可以不断被数据更新的反馈策略。** 围绕这句命题，整座理论大厦分为六层，每一层回答一个更尖锐的问题：

| 层级 | 关键问题 | 理论工具 | 转笔母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **MDP/POMDP 层** | 当前观测是否足以预测未来？ | Markov state、belief、history encoder | 触觉迟滞、指尖温漂、CAN 延迟破坏单帧 Markov 性 | §2 |
| **Bellman 层** | 价值如何递推、如何把末端反馈回传？ | 值函数、TD、SARSA/Q、GAE | 转满一圈的奖励要回传给最初那次"松指" | §2–§3 |
| **策略梯度层** | 环境不可微时如何更新策略？ | log-derivative、baseline、advantage | 接触求解器不可微，仍可采样估计梯度 | §4 |
| **稳定更新层** | 策略如何不被一次更新毁掉？ | TRPO/PPO、KL、clipping、熵 | 防止一次大更新破坏已学会的指步时序 | §5 |
| **样本效率层** | 昂贵的真机数据如何反复利用？ | SAC、replay、MBRL、offline RL | 在硬件磨损与安全约束下榨干每条轨迹 | §5–§6 |
| **迁移层** | 仿真策略如何安全上真机？ | DR、system ID、RMA、world model、safety filter | 把 action gap / transition gap / reward gap 分开诊断 | §9 |

> [!important] Foundation 级判断标准（任何 RL 算法进入本库都要回答四问）
> 1. **数据来自哪里**（on-policy 现采 / off-policy replay / offline 静态 / 想象 rollout）？
> 2. **梯度如何产生**（值的 Bellman 残差 / 策略的 log-derivative / 可微动力学的解析梯度）？
> 3. **旧数据能否重用**（信任域内的重要性采样 / replay buffer / 保守 Q）？
> 4. **接触与执行器的不确定性如何进入系统**（进入状态？进入训练分布？进入 belief？）？

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>      [[Dynamics]] ──模型──┐         ┌──值函数/稳定性证书──> [[ControlTheory]]
> [[ContactMechanics]] ─非光滑─┤        │
>   [[StochasticProcess]] ─belief─┼──> 【RL】 ──探索/熵──> [[InformationTheory]]
>      [[Optimization]] ─序贯优化─┤        │
>  [[RepresentationLearning]] ─表征─┘        └──端到端动作──> [[EmbodiedAI]]
> ```
> 读法：左侧四者是 RL 的"输入"（提供模型、非光滑结构、belief、优化机器、状态表征）；右侧三者消费 RL 的产出（控制证书、信息目标、端到端策略）。本讲会在每个推导拐点用 `[[链接]]` 显式回扣。

---

## 1. 为什么是 RL：从"转笔"看解析方法的失效

> [!tip] 本节四拍
> **直觉**（转笔到底难在哪）→ **推导**（写出动力学与状态空间，看清非光滑性的两副面孔）→ **对比**（解析控制 vs 模仿学习，各自为何不够）→ **落点**（我们需要一种"能试错、能自我修正、对模型误差不敏感"的方法——这正是 RL）。

### 1.1 母题解剖：转一支笔到底在求解什么？

把一支笔架在 Shadow Hand（24 DoF）的四指之间，要求它绕笔的长轴翻转 360°。一个完整的"指步周期"大致是：

```
食指松开(脱离接触) → 笔在重力/惯性下微转 → 中指补位(建立新接触) →
拇指施加切向力(推动旋转) → 无名指防止笔掉落(力闭合) → 循环
```

请注意这一串动作里**没有任何一步可以单独定义成功**。成功只在"转满一圈且笔没掉"这个终点被定义。于是我们要解的，是一个**序贯决策问题**：在每个时刻 $t$，根据观测 $o_t$（关节角、指尖触觉、（也许）笔的位姿）输出力矩或目标关节角 $a_t$，使得某个滞后的、稀疏的成功信号被最大化。这正是马尔可夫决策过程 (MDP) 的语言——我们在 §2 形式化它。但在写下 MDP 之前，先看清这个物理系统"硬"在哪。

### 1.2 状态空间的第一抉择：广义坐标 vs 最大化坐标

构造状态空间 $\mathcal{S}$ 的第一个决策，是坐标系的选取——这个看似平凡的选择，直接决定了网络要学多少"物理常识"。

**广义坐标 (Generalized Coordinates, $q\in\mathbb{R}^n$)**：描述系统构型所需的**最小独立参数集**。对灵巧手就是各关节角 $q=[\theta_1,\dots,\theta_n]^T$。它**自动满足**关节连杆的完整约束 (holonomic constraints)，维度最小，学习效率高。

**最大化坐标 (Maximal Coordinates)**：用每个刚体在世界系下的位姿 $(x,y,z,\text{quat})$ 描述。维度冗余、且需显式维持连杆约束，但它**直接暴露物体间相对距离与接触几何**，让网络更易"看见"接触特征。

机器人的运动方程是一个二阶 ODE（拉格朗日形式，详见 [[Dynamics#3. 能量层：从 Hamilton 原理到操作器方程|Dynamics §3.1]]）：

$$
M(q)\ddot{q} + \underbrace{C(q,\dot q)\dot q}_{\text{科氏/离心}} + \underbrace{g(q)}_{\text{重力}} = \tau + \underbrace{J(q)^T f_{ext}}_{\text{接触力映射}}
$$

- $M(q)\succ0$：惯性矩阵（对称正定）；$C$：科氏与离心；$g$：重力；$\tau$：关节力矩（控制输入）；$J^T f_{ext}$：外部接触力折算到关节空间的力矩。

> [!note] RL 的 value-add 第一次出现在这里
> 经典的**计算力矩控制 (Computed Torque)** 试图用逆动力学 $\tau = M(q)\ddot q_{des}+C\dot q+g - J^Tf_{ext}$ 把非线性"抵消"掉。但转笔时 $f_{ext}$（接触力）**未知、非光滑、强非线性**——指尖软垫的刚度 $K$ 极难辨识（见 [[ContactMechanics#4.3 超越 Hertz：大变形与软体抓取|软指接触]]）。RL 的价值在于：**它不显式求解上式，而是通过交互学一个策略 $\pi_\theta(a\mid s)$ 去隐式地驾驭这些项**，尤其是那个最难建模的 $f_{ext}$。

### 1.3 非光滑性的两副面孔：接触流形与混合动力学

转笔之所以折磨所有方法，根源是**接触带来的非光滑性**。它有两副面孔。

**面孔一：约束流形与切空间（"探索往哪儿走"）。** 当手指压住笔时，系统自由度瞬间下降，状态被钉在一个低维**约束流形**上：

$$
\mathcal{M}_c=\{(q,\dot q)\mid \phi(q)=0,\ J(q)\dot q=0\}
$$

其中 $\phi(q)$ 是接触距离函数（即 [[ComputationalGeometry#4. 有向距离场 (SDF)：连续优化的基石|SDF]]）。若在全空间 $\mathbb{R}^n$ 上加各向同性高斯噪声去探索，会立刻撞上两种失效：**穿透**（指令把手指压进笔内部，物理引擎产生巨大排斥力、仿真爆炸）与**脱离**（不慎断开接触、笔掉落）。

> [!note] 为什么各向同性噪声几乎"必然"违约（补上这一步，不让读者脑补）
> 约束 $\phi(q)=0$ 在 $\mathbb{R}^n$ 里是一张**余维 $\ge 1$ 的超曲面**。在流形上任一点 $q$，整个动作空间正交分解为两块：**切空间** $T_q\mathcal M_c$（沿之移动、一阶保持 $\phi=0$、维持接触）与其正交补**法空间**（沿之移动、直接改变 $\phi$）。一阶展开
> $$\delta\phi \approx \nabla\phi(q)\cdot\delta q,$$
> 而 $\nabla\phi$ 恰是 [[ComputationalGeometry#4. 有向距离场 (SDF)：连续优化的基石|SDF 梯度]]——也就是**接触面的外法向** $\hat n$。各向同性高斯噪声在每个坐标方向独立同分布，因此它的**法向分量以概率 1 非零**：$\delta\phi>0$ 就**脱离**（手指离开笔面、丢失接触、笔掉落），$\delta\phi<0$ 就**穿透**（压进笔体内部、$\phi$ 变负、排斥力爆炸）。恰好落在切空间（$\delta\phi=0$）是一个**零测度事件**——所以"违约"不是偶发、而是几乎处处发生。更糟的是接触流形**余维很高**（五指、每指多个接触约束 → 法向维度远多于切向维度），各向同性噪声几乎把全部"探索预算"砸在违约的法向上，真正"沿笔面滑动"的切向分量寥寥无几。这就是不加几何先验时，RL 要白白烧掉成千上万样本、仅仅去学"别离开接触面"这一条基本物理事实的根源。下面的切空间探索把动作**从一开始就限制在** $T_q\mathcal M_c$ 内，从源头抹掉法向违约。

> [!tip] 几何先验：在切空间上探索（Geometric RL）
> 一个深刻的修补是让策略在流形的**切空间** $T_q\mathcal M_c$ 上输出动作，再用指数映射拉回流形：
> $$a_{safe}=\mathrm{Exp}_q(\pi(s)),\qquad \pi(s)\in T_q\mathcal M_c$$
> 其中 $\mathrm{Log}$ 把流形点映回切空间、$\mathrm{Exp}$ 把切向动作映回流形。这样 RL 不必浪费成千上万样本去学"别穿透笔"这种基本物理事实，而专注于"如何在保持接触的同时转动笔"。这是把 [[ComputationalGeometry]] 的微分几何当作 RL 的归纳偏置——我们在 §7 探索一节会再次回扣这个"安全探索"动机。

**面孔二：模式切换与组合爆炸（"决策有多少种"）。** 从系统论看，转笔是一个**混合动力学系统 (Hybrid System)**，每个接触点都在若干离散模式间跳变：

| 模式     | 物理    | 约束                                               |
| :----- | :---- | :----------------------------------------------- |
| Free   | 手指悬空  | 动力学光滑                                            |
| Impact | 撞上笔   | 速度跳变（动量守恒、能量耗散）                                  |
| Stick  | 摩擦锥内  | 相对速度 $v_{rel}=0$                                 |
| Slide  | 达摩擦极限 | $\|f_t\|=\mu f_n$（库伦律，见 [[ContactMechanics]]摩擦锥） |


五根手指、每指三态（Free/Stick/Slide），瞬时模式数高达 $3^5=243$。解析规划器要在**每一帧**决定处于哪种模式——这是一个**混合整数规划 (MIP)**，一般 NP-hard。这正是 §1.4 解析控制失效的算法根源，也是 §6 接触隐式优化（CITO，见 [[Optimization#5.3 阶段三：接触隐式轨迹优化 CITO（求解器自己发现）|Optimization §3.3]]）试图绕开的难题。

### 1.4 对比之一：解析控制为何失效

> [!warning] 解析控制的两道硬墙
> 1. **模型失配（Sim-to-Real 的物理根源）**：解析控制假设刚体接触，而真实指尖是软的、有变形、迟滞与微观纹理；接触刚度 $K$ 几乎无法精确辨识。误差在长指步序列上累积。
> 2. **求解器瓶颈**：每帧解线性互补问题 (LCP) 算接触力，复杂度随接触点数近似 $O(N^3)$（见 [[ContactMechanics#5.2 两类求解器：直接 vs 迭代|LCP 求解]]）；叠加 §1.3 的 $3^5$ 模式组合，多指实时规划不可行。
>
> **结论**：我们需要一种**对模型误差不敏感 (model-agnostic) 且能实时前向推理**的方法 → 指向"学出来的策略"。

### 1.5 对比之二：纯模仿学习为何不够

既然建模难，能不能直接**模仿人**？这就是行为克隆 (BC)、逆强化学习 (IRL)、GAIL 的思路。它有一个统计学上的致命伤——**分布漂移 (covariate shift)**：

> [!warning] 复合误差：模仿学习的雪崩
> 训练数据来自专家分布 $p_{data}(s)$，但策略上机后自己产生的状态分布是 $p_\pi(s)$。一旦机器人犯一点小错（笔歪了一点），它进入专家从未演示过的状态；BC 没有纠错信号，误差逐步累积 (compounding errors)，在 $T$ 步上以 $O(\epsilon T^2)$ 的速度发散。再加上采集 24-DoF 高维灵巧演示极其昂贵（动捕受遮挡、VR 遥操作低效），**纯模仿不可持续**。

> [!important] 本节落点：为什么必须是 RL
> 解析控制**输在模型**，模仿学习**输在没有纠错**。我们需要的方法要能：**(a)** 在"没见过的状态"里通过**试错 (trial-and-error)** 自我修正；**(b)** 不依赖精确接触模型；**(c)** 实时推理。这三条恰好定义了**强化学习**。下一节，我们用 MDP 与 Bellman 方程把"试错学习"变成可计算的数学。
>
> （但请记住：模仿不是被抛弃，而是被**收编**——§5 的 RLPD、§9 的 teacher-student、§10 的扩散策略，都是"先模仿、再用 RL 修正"。这条"模仿×强化"的缝合线会贯穿全讲。）

---

## 2. MDP 与 Bellman：价值的语言

> [!tip] 本节四拍
> **直觉**（试错学习需要一个"记账系统"）→ **推导**（MDP→值函数→Bellman 方程，逐行推）→ **对比**（估计价值的三种范式 DP/MC/TD，偏差-方差谱）→ **联系**（Bellman↔[[ControlTheory|最优控制]] HJB↔[[Optimization|动态规划]]，Markov↔[[StochasticProcess]]）。

### 2.1 MDP 与 POMDP：把"试错"写成数学

一个**马尔可夫决策过程 (MDP)** 是五元组 $(\mathcal S,\mathcal A,P,r,\gamma)$：状态空间 $\mathcal S$、动作空间 $\mathcal A$、转移核 $P(s'\mid s,a)$、奖励 $r(s,a)$、折扣 $\gamma\in[0,1)$。策略 $\pi(a\mid s)$ 给出动作分布。**转笔的 MDP** 大致是：

- $\mathcal S$：关节角 $q$、关节速度 $\dot q$、指尖触觉图、（特权信息下）笔的位姿与角速度；
- $\mathcal A$：各关节的目标角增量或力矩（连续，$\subset\mathbb R^{24}$）；
- $r$：转过的角度增量 − 掉笔惩罚 − 能量惩罚（奖励设计的陷阱见 §8）；
- $\gamma$：把"转满一圈"的远期成功折算到当下。

**Markov 性是一切递推的地基**：$P(s_{t+1}\mid s_t,a_t)$ 不依赖更早历史。它等价说"$s_t$ 已概括了预测未来所需的一切"。

> [!warning] 转笔里 Markov 性是怎么被破坏的（这决定了你要不要 RNN）
> 单帧观测往往**不是** Markov 状态：
> - **触觉迟滞**：橡胶指垫的 Prandtl–Ishlinskii 迟滞（见 [[SignalProcessing#2.2 迟滞：Prandtl–Ishlinskii 模型与逆补偿|SignalProcessing §2.2]]）让"当前读数"依赖加载历史；
> - **温漂 / 磨损**：电机常数随时间漂移；
> - **通信延迟**：CAN 总线让"指令"与"生效"错开几个控制周期。
>
> 此时问题退化为 **POMDP**：观测 $o_t\ne s_t$。两条出路——**(a)** 把历史编码进隐状态 $b_t=f(o_{1:t})$（RNN/Transformer，即 belief，见 [[StochasticProcess#7. 信念空间规划：为感知而行动|belief space]]）；**(b)** 用环境编码器从历史推断隐式物理参数（RMA，见 §9）。"要不要上 RNN"这个工程问题，本质是"单帧是否 Markov"这个理论问题。
>
> **为什么"注意力读一段历史窗口"就够了（POMDP→belief→latent 这条暗线的关键一环）**：贝叶斯滤波告诉我们，belief $b_t=p(s_t\mid o_{1:t})$ 是**充分统计量**——它压缩了 $o_{1:t}$ 中所有对预测未来有用的信息，据它决策与据全历史决策等价。而一个 **Transformer 对历史窗口 $o_{t-L+1:t}$ 做注意力**，正是在**数据驱动地逼近这个充分统计量**：注意力权重 $\alpha_{t,k}\propto\exp(\langle q_t,k_k\rangle)$ 决定"过去哪几帧对当前决策要紧"，相当于隐式地做了"哪些历史观测该保留进 belief"的加权积分（见 [[RepresentationLearning#4.6 序列与注意力表征：从无序集合到有序序列|RepresentationLearning §4.6]]）。于是 RNN 的递归 belief 更新与 Transformer 的窗口注意力，是同一个"充分统计量"目标的两种参数化——前者串行压缩、后者并行加权。这也解释了窗口长度 $L$ 的物理含义：$L$ 必须覆盖迟滞/延迟/温漂的**最长记忆时间常数**，否则窗口内的历史不足以重建 belief，POMDP 仍未被消解。

### 2.2 值函数与 Bellman 方程

定义从 $t$ 起的**折扣回报** $G_t=\sum_{k\ge0}\gamma^k r_{t+k}$。两个值函数：

$$
V^\pi(s)=\mathbb E_\pi[G_t\mid s_t=s],\qquad
Q^\pi(s,a)=\mathbb E_\pi[G_t\mid s_t=s,a_t=a].
$$

**Bellman 期望方程**来自把回报拆成"一步奖励 + 折扣后的未来回报"，再对一步取期望：

$$
\begin{aligned}
V^\pi(s)&=\mathbb E_{a\sim\pi}\Big[r(s,a)+\gamma\,\mathbb E_{s'\sim P}\big[V^\pi(s')\big]\Big],\\
Q^\pi(s,a)&=r(s,a)+\gamma\,\mathbb E_{s'\sim P}\big[\mathbb E_{a'\sim\pi}Q^\pi(s',a')\big].
\end{aligned}
$$

最优值满足**Bellman 最优方程**（把"对 $\pi$ 求期望"换成"对 $a$ 取 max"）：

$$
Q^*(s,a)=r(s,a)+\gamma\,\mathbb E_{s'}\big[\max_{a'}Q^*(s',a')\big].
$$

> [!note] 跨原理联系：Bellman ↔ HJB ↔ LQR ↔ 动态规划
> Bellman 最优方程是**离散时间**的最优性原理；其连续时间极限就是控制论的 **Hamilton–Jacobi–Bellman (HJB)** 方程。当动力学线性、奖励二次时，HJB 的解是 **LQR**（[[ControlTheory#11. 线性二次最优控制 (LQR)|ControlTheory §11]]）——也就是说 **LQR = 能解析求解的 RL**。这条线索极其重要：它意味着"值函数"既是 RL 的核心对象，也是控制论的最优代价函数 (cost-to-go)，更是 [[Optimization|动态规划]] 的子结构。**记住这一个等价，你就同时拿到了三个领域的钥匙。**

> [!tip] 转笔直觉
> $Q^*(s,a)$ 回答："此刻笔在这个姿态、我做这个'松指'动作，从今往后最好能转多少圈？" 一旦学会 $Q^*$，最优策略就是 $\pi^*(s)=\arg\max_a Q^*(s,a)$——贪婪地挑当下看起来最有前途的指步。难点全在"如何学到这个 $Q^*$"。

### 2.3 估计价值的三种范式：DP → MC → TD（偏差-方差谱）

如何从数据估出 $V^\pi/Q^\pi$？三种范式，构成一条**偏差-方差光谱**：

| 范式 | 更新依据 | 需要模型？ | 需等终止？ | 偏差 | 方差 |
|:--|:--|:--:|:--:|:--:|:--:|
| **动态规划 (DP)** | 全期望 Bellman 回填 | 是（已知 $P$） | 否 | 0 | 0 |
| **蒙特卡洛 (MC)** | 真实整条回报 $G_t$ | 否 | 是 | 0 | 高 |
| **时序差分 (TD)** | $r+\gamma V(s')$ 自举 | 否 | 否 | 有（自举偏差） | 低 |

**TD(0)** 是现代 RL 的心脏——它把 MC 的"真实采样"与 DP 的"Bellman 自举"缝在一起：

$$
V(S_t)\leftarrow V(S_t)+\alpha\,\delta_t,\qquad
\delta_t=\underbrace{R_{t+1}+\gamma V(S_{t+1})}_{\text{TD target}}-V(S_t).
$$

$\delta_t$ 称 **TD error**。它不需要模型（不像 DP），也不必等 episode 结束（不像 MC）。代价是**自举偏差**：用一个还不准的 $V(S_{t+1})$ 去更新 $V(S_t)$。

> [!important] TD(λ)/GAE：用一个旋钮在偏差与方差间滑动
> TD(0) 只把误差分给上一个状态，传播慢；MC 方差又太大。**资格迹 (eligibility trace)** $E_t$ 给近期访问过的状态按 $\gamma\lambda$ 衰减地分配 credit：
> $$E_t(s)=\gamma\lambda E_{t-1}(s)+\mathbf 1\{s=S_t\},\qquad V(s)\leftarrow V(s)+\alpha\,\delta_t E_t(s).$$
> - $\lambda=0$：退化为单步 TD（低方差、传播慢）；
> - $\lambda=1$：逼近 MC（高方差、传播快）。
>
> 其策略梯度版本就是 **GAE (Generalized Advantage Estimation)**，PPO 的标配（§5）：$\hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}$。**$\lambda$ 是一个连续旋钮**，从 §5 的 PPO 一直拧到这里。
>
> **转笔落点**：转一圈、换指、接住这类长因果链任务，成功/失败的奖励严重滞后于真正关键的那次接触决策。$\lambda$ 越大，末端反馈越能回传给前序的"松指/补位"动作——这就是 credit assignment 的核心旋钮。把 $\lambda$ 理解为"信用回传的时间窗"，胜过死记公式。
>
> （旁注：把 $\delta_t E_t$ 看成"误差信号经一个一阶低通后再分配"，与 [[SignalProcessing]] 的指数滑动平均同形——同一个数学，两处出现。）

> [!important] 补严：GAE 为什么恰好是"偏差-方差旋钮"（一步不跳的推导）
> 上面直接给了 $\hat A_t=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}$，但"为什么 $\lambda$ 就是偏差-方差旋钮"需要把它从 **$n$ 步优势**推出来，才不留脑补。
>
> **第一步：$n$ 步优势估计量。** 用 $V$ 当基线、往前展开 $n$ 步真实奖励再接一个 bootstrap：
> $$\hat A_t^{(n)}=\underbrace{-V(s_t)+\sum_{l=0}^{n-1}\gamma^l r_{t+l}}_{\text{前 }n\text{ 步真实回报}}+\underbrace{\gamma^n V(s_{t+n})}_{\text{尾部 bootstrap}}.$$
> 符号：$r_{t+l}$＝第 $t+l$ 步即时奖励（标量，任务单位如"转过的弧度"）；$V(s)$＝状态值估计（同奖励量纲）；$\gamma^l$＝折扣（无量纲）。
>
> **第二步：$\hat A_t^{(n)}$ 就是前 $n$ 个 TD-error 的折扣和。** 代入 $\delta_{t+l}=r_{t+l}+\gamma V(s_{t+l+1})-V(s_{t+l})$，求 $\sum_{l=0}^{n-1}\gamma^l\delta_{t+l}$，其中的 $V$ 项**逐项抵消**（望远镜求和）：第 $l$ 项贡献 $+\gamma^{l+1}V(s_{t+l+1})$，第 $l{+}1$ 项贡献 $-\gamma^{l+1}V(s_{t+l+1})$，两两消去，只剩首尾 $-V(s_t)+\gamma^nV(s_{t+n})$ 与全部奖励项——恰好等于 $\hat A_t^{(n)}$。所以 $\hat A_t^{(n)}=\sum_{l=0}^{n-1}\gamma^l\delta_{t+l}$。
>
> **第三步：两端就是 TD 与 MC。** $n=1$ 时 $\hat A_t^{(1)}=\delta_t$（**低方差**——只含一个随机奖励 $r_t$；**高偏差**——整条尾巴交给还不准的 $V(s_{t+1})$）；$n\to\infty$ 时尾部 $\gamma^nV\to0$，退化为**蒙特卡洛优势**（**零偏差**——全用真实奖励；**高方差**——$n$ 个随机奖励的方差累加）。**这就是偏差-方差谱的两个端点，$n$ 是滑块。**
>
> **第四步：GAE = 对所有 $n$ 做指数加权平均，权重和塌缩成 $(\gamma\lambda)^l$。** 与其硬选一个 $n$，不如按 $\lambda$ 几何加权全体：
> $$\hat A_t^{\text{GAE}(\gamma,\lambda)}=(1-\lambda)\sum_{n=1}^{\infty}\lambda^{n-1}\hat A_t^{(n)}.$$
> 把 $\hat A_t^{(n)}=\sum_{l=0}^{n-1}\gamma^l\delta_{t+l}$ 代入、**按 $\delta_{t+l}$ 归并同类项**：$\delta_{t+l}$（带系数 $\gamma^l$）出现在所有 $n\ge l+1$ 的 $\hat A^{(n)}$ 里，故其总权重为
> $$(1-\lambda)\gamma^l\sum_{n=l+1}^{\infty}\lambda^{n-1}=(1-\lambda)\gamma^l\frac{\lambda^l}{1-\lambda}=(\gamma\lambda)^l.$$
> 于是 $\hat A_t^{\text{GAE}}=\sum_{l\ge0}(\gamma\lambda)^l\delta_{t+l}$——与上面的公式**严格一致**，且现在每个符号的来路都清楚了。$\lambda=0$ 只留 $\delta_t$（偏 TD 端）、$\lambda=1$ 回到 MC 端。**$(\gamma\lambda)^l$ 是"信用回传"的有效衰减：$\gamma$ 管"多久以后的奖励还算数"（任务折扣），$\lambda$ 管"多久以前的 TD-error 还往回分"（估计器选择）**——两个几何衰减一个管环境、一个管算法，这层区分是读懂 PPO 超参 $\lambda$ 的关键。

---

## 3. 价值方法做控制：从 Q-learning 到"过估计的诅咒"

> [!tip] 本节四拍
> **直觉**（学会 $Q$ 就能贪婪决策）→ **推导**（SARSA vs Q-learning 的一字之差）→ **对比**（on-policy 保守 vs off-policy 激进；DQN 的两大稳定器）→ **落点**（max 算子必然高估 → 这道"诅咒"催生了 §5 所有算法的 min-Q 解药）。

### 3.1 SARSA vs Q-learning：一字之差，安全两端

控制需要学动作价值 $Q(s,a)$。SARSA 与 Q-learning 只在 TD target 的"下一项"差一个字，却分出了 on/off-policy 与安全倾向：

| 方法 | TD target | 策略属性 | 行为倾向 |
|:--|:--|:--|:--|
| **SARSA** | $R+\gamma Q(S',A')$，$A'\sim\pi$ | On-policy | 把探索风险算进价值，**偏保守** |
| **Q-learning** | $R+\gamma\max_{a'}Q(S',a')$ | Off-policy | 学最优贪婪策略，**偏激进** |

> [!tip] 从"悬崖行走"到"转笔"：同一个保守/激进之分
> 经典的悬崖行走里，SARSA 因为 $\epsilon$-greedy 可能失足坠崖，会学到一条**远离崖边**的安全路；Q-learning 假设未来永远走最优，倾向**贴崖**的最短路。把这一刻搬到转笔：**SARSA 式的指步**会留出余量、不让笔逼近"即将脱手"的临界姿态；**Q-learning 式的指步**会榨干每一度旋转、贴着掉笔边界走。真机上磨损与掉落代价高，"偏保守"往往更值——这正是 §3.3 偏好"低估"的物理动机。

### 3.2 DQN：深度 RL 的起点与它的"天花板"

DeepMind 的 **DQN (2013–15)** 首次证明深度网络能稳定逼近 $Q$。两大稳定器值得记住，因为它们贯穿后续所有 off-policy 算法：

1. **经验回放 (Experience Replay)**：把 $(s,a,r,s')$ 存进 buffer 随机抽样，**打破样本时间相关性**、并让昂贵数据被反复使用（这正是 §5 SAC 样本效率高的根）。
2. **目标网络 (Target Network)**：用一份滞后参数 $\bar\theta$ 算 TD target，缓解"自举追自己尾巴"的不稳定。

> [!warning] 为什么 DQN 不能直接转笔
> DQN 只能处理**离散动作**（Atari 按键）。灵巧手的关节是**连续**的，无法枚举 $\max_a$。**如何把 DQN 的稳定训练搬到连续动作？** 这道题分出了本讲第 5 章的两条主线：
> - **Actor-Critic 线**（用一个网络近似 $\arg\max$）→ DDPG → TD3 → SAC；
> - **策略梯度 / 信任域线**（直接优化策略）→ REINFORCE → TRPO → PPO。
>
> §4 先补齐策略梯度的理论根，再在 §5 让两条线在转笔上正面对比。

### 3.3 过估计的诅咒：max 算子的"系统性偏高"

DQN 与一切含 $\max$ 的更新都背着一道诅咒。先把它讲成定理，再讲成解药。

> [!note] 先建直觉：为什么"取 max"会系统性偏高（胜者的诅咒）
> 设每个动作的估计 $Q_t(s,a)=Q^*(s,a)+\varepsilon_a$，噪声 $\varepsilon_a$ **零均值**（单个估计无偏）。要命处在于 $\max_a$ 不是"随机拿一个"，而是**专门挑出此刻看起来最大的那个**——而"看起来最大"与"这一次噪声 $\varepsilon_a$ 恰好最正"高度相关。于是 max 并不在估计真实最优值，而是在**优选噪声的正尾**：你系统性地捞起了那个"侥幸高估"的动作。这就是统计学里的**胜者的诅咒 (winner's curse / optimizer's curse)**。用 Jensen 不等式一句话看穿：$\max$ 是凸函数，故 $\mathbb E[\max_a Q_t]\ge\max_a\mathbb E[Q_t]=V^*$，等号仅在完全无噪声时成立——**只要估计带噪，取 max 后的期望就严格高于真值**。噪声越抖（方差越大）、可选动作越多，正尾越容易被捞到，偏差越狠。下面的定理正是把这句"必然偏高"精确到一个闭式数字。

> [!note] 教科书参考
> 本节定理基于 Wang & Xiong《Deep Reinforcement Learning Notes》(Tsinghua, 2024) Ch. 2.7。

> [!theorem] 过估计定理（均匀误差情形）
> 设状态 $s$ 处所有真实动作值相等 $Q^*(s,a)=V^*(s)$，估计误差 $Q_t(s,a)-Q^*(s,a)$ 独立同分布于 $[-1,1]$ 均匀分布。则
> $$\mathbb E\big[\max_a Q_t(s,a)\big]-V^*(s)=\frac{m-1}{m+1},$$
> $m$ 为动作数。**即使估计无偏（误差均值为 0），取 max 后必然偏高。**
>
> **推导（不跳步）**：令 $X_a=Q_t(s,a)-V^*(s)$，则 $\{X_a\}_{a=1}^m$ 独立同分布于 $U[-1,1]$，其 CDF 为 $F(x)=\tfrac{x+1}2$。$m$ 个 iid 的最大值 $Y=\max_a X_a$ 的 CDF 是 $F(x)^m=\big(\tfrac{x+1}2\big)^m$，密度 $f_Y(x)=\tfrac{m}2\big(\tfrac{x+1}2\big)^{m-1}$。代入换元 $u=\tfrac{x+1}2$（即 $x=2u-1$，$dx=2\,du$，$u:0\to1$）：
> $$\mathbb E[Y]=\int_{-1}^1 x\,f_Y(x)\,dx=\int_0^1(2u-1)\,m\,u^{m-1}\,du=2\cdot\frac{m}{m+1}-1=\frac{m-1}{m+1}.$$
> 因 $\mathbb E[X_a]=0$（无偏），故 $\mathbb E[\max_a Q_t]-V^*=\mathbb E[Y]=\frac{m-1}{m+1}>0$——高估幅度随动作数 $m$ 单调升、$m\to\infty$ 时趋于 1（满偏）。

> [!theorem] 更一般的过估计下界
> 若 $\sum_a(Q_t(s,a)-V^*(s))=0$ 且 $\sum_a(Q_t(s,a)-V^*(s))^2=C>0$，则
> $$\max_a Q_t(s,a)\ge V^*(s)+\sqrt{\tfrac{C}{m-1}}.$$
> **高估幅度 $\propto$ 估计方差 $\sqrt C$**（估计越抖、高估越狠），$\propto 1/\sqrt{m-1}$（动作越多越摊薄）。

**这道诅咒在转笔里有真实后果**：接触瞬态会让某些状态的 $Q$ 估计剧烈波动（$C$ 大），$\max$ 把"一次侥幸的猛甩"误判成高价值动作，策略据此施加**危险的大力矩**——轻则掉笔，重则损伤电机。

> [!important] 解药的种子（贯穿 §5）
> **Double Q-learning** 把"选动作"与"评价值"解耦，从机制上消除这种必然高估；其深度版的两个化身——**TD3 的 clipped double-Q（取 $\min$）** 与 **SAC 的双 Q 取 $\min$**——是第 5 章的主角。请记住这条因果：**max 高估（本节）→ 取 min 低估（§5）→ 低估在机器人上更安全（§3.1 的保守倾向）**。三节一线。

---

## 4. 策略梯度：在不可微世界中更新策略

> [!tip] 本节四拍
> **直觉**（接触求解器不可微，怎么求"奖励对策略参数的梯度"？）→ **推导**（log-derivative 技巧，看环境模型如何神奇消失）→ **对比**（REINFORCE → baseline → advantage → Actor-Critic 的诞生）→ **落点**（高方差 + 一次性 + 步长敏感，催生 §5 两条主线）。

### 4.1 策略梯度定理：log-derivative 技巧

§3 的价值方法绕不开 $\max_a$，对连续的 24 维动作无法枚举。**策略梯度**改走另一条路：把策略 $\pi_\theta$ 直接参数化，对期望回报求梯度、做梯度上升。目标函数：

$$
J(\theta)=\mathbb E_{\tau\sim p_\theta(\tau)}\Big[\textstyle\sum_{t} r(s_t,a_t)\Big]=\int p_\theta(\tau)\,r(\tau)\,d\tau.
$$

难点：$\tau$（轨迹）的分布 $p_\theta$ 含有**不可微的环境转移**（接触 LCP 求解器）。怎么对它求 $\nabla_\theta$？

> [!theorem] 策略梯度定理 (Policy Gradient Theorem)
> $$\nabla_\theta J(\theta)=\mathbb E_{\tau\sim p_\theta}\Big[\sum_{t}\nabla_\theta\log\pi_\theta(a_t\mid s_t)\cdot\Big(\sum_{t'\ge t} r(s_{t'},a_{t'})\Big)\Big].$$
>
> **证明骨架（log-derivative 恒等式）**：$\nabla_\theta p_\theta(\tau)=p_\theta(\tau)\,\nabla_\theta\log p_\theta(\tau)$。展开轨迹对数似然：
> $$\log p_\theta(\tau)=\log p(s_1)+\sum_t\big[\log\pi_\theta(a_t\mid s_t)+\log p(s_{t+1}\mid s_t,a_t)\big].$$
> 对 $\theta$ 求导时，**初始分布 $\log p(s_1)$ 与转移 $\log p(s_{t+1}\mid s_t,a_t)$ 都与 $\theta$ 无关，导数为零而消失**。

> [!important] 这一步消失，是整个领域得以成立的原因
> 环境模型 $p(s'\mid s,a)$ 在梯度里**整项蒸发**——这意味着：**哪怕接触动力学完全不可微、完全未知，我们仍能用采样无偏地估计策略梯度。** 这正是 §1.4 解析控制"卡在 LCP 求解器"时，RL 能绕过去的根本数学原因。把这句话刻进脑子：**策略梯度只需要"能采样"，不需要"能微分环境"。**

**因果性修正 (reward-to-go)**：$t$ 时刻的动作不影响 $t'<t$ 的奖励，故可用 $\hat Q_t=\sum_{t'\ge t}r(s_{t'},a_{t'})$ 替换全轨迹回报——**降方差且不引偏**。

### 4.2 REINFORCE：最朴素的实现

1. 用当前 $\pi_\theta$ 采 $N$ 条轨迹；
2. 估梯度 $\nabla_\theta J\approx\frac1N\sum_i\sum_t\nabla_\theta\log\pi_\theta(a_{i,t}\mid s_{i,t})\,\hat Q_{i,t}$；
3. 上升 $\theta\leftarrow\theta+\alpha\nabla_\theta J$。

直觉：**把"高回报轨迹里出现过的动作"的概率推高**。转笔里，一条侥幸转成的轨迹会让其中所有"松指/补位"动作的概率被整体抬升——哪怕其中有几步其实是败笔。这种"一好遮百丑"正是高方差的来源。

### 4.3 方差控制：从 baseline 到 Advantage，Actor-Critic 的诞生

> [!tip] 基线 (baseline)：不改期望，狂降方差
> 减去一个与动作无关的基线 $b(s)$：
> $$\nabla_\theta J=\mathbb E\big[\nabla_\theta\log\pi_\theta(a\mid s)\,(\hat Q-b(s))\big].$$
> **无偏性**：$\mathbb E[\nabla_\theta\log\pi_\theta(a\mid s)\,b(s)]=b(s)\int\nabla_\theta\pi_\theta(a\mid s)\,da=b(s)\nabla_\theta 1=0$。
> 最优基线取 $b(s)=V^\pi(s)$，于是 $\hat Q-V^\pi=\hat A^\pi$——**优势函数 (Advantage)** 登场。

优势函数 $A^\pi(s,a)=Q^\pi(s,a)-V^\pi(s)$ 回答的是相对问题：**"这个动作比该状态下的平均水平好多少？"** 这比绝对回报稳定得多。把"用一个学出来的 Critic $V_\phi$ 当基线"这件事坐实，就得到 **Actor-Critic** 架构：

- **Actor** $\pi_\theta$：出动作；
- **Critic** $V_\phi$（或 $Q_\phi$）：评价值、当基线。

> [!note] 一张图看清两个 §2 概念在这里合流
> Critic 用 §2.3 的 **TD/GAE** 来训练（拟合 $V^\pi$）；Actor 用本节的**策略梯度**、以 Critic 给的优势为权重来更新。**GAE 的 $\lambda$ 旋钮（§2.3）此刻就插在 Actor 的优势估计上**——这就是为什么 PPO 既要 GAE 又要策略梯度。前后两章在此咬合。

### 4.4 落点：REINFORCE 的三宗罪，催生两条主线

| 罪 | 表现 | 解法 → 章节 |
|:--|:--|:--|
| **高方差** | 即便有 baseline，MC 估计仍抖 | Critic 替代 MC 回报 → Actor-Critic / Off-policy（§5.2） |
| **一次性 (on-policy)** | 采的数据只能用一次，样本效率极低 | replay 重用 → DDPG/TD3/SAC（§5.2）；信任域内重要性采样 → PPO（§5.1）|
| **步长敏感** | 步子大→崩、小→慢 | 约束更新幅度 → TRPO/PPO（§5.1）|

> [!important] 承上启下
> 注意"一次性"这宗罪有**两种**修法，正对应 §5 的两条主线：**信任域线**（PPO，老实做 on-policy 但在小信任域内借一点重要性采样）与**off-policy 复用线**（SAC，把数据塞进 replay 反复榨取）。下一章我们先立一个**统一框架**把两条线收编，再让它们在转笔上正面对决。

---

## 5. 两条主线的分野：On-policy 信任域 vs Off-policy 复用【全讲对比脊柱】

> [!tip] 本章四拍（这是全讲最重要的对比章）
> **直觉**（所有现代策略优化都在做同一件事：在"参考分布"附近改进策略）→ **推导**（先立统一框架，再分别推 TRPO/PPO 与 DDPG/TD3/SAC）→ **对比**（让五个算法在转笔上同台，照出各自灵魂）→ **联系**（熵↔[[ControlTheory|阻抗柔顺]]、信任域↔[[Optimization|近端算法]]、min-Q↔§3.3）。

### 5.0 先立统一框架：一切都是"在参考分布附近改进"

> [!abstract] 一个目标，收编四种算法
> 考虑带正则的策略优化目标——在最大化价值的同时，不要离一个**参考分布 (reference distribution)** $\pi_0$ 太远：
> $$\max_\pi\ \mathbb E_{a\sim\pi}[Q(s,a)]-\beta\,D_{KL}\big(\pi(\cdot\mid s)\,\|\,\pi_0(\cdot\mid s)\big).$$
> 用变分法解它（不跳步）：把归一化约束 $\int\pi(a\mid s)\,da=1$ 用乘子 $\nu$ 挂上，构造 Lagrangian
> $$\mathcal L=\int\pi(a\mid s)\Big[Q(s,a)-\beta\log\tfrac{\pi(a\mid s)}{\pi_0(a\mid s)}\Big]da+\nu\Big(\int\pi(a\mid s)\,da-1\Big).$$
> 对 $\pi(a\mid s)$ 求泛函导数并令其为零：$Q(s,a)-\beta\big(\log\tfrac{\pi(a\mid s)}{\pi_0(a\mid s)}+1\big)+\nu=0$。解出 $\log\pi=\log\pi_0+\tfrac{Q}{\beta}+\big(\tfrac{\nu}{\beta}-1\big)$，最后一项与 $a$ 无关、被归一化常数 $Z(s)$ 吸收，即得最优策略的 **Boltzmann 形式**：
> $$\boxed{\ \pi^*(a\mid s)=\frac{\pi_0(a\mid s)\,\exp\!\big(Q(s,a)/\beta\big)}{Z(s)}\ }$$
> **关键洞见：不同 RL 算法的本质差异，只在于"参考分布 $\pi_0$ 选谁"和"温度 $\beta$ 怎么调"。**
>
> | 选择 $\pi_0$ | 得到的算法 | 含义 |
> |:--|:--|:--|
> | **均匀分布** | **SAC**（§5.2） | 对动作无先验偏好 → $D_{KL}(\pi\|\mathrm{Unif})=-H(\pi)+c$，**KL 退化成熵正则** |
> | **旧策略 $\pi_{old}$** | **TRPO/PPO**（§5.1） | "信任旧策略" → KL 约束 = 信任域 |
> | **专家/物理先验** | **π₀ / RLPD / 残差 RL**（§5.2, §9） | 把演示或物理直觉当锚 |
>
> 记住这张表，第 5 章后面所有推导都只是它的特例。**这是本讲"用一个框架串起一片算法"的最佳范例。**

> [!note] 跨原理联系
> 这个"$Q$ − $\beta$·KL-到-参考"的形式，与 [[ControlTheory#10. 稳定性理论的统一基石|控制论的正则化最优控制]]、[[Optimization#2. 优化的语言：可行域、目标、对偶与 KKT|凸优化的近端算子 (proximal operator)]] 完全同构——"目标 − 到锚点的距离惩罚"是近端方法的通用骨架。LLM 后训练里的 RLHF/DPO 也是这个式子（$\pi_0=$ SFT 模型）。**一个变分式，跨越控制、优化、RL、LLM 四个领域。**

### 5.1 On-policy 信任域线：TRPO → PPO（$\pi_0=\pi_{old}$）

#### 5.1.1 TRPO：把"步长敏感"变成"信任域约束"

§4.4 说 REINFORCE 步长敏感。TRPO 的根治办法，是先把策略改进写成**严格的提升量**：

> [!theorem] 性能差分引理 (Performance Difference Lemma)
> $$J(\pi_{\theta'})-J(\pi_\theta)=\mathbb E_{\tau\sim p_{\theta'}}\Big[\sum_t\gamma^t A^{\pi_\theta}(s_t,a_t)\Big].$$
> **直觉**：新策略的提升量 = 用**旧策略的价值观** $A^{\pi_\theta}$ 去评判**新策略所走的轨迹**。

可这右边的期望是关于**新策略状态分布** $p_{\theta'}$ 的，而我们只有旧策略的数据 $p_\theta$。用重要性采样换到旧分布后，问题归结为"能否用 $p_\theta(s)$ 近似 $p_{\theta'}(s)$"。答案：

> [!theorem] 分布间隙界 (Distribution Gap Bound)
> 若 $\max_s D_{KL}(\pi_\theta(\cdot\mid s)\,\|\,\pi_{\theta'}(\cdot\mid s))\le\epsilon$，则状态分布间隙 $|p_{\theta'}(s_t)-p_\theta(s_t)|\le O(\sqrt\epsilon\cdot t)$。

**这就是"信任域"三个字的来历**：只要新旧策略 KL 足够近，用旧数据近似新目标在理论上就是合法的。于是 TRPO 解一个带约束的子问题：

$$
\max_\theta\ \mathbb E\Big[\tfrac{\pi_\theta(a\mid s)}{\pi_{\theta_{old}}(a\mid s)}A(s,a)\Big]\quad\text{s.t.}\quad D_{KL}(\pi_{\theta_{old}}\|\pi_\theta)\le\delta.
$$

代价：要算 Fisher 信息矩阵的逆（自然梯度），计算重。

#### 5.1.2 PPO：用 clip 把硬约束"软化"

PPO 的核心创新，是用一个**截断 (clip)** 替代 TRPO 的硬 KL 约束——工程上简单一个数量级：

$$
L^{CLIP}(\theta)=\mathbb E\Big[\min\big(r_t(\theta)\hat A_t,\ \mathrm{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\hat A_t\big)\Big],\quad r_t(\theta)=\tfrac{\pi_\theta(a_t\mid s_t)}{\pi_{\theta_{old}}(a_t\mid s_t)}.
$$

> [!tip] PPO clip 的转笔直觉
> Clip 在说："**新策略别离旧策略太远——离远了，这一步就不奖励你了。**" $\epsilon=0.2$ 即概率比最多变 20%。落到转笔：策略已经学会了一套精妙的指步**时序**（松指→补位→推动的毫秒级配合），一次过大的更新会把这套时序整体打乱、前功尽弃。Clip 就是那条"别一次毁掉已学会的指步"的护栏。

> [!important] 补严：clip 与信任域的精确关系（min、单侧生效、悲观下界）
> "clip=软化的信任域"常被一带而过，其实要拆成三件互相咬合的事，才不留跳步。
>
> **(1) $\min$ 把 $L^{CLIP}$ 变成未截断目标的悲观下界。** 记未截断代理 $L^{IS}_t=r_t(\theta)\hat A_t$。由于 $L^{CLIP}_t=\min\big(r_t\hat A_t,\ \mathrm{clip}(r_t,1{-}\epsilon,1{+}\epsilon)\hat A_t\big)\le r_t\hat A_t$ **逐样本成立**，故 $L^{CLIP}\le L^{IS}$ 恒成立。优化一个**下界**意味着：算法只在"连最悲观的估计都说该改"时才迈步——这正是保守性的数学来源，与 TRPO"保证单调提升"同一动机（回扣 §5.1.1 的性能差分引理）。
>
> **(2) clip 是"单侧"的，方向由 $\hat A_t$ 符号决定。** 逐符号拆开（$r_t>0$ 恒成立，因是概率比）：
> - $\hat A_t>0$（好动作，想抬概率）：目标为 $\min(r_t,\,1{+}\epsilon)\hat A_t$。一旦 $r_t>1{+}\epsilon$，取到常数 $1{+}\epsilon$，对 $\theta$ **梯度归零**——不再奖励"把好动作概率推得更高"，堵住过冲。但若 $r_t<1{-}\epsilon$（这一步反而把好动作压低了），$\min$ 取回 $r_t\hat A_t$，**梯度仍在**，允许纠回。
> - $\hat A_t<0$（坏动作，想压概率）：对称地，$r_t<1{-}\epsilon$ 时梯度归零（别把坏动作压得过狠），$r_t>1{+}\epsilon$ 时梯度仍在。
>
> 关键：**clip 只在"更新已经朝着扩大差距、且再走会过界"的那一侧断梯度**；朝"收回"的一侧永远留着梯度。这解释了为何 PPO 不像 TRPO 那样对称地硬约束 KL，却仍稳。
>
> **(3) 与 KL 信任域的精确差别——为什么 clip 不完全等价于 TRPO。** TRPO 约束的是**分布级平均** $\bar D_{KL}(\pi_{old}\|\pi_\theta)\le\delta$；clip 约束的是**逐样本似然比** $r_t\in[1{-}\epsilon,1{+}\epsilon]$。二者的桥梁：$D_{KL}\approx\tfrac12\mathbb E[(\log r_t)^2]$（KL 的二阶展开），而 $r_t\in[1{-}\epsilon,1{+}\epsilon]\Rightarrow|\log r_t|\lesssim\epsilon$，故 clip 把每个样本的 $(\log r_t)^2$ 压在 $\epsilon^2$ 量级——**这是对 KL 的逐点一阶代理，不是全局约束**。缺口有二：① 梯度归零 ≠ 参数不动，一次大步仍可能把**某些样本**推出 $[1{-}\epsilon,1{+}\epsilon]$（clip 只让它们不再贡献梯度，管不住已迈出的步）；② 平均 KL 可能因少数样本失控。**正因为 clip 不硬保 KL，工程实现才要再叠一层"KL 自适应学习率"**（见下方 warning）——clip 管"单样本别太离谱"、自适应 LR 管"整体 KL 别漂太快"，两者合起来才凑出 TRPO 那个信任域，这就是后文"软信任域"一词的确切含义。

PPO 的总损失是三项之和——策略、价值、熵：

$$
L^{CLIP+VF+S}_t(\theta)=\hat{\mathbb E}_t\big[L^{CLIP}_t(\theta)-c_1 L^{VF}_t(\theta)+c_2\,S[\pi_\theta](s_t)\big].
$$

| 组成 | 网络 | 拟合目标 | 作用 |
|:--|:--|:--|:--|
| **Policy Loss** $L^{CLIP}$ | Actor | 优势 $\hat A_t$ | 抬高高回报动作概率，clip 保稳 |
| **Value Loss** $L^{VF}$ | Critic | 回报 $G^{target}_t$ | 提供准确基线，降策略梯度方差 |
| **Entropy Bonus** $S$ | Actor | 最大化随机性 | 维持探索，防过早坍缩 |

> [!warning] 核心洞察：三段数据流与梯度属性（实现 PPO 的命门）
> PPO 的变量产生于**三个不同阶段**，梯度属性截然不同（detached 常量 vs 可导变量）：
> - **阶段 1 — Rollout**（参数冻结在 $\theta_{old}$，**全部 detached**）：观测 $s_t$、采样动作 $a_t\sim\mathcal N(\mu_{\theta_{old}}(s_t),\sigma)$、**当场存下** $\log\pi_{\theta_{old}}(a_t\mid s_t)$（网络一更新就再也取不到旧分布值）、基线 $V_{\theta_{old}}(s_t)$、奖励与终止 $r_t,d_t$。
> - **阶段 2 — Advantage**（离线后处理，仍是常量）：用 GAE 反向遍历 buffer 算 $\hat A_t$，$G^{target}_t=\hat A_t+V_{\theta_{old}}(s_t)$。
> - **阶段 3 — Update**（重建计算图，$\theta$ 开始动）：把缓存的 $s_t$ 喂进**更新中的** Actor 得 $\pi_\theta(a_t\mid s_t)$，算比率 $r_t(\theta)=\exp(\log\pi_\theta-\log\pi_{\theta_{old}})$（log-exp 技巧防数值不稳）、$V_\theta(s_t)$、熵 $S[\pi_\theta]$。

> [!note] 补严：critic 的监督目标为何取 $G^{target}_t=\hat A_t^{\text{GAE}}+V_{\theta_{old}}(s_t)$（"value 拟合 $\lambda$-return 保低方差"的确切含义）
> 阶段 2 里的 $G^{target}_t$ 不是随手拼的。把它展开：因为 $\hat A_t^{\text{GAE}}=G_t^{(\lambda)}-V_{old}(s_t)$（优势＝回报减基线），两式相加 $V_{old}$ 抵消，剩下的正是 §2.3 那个 **$\lambda$-return** $G_t^{(\lambda)}$。于是 critic 拟合的既不是纯 MC 回报 $\sum_l\gamma^l r_{t+l}$（$\lambda=1$：无偏，但方差随 horizon 累加），也不是纯单步 TD 目标 $r_t+\gamma V_{old}(s_{t+1})$（$\lambda=0$：方差最小，却把整条尾巴押在还不准的 $V_{old}$ 上、偏差大），而是 $\lambda\approx0.95$ 的**混合目标**——用 rollout 里的**真实奖励** $r_t,r_{t+1},\dots$ 修偏差、用 $V_{old}$ 对尾部**自举**截断随机链降方差。这就是"用 $\lambda$-return 而非裸回报监督 $V$ 以保低方差"的确切含义：**同一个 $\lambda$ 旋钮，§2.3 调 advantage 的偏差-方差，这里调 critic 目标的偏差-方差**，是一根旋钮的两处复用。
> **易漏的梯度细节**：$G^{target}_t$ 里的 $V_{old}(s_t)$、$\hat A_t$ 都是阶段 1/2 缓存的 **detached 常量**，反向传播只经**新** $V_\theta(s_t)$ 回传；若误把目标里的 $V$ 也接上计算图（让目标随参数漂移），critic 会"自举到自己身上"而失稳——这是与"value clipping"并列的第二道防自举护栏。

```python
# PPO Update — 核心张量操作 (PyTorch)
def compute_ppo_loss(obs, actions, old_log_probs, advantages, returns,
                     actor_critic, clip_param=0.2, c1=0.5, c2=0.01):
    # 阶段3: 重新前向传播，建立计算图
    action_dist, new_values = actor_critic(obs)
    new_log_probs = action_dist.log_prob(actions).sum(dim=-1)  # ⚠️ 多维动作必须在 dim=-1 求和
    entropy = action_dist.entropy().sum(dim=-1).mean()

    ratio = torch.exp(new_log_probs - old_log_probs)           # log-exp 技巧
    surr1 = ratio * advantages
    surr2 = torch.clamp(ratio, 1.0 - clip_param, 1.0 + clip_param) * advantages
    policy_loss = -torch.min(surr1, surr2).mean()

    value_loss = (returns - new_values.squeeze(-1)).pow(2).mean()
    total_loss = policy_loss + c1 * value_loss - c2 * entropy
    return total_loss
```

> [!note] 为什么说 PPO"宏观 on-policy，微观带 off-policy 影子"
> 一次 `train_epoch` 里，rollout 用固定的 $\theta_{old}$ 采集；随后多个 mini-epoch 反复用同一批 storage。第一轮更新后当前策略已是 $\theta\ne\theta_{old}$，故需重要性比率 $r_t(\theta)$ 校正。PPO 仍属 **on-policy**——rollout 结束旧数据即丢弃，不像 SAC/DQN 长期进 replay；但它在一个很短的信任域内借用了 off-policy 的重要性采样来复用样本。**这正好坐实 §5.0：PPO 就是 $\pi_0=\pi_{old}$ 的那一行。**

> [!warning] 工程实现常比论文多两层保护（灵巧操作避坑）
> - **Value clipping**：$V_{clip}=V_{old}+\mathrm{clip}(V_\theta-V_{old},-\epsilon,\epsilon)$，critic loss 取 unclipped/clipped MSE 的**较大值**，防 value 在旧数据上暴走。
> - **Bounds loss**：对 actor 均值 $\mu$ 超出软边界（如 $[-1.1,1.1]$）的部分加二次罚，避免高斯均值长期落在 action clamp 外、采样大面积饱和。
> - **KL 自适应学习率**：每个 mini-epoch 估新旧 $D_{KL}$，漂移过快就降 LR——与 clip 共同构成"软信任域"。
> - **三个数值陷阱**：① 24-DoF 的 `log_prob` 必须 `.sum(dim=-1)`（联合概率=各维 log 之和），漏掉会静默学出废策略；② advantage 必须 minibatch 归一化 `(adv-mean)/(std+1e-8)`，否则步长失控、Actor 易崩；③ 熵系数 $c_2$ 过小→手指陷入无效颤动。

> [!danger] 失败模式：稀疏接触任务上 PPO 的"熵套利 → Bang-Bang → 梯度虚胖"三联征（Thumbaround 实录）
> 上面的 bounds loss 与熵系数 $c_2$ 不是可有可无的旋钮——在**转笔 (Thumbaround)** 这类奖励极稀疏、又**力矩饥饿 (torque starvation)** 的接触任务上，配错它们会让 PPO 掉进一个自洽的**奖励作弊 (reward hacking)** 陷阱。分三步看清因果链（每步给理想公式 + 实测曲线特征）：
>
> **(1) 力矩饥饿逼出 Bang-Bang 策略。** 若控制增益 $P_{gain}$ 过低（如 $6.4$）、动作缩放偏小，只有 $|a|\!\to\!1$（满舵）产生的冲量才够突破静摩擦让笔起转——这是 [[ContactMechanics|接触]] 的门槛非线性。从**最优控制**看，最短时间/脉冲驱动问题的解本就是 **Bang-Bang（在 $\pm1$ 间开关）**（[[Optimization|庞特里亚金极值原理]]的边界解），所以 PPO 把高斯均值 $\mu$ 推向边界并没错。
>
> **(2) clamp + 无 bounds loss → 熵套利，$\mu$ 无界漂移（危险信号）。** 实际动作 $a_{real}=\mathrm{clamp}(\mu+\sigma\epsilon,-1,1)$。一旦 $\mu\gg1$（实测能飙到 $20$ 量级），即便 $\sigma$ 涨得很大，采样几乎恒被 clamp 成 $+1$——**物理输出不变（任务奖励不掉），可微分熵 $H=\sum_i\ln(\sigma_i\sqrt{2\pi e})$ 却随 $\sigma$ 无限涨**。若 $c_2>0$ 而 $\texttt{bounds\_loss\_coef}=0$，优化器会发现"增大 $\sigma$、同步把 $\mu$ 推更远保命"是降 total loss 最省力的方向——**entropy 近线性狂涨（如 $20\!\to\!26$）就是这个套利的指纹**，而非健康探索；同时 actor loss 贴 $0$ 微负震荡（$\mu$ 卡在饱和区，$\partial\text{reward}/\partial\mu\approx0$，梯度消失）。治法正是上面那条 bounds loss：罚 $|\mu|>1.1$，堵死漂移，套利立刻终结。
>
> **(3) 收敛末期反转：$\sigma$ 收缩 → 梯度被 $1/\sigma^2$ 放大（健康信号）。** 修好 (2) 后策略真收敛，$\sigma$ 缩小（连续控制用**微分熵**，当 $\sigma<\tfrac1{\sqrt{2\pi e}}\approx0.24$ 时 $H$ 变负——**负熵是"自信"而非报错**）。此时高斯对数似然对均值的梯度 $\nabla_\mu\log\pi=\tfrac{a-\mu}{\sigma^2}$ 分母变小，**同样的优势下原始梯度范数被 $1/\sigma^2$ 放大**（$\sigma:1\!\to\!0.2$ 即 $\times25$）——所以 grad-norm 缓涨（如 $34\!\to\!38$）是"策略对细微误差极敏感、在精修最后 10%"的正常现象，被 `grad_norm` 裁剪当安全带勒住即可，**不是发散**。
>
> **一句话诊断法**：entropy 单调涨 + actor loss 贴 $0$ 震荡 + $\mu$ 冲出 $[-1,1]$ ＝**病态熵套利**（治本：提 $P_{gain}$ 解力矩饥饿；止损：开 bounds loss、clamp `log_std` 上限）；entropy 转负 + grad-norm 缓涨 + critic loss 稳定小 ＝**健康收敛末期**。**同一条 grad-norm 上涨曲线，病因可以完全相反——必须结合 entropy 的符号一起读。**（补：critic loss 稳在某个非零小值也正常——$8\%\!\to\!90\%$ 成功率下存在**状态混叠 (state aliasing)**：极相似的 $s^o$ 因物理噪声一成一败，Bellman 目标天差地别，构成不可约的 irreducible error。）

> [!important] PPO 的单峰高斯局限（直接通向 §10 扩散策略）
> PPO 默认输出对角高斯 $\mathcal N(\mu(s),\sigma)$，是**单峰**的。转笔"可左转可右转"是**多峰**——单峰高斯会拟合到两峰之间的均值（"直接撞上去"），学出无效动作。为什么不直接换多峰分布？
>
> | 替代 | 理论障碍 |
> |:--|:--|
> | **Diffusion** | 无法精确算 $\log p_\theta(a\mid s)$（只有 ELBO 或昂贵 ODE），$r_t(\theta)$ 巨偏 |
> | **GMM** | 高维下混合密度数值下溢、梯度爆炸 |
> | **Normalizing Flows** | 有精确 log-prob，但雅可比行列式开销大 |
>
> 当前灵巧操作的绕法：**放弃 PPO 框架直接用条件扩散做行为克隆**（[[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|扩散策略]]，§10 详述）、课程引导避开多峰区、或**层级策略**（高层离散选模态、低层单峰高斯执行）。**"单峰 vs 多峰"这条线，从 PPO 一直牵到 §10。**

---

### 5.2 Off-policy 复用线：DDPG → TD3 → SAC（$\pi_0=$ 均匀 / 物理先验）

这条线的执念只有一个：**昂贵的真机数据，凭什么只用一次？** 它用 replay buffer 反复榨取历史数据，样本效率比 PPO 高一个数量级——对真机训练是生死攸关的。

#### 5.2.0 先扫雷：Off-policy Actor-Critic 的两个理论谬误

> [!note] 教科书参考
> 本节基于 Wang & Xiong《Deep Reinforcement Learning Notes》Ch. 4.4。从 replay 里取数据做 AC，有两个一不小心就踩的坑。

**谬误一：目标值里的策略不一致。** 朴素写法 $y_i=r_i+\gamma V(s'_i)$ 错在哪？从 buffer 取的 $(s,a,s',r)$ 里，$s'$ 是**旧策略**走出来的，而 $V$ 要的是**当前策略** $\pi_\theta$ 的值。**修正**：改用 $Q$（因为 $Q^\pi(s,a)$ 不要求 $a$ 来自 $\pi$）：
$$y_i=r_i+\gamma\,\hat Q^\pi(s'_i,a'_i),\qquad a'_i\sim\pi_\theta(\cdot\mid s'_i).$$
注意 $a'_i$ 是把 $s'_i$ 喂进**最新策略网络**现采的，不是 buffer 里存的历史动作。

**谬误二：策略梯度里的动作不一致。** 策略梯度要求 $a\sim\pi_\theta$，但 buffer 里的动作来自旧策略。**修正**：对每个采样状态 $s_i$，从当前策略**重新采** $a^\pi_i\sim\pi_\theta(\cdot\mid s_i)$，再算 $\nabla_\theta\log\pi_\theta(a^\pi_i\mid s_i)\hat Q^\pi(s_i,a^\pi_i)$。

> [!tip] 为什么这里用 $Q$ 而不用优势？
> 不减 baseline 会增方差，但这里高方差**可接受**——重采 $a^\pi_i$ 只需前向过一次网络、**无需与仿真器交互**，于是可以大量采样压方差，而不增加昂贵的环境交互成本。这正是 off-policy 的红利。

#### 5.2.1 DDPG (2015)：连续动作的 Actor-Critic，但脆

用确定性策略 $a=\mu_\theta(s)$ 近似 $\arg\max_a Q$，于是把 DQN 搬到了连续动作。**但它在灵巧操作上很脆**——根源正是 §3.3 的**过估计诅咒**：接触瞬态让 $Q$ 估计剧烈波动，$\max$ 式更新把"侥幸猛甩"放大成高价值，Critic 误差正反馈式爆炸、策略崩溃。

#### 5.2.2 TD3 (2018)：三剂解药，让它变得可用

> [!important] TD3 = DDPG + 三个针对性修补（每一个都对应一种灵巧操作病）
> 1. **Clipped Double-Q**：训两个 Critic，目标取 $\min(Q_1,Q_2)$。
>    - *为什么*：直接落实 §3.3 的解药。**在灵巧操作里，低估比高估安全**——低估只是学得慢，高估会让策略施加危险大力矩。宁可保守。
> 2. **Target Policy Smoothing**：目标动作加噪 $\epsilon\sim\mathrm{clip}(\mathcal N(0,\sigma),-c,c)$。
>    - *为什么*：物理上是在找**宽极小 (flat minima)**。若某指步只在 0.1mm 精度下有效、0.2mm 偏差就失败，它就是不可用的。平滑迫使 RL 学**对执行误差鲁棒**的动作。
> 3. **Delayed Policy Update**：Critic 更新数次，Actor 才更新一次——让 Critic 先稳，再引导 Actor。

```python
def train_critic(self, replay_buffer):
    state, action, next_state, reward, not_done = replay_buffer.sample()
    with torch.no_grad():
        # Target Policy Smoothing: 模拟执行误差。若动作加微扰后 Q 骤降，
        # 说明它在"尖峰"上、不稳定。TD3 借此平滑 Q 函数。
        noise = (torch.randn_like(action) * self.policy_noise).clamp(-self.noise_clip, self.noise_clip)
        next_action = (self.actor_target(next_state) + noise).clamp(-self.max_action, self.max_action)
        # Clipped Double-Q: 取 min 抑制高估
        target_Q = torch.min(self.critic_target_1(next_state, next_action),
                             self.critic_target_2(next_state, next_action))
        target_Q = reward + not_done * self.discount * target_Q
    # ... 用 MSE(critic(state, action), target_Q) 更新两个 Critic ...
```

> [!tip] 转笔落点
> 在笔面上滑动指尖时，摩擦力突变会让状态剧烈抖动。Target Smoothing 相当于在 Critic 更新里加了个**低通滤波**（又一次与 [[SignalProcessing]] 同形！），滤掉接触瞬态的高频噪声，让 Critic 学到更本质的物理规律，而非追逐每一次摩擦毛刺。

#### 5.2.3 SAC：黄金标准与"熵即柔顺"

SAC 是 §5.0 统一框架中 **$\pi_0=$ 均匀分布** 那一行——KL 退化成熵正则，目标变成"最大化回报 + 策略熵"：

$$
J(\pi)=\sum_t\mathbb E\big[r_t+\alpha\,H(\pi(\cdot\mid s_t))\big].
$$

**(a) 软值函数与软 Bellman 方程。** 把标准 RL 里所有 $\max$ 换成 soft-max（log-sum-exp），熵就自然长出来：

$$
V^\pi_{soft}(s)=\mathbb E_{a\sim\pi}\big[Q^\pi_{soft}(s,a)-\alpha\log\pi(a\mid s)\big],\qquad
Q^\pi_{soft}(s,a)=r(s,a)+\gamma\,\mathbb E_{s'}\big[V^\pi_{soft}(s')\big].
$$

> [!theorem] 软 Bellman 最优方程 + 软策略迭代收敛
> 最优软策略具 Boltzmann 形式 $\pi^*(a\mid s)\propto\exp(Q^*_{soft}(s,a)/\alpha)$（即 §5.0 框架取 $\pi_0=$ 均匀的特例），代入得
> $$Q^*_{soft}(s,a)=r(s,a)+\gamma\,\mathbb E_{s'}\Big[\alpha\log\sum_{a'}\exp\big(Q^*_{soft}(s',a')/\alpha\big)\Big].$$
> **软策略迭代**（交替软策略评估与改进 $\pi'(a\mid s)=\exp(Q^\pi_{soft}/\alpha)/Z$）满足 $Q^{\pi'}_{soft}\ge Q^\pi_{soft}$ 单调，收敛到唯一最优。这把 §2.2 的 Bellman 收敛理论平滑地推广到了带熵的情形。

**(b) 三个可学组件。** 软 Q 网络（最小化软 Bellman 残差）、策略网络（最大化期望软 Q，需**重参数化**才能反传梯度）、自动温度 $\alpha$（约束优化）。

```python
class GaussianPolicy(torch.nn.Module):
    # ... linear1/linear2 → mean_linear, log_std_linear ...
    # 物理意义：LOG_STD 上限过大→电机高频抖动；下限过小→策略僵死无法探索
    LOG_STD_MAX, LOG_STD_MIN = 2, -20
    def sample(self, state):
        mean, log_std = self.forward(state)
        std = log_std.clamp(self.LOG_STD_MIN, self.LOG_STD_MAX).exp()
        normal = Normal(mean, std)
        x_t = normal.rsample()                  # ★ Reparameterization: a=μ+σ⊙ε，梯度可穿过采样
        y_t = torch.tanh(x_t)                   # 压到关节极限 [-1,1]
        log_prob = normal.log_prob(x_t)
        log_prob -= torch.log(1 - y_t.pow(2) + 1e-6)   # tanh 变量替换的 Jacobian 修正
        return y_t, log_prob.sum(1, keepdim=True), mean
```

> [!note] 重参数化为什么对灵巧操作至关重要
> `rsample` 让策略网络能"感知"到：**在某方向减小方差 $\sigma$，Q 会怎么变**。插销入孔 (peg-in-hole) 的瞬间，网络会**自动学会急剧收紧方差**以提精度。这把"随机策略"和"按需变精确"统一了起来。

```python
# Automatic Entropy Tuning：把"该多探索"变成对偶梯度下降
self.target_entropy = -float(action_dim)        # 目标熵 H̄，经验值 -dim(A)
alpha_loss = -(self.log_alpha * (log_prob + self.target_entropy).detach()).mean()
# 负反馈方向（勿记反，记反即正反馈发散）：
# 策略过自信、熵低于 H̄ → (log_prob+H̄)>0 → log_α 被上推 → α 升 → 加大熵压、拉回探索(柔)
# 策略过随机、熵高于 H̄ → (log_prob+H̄)<0 → α 降 → 松开熵压、允许收敛确定(刚)
```

> [!important] 补严：自动温度 $\alpha$ 是熵约束的对偶变量（一步不跳的对偶推导）
> 上面代码把 $\alpha$ 更新写成一行，但"为什么是这一行、$\alpha$ 到底是什么"需要从**约束优化**推出来才不留脑补。
>
> **第一步：把 SAC 目标写成硬约束问题。** 不再无脑最大化"回报+熵"，而是要求策略在**每个时刻的平均熵不低于一个下限** $\bar{\mathcal H}$（防止它为多拿回报而彻底坍缩成确定策略）：
> $$\max_{\pi}\ \mathbb E\Big[\sum_t r_t\Big]\quad\text{s.t.}\quad \mathbb E_{(s_t,a_t)\sim\rho_\pi}\big[-\log\pi(a_t\mid s_t)\big]\ge\bar{\mathcal H}.$$
> 符号：$\bar{\mathcal H}$＝目标熵（单位 nat；代码取 $-\dim(\mathcal A)$，即"每个动作维平均约 1 nat 不确定性"的工程经验值）；$\mathbb E[-\log\pi]$＝当前策略的实际熵 $H_{cur}$。
>
> **第二步：拉格朗日化，$\alpha$ 就是那个"价格"。** 引入乘子 $\alpha\ge0$ 把约束搬进目标（**把约束价格化**，正是 [[Optimization#2.2 拉格朗日对偶：把约束"价格化"|Optimization §2.2]] 的手法）：
> $$\mathcal L(\pi,\alpha)=\mathbb E\Big[\sum_t r_t\Big]+\alpha\Big(\mathbb E\big[-\log\pi\big]-\bar{\mathcal H}\Big)=\mathbb E\Big[\sum_t\big(r_t+\alpha H(\pi(\cdot\mid s_t))\big)\Big]-\alpha\bar{\mathcal H}.$$
> **看：最大熵目标 $\mathbb E[r+\alpha H]$ 不是拍脑袋加的正则项，而是这个熵约束问题的拉格朗日函数**（差一个与 $\pi$ 无关的常数 $-\alpha\bar{\mathcal H}$）。$\alpha$ 的身份由此确定——它是**熵约束的影子价格**：约束紧（熵不够）就该"涨价"多罚，约束松（熵有余）就该"降价"。
>
> **第三步：对偶梯度下降给出 $\alpha$ 的更新，且方向必是负反馈。** 内层解出 $\pi^*(\alpha)$ 后，外层对 $\alpha$ 做梯度下降：$\partial\mathcal L/\partial\alpha=\mathbb E[-\log\pi]-\bar{\mathcal H}=H_{cur}-\bar{\mathcal H}$。写成
> $$\alpha\leftarrow\alpha-\eta\big(H_{cur}-\bar{\mathcal H}\big)=\alpha+\eta\big(\bar{\mathcal H}-H_{cur}\big).$$
> 于是 $H_{cur}<\bar{\mathcal H}$（策略过自信）→ $\alpha$ **升**（涨熵价、逼它探索）；$H_{cur}>\bar{\mathcal H}$（过随机）→ $\alpha$ **降**。这与上面代码注释的负反馈方向一致——**$\alpha$ 自动追着"把实际熵钉在目标熵上"跑**，这也是为什么 SAC 不用再手调温度这个最难调的超参。$\alpha$ 作为"认知松紧的价格"随训练自适应升降，正是 §5 各处"熵即虚拟柔顺"的机理底座。

> [!important] SAC 为什么统治机器人领域：熵即虚拟柔顺
> 1. **随机策略 = 虚拟柔顺 (Virtual Compliance)**：策略方差 $\sigma$ 可解读为该维度的"软硬"——$\sigma$ 大＝不需精确控制（软），$\sigma$ 小＝需高刚度（硬）。这**天然契合 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]**。自动温度 $\alpha$ 则实现了**自适应刚柔**：初期柔（探索不同抓法）、后期刚（精确执行）。**这是 RL 与控制论最深的一处握手——熵正则在数学上扮演了阻抗的角色。**
> 2. **鲁棒**：熵项防止过早收敛到"只是握住不动"的偷懒局部最优。
> 3. **样本效率**：off-policy + replay，比 PPO 高一个数量级——真机生死线。

> [!tip] 高斯探索不是"图方便"，而是理论最优（[[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Wang et al. 2019]]）
> 用**连续时间随机控制**可证：对 Linear-Quadratic 问题，熵正则下的最优探索分布**恰是高斯** $\mathcal N(\mu^*(s),(\sigma^*)^2)$，且有漂亮的**分离原则**：
> - **均值** $\mu^*(s)$ 只依赖状态、与温度无关 → 负责**利用**；
> - **方差** $(\sigma^*)^2\propto\lambda$（温度）、与状态无关 → 负责**探索**。
>
> 额外洞见：**环境噪声越大，最优探索方差越小**——因为随机环境本身就免费提供了探索。这与 [[StochasticProcess]] 的随机控制视角直接相通。

> [!note] SAC 演进：SQL → SAC v1 → SAC v2
> SQL (2017, SVGD 采样，效率低) → SAC v1 (2018, 重参数化 + 双 Q + 固定 $\alpha$) → SAC v2 (2019, 自动温度，工业标准)。

---

### 5.3 同台对照：五个算法如何转这一支笔

> [!abstract] 一支笔，照出五种算法的灵魂（本讲对比脊柱的高潮）
> 给定同一个转笔任务，把 §5 的五个算法请上同一张桌子：
>
> - **REINFORCE**：一条侥幸转成的轨迹，会把其中所有动作（含败笔）概率整体抬高——"一好遮百丑"，方差极大、常学不动。
> - **DDPG**：一次"侥幸猛甩"被 $\max$ 式 Critic 高估成高价值（§3.3），策略据此施加危险大力矩，掉笔/损机、训练崩溃。
> - **TD3**：取 $\min(Q_1,Q_2)$，**宁可低估也不批准危险扭矩**；再用 target smoothing 反问"这套指步在 0.2mm 抖动下还成立吗？"——只保留鲁棒指步。
> - **SAC**：用熵把"左转/右转"两套指步都留在候选里、不过早押注；把策略方差当**指尖虚拟柔顺**，接触阶段自动变软、精确阶段自动变硬。
> - **PPO**：用 clip 死守"别用一次大更新毁掉已学会的指步时序"，在 IsaacGym 数千并行环境里稳扎稳打。
>
> **同一个任务、五种灵魂**：REINFORCE 输在方差，DDPG 输在高估，TD3 赢在保守鲁棒，SAC 赢在柔顺与样本效率，PPO 赢在更新稳健与并行规模。这就是"用一个母题贯穿整条对比线"。

| 特性 | **DDPG** | **TD3** | **SAC** | 与灵巧操作的相关性 |
|:--|:--|:--|:--|:--|
| 策略类型 | 确定性 | 确定性 | **随机** | 随机性天然建模传感/执行噪声、并提供虚拟柔顺 |
| Critic 更新 | 单 Q | $\min(Q_1,Q_2)$ | $\min(Q_1,Q_2)$ | clipped double-Q 防止因 Q-bias 而过度发力 |
| 探索 | OU 噪声 | 动作噪声 | **熵正则（自动温度）** | 熵自调在精细接触阶段自适应探索强度 |
| 样本效率 | 高 | 高 | **很高** | 直接决定真机训练的可行性（减少磨损） |
| 稳定性 | 低（脆） | 中 | **高** | 接触丰富任务的稳健之选 |

> [!important] PPO vs SAC：到底选哪个？（一句话决策）
> | 场景 | 选 | 原因 |
> |:--|:--|:--|
> | **仿真大规模并行**（IsaacGym 数千环境） | **PPO** | 海量并行弥补 on-policy 的样本低效；实现简单、超稳 |
> | **真机训练**（数据昂贵） | **SAC** | replay 重用历史数据，样本效率高一个数量级 |
> | **高维连续 + 需柔顺** | **SAC** | 最大熵探索 + 熵即柔顺 |
> | **多峰动作**（左/右转） | 二者都不理想 | 转向**扩散策略**（§10）或层级策略 |
>
> 这张表把 §5.0 的统一框架落到了工程决策上：选 PPO 还是 SAC，本质是选 $\pi_0=\pi_{old}$（信任旧策略、丢弃旧数据）还是 $\pi_0=$ 均匀（最大熵、长期复用数据）。

### 5.4 两个延伸：让探索更"连贯"，让范式更"统一"

#### 5.4.1 时间一致探索：从白噪声到自回归过程

> [!tip] 标准高斯探索的隐疾（[[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|AR Policies]]）
> $a_t=\mu(s_t)+\epsilon_t,\ \epsilon_t\sim\mathcal N(0,\sigma^2)$ 的相邻噪声**独立同分布**，导致：**高频抖动**（探索像"原地震动"、覆盖差）+ **硬件损伤**（jerky 运动冲击关节）。
> **自回归探索 (AR-p)**：$\epsilon_t=\sum_{i=1}^p\phi_i\epsilon_{t-i}+\eta_t$，按 Yule–Walker 选系数，可保持**边缘分布不变**（不影响策略梯度）却**可调时间相关性**——$\phi$ 越大轨迹越平滑、探索越"坚持方向"。
> **转笔落点**：精密位置控制需高 $\phi$（连贯），快速接住需低 $\phi$（敏捷）。这里 AR 过程与 [[StochasticProcess#2.1 SDE：漂移 + 扩散，且扩散是状态相关的|有色噪声/OU 过程]] 同源——又一处随机过程↔RL 的连接。

#### 5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家

> [!abstract] 把模仿与强化收进同一个梯度（呼应 §1.5 的"模仿×强化"缝合线）
> 将四种训练范式的梯度都经重要性采样换到 on-policy 分布，它们形如同一式 $\nabla_\theta\log\pi_\theta(a\mid s)\cdot w(s,a)$，只差**权重 $w$** 和**稀疏/稠密**：
>
> | 方法 | 权重 $w$ | 稀疏/稠密 |
> |:--|:--|:--|
> | **SFT (行为克隆)** | 指示函数 $\mathbf 1[a=a^*]$ | 稀疏 |
> | **Off-policy 蒸馏** | 教师分布 $\pi_{teacher}(a\mid s)$ | 稠密 |
> | **AWAC (优势加权 BC)** | $\exp\!\big(A(s,a)/\beta\big)$ | 稠密（软加权，BC↔RL 之桥，详见 §7.4） |
> | **RL (GRPO)** | 优势 $\hat A(s,a)$ | 稀疏 |
> | **On-policy 蒸馏** | 教师分布 | 稠密 |
>
> **洞见**：**SFT = 奖励是指示函数的稀疏 RL**；RL 与 on-policy 蒸馏都是 on-policy，区别只在 reward 稀疏加权 vs 教师稠密加权。
> **灵巧操作含义**：Sim-to-Real 中，仿真专家向真机学生**蒸馏**时，稠密的教师信号比 RL 的稀疏 reward 更高效（直接缓解 §2.3 的 credit assignment）；这为 §9 的 teacher-student 迁移提供了理论依据。

> [!important] 补深：SFT 与 RL 的分野 = forward-KL vs reverse-KL（"学会做" vs "学会选"）
> 上表把 SFT/蒸馏/RL 收进同一梯度骨架，却没点破 **SFT 与 RL 在优化几何上究竟差在哪**。一句话锚定：**差别只在"$\mathbb E$ 下面的采样分布是谁"，而这直接决定拟合的是 forward 还是 reverse KL**。
>
> - **SFT ＝ 在演示分布上最大似然**：$\mathcal L_{SFT}=-\mathbb E_{(x,y)\sim\mathcal D_{demo}}[\log\pi_\theta(y\mid x)]$。期望在**外部专家分布** $\pi_\beta$ 上取，$\log\pi_\beta$ 对 $\theta$ 为常数，故等价于 $\min_\theta D_{KL}(\pi_\beta\,\|\,\pi_\theta)$——**forward KL**。其 **mode-covering（覆盖）** 天性逼模型摊平去盖住专家每个模式（含噪声）；几何上是"**学会做**"：把演示动作统统学会，哪怕它们离模型当前分布很远、需"暴力拉扯"参数（灾难性遗忘的根）。
> - **RL ＝ 在自身分布上按奖励重加权**：$\nabla_\theta\mathcal L_{RL}=-\mathbb E_{y\sim\pi_\theta}[A(x,y)\,\nabla_\theta\log\pi_\theta(y\mid x)]$。期望在**模型自己当前分布** $\pi_\theta$ 上取（on-policy），由 §5.0 的变分解可证它等价于 $\min_\theta D_{KL}(\pi_\theta\,\|\,\pi^*)$，$\pi^*\propto\pi_{ref}\exp(r/\beta)$——**reverse KL**。其 **mode-seeking（寻峰）** 天性让模型只在**已经会说的话**里挑奖励高的加权，不去无中生有拟合遥远的完美答案；几何上是"**学会选**"：在自身支撑集内做拓扑保距的微调，天然小 KL、小漂移。
> - **两条 KL 的几何细节**（mode-covering/-seeking、$\infty$ 惩罚何时触发）**不在此重述**，交给 [[InformationTheory#2.3 KL 散度：信念跳变与"贝叶斯惊奇"|信息论 §2.3]]；此处只留 RL 优化视角的落点：**forward-KL＝SFT＝覆盖＝"学会做"，reverse-KL＝RL＝寻峰＝"学会选"**。这与 §5.0"$\pi_0$ 选谁"的 Boltzmann 表是同一张地图的两种读法——$\pi_0=$ 数据分布即滑向 SFT 端（§7.4 AWAC），$\pi_0=\pi_{old}$ 即 PPO 的 reverse-KL 信任域。
>
> **后训练三范式对照（补 §5.4.2 权重表的 SFT/RLHF 行 + KL 方向列）**：
>
> | 后训练范式 | 采样分布（谁在做题） | 监督信号（谁给分） | 主导 KL | 权重 $w$（统一骨架） |
> |:--|:--|:--|:--|:--|
> | **SFT** | 专家 $\pi_\beta$（off-policy） | 人标硬答案 $y^*$ | forward $D_{KL}(\pi_\beta\|\pi_\theta)$ | 指示 $\mathbf 1[a=y^*]$ |
> | **RLHF (PPO)** | 学生 $\pi_\theta$（on-policy） | 奖励模型标量 $r$ | reverse $D_{KL}(\pi_\theta\|\pi^*)$ | 优势 $\hat A$ |
> | **OPD（on-policy 蒸馏）** | 学生 $\pi_\theta$（on-policy） | 教师稠密 logits | reverse（$\beta{=}1$ 特例） | 隐式优势 $\log\tfrac{\pi_{teacher}}{\pi_{ref}}$ |

> [!abstract] OPD (On-Policy Distillation)：LLM 版的"模仿×强化缝合线"，及其到灵巧操作 VLA 后训练的迁移
> **起源（2011 · DAgger）**：§7.4 已证 DAgger 的**状态**分布是 on-policy（消 covariate shift），但**动作**监督 $\mathbb E_{s\sim\rho_{\pi_\theta}}[D_{KL}(\pi_{oracle}\|\pi_\theta)]$ 仍是 **forward KL**（期望在专家动作上取）——遇多专家/多模态会被 mode-covering 逼出无效**均值动作**（连续空间的 mode collapse）。
> **发展（LLM OPD）**：现代 LLM 的 on-policy 蒸馏（MiniLLM / GKD 一脉）做了一处"微小却深远"的改动——让**学生自己采样动作 $y\sim\pi_\theta$、教师只给这个动作打分**，把内层期望翻到学生分布上：$\mathcal L_{OPD}=\mathbb E_{x\sim\rho_{\pi_\theta}}[D_{KL}(\pi_\theta\|\pi_{teacher})]$——**reverse KL**，于是 mode-seeking，天然避开 DAgger 的均值坍塌。
> **现状（G-OPD 统一定理）**：把教师相对基线的对数概率差定义为**隐式奖励** $r_{implicit}=\log\pi_{teacher}-\log\pi_{ref}$，可证 **OPD ≡ $\beta{=}1$ 的 KL 约束 RL**（§5.0 那个式子的特例）。于是 SFT 与 RL 不再是两件事：**OPD 是一种拥有稠密教师奖励、惩罚系数固定的特殊 RL**——它在学生自己的分布上（on-policy）拟合由教师提供的稠密 advantage。再引入可调外推因子 $\lambda>1$（ExOPD），学生甚至能在特定任务上**超越教师**（reward extrapolation）。
> **缝合线含义**：这正是 §7.4"**模仿×强化缝合线**"的 LLM 实例——SFT（forward-KL 打底）与 RL（reverse-KL 精修）本是一条连续谱，OPD 把二者缝进同一个 on-policy 循环的接缝里。
> **迁移到灵巧操作 VLA 后训练**：把"教师"换成享有特权信息 $s^p$（物体 6D 位姿、摩擦）的 **Oracle 策略**、把"学生"换成只见真机观测 $s^o$ 的 **Generalist**，OPD 就落到 [[EmbodiedAI#2.3 VLA 后训练：从模仿到强化|VLA 后训练]] 与 §9.3 的 teacher-student 迁移上。两条工程要点：① **非对称 actor-critic**——critic 吃特权 $s^p$ 降方差、actor 只吃 $s^o$，且用**历史窗口 $h_t$ 做隐式系统辨识**（从观测序列反推"手里是哪个物体"，正是 §2.1 **POMDP→belief** 暗线：历史即充分统计量、蒸馏出的 belief 顶替特权 latent）；② **复合优势** $A=w_1\,A^{env}_{track}+w_2\,\lambda\big(\log\pi_{oracle}(a\mid s^p)-\log\pi_{base}\big)$——教师 logits 当稠密 shaping，但**最终锚点仍是任务奖励**（如轨迹追踪准确率），随训练衰减教师权重 $w_2\!\to\!0$，防被次优教师限死上限。既拿 OPD 的稠密加速，又不绕开"最大化成功率"这个真目标。

---

## 6. 样本效率的前沿：Model-Based 与 Offline

> [!tip] 本节四拍
> **直觉**（SAC 仍需百万步——真机上是几周；能不能在"脑内"练，或只用历史数据练？）→ **推导**（世界模型 + 不确定性；保守 Q）→ **对比**（Model-Free vs Model-Based vs Offline）→ **联系**（[[Optimization|MPC]]、[[StochasticProcess|不确定性量化]]、[[ControlTheory|安全]]）。

### 6.1 Model-Based RL：在想象中转笔

> [!note] 专门深挖见 [[WorldModels|世界模型 Foundation]]
> 本节讲 MBRL 作为 RL 样本效率手段；而"世界模型"作为独立理论大厦（表征→预测(RSSM)→不确定性(ensemble)→利用→Actuator+Rigid 结构→真机安全调度与课程生成）见 [[WorldModels]]。这里点到的 DreamerV3/RSSM、ensemble、MPC 在那里被系统展开——尤其是 [[Final_WMTS|WMTS]] 项目把世界模型拆成 Actuator+Rigid 两级的核心结构决策。

即便 SAC，也常需百万级交互——真机上意味着数周与可观磨损。MBRL 的思路：**先学一个动力学模型（世界模型），再在模型里规划/想象，省下真实交互。**

> [!important] DreamerV3 / RSSM：解决遮挡的记忆机制
> 学 $p(s_{t+1}\mid s_t,a_t)$（动力学）与 $p(o_t\mid s_t)$（解码）。最关键的是 **RSSM** 把隐状态拆成**确定性部分**（RNN hidden，充当短期记忆）+ **随机部分**。转笔时手指频繁**遮挡**笔身——RSSM 能凭几帧前的记忆推断被遮挡的笔的状态，而单帧 SAC 一遮挡就丢目标。**这正是 §2.1 POMDP→belief 那条线的兑现**：world model 就是一个学出来的 belief 更新器。

**演进**：Version 0.5（朴素：学 $f$ 后直接规划，但**分布不匹配**——策略会跑到模型没见过的区域，误差累积）→ Version 1.5（**MPC**：学模型→规划 $H$ 步→**只执行第一个动作**→观测→重规划）。

> [!tip] MPC 的核心洞见（与 [[Optimization#7. 实时闭环：模型预测控制 (MPC)|Optimization §5]] 同一思想）
> **重规划频率越高，单次规划的精度要求越低**——因为下一步能修正这一步的错误。就像开车频繁看路而非闭眼直行。这把"模型不准"的风险用"高频反馈"摊薄掉。

> [!abstract] 为什么必须建模不确定性（否则优化器会"钻模型的空子"）
> 规划本质是优化。若模型在数据稀疏区过拟合出**不切实际的乐观预测**，优化器会**主动利用这个漏洞**，给出糟糕动作。两类不确定性必须分清：
> - **Aleatoric（偶然）**：数据/世界的内在随机；
> - **Epistemic（认知）**：模型自己的无知，在数据稀疏处缺置信。
>
> 输出分布的熵只能抓 aleatoric；过拟合时熵仍低却很危险。**Bootstrap Ensemble**（训 $N$ 个独立模型，看预测**分歧**）才能抓 epistemic。转笔的接触/非接触**边界**正是 epistemic 最高处——ensemble 让策略别盲目闯进这些高风险区。（这与 [[StochasticProcess#3.1 三类不确定性|结构不确定性]] 和 [[InformationTheory]] 的信息增益探索同源。）

### 6.2 Offline RL：只用历史数据，不在真机上冒险

很多时候我们不愿在真机上做危险探索，只想吃现成的历史数据。但标准 off-policy RL 会因 **OOD（分布外）动作的高估**而失败（又是 §3.3 高估诅咒的变体）。

| 算法 | 机制 | 转笔/灵巧操作含义 |
|:--|:--|:--|
| **CQL (2020)** | 显式**压低**数据集中没出现过的动作的 Q | "安全第一"：只在已知安全动作附近微调，严禁盲目探索损坏硬件 |
| **IQL (2021)** | 用 expectile 回归，**完全回避**对 OOD 动作的 Q 估计 | 更稳的离线训练 |
| **Decision Transformer (2021)** | 把 RL 重构成**序列建模**（given 目标回报，预测动作） | 通往 §10 生成式策略与 VLA 的桥 |

> [!note] CQL 的一行数学直觉
> $\min_Q\ \alpha\big(\mathbb E_{a\sim\pi}[Q(s,a)]-\mathbb E_{a\sim\mathcal D}[Q(s,a)]\big)+\text{(标准 Bellman 误差)}$：**压低当前策略想尝试的动作、抬高数据里真实出现的动作**。在灵巧操作里，这防止机器人去试那些"看起来很美但从未试过"的危险动作。

---

## 7. 探索：稀疏奖励下，如何"撞见"转笔成功

> [!tip] 本节四拍
> **直觉**（随机抖动几乎不可能凑巧转满一圈，怎么办？）→ **推导**（用信息论精确刻画"探索"）→ **对比**（技能发现 vs 内在奖励 vs HER）→ **联系**（[[InformationTheory]] 的熵/互信息、§1.3 的流形安全探索）。

### 7.1 用信息论刻画探索

转笔成功的奖励极其稀疏，纯随机探索几乎触发不了。把探索写成信息论语言，问题就清晰了：

- **状态边缘熵** $H(\pi(s))=\mathbb E_{s\sim\pi}[-\log\pi(s)]$：策略对状态空间的**覆盖度**；
- **互信息 / 赋能 (Empowerment)** $I(s_{t+1};a_t)=H(s_{t+1})-H(s_{t+1}\mid a_t)$：**控制力**——我的动作能多大程度改变未来？

> [!tip] Empowerment 直觉（与 [[InformationTheory#6.1 Empowerment：最大化对未来的控制力|InfoTheory §6.1]] 同一对象）
> 第一项 $H(s_{t+1})$ 要"下一状态多样"（探索）；第二项 $-H(s_{t+1}\mid a_t)$ 要"给定动作后结果确定"（控制）。**高 empowerment 的状态 = 我能可靠地把笔转去很多不同姿态的状态**——这本身就是个绝佳的无奖励学习目标。

> [!note] 从"想探索信息增益"到"可计算的采集函数"：BALD（认知不确定性三用 暗线的探索端）
> 上面把探索写成互信息很漂亮，但落地要问：$I$ 具体算的是**哪两个变量的互信息**、怎么变成一个可优化的分数？这正是 [[InformationTheory#2.2 互信息：观测的"切割能力"|InfoTheory §2.2]] 处理的核心量——互信息度量"一次观测能把不确定性切掉多少"。把它用到 RL 探索上，就得到 **BALD (Bayesian Active Learning by Disagreement)** 采集函数：
> $$\underbrace{I(y;\theta\mid s,a)}_{\text{信息增益}}=\underbrace{H\big[\bar p(y\mid s,a)\big]}_{\text{总熵：ensemble 平均预测}}-\underbrace{\mathbb E_{\theta}\big[H[p(y\mid s,a,\theta)]\big]}_{\text{期望条件熵：各成员各自的熵}},$$
> 每个符号：$y$＝下一步观测/状态（随机变量），$\theta$＝模型参数（对它的不确定性正是**认知不确定性 epistemic**），$s,a$＝当前状态-动作，$H[\cdot]$＝熵（单位 nat）。这个差的物理意义极干净：**总熵高（大家平均起来说不准）但每个成员各自很自信（条件熵低）→ 分歧大 → 认知不确定性高 → 值得去采**；若高熵仅因环境本身随机（aleatoric，各成员都同样地不确定），两项相消、BALD≈0，正确地**不去浪费探索**。这就是把 §7.2(b) 里那个抽象的"信息增益 bonus $I(s';s,a)$"变成一行可算代码。它与 [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性|PETS 的 ensemble 分歧]] 是**同一个量**——只是在世界模型里当"别钻模型空子"的护栏、在这里当"该往哪探"的罗盘（认知不确定性三用之两用）。

### 7.2 三条探索路线

**(a) 技能发现 (Skill Discovery)**：无外部奖励时，学一组**可区分的多样技能** $\max_\pi I(S;G)=H(p(G))-H(p(G\mid S))$（$G$ 为技能、$S$ 为状态）——技能要多样、且从状态能认出是哪个技能。代表：**DIAYN**、**Skew-Fit**。*用途*：接触预训练阶段让手自主探索不同抓姿与接触模式，预训练技能加速下游转笔。

**(b) 内在奖励 (Intrinsic Motivation)**：$\tilde r=r+\beta\cdot\text{bonus}$。常见 bonus：count-based $1/\sqrt{N(s)}$、动力学预测误差（新颖性）、信息增益 $I(s';s,a)$。

**(c) 事后经验回放 (HER)**：

> [!important] HER：把失败"假装"成成功，自动生成课程
> [[Hindsight Experience Replay|HER]] 的核心：**人能从失败里学到几乎和成功一样多**。把一条没达成目标 $g$ 的轨迹，额外以其**实际到达的末态 $g'=s_T$** 作为"假目标"重放、重算奖励。于是早期能力弱时末态接近初态、学短距离操作；能力强后末态更远、逐步学复杂任务——**自动从易到难的隐式课程**。转笔的子目标（某个特定抓姿）天然适合做 HER 的重标注目标。

> [!note] 回扣 §1.3：探索的"安全"与"高效"是两个问题
> §1.3 的流形切空间探索（Geometric RL）解决的是**安全**（别穿透/脱离）；本节的信息论探索解决的是**高效**（别瞎撞）。二者正交、可叠加：**在切空间上做信息论驱动的探索** = 既安全又高效。这是把 [[ComputationalGeometry|几何]] 与 [[InformationTheory|信息论]] 同时当作 RL 归纳偏置的范例。

### 7.3 自动课程与开放式学习：把探索抬到任务空间

> [!tip] 本节四拍
> **直觉**（§7.1–7.2 的探索都发生在**一个固定 MDP 内部**——在给定的转笔任务里撞稀疏奖励。但若任务本身就太难，再聪明的内在动机也撞不开。真正的解法是把探索**抬升一层**：不再问"这一局怎么探"，而问"下一局该练哪个任务"）→ **推导**（六个 Phase，把"谁决定下一个该练什么"从人手里逐级交给算法：手工课程 → learning progress → regret/PLR → ADR → POET → generalist-specialist）→ **对比**（每一代补上一代的什么失效）→ **联系**（continuation 同伦、认知不确定性、CMA-ES 进化引擎、learning progress ≈ 信息增益）。

前面把**探索**定义在状态空间：在固定的转笔 MDP 里找那次稀疏成功。现在把它抬到**任务空间**——把环境参数化为 $\theta$（笔的重心偏移、指垫摩擦 $\mu$、要求转过的角度 $\Delta\phi$、目标位姿容差……），课程就是一个随训练演化的**任务采样分布** $Q_k(\theta)$。核心元准则只有一句：

> [!abstract] Goldilocks 原则（贯穿全节的元准则）
> **永远在"能力边界"上采任务**——既不能太难（策略连一次中等回报都拿不到，梯度信号为零、学不动），也不能太易（策略早已掌握，再练零信息、纯浪费）。下面六代方法的差别，只在于**用什么代理量去定位这条"不难不易"的边界**。记住这一句，六个 Phase 都是它的实现细节。

| Phase | 谁决定下一个任务 | 定位边界的代理量 | 代表 | 补上的失效 |
|:--|:--|:--|:--|:--|
| **1 手工课程** | 人 | 人的先验难度序 | continuation / [[Curriculum Learning]] | —（起点） |
| **2 learning progress** | 算法（选） | 能力变化率 $\nu_k=\lvert\Delta L_k\rvert$ | ALP-GMM | 人工设计不可扩展 |
| **3 regret / PLR** | 算法（回放选） | GAE 优势幅度 $S_l$ | [[Prioritized Level Replay]] | $L_k$ 难估、噪声大 |
| **4 ADR** | 算法（生长边界） | 边界外推 + 覆盖熵 $\mathcal H$ | ADR（见 §9.2） | 只能在固定任务集里"选" |
| **5 POET** | 协同进化（生成） | minimal criterion + 迁移 | [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions\|POET]] | 难度无法线性排序、垫脚石 |
| **6 generalist-specialist** | 蒸馏循环 | 专精 → 合并 | [[Improving Policy Optimization with Generalist-Specialist Learning\|GSL]] / [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning\|UniDexGrasp++]] | 单策略学多样任务负迁移 |

#### Phase 1 — 手工课程与 continuation：先解平滑子问题

最朴素的课程由人预设一条难度递增的任务序列，等价于让采样分布从一个**平滑、近凸的易任务分布** $Q_0$ 退火到**真难度分布** $Q_1$：

$$
Q_k(\theta)=(1-\alpha_k)\,Q_0(\theta)+\alpha_k\,Q_1(\theta),\qquad \alpha_k:0\to1.
$$

- $\theta$：环境参数；$Q_0$：大摩擦、短转角、宽容差的"婴儿版转笔"；$Q_1$：小摩擦、整圈、严容差的"目标转笔"；$\alpha_k\in[0,1]$：课程进度旋钮（随迭代 $k$ 单调升）。

这**正是** [[Optimization|continuation / 同伦方法]] 在任务空间里的化身——与接触平滑（先解软化接触再收紧）、扩散（先去噪粗结构再补细节）是**同一条"先易后难、把难度当连续参数缓缓拧入"的暗线**。

> [!tip] 对号：DNPM 双正交课程 = continuation + ZVF 门控
> [[Dynamic Non-Prehensile Manipulation|DNPM]] 的双正交课程把这条 continuation 拆成**两根正交的难度轴**：一根是**物理难度轴**（Phase 1 式的 $Q_0\to Q_1$，逐步减摩擦/增转角），另一根是**状态空间门控轴**（用 ZVF——零速翻转门控——控制允许策略进入的接触相位区）。二者正交，恰印证 §9.3 的实证结论"**物理难度课程与状态空间课程是两个正交维度，通用课程不存在**"。
>
> **局限**：手工课程需要人工设计、且任务特异（同一课程帮 TP 却伤 TA，见 §9.3）——这催生 Phase 2 把"选哪个任务"自动化。

#### Phase 2 — Learning Progress：让"进步速度"自己指路

自动化的第一步，是给每个任务子区域 $k$ 维护一个能力估计 $L_k$（近期成功率或平均回报的滑动平均），并按**学习进度 (learning progress)** 采样：

$$
\nu_k=\big\lvert L_k^{\text{new}}-L_k^{\text{old}}\big\rvert=\lvert\Delta L_k\rvert,\qquad P(\text{采 }k)\propto\nu_k.
$$

- $L_k$：区域 $k$ 的当前能力；$\nu_k$：能力变化率（绝对值）。

为什么用**变化率**而非能力本身？因为 Goldilocks：**太易**的区域 $L_k$ 已饱和、$\Delta L_k\approx0$；**太难**的区域怎么练都不动、$\Delta L_k\approx0$；只有**恰在能力边界**的区域进步最快、$\nu_k$ 最大。取绝对值 $\lvert\cdot\rvert$ 还能捕捉**负进步**（遗忘）——一旦某区域能力回退，$\nu_k$ 变大，课程自动回头复习。

> [!note] 暗线：learning progress ≈ 信息增益
> "策略在某任务上正快速进步" ≈ "该任务的每个样本正大量削减策略的无知" ≈ **信息增益最大**。于是 learning-progress 课程与 [[InformationTheory|信息论]] 的信息增益探索是同一枚硬币——只是把"削减状态不确定性"换成"削减任务能力不确定性"。这也是"**认知不确定性三用**"暗线在课程一侧的落点（探索里当罗盘、规划里当护栏、**课程里当'该学处'**）。

#### Phase 3 — Regret / PLR：用 GAE 优势幅度当"还能学多少"的代理

Phase 2 要显式估 $L_k$，在高维连续任务里既噪声大又慢。**Prioritized Level Replay (PLR)** 换一个更省的代理：**regret**——策略在某关卡 $l$ 上"距最优还差多少"。它证明 regret 可用一条已经算好的量近似：**GAE 优势的平均幅度**

$$
S_l=\frac1T\sum_{t=0}^{T-1}\big\lvert\hat A_t^{\mathrm{GAE}}\big\rvert.
$$

- $\hat A_t^{\mathrm{GAE}}$：§2.3/§4.3 已在训练里算出的广义优势；$T$：该关卡轨迹长度；$S_l$：关卡 $l$ 的打分。

直觉：优势幅度大 ⇔ Critic 的价值预测与真实回报偏差大 ⇔ 策略在此**还没学明白** ⇔ 高 regret ⇔ 值得回放。这本质是把 §8/DQN 的 prioritized experience replay 从"**优先回放高 TD-error 的 transition**"抬升为"**优先回放高 regret 的整个关卡**"。回放分布是两项混合：

$$
P_{\text{replay}}(l)=(1-\rho)\,P_S(l)+\rho\,P_C(l),
$$

- $P_S(l)$：正比于打分 $S_l$ 的分布（**利用**——多练高 regret 关卡）；$P_C(l)$：正比于"距上次访问的步数"的 staleness 分布（**探索**——久未回访的关卡分数已过时，得重新采一次校准）；$\rho\in[0,1]$：二者的混合系数。这一 exploit/explore 混合与 §7.1 的探索母题同构，只是对象从状态变成了关卡。

#### Phase 4 — ADR：不再"选"任务，而是"生长"任务边界

Phase 1–3 都在一个**固定**任务集里挑；**Automatic Domain Randomization (ADR)** 更进一步——直接把任务集的**边界**长出去。每维参数 $\phi_i$ 维护一个区间 $[\phi_i^L,\phi_i^H]$：在边界处采样评测，性能达标就把该边界**外推**（增难），跌破阈值就**收回**。课程已覆盖多广，用一个**熵**度量：

$$
\mathcal H=\frac1d\sum_{i=1}^d\log\big(\phi_i^H-\phi_i^L\big).
$$

- $d$：随机化参数维数；$\phi_i^H-\phi_i^L$：第 $i$ 维当前区间宽度；$\mathcal H$：随每维宽度单调增长，正是"课程已扩展到多宽"的进度指标（也可当训练是否收敛的信号）。

> [!important] ADR 揭示：课程与 Sim-to-Real 的 DR 是同一台机器
> ADR 就是 §9.2 里那味"增覆盖"的药——**在参数空间寻找可行性边界**。区别只在**读法**：站在 sim-to-real 角度它叫"扩大训练分布覆盖以抗真机扰动"（§9.2），站在课程角度它叫"按能力自动加难"（本节）。**同一个 $[\phi_i^L,\phi_i^H]$ 生长过程，喂饱了两个需求。** OpenAI 魔方项目正是靠 ADR 让手适应戴橡胶手套、断指等极端扰动。

#### Phase 5 — POET：当难度无法线性排序时，协同进化

Phase 1–4 都暗含一个假设：**难度是一根可排序的轴**。但真实的开放式问题里，任务是**多样**而非"更难/更易"的，而且存在**垫脚石效应**——任务 A 的解恰是攻克任务 B 的跳板，但 A 本身可能是条对 B 而言的弯路。**POET** 用（环境，策略）**协同进化**处理这种非线性：

1. **不断生成新环境**，但新环境须通过 **minimal criterion (MC)**：当前策略群里至少有一个能拿到**中等**分数（不是零分＝太难，也不是满分＝太易）——这正是 **Goldilocks 原则的显式实现**，把"不难不易"从代理量变成硬性准入门槛。
2. **跨环境迁移**：定期把每个策略拿到**所有**环境上互测，若某策略在别的环境里更强就迁移过去——让 A 环境练出的技能成为 B 环境的**垫脚石 (stepping stone)**。

> [!note] 暗线：环境生成器 = 任务空间里的进化搜索（复用"采样+加权统一优化"）
> POET 的环境生成本质是在任务空间做**进化搜索**，与 [[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）|CMA-ES]] 是**同一台引擎**——"采样候选 → 按 fitness 加权 → 挪动分布"，只是这里的 fitness 不是回报，而是"**这个任务能给当前策略群带来多少学习潜力**"（回到 Goldilocks）。这把"采样+加权统一优化"暗线从参数/控制/动作空间又延伸到了**任务空间**。

#### Phase 6 — Generalist-Specialist：用蒸馏循环缝合多样性

POET 会生成一大堆多样任务，但让**单一策略**同时学它们会互相打架（负迁移、梯度冲突）。**Generalist-Specialist Learning (GSL)** 用一个蒸馏循环破局：

1. **Specialist**：把任务分组，每组单独训一个专精策略——因为每个任务窄，各自都好学；
2. **Generalist**：用 §5.4.2 的**蒸馏**把所有 specialist 的动作分布压进一个通用策略（教师给的是**稠密**动作分布信号，远比稀疏 reward 好学）；
3. **迭代**：把 generalist 当更好的初始化，再分组精调 specialist……**GiGSL**（geometry-aware iterative，即 [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning\|UniDexGrasp++]]）在抓取上按几何相似度分组，循环迭代。

直觉：**分而治之 + 周期性知识合并**，绕开"一个策略硬扛所有任务"的优化难题。它与 §5.4.2 的洞见严丝合缝——**稠密教师蒸馏是缓解 §2.3 credit assignment 的最快通道**。

> [!important] 对号：WMTS 隐空间任务生成 = PLR + POET + 蒸馏三者融合
> [[Final_WMTS|WMTS]] 的课程构想不是选任一 Phase，而是把三代**叠在世界模型的隐空间里**跑：用 **PLR 的 regret 打分**从生成的任务里选"该学处"，用 **POET 的开放式生成 + minimal criterion** 源源不断造新任务，再用 **generalist-specialist 蒸馏**把学到的技能收拢进一个通用策略。关键红利：**这一切发生在世界模型 latent 里，零真机成本**。而"该生成什么任务"的信号，正来自 [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|无知即课程]]——**用模型的认知不确定性（epistemic）反向定位"我最无知、最该练"的任务**，是 learning-progress 课程的"世界模型版"（认知不确定性三用之"课程当该学处"）。
>
> 一句话串起来：**HER（§7.2）在单任务内把失败重标成课程；本节把课程抬到任务分布；WMTS 再把任务分布搬进想象空间。三级抬升，同一个 continuation 精神。**

### 7.4 模仿学习与策略蒸馏：把演示收编进统一梯度

> [!tip] 本节四拍
> **直觉**（[[ReinforcementLearning#1.5 对比之二：纯模仿学习为何不够|§1.5]] 说纯模仿会"雪崩"——现在把这句话**算成定理**，再看历代方法如何一步步把雪崩摁住）→ **推导**（BC 复合误差 $O(\epsilon T^2)$ 完整推导 → DAgger 降到 $O(\epsilon T)$ → 占用度量匹配 → 优势加权 BC）→ **对比**（每代补上上一代的什么漏洞）→ **联系**（[[ReinforcementLearning#5.0 先立统一框架：一切都是"在参考分布附近改进"|§5.0]] Boltzmann、[[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家|§5.4.2]] 权重表、[[ReinforcementLearning#6.2 Offline RL：只用历史数据，不在真机上冒险|§6.2]] offline、[[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|§10.1]] 扩散、[[WorldModels#6.2 Dream RL 的对抗性风险|Dream RL BC 正则]]）。

§1.5 用"雪崩"的比喻断言纯模仿不够。本节先把这个比喻变成一个可证的界，再沿着"如何把这个界从二次压到线性"这条主线，把 BC → DAgger → GAIL → AWAC → action chunking 串成一条"**逐步收编模仿进 RL**"的谱系。

#### 复合误差定理：兑现 §1.5 的"雪崩"

> [!theorem] 行为克隆的复合误差 $O(\epsilon T^2)$
> **设定**：专家策略 $\pi^*$ 在时刻 $t$ 诱导状态分布 $d_t^*$；BC 学到的策略 $\hat\pi$ 在专家分布下的**每步犯错率**受控，$\mathbb E_{s\sim d_t^*}\big[\mathbf 1\{\hat\pi(s)\ne\pi^*(s)\}\big]\le\epsilon$。记 $p_t$ 为**学习者自己**在时刻 $t$ 的状态分布。
>
> **第一步——分布偏移逐步累积**：用耦合 (coupling) 论证。让学习者与一个"影子专家"从同一状态出发、共享随机性；只要两者尚未分叉、都处于专家分布，则单步分叉概率 $\le\epsilon$。一旦分叉，最坏情形下不再重合。于是"到时刻 $t$ 仍未分叉"的概率 $\ge(1-\epsilon)^t\ge1-\epsilon t$，即
> $$\Pr[\text{到 }t\text{ 已分叉}]\le\epsilon t\ \Longrightarrow\ \big\|p_t-d_t^*\big\|_1\le 2\epsilon t.$$
> （$\ell_1$ 距离 $=2\times$ 全变差；未分叉时两分布共享状态、贡献为零，故全变差被"已分叉概率" $\epsilon t$ 界住。）
>
> **第二步——沿 $T$ 步求和**：设单步代价 $c_t\in[0,1]$。用"分布相近则期望代价相近"（$\mathbb E_{p}[c]-\mathbb E_{d}[c]\le\|p-d\|_{\mathrm{TV}}$，代价幅度 $\le1$）：
> $$J(\hat\pi)-J(\pi^*)=\sum_{t=1}^T\Big(\mathbb E_{p_t}[c_t]-\mathbb E_{d_t^*}[c_t]\Big)\le\sum_{t=1}^T\epsilon t=\epsilon\,\frac{T(T+1)}2=O(\epsilon T^2).$$
>
> **病根**：训练在专家分布 $d^*$ 上、测试在学习者分布 $p_\pi$ 上，二者错位；每步 $O(\epsilon t)$ 的偏移沿时间**线性放大**，求和成**二次** $O(\epsilon T^2)$。$T$ 越长（转一整圈的指步链很长），雪崩越猛——这就是 §1.5 那个比喻的定量版。

#### DAgger：no-regret 把 $T^2$ 压成 $T$

既然病根是"没在自己走出的状态上受训"，**DAgger** 的药就直白：**迭代地在学习者自己的分布 $p_{\hat\pi}$ 上采状态、请专家在这些状态上标注动作、聚合进数据集再重训**。把它写成 online learning：第 $i$ 轮策略 $\pi_i$ 面对损失 $\ell_i(\pi)=\mathbb E_{s\sim d_{\pi_i}}[\,\ell(\pi,s)\,]$，若用一个 **no-regret** 在线算法产生 $\{\pi_i\}$，则平均遗憾 $\frac1N\sum_i\ell_i(\pi_i)-\min_\pi\frac1N\sum_i\ell_i(\pi)\to0$。这保证存在某个 $\hat\pi$ 在**它自己诱导的分布上**误差 $\le\epsilon_N$，于是代价界变成**线性**：

$$
J(\hat\pi)\le J(\pi^*)+O(\epsilon T).
$$

- 关键差别一句话：**BC 在 $d^*$ 上训（测试时错位 → 二次）；DAgger 在 $p_\pi$ 上训（训练测试同分布 → 线性）**。分布错位被消掉，$T^2$ 就塌回 $T$。
- **局限**：需要专家**随叫随到**，且要在学习者走进的**所有状态**（含危险的将掉笔姿态）上给标注——真机上既贵又不安全。

#### HG-DAgger：human gating + 不确定性分诊

[[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]] 补上 DAgger 的两处实操痛点：

1. **Human gating（人类门控）**：不再要专家标注每一个状态，而是**人只在"接管"时贡献数据**——平时旁观，觉得要出事才夺回控制权、这段接管轨迹入库。省人力、且天然只在"危险边缘"采到高价值样本。
2. **Uncertainty triage（不确定性分诊）**：用策略输出方差 / ensemble 分歧当风险度量，**认知不确定性 (epistemic) 高就把控制权交还人类**。这正是"认知不确定性三用"暗线的又一落点——此处它当"**何时求助**"的罗盘。

> [!note] 承接 §9.3：HG-DAgger 是 HIL-SERL 的模仿学习前身
> HG-DAgger 的 gated 干预数据，正是 §9.3 里 HIL-SERL 强调的"**校正 ≠ 演示**"——它是"失败边缘的挽救"，不是"从头成功的示范"。把这段"校正"信号从纯监督（HG-DAgger）换成入 replay 的 RL 转移 $(s,a_{human},r,s')$，就得到 §9.3 的人在回路 RL。**同一份人类干预数据，模仿视角下叫 gating，强化视角下叫 correction。**

#### IRL / GAIL：从"匹配动作"到"匹配占用度量"

BC/DAgger 都在逐状态匹配动作。一个更根本的视角：匹配**占用度量 (occupancy measure)** $\rho_\pi(s,a)=\sum_{t\ge0}\gamma^t\Pr(s_t=s,a_t=a)$——策略在 $(s,a)$ 上停留的折扣频率。**GAIL** 用对抗式直接拉平两者的占用度量：

$$
\min_\pi\max_D\ \mathbb E_{\rho_\pi}\big[\log D(s,a)\big]+\mathbb E_{\rho_{\pi_E}}\big[\log(1-D(s,a))\big]-\lambda\,H(\pi).
$$

- 判别器 $D$ 学着分辨"策略 vs 专家"的 $(s,a)$；策略学着**骗过 $D$**，即把 $\rho_\pi$ 推向专家占用度量 $\rho_{\pi_E}$（等价最小化二者的 Jensen–Shannon 散度）。
- 为什么天然缓解复合误差？因为它在乎的是"**长期停在哪**"（整条分布），而非"**这一步选啥**"（逐点动作）——分布层面对齐，就不会因一步小错而在分布上雪崩。
- 熵项 $H(\pi)$ 正是 §5.2.3 SAC 的最大熵：**GAIL 内核就是一个以 $-\log D$ 为奖励的 max-entropy RL**。代价：min-max 训练不稳、且需在线环境交互（on-policy）。

#### AWAC / 优势加权 BC：§5.0 Boltzmann 取 $\pi_0 =$ 数据分布

最后一步把模仿彻底并进 RL。回到 §5.0 的最优解 $\pi^*(a\mid s)\propto\pi_0(a\mid s)\exp\!\big(Q(s,a)/\beta\big)$，**把参考分布 $\pi_0$ 取成数据（行为）分布 $\pi_\beta$**，再用 KL 投影把它拟合成参数化策略（加权回归）：

$$
\theta^*=\arg\max_\theta\ \mathbb E_{(s,a)\sim\mathcal D}\Big[\log\pi_\theta(a\mid s)\cdot\exp\!\big(A(s,a)/\beta\big)\Big].
$$

- 这就是 **AWAC / AWR**：一个 $\exp(A/\beta)$ **加权的 BC**——数据里优势高的动作多学、优势低的少学，"**只模仿数据中好的那部分**"。
- 它与 §6.2 offline RL 是一条心：**不外推到 OOD 动作**（那会触发 §3.3 的高估诅咒），只在数据支撑内重加权，安全。

> [!important] 统一梯度骨架：补全 §5.4.2 的权重表
> 上述所有方法——BC、蒸馏、AWAC、RL——梯度都是同一副骨架 $\nabla_\theta\log\pi_\theta(a\mid s)\cdot w$，只在**权重 $w$** 上不同：
>
> | 方法 | 权重 $w$ | 参考 $\pi_0$ | 与 §5.0 的关系 |
> |:--|:--|:--|:--|
> | **BC / SFT** | 指示 $\mathbf 1[a=a^*]$ | —（硬模仿） | 奖励是指示函数的稀疏 RL |
> | **Off-policy 蒸馏** | 教师分布 $\pi_{teacher}(a\mid s)$ | 教师 | 稠密教师加权 |
> | **AWAC / 优势加权 BC** | $\exp\!\big(A(s,a)/\beta\big)$ | **数据分布 $\pi_\beta$** | Boltzmann 解的加权回归投影 |
> | **RL (PG / GRPO)** | 优势 $\hat A(s,a)$ | 旧策略 | 优势加权 |
>
> **洞见**：权重从"**指示**（BC）"→"**$\exp(A/\beta)$**（AWAC）"→"**优势**（RL）"是一条**连续谱**。AWAC 恰是 BC 与 RL 之间的**插值**：$\beta\to\infty$ 时 $\exp(A/\beta)\to1$（常权重）＝无差别模仿全部数据＝**纯 BC**；$\beta\to0$ 时权重集中到最大优势动作＝**贪婪 RL**。这补全了 §5.4.2 只有 SFT/蒸馏/RL 三点、独缺 AWAC 这座"BC↔RL 之桥"的权重表。

#### Action chunking：把有效 horizon 从 $T$ 砍到 $T/H$

复合误差 $O(\epsilon T^2)$ 里的 $T$ 是**决策步数**。若策略一次预测 $H$ 步的**动作块 (action chunk)** 并开环执行，决策次数降到 $T/H$，复合误差随之降到 $O\!\big(\epsilon(T/H)^2\big)$——**二次地缩小**。这正是 ACT 与 [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]] 在长时程任务上稳的关键机制之一（表征侧详见 [[RepresentationLearning#2.3 ACT：动作分块处理长时相关|ACT 动作分块]]）。代价：块内开环 → 对块内扰动不反应，故 $H$ 是"**稳健性 vs 反应性**"的旋钮。

> [!tip] 转笔落点
> 一个指步微周期"松指 → 补位 → 推动"天然就是一个 chunk：块级预测既降复合误差，又保住那套毫秒级的**指步时序**——与 §5.1.2 的 clip"别一次毁掉已学会的指步时序"是同一诉求的两种手段（一个在**空间**上锁更新幅度，一个在**时间**上锁动作粒度）。

> [!important] 落点：模仿×强化缝合线的收口 + 对号
> 这一节把 §1.5 埋下的"**模仿×强化缝合线**"补成完整谱系：**纯 BC（雪崩）→ DAgger（在线纠错）→ GAIL（分布匹配）→ AWAC（优势加权、滑向 RL）→ §9.3 RLPD/HIL-SERL（真机缝合）→ §10.1 扩散 + RL**。而"演示昂贵"这个 §1.5 的痛点，也有了新解——用扩散 + RL **合成**演示数据（[[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training\|Beyond Human Demonstrations]]），把稀缺的人类演示放大成海量训练数据。
>
> - **暗线（认知不确定性 / 对抗风险）**：[[WorldModels#6.2 Dream RL 的对抗性风险|Dream RL 的 BC 正则]]——世界模型里想象训练时，加一个 BC / 行为正则把策略**锚在数据分布附近**，防它钻模型漏洞（§6.1 的"优化器利用模型过拟合"）。这正是 AWAC 的"$\pi_0=$ 数据分布"锚在**想象空间**里的翻版。
> - **对号：WMTS Oracle→Generalist = 特权蒸馏 + 块级 BC + 真机 AWAC**。仿真里 Oracle 用特权信息当 specialist，向 Generalist **蒸馏**稠密动作分布（§5.4.2 / §7.3 Phase 6）；用 **action chunk** 降低长指步链的复合误差；搬上真机后用 **AWAC**（offline 优势加权、不外推）做安全的最后一段收口。

---

## 8. 燃料：状态表征与奖励工程

> [!tip] 本节四拍
> **直觉**（算法是引擎，状态与奖励才是燃料；燃料配错，再好的引擎也跑偏）→ **推导**（触觉的非欧结构；PBRS 的保策略不变定理）→ **对比**（CNN vs GNN 触觉；稀疏/稠密/塑形奖励）→ **联系**（[[RepresentationLearning]]、[[Optimization|非凸景观]]、[[InformationTheory|因果中介]]）。

### 8.1 状态表征：触觉是灵巧操作的"暗感官"

近距离操作中视觉常被手指**自遮挡**，触觉（GelSight、BioTac）至关重要。但触觉数据是**非欧几里得**的——指尖是曲面。两种表征路线：

| 路线 | 做法 | 优点 | 缺点 |
|:--|:--|:--|:--|
| **Tactile Images + CNN** | 把压力分布摊成 2D 图，套 ResNet | 复用成熟架构 | 指尖球面展开引入畸变 |
| **GNN** | taxel 建为图节点、邻接矩阵=传感器拓扑 | 对软指变形更**不变**（压扁时图结构仍保局部关系） | 实现复杂 |

> [!note] 跨域联系
> 触觉表征的"该学什么、怎么学"属于 [[RepresentationLearning|表征学习]]（多模态融合与触觉智能一节）；触觉信号的"怎么滤波、怎么估状态"属于 [[SignalProcessing|信号处理]]（触觉转导与状态估计）。RL 只是这些表征的**消费者**——好状态让 §2.1 的 Markov 性更易满足。

### 8.2 奖励工程：最危险的自由度

| 类型 | 形式 | 优点 | 风险 |
|:--|:--|:--|:--|
| **稀疏** | 成功 +1，否则 0 | 最"纯粹"，保证最优 | 高维下探索到成功概率近 0 |
| **稠密 (shaping)** | $R=w_1\,\text{dist}+w_2\,\text{quat\_diff}+w_3\,\text{energy}+\dots$ | 引导探索 | **reward hacking**：学会钻奖励空子而非完成任务 |

稠密奖励是把双刃剑。它什么时候**安全**？有一个漂亮的充要条件：

> [!theorem] 势函数奖励塑形 (PBRS) — 保最优策略不变（Ng, Harada & Russell, 1999）
> 折扣 MDP（$\gamma<1$）中，塑形 $R'=R+F(s,a,s')$ 保持**所有最优策略不变**，**当且仅当**存在势函数 $\Phi:S\to\mathbb R$ 使
> $$F(s,a,s')=\gamma\Phi(s')-\Phi(s).$$
> **直觉**：PBRS 像物理学里"重设势能零点"——不改变力的方向（即不改变最优策略）。$\Phi(s)$ 可理解为"距目标还有多远"的估计。
>
> **为什么非 PBRS 的塑形会引发 hacking**：当 $F$ 不是势差形式，它**改变了最优策略**——策略转而最大化 $F$（塑形信号）而非 $R$（真任务）。**每加一个非 PBRS 项，就开一个新的 hacking 通道**，多项叠加使偏离**超线性**增长。

> [!warning] 实证：塑形项数量与 reward hacking 的"剂量-反应"关系（[[Dynamic Non-Prehensile Manipulation|DNPM]] Exp2, 2026-02）
> 转笔任务的系统性奖励搜索发现：
>
> | 配置 | 塑形项数 | TA 成功率 | TP 成功率 |
> |:--|:--|:--|:--|
> | **Heavy** | 6 (dist+rot+vel+energy+contact+bonus) | **0.00** | **0.00** |
> | **Medium** | 4 (dist+rot+vel+energy) | 0.31–0.72 | **0.86** |
> | **Light** | 3 (dist+rot+bonus) | **0.83** | 0.66–0.81 |
> | **Reduced** | 2 (dist+rot) | 0.17–0.75 | 0.21–0.74 |
>
> **洞见**：① Heavy 配置 **100% 失败**（强证据：过多塑形项=找到 hacking 捷径）；② 最简洁的 Light 在 TA 上最优（"少即是多"）；③ 塑形项**边际效用递减甚至为负**；④ **任务特异性**：TA 偏好 3 项、TP 偏好 4 项。理论上，多塑形项的联合景观里梯度被塑形信号主导，与 [[Optimization#3. 接触如何毁掉优化：互补约束与非凸景观|非凸景观]] 的"塑形 reward 制造更深局部极小"一致。

**更优的奖励来源**（绕开手工塑形）：

> [!tip] Mediator-Based 替代奖励——用因果结构降方差
> 当原始奖励噪声大（如接触任务的二值成功/失败），可借因果 DAG 的**中介变量 (Mediator)** 构造替代奖励。因果链 $\text{Action}\to\text{Mediator}\to\text{Reward}$，定义 $\tilde R(m,s)=\mathbb E[R\mid M=m,S=s]$。在 surrogacy 假设（$R\perp A\mid M,S$）下：**无偏** $\mathbb E[\tilde R\mid A,S]=\mathbb E[R\mid A,S]$ 且 **方差严格更低** $\mathrm{Var}(\tilde R)\le\mathrm{Var}(R)$。
> **转笔含义**：长因果链（发力→惯性→接触力→摩擦→抗重力）中，中间状态（接触力大小、笔角速度）可作 mediator，显著降低 §2.3 credit assignment 的方差。这把 [[InformationTheory|信息论/因果]] 直接接到了奖励设计上。其他路线：**ARES**（Transformer 从演示学权重）、**IRL**（从演示反推奖励）、**EUREKA**（LLM 自动写奖励）。

---

## 9. Sim-to-Real：把转笔策略搬上真机

> [!tip] 本节四拍
> **直觉**（仿真里转得飞起，真机一上手就掉笔——gap 到底在哪？）→ **推导**（按 MDP 四要素把 gap 拆开诊断）→ **对比**（System ID 减偏差 vs DR 增覆盖 vs 在线自适应）→ **联系**（[[ControlTheory#12. 自适应控制与确定性等价|自适应控制]]、[[Dynamics]]、[[ContactMechanics]]）。

### 9.1 先分类，再治疗：MDP 四要素 gap 诊断

> [!abstract] 把"sim-to-real gap"拆成四个可定位的源（[[A Survey of Sim-to-Real Methods in RL|MDP 四要素框架]]）
> | MDP 元素 | gap 来源 | 转笔里的典型表现 | 主要手段 |
> |:--|:--|:--|:--|
> | **State $S$** | 感知差异 | 渲染逼真度、触觉噪声 | 视觉域适应、随机纹理 |
> | **Action $A$** | 执行差异 | 电机延迟、齿槽、减速器背隙、力矩-转速包络 | action smoothing、[[Actuation|执行器建模]] |
> | **Transition $T$** | 动力学差异 | 笔的质量分布、指垫摩擦、弹性 | DR、系统辨识、残差模型 |
> | **Reward $R$** | 奖励差异 | 仿真 GT 位姿 vs 真机传感 | learned reward、人类反馈 |
>
> **对灵巧操作，$T$ 与 $A$ 是主瓶颈**——接触非线性（[[ContactMechanics]]）+ 执行器非理想（[[Actuation|电机/FOC/减速器/传动]]——仿真"关节虚拟力矩"假设的失效）共同构成 gap 核心。**先分清是哪一类 gap，再选药**，否则乱投医。

### 9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）

**离线系统辨识**：用真机诊断实验估物理参数 $\xi^*=\arg\min_\xi\|f_{sim}(s,a;\xi)-f_{real}(s,a)\|^2$——刚体参数（质量/惯量/质心，激励轨迹+最小二乘，见 [[Dynamics]]）、接触参数（摩擦/恢复系数，碰撞实验，见 [[ContactMechanics]]）、执行器参数（$K_t$、减速器效率 $\eta$、Stribeck 摩擦）。**局限**：静态辨识抓不住温漂、磨损等时变效应。

**在线自适应**：运行时持续校正。

| 方法 | 机制 | 代表 |
|:--|:--|:--|
| **RMA** | 环境编码器从历史观测推断隐式物理参数 $z=f(h_t)$ | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] |
| **Neural Dynamics** | 关节级残差网络补偿 sim-real 动力学差 | [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] |
| **Online Correction** | 人类在线修正→学修正模型 $\Delta a=g(s,a_{sim})$ | [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction\|TRANSIC]] |
| **Grounded Action Transform** | 学 $a_{real}=h(s,a_{sim})$ 修正仿真动作 | [[Grounded Action Transformation\|GAT]] |

> [!important] DR 与 System ID 是互补，不是二选一
> - **System ID** 减小 $\mathbb E\|T_{sim}-T_{real}\|$（**中心偏差**）；
> - **Domain Randomization** 增大 $\mathrm{Var}[T_{sim}]$（**覆盖范围**），$\xi\sim U[\xi_{low},\xi_{high}]$，学 $\max_\theta\mathbb E_{\xi}[J(\pi_\theta,\xi)]$；
> - **最佳实践**：先 System ID 缩中心偏差，再 DR 覆盖残余不确定性。灵巧手里，执行器参数（$K_t,\eta,$ 背隙）宜 System ID，接触摩擦宜 DR。
> - **Adaptive DR (ADR)**：像课程一样动态调随机范围（性能达标就加难），在参数空间找**可行性边界**——OpenAI 魔方项目靠它让手适应戴橡胶手套等极端扰动。

> [!important] 跨原理联系：RMA/DexNDM/GAT 都是"学出来的确定性等价控制器"
> 它们本质上都用隐变量 $z$ 替代经典自适应控制里的参数估计 $\hat\theta$——其稳定性、收敛性与**持续激励 (PE)** 条件的严格分析，见 [[ControlTheory#12. 自适应控制与确定性等价|ControlTheory §12]]。这条桥解释了"小数据真机适配为何可行"（NTK lazy regime + PE → 参数收敛）。**经典自适应控制不是被 RL 取代，而是给了 RL 一个稳定性分析的语言。**

### 9.3 真机高效 RL：把"模仿×强化"缝合线收口

回到 §1.5/§5.4.2 的伏笔——真机上最实用的不是纯 RL，而是**模仿打底 + RL 修正**。

- **RLPD**：每个训练步从**演示**与**在线**数据各采 50%——演示给初始方向、在线超越演示，50% 经验最优。
- **HIL-SERL（人在回路）**：关键区分 **校正 ≠ 演示**——演示是"成功轨迹（正样本模仿）"，校正是"失败边缘的挽救（从错误学）"。人观察到将失败→SpaceMouse 接管→$(s_t,a_{human},r,s_{t+1})$ 入 buffer→策略学"此处该做 $a_{human}$ 而非 $a_{policy}$"。结果：1–2.5 小时训练、相比 BC 提升约 101%、首次实现双臂动态抽叠等任务。系统要点：算法用 RLPD（高 update-to-data）、奖励用二值分类器、重置用前向-后向策略、控制器用阻抗（接触安全）。
- **RLT（VLA 在线精细化，Physical Intelligence 2026）**：不微调大 VLA，而是把其 embedding 压成单个 RL token（信息瓶颈），仅对 token 训极小 actor-critic，学**残差动作** $a=a_{VLA}+\Delta a_\theta$（reference-action dropout 防退化为恒等）。15 分钟真实数据→精密操作 3× 加速。转笔的关键接触切换点可用此架构做部署时在线精细化。

> [!note] 一条反直觉的实证：课程比触觉更重要（[[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation|Curriculum > Haptic]]）
> 三指手抓+转球实验里，**不同课程策略带来的性能差异 >> 有无触觉的差异**；某些课程下仅凭本体感知也能成功。**启示**：先设计好课程（课程即 inductive bias、即 [[Optimization|continuation method]] 的连续化），再谈堆传感器。但课程有**任务特异性**——DNPM 实验中同一课程（TWC）帮了 TP（成功率 0.66→0.86、方差降 19×）却伤了 TA（0.83→0.72），印证"物理难度课程"与"状态空间课程"是正交维度，通用课程不存在。

---

## 10. 前沿融合：当 RL 遇见生成模型与世界模型

> [!tip] 本节四拍
> **直觉**（§5.1.2 留下的"单峰高斯转不了多峰的笔"如何根治？真机交互太贵又如何免除？）→ **推导**（扩散把多峰建模做到极致；世界模型把交互搬进想象）→ **对比**（隐空间 vs 像素空间世界模型；PPO vs GRPO）→ **联系**（[[RepresentationLearning|扩散策略]]、[[EmbodiedAI|VLA]]、[[StochasticProcess|score matching]]）。

### 10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）

转笔"可左转可右转"是多峰的，单峰高斯会拟合到无效的中间均值。**扩散策略**把策略建成条件去噪过程：

$$
a_k\leftarrow a_{k-1}-\alpha\,\nabla\log p(a_{k-1}\mid s)+\mathcal N(0,\sigma),
$$

它能精确建模非凸、多峰的动作分布，标志从"**拟合均值**"到"**拟合分布**"的范式转移（理论详见 [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|扩散策略]]，其 score 与 [[StochasticProcess|SDE]] 同源）。

> [!tip] 扩散策略如何接受 RL 微调：Denoising Sub-MDP（[[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]）
> 矛盾：去噪多步推理与 RL 的单步 MDP 不兼容。RL-100 把**每一步去噪视作一个 sub-MDP 步**（状态含 $(s_{env},a_k,k)$），并用**一致性蒸馏**把 $K$ 步 DDPM 压成 1 步（100ms→10ms），让 RL 梯度可直接穿过单步 denoiser；再走 **IL→Offline RL→Online RL 三阶段**。7 个真实任务 900/900（100%）成功。**这给了"扩散模仿打底 + RL 修正"一条完整迁移路径**——又一次"模仿×强化"缝合。

### 10.2 世界模型 RL：隐空间 vs 像素空间

§6.1 的 **DreamerV3** 在**隐空间**做 imagination 规划（RSSM 记忆解遮挡）。新一代把世界模型搬到**像素空间**以对齐 VLA 的视觉特征：

> [!abstract] WMPO：像素空间世界模型 + GRPO 对 VLA 做 RL 后训练（[[WMPO - World Model-based Policy Optimization for VLA|WMPO]]）
> | 维度 | WMPO | 传统 | 优势 |
> |:--|:--|:--|:--|
> | 世界模型空间 | 像素空间视频生成 | 隐空间 (Dreamer) | 对齐 VLA 预训练视觉特征 |
> | RL 算法 | **GRPO** | PPO/REINFORCE | 无需 value 网络，组内比较更稳 |
> | 奖励 | VLM-as-Judge | 手工设计 | 可扩展到开放任务 |
> | 数据 | WM 内 on-policy rollout | 真机交互 | 零真实交互成本 |
>
> **GRPO**（组相对策略优化）：$\hat A_i=\frac{R_i-\mathrm{mean}(R_{1:G})}{\mathrm{std}(R_{1:G})}$ 用**组内归一化**替代 value 网络，是 §4.3 优势函数的"无 Critic 廉价版"。

### 10.3 RL Scaling Laws：把算力花在刀刃上

> [!abstract] IsoCompute Playbook：固定采样预算 $C=n\times B_{problem}\times M$ 如何最优分配？
> - **最优并行采样数 $n^*(C)$ 随预算 sigmoid 增长**（预算足时多开并行环境，如 IsaacGym）；
> - **Easy/Hard 机制不同**：Easy 任务靠大 $n$ **锐化**策略（改善 worst@k）；Hard 任务靠大 $n$ **扩展覆盖**（改善 best@k）；
> - **熵控制因难度而异**：Easy 需 KL/熵约束防过早坍缩，Hard 去正则反而更好；
> - **学习率随 batch size 平方根缩放** $\mathrm{lr}\propto\sqrt B$。
>
> 与转笔的关联：quasi-static（easy）vs dynamic（hard）任务需不同采样与熵策略；课程从 easy→hard 迁移时应**动态调熵正则**——这把 §5 SAC 的温度 $\alpha$ 与课程难度直接挂钩。

### 10.4 Test-Time RL：部署时继续学这一支特定的笔

> [!abstract] TTT-Discover：测试时对单个问题继续 RL
> 与标准 RL 优化**期望**奖励、需跨环境泛化不同，TTT 只需为**当前**问题找到**单个**最优解（max 而非 E）。其 **entropic objective** $J_\beta(\theta)=\mathbb E_s[\log\mathbb E_{a\sim\pi_\theta}e^{\beta R(s,a)}]$ 的策略梯度是 softmax 加权：$\beta\to\infty$ 退化为贪婪 argmax，$\beta\to0$ 退化为标准策略梯度。**转笔关联**：把策略部署到新笔（新摩擦/重心）时，测试时对该笔做 TTT 发现针对性指步——可视为"带学习的 [[Optimization#7.3 基于采样：MPPI（用并行换梯度）|MPPI]]"。$\beta$ 控探索-利用，类比 §5.2.3 SAC 的温度 $\alpha$。

### 10.5 统一分类：PPO/SAC/BRAC 差异仅在"更新时序"

> [!abstract] On/Off-Policy 的统一视角（[[Unified Policy Evaluation and Improvement - On Off-Policy Classification|Unified Policy]]）
> 用**评估** $\pi_E$ 与**改进** $\pi_I$ 两个维度看，所有算法都在解 $\pi_I=\arg\max_\pi\mathbb E_{a\sim\pi}[Q^{\pi_E}]-\alpha D_{KL}(\pi\|\pi_{ref})$（**正是 §5.0 的统一框架！**），差异只在 update schedule：
> | 状态 | $\pi_E$ | $\pi_I$ | 代表 |
> |:--|:--|:--|:--|
> | Pure On-Policy | 最新 | 最新 | **PPO** |
> | Pure Off-Policy | 旧 | 最新 | BRAC |
> | Cross-Policy | 连续更新 | 最新 | **SAC** |
>
> 这给"转笔该用 PPO 还是 SAC"再次提供理论判据：PPO 的 pure on-policy 适合 IsaacGym 大规模并行；转 SAC 则要管理 replay 的 staleness。**第 5 章开篇立的框架，在这里完成闭环。**

---

## 11. 知识回扣与记忆图：一支笔串起整本讲稿

> [!abstract] 用一条故事线把全讲复述一遍（这是刻意的复述，为了记忆）
> 我们要让一支笔在指间转一圈。**(§1)** 解析控制卡在 $3^5$ 模式组合与不可辨识的接触刚度，纯模仿又会因分布漂移雪崩——于是请出 RL。**(§2)** 我们用 MDP 描述它，用 Bellman 方程定义"转满一圈值多少"，并发现 Bellman=离散 HJB=LQR 的近亲；用 TD(λ) 的 $\lambda$ 旋钮把滞后的成功反馈回传给最初那次松指。**(§3)** 想直接学 $Q$ 做贪婪决策，却撞上 max 高估的诅咒——它会把侥幸猛甩误判成高价值。**(§4)** 改用策略梯度，靠 log-derivative 让不可微的接触求解器神奇消失，再用 baseline→优势→Actor-Critic 压住方差。**(§5)** 两条主线在统一的"$Q-\beta\,$KL-到-参考"框架下分叉：PPO 用 clip 守住已学会的指步时序，TD3 用 min-Q 拒绝危险扭矩，SAC 用熵把"左转/右转"都留着、把方差当指尖柔顺。**(§6)** 嫌交互太贵，就在世界模型里"想象转笔"（RSSM 还能记住被手指遮住的笔）。**(§7)** 成功太稀疏，就用 empowerment/HER 把失败也变成可学的课程。**(§8)** 给它喂好燃料：触觉表征当感官、PBRS 守住奖励不被 hack。**(§9)** 搬上真机时按 MDP 四要素诊断 gap，先 System ID 再 DR，用 RLPD/人在回路把模仿与强化缝在一起。**(§10)** 最后用扩散策略根治多峰、用 GRPO+世界模型零真机成本后训练 VLA。**一支笔，转完了整座理论大厦。**

> [!important] 一张表记住全篇（层级 → 问题 → 工具 → 转笔角色）
> | 层 | 核心问题 | 关键工具 | 代表算法 | 笔的哪一环 |
> |:--|:--|:--|:--|:--|
> | §2 MDP/Bellman | 价值如何递推 | TD、GAE、$\lambda$ 旋钮 | — | 成功反馈回传到松指 |
> | §3 价值方法 | max 为何高估 | Double-Q | DQN | 别把猛甩当高价值 |
> | §4 策略梯度 | 不可微怎么更新 | log-derivative、优势 | REINFORCE/A2C | 绕开接触求解器 |
> | §5 稳定更新 | 别毁掉已学策略 | KL-到-参考、clip、min-Q、熵 | TRPO/PPO/TD3/SAC | 守指步时序 / 拒危险扭矩 / 留多峰 |
> | §6 样本效率 | 数据如何省 | 世界模型、保守 Q | Dreamer/CQL | 想象转笔、安全微调 |
> | §7 探索 | 稀疏奖励怎么撞见 | 熵、empowerment、HER | DIAYN/HER | 把失败变课程 |
> | §8 燃料 | 状态/奖励配方 | 触觉表征、PBRS | — | 别被奖励 hack |
> | §9 Sim2Real | 仿真→真机 | MDP-4 gap、SysID/DR、RLPD | RMA/HIL-SERL | 诊断掉笔的 gap |
> | §10 前沿 | 多峰/零成本 | 扩散、GRPO、世界模型 | RL-100/WMPO | 左右转、后训练 |

> [!tip] 五条贯穿全讲的"暗线"（抓住这五条，细节自来）
> 1. **高估→低估→保守**：max 必然高估（§3.3）→ 取 min 低估（§5.2）→ 低估在真机更安全（§3.1）。
> 2. **一个框架收编一片算法**：$\max_\pi Q-\beta\,D_{KL}(\pi\|\pi_0)$，选 $\pi_0$=均匀得 SAC、=旧策略得 PPO、=专家得 RLPD（§5.0，§10.5 闭环）。
> 3. **模仿×强化的缝合线**：纯模仿会漂移（§1.5）→ SFT=稀疏 RL（§5.4.2）→ RLPD/teacher-student/扩散+RL（§9、§10）。
> 4. **信息=探索=柔顺**：熵既是探索目标（§7）又是 SAC 的虚拟阻抗柔顺（§5.2.3）——一个量，两副面孔，连起 [[InformationTheory]] 与 [[ControlTheory]]。
> 5. **低通滤波到处都是**：GAE 的资格迹（§2.3）、TD3 的目标平滑（§5.2.2）本质都是对噪声信号做一阶低通，与 [[SignalProcessing]] 同形。

> [!note] 跨领域链接（双向、点对点）
> - **→ [[ControlTheory]]**：Bellman↔HJB↔LQR（§2.2）；SAC 熵↔阻抗柔顺（§5.2.3）；RMA↔确定性等价自适应控制（§9.2）；Safe RL↔稳定性证书。
> - **→ [[Optimization]]**：策略优化↔随机优化；KL-到-参考↔近端算子（§5.0）；MBRL↔MPC（§6.1）；奖励塑形↔非凸景观（§8.2）。
> - **→ [[StochasticProcess]]**：belief-MDP↔粒子滤波（§2.1）；扩散策略↔SDE/score（§10.1）；AR 探索↔OU 过程（§5.4.1）；MPPI↔test-time RL（§10.4）。
> - **→ [[InformationTheory]]**：探索↔熵/互信息/empowerment（§7）；mediator 奖励↔因果（§8.2）；信息瓶颈↔RLT token（§9.3）。
> - **→ [[RepresentationLearning]]**：触觉表征（§8.1）；扩散策略理论（§10.1）；状态表征决定泛化。
> - **→ [[Dynamics]] / [[ContactMechanics]]**：非光滑接触是策略梯度高方差之源（§1.3）；动力学模型即世界模型（§6.1）；System ID 的物理参数（§9.2）。
> - **→ [[EmbodiedAI]]**：VLA 后训练（§10.2）；RL token 在线精细化（§9.3）；GRPO（§10.2/§10.5）。

---

## 12. 结论：走向物理感知的智能

强化学习在灵巧操作的成功，不是算力的堆砌，而是**对物理问题的深刻抽象 + 算法适配**：

1. **SAC** 用熵正则把物理柔顺编码进策略，化解接触刚性（§5.2.3）。
2. **Geometric RL** 用流形约束，把探索从"别穿透"中解放出来（§1.3、§7）。
3. **Sim-to-Real（System ID + ADR）** 在参数空间一减偏差、一增覆盖，弥合理想模型与真实世界（§9）。
4. **World Models** 用隐空间记忆解决遮挡与部分可观测（§6.1）。

未来在于 **Physics-Informed RL 与生成模型的深度融合**：不再把机器人当黑盒 MDP，而是用接触力学与几何先验去引导扩散/世界模型的生成。这是从"计算"回归"物理"的必经之路。

---

## 13. 学习资源

> Source: [[Books/lumina-eai-guide.pdf|Lumina Embodied AI Guide]]

| 类别 | 资源 | 链接 | 备注 |
|:--|:--|:--|:--|
| 数学基础 | Shiyu Zhao (Westlake): RL Math | [bilibili](https://www.bilibili.com/video/BV1sd4y167NS) | 系统推导 |
| DRL 概览 | Pieter Abbeel 6 Lectures | - | 快速框架 |
| DRL 系统 | Berkeley CS285 (Levine) | [website](https://rail.eecs.berkeley.edu/deeprlcourse/) | 工业标准 |
| 中文 DRL | 李宏毅 RL | - | 实践友好 |
| 上手 | EasyRL（蘑菇书） | [GitHub](https://github.com/datawhalechina/easy-rl) | 实操 |

| Baseline | 代码 | 特点 |
|:--|:--|:--|
| ACT | [GitHub](https://github.com/tonyzhaozh/act) | 经典 IL baseline |
| Diffusion Policy | [GitHub](https://github.com/real-stanford/diffusion_policy) | 鲁棒扩散 |
| DP3 | [GitHub](https://github.com/YanjieZe/3D-Diffusion-Policy) | 3D 表征 |

| 仿真器 | 链接 | 用途 |
|:--|:--|:--|
| Isaac Lab | [GitHub](https://github.com/NVIDIA-Omniverse/IsaacLab) | GPU 并行训练 |
| legged-gym | [GitHub](https://github.com/leggedrobotics/legged_gym) | 足式 |
| SAPIEN/ManiSkill | [Website](https://sapien.ucsd.edu/) | 操作 |
| Genesis | [Website](https://genesis-world.readthedocs.io/) | 新一代 GPU 仿真器 |

---

## 14. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的强化学习理论与方法。

### SAC 与最大熵 RL
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]]：SAC 用于触觉灵巧操作
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]]：纯触觉 RL 策略
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture|Dextrous Tactile]]：模块化 RL 架构
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach|Exploration vs Exploitation]]：高斯探索最优性的随机控制证明
- [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|AR Policies]]：时间一致探索

### 课程学习与渐进训练
- [[Curriculum Learning]]：课程学习的理论基础
- [[Prioritized Level Replay]]：regret/GAE 优势幅度打分的自动课程回放（§7.3 Phase 3）
- [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]：开放式协同进化 + minimal criterion + 跨环境迁移（§7.3 Phase 5）
- [[Improving Policy Optimization with Generalist-Specialist Learning|GSL]]：generalist-specialist 蒸馏循环（§7.3 Phase 6）
- [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning|UniDexGrasp++]]：几何感知课程 + 迭代 GiGSL
- [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation|Curriculum vs Haptic]]：课程设计 > 触觉传感
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation|CSR]]：传感课程与 Sim-to-Real
- [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]：示范引导自动课程
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]：熵引导演示加速

### Sim-to-Real 迁移
- [[A Survey of Sim-to-Real Methods in RL]]：MDP 四要素分类框架（State/Action/Transition/Reward）
- [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer|Tiwari et al. Survey]]：执行器级建模视角
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]]：RMA 隐式物理参数推断
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]]：关节级残差神经动力学
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]]：在线修正的策略迁移
- [[Grounded Action Transformation|GAT]]：仿真器 grounding 经典方法（AAAI 2017）
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]]：真实演示辅助迁移
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation|CyberDemo]]：仿真演示增强
- [[Part-Guided 3D RL for Sim2Real Articulated Object Manipulation]]：3D 部件引导跨铰接物体 Sim2Real

### 模仿学习与行为克隆
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills|DeepMimic]]：参考动作引导深度 RL
- [[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]]：human gating + 不确定性分诊的交互式模仿（§7.4）
- [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]：动作分块 + 扩散，降复合误差（§7.4 / §10.1）
- [[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training|Beyond Human Demonstrations]]：扩散 + RL 合成演示数据（§7.4 落点）
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]]：人类参考的神经跟踪控制 + 数据飞轮
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]：规划引导扩散策略

### 奖励设计与探索
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models|EUREKA]]：LLM 自动奖励设计
- [[Hindsight Experience Replay]]：稀疏奖励基石，目标重标注的隐式课程

### 控制频率与时间抽象
- [[TARC - Time-Adaptive Robotic Control]]：策略输出动作 + 持续时间
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|Control Frequency Adaptation]]：动作持续性与频率适应
- [[Elastic Time Step Reinforcement Learning, VTS-RL|VTS-RL]]：弹性时间步 RL
- [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks|EvoControl]]：演化高频控制
- [[Reinforcement Learning for Control with Multiple Frequencies|AP-AC]]：多变量各自频率 + 周期非平稳最优性
- [[Hierarchical Coordination Multi-Agent RL with Spatio-Temporal Abstraction|HSTCN]]：分层时间抽象（高层每 $c$ 步下达内在目标）

### 稳定性与平滑策略（RL × Control）
- [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]]：稳定性证书方法
- [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control|LipsNet]]：自适应 Lipschitz 约束网络

### 长时程与接触丰富任务
- [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]]：特权动作简化长时程探索
- [[Dexterous Robotic Manipulation using Deep RL and Knowledge Transfer]]：知识迁移框架
- [[Vision-force-fused Curriculum Learning for Robotic Assembly]]：视觉-力融合课程
- [[Deep Dynamics Models for Learning Dexterous Manipulation]]：model-based RL 在 Shadow Hand 上的高效真机学习
- [[Learning Quadrupedal Locomotion over Challenging Terrain]]：privileged teacher-student + adaptive curriculum 的 sim-to-real

### 扩散策略的 RL 微调与 World Model RL
- [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]：Denoising Sub-MDP，IL→Offline→Online 三阶段，consistency distillation
- [[WMPO - World Model-based Policy Optimization for VLA|WMPO]]：像素空间世界模型 + GRPO，VLM-as-Judge
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]]：Flow Matching 预训练 + 残差 RL 后训练

### 物理感知预训练与几何表征
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]]：Dynamics-lifted 几何预训练

### 非紧握操作与外在灵巧性
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]]：动力学感知策略学习，世界模型条件化 RL

### 触觉与多模态推理
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|SToLa]]：MoE 触觉-语言融合

### 数据生成与双臂操作
- [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation|RoboTwin 2.0]]：MLLM 驱动双臂数据生成 + 5 轴域随机化

### VLA 在线精细化与人形运动
- [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]]：RL Token 信息瓶颈，冻结 VLA + 轻量级 actor-critic
- [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]]：首个 arm-hand VLA 人在回路 post-training
- [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]]：Physics-prefix 引导运动生成
- [[Unified Policy Evaluation and Improvement - On Off-Policy Classification|Unified Policy]]：On/Off-Policy 统一分类（evaluation × improvement schedule）

### 真机 RL 系统
- [[SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning|SERL]]：真实世界 RL 系统
- [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning|HIL-SERL]]：人在回路校正
- [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|残差学习]]：接触丰富任务的残差 DMP

### 项目级真机 RL Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/_InsightsIndex|WMTS Insights Index]]：15 个真机 RL 角度的 idea（reward / sim-to-real / autonomy 三主线）
- 重点：[[Projects/World Model as Task Scheduler/all_Insights_local/Idea-001-Tactile-Anchored-Reward|TAR（无 GT pose reward）]] · [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-008-Physics-Aware-PER|PA-PER]] · [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-011-WM-Importance-Weighted-Diffusion|WMID off-policy diffusion RL]] · [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-015-Reset-Free-Autonomy|Reset-Free Autonomy]]

---

---

---

---

---

---

---
