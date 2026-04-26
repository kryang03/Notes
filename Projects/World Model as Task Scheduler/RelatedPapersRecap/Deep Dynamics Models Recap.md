---
tags: [paper, dexterous-manipulation, model-based, WMTS]
aliases: [PDDM]
paper-year: 2019
venue: CoRL
related: ["[[Dynamics]]", "[[Optimization]]", "[[Final_WMTS]]"]
paper-pdf: "[[Deep Dynamics Models for Learning Dexterous Manipulation.pdf]]"
---

# PDDM: Deep Dynamics Models for Learning Dexterous Manipulation

> [!abstract] 核心贡献
> 首次证明深度动力学模型 + 在线 MPC 规划可以高效学习复杂灵巧操作（24-DoF Shadow Hand 转 Baoding 球），仅 4 小时真机数据，无需演示。

## 核心方法

1. **Bootstrap Ensemble 动力学模型**：$E$ 个独立初始化的 MLP，输出 $\hat{s}_{t+1} \sim \mathcal{N}(f_{\theta_i}(s, a), \Sigma)$
2. **在线 MPC + 滤波优化**：MPPI 变体优化器，利用时间相关性的滤波采样（$\beta$-filtering），比 CEM 更高效
3. **Ensemble Disagreement → 奖励调制**：模型间预测方差影响动作选择，自动回避高不确定性区域

## 关键公式

$$\mu_t = \frac{\sum_{k=0}^{N} (e^{\gamma \cdot R_k})(a_t^{(k)})}{\sum_{j=0}^{N} e^{\gamma \cdot (R_j)}}$$

## 关键结果

- Shadow Hand Baoding balls：4 小时真机数据
- Valve rotation、Handwriting、In-hand reorientation
- 比 SAC/PPO 样本效率高 10-100 倍

## 与 WMTS 的关联

- **直接启发 WMTS §四 Ensemble WM 设计**：Ensemble 量化认知不确定性 + MPC 规划
- **PDDM 的 Ensemble Disagreement** 就是 WMTS §一中 $R_I$ (Curiosity) 的实现
- **局限**：PDDM 无隐空间（原始状态空间 MPC），WMTS 需要隐空间做长 horizon dream
- **PDDM 只做 MPC 不学策略**：WMTS 结合了策略学习（Diffusion）和 WM 规划

## 颗粒度补强：PDDM 作为 WMTS 的不确定性原型

### 数学框架

PDDM 学习 ensemble transition：

$$
\hat{p}_{\theta_i}(s_{t+1}\mid s_t,a_t)=\mathcal{N}(f_{\theta_i}(s_t,a_t),\Sigma_i),\quad i=1,\ldots,E.
$$

MPC 采样 action sequence 并用 reward-weighted update 更新均值：

$$
\mu_t=\frac{\sum_k\exp(\gamma R_k)a_t^{(k)}}{\sum_j\exp(\gamma R_j)}.
$$

动作噪声采用 beta filtering：

$$
n_t=\beta u_t+(1-\beta)n_{t-1},\quad u_t\sim\mathcal{N}(0,\Sigma).
$$

### 精简代码逻辑

```python
noise = filtered_gaussian_noise(num_samples, horizon, act_dim, beta)
actions = mean[None] + noise
states = repeat(current_state, num_samples)
for t in range(horizon):
	model = random_choice(ensemble)
	states = model(states, actions[:, t])
	returns += reward_fn(states)
weights = torch.softmax(gamma * returns, dim=0)
mean = (weights[:, None, None] * actions).sum(dim=0)
execute(mean[0])
```

### Ablation 因果链

| 组件 | 去掉后的问题 | 原因 |
|---|---|---|
| Ensemble | 早期训练不稳定 | 单模型在小数据下过拟合且过度自信 |
| Reward-weighted update | 搜索效率下降 | hard elite 丢弃大量排序信息 |
| Beta filtering | 动作高频抖动 | 高维手部动作序列独立采样导致接触力突变 |

### WMTS 迁移

PDDM 不应替代 WMTS Generalist，但应成为两个模块的数学模板：

1. **Latent Task Generator**：用 ensemble disagreement 找能力边界；
2. **Look-ahead Safety Filter**：用 pessimistic rollout 拦截 diffusion action chunk。

主库精读版见 [[Deep Dynamics Models for Learning Dexterous Manipulation]]。
