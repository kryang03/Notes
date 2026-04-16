---
tags: [paper, sim-to-real, agile-locomotion, WMTS]
aliases: [Agile Locomotion Sim-to-Real]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Dynamics]]", "[[Final_WMTS]]"]
paper-pdf: "[[Sim-to-Real Learning for Agile Locomotion.pdf]]"
---
# Sim-to-Real Learning for Agile Locomotion
> [!abstract] 核心贡献
> 从仿真到真实敏捷运动迁移的系统方法：动作延迟建模 + 电机模型 + DR + 历史编码器，在真机上实现敏捷跳跃。

## 与 WMTS 关联
- **Actuator Network（电机模型）**直接对标 WMTS Actuator Model（§四 4.A）
- 动作延迟建模方法可用于 WMTS 处理 CAN 总线延迟（~15-20ms）
- Teacher-Student 蒸馏（privileged→real obs）= WMTS 的 Oracle→Generalist 蒸馏
