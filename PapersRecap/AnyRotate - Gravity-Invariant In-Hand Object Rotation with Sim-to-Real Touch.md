---
tags:
  - paper
  - dexterous-manipulation
  - tactile-sensing
  - sim-to-real
  - in-hand-manipulation
  - reinforcement-learning
aliases:
  - AnyRotate
paper-year: 2024
read-date: 2026-02-01
venue: CoRL 2024
paper-pdf: "[[Papers/AnyRotate Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
---

# AnyRotate: Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch

> [!abstract] 核心贡献
> AnyRotate 提出一个统一策略，使 16-DoF Allegro Hand + 4 个视觉触觉指尖能在任意期望旋转轴和不同手朝向下进行 in-hand object rotation：它把连续旋转转写为 moving auxiliary goal reorientation，以 dense tactile features（contact pose $(R_x,R_y)$ + contact force magnitude $\|F\|$）替代 binary/discrete touch，并通过 teacher-student distillation 把带 privileged object/gravity/goal information 的 PPO teacher 蒸馏成只依赖本体+触觉历史的 student；真实端用 tactile perception model 从触觉图像预测显式接触特征，实现 10 个未见物体上的 zero-shot sim-to-real。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 这是 goal-conditioned PPO + privileged teacher / student distillation；auxiliary goal 是探索友好的任务重写，不应过度说成严格不改变最优策略的 potential shaping。
> - [[ContactMechanics]] — dense touch 把接触降维为 contact pose 和 force magnitude；它比 binary touch 更接近滑移/接触边界，但仍缺切向剪切和多点接触。
> - [[SignalProcessing]] — raw TacTip/DigiTac-style optical tactile image 经灰度处理、SSIM contact mask 和 CNN 预测接触特征。
> - [[RepresentationLearning]] — 可迁移单元不是原始触觉图像，而是显式物理中间表征 $(P,F)$。
> - [[ControlTheory]] — policy 输出相对关节位置，经 EMA 平滑后由 300Hz PD controller 执行；策略不是 torque controller。
>
> **核心技术**: Dense Featured Touch, Auxiliary Goal Formulation, Gravity-Invariant In-Hand Rotation, Teacher-Student Distillation, Sim-to-Real Tactile Perception, PPO

## 0. 阅读定位与范本价值

AnyRotate 是触觉灵巧操作簇中非常接近“转笔”但仍有关键差异的一篇。它已经走出 palm-up 单轴旋转，进入：

- 任意旋转轴 $\hat k$；
- 多个手朝向相对重力；
- 真实未见物体；
- 触觉 sim-to-real；
- moving hand / rotating hand 的部署示例。

但它仍然是 stable precision grasp 下的 in-hand object rotation，不是无支撑、带 aerial phase 的高速 pen spinning。对你的 WMTS / LinkerHand 项目，它最有价值的不是“直接复刻任务”，而是三条设计原则：

1. **连续旋转奖励要改写成可达子目标**，否则 angular velocity reward 在多轴/重力扰动下容易卡住。
2. **触觉不要过早二值化**；contact pose + force magnitude 的 dense features 明显提高 OOD mass/shape 和 real-world robustness。
3. **重力不变性不能靠 palm-up 训练外推**；必须在训练中让策略经历不同 hand orientation / gravity-in-hand-frame。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 本文的优势是“任意轴 + 任意手朝向 + dense tactile sim-to-real”的组合 |
| 原理与理论 | §2 | 从 goal-conditioned MDP、EMA action、auxiliary goal、dense tactile、teacher-student loss 推导 |
| 实验与验证 | §3 | Table 1-3 证明 dense touch 在 OOD mass/shape、手朝向、旋转轴上均优于 proprio/binary |
| 未来与结合 | §5-§7 | 对转笔要保留 auxiliary subgoal 思想，但必须扩展到高速接触切换、切向滑移和更高控制频率 |

## 1. 问题设定与动机

### 1.1 一句话核心

AnyRotate 要解决的是：机器人手如何在没有支撑面的情况下，面对任意重力相对方向和任意目标旋转轴，利用触觉维持稳定抓持并连续旋转物体。

### 1.2 直观隐喻

Palm-up rotation 像把物体放在手心托着转；gravity 帮你把物体压进手里。Palm-down 或 thumb-up rotation 像在空中用指尖夹着物体转；重力随时把物体拉出接触。AnyRotate 的策略必须像人手一样，一边转、一边摸、一边补救即将滑走的接触。

Dense touch 在这里不是“额外传感器”，而是策略的报警系统：当接触跑到边界、力幅度异常、接触姿态周期变化被破坏时，手指能做 reactive finger-gaiting。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 |
|---|---|---|
| HORA / RMA-style proprioception | 用历史本体推断隐变量 | 没有局部触觉，无法直接看到指尖接触边界和滑移前兆 |
| RotateIt / vision+touch rotation | 多模态感知支持 general rotation | 多轴/不同轴常需要分别处理；对 gravity-invariant moving hand 不是核心 |
| Touch Dexterity / purely tactile rotation | 强调触觉在 in-hand rotation 中的价值 | 常限于主轴或较低维 tactile representation |
| Binary touch | 只知道接触有/无 | 不知道接触在指尖哪里、力多大、是否逼近边缘 |
| Raw tactile image sim-to-real | 保留高分辨率触觉图像 | 触觉图像 domain gap 大，实时渲染/迁移成本高 |
| Angular velocity reward | 直接奖励 $\omega\cdot \hat k$ | 多轴稳定抓持早期 reward noisy，容易学成“抓稳但不转” |

### 1.4 Delta 分析

| 维度 | 前人常见做法 | AnyRotate 的增量 |
|---|---|---|
| 旋转目标 | 单轴或分轴策略 | 统一策略 conditioned on desired rotation axis $\hat k$ |
| 重力 | palm-up 为主 | 训练随机化 hand orientation，评测 6 个 key orientations |
| 触觉 | binary contact / discrete contact location | contact pose $(R_x,R_y)$ + force magnitude $\|F\|$ |
| 奖励 | angular velocity reward | moving auxiliary goal + keypoint distance + goal bonus |
| sim-to-real | 端到端 tactile image 或 low-dim contact | tactile perception model 预测物理中间特征 |
| 部署 | 静态手姿态 | 展示 rotating hand / changing gravity vector in hand frame |

这篇论文讲故事最有力的地方，是 Table 1-3 都在回答同一个机制问题：**更细的触觉接触信息是否真的让策略更稳？** 答案是 yes，但边界也清楚：尖角/边缘物体仍困难，Allegro Hand 在某些 orientation 下 actuation 明显弱。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $q_t$ | $\mathbb R^{16}$ | Allegro joint observation | 否 | 当前关节位置 | student/real 可见 |
| $\bar q_t$ | $\mathbb R^{16}$ | target joint command state | 否 | EMA 后的目标关节位置 | 不是 object goal；是 hand joint target |
| $a_t$ | $\mathbb R^{16}$ | policy output | 是 | 相对关节位置增量 $\Delta\theta$ | 限制在 $[-0.026,0.026]^{16}$ rad |
| $\tilde a_t$ | $\mathbb R^{16}$ | EMA action | 计算图中间量 | 平滑后的动作增量 | $\tilde a_t=\eta a_t+(1-\eta)a_{t-1}$ |
| $fp_t$ | $\mathbb R^{12}$ | forward kinematics | 否 | 4 指尖位置 | 真实端由 FK 算 |
| $fo_t$ | $\mathbb R^{16}$ | forward kinematics | 否 | 4 指尖姿态 | 每指四元数或等价姿态表示 |
| $c_t$ | $\{0,1\}^4$ | tactile contact detection | 否 | 4 指尖 binary contact | 真实端 SSIM threshold 0.6；仿真 force threshold 0.25N |
| $P_t$ | $\mathbb R^8$ | sim contact / tactile CNN | CNN 有梯度 | 4 指尖 contact pose $(R_x,R_y)$ | 姿态角范围约 $[-28^\circ,28^\circ]$，不是接触点三维位置 |
| $F_t$ | $\mathbb R^4$ | sim contact / tactile CNN | CNN 有梯度 | 4 指尖 contact force magnitude | 来自 $F_x,F_y,F_z$ 的 magnitude，丢切向方向 |
| $\hat k$ | $S^2$ | task command | 否 | desired rotation axis | 指令轴，不等于当前实际旋转轴 |
| $g$ | goal pose | auxiliary goal generator | 否 | 当前 moving object reorientation target | 达到后刷新 |
| $z_t$ | $\mathbb R^8$ | student TCN encoder | 是 | 从历史本体+触觉预测的 latent | student 部署可用 |
| $\bar z_t$ | $\mathbb R^8$ | teacher privileged encoder | detached supervision | privileged latent target | student loss 的监督，不可在真实部署访问 |
| $\hat g_{\mathrm{gravity}}$ | $\mathbb R^3$ | privileged information | 否 | gravity vector in simulation | paper 说显式给 policy 没明显收益，history 可隐式推断 |

### 2.2 Goal-conditioned MDP

论文定义 finite-horizon goal-conditioned MDP：

$$
\mathcal M=(\mathcal S,\mathcal A,\mathcal R,\mathcal P,\mathcal G).
$$

策略：

$$
\pi_\theta(a_t|s_t,g).
$$

目标是最大化：

$$
\mathbb E_{\tau\sim p_\pi(\tau),g\sim q(g)}
\left[
\sum_{t=0}^{T}\gamma^t r(s_t,a_t,g)
\right].
$$

Real-world observation 包括：

| 类别 | 变量 | 维度 |
|---|---|---:|
| Proprioception | joint position $q$ | 16 |
| Proprioception | fingertip position $fp$ | 12 |
| Proprioception | fingertip orientation $fo$ | 16 |
| Proprioception | previous action $a_{t-1}$ | 16 |
| Proprioception | target joint positions $\bar q$ | 16 |
| Tactile | binary contact $c$ | 4 |
| Tactile | contact pose $P$ | 8 |
| Tactile | contact force magnitude $F$ | 4 |
| Task | target rotation axis $\hat k$ | 3 |

因此 proprioception-only input dim 是 79，binary touch 是 83，dense touch 是 95。这个数字和 Table 7 对齐。

### 2.3 Action space 与控制接口

Policy 输出：

$$
a_t:=\Delta\theta\in[-0.026,0.026]^{16}.
$$

为了让手指动作平滑，先做 exponential moving average：

$$
\tilde a_t
=
\eta a_t+(1-\eta)a_{t-1}.
$$

再更新 target joint positions：

$$
\bar q_t
=
\bar q_{t-1}+\tilde a_t.
$$

真实系统中 policy / tactile-proprioception stream 是 20Hz，Allegro Hand 的 PD controller 在 300Hz 将 target joint commands 转成 torque commands。

这个细节对迁移到 LinkerHand 很关键：AnyRotate 不是 torque-level RL；它依赖底层 PD 控制器和硬件能跟踪位置目标。

### 2.4 Auxiliary goal：把连续旋转改写成移动重定向

直接用 angular velocity reward：

$$
r_{\mathrm{av}}
=
\mathrm{clip}(\omega\cdot\hat k,-c_2,c_2),
\qquad c_2=0.5,
$$

在多轴 rotation 中训练失败。原因不是公式错，而是早期 exploration 太脆弱：物体无支撑、指尖稍微错位就掉落，策略会倾向于保守抓稳，角速度很低时 $\omega\cdot\hat k$ 又 noisy，无法把策略推出 local optimum。

AnyRotate 将目标改成 moving reorientation goal：

1. 给定 desired axis $\hat k$；
2. 生成当前 target orientation；
3. 用 object keypoints 与 goal keypoints 的距离作为 dense signal；
4. 当 keypoint distance 小于 tolerance $d_{\mathrm{tol}}$ 时，沿 $\hat k$ 生成下一个 goal。

Keypoint distance：

$$
d_{\mathrm{kp}}
=
\frac{1}{N}
\sum_{i=1}^{N}
\|k_o^i-k_g^i\|.
$$

附录写明 $N=6$，keypoints 放在 object origin 的 six principal axes 上，距离 5 cm。

Goal bonus：

$$
r_{\mathrm{goal}}
=
\begin{cases}
1,& d_{\mathrm{kp}}<d_{\mathrm{tol}},\\
0,& \text{otherwise}.
\end{cases}
$$

重要批判：这是一种很有效的 dense subgoal formulation，但不应过度声称它严格等价于 Ng-style potential-based shaping 且“不改变最优策略”。因为这里 goal 本身被动态刷新，且作为 MDP goal state 参与训练；它更像把任务重写为 goal-reaching sequence。

### 2.5 Reward 结构

总体：

$$
r
=
r_{\mathrm{rotation}}
+
r_{\mathrm{contact}}
+
r_{\mathrm{stable}}
+
r_{\mathrm{terminate}}.
$$

附录细分：

$$
r_{\mathrm{rotation}}
=
\lambda_{\mathrm{kp}}r_{\mathrm{kp}}
+
\lambda_{\mathrm{rot}}r_{\mathrm{rot}}
+
\lambda_{\mathrm{goal}}r_{\mathrm{goal}}.
$$

$$
r_{\mathrm{contact}}
=
\lambda_{\mathrm{rew}}
(\lambda_{\mathrm{gc}}r_{\mathrm{gc}}+\lambda_{\mathrm{bc}}r_{\mathrm{bc}}).
$$

$$
r_{\mathrm{stable}}
=
\lambda_{\mathrm{rew}}
(\lambda_{\omega}r_\omega
+\lambda_{\mathrm{pose}}r_{\mathrm{pose}}
+\lambda_{\mathrm{work}}r_{\mathrm{work}}
+\lambda_{\mathrm{torque}}r_{\mathrm{torque}}).
$$

其中：

| Term | 作用 |
|---|---|
| $r_{\mathrm{kp}}$ | 用 keypoint distance 拉近当前 object pose 和 goal pose |
| $r_{\mathrm{rot}}$ | clip 后的沿目标轴增量旋转，$c_1=0.025$ rad |
| $r_{\mathrm{goal}}$ | 达到当前 auxiliary goal 的 sparse bonus |
| $r_{\mathrm{gc}}$ | tip contacts 数量至少 2 时奖励 |
| $r_{\mathrm{bc}}$ | 惩罚非指尖接触 |
| $r_\omega$ | object angular velocity 超过 $\omega_{\max}=0.6$ 时惩罚 |
| $r_{\mathrm{pose}}$ | 偏离 canonical grasp pose 的惩罚 |
| $r_{\mathrm{work}},r_{\mathrm{torque}}$ | controller work / torque regularization |
| $r_{\mathrm{terminate}}$ | object falls 或 rotation axis deviation 超阈值时惩罚 |

权重：

| 权重 | 值 |
|---|---:|
| $\lambda_{\mathrm{kp}}$ | 1.0 |
| $\lambda_{\mathrm{rot}}$ | 5.0 |
| $\lambda_{\mathrm{goal}}$ | 10.0 |
| $\lambda_{\mathrm{gc}}$ | 0.1 |
| $\lambda_{\mathrm{bc}}$ | 0.2 |
| $\lambda_\omega$ | 0.5 |
| $\lambda_{\mathrm{pose}}$ | 0.5 |
| $\lambda_{\mathrm{work}}$ | 0.1 |
| $\lambda_{\mathrm{torque}}$ | 0.05 |
| $\lambda_{\mathrm{penalty}}$ | 50.0 |

### 2.6 Adaptive curriculum

Contact 和 stability rewards 有双刃剑效应：

- 太早强调稳定，策略会学会“抓稳但不转”；
- 太晚强调稳定，策略会学会“乱转但掉落”。

AnyRotate 用平均 achieved goals 调度：

$$
\lambda_{\mathrm{rew}}
=
\frac{g_{\mathrm{eval}}-g_{\min}}
{g_{\max}-g_{\min}},
\qquad
[g_{\min},g_{\max}]=[1.0,2.0].
$$

这让训练先学会 goal-reaching rotation，再逐步加大 contact/stability 的约束。

### 2.7 Teacher-student distillation

Teacher 使用 privileged information：

| Privileged group | Variables |
|---|---|
| Object information | position, orientation, angular velocity, dimensions, COM, mass |
| Environment | gravity vector |
| Auxiliary goal | goal position, goal orientation |

Student 部署时不能访问这些信息，只能用历史 real-world observations。Student latent：

$$
z_t
=
\phi(O_t,O_{t-1},\dots,O_{t-n}).
$$

论文使用 TCN encoder，history length 30。Student policy 与 teacher actor-critic 架构相同，输出 diagonal Gaussian：

$$
a_t\sim\mathcal N(\mu_\theta,\Sigma_\theta).
$$

训练损失：

$$
\mathcal L_{\mathrm{student}}
=
\|z_t-\bar z_t\|_2^2
+
\mathrm{NLL}
\left(
\pi_s(a|\cdot),
\bar a_t
\right),
$$

其中 $\bar z_t$ 和 $\bar a_t$ 来自 teacher。论文还指出 student 因缺少 explicit object/goal information，goal-reaching accuracy 会下降，因此 student training 中把 goal update tolerance 提高到 $d_{\mathrm{tol}}=0.25$。

### 2.8 Dense tactile representation

AnyRotate 的触觉不是 raw image，也不是二值 contact，而是：

$$
\text{dense touch}
=
(P,F),
$$

其中：

$$
P=(R_x,R_y)
$$

表示 contact pose 的 spherical coordinates：polar angle $R_x$ 与 azimuthal angle $R_y$；

$$
F=\|[F_x,F_y,F_z]\|.
$$

真实端数据采集：

| 项 | 设置 |
|---|---|
| Robot | UR5 moves tactile sensor |
| Label source | F/T sensor on workspace platform |
| Samples | 3000 images per fingertip sensor；2400 train / 600 test |
| Labels | contact depth $z$, pose $R_x,R_y$, forces $F_x,F_y,F_z$ |
| Pose range | $R_x,R_y\in[-28^\circ,28^\circ]$ |
| Force range | up to 5 N |
| Raw image | RGB 640×480, up to 30 FPS |
| Processing | grayscale, resize to 240×135 |
| Binary contact | SSIM threshold 0.6 |
| Dense prediction | CNN predicts 6 outputs, then use $R_x,R_y,\|F\|$ |

CNN training parameters:

| 参数 | 值 |
|---|---|
| Conv filters | [32, 32, 32, 32] |
| Kernels | [11, 9, 7, 5] |
| Max pooling | kernel/stride [2,2,2,2] |
| Output dim | 6 |
| Batch norm | true |
| Activation | ReLU |
| LR | $10^{-4}$ |
| Batch size | 16 |
| Epochs | 100 |
| Optimizer | Adam |

### 2.9 Simulated tactile processing

仿真用 rigid body contact 信息近似 soft tactile sensor：

Binary contact：

$$
c=
\begin{cases}
1,&\|F\|>0.25\mathrm N,\\
0,&\text{otherwise}.
\end{cases}
$$

Force delay EMA：

$$
F_t^{\mathrm{smooth}}
=
\alpha F_t+(1-\alpha)F_{t-1},
\qquad
\alpha=0.5.
$$

Force saturation/rescaling：

$$
F=\beta_F\ \mathrm{clip}(F,F_{\min},F_{\max}),
$$

with $\beta_F=0.6$, $F_{\min}=0$, $F_{\max}=5.0\mathrm N$.

Pose saturation/rescaling：

$$
P=\beta_P\ \mathrm{clip}(P,P_{\min},P_{\max}),
$$

with $\beta_P=0.6$, $P_{\min}=-0.53$ rad, $P_{\max}=0.53$ rad.

最后用 binary contact mask 掉无接触时的 pose/force prediction，减少噪声。

## 3. 训练、数据与实验

### 3.1 系统与训练设置

| 项 | 设置 |
|---|---|
| Real hand | 16-DoF Allegro Hand |
| Arm | UR5 provides hand orientations |
| Tactile sensors | 4 front-facing vision-based tactile fingertips, modified DigiTac/TacTip style |
| Control | policy/tactile-proprioception 20Hz；PD controller 300Hz |
| Simulator | IsaacGym |
| Sim timestep | $dt=1/60$s |
| Training objects | capsule and box |
| Simulation OOD tests | OOD Mass, OOD Shape |
| Real objects | 10 unseen everyday objects |
| Evaluation length | 600 steps = 30s |
| Metrics | Rotation Count (Rot), Time to Terminate (TTT) |

Policy training Table 7:

| 参数 | Teacher | Student |
|---|---:|---:|
| Num envs | 8192 | 8192 |
| Learning rate | $5\times10^{-3}$ | $3\times10^{-4}$ |
| Teacher MLP hidden | [256,128,8] | - |
| Student TCN input | - | [30,N] |
| Student latent dim | - | 8 |
| Policy hidden | [512,256,128] | [512,256,128] |
| Rollout steps | 8 | - |
| Minibatch / batch | 32768 | 8192 |
| Discount | 0.99 | - |
| GAE | 0.95 | - |
| Goal update $d_{\mathrm{tol}}$ | 0.15 | 0.25 |

### 3.2 Domain randomization 与 system identification

System identification：对 Allegro Hand 的 16 DoF，每个 DoF 优化 stiffness、damping、mass、friction、armature，共 80 个参数，用 CMA-ES 最小化 sim/real trajectory MSE。

Domain randomization Table 6：

| 类别 | 参数 |
|---|---|
| Object geometry | capsule radius [0.025,0.034] m；capsule width [0,0.012] m；box width/height [0.045,0.06] m |
| Object mass | [0.025,0.20] kg |
| Friction | object 10.0；hand 10.0 |
| COM | [-0.01,0.01] m |
| Disturbance | scale 2.0；probability 0.25；decay 0.99 |
| Hand PD | stiffness/damping $\times U(0.9,1.1)$ |
| Observation noise | joint 0.03；fingertip position 0.005；orientation 0.01 |
| Tactile noise | pose 0.0174；force 0.1 |

旧稿中写“摩擦 0.4-1.5”不是本文 Table 6 的数值；本文给的是 object/hand friction 10.0。

### 3.3 Table 1：仿真 OOD mass / shape

| Tactile Observation | OOD Mass Rot | OOD Mass EpLen(s) | OOD Shape Rot | OOD Shape EpLen(s) |
|---|---:|---:|---:|---:|
| Fixed Hand Orn | 0.55±0.06 | 11.8±0.2 | 0.55±0.04 | 19.1±0.5 |
| Proprioception | 1.34±0.07 | 21.5±0.5 | 0.82±0.02 | 25.1±0.3 |
| Binary Touch | 1.90±0.04 | 20.8±0.5 | 1.57±0.05 | 25.3±0.2 |
| Discrete Touch | 1.95±0.15 | 22.2±0.4 | 1.67±0.08 | 26.5±0.1 |
| Dense Force (w/o Pose) | 2.05±0.04 | 22.0±0.8 | 1.60±0.02 | 25.5±0.4 |
| Dense Pose (w/o Force) | 2.05±0.05 | 21.9±0.1 | 1.73±0.03 | 26.7±0.0 |
| Dense Touch (Ours) | **2.18±0.05** | **22.8±0.8** | **1.77±0.01** | **27.2±0.3** |

因果解释：

- Fixed hand orientation policy 只有 0.55 rotations，证明 gravity-invariant training 不是可选项。
- Binary touch 明显优于 proprioception，说明触觉存在/不存在本身已经补了 contact state。
- Dense force 对 OOD mass 很有用，Dense pose 对 OOD shape 更有用；这正好对应论文说法：force 捕捉 interaction physics，pose 捕捉 contact geometry。
- Full dense touch 最好，说明 $(R_x,R_y)$ 和 $\|F\|$ 是互补而非重复信息。

### 3.4 Table 2：真实世界不同手朝向

任务：z-axis rotation，10 个真实未见物体，6 个 hand orientations。

| Observation | Palm Up Rot/TTT | Palm Down Rot/TTT | Base Up Rot/TTT | Base Down Rot/TTT | Thumb Up Rot/TTT | Thumb Down Rot/TTT |
|---|---|---|---|---|---|---|
| Proprioception | 1.47±0.69 / 27.6 | 1.05±0.37 / 25.3 | 0.84±0.30 / 26.8 | 0.87±0.46 / 22.8 | 0.78±0.53 / 20.3 | 0.51±0.65 / 9.5 |
| Binary Touch | 1.32±0.52 / 25.5 | 0.89±0.28 / 23.8 | 0.86±0.32 / 25.3 | 0.77±0.28 / 23.0 | 0.83±0.49 / 22.6 | 0.47±0.32 / 13.2 |
| Dense Touch | **1.57±0.57 / 30.0** | **1.33±0.44 / 28.2** | **1.32±0.32 / 29.8** | **1.17±0.38 / 29.4** | **1.08±0.47 / 27.9** | **0.91±0.33 / 29.2** |

因果解释：

- Dense touch 在所有方向上 TTT 接近 28-30s，说明它真正提高了“不断开/不掉落”的稳定性。
- Thumb up/down 最难，论文解释为手指水平时 gravity loading acts against actuation，Allegro actuation 被削弱。
- Binary touch 不总是优于 proprioception，特别是 palm-up/z-axis 上略低；这说明低维触觉如果没有足够空间/力信息，可能只带来噪声或不充分信息。

### 3.5 Table 3：真实世界不同旋转轴

任务：palm-down configuration，比较 x/y/z axes。

| Observation | x-axis Rot/TTT | y-axis Rot/TTT | z-axis Rot/TTT |
|---|---:|---:|---:|
| Proprioception | 0.35±0.33 / 16.6 | 0.17±0.19 / 8.33 | 1.05±0.37 / 25.3 |
| Binary Touch | 0.87±0.43 / 26.5 | 0.25±0.18 / 15.9 | 0.89±0.28 / 23.8 |
| Dense Touch | **1.33±0.50 / 28.6** | **0.79±0.37 / 27.8** | **1.33±0.44 / 28.2** |

因果解释：

- z-axis 最容易，x/y 更需要复杂 finger-gaiting，因为要两指稳住物体、另两指提供旋转。
- Dense touch 对 x/y 的提升尤其重要，证明 contact pose/force 不只是提升稳定 z-axis，还支持更复杂多指协调。
- y-axis 仍最低，说明“任意轴”并不等于所有轴等难；任务几何和手形态仍决定难度。

### 3.6 Table 11：auxiliary goal 设计选择

| Goal Update Tolerance | Rot | TTT(s) | #Success |
|---|---:|---:|---:|
| $d_{\mathrm{tol}}=0.15$ | 0.75 | 28.1 | 3.07 |
| $d_{\mathrm{tol}}=0.20$ | 1.36 | 27.7 | 4.48 |
| $d_{\mathrm{tol}}=0.25$ | **1.77** | 27.2 | **5.26** |

| Goal Increment | Rot | TTT(s) | #Success |
|---|---:|---:|---:|
| $\theta=30^\circ$ | **1.77** | 27.2 | **5.26** |
| $\theta=40^\circ$ | 1.50 | 26.7 | 4.36 |
| $\theta=50^\circ$ | 1.30 | 27.1 | 3.86 |

因果解释：

- student 的 $d_{\mathrm{tol}}$ 太小，会因为缺少 privileged goal/object 信息而频繁错过 goal，导致 OOD data 和低 rotation。
- goal increment 太大，单个子目标更难 reach，dense reward 变弱；Table 11 中 30° 最好。
- 旧稿写 $\delta\theta$ sweet spot 约 15° 不符合附录；本文明确比较的是 30/40/50°。

### 3.7 Emergent tactile behavior

Figure 7 在 rollout 第 300 step 施加 grasp offset。Dense tactile policy 展现两个重要行为：

1. $R_y$ 中能看到 object rolling along fingertips 的周期；
2. 当 contact pose 接近边界时，fingers extend to reduce contact angle in subsequent cycles。

这说明 dense touch 不只是提高表格平均分，而是让 policy 学到 reactive recovery：检测 unstable grasp under boundary contact，然后通过 finger-gaiting 防止继续滑落。论文明确说这种行为在 proprioception 或 binary touch 中没有出现。

## 4. 核心洞见

### 4.1 AnyRotate 的真正 insight

AnyRotate 的核心不是“加触觉就更好”，而是三件事必须同时成立：

$$
\text{multi-axis goal formulation}
+
\text{gravity-invariant training distribution}
+
\text{dense sim-to-real tactile features}.
$$

只加任意一项都不够：

- 没有 auxiliary goal，多轴训练会卡住；
- 没有 gravity randomization，fixed hand orientation policy 泛化差；
- 没有 dense touch，真实手朝向/轴变化下稳定性不足。

### 4.2 为什么 dense touch 有效

Binary touch 只回答：

$$
\text{finger in contact?}
$$

Dense touch 回答：

$$
\text{contact where on the fingertip? how strong?}
$$

对 in-hand rotation，这两类信息对应不同控制需求：

| 信息 | 控制意义 |
|---|---|
| contact pose $R_x,R_y$ | 判断物体是否滚到指尖边界，决定是否 finger extend / regrasp |
| force magnitude $\|F\|$ | 判断抓持是否过松/过紧，尤其在 OOD mass 下有用 |
| contact temporal history | 通过 TCN 推断趋势、重力方向和滑移风险 |

这也是为什么 Dense Force 和 Dense Pose 各自在 OOD mass / OOD shape 上有不同作用。

### 4.3 与转笔的关键差异

AnyRotate 的 object 始终被多指支撑；转笔会出现：

- object 与手指完全脱离的 aerial phase；
- 碰撞式 catch；
- 高速角动量主导；
- 瞬时接触切换；
- 更强的切向摩擦和滚动/滑动模式。

因此 AnyRotate 的 auxiliary goal 思想可以迁移，但它的 quasi-stable precision grasp 假设不能直接迁移。

## 5. 替代方案与理论局限

### 5.1 理论维度

AnyRotate 的接触表征是：

$$
(R_x,R_y,\|F\|).
$$

它是 full contact state 的低维投影：

$$
(p_c,n_c,f_n,f_t,\tau,\mathrm{contact\ patch})
\rightarrow
(R_x,R_y,\|F\|).
$$

这会丢失：

- 切向力方向；
- 接触 patch 形状；
- 多点接触；
- torsional friction；
- incipient slip 的局部剪切场。

对 stable rotation 已经很有用；对 pen spinning / high-speed rolling 可能不够。

### 5.2 算法维度

| 局限 | 影响 |
|---|---|
| Teacher-student bottleneck | student 只能通过 30-step history 推断 privileged object/goal/gravity 信息 |
| PPO sample cost | 8192 env + large-scale sim 仍需要复杂工程 |
| Tactile perception assumes single combined contact | 边缘/多点接触或复杂物体可能预测不准 |
| Auxiliary goal 依赖可达子目标 | aerial phase 或高速动态操作中子目标可能不可连续跟踪 |
| Goal tolerance/increment 敏感 | Table 11 显示 $d_{\mathrm{tol}}$ 和 $\theta$ 选择显著影响结果 |

### 5.3 工程/实验维度

- 触觉传感器是定制前向光学触觉指尖；侧面 casing 接触滑，论文通过传感器安装角度 offset 缓解。
- 真实传感器 30 FPS，policy 20Hz；对高速转笔可能不够。
- 论文报告 10 个物体，但 sharp corners / edges 仍困难，需要 edge feature 或视觉 shape。
- Allegro 在 thumb up/down 等方向 actuation weakened，说明硬件形态与重力方向强耦合。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔可迁移的部分

| AnyRotate 元件 | 转笔/WMTS 迁移方式 | 必须修改 |
|---|---|---|
| Auxiliary goal | 把连续转笔拆成 phase/subgoal：push → release → aerial → catch → regrasp | 子目标不能只用 object orientation，要包含 contact phase |
| Dense touch $(P,F)$ | 用 tactile tensor 预测 contact pose / force / slip probability | 增加 tangential shear 和 contact patch |
| Gravity-invariant training | 随机化 hand/object orientation、重力在手坐标系方向 | 转笔还要随机化角动量和初始接触 |
| Teacher-student | PPO Oracle 用特权 object/contact state，student 用真实 tactile/proprio history | student 需要更高频历史和 uncertainty |
| Reactive recovery | 用 tactile boundary/slip detection 触发 correction | catch phase 要允许离散重接触冲击 |

### 6.2 对 WMTS pipeline 的结合

| WMTS 模块 | AnyRotate 启发 |
|---|---|
| latent task generation | 生成 moving auxiliary goals，而不是只给最终旋转目标 |
| PPO Oracle | teacher 可用 privileged object pose/contact/goal/gravity，训练高质量 oracle |
| Diffusion/Flow generalist | student/diffusion policy 条件化 tactile dense features 和 phase goal |
| Ensemble World Model | 预测 contact pose/force/slip 的未来分布，发现 unstable grasp |
| real fine-tuning | 用真实 tactile perception model 对齐接触中间表征 |

最值得复用的是：**让 world model / scheduler 选择下一个 auxiliary goal，而不是让 policy 直接追最大角速度。** 这会把转笔从“一个长期稀疏动态任务”拆成可验证的小阶段。

### 6.3 可验证实验建议

| 实验 | 设计 | 证伪条件 |
|---|---|---|
| angular reward vs auxiliary subgoal | LinkerHand 转笔比较直接 $\omega$ reward 与 phase/subgoal reward | auxiliary subgoal 不提升 exploration 或导致不自然动作 |
| binary touch vs dense tactile | 二值接触、contact pose/force、pose/force/shear 三档 | dense tactile 不提升 catch/slip recovery |
| gravity-hand randomization | palm-up-only vs randomized wrist orientation | randomized policy 不提升姿态泛化 |
| teacher-student privileged gap | teacher 用 object pose/contact truth，student 用 tactile/proprio | student distillation 后性能断崖，说明观测不足 |
| reactive recovery probe | 人为扰动笔/物体接触，观察 tactile policy 是否恢复 | 没有恢复行为，说明触觉特征未被策略利用 |

### 6.4 不应过度外推的点

- AnyRotate 的 object 没有自由飞行；转笔 aerial phase 是本质不同的动力学模式。
- 它的 dense touch 没有显式 shear/slip direction；转笔更依赖切向信息。
- 20Hz control 和 30FPS tactile 对高速 pen spinning 可能太低。
- 成功依赖 Allegro + 4 个定制 tactile sensors；LinkerHand 的 actuator/tactile layout 需要重新建模。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

AnyRotate 是 PPO 在高难接触任务上的一个很好的 reward/task formulation 案例。关键不是 PPO 本身，而是把 multi-axis rotation 改写成 moving auxiliary goal，让 exploration 有 dense progress signal。Teacher-student distillation 属于 privileged learning / sim-to-real 策略压缩。

### 7.2 与 [[ContactMechanics]] 的联系

Dense touch 是接触状态的低维物理表征。它承认 in-hand rotation 的核心不是“关节角轨迹”，而是接触位置和法向力如何随物体滚动循环变化。Figure 7 的 reactive recovery 正是 contact boundary feedback 的体现。

### 7.3 与 [[SignalProcessing]] 的联系

触觉图像处理包括灰度化、resize、SSIM contact detection、CNN regression。重要的是 signal pipeline 产生的是显式接触变量，而不是让策略端到端处理 raw image。

### 7.4 与 [[RepresentationLearning]] 的联系

AnyRotate 是“物理中间表征优先”的例子：$(R_x,R_y,\|F\|)$ 比 raw tactile image 更容易 sim-to-real，比 binary contact 更有信息。它和 Tacmap 的共同点是都在寻找触觉的 gap-invariant observation subspace。

### 7.5 与 [[ControlTheory]] 的联系

策略输出相对位置增量，底层 PD 控制执行。AnyRotate 的稳定性依赖 action smoothing、PD tracking、actuation strength 和 tactile recovery。若迁移到 LinkerHand，需要先确认低层位置/力控接口能支持类似的快速 finger-gaiting。

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “AnyRotate 为什么比角速度奖励好？” | 写出 angular reward 在 early exploration 中 noisy，auxiliary goal 用 keypoint distance 给 dense signal |
| “Dense touch 到底多了什么？” | contact pose $(R_x,R_y)$ 定位指尖接触边界，$\|F\|$ 表示抓持强度；Table 1 分别显示 mass/shape 作用 |
| “重力不变怎么来的？” | 训练随机化 hand orientation，teacher 有 gravity vector，student 用 tactile/proprio history 隐式推断 |
| “结果最强证据是什么？” | Table 2/3 中 Dense Touch 在所有 hand orientations / axes 上 Rot 和 TTT 最好 |
| “对转笔怎么用？” | 用 auxiliary phase goals + dense tactile/slip features，但必须处理 aerial phase、shear 和更高频控制 |

## References

- Yang, M. et al. **AnyRotate: Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch**. CoRL 2024.
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
- [[RotateIt - General In-Hand Object Rotation with Vision and Touch]]
- [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]]
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]]
- [[ReinforcementLearning]]
- [[ContactMechanics]]
- [[SignalProcessing]]
- [[RepresentationLearning]]
- [[ControlTheory]]
