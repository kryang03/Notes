---
tags: [insight, WMTS, real-robot-rl, latent-task, discrete]
aliases: [Discrete Task Tokens, DTT-WMTS]
created: 2026-04-27
status: draft
feasibility: B
novelty: A
target-venue: NeurIPS / RSS
related:
  - "[[Final_WMTS]]"
  - "[[STORM Recap]]"
  - "[[CMA-ES Tutorial Recap]]"
  - "[[Latent Space Survey Recap]]"
  - "[[FLD Recap]]"
---

# Idea-009: VQ-Discrete Task Tokens for Real-Robot Re-Plan Safety

> [!abstract] 核心贡献（一句话）
> 我们将 [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|CVAE 连续隐空间]] 替换为 **VQ-VAE 离散 token 字典**，每个 token 是一个"动力学验证过的可行任务原语"，真机 replan 在 token 级而非连续 latent 上进行——大幅降低组合爆炸的安全风险。

---

## 1. 问题定义与动机

### 1.1 大背景引入
连续 latent space 的优势是平滑插值，但缺陷是**任意一点都可能映射到不可执行任务**。真机 replan 时连续 latent 漂移可能瞬间跨入硬件不可行区域。

### 1.2 现有方法的局限
- [[CMA-ES Tutorial Recap]]：CMA-ES 在连续空间演化，每个候选都需要长 rollout 验证。
- [[STORM Recap]]：用 discrete tokens 但只用于 dynamics 表达，未用于任务调度。

### 1.3 我们的洞见
> [!tip] Key Insight
> 把任务空间预先离散为 **K=512 个 token**，每个 token 在 sim 阶段已被验证 actuator+contact feasibility。Real-robot replan 只在 token 之间切换，每次切换的 risk 都是查表已知。这比连续 latent 安全得多，且语义可解释（"摇头 token"、"翻转 token"）。

### 1.4 贡献声明
1. 我们用 VQ-VAE + reliability constraint 训练 **Feasible Task Codebook**。
2. 我们提出 **Token Transition Graph**：节点 = token，边 = sim 验证过的安全切换序列。
3. 我们证明 token-level replan 在真机上的 emergency stop 率低于连续 latent replan ≥3x。

---

## 2. 方法论

### 2.1 问题形式化
VQ-VAE 训练目标：

$$
\mathcal{L}_{VQ} = \|x - D(q(E(x)))\|^2 + \|\mathrm{sg}[E(x)] - e_q\|^2 + \lambda_{feas} \mathcal{L}_{feasibility}(e_q),
$$

其中 $\mathcal{L}_{feasibility}$ 来自 [[WMTS_Reliability_Extensions#1.1 三类风险量|reliability score]]，惩罚 codebook 中的不可执行 token。

Token Transition Graph: 边 $e_{ij}$ 标注 transition cost = $\Delta U_{dyn} + \Delta U_{act} + \Delta C_{contact}$。

### 2.2 核心算法
```
Sim Phase:
  1. Train VQ-VAE on Oracle-solvable tasks with feasibility loss
  2. For each token e_k: compute representative trajectory + feasibility certificate
  3. Build transition graph: edge weight = avg cost over sim rollout

Real Robot:
  1. Encode current task to nearest token e_k*
  2. Replan = graph search (Dijkstra on transition cost) over allowed tokens
  3. Diffusion Generalist conditioned on token e_k* (one-hot or learned embedding)
```

### 2.3 理论分析
离散化是 [[Optimization|combinatorial optimization]] vs continuous 的经典 trade-off。$K$ 大时近似连续；小时损失精度但获 safety。Feasibility-constrained codebook 学习是 information bottleneck 的可行性约束实例。

### 2.4 实现细节
- 新增 `algos/task_generator/vq_codebook.py`。
- 新增 `algos/task_generator/transition_graph.py`：维护 K×K 转移代价矩阵 + Dijkstra search。
- 修改 `diffusion_policy.py` 条件输入支持 token embedding（取代 continuous z_task）。

---

## 3. 实验计划

### 3.1 Stage 0：codebook 大小与覆盖率
| 实验 ID | 自变量 | 因变量 | Grid | 预期 |
|---------|--------|--------|------|------|
| E0.1 | $K$ | 任务覆盖率 vs feasibility ratio | $\in \{64, 128, 256, 512, 1024\}$ | 256 拐点 |
| E0.2 | $\lambda_{feas}$ | unsafe token 比例 | $\in \{0, 0.5, 2, 10\}$ | 2.0 |
| E0.3 | replan strategy | success vs safety | {greedy, dijkstra, A*} | dijkstra |

### 3.2 Stage 1：仿真对比
连续 CMA-ES vs 离散 token replan，比较任务多样性 / safety / success。

### 3.3 Stage 2：真机 replan 频率压力测试
高频任务切换（每 5 秒切换），记录 emergency stop 次数。

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|-----|------|------|------|
| K 不够导致任务覆盖差 | 中 | 中 | 自适应增长 codebook + online dictionary update |
| Token boundary 处行为抖动 | 中 | 中 | 短 transition phase + Diffusion smoothing |
| VQ-VAE codebook collapse | 高 | 中 | EMA + commitment loss + restart dead codes |

---

## 5. 知识库关联

- [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|§一]] — 替换 CVAE
- [[STORM Recap]] — discrete tokenization 经验
- [[WMTS_Reliability_Extensions#1.1 三类风险量|Reliability §1.1]] — feasibility 项
- [[CMA-ES Tutorial Recap]] — 连续 CMA-ES 仍可用于 token 字典内的微调

---

## 6. 动态迭代日志

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | E0.1 | *待运行* | *待定* |
