---
tags: [paper, world-model, real-robot, WMTS]
aliases: [DayDreamer]
paper-year: 2022
venue: NeurIPS
related: ["[[ReinforcementLearning]]", "[[EmbodiedAI]]", "[[Final_WMTS]]"]
paper-pdf: "[[DayDreamer- World Models for Physical Robot Learning.pdf]]"
---

# DayDreamer: World Models for Physical Robot Learning

> [!abstract] 核心贡献
> 首个直接在真机上从零学习的 WM 框架。通过 Dreamer-v3 在真机数据上训练 WM，策略在 dream 中优化，仅 1 小时真机数据让 A1 四足学会行走。

## 核心方法

- 直接在真机上收集数据 → 训练/更新 RSSM WM → 在 dream 中训练策略 → 部署真机收集新数据
- 无需仿真器、无需预训练、无需人工演示
- 关键：真机数据的 reward shaping + 安全约束（hardware safety limits）

## 关键结果

| 平台 | 数据量 | 任务 |
|-----|------|------|
| A1 四足 | 1 小时 | 行走 |
| UR5 机械臂 | 2.5 小时 | Pick-and-place |
| XArm | 10 分钟 | 按钮/旋钮 |

## 与 WMTS 的关联

- **启发 WMTS 真机 WM 微调流程（§五）**：DayDreamer 证明了 WM 可以纯真机数据训练有效
- **WMTS 的改进**：WMTS 先在仿真预训练 WM（Rigid Dynamic Model），真机仅微调 Actuator Model——数据效率更高
- **局限**：DayDreamer 面对灵巧手的高维观测（触觉 360 维）和接触丰富任务可能需要更多数据
