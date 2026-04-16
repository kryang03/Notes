---
tags: [paper, world-model, WMTS]
aliases: [RWM, Robotic World Model]
paper-year: 2024
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Robotic World Model: A Neural Network Simulator.pdf]]"
---
# Robotic World Model (RWM): A Neural Network Simulator
> [!abstract] 核心贡献
> 自回归 WM + 历史上下文窗口长 horizon 预测。输入 $M$ 步历史 + 误差自校正（自己的预测作为下一步输入），在 POMDP 环境下实现稳健 rollout。

## 与 WMTS 关联
- 自回归训练范式可用于 WMTS Rigid Dynamic Model（误差累积控制）
- 历史上下文窗口 $M$ 类比 WMTS Actuator Model 的历史窗口 $H$
- POMDP 处理策略与 WMTS 对灵巧手部分可观测性的处理一致
