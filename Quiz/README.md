---
tags:
  - quiz
  - index
  - interview
aliases:
  - Quiz Index
  - 知识库小测索引
created: 2026-05-01
related:
  - "[[taxonomy]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
---

# Quiz Index

> [!abstract] 定位
> 本目录是基于整份灵巧操作知识库生成的严格面试式简答题题库。当前包含 11 个专题，每个专题 100 题，总计 1100 道简答题；每道题后直接附标准答案与评分要点，用于检查是否真正理解了 Foundations、PapersRecap 与 Projects 中的关键理论、方法和研究设计。

## 使用方式

1. 先遮住答案，用 2-5 分钟口头回答。
2. 对照“标准答案”检查是否讲清楚定义、公式、物理直觉、工程约束与研究启发。
3. 对照“评分要点”判断是否只是背名词，还是能把理论迁移到灵巧手转笔、Sim-to-Real 与真机 RL。

## 题库文件

| 文件 | 覆盖范围 | 题量定位 |
|---|---|---|
| [[01_Foundations_Physics_and_Geometry]] | [[Dynamics]], [[ContactMechanics]], [[ComputationalGeometry]] | 100 题：物理建模、接触几何、SDF/GJK/EPA、神经场、执行器-刚体差异 |
| [[02_Foundations_Control_and_Optimization]] | [[ControlTheory]], [[Optimization]] | 100 题：阻抗/导纳、稳定性证书、LQR/iLQR/MPC、CITO、DeePC、安全过滤 |
| [[03_Foundations_RL_Stochastic_Info]] | [[ReinforcementLearning]], [[StochasticProcess]], [[InformationTheory]] | 100 题：PPO/SAC/offline RL、世界模型、不确定性、POMDP、信息增益 |
| [[04_Foundations_Perception_Representation_EmbodiedAI]] | [[SignalProcessing]], [[RepresentationLearning]], [[EmbodiedAI]] | 100 题：触觉信号、表征学习、3D/空间智能、VLA、仿真器生态 |
| [[05_Papers_Sim2Real_and_Dexterous_RL]] | Sim-to-Real 与灵巧手 RL 论文 | 100 题：DR/System ID/Adaptation、课程、演示、执行器 gap、真机实验矩阵 |
| [[06_Papers_Tactile_Visuotactile_and_Contact]] | 触觉、视触觉、接触生成论文 | 100 题：触觉策略、视触融合、contact grounding、FACET/Minimalist/P2GI、触觉消融 |
| [[07_Papers_VLA_WorldModel_and_Diffusion]] | VLA、World Model、Diffusion Policy | 100 题：ACT/diffusion、world guidance、RLT/DexHiL/RECAP、空间智能、后训练 |
| [[08_Papers_Control_Safety_and_RealWorld_RL]] | 控制、安全、真实世界 RL | 100 题：SERL/HIL/RL-100、CBF/RCRL、Lipschitz、阻抗动作、多频控制、安全后训练 |
| [[09_Projects_DNPM]] | [[Dynamic Non-Prehensile Manipulation]] | 100 题：DNPM 任务物理、PAI/DOC/HDC、Isaac Gym action 链、奖励与实验诊断 |
| [[10_Projects_WMTS]] | [[Final_WMTS]] 与 WMTS ideas | 100 题：任务调度、扩散 Generalist、执行器-刚体解耦、TAR/WPTE/Reset-Free、可靠性扩展 |
| [[11_Cross_Domain_Oral_Exam]] | 跨领域综合面试 | 100 题：理论-论文-项目-真机部署的高压综合口试 |

## 评分标准

| 等级 | 判断标准 |
|---|---|
| A | 能给出数学定义、物理直觉、工程实现、局限性，并能迁移到灵巧手真机问题。 |
| B | 能讲清核心定义和主要方法，但迁移分析不够深入。 |
| C | 只记住关键词，不能解释因果机制或工程约束。 |
| D | 概念混淆，公式或物理方向错误。 |
