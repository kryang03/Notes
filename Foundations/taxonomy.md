---
tags:
  - index
  - taxonomy
  - meta
aliases:
  - 领域分类
  - Domain Taxonomy
created: 2026-01-31
---

# 灵巧操作知识领域分类

# Dexterous Manipulation Knowledge Taxonomy

---

## 领域速查表

| 领域 (Domain) | 核心关注 (Primary Focus) | 关键实现/库 (Key Implementation) | 现代 Value-Add (Modern Insight) |
|--------------|-------------------------|--------------------------------|-------------------------------|
| [[Optimization]] | 决策生成 | iLQR / OSQP / cvxpy | 可微优化层 (Diff. Layers), MPC |
| [[ControlTheory\|Control]] | 稳定性与交互 | Transfer Function / State-space / LQR / SDP | 古典频域/状态空间 + 阻抗/导纳分层 + 数据驱动 LMI 证书 |
| [[Actuation\|执行器]] | 力矩兑现与传递 | FOC / Clarke-Park / Actuator Net / 谐波减速 | 电流→关节力矩全链路 + 力矩-转速包络 + 执行器 Sim-to-Real |
| [[Dynamics]] | 物理建模 | ABA / RNEA / pinocchio | 可微物理引擎 (Brax, Dojo) |
| [[ContactMechanics\|Contact Mech.]] | 交互物理 | GJK / EPA / Friction Cones | 软指模型, 黏滞-滑移检测 |
| [[ReinforcementLearning\|RL]] | 行为学习 | TD / PPO / SAC / Stable-Baselines3 | 代码级 PPO 数据流, Sim-to-Real |
| [[WorldModels\|World Model]] | 想象中试错 | RSSM / Dreamer / PETS / TD-MPC / 扩散 WM | 认知不确定性驱动规划-安全-课程, Actuator+Rigid 解耦 |
| [[SignalProcessing\|Signal Proc.]] | 时频分析与状态估计 | Fourier / STFT / Wavelet / KF-EKF-PF | 采样带宽约束 + 视触觉状态估计 |
| [[InformationTheory\|Info. Theory]] | 不确定性与探索 | Mutual Information / Entropy | 内在动机, 表征解耦 |
| [[ComputationalGeometry\|Comp. Geometry]] | 空间推理 | SDFs / Voronoi / trimesh | 隐式神经表示 (Neural Fields) |
| [[StochasticProcess\|Stochastic Proc.]] | 随机建模 | Gaussian Processes / SDEs | 扩散策略 (Diffusion Policies) |
| [[RepresentationLearning\|Representation]] | 特征提取 | VAE / Contrastive Learning | 多模态融合, 流形学习 |
| [[EmbodiedAI\|Embodied AI]] | 端到端系统 | VLA / Isaac Lab / Diffusion Policy | 从感知到动作的统一建模 |

---

## 领域关联图

```
                        ┌─────────────────┐
                        │   Dexterous     │
                        │  Manipulation   │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
   ┌───────────┐          ┌───────────┐          ┌───────────┐
   │  Physics  │          │  Control  │          │ Learning  │
   │  Modeling │          │ & Decision│          │ & Sensing │
   └─────┬─────┘          └─────┬─────┘          └─────┬─────┘
         │                      │                      │
    ┌────┴────┐            ┌────┴────┐            ┌────┴────┐
    │         │            │         │            │         │
    ▼         ▼            ▼         ▼            ▼         ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Dynamics│ │Contact │ │Control │ │Optim.  │ │  RL    │ │Signal  │
│        │ │Mech.   │ │Theory  │ │        │ │        │ │Proc.   │
└───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
    │          │          │          │          │          │
    └──────────┴──────┬───┴──────────┴──────────┴──────────┘
                      │
              ┌───────┴───────┐
              │  Foundations  │
              │   交叉领域     │
              └───────┬───────┘
                      │
     ┌────────────────┼────────────────┐
     ▼                ▼                ▼
┌─────────┐     ┌─────────┐     ┌─────────┐
│ Comp.   │     │ Info.   │     │Stochast.│
│Geometry │     │ Theory  │     │ Process │
└─────────┘     └─────────┘     └─────────┘
     │                │                │
     └────────────────┼────────────────┘
                      ▼
              ┌─────────────┐
              │ Embodied AI │
              │   VLA/E2E   │
              └─────────────┘
```

---

## 领域交叉关系

### 强关联 (Strong Coupling)

| 领域 A | 领域 B | 交叉点 |
|-------|-------|-------|
| [[ControlTheory]] | [[Dynamics]] | 动力学一致逆运动学、OSF |
| [[Actuation]] | [[ControlTheory]] | 电流/速度/位置串级环、Luenberger 观测器、相位裕度、阻抗与反驱动性 |
| [[Actuation]] | [[Dynamics]] | 操作器方程右端的 $\tau$、腱耦合矩阵 $P$、reflected inertia、神经动力学残差 |
| [[Actuation]] | [[ReinforcementLearning]] | 执行器 Sim-to-Real gap（Action/Transition）、DR 参数、actuator net |
| [[WorldModels]] | [[ReinforcementLearning]] | Model-Based RL、想象训练、Dreamer latent actor-critic |
| [[WorldModels]] | [[StochasticProcess]] | PETS ensemble、epistemic 不确定性、model exploitation |
| [[WorldModels]] | [[Dynamics]] | 学出来的动力学、physics-informed、Actuator+Rigid 解耦 |
| [[WorldModels]] | [[InformationTheory]] | ensemble 分歧＝信息增益＝认知不确定性驱动课程 |
| [[ContactMechanics]] | [[Dynamics]] | 接触动力学、LCP |
| [[ReinforcementLearning]] | [[ControlTheory]] | 稳定性约束RL、Safe RL |
| [[Optimization]] | [[ControlTheory]] | MPC、轨迹优化 |
| [[ControlTheory]] | [[SignalProcessing]] | 频率响应/采样延迟、状态估计、噪声数据鲁棒镇定、数据驱动 LMI 证书 |
| [[ReinforcementLearning]] | [[StochasticProcess]] | 扩散策略、GP-based RL |
| [[InformationTheory]] | [[ReinforcementLearning]] | Mediator奖励、RL Scaling Laws 熵控制、内在动机 |
| [[InformationTheory]] | [[SignalProcessing]] | 压缩-去噪对偶性、率失真→触觉去噪 |

### 弱关联 (Weak Coupling)

| 领域 A | 领域 B | 潜在交叉 |
|-------|-------|---------|
| [[ComputationalGeometry]] | [[ReinforcementLearning]] | 神经场表示用于RL |
| [[SignalProcessing]] | [[RepresentationLearning]] | 触觉特征提取 |
| [[EmbodiedAI]] | [[ControlTheory]] | 分层VLA中的低层控制 |
| [[EmbodiedAI]] | [[ReinforcementLearning]] | Robot Learning范式 |
| [[EmbodiedAI]] | [[RepresentationLearning]] | Vision Foundation Models |

---

## 跨 Foundation 暗线（记忆主线，2026-07-12 并行深化织入）

> [!abstract] 为什么设"暗线"
> 本库的价值在**关联**。经两轮并行深化 + LLM 后训练脉络融入，13 个 Foundation 已被 8 条反复出现的**暗线 (leitmotif)** 缝成一体——同一个数学/物理结构在多个模块以不同面貌出现。**顺着暗线走，就能把散在各模块的知识点串成一条记忆链**。补充/复习任何知识点时，先问"它挂在哪条暗线上"。

| # | 暗线 | 一句话 | 关键节点（顺链复习） |
|:-:|:--|:--|:--|
| 1 | **对偶性 $J/G/P$** | 手雅可比、抓取矩阵、腱耦合矩阵数学同构，力闭合/冗余/零空间工具三处复用 | [[Dynamics#8.1 腱网络运动学：耦合矩阵 $P$\|P]] · [[ContactMechanics#3.1 抓取矩阵的严格定义与内力\|G]] · [[ControlTheory#2.1 虚功原理与对偶性\|虚功对偶]] · [[Optimization#2.3 KKT 条件：约束最优的"语法"\|KKT乘子=约束反力]] |
| 2 | **价值即 Lyapunov** | 值函数=Lyapunov 函数；Bellman↔HJB、Riccati↔价值迭代↔稳定性证书 | [[ControlTheory#11. 线性二次最优控制 (LQR)\|LQR/Riccati]] · [[Optimization#6.1 iLQR/DDP：动态规划结构上的 Gauss-Newton\|iLQR]] · [[ReinforcementLearning#2.2 值函数与 Bellman 方程\|Bellman]] · [[ControlTheory#10.4 被动性与"价值即 Lyapunov"\|passivity]] |
| 3 | **认知不确定性三用** | ensemble 分歧=epistemic=信息增益：规划护栏 / 探索罗盘 / 课程"该学处" | [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性\|PETS]] · [[InformationTheory#2.2 互信息：观测的"切割能力"\|BALD]] · [[StochasticProcess#3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic\|epistemic]] · [[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成\|课程]] · [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间\|自动课程]] |
| 4 | **Continuation / 平滑化** | 先解平滑近凸子问题再逐步引入真难度：接触平滑 / 课程 $Q_0\to Q_1$ / 扩散去噪 | [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）\|接触平滑]] · [[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间\|课程continuation]] · [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器\|扩散]] |
| 5 | **POMDP → belief → latent** | 部分可观→充分统计量 belief→世界模型 latent（RSSM）；历史窗口是解药 | [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学\|POMDP]] · [[SignalProcessing#5. 状态估计：从局部触觉到全局语义\|KF/PF祖先]] · [[StochasticProcess#4.0 贝叶斯滤波的骨架：预测-更新递推（KF→EKF→UKF→PF 一张阶梯）\|Bayes滤波]] · [[WorldModels#2. 预测层：在 latent 里推演未来\|RSSM]] · [[RepresentationLearning#4.6 序列与注意力表征：从无序集合到有序序列\|注意力≈belief]] |
| 6 | **采样 + 加权 统一优化** | CMA-ES（参数）、MPPI（控制序列）、策略梯度（动作）同宗：采样→按 fitness 加权→挪分布 | [[Optimization#4.4 零阶与进化优化：当梯度根本求不出来（CMA-ES）\|CMA-ES]] · [[StochasticProcess#6. 随机最优控制：MPPI（用采样代替梯度）\|MPPI]] · [[ReinforcementLearning#4.1 策略梯度定理：log-derivative 技巧\|策略梯度]] |
| 7 | **电流 ≠ 关节力矩 / τ 身份错位** | 仿真把 $\tau$ 当输入直接施加；真机 $\tau$ 是电机→FOC→减速器→传动链的输出=Sim-to-Real gap 物理来源 | [[Actuation#9.2 完整力矩传递链模型\|力矩传递链]] · [[Dynamics#5.2 RNEA：$O(N)$ 逆动力学（控制的基石）\|RNEA给需求]] · [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦\|Actuator+Rigid解耦]] · [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机\|Sim-to-Real]] |
| 8 | **KL 方向决定 covering vs seeking** | 前向 KL→mode-covering→SFT"学会做"（覆盖所有演示、易均值坍缩）；反向 KL→mode-seeking→RL/RLHF"学会选"（挑高奖励峰、天然 KL 小） | [[InformationTheory#2.3.1 前向 KL vs 反向 KL 的几何：为什么方向决定 covering vs seeking（SFT vs RL）\|KL几何]] · [[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家\|统一梯度]] · [[EmbodiedAI#2.3.1 一条更深的暗线：On-Policy Distillation (OPD) —— 从 LLM 后训练到 Oracle→Generalist 蒸馏\|OPD]] · [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器\|扩散=覆盖做对]] |

> [!tip] 用法
> 复习/补写时，任一知识点都应能回答"它在哪条暗线的哪一环"。若一个新知识点挂不上任何暗线，要么它是孤立的（补关联），要么它揭示了**第 8 条暗线**（值得单列）。

---

## Foundation 理论大厦骨架索引

> [!abstract] 本轮 Foundation 补齐标准
> 每个 Foundation 不再只保存定义，而要显式回答“理论从哪里来、如何逐层构建、怎样落到灵巧操作失败模式或算法设计”。以下表格用于快速定位各领域的主线。

| Foundation | 理论构建主线 | 关键落点 |
|-----------|--------------|----------|
| [[Dynamics]] | 几何表示 → 能量原理 → 约束动力学 → RNEA/ABA → 接触仿真 → 真机残差 | 高 DoF 多体求解、接触 solver、执行器建模 |
| [[ContactMechanics]] | 接触几何 → 接触运动学 → 接触静力学 → 接触动力学 → 可微接触 | 力闭合、摩擦锥、LCP、可微物理 |
| [[ComputationalGeometry]] | 集合运算 → 凸支持函数 → GJK/EPA → SDF → 神经隐式几何 | 最近点、法向、穿透深度、优化梯度 |
| [[ControlTheory]] | 系统描述 → 稳定性 → 频域/延迟 → 柔顺控制 → MPC/OSF → 数据证书 | 负反馈、阻抗/导纳、相位裕度、安全闭环 |
| [[Actuation]] | 电机模型 → FOC 降维 → 串级环/观测器 → 电气热极限 → 传动/减速 → 执行器 gap → actuator net | 电流→关节力矩、力矩-转速包络、背隙/Stribeck、reflected inertia、热漂移 |
| [[Optimization]] | 可行域 → 目标函数 → 求解器 → 非凸景观 → CITO → 学习加速 | 轨迹优化、接触隐式、实时 MPC |
| [[ReinforcementLearning]] | MDP/POMDP → Bellman/TD → 策略梯度 → 稳定更新 → 样本效率 → Sim-to-Real | PPO/SAC、credit assignment、真机安全数据利用 |
| [[WorldModels]] | 表征(latent) → 预测(RSSM) → 不确定性(ensemble) → 利用(Dyna/MPC/Dreamer) → 结构(Actuator+Rigid) → 部署(安全/课程) | 想象试错、认知不确定性、model exploitation、真机安全调度 |
| [[StochasticProcess]] | SDE → 马尔可夫性 → Bayes filter → GP/ensemble → MPPI → 随机互补 | belief、uncertainty、robust rollout |
| [[SignalProcessing]] | 转导 → 采样 → 频域 → 时频 → 状态估计 → 控制接口 | 触觉滤波、滑移检测、KF/EKF/UKF/PF |
| [[InformationTheory]] | belief → 熵/KL/MI → 主动感知 → 物理代价耦合 → 信息瓶颈/empowerment | 预期信息增益、主动触摸、表征压缩 |
| [[RepresentationLearning]] | 重构 → 对比 → 几何 → 动作 → 因果表征 | 触觉/视觉 latent、3D flow、Diffusion/Flow Matching |
| [[EmbodiedAI]] | 任务语义 → 空间 grounding → 动作生成 → 低层控制 → 数据飞轮 | VLA、action chunk、world model、真机闭环 |

---

## 各领域研究侧重点

> [!note] 灵巧操作视角
> 以下是从灵巧操作角度对各领域的研究侧重点定义

### [[Dynamics|动力学]]
从刚体到多体，再到接触动力学。灵巧手的高维特性要求极其高效的动力学解算。

### [[ContactMechanics|接触力学]]
这是灵巧操作的灵魂。从点接触到软指接触，从库伦摩擦到 LCP。

### [[ComputationalGeometry|计算几何]]
碰撞检测是运动规划的前置，SDF 是现代操作优化的核心。

### [[ControlTheory|控制理论]]
从位置控制转向阻抗/导纳分层、力/位混合控制、鲁棒/自适应控制，以及用短真机数据给出稳定性证书的数据驱动控制。

### [[Actuation|执行器与驱动]]
仿真把关节力矩当理想输入，真机里它要穿过电机→FOC→减速器→传动才到关节。机械差异（背隙、Stribeck 摩擦、扭转弹性、reflected inertia）与电气差异（电流环带宽、反电动势天花板、热漂移）共同构成执行器级 Sim-to-Real gap；用 actuator net 学"仿真 PD 没覆盖的那段残差"，是 [[ControlTheory]] 与 [[Dynamics]] 之间"力矩兑现"的缺失一环。

### [[Optimization|优化理论]]
轨迹优化是现代操作的核心，MPC 是实时性的关键。

### [[ReinforcementLearning|强化学习]]
解决接触丰富、难以建模的复杂操作任务；重点追踪 TD credit assignment、PPO rollout/update 数据流与真机 Sim-to-Real 约束。

### [[WorldModels|世界模型]]
把"在真机试错"换成"在学出来的脑内引擎里试错"。核心不是预测多准，而是用 ensemble 认知不确定性同时做三件事：规划兜底（别钻模型空子）、安全调度（拦截 OOD 动作）、课程生成（无知处即该学处）。[[Final_WMTS|WMTS]] 项目把 WM 拆成 Actuator+Rigid 两级以隔离[[Actuation|执行器]] Sim-to-Real gap。

### [[StochasticProcess|随机过程]]
操作充满了不确定性（物体质量、摩擦系数未知）。

### [[SignalProcessing|信号处理]]
触觉信号处理与状态估计。

### [[InformationTheory|信息论]]
探索（Exploration）与感知的主动性。率失真理论为压缩-去噪对偶性提供统一框架，Mediator因果推断为奖励设计提供信息论基础。

### [[RepresentationLearning|表征学习]]
多模态融合与流形学习。

### [[EmbodiedAI|具身智能]]
从感知到动作的端到端系统，VLA模型将视觉-语言-动作统一建模。仿真器生态和Sim-to-Real是关键挑战。

---

## 相关论文索引

| 论文 | 相关领域 |
|-----|---------|
| [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] | RL, Control |
| [[Elastic Time Step Reinforcement Learning, VTS-RL]] | RL, Optimization |
| [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] | RL, Control |
| [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training\|GeoPT]] | Dynamics, CompGeo, ReprLearn |
| [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA\|LaST0]] | EmbodiedAI, ReprLearn, RL |
| [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control\|OmniXtreme]] | RL, Control, Dynamics |
| [[RL-100 - Performant Robotic Manipulation with Real-World RL\|RL-100]] | RL, StochasticProcess, Control |
| [[WMPO - World Model-based Policy Optimization for VLA\|WMPO]] | RL, EmbodiedAI, StochasticProcess |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]] | ContactMech, Control, ReprLearn, SignalProc |
| [[Minimalist Compliance Control|MCC]] | Control, Dynamics, ContactMech |
| [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]] | EmbodiedAI, RL, ReprLearn |
| [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] | SignalProc, CompGeo, RL, ContactMech |
| [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] | RL, ContactMech, Dynamics, ReprLearn |
| [[Grounded Action Transformation|GAT]] | RL, Dynamics |
| [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|SToLa]] | SignalProc, ReprLearn, InfoTheory |
| [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation|RoboTwin 2.0]] | EmbodiedAI, RL |
| [[A Survey of Sim-to-Real Methods in RL\|Sim2Real Survey]] | RL, Dynamics, EmbodiedAI |
| [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer|Tiwari Sim2Real]] | RL, Dynamics |
| [[空间智能作为机器人的结构化表征|PointWorld]] | EmbodiedAI, ReprLearn, CompGeo, Dynamics |
| [[谐波减速器与RV减速器选型核心区分依据|谐波 vs RV]] | Dynamics, Control |

---

## 相关项目

- [[Dynamic Non-Prehensile Manipulation]] - 动态非抓取灵巧操作研究
  - [[sim2real\|硬件 Sim-to-Real Gap 分析]] — 电机/减速器/传动选型对 RL 仿真迁移的影响
