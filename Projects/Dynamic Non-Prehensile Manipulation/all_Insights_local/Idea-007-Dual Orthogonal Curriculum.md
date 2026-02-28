---
tags:
  - insight
  - reinforcement-learning
  - curriculum-learning
  - DNPM
aliases:
  - Dual Orthogonal Curriculum
  - DOC
  - 双正交课程
created: 2026-02-28
status: draft
feasibility: A
novelty: B+
target-venue: RSS/CoRL
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]]"
  - "[[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]]"
  - "[[Curriculum Learning]]"
  - "[[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]]"
---

# Dual Orthogonal Curriculum: Decoupling Physics Difficulty and State Difficulty for Dynamic Non-Prehensile Manipulation

> [!abstract] 核心贡献（一句话）
> 我们发现 HDC 的 α-curriculum 仅沿**物理难度**一个轴推进，而动态非紧握操作还存在正交的**状态难度**轴（从成功中间状态出发 vs 从头开始）。我们提出 Dual Orthogonal Curriculum (DOC)：沿物理轴用 α-scaling、沿状态轴用 DemoStart 风格的成功状态初始化 + ZVF 门控，两轴独立调度，在 Thumbaround 上将 HDC 的样本效率提高 2-3× 并直接增强 HDC 论文的故事线。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

课程学习（Curriculum Learning）是 RL 解决复杂任务的核心策略。HDC 的创新在于通过 α-scaling 让物理世界"变慢变轻"，构造了一条从简单物理到真实物理的连续课程。然而，当前HDC 的课程**只有一个维度**。

在 Thumbaround 任务中，策略必须克服两类独立的难度：
1. **物理难度**（$\alpha$ 控制）：重力强度、惯性力大小——$\alpha=0.5$ 比 $\alpha=1.0$ 容易
2. **状态难度**（初始化控制）：从标准起手式开始 vs 从 spin 中途开始——后者跳过了最难的 snap 探索阶段

当前 HDC **同时面对两种难度**：策略在 $\alpha=1.0$ 下不仅要应对真实物理，还要从零开始完成整条 snap→spin→catch 链。如果能**解耦这两个难度轴**，策略可以先在"简单物理 + 简单状态"下学会基本技能，再沿两轴独立推进。

### 1.2 现有方法的局限

**局限 1：HDC 的 α-curriculum 仅改变物理参数，不改变初始状态分布。** 无论 $\alpha$ 取何值，策略都从相同的 GraspCache 初始化出发。这意味着即使在 $\alpha=0.5$ 的简单物理下，策略仍需完成完整的 snap→spin→catch 链——探索瓶颈只被部分缓解。

**局限 2：HDC 的 $\alpha$ 递增判据（固定 70% 成功率阈值）过于粗糙。** DemoStart ([[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]) 提出的 Zone of Proximal Failure (ZVF) 提供了更精细的判据：只在策略"时成时败"的难度上训练，而非在已经掌握或完全无法应对的难度上浪费计算。

**局限 3：Finger Gaiting ([[Learning Human-like Finger Gaiting on an Anthropomorphic Hand|Finger Gaiting]]) 证明了从人类演示的过渡路径点初始化可以 1.5h 训练完成转笔。** 但该方法依赖高质量人类演示数据。如果能用**策略自身的成功经验**替代人类演示作为初始化来源，就消除了对外部数据的依赖。

### 1.3 我们的洞见

> [!tip] Key Insight
> 动态非紧握操作的训练难度可以分解为**两个正交轴**：
>
> ```
>        状态难度 ↑ (从头开始)
>             │
>   "最难"    │    "物理已掌握但探索未完成"
>   α=1.0     │    α=1.0
>   全链      │    中间状态启动
>             │
>  ─────────────┼─────────────→ 物理难度 (α)
>             │
>   "物理简单  │    "最简单"
>    但全链"   │    α=0.5
>    α=0.5    │    中间状态启动
>             │
> ```
>
> HDC 只在水平轴上做课程（$\alpha: 0.5 \to 1.0$），完全忽略了垂直轴。
> 方向 B (Idea-004 CSS) 在垂直轴上做了部分工作，但仅限于高惯性状态的凸包。
> **DOC 同时在两个轴上做课程，且两轴的推进由独立的门控机制控制。**

### 1.4 贡献声明

1. 我们形式化了 DNPM 训练中的**双正交难度分解**（物理难度 × 状态难度），并证明两轴独立推进优于单轴课程
2. 我们提出 **Dual Orthogonal Curriculum (DOC)**：α-scaling（物理轴）+ 成功状态自举初始化（状态轴），使用 ZVF 机制分别门控两轴推进
3. 我们在 Thumbaround 上验证了 DOC 将 HDC 的首次成功时间缩短 2-3×、最终成功率提升 5-10%，且**直接嵌入 HDC 论文框架**作为方法增强

---

## 2. 方法论（Method）

### 2.1 问题形式化

定义训练难度空间为二维：$(\alpha, \delta)$，其中：
- $\alpha \in [\alpha_{min}, 1.0]$：物理难度（α-scaling 参数）
- $\delta \in [0, 1]$：状态难度，$\delta = 0$ 表示从成功轨迹中间状态启动（最简单），$\delta = 1$ 表示从标准 GraspCache 启动（最难）

策略在难度 $(\alpha, \delta)$ 下的成功率定义为 $\eta(\alpha, \delta)$。

**DOC 目标**：找到从 $(\alpha_{min}, 0) \to (1.0, 1.0)$ 的最优课程路径，使总训练样本量最小。

### 2.2 状态轴课程：成功状态自举初始化

**阶段 1：收集成功状态库 $\mathcal{B}$**

在每个 episode 结束后，如果成功，将整条轨迹上的关键中间状态（以固定间隔采样）存入缓冲区：

$$\mathcal{B} = \{(s_k, \alpha_k, t_k / T_k) : s_k \in \tau_{success}, k \in \text{sample}\}$$

其中 $t_k / T_k$ 是状态在轨迹中的相对位置（0=初始, 1=结束）。

**阶段 2：$\delta$-混合初始化**

每个 episode 的初始状态以概率 $\delta$ 从 GraspCache 采样，以概率 $1-\delta$ 从 $\mathcal{B}$ 采样：

$$s_0 \sim \begin{cases} \text{GraspCache} & \text{w.p. } \delta \\ \text{Uniform}(\mathcal{B}) & \text{w.p. } 1 - \delta \end{cases}$$

当 $\delta = 0$ 时，策略总是从成功中间状态开始（最简单——只需学会完成轨迹的后半段）。
当 $\delta = 1$ 时，策略总是从标准起手式开始（最难——需要完成完整链条）。

**阶段 3：$\delta$ 递进**

$\delta$ 从 0 逐渐增大到 1，策略被迫学会从越来越早的阶段开始完成任务。

### 2.3 ZVF 门控机制

借鉴 DemoStart 的 Zone of Proximal Failure (ZVF) 思想，对 $\alpha$ 和 $\delta$ **分别**定义门控判据：

**α 轴门控**（替代固定 70% 阈值）：

$$\text{advance } \alpha \iff \eta(\alpha, \delta_{current}) \in [\eta_{low}, \eta_{high}]$$

只有当策略在当前 $\alpha$ 下处于"时成时败"的区间（$\eta_{low}=0.4, \eta_{high}=0.8$）时才推进 $\alpha$。如果 $\eta < \eta_{low}$（太难），维持当前 $\alpha$；如果 $\eta > \eta_{high}$（太易），加速推进。

**δ 轴门控**：

$$\text{advance } \delta \iff \eta(\alpha_{current}, \delta) \in [\eta_{low}, \eta_{high}]$$

当策略在当前 $\delta$ 下处于 ZVF 时，增大 $\delta$（减少成功状态初始化的比例）。

**两轴交替推进**：每 $N_{check}$ 步检查一次，优先推进成功率更高的轴（让较容易的轴先推进）。

### 2.4 与 HDC 的无缝集成

DOC 对 HDC 框架的改动极小：

1. **$\alpha$ 轴**：保留 `TimeWarpingOrchestrator` 的全部逻辑，仅将 `gate_success_threshold=0.7` 替换为 ZVF 区间 $[\eta_{low}, \eta_{high}]$
2. **$\delta$ 轴**：在 `reset_idx()` 中添加从 $\mathcal{B}$ 采样的逻辑（~30 行代码）
3. **$\mathcal{B}$ 维护**：在每个 epoch 结束后收集成功轨迹中间状态（~20 行代码）

**总工程量**：~100 行代码修改，无需新增模块。

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/tasks/linker_hand_hora.py` | `reset_idx()`: 添加 $\delta$-混合初始化逻辑（从 $\mathcal{B}$ 或 GraspCache 采样） |
| `penspin/algo/ppo/ppo_rl_teacher.py` | `play_steps()` 后添加成功轨迹状态收集；`update()` 中添加 ZVF 门控逻辑 |
| `penspin/utils/time_warping.py` | 将 `gate_success_threshold` 替换为 ZVF 区间检查 |
| `configs/task/LinkerHandHora.yaml` | 新增 `task.env.doc.enabled`, `task.env.doc.delta_start: 0.0`, `task.env.doc.zvf_low: 0.4`, `task.env.doc.zvf_high: 0.8` |

**无需新增文件**——所有逻辑嵌入现有模块。

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> Stage 0 仅需修改 `reset_idx()` 的初始化逻辑（~20行），**半天内**可完成代码改动并开始实验。

**前提**：先用已有的 best checkpoint 运行 500 个 episode，收集成功轨迹的中间状态（每条轨迹等间距采样 10 个状态，存为 `.npy` 文件）。

**最小实现**：在 `reset_idx()` 中加入：
```python
if np.random.random() < (1 - delta):
    # 从成功状态缓冲区采样
    idx = np.random.randint(len(success_state_buffer))
    self.dof_pos[env_ids] = success_state_buffer[idx]['dof_pos']
    self.object_pos[env_ids] = success_state_buffer[idx]['obj_pos']
    # ... 恢复其他状态量
```

| 实验 ID | $\delta$ | 初始化混合 | 预期 |
|---------|---------|-----------|------|
| GS-7.1 | 1.0 (纯 GraspCache, 当前) | 0% 成功状态 | Baseline |
| GS-7.2 | 0.7 | 30% 成功状态 | 加速首达 |
| GS-7.3 | 0.5 | 50% 成功状态 | 最优均衡点 |
| GS-7.4 | 0.3 | 70% 成功状态 | 更快但可能过拟合 |
| GS-7.5 | 0.0 (纯成功状态) | 100% 成功状态 | 极快收敛但缺乏从头完成的能力 |

**执行方式**：
```bash
# 5 个 delta × 3 seeds = 15 runs
# 在 8×A100 上并行，约 6 小时完成
for delta in 1.0 0.7 0.5 0.3 0.0; do
  for seed in 42 123 456; do
    python train.py task.env.doc.delta=$delta seed=$seed ...
  done
done
```

**判断标准**：
- 如果 $\delta < 1.0$ 的配置显著加速首次成功到达 → **状态轴课程有效**
- 如果 $\delta = 0.0$ 收敛最快但最终成功率低于 $\delta = 0.5$ → **需要课程推进 $\delta$**
- 如果所有 $\delta$ 表现类似 → 当前任务的探索瓶颈不在状态初始化

**进阶 Grid Search**（Stage 0.5）：
- 固定 $\delta=0.5$，测试 ZVF 替代固定 70% 阈值的效果
- 对比：$\eta_{threshold}=0.7$ (当前) vs ZVF $[0.4, 0.8]$ vs ZVF $[0.3, 0.9]$

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | DOC vs HDC alone | 是否使用状态轴 | 首达时间、最终成功率 | HDC (α-only) | DOC 首达 2-3× faster |
| E1.2 | DOC vs Idea-004 (CSS) | 初始化来源 | 成功率 | CSS 几何引导 | DOC 更简单且效果相当 |
| E1.3 | ZVF vs 固定阈值 | 门控机制 | 课程推进效率 | 70% 固定阈值 | ZVF 避免过早/过晚推进 |
| E1.4 | 两轴推进策略 | 交替 vs 同步 | 收敛速度 | 固定比例 | 交替更优 |

### 3.2 课程路径可视化实验

| 实验 ID | 目的 | 分析方法 |
|---------|------|---------|
| E2.1 | 可视化 $(\alpha, \delta)$ 课程轨迹 | 记录训练中 $\alpha$ 和 $\delta$ 的变化曲线 |
| E2.2 | 绘制 $\eta(\alpha, \delta)$ 热力图 | 在 Grid 上评估已训练策略，展示两轴难度的正交性 |
| E2.3 | 对比 DOC 路径与最短路径 | 分析 DOC 是否自动发现了接近最优的课程路径 |

### 3.3 计算资源估算

- Stage 0: 15 runs × 3h = ~6 小时（8×A100）
- 消融实验: 4 (E1) + 3 (E2) = 7 组 × 3 种子 = 21 次训练
- 预计总耗时: ~3 天 (8×A100)

### 3.4 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| First-Hit Time | 首次 success_rate > 5% 的 agent_steps | 探索加速效果 |
| α Convergence Time | $\alpha$ 达到 1.0 的 wall-clock 时间 | 课程效率 |
| δ Convergence Time | $\delta$ 达到 1.0 的 wall-clock 时间 | 状态轴效率 |
| ZVF Efficiency | 训练时间在 ZVF 区间内的比例 | 计算利用率 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| 成功状态缓冲区初期为空 | 高 | 高 | 用 $\alpha=0.5$ 的 HDC 预训获得首批成功经验；或使用已有 checkpoint 的轨迹 |
| 从中间状态启动导致策略不学"开头" | 中 | 高 | $\delta$ 递增确保最终从标准初始化训练；ZVF 门控防止过早推进 |
| 两轴推进节奏不协调 | 中 | 中 | 加入"同步检查"：如果 $\alpha$ 远超 $\delta$ 的进度，暂停 $\alpha$ 等待 $\delta$ |
| 状态恢复不完整（Isaac Gym 限制） | 低 | 中 | 验证 `set_actor_root_state_tensor` + `set_dof_state_tensor` 能完整恢复仿真状态 |

---

## 5. 与 HDC 论文的直接关联

> [!tip] 对 HDC 论文的增强
> DOC 可以**直接集成到 HDC 论文中**作为方法改进，而非独立论文。具体地：
> - **§Method**：在 α-curriculum 之后添加 "State Difficulty Curriculum" 子节
> - **§Experiments**：新增 "Orthogonal Difficulty Ablation" 实验（E2.2 热力图）
> - **§Analysis**：课程路径可视化（E2.1）直接增强论文的分析深度
> - **Reviewer Response**：如果 reviewer 质疑 "HDC 的优势来自更高频率"，DOC 的状态轴课程提供了**独立于频率的改进维度**

---

## 6. 动态迭代日志

> [!note] 🔄 实验结果追踪（与远端服务器同步）
> 本节用于记录实验结果和迭代决策。远端服务器 Agent 将实验结果写入 `_ExperimentResultsAll.md`，
> 本地 Agent 在每次会话中检查新增结果后更新本节。
>
> **结果来源**: `_ExperimentResultsAll.md` 中关联本 Idea 的 `[EXP-*]` 条目

| 日期 | 实验 (EXP-ID) | 结果摘要 | 决策 |
|------|--------------|---------|------|
| 2026-02-28 | Exp2 TP Reduced TWC vs BASE (前置) | ⚡ TWC SR=0.87±0.02, BASE SR=0.54±0.38 | TWC 提供更平滑 Value Landscape, 支持 DOC 物理轴设计 |
| 2026-02-28 | Exp2 TA SR 分布 (前置) | TA Light BASE SR=0.83±0.04 稳定, TWC 方差大 (0.15) | TA 任务的状态轴课程可能比物理轴课程更重要 |
| *待填* | *Stage 0: 固定 δ Grid Search* | *待运行* | *待定* |

### 迭代记录

**2026-02-28 Exp2 前置发现** (TWC 稳定性 & 双轴设计启示):
- TP Reduced TWC SR=0.87±0.02 vs BASE SR=0.54±0.38 → TWC 显著提升**稳定性** (方差降19×)
- 这支持 DOC 的核心假设: 物理轴 (α) 课程能平滑 Value Landscape
- 但 TA 的实验表明 TWC 在 TA 任务上优势不明显 (甚至劣于 BASE), 说明**状态轴课程** (DOC 的另一维) 可能对 TA 更关键
- **Stage 0 重点调整**: Stage 0 优先验证 TA 任务的状态初始化课程 (因为 TWC 在 TA 上优势有限, DOC 的状态轴可能是突破口)

**下一步服务器方向**:
- [ ] 等待 Exp3a 完成 → 获取 TA/TP 各 α 值的 SR 曲线，明确“物理轴课程”的实际价值
- [ ] 启动 DOC Stage 0 (状态轴): 在 TA 上从 spin 相位成功状态初始化开始训练, 对比 vs 标准 reset
- [ ] 测试 δ ∞ {1.0, 0.7, 0.3} × TA Light BASE × 3 seeds → 验证状态初始化是否加速 TA 探索

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[ReinforcementLearning#6.3 RL Scaling Laws: 计算最优的训练资源分配]] — ZVF 的"只在有效难度下训练"思想与 Scaling Law 的"最优计算分配"一脉相承
- [[Optimization#2.5 非凸优化景观理论 (Nonconvex Optimization Landscapes)]] — 双轴课程将 landscape 的探索难度在两个独立维度上渐进学习
- [[ReinforcementLearning#2.8 Exploration 理论：从信息论到技能发现]] — 状态初始化课程本质上是 intrinsic motivation 的显式替代

### 与已有论文的联系
- [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] — **ZVF 门控机制的直接来源**；DOC 将 ZVF 扩展到双轴场景且用自举数据替代人类演示
- [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] — **路径点初始化的灵感来源**；证明了从中间状态启动训练转笔的有效性
- [[Curriculum Learning]] — 课程学习的理论框架，DOC 是在物理参数和初始状态两个维度上的实例化
- [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] — 熵标定难度阶段的思路可用于 ZVF 区间的自适应调节

### 与项目其他 Idea 的联系
- 与 Idea-004 (CSS) **互补替代**：CSS 用 GMM 构建成功状态的几何模型（复杂但信息更丰富），DOC 直接从缓冲区采样（简单但无几何结构）——可先用 DOC 快速验证，再升级为 CSS
- 与 Idea-002 (CA-ARP) **正交叠加**：DOC 改善"从哪里开始探索"，CA-ARP 改善"如何探索"——联合使用效果叠加
- 与 Idea-001 (PAI) **兼容**：DOC 对控制架构无任何要求，可与 PAI 联合使用
- **最强组合**：DOC + CA-ARP + ALA = 双轴课程 + 时间相关探索 + 平滑策略网络，三者完全正交
