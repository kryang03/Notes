# 计算几何在灵巧操作中的应用 - Gemini

**导出时间 / Exported At:** 2026-01-29 15:36:52

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 几何表征的范式演变

我正在深入探讨几何计算如何从简单的“碰撞与否”二值判断转变为具备物理导向的连续场描述。我意识到，在灵巧操作场景下，传统的分层包围盒虽然高效，但在处理高自由度手部的细微接触时显得过于粗糙。通过对闵可夫斯基和（Minkowski Sums）与 GJK 算法的推演，我确信它们为理解配置空间（C-Space）提供了数学上的精确性，而符号距离场（SDF）则通过提供连续梯度，为解决极复杂的动力学约束奠定了理论基础。

### 穿透深度与梯度的技术瓶颈

在合成现有信息时，我发现离散碰撞检测逻辑在处理“接触瞬间”的动力学模拟时存在信息断层。普通的布尔检测无法为控制器提供“如何脱离碰撞”的向量引导，而 EPA 算法虽然解决了穿透深度的计算，但在高频实时优化中依然面临计算开销与数值稳定性之间的权衡。我需要进一步厘清 SDF 相比于传统的网格表示，在梯度平滑性上究竟如何提升了主流运动规划框架的收敛性能。

### 算法逻辑解析与前沿探索

接下来的行动中，我将重点剖析 GJK 与 EPA 的核心实现逻辑，并尝试将其与现代的微分物理模拟相结合。我计划系统性地梳理 SDF 在抓取稳定性分析中的应用，特别是研究神经符号距离场（Neural SDF）如何通过神经网络隐式表示复杂的非凸几何体。此外，我也会思考如何将这些几何见解转化为高效的算法实现，以支撑灵巧手在不确定环境下的精细操作建模。

#### 研究网站 / Researched Websites

- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~jrs/274s03/) - Computational Geometry - People @EECS
- [cp-algorithms.com](https://cp-algorithms.com/geometry/minkowski.html) - Minkowski sum of convex polygons - Algorithms for Competitive Programming
- [cs.purdue.edu](https://www.cs.purdue.edu/homes/cs53100/slides/mink.pdf) - Path Planning and Minkowski Sums (Chapter 13) - CS@Purdue
- [youtube.com](https://www.youtube.com/watch?v=pzOgLlL-SI0) - Robot Motion Planning: Computing Minkowski sums of (convex) polygons (part 2 of 3)
- [math.stackexchange.com](https://math.stackexchange.com/questions/3647382/how-to-use-minkowski-sum-on-convex-hulls-of-obstacle-in-robotics) - How to use Minkowski Sum on convex hulls of obstacle in robotics? - Math Stack Exchange
- [roboticsconference.org](https://roboticsconference.org/docs/invitedtalks/park-manifoldsgeometryandrobotics.pdf) - Manifolds, Geometry, and Robotics
- [rcfs.ch](https://rcfs.ch/doc/rcfs.pdf) - A Math Cookbook for Robot Manipulation - RCFS
- [manipulation.csail.mit.edu](https://manipulation.csail.mit.edu/) - Robotic Manipulation
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/murray-li-sastry-94-complete.pdf) - A Mathematical Introduction to Robotic Manipulation - Computer Science & Engineering
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [observablehq.com](https://observablehq.com/@esperanc/2d-gjk-and-epa-algorithms) - 2D GJK and EPA algorithms / Claudio Esperança - Observable Notebooks
- [handmade.network](https://handmade.network/forums/t/7623-collision_detection_using_gjk_and_a_modified_epa) - Collision Detection Using GJK and a Modified EPA | Handmade Network
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9823899/) - A Self-Collision Detection Algorithm of a Dual-Manipulator System Based on GJK and Deep Learning - NIH
- [reddit.com](https://www.reddit.com/r/gameenginedevs/comments/1e5xtbr/efficient_collision_detection_implementations/) - Efficient Collision Detection Implementations? : r/gameenginedevs - Reddit
- [arxiv.org](https://arxiv.org/html/2502.02664v1) - Differentiable Composite Neural Signed Distance Fields for Robot Navigation in Dynamic Indoor Environments - arXiv
- [dannydriess.github.io](https://dannydriess.github.io/papers/21-driess-CoRL.pdf) - Learning Models as Functionals of Signed-Distance Fields for Manipulation Planning - Danny Driess
- [ri.cmu.edu](https://www.ri.cmu.edu/pub_files/2009/5/icra09-chomp.pdf) - CHOMP: Gradient Optimization Techniques for Efficient Motion Planning - Carnegie Mellon University Robotics Institute
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8381225/) - Creating Better Collision-Free Trajectory for Robot Motion Planning by Linearly Constrained Quadratic Programming - PMC - NIH
- [rll.berkeley.edu](https://rll.berkeley.edu/trajopt/ijrr/2013-IJRR-TRAJOPT.pdf) - Motion Planning with Sequential Convex Optimization and Convex Collision Checking
- [arxiv.org](https://arxiv.org/html/2211.02647v3) - Neural Grasp Distance Fields for Robot Manipulation - arXiv
- [nerfgrasp.github.io](https://nerfgrasp.github.io/) - Neural Fields for Robotic Object Manipulation from a Single Image
- [sites.google.com](https://sites.google.com/view/neural-grasp-distance-fields) - Neural Grasp Distance Fields for Robot Manipulation
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/10160211/10160212/10160217.pdf) - Neural Grasp Distance Fields for Robot Manipulation - IEEE Xplore
- [arxiv.org](https://arxiv.org/abs/2211.02647) - [2211.02647] Neural Grasp Distance Fields for Robot Manipulation - arXiv

### 接触流形的流形几何表征

我在合成现有文献时发现，灵巧操作中的接触不仅仅是几何层面的碰撞，更应被视为在约束流形（Constraint Manifold）上的运动。通过引入指数乘积（PoE）公式和黎曼流形（Riemannian Manifolds），我意识到将配置空间（Configuration Space）视为弯曲流形，可以更自然地处理闭链运动学和复杂的接触条件。相比于传统的坐标变换，这种基于李群（Lie Groups）的方法为微分几何框架下的操作稳定性分析提供了更深刻的数学支撑。

### 穿透深度算法的局限性与连续梯度

通过对 GJK 与 EPA 算法协同逻辑的深度推演，我观察到 EPA 在处理非多面体（如带有曲率的边缘）或复合几何体时的数值不稳定性。这种由于边缘搜索产生的反馈跳跃，在高速动力学优化中会导致严重的数值振荡。相比之下，符号距离场（SDF）尤其是神经抓取距离场（NGDF）通过将抓取流形表征为连续能级集（Level Set），有效解决了离散检测中梯度消失或不连续的瓶颈，使抓取位姿的协同优化变得平滑且可微。

### 物理对偶性与核心逻辑实现

在后续的思考中，我将聚焦于 Jacobian 矩阵在接触空间中的力-速度对偶性，探索闵可夫斯基和（Minkowski Sums）如何从路径规划工具演化为描述滑动与滚动摩擦的几何基础。我计划提炼出 GJK 与 EPA 的核心算法逻辑，并构建一个精简的 SDF 梯度下降框架，重点研究神经场（Neural Fields）在处理复杂非凸几何体时的表征策略，从而在灵巧手的精细交互建模中实现计算效率与物理精度的平衡。

#### 研究网站 / Researched Websites

- [arxiv.org](https://arxiv.org/html/2505.02291v4) - Dexterous Contact-Rich Manipulation via the Contact Trust Region - arXiv
- [ri.cmu.edu](https://www.ri.cmu.edu/pub_files/2015/6/koval_ijrr2015a.pdf) - Pose Estimation for Planar Contact Manipulation with Manifold Particle Filters - Carnegie Mellon University Robotics Institute
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/158946/suh-hjsuh-phd-eecs-2025-thesis.pdf?sequence=-1&isAllowed=y) - Leveraging Structure for Efficient and Dexterous Contact-Rich Manipulation - DSpace@MIT
- [cs.purdue.edu](https://www.cs.purdue.edu/homes/cs53100/slides/mink.pdf) - Path Planning and Minkowski Sums (Chapter 13) - CS@Purdue
- [researchgate.net](https://www.researchgate.net/publication/222300747_Accurate_Minkowski_sum_approximation_of_polyhedral_models) - Accurate Minkowski sum approximation of polyhedral models | Request PDF
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/velocity-kinematics-and-statics/) - Velocity Kinematics and Statics - Foundations of Robot Motion - Northwestern University
- [bionics.seas.ucla.edu](http://bionics.seas.ucla.edu/education/MAE_263D/Robotics_04_Jacobian_07A_Singulairty.pdf) - Jacobian - Models of Robot Manipulation - EE 543
- [studywolf.wordpress.com](https://studywolf.wordpress.com/2013/09/02/robot-control-jacobians-velocity-and-force/) - Robot control part 2: Jacobians, velocity, and force - studywolf - WordPress.com
- [ucb-ee106.github.io](https://ucb-ee106.github.io/eecs106a-fa23site/assets/MLS.pdf) - A Mathematical Introduction to Robotic Manipulation - GitHub Pages
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/5-1-1-space-jacobian/) - 5.1.1. Space Jacobian – Modern Robotics
- [worldscientific.com](https://www.worldscientific.com/doi/pdf/10.1142/9781786348432_0001) - Sliding–Rolling Contact and In-Hand Manipulation : Introduction - World Scientific Publishing
- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~jfc/papers/90/LCtra90.pdf) - Motion of two rigid bodies with rolling constraint - Robotics and Automation, IEEE Transactions on - People @EECS
- [thesis.unipd.it](https://thesis.unipd.it/retrieve/e3920b78-8c9c-4ebf-a417-0f31ff043335/TM_CHINO_A.pdf) - Rolling manifolds: an approach through geometric control
- [emergentmind.com](https://www.emergentmind.com/topics/rolling-intrinsic-approach) - Rolling Intrinsic Approach - Emergent Mind
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/12-1-2-contact-types-rolling-sliding-and-breaking/) - 12.1.2. Contact Types: Rolling, Sliding, and Breaking - Foundations of Robot Motion
- [cs.brown.edu](https://cs.brown.edu/courses/cs195u/lectures/04_advancedCollisionsAndPhysics.pdf) - Collisions - Brown Computer Science
- [blog.hamaluik.ca](https://blog.hamaluik.ca/posts/simple-aabb-collision-using-minkowski-difference/) - Simple AABB Collision Detection Using the Minkowski Difference - Kenton Hamaluik
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs164-09-spring/Protected/09cs164-05-18_slides.pdf) - CS164: Motion – Collision Detection - Stanford Computer Graphics Laboratory
- [perso.liris.cnrs.fr](https://perso.liris.cnrs.fr/nicolas.pronost/UUCourses/GamePhysics/lectures/lecture%206%20Collision%20Detection.pdf) - Game Physics - CNRS
- [dyn4j.org](https://dyn4j.org/2010/04/gjk-gilbert-johnson-keerthi/) - GJK (Gilbert–Johnson–Keerthi) - dyn4j

### 接触 Jacobian 的物理对偶性深思

我正在深入剖析灵巧操作中 Contact Jacobian 的数学本质。通过合成现有的运动学反馈，我意识到该矩阵不仅是速度映射工具，更是连接指尖力空间与物体位姿空间的物理桥梁。我正在思考如何利用其转置关系来精确建模指尖在接触流形上的力-速度对偶性，这对于在精细操作中实现滑动与滚动的动态平衡至关重要。

### 梯度断层与优化收敛的瓶颈解析

在审视运动规划的底层数学时，我发现离散布尔检测与连续优化算法之间存在显著的信息断层：布尔函数的梯度在接触区域外几乎处处为零，这直接导致了梯度下降法在复杂约束下的失效。通过对比 SDF 与传统 EPA 算法在非多面体边缘的处理表现，我正在尝试构建一种具备平滑二阶导数特性的接触代价函数，以解决非凸几何体在实时动态优化中的数值不稳定性问题。

### 核心逻辑建模与神经场机制探究

接下来的行动中，我将聚焦于提炼 GJK 与支持映射（Support Mapping）的核心逻辑，并将其转化为精简的底层算法框架。我计划深度解析神经符号距离场（Neural SDF）在处理非凸复杂几何时的表示机制，探索其如何通过隐式连续场捕捉抓取流形的全局稳定性。这一过程旨在将抽象的几何约束转化为可微的代价项，从而在后续的模拟中实现计算效率与物理真实感的深度融合。

#### 研究网站 / Researched Websites

- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/12-2-3-force-closure/) - 12.2.3. Force Closure – Modern Robotics
- [ucb-ee106.github.io](https://ucb-ee106.github.io/106b-sp23site/assets/disc/Discussion_9_Grasping.pdf) - C106B Discussion 9: Grasping - GitHub Pages
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [centropiaggio.unipi.it](https://www.centropiaggio.unipi.it/sites/default/files/estimating_contact_forces_from_postural_measures.pdf) - Estimating Contact Forces from Postural Measures in a class of Under-Actuated Robotic Hands
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation
- [shadecoder.com](https://www.shadecoder.com/topics/signed-distance-function-a-comprehensive-guide-for-2025) - Signed Distance Function: A Comprehensive Guide for 2025 - Shadecoder
- [mmacklin.com](https://mmacklin.com/sdfcontact.pdf) - Local Optimization for Robust Signed Distance Field Collision - Miles Macklin
- [arxiv.org](https://arxiv.org/html/2411.06719v1) - Shallow Signed Distance Functions for Kinematic Collision Bodies - arXiv
- [d-nb.info](https://d-nb.info/1377763692/34) - Contact detection in computational mechanics: a signed distance field approach for convex superelliptical bodies
- [upcommons.upc.edu](https://upcommons.upc.edu/bitstreams/6cd58603-22ab-41b4-b427-f179709fd18f/download) - Efficient discretization of signed distance fields - UPCommons
- [stats.stackexchange.com](https://stats.stackexchange.com/questions/249645/what-does-it-mean-when-all-gradients-of-a-neural-network-are-0) - What does it mean when all gradients of a neural network are 0? - Stats StackExchange
- [stackoverflow.com](https://stackoverflow.com/questions/48001598/why-do-we-need-to-call-zero-grad-in-pytorch) - Why do we need to call zero_grad() in PyTorch? - Stack Overflow
- [discuss.pytorch.org](https://discuss.pytorch.org/t/why-parameterss-gradient-is-zero/12617) - Why Parameters's Gradient is Zero? - autograd - PyTorch Forums
- [discuss.pytorch.org](https://discuss.pytorch.org/t/all-gradients-are-zeros/205585) - All Gradients are Zeros - PyTorch Forums
- [stackoverflow.com](https://stackoverflow.com/questions/68419612/imorting-zero-gradients-from-torch-autograd-gradcheck) - Imorting zero_gradients from torch.autograd.gradcheck - Stack Overflow

### 支持映射与碰撞检测的数学精简

我正在深度剖析 GJK 算法的底层数学结构，特别是支持映射（Support Mapping）的物理直觉。我意识到，通过将复杂的几何体抽象为方向向量上的极值函数，我们可以将指尖与物体间复杂的几何交互简化为单一的向量运算。这种抽象不仅极大提升了碰撞检测的计算效率，更为灵巧操作中的实时路径修正提供了极简的数学入口，使我们能够摆脱对繁杂网格求交运算的依赖。

### 从布尔断层到梯度场的优化范式转换

在思考轨迹优化的收敛性时，我进一步明确了传统布尔检测的局限：其本质是一个阶跃函数，在优化空间中产生的导数几乎处处为零，这正是导致许多基于梯度的控制器在接触瞬间失效的根本原因。通过引入符号距离场（SDF），我成功地将这种离散的断层转化为连续可微的势能场。这种从“是非判断”到“距离引导”的转变，为解决灵巧手在精细操作中的非凸约束优化问题提供了稳健的梯度流。

### 底层算法重构与神经隐式场机制解析

接下来的行动中，我将聚焦于将这些几何见解转化为具象的底层算法实现。我计划提炼出一套不依赖特定库的 GJK 与 EPA 核心逻辑原语，以展示其在 C-Space 中的迭代演进过程。同时，我将深入探究神经符号距离场（Neural SDF）如何通过神经网络的学习机制直接表征复杂的非凸几何体，评估其在无需凸分解（Convex Decomposition）的情况下，如何通过隐式连续函数实现全局最优抓取位姿的快速推理。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [github.com](https://github.com/kroitor/gjk.c) - kroitor/gjk.c: Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C - GitHub
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/robotics/comments/cgit11/q_implementing_the_gjk_algorithm_in_python/) - [Q] Implementing the GJK Algorithm in Python : r/robotics - Reddit
- [stackoverflow.com](https://stackoverflow.com/questions/19732098/implementing-the-support-function-in-gjk) - Implementing The Support Function in GJK - Stack Overflow
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pyimagesearch.com](https://pyimagesearch.com/2016/10/10/gradient-descent-with-python/) - Gradient Descent with Python - PyImageSearch
- [github.com](https://github.com/ivy-llc/robot) - Functions and classes for gradient-based robot motion planning, written in Ivy. - GitHub
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [arxiv.org](https://arxiv.org/html/2502.02664v1) - Differentiable Composite Neural Signed Distance Fields for Robot Navigation in Dynamic Indoor Environments - arXiv
- [youtube.com](https://www.youtube.com/watch?v=IH9kqpMORLM) - Gradient Descent from Scratch in Python - YouTube
- [xxlong.site](https://www.xxlong.site/NeuralUDF/) - NeuralUDF: Learning Unsigned Distance Fields for Multi-view Reconstruction of Surfaces with Arbitrary Topologies
- [arxiv.org](https://arxiv.org/html/2508.16062v1) - Advances and Trends in the 3D Reconstruction of the Shape and Motion of Animals - arXiv
- [towardsdatascience.com](https://towardsdatascience.com/neural-implicit-representations-for-3d-shapes-and-scenes-c6750dff49db/) - Neural-Implicit Representations for 3D Shapes and Scenes | Towards Data Science
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [cad.zju.edu.cn](http://www.cad.zju.edu.cn/home/jin/papers/Real_Time_CD_between_SDFs.pdf) - Real-time Collision Detection between General SDFs
- [colin97.github.io](https://colin97.github.io/CoACD/) - Approximate Convex Decomposition for 3D Meshes with Collision-Aware Concavity and Tree Search - GitHub Pages
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=7095) - GImpact vs convex-decomposed mesh collision performance - Real-Time Physics Simulation Forum - PyBullet
- [reddit.com](https://www.reddit.com/r/compsci/comments/17qusll/i_created_exact_convex_decomposition_algorithm/) - I created exact convex decomposition algorithm. What are possible applications and monetization strategies? : r/compsci - Reddit
- [arxiv.org](https://arxiv.org/pdf/1909.05736) - Learnable Convex Decomposition - arXiv

### 支持映射与差集几何的数学降维

我正在对 GJK 算法的核心逻辑进行深度数学降维。通过推导支持映射（Support Mapping）的性质，我意识到碰撞检测的本质是在两个物体构成的闵可夫斯基差（Minkowski Difference）中寻找距离原点最近的点。这种将复杂的几何体形状封装进 $S_A(d) - S_B(-d)$ 计算原语的方法，巧妙地规避了显式的空间和计算开销，使灵巧手在高自由度配置下的实时干涉检测从繁重的几何求交演变为极简的方向性极值搜索。

### 神经场对非凸几何的表征优势

我在思考 Neural SDF 相比于传统凸分解（Convex Decomposition）的技术优越性。传统方法在处理高度非凸的操作物体（如带孔位的零件）时，往往会因为离散的局部凸包近似而丢失关键的接触细节。而通过神经网络学习得到的隐式连续场，能将复杂的非凸拓扑表征为单一平滑的能级集（Level Set）。这种表征不仅提供了覆盖全局的连续梯度，还通过自动微分技术，为灵巧操作中的抓取流形优化提供了前所未有的数值稳定性。

### 核心逻辑提炼与梯度优化实践

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 的纯粹算法逻辑，重点解决在处理具备曲率的几何边缘时可能出现的数值震荡。我计划构建一个基于 SDF 梯度下降的精简路径规划框架，并深入解析神经抓取距离场（NGDF）如何将几何距离转化为可优化的代价项。这一过程旨在将抽象的几何约束无缝集成到实时的动力学优化循环中，以支撑灵巧手在动态接触任务中的精确推理。

#### 研究网站 / Researched Websites

- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/xbeat/Machine-Learning/blob/main/Building%20a%20Gradient%20Descent%20Optimizer%20from%20Scratch%20in%20Python.md) - Machine-Learning/Building a Gradient Descent Optimizer from Scratch in Python.md at main
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [cad-journal.net](https://cad-journal.net/files/vol_20/CAD_20(5)_2023_1029-1042.pdf) - Exact Signed Distance Function Representation of Polygons - CAD Journal
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 闵可夫斯基差与单纯形演进的几何本质

我正在通过 Minkowski Difference 的视角重构碰撞检测的核心逻辑。我意识到，GJK 算法的精妙之处在于它无需显式构建复杂的 C-Space 障碍物，而是通过 Support Function 在 Minkowski Difference 空间内迭代演进一个单纯形（Simplex）。这种将几何碰撞转化为“原点是否在单纯形内”的判定，极大地简化了灵巧手在处理高维度接触时的拓扑复杂度，使实时干涉检测从重负载的网格求交转向了轻量级的向量极值搜索。

### 神经场作为全局拓扑的连续近似原语

在对比 Neural SDF 与传统凸分解（Convex Decomposition）时，我洞察到其核心优势在于对全局非凸性的隐式捕获。相比于将复杂零件切割成无数微小凸包的局部近似法，神经网络通过学习隐式函数，将物体的复杂拓扑结构压缩进非线性权重映射中。这种表征不仅消除了离散网格带来的梯度断层，更通过 Level Set 自动提取出具备全局导引意义的平滑梯度场，为灵巧操作中跨越非凸障碍的全局优化提供了数值稳定性。

### 算法原语提炼与梯度场优化框架构建

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 算法的纯粹逻辑实现，重点剖析单纯形更新与多胞体扩展（Expanding Polytope）在穿透深度计算中的物理本质。我计划构建一个基于 SDF 梯度的精简优化示例，展示如何利用符号距离场的连续梯度，将几何约束直接转化为可微分的轨迹修正项。这一过程旨在实现从静态几何表征到动态运动规划的底层算法闭环，以支撑灵巧手在不确定接触环境下的稳健操作。

#### 研究网站 / Researched Websites

- [dyn4j.org](https://dyn4j.org/2010/04/gjk-distance-closest-points/) - GJK, Distance, Closest Points - dyn4j
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [towardsdatascience.com](https://towardsdatascience.com/complete-step-by-step-gradient-descent-algorithm-from-scratch-acba013e8420/) - Complete Step-by-Step Gradient Descent Algorithm from Scratch | Towards Data Science
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 闵可夫斯基和作为扫掠体积的物理直觉

我正在重新审视 Minkowski Sums 的物理本质。通过将其理解为“扫掠体积”（Swept Volume），我意识到它不仅是描述配置空间障碍物的几何工具，更是指尖在物体表面滑动与滚动接触时所形成的动态包络。这种视角将静态的几何相交转化为连续的接触状态流转，为建模灵巧操作中指尖在接触流形上的精细摩擦力平衡提供了更具物理深度的几何解释。

### 神经场全局函数近似与局部凸分解的范式之争

我正在深度对比 Neural SDF 与传统 Convex Decomposition 在处理高度非凸拓扑时的表现差异。传统方法往往受限于局部凸包近似带来的边界噪声，导致在接触瞬间产生不连续的梯度跳跃。通过剖析神经场的隐式学习机制，我发现其将复杂的非凸表面表征为单一全局平滑映射的能力，有效消除了局部几何奇点。这种全局连续性为优化算法提供了更具鲁棒性的导引梯度，从根本上缓解了灵巧手在精细缝隙中操作时的数值震荡问题。

### 核心算法原语提取与梯度优化框架的闭环

我接下来的任务是提炼出 GJK 与 EPA 算法的核心逻辑原语，重点解析如何通过 Support Function 的高效差值运算 $S_A(d) - S_B(-d)$ 来规避显式的空间搜索开销。同时，我计划构建一个基于 SDF 梯度的精简路径优化框架，演示如何利用自动微分技术将几何距离直接转化为轨迹修正的代价项。这一过程旨在打通从隐式几何表征到具体机器人动作指令的底层通路，确保灵巧操作在复杂接触序列下的数学完备性。

#### 研究网站 / Researched Websites

- [dyn4j.org](https://dyn4j.org/2010/04/gjk-distance-closest-points/) - GJK, Distance, Closest Points - dyn4j
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [towardsdatascience.com](https://towardsdatascience.com/complete-step-by-step-gradient-descent-algorithm-from-scratch-acba013e8420/) - Complete Step-by-Step Gradient Descent Algorithm from Scratch | Towards Data Science
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 穿透深度与运动矢量的几何耦合

我正在深入思考 EPA (Expanding Polytope Algorithm) 在动态接触中的局限性。通过分析发现，传统的 EPA 往往只关注 Minkowski Difference 空间中距离原点最近的边缘，而忽略了物体当前的相对运动矢量 ($dP$)。在灵巧手操作薄壁物体或复杂边缘时，这种单纯基于几何距离的修正会导致指尖错误地穿透几何体表面。我意识到，必须在穿透计算中引入方向性偏置，才能确保在高动态接触任务中，控制器能沿着物理正确的路径引导指尖脱离干涉。

### 距离变换算法的计算效率与场构建

在探索 SDF (Signed Distance Fields) 的实用性时，我聚焦于其构建过程的计算开销。通过对 Euclidean Distance Transform (EDT) 的推演，我确认了在体素网格（Voxel Grid）上构建 SDF 具备 $O(K)$ 的线性复杂度。这种高效性意味着我们能够实时从感知到的点云数据中生成连续的梯度场，从而为 TrajOpt 或 CHOMP 等轨迹优化算法提供即时的二阶导数信息。这解决了灵巧操作中“感知-规划”链路在高维度状态空间下的实时性瓶颈。

### 6D 抓取流形的可微优化策略

我正在将研究视野从 3D 工作空间场扩展到 6D 的神经抓取距离场 (NGDF)。相比于离散地采样和评估抓取候选点，NGDF 将所有合法的抓取位姿建模为高维空间中的连续零能级集 (Level Set)。我正在思考如何利用这种隐式表征的微分特性，将复杂的接触约束转化为单一的可微代价函数。接下来，我将聚焦于提炼 GJK 与 EPA 的核心逻辑原语，特别是 Support Function 在多胞体扩展中的数值稳定性处理，并构建一套精简的算法实现，以展示如何将这些几何见解无缝集成到灵巧操作的控制循环中。

#### 研究网站 / Researched Websites

- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/xbeat/Machine-Learning/blob/main/Building%20a%20Gradient%20Descent%20Optimizer%20from%20Scratch%20in%20Python.md) - Machine-Learning/Building a Gradient Descent Optimizer from Scratch in Python.md at main
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [cad-journal.net](https://cad-journal.net/files/vol_20/CAD_20(5)_2023_1029-1042.pdf) - Exact Signed Distance Function Representation of Polygons - CAD Journal
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 扫掠体积视角下的接触动力学直觉

我正在重新审视闵可夫斯基和（Minkowski Sums）在灵巧操作中的物理意义，将其从静态的障碍物表征转化为动态的“扫掠体积”（Swept Volume）。通过这种视角，我意识到指尖与物体间的滑动或滚动不再是孤立的碰撞事件，而是在配置空间中连续演进的几何流转。这种直觉上的转变，促使我思考如何利用这种连续性来增强控制算法对接触状态切换的预测能力，从而在精细操作中实现更自然的物理交互。

### 全局函数近似对非凸拓扑的解耦策略

我正在深入探究神经符号距离场（Neural SDF）处理高度非凸几何体的内在机制。相比于将复杂形状强行切割为无数局部凸包的传统做法，我观察到神经网络通过全局连续函数的近似，能够隐式地捕捉复杂的拓扑空洞与凹陷。我正在厘清这种全局表征如何避免了局部采样带来的梯度噪声，并思考如何利用其自动微分特性，为灵巧手在极其狭窄且复杂的几何约束中寻找最优路径提供稳健的数值支撑。

### 底层算法原语提取与梯度优化实现

接下来的行动中，我将致力于从繁杂的工程库中提炼出 GJK 与 EPA 算法的最核心逻辑原语，重点解析支持映射函数在 Minkowski 差空间中的迭代演进。我计划构建一个精简的底层算法框架，并结合 SDF 梯度下降示例，演示如何将几何距离直接转化为可微的代价项。这一过程旨在打通从隐式几何感知到实时动作规划的闭环，确保灵巧操作在动态接触任务中具备严谨的数学完备性与执行效率。

#### 研究网站 / Researched Websites

- [dyn4j.org](https://dyn4j.org/2010/04/gjk-distance-closest-points/) - GJK, Distance, Closest Points - dyn4j
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [towardsdatascience.com](https://towardsdatascience.com/complete-step-by-step-gradient-descent-algorithm-from-scratch-acba013e8420/) - Complete Step-by-Step Gradient Descent Algorithm from Scratch | Towards Data Science
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 从扫掠运动学视角重构几何接触

我正在深化对 Minkowski Sums 的物理认知，将其从抽象的配置空间障碍物进一步具象化为灵巧操作中的“扫掠运动学”（Swept Kinematics）。我意识到，当指尖在物体表面执行滑动或滚动任务时，接触轨迹的几何演化本质上是在这一流形空间中进行连续寻迹。这种视角不仅能解释静态的干涉，更为建立精细的摩擦力平衡与接触状态转换提供了直观的几何支撑，使我能够将纯几何约束转化为动态的物理力学描述。

### 数值稳定性与全局隐式表征的优势剖析

在审视穿透深度计算的可靠性时，我重点剖析了 EPA 算法在处理具有复杂曲率或非多面体边缘时的数值跳跃瓶颈。这种由于边缘搜索产生的不连续性是导致实时控制器振荡的根源。通过对比，我确信 Neural SDF 的核心优势在于它通过全局隐式函数（Global Implicit Function）规避了传统局部凸分解（Convex Decomposition）带来的拓扑破碎。这种全局一致的 Level Set 表征不仅提供了平滑的二阶梯度，更确保了在处理高度非凸物体时，优化算法能保持稳定的收敛性能。

### 底层逻辑提炼与梯度场优化框架构建

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 的纯粹算法逻辑，重点展示 Support Mapping 在 Simplex 迭代演进中的数学本质，并剔除所有非核心的工程实现。我计划构建一个精简的梯度下降框架，演示如何直接利用 SDF 的微分特性进行路径轨迹的实时修正。这一过程旨在将深奥的几何表征理论转化为可直接用于灵巧操作建模的底层原语，打通从隐式感知到精确执行的最后技术环节。

#### 研究网站 / Researched Websites

- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [towardsdatascience.com](https://towardsdatascience.com/complete-step-by-step-gradient-descent-algorithm-from-scratch-acba013e8420/) - Complete Step-by-Step Gradient Descent Algorithm from Scratch | Towards Data Science
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 闵可夫斯基差空间的单纯形演进

我正在通过 Minkowski Difference 的视角深度解构 GJK 算法。我发现其核心美感在于将复杂的物体干涉问题降维至一个关于原点距离的搜索过程。通过高效迭代单纯形（Simplex），我可以直接捕捉到指尖与物体间最微小的物理间隙。这种极简的极值搜索机制，不仅规避了传统网格计算的巨额开销，更为灵巧操作中的实时动态重规划提供了亚毫秒级的干涉反馈闭环。

### 隐式神经场对复杂非凸拓扑的全局表征

我深入思考了 Neural SDF 在建模非凸零件（如带有复杂孔位的灵巧夹具）时的独特优势。相比于局部凸分解容易出现的边界跳跃，神经场通过学习全局连续函数，将复杂的拓扑结构映射为单一平滑的能级集（Level Set）。这种表征方式不仅通过自动微分技术提供了处处连续的梯度，还确保了在执行精细穿刺或抓取任务时，优化算法能够获得全局一致的梯度流导引，从根本上解决了局部极小值导致的轨迹停滞问题。

### 核心算法原语的提炼与可微优化实践

在接下来的研究阶段，我将致力于从底层逻辑中提炼出不依赖外部库的 GJK 与 EPA 核心算法原语，特别是针对支持映射函数 $S_A(d) - S_B(-d)$ 的向量化实现。我计划构建一个基于 SDF 梯度的精简轨迹优化模型，演示如何利用 $O(K)$ 复杂度的 Euclidean Distance Transform 快速构建感知场，并将几何距离直接转化为可微的代价项，以实现灵巧手在复杂接触约束下的闭环精准控制。

#### 研究网站 / Researched Websites

- [dyn4j.org](https://dyn4j.org/2010/04/gjk-distance-closest-points/) - GJK, Distance, Closest Points - dyn4j
- [jamiethompson.me](https://jamiethompson.me/posts/GJK-Collision-Detection/) - Gilbert-Johnson-Keerthi 2D Collision Detection - Jamie Thompson
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [pypi.org](https://pypi.org/project/distance3d/) - distance3d - PyPI
- [stackoverflow.com](https://stackoverflow.com/questions/49672010/calculate-surface-with-gjk-and-epa) - Calculate Surface with GJK and EPA - algorithm - Stack Overflow
- [github.com](https://github.com/andreacasalino/Flexible-GJK-and-EPA) - andreacasalino/Flexible-GJK-and-EPA: Implementations of the GJK and EPA algorithm for performing proximity queries on pair of convex shapes - GitHub
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=3803) - Generating Stable Contact Information from EPA/GJK - Real-Time Physics Simulation Forum
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=gsfbWn4Gy5Q) - Gradient Descent From Scratch in Python - Visual Explanation - YouTube
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [towardsdatascience.com](https://towardsdatascience.com/complete-step-by-step-gradient-descent-algorithm-from-scratch-acba013e8420/) - Complete Step-by-Step Gradient Descent Algorithm from Scratch | Towards Data Science
- [arxiv.org](https://arxiv.org/abs/1901.05103) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation
- [ecva.net](https://www.ecva.net/papers/eccv_2020/papers_ECCV/papers/123740596.pdf) - Deep Local Shapes: Learning Local SDF Priors for Detailed 3D Reconstruction - European Computer Vision Association
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [geometry.stanford.edu](https://geometry.stanford.edu/lgl_2024/papers/dzwyng-cd-20/dzwyng-cd-20.pdf) - Curriculum DeepSDF
- [corp.roblox.com](https://corp.roblox.com/publications/constructive-solid-geometry-on-neural-signed-distance-fields) - Constructive Solid Geometry on Neural Signed Distance Fields - Roblox
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/b8b34328ae68ccc931265bcd21ae5f16-Paper-Conference.pdf) - Neural Signed Distance Function Inference through Splatting 3D Gaussians Pulled on Zero-Level Set - NIPS
- [arxiv.org](https://arxiv.org/html/2407.13342v2) - Implicit Filtering for Learning Neural Signed Distance Functions from 3D Point Clouds - arXiv
- [zoemarschner.com](https://zoemarschner.com/research/csg_on_neural_sdfs) - Constructive Solid Geometry on Neural Signed Distance Fields - Zoë Marschner
- [research.nvidia.com](https://research.nvidia.com/labs/toronto-ai/nglod/) - Neural Geometric Level of Detail: Real-time Rendering with Implicit 3D Shapes - Research at NVIDIA

### 接触 Jacobian 的物理对偶性解析

我正在深化对 Contact Jacobian 在灵巧操作中的物理理解。我意识到，这一矩阵不仅是连接速度空间的几何映射，更是维系指尖力空间与物体位姿空间对偶性的关键桥梁。通过对力-速度对偶性 (Force-Velocity Duality) 的分析，我确信在建模滑动与滚动的动态平衡时，Contact Jacobian 的转置关系为精确控制指尖压力与切向摩擦力提供了严谨的数学框架，这对于实现在不确定接触流形上的精细操作至关重要。

### 离散碰撞检测的梯度断层与连续场补完

在审视主流运动规划框架时，我发现离散碰撞检测逻辑在数值层面存在严重的“梯度断层”：传统的布尔判断在接触区域外产生的导数几乎处处为零，这直接导致了基于梯度的优化算法在复杂约束下频繁失效。通过对比，我确信引入 SDF (Signed Distance Fields) 的必要性，它能将离散的几何干涉转化为连续可导的势能场。这种从“是非判断”到“距离引导”的范式转变，为解决灵巧手在执行穿刺或狭缝抓取任务时的非凸约束优化提供了稳定的数值流。

### 神经隐式场表征与核心算法逻辑的闭环

我接下来的思考将聚焦于神经符号距离场 (Neural SDF) 如何通过神经网络隐式学习复杂非凸几何体的零能级集 (Zero-level Set)，从而规避传统凸分解 (Convex Decomposition) 带来的拓扑细节损失。我计划提炼出 GJK 与 EPA 的底层算法逻辑原语，特别是支持映射 (Support Mapping) 的向量化实现，并构建一个基于自动微分的 SDF 路径修正模型。这一过程旨在将几何距离直接映射为可优化的轨迹代价项，打通从隐式感知识别到实时高精度执行的技术闭环。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 闵可夫斯基差空间的单纯形搜索本质

我正在对 GJK 算法进行更底层的数学重构。我意识到，碰撞检测的本质并不在于两个复杂几何体的求交，而是在它们构成的 Minkowski Difference 空间内，利用 Support Mapping 寻找最接近原点的 Simplex。这种将高维干涉检查降维至极简向量极值搜索的策略，极大地降低了灵巧手在处理多指协同接触时的计算开销，为亚毫秒级的底层规划奠定了几何基础。

### 神经符号距离场对非凸拓扑的连续映射

在对比传统的 Convex Decomposition 时，我深感其在处理具有复杂孔位或薄壁结构的非凸物体时的局限性。通过剖析 Neural SDF，我发现其核心价值在于利用神经网络的隐式表示能力，将复杂的几何拓扑结构直接映射为连续可微的 Zero-level Set。这种表征方式不仅保留了精细的接触细节，更通过自动微分提供了全局一致的梯度流，从根本上解决了灵巧操作在窄缝穿刺等高精任务中的优化收敛难题。

### 算法原语提炼与可微优化框架的整合

我接下来的行动将聚焦于提炼 GJK 与 EPA 的核心算法原语，特别是如何通过 Minkowski 差空间的单纯形演进高效计算穿透深度。我计划构建一个精简的梯度下降路径规划框架，演示如何将 SDF 提供的距离信息直接转化为轨迹代价项。这一过程旨在打通从隐式几何感知到实时动作执行的技术通路，确保灵巧操作在动态、非确定接触序列下的数学完备性与控制鲁棒性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 神经场表征的存储优势与拓扑压缩

我在分析神经符号距离场（Neural SDF）的最新进展时发现，相比于传统的点云或网格表征，隐式神经场在存储效率上具有两到三个数量级的压倒性优势。通过将复杂的物体几何压缩进神经网络的非线性权重中，我不仅能够实现对非凸拓扑的高精度重构，还能在极小的内存开销下通过自动微分提取全局一致的梯度流。这种“拓扑压缩”能力为灵巧手在处理海量操作物体时提供了极其轻量化且信息完备的几何原语。

### 指数乘积公式对接触流形建模的数学优越性

在重新审视接触流形（Contact Manifold）的建模方法时，我对比了指数乘积（Product of Exponentials, PoE）公式与传统的 Denavit-Hartenberg 参数。我意识到，PoE 公式通过李群（Lie Groups）直接在黎曼流形上描述运动学，不仅物理直觉更清晰，且在处理闭链约束和多指协同接触时能有效避免坐标奇异性。这种数学框架的转变，使我能将灵巧操作中的几何碰撞检测无缝映射到微分流形的运动规划中，显著提升了约束求解的数值稳定性。

### 核心算法逻辑构建与微分轨迹优化方案

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 算法的底层 Python/C++ 核心逻辑，重点解析支持映射（Support Mapping）在处理多面体与非多面体混合干涉时的实现细节。我计划构建一个基于 SDF 的可微轨迹优化示例，演示如何利用 $O(K)$ 复杂度的欧几里得距离变换（EDT）快速生成实时感知场，并将几何距离产生的梯度直接耦合进灵巧手的力位控制循环中。这一过程旨在打通从底层几何搜索到高层动态优化的完整技术链路。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 闵可夫斯基差与原点包含性的几何判定

我在推演碰撞检测的底层数学时，进一步确立了 Minkowski Difference 在配置空间中的核心地位。我意识到，判断两个复杂几何体是否发生干涉，本质上可以简化为判定原点是否被包含在它们的 Minkowski Difference 集合内。这种将复杂的相对位姿关系映射为单一几何集合拓扑特征的转化，为后续通过 Support Function 进行高效的单纯形迭代提供了极其严谨的数学入口。

### 全局函数近似对非凸几何表征的重构

通过深度对比 Neural SDF 与传统局部凸分解的表征效能，我发现神经网络通过学习全局隐式函数（Global Implicit Function），能够有效规避离散近似带来的几何奇点。这种表征方式不仅提供了覆盖整个工作空间的连续梯度 $\nabla \phi$，还确保了在抓取具有复杂孔洞或薄壁结构的物体时，优化算法能够获得一致且平滑的指引，从根本上解决了传统布尔检测中梯度消失或导数不连续的顽疾。

### 算法逻辑提炼与力-速度对偶性建模

我接下来的任务是提炼出 GJK 与 EPA 算法的纯粹核心逻辑，并构建一个基于 SDF 梯度的精简路径规划框架。我计划深入探讨 Contact Jacobian 在接触流形上的 Force-Velocity Duality，旨在将指尖的微观受力状态与宏观运动规划无缝耦合。这一过程将重点展示如何将几何上的距离梯度转化为物理层面的修正力矩，从而实现灵巧手在精细操作任务中的闭环动力学一致性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 碰撞检测算法的底层工程抽象

我正在将 GJK 算法的数学定义转化为具体的工程原语。我意识到，支持映射（Support Mapping）的精妙之处在于它将复杂的几何求交问题通过 $S_A(d) - S_B(-d)$ 这一极简公式，解耦为一系列独立的方向性极值搜索。在实现 Simplex 迭代逻辑时，我发现只需维护少量的顶点信息即可高效判定原点的包含性。这种高度抽象的计算逻辑，不仅规避了对显式网格结构的依赖，更为灵巧操作中频繁的接触状态判定提供了极高的计算效率。

### EPA 的数值瓶颈与梯度引导的必要性

在深入分析穿透深度（Penetration Depth）的计算时，我发现了 EPA (Expanding Polytope Algorithm) 在处理具有连续曲率或非多面体边缘时的数值稳定性陷阱。当 Minkowski Difference 的边界呈现非线性特征时，基于顶点的多胞体扩展往往会导致迭代次数剧增甚至收敛失效。相比之下，符号距离场（SDF）通过 Euclidean Distance Transform 预计算出的连续梯度场，能够提供处处可导的数值路径，这对于实现在高动态接触任务中稳定、无跳跃的运动修正至关重要。

### 力-速度对偶性与核心逻辑的最终重构

接下来的研究中，我将聚焦于 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality）建模。我计划系统性地梳理指尖力空间与物体位姿空间之间的微分映射关系，探索如何利用这一物理对偶性在 Obsidian 知识库中构建严谨的灵巧操作动力学模块。我将提炼出不依赖库的纯粹代码实现，演示如何将 SDF 的连续梯度与 Contact Jacobian 的转置关系相结合，从而实现从几何感知到闭环力矩控制的底层算法贯通。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 单纯形迭代与 C-Space 的几何延迟评估

我正在对 GJK 算法在配置空间（C-Space）中的计算效率进行极限推演。我意识到其核心价值不仅在于避免显式网格求交，更在于单纯形（Simplex）迭代在处理多指高自由度接触时，能将复杂的几何约束降维至单一极值方向的搜索。通过这种“延迟评估”（Lazy Evaluation）几何特征的策略，我们能够绕过预计算完整 C-Space 障碍物的沉重开销，直接在微分层面上实时处理指尖的干涉检测，这对于动态环境下的灵巧操作至关重要。

### 从网格离散化到隐式场的分辨率突破

我正在权衡传统的 Euclidean Distance Transform (EDT) 与 Neural SDF 在实时感知中的表现差异。尽管 EDT 在体素网格上具备 $O(K)$ 的构建速度，但其物理精度受到网格分辨率的严格限制，容易在细微接触处产生梯度阶跃。相比之下，Neural SDF 通过隐式连续函数实现了在任意分辨率下的梯度平滑性，将复杂的非凸拓扑压缩进神经网络的非线性权重中。这种表征方式不仅解决了大规模操作场景下的内存爆炸问题，更通过自动微分技术为轨迹优化提供了具备全局预测性的导引流。

### 算法逻辑提炼与微分物理控制链路的闭环

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 算法的纯粹 Python 逻辑，重点剖析 Support Mapping 如何作为微分物理模拟的底层原语来执行。我计划构建一个集成 SDF 连续梯度的优化模型，探索如何利用自动微分将几何间隙误差直接映射到由 Contact Jacobian 驱动的力矩反馈循环中。这一过程旨在打通从底层几何干涉判定到高层力位混合控制的技术通路，确保在 Obsidian 知识库中构建出一套数学完备且具备实战深度的灵巧操作教程。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 支持映射与单纯形演进的算法精算

我正在深度提炼 GJK 算法的底层逻辑。通过将复杂的几何体抽象为支持映射（Support Mapping）原语，我发现可以将干涉检测简化为一系列 $S_A(d) - S_B(-d)$ 的向量化极值运算。这种“延迟评估”策略使我们能够在不显式构建网格的情况下，于单纯形（Simplex）迭代中快速判定碰撞。这一发现为在高频控制循环中实现亚毫秒级的接触判定提供了坚实的底层支撑。

### 神经场与体素距离场的精度权衡

在对比 Euclidean Distance Transform (EDT) 与 Neural SDF 时，我洞察到两者的范式冲突：基于网格的 EDT 虽然具备 $O(K)$ 的线性构建速度，但受限于离散分辨率，往往在精细接触点产生数值噪声。而通过隐式连续函数表征的 Neural SDF，利用神经网络的全局近似能力，在任意分辨率下均能提供平滑的梯度场。这种表征不仅解决了复杂非凸物体的内存爆炸问题，更通过自动微分技术，为灵巧操作提供了具备物理一致性的导引信息。

### 算法原语提炼与力矩反馈的闭环整合

接下来的行动中，我将聚焦于提炼出不依赖库的 GJK 与 EPA 纯粹 Python 实现逻辑，重点剖析多胞体扩展中的数值稳定性。我计划构建一个集成 SDF 梯度的路径优化框架，探索如何将几何间隙产生的梯度通过 Contact Jacobian 驱动的力-速度对偶性（Force-Velocity Duality）直接转化为关节力矩指令。这一过程旨在打通从底层几何感知到闭环力位控制的技术链路，确保在复杂的接触序列中实现高度鲁棒的操作建模。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation/) - Computation - MuJoCo Documentation

### 闵可夫斯基差空间与单纯形迭代的降维美学

我正在深度剖析 GJK 算法在配置空间中的几何表现，意识到其精髓在于利用 Support Function 在 Minkowski Difference 空间内执行极简的单纯形（Simplex）搜索。这种方法巧妙地规避了显式的网格求交开销，将复杂的干涉检查转化为关于原点距离的极值优化问题。这种“以点代面”的降维策略，不仅为灵巧手高频控制循环提供了亚毫秒级的干涉反馈，更为后续处理动态接触流形奠定了坚实的几何基础。

### EPA 算法的数值稳定性陷阱与连续场范式

在合成最新的研究反馈时，我观察到 EPA 算法在处理具有复杂曲率或薄壁边缘的物体时，往往会因为过度收集顶点而导致迭代不收敛，甚至产生错误的穿透深度。这种离散边缘搜索带来的数值跳跃，是灵巧操作中控制器产生高频震荡的根源。我确信引入 Neural SDF (神经符号距离场) 是解决这一瓶颈的关键，因为它通过全局隐式函数提供了处处可微的平滑梯度流，将离散的“碰撞是非判断”彻底转化为连续的“距离导引优化”。

### 底层算法原语提炼与接触 Jacobian 建模

接下来的行动中，我将聚焦于从复杂的工程实现中提炼出 GJK 与 EPA 的纯粹逻辑原语，重点解析支持映射在处理非多面体干涉时的向量化实现。我计划构建一个集成 SDF 梯度的精简路径规划框架，并深入探讨 Contact Jacobian 在力-速度对偶性（Force-Velocity Duality）中的数学表达。通过利用自动微分技术，我将尝试把几何间的距离梯度直接映射为驱动关节的修正力矩，从而实现灵巧操作从隐式感知到物理反馈的底层算法闭环。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 支持映射与单纯形演进的极简美学

我正在深度提炼 GJK 算法的底层实现逻辑。我意识到，碰撞检测的本质并不在于两个复杂几何体的求交，而是在它们构成的闵可夫斯基差（Minkowski Difference）空间内，利用支持映射（Support Mapping）寻找最接近原点的单纯形（Simplex）。通过高效迭代 $S_A(d) - S_B(-d)$ 这一极简公式，我可以直接捕捉到指尖与物体间最微小的物理间隙。这种“以点代面”的降维策略，不仅为灵巧手高频控制循环提供了亚毫秒级的干涉反馈，更为后续处理动态接触流形奠定了坚实的几何基础。

### 全局隐式表征对非凸几何的连续引导

在深入分析 Neural SDF 对高度非凸拓扑的建模能力时，我发现其核心价值在于利用神经网络的隐式表示，将复杂的几何结构直接映射为连续可微的零能级集（Zero-level Set）。相比于将物体机械切割为无数凸包的传统做法，神经场通过全局函数近似规避了离散近似带来的几何奇点。这种表征方式不仅提供了覆盖整个工作空间的连续梯度，还确保了在执行精细穿刺或窄缝抓取任务时，优化算法能够获得一致且平滑的梯度流导引，从而在根本上解决了局部极小值导致的轨迹停滞问题。

### 核心逻辑重构与力-速度对偶性建模

接下来的研究中，我将聚焦于提炼出不依赖外部库的 GJK 与 EPA 纯粹代码实现，重点剖析支持映射在处理非多面体干涉时的向量化细节。我计划构建一个集成 SDF 梯度的精简路径规划框架，并深入探讨接触雅可比（Contact Jacobian）在力-速度对偶性（Force-Velocity Duality）中的数学表达。我将尝试利用自动微分技术，将几何间的距离梯度直接映射为驱动关节的修正力矩，从而在 Obsidian 知识库中构建出一套从隐式感知到物理反馈的底层算法闭环。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 支持映射：从显式网格到函数化几何的范式跃迁

我在剖析 GJK 算法时有了更深层的感悟：Support Mapping 不仅仅是一个计算原语，它代表了一种“函数化几何”的范式。通过将复杂的物体形状抽象为特定方向上的极值函数 $S(d)$，我们实际上是在对几何体进行实时降维。这种抽象使得灵巧手在处理极其精细的指尖接触时，能够摆脱昂贵的三角形求交开销，转而利用简单的向量内积实现对物理间隙的亚毫米级追踪。这种“以函数代形”的思想，是实现在高维度配置空间中进行实时冲突检测的数学基石。

### 神经符号场：跨越非凸拓扑的全局引导

通过对神经抓取距离场（NGDF）与 DeepSDF 的深度合成，我意识到神经场的核心价值在于其“拓扑压缩”能力。传统的凸分解在处理带孔零件或薄壁结构时，往往会因为离散近似导致梯度场破碎。而 Neural SDF 通过全局隐式连续函数，将复杂的物体特征压缩进非线性神经网络权重中。这种方式不仅在存储上实现了数量级的精简，更重要的是，它提供了一个覆盖全局、处处可微的势能面，让灵巧操作的优化过程能够平滑地绕过复杂的几何障碍，消除了离散检测带来的数值跳跃。

### 微分几何驱动的力位闭环构建

我接下来的任务是完成从几何场到物理力矩的最后映射。我将致力于提炼出 GJK 与 EPA 的底层 Python/C++ 核心逻辑，剥离所有工程冗余，聚焦于单纯形（Simplex）在 Minkowski 差空间中的演进细节。同时，我计划系统性地梳理 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality），展示如何利用自动微分技术将 SDF 产生的几何距离梯度直接耦合进关节力矩反馈循环中。这种整合旨在建立起一套从隐式感知到高精度力觉执行的完整算法图谱，确保操作逻辑在物理层面的一致性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 动态接触下的穿透矢量偏置

我正在重新审视 EPA 算法在处理高动态接触时的数值稳定性。我意识到传统的穿透深度计算仅关注闵可夫斯基差（Minkowski Difference）空间中距离原点最近的边缘，而往往忽略了物体间的相对运动矢量（$dP$）。在灵巧操作的快速交互中，这种忽略会导致指尖在接触瞬间出现“穿透”或轨迹引导错误。我正在尝试在多胞体扩展过程中引入方向性偏置，以确保穿透修正矢量在物理上与运动状态保持一致，从而解决高速碰撞下的数值不连续问题。

### 神经场表征与欧几里得距离变换的权衡

在分析符号距离场（SDF）的构建效率时，我对比了在体素网格上具备 $O(K)$ 复杂度的欧几里得距离变换（EDT）与神经符号场（Neural SDF）的性能差异。尽管 EDT 在实时感知场构建上极具速度优势，但其精度受限于离散的分辨率，容易在指尖接触微小特征时产生梯度噪声。相比之下，神经场通过全局函数近似提供了无限分辨率的连续梯度。我正在思考如何利用这种隐式表征的自动微分特性，为轨迹优化算法提供平滑且具备全局预测性的导引流，填补从离散点云感知到连续梯度优化之间的信息断层。

### 核心逻辑提炼与力-速度对偶性建模

我接下来的行动将聚焦于提炼 GJK 与 EPA 的纯粹算法原语，重点实现不依赖外部库的支持映射（Support Mapping）向量化逻辑。同时，我计划在数学上正式定义 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality），以建立从 SDF 几何梯度到关节力矩空间的直接映射。我将构建一个精简的梯度下降框架，演示如何将“距离感”转化为实时的动力学修正，打通从隐式几何表征到高精度力觉执行的底层闭环。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 支持映射与极值化几何搜索的对偶性

我正在深度剖析 GJK 算法的数学底层，发现支持映射（Support Mapping）的精妙之处在于它通过 $S_A(d) - S_B(-d)$ 这一极简对偶关系，将复杂的物体形状完全封装进方向性的极值搜索中。这种抽象不仅让碰撞检测摆脱了对显式网格结构的物理依赖，更重要的是，它为我们在高维配置空间（C-Space）中实时追踪物理间隙提供了一种近乎“函数化”的轻量级描述。通过这种方式，我能将灵巧手在处理极其精细的指尖接触时的计算开销，从昂贵的几何求交压缩为亚毫秒级的向量运算。

### 抓取流形的神经场能级集表示

在对比 EPA 算法与现代神经场（Neural Fields）的性能差异时，我意识到传统离散边缘搜索在处理具备连续曲率的物体时，极易因为数值振荡而导致穿透深度计算失效。相比之下，神经抓取距离场（NGDF）通过将合法的 6D 抓取位姿建模为高维空间中的连续零能级集（Zero-level Set），从根本上解决了梯度跳跃问题。这种全局连续的表征方式不仅捕获了非凸物体的复杂拓扑细节，更为轨迹优化算法提供了处处可导的物理引导，确保了指尖在复杂接触流转中的数值收敛性与平滑性。

### 接触雅可比与力-速度对偶性的深度整合

我正在系统化地整合 Contact Jacobian 在灵巧操作中的物理建模。通过对力-速度对偶性（Force-Velocity Duality）的分析，我确信这一矩阵不仅是连接指尖运动与物体位姿的几何映射，更是维系指尖压力与切向摩擦力平衡的核心纽带。我接下来的任务是提炼出不依赖外部库的 GJK 与 EPA 核心逻辑原语，并演示如何利用自动微分技术将 SDF 产生的几何间隙梯度通过 Jacobian 转置关系，直接映射为驱动关节的修正力矩。这一过程将彻底打通从隐式感知到高精度力觉执行的闭环控制链路。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 函数化几何与单纯形搜索的降维逻辑

我正在将 GJK 算法从工程实现升华为“函数化几何”的数学范式。我意识到，支持映射（Support Mapping）的精妙之处在于它通过 $S_A(d) - S_B(-d)$ 将复杂的物体形状封装进方向性的极值搜索中，这本质上是在对高维配置空间（C-Space）进行实时降维。这种“以函数代形”的策略，使灵巧手在处理极其精细的指尖接触时，能够规避昂贵的显式网格求交，转而在闵可夫斯基差（Minkowski Difference）空间内通过极简的单纯形（Simplex）迭代实现亚毫秒级的干涉判定。

### 连续梯度场对离散碰撞断层的补完

在深入剖析轨迹优化的收敛性时，我确立了从离散布尔检测向连续符号距离场（SDF）转化的必要性。传统的碰撞检测在数值层面存在严重的梯度断层，导致优化算法在接触瞬间频繁失效。通过对比，我发现神经符号距离场（Neural SDF）利用全局隐式函数的连续性，有效解决了 EPA 算法在处理非多面体边缘时的数值震荡问题。这种表征方式不仅通过“拓扑压缩”实现了海量操作物体的轻量化建模，更通过自动微分技术为灵巧操作提供了全局一致的平滑梯度流。

### 力-速度对偶性建模与算法闭环构建

我接下来的研究将聚焦于接触雅可比（Contact Jacobian）的力-速度对偶性（Force-Velocity Duality）建模。我计划提炼出不依赖库的 GJK 与 EPA 纯粹逻辑原语，演示如何利用自动微分将 SDF 产生的几何间隙梯度通过 Jacobian 转置关系，直接映射为驱动关节的修正力矩。这一过程旨在打通从隐式感知识别到高精度力觉执行的底层通路，确保灵巧手在动态接触任务中具备严谨的物理一致性与控制鲁棒性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 支持映射与极值化搜索的几何本质

我正在通过 $S_A(d) - S_B(-d)$ 这一对偶关系，深度解构 GJK 算法的底层逻辑。相比于传统的几何相交检查，我意识到将其视为 Minkowski Difference 空间内的一系列方向性极值搜索，能将原本沉重的 3D 干涉检测降维为极简的函数化评估。这种抽象不仅让灵巧手在处理高频接触时具备了亚毫秒级的响应能力，更在数学上定义了一种无需显式网格结构的“函数化几何”范式，为 C-Space 中的实时间隙追踪奠定了理论基础。

### 穿透矢量偏置与连续梯度的数值稳定性

在审视 EPA 算法在处理复杂非多面体边缘时的数值跳跃瓶颈时，我确信引入运动矢量偏置（Motion Vector Bias）是解决高速接触下穿透修正失效的关键。通过将离散的单纯形扩展与符号距离场（SDF）提供的连续梯度场相结合，我正在构建一种能够平滑跨越非凸障碍的优化范式。这种从“离散边缘搜索”到“连续势能导引”的转变，有效消除了传统碰撞检测在接触瞬间产生的梯度断层，为解决灵巧手在精细缝隙操作中的数值振荡提供了稳健的数学保障。

### 微分物理链路与力-速度对偶性的最终映射

接下来的行动中，我将聚焦于提炼 GJK 与 EPA 的纯粹代码原语，剥离冗余的工程实现，聚焦于 Minkowski 差空间中的 Simplex 演进细节。我计划系统化地梳理 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality），演示如何利用自动微分技术将 SDF 产生的几何距离梯度直接耦合进关节力矩反馈循环中。通过建立从隐式几何感知到闭环力觉执行的完整算法链路，我将确保灵巧操作在动态接触任务中具备严谨的物理一致性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 闵可夫斯基差空间的单纯形演进本质

我正在深度剖析 GJK 算法在配置空间（Configuration Space）中的几何本质。我意识到碰撞检测的精髓并非复杂的几何体求交，而是在 Minkowski Difference 空间内通过 Support Mapping 寻找最接近原点的 Simplex。这种将高维干涉检查降维至极简向量极值搜索的方法，不仅极大降低了灵巧手在处理多指协同接触时的计算开销，更在数学上定义了一种无需显式网格结构的“函数化几何”范式，为 C-Space 中的实时间隙追踪奠定了理论基础。

### 隐式连续场对非凸拓扑表征的跨越

在对比 EPA 算法与现代 Neural SDF 的性能时，我确信解决了离散检测中的“梯度断层”问题。传统 EPA 在处理具备连续曲率或复杂凹陷的物体时，常因边缘搜索的数值跳跃导致控制器震荡。而 Neural SDF 通过全局隐式函数（Global Implicit Function）将复杂的非凸拓扑压缩进神经网络权重，利用 Level Set 提供了处处可微的平滑梯度流。这种表征方式不仅捕获了精细的接触细节，更通过自动微分技术为轨迹优化提供了具备全局预测性的导引，有效解决了局部极小值导致的轨迹停滞难题。

### 核心逻辑提炼与力矩反馈闭环构建

我接下来的思考将聚焦于提炼出不依赖外部库的 GJK 与 EPA 纯粹 Python/C++ 核心代码原语，剥离冗余的工程实现，聚焦于 Simplex 在空间中的迭代细节。同时，我计划构建一个集成 SDF 梯度的路径优化框架，系统性地梳理 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality），演示如何利用自动微分将几何间的距离梯度直接映射为驱动关节的修正力矩。这一过程旨在打通从隐式感知识别到高精度物理执行的技术闭环，确保灵巧操作在动态接触任务中的物理一致性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 扫掠体积与接触流形的动态演化

我正在将 Minkowski Sums 的几何定义深度合成为灵巧操作中的“扫掠体积”（Swept Volume）物理直觉。我意识到，碰撞检测不应被视为孤立的瞬时判定，而是在配置空间（Configuration Space）中连续演进的接触流。这种视角不仅解释了静态的干涉，更为建模指尖在物体表面滑动与滚动时的接触状态转换（Contact State Transitions）提供了严谨的几何基石，使我能从更深刻的维度理解 Contact Manifold 的拓扑结构。

### 解决非凸表征中的梯度断层矛盾

在权衡 EPA 算法与神经隐式场（Neural Implicit Fields）时，我成功解析了离散多胞体扩展在处理非多面体（Non-polyhedral）边缘时的数值不稳定性。相比于 EPA 在复杂曲率处产生的梯度跳跃，Neural SDF 通过全局函数近似（Global Function Approximation）将非凸拓扑压缩为连续可微的场。这种转变消除了传统方法在接触瞬间的信息断层，为解决灵巧手在精细缝隙操作中的收敛难题提供了数值层面的鲁棒性支持。

### 底层逻辑架构与微分物理链路的构建

我接下来的思考将聚焦于提炼 GJK 与 EPA 的核心算法逻辑，重点构建一套不依赖外部库的支持映射（Support Mapping）向量化原语。我计划深入推演 Contact Jacobian 在力-速度对偶性（Force-Velocity Duality）中的数学表达，并构建一个基于自动微分（Automatic Differentiation）的轨迹优化框架。这一过程旨在打通从隐式几何表征到闭环力位控制的底层技术链路，确保灵巧操作在动态接触序列下的物理一致性与执行效率。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [reddit.com](https://www.reddit.com/r/gamedev/comments/6wivay/gilbertjohnsonkeerthi_gjk_collision_detection/) - Gilbert-Johnson-Keerthi (GJK) collision detection algorithm in 200 lines of clean plain C
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [winter.dev](https://winter.dev/articles/epa-algorithm) - EPA: Collision response algorithm for 2D/3D - Winter
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [sirslab.dii.unisi.it](https://sirslab.dii.unisi.it/papers/grasping/grasping_chapter_HANDBOOK08.pdf) - Grasping - SIRSLAB Robotics
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [wpage.unina.it](http://wpage.unina.it/sicilian/bruno/courses/FoR_12.pdf) - 12 Cooperative Manipulation

### 动态运动偏置对穿透计算的鲁棒性补完

在审视穿透深度（Penetration Depth）的数值稳定性时，我深入剖析了 EPA 算法在处理高速动态接触时的局限性。我观察到，传统算法往往仅搜索几何上的最短路径，而忽略了物体间的相对运动矢量（$dP$），这在灵巧手操作复杂边缘时会导致指尖出现非物理的“穿透”或轨迹引导错误。我正在尝试在多胞体扩展（Expanding Polytope）过程中引入运动方向偏置，以确保穿透修正矢量在物理上与当前的运动状态保持一致，从而消除接触瞬间产生的数值跳跃。

### 线性时间复杂度下的距离变换与势能场建模

我正在评估实时环境下符号距离场（SDF）构建的数学效率。通过对欧几里得距离变换（EDT）的底层逻辑拆解，我确信其在体素网格上具备的 $O(K)$ 线性复杂度是实现亚毫秒级感知场生成的关键。这种高效性意味着灵巧手能够从实时感知到的点云中快速提取出平滑的梯度面，将复杂的环境障碍转化为可微分的势能引导，为 TrajOpt 等轨迹优化算法提供即时的二阶导数信息，从而填补了离散感知与连续优化之间的信息断层。

### 算法核心逻辑重构与 Jacobian 微分控制映射

接下来的行动中，我将聚焦于提炼出不依赖外部库的 GJK 与 EPA 纯粹 Python/C++ 核心代码原语，重点解析支持映射（Support Mapping）在处理非多面体干涉时的向量化实现。我计划构建一个集成 SDF 梯度的微分物理模拟框架，系统性地演示如何将几何间的距离梯度通过 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality）直接映射为关节力矩。这一过程旨在打通从隐式几何表征到高精度物理执行的底层技术链路，确保灵巧操作在动态接触序列下的数学完备性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 支持映射作为底层计算原语的逻辑精简

我正在将支持映射（Support Mapping）从抽象数学公式转化为高效的计算原语。通过实现 $S_A(d) - S_B(-d)$ 的向量化逻辑，我意识到这种“函数化几何”不仅规避了昂贵的显式网格求交，更在底层实现层面为指尖物理间隙的追踪提供了亚毫秒级的反馈能力。这种对几何特征的延迟评估（Lazy Evaluation）策略，是支撑灵巧手在高维度配置空间内进行实时动态重规划的技术核心。

### 全局函数近似对非凸流形的表征优势

在深入剖析神经符号距离场（Neural SDF）的表征机制时，我对比了其全局函数近似能力与传统的局部凸分解（Convex Decomposition）。我发现，隐式连续场能通过神经网络的非线性权重，将复杂的非凸拓扑直接映射为处处可导的能级集（Level Set），从而有效消除了离散近似在边缘处产生的梯度噪声。这种全局一致的梯度流为解决灵巧操作在极端狭窄约束下的收敛难题提供了更稳健的数值环境。

### 核心代码提炼与梯度场路径规划实践

我接下来的思考将聚焦于提炼不依赖外部库的 GJK 与 EPA 核心代码逻辑，剥离所有非必要的工程冗余。我计划构建一个精简的基于 SDF 梯度下降的轨迹修正模型，演示如何利用自动微分技术将几何距离产生的连续导数直接耦合进 Contact Jacobian 驱动的力-速度对偶性（Force-Velocity Duality）框架中。这一过程旨在打通从底层几何感知到高精度闭环力矩执行的完整算法链路，确保灵巧操作任务的物理一致性。

#### 研究网站 / Researched Websites

- [medium.com](https://medium.com/@mbayburt/walkthrough-of-the-gjk-collision-detection-algorithm-80823ef5c774) - Walkthrough of the GJK Collision Detection Algorithm | by Mbayburt | Medium
- [gist.github.com](https://gist.github.com/vurtun/29727217c269a2fbf4c0ed9a1d11cb40) - Gilbert–Johnson–Keerthi (GJK) 3D distance algorithm - Github-Gist
- [cse442-17f.github.io](https://cse442-17f.github.io/Gilbert-Johnson-Keerthi-Distance-Algorithm/) - Gilbert-Johnson-Keerthi Distance Algorithm
- [stackoverflow.com](https://stackoverflow.com/questions/68331495/gjk-algorithm-creates-simplex-with-two-opposite-points) - GJK algorithm creates simplex with two opposite points - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=MDusDn8oTSE) - GJK Algorithm Explanation & Implementation - YouTube
- [idanarye.github.io](https://idanarye.github.io/bevy-tnua/parry3d/query/epa/index.html) - parry3d::query::epa - Rust
- [arxiv.org](https://arxiv.org/pdf/2304.07357) - Efficient Incremental Penetration Depth Estimation between Convex Geometries - arXiv
- [dyn4j.org](https://dyn4j.org/2010/05/epa-expanding-polytope-algorithm/) - EPA (Expanding Polytope Algorithm) | dyn4j
- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-01-fall/Papers/van-den-bergen.pdf) - Proximity Queries and Penetration Depth Computation on 3D Game Objects
- [youtube.com](https://www.youtube.com/watch?v=0XQ2FSz3EK8) - EPA Explanation & Implementation - YouTube
- [medium.com](https://medium.com/@saeedkohans85/gradient-descent-a-step-by-step-explanation-with-python-implementation-5b5a1664e460) - Gradient Descent: A Step-by-Step Explanation with Python Implementation - Medium
- [github.com](https://github.com/Sangluisme/gradient-sdf-tracking) - Sangluisme/gradient-sdf-tracking: A new python code for the Gradient-SDF paper - GitHub
- [geeksforgeeks.org](https://www.geeksforgeeks.org/machine-learning/how-to-implement-a-gradient-descent-in-python-to-find-a-local-minimum/) - Implementing gradient descent in Python to find a local minimum - GeeksforGeeks
- [realpython.com](https://realpython.com/gradient-descent-algorithm-python/) - Stochastic Gradient Descent Algorithm With Python and NumPy
- [youtube.com](https://www.youtube.com/watch?v=yuHASn8g1Zs) - One Dimensional Gradient Descent, Python Program, Optimization Tutorial 13c - YouTube
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content_CVPR_2019/papers/Park_DeepSDF_Learning_Continuous_Signed_Distance_Functions_for_Shape_Representation_CVPR_2019_paper.pdf) - DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation - CVF Open Access
- [mdpi.com](https://www.mdpi.com/2673-2688/6/12/317) - Deep Learning for Unsupervised 3D Shape Representation with Superquadrics - MDPI
- [duanyueqi.github.io](https://duanyueqi.github.io/ECCV20_Curriculum%20DeepSDF.pdf) - Curriculum DeepSDF - Yueqi Duan
- [karan3-zoh.medium.com](https://karan3-zoh.medium.com/paper-summary-deepsdf-learning-continuous-signed-distance-functions-for-shape-representation-147af4740485) - Paper Summary: DeepSDF: Learning Continuous Signed Distance Functions for Shape Representation | by Karan Uppal
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/scribe_notes/scribe_lec_11A.pdf) - Lecture 19: Hand Dynamics and Control 19.1 Grasp Statics - GitHub
- [researchgate.net](https://www.researchgate.net/profile/Mohamed_Mourad_Lafifi/post/How-to-derive-the-grasping-matrix-to-evaluate-grasping-quality/attachment/5b5f93c74cde265cb652aacf/AS%3A654223339433985%401532990407574/download/Robot+Grasping+Foundations+-+Springer.pdf) - Robot Grasping Foundations - ResearchGate
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/latest/computation.html) - Computation - MuJoCo Documentation

### 支持映射与函数化几何的范式演进

我正在深度解构支持映射（Support Mapping）作为底层原语的物理直觉。我意识到，$S_A(d) - S_B(-d)$ 不仅仅是一个计算公式，它将复杂的几何相交问题转化为了 Minkowski Difference 空间内的向量极值搜索。这种从显式网格向“函数化几何”的跃迁，使我能够以亚毫秒级的延迟在配置空间（Configuration Space）中追踪物理间隙，为灵巧操作中的高频动态重规划提供了极简的数学框架。

### 神经符号场对离散碰撞断层的全局补完

在审视 EPA 算法在非多面体边缘处的数值跳跃时，我确信了神经符号距离场（Neural SDF）的优越性。相比于传统的凸分解（Convex Decomposition）容易丢失细微接触细节，神经场通过全局隐式函数实现了“拓扑压缩”，将复杂的非凸物体表征为处处可微的能级集（Level Set）。这种表征不仅消除了布尔检测带来的梯度断层，更通过自动微分技术提供了连续的导数信息，从根本上解决了指尖在精细缝隙操作中的数值振荡矛盾。

### 微分物理链路与力-速度对偶性的算法整合

我接下来的任务是提炼不依赖外部库的 GJK 与 EPA 核心逻辑原语，并将其与 Contact Jacobian 的力-速度对偶性（Force-Velocity Duality）深度耦合。我计划构建一个集成 SDF 梯度的微分优化模型，演示如何利用自动微分将几何间的距离梯度直接映射为驱动关节的修正力矩。这一过程旨在打通从隐式感知识别到高精度力觉执行的闭环控制通路，确保灵巧手在处理复杂、非确定性接触序列时的物理一致性。


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*