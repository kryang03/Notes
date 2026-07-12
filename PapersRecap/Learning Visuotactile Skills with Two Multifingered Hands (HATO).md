---
tags:
  - paper
  - bimanual-manipulation
  - dexterous-manipulation
  - visuotactile
  - teleoperation
  - imitation-learning
  - diffusion-policy
aliases:
  - HATO
  - Hands-Arms Tele-Operation
  - Visuotactile Bimanual
paper-year: 2024
read-date: 2026-02-01
venue: arXiv 2024
paper-pdf: "[[Papers/Learning Visuotactile Skills with Two Multifingered Hands.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ContactMechanics]]"
  - "[[StochasticProcess]]"
---

# Learning Visuotactile Skills with Two Multifingered Hands

> [!abstract] 核心贡献
> HATO 的 value add 不是又训练了一个 Diffusion Policy，而是把低成本 VR 双臂遥操作、双多指义肢手、60 通道连续触觉和异步 action-chunk diffusion deployment 接成一条可采集、可学习、可部署的真实双手灵巧操作数据链；它证明了在四个真实长时程任务中，触觉和腕部视觉不是装饰传感器，而是 rare initialization 与 tool-use 成败的闭环观测。

> [!tip] 与理论基础的关联
> - [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|RepresentationLearning §2.2]]：把 action chunk 的条件分布 $p(a_{t:t+H-1}\mid o_t)$ 写成 DDPM 去噪生成，而不是单点 MSE 回归。
> - [[RepresentationLearning#5. 多模态融合：视触觉的交响|RepresentationLearning §5]]：视觉、触觉、本体感觉先独立编码再 concat，是 late-fusion visuotactile policy 的典型形态。
> - [[ContactMechanics#1. 接触：灵巧操作的灵魂|ContactMechanics §1]]：多指手的接触面积、接触冗余和触觉观测共同解释夹爪 teleop 的失败模式。
> - [[StochasticProcess#扩散模型与生成式策略|StochasticProcess: diffusion policy]]：DDPM 前向加噪、反向去噪和 score/噪声预测是动作分布建模的概率根。
> **核心技术**: hands-arms teleoperation, Psyonic Ability Hand repurposing, 60-channel fingertip tactile sensing, RGB-D wrist/head cameras, Diffusion Policy, asynchronous inference, temporal ensemble.

---

## 0. 阅读定位与范本价值

这篇 paper 在知识库里应该被放在三条线的交点：

1. **双手多指遥操作数据线**：它接在 [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]] / ALOHA 之后，但把 gripper 换成 two multifingered hands，并加入 tactile。
2. **视触觉真实策略线**：它和 [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]]、[[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]、[[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] 同属“接触观测如何进入策略”的问题。
3. **Diffusion Policy 部署线**：它沿用 Diffusion Policy 的 action chunk 生成，但加入 asynchronous inference + temporal ensemble，解决真实双臂多指系统上模型推理和执行不同步导致的动作抖动。

它的范本价值不在理论新颖性，而在**把一个困难系统工程问题拆成可被学习算法吃下去的数据接口**。

| 范本要求 | 本文应回答的问题 | 本 recap 落点 |
|---|---|---|
| 逻辑与价值 | 为什么双多指手 + 触觉 + VR teleop 是对 ALOHA/夹爪路线的结构增量？ | §1 写清 teleop prior 和 morphology prior |
| 原理与理论 | Quest controller 如何映射到 hand-arm commands？Diffusion Policy 如何建模 24D action chunk？ | §2 从映射、BC、DDPM、异步部署无跳步推导 |
| 实验与验证 | Table I-IV / Fig.5-8 的数字如何证明“触觉与腕部视觉是闭环观测”？ | §3 用 success rate、rare init、Steak Serving 和 ActionMSE 张力解释 |
| 未来与结合 | 对 LinkerHand 转笔、WMTS 数据飞轮、PPO Oracle 有什么可借、什么不能借？ | §5-7 给出迁移表、实验建议和不外推边界 |

---

## 1. 问题设定与动机

### 1.1 一句话核心

HATO 要解决的问题是：真实双臂多指灵巧操作缺少一种低成本、可上手、能同步记录视觉/触觉/本体/动作的 demonstration pipeline；没有这条数据链，再强的 imitation learning policy 也没有高质量行为分布可学。

### 1.2 直观隐喻

ALOHA 像是用两把夹子教机器人做家务；HATO 像是给机器人换上两只有触觉的“简化人手”，但操作员不是逐个控制每根手指，而是用一个 grip button 发出 power grasp，用 thumbstick 控制拇指。

这个隐喻的可证伪点是：

- 如果多指形态真的只是“看起来像人手”，那么换成 parallel-jaw gripper 时不应出现系统性滑落、支撑不足和不稳定抓取。
- 如果触觉只是多余输入，那么在 rare rotated block 或 Steak Serving 中去掉 touch 不应让 success 从可完成变成 0/10。

论文的实验恰好验证了相反结论。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 |
|---|---|---|
| ALOHA / Mobile ALOHA 式双臂夹爪 | 低成本、可规模化 teleop；gripper 简单可靠 | 末端只有少量接触自由度，遇到滑溜/大物体/工具支撑时 teleop 失败模式明显 |
| 单手灵巧操作系统 | 多指形态和 in-hand manipulation 能力 | 无法覆盖递送、倒酒、托盘/工具这类需要左右手互补约束的任务 |
| 视觉 + 本体模仿学习 | 从 demonstration 中直接回归动作 | 遮挡与接触阶段不可见，ActionMSE 低不等于任务成功 |
| 高自由度手套/外骨骼 teleop | 更接近人手 finger pose | 设备昂贵、穿戴/标定复杂，延迟和形态 retargeting 可能降低数据效率 |
| 纯仿真 RL / sim-to-real | 可无限采样、可用 privileged state | 双手多指接触仿真 gap 大，真实复杂任务仍需要 high-quality real demonstrations |
| 高精触觉或 GelSight | 能提供几何/剪切/法向细节 | 集成复杂，成本和体积影响多指手部署；HATO 先证明低维连续触觉也有价值 |

### 1.4 Delta 分析

| 维度 | 旧路线 | HATO 的增量 | 真正 value add |
|---|---|---|---|
| 末端执行器 | 双臂夹爪或单灵巧手 | two UR5e + two Psyonic Ability Hands | 把双手协作和多指接触同时纳入数据链 |
| 遥操作接口 | 教导臂、手套、外骨骼、gripper open/close | Quest controller pose + grip + thumbstick | 用低维人机接口换取数据采集的可操作性 |
| 触觉 | 无触觉或单手触觉 | 每个 fingertip 6 sensors，双手 60 通道连续 tactile | 让 policy 直接观测接触发生与接触强弱的变化 |
| 学习算法 | BC / ACT / Diffusion Policy | observation horizon 1 + 16-step action chunk DDPM | 保持现成 DP 优势，把系统贡献集中在数据和部署 |
| 部署 | 同步推理后执行 action sequence | remote inference server + temporal ensemble | 缓解 diffusion inference 慢导致的真实机器人动作不连续 |
| 证据 | 多数只展示任务成功 | success + ActionMSE + modality/camera/data-size ablations | 显示“预测误差低”和“任务能成”之间并不等价 |

---

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $T^Q_t$ | $SE(3)$ | Quest controller pose | 否，teleop 输入 | 人手控制器位姿 | 不是 robot EEF pose，需要坐标变换 |
| $T^{EEF,*}_t$ | $SE(3)$ | teleop mapping | 否 | 目标末端位姿 | IK 失败时沿用上次 joint command |
| $q^{arm,*}_t$ | $\mathbb{R}^{12}$ | IK / onboard controller | 否，action label | 两个 UR5e 的 12 个目标关节角 | action 是 target joint positions，不是 torque |
| $g_t$ | $[0,1]$ | Quest grip button | 否 | 四个非拇指的 power grasp 强度 | 一个标量控制 4 个手指，牺牲独立 finger gaiting |
| $u_t$ | $[-1,1]^2$ | Quest thumbstick | 否 | 拇指 2-DoF 控制 | thumbstick 坐标不是笛卡尔 fingertip pose |
| $q^{hand,*}_t$ | $\mathbb{R}^{12}$ | grip/thumb mapping | 否，action label | 两只 Ability Hands 的目标 finger positions | 每只手 6 actuated DoF：4 fingers + 2 thumb |
| $x^{prop}_t$ | EEF pose + finger/arm proprio | observation | 否，policy 输入 | 本体状态 | policy 使用 EEF pose，不把 arm joint position 当主要 proprio |
| $I_t$ | $3\times240\times320$ RGB-D streams | cameras | 否，policy 输入 | 两个 wrist views + 一个 third-view | 论文发现 depth 不明显有益，RGB/wrist 更关键 |
| $h_t$ | $\mathbb{R}^{60}$ | fingertip tactile sensors | 否，policy 输入 | 双手 60 个连续压力读数 | 不是 calibrated force vector；无接触约 200-400 ADC，接触常 >1000 |
| $o_t$ | multimodal embedding | encoder output | 是，训练图中 | diffusion policy 的条件向量 | late fusion；没有 cross-attention 或显式 contact graph |
| $a_t$ | $\mathbb{R}^{24}$ | demonstration action | 否，label；预测时是输出 | 12 arm joint targets + 12 hand joint targets | 24D action chunk，不是 human command 原始量 |
| $a_{t:t+15}$ | $\mathbb{R}^{16\times24}$ | action sequence label/output | 训练 label / policy output | 1.6s 左右的 future target-joint sequence（10Hz 数据） | action horizon 与 diffusion denoising step 是两个不同时间轴 |
| $k$ | $\{1,\dots,K\}$ | diffusion denoising index | 否 | 加噪/去噪步 | $k$ 不是 robot time $t$ |
| $\epsilon_\theta$ | neural network | learned model | 是 | 预测加入 action chunk 的噪声 | 条件是当前 $o_t$，不是 learned dynamics rollout |

### 2.2 Teleoperation mapping：从人类控制器到机器人动作标签

HATO 的第一层理论不是概率模型，而是一个**低维控制先验**：让操作员不用控制完整手指空间，也能产生稳定、可学习的双手多指行为。

从坐标变换开始。Quest controller 给出人的手柄位姿：

$$
T^Q_t \in SE(3)
$$

通过一次标定得到从 Quest 坐标系到 robot base 坐标系的变换 $T^{R}_{Q}$，再得到目标末端位姿：

$$
T^{EEF,*}_t = T^{R}_{Q} T^Q_t T^{offset}
$$

这里 $T^{offset}$ 表示手柄握持姿态到机器人末端工具坐标的固定偏移。然后用逆运动学求 UR5e 目标关节：

$$
q^{arm,*}_t = IK(T^{EEF,*}_t)
$$

若 IK 失败，系统使用上一时刻的 commanded joint positions。这不是优雅的最优控制，但对 teleop 数据采集很实用：它避免一个瞬时 IK failure 把整条 demonstration 打断。

手部控制更关键。每只 Psyonic Ability Hand 的可控手部空间可以写成：

$$
q^{hand,*}_t =
\begin{bmatrix}
q^{index}_t \\
q^{middle}_t \\
q^{ring}_t \\
q^{little}_t \\
q^{thumb,flex}_t \\
q^{thumb,abd}_t
\end{bmatrix}
\in\mathbb{R}^{6}
$$

HATO 不让操作者逐个控制这 6 个量，而是做低维映射：

$$
q^{nonthumb,*}_{t,j} = q^{min}_j + g_t(q^{max}_j-q^{min}_j), \quad j=1,\dots,4
$$

$$
\begin{bmatrix}
q^{thumb,flex,*}_t\\
q^{thumb,abd,*}_t
\end{bmatrix}
= A u_t + b
$$

其中 $g_t$ 是 grip button 的按压程度，$u_t$ 是 thumbstick 的二维读数。这个设计的本质是把手部动作空间压成：

$$
\underbrace{\mathbb{R}^{6}}_{\text{每只手可控 DoF}}
\quad\longrightarrow\quad
\underbrace{\mathbb{R}^{3}}_{\text{grip + thumbstick}}
$$

这就是 HATO 最重要的 trade-off：

- 好处：power grasp 是大量日常双手任务的强先验，操作者 5-10 分钟就能上手，能在几小时内采集数百条 demonstration。
- 代价：独立 finger gaiting、滚动重抓、笔杆在指间连续滚动这类技能不在数据分布里。

所以 HATO 对“拿稳、递送、堆叠、倒酒、用工具托住”很合适，但不能直接作为转笔/pen spinning 的高自由度 demonstration pipeline。

### 2.3 从行为克隆到 Diffusion Policy：为什么不是单点 MSE

给定当前 observation $o_t$，imitation learning 的目标是学习人类 demonstration 的条件动作分布：

$$
p_{\mathcal{D}}(a_{t:t+H-1}\mid o_t)
$$

最朴素的行为克隆会训练一个确定性函数：

$$
\hat{a}_{t:t+H-1}=f_\theta(o_t)
$$

并最小化：

$$
\mathcal{L}_{MSE}(\theta)=
\mathbb{E}_{(o,a)\sim\mathcal{D}}
\left[\left\|a_{t:t+H-1}-f_\theta(o_t)\right\|^2\right]
$$

这个目标隐含一个强假设：同一个 observation 下只有一个“平均动作”是合理的。但双手多指操作常常是多峰的：同样要托住物体，左手可以微调，右手也可以微调；同样要把 spatula 插到 steak 下方，角度、速度和接触时机都有多个可行模式。

Diffusion Policy 的增量是把动作 chunk 当作条件生成对象。令 clean action chunk 为：

$$
a^0 \equiv a_{t:t+15} \in \mathbb{R}^{16\times24}
$$

DDPM 前向过程逐步加噪：

$$
q(a^k\mid a^{k-1})=
\mathcal{N}\left(
a^k;
\sqrt{1-\beta_k}a^{k-1},
\beta_k I
\right)
$$

定义：

$$
\alpha_k=1-\beta_k,\qquad
\bar{\alpha}_k=\prod_{i=1}^{k}\alpha_i
$$

则反复代入可得到闭式采样式：

$$
a^k = \sqrt{\bar{\alpha}_k}a^0+
\sqrt{1-\bar{\alpha}_k}\epsilon,\qquad
\epsilon\sim\mathcal{N}(0,I)
$$

训练时网络看到 noisy chunk $a^k$、扩散步 $k$ 和条件 observation $o_t$，预测噪声：

$$
\epsilon_\theta=\epsilon_\theta(a^k,k,o_t)
$$

优化目标是：

$$
\mathcal{L}_{DDPM}(\theta)=
\mathbb{E}_{a^0,o_t,k,\epsilon}
\left[
\left\|\epsilon-\epsilon_\theta(a^k,k,o_t)\right\|^2
\right]
$$

HATO 沿用 Diffusion Policy 的设置：

| 设计项 | HATO 选择 | 机制含义 |
|---|---|---|
| Observation horizon | 1 | 只用当前 observation，训练更快；但历史接触记忆弱 |
| Action horizon | 16 | 一次预测 16 个 24D target-joint actions |
| Training diffusion steps | 100 | 训练时的去噪链长度 |
| Inference diffusion steps | 15 | 部署时加速采样 |
| Visual encoder | per-camera ResNet-18 + GroupNorm, output 32 | 三路相机不共享权重 |
| Proprio/touch encoder | 2-layer MLP, hidden 256, output 64 | 本体和触觉各自编码 |
| Optimizer | AdamW, lr $10^{-4}$, weight decay $10^{-5}$, batch 128 | 论文明确给出的训练细节 |
| EMA | evaluation/deployment 使用权重 EMA | 降低 diffusion policy 输出抖动 |

需要注意：HATO 的 diffusion policy 不是 world model，也不预测下一帧视觉/触觉。它只建模：

$$
o_t \longmapsto p_\theta(a_{t:t+15}\mid o_t)
$$

所以它的闭环能力完全依赖下一控制步重新观测并重新采样，而不是在 latent dynamics 里规划。

### 2.4 异步部署：为什么 action chunk 还需要 temporal ensemble

真实系统上的 diffusion inference 比普通 MLP 慢。如果简单“等模型生成完整 sequence，再执行”，机器人会卡顿；如果执行旧 sequence 太久，又会变成开环。

HATO 的部署逻辑是：

1. local process 每个控制步发送最新 observation 和对应 timestep；
2. remote inference server 持续用最新 observation 运行 diffusion model；
3. 每次生成一个带 timestep 的 future action sequence；
4. local process 对多个预测序列中指向同一执行时刻的 action 做平均，类似 ACT 的 temporal ensemble；
5. 执行平滑后的 target joint positions。

可以把某个真实执行时刻 $\tau$ 的动作写成：

$$
\bar{a}_{\tau}
=
\frac{\sum_{m\in\mathcal{M}(\tau)} w_m a^{(m)}_{\tau}}
{\sum_{m\in\mathcal{M}(\tau)} w_m}
$$

其中 $m$ 表示不同 inference call 产生的 action sequence，$\mathcal{M}(\tau)$ 是覆盖时刻 $\tau$ 的预测集合。

这个机制的核心不是“平均让一切更好”，而是一个工程权衡：

- 平均能抑制 diffusion sample-to-sample jitter；
- 但平均也可能把接触切换处的多峰动作抹平；
- 因此它适合 HATO 这类慢速、长时程、抓持稳定任务，不一定适合转笔中的快速接触切换。

### 2.5 符号与概念陷阱

| 陷阱 | 正确理解 | 为什么重要 |
|---|---|---|
| robot time $t$ vs diffusion step $k$ | $t$ 是真实控制时刻，$k$ 是对同一个 action chunk 的去噪索引 | 混淆后会误以为 diffusion 在预测物理时间演化 |
| touch $h_t$ vs force $F_t$ | $h_t$ 是连续 ADC sensor readings，不是标定后的 3D force/shear | 不能把 HATO 说成显式力控 |
| action MSE vs success | MSE 衡量 imitation prediction error，不等于闭环任务完成率 | Steak Serving 中 no-touch MSE 低但 success 0/10 |
| power grasp prior vs dexterity | 低维 grip/thumb mapping 能稳定抓持，但限制独立手指策略类 | 对转笔不能直接照搬 |
| wrist camera vs depth | 腕部 RGB 视角给任务相关局部线索；depth 噪声反而可能伤害 | “更多传感器”不等于更好的 observation |
| teleop data quality vs policy algorithm | HATO 的主要贡献在数据接口，不是发明新 diffusion objective | 评价 novelty 时不能把 Diffusion Policy 的贡献算给 HATO |

---

## 3. 训练、数据与实验

### 3.1 系统与任务设置

| 项目 | 论文设置 |
|---|---|
| Robot arms | 2× UR5e, each 6 DoF |
| Robot hands | 2× Psyonic Ability Hands, each 6 actuated hand DoF |
| Tactile | each fingertip 6 touch sensors, total 60 readings for two hands |
| Cameras | 2 wrist-mounted RealSense + 1 stationary third-view RealSense |
| Vision stream | RGB-D 480×640, resized to 240×320 |
| Teleoperation | Meta Quest 2 controllers; pose→EEF, grip→non-thumb fingers, thumbstick→thumb |
| Data collection rate | 10 Hz |
| Policy | Diffusion Policy over 16-step, 24D action chunks |
| Action | desired joint positions for two arms and two hands: $12+12=24$ |
| Optimizer | AdamW, lr 0.0001, weight decay 0.00001, batch size 128 |
| Deployment | asynchronous remote inference + temporal ensemble; 15 diffusion steps |

四个任务：

| Task | 任务结构 | 为什么需要多指/双手 |
|---|---|---|
| Slippery Handover | 一只手拿起滑溜物体，递给另一只手 | 大接触面积减少滑落，双手协调递接 |
| Tower Block Stacking | 两手搬起两块大积木并堆到第三块上 | 平掌支撑和姿态稳定比夹爪更重要 |
| Wine Pouring | 一手持瓶、一手持杯，倒出珠子模拟液体 | 大物体 + 质心变化 + 双手稳定 |
| Steak Serving | 一手持锅、一手用 spatula 托起 steak 并送到盘子 | 工具使用、长 horizon、高精度接触 |

数据量：

| Task | demonstrations | 单条时长 | teleoperator practice |
|---|---:|---:|---:|
| Slippery Handover | 100 | about 6 s | 5-10 min |
| Tower Block Stacking | 100 | about 20 s | 5-10 min |
| Wine Pouring | 300 | about 25 s | 5-10 min |
| Steak Serving | 300 | about 40 s | 5-10 min |

### 3.2 主任务成功率：HATO 数据能学出真实策略，但难度差异很大

Table I 报告每个任务 10 次真实部署：

| Task | Pickup | Task Success | Observation used in Table I |
|---|---:|---:|---|
| Slippery Handover | 10/10 | 10/10 | image + proprioception |
| Tower Block Stacking | 10/10 | 10/10 | image + proprioception + touch |
| Wine Pouring | 10/10 | 9/10 | image + proprioception |
| Steak Serving | 10/10 | 5/10 | image + proprioception + touch |

**因果解释**：

HATO 的数据链足以支撑三类能力：递接、堆叠、倒酒。Steak Serving 只到 5/10，反而是最有价值的边界：它包含 tool insertion、托举、平衡和长 horizon 接触，说明当前 observation horizon=1 + BC action chunk 对长时程误差恢复仍不够。

不要把这张表读成“触觉在所有任务都必要”。论文自己指出 Handover 和 Wine Pouring 只用 image + proprioception 已接近 100%。触觉最有价值的地方是**接触不确定和 rare state 下的鲁棒性**，不是每个任务都必然提升平均 MSE。

### 3.3 数据规模：几十到几百条 demonstration 已经有边际饱和

Fig.6 用 held-out ActionMSE 研究数据量：

| Task | Demo counts tested | ActionMSE trend $(\times10)$ | 论文结论 |
|---|---|---|---|
| Slippery Handover | 25/50/75/100 | 0.86 → 0.43 → 0.34 → 0.25 | 100 条仍可能继续受益 |
| Block Stacking | 25/50/75/100 | 0.22 → 0.27 → 0.12 → 0.14 | around 75 demos saturates |
| Wine Pouring | 50/100/200/300 | 3.46 → 2.42 → 1.45 → 1.78 | around 200 demos saturates |
| Steak Serving | 50/100/200/300 | 0.13 → 0.09 → 0.08 → 0.08 | around 100 demos saturates |

**因果解释**：

这个结果说明 HATO 的 teleop interface 确实能产生可学习分布：不是必须上万条 trajectory 才能训练策略。但它也暴露 ActionMSE 的局限：Wine Pouring 300 条 MSE 比 200 条略高，Steak Serving MSE 很低仍只有 5/10 主任务成功。对接触任务，validation MSE 只能当粗略诊断，不能替代真实闭环 success。

### 3.4 模态消融：MSE 和 success 的张力是本文最重要的实验洞见

Fig.5 报告不同 sensing modality 的 ActionMSE：

| Task | Proprio only | No Vision | No Touch | Ours |
|---|---:|---:|---:|---:|
| Slippery Handover | 0.39 | 0.32 | 0.30 | 0.25 |
| Block Stacking | 0.17 | 0.16 | 0.15 | 0.14 |
| Wine Pouring | 5.06 | 3.22 | 1.93 | 1.78 |
| Steak Serving | 0.15 | 0.10 | 0.07 | 0.08 |

若只看 MSE，触觉在 Steak Serving 中似乎“不重要”，因为 no-touch 的 0.07 甚至低于 ours 的 0.08。但 Table III 显示：

| Steak Serving modality | Pickup | Success |
|---|---:|---:|
| Ours | 10/10 | 5/10 |
| without Touch | 10/10 | 0/10 |
| without Vision | 0/10 | 0/10 |
| EEF Only | 0/10 | 0/10 |

**因果链**：

`remove touch -> ActionMSE stays low or lower -> because dataset-average joint targets can still be predicted -> but contact/force phase during spatula transfer is unobserved -> closed-loop success collapses to 0/10`

这是本文真正应该被记住的 insight：**接触任务的关键观测可能只影响少数时间点，而这些时间点在 MSE 中权重很小，却决定任务成败。**

对用户的转笔/DNPM，这句话非常重要。pen spinning 的 slip、catch、release、recontact 都是稀疏关键相位；如果只用 action MSE 或轨迹误差评估，会错过触觉的真实价值。

### 3.5 Rare initialization：触觉和视觉提高鲁棒性，不只是拟合训练分布

Table II 对 Block Stacking 做 rare rotated block 初始化：

| Modality | Default Init. | Rare Init. |
|---|---:|---:|
| Ours | 10/10 | 10/10 |
| without Touch | 10/10 | 4/10 |
| without Vision | 10/10 | 0/10 |

**因果链**：

`rare rotated blocks -> grasp/support geometry deviates from common demonstrations -> vision estimates changed pose; touch reports whether multi-finger support actually formed -> policy can correct -> success remains 10/10`

`remove touch -> visual pose still available but contact stability hidden -> success drops to 4/10`

`remove vision -> rare geometry invisible -> policy cannot choose approach/support -> success 0/10`

这个实验比默认初始化更能证明 HATO 的 story。默认初始化三种设置都 10/10，说明在分布内开环回放就可能够用；rare init 才把闭环观测的价值显现出来。

### 3.6 Camera/depth ablation：腕部 RGB 比“更多深度”更可靠

Fig.8 比较 camera configuration 的 ActionMSE：

| Task | 3rd View Only | Ours with Depth | Ours |
|---|---:|---:|---:|
| Slippery Handover | 0.36 | 0.27 | 0.25 |
| Block Stacking | 0.17 | 0.15 | 0.14 |
| Wine Pouring | 1.72 | 2.29 | 1.78 |
| Steak Serving | 0.36 | 0.27 | 0.25 |

论文结论：

- wrist-view cameras 通常比 only third-view 更低 prediction error；
- depth 没有稳定收益，Wine Pouring 甚至更差；
- 作者推测 depth readings noise 伤害学习。

Table IV 还给出 Steak Serving 的 camera ablation：all-camera RGB without depth 是最强设置，加入 depth 或只保留部分相机都会显著变差。需要谨慎的是，Table IV 的 success 数字与 Table I 的 Steak Serving 5/10 主结果不是同一个稳定 headline；我在知识库里只把它当作“camera configuration 的方向性证据”，不把它合并成主成功率。

### 3.7 Parallel-jaw gripper 对比：不是定量表，但解释 morphology prior

论文用 Robotiq gripper 替换 Ability Hand 做 qualitative teleoperation 对比。夹爪常见失败模式包括：

| Failure mode | 机制解释 |
|---|---|
| small contact area | 滑溜/大物体需要更精确 grasp point |
| object slips | 单个夹持法向力不足以稳定复杂接触 |
| shaky hold | 缺少 palm/finger support surface |
| unstable grasp points | teleoperator 很难实时规划微小夹爪位置 |
| fail to balance object | 工具/托举任务需要分布式支撑 |

这不是严格 benchmark，但它在逻辑上支撑 HATO 的结构假设：多指形态先验不是为了“拟人”，而是为了让 teleoperation 的误差有接触冗余可以吸收。

---

## 4. 核心洞见

### 4.1 论文真正的 insight

HATO 的核心洞见是：**对真实双手灵巧操作，学习算法之前先要有一个可采集高质量 demonstration 的 morphology-interface-sensing 三元组。**

三元组分别是：

1. morphology：two multifingered hands 提供多接触点和支撑面；
2. interface：Quest grip/thumbstick 把高维手部控制压缩成可上手 power-grasp prior；
3. sensing：wrist RGB + tactile 让 policy 在闭环中知道物体在哪里、接触是否成立。

如果只拿其中一个元素，story 都不完整：

- 只有多指手，没有好 teleop，数据采不出来；
- 只有 teleop，没有触觉，策略对 rare contact state 不鲁棒；
- 只有 diffusion policy，没有数据链，只是在复用已有 imitation learner。

### 4.2 为什么这个设计有效

HATO 的有效性来自三个“降低难度”的操作。

第一，teleop mapping 降低人类控制难度。用 $g_t$ 控制四指 power grasp 是强 hand prior，它把大量日常任务中的“抓住/托住/支撑”变成一个连续标量。

第二，多指手降低接触规划精度要求。夹爪必须找到少数稳定夹持点，多指手可以用更大接触面和冗余支撑吸收 teleop error。

第三，Diffusion Policy 降低动作分布建模难度。它不要求把 16-step future 动作压成一个均值，而是用去噪过程近似条件动作分布。

### 4.3 什么时候会失效

HATO 会在以下情形变弱：

| 情形 | 失败原因 |
|---|---|
| 需要独立 finger gaiting | grip/thumbstick 数据分布没有独立手指相位 |
| 高速动态接触 | 10Hz demonstration 和 temporal averaging 可能错过 10-50ms contact transition |
| 需要剪切/滑移判断 | Ability Hand touch readings 是连续压力，不是 shear/slip sensor |
| 外观强变化 | policy 从 scratch 学，没有大规模视觉预训练 |
| 长 horizon recovery | BC 没有主动探索和失败恢复机制 |
| 精细力控 | action 是 target joint positions，不是 impedance/force control |

---

## 5. 替代方案与理论局限

### 5.1 理论维度

HATO 没有显式建模双手接触动力学。接触丰富操作的物理根可以写成：

$$
M(q)\ddot{q}+C(q,\dot{q})\dot{q}+g(q)
=\tau+J_c(q)^\top \lambda
$$

其中 $\lambda$ 是接触力，$J_c$ 是接触雅可比。HATO 的 policy 并不估计 $\lambda$，也不约束摩擦锥：

$$
\sqrt{\lambda_t^2+\lambda_b^2}\leq \mu \lambda_n
$$

它只是把 tactile readings $h_t$ 当 observation，让神经网络从 demonstration 中隐式学习“什么接触状态下该输出什么 joint target”。这使系统实用，但也意味着：

- 不能保证 force closure；
- 不能解释失败时是哪一个接触约束被破坏；
- 不能直接迁移到不同触觉传感器或不同手型，除非重新采数据或做表示对齐。

### 5.2 算法维度

| 替代方案 | 可能优势 | 相对 HATO 的问题 |
|---|---|---|
| ACT / CVAE action chunk | temporal ensemble 成熟，训练稳定 | 对多峰连续动作可行，但缺 diffusion 的 iterative refinement |
| State-based RL in sim | 可用 privileged state 和 reward | 双手多指触觉 sim-to-real gap 很大 |
| Residual RL on top of BC | 能学习 recovery 和 contact correction | 需要安全在线探索；HATO 论文没有这部分 |
| Contact-grounded generative policy | 可显式生成 contact-consistent actions | 需要 contact representation，HATO 只用 raw tactile readings |
| World model + MPC | 可在 latent 里评估候选动作 | HATO 没有 dynamics data/modeling objective，需另建预测目标 |
| Data glove teleop | 更高自由度 finger control | 成本、标定、retargeting 和延迟更高 |

### 5.3 工程/实验维度

1. **10 trials 很少**：Table I-IV 多数是 10 次部署，足以展示 feasibility，但不足以精确估计成功率分布。
2. **Table IV 与 Table I 需分开读**：Steak Serving 在主任务表是 5/10，但 camera ablation 表里 all-camera setting 又显示 10/10；这提示不同实验设置、训练 run 或 evaluation split 可能不完全一致。
3. **触觉没有 haptic feedback 给人**：human teleoperator 采数据时没有感受到机器人触觉，论文未来工作也指出 haptic feedback 可能提高数据质量。
4. **没有 multi-operator 统计**：5-10 分钟上手很吸引人，但不同操作者的数据质量差异未系统报告。
5. **没有强外观泛化**：作者自己承认 policy 从 scratch 学，容易受 scene appearance changes 影响。
6. **没有 sim-to-real**：这是 pure real-world IL pipeline，不解决仿真触觉建模。

---

## 6. 对用户研究的启发

### 6.1 对 DNPM / LinkerHand 转笔的直接迁移

HATO 可以借鉴，但不能直接复刻。

| HATO 变量/设计 | 在 LinkerHand 转笔中应变成什么 | 迁移判断 |
|---|---|---|
| grip scalar $g_t$ | 不应作为主控制接口；最多用于 canonical grasp 初始化 | 转笔需要独立 finger gaiting，单 scalar 太窄 |
| thumbstick 2D | 可类比少数关键手指的低维 phase command | 只能做慢速教学，不够覆盖高速转笔 |
| 60-channel tactile $h_t$ | LinkerHand tactile $5\times12\times6$ 或二值/低维 contact events | 强相关；应记录 contact timing、contact patch、滑移 proxy |
| 16-step action chunk | diffusion/flow generalist 的 short-horizon action plan | 可用，但 horizon/frequency 要按接触相位重调 |
| temporal ensemble | 真机部署动作平滑器 | 对慢任务有益；对 release/catch 相位可能抹掉尖锐动作 |
| wrist/third-view RGB | hand/object tracking camera | 对笔杆 pose 可观测性关键，但遮挡严重，需 tactile 补 |
| no haptic feedback teleop | data glove + vibrotactile/haptic feedback | 若要高质量转笔 demonstration，必须考虑反馈给人 |

最直接的启发是：**先不要一上来追求全自由度 teleop；可以先设计一个低维、任务相关、能稳定采数据的 human interface，但必须承认它定义了可学策略类的上界。**

对转笔，这个低维接口不能是 HATO 的 power grasp，而更可能是：

- canonical grasp + phase buttons；
- index/middle/thumb 的几个 principal components；
- contact-event guided correction；
- data glove 记录 full finger pose，但训练时再降维成 phase-conditioned action primitives。

### 6.2 对 WMTS 五模块的具体接法

WMTS pipeline 是：latent task generation → PPO Oracle specialist → Diffusion/Flow generalist → Ensemble World Model → real robot fine-tuning。HATO 可以放进三个位置。

| WMTS 模块 | HATO 可提供的东西 | 必须修改的点 |
|---|---|---|
| latent task generation | 从 teleop demonstrations 抽取可行接触模式和 task phases | 不要用 HATO 的低维 power grasp 定义所有任务空间 |
| PPO Oracle specialist | 用 HATO demonstrations 初始化 policy 或 replay buffer | PPO 仍要在仿真/真机中学 recovery，不应停留在 BC |
| Diffusion/Flow generalist | 直接借 action chunk 条件生成框架 | 条件输入要包括 tactile/contact phase，不只是 RGB/proprio |
| Ensemble World Model | HATO data 可作为真实 transition dataset | world model 要预测 tactile/contact next state，不能只预测 joint state |
| real robot fine-tuning | asynchronous inference + temporal ensemble 可作为部署平滑器 | 对快速接触相位要做 phase-gated smoothing，不能全程平均 |

一个具体改造：

$$
o_t^{WMTS} =
\left[
q_t,\dot q_t,
x^{pen}_t,
h^{tactile}_t,
\phi^{contact}_t,
\tau^{actuator}_t,
z^{task}_{t:t+H}
\right]
$$

其中 $\phi^{contact}_t$ 是从触觉/视觉估计的 contact phase，不是人工 task label。Diffusion/Flow generalist 预测：

$$
p_\theta(a_{t:t+H-1}\mid o_t^{WMTS})
$$

ensemble world model 则预测：

$$
p_{\psi_i}(o_{t+1}\mid o_t,a_t),\quad i=1,\dots,N
$$

并用 ensemble disagreement 区分“模型不知道的接触相位”和“策略本身差”。这比 HATO 的 pure BC 更适合 WMTS。

### 6.3 可验证实验建议

| 实验 | 对照组 | 关键指标 | 能证伪什么 |
|---|---|---|---|
| 转笔 tactile ablation | proprio+vision vs +binary contact vs +full tactile | success、catch timing error、slip rate、contact phase F1 | 如果 full tactile 不优于 binary/contact timing，说明任务主要需要接触时刻而非力分布 |
| Teleop interface ablation | HATO-like low-DoF command vs data glove high-DoF | demo success、policy success、finger phase diversity | 如果 low-DoF 接口学不出 finger gaiting，就不能作为转笔数据主线 |
| ActionMSE vs task success | 用同一 dataset 训练不同模态 policy | ActionMSE、real rollout success、critical phase error | 验证 HATO 的核心警告：MSE 低不代表接触任务能成 |
| Temporal ensemble ablation | no ensemble / uniform average / phase-gated average | smoothness、release/catch success、delay | 如果全程平均降低 catch 成功率，说明需要接触相位条件平滑 |
| Haptic feedback data quality | no feedback vs vibrotactile feedback to operator | teleop correction time、contact overshoot、demo discard rate | 验证 HATO 未来工作是否对转笔数据质量关键 |

### 6.4 不应过度外推的点

- 不要把 HATO 当作“触觉越多越好”的证据。它更准确地证明：在 rare contact state 和 high-precision tool-use 中，触觉可改变闭环成功率。
- 不要把 HATO 的 power-grasp mapping 当作灵巧手通用遥操作方案。它是为日常抓持/托举任务优化的，不覆盖转笔。
- 不要把 Diffusion Policy 成功归因给 HATO 的算法新颖性。算法主要来自 Diffusion Policy；HATO 的新意是数据和系统接口。
- 不要用 ActionMSE 作为唯一模型选择指标。Steak Serving 的 no-touch 设置已经说明 MSE 会误判。
- 不要默认 depth 有用。论文显示 noisy depth 可能伤害学习。

---

## 7. 与知识体系的联系

### 7.1 与 [[RepresentationLearning]] 的联系

HATO 是 late-fusion visuotactile representation 的工程范例：

$$
z_t =
\left[
f_{vis}(I_t),
f_{touch}(h_t),
f_{prop}(x^{prop}_t)
\right]
$$

它没有做 cross-attention 或 shared token pretraining，因此与 [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]] 形成对比：

- HATO：触觉直接作为 policy input，靠 task loss 学到何时使用；
- Visual-tactile Pretraining：先用 masked reconstruction / IPL token 学表征，再接 PPO/IL。

这个对比能帮助用户区分“触觉作为实时闭环观测”和“触觉作为预训练监督信号”。

### 7.2 与 [[ContactMechanics]] 的联系

HATO 的多指手优势对应接触力学中的接触冗余：

$$
G\lambda + w_{ext}=0
$$

其中 $G$ 是 grasp map，$\lambda$ 是所有接触点力。parallel-jaw gripper 的接触点少、支撑面小，teleop error 很难被接触冗余吸收；多指手和平掌提供更多可行 $\lambda$，使同样粗糙的人类遥操作也能稳定完成。

但 HATO 没有显式估计 $G$ 或 $\lambda$。这就是它的边界：它利用 contact redundancy，但不解释或保证 contact stability。

### 7.3 与 [[StochasticProcess]] / Diffusion Policy 的联系

HATO 的 action generation 是 DDPM 在 action space 上的条件采样：

$$
a^k = \sqrt{\bar{\alpha}_k}a^0+\sqrt{1-\bar{\alpha}_k}\epsilon
$$

$$
\epsilon_\theta(a^k,k,o_t)\approx\epsilon
$$

这和 image diffusion 的差别是：样本不是图片像素，而是 16-step robot action chunk。对机器人而言，denoising 的平滑性会转化成动作连续性，但也可能在接触切换处产生“平均动作”风险。

### 7.4 与现有 tactile/dexterous recaps 的关系

| 相关 recap | 与 HATO 的关系 |
|---|---|
| [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]] | HATO 继承低成本双臂 teleop 的思想，但把 gripper 升级为双多指手并加入 tactile |
| [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] | Robot Synesthesia 更强调 tactile point cloud / synesthetic representation；HATO 强调双手系统和 teleop data pipeline |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | Touch Dexterity 证明纯触觉能做 in-hand rotation；HATO 证明 vision+touch 对双手 tool-use/rare init 更鲁棒 |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] | CGP 把 contact grounding 放进生成模型；HATO 只做 raw tactile late fusion，机制更弱但系统更直接 |
| [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]] | 两者都强调低成本触觉；HATO 从 real teleop BC 学，Visual-tactile Pretraining 用 human observation 先学 multisensory representation |

---

### 7.5 簇内定位与暗线锚点（触觉操作簇）

在“触觉表征丰富度谱”上，HATO 位于**最朴素一端**：60 通道连续压力做 late fusion，不建模接触、不提取物理中间量。机制最弱，但采数据与部署最直接。

| 簇内对照 | Delta（本文相对它） |
|---|---|
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] | AnyRotate 把触觉压成物理中间量 $(R_x,R_y,\|F\|)$ 求 sim-to-real 对齐；HATO 直接喂 raw 连续压力做 concat，靠真实数据规模而非表征设计。 |
| [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] | CGP 把触觉当被预测+被执行的 contact latent；HATO 只把触觉当 observation late-fusion。CGP 有 contact grounding 机制，HATO 无。 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] | 都靠低成本触觉，但 Touch Dexterity 二值化求 sim-to-real 一致（纯仿真训练）；HATO 用连续压力做真实 teleop BC（无仿真）。 |

**精确 Foundation 锚点（补 §7.2 之外）**：

- [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|ReinforcementLearning §2.1]]：Steak Serving 的“no-touch ActionMSE 0.07 却 success 0/10”是部分可观 MDP 的教科书案例——contact phase 是 unobserved 关键相位，权重在平均误差里被稀释。
- [[SignalProcessing#4.1 早期滑移 (Incipient Slip) 检测|SignalProcessing §4.1]]：Ability Hand 的连续压力无 shear，做不了 §4.1 的 incipient slip，这是 HATO 迁移到转笔 release/catch 相位的硬边界。

**暗线挂载（POMDP → belief）**：本文最重要 insight（MSE↔success 张力）本质是“关键接触相位不可观”；触觉是把这一相位重新带回 observation 的解药，但连续压力 late fusion 不构造显式 belief，故 rare init 才把差距显出来。

---

## 8. 应主动追问的颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “HATO 相比 ALOHA 的真正 delta 是什么？” | 不是 Diffusion Policy，而是 gripper→multi-finger morphology、无触觉→60-channel tactile、同步部署→异步 temporal ensemble |
| “触觉到底证明了什么？” | Table II/III：rare init 和 Steak Serving success，而不是 Fig.5 的 ActionMSE |
| “能不能用于转笔数据采集？” | 只能借低成本 teleop/data pipeline 思想；power-grasp mapping 不够，需要 high-DoF 或 phase-conditioned interface |
| “为什么 ActionMSE 不够？” | no-touch Steak Serving MSE 0.07 但 success 0/10；接触关键相位在平均误差里被稀释 |
| “它和 world model 有什么关系？” | HATO 本身不是 world model，但提供真实 transition/action/tactile 数据，可作为 WMTS ensemble world model 的真实数据源 |
| “最危险的外推是什么？” | 把慢速双手抓持/托举任务的 temporal ensemble 直接用于高速 release/catch/pen-spin |

## References

- Lin, Toru, Yu Zhang, Qiyang Li, Haozhi Qi, Brent Yi, Sergey Levine, and Jitendra Malik. "Learning Visuotactile Skills with Two Multifingered Hands." arXiv:2404.16823, 2024.
- [[Diffusion Policy: Visuomotor Policy]]
- [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]]
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]]
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]]
- [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]]
- [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]]
