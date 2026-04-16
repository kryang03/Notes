---
tags: [paper, world-model, lookahead, WMTS]
aliases: [MB-Lookahead]
paper-year: 2023
related: ["[[ReinforcementLearning]]", "[[Optimization]]", "[[Final_WMTS]]"]
paper-pdf: "[[Model-Based Lookahead Reinforcement Learning.pdf]]"
---
# Model-Based Lookahead Reinforcement Learning
> [!abstract] 核心贡献
> 用学到的 WM 做 k-step lookahead 搜索来辅助策略选择，融合 model-based planning 和 model-free RL。

## 与 WMTS 关联
- **WM Lookahead → Safety Check（§五）**：WMTS 用 WM rollout 判断安全阈值就是 lookahead
- 搜索深度 k 与 WM 精度的权衡——compound error 控制方法参考
- 混合 MB/MF 策略类似 WMTS 的 MF PPO + MB WM 架构
