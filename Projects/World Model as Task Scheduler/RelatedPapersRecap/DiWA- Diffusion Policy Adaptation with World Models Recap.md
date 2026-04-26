---
tags: [paper, world-model, diffusion-policy, WMTS]
aliases: [DiWA]
paper-year: 2025
related: ["[[ReinforcementLearning]]", "[[StochasticProcess]]", "[[Final_WMTS]]"]
paper-pdf: "[[DiWA- Diffusion Policy Adaptation with World Models.pdf]]"
---

# DiWA: Diffusion Policy Adaptation with World Models

> [!abstract] 核心贡献
> 首个完全离线框架：冻结预训练 WM，在其隐空间内构造 **Dream Diffusion MDP**，用 PPO (DPPO) 微调预训练 Diffusion Policy，无需任何真实/仿真环境交互。

## 核心方法

1. **World Model 训练**：从无标签 play 数据学习隐空间动力学（RSSM 架构）
2. **Diffusion Policy 预训练**：专家演示上行为克隆，条件为 WM 编码的隐状态
3. **奖励估计**：训练成功分类器（Success Verifier）作为 reward signal
4. **Dream Diffusion MDP**：将 Diffusion 去噪过程嵌入 WM MDP，每个去噪步 $k$ 视为 MDP 中的一步动作，PPO 直接在此 MDP 上优化

## 关键公式

$$\bar{a}^{k-1}_t \sim \pi_\theta(\bar{a}^{k-1}_t | s_t, \bar{a}^k_t), \quad k = K, K-1, \ldots, 1$$

WM 转移在隐空间完成：$\hat{s}_{t+1} \sim p_\phi(\cdot | s_t, a_t)$

## 关键结果

- CALVIN benchmark 上显著优于纯 BC baseline
- Zero-shot 真机部署：完全在 WM dream 中微调的策略可直接部署真机
- 样本效率：不需要额外真机/仿真交互

## 与 WMTS 的关联

- **直接启发 §五选择二**：WMTS 提出的"冻结 WM 作为物理引擎 + PPO 微调 Diffusion"方案与 DiWA 框架高度一致
- **风险启示**：DiWA 同样面临 PPO Exploit WM 漏洞的风险（对抗性动作），WMTS 中已识别此问题
- **Success Verifier** 可类比 WMTS 的 Discrepancy-Aware Success Predictor
- **局限**：DiWA 用的是 manipulation 任务，未考虑 actuator 非线性；WMTS 需要处理更复杂的 Sim-to-Real gap

## 颗粒度补强：Dream Diffusion MDP 与 WMTS 风险边界

### 数学框架

DiWA 将扩散策略的去噪链条重写为一个 dream 内 MDP。给定 WM 隐状态 $s_t$ 和 noisy action chunk $\bar{a}_t^k$：

$$
\bar{a}_t^{k-1}\sim\pi_\theta(\cdot\mid s_t,\bar{a}_t^k,k),\quad k=K,\ldots,1,
$$

最终 clean action $a_t=\bar{a}_t^0$ 被送入冻结 WM：

$$
\hat{s}_{t+1}\sim p_\phi(\cdot\mid s_t,a_t),\quad \hat{r}_t=V_\psi(\hat{s}_{t+1},g).
$$

DPPO 微调目标可写成：

$$
\mathcal{L}=\mathcal{L}_{PPO}^{dream}+\lambda_{BC}\|\epsilon_\theta-\epsilon_{BC}\|_2^2+\lambda_{KL}D_{KL}(\pi_\theta\|\pi_{BC}).
$$

这里 $\lambda_{BC}$ 是防止策略 exploit WM 漏洞的核心安全阀。

### 精简代码逻辑

```python
with torch.no_grad():
	state = world_model.encode(obs)
noisy_action = torch.randn(batch, chunk, act_dim)
log_probs, rewards = [], []
for denoise_step in reversed(range(num_diffusion_steps)):
	dist = diffusion_policy.denoise_dist(noisy_action, state, denoise_step)
	next_action = dist.sample()
	log_probs.append(dist.log_prob(next_action).sum(dim=(-1, -2)))
	noisy_action = next_action

dream_state = world_model.rollout(state, noisy_action)
rewards = success_verifier(dream_state, goal)
loss = clipped_ppo_loss(log_probs, rewards) + bc_reg(diffusion_policy, bc_policy)
```

### Ablation 因果链

| 组件 | 去掉后的风险 | 因果机制 |
|---|---|---|
| Success Verifier | reward 不可用或过稀疏 | 离线 dream 中没有环境终止反馈，需要 learned reward 填补监督 |
| BC/KL regularization | PPO 过快找到 WM 漏洞 | diffusion policy 离开专家动作流形后，冻结 WM 的外推误差被策略放大 |
| 冻结 WM | 联合训练不稳定 | reward、dynamics、policy 同时漂移会破坏 PPO 的 on-policy 假设 |

### WMTS 迁移

WMTS 不能直接把 DiWA 的 single WM dream 作为真机优化环境，必须加入 [[Deep Dynamics Models Recap|PDDM]] 式 ensemble pessimism 与 actuator discrepancy penalty：

$$
r^{WMTS}=\hat{r}_{succ}-\lambda_u\mathrm{tr}\,\mathrm{Cov}(\hat{s}_{t+1}^{1:M})-\lambda_a\|\hat{\tau}_{link}-\tau_{cmd}\|_2.
$$
