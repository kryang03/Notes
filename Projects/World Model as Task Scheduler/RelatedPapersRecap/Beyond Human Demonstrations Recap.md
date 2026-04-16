---
tags: [paper, diffusion, reinforcement-learning, VLA, WMTS]
aliases: [Diffusion RL for VLA]
paper-year: 2024
related: ["[[StochasticProcess]]", "[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Beyond Human Demonstrations- Diffusion Model-Based RL Fine-Tuning for VLA Robots.pdf]]"
---
# Beyond Human Demonstrations: Diffusion Model-Based RL Fine-Tuning for VLA Robots
> [!abstract] 核心贡献
> 用 RL 微调 Diffusion-based VLA 策略（超越纯 imitation）：DDPO/DRO 等策略梯度方法直接优化 Diffusion 采样。

## 与 WMTS 关联
- **RL 微调 Diffusion 策略**启发 WMTS 的两个方面：
  1. Generalist Diffusion Policy 的在线微调路径
  2. §五 真机闭环中用 WM reward（而非环境 reward）微调 Diffusion
- DDPO 方法可用于 WMTS 在 WM dream 中微调 Generalist
