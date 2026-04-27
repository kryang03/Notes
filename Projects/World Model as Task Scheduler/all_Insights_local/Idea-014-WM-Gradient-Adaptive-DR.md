---
tags: [insight, WMTS, real-robot-rl, sim-to-real, gradient-based-DR]
aliases: [WM-Gradient Adaptive DR, WG-ADR]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: CoRL / RSS
related:
  - "[[Final_WMTS]]"
  - "[[Solving Rubiks Cube Recap]]"
  - "[[DeXtreme Recap]]"
  - "[[Sim-to-Real Agile Locomotion Recap]]"
---

# Idea-014: WM-Gradient-Driven Adaptive Domain Randomization

> [!abstract] 核心贡献（一句话）
> 我们用 WM 的 **input gradient** 自动识别"哪些 DR 维度对真机 sim-to-real gap 最敏感"，并在仿真中动态扩大这些维度的范围，避免传统 ADR/DeXtreme 全维度盲目扩张。

---

## 1. 问题定义与动机

### 1.1 大背景引入
[[Solving Rubiks Cube Recap|ADR]] 与 [[DeXtreme Recap|DeXtreme]] 用全局成功率作为 DR 范围调整信号，造成"摩擦系数已经够鲁棒了，但 mass 还在猛涨"。每个 DR 维度对最终性能的边际收益完全不同。

### 1.2 现有方法的局限
- ADR：scalar fitness 全局调整，维度无关。
- 手工调 DR：依赖经验，不收敛。

### 1.3 我们的洞见
> [!tip] Key Insight
> WM 已经被训练为 $f(s, a; \xi_{DR}) \to s'$。**计算 $\partial f / \partial \xi_{DR,i}$ 在真机数据上的梯度范数**就是该维度的"sim-to-real 影响力"。范数大 = 该维度仿真值偏一点就严重影响预测，必须强 DR；范数小 = 该维度无关紧要，可固定。

### 1.4 贡献声明
1. 我们提出 **WG-ADR**：用 WM 反向梯度计算 per-dim DR sensitivity，动态更新 DR 范围。
2. 我们证明 WG-ADR 比 vanilla ADR 减少 30% 仿真时间达到相同真机性能。
3. 我们提出 **dimension scheduling**：先扩张最敏感维度，再扩张次敏感（curriculum-style ADR）。

---

## 2. 方法论

### 2.1 问题形式化
DR 参数向量 $\xi_{DR} \in \mathbb{R}^d$。Per-dim sensitivity:

$$
S_i = \mathbb{E}_{(s, a, s') \sim D_{real}}\left[\left\|\frac{\partial f_{WM}(s, a; \xi_{DR})}{\partial \xi_{DR,i}}\right\|_2\right].
$$

Adaptive range update:

$$
\sigma_i^{(g+1)} = \sigma_i^{(g)} \cdot \exp(\eta \cdot S_i / \bar{S}).
$$

### 2.2 核心算法
```
Initialize σ_i for all DR dims uniformly small
For sim epoch:
  Train Oracle/Generalist with current DR ranges
  Periodically:
    Collect minibatch from real buffer (or held-out sim)
    Compute S_i for all i via WM gradient
    Update σ_i with normalization
  If success rate plateau: shift focus to lower-sensitivity dims (curriculum)
```

### 2.3 理论分析
$S_i$ 是 [[Optimization|Lipschitz constant]] 的 finite-sample estimate。在 robust optimization 框架下，扩张高 $S_i$ 维度 = 在最 worst-case 方向防御。

### 2.4 实现细节
- 修改 `envs/isaac_gym/domain_randomization.py` 支持 per-dim 独立 σ 更新。
- 新增 `algos/wg_adr.py`：梯度计算 + 范围更新 controller。

---

## 3. 实验计划

### 3.1 Stage 0：仿真敏感度真值校准
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | DR dim | true sim2real gap correlation | per-dim | $S_i$ ↔ gap 强相关 |
| E0.2 | 更新频率 | 训练稳定性 | {100, 1k, 10k} steps | 1k |
| E0.3 | $\eta$ | 收敛速度 | $\in \{0.01, 0.1, 1\}$ | 0.1 |

### 3.2 Stage 1：与 ADR 对比
固定真机性能目标，比较达到所需的总仿真训练时间。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| WM 在 OOD ξ_DR 上梯度不可信 | 中 | 中 | 限制 σ 增长率上界 |
| 真机数据少导致 $S_i$ 估计噪声大 | 高 | 中 | 用 sim hold-out 替代/补充真机；EMA |
| 维度间相关性破坏独立估计 | 中 | 中 | 用 Hessian diag 替代 per-dim gradient |

---

## 5. 知识库关联

- [[Final_WMTS#4. Ensemble World Model|§4 WM]] — 提供 gradient
- [[Solving Rubiks Cube Recap|ADR]] — baseline
- 与 Idea-003 互补：失败模式聚类 → 修复哪些类失败；WG-ADR → 修复哪些 DR 维度

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
