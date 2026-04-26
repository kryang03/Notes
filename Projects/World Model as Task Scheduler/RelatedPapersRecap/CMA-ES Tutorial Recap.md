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

## 颗粒度补强：为什么 CMA-ES 适合任务隐空间

### 数学框架

CMA-ES 在隐空间维护搜索分布：

$$
z_i^{(g)}\sim m^{(g)}+\sigma^{(g)}\mathcal{N}(0,C^{(g)}),\quad i=1,\ldots,\lambda.
$$

排序后取 top-$\mu$ 更新均值：

$$
m^{(g+1)}=\sum_{i=1}^{\mu}w_i z_{i:\lambda}^{(g)}.
$$

协方差由 rank-one evolution path 与 rank-$\mu$ 当代优秀样本共同更新：

$$
C^{(g+1)}=(1-c_1-c_\mu)C^{(g)}+c_1p_cp_c^T+c_\mu\sum_{i=1}^{\mu}w_i y_{i:\lambda}y_{i:\lambda}^T.
$$

### WMTS Fitness 的可靠化

原始舒适区边缘 fitness 可增强为 pessimistic objective：

$$
\mathcal{F}_{robust}(z)=\alpha\,\mathbb{E}[\mathcal{E}_{traj}\mathcal{R}_{succ}]-\lambda_hD_{hull}(z)-\lambda_uU_{WM}(z)-\lambda_jJ_{jerk}(z).
$$

其中 $U_{WM}$ 是 ensemble disagreement，$J_{jerk}$ 惩罚不可执行高频任务。

### 精简代码逻辑

```python
z = mean + sigma * sample_multivariate_normal(cov, population)
tasks = cvae.decode(z, object_cond)
scores = world_model_rollout_score(tasks) - uncertainty_penalty(tasks)
elite = z[scores.argsort(descending=True)[:mu]]
mean = (weights[:, None] * elite).sum(dim=0)
cov = rank_mu_update(cov, elite - mean) + rank_one_path_update(path)
sigma = csa_update(sigma, path_sigma)
```

### WMTS 迁移

CMA-ES 应当只负责**提出课程候选**，不应直接成为最终 scheduler。最终派发需经过 WM Safety Checker：低 hull 距离、高不确定、高 actuator infeasibility 的任务可以进入“探测队列”，但不能直接真机执行。
