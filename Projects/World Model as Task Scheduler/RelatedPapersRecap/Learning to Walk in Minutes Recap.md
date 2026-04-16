---
tags: [paper, sim-to-real, locomotion, WMTS]
aliases: [Semi-structured Dynamics]
paper-year: 2024
related: ["[[Dynamics]]", "[[ReinforcementLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Learning to Walk in Minutes Using Massively Parallel Deep Reinforcement Learning（Semi-structured Dynamics）.pdf]]"
---
# Learning to Walk in Minutes Using Massively Parallel Deep RL
> [!abstract] 核心贡献
> 大规模 GPU 并行仿真（Isaac Gym）+ Semi-structured Dynamics：将已知结构（刚体动力学）与神经网络残差模型结合，实验实现分钟级四足训练。

## 与 WMTS 关联
- **Semi-structured Dynamics** 直接启发 WMTS 的 Physics-Informed Rigid Dynamic Model（§四 4.B）：$f_{\text{physics}}(s,a) + f_{\text{residual}}(s,a)$
- 大规模并行仿真是 WMTS 高效 Oracle 训练的基础设施
- 物理先验嵌入减少数据需求——在灵巧操作中更关键（接触动力学比自由空间更难学）
