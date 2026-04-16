---
tags: [paper, imitation-learning, DAgger, WMTS]
aliases: [HG-DAgger]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[HG-DAgger- Interactive Decision Making.pdf]]"
---
# HG-DAgger: Interactive Decision Making
> [!abstract] 核心贡献
> DAgger 框架改进：Human-Gated 交互式纠正——让专家只在策略犯错时提供纠正演示，高效蒸馏。

## 与 WMTS 关联
- **启发 Oracle→Generalist 蒸馏策略**：Oracle 只在 Generalist 偏差大时提供纠正数据
- 减少蒸馏数据量的策略可用于 WMTS 异步蒸馏资源分配
- Interactive correction 范式可扩展到 WMTS Generalist 真机部署后的 WM 纠正
