---
tags:
  - WMTS
  - cross-paper-synthesis
  - insight-network
  - critical-thinking
aliases:
  - 跨论文 Insight 综合
  - Cross-Paper Insights
  - WM-core 论证线
created: 2026-06-16
related:
  - "[[Final_WMTS]]"
  - "[[_UpgradeProgress]]"
  - "[[_RelatedPapersIndex]]"
  - "[[Rationale-Planner-Follower-Task-Definition]]"
---

# 跨论文 Insight 综合：WMTS 设计决策的论证网络

> [!abstract] 这份文档解决什么
> 48 篇 RelatedPapersRecap 各自在 §0/§5/§6 里做了跨论文分析，但**整张论证网络散落各处，无人能一眼看全**。本文把它们装配成**以 WMTS 设计决策为节点的论证网络**：每条线 = 一个设计选择 + 支持它的 recap 群（各自贡献的精确主张）+ 反面/边界 recap + 残留张力。这是从"读懂每篇"到"看清每个决策为何这样定"的升维。
>
> **读法**：每条线先给 **WMTS 决策**（一句话结论），再给**支持证据**（哪篇 recap 贡献了哪个精确论点）、**反面/边界**（哪篇划出了不适用区）、**开放问题**。所有论点均可回溯到对应 recap 正文。

> [!tip] 与索引的分工
> - [[_RelatedPapersIndex]]：按主题**列举**论文（查"有哪些"）。
> - [[_UpgradeProgress]]：recap 升级**进度**（查"写到位没"）。
> - **本文**：跨论文**论证**（查"为什么 WMTS 这样设计、哪些论文支持/反对"）。

---

## 线 1 — Ensemble + 显式 LCB：WM 可靠性的演化主线

> [!success] WMTS 决策
> WM 必须 **ensemble + 显式 LCB（下置信界）**，把保守度放到**非参数规划/排序的测试期**、用 ensemble 不确定性**自适应**调节，而非训练时硬塞保守。Eq 4 式 $\hat R=\sum_t\gamma^t(R-\lambda u_t)$ 就是 WMTS reliability head 的实现。

| recap | 在演化链中的位置 | 精确贡献 |
|---|---|---|
| [[Deep Dynamics Models for Learning Dexterous Manipulation\|PDDM]] (2019) | 奠基 | ensemble 动力学，reward 取 ensemble **mean**（隐式抗乐观）；DNPM 经典先例（书写/Baoding） |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation\|MoDem-V2]] (2024) | 显式化 | actor-critic ensemble，**显式 LCB** $w_1\text{mean}+w_2\text{std}$；**online-from-scratch + 保守探索** |
| [[Finetuning Offline World Models in the Real World\|FOWM]] (2023) | 配方化 | **Q-ensemble LCB（Eq 4）** + **offline→online 微调** + IQL in-sample；真机 20 trials 22%→67% |

**反面（单 WM / 无 ensemble，反衬 WMTS 必须 ensemble）**：[[DiWA- Diffusion Policy Adaptation with World Models|DiWA]]、[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]、[[Robotic World Model: A Neural Network Simulator|RWM]]、[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]——单一 WM 无 epistemic 惩罚，在 OOD/接触密集处易 model-exploitation。

**张力与开放问题**：FOWM 的 LCB 用 **Q-ensemble（仅值不确定性）**；灵巧手接触密集时 **dynamics/reward 的 OOD 更危险**，WMTS 宜上 **dynamics-ensemble**（PDDM 路线）或两者兼用。FOWM + MoDem-V2 正好覆盖 WMTS **两种真机模式**：offline→online 微调 vs online-from-scratch 保守探索。

---

## 线 2 — 结构化光谱：WM 该结构化到什么程度

> [!success] WMTS 决策
> WM 取**光谱中间**：**actuator+rigid 结构化先验**（要样本效率与物理正确）**＋ 学习残差/触觉**（补结构化建不出的接触/形变）**＋ ensemble-LCB**（因为一旦引入学习成分，model-exploitation 就回来了——见线 1）。

| recap | 光谱位置 | 精确贡献 |
|---|---|---|
| [[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation\|DexSim2Real2]] | **最结构化极** | 显式物理数字孪生 + 采样 MPC；**无 model-exploitation、样本极省、泛化未见长程**；但**只能刚体运动学**，抓不住弹性形变/高速接触 |
| [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models\|SSRL]] | **显式中间（先例）** | semi-structured：已知物理结构 + 学习残差，3 分钟真机数据——WMTS"结构化+残差"的现成范式 |
| [[World Models for Learning Dexterous Hand-Object Interactions from Human Videos\|DexWM]] | **神经 latent 极** | 神经 latent WM，可学复杂动力学、通用；但有 model-exploitation 风险、需 ensemble |

**与线 9（latent vs 显式）的衔接**：[[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook|Latent Space 综述]] champions "latent 是计算原生基底"——对 LLM 推理成立，但 WMTS 的 WM 处理**物理接触动力学**，需可解释/可验证/无 exploitation，故不全押纯 latent。

**张力**：结构化↑ → 样本效率↑、exploitation↓，但表达力↓（建不出 un-modeled 动力学）。**转笔是高速动态 + 接触主导 + 难重建**，全显式孪生路线在此不可行，只能取其"结构化先验 + 主动辨识"精神。这条张力直接推出线 1 的必要性：**学习残差一引入，就必须 ensemble-LCB 兜底**。

**WMTS 结构化 WM 的组件分解（跨 4 篇拼装的白箱蓝图）**：WMTS"取中间"时，结构化部分不是黑箱，而是可分别用真机数据校准的物理组件流水线——
$$
\text{命令}\xrightarrow{\text{actuator net (Hwangbo)}}\tau\xrightarrow{\text{Lagrangian 刚体 (SSRL)}}\ddot q\;+\;\underbrace{F^e}_{\text{ensemble 接触力 (SSRL)}}\;+\;\underbrace{(K_P,K_D)}_{\text{自适应增益 (DexCtrl)}}\;+\;\text{学习残差}\;+\;\text{ensemble-LCB}
$$
[[Learning Agile and Dynamic Motor Skills for Legged Robots|Hwangbo]] 的 actuator net（命令历史→力矩）+ [[Learning to Walk from Three Minutes of Real-World Data with Semi-structured Dynamics Models|SSRL]] 的 Lagrangian 刚体 + ensemble 接触力残差 + [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] 的自适应增益——每个组件物理意义明确、可独立校准、样本高效、结构正确处无 model-exploitation。这就是 WMTS 区别于纯神经 WM（线 12 的 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]/[[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning|STORM]]）的"**白箱骨架 + 学习残差**"。

---

## 线 3 — 无梯度规划：接触不可微的共识

> [!success] WMTS 决策
> 接触动力学**不可微**，WM 内规划用**采样式无梯度方法**（MPPI/CEM/iCEM），与 **PPO**（对动力学也免梯度）天然兼容；不依赖可微物理。

支持：[[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]（MPPI/filtering）、[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]（采样 + synergy）、[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（iCEM）、[[Finetuning Offline World Models in the Real World|FOWM]]（TD-MPC 的 MPPI）。

**无梯度规划器谱（按 sophistication，[[The CMA Evolution Strategy: A Tutorial|CMA-ES tutorial]] 提炼）**：random shooting < CEM(固定协方差) < MPPI([[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]) < iCEM([[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]) < **CMA-ES(协方差自适应 ≈ 逆 Hessian)**。越往右越能处理病态/不可分景观——灵巧手高 DOF 动作空间正是病态，WMTS 规划器宜取谱右端。

**开放问题**：采样规划在高 DOF（21-DOF LinkerHand）上搜索空间爆炸——由**线 5（降维）**解决；CMA-ES 的 $O(n^2)$ 协方差成本尤其需 eigengrasp 降维或低秩变体（**线 3↔线 5 的具体耦合**）。

---

## 线 4 — 探索信号：epistemic 而非 aleatoric

> [!success] WMTS 决策
> Probe/探索必须求 **epistemic（可约、可学）**不确定，**显式排除 aleatoric（不可约接触噪声）**；用 **ensemble disagreement 或 Bayesian surprise** 作信号，天然抗 NoisyTV。

| recap | 精确贡献 |
|---|---|
| [[Curiosity-Driven Exploration via Latent Bayesian Surprise\|LBS]] | Bayesian surprise（后验 vs 先验信念差）只奖励信念更新→抗 NoisyTV；移到 latent 空间省算力 |
| [[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation\|CEE-US]] | ensemble disagreement 也只测 epistemic——aleatoric 噪声上 ensemble 一致（不 disagree）→ 天然抗噪 |
| [[Prioritized Level Replay\|PLR]] | "学习潜力"= epistemic 可约部分（被 LBS/CEE-US 精化为"非 aleatoric"） |

**为什么对转笔关键**：转笔有真实接触噪声（aleatoric），裸预测误差（surprisal）会陷 NoisyTV——把算力浪费在本质随机、学不动的配置上。

---

## 线 5 — 降维/synergy：让高 DOF 规划可行

> [!success] WMTS 决策
> 对 **21-DOF LinkerHand** 做 **PCA synergy（eigengrasp）降维**，让 MPC/PPO 搜索可行、手姿平滑可执行。

支持：[[DexSim2Real2 - Building Explicit World Model for Precise Articulated Object Dexterous Manipulation|DexSim2Real2]]（eigengrasp PCA，**实测 m=2 ≈ m=7/16 成功率却大幅省算力、jerk 更低**）、[[Model-Based Lookahead Reinforcement Learning for in-hand manipulation|Model-Based Lookahead]]（欠驱 synergy）、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]（D'Manus synergy）。

**边界**：降维丢部分灵巧自由度，高速精细转笔需谨慎选维（m 太小可能丢关键自由度）。

---

## 线 6 — 感知路线：touch-centric 绕过视觉天花板

> [!success] WMTS 决策
> **touch-centric（触觉 + 本体）**为主，绕过 RGB 在快速遮挡下的天花板；触觉/接触是一等约束，非装饰传感器。

| recap | 精确贡献 |
|---|---|
| [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation\|ViserDex]] | vision-centric 做到极好，但**自陈** perception-control gap：快速运动→自遮挡+模糊→RGB 位姿估计极难，连续旋转"靠 proprioceptive+tactile"；药片瓶低摩擦盲区（纯视觉无法感知微观打滑） |
| [[DeXtreme- Transfer of Agile In-hand Manipulation from Simulation to Reality\|DeXtreme]] / [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND\|Rubik]] | 多相机 + 大规模 ADR，集群算力，仅简单物体 |

**论证**：转笔比重定向更快、遮挡更重 → RGB 必失守 → 这是 WMTS 选触觉的**最强外部实证**（ViserDex 自己标出了视觉天花板）。但 ViserDex 的**效率范式（curriculum+蒸馏替 ADR、单 GPU）可借**。

---

## 线 7 — 任务定义：Planner-Follower 防 mode collapse

> [!success] WMTS 决策
> 拒绝"绝对目标 + 端到端 PPO"（必致 mode collapse）；改 **receding-horizon 航点追踪 + Planner-Follower**：上层规划"去哪"，PPO 退化为"怎么跟"。详见 [[Rationale-Planner-Follower-Task-Definition]]。

- **症状证据**：[[auto_taskgen]] 已记录 Start-to-Goal 的"过拟合/机械记忆"；[[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] Turn-1 观察"绕轴旋转不需精确物理、goal-reorientation 才需要"。
- **理论 why**（三机制）：最小阻力轨迹 / 虚假相关(背板) / credit assignment 失效——见 Rationale note。
- **POMDP→Teacher-Student**：与 [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation|ViserDex]] 的 belief-state RNN 蒸馏、[[Finetuning Offline World Models in the Real World|FOWM]] 的 latent 表示同构。
- **PPO-only**：用户已否决 SAC 最大熵——熵正则不改"单目标→单轨迹"的激励结构，改任务定义才是解。

---

## 线 8 — 适应机制谱：LAAA 按"幅度×算力×速度"选

> [!success] WMTS 决策
> 真机适应按**适应幅度 × 算力 × 速度**在谱上选点；轻量优先 FiLM/控制器增益，需大幅适应才上 hypernetwork/微调。

| 机制 | 代表 recap | 特点 |
|---|---|---|
| FiLM 单向量 | [[DyWA: Dynamics-adaptive World Action Model\|DyWA]] / [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning\|DexCtrl]] | 轻，但单向量瓶颈 |
| hypernetwork 全权重 | [[Transformers as Meta-Learners for Implicit Neural Representations\|Trans-INR]] | 一次前向生成全权重，表达力高 |
| 梯度微调 | [[Finetuning Offline World Models in the Real World\|FOWM]] | 慢但彻底 |
| 隐式 ICL | [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND\|Rubik]] / [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY\|ICL-paper]] | 零梯度、上下文内适应 |
| 控制器增益 | [[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning\|DexCtrl]] | 底层增益自适应 |
| 隐式延迟 DR | [[ViserDex Visual Sim-to-Real for Robust Dexterous In-hand Reorientation\|ViserDex]] EMA(α 随机化) | [[Idea-002-Latency-Aware-Actuator\|Idea-002 LAAA]] 的轻量先例 |

**两种正交视角**（[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning|DexCtrl]] §5.2 提炼）：上表按**适应机制**分（FiLM/hypernet/梯度/ICL）；另一维按**适应目标层级**——控制器增益级（DexCtrl 学 $K_P,K_D$，接触力）/ 动力学显式级（[[DyWA: Dynamics-adaptive World Action Model|DyWA]]/RMA 物理嵌入）/ 动力学隐式级（[[SOLVING RUBIK’S CUBE WITH A ROBOT HAND|Rubik]] LSTM meta-learn）/ 不确定性级（[[Finetuning Offline World Models in the Real World|FOWM]] epistemic）。WMTS 的 LAAA 应**多级叠加**（控制器增益 + 动力学嵌入 + ensemble-LCB），并把执行器状态（增益/温度/延迟）显式入 observation——这是 [[Idea-002-Latency-Aware-Actuator|Idea-002]] 的设计依据。

---

## 线 9 — latent vs 显式：按"效率 vs 可解释"分工

> [!success] WMTS 决策
> **效率敏感处（高频 rollout）可更 latent；安全/可解释处（接触力安全、Reject 判定）必须显式/结构化。** 由 [[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook|Latent Space 综述]] 的 Representation(hybrid)/Computation(adaptive) 分类精确描述 WMTS WM 的 latent 部分。

与线 2 互为表里：线 2 谈"WM 的物理结构化程度"，线 9 谈"计算基底的可解释性"——两者都指向 WMTS 的"结构化+latent 残差"中间路线。

---

## 线 10 — Specialist→Generalist 蒸馏：WMTS 管线的骨架

> [!success] WMTS 决策
> 管线核心是 **PPO Oracle 专家 → Diffusion/Flow generalist**：先用专家在窄子集达高回报，再把多专家能力蒸馏/合并进一个泛化 generalist。标准配方 = GSL 的 **克隆-专精-合并**，几何化迭代版 = GiGSL。

| recap | 谱系位置 | 精确贡献 |
|---|---|---|
| [[Improving Policy Optimization with Generalist-Specialist Learning\|GSL]] | **奠基框架** | generalist plateau（catastrophic forgetting+ignorance）→ 克隆 specialists population 攻难子集 → 示范辅助奖励合并回 generalist |
| [[UniDexGrasp++- Improving Dexterous Grasping Policy Learning via Geometry-aware Curriculum and Iterative Generalist-Specialist Learning\|UniDexGrasp++]] | 几何化迭代版 | GiGSL：几何聚类分子集 + 迭代 generalist↔specialist |
| [[Generalization in Dexterous Manipulation via Geometry-Aware Multi-Task Learning\|Geometry-Dex]] | generalist 端 | 好表示让 generalist 直接赢（无需专家） |
| [[DexReMoE-In-hand Reorientation of General Object via Mixtures of Experts\|DexReMoE]] | 专家并存端 | MoE 多专家 + worst-case 兜底（路由而非合并） |
| [[Beyond Human Demonstrations- Diffusion-Based Reinforcement Learning to Generate Data for VLA Training\|Beyond Human Demos]] | 合并数据源 | 用 RL 生成数据训 generalist（蒸馏的数据侧） |
| [[Diffusion Policy: Visuomotor Policy\|Diffusion Policy]] | generalist 载体 | 多峰动作分布的 generalist backbone（破 PPO 单峰瓶颈） |
| [[HG-DAgger- Interactive Imitation Learning with Human Experts\|HG-DAgger]] | 交互蒸馏 | human-gated DAgger，专家→学生的交互式蒸馏 |

**为什么 WMTS 必须用它**：转笔不同配置后期分化大 → 单一 generalist 必 plateau（GSL 诊断）；故先专后合。**与线 7（Planner-Follower）衔接**：specialist 是"窄子集的 follower 专家"，合并后的 generalist 仍是 follower；上层 Planner（任务调度）决定练哪些子集、何时克隆。**与线 1 衔接**：DexReMoE 的 worst-case 兜底 = 对 generalist 不可靠子集的专家补丁，呼应 reliability head 的保守排序。

**开放问题**：population 算力大 → 在 sim Oracle 阶段做、非真机；合并保真（蒸馏不全会丢专家能力）。

---

## 线 11 — 安全/cost 约束：Reject 队列与 safety filter

> [!success] WMTS 决策
> 把"安全"从 reward 拆成**独立 cost 通道**，在 WM 内**前瞻规划过滤**不安全 action chunk（OSRP 式），用 **cost critic + ensemble-LCB** 接长期安全、防"假安全"。这正是 WMTS 的 **Reject 队列 + safety filter**。

| recap | 精确贡献 |
|---|---|
| [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL\|SafeDreamer]] | cost decoder+critic 进 DreamerV3；OSRP（WM 内 MPC 按 cost≤b 过滤）+ BSRP-Lag；Constrained CEM；near-zero-cost。**cost 必须独立于 reward**（否则 reward hacking） |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation\|MoDem-V2]] | 保守探索（LCB）——安全的"探索端"对应物 |
| [[Finetuning Offline World Models in the Real World\|FOWM]] | Q-ensemble LCB——cost critic 的不确定性版 |

**最关键的张力（critical thinking）**：SafeDreamer 的安全**完全依赖 WM 的 cost 预测准确性**——WM 在 OOD 处乐观 = **"假安全"**（规划以为安全实则危险），是 model-based safety 的根本失败模式。**所以 WMTS 的 safety filter 必须用 ensemble-LCB 的 cost 预测（线 1），而非单 WM**——这把线 11 和线 1 死死绑在一起：**安全 = 可靠性 = ensemble 不确定性惩罚**。灵巧手的 cost 须定义为接触力超限/力矩饱和/掉物/热超限等物理量。SafeDreamer 给软约束统计安全、**非硬证书**，高风险动作仍需底层限幅/CBF 兜底。

---

## 线 12 — WM 神经主干：Transformer vs RNN + 抗 autoregressive 误差

> [!success] WMTS 决策
> WM 的**神经部分**（线 2"学习残差/latent"那一半）序列主干用 **Transformer**（注意力回看接触/触觉序列、可并行训练）而非 RNN；autoregressive 误差用 **ensemble**（不止 categorical 噪声）抑制——ensemble 既抗误差又给可量化 uncertainty（接回 keystone）。

| recap | 主干 | 精确贡献 |
|---|---|---|
| [[STORM: Efficient Stochastic Transformer based World Models for Reinforcement Learning\|STORM]] | GPT-Transformer + 单 categorical token | Transformer>GRU（并行+长程）；单 token 高效（11.9 FPS）；**categorical 随机性抗 autoregressive 误差累积、防"追逐虚拟目标"**；但 Atari 像素、无接触 |
| [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION\|Dreamer]]/DreamerV3 | RSSM(GRU) | latent imagination 骨架（λ-return/symlog/KL-balance），RNN 串行慢、长程弱——STORM 换主干的基线 |

**与线 2 的分工**：线 2 定"WM 要多少物理结构"；线 12 定"其中神经那部分用什么序列主干"——两者正交。
**与线 1 / keystone 的衔接（critical thinking）**：STORM 用 **categorical 噪声**抗 autoregressive 误差，但噪声**不产出可量化 uncertainty**；WMTS 改用 **ensemble**——一举两得：既抑制误差累积（多模型平均），又产出 keystone 的 Solve/Probe/Reject 信号。这正是 WMTS 不照搬 STORM 单 WM、而上 ensemble 的理由。
**边界**：STORM 是 2D 离散像素 + reinforce，无接触/力/连续控制；"一帧一 token"迁到灵巧手必须把**接触/触觉/本体**编进 token，否则会像 STORM 在小运动物体上那样在精细接触处失真。

---

## 线 13 — 任务生成/课程：选择 vs 生成 + 垫脚石

> [!success] WMTS 决策
> Latent Task Generator = **PLR 选择（学习潜力）+ POET 生成（open-ended + 跨配置迁移 + 垫脚石）+ Goldilocks 难度筛选 + 可行性过滤（线 11）**；最难转笔配置可能需**非直接路径垫脚石**，而非"易→难"直接课程。

| recap | 角色 | 精确贡献 |
|---|---|---|
| [[Prioritized Level Replay\|PLR]] | **选择**既有任务 | 按学习潜力（TD-error）优先既有 level；Goldilocks（= 线 4 epistemic 可约部分） |
| [[Paired Open-Ended Trailblazer (POET)- Endlessly Generating Increasingly Complex and Diverse Learning Environments and Their Solutions\|POET]] | **生成**新任务 | 配对生成环境+优化 agent；**跨配置迁移解（stepping stones）**；最难能力**不可由直接课程达到**，需 open-ended 分叉路径 |
| [[The CMA Evolution Strategy: A Tutorial\|CMA-ES]] | 生成的**优化器** | auto_taskgen 用其按 fitness（高认知误差 + 可行性惩罚）生成任务；亦是 POET 的 ES |
| [[SOLVING RUBIK’S CUBE WITH A ROBOT HAND\|ADR]] | 自动扩随机化 | 按表现自动扩任务/DR 分布（curriculum 的 DR 版） |

**与 keystone/线 11 的衔接**：生成或选出的候选任务，由**同一 ensemble** 过 Solve/Probe/Reject——可行（Solve）、信息丰富（Probe，线 4）、不可学/不安全（Reject，线 11）。**与线 10 的衔接**：[[Improving Policy Optimization with Generalist-Specialist Learning|GSL]] 的"克隆专家攻难子集"= 对 PLR/POET 标出的难配置做 specialist。
**边界**：POET 种群协同进化对真机/算力昂贵 → 生成在 sim、迁移有限；取其**原则**（生成+选择+垫脚石+Goldilocks）而非完整算法。

---

## 跨线张力（元层洞见）

> [!important] 🔑 Keystone：一个 ensemble，三种读法 = 整个 scheduler
> WMTS scheduler 的 **Solve / Probe / Reject** 三队列，本质是**同一个 ensemble epistemic 不确定性信号的三种读法**：
> - **Solve（避不确定）**：朝低 disagreement 规划，LCB 安全利用（线 1：[[Finetuning Offline World Models in the Real World|FOWM]] Eq4 / [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]）。
> - **Probe（求不确定）**：朝高 disagreement 规划，信息增益探索以最快改进 WM（线 4：[[Curious Exploration via Structured World Models Yields Zero-Shot Object Manipulation|CEE-US]]，与 [[Prioritized Level Replay|PLR]] 学习潜力一致）。
> - **Reject（判不确定）**：disagreement 过高且**不可约（aleatoric，线 4 的 NoisyTV）**或预测 **cost 超限（线 11：[[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]）** → 判为不可学/不安全而弃。
>
> 这是 WMTS 架构的最大经济性：**不需要三套机制，一个 ensemble 不确定性同时驱动调度、探索、安全**。线 1 / 4 / 11 在此收敛为一点——这是整个知识库跨论文综合后浮现的、单篇 recap 看不到的架构级 insight。

> [!important] 这些线不是独立的，它们互相约束
> 1. **线 2 → 线 1**：结构化光谱一旦取中间（引入学习残差），model-exploitation 就回来 → **必须** ensemble-LCB。结构化不是 ensemble 的替代，是减轻其负担。
> 2. **线 3 → 线 5**：无梯度采样规划在高 DOF 爆炸 → 必须 synergy 降维才可行。
> 3. **线 6 → 线 7**：touch-centric 因遮挡仍是 POMDP → Teacher-Student belief 必然，且 belief 须含触觉。
> 4. **线 4 vs 线 1 的 ensemble 复用**：CEE-US 的 ensemble disagreement 既是探索信号（线 4）又是可靠性信号（线 1）——**同一个 ensemble 一物两用**（Probe 朝 disagreement 高处探索、规划朝 disagreement 低处保守）。这是 WMTS 架构的关键经济性。
> 5. **线 7 → 线 1**：Planner-Follower 把"去哪"交给上层规划（在 WM 里 lookahead），于是 WM 的可靠性（线 1）直接决定任务可行性判定——reliability head 同时服务规划与 Reject。
> 6. **线 11 → 线 1（安全=可靠性）**：SafeDreamer 的"假安全"风险（WM cost 在 OOD 处乐观）逼出硬结论——**safety filter 的 cost 预测必须用 ensemble-LCB，不能用单 WM**。于是"安全""可靠性""ensemble 不确定性"在 WMTS 里收敛为同一件事。
> 7. **线 10 → 线 7（专家即 follower）**：specialist→generalist 的每个 specialist 都是"窄子集的 follower 专家"，上层 Planner（任务调度）决定练哪些子集、何时克隆——GSL 的"克隆-专精-合并"正嵌进 Planner-Follower 的"Planner 调度 + Follower 执行"。
> 8. **线 12 → 线 1（噪声 vs ensemble）**：STORM 用 categorical 噪声抗 autoregressive 误差，但噪声不产出可量化 uncertainty；WMTS 用 ensemble 替代——同时拿到误差抑制 + keystone 的不确定性信号。**一个机制顶两个**。

---

## 一页速查：线 → 决策 → 关键论文

| 线 | WMTS 决策 | 支持极 | 反面/边界极 |
|---|---|---|---|
| 1 Ensemble-LCB | ensemble + 显式 LCB + 测试期自适应保守 | PDDM/MoDem-V2/FOWM | DiWA/World4RL/RWM/Dreamer（单 WM） |
| 2 结构化光谱 | 结构化先验+学习残差+ensemble（居中） | DexSim2Real2（显式） | DexWM（神经 latent） |
| 3 无梯度规划 | MPPI/CEM/iCEM + PPO | PDDM/MBL/DexSim2Real2/FOWM | （可微物理不依赖） |
| 4 探索信号 | epistemic（disagreement/Bayesian surprise） | LBS/CEE-US/PLR | 裸 surprisal（NoisyTV） |
| 5 降维 | PCA synergy（eigengrasp） | DexSim2Real2(m=2)/MBL/MoDem-V2 | 高速精细丢自由度 |
| 6 感知路线 | touch-centric | ViserDex 自陈视觉天花板 | DeXtreme/Rubik（多相机 ADR） |
| 7 任务定义 | Planner-Follower + receding horizon | Rationale note/auto_taskgen | 端到端 goal-conditioned PPO |
| 8 适应机制 | 按幅度×算力×速度选谱 | DyWA/Trans-INR/FOWM/Rubik/DexCtrl | 单一机制硬套 |
| 9 latent vs 显式 | 效率→latent，安全→显式 | Latent Space 综述 | 纯 latent 原生基底主张 |
| 10 Specialist→Generalist | 克隆-专精-合并（GSL/GiGSL） | GSL/UniDexGrasp++/DiffusionPolicy | DexReMoE（路由不合并） |
| 11 安全/cost | 独立 cost + OSRP 过滤 + ensemble-LCB | SafeDreamer/MoDem-V2/FOWM | 单 WM 的"假安全" |
| 12 WM 神经主干 | Transformer + ensemble 抗误差 | STORM(Transformer/categorical) | Dreamer(RNN 串行) |
| 13 任务生成/课程 | 选择(PLR)+生成(POET)+Goldilocks+可行性过滤 | PLR/POET/CMA-ES/ADR | 直接路径课程(够不到最难) |

## References
- 综合自 [[_RelatedPapersIndex]] 的 48 篇 recap（各篇 §0/§5/§6 的跨论文分析）
- 进度与 WM-core 论证线源头：[[_UpgradeProgress]]
- 任务定义专论：[[Rationale-Planner-Follower-Task-Definition]]
- 项目主架构：[[Final_WMTS]]
