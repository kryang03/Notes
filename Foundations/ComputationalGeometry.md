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
---

# 计算几何在机器人灵巧操作中的深度解析：从离散接触物理到连续流形优化

# Computational Geometry in Robotic Dexterous Manipulation: From Discrete Contact Physics to Continuous Manifold Optimization

> [!tip] 相关领域
> - [[ContactMechanics]] - 接触点几何与接触雅可比
> - [[Optimization]] - 基于SDF的轨迹优化 (TrajOpt, CHOMP)
> - [[Dynamics]] - 刚体运动学与构型空间
> - [[RepresentationLearning]] - 神经隐式表示 (DeepSDF, Neural Grasp)
>
> **核心算法链**: 闵可夫斯基和 → GJK/EPA → SDF → 神经隐式场

## 1. 引言：几何——灵巧操作的物理语言

## 1. Introduction: Geometry as the Physics Language of Manipulation

在机器人灵巧操作（Dexterous Manipulation）的深层逻辑中，几何学不仅仅是关于形状的描述，它是物理交互发生的根本场所。作为操作领域的科研人员，我们必须超越简单的“避障”思维，重新审视几何数据如何编码物理约束（Physical Constraints）和任务流形（Task Manifolds）。

当前的机器人学正处于一个范式转移的关键时刻：从传统的基于采样的几何规划（如RRT*、PRM）向基于优化的运动生成（Optimization-based Motion Generation）转变。在这一转变中，计算几何的角色发生了质的飞跃——它不再仅仅提供二值的碰撞检测（Collision Detection），而是必须提供连续、可导的梯度信息，以引导机器人在复杂的构型空间（Configuration Space, C-Space）中寻找最优解。

本报告将从严谨的数学视角和工程实践出发，系统解构支撑现代灵巧操作的三大几何支柱：**闵可夫斯基和（Minkowski Sums）**作为构型空间障碍物的理论基础；\**GJK与EPA算法\**作为离散接触检测的工业标准；以及**有向距离场（Signed Distance Fields, SDF）**作为现代轨迹优化的核心势能场。同时，我们将审视**神经隐式表示（Neural Implicit Representations）**如何正在重塑我们对非凸物体和抓取流形的理解。

### 1.1 核心范式对比 (Core Paradigms Comparison)

为了理解计算几何在操作中的演进，我们首先对比三种核心几何处理范式：

| **特性 (Feature)** | **离散碰撞检测 (Discrete Collision)** | **距离场优化 (Distance Field Opt.)**                  | **神经隐式表示 (Neural Implicit)** |
| ------------------ | ------------------------------------- | ----------------------------------------------------- | ---------------------------------- |
| **核心算法**       | GJK, EPA, SAT, BVH                    | EDT (Euclidean Distance Transform), SDF               | DeepSDF, NeuralUDF, NGDF           |
| **数学输出**       | Boolean (True/False), Depth vector    | Scalar Field ($\mathbb{R}$), Gradient ($\nabla \phi$) | Manifold Distance, Occupancy Prob. |
| **连续性**         | $C^{-1}$ (Discontinuous)              | $C^0$ or $C^1$ (Continuous/Differentiable)            | $C^\infty$ (Smooth approximation)  |
| **计算复杂度**     | $O(1)$ to $O(n)$ per pair             | $O(1)$ lookup / $O(N)$ grid gen                       | $O(MLP)$ inference                 |
| **在操作中的角色** | 物理引擎接触解算、硬约束检查          | 运动规划代价函数 (TrajOpt, CHOMP)                     | 形状补全、抓取姿态生成、可微物理   |
| **局限性**         | 无法提供排斥梯度，仅知"已碰撞"        | 存储消耗大(Voxel)，精度受分辨率限制                   | 推理慢，训练需数据，存在伪影       |



------

## 2. 闵可夫斯基代数与构型空间障碍物

## 2. Minkowski Algebra and Configuration Space Obstacles

在操作任务中，机器人不是一个质点，而是一个具有体积的刚体集合。要在数学上处理这种体积排斥，最优雅的工具莫过于**闵可夫斯基和（Minkowski Sum）**。它不仅仅是一种几何运算，更是将工作空间（Workspace）障碍物映射到构型空间（C-Space）的桥梁。

### 2.1 闵可夫斯基差的物理本质 (The Physics of Minkowski Difference)

对于两个凸点集 $A, B \subset \mathbb{R}^d$，其闵可夫斯基和定义为 $A \oplus B = \{a+b | a \in A, b \in B\}$。但在碰撞检测中，我们更关注**闵可夫斯基差（Minkowski Difference）**：

$$A \ominus B = A \oplus (-B) = \{ a - b \mid a \in A, b \in B \}$$

**深度解析：**

为什么这个概念如此重要？因为它将两个物体的相交测试（Intersection Test）转化为单个凸体与原点（Origin）的位置关系测试：

- **碰撞条件：** 当且仅当原点 $\mathbf{0} \in (A \ominus B)$ 时，$A$ 与 $B$ 相交 。
- **距离度量：** $A$ 与 $B$ 之间的欧几里得距离等于原点到集合 $A \ominus B$ 边界的最短距离。
- **穿透深度：** 如果原点在内部，穿透深度等于原点到 $A \ominus B$ 边界的最短距离。

在物理意义上，$A \ominus B$ 代表了物体 $A$ 相对于物体 $B$ 所有可能的相对位置向量，使得两者发生接触。这不仅是碰撞检测的基础，也是**滑移运动（Sliding Motion）**规划的基础——如果你想让手指在物体表面滑动而不脱离接触，你的控制轨迹必须严格沿着 $A \ominus B$ 的边界移动 。

### 2.2 构型空间中的障碍物膨胀 (C-Space Obstacle Inflation)

在机器人运动规划中，我们将机器人视为一个点 $q \in \mathcal{C}$，而将障碍物 $O$ 在 $\mathcal{C}$ 空间中进行“膨胀”。对于平移机器人 $A$ 和障碍物 $B$，C-Space障碍物 $CB$ 精确地等于 $B \ominus A(0)$。

然而，当引入旋转自由度（$SO(3)$）时，问题变得极其复杂。$\mathcal{C}_{obs}$ 不再是静态的，而是随着旋转参数变化的流形截面。

- **高维困境：** 显式计算高维（如6-DOF机械臂）的闵可夫斯基和在计算上是不可行的（计算复杂度随维度指数级增长）。
- **隐式替代：** 现代算法（如GJK）并不显式构建 $A \ominus B$，而是通过**支持函数（Support Functions）**在需要时“懒惰地”（Lazily）查询该集合的局部几何特征。这种从“显式构建”到“隐式查询”的转变，是计算几何在机器人领域应用的关键分水岭 。

### 2.3 凸分解 (Convex Decomposition)

现实世界中的操作对象（如杯子、电钻、剪刀）绝大多数是非凸的。闵可夫斯基和性质仅对凸体良好保持（两个凸体的Minkowski和仍是凸体）。对于非凸物体，标准的工业流程是**凸分解（Convex Decomposition）**。

**技术演进：**

1. **V-HACD (Volumetric Hierarchical Approximate Convex Decomposition):** 基于体素的层次化分解。它通过体素化网格，然后逐步合并体素来生成近似凸包。优点是鲁棒，缺点是可能产生过多的细碎凸包 。
2. **CoACD (Collision-Aware Convex Decomposition):** 最新的进展。它引入了“碰撞感知”的凹度度量（Concavity Metric），通过直接切割网格（Cutting Planes）而非体素化来生成凸包。这保留了尖锐特征，减少了甚至消除了在物体内部产生空隙或重叠的现象，对于精细操作（如插拔任务）至关重要 。

**批判性视角：** 为什么不直接用非凸网格做碰撞？因为非凸-非凸的碰撞检测极其昂贵（需遍历所有三角面片），且计算出的穿透深度（Penetration Depth）往往是不连续或多值的，会导致物理引擎中的接触力发生剧烈震荡（Jittering）。凸分解是目前兼顾效率与稳定性的妥协之选，但未来的方向可能是基于SDF的直接非凸查询 。

------

## 3. 离散碰撞检测算法的核心逻辑：GJK 与 EPA

## 3. Core Logic of Discrete Collision Algorithms: GJK and EPA

Gilbert-Johnson-Keerthi (GJK) 算法及其扩展 Expanding Polytope Algorithm (EPA) 是现代物理引擎（如Bullet, MuJoCo, PhysX）的基石。作为首席科学家，我要求您不仅要会调用库，更要理解其内部的数值稳定性逻辑。

### 3.1 GJK算法：单纯形的迭代演化 (GJK: Iterative Simplex Evolution)

GJK利用了凸集的性质：两个凸集不相交，当且仅当存在一个分离轴。算法本质上是在寻找这就分离轴，或者证明其不存在（即原点被包含）。

#### 3.1.1 支持函数 (The Support Function)

支持函数是GJK的灵魂。它将复杂的几何形状抽象为一个简单的数学查询：

$$s_A(\mathbf{d}) = \underset{\mathbf{x} \in A}{\text{argmax}} (\mathbf{x} \cdot \mathbf{d})$$

即在方向 $\mathbf{d}$ 上找到物体 $A$ 最极端的点。

对于闵可夫斯基差 $C = A \ominus B$，其支持点为：

$$s_C(\mathbf{d}) = s_A(\mathbf{d}) - s_B(-\mathbf{d})$$

这使得我们从未显式计算 $C$，却能在 $C$ 的空间中漫游 。

> [!note] Support Mapping 的数学本质
> 支持函数的威力来自**凸共轭对偶性 (Convex Conjugate Duality)**。对于凸集 $A$，其 **Gauge Function**（或 Minkowski Functional）定义为：
> 
> $$\gamma_A(\mathbf{x}) = \inf \{ t > 0 : \mathbf{x} \in t \cdot A \}$$
> 
> 支持函数 $h_A(\mathbf{d}) = \sup_{\mathbf{x} \in A} \langle \mathbf{d}, \mathbf{x} \rangle$ 正是 $\gamma_A$ 的 **Fenchel 共轭**。
> 
> **几何意义**：$h_A(\mathbf{d})$ 是过原点、法向为 $\mathbf{d}$ 的超平面"刚好接触" $A$ 时，距原点的有符号距离。这也是为什么支持函数能够直接给出分离超平面。

**Support Mapping 在灵巧操作中的价值**：

对于实际使用的几何基元，支持映射有解析解，无需遍历顶点：

| 几何体 | Support Mapping $s(\mathbf{d})$ |
|--------|-------------------------------|
| **球 (Sphere)** | $\mathbf{c} + r \frac{\mathbf{d}}{\|\mathbf{d}\|}$ |
| **椭球 (Ellipsoid)** | $\mathbf{c} + D \frac{D\mathbf{d}}{\|D\mathbf{d}\|}$，$D = \text{diag}(a, b, c)$ |
| **圆柱 (Cylinder)** | 沿轴向投影 + 底圆/顶圆上的最远点 |
| **胶囊 (Capsule)** | 线段支持 + 半径偏移 |
| **凸包 (Convex Hull)** | $O(n)$ 暴力搜索，或 **Hill Climbing** 利用局部邻接关系 $O(\log n)$ |

> [!tip] 工程洞察：Hill Climbing 优化
> 对于高多边形凸包（如 1000+ 顶点的手指模型），暴力搜索每个顶点会成为瓶颈。**Hill Climbing** 利用了多面体的邻接图：从上一帧的支持点出发，沿梯度（邻居中点积更大的方向）爬坡，通常 2-3 步就能收敛。这是 **Temporal Coherence（时间一致性）** 在几何算法中的典型应用。

#### 3.1.2 核心逻辑实现 (Python Implementation)

以下代码展示了GJK的核心循环。注意，单纯形（Simplex）在3D中最多包含4个点（四面体）。

Python

```
import numpy as np

# 辅助函数：支持函数
def support(shape_a, shape_b, direction):
    # shape_a.get_farthest_point(d) 返回物体A在方向d上的最远顶点
    # 注意 shape_b 使用 -direction
    return shape_a.get_farthest_point(direction) - shape_b.get_farthest_point(-direction)

def gjk_intersection_test(shape_a, shape_b):
    """
    GJK 算法核心逻辑：检测两个凸体是否相交
    返回: (bool) 是否碰撞, (list) 最终的单纯形
    """
    # 1. 初始猜测方向 (可以是任意非零向量，通常选中心连线)
    direction = np.array([1.0, 0.0, 0.0])
    
    # 2. 获取第一个闵可夫斯基差的点
    c = support(shape_a, shape_b, direction)
    simplex = [c]
    
    # 3. 下一个搜索方向指向原点 (这就体现了贪婪策略：试图包围原点)
    direction = -c 
    
    while True:
        # 4. 沿当前方向寻找新点
        a = support(shape_a, shape_b, direction)
        
        # 5. 早期退出判定：
        # 如果新点 a 在方向 direction 上的投影没有越过原点 (dot < 0)，
        # 说明原点不可能在闵可夫斯基差内（因为a已经是该方向最极端的点了）。
        if np.dot(a, direction) < 0:
            return False, simplex # 无碰撞
        
        simplex.append(a)
        
        # 6. 单纯形处理 (DoSimplex):
        # 检查原点是否被当前的单纯形包围，或者更新单纯形和搜索方向
        contains_origin, direction, simplex = handle_simplex(simplex, direction)
        
        if contains_origin:
            return True, simplex # 发生碰撞

# 单纯形处理逻辑 (Handle Simplex) - 这是最易出错的部分
# 需要处理 Line, Triangle, Tetrahedron 三种情况 (在3D中)
def handle_simplex(simplex, direction):
    # 以点A为最新加入的点，检查原点相对于单纯形各特征（顶点、边、面）的位置
    # 利用叉积判断Voronoi区域
    # 此处省略几十行复杂的向量运算逻辑...
    # 核心思想：保留最靠近原点的特征，丢弃其他点，并将方向设为指向原点
    pass 
```

**Voronoi区域判定逻辑 (Insight):**

`handle_simplex` 函数实际上是在执行一个降维的Voronoi区域搜索。

- 如果是线段 $AB$，它检查原点是在 $AB$ 之间，还是在 $A$ 外侧（$B$ 外侧不可能，因为 $A$ 是最后加入的）。
- 如果是三角形 $ABC$，它检查原点是在三角形平面上下，还是在边的外侧。
- **数值陷阱：** 当三个点几乎共线或四个点几乎共面时，叉积结果接近零，归一化会导致除零错误或精度爆炸。必须引入 `EPSILON` 并处理退化情况 。

### 3.2 EPA算法：从碰撞检测到物理响应 (EPA: From Detection to Response)

GJK只能告诉你“撞了”。但在物理模拟中，你需要知道“撞多深”（Penetration Depth）以及“怎么推开”（Contact Normal）。**Expanding Polytope Algorithm (EPA)** 接管了GJK留下的包含原点的单纯形，并将其向外“炸开”。

#### 3.2.1 算法流程

1. **初始多面体：** 使用GJK终止时的单纯形（四面体）作为初始多面体。
2. **寻找最近面：** 在多面体表面找到距离原点最近的面 $F_{nearest}$，其距离为 $d$，法线为 $\mathbf{n}$。
3. **扩展：** 沿法线 $\mathbf{n}$ 查询支持点 $p = s_{A \ominus B}(\mathbf{n})$。
4. **终止判定：** 如果 $p$ 到原点的距离与 $d$ 的差值小于阈值 $\epsilon$，则收敛。$d$ 即为穿透深度，$\mathbf{n}$ 为接触法线。
5. **重构：** 如果未收敛，将 $p$ 加入多面体，移除所有对 $p$ 可见的面（Lit Faces），用 $p$ 与这些面的边缘构建新的锥体，修补多面体漏洞。回到步骤2 。

#### 3.2.2 性能与稳定性的博弈

EPA在理论上很完美，但在工程上是噩梦：

- **无限循环：** 在曲面上，面数可能无限增加。通常需要设置 `MAX_ITERATIONS`。
- **数值震荡：** 当穿透很深或接触面很平时，最近面的选择会因为浮点误差而在相邻面间跳动。
- **Python实现挑战：** 维护一个动态的半边数据结构（Half-edge data structure）或邻接表来快速移除和添加面是高效实现EPA的关键 。

**为什么EPA对灵巧操作很重要？** 在抓取中，软指（Soft Finger）往往会发生微小的穿透。EPA提供的法线方向直接决定了摩擦锥的方向，进而决定了抓取是否满足**力封闭（Force Closure）**。错误的法线计算会导致抓取稳定性分析完全失效 。

------

## 4. 有向距离场 (SDF)：连续操作优化的基石

## 4. Signed Distance Fields (SDF): The Cornerstone of Continuous Optimization

如果说GJK是离散的“开关”，那么SDF就是连续的“旋钮”。在现代基于优化的运动规划（如TrajOpt, CHOMP, GPMP2）中，SDF是不可或缺的核心组件。

### 4.1 SDF的数学定义与梯度属性 (Mathematical Definition & Gradient Properties)

对于环境中的障碍物集合 $\Omega$，其有向距离函数 $\phi: \mathbb{R}^3 \to \mathbb{R}$ 定义为：

$$\phi(\mathbf{x}) = \begin{cases} d(\mathbf{x}, \partial \Omega) & \text{if } \mathbf{x} \notin \Omega \quad (\text{外部，正值}) \\ 0 & \text{if } \mathbf{x} \in \partial \Omega \\ -d(\mathbf{x}, \partial \Omega) & \text{if } \mathbf{x} \in \text{int}(\Omega) \quad (\text{内部，负值}) \end{cases}$$

其中 $d(\cdot)$ 是欧几里得度量。

**梯度的物理意义：**

SDF最强大的特性在于其梯度 $\nabla \phi(\mathbf{x})$：

1. **方向：** $\nabla \phi(\mathbf{x})$ 是单位向量，指向距离增加最快的方向，即**离开最近障碍物的方向**。
2. **模长：** 在几乎所有点 $|\nabla \phi(\mathbf{x})| = 1$（除了骨架轴 Medial Axis 处）。

这使得我们可以将避障问题转化为一个无约束优化问题。我们不再说“不能碰障碍物”，而是定义一个代价函数（Cost Function）：

$$J_{obs}(\mathbf{q}) = \sum_{\mathbf{x} \in \text{Robot}(\mathbf{q})} \max(0, \epsilon - \phi(\mathbf{x})) \cdot |\nabla \phi(\mathbf{x})|$$

这个Hinge Loss函数在安全距离 $\epsilon$ 外为0，在进入危险区后迅速上升，并且其梯度 $-\nabla \phi$ 会产生一个将机器人推离障碍物的“虚拟力” 。

### 4.2 为什么SDF优于布尔碰撞？ (SDF vs. Boolean Collision)

在轨迹优化（Trajectory Optimization）中，布尔碰撞检测会导致**零梯度问题（Zero Gradient Problem）**。

- **布尔检测：** $C(\mathbf{q}) \in \{0, 1\}$。如果机器人处于自由空间，梯度为0，优化器不知道该往哪里移动才能远离障碍物（或者保持距离）。
- **SDF：** 即使在自由空间，SDF也提供距离值。我们可以优化“最大化最小距离”，从而让机器人自然地在障碍物中间穿行，而不是贴着墙走 。

### 4.3 梯度下降路径规划示例 (Code Implementation)

以下Python代码展示了如何利用SDF梯度进行简单的轨迹平滑与避障优化。这是理解CHOMP/TrajOpt微观机制的核心。

Python

```
import numpy as np

def sdf_sphere(point, center, radius):
    """简单的球体SDF"""
    return np.linalg.norm(point - center) - radius

def sdf_gradient(point, center, radius):
    """计算SDF相对于位置的梯度 (即排斥力方向)"""
    diff = point - center
    dist = np.linalg.norm(diff)
    if dist < 1e-6: return np.zeros_like(point) # 避免除零
    return diff / dist # 单位向量

def optimize_path_sgd(waypoints, obs_center, obs_radius, lr=0.01, iterations=100):
    """
    使用随机梯度下降(SGD)优化路径
    Cost = Smoothness + Collision
    """
    path = np.copy(waypoints)
    n_points = len(path)
    epsilon = 0.5 # 安全边距
    
    for _ in range(iterations):
        grads = np.zeros_like(path)
        
        # 1. 平滑性梯度 (拉向相邻点，模拟弹簧力)
        # Cost_smooth = ||q_i - q_{i-1}||^2
        # dCost/dq_i = 2(q_i - q_{i-1}) +...
        for i in range(1, n_points - 1):
            force_smooth = (path[i-1] - path[i]) + (path[i+1] - path[i])
            grads[i] += 0.5 * force_smooth # 权重系数
            
        # 2. 碰撞梯度 (SDF排斥力)
        for i in range(1, n_points - 1):
            dist = sdf_sphere(path[i], obs_center, obs_radius)
            
            # 只有当进入影响范围(epsilon)时才产生排斥力
            if dist < epsilon:
                # Cost_coll = (epsilon - dist)^2
                # Gradient direction = -SDF_gradient (推离障碍物)
                grad_dir = sdf_gradient(path[i], obs_center, obs_radius)
                # 越近排斥力越大
                force_coll = 10.0 * (epsilon - dist) * grad_dir 
                grads[i] += force_coll
        
        # 更新路径 (保持起点终点固定)
        path[1:-1] += lr * grads[1:-1]
        
    return path
```

**深度分析：** 上述代码虽然简单，却揭示了基于梯度的规划器的核心弱点：**局部极小值（Local Minima）**。如果初始路径直接穿过障碍物中心，梯度可能会相互抵消，或者将路径推向错误的一侧（例如，应该从上方绕过，却被推向下方更拥堵的区域）。这就是为什么TrajOpt和CHOMP通常需要一个较好的初始猜测（Initial Guess），或者结合全局规划器（如RRT）使用 。

------

## 5. 神经隐式表示：DeepSDF与几何学习的前沿

## 5. Neural Implicit Representations: Frontiers of DeepSDF and Geometric Learning

随着深度学习的介入，SDF的表示形式正在发生革命。传统的SDF需要预先计算并存储在体素网格（Voxel Grid）中，分辨率受限于显存。**Neural SDFs** 通过神经网络拟合SDF函数，实现了无限分辨率的连续查询。

### 5.1 DeepSDF架构解析 (Architecture Deep Dive)

DeepSDF的核心思想是学习一个函数 $f_\theta(\mathbf{x}, \mathbf{z}) \approx \text{SDF}(\mathbf{x})$，其中 $\mathbf{z}$ 是代表形状的潜在编码（Latent Code）。

- **输入：** 3D坐标 $\mathbf{x} \in \mathbb{R}^3$ 和 形状编码 $\mathbf{z} \in \mathbb{R}^k$。
- **输出：** 标量距离值 $s \in \mathbb{R}$。
- **训练：** 这是一个**自解码器（Auto-decoder）**架构。训练时不仅优化网络参数 $\theta$，还同时优化每个训练样本的潜在编码 $\mathbf{z}_i$ 。

**优势分析：**

1. **非凸拓扑的平滑近似：** 神经网络擅长拟合高频细节和复杂的非凸拓扑。对于具有薄壁、孔洞的复杂操作对象（如镂空的把手），DeepSDF比凸分解能提供更精确的几何描述 。
2. **数据驱动的补全：** 当机器人视觉系统只能看到物体的正面（Partial View）时，DeepSDF可以基于先验知识“脑补”出背面的几何形状，这对于规划抓取点至关重要。

### 5.2 Neural Grasp Distance Fields (NGDF)

DeepSDF表示的是物体表面，而**NGDF**将这一概念推广到了任务空间。 NGDF学习的场函数是 $f(\mathbf{T}_{ee}) = d_{grasp}$，即输入末端执行器的6D位姿 $\mathbf{T}_{ee}$，输出距离“成功抓取流形”的距离 。

- **物理意义：** 传统的抓取规划是“采样-评分”机制。NGDF将其转化为“梯度优化”机制。我们可以直接对NGDF求梯度 $\nabla f(\mathbf{T}_{ee})$，然后沿着梯度下降，将机械手“吸附”到最近的可行抓取姿态上。
- **结合TrajOpt：** NGDF可以直接作为TrajOpt的一个代价项。优化器不仅规划避障轨迹，还同时优化抓取姿态，实现了接近（Reaching）与抓取（Grasping）的联合优化 。

**局限性与挑战：** 神经SDF并非完美的。它们通常需要大量的离线训练数据。在推理时，通过反向传播求解潜在编码 $\mathbf{z}$ 可能很慢。此外，神经网络可能在训练数据分布之外产生非物理的伪影（Ghost Geometry），导致机器人试图避开不存在的障碍物。这是目前**可微物理（Differentiable Physics）**研究的热点 。

------

## 6. 接触流形与运动学对偶性

## 6. Contact Manifolds and Kinematic Duality

在灵巧操作中，所有的几何计算最终都要服务于力学控制。**接触流形（Contact Manifold）**是连接几何与力学的界面。

### 6.1 抓取矩阵与手雅可比的对偶性 (Duality of Grasp Matrix and Hand Jacobian)

在多指灵巧手中，我们需要协调手指运动以控制物体。这里有两个核心矩阵：

1. **抓取矩阵 (Grasp Matrix, $G$):** 描述接触力 $\mathbf{f}_c$ 如何映射到物体坐标系下的合外力（Wrench）$\mathbf{w}_{ext}$。

   $$\mathbf{w}_{ext} = G \mathbf{f}_c$$

   $G$ 的结构完全取决于接触点的几何位置和法线方向 。

2. **手雅可比 (Hand Jacobian, $J_h$):** 描述关节速度 $\dot{\mathbf{q}}$ 如何映射到接触点速度 $\mathbf{v}_c$。

   $$\mathbf{v}_c = J_h \dot{\mathbf{q}}$$

**对偶关系：**

根据虚功原理（Virtual Work Principle），如果忽略摩擦耗散，物体速度 $\mathbf{v}_{obj}$ 对接触点速度的约束关系由 $G$ 的转置给出：

$$\mathbf{v}_{c, \text{virtual}} = G^T \mathbf{v}_{obj}$$

这是一个深刻的物理洞察：**几何上的约束（$G$）直接定义了运动学上的相容性（$G^T$）**。如果 $J_h \dot{\mathbf{q}} \neq G^T \mathbf{v}_{obj}$，则意味着接触点发生了相对滑动（Sliding）或脱离（Breaking Contact）。

### 6.2 滚动接触的微分几何 (Differential Geometry of Rolling Contact)

在高级操作（如手指捻动硬币）中，我们希望维持**纯滚动（Pure Rolling）\**接触。这是非完整约束（Non-holonomic constraints）。 Montana公式描述了接触点坐标 $(u, v)$ 在两个曲面上随时间的演化。这需要计算曲面的\**曲率形式（Curvature Form）\**和\**度量张量（Metric Tensor）**。

- **应用：** 为了规划滚动操作，我们需要精确的几何模型来计算表面法线和曲率。多面体近似（如网格）在这里会失效，因为其曲率在顶点和棱边处是狄拉克δ函数（无限大）。因此，对于精细的滚动操作，基于NURBS或Neural SDF的光滑几何表示是必须的 。

------

## 7. 结论与建议

## 7. Conclusion and Recommendations

通过对计算几何在机器人灵巧操作中应用的深度剖析，我们可以得出以下结论：

1. **几何处理的分层架构：** 现代机器人系统不应依赖单一的几何算法。应构建分层的处理管线：底层使用 **BVH** 进行广相剔除；中层使用 **GJK/EPA** 处理精细的物理接触和力解算；顶层使用 **SDF** 和 **NGDF** 进行基于梯度的轨迹和抓取优化。
2. **SDF是优化的核心：** 从离散的碰撞状态转向连续的SDF势场，是实现平滑、自然、类人操作动作的关键。掌握SDF的构建（EDT）和学习（DeepSDF）是高级运动规划的前提。
3. **神经几何的潜力与风险：** 神经隐式表示提供了处理复杂非凸拓扑的强大能力，特别是对于未见物体（Unseen Objects）的泛化。但必须警惕其推理延迟和非物理的几何伪影。

**构建Obsidian知识库的建议：**

- **标签体系：** 将算法分为 `#DiscreteCollision` (GJK, EPA) 和 `#ContinuousOptimization` (SDF, TrajOpt)。
- **关联链接：** 在 `DeepSDF` 条目中，务必链接到 `Level Set Methods` 和 `Auto-decoder`，强调其数学本质。在 `Contact Manifold` 条目中，链接到 `Screw Theory` 和 `Grasp Matrix`，强调几何与力学的对偶性。
- **代码片段：** 保存 GJK 的单纯形处理逻辑和 SDF 的梯度计算代码，这是复现这些算法最容易出错的地方。

作为首席科学家，我建议您接下来的研究重点关注**可微碰撞检测（Differentiable Collision Detection）**，即如何将GJK/EPA的过程可微化，从而将硬接触约束反向传播到控制策略中。这是目前Robotics Learning领域的圣杯。

------

## 8. 相关论文 (PapersRecap)

以下论文涉及本 Foundation 中的计算几何技术：

### SDF与距离场表示
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]: SDF引导的双臂避障规划
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing|Robot Synesthesia]]: 视觉触觉几何重建
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction|TRANSIC]]: 几何对齐的迁移学习

### 点云与3D表示
- [[Proximity Perception-Based Grasping Intelligence (P2GI)|P2GI]]: 部件级点云分割与几何推理
- [[RotateIt - General In-Hand Object Rotation with Vision and Touch|RotateIt]]: 点云状态估计与旋转表示

### 接触几何与抓取分析
- [[Lessons from Learning to Spin Pens|Lessons from Spin Pens]]: 几何形状对操作可行性的影响
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]]: 接触几何的 Sim-to-Real 对齐

------

**References Citations:** Minkowski Sums & C-Space. GJK Algorithm details. EPA Algorithm & Penetration Depth. SDF, CHOMP, TrajOpt & Optimization. DeepSDF, NGDF & Neural Implicit. Contact Manifolds, Grasp Matrix & Kinematics. Convex Decomposition (V-HACD, CoACD).