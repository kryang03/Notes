---
tags:
  - paper
  - world-model
  - human-video
  - dexterous-manipulation
  - latent-jepa
  - mpc-planning
  - WMTS
aliases:
  - DexWM
  - Human Video Dexterous WM
paper-year: 2026
read-date: 2026-06-15
venue: arXiv 2512.13644 (FAIR Meta / NYU, LeCun 组)
paper-pdf: "[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[StochasticProcess]]"
  - "[[WorldModels]]"
  - "[[Final_WMTS]]"
---

# DexWM: World Models for Dexterous Hand-Object Interactions from Human Videos

> [!abstract] 核心贡献
> 学一个**专门面向灵巧手-物体交互**的 latent world model（JEPA 式：冻结 DINOv2 编码、预测 latent 而非像素）。三个关键点：(1) **动作用 3D 手部关键点之差**（MANO 21 点/手 + 相机运动，Eq 2，$\in\mathbb R^{44\times3}$）表示——细粒度灵巧，远胜 text/wrist/whole-body 粗动作；(2) 为绕开灵巧数据稀缺，**在 900+ 小时人类 egocentric 视频（EgoDex）+ 非灵巧机器人（DROID）上训练**，跨本体；(3) 发现**只预测视觉 latent 不足以抓住灵巧细节**，加 **hand-consistency 辅助损失**（预测指尖/腕热力图）后 PCK@20 从 26→60。把训好的 DexWM 当**状态转移模型在 MPC/CEM 里规划** waypoint，真机 Franka+Allegro **抓取成功率 83%**，平均**超过 Diffusion Policy 50%+**。**它是库内最贴近 WMTS 的灵巧 WM 论文，而其最重要的洞见——"latent 视觉特征不足以表达灵巧、必须加结构化手部监督"——正是 WMTS 必须在 latent 之外加触觉/接触/结构化状态的直接论据。**

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间]] — WM 当状态转移模型做 MPC/CEM 规划（隐空间 WM，model-based planning，非端到端 RL）；被它超越的 DP 本体见 [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）]]。
> - [[EmbodiedAI]] — 从人类 egocentric 视频学灵巧先验、跨本体（human↔robot）、zero-shot sim-to-real。
> - [[StochasticProcess]] — Conditional Diffusion Transformer (CDiT) 架构 + AdaLN 动作条件（但直接回归 latent、不做迭代去噪）；CEM 采样规划呼应 [[StochasticProcess#6.2 物理根：自由能最小化与重要性采样]]。
> - [[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]] — DexWM 是**确定性单 WM**、无 epistemic 度量，规划会利用 WM 误差；WMTS 必须叠 ensemble-LCB（与 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] 合流）。
> - [[Final_WMTS]] — **WMTS 灵巧 WM 的最近范本**；HC-loss 洞见 = WMTS 需触觉/结构化状态的论据；WM-当-planner、超越 DP 印证 WMTS "WM 精炼/引导 generalist"。
>
> **暗线定位**：DexWM 从两侧碰到 **认知不确定性三用** 暗线——确定性单 WM 缺 epistemic 护栏（→ ensemble-LCB）；而其真正独有的一击是指出"视觉 latent 表达灵巧有上限，必须加结构化（手/接触）监督"，这对 WMTS 的"latent 之外还要触觉一等输入"是最强论据。
>
> **核心技术**: JEPA 式 latent WM (冻结 DINOv2), 手部关键点动作 (MANO, Eq 2), CDiT 预测器 (直接回归 latent), Hand-Consistency Loss (Eq 5), 人类视频 + 跨本体训练, CEM/MPC 规划 (Eq 6)

## 0. 阅读定位与范本价值

DexWM 是**库内最贴近 WMTS 的灵巧 world model**：专门建灵巧手-物体动力学、用 WM 做规划、且在真机灵巧手上超过 [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]（WMTS 的 generalist 本体）。读它要抓三条对 WMTS 决定性的线：

1. **动作表示**——用手部关键点（运动学）而非粗动作，是"灵巧"能被建模的前提；
2. **HC-loss 洞见**——"只预测视觉 latent 不足以表达灵巧（手在图里只占小区域），必须加结构化手部监督"，PCK@20 从 26→60。这是**整篇最可迁移的一条**：它直接论证 WMTS 不能只靠 latent/视觉 WM，必须加触觉/接触/结构化状态；
3. **WM 当 planner**——把 WM 当状态转移模型在 MPC/CEM 里规划，zero-shot 超过 DP 50%+，印证"WM 引导/精炼 generalist"。

它与 [[DyWA: Dynamics-adaptive World Action Model|DyWA]]（非抓取、状态回归）、[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]（真机灵巧 MBRL）、DexSim2Real2（显式 articulated WM）同属"灵巧 + WM"族，但 DexWM 是**JEPA 式 latent + 人类视频规模 + 灵巧专用动作**的最新代表（LeCun 组）。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
建灵巧手-物体交互很难：细微手指动作经接触影响环境。现有 world model 的动作空间太粗（text/导航/全身），抓不住灵巧；灵巧机器人数据又稀缺。DexWM 用**手部关键点动作** + **海量人类视频** + **hand-consistency 损失**解决三难，并用 WM 在 MPC 里 zero-shot 规划灵巧操作。

### 1.2 直观隐喻
粗动作 WM 像"只知道手大概往哪挪"，建不出"松开手指物体会掉"这种灵巧因果。DexWM 让模型"看人类视频里手指关键点怎么动、物体怎么反应"，并**专门考核它能否还原手的位置**（HC loss）——逼它把手的精细构型学进 latent。规划时像"在脑内世界里搜一串关节角，让物体到达目标"。可证伪含义：优势应集中在"**需要精细手指构型**"的任务；动作越粗、手在图里越小，越需要 HC 这类结构化监督——Table 2/3 正是如此。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 / 动作空间 | 关键局限 |
|---|---|---|
| Cosmos / 文本 video-to-world | 文本条件生成视频 | 动作太粗，无精细控制 |
| NWM（导航 WM） | 相机/导航动作 | 不含手/身体动力学 |
| PEVA（全身 pose WM） | 上半身 pose | **无手指 articulation** |
| Diffusion Policy（BC 动作） | 多模态动作分布 | 泛化弱、规划不鲁棒（被 DexWM 超 50%+） |
| DexSim2Real2 / DWM | articulated / 场景-动作视频扩散 | 各自范围；非通用人类视频 latent |
| **DexWM** | **手部关键点动作 + 人类视频 + HC loss** | 视觉 latent（无触觉/力）；确定性单 WM；准静态抓放；动作=运动学非力矩 |

### 1.4 Delta 分析
精确增量 = **灵巧专用动作（手部关键点差）+ 人类视频跨本体规模训练 + hand-consistency 损失**。相对粗动作 WM（NWM/PEVA/文本）：动作细到手指、并用 HC loss 补"视觉 latent 抓不住手"的洞；相对灵巧 WM（DexSim2Real2/DWM）：JEPA 式通用 latent + 900h 人类视频 scaling + zero-shot MPC 规划。工程取舍：**确定性 latent**（推理快）、CDiT 但**直接回归不去噪**（更快）。

## 2. 核心方法与理论（原理与理论：latent WM + 关键点动作 + HC loss + 规划）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $I_{k_i}$ | egocentric RGB | 人/机器人相机 | observed | 观测图像 | 真状态不可观 |
| $s_{k_i}=E_\phi(I_{k_i})$ | $\mathbb R^{P\times d}$ patch latent | **冻结 DINOv2** | frozen | latent 状态 | 编码器训练时冻结 |
| $H_{k_i}=\{H^L,H^R\}$ | $21\times3$/手 | MANO 关键点 | 数据/FK | 手构型 | 表达灵巧的核心 |
| $a_{k_1\to k_2}$ | $\mathbb R^{44\times3}$ | 关键点差 + 相机 (Eq 2) | 条件 | 灵巧动作 | **运动学动作，非力矩** |
| $f_\theta$ | predictor | CDiT 训练 | learned | latent 转移 (Eq 1/3) | **确定性**、直接回归 latent |
| $\hat s_{k_{n+1}}$ | latent | 预测 | learned | 下一 latent | 多步=自回归喂回 |
| $\hat V_{k_{n+1}}$ | $12\times H\times W$ 热力图 | $g_\theta$ | learned | 指尖/腕位置 | HC loss 监督 |
| $\Theta_k$ | 关节角 | CEM 优化 | 优化变量 | 规划输出 | $a_k=G(\Theta_k)$ FK |
| $\lambda,\mu$ | =100, 0.001 | 超参 | 固定 | HC 损失权 / 关键点 cost 权 | $\lambda$ 大说明 HC 很重要 |

### 2.2 状态与动作表示（无跳步）
**latent 状态**：用**冻结 DINOv2** $E_\phi$ 把图像编码成 patch latent $s_{k_i}\in\mathbb R^{P\times d}$（语义丰富、跨场景泛化），不在像素层建模（JEPA 思想）。

**动作（Eq 2）**：手部关键点之差 + 相机运动，全部对齐到同一坐标系 $k_1$：
$$
a_{k_1\to k_2}=\big[(H_{k_2}-H_{k_1})^T,\ \delta t_{k_1\to k_2}^T,\ \delta q_{k_1\to k_2}^T\big]^T\in\mathbb R^{44\times3}.
$$
人类视频已带关键点标注；DROID 的二指夹爪用**末端 dummy 关键点**近似成灵巧手（开合改变同心圆半径模拟手指张开）；真机/RoboCasa 用 FK 算关键点。Allegro 4 指映射到 5 指动作空间（最后一指复用为小指）。

### 2.3 预测器与多步预测（Eq 1/3）
$$
\hat s_{k_{n+1}}=f_\theta(s_{k_0},\dots,s_{k_n},\ a_{k_n\to k_{n+1}}).
$$
架构基于 **CDiT**（Conditional Diffusion Transformer），AdaLN 注入 132 维 flatten 动作做条件；但**不做迭代去噪、直接回归 DINOv2 latent**（推理快）。**假设环境确定性**（更快）；训练时**随机跳帧**（非固定频率）提升泛化。多步：自回归把 $\hat s$ 与下一动作喂回。

### 2.4 Hand-Consistency 损失（关键洞见，Eq 4-5）
主损失是 latent MSE（Eq 4）：$\mathcal L_{state}=\frac1{Pd}\sum_p\|s_{k_{n+1}}(p)-\hat s_{k_{n+1}}(p)\|_2^2$。**但只用它不够**——手在图里只占小区域，latent 相似不代表手位置准。于是加 HC loss（Eq 5）：用 $g_\theta$ 预测指尖/腕热力图 $\hat V$，
$$
\mathcal L_{HC}=\frac1{12HW}\|V_{k_{n+1}}-\hat V_{k_{n+1}}\|_2^2,\qquad \mathcal L=\mathcal L_{state}+\lambda\mathcal L_{HC}\ (\lambda=100).
$$
$\lambda=100$ 极大权重说明：**结构化手部监督是灵巧建模的关键，不是点缀**。

### 2.5 规划（Eq 6，MPC/CEM）
把 DexWM 当状态转移模型做 goal-conditioned 规划：优化关节角序列 $\Theta_{0:T-1}$ 使终态 latent 逼近目标，$a_k=G(\Theta_k)$（FK），用 **CEM** 优化。cost $C=C_{state}+\mu C_{kp}$（latent L2 + 关键点像素距离，$\mu=0.001$）——**只用 latent cost 次优，加关键点 cost 才好**（再次印证 latent 不够）。

### 2.6 概念边界与符号陷阱
- **JEPA 式 latent WM**：预测 DINOv2 latent，不重构像素（≠ World4RL 像素扩散、≠ STORM 重构）；又一种 "world model" 义项。
- 动作是**运动学手部关键点**，不是电机力矩——规划出 waypoint 交低层控制器执行。
- **确定性单 WM**：无随机、无 ensemble、无不确定性。
- **latent ≠ 手位置准**：Table 3 显示 embedding L2 更低不代表 PCK 更高 → 感知相似度不等于灵巧准确度。
- 规划用 **CEM/MPC**（test-time 动作优化），不是 PPO。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
EgoDex（829h egocentric 人类视频，带手/pose 标注）+ DROID（二指机器人）+ ~4h RoboCasa exploratory 灵巧数据（fine-tune）。真机 Franka + Allegro。指标：embedding L2、PCK@20（关键点重叠%）、任务成功率。基线 Cosmos-Predict2、NWM*、PEVA*、Diffusion Policy。

### 3.2 关键结果与因果解释
- **HC loss（Table 2，核心）**：加 HC 后 PCK@20 **26→60**、embedding L2 0.85→0.66。**因果**：手占图小、latent 主损失忽略它，HC 强制 latent 含手位置信息——灵巧建模的关键。
- **人类视频（Table 1）**：EgoDex+DROID 在 RoboCasa 上显著优于 DROID-only（embedding L2 1.3→0.79，PCK 12→17），且不损 EgoDex 性能。**因果**：人类视频提供灵巧先验、跨本体迁移。
- **动作空间（Table 3）**：DexWM PCK@20 60/68 最佳，胜 NWM*（34/48，仅相机）、PEVA*（56/63，无手指）。**关键**：PEVA* embedding L2 略低（0.62）但 PCK 更差——**感知相似 ≠ 手准**。
- **真机**：Franka+Allegro 抓取 **83%**，平均超 DP **50%+**（grasp/place/reach）。**因果**：WM 做 MPC 规划比 DP 直接预测动作更鲁棒、更能泛化到 unseen。
- **scaling/backbone**：30M→450M 单调提升；跨 DINOv2/v3/Web-SSL/V-JEPA2/SigLIP2 都行，DINOv2 最强。

### 3.3 Ablation / 对照因果链
- `去 HC loss → 只学 latent → 手位置不准（PCK 26）`。
- `去人类视频（仅 DROID）→ 缺灵巧先验 → 跨本体差`。
- `规划只用 latent cost（去关键点 cost）→ 规划次优`。
- `粗动作（相机/全身）替关键点 → 抓不住灵巧（NWM*/PEVA* 更差）`。

### 3.4 工程约束与实验边界
- **视觉 latent，无触觉/力/接触**显式建模。
- 准静态 grasp/place/reach，**非高速动态 in-hand**。
- 动作=运动学关键点，规划 waypoint 交低层控制器；非力矩级。
- 确定性单 WM，无不确定性。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**灵巧手-物体动力学要建好，必须 (a) 用细到手指关键点的动作表示、(b) 借海量人类视频补数据稀缺、(c) 加结构化手部监督（HC loss）——因为纯视觉 latent 抓不住"手在图里只占小区域"的灵巧细节；如此训出的 latent WM 当 MPC 状态转移模型，zero-shot 超过 Diffusion Policy。** 一句话：**latent 视觉 WM 对灵巧"看起来准"不等于"手真的准"，必须加结构化（手/接触）监督。**

### 4.2 为什么这个设计有效
(1) 关键点动作精确表达手指；(2) 人类视频提供海量灵巧先验、跨本体迁移；(3) HC loss 强制 latent 含手位置信息；(4) WM 做 MPC 规划比 BC 直接出动作更鲁棒；(5) 直接回归 latent + 确定性 → 推理快、适合规划。

### 4.3 什么时候会失效
- 需要**触觉/力**判断的任务：纯视觉 latent 无接触信息。
- 高速动态 in-hand（转笔）：准静态抓放不能外推。
- 动作=运动学：力控/阻抗相关任务表达不足。
- 确定性单 WM：OOD 处无不确定性、易被规划利用。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
DexWM 是 JEPA 式 latent 预测 + MPC 规划：规划质量受 latent WM 保真 + cost 设计限。确定性假设省时但丢随机性；无 ensemble/uncertainty → 规划可利用 WM 误差（无显式抑制）。HC loss 是"latent 不足"的补丁，本质指出**纯视觉 latent 对灵巧的表达上限**。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 DexWM 关系 |
|---|---|---|---|
| Diffusion Policy（BC） | 多模态动作 | 泛化/规划弱 | 被 DexWM 超 50%+ |
| NWM/PEVA（粗动作 WM） | 全身/导航 | 无手指 | DexWM 用关键点胜出 |
| DexSim2Real2 | 显式 articulated | 范围窄 | 灵巧 WM 同族 |
| [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]] | ensemble-LCB、真机 | latent 无关键点结构 | **互补**：DexWM 缺的 ensemble + MoDem-V2 缺的关键点结构 |

### 5.3 工程/实验维度
视觉 latent 无触觉、确定性单 WM、运动学动作、准静态、CEM 计算成本是主要边界；高速动态接触、力控、触觉未覆盖。

## 6. 对用户研究的启发（未来与结合）

### 6.1 对 WMTS / 灵巧手的迁移

| WMTS 模块 | DexWM 对应 | 迁移设计 |
|---|---|---|
| **灵巧 WM 设计** | JEPA latent + 关键点动作 + HC loss | WMTS 的 WM 状态/动作要含**手指构型**；HC loss 思想换成**触觉/接触一致性损失** |
| 数据策略 | 900h 人类视频 + 跨本体 | 用人类/teleop 视频学转笔灵巧先验，跨本体迁到 LinkerHand |
| WM 当 planner | CEM/MPC 规划 waypoint | WMTS 可用 WM 做 task/chunk 规划；但保留 PPO Oracle（接触不可微） |
| 超越 DP | zero-shot 超 DP 50%+ | 印证 "WM 引导 generalist > 纯 DP"，支撑 WMTS 精炼步 |
| 抗 WM 误差 | ✘（确定性单 WM） | **加 ensemble-LCB**（[[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]） |

**核心论证（critical thinking）**：DexWM 给 WMTS 的最强一击是 **HC-loss 洞见**——它用实验（PCK 26→60、Table 3 "L2 低 ≠ 手准"）证明**纯视觉 latent WM 不足以表达灵巧，必须加结构化手部监督**。把这条迁到 WMTS：**latent/视觉 WM 对转笔这种接触主导任务同样不够，WMTS 必须把触觉（5×12×6）、接触状态、actuator 物理作为一等监督/输入**（DexWM 用手部关键点热力图，WMTS 用触觉拓扑 + 接触一致性损失）。其次，DexWM 验证了"**WM 当 planner zero-shot 超过 DP**"，支撑 WMTS"WM 引导/精炼 DP generalist"的核心论点；它的人类视频 scaling 也提示 WMTS 可借 teleop/人类视频学灵巧先验。**但要警惕外推**：(1) DexWM 是**准静态抓放**，转笔是高速动态接触，动力学体制差；(2) 动作是**运动学关键点**，WMTS 是电机力矩/阻抗，sim-to-real 与控制接口不同；(3) **确定性单 WM 无不确定性**，WMTS 必须叠 ensemble-LCB（与 MoDem-V2/RWM/Model-Based Lookahead 的结论再次合流）；(4) DexWM 用 CEM 规划，WMTS 接触不可微宜保留 PPO + WM ranking。

### 6.2 可验证实验建议
- 把 HC loss 换成**触觉一致性损失**：在转笔 WM 上加"预测触觉拓扑/接触点"辅助目标，对照纯 latent，测灵巧动力学保真（直接对标 Table 2）。
- 人类视频灵巧先验：用 teleop/人类转笔视频预训 WM/generalist，测跨本体迁到 LinkerHand 的样本效率。
- WM-planner vs DP：复刻"WM-MPC 超 DP 50%+"到手内任务，并加 ensemble-LCB，测 zero-shot 与 model-exploitation。

### 6.3 不应过度外推的点
- 准静态抓放成功**不能**外推到高速转笔。
- 视觉 latent 无触觉/力 → 接触主导任务需触觉一等输入。
- 确定性单 WM 无不确定性 → 必须 ensemble-LCB。
- 运动学关键点动作 ≠ 力矩/阻抗控制接口。

## 7. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
WM 当状态转移模型做 goal-conditioned MPC/CEM 规划（Eq 6），是 model-based planning（非端到端 RL，[[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间]]）；与 Dreamer/TD-MPC 的 WM-for-control 一脉。

### 与 [[EmbodiedAI]] 的联系
从 829h 人类 egocentric 视频 + 跨本体（human↔二指↔Allegro）学灵巧先验，zero-shot sim-to-real 到 Franka+Allegro；体现"用人类数据 scale 灵巧"的具身路线。

### 与 [[StochasticProcess]] 的联系
Conditional Diffusion Transformer (CDiT) + AdaLN 动作条件（但直接回归 latent、不去噪）；CEM 进化采样规划，与 [[StochasticProcess#6.2 物理根：自由能最小化与重要性采样]] 的采样+加权同宗。

### 与 [[WorldModels]] 的联系
DexWM 是隐空间 WM 当 planner 的灵巧实例；但确定性单 WM 无 epistemic 度量（[[WorldModels#3.2 PETS：用 Bootstrap Ensemble 抓认知不确定性]]），规划会利用 WM 误差，是 WMTS 加 ensemble-LCB 的又一证。

### 与 [[Final_WMTS]] 的联系
WMTS 灵巧 WM 的最近范本；HC-loss 洞见（latent 不足、需结构化监督）= WMTS 必须加触觉/接触/actuator 结构的论据；"WM-planner 超 DP"印证 WM 引导 generalist；其确定性单 WM 软肋 = WMTS 加 ensemble-LCB 的又一证。

## References
- 原始 PDF：[[World Models for Learning Dexterous Hand-Object Interactions from Human Videos.pdf]]（FAIR Meta / NYU，arXiv 2512.13644）
- 被超越：[[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]；对照 NWM/PEVA/Cosmos
- 灵巧 WM 同族：DexSim2Real2、DWM；互补 [[MoDem-V2- Visuo-Motor World Models for Real-World Robot Manipulation|MoDem-V2]]
- 思想源：JEPA/V-JEPA2（LeCun）、DINOv2、CDiT、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]
- 项目入口：[[Final_WMTS]]
- 簇内关系（Delta）：
  - vs [[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]：DP 直接回归动作（BC）；DexWM 把灵巧 latent WM 当 MPC planner，zero-shot 超 DP 50%+，论证"BC 直接出动作"泛化/规划弱。
  - vs [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]：都用高保真生成 WM，但 World4RL 像素扩散 + PPO 端到端**训策略**；DexWM latent-JEPA + CEM/MPC **测试期规划**（不训策略）。
  - vs [[SAFEDREAMER- SAFE REINFORCEMENT LEARNING WITH WORLD MODEL|SafeDreamer]]：都在 WM 里做 CEM 前瞻规划，SafeDreamer 加 cost 约束做安全过滤，DexWM 只 goal-conditioned latent+关键点 cost，无安全通道。
