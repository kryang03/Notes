---
tags: [paper, representation-learning, locomotion, WMTS]
aliases: [FLD]
paper-year: 2024
related: ["[[RepresentationLearning]]", "[[SignalProcessing]]", "[[Final_WMTS]]"]
paper-pdf: "[[FLD- Fourier Latent Dynamics for Structured Motion Representation and Learning.pdf]]"
---
# FLD: Fourier Latent Dynamics for Structured Motion Representation and Learning
> [!abstract] 核心贡献
> 用 Fourier 基函数参数化隐空间动力学，将运动轨迹编码为结构化频域表征。实现平滑、可解释的运动生成。

## 与 WMTS 关联
- **频域隐空间编码**启发 WMTS 的 WM 表征设计：灵巧手周期性运动（如转笔）天然适合 Fourier 分解
- 结构化隐空间（vs 自由 VAE 隐空间）可能提高 WMTS WM 的预测稳定性
- 可用于 WMTS 任务表征（§零 Task Encoder）的频域先验
