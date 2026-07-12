---
tags:
  - paper
  - safe-rl
  - world-model
  - constrained-rl
  - lagrangian
  - WMTS
aliases:
  - SafeDreamer
paper-year: 2024
read-date: 2026-06-15
venue: ICLR 2024
paper-pdf: "[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Optimization]]"
  - "[[StochasticProcess]]"
  - "[[ControlTheory]]"
  - "[[WorldModels]]"
  - "[[Final_WMTS]]"
---

# SafeDreamer: Safe Reinforcement Learning with World Model

> [!abstract] 核心贡献
> 把 **Lagrangian 约束方法**与 **world-model 内的安全规划（safety planning）**统一进 DreamerV3，并给 world model 加上 **cost decoder + cost critic**，使 agent 能在想象中既估回报又估长期成本。它在 Safety-Gymnasium（低维 + 纯视觉）上达到**近零成本（near-zero-cost）**，而纯 Lagrangian model-free 方法在成本阈值趋近 0 时往往要么违约、要么完不成任务。是**唯一同时支持 视觉+低维 + Lagrangian + 在线规划(OSRP) + 背景规划(BSRP)**的方法。（PKU Yaodong Yang 组）

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — CMDP 与约束 RL；Lagrangian 对偶把约束问题转成 min-max。
> - [[Optimization#2.2 拉格朗日对偶：把约束"价格化"]] — 拉格朗日对偶 + 对偶上升（dual ascent / PID-Lagrangian）；Constrained CEM 规划。
> - [[ControlTheory]] — OSRP = world model 内的 MPC（receding-horizon 在线规划），与 CBF/安全集思想呼应。
> - [[StochasticProcess]] — DreamerV3 离散 latent + CEM 采样轨迹分布。
> - [[WorldModels#6.1 世界模型作安全调度器（Look-ahead Safety Filter）]] — SafeDreamer 的 OSRP 正是该节的具体实现（前瞻 rollout 筛掉超 cost 轨迹）；其"假安全"风险对应 [[WorldModels#6.2 Dream RL 的对抗性风险]]。
> - [[Final_WMTS]] — **WMTS 安全过滤模块的直接模板**：OSRP 对候选 action chunk 按预测 cost ≤ b 过滤；cost critic ≈ WMTS reliability head。
>
> **暗线定位**：SafeDreamer 是 **认知不确定性三用** 暗线"规划护栏"面的安全版——WM 在 OOD 对 cost 过度乐观 = "假安全"，本质是缺 epistemic 度量；WMTS 用 ensemble LCB（[[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]]）给 cost 预测带上不确定性带，才敢用它当护栏。cost critic 接长期安全亦呼应"价值即 Lyapunov"暗线（[[ControlTheory#10.4 被动性与"价值即 Lyapunov"]]）。
>
> **核心技术**: CMDP, Lagrangian/对偶上升, Cost Critic, OSRP(在线安全规划)/BSRP(背景安全规划), Constrained CEM, TD(λ) for cost

## 0. 阅读定位与范本价值

WMTS 五模块流水线的 **safety filter** 一环，SafeDreamer 是最贴近的现成模板。理论上它复用 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]] 的 RSSM/TD(λ)（不重复推导），新增的是**把"安全"从 reward 里拆出来当独立 cost 通道，并用 Lagrangian + 规划在 world model 里平衡长期 reward 与 cost**。读它要回答：WMTS 的 safety filter 该用"在线规划过滤 chunk"（OSRP）还是"背景更新安全 actor"（BSRP-Lag）？cost 在灵巧手上如何定义？又因是同校（PKU）同方向工作，迁移/合作成本低。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
真实部署的 RL 必须满足安全约束。把安全写成 cost 约束（CMDP）后，主流 **Lagrangian** 方法在**成本阈值趋近 0** 时常失败：要么违约，要么为了不违约而完不成任务；且 model-free 样本低效、多数只支持低维输入。SafeDreamer 用 world model 的样本效率 + 规划的前瞻性来同时拿到高回报和近零成本。

### 1.2 直观隐喻
- **纯 Lagrangian（PPO-Lag 等）**：像"事后罚款调节"——罚太轻→违规，罚太重→畏手畏脚做不成事；在"零容忍"阈值下罚款系数来回震荡，学不稳。
- **SafeDreamer**：像"在脑内世界里先模拟若干条路线 → 筛掉会撞的 → 在安全路线里挑回报最高的"，同时配一个**长期安全 critic** 防止只顾眼前安全而埋下远期隐患。

可证伪含义：优势应集中在"成本阈值极低 + 需要前瞻才能避险"的任务；若危险是瞬时不可预测的，WM 规划的前瞻性帮助有限。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| CPO / PPO-Lag / TRPO-Lag | CMDP + Lagrangian 对偶 | near-zero b 下乘子震荡、违约或完不成；model-free 样本低效；多只支持低维 |
| MPC / SafeLOOP（在线规划） | WM 内 lookahead 选安全动作 | 有限 horizon → 短视、局部最优；无 critic 接长期安全 |
| MBPPO-Lag（背景规划） | ensemble Gaussian + 安全 value 更新 PPO/SAC | 难处理视觉输入 |
| LAMBDA / Safe SLAC（视觉 WM + Lag） | DreamerV1/SLAC + Lagrangian | DreamerV1 不稳、不支持低维、未用在线规划 |
| **SafeDreamer** | DreamerV3 + Lagrangian + OSRP + BSRP + cost critic | 仍需定义 cost 函数；规划计算开销 |

### 1.4 Delta 分析
把 SafeRL 的两条主线——**Lagrangian 对偶** 与 **world-model 内安全规划**——统一进稳定的 DreamerV3，并用 **cost critic** 把"长期安全"接进规划（解决纯 MPC 短视）。Table 1 中它是**唯一**同时勾选 Vision + Low-dim + Lagrangian + Online Planning + Background Planning 的方法。

## 2. 核心方法与理论（原理与理论：CMDP → Lagrangian → WM 内安全规划）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $s_t=(h_t,z_t)$ | latent（确定 $h_t$ + 离散 $z_t$） | encoder/RSSM | learned | DreamerV3 模型状态 | 非物理状态 |
| $\hat r_t,\hat v_{r_t}$ | 标量 | reward decoder/critic | learned | 回报信号与回报价值 | — |
| $\hat c_t,\hat v_{c_t}$ | 标量 | **cost decoder/critic** | learned | **安全成本与长期成本价值** | cost 与 reward 必须分开；cost 估不准 = 假安全 |
| $b$ | 标量 | 设计 | 固定 | cost 阈值（near 0） | 阈值越接近 0，纯 Lagrangian 越易崩 |
| $\lambda_p$ | 标量 ≥0 | 对偶上升 | 由约束违反更新 | Lagrangian 乘子 | 是对偶变量，不是网络权重；易震荡 |
| $\mu,\sigma$ | 动作分布参数 | CEM 迭代 | 计算 | Constrained CEM 采样分布 | 规划期内迭代刷新 |
| $P_\phi(\cdot\mid s,a)$ | world model | WM 训练 | learned | 想象动力学 | model bias 累积影响 cost 估计 |

### 2.2 从 CMDP 到 Lagrangian：为什么 near-zero 阈值会崩

**CMDP**（Eq 1）$\;M=(S,A,P,R,C,\mu,\gamma)$，回报与成本回报

$$
J^R(\pi)=\mathbb E\Big[\sum_t\gamma^t R(s_{t+1}\mid s_t,a_t)\Big],\quad
J^C_i(\pi)=\mathbb E\Big[\sum_t\gamma^t C_i(s_{t+1}\mid s_t,a_t)\Big],
$$
目标 $\pi^\star=\arg\max_{\pi\in\Pi_C}J^R(\pi)$，可行集 $\Pi_C=\{\pi: J^C_i(\pi)\le b_i\}$。

**Lagrangian 松弛**把约束问题转成无约束 min-max：

$$
\min_{\lambda\ge0}\max_{\theta}\ \mathcal L(\theta,\lambda)=J^R(\pi_\theta)-\lambda\big(J^C(\pi_\theta)-b\big).
$$

内层对策略 $\theta$ 上升、外层对乘子 $\lambda$ 做**对偶上升**：$\lambda\leftarrow[\lambda+\eta(J^C(\pi_\theta)-b)]_+$。

**为什么 near-zero b 崩（关键洞见）**：当 $b\to0$，任何微小违约都推高 $\lambda$，$\lambda$ 一大策略立刻变得过度保守完不成任务、$J^C$ 降回 0 又让 $\lambda$ 回落——两个时间尺度耦合产生**震荡**，且 model-free 的 $J^C$ 估计噪声大，乘子更难收敛。这就是"罚款调节"在零容忍下失稳的数学根源。

### 2.3 world model 怎么救：把"反应式罚款"换成"前瞻式规划 + 长期安全 critic"

**Safe model-based RL（Eq 2-4）**：用 world model $P_\phi$ rollout 想象轨迹来估 $J^R_\phi,J^C_\phi$：

$$
\max_{\pi_\theta}J^R_\phi(\pi_\theta)\ \ \text{s.t.}\ \ J^C_\phi(\pi_\theta)\le b.
$$

在 DreamerV3 上**新增 cost decoder $\hat c_t$ 与 cost critic $\hat v_{c_t}$**，并用 TD(λ) 同时估 reward return 与 **cost return**（Fig 2）。两种用法：

- **OSRP（在线安全规划，Algorithm 1）= world model 内的 MPC**：在每个决策时刻，用 **Constrained CEM** 从当前 $s_t$ 采 $N$ 条轨迹、在 WM 内 rollout、用 reward/cost 模型 + critic 评估，**筛掉 cost-return > b 的轨迹**，在安全集里选回报最高的动作执行。cost critic 接住 horizon 之外的长期成本，解决纯 MPC 的短视。
- **OSRP-Lag**：当没有完全安全的轨迹时，用 $\lambda_p$ 在线平衡 reward 与 cost（规划目标 $=$ reward $-\lambda_p\cdot$ cost）。
- **BSRP-Lag（背景安全规划）**：不在线规划，而是在 imagination 里用 Lagrangian 更新一个**安全 actor**（类似 Dreamer 的背景策略学习 + cost 约束）。

**Constrained CEM**：标准 CEM 用 elite 轨迹更新采样分布 $\mu,\sigma$；约束版在选 elite 时先要求 cost ≤ b（可行性优先），再按 reward 排序。

### 2.4 概念边界与符号陷阱
- **online vs background planning**：OSRP 在每步决策时规划动作（推理期 MPC，慢但安全可控）；BSRP 在训练期用规划更新 actor（部署时只跑 actor，快）。WMTS 选型取决于推理预算。
- **cost 必须独立于 reward**：把安全混进 reward（shaped penalty）会重蹈 reward hacking；SafeDreamer 显式分离 cost 通道。
- $\lambda_p$ 是对偶变量（由约束违反驱动），不是网络权重。
- WM cost 估不准 = **假安全**：规划以为安全实则危险——这是 model-based safety 的根本风险（model bias 直接威胁安全，而非仅性能）。

### 2.5 信息流/算法机制（无代码）
观测 → encoder → $s_t$ → 在 WM 内 rollout 候选动作轨迹 → 每个 latent 预测 $\hat r,\hat c,\hat v_r,\hat v_c$ → TD(λ) 估 reward/cost return → (OSRP) Constrained CEM 选安全高回报动作执行 / (BSRP-Lag) Lagrangian 更新安全 actor → 真机交互入 replay → 更新 WM 与 critics。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
**Safety-Gymnasium** 基准，同时覆盖**低维状态输入与纯视觉输入**；对比 model-free（PPO-Lag/TRPO-Lag/CPO）与 model-based（LAMBDA、Safe SLAC、MBPPO-Lag、DreamerV3）安全 RL。

### 3.2 关键结果与因果解释
- **近零成本（near-zero-cost）**：SafeDreamer 在低维与纯视觉任务上都达到近零 cost 同时保持高 reward；纯 Lagrangian model-free 在 $b\to0$ 时做不到（§2.2 的震荡）。
- **能力覆盖（Table 1）**：唯一同时支持 Vision + Low-dim + Lagrangian + Online + Background 的方法。**因果**：online planning 提供前瞻避险，cost critic 提供长期安全，Lagrangian 在无完全安全轨迹时兜底——三者缺一都会在某类任务上掉到非零成本。
- **vision-only**：DreamerV3 的稳定 latent 让 cost 预测在像素输入下也可用，这是 LAMBDA(DreamerV1) 做不稳的地方。

### 3.3 Ablation / 对照因果链
- `去 cost critic（纯 OSRP MPC）→ 只看有限 horizon 成本 → 远期危险被忽略 → 长程任务成本回升`：印证 cost critic 接长期安全的作用。
- `去 online planning（纯 Lagrangian/BSRP）→ 反应式、无前瞻 → near-zero 阈值下震荡/违约`。
- `把 cost 并进 reward（不分离）→ reward hacking 风险 + 无法独立设阈值`。

### 3.4 工程约束与实验边界
- OSRP 在线规划每步要在 WM 内跑 CEM → 推理开销大（部署慢）；BSRP 部署快但训练更复杂。
- 安全完全依赖 WM 的 cost 预测准确性：WM 在分布外的乐观会造成"假安全"。
- 需要可定义的 cost 函数与阈值 b。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**把安全从 reward 里拆成独立 cost 通道，用 world model 的"前瞻规划 + 长期 cost critic"取代纯 Lagrangian 的"反应式罚款"**，从而在零容忍阈值下既安全又能完成任务。Lagrangian 退化为"无完全安全轨迹时的兜底"，而非唯一安全机制。

### 4.2 为什么这个设计有效
(1) WM 样本效率让 cost 动力学可被少量数据学到；(2) online planning 的 lookahead 在动作执行前就排除危险轨迹；(3) cost critic 把 horizon 外的长期成本接进规划，克服 MPC 短视；(4) DreamerV3 的稳定性让其在视觉输入也成立。

### 4.3 什么时候会失效
- WM cost 预测在 OOD 处过度乐观 → 假安全（最危险的失败模式）。
- 瞬时、不可预测的危险（前瞻无用）。
- cost 函数难以定义（如灵巧手"安全"的量化）。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
SafeDreamer 用软约束（Lagrangian）+ 经验规划，**没有硬安全保证**（不像 CBF/可达性给出形式化不变集）。安全性等价于 WM cost 估计的准确性——是统计保证而非控制论证书。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 SafeDreamer 关系 |
|---|---|---|---|
| PPO-Lag/CPO | 简单、model-free | near-zero 失稳、低维 | SafeDreamer 的对照与兜底成分 |
| MPC/CBF | 在线安全、可给证书 | 需模型/短视/无长期 | OSRP = WM 内 MPC；cost critic 补长期 |
| LAMBDA/Safe SLAC | 视觉 WM 安全 | DreamerV1 不稳、无 online planning | SafeDreamer 用 DreamerV3 + 双规划改进 |

### 5.3 工程/实验维度
在线规划开销、cost 函数设计、WM 在 OOD 的乐观、Lagrangian 乘子调参是主要工程点。

## 6. 对用户研究的启发（未来与结合：WMTS safety filter）

### 6.1 对 WMTS / 灵巧手 / Sim-to-Real 的迁移

| WMTS 模块 | SafeDreamer 对应 | 迁移设计 |
|---|---|---|
| **Safety Filter** | OSRP：在 WM 内对候选 action chunk 按预测 cost ≤ b 过滤 | 用 ensemble WM 预测 chunk 的 contact-force/saturation/drop cost，筛掉超限 chunk 再交 PPO/DP 执行 |
| **Reliability head** | cost critic（长期成本价值） | reliability head ≈ 学一个"长期不安全/不可靠"价值，对应 WMTS_Reliability_Extensions 的 LCB |
| Oracle/Generalist 约束 | OSRP-Lag / BSRP-Lag | 对 PPO Oracle 加 cost 约束（PPO-Lag），或在 imagination 里更新安全 actor |
| 任务调度 | cost-aware 轨迹选择 | scheduler 选任务时把"预测成本/可行性"作为约束（Solve/Probe/Reject 三队列） |

**灵巧手上的关键设计（critical thinking）**：SafeDreamer 的"安全"在 Safety-Gymnasium 是几何避障 cost；迁到灵巧手要把 cost 定义为**接触力超限 / 执行器力矩饱和 / 掉物 / 热超限**等物理成本，且 ensemble WM 必须给出**带不确定性**的 cost 预测（用 LCB / disagreement 防"假安全"）。这正是 WMTS 用 ensemble（而非单一 WM）的理由。

### 6.2 可验证实验建议
- 在手内重定向上实现 OSRP：ensemble WM 预测每个 DP/PPO chunk 的 contact-force cost return，过滤 > b 的 chunk，比较"无过滤 / OSRP 过滤 / OSRP-Lag" 的违约率与成功率。
- 验证"假安全"风险：在 OOD 物体/摩擦下，测单 WM vs ensemble-LCB cost 预测的过度乐观程度与真实违约率。
- cost critic vs 纯有限 horizon cost：测长程任务里远期违约是否被 cost critic 抑制。

### 6.3 不应过度外推的点
- SafeDreamer 给的是软约束统计安全，**不是硬证书**；灵巧手高风险动作仍需底层限幅/CBF 兜底。
- "near-zero cost" 依赖 WM cost 估计准；接触动力学难学准时安全性打折。
- cost 必须独立定义，不能塞进 reward。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
CMDP + 约束 RL；Lagrangian 把约束转 min-max（§2.2），对偶上升更新乘子。是 PPO-Lag/CPO 一脉在 world-model 上的统一与改进。

### 与 [[Optimization]] 的联系
核心是拉格朗日对偶 + 对偶上升（PID-Lagrangian，[[Optimization#2.2 拉格朗日对偶：把约束"价格化"]]），以及 Constrained CEM（带可行性约束的进化采样）——约束优化与对偶方法的直接应用。

### 与 [[ControlTheory]] 的联系
OSRP = world model 内的 receding-horizon MPC；cost 约束 + 安全集思想与 CBF/可达性安全过滤呼应，但 SafeDreamer 是学习式软约束、无形式化不变集证书。cost critic 把长期安全接进规划，是"价值即 Lyapunov"（[[ControlTheory#10.4 被动性与"价值即 Lyapunov"]]）的安全版实例。

### 与 [[StochasticProcess]] 的联系
DreamerV3 离散 latent + CEM 在动作分布上采样轨迹，用 TD(λ) 估 reward/cost return。

### 与 [[WorldModels]] 的联系
OSRP 是 [[WorldModels#6.1 世界模型作安全调度器（Look-ahead Safety Filter）]] 的最贴近实现；但单 WM 的 cost 预测在 OOD 会"假安全"（[[WorldModels#6.2 Dream RL 的对抗性风险]]），WMTS 必须用 ensemble（[[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]]）给 cost 带上不确定性。

### 与 [[Final_WMTS]] 的联系
WMTS safety filter 的直接模板：OSRP 过滤 action chunk、cost critic 充当 reliability head、OSRP-Lag/BSRP-Lag 对应 Oracle/Generalist 的安全约束；同为 PKU 工作，迁移成本低。

## References
- 原始 PDF：[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL.pdf]]
- 理论基础（共享）：[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]（RSSM/TD(λ)）、DreamerV3
- 相关：CPO / PPO-Lag / TRPO-Lag、LAMBDA、Safe SLAC、Constrained CEM
- 项目入口：[[Final_WMTS]]、WMTS_Reliability_Extensions
- 簇内关系（Delta）：
  - vs [[DiWA- Diffusion Policy Adaptation with World Models|DiWA]] / [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]：三者都在 world model 想象里跑 RL，但 DiWA/World4RL 只优化回报（精炼 DP）；SafeDreamer 多一路 cost 通道 + Lagrangian，把"安全"做成独立约束——WMTS 精炼步（DiWA/World4RL）叠上 SafeDreamer 的 OSRP 才是完整"精炼 + 安全过滤"。
  - vs [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos|DexWM]]：都用 WM 做前瞻规划（CEM/MPC），SafeDreamer 规划目标含 cost 约束，DexWM 只 goal-conditioned latent cost。
