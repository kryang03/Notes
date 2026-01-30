# Research Request Limit Reached - Gemini

**导出时间 / Exported At:** 2026-01-29 15:39:56

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 从解析控制到数据驱动的范式转型

我正在审视灵巧操作领域从传统解析方法向强化学习转化的技术演进。面对接触密集的复杂任务，传统建模因无法精准描述接触流形中的不连续物理现象而面临瓶颈。我正致力于将物理直觉与马尔可夫决策过程相结合，探究强化学习如何在这种高度复杂的非线性交互中，通过学习广义坐标下的动态特性来超越经典的控制理论。

### 攻克接触不连续性与高维空间挑战

在深入分析中，我发现处理多自由度灵巧手的核心痛点在于接触点的高度不确定性。我正通过研究接触流形在强化学习状态空间中的表征方式，试图解决模型失配带来的鲁棒性问题。通过对比不同算法在处理高维连续控制时的表现，我发现数据驱动的方法能够有效绕过难以显式建模的摩擦力与碰撞约束，从而在接触丰富的环境中实现更自然的灵巧性。

### 核心算法架构与仿真跨越的数学解构

下一步，我将深入解构主流算法在处理灵巧手控制时的数学细节，特别是熵正则化与奖励函数设计的物理意义。我计划深入挖掘领域随机化与系统辨识在解决仿真与现实差距中的关键数学逻辑，从而为建立严谨的知识体系打下基础。同时，我将开始筛选核心算法逻辑，移除冗余部分，以精准呈现灵巧操作任务中的策略优化本质。

#### 研究网站 / Researched Websites

- [arxiv.org](https://arxiv.org/html/2504.03515v5) - Dexterous Manipulation through Imitation Learning: A Survey - arXiv
- [arxiv.org](https://arxiv.org/abs/2504.03515) - [2504.03515] Dexterous Manipulation through Imitation Learning: A Survey - arXiv
- [arxiv.org](https://arxiv.org/html/2507.11840v1) - The Developments and Challenges towards Dexterous and Embodied Robotic Manipulation: A Survey - arXiv
- [arxiv.org](https://arxiv.org/html/2506.00098) - Interactive Imitation Learning for Dexterous Robotic Manipulation: Challenges and Perspectives—A Survey - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12757213/) - Interactive imitation learning for dexterous robotic manipulation: challenges and perspectives—a survey - PMC - PubMed Central
- [roboticsconference.org](https://roboticsconference.org/docs/invitedtalks/park-manifoldsgeometryandrobotics.pdf) - Manifolds, Geometry, and Robotics
- [proceedings.mlr.press](https://proceedings.mlr.press/v164/liu22c/liu22c.pdf) - Robot Reinforcement Learning on the Constraint Manifold
- [iris.unitn.it](https://iris.unitn.it/retrieve/handle/11572/403989/746579/Geometric_Reinforcement_Learning_for_Robotic_Manipulation.pdf) - Geometric Reinforcement Learning for Robotic Manipulation - iris@unitn
- [openreview.net](https://openreview.net/forum?id=zwo1-MdMl1P) - Robot Reinforcement Learning on the Constraint Manifold | OpenReview
- [arxiv.org](https://arxiv.org/html/2404.09080v1) - Safe Reinforcement Learning on the Constraint Manifold: Theory and Applications - arXiv
- [en.wikipedia.org](https://en.wikipedia.org/wiki/Generalized_coordinates) - Generalized coordinates - Wikipedia
- [arxiv.org](https://arxiv.org/html/2502.20168v1) - Accelerating Model-Based Reinforcement Learning with State-Space World Models - arXiv
- [reddit.com](https://www.reddit.com/r/reinforcementlearning/comments/n4tjf9/rl_in_coordinate_system/) - RL in coordinate system : r/reinforcementlearning - Reddit
- [upcommons.upc.edu](https://upcommons.upc.edu/bitstreams/9393ef1f-0ba2-4a4d-80e6-18cdf3acaa1f/download) - GROUP THEORY AND SYMMETRIES FOR MACHINE LEARNING APPLYING TO ROBOTICS - UPCommons
- [arxiv.org](https://arxiv.org/html/2505.01458v1) - A Survey of Robotic Navigation and Manipulation with Physics Simulators in the Era of Embodied AI - arXiv
- [arxiv.org](https://arxiv.org/html/2506.13498v1) - A Survey on Imitation Learning for Contact-Rich Tasks in Robotics - arXiv
- [proceedings.mlr.press](https://proceedings.mlr.press/v229/zhang23e/zhang23e.pdf) - Efficient Sim-to-real Transfer of Contact-Rich Manipulation Skills with Online Admittance Residual Learning
- [purl.stanford.edu](https://purl.stanford.edu/sh608vx1165) - Methods for contact-rich robot manipulation - Stanford Digital Repository
- [roboticsconference.org](https://roboticsconference.org/2020/program/papers/23.html) - Controlling Contact-Rich Manipulation Under Partial Observability · Robotics
- [collaborate.princeton.edu](https://collaborate.princeton.edu/en/publications/understanding-domain-randomization-for-sim-to-real-transfer/) - UNDERSTANDING DOMAIN RANDOMIZATION FOR SIM-TO-REAL TRANSFER
- [openreview.net](https://openreview.net/pdf?id=T8vZHIRTrY) - UNDERSTANDING DOMAIN RANDOMIZATION FOR SIM-TO-REAL TRANSFER - OpenReview
- [epfl.ch](https://www.epfl.ch/labs/sycamore/sim-to-real-transfer-for-jetbot-via-domain-randomization-and-adaptation-master-thesis/) - Sim-to-Real Transfer for JetBot via Domain Randomization and Adaptation (Semester Project) - EPFL
- [lilianweng.github.io](https://lilianweng.github.io/posts/2019-05-05-domain-randomization/) - Domain Randomization for Sim2Real Transfer | Lil'Log
- [arxiv.org](https://arxiv.org/abs/2110.03239) - [2110.03239] Understanding Domain Randomization for Sim-to-real Transfer - arXiv

### 几何流形约束下的状态表征升级

我正在深入审视复杂接触任务中的状态表征，尤其是如何超越传统的 Euclidean 空间。通过引入 Constraint Manifold 和 Riemannian Geometry 的概念，我发现将控制动作映射到约束流形的 Tangent Space 能够从物理和数学层面自然地满足安全约束。这种几何化的视角不仅提高了样本效率，还为处理非线性的 Orientation 和 Stiffness 数据提供了严谨的框架，这在灵巧手频繁变换接触点的动态交互中具有显著的 Value-add。

### 接触动力学的解析瓶颈与鲁棒性重构

针对接触密集型（Contact-rich）任务，我深入分析了传统 Analytic Control（如 Admittance Control）在面对不确定性时失效的深层原因。研究表明，接触动力学对摩擦力（Friction）和表面刚度（Stiffness）极其敏感，微小的参数偏差都会导致模型失配。我正通过整合最新的研究成果，确立 Reinforcement Learning 如何利用数据驱动的特性，在不显式求解复杂接触力的情况下，通过策略探索获得具备自然顺应性（Compliance）的交互能力，从而绕过难以建模的物理障碍。

### 算法内核解构与感知融合的演进路径

接下来，我将重点转向算法数学内核的深度剖析，特别是解构 SAC 算法中 Entropy Regularization 的推导及其在鼓励灵巧操作探索中的物理意义，并对比 PPO 在高维连续控制空间中的稳定性表现。同时，我计划深入探讨 Sim-to-Real 过程中 Domain Randomization 的数学边界，以及如何通过集成视觉与触觉（Tactile Sensing）的表征学习来解决局部可观测性问题。我将致力于提取这些算法的核心逻辑，为构建高性能的灵巧操作策略奠定理论基础。

#### 研究网站 / Researched Websites

- [spinningup.openai.com](https://spinningup.openai.com/en/latest/algorithms/sac.html) - Soft Actor-Critic — Spinning Up documentation - OpenAI
- [imgeorgiev.com](http://www.imgeorgiev.com/2023-06-27-sac/) - Deriving Soft Actor Critic (SAC)
- [chrishoffmann.dev](https://chrishoffmann.dev/post/soft_actor_critic/) - Soft Actor-Critic | Chris Hoffmann
- [lilianweng.github.io](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/) - Policy Gradient Algorithms - Lil'Log
- [medium.com](https://medium.com/data-science/entropy-in-soft-actor-critic-part-1-92c2cd3a3515) - Entropy in Soft Actor-Critic (Part 1) | by Rafael Stekolshchik | TDS Archive | Medium
- [ai.stackexchange.com](https://ai.stackexchange.com/questions/36092/does-sac-perform-better-than-ppo-in-sample-expensive-tasks-with-discrete-action) - Does SAC perform better than PPO in sample-expensive tasks with discrete action spaces?
- [joel-baptista.github.io](https://joel-baptista.github.io/phd-weekly-report/posts/ac/) - Actor-Critic Methods: SAC and PPO | Joel's PhD Blog
- [scirp.org](https://www.scirp.org/journal/paperinformation?paperid=123401) - A Comparison of PPO, TD3 and SAC Reinforcement Algorithms for Quadruped Walking Gait Generation - SciRP.org
- [researchgate.net](https://www.researchgate.net/publication/396524928_An_Iterative_Methodology_for_Comparing_PPO_and_SAC_in_Hybrid_and_Continuous_Control_Tasks) - An Iterative Methodology for Comparing PPO and SAC in Hybrid and Continuous Control Tasks - ResearchGate
- [reddit.com](https://www.reddit.com/r/reinforcementlearning/comments/y2af2i/are_there_any_papers_or_theories_on_why_sac_is/) - Are there any papers or theories on why SAC is better for continuous control tasks than on-policy methods? : r/reinforcementlearning - Reddit
- [mathworks.com](https://www.mathworks.com/help/reinforcement-learning/ug/td3-agents.html) - Twin-Delayed Deep Deterministic (TD3) Policy Gradient Agent - MATLAB & Simulink
- [youtube.com](https://www.youtube.com/watch?v=ZhFO8EWADmY) - Mastering Continuous Robotic Control with TD3 | Twin Delayed Deep Deterministic Policy Gradients - YouTube
- [spinningup.openai.com](https://spinningup.openai.com/en/latest/algorithms/td3.html) - Twin Delayed DDPG — Spinning Up documentation - OpenAI
- [mdpi.com](https://www.mdpi.com/2218-6581/14/6/76) - Guided Reinforcement Learning with Twin Delayed Deep Deterministic Policy Gradient for a Rotary Flexible-Link System - MDPI
- [medium.com](https://medium.com/@heyamit10/twin-delayed-deep-deterministic-policy-gradient-td3-fc8e9950f029) - Twin Delayed Deep Deterministic Policy Gradient (TD3) | by Hey Amit - Medium
- [upgrad.com](https://www.upgrad.com/tutorials/ai-ml/machine-learning-tutorial/ddpg-in-reinforcement-learning/) - DDPG in Reinforcement Learning for Continuous Control - upGrad
- [medium.com](https://medium.com/@kdk199604/td3-overcoming-overestimation-in-deep-reinforcement-learning-c52d1cc9d69a) - TD3: Overcoming Overestimation in Deep Reinforcement Learning | by Dong-Keon Kim
- [arxiv.org](https://arxiv.org/pdf/1509.02971) - Continuous control with deep reinforce - arXiv
- [mathworks.com](https://www.mathworks.com/matlabcentral/answers/496825-ddpg-agent-not-stabilizing-creating-an-unstable-model) - DDPG Agent: Not stabilizing creating an unstable model - MATLAB Answers - MathWorks
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12650239/) - A Two-Stage Reinforcement Learning Framework for Humanoid Robot Sitting and Standing-Up - PubMed Central
- [ri.cmu.edu](https://www.ri.cmu.edu/pub_files/2013/7/Kober_IJRR_2013.pdf) - Reinforcement Learning in Robotics: A Survey
- [arxiv.org](https://arxiv.org/html/2502.20168v1) - Accelerating Model-Based Reinforcement Learning with State-Space World Models - arXiv
- [eringrant.github.io](https://eringrant.github.io/spirl/2019/camera-ready/spirl_camera-ready_23.pdf) - STRUCTURED MECHANICAL MODELS FOR EFFICIENT REINFORCEMENT LEARNING - Erin Grant
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/10160211/10160212/10161548.pdf) - Safe Reinforcement Learning of Dynamic High-Dimensional Robotic Tasks: Navigation, Manipulation, Interaction - IEEE Xplore
- [mdpi.com](https://www.mdpi.com/1424-8220/23/7/3762) - A Survey on Deep Reinforcement Learning Algorithms for Robotic Manipulation - MDPI
- [arxiv.org](https://arxiv.org/html/2506.17518v1) - A Survey of State Representation Learning for Deep Reinforcement Learning - arXiv
- [arxiv.org](https://arxiv.org/html/2506.13498v1) - A Survey on Imitation Learning for Contact-Rich Tasks in Robotics - arXiv
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/7083369/7339444/09812508.pdf) - Variable Impedance Skill Learning for Contact-Rich Manipulation - IEEE Xplore
- [purl.stanford.edu](https://purl.stanford.edu/sh608vx1165) - Methods for contact-rich robot manipulation - Stanford Digital Repository
- [arxiv.org](https://arxiv.org/html/2506.16685v4) - Compliant Residual DAgger: Improving Real-World Contact-Rich Manipulation with Human Corrections - arXiv
- [roboticsconference.org](https://roboticsconference.org/2020/program/papers/23.html) - Controlling Contact-Rich Manipulation Under Partial Observability · Robotics
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss16/p023.pdf) - Controlling Contact-Rich Manipulation Under Partial Observability - Robotics
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/158946/suh-hjsuh-phd-eecs-2025-thesis.pdf?sequence=-1&isAllowed=y) - Leveraging Structure for Efficient and Dexterous Contact-Rich Manipulation - DSpace@MIT
- [proceedings.mlr.press](http://proceedings.mlr.press/v120/lambert20a/lambert20a.pdf) - Objective Mismatch in Model-based Reinforcement Learning
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss21/p053.pdf) - Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization - Robotics
- [hitl-robot-learning.github.io](https://hitl-robot-learning.github.io/pdfs/compliant.pdf) - Compliant Residual DAgger: Improving Real-World Contact-Rich Manipulation with Human Corrections
- [dausy.poliba.it](http://dausy.poliba.it/phd/wp-content/uploads/scheda_PNRR118_16.pdf) - REINFORCEMENT LEARNING ALGORITHMS FOR CONTACT-RICH MANIPULATION TASKS Project description The automatization of manufacturing pr - DAUSY
- [arxiv.org](https://arxiv.org/html/2412.09743v1) - Should We Learn Contact-Rich Manipulation Policies from Sampling-Based Planners? - arXiv

### 奖励函数塑造与课程学习的逻辑重构

我正在针对灵巧操作中的任务定义进行深度解构，尤其是如何通过奖励塑造（Reward Shaping）解决 In-hand Manipulation 中的 finger gaiting 等高难度动作。稀疏奖励虽然具备物理真理性，但在高维空间中面临严重的样本效率挑战。我正致力于合成一种基于 Curriculum Learning 的方案，通过类似自动领域随机化（Automatic Domain Randomization）的机制动态调整环境难度，使策略能够从基础的姿态保持逐步演进到复杂的重新定向任务。

### 多模态感知融合下的表征稳定性

我正在深入研究跨模态表征学习，以解决灵巧操作中普遍存在的局部可观测性（Partial Observability）问题。当手指遮挡视觉特征时，集成触觉传感（Tactile Sensing）成为维持状态估计稳定的关键。我正探究如何利用 Graph Neural Networks (GNN) 处理非结构化的触觉图像，并将其与 Visuomotor 策略进行融合。这种多模态表征不仅能捕捉接触点的瞬态变化，还能增强策略在处理不同材质物体时的泛化能力。

### 前沿架构演进与内核算法实现

下一步，我将探索 Diffusion Policies 和 Offline RL 在灵巧操作领域的应用潜力，思考如何利用保守 Q 学习（Conservative Q-Learning）从次优数据中提取高性能策略。同时，我将专注于提取 SAC 算法中重参数化技巧（Reparameterization Trick）的核心逻辑，并对约束流形（Constraint Manifold）的投影公式进行严格的数学形式化。这些努力旨在构建一个既有深度理论支撑、又具备核心代码逻辑的严谨知识库。

#### 研究网站 / Researched Websites

- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.799893/full) - Robot Learning From Randomized Simulations: A Review - Frontiers
- [medium.com](https://medium.com/@kdk199604/adr-train-hard-transfer-smart-bad19432c3b9) - ADR: Train Hard, Transfer Smart. Learned domain randomization selects… | by Dong-Keon Kim | Medium
- [lilianweng.github.io](https://lilianweng.github.io/posts/2019-05-05-domain-randomization/) - Domain Randomization for Sim2Real Transfer | Lil'Log
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss15/p29.pdf) - BayesSim: adaptive domain randomization via probabilistic inference for robotics simulators
- [arxiv.org](https://arxiv.org/abs/1906.01728) - [1906.01728] BayesSim: adaptive domain randomization via probabilistic inference for robotics simulators - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11963968/) - Curriculum is more influential than haptic feedback when learning object manipulation - PMC - PubMed Central
- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2024.1455431/full) - Survey of learning-based approaches for robotic in-hand manipulation - Frontiers
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/143155/Chen-taochen-SM-EECS-2022-thesis.pdf?sequence=1&isAllowed=y) - A System for General In-Hand Object Re-Orientation Tao Chen - DSpace@MIT
- [taochenshh.github.io](https://taochenshh.github.io/projects/visual-dexterity) - Visual Dexterity: In-Hand Reorientation of Novel and Complex Object Shapes - Tao Chen
- [arxiv.org](https://arxiv.org/html/2506.11775v2) - ExoStart: Efficient learning for dexterous manipulation with sensorized exoskeleton demonstrations - arXiv
- [openreview.net](https://openreview.net/forum?id=Vl0SOQWJ6Y) - Attention-Based Reward Shaping for Sparse and Delayed Rewards - OpenReview
- [papers.neurips.cc](http://papers.neurips.cc/paper/9225-keeping-your-distance-solving-sparse-reward-tasks-using-self-balancing-shaped-rewards.pdf) - Keeping Your Distance: Solving Sparse Reward Tasks Using Self-Balancing Shaped Rewards - NIPS
- [arxiv.org](https://arxiv.org/html/2408.10215v1) - Comprehensive Overview of Reward Engineering and Shaping in Advancing Reinforcement Learning Applications - arXiv
- [emergentmind.com](https://www.emergentmind.com/topics/dense-reward-functions) - Dense Reward Functions in RL - Emergent Mind
- [ai.stackexchange.com](https://ai.stackexchange.com/questions/23012/what-are-the-pros-and-cons-of-sparse-and-dense-rewards-in-reinforcement-learning) - What are the pros and cons of sparse and dense rewards in reinforcement learning?
- [mdpi.com](https://www.mdpi.com/2075-1702/13/7/605) - Visual–Tactile Fusion and SAC-Based Learning for Robot Peg-in-Hole Assembly in Uncertain Environments - MDPI
- [openreview.net](https://openreview.net/pdf/a9af0920a9f638eabdbd043c89fba9fdcd0b7117.pdf) - VITAS: VISUAL TACTILE SOFT FUSION CONTRASTIVE LEARNING FOR REINFORCEMENT LEARNING - OpenReview
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC3267194/) - Survey of Visual and Force/Tactile Control of Robots for Physical Interaction in Spain - NIH
- [aravindr93.github.io](https://aravindr93.github.io/assets/research/HMS_visuomotor_policy.pdf) - Learning Deep Visuomotor Policies for Dexterous Hand Manipulation - Aravind Rajeswaran
- [arxiv.org](https://arxiv.org/html/2504.02477v3) - Multimodal Fusion and Vision-Language Models: A Survey for Robot Vision - arXiv
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/document/8967938) - State Representation Learning with Robotic Priors for Partially Observable Environments
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss10/p19.pdf) - State Representation Learning in Robotics: Using Prior Knowledge about Physical Interaction
- [roboticsconference.org](https://roboticsconference.org/2020/program/papers/23.html) - Controlling Contact-Rich Manipulation Under Partial Observability · Robotics
- [researchgate.net](https://www.researchgate.net/publication/338945965_State_Representation_Learning_with_Robotic_Priors_for_Partially_Observable_Environments) - State Representation Learning with Robotic Priors for Partially Observable Environments | Request PDF - ResearchGate
- [arxiv.org](https://arxiv.org/pdf/1802.04181) - State Representation Learning for Control - arXiv
- [papers.neurips.cc](https://papers.neurips.cc/paper_files/paper/2020/file/0d2b2061826a5df3221116a5085a6052-Paper.pdf) - Conservative Q-Learning for Offline Reinforcement Learning - NeurIPS
- [openreview.net](https://openreview.net/pdf?id=VYYf6S67pQc) - Mildly Conservative Q-Learning for Offline Reinforcement Learning - OpenReview
- [offline-rl-neurips.github.io](https://offline-rl-neurips.github.io/2021/pdf/24.pdf) - Offline Reinforcement Learning with Implicit Q-Learning
- [arxiv.org](https://arxiv.org/abs/2006.04779) - [2006.04779] Conservative Q-Learning for Offline Reinforcement Learning - arXiv
- [bair.berkeley.edu](https://bair.berkeley.edu/blog/2020/12/07/offline/) - Offline Reinforcement Learning: How Conservative Algorithms Can Enable New Applications – The Berkeley Artificial Intelligence Research Blog
- [arxiv.org](https://arxiv.org/html/2502.20168v1) - Accelerating Model-Based Reinforcement Learning with State-Space World Models - arXiv
- [arxiv.org](https://arxiv.org/html/2510.18518v1) - Efficient Model-Based Reinforcement Learning for Robot Control via Online Learning - arXiv
- [openreview.net](https://openreview.net/forum?id=oBXfPyi47m) - Efficient Reinforcement Learning by Guiding World Models with Non-Curated Data | OpenReview
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12510832/) - DreamerNav: learning-based autonomous navigation in dynamic indoor environments using world models - PubMed Central
- [findingtheta.com](https://findingtheta.com/blog/the-evolution-of-imagination-a-deep-dive-into-dreamerv3-and-its-conquest-of-minecraft) - The Evolution of Imagination: A Deep Dive into DreamerV3 and its Conquest of Minecraft
- [medium.com](https://medium.com/data-science/soft-actor-critic-demystified-b8427df61665) - Soft Actor-Critic Demystified. An intuitive explanation of the theory… | by Vaishak V.Kumar | TDS Archive | Medium
- [emergentmind.com](https://www.emergentmind.com/topics/soft-actor-critic-implementation) - Soft Actor-Critic (SAC) Implementation - Emergent Mind
- [docs.cleanrl.dev](https://docs.cleanrl.dev/rl-algorithms/sac/) - Soft Actor-Critic (SAC) - CleanRL
- [youtube.com](https://www.youtube.com/watch?v=ioidsRlf79o) - Soft Actor Critic is Easy in PyTorch | Complete Deep Reinforcement Learning Tutorial
- [github.com](https://github.com/pranz24/pytorch-soft-actor-critic) - PyTorch implementation of soft actor critic - GitHub

### 扩散策略与强化学习的范式融合

我正在深度评估 Diffusion Policies 在灵巧操作领域引发的技术变革。这种生成式建模方法在处理多模态动作分布时展现出了超越传统策略梯度方法的潜力。通过审视 2023 至 2025 年间的前沿进展，我正试图厘清这种架构如何通过学习复杂的向量场来捕捉接触力学的细微变化，以及它在 Reinforcement Learning 框架中是作为独立的 Policy 还是作为辅助采样器来增强策略的表达能力。

### 策略熵自动调节的对偶梯度下降逻辑

为了确保算法实现的严谨性，我正在对 SAC 算法中温度参数的自动调节机制进行数学重构。这并非简单的参数搜索，而是在约束优化框架下利用 Dual Gradient Descent 实现的动态平衡。我正致力于提取其 Reparameterization Trick 的核心数学逻辑，确保在处理具有高度非线性特征的 Contact-rich 任务时，算法能够通过精确的熵正则化维持探索的深度，从而解决灵巧手在高维状态空间中容易陷入局部最优的顽疾。

### 触觉图表征建模与流形投影的最终闭环

接下来的重点将聚焦于触觉表征的深度对比，特别是评估 Graph Neural Networks 在处理非结构化触觉数据时相较于传统图像表征的 Value-add。我计划对 Contact Manifold 的投影算子进行严格的数学形式化推导，确保控制动作能始终保持在物理合法的切空间内。这些深入的分析将直接转化为核心算法逻辑，从而完成从几何直觉到数学定义、再到高性能代码实现的完整知识体系构建。

#### 研究网站 / Researched Websites

- [openreview.net](https://openreview.net/forum?id=GqsXp43EPB) - Toward Autonomous Dexterous Manipulation using Diffusion Policies with a Humanoid Robot | OpenReview
- [unidexfpm.github.io](https://unidexfpm.github.io/unidexfpm.pdf) - Dexterous Functional Pre-Grasp Manipulation with Diffusion Policy
- [mdpi.com](https://www.mdpi.com/2227-7390/13/22/3585) - Progressive Policy Learning: A Hierarchical Framework for Dexterous Bimanual Manipulation - MDPI
- [arxiv.org](https://arxiv.org/html/2504.03515v1) - Dexterous Manipulation through Imitation Learning: A Survey - arXiv
- [openaccess.thecvf.com](https://openaccess.thecvf.com/content/CVPR2025/papers/Liang_DexHandDiff_Interaction-aware_Diffusion_Planning_for_Adaptive_Dexterous_Manipulation_CVPR_2025_paper.pdf) - DexHandDiff: Interaction-aware Diffusion Planning for Adaptive Dexterous Manipulation - CVF Open Access
- [spinningup.openai.com](https://spinningup.openai.com/en/latest/algorithms/sac.html) - Soft Actor-Critic — Spinning Up documentation - OpenAI
- [medium.com](https://medium.com/@abatrek059/soft-actor-critic-sac-for-forex-trading-an-example-implementation-11c679b80f32) - Soft-Actor-Critic (SAC) for Forex Trading: An example implementation - Medium
- [automl.org](https://www.automl.org/wp-content/uploads/2020/07/AutoML_2020_paper_47.pdf) - Meta-SAC: Auto-tune the Entropy Temperature of Soft Actor-Critic via Metagradient - AutoML.org
- [imgeorgiev.com](http://www.imgeorgiev.com/2023-06-27-sac/) - Deriving Soft Actor Critic (SAC)
- [lilianweng.github.io](https://lilianweng.github.io/posts/2018-04-08-policy-gradient/) - Policy Gradient Algorithms - Lil'Log
- [roboticsconference.org](https://roboticsconference.org/docs/invitedtalks/park-manifoldsgeometryandrobotics.pdf) - Manifolds, Geometry, and Robotics
- [personalrobotics.cs.washington.edu](https://personalrobotics.cs.washington.edu/publications/koval2015mpf.pdf) - Pose estimation for planar contact manipulation with manifold particle filters - Personal Robotics Lab
- [ethz.ch](https://ethz.ch/content/dam/ethz/special-interest/mavt/robotics-n-intelligent-systems/rsl-dam/documents/RobotDynamics2017/RD_HS2017script.pdf) - Robot Dynamics Lecture Notes
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10383597/) - TactiGraph: An Asynchronous Graph Neural Network for Contact Angle Prediction Using Neuromorphic Vision-Based Tactile Sensing - NIH
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/6287639/10005208/10274715.pdf) - Graph Learning in Robotics: A Survey - IEEE Xplore
- [arxiv.org](https://arxiv.org/html/2408.11537v1) - A Survey of Embodied Learning for Object-Centric Robotic Manipulation - arXiv
- [livrepository.liverpool.ac.uk](https://livrepository.liverpool.ac.uk/3179852/1/201290032_Mar2024.pdf) - Touching the World from Known to Unknown: Tactile Representation Learning for Robotic Perception - The University of Liverpool Repository
- [arxiv.org](https://arxiv.org/html/2510.10804v1) - Representing Data in Robotic Tactile Perception - A Review - arXiv

### 黎曼几何下的切空间策略平移

我正在深化对几何强化学习（Geometric RL）的数学理解，特别是如何超越静态流形约束，引入 Riemannian Geometry 中的 Parallel Transport 机制。通过在局部切空间（Local Tangent Space）之间进行策略平移，我发现可以显著降低灵巧手在连续变换接触点时的线性近似误差。这种方法为处理非欧几里得空间中的 Orientation 和 Stiffness 数据提供了严谨的数学支点，使策略在复杂的物理流形上具备更强的泛化性能。

### 领域随机化理论中的记忆增强效应

我正通过数学证明审视 Domain Randomization (DR) 的有效性边界。最新的理论分析表明，在 Sim-to-Real 过程中，具备记忆能力的 History-dependent Policies 是减小跨域差距（Sim-to-Real Gap）的关键。这证明了策略并非仅在学习静态映射，而是在利用历史观测序列隐式地推断环境的潜变量。这一发现解决了纯随机化在复杂接触动力学中鲁棒性不足的矛盾，为实现零样本迁移（Zero-shot Transfer）提供了坚实的理论支撑。

### 算法逻辑提取与物理仿真的最终集成

我接下来的思考将聚焦于整合 SAC 算法中 Reparameterization Trick 的核心代码逻辑，并结合 Generalized Coordinates 完善物理仿真中的接触建模描述。我计划通过对比 SimOpt 等轨迹差异最小化方法与 CITO（接触隐式轨迹优化）的 Value-add，完成从几何直觉到高性能代码实现的完整知识体系构建，并最终输出为 Obsidian 知识库中的严谨教程。


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*