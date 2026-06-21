---
tags: [insight, WMTS, real-robot-rl, sim-to-real, energy-based]
aliases: [EBM Mode-Mismatch Detector, EBM-MMD]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: ICRA / RSS workshop
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[StochasticProcess]]"
  - "[[InformationTheory]]"
---

# Idea-010: Energy-Based Sim-to-Real Mode Mismatch Detector

> [!abstract] 核心贡献（一句话）
> 我们训练一个 **energy-based model (EBM)** 拟合仿真侧的 (action, tactile, proprio) 联合分布。真机部署时，EBM 能量值激增即标志 sim-to-real mode mismatch，自动触发 Idea-003 失败模式聚类与 Idea-005 主动数据收集。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机部署时，"何时知道自己已经偏离 sim distribution" 是个根本难题。Ensemble disagreement（[[Final_WMTS|WM 已有]]）只对 dynamics 敏感，对静态分布漂移（如新物体表面、磨损）反应迟钝。

### 1.2 现有方法的局限
- Ensemble disagreement：只看 epistemic uncertainty 上的预测分歧。
- OOD detection 依赖 softmax confidence 或 reconstruction error，对结构化 manipulation 数据不准。

### 1.3 我们的洞见
> [!tip] Key Insight
> 用 EBM 显式建模 sim 数据流形的 unnormalized log-density。真机数据点的 EBM energy 是直接的 likelihood proxy，比间接的 ensemble 信号更敏感。配合阈值门控，可作为 trigger 调度其它 reliability 模块。

### 1.4 贡献声明
1. 我们提出 **Sim-Distribution EBM**：用 contrastive divergence 在仿真 buffer 上训练。
2. 我们证明 EBM energy 与真实 sim-to-real gap 的相关性 > 0.8。
3. 我们将 EBM 作为 **WMTS 自治调度器的 trigger**，自动唤醒 Idea-003/005/006。

---

## 2. 方法论

### 2.1 问题形式化
EBM $E_\theta(x)$ where $x = (a, x_{tactile}, \phi, \dot\phi)$。Loss:

$$
\mathcal{L}_{EBM} = \mathbb{E}_{x \sim p_{sim}}[E_\theta(x)] - \mathbb{E}_{x \sim p_\theta}[E_\theta(x)],
$$

后项用 Langevin sampling 近似。

Real-Robot detection: $\mathrm{score}(x_{real}) = E_\theta(x_{real}) - \mathrm{baseline}$，threshold 化触发。

### 2.2 核心算法
```
Sim Train:
  1. Collect 1M (a, tactile, proprio) tuples from sim Oracle/Generalist
  2. Train EBM with CD-K (K=10 Langevin steps)
  3. Calibrate baseline = E[E_θ(x_sim_held_out)]

Real Robot Inference:
  At each control step:
    e_t = E_θ(x_real,t) - baseline
    if e_t > τ_high for K consecutive steps:
      Trigger Idea-003 failure clustering
      Trigger Idea-005 SBSP data collection
      Reduce task speed via Idea-004 risk schedule
```

### 2.3 理论分析
EBM energy 是 unnormalized negative log-likelihood，[[InformationTheory|KL]] 与 cross-entropy 同源。Threshold 是单边 hypothesis test on data manifold drift。

### 2.4 实现细节
- 新增 `algos/ebm_detector.py`：CD 训练 + Langevin sampler。
- 集成到 `algos/safety_filter.py` 作为 dispatcher。

---

## 3. 实验计划

### 3.1 Stage 0：合成 sim-to-real gap 灵敏度
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | gap 类型 | EBM energy ROC AUC | {friction, mass, geometry, latency} | AUC > 0.85 |
| E0.2 | EBM 架构 | detection latency | {MLP, CNN, Transformer} | CNN |
| E0.3 | threshold 校准 | FP/FN trade-off | percentile {95, 99, 99.5} | 99 |

### 3.2 Stage 1：仿真闭环触发
注入 gap → EBM 触发 → Idea-003/005 响应。指标：触发延迟、误触发率、修复后 success rate 提升。

### 3.3 Stage 2：真机长时间漂移检测
真机 2 小时连续运行（温度爬升），看 EBM 是否成功捕捉漂移并触发冷却。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| EBM 训练不稳定 | 高 | 中 | 用 short-run MCMC + noise injection |
| Langevin sampling 慢 | 中 | 中 | inference 用 single forward pass，不用 sampling |
| False positive 频繁触发 | 中 | 高 | 多步 confirmation + cooldown timer |

---

## 5. 知识库关联

- [[StochasticProcess]] — Langevin dynamics 理论
- [[InformationTheory]] — EBM 与 free energy
- [[WMTS_Reliability_Extensions#2.5 Safety Filter：下置信界放行|Reliability §2.5]] — EBM score 可加入 LCB

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
