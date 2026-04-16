---
tags: [paper, dexterous-manipulation, sim-to-real, world-model, WMTS]
aliases: [DexSim2Real2]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[DexSim2Real2- Building Explicit World Model for Precise Articulated Object Dexterous Manipulation.pdf]]"
---
# DexSim2Real2: Building Explicit World Model for Precise Articulated Object Dexterous Manipulation
> [!abstract] 核心贡献
> 为铰接物体构建显式 WM（旋量表示 + 铰链运动学），用 WM 预测 → 规划实现精确灵巧操作 Sim-to-Real。

## 与 WMTS 关联
- **显式物理 WM** 类比 WMTS Rigid Dynamic Model：嵌入运动学先验减少数据需求
- 旋量表示 $se(3)$ 与 WMTS 的 6D 旋转任务空间（§零 $\mathbf{q} \in \mathbb{R}^6$）可互补
- 铰接物体处理为 WMTS 扩展到非刚体任务提供参考
