---
tags:
  - paper
  - dexterous-manipulation
  - visuotactile
  - in-hand-manipulation
  - transformer
aliases:
  - RotateIt
paper-year: 2023
read-date: 2026-02-01
venue: CoRL 2023
paper-pdf: "[[Papers/General In-Hand Object Rotation with Vision and Touch.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ComputationalGeometry]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
---

# RotateIt: General In-Hand Object Rotation with Vision and Touch

> [!abstract] 核心贡献
> RotateIt 把多轴 in-hand object rotation 的瓶颈定位为 **extrinsics 不可观测**：oracle policy 在仿真中用 object shape + physical properties 学会稳定旋转，部署时用 visuotactile transformer 从 proprioception、depth、tactile contact location 和 action history 在线回归这个 extrinsics latent，从而把 HORA 类 z-axis proprioception-only rotation 推进到多轴、跨物体、真实 AllegroHand zero-shot transfer。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — 惯性张量 $I$ 与欧拉方程解释为什么非 z 轴旋转更依赖物体形状，而不是“形状编码碰巧有用”。
> - [[ReinforcementLearning]] — privileged oracle policy + sensorimotor distillation：训练时可用 $z_t$，部署时只能用 $\hat z_t$。
> - [[RepresentationLearning]] — PointNet shape encoder + transformer temporal fusion：从 point cloud / visuotactile history 到 task-relevant extrinsics。
> - [[SignalProcessing]] — depth segmentation、contact-location discretization 和 temporal transformer 都是在做 noisy multimodal signal filtering。
> - [[ContactMechanics]] — contact location 比 binary contact 更关键，因为多轴 finger-gaiting 需要知道接触在 fingertip 上的方向，而不只是”接触发生了”。
> - [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL §9]] — privileged oracle $\pi(p_t,z_t)$ → visuotactile 估计 $\hat z_t$ 的 teacher-student，是 §9 里”critic/teacher 可 privileged、actor 部署只能用可观测估计”的范本。
> - [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]] — **电流≠关节力矩**暗线：action=20 Hz position target 经 300 Hz PD 转 torque；RotateIt 的 sim-to-real 全压在 $\hat z_t$ 的感知估计上，而执行器 gap 由 PD 层与 randomization 兜底（与 HORA 同接口）。
>
> **核心技术**: privileged extrinsics, PointNet shape encoding, visuotactile transformer, contact-location tactile representation, multi-axis in-hand rotation

## 0. 阅读定位与范本价值

这篇论文在触觉/灵巧手谱系里的位置很明确：

> HORA 证明了 proprioception-only + RMA 可以做 z-axis in-hand rotation；RotateIt 追问：如果目标不是最容易的 z-axis，而是 x/y/z 多轴，缺的到底是什么？

它的答案不是“换一个更大的网络”，而是：

1. **shape matters**：非 z 轴旋转强依赖物体几何、惯性和 contact affordance；
2. **touch location matters**：binary contact 只说“有没有碰”，不能告诉 finger-gaiting 应该从哪个方向换指；
3. **vision and touch are complementary**：depth 给 shape/global geometry，tactile 给 local contact state；
4. **deployment bottleneck is estimating privileged extrinsics**：真实世界拿不到 mass/friction/shape latent，只能从 noisy sensor history 估计。

这篇和最近几篇 tactile recaps 的分工：

| 论文 | 核心触觉观点 | 对 WMTS / 转笔的价值 |
|---|---|---|
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | binary full-hand contact 足以跨 sim-real 做 blind rotation | 证明“少但稳”的 contact event 可以有价值 |
| [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]] | 显式 belief estimator 比 opaque RNN 更可调试 | 给 hidden object-state estimation 的模块化模板 |
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | dense tactile + moving goal 支持任意轴、任意重力方向 | 更接近最终 arbitrary-axis rotation controller |
| [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | 不补感知、而补**关节级动力学**：joint-wise 神经动力学 + residual | 与 RotateIt 互补——RotateIt 估计 object extrinsics（$\Delta_S$/感知侧），DexNDM ground 执行器/载荷响应（$\Delta_T$/动力学侧），二者攻的是同一 in-hand rotation gap 的两个正交半边 |
| **RotateIt** | depth + contact location + proprio history 可回归 extrinsics | 说明多轴旋转需要 shape/contact-location observability |

最低标准：

| 支柱 | 本文必须讲清的问题 | 本 recap 的位置 |
|---|---|---|
| 逻辑与价值 | 为什么 z-axis HORA 不够？为什么多轴需要 vision+touch？ | §1 |
| 原理与理论 | shape 为什么从动力学上进入 reward/控制？$\omega\cdot k$ 与 $\omega\times k$ 如何定义任务？ | §2.2-2.5 |
| 实验与验证 | Table 1/2/4/Fig.8 分别证明了哪个 mechanism？ | §3 |
| 未来与结合 | 它对 LinkerHand 转笔有何启发，又为何不能直接用于 pencil/screwdriver？ | §5-§6 |

## 1. 问题设定与动机

### 1.1 一句话核心

RotateIt 要学的是：

> 用 AllegroHand 指尖在无支撑面条件下持续旋转多种物体，并且不只绕 z-axis，而是绕 hand-centric x/y/z axes 做连续 rotation；训练在仿真中使用 privileged object shape/physics，部署时用 real depth + tactile sensor + proprioception 估计这些 privileged extrinsics。

这和 “object reorientation to a target pose” 不同。本文任务是 continuous rotation：尽可能多地绕指定轴旋转，episode 最大 20 s。它关心：

- object 什么时候掉：TTF；
- 绕目标轴转得快不快：RotR = average $\omega\cdot k$；
- 有没有偏到非目标轴：RotP = average $\|\omega\times k\|$；
- 真实世界转了多少弧度：Radians Rotated。

### 1.2 直观隐喻

HORA 像是一个熟练的人闭眼转一个方向最顺手的物体；RotateIt 像是让这个人转一个陌生物体时先快速摸形状、看轮廓，再决定 finger-gaiting 的节奏。

这个隐喻的关键是：

- **vision** 给“这个物体大概什么形状”；
- **touch location** 给“当前指尖从哪个方向顶住它”；
- **proprioception/action history** 给“我的手刚刚怎么动，它如何回应”；
- **transformer** 把这些历史压成 $\hat z_t$，近似 oracle 本来拥有的 shape/physical properties。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| HORA / RMA proprioception-only | 从关节和动作历史隐式估计物体 dynamics | z-axis 很强，但 x/y 轴缺 shape/contact-location observability |
| vision-only dexterity | depth/pose 估计提供 global geometry | contact state 和滑移方向不可见；遮挡严重 |
| tactile binary contact | 接触事件作为闭环反馈 | 对 RotateIt 来说几乎不优于 no-touch，因为 proprio history 已隐含“是否接触” |
| full privileged oracle | 直接给 shape、mass、friction、pose 等 extrinsics | 真实部署不可用，只能作为 training upper bound |
| 每轴单独 RL policy | 固定 $k$ 时训练稳定 | 不是真正一开始就学 arbitrary-axis；appendix 需要 imitation distillation 才得到 multi-axis policy |
| SAM + RGBD depth pipeline | 降低 real depth 背景 gap | 增加感知依赖和延迟；高速 manipulation 中可能不稳定 |

### 1.4 Delta 分析

本文相对 HORA 的 delta 不只是“多加两个 sensor”：

1. **privileged input 扩展**：HORA 主要做 physical extrinsics/RMA；RotateIt 显式加入 object shape point cloud encoding。
2. **task axis 扩展**：从 z-axis continuous rotation 到 x/y/z axes，且真实实验重点展示 x-axis，因为这是 HORA 失败点。
3. **tactile representation 细化**：不是 binary contact，而是 fingertip frame 上 8-bin contact location + finger index。
4. **sensorimotor distillation**：oracle $\pi(p_t,z_t)$ 用 PPO 学；visuotactile transformer $\phi(f_T)$ 学 $\hat z_t$，让部署 policy 近似 oracle。
5. **evidence pattern 更完整**：Table 1 证明 shape；Table 2 证明 contact location；Table 4 证明 vision/touch/transformer；Fig.8 证明 real-world gap。

一句话：

> RotateIt 的 insight 是：多轴旋转不是 z-axis policy 的简单泛化，而是一个 extrinsics-identification problem；只有把 shape 和 local contact location 变成可估计 latent，policy 才有信息去选择正确 finger-gaiting。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $q_t$ | $\mathbb{R}^{16}$ | Allegro joint positions | policy input | 手当前关节位置 | 不是 velocity；$p_t$ 用 $q_{t-2:t}$ |
| $a_t$ | $\mathbb{R}^{16}$ | policy output | actor output | PD target joint position | 不是 torque；20 Hz command，经 PD 300 Hz 转 torque |
| $p_t$ | $\mathbb{R}^{96}$ | computed proprio/action history | policy input | $[q_{t-2:t},a_{t-3:t-1}]$ | 维度 $3\times16+3\times16=96$ |
| $k$ | unit vector in hand-centric frame | task command | fixed per policy / input for multi-axis | desired rotation axis | $k$ 是目标轴，不是实际 angular velocity |
| $\omega$ | $\mathbb{R}^3$ | simulator privileged state | reward only | object angular velocity | real-world 不能直接用于 reward |
| $z_t^{\text{shape}}$ | $\mathbb{R}^{32}$ | object mesh → PointNet | encoder learned in oracle training | shape latent | 使用 $N_p=100$ mesh points；部署时没有 mesh |
| raw physical vector | 7 dims | simulator privileged parameters | input to privileged encoder | mass, CoM, friction, scale, restitution | 不是最终 $z_t^{phys}$ |
| object pose vector | 10 dims | simulator privileged state | input to privileged encoder | position, quaternion, angular velocity | 和 7 维 physical vector concat |
| $z_t^{\text{phys}}$ | $\mathbb{R}^{8}$ | MLP encoder output | encoder learned | physical/pose extrinsics encoding | 旧稿常误写成“8 个物理属性”；其实是 17 维输入投影 |
| $z_t$ | $\mathbb{R}^{40}$ | concat | oracle policy input | $[z_t^{phys},z_t^{shape}]$ | privileged，真实部署不可用 |
| $o_t^{touch}$ | $N_c\times9$ | simulator contact / real tactile image | transformer input | 8-bin contact location + finger index | binary contact 不够；location 才有用 |
| $o_t^{depth}$ | $60\times60$ depth | RGBD/SAM foreground depth | ConvNet input | object depth/shape signal | real 用 SAM 分割，不是 raw RGB |
| $f_t^{touch}$ | $\mathbb{R}^{32}$ | MLP + average pooling | learned | contact feature | contact number $N_c$ varies, so pool across contacts |
| $f_t^{depth}$ | $\mathbb{R}^{32}$ | ConvNet + global average pooling | learned | depth feature | main text says ConvNet; appendix reports 4-layer ConvNet |
| $f_T$ | sequence of multimodal features | history window | transformer input | temporal evidence for extrinsics | $T$ 是 transformer history，不是 robot time alone |
| $\hat z_t$ | $\mathbb{R}^{40}$ | visuotactile transformer output | learned | predicted privileged extrinsics | deployment replaces $z_t$ with $\hat z_t$ |
| RotR | scalar | simulation metric | no gradient in eval | average $\omega\cdot k$ | 越大越好 |
| RotP | scalar | simulation metric | no gradient in eval | average $\|\omega\times k\|$ | 越小越好；reward 中用负权重惩罚 |
| TTF | scalar | eval metric | no gradient | normalized time-to-fall, max 20 s | 0.79 约等于能撑 15.8 s |

### 2.2 从刚体旋转推导：为什么 shape 对非 z 轴更重要

object rotation 的核心物理量是角速度 $\omega$ 和角动量：

$$
L = I\omega,
$$

其中 $I$ 是物体惯性张量。对刚体：

$$
I=\int_{\mathcal{B}}\rho(r)\left((r^\top r)I_3-rr^\top\right)\,dr.
$$

这一步说明了 shape 为什么进入动力学：$I$ 由质量分布和几何决定。长条、球、盒子、异形物体的 $I$ 完全不同。

刚体角运动满足欧拉方程：

$$
\tau = I\dot{\omega}+\omega\times(I\omega).
$$

如果物体绕惯性主轴转，且 $\omega$ 与 $I\omega$ 平行：

$$
\omega\times(I\omega)=0.
$$

这时所需补偿力矩较简单，旋转更“自然”。但如果要求绕一个非主轴方向转：

$$
\omega\times(I\omega)\neq 0,
$$

会出现陀螺/进动项，手指必须通过 contact force 产生额外力矩去维持指定轴。

因此，多轴 in-hand rotation 需要知道：

- 物体几何和质量分布给出的 $I$；
- 哪些 fingertip contact 可以产生所需 torque；
- 当前接触位置是否允许 finger-gaiting 继续维持 force closure。

这就是 PointNet shape encoding 和 tactile contact location 的物理根。它们不是装饰性多模态输入，而是在给 policy 估计：

$$
\text{what torque/contact strategy is feasible for this object about this axis?}
$$

### 2.3 reward：$\omega\cdot k$ 与 $\omega\times k$ 的轴向分解

desired rotation axis 是 hand-centric unit vector $k$。实际 angular velocity 可分解为平行和垂直两部分：

$$
\omega_{\parallel}=(\omega\cdot k)k,
\qquad
\omega_{\perp}=\omega-(\omega\cdot k)k.
$$

向量叉积满足：

$$
\|\omega\times k\| = \|\omega\|\,\|k\|\sin\alpha = \|\omega_\perp\|,
$$

其中 $\alpha$ 是 $\omega$ 与 $k$ 的夹角，$\|k\|=1$。

所以：

- $\omega\cdot k$ 衡量绕目标轴转得多快；
- $\|\omega\times k\|$ 衡量偏离目标轴的 undesired rotation。

论文 reward 写成：

$$
r =
r_{\text{rotr}}
\lambda_{\text{rotp}}r_{\text{rotp}}
\lambda_{\text{pose}}r_{\text{pose}}
\lambda_{\text{linvel}}r_{\text{linvel}}
\lambda_{\text{work}}r_{\text{work}}
\lambda_{\text{torque}}r_{\text{torque}}.
$$

其中：

$$
r_{\text{rotr}}=
\max(\min(\omega\cdot k,r_{\max}),r_{\min}),
$$

$$
r_{\text{rotp}}=\|\omega\times k\|_1.
$$

appendix 给出：

$$
r_{\max}=0.5,\quad r_{\min}=-0.5,\quad
\lambda_{\text{rotp}}=-0.1.
$$

也就是说 $r_{\text{rotp}}$ 本身是 penalty magnitude，靠负权重加入 reward。论文还说如果一开始就用 $\lambda_{\text{rotp}}=-0.1$，policy 只会学会稳定 hold object，所以训练时先设为 0，再 curriculum 线性降到 -0.1。

这个细节很重要：非目标轴惩罚太早太强，会抑制 exploration，导致策略宁可不动也不犯错。

### 2.4 oracle policy：privileged extrinsics 如何进入控制

oracle policy 输入：

$$
a_t=\pi(p_t,z_t),
$$

其中：

$$
p_t=[q_{t-2:t},a_{t-3:t-1}]\in\mathbb{R}^{96},
$$

$$
z_t=[z_t^{phys},z_t^{shape}]\in\mathbb{R}^{40}.
$$

shape 部分：

$$
\{p_i\}_{i=1}^{N_p}\xrightarrow{\text{PointNet}}z_t^{shape},
\qquad
N_p=100,\quad \dim(z_t^{shape})=32.
$$

PointNet 的核心结构是 permutation-invariant：

$$
z^{shape}=\operatorname{MaxPool}_i(\operatorname{MLP}(p_i)).
$$

physical/pose 部分：

- 7-d physical property vector：mass, center of mass, coefficient of friction, scale, restitution；
- 10-d pose/state vector：object position, orientation quaternion, angular velocity；
- concat 后经 MLP projection 到 $z_t^{phys}\in\mathbb{R}^8$。

所以最终：

$$
\dim(z_t)=8+32=40.
$$

这个 oracle 不是可部署 policy，而是 upper-bound teacher。它回答的是：**如果 policy 知道 object extrinsics，任务能做多好？**

### 2.5 visuotactile transformer：从传感历史回归 $\hat z_t$

真实部署时 $z_t$ 不可得，因此训练 transformer：

$$
\hat z_t=\phi(f_T),
$$

其中：

$$
f_t=[f_t^{depth},f_t^{touch},q_t,a_{t-1}],
\qquad
f_T=\{f_{t-k},\ldots,f_t\}.
$$

depth branch：

- simulation：object foreground depth；
- real：RealSense D435 depth + SAM foreground segmentation；
- implementation：$60\times60$ depth image，经 ConvNet + global average pooling 得到 $f_t^{depth}\in\mathbb{R}^{32}$；
- training randomizes camera position/orientation/FOV/segmentation noise。

touch branch：

- simulation：直接用 simulator contact location；
- real：四个 omnidirectional vision-based tactile sensors，追踪最高 intensity/deformation keypoint；
- 每个 contact 表示为 8-d discretized fingertip location + finger index，共 9 维；
- 多 contact 时经 MLP 后 average pooling 得到 $f_t^{touch}\in\mathbb{R}^{32}$。

transformer：

- feature dimension 32；
- depth 2；
- self-attention heads 2；
- output $\hat z_t\in\mathbb{R}^{40}$。

训练目标包含两层：

$$
\mathcal{L}_{z}=\|z_t-\hat z_t\|_2^2,
$$

以及 action consistency：

$$
\mathcal{L}_{a}=\|a_t-\hat a_t\|_2^2,
$$

其中 $a_t$ 来自 oracle/privileged route，$\hat a_t$ 来自 predicted extrinsics route。这个 action loss 的意义是：$\hat z_t$ 不一定要重构所有物理真相，但必须保留控制决策所需的信息。

### 2.6 触觉表示：为什么 contact location 胜过 binary contact

本文的 tactile 不是直接把 tactile image 丢给大网络，而是强行压成低维 contact location：

$$
o_t^{touch}\in\mathbb{R}^{N_c\times 9}.
$$

每个 contact：

- 8-d one-hot：接触落在 fingertip frame 的哪个离散方向；
- 1-d / index：哪个 finger。

这是一种刻意的信息瓶颈：

- 舍弃 deformation magnitude、normal、scale 等高维细节；
- 保留 finger-gaiting 最需要的局部几何方向；
- 降低 sim-to-real gap，因为真实 tactile image 只需稳定追踪 contact keypoint。

Table 2 的关键结论是：binary contact 几乎不提供额外价值，因为 proprioception/action history 已经能隐含“有没有碰”；真正有价值的是“在哪个方向碰”。

这点和 [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] 形成有趣张力：

- Touch Dexterity：full-hand binary contact 足以做 blind rotation；
- RotateIt：对多轴 finger-gaiting，binary contact 不够，contact location 才关键。

差异不是矛盾，而是任务瓶颈不同：前者 bottleneck 是是否接触/全手覆盖，后者 bottleneck 是 contact direction for multi-axis control。

### 2.7 概念边界与符号陷阱

- **$z_t$ vs $\hat z_t$**：$z_t$ 是 privileged oracle latent，$\hat z_t$ 是部署时估计；所有 sim-to-real 能力都压在 $\hat z_t$ 是否保留 task-relevant extrinsics。
- **physical vector vs $z_t^{phys}$**：physical/pose 原始向量不是 8 维，8 维是 MLP 投影后的 encoding。
- **RotP 越小越好**：它是 undesired rotation magnitude，reward 中靠负权重惩罚。
- **每轴单独 vs multi-axis**：正文主实验每个 axis 单独训练；appendix 通过加入 $k$ 和 imitation objective distill multi-axis policy，且 RL-only multi-axis 不收敛。
- **real metric different**：真实世界没有 simulator angular velocity，只报告 radians rotated；不要把 real Fig.8 和 sim RotR 直接等同。
- **touch sensor image not used fully**：real tactile image 被压成 contact keypoint；论文 limitation 明说没有利用 full tactile image information。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设置 |
|---|---|
| Robot | Wonik AllegroHand, 4 fingers, 16 joints |
| Command rate | position commands at 20 Hz |
| Low-level controller | PD controller at 300 Hz |
| Depth sensor | Intel RealSense D435, about 36 cm from Allegro base |
| Tactile sensors | four omnidirectional vision-based tactile sensors at fingertips |
| Simulator | IsaacGym |
| Parallel envs | 32768 environments on 4 GPUs |
| Simulation frequency | 200 Hz |
| Control frequency | 20 Hz |
| Episode length | 400 control steps = 20 s |
| Reset condition | object falls below 13.5 cm relative to hand |
| PPO sample collection | 10 agent steps per env per iteration = 0.5 s |
| PPO epochs / batch / LR | 5 epochs, batch 32768, LR $5\times10^{-3}$ |
| Visuotactile optimizer | Adam, MSE loss, LR $3\times10^{-4}$ |

注意旧稿中常见的 “policy 10 Hz / PD 1 kHz” 不适用于这篇。RotateIt appendix 明确写的是 20 Hz commands、300 Hz PD、200 Hz simulation。

### 3.2 网络与随机化细节

| 组件 | 设置 |
|---|---|
| Oracle policy MLP | hidden/output dimensions $[512,256,128,16]$, ELU |
| Privileged encoder $\mu$ | MLP $[256,128,8]$, ReLU |
| PointNet encoder | MLP $[32,32,32]$ + max pooling |
| Depth input | $60\times60$ object depth |
| Depth feature | ConvNet + global average pooling → 32 dim |
| Touch MLP | contact 9-d → MLP $[32,32,32]$ → average pooling |
| Proprio/action encoder | two-layer MLP $[32,32]$ |
| Transformer | feature dim 32, depth 2, 2 heads |

Physical randomization:

| Parameter | Range |
|---|---|
| Object scale | $[0.46,0.68]$ |
| Mass | $[0.01,0.25]$ kg |
| Center of mass | $[-1,1]$ cm |
| Coefficient of friction | $[0.3,3.0]$ |
| External disturbance | scale $2m$, resample probability 0.25 |
| PD stiffness | $[2.9,3.1]$ |
| PD damping | $[0.09,0.11]$ |

Vision randomization:

| Setting | Cam Pos | Cam RPY | Cam FOV | Seg Noise | Seg Failure | RotR |
|---|---:|---:|---:|---:|---:|---:|
| Perfect Vision | 0 | 0 | 0 | 0 | 0 | 119.19 |
| Same Noise as training | $\mathcal{N}(0,0.01)$ | $\mathcal{N}(0,0.03)$ | $\mathcal{U}(52,58)$ | 0.2 | 0.05 | 118.42 |
| OOD Noise | $\mathcal{N}(0,0.015)$ | $\mathcal{N}(0,0.035)$ | $\mathcal{U}(48,62)$ | 0.25 | 0.075 | 115.30 |
| Larger Noise | $\mathcal{N}(0,0.02)$ | $\mathcal{N}(0,0.04)$ | $\mathcal{U}(45,65)$ | 0.3 | 0.1 | 102.80 |
| No Vision | / | / | / | / | / | 99.29 |

因果解释：vision branch 对 calibration/segmentation noise 有一定鲁棒性，但大噪声会明显伤性能；这说明 SAM/depth 不是免费信息源，真实部署要把 segmentation failure 当成系统风险。

### 3.3 Table 1：shape encoding 是否真的必要

| Method | x RotR | x TTF | x RotP | y RotR | y TTF | y RotP | z RotR | z TTF | z RotP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| HORA | $79.13\pm11.22$ | $0.52\pm0.02$ | $0.55\pm0.03$ | $82.25\pm14.21$ | $0.54\pm0.04$ | $0.44\pm0.01$ | $99.83\pm11.72$ | $0.60\pm0.03$ | $0.39\pm0.04$ |
| w/o shape | $85.10\pm12.56$ | $0.56\pm0.03$ | $0.39\pm0.03$ | $99.92\pm10.21$ | $0.62\pm0.04$ | $0.41\pm0.02$ | $129.38\pm10.26$ | $0.75\pm0.03$ | $0.29\pm0.01$ |
| Oracle | $125.23\pm16.24$ | $0.79\pm0.03$ | $0.35\pm0.02$ | $118.26\pm13.20$ | $0.79\pm0.05$ | $0.30\pm0.01$ | $140.90\pm17.26$ | $0.82\pm0.02$ | $0.27\pm0.01$ |

因果解释：

- adding pose/physical info without shape already improves z-axis a lot（99.83→129.38），说明 HORA 的 implicit adaptation 不是上界；
- shape 对 x-axis 的提升最大：85.10→125.23；
- y-axis 也明显：99.92→118.26；
- z-axis 提升较小但仍有：129.38→140.90。

这和 §2.2 的物理推导一致：非 z 轴更需要 shape-dependent torque/contact strategy；z-axis 更接近 HORA 已经擅长的方向。

### 3.4 OOD objects：shape / visuotactile 是否帮助泛化

Fig. 6 的两个数字很关键：

| Comparison | In-distribution → OOD drop |
|---|---:|
| Oracle with point cloud | 8% decrease |
| Oracle without point cloud | 22.6% decrease |
| Sensorimotor visuotactile | 15.4% decrease |
| Sensorimotor proprioception-only | 41.6% decrease |

因果解释：

- point cloud shape encoding 不只是提高 train objects 分数，还显著降低 OOD generalization drop；
- visuotactile sensing 不是只补一点 real-world noise，而是在 OOD objects 上把 drop 从 41.6% 压到 15.4%；
- 因此 RotateIt 的核心不是 overfit object list，而是让 policy 获得估计 object-specific extrinsics 的通道。

### 3.5 Table 2：tactile contact location 的证据

Table 2 是理解 tactile 表示的关键，因为它把 binary/contact-location/full-contact 分开了。所有方法都不使用 vision。

| Touch representation | x RotR | x TTF | x RotP | y RotR | y TTF | y RotP | z RotR | z TTF | z RotP |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| NoTouch | $79.37\pm8.72$ | $0.46\pm0.03$ | $0.55\pm0.02$ | $67.21\pm7.25$ | $0.48\pm0.02$ | $0.55\pm0.03$ | $108.25\pm10.92$ | $0.62\pm0.01$ | $0.43\pm0.02$ |
| Binary | $80.14\pm7.25$ | $0.47\pm0.02$ | $0.53\pm0.03$ | $66.29\pm8.53$ | $0.49\pm0.01$ | $0.56\pm0.04$ | $110.24\pm9.48$ | $0.63\pm0.03$ | $0.42\pm0.02$ |
| ContactLoc | $102.36\pm9.82$ | $0.65\pm0.04$ | $0.41\pm0.04$ | $92.22\pm7.69$ | $0.64\pm0.01$ | $0.36\pm0.03$ | $122.60\pm10.39$ | $0.73\pm0.02$ | $0.35\pm0.01$ |
| Full | $104.29\pm10.29$ | $0.68\pm0.04$ | $0.41\pm0.02$ | $93.05\pm9.28$ | $0.65\pm0.01$ | $0.34\pm0.03$ | $126.73\pm10.11$ | $0.72\pm0.03$ | $0.32\pm0.03$ |

因果链：

`NoTouch → Binary` 几乎不变，因为 proprio/action history 已经暗含接触是否发生；

`Binary → ContactLoc` 大幅提升，因为 finger-gaiting 需要知道接触在 fingertip 上的方向；

`ContactLoc → Full` 提升很小，说明本文任务中低维 contact location 捕获了多数可迁移 tactile signal。

这对 LinkerHand tactile arrays 很重要：不要默认“全 tactile map 输入越多越好”。应该先问控制瓶颈是 contact existence、contact location、normal/shear，还是 deformation magnitude。

### 3.6 Table 4：vision、touch、transformer 的组合效应

Appendix Table 4 更完整地比较了 modality 和 sequence model。核心数字：

| Model / Modality | x RotR | y RotR | z RotR | 机制解释 |
|---|---:|---:|---:|---|
| Conv, no vision/touch | 66.23 | 54.19 | 89.21 | 当前帧/弱时序下 proprio-only 不够 |
| Conv, both vision+touch | 98.20 | 89.82 | 113.26 | 多模态有用，但 temporal modeling 不足 |
| Transformer, no vision/touch | 79.37 | 67.21 | 108.25 | 只换 transformer 已提高，说明 history matters |
| Transformer, both vision+touch | 118.42 | 109.31 | 136.25 | 接近 oracle，说明时序多模态能恢复 task-relevant extrinsics |
| Oracle | 125.23 | 118.26 | 140.90 | privileged upper bound |

因果解释：

- Conv → Transformer 的提升说明 extrinsics 不是单帧可估计，而是要从动作-响应历史中 system ID；
- no vision/touch → both 的提升说明 proprioception alone 对复杂/OOD shapes 不足；
- transformer + visuotactile 接近 oracle，证明 $\hat z_t$ 捕获了相当多控制相关 extrinsics。

### 3.7 Fig. 7：latent 里真的有 shape 吗

论文冻结四个 policies，收集 20 个 objects 上的 extrinsic vectors，再训练 decoder 从 subsequence of extrinsic vectors 预测 voxel grid。结果：

- oracle with shape 的 $z_t$ 能重构 shape；
- stage2 visuotactile $\hat z_t$ 也保留了可恢复的 shape 信息；
- proprioception-only 可以区分 sphere vs cuboid 这类粗类别；
- irregular objects（pear 等）需要 vision/touch 才能更好理解。

这个实验不是为了做 3D reconstruction，而是做 representation audit：

> 如果 $\hat z_t$ 真的是“object extrinsics”，它应该包含能解释 object shape 的信息；Fig. 7 是对 latent semantics 的间接验证。

对 WMTS 的启发是：不要只看 latent policy performance，可以用 auxiliary decoder / probe 检查 latent 是否真的编码了你声称的物理变量。

### 3.8 Fig. 8：真实机器人 x-axis 结果

真实世界只量化比较 x-axis rotations，因为这是 HORA 的明显弱项。

| Object | HORA rotations | RotateIt rotations |
|---|---:|---:|
| Cocoon | $0.54\pm0.39$ | $12.71\pm1.29$ |
| Squishy | $0.50\pm0.47$ | $8.29\pm1.73$ |
| Baseball | $0.26\pm0.19$ | $6.72\pm0.91$ |
| Puzzle | $0.48\pm0.25$ | $6.12\pm0.79$ |
| Box | $0.52\pm0.18$ | $5.05\pm0.87$ |
| Stego | $0.46\pm0.23$ | $5.01\pm0.79$ |

因果解释：

- HORA 基本停留在 in-grasp movement，不能完成 x-axis finger-gaiting；
- RotateIt 在 20 s 内可以转约 $2\pi$ 到 $4\pi$ 甚至更多；
- Cocoon / Squishy / Box / Stego 等很多 real objects 不在 training set，说明不是记忆对象外观；
- 但真实实验重点是 x-axis，不能把它解释为“所有任意轴都已充分量化验证”。论文把其他轴和 beyond-canonical axes 主要放在 website qualitative videos。

### 3.9 Appendix Table 3：multi-axis policy 的 nuance

正文说每个 rotation axis 单独训练 policy。Appendix A.2 展示可以 distill 一个 multi-axis policy：

| Method | +x | -x | +y | -y | +z | -z |
|---|---:|---:|---:|---:|---:|---:|
| Single-axis | $110.19\pm8.26$ | $104.29\pm10.29$ | $93.05\pm9.28$ | $90.20\pm10.39$ | $124.91\pm8.78$ | $126.73\pm10.11$ |
| Multi-axis | $105.21\pm9.27$ | $103.11\pm10.17$ | $85.38\pm9.71$ | $89.83\pm10.11$ | $125.32\pm7.81$ | $125.19\pm9.93$ |

关键 nuance：

- multi-axis distilled policy 接近 single-axis oracle；
- 但论文明确说 only-RL multi-axis 不收敛，需要加入 $k$ 并用 corresponding single-axis oracles 的 imitation objective；
- 因此 RotateIt 不是从零直接学出 arbitrary-axis RL controller，而是先通过 single-axis experts，再 distill。

这对 WMTS 很有价值：generalist policy 很可能需要 specialist oracles 提供 distillation 数据，而不是期待一个统一 PPO 从零吞下所有技能。

## 4. 核心洞见

### 4.1 真正的 insight：多轴旋转是 extrinsics identification，不只是 control

RotateIt 的最大 insight 是把多轴旋转拆成：

$$
\text{multimodal history}
\to
\hat z_t \text{ (shape/physics/task extrinsics)}
\to
\text{axis-conditioned finger-gaiting action}.
$$

这和端到端 sensorimotor policy 的区别在于，RotateIt 明确承认“当前 observation 不足以决定动作”，必须通过历史推断：

- 这个物体形状导致哪些接触策略可行；
- 当前 contact 在 fingertip 的什么方向；
- 物体对上一段动作的响应暗示了什么 mass/friction/shape；
- 目标轴 $k$ 下，哪些 off-axis rotations 必须被抑制。

### 4.2 为什么这个设计有效

它有效不是因为 transformer 神奇，而是因为输入和任务 bottleneck 对齐：

| Bottleneck | RotateIt 给的信号 | 为什么对齐 |
|---|---|---|
| shape/inertia unknown | depth + PointNet-supervised latent | 非 z 轴 torque/contact strategy 依赖 shape |
| contact direction unknown | 8-bin fingertip contact location | finger-gaiting 需要知道该从哪边换指 |
| physical properties unknown | proprio/action response history | mass/friction 体现在动作后的物体响应 |
| single-frame ambiguity | transformer sequence | extrinsics 是从时间中的 input-output relation 推断 |
| sim-real visual clutter | SAM foreground depth + randomization | 减少 raw RGB/background gap |

### 4.3 什么时候会失效

论文自己承认几个边界：

- object 不能太长，例如 pencil or screwdriver；
- object 必须在 hand mechanical limits 内；
- policy 训练后冻结，部署时不能利用 real-world experience；
- tactile pipeline 只用低维 contact location，没有利用 full tactile image；
- vision pipeline 依赖 depth/SAM/camera calibration；
- multi-axis policy 需要 distillation，RL-only 不收敛。

对用户当前“转笔”方向，第一条尤其刺眼：论文直接排除了 pencil/screwdriver 这类长物体。也就是说，RotateIt 的方法不能直接作为 pen-spinning baseline，只能迁移它的 shape/contact/extrinsics 思想。

## 5. 替代方案与理论局限

### 5.1 理论维度

| 局限 | 根因 | 对研究判断的影响 |
|---|---|---|
| shape latent 来自 mesh/point cloud oracle | 训练时物体模型已知 | 对未知真实物体，$\hat z_t$ 只能近似 oracle latent |
| reward 仍依赖 simulator $\omega$ | real world 不能直接测 angular velocity | real fine-tuning / evaluation 难闭环 |
| contact representation 过低维 | 只保留 8-bin location | shear/slip/normal force 信息丢失，可能不够支持高速转笔 |
| inertia reasoning 是隐式的 | 没有显式建模 $I$ 或 contact wrench cone | 对 OOD 几何可能仍靠数据插值 |
| multi-axis from distillation | single-axis experts 先行 | 不是完全端到端任意轴 RL 解法 |

### 5.2 算法维度

| 替代路线 | 可能优势 | 相对 RotateIt 的风险 |
|---|---|---|
| RMA proprioception-only | 简洁、部署无需外部 camera/tactile | x/y/OOD shape 性能弱，real Fig.8 已暴露 |
| AnyRotate-style tactile goal curriculum | 更接近 arbitrary-axis rotation | 需要 dense tactile 和 moving-goal reward 设计 |
| DPF/belief estimator | 可解释、能输出 uncertainty | 对 high-dimensional shape/contact latent 可能表达不足 |
| end-to-end VLA / diffusion policy | 可融合更多感知和 language/task | 需要大量真实/仿真数据，且控制频率/latency 难保证 |
| explicit model-based contact planner | 物理解释强 | 对多物体、多接触 Sim-to-Real 很难建准 |

### 5.3 工程/实验维度

- 32768 envs + 4 GPUs 是重仿真训练路线，不是低资源可复现设置。
- Real-world quantitative table 只展示 x-axis，其他轴主要是 qualitative/video。
- SAM/depth pipeline 可能引入 latency；论文没有把 end-to-end perception latency 作为主要实验变量。
- 真实 tactile sensors 是 omnidirectional vision-based fingertip sensors，和 LinkerHand 的 tactile array/通信约束不同。
- 对长物体不适用，这直接限制转笔。
- policy frozen after training，不能利用真实失败数据继续适应。

## 6. 对用户研究的启发

### 6.1 对 LinkerHand / 转笔的直接迁移

RotateIt 不应被当作“转笔方法”，但它给了三个很强的设计启发。

**启发 1：转笔的 latent 不应只叫 object state，而要叫 task extrinsics。**

| RotateIt latent | 转笔可能对应 |
|---|---|
| $z^{shape}$ | 笔长、半径、重心、表面摩擦、笔帽/非对称结构 |
| $z^{phys}$ | mass、CoM、friction、restitution、moment of inertia |
| pose/angular velocity | pen axis、spin phase、angular velocity、aerial/contact mode |
| contact location | 哪个指节/触觉 taxel 区域接触，接触在笔周向的相位 |
| target axis $k$ | 当前 skill phase 的期望旋转轴/进动方向 |

**启发 2：contact location 比 contact existence 更可能是转笔瓶颈。**

转笔中“碰到了没有”通常不够，关键是：

- 接触点在指尖/指节上的位置；
- 接触点在笔身周向的相位；
- 是否发生 slip；
- normal/shear force 是否足以继续注入角动量。

所以 LinkerHand tactile 不应一开始就压成单个 binary。可以先比较三种 representation：

| Representation | 假设 | 可能结果 |
|---|---|---|
| binary contact | 只需要知道接触事件 | 简洁但可能无法控制相位 |
| contact centroid / patch location | 需要局部几何方向 | 更像 RotateIt，适合 finger-gaiting |
| full tactile map + learned encoder | shear/deformation 重要 | 表达强，但 sim-to-real 和 bandwidth 风险高 |

**启发 3：axis penalty 可以直接迁移。**

转笔也需要抑制非目标轴漂移。可以把 reward 写成：

$$
r_{\text{spin}}=\operatorname{clip}(\omega_{\text{pen}}\cdot k,r_{\min},r_{\max})
\lambda_{\perp}\|\omega_{\text{pen}}\times k\|_1
\lambda_{\text{drop}}r_{\text{drop}}
\lambda_{\text{contact}}r_{\text{contact}}.
$$

其中 $\lambda_{\perp}<0$，并像 RotateIt 一样 curriculum：先允许旋转起来，再逐步加强轴向约束。

### 6.2 对 WMTS 的结合

RotateIt 可以被放进 WMTS 的 “specialist → generalist” 证据链：

| WMTS 模块 | RotateIt 提供的模板 | 应如何改造 |
|---|---|---|
| latent task generation | axis $k$ / skill-specific target | 生成 skill phase、axis、contact mode，而不是只给自然语言目标 |
| PPO Oracle | privileged oracle $\pi(p,z)$ | critic/teacher 可用 sim extrinsics；actor/generalist 必须用 estimated latent |
| Diffusion/Flow generalist | distill from specialist oracles | 像 appendix multi-axis，用 specialist data 训练 unified policy |
| Ensemble World Model | predict extrinsics/belief transition | ensemble disagreement 标记 shape/contact uncertainty |
| real-robot fine-tuning | 当前 RotateIt 不做 | WMTS 应补上 real failure buffer 和 online adaptation |

最重要的 project-level insight：

> 不要指望一个 generalist policy 从零学会所有轴/所有物体/所有接触模式。RotateIt 的 appendix 已经暗示：single-axis specialists + imitation/distillation 可能比 pure multi-task RL 更可靠。

### 6.3 可验证实验建议

| 实验 | Baselines | 指标 | 证伪标准 |
|---|---|---|---|
| 转笔是否需要 contact location | binary vs centroid/location vs full tactile map | spin duration, phase error, drop rate | binary 与 location 持平则 RotateIt-style location 不是瓶颈 |
| axis penalty curriculum 是否必要 | fixed $\lambda_\perp$ vs curriculum $\lambda_\perp$ | initial learning speed, final axis drift | curriculum 不改善则可能已有足够稳定 axis prior |
| specialist→generalist 是否优于 pure multi-task PPO | per-skill PPO distillation vs unified PPO from scratch | success across skills/phases | unified PPO 同等好则不必复杂 distillation |
| extrinsics latent 是否可解释 | auxiliary decoder/probe predicts pen CoM/friction/phase | probe accuracy + policy success correlation | probe 好但 policy 不好说明 latent semantic 不等于 control-useful |
| vision 是否值得 | proprio+tactile vs proprio+tactile+vision | latency-adjusted success | vision 提升小于 latency 代价则不部署 |

### 6.4 不应过度外推的点

- RotateIt 明确假设 object 不太长；pen spinning 正好是长物体，这是硬边界。
- 它用 Allegro + external RGBD + fingertip tactile；LinkerHand 的 actuator/tactile bandwidth 不同。
- 它的真实量化主表是 x-axis，不是完整 arbitrary-axis real benchmark。
- 它的 tactile image 被压成 contact location；不能证明 full tactile image learning 没必要。
- 它 frozen after training；不能说明 online real-world adaptation 已解决。

## 7. 与知识体系的联系

### 7.1 与 [[Dynamics]] 的联系

RotateIt 的 shape result 可以从刚体动力学读出：

$$
\tau=I\dot{\omega}+\omega\times(I\omega),
$$

其中 $I$ 由 shape/mass distribution 决定。非 z 轴/非主轴旋转更依赖 $I$ 和 contact wrench，因此 shape encoding 对 x/y axis 提升最大。

### 7.2 与 [[ReinforcementLearning]] 的联系

这是 privileged learning / teacher-student 的清晰实例：

$$
\pi_{\text{oracle}}(a_t\mid p_t,z_t)
\quad\to\quad
\pi_{\text{deploy}}(a_t\mid p_t,\hat z_t),
\qquad
\hat z_t=\phi(f_T).
$$

它提醒我们：privileged information 不能直接进部署 policy，必须通过可观测 history 估计。

### 7.3 与 [[RepresentationLearning]] 的联系

PointNet 提供 permutation-invariant shape latent：

$$
z^{shape}=\operatorname{MaxPool}_i(\operatorname{MLP}(p_i)).
$$

Transformer 则把 multimodal temporal stream 编码为 $\hat z_t$。Fig. 7 用 shape reconstruction probe 检查 latent 是否真的保留 shape，这种 probe 可迁移到 WMTS latent diagnostics。

### 7.4 与 [[SignalProcessing]] 的联系

RotateIt 的感知 pipeline 本质是三重 filtering：

- SAM/depth foreground filtering；
- tactile image → contact keypoint → 8-bin spatial quantization；
- transformer temporal filtering from noisy multimodal history。

这不是“更多传感器就更好”，而是把每个传感器压到 sim-to-real 可承受的信息形式。

### 7.5 与 [[ContactMechanics]] 的联系

Table 2 说明 contact existence 和 contact location 的物理含义不同。多轴 finger-gaiting 需要知道接触位置，因为接触点决定可产生的 wrench：

$$
\tau_{\text{contact}} = r_{\text{contact}}\times f_{\text{contact}}.
$$

没有 $r_{\text{contact}}$ 的方向信息，policy 很难知道下一步换指应如何维持目标轴旋转。

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “为什么 shape 对 x/y 更重要？” | 从 $I$、$\omega\times(I\omega)$ 和 contact wrench 解释非主轴旋转 |
| “RotP 是什么？” | $\|\omega\times k\|$，衡量 off-axis angular velocity，越小越好 |
| “binary touch 为什么没用？” | proprio/action history 已含 contact existence；RotateIt 需要 contact location |
| “它是不是任意轴 policy？” | 正文每轴训练；appendix distill multi-axis，pure RL multi-axis 不收敛 |
| “真实结果最强证据是什么？” | Fig.8：HORA 约 0.3-0.5 rotations，RotateIt 约 5-12.7 rotations |
| “对转笔能直接用吗？” | 不能直接用；论文排除 pencil/screwdriver，能迁移的是 extrinsics/contact-location/axis-penalty 思想 |
| “WMTS 应吸收什么？” | specialist oracle → estimated latent → generalist distillation，外加 latent probe 和 real adaptation |

## References

- Haozhi Qi, Brent Yi, Sudharshan Suresh, Mike Lambeta, Yi Ma, Roberto Calandra, Jitendra Malik. *General In-Hand Object Rotation with Vision and Touch*. CoRL 2023.
- Qi et al. *In-Hand Object Rotation via Rapid Motor Adaptation*. CoRL 2022.
- Chen et al. *Visual Dexterity: In-Hand Dexterous Manipulation from Depth*. 2022.
