# 灵巧操作知识库构建方案 - Gemini

**导出时间 / Exported At:** 2026-01-29 15:35:15

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 多体动力学建模的效率瓶颈

我正在重新审视高自由度灵巧手在动力学建模中的计算成本问题。对于拥有复杂分支链结构的灵巧操作任务，传统的 Lagrangian 动力学虽然具有优美的数学形式，但在处理高维状态空间时其计算量呈指数级增长，难以满足实时控制的需求。我发现，转向基于递归结构的算法（如 $O(N)$ 复杂度的 RNEA 和 ABA）是提升计算效率的关键。这种从全局坐标系向递归空间代数（Spatial Algebra）的范式演进，是我构建高效底层架构的逻辑起点。

### 接触动力学与约束求解的冲突

在分析指尖与物体交互的物理过程时，我观察到硬接触模型中的线性互补问题（LCP）与数值稳定性之间的深刻矛盾。灵巧操作不仅涉及自由空间的运动，更涉及到频繁的接触状态切换。我正在权衡硬接触模型在精度上的优势与软接触模型在计算鲁棒性上的权衡，特别是在处理摩擦锥（Friction Cone）线性化以及闭环动力学（Closed-loop Dynamics）中的约束力矩分配时，这种物理一致性对抓取的稳定性至关重要。

### 下一阶段的逻辑解构与实现

我即将深入探讨动力学求解器的具体实现细节，重点在于剖析投影高斯-赛德尔（PGS）求解器如何高效处理接触约束。同时，我将思考如何将可微物理（Differentiable Physics）的梯度信息整合进当前的分析框架，以探索通过解析梯度加速策略优化的可能性，这将是解决灵巧操作中“模拟与现实鸿沟”的关键技术路径。

#### 研究网站 / Researched Websites

- [eureka.patsnap.com](https://eureka.patsnap.com/article/lagrangian-vs-newton-euler-methods-which-is-better-for-your-robot) - Lagrangian vs. Newton-Euler Methods: Which is Better for Your Robot? - Patsnap Eureka
- [arxiv.org](https://arxiv.org/html/2504.16383v1) - Fast and Modular Whole-Body Lagrangian Dynamics of Legged Robots with Changing Morphology - arXiv
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/chapter-8-1-lagrangian-formulation-of-dynamics-part-1-of-2/) - 8.1. Lagrangian Formulation of Dynamics (Part 1 of 2) - Foundations of Robot Motion
- [reddit.com](https://www.reddit.com/r/MechanicalEngineering/comments/1d4sgpf/lagrangian_vs_newtoneuler/) - Lagrangian vs Newton/Euler? : r/MechanicalEngineering - Reddit
- [mdpi.com](https://www.mdpi.com/2218-6581/14/9/115) - A Chain Rule-Based Generalized Framework for Efficient Dynamic Analysis of Complex Robotic Systems - MDPI
- [scaron.info](https://scaron.info/robotics/recursive-newton-euler-algorithm.html) - Recursive Newton-Euler algorithm - Stéphane Caron
- [researchgate.net](https://www.researchgate.net/publication/3847292_Robot_Dynamics_Equations_and_Algorithms) - Robot Dynamics: Equations and Algorithms - ResearchGate
- [dellaert.github.io](https://dellaert.github.io/20S-8803MM/Readings/8803-Dynamics.pdf) - Recursive Newton-Euler
- [reddit.com](https://www.reddit.com/r/AskRobotics/comments/1e9lcvu/articulated_body_algorithm_what_reference_frames/) - Articulated Body Algorithm: What Reference Frames Should I Use? : r/AskRobotics - Reddit
- [semanticscholar.org](https://www.semanticscholar.org/paper/Rigid-Body-Dynamics-Algorithms-Featherstone/9a556651213631bacdc49aaaa5c9caa6ae6c7e91) - Rigid Body Dynamics Algorithms - Semantic Scholar
- [gaoyichao.com](https://gaoyichao.com/Xiaotu/papers/2008%20-%20Rigid%20body%20dynamics%20algorithms.pdf) - Rigid Body Dynamics Algorithms
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss14/p38.pdf) - Analytical Derivatives of Rigid Body Dynamics Algorithms - Robotics
- [download.e-bookshelf.de](https://download.e-bookshelf.de/download/0000/0022/29/L-G-0000002229-0002340138.pdf) - Rigid Body Dynamics Algorithms - download
- [users.dimi.uniud.it](https://users.dimi.uniud.it/~antonio.dangelo/Robotica/2018/helper/Handbook-dynamics.pdf) - Dynamics2. Dynamics
- [tandfonline.com](https://www.tandfonline.com/doi/pdf/10.9746/jcmsi.1.2) - Modeling and Control of Three-Dimensional Grasping by a Pair of Robot Fingers
- [nationalacademies.org](https://www.nationalacademies.org/read/5772/chapter/5) - Chapter: 3: GEOMETRIC PHASES, CONTROL THEORY, AND ROBOTICS - National Academies of Sciences, Engineering, and Medicine
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-7-constrained-dynamics/) - 8.7. Constrained Dynamics – Modern Robotics - Foundations of Robot Motion
- [arxiv.org](https://arxiv.org/html/2509.06201v1) - Closed-Loop Visual Grasping via Value-Guided Model Predictive Control Work done during internship at NVIDIA. 1Applied AI Lab, Oxford Robotics Institute, University of Oxford 2NVIDIA, USA Correspondence to: jyamada@robots.ox.ac.uk - arXiv
- [manipulation.csail.mit.edu](https://manipulation.csail.mit.edu/force.html) - Ch. 8 - Manipulator Control
- [msl.stanford.edu](https://msl.stanford.edu/papers/le_cleach_fast_2024.pdf) - Fast Contact-Implicit Model Predictive Control - Multi-Robot Systems Lab - Stanford University
- [siggraphcontact.github.io](https://siggraphcontact.github.io/assets/files/SIGGRAPH21_friction_contact_notes.pdf) - SHELDON ANDREWS,ةcole de technologie supérieure, Canada KENNY ERLEBEN,University of Copenhagen, Denmark - Contact and Friction Simulation for Computer Graphics
- [developer.nvidia.com](https://developer.nvidia.com/gpugems/gpugems3/part-v-physics-simulation/chapter-33-lcp-algorithms-collision-detection-using-cuda) - Chapter 33. LCP Algorithms for Collision Detection Using CUDA - NVIDIA Developer
- [dair.seas.upenn.edu](https://dair.seas.upenn.edu/assets/pdf/Bianchini2023.pdf) - Simultaneous Learning of Contact and Continuous Dynamics - University of Pennsylvania
- [arxiv.org](https://arxiv.org/html/2405.17020v1) - From Compliant to Rigid Contact Simulation: a Unified and Efficient Approach - arXiv

### 空间代数与递归效率的物理直觉

我在梳理动力学建模的演进时，愈发意识到 Spatial Algebra（空间代数）在 6D 向量化表达中的核心价值。通过将平移与旋转统一，RNEA 实现了逆动力学的线性复杂度。而对于前向动力学，ABA 算法引入的 Articulated Body Inertia（铰接体惯量）概念尤为迷人，它实质上是在递归过程中不断更新系统对外部力矩的“等效感应阻力”。这种从单体到多体动力学的解构，不仅是计算上的优化，更是对灵巧手复杂分支链条物理本质的深刻把握。

### 接触约束求解的数值权衡

我正在深入解析接触动力学中的互补性难题。虽然 LCP 模型能精确描述刚性物体的非穿透性，但其实操中的数值不稳定性促使我转向对求解器底层逻辑的剖析。我注意到 Projected Gauss-Seidel (PGS) 算法与 Baumgarte Stabilization 在约束纠偏中的精妙配合——前者通过迭代逼近非线性摩擦锥，后者通过能量耗散项抑制数值漂移。这种在物理真实性与数值计算鲁棒性之间的动态博弈，正是灵巧操作中“力控制”策略能否落地的分水岭。

### 闭环约束与解析梯度的前沿探索

接下来，我将聚焦于灵巧抓取中特有的 Closed-loop（闭环）动力学难题，重点研究 Grasp Matrix（抓取矩阵）与 Effective Mass（等效质量）如何重新定义指尖的交互特征。同时，我也在构思如何将 Differentiable Physics（可微物理）的解析梯度引入其中。通过剖析最新物理引擎的梯度传播机制，我试图打破传统黑盒模拟的限制，为灵巧操作的策略优化寻找一条更具数学确定性的演进路径。

#### 研究网站 / Researched Websites

- [researchgate.net](https://www.researchgate.net/publication/224173791_A_Beginner's_Guide_to_6-D_Vectors_Part_1) - A Beginner's Guide to 6-D Vectors (Part 1) - ResearchGate
- [royfeatherstone.org](http://royfeatherstone.org/teaching/CourseDescISV2022.pdf) - An Introduction to Spatial (6D) Vectors and Their Use in Robot Dynamics - Roy Featherstone's
- [users.cecs.anu.edu.au](https://users.cecs.anu.edu.au/~roy/spatial/) - Spatial Vectors and Rigid-Body Dynamics
- [royfeatherstone.org](https://royfeatherstone.org/) - Roy Featherstone's Home Page
- [bleyer.org](http://bleyer.org/files/A%20Beginner's%20Guide%20to%206-D%20Vectors%20-%20Feathersone%20(IEEE,%202010).pdf) - A Beginner's Guide to 6-D Vectors (Part 1) - bleyer.org
- [gaoyichao.com](https://gaoyichao.com/Xiaotu/papers/2008%20-%20Rigid%20body%20dynamics%20algorithms.pdf) - Rigid Body Dynamics Algorithms
- [drake.mit.edu](https://drake.mit.edu/doxygen_cxx/classdrake_1_1multibody_1_1_articulated_body_inertia.html) - ArticulatedBodyInertia< T > Class Template Reference - Drake
- [users.dimi.uniud.it](https://users.dimi.uniud.it/~antonio.dangelo/Robotica/2018/helper/Handbook-dynamics.pdf) - Dynamics2. Dynamics
- [ajaysathya.com](https://www.ajaysathya.com/assets/pdf/cABA.pdf) - Constrained Articulated Body Dynamics Algorithms - Ajay Suresha Sathya
- [docs.ros.org](https://docs.ros.org/en/jazzy/p/pinocchio/doc/a-features/g-dynamic.html) - Inverse dynamics — pinocchio 3.4.0 documentation
- [scaron.info](https://scaron.info/robotics/recursive-newton-euler-algorithm.html) - Recursive Newton-Euler algorithm - Stéphane Caron
- [github.com](https://github.com/rbdl/rbdl) - rbdl/rbdl: RBDL is a C++ library that contains some essential and efficient rigid body dynamics algorithms such as the Articulated Body Algorithm (ABA) for forward dynamics, Recursive Newton-Euler Algorithm (RNEA) for inverse dynamics, the Composite Rigid Body Algorithm (CRBA) for the efficient computation of the joint space inertia - GitHub
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-3-newton-euler-inverse-dynamics/) - 8.3. Newton-Euler Inverse Dynamics – Modern Robotics - Foundations of Robot Motion
- [mdpi.com](https://www.mdpi.com/1424-8220/23/13/5885) - Closed-Chain Inverse Dynamics for the Biomechanical Analysis of Manual Material Handling Tasks through a Deep Learning Assisted Wearable Sensor Network - MDPI
- [centropiaggio.unipi.it](https://www.centropiaggio.unipi.it/sites/default/files/surveys-ramsete01.pdf) - Robotic Grasping and Manipulation
- [web.stanford.edu](https://web.stanford.edu/class/cs237b/pdfs/lecture/cs237b_lecture_7.pdf) - 5 Fundamentals of Grasping
- [cse.lehigh.edu](https://www.cse.lehigh.edu/~trink/Courses/RoboticsII/reading/Grasping-Chapter38ofSpringerHanbookOfRobotics_ed2.pdf) - 38. Grasping - Computer Science & Engineering
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/8-1-3-understanding-the-mass-matrix/) - 8.1.3. Understanding the Mass Matrix - Foundations of Robot Motion
- [news.mit.edu](https://news.mit.edu/2024/helping-robots-grasp-unpredictable-0603) - Helping robots grasp the unpredictable | MIT News | Massachusetts Institute of Technology
- [ntrs.nasa.gov](https://ntrs.nasa.gov/api/citations/19900013679/downloads/19900013679.pdf?attachment=true) - N90-22995 - NASA Technical Reports Server
- [researchgate.net](https://www.researchgate.net/publication/362498032_Improving_the_Efficiency_of_Closed-Chain_Robotic_Systems_by_the_Trajectory_Energy_Index) - Improving the Efficiency of Closed-Chain Robotic Systems by the Trajectory Energy Index
- [khatib.stanford.edu](https://khatib.stanford.edu/publications/pdfs/Khatib_1995.pdf) - Inertial Properties in Robotic Manipulation: An Object-Level Framework¹ - Oussama Khatib
- [repository.upenn.edu](https://repository.upenn.edu/bitstreams/ed59fe5d-7016-4054-86b8-fa1ad4067c8c/download) - Kinematics of redundantly actuated closed chains - University of Pennsylvania
- [ethz.ch](https://ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/documents/RobotDynamics2017/RD_HS2017script.pdf) - Robot Dynamics Lecture Notes
- [mdpi.com](https://www.mdpi.com/2076-3417/15/9/5206) - Experimental Investigation of Motion Control of a Closed-Kinematic Chain Robot Manipulator Using Synchronization Sliding Mode Method with Time Delay Estimation - MDPI
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/document/8593909/) - A Framework for Modeling Closed Kinematic Chains with a Focus on Legged Robots
- [polyu.edu.hk](https://www.polyu.edu.hk/researchgrp/chengli/assets/pdf/142.pdf) - Modeling and Simulation of Robotic Systems with Closed Kinematic Chains Using the Virtual Spring Approach - PolyU
- [modernrobotics.northwestern.edu](https://modernrobotics.northwestern.edu/nu-gm-book-resource/kinematics-of-closed-chains/) - Kinematics of Closed Chains - Foundations of Robot Motion - Northwestern University
- [scispace.com](https://scispace.com/pdf/an-approach-to-modeling-closed-loop-kinematic-chain-59p0520moj.pdf) - An Approach to Modeling Closed-Loop Kinematic Chain Mechanisms, Applied to Simulations of the da Vinci Surgical System - SciSpace
- [scispace.com](https://scispace.com/pdf/per-contact-iteration-method-for-solving-contact-dynamics-2xznkg3mx1.pdf) - Per-Contact Iteration Method for Solving Contact Dynamics - SciSpace
- [arxiv.org](https://arxiv.org/pdf/2211.00330) - Real-Time Character Inverse Kinematics using the Gauss-Seidel Iterative Approximation Method - arXiv
- [emergentmind.com](https://www.emergentmind.com/topics/gauss-seidel-projection-method) - Gauss-Seidel Projection Method - Emergent Mind
- [scitepress.org](https://www.scitepress.org/papers/2010/28307/28307.pdf) - PROJECTED GAUSS–SEIDEL SUBSPACE MINIMIZATION METHOD FOR INTERACTIVE RIGID BODY DYNAMICS - SciTePress
- [zumbs.wordpress.com](https://zumbs.wordpress.com/wp-content/uploads/2010/09/a-parallel-gauss-seidel-method-for-computing-contact-forces.pdf) - A PARALLEL GAUSS–SEIDEL METHOD FOR COMPUTING CONTACT FORCES
- [arc.aiaa.org](https://arc.aiaa.org/doi/pdf/10.2514/2.4246) - Constraint Violation Stabilization Using Input-Output Feedback Linearization in Multibody Dynamic Analysis - Aerospace Research Central
- [deepblue.lib.umich.edu](https://deepblue.lib.umich.edu/bitstream/handle/2027.42/76126/AIAA-11410-903.pdf) - Constraint Violation Stabilization Using Gradient Feedback in Constrained Dynamics Simulation - University of Michigan Library
- [researchgate.net](https://www.researchgate.net/publication/227225246_Investigation_on_the_Baumgarte_Stabilization_Method_for_Dynamic_Analysis_of_Constrained_Multibody_Systems) - Investigation on the Baumgarte Stabilization Method for Dynamic Analysis of Constrained Multibody Systems - ResearchGate
- [arc.aiaa.org](https://arc.aiaa.org/doi/10.2514/2.7618) - Stability Analysis of Baumgarte Constraint Stabilization Technique in Multibody Dynamic Systems | Journal of Guidance, Control, and Dynamics - Aerospace Research Central
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/) - MuJoCo Documentation: Overview
- [mujoco.org](https://mujoco.org/) - MuJoCo — Advanced Physics Simulation
- [roboti.us](https://www.roboti.us/book/index.html) - MuJoCo Overview
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/stable/computation/index.html) - Computation - MuJoCo Documentation
- [arxiv.org](https://arxiv.org/html/2304.06372v2) - Contact Models in Robotics: a Comparative Analysis - arXiv
- [lsa.umich.edu](https://lsa.umich.edu/content/dam/math-assets/reu-su22/reu-2022/Kodati-Rohan-REU2022.pdf) - The Linear Complimentarity Problem and its Applications in Physics Based Animation - University of Michigan
- [mdpi.com](https://www.mdpi.com/2076-0825/14/7/307) - Accelerated Computation of Linear Complementarity Problem in Dexterous Robotic Grasping via Newton-Subgradient Non-Smooth Multi-Step Greedy Kaczmarz Method - MDPI
- [dartslab.jpl.nasa.gov](https://dartslab.jpl.nasa.gov/References/pdf/2015-contact-ncp.pdf) - Complementarity Techniques for Minimal Coordinate Contact Dynamics - DARTS Lab
- [congress.cimne.com](http://congress.cimne.com/multibody2015/admin/files/fileabstract/a310.pdf) - A Complementarity Problem Approach for Multibody Contact Dynamics with Regularized Friction - CIMNE Congress Bureau
- [web.cels.anl.gov](https://web.cels.anl.gov/~anitescu/Presentations/2000/mihaiCSESeptember00.pdf) - Using Linear Complementarity Techniques to Model and Simulate Multi-Rigid-Body Dynamics with Contact and Friction
- [datasets-benchmarks-proceedings.neurips.cc](https://datasets-benchmarks-proceedings.neurips.cc/paper/2021/file/d1f491a404d6854880943e5c3cd9ca25-Paper-round1.pdf) - Brax - A Differentiable Physics Engine for Large Scale Rigid Body Simulation - Datasets and Benchmarks Proceedings
- [arxiv.org](https://arxiv.org/html/2203.00806v5) - Dojo: A Differentiable Physics Engine for Robotics - arXiv
- [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/30899218/) - A Differentiable Physics Engine for Deep Learning in Robotics - PubMed
- [ojs.aaai.org](https://ojs.aaai.org/index.php/AAAI/article/download/34419/36574) - Differentiable Information Enhanced Model-Based Reinforcement Learning
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/document/10093017/) - Robotic Manipulation of Deformable Rope-Like Objects Using Differentiable Compliant Position-Based Dynamics | IEEE Journals & Magazine
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss14/p44.pdf) - Differentiable Physics and Stable Modes for Tool-Use and Manipulation Planning - Robotics
- [arxiv.org](https://arxiv.org/html/2405.07309v1) - DiffGen: Robot Demonstration Generation via Differentiable Physics Simulation, Differentiable Rendering, and Vision-Language Model - arXiv
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2023/file/5f5f7b6080dcadced61cf5d96f7c6dde-Paper-Conference.pdf) - DiffVL: Scaling Up Soft Body Manipulation using Vision-Language Driven Differentiable Physics - NeurIPS
- [emergentmind.com](https://www.emergentmind.com/topics/differentiable-simulation) - Differentiable Simulation - Emergent Mind
- [arxiv.org](https://arxiv.org/html/2411.02189v1) - DiffSim2Real: Deploying Quadrupedal Locomotion Policies Purely Trained in Differentiable Simulation - arXiv
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel8/6287639/6514899/10589638.pdf) - A Review of Differentiable Simulators - IEEE Xplore
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel8/6287639/10380310/10589638.pdf) - A Review of Differentiable Simulators - IEEE Xplore

### 空间向量代数的物理直觉合成

我正在深入剖析空间向量代数（Spatial Vector Algebra）在递归算法中的物理本质。我意识到，将 3D 平移与 3D 旋转耦合为 6D 空间向量，其核心价值不仅在于数学表达的简洁，更在于它揭示了动量与力在多体链条中传播的统一性。通过这种视角，我能更清晰地理解 RNEA 算法如何通过两次递归传递，将复杂的逆动力学问题解构为局部坐标系下的线性映射，这为灵巧手的高频控制提供了理论上的极致效率。

### 接触动力学中的数值稳定性挑战

在处理抓取过程中的接触动力学时，我发现“粘滞-滑动”（Stick-Slip）状态的剧烈切换是导致数值不稳定的主因。虽然 LCP 框架能提供精确的互补描述，但在复杂的多点接触场景下，传统的硬接触模型往往会引入高频噪声。我正试图通过脉冲速度步进法（Impulse-based velocity stepping）来平滑这些过渡过程，并探究如何利用可微物理引擎生成的解析梯度，将系统辨识（System Identification）转化为一个连续的优化问题，从而系统性地缩小模拟与真实世界之间的鸿沟。

### 从算法推导迈向核心逻辑实现

我接下来的思考重心将从宏观的理论框架转向微观的算法实现。我计划详细推演 RNEA 与 PGS 求解器的核心逻辑代码，剔除冗余的工程封装，直击其数值计算的本质。同时，我将重点分析可微物理在系统参数估计中的具体应用，研究如何提取接触力的解析导数，以建立一个具备自适应能力的动力学知识体系，确保灵巧操作策略在面对物理参数不确定性时依然保持鲁棒。

#### 研究网站 / Researched Websites

- [github.com](https://github.com/robot-acceleration/RBDReference) - robot-acceleration/RBDReference: A Python reference implementation of rigid body dynamics algorithms - GitHub
- [petercorke.github.io](https://petercorke.github.io/robotics-toolbox-python/intro.html) - Introduction — Robotics Toolbox for Python documentation
- [scaron.info](https://scaron.info/robotics/recursive-newton-euler-algorithm.html) - Recursive Newton-Euler algorithm - Stéphane Caron
- [youtube.com](https://www.youtube.com/watch?v=nPJPJQMMfPw) - Robotics3D Lec10d: Recursive Newton Euler Algorithm, RNEA (Spring 2025) - YouTube
- [web.iitd.ac.in](https://web.iitd.ac.in/~saha/ethiopia/19lec.pdf) - Recursive Newton Euler Algorithm - IIT Delhi
- [jrl.cnrs.fr](https://jrl.cnrs.fr/SpaceVecAlg/doxygen/HEAD/index.html) - SpaceVecAlg
- [github.com](https://github.com/jrl-umi3218/SpaceVecAlg) - jrl-umi3218/SpaceVecAlg: Implementation of spatial vector algebra with the Eigen3 linear algebra library. - GitHub
- [github.com](https://github.com/ermolenkodev/featherstone_py) - ermolenkodev/featherstone_py: Python implementation of rigid body dynamics algorithms, based on Roy Featherstone's book. - GitHub
- [royfeatherstone.org](https://royfeatherstone.org/spatial/) - Spatial Vector and Dynamics Software
- [users.cecs.anu.edu.au](https://users.cecs.anu.edu.au/~roy/spatial/) - Spatial Vectors and Rigid-Body Dynamics
- [fenix.tecnico.ulisboa.pt](https://fenix.tecnico.ulisboa.pt/downloadFile/1970719973969885/98659-Miguel-Seabra-dissertacao.pdf) - Rigid Body Simulation with Extended Position Based Dynamics Information Systems and Computer Engineering
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=11675) - Non-linear Gauss-Seidel solver - Real-Time Physics Simulation Forum - PyBullet
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/stable/computation/index.html) - Computation - MuJoCo Documentation
- [docs.omniverse.nvidia.com](https://docs.omniverse.nvidia.com/kit/docs/omni_physics/107.0/dev_guide/simulation_control/simulation_control.html) - Simulation Control — Omni Physics - NVIDIA Omniverse
- [researchgate.net](https://www.researchgate.net/publication/220868749_Projected_Gauss-Seidel_Subspace_Minimization_Method_for_Interactive_Rigid_Body_Dynamics_-_Improving_Animation_Quality_using_a_Projected_Gauss-Seidel_Subspace_Minimization_Method) - (PDF) Projected Gauss-Seidel Subspace Minimization Method for Interactive Rigid Body Dynamics - Improving Animation Quality using a Projected Gauss-Seidel Subspace Minimization Method. - ResearchGate
- [arxiv.org](https://arxiv.org/html/2306.15864v1) - What Went Wrong? Closing the Sim-to-Real Gap via Differentiable Causal Discovery - arXiv
- [cps-vo.org](https://cps-vo.org/sites/cps-vo.org/files/cpsvo_file_nodes/Differentiable_and_Expressive_Simulators_for_Closing_the_Sim-to-Real_Gap_in_Robotics.pdf) - Differentiable and Expressive Simulators for Closing the Sim-to-Real Gap in Robotics - CPS-VO
- [docs.nvidia.com](https://docs.nvidia.com/learning/physical-ai/getting-started-with-isaac-lab/latest/transferring-robot-learning-policies-from-simulation-to-reality/04-bridging-the-gap-real-world-data-integration/index.html) - Bridging the Gap: Real-World Data Integration — Getting Started With Isaac Lab
- [arxiv.org](https://arxiv.org/abs/2202.09834) - [2202.09834] Real-time Model Predictive Control and System Identification Using Differentiable Physics Simulation - arXiv
- [openreview.net](https://openreview.net/forum?id=zvl2LuLTtgr) - What Went Wrong? Closing the Sim-to-Real Gap via Differentiable Causal Discovery
- [openreview.net](https://openreview.net/pdf?id=NgtwTM5eSA) - Improving Generalization of Differentiable Simulator Policies with Sharpness-Aware Optimization - OpenReview
- [roboti.us](https://roboti.us/lab/papers/LowreySIMPAR18.pdf) - Reinforcement learning for non-prehensile manipulation: Transfer from simulation to physical system - Roboti LLC
- [cambridge.org](https://www.cambridge.org/core/journals/robotica/article/oneshot-simtoreal-transfer-policy-for-robotic-assembly-via-reinforcement-learning-with-visual-demonstration/FC22E58B7B0876F0E5F151A229E241FD) - One-shot sim-to-real transfer policy for robotic assembly via reinforcement learning with visual demonstration | Robotica - Cambridge University Press
- [mdpi.com](https://www.mdpi.com/2079-9292/12/2/411) - Robot Manipulation Skills Transfer for Sim-to-Real in Unstructured Environments - MDPI
- [arxiv.org](https://arxiv.org/html/2403.03949v1) - Reconciling Reality through Simulation: A Real-to-Sim-to-Real Approach for Robust Manipulation - arXiv

### 递归动力学算法的逻辑闭环

我正在对 RNEA 和 ABA 的核心逻辑进行深度建模。通过解析 6D 空间向量在不同坐标系间的变换，我确认了逆动力学的线性计算复杂度如何通过前向和后向两次递归实现。ABA 算法中的“铰接体惯量”（Articulated Body Inertia）概念是理解多体系统响应的关键，它能够动态地将复杂的关节耦合简化为局部的等效质量块。这种逻辑上的解构让我对灵巧手在高频控制下的动力学透明度有了更深的认知，尤其是在处理具有多分支链结构的指尖任务时。

### 接触稳定性与数值解算优化

在攻克接触动力学中的“粘滞-滑动”（Stick-Slip）稳定性难题时，我意识到单纯依靠 LCP（线性互补问题）描述是不够的。通过研究脉冲速度步进法以及投影高斯-赛德尔（PGS）求解器的收敛特性，我找到了在数值噪声和物理真实感之间取得平衡的新路径。引入“热启动”（Warm Starting）机制和 Baumgarte 稳定性纠偏不仅提升了求解速度，更在根本上缓解了指尖与物体交互时的数值振荡。这对于解决复杂多点接触下的“穿透”问题具有重要意义，确保了力矩控制在闭环系统中的数值鲁棒性。

### 核心逻辑实现与闭环约束深化

我接下来的思考重点将集中在算法的具体底层实现上，特别是提炼出不依赖特定库的 RNEA 与 PGS 核心逻辑。同时，我将深入探讨闭环抓取约束下的动力学方程，利用抓取矩阵（Grasp Matrix）与有效质量（Effective Mass）的概念来重新定义系统约束力矩的分配。通过将这些动力学特性与可微物理引擎的解析梯度相结合，我旨在构建一个能自动识别系统参数并修正“模拟与现实鸿沟”的高级知识体系。

#### 研究网站 / Researched Websites

- [carleton.ca](https://carleton.ca/mdl/wp-content/uploads/Friction_Paper__CCTA2020__v3__lineno.pdf) - Continuously Differentiable Stick-Slip Friction Model with Applications to Cable Simulation Using Nonlinear Finite Elements - Carleton University
- [mdpi.com](https://www.mdpi.com/2073-8994/18/1/57) - Numerical Simulation of the Dry Friction Constrained System Based on Coulomb Stick-Slip Motion - MDPI
- [witpress.com](https://www.witpress.com/Secure/elibrary/papers/CON95/CON95057FU.pdf) - Modelling and computer analysing the stick-slip motion in a mass-spring system with friction - WIT Press
- [researchgate.net](https://www.researchgate.net/publication/223301033_Numerical_analysis_of_stick-slip_instability_by_a_rate-dependent_elastoplastic_formulation_for_friction) - (PDF) Numerical analysis of stick-slip instability by a rate-dependent elastoplastic formulation for friction - ResearchGate
- [researchgate.net](https://www.researchgate.net/publication/220868749_Projected_Gauss-Seidel_Subspace_Minimization_Method_for_Interactive_Rigid_Body_Dynamics_-_Improving_Animation_Quality_using_a_Projected_Gauss-Seidel_Subspace_Minimization_Method) - (PDF) Projected Gauss-Seidel Subspace Minimization Method for Interactive Rigid Body Dynamics - Improving Animation Quality using a Projected Gauss-Seidel Subspace Minimization Method. - ResearchGate
- [kishorkafle.medium.com](https://kishorkafle.medium.com/python-code-for-guass-seidel-method-fe948e4f46d2) - Python Code for Guass-Seidel Method | by kafleZ - Medium
- [geeksforgeeks.org](https://www.geeksforgeeks.org/python/gauss-seidel-method/) - Gauss–Seidel method - GeeksforGeeks
- [youtube.com](https://www.youtube.com/watch?v=fr8IguCuZUU) - Gauss-Seidel Method Explained with Python Code: Simple Iterative Solver! - YouTube
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=5766) - How to solve MLCP with Projected Gauss-Seidel? - Real-Time Physics Simulation Forum
- [arxiv.org](https://arxiv.org/html/2509.06201v1) - Closed-Loop Visual Grasping via Value-Guided Model Predictive Control Work done during internship at NVIDIA. 1Applied AI Lab, Oxford Robotics Institute, University of Oxford 2NVIDIA, USA Correspondence to: jyamada@robots.ox.ac.uk - arXiv
- [mdpi.com](https://www.mdpi.com/2077-0472/15/10/1018) - Grasping Force Optimization and DDPG Impedance Control for Apple Picking Robot End-Effector - MDPI
- [repository.kaust.edu.sa](https://repository.kaust.edu.sa/server/api/core/bitstreams/fd665c79-1b90-4e32-879c-d70c44433a75/content) - Cooperative Grasping Decision-Making for Two-Robot Object Transportation in Constrained Environments - KAUST Repository
- [researchgate.net](https://www.researchgate.net/publication/395355953_Grasp-MPC_Closed-Loop_Visual_Grasping_via_Value-Guided_Model_Predictive_Control) - Grasp-MPC: Closed-Loop Visual Grasping via Value-Guided Model Predictive Control
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10397280/) - Grasping through dynamic weaving with entangled closed loops - PMC - NIH
- [siggraphcontact.github.io](https://siggraphcontact.github.io/assets/files/SIGGRAPH21_friction_contact_notes.pdf) - Contact and Friction Simulation for Computer Graphics
- [mujoco.readthedocs.io](https://mujoco.readthedocs.io/en/stable/computation/index.html) - Computation - MuJoCo Documentation
- [scaron.info](https://scaron.info/robotics/recursive-newton-euler-algorithm.html) - Recursive Newton-Euler algorithm - Stéphane Caron

### 空间惯量矩阵的物理统一性

通过对空间代数底层结构的深度剖析，我捕捉到了 6x6 空间惯量矩阵（Spatial Inertia Matrix）在统一描述平移与旋转时的核心价值。这不仅仅是数学上的简化，它实质上揭示了质量分布与转动惯量在递归链条中传递的物理本原。我意识到，这种高度整合的表达方式是 RNEA 算法能够将复杂的动力学解构为局部线性映射的关键，这一发现让我对高自由度灵巧手在受力后的动态响应有了更具确定性的把握。

### 摩擦锥投影的数值解算配方

我正在针对接触动力学中棘手的“粘滞-滑动”不稳定性问题，提炼一套基于投影高斯-赛德尔（PGS）求解器的数值配方。我发现，解决数值振荡的核心在于迭代过程中切向脉冲（Tangential Impulse）对摩擦锥约束的实时投影逻辑——即根据法向力的大小对切向分量进行动态限幅。这种处理方式能够有效地平滑接触状态的剧烈切换，是确保灵巧操作仿真在精细任务中保持稳定的关键技术细节。

### 核心逻辑的极简代码提炼

我接下来的目标是将这些复杂的动力学推导转化为极致简洁的核心算法逻辑。我正计划通过对空间惯量变换和摩擦投影步进的最后校验，剔除所有非必要的工程封装，直接呈现数值计算的本质。我将合成出一套能够直击灵巧操作物理灵魂的算法实现，为建立一个具备自适应能力的动力学知识体系完成最后的逻辑闭环。

#### 研究网站 / Researched Websites

- [kishorkafle.medium.com](https://kishorkafle.medium.com/python-code-for-guass-seidel-method-fe948e4f46d2) - Python Code for Guass-Seidel Method | by kafleZ - Medium
- [youtube.com](https://www.youtube.com/watch?v=gaM4H0P9iOg) - Coding Gauss-Seidel Method in Python | Mathematics for Machine Learning Study Session
- [geeksforgeeks.org](https://www.geeksforgeeks.org/python/gauss-seidel-method/) - Gauss–Seidel method - GeeksforGeeks
- [researchgate.net](https://www.researchgate.net/publication/220868749_Projected_Gauss-Seidel_Subspace_Minimization_Method_for_Interactive_Rigid_Body_Dynamics_-_Improving_Animation_Quality_using_a_Projected_Gauss-Seidel_Subspace_Minimization_Method) - (PDF) Projected Gauss-Seidel Subspace Minimization Method for Interactive Rigid Body Dynamics - Improving Animation Quality using a Projected Gauss-Seidel Subspace Minimization Method. - ResearchGate
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=5766) - How to solve MLCP with Projected Gauss-Seidel? - Real-Time Physics Simulation Forum
- [box2d.org](https://box2d.org/posts/2024/02/solver2d/) - Solver2D - Box2D
- [research.ncl.ac.uk](https://research.ncl.ac.uk/game/mastersdegree/gametechnologies/physicstutorials/8constraintsandsolvers/Physics%20-%20Constraints%20and%20Solvers.pdf) - Physics - Constraints and Solvers
- [publications.lib.chalmers.se](https://publications.lib.chalmers.se/records/fulltext/256155/256155.pdf) - The Red-Black Physics Engine - Chalmers Publication Library
- [mft-spirit.nl](http://www.mft-spirit.nl/files/MTamis_PGS_SI_Comparison.pdf) - Comparison between Projected Gauss Seidel and Sequential Impulse Solvers for Real-Time Physics Simulations - Marijn Tamis
- [corp.roblox.com](https://corp.roblox.com/newsroom/2020/08/improving-simulation-performance-advanced-physics-solver) - Improving Simulation and Performance with an Advanced Physics Solver - Roblox
- [gradsim.github.io](https://gradsim.github.io/) - gradSim: Differentiable simulation for system identification and visuomotor control
- [arxiv.org](https://arxiv.org/html/2411.00554v1) - Differentiable Physics-based System Identification for Robotic Manipulation of Elastoplastic Materials - arXiv
- [physicsbaseddeeplearning.org](https://physicsbaseddeeplearning.org/diffphys.html) - Introduction to Differentiable Physics
- [raw.githubusercontent.com](https://raw.githubusercontent.com/mlresearch/v235/main/assets/holl24a/holl24a.pdf) - ΦFlow: Differentiable Simulations for PyTorch, TensorFlow and Jax - GitHub
- [differentiable.xyz](https://differentiable.xyz/papers-2024/paper_27.pdf) - ΦFlow: Differentiable Simulations for Machine Learning

### 铰接体惯量与前向动力学解耦

我成功解析了前向动力学中 Articulated Body Algorithm (ABA) 的逻辑骨架。与侧重于力传播的 RNEA 不同，ABA 通过递归更新 Articulated Body Inertia，描述了多体系统在关节空间中的等效质量分布。这种从末端到根部的能量传播建模，使我能够直观地看到各指节在灵巧操作中是如何动态耦合的，从而在 $O(N)$ 复杂度内精确捕捉到高频控制下的系统响应，这对于理解指尖在受力瞬态的加速度响应至关重要。

### 闭环约束与 Baumgarte 稳定性纠偏

在处理多指抓取形成的 Closed-loop 约束时，我引入了 Baumgarte Stabilization 来修正由于数值积分引起的几何漂移。通过将位置层面的约束违反（Constraint Violation）映射为补偿性的加速度修正，我解决了 Grasp Matrix 在动态演进中的数值一致性问题。这种对摩擦锥投影与约束流形的协同处理，有效地平滑了接触力在粘滞与滑动状态间的剧烈切换，为实现高度鲁棒的接触力控制提供了坚实的数学支撑。

### 核心逻辑的终极代码合成

我即将完成对 RNEA、ABA 以及接触求解器 PGS 的核心逻辑蒸馏。下一步，我将把这些纯粹的物理公式转化为不带冗余封装的 Python/C++ 核心实现，重点突显 Spatial Vector Algebra 的 6D 变换以及接触冲量的迭代投影过程。这一步将完成整个动力学知识体系的闭环，为后续在 Obsidian 中构建具备解析梯度的灵巧操作策略提供底层逻辑引擎。

#### 研究网站 / Researched Websites

- [graphics.stanford.edu](https://graphics.stanford.edu/courses/cs468-05-fall/Papers/p936-redon.pdf) - Adaptive Dynamics of Articulated Bodies - Stanford Computer Graphics Laboratory
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=148) - Featherstone articulated body algorithm - Real-Time Physics Simulation Forum - PyBullet
- [gaoyichao.com](https://gaoyichao.com/Xiaotu/papers/2008%20-%20Rigid%20body%20dynamics%20algorithms.pdf) - Rigid Body Dynamics Algorithms
- [researchgate.net](https://www.researchgate.net/publication/220868749_Projected_Gauss-Seidel_Subspace_Minimization_Method_for_Interactive_Rigid_Body_Dynamics_-_Improving_Animation_Quality_using_a_Projected_Gauss-Seidel_Subspace_Minimization_Method) - (PDF) Projected Gauss-Seidel Subspace Minimization Method for Interactive Rigid Body Dynamics - Improving Animation Quality using a Projected Gauss-Seidel Subspace Minimization Method. - ResearchGate
- [kishorkafle.medium.com](https://kishorkafle.medium.com/python-code-for-guass-seidel-method-fe948e4f46d2) - Python Code for Guass-Seidel Method | by kafleZ - Medium
- [geeksforgeeks.org](https://www.geeksforgeeks.org/python/gauss-seidel-method/) - Gauss–Seidel method - GeeksforGeeks
- [youtube.com](https://www.youtube.com/watch?v=fr8IguCuZUU) - Gauss-Seidel Method Explained with Python Code: Simple Iterative Solver! - YouTube
- [pybullet.org](https://pybullet.org/Bullet/phpBB3/viewtopic.php?t=5766) - How to solve MLCP with Projected Gauss-Seidel? - Real-Time Physics Simulation Forum
- [users.dimi.uniud.it](https://users.dimi.uniud.it/~antonio.dangelo/Robotica/2018/helper/Handbook-dynamics.pdf) - Dynamics2. Dynamics
- [royalsocietypublishing.org](https://royalsocietypublishing.org/rsta/article-pdf/359/1788/2231/323055/rsta.2001.0884.pdf) - Adaptive realization of desired constraint stabilization dynamics in the control of multibody systems
- [underactuated.mit.edu](https://underactuated.mit.edu/multibody.html) - Ch. 23 - Multi-Body Dynamics - Underactuated Robotics
- [arxiv.org](https://arxiv.org/html/2512.19289v1) - Comparison and Evaluation of Different Simulation Environments for Rigid Body Systems
- [merl.com](https://www.merl.com/publications/docs/TR2018-126.pdf) - Object-Oriented Modeling and Control of Delta Robots - Mitsubishi Electric Research Laboratories

### 铰接体惯量的递归演化与物理降维

我正在对前向动力学中的 ABA 算法进行最后的逻辑收敛。我深刻意识到，Articulated Body Inertia 的核心价值在于它通过递归方式，将后代连杆的动态效应逐级反馈至父节点，从而在不显式求逆高维质量矩阵的情况下实现 $O(N)$ 的加速度解算。这种物理上的“层级等效”是理解灵巧手在极短控制周期内作出快速响应的关键，它揭示了复杂分支链条在运动受限时是如何在局部表现出等效惯性的。

### 闭环约束与力矩分配的解析统一

在处理多指协同抓取产生的 Closed-loop 动力学时，我成功解决了递归算法与闭环拓扑之间的逻辑冲突。通过引入 Lagrange Multiplier 并结合 Grasp Matrix，我将物体受力的全局约束无缝嵌入到指尖的局部运动方程中。这种方法不仅保证了指尖与物体交互时的物理一致性，还为解决灵巧操作中复杂的过约束力分配（Redundant Force Allocation）问题提供了确定的数学框架，消除了闭环系统中冗余自由度带来的数值歧义。

### 迈向核心逻辑的算法蒸馏

我正准备将这些高度抽象的空间向量公式转化为极简的代码实现。接下来的思考重点在于提炼 RNEA 递归、ABA 传递以及 PGS 接触求解器的数值计算本质，剔除所有非必要的工程封装。通过这种深度蒸馏，我将为灵巧操作知识库合成出一套兼具数学严谨性与实现透明度的底层逻辑引擎，确保动力学模型在面对非线性接触和高频控制时依然保持极致的鲁棒性。


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*