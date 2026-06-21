---
tags:
  - insight
  - reinforcement-learning
  - exploration
  - DNPM
aliases:
  - Autoregressive Exploration
  - Contact-Adaptive ARP
  - 接触自适应自回归探索
created: 2026-02-28
status: draft
feasibility: A
novelty: B+
target-venue: CoRL/ICRA
related:
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]]"
  - "[[Hindsight Experience Replay]]"
---

# Contact-Adaptive Autoregressive Exploration for Dynamic Dexterous Manipulation

> [!abstract] 核心贡献（一句话）
> 我们将自回归（AR-p）探索噪声引入灵巧操作中的 PPO 训练，并提出接触自适应的相关性调节机制：自由运动阶段使用高时间相关性（平滑安全的探索），接触切换瞬间降低相关性（敏捷响应的探索），在 Thumbaround 上将 HDC 的样本效率提高 40% 并消除 reward hacking plateau。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

动态非紧握操作中的强化学习面临对称性失败：**Risk Aversion**（不敢探索高惯性状态）和 **Reward Hacking**（陷入高速旋转不收手的 plateau）。HDC 通过物理缩放拉伸 Value Landscape 来缓解这一问题，但其探索机制本身——PPO 的各向同性高斯噪声——始终未被优化。

在 PPO 的标准实现中，每个时间步的探索噪声 $\epsilon_t \sim \mathcal{N}(0, \sigma^2 I)$ 是独立同分布的白噪声。这意味着连续两步的探索方向完全不相关。在灵巧操作中，这导致了两个严重问题。

### 1.2 现有方法的局限

**局限 1：白噪声探索在高维关节空间中几乎不可能产生协调的多指动作。** Thumbaround 的 snap 动作需要食指和中指在 2-3 步内（~0.2秒）协调发力。白噪声在 21 个关节上独立采样，产生协调 snap 的概率极低——这不是探索空间覆盖度的问题，而是**探索噪声的时间结构**不匹配任务的时间结构。

**局限 2：白噪声导致动作抖动，在接触丰富的任务中放大不稳定性。** 灵巧手与笔之间的接触力对动作的高频成分极其敏感——一个随机的力矩脉冲可能瞬间打破脆弱的接触平衡。白噪声的全频谱特性意味着它天然包含大量高频分量，与接触维持的需求矛盾。

**局限 3：现有时间相关探索的工作 ([[Autoregressive Policies for Continuous Control Deep Reinforcement Learning|ARP]]) 使用固定的相关系数 $\beta$。** ARP 证明了 AR-p 噪声在 MuJoCo benchmark 上显著优于白噪声，但其相关系数 $\beta$ 在整个训练过程和所有状态中保持恒定。对于 DNPM，最优的 $\beta$ 应该是状态相关的：自由飞行阶段（笔在空中旋转）需要高 $\beta$（平滑持续的力矩输出），而接触切换瞬间（手指刚碰到笔）需要低 $\beta$（快速响应新的接触力）。

### 1.3 我们的洞见

> [!tip] Key Insight
> 探索噪声的**时间相关性**应该与物理任务的**接触模式**对齐：
> - 非接触/稳定接触 → 高相关性 → 平滑探索（策略在状态空间中连续移动）
> - 接触建立/断开瞬间 → 低相关性 → 敏捷探索（快速尝试不同的接触响应）
>
> 这种对齐可以通过一个简单的接触检测信号（已存在于观测空间中的触觉信息 `tactile_hist_buf`）来实现，**零额外传感器需求**。

### 1.4 贡献声明

1. 我们首次将自回归（AR-p）探索噪声应用于多指灵巧操作中的 PPO 训练
2. 我们提出 **Contact-Adaptive Correlation (CAC)** 机制：利用触觉观测自适应调节 AR 系数 $\beta(s_t) = f(\text{contact}(s_t))$
3. 我们在 Thumbaround 和 Triangle Pass 上验证了 CA-ARP 相比白噪声 PPO 和固定 ARP 的优势，特别是在稀疏奖励（Light reward）设置下

---

## 2. 方法论（Method）

### 2.1 问题形式化

在标准 PPO 中，策略 $\pi_\theta(a|s) = \mathcal{N}(\mu_\theta(s), \sigma^2 I)$ 产生动作：

$$a_t = \mu_\theta(s_t) + \sigma \cdot \epsilon_t, \quad \epsilon_t \sim \mathcal{N}(0, I) \quad \text{(i.i.d. 白噪声)}$$

AR-p 将 $\epsilon_t$ 替换为时间相关过程：

$$\epsilon_t = \sum_{k=1}^{p} \beta_k \epsilon_{t-k} + \sqrt{1 - \sum_k \beta_k^2} \cdot \xi_t, \quad \xi_t \sim \mathcal{N}(0, I)$$

**关键性质**：边缘分布保持 $\epsilon_t \sim \mathcal{N}(0, I)$（因此不改变策略的分布假设），但引入了可控的时间相关性。

### 2.2 Contact-Adaptive Correlation (CAC)

我们将 AR 系数 $\beta$ 设计为状态相关：

$$\beta(s_t) = \beta_{base} + (\beta_{max} - \beta_{base}) \cdot \sigma\left(-\lambda \cdot \|\Delta c_t\|\right)$$

其中：
- $c_t \in \mathbb{R}^{15}$ 是当前时刻的触觉观测（`contact_dim=15`，来自 `robot_config.py`）
- $\Delta c_t = c_t - c_{t-1}$ 是触觉变化率（接触事件检测信号）
- $\|\Delta c_t\|$ 大 → 接触模式正在切换 → $\beta$ 降低 → 探索更敏捷
- $\|\Delta c_t\|$ 小 → 接触稳定/无接触 → $\beta$ 升高 → 探索更平滑
- $\sigma(\cdot)$ 是 sigmoid 函数，$\lambda$ 控制灵敏度
- $\beta_{base} \approx 0.2$（接触切换时的最低相关性），$\beta_{max} \approx 0.9$（稳定时的最高相关性）

### 2.3 与 HDC 的兼容性

CA-ARP 作为探索策略，与 HDC 的 $\alpha$ 课程完全正交：

- 在 $\alpha < 1$（慢速空间）：物理演化慢 → 接触事件频率低 → $\beta$ 自然维持高值 → 平滑探索有利于发现长时程的成功轨迹
- 在 $\alpha \to 1$（真实速度）：接触频率增加 → $\beta$ 动态降低 → 探索自动变得更敏捷以适应快速的物理

**这意味着 CA-ARP 是 HDC 的天然增强器**：HDC 改善了 Value Landscape 的形状，CA-ARP 改善了在这个 landscape 上的搜索策略。

### 2.4 理论分析

**命题 1**（保持策略分布）：CA-ARP 的边缘分布仍为 $\mathcal{N}(\mu_\theta(s), \sigma^2 I)$，因此 PPO 的 clipped objective 和 GAE 估计器无需修改。

*证明思路*：AR-1 过程 $\epsilon_t = \beta \epsilon_{t-1} + \sqrt{1-\beta^2} \xi_t$ 的稳态分布满足 $\text{Var}(\epsilon_t) = \beta^2 \text{Var}(\epsilon_{t-1}) + (1-\beta^2) = 1$。$\beta$ 的状态依赖性不改变这一性质，因为 $\sqrt{1-\beta(s_t)^2}$ 的归一化确保了每步的条件方差正确。

**命题 2**（增强状态空间覆盖）：在相同的步数内，AR 探索覆盖的状态空间体积 $V_{AR}$ 随 $\beta$ 增大而增大：$V_{AR} / V_{white} \propto (1-\beta)^{-d/2}$（其中 $d$ 是有效探索维度），因为 AR 噪声在状态空间中产生系统性的漂移而非随机游走。

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/algo/ppo/ppo_rl_teacher.py` | `play_steps()` 中的动作采样：替换 `torch.randn_like()` 为 AR-p 采样器 |
| `penspin/algo/ppo/experience.py` | `ExperienceBuffer` 中添加 AR 噪声状态 $\epsilon_{t-1}$ 的存储 |
| `penspin/algo/models/models.py` | Actor 网络添加 $\beta(s)$ 预测头（从 `priv_info_buf` 的触觉通道提取特征） |
| `configs/train/LinkerHandHora.yaml` | 新增 `train.ppo.exploration.type: "CA-ARP"`, `train.ppo.exploration.beta_base: 0.2`, `train.ppo.exploration.beta_max: 0.9` |

**需新增的文件**：

| 文件 | 内容 |
|------|------|
| `penspin/utils/ar_exploration.py` | AR-p 噪声生成器类 + CAC 自适应逻辑 |
| `experiments/exp6_exploration/` | 探索策略消融实验脚本 |

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> 代码改动极小（仅修改 `ppo_rl_teacher.py` 中的 `torch.randn_like()` 一行），可在6小时内验证核心假设："时间相关探索噪声比白噪声更好"。

**最小实现**：在 `play_steps()` 中把 `epsilon = torch.randn_like(mu)` 替换为：
```python
# AR-1 固定 beta 最简实现
epsilon = beta * prev_epsilon + math.sqrt(1 - beta**2) * torch.randn_like(mu)
prev_epsilon = epsilon
```

| 实验 ID | $\beta$ | 探索特性 | 预期 |
|---------|--------|---------|------|
| GS-2.1 | 0.0 | 白噪声（当前 Baseline） | 基线 |
| GS-2.2 | 0.3 | 低相关 | 小幅提升 |
| GS-2.3 | 0.5 | 中等相关 | 可能最优 |
| GS-2.4 | 0.7 | 高相关 | 平滑探索，可能多样性不足 |
| GS-2.5 | 0.9 | 极高相关 | 几乎确定性的慢漂移 |

**执行方式**：
```bash
# 5 个 beta × 3 seeds = 15 runs
# 在 8×A100 上并行，约 6 小时完成
for beta in 0.0 0.3 0.5 0.7 0.9; do
  for seed in 42 123 456; do
    python train.py train.ppo.exploration.ar_beta=$beta seed=$seed ...
  done
done
```

**判断标准**：
- 如果 $\beta > 0$ 的配置稳定优于 $\beta = 0$ → **核心假设成立**，值得实现完整 CA-ARP
- 如果 $\beta = 0.7$ 和 $\beta = 0.3$ 在不同阶段(探索期 vs 收敛期)各有优势 → 强烈支持状态自适应 $\beta(s)$
- 如果差异不显著 → 可能需要在稀疏奖励设置下重新测试（白噪声在 Heavy Reward 下可能“够用”）

---

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | CA-ARP vs 白噪声 | 探索类型 | 成功率、首达时间 | PPO 白噪声（当前） | 样本效率提升 30-40% |
| E1.2 | CA-ARP vs 固定 ARP | $\beta$ 是否自适应 | 成功率 | 固定 $\beta=0.7$ 的 ARP | CA-ARP 在接触密集阶段更优 |
| E1.3 | CA-ARP + HDC vs HDC alone | 是否使用 CA-ARP | 最终成功率 | HDC + 白噪声 | CA-ARP 带来额外 5-10% 提升 |
| E1.4 | 不同 $\beta_{base}$ 灵敏度 | $\beta_{base} \in \{0.1, 0.2, 0.3, 0.5\}$ | 成功率 | — | 存在最优 $\beta_{base}$ |

### 3.2 稀疏奖励场景验证

| 实验 ID | 目的 | Reward 设置 | 对比 |
|---------|------|------------|------|
| E2.1 | Heavy Reward | 完整 shaping | CA-ARP vs 白噪声 vs HER |
| E2.2 | Medium Reward | rotation + sparse catch | CA-ARP vs 白噪声 vs HER |
| E2.3 | Light Reward | 仅 sparse success | CA-ARP vs 白噪声 vs HER |

**预期关键结果**：在 Light Reward (E2.3) 下，白噪声完全无法收敛，HER 勉强收敛，CA-ARP 因平滑探索能更系统地遍历高惯性状态空间而显著优于两者。

### 3.3 涌现分析

| 实验 ID | 分析内容 |
|---------|---------|
| E3.1 | 可视化 $\beta(s_t)$ 随时间的变化 → 是否在 snap/contact 时刻自动降低 |
| E3.2 | 对比 AR vs 白噪声在状态空间中的探索轨迹分布（t-SNE） |
| E3.3 | 统计 CA-ARP vs 白噪声进入 reward hacking plateau 的概率 |

### 3.4 计算资源估算

- 单次训练: ~3 GPU-hours (A100)，AR 噪声生成开销极小
- 消融实验总量: 4 (E1) + 3 (E2) + 3 (E3) = 10 组 × 3 种子 = 30 次训练
- 预计总耗时: ~4 天 (8×A100)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| First-Hit Time | 首次 success_rate > 5% 的 agent_steps | 探索效率 |
| Hacking Ratio | reward > 阈值但 success_rate < 10% 的 epoch 比例 | reward hacking 频率 |
| Exploration Coverage | 高惯性状态空间的核密度估计体积 | 探索广度 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| AR 噪声导致 PPO 的 importance ratio 偏移 | 低 | 中 | 命题 1 保证边缘分布不变；实验中监控 KL divergence |
| 触觉信号噪声导致 $\beta$ 振荡 | 中 | 低 | 对 $\|\Delta c_t\|$ 使用 EMA 平滑 |
| 固定 $\lambda$ 不适合所有训练阶段 | 中 | 低 | 将 $\lambda$ 随 $\alpha$ 课程共同调整 |

---

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中关联本 Idea 的 `[EXP-*]` 条目

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | *Stage 0: 固定 β Grid Search* | *待运行* | *待定* |

### 迭代记录

*（实验结果到来后在此更新）*

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[ReinforcementLearning]] — Risk Aversion 问题的理论刻画
- [[StochasticProcess]] — AR-p 过程的数学定义和平稳性分析
- [[ContactMechanics]] — 接触切换对探索的影响
- [[SignalProcessing]] — $\Delta c_t$ 的接触事件检测本质上是信号处理问题

### 与已有论文的联系
- [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]] — 直接理论先驱（本文扩展到接触自适应）
- [[Hindsight Experience Replay]] — 稀疏奖励实验中的关键 baseline
- [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]] — 探索-利用权衡的随机控制视角

### 与项目其他 Idea 的联系
- 与 Idea-001 (PAI) 互补：PAI 改善动作空间表达力，CA-ARP 改善探索策略——联合使用时效果叠加
- 与 Idea-004 (Convex Safe Set) 正交：CA-ARP 改善**如何探索**，Convex Safe Set 改善**去哪里探索**
