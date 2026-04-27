---
tags: [insight, WMTS, real-robot-rl, replay-buffer, sample-efficiency]
aliases: [Physics-Aware PER, PA-PER]
created: 2026-04-27
status: draft
feasibility: A
novelty: B
target-venue: ICRA / NeurIPS workshop
related:
  - "[[Final_WMTS]]"
  - "[[ReinforcementLearning]]"
  - "[[Prioritized Level Replay Recap]]"
  - "[[Finetuning Offline WM Recap]]"
---

# Idea-008: Physics-Informativeness Replay Prioritization for Real-Robot WM Updates

> [!abstract] 核心贡献（一句话）
> 我们提出 **PA-PER (Physics-Aware Prioritized Experience Replay)**：在 WMTS WM 微调时，用样本对 **(Actuator residual + Rigid log-likelihood + Tactile NLL)** 的总贡献加权，使 1 小时真机数据等效于 4-5 小时随机回放。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机 sample 极其昂贵，而 PER（基于 TD error）针对 RL value function 设计，对 WM 训练并非最优。WMTS 的 WM 是多 head 联合（Actuator + Rigid + Tactile），需要专门的 prioritization 策略。

### 1.2 现有方法的局限
- 经典 PER：用 TD-error，不适用 WM 的 likelihood loss。
- [[Prioritized Level Replay Recap|PLR]]：在 task level prioritize，未到 transition level。
- [[Finetuning Offline WM Recap|FOWM]]：uniform replay。

### 1.3 我们的洞见
> [!tip] Key Insight
> WM 的每个样本对各 head 的"惊讶度"不同。Actuator residual 大 = 该样本暴露执行器非线性；Rigid log-lik 低 = 该样本暴露动力学未知项；Tactile NLL 大 = 接触模式新颖。**联合三项**作为 priority，能让 WM 微调聚焦于真正有信息的样本。

### 1.4 贡献声明
1. 我们提出 **PA-PER priority**: $p_i = (r_{act,i})^\alpha + (r_{rigid,i})^\beta + (r_{tac,i})^\gamma$。
2. 我们证明在固定真机 budget 下，PA-PER 使 WM 校准 ECE 改善 ≥30%。
3. 与 Idea-003 联动：高 priority 样本同时贡献 failure mode 聚类信号。

---

## 2. 方法论

### 2.1 问题形式化
Sample $i$ priority:

$$
p_i \propto \big[(r_{act,i})^\alpha + (r_{rigid,i})^\beta + (r_{tac,i})^\gamma\big] + \epsilon,\quad P(i) = p_i / \sum_j p_j.
$$

Importance weight: $w_i = (1/(N P(i)))^\beta_{IS}$ 用于 unbiased loss correction（同 PER）。

### 2.2 核心算法
```
For each new transition (s, a, s', τ_fb, x_tactile):
  Compute residuals via current WM ensemble:
    r_act = ‖τ_fb - τ̂_link‖
    r_rigid = -log N(s'|μ,Σ)
    r_tac = ‖x_tactile - x̂_tactile‖
  Insert into buffer with priority p_i

For each WM update step:
  Sample batch with prob ∝ p_i
  Update WM with importance-weighted loss
  Recompute p_i for sampled items
```

### 2.3 理论分析
PA-PER 等价于 importance-weighted maximum likelihood with uncertainty-driven proposal distribution。在 [[InformationTheory|information-theoretic]] 上是变分自由能下降的 surrogate。

### 2.4 实现细节
- 修改 `utils/replay_buffer.py` 加入 `PA-PERBuffer`。
- 配置：`configs/world_model/Ensemble.yaml` 新增 `replay: {type: PA-PER, alpha: 1.0, beta: 0.5, gamma: 1.5}`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真消融
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $(\alpha, \beta, \gamma)$ | WM ECE | grid 27 configs | tactile heavy 最佳 |
| E0.2 | replay type | sample efficiency | {uniform, classic PER, PA-PER} | PA-PER 4x |
| E0.3 | $\beta_{IS}$ | bias-variance | $\in [0, 1]$ | linear schedule |

### 3.2 Stage 1：固定 budget 对比
真机 1 小时数据，分别用 uniform / PER / PA-PER 微调 WM，比较 calibration 与 downstream policy success。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 高 priority 样本可能是 outlier/noise | 中 | 中 | 加 cap on max priority；ensemble agreement filter |
| 三项 scale 不一致 | 高 | 低 | per-dim z-score 归一化 |

---

## 5. 知识库关联

- [[Final_WMTS#4. Ensemble World Model|§4]] — 三 head 联合 priority
- [[Prioritized Level Replay Recap]] — task-level vs transition-level
- 与 Idea-003 互补：失败模式 → 课程；PA-PER → 样本优先级

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
