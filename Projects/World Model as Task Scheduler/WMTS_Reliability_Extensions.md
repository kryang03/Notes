---
tags:
  - WMTS
  - research-idea
  - world-model
  - sim-to-real
  - dexterous-manipulation
aliases:
  - WMTS Reliability Extensions
  - Pessimistic Contact-Actuation Scheduler
date: 2026-04-26
related:
  - "[[Final_WMTS]]"
  - "[[Deep Dynamics Models Recap]]"
  - "[[DiWA- Diffusion Policy Adaptation with World Models Recap]]"
  - "[[ANYmal Parkour Recap]]"
  - "[[Diffusion Policy Recap]]"
  - "[[CMA-ES Tutorial Recap]]"
  - "[[GenDexGrasp - Generalizable Dexterous Grasping]]"
  - "[[Learning Quadrupedal Locomotion over Challenging Terrain]]"
  - "[[SafeDreamer Recap]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# WMTS Reliability Extensions: Pessimistic Contact-Actuation Scheduler

> [!abstract] 核心想法
> 在不改变 [[Final_WMTS]] 五模块主架构的前提下，新增一个“可靠性增强层”：让 Scheduler 不只寻找通才失败任务，而是同时评估 **dynamics epistemic uncertainty、actuator feasibility、contact topology feasibility** 三类风险，用保守但信息量高的任务队列推动真机闭环。

---

## 0. 与当前架构的关系

当前 [[Final_WMTS]] 已有五模块：隐空间任务生成器、Oracle、Generalist Diffusion Policy、Ensemble WM、真机微调与安全闭环。本方案不替换任何模块，只给每个模块增加一个可插拔的 reliability head：

| 原模块 | 新增可靠性头 | 作用 |
|---|---|---|
| §一 Latent Task Generator | Risk-aware Task Queue | CMA-ES 只提出候选，可靠性头负责排序和分流 |
| §二 Oracle Specialist | Privileged-Observable Consistency | 将特权接触/摩擦知识压缩为真机可观测 latent |
| §三 Generalist Diffusion | Actuation-aware Conditioning | 让 diffusion action chunk 感知执行器可行性 |
| §四 Ensemble WM | Contact-Actuation Decomposition | 明确拆分 contact topology 与 actuator gap |
| §五 Safety Filter | Pessimistic Look-ahead Certificate | 用下置信界而非均值成功率放行真机动作 |

---

## 1. 核心方案：三重不确定性的保守任务调度

### 1.1 三类风险量

**1. Dynamics epistemic uncertainty**（来自 [[Deep Dynamics Models Recap|PDDM]]）：

$$
U_{dyn}(\xi)=\sum_{t=1}^{H}\mathrm{tr}\,\mathrm{Cov}\left(\{\hat{s}_{t}^{m}\}_{m=1}^{M}\right)
$$

反映世界模型是否理解该任务区域。

**2. Actuator feasibility**（来自 [[ANYmal Parkour Recap|Actuator Network]] 与 [[Final_WMTS#4.A Actuator Model：指令 → 关节力矩|WMTS Actuator Model]]）：

$$
\rho_{act,t}=\frac{\|\hat{\tau}_{link,t}\|_2}{\|\tau_{cmd,t}\|_2+\epsilon},\quad U_{act,t}=\mathrm{tr}\,\mathrm{Cov}\left(\{f_{act}^{m}(x_{act,t})\}_{m=1}^{M_a}\right).
$$

$\rho_{act}\ll 1$ 表示命令无法落地，常见原因包括反电动势、电机热衰减、丝杠静摩擦或连杆弹性吸收。

**3. Contact topology feasibility**（来自 [[GenDexGrasp - Generalizable Dexterous Grasping|GenDexGrasp]] 与触觉预测）：

将任务 latent 拆成运动与接触两部分：

$$
z_{task}=[z_{motion},z_{contact}],\quad \hat{\Omega}_{1:H}=D_{contact}(z_{contact},o_{shape}).
$$

用预测触觉 latent 与目标接触图一致性评估任务是否有合理接触路径：

$$
C_{contact}(\xi)=\sum_{t=1}^{H}\|E_{tactile}(\hat{x}_{tactile,t})-E_{contact}(\hat{\Omega}_t)\|_2^2.
$$

### 1.2 任务排序目标

CMA-ES 仍在 CVAE 隐空间提出候选 $\xi$，但最终不是按“新奇/困难”直接执行，而是按 risk-aware score 分流：

$$
\mathcal{S}(\xi)=\underbrace{\alpha I_{gain}(\xi)}_{\text{值得探索}}+\underbrace{\beta B_{edge}(\xi)}_{\text{能力边界}}-\lambda_d U_{dyn}(\xi)-\lambda_a U_{act}(\xi)-\lambda_c C_{contact}(\xi)-\lambda_j J_{jerk}(\xi).
$$

其中：

- $I_{gain}$：预计能降低 WM 认知不确定性的价值；
- $B_{edge}$：通才“没掉但跟得吃力”的能力边界分数；
- $J_{jerk}$：任务轨迹高频性，防止 Scheduler 生成 actuator 不可执行的尖锐轨迹。

> [!tip] 关键区别
> 传统 curriculum 追求“更难”；本方案追求“更有信息、但可控”。这比单纯最大化 ensemble disagreement 更适合真机。

---

## 2. 模块级实现细节

### 2.1 Latent Task Generator：双队列而非单队列

候选任务分三类：

| 队列 | 条件 | 去向 |
|---|---|---|
| Solve Queue | $U_{dyn}$ 中等、$\rho_{act}$ 高、$C_{contact}$ 低 | Oracle 训练 + Generalist 蒸馏 |
| Probe Queue | $U_{dyn}$ 高但 actuator/contact 风险低 | 仿真/低速真机探测，用于补 WM 数据 |
| Reject Queue | actuator 或 contact 风险高 | 不执行；作为生成器负样本训练 |

这直接修复 [[Final_WMTS#一、 仿真隐空间任务生成器 (Latent Task Generator)|当前任务生成器]] 的一个隐患：CMA-ES 可能偏好“世界模型不懂但硬件做不到”的任务。

### 2.2 Oracle-Generalist：特权到可观测的一致性蒸馏

借鉴 [[Learning Quadrupedal Locomotion over Challenging Terrain|privileged teacher-student]]：Oracle 不只输出动作，还输出中间 latent：

$$
z_{priv}=E_{priv}(F_{contact},\mu_{fric},m,I_{obj}),\quad z_{obs}=E_{obs}(\phi_{t-H:t},\dot{\phi}_{t-H:t},x_{tactile,t-H:t}).
$$

新增一致性损失：

$$
\mathcal{L}_{align}=\|\mathrm{sg}(z_{priv})-z_{obs}\|_2^2+\mathcal{L}_{NTXent}(z_{priv},z_{obs}).
$$

这让 Generalist 从真机可得历史中恢复“接触/摩擦隐变量”，不是只做动作 BC。

### 2.3 Diffusion Generalist：执行器可行性条件化

扩散策略条件从

$$
c_t=[O_{real,t},C_{local,t}]
$$

扩展为：

$$
c_t=[z_{prop},z_{tactile},z_{task},z_{act},z_{contact}],
$$

其中：

$$
z_{act}=E_{act}(a_{t-H:t},\phi_{t-H:t},\dot{\phi}_{t-H:t},T_t,\tau_{fb,t-H:t}).
$$

训练时加入 actuator-aware denoising loss：

$$
\mathcal{L}_{diff}^{act}=\|\epsilon-\epsilon_\theta(A_k,k,c_t)\|_2^2+\lambda_{sat}\sum_t\max(0,\|\hat{\tau}_{link,t}\|-\tau_{max}(\dot{\phi}_t,T_t))^2.
$$

这把 [[Diffusion Policy Recap|Diffusion Policy]] 的多模态动作优势与 [[ANYmal Parkour Recap|Actuator Network]] 的可执行性约束连起来。

### 2.4 Ensemble WM：Actuator-Rigid counterfactual loss

为了避免 Actuator Model 和 Rigid Dynamic Model 相互“背锅”，加入 counterfactual consistency：如果两条不同命令历史产生近似相同 $\hat{\tau}_{link}$，Rigid Dynamic Model 预测应一致。

$$
\|\hat{\tau}_{link}^{(i)}-\hat{\tau}_{link}^{(j)}\|<\delta \Rightarrow \|f_{dyn}(s,\hat{\tau}_{link}^{(i)})-f_{dyn}(s,\hat{\tau}_{link}^{(j)})\|<\epsilon.
$$

损失为：

$$
\mathcal{L}_{cf}=\sum_{i,j}w_{ij}\|f_{dyn}(s,\hat{\tau}_{link}^{(i)})-f_{dyn}(s,\hat{\tau}_{link}^{(j)})\|_2^2,
$$

$$
w_{ij}=\exp(-\|\hat{\tau}_{link}^{(i)}-\hat{\tau}_{link}^{(j)}\|_2^2/\sigma^2).
$$

### 2.5 Safety Filter：下置信界放行

真机放行不看平均成功率，而看 pessimistic lower confidence bound：

$$
\mathrm{LCB}_{succ}=\mathbb{E}_{m}[P_{succ}^{m}]-\kappa\sqrt{\mathrm{Var}_{m}(P_{succ}^{m})}-\lambda_aU_{act}-\lambda_cC_{contact}.
$$

动作块放行条件：

$$
\mathrm{LCB}_{succ}>\eta_{safe},\quad \rho_{act}>\eta_{act},\quad \max_t T_{motor,t}<T_{limit}.
$$

这对应 [[SafeDreamer Recap|SafeDreamer]] 的安全约束思想，但更加贴合灵巧手执行器与接触风险。

---

## 3. 预计实现优先级

### Stage A：离线验证（不碰真机）

1. 从现有仿真 rollout 训练 $E_{obs}$、$E_{priv}$ 和 contact feasibility head。
2. 用已有 Oracle 轨迹估计 $C_{contact}$ 是否能预测失败/掉落。
3. 将 Risk-aware score 与原始 CMA-ES fitness 对比，看候选任务是否更可执行。

### Stage B：仿真闭环

1. Solve/Probe/Reject 三队列替换单一任务池。
2. 在 Probe Queue 中主动采集 WM 高不确定但硬件可行的样本。
3. 检查 Generalist 成功率与 WM 校准误差是否同步改善。

### Stage C：低速真机闭环

1. 限制任务速度与动作幅度，只验证 Actuator feasibility LCB。
2. 用短 horizon action chunk 做安全放行。
3. 记录 Reject Queue 中被安全层拦截但仿真认为可行的任务，作为 sim-to-real gap 诊断集。

---

## 4. 关键消融实验

| 实验 | 对照 | 预期结论 |
|---|---|---|
| Risk-aware score vs 原始 CMA-ES score | 任务成功率、掉落率、WM 校准误差 | 三重风险项应降低“高新奇但不可执行”的任务比例 |
| 去掉 $U_{act}$ | 电机温度升高/高速任务下成功率 | actuator feasibility 是高动态失败的核心预测因子 |
| 去掉 $C_{contact}$ | 薄接触/换指任务成功率 | 接触拓扑约束能减少几何可达但力学不可行的任务 |
| 去掉 $\mathcal{L}_{align}$ | 真机只观测策略泛化 | privileged-observable alignment 能提升 sim-to-real latent 可迁移性 |
| Mean success vs LCB success | 真机安全拦截误报/漏报 | LCB 应减少危险 false positive |

---

## 5. 为什么这个方案足够值得做

1. **不是单点 trick**：它把 [[Deep Dynamics Models Recap|PDDM]] 的 ensemble uncertainty、[[ANYmal Parkour Recap|Actuator Network]]、[[GenDexGrasp - Generalizable Dexterous Grasping|contact map]]、[[Diffusion Policy Recap|Diffusion Policy]] 与 [[SafeDreamer Recap|safe dream]] 统一成一个可实验验证的调度层。
2. **服务真机可靠性**：它把“任务新奇性”从单一目标降级为多目标之一，避免 WMTS 变成会主动寻找硬件不可执行任务的系统。
3. **有清晰论文叙事**：核心 story 是 **World Model should schedule not only by novelty, but by calibrated feasibility under contact and actuation constraints**。
4. **可渐进落地**：Stage A 完全离线，Stage B 仿真闭环，Stage C 才低速真机，不要求一次性推翻当前实现。
