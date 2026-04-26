---
tags: [paper, world-model, latent-imagination, WMTS]
aliases: [Dreamer, Dreamer-v1]
paper-year: 2020
venue: ICLR
related: ["[[ReinforcementLearning]]", "[[StochasticProcess]]", "[[Final_WMTS]]"]
paper-pdf: "[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION.pdf]]"
---

# Dreamer: Dream to Control via Latent Imagination

> [!abstract] 核心贡献
> 首次在隐空间中完全通过想象（imagination）训练策略的 actor-critic 方法，无需在真实环境中做策略梯度。WM 学习紧凑的隐表征并预测奖励，策略完全在 dream 中优化。

## 核心方法

RSSM (Recurrent State-Space Model) 架构：
- **Representation model**: $p(s_t | s_{t-1}, a_{t-1}, o_t)$ — 从观测编码隐状态
- **Transition model**: $q(s_t | s_{t-1}, a_{t-1})$ — 纯隐空间前向预测
- **Observation model**: $p(o_t | s_t)$ — 解码观测（重建损失）
- **Reward model**: $p(r_t | s_t)$ — 预测奖励

**Imagination 训练**：Actor 和 Critic 完全在 Transition model 的 rollout 上优化，使用 $\lambda$-return。

## 关键结果

- 20 个 DeepMind Control Suite 任务中 16 个 SOTA
- 比 D4PG (model-free) 样本效率高数个量级
- Dream rollout 可做到 50 步以上而不严重偏离

## 与 WMTS 的关联

- **WMTS WM 隐空间 rollout 的理论基础**：Dreamer 的 RSSM 和 imagination training 直接启发了 WMTS §四的 Ensemble WM 设计
- **WMTS 的改进**(相比 Dreamer)：
  - Dreamer 用单 WM；WMTS 用 Ensemble 量化认知不确定性
  - Dreamer 不区分 Actuator/Rigid Dynamics；WMTS 显式解耦
  - Dreamer 隐空间连续；WMTS 需要处理接触不连续性

## 颗粒度补强：RSSM、λ-return 与接触任务的误差累积

### 数学框架

RSSM 将隐状态拆成 deterministic recurrent state $h_t$ 与 stochastic state $z_t$：

$$
h_t=f(h_{t-1},z_{t-1},a_{t-1}),\quad z_t\sim q_\phi(z_t\mid h_t,o_t).
$$

先验转移为：

$$
\hat{z}_t\sim p_\theta(z_t\mid h_t),
$$

训练目标包含观测重建、奖励预测与 KL：

$$
\mathcal{L}_{WM}=\sum_t-\log p(o_t\mid h_t,z_t)-\log p(r_t\mid h_t,z_t)+\beta D_{KL}(q_\phi(z_t\mid h_t,o_t)\|p_\theta(z_t\mid h_t)).
$$

Actor 在 imagination 中最大化 $\lambda$-return：

$$
V_t^\lambda=r_t+\gamma[(1-\lambda)v_\psi(s_{t+1})+\lambda V_{t+1}^\lambda].
$$

### 精简代码逻辑

```python
post = rssm.observe(obs, actions)          # q(z_t | h_t, o_t)
prior = rssm.imagine_prior(actions)        # p(z_t | h_t)
wm_loss = recon_loss(obs, post) + reward_loss(reward, post) + kl(post, prior)

imag_state = rssm.start(post.detach())
imag_traj = rssm.imagine(actor, imag_state, horizon=50)
lambda_return = compute_lambda_return(reward_head(imag_traj), value_head(imag_traj))
actor_loss = -lambda_return.mean()
```

### 接触任务局限

Dreamer 的单 WM 在连续控制任务中很强，但接触操作有三类额外风险：

| 风险 | 表现 | WMTS 对策 |
|---|---|---|
| 接触模式跳变 | latent rollout 平滑化 impact | Actuator/Rigid/Contact feature 分解预测 |
| 单模型过度自信 | actor exploit dream | ensemble pessimism + SafeDreamer Lagrangian |
| 长 horizon compound error | 成功预测虚高 | 短 horizon receding dream + 真机数据在线校准 |

### WMTS 迁移

WMTS 可以采用 RSSM 作为高层 latent memory，但低层 $\phi,\dot{\phi},z_{tactile}$ 预测应保持显式，避免所有物理量被压进不可解释 latent 中。
