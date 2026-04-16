---
tags: [paper, dexterous-manipulation, MoE, WMTS]
aliases: [DexReMoE]
paper-year: 2025
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts.pdf]]"
---
# DexReMoE: In-hand Reorientation via Mixture-of-Experts
> [!abstract] 核心贡献
> MoE 框架：多专家策略各负责不同复杂形状，Router 根据物体几何自适应分配权重，150 个物体平均连续成功 19.5 次，worst-case 从 0.69 提升至 6.05。

## 与 WMTS 关联
- MoE 的 Router 机制可替代 WMTS 中简单的 Oracle 分配策略
- Extrinsics embedding（低维形状+物理编码）类比 WMTS 的 PointNet + Inertia 参数
- 空中朝下（最难场景）的成功表明纯 RL 已能处理重力反向，为 WMTS 手腕姿态泛化提供参考
