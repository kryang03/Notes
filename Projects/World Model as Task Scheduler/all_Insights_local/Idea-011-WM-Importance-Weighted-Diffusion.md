---
tags: [insight, WMTS, real-robot-rl, off-policy, diffusion]
aliases: [WM-Importance-Weighted Diffusion, WMID]
created: 2026-04-27
status: draft
feasibility: B
novelty: A
target-venue: NeurIPS / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[Diffusion Policy: Visuomotor Policy]]"
  - "[[DiWA- Diffusion Policy Adaptation with World Models]]"
  - "[[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training]]"
  - "[[Finetuning Offline World Models in the Real World]]"
---

# Idea-011: WM-Importance-Weighted Off-Policy Diffusion RL on Real Robot

> [!abstract] 核心贡献（一句话）
> 我们打通 **AWAC**（[[Final_WMTS#5.4 通才微调策略|§5.4 选项 A]]）与 **DiWA**（[[Final_WMTS#5.4 通才微调策略|§5.4 选项 B]]），用 WM rollout 估计 off-policy importance ratio，让历史真机数据也能在新策略下贡献无偏 gradient。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机数据每条都极昂贵，浪费历史数据是不可接受的。但 [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]] 没有显式 likelihood，标准 IS weight 不可用。WMTS 当前在 AWAC 与 Dream RL 之间二选一，未充分利用两者优势。

### 1.2 现有方法的局限
- AWAC：只用 advantage 加权 BC，bias 可控但 sample efficiency 一般。
- DiWA：纯 dream rollout，对 WM 误差敏感（"WM 漏洞"）。
- Diffusion 本身：no log-likelihood gradient → 标准 importance sampling 不可用。

### 1.3 我们的洞见
> [!tip] Key Insight
> 用 WM 给 off-policy 数据估计 **action-conditional likelihood ratio** 的 surrogate：

$$
\hat{w}(s, a) = \exp\big(\beta(\hat{V}^{\pi_{new}}(s, a) - \hat{V}^{\pi_{old}}(s, a))\big),
$$

其中 $\hat V$ 由 WM-rolled cumulative reward 计算。这是 [DICE-family] off-policy estimator 的 diffusion-policy 适配。

### 1.4 贡献声明
1. 我们提出 **WMID Loss**：

   $$\mathcal{L}_{WMID} = \mathbb{E}_{(s,a) \sim D_{old}}[\hat{w}(s,a) \cdot \|\epsilon - \epsilon_\theta(\mathbf{A}_k, k, s)\|^2].$$

2. 我们证明 WMID 在固定真机 budget 下 sample efficiency 高于 AWAC ≥40%，安全性高于 DiWA。
3. 我们提出 **混合 horizon 策略**：短 horizon 用 WMID（数据驱动），长 horizon 用 DiWA（模型驱动）。

---

## 2. 方法论

### 2.1 问题形式化
Off-policy buffer $D_{old}$ 来自旧策略 / 旧 oracle / 旧 generalist 。WM 给出 $\hat{V}^\pi(s,a) = \mathbb{E}[\sum_t r_t | s, a, \pi]$ 通过 K-step rollout。Importance weight $\hat w$ 用 advantage 估计代替 likelihood ratio（与 AWAC 同理）。

### 2.2 核心算法
```
For real session:
  1. Replay buffer D = D_real ∪ D_sim (mixed)
  2. Sample (s, a, x_tactile, ...) ~ D
  3. Compute ŵ(s, a) using WM K-step rollout under π_new
  4. Apply WMID loss with ŵ as IS weight
  5. Periodically update WM with new transitions (PA-PER from Idea-008)
```

### 2.3 理论分析
当 $\hat V$ 准确时，WMID 等价于 advantage-weighted regression（无偏）；当 $\hat V$ 误差大时，clip 后近似 BC（保守 bias）。混合 horizon 在 model-based vs model-free 之间做凸组合。

### 2.4 实现细节
- 新增 `algos/wmid_diffusion.py`。
- 复用 Idea-008 PA-PER buffer。
- 配置：`configs/algo/Diffusion_Generalist.yaml` 增加 `wmid: {beta: 1.0, horizon: 5, clip: 10}`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真消融
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $\beta$ | bias-variance | $\in \{0.5, 1, 2, 5\}$ | 1.0 |
| E0.2 | horizon $K$ | sample efficiency | $\in \{1, 3, 5, 10\}$ | 5 |
| E0.3 | clip | stability | $\in \{None, 5, 10, 50\}$ | 10 |

### 3.2 Stage 1：固定 budget 对比
真机 1 小时，比较 WMID / AWAC / DiWA / mix。指标：success rate, gradient stability。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| WM 误差导致 IS 估计 bias 大 | 高 | 高 | clip + ensemble disagreement weighted |
| Off-policy gradient 不稳定 | 中 | 中 | 学习率小 + warmup |

---

## 5. 知识库关联

- [[Final_WMTS#5.4 通才微调策略|§5.4]] — 直接统一两个方案
- 与 Idea-004 互补：Idea-004 是 inference-time, WMID 是 training-time
- 与 Idea-008 互补：PA-PER 控制 sample 优先级，WMID 控制 sample 权重

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
