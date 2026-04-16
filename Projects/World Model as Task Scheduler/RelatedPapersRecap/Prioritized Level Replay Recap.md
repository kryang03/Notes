---
tags: [paper, curriculum, WMTS]
aliases: [PLR, Prioritized Level Replay]
paper-year: 2021
venue: ICML
related: ["[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Prioritized Level Replay.pdf]]"
---
# Prioritized Level Replay
> [!abstract] 核心贡献
> 基于 TD-error 或 regret 的环境优先级回放，自动选择最有学习价值的训练关卡。

## 与 WMTS 关联
- **任务生成优先级**启发 WMTS 的 CMA-ES Fitness Function 设计：优先生成策略"刚好掉落"的任务
- PLR 的 regret-based scoring 可替代 WMTS 当前的 $\mathcal{E}_{traj} \cdot \mathcal{R}_{succ}$ fitness
- 计算效率高（不需要 rollout），可用于 WMTS 任务缓冲区的重放优先级
