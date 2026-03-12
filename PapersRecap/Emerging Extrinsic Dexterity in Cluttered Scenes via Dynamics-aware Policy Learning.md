---
tags:
  - paper
  - non-prehensile
  - extrinsic-dexterity
  - reinforcement-learning
  - dynamics-model
aliases:
  - DAPL
  - Emerging Extrinsic Dexterity
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (Galbot / Peking University / CASIA / BAAI)
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[RepresentationLearning]]"
---

# Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning

> [!abstract] 核心贡献
> 提出 **Dynamics-Aware Policy Learning (DAPL)**，通过学习世界模型预测接触诱导的物体动力学表征，条件化 RL 策略实现杂乱场景中的**外在灵巧性 (Extrinsic Dexterity)** 涌现——推、滑、翻转等非紧握操作无需手工接触启发式。实物成功率 ~50%，超越抓取策略和人类遥操作 25%+。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — Dynamics-conditioned RL + curriculum learning
> - [[ContactMechanics]] — 多物体接触耦合动力学
> - [[Dynamics]] — 刚体接触动力学的世界模型预测
> - [[RepresentationLearning]] — 动力学表征作为策略条件输入
>
> **核心技术**: World Model (Contact-Induced Dynamics Prediction), Dynamics-Conditioned RL, Curriculum Learning

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
杂乱场景中的非紧握操作成功与否不取决于几何形态，而取决于物体接触后如何运动——学习一个预测接触后果的世界模型，用其体征条件化策略。

### 领域定位
- **非紧握操作**: 从单物体推 → 杂乱场景中选择性利用环境接触
- **核心挑战**: 必须**选择性利用**有益接触（如借助邻居物体翻转目标）同时**避免**有害接触（碰倒无关物体）
- **DNPM 直接呼应**: 外在灵巧性正是非紧握操作的核心——DAPL 的方法论可迁移到 DNPM 的动态阶段

### 关键创新
1. **动力学感知表征** — 世界模型显式预测接触后的物体运动，而非仅依赖几何观测
2. **表征解耦** — 动力学学习与任务控制解耦：先训世界模型，再用其表征条件化 RL
3. **Curriculum learning** — 用策略轨迹自动生成课程，从简单场景渐进到密集杂乱

## 2. 对灵巧操作的启发 (Implications)

> [!warning] 与 DNPM 项目的关键连接
> - DAPL 的"先学动力学表征再条件化策略"范式 与 DNPM Idea-005 (Test-Time Contact Adaptation) 的"利用接触信息自适应"高度一致
> - 外在灵巧性 (extrinsic dexterity) 本质上是非紧握操作的一种——物体的运动部分由环境接触驱动而非末端执行器完全控制
> - 杂乱场景中选择性利用接触的策略学习，可为 DNPM 中的 Thumbaround 任务提供启发（利用拇指背侧的被动接触）

## 3. 演进脉络定位 (Evolution Context)

```
CORN/UniCORN (几何表征, 脆弱)
    ↓ 缺少动力学建模
本论文: DAPL (世界模型学习 + 动力学条件化 RL)
    ↓
后续: 可微世界模型 + 端到端优化
```
