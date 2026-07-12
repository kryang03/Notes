---
tags:
  - foundation
  - optimization
  - dexterous-manipulation
  - MPC
  - trajectory-optimization
aliases:
  - 优化理论
  - Optimization
  - iLQR
  - MPC
created: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[ComputationalGeometry]]"
  - "[[WorldModels]]"
---

# 灵巧操作中的优化理论：从可行域到实时接触隐式闭环

# Optimization for Dexterous Manipulation: From Feasible Sets to Real-Time Contact-Implicit Loops

> [!tip] 相关领域
> - [[ControlTheory]] — MPC 是优化在闭环里的实时实现；优化"每次解一个决策"，控制论问"解放进闭环后稳不稳"
> - [[Dynamics]] — 动力学方程是轨迹优化的等式约束；可微物理决定梯度能否穿过接触
> - [[ContactMechanics]] — 互补约束 (LCP)、摩擦锥是优化里最难啃的非凸非光滑源
> - [[ReinforcementLearning]] — RL=随机优化做序贯决策；iLQR 的 Riccati 与 RL 的 Bellman 同源
> - [[StochasticProcess]] — 采样式 MPC (MPPI)、随机平滑的理论母体
> - [[ComputationalGeometry]] — SDF 把"避碰/接触"变成可微的势能场
>
> **贯穿母题（本讲的"主角"）**：**伸手-抓杯-倒水 (reach → grasp → pour)**。一条看似平常的家务动作，恰好把优化理论每一层都"演"一遍——我们让它贯穿全篇。

---

## 0. 母题与理论大厦构建路线：从可行域到实时闭环优化

> [!abstract] 为什么用"伸手-抓杯-倒水"做贯穿母题？
> 优化在灵巧操作里的难点，不是"会不会解 QP"，而是"如何把物理约束写成**可求解、可解释、可实时更新**的问题"。**伸手-抓杯-倒水**这一条龙，恰好分段激活了每一层：
> - **伸手 (reach)**：在杂物间找一条**无碰撞**的平滑轨迹 → 可行域、SDF 势场、避碰约束；
> - **抓杯 (grasp)**：手指落到杯壁、形成**力闭合** → 摩擦锥（二阶锥约束）、可微抓取质量；
> - **端起 (lift)**：从"无接触"切到"稳定接触" → **接触模式切换**＝非凸、非光滑、组合爆炸；
> - **倒水 (pour)**：水流出使**质心实时漂移**，腕部要边转边保持不洒 → 动力学随时间变化的**实时 MPC**。
>
> 全讲每引入一个概念，我们都回到这只杯子："**它对应倒水的哪一步？这一步为什么会让上一个方法卡住？**"

优化理论在灵巧操作中的主线，是把物理约束翻译成机器能改进的问题。整座大厦分六层，每层回答一个更尖锐的问题，并落到"倒水"的某一段：

| 层级 | 建模问题 | 数学工具 | 倒水母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **可行域层** | 什么状态/接触/力是允许的？ | 凸集、约束、KKT、互补条件 | 关节限位、摩擦锥、不可穿透 | §2 |
| **目标层** | 什么轨迹算"好"？ | 代价函数、势函数、能量/风险项 | 成功、不洒、省力、平滑——不能糊成一团 | §2 |
| **求解层** | 如何从当前轨迹改进？ | GD、Newton、SQP、内点、iLQR/DDP、**零阶/CMA-ES** | 决定 MPC 能否在一个控制周期内收敛；黑箱目标只能零阶搜索 | §4、§6 |
| **非凸层** | 为什么会卡住或失败？ | 鞍点、PL、strict saddle、平滑化 | 端杯时接触模式切换造成局部极小与梯度断裂 | §3 |
| **接触层** | 模式未知时如何优化？ | CITO、LCP 松弛、隐式微分 | 让求解器自动发现"何时该碰杯壁、何时滑动" | §5、§6 |
| **学习层** | 如何用数据加速/替代求解？ | 可微优化层、warm start、策略蒸馏 | RL/IL 学求解器先验，但绕不开物理约束 | §7、§5 |

> [!important] Foundation 级判断标准（任何优化方法进入本库都要回答四问）
> 1. **接触怎么建模**（硬 LCP / 软平滑 / 黑盒仿真）？这决定了梯度的"成色"。
> 2. **梯度从哪来**（解析 / 隐式微分 / 零阶采样）？
> 3. **能否实时**（一次求解是 1ms、20ms 还是 1s？）这是 MPC 的生死线。
> 4. **如何逃局部极小**（warm start / 同伦 / 采样探索 / 熵正则）？

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>   [[Dynamics]] ──等式约束──┐                 ┌── MPC 实时闭环 ──> [[ControlTheory]]
> [[ContactMechanics]] ─LCP/摩擦锥─┤                │
> [[ComputationalGeometry]] ─SDF势场─┼──> 【Optimization】 ──Riccati↔Bellman──> [[ReinforcementLearning]]
>                                 │                │
>            采样/随机平滑 <──[[StochasticProcess]]┘                └── 可微优化层 ──> 学习加速
> ```
> 读法：左侧四者给优化"喂"约束与梯度（动力学方程、接触互补、SDF、随机性）；右侧消费优化的解（MPC 进控制闭环、iLQR 与 RL 共享 Bellman 结构）。每个推导拐点都会用 `[[链接]]` 回扣。

---

## 1. 为什么优化是灵巧操作的"决策内核"：欠驱动流形与"规划接触力"

> [!tip] 本节四拍
> **直觉**（倒水到底在优化什么？）→ **推导**（写出欠驱动操纵器方程，看清"物体只能被接触力间接驱动"）→ **对比**（纯几何规划 RRT 为何失效）→ **落点**（核心不是规划关节轨迹，而是规划接触力序列）。

### 1.1 母题解剖：倒水到底在求解什么？

把"伸手-抓杯-倒水"摊开看，它不是一段轨迹，而是一串**带约束的决策**：

```
伸手: 在障碍间找平滑、省力、无碰撞的手臂轨迹     (无接触，纯几何+动力学)
抓杯: 指尖落到杯壁、法向力进摩擦锥、形成力闭合     (建立接触，力分配)
端起: 接触从"无"切到"稳定" → 杯子开始被手驱动      (模式切换，欠驱动→受控)
倒水: 水流出，质心与惯量实时漂移；腕转而不洒不滑     (时变动力学，实时重规划)
```

注意：**杯子（和水）本身没有电机**。它能动，完全是因为手指通过接触给它施力。这就是灵巧操作优化的第一性事实——**我们真正要规划的，不是关节怎么走，而是接触力怎么给**。

### 1.2 推导：欠驱动流形与操纵器方程

系统状态必须**同时**含手与物体。定义广义配置 $q\in\mathbb R^{n_q}$：

$$
q=\begin{bmatrix}q_{hand}\\ q_{object}\end{bmatrix},\qquad
q_{hand}\in\mathbb R^{n_a}\ \text{(全驱动，Shadow Hand 20–24 DoF)},\quad
q_{object}\in SE(3)\ \text{(浮动基)}.
$$

状态 $x=[q;v]\in\mathbb R^{2n_q}$。动力学写成**操纵器方程**：

$$
M(q)\dot v + \underbrace{C(q,v)v}_{\text{科氏/离心}} + \underbrace{g(q)}_{\text{重力}} = \underbrace{Bu}_{\text{电机力矩}} + \underbrace{J_c(q)^T\lambda}_{\text{接触力映射}}.
$$

| 符号 | 含义 | 倒水中的角色 |
|:--|:--|:--|
| $M(q)\succ0$ | 广义惯性矩阵（分块：手 + 物体） | 水流出 → $M$ 的物体块**实时变化** |
| $C,g$ | 科氏/离心、重力 | 杯倾斜时重力矩剧变，是"洒"的主因 |
| $B$ | 驱动矩阵；**对应 $q_{object}$ 的行全为零** | 这一行的零，就是"欠驱动"的数学定义 |
| $J_c(q)$ | 接触雅可比 | 把指尖接触力 $\lambda$ 折算到广义力空间 |
| $\lambda$ | 接触力 | **最核心的决策变量与非线性源** |

> [!important] 第一性洞见：优化的本质是寻找可行的接触力序列
> 因为 $B$ 在物体那几行是零，**物体加速度 $\dot v_{object}$ 只能由 $J_c^T\lambda$ 产生**。若 $\lambda=0$，杯子完全不受控、自由落体。于是优化的真正目标，是找一段 $\lambda_{1:T}$，让 $J_c^T\lambda$ 恰好抵消并塑造物体的动态。**"规划接触力"而非"规划关节轨迹"——这一句话，是本讲所有算法的共同出发点。**（这条欠驱动主线与 [[Dynamics#8.3 冗余、自运动与可操作度|Dynamics 冗余/欠驱动]] 和 [[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|操作空间力控]] 直接接续。）

### 1.3 对比：纯几何规划 (RRT) 为何失效

最早人们把灵巧操作当**纯几何**问题：用 RRT/PRM 在构型空间搜一条无碰撞路径到预抓取点，再闭合手指，过程假设**准静态**（忽略 $M\ddot q$）。

> [!warning] 几何规划的三道墙
> 1. **割裂过程与结果**：手内操作（转、调姿、倒）要求"接触的同时发生相对运动"，准静态无法预测接触力演化。
> 2. **概率零陷阱**：接触流形是构型空间里的**零测度低维子流形**（$\phi(q)=0$）；无引导的随机采样落在接触面上的概率为零——RRT 几乎永远采不到"指尖正好贴住杯壁"。
> 3. **几何可行 ≠ 物理可行**：几何上碰到了，物理上杯子可能立刻滑落，必须有动力学一致性。
>
> **落点**：我们需要一种**把动力学与接触力当作决策变量、并能处理约束**的框架——这就是轨迹优化 (TrajOpt) 与 MPC。下一节先把"约束优化"的语言（凸性、对偶、KKT）建立起来。

---

## 2. 优化的语言：可行域、目标、对偶与 KKT

> [!tip] 本节四拍
> **直觉**（凸性="局部最优即全局最优"，是一切高效求解的根）→ **推导**（凸集/凸函数→拉格朗日对偶→KKT）→ **对比**（凸 vs 非凸：KKT 在凸问题里是充要、在非凸里仅必要）→ **联系**（KKT 互补松弛 ↔ [[ContactMechanics|LCP]]；对偶 ↔ [[ControlTheory|Safe RL 拉格朗日]]）。

> [!note] 教科书参考
> 本节基于 *Optimization in Theory and Practice* (Wright 2025) §2、§5 与凸优化教材 Ch.3–4（凸集/凸函数）、Ch.6（最优性条件与对偶）。

### 2.1 凸集与凸函数：为什么"凸"是分水岭

灵巧操作里许多子问题——力分配 QP、抓取规划、MPC 子问题——本身是凸的，或可松弛为凸。**凸性的全部好处浓缩成一句**：凸函数在任一点的切平面都是全局下界，故**一阶驻点即全局最优**。

集合 $C$ 凸 $\iff$ $\forall x,y\in C,\theta\in[0,1]:\ \theta x+(1-\theta)y\in C$。几类关键凸集，恰好对应倒水的约束：

| 凸集 | 定义 | 倒水/灵巧操作对应 |
|:--|:--|:--|
| 半空间 | $\{x\mid a^Tx\le b\}$ | 摩擦锥的多面体线性化 |
| 多面体 | $\{x\mid Ax\preceq b\}$ | 力分配可行域 |
| 椭球 | $(x-x_c)^TP^{-1}(x-x_c)\le1$ | 状态估计的不确定性椭球 |
| **二阶锥** | $\{(x,t)\mid\|x\|\le t\}$ | **摩擦锥** $\|\lambda_t\|\le\mu\lambda_n$ → 抓杯=SOCP |

凸函数（一阶条件）：$f(x+s)\ge f(x)+\nabla f(x)^Ts$；$\mu$-强凸再加 $+\frac\mu2\|s\|^2$（等价 $\nabla^2f\succeq\mu I$）。**保凸运算**（非负加权和、仿射复合、逐点上确界）让我们能"搭积木"地确认一个复杂目标是否凸。

> [!tip] 倒水里的凸性边界
> - 力分配"最小力范数" $\|f_c\|^2$ 是强凸的 → 好解；
> - 摩擦锥是二阶锥约束 → 抓杯是 SOCP，仍可高效解；
> - 但 **Ferrari-Canny 抓取质量是凸包运算（逐点上确界）的结果，不可微**（§8 专门修它）；
> - 而接触模式一旦进来（§3），可行域变成"坐标轴的并集"，**凸性彻底崩塌**。

### 2.2 拉格朗日对偶：把约束"价格化"

考虑一般非线性规划 (NLP) $\min_x f_0(x)$ s.t. $f_i(x)\le0,\ h_j(x)=0$。拉格朗日函数把约束用"价格"（乘子）并进目标：

$$
L(x,\lambda,\nu)=f_0(x)+\sum_i\lambda_i f_i(x)+\sum_j\nu_j h_j(x),\qquad \lambda_i\ge0.
$$

对偶函数 $g(\lambda,\nu)=\inf_x L$，对偶问题 $\max_{\lambda\ge0,\nu}g$。

> [!theorem] 弱对偶与 Slater 强对偶
> **弱对偶**：$\forall\lambda\ge0:\ g(\lambda,\nu)\le p^*$（证：可行点 $\tilde x$ 处 $\sum\lambda_if_i(\tilde x)\le0\Rightarrow L\le f_0$，取 inf）。对偶问题**恒为凸**（仿射族的逐点下确界=凹）。
> **强对偶 (Slater)**：若原问题凸且存在**严格可行点** $f_i(\tilde x)<0$，则 $p^*=d^*$（对偶间隙为零）。
> **倒水含义**：力分配 QP 几乎总满足 Slater（只要存在一个严格落在摩擦锥内部的力分配），故可放心用对偶/内点法求解。

> [!note] 对偶间隙到底是什么、为什么算法"离不开它"（补跳步 + 单位）
> **定义**：对偶间隙 $\Delta=p^*-d^*\ge0$（非负由弱对偶保证），单位与目标 $f_0$ 相同（倒水里若 $f_0=\|f_c\|^2$，则 $\Delta$ 单位为 $\mathrm N^2$）。它量的是"用对偶下界 $d^*$ 近似原始最优 $p^*$，最坏差多少"。
> **几何图像（为什么非凸才有缝）**：把每个 $x$ 映到点 $\big(f_1(x),\dots,f_m(x),\,f_0(x)\big)\in\mathbb R^{m+1}$，得值域集 $\mathcal G$。原始最优 $p^*$ 是 $\mathcal G$ 落在"约束轴 $\le0$"一侧的**最低高度**；对偶最优 $d^*$ 是 $\mathcal G$ 的**下凸包**在该处支撑超平面的高度。$\mathcal G$ 凸（凸问题）时支撑平面恰好顶到实体，$\Delta=0$；非凸时 $\mathcal G$ 有"凹陷"，支撑平面够不到底部，$\Delta>0$——**对偶间隙就是非凸留下的那道缝**。这也解释了 §3 一旦接触模式（非凸）进来，为何强对偶不再免费。
> **为什么算法离不开它**：① 任何一个对偶可行的 $(\lambda,\nu)$ 都白送一个**在线可算的下界** $g(\lambda,\nu)\le p^*$，于是 $f_0(x)-g(\lambda,\nu)$ 是"当前解离最优还差多远"的**实时证书**——这正是内点法/原始-对偶法的**停机准则**（间隙压到 $\epsilon$ 即停，无需知道 $p^*$）；② §4.3 中心路径参数 $\mu$ 与间隙同阶（$\Delta\approx n\mu$，$n$＝不等式约束个数），"令 $\mu\to0$"字面就是"令对偶间隙 $\to0$"——内点法的整条中心路径，就是沿"间隙均匀收缩"的轨迹走。
> **跨原理联系**：对偶函数 $g$ 作为"永不高估最优的下界证书"，与 [[ControlTheory#10.4 被动性与"价值即 Lyapunov"|"价值即 Lyapunov"]] 里值函数作为"界定最优代价的证书"是同一种数学角色（都从一侧夹逼最优）；把安全约束做拉格朗日对偶的 Safe RL（本节末 [[Reachability Constrained Reinforcement Learning]]）解的正是这套"原始-对偶夹逼"——对偶间隙即其"约束违反的价格是否收敛"的度量。

### 2.3 KKT 条件：约束最优的"语法"

对一般 NLP（适当约束规范下），最优解 $x^*$ 满足 KKT 一阶必要条件：

$$
\underbrace{\nabla f_0+\textstyle\sum_i\lambda_i\nabla f_i+\sum_j\nu_j\nabla h_j=0}_{\text{驻点}},\quad
\underbrace{f_i\le0,\ h_j=0}_{\text{原始可行}},\quad
\underbrace{\lambda_i\ge0}_{\text{对偶可行}},\quad
\underbrace{\lambda_i f_i=0}_{\text{互补松弛}}.
$$

**互补松弛**的物理意义：最优处要么约束不活跃（$f_i<0,\lambda_i=0$），要么恰好活跃（$f_i=0,\lambda_i>0$）。约束规范强弱链：LICQ ⇒ MFCQ ⇒ ACQ（Slater 是凸情形的 CQ）。

> [!note] 逐条推导：KKT 四条各自从哪来（不跳步）
> 设 $x^*$ 是局部最优，记活跃集 $\mathcal A=\{i\mid f_i(x^*)=0\}$（顶在边界上的约束）。在约束规范（如 LICQ：活跃约束梯度 $\{\nabla f_i,\nabla h_j\}$ 线性无关）下，逐条追溯：
> 1. **驻点条件**（源自"最优点处没有可行下降方向"）：若 $x^*$ 最优，则不存在方向 $d\in\mathbb R^n$ 同时满足 $\nabla f_0^Td<0$（一阶下降）与 $\nabla f_i^Td\le0,\ i\in\mathcal A$、$\nabla h_j^Td=0$（保持可行）。由 **Farkas 引理**，"这样的 $d$ 不存在" $\iff$ $-\nabla f_0$ 落在活跃约束梯度张成的锥内，即存在系数 $\lambda_i\ge0,\nu_j\in\mathbb R$ 使 $\nabla f_0+\sum_{i}\lambda_i\nabla f_i+\sum_j\nu_j\nabla h_j=0$。物理图像：**目标下降的"拉力"被约束边界的"支持力"恰好顶住**——这与 [[Dynamics#4.2 约束动力学：Lagrange 乘子与约束反力|Dynamics 约束反力]] 里 $\lambda$ 作为约束反力是**同一个乘子**（对偶性暗线：约束的乘子＝维持约束所需的力/价格）。
> 2. **原始可行** $f_i\le0,\ h_j=0$：$x^*$ 本就是可行解，天然成立（单位随 $f,h$ 的量纲——如距离约束 $[\mathrm m]$、力约束 $[\mathrm N]$）。
> 3. **对偶可行** $\lambda_i\ge0$：乘子是约束的"影子价格"——把 $f_i\le0$ 放松成 $f_i\le\epsilon$，最优值改善约 $-\lambda_i\epsilon$。不等式约束只能被"单向"顶住（多推一点边界一定不会更差），故其价格非负；等式约束 $h_j$ 可双向变形，故 $\nu_j$ **无符号约束**。这正对应 §3.1 接触"只能推不能拉"$\lambda_n\ge0$ 的单边性。
> 4. **互补松弛** $\lambda_if_i=0$（**不是额外假设，而是第 1 步的副产品**）：Farkas 锥**只由活跃约束构成**——对不活跃约束（$f_i<0$，离边界尚有余量）我们直接令 $\lambda_i=0$，于是 $\lambda_if_i=0$ 自动成立；对活跃约束则 $f_i=0$，故 $\lambda_if_i=\lambda_i\cdot0=0$。两种情形合起来即 $\lambda_if_i=0$。直觉：**只有顶在边界上的约束才可能有正影子价格，有余量的约束对最优毫无发言权**。这一条正是下一节 §3.1 接触互补、以及 §4.3 内点法所松弛的那个对象。

> [!important] 跨原理联系：KKT 互补松弛 = 接触 LCP
> 把 KKT 互补松弛 $\lambda_i f_i=0$ 与 [[ContactMechanics#5.1 互补条件与 LCP 的构建|接触 LCP]] 的 $0\le\phi(q)\perp\lambda_n\ge0$ 并排看——**它们是同一个数学对象**：距离 $\phi$ 是"约束 $f$"、法向力 $\lambda_n$ 是"乘子 $\lambda$"，"要么分离要么受力"就是"要么约束松要么乘子零"。**接触力学的核心约束，本质上是优化的 KKT 条件。** 这一眼看穿，你就同时拿到了 [[ContactMechanics]]、[[Dynamics]] 接触求解、与本讲 §3 的钥匙。
>
> 推论：① 凸问题 + Slater ⇒ KKT 是全局最优的**充要**条件（这是凸优化能被高效求解的根本）；② 内点法每步在解一个"把互补条件松弛成 $\lambda_if_i=-\mu$"的扰动 KKT 系统（§4）；③ Safe RL 的拉格朗日法（[[ControlTheory|约束 MDP]]）也是在解这套对偶-KKT。

---

## 3. 接触如何毁掉优化：互补约束与非凸景观

> [!tip] 本节四拍
> **直觉**（端杯那一瞬，接触从"无"变"有"——优化器为什么会在这里崩）→ **推导**（互补约束 LCP；非凸景观的鞍点/虚假极小）→ **对比**（好景观 PL/RSI vs 坏景观；硬接触 vs 平滑近似）→ **落点**（这三种"坏"催生了 §4 的求解器谱系与 §5 的演进）。

### 3.1 互补约束：接触把可行域撕成"坐标轴的并集"

刚体接触要求满足 Signorini 条件（非穿透）。无摩擦最简形式即一个**线性互补问题 (LCP)**（详见 [[ContactMechanics#5.1 互补条件与 LCP 的构建|ContactMechanics §5.1]]）：

$$0\le\phi(q)\ \perp\ \lambda_n\ge0,$$

三条逻辑合一：① 非穿透 $\phi(q)\ge0$（$\phi$ 是 SDF，见 [[ComputationalGeometry|SDF]]）；② 单边力 $\lambda_n\ge0$（只能推不能拉）；③ 互补 $\phi\cdot\lambda_n=0$（**要么分离 $\phi>0,\lambda=0$，要么接触 $\phi=0,\lambda\ge0$**）。加摩擦后是库伦锥 $\mathcal K(\mu)=\{(\lambda_n,\lambda_t)\mid\|\lambda_t\|\le\mu\lambda_n\}$，且最大耗散原理要求滑动时 $\lambda_t$ 反平行于切向速度。

> [!warning] 为什么这是梯度优化的噩梦（端杯瞬间发生了什么）
> - **非凸**：互补可行域是"坐标轴的并集"（$\phi=0$ **或** $\lambda=0$），不是凸集——§2.1 的全部好处此刻失效。
> - **梯度消失/爆炸**：未接触时 $\partial\lambda/\partial q\equiv0$（手离杯还有距离，再怎么动力都是零，优化器**收不到任何信号**）；接触瞬间梯度理论上 $\to\infty$（刚体碰撞）。端杯那一刻，优化器要么"看不见杯子"，要么被无穷梯度甩飞。
> - **模态分裂**：$N$ 个潜在接触点 → $2^N$（含滑/滞则 $3^N$）个离散模态；模态切换处动力学方程突变。

### 3.2 非凸景观：鞍点、虚假极小与"好景观"的判据

> [!note] 教科书参考
> 本节非凸景观部分基于 Arora et al. *Theory of Deep Learning* Ch.6–7。轨迹优化与深度学习共享这套几何语言。

把目标 $f(w)$ 的"地形"分类：**全局极小**（处处最低）、**虚假局部极小**（局部最低但 $f>f^*$，梯度法逃不出的陷阱）、**鞍点**（$\nabla f=0$ 但 Hessian 有正负特征值）。二阶判据：$\nabla^2f\succ0$ 极小、$\prec0$ 极大、不定为鞍点。最简鞍点 $f=w_1^2-w_2^2$ 在原点。

并非所有非凸都可怕。三类"好景观"保证梯度法线性收敛到全局最优：

| 条件 | 不等式 | 直觉 |
|:--|:--|:--|
| **PL (Polyak–Łojasiewicz)** | $\|\nabla f\|^2\ge\mu(f-f^*)$ | 梯度非零 ⇒ 离最优还有距离 |
| **弱拟凸** | $\langle\nabla f,w-w^*\rangle\ge\tau(f-f^*)$ | 梯度方向与"指向最优"正相关 |
| **RSI（受限割线）** | $\langle\nabla f,w-w^*\rangle\ge\mu\|w-w^*\|^2$ | 比强凸弱、但够用 |

> [!important] 对称性 ⇒ 必然非凸 + 必然有鞍点
> 若 $f$ 有置换对称性（如神经网络神经元可互换、或多指抓取的指间对称），则把所有置换平均得到的 $\bar\theta$ 若在凸情形下也该是最优——但 $\bar\theta$ 通常退化（等价单神经元/对称塌缩）而达不到最优，**矛盾**。故对称系统**必然非凸且必然有鞍点**。这就是为什么转杯/对称抓取时优化天然多鞍点。优化的目标应是找**二阶驻点 (SOSP)** $\nabla f=0,\nabla^2f\succeq0$，而非任意 $\nabla f=0$。

> [!theorem] 鞍点逃逸：扰动梯度下降 (Ge et al. 2015)
> $w_{t+1}=w_t-\eta\nabla f(w_t)+\xi_t,\ \xi_t\sim\mathcal N(0,\sigma^2I)$。对 $L$-光滑、$\rho$-Hessian-Lipschitz 的 $f$，在 $\tilde O(1/\epsilon^2)$ 步内找到 $\epsilon$-SOSP。**机制**：鞍点处随机扰动有 $\Omega(1/d)$ 概率落进负曲率"逃逸锥"，沿负曲率方向快速滑离；负曲率区停留不超过 $O(\log d/\gamma)$ 步。
>
> **跨原理联系**：[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 的熵正则]] $-\alpha H(\pi)$ 在策略优化里正是**隐式的扰动注入**，帮助逃离对称抓取造成的鞍点——RL 的"探索"与优化的"鞍点逃逸"是同一件事的两种说法。

> [!tip] 一个可处理的特例：NTK 区间下的"凸化"（跨域链接）
> 网络足够宽时，训练动力学退化为关于预测向量的**线性 ODE**，损失对预测是凸二次、全局收敛有保证——非凸景观里一个 tractable subclass。严格推导（特征分解收敛速率、Rademacher 泛化界）见 [[RepresentationLearning|RepresentationLearning §6.3.7]]。它解释了"为何过参数化世界模型能从 <1h 真机数据稳定微调"。

### 3.3 接触优化的复杂度困境与平滑化权衡

把上面三条合起来，接触优化为何特别难就一目了然：**非凸**（互补可行域）+ **非光滑**（接触瞬间梯度断裂）+ **组合**（$3^N$ 模态）。应对的核心手段是"平滑化"——但平滑度、精度、开销三者互相拉扯：

| 松弛方法 | 光滑性 | 精度损失 | 开销 |
|:--|:--|:--|:--|
| **Sigmoid 松弛** | $C^\infty$ | $O(\epsilon)$ | 低 |
| **Fischer–Burmeister** | $C^1$ | 极限下精确 | 中 |
| **随机平滑** | 期望意义光滑 | $O(\sigma)$ | 高（需采样） |

> [!important] 本节落点
> "梯度断裂"是接触优化的万恶之源。§5 的演进史，本质就是一部**修复梯度流**的历史（软接触、隐式微分、随机平滑都是在让优化器重新"感觉"到接触）；§4 则先回答："梯度有了，用什么求解器吃它最快？"

---

## 4. 求解器谱系：从一阶到二阶到内点【收敛速度的对比脊柱】

> [!tip] 本节四拍
> **直觉**（同一个倒水子问题，GD 要几千步、Newton 几步——差距从哪来？）→ **推导**（收敛率与条件数）→ **对比**（一阶 / 二阶 / 内点，横向对比表）→ **联系**（Gauss-Newton↔iLQR↔[[ReinforcementLearning|Bellman]]；内点↔§2.3 KKT）。

> [!tip] 参考资料
> 详见 [[Books/Optimization in Theory and Practice.pdf]] (Wright 2025) §2–4。

### 4.1 用什么衡量"快"：收敛率与条件数

无约束 $\min_x f$ 的近似最优：一阶 $\|\nabla f\|\le\epsilon_g$，二阶再加 $\nabla^2f\succeq-\epsilon_H I$。复杂度用达到 $\epsilon$ 解所需的 oracle（$(f,\nabla f)$）调用数衡量。对 $L$-光滑 $f$，梯度下降的收敛率由**条件数** $\kappa=L/\mu$ 主宰：

| 问题类型 | GD 收敛率 | Oracle 复杂度 |
|:--|:--|:--|
| 凸、光滑 | $O(1/k)$ | $O(L/\epsilon)$ |
| **强凸**、光滑 | 线性 $(1-\mu/L)^k$ | $O(\kappa\log(1/\epsilon))$ |
| 非凸、光滑 | $O(1/\sqrt k)$（到驻点） | $O(1/\epsilon^2)$ |

> [!important] Nesterov 加速与下界
> 对凸光滑函数，最优一阶方法达 $f(x_k)-f^*\le O(L\|x_0-x^*\|^2/k^2)=O(1/k^2)$，且存在**匹配下界**——任何一阶方法都不可能更快。倒水里：接触模式固定的局部区域内代价近似强凸（满足 §3.2 的 RSI），加速法在"模式内"显著提速，这也解释了 iLQR 为何"模式内"收敛快。

### 4.2 二阶方法：用曲率把步数压到个位数

二阶法用 Hessian 建局部二次模型，$x_{k+1}=x_k-[\nabla^2f]^{-1}\nabla f$，达**超线性/二次**收敛：

| 方法 | 信息 | 每步 | 收敛 | 场景 |
|:--|:--|:--|:--|:--|
| **Newton** | Hessian | $O(n^3)$ 求逆 | 二次 | 小规模精确 |
| **BFGS** | 仅梯度 | $O(n^2)$ 秩2更新 | 超线性 | 中规模无约束 |
| **L-BFGS** | 仅梯度 | $O(mn)$ | 超线性 | 大规模无约束 |
| **Gauss-Newton** | 雅可比 $J$（$J^TJ$ 近似 Hessian） | $O(n^2)$ | 超线性 | 最小二乘 / 轨迹优化 |

> [!important] 跨原理联系：iLQR 就是动态规划结构上的 Gauss-Newton
> **iLQR/DDP**（§6）本质是把 Gauss-Newton 特化到时序（Riccati）结构上；**SQP**（§7）每步解一个 QP、其 Hessian 来自 BFGS 更新；**内点法**（§4.3）每步解一个 Newton 系统。**Newton 法是几乎所有高阶轨迹优化算法的计算内核。** 而 iLQR 的 backward pass 退化成 Riccati 递推——这与 [[ReinforcementLearning#2.2 值函数与 Bellman 方程|RL 的 Bellman 递推]]、[[ControlTheory#11. 线性二次最优控制 (LQR)|LQR]] 是**同一个最优性原理**的三处显形。一个 Riccati，串起优化、控制、RL。

### 4.3 内点法：沿"中心路径"把约束问题变成一串 Newton

线性/二次规划的两条路线对比：

| 方法 | 最坏复杂度 | 实践 |
|:--|:--|:--|
| **单纯形法** | 指数 $O(2^n)$ | 多项式（平滑分析 Spielman–Teng 解释） |
| **内点法** | $O(\sqrt n\log(1/\epsilon))$ 迭代 | 大规模首选 |

内点法的核心是追踪**中心路径**：把 KKT 互补条件 $x_is_i=0$ 松弛为 $x_is_i=\mu$，令 $\mu\to0$。

> [!note] 中心路径 Newton 系统的来历（从 KKT 到那个矩阵，逐步）
> 取标准形 LP $\min c^Tx$ s.t. $Ax=b,\ x\ge0$（$x\in\mathbb R^n$ 决策变量，$A\in\mathbb R^{m\times n}$ 约束矩阵，$b\in\mathbb R^m$；$\lambda\in\mathbb R^m$ 为等式乘子，$s\in\mathbb R^n$ 为不等式 $x\ge0$ 的乘子＝对偶松弛/影子价格）。把 §2.3 的 KKT 特化到此：
> $$\underbrace{A^T\lambda+s=c}_{\text{驻点/对偶可行}},\quad\underbrace{Ax=b}_{\text{原始可行}},\quad\underbrace{x_is_i=0}_{\text{互补}},\quad x,s\ge0.$$
> **全部难点集中在互补** $x_is_i=0$：它非光滑——解被逼到"坐标轴的并集"上（$x_i=0$ **或** $s_i=0$，正是 §3.1 那个恶魔的 LP 版），Newton 法在这种折角上无从线性化。**内点法的一招**：把它松弛成 $x_is_i=\mu>0$，迫使解走在可行域**严格内部**、离每条边界至少 $\mu$ 远，于是得到一族**处处光滑**的非线性方程 $F_\mu(x,\lambda,s)=0$：
> $$F_\mu=\begin{pmatrix}A^T\lambda+s-c\\ Ax-b\\ XS\mathbf1-\mu\mathbf1\end{pmatrix}=0,\qquad X=\mathrm{diag}(x),\ S=\mathrm{diag}(s).$$
> 现在对光滑的 $F_\mu$ 做**一步 Newton**：$F_\mu(z+\Delta z)\approx F_\mu(z)+\nabla F_\mu(z)\,\Delta z=0$，即 $\nabla F_\mu\,\Delta z=-F_\mu$。逐块求雅可比 $\nabla F_\mu$：第一行 $A^T\lambda+s-c$ 对 $(x,\lambda,s)$ 的偏导为 $(0,\,A^T,\,I)$；第二行 $Ax-b$ 为 $(A,\,0,\,0)$；第三行 $XS\mathbf1$ 对 $x$ 是 $S$、对 $s$ 是 $X$（对 $\lambda$ 为 $0$）。拼起来正是下面的系数矩阵；右端第三块 $\mu\mathbf1-XS\mathbf1$ 就是 $-F_\mu$ 的第三块（前两块在**可行**迭代下已为零，故显示为 $0$）。**每追踪一步 $\mu$，就是解一次这样的线性系统——这就是"沿中心路径把约束问题变成一串 Newton"的字面含义。**

每步解一个 Newton 系统：

$$
\begin{pmatrix}0&A^T&I\\A&0&0\\S&0&X\end{pmatrix}\!\begin{pmatrix}\Delta x\\\Delta\lambda\\\Delta s\end{pmatrix}=\begin{pmatrix}0\\0\\\mu\mathbf 1-XS\mathbf 1\end{pmatrix},\quad X=\mathrm{diag}(x),S=\mathrm{diag}(s).
$$

> [!theorem] 内点法复杂度
> 长步路径追踪在 $O(n\log(1/\epsilon))$ 次迭代内得 $\epsilon$ 解，每步 $O(n^3)$。Mehrotra 预测-校正在实践中远快于理论界。
> **倒水含义**：内点法对初值不敏感、收敛快，是抓杯力分配 QP / MPC 子问题（§7）的首选——它每步在解的，正是 §2.3 那个扰动 KKT 系统。

### 4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）

> [!tip] 本节四拍
> **直觉**（有些目标只能"跑一次才知道好不好"，压根没有梯度）→ **推导**（零阶梯度估计 → CMA-ES 四步机制）→ **对比**（CMA-ES vs MPPI vs 策略梯度：都是"采样+加权"，差在更新什么）→ **联系**（[[StochasticProcess#6. 随机最优控制：MPPI（用采样代替梯度）|MPPI]]、[[ReinforcementLearning#4.1 策略梯度定理：log-derivative 技巧|策略梯度]]、[[Final_WMTS|WMTS 任务生成器]]）。

§4.1–4.3 的求解器都吃**梯度**（甚至 Hessian）。但灵巧操作里有一类目标**求不出梯度**：
- **黑箱 rollout**：倒水"洒不洒"要跑完整条轨迹才知道，接触切换（§3）让它对控制参数**处处不可微**；
- **离散/结构目标**：奖励函数超参、课程任务的"难度是否合适"；
- **[[Final_WMTS|WMTS]] 隐空间任务生成**：任务 $\xi$ 的 fitness = 通才 zero-shot rollout 的成功率×轨迹误差——一个纯黑箱标量，无梯度可回传。

这时只能**零阶 (zeroth-order) / 无导数 (derivative-free)** 优化：只用**函数值**改进。

**从零阶梯度估计说起**（不跳步）。既然拿不到 $\nabla f$，就用采样**估**一个：在当前点 $x$ 附近撒 $\lambda$ 个扰动 $x+\sigma\epsilon_i$，用它们的函数值加权平均出一个"下降方向"。最朴素的是有限差分；更优雅的是**进化策略 (ES)** 的对数似然技巧——与 [[ReinforcementLearning#4.1 策略梯度定理：log-derivative 技巧|策略梯度]] **同一个 log-derivative 恒等式**：
$$\nabla_\theta\,\mathbb E_{x\sim\mathcal N(\theta,\sigma^2 I)}[f(x)] = \frac{1}{\sigma^2}\,\mathbb E[(x-\theta)\,f(x)]\ \approx\ \frac{1}{\sigma^2\lambda}\sum_i \epsilon_i\, f(x+\sigma\epsilon_i).$$
**这就是零阶与一阶的桥**：策略梯度是"在动作分布上"做这件事，ES 是"在参数空间"做同一件事——都不需要 $f$ 可微，只需能采样、能评估。

**CMA-ES 的核心升级**：朴素 ES 用各向同性高斯 $\mathcal N(\theta,\sigma^2 I)$ 撒点，在**病态地形**（各方向曲率悬殊，如狭长山谷）里极慢。**CMA-ES (Covariance Matrix Adaptation ES)** 让采样分布 $\mathcal N(m,\sigma^2 C)$ 的**协方差 $C$ 自适应地贴合局部地形**——等价于在线学出一个**无需 Hessian 的二阶信息**。四步迭代：

| 步 | 机制 | 直觉 |
|:--|:--|:--|
| **① 采样** | $x_k\sim m+\sigma\,\mathcal N(0,C)$，$k=1..\lambda$ | 按当前信念撒 $\lambda$ 个候选 |
| **② 评估排序** | 跑黑箱 fitness，取前 $\mu$ 名 | 只用**排名**（对 fitness 单调变换不变，极鲁棒） |
| **③ 均值更新** | $m\leftarrow\sum_i w_i x_{i:\lambda}$（加权重组，$\mu_{eff}=1/\sum w_i^2$） | 把均值挪向优胜者的加权中心 |
| **④ 协方差自适应** | **rank-$\mu$**（当代优胜者的散布 $\sum w_i\Delta x\Delta x^T$）+ **rank-one / 累积进化路径** $p_c$（跨代方向相关，加速狭长谷） | 学出"该往哪个方向、以多大各向异性撒点" |

外加**步长控制 (CSA)**：比较进化路径 $p_\sigma$ 的实际长度与随机游走期望长度——**比期望长**说明在稳步下山→增大 $\sigma$（迈大步）；**比期望短**说明在原地打转→减小 $\sigma$（精修）。

> [!important] 三种"采样+加权"优化的统一视角（记忆锚点）
> CMA-ES、MPPI、策略梯度**同宗**——都在"参考分布附近采样、按 fitness/return 加权、把分布挪向优胜者"。差别只在**更新什么**：
> | 方法 | 采样空间 | 加权方式 | 更新对象 | 归属 |
> |:--|:--|:--|:--|:--|
> | **CMA-ES** | 参数 $\theta$ | 排名 (rank-based) | 分布均值 $m$ + **协方差 $C$** | 本节 |
> | **MPPI** | 控制序列 $u_{0:H}$ | $\exp(-\tfrac1\lambda S)$ 软加权 | 名义控制序列 | [[StochasticProcess#6. 随机最优控制：MPPI（用采样代替梯度）\|随机过程 §6]] |
> | **策略梯度** | 动作 $a$ | advantage $\times\nabla\log\pi$ | 策略网络参数 | [[ReinforcementLearning#4.1 策略梯度定理：log-derivative 技巧\|RL §4.1]] |
> **一句话记忆**：CMA-ES 学的是"**在哪撒点**（协方差几何）"，MPPI 学的是"**这一时刻怎么动**"，策略梯度学的是"**给定状态怎么动**"。协方差自适应≈自然梯度/信息几何（用 Fisher 度量拉直参数空间），是 CMA-ES 逼近二阶而不算 Hessian 的秘密。

> [!tip] 对 WMTS 的直接落点
> [[Final_WMTS|WMTS]] 的隐空间任务生成器正是"CVAE 映射到低维隐空间 → **CMA-ES 在隐空间演化任务** → 通才 zero-shot rollout 评 fitness → 盲区任务派给 Oracle"。用 CMA-ES 而非梯度，是因为 fitness（成功率×误差×凸包距离）是**黑箱、非光滑、且要跨整条 rollout 才能算**。这条线与[[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|世界模型"无知即课程"]]、开放式演化（[[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]]）汇合——进化算法是自动课程搜索的天然引擎：它把"采样+加权"从**参数空间**（找一个好策略）**抬到任务空间**（找"此刻最该学的任务"），fitness 越低（越难、越落在通才盲区）的任务被赋越高权重、被优先生成——这在数学上等价于 [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|RL §7.3 自动课程]] 里用 regret / learning-progress 当"还能学多少"的代理来选任务。**CMA-ES 恰是那台"任务空间搜索引擎"的一种实现**（POET 用群体进化、PLR 用优势幅度，与 CMA-ES 的协方差自适应同属"用采样+加权在任务分布上爬坡"）。

> [!important] 本节落点（接 §5）
> 求解器谱系告诉我们"梯度/Hessian 有了能多快收敛"。但 §3 说接触会**毁掉**梯度。于是真正的灵巧操作优化史，是一部"如何既保留物理接触、又让这些快速求解器能用上"的演进史——这就是 §5。

---

## 5. 演进脉络：从模态预设到接触隐式（修复梯度流的四个阶段）

> [!tip] 本节四拍
> **直觉**（端杯这一步，"何时该碰杯壁"到底谁来决定？）→ **推导**（四个阶段如何一步步把"模式决策"从人手里交给求解器）→ **对比**（RRT→MIQP→CITO→可微物理，各自的 value-add 与失效）→ **落点**（现代答案＝把接触力当决策变量 + 平滑化让梯度穿过接触）。

这条演进史回答同一个问题的不同答案：**"接触模式（何时碰、何时滑、何时离）由谁决定？"**

### 5.1 阶段一：模态预设（人来决定）

**RRT/PRM + 准静态抓取**：人先指定"先到预抓取点、再闭合手指"，过程忽略惯性。它为何失效已在 §1.3 详述——割裂过程与结果、概率零陷阱、几何可行≠物理可行。**一句话**：把"何时接触"交给人预设，无法处理倒水这类接触中带相对运动的任务。

### 5.2 阶段二：MIQP 模态调度（整数变量来决定）

为处理接触的离散性，引入整数 $z\in\{0,1\}$ 表示接触态，用 **Big-M** 写约束：

$$\lambda\le Mz,\qquad \phi(q)\le M(1-z).$$

**value-add**：数学严谨、给出（离散精度下的）全局最优。**失效**：**组合爆炸**——$N_c$ 个潜在接触点、$T$ 步轨迹 → $(2^{N_c})^T$ 个离散组合，NP-hard。这正是 [[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 那一讲里 $3^5=243$ 模式爆炸]]的优化版表述——**同一个组合爆炸，逼出了两个领域各自的解法**（RL 用策略隐式学、优化用下一阶段的连续松弛）。

### 5.3 阶段三：接触隐式轨迹优化 CITO（求解器自己发现）

> 关键人物：Michael Posa、Russ Tedrake (MIT)。

**突破**：不用整数变量，把接触力 $\lambda$ 当**连续决策变量**，把 LCP 互补约束**直接塞进 NLP**：

$$
\min_{x_{1:T},u_{1:T},\lambda_{1:T}}\sum_t \mathrm{Cost}(x_t,u_t)\quad
\text{s.t. } \text{Dynamics}(x_t,u_t,\lambda_t)=0,\ \ 0\le\phi(q_t)\perp\lambda_t\ge0.
$$

**value-add**：**无需预设接触序列**——求解器自动"发现"何时该碰杯壁、何时借桌面借力（extrinsic dexterity）；规划与控制统一在一个框架。**怀疑视角（缺陷）**：① 带互补约束的数学规划 (MPCC) 违反标准约束规范 (LICQ)，最优解处乘子可能无界；② 求解器（IPOPT/SNOPT）常卡在不可行局部极小，需极精确的 warm-start；③ 一次求解几秒到几分钟，**无法直接实时**。

### 5.4 阶段四：可微物理与平滑化（让梯度穿过接触）

> 关键人物：Todorov (MuJoCo)、Levine、Manchester。

**问题**：要用极速的 iLQR/DDP，需动力学二阶可微；刚体接触破坏了它。**解法**：在物理模型上妥协换平滑——把硬 LCP 松弛为平滑函数，如

$$\lambda_n(\phi)\approx\frac{k}{1+\exp(\beta\phi(q))}\quad(\text{Sigmoid 软接触}),$$

或在代价里加 log-barrier 惩罚穿透。**Insight**：平滑后接触不再是突变开关，而是一道陡坡——梯度能**穿透**接触事件：手还没碰到杯子时，$\phi$ 的微小变化就引起力的微小变化，给出非零梯度，等于在对优化器说"再靠近一点，力就来了"。这正是 §3.1"梯度消失"的解药。另一路是 Manchester 的**变分积分器**（从离散拉格朗日量出发），接触时能量守恒更好、梯度更稳。

> [!important] 🔬 同伦优化：用"从易到难的连续路径"逃局部极小（[[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack, ICLR 2025]]）
> CITO 易卡局部极小。**同伦/延拓法 (Continuation Method)** 构造一条从"简单问题"到"目标问题"的连续路径 $H(\lambda)=(1-\lambda)\cdot\text{简单}+\lambda\cdot\text{目标},\ \lambda:0\to1$，逐步逼近。对倒水/转笔：
> ```
> λ=0.0 静态抓握 → 0.3 仅平移 → 0.7 小幅旋转 → 1.0 完整动态操作
> ```
> **跨原理联系**：这与 [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|课程学习]]（"课程即 continuation method"）、与思维链 (CoT) 的"中间步骤降低非凸性"是同一思想——**先解一个凸/易的近邻问题，再连续形变到难问题**。同伦把 §3 的"坏景观"问题，用"渐进改变地形"绕开。

> [!important] 🔬 阻抗参数的凸辨识（[[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking|Prosthesis VI, IEEE TRO 2022]]）
> 阻抗参数 $(K,B,\theta_{eq})$ 怎么自动定？**关键洞察**：固定平衡角 $\theta_{eq}$ 后，$\tau=-K(\theta-\theta_{eq})-B\dot\theta$ 关于 $(K,B)$ 是**线性**的！于是两步凸优化：先从运动学估 $\theta_{eq}$，再凸 QP 解 $\min_{c^K,c^B}\sum_n\|\tau_n^{data}-\tau_n^{model}\|^2$。把阻抗写成相位/速度/任务参数的 B-spline 连续函数。**倒水含义**：抓取力"随操作相位如何变化"可从演示数据凸辨识学到——这条把 [[ControlTheory#3.4 学习型变阻抗：RL × 阻抗的桥|变阻抗控制]] 接到了优化上。

---

## 6. 核心算法实现：iLQR/DDP 与"让梯度穿过接触"的三方案

> [!tip] 本节四拍
> **直觉**（iLQR 在问："此刻状态/控制动一点点，总 Cost 怎么变？"）→ **推导**（backward Riccati + forward rollout）→ **对比**（让梯度穿过接触的三方案 A/B/C）→ **落点**（`model.derivatives` 那一行，是接触优化全部难点的所在）。

### 6.1 iLQR/DDP：动态规划结构上的 Gauss-Newton

iLQR 是 DDP 的变体（略去二阶动力学项以提速）。它在当前轨迹附近做**局部二次近似**，利用 Bellman 最优性做 backward/forward 迭代，达二阶收敛。复杂度 $O(T(n_x^3+n_u^3))$——比直接解 NLP 的 $O((Tn_x)^3)$ 快得多，因为它利用了**时序结构**（Riccati 递推）。

> [!note] iLQR 的 backward pass = 离散 Riccati = LQR
> 每次迭代把非线性动力学线性化为 $\delta x_{k+1}=A_k\delta x_k+B_k\delta u_k$、代价二次近似，此时 backward pass **退化为标准离散时间 Riccati 递推**。其闭式解、稳定性与最优反馈律见 [[ControlTheory#11. 线性二次最优控制 (LQR)|ControlTheory §11]]。**理解 LQR 是理解 iLQR 收敛性的前提**——再次印证 §4.2 的"一个 Riccati 串起优化/控制/RL"。

> [!note] Backward pass 每一步从哪来：Bellman → Q 二次展开 → 消 $\delta u$ → Riccati（逐行对应下方代码）
> 记值函数 $V_t(x)$＝从 $t$ 步到末端沿最优控制的**剩余最小总代价**（cost-to-go，单位＝代价量纲）。它满足 **Bellman 最优性方程**（与 [[ReinforcementLearning#2.2 值函数与 Bellman 方程|RL 的 Bellman 方程]] 是同一个方程，只是这里最小化"代价"、RL 最大化"回报"，$\min\leftrightarrow\max$、$\ell\leftrightarrow r$）：
> $$V_t(x)=\min_{u}\big[\underbrace{\ell(x,u)}_{\text{本步代价}}+\underbrace{V_{t+1}(f(x,u))}_{\text{下步 cost-to-go}}\big].$$
> **第 1 步——展开方括号里的量为 $Q_t$**。在名义轨迹 $(\bar x_t,\bar u_t)$ 附近取扰动 $\delta x,\delta u$，把 $Q_t=\ell+V_{t+1}\!\circ f$ 二次展开，其一、二阶系数（用 $V'_x,V'_{xx}$ 记 $t{+}1$ 时刻的值函数导数、$f_x,f_u$ 即线性化的 $A_t,B_t$）为
> $$Q_x=\ell_x+f_x^TV'_x,\quad Q_u=\ell_u+f_u^TV'_x,\quad Q_{xx}=\ell_{xx}+f_x^TV'_{xx}f_x,\quad Q_{uu}=\ell_{uu}+f_u^TV'_{xx}f_u,\quad Q_{ux}=\ell_{ux}+f_u^TV'_{xx}f_x.$$
> **这正是下方代码的第 2 步那三行**——每个 $Q$ 项＝"本步代价的导数 $\ell_\bullet$" ＋ "动力学把下步值函数曲率 $V'_{xx}$ 折算回来"。
> **第 2 步——对 $\delta u$ 求极小**。$Q_t$ 关于 $\delta u$ 是二次的，令 $\partial Q_t/\partial\delta u=Q_u+Q_{uu}\delta u+Q_{ux}\delta x=0$，解出最优扰动
> $$\delta u^*=\underbrace{-Q_{uu}^{-1}Q_u}_{k\ \text{（前馈增益）}}+\underbrace{(-Q_{uu}^{-1}Q_{ux})}_{K\ \text{（反馈增益）}}\,\delta x,$$
> 即代码第 4 步的 $k,K$。可解的前提是 $Q_{uu}\succ0$；接触任务里 $Q_{uu}$ 常不定，故第 3 步加 Levenberg–Marquardt 正则 $Q_{uu}+\lambda I$ 把它强行拉正（等价于给更新步长加阻尼、限制在信赖域内）。
> **第 3 步——回代得 $V_t$，即 Riccati**。把 $\delta u^*$ 塞回 $Q_t$，$V_t$ 仍是 $\delta x$ 的二次型，其系数递推
> $$V_x=Q_x+K^TQ_{uu}k+K^TQ_u,\qquad V_{xx}=Q_{xx}+K^TQ_{uu}K+K^TQ_{ux}+Q_{ux}^TK,$$
> **正是代码第 5 步、也就是离散时间 Riccati 方程**。从 $t=T$（末端 $V_T$＝终端代价）反传到 $t=0$，值函数曲率 $V_{xx}$ 层层"卷"回来，等同 [[ControlTheory#11. 线性二次最优控制 (LQR)|LQR]] 里的 Riccati 矩阵 $P_t$。**一个反向递推同时是：最优控制的 Riccati、RL 的 Bellman、iLQR 的 backward pass**——[[ControlTheory#10.4 被动性与"价值即 Lyapunov"|"价值即 Lyapunov"]]这条暗线在此第三次显形（值函数 $V$ 既是"还要花多少代价"，又是控制论里那个下降的 Lyapunov 证书）。

```python
import numpy as np
# iLQR 核心逻辑（去除防御性代码，聚焦数学）
def backward_pass(model, cost, x_seq, u_seq, lamb_reg):
    """解 Riccati 反向递推，得前馈增益 k 与反馈增益 K。"""
    T, n_x, n_u = len(u_seq), x_seq.shape[1], u_seq.shape[1]
    k_seq  = np.zeros((T, n_u))            # 前馈增益
    K_seq  = np.zeros((T, n_u, n_x))       # 反馈增益
    Vx, Vxx = cost.terminal_derivatives(x_seq[-1])   # 末端值函数导数
    for t in range(T - 1, -1, -1):
        # 1) 线性化动力学 + 二次化代价 —— ★接触可微性就进在这一行★
        fx, fu = model.derivatives(x_seq[t], u_seq[t])   # 必须捕捉"穿过接触"的梯度
        lx, lu, lxx, luu, lux = cost.step_derivatives(x_seq[t], u_seq[t])
        # 2) Q 函数（动作-值）展开
        Qx, Qu  = lx + fx.T @ Vx,  lu + fu.T @ Vx
        Qxx, Quu = lxx + fx.T @ Vxx @ fx,  luu + fu.T @ Vxx @ fu
        Qux = lux + fu.T @ Vxx @ fx
        # 3) 正则化（Levenberg–Marquardt）：接触任务里 Quu 常不定，等价于给更新加阻尼
        Quu_reg = Quu + lamb_reg * np.eye(n_u)
        Quu_inv = np.linalg.inv(Quu_reg)
        # 4) 最优增益： u* = k + K·δx
        k, K = -Quu_inv @ Qu, -Quu_inv @ Qux
        # 5) 回填值函数到 t-1
        Vx  = Qx + K.T @ Quu @ k + K.T @ Qu
        Vxx = Qxx + K.T @ Quu @ K + K.T @ Qux + Qux.T @ K
        Vxx = 0.5 * (Vxx + Vxx.T)          # 对称化防数值漂移
        k_seq[t], K_seq[t] = k, K
    return k_seq, K_seq

def forward_pass(model, x_seq, u_seq, k_seq, K_seq, alpha=1.0):
    """用增益 rollout 新轨迹；alpha 为 line search 回溯系数。"""
    x_new = [x_seq[0]]; u_new = []
    for t in range(len(u_seq)):
        du = alpha * k_seq[t] + K_seq[t] @ (x_new[-1] - x_seq[t])
        u_new.append(u_seq[t] + du)
        x_new.append(model.step(x_new[-1], u_new[-1]))   # 非线性 rollout
    return np.array(x_new), np.array(u_new)
```

### 6.2 让梯度穿过接触的三方案（`model.derivatives` 的成败手）

上面代码里 `model.derivatives` 是命门：直接用刚体引擎（Bullet/ODE）梯度往往是零或错的（§3.1）。三条修复路线：

| 方案 | 做法 | 优点 | 缺点 |
|:--|:--|:--|:--|
| **A 平滑接触** | Sigmoid/log-barrier 近似 Signorini，$\partial\lambda_n/\partial q$ 处处非零 → 形成"力场"引导手指 | 最实用，适合 DDP | $\beta$ 越大越像刚体但梯度越 stiff、越不稳 |
| **B 隐式微分** | 保留硬 LCP，对解 $\lambda^*$ 用隐函数定理 $\frac{\partial\lambda^*}{\partial u}=-(\frac{\partial R}{\partial\lambda})^{-1}\frac{\partial R}{\partial u}$，**不必反传迭代求解器** | 物理真实、梯度精度与迭代数无关 | active set 变化时 $\partial R/\partial\lambda$ 奇异，需广义雅可比 |
| **C 随机平滑** | 状态/参数加噪取期望，把非光滑 Cost 抹平 | 可用不可微/黑盒 Cost | 开销高，用于 MPPI / ES |

> [!note] 隐函数定理为何给出方案 B 的梯度（逐步推导，不跳步）
> 硬 LCP 的解 $\lambda^*$ **没有显式公式**（是求解器迭代出来的），但它由一组**最优性/互补残差**隐式定义：$R(\lambda^*,u)=0$，其中 $R$ 打包了动力学等式与互补条件（$u$ 为控制/参数，$\lambda^*$ 为接触力解，$R$ 与 $\lambda,u$ 同维）。我们要 $\partial\lambda^*/\partial u$（接触力对控制的灵敏度），却**不想反传求解器内部的几十步迭代**。招数：把 $\lambda^*$ 看成 $u$ 的隐函数，对恒等式 $R(\lambda^*(u),u)\equiv0$ 两边关于 $u$ 求全导数（链式法则，$\lambda^*$ 随 $u$ 变、$u$ 也直接进 $R$）：
> $$\frac{\partial R}{\partial\lambda}\,\frac{\partial\lambda^*}{\partial u}+\frac{\partial R}{\partial u}=0\quad\Longrightarrow\quad \frac{\partial\lambda^*}{\partial u}=-\Big(\frac{\partial R}{\partial\lambda}\Big)^{-1}\frac{\partial R}{\partial u}.$$
> **关键红利**：右端只用到**收敛点** $\lambda^*$ 处的两个偏导，与"求解器迭代了几步、用的是 PGS 还是内点"**完全无关**——这就是表中"梯度精度与迭代数无关"的来源，也是 [[ContactMechanics#6.2 实现可微的三条路径|可微接触物理]] 与可微优化层（OptNet 等）**共用的同一套数学**（接触非光滑暗线：三个领域都靠隐式微分把"不可反传的求解器"变成"一次线性解"）。**失效边界**：当 active set 切换（某接触点从"受力 $\lambda>0$"跳到"分离 $\phi>0$"）时，$\partial R/\partial\lambda$ 在折角处**奇异、逆不存在**，须退到广义雅可比或局部松弛——这正是 §3.1 非光滑性在梯度层的复现。

> [!note] 跨原理联系
> 方案 B 的隐函数定理梯度，与 [[ContactMechanics#6.2 实现可微的三条路径|可微接触物理]] 是同一套数学；方案 C 的随机平滑，与 [[StochasticProcess|MPPI]]、[[ReinforcementLearning#5.4.1 时间一致探索：从白噪声到自回归过程|RL 的探索噪声]] 同源。三个领域在"如何对不可微对象求可用梯度"上殊途同归。

---

## 7. 实时闭环：模型预测控制 (MPC)

> [!tip] 本节四拍
> **直觉**（倒水时水在流、质心在漂，离线轨迹立刻过时——必须边走边重规划）→ **推导**（Receding Horizon + RTI + warm-start）→ **对比**（基于梯度的 SQP-MPC vs 基于采样的 MPPI）→ **联系**（MPC 是优化与 [[ControlTheory|控制论]] 的交界面）。

轨迹优化（§6）多是离线规划器。要上真机，须经 **Receding Horizon Control** 变成 MPC：每步只解一小段、只执行第一个动作、再重解。

> [!note] 古典前置：一段 horizon 如何"凝聚"成一个 QP
> 本节讲的都是接触隐式 / 非光滑 MPC；它们的**骨架**是最基础的线性 MPC——把 horizon 内的动力学等式约束 $x_{t+1}=A x_t+B u_t$ 逐步回代、消去中间状态，整段轨迹优化**凝聚 (condensation)** 成一个只以控制序列 $u_{0:H-1}$ 为变量的稠密 QP（状态被显式写成初态 $x_0$ 与控制序列的仿射函数）。这套"凝聚"构造、以及稀疏 (sparse) vs 稠密 (dense) QP 的规模取舍，是读懂下面 §7.2 SQP/RTI 的前置语言，详见 [[ControlTheory#8.1 古典前置：基础线性 MPC 的 QP 凝聚 (Condensation) 构造|ControlTheory §8.1]]。**一句话对接**：§7.2 SQP 每步解的那个 QP，正是这套凝聚 QP 在非线性动力学上"线性化一次 Newton"的版本——古典线性 MPC 是它的 $A,B$ 常值特例。

### 7.1 实时性挑战：接触事件比控制周期还快

灵巧操作的接触事件 ~1–5ms，而 MPC 若 >20–30ms 才解完，机器人就出现"盲区"：指尖滑过杯沿、控制器还没反应，杯子已弹飞。这是 **Sim-to-Real Gap 在时间维度上的体现**——再准的模型，解得太慢也没用。

### 7.2 基于梯度：SQP 与实时迭代 (RTI)

现代框架（OCS2、Acados）用 **SQP**：不每步重解完整 NLP，只做一次 QP 近似（**Real-Time Iteration**）。靠 **warm-start** 复用上一时刻的解 $x^{k+1}_{init}=\mathrm{Shift}(x^k_{sol})$——物理连续性使其通常很有效。**但接触瞬间（impact）解会跳变，warm-start 失效、求解器可能发散**。对策：**Contact Schedule Smoothing**——不强制接触发生在某一精确时刻，而是松弛互补约束、允许接触时间在窗口内浮动。

> [!note] SQP 的 QP 子问题从哪来：对 KKT 系统做 Newton（不跳步）
> **SQP (Sequential Quadratic Programming)** 直译"序贯二次规划"——把一个难的非线性规划 (NLP) 拆成一串 QP 来逼近。它与内点法（§4.3）是**同一个思想的两种落法**：都对 KKT 系统做 Newton，只是处理不等式的方式不同（内点法用障碍/中心路径把不等式变光滑，SQP 用活跃集直接线性化）。推导：对 NLP $\min_x f_0(x)$ s.t. $h(x)=0$（等式，含动力学约束）、$g(x)\le0$，其 KKT（§2.3）是关于 $(x,\nu,\lambda)$ 的**非线性方程组**。对它做**一步 Newton**，可证等价于求解如下 QP（决策变量为步长 $\Delta x$）：
> $$\min_{\Delta x}\ \tfrac12\Delta x^T\big(\underbrace{\nabla^2_{xx}L}_{\text{拉格朗日量 Hessian}}\big)\Delta x+\nabla f_0^T\Delta x\quad\text{s.t. }\ h+\nabla h^T\Delta x=0,\ \ g+\nabla g^T\Delta x\le0.$$
> **逐项对应**：① 目标的二次项是**拉格朗日量 $L=f_0+\nu^Th+\lambda^Tg$ 的 Hessian**（不是 $f_0$ 的——因为约束的曲率也必须进来，这一点常被跳过），实践中用 BFGS（§4.2）近似省掉二阶导；② 约束是原等式/不等式在当前点的**一阶线性化**。解出 $\Delta x$、更新 $x\leftarrow x+\alpha\Delta x$（$\alpha$ 为线搜索步长），重复至收敛。**Real-Time Iteration (RTI)** 是它的极致近似：每个控制周期**只做一次**这样的 QP（不迭代到收敛），把"没解完的误差"靠 warm-start 顺延到下一周期——用"每步最优性"换"实时性"。这与 iLQR（§6.1）互为表里：iLQR 利用**时序 Riccati 结构**消元、SQP 保留**一般约束结构**，但**内核都是 Newton-on-KKT**（§4.2 那句"Newton 是几乎所有高阶轨迹优化的计算内核"在此再次兑现）。

> [!note] warm-start 为什么有效、RTI 为什么"一步就够"（补跳步 + 单位）
> **warm-start 的数学理由**：把 MPC 每个周期的问题看成参数 $\theta$（当前状态 $x_0$，以及倒水里时变的质心/惯量）连续变化的一族 NLP。在满足 LICQ + 二阶充分条件的解处，**解映射 $\theta\mapsto z^*(\theta)$ 是 Lipschitz 连续的**（$z$＝整段轨迹的原始-对偶变量）。这不是新定理，正是 §6.2 那条**隐函数定理**作用在 KKT 系统 $F(z,\theta)=0$ 上：$\partial z^*/\partial\theta=-(\nabla_z F)^{-1}\nabla_\theta F$，只要 KKT 雅可比 $\nabla_z F$ 非奇异。于是相邻周期 $\|\Delta\theta\|$ 小 $\Rightarrow\|z^*(\theta_{k+1})-z^*(\theta_k)\|\le L_z\|\Delta\theta\|$ 也小（$L_z$＝解对参数的灵敏度/Lipschitz 常数，量纲＝轨迹变量/参数变量）——把上一时刻的解**沿时间平移一格**（$\mathrm{Shift}$），就落进新问题的 Newton 收敛域内。
> **RTI 的"一步够"**：因 warm-start 已在收敛域内，SQP 的一次 Newton 步是**局部收缩**（$\|z_{k+1}-z^*\|\le c\|z_k-z^*\|^2$，二次收缩）；单步就把优化残差压到与"模型-真机失配"同阶——再多迭代的收益会被建模误差淹没，不划算。这就是"每周期只解一次 QP、把没解完的残差顺延到下周期"在数学上站得住的原因。
> **跨原理联系（[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|continuation 暗线]]）**：warm-start 本质是**在时间轴上做同伦**——把"上一时刻已解好的问题"当简单端点，沿真实动力学的连续形变把它推到"这一时刻的新问题"，连续参数就是**物理时间**本身。这与 §5.4 的同伦优化、[[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|课程即 continuation]] 共用同一把"从已解连续变形到难解"的钥匙。而接触 impact 让 $\theta$（接触模式）**突跳**、打断这条连续性——$\|\Delta\theta\|$ 不再小、Lipschitz 界失效，正是本节"warm-start 在 impact 处失效"的根，也再次落到"[[Optimization#3.1 互补约束：接触把可行域撕成"坐标轴的并集"|接触的非光滑性]]"这条全库暗线。

### 7.3 基于采样：MPPI（用并行换梯度）

梯度法易陷局部极小（§3）；采样式 MPC（MPPI, Model Predictive Path Integral）借 GPU 并行同时模拟数千条轨迹，按代价加权平均：

$$u_t^*=\frac{\sum_k w_k u_t^{(k)}}{\sum_k w_k},\qquad w_k=\exp\!\big(-\tfrac1\lambda S(u^{(k)})\big).$$

| | 优势 | 劣势 |
|:--|:--|:--|
| **MPPI** | ① 不需梯度（可用二值成功率等不可微 Cost）；② 天然处理多模态；③ 对模型误差不敏感 | **维数灾难**：24-DoF 手纯随机采样几乎采不到"指尖正好捏住杯沿"这种低概率高精度事件 |

> [!note] "并行换梯度"的账怎么算：为什么 MPPI 天生吃 GPU（补跳步 + 单位）
> **结构**：MPPI 每周期撒 $K$ 条控制序列 $u^{(k)}_{0:H-1}$（$K\sim10^3$–$10^4$ 条，$H$＝预测步数），每条独立 rollout 一遍动力学得代价 $S(u^{(k)})$（单位＝代价量纲）。**命门在"独立"**：$K$ 条 rollout 之间零耦合、不共享中间状态——这是**尴尬并行 (embarrassingly parallel)** 的教科书样例，正好铺满 GPU 数千个核，"一个物理步跑 $K$ 条"与"跑 1 条"几乎等时。于是 MPPI 用**宽度**（$K$ 条并行 rollout）换掉了梯度法要的**深度**（Newton 迭代必须串行）——这也是它必须配 Isaac Gym / Brax 这类 GPU 批量仿真器（§10）才实时的根本原因。
> **温度旋钮**：权重 $w_k=\exp(-S_k/\lambda)\big/\sum_j\exp(-S_j/\lambda)$ 是对代价做 **softmin**（$\lambda>0$ 温度，单位＝代价量纲）：$\lambda\to0$ 退化成"只取最优那条"（贪心、高方差）、$\lambda\to\infty$ 退化成"所有样本等权平均"（保守、抹平多峰）。它与 §4.3 内点法的 $\mu$、[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 温度 $\alpha$]] 是同一把"探索↔利用"旋钮（§9 暗线四）。
> **维数灾难的定量**：要盲采到"指尖正好捏住杯沿"这类目标流形，随机命中概率随控制维度 $n_u\times H$ **指数衰减**，$K$ 必须指数增长才能覆盖——GPU 也救不了。这正是 §9 主张"iLQR 生成 nominal 轨迹 + 在其邻域采样"的原因：**把全空间盲采压缩成 nominal 附近的局部采样，让固定的 $K$ 重新够用**。
> **跨原理联系（[[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）|采样+加权 暗线]]）**：MPPI 的"撒 $K$ 条 → 按 $\exp(-S/\lambda)$ 加权 → 挪名义序列"，与 CMA-ES（§4.4）"撒 $\lambda$ 个 → 按排名加权 → 挪均值/协方差"、策略梯度"采动作 → 按 advantage 加权 → 挪网络"是**同一台机器的三种投影**，其共同物理根是 [[StochasticProcess#6.2 物理根：自由能最小化与重要性采样|自由能最小化 / 重要性采样]]。差别仅在采样空间（控制序列 vs 参数 vs 动作）与"挪什么"。

> [!tip] 混合方案与跨域联系
> 实践常用 **iLQR 生成 nominal 轨迹 + 在其附近做 MPPI 采样**：iLQR 是精准的"手术刀"、MPPI 是鲁棒的"大锤"。MPPI 的重要性采样权重 $w_k=\exp(-S/\lambda)$ 与 [[StochasticProcess|自由能最小化]] 同形，其温度 $\lambda$ 与 [[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 温度]]、§10 的 test-time RL 是同一探索-利用旋钮。MPC 正是 Optimization 与 [[ControlTheory#8. 接触隐式模型预测控制 (Contact-Implicit MPC)|ControlTheory 的接触隐式 MPC]] 的交界面。

---

## 8. 深度专题：可微抓取合成 (Differentiable Grasp Synthesis)

> [!tip] 本节四拍
> **直觉**（"抓得稳不稳"要能对关节角求导，才能塞进轨迹优化）→ **推导**（把不可微的 Ferrari-Canny 换成可微力闭合能量）→ **对比**（凸包指标 vs SDF 势场代理）→ **落点**（SDF 让"还没接触"时梯度就能拉手指就位——呼应 §5.4）。

### 8.1 传统指标为何不可微

Ferrari-Canny $\epsilon$-metric 要算 6D wrench space 凸包、再求原点到凸包面的最短距离——纯几何、难对关节角 $q$ 求导（§2.1 已点出它是逐点上确界的产物）。塞进轨迹优化的 Cost 就无法回传梯度。

### 8.2 可微力闭合能量 + SDF 引导

> [!note] 承接：我们到底在替换 $Q_1$ 的哪一处不可微（精确来历）
> §8.1 只说"Ferrari-Canny $Q_1$ 不可微"，其**精确来历**在 [[ContactMechanics#3.4 抓取品质度量：抓得"有多好"|ContactMechanics §3.4]]：把 wrench 凸包写成 $\mathcal W=\{w:a_\ell^Tw\le b_\ell\}$ 后，$Q_1=\min_\ell b_\ell(G)$（原点到最近 facet 的距离，单位 N 或 N·m）是各 facet 距离的**逐点最小 (pointwise min)**。不可微来自两处：① 当"最近 facet"随关节角 $q$ 变化而**切换**时，$\mathrm{argmin}_\ell$ 跳变，$\min$ 在该处出现**次可微折点 (kink)**、梯度不连续；② 构成 $\mathcal W$ 的凸包顶点集本身随 $q$ 增删，是**组合不连续**。下面构造的可微能量 $L(q)$ 做的，正是把这个 hard-$\min$ 换成温度可调的**软最小 / 势场代理**——沿用本讲 §3.3、§5.4 的"非光滑 → 平滑化" [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|continuation]] 暗线（与 ContactMechanics §3.4 的"用 softmin 替 $Q_1$"是同一处修法的两端）。

构造可微能量 $L(q)$，力闭合时最小：

$$
L(q)=w_{dist}\sum_i\|p_i(q)-p_{obj}\|^2+w_{force}\,E_{FC}(n_i,p_i)+w_{pen}\,E_{pen}(q),
$$

- **接触引导项**：用 [[ComputationalGeometry|SDF]] 把指尖拉向杯壁；
- **力闭合项** $E_{FC}$：惩罚接触法向无法张成整个力空间（近似：最小化法向均值模长、最大化法向夹角方差）；
- **穿透惩罚** $E_{pen}=\sum\mathrm{ReLU}(-\phi(q))$。

```python
import torch
def optimize_grasp_pose(hand_model, object_sdf, initial_q):
    """用自动微分优化关节角，最大化抓取质量（去防御代码，聚焦逻辑）。"""
    q = initial_q.clone().detach().requires_grad_(True)
    opt = torch.optim.Adam([q], lr=0.01)
    for _ in range(100):
        contact_points, normals = hand_model.forward_kinematics(q)  # 可微 FK
        dists = object_sdf(contact_points)                          # SDF 有向距离
        dist_loss   = (dists ** 2).sum()                            # 拉指尖贴壁
        equilibrium = torch.norm(normals.mean(0))                   # 法向和→0（力平衡）
        spread      = -contact_points.var(0).sum()                  # 接触点分散（抗力矩）
        pen_loss    = torch.relu(-dists).sum()                      # 穿透惩罚
        loss = 1.0*dist_loss + 10.0*equilibrium + 0.1*spread + 100.0*pen_loss
        opt.zero_grad(); loss.backward(); opt.step()
    return q.detach()
```

**关键**：利用 SDF 的可微性，把几何约束变成平滑势场——**手还没碰到杯子，梯度就能"拉"手指到最优就位姿态**（正是 §5.4 软接触思想在抓取合成里的体现）。这条把 [[ComputationalGeometry]] 与 [[ContactMechanics#3.2 力闭合 vs 形闭合：抓取稳定性的数学条件|力闭合]] 接到了优化上。

---

## 9. 三大范式同台与知识回扣：一只杯子串起优化六层

> [!abstract] 一只杯子，照出三大范式的灵魂（对比脊柱的高潮）
> 给同一个"伸手-抓杯-倒水"任务，三大优化范式各显神通、也各有死穴：
> - **CITO（直接法）**：把整段轨迹 + 接触力 + 互补约束一次性交给 NLP，**自动发现**"何时碰杯壁、何时借桌沿借力"——能生成最巧妙的动作（甚至学会先把杯蹭到桌边再抓）。但带互补约束的 NLP 易卡死、一次几秒，**只能离线**生成动作库。
> - **iLQR/DDP（打靶法）**：用软接触让梯度穿过"端杯"的接触切换，Riccati 递推二阶收敛、10–50ms 可实时——精准的"手术刀"。但**依赖初值**，倒水中途质心突变可能跳出收敛域。
> - **MPPI（采样法）**：GPU 并行撒数千条"怎么倒"的轨迹、按"洒没洒"加权平均，不需梯度、天然多模态、对模型误差不敏感——鲁棒的"大锤"。但 24-DoF 下**采不中**"指尖正好捏杯沿"的精细事件。
>
> **现代答案是融合**：CITO 离线产出动作库 → iLQR 实时精修 → MPPI 兜底鲁棒。一只杯子，照出"精度（iLQR）×自动性（CITO）×鲁棒（MPPI）"的三角权衡。

| 特性 | **CITO（直接法）** | **iLQR/DDP（打靶法）** | **MPPI（采样法）** |
|:--|:--|:--|:--|
| 接触建模 | LCP 硬约束 | 软/平滑接触 | 任意（黑盒/仿真） |
| 梯度处理 | MPCC 互补约束 | 解析梯度 | 无需梯度（零阶） |
| 求解器 | IPOPT/SNOPT (NLP) | Riccati 递推 | GPU 并行 rollout |
| 复杂度 | 极高（最坏非多项式） | $O(TN^3)$ 二次收敛 | $O(KT)$ 随样本线性 |
| 局部极小 | 严重（常卡死） | 中（依赖初值） | 较好（有探索性） |
| 实时性 | 否（>1s） | 可（10–50ms） | 可（10–50ms，需 GPU） |
| 适用 | 离线动作库、理论研究 | 实时 MPC、接触较平滑 | 高不确定、非光滑 Cost |

| 接触模型 | 物理真实性 | 梯度特性 | 优化难度 |
|:--|:--|:--|:--|
| 刚体 (LCP) | 高 | 0（非接触）或 $\infty$（碰撞） | 极难（需特殊求解器） |
| 罚函数 (Penalty) | 低（似弹簧、有穿透） | 线性/二次增长 | 易（但刚度大会震荡） |
| Log-Barrier | 中（渐进不可穿透） | 平滑非线性 | 中（需调 barrier 参数） |
| Sigmoid/Soft | 中（容许微变形） | Sigmoid 形、提供远距引导 | 较易（适合 DDP） |

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 倒水角色）
> | 层 | 核心问题 | 关键工具 | 倒水的哪一段 |
> |:--|:--|:--|:--|
> | §1 决策内核 | 优化什么 | 欠驱动流形、$J_c^T\lambda$ | 规划接触力而非关节轨迹 |
> | §2 语言 | 何为可解 | 凸性、对偶、KKT | 抓杯力分配 QP（SOCP） |
> | §3 接触之难 | 为何崩 | LCP、鞍点、$3^N$ | 端杯瞬间梯度断裂 |
> | §4 求解器 | 多快收敛 | GD/Newton/内点、Riccati | 一个控制周期内解完 |
> | §5 演进 | 谁定接触模式 | RRT→MIQP→CITO→可微物理 | 自动发现何时碰杯壁 |
> | §6 实现 | 梯度怎么穿接触 | iLQR + 软/隐式/随机 | `model.derivatives` |
> | §7 实时 | 边走边重规划 | SQP/RTI、MPPI | 水流出质心漂移时重规划 |
> | §8 抓取合成 | 抓得稳吗 | 可微力闭合 + SDF | 抓杯就位 |

> [!tip] 四条贯穿全讲的"暗线"（抓住它们，细节自来）
> 1. **一个 Riccati 串三领域**：iLQR backward pass = LQR = [[ReinforcementLearning#2.2 值函数与 Bellman 方程|RL Bellman]]（§4.2、§6.1）。
> 2. **KKT 互补 = 接触 LCP**：优化的乘子互补松弛，就是接触力学的"要么分离要么受力"（§2.3、§3.1）——优化与 [[ContactMechanics]] 共用一套约束语法。
> 3. **修复梯度流是主线**：软接触/隐式微分/随机平滑/同伦，全是为了让优化器重新"感觉"到接触（§3→§5→§6）。
> 4. **温度旋钮到处都是**：MPPI 的 $\lambda$、内点法的 $\mu$、SAC 的 $\alpha$、同伦的 $\lambda$——都是"从软/探索连续过渡到硬/利用"的同一把旋钮。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[ContactMechanics]]**：KKT 互补松弛 = LCP（§2.3、§3.1）；可微接触的隐式微分（§6.2）；力闭合能量（§8.2）。
> - **↔ [[Dynamics]]**：操纵器方程是等式约束（§1.2）；欠驱动 = $B$ 的零行（§1.2）；变分积分器（§5.4）。
> - **↔ [[ControlTheory]]**：MPC 是优化进闭环（§7）；iLQR↔LQR↔Riccati（§4.2、§6.1）；变阻抗凸辨识（§5.4）；Safe RL 拉格朗日对偶（§2.3）。
> - **↔ [[ReinforcementLearning]]**：RL=随机优化做序贯决策；Bellman↔Riccati（§4.2）；鞍点逃逸↔熵正则（§3.2）；MPPI↔test-time RL（§7.3）。
> - **↔ [[ComputationalGeometry]]**：SDF 把避碰/接触变成可微势场（§3.1、§8.2）。
> - **↔ [[StochasticProcess]]**：MPPI、随机平滑、自由能最小化（§6.2、§7.3）。
> - **↔ [[RepresentationLearning]]**：NTK 区间下的凸化（§3.2）；可微优化层作为网络模块。

---

## 10. 结论与展望

灵巧操作的优化理论，正从"几何规划"转向"物理兼容的动态规划"——不再满足于规划一个静态抓取姿态，而是在时域上连续地塑造接触力的演化。三条主线：

1. **物理建模的范式转移**：从追求绝对精确的 LCP 硬接触，转向追求优化友好的可微软接触。**在优化循环里，错误但指向正确方向的梯度，胜过没有梯度**——平滑化不只是数学技巧，更是物理先验的注入（§5.4）。
2. **算法融合**：主流架构将是 **iLQR/DDP（高精度"手术刀"）+ MPPI（多模态/鲁棒"大锤"）+ CITO（离线动作库）** 的组合（§9）。
3. **算力解放实时性**：GPU 物理仿真（Isaac Gym、Brax、Dojo）让"并行求解上万个优化问题"成为可能，从 single-shooting 走向 massive-parallel-shooting。

> [!important] 首席科学家视角的最终建议
> 不要被 complementarity constraints、variational integrators 这些名词吓住——抓住一个物理图像即可：**"梯度如何穿过接触点"**。所有算法变体（软接触、随机平滑、隐式微分、同伦）本质都在**修复断裂的梯度流**，让优化器能"感觉"到接触的存在与远近。理解了这一点，你就拿到了灵巧操作优化的钥匙；再叠上"KKT 互补=接触 LCP"与"Riccati=Bellman=LQR"这两座桥，优化、接触、控制、RL 在你眼里就连成了一张图。

---

## 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的优化理论核心主题。

### 轨迹优化与 MPC
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 同伦优化 + 数据飞轮（§5.4）
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 轨迹优化数据生成
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] — 规划引导扩散

### 阻抗参数优化
- [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking]] — 凸阻抗辨识（§5.4）
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 阻抗空间优化

### 奖励与课程优化
- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — LLM 奖励设计
- [[Curriculum Learning]] — 课程学习理论（continuation method 与凸→非凸渐进，§5.4）
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] — 熵引导示范加速

### 零阶与进化优化（§4.4）
- [[The CMA Evolution Strategy: A Tutorial|CMA-ES 教程]] — 协方差自适应进化策略的权威推导（四步机制 + CSA 步长控制）
- [[cmaes- A Simple yet Practical Python Library for CMA-ES|cmaes 库]] — CMA-ES 的实用实现（[[Final_WMTS|WMTS]] 隐空间任务生成器所用）
- [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions|POET]] — 进化算法驱动的开放式课程（环境-智能体协同进化）

### 约束优化与对偶方法
- [[Reachability Constrained Reinforcement Learning]] — PPO/SAC-Lagrangian（拉格朗日对偶分解安全约束，§2.2）
- [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]] — 单调性约束的凸优化
- [[Safe Model-based Reinforcement Learning with Stability Guarantees]] — CLF-CBF 对偶框架

### 稀疏与可解释优化
- [[Weight-sparse transformers have interpretable circuits]] — $L_0$ 稀疏优化

