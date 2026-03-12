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
| [[ControlTheory\|Control]] | 稳定性与交互 | Operational Space / franka_ros | 变阻抗控制 (Variable Impedance) |
| [[Dynamics]] | 物理建模 | ABA / RNEA / pinocchio | 可微物理引擎 (Brax, Dojo) |
| [[ContactMechanics\|Contact Mech.]] | 交互物理 | GJK / EPA / Friction Cones | 软指模型, 黏滞-滑移检测 |
| [[ReinforcementLearning\|RL]] | 行为学习 | PPO / SAC / Stable-Baselines3 | Sim-to-Real, 域随机化 |
| [[SignalProcessing\|Signal Proc.]] | 状态估计 | EKF / Particle Filter | 视触觉感知 (GelSight as Vision) |
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
    │Geometry │  │ Theory  │  │ Process │
    └─────────┘  └─────────┘  └─────────┘
```

---

## 领域交叉关系

### 强关联 (Strong Coupling)

| 领域 A | 领域 B | 交叉点 |
|-------|-------|-------|
| [[ControlTheory]] | [[Dynamics]] | 动力学一致逆运动学、OSF |
| [[ContactMechanics]] | [[Dynamics]] | 接触动力学、LCP |
| [[ReinforcementLearning]] | [[ControlTheory]] | 稳定性约束RL、Safe RL |
| [[Optimization]] | [[ControlTheory]] | MPC、轨迹优化 |
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
从位置控制转向力/位混合控制，以及处理非线性的能力。

### [[Optimization|优化理论]]
轨迹优化是现代操作的核心，MPC 是实时性的关键。

### [[ReinforcementLearning|强化学习]]
解决接触丰富、难以建模的复杂操作任务。

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
| [[WMPO - World Model-based Policy Optimization for VLA\|WMPO]] | RL, EmbodiedAI, StochasticProcess || [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding|CGP]] | ContactMech, Control, ReprLearn, SignalProc |
| [[Minimalist Compliance Control|MCC]] | Control, Dynamics, ContactMech |
| [[DexHiL - Human-in-the-Loop VLA Post-Training for Dexterous Manipulation|DexHiL]] | EmbodiedAI, RL, ReprLearn |
| [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Penetration Depth Map|Tacmap]] | SignalProc, CompGeo, RL, ContactMech |
| [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] | RL, ContactMech, Dynamics, ReprLearn |
| [[Grounded Action Transformation|GAT]] | RL, Dynamics |
| [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|SToLa]] | SignalProc, ReprLearn, InfoTheory |
| [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Robotic Manipulation|RoboTwin 2.0]] | EmbodiedAI, RL |
| [[A Survey of Sim-to-Real Methods in RL|Sim-to-Real Survey]] | RL, EmbodiedAI |
| [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer|Tiwari Sim2Real]] | RL, Dynamics |
| [[空间智能作为机器人的结构化表征|PointWorld]] | EmbodiedAI, ReprLearn, CompGeo, Dynamics |
| [[谐波减速器与RV减速器选型核心区分依据|谐波 vs RV]] | Dynamics, Control |
---

## 相关项目

- [[Dynamic Non-Prehensile Manipulation]] - 动态非抓取灵巧操作研究
