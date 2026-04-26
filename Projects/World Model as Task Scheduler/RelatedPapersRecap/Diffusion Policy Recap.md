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

## 颗粒度补强：Action Chunking 作为隐式 MPC

### 数学框架

训练时对专家动作块 $A_0=[a_t,\ldots,a_{t+K-1}]$ 加噪：

$$
A_k=\sqrt{\bar{\alpha}_k}A_0+\sqrt{1-\bar{\alpha}_k}\epsilon,
$$

并学习条件去噪：

$$
\mathcal{L}_{DSM}=\mathbb{E}_{A_0,o,k,\epsilon}\|\epsilon-\epsilon_\theta(A_k,k,o)\|_2^2.
$$

推理阶段的 receding horizon 只执行 chunk 前几步，然后重新观测再采样，因此它不是 open-loop 行为克隆，而是“生成式短 horizon MPC”。

### 精简代码逻辑

```python
action = torch.randn(batch, horizon, act_dim)
for k in reversed(range(num_steps)):
	eps_cond = net(action, k, obs_cond)
	eps_uncond = net(action, k, empty_cond)
	eps = (1 + guidance_w) * eps_cond - guidance_w * eps_uncond
	action = ddpm_step(action, eps, k)
execute(action[:, :exec_horizon])
```

### 工程避坑

- `log_prob` 不像高斯 PPO 那样直接可得；若要 RL 微调，需采用 DPPO/DiWA 这类把每个 denoising step 视为 action 的重参数化。
- chunk 太长会增加推理延迟并放大模型误差；chunk 太短则失去时间一致性。WMTS 可采用 `predict_horizon > action_horizon > exec_horizon`。
- CFG 权重过大时会牺牲动作流形先验，表现为高频关节抖动；真机应由 WM Safety Checker 限制 CFG。

### WMTS 迁移

WMTS 的 Generalist 应保留 Diffusion Policy 的多模态优势，但训练条件不应只含 $O_{real}$ 与任务目标，还应加入 actuator feasibility token：

$$
c_t=[z_{prop},z_{tactile},z_{task},z_{act-feasible}],\quad z_{act-feasible}=f_{act}^{enc}(a_{t-H:t},\phi_{t-H:t},T_t).
$$
