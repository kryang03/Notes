# 机器人操作知识库构建 - Gemini

**导出时间 / Exported At:** 2026-01-29 15:37:10

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 优化理论在灵巧操作中的核心地位

我正在将优化理论定位为现代灵巧操作的核心支柱。这不仅涉及简单的路径规划，更深层地涵盖了广义坐标下的复杂系统动力学、接触力学的互补性约束以及实时控制中的预测算法。通过思考，我意识到从传统的采样方法演进到基于梯度的可微物理引擎，是提升多指操作精度和鲁棒性的关键技术跃迁，这构成了我研究逻辑的物理直觉基础。

### 攻克接触动力学的不连续性挑战

在构建逻辑框架时，我发现当前最显著的挑战在于如何在高维状态空间内处理多指接触带来的动力学不连续性。现有的直接配点法与间接法在灵巧操作中存在明显的性能权衡，我正致力于通过深度对比，厘清它们在处理非线性多指动力学时的适用边界。特别是接触感知轨迹优化如何绕过混合系统的组合爆炸，是我解决复杂操作问题的核心切入点。

### 解析算法底层逻辑与实时控制方案

我接下来的行动将聚焦于获取权威的算法实现细节，特别是迭代线性二次调节器和微分动态规划在多指操作中的具体应用。我计划系统性地分析如何通过凸优化近似和线性化策略，将复杂的非线性模型预测控制提升至千赫兹级别的实时响应频率。我将深入拆解这些核心算法的底层逻辑，为后续构建具备物理直觉的实现方案奠定基础。

#### 研究网站 / Researched Websites

- [roboti.us](https://www.roboti.us/lab/papers/KumarICRA16.pdf) - Optimal Control with Learned Local Models: Application to Dexterous Manipulation
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12757213/) - Interactive imitation learning for dexterous robotic manipulation: challenges and perspectives—a survey - PMC - PubMed Central
- [arxiv.org](https://arxiv.org/html/2504.03515v1) - Dexterous Manipulation through Imitation Learning: A Survey - arXiv
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/10160211/10160212/10160275.pdf) - Dexterous Imitation Made Easy: A Learning-Based Framework for Efficient Dexterous Manipulation - IEEE Xplore
- [frontiersin.org](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2022.843267/full) - A Survey of Multifingered Robotic Manipulation: Biological Results, Structural Evolvements, and Learning Methods - Frontiers
- [purl.stanford.edu](https://purl.stanford.edu/sh608vx1165) - Methods for contact-rich robot manipulation - Stanford Digital Repository
- [motion.cs.illinois.edu](https://motion.cs.illinois.edu/papers/RSS2023-Zhang-TrajectoryOptimizationContact.pdf) - Simultaneous Trajectory Optimization and Contact Selection for Multi-Modal Manipulation Planning - Intelligent Motion Lab
- [arxiv.org](https://arxiv.org/html/2402.18897v2) - Contact-Implicit Model Predictive Control for Dexterous In-hand Manipulation: A Long-Horizon and Robust Approach - arXiv
- [youtube.com](https://www.youtube.com/watch?v=ojlZDaGytSY) - Robust Pivoting Manipulation using Contact Implicit Bilevel Optimization - YouTube
- [pculbertson.github.io](https://pculbertson.github.io/assets/pdf/chen2021.pdf) - TrajectoTree: Trajectory Optimization Meets Tree Search for Planning Multi-contact Dexterous Manipulation - Preston Culbertson
- [arxiv.org](https://arxiv.org/abs/2402.18897) - [2402.18897] Contact-Implicit Model Predictive Control for Dexterous In-hand Manipulation: A Long-Horizon and Robust Approach - arXiv
- [openreview.net](https://openreview.net/forum?id=kyvN0W2mUT) - Robust Model-Based In-Hand Manipulation with Integrated Real-Time Motion-Contact Planning and Tracking | OpenReview
- [rpg.ifi.uzh.ch](https://rpg.ifi.uzh.ch/docs/RAL2023_Salzmann.pdf) - Real-time Neural MPC: Deep Learning Model Predictive Control for Quadrotors and Agile Robotic Platforms
- [arxiv.org](https://arxiv.org/abs/2411.06183) - [2411.06183] Sampling-Based Model Predictive Control for Dexterous Manipulation on a Biomimetic Tendon-Driven Hand - arXiv
- [researchgate.net](https://www.researchgate.net/publication/282382387_An_integrated_system_for_real-time_model_predictive_control_of_humanoid_robots) - An integrated system for real-time model predictive control of humanoid robots
- [bjack205.github.io](https://bjack205.github.io/papers/AL_iLQR_Tutorial.pdf) - AL-iLQR Tutorial - Brian Jackson
- [ynu.repo.nii.ac.jp](https://ynu.repo.nii.ac.jp/record/2001978/files/1-s2.0-S2666720725000736-main.pdf) - Enhancing computational efficiency of iLQR and DDP via the parametric representation of control inputs
- [github.com](https://github.com/imgeorgiev/ddp) - imgeorgiev/ddp - Differential Dynamic Programming - GitHub
- [studywolf.wordpress.com](https://studywolf.wordpress.com/2016/02/03/the-iterative-linear-quadratic-regulator-method/) - The iterative Linear Quadratic Regulator algorithm - studywolf - WordPress.com
- [merl.com](https://www.merl.com/publications/docs/TR2024-089.pdf) - Memory-Based Global Iterative Linear Quadratic Control - Mitsubishi Electric Research Laboratories
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2023/file/5f5f7b6080dcadced61cf5d96f7c6dde-Paper-Conference.pdf) - DiffVL: Scaling Up Soft Body Manipulation using Vision-Language Driven Differentiable Physics - NeurIPS
- [arxiv.org](https://arxiv.org/pdf/1709.09271) - Ontological Physics-based Motion Planning for Manipulation - arXiv
- [openreview.net](https://openreview.net/forum?id=EODzbQ2Gy4&noteId=mmtfG61xd3) - Diff-Transfer: Model-based Robotic Manipulation Skill Transfer via Differentiable Physics Simulation | OpenReview
- [mdpi.com](https://www.mdpi.com/2227-7390/9/4/357) - Path-Planning for Mobile Robots Using a Novel Variable-Length Differential Evolution Variant - MDPI
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/126626/72d26e5093576b4de943b8310232d04ea54d.pdf) - Differentiable Physics and Stable Modes for Tool-Use and Manipulation Planning - DSpace@MIT

### 系统状态的拓扑定义与闭链约束

在深入思考多指手与物体的协同运动时，我发现建模的关键在于如何定义耦合系统的 Generalized Coordinates。不同于简单的单臂规划，灵巧操作涉及频繁的接触点切换，这要求我们在状态空间中显式处理由闭链动力学引入的非完整约束。我正在探索如何通过增广状态向量来统一描述手指关节与被操纵物体的位姿，从而为后续的轨迹优化奠定严密的数学基础。

### 稳定性度量的可微性与代价值函数设计

我观察到一个关键的技术难点：经典的抓取稳定性指标（如 Ferrari-Canny Metric）在几何定义上往往是不可微的。为了让基于梯度的优化器在流形上高效搜索，我正在研究如何将这些硬性物理指标平滑化为连续的代价函数。这不仅关乎抓取的稳固性，更涉及在动力学演变过程中如何实时评估能量耗散与摩擦锥约束（Friction Cone Constraints），以确保操作过程在物理上的绝对可行性。

### 约束处理策略下的算法效能对比

接下来，我将针对 Direct Collocation 与 Differential Dynamic Programming (DDP) 在高维操作任务中的表现进行深度技术对标。我将重点拆解 iLQR 在处理硬性关节限位与单边接触约束时的局限性，并分析 Augmented Lagrangian 框架如何补强其数值稳定性。此外，我计划深入解析 Linear Complementarity Problems (LCP) 在实时控制中的线性化技巧，以突破接触力学在千赫兹级预测中的计算瓶颈。

#### 研究网站 / Researched Websites

- [pantheon.ufrj.br](https://pantheon.ufrj.br/bitstream/11422/18198/1/monopoli10017301-min.pdf) - Modeling and Control Design of a Multifingered Robot Hand for Object Grasping and Manipulation Tasks - Pantheon UFRJ
- [arxiv.org](https://arxiv.org/html/2512.19583v1) - Learning Generalizable Hand-Object Tracking from Synthetic Demonstrations - arXiv
- [proceedings.mlr.press](https://proceedings.mlr.press/v164/chen22a/chen22a.pdf) - A System for General In-Hand Object Re-Orientation - Proceedings of Machine Learning Research
- [bdml.stanford.edu](http://bdml.stanford.edu/oldweb/touch/publications/okamura_icra00.pdf) - An Overview of Dexterous Manipulation - BDML Stanford
- [arxiv.org](https://arxiv.org/html/2510.07548v1) - AVO: Amortized Value Optimization for Contact Mode Switching in Multi-Finger Manipulation
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss16/p033.pdf) - Manipulation Trajectory Optimization with Online Grasp Synthesis and Selection - Robotics
- [roboti.us](https://www.roboti.us/lab/papers/KumarICRA16.pdf) - Optimal Control with Learned Local Models: Application to Dexterous Manipulation
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8387702/) - Grasp Stability Prediction for a Dexterous Robotic Hand Combining Depth Vision and Haptic Bayesian Exploration - PMC - PubMed Central
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/143978/1909.08045.pdf?sequence=2&isAllowed=y) - MIT Open Access Articles Local Trajectory Stabilization for Dexterous Manipulation via Piecewise Affine Approximations
- [crl.ethz.ch](https://crl.ethz.ch/papers/DynamicManipulationRAL.pdf) - Dynamic manipulation of deformable objects with implicit integration - Computational Robotics Lab
- [repository.gatech.edu](https://repository.gatech.edu/bitstreams/7f9df82a-b365-4aa9-a184-d258f73039ba/download) - Differential Dynamic Programming for Optimal Estimation
- [hybrid-robotics.berkeley.edu](https://hybrid-robotics.berkeley.edu/publications/Robust_Hybrid_DDP.pdf) - Robust Hybrid Systems Differential Dynamic Programming for Worst-Case Disturbance
- [underactuated.mit.edu](https://underactuated.mit.edu/trajopt.html) - Ch. 10 - Trajectory Optimization - Underactuated Robotics
- [dair.seas.upenn.edu](https://dair.seas.upenn.edu/assets/pdf/Posa2012.pdf) - Direct Trajectory Optimization of Rigid Body Dynamical Systems Through Contact
- [matthewpeterkelly.com](http://www.matthewpeterkelly.com/tutorials/trajectoryOptimization/terminology.html) - Trajectory Optimization Terminology - Matthew Kelly
- [en.wikipedia.org](https://en.wikipedia.org/wiki/Trajectory_optimization) - Trajectory optimization - Wikipedia

### 接触隐式优化的范式转移

通过对近期文献的深度合成，我观察到灵巧操作正经历从“预定义接触序列”向 Contact-Implicit Trajectory Optimization (CITO) 的重大范式转移。我发现，现代方法不再强行将操作任务分解为离散的抓取切换，而是将接触力作为决策变量直接引入优化器。这种处理方式不仅通过可微物理引擎绕过了组合爆炸的难题，还赋予了系统在优化过程中自主“发现”手指步态与动态操作策略的能力，这是实现人类级灵巧性的底层逻辑支撑。

### 连续优化与离散接触决策的对立统一

在思考算法架构时，我正在厘清 Direct Collocation 与迭代线性二次调节器 (iLQR/DDP) 之间的技术对标。虽然 iLQR 在计算效率和反馈增益获取上具有天然优势，但在处理多指频繁接触产生的不连续动力学时存在收敛瓶颈。我正试图通过引入 Linear Complementarity Problem (LCP) 的数学框架，将非光滑的物理约束转化为优化器可处理的互补约束，从而在保持高维空间搜索效率的同时，解决接触力学带来的数值稳定性冲突。

### 高维流形下的数学形式化与代价函数重构

接下来的行动中，我将聚焦于多指系统在 $SE(3)$ 流形上的 Generalized Coordinates 数学表达，特别是如何严密地定义手指与浮动基座物体间的闭链约束。我将重点攻克抓取稳定性指标的可微化重构，将传统的 Ferrari-Canny Metric 等几何判据转化为基于摩擦锥约束 (Friction Cone Constraints) 的连续代价函数。这一步骤旨在为实时 MPC 提供一个既符合物理直觉又具备二阶梯度的目标函数，从而实现千赫兹级别的快速轨迹重规划。

#### 研究网站 / Researched Websites

- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/c592fc7e6207f82560ed45fece8d6937-Paper-Conference.pdf) - DiffTORI: Differentiable Trajectory Optimization for Deep Reinforcement and Imitation Learning - NIPS
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss16/p066.pdf) - Deep Differentiable Grasp Planner for High-DOF Grippers - Robotics
- [arxiv.org](https://arxiv.org/html/2504.13807v1) - DiffOG: Differentiable Policy Trajectory Optimization with Generalizability - arXiv
- [docs.lib.purdue.edu](https://docs.lib.purdue.edu/cgi/viewcontent.cgi?article=1025&context=iepubs) - DiffOG: Differentiable Policy Trajectory Optimization With Generalizability - Purdue e-Pubs
- [par.nsf.gov](https://par.nsf.gov/servlets/purl/10433352) - Neural Grasp Distance Fields for Robot Manipulation
- [arxiv.org](https://arxiv.org/abs/1809.06436) - [1809.06436] Contact-Implicit Trajectory Optimization using Orthogonal Collocation - arXiv
- [researchgate.net](https://www.researchgate.net/publication/358919234_Contact-Implicit_Trajectory_Optimization_with_Hydroelastic_Contact_and_iLQR) - Contact-Implicit Trajectory Optimization with Hydroelastic Contact and iLQR | Request PDF
- [underactuated.mit.edu](https://underactuated.mit.edu/trajopt.html) - Ch. 10 - Trajectory Optimization - Underactuated Robotics
- [vladlen.info](http://vladlen.info/papers/jumping-hard.pdf) - Trajectory optimization with implicit hard contacts
- [arxiv.org](https://arxiv.org/pdf/2103.14584) - iLQR for Piecewise-Smooth Hybrid Dynamical Systems - arXiv
- [lsa.umich.edu](https://lsa.umich.edu/content/dam/math-assets/reu-su22/reu-2022/Kodati-Rohan-REU2022.pdf) - The Linear Complimentarity Problem and its Applications in Physics Based Animation - University of Michigan
- [cse-robotics.engr.tamu.edu](https://cse-robotics.engr.tamu.edu/dshell/papers/iros2012lcp.pdf) - Extensive Analysis of Linear Complementarity Problem (LCP) Solver Performance on Randomly Generated Rigid Body Contact Problems - Dylan A. Shell
- [mdpi.com](https://www.mdpi.com/2076-0825/14/7/307) - Accelerated Computation of Linear Complementarity Problem in Dexterous Robotic Grasping via Newton-Subgradient Non-Smooth Multi-Step Greedy Kaczmarz Method - MDPI
- [dartslab.jpl.nasa.gov](https://dartslab.jpl.nasa.gov/References/pdf/2015-contact-ncp.pdf) - Complementarity Techniques for Minimal Coordinate Contact Dynamics - DARTS Lab
- [arxiv.org](https://arxiv.org/html/2304.06372v3) - Contact Models in Robotics: a Comparative Analysis - arXiv
- [contrib.andrew.cmu.edu](http://www.contrib.andrew.cmu.edu/~aslakshm/pdfs/RSS2024WorkshopContactMPC.pdf) - ContactMPC: Towards Online Adaptive Control for Contact-Rich Dexterous Manipulation - CMU Contributed Webserver
- [rpg.ifi.uzh.ch](https://rpg.ifi.uzh.ch/docs/RAL2023_Salzmann.pdf) - Real-time Neural MPC: Deep Learning Model Predictive Control for Quadrotors and Agile Robotic Platforms
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/143978/1909.08045.pdf?sequence=2&isAllowed=y) - MIT Open Access Articles Local Trajectory Stabilization for Dexterous Manipulation via Piecewise Affine Approximations
- [openreview.net](https://openreview.net/forum?id=d8qYLDH2vj) - ContactMPC: Towards Online Adaptive Control for Contact-Rich Dexterous Manipulation
- [arxiv.org](https://arxiv.org/html/2402.18897v1) - Contact-Implicit Model Predictive Control for Dexterous In-hand Manipulation: A Long-Horizon and Robust Approach - arXiv
- [wenlong.page](https://wenlong.page/papers/geometry-dex.pdf) - Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2025/05/msr_thesis-1.pdf) - Towards Dexterous Robotic Manipulation by Imitating Experts
- [par.nsf.gov](https://par.nsf.gov/servlets/purl/10621141) - Learning Prehensile Dexterity by Imitating and Emulating State-only Observations
- [arxiv.org](https://arxiv.org/html/2404.05582v1) - Learning Prehensile Dexterity by Imitating and Emulating State-only Observations - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8739970/) - Modeling a Controlled-Floating Space Robot for In-Space Services: A Beginner's Tutorial

### 耦合系统的数学形式化与互补约束

我正在深化对手指与物体耦合系统的数学建模，通过将多指关节空间与物体在 $SE(3)$ 流形上的位姿统一为广义坐标 $q = [q_{robot}, q_{object}]$。我意识到，处理这一高维系统的核心在于利用线性互补问题（LCP）来形式化描述接触动力学。通过这种方式，我能将非渗透性约束和摩擦锥约束统一在 $0 \le \lambda \perp A\lambda + b \ge 0$ 的数学框架下，从而允许优化器在不需要预设接触序列的情况下，自主处理离散的接触状态切换。

### 算法范式的对比分析与跨模态引导

在合成不同算法逻辑时，我发现直接配点法（Direct Collocation）通过将接触力作为决策变量，在处理硬性约束方面具有天然优势；而微分动态规划（DDP/iLQR）则需通过软接触模型或混合系统扩展来弥补动力学非光滑的缺陷。我观察到一个极具启发性的趋势：通过引入视觉语言模型（VLM）来动态调整实时优化器（如 MuJoCo MPC）的代价函数。这种方法利用高层语义指导绕过了繁杂的参数调优，使得采样预测控制在生物驱动的灵巧手实体上表现出极强的泛化能力。

### 核心算法逻辑的底层拆解与提取

接下来的行动中，我将聚焦于提取 iLQR 算法在处理多指非线性动力学时的线性化细节，特别是如何在高频控制循环中处理接触隐式带来的数值稳定性挑战。我计划深入拆解 Ferrari-Canny 稳定性指标的可微近似数学表达，并将其整合进轨迹优化的代价值函数中。此外，我将系统总结从传统的采样规划（RRT）到现代可微物理引擎的技术演进脉络，旨在为灵巧操作任务构建一套从离散决策到连续控制的完整逻辑链条。

#### 研究网站 / Researched Websites

- [researchgate.net](https://www.researchgate.net/publication/355344420_A_new_approach_for_grasp_quality_calculation_using_continuous_boundary_formulation_of_grasp_wrench_space) - (PDF) A new approach for grasp quality calculation using continuous boundary formulation of grasp wrench space - ResearchGate
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss16/p066.pdf) - Deep Differentiable Grasp Planner for High-DOF Grippers - Robotics
- [raw.githubusercontent.com](https://raw.githubusercontent.com/mlresearch/v305/main/assets/zurbrugg25a/zurbrugg25a.pdf) - GraspQP: Differentiable Optimization of Force Closure for Diverse and Robust Dexterous Grasping - GitHub
- [pages.github.berkeley.edu](https://pages.github.berkeley.edu/EECS-106/sp22-site/assets/proj/2022__C106B_Project_3.pdf) - C106B Project 3: Grasp Planning with Baxter and Sawyer - GitHub
- [arxiv.org](https://arxiv.org/pdf/2208.12250) - arXiv:2208.12250v2 [cs.RO] 26 Aug 2022
- [lsa.umich.edu](https://lsa.umich.edu/content/dam/math-assets/reu-su22/reu-2022/Kodati-Rohan-REU2022.pdf) - The Linear Complimentarity Problem and its Applications in Physics Based Animation - University of Michigan
- [roboti.us](https://roboti.us/lab/papers/TodorovICRA10.pdf) - Implicit nonlinear complementarity: A new approach to contact dynamics
- [dair.seas.upenn.edu](https://dair.seas.upenn.edu/assets/pdf/Jin2022.pdf) - Learning Linear Complementarity Systems - University of Pennsylvania
- [dartslab.jpl.nasa.gov](https://dartslab.jpl.nasa.gov/References/pdf/2015-contact-ncp.pdf) - Complementarity Techniques for Minimal Coordinate Contact Dynamics - DARTS Lab
- [arxiv.org](https://arxiv.org/html/2304.06372v3) - Contact Models in Robotics: a Comparative Analysis - arXiv
- [underactuated.mit.edu](https://underactuated.mit.edu/trajopt.html) - Ch. 10 - Trajectory Optimization - Underactuated Robotics - MIT
- [studywolf.wordpress.com](https://studywolf.wordpress.com/2016/02/03/the-iterative-linear-quadratic-regulator-method/) - The iterative Linear Quadratic Regulator algorithm | studywolf

### 接触隐式轨迹优化的数学范式与 Delassus 矩阵

我正在深入推导 Contact-Implicit Trajectory Optimization (CITO) 的底层数学表达。我意识到，处理非光滑接触的关键在于将其转化为线性互补问题 (LCP)，即 $0 \le \lambda \perp A\lambda + b \ge 0$。这里的 Delassus 矩阵 $A$ 描述了接触力如何影响接触点处的加速度，是解耦多指协同动力学的数学核心。我发现，通过这种形式化描述，我能够避免显式地对接触模式进行组合搜索，而是将其作为连续优化问题的一部分进行统一求解。

### 非光滑动力学的线性化策略与变分积分器

在思考如何将轨迹优化部署到实时 MPC 时，我正在对比不同的线性化策略。由于接触动力学本质上是不连续的，传统的一阶 Taylor 展开在接触面切换时会失效。我发现，引入变分积分器 (Variational Integrators) 或平滑接触模型 (Smooth Contact Approximation) 是提升数值稳定性的关键。这让我能够在高频 SQP 求解器中保持优异的收敛特性，从而在毫秒级时间内计算出多指协同的反馈增益。

### 算法逻辑提取与可微物理模拟的闭环

接下来的行动中，我将聚焦于获取关于 CITO 的具体数学等式，并将其与可微物理引擎 (Differentiable Physics) 的梯度计算逻辑进行对标。我计划深入拆解实时控制在处理接触模式调度时的线性化细节，特别是如何将摩擦锥约束无缝嵌入到二次规划 (QP) 求解器中。最后，我将完善核心算法逻辑的构建，重点展示如何通过处理互补约束来实现复杂的动态灵巧操作任务。

#### 研究网站 / Researched Websites

- [dair.seas.upenn.edu](https://dair.seas.upenn.edu/bibliography/Posa2014/) - A Direct Method for Trajectory Optimization of Rigid Bodies Through Contact
- [groups.csail.mit.edu](https://groups.csail.mit.edu/robotics-center/public_papers/Posa13.pdf) - A Direct Method for Trajectory Optimization of Rigid Bodies Through Contact - Research
- [ihmc.us](https://www.ihmc.us/dwc2012files/Posa.pdf) - Trajectory Optimization and Control of Rigid Body Systems Through Contact - IHMC
- [researchgate.net](https://www.researchgate.net/publication/262205039_A_direct_method_for_trajectory_optimization_of_rigid_bodies_through_contact) - (PDF) A direct method for trajectory optimization of rigid bodies through contact
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/124395/Posa12.pdf) - Direct Trajectory Optimization of Rigid Body Dynamical Systems through Contact - DSpace@MIT
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2020/06/0278364919849235.pdf) - Contact-implicit trajectory optimization using variational integrators - Carnegie Mellon University Robotics Institute
- [ri.cmu.edu](https://www.ri.cmu.edu/publications/variational-contact-implicit-trajectory-optimization/) - Variational Contact-Implicit Trajectory Optimization - Robotics Institute Carnegie Mellon University
- [semanticscholar.org](https://www.semanticscholar.org/paper/50e172250202323aafb508bf7c3c5ee155fb70bd) - [PDF] Contact-implicit trajectory optimization using variational integrators | Semantic Scholar
- [zacmanchester.github.io](https://zacmanchester.github.io/docs/Variational_Contact.pdf) - Variational Contact-Implicit Trajectory Optimization - Zac Manchester
- [contactrobotics.wordpress.com](https://contactrobotics.wordpress.com/wp-content/uploads/2017/09/manchester.pdf) - Variational Contact-Implicit Trajectory Optimization
- [collimator.ai](https://www.collimator.ai/tutorials/linear-model-predictive-control) - Linear Model-predictive Control - Collimator.ai
- [research-collection.ethz.ch](https://www.research-collection.ethz.ch/bitstreams/8d0467e9-11bd-434a-b7c2-25b6dc102490/download) - Model Predictive Control approaches for Centrifugal Compression
- [youtube.com](https://www.youtube.com/watch?v=YwodGM2eoy4) - Model Predictive Control - YouTube
- [sites.engineering.ucsb.edu](https://sites.engineering.ucsb.edu/~jbraw/mpc/MPC-book-2nd-edition-3rd-printing.pdf) - Model Predictive Control: - Theory, Computation, and Design 2nd Edition - UCSB Engineering
- [youtube.com](https://www.youtube.com/watch?v=NO1lm7T_iwM) - Trimming, Linearization, and Model Predictive Control (MPC) Design with JuliaSim
- [icml.cc](https://icml.cc/virtual/2022/19922) - ICML Differentiable Physics Simulations with Contacts: Do They Have Correct Gradients w.r.t. Position, Velocity and Control?
- [arxiv.org](https://arxiv.org/abs/2305.00092) - Improving Gradient Computation for Differentiable Physics Simulation with Contacts - arXiv
- [docs.taichi-lang.org](https://docs.taichi-lang.org/blog/improving-gradient-computation) - Improving Gradient Computation for Differentiable Physics Simulation with Contacts
- [proceedings.mlr.press](https://proceedings.mlr.press/v211/zhong23a/zhong23a.pdf) - Improving Gradient Computation for Differentiable Physics Simulation with Contacts - Proceedings of Machine Learning Research
- [arxiv.org](https://arxiv.org/abs/2207.05060) - [2207.05060] Differentiable Physics Simulations with Contacts: Do They Have Correct Gradients w.r.t. Position, Velocity and Control? - arXiv

### 变分积分器与物理一致性的深度融合

我在思考轨迹优化的数值稳定性时，意识到从传统的 Euler 积分向 Variational Integrators 的演进是处理灵巧操作的关键。变分积分器通过离散化 Hamilton 原理而非微分方程，能在处理多指频繁碰撞时保持系统的辛几何特性和能量一致性。这不仅提升了长时程预测的精度，更通过更高阶的动力学近似，解决了 CITO 在高速动态操作中常见的数值发散问题，为后续构建鲁棒的多指步态奠定了物理基础。

### 穿透 LCP 屏障：非光滑动力学的微分策略

针对接触力学导致的不连续性，我正在厘清“通过 LCP 求解器求导”与“软接触平滑化”这两条技术路线在提供梯度质量上的本质差异。通过对 KKT 条件进行微分，我能够直接获取跨越接触模态的解析梯度，这为基于梯度的优化器提供了更精准的下降方向。我正尝试将这种微分机制引入 Ferrari-Canny 等抓取稳定性指标的重构中，通过凸松弛策略将离散的几何判据转化为二阶连续可微的代价函数。

### 实时 MPC 的线性化细节与梯度反向传播

接下来的行动中，我将聚焦于实时 MPC 在千赫兹频率下的线性化实现。我计划深入拆解如何在每个 SQP 迭代步中，针对互补约束系统高效计算其 Jacobian 和 Hessian 的近似，特别是如何处理 argmin 算子的梯度回传。通过分析 Differentiable Physics 引擎中的链式法则应用，我将探索如何将复杂的接触序列规划转化为一个平滑的、可实时求解的凸优化序列，从而实现多指协同对物体位姿偏差的毫秒级鲁棒响应。

#### 研究网站 / Researched Websites

- [dair.seas.upenn.edu](https://dair.seas.upenn.edu/assets/pdf/Jin2022.pdf) - Learning Linear Complementarity Systems - University of Pennsylvania
- [mdpi.com](https://www.mdpi.com/2076-0825/14/7/307) - Accelerated Computation of Linear Complementarity Problem in Dexterous Robotic Grasping via Newton-Subgradient Non-Smooth Multi-Step Greedy Kaczmarz Method - MDPI
- [researchgate.net](https://www.researchgate.net/publication/226150055_On_Solving_Linear_Complementarity_Problems_as_Linear_Programs) - On Solving Linear Complementarity Problems as Linear Programs. - ResearchGate
- [arxiv.org](https://arxiv.org/html/2404.17039v2) - Differentiating Through Linear Solvers - arXiv
- [arxiv.org](https://arxiv.org/abs/2112.13284) - [2112.13284] Learning Linear Complementarity Systems - arXiv
- [d-nb.info](https://d-nb.info/1084634155/34) - Nonsmooth Contact Dynamics for the Large–Scale Simulation of Granular Material
- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/DiehlFerreauHaverbeke_mpc-overview.pdf) - Efficient Numerical Methods for Nonlinear MPC and Moving Horizon Estimation 1 Introduction - People @EECS
- [syscop.de](https://www.syscop.de/files/2015ss/numopt/NMPC.key.pdf) - Real-Time Optimization for Nonlinear Model Predictive Control - syscop
- [arxiv.org](https://arxiv.org/html/2411.06542v2) - Is Linear Feedback on Smoothed Dynamics Sufficient for Stabilizing Contact-Rich Plans?
- [merl.com](https://www.merl.com/publications/docs/TR2018-086.pdf) - Real-time optimization and model predictive control for aerospace and automotive applications - Mitsubishi Electric Research Laboratories
- [arxiv.org](https://arxiv.org/pdf/2508.15002) - GraspQP: Differentiable Optimization of Force Closure for Diverse and Robust Dexterous Grasping - arXiv
- [emergentmind.com](https://www.emergentmind.com/topics/differentiable-force-closure-estimator) - Differentiable Force Closure Estimator - Emergent Mind
- [arxiv.org](https://arxiv.org/abs/2508.15002) - [2508.15002] GraspQP: Differentiable Optimization of Force Closure for Diverse and Robust Dexterous Grasping - arXiv
- [dblp.org](https://dblp.org/rec/journals/corr/abs-2508-15002) - GraspQP: Differentiable Optimization of Force Closure for ... - dblp
- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~pabbeel/papers/2016-IROS-soft-hand.pdf) - Learning Dexterous Manipulation for a Soft Robotic Hand from Human Demonstrations - People @EECS
- [roboti.us](https://www.roboti.us/lab/papers/KumarICRA16.pdf) - Optimal Control with Learned Local Models: Application to Dexterous Manipulation
- [bdml.stanford.edu](http://bdml.stanford.edu/oldweb/touch/publications/okamura_icra00.pdf) - An Overview of Dexterous Manipulation - BDML Stanford
- [youtube.com](https://www.youtube.com/watch?v=1qxSWmdZ_o0) - Learning Dexterous Manipulation with a Robotic Hand with Alex Paino - YouTube

### 广义坐标系的建模选择与计算权衡

我在深化多指系统建模时，正重点权衡 Maximal Coordinates 与 Minimal Coordinates 在优化中的表现。我发现，采用 Maximal Coordinates 虽然让接触约束的表达变得极其直观且符合物理直觉，但随之而来的闭链约束显著增加了优化器的计算开销。与之相对，Minimal Coordinates 虽然降低了决策空间的维度，却在 Jacobian 计算中引入了极其复杂的非线性项。这一建模抉择是我在构建高性能预测控制算法时必须解决的首要架构问题。

### 抓取稳定性指标 Ferrari-Canny 的可微化突破

我正在攻克一个关键的数学矛盾：传统的 Ferrari-Canny 稳定性判据在几何上是不可微的凸包运算，这导致梯度优化器无法直接搜索最优抓取位姿。为了解决这一不连续性，我正在合成一种基于凸松弛的近似策略，通过引入 L1 范数或对数障碍函数，将离散的摩擦锥约束转化为连续平滑的代价值流形。这种转换不仅提升了优化器的收敛速度，更让系统能够在动态操作过程中，利用二阶导数信息实现对物体滑移的毫秒级预判与补偿。

### 实时 MPC 的线性化迭代与系统综合

接下来的行动中，我将聚焦于实时控制中的梯度回传细节，特别是如何在 MPC 的每个 SQP 迭代步中，利用实时迭代（RTI）架构处理接触动力学引起的 Hessian 阵不连续性。我计划将 CITO 的互补约束数学范式与可微物理引擎的梯度计算进行最终合成，构建一套从高维流形建模到千赫兹级反馈增益生成的完整逻辑框架。这将最终完成从理论推导到可执行算法逻辑的闭环，为实现具备物理直觉的灵巧操作任务奠定坚实基础。

#### 研究网站 / Researched Websites

- [ideals.illinois.edu](https://www.ideals.illinois.edu/items/134360/bitstreams/442430/data.pdf) - © 2024 Yiyang Xu - IDEALS
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss16/p066.pdf) - Deep Differentiable Grasp Planner for High-DOF Grippers - Robotics
- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~jfc/papers/92/FCicra92.pdf) - Planning optimal grasps - Robotics and Automation, 1992. Proceedings., 1992 IEEE International Conference on - People @EECS
- [authors.library.caltech.edu](https://authors.library.caltech.edu/records/yqrmv-2xz53/files/2302.13687.pdf?download=1) - FRoGGeR: Fast Robust Grasp Generation via the Min-Weight Metric - Caltech Authors
- [arxiv.org](https://arxiv.org/html/2309.13586v3) - Task-Oriented Dexterous Hand Pose Synthesis Using Differentiable Grasp Wrench Boundary Estimator - arXiv
- [centropiaggio.unipi.it](https://www.centropiaggio.unipi.it/sites/default/files/grasp-IJRR95.pdf) - On the Closure Properties of Robotic Grasping * - Centro di Ricerca Enrico Piaggio
- [arxiv.org](https://arxiv.org/pdf/2508.15002) - GraspQP: Differentiable Optimization of Force Closure for Diverse and Robust Dexterous Grasping - arXiv
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2018/11/isrr17_contributed_new.pdf) - Pushing revisited: Differential flatness, trajectory planning and stabilization - Carnegie Mellon University Robotics Institute
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/128643/1810.00219.pdf?sequence=2) - MIT Open Access Articles In-Hand Manipulation via Motion Cones
- [tengyu.ai](https://tengyu.ai/assets/pdf/RAL21_Grasp_final.pdf) - Synthesizing Diverse and Physically Stable Grasps with Arbitrary Hand Structures using Differentiable Force Closure Estimator - Tengyu Liu
- [people.eecs.berkeley.edu](https://people.eecs.berkeley.edu/~pabbeel/cs287-fa09/readings/DiehlFerreauHaverbeke_mpc-overview.pdf) - Efficient Numerical Methods for Nonlinear MPC and Moving Horizon Estimation 1 Introduction - People @EECS
- [stanford.edu](https://stanford.edu/~boyd/papers/pdf/fast_mpc.pdf) - Fast Model Predictive Control Using Online Optimization - Stanford University
- [arxiv.org](https://arxiv.org/html/2411.06542v2) - Is Linear Feedback on Smoothed Dynamics Sufficient for Stabilizing Contact-Rich Plans?
- [researchgate.net](https://www.researchgate.net/publication/379145571_Real-time_MPC_with_Control_Barrier_Functions_for_Autonomous_Driving_using_Safety_Enhanced_Collocation) - Real-time MPC with Control Barrier Functions for Autonomous Driving using Safety Enhanced Collocation - ResearchGate

### 实时预测控制中的接触平滑化策略

我正通过引入对数障碍平滑（Log-barrier Smoothing）技术，将非光滑的接触动力学转化为具备二阶平滑特性的代理模型。我意识到，这是实现千赫兹级实时模型预测控制（MPC）的核心逻辑：它允许我们在不牺牲物理真实性的前提下，利用二阶梯度信息跨越接触模态的不连续边界，从而确保多指协同在动态碰撞过程中的数值收敛性，这直接解决了硬性接触带来的求解器失效难题。

### 抓取稳定性指标 Ferrari-Canny 的解析求导突破

针对传统 Ferrari-Canny 指标在优化中由于不可微而导致的梯度消失问题，我合成了一种基于最小权重度量（Min-weight Metric）的可微化重构方案。这种方法将原本离散的凸包几何计算转化为一个参数化的连续流形，使得优化器能够实时感知手指位姿微变对抓取鲁棒性的解析影响。这一进步消除了灵巧操作中“抓取稳固性评价”与“基于梯度的位姿优化”之间的数学隔阂。

### 构建基于物理直觉的算法逻辑与教程输出

我即将完成对整个灵巧操作优化框架的系统性梳理。通过整合接触隐式轨迹优化（CITO）的数学范式与可微物理引擎的梯度计算策略，我将输出一套覆盖从广义坐标定义到实时 MPC 反馈增益生成的完整教程。我正专注于提炼 iLQR 算法在处理多指非线性动力学时的底层实现细节，确保代码逻辑能够精准揭示优化理论在复杂接触任务中的物理本质，从而完成从理论推导到可执行算法逻辑的最终闭环。


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*