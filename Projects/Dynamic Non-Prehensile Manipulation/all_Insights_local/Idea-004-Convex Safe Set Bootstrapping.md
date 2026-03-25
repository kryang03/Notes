---
tags:
  - insight
  - reinforcement-learning
  - optimization
  - exploration
  - DNPM
aliases:
  - Convex Safe Set
  - CSS Bootstrapping
  - 凸安全集 Bootstrapping
created: 2026-02-28
status: draft
feasibility: B
novelty: A
target-venue: RSS/CoRL
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[InformationTheory]]"
  - "[[Hindsight Experience Replay]]"
  - "[[Reachability Constrained Reinforcement Learning]]"
---

# Convex Safe Set Bootstrapping: Geometric Exploration Guidance for High-Inertia State Spaces

> [!abstract] 核心贡献（一句话）
> 我们提出 Convex Safe Set (CSS) Bootstrapping：从少量成功轨迹中在高惯性状态空间构建凸包（safe set），作为探索引导信号——处于凸包内的高惯性状态获得安全 bonus，策略被引导在凸包边界扩展，从而将 HER 的 goal relabeling 思想**从目标空间推广到高惯性状态空间的几何结构**。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

动态非紧握操作的核心困难在于**高惯性状态的不可归因性**：策略在 $t_0$ 时刻将物体送入高惯性状态（高速旋转/飞行），但该状态的好坏可能要在 $t_0 + \Delta t$ 之后才能通过成功/失败来判断。更危险的是，在状态空间维度上，"好的" 和 "坏的" 高惯性状态可能在观测上几乎不可区分——同样的角速度 $\omega = 18$ rad/s，微小的角度差异（笔偏离拇指轴线 2°）就可能决定成功与失败。

### 1.2 现有方法的局限

**局限 1：Dense Reward 无法区分好坏高惯性状态。** 奖励 $r \propto \omega$ 只看角速度大小，不看角速度方向和上下文。两个完全不同含义的状态获得相同 reward。

**局限 2：HER 的几何结构假设太弱。** HER 假设任何到达过的状态都可以作为虚拟目标，但不利用这些状态之间的几何关系——它不知道 "两个成功状态之间的状态也可能是安全的"。

**局限 3：Hamilton-Jacobi 可达性分析 ([[Reachability Constrained Reinforcement Learning|RCRL]]) 在高维灵巧操作中计算不可行。** HJ 值函数需要在完整状态空间上求解 PDE，对于 21-DoF 手 + 6-DoF 物体的 27 维空间，网格方法完全不可行。

### 1.3 我们的洞见

> [!tip] Key Insight
> **成功轨迹通过的高惯性状态在状态空间中构成近似凸集。**
>
> 物理直觉：如果从状态 $s_A$ 出发和从状态 $s_B$ 出发都能成功完成旋转，那么从 $s_A$ 和 $s_B$ 的凸组合 $\lambda s_A + (1-\lambda) s_B$ 出发，物理演化的连续性保证了大概率也能成功——因为动力学方程在局部是近似线性的。
>
> 这个假设远弱于 HJ 可达性分析（不需要求解 PDE），但远强于 HER 的无结构假设（利用了几何近似）。它恰好填补了计算可行性和结构利用之间的空白。

### 1.4 贡献声明

1. 我们提出 **Convex Safe Set (CSS) Bootstrapping**：从成功经验中构建高惯性状态的凸包，作为探索的几何引导
2. 我们设计了三种 CSS 利用机制：（a）安全 bonus reward、（b）初始化分布扩展、（c）探索优先级引导
3. 我们在 Thumbaround 和陀螺旋转（新任务）上验证了 CSS 相比 HER 和纯 Dense Reward 的优势

---

## 2. 方法论（Method）

### 2.1 问题形式化

定义**高惯性状态空间** $\mathcal{H} \subset \mathcal{S}$：所有满足 $\|\dot{q}_{obj}\| > v_{threshold}$ 的状态（物体速度超过阈值，已进入惯性主导区域）。

定义**成功高惯性状态集** $\mathcal{H}^+ = \{h \in \mathcal{H} : \tau(h) \text{ leads to success}\}$，其中 $\tau(h)$ 是从 $h$ 出发的后续轨迹。

**CSS 假设**：$\text{Conv}(\mathcal{H}^+)$（$\mathcal{H}^+$ 的凸包）中的状态也大概率导致成功。

### 2.2 CSS 构建

**状态降维**：$\mathcal{H}$ 的原始维度太高（27+维），直接构建凸包不可行。使用如下降维方案：

$$z = \phi(h) = [\omega_{obj}, \text{pos}_{obj}, \text{contact\_mask}] \in \mathbb{R}^d, \quad d \approx 10-12$$

其中 $\omega_{obj} \in \mathbb{R}^3$ 是物体角速度，$\text{pos}_{obj} \in \mathbb{R}^3$ 是物体相对手掌位置，$\text{contact\_mask} \in \{0,1\}^5$ 是各指接触状态。

**凸包更新**：使用在线增量凸包算法（或更高效的核密度估计软凸包）：

$$\text{CSS}_n = \text{ConvHull}(\{z_i\}_{i=1}^{n}), \quad z_i \in \phi(\mathcal{H}^+)$$

**软凸包替代**（更实用）：用高斯混合模型 (GMM) 拟合 $\mathcal{H}^+$ 在 $z$ 空间的分布：

$$p_{CSS}(z) = \sum_k \alpha_k \mathcal{N}(z | \mu_k, \Sigma_k)$$

$p_{CSS}(z) > \theta$ 的区域定义软 CSS 边界。

### 2.3 三种 CSS 利用机制

**机制 A：安全 Bonus Reward。**

$$r_{CSS}(s_t) = \lambda_{CSS} \cdot \log p_{CSS}(\phi(s_t)) \cdot \mathbb{1}[s_t \in \mathcal{H}]$$

处于 CSS 内部的高惯性状态获得正奖励；CSS 外部获得零奖励（不惩罚）。

**机制 B：初始化分布扩展（联动 ideas.md §3.3 方向 C）。**

$$s_0 \sim \begin{cases} \text{GraspCache} & \text{w.p. } 1-\epsilon \\ \text{Uniform}(\text{CSS}) & \text{w.p. } \epsilon \end{cases}$$

随机地从 CSS 内部采样初始化状态，让策略学习 "从高惯性状态中途开始" 如何成功——这跳过了探索的最难部分（进入高惯性状态）。

**机制 C：探索优先级。** 在 CSS 边界附近的状态获得更高的探索优先级（类似 curiosity-driven 的边界探索），鼓励策略扩展 CSS。

### 2.4 CSS 的渐进式增长

```
训练初期 (α=0.5, 慢速空间):
  → 较容易获得成功经验
  → CSS 从少量点开始构建
  → 主要用机制 B (跳过探索瓶颈)

训练中期 (α→0.7):
  → 更多成功经验积累
  → CSS 扩大并精化
  → 主要用机制 A (精确引导)

训练后期 (α→1.0):
  → CSS 已覆盖真实物理下的安全区域
  → 主要用机制 C (边界探索以发现新安全策略)
```

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/tasks/linker_hand_hora.py` | `compute_reward()` 添加 $r_{CSS}$；`reset_idx()` 支持从 CSS 采样初始化 |
| `penspin/algo/ppo/ppo_rl_teacher.py` | 在 rollout 结束后更新 CSS（GMM 参数） |
| `configs/task/LinkerHandHora.yaml` | 新增 `task.env.reward.css_scale`, `task.env.css.enabled`, `task.env.css.init_ratio` |

**需新增的文件**：

| 文件 | 内容 |
|------|------|
| `penspin/utils/convex_safe_set.py` | CSS 类：GMM 拟合 + 密度查询 + 采样 + 增量更新 |
| `experiments/exp8_CSS/` | CSS 实验脚本 |

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> 先从已训练策略中收集成功轨迹，人工构建简单 safe set，验证 "凸包初始化" 是否加速探索。

**最小实现**：
1. 运行已训练的 best checkpoint，录制 1000 条成功轨迹
2. 提取每条轨迹的 $(\omega_{obj}, pos_{obj})$ 序列
3. 在 `reset_idx()` 中随机从这些成功中间状态重新开始（跳过 snap 的难度）

| 实验 ID | 初始化来源 | 对照 | 预期 |
|---------|-----------|------|------|
| GS-4.1 | 仅 GraspCache (当前) | Baseline | 基线 |
| GS-4.2 | 50% GraspCache + 50% 成功中间状态 | GS-4.1 | 显著加速收敛 |
| GS-4.3 | 30% GraspCache + 70% 成功中间状态 | GS-4.1 | 更快但可能过拟合 |

3 组 × 3 seeds = 9 runs，约 1.5 天 on 8×A100。

**判断标准**：
- 如果成功状态初始化显著加速“首次到达”时间 → 倬包假设值得深入探索
- 结合 DemoStart 论文的 ZVF 思路：只在“时成时败”的难度上训练

---

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | CSS vs 无引导 | 是否使用 CSS | 成功率、首达时间 | HDC + Dense Reward | CSS 加速首达 2x |
| E1.2 | CSS vs HER | 结构利用方式 | Light Reward 下成功率 | HER relabeling | CSS 显著优于 HER |
| E1.3 | 三种机制消融 | A/B/C 机制开关 | 成功率 | 单一机制 | A+B 效果最好 |
| E1.4 | CSS 降维方案 | 特征选择 | CSS 质量（AUC） | 不同 $z$ 定义 | $(\omega, pos, contact)$ 最优 |

### 3.2 凸包假设验证实验

| 实验 ID | 目的 | 方法 |
|---------|------|------|
| E2.1 | 验证凸包假设 | 从已训练策略收集成功轨迹，在凸组合点重新运行仿真，检查成功率 |
| E2.2 | 凸包覆盖率分析 | CSS 内部的成功率 vs CSS 外部的成功率 |
| E2.3 | 降维信息保留 | $z$ 空间的 CSS 覆盖率 vs 原始空间的 CSS 覆盖率 |

### 3.3 新任务泛化（陀螺旋转）

| 实验 ID | 目的 | 说明 |
|---------|------|------|
| E3.1 | CSS 对初始条件敏感任务的效果 | 陀螺需要精确初始旋转速度和角度，CSS 直接缩小搜索范围 |
| E3.2 | CSS 跨任务迁移 | Thumbaround 训练的 CSS 是否对 Triangle Pass 有部分指导价值 |

### 3.4 计算资源估算

- 单次训练: ~4 GPU-hours (A100)（GMM 更新开销 ~10%）
- 消融实验总量: 4 (E1) + 3 (E2) + 2 (E3) = 9 组 × 3 种子 = 27 次训练
- 预计总耗时: ~4 天 (8×A100)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| CSS Volume | GMM 的高密度区域体积（$p > \theta$） | CSS 覆盖范围 |
| CSS Precision | CSS 内状态的成功率 | 凸包假设的有效性 |
| First-Hit Time | 首次 success_rate > 5% 的 agent_steps | 探索加速效果 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| 凸包假设在某些状态子空间不成立 | 中 | 中 | 使用 GMM 软凸包而非硬凸包；分段构建（每个旋转相位独立 CSS） |
| 训练初期成功经验太少，CSS 退化 | 中 | 高 | 与 HDC 联合：$\alpha=0.5$ 下更容易获得成功经验来初始化 CSS |
| 降维丢失关键信息 | 中 | 中 | 使用 VAE 学习降维，保留重建精度 |
| CSS 过度引导导致策略多样性丧失 | 低 | 中 | $\lambda_{CSS}$ 随训练递减；机制 C 鼓励边界探索 |

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中关联本 Idea 的 `[EXP-*]` 条目

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| *待填* | *Stage 0: 成功状态初始化* | *待运行* | *待定* |

### 迭代记录

*（实验结果到来后在此更新）*

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[Optimization#2.6 非凸优化景观理论 (Nonconvex Optimization Landscapes)]] — CSS 将 Value Landscape 中的 "稀疏踏脚石" 用凸几何连接起来
- [[InformationTheory#6.1 赋能 (Empowerment)：最大化信道容量]] — CSS 可视为 empowerment 的几何替代：处于 CSS 内的状态 "对未来有更多控制力"
- [[ReinforcementLearning#2.8 Exploration 理论：从信息论到技能发现]] — CSS 边界探索是 intrinsic motivation 的几何实例化

### 与已有论文的联系
- [[Hindsight Experience Replay]] — CSS 是 HER 的几何推广：从 "重标注目标" 到 "构建安全集"
- [[Reachability Constrained Reinforcement Learning]] — CSS 是 HJ 可达性的计算可行替代（数据驱动 vs PDE 求解）
- [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] — CSS 的机制 B（从 CSS 采样初始化）与 DemoStart 的 demo-led 初始化思想一脉相承

### 与项目其他 Idea 的联系
- 与 Idea-003 (CMR) 关联：CSS 可视为 $V_M > \theta$ 的 sublevel set；如果 CMR 已训练好 $V_M$，CSS 可以直接从 $V_M$ 导出
- 与 Idea-002 (CA-ARP) 互补：CA-ARP 控制 "怎么探索"，CSS 控制 "去哪里探索"——联合使用理论上最优
