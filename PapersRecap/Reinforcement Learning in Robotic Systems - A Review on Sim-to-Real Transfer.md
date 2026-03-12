---
tags:
  - paper
  - survey
  - sim-to-real
  - reinforcement-learning
  - robotics
aliases:
  - Sim-to-Real Robotics Review
  - Tiwari et al. Sim2Real
paper-year: 2026
read-date: 2026-03-13
venue: Robotics and Autonomous Systems (Elsevier)
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
---

# Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer

> [!abstract] 核心贡献
> 面向机器人系统的 sim-to-real RL 综述，从**仿真逼真度提升**、**执行器级建模**和**域随机化**三条主线展开，提出涵盖仿真模型优化→策略迁移→迭代精炼的统一框架。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — Sim-to-real 经典分类: System ID、Domain Randomization、Domain Adaptation、Multi-fidelity Learning
> - [[Dynamics]] — 执行器建模 (actuator-level modeling) 与物理引擎逼真度

## 1. 核心整理价值

### Sim-to-real 方法分类
1. **System Identification** — 估计真实动力学参数映射到仿真
2. **Domain Randomization** — 环境/机器人参数随机化
3. **Domain Adaptation** — 真实数据辅助对齐
4. **Multi-fidelity Learning** — 从低→高逼真度梯度学习

### 关键见解
- **仿真器逼真度 vs 域随机化是互补关系而非替代**——高逼真度仿真缩小 gap 基础，域随机化提供鲁棒性
- **执行器建模** 被传统 sim-to-real 综述忽视，但在灵巧操作中至关重要（高减速比关节的非线性响应）
- Progressive Neural Networks 的"策略迁移 (policy migration)"范式在 sim-to-real 中被再次验证有效

### 与 [[A Survey of Sim-to-Real Methods in RL|Da et al. Survey]] 的互补
- Da et al. 以 MDP 四要素为分类轴，侧重方法论
- 本文以机器人系统工程为视角，侧重仿真器构建和执行器建模

## 2. 对 DNPM 项目的启发

> [!note] 关键洞见
> - 执行器级建模对高减速比伺服（谐波减速器 >100:1）的 sim-to-real 至关重要
> - 本项目中 LinkerHand 使用高减速比舵机，[[Minimalist Compliance Control]] 的效率模型本质上是一种 actuator-level grounding
> - Multi-fidelity 方法可用于 DNPM: 先在 rigid body sim 学习粗策略，再在含柔性/接触 sim 中精炼
