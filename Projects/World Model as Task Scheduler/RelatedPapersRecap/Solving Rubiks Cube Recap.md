---
tags: [paper, dexterous-manipulation, ADR, WMTS]
aliases: [OpenAI Rubiks Cube]
paper-year: 2019
venue: OpenAI
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[SOLVING RUBIK'S CUBE WITH A ROBOT HAND.pdf]]"
---
# Solving Rubik's Cube with a Robot Hand
> [!abstract] 核心贡献
> Automatic Domain Randomization (ADR)：自动扩展 DR 参数范围直到策略失败边界，Shadow Hand 解魔方 Sim-to-Real。

## 与 WMTS 关联
- **ADR 自动课程**启发 WMTS 的 CMA-ES 任务生成器——都是自动寻找策略能力边界
- 极限 DR 范围（质量 ×10、摩擦 ×3）为 WMTS DR 参数设计提供参考
- 证明纯 model-free + 极限 DR 可行但代价大（数万 GPU 小时）；WMTS 用 WM 提高效率
