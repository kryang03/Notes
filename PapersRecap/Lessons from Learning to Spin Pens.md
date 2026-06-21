---
tags:
  - paper
  - dexterous-manipulation
  - pen-spinning
  - in-hand-manipulation
  - sim-to-real
  - reinforcement-learning
  - PPO
aliases:
  - Lessons from Pen Spinning
  - Pen Spinning
  - Spin Pens
read-date: 2026-01-31
venue: CoRL 2024
paper-year: 2024
authors:
  - Jun Wang
  - Ying Yuan
  - Haichuan Che
  - Haozhi Qi
  - Yi Ma
  - Jitendra Malik
  - Xiaolong Wang
institution: UC San Diego, CMU, UC Berkeley
paper-pdf: "[[Papers/Lessons from Learning to Spin Pens.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
---

# Lessons from Learning to Spin "Pens"

> [!abstract] 核心贡献
> 首个实现**连续旋转无自然支撑笔状物体**的学习系统。核心不是某个新网络，而是一条 **特权 Oracle (PPO) → Open-loop Replay 数据引擎 → 纯本体 Student fine-tune** 的三阶段 sim-to-real 流程：用人类启发的 6 种 Canonical Grasp 把 finger gaiting 的关键帧塞进初始状态分布，用 $r_z$ 水平约束把"仿真花哨但真机不稳"的解从策略空间里剔除，最后用开环回放自动产出 **<50 条** 真机成功轨迹完成微调，在 10+ 种不同质量/摩擦/尺寸的笔上实现多圈旋转。

> [!tip] 与理论基础的关联
> - [[Dynamics|Dynamics §2.3]] — finger gaiting 的纯滚动/非完整 (Pfaffian) 约束与接触反力，是"手指交替接触维持持续旋转"的数学根；笔旋转是 open-chain↔closed-chain 反复切换的混合系统。
> - [[ContactMechanics|ContactMechanics §3]] — 二值触觉 $c_t$ 对应硬指点接触模型的退化观测；摩擦锥 $\|f_t\|\le\mu f_n$ 决定笔倾斜后何时滑落。
> - [[ReinforcementLearning|ReinforcementLearning §5]] — 三阶段流程用 Open-loop Replay **替代** zero-shot Domain Randomization 的迁移路线。
> - [[ControlTheory|ControlTheory §3]] — 30 Hz PD 位置控制 + "真机降增益容错"是刚度-柔顺权衡的具体落点。
> - [[EmbodiedAI|EmbodiedAI §2.3]] — Oracle→Student 蒸馏与真机演示 fine-tune 是 RL+IL 混合的模仿学习范式。
>
> **核心技术**: Privileged Oracle (PPO, 特权信息) · Canonical Grasp 初始状态分布 · $r_z$ 水平约束 · Open-loop Replay 数据引擎 · Proprioceptive Student Fine-tune

## 0. 阅读定位与领域坐标

这篇是 in-hand rotation 这条领域主线上**难度被推到极端**的一篇：它把"被旋转的物体"从立方体/球（有自然支撑面）换成了笔（细长、无支撑、必须动态平衡），从而把任务从"重定向"逼成了"动态平衡 + finger gaiting 协调"。它在知识图谱里的角色有三层：

1. **转笔项目 (灵巧手转笔/Thumbaround) 的直接母本**——它给出了一套可复刻的 sim-to-real 工程范式（见 §6），用户的 PPO 转笔方案几乎可以逐条对照。
2. **in-hand rotation 领域综述的锚点**——它与 [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] / [[RotateIt - General In-Hand Object Rotation with Vision and Touch|RotateIt]] / [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] / [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]] / [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand|Finger Gaiting]] 构成可对比的演进谱系（见 §7 领域综述）。
3. **sim-to-real 方法论的反例样本**——它**没有**走主流的 zero-shot DR / 在线 RMA 适应，而是承认 gap 不可消、转而用"开环回放 + 少量真机微调"绕过它。这条路线对 WMTS 的 real-robot fine-tuning 阶段是直接参考。

> [!info] 与范本的关系
> 本篇按 [[Example/Rodrigues Network for Learning Robot Actions|RodriNet 范本]] 的四支柱整理：§1 逻辑与价值、§2 原理与理论（变量来源追踪 + 无跳步推导 + 符号陷阱）、§3 实验与验证、§5–§7 局限与个性化迁移。

## 1. 问题设定与动机 ← 逻辑与价值

### 1.1 一句话核心

通用 in-hand 方法默认物体有支撑面、姿态误差可恢复；转笔没有这两个前提，于是论文不去强化策略本身，而是**重塑训练分布与数据来源**——用 canonical grasp 喂对初始状态、用 $r_z$ 砍掉不可迁移的解、用 open-loop replay 把"哪条仿真轨迹真机也成立"这件事直接测出来。

### 1.2 直观隐喻

> [!tip] Oracle 轨迹如同乐谱
> 即使演奏者（真机）与作曲家（仿真）的乐器音色不同，照谱演奏（Open-loop Replay）仍能奏出旋律（成功轨迹）；成功的演奏录音再反哺训练即兴演奏（闭环 Student 策略）。这个隐喻是**可证伪的**：它断言"动作序列"比"状态-动作映射"更能跨越 gap——若真机动力学与仿真差到连开环都失败，整套方法立刻崩溃（§4.3）。

### 1.3 现有方法的局限

| 方法范式 | 注入了什么先验/假设 | 关键局限（对转笔为何不够） |
|------|----------------|----------|
| 经典模型控制 (model-based) | 精确接触模型 + 摩擦参数 | 笔的质心/摩擦逐物体变化且难辨识，模型误差直接放大为滑落 |
| Teleoperation + IL | 人能演示 | 转笔是高速动态动作，遥操作延迟使人无法采集到稳定演示 |
| Zero-shot DR (Dactyl 路线) | DR 覆盖足够宽则真机落在分布内 | 笔的动态平衡对参数极敏感，DR 要覆盖到的范围会稀释策略，仿真就难收敛 |
| 在线适应 RMA (HORA 路线) | 真机可在线估计 extrinsics | 转笔失败即掉落不可恢复，没有"边转边适应"的容错窗口 |
| 纯本体策略直接训练 | 本体感觉足以推断接触 | 仿真中就无法收敛——缺接触/几何信息时 finger gaiting 探索不到 |

### 1.4 Delta 分析（相对最近基线）

| 维度 | 前人 (OpenAI Dactyl / HORA) | 本文 |
|-----|------|------|
| 物体类型 | 立方体/球体（有自然支撑面，姿态误差可恢复） | **笔状物体**（无支撑，倾斜不可逆，需动态平衡） |
| 感知模态 | 视觉追踪 / 纯本体 | 训练期 点云+触觉+特权物理 (Oracle) → 部署期 纯本体 (Student) |
| Sim-to-Real | Zero-shot DR / RMA 在线适应 | **三阶段**: 仿真预训练 → Open-loop Replay → Real Fine-tune |
| 真实数据需求 | 0（零样本）或大量遥操作 | **<50 条**（由 Open-loop 自动产生，非人工遥操作） |
| 核心新颖性 | DR 覆盖 / 适应模块 | Canonical Grasp 初始化 + Open-loop 数据引擎 + $r_z$ 约束 |

> Delta 的精确表述：**不是"换了更强的策略网络"，而是把 sim-to-real 的负担从"让一个策略零样本鲁棒"转移到"用开环把可迁移的动作序列筛出来，再用极少真机数据贴合真实动力学"。**

## 2. 核心方法与理论 ← 原理与理论

### 2.1 变量来源追踪表

这是理解全文的钥匙：表中"来源阶段"一栏区分了 **特权 (privileged)** 与 **本体 (proprioceptive)** 两类观测——三阶段管线之所以存在，正是因为右侧三行（笔位姿、点云、物理属性）在真机上**不可观测**。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $q_t$ | $\mathbb{R}^{16}$（Allegro 16 DoF） | 观测（本体） | 否（输入） | 关节角，Oracle 取 3 帧、Student 取 30 帧历史 | 时间窗 Oracle≠Student；是位置非速度 |
| $a_{t-1}$ | $\mathbb{R}^{16}$ | 网络上一步输出 | 否（作为输入） | 上一步 PD **位置目标** | 动作是 target joint pose，**不是力矩** |
| $c_t$ | $\{0,1\}^{20}$ (4 指 × 5) | 观测（二值触觉） | 否 | 指尖接触有/无 | 二值 $\neq$ 接触力；sim 阈值化 vs 真机噪声 |
| $p_t$ | $\mathbb{R}^{12}$ (4 指尖 xyz) | 观测/FK | 否 | 指尖位置 | 手坐标系 vs 世界系需对齐 |
| $w_t$ | $\mathbb{R}^7\!+\!\mathbb{R}^3$ | **特权**（仿真真值） | 否 | 笔位姿 (pos+quat) + 角速度 | 部署时 Student **无此量** |
| 点云特征 | $\mathbb{R}^{100\times3}\!\to\!\mathbb{R}^{64}$ | **特权**（仿真几何）→PointNet | PointNet 参数带梯度 | 物体形状编码 | 部署时无点云，靠 motion prior 隐式代偿 |
| 物理属性 | $\mathbb{R}^5$ | **特权**（仿真参数） | 否 | 质量/质心/摩擦/尺寸 | 真机不可观测——**sim-to-real gap 的根源** |
| $\hat{A}_t$ | scalar | rollout + GAE 计算 | 否（detached 作权重） | 优势函数 | GAE 估计，作为 surrogate 的系数不回传 |
| $r_t(\theta)$ | scalar | $\pi_\theta/\pi_{\theta_{old}}$ | 是（对 $\theta$） | 重要性采样比 | 分母 $\pi_{\theta_{old}}$ detached |
| $r_z$ | scalar | 奖励计算 | 否 | 惩罚笔最高/最低点高度差 | $z$ 是**世界竖直轴**（重力方向），非笔长轴 |

### 2.2 前置理论从零推导：为什么转笔**必须** finger gaiting

范本要求"从经典理论无跳步推到论文设计"。本文三个核心设计（Canonical Grasp、$r_z$、gaiting 本身）其实都能从单刚体旋转动力学 + 摩擦锥约束推出来，不是经验拍脑袋。

**第 1 步——单刚体旋转的欧拉方程。** 笔近似为绕世界竖直轴 $z$ 旋转的刚体，转动惯量 $I$，角速度 $\omega$。各手指 $i$ 在接触点 $r_i$ 施加力 $f_i$，则
$$I\dot{\omega} = \tau_{ext} = \sum_i \big(r_i \times f_i\big)\cdot \hat{z}.$$
要持续旋转（$\omega>0$ 不衰减），需要净力矩长期为正。

**第 2 步——接触力被摩擦锥单向约束。** 每个接触力分解为法向 + 切向，库仑摩擦给出
$$f_{i,n}\ge 0,\qquad \|f_{i,t}\|\le \mu\, f_{i,n}.$$
关键：法向力**只能推不能拉**（$f_{i,n}\ge0$），切向力被法向力上界锁死。单个手指能提供的力矩方向和大小因此受限。

**第 3 步——手指工作空间有限 ⇒ 单指无法持续供矩。** 指尖轨迹在手的工作空间内有界，一根手指推着笔转过一个角度后就到达工作空间边界，无法继续同向施力。要让 $\sum_i(r_i\times f_i)\cdot\hat z$ 长期为正，必须有手指"脱离接触 → 回到起始位姿 → 重新接触"的循环——这就是 **finger gaiting**：把连续旋转拆成"几根手指供矩 + 其余手指复位"的相位序列。

**第 4 步——这是一个受控切换（混合）系统。** 设接触集 $\sigma(t)\subseteq\{1,2,3,4\}$，则系统动力学是分段的
$$\dot{x} = f_{\sigma(t)}(x,u),\qquad \sigma(t)\in 2^{\{1,\dots,4\}}.$$
每次手指接触/脱离，系统在 open-chain 与 closed-chain 之间切换，质量矩阵 $M(q)$ 的秩突变（[[Dynamics|Dynamics §2.1]]）。gaiting = **一段受控的模式切换序列**。这正是 [[Dynamics|Dynamics §2.3]] 里 finger gaiting 作为非完整重定位机动的动力学版本。

**第 5 步——两个设计的物理必然性，与退化情形。**
- **Canonical Grasp 的必然性**：模式序列 $\sigma(t)$ 是周期的，存在几个关键相位（哪几指供矩、哪几指复位）。若初始状态只采一个相位，策略永远探索不到完整循环 → 必须用 6 个 canonical grasp 覆盖周期上的关键切换点（这把 §3.3 "单 pose 不稳定"的消融解释为**覆盖不到切换流形**，而非"数据不够"）。
- **$r_z$ 的必然性**：笔倾斜角 $\theta$ 时重力矩 $\tau_g = mgl\sin\theta$ 增大，需更大法向力补偿；一旦所需切向力超出摩擦锥 $\|f_t\|\le\mu f_n$，笔滑落。仿真能精确补偿，真机接触误差放大后不可恢复——所以必须在奖励里**显式禁止倾斜**，把这类"仿真可行、真机致命"的解从策略空间剔除。
- **退化情形（解释为何立方体比笔简单）**：若物体有自然支撑（桌面/手掌），出现额外法向约束，$\sum f_{i,n}$ 不必全靠手指提供，gaiting 与水平约束都可放松——这正是 Dactyl/HORA 任务更易的结构性原因。

### 2.3 三阶段管线的信息流（principle-level，无代码堆砌）

```
(A) Oracle Policy (PPO, 特权观测)  ──训练──▶  能 finger gaiting 的特权策略
            │ rollout (s_t, a_t)
            ▼
(B) Student 预训练 (纯本体, 30 步历史)  ──模仿──▶  获得 motion prior（仿真内）
            │
            ▼
(C) Open-loop Replay：选 15 条 >800 步仿真轨迹的动作序列，真机开环回放
            │ human-in-the-loop 筛成功  →  <50 条真机 (obs, action)
            ▼
(D) Real Fine-tune：用真机成功轨迹微调纯本体 Student → 部署
```

- **(A) 为何特权**：笔位姿/点云/物理参数在仿真免费可得，让 Oracle 先解决"怎么转"这个最难的探索问题，不被部分可观测拖累。
- **(B) 为何不能直接 DAgger 蒸馏到位**：视触觉 Student 的 sim-to-real gap 太大、纯本体 Student 仿真内又难收敛——所以只把仿真蒸馏当作"拿 motion prior"，不指望它真机零样本可用。
- **(C) 为何开环有效**：open-loop controller 对 in-hand manipulation 出奇鲁棒——它迁移的是**动作序列**而非状态-动作映射，规避了闭环里观测分布偏移被反馈放大的问题（§2.5 符号陷阱）。
- **(D) 为何 <50 条够**：(B) 已给出强 motion prior，真机微调只需把动力学细节贴合，不需从零学 gaiting。

### 2.4 奖励塑形的物理含义

$$r = r_{rot} + \lambda_z\, r_z + \lambda_{energy}\, r_{energy}$$

| 项 | 形式 | 物理作用 | 去掉会怎样 |
|----|------|----------|-----------|
| $r_{rot}$ | $\propto \omega_z\,\Delta t$ | 奖励绕世界 $z$ 轴净旋转 | 无旋转信号，任务无定义 |
| $r_z$ | $-\lambda_z(z_{max}-z_{min})$ | 强制笔保持水平（见 §2.2 第 5 步） | 仿真可行→真机倾斜后滑落 |
| $r_{energy}$ | $-\lambda_e\|\tau\|^2$ | 抑制高频抖动/过激力矩 | 策略学到真机无法执行的剧烈动作 |

### 2.5 概念边界与符号陷阱

- **动作是位置目标不是力矩**：$a_t$ 经 PD 控制 $\tau=K_p(a_t-q)+K_d(\dot a_t-\dot q)$ 才变力矩。把动作当力矩会误判带宽与稳定性。
- **二值触觉 $\neq$ 接触力**：$c_t\in\{0,1\}^{20}$ 是接触有无，丢弃了力大小。这是刻意的信息瓶颈——二值量在 sim-to-real 中比连续力读数鲁棒得多。
- **特权 vs 部署观测的分布鸿沟**：$w_t$/点云/物理参数是三阶段管线**存在的唯一理由**；忽视这条会误以为"训练一个策略就能部署"。
- **$r_z$ 的 $z$ 是世界重力轴**，不是笔的长轴——惩罚的是笔偏离水平面，不是笔自转。
- **Open-loop "replay" 回放的是开环动作序列**，不是策略——成功率高说明"动作可迁移"，不代表"策略可迁移"。
- **"<50 条"指真机成功微调轨迹**，不是真机总交互量（开环回放本身也要真机执行）。

## 3. 训练、数据与实验 ← 实验与验证

### 3.1 实验设置

| 项目 | 细节 |
|------|------|
| 仿真环境 | IsaacGym, 4096 并行环境 |
| Oracle 算法 | PPO（clipped surrogate + GAE），~10B 环境步 |
| Student 架构 | Temporal Transformer (30 步本体历史) + MLP |
| 预训练数据 | 100K+ Oracle rollout $(s_t,a_t)$ |
| Fine-tune 数据 | **<50 条**真机成功轨迹 |
| 控制 | 30 Hz PD 位置控制 |
| 硬件 | Allegro Hand (16 DoF) + 5×4 二值触觉 |
| 物体 | 10+ 种笔状物体（不同质量/摩擦/尺寸） |

### 3.2 关键结果（真机）

指标：**RR** = Rotation Revolutions（旋转圈数），**Suc** = 成功率。

| 方法 | Object A | Object B | Object C |
|------|----------|----------|----------|
| Replay（纯开环回放） | 2.80 / 38% | 3.37 / 54% | 2.65 / 30% |
| V. Distill（视觉蒸馏） | 1.85 / 18% | - | - |
| P. Distill（纯本体蒸馏，无微调） | 1.57 / 0% | 1.57 / 0% | 1.57 / 0% |
| **Ours（三阶段）** | **3.43 / 55%** | **3.38 / 70%** | **3.50 / 68%** |

> [!important] 数字如何印证故事
> - **P. Distill 成功率全为 0%**：纯本体策略直接蒸馏到真机完全失败 → 证明 motion prior 不足以跨 gap，**真机 fine-tune (D) 不可省**。
> - **Replay 已能拿到 38–54%**：开环动作序列本身就有相当迁移性 → 直接验证 §1.2 隐喻"动作序列 > 状态映射"，也是数据引擎 (C) 成立的前提。
> - **Ours > Replay 且圈数更高**：闭环 Student 在开环基础上补了反馈纠偏 → 三阶段的边际价值是"把开环的开环误差用少量真机反馈闭合"。
> 泛化到未见物体（不同质量/摩擦/尺寸）成功率 50–80%，仅用 <50 条真机轨迹。

### 3.3 Ablation 因果链

`移除/改变 A → 指标 B 变化 → 因为机制 C 被破坏 → 对使用方法的启示 D`

| 移除/改变 | 指标变化 | 因果机制 C | 启示 D |
|---------|------|----------|--------|
| 多 Canonical Pose → 单一姿态 | 不稳定，学不到 gaiting | 单 pose 覆盖不到模式切换流形 $\sigma(t)$ 的完整周期（§2.2 第 5 步） | 初始状态分布要按 gaiting 相位设计，不能随机采 |
| 去触觉 | 性能下降 | 失去接触/脱离时机 → 手指协调退化为隐式估计 | 接触离散事件是 gaiting 的同步信号 |
| 去点云 | 性能下降 | Oracle 无几何 → 无法按笔形状选最优旋转轨迹 | 训练期几何信息值得用特权方式喂入 |
| 去特权物理 | 性能下降 | 无法区分轻/重、高/低摩擦 → 被迫单一保守策略 | 物理参数是 Oracle 因物施策的依据 |
| 去 $r_z$ 水平约束 | 仿真可行 → 真机失败 | 倾斜后重力矩超摩擦锥不可恢复（§2.2 第 5 步） | sim-to-real 约束要写进奖励而非寄望 DR |

### 3.4 工程约束与实验边界

- **Canonical Grasp 验证**：每种 grasp 须经物理验证（仿真 1000 步不掉落），无效初始态浪费 rollout。
- **$\lambda_z$ 区间**：$[0.5,1.0]$ 最佳——过小则倾斜（真机不鲁棒），过大则限制旋转自由度。
- **开环轨迹长度阈值 >800 步**：更短轨迹初始化误差累积，真机易失败。
- **PD 增益 sim-to-real 调整**：真机增益略低于仿真，补偿关节摩擦与腱弹性（对应 [[ControlTheory|降虚拟刚度容错]]）。
- **Temporal Transformer 历史 30 步（~1s@30Hz）**：性能与推理延迟的折中。
- **PointNet 100 点**：足以捕获笔形状，更多点不提升性能。

## 4. 核心洞见 ← 逻辑与价值 + 未来与结合

### 4.1 论文真正的 insight

四个 Lesson 其实是一个 insight 的四个切面：**当 sim-to-real gap 不可消时，不要强化策略去硬扛，而要重塑训练分布与数据来源，让"可迁移性"成为被显式优化/筛选的量。**
- 初始状态分布（Canonical Grasp）决定能不能学到 gaiting；
- 奖励约束（$r_z$）决定学到的解能不能迁移；
- 数据来源（Open-loop Replay）把"可迁移性"从假设变成可测量、可筛选的信号。

### 4.2 为什么这个设计有效

因为它把一个"不可观测、不可控"的 gap，转化成了一个"可观测、可筛选"的实验：开环回放的成功率**就是** gap 的直接读数（§6 把它用作诊断指标）。这比 DR 的"盲目加宽分布"信息量大得多。

### 4.3 什么时候会失效

- 若真机动力学差到**连开环都失败**（高 gap），(C) 产不出成功轨迹，整条链断裂。
- 若任务需要**实时反馈纠偏**（如外部扰动频繁），开环动作序列的容错性消失。
- 若物体姿态误差**可恢复**（有支撑面），三阶段的复杂度相对 zero-shot DR 不划算。

## 5. 替代方案与理论局限 ← 未来与结合

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | Open-loop Replay 无收敛保证——有效轨迹数取决于 gap 大小，无理论下界 | 用域适应理论（$\mathcal{H}\Delta\mathcal{H}$-divergence）量化可迁移性，给"几条轨迹够"一个界 |
| **算法** | 三阶段线性管线、错误不可回溯——开环失败率高则微调数据不足 | 闭环迭代：fine-tune 后的策略再收集数据反哺（DAgger 式滚动） |
| **工程** | Human-in-the-loop 筛选难规模化；Canonical Grasp 需手工设计 | 自动成功检测（力/位阈值）+ 课程化初始状态生成 |
| **任务** | 仅绕世界 $z$ 轴、笔状物体，无 SO(3) 全姿态 | 见 §7 领域空白：无支撑 + 任意轴 + 纯本体 |

## 6. 对用户研究的启发 ← 未来与结合

> [!tip] 与「灵巧手转笔 / Thumbaround」PPO 方案的直接对照

### 6.1 三阶段范式直接可复用
用户 PPO 转笔策略可按同一流程：**特权 Oracle → Open-loop 回放真机 → 成功轨迹 fine-tune 纯本体**，比 zero-shot DR 更安全、真机数据需求更低。

### 6.2 关键设计 → 转笔任务的映射

| 本文设计 | 转笔 (Thumbaround) 中变成什么 |
|----------|------------------------------|
| 6 种 Canonical Grasp | Thumbaround 的周期关键帧：snap 发力 → 滑过食指 → 收手复位，定义 4–6 个 canonical 初始态覆盖完整循环 |
| $r_z$ 水平约束 | 限制笔轴偏离目标平面的角度——仿真"花哨"旋转在真机会失败 |
| 二值触觉 $c_t$ | 食指/拇指接触事件作为相位切换的同步信号 |
| 特权物理参数 | Oracle 用笔质心/摩擦因物施策；Student 部署靠 motion prior 隐式代偿 |
| Open-loop 成功率 | **Gap 诊断指标**：若极低，应改善仿真而非加大 DR 强度 |

### 6.3 可验证实验建议
- **诊断实验**：固定 Student，扫 $\lambda_z\in\{0,0.5,1.0,2.0\}$，测开环回放真机成功率随 $\lambda_z$ 的曲线——若成功率在 $\lambda_z\!\approx\!0$ 时崩塌，证明 §2.2 第 5 步的摩擦锥机制是真机失败主因（falsifier：若曲线平坦则机制不成立）。
- **WMTS 接口**：把 Open-loop Replay 作为 WMTS pipeline 中 real-robot fine-tuning 阶段的数据引擎，用 Ensemble World Model 替代 human-in-the-loop 做成功判定。

### 6.4 不应过度外推的点
- "<50 条"是**笔状物体 + 强仿真 prior**下的结论，不能默认任何接触任务都这么省数据。
- 开环鲁棒性是 in-hand（手内闭合接触）的特性，移到自由空间抓取/装配不一定成立。

## 7. 与知识体系的联系 ← 未来与结合

### 7.1 各 Foundation 的数学链
- **[[Dynamics|Dynamics §2.3]]**：finger gaiting = 受控的接触模式切换 $\dot x=f_{\sigma(t)}(x,u)$；纯滚动是非完整 (Pfaffian) 约束，限制瞬时速度方向但不降 C-space 维数。
- **[[ContactMechanics|ContactMechanics §3]]**：$r_z$ 的物理本质——倾斜时 $\tau_g=mgl\sin\theta$ 增大，所需切向力超出摩擦锥 $\|f_t\|\le\mu f_n$ 即滑落。
- **[[ReinforcementLearning|PPO §3]]**：4096 并行环境降低 $\hat A_t$ 方差，clip $\epsilon$ 保证长 horizon 多模态 gaiting 策略的更新稳定；[[ReinforcementLearning|RL §5]]：用 Open-loop Replay 替代 DR 的 sim-to-real 路线。
- **[[ControlTheory|ControlTheory §3]]**：30 Hz PD + 真机降增益 = 刚度-柔顺权衡。
- **[[Dynamic Non-Prehensile Manipulation]]**：转笔是依赖惯性/动量的动态非抓取操作的代表 benchmark。

### 7.2 in-hand rotation 领域级综述（本篇的横向坐标）

把同簇论文放到三条正交轴上，能看出领域的演进主线，也能看出**还没人占的格子**：

| 论文 | 物体/支撑 | 旋转自由度 | 感知模态 (部署) | Sim-to-Real 路线 | 注入的核心先验 |
|------|-----------|-----------|-----------------|------------------|----------------|
| OpenAI Dactyl | 立方体（有支撑） | SO(3) 重定向 | 视觉追踪 | Zero-shot DR | DR 覆盖足够宽 |
| [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)|HORA]] | 多形状（指尖上） | 绕 z | 纯本体 | 在线适应 RMA | 真机可在线估 extrinsics |
| [[RotateIt - General In-Hand Object Rotation with Vision and Touch|RotateIt]] | 多形状 | 绕 z | 视觉+触觉 | 蒸馏 | 视触觉互补 |
| [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing|Robot Synesthesia]] | 多形状 | 绕 z | 视触觉融合 (点云化触觉) | 蒸馏 | 触觉与视觉共享几何表征 |
| [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch|Touch Dexterity]] | 多形状 | 绕 z | **纯触觉**（不看） | DR | 接触模式足以驱动旋转 |
| [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch|AnyRotate]] | 多形状 | **任意轴** | 稠密触觉 | 蒸馏 + gravity-invariant | 重力不变 + 稠密触觉 |
| [[Learning Human-like Finger Gaiting on an Anthropomorphic Hand|Finger Gaiting]] | 多形状 | 绕 z | 本体+触觉 | DR + 课程 | 人手式 gaiting 模式库 |
| **本篇 Spin Pens** | **笔（无支撑）** | 绕 z 多圈 | 纯本体 | **三阶段 Open-loop Replay** | Canonical Grasp + $r_z$ + 数据引擎 |

> [!note] 领域级 insight（本篇升级新增）
> 1. **难度由三轴决定**：in-hand rotation 的真实难度不是"形状多不多"，而是 ⟨是否有自然支撑⟩ × ⟨是否需 SO(3) 全姿态⟩ × ⟨感知可观测性⟩。Dactyl 难在 SO(3)，AnyRotate 难在任意轴，**Spin Pens 难在"无支撑 + 动态平衡"**——它用"退回单轴 + 纯本体"换取攻克无支撑。
> 2. **sim-to-real 路线在分化**：DR（覆盖）→ RMA（在线适应）→ 蒸馏（特权压缩）→ **Open-loop Replay（离线筛选）**。前三条都试图让"一个策略"跨 gap，本篇承认 gap 不可消、改为筛"可迁移的动作"。这是方法论上的范式差异，不只是 trick。
> 3. **开启的领域空白**：表里**「无支撑 + 任意轴 + 纯本体」这一格至今空白**。Spin Pens 解决了无支撑但退回单轴，AnyRotate 解决了任意轴但物体有支撑。把两者合流（无支撑笔的任意轴翻转 + 纯本体部署）是 WMTS / 转笔项目可切入的、有领域显示度的开放问题——其难点恰好落在本篇 §2.2 推导的摩擦锥 + 切换系统交汇处。

## References

- [[EUREKA: Human-Level Reward Design via Coding Large Language Models]] — 用 LLM 设计转笔奖励，与本文手工 $r_z$ 形成对照
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 追踪人类参考的灵巧操作，可作 gaiting 参考来源
- [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] — RL 中的阻抗控制动作空间
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] · [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] · [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] — 见 §7 领域综述
