---
tags:
  - paper
  - dexterous-manipulation
  - sim-to-real
  - data-augmentation
  - imitation-learning
  - curriculum-learning
aliases:
  - CyberDemo
paper-year: 2024
read-date: 2026-06-25
venue: CVPR 2024
paper-pdf: "[[Papers/CyberDemo - Augmenting Simulated Human Demonstration.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
---

# CyberDemo: Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation

> [!abstract] 核心贡献
> CyberDemo 反转了“真实 demo 一定比仿真 demo 更有价值”的默认信念：它把少量仿真人类演示变成一个物理一致的轨迹级数据生成器，再用任务成功率驱动课程训练，最后只用约 3 分钟真实 demo 修补残余 sim-to-real gap。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — 行为克隆的分布覆盖问题：CyberDemo 不改变 BC 目标，而是扩大训练分布的支持集，并用课程避免一开始把 BC 推到无效增强分布上。
> - [[RepresentationLearning]] — 它不是只学视觉不变性；视觉随机化和轨迹级物理增强共同决定策略表征是否能对光照、相机、几何与初始位姿变化不敏感。
> - [[EmbodiedAI]] — 这是“仿真数据飞轮 + 少量真实适配”的具身版本，但仍需要任务级仿真搭建和真实微调，不能被读成纯 zero-shot sim-to-real。
>
> **核心技术**: simulated human demonstrations, trajectory-level physical augmentation, sensitivity-aware SE(3) kinematic augmentation, automatic curriculum learning, ACT-style action chunking, few-real-demo fine-tuning

## 0. 阅读定位与范本价值

CyberDemo 在知识库里的位置不是“又一篇 domain randomization 论文”，而是 demonstration/data-generation 簇里的一个关键分叉点：

| 四支柱 | 本文必须回答的问题 | 本 recap 的落点 |
|---|---|---|
| 逻辑与价值 | 为什么仿真 demo 可能比真实 demo 更有价值？ | §1 把“真实数据质量高”改写成“真实数据覆盖窄，仿真可生成 physically grounded coverage” |
| 原理与理论 | 轨迹增强到底是不是物理一致？ | §2 从 BC 分布覆盖、SE(3) 相对位姿保持、log/exp 位姿分配、敏感度估计逐步推导 |
| 实验与验证 | 哪些数字证明“仿真增强”而不是“视觉 backbone”在起作用？ | §3 用 Table 1/2/3 的真实数字解释 in-domain、OOD、augmentation、curriculum 的因果链 |
| 未来与结合 | 这套方法能否直接用于转笔/WMTS？ | §5-§7 说明可迁移的是“demo 变任务生成器”的思想，不可直接照搬的是 6D 末端位姿增强 |

对用户的 WMTS / 灵巧手转笔来说，本文最有价值的 insight 是：**demo 不只是监督样本，而可以是一个可被仿真器重放、扰动、筛选、课程化的生成种子**。这和 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] 的 “demo state as reset task proposal” 以及 [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] 的 “demo time as compressible resource” 形成互补：CyberDemo 处理的是 **demo trajectory as physically grounded augmentation seed**。

## 1. 问题设定与动机

### 1.1 一句话核心

真实 demo 的问题不是“不真实”，而是**覆盖太窄**；仿真 demo 的问题不是“便宜”，而是**若能在物理状态空间里被重放和改写，它能产生真实世界很难采到的覆盖**。

CyberDemo 的结构性赌注是：

$$
\text{few sim demos} + \text{physically grounded augmentation} + \text{few real demos}
\quad > \quad
\text{few real demos} + \text{generic visual pretraining}.
$$

这个不等式不是说 sim 比 real 更准确；它说的是，当真实 demo 很少时，**覆盖度的边际价值**大于单条数据真实性的边际价值。真实 fine-tuning 仍然必要，因为仿真无法完全吃掉视觉、接触、控制器和执行延迟 gap。

### 1.2 直观隐喻

CyberDemo 像是把一条人类演示从“录像”变成“可重拍的动作剧本”：

- 纯真实 IL 只有一条录像：光照、相机、物体和起始姿态都固定；
- 图像增强是在录像上加滤镜：视觉变了，但物理事件没有变；
- CyberDemo 在仿真片场重拍：相机、灯光、物体形状、起始姿态都能改，并且每次重拍都要让动作真的完成任务。

这个隐喻的可证伪点是：如果增强只改像素、不改物理状态，OOD object pose / object geometry 应该仍然崩；如果增强真的改变了物理轨迹覆盖，Table 2 中更多 augmentation level 应该同时提升 sim 和 real 的难场景表现。论文确实显示后者。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验 | 关键局限 | CyberDemo 的增量 |
|---|---|---|---|
| 少量真实 demo + BC | 部署域数据最可信 | 高 DoF 灵巧手 demo 贵，覆盖窄；光照、相机、物体、初始位姿稍变就 OOD | 用仿真把少量 demo 扩成多条件覆盖，再用少量真实 demo 修补 residual gap |
| 视觉预训练 R3M/PVR/MVP | 大规模图像/视频表征能迁移到机器人 | 表征能抗视觉变化，但不知道任务接触几何和动作后果 | 用动作轨迹和仿真成功筛选把 task prior 注入 policy |
| 图像级增强 | 保持标签不变的视觉不变性 | crop/color jitter 不保证透视、遮挡、接触和对象姿态物理一致 | 在 simulator state 上重渲染，视觉变化来自同一个物理世界状态 |
| RL + domain randomization | 用大量交互覆盖随机化分布 | 需要 reward、reset、百万级交互；灵巧手任务 reward 设计成本高 | 用 teleop demo + BC 避免 reward 设计，同时保留 DR 的覆盖思想 |
| MimicGen 类仿真内 demo 合成 | 长程任务可由仿真 demo 拼接/合成 | 主要服务 sim policy，不直接解决真实灵巧手部署 | 明确加入 few-real-demo fine-tuning 和真实 robot evaluation |

### 1.4 Delta 分析

本文真正的 delta 不是“用了仿真”或“用了 domain randomization”，而是把 augmentation 的作用对象从 image 提升到 **trajectory under simulator validation**：

$$
T_{\text{image}}(o_t) \quad \longrightarrow \quad
T_{\text{sim}}(s_{1:T}, a_{1:T}) \xrightarrow{\mathrm{render}} o'_{1:T}, \quad
\mathrm{eval}(s'_{1:T}, a'_{1:T}) = 1.
$$

这里的关键是最后的 success filter。图像增强默认标签不变；CyberDemo 不能默认轨迹标签不变，因为物体形状和初始位姿一变，原动作可能失败。所以它用 simulator 低成本枚举扰动，只保留成功轨迹。这使它比普通 augmentation 更接近“数据生成系统”。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---:|---|---|---|---|
| $D_h$ | human demo trajectory set | teleoperation in simulation | 否 | 原始仿真人类演示，是所有增强的种子 | 它不是 policy rollout，也不是 expert reward；是可重放的 state-action 序列 |
| $D$ | training dataset | curriculum loop | 否 | 按 level 动态追加的训练集 | 训练集不是一次性固定，而是随策略评估结果增长 |
| $o_t$ | RGB image + proprioception | observation | 对 policy 输入可反传到 encoder | 策略看到的部署观测 | sim 中还有 oracle state/contact，但真实 policy 不直接使用 |
| $a_t$ | 6D EE Cartesian velocity + 16D finger target | teleop action label | 监督标签，不反传 | 行为克隆目标 | SE(3) 位姿增强只处理 6D end-effector 部分，不处理 finger motion |
| $T_A^B$ | $SE(3)$ | simulator/kinematics | 否 | frame $B$ relative to frame $A$ | 上标/下标方向易反：$T_W^O$ 是 object in world |
| $T_W^{O_{\mathrm{old}}}$ | $SE(3)$ | original demo state | 否 | 原始物体位姿 | old/new 是 object pose，不是 policy iteration |
| $T_W^{O_{\mathrm{new}}}$ | $SE(3)$ | randomized reset | 否 | 新物体位姿 | 随机化后不能简单重放原动作 |
| $T_W^{R_{\mathrm{old}}}$ | $SE(3)$ | original robot/EE pose | 否 | 原始末端位姿 | paper 用 $R$ 表示 robot/end-effector pose，不是 rotation matrix |
| $\Delta T$ | $SE(3)$ | computed transform | 否 | 新旧 object pose 的相对变化 | 应用在 world frame，再经 $f_i$ 转到当前 EE action frame |
| $\tau=\{a_1,\ldots,a_N\}$ | trajectory | original demo | 否 | 原动作序列 | 这里的 $N$ 是 robot time，不是 diffusion step |
| $M,K$ | integers | segmentation hyperparameters | 否 | $M$ 段，每段 $K=N/M$ 步 | 论文没有把具体 $M,K$ 当核心贡献，别编数值 |
| $\delta_a$ | normalized action noise scale | augmentation search | 否 | 测某段对动作噪声的容忍度 | action space 假设归一化到 $[-1,1]$ |
| $\epsilon_i$ | Gaussian noise | sampling | 否 | 扰动某段动作 | 只在被测 segment 内加，segment 外动作保持不变 |
| $\psi_{\mathrm{seg}}$ | positive scalar | sensitivity analysis | 否 | robustness = sensitivity 的倒数意义 | 越大越能承担 object-pose change，不是越大越危险 |
| $\pi_\theta$ | policy network | learned model | 是 | ACT-style chunk policy | policy 输入是图像+本体，不输入 oracle contact |
| $L$ | curriculum level | ACL loop | 否 | 当前 augmentation/evaluation 难度 | level 是训练难度，不是 task reward level |
| $r_{\mathrm{succ}}, r_{\mathrm{up}}$ | scalar success rates | eval loop | 否 | 是否升级课程的判据 | 论文 Table 3 说明 task success 比 data generation rate 更适合做升级信号 |
| $N_{\mathrm{fail}}, N_{\max}$ | counters | ACL loop | 否 | 防止卡在某难度无限训练 | 失败次数达到上限也会升级，不表示当前 level 已学会 |

### 2.2 从行为克隆的分布覆盖问题开始

最朴素的行为克隆写成：

$$
\min_\theta \mathcal{L}_{BC}(\theta)
=
\mathbb{E}_{(o_t,a_t)\sim D}
\left[\ell(\pi_\theta(o_t), a_t)\right].
$$

如果用平方误差，$\ell(\hat a,a)=\|\hat a-a\|^2$；如果用 ACT，$\pi_\theta(o_t)$ 输出的是未来 action chunk，但监督本质仍是从 demo 数据分布上回归动作。

BC 的根本问题不是这个目标写错了，而是期望只覆盖 $D$ 的支持集：

$$
\mathrm{supp}(p_D(o,a))
\ll
\mathrm{supp}(p_{\mathrm{deploy}}(o,a)).
$$

少量真实 demo 的 $p_D$ 虽然来自真实世界，但很窄；部署时会遇到未见过的光照、相机、物体和初始位姿。CyberDemo 的动作是构造一个增强分布：

$$
D_{\mathrm{aug}}
=
\bigcup_{L=0}^{4}
\mathrm{aug}_L(D_h),
$$

让

$$
\mathrm{supp}(p_{D_{\mathrm{aug}}})
\supset
\mathrm{supp}(p_{D_h})
$$

并尽量靠近真实部署分布。注意这里没有理论保证 $p_{D_{\mathrm{aug}}}=p_{\mathrm{deploy}}$；论文靠少量真实 demo fine-tuning 承认这个残差。

### 2.3 为什么图像增强不够：状态增强才有物理标签

普通视觉增强默认：

$$
(o_t,a_t)\in D
\Rightarrow
(g(o_t),a_t)\in D',
$$

其中 $g$ 是 crop、color jitter、blur 等变换。这在分类任务里常见，因为标签 $y$ 对这些变换不变。但在 manipulation 中，动作标签是否不变取决于物理状态。

例如物体初始 pose 变了：

$$
T_W^{O_{\mathrm{old}}}
\to
T_W^{O_{\mathrm{new}}},
$$

原动作 $a_{1:T}$ 不一定还能成功。若仍把 $(o'_{1:T},a_{1:T})$ 当监督标签，训练集会包含“看起来合理但物理上失败”的标签。CyberDemo 的 simulator replay/success filter 就是在避免这一点：

$$
(s'_{1:T},a'_{1:T}) \in D_{\mathrm{aug}}
\quad \text{only if} \quad
\mathrm{eval}(s'_{1:T},a'_{1:T})=1.
$$

所以本文的 augmentation 本质是 **label-preserving only after simulator validation**，不是先验地 label-preserving。

### 2.4 SE(3) object pose augmentation 从零推导

设 $T_A^B \in SE(3)$ 表示 frame $B$ 相对 frame $A$ 的位姿。原始 demo 中：

- object pose: $T_W^{O_{\mathrm{old}}}$；
- robot/end-effector pose: $T_W^{R_{\mathrm{old}}}$；
- 新随机 object pose: $T_W^{O_{\mathrm{new}}}$。

如果希望 robot 相对 object 的初始关系不变，先写出原始相对位姿：

$$
T_{O_{\mathrm{old}}}^{R_{\mathrm{old}}}
=
\left(T_W^{O_{\mathrm{old}}}\right)^{-1}T_W^{R_{\mathrm{old}}}.
$$

把同一个相对关系放到新 object 上：

$$
T_W^{R_{\mathrm{new}}}
=
T_W^{O_{\mathrm{new}}}
T_{O_{\mathrm{old}}}^{R_{\mathrm{old}}}.
$$

代入上式：

$$
T_W^{R_{\mathrm{new}}}
=
T_W^{O_{\mathrm{new}}}
\left(T_W^{O_{\mathrm{old}}}\right)^{-1}
T_W^{R_{\mathrm{old}}}.
$$

这就是论文里 naive reaching-to-new-pose 的数学来源。它能生成成功轨迹，但信息量低：每条增强轨迹都变成“先到新初始位姿，再重放原轨迹”。大量数据共享后半段原轨迹，BC 看到的是冗余样本，而不是多样化的接触策略。

CyberDemo 因此不把 $\Delta T$ 一次性塞进开头，而是把 object pose 变化分摊到整条轨迹中：

$$
\Delta T
=
T_W^{O_{\mathrm{new}}}
\left(T_W^{O_{\mathrm{old}}}\right)^{-1}.
$$

问题变成：哪些时间段应该承担更多 $\Delta T$？

### 2.5 轨迹段敏感度：把“该改哪里”变成可计算量

原始动作轨迹：

$$
\tau=\{a_1,a_2,\ldots,a_N\}.
$$

把它分成 $M$ 段，每段长度 $K=N/M$。对某个 segment，只扰动该段动作：

$$
a_i' = a_i+\delta_a\epsilon_i,
\quad
\epsilon_i\sim\mathcal{N}(0,1),
\quad
i\in \mathrm{seg},
$$

segment 外保持原动作不变，得到：

$$
\tau'
=
\{a_1,\ldots,a_n',\ldots,a_{n+K-1}',\ldots,a_N\}.
$$

然后用 simulator 判断这条扰动轨迹是否仍成功：

$$
\mathrm{eval}(\tau')=1.
$$

论文定义 segment robustness：

$$
\psi_{\mathrm{seg}}
=
\exp(\max \delta_a)
\quad
\text{s.t.}\quad
\mathrm{eval}(\tau')=1.
$$

含义很直接：

- 若一个 segment 在很大动作噪声下仍成功，$\max\delta_a$ 大，$\psi_{\mathrm{seg}}$ 大，说明它低敏感、高鲁棒；
- 若一个 segment 稍微扰动就失败，$\psi_{\mathrm{seg}}$ 小，说明它高敏感、低鲁棒；
- pre-grasp/far-from-object 往往低敏感，contact/precision phase 往往高敏感。

这里的关键洞见是：**object pose 变化不应该平均分配给每个时间步，而应该更多交给低敏感段。**

### 2.6 用 Lie algebra 把 $\Delta T$ 分配给轨迹段

由于 $\Delta T\in SE(3)$，不能直接把它当欧氏向量逐元素除以 $M$。CyberDemo 采用 $SE(3)$ 的 log/exp 思路：

1. 用 $\log(\Delta T)$ 把位姿变化映射到李代数 $\mathfrak{se}(3)$；
2. 按 segment robustness 分配比例；
3. 再用 $\exp(\cdot)$ 映回 $SE(3)$。

先归一化 robustness：

$$
\bar{\psi}_j
=
\frac{\psi_{\mathrm{seg}_j}}
{\sum_{m=1}^{M}\psi_{\mathrm{seg}_m}}.
$$

第 $j$ 段每一步承担的 pose increment：

$$
\Delta T_j
=
\exp\left(
\frac{\bar{\psi}_j}{K}\log(\Delta T)
\right).
$$

为什么除以 $K$？因为这一段有 $K$ 个时间步。若同一段内每步都施加同方向小位姿增量，则 $K$ 次累积近似为：

$$
\prod_{k=1}^{K}\Delta T_j
=
\exp\left(\bar{\psi}_j\log(\Delta T)\right),
$$

再跨段累积：

$$
\prod_{j=1}^{M}
\exp\left(\bar{\psi}_j\log(\Delta T)\right)
\approx
\exp\left(
\sum_{j=1}^{M}\bar{\psi}_j\log(\Delta T)
\right)
=
\exp(\log(\Delta T))
=
\Delta T.
$$

这个推导解释了本文最核心的数学结构：**整条轨迹最终吸收同一个 object pose change，但每段承担多少由 robustness 决定**。论文再通过 $f_i(\Delta T_j)$ 把 world-frame pose modification 转到当前 end-effector action frame，更新 6D 末端动作：

$$
a_i^{\mathrm{new}}
=
a_i f_i(\Delta T_j).
$$

这里不应过度解读成严格的群乘法 action model；论文的动作空间是末端 6D delta pose + finger target，$f_i$ 表示把位姿修正转换到当前动作表示的相似变换。更重要的边界是：**这个增强主要作用于 6D end-effector motion，不自动重写 16D finger joint motion**。

### 2.7 自动课程学习：为什么用 policy success 而不是 data generation rate

Algorithm 1 的训练循环可以抽象为：

$$
D \leftarrow D\cup \mathrm{aug}_L(D_h),
\quad
\pi_\theta \leftarrow \arg\min_\theta \mathcal{L}_{BC}(\theta;D),
\quad
r_{\mathrm{succ}}=\mathrm{eval}_L(\pi_\theta).
$$

升级规则：

$$
L\leftarrow L+1
\quad \text{if}\quad
r_{\mathrm{succ}}\ge r_{\mathrm{up}}
\quad \text{or}\quad
N_{\mathrm{fail}}\ge N_{\max}.
$$

这个设计微妙但重要：augmentation 难度不是按“仿真能生成多少成功轨迹”升级，而是按“当前 policy 能否在当前难度完成任务”升级。原因是 data generation rate 只说明 simulator replay 能找到成功动作，不说明 BC policy 已学会这个分布。

Table 3 直接验证了这一点：success-rate-based ACL 的真实 hardest setting 是 35%，data-generation-rate-based ACL 是 20%，无 curriculum 的 data-rate 版本只有 5%。这说明课程信号必须跟 learner 对齐，而不是只跟 generator 对齐。

### 2.8 信息流与算法机制

CyberDemo 的信息流可以写成五段：

| 阶段 | 输入 | 输出 | 作用 |
|---|---|---|---|
| Sim teleoperation | human motion + SAPIEN env | $D_h$ | 获得可重放的原始 demo seed |
| Sim augmentation | $D_h$ + oracle state/contact + randomized visual/geometry/pose | $D_{\mathrm{aug}}$ | 生成视觉、几何、运动学覆盖 |
| Auto curriculum | $\mathrm{aug}_L$, $\mathrm{eval}_L$, $\pi_\theta$ | level-wise dataset growth | 避免一开始训练在过难/过噪分布上 |
| Policy learning | RGB + proprioception, action chunks | ACT-style visuomotor policy | 降低 compounding error，平滑 human teleop 噪声 |
| Few real fine-tuning | about 3-minute real trajectories/task | deployment policy | 修补 controller/contact/visual residual gap |

注意 simulator oracle state/contact 只服务于数据生成和验证，不是部署 policy 的输入。这一点让方法更可部署，但也限制了它对高精度接触模式的可解释性。

## 3. 训练、数据与实验

### 3.1 实验设置

| 项 | 论文设置 |
|---|---|
| Robot | Allegro hand + XArm6 |
| Action | 6D arm end-effector delta pose + 16D finger joint position target |
| Control | arm/hand 都用 PD control |
| Observation | RGB image + robot proprioception |
| Demo rate | 30 Hz |
| Real data | 每个任务约 3 分钟真实轨迹 |
| Sim env | SAPIEN 中复刻真实桌面、物体和任务 |
| Tasks | pick-and-place, rotate valve, pour |
| Policy | ACT-style action chunking policy |
| Baselines | R3M, PVR, MVP，均用作者提供预训练模型并在同一真实 demo 数据上 fine-tune |
| Real evaluation | 每个 setting 20 trials |
| Sim ablation eval | Table 2/3 中每个 setting 200 simulations |

任务设计：

| 任务 | 成功条件 | 为什么能检验故事 |
|---|---|---|
| Pick and Place | 把物体放到红盘上 | 准静态任务，主要考察视觉/pose/object coverage |
| Rotate | 把 valve 转到 720 degrees | 非准静态任务，考察控制器 gap 和接触动态 |
| Pour | 把 4 个小盒子全部倒入碗中 | 同时需要 grasp、transport、orientation control |

四个 real-world evaluation levels：

| Level | 真实评估条件 |
|---|---|
| L1 | In Domain |
| L2 | Out of Position |
| L3 | Random Light |
| L4 | Out of Position + Random Light |

### 3.2 主结果：仿真增强是否真的比视觉预训练更有用

Table 1 的核心数字如下，单位是 success / 20 trials。

| Task / Setting | R3M | PVR | MVP | CyberDemo |
|---|---:|---:|---:|---:|
| Bottle L1 | 2 | 4 | 2 | 7 |
| Bottle L2 | 0 | 0 | 0 | 6 |
| Bottle L3 | 0 | 0 | 3 | 8 |
| Bottle L4 | 0 | 0 | 1 | 5 |
| Can L1 | 7 | 4 | 7 | 14 |
| Can L2 | 3 | 0 | 2 | 11 |
| Can L3 | 4 | 3 | 4 | 13 |
| Can L4 | 0 | 0 | 2 | 13 |
| Pour L1 | 3 | 2 | 1 | 9 |
| Pour L2 | 0 | 0 | 1 | 4 |
| Pour L3 | 0 | 1 | 3 | 10 |
| Pour L4 | 0 | 0 | 2 | 7 |
| Rotate L1 | 11 | 8 | 8 | 15 |
| Rotate L2 | 2 | 3 | 4 | 10 |
| Rotate L3 | 6 | 5 | 10 | 17 |
| Rotate L4 | 2 | 1 | 6 | 13 |

因果解释：

- 在 in-domain L1，CyberDemo 总计 $45/80=56.25\%$，三种视觉预训练 baseline 平均约 $24.58\%$，差值正好是论文报告的 31.67 percentage points。这说明它不是只在 OOD 才有效，而是仿真增强本身也提升了 task-relevant policy prior。
- 在 Bottle/Can/Pour 的 L4，baseline 多数接近 $0/20$，CyberDemo 分别是 $5/20,13/20,7/20$。这对应它的视觉和 pose augmentation story：光照和位置组合变化正是增强覆盖的目标。
- Rotate L3/L4 中 CyberDemo 是 $17/20,13/20$，MVP 是 $10/20,6/20$，R3M 是 $6/20,2/20$。这说明即使视觉 backbone 强，若没有物理轨迹覆盖和少量真实 fine-tune，非准静态接触任务仍不稳。

这张表最重要的判断不是“CyberDemo 第一”，而是：**它打败的是用真实 demo fine-tune 的大规模视觉预训练模型**。因此结果支持的不是“视觉表征不重要”，而是“对灵巧操作，视觉表征不等于动作-接触分布覆盖”。

### 3.3 Novel object generalization

论文报告两个关键泛化结果：

| Scenario | Baseline behavior | CyberDemo behavior | 解释 |
|---|---|---|---|
| Pick-and-place novel objects | baselines 在复杂 light/pose/object 组合下大幅下降 | Figure 4 中 CyberDemo 在最难组合仍显著高于 baseline | diverse object augmentation 让 policy 见过对象形状变化，而不是只靠 R3M 的 image prior |
| Rotate novel tetra/penta valve | hardest setting 中 baseline 只有一个方法偶然达到 2.5% | CyberDemo 在最难 novel-object + random-light + out-of-position setting 仍有 30%，平均/相关设置中报告 42.5% | tri-valve demo 被扩展成几何变化下的 contact strategy family |

这里的边界也要说清楚：novel valve 不是任意未知物体。tetra/penta-valve 与 tri-valve 仍共享“中心旋转、径向把手、桌面固定底座”的任务结构。CyberDemo 证明的是 **同一任务拓扑下的形状泛化**，不是开放世界物体操作。

### 3.4 Data augmentation ablation

Table 2 直接回答：“是不是 augmentation level 越全越好？”

| Training levels / demos | Sim L1 | Sim L2 | Sim L3 | Sim L4 | Real In Domain | Real Random Light | Real Out of Position | Real Out of Position + Random Light |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| [1] / 100 | 78% | 0% | 0% | 0% | 20% | 5% | 0% | 0% |
| [1,2] / 330 | 73% | 75% | 10.5% | 7.5% | 15% | 25% | 0% | 0% |
| [1,2,3] / 550 | 58% | 66.5% | 43.5% | 21% | 15% | 15% | 5% | 15% |
| [1,2,3,4] / 810 | 92.5% | 81% | 63% | 49% | 35% | 30% | 30% | 40% |

Ablation 因果链：

`只用 Level 1 → sim L1 有 78% 但 L2-L4 全 0 → policy 只学到窄初始分布 → real OOD 也几乎全 0 → 真实 demo 少时，in-domain 拟合不能替代 coverage。`

`加入 Level 2 → sim L2 到 75%、real random light 到 25% → 视觉随机化开始对对应评估维度有效 → 但 out-of-position 仍 0 → 光照增强不能替代 pose coverage。`

`加入 Level 3 → sim L3 到 43.5%、real hardest 到 15% → target/pose 变化开始进入支持集 → 但 Level 4 仍弱 → 说明难度覆盖仍不足。`

`Level 1-4 全部加入 → sim L1 也从 78% 到 92.5%，real hardest 到 40% → 更强随机化没有破坏简单场景，反而提升基础鲁棒性 → coverage gain 大于 distribution noise cost。`

最有意思的是 sim L1：全 augmentation 版本比只训 L1 还高。这反驳了一个常见担心，即“随机化会牺牲 in-domain 性能”。在这篇论文的设置里，增强分布仍围绕同一任务结构，因此更像 regularization，而不是无关噪声。

### 3.5 Auto-curriculum ablation

Table 3 对比三种课程信号：

| Method | Sim L1 | Sim L2 | Sim L3 | Sim L4 | Real hardest setting |
|---|---:|---:|---:|---:|---:|
| ACL (Task success) | 80% | 61% | 43.5% | 57% | 35% |
| ACL (Data generation rate) | 19.5% | 30% | 75% | 66% | 20% |
| ACL wo CL (Data generation rate only) | 20% | 22% | 32.5% | 15% | 5% |

因果解释：

- ACL(Task) 的 sim L4 不是最高，但 real hardest 最高。这说明 curriculum 不是为了让 simulator replay 越难越好，而是为了让 learner 形成可迁移 policy。
- ACL(Data) 在 sim L3/L4 高，却 real 较低，说明“容易生成成功轨迹”的分布不等于“policy 学出来后能真实部署”的分布。
- 无课程版本 real hardest 只有 5%，说明直接把复杂增强喂给 BC 会造成早期学习信号混乱：policy 还没掌握基础接近/抓取，就被高随机化样本推着拟合多峰动作。

这对 WMTS 很重要：任务生成器的评价指标不能只看“能生成多少任务/轨迹”，必须看当前 learner 在这些任务上的学习进展。也就是 generator-centered curriculum 不够，learner-centered curriculum 才有效。

### 3.6 工程边界

| 设计 | 论文收益 | 边界 |
|---|---|---|
| ACT action chunking | 平滑人类 teleop 噪声，降低逐步 BC compounding error | 不解决 demo 分布外状态纠错；没有 DAgger/online recovery |
| Action aggregation for small motion | 合并小抖动/停顿，减少低质量 teleop label | 可能删除 contact-rich manipulation 中有意义的微小调整 |
| Few real demo fine-tuning | 修补 controller/dynamics/visual residual gap | 说明方法不是 zero-shot；真实 demo 仍是必要校准 |
| SAPIEN task replication | 允许 replay、oracle state/contact、success filter | 每个真实任务仍需搭建仿真环境；接触模型质量决定上限 |

## 4. 核心洞见

### 4.1 论文真正的 insight

CyberDemo 的 insight 是：**仿真 demo 的价值不在“更真实”，而在“可编辑”。**

真实 demo 是高保真但低可编辑的数据；仿真 demo 是低保真但高可编辑的数据。只要最后用少量真实 demo 校准，后者能通过可编辑性获得更大的分布覆盖。这个思想解释了为什么 30 分钟 sim demo + augmentation + 3 分钟 real fine-tune 能打过只依赖真实 demo fine-tuned 的 R3M/PVR/MVP。

### 4.2 为什么这个设计有效

有效性来自三个层次叠加：

1. **视觉层**：camera/light/texture randomization 让 encoder 不把策略绑死在采集环境；
2. **运动学层**：SE(3) object pose augmentation 让动作不只会原始相对位姿；
3. **任务层**：success filter 和 auto curriculum 保证新增样本不是任意噪声，而是当前任务结构内的可学习变化。

三个层次缺一不可。只有视觉层，会变成普通 domain adaptation；只有运动学层，没有课程，BC 容易被过难样本打乱；只有课程，没有真实 fine-tune，controller/contact gap 仍会暴露，尤其是 rotate 这类非准静态任务。

### 4.3 什么时候会失效

CyberDemo 的失效条件也很清楚：

| 失效条件 | 为什么会失效 | 对应到转笔/WMTS |
|---|---|---|
| 仿真器无法稳定判断 success | success filter 选不出真实有效轨迹 | 转笔掉落/滑移需要高质量 contact/friction sensing，不能只靠视觉成功 |
| task topology 变化太大 | tri-valve 到 tetra-valve 可泛化，但 valve 到 rope/cloth 不是同一结构 | 只用笔形状随机化不能覆盖不同非抓取接触模式 |
| 关键动作在 finger-level contact，而非 EE pose | 论文 SE(3) augmentation 主要改 arm/EE motion | 转笔核心是指尖力、切向摩擦、相位切换，不能只改 wrist pose |
| real fine-tuning 数据太少或偏置 | residual gap 无法校准 | LinkerHand actuator latency、tactile threshold、CAN 延迟都可能需要专门校准 |
| human demo 噪声和微动作不可简单聚合 | action aggregation 会吞掉细微控制 | 转笔中小幅拨动/摩擦调节可能正是 skill，而不是噪声 |

## 5. 替代方案与理论局限

### 5.1 理论维度

**BC 分布漂移没有被根治。** CyberDemo 扩大 $D$，但目标仍是 supervised imitation：

$$
\min_\theta
\mathbb{E}_{(o,a)\sim D_{\mathrm{aug}}\cup D_{\mathrm{real}}}
\ell(\pi_\theta(o),a).
$$

当 policy rollout 进入 demo/augmentation 没覆盖的状态，仍没有在线纠错机制。ACT chunking 只是缩短有效决策频率、平滑动作，不等于 DAgger。

**augmentation 分布没有最优性保证。** Level 1-4 是人为设计的随机化维度，成功率阈值也是启发式。它证明了这些增强在三类任务上有效，但没有告诉我们如何从 deployment distribution 反推最小充分增强集。

**SE(3) 位姿分配不是完整接触动力学。** 它是 kinematic augmentation，而不是 contact dynamics augmentation。没有显式建模：

$$
M(q)\ddot q+C(q,\dot q)\dot q+g(q)
=
\tau+J_c(q)^\top \lambda,
$$

也没有建模摩擦锥、stick-slip、触觉观测等。对 valve rotate 已经需要真实 fine-tune；对 pen spinning 这种非抓取动态接触，边界会更明显。

### 5.2 算法维度

| 替代路线 | 优点 | 相对 CyberDemo 的代价 |
|---|---|---|
| DAgger / online correction | 直接修正 covariate shift | 需要真实交互和人类在线纠正，灵巧手成本高 |
| RL + domain randomization | 可从 reward 优化超越 demo | reward/reset/探索成本高，灵巧手 contact 任务样本需求大 |
| DemoStart 类 demo-reset RL | demo state 变 curriculum reset，可学到超越 demo 的策略 | 需要 teacher/RL training，系统复杂度高 |
| MimicGen 类仿真 demo synthesis | 长程任务数据生成能力强 | 若不加 real fine-tune，不能直接声明 real dexterous transfer |
| Diffusion Policy | 能表示多模态动作分布 | 仍需要覆盖足够的数据；不能自动解决 sim-to-real gap |

### 5.3 工程/实验维度

- 真实评估每 setting 20 trials，足够展示趋势，但不足以细分失败模式。
- 任务都在固定桌面环境，object family 相对可控；开放环境、遮挡严重场景未证明。
- 少量真实 demo 是每任务都要采的，不是一次采完全迁移。
- 论文没有把 tactile sensing 纳入 policy 输入；对接触状态不可见的任务，视觉+本体可能不够。
- 仿真环境仍需人工搭建。作者正确指出它不需要 RL reward design，但几何、材质、关节、接触参数的建模仍是人力成本。

## 6. 对用户研究的启发

### 6.1 对 WMTS 的直接迁移

CyberDemo 可以成为 WMTS 的“轨迹级数据生成前端”，但要做三处改造：

| CyberDemo 变量/模块 | 在 WMTS 中应变成什么 | 为什么 |
|---|---|---|
| $D_h$ simulated teleop demos | PPO Oracle 或 human/retargeted seed trajectories | WMTS 不应只靠人类 teleop；PPO Oracle 可生成更覆盖的 specialist seed |
| $\mathrm{aug}_L(D_h)$ | latent task generator proposed rollouts | augmentation level 可对应 task difficulty / object pose / contact phase / actuator delay |
| $\psi_{\mathrm{seg}}$ robustness | ensemble world model uncertainty + contact sensitivity score | 不能只用动作噪声成功率；转笔需要预测滑移/掉落风险 |
| $\mathrm{eval}_L(\pi)$ | learner-centered scheduler signal | 沿用 Table 3 的教训：generator 成功率不能替代 policy 学习进展 |
| few real demo fine-tuning | LinkerHand real-robot residual calibration | 真实 actuator/tactile/contact gap 必须被显式承认 |

最值得复刻的是课程信号：**task scheduler 应该看当前 policy/world-model 在任务上的学习状态，而不是只看任务生成器能否生成任务。** 这和 WMTS 的名字高度一致：world model as task scheduler 的 scheduler 应该是 learner-conditioned。

### 6.2 对转笔/DNPM 的具体设计

CyberDemo 的 sensitivity-aware augmentation 可迁移，但 action space 必须改。

| CyberDemo 中的对象 | 转笔中对应对象 | 必须修改的原因 |
|---|---|---|
| object pose change $\Delta T$ | pen initial pose / angular momentum / grip phase change | 转笔不只是物体位姿变化，还有动量和接触相位变化 |
| low-sensitivity segment | free-space approach / pre-contact reposition | 可承担较大随机化 |
| high-sensitivity segment | flick、catch、rolling contact、slip boundary | 不能简单聚合或大扰动 |
| 6D EE delta pose | finger joint torques/targets + tactile/contact latent | 转笔核心不是腕部轨迹，而是指尖接触力 |
| success filter | no-drop + desired spin axis + angular velocity + tactile stability | 成功不是单一终点事件，需要时序约束 |

一个可验证实验：

1. 用现有 DNPM/PPO specialist 生成若干成功转笔轨迹；
2. 按时间段测 action-noise robustness，得到 $\psi_{\mathrm{seg}}$；
3. 只在高 $\psi$ 段随机化 object/hand pose，在低 $\psi$ 接触段保持或小范围扰动；
4. 对比三组 BC/DP generalist：无增强、均匀增强、sensitivity-aware 增强；
5. 若 CyberDemo 机制成立，sensitivity-aware 应该在真实/高保真仿真 perturbation 下优于均匀增强，同时不牺牲 in-domain 成功率。

可能 falsify 的结果：如果均匀增强和 sensitivity-aware 没差，说明转笔的关键泛化不是“哪些时间段能承担变化”，而可能是 tactile belief / actuator latency / friction randomization 才是瓶颈。

### 6.3 与 DemoStart / DemoSpeedup 的组合

三篇 demonstration 论文可以形成一个数据飞轮：

| 论文 | demo 被当作什么 | 对 WMTS 的角色 |
|---|---|---|
| CyberDemo | physically editable trajectory seed | 生成多条件 imitation pretraining data |
| DemoStart | reset-state curriculum frontier | 让 PPO Oracle 从有价值失败边界继续探索 |
| DemoSpeedup | time allocation resource | 压缩低信息段，突出高精度接触段 |

组合方式：

$$
\text{seed demo}
\xrightarrow{\text{CyberDemo}}
\text{augmented trajectory family}
\xrightarrow{\text{DemoStart}}
\text{frontier reset states}
\xrightarrow{\text{PPO Oracle}}
\text{specialist success/failure data}
\xrightarrow{\text{DemoSpeedup}}
\text{time-efficient generalist training set}.
$$

这条链条的 critical point 是：CyberDemo 的 action aggregation 不能盲目套用 DemoSpeedup 的加速思想。对于转笔，高 entropy/高 sensitivity 的接触瞬间可能需要保留甚至加密，而不是合并。

### 6.4 不应过度外推的点

- 不要把“仿真 demo 优于真实 demo”读成“真实 demo 不重要”。论文用了 real fine-tuning，且 rotate 这种动态任务正说明 residual gap 存在。
- 不要把 42.5% novel valve 泛化读成开放类别泛化。它仍在同一 valve 操作拓扑内。
- 不要把 random camera/light/texture 当成 tactile/contact gap 的替代。视觉 DR 解决不了指尖剪切、法向力阈值和 actuator latency。
- 不要照抄 action aggregation 到转笔。teleop 手抖可能是噪声，但转笔中的微小滑移修正可能是控制信号。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

CyberDemo 对 RL/IL 基础的贡献是把 BC 的核心短板从 objective 层移到 data distribution 层分析：

$$
\mathcal{L}_{BC}
\text{ 不变}
\quad \Rightarrow \quad
\text{提升来自 } p_D \text{ 的支持集扩展，而不是优化目标创新。}
$$

这和 PPO/RL 路线形成互补。RL 通过 online interaction 改变数据分布，CyberDemo 通过 simulator augmentation 离线改变数据分布。对 WMTS 来说，二者不应互斥：CyberDemo 可用于 generalist pretraining，PPO Oracle 用于填补 BC 无法覆盖的失败边界。

### 7.2 与 [[RepresentationLearning]] 的联系

R3M/PVR/MVP 对比说明：大规模视觉表征不是 manipulation policy 的充分条件。真正要学的是：

$$
\phi(o_t)
\to
a_{t:t+H}
\quad
\text{under contact- and pose-varying task distribution}.
$$

CyberDemo 的增强让 representation 不只对图像变换不变，还要对任务等价的物理变化保持可控。换句话说，它把 representation learning 从 passive invariance 推向 active, action-conditioned invariance。

### 7.3 与 [[EmbodiedAI]] 的联系

CyberDemo 是 embodied data flywheel 的小型版本：

$$
\text{simulate}
\to
\text{augment}
\to
\text{imitate}
\to
\text{few real adapt}
\to
\text{deploy}.
$$

但它也提醒 WMTS：数据飞轮必须有物理验证环节。没有 success filter 的合成数据只是“看起来多”；有 success filter 和 learner-centered curriculum 的数据才可能变成可学习的 task distribution。

## 8. 应复刻的提问颗粒度

| 用户式追问 | Agent 应主动补充 |
|---|---|
| “它相对 MimicGen / DemoStart 的 value add 是什么？” | MimicGen 合成 sim policy 数据；DemoStart 用 demo reset 做 RL curriculum；CyberDemo 用仿真 demo 做真实部署前的物理增强 pretraining |
| “公式里的 $\Delta T$ 到底怎么来的？” | 从保持 robot-object relative pose 推导 $T_W^{R_{\mathrm{new}}}=T_W^{O_{\mathrm{new}}}(T_W^{O_{\mathrm{old}}})^{-1}T_W^{R_{\mathrm{old}}}$，再解释为什么 naive reaching 冗余 |
| “敏感度为什么能指导 augmentation？” | segment 可承受的最大动作噪声越大，越说明低敏感，越适合承担 object-pose change |
| “实验到底证明了什么？” | Table 1 证明仿真增强打过真实 demo fine-tuned 视觉预训练；Table 2 证明 coverage level 对应 OOD level；Table 3 证明 learner-centered curriculum 优于 generator-centered curriculum |
| “能不能直接用于转笔？” | 思想可迁移，6D EE augmentation 不可直接迁移；必须改成 finger contact/tactile/actuator-aware augmentation |

## References

- Jun Wang, Yuzhe Qin, Kaiming Kuang, Yigit Korkmaz, Akhilan Gurumoorthy, Hao Su, Xiaolong Wang. **CyberDemo: Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation**. CVPR 2024.
