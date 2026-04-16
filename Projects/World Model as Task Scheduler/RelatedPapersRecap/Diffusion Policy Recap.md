---
tags: [paper, diffusion-policy, imitation-learning, WMTS]
aliases: [Diffusion Policy]
paper-year: 2023
venue: RSS
related: ["[[StochasticProcess]]", "[[RepresentationLearning]]", "[[Final_WMTS]]"]
paper-pdf: "[[Diffusion Policy: Visuomotor Policy.pdf]]"
---

# Diffusion Policy: Visuomotor Policy Learning via Action Diffusion

> [!abstract] 核心贡献
> 将 Diffusion 去噪过程作为策略表示，通过 Denoising Score Matching 从专家演示学习动作分布，天然支持多模态动作分布和 Action Chunking。

## 核心方法

- **前向加噪**：$x_t = \sqrt{\bar{\alpha}_t}x_0 + \sqrt{1-\bar{\alpha}_t}\epsilon$
- **反向去噪**（策略输出）：$p_\theta(x_{t-1}|x_t, c) = \mathcal{N}(x_{t-1}; \mu_\theta(x_t, t, c), \Sigma)$
- **条件**：观测序列 $O_{real}$ + 任务编码 $c$
- **Action Chunking**：一次预测完整动作块 $[a_t, \ldots, a_{t+K-1}]$
- **DDPM / DDIM** 采样加速推理

## 关键特性

- 多模态动作分布（vs Gaussian policy 的单峰局限）
- 训练稳定（不需要对抗训练）
- 时间一致性（Action Chunking 避免抖动）

## 与 WMTS 的关联

- **WMTS 通才策略（§三）的核心架构**：WMTS 的 Generalist 直接采用 Diffusion Policy
- **Denoising Score Matching Loss** 直接用于 Oracle → Generalist 蒸馏
- **CFG (Classifier-Free Guidance)**：WMTS 在 §三中详细推导了 CFG 的物理含义（流形引力 + 任务拉力）
- **局限**：原始 Diffusion Policy 是纯 BC，无法自我改进；WMTS 通过 DiWA/PPO/AWAC 微调解决
