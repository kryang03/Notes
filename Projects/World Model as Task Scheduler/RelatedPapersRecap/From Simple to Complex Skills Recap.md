---
tags: [paper, dexterous-manipulation, hierarchical, WMTS]
aliases: [DexHier]
paper-year: 2025
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[From Simple to Complex Skills- The Case of In-Hand Object Reorientation.pdf]]"
---
# From Simple to Complex Skills: The Case of In-Hand Object Reorientation
> [!abstract] 核心贡献
> 层次策略：底层预训练单轴旋转技能，上层 Planner 选择旋转轴 + 输出残差修正。使用本体感受估计物体位姿，泛化到对称/无纹理物体。

## 与 WMTS 关联
- 技能复用范式可用于 WMTS Oracle 训练：先训单轴旋转 Oracle → 层次组合实现任意 reorientation
- 本体感受位姿估计器（无需外部视觉）与 WMTS 对真机最小依赖原则一致
- 残差动作修正机制可用于 WMTS Generalist 对预训练技能的精细调整
