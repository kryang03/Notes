---
tags: [paper, CMA-ES, optimization, WMTS]
aliases: [CMA-ES]
paper-year: 2016
related: ["[[Optimization]]", "[[Final_WMTS]]"]
paper-pdf: "[[The CMA Evolution Strategy: A Tutorial.pdf]]"
---

# The CMA Evolution Strategy: A Tutorial

> [!abstract] 核心贡献
> CMA-ES 的权威教程。维护多维正态分布 $\mathcal{N}(m, \sigma^2 C)$，通过 Rank-$\mu$ 更新（种群内部方差）+ Rank-1 累积（代际进化路径）+ CSA 步长控制，实现高效黑盒优化。

## 核心机制

1. **采样**：$x_k \sim m + \sigma \mathcal{N}(0, C)$
2. **选择 + 均值更新**：截断选择 top-$\mu$，加权重组
3. **协方差适应**：
   - Rank-$\mu$：利用当代优秀变异步长 $C_\mu = \sum w_i \delta_i \delta_i^T$
   - Rank-1 + Cumulation：进化路径 $p_c$ 的外积 $p_c p_c^T$
4. **CSA 步长控制**：比较 $\|p_\sigma\|$ 与随机游走期望长度

## 与 WMTS 的关联

- **WMTS §一隐空间任务生成器的核心算法**：CMA-ES 在 VAE 隐空间中搜索"通才能力盲区"的任务
- **Fitness Function**：WMTS 定义为 $\mathcal{F}(\xi_{new}) = \alpha \cdot (\mathcal{E}_{traj} \cdot \mathcal{R}_{succ}) - \lambda_{hull} \mathcal{D}_{latent}(\xi_{new}, \text{Hull}(\mathcal{D}_{known}))$
- **优势**：不需梯度（适合 WM rollout 评估的黑盒 fitness）、自适应搜索分布、能沿可行流形边缘滑动
