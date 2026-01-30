# Deep Research Conversation

**导出时间 / Exported At:** 2026-01-29 15:38:17

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 确立信息论在灵巧操作中的核心地位

我正在构建一个深度研究框架，旨在探讨信息论如何从根本上改变机器人灵巧操作中的感知与探索方式。相比于传统的被动观察，我正着眼于将信息熵、互信息和KL散度等数学工具转化为机器人理解物体几何形状、摩擦力及姿态的不确定性度量。通过将感知视为一个主动寻求降低不确定性的过程，我试图揭示如何从物理交互中最大化获取有价值的信息。

### 审视主动感知的演进脉络与技术瓶颈

我正在深入思考感知范式的演进——从简单的启发式探索转向基于信息增益的决策逻辑。过去的方法在面对高维状态空间和复杂接触动力学时往往失效，因此我需要厘清“最佳触碰”策略如何利用高斯过程和粒子滤波来动态调整探索轨迹。我将重点分析为何在灵巧操作中，触觉反馈中的信息量化是解决操作任务不确定性的关键价值所在。

### 探索强化学习中的内在动机与算法实现

接下来的行动中，我将重点研究如何将内在动机和好奇心驱动的机制引入强化学习，以解决灵巧操作中奖励极度稀疏的难题。我正准备梳理期望信息增益的具体计算逻辑，并探讨其在广义坐标系下的数值实现。此外，我还会评估实时性要求与计算复杂度之间的矛盾，以及从模拟环境到现实物理世界迁移时的信息保真度挑战，从而为后续的核心算法解析奠定坚实基础。

#### 研究网站 / Researched Websites

- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2025.1606247/full) - Diffusion models for robotic manipulation: a survey - Frontiers
- [cs.stanford.edu](https://cs.stanford.edu/~quocle/activevision.pdf) - Active Perception: Interactive Manipulation for Improving Object Detection - Stanford Computer Science
- [merl.com](https://www.merl.com/publications/docs/TR2022-139.pdf) - Active Exploration for Robotic Manipulation - Mitsubishi Electric Research Laboratories
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC6954017/) - Revisiting active perception - PMC - PubMed Central
- [arxiv.org](https://arxiv.org/html/2601.13639v1) - A General One-Shot Multimodal Active Perception Framework for Robotic Manipulation: Learning to Predict Optimal Viewpoint - arXiv
- [towardsdatascience.com](https://towardsdatascience.com/understanding-kl-divergence-entropy-and-related-concepts-75e766a2fd9e/) - Understanding KL Divergence, Entropy, and Related Concepts | Towards Data Science
- [ra1ndeer.github.io](https://ra1ndeer.github.io/posts/primer_info_theory.html) - A Primer on Entropy, Kullback-Leibler Divergence and Mutual Information | Project Iceberg
- [medium.com](https://medium.com/@jacowp357/entropy-kl-divergence-cross-entropy-and-mutual-information-519075a2e3fa) - Entropy, KL divergence, Cross-entropy, and Mutual information | by Jaco du Toit - Medium
- [pages.cs.wisc.edu](https://pages.cs.wisc.edu/~jerryzhu/cs769/info.pdf) - Information Theory 1 Entropy 2 Mutual Information - cs.wisc.edu
- [tungmphung.com](https://tungmphung.com/information-theory-concepts-entropy-mutual-information-kl-divergence-and-more/) - Information Theory concepts: Entropy, Mutual Information, KL-Divergence, and more
- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.993359/full) - Bayesian optimization with unknown constraints in graphical skill models for compliant manipulation tasks using an industrial robot - Frontiers
- [arxiv.org](https://arxiv.org/html/2507.05522v1) - Gaussian Process-Based Active Exploration Strategies in Vision and Touch - arXiv
- [users.cs.utah.edu](https://users.cs.utah.edu/~thermans/papers/yi-iros2016-gp-active-touch.pdf) - Active Tactile Object Exploration with Gaussian Processes
- [alonsomarco.me](https://alonsomarco.me/project/auto_tuning_bayesian/) - Controller Learning using Bayesian Optimization - Alonso Marco
- [arxiv.org](https://arxiv.org/html/2410.04680v2) - Next Best Sense: Guiding Vision and Touch with FisherRF for 3D Gaussian Splatting - arXiv
- [medium.com](https://medium.com/biased-algorithms/curiosity-driven-exploration-in-reinforcement-learning-dd3f7d263fce) - Curiosity-Driven Exploration in Reinforcement Learning | by Amit Yadav | Biased-Algorithms
- [cambridge.org](https://www.cambridge.org/core/books/drive-for-knowledge/curiositydriven-exploration/D545C1583CE3E0765BB9E5F6C5766268) - Curiosity-Driven Exploration (Chapter 3) - The Drive for Knowledge
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/document/8961529/) - Curiosity-Driven Exploration for Off-Policy Reinforcement Learning Methods - IEEE Xplore
- [youtube.com](https://www.youtube.com/watch?v=Qob2k_ldLuw) - Curiosity-Driven Learning of Joint Locomotion and Manipulation Tasks - YouTube
- [arxiv.org](https://arxiv.org/abs/1903.08542) - [1903.08542] Learning Gentle Object Manipulation with Curiosity-Driven Deep Reinforcement Learning - arXiv
- [mdpi.com](https://www.mdpi.com/1099-4300/22/2/258) - Gaussian Process Based Expected Information Gain Computation for Bayesian Optimal Design - MDPI
- [rpg.ifi.uzh.ch](https://rpg.ifi.uzh.ch/docs/ICRA16_Isler.pdf) - An Information Gain Formulation for Active Volumetric 3D Reconstruction - Robotics and Perception Group
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss01/p09.pdf) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters - Robotics
- [en.wikipedia.org](https://en.wikipedia.org/wiki/Information_gain_(decision_tree)) - Information gain (decision tree) - Wikipedia
- [eems.mit.edu](https://eems.mit.edu/wp-content/uploads/2020/03/2020_icra_fcmi.pdf) - An Efficient and Continuous Approach to Information-Theoretic Exploration

### 触觉感知与几何不确定性的物理映射

我正在将抽象的信息论指标转化为具体的物理交互逻辑。通过分析最新的触觉探索算法，我发现利用 Gaussian Process (GP) 对物体表面进行隐式建模，能有效地将局部触碰转化为全局几何形状的置信度更新。特别是 Fisher Information 在视觉与触觉多模态融合中的应用，为机器人提供了从被动接收转向主动探测的数学依据，这对于在遮挡环境下保持灵巧操作的稳定性至关重要。

### 实时感知与高维优化的效能博弈

在评估主动感知框架时，我注意到一个关键的矛盾：虽然贪婪最大化 Mutual Information (MI) 显著提升了目标检测的鲁棒性，但其高昂的计算开销限制了在高动态操作中的实时应用。我正深入思考如何利用信息搜索型 MPC（Model Predictive Control）在稀疏奖励环境下，通过建模 Epistemic Uncertainty 来平衡探索广度与执行精度。这种从迭代优化向预测性框架的转型，是解决实时几何更新瓶颈的核心路径。

### 构建高维空间下的信息采样与赋能逻辑

我接下来的行动将聚焦于高维 Generalized Coordinates 下 Expected Information Gain (EIG) 的具体数值实现。我计划梳理一套基于采样的计算逻辑，并探讨 Empowerment 概念如何引导多自由度灵巧手发现潜在的物理交互模式。此外，我将重点剖析信息度量在 Sim-to-Real 迁移中的保真度问题，确保在模拟器中最小化的熵能真实转化为现实世界中操作成功率的提升。

#### 研究网站 / Researched Websites

- [cvg.cit.tum.de](https://cvg.cit.tum.de/_media/spezial/bib/sturm11phd.pdf) - Approaches to Probabilistic Model Learning for Mobile Manipulation Robots (PhD Thesis) - Computer Vision Group
- [argmin.lis.tu-berlin.de](https://argmin.lis.tu-berlin.de/papers/19-driess-ICRA.pdf) - Active Multi-Contact Continuous Tactile Exploration with Gaussian Process Differential Entropy - Learning and Intelligent Systems @ TU Berlin
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC6140341/) - Ergodic Exploration Using Binary Sensing for Nonparametric Shape Estimation - PMC - NIH
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2019/03/Kroemer_Chebotar_IROS_2014.pdf) - Learning Robot Tactile Sensing for Object Manipulation
- [arxiv.org](https://arxiv.org/pdf/2403.13701?) - What Matters for Active Texture Recognition With Vision-Based Tactile Sensors - arXiv
- [arxiv.org](https://arxiv.org/html/2507.05522v1) - Gaussian Process-Based Active Exploration Strategies in Vision and Touch - arXiv
- [users.cs.utah.edu](https://users.cs.utah.edu/~thermans/papers/yi-iros2016-gp-active-touch.pdf) - Active Tactile Object Exploration with Gaussian Processes
- [arxiv.org](https://arxiv.org/html/2403.09875v3) - Touch-GS: Visual-Tactile Supervised 3D Gaussian Splatting - arXiv
- [cs.cmu.edu](https://www.cs.cmu.edu/~kaess/pub/Suresh22icra.pdf) - ShapeMap 3-D: Efficient shape mapping through dense touch and vision
- [h2t.iar.kit.edu](https://h2t.iar.kit.edu/pdf/Ottenhaus2019.pdf) - Visuo-Haptic Grasping of Unknown Objects based on Gaussian Process Implicit Surfaces and Deep Learning - High Performance Humanoid Technologies (H²T)
- [arxiv.org](https://arxiv.org/html/2601.10276v1) - How Intrinsic Motivation Underlies Embodied Open-Ended Behavior - arXiv
- [arxiv.org](https://arxiv.org/pdf/2601.10276) - How Intrinsic Motivation Underlies Embodied Open-Ended Behavior - arXiv
- [medium.com](https://medium.com/data-science/empowerment-as-intrinsic-motivation-b84af36d5616) - Empowerment as Intrinsic Motivation | by Chris Marais | TDS Archive - Medium
- [henrycharlesworth.com](https://www.henrycharlesworth.com/research.html) - Research - Henry Charlesworth's
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/151079/10514_2023_Article_10087.pdf?sequence=1&isAllowed=y) - An empowerment-based solution to robotic manipulation tasks with sparse rewards - DSpace@MIT
- [researchgate.net](https://www.researchgate.net/publication/275461463_Sampling-based_robotic_information_gathering_algorithms) - Sampling-based robotic information gathering algorithms - ResearchGate
- [stackoverflow.com](https://stackoverflow.com/questions/46752650/information-gain-calculation-with-scikit-learn) - Information Gain calculation with Scikit-learn - python - Stack Overflow
- [ir.library.oregonstate.edu](https://ir.library.oregonstate.edu/downloads/gq67jt01h) - Sampling-based robotic information gathering algorithms - Oregon State University
- [github.com](https://github.com/ethz-asl/cvae_exploration_planning) - ethz-asl/cvae_exploration_planning: Learning informed sampling distributions and information gains for efficient exploration planning. - GitHub
- [autonomousrobots.nl](https://autonomousrobots.nl/assets/files/publications/22-lodel-icra.pdf) - Where to Look Next: Learning Viewpoint Recommendations for Informative Trajectory Planning - Autonomous Multi-Robots Lab
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/8fa068ffe59817175d176bd75641fe16-Paper-Conference.pdf) - Overcoming the Sim-to-Real Gap: Leveraging Simulation to Learn to Explore for Real-World RL - NIPS
- [reinforcementlearningpath.com](https://www.reinforcementlearningpath.com/sim2real) - SIM2REAL: How to Reduce the Reality Gap in Robotics - Reinforcement Learning Path
- [arxiv.org](https://arxiv.org/html/2410.20254v1) - Overcoming the Sim-to-Real Gap: Leveraging Simulation to Learn to Explore for Real-World RL - arXiv
- [research.google](https://research.google/blog/closing-the-simulation-to-reality-gap-for-deep-robotic-learning/) - Closing the Simulation-to-Reality Gap for Deep Robotic Learning - Google Research
- [openreview.net](https://openreview.net/forum?id=Bq4XOaU4sV&noteId=ArIwKiOmst) - Bridging the Sim-to-Real Gap from the Information Bottleneck Perspective - OpenReview
- [arxiv.org](https://arxiv.org/html/2312.00215v1) - Learning active tactile perception through belief-space control - arXiv
- [indelman.github.io](https://indelman.github.io/ANPL-Website/Publications/Pathak16ecai.pdf) - DA-BSP: Towards Data Association Aware Belief Space Planning for Robust Active Perception - GitHub Pages
- [lis.csail.mit.edu](https://lis.csail.mit.edu/pubs/tlp/IJRRBelFinal.pdf) - Integrated task and motion planning in belief space - Learning and Intelligent Systems Group
- [arxiv.org](https://arxiv.org/html/2504.03245v1) - Seeing is Believing: Belief-Space Planning with Foundation Models as Uncertainty Estimators - arXiv
- [opus.lib.uts.edu.au](https://opus.lib.uts.edu.au/bitstream/10453/187551/1/thesis.pdf) - Reduced latent belief spaces for active perception in robotics - OPUS at UTS

### 触觉建模中高斯过程隐式表面的数学具象化

我正深入剖析 Gaussian Process Implicit Surfaces (GPIS) 的数学机理。相比于此前对不确定性的宏观定义，我发现通过建模触碰概率 $P(z|x)$ 并计算其微分熵，能将抽象的信息论指标直接转化为灵巧手对物体边缘进行精细化探测的物理准则。这种从“模糊感知”到“显式几何置信度更新”的数学跃迁，是实现灵巧操作中亚毫米级定位精度、克服视觉遮挡问题的关键底层逻辑。

### 破解高维空间下的互信息计算困局

在处理拥有 20 多个自由度的灵巧手时，我意识到计算 Mutual Information 的计算复杂度呈指数级增长。为了解决这一瓶颈，我正尝试引入 Variational Information Bottleneck (VIB) 和变分推断（Variational Inference）来近似求解。这种方法不仅大幅降低了评估 Empowerment 的算力成本，更通过将全局优化转化为局部变分界限的逼近，使得机器人在复杂的接触动力学中能实时捕捉最具价值的交互特征，避免了在高维 Belief Space 中迷失。

### 算法实现逻辑与跨环境一致性验证

我接下来的行动将聚焦于提炼 Expected Information Gain (EIG) 的数值实现逻辑，通过采样粒子并闭环运行物理仿真，构建一套可直接指导探索动作的代码框架。我将特别关注如何在 Simulation 中保持信息度量的保真度，防止模型过度拟合模拟环境中的理想观测值。通过优化获取函数（Acquisition Function），我旨在确保探索策略在从模拟向现实世界（Sim-to-Real）迁移时，依然能保持高效的熵减速率和操作成功率。

#### 研究网站 / Researched Websites

- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11089096/) - Safe contact-based robot active search using Bayesian optimization and control barrier functions - PMC - NIH
- [cognex.com](https://www.cognex.com/blogs/deep-learning/research/overview-bayesian-optimization-effective-hyperparameter-search-technique-deep-learning-1) - Bayesian Optimization Summary: Effective Methodology of Exploring Hyperparameters in Deep Learning Models - Blog | Cognex
- [papers.neurips.cc](https://papers.neurips.cc/paper_files/paper/2021/file/32bbf7b2bc4ed14eb1e9c2580056a989-Paper.pdf) - Scaling Gaussian Processes with Derivative Information Using Variational Inference - NeurIPS
- [researchgate.net](https://www.researchgate.net/publication/309233170_Active_Tactile_Object_Exploration_with_Gaussian_Processes) - Active Tactile Object Exploration with Gaussian Processes - ResearchGate
- [mdpi.com](https://www.mdpi.com/2218-6581/4/2/141) - DOF Decoupling Task Graph Model: Reducing the Complexity of Touch-Based Active Sensing - MDPI
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2017/05/thesis_shiyuanc.pdf) - Touch Based Localization for High-Precision Manufacturing - Carnegie Mellon University Robotics Institute
- [dcc.ufmg.br](https://www.dcc.ufmg.br/~msalvim/publications/2017-JIRS.pdf) - Information-driven Rapidly-exploring Random Tree for Efficient Environment Exploration - DCC/UFMG
- [bradsaund.com](https://www.bradsaund.com/file/IROS2017.pdf) - The Datum Particle Filter: Localization for Objects with Coupled Geometric Datums - Brad Saund
- [is.mpg.de](https://is.mpg.de/uploads/publication_attachment/attachment/307/2010_IROS_bjbk_camred.pdf) - Strategies for Multi-Modal Scene Exploration - Max Planck Institute for Intelligent Systems
- [researchgate.net](https://www.researchgate.net/publication/282403663_Variational_Information_Maximisation_for_Intrinsically_Motivated_Reinforcement_Learning) - Variational Information Maximisation for Intrinsically Motivated Reinforcement Learning | Request PDF - ResearchGate
- [openreview.net](https://openreview.net/pdf?id=HJlmHoR5tQ) - ADVERSARIAL IMITATION VIA VARIATIONAL INVERSE REINFORCEMENT LEARNING - OpenReview
- [arxiv.org](https://arxiv.org/html/2403.14593v1) - Rethinking Adversarial Inverse Reinforcement Learning: From the Angles of Policy Imitation and Transferable Reward Recovery - arXiv
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2023/file/bcf26768143c94bd36e363cd4bf5daf0-Paper-Conference.pdf) - Ess-InfoGAIL: Semi-supervised Imitation Learning from Imbalanced Demonstrations - NeurIPS
- [ojs.aaai.org](https://ojs.aaai.org/index.php/AAAI/article/view/29019/29933) - DGPO: Discovering Multiple Strategies with Diversity-Guided Policy Optimization
- [scispace.com](https://scispace.com/pdf/approximation-of-empowerment-in-the-continuous-domain-50a4vcwi4s.pdf) - Approximation of empowerment in the continuous domain - SciSpace
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/144824/dai-sylviad-phd-meche-2022-thesis.pdf?sequence=1&isAllowed=y) - Learning to Make Decisions in Robotic Manipulation - DSpace@MIT
- [alphaxiv.org](https://www.alphaxiv.org/overview/1310.1863v2) - Empowerment -- an Introduction | alphaXiv
- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2017.00025/full) - Empowerment As Replacement for the Three Laws of Robotics - Frontiers
- [arxiv.org](https://arxiv.org/html/2501.01539v1) - In Search of a Lost Metric: Human Empowerment as a Pillar of Socially Conscious Navigation - arXiv
- [lucris.lub.lu.se](https://lucris.lub.lu.se/ws/files/3352295/4407278.pdf) - Particle Filtering and Optimal Control for Vehicles and Robots Berntorp, Karl - Lucris
- [tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/01691864.2023.2225175) - Active exploration based on information gain by particle filter for efficient spatial concept formation - Taylor & Francis
- [ai.stanford.edu](https://ai.stanford.edu/~gabeh/papers/Hoffmann_ParticleMutualInfo_CDC06.pdf) - Mutual Information Methods with Particle Filters for Mobile Sensor Network Control - Stanford AI Lab
- [ri.cmu.edu](https://www.ri.cmu.edu/app/uploads/2021/08/thesis.pdf) - Mutual Information Maps for Single and Multi-Target Ergodic Search - Carnegie Mellon University Robotics Institute
- [frontiersin.org](https://www.frontiersin.org/journals/robotics-and-ai/articles/10.3389/frobt.2022.950427/full) - Improved weighting in particle filters applied to precise state estimation in GNSS - Frontiers
- [users.cs.utah.edu](https://users.cs.utah.edu/~thermans/papers/yi-iros2016-gp-active-touch.pdf) - Active Tactile Object Exploration with Gaussian Processes

### 粒子滤波与期望信息增益的算法闭环

我正在将抽象的 Expected Information Gain (EIG) 转化为可执行的数值计算逻辑。通过深入分析 Rao-Blackwellized Particle Filter，我发现利用粒子集合表征物体状态的 Belief 分布，可以有效解决非线性接触动力学中的熵减量化问题。我正在提炼一种采样算法，旨在通过模拟未来可能的观测序列，预估动作对 Mutual Information 的贡献。这种方法成功将信息论的顶层设计降维至可操作的离散候选动作评估，为灵巧操作中的主动路径规划提供了数学闭环。

### 高维自由度下赋能计算的架构突破

在处理拥有 20 多个自由度的灵巧手时，我意识到传统的 Empowerment 评估面临严重的计算瓶颈。为了应对这一挑战，我正在研究 Variational Information Maximization 的神经网络实现，特别是借鉴 DIAYN 等算法中的 Discriminator 架构。我发现，通过学习一个能够区分不同技能或动作序列的变分下界，可以在不直接求解复杂积分的情况下，引导灵巧手发现具有物理意义的交互模式。这种从全局优化向变分推理的转型，是解决高维 Generalized Coordinates 下自主探索的核心关键。

### 触觉传感器物理建模与感知模型构建

我接下来的行动将聚焦于构建更具物理真实性的触觉感知模型，通过对比 Bernoulli 和 Gaussian 分布在描述“触碰-脱离”事件中的信息捕获效能，确立最适合灵巧操作的似然函数 $P(z|x)$。我将整理出一套完整的 EIG 计算流程，并重点剖析 Sim-to-Real 迁移中因软体形变和传感噪声导致的信息增益偏差。我的目标是建立一套能够处理非刚性物体且具备抗噪能力的探索框架，确保机器人在真实环境中的每一次触碰都能获得最大的物理启发价值。

#### 研究网站 / Researched Websites

- [nowpublishers.com](https://www.nowpublishers.com/article/DownloadSummary/ROB-013) - Particle Filters for Robot Navigation
- [autonomousrobots.nl](https://autonomousrobots.nl/assets/files/publications/22-lodel-icra.pdf) - Where to Look Next: Learning Viewpoint Recommendations for Informative Trajectory Planning - Autonomous Multi-Robots Lab
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss01/p09.pdf) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters - Robotics
- [eems.mit.edu](https://eems.mit.edu/wp-content/uploads/2020/03/2020_icra_fcmi.pdf) - An Efficient and Continuous Approach to Information-Theoretic Exploration
- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2023/file/bcf26768143c94bd36e363cd4bf5daf0-Paper-Conference.pdf) - Ess-InfoGAIL: Semi-supervised Imitation Learning from Imbalanced Demonstrations - NeurIPS
- [ideals.illinois.edu](https://www.ideals.illinois.edu/items/123274/bitstreams/406065/data.pdf) - © 2021 Tanmay Gangwani - IDEALS
- [citeme.ai](https://www.citeme.ai/trajectories.html) - CiteAgent Trajectories - CiteME
- [bayesiandeeplearning.org](https://bayesiandeeplearning.org/2017/papers/11.pdf) - Variational Deep Q Network
- [scribd.com](https://www.scribd.com/document/689669503/Deep-Reinforcement-Learning) - Deep Reinforcement Learning | PDF | Applied Mathematics - Scribd
- [github.com](https://github.com/Egiob/DiversityIsAllYouNeed-SB3) - Egiob/DiversityIsAllYouNeed-SB3: Implementation of Diversity Is All You Need (DIAYN) on top of Stable Baselines 3. - GitHub
- [github.com](https://github.com/alirezakazemipour/DIAYN-PyTorch) - alirezakazemipour/DIAYN-PyTorch: Diversity is All You Need - GitHub
- [reddit.com](https://www.reddit.com/r/reinforcementlearning/comments/fjx8t1/diversity_is_all_you_need_learning_skills/) - 'Diversity is all you need: learning skills' implementation with a hardcoded Discriminator : r/reinforcementlearning - Reddit
- [openreview.net](https://openreview.net/pdf?id=H1eRBoC9FX) - UNSUPERVISED META-LEARNING FOR REINFORCEMENT LEARNING - OpenReview
- [remydeshayes.github.io](https://remydeshayes.github.io/assets/papers/rl_dyan_website.pdf) - Reinforcement Learning : Final Project - Rémy Deshayes
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC12321859/) - A hybrid elastic-hyperelastic approach for simulating soft tactile sensors - PMC - NIH
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/8860/4359257/10054516.pdf) - Simulation, Learning, and Application of Vision-Based Tactile Sensing at Large Scale - IEEE Xplore
- [arxiv.org](https://arxiv.org/html/2510.25405v1) - Sim-to-Real Gentle Manipulation of Deformable and Fragile Objects with Stress-Guided Reinforcement Learning - arXiv
- [researchgate.net](https://www.researchgate.net/publication/383361106_Sim-to-Real_of_Soft_Robots_with_Learned_Residual_Physics) - Sim-to-Real of Soft Robots With Learned Residual Physics - ResearchGate
- [yzhu.io](https://yzhu.io/publication/tactile2025neurips/paper.pdf) - Taccel: Scaling Up Vision-based Tactile Robotics via High-performance GPU Simulation - Yixin Zhu | PKU
- [mdpi.com](https://www.mdpi.com/1424-8220/19/4/814) - Contact Modelling and Tactile Data Processing for Robot Skins - MDPI
- [researchgate.net](https://www.researchgate.net/publication/384364207_Tactile_Probabilistic_Contact_Dynamics_Estimation_of_Unknown_Objects) - Tactile Probabilistic Contact Dynamics Estimation of Unknown Objects - ResearchGate
- [merl.com](https://www.merl.com/publications/docs/TR2024-053.pdf) - Tactile Estimation of Extrinsic Contact Patch for Stable Placement - Mitsubishi Electric Research Laboratories
- [arxiv.org](https://arxiv.org/html/2408.06506v1) - TacSL: A Library for Visuotactile Sensor Simulation and Learning - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7967204/) - Vision-Based Tactile Sensor Mechanism for the Estimation of Contact Position and Force Distribution Using Deep Learning - NIH

### 粒子滤波框架下的期望信息增益数值结算

我正在通过 Rao-Blackwellized Particle Filter (RBPF) 将 Belief Space 的演化过程具象化，旨在为灵巧操作提供一套严谨的数值计算逻辑。核心突破在于利用粒子集合的分布差异来近似高维连续熵的降幅：通过模拟未来可能的观测序列，我正构建一个“预见性”的评估体系，计算动作执行后后验分布相对于先验分布的 KL Divergence。这种采样驱动的方法成功规避了在处理非线性接触动力学时，因直接求解高维积分而产生的计算爆炸问题。

### 变分赋能计算与判别器架构的融合

在探索高维 Generalized Coordinates 的自主性时，我正聚焦于 Variational Information Maximization 的网络架构实现。通过引入类似于 DIAYN 架构中的判别器（Discriminator），我正尝试将抽象的 Empowerment 转化为可优化的互信息变分下界。这种设计的物理意义在于，它允许灵巧手在没有任何外部奖励信号的情况下，仅凭感知反馈的统计特征就能自主发现具有操作价值的交互模式。我正在深究如何训练该判别器，使其在复杂的接触特征中提取出最具区分度的本征信息。

### 触觉感知的物理本质与下一步算法验证

我正在重新审视触觉传感器的物理建模逻辑，特别是将“触碰-脱离”这一离散事件建模为 Bernoulli 分布后，如何与连续场的熵计算进行有效对齐。我意识到，真实世界中的传感噪声和非刚性形变往往会导致模拟器中预估的信息增益出现“幻觉”。接下来的行动中，我将重点梳理 EIG 的具体代码实现步骤，并深入剖析 Sim-to-Real 迁移中因物理建模失真导致的信息保真度下降问题，以确立一套能够处理软体接触且具备抗噪能力的探索框架。

#### 研究网站 / Researched Websites

- [nowpublishers.com](https://www.nowpublishers.com/article/DownloadSummary/ROB-013) - Particle Filters for Robot Navigation
- [medium.com](https://medium.com/@mathiasmantelli/particle-filter-part-2-intuitive-example-and-equations-0716223b862b) - Particle Filter Part 2 — Intuitive example and equations | by Mathias Mantelli | Medium
- [web.mit.edu](https://web.mit.edu/16.412j/www/html/Advanced%20lectures/Slides/Hsaio_plinval_miller_ParticleFiltersPrint.pdf) - Particle Filters and Their Applications - MIT
- [cs.ubc.ca](https://www.cs.ubc.ca/~murphyk/Papers/rbpf_uai00.pdf) - Rao-Blackwellised Particle Filtering for Dynamic Bayesian Networks - UBC Computer Science
- [papers.neurips.cc](http://papers.neurips.cc/paper/5668-variational-information-maximisation-for-intrinsically-motivated-reinforcement-learning.pdf) - Variational Information Maximisation for Intrinsically Motivated Reinforcement Learning - NIPS
- [ijcai.org](https://www.ijcai.org/proceedings/2021/0316.pdf) - Variational Model-based Policy Optimization - IJCAI
- [anuj-mahajan.github.io](https://anuj-mahajan.github.io/files/virel.pdf) - VIREL: A Variational Inference Framework for Reinforcement Learning - Anuj Mahajan
- [arxiv.org](https://arxiv.org/abs/1605.09674) - [1605.09674] VIME: Variational Information Maximizing Exploration - arXiv
- [reddit.com](https://www.reddit.com/r/MachineLearning/comments/3mxocf/variational_information_maximisation_for/) - Variational Information Maximisation for Intrinsically Motivated Reinforcement Learning : r/MachineLearning - Reddit
- [mdpi.com](https://www.mdpi.com/2072-666X/13/7/1053) - Contact Pattern Recognition of a Flexible Tactile Sensor Based on the CNN-LSTM Fusion Algorithm - MDPI
- [dannydriess.github.io](https://dannydriess.github.io/papers/19-driess-ICRA.pdf) - Active Multi-Contact Continuous Tactile Exploration with Gaussian Process Differential Entropy - Danny Driess
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7956238/) - A Vibrissa-Inspired Highly Flexible Tactile Sensor: Scanning 3D Object Surfaces Providing Tactile Images - NIH
- [arxiv.org](https://arxiv.org/html/2303.00935v3) - Learning to Detect Slip through Tactile Estimation of the Contact Force Field and its Entropy
- [merl.com](https://www.merl.com/publications/docs/TR2024-053.pdf) - Tactile Estimation of Extrinsic Contact Patch for Stable Placement - Mitsubishi Electric Research Laboratories
- [rrwiyatn.github.io](https://rrwiyatn.github.io/blog/robotik/2020/12/30/particle-filter.html) - Robotik - Ep.7: State Estimation with Particle Filter | rey's blog - democratizing robotics + ai.
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7826670/) - Particle Filters: A Hands-On Tutorial - PMC - PubMed Central
- [researchgate.net](https://www.researchgate.net/figure/Pseudo-code-for-particle-filter-algorithm_fig1_220757300) - Pseudo code for particle filter algorithm | Download Scientific Diagram - ResearchGate
- [medium.com](https://medium.com/@mathiasmantelli/particle-filter-part-4-pseudocode-and-python-code-052a74236ba4) - Particle Filter Part 4 — Pseudocode (and Python code) | by Mathias Mantelli - Medium
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss01/p09.pdf) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters - Robotics
- [tandfonline.com](https://www.tandfonline.com/doi/full/10.1080/01691864.2023.2225175) - Active exploration based on information gain by particle filter for efficient spatial concept formation - Taylor & Francis
- [cs.cmu.edu](https://www.cs.cmu.edu/~motionplanning/reading/boris-presentation.pdf) - Rao-Blackwellised Particle Filtering
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10054117/) - Rao-Blackwellized Particle Filter Algorithm Integrated with Neural Network Sensor Model Using Laser Distance Sensor - NIH
- [diva-portal.org](https://www.diva-portal.org/smash/get/diva2:412640/fulltext01.pdf) - The Rao-Blackwellized Particle Filter: A Filter Bank Implementation - DiVA portal
- [github.com](https://github.com/p-christ/Deep-Reinforcement-Learning-Algorithms-with-PyTorch/blob/master/agents/hierarchical_agents/DIAYN.py) - Deep-Reinforcement-Learning-Algorithms-with-PyTorch/agents/hierarchical_agents/DIAYN.py at master - GitHub
- [baeldung.com](https://www.baeldung.com/cs/pytorch-generative-adversarial-networks) - GAN Implementation in PyTorch | Baeldung on Computer Science
- [github.com](https://github.com/eriklindernoren/PyTorch-GAN) - eriklindernoren/PyTorch-GAN: PyTorch implementations of Generative Adversarial Networks. - GitHub
- [docs.pytorch.org](https://docs.pytorch.org/tutorials/beginner/dcgan_faces_tutorial.html) - DCGAN Tutorial — PyTorch Tutorials 2.10.0+cu130 documentation
- [argmin.lis.tu-berlin.de](https://argmin.lis.tu-berlin.de/papers/19-driess-ICRA.pdf) - Active Multi-Contact Continuous Tactile Exploration with Gaussian Process Differential Entropy - Learning and Intelligent Systems @ TU Berlin
- [arxiv.org](https://arxiv.org/html/2502.09535v6) - Entropy Collapse in Mobile Sensors: The Hidden Risks of Sensor-Based Security - arXiv
- [users.cs.utah.edu](https://users.cs.utah.edu/~thermans/papers/veiga-iros2015-slip-control.pdf) - Stabilizing Novel Objects by Learning to Predict Tactile Slip
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC8562425/) - Comparative Analysis of Model-Based Predictive Shared Control for Delayed Operation in Object Reaching and Recognition Tasks With Tactile Sensing

### 期望信息增益的数值闭环与采样优化

我已经确立了在粒子滤波中通过模拟未来观测来估算熵减的数值路径。这种方法的核心在于利用当前信念分布生成可能的感官反馈，并评估这些反馈在多大程度上能使粒子集合趋于一致。我发现，通过优化采样频率和观测似然函数，可以有效解决灵巧操作中触觉数据的稀疏性问题，使感知过程更具目的性，而不是盲目的空间探索。

### 变分框架下判别器架构的深度特化

在处理具有二十多个自由度的灵巧手时，我正专注于提炼变分信息极大化算法中的判别器逻辑。通过分析特定任务下的状态空间映射，我正在解决如何精准定义技能序列与物理反馈之间互信息的数值边界。这一突破能够让机器人在复杂的接触动力学中，通过最大化其对环境的影响力（Empowerment），自主学习到稳定抓取和旋转物体的基础物理技能，填补了高维控制与自主探索之间的鸿沟。

### 算法复杂度结算与感知保真度验证

我接下来的行动将聚焦于量化整个主动感知循环的计算开销，特别是分析粒子规模与信息增益评估精度之间的权衡关系。我将进一步核实高斯过程在描述复杂几何边缘时的微分熵计算细节，并深入剖析判别器在处理多模态输入时的架构差异。我的目标是确保最终的算法逻辑既具备深厚的数学根基，又能应对现实物理世界中由于软体形变和传感噪声带来的保真度挑战。

#### 研究网站 / Researched Websites

- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss09/p53.pdf) - Approximate Representations for Multi-Robot Control Policies that Maximize Mutual Information
- [mavmatrix.uta.edu](https://mavmatrix.uta.edu/cgi/viewcontent.cgi?article=1671&context=mechaerospace_theses) - OPTIMIZING MULTI-AGENT NETWORK FOR TARGET LOCALIZATION THROUGH MUTUAL INFORMATION MAXIMIZATION - MavMatrix
- [arxiv.org](https://arxiv.org/pdf/2403.01674) - ASPIRe: An Informative Trajectory Planner with Mutual Information Approximation for Target Search and Tracking - arXiv
- [ai.stanford.edu](https://ai.stanford.edu/~gabeh/papers/Hoffmann_ParticleMutualInfo_CDC06.pdf) - Mutual Information Methods with Particle Filters for Mobile Sensor Network Control - Stanford AI Lab
- [researchgate.net](https://www.researchgate.net/figure/Architecture-of-the-Discriminator_fig2_353023534) - Architecture of the Discriminator | Download Scientific Diagram - ResearchGate
- [researchgate.net](https://www.researchgate.net/figure/The-architecture-of-PatchGAN-discriminator_fig4_366627726) - The architecture of PatchGAN discriminator | Download Scientific Diagram - ResearchGate
- [openreview.net](https://openreview.net/pdf/8ab82acd2672b63eb1d694fcb5fc26a32c2f6d74.pdf) - HIERARCHICAL REINFORCEMENT LEARNING BY DISCOVERING INTRINSIC OPTIONS - OpenReview
- [researchgate.net](https://www.researchgate.net/figure/Discriminator-architecture-in-DG-AIL_fig1_335399882) - Discriminator architecture in DG-AIL. | Download Scientific Diagram - ResearchGate
- [researchgate.net](https://www.researchgate.net/publication/392820300_Discriminator-weighted_offline_imitation_learning_with_unlabeled_demonstrations_for_robotic_tasks) - Discriminator-weighted offline imitation learning with unlabeled demonstrations for robotic tasks | Request PDF - ResearchGate
- [arxiv.org](https://arxiv.org/html/2507.05522v1) - Gaussian Process-Based Active Exploration Strategies in Vision and Touch - arXiv
- [opus.lib.uts.edu.au](https://opus.lib.uts.edu.au/bitstream/10453/102700/2/02Whole.pdf) - Gaussian processes for information-theoretic robotic mapping and exploration - OPUS at UTS
- [robotics.caltech.edu](http://robotics.caltech.edu/wiki/images/f/fb/GPISforGrasping.pdf) - Gaussian process implicit surfaces for shape estimation and grasping - Robotics
- [mdpi.com](https://www.mdpi.com/1099-4300/23/8/1046) - A Review of Shannon and Differential Entropy Rate Estimation - MDPI
- [gaussianprocess.org](https://gaussianprocess.org/gpml/chapters/RW.pdf) - CE Rasmussen & CKI Williams, Gaussian Processes for Machine Learning, the MIT Press, 2006

### 期望信息增益的闭环计算逻辑

我已经成功构建了期望信息增益（EIG）的完整闭环计算逻辑。通过将机器人当前的 Belief 视为粒子分布，我正在模拟“如果我执行动作 $a$，我会观察到什么 $z$”的虚拟反馈过程。我发现，最有效的路径是通过蒙特卡洛采样未来可能的观测序列，并计算后验分布相对于先验的 KL 散度。这种方法将复杂的偏微分方程求解转化为可数值化结算的采样过程，使得灵巧手能够预见每一次触碰背后的信息价值，从而在接触发生前就优化其轨迹。

### 高维空间下的本征动力学识别

在解决高维广义坐标系下的探索难题时，我厘清了判别器（Discriminator）在变分赋能算法中的核心作用。我确定采用 $q(z|s)$ 的映射架构，即通过观察状态序列来推断隐含的动作技能。这种设计有效解决了奖励极度稀疏的问题，使机器人能自发地探索那些能最大限度改写环境状态（State Coverage）的交互模式。我意识到，这种从状态覆盖率出发的探索策略，比单纯的随机运动更能让灵巧手理解物体的物理边界。

### 物理真实性与感知模型最终集成

在进入最终的体系构建阶段，我将着重解决模拟环境与真实物理世界之间的信息保真度鸿沟。我注意到，校准误差常导致算法在模拟中预测的熵减在现实中因“落空”而失效，这种“信息幻觉”是主动感知失败的主要诱因。我接下来的行动将聚焦于在算法逻辑中引入触觉传感器的噪声鲁棒性建模，并整合出一套兼顾实时性与探索深度的代码架构。我将确保最终生成的逻辑能够反映出物理接触的非线性和传感器的统计特征，为知识库提供一个从数学定义到物理落地的完整闭环。

#### 研究网站 / Researched Websites

- [proceedings.neurips.cc](https://proceedings.neurips.cc/paper_files/paper/2024/file/8fa068ffe59817175d176bd75641fe16-Paper-Conference.pdf) - Overcoming the Sim-to-Real Gap: Leveraging Simulation to Learn to Explore for Real-World RL - NIPS
- [arts.units.it](https://arts.units.it/bitstream/11368/2998556/5/Crossing_the_Reality_Gap_A_Survey_on_Sim-to-Real_Transferability_of_Robot_Controllers_in_Reinforcement_Learning.pdf) - Crossing the Reality Gap: A Survey on Sim-to-Real Transferability of Robot Controllers in Reinforcement Learning - ArTS
- [arxiv.org](https://arxiv.org/html/2601.02778v1) - Closing the Reality Gap: Zero-Shot Sim-to-Real Deployment for Dexterous Force-Based Grasping and Manipulation - arXiv
- [rpg.ifi.uzh.ch](https://rpg.ifi.uzh.ch/docs/AR25_Aljalbout.pdf) - The Reality Gap in Robotics: Challenges, Solutions, and Best Practices
- [arxiv.org](https://arxiv.org/html/2410.20254v1) - Overcoming the Sim-to-Real Gap: Leveraging Simulation to Learn to Explore for Real-World RL - arXiv
- [roboticsproceedings.org](https://www.roboticsproceedings.org/rss01/p09.pdf) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters - Robotics
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10054117/) - Rao-Blackwellized Particle Filter Algorithm Integrated with Neural Network Sensor Model Using Laser Distance Sensor - NIH
- [ipb.uni-bonn.de](https://www.ipb.uni-bonn.de/wp-content/papercite-data/pdf/burgard05snowbird.pdf) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters
- [merl.com](https://www.merl.com/publications/docs/TR2010-028.pdf) - Rao-Blackwellized Particle Filtering for Probing-Based 6-DOF Localization in Robotic Assembly - Mitsubishi Electric Research Laboratories
- [researchgate.net](https://www.researchgate.net/publication/221344623_Information_Gain-based_Exploration_Using_Rao-Blackwellized_Particle_Filters) - Information Gain-based Exploration Using Rao-Blackwellized Particle Filters
- [frontiersin.org](https://www.frontiersin.org/journals/neurorobotics/articles/10.3389/fnbot.2019.00027/full) - Neural Activations Associated With Friction Stimulation on Touch-Screen Devices - Frontiers
- [royalsocietypublishing.org](https://royalsocietypublishing.org/rsif/article/20/199/20220718/90285/Rapid-change-of-friction-causes-the-illusion-of) - Rapid change of friction causes the illusion of touching a receding surface
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel8/4543165/10807698/10746609.pdf) - Perceptual Constancy in the Speed Dependence of Friction During Active Tactile Exploration - IEEE Xplore
- [arxiv.org](https://arxiv.org/abs/2312.00215) - [2312.00215] Learning active tactile perception through belief-space control - arXiv

### 期望信息增益的粒子化离散求解

我已成功将复杂的 Expected Information Gain (EIG) 计算转化为一套基于 Rao-Blackwellized Particle Filter (RBPF) 的数值结算方案。通过在粒子空间中进行蒙特卡洛采样，我能够模拟未来的观测序列并直接计算信念分布的 KL Divergence。这种方法巧妙地避开了高维状态空间中复杂的微分方程，使我能够在机器人执行触碰动作前，就准确量化每一个动作对降低物体几何不确定性的边际贡献。这种采样驱动的预见性感知，是实现灵巧操作中主动搜索逻辑的核心。

### 变分赋能下的本征技能发现逻辑

在探索灵巧手如何自主掌握交互技能时，我厘清了判别器 (Discriminator) 在变分互信息极大化中的关键构造。通过采用 $q(z|s)$ 的映射架构，即根据状态序列推断隐含的动作技能，我实现了对 Empowerment 的有效近似。这种变分推断逻辑解决了奖励极度稀疏环境下的自主探索问题，使灵巧手能够在没有外部引导的情况下，自发地发现诸如“物体翻转”或“边缘追踪”等具有物理意义的操作基元，从而显著提升了状态空间的覆盖效率。

### 物理保真度校准与代码架构集成

我最后阶段的行动将聚焦于解决 Sim-to-Real 迁移中的“信息幻觉”问题。我正深入思考如何建模传感器的噪声特性，以防止算法在理想化的模拟环境中产生虚假的信息增益。我将整合出一套兼顾数值稳定性与物理真实性的核心逻辑代码，涵盖触觉传感器的似然建模以及判别器网络的具体实现细节。这将最终形成一个从信息论底层定义出发，历经主动感知算法演进，最终落地于灵巧操作物理实践的深度知识闭环。

#### 研究网站 / Researched Websites

- [arxiv.org](https://arxiv.org/pdf/2511.01281) - Particle Filter Made Simple: A Step-by-Step Beginner-friendly Guide - arXiv
- [medium.com](https://medium.com/@mathiasmantelli/particle-filter-part-2-intuitive-example-and-equations-0716223b862b) - Particle Filter Part 2 — Intuitive example and equations | by Mathias Mantelli | Medium
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7826670/) - Particle Filters: A Hands-On Tutorial - PMC - PubMed Central
- [stats.ox.ac.uk](https://www.stats.ox.ac.uk/~doucet/doucet_johansen_tutorialPF2011.pdf) - A Tutorial on Particle Filtering and Smoothing: Fifteen years later - Oxford statistics department
- [ai.stanford.edu](https://ai.stanford.edu/~gabeh/papers/Hoffmann_ParticleMutualInfo_CDC06.pdf) - Mutual Information Methods with Particle Filters for Mobile Sensor Network Control - Stanford AI Lab
- [arxiv.org](https://arxiv.org/html/2510.24257v1) - Learning Task-oriented Manipulation Skills by Adversarial Motion Priors - arXiv
- [mdpi.com](https://www.mdpi.com/1424-8220/24/2/700) - Deep Reinforcement Learning for Autonomous Driving with an Auxiliary Actor Discriminator

### 期望信息增益的闭环数值结算方案

我正在对基于采样的方法进行最后的数值合成，以解决灵巧操作中 Expected Information Gain (EIG) 的计算难题。通过将 Rao-Blackwellized Particle Filter (RBPF) 与互信息度量深度耦合，我构思了一套闭环逻辑：利用当前粒子分布模拟未来的感官观测，从而量化每一次触碰对降低物体位姿不确定性的边际价值。这种方法成功绕过了高维 Belief Space 中的连续积分难题，将抽象的信息论原则转化为机器人可执行的离散路径规划决策。

### 变分赋能中的行为区分度建模

在思考如何让二十多个自由度的灵巧手在无奖励环境下自主探索时，我提炼出了变分赋能算法的核心——判别器 (Discriminator) 架构。我确定通过学习映射 $q(z|s)$，使机器人能够根据其运动轨迹推断出隐含的交互技能。这种机制的精妙之处在于，它促使机器人自发地产生具有高度区分度的行为模式，如边缘追踪或物块翻转，从而在复杂的接触动力学中最大化其对环境的控制力 (Empowerment) 和信息覆盖率。

### 感知模型集成与知识库最终交付

通过对多模态主动感知框架的深入审视，我已完成了所有必要的理论探索与技术对比，现在正转向最终的知识体系构建。我将特别关注如何处理从模拟环境到现实物理世界 (Sim-to-Real) 迁移时出现的信息增益偏差，通过在感知模型中引入非线性噪声建模来消除“信息幻觉”。接下来的行动中，我将开始撰写核心算法的实现逻辑，涵盖触觉似然函数建模、粒子权重更新以及判别器训练流程，构建一个从数学定义到物理落地的深度灵巧操作知识库。


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*