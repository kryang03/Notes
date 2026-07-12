---
tags:
  - paper
  - dexterous-manipulation
  - in-hand-manipulation
  - tactile-sensing
  - state-estimation
  - reinforcement-learning
aliases:
  - DLR Tactile Manipulation
  - Modular RL Architecture
paper-year: 2023
read-date: 2026-02-01
venue: RA-L 2023
paper-pdf: "[[Papers/Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[SignalProcessing]]"
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
---

# Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture

> [!abstract] 核心贡献
> 这篇论文把倒置手掌中的 cube goal reorientation 写成一个 **belief-state control** 问题：controller 不直接从短历史里“猜”物体状态，而是显式接收一个由 differentiable particle filter 估计出的 cube pose，从而在无外部视觉、永久 force closure、24 个 $\pi/2$ 目标方位的真实 DLR-Hand II 上实现 zero-shot Sim-to-Real。

> [!tip] 与理论基础的关联
> - [[StochasticProcess]] / [[SignalProcessing]] — Bayes filtering：从 $p(s_t\mid z_{1:t},u_{1:t})$ 到粒子集合 $\{w_t^{(i)},s_t^{(i)}\}$，这是本文 DPF 的数学根。
> - [[ReinforcementLearning]] — SAC + asymmetric critic：policy 只拿可部署观测，Q-function 拿 privileged ground-truth state，降低训练方差但不污染部署接口。
> - [[ControlTheory]] — impedance-controlled hand：策略输出 desired joint-angle increment，经 $K_p$ 与 $\tau_{\max}$ 缩放后进入低层阻抗控制。
> - [[ContactMechanics]] — 多接触、摩擦、spinning friction 让解析状态转移不可用，所以需要学习式 belief update。
> - [[StochasticProcess#3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic|StochasticProcess §3.2]] — 挂 **认知不确定性三用** 暗线：DPF 的 belief $b_t(s_t)$ 表达的是对 cube pose 的 epistemic 不确定性；论文 future work"把 estimator uncertainty 喂给 policy"正是"探索/护栏/课程"三用里 policy 侧的缺口。真机 goal 6 更难、$x_3$ weakly observable 都是 belief 多模态/弱可观的具体表现。
> - [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]] — **电流≠关节力矩**暗线：policy 不输出 torque，而输出被 $\tau_{\max}/K_p$ 硬约束的 desired joint increment，经 impedance 层执行；Fig.7 的 spinning friction 敏感说明真机 gap 主要在接触/摩擦而非视觉。
>
> **核心技术**: modular RL, differentiable particle filter, belief-state policy, asymmetric observations, tactile-only Sim-to-Real

## 0. 阅读定位与范本价值

这篇论文对当前知识库的价值不是“又一篇 tactile in-hand manipulation 成功案例”，而是给了一个非常清晰的架构判断：

**当物体状态不可观测、接触动力学不可解析、但任务又必须知道物体是否到达目标时，不要急着把所有东西塞进一个 recurrent policy；先问：是否应该把物体 belief 做成一个显式、可调试、可替换的中间模块。**

它和前面几篇触觉论文的定位不同：

| 论文 | 触觉/状态变量如何进入控制 | 真正回答的问题 |
|---|---|---|
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | dense tactile + moving goal，policy 直接闭环 | 触觉能否让任意轴连续旋转跨重力方向泛化 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | binary full-hand contact 直接给 policy | 1-bit 全手 contact 是否比 continuous force 更好迁移 |
| [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]] | deform map 作为几何公共空间 | tactile sim-to-real gap 能否通过几何表示消掉 |
| [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] | RMA adaptation module 隐式回归 extrinsics latent | 与本文构成"隐式 vs 显式 belief"对照：HORA 让 $\hat z_t$ 隐式吸收 hidden context、不可审计；本文 DPF 把 belief 显式化、可 debug、可传 uncertainty——同一 POMDP 的两种解 |
| **本文** | DPF 显式估计 cube state，再交给 SAC controller | 在没有外部 state 的 goal-reaching 任务里，belief module 是否是更可审计的接口 |

最低标准：

| 支柱 | 本文必须回答的问题 | 本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么 goal reorientation 比无限旋转更需要 state estimator？ | §1.1-1.4 |
| 原理与理论 | DPF 从 Bayes filter 如何一步步来？policy action 为什么写成 $\tau_{\max}/K_p$？ | §2.2-2.5 |
| 实验与验证 | Table III 的 0.68→0.99→0.74→0.76→0.92 到底证明了什么？ | §3.2 |
| 未来与结合 | 这个 modular belief 接口如何迁移到 LinkerHand 转笔 / WMTS？什么时候不该照搬？ | §5-§6 |

## 1. 问题设定与动机

### 1.1 一句话核心

本文解决的是：

> 在手掌朝下、没有外部视觉、只依赖 DLR-Hand II 的本体/力矩相关触觉信息时，如何让多指手把 cube 旋到 24 个离散 $\pi/2$ 目标方位之一，并且知道什么时候已经到达目标。

这里的关键不是“把 cube 转起来”。前作已经能做单轴连续旋转。关键是 **goal-oriented reorientation**：

- 连续旋转只要保持运动趋势，物体一直在动即可。
- goal reorientation 必须判断当前 $R_t$ 和 $R_{\text{goal}}$ 的差距 $\theta=d(R_{\text{goal}},R_t)$。
- 如果没有外部 tracking，$\theta$ 不可直接观测。
- 因此任务从普通 MDP 变成了 POMDP：策略看到的是关节/接触历史，不是 cube state。

这就是为什么状态估计不是“辅助模块”，而是任务定义本身的一部分。

### 1.2 直观隐喻

本文不是给 blindfolded robot hand 加一双眼睛，而是在手指和控制器之间放一个 **可审计的仪表盘**：

- policy 不需要把所有接触历史压成黑箱 hidden state；
- DPF 把“我相信 cube 现在在哪里、朝哪儿、速度如何”显式写成 $\hat{s}_t$；
- 真实机器人失败时，研究者可以直接看 $\hat{x}_t,\hat{R}_t$ 是否漂了，而不是只盯着一个 opaque recurrent hidden state。

这个隐喻的可证伪点是：如果主要失败来自低层接触模型/摩擦，而不是状态不可观测，那么显式 belief 只能帮助 debug，不能自动带来高成功率。Fig. 7 里 spinning friction 的影响正好暴露了这个边界。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| OpenAI Dactyl / vision-based reorientation | 外部视觉或 mocap 提供 object state | 遮挡和真实部署成本高；手朝上时重力帮助保持物体，和本文倒置 force-closure 不同 |
| 前作 DLR tactile spinning | 纯触觉 + torque-controlled hand 可以连续旋转 cube | 连续绕单轴转不等于到达指定姿态；可以“不知道绝对姿态”仍然表现不错 |
| end-to-end recurrent policy | RNN hidden state 自己学 belief | 若真实机器人失败，很难判断是状态估计错、控制错、还是 sim contact model 错 |
| analytic/EKF-style estimator | 显式 dynamics + 局部线性化 | 多接触、摩擦、碰撞切换让 $p(s_t\mid s_{t-1},u_t)$ 非线性、多模态、非光滑 |
| domain randomization brute force | 用大范围随机化覆盖 sim-real gap | friction 范围过宽会让策略在 unrealistically hard domains 上牺牲真实表现；范围过窄又迁移失败 |

### 1.4 Delta 分析

本文的 delta 有四层，必须分开看：

1. **任务 delta**：从前作“绕 vertical axis 无限 spinning”升级到“24 个 $\pi/2$ goal orientations”。这让 object state estimation 从可选变成必需。
2. **传感 delta**：不用外部 camera/mocap，只用 hand 内部 position/torque-related sensing。注意它不是 taxel tactile image，而是 torque-controlled hand 在接触下的本体响应。
3. **架构 delta**：不是让 LSTM policy 自己发明 belief，而是用 DPF 显式估计 cube state，再把 $\hat{s}_t$ 作为 controller observation。
4. **训练 delta**：不是一次训练到底，而是 S1-S5：先用 true state 训 controller，再训 estimator，再 estimator-in-loop 细化 policy。

所以这篇论文讲的故事很明确：

> goal-reaching 需要知道 state；真实 tactile-only 又拿不到 state；contact dynamics 太难写解析 filter；于是用 learning-based particle filter 作为 belief interface，并用 modular curriculum 把 estimator 和 controller 接起来。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_t$ | hand joint angles | robot sensors / simulation | policy input，不对真实传感器求梯度 | 当前实际关节角 | 不是 action；contact 会让 $q_t$ 和 desired angle 产生差 |
| $\bar{q}_{t-1}$ | desired joint angles | previous controller command | policy input | 上一步希望低层 impedance controller 达到的位置 | 论文用 desired angle 作为统一接口，不直接输出 torque |
| $\bar{q}_{t-1}-q_t$ | joint-space error | computed observation | policy input | 接触/阻抗响应的间接触觉线索 | 这比 raw taxel 更隐式；不要误读成视觉 state |
| $R_{\text{goal}}$ | $SO(3)$ / quaternion | task command | fixed per subgoal | 目标 cube orientation | cube 有 octahedral symmetry，实际用 reduced orientation |
| $x_t,R_t$ | $\mathbb{R}^3\times SO(3)$ | simulator ground truth | Q-function privileged input；policy only in early training | cube position/orientation | 真实部署拿不到；不能把它当可部署 observation |
| $\hat{x}_t,\hat{R}_t$ | $\mathbb{R}^3\times SO(3)$ | DPF output | estimator 内部可微；policy 视作输入 | cube state belief / point estimate | estimator error 会直接变成 policy observation noise |
| $R_{\text{sym},t}$ | reduced cube orientation | octahedral symmetry reduction | computed | 消除 cube 24-fold symmetry 下的等价姿态 | symmetry 只适合 cube，不适合任意物体 |
| $R_{\text{goal}}^{-1}R_t$ | relative rotation | computed observation | Q privileged / policy estimated | 当前离目标的姿态差 | 左乘/右乘代表 frame convention，不能随便换 |
| $v_t,\omega_t$ | $\mathbb{R}^3,\mathbb{R}^3$ | simulator / estimator state | Q-function privileged; estimator target | cube linear/angular velocity | policy table 里 Q-function 拿 $v_t$，policy 不拿真实 velocity |
| $s_t$ | $\mathbb{R}^3\times SO(3)\times\mathbb{R}^3\times\mathbb{R}^3$ | hidden object state | estimator target | $(x_t,R_t,v_t,\omega_t)$ | 这是滤波 state，不是 RL full state |
| $z_t$ | joint measurement vector | estimator observation | estimator input | paper writes $z_t=(q_t,\dot{q}_t)$ | DPF 还用 control input $u_t=\bar{q}_t$ |
| $u_t$ | desired joint command | controller output history | estimator input | 解释 observed joint motion 的外部驱动 | 没有 $u_t$，同样的 $q$ 变化无法区分主动运动和接触扰动 |
| $\pi(o_t)$ | normalized action | policy network output | learned by SAC | desired joint-angle increment direction | 经过 $\tau_{\max}/K_p$ 缩放后才变成 desired angle |
| $K_p,\tau_{\max}$ | impedance gain / torque limit | low-level controller / hardware | fixed/randomized | 把 policy output 约束在安全 torque envelope 内 | 不是 RL reward 系数；是 control interface |
| $\eta_{\text{lat}},\eta_{\text{spin}}$ | friction coefficients | domain randomization | sampled env parameter | lateral/spinning friction | Fig. 7 说明 spinning friction 是 sim-real 关键敏感项 |
| $b$ | success rate | benchmark evaluation | metric | 24 goals × 3 friction values × 8 runs 的平均成功率 | Table III 的 $b$ 是 simulation benchmark，不是真机成功率 |

### 2.2 从 POMDP 到 belief-state control

如果 cube state 可观测，任务可以写成标准 MDP：

$$
s_t^{\text{MDP}}=(q_t,\dot{q}_t,x_t,R_t,v_t,\omega_t,R_{\text{goal}}),
\qquad
a_t\sim \pi(a_t\mid s_t^{\text{MDP}}).
$$

但真实设置里没有 external tracking，因此 policy 实际只看到：

$$
o_t=(q_t,\bar{q}_{t-1},\bar{q}_{t-1}-q_t,R_{\text{goal}},\text{history}),
$$

而 cube state 是 hidden variable。于是控制问题更准确地是 POMDP：

$$
s_t \text{ hidden},\qquad z_t \text{ observed},\qquad u_t \text{ commanded}.
$$

从 Bayesian filtering 开始，belief 是：

$$
b_t(s_t)=p(s_t\mid z_{1:t},u_{1:t}).
$$

递推分两步：

**prediction：**

$$
\bar{b}_t(s_t)=\int p(s_t\mid s_{t-1},u_t)b_{t-1}(s_{t-1})\,ds_{t-1}.
$$

**update：**

$$
b_t(s_t)=\eta\,p(z_t\mid s_t,u_t)\bar{b}_t(s_t),
$$

其中 $\eta$ 是归一化常数。

如果 $p(s_t\mid s_{t-1},u_t)$ 和 $p(z_t\mid s_t,u_t)$ 都是线性高斯，Kalman filter 就够了。但本文的 hand-object system 有两个破坏条件：

1. **contact transition 非光滑**：接触点出现/消失会让 dynamics 突变。
2. **shape/contact ambiguity 多模态**：只从手指接触和关节响应看 cube，多个姿态可能解释同一段触觉历史。

因此本文选择粒子滤波：

$$
b_t(s_t)\approx \sum_{i=1}^{N} w_t^{(i)}\delta(s_t-s_t^{(i)}).
$$

粒子滤波的 insight 是：不强迫 belief 是单峰 Gaussian，而是保留一组 hypotheses。对 tactile in-hand manipulation 来说，这比 EKF 的单一均值/协方差更合理。

### 2.3 DPF：把 Bayes filter 的两个模型神经化

论文使用 D2P2F，一种 differentiable particle filter variant。cube hidden state 定义为：

$$
s_t=(x_t,R_t,v_t,\omega_t)^\top
\in \mathbb{R}^3\times SO(3)\times\mathbb{R}^3\times\mathbb{R}^3.
$$

这里：

- $x_t$：cube Cartesian position；
- $R_t$：cube orientation；
- $v_t$：cube lateral velocity；
- $\omega_t$：cube rotational velocity。

标准 particle filter 要手写 motion model 和 observation likelihood：

$$
s_t^{(i)}\sim p(s_t\mid s_{t-1}^{(i)},u_t),
\qquad
w_t^{(i)}\propto w_{t-1}^{(i)}p(z_t\mid s_t^{(i)},u_t).
$$

本文不手写它们，而是学习：

$$
F_\phi(\cdot\mid s_{t-1}^{(i)},z_t,u_t)
\quad\text{and}\quad
G_\phi(s_{t-1}^{(i)},z_t,u_t),
$$

其中：

$$
z_t=(q_t,\dot{q}_t),\qquad u_t=\bar{q}_t.
$$

这两个输入的物理意义很关键：

- $z_t$ 是“手实际发生了什么”；
- $u_t$ 是“controller 想让手发生什么”；
- 两者差异让系统能从 joint response 中读出 contact。

因此本文的“tactile”不是 GelSight/TacTip 那类 image tactile，而是 torque-controlled hand 的 intrinsic tactile information。论文结论不能直接外推到任何有 taxel map 的手，也不能直接外推到没有 torque/impedance quality 的手。

DPF 输出 point estimate：

- particle positions 的 weighted mean；
- particle rotations 的 medoid；
- lateral / rotational velocity 的 weighted mean。

训练 loss 是：

$$
L_\phi=
\frac{1}{T}\sum_{t=1}^{T}\sum_j c_j d_j(\hat{s}_{j,t},s_{j,t})^2,
$$

其中 $d_j$ 对 Euclidean component 是欧氏距离，对 orientation 是 rotation angle distance。论文设置：

$$
c_x=1.0,\qquad c_R=100.0,\qquad c_v=c_\omega=0.1.
$$

这组权重本身就透露了任务偏好：orientation error 比 velocity error 重要得多，因为 goal reorientation 的成功条件主要由 $\theta=d(R_{\text{goal}},R_t)$ 决定。

### 2.4 DPF 训练为什么要三阶段

DPF 不是直接拿最终 policy 的真实部署轨迹训练一次就完事。论文的训练顺序是：

1. **single-particle one-step prediction**：先训练 proposal model 做 $T=1$ 的短期预测，避免一开始就 BPTT 崩掉。
2. **sequence training**：在 $T=100$ timesteps 上 BPTT，让 filter 学会长期 rollout 中的误差积累。
3. **estimator-in-loop data aggregation**：让 policy 用当前 estimator 的 prediction 跑 simulation，把 in-loop 数据追加到 dataset，再训练 2 epochs，反复直到 in-loop/offline data fraction 达到 $1/2$。

这背后的理论原因是 distribution shift：

$$
p_{\text{offline}}(z_{1:T},u_{1:T})
\neq
p_{\text{in-loop}}(z_{1:T},u_{1:T}),
$$

因为 policy 一旦依赖 $\hat{s}_t$，估计误差会改变后续动作，后续动作又改变接触轨迹。只在 true-state policy 生成的数据上训练 estimator，会遇到类似 imitation learning 的 covariate shift。

这也是本文和“纯 supervised estimator”不同的地方：它虽然不是端到端 jointly optimized，但它承认 estimator 和 controller 的闭环数据分布互相影响。

### 2.5 policy action：为什么出现 $\tau_{\max}/K_p$

DLR-Hand II 底层是 high-fidelity impedance control。简化写，一个关节的阻抗力矩近似是：

$$
\tau \approx K_p(\bar{q}-q)+K_d(\dot{\bar{q}}-\dot{q}).
$$

如果忽略速度项，只看 stiffness term，要保证不超过 torque limit：

$$
|\tau|\le \tau_{\max}
\quad\Rightarrow\quad
|K_p(\bar{q}-q)|\le \tau_{\max}
\quad\Rightarrow\quad
|\bar{q}-q|\le \frac{\tau_{\max}}{K_p}.
$$

所以 policy 不直接输出 torque，也不直接输出 arbitrary desired joint angle，而是输出一个 normalized increment：

$$
\tilde{q}_{t+1}
=
\operatorname{clip}
\left(
q_t+\pi(o_t)\frac{\tau_{\max}}{K_p},
q_{\min},
q_{\max}
\right).
$$

这个公式的 value add 很实际：

- policy action 被硬限制在低层 controller 可安全执行的范围；
- desired joint angle 作为统一接口，既能做 free-space motion，也能借 impedance 在 contact 中调力；
- 低频 policy（10 Hz）不需要直接解决高频 torque stabilization。

对 LinkerHand 迁移时，这个公式不能机械照搬。需要先确认 LinkerHand 的底层控制接口是 position、current、torque 还是 hybrid；如果没有稳定的 impedance layer，$\tau_{\max}/K_p$ 这个安全解释就不成立。

### 2.6 reward：从 terminal goal 到增量进步，再到 estimator-aware policy

论文使用两个主要 reward。

初始 goal reward $r_g$ 来自 Chen et al.：

$$
r_g=
\begin{cases}
\lambda_{\text{drop}}, & \text{if drop},\\
\dfrac{\lambda_\theta}{\theta+\epsilon_\theta}
-\operatorname{clip}(\lambda_{\text{pos}}\|x\|,0,\lambda_{\text{clip}})
+\lambda_{\text{succ}}, & \text{if succ.},\\
0, & \text{else}.
\end{cases}
$$

其中：

- $\theta=d(R_{\text{goal}},R_t)$；
- $x$ 是 cube position deviation；
- success 要求 $|x|<2.5\text{ cm}$ 且 $\theta<0.4\text{ rad}$ 保持 400 ms；
- drop 条件包括 cube 掉到 $x_3<-5\text{ cm}$ 或离 origin 超过 10 cm。

后来切换到 simpler reward：

$$
r_s=
\operatorname{clip}(-\lambda'_\theta\Delta\theta,-\infty,\lambda'_{\text{clip}})
-\lambda'_{\text{pos}}\Delta x,
$$

其中：

$$
\Delta\theta_t=\theta_t-\theta_{t-1},
\qquad
\Delta x_t=\|x_t\|-\|x_{t-1}\|.
$$

这个 reward 的逻辑比 $r_g$ 更适合 Sim-to-Real：

- 它奖励“每一步让 orientation error 下降”，不是只奖励 terminal success；
- 位置项约束 cube 不要偏离；
- step reward 被 clipping，迫使策略在 randomized domains 中学稳健进步，而不是在某些容易环境中拿极高回报。

最终 estimator-in-loop 阶段加入 estimator-aware term：

$$
r_e = r_s + \text{clipped estimator-error term}.
$$

论文文字明确说这是为了惩罚 estimation error、鼓励 policy 选择可预测的 state transitions。这里读公式时要注意：如果实现中写成加号，则相应系数/优化约定必须让它成为 penalty；把它理解为“奖励估计误差”会和论文语义矛盾。

这个设计的真正含义是：

> controller 不只要完成任务，还要避免把系统带到 estimator 难以解释的接触状态。

这对转笔很重要。高速 aerial/sliding contact 可能短期提高旋转速度，但如果 belief estimator 完全丢失 phase，后续控制会崩。

### 2.7 asymmetric observations：训练可以 privileged，部署不能 privileged

Table I 的核心不是“观测很多”，而是 **Q-function 和 policy 观测被刻意分开**：

| Name | Q-function | Policy |
|---|---|---|
| Joint angles | $q_t$ | $q_t$ |
| Desired angles | $\bar{q}_{t-1}$ | $\bar{q}_{t-1}$ |
| Control error | $\bar{q}_{t-1}-q_t$ | $\bar{q}_{t-1}-q_t$ |
| Goal orientation | $R_{\text{goal}}$ | $R_{\text{goal}}$ |
| Cube state | $(x_t,R_{\text{sym},t})$ | $(\hat{x}_t,\hat{R}_{\text{sym},t})$ |
| Delta rotation | $R_{\text{goal}}^{-1}R_t$ | $R_{\text{goal}}^{-1}\hat{R}_t$ |
| Cube linear velocity | $v_t$ | not deployed as true state |

完整输入是长度 $S=5$ 的 time stack。policy rate 是 10 Hz，所以 history window 是 0.5 s。旧稿里若写成 20 Hz/10 frames，是把 frequency 和 stack length 混了。

asymmetric critic 的意义：

$$
Q_\psi(o_t^{Q},a_t)
\quad\text{can use privileged true state in simulation,}
$$

但 actor 部署时只用：

$$
\pi_\theta(a_t\mid o_t^{\pi}),
\quad
o_t^\pi \text{ contains estimated state, not true state.}
$$

这降低训练难度，但不会在真实机器人上引入不可用输入。对 WMTS 的 PPO Oracle 也一样：critic 可以 privileged，actor 不可以。

### 2.8 cube symmetry：24 个目标不是任意 SO(3)

cube 的 orientation 有 octahedral group symmetry。论文把 cube orientation reduced to $R_{\text{sym}}$，目标是 24 个 $\pi/2$ raster orientations。

这既是优势也是边界：

- 优势：减少等价姿态带来的多值歧义，policy/estimator 的目标更清楚。
- 边界：这不是任意物体的 continuous SO(3) reorientation；对于笔、工具、非对称物体，symmetry group 不同甚至不存在。

因此这篇论文对转笔的启发不是“用 24 类姿态分类”，而是“把任务相关的 hidden state 显式化”。对笔来说，hidden state 更可能是：

$$
(\text{axis line},\text{spin phase},\omega,\text{contact mode},\text{slip velocity}),
$$

而不是 cube 的 24-fold orientation class。

### 2.9 整体训练算法机制

本文不是端到端一把梭，而是一个 staged modular pipeline：

| Step | 训练内容 | policy 输入 | benchmark success $b$ | 机制解释 |
|---|---|---|---:|---|
| S1 | train policy $\pi_{00}$ on $r_g$ | true cube state | 0.68 | terminal/goal reward 可启动，但不够稳健 |
| S2 | refine policy on $r_s$ to $\pi_0$ | true cube state + noise | 0.99 | 增量 reward 让策略学到跨随机域的稳健进步 |
| S3 | train estimator $f_0$ on data from $\pi_0$ | estimator used for benchmark | 0.74 | estimator 加入后 performance 大跌，说明 state estimation 是瓶颈 |
| S4 | iteratively refine estimator $f_i$ with in-loop data | estimator in-loop | 0.76 | estimator distribution shift 被部分缓解，但 policy 还未适应估计误差 |
| S5 | refine policy on $r_e$ to $\pi_1$ with $f_i$ in-loop | estimator in-loop | 0.92 | policy 学会和 estimator 共同工作，接近可部署闭环 |

Table III 是这篇论文最核心的 evidence。它说明：

- controller 如果拿 true state，任务几乎可解（0.99）；
- 直接换成 estimator，成功率掉到 0.74；
- 单独把 estimator 变准，只带来 0.74→0.76 的小提升；
- 真正恢复性能的是 **policy with estimator-in-loop fine-tuning**（0.76→0.92）。

这不是“估计器越准越好”这么简单，而是 **controller 必须适应 belief 的误差结构**。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设置 |
|---|---|
| Robot | DLR-Hand II，4 指，每指 3 active joints + 1 passive joint |
| Hand pose | upside down，必须永久 force closure |
| Task | cube reorientation to 24 $\pi/2$ goal orientations |
| Sensors | integrated position and torque sensors；policy/estimator 主要用 joint/desired-angle/history 信号 |
| Low-level control | high-fidelity impedance control |
| Policy rate | 10 Hz |
| Estimator rate | 100 Hz |
| Policy network | simple MLP, 2 layers, 512 units |
| RL algorithm | Soft Actor-Critic, PyBullet simulation |
| Parallel simulation | 120 workers |
| Replay buffer | 1.5M steps |
| Observation stack | $S=5$ frames = 0.5 s |
| DPF sequence training | $T=100$ timesteps BPTT |
| Training compute | around two weeks on machines up to 80 cores |

这个 setup 有两个现实含义：

1. 它不是轻量方法。训练靠大量并行仿真和 staged curriculum。
2. 它的 real-world success 不是“真实在线 RL”，而是 simulation training + zero-shot transfer。

### 3.2 Domain randomization

论文真正重视的 randomization 不是一个笼统 DR 列表，而是围绕 tactile/contact gap：

| Parameter | Distribution | Notes |
|---|---|---|
| joint angle noise $q$ | $\mathcal{N}(0,0.02)$ per step | policy sensor noise |
| cube position noise $x$ | $\mathcal{N}(0,0.01)$ per step | S4/S5/benchmark off |
| cube orientation noise $R$ | $\mathcal{N}(0,0.2)$ per step | S4/S5/benchmark off |
| joint offset $q_{\text{off}}$ | $\mathcal{U}(-0.04,0.04)$ per episode | calibration/offset gap |
| lateral friction $\eta_{\text{lat}}$ | $\mathcal{U}(0.81,0.99)$ | contact tangential behavior |
| spinning friction $\eta_{\text{spin}}$ | $\operatorname{LogU}(2\times10^{-4},2\times10^{-2})$ | benchmark fixes selected values |

其他随机化还包括 sticky actions、$K_p/K_d$、parasitic stiffness、cube mass/size/initial pose、random forces and torques。

因果解释：

- joint/pose noise 测试 policy 对 sensing error 的稳健性；
- controller randomization 测试低层 impedance 和通信延迟 gap；
- cube/friction randomization 测试 contact dynamics gap；
- spinning friction 被单独强调，是因为 cube 被两指夹持时，高/低 spinning friction 会导致完全不同的 qualitative behavior：卡住或摆落。

### 3.3 Table III：训练序列是最强实验

| Step | 训练阶段 | benchmark success $b$ | 证明了什么 |
|---|---|---:|---|
| S1 | $r_g$ + true cube state | 0.68 | goal reward 可启动，但还没有可靠跨域策略 |
| S2 | $r_s$ + true cube state | 0.99 | simpler dense incremental reward 解决了大部分控制问题 |
| S3 | train estimator, policy uses $f_0$ | 0.74 | estimator error 是从 sim policy 到可部署 policy 的主要落差 |
| S4 | estimator in-loop refinement | 0.76 | estimator 数据分布修正有用但不足 |
| S5 | policy refined with estimator-in-loop and $r_e$ | 0.92 | controller 必须适应 estimator 的误差形态，模块组合才真正闭环 |

这张表的 critical reading：

- 如果只看 S2，会误以为 task 已经解决；
- 如果只看 S3/S4，会误以为 estimator 不够准；
- S5 说明核心不是 estimator 单模块精度，而是 **estimator-policy co-adaptation**。

对 WMTS 来说，这直接对应：

> world model / state estimator 不应该只用 one-step prediction loss 选最好；必须看 policy-in-the-loop 后闭环性能是否恢复。

### 3.4 Benchmark protocol 与真实机器人结果

仿真 benchmark：

| 项目 | 设置 |
|---|---|
| Goals | 24 goal orientations |
| Friction values | $\eta_{\text{spin}}\in\{2\times10^{-4},10^{-3},10^{-2}\}$ |
| Runs | 8 runs per goal-friction combination |
| Total | $24\times3\times8=576$ episodes |
| Other DR | still active, but cube size fixed nominal 8 cm |
| Best deployed policy | $\pi_1$ with estimator in-loop |
| Reported success | 92% |

真实机器人：

| 项目 | 设置 / 结果 |
|---|---|
| Policy | $\pi_1$ zero-shot transferred |
| Trials | 4 runs per goal orientation |
| Evaluation | qualitative success per goal because no external tracking for reward computation |
| Headline | all 24 goal orientations could be reached with high success rate |
| Important caveat | some goals that look easy in simulation are harder on real robot, e.g. goal 6 |

因果解释：

- “all 24 goals reached” 支持 modular tactile-only state estimation 的可行性；
- “some sim-easy goals fail more in real” 反过来说明 simulator contact model 仍然是瓶颈；
- 真实实验没有 external tracking，所以不能像仿真那样给精确 reward/pose error，只能按 goal-level trial success 定性/半定量评估。

这不是论文弱点，而是这类 tactile-only 设置的真实代价：如果坚持不用外部传感器，评估本身也会更难。

### 3.5 Estimator evaluation：Fig. 4 / Fig. 5 的含义

Fig. 4 显示 estimator prediction error 在 iterative in-loop training 中下降。论文的关键解释是：

- estimator 已经在 offline data 上 train until convergence；
- 但 in-loop data 加入后仍能降低 error；
- 这说明 estimator 的错误不是纯容量问题，而是 data distribution 问题。

Fig. 5 里 $x_3$ position error 会随时间积累。原因很具体：

> cube 被四侧夹住时，height 不能唯一确定；只有当 finger 接触到 cube upper edge 时，才能推断 $x_3$。

这条 observation 很重要，因为它把 “tactile state estimation is hard” 从口号变成了具体不可观测性：

- 有些 state component 在当前 contact geometry 下就是 weakly observable；
- 再大的网络也不能从没有信息的接触模式中恢复唯一高度；
- 需要主动触碰 upper edge 或设计 information-gathering motion。

对 WMTS 的启发是：latent task scheduler 不应只生成完成任务的动作，也应生成让 hidden state 变可观测的 probing subtask。

### 3.6 Fig. 7：spinning friction 是 Sim-to-Real 的真正痛点

Fig. 7 把 $\pi_1$ 在不同 spinning friction values 下的 24-goal benchmark success 画出来。论文观察：

- policy 在较低 friction 端表现显著更好；
- 较高 spinning friction 会让任务变难；
- 即使训练时采样了宽范围 friction，policy 也不能在整个范围 equally generalize。

这条结果的意义比“randomize friction 很重要”更尖锐：

> DR 不是越宽越好。如果随机域包含大量真实机器人不会出现、但任务极难的 configuration，policy 可能把容量花在错误区域；如果不覆盖真实 gap，又会迁移失败。

这和 WMTS 的 ensemble world model 逻辑一致：我们不只要随机化，还要知道当前模型在哪些 contact modes 上不确定，以及哪些不确定性是真实风险、哪些只是过宽 DR 制造的虚假困难。

### 3.7 Ablation / 因果链重写

论文没有给传统 “remove module” 大表，但 Table III、Fig. 4、Fig. 7 已经构成了足够强的 causal evidence：

| 变化 | 指标变化 | 因果机制 | 对使用者的含义 |
|---|---|---|---|
| $r_g$ policy → $r_s$ policy | 0.68 → 0.99 | dense incremental reward 更稳定地奖励接近目标和保持位置 | 对复杂接触任务，reward shaping 应优先奖励可持续 progress |
| true state policy → estimator input | 0.99 → 0.74 | belief error 直接污染 policy observation | 只在 privileged state 下成功不代表可部署 |
| offline estimator → in-loop refined estimator | 0.74 → 0.76 | distribution shift 缓解，但 policy 未适应 estimator error | 单独优化 estimator loss 不够 |
| estimator-in-loop policy fine-tuning | 0.76 → 0.92 | policy 学会选择 estimator 可预测的 transitions | controller 和 estimator 要共同闭环验证 |
| varying spinning friction | success strongly changes | contact dynamics qualitative mode 变化 | Sim-to-Real 的核心 gap 是 contact/friction，不是视觉缺失 |

这篇论文最值得复刻的实验不是“24 goals reached”，而是这条训练表：它把模块化每一步的收益和断点都暴露出来了。

## 4. 核心洞见

### 4.1 真正的 insight：belief 是一个工程接口，不只是数学对象

Bayes filtering 在数学上是估计 $p(s_t\mid z_{1:t},u_{1:t})$。本文的 insight 是把它变成机器人学习中的工程接口：

- 对 controller：belief 提供 task-relevant object state；
- 对 researcher：belief 提供可视化 debug 信号；
- 对 training：belief 把 policy 从长期 history compression 中解放出来；
- 对 Sim-to-Real：belief 暴露了 sim contact model 和 real contact behavior 的 mismatch。

这比“模块化更可解释”更具体。可解释性不是哲学优点，而是当 real robot 失败时，你能看见 $\hat{R}$ 是否跳到了错误 face、$\hat{x}_3$ 是否漂、某个 goal 是否利用了 unreal contact。

### 4.2 为什么这个设计有效

本文有效的前提有四个：

1. **任务 state 低维且明确**：cube pose/velocity 是合理 abstraction。
2. **手本身提供可用 tactile signal**：torque-controlled DLR-Hand II 的 actual/desired joint behavior 包含 contact 信息。
3. **低层控制足够稳定**：10 Hz policy 通过 impedance interface 可以安全执行。
4. **sim 能生成足够覆盖的 estimator data**：DPF 训练需要大量有 ground-truth state 的 simulated rollouts。

如果这四个条件成立，模块化比 end-to-end RNN 更有优势，因为它把函数分解为：

$$
\text{history}\to \hat{s}_t,
\qquad
(\hat{s}_t,R_{\text{goal}},q_t)\to a_t.
$$

这比直接学：

$$
\text{history},R_{\text{goal}}\to a_t
$$

更容易 debug，也更容易在 sim-to-real 中定位问题。

### 4.3 什么时候会失效

这个方法不是万能 tactile manipulation recipe。它会在以下条件下变弱：

- hidden state 不是低维 pose，而是高维 deformable state；
- tactile observation 对关键 state 不可观测，且没有主动 probing；
- contact dynamics 比 cube reorientation 更快，比如转笔中的 aerial phase；
- 机器人没有可靠 impedance/torque sensing，actual-vs-desired joint response 不含稳定 tactile 信息；
- object geometry/symmetry 不是已知 cube，不能用 $R_{\text{sym}}$ 简化；
- estimator uncertainty 没有传给 policy，policy 把错误 point estimate 当真。

最后一点是论文自己也承认的 future work：把 estimator uncertainty 作为 policy input。对当前 WMTS，这一点应当直接吸收。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 根因 | 为什么重要 |
|---|---|---|
| DPF 输出主要作为 point estimate | policy 没有显式消费 full particle belief / uncertainty | 当 belief 多模态时，均值/medoid 可能掩盖危险 |
| cube symmetry 强先验 | $R_{\text{sym}}$ 依赖 octahedral group | 不能直接迁移到笔、工具、非规则物体 |
| state definition 手工指定 | $s_t=(x,R,v,\omega)$ | 若任务关键变量是 slip/contact mode/material deformation，state 不完整 |
| observation weak observability | 四侧接触无法唯一确定 $x_3$ | 需要主动信息采集，而不仅是被动滤波 |
| no analytic contact model | 用 DPF 学 proposal/update | 可迁移性受 sim contact distribution 限制 |

### 5.2 算法维度

| 替代方案 | 可能优势 | 相对本文的风险 |
|---|---|---|
| recurrent SAC / PPO policy | 不需要手工 state estimator | hidden state 不可审计；real failure 难定位 |
| end-to-end estimator-policy training | 可能更高最终性能 | credit assignment 更难，容易让 estimator 学 task-specific shortcut |
| ensemble world model belief | 能表达 model uncertainty | 比 DPF 更重，需要防止 model exploitation |
| tactile representation learning | 可适配高维 taxel map | 不一定提供 task-level pose/phase 可解释状态 |
| analytic contact filtering | 物理可解释 | 多接触摩擦参数难准，EKF/UKF 易被非光滑切换破坏 |

### 5.3 工程/实验维度

- 训练约两周、最高 80 cores，不是低成本 pipeline。
- 真实实验每 goal 4 次，且无外部 tracking，统计强度有限。
- policy 对 spinning friction 敏感，说明 sim contact fidelity 仍是主要瓶颈。
- DLR-Hand II 的 torque-controlled hardware quality 是方法成立的一部分，不是所有灵巧手默认具备。
- reward/curriculum 多阶段手工设计，距离自动化 task learning 还有距离。
- estimator uncertainty 未进入 policy；真实部署时 overconfident wrong estimate 可能造成失败。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔的直接迁移

这篇论文最值得迁移的是 **显式 belief module**，不是 cube symmetry，也不是 24-goal setting。

| DLR cube reorientation | LinkerHand / 转笔可迁移版本 | 是否应照搬 |
|---|---|---|
| $x_t,R_t$ cube pose | pen axis line、center、spin phase、angular velocity | 迁移 abstraction，不迁移具体变量 |
| $R_{\text{goal}}$ | scheduler 给出的 target phase / target contact mode / target angular velocity | 可迁移 |
| $R_{\text{goal}}^{-1}R_t$ | phase error、axis error、energy error | 可迁移 |
| $z_t=(q_t,\dot q_t)$ | LinkerHand $q,\dot q$、motor current、tactile $5\times12\times6$、contact events | 扩展，不照搬 |
| $u_t=\bar q_t$ | previous action / desired tendon-motor command / low-level target | 可迁移 |
| $R_{\text{sym}}$ | pen symmetry: rotation around long axis may be visually/tactually ambiguous | 需重新定义 symmetry |
| DPF particles | belief over pen phase/contact mode | 可迁移，但要评估实时性 |
| 10 Hz policy | 转笔可能需要更高 frequency 或 lower-level reflex | 不能照搬 |

一个可行架构是：

$$
\text{tactile/proprio/history}
\xrightarrow{\text{belief estimator}}
\hat{b}_t(\text{pen axis},\text{phase},\omega,\text{contact mode})
\xrightarrow{\text{PPO Oracle / controller}}
a_t.
$$

关键是 belief estimator 不应只输出 point state。对转笔，phase/contact mode 经常多模态，至少应该输出：

- mean estimate；
- uncertainty/confidence；
- top-k particle modes 或 contact-mode probabilities；
- belief age / last reliable contact event。

### 6.2 对 WMTS 的结合

WMTS pipeline 可以这样吸收本文：

| WMTS 模块 | 从本文吸收什么 | 具体实现建议 |
|---|---|---|
| latent task generation | 生成 not only task goals but information-gathering subgoals | 当 belief uncertainty 高时，调度 probing/contact-reset subtask |
| PPO Oracle | 用 privileged critic + deployable actor | critic 可拿 sim ground-truth pen state；actor 只能拿 estimator belief |
| Diffusion/Flow generalist | 学 belief-conditioned action chunks | condition 不只包括 observation，还包括 belief mean/uncertainty/contact mode |
| Ensemble World Model | 预测 belief dynamics 而不是 only state dynamics | ensemble disagreement 用于判断 estimator unreliable / contact model mismatch |
| real-robot fine-tuning | estimator-in-loop adaptation | 不要只 fine-tune policy；同时评估 estimator drift 和 policy adaptation |

最重要的一条：

> 不要让 world model 或 task scheduler 直接依赖不可部署的 simulator state。所有 privileged state 只能留在 critic、supervision、diagnostic 和 offline label 中。

这正是本文 asymmetric observation 的价值。

### 6.3 对转笔任务的必要扩展

如果把本文用于 DNPM / 转笔，至少需要三处扩展：

1. **从 quasi-static cube contact 到 dynamic pen contact**
   - cube reorientation 多数时间保持 force closure；
   - 转笔可能包含 rolling、sliding、aerial micro-phase；
   - estimator state 必须显式含 contact mode 和 angular velocity。

2. **从 24-goal orientation 到 phase/skill scheduler**
   - 转笔不是到达某个静态姿态就结束；
   - scheduler 可能要在 charge / sonic / around / catch 等 skill phases 间切换；
   - belief state 要支持 phase-conditioned policy。

3. **从 point estimate 到 uncertainty-aware control**
   - cube 任务中错误 estimate 会让某个 goal 失败；
   - 转笔中错误 phase 可能直接导致 drop；
   - policy 必须知道“我是否不确定”，并有 recovery behavior。

### 6.4 可验证实验建议

可以在当前知识库里设计一组逐层实验：

| 实验 | Baselines | 关键指标 | 可证伪机制 |
|---|---|---|---|
| belief module 是否有用 | RNN policy vs DPF/belief + MLP policy | success, drop rate, phase error, recovery time | 若 RNN 同样可解释且迁移更好，显式 belief 价值下降 |
| estimator-in-loop 是否必要 | offline estimator only vs in-loop DAgger-style estimator data | real/sim closed-loop success | 若 estimator loss 降低但 policy success 不升，说明 loss 与控制目标错位 |
| uncertainty 是否有用 | point estimate vs belief mean+variance/particles | high-speed phase recovery | 若 uncertainty 不改善 failure recovery，说明 policy 没用上 belief |
| tactile modality 是否关键 | proprio only vs proprio+taxel vs proprio+current | state error / control success | 若 proprio only 足够，tactile array 可能不是瓶颈 |
| friction/domain gap | fixed friction vs DR vs adaptive DR / ensemble LCB | sim-real drop | 若 wide DR 反而伤 real，说明需要 uncertainty-guided DR 而非盲目扩宽 |

### 6.5 不应过度外推的点

- 不要把 “purely tactile” 理解成“任何触觉输入都能 work”。本文依赖 DLR-Hand II 的 torque-controlled hand quality。
- 不要把 24-goal cube success 外推到任意物体 continuous reorientation。
- 不要把 DPF 当作比 RNN 永远更好；当 state 不可清晰定义或 tactile 信号太弱时，显式 filter 会变成错误瓶颈。
- 不要只复刻 staged training，而忽略 Table III 的教训：每一步都必须有 benchmark 证明它真的弥合了哪个 gap。

## 7. 与知识体系的联系

### 7.1 与 [[StochasticProcess]] / [[SignalProcessing]] 的联系

本文是 Bayes filtering 在 dexterous manipulation 中的实例：

$$
p(s_t\mid z_{1:t},u_{1:t})
\approx
\sum_i w_t^{(i)}\delta(s_t-s_t^{(i)}).
$$

区别在于 transition/update model 不是解析概率模型，而是 learned proposal/update functions。它可以作为知识库中“belief-state estimation under contact partial observability”的代表论文。

### 7.2 与 [[ReinforcementLearning]] 的联系

本文使用 SAC，但最值得记的是 asymmetric observation：

$$
Q(o^Q,a) \text{ uses privileged state},
\qquad
\pi(a\mid o^\pi) \text{ uses deployable estimated state}.
$$

这对 PPO Oracle 同样成立。训练时给 critic 更多信息是可以的，但 actor 输入必须严格遵守真实部署条件。

### 7.3 与 [[ControlTheory]] 的联系

Eq. (1) 把 RL action 放进 impedance controller 的安全 envelope：

$$
\tilde{q}_{t+1}
=
\operatorname{clip}
\left(q_t+\pi(o_t)\frac{\tau_{\max}}{K_p},q_{\min},q_{\max}\right).
$$

这说明很多 Sim-to-Real 成功不是 policy 单独完成的，而是 policy + low-level controller + action parameterization 共同完成的。

### 7.4 与 [[ContactMechanics]] 的联系

Fig. 7 的 spinning friction 分析是这篇论文最有 contact-mechanics 味道的部分。它告诉我们：

- lateral friction 和 spinning friction 会改变接触模式；
- 两指夹持时微小 spinning friction 差异会导致 stuck / swing-down 这类 qualitative behavior；
- DR 只能覆盖一部分 gap，不能替代 contact model 诊断。

### 7.5 与 WMTS 论证线的联系

本文应该放入 WMTS 的 “belief / estimator / world-model interface” 论证线：

- 它支持 **模块化接口**：先把 hidden physical state 变成 belief，再交给 policy。
- 它支持 **in-loop verification**：estimator loss 好不等于 closed-loop success 好。
- 它支持 **privileged critic**：训练可以用真 state，但部署路径必须干净。
- 它也提醒 **single point estimate 不够**：未来 WMTS 应把 uncertainty 传给 scheduler / policy。

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “为什么 goal reorientation 必须估计 state？” | 连续旋转和 goal reaching 的信息需求不同；后者必须知道 $\theta=d(R_{\text{goal}},R_t)$ |
| “DPF 和普通 particle filter 差在哪？” | Bayes recursion 不变，proposal/update model 被 learned functions 替代，并可通过 sequence loss 训练 |
| “Table III 真正证明了什么？” | 证明 bottleneck 不是 controller alone，而是 estimator-policy co-adaptation |
| “为什么 0.99 到 0.74 掉这么多？” | true state policy 换成 estimated state 后，belief error 进入 actor observation |
| “为什么 S4 estimator 变好但 success 只 0.02 提升？” | estimator metric 与 closed-loop control metric 不完全对齐，policy 还没适应估计误差 |
| “对转笔最该迁移什么？” | belief-state interface、asymmetric critic、estimator-in-loop fine-tuning，而不是 cube symmetry/24 goals |
| “最大风险是什么？” | 高速接触状态不可观测或 belief 多模态时，point estimate 会误导 policy |

## References

- Johannes Pitz, Lennart Röstel, Leon Sievers, Berthold Bäuml. *Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture*. arXiv:2303.04705, 2023.
- Jonschkowski et al. *Differentiable Particle Filters: End-to-End Learning with Algorithmic Priors*. RSS 2018.
- Röstel et al. *Learning a State Estimator for Tactile In-Hand Manipulation*. 2022.
