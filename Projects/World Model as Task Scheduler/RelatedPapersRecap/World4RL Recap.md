---
tags: [paper, world-model, diffusion, WMTS]
aliases: [World4RL]
paper-year: 2024
related: ["[[StochasticProcess]]", "[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation.pdf]]"
---
# World4RL: Diffusion World Models for Policy Refinement with RL
> [!abstract] 核心贡献
> 用 Diffusion 模型作为 WM（生成式动力学模型）来预测下一状态，结合 RL 精炼操作策略。

## 与 WMTS 关联
- WM 架构参考：Diffusion 作为动力学预测器（vs WMTS 的 Ensemble MLP / RSSM）
- Diffusion WM 天然支持多模态转移（接触/非接触），可能比单高斯 Ensemble 更适合灵巧操作
- 但 Diffusion WM 推理慢（多步去噪）→ WMTS 需要高频 Safety Check，需权衡
