---
tags: [paper, world-model, online-adaptation, WMTS]
aliases: [FOWM]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Finetuning Offline World Models in the Real World.pdf]]"
---
# Finetuning Offline World Models in the Real World
> [!abstract] 核心贡献
> 离线预训练 WM → 真机在线微调。关键：防止灾难性遗忘 + 处理分布偏移。

## 与 WMTS 关联
- **启发 WMTS Actuator Model 在线适应**：WMTS 的 WM 在仿真预训练后需要真机微调
- 灾难性遗忘防护策略（EWC/replay buffer）可用于 WMTS WM 微调时保留仿真知识
- 分布偏移处理：真机数据与仿真数据的域差异
