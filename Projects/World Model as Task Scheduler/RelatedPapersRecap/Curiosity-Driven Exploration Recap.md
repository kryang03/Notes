---
tags: [paper, exploration, curiosity, WMTS]
aliases: [Latent Bayesian Surprise]
paper-year: 2021
related: ["[[InformationTheory]]", "[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Curiosity-Driven Exploration via Latent Bayesian Surprise.pdf]]"
---
# Curiosity-Driven Exploration via Latent Bayesian Surprise
> [!abstract] 核心贡献
> 在隐空间中计算贝叶斯惊奇（信息增益），作为内在奖励驱动探索。比 RND/ICM 等方法更理论严格。

## 与 WMTS 关联
- **启发 WMTS Ensemble Disagreement**（§一 $R_I$）：WMTS 用 Ensemble 预测方差近似信息增益
- 贝叶斯惊奇 = 认知不确定性，与 WMTS 区分 epistemic vs aleatoric uncertainty 一致
- 隐空间探索优于原始状态空间——支持 WMTS 在 VAE 隐空间中做任务搜索
