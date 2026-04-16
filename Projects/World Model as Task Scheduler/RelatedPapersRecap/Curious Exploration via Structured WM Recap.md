---
tags: [paper, exploration, world-model, WMTS]
aliases: [Plan2Explore]
paper-year: 2020
related: ["[[ReinforcementLearning]]", "[[InformationTheory]]", "[[Final_WMTS]]"]
paper-pdf: "[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation.pdf]]"
---
# Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation
> [!abstract] 核心贡献
> 用 WM Ensemble Disagreement 作为内在奖励进行无任务探索，学到的 WM 可 zero-shot 迁移到下游操作任务。

## 与 WMTS 关联
- **WM 探索 + zero-shot 迁移**与 WMTS 的"先用 Curiosity 探索 → WM 泛化到新任务"路径一致
- 结构化 WM（object-centric）参考——WMTS 可考虑物体级别的预测
- Ensemble Disagreement 作为探索信号在操作任务中的有效性验证
