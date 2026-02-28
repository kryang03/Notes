---
tags:
  - foundation
  - embodied-ai
  - vla
  - robot-learning
  - simulators
aliases:
  - 具身智能
  - VLA Models
  - Robot Learning Systems
created: 2026-02-02
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
---

# Embodied AI - 具身智能系统

# Embodied Intelligence Systems & Vision-Language-Action Models

---

## Core Concepts

具身智能 (Embodied AI) 是一种基于**物理实体**进行感知和行动的智能系统，通过智能体与环境的交互获取信息、理解问题、做出决策并实现行动。与纯软件 AI 不同，具身智能必须处理：
- **物理约束**: 真实世界的连续性、不可逆性
- **感知-行动闭环**: 实时反馈与响应
- **多模态融合**: 视觉、触觉、本体感受等多源信息整合

---

## 1. Vision-Language-Action (VLA) Models

### 1.1 核心架构范式

VLA 模型将视觉、语言和动作统一到端到端的神经网络框架中，实现从感知到执行的直接映射。

```
┌─────────────────────────────────────────────────────────────┐
│                    VLA Architecture                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐  │
│  │   Vision    │    │   Language   │    │    Action     │  │
│  │   Encoder   │───▶│   Backbone   │───▶│    Decoder    │  │
│  │ (ViT/CLIP)  │    │ (LLM 7B-70B) │    │ (Diffusion/AR)│  │
│  └─────────────┘    └──────────────┘    └───────────────┘  │
│         │                  │                    │          │
│         ▼                  ▼                    ▼          │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Multi-Modal Fusion Layer               │   │
│  │         (Cross-Attention / Concatenation)           │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 经典 VLA 模型演进

| 模型 | 机构 | 参数量 | 特点 | 关键创新 |
|------|------|--------|------|----------|
| **RT-1** | Google | 35M | 开创性工作 | Transformer-based action tokenization |
| **RT-2** | Google | 55B | VLM直接生成动作 | 动作作为文本token |
| **OpenVLA** | Stanford | 7B | 开源标杆 | Prismatic VLM backbone |
| **π₀** | Physical Intelligence | 3.3B | Flow Matching | 扩散策略 + VLM 结合 |
| **Octo** | UC Berkeley | 93M | 泛化能力 | Transformer + Diffusion |
| **RDT-1B** | THU | 1.2B | 双臂操作 | Scalable Diffusion Transformer |
| **3D-VLA** | - | - | 3D感知 | 3D scene representation |
| **SpatialVLA** | - | - | 空间推理 | Spatial reasoning enhanced |

### 1.3 VLA 的动作输出范式

**自回归 (Autoregressive) 方式**:
$$a_t = \arg\max_a P(a | s_{1:t}, g; \theta)$$

将动作离散化为 token，与文本生成统一处理。代表：RT-1, RT-2, OpenVLA

**扩散 (Diffusion) 方式**:
$$a_t = \mathcal{D}_\theta(\epsilon, s_t, g)$$

从噪声中逐步去噪生成连续动作。代表：Diffusion Policy, π₀, RDT

> [!note] 设计权衡
> - 自回归：推理快，但离散化损失精度
> - 扩散：动作平滑，但计算量大，延迟高
> - 混合策略：粗调用 AR，细调用 Diffusion

### 1.4 分层双系统 VLA (Hierarchical Dual-System)

受人类认知"快慢系统"启发，现代 VLA 架构常采用双层设计：

```
┌──────────────────────────────────────────────────────────┐
│  System 2 (Slow): High-Level Reasoning                   │
│  ─────────────────────────────────────────────────────   │
│  • 大型 VLM (7B-70B) 进行任务理解和规划                   │
│  • 输出: 子目标序列、语言指令                             │
│  • 频率: 1-10 Hz                                         │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  System 1 (Fast): Low-Level Control                      │
│  ─────────────────────────────────────────────────────   │
│  • 轻量级策略网络 (Diffusion/Flow Matching)               │
│  • 输出: 连续动作轨迹                                     │
│  • 频率: 50-200 Hz                                       │
└──────────────────────────────────────────────────────────┘
```

这与 [[ControlTheory]] 中的**分层控制**思想一致：高层任务规划 + 低层反馈控制。

---

## 2. Robot Learning Paradigms

### 2.1 学习范式对比

| 范式 | 核心思想 | 数据需求 | 典型算法 | 与灵巧操作的关联 |
|------|---------|---------|---------|-----------------|
| **强化学习 (RL)** | 试错学习 | 仿真交互 | PPO, SAC, TD3 | Sim-to-Real, 接触丰富任务 |
| **模仿学习 (IL)** | 专家示范 | 真机遥操 | BC, ACT, Diffusion Policy | 数据高效，但泛化受限 |
| **MPC** | 模型预测 | 动力学模型 | iLQR, MPPI | 精确控制，但建模困难 |
| **VLA** | 端到端 | 大规模多任务 | RT系列, OpenVLA | 语言条件任务 |

### 2.2 强化学习在机器人中的应用

> [!important] 与 [[ReinforcementLearning]] 的关系
> RL Foundation 文件侧重于算法理论 (MDP, Policy Gradient, Value Function)
> 本节侧重于 RL 在具身智能中的**系统层面应用**

**关键挑战**:

1. **Sample Efficiency**: 真实机器人交互成本高
   - 解决方案: Sim-to-Real, Domain Randomization, System Identification

2. **Reward Engineering**: 稀疏/延迟奖励
   - 解决方案: Reward Shaping, Curriculum Learning, Inverse RL

3. **Safety**: 训练过程中的安全约束
   - 解决方案: Constrained RL, Safe Exploration

**经典学习资源**:
- 西湖大学赵世钰《强化学习数学原理》
- UC Berkeley CS285 Deep RL
- CMU 10-703 Deep RL & Control
- OpenAI Spinning Up

### 2.3 模仿学习 (Imitation Learning)

**行为克隆 (Behavior Cloning)**:
$$\pi^* = \arg\min_\pi \mathbb{E}_{(s,a)\sim\mathcal{D}} \left[ \mathcal{L}(\pi(s), a) \right]$$

直接从专家数据学习策略映射，但存在**分布漂移** (covariate shift) 问题。

**现代 IL 架构**:
- **ACT (Action Chunking Transformer)**: 预测动作序列而非单步
- **Diffusion Policy**: 用扩散模型建模动作分布
- **DP3**: 3D感知增强的扩散策略

### 2.4 Sim-to-Real Transfer

从仿真到真实的迁移是具身智能的核心挑战之一：

```
┌─────────────────────────────────────────────────────────────┐
│                 Sim-to-Real Pipeline                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  Domain      ┌─────────────┐              │
│  │  Simulator  │─Randomization─▶│   Policy   │              │
│  │ (Isaac/Mujoco)│             │  Training   │              │
│  └─────────────┘              └──────┬──────┘              │
│         │                            │                      │
│  ┌──────▼──────┐              ┌──────▼──────┐              │
│  │  Physics    │              │  Trained    │              │
│  │ Randomization│              │   Policy    │              │
│  │ (mass,friction│              └──────┬──────┘              │
│  │  sensor noise)│                    │                      │
│  └─────────────┘              ┌──────▼──────┐              │
│                               │  Real Robot │              │
│                               │  Deployment │              │
│                               └─────────────┘              │
└─────────────────────────────────────────────────────────────┘
```

**Domain Randomization 参数**:
- 动力学: 质量、摩擦系数、关节阻尼
- 视觉: 光照、纹理、相机位姿
- 传感器: 噪声、延迟、dropout

---

## 3. Vision Foundation Models for Robotics

### 3.1 表征学习基础模型

| 模型 | 类型 | 输出 | 在机器人中的应用 |
|------|------|------|------------------|
| **CLIP** | 视觉-语言对齐 | 对齐特征 | 开放词汇物体识别 |
| **DINO/DINOv2** | 自监督视觉 | Dense特征 | 对应点匹配、部件理解 |
| **SAM/SAM2** | 分割 | Mask | 物体分割、视频追踪 |
| **Grounding-DINO** | 开放词汇检测 | BBox | 语言引导物体定位 |
| **FoundationPose** | 姿态估计 | 6DoF Pose | 物体姿态 |
| **Depth Anything** | 单目深度 | Depth Map | 深度感知 |

### 3.2 特征金字塔

```
┌─────────────────────────────────────────────────────────────┐
│              Vision Features for Robotics                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  High-Level (Semantic)          ┌─────────────────────┐     │
│  ─────────────────────         │ CLIP: "红色杯子"     │     │
│  • 物体类别                     └─────────────────────┘     │
│  • 语言关联                                                 │
│                                                             │
│  Mid-Level (Correspondence)     ┌─────────────────────┐     │
│  ─────────────────────         │ DINO: 部件对应       │     │
│  • 部件理解                     └─────────────────────┘     │
│  • 跨实例对应                                               │
│                                                             │
│  Low-Level (Geometric)          ┌─────────────────────┐     │
│  ─────────────────────         │ SAM + Depth: 3D点云  │     │
│  • 精确分割                     └─────────────────────┘     │
│  • 深度信息                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

> [!note] 与 [[RepresentationLearning]] 的关联
> Foundation Models 提供了强大的预训练表征，降低了下游任务的数据需求。
> 但在机器人领域，仍需考虑**动作相关的表征** (affordance-aware features)。

---

## 4. Simulators Ecosystem

### 4.1 主流仿真器对比

| 仿真器 | 引擎 | 优势 | 劣势 | 适用场景 |
|--------|------|------|------|----------|
| **Isaac Lab** | PhysX 5 | GPU并行、官方支持 | 学习曲线陡 | 大规模RL训练 |
| **MuJoCo** | 自研 | 精确、轻量 | CPU为主 | 精细操作、基准测试 |
| **SAPIEN** | PhysX | 易用、灵活 | 性能一般 | 快速原型验证 |
| **Genesis** | 多后端 | 4300万FPS、可微 | 较新 | 下一代研究 |
| **PyBullet** | Bullet | 免费、社区大 | 精度一般 | 教学入门 |

### 4.2 Isaac Lab 生态

```
┌─────────────────────────────────────────────────────────────┐
│                    Isaac Lab Ecosystem                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│  │  Isaac Lab    │  │  Isaac Sim    │  │   Omniverse   │   │
│  │  (RL框架)     │  │  (渲染引擎)   │  │   (平台)      │   │
│  └───────┬───────┘  └───────┬───────┘  └───────────────┘   │
│          │                  │                               │
│          └────────┬─────────┘                               │
│                   ▼                                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                   PhysX 5.0                          │   │
│  │  • GPU Tensor API                                    │   │
│  │  • Deformable Body                                   │   │
│  │  • Particle System                                   │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  常用环境:                                                   │
│  • legged_gym: 足式机器人                                   │
│  • bi-dexhands: 双灵巧手                                    │
│  • OmniGibson: 室内导航                                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.3 MuJoCo 生态

```
MuJoCo Ecosystem
├── MuJoCo Playground (Google DeepMind, 2025)
│   ├── dm_control suite 继任者
│   ├── MJX (JAX 加速)
│   └── GPU 并行仿真
├── Brax (可微仿真)
├── Robosuite (操作任务)
└── gymnasium (标准接口)
```

### 4.4 Genesis: 下一代仿真器

Genesis 是一个新兴的通用物理仿真平台，支持多种物理后端：

- **速度**: 最高 4300 万 FPS (Franka IK)
- **可微分**: 支持梯度计算
- **多后端**: 刚体、软体、流体统一

> [!tip] 选择建议
> - **入门学习**: MuJoCo + gymnasium
> - **大规模RL**: Isaac Lab
> - **快速原型**: SAPIEN + RoboTwin
> - **研究前沿**: Genesis

---

## 5. Hardware & Data Infrastructure

### 5.1 数据采集系统

| 系统 | 类型 | 特点 |
|------|------|------|
| **ALOHA** | 双臂遥操 | 低成本、开源 |
| **UMI** | 手持教学 | 无需机器人 |
| **GELLO** | 外骨骼 | 直觉操作 |
| **TeleMoMa** | 多模态 | VR集成 |

### 5.2 触觉传感器

与 [[SignalProcessing]] 和 [[ContactMechanics]] 紧密相关：

- **GelSight 系列**: 视触觉传感器，将触觉转化为视觉问题
- **电子皮肤**: 分布式压力感知
- **关节力矩传感器**: 力控基础

### 5.3 关键数据集

| 数据集 | 规模 | 机器人 | 特点 |
|--------|------|--------|------|
| **Open X-Embodiment** | 100万+ | 多平台 | 谷歌主导 |
| **DROID** | 76K | Franka | 真机数据 |
| **RH20T** | 20T | 多平台 | 清华主导 |

---

## 6. Embodied AI for X

### 6.1 Healthcare Robotics

医疗机器人的特殊要求：
- **安全性**: 接触人体需要严格的力控制
- **精度**: 微创手术的高精度需求
- **交互**: 康复机器人的自适应

关键技术：
- Surgical Autonomy Levels (L0-L5)
- Force Feedback Control
- Compliant Mechanisms

### 6.2 UAV (Unmanned Aerial Vehicles)

无人机仿真器：
- **AirSim**: UE4 引擎，微软开源
- **Flightmare**: Unity 引擎，高效
- **AerialGym**: Isaac Sim 集成

控制层次：
```
高层: 任务规划 (Mission Planning)
  ↓
中层: 路径规划 (Path Planning)
  ↓
低层: 姿态控制 (Attitude Control) → PID/LQR
```

### 6.3 Autonomous Driving

端到端驾驶与传统模块化的对比：

| 方面 | 模块化 | 端到端 |
|------|--------|--------|
| 可解释性 | 高 | 低 |
| 开发复杂度 | 高 | 低 |
| 数据需求 | 中 | 高 |
| 代表 | Apollo, Autoware | Tesla FSD |

---

## Evolution & Insights

### VLA 发展脉络

```
2022: RT-1 开创性工作
  ↓
2023: RT-2 (VLM直接输出动作)
  ↓   Diffusion Policy (扩散建模动作)
2024: OpenVLA (开源7B)
  ↓   π₀ (Flow Matching)
2025: 分层双系统成为主流
      3D感知增强 (3D-VLA, SpatialVLA)
```

### 关键洞见

> [!quote] Insight 1: Scaling Law in Robotics
> 与 LLM 类似，机器人基础模型展现出 scaling 特性：更多数据、更大模型 → 更好泛化

> [!quote] Insight 2: Simulation is Key
> 仿真器质量决定了 Sim-to-Real 的上限。可微仿真是下一个前沿。

> [!quote] Insight 3: Data Flywheel
> 采集 → 训练 → 部署 → 自动采集 的闭环是规模化的关键。

---

## Implementation

### 开源代码库

| 项目 | 功能 | 链接 |
|------|------|------|
| **LeRobot** | HuggingFace 机器人库 | `huggingface/lerobot` |
| **OpenVLA** | VLA 训练框架 | `openvla/openvla` |
| **π₀** | Physical Intelligence 开源 | `Physical-Intelligence/openpi` |
| **RoboTwin 2.0** | 双臂仿真平台 | `robotwin-Platform/robotwin` |
| **Isaac Lab** | NVIDIA RL框架 | `isaac-orbit/IsaacLab` |

### 学习路径建议

```
入门路径 (建议1周完成):
├── 1. 用 RoboTwin 2.0 走通策略训练全流程
│   ├── 数据生成
│   ├── 策略训练 (BC/Diffusion)
│   └── 仿真评测
├── 2. 阅读 Diffusion Policy 论文 + 代码
└── 3. 尝试在真机上部署 (如有条件)

进阶路径:
├── 深入学习 [[ReinforcementLearning]] 基础
├── 研究 VLA 模型架构 (RT-2, OpenVLA)
├── 探索 Sim-to-Real 技术
└── 关注 3D 感知与触觉融合
```

---

## Cross-Domain Links

- **[[ReinforcementLearning]]**: RL算法是Robot Learning的核心，PPO/SAC广泛应用
- **[[ControlTheory]]**: 分层控制、阻抗控制是低层执行的基础
- **[[Dynamics]]**: 仿真器的物理建模基础
- **[[ContactMechanics]]**: 操作任务的接触力学
- **[[RepresentationLearning]]**: Vision Foundation Models的理论基础
- **[[Optimization]]**: MPC、轨迹优化

---

## 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文在其研究中涉及具身智能的核心主题

### Diffusion Policy & 生成式策略
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] — 规划引导的扩散策略，双臂操作
- [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] — 仿真数据自动生成
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 物理驱动数据生成

### Sim-to-Real & 迁移学习
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 可组合 Sim-to-Real
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] — 仿真增强真实演示
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] — Real-to-Sim-to-Real

### 触觉与多模态感知
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] — 视触觉遥操作
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] — 视触觉联觉表征
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] — 纯触觉手内操作

---

## References & Resources

### 社区与资源

- **Lumina 具身智能社区**: https://lumina-embodied.ai/
- **Embodied-AI-Guide**: https://github.com/TianxingChen/Embodied-AI-Guide (11.6k stars)
- **Simulately Wiki**: https://simulately.wiki/
- **DeepTimber Paper Reading**: https://github.com/DeepTimber-Robot-Lab/Paper-Reading-List

### 高质量会议/期刊

**Top-tier**: Science Robotics, TRO, IJRR, RSS, CoRL
**AI交叉**: NeurIPS, ICML, ICLR, CVPR, ICCV
**机器人**: ICRA, IROS, RAL
