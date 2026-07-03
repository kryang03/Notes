---
tags:
  - paper
  - reinforcement-learning
  - long-horizon
  - curriculum-learning
  - non-prehensile
  - dexterous-manipulation
aliases:
  - Privileged Action
  - Long-Horizon Manipulation
paper-year: 2025
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/Learning_Long-Horizon_Robot_Manipulation_Skills_via Privileged Action.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
  - "[[EmbodiedAI]]"
---

# Learning Long-Horizon Robot Manipulation Skills via Privileged Action

> [!abstract] 核心贡献
> 本文提出 privileged action：在仿真训练中临时允许真实世界不可部署的动作/物理干预，例如 robot-table collision relaxation 与 gated virtual force on object，再通过三阶段 curriculum 逐步移除这些 privilege，使策略能在没有额外非抓取奖励或 reference trajectory 的情况下发现 push-and-grasp、pivot grasp 和 thin-object dexterous grasping 等长 horizon contact-rich 行为。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 这是 curriculum RL 的一种 action-space relaxation：先扩大可探索 state-action set，再逐步收紧到真实 MDP。
> - [[ContactMechanics]] — 接触边界把可行探索区域切得很薄；collision relaxation 和 virtual force 通过改变接触约束与对象受力通道来降低探索难度。
> - [[Optimization]] — curriculum 相当于 continuation method：先解松弛问题，再沿着约束收紧路径追踪到真实问题。
> - [[EmbodiedAI]] — 与 privileged information 不同，本文的特权发生在 action / dynamics interface，而不是 observation。
>
> **核心技术**: Privileged Action, Constraint Relaxation, Virtual Force, Auto-Curriculum, Non-Prehensile Manipulation, Long-Horizon RL

## 0. 阅读定位与范本价值

这篇论文的价值不在于某个复杂网络结构，而在于它提出了一个很适合思考灵巧操作探索难题的视角：**有些 contact-rich long-horizon skill 学不出来，不是策略表达力不够，而是早期探索几乎碰不到能产生后续高奖励的状态。**

它的解决方式是训练时“临时改变动作和物理约束”：

1. 第一阶段放松 robot-table collision，让机械臂能先学会接近和抓取结构。
2. 第二阶段给物体一个 gated virtual force action channel，让策略更容易发现“要让物体动起来”的交互。
3. 第三阶段移除 privileged action，在真实物理约束下继续训练。

注意：这不是部署时作弊。Privileged actions 是训练脚手架；最终策略必须在 normal setting 下工作。

最低标准对齐：

| 四支柱 | 本文必须回答的问题 |
|--------|--------------------|
| 逻辑与价值 | 为什么普通 PPO 会卡在 end-effector 靠近物体的局部最优？privileged action 比 dense reward / demo / skill chaining 多了什么？ |
| 原理与理论 | collision relaxation 如何改变 contact complementarity？virtual force 如何通过 $B(x_t)$ gating 接入对象动力学？curriculum 参数如何收紧？ |
| 实验与验证 | Push-and-Grasp / Pivot Grasp 的 reward 差距、YCB thin objects、stage ablation 和 real-world qualitative transfer 是否支撑主张？ |
| 未来与结合 | 对转笔/WMTS，哪些 privileged actions 可以作为探索脚手架，哪些会诱导不可迁移 cheat？如何与 tactile/contact reward 结合？ |

## 1. 问题设定与动机

### 1.1 一句话核心

Privileged Action 的核心是：在仿真训练早期临时放宽接触约束或给物体额外受力通道，让策略先发现长 horizon 操作链条，再通过 curriculum 把这些不真实的动作权限逐步收回。

### 1.2 直观隐喻

它像训练体操时的吊带和软垫：初学者先在辅助设备下学会动作顺序和身体协调，然后逐步减少辅助。关键不是让比赛时还吊着绳子，而是让学习者先进入“做出整套动作”的状态分布，否则永远卡在起跳前。

这个隐喻可被 falsify：如果辅助太强且收不回来，最终策略只会在 privileged environment 中成功；如果辅助刚好，它应该在 privilege 被移除后仍能保留可行的真实行为。

### 1.3 现有方法的局限

| 方法 | 注入了什么 | 局限 |
|------|------------|------|
| Vanilla PPO | 从 reward 自主探索 | long horizon + contact boundary 让高奖励区域几乎不可达，容易卡在局部最优 |
| Dense reward shaping | 人工中间目标 | 每个任务都要设计，可能改变 reward landscape |
| Reference trajectory / demonstration | 给出成功路径 | 数据采集贵，且 human behavior 未必适合机器人 |
| Skill decomposition / chaining | 手工子任务结构 | 需要人工指定 primitive 和 transition |
| Privileged information | 给训练策略更多状态信息 | 只改善 state-action mapping，不一定帮助发现新的 contact behavior |
| Privileged action | 训练时改变可行动作/物理约束 | 需要设计 privilege 和 curriculum，且有不可迁移风险 |

本文的 Delta：**不告诉策略“应该怎么推/转/抓”，而是临时放宽物理交互，使策略自己能探索到推、pivot、抓这些行为。**

### 1.4 论文贡献

1. 提出 privileged actions：真实世界不可执行，但仿真中可用于降低探索难度的动作/约束修改。
2. 设计三阶段 curriculum：constraint relaxation → virtual force → normal setting。
3. 使用同一默认 grasp/lift reward，不加入专门的 non-prehensile reward，也不使用 reference trajectory。
4. 在 Franka push-and-grasp、constrained pivot grasp、Kuka+AllegroHand grasp/reorientation YCB thin objects 上展示行为涌现。
5. 用真实 Franka 实验展示 learned behavior 的物理可行性，但真机部分主要是 trajectory transfer/replication，不是大规模闭环统计评测。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $q_{R,t},q_{O,t}$ | robot/object positions | simulator state | 输入 | 机器人与物体位置 | object pose 在真机可能因遮挡难获得 |
| $\dot q_{R,t},\dot q_{O,t}$ | robot/object velocities | simulator state | 输入 | 速度状态 | 真实部署不一定可靠观测 |
| $x_t=[q_R,q_O,\dot q_R,\dot q_O]$ | state | IsaacGym | 输入 | policy observation / dynamics state | 不是纯视觉 setting |
| $u_{R,t}$ | robot control | policy output | policy 参数带梯度 | 真实可部署控制 |
| $u_{O,t}$ | object force control | privileged policy output | policy 参数带梯度，部署移除 | 直接对物体施加 virtual force | 真实世界不可执行 |
| $f(x_t)$ | passive dynamics | simulator | 否 | inertia/contact/external passive effects | 包括 contact forces |
| $g(x_t)$ | control influence | simulator dynamics | 否 | action 如何影响状态 | privileged stage 改写 $g$ |
| $B(x_t)$ | gating matrix | hand-designed | 否 | 决定 $u_O$ 何时能作用到 object | 只有末端与物体位置/速度接近时才启用 |
| $\phi_R(x_t)$ | signed distance robot/table | simulator contact geometry | 否 | robot-table contact constraint | Stage 1 修改这个距离约束 |
| $F_{R,t},F_{O,t}$ | normal/contact forces | physics solver | 否 | robot/object contact forces | 不由 policy 直接控制 |
| $\Delta_R$ | virtual table offset | curriculum parameter | 否 | robot-table collision relaxation | 初始 30cm below actual surface，逐步抬高到 0 |
| $\delta_p,\delta_v$ | position/velocity thresholds | hyperparameters | 否 | virtual force gating threshold | 初始 $\delta_p=10,\delta_v=5$ |
| $\alpha$ | curriculum factor | auto-curriculum | 否 | 缩小 virtual force activation region | 初始 0.85，成功后乘 0.9，最低 0.06 |
| $r_{total}$ | reward | IsaacGym default grasp/lift reward | 否 | 训练目标 | 没有额外 non-prehensile reward，但不是纯 sparse reward |

### 2.2 普通 tabletop manipulation MDP

状态：

$$
x_t=[q_{R,t},q_{O,t},\dot q_{R,t},\dot q_{O,t}].
$$

目标：

$$
J(\theta)
=
\mathbb{E}_{x_0\sim p_0,u_t\sim\pi_\theta(\cdot\mid x_t)}
\left[
\sum_{t=0}^{\infty}\gamma^t r(x_t,u_t)
\right].
$$

系统更新写成：

$$
x_{t+1}
=
x_t+
\left[f(x_t)+g(x_t)u_t\right]\Delta t.
$$

普通真实设置中，policy 只能控制 robot：

$$
u_t=u_{R,t}.
$$

对象状态只能通过接触力间接改变。对于 non-graspable pose，这造成探索困境：策略必须先学会推/转物体，才能进入能抓取和 lift 的状态；但 reward 主要在接近、抓取、lift/goal 处显著，早期随机探索很难发现这条长链。

### 2.3 Stage 1: constraint relaxation

第一阶段不是禁用 hand-object collision，而是放松 robot-table collision。原始接触互补条件可写成：

$$
F_{R,t}\ge0,\qquad
\phi_R(x_t)\ge0,\qquad
\phi_R(x_t)F_{R,t}=0.
$$

论文把 table contact 触发距离改成：

$$
F_{R,t}\ge0,\qquad
\phi_R(x_t)+\Delta_R\ge0,\qquad
\left(\phi_R(x_t)+\Delta_R\right)F_{R,t}=0.
$$

如果 $\Delta_R>0$，等价于真实桌面下方还有一个 virtual table / relaxed collision boundary，使 robot 在早期可以“穿过”实际桌面附近的区域，先学会接近和抓取结构。

但作者也指出风险：过度 relaxation 会让策略学到错误行为，例如用机械臂而非 gripper 抬物体。因此他们引入 grey virtual table 并逐步抬高，直到与真实桌面对齐。

curriculum：

$$
\Delta_R:0.3\text{ m}\rightarrow0,
$$

每当 success rate > 70%，就：

$$
\Delta_R\leftarrow\Delta_R-0.1.
$$

### 2.4 Stage 2: virtual force

当桌面碰撞恢复后，策略仍很难学会“通过接触让物体动”。因此 Stage 2 扩展 action：

$$
u_t=[u_{R,t},u_{O,t}],
$$

其中 $u_{O,t}$ 是直接施加在 object 上的 virtual force。此时 control influence 变为：

$$
g(x_t)=
\begin{bmatrix}
0\\
M(q)^{-1}
\begin{bmatrix}
I_{n_v\times m_R} & 0\\
0 & B(x_t)
\end{bmatrix}
\end{bmatrix}.
$$

$B(x_t)$ 是 gating matrix：

$$
B(x_t)=
\begin{cases}
I_{n_{v_O}\times m_O},
& \text{if } q_{O,t}-q_{EE,t}<\delta_p\alpha
\ \land\
\dot q_{O,t}-\dot q_{EE,t}<\delta_v\alpha,\\
0,
& \text{otherwise}.
\end{cases}
$$

解释：

- virtual force 不是任意时候都能推物体。
- 只有 end-effector 与 object 在位置和速度上足够接近时，$u_O$ 才起作用。
- 这防止 policy 在远处“念力移动物体”，迫使 robot movement 逐步替代 virtual force。

原文设置：

$$
\delta_p=10,\qquad \delta_v=5,\qquad \alpha=0.85.
$$

成功后：

$$
\alpha\leftarrow\operatorname{clamp}(\alpha\cdot0.9,0.06,0.85).
$$

随着 $\alpha$ 降低，virtual force 的激活条件更严格，privilege 逐渐收回。virtual force 只限制在 $x,y$ 方向，而不是旧稿里写的竖直抗重力。

### 2.5 Stage 3: normal setting

当 $\Delta_R=0$ 且 $\alpha$ 降到 $\alpha_{\min}=0.06$ 后，训练进入无 privileged action 的 normal setting。最终策略不应依赖 table penetration 或 object virtual force。

三阶段算法：

| 阶段 | 条件 | 训练环境 | 成功后更新 |
|------|------|----------|------------|
| Stage 1 | $\Delta_R>0$ | robot-table collision relaxed | $\Delta_R\leftarrow\Delta_R-0.1$ |
| Stage 2 | $\alpha>\alpha_{\min}$ | virtual force gated by $B(x_t)$ | $\alpha\leftarrow\max(0.9\alpha,\alpha_{\min})$ |
| Stage 3 | otherwise | no privileged actions | normal RL training |

### 2.6 Reward 设置

论文强调没有为 non-prehensile manipulation 设计额外 reward，但它不是纯 sparse terminal reward。它使用 IsaacGym 默认 grasp/lift reward：

$$
r_{total}=r_f+r_l+r_k+r_p+r_b.
$$

其中：

- $r_f$：end-effector 到 object 的距离 reward。
- $r_l$：lifting reward。
- $r_k$：object 到 goal 的距离 reward。
- $r_p$：jerk penalty。
- $r_b$：success bonus。

关键点：这些 reward 鼓励接近、lift 和到达目标，但**没有显式奖励“推到桌边”“pivot grasp”“重定向 scissors”**。非抓取行为是为了达成最终 grasp/lift reward 而涌现。

## 3. 训练、数据与实验

### 3.1 任务设置

| Task | Robot | Object / challenge | Desired emergent behavior |
|------|-------|--------------------|--------------------------|
| Push-and-Grasp | Franka + gripper | 15cm × 10cm × 6cm object，gripper max opening 8cm，平放不可直接抓 | 推到桌边，从侧面抓取并 lift |
| Pivot Grasp | Franka + gripper，桌边有小墙阻止直接推到边缘 | 原 push-and-grasp 策略被墙挡住 | 利用 robot base/support 做 pivot grasp |
| Thin-object dexterous grasp | Kuka + AllegroHand | YCB scissors, stapler, wrench | 先 maneuver 到边缘，再抓取/重定向 |

所有任务在 IsaacGym 中训练。

### 3.2 Franka push-and-grasp / pivot grasp

| Task | Our method | PPO |
|------|------------|-----|
| Push and Grasp | $(2.34\pm0.13)\times10^4$ | $65\pm10$ |
| Pivot Grasp | $(2.17\pm0.29)\times10^4$ | $52\pm17$ |

因果解释：

- PPO 几乎只学到 end-effector 待在 object 中心附近，因为这是 distance reward 的局部最优；它没有发现“先改变物体可抓状态”的长链。
- Privileged action curriculum 让策略先进入能抓/lift 的状态分布，再逐步恢复物理约束，因此最终 reward 高几个数量级。
- Pivot Grasp 说明这不是单一轨迹记忆：当桌边小墙阻止直接 push-to-edge，策略发现利用 robot base 支撑进行 pivot 的替代行为。

### 3.3 Kuka + AllegroHand thin YCB objects

论文选择 scissors、stapler、wrench，因为 prior functional grasping work 在这些 thin objects 上失败。对比方法是 DexPBT 和 SAPG，同环境、同 observation、同 reward。

主文未给精确表格数字，但 Fig. 5 和文字说明如下：

- 本文方法在三个 objects 上均能学到有效策略。
- DexPBT 对相对较厚的 stapler 能收敛到约 1500 reward，但仍低于本文方法。
- DexPBT/SAPG 在 scissors 和 wrench 等更难对象上失败或低 reward。
- scissors 行为包括先把物体 maneuver 到桌边再抓取。

因果解释：

- DexPBT/SAPG 增强探索，但仍受真实接触约束下的可达高奖励区域稀薄问题限制。
- Privileged actions 改变了早期探索拓扑，使策略能先看到“对象状态被改变后可以抓”的高回报路径。

### 3.4 Sim-to-real

论文做了 Franka real-world experiments，展示 push-to-edge 和 pivot grasp 行为的物理可行性。重要细节：

- 使用 domain randomization：object pose/shape randomization + observation noise。
- 因 tabletop non-graspable pose 常有 occlusion，难以精准获得 pose。
- 作者将仿真中的 robot movement trajectories distilled/recorded 后，在真实环境中复制这些行为。
- 主文没有给出大规模 real-world success-rate table。

因此这部分应理解为 qualitative physical validation，而不是像 RL-100 那样的部署级统计验证。

### 3.5 Ablation

对 scissors 做 stage ablation：

| Variant | 结果 | 因果解释 |
|---------|------|----------|
| Full framework | 快速收敛到高 reward | Stage 1 给稳定 grasp pose 搜索通道，Stage 2 给对象交互探索通道 |
| Without Stage 1 | 最终可学到 workable behavior，但训练更慢、reward 更低 | virtual force 能帮助物体交互，但没有 collision relaxation 时，选择合适 grasp pose 更难 |
| Without Stage 2 | 失败，卡在局部最优 | 没有 virtual force，策略缺少探索对象状态改变的有效通道 |

这组 ablation 支持一个清晰结论：Stage 1 主要帮助 grasp pose discovery，Stage 2 是突破 object-interaction exploration bottleneck 的关键。

## 4. 核心洞见

### 4.1 论文真正的 insight

本文真正的 insight 是：**对 long-horizon contact-rich RL，最难的不是最终动作控制，而是让随机探索进入“对象状态已经被改变”的中间状态分布。**

Privileged action 并不直接告诉策略应该怎么推；它临时让“物体能被影响”这件事更容易发生。策略一旦看见这种因果链，curriculum 再把不真实通道关掉，逼它用真实接触替代 privilege。

### 4.2 为什么有效

有效链条：

`collision relaxation`
→ 更容易探索到接近/抓取形态
→ `virtual force`
→ 更容易让物体状态发生变化
→ reward 开始反馈“改变物体状态能带来 lift/goal”
→ curriculum 收紧 privilege
→ robot motion 逐步替代 virtual force / penetration
→ normal setting 下保留真实可执行行为。

这是一种 continuation method：先优化松弛问题，再连续变形到原问题。

### 4.3 什么时候会失效

1. **privilege 太强**：策略可能学会远程移动物体或穿透行为，课程收不回来。
2. **最终真实任务需要精细接触**：虚拟力只提供粗 object motion，不教 tactile/contact stability。
3. **reward 局部最优不变**：如果默认 grasp/lift reward 本身错位，privilege 可能放大错误行为。
4. **仿真到真实观察缺口大**：本文真机部分用轨迹复制而不是 fully closed-loop robust deployment，说明视觉/pose/occlusion 仍是问题。
5. **privileged action 手工设计**：不同任务需要设计不同 relax/force channel，目前无统一自动方法。

## 5. 替代方案与理论局限

### 5.1 理论维度

Privileged MDP 可以理解为一族 curriculum MDP：

$$
\mathcal{M}_{\eta}
=
(S,A_R\cup A_P,P_\eta,R,\gamma),
$$

其中 $\eta=(\Delta_R,\alpha)$ 控制 privilege 强度，最终目标是：

$$
\eta\to(0,\alpha_{\min}),\qquad A_P\to\varnothing.
$$

但没有理论保证：

$$
\pi^*_{\mathcal{M}_{\eta_0}}
\rightarrow
\pi^*_{\mathcal{M}_{real}}.
$$

curriculum path 可能进入真实 MDP 中不可行或低效的 basin。论文用 staged ablation 和 real-world qualitative validation 支持它在这些任务上有效，但这不是普适保证。

### 5.2 算法维度

| 方法 | 优势 | 风险 |
|------|------|------|
| Privileged Action | 强化探索，减少 reward engineering/demo 需求 | 需手工设计 privilege，可能学到 cheat |
| Dense reward shaping | 直接引导中间行为 | 任务特定，容易改变最优策略 |
| Demonstrations/reference trajectories | 高效 warm-start | 收集贵，human bias，泛化差 |
| Skill chaining | 可控、可解释 | 需要人工分解和 transition design |
| Domain randomization | sim-to-real 更稳 | 不解决 early exploration bottleneck |

### 5.3 工程与实验维度

1. real-world 没有量化 success table，只是展示迁移行为。
2. 部署并非直接用完整 RL policy 闭环，而是对仿真 trajectory 做 distillation/replication。
3. reward 仍然是 dense grasp/lift default，不是完全 sparse。
4. privileged action 依赖 IsaacGym 中可修改 collision/force 的能力。
5. 对真正动态、触觉密集、非准静态操作，virtual force curriculum 是否能迁移仍未知。

## 6. 对用户研究的启发

### 6.1 对 DNPM / WMTS 的迁移

这篇对转笔的启发很直接：转笔的长因果链是“接触施力 → 物体旋转/滑移 → 空中或低接触阶段 → 再接触接住”。随机策略很难探索到完整链条。Privileged action 可作为仿真内脚手架。

| 本文 privilege | 转笔可替代版本 | 风险控制 |
|----------------|----------------|----------|
| robot-table collision relaxation | finger-object soft contact / relaxed penetration with penalty | 不能让手指长期穿透物体，必须逐步恢复硬接触 |
| virtual force on object | gated virtual torque / angular velocity assist on pen | 只能在手指接近并速度匹配时启用，避免远程控笔 |
| virtual table curriculum | gravity/friction/contact stiffness curriculum | 每阶段必须在 no-privilege eval 中验证 |
| no non-prehensile reward | 只给 terminal spin/catch reward + tactile stability bonus | 对转笔可能需要少量 contact-progress reward，否则 credit 太稀 |

一个 WMTS 训练版本：

1. Stage 1：softened contact / reduced gravity，让策略探索到基本 finger-object coordination。
2. Stage 2：gated virtual angular impulse，只在真实接触附近允许，帮助发现旋转相位。
3. Stage 3：逐步恢复真实摩擦、重力、contact stiffness，移除 virtual torque。
4. Stage 4：用 PPO Oracle / RL-100 style fine-tuning 在真实或高保真 sim 中修补失败边界。

### 6.2 可验证实验建议

1. **Privilege strength sweep**  
   比较不同 virtual torque 上限和 gating threshold。若 privilege 太强导致 final no-privilege success 下降，说明学到 cheat。

2. **Curriculum ablation**  
   对转笔复现本文结构：without Stage 1、without Stage 2、direct real physics。看哪个阶段对应 grasp/catch/rotation bottleneck。

3. **No-privilege evaluation at every curriculum step**  
   不只看当前 privileged env success，而要每轮在真实物理无 privilege 环境评估，防止假收敛。

4. **Tactile-aware gating**  
   将 $B(x_t)$ 从 position/velocity gating 改成 tactile contact gating：只有触觉确认接触时才允许 virtual torque 辅助。

5. **Distillation check**  
   如果使用 privileged policy 产生 demonstrations，必须训练 deployable policy 不含 privileged action head，并检查是否能闭环恢复。

### 6.3 不应过度外推的点

- 本文的 Franka/YCB 任务仍主要是 tabletop grasp/lift + non-prehensile reposition，不是高速动态转笔。
- virtual force 可能隐藏了真实接触动力学学习，特别是摩擦、滑移、触觉反馈。
- “无额外非抓取 reward”不等于 reward 简单到只有 terminal success；它仍有 IsaacGym dense grasp/lift components。
- 真机验证不是大规模统计部署，因此对 sim-to-real 成功率要谨慎。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

Privileged action 是 exploration-shaping，不是 policy class 本身。它改变训练 MDP：

$$
P_{real}(x_{t+1}\mid x_t,u_R)
\quad\rightarrow\quad
P_{\eta}(x_{t+1}\mid x_t,u_R,u_O,\Delta_R).
$$

最终目标是让 $\eta$ 回到真实设置，使 learned policy 落在 original MDP 中。

### 7.2 与 [[ContactMechanics]] 的联系

Stage 1 修改的是接触互补条件：

$$
\phi_R(x)F_R=0
\quad\rightarrow\quad
(\phi_R(x)+\Delta_R)F_R=0.
$$

Stage 2 则直接给 object dynamics 增加受力通道。二者都在绕开 contact boundary 的探索稀疏性，但也都可能破坏真实接触结构。

### 7.3 与 WMTS 的联系

Privileged Action 可以作为 WMTS 的 latent task generation / PPO Oracle 的 curriculum generator：先用 relaxed physics 找到可能的 contact sequence，再在真实 physics 中筛选和 fine-tune。

但最终必须与以下机制结合：

- ensemble world model uncertainty：检测 privilege removal 后哪些 states 不可信；
- tactile/contact reward：让真实接触质量进入 credit assignment；
- RL-100 style real fine-tuning：修补 privilege-to-real 的最后差距；
- GAT/DexNDM style actuator grounding：防止仿真中的 privileged trajectory 上真机时被执行器误差破坏。

## References

- Mao et al., 2025. *Learning Long-Horizon Robot Manipulation Skills via Privileged Action*.
- Zhou and Held, 2023. *Learning to Grasp the Ungraspable with Emergent Extrinsic Dexterity*.
- Petrenko et al., 2023. *DexPBT*.
- Singla et al., 2024. *SAPG: Split and Aggregate Policy Gradients*.
