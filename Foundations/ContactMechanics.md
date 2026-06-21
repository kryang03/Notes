---
tags:
  - foundation
  - contact-mechanics
  - dexterous-manipulation
  - friction
  - LCP
aliases:
  - 接触力学
  - Contact
  - 摩擦锥
  - Friction Cone
created: 2026-01-31
related:
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[ComputationalGeometry]]"
  - "[[StochasticProcess]]"
---

# 机器人灵巧操作中的接触力学：从曲面微分几何到可微物理

# Contact Mechanics for Dexterous Manipulation: From Surface Differential Geometry to Differentiable Physics

> [!tip] 相关领域
> - [[Dynamics]] — 接触动力学与多体动力学的耦合；LCP 是接触仿真时间步进的核心
> - [[ControlTheory]] — 力/位混合控制、接触状态机依赖接触模型；抓取矩阵的对偶性是控制基础
> - [[Optimization]] — LCP/QP 求解器、摩擦锥的多面体线性化、可微力闭合能量
> - [[ComputationalGeometry]] — SDF/最近点/穿透深度查询是接触检测的前置
> - [[StochasticProcess]] — 摩擦不确定性、随机互补问题 (SCP)
>
> **贯穿母题**：**指尖间滚转一颗玻璃弹珠 (rolling a marble between two fingertips)**。一颗光滑小球在两根软指间被夹住、滚动、旋拧——这一个动作，把接触力学的五层理论全部点亮。

## 0. 母题与理论大厦构建路线：从接触点到可计算力学

> [!abstract] 为什么用"指尖滚转弹珠"做母题？
> 弹珠是接触力学最干净的"探针"：
> - 它是**完美球面**（$K=\mathrm{diag}(1/R,1/R)$），让曲率张量与 Montana 方程的几何一目了然；
> - 滚动它需要**纯滚动 vs 滑动**的判别——这是**摩擦锥**与**非完整约束**；
> - 夹住它不掉，需要**力闭合**；软指压上去形成**接触斑**，带来**扭转摩擦**；
> - 在仿真里让它不穿透手指、受力后弹开，需要 **LCP/互补条件**；
> - 想用梯度优化"怎么滚得更稳"，需要**可微接触**。
>
> 全讲每引入一个概念，都回到这颗弹珠：**"它此刻在滚还是在滑？两指能不能夹稳它？仿真里它为什么会抖？"**

接触力学的理论大厦有五层，每层回答一个更具体的问题，且每层都把下一层"喂"给一个相邻领域：

| 层级 | 要回答的问题 | 关键对象 | 下游依赖 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **接触几何** | 接触点在哪、法向与曲率如何变？ | 高斯标架、度量/曲率张量 | [[ComputationalGeometry]] 的 SDF/最近点 | §2 |
| **接触运动学** | 接触点如何在两曲面上滚/滑？ | Montana 方程、接触雅可比、非完整约束 | [[ControlTheory]] 的力/位混合与接触状态机 | §2 |
| **接触静力学** | 接触力能否抵抗任意扰动？ | 抓取矩阵、摩擦锥、力闭合、内力 | 抓取合成、grasp quality | §3 |
| **接触动力学** | 力如何与速度跳变、不可穿透耦合？ | LCP、冲量、互补条件 | [[Dynamics]] 的接触时间步进与仿真器 | §4–§5 |
| **可微/学习层** | 如何让接触进入梯度优化与策略学习？ | 平滑化、隐函数定理、随机化 | [[Optimization]] 的 CITO、[[ReinforcementLearning]] 的 contact-rich policy | §6 |

> [!important] 细颗粒度检查标准
> 任何接触概念都要同时说清：**几何约束是什么、允许哪些速度、能传哪些力、求解器如何数值实现、对灵巧手策略有什么风险**。只写"摩擦锥/力闭合定义"远远不够。

> [!note] 本讲在知识图谱中的位置
> ```
> [[ComputationalGeometry]] ──SDF/最近点──> 【接触几何】
>                                              │
>                          【接触运动学】──对偶 Jₕ/G──> [[ControlTheory]]
>                                              │
>            【接触静力学：力闭合】──> 抓取合成 / [[Optimization|可微抓取]]
>                                              │
> 【接触动力学：LCP】──时间步进──> [[Dynamics]] ──不确定性──> [[StochasticProcess]]
>                                              │
>            【可微接触】──解析梯度──> [[Optimization|CITO]] / [[ReinforcementLearning|可微物理 RL]]
> ```

---

## 1. 接触：灵巧操作的灵魂

> [!tip] 本节四拍
> **直觉**（灵巧操作的本质是"通过接触界面管理力与运动的传递"）→ **推导**（接触为何引入非光滑性）→ **对比**（工业抓取 vs 灵巧操作：刚性闭合 vs 主动利用滚/滑/扭）→ **落点**（这定义了后续五层理论的任务）。

与传统工业抓取（只关心抓牢、刚性闭合）不同，灵巧操作的灵魂在于**主动利用接触**：让弹珠在指间**滚动 (rolling)**、**滑动 (sliding)**、甚至受控**扭转 (torsional)**，以调整其姿态。这要求我们不仅能精确描述接触点在曲面流形上的演化（运动学），还要能构造数值稳定的求解器去处理接触带来的两类**非光滑性**：

1. **几何非光滑**：接触的"通/断"是阶跃的（make/break contact），导致力与梯度的不连续——这是 §6 可微接触与 [[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 高方差]] 的共同根源；
2. **本构非光滑**：摩擦的"粘/滑"切换（stick→slip）是非光滑的——这是 §3 摩擦锥与 [[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|滑移检测]] 的核心。

> [!important] 一句话定位
> **接触力学 = 把"力与运动如何穿过接触界面"写成可计算的几何、静力学与动力学。** 它向上托起 [[ControlTheory|柔顺控制]]、[[Dynamics|接触仿真]]、[[Optimization|接触隐式优化]]，向下扎根于 [[ComputationalGeometry|几何查询]]。

---

## 2. 接触几何与运动学：接触点如何在曲面上演化

> [!tip] 本节四拍
> **直觉**（弹珠在指上滚，接触点在两个曲面上各自"爬行"）→ **推导**（高斯标架→曲率张量→Montana 方程）→ **对比**（纯滚动 vs 纯滑动：非完整 vs 完整）→ **联系**（接触雅可比连接关节空间，对偶到 [[ControlTheory]]）。

### 2.1 曲面微分几何基础：高斯标架、度量与曲率

把手指与弹珠都看作三维欧氏空间中的光滑曲面 $f_i:\mathbb R^2\to\mathbb R^3$（$i\in\{1,2\}$）。在接触点建局部正交**高斯标架** $\{x,y,z\}$：$z$ 沿外法线，$x,y$ 在切平面内。

**第一基本形式（度量张量 $M_i$）** 把参数速度 $\dot u_i=(\dot u,\dot v)$ 映到切平面线速度：$v_{tan}=M_i\dot u_i$。正交参数化下
$$M_i=\begin{bmatrix}\|\partial f_i/\partial u\| & 0\\ 0 & \|\partial f_i/\partial v\|\end{bmatrix}.$$

**第二基本形式（曲率张量 $K_i$）** 描述法向 $z$ 随切向位移的变化率：$\dot n_i=-M_iK_i\dot u_i$。其特征值是主曲率。**弹珠（半径 $R$）**：$K=\mathrm{diag}(1/R,1/R)$；**平面**：$K=0$。**挠率张量 $T_i$** 描述标架绕法线的自转（处理非测地运动时关键）。

### 2.2 Montana 接触运动学方程

> [!note] 历史地位
> David Montana (1988) 的接触运动学方程是灵巧操作的里程碑：它把物体间的**相对刚体运动**与**接触点在各自曲面上的演化速度**用微分关系联系起来。

设接触保持闭合（法向距离 0、$v_z=0$），接触点在两曲面的演化率为 $\dot u_1,\dot u_2$，两标架 $x$ 轴夹角为 $\psi$。相对线速度 $(v_x,v_y,v_z)$、角速度 $(\omega_x,\omega_y,\omega_z)$。Montana 方程组：

$$
\dot u_1=M_1^{-1}(K_1+\tilde K_2)^{-1}\Big(\begin{bmatrix}-\omega_y\\\omega_x\end{bmatrix}-\tilde K_2\begin{bmatrix}v_x\\v_y\end{bmatrix}\Big),\quad
\dot u_2=M_2^{-1}R_\psi^T(K_1+\tilde K_2)^{-1}\Big(\begin{bmatrix}-\omega_y\\\omega_x\end{bmatrix}+K_1\begin{bmatrix}v_x\\v_y\end{bmatrix}\Big),
$$
$$
\dot\psi=\omega_z+T_1M_1\dot u_1+T_2M_2\dot u_2,\qquad \tilde K_2:=R_\psi K_2R_\psi^T,
$$
其中 $R_\psi$ 是角度 $\psi$ 的二维旋转矩阵。

> [!important] 物理洞察（弹珠版）
> - **相对曲率项 $(K_1+\tilde K_2)^{-1}$ 是方程的心脏**。若两面**共形**（如半径 $R$ 的弹珠落进半径 $R$ 的球窝），相对曲率趋于奇异、其逆趋于无穷——接触点速度不定，物理上对应**面接触而非点接触**。故 Montana 方程仅适用于**非共形点接触**。
> - **曲率估计 = 主动感知**：未知物体时，机器人可由自身关节运动推算 $\omega,v$，再用触觉测 $\dot u_1$，**反解 $K_2$**——靠"抚摸"重建局部几何。这正是 [[InformationTheory#3.1 隐式曲面高斯过程 (GPIS)|主动触觉建图]] 的力学根。
> - **纯滚动 vs 纯滑动**：
>   - **纯滚动** ($v_x=v_y=0$)：接触点移动全由相对角速度驱动。滚动是**非完整约束 (non-holonomic)** 的典型——路径依赖，不能只靠改位置变量回到原点。这给"在指间把弹珠滚到指定姿态"引入了与 [[ControlTheory#6. 接触非线性：Montana 接触运动学|非完整控制]] 同源的规划难度。
>   - **纯滑动** ($\omega_x=\omega_y=0$)：移动仅由切向速度驱动，轨迹取决于切向力方向与表面几何。

### 2.3 接触雅可比与对偶性：连接关节空间

要把接触层的运动学接到机器人关节，需要两个映射，它们经**虚功原理**形成对偶：

$$
\underbrace{V_{contact}=J_h\dot q}_{\text{手雅可比：关节→接触}},\qquad
\underbrace{W_{object}=Gf_c}_{\text{抓取矩阵：接触力→物体 wrench}},\qquad
\underbrace{\tau_q=J_h^Tf_c}_{\text{对偶：接触力→关节力矩}}.
$$

> [!tip] 对偶关系的物理含义（一句话记住三个矩阵）
> $J_h$ 答"关节动→接触点怎么动"；$J_h^T$ 答"接触力→关节上多大负载"；$G$ 答"接触力→物体受什么 wrench"。**灵巧操作的本质，就是同时选 $\dot q$ 与 $f_c$，让运动约束（$J_h$）与力约束（$G$、摩擦锥）都可行。** 这条对偶线在 [[ControlTheory#2.1 虚功原理与对偶性|控制理论]] 与 [[Dynamics#7.1 拓扑突变与有效惯量|动力学]] 中反复出现——记住它，三个领域通。

注意：$G$ 的结构取决于**接触模型**（§4）。软指接触下 $G$ 不仅含力传递块、还含力矩传递块，使某些点接触下不可控的操作（如原地扭转弹珠）成为可能。

---

## 3. 接触静力学：能否夹稳这颗弹珠

> [!tip] 本节四拍
> **直觉**（两指要夹住弹珠抵抗任意方向的扰动）→ **推导**（抓取矩阵→wrench space→力闭合的数学条件）→ **对比**（形闭合 vs 力闭合；不同接触模型的最小接触点数）→ **联系**（力闭合↔[[Optimization|可微抓取能量]]、grasp quality↔抓取合成）。

### 3.1 抓取矩阵的严格定义与内力

> [!note] 教科书参考
> 本节严格遵循 Murray, Li & Sastry《A Mathematical Introduction to Robotic Manipulation》Ch. 5–6。

设 $k$ 个接触点，第 $i$ 点相对物体质心位置 $r_i$。单点接触力 $f_i\in\mathbb R^3$ 在质心产生 wrench
$$w_i=\begin{bmatrix}f_i\\ r_i\times f_i\end{bmatrix}=\begin{bmatrix}I_{3\times3}\\ \hat r_i\end{bmatrix}f_i,$$
$\hat r_i$ 为叉乘反对称矩阵。堆叠得**抓取矩阵** $G\in\mathbb R^{6\times3k}$（点接触）：
$$G=\begin{bmatrix}I & \cdots & I\\ \hat r_1 & \cdots & \hat r_k\end{bmatrix},\qquad w_{total}=Gf,\quad f=[f_1^T,\dots,f_k^T]^T.$$

> [!important] 两个子空间，两层物理
> - **列空间 $\mathrm{Range}(G)$**：当前接触配置能施加的所有 wrench 集合。$\mathrm{rank}(G)=6$ 才可能完全约束物体。
> - **零空间 $\mathrm{Null}(G)$ = 内力 (Internal Forces)**：$Gf_{int}=0$，施加这些力**不改变物体运动**，却决定**抓取稳定性**（如挤压弹珠的预紧力）。两指夹弹珠时，"夹多紧"正是在 $\mathrm{Null}(G)$ 里选点——这与 [[Dynamics#7.2 约束漂移与内力|动力学的内力]] 是同一对象。

### 3.2 力闭合 vs 形闭合：抓取稳定性的数学条件

> [!important] 核心概念
> **力闭合 (Force Closure)**：能用**摩擦约束内**的接触力，抵抗施加在物体上的**任意方向** wrench。这是灵巧抓取的核心数学条件。

- **形闭合 (Form Closure)**：纯靠几何"锁死"，无摩擦也不动。条件 $\mathrm{rank}(G)=6$ 且 $\mathrm{Null}(G_{vel})=\{0\}$（如把方块卡进 V 槽）。**很少用**——依赖精确几何配合、缺乏灵活性。
- **力闭合**：几何条件是 wrench 空间原点位于**可达 wrench 锥**内部：$0\in\mathrm{int}(\mathrm{ConvexHull}(\mathcal W))$，$\mathcal W=\{Gf:f\in\mathcal{FC}\}$，$\mathcal{FC}$ 是所有接触点摩擦锥约束。**等价条件（Murray 定理 5.4）**：不存在 $\lambda\ne0$ 使 $\lambda^TW_i\ge0\ \forall i$（**无公共半空间**）。

> [!tip] 物理直觉
> **力闭合 = "手指把物体团团围住"**：无论外扰从哪来，总有手指能推回去。若所有接触力只能指向某个半空间，反方向扰动就无法抵抗。

### 3.3 最小接触点数：Caratheodory、Steinitz 与"例外曲面"

> [!theorem] 凸分析两定理 → 抓取下界与上界
> - **Caratheodory**：若 $\{v_1,\dots,v_k\}$ 正生成 $\mathbb R^p$，则 $k\ge p+1$ → 力闭合**至少**需 $p+1$ 个接触点。
> - **Steinitz**：若 $q\in\mathrm{int}(\mathrm{co}(S))$，存在 $\le2p$ 个点的子集使 $q$ 仍在其凸包内部 → 非例外曲面**至多** $2p$ 个点即可力闭合。

| 接触模型 | 2D 最小点数 | 3D 最小点数 |
|:--|:--:|:--:|
| 无摩擦点接触 | 4 | 7 |
| 有摩擦点接触 | 2 | 3 |
| 软指接触 | 2 | 2 |

> [!warning] 弹珠正是"例外曲面"！
> 若物体可达 wrench 集的凸包不含原点邻域，则它**永远无法**用无摩擦点接触实现力闭合。典型例子就是**球体**——所有法向量都通过球心，无法产生抵抗绕心扭转的 wrench。**这解释了为什么徒手（无摩擦想象）夹不稳一颗玻璃弹珠，而靠摩擦/软指就能**：摩擦把"点"变成了能传切向力的锥，软指把"点"变成了能传扭矩的斑。**洞察**：软指模型用更少接触点实现力闭合（3D 仅需 2 点），对高 DoF 灵巧手是协调控制的极大简化。

### 3.4 抓取品质度量：抓得"有多好"

| 度量 | 定义 | 物理意义 |
|:--|:--|:--|
| **Ferrari–Canny $Q_1$** | wrench 集内接最大球半径 $\max\{r:B(0,r)\subseteq\mathcal W\}$ | 能抵抗的最大**均匀**扰动；$Q_1>0\Leftrightarrow$ 力闭合 |
| **Wrench Space Volume $Q_2$** | $\mathrm{Volume}(\mathcal W)$ | 考虑各向异性（某些方向能发更大力） |
| **$\sigma_{\min}(G)$** | $G$ 最小奇异值 | 抓取配置的病态程度；越大力传递越高效 |

> [!note] 工程选择与可微化
> 实际抓取规划常用 **Ferrari–Canny $Q_1$**（直接对应鲁棒性、计算高效，转化为 LP/SOCP）。但 $Q_1$ **不可微**（取 min/凸包），无法直接进梯度优化——这正是 §6 与 [[Optimization#8. 深度专题：可微抓取合成 (Differentiable Grasp Synthesis)|可微力闭合能量]] 要解决的问题：用可微的力闭合代理能量替代 $Q_1$，让抓取合成能端到端学习。

---

## 4. 接触模型的层级：从点接触到软体

> [!tip] 本节四拍
> **直觉**（弹珠压上软指尖，"点"其实是一小块"斑"）→ **推导**（从无摩擦点到软指椭球极限曲面）→ **对比**（四种模型的力矩传递能力与复杂度）→ **联系**（模型决定 $G$ 的结构，进而决定 §3 的可控操作）。

### 4.1 硬指模型（点接触）

- **无摩擦点接触**：只能沿法向推 $f_n\ge0$，切向力为零。仅用于理论的形闭合分析。
- **有摩擦点接触（硬指）**：法向 + 切向摩擦力，遵循库伦律 $\|f_t\|\le\mu f_n$。几何上是一个**摩擦锥 (Friction Cone)**。硬指**不能传力矩**——手指像球铰链，物体可绕接触点自由转，除非被多指约束。

### 4.2 软指模型：接触斑与扭转摩擦

真实指尖覆橡胶/硅胶，受压时"点"扩为**接触斑 (contact patch)**。于是手指除切向力外还能施加**绕法线的扭转力矩** $\tau_n$。经典模型用**椭球极限曲面**耦合切向与扭转摩擦：

$$\frac{f_t^2}{\mu^2}+\frac{\tau_n^2}{\gamma^2}\le f_n^2,$$

$\gamma$ 为扭转摩擦系数。**这正是"两指原地扭拧弹珠"的力学依据**——硬指做不到，软指靠扭转摩擦做得到（呼应 §3.3：软指让球体这种例外曲面也能稳定操作）。

### 4.3 超越 Hertz：大变形与软体抓取

Hertz 理论假设小应变线性弹性，预测接触半径 $a\propto F^{1/3}$。但软指大变形（压缩 50%）时，超弹性与几何非线性使刚度急剧硬化 (hardening)，偏离 Hertz——需用**降维法 (MDR)** 推导的缩放定律。获取真实应力分布的金标准是**有限元 (FEM)**，但非实时；机器人控制常用**多点代理模型**（把软指建为一组弹簧连接的刚性微球），既快又能模拟抗扭特性。

| 模型 | 自由度约束 | 力矩传递 | 适用场景 | 复杂度 |
|:--|:--|:--|:--|:--|
| 无摩擦点接触 | 1（法向） | 无 | 形闭合分析 | 极低 |
| 硬指接触 | 3（法向+切向） | 无 | 金属/硬塑、精密装配 | 低 |
| **软指接触** | 4（+扭转） | 有（法向轴） | 橡胶指尖、手内操作 | 中 |
| 有限元/多点 | 6+（分布力） | 有（任意轴） | 软体机器人、大变形 | 高 |

---

## 5. 接触动力学与求解器：如何算出下一时刻

> [!tip] 本节四拍
> **直觉**（仿真里弹珠不能穿进手指、受压要弹开——这是个约束求解问题）→ **推导**（互补条件→LCP→Delassus 矩阵）→ **对比**（直接 Lemke vs 迭代 PGS/SI vs 凸优化 MuJoCo vs 位置层 XPBD）→ **联系**（LCP↔[[Optimization]]、时间步进↔[[Dynamics]]、随机化↔[[StochasticProcess]]）。

### 5.1 互补条件与 LCP 的构建

刚体非穿透本质是**互补条件**：间距 $d\ge0$、法向力 $f_n\ge0$、且 $d\cdot f_n=0$（分离则无力，受力则贴合）。结合离散动力学，化为标准**线性互补问题 (LCP)**：

$$w=Az+q,\qquad 0\le w\perp z\ge0.$$

> [!note] Stewart–Trinkle：从加速度层到速度-冲量层
> 早期在**加速度层**求解易遇 Painlevé 悖论（解不存在/不唯一）。Stewart–Trinkle (1996) 改在**速度-冲量层**做时间步进，彻底解决存在性：
> $$M(v^{t+1}-v^t)=h(f_{ext}+J_n^T\lambda_n+J_t^T\lambda_t),$$
> 重写为 LCP。矩阵 $A$（**Delassus 矩阵**）反映系统在接触点的有效逆质量——它与 [[Dynamics#5.1 空间向量代数：6D 统一平动与转动|空间向量代数]] 紧密配合。

**摩擦锥的多面体线性化**：库伦锥 $\sqrt{f_x^2+f_y^2}\le\mu f_n$ 是二阶锥（非线性）。要纳入**线性** LCP，须用四/八棱锥近似。代价是引入**各向异性**——弹珠沿棱方向与沿面方向的滑动阻力不同，这也是某些引擎里物体旋转"卡顿"的来源。

### 5.2 两类求解器：直接 vs 迭代

| 求解器 | 代表 | 原理 | 优点 | 缺点 | 典型引擎 |
|:--|:--|:--|:--|:--|:--|
| **直接（枢轴）** | Lemke | 类单纯形枢轴 | 有解必得**精确解**；高精度抓取稳定性分析首选 | 最坏指数复杂度；大量接触时难并行 | — |
| **迭代** | PGS / Sequential Impulses | 对偶问题上投影高斯-赛德尔 | $O(N)$，易实现，天然处理过约束 | 解近似、接触显**非物理软度**（刚度随迭代数/步长变） | Bullet, PhysX, PyBullet, Dart |

> [!tip] 顺序冲量 (SI) 的关键技巧：热启动
> Erin Catto 的 SI 在数学上等价于对对偶问题做 PGS。其**热启动 (warm starting)** 用上一帧冲量 $\lambda^{t-1}$ 作初值，利用时间相干性把堆叠物体的收敛迭代从几百次降到几十次——这与 [[Optimization|MPC 的 warm start]] 是同一思想：相邻时刻的解很接近，别从零开始。

### 5.3 凸优化范式（MuJoCo）与位置层（XPBD）

- **MuJoCo（凸优化）**：Todorov 指出，若允许约束微小变形（软约束），接触动力学可建为**凸 QP**。好处：① 全局最优唯一；② 可用牛顿法（二阶收敛，远快于 PGS 的一阶）；③ **逆动力学良定义**——即使有接触也能解析算控制力矩，这对 [[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|基于模型的控制]]是巨大优势。
- **XPBD（位置层）**：跳过速度层，直接在位置层投影约束。对软体/布料/绳索/柔性抓手**稳定性无与伦比**（不会因速度层误差积累而"爆炸"）。引入顺应参数 $\alpha=1/(kh^2)$，使材料刚度与迭代数、步长**解耦**，获得物理真实性。

> [!important] 求解器选型的二元性（贯穿 [[Dynamics]] 与 [[EmbodiedAI|仿真器生态]]）
> **追求真理 → Lemke/牛顿**（高精度仿真、稳定性分析）；**追求速度与稳定 → PGS/SI/XPBD**（实时游戏、RL 训练环境）。这条"精度 vs 速度"的二元对立，会在 [[Dynamics#6. 仿真层：接触动力学的深水区|动力学的接触求解]]与 [[EmbodiedAI#4. 仿真器生态|仿真器选型]]中再次出现——记住这条线，你就能预判任何新仿真器的取舍。

---

## 6. 可微接触物理：让接触进入梯度优化

> [!tip] 本节四拍
> **直觉**（若仿真可微，就能用梯度直接优化"怎么滚稳弹珠"，效率远超无梯度法）→ **推导**（接触不连续为何让梯度失效；隐函数定理如何救场）→ **对比**（平滑 vs 展开 vs 解析梯度）→ **联系**（[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|CITO]]、[[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|可微物理 RL]]）。

### 6.1 不连续性的挑战

接触本质不连续：微小动作改变可让接触**通/断 (make/break)**。这种阶跃使梯度要么为零（无接触时）、要么未定义（撞击瞬间）。这正是 [[ReinforcementLearning#1.3 非光滑性的两副面孔：接触流形与混合动力学|RL 在接触任务上高方差]]的同一物理根源——一个用梯度、一个用采样，面对的是同一道墙。

### 6.2 实现可微的三条路径

| 方法 | 原理 | 优点 | 缺点 | 典型引擎 |
|:--|:--|:--|:--|:--|
| **软化/平滑** | 弹簧阻尼替代硬约束 | 易实现，梯度连续 | 物理失真（穿透、振荡） | Brax(早期)、System ID |
| **展开 (Unrolling)** | 通过求解器迭代步反向传播 | 适用任意可微操作 | 内存大、梯度爆炸/消失 | DiffTaichi(部分) |
| **解析梯度 (IFT)** | 隐函数定理/KKT 条件 | 极快、精度高、内存小 | 需推导特定模型导数 | Nimble、MuJoCo(新)、Dojo |

> [!important] 隐函数定理：最前沿的解析梯度（一行公式的威力）
> 与其对 PGS 数百次迭代反向传播（计算图过深、梯度不稳），不如直接对**求解结果**微分。设求解器找到 $z^*$ 满足平衡 $R(z^*,\theta)=0$（$\theta$ 为物理参数），由隐函数定理：
> $$\frac{\partial z^*}{\partial\theta}=-\Big(\frac{\partial R}{\partial z}\Big)^{-1}\frac{\partial R}{\partial\theta}.$$
> 只需在求解后解一个线性方程组，就一次性得到解对所有参数的梯度——**梯度精度与前向迭代次数无关**，极其稳定。这与 [[Optimization#2. 优化的语言：可行域、目标、对偶与 KKT|可微优化层 (OptNet)]] 是同一数学：对 KKT 条件用隐函数定理。**零阶平滑（上表第一行）则与 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|域随机化]]同构**——都是用"在期望上抹平"来制造有意义的梯度方向。
>
> 补充：**碰撞时间 (TOI) 梯度**用连续碰撞检测算出精确碰撞时刻 $t_c$，填补固定步长仿真在时间维度上丢失的梯度信息——对优化高速运动（如快速接住弹珠）至关重要。

---

## 7. Sim-to-Real 与工程实现

> [!tip] 本节四拍
> **直觉**（仿真里滚得稳的弹珠，真机一上手就掉——接触的 reality gap 是落地最大障碍）→ **推导**（要随机化的不止摩擦）→ **对比**（离线辨识 vs 在线辨识）→ **联系**（与 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL 的 sim-to-real]] 是同一战场的两侧）。

**接触域随机化（不能只随机摩擦）**：① 摩擦系数 $\mu$（含滚动/扭转摩擦）；② 接触刚度/阻尼（MuJoCo 的 `solref`/`solimp`）；③ 延迟（接触发生→力读数、指令→力矩生效）；④ 接触几何（碰撞网格顶点扰动、凸分解精度）。**渐进式随机化**（从确定环境起、逐步加幅度）比一上来全域大随机收敛更好——这与 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|Adaptive DR]]、[[Optimization|continuation method]] 同源。

**在线系统辨识**：借可微物理，机器人在交互中（如指尖轻滑弹珠表面）实时算 $\nabla_\mu\text{Loss}$ 在线更新摩擦系数——像人一样"试探"未知接触特性，实现自适应。其稳定性分析见 [[ControlTheory#12. 自适应控制与确定性等价|自适应控制]]。

---

## 8. 知识回扣与记忆图：一颗弹珠串起接触力学

> [!abstract] 用一颗弹珠把全讲复述一遍（刻意复述，为记忆）
> 我们要在两根软指间滚转一颗玻璃弹珠。**(§2)** 弹珠是完美球面（$K=\mathrm{diag}(1/R,1/R)$），Montana 方程告诉我们接触点如何在指面与球面上各自爬行；它在滚（非完整）还是在滑（完整），由切向速度与角速度的配比决定；接触雅可比 $J_h$ 与抓取矩阵 $G$ 经虚功对偶，把关节、接触、物体三层串起。**(§3)** 想夹稳它，需要力闭合——可弹珠是"例外曲面"，无摩擦点接触永远夹不稳，必须靠摩擦锥（把点变锥）或软指（把点变斑、能传扭矩）；夹多紧则在 $\mathrm{Null}(G)$ 的内力里选。**(§4)** 软指接触斑带来椭球极限曲面，这才让"原地扭拧弹珠"成为可能。**(§5)** 仿真里要让它不穿透、受压弹开，把非穿透写成互补条件→LCP；Lemke 求真、PGS/SI 求快、MuJoCo 凸化求稳、XPBD 在位置层求软体稳定。**(§6)** 想用梯度优化"怎么滚更稳"，靠隐函数定理对求解结果直接微分。**(§7)** 搬上真机，随机化摩擦/刚度/延迟/几何，并在线辨识。**一颗弹珠，滚遍了接触力学的五层大厦。**

> [!important] 一张表记住全篇
> | 层 | 核心问题 | 关键工具 | 弹珠的哪一环 |
> |:--|:--|:--|:--|
> | §2 几何/运动学 | 接触点如何演化 | 高斯标架、Montana、非完整约束 | 滚还是滑 |
> | §3 静力学 | 能否夹稳 | 抓取矩阵、力闭合、例外曲面 | 球为何难夹 |
> | §4 接触模型 | 能传哪些力 | 摩擦锥、软指椭球极限面 | 能否扭拧 |
> | §5 动力学/求解器 | 下一时刻状态 | LCP、Lemke/PGS/MuJoCo/XPBD | 仿真为何抖 |
> | §6 可微接触 | 如何进梯度优化 | 隐函数定理、TOI | 怎么滚更稳 |

> [!tip] 四条贯穿全讲的"暗线"
> 1. **对偶性 $J_h\leftrightarrow G$**：运动映射与力映射经虚功对偶，贯穿 §2，并延伸到 [[ControlTheory]] 与 [[Dynamics]]。
> 2. **LCP 主线**：互补条件（§5）是连接 [[Dynamics|接触仿真]]、[[Optimization|LCP/QP 求解]]、[[StochasticProcess|随机互补]]、[[ReinforcementLearning|混合动力学]]的枢纽——一个数学结构，五个领域共用。
> 3. **摩擦锥与粘/滑**：库伦锥（§4）既定义力闭合（§3）、又驱动 [[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|滑移检测]]、还是 [[ControlTheory#7.3 滑移检测与闭环防滑|防滑控制]]的对象。
> 4. **非光滑性 → 可微化/采样**：接触的通/断不连续（§6），用解析平滑应对是可微物理、用采样应对是 [[ReinforcementLearning|RL]]——同一道墙，两种翻法。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[Dynamics]]**：LCP 时间步进（§5）；Delassus 矩阵↔空间向量代数；抓取矩阵↔有效惯量与内力。
> - **↔ [[Optimization]]**：LCP/QP 求解、摩擦锥多面体线性化、可微力闭合能量替代不可微 $Q_1$（§3.4/§6）。
> - **↔ [[ComputationalGeometry]]**：SDF/最近点/穿透深度是接触检测前置（§0/§2）。
> - **↔ [[ControlTheory]]**：虚功对偶（§2.3）、软指 $G$ 使力位混合可行、非完整滚动控制、防滑控制。
> - **↔ [[StochasticProcess]]**：摩擦不确定性、随机互补问题 (SCP)。
> - **↔ [[ReinforcementLearning]]**：接触非光滑=策略梯度高方差之源；可微接触=可微物理 RL。
> - **↔ [[SignalProcessing]]**：粘/滑切换的触觉检测。

---

## 9. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及接触力学的核心主题。

### 手内操作与接触建模
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] — 重力无关旋转
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] — 纯触觉旋转
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] — 视触觉联觉
- [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] — 手指步态

### 接触丰富的学习
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 物理驱动数据生成
- [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation]] — 残差 DMP
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — 接触丰富任务的阻抗控制
- [[Deep Dynamics Models for Learning Dexterous Manipulation]] — contact-rich MPC 在多指手任务中的经验验证

### 触觉感知与抓取
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] — 视触觉遥操作
- [[Proximity Perception-Based Grasping Intelligence (P2GI)]] — 近距离感知抓取
- [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] — 触觉反馈与课程学习
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] — 穿透深度作为域不变触觉表征，zero-shot sim-to-real
- [[GenDexGrasp - Generalizable Dexterous Grasping]] — 以 contact map 作跨手型抓取表征，用 force closure 合成 MultiDex

### 接触丰富的非抓取操作
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 杂乱场景中选择性利用环境接触的 extrinsic dexterity

### 视触觉策略生成
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]] — 接触 grounding 扩散策略，耦合状态-触觉扩散 + 接触一致性映射
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] — 穿透深度图作为统一触觉 sim-to-real 表征

### 柔顺控制与力学建模
- [[Minimalist Compliance Control|MCC]] — 无传感器柔顺控制，利用电机电流估计接触力，方向相关效率模型

### 项目级真机接触 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-007-Implicit-Explicit-Contact-WM|IECW]] — 解析刚体动力学（隐式接触）+ 触觉门控 patch 残差网络（显式接触）的双通路世界模型
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-013-Stick-Slip-Mode-Switching|SSMS]] — 基于 stick-slip 模态识别的双子策略（slow/burst）+ WM dispatcher
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-001-Tactile-Anchored-Reward|TAR]] — 以触觉拓扑替代 GT pose 的真机奖励信号

---

## 10. 结论

接触力学是灵巧操作的基石。从 Montana 方程的几何演化（§2）、力闭合的凸分析条件（§3）、到 LCP/MuJoCo/XPBD 的计算工具（§5）、再到隐函数定理开启的可微物理（§6），这一领域正在经历从"刚体精确建模"到"软体可微学习"的深刻变革。四条核心建议：

1. **分层记忆**：几何原理（Montana）→ 物理建模（软指）→ 求解算法（LCP）→ 学习应用（可微）——对应本讲 §2→§4→§5→§6。
2. **关注软体趋势**：软抓手普及下，超弹性接触与 XPBD 比刚体 LCP 更贴合现实。
3. **求解器二元性**：高精度仿真（Lemke/牛顿）vs 实时 RL 环境（PGS/SI/XPBD），前者追真理、后者追速度与稳定。
4. **可微物理的前瞻**：隐函数定理是连接传统力学与现代深度学习的桥——它同时点亮 [[Optimization|CITO]] 与 [[ReinforcementLearning|可微物理 RL]]。
