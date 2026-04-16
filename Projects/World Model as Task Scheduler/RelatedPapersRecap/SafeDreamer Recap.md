---
tags: [paper, world-model, safety, WMTS]
aliases: [SafeDreamer]
paper-year: 2024
venue: NeurIPS
related: ["[[ReinforcementLearning]]", "[[Optimization]]", "[[Final_WMTS]]"]
paper-pdf: "[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL.pdf]]"
---
# SafeDreamer: Safe Reinforcement Learning with World Model
> [!abstract] 核心贡献
> 在 Dreamer WM imagination 中引入安全约束（Lagrangian），在 dream 中预测安全代价并约束策略优化，实现安全 RL。

## 与 WMTS 关联
- **WMTS Safety Checker（§五）的理论支撑**：WM rollout 预测安全指标 → 超阈值时降级
- Lagrangian 安全约束可用于 WMTS 的 PPO 微调（在 WM dream 中限制物体掉落概率）
- Safety cost = WMTS 的 $\hat{\mathcal{R}}_{succ} < \text{Threshold}$
