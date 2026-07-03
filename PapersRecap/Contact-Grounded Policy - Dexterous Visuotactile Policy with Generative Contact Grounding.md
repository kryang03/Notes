---
tags:
  - paper
  - manipulation
  - tactile
  - imitation-learning
  - sim-to-real
  - diffusion-policy
  - contact-grounding
aliases:
  - CGP
  - Contact-Grounded Policy
paper-year: 2026
read-date: 2026-06-25
venue: arXiv
paper-pdf: "[[Papers/Contact-Grounded Policy- Dexterous Visuotactile Policy with Generative Contact Grounding.pdf]]"
related:
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[ReinforcementLearning]]"
  - "[[Diffusion Policy: Visuomotor Policy]]"
  - "[[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]]"
---

# Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding

> [!abstract] 核心贡献
> Contact-Grounded Policy (CGP) 的关键不是“给 Diffusion Policy 加触觉观测”，而是让策略先生成未来**实际机器人状态 + 触觉反馈**的耦合轨迹，再通过 learned contact-consistency mapping 把每个 $(x_t,u_t)$ 转成 compliance controller 可执行的 target state $a_t$，从而把 contact prediction 接进低层控制栈。

> [!tip] 与理论基础的关联
> - [[ContactMechanics#5. 接触动力学与求解器：如何算出下一时刻|ContactMechanics §5]]：CGP 用 tactile field + actual-target gap 隐式表示多点接触演化，避开显式接触模式枚举。
> - [[Dynamics#4.2 约束动力学：Lagrange 乘子与约束反力|Dynamics §4.2]]：接触力通过 compliant controller 的 target-actual discrepancy 体现。
> - [[Diffusion Policy: Visuomotor Policy]]：继承 conditional diffusion / receding horizon，但预测对象从 action trajectory 改成 state-tactile contact trajectory。
> - [[ReinforcementLearning#8.1 状态表征：触觉是灵巧操作的"暗感官"|ReinforcementLearning §8.1]]：触觉不再只是 observation，而是被预测并执行的 contact latent。
> **核心技术**: latent tactile VAE, coupled state-tactile diffusion, contact-consistency mapping, residual target prediction, receding horizon execution.

---

## 0. 阅读定位与范本价值

这篇 paper 位于“触觉策略到底应该怎么用”的关键位置。前面几篇 tactile/in-hand rotation 论文证明了触觉有价值，但常见做法是：

1. 把 tactile 当作额外 observation；
2. 或者把 tactile prediction 当作 auxiliary loss；
3. 最后 policy 仍然直接输出 action / target state。

CGP 的价值在于它指出：**预测触觉本身不够，预测出来的 contact pattern 必须能通过 low-level compliance controller 被实际执行出来。** 于是它把策略分解为：

$$
O_t
\rightarrow
(\hat x_{t+1:t+T},\hat u_{t+1:t+T})
\rightarrow
\hat a_{t+1:t+T}
\rightarrow
\text{compliance controller}
$$

这对用户的 LinkerHand / DNPM 很重要：如果转笔策略只把触觉作为“输入”，它可能知道要滑了，但动作输出不一定能制造正确接触力；CGP 试图把“希望发生的接触”变成“控制器目标”。

| 范本要求 | CGP 应回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么 visuotactile DP 不够？ | §1 写清“contact awareness disconnected from control” |
| 原理与理论 | $(x,u,a)$ triplet、PD gap、VAE latent、diffusion 如何连成闭环？ | §2 无跳步推导 contact-consistency mapping |
| 实验与验证 | Table II/III/IV 如何分别验证 policy、mapping、latent？ | §3 用真实数字解释因果链 |
| 未来与结合 | 对转笔、WMTS、tactile latent 和 actuator residual 有什么启发？ | §5-7 写具体实验和边界 |

---

## 1. 问题设定与动机

### 1.1 一句话核心

CGP 把 contact-rich dexterous manipulation 视为 contact grounding：策略不直接生成 controller reference，而是先预测未来实际状态和触觉反馈，再学习一个 controller-specific inverse map，把预测 contact evolution 翻译成低层 compliance controller 能执行的 target robot states。

### 1.2 直观隐喻

Visuotactile diffusion policy 像一名厨师看着锅和温度计直接决定下一步手怎么动；CGP 更像先在脑中预测“手指应该在哪里、指尖会感到怎样的压力分布”，再把这个压力分布翻译成“手柄应该压到哪个目标位置”。  

可证伪点：如果 contact prediction 没有通过 controller target 被执行，预测触觉再准也只是旁观；Table II/III 的意义就在于证明“state+tactile -> target”这个 mapping 确实提高 closed-loop success。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| Grasp-centric pipelines | 先生成稳定抓取 | 抓住后通常限制手指运动，不适合持续接触重配置 |
| RL dexterous policies | 通过 reward 发现接触策略 | reward engineering 与 sim-to-real 难，视觉/触觉 transfer 成本高 |
| Visuomotor Diffusion Policy | 直接从视觉/状态生成 action | 没有 contact semantics，容易 slip 或 over-stiff |
| Visuotactile Diffusion Policy | tactile 作为额外 observation | tactile awareness 与 low-level controller 脱节，预测/感知 contact 不等于能执行 contact |
| Tactile auxiliary prediction | 预测未来 tactile 或 force 作为 representation | 如果不转成 controller reference，rollout 时 contact pattern 未必复现 |
| Sparse fingertip force policies | 预测少量力/触点 | 对 distributed full-hand multi-patch contact 表达不足 |

### 1.4 Delta 分析

| 维度 | Diffusion Policy / Visuotactile DP | CGP 的 Delta | 真正 value add |
|---|---|---|---|
| 生成对象 | action / target trajectory | future actual state + tactile feedback | 先表达 contact evolution |
| 触觉角色 | observation 或 auxiliary target | policy 预测的一部分，并被映射成 action | tactile 进入执行链 |
| 接触表示 | 隐式在 policy hidden state 中 | triplet $(x_t,u_t,a_t)$ | 可测、可学、controller-specific |
| 控制接口 | 直接输出 target state | $a_t=M_\phi(x_t,u_t)$ | 让 target 与 predicted contact 一致 |
| 实时性 | 只生成动作，轻 | latent tactile + 8-step DDIM + lightweight mapping | 用 VAE latent 控制计算成本 |

---

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $i_t$ | $N_i\times H_i\times W_i\times3$ | RGB cameras | 否，输入 | agent-view + wrist-view vision | 视觉只提供外观/物体上下文，不直接给接触力 |
| $u_t$ | tactile RGB 或 tactile array | tactile sensors | 否，输入/监督 | 当前触觉反馈 | sim 是 $768\times3$ force array；real 是 4 个 Digit360 RGB |
| $x_t$ | robot actual state | robot proprioception | 否，输入/预测目标 | arm pose + hand joints | actual state，不是 controller target |
| $a_t$ | target robot state | policy output / controller reference | 是，映射输出 | compliance controller setpoint | action 表示 target state，非 torque |
| $O_t$ | observation history | history buffer | 否，condition | $\{o_{t-T_o+1},...,o_t\}$ | Table V 中 $T_o=2$ |
| $T$ | prediction horizon | hyperparameter | 否 | diffusion 预测未来步数 | Table V 中 $T=16$ |
| $T_a$ | execution horizon | receding horizon | 否 | 每次执行前 $T_a$ 个 targets | Table V 中 $T_a=8$ |
| $h_t=E(u_t)$ | tactile latent | VAE encoder | 是，latent in training | 压缩触觉表示 | sim latent 32；real Digit360 latent 80 |
| $Y_t$ | $[x_{t+1:t+T},h_{t+1:t+T}]$ | diffusion trajectory | 是，denoising target | future state-tactile latent trajectory | 不是 action trajectory |
| $\pi_\theta$ | U-Net denoiser | diffusion policy | 是 | 预测 injected noise $\epsilon$ | DDPM/DDIM 训练目标 |
| $M_\phi$ | MLP / mapping network | learned contact map | 是 | $(x_t,u_t)\to a_t$ | tied to sensor, robot, controller gains |
| rot6D | $\mathbb{R}^6$ | action parameterization | 是/输出 | stable target rotation | state uses quaternion, action uses rot6D |

### 2.2 从 compliance control 到 contact-consistency mapping

低层控制器把 target state $a_t$ 转成 torque。对手指关节可以近似看作 PD：

$$
\tau_t=K_p(a_t-x_t)-K_d\dot x_t
$$

接触发生时，物体对手的反力会让 actual state $x_t$ 无法完全追上 target state $a_t$。这个 target-actual discrepancy 就是 compliance controller 与环境互动的结果。直观上：

$$
a_t-x_t
\rightarrow
\text{joint torque / contact force}
\rightarrow
u_t
$$

在准静态弹簧近似下，如果忽略惯性与阻尼：

$$
f_{contact}\approx K_p(a_t-x_t)
$$

触觉 $u_t$ 是接触力、形变、接触区域的传感器读数，所以可以把 contact outcome 写成：

$$
u_t \approx \mathcal{S}(x_t,a_t;\text{object},\mu,K_p,K_d,\text{sensor})
$$

CGP 反过来学习一个 setup-specific inverse：

$$
a_t=M_\phi(x_t,u_t)
$$

这就是 contact-consistency mapping。它不是物理解析逆解，而是利用当前 embodiment、sensor 和 controller 固定这一点，从数据中学“如果手实际在这里且触觉应该是这样，那么 target state 应该放在哪里”。

### 2.3 为什么 triplet $(x_t,u_t,a_t)$ 比显式 contact mode 更实用

显式 contact modeling 需要决定：

- 哪些手指/掌面接触；
- 每个 contact patch 的位置；
- stick/slip mode；
- 法向与切向力；
- 多点接触如何分配 wrench。

对 full-hand tactile array 或 Digit360 fingertip images，这个状态是高维且组合爆炸的。CGP 的选择是绕开 contact mode enumeration：

| 显式接触变量 | CGP 中的替代 |
|---|---|
| contact location/mode | tactile feedback $u_t$ |
| robot pose under contact | actual state $x_t$ |
| intended compliance force | target-actual gap encoded by $a_t-x_t$ |
| executable command | $a_t=M_\phi(x_t,u_t)$ |

代价是可解释性下降，且 mapping 与硬件绑定；收益是可以覆盖 distributed multi-patch contacts，而不必手工写接触参数化。

### 2.4 Coupled diffusion：预测的不是动作，而是 contact evolution

CGP 对未来生成：

$$
(\hat X_t,\hat U_t)\sim\pi_\theta(\cdot|O_t)
$$

其中：

$$
\hat X_t=\{\hat x_{t+1},...,\hat x_{t+T}\}
$$

$$
\hat U_t=\{\hat u_{t+1},...,\hat u_{t+T}\}
$$

为了实时，触觉先被 VAE 压缩：

$$
h_t=E(u_t),\qquad \hat u_t=G(h_t)
$$

于是 diffusion 生成的是：

$$
Y_t=[x_{t+1:t+T},h_{t+1:t+T}]
$$

DDPM/DDIM training 过程：

$$
Y_t^j=\alpha_jY_t^0+\sigma_j\epsilon,\qquad \epsilon\sim\mathcal{N}(0,I)
$$

denoiser 目标：

$$
L_{diff}(\theta)
=
\mathbb{E}_{(O_t,Y_t^0),\epsilon,j}
\left[
\|\epsilon-\pi_\theta(O_t,Y_t^j,j)\|^2
\right]
$$

推理时每个未来步映射为 target：

$$
\hat a_{t+k}=M_\phi(\hat x_{t+k},\hat u_{t+k}),\qquad k=1,...,T
$$

再执行 receding horizon：Table V 中 $T=16$、$T_a=8$，policy 5 Hz rollout，8-step DDIM denoising。

### 2.5 VAE 与 KL：为什么重建误差更低不一定更好

VAE 训练目标可写成：

$$
L_{VAE}
=
\mathbb{E}_{q(h|u)}[-\log p(u|h)]
+
\beta D_{KL}(q(h|u)\|p(h))
$$

第一项追求 tactile reconstruction；第二项让 latent space 接近结构化先验。Table IV/VI 都显示一个重要现象：去掉 KL 后重建误差更低，但 latent KL 大幅变高，rollout performance 反而下降。  

原因是 diffusion 不只需要 reconstruct，还需要在 latent space 中采样和去噪。如果 latent manifold 崎岖、不连续，diffusion 生成的 $h_t$ 虽然看似低 reconstruction error，却更容易落到不可执行 contact latent 上。

### 2.6 实现细节：sim 与 real 的 tactile mapping 不同

| 系统 | Robot / tactile | Mapping 实现 |
|---|---|---|
| Simulation | UR5 + Tesollo DG-5F 20-DoF hand; dense $768\times3$ tactile array | diffusion-predicted tactile latent 先 decode 到 raw tactile，再 re-encode 成 feature，与 actual state 拼接给 MLP |
| Real | Franka + Allegro V5 16-DoF hand; 4 Digit360 tactile RGB sensors | 为实时性，不重建 tactile images，直接拼接 predicted tactile latent 与 actual state 给 MLP |

这个差异很重要：CGP 不是一个完全统一的触觉后端。它在不同 tactile modality 上采用不同工程折中。

---

## 3. 训练、数据与实验

### 3.1 任务、数据与维度设置

| Task | Domain | Demos | $T$ | $T_o$ | $T_a$ | Action | State | Tactile | Latent |
|---|---|---:|---:|---:|---:|---:|---:|---|---:|
| In-Hand Box Flipping | Sim | 60 | 16 | 2 | 8 | 29 | 27 | $768\times3$ array | 32 |
| Fragile Egg Grasping | Sim | 100 | 16 | 2 | 8 | 29 | 27 | $768\times3$ array | 32 |
| Dish Wiping | Sim | 100 | 16 | 2 | 8 | 29 | 27 | $768\times3$ array | 32 |
| Jar Opening | Real | 45 | 16 | 2 | 8 | 25 | 23 | 4×RGB 72×72 Digit360 | 80 |
| Real In-Hand Box Flipping | Real | 90 | 16 | 2 | 8 | 25 | 23 | 4×RGB 72×72 Digit360 | 80 |

Action 维度解释：

- sim: arm position + rot6D + 20 hand joints = 29；
- real: arm position + rot6D + 16 hand joints = 25；
- state 用 quaternion 而 action 用 rot6D，是为了稳定 action regression。

### 3.2 端到端任务成功率：Table II 的正确读法

| Task | Domain | CGP | Visuotactile DP | Visuomotor DP |
|---|---|---:|---:|---:|
| In-Hand Box Flipping | Sim | **66.0%** | 58.0% | 53.2% |
| Fragile Egg Grasping | Sim | **74.8%** | 70.0% | 53.2% |
| Dish Wiping | Sim | **58.4%** | 43.6% | 42.4% |
| Jar Opening | Real | **93.3%** | 66.7% | 73.3% |
| Real In-Hand Box Flipping | Real | **80.0%** | 60.0% | 60.0% |

仿真任务用最后 5 个 checkpoint 的均值，共 250 rollouts；真机任务用 15 consecutive rollouts。

**因果解释**：CGP 在所有任务上优于两个 DP baseline，且提升最大的不是“视觉难”的任务，而是 contact evolution 关键的任务：Dish Wiping 从 43.6/42.4 到 58.4，Jar Opening 从 66.7/73.3 到 93.3。它证明的是 contact-grounded execution，而不是多模态输入数量本身。

### 3.3 Contact-consistency mapping：Table III 直接验证 $(x,u)\to a$

作者单独设计 hand configuration prediction，不涉及 downstream policy，只测试 mapping。数据：simulation 中 150 个 teleoperated grasping episodes，4114 frames，11 objects；episode-level 1:1 train/validation split。

| Input | Encoder | Absolute MAE ↓ | Residual MAE ↓ |
|---|---|---:|---:|
| State + Tactile | ResNet1D | 8.80±0.24 | **5.94±0.20** |
| State + Tactile | MLP | 12.50±0.32 | 8.33±0.32 |
| State + Tactile | Transformer | 14.39±0.38 | 9.58±0.48 |
| State Only | - | 16.05±0.39 | 10.64±0.38 |
| Tactile Only | ResNet1D | 35.93±0.89 | 12.15±0.20 |
| Tactile Only | MLP | 36.86±0.25 | 12.72±0.25 |
| Tactile Only | Transformer | 43.11±0.91 | 14.62±0.43 |

单位是 joint-angle MAE $\times10^{-3}$ rad。

因果链：

`state+tactile > state-only/tactile-only`  
说明 target state 不是单靠姿态或单靠触觉就能恢复；接触力和空间状态必须耦合。

`residual mode > absolute mode`  
说明 $a_t$ 最好建模为 actual state 周围的 contact-conditioned offset，而不是从零预测绝对 target。

`ResNet1D > MLP/Transformer`  
说明 tactile array 的局部空间结构对 mapping 有用，简单 flatten MLP 和重型 Transformer 都不如合适的卷积归纳偏置。

### 3.4 KL-regularized tactile latent：Table IV 的反直觉点

仿真 tactile array validation：

| Task | Model | MAE ↓ | Active MAE ↓ | KL ↓ |
|---|---|---:|---:|---:|
| Box | ResNet1D w/ KL | 1.26 | 12.07 | **0.12** |
| Box | ResNet1D w/o KL | **0.97** | **9.91** | 0.73 |
| Egg | ResNet1D w/ KL | 0.69 | 5.95 | **0.22** |
| Egg | ResNet1D w/o KL | **0.45** | **3.92** | 0.43 |
| Dish | ResNet1D w/ KL | 1.54 | 6.80 | **0.24** |
| Dish | ResNet1D w/o KL | **1.02** | **4.49** | 0.45 |

MAE 和 Active MAE 单位是 $10^{-2}$ N。去掉 KL 后 reconstruction 更好，但 KL 变差；Fig. 7 显示 rollout performance 下降。

**因果解释**：对 CGP 来说，VAE latent 不是最终输出，而是 diffusion 生成空间。一个 reconstruction 更好的 latent 如果分布不规则，会让 diffusion 采样更难，最终 policy 更差。这是典型“表示学习服务于生成控制，而不是服务于重建指标”的例子。

### 3.5 Digit360 tactile compression：real sensor 上同样成立

真实 Digit360 tactile images 上，latent 80 的例子：

| Task | Model | MAE ↓ | KL Loss ↓ | PSNR ↑ | SSIM ↑ |
|---|---|---:|---:|---:|---:|
| Box | w/ KL | 9.01 | **0.0694** | 35.2050 | 0.9870 |
| Box | w/o KL | **4.55** | 0.7781 | **40.4590** | **0.9939** |
| Jar | w/ KL | 8.10 | **0.0647** | 35.9445 | 0.9883 |
| Jar | w/o KL | **3.88** | 0.6247 | **42.9845** | **0.9957** |

再次说明：更像原图不等于更适合 downstream diffusion control。作者最后选择 real Digit360 latent 80，即每个 sensor 20 维，平衡 reconstruction、latent regularity 和 runtime。

### 3.6 可视化证据的正确位置

Fig. 5 的价值不是“预测 tactile 看起来像”，而是 time-aligned 证据：模型在 replanning 时预测未来 16 steps 的 tactile/state，执行 8 steps 后，未来时刻的 observed tactile 与此前 predicted tactile 对齐。这说明 predicted contact evolution 被 controller target 实际复现。

Fig. 12 的 real robot overlay 也有一个重要解释：接触前 target-actual mismatch 小，主要来自 gravity/friction 下的 steady-state PD error；接触时 mismatch 变大，体现 compliance controller 被接触力顶住；手指失去接触后 gap 缩小。这个现象正是 $(x,u,a)$ contact representation 的物理根。

---

## 4. 核心洞见

### 4.1 论文真正的 insight

CGP 的真正 insight 是：

> 触觉要成为动作生成的一部分，而不是只成为动作生成的输入。

也就是说，policy 需要回答两个问题：

1. 未来应该出现什么接触？
2. 在当前 compliance controller 下，什么 target state 会制造这个接触？

Visuotactile DP 通常只回答“看到触觉后输出什么动作”；CGP 通过 $Y_t=[x,h]$ 和 $M_\phi(x,u)$ 把“contact intention”显式放进中间层。

### 4.2 为什么这个设计有效

它有效依赖三层结构：

| 层 | 功能 | 如果移除 |
|---|---|---|
| tactile VAE + KL | 把高维 tactile 压成可生成 latent | raw tactile 生成太贵；无 KL latent 不稳定 |
| coupled diffusion | 同时生成 actual state 与 tactile latent | 状态和接触分离，容易出现物理不一致 |
| contact-consistency mapping | 把 predicted contact 转成 controller target | tactile prediction 变成辅助任务，无法保证执行 |

### 4.3 什么时候会失效

| 场景 | 原因 |
|---|---|
| controller gains / update rate 改变 | $M_\phi$ 绑定特定 compliance controller |
| sensor type 或安装方式变化 | tactile distribution 和 contact geometry 改变 |
| 高动态抛接/转笔飞行相 | $u_t\approx f(a_t-x_t)$ 的准静态直觉不够，需要速度/惯性 |
| 任务跨域泛化 | 论文是 single-task training/evaluation，没有证明跨任务 contact transfer |
| 接触不可观测 | fingertip Digit360 无法看到掌面/侧面接触时，mapping 缺信息 |
| 长时序误差累积 | diffusion prediction error 经过 $M_\phi$ 变成 target error，再影响下一轮 contact |

---

## 5. 替代方案与理论局限

### 5.1 理论维度

CGP 的映射：

$$
a_t=M_\phi(x_t,u_t)
$$

隐含一个强假设：给定 actual state 和 tactile feedback，存在足够确定的 target state 能复现该 interaction。多点摩擦接触中，这个逆映射未必唯一。同一个 tactile pattern 可能来自不同切向力分配、不同接触历史或不同 object pose。MLP 学到的可能是数据分布上的平均可行解，而不是物理唯一解。

此外，PD 弹簧直觉更适合低速/持续接触任务。对转笔、抛接、快速 slip-regrasp 等高动态技能，惯性项：

$$
M(q)\ddot q+C(q,\dot q)\dot q
$$

不能被简单吞进 $a_t-x_t$。如果要迁移到 DNPM，需要把 velocity、history 或 actuator dynamics 加入 mapping。

### 5.2 算法维度

| 替代方案 | 优点 | 相对 CGP 的问题 |
|---|---|---|
| End-to-end Diffusion Policy | 简洁、硬件依赖小 | 接触预测与控制执行脱节 |
| Visuotactile DP | 利用触觉输入 | tactile 是 observation，不是 executable contact plan |
| Force/impedance target policy | 控制理论更直接 | 需要可测/可控力接口，难覆盖 dense multi-patch contact |
| Explicit contact model + MPC | 可解释，可约束 | 接触模式组合爆炸，实时困难 |
| DexTrack-style reference tracker | 可利用人类 reference | 如果没有 tactile-grounded execution，接触力仍可能错 |

### 5.3 工程/实验维度

- 每个任务单独训练，demo 数量也很小：real Jar Opening 45 demos，real Box Flipping 90 demos。
- 真机使用 Digit360 指尖触觉，掌面/指侧接触不可见；而仿真有 dense full-hand tactile array。
- 推理时间在 A100 80GB 上测，不能直接推断边缘设备实时性。
- 5 Hz policy rollout + 8-step DDIM 对高频接触事件可能偏慢。
- sensor/controller 改变需要重新训练或适配，这是论文自己列出的首要限制。

---

## 6. 对用户研究的启发

### 6.1 对 DNPM / LinkerHand 转笔的直接迁移

| CGP 部件 | 用户项目中应变成什么 | 价值 | 风险 |
|---|---|---|---|
| tactile latent $h_t$ | LinkerHand $5\times12\times6$ tactile encoder latent | 把分布式触觉压成可生成 contact state | 需要覆盖 shear/slip，不只是 normal pressure |
| coupled state-tactile prediction | 预测未来 joint state + tactile/contact phase | 让策略显式规划“接下来应该碰哪里、怎么受力” | 高动态转笔需要 velocity/history |
| $M_\phi(x,u)\to a$ | learned target-state inverse for LinkerHand PD / motor controller | 把期望接触转成可执行 target | 绑定 $K_p,K_d$、CAN latency、actuator response |
| residual mapping | $a=x+\Delta a(x,u)$ | 降低 target regression 难度 | 若 tactile prediction 错，residual 会放大错误 |
| KL latent | tactile generative prior | 稳定 contact-latent diffusion | reconstruction 指标不能单独作为选择标准 |

### 6.2 对 WMTS 五模块的具体接法

| WMTS 模块 | CGP 的进入方式 |
|---|---|
| latent task generation | 生成期望 contact/tactile latent trajectory，而不只是 object pose |
| PPO Oracle | 在仿真中用 privileged force/tactile 训练 contact-grounded oracle，记录 $(x,u,a)$ triplets |
| Diffusion/Flow generalist | 学 $[x,h]$ coupled trajectory，再经 $M_\phi$ 输出 target |
| Ensemble World Model | 预测 tactile/contact latent 是否可执行，识别 slip/drop uncertainty |
| real-robot fine-tuning | 单独适配 $M_\phi$ 到真实 tactile sensor + controller，不必重训高层 contact generator |

### 6.3 和 DexTrack / DexNDM 的组合

| 论文 | 给用户系统的部件 | CGP 如何补 |
|---|---|---|
| [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] | human reference -> tracking controller | CGP 给 tracker 加 contact-grounded execution，不只跟几何 |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] | joint-wise real dynamics residual | CGP 的 $M_\phi$ 可加入 actuator/joint dynamics 条件 |
| [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand]] | transition waypoint + force privileged insight | CGP 可把 waypoint 扩展为 expected tactile/contact trajectory |

对转笔，最合理的组合不是直接套 CGP，而是：

1. DexTrack / human video 给出 kinematic phase reference；
2. FingerGaiting 给出 transition waypoints 和 contact role；
3. CGP 生成 future tactile/contact latent；
4. DexNDM-style residual 修正真实 actuator response；
5. WMTS ensemble 判断该 contact latent 是否高风险。

### 6.4 可验证实验建议

1. **LinkerHand contact-consistency mapping test**  
   采集 $(x_t,u_t,a_t)$，比较 state-only、tactile-only、state+tactile、history-state+tactile 对 target prediction MAE 的影响。

2. **Tactile latent KL ablation**  
   不要只看 tactile reconstruction MAE；必须看 diffusion rollout success、slip rate、drop rate。CGP 证明低 reconstruction error 可能更差。

3. **Contact-grounded PPO auxiliary branch**  
   在 PPO oracle 中加预测 $[x_{t+1:t+T},h_{t+1:t+T}]$ 的 auxiliary loss，测试是否提升样本效率和 sim-to-real。

4. **High-frequency contact stress test**  
   在仿真中把 policy rollout 从 5 Hz 提到 10/20 Hz，对转笔/快速 regrasp 任务比较 CGP-style mapping 是否仍稳定。

5. **Controller-parameter conditioning**  
   随机化 $K_p,K_d$、latency、update rate，训练 $M_\phi(x,u,K_p,K_d,\Delta t)$。如果能泛化，才适合 LinkerHand 多控制设置。

### 6.5 不应过度外推的点

- CGP 不证明跨任务 tactile contact knowledge 已经迁移；论文是 single-task train/eval。
- 真机只用 fingertip Digit360，不等于 full-hand tactile。
- Table II 的高成功率来自小规模 demos 和特定任务，不是开放世界灵巧操作。
- 对 DNPM 转笔，高动态/飞行相会挑战 $M_\phi(x,u)$ 的准静态假设。

---

## 7. 与知识体系的联系

### 7.1 与 [[ContactMechanics]] 的联系

CGP 是“用传感器空间绕开接触模式枚举”的代表。它不显式写 contact Jacobian、摩擦锥或 mode schedule，而是把接触结果编码到 tactile field $u_t$，再用 target-actual gap 使其可执行。这对 distributed contact 有工程优势，但牺牲了可解释约束。

### 7.2 与 [[Dynamics]] 的联系

低层控制器可视为弹簧阻尼系统：

$$
\tau=K_p(a-x)-K_d\dot x
$$

接触力造成 target 和 actual 的偏差。CGP 学的是这个偏差如何与 tactile feedback 对应。它不是完整动力学模型，但它把 controller dynamics 放回了 policy 结构中。

### 7.3 与 [[Diffusion Policy: Visuomotor Policy]] 的联系

Diffusion Policy 生成 action trajectory；CGP 生成 state-tactile trajectory。这个差异很重要：

| 方法 | diffusion sample 的对象 | 控制含义 |
|---|---|---|
| Diffusion Policy | $a_{t:t+T}$ | 直接动作序列 |
| Visuotactile DP | $a_{t:t+T}$ conditioned on tactile | 触觉增强动作序列 |
| CGP | $[x_{t:t+T},h_{t:t+T}]$ | contact evolution，再映射成 target |

CGP 可以理解为把 diffusion policy 的 action space 替换成“可执行接触空间”。

### 7.4 与 tactile policy 簇的关系

| 论文 | tactile 角色 | CGP 的区别 |
|---|---|---|
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | tactile/contact as observation | CGP 预测 tactile future 并执行 |
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | tactile supports axis-invariant rotation | CGP 更强调 controller-executable contact target |
| [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] | visuotactile fusion | CGP 进一步把 tactile 接进 target mapping |
| [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] | reference tracking | CGP 可补 contact-grounded execution |

---

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “CGP 和 visuotactile DP 的本质区别？” | visuotactile DP 用 tactile condition action；CGP 生成 future tactile/state，再映射成 executable target |
| “为什么需要 $M_\phi(x,u)$？” | 因为 contact prediction 必须经过 compliance controller 才能变成真实接触，否则只是辅助预测 |
| “KL 明明让重建变差，为什么还要？” | diffusion 需要规则 latent manifold；重建好但 KL 高会让 rollout 更差 |
| “能不能用于转笔？” | 只能作为 contact-latent execution 模块；高动态转笔需要加入 velocity/history/actuator dynamics |
| “最大工程风险？” | sensor/controller-specific，换触觉或控制增益就需要适配 |
| “和 WMTS 怎么结合？” | 把期望 tactile/contact latent 纳入 task scheduler 和 world-model uncertainty，而不是只预测 object pose |

---

## References

- Zhengtong Xu, Yeping Wang, Ben Abbatematteo, Jom Preechayasomboon, Sonny Chan, Nick Colonnese, Amirhossein H. Memar. *Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding*. arXiv, 2026.
- Project website: contact-grounded-policy.github.io.
- Hardware: Franka Panda + Allegro V5 + four Digit360 sensors; simulation: UR5 + Tesollo DG-5F + dense tactile array.
