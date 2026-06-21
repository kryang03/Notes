---
tags: [insight, WMTS, real-robot-rl, in-context-learning, online-adaptation]
aliases: [In-Context Hypernet Adapter, ICHA]
created: 2026-04-27
status: draft
feasibility: B
novelty: A
target-venue: NeurIPS / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY]]"
  - "[[Finetuning Offline World Models in the Real World]]"
  - "[[ANYmal parkour Learning agile navigation for quadrupedal robots]]"
  - "[[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models]]"
---

# Idea-006: In-Context Hypernet Adapter for Per-Episode Real-Robot Adaptation

> [!abstract] 核心贡献（一句话）
> 我们引入一个 **frozen** WMTS 主体 + 一个轻量 **Hypernet**，让 Hypernet 以最近 50 步触觉/proprio/温度历史为 prompt，输出 Actuator FiLM 参数和 Diffusion guidance scale，实现**每条 episode 内的零梯度适应**。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机灵巧手在每个 episode 间状态会显著变化：(a) 温度爬升导致 $K_t$ 漂移，(b) 物体表面打磨/磨损，(c) 累积疲劳改变弹性。Idea-002 用 5 分钟数据微调 FiLM，但仍是离线 step。理想情况是每条 episode 自动校准。

### 1.2 现有方法的局限
- [[ANYmal parkour Learning agile navigation for quadrupedal robots|Actuator Network]]：参数固定。
- [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|Semi-structured Dynamics]]：3 分钟微调，但每次新环境都要重训。
- [[Finetuning Offline World Models in the Real World|FOWM]]：在线但仍需梯度更新。

### 1.3 我们的洞见
> [!tip] Key Insight
> [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|ICL]] 已证明 Transformer 不需要参数更新就能"在 prompt 内"做 regression。把灵巧手 episode 起始 50 步当 prompt，Hypernet 输出 Actuator FiLM offset $\Delta\gamma, \Delta\beta$ 和 Diffusion guidance scale $\Delta\eta_{risk}$，整个 WMTS 主体冻结。这是 **真机零梯度在线适应** 的最优雅形式。

### 1.4 贡献声明
1. 我们提出 **ICHA** — Transformer-based hypernet 输入触觉/proprio/温度 prompt，输出多个模块的 lightweight adapter 参数。
2. 我们用 meta-learning 在仿真训练 ICHA，模拟 1000+ 不同的硬件状态。
3. 我们证明真机部署时，ICHA 可使每条新 episode 的前 100 步表现显著优于 frozen baseline，且**不需要任何真机梯度更新**。

---

## 2. 方法论

### 2.1 问题形式化
Prompt: $P = \{(\phi, \dot{\phi}, x_{tactile}, T)_{t=-50:0}\}$。Hypernet $h_\omega$:

$$
(\Delta\gamma, \Delta\beta, \Delta\eta_{risk}) = h_\omega(P).
$$

Actuator Network: $f_{act}(x; \gamma_0+\Delta\gamma, \beta_0+\Delta\beta)$。Diffusion guidance: $\eta_{risk}^{base}+\Delta\eta_{risk}$。

### 2.2 核心算法
```
Meta-Train (sim, 1000+ DR configs):
  For each task:
    Sample DR config ξ (motor params, friction, mass, temperature offset)
    Generate 50-step prompt P with current ξ
    Generate 100-step task rollout
    Compute task loss L_task
    Update h_ω via ∇_ω L_task (treating frozen WMTS as fixed)

Meta-Test (real robot, no gradient):
  Episode k:
    Collect first 50 steps with default policy
    Compute (Δγ, Δβ, Δη_risk) = h_ω(P)
    Inject into Actuator Net + Diffusion inference
    Continue episode with adapted modules
```

### 2.3 理论分析
ICHA 是一个 **conditional implicit-MAML** 的极限情况：把内层梯度更新替换为 forward-pass。在 [[Optimization|optimization landscape]] 视角下，meta-train 学到的是 prompt → 参数的映射 manifold，假设此 manifold 足够低维（DR 参数 < 50 维）。

### 2.4 实现细节
- 新增 `algos/icha/hypernet.py`：Transformer encoder 处理 50-step prompt → MLP 输出 adapter params。
- 新增 `algos/icha/adapter_inject.py`：包装 frozen Actuator Net 和 Diffusion 注入 ICHA 输出。
- meta-train：`scripts/meta_train_icha.py`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真消融
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | prompt 长度 | adapt accuracy | {10, 30, 50, 100} | 50 拐点 |
| E0.2 | hypernet 容量 | overfit/underfit | {Tiny/Base/Large} | Base |
| E0.3 | 注入位置 | task improvement | {Actuator only, Diff only, both} | both |

### 3.2 Stage 1：仿真 hold-out DR test
DR 配置训练 80% / 测试 20%，比较 (a) frozen, (b) full FT, (c) ICHA。指标：unseen DR 上的 success rate。

### 3.3 Stage 2：真机 5 物体 × 10 episodes
真机 30 分钟，零梯度部署 ICHA，记录每条 episode 的成功曲线、温度漂移、Actuator 残差。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 真机分布在 meta-train DR 之外 | 中 | 高 | meta-train DR 范围 ≥3σ 真机；fallback 到 frozen |
| Hypernet 输出 adapter 不稳定 | 中 | 中 | output regularization (L2 on Δ) |
| Prompt 50 步本身就含失败行为 | 中 | 中 | prompt-conditioning aware：给 hypernet 看 success tag |

---

## 5. 知识库关联

- [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|§4.A]] — 注入点之一
- [[Final_WMTS#3.3 Classifier-Free Guidance (CFG)|§3.3]] — 注入点之二
- [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY]] — Transformer ICL 理论支撑
- 与 Idea-002 互补：Idea-002 用真机数据离线微调 FiLM，ICHA 用 meta-trained 网络实现零梯度在线版

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
