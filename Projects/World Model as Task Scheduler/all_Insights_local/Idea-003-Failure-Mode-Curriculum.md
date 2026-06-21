---
tags: [insight, WMTS, real-robot-rl, world-model, sim-to-real]
aliases: [Failure-Mode Curriculum, FMC]
created: 2026-04-27
status: draft
feasibility: A
novelty: A
target-venue: CoRL / RSS
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[Curiosity-Driven Exploration via Latent Bayesian Surprise]]"
  - "[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation]]"
  - "[[Prioritized Level Replay]]"
  - "[[The CMA Evolution Strategy: A Tutorial]]"
---

# Idea-003: Real-Robot Failure-Mode Clustering for Closed-Loop Sim Curriculum

> [!abstract] 核心贡献（一句话）
> 我们让真机失败的"诊断"成为 Latent Task Generator 的输入：将每次真机 drop/掉落事件按 **WM 各 head 残差谱**聚类，每个簇驱动一类针对性的仿真课程，形成 **真机 → 失败模式 → 仿真课程 → 真机** 的闭环。

---

## 1. 问题定义与动机

### 1.1 大背景引入
真机 RL 的根本困境：**真机失败数据极其昂贵**，每次掉落代价高（物理损伤 + 重置开销 + 手动复位时间），但失败本身蕴含的 sim-to-real gap 信息却最丰富。WMTS 当前的 [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|CMA-ES task generator]] 仅在仿真中演化，对真机失败模式无感。

### 1.2 现有方法的局限
- [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|ADR]]：失败时整体放大 DR 范围，无法定位具体 sim-to-real gap 维度。
- [[Prioritized Level Replay|PLR]]：在 sim level 上做优先级，未考虑真机反馈。
- [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|Plan2Explore]]：只在 WM 内做好奇心驱动，未连接真机失败诊断。

### 1.3 我们的洞见
> [!tip] Key Insight
> 真机失败时的 WM 残差有结构：(a) Actuator head 残差大 → 执行器可行性 gap；(b) Rigid head 残差大但 Actuator 准 → 接触/摩擦 gap；(c) Tactile head 残差大 → 几何/姿态估计 gap。这三类 gap 对应**不同的仿真补救策略**（DR 范围调整 / 接触模型升级 / 触觉噪声模型）。聚类残差 → 直接路由到课程。

### 1.4 贡献声明
1. 我们提出 **WM-Residual Failure Taxonomy**：用 (Actuator MSE, Rigid log-likelihood, Tactile NLL) 三维谱聚类（GMM）。
2. 我们提出 **Cluster-Conditioned Curriculum**：每簇映射到一种仿真增强策略（DR 范围、Stribeck 摩擦强度、触觉噪声）。
3. 我们证明该闭环每 1 小时真机数据可减少 ≥25% 的同类失败重现率（vs. 仅扩大 ADR 基线）。

---

## 2. 方法论

### 2.1 问题形式化
真机失败事件 $e = (\tau_{0:H}, t_{fail})$，提取残差谱：

$$
\mathbf{r}(e) = \big[\underbrace{\frac{1}{H}\sum_t \|\tau_{fb,t} - \hat{\tau}_{link,t}\|_2}_{r_{act}},\; \underbrace{-\frac{1}{H}\sum_t \log \mathcal{N}(s_{t+1}|\mu_m,\Sigma_m)}_{r_{rigid}},\; \underbrace{\frac{1}{H}\sum_t \|x_{tactile,t+1} - \hat{x}_{tactile,t+1}\|_2}_{r_{tac}}\big].
$$

GMM 聚类 $\mathbf{r}(e) \in \mathbb{R}^3$ 得 $K$ 簇 $\{C_k\}$，每簇有 prototype $\mathbf{r}_k^*$ 和分配的仿真增强 $A_k$。

### 2.2 核心算法
```
Algorithm: Failure-Mode-Driven Curriculum
─────────────────────────────────────────
Initialize: GMM with K=3 clusters, sim curricula A_1=actuator-DR, A_2=contact-DR, A_3=tactile-noise

For real_session in 1..N:
  1. Real rollout, collect failure events {e_i}
  2. Compute r(e_i), update GMM (online EM)
  3. For each cluster C_k:
       - count failure rate q_k = |{e_i ∈ C_k}| / total
       - if q_k > threshold: amplify A_k in next sim batch
  4. Sim training (Oracle + WM update) with adapted curriculum
  5. Distill to Generalist
  6. Deploy back to real
```

### 2.3 理论分析
GMM 在残差空间是**MAP-style 故障归因**。每簇的仿真增强可视为对 sim distribution 的 importance reweighting，其权重正比于真机失败概率。在 distributional robustness 框架下，这是 min-max policy optimization 的近似（minimize worst-case failure probability over reweighted sim distribution）。

### 2.4 实现细节
- 新增 `algos/task_generator/failure_taxonomy.py`：维护 online GMM + cluster→curriculum 映射表。
- 修改 `envs/isaac_gym/domain_randomization.py`：暴露 per-axis DR 范围 setter。
- 新增 `algos/task_generator/curriculum_adapter.py`：将 cluster failure rate 映射为 DR 比例。
- 配置：`configs/task/InHandReorient.yaml` 新增 `failure_taxonomy: {K: 3, online_em_step: 0.05}`。

---

## 3. 实验计划

### 3.1 Stage 0：仿真注入合成失败 → 验证聚类可分性
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | 注入 gap 类型 | GMM 聚类 ARI | {act-only, contact-only, tactile-only, mixed} | ARI > 0.7 (3-class) |
| E0.2 | $K$ | BIC | $K \in \{2,3,4,5\}$ | $K=3$ 拐点 |
| E0.3 | Curriculum 强度 | sim 次代失败率 | low/med/high | high 但需配 BC 正则 |

### 3.2 Stage 1：仿真闭环（合成 sim-to-real gap）
人为在 evaluation env 注入未知 gap，比较 (a) 无 curriculum, (b) 全局 ADR, (c) Failure-mode-driven curriculum。指标：失败模式重现率、连续旋转时长。

### 3.3 Stage 2：真机闭环（≤2 小时真机时间）
3 轮迭代，每轮真机 30 分钟收集失败 → sim 4 小时 → 部署。指标：每轮失败率衰减曲线。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| 失败事件少导致 GMM 不稳定 | 高 | 中 | 用 prior strong 的 Bayesian GMM；前 2 轮回退到 uniform curriculum |
| 簇间残差谱重叠 | 中 | 中 | 增加额外维度（温度峰值 / 接触切换频率） |
| Curriculum 过激导致 Oracle 训练崩溃 | 中 | 高 | 增长率 cap + KL 早停 |

---

## 5. 知识库关联

- [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|§一]] — 输入新增 cluster failure rate
- [[WMTS_Reliability_Extensions#2.1 Latent Task Generator：双队列而非单队列|Reliability §2.1]] — Reject Queue 与失败簇可共享 backbone
- [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|Plan2Explore]] — Curiosity 在仿真侧, 本方案补真机侧诊断回路

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
