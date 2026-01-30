# Research Request Limit Reached - Gemini

**导出时间 / Exported At:** 2026-01-29 15:38:56

**总思考阶段 / Total Phases:** 1

---

## 思考阶段 1 / Thinking Phase 1

### 核心理论架构与物理建模

我正在构建一个多维度的信号处理框架，重点聚焦于触觉传感器底层的物理建模。通过分析MEMS气压计、视触觉传感器以及电容式阵列的原始信号特征，我识别出了噪声、迟滞效应及非线性等关键物理瓶颈。我不仅关注数据的提取，更在思考如何通过数学模型精确描述传感器与物体接触时的力学交互，以建立起从原始电压或图像信号到物理力学参数的映射。

### 状态估计中的复杂性挑战

在接触定位与力矢量分解的研究中，我发现传统线性滤波与高度非线性的触觉交互之间存在明显的代差。目前的研究正从简单的力反馈转向复杂的局部曲率估计与摩擦锥参数识别。我正试图理清如何利用高级估计算法或深度学习架构来弥合几何特征与动力学状态之间的信息鸿沟，解决复杂灵巧操作中的多维约束问题。

### 动态感知与控制闭环的下一步行动

接下来，我将深入探讨动态事件感知，特别是利用时频分析和基于事件的信号处理来捕获早期滑移的关键特征。同时，我会着重研究多模态传感器融合策略，尝试将触觉、视觉与本体感受集成到统一的估计框架中，以实现更高频率的力控稳定。我的目标是整合出一套能够直接指导硬件算法实现的核心逻辑，确保信号处理的低延迟与高保真度。

#### 研究网站 / Researched Websites

- [arxiv.org](https://arxiv.org/html/2504.03515v5) - Dexterous Manipulation through Imitation Learning: A Survey - arXiv
- [arxiv.org](https://arxiv.org/html/2507.11840v2) - The Developments and Challenges towards Dexterous and Embodied Robotic Manipulation: A Survey - arXiv
- [arxiv.org](https://arxiv.org/html/2510.14647v1) - Spatially-anchored Tactile Awareness for Robust Dexterous Manipulation - arXiv
- [arxiv.org](https://arxiv.org/html/2409.20473v2) - Learning with Less: Optimizing Tactile Sensor Configurations for Dexterous Manipulation
- [arxiv.org](https://arxiv.org/html/2401.12496v2) - DexTouch: Learning to Seek and Manipulate Objects with Tactile Dexterity - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9782357/) - MEMS-Based Tactile Sensors: Materials, Processes and Applications in Robotics - PMC
- [mdpi.com](https://www.mdpi.com/1424-8220/23/1/428) - BaroTac: Barometric Three-Axis Tactile Sensor with Slip Detection Capability - MDPI
- [dash.harvard.edu](https://dash.harvard.edu/bitstreams/7312037d-5579-6bd4-e053-0100007fdf3b/download) - The Feel of MEMS Barometers: Inexpensive and Easily Customized Tactile Array Sensors - DASH (Harvard)
- [researchgate.net](https://www.researchgate.net/publication/265555831_The_Feel_of_MEMS_Barometers_Inexpensive_and_Easily_Customized_Tactile_Array_Sensors) - The Feel of MEMS Barometers: Inexpensive and Easily Customized Tactile Array Sensors
- [hira.hope.ac.uk](https://hira.hope.ac.uk/id/eprint/3041/1/Final_GelSightReview.pdf) - Visuotactile Sensors with Emphasis on GelSight Sensor: A Review - Hope's Institutional Research Archive (HIRA)
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5751610/) - GelSight: High-Resolution Robot Tactile Sensors for Estimating Geometry and Force - PMC
- [gelsight.csail.mit.edu](https://gelsight.csail.mit.edu/wedge/ICRA2021_Wedge.pdf) - GelSight Wedge: Measuring High-Resolution 3D Contact Geometry with a Compact Robot Finger - MIT
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/126631/1708.00922.pdf?sequence=2&isAllowed=y) - Improved GelSight tactile sensor for measuring geometry and slip - DSpace@MIT
- [arxiv.org](https://arxiv.org/html/2409.20142v1) - Signal Processing for Haptic Surface Modeling: a Review - arXiv
- [mdpi.com](https://www.mdpi.com/1424-8220/23/16/7293) - Modified Nonlinear Hysteresis Approach for a Tactile Sensor - MDPI
- [scholarworks.indianapolis.iu.edu](https://scholarworks.indianapolis.iu.edu/bitstreams/064a37d1-69bf-4e38-8887-bd4f17d13e4c/download) - Mathematical Model and Experimental Design of Nanocomposite Proximity Sensors - IU Indianapolis ScholarWorks
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC6263915/) - A Non-Linear Model of an All-Elastomer, in-Plane, Capacitive, Tactile Sensor Under the Application of Normal Forces - NIH
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/7361/10251409/10209412.pdf) - Mathematical Model and Experimental Characterization of Vertically Stacked Capacitive Tactile Sensors - IEEE Xplore
- [mdpi.com](https://www.mdpi.com/1424-8220/22/17/6697) - Nonlinear Tactile Estimation Model Based on Perceptibility of Mechanoreceptors Improves Quantitative Tactile Sensing - MDPI
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/128649/py-icra18.pdf?sequence=2) - Realtime State Estimation with tactile and visual sensing. Application to Planar Manipulation. - DSpace@MIT
- [mdpi.com](https://www.mdpi.com/1424-8220/17/12/2762) - GelSight: High-Resolution Robot Tactile Sensors for Estimating Geometry and Force - MDPI
- [motion.cs.illinois.edu](https://motion.cs.illinois.edu/papers/ICRA2024_Peng_EstimationSoftBubble.pdf) - 3D Force and Contact Estimation for a Soft-Bubble Visuotactile Sensor Using FEM - Intelligent Motion Lab
- [arxiv.org](https://arxiv.org/html/2410.02048v1) - FeelAnyForce: Estimating Contact Force Feedback from Tactile Sensation for Vision-Based Tactile Sensors - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7967204/) - Vision-Based Tactile Sensor Mechanism for the Estimation of Contact Position and Force Distribution Using Deep Learning - NIH

### 触觉感知的层级演进与物理特征映射

通过对多模态触觉信息的深度解构，我观察到感知任务正从简单的接触触发（Gating Signals）向高维几何推理（Geometric Reasoning）以及最终的力主导合规控制（Force-dominant Control）演进。特别是在视触觉传感领域，我发现通过Photometric Stereo算法解析图像梯度，并利用Poisson方程重建亚毫米级深度场，是实现精密灵巧操作的关键。这种从原始像素到微观几何的映射，为机器人提供了超越传统视觉的闭环控制精度。

### 非线性迟滞建模与信号质量优化

我正在分析MEMS与柔性电容阵列在实际操作中面临的物理瓶颈。尽管多项式拟合能缓解部分静态非线性，但在高频动态接触下，传感器固有的迟滞（Hysteresis）和路径依赖性成为状态估计的主要偏差来源。我正致力于引入更复杂的数学模型（如Prandtl-Ishlinskii模型）来补偿这种动态误差，并研究如何通过时频分析手段，在噪声干扰中提取更纯净的力矢量特征。

### 早期滑移辨识与多模态因子图构建

接下来的阶段，我将聚焦于早期滑移（Incipient Slip）的瞬态辨识算法，利用STFT或小波变换捕捉接触面边缘的微振动特征。同时，我计划构建一个基于因子图（Factor Graph）的视觉-触觉融合框架，将触觉提供的局部几何约束与视觉的全局位姿信息进行联合优化。我的核心目标是推导并实现这些算法的底层逻辑，确保在灵巧操作中实现对物体状态的准实时、高保真度追踪。

#### 研究网站 / Researched Websites

- [mdpi.com](https://www.mdpi.com/1424-8220/22/22/8763) - A Modified Prandtl–Ishlinskii Hysteresis Model for Modeling and Compensating Asymmetric Hysteresis of Piezo-Actuated Flexure-Based Systems - MDPI
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10458598/) - Modified Nonlinear Hysteresis Approach for a Tactile Sensor - PMC - PubMed Central
- [developmental-robotics.jp](https://developmental-robotics.jp/wp-content/uploads/publications/Horii_Humanoids14.pdf) - Compensation for Tactile Hysteresis Using Gaussian Process with Sensory Markov Property
- [researchgate.net](https://www.researchgate.net/publication/253598448_Hysteresis_Correction_of_Tactile_Sensor_Response_with_a_Generalized_Prandtl-Ishlinskii_Model) - Hysteresis Correction of Tactile Sensor Response with a Generalized Prandtl-Ishlinskii Model | Request PDF - ResearchGate
- [pdfs.semanticscholar.org](https://pdfs.semanticscholar.org/b8b6/d394890db1db79eec74eba7f51701f4aac60.pdf) - A New Model Based on Adaptation of the External Loop to Compensate the Hysteresis of Tactile Sensors - Semantic Scholar
- [mdpi.com](https://www.mdpi.com/1424-8220/14/1/709) - Micro-Vibration-Based Slip Detection in Tactile Force Sensors - MDPI
- [researchgate.net](https://www.researchgate.net/publication/349421334_Method_for_Automatic_Slippage_Detection_With_Tactile_Sensors_Embedded_in_Prosthetic_Hands) - Method for Automatic Slippage Detection With Tactile Sensors Embedded in Prosthetic Hands - ResearchGate
- [apps.dtic.mil](https://apps.dtic.mil/sti/tr/pdf/ADA259423.pdf) - Incipient Failure Detection Using Wavelets - DTIC
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11243884/) - Wavelet Transforms Significantly Sparsify and Compress Tactile Interactions - PMC - NIH
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/8253409/9437987/09356667.pdf) - Method for Automatic Slippage Detection With Tactile Sensors Embedded in Prosthetic Hands - IEEE Xplore
- [emergentmind.com](https://www.emergentmind.com/topics/factor-graph-based-sensor-fusion) - Factor Graph-Based Sensor Fusion - Emergent Mind
- [cs.cmu.edu](https://www.cs.cmu.edu/~kaess/pub/Sodhi21icra.pdf) - Learning Tactile Models for Factor Graph-based Estimation - CMU School of Computer Science
- [mdpi.com](https://www.mdpi.com/2072-4292/16/22/4171) - Tightly Coupled LIDAR/IMU/UWB Fusion via Resilient Factor Graph for Quadruped Robot Positioning - MDPI
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10318164/) - Adaptive visual–tactile fusion recognition for robotic operation of multi-material system - NIH
- [arxiv.org](https://arxiv.org/pdf/2105.08257) - Differentiable Factor Graph Optimization for Learning Smoothers - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC6539104/) - Localization of Sliding Movements Using Soft Tactile Sensing Systems with Three-axis Accelerometers - PMC - NIH
- [amolchanov86.github.io](https://amolchanov86.github.io/pdf/molchanov16iros.pdf) - Contact Localization on Grasped Objects using Tactile Sensing - Artem Molchanov
- [mdpi.com](https://www.mdpi.com/1424-8220/14/2/3227) - Object Recognition and Localization: The Role of Tactile Sensors - MDPI
- [researchgate.net](https://www.researchgate.net/publication/312288511_Contact_localization_on_grasped_objects_using_tactile_sensing) - Contact localization on grasped objects using tactile sensing - ResearchGate
- [faculty.sites.iastate.edu](https://faculty.sites.iastate.edu/jia/files/inline-files/IROS03.pdf) - Contact Sensing for Parts Localization - Iowa State University
- [experts.illinois.edu](https://experts.illinois.edu/en/publications/measurement-of-shear-and-slip-with-a-gelsight-tactile-sensor/) - Measurement of shear and slip with a GelSight tactile sensor - Illinois Experts
- [arxiv.org](https://arxiv.org/html/2411.03315v3) - Learning Force Distribution Estimation for the GelSight Mini Optical Tactile Sensor Based on Finite Element Analysis - arXiv
- [mdpi.com](https://www.mdpi.com/1424-8220/17/12/2762) - GelSight: High-Resolution Robot Tactile Sensors for Estimating Geometry and Force - MDPI
- [dspace.mit.edu](https://dspace.mit.edu/bitstream/handle/1721.1/126631/1708.00922.pdf?sequence=2&isAllowed=y) - Improved GelSight tactile sensor for measuring geometry and slip - DSpace@MIT
- [youtube.com](https://www.youtube.com/watch?v=TgR0NvYty0A) - Shape As Points: A Differentiable Poisson Solver - YouTube
- [hira.hope.ac.uk](https://hira.hope.ac.uk/id/eprint/3041/1/Final_GelSightReview.pdf) - Visuotactile Sensors with Emphasis on GelSight Sensor: A Review
- [motion.cs.illinois.edu](https://motion.cs.illinois.edu/papers/ICRA2024_Peng_EstimationSoftBubble.pdf) - 3D Force and Contact Estimation for a Soft-Bubble Visuotactile ...
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC6263915/) - A Non-Linear Model of an All-Elastomer, in-Plane, Capacitive ... - NIH
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9782357/) - MEMS-Based Tactile Sensors: Materials, Processes and ...

### 视触觉底层重构与有限元力学推演

我正在深入解析视触觉传感器的底层解算逻辑。通过对GelSight图像梯度的分析，我进一步明确了利用Poisson方程（$
abla^2 Z = p_x + q_y$）进行高度场重构的精确路径。同时，针对Soft-bubble这类具有全局形变特征的传感器，我正在研究如何引入有限元分析（FEM）和线性平面应力近似，将复杂的表面张力与气压变化转化为精确的接触力矢量，这为从原始视觉信号中提取高保真度的力学特征提供了物理理论支撑。

### 感知不确定性建模与因子图观测模型

在处理传感器噪声与非线性偏差时，我正试图跳出简单的统计滤波，转向更为精细的功率谱密度（PSD）分析与Allan方差建模，以量化MEMS等硬件的固有漂移。我发现解决接触定位偏差的关键在于构建精准的因子图观测模型 $h(x)$。通过推导触觉测量值与物体位姿之间的非线性似然函数，我正致力于将触觉约束与动力学状态进行深度耦合，从而在存在迟滞和噪声的环境中，依然能实现对接触点及摩擦锥边界的鲁棒估计。

### 瞬态特征算法链与摩擦约束细化

接下来的行动中，我将聚焦于早期滑移辨识的算法逻辑细化，特别是确定从STFT时频分析到二值化判定信号的特征提取算子。我将重点攻克摩擦锥估计的数学细节，探寻针对嘈杂触觉数据的闭式解或优化算法。此外，我将整合出一套完整的因子图势函数公式，确保从微观的信号震荡到宏观的物体状态追踪之间，建立起严密的逻辑闭环，为灵巧操作的合规控制提供算法基础。

#### 研究网站 / Researched Websites

- [cs.cmu.edu](https://www.cs.cmu.edu/~kaess/pub/Sodhi21icra.pdf) - Learning Tactile Models for Factor Graph-based Estimation - CMU School of Computer Science
- [visal.cs.cityu.edu.hk](http://visal.cs.cityu.edu.hk/static/pubs/journal/tip14-robustlikelihood.pdf) - A Robust Likelihood Function for 3D Human Pose Tracking - VISAL
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC10054539/) - Real-Time 6-DOF Pose Estimation of Known Geometries in Point Cloud Data - PMC
- [arxiv.org](https://arxiv.org/abs/2012.03768) - [2012.03768] Learning Tactile Models for Factor Graph-based Estimation - arXiv
- [youtube.com](https://www.youtube.com/watch?v=JmR2YpkLNt0) - Factor Graphs and Robust Perception | Michael Kaess | Tartan SLAM Series - YouTube
- [repository.tudelft.nl](https://repository.tudelft.nl/file/File_68ada542-01f2-4c7b-b0a6-c343006dc6c2) - Role of Friction Estimation in Quadrupedal Locomotion MPC - TU Delft Repository
- [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/26737272/) - An eight-legged tactile sensor to estimate coefficient of static friction - PubMed
- [researchgate.net](https://www.researchgate.net/publication/327409620_Tactile_Sensors_for_Friction_Estimation_and_Incipient_Slip_Detection_-_Towards_Dexterous_Robotic_Manipulation_A_Review) - Tactile Sensors for Friction Estimation and Incipient Slip Detection – Towards Dexterous Robotic Manipulation: A Review | Request PDF - ResearchGate
- [mdpi.com](https://www.mdpi.com/2076-3417/13/2/921) - Detecting and Controlling Slip through Estimation and Control of the Sliding Velocity - MDPI
- [arxiv.org](https://arxiv.org/html/2501.09468v2) - Sensorimotor Control Strategies for Tactile Robotics - arXiv
- [mdpi.com](https://www.mdpi.com/1424-8220/14/1/709) - Micro-Vibration-Based Slip Detection in Tactile Force Sensors - MDPI
- [researchgate.net](https://www.researchgate.net/publication/398136004_Slip_Detection_and_Stable_Grasping_With_Multi-Fingered_Robotic_Hand_Using_Deep_Learning_Approach) - Slip Detection and Stable Grasping With Multi‐Fingered Robotic Hand Using Deep Learning Approach - ResearchGate
- [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/41336407/) - Spatial Features-Based Slip Detection in Neuromorphic Vision Tactile Sensors - PubMed
- [data.mendeley.com](https://data.mendeley.com/datasets/yfvv3crnpy/1) - Spectral Centroid Images for Multi-class Human Action Analysis : A Benchmark Dataset - Mendeley Data
- [arxiv.org](https://arxiv.org/html/2411.07442v1) - Learned Slip-Detection-Severity Framework using Tactile Deformation Field Feedback for Robotic Manipulation - arXiv
- [gelsight.csail.mit.edu](https://gelsight.csail.mit.edu/wedge/ICRA2021_Wedge.pdf) - GelSight Wedge: Measuring High-Resolution 3D Contact Geometry with a Compact Robot Finger - MIT
- [mdpi.com](https://www.mdpi.com/1424-8220/22/17/6470) - Model-Based 3D Contact Geometry Perception for Visual Tactile Sensor - MDPI
- [discovery.ucl.ac.uk](https://discovery.ucl.ac.uk/10204702/1/GelPoLight_A_Novel_Visual_Tactile_Sensor_Based_on_Photometric_Stereo_with_Point_Lighting.pdf) - GelPoLight: A Novel Visual Tactile Sensor Based on Photometric Stereo with Point Lighting - UCL Discovery
- [ccs.neu.edu](https://www.ccs.neu.edu/home/atp/publications/gelsightinsertion_iros2014.pdf) - Localization and Manipulation of Small Parts Using GelSight Tactile Sensing - Khoury College of Computer Sciences
- [arxiv.org](https://arxiv.org/html/2412.09617v1) - NormalFlow: Fast, Robust, and Accurate Contact-based Object 6DoF Pose Tracking with Vision-based Tactile Sensors - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC9782357/) - MEMS-Based Tactile Sensors: Materials, Processes and Applications in Robotics - PMC
- [dash.harvard.edu](https://dash.harvard.edu/bitstreams/7312037d-5579-6bd4-e053-0100007fdf3b/download) - The Feel of MEMS Barometers: Inexpensive and Easily Customized Tactile Array Sensors - DASH (Harvard)
- [researchgate.net](https://www.researchgate.net/publication/364318246_MEMS_Inertial_Sensors_Modeling_Using_Power_Spectral_Density_Method_MEMS_Inertial_Sensors_Modeling_Using_Power_Spectral_Density_Method) - (PDF) MEMS Inertial Sensors Modeling Using Power Spectral Density Method MEMS Inertial Sensors Modeling Using Power Spectral Density Method - ResearchGate
- [mdpi.com](https://www.mdpi.com/2076-3417/14/3/1121) - Analysis of Stochastic Properties of MEMS Accelerometers and Gyroscopes Used in the Miniature Flight Data Recorder - MDPI
- [dsp.stackexchange.com](https://dsp.stackexchange.com/questions/90125/modelling-mems-accelerometer-noise) - Modelling MEMS accelerometer noise - Signal Processing Stack Exchange

### 触觉感知能级的多维跃迁

我在分析中观察到，触觉感知任务正经历从基础的门控信号（Gating Signals）向高维几何推理（Geometric Reasoning）的本质跨越。特别是通过研究Spatially-anchored Tactile Awareness框架，我发现将触觉特征直接锚定在三维空间坐标系中，是实现毫米级高精度灵巧操作的核心。这种空间锚定机制不仅提升了对物体几何形状的感知深度，也为最终实现力主导的合规控制（Force-dominant Control）提供了关键的拓扑约束。

### 非线性模型校准与摩擦锥鲁棒估计

在解决传感器非线性难题时，我进一步细化了电容式阵列的物理响应模型，通过引入更精确的指数映射函数来捕捉极板间距与电荷变化之间的非线性关系。针对摩擦锥（Friction Cone）在复杂噪声环境下的辨识问题，我正试图利用递归最小二乘法（RLS）或基于优化的方法代替传统的简单线性回归，以更稳健地识别摩擦系数 $\mu$ 的动态演变。这种对摩擦物理边界的实时追踪，是防止灵巧操作过程中物体意外滑脱的理论基石。

### 瞬态算法链构建与因子图势函数推演

接下来的行动中，我将聚焦于早期滑移（Incipient Slip）辨识算法的工程化落地，计划通过提取STFT频谱质心（Spectral Centroid）来构建一套严密的实时判定逻辑。同时，我将深入推导触觉因子图中的似然函数（Likelihood Function），试图将传感器观测到的局部几何接触与物体全局位姿之间的偏差转化为数学上的势函数约束。最后，我会整合出一套针对触觉阵列的接触定位核心逻辑，通过加权质心或图像矩（Image Moments）方法实现对接触斑块的快速、高保真解析。

#### 研究网站 / Researched Websites

- [semanticscholar.org](https://www.semanticscholar.org/paper/8bbd1f68b6136057b76e3e58b2327c03746ff5c6) - [PDF] Learning Tactile Models for Factor Graph-based State Estimation - Semantic Scholar
- [cs.cmu.edu](https://www.cs.cmu.edu/~kaess/pub/Sodhi21icra.pdf) - Learning Tactile Models for Factor Graph-based Estimation - CMU School of Computer Science
- [orbilu.uni.lu](https://orbilu.uni.lu/bitstream/10993/64744/1/ACCESS3534993.pdf) - Factor Graphs in Optimization-Based Robotic Control—A Tutorial and Review - ORBilu
- [researchgate.net](https://www.researchgate.net/publication/346701537_Learning_Tactile_Models_for_Factor_Graph-based_State_Estimation) - (PDF) Learning Tactile Models for Factor Graph-based State Estimation - ResearchGate
- [arxiv.org](https://arxiv.org/abs/2012.03768) - [2012.03768] Learning Tactile Models for Factor Graph-based Estimation - arXiv
- [pubmed.ncbi.nlm.nih.gov](https://pubmed.ncbi.nlm.nih.gov/26737272/) - An eight-legged tactile sensor to estimate coefficient of static friction - PubMed
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel8/6287639/10820123/11129059.pdf) - Joint Friction Dynamic Estimation for Robotic Finger Using Novel Fixed-Time Adaptive Model Free Algorithm With ZNN-Based Approximator
- [pure.kaist.ac.kr](https://pure.kaist.ac.kr/en/publications/linearized-recursive-least-squares-methods-for-real-time-identifi/) - Linearized Recursive Least Squares Methods for Real-Time Identification of Tire-Road Friction Coefficient - Korea Advanced Institute of Science and Technology
- [researchgate.net](https://www.researchgate.net/publication/43808074_Application_of_Recursive_Least_Square_Algorithm_on_Estimation_of_Vehicle_Sideslip_Angle_and_Road_Friction) - Application of Recursive Least Square Algorithm on Estimation of Vehicle Sideslip Angle and Road Friction - ResearchGate
- [mdpi.com](https://www.mdpi.com/2076-3417/7/12/1230) - Road Friction Virtual Sensing: A Review of Estimation Techniques with Emphasis on Low Excitation Approaches - MDPI
- [researchgate.net](https://www.researchgate.net/publication/380208487_Contact_localization_from_soft_tactile_array_sensor_using_tactile_image) - Contact localization from soft tactile array sensor using tactile image - ResearchGate
- [github.com](https://github.com/HIRO-group/TactileContactLocalization) - HIRO-group/TactileContactLocalization: 3D Contact localization for mutual capacitive tactile sensing arrays for robotics - GitHub
- [semanticscholar.org](https://www.semanticscholar.org/paper/4311fb28f8151580af1d9866d9441201b874346b) - Contact localization from soft tactile array sensor using tactile image | Semantic Scholar
- [arxiv.org](https://arxiv.org/abs/1708.04441) - Localizing the Object Contact through Matching Tactile Features with Visual Map - arXiv
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC7374373/) - 3D Contact Position Estimation of Image-Based Areal Soft Tactile Sensor with Printed Array Markers and Image Sensors - NIH
- [apps.dtic.mil](https://apps.dtic.mil/sti/tr/pdf/ADA259423.pdf) - Incipient Failure Detection Using Wavelets - DTIC
- [researchgate.net](https://www.researchgate.net/figure/Slip-detection-based-on-wavelet-transformation_fig2_311849693) - Slip detection based on wavelet transformation. - ResearchGate
- [academia.edu](https://www.academia.edu/3431742/Detection_of_Incipient_Faults_in_Power_Transformer_Using_Wavelet_Transform_Lessons_Learned) - (PDF) Detection of Incipient Faults in Power Transformer Using Wavelet Transform: Lessons Learned - Academia.edu
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856167/) - A Novel Event-Based Incipient Slip Detection Using Dynamic Active-Pixel Vision Sensor (DAVIS) - NIH
- [ieeexplore.ieee.org](https://ieeexplore.ieee.org/iel7/6287639/8948470/09066937.pdf) - Methods and Sensors for Slip Detection in Robotics: A Survey - IEEE Xplore

### 因子图观测模型的数学重构

我正在对触觉观测因子进行深度数学建模，将其从模糊的概率约束精炼为显式的势函数：$\phi(X_t, Z_t) \propto \exp(-\frac{1}{2} \| f(Z_t) - h(X_t) \|^2_{\Sigma})$。这种结构通过深度卷积网络提取原始触觉图像中的位姿特征 $f(Z_t)$，并与基于物理状态的观测方程 $h(X_t)$ 进行残差计算。这种方法有效解决了传统滤波器在处理高维图像观测时的表征难题，为复杂接触状态下的物体位姿追踪提供了严谨的概率推理框架。

### 递归最小二乘法下的动态摩擦估计

在处理摩擦边界的不确定性时，我正利用递归最小二乘法（RLS）优化参数识别逻辑。通过构建回归向量 $\phi$ 与参数矢量 $\theta$ 的线性映射，我试图将法向力与切向力的动态比值转化为对摩擦系数 $\mu$ 的实时追踪。这种方法能够敏锐捕捉物体表面物理特性的瞬时变化，解决了静态摩擦模型在灵巧操作中因接触面特性不均导致的估计偏差，确保护持任务始终处于摩擦锥（Friction Cone）的物理约束内。

### 算法链整合与状态估计闭环

我目前正在整合一套从底层信号处理到高层状态估计的完整算法链，重点在于明确从带通滤波到频谱质心提取的滑移判定逻辑。我将深入推导因子图中协方差矩阵的自适应调整机制，以应对传感器迟滞带来的非高斯噪声。接下来的行动中，我将完成摩擦估计与滑移检测的核心逻辑校验，并将其转化为具体的算法实现，从而构建起一个从微观触觉特征到宏观操作策略的深度感知闭环。

#### 研究网站 / Researched Websites

- [lup.lub.lu.se](https://lup.lub.lu.se/luur/download?func=downloadFile&recordOId=8847828&fileOId=8859388) - Road-Tire Friction Estimation for AFS Vehicle Control - Lund University Publications
- [mdpi.com](https://www.mdpi.com/2079-9292/11/19/3119) - Intelligent Vehicle Trajectory Tracking Control Based on VFF-RLS Road Friction Coefficient Estimation - MDPI
- [kth.diva-portal.org](https://kth.diva-portal.org/smash/get/diva2:1183292/FULLTEXT01.pdf) - Heavy Vehicle Braking using Friction Estimation for Controller Optimization - kth .diva
- [researchgate.net](https://www.researchgate.net/publication/336787001_Road_tire_friction_coefficient_estimation_for_four_wheel_drive_electric_vehicle_based_on_moving_optimal_estimation_strategy) - Road tire friction coefficient estimation for four wheel drive electric vehicle based on moving optimal estimation strategy | Request PDF - ResearchGate
- [pmc.ncbi.nlm.nih.gov](https://pmc.ncbi.nlm.nih.gov/articles/PMC11991622/) - Segmented Estimation of Road Adhesion Coefficient Based on Multimodal Vehicle Dynamics Fusion in a Large Steering Angle Range - NIH
- [github.com](https://github.com/wkoa/slip_detection) - wkoa/slip_detection: A pytorch implement of Slip Detection with Combined Tactile and Vision Information - GitHub
- [mdpi.com](https://www.mdpi.com/1424-8220/19/3/523) - Learning Spatio Temporal Tactile Features with a ConvLSTM for the Direction Of Slip Detection - MDPI
- [arxiv.org](https://arxiv.org/abs/2303.00935) - [2303.00935] Learning to Detect Slip through Tactile Measures of the Contact Force Field and its Entropy - arXiv
- [towardsdatascience.com](https://towardsdatascience.com/decoding-the-symphony-of-sound-audio-signal-processing-for-musical-engineering-c66f09a4d0f5/) - Decoding the Symphony of Sound: Audio Signal Processing for Musical Engineering
- [syscop.de](https://www.syscop.de/files/2024ws/msi/exercise6.pdf) - Exercise 6: Recursive Least Squares - syscop
- [ri.cmu.edu](https://www.ri.cmu.edu/publications/learning-tactile-models-for-factor-graph-based-estimation/) - Learning Tactile Models for Factor Graph-based Estimation - CMU Robotics Institute
- [arxiv.org](https://arxiv.org/abs/2012.03768) - [2012.03768] Learning Tactile Models for Factor Graph-based Estimation - arXiv
- [researchgate.net](https://www.researchgate.net/publication/355432653_Learning_Tactile_Models_for_Factor_Graph-based_Estimation) - Learning Tactile Models for Factor Graph-based Estimation
- [researchgate.net](https://www.researchgate.net/publication/346701537_Learning_Tactile_Models_for_Factor_Graph-based_State_Estimation) - Learning Tactile Models for Factor Graph-based State Estimation
- [kaggle.com](https://www.kaggle.com/code/anshtanwar/rls-recursive-least-squares) - RLS: Recursive Least Squares - Kaggle
- [github.com](https://github.com/AleksandarHaber/Disciplined-Python-Implementation-of-the-Recursive-Least-Squares-Method) - AleksandarHaber/Disciplined-Python-Implementation-of-the-Recursive-Least-Squares-Method - GitHub
- [aleksandarhaber.com](https://aleksandarhaber.com/introduction-to-kalman-filter-disciplined-python-implementation-of-recursive-least-squares-method/) - Introduction to Kalman Filter: Disciplined Python Implementation of Recursive Least Squares Method - Aleksandar Haber
- [stackoverflow.com](https://stackoverflow.com/questions/43788014/recursive-least-squares-in-python) - Recursive Least Squares in Python - algorithm - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=y0O0WaPoJSw) - Disciplined Python Implementation of Recursive Least Squares Method - Intro to Kalman Filtering - YouTube
- [librosa.org](https://librosa.org/doc/main/generated/librosa.feature.spectral_centroid.html) - librosa.feature.spectral_centroid — librosa 0.11.0 documentation
- [mdpi.com](https://www.mdpi.com/1424-8220/14/1/709) - Micro-Vibration-Based Slip Detection in Tactile Force Sensors - MDPI
- [arxiv.org](https://arxiv.org/html/2303.00935v3) - Learning to Detect Slip through Tactile Estimation of the Contact Force Field and its Entropy
- [stackoverflow.com](https://stackoverflow.com/questions/60509010/spectral-centroid-calculation-using-librosa) - Spectral Centroid Calculation using librosa - Stack Overflow
- [youtube.com](https://www.youtube.com/watch?v=j6NTatoi928) - Extracting Spectral Centroid and Bandwidth with Python and Librosa - YouTube
- [cs.cmu.edu](https://www.cs.cmu.edu/~kaess/pub/Sodhi21icra.pdf) - Learning Tactile Models for Factor Graph-based Estimation


---

*Generated by [Gemini Voyager](https://github.com/Nagi-ovo/gemini-voyager)*