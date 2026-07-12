---
tags:
  - paper
  - manipulation
  - vla
  - human-in-the-loop
  - dexterous-manipulation
  - post-training
  - WMTS
aliases:
  - DexHiL
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/DexHiL- A Human-in-the-Loop Framework for Vision-Language-Action Model Post-Training in Dexterous Manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[Final_WMTS]]"
---

# DexHiL: A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation

> [!abstract] 核心贡献
> DexHiL 是一个面向灵巧操作 VLA 的 arm-hand integrated human-in-the-loop post-training 框架。它不是简单地“多收一些遥操作数据”，而是把**人类介入发生在哪里**作为训练信号：通过 intervention-aware weighting 把稀疏但高信息密度的纠正片段放大，使 VLA 在高 DOF、接触密集、易 covariate-shift 的灵巧手任务中快速学到 recovery behavior。真实 Franka + DexHand021 实验中，DexHiL 在 tissue extraction 达到 19/20，在 plush toy grasping 达到 13/20，较 data-matched offline baseline 平均提升约 25% success rate。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — DexHiL 是 DAgger / intervention learning 在 dexterous VLA post-training 上的工程化扩展，但严格说它仍是 weighted imitation，不是 autonomous RL。
> - [[EmbodiedAI]] — 它把 VLA 的后训练放回真实 robot-in-the-loop 分布，解决纯 offline SFT 无法覆盖 learner-induced failure states 的问题。
> - [[ControlTheory]] — arm-hand teleoperation、ArUco pose mapping、hand retargeting 质量直接决定 human correction 是否可用。
> - [[Final_WMTS]] — 对 WMTS 最关键的是“纠正片段比成功片段信息密度高”，这能指导真机少量数据采集策略。
>
> **核心技术**: human-in-the-loop VLA post-training, intervention-aware weighting, dexterous teleoperation, modular hand retargeting, weighted Flow Matching, data filtering

> [!note] 簇内坐标与暗线（模仿学习 · 数据生成 · 真机 RL · 人机协作）
> **簇内互链（Delta）**
> - vs [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning|HIL-SERL]]：都用人类纠正，但 HIL-SERL 把纠正**入 off-policy RL**（Q 决定利用、可超人类），DexHiL 是 category-reweighted **imitation**（$P^*(\text{itv})=0.5$，非 autonomous RL），且专攻高 DOF 灵巧手 VLA。
> - vs [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]]：都 VLA 后训练；DexHiL 用**加权模仿**放大人类纠正，RLT 冻结 VLA 学 **RL 残差 token**。
> - vs [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action|Privileged Action]]：都定向解决"失败边界/长因果链"探索稀薄；DexHiL 用**人类介入**采样失败边界，Privileged Action 用**仿真特权动作**改变探索拓扑。
>
> **Foundation 精确锚点**（已 grep 验证）
> - [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|RL §7.4]] — DexHiL = DAgger/HG-DAgger 的 dexterous VLA 工程化；intervention-aware weighting ≈ §7.4 权重表的 **category 版**加权 BC。
> - [[EmbodiedAI#2.3 VLA 后训练：从模仿到强化|EmbodiedAI §2.3]] — 把 VLA 后训练放回 robot-in-the-loop 分布，解决纯 offline SFT 覆盖不到 learner-induced OOD 的问题。
>
> **暗线**：**模仿×强化缝合线**上 DexHiL 偏"weighted imitation"端（介于 BC 与 autonomous RL）；human intervention = **failure-boundary sampling**（prioritized，belief 能力边界的采样）。

## 0. 阅读定位与范本价值

DexHiL 应该和 [[RECAP - A VLA that Learns from Experience|RECAP]] 放在一起读，但二者的角色不同：

| 论文 | 核心数据源 | 改进机制 | 最适合回答的问题 |
|---|---|---|---|
| RECAP / π*0.6 | demonstrations + corrections + autonomous experience | value/advantage-conditioned policy | VLA 如何从自己的长期经验中提高 throughput/reliability |
| DexHiL | offline demos + online human interventions | intervention-aware weighted imitation | 灵巧手 VLA 如何用少量人类纠正突破 offline SFT plateau |

DexHiL 的价值不是提出新的 RL 理论，而是把一个现实问题做实：**灵巧手高维接触任务里，失败状态非常具体，靠 offline 成功演示堆数据很慢；人类只在即将失败时介入，得到的是高密度的 OOD recovery data。**

对当前知识库，它补齐了一个重要节点：

- DeXtreme / Rubik's Cube 说明大规模 sim RL + DR 可以获得 dexterity。
- RECAP / RL-100 说明真实经验可以突破 imitation 天花板。
- DexHiL 说明在 dexterous VLA 上，**human correction 的采集接口和加权方式本身就是核心算法部件**。

## 1. 问题设定与动机

### 1.1 一句话核心

Dexterous VLA post-training 失败的主要原因不是 VLA “不知道语言指令”，而是**高 DOF 手部动作 + 接触 discontinuity + learner-induced OOD states** 让 offline SFT 很快到平台期；DexHiL 用在线人类介入把这些失败状态变成训练样本。

### 1.2 为什么 dexterous VLA 比普通 arm VLA 更难

普通 VLA post-training 多数处理低维末端动作或 gripper open/close。DexHiL 面对的是 arm + dexterous hand：

- Franka arm：7-DOF，主要负责全局位姿。
- DexHand021：高维手部关节，负责接触、包覆、pinch、lift。
- contact-rich task：tissue edge、plush toy deformation 都依赖微小手指误差。

因此 error distribution 变得很尖锐：

```text
slightly bad wrist pose
  -> fingertip contact missed
  -> object/tissue deforms or slips
  -> next observation far from offline demos
  -> VLA action becomes less meaningful
```

这就是 DexHiL 把 “human takes over near failure” 当作主数据源的原因。不是所有数据等价；**失败边缘的数据更值钱**。

### 1.3 相对 DAgger / Offline SFT / RECAP 的 delta

| 方法 | 采样分布 | 是否区分 intervention | 是否适配 dexterous hand | 局限 |
|---|---|---|---|---|
| Offline SFT | expert demos | 否 | 可以，但数据需求大 | 不覆盖 learner-induced OOD |
| DAgger | learner states + expert labels | 弱 | 多用于低维 arm/gripper | 所有聚合数据常被均匀训练 |
| HG-DAgger | human-gated takeover | 有安全意义 | 原论文不是 dexterous VLA | 无高维手部 teleop / VLA FM action head |
| RECAP | corrections + autonomous experience | advantage-conditioned | VLA 但非 dexterous focus | 依赖 value/advantage，系统细节不公开 |
| **DexHiL** | dexterous learner rollout + human intervention | **显式 reweight** | **是** | 仍依赖人类介入，非 autonomous RL |

它讲故事的方式很直接：

1. **先说 offline SFT 不够**：因为重复成功数据主导梯度。
2. **再说 human correction 有用但稀疏**：需要被训练机制看见。
3. **最后用 intervention-aware weighting 连接二者**：让少量 correction 在 loss 里占到目标比例。

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 空间/形状 | 来源阶段 | 固定/学习/观测/计算 | 含义 | 易错点 |
|---|---|---|---|---|---|
| $o_t$ | multimodal observation | RealSense + proprioception + instruction | observed | VLA 输入 | 是否包含足够手部/物体接触信息决定恢复能力 |
| $q_{\mathrm{arm},t}$ | arm joints | Franka / IK | observed/computed | arm command/state | arm intervention 与 hand intervention 必须同步 |
| $q_{\mathrm{hand},t}$ | hand joint angles | Manus glove retargeting | observed/computed | dexterous hand command | retargeting 误差会污染 correction label |
| $I_t$ | $\{0,1\}$ | online rollout annotation | observed | intervention indicator | 不是 reward；是数据来源/重要性标签 |
| $\pi(o_t)$ | robot policy command | Being-H0.5 VLA | learned | autonomous action | cold-start action head 需要 warm-up |
| $u_{\mathrm{human}}$ | teleop command | human intervention | observed | correction action | 高信息密度，但质量受 teleop interface 限制 |
| $c$ | category label | intervention / non-intervention | observed | sample category | 用于 importance weight |
| $P(c)$ | empirical category frequency | aggregated dataset | computed | 当前数据中 intervention 占比 | intervention 通常很少 |
| $P^*(c)$ | target category frequency | design choice | fixed | 训练希望看到的类别比例 | 文中设 $P^*(\mathrm{intervention})=0.5$ |
| $w(o,a,c)$ | scalar | importance weighting | computed | loss 权重 | 不是质量评分，只是类别重平衡 |
| $v_\theta$ | Flow Matching velocity field | VLA action head | learned | 从噪声到 action 的速度场 | 训练是 weighted imitation，不是 RL |

### 2.2 Teleoperation / retargeting：为什么硬件接口是算法的一部分

DexHiL 把 teleoperation 分成 arm 和 hand 两条路径。

**Arm pose mapping** 使用 ArUco cube 的 6D pose。人类按键触发 intervention 时，记录当前 robot EE pose $T_{EE0}$ 和 cube pose $T_{M0}$，之后用 cube 的相对位姿驱动 robot end-effector：

$$
T_{EE}
= T_{EE0}(T^{\mathrm{cube}}_{\mathrm{robot}})^{-1}
T_{M0}^{-1}T_M T^{\mathrm{cube}}_{\mathrm{robot}}.
$$

再经 IK：

$$
q_{\mathrm{arm}} = K^{-1}(T_{EE}).
$$

**Hand retargeting** 用 Manus glove 的 human keypoints，经学习映射到 robot actuated joints。论文强调单一五指网络会退化成 pinch-like posture，因此采用 two-stage：

1. 先训练四个非拇指的 mapping，保留 enveloping grasp manifold。
2. 冻结非拇指后，单独训练 thumb residual，并加入 direction / coverage / flatness / pinch / inter-fingertip kinematic losses。

这个细节很重要。DexHiL 的 human correction 是否高质量，首先取决于人类能不能实时、准确地把“我想怎么抓/捏/提”映射到 robot hand。对 WMTS/LinkerHand，这意味着不能只讨论 policy loss；**human correction pipeline 本身就是数据质量瓶颈**。

### 2.3 Human-in-the-loop control law

在线 rollout 中，每个时刻的控制由 intervention indicator 决定：

$$
u_t =
\begin{cases}
\pi(o_t), & I_t=0 \quad \text{Autonomous}\\
u_{\mathrm{human}}, & I_t=1 \quad \text{Intervention}
\end{cases}
$$

聚合数据：

$$
D=\{(o_t,q_{\mathrm{arm},t},q_{\mathrm{hand},t},I_t)\}_{t=1}^{T}.
$$

这个 formulation 把 DexHiL 和普通 offline SFT 区分开：dataset 不只是 $(o,a)$，还包含“这段 action 是否来自人类救场”的结构信息。

### 2.4 Intervention-aware weighting

设聚合数据中类别 $c$ 的经验分布为：

$$
P(c)=\frac{n_c}{N}.
$$

DexHiL 指定一个目标分布 $P^*(c)$，尤其设：

$$
P^*(\mathrm{intervention})=0.5.
$$

样本权重：

$$
w(o,a,c)=\frac{P^*(c)}{P(c)}.
$$

如果 intervention 很少，比如 $P(\mathrm{intervention})=0.1$，则 intervention 样本被乘以 $0.5/0.1=5$。这不是在说每个 intervention 都完美，而是在说：

> 在 high-DOF dexterous post-training 中，少量 correction 代表 policy failure boundary，不能被海量正常/重复数据淹没。

### 2.5 Weighted Flow Matching objective

DexHiL 以 Being-H0.5 作为 VLA backbone，其 action head 是 Flow Matching。单样本 imitation loss：

$$
\ell_{\mathrm{IL}}(\theta;o,a)
=
\mathbb{E}_{t,x_t}
\left\|
v_\theta(x_t,t,o)-u_t(a\mid x_0)
\right\|_2^2,
$$

其中：

$$
x_t=(1-t)x_0+ta,\qquad
u_t(a\mid x_0)=a-x_0.
$$

加入 intervention-aware weight 后：

$$
L^{(i)}(\theta;D_i)
=
\mathbb{E}_{(o,a,c)\sim D_i}
\left[
w(o,a,c)\ell_{\mathrm{IL}}(\theta;o,a)
\right].
$$

参数更新：

$$
\theta^{(i)}
\leftarrow
\theta^{(i-1)}
-
\eta\nabla_\theta L^{(i)}(\theta;D_i).
$$

注意：这里没有 value function、advantage、reward、policy gradient。DexHiL 是 **weighted supervised post-training**，其“RL-like”部分来自 online interaction distribution，而非 RL objective。

### 2.6 Data filtering：为什么只保留最后一次介入到完成

论文只保留 “final intervention → task completion” 片段，丢弃最后一次介入之前的轨迹。原因：

- 多次 intervention 的整条轨迹可能包含互相矛盾的 partial corrections。
- intervention 前的 policy action 本来就是 suboptimal。
- 全部拿来训练会造成 policy oscillation 或 multimodal distribution conflict。

因果链：

```text
multiple takeovers in one trial
  -> pre-takeover actions include failed attempts
  -> uniform training sees mixed wrong/recovery behavior
  -> action distribution becomes incoherent
  -> only final recovery segment gives clean "from bad state to success" supervision
```

## 3. 实验与验证

### 3.1 实验设置

平台：

- Franka Research 3 arm。
- DexHand021 dexterous hand。
- Manus glove。
- RealSense D455/D435 cameras。
- ArUco marker for arm teleoperation。
- Being-H0.5 VLA backbone。

训练：

- warm-up：60 offline trajectories 初始化。
- online rounds：每轮每个任务增加 10 trajectories。
- training：8×H100 full training，online human-interaction data fine-tuning 用单 H100。
- policy inference：20 Hz；human-guided arm/hand teleoperation：30 Hz / 90 Hz。

任务：

| 任务 | 成功标准 | 难点 |
|---|---|---|
| Tissue Extraction | 抽出超过半张纸巾长度 | 薄片 deformable，需精确 fingertip alignment / pinch / vertical retraction |
| Plush Toy Grasping | 物体完全离开桌面 | deformable object，需要 arm-hand coordination 和 enveloping grasp |

Baselines：

- Offline-40/50/60：相同数据量，但只加 offline trajectories。
- DAgger*：online training without intervention-aware mechanism。
- DexHiL：online intervention + weighting + filtering。

### 3.2 关键结果

| 方法 | Tissue Warm-up | Tissue R1 | Tissue R2 | Tissue R3 | Plush Warm-up | Plush R1 | Plush R2 | Plush R3 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| DexHiL | 2/20 | 10/20 | 15/20 | **19/20** | 0/20 | 4/20 | 6/20 | **13/20** |
| DAgger* | 2/20 | 7/20 | 9/20 | 16/20 | 0/20 | 2/20 | 3/20 | 4/20 |
| Offline baseline | 2/20 | 8/20 | 11/20 | 15/20 | 0/20 | 0/20 | 3/20 | 7/20 |

直接读数：

- Tissue Extraction：DexHiL 最终 95%，比 offline baseline 75%、DAgger* 80% 更高。
- Plush Toy：DexHiL 最终 65%，显著高于 offline baseline 35%、DAgger* 20%。
- 人力效率：intervention segment 约 3s，offline trajectory 约 10s；Round 3 总人力 13 min vs 20 min，减少约 35%。
- 论文报告两任务相对 offline-only finetuning 平均 success rate 提升约 25%。

### 3.3 实验如何印证故事

**Story claim**：intervention samples 是高信息密度 recovery data，必须被优先训练。

证据链：

```text
Warm-up 几乎失败
  -> VLA base 对 dexterous task 不够

Offline baseline 随数据增加缓慢提高
  -> 说明更多普通数据有用但效率有限

DAgger* 在 tissue 有提高但 plush 很差
  -> learner-state data 有用，但如果不重权 correction，复杂 coordination task 下仍被稀释

DexHiL 在 plush 从 0/20 到 13/20
  -> intervention-aware weighting 对最难任务更关键
```

为什么 Plush Toy 更有信息量：它比 tissue 更依赖 arm-hand timing 和包覆抓取，普通 offline 成功数据很难覆盖 policy 出错后的细粒度 recovery。DexHiL 在这个任务上相对 DAgger* 的提升最大，说明“纠正片段被放大”不是装饰模块。

### 3.4 Loss spike 的正确解释

论文提到每轮加入 human corrections 后，training loss 初始出现 spike。这个现象不应被简单看作训练不稳定。更合理解释：

```text
human correction adds OOD recovery states
  -> current policy/value head 尚不能拟合
  -> loss spike
  -> weighted optimization focuses on these states
  -> policy gains recovery capability
```

这和 [[RECAP - A VLA that Learns from Experience|RECAP]] 的核心一致：最有价值的数据往往不是低 loss 的重复成功样本，而是当前模型不懂的失败边界。

## 4. 核心洞见

### 4.1 最重要 insight：human intervention 是 failure-boundary sampling

DexHiL 的干预不是普通人工示范，而是一个 sampling strategy：

$$
s_t \sim d^{\pi_\theta}
\quad \text{and human intervenes near failure.}
$$

这意味着 intervention data 自动聚焦在 policy 的能力边界。相比随机加 demo，它更像 prioritized replay：

- replay prioritizes TD error；
- DexHiL prioritizes human-observed failure boundary；
- WMTS 可以 prioritizes world-model uncertainty / risk / value drop。

### 4.2 第二个 insight：加权比“只聚合”更关键

DAgger 的直觉是把 expert correction 加进 dataset。但在大数据/大模型 setting，聚合不等于有效学习。若 correction 只占 5%，uniform loss 中它仍可能被 95% normal data 淹没。

DexHiL 的 $P^*(\mathrm{intervention})=0.5$ 是很粗暴但有效的做法：不试图精确估计每个 sample 的质量，而是先承认 intervention 类别整体更稀缺、更重要。

### 4.3 第三个 insight：teleoperation interface 决定 algorithm ceiling

如果 human operator 无法精确控制 robot hand，intervention data 就不是“专家纠正”，而是 noisy label。DexHiL 花很多篇幅在 retargeting 上，说明在 dexterous task 中，数据采集硬件不是 appendix，而是方法本体。

对 LinkerHand / 灵巧手转笔，这点尤其关键：

- glove-to-hand retargeting 可能不足以表达高速 finger gait；
- tactile/contact feedback 不回传给 human 时，correction 质量有限；
- 一味 human-in-loop 不会自然解决 contact sensing 缺口。

## 5. 局限与批判

### 5.1 理论局限

DexHiL 的 weighting 是 category-level importance sampling：

$$
w(c)=P^*(c)/P(c).
$$

这不区分 intervention 的质量：

- 有些 intervention 是精准 recovery；
- 有些 intervention 只是粗糙 reset；
- 有些 intervention 可能来自 human delay 或错误判断。

因此 $P^*=0.5$ 是经验工程选择，不是最优理论。更强版本应结合：

- task progress change；
- intervention duration；
- post-intervention success probability；
- model uncertainty；
- tactile/contact discontinuity。

### 5.2 算法局限

DexHiL 没有 autonomous RL / value learning。它解决的是 “让人类纠正更有效”，不是 “机器人自己从大量成功失败中提炼 reward signal”。因此它和 RECAP 的关系是互补而非替代：

| 维度 | DexHiL | RECAP |
|---|---|---|
| human correction | 强 | 有 |
| autonomous practice | 弱 | 强 |
| value/advantage | 无 | 核心 |
| dexterous hardware | 强 | 弱/未聚焦 |
| scalable self-improvement | 未充分证明 | 主要卖点 |

对 WMTS，理想路线是二者合并：先用 DexHiL-style intervention 定向修复危险/失败边界，再用 RECAP-style advantage/world-model labels 扩大自主经验利用率。

### 5.3 实验局限

- 只验证两个任务，且都相对短 horizon。
- 每个任务 20 trials，统计规模不大。
- 使用 Being-H0.5 和特定硬件，跨 robot hand / embodiment 泛化未知。
- 没有完整比较不同 $P^*$、intervention quality、filtering window 的 sensitivity。
- Plush Toy 最终 65% 仍未达到可靠部署级，说明 dexterous VLA 后训练仍远未解决。

### 5.4 工程局限

- 需要人类实时监督，无法完全 autonomous。
- 需要可用的 hand retargeting interface。
- 需要多线程控制避免 takeover delay。
- 对高速任务（转笔）而言，人类介入时延可能比失败发生还慢；此时 DexHiL 只能用于慢速 recovery 或 phase-specific coaching，而不是全程安全保障。

## 6. 对 WMTS / 灵巧手 / 转笔的具体启发

### 6.1 用 intervention 作为 task scheduler 的监督信号

WMTS 的 scheduler 可以把 human intervention 视作能力边界标签：

$$
\mathrm{risk}(s_t,a_t) \uparrow
\quad \text{if human intervenes near } (s_t,a_t).
$$

这可以产生三类训练数据：

| 数据类型 | DexHiL 解释 | WMTS 用法 |
|---|---|---|
| autonomous success | 当前 policy 能处理 | Solve data |
| human intervention + recovery | 当前 policy 边界 | high-priority correction / Probe data |
| repeated failure before intervention | 当前 policy 不应执行 | Reject / safety filter data |

### 6.2 转笔中可做的最小实验

不要一开始做完整 pen spinning。可以做一个 DexHiL-style micro-loop：

1. 选择一个失败高发 phase：例如拇指-食指交接、笔即将滑出、接触从指腹到指尖切换。
2. 让 base policy 自主运行到接近失败。
3. 人类/安全 controller 触发 intervention：
   - 降速；
   - 重夹持；
   - 回到 safe grasp；
   - 或完成一个短 recovery arc。
4. 标注 intervention segment。
5. 用 $P^*(\mathrm{intervention})$ 或更细的 risk/progress 权重训练 low-level generalist。

关键对照：

- uniform DAgger aggregation；
- DexHiL-style category weighting；
- RECAP-style advantage weighting；
- WMTS-style ensemble risk + progress weighting。

### 6.3 与 LinkerHand 的硬件提醒

DexHiL 用 DexHand021 + Manus glove；你的 LinkerHand L25 有不同 actuator dynamics、CAN latency、tactile arrays。迁移时需要重新回答：

- 人类手套/视觉手势能否映射到 LinkerHand 的真实可达 finger gait？
- tactile feedback 是否应作为 intervention trigger？
- human intervention 的延迟是否低于 contact failure 的时间尺度？
- 介入数据是否应包含 motor temperature/current/latency 作为 context？

这和 Part A 的 [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] / Hwangbo actuator-net / SSRL 线能接起来：DexHiL 处理 high-level correction；WMTS 还必须处理 low-level actuator/contact mismatch。

## 7. 与知识体系的联系

### 与 [[RECAP - A VLA that Learns from Experience]] 的联系

两者共同证明：VLA post-training 的关键不是“再做 SFT”，而是把部署经验结构化。

- RECAP：部署经验通过 value/advantage 被解释。
- DexHiL：部署失败通过 human intervention category 被解释。

这两条线合起来给出一个更完整的数据飞轮：

```text
offline demos
  -> base policy
  -> autonomous rollout
  -> human intervention for dangerous/obvious failures
  -> value/world-model labels for subtle progress/failure
  -> weighted/conditioned post-training
```

### 与 [[HG-DAgger- Interactive Imitation Learning with Human Experts]] 的联系

HG-DAgger 的核心是 human-gated takeover，避免让 human 在 shared-control lag 下提供低质量 labels。DexHiL 把这个思想搬到 dexterous arm-hand VLA，并补上 hand retargeting + Flow Matching + intervention weighting。

### 与 [[ReinforcementLearning]] 的联系

DexHiL 的 intervention-aware weighting 很像 prioritized replay / importance sampling，但它没有 TD error，而是用 human takeover category 作为粗粒度 priority。它是一个介于 imitation learning 和 RL 之间的工程折中。

### 与 [[Final_WMTS]] 的联系

DexHiL 支持 WMTS 的一个具体设计原则：

> 真机数据采集不应均匀；应围绕 policy 的失败边界、world-model 的不确定边界、以及 human/safety controller 的介入边界采样。

## References

- 原始 PDF：[[Papers/DexHiL- A Human-in-the-Loop Framework for Vision-Language-Action Model Post-Training in Dexterous Manipulation.pdf]]
- 相关：[[RECAP - A VLA that Learns from Experience]]
- 相关：[[HG-DAgger- Interactive Imitation Learning with Human Experts]]
- 相关：[[RL-100 - Performant Robotic Manipulation with Real-World RL]]
- 相关：[[WMPO - World Model-based Policy Optimization for VLA]]
- 项目入口：[[Final_WMTS]]
