---
tags:
  - paper
  - reinforcement-learning
  - vla
  - real-world-rl
  - post-training
  - WMTS
aliases:
  - pi-star-0.6
  - π*0.6
  - RECAP
  - A VLA that Learns from Experience
paper-year: 2025
read-date: 2026-03-25
venue: Physical Intelligence Blog
paper-pdf: "[[Papers/A VLA that Learns from Experience.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[Final_WMTS]]"
---

# π*0.6: A VLA that Learns from Experience (RECAP)

> [!abstract] 核心贡献
> Physical Intelligence 的 π*0.6 / RECAP 把 VLA post-training 从单纯 imitation learning 推到一个更像真实技能学习的三段式闭环：**demonstrations 定义任务策略骨架，corrections 覆盖 policy 自己制造的错误状态，autonomous experience + value/advantage 把长时间练习转化为可训练信号**。它的真正 value add 不是“又收集更多数据”，而是把 bad rollout 中哪些动作应该复制、哪些动作应该避免的问题变成 advantage-conditioned policy extraction，从而让真实机器人经验不再只是失败日志，而成为提高 throughput 和可靠性的训练数据。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — RECAP 的核心是 value function / advantage estimation / policy extraction，而不是传统 supervised fine-tuning。
> - [[EmbodiedAI]] — 它把 VLA 从静态预测模型推回 closed-loop embodied control，核心瓶颈是 covariate shift 与 compounding error。
> - [[RepresentationLearning]] — π0.6 的 VLA backbone 接收异构 prompt/conditioning；RECAP 把 desired advantage 也变成 prompt 条件。
> - [[Final_WMTS]] — 对 WMTS 最有用的是“经验数据如何被评价并回灌到 generalist policy”，不是 espresso/box/laundry 任务本身。
>
> **核心技术**: RL with Experience & Corrections via Advantage-conditioned Policies, human correction, autonomous rollout, value function, advantage-conditioned VLA, real-world VLA post-training

## 0. 阅读定位与文献类型

这不是一篇标准 peer-reviewed paper，而是 Physical Intelligence 发布的研究博客/技术报告。它的证据形式和学术论文不同：

- 有清晰方法叙事、系统框架、真实任务视频和 throughput/success graph。
- 没有完整算法伪代码、训练超参、数据规模细节、公开权重/代码、统计显著性、完整 ablation 表。
- 因此 recap 时必须把它当成**强系统信号 + 弱可复现证据**：适合用来提炼 VLA post-training 方向和工程靶点，不适合把每个数值当成可复现 benchmark。

它在当前知识库中的位置：

1. 和 [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]] 一起构成 **human correction / human-in-the-loop VLA post-training** 分支。
2. 和 [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]]、[[WMPO - World Model-based Policy Optimization for VLA|WMPO]] 一起构成 **IL 之后用 RL/WM 突破可靠性天花板** 的分支。
3. 和 WMTS 的关系更底层：WMTS 不一定要做 VLA，但必须回答同一个问题：**真实执行经验如何被 value/world model 评价，然后变成更好的低层 generalist 或 task scheduler？**

最低 takeaway：

| 维度 | RECAP 给出的答案 | 对 WMTS 的迁移 |
|---|---|---|
| 逻辑与价值 | imitation 只能“偶尔成功”，经验+纠正把 policy 推向“可靠且高吞吐” | PPO/DP Oracle 之后必须有真机 experience loop |
| 原理与理论 | value change / advantage 给每个 action 赋 credit | scheduler 可用 $\Delta V$ / WM regret / contact progress 给 task/action 打分 |
| 实验与验证 | espresso/laundry/box 的 throughput 与 success 明显提升 | 评估不能只看 success，要看 speed、recovery、长时不中断 |
| 未来与结合 | 缺少开源、精确 ablation、跨 embodiment 证据 | WMTS 应把 RECAP 变成可验证、可复现的小规模实验 |

## 1. 问题设定与动机

### 1.1 一句话核心

VLA 的瓶颈不是“不会动作”，而是**closed-loop 执行中一点小错会把机器人推到训练分布之外，随后错误滚雪球**；RECAP 的故事是让机器人用自己的失败和被纠正经验补齐这块分布。

### 1.2 它相对纯 IL / 纯 RL 的逻辑优势

纯 imitation learning 的优势是启动快：人类示范直接告诉模型“这个任务大概怎么做”。但它有一个 closed-loop 控制里绕不开的问题：

$$
o_t \sim d^{\pi_{\mathrm{demo}}}(o)
\quad \text{during training, but} \quad
o_t \sim d^{\pi_\theta}(o)
\quad \text{during deployment.}
$$

如果 $\pi_\theta$ 在某一步抓偏了、碰歪了、放慢了，后续 observation 就不再来自示范分布 $d^{\pi_{\mathrm{demo}}}$。这就是 covariate shift / compounding error。LLM 输出一句文本时没有持续改变外部世界，因此这个问题弱很多；机器人每个 action 都会改变下一个 state，错误有动力学后果。

纯 RL 的优势是能从任务结果中优化真实目标，但代价是：

- 真实机器人 rollout 昂贵、慢、有安全风险。
- sparse reward 下 credit assignment 困难。
- 大 VLA 模型直接 on-policy RL 不现实。

RECAP 的 value add 在于它不是在 IL 和 RL 之间二选一，而是把三种数据源分工：

| 数据源 | 解决什么问题 | 不解决什么问题 |
|---|---|---|
| Demonstrations | 给任务定义、基本策略和语言语义 grounding | 覆盖不了 policy 自己制造的错误状态 |
| Corrections | 人类在真实错误状态下给 recovery label | 成本高，覆盖不了细微速度/吞吐优化 |
| Autonomous experience | 大量覆盖真实 rollout 分布，优化 throughput/reliability | raw rollout 有坏动作，不能直接 behavior clone |

故事讲得好的地方：它用“学装盒子”这个人类学习隐喻把三段式讲清楚，但背后的技术逻辑是严肃的：**demonstration 是 behavior prior，correction 是 targeted DAgger，autonomous RL 是 value-based policy improvement**。

### 1.3 与相关路线的区别

| 路线 | 核心信号 | 优势 | RECAP 的区别 |
|---|---|---|---|
| Behavior cloning / SFT | 人类示范动作 | 简单稳定 | 无法从自己失败中学 |
| DAgger / HG-DAgger | expert 对 learner states 标注 | 处理 covariate shift | 主要依赖人类纠正，缺少 autonomous reward improvement |
| RL-100 | real-world RL / diffusion policy improvement | 可从在线经验提高 | 更偏 low-level policy，RECAP 是 VLA-level advantage conditioning |
| WMPO / model-based VLA | world model 内 policy optimization | 减少真实交互 | RECAP 直接用真机经验，不依赖 learned simulator |
| Beyond Human Demonstrations | RL 生成高质量 VLA 数据 | 训练数据可超过人类 | RECAP 更强调机器人自己部署后的 lifelong improvement |

## 2. 核心方法与理论

### 2.1 变量来源追踪

| 变量 | 空间/形状 | 来源阶段 | 固定/学习/观测/计算 | 意义 | 易错点 |
|---|---|---|---|---|---|
| $\pi_{0.6}$ | VLA policy | PI base model | learned | supervised/VLA pretrain 基座 | 不是最终策略 |
| $\pi^*_{0.6}$ | advantage-conditioned VLA | RECAP | learned | 用 offline RL + task SFT + on-robot experience 得到的策略 | 星号代表 post-training，不是 architecture 全新 |
| $D_{\mathrm{demo}}$ | trajectories | human teleoperation | observed dataset | 定义任务、提供初始 skill prior | 只覆盖 expert distribution |
| $D_{\mathrm{corr}}$ | recovery trajectories | human takeover | observed dataset | 对 learner-induced states 给出纠正 | 高质量但成本高 |
| $D_{\mathrm{auto}}$ | autonomous episodes | robot rollout | observed dataset | 覆盖真实 deployment state distribution | 混有失败，不能直接复制 |
| $r(\tau)$ | success / task outcome | episode-level reward label | observed/computed | 判断 episode 好坏 | sparse reward 下 credit assignment 难 |
| $V_\psi(s_t)$ | scalar value | trained value function | learned/computed | 预测当前状态距离成功/完成还有多好 | blog 中有“negative steps to completion”可视化 |
| $\Delta V_t$ | $V(s_{t+1})-V(s_t)$ | value prediction difference | computed | 局部 progress / action credit | 不是 ground-truth causality，只是估计 |
| $A_t$ | advantage / quality condition | value + reward estimate | computed condition | 告诉 VLA 当前 action 是好还是坏 | 条件变量，不等于动作本身 |
| $c$ | language + heterogeneous prompt + advantage | VLA input | observed/computed | 任务指令和 desired action quality | 推理时人为设成 high-advantage |

### 2.2 从零推导：为什么需要 advantage 而不只是 reward

机器人 episode 只有最终成败时，简单 reward 是：

$$
r_T =
\begin{cases}
1, & \text{task success}\\
0, & \text{task failure}
\end{cases}
$$

但一个 episode 可能长达几百步。若咖啡任务最后失败，错误可能发生在很早的 portafilter grasp，而不是最后插入动作。直接把整条失败轨迹都标成坏，太粗；直接 behavior clone 失败轨迹，又会复制错误。

所以需要 value function：

$$
V_\psi(s_t) \approx \mathbb{E}[\text{future success or remaining progress}\mid s_t].
$$

如果某个动作 $a_t$ 后状态更接近完成：

$$
\Delta V_t = V_\psi(s_{t+1}) - V_\psi(s_t) > 0,
$$

它就是一个局部好动作；如果 $\Delta V_t<0$，它可能让任务变差。更一般地，可写成 TD advantage：

$$
A_t = r_t + \gamma V_\psi(s_{t+1}) - V_\psi(s_t).
$$

RECAP 的关键不是“训练 value function”本身，而是下一步 policy extraction：把 $A_t$ 当成 VLA 的条件输入。

### 2.3 Advantage-conditioned policy extraction

普通行为克隆拟合：

$$
\max_\theta \sum_{(s_t,a_t)\in D} \log \pi_\theta(a_t\mid s_t, \ell),
$$

其中 $\ell$ 是语言指令。它会把 good action 和 bad action 都一起学进去。

RECAP 的思想可以抽象成：

$$
\max_\theta \sum_{(s_t,a_t,A_t)\in D}
\log \pi_\theta(a_t\mid s_t, \ell, A_t).
$$

训练时不丢弃 bad data，而是告诉模型：“这个动作是在 low-advantage 条件下发生的”。推理时，把条件设成 high-advantage：

$$
a_t \sim \pi_\theta(a_t\mid s_t,\ell,A=\text{high}).
$$

这有点像 Decision Transformer / return-conditioned policy 的机器人 VLA 版本，也像 advantage-weighted imitation 的条件化变体。但 RECAP 的好处是工程上可扩展：大模型仍然主要做 supervised-style next-action prediction，不需要对整个 VLA 做高方差 policy-gradient update。

### 2.4 Corrections 在理论里的位置

人类纠正不是普通 demonstration。它的状态分布来自 learner：

$$
s_t \sim d^{\pi_\theta},
$$

而不是 expert demo distribution。这一点让它接近 DAgger / [[HG-DAgger- Interactive Imitation Learning with Human Experts|HG-DAgger]]。

但 RECAP 比 DAgger 更宽：

- correction 解决明显错误和恢复策略；
- autonomous reward/value 解决细粒度速度、路径、等待、长 horizon credit；
- advantage conditioning 统一两类数据：correction 可以近似视为 high-advantage recovery sample，失败 rollout 可以作为 low-advantage negative context。

这里的 subtle point：correction 的价值不只是“更好动作”，而是**在模型自己会去到的坏状态上给出 recovery action**。对真实机器人，这比再多收集一批干净 expert demos 更有信息量。

### 2.5 信息流

```text
human demos
  -> VLA pretraining / SFT
  -> base π0.6

base/current policy rollout on robot
  -> autonomous episodes with success/failure reward
  -> value function V(s)
  -> advantage / progress annotation A_t

human takeover on learner mistakes
  -> correction trajectories
  -> high-quality recovery examples

all data + advantage labels
  -> advantage-conditioned VLA
  -> inference with high-advantage condition
  -> π*0.6
```

### 2.6 符号与概念陷阱

- **Advantage label 不是 reward label**：reward 是 episode/task outcome；advantage 是 step-level progress estimate。
- **Bad data 不是废数据**：bad rollout 在 RECAP 中提供 low-advantage contrast，帮助 policy 知道什么不该做。
- **Corrections 不是普通 demos**：它们来自 policy-induced error states，因此更像 targeted distribution repair。
- **π*0.6 不是单任务小 policy**：它仍是 VLA，只是加了 experience/correction/RL post-training。
- **Blog graph 不是完整 benchmark 表**：PDF 提供 throughput/success bar chart，但正文没有列出所有精确数值；结论应写成“graphically/qualitatively shown”，不要伪造数字。

## 3. 实验与验证

### 3.1 任务设置

RECAP 在三个真实应用上验证：

| 任务 | 难点 | 为什么不是普通 pick-place |
|---|---|---|
| Espresso drinks | 长 horizon、等待 grinder/machine、液体、清洁、多阶段语言高层策略 | 早期 grasp/insert 错误会延迟暴露；credit assignment 明显 |
| Folding laundry | deformable objects、50 个 novel items、新家庭环境 | 布料 dynamics 和形状多样性让 IL 分布覆盖很难 |
| Box assembly | 重复工业流程、flap folding、粘连/多拿盒子、真实包装 | 需要 throughput、edge-case recovery 和长时稳定 |

评估指标：

- throughput：每小时成功完成数。
- success rate：任务成功比例。
- uninterrupted operation：是否能长时间持续运行。

这几个指标比单次 success 更接近真实机器人部署要求。对 WMTS 也一样：转笔不能只看“偶尔转起来”，还要看连续周期数、掉笔恢复、速度、contact safety 和 long-run stability。

### 3.2 报告中的主要结果

正文给出的关键证据：

- RECAP 在 hardest tasks 上让 throughput 和 success rate 均显著提升；espresso making 中 throughput 和 success rate “more than double”。
- 最终 π*0.6 能：
  - 5:30am 到 11:30pm 制作 espresso drinks。
  - 在新家庭环境折叠 50 个 novel laundry items。
  - 在真实工厂组装/贴标 59 个包装盒。
- espresso task 最终模型可达到 over 90% success rate。
- graph 比较四个阶段：`π0.6 Pretrain`、`π*0.6 OfflineRL Pretrain`、`π*0.6 OfflineRL + SFT`、`π*0.6 Ours`。

这组证据支持的 causal story：

```text
IL-only base VLA
  -> can perform nominal behavior
  -> but fails under learner-induced distribution shift

offline RL pretrain
  -> improves base action quality / value-aware conditioning

task SFT
  -> specializes to each application

on-robot corrections + autonomous experience
  -> covers actual failure states and optimizes throughput
  -> final π*0.6 improves success and speed
```

### 3.3 Ablation 该如何读

报告不是完整 academic ablation，但阶段对比仍然很有价值：

| 对比 | 观察 | 因果解释 |
|---|---|---|
| π0.6 Pretrain vs π*0.6 OfflineRL Pretrain | base capability improved | offline RL/value-conditioned training给 VLA 更好的行为 prior |
| OfflineRL Pretrain vs OfflineRL + SFT | task-specific gains | demonstrations still define task-specific behavior and language grounding |
| OfflineRL + SFT vs Ours | 最大实际部署提升 | on-robot experience/corrections cover real failure states and improve credit assignment |

最关键的 missing ablation：

- corrections-only vs autonomous-RL-only 没有被清楚拆开。
- value function 质量/advantage binning 的敏感性没有公开。
- high-advantage inference condition 如何选择没有完整披露。

因此最严谨的结论不是“RECAP 每个组件都被严格证明”，而是：

> 真实 VLA 可靠性提升很可能来自 demo/correction/experience 三者组合；报告强烈支持这一路线，但还不足以分辨每个组件的独立贡献。

## 4. 核心洞见

### 4.1 最重要 insight：把 bad experience 变成有符号监督

很多机器人学习系统卡在一个悖论：

- 想让机器人从自己的经验学，就必须收集失败。
- 但如果直接行为克隆失败轨迹，就会学习失败。

RECAP 的 insight 是用 value/advantage 给 experience 上“正负号”。同一批 rollout 不再只是 demonstrations，而是：

```text
state, action, outcome
  -> value/progress estimate
  -> action quality condition
  -> policy learns conditional behavior manifold
```

这对 WMTS 很关键：WMTS 也会产生大量失败 task/action chunk。失败不是垃圾，只要能用 world model/value model 标注“失败在哪里、是否可恢复、是否值得 probe”，它就是 scheduler 和 generalist 的训练信号。

### 4.2 第二个 insight：correction 是高信息密度数据

普通 demo 往往只覆盖 clean path。Correction 覆盖的是当前 policy 的 failure manifold。对机器人来说，这比更多 clean demos 更贵但也更值钱。

对灵巧手/转笔，这意味着真机数据采集不应均匀采样：

- 不是“多采一些成功转笔 demo”；
- 而是找到策略最常失败的 contact phase、slip angle、motor lag condition；
- 让人/算法/安全 controller 给 recovery or reset trajectory；
- 把这些作为 high-value correction data。

### 4.3 第三个 insight：部署指标必须包含 throughput

Robotics paper 常只报 success rate，但 RECAP 强调 throughput。原因很现实：

- 一个 99% 成功但每次慢 5 分钟的系统，不一定可用。
- 一个 90% 成功但有 recovery、速度快、可长时运行的系统可能更有工业价值。

WMTS 也应该避免只优化 success。对转笔/灵巧手，应至少同时看：

- 成功周期数 / 连续不掉笔时间。
- 单周期速度与稳定性。
- recovery time。
- contact force / motor saturation。
- real-world reset cost。

## 5. 局限与批判

### 5.1 理论局限

Advantage-conditioned policy 依赖 value function。若 $V_\psi$ 不能区分“真正进步”和“偶然状态变化”，policy extraction 会被错误 credit 误导。

典型风险：

- sparse reward 让 value function 过度平滑；
- long-horizon espresso / folding task 中早期动作 credit 很难；
- deformable objects 和 liquids 的 hidden state 可能导致 $V(s)$ 不 Markov；
- value 提升不一定因当前 action 造成，可能来自外部时序或环境变化。

这正好提示 WMTS：如果用 $\Delta V$ 或 world-model regret 做 task scheduler，必须有 negative controls，例如打乱 action、保持 state 不变、或者对不可控噪声做 aleatoric/epistemic 分离。

### 5.2 实验局限

- 这是公司博客，不是 peer-reviewed benchmark。
- graphs 没有完整数字表和置信区间。
- 没公开数据规模、reward labeling 细节、value architecture、advantage discretization、safety intervention protocol。
- 任务是 PI 自家硬件/系统 pipeline，跨 embodiment 泛化未验证。
- “entire day / hours without interruption” 很强，但需要知道 reset、human monitoring、failure criteria、manual cleanup 的边界。

### 5.3 工程局限

RECAP 要成立，需要一个很强的真实机器人数据闭环：

- 能安全跑 autonomous rollout。
- 能自动或低成本 reset。
- 能实时检测 success/failure。
- 能让专家 intervention 不破坏数据记录。
- 能保存多模态 observation/action/reward/value 训练数据。

这对小实验室不是小成本。WMTS 若迁移，必须把 system scope 缩小：先做一个可自动 reset 的 micro-task，而不是一上来做完整长时灵巧操作。

## 6. 对 WMTS / 灵巧手 / VLA-RL 的具体启发

### 6.1 WMTS 可直接借用的三段式

把 RECAP 映射到 WMTS：

| RECAP | WMTS 对应物 |
|---|---|
| Demonstrations | PPO Oracle / Diffusion Policy demos / scripted safe primitives |
| Corrections | 真机失败后的 human/safety-controller recovery，或 WM 标注的 high-value correction |
| Autonomous experience | LinkerHand 真机 rollout / sim-to-real rollouts |
| Value function | ensemble world model + task value + tactile progress estimator |
| Advantage condition | task/action chunk quality tag；可作为 DP/Flow generalist 的 condition |

一个可执行实验：

1. 选一个最小转笔子任务，例如“稳定夹持后推进半周期”。
2. 用 sim PPO/DP 生成 base policy。
3. 真机跑 100-300 条短 rollout，记录 tactile/contact/proprioception。
4. 训练 $V_\psi$ 预测短 horizon progress：角速度、相位进度、是否打滑、是否接近掉笔。
5. 给每个 action chunk 标注 $A_t$。
6. 训练 advantage-conditioned Diffusion Policy：

$$
\pi_\theta(a_{t:t+H}\mid o_t, g, A=\text{high}).
$$

7. 对比普通 BC / DP、只加 corrections、加 advantage-conditioned experience 三组。

### 6.2 与 WMTS scheduler 的关系

RECAP 用 advantage 区分 action 好坏；WMTS 可以把这个思想升到 task level：

$$
\mathrm{score}(g)
= \mathbb{E}[\Delta V \mid g]
- \lambda \cdot \mathrm{risk}(g)
+ \beta \cdot \mathrm{epistemic}(g).
$$

这与 Part A 里已经形成的 Solve/Probe/Reject 三读法统一：

- high $\Delta V$, low risk：Solve。
- high epistemic, bounded risk：Probe。
- low value / high risk：Reject。

RECAP 提醒我们：scheduler 不只是“选任务”，还要把 experience 标成可学习数据。否则任务生成和策略训练是断开的。

### 6.3 与 VLA post-training 子簇的定位

| 论文 | 核心 post-training 信号 | 对 RECAP 的互补 |
|---|---|---|
| [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]] | human-in-the-loop dexterous correction | 更聚焦灵巧操作与人类介入流程 |
| [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] | offline/online RL for manipulation | 更接近 low-level real-world RL |
| [[WMPO - World Model-based Policy Optimization for VLA|WMPO]] | world model policy optimization | 用 WM 降低真实 rollout 成本 |
| [[WoG - World Guidance for VLA Action Generation|WoG]] | world guidance during action generation | 更像 inference-time correction |
| RECAP | advantage-conditioned VLA from real experience | 直接把真实 rollout 变成 VLA training signal |

### 6.4 不应照搬的点

RECAP 是大公司 VLA system paper。对 WMTS 不应直接照搬：

- 不要默认有足够机器人数量跑 long autonomous rollouts。
- 不要默认 value function 从视频/语言里能学出 contact credit。
- 不要把 high-advantage conditioning 当作 magic；它只是把 value 的判断交给 policy 执行。
- 不要忽视 reset、安全和硬件磨损。

更现实的落点是：做一个“小而硬”的 RECAP-style loop，在 LinkerHand 上验证**experience annotation**是否真的能提升一个特定 contact-rich skill。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系

RECAP 是 offline/online RL 思想在 VLA 上的工程化版本。它没有把 VLA 直接变成 policy-gradient learner，而是把 RL 信号压缩成 value/advantage labels，再用 supervised-style conditional modeling 吸收。这很适合大模型 post-training。

### 与 [[EmbodiedAI]] 的联系

它清楚说明 embodied model 与 LLM 的差别：机器人会改变自己的下一步输入分布。因此 real-world embodied intelligence 不能只靠 demonstration pretraining，必须有 deployment-time experience loop。

### 与 [[RepresentationLearning]] 的联系

Advantage condition 是一种 representation choice：把“行为质量”显式变成模型输入，而不是希望 transformer 在混合数据里自己分离好坏动作。这个思想可以推广到 tactile progress、contact phase、safety margin 等条件变量。

### 与 [[Final_WMTS]] 的联系

RECAP 支持 WMTS 的一个核心判断：**数据飞轮的关键不是多，而是每条经验是否被正确解释**。WMTS 的 world model/task scheduler 若能把 rollout 标成 Solve/Probe/Reject、high/low advantage、recoverable/unrecoverable，它就不只是生成任务，而是在生成可训练知识。

## References

- 原始 PDF：[[Papers/A VLA that Learns from Experience.pdf]]
- 相关：[[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation]]
- 相关：[[RL-100 - Performant Robotic Manipulation with Real-World RL]]
- 相关：[[WMPO - World Model-based Policy Optimization for VLA]]
- 相关：[[WoG - World Guidance for VLA Action Generation]]
- 项目入口：[[Final_WMTS]]
