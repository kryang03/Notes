---
tags:
  - paper
  - dexterous-manipulation
  - sim-to-real
  - neural-dynamics
  - in-hand-rotation
  - residual-policy
  - autonomous-data-collection
aliases:
  - DexNDM
  - Joint-wise Dynamics
paper-year: 2025
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/DEXNDM: CLOSING THE REALITY GAP FOR DEXTEROUS IN-HAND ROTATION VIA JOINT-WISE NEURAL DYNAMICS MODEL.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[Optimization]]"
  - "[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]]"
  - "[[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]]"
---

# DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model

> [!abstract] 核心贡献
> DexNDM 的关键不是“学一个真实动力学模型”，而是把高维手-物系统的 sim-to-real gap 投影到**每个关节自己的 state-action history** 上，用 joint-wise neural dynamics 收缩分布偏移，再训练 residual policy 让真实关节响应追上仿真基策略，从而在 LEAP Hand 上实现复杂物体、多轴、多腕姿态的真实 in-air rotation。

> [!tip] 与理论基础的关联
> - [[Dynamics#3.1 操作器方程：$M(q)\ddot q+C(q,\dot q)\dot q+N(q)=\tau$|Dynamics §3.1]]：joint-wise effective dynamics 来自操作器方程的分块消元。
> - [[Dynamics#4.2 约束动力学：Lagrange 乘子与约束反力|Dynamics §4.2]]：物体接触力作为 $\tau_{ext}$ / $J_c^\top f_c$ 进入关节动力学，但 DexNDM 不显式估计物体状态。
> - [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|ReinforcementLearning §9]]：它是 $\Delta_T$ transition-gap 修正，不是视觉 gap 或 reward gap。
> - [[Optimization#2.2 拉格朗日对偶：把约束"价格化"|Optimization §2.2]]：residual policy 的监督目标等价于让真实动力学下的下一状态逼近仿真参考转移。
> - [[Actuation#10. 迁移层 II：数据驱动执行器模型 (Actuator Model)|Actuation §10]]：joint-wise $q^i_{t+1}=f_{\psi_i}(h^i_t)$ 正是 Actuator Net 的手内旋转版——学"仿真 PD 没覆盖的那段残差"；挂 **电流≠关节力矩** 暗线：它建模的是 command→真实关节响应的净效应（$H^{eff}\ddot q^i+G^{eff}=\tau^i$），刻意绕开显式 $\tau$。
> - [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦|WorldModels §5.2]]：DexNDM 只建 joint（actuator 侧）转移、刻意丢掉 object 状态，是 WMTS "Actuator + Rigid 解耦" 的 actuator 半边实证——WM 若缺这一层，会把真实执行偏差误判成高层任务失败。
> **核心技术**: specialist-to-generalist distillation, joint-wise neural dynamics, KL information contraction, Chaos Box autonomous data, residual action compensation.

---

## 0. 阅读定位与范本价值

这篇 paper 是 in-hand rotation 簇里非常重要的一环，因为它补上了前面几篇的空白：

- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] 证明触觉可以帮助真实旋转，但物体主要是 regular-sized / regular-shaped。
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] 用 adaptation module 估计 hidden context，但更像系统级 extrinsics。
- [[Lessons from Learning to Spin Pens]] 能真机转笔，但使用 open-loop replay 和后续微调，策略泛化边界比较窄。
- DexNDM 试图回答：**如果我们不想依赖昂贵触觉、不想追踪物体 pose、不想让人工反复 reset，能不能仍然收集足够真实动力学信息来闭合 gap？**

它的回答是 joint-wise factorization。这个答案值得严肃对待，也必须批判性对待：它不是完整 world model，不预测物体状态，不显式建模接触模式；它只是说，对“把仿真动作转到真实手关节响应”这个子问题，每个关节的本体历史可能已经包含足够的低维净效应。

| 范本要求 | DexNDM 应回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么 whole-hand dynamics / DR / ASAP-UAN 不够？ | §1 写出数据分布相关性与规模的冲突 |
| 原理与理论 | joint-wise 分解从哪里来？KL 收缩为什么与泛化有关？ | §2 从 manipulator equation、projection、DPI 和 residual objective 推导 |
| 实验与验证 | 哪些真实数字证明它不是只会 cube？ | §3 汇总 Table 1-7 与 data-collection evidence |
| 未来与结合 | 对 WMTS / LinkerHand actuator dynamics / DNPM 有什么启发？ | §5-7 写出可迁移接口和拒绝理由 |

---

## 1. 问题设定与动机

### 1.1 一句话核心

DexNDM 把 dexterous in-hand rotation 的 sim-to-real 问题从“学习整个手-物系统的真实动力学”改写成“学习每个关节在真实载荷和耦合下的下一步响应”，再用 residual action 让真实手沿着仿真策略期望的关节转移走。

### 1.2 直观隐喻

whole-hand dynamics 像试图从整个交响乐录音里恢复每个乐器的物理模型；DexNDM 像给每个乐手一个自己的节拍器和最近几拍历史，让它只预测自己下一拍会落在哪里。  

这个隐喻的关键不是“每个乐手独立”，而是“每个乐手的下一步由全局影响压缩出的低维净效应决定”。如果这个净效应确实能从自己的历史中读出来，模型会很省数据；如果某个任务需要精确知道物体 pose、接触点和跨指耦合，joint-wise projection 就会丢掉太多信息。

### 1.3 现有方法的局限

| 方法范式 | 注入的先验 | 在本文任务上的失败点 |
|---|---|---|
| Domain Randomization | 用很宽的仿真参数覆盖真实世界 | ranges heuristic；面对复杂形状、高 aspect ratio、多腕姿态时需要极大仿真覆盖 |
| System Identification | 用真实数据拟合 simulator 参数 | 上界受参数化模型限制，接触、软形变、joint friction、load-dependent effects 难以写进低维参数 |
| Whole-hand neural dynamics | 学 $q_{t+1}=f_\theta(H_t)$，把整手 history 输入模型 | 输入维度高，数据需求大；autonomous data 与 rotation task 分布不一致时更容易过拟合 source distribution |
| Delta-action compensator, ASAP/UAN 类 | 学 sim-real action correction，再 fine-tune policy | 需要分布相关且质量高的真实转移；本文适配后在真实测试中甚至无法转简单 cylinder |
| 任务相关真实数据采集 | 直接 rollout policy，追踪物体 pose | 小物体遮挡、轴对称物体 pose ambiguity、掉落后人工 reset，平均 200s/trajectory 或 42.86s/trajectory，覆盖窄 |
| 触觉 Sim-to-Real | 用 tactile 直接观测接触 | 有效但依赖额外硬件；DexNDM 想证明无昂贵 tactile 也能跨更宽物体分布 |

### 1.4 Delta 分析

| 维度 | 最近邻方法 | DexNDM 的 Delta | 真实 value add |
|---|---|---|---|
| 动力学粒度 | HORA 学系统级 extrinsics；whole-hand NDM 学全局 history | 学每个关节的 $f_{\psi_i}(h^i_t)$ | 降低维度，缓解分布偏移，提高低数据泛化 |
| 数据采集 | task-aware rollout + pose tracking / manual reset | Chaos Box object-loaded autonomous replay | 不需要物体 pose，不需要频繁人工 reset，可持续收集外部载荷下的本体转移 |
| 策略训练 | single policy 或 online fine-tune | specialist PPO -> BC generalist -> residual policy | 把“任务泛化”和“真实动力学补偿”拆开 |
| Sim-to-Real 补偿 | 直接 fine-tune 或 action delta | residual policy 让 learned real dynamics 下的 next state match sim next state | 保留好用的 base policy，避免错误 dynamics 把整策略 fine-tune 崩 |

---

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_t$ | $\mathbb{R}^{16}$ | LEAP Hand joint position | 否，观测 | 真实/仿真关节状态 | DexNDM 用 LEAP 16 DoF，不是 LinkerHand |
| $a_t$ | $\mathbb{R}^{16}$ | target joint position | policy output / executed input | 位置控制目标 | 论文中 $a_t=a_{t-1}+\alpha\Delta a_t$，$\alpha=1/24$ |
| $\Delta a_t$ | $\mathbb{R}^{16}$ | policy sampled relative target | 是，策略输出 | 增量动作 | 不是 torque；torque 由 PD 生成 |
| $\tau_t$ | $\mathbb{R}^{16}$ | PD controller | 对策略不可微 | $\tau_t=K_p(q^{tar}_t-q_t)-K_d\dot q_t$ | real setup: 20 Hz, $K_p=800$, $K_d=200$ |
| $o_t^{oracle}$ | 320-dim | privileged sim observation | 否，输入 | specialist PPO 使用的富观测 | 包含 object state/force/contact，不能直接部署 |
| $o_t^{gene}$ | proprio history + wrist + axis | BC generalist observation | 否，输入 | 真实可部署策略输入 | 不包含物体 pose，不是 oracle observation |
| $H_t$ | whole-hand history | dynamics model input candidate | 否 | $\{q_j,a_j\}_{j=t-W+1}^{t}$ for all joints | whole-hand model用它，维度高 |
| $h^i_t$ | per-joint history | joint-wise dynamics input | 否 | $\{q^i_j,a^i_j\}_{j=t-W+1}^{t}$ | 只看第 $i$ 个关节，不看其他关节 |
| $f_{\psi_i}$ | neural model | learned dynamics | 是，模型参数 | 预测 $q^i_{t+1}$ | 每关节一个模型/头，不是完整 hand-object WM |
| $P,Q$ | target/source distributions | theory abstraction | 否 | $P$ 是任务相关真实分布，$Q$ 是收集数据分布 | 泛化证明依赖 covariate shift 与表达性假设 |
| $g$ | projection map | theory abstraction | 否 | $(H_t,q^i_{t+1})\mapsto(h^i_t,q^i_{t+1})$ | 降维会收缩 shift，也会丢信息 |
| $\pi_{base}$ | base generalist policy | BC training | 是，训练后部署 | 仿真训练并蒸馏出的可部署策略 | 没有 residual 时 direct transfer |
| $\pi_{res}$ | residual policy | supervised training | 是 | 输出 $a_t^{res}$ 补偿真实动力学 | 目标是 matching sim next-state，不是重新学任务 |
| Chaos Box data | transitions | real collection | 否，数据 | soft balls 施加随机载荷 | load distribution 必须覆盖任务中的物体作用 |

### 2.2 从 MDP 到 specialist-to-generalist：为什么先训练多个 oracle

任务先被写成 POMDP：

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},\mathcal{O},P,R)
$$

目标是：

$$
\pi^\*=\arg\max_\pi
\mathbb{E}_{\tau\sim p_\pi(\tau)}
\left[\sum_{t=1}^{N}r(s_t,a_t)\right]
$$

oracle policy 在 Isaac Gym 里使用 rich privileged observation。Appendix A.1 给出的 320-dim oracle observation 包括：

| 观测块 | 维度 |
|---|---:|
| 3-step joint position history | 48 |
| 3-step joint target history | 48 |
| joint velocity | 16 |
| fingertip state and velocity | 52 |
| object state and velocity | 13 |
| object guiding goal pose | 4 |
| joint and rigid body forces | 40 |
| contact force and binary contact | 92 |
| wrist orientation quaternion | 4 |
| rotation axis | 3 |
| **Total** | **320** |

策略动作是 relative target position：

$$
\Delta a_t\sim\pi(o_t),\qquad
a_t=a_{t-1}+\alpha\Delta a_t,\qquad \alpha=\frac{1}{24}
$$

然后由 PD controller 执行：

$$
\tau_t=K_p(q^{tar}_t-q_t)-K_d\dot q_t
$$

奖励由三部分组成：

$$
r=\alpha_{rot}r_{rot}+\alpha_{goal}r_{goal}+\alpha_{penalty}r_{penalty}
$$

旋转奖励：

$$
r_{rot}=\text{clip}(\omega_t\cdot k,-c,c),\qquad c=0.5
$$

其中 $k$ 是目标旋转轴，$\omega_t$ 是物体角速度。惩罚项包括 off-axis angular velocity、object linear velocity、hand pose deviation、joint work/torque：

$$
r_{penalty}
=
-\alpha_{rotp}\|\omega_t\times k\|_1
-\alpha_{lin}\|v_t\|_2^2
-\alpha_{pose}\|q_t-q_{init}\|_2^2
-\alpha_{work}\tau^\top\dot q
-\alpha_{torque}\|\tau\|_2^2
$$

论文发现仅靠这些 reward 解决不了 long object rotation，于是加入每 $90^\circ$ 更新的 intermediate goal pose reward。这里和刚处理的 [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] 有共性：困难旋转任务不能只靠最终 rotation reward，需要中间相位/目标来避免局部最优。

因为一个 oracle 覆盖所有物体类别很难，DexNDM 先按几何类别训练 5 个 PPO specialist，再聚合成功轨迹，用 BC 训练一个 generalist。作者明确说 DAgger-style distillation 在此设置下不稳定，甚至在真实世界 collapse；BC 反而因为只模仿 high-quality oracle behavior，更可部署。

### 2.3 操作器方程到 joint-wise effective dynamics 的无跳步推导

从标准 manipulator equation 开始，把物体接触的影响当作外部广义力：

$$
M(q)\ddot q+C(q,\dot q)\dot q+G(q)=\tau+\tau_{ext}
$$

论文在低速假设下忽略 Coriolis：

$$
C(q,\dot q)\dot q\approx 0
$$

现在只建模第 $i$ 个关节。把它记为 modeled joint $m$，其余 15 个关节记为 slave joints $s$：

$$
q_m=[q_i]\in\mathbb{R}^1,\qquad
q_s=[q_j,\ j\ne i]\in\mathbb{R}^{15}
$$

将质量矩阵分块：

$$
\begin{bmatrix}
M^{mm} & M^{ms}\\
M^{sm} & M^{ss}
\end{bmatrix}
\begin{bmatrix}
\ddot q^m\\
\ddot q^s
\end{bmatrix}
+
\begin{bmatrix}
G^m\\
G^s
\end{bmatrix}
=
\begin{bmatrix}
\tau^{m,total}\\
\tau^{s,total}
\end{bmatrix}
$$

第二行给出：

$$
M^{sm}\ddot q^m+M^{ss}\ddot q^s+G^s=\tau^{s,total}
$$

解出 slave acceleration：

$$
\ddot q^s
=
(M^{ss})^{-1}(\tau^{s,total}-G^s-M^{sm}\ddot q^m)
$$

代回第一行：

$$
M^{mm}\ddot q^m+
M^{ms}(M^{ss})^{-1}(\tau^{s,total}-G^s-M^{sm}\ddot q^m)
+G^m
=
\tau^{m,total}
$$

把 $\ddot q^m$ 项合并：

$$
\left(M^{mm}-M^{ms}(M^{ss})^{-1}M^{sm}\right)\ddot q^m
+M^{ms}(M^{ss})^{-1}(\tau^{s,total}-G^s)
+G^m
=
\tau^{m,total}
$$

其中 modeled joint 的 total torque 可以写成：

$$
\tau^{m,total}=[\tau_i+\tau_i^{ext}]^\top
$$

把所有来自 slave joints、重力、外部接触、耦合的项压缩成 effective terms：

$$
H_t^{eff}
=
M^{mm}-M^{ms}(M^{ss})^{-1}M^{sm}
$$

$$
G_t^{eff}
=
M^{ms}(M^{ss})^{-1}(\tau^{s,total}-G^s)+G^m-\tau^{eff}
$$

于是单关节动力学可以写成：

$$
H_t^{eff}\ddot q^i_t+G_t^{eff}=\tau^i_t
$$

这一步是 DexNDM 的理论核心：它没有声称关节真的独立，而是声称**其他关节、物体载荷、驱动误差和接触影响，可以在短时间窗口内表现为该关节的低维 effective terms**。神经模型不显式预测 $H_t^{eff},G_t^{eff}$，而是直接学：

$$
q^i_{t+1}=f_{\psi_i}(h^i_t),\qquad
h^i_t=\{q^i_j,a^i_j\}_{j=t-W+1}^{t}
$$

论文给出的直觉是短窗口 $W=10$，对应约 0.5s；在这个窗口里 joint state、active torque、virtual external torque 都可被平滑函数近似，历史窗口能隐式编码 net effects。

### 2.4 信息收缩：为什么 joint-wise projection 可能更泛化

whole-hand model 学：

$$
q^i_{t+1}=f^i_\theta(H_t)
$$

joint-wise model 学：

$$
q^i_{t+1}=f_{\psi_i}(h^i_t)
$$

定义 target distribution $P$ 是任务相关转移分布，例如真实旋转中的 transition；source distribution $Q$ 是可收集的数据分布，例如 Chaos Box autonomous data。投影：

$$
g:(H_t,q^i_{t+1})\mapsto(h^i_t,q^i_{t+1})
$$

Data Processing Inequality 告诉我们：

$$
KL(P\|Q)\ge KL(g(P)\|g(Q))
$$

如果 $g$ 是非单射并且确实合并了源/目标中相对结构不同的点，严格小于成立：

$$
KL(P\|Q)> KL(g(P)\|g(Q))
$$

意思是：投影到 per-joint history 后，source 和 target 的分布差异会变小。这就是作者所谓 information contraction。

但这不是免费的午餐。泛化误差可以拆成两部分：

$$
RP(f^Q_2\circ g_X)-RP(f^Q_1)
=
\underbrace{RQ(f^Q_2\circ g_X)-RQ(f^Q_1)}_{\epsilon_A:\ \text{approximation cost}}
+
\underbrace{[RP-RQ]_{joint}-[RP-RQ]_{whole}}_{-\epsilon_B:\ \text{generalization benefit}}
$$

只有当：

$$
\epsilon_B>\epsilon_A
$$

joint-wise model 才会在 target distribution 上优于 whole-hand model。  

这就是本 paper 讲故事最漂亮的地方：它没有简单说“低维一定好”，而是给出一个 tradeoff：

| 项 | 含义 | DexNDM 的判断 |
|---|---|---|
| $\epsilon_A$ | 降维后丢掉信息造成的表达性损失 | 在高数据、in-domain 时 joint-wise 略弱于 whole-hand，说明确实有损失 |
| $\epsilon_B$ | 分布偏移收缩带来的泛化收益 | 在低数据和 OOD 设置下显著更强，说明收益更大 |

### 2.5 Chaos Box 数据采集：为什么“不追踪物体”反而合理

DexNDM 的数据采集设计叫 Chaos Box：把 LEAP Hand 放在装有 soft balls 的容器里，open-loop replay 仿真 base policy 动作，让手持续受到随机载荷。四个原则：

| 原则 | 实现方式 | 解决的问题 |
|---|---|---|
| policy-awareness | replay simulated base policy actions | 让关节动作分布不要偏离任务太远 |
| object-loaded interaction | soft balls 持续接触手 | 提供外部载荷和耦合扰动 |
| broad coverage | 以 0.5 概率给动作加 $\sigma=0.01$ Gaussian noise | 扩展 coverage，避免只覆盖 easy trajectories |
| scalability | 无 object pose tracking，无人工 reset | 允许 overnight autonomous collection |

关键 insight 是：如果模型只预测 per-joint next state，那么它不需要知道具体是 bunny、cube 还是 ball 造成了载荷；它只需要看到“这个关节在某类载荷与自身动作历史下会怎么响应”。这正是 joint-wise projection 让 autonomous data 可用的原因。

### 2.6 Residual policy：不是直接 fine-tune，而是让真实动力学追仿真转移

base generalist 给出 $a_t$。learned real dynamics $f_\psi$ 可以预测真实手在动作下的下一关节状态。residual policy 输出 $a_t^{res}$，部署时执行：

$$
a_t^{final}=a_t+a_t^{res}
$$

训练目标可以理解为：

$$
\pi^{res\*}
=
\arg\min_{\pi^{res}}
\mathbb{E}
\left[
\sum_{t=1}^{N-1}
\left\|
q^{sim}_{t+1}
-
f_\psi\left(\{q_j,a_j+\pi^{res}(o_j,a_j)\}_{j=t-W+1}^{t}\right)
\right\|_2
\right]
$$

也就是说，它不直接最大化任务 reward，而是监督式地学一个 action correction，使得“真实动力学模型预测的下一状态”尽量匹配“仿真轨迹里的下一状态”。

为什么这比 direct fine-tuning 稳？Appendix B.4 说 direct fine-tuning on learned dynamics 对超参数敏感，行为 erratic，甚至基本旋转失败。直观原因是：如果 learned dynamics 有偏差，直接用它优化整个 policy 会把策略推向 model error；residual policy 只是补偿一个好 base policy，错了也更不容易把基础能力毁掉。

---

## 3. 训练、数据与实验

### 3.1 训练与硬件设置

| 项目 | 论文设置 |
|---|---|
| Robot | LEAP Hand + Franka Arm |
| Control | position control, 20 Hz |
| Real PD gains | $K_p=800$, $K_d=200$ |
| Base policy training | 5 object-category PPO specialists in Isaac Gym |
| Generalist training | BC from successful specialist trajectories |
| Generalist architecture | Residual MLP, 5 residual blocks, hidden dim 1024 |
| Dynamics model | pretrain in sim, fine-tune on real transitions |
| Real transition collection | Chaos Box; 400-step episode at 20 Hz, about 20s/trajectory |
| Multi-orientation real data | 6 wrist orientations, 4000 trajectories per orientation |
| Ablation real data | 4000 trajectories, 1,600,000 transitions |
| Dynamics/residual training | 8 A10 GPUs; residual policy about 10-13h depending setting |

**因果解释**：这个设置反驳了“只要真实数据足够就能学 whole-hand model”的朴素看法。真实数据不是缺采样按钮，而是缺可扩展、分布相关、无需 pose tracking 和 reset 的采集方式。DexNDM 的 engineering value 在于把数据需求降到可以由 autonomous proprioceptive collection 承担。

### 3.2 Simulation generalization: base generalist 先证明任务覆盖

| Method | General axes RotR ↑ | General axes TTF ↑ | General axes RotP ↓ | GO Success ↑ |
|---|---:|---:|---:|---:|
| AnyRotate* re-implementation | 162.55±19.18 | 0.86±0.18 | 0.79±0.11 | 64.33±4.70 |
| Ours Generalist in Sim | **242.33±23.30** | **0.94±0.05** | **0.46±0.06** | **88.27±3.21** |

更完整的 Table 1 里，Ours 在 ±x、±y、±z 和 general axes 上都超过 AnyRotate*；例如 ±z RotR 从 173.87±11.70 到 314.28±27.91。  

**因果解释**：这张表证明 specialist-to-generalist pipeline 不是只靠 sim-to-real trick 托底。它先在仿真中训练出更强的 multi-axis / multi-wrist / unseen-shape generalist，否则后面的 residual policy 没有好的 base 可以补偿。

### 3.3 与 AnyRotate 的真实对比：DexNDM 真正放大的是困难设置

Table 2 在 AnyRotate 可复现实物上比较 Rot(rad) 和 TTF(s)。选几个最有解释力的数：

| Object / setting | AnyRotate Rot / TTF | Direct Transfer Rot / TTF | DexNDM Rot / TTF | 关键含义 |
|---|---:|---:|---:|---|
| Cube, rotation axis | 6.53 / 24.00 | 14.92 / 38.67 | **39.10 / 198.39** | residual 后从“能转几圈”到长时间稳定 |
| Container, rotation axis | 2.63 / 25.00 | 8.49 / 40.22 | **10.79 / 45.00** | Direct 已强，DexNDM 补稳定性 |
| Tin Cylinder, rotation axis | 5.78 / 29.7 | 9.16 / 23.67 | **15.68 / 37.83** | 真实动力学补偿提高旋转量和存活时间 |
| Gum Box, rotation axis | 4.08 / 18.3 | 10.65 / 38.56 | **13.96 / 47.22** | box 类 object 也受益 |

**因果解释**：Direct Transfer 已经强于 AnyRotate，说明 base generalist 本身很关键；DexNDM 进一步把最难稳定的 settings 拉开，说明 residual policy 补的是真实动力学误差，而不是替代策略学习。

### 3.4 与 Visual Dexterity 的对比：注意 metric favor 和 supporting table

Table 3 用视频估计 survival angle $\lfloor radian / 0.5\pi\rfloor$，粗略衡量掉落前转过多少个 90 度。部分 Visual Dexterity 结果有 supporting table，metric 还偏向 VD。即使如此：

| Object | Visual Dexterity | DexNDM | 解读 |
|---|---:|---:|---|
| Cow | 7 | **8** | comparable/slightly better |
| Bear | **10** | **10** | 持平 |
| GRAB Elephant | 3 | **7** | complex shape 明显提升 |
| Bunny | 2 | **5** | complex animal shape 明显提升 |
| Teapot | 8* | **48** | VD 有 supporting table，DexNDM 仍大幅更高 |

**因果解释**：这张表支持“复杂形状”claim，但它不是严格同平台对比。作者也承认 D'Claw 到 LEAP 的直接适配不可行，因此这是 weaker evidence。范本级 recap 不能把它写成完全公平 SOTA victory。

### 3.5 Multi-axis real rotation：whole-hand NDM 在小物体上崩得很清楚

Table 4 在 palm-down wrist 下比较 Direct Transfer、Whole Hand NDM、DexNDM。

| Object set / axis | Direct Transfer Rot / TTF | Whole Hand NDM Rot / TTF | DexNDM Rot / TTF |
|---|---:|---:|---:|
| Regular, ±z | 11.69 / 21.67 | 7.38 / 16.33 | **23.82 / 37.50** |
| Regular, cubic diagonal | 9.03 / 22.71 | 3.30 / 8.87 | **16.93 / 30.44** |
| Small, ±z | 6.94 / 20.17 | 0.00 / 0.00 | **9.29 / 26.75** |
| Small, cubic diagonal | 5.40 / 23.21 | 0.26 / 0.67 | **6.03 / 27.34** |
| Irregular, ±y | 6.13 / 24.62 | 2.91 / 10.32 | **11.32 / 39.04** |
| Irregular, cubic diagonal | 6.53 / 26.29 | 2.33 / 11.68 | **9.19 / 33.14** |

**因果解释**：最有力的不是 DexNDM 比 Direct Transfer 高，而是 Whole Hand NDM 经常比 Direct Transfer 更差，甚至小物体 ±z 变成 0.00/0.00。这说明“学一个 neural dynamics model”并不自动有帮助；错误粒度的动力学模型会把策略带偏。

### 3.6 Multi-wrist real rotation：DexNDM 的 claim 不止 palm-down

Table 5 在 z-axis rotation 下测试六种 wrist orientations。

| Wrist orientation | Direct Transfer Rot / TTF | Whole Hand NDM Rot / TTF | DexNDM Rot / TTF |
|---|---:|---:|---:|
| Palm Up | 10.03 / 25.63 | 7.37 / 20.42 | **14.61 / 32.82** |
| Palm Down | 7.64 / 20.98 | 3.46 / 14.21 | **13.20 / 29.33** |
| Base Up | 5.40 / 21.48 | 4.17 / 18.22 | **9.42 / 36.00** |
| Base Down | 4.92 / 18.37 | 2.33 / 7.06 | **7.59 / 44.67** |
| Thumb Up | 6.46 / 25.02 | 4.79 / 20.15 | **11.93 / 28.37** |
| Thumb Down | 5.90 / 20.77 | 1.91 / 6.33 | **8.60 / 26.93** |

**因果解释**：DexNDM 对 every wrist orientation 都提升，说明它补的不是单一姿态下的接触 bias，而是更底层的 joint-response gap。Base Down 的 TTF 从 18.37 到 44.67 尤其说明 residual compensation 提高稳定性。

### 3.7 Challenging-shape case study：residual policy 的实际价值

| Challenging object | Direct Transfer Rot | DexNDM Rot | 改善类型 |
|---|---:|---:|---|
| Bunny (z) | 7.33 | **8.38** | 小幅稳定性提升 |
| Cow (z) | 3.67 | **6.28** | complex shape 提升明显 |
| Cuboid (vertical, -z) | 31.42 | **99.48** | thin/unstable gait 被显著稳定 |
| Broccoli (-z) | 5.76 | **10.47** | irregular object 提升 |
| Cube (y) | 19.37 | **130.90** | 长时间稳定旋转 |

论文还给出具体观察：3cm × 3cm × 10cm cuboid 没有 residual 最多约 5 circles，有 residual 可持续超过 5 minutes，约 30 circles。这是 residual policy 最能打动人的证据：它不是只提高平均角度，而是把不稳定策略推成可持续技能。

### 3.8 数据采集证据：为什么 Chaos Box 是方法的一半

| 数据采集方式 | 论文观察 |
|---|---|
| task-aware with object pose | 每条 usable trajectory 平均约 200s；小物体遮挡严重；轴对称物体 pose 会“自己旋转”；需 CAD 与初始化 |
| task-aware without pose | 平均 42.86s；仍需人工 reset；数据受 policy 当前能力限制，难加噪声 |
| base waves | 对灵巧手会有自碰风险；history-based model 容易遭遇 distribution shift；波形设计劳动密集 |
| Chaos Box | object-agnostic、可加噪声、无需物体 pose、可 overnight unattended |

最夸张但有用的量级判断：用 task-aware pose 数据点拟合 scaling curve，作者估计要达到 4000 条 autonomous trajectories 的效果，需要 52,483,440 task-aware trajectories，显然不可行。这个 extrapolation 只基于少量点，不能当严格定理，但足以说明传统数据路线的工程不可承受性。

---

## 4. 核心洞见

### 4.1 论文真正的 insight

DexNDM 的真正 insight 是：

> Sim-to-real dynamics modeling 的关键不是模型越完整越好，而是找到一个对任务足够、对分布偏移不敏感、且真实数据能覆盖的表示粒度。

这句话比“joint-wise dynamics 很强”更准确。joint-wise 不是物理上最真实，而是在这个任务里达成了三者平衡：

| 要求 | whole-hand model | joint-wise model |
|---|---|---|
| 表达性 | 高，理论上可包含全局交互 | 稍低，丢掉跨关节显式信息 |
| 样本效率 | 低，真实数据不足时过拟合 | 高，每关节低维预测 |
| 分布鲁棒 | 弱，source/target shift 大 | 强，projection 收缩 KL shift |
| 数据可采集性 | 需要 task-relevant coverage | Chaos Box 的 per-joint load history 足够接近 |

### 4.2 为什么这个设计有效

这套系统不是一个单点技巧，而是互相咬合的三段结构：

1. **Specialist-to-generalist** 先在仿真里获得强 base policy。没有好 base，residual 没东西可补。
2. **Joint-wise dynamics** 把真实交互压成每关节 next-state prediction，降低 real data 的覆盖要求。
3. **Residual policy** 让真实执行追仿真下一状态，不把 learned dynamics 直接用于不稳定 fine-tuning。

### 4.3 什么时候会失效

| 失效场景 | 原因 |
|---|---|
| 任务需要显式物体状态预测 | joint-wise model 只预测 hand joint transition，不知道物体未来 |
| 高速抛接 / aerial phase / 非连续接触 | per-joint history 可能不足以推断飞行物体状态 |
| 强跨指同步耦合主导 | 单关节 history 无法还原 coupling structure |
| 真实载荷超出 Chaos Box 覆盖 | residual policy 会补错方向 |
| base policy 在仿真中已很差 | residual 只能补动力学 gap，不能发明任务策略 |
| tactile/contact sensing 是关键 | 本文没有触觉，limitation 明确建议 richer signals / tactile |

---

## 5. 替代方案与理论局限

### 5.1 理论维度

1. **DPI 只保证 divergence 不增，不保证 prediction 更好**  
   只有当降维后的 approximation error $\epsilon_A$ 小于 generalization benefit $\epsilon_B$，joint-wise 才赢。这个条件在本任务成立，但不能普适外推。

2. **covariate shift 假设很强**  
   Theorem 3.2 假设 $P(Y|X)=Q(Y|X)$。真实接触任务里，Chaos Box load 和旋转物体 load 的条件转移不一定完全一致。

3. **物体状态被刻意丢掉**  
   这对 hand joint response transfer 是优点，对 planning / object-level success prediction 是缺点。它不是 world model。

4. **partial observation ceiling**  
   论文结论明确写道模型上限受 partial observations 限制，未来应 joint modeling hand-object transitions with richer signals and tactile。

### 5.2 算法维度

| 替代方案 | 优点 | 相对 DexNDM 的问题 |
|---|---|---|
| Domain Randomization | 不需要真实数据 | 覆盖复杂对象和腕姿态成本高，range heuristic |
| HORA / RMA | 在线 adaptation 简洁 | 系统级 latent 可能不够细，难处理每关节 actuator/载荷差异 |
| AnyRotate tactile route | 真实接触信号强 | 依赖 tactile hardware，且任务分布较 regular |
| Whole-hand world model | 可预测手-物联合未来 | 数据需求大，source/target shift 下可能比 direct transfer 更差 |
| Direct fine-tuning on learned dynamics | 理论上可端到端优化任务 | 论文实测 unstable, erratic, basic rotation 失败 |

### 5.3 工程/实验维度

- Chaos Box palm-up 受机器人臂 kinematic constraints 限制，需要 bandaged-ball setup，载荷多样性较弱。
- 训练仍重：8 A10 GPUs，dynamics / residual training 以小时到天计。
- AnyRotate / Visual Dexterity 对比存在复现实验和平台差异，不是完全公平同硬件 benchmark。
- residual action magnitude 不大，但长期稳定性提升明显；这说明 gap 可能是小偏差长期积累，而不是单步大错。
- LEAP Hand 结论不能直接搬到 LinkerHand：关节传动、摩擦、控制接口、触觉阵列都不同。

---

## 6. 对用户研究的启发

### 6.1 对 WMTS / LinkerHand / DNPM 的可迁移接口

| DexNDM 机制 | 用户项目中应变成什么 | 价值 |
|---|---|---|
| per-joint $h^i_t=\{q^i,a^i\}_{t-W+1:t}$ | LinkerHand 每关节本体历史 + target history + motor current / actuator temp / latency proxy | 建模 actuator / tendon / joint friction gap |
| Chaos Box object-loaded data | LinkerHand 上安全的随机载荷装置或软物体扰动台 | 不依赖笔 pose 就采集真实关节响应 |
| residual action $a+a^{res}$ | 在 PPO Oracle / Diffusion Policy 输出后加低幅 residual corrector | 不重训主策略，先补真实执行偏差 |
| joint-wise projection | WMTS transition model 的 actuator submodule | 把 $\Delta_T$ 拆成 actuator-level gap 与 object-level contact gap |
| partial-observation limitation | tactile/contact latent module | 转笔不只关节响应，还需要 slip / contact phase |

### 6.2 和当前 FingerGaiting paper 的互补

刚处理的 [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] 卡在 simulation-only + privileged 3D net force。DexNDM 给出另一条真机路线：

| FingerGaiting 缺口 | DexNDM 可补什么 | 仍然缺什么 |
|---|---|---|
| 没有 sim-to-real | joint-wise real dynamics + residual compensation | 只补手关节响应，不补接触力可观测性 |
| privileged 3D force 不可得 | 本体历史可隐式吸收部分载荷影响 | 无法直接知道支撑/推进/交接触碰角色 |
| waypoint 初始化偏仿真 | 真实残差可稳定执行 learned gait | waypoint/phase 仍需单独设计 |

这给用户 DNPM 一个清晰组合：**FingerGaiting 提供 phase/waypoint curriculum，DexNDM 提供 actuator-level sim-to-real grounding，tactile module 提供 contact role observability**。

### 6.3 对 WMTS 五模块的具体接法

| WMTS 模块 | DexNDM 的进入方式 |
|---|---|
| latent task generation | 生成接触 phase / rotation axis / wrist orientation 条件，不直接生成动力学 |
| PPO Oracle | 在 sim 中仍用 privileged observation 训练 specialist；同时记录 $(q,a)$ trajectories |
| Diffusion/Flow generalist | 模仿 oracle 动作，但部署前加 actuator residual 或把 residual 数据蒸馏进 policy |
| Ensemble World Model | 分成 object/contact WM 和 joint-wise actuator WM；不要把二者混成单 latent |
| real-robot fine-tuning | 先用 autonomous load data 训练 joint-wise model，再用少量真实转笔轨迹校准 tactile/contact latent |

### 6.4 可验证实验建议

1. **LinkerHand joint-wise actuator model**  
   在无笔条件下采集不同软负载、不同腕姿态、不同控制频率数据，比较 per-joint / per-finger / whole-hand next-state prediction 的 OOD error。

2. **Residual on top of PPO Oracle**  
   训练仿真 PPO 转笔策略后，不直接真机 fine-tune；先用 DexNDM-style residual 让真实关节 next state match sim next state。指标：掉笔率、平均转数、cycle completion、action correction magnitude。

3. **接触任务中的 two-level dynamics**  
   把 transition gap 分成 actuator gap 和 contact gap。若 residual 只能修正关节轨迹但不能提升 contact phase success，说明还需要 tactile/contact world model。

4. **Chaos Box vs task-aware data**  
   用同等时间预算比较 autonomous load data 与少量真实 pen-spinning data 对 residual policy 的帮助。若 autonomous 数据只提升自由运动、不提升握笔转移，说明 load distribution 不够 task-relevant。

5. **DPI 假设的实证检查**  
   用 t-SNE / MMD / KL proxy 比较 whole-hand history 与 per-joint history 在 source/target 之间的分布距离。不要只看 final task success。

### 6.5 不应过度外推的点

- DexNDM 不是完整 contact-rich world model；它预测 hand joint transition，不预测 object future。
- 它不替代 tactile。论文自己承认 richer signals / tactile 是未来方向。
- 它不说明 direct fine-tuning 永远不行，只说明在他们的 learned dynamics 和训练设置中不稳定。
- 它的 broad generality 建立在强仿真 base policy + 真实 residual 上，不是一个 15 分钟数据从零学技能的方法。
- 对用户 LinkerHand，joint layout、actuator delay、tactile skin、CAN bandwidth 都可能让 per-joint history 的充分性发生变化。

---

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

DexNDM 最值得写进 Dynamics 的不是“用神经网络学动力学”，而是“分块消元后的 effective single-joint dynamics”：

$$
H_t^{eff}\ddot q_t^i+G_t^{eff}=\tau_t^i
$$

这给 [[Dynamics#3.1 操作器方程：$M(q)\ddot q+C(q,\dot q)\dot q+N(q)=\tau$|操作器方程]] 一个工程化学习版本：不再显式估计全局 $M,C,G,J_c^\top f_c$，而是让每关节历史吸收这些项的净效应。

### 7.2 与 [[ReinforcementLearning]] 的联系

DexNDM 属于 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|Sim-to-Real 的 transition-gap 修正]]。它没有改变 reward，也没有做 test-time RL；它保持 base policy，并在 action 层加 residual，使真实 next-state 贴近仿真 next-state。

### 7.3 与 [[ContactMechanics]] 的联系

本文故意避开 object pose 和 contact force 的显式估计，把物体接触的影响压成 joint-level load response。这对一般 in-hand rotation 足够有效，但对 DNPM 转笔的飞行相位、滑移、接棒触点未必足够。ContactMechanics 视角下，它是在学接触结果的投影，而不是接触本身。

### 7.4 与 sim-to-real 粒度谱的关系

| 粒度 | 代表 | 修正对象 | 适用直觉 |
|---|---|---|---|
| 系统级 latent | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] | object / environment extrinsics | hidden context 少且缓慢变化 |
| 动作级 mapping | [[Grounded Action Transformation]] / ASAP-UAN 类 | $a_{sim}\to a_{real}$ | action mismatch 主导 |
| **关节级 dynamics** | **DexNDM** | $q^i_{t+1}=f_{\psi_i}(h^i_t)$ | actuator/load/joint response gap 主导 |
| 接触/触觉级 | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | contact observation and tactile state | 接触可观测性主导 |
| world-model 级 | WMTS ensemble | object/contact future + uncertainty | planning / scheduler 需要知道失败边界 |

DexNDM 的位置非常清楚：它是 actuator/load response grounding，不是 task scheduler 本身。但 WMTS 如果没有这一层，world model 很可能把真实执行偏差误判成高层任务失败。

---

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “joint-wise 为什么不是粗暴忽略耦合？” | 从分块操作器方程推导 $H^{eff},G^{eff}$，说明耦合被压缩为净效应，而不是不存在 |
| “DPI 和泛化有什么关系？” | 解释 $KL(g(P)\|g(Q))<KL(P\|Q)$ 只收缩 shift；还需要 $\epsilon_B>\epsilon_A$ 才能降低 target risk |
| “为什么 whole-hand NDM 反而更差？” | Table 4 小物体 whole-hand 0.00/0.00 是证据；高维模型在低数据和分布偏移下会把 base policy 带偏 |
| “Chaos Box 真能代表转笔吗？” | 只能代表一部分 object-loaded joint response；不能代表 contact phase 和 object pose dynamics |
| “能不能直接用于 LinkerHand？” | 不能直接；应先做 per-joint / per-finger / whole-hand OOD prediction 对比，再决定 residual 粒度 |
| “它和 tactile 路线冲突吗？” | 不冲突；DexNDM 补 actuator dynamics，tactile 补 contact observability，DNPM 很可能两者都需要 |

---

## References

- Xueyi Liu, He Wang, Li Yi. *DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model*. arXiv, 2025.
- Project website: meowuu7.github.io/DexNDM.
- Hardware: LEAP Hand + Franka Arm.
- Core local links: [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]], [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]], [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]], [[Lessons from Learning to Spin Pens]].
