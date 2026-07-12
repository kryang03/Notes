---
tags:
  - index
  - meta
aliases:
  - 知识库首页
  - Home
created: 2026-01-31
---
# 🤖 灵巧操作知识图谱

# Dexterous Manipulation Knowledge Graph

> **研究方向**: 动态非抓取灵巧操作 (Dynamic Non-Prehensile Manipulation)
> **维护者**: 北京大学研究生
> **AI 助手**: Claude Opus 4.5

---

## 📚 知识结构概览

```
                    ┌─────────────────────────────────────┐
                    │         灵巧操作 (Dexterous         │
                    │           Manipulation)             │
                    └──────────────┬──────────────────────┘
                                   │
        ┌──────────────────────────┼──────────────────────────┐
        │                          │                          │
        ▼                          ▼                          ▼
┌───────────────┐         ┌───────────────┐         ┌───────────────┐
│   物理建模     │         │   决策与控制   │         │   感知与学习   │
│  (Physics)    │         │  (Control)    │         │  (Learning)   │
└───────┬───────┘         └───────┬───────┘         └───────┬───────┘
        │                         │                         │
   ┌────┴────┐               ┌────┴────┐               ┌────┴────┐
   │         │               │         │               │         │
   ▼         ▼               ▼         ▼               ▼         ▼
Dynamics  Contact        Control   Optimization      RL    Representation
          Mechanics      Theory                            Learning
```

---

## 🧠 Foundations — 核心理论

| 领域 | 文件 | 核心关注 |
|-----|------|---------|
| 🔧 [[Dynamics\|动力学]] | `Foundations/Dynamics.md` | 刚体/多体/接触动力学，ABA/RNEA 算法 |
| 🤝 [[ContactMechanics\|接触力学]] | `Foundations/ContactMechanics.md` | 点接触/软指/摩擦锥/LCP |
| 📐 [[ComputationalGeometry\|计算几何]] | `Foundations/ComputationalGeometry.md` | SDF/碰撞检测/神经隐式表示 |
| 🎮 [[ControlTheory\|控制理论]] | `Foundations/ControlTheory.md` | 阻抗控制/操作空间/MPC |
| ⚡ [[Actuation\|执行器与驱动]] | `Foundations/Actuation.md` | 电机/FOC/传动/减速器/执行器 Sim-to-Real |
| 📈 [[Optimization\|优化理论]] | `Foundations/Optimization.md` | iLQR/凸优化/可微优化层 |
| 🎯 [[ReinforcementLearning\|强化学习]] | `Foundations/ReinforcementLearning.md` | PPO/SAC/Sim-to-Real |
| 🌍 [[WorldModels\|世界模型]] | `Foundations/WorldModels.md` | RSSM/Dreamer/PETS/想象试错/Actuator+Rigid 解耦 |
| 🎲 [[StochasticProcess\|随机过程]] | `Foundations/StochasticProcess.md` | GP/扩散策略 |
| 📡 [[SignalProcessing\|信号处理]] | `Foundations/SignalProcessing.md` | EKF/触觉感知 |
| 🔬 [[InformationTheory\|信息论]] | `Foundations/InformationTheory.md` | 互信息/内在动机 |
| 🧬 [[RepresentationLearning\|表征学习]] | `Foundations/RepresentationLearning.md` | 多模态融合/流形 |

**领域分类索引**: [[taxonomy|Foundations/taxonomy.md]]

---

## 🚀 Projects — 研究项目

### [[Dynamic Non-Prehensile Manipulation|动态非抓取灵巧操作]]

基于惯性因果链的任务分类与仿真实现研究。核心观点：DNPM 系统通过 **主动发力 → 高惯性状态 → 惯性力产生 → 对抗重力** 的因果链条完成操作。

---

## 📝 PapersRecap — 论文精读

| 论文 | 关联领域 |
|-----|---------|
| [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] | RL + Control |
| [[Elastic Time Step Reinforcement Learning, VTS-RL]] | RL + Optimization |
| [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] | RL + Control |
| [[Weight-sparse transformers have interpretable circuits]] | Representation |

---

## 📥 MergeBuffer — 待处理

> [!success] 处理完成
> 所有 MergeBuffer 文件已于 2026-01-31 完成分析和融合。
> 详细处理记录参见 [[_MergeIndex|MergeBuffer/_MergeIndex.md]]
> 管理流程参见 [管理指南](.github/skills/knowledge-graph-management/SKILL.md)

| 状态 | 统计 |
|------|------|
| ✅ 已处理 | 10/10 |
| 📂 待处理 | 0 |

**最近一次结构性扩展 (2026-07-12)**:
- 🆕 **新建 [Actuation.md](Foundations/Actuation.md) 执行器与驱动模块**：整合灵巧手 Sim-to-Real 的机电资料（电机/FOC/串级环/传动/减速器/热漂移/actuator net/嵌入式），把项目级机电笔记提升为 Foundation 理论，补上 [[ControlTheory]] 与 [[Dynamics]] 之间"力矩兑现"的缺失一环
- 来源：MergeBuffer `book-control`（控制教材，补强 ControlTheory）+ `机械+电气`（电机/传动/减速器工程培训）+ 项目笔记 [[电机]]/[[传动]]/[[减速器]]/[[sim2real]]/[[FOC_Control]]/[[Actuator2RigidDynamicsModel_gap]]

**理论导师模式增强 (2026-01-31)**:
- [StochasticProcess.md](Foundations/StochasticProcess.md): 添加 SCP 严格数学定义
- [InformationTheory.md](Foundations/InformationTheory.md): 添加 Empowerment 变分下界推导
- [ComputationalGeometry.md](Foundations/ComputationalGeometry.md): 添加 Support Mapping 凸共轭理论
- [ControlTheory.md](Foundations/ControlTheory.md): 添加阻抗控制 Passivity 稳定性证明

---

## 📖 Books — 参考书籍

- A Mathematical Introduction to Robotic Manipulation (Murray)
- Deep Reinforcement Learning
- Optimization in Theory and Practice
- Theory of Deep Learning
- Data-based Linear Systems and Control Theory

---

## 🤖 AI 管理指南

本知识库由 Claude Opus 4.5 协助管理，管理规范详见：

📋 [.github/skills/knowledge-graph-management/SKILL.md](.github/skills/knowledge-graph-management/SKILL.md)

---

