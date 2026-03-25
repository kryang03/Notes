---
tags:
  - paper
  - survey
  - sim-to-real
  - reinforcement-learning
aliases:
  - RL sim-to-real review
  - Tiwari 2026 review
paper-year: 2026
read-date: 2026-03-13
venue: Robotics and Autonomous Systems
paper-pdf: "[[Papers/Reinforcement learning in robotic systems - A review on sim-to-real transfer.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[EmbodiedAI]]"
---

# Reinforcement Learning in Robotic Systems: A Review on Sim-to-Real Transfer

> [!abstract] 核心贡献
> 从信息流和方法作用对象的角度，提出 sim-to-real 迁移的统一框架，将现有方法分为三大类：面向真实环境的模型优化、基于仿真环境的知识迁移、仿真-现实迭代策略精炼。综述了 System ID、DR、Domain Adaptation、Multi-Fidelity、Progressive Neural Networks 等方法。

## 1. 综述框架

### 三大类 Sim-to-Real 方法

| 类别 | 核心思路 | 代表方法 |
|------|---------|---------|
| **模型优化** | 让仿真更接近真实 | System ID, 物理参数辨识, 执行器建模 |
| **知识迁移** | 让策略对 Gap 鲁棒 | Domain Randomization, Domain Adaptation, Transfer Learning |
| **迭代精炼** | 仿真-真实交替优化 | Real-to-Sim-to-Real (R2S2R), Multi-Fidelity Learning |

### 关键概念

- **Reality Gap**: 物理动力学、感知输入、环境变异性的系统性差异
- **MDP 框架**: $\mathcal{M} = (S, A, P, R, \gamma)$ — sim/real 的 $P$, $R$ 差异是 Gap 的数学本质
- **仿真优势**: 低成本、可真实性、多维度、安全性

## 2. 方法分类总结

### System Identification
- 物理参数辨识 → 仿真器校准
- 自动化调优趋势

### Domain Randomization
- 环境参数 + 机器人参数
- 从均匀分布到 ADR (Automatic DR)

### Domain Adaptation
- 仿真→真实的表征对齐
- 对抗训练 (GAN-based)

### 新兴方向
- **Progressive Neural Networks**: 列式扩展防止灾难性遗忘
- **执行器级建模**: 精确的电机/传动仿真
- **R2S2R 管线**: 真实数据反馈→仿真改进→策略重训

## 3. 核心洞见 (Insights)

1. **System ID 与 DR 互补**: 前者提升仿真保真度，后者提升策略鲁棒性 → 与 [[ReinforcementLearning#5.0 系统辨识与在线参数学习 (System Identification & Online Adaptation)|RL §5.0]] 的"正交关系"分析一致
2. **执行器建模被低估**: 大多数 sim-to-real 工作忽视电机/驱动器级别建模 → 与 [[ControlTheory#Sim-to-Real 迁移中的控制挑战|ControlTheory sim-to-real]] 中的硬件 Gap 分析呼应
3. **统一框架思维**: 从信息流角度审视迁移方法，有助于识别方法组合策略

## 4. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- 为 §5 Sim-to-Real 提供了系统性的分类视角
- 补充了 Progressive Neural Networks、Multi-Fidelity 等未被充分覆盖的方法

### 与 [[Dynamics]] 的联系
- System ID 和执行器建模直接关联 [[Dynamics#Sim-to-Real 与动力学迁移|动力学迁移]]
- 仿真器物理保真度是所有方法的底层依赖

### 与 [[EmbodiedAI]] 的联系
- 基准平台综述: Real Robot Challenge, HomeRobot/OVMM, NAO testbed
- 与社区走向标准化评估的趋势一致

## 5. 局限

- 作为综述，缺乏新的实验验证
- 对灵巧操作场景的覆盖较少（多为 locomotion/navigation 视角）
- 对 VLA 等最新范式的覆盖不足

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **Sim-to-Real 分类学习**: 本综述对 DR/DA/Transfer Learning 的分类框架可为转笔项目的 sim-to-real 方案选型提供系统性参考
2. **Gap 分析思维**: 将 sim-to-real gap 分解为力学/视觉/触觉/执行器多个维度，逐一定位和解决，而非笼统地“加域随机化”
3. **补充参考**: 本综述侧重 locomotion，灯巧操作特定的 sim-to-real 应参考 [[A Survey of Sim-to-Real Methods in RL|AwesomeSim2Real]] 综述中的 MDP 四元素框架
