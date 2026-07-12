---
tags:
  - paper
  - manipulation
  - imitation-learning
  - action-chunking
  - bimanual-manipulation
aliases:
  - ACT
  - ALOHA
paper-year: 2023
read-date: 2026-03-25
venue: RSS 2023
paper-pdf: "[[Papers/ACT: Learning Fine-Grained Bimanual Manipulation with.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
---

# Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)

> [!abstract] 核心贡献
> 本文同时提出低成本双臂遥操作硬件 ALOHA 与 Action Chunking with Transformers (ACT)：ALOHA 用 <$20k 的 ViperX/WidowX leader-follower 系统收集高质量 50Hz 示范，ACT 则让策略从单步动作预测升级为长度 $k$ 的未来动作序列预测，并用 CVAE 处理人类示范多模态、用 temporal ensembling 平滑重叠动作块；在 6 个真实精细双臂任务上仅用约 10-20 分钟示范数据达到最高 80-90% 级成功率。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — ACT 是 behavior cloning 的结构化改造：把 decision horizon 从每步决策改成 chunk-level 决策，缓解但不消除 covariate shift。
> - [[RepresentationLearning]] — CVAE 的 latent $z$ 是人类示范风格/多模态的 information bottleneck；Transformer decoder 是动作序列生成器。
> - [[ControlTheory]] — ALOHA 的 joint-space teleoperation、50Hz 控制、低层 PID target joint position，都是硬件可执行性的核心，而不是论文附属细节。
> - [[StochasticProcess]] — human demonstration 中的 pause、handover location、随机细节是 temporally correlated confounders；action chunking 在局部窗口内吸收这些非 Markov 因素。
>
> **核心技术**: Action Chunking, Temporal Ensembling, CVAE Policy, Pixel-to-Joint Imitation Learning, Low-Cost Bimanual Teleoperation

> [!note] 簇内坐标与暗线（模仿学习 · 数据生成 · 真机 RL · 人机协作）
> **簇内互链（Delta）**
> - vs [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations|MimicGen]] / [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation|CyberDemo]]：都降低精细操作门槛，但 ACT 在**算法/表示侧**（chunk + CVAE 改造 BC 输出），二者在**数据侧**（segment 变换 / 物理增强）——正交互补。
> - vs [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration|DemoSpeedup]]：DemoSpeedup 直接以 ACT 为 proxy/最终 policy，改写 chunk 的**时间尺度**（熵引导加速）；ACT 定义 chunk，DemoSpeedup 调 chunk 的执行速度。
> - vs [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]：RL-100 把 chunked (diffusion) action 接入真机 RL fine-tuning，**突破 ACT 的 imitation ceiling**。
>
> **Foundation 精确锚点**（已 grep 验证）
> - [[RepresentationLearning#2.3 ACT：动作分块处理长时相关|RepresentationLearning §2.3]] — ACT 的数学根（CVAE + Transformer decoder）就在此节。
> - [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|RL §7.4]] — action chunking 把有效 horizon 从 $T$ 砍到 $T/H$、缓解复合误差 $O(\epsilon T^2)$ 的落点在此。
>
> **暗线**：**POMDP→belief→latent**——action chunk 是 latent plan 的一种，CVAE 的 $z$ 吸收人类多模态 belief；**模仿×强化缝合线**的"纯 BC"端（缓解但未消除 covariate shift，需 §9.3 真机 RL 收口）。

## 0. 阅读定位与范本价值

ACT 这篇论文容易被误读成“Transformer + CVAE 成功了”。更准确的读法是：**硬件采集分布、动作输出粒度、时序平滑和生成式 imitation objective 四件事共同成立，才让低成本硬件做精细操作。**

对你的 WMTS / 灵巧手研究，它的价值不只是 imitation baseline，而是 action representation 的基础经验：高频控制下，单步 action 太碎，纯开环 chunk 太迟钝；ACT 的重叠动作块是这两者之间的工程折中。

最低标准映射：

| 四支柱 | 本文 recap 的落点 | 必须抓住的判断 |
|---|---|---|
| 逻辑与价值 | §1, §4 | 论文的故事是“低成本硬件 + 结构化 BC”共同降低 fine manipulation 门槛 |
| 原理与理论 | §2 | 从 BC covariate shift 到 action chunking、CVAE ELBO、temporal ensemble 的变量来源 |
| 实验与验证 | §3 | 真实任务表、chunking ablation、CVAE ablation、50Hz user study 必须一起看 |
| 未来与结合 | §5-§7 | 对 PPO/WMTS 可借鉴 chunk/macro-action，但 temporal ensemble 会破坏简单 policy-gradient logprob 语义 |

## 1. 问题设定与动机

### 1.1 一句话核心

ACT 让策略每次预测未来 $k$ 步 target joint positions，并在推理时重叠预测同一时刻动作，从而在高频视觉闭环和低频长期一致性之间取得折中。

### 1.2 直观隐喻

单步 BC 像一个人每走一毫米都重新问“下一毫米怎么走”：每次误差很小，但很容易在长任务中偏离轨道。完全开环的长轨迹像“看一眼就走完整条路”：中途遇到偏差无法纠正。ACT 像每一帧都重新规划未来一小段路，然后对多个计划在当前步的建议做加权投票。

这个隐喻的关键是：ACT 不是抛弃闭环，而是用 overlapping chunks 保留高频观测更新。

### 1.3 现有方法的局限

| 方法 | 注入了什么先验 | 关键局限 |
|---|---|---|
| 单步 BC / ConvMLP | 当前图像+关节 → 下一步动作 | fine manipulation 中每步毫米级误差会快速 compound |
| history-conditioned BeT/RT-1 | 用历史窗口缓解非 Markov | 仍逐步输出；离散 action bin 对精细连续关节 target 不友好 |
| DAgger / online correction | 让专家纠正 off-distribution states | 遥操作纠正成本高；噪声注入对精细任务会直接导致失败 |
| 模型/规划 | 显式建模接触、形变、视觉几何 | condiment cup、ziploc、tape 等软/透明/接触丰富物体建模成本很高 |
| 高端硬件遥操作 | 更高精度和传感器 | 成本高、难复现；论文目标是 <$20k 的可复制系统 |

### 1.4 Delta 分析

本文有两个互相支撑的 Delta：

1. **硬件 Delta**：ALOHA 用低成本 leader-follower joint-space mapping 收集精细双臂示范，不依赖高端力传感、深度相机或工业臂。
2. **算法 Delta**：ACT 用 action chunking + CVAE + temporal ensembling，把 BC 的输出从 $a_t$ 改成 $a_{t:t+k}$，并处理人类示范中的多模态与暂停。

这两个 Delta 缺一不可。没有 ALOHA，数据质量不足；没有 ACT，单步 BC 在高精度长时序任务里迅速崩。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 空间/类型 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $o_t$ | images + joint positions | observation | 否 | 当前视觉与本体状态 | 图像来自 4 个 RGB camera；关节是 follower joints |
| $\bar o_t$ | proprioception-only observation | CVAE encoder input | 否 | 去掉 image 的训练时条件 | encoder 训练时不看图像以加快训练 |
| $a_t$ | $\mathbb R^{14}$ | leader joint positions | 监督标签 | 双臂 7+7 target joint positions | 用 leader 而非 follower，隐含人施力意图 |
| $a_{t:t+k}$ | $\mathbb R^{k\times14}$ | demonstration chunk | 监督标签 | 未来 $k$ 步动作序列 | $k=100$ 是默认超参，不是 universally optimal |
| $q_\phi(z|a_{t:t+k},\bar o_t)$ | diagonal Gaussian | CVAE encoder | 是 | 示范动作风格后验 | 测试时 encoder 丢弃 |
| $z$ | $\mathbb R^{32}$ | CVAE latent | 是/测试固定 | 人类多模态风格变量 | 推理时设 $z=0$，并不采样多模式 |
| $\pi_\theta(\hat a_{t:t+k}|o_t,z)$ | Transformer decoder policy | 学习模型 | 是 | 从当前观测生成未来动作块 | 输出绝对 joint target，不是 delta action |
| $B[t]$ | FIFO action buffer | inference state | 否 | 存储多个 chunk 对同一时刻 $t$ 的预测 | 行为依赖 buffer，非简单 Markov policy |
| $w_i=\exp(-mi)$ | temporal ensemble weight | inference rule | 否 | 融合同一时刻的多次预测 | 不是训练 loss；$m$ 控制新旧预测融合 |
| $k$ | chunk size | hyperparameter | 否 | 有效决策粒度 | $k=1$ 退化单步 BC；$k$ 太大接近开环 |
| $\beta$ | KL weight | hyperparameter | 否 | 控制 latent 信息瓶颈 | 高 $\beta$ 让 $z$ 传信息更少 |

### 2.2 从 BC 的误差累积到 action chunking

单步 BC 学：

$$
\pi_\theta(a_t|o_t).
$$

如果每步有小误差，rollout 后状态分布会偏离示范分布：

$$
o_t^{\pi_\theta}\not\sim o_t^{\mathrm{demo}}.
$$

fine manipulation 中这个问题尤其严重，因为几毫米误差就会错过拉链头、线孔、电池槽或杯盖边缘。ACT 改成：

$$
\pi_\theta(a_{t:t+k}|o_t),
\qquad
a_{t:t+k}\in\mathbb R^{k\times14}.
$$

若天真地每 $k$ 步观测一次并执行完整 chunk，有效决策步数从 $T$ 降到 $T/k$，误差累积路径变短；但这会损失闭环反应。因此 ACT 的实际推理不是“每 $k$ 步看一次”，而是每个 timestep 都查询策略，生成重叠 chunks。

### 2.3 Temporal ensembling：同一时刻动作的多次预测投票

推理时，第 $t$ 个真实动作可能被过去多个 chunk 预测过。Algorithm 2 用 buffer $B[t]$ 保存这些候选：

$$
A_t=B[t].
$$

执行动作为：

$$
a_t=
\frac{\sum_i w_i A_t[i]}{\sum_i w_i},
\qquad
w_i=\exp(-m i).
$$

这和普通 action smoothing 的差别是：普通 smoothing 混合相邻时间步动作；ACT 混合的是“不同观测时刻对同一个时间步的预测”。因此它减少 jerky switching，但理论上仍在执行一个由 history/buffer 定义的策略。

这个细节对 RL 迁移非常重要：如果在 PPO 里照搬 temporal ensembling，最终执行动作不再是单次 policy forward 的样本，logprob/importance ratio 会变复杂。

### 2.4 CVAE：人类示范的多模态不是噪声

同一个观测下，人可能用不同但都成功的轨迹完成任务，尤其是 handover 位置、暂停时长、绕障方式。这对单峰回归是灾难：平均轨迹可能撞物体或错过接触点。

ACT 训练 CVAE：

$$
q_\phi(z|a_{t:t+k},\bar o_t),
\qquad
\pi_\theta(\hat a_{t:t+k}|o_t,z).
$$

Loss：

$$
\mathcal L
=
\mathcal L_{\mathrm{reconst}}
+
\beta D_{KL}\left(q_\phi(z|a_{t:t+k},\bar o_t)\,\|\,\mathcal N(0,I)\right).
$$

Algorithm 1 写 reconstruction 为 MSE，但正文实现强调使用 L1 loss 比 L2 更精确；因此更稳妥的读法是：ACT 的核心是 reconstruction + KL 的 CVAE 目标，最终实现中 L1 是关键工程选择。

训练/推理区别：

| 阶段 | $z$ 来源 | encoder 是否使用 | 含义 |
|---|---|---|---|
| train | $z\sim q_\phi(z|a_{t:t+k},\bar o_t)$ | 使用 | 用动作序列解释示范风格 |
| test | $z=0$ | 丢弃 | 取 Gaussian prior 均值，确定性解码 |

这也暴露一个边界：ACT 用 CVAE 改善训练，但推理时没有显式采样多种动作模式；它偏向“最典型风格”，而不是在线多假设规划。

### 2.5 Transformer architecture 与 shape

Observation：

- 4 路 RGB camera；
- 每路 $480\times640\times3$；
- follower robot joint positions；
- action 是双臂 target joint positions，$14$ 维。

Image encoder：

$$
480\times640\times3
\xrightarrow{\mathrm{ResNet18}}
15\times20\times512.
$$

每个 camera flatten 为 $300\times512$，4 个 camera 得到 $1200\times512$。再 append：

- joint feature: $14\to512$；
- style variable: $z\in\mathbb R^{32}\to512$。

所以 transformer encoder 输入约为：

$$
1202\times512.
$$

Transformer decoder 用固定 position embeddings 作为 $k$ 个 queries，cross-attend encoder output，输出：

$$
k\times512 \to k\times14.
$$

默认超参：

| 项 | 数值 |
|---|---:|
| parameters | about 80M |
| training time | about 5h on one 11G RTX 2080Ti |
| inference time | about 0.01s |
| learning rate | $10^{-5}$ |
| batch size | 8 |
| encoder layers | 4 |
| decoder layers | 7 |
| feedforward dim | 3200 |
| hidden dim | 512 |
| heads | 8 |
| chunk size | 100 |
| $\beta$ | 10 |
| dropout | 0.1 |

### 2.6 ALOHA 硬件不是背景板

ALOHA 的硬件选择直接塑造数据分布：

| 设计 | 作用 |
|---|---|
| <$20k off-the-shelf + 3D printed parts | 让 fine manipulation 数据采集可复制 |
| ViperX 6-DoF follower + gripper | 低成本执行端；payload 750g，accuracy 5-8mm |
| WidowX leader | 操作者 backdrive 小臂，joint-space 映射到 follower |
| joint-space mapping | 避开低 DoF 机械臂 IK near-singularity 失败，降低 latency |
| leader 重量/橡皮筋平衡 | 物理上过滤手抖，让人类动作更平滑 |
| 4 RGB cameras | top/front/wrist 视角覆盖精细接触 |
| 50Hz data/control | 400-700 steps per 8-14s demo；高频微调精细接触 |

论文很诚实地表明：算法成功不是在任意廉价硬件上发生，而是在一个为了 imitation 数据质量精心设计的低成本遥操作系统上发生。

## 3. 训练、数据与实验

### 3.1 数据采集

| 项 | 设置 |
|---|---|
| real tasks | 6 个：Slide Ziploc, Slot Battery, Open Cup, Thread Velcro, Prep Tape, Put On Shoe |
| sim tasks | 2 个：Cube Transfer, Bimanual Insertion |
| real demos | 每任务 50 条，Thread Velcro 100 条 |
| episode length | 8-14s |
| control frequency | 50Hz |
| timesteps per episode | 400-700 |
| data amount | 每真实任务约 10-20 min 有效示范，30-60 min wall-clock |
| sim demos | scripted 50 + human 50 |

### 3.2 主结果：ACT 在最后子任务上压倒 baselines

Table I/II 的核心不是看第一阶段是否会碰到物体，而是看最终子任务是否完成。下面列最终成功率：

| Task | BC-ConvMLP | BeT | RT-1 | VINN | ACT |
|---|---:|---:|---:|---:|---:|
| Cube Transfer sim, scripted | 1 | 27 | 2 | 3 | **86** |
| Cube Transfer sim, human | 0 | 1 | 0 | 0 | **50** |
| Bimanual Insertion sim, scripted | 1 | 3 | 1 | 1 | **32** |
| Bimanual Insertion sim, human | 0 | 0 | 0 | 0 | **20** |
| Slide Ziploc real | 0 | 0 | 0 | 0 | **88** |
| Slot Battery real | 0 | 0 | 0 | 0 | **96** |
| Open Cup real | - | 0 | - | - | **84** |
| Thread Velcro real | - | 0 | - | - | **20** |
| Prep Tape real | - | 0 | - | - | **64** |
| Put On Shoe real | - | 0 | - | - | **92** |

因果解释：

- Baselines 在 early subtasks 有时能进展，但 final success 近乎全灭，说明 fine manipulation 的失败主要发生在长时序误差累积后段。
- ACT 在 Slot Battery/Slide Ziploc 上 96/88%，证明 action chunking + pixel feedback 足以处理毫米级插入/滑动。
- Thread Velcro 只有 20%，是重要负例：黑色 cable tie 小、低对比、只占图像很小区域，视觉定位失败使后段 grasp/insert 分别从 92% → 40% → 20%。这说明 ACT 不是魔法，感知瓶颈仍会压垮动作模型。

### 3.3 子任务级证据

| Task | ACT 子任务成功率 | 说明 |
|---|---|---|
| Slide Ziploc | Grasp 92, Pinch 96, Open 88 | 两臂分工稳定，最后拉开仍保持高成功率 |
| Slot Battery | Grasp 100, Place 100, Insert 96 | 插入阶段仍高，支持“action sequence helps precision” |
| Open Cup | Tip Over 100, Grasp 96, Open Lid 84 | 透明杯盖 + prying 接触仍可学 |
| Thread Velcro | Lift 92, Grasp 40, Insert 20 | 视觉局部化和 mid-air handover 是主要瓶颈 |
| Prep Tape | Grasp 96, Cut 92, Handover 72, Hang 64 | 多阶段 bimanual coordination 可行但误差逐段累积 |
| Put On Shoe | Lift 100, Insert 92, Support 92, Secure 92 | 复杂任务中后段保持强，说明 closed-loop chunking 有效 |

### 3.4 Action chunking ablation

Figure 8(a) 在 2 个模拟任务 × scripted/human data 共 4 个设置上平均成功率：

| chunk size | 含义 | 观察 |
|---:|---|---|
| $k=1$ | 无 action chunking，单步 BC | 成功率约 1% |
| $k=100$ | 默认最佳附近 | 成功率约 44% |
| $k=200,400$ | 接近更开环 | 略下降 |

因果链：

$$
k=1
\to
\text{每步独立预测}
\to
\text{covariate shift 快速累积}
\to
\text{后段失败}.
$$

$$
k=100
\to
\text{局部动作序列一致}
\to
\text{有效 horizon 降低}
\to
\text{精细接触动作更连贯}.
$$

$$
k\text{过大}
\to
\text{接近 open-loop}
\to
\text{无法响应偏差}
\to
\text{性能回落}.
$$

### 3.5 Temporal ensemble ablation

Figure 8(b) 显示 temporal ensemble：

| Method | TE 效果 | 解释 |
|---|---:|---|
| ACT | +3.3% | 平滑 Transformer 预测误差，减少 chunk 边界抖动 |
| BC-ConvMLP | +4% | parametric model 的预测噪声更受益 |
| VINN | -20% | VINN 检索 demonstration ground-truth actions，ensemble 反而混坏非参数动作 |

这说明 temporal ensemble 不是通用 smoothing trick。它主要帮助 parametric policies 平滑建模误差；对 retrieval-based 方法可能破坏本来正确的动作。

### 3.6 CVAE ablation

Figure 8(c) 对比有无 CVAE objective：

| 数据类型 | 去掉 CVAE 的影响 | 机制 |
|---|---|---|
| scripted data | 几乎无影响 | 示范确定性强，单一动作模式足够 |
| human data | 35.3% → 2% | 人类示范有多模态、暂停、handover 位置变化；无 latent bottleneck 时回归学到平均/混合轨迹 |

这证明 CVAE 的价值不是为了“生成酷炫多样性”，而是为了让模型在训练时解释人类数据的多种合理风格，从而别把它们平均成坏动作。

### 3.7 50Hz 是否必要

用户研究让 6 名参与者用 5Hz 或 50Hz teleoperation 做两项精细任务：

| Task | 5Hz | 50Hz | 变化 |
|---|---:|---:|---:|
| thread zip tie | 33s | 20s | 更快、更顺 |
| unstack cups | 16s | 10s | 更快、更顺 |

从 50Hz 降到 5Hz 总体导致 62% completion-time slowdown，统计检验 $p<0.001$。

这对 ACT 的故事很关键：论文不是说“低频 chunking 足够”。相反，低层控制和示范仍要高频；action chunking 是高频序列上的表示压缩，不是把机器人控制频率降到 5Hz。

## 4. 核心洞见

### 4.1 ACT 的真正 insight

ACT 不是简单地“预测多步动作”。它的 insight 是把高频动作序列分成两种时间尺度：

$$
\text{每帧重新感知}
\quad+\quad
\text{每次生成局部未来动作计划}
\quad+\quad
\text{同一时刻多计划加权融合}.
$$

这和 MPC 有相似外形，但 ACT 没有显式 dynamics model，也不在线优化；它把人类示范里的局部计划模式编译进一个前向网络。

### 4.2 为什么 ACT 比 BeT/RT-1 更适合 fine manipulation

| 维度 | BeT / RT-1 类 | ACT |
|---|---|---|
| action output | 单步、常离散化 | 连续 $k\times14$ joint targets |
| temporal structure | history-conditioned | future-sequence-conditioned |
| precision | 离散 bin/offset 对毫米级关节 target 不友好 | 直接连续回归 |
| compounding errors | 每步重新预测，后段易漂 | chunk 降低有效决策步数 |
| human multimodality | 历史窗口不一定解释示范风格 | CVAE latent 吸收 action style |

### 4.3 最需要保留的批判

ACT 缓解 covariate shift，但不从理论上消除它。只要 rollout 进入 demonstration 从未覆盖的状态，策略仍可能失败；Thread Velcro 正是例子。Action chunking 降低的是决策频率和局部不一致性，不是让 imitation learning 拥有 on-policy correction。

## 5. 替代方案与理论局限

### 5.1 理论维度

行为克隆的本质风险仍在：

$$
d^{\pi_\theta}(o)\ne d^{\mathrm{demo}}(o).
$$

ACT 通过 chunking 改变 action representation，但没有改变训练数据仍来自 demonstration distribution 的事实。它没有 DAgger 式专家纠正，也没有 RL fine-tuning。因此一旦物体进入未见状态，chunk 可能连续输出错误动作。

### 5.2 算法维度

| 局限 | 影响 |
|---|---|
| 推理时 $z=0$ | 多模态生成能力在部署时被压成确定性典型模式 |
| 单任务训练 | 每个任务从头训练约 80M 模型，没有验证跨任务泛化 |
| 纯 RGB + joints | 透明/低对比/小物体会成为瓶颈；无触觉/力反馈 |
| temporal ensemble buffer | 策略依赖过去预测，不是简单 Markov policy |
| action chunk fixed $k=100$ | 不同任务阶段最佳 chunk 长度可能不同 |

### 5.3 工程/硬件维度

ALOHA 的限制：

- 低成本 motor torque 不足，打不开紧瓶盖、重物、压紧 marker cap；
- parallel jaw gripper 不能完成需要多指的 child-proof bottle 等任务；
- 没有 fingernail，无法处理胶带边缘、汽水罐等需要薄边工具的动作；
- 摄像头 30fps、控制 50Hz，与动作预测高频之间存在感知/控制同步细节；
- 透明物体和低对比物体仍会失败。

## 6. 对用户研究的启发

### 6.1 对 PPO / WMTS 的可迁移点

Action chunking 可迁移，但要换成 RL 正确语义。若 PPO policy 输出 macro-action：

$$
\pi_\theta(A_t|s_t),\qquad
A_t=(a_t,\dots,a_{t+k-1}),
$$

并开环执行 $k$ 步，则 advantage 可写成 semi-MDP 形式：

$$
A_t=
\sum_{i=0}^{k-1}\gamma^i r_{t+i}
+
\gamma^k V(s_{t+k})
-
V(s_t).
$$

这是合理的 macro-action PPO。危险的是直接照搬 ACT temporal ensemble：若真实执行动作是多个过去 policy outputs 的加权平均，单个 timestep 的 logprob 不再对应一次清晰采样，PPO ratio 会失去简单解释。

### 6.2 对 WMTS task scheduler 的启发

ACT 给 WMTS 的不是“固定 $k=100$”，而是状态依赖 action horizon：

| 状态/phase | 建议 chunk |
|---|---|
| 开始接近、粗定位 | 长 chunk，减少抖动和探索维度 |
| 即将接触 | 短 chunk，高频闭环 |
| 稳定持续施力 | 中等 chunk，保证力/位移连贯 |
| 接触失败/触觉异常 | 立即打断 chunk，重新规划 |

这和 PFQI 的固定 $k$ 理论锚点互补：PFQI 告诉我们 $k$ 改变 MDP；ACT 告诉我们动作序列模型在真实精细操作中为什么有用。WMTS 的机会是把 $k$ 从固定超参升级为 world-model-conditioned scheduler output。

### 6.3 对 LinkerHand / 转笔的具体设计

对转笔，动作 chunk 不能太长。contact-rich dynamic manipulation 里，接触模式切换比 ziploc/battery 更快。建议实验：

| 实验 | 设计 |
|---|---|
| chunked PPO | 比较 $k=1,2,4,8,16$，开环执行 macro-action |
| tactile interrupt | 若触觉 slip/contact loss，提前终止 chunk |
| diffusion/action-chunk distillation | 用 PPO Oracle 数据训练 chunked diffusion/flow policy |
| no-TE vs TE deployment | IL 阶段可试 temporal ensemble；RL/PPO 阶段先不用 TE，避免 logprob 问题 |
| variable chunk scheduler | world model 预测不同 $k$ 下 success/uncertainty，选 LCB 最优 |

### 6.4 不应过度外推的点

- ALOHA 是 parallel jaw bimanual，不是多指灵巧手；动作结构差异巨大。
- ACT 的 50Hz 不是所有硬件都能达到；LinkerHand CAN/执行器延迟必须实测。
- ACT 用绝对 joint targets；灵巧手转笔可能更需要 torque/current/PD target 与触觉闭环。
- CVAE 推理 $z=0$ 对多模态动态任务可能过于保守；WMTS 可能需要保留多候选 rollout，而不是直接取均值。

## 7. 与知识体系的联系

### 7.1 与 [[ReinforcementLearning]] 的联系

ACT 是 BC 的结构化 action-space 改造，不是 RL。迁移到 PPO 时，关键是把 action chunk 当 macro-action / SMDP action，而不是把 temporal ensemble 直接塞进 on-policy update。它与 PFQI/action persistence 的共同点是都改变“多久重新决定一次动作”，但 ACT 通过 learned future sequence 表达局部计划，而 PFQI 只是重复同一 action。

### 7.2 与 [[RepresentationLearning]] 的联系

CVAE latent $z$ 是多模态 demonstration 的压缩变量。它在训练时解释“同一观测下不同人类轨迹”，在推理时被置零以获得确定性。这个设计适合稳定复现，但不适合需要在线多假设搜索的任务。

### 7.3 与 [[ControlTheory]] 的联系

ALOHA 的 joint-space mapping 是一个很强的控制工程判断：6-DoF 低成本臂 near singularity 时 IK 不稳，joint-space leader-follower 可以降低 latency 并保持高带宽。低层 Dynamixel PID 负责跟踪 target joint positions，ACT 学的是 target sequence，不是直接电机电流。

### 7.4 与 action-horizon / control-frequency 簇的联系

| 论文 | 时间结构 | 关键区别 |
|---|---|---|
| [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning|PFQI]] | 重复同一动作 $k$ 步 | 理论清晰，但动作内容不变 |
| ACT | 预测未来 $k$ 个不同动作 | 更适合精细操作，但理论保证弱 |
| [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]] | fast-slow latent reasoning | 在 representation 层做时间分解 |
| [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] | denoising action sequence + real RL | 将 chunked action sequence 接入 RL fine-tuning |

簇级 insight：动作时间结构有三档：repeat action、predict action chunk、reason over latent plan。WMTS 应把三者统一成状态依赖调度，而不是固定某一种。

## 8. 应主动追问的颗粒度

| 用户式追问 | recap 应主动补充 |
|---|---|
| “ACT 为什么能缓解误差累积？” | 写出 $\pi(a_{t:t+k}|o_t)$，说明有效 horizon 降低但 covariate shift 未消失 |
| “Temporal ensemble 是什么？” | 区分同一时刻多预测融合 vs 普通相邻动作 smoothing |
| “CVAE 有什么用？” | 用 scripted vs human ablation：human data 35.3% → 2% |
| “实验数字证明了什么？” | 主表 final success、chunking 1%→44%、TE +3.3%、50Hz vs 5Hz 62% slowdown |
| “怎么用于 PPO/WMTS？” | macro-action 可以，直接 TE 要小心 logprob；更好是 variable chunk scheduler |

## References

- Zhao, T. Z., Kumar, V., Levine, S., & Finn, C. **Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware**. RSS 2023.
- [[ReinforcementLearning]]
- [[RepresentationLearning]]
- [[ControlTheory]]
- [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]]
- [[RL-100 - Performant Robotic Manipulation with Real-World RL]]
- [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA]]
