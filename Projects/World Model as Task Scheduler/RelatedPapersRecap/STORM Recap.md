---
tags: [paper, world-model, transformer, WMTS]
aliases: [STORM]
paper-year: 2023
related: ["[[ReinforcementLearning]]", "[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning.pdf]]"
---

# STORM: Efficient Stochastic Transformer based World Models for RL

> [!abstract] 核心贡献
> 用 Stochastic Transformer 替代 RSSM 中的 RNN，通过离散 token 化状态实现高效随机 WM，在 Atari 上达到 SOTA 且训练速度快 3.3 倍。

## 核心方法

- 状态 token 化：连续观测 → VQ-VAE 离散 token 序列
- Transformer 动力学模型：自回归预测下一状态 token
- 随机性：通过采样 token 实现多模态未来
- Imagination 训练：类 Dreamer 在 token 空间做 rollout

## 与 WMTS 的关联

- **架构参考**：Transformer WM 处理长 horizon 依赖优于 RNN，WMTS 的 Ensemble WM 可考虑 Transformer 主干
- **离散 token** 在接触丰富任务中的适用性需要验证——接触状态转换天然离散，可能与 token 化相性好
- **效率**：WMTS 需要真机在线更新 WM，STORM 的训练效率优势重要
