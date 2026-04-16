---
tags: [paper, dexterous-manipulation, multi-task, WMTS]
aliases: [Geometry-Dex]
paper-year: 2021
related: ["[[ReinforcementLearning]]", "[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning.pdf]]"
---
# Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning
> [!abstract] 核心贡献
> 单一多任务策略 + PointNet 物体表征 → 100+ 物体 in-hand reorientation 泛化，多任务训练甚至超越单物体专才。

## 核心发现
- 多任务 + 合适表征 → **通才超越专才**（surprising result）
- PointNet 编码物体几何 → 策略自动学习形状-控制对应关系
- 训练物体数量线性增长 → 泛化性能线性提升

## 与 WMTS 关联
- **PointNet 物体表征**直接用于 WMTS 的 $\mathbf{o}^{\text{shape}} = \text{PointNet}(\mathcal{P})$（§零）
- "通才超越专才"为 WMTS 的 Generalist Diffusion Policy 设计提供信心
- 多任务训练的 scaling law 支持 WMTS 的隐空间任务生成策略
