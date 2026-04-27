---
tags: [insight, WMTS, real-robot-rl, diffusion-policy, test-time]
aliases: [WM-Guided Diffusion Refinement, WGDR]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: NeurIPS / RSS
related:
  - "[[Final_WMTS]]"
  - "[[Diffusion Policy Recap]]"
  - "[[DiWA- Diffusion Policy Adaptation with World Models Recap]]"
  - "[[SafeDreamer Recap]]"
  - "[[Beyond Human Demonstrations Recap]]"
---

# Idea-004: WM-Guided Diffusion Refinement at Test-Time (No Retraining)

> [!abstract] 核心贡献（一句话）
> 我们将 WMTS Safety Filter 从**外置二值门**升级为 **diffusion 反向过程内的可微引导项**，在每个去噪步骤中向动作 chunk 注入 WM 风险梯度，实现真机部署时**零参数更新**的策略精化。

---

## 1. 问题定义与动机

### 1.1 大背景引入
[[Final_WMTS#5.1 Look-ahead Safety Filter|当前 Safety Filter]] 是 reject-and-replan 模式：动作生成后做 WM 推演，不通过则丢弃。这种二值放行有两个问题：(1) 拒绝率高时真机执行频率掉到不可用；(2) 完全浪费了已生成的 sample 信息。

### 1.2 现有方法的局限
- [[Diffusion Policy Recap|Diffusion Policy]]：原生没有 reward / safety guidance。
- [[DiWA- Diffusion Policy Adaptation with World Models Recap|DiWA]]：用 WM 在 dream MDP 中 PPO 微调 diffusion，但需要梯度回传与离线训练，无法 on-the-fly 调整。
- [[SafeDreamer Recap|SafeDreamer]]：在 dream 内做约束 RL，未应用到 diffusion 反向过程。

### 1.3 我们的洞见
> [!tip] Key Insight
> Diffusion 反向过程本质是 score-based 引导。WM 给出的"动作 → 风险"是可微的（ensemble disagreement、actuator saturation、temperature constraint 都是 differentiable through reparameterization）。把它们作为额外的 score gradient 加进 CFG 框架，就能在**单次推理内**得到风险感知的动作分布——无需重训。

### 1.4 贡献声明
1. 我们提出 **WM-Guided Score Modification**：

   $$\tilde{\epsilon}_\theta = (1-w)\epsilon_\theta(\emptyset) + w\,\epsilon_\theta(c) - \eta_{risk}\nabla_{x_t} \mathcal{R}_{WM}(x_t),$$

   其中 $\mathcal{R}_{WM}$ 由 WM 推演风险（OOD + actuator + temperature）给出。
2. 我们证明该方案可在不退化原始任务性能的前提下，把真机紧急停止率从 X% 降到 Y%。
3. 我们提出 **Adaptive $\eta_{risk}$ schedule**：早 step 大 guidance（修方向），晚 step 小 guidance（保细节）。

---

## 2. 方法论

### 2.1 问题形式化
风险函数 $\mathcal{R}_{WM}(x_t)$ 由 differentiable rollout 给出：

$$
\mathcal{R}_{WM}(\mathbf{A}_t) = \lambda_1 \mathrm{tr}\,\mathrm{Cov}\big(\{f_{m}(s_0, \mathbf{A}_t)\}_m\big) + \lambda_2 \sum_t \max(0, \|\hat{\tau}_{link,t}\| - \tau_{max}(\dot{\phi}_t,T_t))^2 + \lambda_3 \max(0, \max_t T_{motor,t} - T_{limit})^2.
$$

每个 reverse step:

$$
x_{t-1} = \mu_\theta(x_t, t, c) - \eta_{risk}(t) \cdot \Sigma_t \nabla_{x_t} \mathcal{R}_{WM}(x_t) + \sigma_t z.
$$

### 2.2 核心算法
```
Algorithm: WM-Guided Diffusion Inference
────────────────────────────────────────
Input: trained π_diff, WM ensemble, risk function R_WM
For inference at real robot timestep:
  Sample x_T ~ N(0, I)
  For k = T..1:
    1. ε_cfg = (1-w)·ε_θ(x_k, k, ∅) + w·ε_θ(x_k, k, c)
    2. g_risk = ∇_{x_k} R_WM(x_k)         # via differentiable WM rollout
    3. η = η_max · cos(π·k/T) / 2          # cosine schedule
    4. x_{k-1} = denoise_step(x_k, ε_cfg) - η·Σ_k·g_risk + σ_k·z
  Return executable action chunk x_0
```

### 2.3 理论分析
该修正等价于 Bayes 反推 $\nabla \log p(x_t|c, \mathrm{safe})$，其中 $p(\mathrm{safe}|x_t) \propto \exp(-\mathcal{R}_{WM}(x_t))$。这是 [Score-based Bayesian inference](https://arxiv.org/abs/2305.04391) 的灵巧手机器人安全实例化。Adaptive schedule 来自 noise scale 的几何含义：早期 $x_k$ 离数据流形远，guidance 主导拓扑选择；晚期接近 $x_0$，guidance 仅做局部修正。

### 2.4 实现细节
- 新增 `algos/wm_guided_diffusion.py`：包装现有 `diffusion_policy.py` 的 inference loop。
- WM 接口：`world_model/ensemble.py` 暴露 `differentiable_rollout(s_0, action_chunk)` 返回 mean/var/τ̂。
- 配置：`configs/algo/Diffusion_Generalist.yaml` 新增 `wm_guidance: {eta_max: 0.5, schedule: cosine, lambda: [1, 0.5, 2]}`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真消融
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $\eta_{max}$ | safety vs success | $\in \{0, 0.1, 0.5, 1.0\}$ | 0.5 sweet spot |
| E0.2 | schedule | success rate | {const, linear, cosine, sigmoid} | cosine 最佳 |
| E0.3 | $\lambda$ 权重 | trade-off | grid | actuator term 主导 |

### 3.2 Stage 1：仿真对比
对照：(a) Vanilla diffusion, (b) Reject-and-replan filter, (c) DiWA 微调, (d) Ours。指标：success rate, emergency stop rate, control freq sustained。

### 3.3 Stage 2：真机部署
在 LinkerHand 上跑 4 物体 × 5 任务，比较 emergency stop / 物体破坏次数。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 可微 rollout 计算成本超过控制频率 | 高 | 高 | 用 1-step Jacobian linearization；只对前 1-2 step 完整 rollout |
| Guidance 过强导致 mode collapse | 中 | 中 | adaptive schedule + KL clip |
| WM 在 OOD 时 gradient 错误 | 中 | 高 | 用 ensemble disagreement 作为 gradient confidence weight |

---

## 5. 知识库关联

- [[Final_WMTS#3.3 Classifier-Free Guidance (CFG)|§3.3 CFG]] — 数学框架天然支持额外 score 项
- [[Final_WMTS#5.1 Look-ahead Safety Filter|§5.1]] — 升级为可微版本
- [[WMTS_Reliability_Extensions#2.5 Safety Filter：下置信界放行|Reliability §2.5]] — LCB 可作为 R_WM 的一项

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
