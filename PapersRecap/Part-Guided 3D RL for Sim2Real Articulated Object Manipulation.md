---
tags:
  - paper
  - articulated-manipulation
  - sim-to-real
  - point-cloud
  - reinforcement-learning
aliases:
  - Part-Guided 3D RL
paper-year: 2024
read-date: 2026-02-01
venue: ECCV 2024
paper-pdf: "[[Papers/Part-Guided 3D RL for Sim2Real Articulated Object Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ComputationalGeometry]]"
  - "[[RepresentationLearning]]"
---

# Part-Guided 3D RL for Sim2Real Articulated Object Manipulation

> [!abstract] 核心贡献
> 这篇论文把 articulated object manipulation 的视觉输入从“整幅 RGB-D / 无结构点云 / 少数关键点”改成 **部件语义引导的 3D 点集**，并用 Frame-consistent Uncertainty-aware Sampling (FUS) 把合成分割网络在真实世界中的噪声压成稳定可控的策略输入，从而在无需 demonstration 的仿真 SAC 训练后 zero-shot 部署到真实门、抽屉、水龙头。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]]：任务被建模为 POMDP；part-guided points 与 robot state 作为 observation，SAC 学习 target joint positions 和 gripper finger action。
> - [[ComputationalGeometry]]：从 RGB-D 像素经相机内外参 lift 到 3D world-frame points，再按 part mask 构成分层点集。
> - [[RepresentationLearning]]：2D synthetic part segmentation 提供语义先验；PointNet 把每个 part 的采样点压成 geometric feature。
>
> **核心技术**: hand-centric RGB-D, synthetic part segmentation, part-wise point lifting, FUS, PointNet geometric feature, SAC, versatile multi-task articulated manipulation policy

## 0. 阅读定位与范本价值

这篇的核心不是“又一个 point cloud RL”，而是回答一个更具体的问题：在真实 articulated object 操作中，机器人到底应该看什么？如果看整幅图像，RL 需要从大量背景、纹理和遮挡里自己发现把手/面板/底座；如果只看关键点，信息太稀疏且对遮挡敏感；如果看无结构点云，小部件会在下采样里被淹没。作者的答案是：看 **part-level 3D representation**，而且每个 part 都要保留固定数量的几何证据。

对当前知识库，这篇应放在“结构化视觉表示 -> RL policy -> Sim-to-Real”的线索中。它和 [[Grounded Action Transformation]] 一样关心 Sim-to-Real，但这里 grounding 的不是动作，而是视觉观测；它和 Dexpoint 类 3D RL 一样使用点云，但核心增量是“点云必须按可操作部件分层”。

| 四支柱 | 本文需要读出的颗粒度 | 在本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么 part prior 比 image/keypoint/unstructured point cloud 更适合 articulated manipulation | §1, §4 |
| 原理与理论 | POMDP、2D segmentation、RGB-D lift、FUS 权重、SAC 信息流如何无跳步连接 | §2 |
| 实验与验证 | simulation/real Table I-III 如何证明 part + FUS 的机制 | §3 |
| 未来与结合 | rigid part assumption、reward shaping、handle visibility 对 WMTS/灵巧手的边界 | §5-§7 |

## 1. 问题设定与动机

### 1.1 一句话核心

Part-Guided 3D RL 的核心判断是：articulated object manipulation 的难点不是“视觉特征不够强”，而是 **策略需要一个同时保留 3D 几何、操作语义和跨帧稳定性的低维观测表示**；部件分割提供语义，3D 点云提供空间关系，FUS 把真实分割噪声变成可控采样过程。

### 1.2 直观隐喻

开门时，人不会平均看整扇门的所有像素，也不会只盯一个关键点；人会把“把手、门板、门框/固定底座”看成不同功能部件。Part-Guided 3D RL 就是给机器人同样的视觉索引：把手是可抓/可拉的操作接口，面板告诉运动结果，固定底座告诉不能动的参考系。

这个隐喻可证伪：如果只是“更多点云”有效，Dexpoint/unstructured point cloud 应该接近 Ours；如果只是“语义分割”有效，image-based part mask 应该接近 Ours。实验恰好说明两者都不够，必须是 **part semantics + 3D geometry + stable sampling** 的组合。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 | 本文的增量 |
|---|---|---|---|
| Affordance methods (Where2Act/UMPNet/FlowBot3D) | 学到哪里可交互、沿什么方向动 | 往往还需要人设计 execution motion；对 gripper grasp/contact 细节支持弱 | 用 RL 闭环学习执行策略，而不是只预测 affordance |
| Image-based RL | CNN/encoder 从 RGB-D 或 mask 中自学特征 | 2D feature 不显式表达 robot-object 3D 空间关系；样本效率低 | 把 part mask lift 成 world-frame 3D points |
| Keypoints-based RL | 用少数关键点压缩视觉 | 关键点遮挡、漏检或定义不稳会直接崩；无法表达部件形状 | 用 part-level sampled point set 保留形状和局部几何 |
| Unstructured point-cloud RL / Dexpoint | 保留 3D geometry | 下采样会丢掉把手等小部件；背景/固定结构淹没操作信号 | 每个 part 采样固定点数，避免小 part 被稀释 |
| Oracle segmentation | 直接给仿真真值 part mask | 真实世界不可得，只能作为上界 | synthetic segmentation + DR + FUS 逼近 oracle |

### 1.4 Delta 分析

本文的 delta 有两层：

1. **表示层 delta**：不是 image feature，也不是 sparse keypoints，而是 part-wise 3D point set。这样策略看到的是“每类功能部件的几何证据”，而不是无语义点云。
2. **Sim-to-Real delta**：不是简单把 synthetic segmentation 直接部署到真实世界，而是设计 FUS。FUS 同时利用预测不确定性和跨帧一致性，让真实世界偶发误分割不至于把 RL policy 输入打散。

最有价值的 insight 是：part segmentation 本身不够。分割网络在真实图像上会噪，点云采样又会把噪声放大成 policy observation jitter。FUS 才是让“合成语义先验”能进入真实闭环控制的关键连接器。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $I_t$ | $H\times W\times 4$ RGB-D，实验中 $144\times256$ | hand-centric camera | 分割训练时对 $f_\theta$ 有梯度；RL 部署时输入无梯度 | 当前视觉观测 | hand-centric 不是第三视角；handle 初始可见是隐含假设 |
| $g_t$ | joint angles, gripper finger position, end-effector position | robot state | SAC 更新时作为 observation 输入 | 机器人本体状态 | 旧稿写 PPO/6D EE action 不准确；本文 action 是 target joint positions + gripper finger |
| $o_t=(I_t,g_t)$ | POMDP observation | observation fusion | 对策略网络有梯度 | policy 的输入信息 | 真实任务部分可观测，不是完整 MDP state |
| $f_\theta$ | segmentation network, MobileNetV2/UNet-style | synthetic pretraining | 分割训练时有梯度；RL 训练/部署中通常固定 | RGB-D 到 part mask | 在真实世界的错误会直接影响 point set |
| $S$ | $\{0,1\}^{C\times H\times W}$ 或 softmax/probability map | segmentation output | 对 RL 视作固定观测 | part label map | 文中有 hard mask $S$ 和 softmax $P_k$ 两套表示 |
| $C$ | part classes 数 | task/part definition | 固定 | handle/facade/base 等 part 类别 | 不是 object category 数；part spec 预定义 |
| $p_i$ | $\mathbb{R}^3$ world-frame point | RGB-D lift | 无梯度 | 像素对应的 3D 点 | world frame/robot frame/camera frame 不能混用 |
| $p_c$ | $N_c\times3$ | part mask filtering | 无梯度 | part $c$ 的候选点集 | $N_c$ 随 mask 面积变化；小 part 可能很少 |
| $N_s$ | scalar，本文取 32 | sampling hyperparameter | 固定 | 每个 part 采样点数 | 是 per-part，不是全局点数 |
| $P_k$ | $C\times H\times W$ | 第 $k$ 次 TTA/dropout forward | 对不确定性估计无梯度 | segmentation class probability | $K$ 同时用于 TTA/MC dropout 次数；实验中 $K=4$ |
| $U$ | $H\times W$ entropy map | predictive entropy | 无梯度 | segmentation uncertainty | 论文公式用 $w^{ua}=\mathrm{softmax}(U_c)$，不是 $\mathrm{softmax}(-U_c)$ |
| $Q$ | 历史 sampled points queue | rollout memory | 无梯度 | 保存最近 $T_{fc}$ 帧的 sampled part points | $Q$ 是队列，不是 RL critic $Q$ |
| $d_c$ | $N_c\times1$ | nearest distance to historical points | 无梯度 | 当前候选点与同 part 历史点的一致性距离 | 距离小代表 frame-consistent，未必代表语义正确 |
| $w_c^{ua}$ | $N_c\times1$ | uncertainty weights | 无梯度 | 按 uncertainty 给候选点分配采样概率 | 正号 softmax 是重要符号陷阱 |
| $w_c^{fc}$ | $N_c\times1$ | frame-consistency weights | 无梯度 | 靠近历史同 part 点的候选点权重大 | 系统性误分割若跨帧稳定，也会被强化 |
| $\hat p_c$ | $N_s\times3$ | weighted sampling | 无梯度 | part $c$ 的固定大小 sampled point set | weighted sampling 引入随机性，但策略输入尺寸固定 |
| $\hat F$ | compact geometric feature | PointNet output | 对 PointNet/RL network 有梯度 | part-guided geometry embedding | max pooling 保留全局几何，可能丢局部接触细节 |
| $\pi(a|o)$ | SAC actor | RL policy | 对 actor 参数有梯度 | 输出 robot target joint positions 和 gripper finger position | 不是 demonstration policy；本文强调 without demos |
| $r$ | scalar reward | shaped reward | 作为 SAC target 数值 | approach/direction/position/visibility/grasp | reward shaping 仍然大量依赖任务设计 |

### 2.2 从 POMDP 到 part-guided observation

Articulated manipulation 可以写成 POMDP：

$$
\mathcal{M}=(\mathcal{S},\mathcal{A},\mathcal{O},T,R,\Omega,\gamma).
$$

真实状态 $s_t$ 包含 object joint angle、handle pose、contact state、robot state 等，但机器人只观测到：

$$
o_t=(I_t,g_t),
$$

其中 $I_t$ 是 hand-centric RGB-D，$g_t$ 是 robot state。策略是：

$$
\pi:\mathcal{O}\rightarrow\mathcal{A}.
$$

如果直接把 $I_t$ 喂给 CNN，策略要同时学三件事：哪些像素是可动部件、这些像素在 3D 里在哪里、它们和 gripper 的关系是什么。本文把这个任务拆开：

$$
I_t \xrightarrow{f_\theta} S_t
\xrightarrow{\text{RGB-D lift}} \{p_c\}_{c=1}^{C}
\xrightarrow{\text{FUS}} \{\hat p_c\}_{c=1}^{C}
\xrightarrow{\text{PointNet}} \hat F_t
\xrightarrow{\text{concat }g_t} \pi(a_t|o_t).
$$

这条链的意义是把 representation learning 的一部分从 RL 中拿出来，用 synthetic segmentation 预训练提供结构先验，使 SAC 不必从稀疏 reward 中发现 part semantics。

### 2.3 从 RGB-D 到 world-frame part points

对一个像素 $(u,v)$ 和深度 $d$，相机内参矩阵为 $K_{cam}$。相机坐标系中的 3D 点是：

$$
x_{cam}=dK_{cam}^{-1}
\begin{bmatrix}
u\\v\\1
\end{bmatrix}.
$$

再用相机到世界或机器人基座的外参 $T_{world\leftarrow cam}$：

$$
\tilde p_i
=
T_{world\leftarrow cam}
\begin{bmatrix}
x_{cam}\\1
\end{bmatrix},
\qquad
p_i=\tilde p_i[1:3].
$$

分割网络给每个像素一个 part label。对 part $c$：

$$
p_c=\{p_i \mid \arg\max_{c'} S_{c'}(u_i,v_i)=c\}.
$$

为什么这一步重要？因为 articulated manipulation 的控制量是空间关系：gripper 到 handle 的距离、pull direction 与 joint axis 的关系、fixed base 的碰撞边界。这些无法从纯 2D mask 中直接读出。

### 2.4 Part definition：语义不是类别，而是 affordance

论文沿用 GAPartNet 风格定义 part：part 是一个 rigid segment，且具有相似 affordance。门/抽屉包含 fixed handle、door/drawer facade、fixed base；水龙头包含 handle 和 fixed base。

这不是视觉分类的小细节，而是方法成立的核心先验。Part label 的含义是“怎样与它交互”：

| Part | 物理意义 | 策略用途 |
|---|---|---|
| handle | 可抓/可拉/可转的操作接口 | approach、grasp、force direction |
| facade / drawer front | movable body 的几何外观 | 判断 opening progress 和空间关系 |
| fixed base | 不应被推动的环境参考 | 避免碰撞，提供相对运动参照 |

因此“object-irrelevant part representation”不是说完全无先验，而是把 object category 先验换成 part affordance 先验。门和抽屉类别不同，但 fixed handle 的交互意义相似。

### 2.5 FUS 的无跳步推导

原始点云很大，RL 训练需要固定大小输入。最朴素做法是 uniform downsampling：

$$
\hat p \sim \mathrm{Uniform}(\{p_i\}).
$$

这会让小把手被大面积背景/门板淹没。Part-wise sampling 先改为每个 part 取相同数量 $N_s$：

$$
\hat p_c = \mathrm{Sample}_{N_s}(p_c).
$$

这解决“小 part 被稀释”，但还没解决真实分割噪声。于是 FUS 为每个 part 内的候选点构造权重：

$$
w_c=w_c^{fc}\circ w_c^{ua}.
$$

#### 2.5.1 Uncertainty weights

对同一输入图像 $I$ 做 $K$ 次 stochastic forward：TTA 加上 MC Dropout，得到 softmax maps：

$$
\{P_k\in\mathbb{R}^{C\times H\times W}\}_{k=1}^{K}.
$$

平均概率为：

$$
P_c=\frac{1}{K}\sum_{k=1}^{K}P_k^c.
$$

predictive entropy：

$$
U=-\sum_{c}P_c\log P_c.
$$

对 part $c$ 的像素取出对应 uncertainty vector：

$$
U_c=
\left[
U_{(u,v)}
\mid
\arg\max S_{(u,v)}=c
\right].
$$

论文公式写：

$$
w_c^{ua}=\mathrm{softmax}(U_c).
$$

这里有一个必须主动指出的符号陷阱：如果 $U$ 真的是 entropy，$\mathrm{softmax}(U_c)$ 会给高不确定点更高采样权重，而不是“避开不确定点”。旧稿常会自然写成“高不确定 -> 低权重”，但这和论文公式不一致。

我对这个设计的理解是：FUS 不是简单 uncertainty rejection，而是 uncertainty-aware emphasis 加 frame consistency filter。高熵点往往位于边界、小 handle 或 ambiguity 区域；单独上调会危险，但再乘以跨帧一致性后，可以保留“重要且稳定的模糊区域”，抑制“高熵但漂移的误分割噪声”。如果作者原意是拒绝 uncertainty，那么公式应写成 $\mathrm{softmax}(-U_c)$；论文没有这样写，所以 recap 必须按原公式并保留批判。

#### 2.5.2 Frame consistency weights

为每个 part 保存最近 $T_{fc}$ 帧 sampled points queue：

$$
Q_c=\{\hat p_c^{t-1},\hat p_c^{t-2},\ldots\}.
$$

对当前 part 候选点 $p_i\in p_c$，计算它到历史同 part 点的最近距离：

$$
d_i=\min_{q_j\in Q_c}\|p_i-q_j\|.
$$

写成向量：

$$
d_c=
\left[
\min_{q_j\in Q_c}\|p_i-q_j\|
\mid
p_i\in p_c
\right].
$$

距离越小，说明该点在连续帧中更稳定。权重为：

$$
w_c^{fc}=2^{-K^{fc}d_c}.
$$

若 $d_i=0$，$w=1$；若 $d_i$ 增大，权重指数衰减。这是一个低通滤波器：偶发误分割点通常不会和历史同 part 点靠近，所以被压低。

#### 2.5.3 Combined sampling

最终：

$$
w_c=w_c^{fc}\circ w_c^{ua},
\qquad
\hat p_c\sim \mathrm{WeightedSample}_{N_s}(p_c,w_c).
$$

实验中 $K=4$，$T_{fc}=3$，$K^{fc}=40$，$N_s=32$。采样后的各 part 点集合 $\hat p=\cup_c \hat p_c$ 进入 PointNet，得到几何特征 $\hat F$，再与 robot state $g$ 拼接：

$$
z_t=\hat F_t\oplus g_t.
$$

SAC actor/critic 用 $z_t$ 作为 observation embedding。

### 2.6 SAC policy learning

论文采用 SAC，而不是旧稿中写的 PPO。SAC 的 classical root 是最大熵 off-policy actor-critic：

$$
J(\pi)=
\mathbb{E}_{\pi}
\left[
\sum_t\gamma^t
\left(
r(s_t,a_t)+\alpha\mathcal{H}(\pi(\cdot|o_t))
\right)
\right].
$$

这里的 $o_t$ 不是完整 state，而是由 part-guided 3D features 和 robot state 组成的 observation。动作 $a_t$ 表示 robot target joint positions 和 gripper finger position。这个动作选择也反映了论文的任务边界：它是 7-DOF arm + two-finger gripper 的 articulated object manipulation，不是多指手内操作。

reward shaping 包含五项：

| Reward term | 作用 | 哪些任务使用 |
|---|---|---|
| Approaching | 鼓励 gripper 接近 movable part | Door/Drawer/Faucet |
| Direction | 鼓励沿正确方向操作 part | Door/Drawer/Faucet |
| Position | 推动 movable part 到目标位置 | Door/Drawer/Faucet |
| Visibility | 保持对 movable part 的视觉接触 | Door/Drawer/Faucet |
| Grasp | 鼓励抓住 handle | Door/Drawer；TurnFaucet 去掉 |

这也是 limitation 的根：虽然论文强调 no demonstrations，但它并不是 reward-free。它用 dense shaped reward 支撑 SAC 训练，reward 设计仍然依赖对任务几何和操作方向的理解。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项目 | 设定 |
|---|---|
| 真实硬件 | ROKAE xMate3Pro 7-DOF arm + Robotiq 2F-140 gripper + Intel RealSense D435 |
| 视角 | hand-centric RGB-D camera |
| 仿真器 | SAPIEN / ManiSkill-style articulated objects |
| 训练对象 | PartNet Mobility: 40 doors, 16 drawers, 14 faucets |
| RL training instances | 每类 4 个实例 |
| RL steps | 2 million steps |
| 随机种子 | simulation results averaged over 7 seeds |
| 评估 | 每任务 novel instance，50 trials；真实每类 2 个物体，每个 20 trials |
| Success criterion | simulation 移动 part 至 50% range；真实 door/faucet 45 degrees，drawer 10 cm |
| RL algorithm | SAC |
| Segmentation | synthetic RGB-D part masks, MobileNetV2/UNet-style fast segmentation |
| FUS hyperparameters | $K=4$, $T_{fc}=3$, $K^{fc}=40$, $N_s=32$ |

### 3.2 Simulation：part-guided 3D 表示是否接近 oracle

| Task | Image-based RL | Keypoints-based RL | Dexpoint-based RL | Oracle | Ours |
|---|---:|---:|---:|---:|---:|
| OpenDoor | 0.000 ± 0.000 | 0.574 ± 0.197 | 0.000 ± 0.000 | 0.929 ± 0.062 | 0.871 ± 0.060 |
| OpenDrawer | 0.006 ± 0.009 | 0.594 ± 0.199 | 0.017 ± 0.042 | 0.914 ± 0.061 | 0.831 ± 0.107 |
| TurnFaucet | 0.294 ± 0.182 | 0.246 ± 0.168 | 0.243 ± 0.061 | 0.883 ± 0.045 | 0.843 ± 0.083 |
| Hybrid-Door | 0.029 ± 0.018 | 0.040 ± 0.049 | 0.006 ± 0.009 | 0.791 ± 0.079 | 0.726 ± 0.102 |
| Hybrid-Drawer | 0.023 ± 0.017 | 0.029 ± 0.034 | 0.006 ± 0.009 | 0.857 ± 0.081 | 0.754 ± 0.143 |
| Hybrid-Faucet | 0.080 ± 0.043 | 0.009 ± 0.015 | 0.009 ± 0.015 | 0.814 ± 0.081 | 0.737 ± 0.132 |

因果解释：

1. Ours 与 Oracle 的差距很小：OpenDoor 差 0.058，OpenDrawer 差 0.083，TurnFaucet 差 0.040。这说明合成分割 + FUS 已经接近真值 part mask 的上界，Sim-to-Real 风险不是来自 RL 算法本身，而主要来自 perception front-end。
2. Image-based RL 在 OpenDoor/OpenDrawer 几乎为 0，说明“有 part mask 的 2D 图像特征”仍不足以表达机器人和 handle 的 3D 空间关系。
3. Keypoints-based RL 在单任务 Door/Drawer 有中等表现，但 Hybrid 近乎崩掉，说明少数 keypoints 对类别内任务有效，对跨类别泛化和遮挡不稳。
4. Dexpoint/unstructured point cloud 大多接近 0，说明“3D”本身不是解法；没有 part-wise 采样，小 handle 与可操作结构会被点云背景稀释。

### 3.3 Simulation：采样点数的计算-性能折中

Fig. 7 显示 OpenDoor 中 $N_s$ 从 $2^1$ 到 $2^6$ 增加时，success rate 上升并在一定点数后 plateau，average success steps 下降。作者最终取 $N_s=32$。这不是随手调参，而是 part-wise representation 的一个必要 tradeoff：点太少不能表达 handle/facade 形状；点太多增加 PointNet 和 RL 训练成本，并可能引入噪声。

### 3.4 Real：zero-shot Sim-to-Real 是否成立

| Setting | Task | Dexpoint success | Ours success | Ours avg success steps |
|---|---|---:|---:|---:|
| Single | OpenDoor | 0 / 40 | 35 / 40 | 27.8 ± 3.2 |
| Single | OpenDrawer | 0 / 40 | 32 / 40 | 28.3 ± 3.0 |
| Single | TurnFaucet | 8 / 40 | 35 / 40 | 19.9 ± 2.7 |
| Hybrid | OpenDoor | 0 / 40 | 31 / 40 | 31.1 ± 3.8 |
| Hybrid | OpenDrawer | 0 / 40 | 27 / 40 | 30.1 ± 4.2 |
| Hybrid | TurnFaucet | 0 / 40 | 32 / 40 | 19.7 ± 4.5 |

因果解释：真实实验最强的证据不是单任务 35/40，而是 Hybrid policy 仍然能在三个类别上保持 31/40、27/40、32/40。它说明 part representation 把类别差异压成了可共享的 affordance structure。Dexpoint 用同样 domain randomization 仍然在 Door/Drawer 为 0/40，说明真实迁移中缺的不是“点云 + DR”，而是 part-conditioned 采样。

### 3.5 Real ablation：FUS 两个分量各自贡献什么

| Sampling strategy | OpenDoor real success |
|---|---:|
| Random | 24 / 40 (60.0%) |
| FPS | 26 / 40 (65.0%) |
| FUS w/o Uncertainty | 29 / 40 (72.5%) |
| FUS w/o Consistency | 31 / 40 (77.5%) |
| FUS | 35 / 40 (87.5%) |

Ablation 因果链：

- Random/FPS -> 24/40 或 26/40 -> 只保证随机覆盖或几何分散，不保证 handle 等小 part 的语义稳定 -> policy 输入仍被误分割和点云抖动污染。
- 去掉 uncertainty -> 29/40 -> 只靠跨帧距离滤波，无法主动处理 segmentation confidence/entropy 结构 -> 对边界和小 handle 的候选点选择较弱。
- 去掉 consistency -> 31/40 -> 有 uncertainty-aware sampling，但跨帧漂移点仍可进入输入 -> policy observation jitter 变大。
- 完整 FUS -> 35/40 -> uncertainty 提供候选权重，frame consistency 抑制偶发误分割 -> 真实闭环输入更稳定。

这里要保留一个批判点：由于论文公式是 $w_c^{ua}=\mathrm{softmax}(U_c)$，FUS w/o Consistency 仍能达到 31/40，并不意味着“高不确定点被拒绝”有效；它更可能说明高熵区域包含重要边界/小部件信息，而 consistency 是把这种 aggressive sampling 变稳的关键。

### 3.6 Versatile policy 扩展到更多类别

为排除 segmentation error 的影响，作者用 oracle part segmentation 在仿真中分析 3-class 到 5-class 的 versatile policy：

| Method | Oracle-3class | Oracle-5class |
|---|---:|---:|
| HybridDoor | 0.791 ± 0.079 | 0.466 ± 0.243 |
| HybridDrawer | 0.857 ± 0.081 | 0.903 ± 0.131 |
| HybridFaucet | 0.814 ± 0.081 | 0.694 ± 0.155 |
| HybridLaptop | N/A | 0.974 ± 0.028 |
| HybridKitchenPot | N/A | 0.477 ± 0.234 |

平均成功率从 82.1% 降到 70.3%。这支持“part representation 有跨类别潜力”，但也说明 scaling 不免费：增加 object types 后，reward、policy capacity、part spec 和 action distribution 都会出现冲突。特别是 Door 和 KitchenPot 下滑/低分，说明“handle/base/facade”这样的 part schema 不是 universal grammar。

### 3.7 Failure cases

论文列出三类失败：

| Failure | 直接原因 | 机制层解释 | 可能补救 |
|---|---|---|---|
| 误把背景当 handle，无法 approach | sampled points 错 | perception front-end 给 policy 错目标 | 更强 segmentation / object tracking / language constraint |
| 拉动方向不对 | grasp point 或 force direction 不合适 | 只有几何点，不知道接触力和摩擦 | 加 force-torque/tactile sensing |
| gripper 卡在 fixed link/base | 固定部件碰撞 | part 表示告诉了 base，但 reward/control 没完全处理 contact constraint | 加 collision-aware planning 或 contact world model |

这三类失败很适合连接 WMTS：它们都不是单帧语义能解决的问题，而是需要接触结果预测、force/tactile feedback 和 world model lookahead。

## 4. 核心洞见

### 4.1 论文真正的 insight

Part-Guided 3D RL 的 insight 是：对 articulated manipulation 来说，视觉表示应当按 **可操作结构** 而不是按像素、类别或均匀几何来组织。部件不是语义标签的装饰，而是把 RL observation 的信噪比提高了。

更具体地说：

$$
\text{small handle signal}
\ll
\text{door/background/fixed base points}
$$

在无结构点云中，小 handle 容易被采样丢掉；在 2D image 中，handle 与 robot 的 3D 接近关系不显式；在 keypoints 中，handle shape 和抓取冗余丢失。Part-wise sampled point sets 让每个 affordance-bearing part 都有固定表达预算。

### 4.2 为什么这个设计有效

有效性来自三个嵌套 prior：

| Prior | 缩小了什么搜索空间 | 实验证据 |
|---|---|---|
| Part prior | 从全图/全点云缩到 handle/facade/base 等功能部件 | Image-based/Dexpoint 远低于 Ours |
| 3D geometry prior | 从 2D mask 到 robot-object 空间关系 | Image-based RL 几乎失败 |
| Temporal consistency prior | 从单帧 noisy segmentation 到稳定 part evidence | FUS 35/40 > no consistency 31/40 |

这也是为什么 Ours 接近 Oracle。Oracle 给的是完美 part mask；Ours 用 synthetic segmentation + FUS 在真实/novel 场景中逼近这个结构先验。

### 4.3 什么时候会失效

它会在以下条件下失效或变弱：

1. part specification 不清楚，例如软物体、工具链、多物体堆叠或没有固定 handle 的物体。
2. hand-centric camera 初始看不到关键 part，例如 handle 被遮挡或策略早期走错后丢失目标。
3. 错误分割是系统性的、跨帧稳定的，此时 frame consistency 会强化错误，而不是消除错误。
4. 任务需要精细力控，几何点集无法判断抓握力、摩擦锥、卡滞和滑动。
5. reward shaping 无法随类别扩展，versatile policy 会因 reward/action distribution 冲突下降。

## 5. 替代方案与理论局限

### 5.1 理论维度

FUS 的理论还停在启发式层面。它没有证明 $w_c^{ua}\circ w_c^{fc}$ 是某个后验概率的近似，也没有给出在何种噪声模型下 softmax entropy 与 nearest-neighbor temporal distance 的乘积是最优采样分布。

特别是 uncertainty 权重存在符号争议：如果 $U$ 是 entropy，高 $U$ 代表高不确定，那么 $w_c^{ua}=\mathrm{softmax}(U_c)$ 会强调不确定点。这个设计可以被解释为“采样信息量高的边界/小部件”，但论文文字没有充分澄清。未来若要严谨化，应比较 $\mathrm{softmax}(U)$、$\mathrm{softmax}(-U)$、calibrated confidence、mutual information 等不同 uncertainty-to-weight mappings。

### 5.2 算法维度

本文强调 without demonstrations，但依赖 dense reward shaping。SAC 能学习，是因为 approach/direction/position/visibility/grasp 把长时序任务拆成了连续信号。若换到 reward 稀疏或目标难定义的任务，这个 framework 不会自然解决 credit assignment。

此外，SAC policy 是针对 7-DOF arm + parallel gripper 的 target joint positions。迁移到 dexterous hand 时，动作维度、接触模式和稳定性完全不同，不能只换 observation front-end。

### 5.3 工程/实验维度

| 局限 | 论文中的具体表现 | 对真实系统的影响 |
|---|---|---|
| 预定义 part spec | Door/Drawer/Faucet 的 parts 由人设计 | 新类别需要重新定义 part schema |
| 初始可见假设 | hand-centric setting 假设 handle 初始可见 | 遮挡或错位会让 policy 从第一步就追错目标 |
| rigid base assumption | FUS 依赖 object rigid base stationary | base 移动、物体滑动或多物体交互会破坏 consistency |
| 系统性误分割 | 某区域连续帧都被误认为 handle | frame consistency 会错误增强 |
| 缺少力/触觉 | failure case 中 grasp loose/contact direction 错 | 几何表示无法判断摩擦和接触质量 |
| reward tuning cost | 作者未来工作也提到 refine reward-tuning | 扩展到更多 articulated objects 会变慢 |

## 6. 对用户研究的启发

### 6.1 对 WMTS 的迁移

这篇最适合迁移到 WMTS 的地方不是 SAC 本身，而是 **part-conditioned observation token**。

| 本文组件 | WMTS 对应物 | 迁移方式 |
|---|---|---|
| part segmentation | task-relevant object/contact segmentation | 把 object 分成可操作区域、支撑区域、禁止碰撞区域 |
| part-wise points | world model object tokens | 每个 part/contact region 形成 token，输入 PPO Oracle / world model / diffusion policy |
| FUS | uncertainty + temporal consistency filter | 对视觉/tactile/contact tokens 做稳定采样，避免单帧感知抖动 |
| versatile policy | multi-task generalist | 用 shared part grammar 支撑多任务策略，而不是每类物体单独训练 |
| failure analysis | world model lookahead targets | 预测抓不稳、方向错、卡 base 等失败模式 |

WMTS 可以把 part-guided representation 用在 latent task generation 阶段：任务不只是“打开门”，而是“接近 handle -> grasp handle -> 沿 joint-compatible direction 拉动 -> 避开 fixed base”。这比纯文本/图像 task embedding 更接近控制因果链。

### 6.2 对灵巧手/转笔的启发

对转笔不能直接套“handle/facade/base”。笔不是 articulated object，且关键结构不是 rigid semantic part，而是动态接触角色：

| Part-Guided 3D RL 中的 part | 转笔中更合理的对应物 |
|---|---|
| handle | 当前主要推力接触区域 / 指尖接触 patch |
| facade / movable body | 笔身姿态、角速度、相位 |
| fixed base | 手掌/非接触手指构成的约束边界 |
| FUS consistency | 触觉接触点/滑动方向的跨帧稳定性 |

因此对 DNPM 更有价值的不是视觉 part segmentation，而是 **contact-role-guided sampling**：把 tactile/contact/vision features 按“推动、接住、稳定、释放”角色组织，再做 uncertainty + temporal consistency。这里的 part 是功能角色，不是物体外观标签。

### 6.3 可验证实验建议

1. **Part token vs unstructured token**：在 articulated manipulation 或 LinkerHand object interaction 中比较 part-wise tokens、uniform point tokens、keypoint tokens。若 part token 只在有 clear affordance 的任务上有效，说明它是任务结构 prior，不是通用 representation。
2. **FUS sign ablation**：比较 $\mathrm{softmax}(U)$、$\mathrm{softmax}(-U)$、confidence sampling、FUS consistency only。这个实验能澄清论文中 uncertainty 权重的真实作用。
3. **Vision-only vs visuotactile FUS**：在接触失败多的任务上加入 force/tactile consistency。如果几何 FUS 仍有抓不稳/力方向错，触觉应显著改善 failure case (b)。
4. **World-model failure prediction**：用 part-guided tokens 训练 ensemble world model，预测 “handle lost / wrong pull direction / stuck on base”。若能提前 reject 高风险动作，就能把本文表示接到 WMTS 的 Solve/Probe/Reject 结构。

### 6.4 不应过度外推的点

本文的成功建立在有 clear articulated parts、synthetic annotations、dense reward shaping、hand-centric initial visibility 和 7-DOF arm + gripper 上。它不能证明“只要有 part segmentation，任意 dexterous manipulation 都能 zero-shot Sim-to-Real”。对灵巧手，真正难的可能是 contact dynamics、actuator delay、tactile slip 和高维 action coordination，这些不是 FUS 能单独解决的。

## 7. 与知识体系的联系

### 与 [[ComputationalGeometry]] 的联系

本文的几何链条是：

$$
\text{RGB-D pixel}
\rightarrow
\text{camera 3D point}
\rightarrow
\text{world-frame point}
\rightarrow
\text{part-conditioned point set}
\rightarrow
\text{PointNet feature}.
$$

它不是为了重建完整 object mesh，而是为了给策略一个最小可操作几何表示。这个定位很适合放在“几何不是越完整越好，而是要服务控制因果变量”的知识线上。

### 与 [[RepresentationLearning]] 的联系

2D segmentation 在这里是 representation bottleneck。它把高维 RGB-D 压成 part labels，再 lift 到 3D。FUS 进一步说明，representation 的问题不只在 accuracy，还在 temporal stability：单帧 mIoU 高不代表闭环控制稳定。

这对后续所有 vision/tactile policy 都重要。一个 perception model 的好坏，应该用 downstream closed-loop stability 判断，而不是只看离线分割分数。

### 与 [[ReinforcementLearning]] 的联系

本文把 SAC 的学习难度主要降在 observation design 上，而不是改变 RL objective。也就是说，它的 RL lesson 是：

$$
\text{better observation prior}
\Rightarrow
\text{easier value function}
\Rightarrow
\text{more stable policy learning}
\Rightarrow
\text{better Sim-to-Real}.
$$

这与 SERL 的 lesson 互补：SERL 强调 real-world RL 的系统栈，Part-Guided 强调 real-world RL 的观测结构。WMTS 如果只做 world model/RL objective，而不给策略稳定的 object/contact tokens，仍然可能被视觉噪声和小部件稀释拖垮。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| 这篇相对 affordance/keypoint/point-cloud 方法的优势是什么？ | 说明它不是只预测可操作点，而是让 RL 闭环使用 part-wise 3D representation；每个 part 固定采样避免小 handle 被稀释。 |
| FUS 到底在做什么？ | 从 entropy uncertainty、历史 queue、nearest distance、$2^{-K^{fc}d}$、element-wise product 推到 weighted sampling。 |
| uncertainty 是不是低权重？ | 不能乱说。论文公式是 $\mathrm{softmax}(U_c)$，会强调高 entropy；必须把这个符号陷阱和可能解释讲清楚。 |
| 实验如何证明 part prior？ | 用 Table I：Ours 接近 Oracle，Image/Dexpoint 近乎失败，Keypoints Hybrid 崩；说明 part+3D+sampling 的组合有效。 |
| 实验如何证明 Sim-to-Real？ | 用 Table II/III：真实 Ours 35/32/35 out of 40，Hybrid 31/27/32；FUS 35/40 > no uncertainty 29/40 > random 24/40。 |
| 能不能用于转笔？ | 不能直接用 handle/facade/base；应转成 contact-role-guided tactile/vision token，并加入 force/tactile/world-model failure prediction。 |

## References

- Xie, Pengwei, Rui Chen, Siang Chen, Yuzhe Qin, Fanbo Xiang, Tianyu Sun, Jing Xu, Guijin Wang, and Hao Su. 2024. *Part-Guided 3D RL for Sim2Real Articulated Object Manipulation*. arXiv:2404.17302.
- Geng, Haoran et al. 2023. *GAPartNet: Cross-Category Domain-Generalizable Object Perception and Manipulation via Generalizable and Actionable Parts*.
- Haarnoja, Tuomas et al. 2018. *Soft Actor-Critic: Off-Policy Maximum Entropy Deep Reinforcement Learning with a Stochastic Actor*.
