---
tags: [insight, WMTS, real-robot-rl, exploration, active-learning]
aliases: [Saturation Boundary Active Learning, SBAL]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: ICRA / CoRL
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[FOC_Control]]"
  - "[[Curiosity-Driven Exploration Recap]]"
  - "[[Curious Exploration via Structured WM Recap]]"
---

# Idea-005: Active Real-Robot Data Collection at Actuator Saturation Boundary

> [!abstract] 核心贡献（一句话）
> 我们设计 **Saturation-Boundary Sampling Policy (SBSP)**：让真机数据收集策略主动驱动系统至 [[FOC_Control#5.1 反电动势电压天花板与弱磁区域|actuator feasibility 边界]]（$\rho_{act} \approx \eta_{act}$），最大化每次真机交互对 Actuator Network 的信息增益。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机数据稀缺。现有 Sim-to-Real 工作（[[ANYmal Parkour Recap]]、[[Learning Agile and Dynamic Motor Skills for Legged Robots]]）真机数据收集策略基本是 (a) 随机摆动或 (b) 用最终任务策略。前者数据无关，后者数据冗余（多在 actuator 线性区）。

### 1.2 现有方法的局限
- [[Curiosity-Driven Exploration Recap|Latent Bayesian Surprise]]：只在状态空间做 curiosity，不知 actuator 物理边界。
- [[ANYmal Parkour Recap|Actuator Network]]：原始训练数据是 quasi-static 摆动，高动态区域 OOD 严重。

### 1.3 我们的洞见
> [!tip] Key Insight
> Actuator Model 在 $\rho_{act} \approx 1$（线性区）信息饱和，在 $\rho_{act} \to 0$（饱和区）才暴露非线性。**最有信息量的样本恰好在这个边界**，但常规策略不会主动去那里——既危险又没有奖励指引。我们设计专门的 **boundary-seeking exploration policy**，仅用于数据收集，不参与最终任务。

### 1.4 贡献声明
1. 我们提出 **SBSP** — 一个轻量 policy（<1M params），目标是最大化 $-|\rho_{act} - \eta_{boundary}|$，同时受 safety constraint 约束。
2. 我们证明 SBSP 收集的 60 分钟数据使 Actuator MSE 降低相当于 4 小时随机数据。
3. 我们将 SBSP 与 [[WMTS_Reliability_Extensions#2.1 Latent Task Generator：双队列而非单队列|Probe Queue]] 融合：Probe Queue 决定**任务**，SBSP 决定**任务内的探索路径**。

---

## 2. 方法论

### 2.1 问题形式化
设当前 Actuator Network 估计 $\rho_{act,t} = \|\hat{\tau}_{link,t}\|/\|\tau_{cmd,t}\|$。SBSP 优化目标：

$$
\max_{\pi_{SBSP}} \mathbb{E}_{\tau \sim \pi_{SBSP}}\Big[\sum_t I_{gain}(s_t, a_t) - \lambda |\rho_{act,t} - \eta_b| - \mu \mathbb{1}[\text{unsafe}]\Big],
$$

其中 $I_{gain}$ 是 Actuator Network 的 ensemble disagreement (epistemic uncertainty)。

### 2.2 核心算法
```
Algorithm: SBSP Data Collection
───────────────────────────────
Initialize: π_SBSP (small MLP), Actuator Net f_act ensemble
For data session (real, ≤30 min):
  1. Sample task z_task ~ Probe Queue (low-risk slow tasks)
  2. Rollout π_SBSP, but project actions through Safety Filter
  3. For each step:
       compute ρ_act, I_gain via f_act ensemble
       reward = I_gain - λ|ρ_act - η_b|
  4. Append (a, φ, φ̇, τ_fb, T) to replay buffer
  5. Update f_act via supervised learning on buffer
  6. Update π_SBSP via PPO with above reward
End
Use accumulated buffer for downstream Actuator Network finetuning.
```

### 2.3 理论分析
SBSP 的 reward 是 [Bayesian Active Learning by Disagreement (BALD)] 的 actuator-physics 实例化。$\eta_b$ 选择略低于 1（如 0.7-0.8），平衡 information value 和 safety。

### 2.4 实现细节
- 新增 `algos/sbsp.py`：实现 SBSP policy（PPO-tiny）和 reward 计算。
- 修改 `scripts/deploy_real.py`：增加 `--mode data_collection` 入口。
- 配置：`configs/algo/SBSP.yaml` — `eta_b: 0.75, lambda: 1.0, hidden: 64`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真验证 information gain
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $\eta_b$ | Actuator MSE 下降率 | $\in \{0.3, 0.5, 0.7, 0.9\}$ | 0.7 最佳 |
| E0.2 | data 收集策略 | sample efficiency | {random, task policy, SBSP} | SBSP 4x |
| E0.3 | safety constraint 力度 | unsafe ratio | {soft, hard, mixed} | hard + soft warmup |

### 3.2 Stage 1：仿真闭环 + 端到端 RL
比较：训练 Generalist 时分别用 (a) random 30min, (b) task-policy 30min, (c) SBSP 30min 收集的数据更新 Actuator → 对比 Generalist 真机迁移性能。

### 3.3 Stage 2：真机 30 分钟收集
真机执行 SBSP 30 分钟，测量 Actuator Net 适应曲线、与 random baseline 对比。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| SBSP 主动撞 saturation 导致硬件磨损 | 中 | 高 | 严格 temperature 上限 + 速度 envelope；每 5min 强制冷却 |
| $I_{gain}$ 在初期估计不准 | 高 | 中 | warmup 用 random rollout 200 步 |
| SBSP 学到 trivial actuator-bias 操作 | 低 | 中 | Probe Queue 控制任务多样性 |

---

## 5. 知识库关联

- [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|§4.A]] — Actuator Network 数据需求来源
- [[WMTS_Reliability_Extensions#2.1 Latent Task Generator：双队列而非单队列|Probe Queue]] — 任务级 vs 路径级 active learning 互补
- [[FOC_Control#5.1 反电动势电压天花板与弱磁区域|FOC §5.1]] — saturation 物理来源

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
