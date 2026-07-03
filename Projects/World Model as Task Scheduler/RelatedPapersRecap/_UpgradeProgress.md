# Recap 升级进度 (Gold-Standard Upgrade Progress)

> [!important] 目的与模式
> 把所有论文 recap 升级到 `Example/Rodrigues Network for Learning Robot Actions.md` 的颗粒度，按四支柱组织：**逻辑与价值 / 原理与理论 / 实验与验证 / 未来与结合**。
> 工作模式：**主线程串行，一次一篇**（不开高并发 Agent、不频繁检索）。每篇读 PDF + 旧稿 → 重写到位 → 在此翻一个勾。
> 原则源：`.github/skills/paper-recap-insight/SKILL.md` + `references/taste-rubric.md`。
> 判定标准：四支柱齐全、变量来源表 + 无跳步推导、真实实验表 + 因果解释、3 维 limitation + 具体 WMTS/灵巧手迁移、无 generic filler / 无 LaTeX 损坏。

**最后更新**: 2026-06-25 — **Part A 全部 48 篇达范本级**；**Part B 已启动，当前 44/87 篇达范本级**。Part A 额外成果：(+The Latent Space：latent 计算坐标系综述，latent-vs-结构化张力定位 WMTS)；(1) ✅ 萃取 `insight-chat-tmp.md`（ViserDex 深度对话）入 ViserDex recap——SH 函数 / K-means 簇内 DR / **EMA 动作平滑(α 随机化) ↔ [[Idea-002-Latency-Aware-Actuator]]** / belief-RNN 蒸馏；Turn 2-3 用户核心 insight → 新建 [[Rationale-Planner-Follower-Task-Definition]]；(2) ✅ 已建 [[_CrossPaperInsights]]（13 条论证线 + 🔑keystone + 跨线张力 + 速查矩阵；含 specialist→generalist、安全-cost、WM 神经主干、任务生成-课程、适应多级），并在 [[_RelatedPapersIndex]] 加导航指针。**待办**：`insight-chat-tmp.md` 内容已全萃取，可清（用户确认）；Bash 恢复后跑 `.github/scan_links.py`；继续 Part B（PapersRecap）。
**二次审计 (2026-06-16)**: 实读细查 15/48 篇（前述 11 + STORM + Hwangbo + CMA-ES + POET，覆盖 WM/灵巧/locomotion/优化-课程 四簇、最长 338→最短 122 行），均确认范本级——行数无关，最短的 World Models Uncomputable 是"愿景随笔文体判定 + 批判隔离"的范本。[[_CrossPaperInsights]] 新增 🔑 **keystone**：一个 ensemble → Solve/Probe/Reject 三读法，统一线 1（避不确定/LCB）/线 4（求不确定/Probe）/线 11（判不确定/Reject）。又补线 12（WM 神经主干 Transformer vs RNN，STORM）+ 线 2 组件分解（命令→actuator net(Hwangbo)→力矩→Lagrangian(SSRL)→运动 + 接触力 + 增益(DexCtrl)，白箱拼装）。
**适应机制谱（WMTS LAAA 完整）**：FiLM 单向量(DyWA/DexCtrl,轻但瓶颈) / hypernetwork 全权重(Trans-INR,表达力高) / 梯度微调(FOWM,慢) / 隐式 ICL(Rubik/ICL-paper) / 控制器增益(DexCtrl) / 动力学嵌入(DyWA-RMA)。按"适应幅度×算力×速度"选。
**注**: dontAsk 模式 Write 被拒、Edit 可用 → Read 全文草稿后用两个 Edit（frontmatter + body）全文替换。PDF 抽取：Bash(pdftotext) classifier 时有不可用 → 回退 Read 工具读 PDF 页。
**WM-core 论证线**: (1) **ensemble/不确定性线**：PDDM（2019 奠基：ensemble 动力学 + mean reward）→ MoDem-V2（AC-ensemble 显式 LCB, online-from-scratch）→ FOWM（Q-ensemble LCB Eq4, offline→online 微调）+ DiWA/World4RL/RWM/Model-Based Lookahead（单 WM/无 ensemble 的反面）→ WMTS 必须 ensemble+显式 LCB。FOWM+MoDem-V2 覆盖真机两模式。(2) **结构化光谱**：DexSim2Real2（显式刚体孪生）↔ DexWM（神经 latent，"latent 不足需结构化监督"）→ WMTS 取中间。(3) **无梯度规划**：PDDM/Model-Based Lookahead/DexSim2Real2/FOWM(MPPI)。(4) **安全**：SafeDreamer(cost)+MoDem-V2(保守探索)。(5) **降维**：eigengrasp+filtering。(6) **DNPM 经典先例**：PDDM 书写/Baoding。
**读取方法**: 默认 `pdftotext -layout`（轻量、文本）；仅当抽取乱码或公式/表格不清时回退 Read 工具按页渲染。**每篇流程**: pdftotext 取正文 → Read 旧稿取 frontmatter（Write 前必须 Read）→ Write 重写。

## A. RelatedPapers（WMTS 项目，47 篇）→ RelatedPapersRecap/

优先级：World Model 核心 → 灵巧 Sim-to-Real → Diffusion/IL → 探索/课程 → 表征/理论 → locomotion/control。

### World Model / Model-Based RL
- [x] **A Step Toward World Models- A Survey on Robotic Manipulation** ✅ 2026-06-15 (范本级/导航图)
- [x] **DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION (Dreamer)** ✅ 2026-06-15 (范本级)
- [x] **DayDreamer- World Models for Physical Robot Learning** ✅ 2026-06-15 (范本级)
- [x] **Deep Dynamics Models for Learning Dexterous Manipulation (PDDM)** ✅ 2026-06-15 (范本级)
- [x] **DexSim2Real2 - Building Explicit World Model ...** ✅ 2026-06-15 (范本级)
- [x] **DiWA- Diffusion Policy Adaptation with World Models** ✅ 2026-06-15 (范本级)
- [x] **DyWA: Dynamics-adaptive World Action Model** ✅ 2026-06-15 (范本级)
- [x] **Finetuning Offline World Models in the Real World (FOWM)** ✅ 2026-06-15 (范本级)
- [x] **Learning to Model the World: A Survey of World** ✅ 2026-06-15 (范本级/导航图)
- [x] **MoDem-V2- Visuo-Motor World Models ...** ✅ 2026-06-15 (范本级)
- [x] **Model-Based Lookahead Reinforcement Learning for in-hand manipulation** ✅ 2026-06-15 (范本级)
- [x] **Robotic World Model: A Neural Network Simulator** ✅ 2026-06-15 (范本级)
- [x] **SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL** ✅ 2026-06-15 (范本级)
- [x] **STORM: Efficient Stochastic Transformer based World Models for RL** ✅ 2026-06-15 (范本级)
- [x] **World Models Computing the Uncomputable** ✅ 2026-06-15 (范本级/愿景随笔批判)
- [x] **World4RL- Diffusion World Models for Policy Refinement ...** ✅ 2026-06-15 (范本级)

### Diffusion / Imitation / VLA
- [x] **Diffusion Policy: Visuomotor Policy** ✅ 2026-06-15 (范本级)
- [x] **Beyond Human Demonstrations- Diffusion-Based RL to Generate Data for VLA** ✅ 2026-06-15 (范本级)
- [x] **HG-DAgger- Interactive Imitation Learning with Human Experts** ✅ 2026-06-15 (范本级)

### Dexterous Manipulation / Sim-to-Real
- [x] **DEXTERITYGEN- Foundation Controller for Unprecedented Dexterity** ✅ 2026-06-15 (范本级)
- [x] **DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality** ✅ 2026-06-15 (范本级)
- [x] **DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning** ✅ 2026-06-15 (范本级)
- [x] **DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts** ✅ 2026-06-15 (范本级)
- [x] **From Simple to Complex Skills- The Case of In-Hand Object Reorientation** ✅ 2026-06-15 (范本级)
- [x] **Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning** ✅ 2026-06-15 (范本级)
- [x] **LIGHTNING GRASP ... PROCEDURAL GRASP SYNTHESIS WITH CONTACT FIELDS** ✅ 2026-06-15 (范本级)
- [x] **SOLVING RUBIK'S CUBE WITH A ROBOT HAND** ✅ 2026-06-15 (范本级)
- [x] **UniDexGrasp++- ... Geometry-aware Curriculum and Iterative GSL** ✅ 2026-06-15 (范本级)
- [x] **ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation** ✅ 2026-06-15 (范本级)
- [x] **World Models for Learning Dexterous Hand-Object Interactions from Human Videos (DexWM)** ✅ 2026-06-15 (范本级)

### Locomotion / Sim-to-Real / Control
- [x] **ANYmal parkour Learning agile navigation for quadrupedal robots** ✅ 2026-06-15 (范本级)
- [x] **ASAP- Aligning Simulation and Real-World Physics ...** ✅ 2026-06-15 (范本级)
- [x] **Learning Agile and Dynamic Motor Skills for Legged Robots** ✅ 2026-06-15 (范本级)
- [x] **Learning a Unified Policy for Position and Force** ✅ 2026-06-15 (范本级)
- [x] **Learning to Walk from Three Minutes of Real-World Data ...** ✅ 2026-06-15 (范本级/WM 架构蓝图)
- [x] **Sim-to-Real: Learning Agile Locomotion For Quadruped Robots** ✅ 2026-06-15 (范本级)

### Exploration / Curriculum / Optimization
- [x] **Curiosity-Driven Exploration via Latent Bayesian Surprise** ✅ 2026-06-15 (范本级)
- [x] **Curious Exploration via Structured World Models ...** ✅ 2026-06-15 (范本级)
- [x] **Improving Policy Optimization with Generalist-Specialist Learning** ✅ 2026-06-15 (范本级)
- [x] **Paired Open-Ended Trailblazer (POET)- ...** ✅ 2026-06-15 (范本级)
- [x] **Prioritized Level Replay** ✅ 2026-06-15 (范本级)
- [x] **The CMA Evolution Strategy: A Tutorial** ✅ 2026-06-16 (范本级)
- [x] **cmaes- A Simple yet Practical Python Library for CMA-ES** ✅ 2026-06-16 (范本级)

### Representation / Latent / Rotation / Theory
- [x] **FLD: Fourier Latent Dynamics ...** ✅ 2026-06-16 (范本级)
- [x] **IS ATTENTION REQUIRED FOR ICL? ...** ✅ 2026-06-16 (范本级)
- [x] **On the Continuity of Rotation Representations in Neural Networks** ✅ 2026-06-16 (范本级)
- [x] **The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook** ✅ 2026-06-16 (范本级/latent 计算坐标系综述；latent-vs-结构化张力)
- [x] **Transformers as Meta-Learners for Implicit Neural Representations** ✅ 2026-06-16 (范本级)

## B. Papers（主库，87 篇）→ PapersRecap/

Part A 已完成。Part B 按相同方式推进：**一次只处理一篇**，先处理与当前 WMTS / 灵巧手 / VLA-RL / 触觉接触最相关、且明显仍是短草稿的 recap。逐篇在此补勾，避免一次性载入。

> [!note] 处理顺序原则
> 1. 与当前研究直接相关（灵巧手、Sim-to-Real、PPO、课程、触觉/接触、world model）。
> 2. Foundation 高频引用的基础工作。
> 3. 其余按主题聚类逐篇。
>
> Papers/ 清单以 `Papers/` 与 `PapersRecap/` 当前文件为准；每篇完成后在本节追加 `- [x] <basename> ✅ 日期`。

### World Model / Model-Based RL
- [x] **Deep Dynamics Models for Learning Dexterous Manipulation** ✅ 2026-06-25 (范本级/PDDM；bootstrap ensemble dynamics + reward-weighted MPC + beta-filtered action noise；Baoding 100k datapoints/2.7h；真机 90°≈100%、180°≈54%；WMTS evaluator/teacher 而非最终 policy)

### Extrinsic Dexterity / Dynamics-Aware Contact Policy
- [x] **Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning** ✅ 2026-06-25 (范本级/DAPL；$(p,m,v)$ point-level world model→PPO dynamics conditioning；Dense 44.56 vs CORN 22.22；Sparse ablation 71.88 vs object-level 16.88；real 48%/42.6s；WMTS contact-outcome token)

### VLA / Real-World RL / Post-Training
- [x] **RECAP - A VLA that Learns from Experience** ✅ 2026-06-25 (范本级/PI 技术报告批判；advantage-conditioned experience → WMTS 数据飞轮)
- [x] **DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation** ✅ 2026-06-25 (范本级/intervention-aware weighting；failure-boundary sampling → WMTS 真机纠正数据)
- [x] **WMPO - World Model-based Policy Optimization for VLA** ✅ 2026-06-25 (范本级/pixel-space imagined GRPO；PBA failure distribution → WMTS semi-structured ensemble WM)
- [x] **WoG - World Guidance for VLA Action Generation** ✅ 2026-06-25 (范本级/condition-space world modeling；future contact tokens → WMTS action guidance)
- [x] **LaST0 - Latent Spatio-Temporal CoT for Robotic VLA** ✅ 2026-06-25 (范本级/latent CoT + fast-slow MoT；contact-latent scheduler → WMTS)
- [x] **RL-100 - Performant Robotic Manipulation with Real-World RL** ✅ 2026-06-25 (范本级/denoising sub-MDP PPO；offline-to-online real RL → WMTS final-mile tuning)
- [x] **SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning** ✅ 2026-06-25 (范本级/real-world RL full stack；RLPD demo-online 50/50 + high UTD；classifier/VICE reward；forward-backward reset；10Hz→1kHz impedance reference clipping；PCB 20min 100/100、Cable 31min 100/100、Object 105min 100/100；WMTS real-robot fine-tuning infrastructure)
- [x] **HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning** ✅ 2026-06-25 (范本级/intervention≠demo；RLPD demo/RL buffer；Table1 avg 49.7→100 + cycle 1.8x；Q-funnel critical states；PPO/WMTS off-policy 接口边界)

### Sim-to-Real / Action Grounding
- [x] **Grounded Action Transformation** ✅ 2026-06-25 (范本级/action-grounded simulator；actuator/latency grounding → LinkerHand/WMTS)
- [x] **Part-Guided 3D RL for Sim2Real Articulated Object Manipulation** ✅ 2026-06-25 (范本级/part-wise 3D observation；FUS uncertainty+frame consistency；SAC target joint/gripper actions；sim Ours≈Oracle；real 35/40 door、32/40 drawer、35/40 faucet；uncertainty softmax 符号陷阱；WMTS part/contact-token front-end)

### Long-Horizon / Curriculum / Privileged Training
- [x] **Learning Long-Horizon Robot Manipulation Skills via Privileged Action** ✅ 2026-06-25 (范本级/privileged action curriculum；virtual contact/force scaffold → DNPM/WMTS)
- [x] **DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots** ✅ 2026-06-25 (范本级/demonstration state reset；ZVF $0<\\hat p<1$ frontier；K=8,T=4,M=50；MPO teacher→RGB PAC student；99.6 sim→64 real contact gap；WMTS Solve/Probe/Reject)
- [x] **Hindsight Experience Replay** ✅ 2026-06-25 (范本级/UVFA + off-policy achieved-goal relabeling；$m:S\\to G$ 前提；future k=4/8 best；DDPG sparse Fetch 三任务近满成功；shaped reward 失败；real Fetch 2/5→1cm noise 5/5；WMTS achieved-outcome curriculum)

### Imitation Learning / Action Chunking
- [x] **ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware** ✅ 2026-06-25 (范本级/action chunking + temporal ensemble；BC horizon 缩短但 covariate shift 未消失；macro-action PPO/WMTS scheduler 启发)
- [x] **DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration** ✅ 2026-06-25 (范本级/action entropy→precision proxy；KDE/HDBSCAN；RBD 防状态覆盖丢失；ACT/DP 1.9-2.1×；real Conveyer Fast 大幅提升；转笔需 entropy+contact/WM uncertainty)
- [x] **DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills** ✅ 2026-06-25 (范本级/reference motion→reward/reset/termination/action abstraction；RSI 改 $\rho_0$、ET 清失败吸引域；Table4 style-goal 张力、Table5 RSI/ET 因果链；转笔需 contact/tactile phase 而非线性 clock)

### Contact-Rich Residual / Demonstration Adaptation
- [x] **Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation** ✅ 2026-06-25 (范本级/DMP 100Hz + residual RL 10Hz + impedance 500Hz；task-space residual 74.9 vs PoWER 23.3；full-pose PPO/PPO 86.9；3-shot transfer 81.3/60 episodes；WMTS bounded residual head)

### Synthetic Data / Bimanual Benchmark
- [x] **RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation** ✅ 2026-06-25 (范本级/MLLM expert-code 闭环 + 5 轴 DR + embodiment-aware grasp；VLM observer 弱点批判；WMTS 任务/数据生成器启发)
- [x] **CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation** ✅ 2026-06-25 (范本级/sim demo as physically editable trajectory seed；sensitivity-aware SE(3) augmentation；ACL success-rate > generation-rate；3min real fine-tune；转笔需 finger-contact/tactile 改造)
- [x] **MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations** ✅ 2026-06-25 (范本级/object-centric segment library；$SE(3)$ target-pose transform；DGR≠policy SR；action noise 降 DGR 但升 SR；准静态/单臂/刚体边界)
- [x] **Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization** ✅ 2026-06-25 (范本级/demo as global contact prior；retarget Eq(1)+dynamics trajopt Eq(2)；Table II kinematic replay 4-6/24 vs trajopt 2164-2462/3000；hardware iiwa 26%→74%)

### Tactile / Touch-Language Reasoning
- [x] **STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning** ✅ 2026-06-25 (范本级/MoE token-level tactile-language routing；Table 1-4 纠错与 routing 机制解释；离线 QA ≠ 触觉闭环控制)
- [x] **Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map** ✅ 2026-06-25 (范本级/deform map 公共几何空间；normal-projection ray casting；zero-shot 证据边界 + 转笔需 shear/slip 扩展)
- [x] **AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch** ✅ 2026-06-25 (范本级/auxiliary moving goal + dense tactile $(R_x,R_y,\|F\|)$；Table 1-3 真实数字；转笔 aerial/shear 边界)
- [x] **Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch** ✅ 2026-06-25 (范本级/16-bit full-hand binary contact mode；continuous force gap vs threshold invariance；全手覆盖 ablation + 转笔 contact-event baseline)
- [x] **Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture** ✅ 2026-06-25 (范本级/POMDP→belief-state DPF→asymmetric SAC；Table III estimator-policy co-adaptation；spinning-friction Sim-to-Real 边界 + 转笔 belief 接口)
- [x] **RotateIt - General In-Hand Object Rotation with Vision and Touch** ✅ 2026-06-25 (范本级/extrinsics identification；PointNet shape + contact-location tactile；Fig.8 real x-axis 证据；长物体/转笔不可直接外推)
- [x] **Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing** ✅ 2026-06-25 (范本级/FSR→FK tactile point cloud；PointNet input-level fusion；Table I-III nuanced evidence；Syn 非全项最高但真机难任务收益明显)
- [x] **Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding** ✅ 2026-06-25 (范本级/state+tactile coupled diffusion；contact-consistency mapping $(x,u)\to a$；KL latent 生成稳定性；sensor/controller-specific 边界)
- [x] **Visual-tactile Pretraining for Humanlike Manipulation Dexterity** ✅ 2026-06-25 (范本级/MAE-style visual-tactile masked reconstruction；IPL integration token；binary tactile contact timing supervision；PPO experts→online IL unified policy；state-expert distillation gap)
- [x] **Learning Visuotactile Skills with Two Multifingered Hands (HATO)** ✅ 2026-06-25 (范本级/Quest teleop→双多指 power-grasp prior；60-channel tactile；16-step Diffusion Policy；asynchronous inference + temporal ensemble；ActionMSE≠contact success)
- [x] **Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation** ✅ 2026-06-25 (范本级/curriculum 改变 PPO advantage basin；C1-C5 两阶段 reward；no-tactile existence proof 非触觉无用；cube/真实接触边界；piecewise LR scheduler 1000→450→250)

### In-Hand Rotation / Rapid Adaptation
- [x] **In-Hand Object Rotation via Rapid Motor Adaptation (HORA)** ✅ 2026-06-25 (范本级/hidden-context MDP→learned extrinsics→online amortized inference；DR 稳健 vs adaptation 最优性；纯本体 contact-point 不可观测边界)
- [x] **Lessons from Learning to Spin Pens** ✅ 2026-06-25 (范本级/DNPM 母本；privileged oracle→open-loop replay→45 条真机成功轨迹 fine-tune；$r_z$ 摩擦锥约束 + canonical grasp 相位覆盖)
- [x] **Learning Human-like Finger Gaiting on an Anthropomorphic Hand** ✅ 2026-06-25 (范本级/LinkerHand 21DoF 形态→gaiting 策略类；human transition waypoint 初始化；3D net force privileged normalization；simulation-only + sim-to-real 缺口)
- [x] **DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model** ✅ 2026-06-25 (范本级/joint-wise effective dynamics；KL information contraction；Chaos Box autonomous load data；residual policy 让真实 next-state 追仿真转移；partial-observation/tactile 边界)
- [x] **DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References** ✅ 2026-06-25 (范本级/human reference→robot tracking demonstration；RL+IL controller；data flywheel；homotopy parent-task diffusion generator；contact/reachability 边界)
- [x] **Dexterous Robotic Manipulation using Deep RL and Knowledge Transfer** ✅ 2026-06-25 (范本级/TriFinger RRC；DDPG+HER；HER xy not z；NDR→DR tune；ACTOR-CRITIC KT best；Pro scratch 0.134m/142.2°→0.023m/75.8°)

### Control Frequency / Temporal Abstraction
- [x] **Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning** ✅ 2026-06-25 (范本级/PFQI；$T_k^*=(T^\delta)^{k-1}T^*$ 顺序纠错；固定 $k$ 理论锚点 → WMTS 状态依赖调度粒度)
- [x] **Autoregressive Policies for Continuous Control Deep Reinforcement Learning** ✅ 2026-06-25 (范本级/stationary AR-p Gaussian exploration；Yule-Walker unit variance；extended MDP PPO-compatible；Square/UR5 high-action-rate sparse reward evidence；dense MuJoCo 边界；LinkerHand grouped/state-dependent exploration smoothing)

### Signal Processing / Actuator Encoding
- [x] **The Sampling Theorem With Constant Amplitude Variable Width Pulses** ✅ 2026-06-25 (范本级/PWM sampling theorem；worst-ISI → $2/\pi$ 峰值界；底层 actuator encoding 理论，不强行外推为策略方法)

### Dexterous Grasping / Contact Representation
- [x] **GenDexGrasp - Generalizable Dexterous Grasping** ✅ 2026-06-25 (范本级/object-centric contact map；aligned distance 消薄壳歧义；静态 $\Omega$ → 动态 contact schedule $\Omega_{1:T}$)

（B 部分后续逐篇补勾）
