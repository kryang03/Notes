---
tags:
  - paper
  - manipulation
  - sim-to-real
  - domain-randomization
  - bimanual
  - benchmark
aliases:
  - RoboTwin 2.0
paper-year: 2025
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/RoboTwin 2.0- A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Dynamics]]"
---

# RoboTwin 2.0: A Scalable Data Generator and Benchmark with Strong Domain Randomization for Robust Bimanual Robotic Manipulation

> [!abstract] 核心贡献
> 面向双臂操作的可扩展仿真数据生成框架：整合 MLLM 自动代码生成 + simulation-in-the-loop 验证 + 5 轴域随机化（杂物/光照/背景/桌高/语言指令），50 任务 × 5 机器人 × 731 物体。Few-shot（10 real + 1k sim）平均提升 24.4%，zero-shot 仍提升 ~20%。

## 1. 问题设定与动机

仿真合成数据用于双臂操作面临三大不足：
1. **缺乏自动化质量控制**: 无验证环路，生成的轨迹含执行失败
2. **域随机化不足**: 场景过于干净，缺少杂乱/光照变化/模糊指令
3. **忽视跨体现差异**: 不同双臂平台（低 DOF Piper vs 高 DOF Franka）的抓取策略差异未被编码

## 2. 核心方法

### 2.1 Expert Data Generation Pipeline

- **RoboTwin-OD**: 731 物体实例 × 147 类别，含语义+操作标签
- **MLLM Code Gen**: 多模态大语言模型生成任务执行代码 → simulation-in-the-loop 反馈修复
- **质量门控**: 需达到 10 次仿真运行的设定成功率

### 2.2 5 轴 Domain Randomization

| 轴 | 随机化内容 |
|----|----------|
| 场景杂物 | 桌面干扰物体 |
| 光照 | 方向/强度/颜色 |
| 背景 | 纹理/图案 |
| 桌面高度 | 物理高度变化影响感知+规划 |
| 语言指令 | 同义表述多样化 |

### 2.3 Embodiment-Aware Adaptation

- 物体 affordance 标注 → 针对不同机器人生成体现特定的动作候选
- 支持 5 种双臂平台: Franka, UR5, Aloha AgileX, COBOT-Magic, Piper

## 3. 实验结果

**仿真策略鲁棒性 (8 任务, DR 评估)**:

| 方法 | Avg SR |
|------|:------:|
| ACT | 2.0% |
| DP | 0.0% |
| RDT (pretrained) | 18.8% |
| **Pi0 + RoboTwin 2.0 DR** | **29.1%** |
| RDT + RoboTwin 2.0 DR | 24.9% |
| RDT + Clean FT | 22.5% |

- Clean data FT 几乎无改善 → DR 才是泛化关键
- RDT/Pi0 + DR 预训练：相对提升 31.9% / 29.3%

**真实世界 (4 双臂任务, COBOT-Magic)**:
- Few-shot (10 real + 1k DR sim): 平均提升 +24.4%
- Zero-shot (仅 1k DR sim): unseen 背景仍提升 +20.5%
- 视觉复杂场景增益更大 → DR 在困难条件下尤其有效

## 4. 核心洞见 (Insights)

1. **Clean sim data 无用**: VLA 在无 DR 的仿真数据微调后，真实世界提升可忽略 → 域随机化是必要条件而非锦上添花
2. **DR 预训练具有后续迁移性**: 即使下游任务用 clean data 训练，DR 预训练的 backbone 仍保持鲁棒性 → 与 [[ReinforcementLearning#5.1 Domain Randomization 与 Sim-to-Real|DR]] 理论一致
3. **MLLM→仿真代码闭环**: 用大语言模型生成操作代码 + simulation 验证，可扩展性远超人工编程
4. **10 real demo 即足够**: 10 条真实数据 + 1000 合成 → 367% 相对提升，暗示仿真数据的多样性比真实数据量更重要

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning#5.1 Domain Randomization 与 Sim-to-Real|Domain Randomization]] 的联系
- 5 轴 DR 是系统性的 DR 实践 → 桌高随机化尤为独特（物理+感知双重影响）
- 验证了 DR 预训练的"保护"效应 — 下游 clean 训练不会丧失 DR 带来的鲁棒性

### 与 [[EmbodiedAI]] 的联系
- VLA backbone (RDT, Pi0) 的后训练范式验证 → 与 [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]] 平行但采用纯合成数据路线
- 50 任务 × 5 体现 benchmark 是社区基础设施级贡献

### 与 [[Dynamics]] 的联系
- 仿真物理保真度（物体动力学、抓取力学）是 zero-shot 迁移成功的基础

## 6. 局限与未来方向

- 双臂操作聚焦，灵巧手操作未涉及
- 仿真代码生成依赖 skill API → 对 API 库外的新技能不适用
- 5 轴 DR 的贡献消融不足（哪些轴最关键？）
- 仅 4 个真实世界任务验证
