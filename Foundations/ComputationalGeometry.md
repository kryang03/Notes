---
tags:
  - foundation
  - computational-geometry
  - collision-detection
  - SDF
aliases:
  - 计算几何
  - GJK
  - EPA
  - 有向距离场
  - 凸分解
created: 2026-01-31
related:
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
  - "[[Dynamics]]"
  - "[[RepresentationLearning]]"
  - "[[InformationTheory]]"
---

# 灵巧操作中的计算几何：从离散碰撞到连续可微接触场

# Computational Geometry for Dexterous Manipulation: From Discrete Collision to Continuous Differentiable Contact Fields

> [!tip] 相关领域
> - [[ContactMechanics]] — 接触点几何、接触雅可比、抓取矩阵的几何来源
> - [[Optimization]] — SDF 把避碰/接触变成可微势场，喂给 TrajOpt/CHOMP
> - [[Dynamics]] — 刚体运动学与构型空间；碰撞是仿真接触求解的前置
> - [[RepresentationLearning]] — 神经隐式几何 (DeepSDF/NGDF) 是学出来的几何
> - [[InformationTheory]] — GPIS 的隐式曲面、主动触摸的几何先验
>
> **贯穿母题（本讲的"主角"）**：**在杂乱抽屉里无碰撞地够到并取出一把钥匙 (reach into a cluttered drawer to retrieve a key)**。一个"伸手进抽屉摸索取物"的动作，把计算几何每一层都点亮——我们让它贯穿全篇。

## 0. 母题与理论大厦构建路线：从集合运算到可微接触几何

> [!abstract] 为什么用"杂乱抽屉取钥匙"做贯穿母题？
> 计算几何在灵巧操作里不是"碰撞检测工具箱"，而是把**形状、距离、接触法向、优化梯度**统一起来的底层语言。**伸手进塞满杂物的抽屉、绕开障碍够到钥匙、再把它捻出来**，恰好逐层激活：
> - 手是有体积的、要在杂物间穿行 → **闵可夫斯基/构型空间**把"两物体问题"变成"原点是否落入一个集合"；
> - 手指与抽屉壁、其他物体是否相撞 → **GJK/EPA** 离散碰撞 + 穿透深度/法向；
> - "离最近障碍还有多远、该往哪躲" → **SDF** 把边界变成可微势场，指引平滑伸入；
> - 只看到钥匙一角、得脑补全貌才能规划抓取 → **神经隐式几何 (DeepSDF/NGDF)**；
> - 摸到钥匙后捻动取出 → **接触流形与滚动接触**的微分几何。
>
> 全讲每引入一个概念，我们都回到这只抽屉："**它能否稳定地给出最近点、接触法向、穿透深度、和可用于优化的连续梯度？**"——这是几何服务于"安全推/滚/夹"的唯一标准。

整座大厦是一条从离散到连续、从布尔到可微的链：

| 层级 | 关键问题 | 理论对象 | 抽屉母题的映射 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **集合层** | 碰撞=什么？ | 点集相交、闵可夫斯基差 | 手与杂物是否相交 | §2 |
| **凸几何层** | 如何高效查询凸体？ | 支持函数、对偶 | 不显式构造、懒查询 | §3 |
| **响应层** | 撞了多深、往哪退？ | EPA、穿透深度、法向 | 退出抽屉壁的方向 | §3 |
| **连续场层** | 如何给优化器梯度？ | SDF、Eikonal、梯度=法向 | 平滑伸入而不贴壁 | §4 |
| **神经场层** | 如何学复杂/未见几何？ | DeepSDF、NGDF、UDF | 脑补钥匙被遮挡的部分 | §5 |
| **接触流形层** | 几何如何接力学？ | 抓取矩阵↔雅可比、Montana | 捻动取出钥匙 | §6 |

> [!important] Foundation 级判断标准（任何几何方法进入本库都要回答四问）
> 1. **输出是布尔还是连续场**（$C^{-1}$ 的"撞没撞" vs $C^1$ 的距离+梯度）？只有后者能进梯度优化。
> 2. **能否给出接触法向与穿透深度**？这是 [[ContactMechanics]] 摩擦锥与冲量响应的几何输入。
> 3. **凸还是非凸**（凸有支持函数/对偶的红利；非凸要分解或学）？
> 4. **梯度可信吗**（神经场可能"看似平滑、物理错误"，需 Eikonal/法向校准/接触验证）？

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>   [[Dynamics]] ─构型空间/运动学─┐                ┌── 最近点/法向/穿透 ──> [[ContactMechanics]]
>                              ├──> 【ComputationalGeometry】 │
> [[RepresentationLearning]] ─神经隐式─┤                       └── SDF 可微势场 ──> [[Optimization]]
>                              │
>             GPIS 隐式曲面 <──> [[InformationTheory]]
> ```
> 读法：动力学/运动学给几何"舞台"，表征学习给"学出来的几何"；几何的产出（最近点、法向、穿透、SDF 梯度）喂给接触力学与优化——**几何是接触与优化之间的翻译官**。

## 1. 几何：灵巧操作的物理语言

> [!tip] 本节四拍
> **直觉**（伸手进抽屉，几何不只是"形状"，而是物理交互发生的场所）→ **推导**（从二值避障到连续可微梯度的范式转移）→ **对比**（离散碰撞 vs 距离场 vs 神经隐式）→ **落点**（几何必须提供可导梯度来引导优化）。

几何学在灵巧操作里不仅描述形状，**它是物理交互发生的根本场所**。机器人学正经历范式转移：从基于采样的几何规划（RRT*/PRM）转向**基于优化的运动生成**。在这一转变中，计算几何的角色发生质变——**不再只提供二值碰撞检测，而必须提供连续、可导的梯度**，引导机器人在构型空间 (C-Space) 里找最优解。本讲解构三大几何支柱：闵可夫斯基和（C-space 障碍的理论基础）、GJK/EPA（离散接触工业标准）、SDF（现代轨迹优化的核心势场），并审视神经隐式表示如何重塑对非凸物体与抓取流形的理解。

### 1.1 三种范式对比（一张表看清演进方向）

| 特性 | 离散碰撞检测 | 距离场优化 | 神经隐式表示 |
|:--|:--|:--|:--|
| 核心算法 | GJK, EPA, SAT, BVH | EDT, SDF | DeepSDF, NeuralUDF, NGDF |
| 数学输出 | 布尔 + 穿透向量 | 标量场 $\phi$ + 梯度 $\nabla\phi$ | 流形距离、占据概率 |
| 连续性 | $C^{-1}$（不连续） | $C^0/C^1$（可微） | $C^\infty$（光滑近似） |
| 复杂度 | $O(1)\sim O(n)$/对 | $O(1)$ 查表 / $O(N)$ 建格 | $O(\text{MLP})$ 推理 |
| 操作中的角色 | 物理引擎接触解算、硬约束 | 运动规划代价（TrajOpt/CHOMP） | 形状补全、抓取生成、可微物理 |
| 局限 | 无排斥梯度、只知"已碰" | 体素存储大、精度受分辨率限 | 推理慢、需数据、有伪影 |

> [!important] 本节落点：零梯度问题
> 抽屉取钥匙时，若用布尔碰撞——手在自由空间里梯度恒为零，优化器**不知道往哪挪才能既不碰壁又靠近钥匙**。这就是 §4 SDF 要解决的"零梯度问题"，也是整条"从离散到连续"演进的根本动机。

------

## 2. 闵可夫斯基代数与构型空间障碍

> [!tip] 本节四拍
> **直觉**（手是有体积的刚体，不是质点——如何数学化"体积排斥"？）→ **推导**（闵可夫斯基差把相交测试变成"原点是否在一个集合内"）→ **对比**（显式构造 vs 隐式懒查询；凸 vs 非凸）→ **落点**（凸分解是效率与稳定的妥协）。

### 2.1 闵可夫斯基差：把"两物体相交"变成"原点在不在一个集合里"

凸点集 $A,B$ 的闵可夫斯基和 $A\oplus B=\{a+b\}$；碰撞检测更关心**闵可夫斯基差** $A\ominus B=\{a-b\mid a\in A,b\in B\}$。它的威力在于把两物体相交测试**化归为单个凸体与原点的位置关系**：

- **碰撞** $\iff$ $\mathbf 0\in(A\ominus B)$；
- **距离** = 原点到 $A\ominus B$ 边界的最短距离；
- **穿透深度** = 原点在内部时到边界的最短距离。

物理上 $A\ominus B$ 是"$A$ 相对 $B$ 所有发生接触的相对位置向量"——它不仅是碰撞检测基础，也是**滑移运动规划**的基础：手指要在物体表面滑而不脱离，控制轨迹必须严格沿 $A\ominus B$ 边界走（接 §6 的接触流形）。

### 2.2 构型空间障碍与"显式→隐式"的分水岭

运动规划把机器人视为点 $q\in\mathcal C$、把障碍在 C-space 膨胀：平移机器人 $A$ 与障碍 $B$ 的 C-space 障碍精确等于 $B\ominus A$。但一引入旋转 $SO(3)$，$\mathcal C_{obs}$ 就成了随旋转变化的流形截面。

> [!important] 关键分水岭：从显式构建到隐式懒查询
> 显式算高维（6-DoF 臂）的闵可夫斯基和**计算不可行**（复杂度随维度指数爆炸）。现代算法（GJK）**不显式构建 $A\ominus B$**，而是用**支持函数**在需要时"懒惰地"查询其局部几何（§3）。**这种"显式构建 → 隐式查询"的转变，是计算几何能用于高维机器人的关键。** 抽屉取钥匙时，我们从不真的算出"手相对所有杂物的差集"，只在 GJK 迭代需要时查几个支持点。

### 2.3 凸分解：非凸世界的妥协

现实操作对象（杯、钻、剪刀、钥匙）多非凸，而闵可夫斯基/支持函数的红利只对凸体良好。标准流程是**凸分解**：

- **V-HACD**：体素化 + 层次合并近似凸包。鲁棒，但易产生过多细碎凸包。
- **CoACD**：碰撞感知凹度度量，直接切割网格（而非体素化）生成凸包——**保留尖锐特征**（如钥匙齿），减少内部空隙/重叠，对插拔等精细操作至关重要。

> [!tip] 为什么不直接用非凸网格碰撞？
> 非凸-非凸碰撞极贵（遍历所有三角面），且穿透深度常**不连续或多值**，致物理引擎接触力剧烈震荡 (jittering)。凸分解是当前兼顾效率与稳定的妥协；未来方向是基于 SDF 的直接非凸查询（§4）。

------

## 3. 离散碰撞检测：GJK 与 EPA

> [!tip] 本节四拍
> **直觉**（手伸进抽屉，怎么快速判断"撞没撞、撞多深、往哪退"？）→ **推导**（支持函数=凸共轭对偶；GJK 用 simplex 逼近原点）→ **对比**（GJK 只判"撞没撞" vs EPA 给穿透深度+法向）→ **落点**（法向直接决定 [[ContactMechanics|摩擦锥]] 方向，错了抓取分析全失效）。

GJK 及其扩展 EPA 是现代物理引擎（Bullet/MuJoCo/PhysX）的基石。

### 3.1 支持函数：GJK 的灵魂

支持函数把复杂形状抽象成一个方向查询——"在方向 $\mathbf d$ 上物体最极端的点"：

$$
s_A(\mathbf d)=\arg\max_{\mathbf x\in A}(\mathbf x\cdot\mathbf d),\qquad s_C(\mathbf d)=s_A(\mathbf d)-s_B(-\mathbf d)\ \ (C=A\ominus B).
$$

后一式让我们**从不显式算 $C$，却能在 $C$ 的空间里漫游**（兑现 §2.2 的"隐式懒查询"）。

> [!note] 数学本质：支持函数 = Gauge 函数的 Fenchel 共轭
> 凸集 $A$ 的 Gauge 函数 $\gamma_A(\mathbf x)=\inf\{t>0:\mathbf x\in tA\}$，支持函数 $h_A(\mathbf d)=\sup_{\mathbf x\in A}\langle\mathbf d,\mathbf x\rangle$ 正是 $\gamma_A$ 的 **Fenchel 共轭**（与 [[Optimization#2.2 拉格朗日对偶：把约束"价格化"|凸优化对偶]]同源）。几何意义：$h_A(\mathbf d)$ 是法向为 $\mathbf d$ 的支撑超平面"刚好贴住" $A$ 时到原点的有符号距离——这就是为什么支持函数能直接给出**分离超平面**。

常用几何基元的支持映射有解析解，无需遍历顶点：

| 几何体 | $s(\mathbf d)$ |
|:--|:--|
| 球 | $\mathbf c+r\,\mathbf d/\|\mathbf d\|$ |
| 椭球 | $\mathbf c+D\,D\mathbf d/\|D\mathbf d\|$，$D=\mathrm{diag}(a,b,c)$ |
| 圆柱/胶囊 | 轴向投影 + 底圆最远点 / 线段支持 + 半径偏移 |
| 凸包 | $O(n)$ 暴力，或 **Hill Climbing** 沿邻接图爬坡 $O(\log n)$ |

> [!tip] Hill Climbing = 几何里的时间一致性
> 高多边形凸包（1000+ 顶点的手指模型）暴力搜每个顶点会成瓶颈。Hill Climbing 利用多面体邻接图：从上一帧支持点出发、沿"邻居中点积更大"的方向爬坡，通常 2–3 步收敛——这是 **temporal coherence** 在几何算法里的典型应用（与 [[ContactMechanics#5.2 两类求解器：直接 vs 迭代|接触求解的 warm-start]]、[[Optimization#7.2 基于梯度：SQP 与实时迭代 (RTI)|MPC warm-start]] 同思想）。

```python
import numpy as np
# GJK 核心循环：检测两个凸体是否相交（去防御代码，聚焦逻辑）
def support(shape_a, shape_b, d):                         # 闵可夫斯基差的支持点
    return shape_a.farthest(d) - shape_b.farthest(-d)

def gjk_intersection(shape_a, shape_b):
    d = np.array([1.0, 0, 0])                             # 任意初始方向
    simplex = [support(shape_a, shape_b, d)]
    d = -simplex[0]                                       # 下一搜索方向指向原点（贪婪包围原点）
    while True:
        a = support(shape_a, shape_b, d)
        if np.dot(a, d) < 0:                             # 早退：新点没越过原点 → 原点不可能在差集内
            return False                                  #        （a 已是该方向最极端点）
        simplex.append(a)
        contains, d, simplex = handle_simplex(simplex, d) # 检查原点是否被 simplex 包围 / 更新方向
        if contains:
            return True
# handle_simplex：3D 中处理 线段/三角形/四面体 三种情况，
#   本质是降维的 Voronoi 区域搜索——保留最靠近原点的特征、丢弃其余、方向设为指向原点。
#   数值陷阱：近共线/近共面时叉积≈0，须引入 EPSILON 处理退化，否则除零/精度爆炸。
```

### 3.2 EPA：从"撞了"到"撞多深、往哪退"

GJK 只告诉你"撞了"。物理模拟还需**穿透深度**和**接触法向**。**EPA (Expanding Polytope Algorithm)** 接管 GJK 终止时那个含原点的 simplex，向外"炸开"：① 以四面体为初始多面体；② 找离原点最近的面（距离 $d$、法向 $\mathbf n$）；③ 沿 $\mathbf n$ 查支持点 $p$；④ 若 $p$ 到原点距离与 $d$ 之差 $<\epsilon$ 则收敛——$d$=穿透深度、$\mathbf n$=接触法向；⑤ 否则把 $p$ 加入、移除对 $p$ 可见的面、修补多面体，回到②。

> [!warning] EPA 是工程噩梦，但法向至关重要
> 曲面上面数可能无限增长（需 `MAX_ITERATIONS`）；穿透深或接触面平时，最近面会因浮点误差在相邻面间跳动（数值震荡）；高效实现需维护半边数据结构。**为什么对灵巧操作至关重要**：软指会微小穿透，EPA 给的法向**直接决定摩擦锥方向**，进而决定抓取是否满足 [[ContactMechanics#3.2 力闭合 vs 形闭合：抓取稳定性的数学条件|力闭合]]——**法向算错，抓取稳定性分析全盘失效**。抽屉取钥匙时，正是 EPA 的法向告诉手指"该往哪个方向退出抽屉壁、又不松开钥匙"。

------

## 4. 有向距离场 (SDF)：连续优化的基石

> [!tip] 本节四拍
> **直觉**（GJK 是离散"开关"，SDF 是连续"旋钮"——自由空间里也告诉你"离障碍多远"）→ **推导**（SDF 定义；梯度=单位法向）→ **对比**（SDF vs 布尔碰撞的零梯度问题）→ **落点**（把避碰变成无约束优化，但小心局部极小）。

### 4.1 定义与梯度的物理意义

障碍集合 $\Omega$ 的有向距离函数：外部为正、边界为零、内部为负，$\phi(\mathbf x)=\pm d(\mathbf x,\partial\Omega)$。**SDF 最强大的是梯度** $\nabla\phi$：① 方向=**离开最近障碍最快的方向**；② 模长 $\|\nabla\phi\|=1$（几乎处处，除骨架轴 medial axis 外，满足 **Eikonal 方程** $\|\nabla\phi\|=1$）。于是避障变成无约束优化——不再说"不能碰"，而是定义代价：

$$
J_{obs}(\mathbf q)=\sum_{\mathbf x\in\text{Robot}(\mathbf q)}\max(0,\ \epsilon-\phi(\mathbf x)),
$$

它在安全距离 $\epsilon$ 外为零、进入危险区后陡升，梯度 $-\nabla\phi$ 产生把手推离障碍的"虚拟力"。这正是抽屉取钥匙时"贴近壁就被推开、留出余量平滑伸入"的机制。

### 4.2 为什么 SDF 优于布尔碰撞：零梯度问题

> [!important] 这是 §1 落点的兑现
> 布尔检测 $C(\mathbf q)\in\{0,1\}$：手在自由空间梯度恒为零，优化器**不知往哪挪**。SDF 即使在自由空间也给距离值，可优化"最大化最小距离"，让手**自然地在杂物中间穿行而非贴壁**。这是 [[Optimization#6. 核心算法实现：iLQR/DDP 与"让梯度穿过接触"的三方案|TrajOpt/CHOMP]] 能用梯度法做运动规划的前提，也与 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|软接触平滑]] 同一哲学——**把"非黑即白"的硬约束变成"有坡度"的连续场，让梯度能流动**。

```python
import numpy as np
# 用 SDF 梯度做轨迹平滑 + 避障（CHOMP/TrajOpt 的微观机制）
def sdf_sphere(p, c, r):  return np.linalg.norm(p - c) - r          # 球体 SDF
def sdf_grad(p, c):       d = p - c; return d / (np.linalg.norm(d) + 1e-9)  # 梯度=单位法向

def optimize_path(waypoints, obs_c, obs_r, lr=0.01, iters=100, eps=0.5):
    path = np.copy(waypoints)
    for _ in range(iters):
        g = np.zeros_like(path)
        for i in range(1, len(path)-1):
            g[i] += 0.5 * ((path[i-1]-path[i]) + (path[i+1]-path[i]))  # 平滑项：相邻点弹簧力
            dist = sdf_sphere(path[i], obs_c, obs_r)
            if dist < eps:                                           # 碰撞项：仅进入影响范围才排斥
                g[i] += 10.0 * (eps - dist) * sdf_grad(path[i], obs_c)  # 越近排斥越大
        path[1:-1] += lr * g[1:-1]                                   # 起终点固定
    return path
```

> [!warning] 局部极小：基于梯度规划器的死穴
> 若初始路径直接穿过障碍中心，梯度可能相互抵消、或把路径推向更拥堵的一侧。这正是 [[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|非凸景观]]的局部极小，也是为什么 TrajOpt/CHOMP 需好的初值或结合全局规划器（RRT）——呼应 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|同伦/continuation method]]：用一个易解的近邻问题热启动。

------
