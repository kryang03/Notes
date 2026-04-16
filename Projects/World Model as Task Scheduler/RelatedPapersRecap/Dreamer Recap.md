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
