---
tags:
  - insight
  - sim-to-real
  - dynamics
  - adaptation
  - DNPM
aliases:
  - Test-Time Contact Adaptation
  - TTCA
  - 部署时接触适应
created: 2026-02-28
status: draft
feasibility: B
novelty: A
target-venue: CoRL/ICRA
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]]"
  - "[[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]]"
  - "[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]]"
  - "[[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]]"
---

# Test-Time Contact Adaptation: Online Physics Identification for Dynamic Non-Prehensile Sim-to-Real Transfer

> [!abstract] 核心贡献（一句话）
> 我们提出 Test-Time Contact Adaptation (TTCA)：在部署时通过短暂的 "探测性交互"（diagnostic touches）在线辨识接触物理参数（摩擦系数、恢复系数、质量分布），利用辨识结果实时调整策略行为，解决动态非紧握操作中仿真-真机接触模型的 domain gap——这是该类任务 Sim-to-Real 的核心瓶颈。

---

## 1. 问题定义与动机（Intro 故事线）

### 1.1 大背景引入

Sim-to-Real 迁移是将强化学习策略部署到真实机器人的关键环节。对于准静态操作，域随机化 (Domain Randomization, DR) 已经足够——因为准静态下接触参数的精确值不太重要（力闭合提供了足够的容错空间）。然而，**动态非紧握操作对接触参数极其敏感**：

- Thumbaround 中，$\mu$（摩擦系数）0.1 的偏差可能导致 spin 阶段笔从拇指上滑落
- 颠锅中，$e$（恢复系数）0.05 的偏差可能导致食材弹跳轨迹完全偏离预期
- 陀螺旋转中，质量分布的微小不对称导致进动角完全不同

旋转一圈（~0.5秒）内累积的动力学误差足以使预训练策略完全失效。DR 无法穷尽连续参数空间的所有组合，而固定参数的仿真器无法捕捉这些敏感性。

### 1.2 现有方法的局限

**局限 1：域随机化在高敏感参数上失效。** DR 通过在训练时随机化参数来学习鲁棒策略，但对 DNPM 任务，参数空间中的 "安全通道" 太窄——随机化使策略学会了 "在所有参数下都勉强成功的保守策略"，而非 "针对当前参数精确执行的最优策略"。

**局限 2：HORA ([[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]]) 的适应模块以本体感觉估计 extrinsics，但不显式辨识物理参数。** HORA 学习了一个从本体感觉历史到 latent extrinsics 的映射，但这个映射是黑盒的——无法解释策略为什么改变行为，也无法保证在 OOD 物理参数下的推断和适应质量。

**局限 3：RialTo ([[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]]) 在仿真中匹配真实数据，但需要丰富的真实轨迹数据。** 对于 DNPM 这类高失败率任务，收集足够的真机轨迹数据本身就极其昂贵。

### 1.3 我们的洞见

> [!tip] Key Insight
> 动态非紧握操作中，**策略可以通过短暂的 "探测性交互" 主动获取接触参数信息**：
> - 轻触物体 → 从接触力响应估计 $\mu$（摩擦系数）和局部刚度
> - 轻推物体观察运动 → 估计质量和质心位置
> - 微抛接 → 估计恢复系数 $e$
>
> 关键突破：不是被动等待策略在执行任务时 "偶然发现" 参数（HORA 的隐式方式），而是**主动设计一段 2-3 秒的探测序列**，在任务执行前完成参数辨识——类似人类拿到新物体时会先 "掂一掂"、"搓一搓"。
>
> 这结合了 [[InformationTheory]] 中的主动感知 (Active Perception) 思想和 [[Dynamics]] 中的系统辨识理论。

### 1.4 贡献声明

1. 我们设计了一套针对灵巧手的 **探测性交互序列** (Diagnostic Touch Protocol)，能在 2-3 秒内辨识 $(\mu, e, m, p_{com})$ 四个关键接触参数
2. 我们提出 **参数条件化策略** (Parameter-Conditioned Policy)：将辨识出的参数作为策略的显式条件，替代 HORA 式的黑盒 extrinsics
3. 我们在仿真中验证了 TTCA 相比 Domain Randomization 和 HORA 适应模块在高参数敏感性任务下的优势，并提供了真机部署的可行性分析

---

## 2. 方法论（Method）

### 2.1 问题形式化

将部署场景建模为参数化 MDP $\mathcal{M}_\phi$，其中 $\phi = (\mu, e, m, p_{com})$ 是未知接触物理参数。

目标：学习一对策略：
1. **Diagnostic Policy** $\pi_D$：执行探测性交互，输出参数估计 $\hat{\phi}$
2. **Task Policy** $\pi_T(\cdot | \hat{\phi})$：基于 $\hat{\phi}$ 执行目标任务

### 2.2 Diagnostic Touch Protocol

设计三段探测序列：

**Phase D1: 静态压力测试（~0.5秒）**
- 动作：食指轻触物体表面，施加已知法向力 $F_n^*$
- 观测：物体是否滑动 → 如果滑动，$\hat{\mu} < F_n^* / mg$；如果不滑动，逐渐增加 $F_n^*$ 直到滑动边界
- 辨识：$\hat{\mu} = F_n^{*}(\text{slip onset}) / mg$

**Phase D2: 动态推击测试（~1.0秒）**
- 动作：用已知力矩推击物体，使其在手掌上平移一小段距离
- 观测：从物体的加速度响应推断质量 $\hat{m} = F_{push} / a_{obs}$，从运动偏心度推断质心 $\hat{p}_{com}$

**Phase D3: 微抛接测试（~1.0秒）**
- 动作：将物体微抛（1-2 cm 高度），观察弹跳特性
- 观测：弹跳速度比 → $\hat{e} = |v_{after}| / |v_{before}|$

### 2.3 参数条件化策略训练

在仿真中通过 DR 训练 $\pi_T(\cdot | \hat{\phi})$：

$$\pi_T = \arg\max_\theta \mathbb{E}_{\phi \sim p(\phi)} [\mathbb{E}_{\pi_T(\cdot|\phi)} [R(\tau)]]$$

关键区别于标准 DR：策略**显式接收参数作为输入**，而非隐式适应。这使策略在知道参数的条件下能做出更精确的控制（而非保守的鲁棒策略）。

**实现方式**：将 $\hat{\phi}$ 拼接到 `priv_info_buf` 中（替代或补充现有的 obj_mass, obj_friction 等维度），Teacher 策略在训练时直接使用真值 $\phi$，Student 策略用 Diagnostic Policy 估计的 $\hat{\phi}$ 替代。

### 2.4 与 HORA 适应模块的区别

| 对比维度 | HORA Adaptation | TTCA |
|---------|----------------|------|
| 辨识方式 | 被动（从任务执行历史隐式估计） | **主动**（设计探测序列显式辨识） |
| 辨识结果 | 黑盒 latent extrinsics | **可解释**的物理参数 $(\mu, e, m, p_{com})$ |
| 辨识时机 | 实时（但需要多步历史积累） | **任务前**（2-3 秒完成） |
| OOD 鲁棒性 | 依赖训练分布内的泛化 | 物理模型驱动，**对 OOD 参数天然鲁棒** |

### 2.5 实现细节

**需修改的文件**：

| 文件 | 修改内容 |
|------|---------|
| `penspin/tasks/linker_hand_hora.py` | 添加 diagnostic 阶段的环境逻辑（D1/D2/D3 三段探测） |
| `penspin/algo/models/models.py` | `priv_info_buf` 中 $\phi$ 维度从不可见切换到可见（参数条件化） |
| `configs/task/LinkerHandHora.yaml` | 新增 `task.env.ttca.enabled`, `task.env.ttca.diagnostic_steps`, `task.env.ttca.param_noise` |

**需新增的文件**：

| 文件 | 内容 |
|------|------|
| `penspin/utils/diagnostic_policy.py` | 探测性交互策略（规则驱动或简单 RL） |
| `penspin/utils/param_estimator.py` | 从探测观测到参数估计的物理模型 |
| `experiments/exp9_TTCA/` | TTCA 实验脚本 |

---

## 3. 实验计划（Experiment Plan）

### 3.0 Stage 0: Grid Search 快速验证（⚡ 优先执行）

> [!important] 算力充足策略
> 先验证 "显式物理参数作为策略输入" 的核心假设，无需实现诊断性交互。

**最小实现**：将 `priv_info_buf` 中已有的 `obj_mass`, `obj_friction` 从 Teacher-only 切换为 Student 可见，观察“知道真实参数”比“被动估计”提升多少。

| 实验 ID | 策略输入 | 参数范围 | 预期 |
|---------|---------|---------|------|
| GS-5.1 | 无物理参数（当前 Student）| $\mu \in [0.3,1.2]$ | Baseline |
| GS-5.2 | 精确参数（Oracle）| $\mu \in [0.3,1.2]$ | 显著优于 Baseline |
| GS-5.3 | 带噪声的参数（模拟估计）| $\mu + \mathcal{N}(0, 0.1)$ | 接近 Oracle |

3 组 × 4 参数点 × 3 seeds = 36 runs，约 2 天 on 8×A100。

**判断标准**：
- Oracle 比 Baseline 提升 >15% → “显式参数”假设成立，值得设计诊断策略
- 带噪声仍然优于 Baseline → 诊断精度不需要很高

---

### 3.1 核心消融实验

| 实验 ID | 目的 | 自变量 | 因变量 | 对照组 | 预期结果 |
|---------|------|--------|--------|--------|----------|
| E1.1 | TTCA vs DR | 适应方式 | 在参数偏移下的成功率 | 标准 DR | 偏移 >10% 时 TTCA 显著更优 |
| E1.2 | TTCA vs HORA adaptation | 辨识方式 | 成功率、前 5 步成功率 | HORA adaptation module | TTCA 在第一次尝试就接近最优 |
| E1.3 | 显式参数 vs 隐式 extrinsics | 策略条件化方式 | 成功率 w.r.t. 参数偏移量 | 相同训练但无参数输入 | 显式条件化在大偏移下优势明显 |
| E1.4 | Diagnostic 相消融 | D1/D2/D3 各段开关 | 参数估计精度 + 成功率 | 单阶段 | D1（摩擦）贡献最大 |

### 3.2 参数敏感性分析

| 实验 ID | 参数 | 偏移范围 | 预期 |
|---------|------|---------|------|
| E2.1 | $\mu \in [0.3, 1.2]$ | 训练值 ±50% | $\mu$ 是 DNPM 最敏感参数 |
| E2.2 | $e \in [0.0, 0.8]$ | 训练值 ±80% | $e$ 影响抛接任务 |
| E2.3 | $m \in [0.01, 0.1]$ kg | 训练值 ±200% | 质量影响惯性力 |
| E2.4 | 联合偏移 | 同时偏移 $\mu, e, m$ | 真机最接近场景 |

### 3.3 仿真中模拟真机场景

| 实验 ID | 场景 | 说明 |
|---------|------|------|
| E3.1 | 未知笔 A（重, 粗糙） | $m=0.08$kg, $\mu=1.0$ |
| E3.2 | 未知笔 B（轻, 光滑） | $m=0.02$kg, $\mu=0.4$ |
| E3.3 | 湿手指模拟 | $\mu$ 从 0.8 渐变到 0.3 |

### 3.4 计算资源估算

- 单次训练: ~4 GPU-hours (A100)
- 消融实验总量: 4 (E1) + 4 (E2) + 3 (E3) = 11 组 × 3 种子 = 33 次训练
- 预计总耗时: ~5 天 (8×A100)

### 3.5 关键指标

| 指标 | 计算方式 | 意义 |
|-----|---------|------|
| Success Rate | 现有 [METRICS] | 任务完成 |
| Param. Estimation Error | $\|\hat{\phi} - \phi^*\| / \|\phi^*\|$ | 辨识精度 |
| Diagnostic Cost | 探测阶段的步数 / 总步数 | 辨识效率 |
| First-Try Success | 辨识后第一次任务执行的成功率 | 快速适应能力 |

---

## 4. 风险与缓解

| 风险 | 概率 | 影响 | 缓解策略 |
|-----|------|------|---------|
| 探测交互可能不安全（物体掉落） | 中 | 高 | 探测力度限制在安全范围内；失败后可重新抓取 |
| 参数估计精度不足 | 中 | 中 | 使用贝叶斯估计 + 多次探测融合 |
| 真机传感器噪声导致估计偏差 | 中 | 中 | 在仿真训练时添加传感器噪声模拟 |
| 探测阶段延长任务总时间 | 低 | 低 | 2-3 秒探测换取整个任务的成功率大幅提升 |

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
| *待填* | *Stage 0: Oracle参数输入* | *待运行* | *待定* |

### 迭代记录

*（实验结果到来后在此更新）*

---

## 7. 知识库关联

### 与 Foundations 的联系
- [[Dynamics#10. Future Outlook: Differentiable Physics (可微物理)]] — 可微物理的在线辨识是 TTCA 的理论基础
- [[ContactMechanics#6. 仿真到现实 (Sim2Real)]] — 接触参数的 Sim-Real gap 是本文攻击的核心问题
- [[SignalProcessing]] — 探测信号的处理和参数估计本质是信号处理问题
- [[InformationTheory]] — 主动探测设计是 Active Perception 的直接应用

### 与已有论文的联系
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] — HORA 的适应模块是本文的核心 baseline
- [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] — 关节级神经动力学模型可作为 TTCA 的补充
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] — Real-to-Sim-to-Real 管线的参考
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 在线修正的思路与 TTCA 互补

### 与项目其他 Idea 的联系
- 与 Idea-001 (PAI) 协同：TTCA 辨识出的 $\mu$ 可直接影响 PAI 中 catch 阶段的最优 $K_p$——柔顺度需要根据摩擦系数调整
- 是 HDC 的自然后续：HDC 解决仿真中的训练，TTCA 解决真机上的部署——两者合在一起构成完整的 Sim-to-Real 管线
