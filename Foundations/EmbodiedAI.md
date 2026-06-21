---
tags:
  - foundation
  - embodied-ai
  - vla
  - robot-learning
  - simulators
aliases:
  - 具身智能
  - VLA Models
  - Robot Learning Systems
created: 2026-02-02
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[Optimization]]"
  - "[[SignalProcessing]]"
---

# 具身智能：从"会看会说"到"能安全改变世界"

# Embodied AI: From Seeing-and-Speaking to Safely Changing the World

> [!tip] 相关领域（本讲是"栈顶集成层"，消费所有其他 Foundation）
> - [[ReinforcementLearning]] — VLA 的 RL 后训练、sim-to-real、真机闭环
> - [[RepresentationLearning]] — 扩散/Flow Matching 动作头、Vision Foundation Models
> - [[ControlTheory]] — 分层控制：VLA 出子目标、低层阻抗/MPC 执行
> - [[Dynamics]] / [[Optimization]] — 仿真器的物理与求解；MPC
> - [[SignalProcessing]] / [[ContactMechanics]] — 触觉传感与接触
>
> **贯穿母题（本讲的"主角"）**：**"把桌上的红杯子端给我"——语言指令取物 (language-conditioned fetch)**。一句日常指令，要走完"听懂→定位→规划→抓取→搬运→放置→确认"的全栈闭环，把具身智能每一层都点亮，我们让它贯穿全篇。

## 0. 母题与理论大厦构建路线：从语义到安全的物理交互

具身智能 (Embodied AI) 是基于**物理实体**感知与行动的智能：它必须处理纯软件 AI 不面对的**物理约束**（连续性、不可逆性）、**感知-行动闭环**（实时反馈）、**多模态融合**（视/触/本体）。

> [!abstract] 为什么用"端红杯子给我"做贯穿母题？
> 它的理论骨架不能停在"VLA = 视觉 + 语言 + 动作"的定义层，而应理解为一个**逐层收紧的闭环**：把开放世界语义压成可执行任务 → 落到连续动作 → 用底层控制和真实反馈保证物理安全。**"端红杯子"** 恰好逐层激活：
> - "红杯子"而非"蓝杯子" → **任务语义 grounding**；
> - 杯子在哪、与手如何相对 → **空间表征**（CLIP/DINO/SAM + 3D 点云）；
> - 怎么伸手、正着抓还是侧着抓 → **动作生成**（多峰，AR/Diffusion/Flow Matching）；
> - 别把杯子捏碎、别洒出来 → **控制执行**（阻抗/MPC、限幅）；
> - 这次没端稳，下次怎么变好 → **数据飞轮**。
>
> 全讲每引入一个组件，我们都回到这只红杯子："**它让'端杯子'这件事更可靠、更安全了吗？**"

| 层级 | 核心问题 | 理论工具 | 端红杯子的检查点 | 讲稿位置 |
|:--|:--|:--|:--|:--|
| **任务语义层** | 指令如何变可验证目标？ | 语言 grounding、任务图、前/后置条件 | "红杯子"拆成 找→抓→端→放 | §1 |
| **空间表征层** | 目标在哪、与手如何相对？ | 3D 表征、点云、SDF、物体中心系 | 不只识别"杯"，要定位杯壁/可抓边 | §1、§3 |
| **动作生成层** | 连续动作如何表达多峰方案？ | AR token、Diffusion、Flow Matching、chunk | 正抓/侧抓均可，均值动作常无效 | §1、§2 |
| **控制执行层** | 大模型动作如何变稳定力学交互？ | 阻抗/导纳、MPC、安全过滤、频率分层 | VLA 不应直接接电机，要低层闭环+限幅 | §2 |
| **数据飞轮层** | 系统如何从失败持续变强？ | IL→offline RL→online RL、人类校正、world model | 真机失败回流成可诊断数据 | §2 |

> [!important] Foundation 级判断标准
> 一个 Embodied AI 系统，只有能回答"**语义目标如何约束物理状态、动作表示如何尊重执行器带宽、反馈如何修正分布外接触**"，才真正进入机器人理论大厦——否则只是把 VLM 接到 action head 的工程拼接。

> [!note] 本讲在知识图谱中的位置（它是所有 Foundation 的汇聚点）
> ```
> [[RepresentationLearning]](动作头/视觉表征) ┐
> [[ReinforcementLearning]](后训练/sim2real) ┤
>      [[ControlTheory]](低层力控)        ├──> 【EmbodiedAI = 全栈集成】──> 真机执行"端红杯子"
> [[Dynamics]]/[[Optimization]](仿真/MPC)  ┤
> [[SignalProcessing]]/[[ContactMechanics]](触觉/接触) ┘
> ```
> 读法：具身智能不"产生"新的底层理论，而是把其余十门 Foundation **编排成一个能安全改变世界的闭环**。§7 的回扣会显式追踪每门 Foundation 如何为"端红杯子"出力——这也是通往 [[taxonomy|知识图谱]] 的桥。

---

## 1. Vision-Language-Action (VLA)：把"看-说-做"统一

> [!tip] 本节四拍
> **直觉**（"端红杯子"要把一句话直接变成手的动作）→ **推导**（VLA 架构：视觉编码→语言骨干→动作解码）→ **对比**（三种动作输出：AR vs Diffusion vs Flow Matching）→ **落点**（分层双系统：慢推理 + 快控制）。

### 1.1 核心架构

VLA 把视觉、语言、动作统一到端到端网络，实现从感知到执行的直接映射：

```
  Vision Encoder (ViT/CLIP) ─┐
                             ├─> Multi-Modal Fusion ─> Action Decoder (Diffusion/AR/Flow)
  Language Backbone (LLM) ───┘     (Cross-Attention)         │
       ▲ "把红杯子端给我"                                    ▼ 连续动作/动作 token
```

### 1.2 经典 VLA 演进

| 模型 | 机构 | 参数 | 关键创新 |
|:--|:--|:--|:--|
| **RT-1** | Google | 35M | Transformer 动作 tokenization |
| **RT-2** | Google | 55B | VLM 直接生成动作（动作作为文本 token） |
| **OpenVLA** | Stanford | 7B | 开源标杆，Prismatic VLM backbone |
| **π₀** | Physical Intelligence | 3.3B | Flow Matching + VLM |
| **Octo** | UC Berkeley | 93M | Transformer + Diffusion |
| **RDT-1B** | THU | 1.2B | 双臂，Scalable Diffusion Transformer |
| **SpatialVLA / 3D-VLA** | — | — | 空间推理 / 3D 场景表征 |
| **LaST0** | HKU/ByteDance | 7B | 潜在时空 CoT，MoT 双系统 |

### 1.3 三种动作输出范式（横向对比）

| 范式 | 公式 | 优点 | 缺点 | 代表 |
|:--|:--|:--|:--|:--|
| **自回归 (AR)** | $a_t=\arg\max_a P(a\mid s_{1:t},g)$ | 推理快、与文本统一 | 离散化损精度 | RT-1/2, OpenVLA |
| **扩散 (Diffusion)** | $a_t=\mathcal D_\theta(\epsilon,s_t,g)$ | 动作平滑、多峰 | NFE 高（100–1000）、延迟大 | Diffusion Policy, RDT |
| **流匹配 (Flow Matching)** | $a_t=x_0+\int_0^1 v_\theta(x_\tau,\tau,s_t)d\tau$ | 直线最优传输、NFE 极低（4–10）、兼顾多峰与实时 | 较新 | π₀, LaST0, OmniXtreme |

> [!note] 设计权衡（接 [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|表征学习的扩散/Flow Matching]]）
> "端红杯子"可正抓也可侧抓（多峰）——AR 的离散化与确定性回归都易学成无效均值动作；扩散/Flow Matching 能精确建多峰。混合策略：粗调用 AR、细调用 Flow Matching（如 LaST0 的 MoT 双系统）。**这正是 [[RepresentationLearning#2.1 两大顽疾：协变量漂移与多峰|表征学习"逃离均值坍缩"]]主线在 VLA 的延续。**

### 1.4 分层双系统：慢推理 + 快控制

受人类"快慢系统"启发，现代 VLA 常用双层设计：

```
System 2 (慢, 1–10 Hz): 大 VLM 任务理解+规划 → 子目标序列/语言指令
        │
System 1 (快, 50–200 Hz): 轻量策略 (Diffusion/Flow) → 连续动作轨迹
```

> [!important] 这与 [[ControlTheory|分层控制]]、灵巧操作的"频率困境"是同一思想
> 高层任务规划 + 低层反馈控制——VLA 出"去抓红杯子"，低层阻抗控制器保证"接触杯壁时不捏碎"。**慢/快双系统直接映射灵巧操作的频率困境**：quasi-static 相位（慢系统规划握姿转换）vs dynamic 相位（快系统反应式力控，见 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|控制频率自适应]]、[[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|采样带宽]]）。

> [!tip] LaST0：隐式双系统（[[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]]）
> 与显式分层不同，LaST0 用 **Mixture-of-Transformers (MoT)** 在同一 VLM 内把 QKV/FFN/LN 参数解耦为慢推理专家与快动作专家，梯度互不干涉、避免特征干扰；两专家共享注意力 + KV Cache（慢专家的 $K,V$ 冻结入 cache、快专家 $O(1)$ 提取）；带锁均摊同步调度（$\kappa=4$，均摊 ~15.4 Hz）；**Latent CoT** 在隐空间（而非文本空间，避免延迟）自回归预测未来 2D 语义 + 3D 几何 + 本体状态。结果：10 项真实任务 +13–14% SR，速度 14× 于显式 CoT。

---

## 2. 机器人学习范式与 VLA 后训练

> [!tip] 本节四拍
> **直觉**（"端红杯子"可以试错学(RL)、模仿学(IL)、模型预测(MPC)、或端到端(VLA)）→ **推导**（四范式的数据与适用）→ **对比**（IL 数据高效但泛化弱 vs RL 鲁棒但样本贵）→ **落点**（仅 IL 不够，RL 后训练是 VLA 走向实用的关键）。

### 2.1 四范式对比

| 范式 | 核心 | 数据 | 典型 | 与灵巧操作关联 |
|:--|:--|:--|:--|:--|
| **RL** | 试错 | 仿真交互 | PPO/SAC/TD3 | sim-to-real、接触丰富（见 [[ReinforcementLearning]]） |
| **IL** | 专家示范 | 真机遥操 | BC/ACT/Diffusion | 数据高效、泛化受限（见 [[RepresentationLearning]]） |
| **MPC** | 模型预测 | 动力学模型 | iLQR/MPPI | 精确但建模难（见 [[Optimization]]） |
| **VLA** | 端到端 | 大规模多任务 | RT 系列/OpenVLA | 语言条件任务 |

这四范式不是互斥的——现代系统把它们**编排**起来：VLA 提供语言条件的端到端先验，IL 打底，RL 后训练突破模仿天花板，MPC/控制保底层安全。

### 2.2 Sim-to-Real：从仿真到真实

```
Simulator (Isaac/MuJoCo) ──Domain Randomization──> Policy Training ──> Real Robot
   动力学(质量/摩擦/阻尼)、视觉(光照/纹理)、传感器(噪声/延迟) 全部随机化
```

DR 把动力学（质量、摩擦、阻尼）、视觉（光照、纹理、相机位姿）、传感器（噪声、延迟、dropout）随机化，逼策略学不变特征。**但这只是 sim-to-real 的一面**——完整的诊断框架（按 MDP 四要素拆 gap、System ID vs DR vs 在线自适应）见 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL §9]]，其泛化理论（域适应界）见 [[RepresentationLearning#6.5 Sim-to-Real 的泛化视角：域适应|表征学习 §6.5]]。**端红杯子的 sim-to-real 难点**：真杯子的重量分布、桌面摩擦、杯壁柔顺都与仿真不同。

### 2.3 VLA 后训练：从模仿到强化

> [!important] 关键共识：仅靠 IL 不足以鲁棒部署，RL 后训练是 VLA 走向实用的关键
> VLA 在大规模 IL 数据上预训练后，需 RL 后训练突破模仿质量天花板。四条互补路径：

| 路径 | 代表 | 核心 | 适用 |
|:--|:--|:--|:--|
| **Real-World RL** | [[RL-100 - Performant Robotic Manipulation with Real-World RL\|RL-100]] | IL→Offline→Online 三阶段 | 大规模端到端改进，无 sim2real gap |
| **World Model RL** | [[WMPO - World Model-based Policy Optimization for VLA\|WMPO]] | 像素空间世界模型 + GRPO | 零真实交互成本 |
| **Lightweight Online RL** | [[RLT - Precise Manipulation with Efficient Online RL Tokens\|RLT]] | VLA→RL Token(信息瓶颈)→轻量 actor-critic | 部署时 15 分钟快速微调精密阶段 |
| **Experience-Based RL** | [[RECAP - A VLA that Learns from Experience\|RECAP (π₀.6)]] | Demos→Corrections→RL，advantage-conditioned | 经验闭环持续自改进 |

四路在成本与范围上互补，详见 [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]] 与 [[ReinforcementLearning#10.2 世界模型 RL：隐空间 vs 像素空间|RL §10.2]]。**这正是"端红杯子"从"能端"到"端得稳"的关键一跃**——IL 让它学会端，RL 后训练让它在各种杯子/桌面上都端得稳。

---

## 3. 机器人视觉基础模型

> [!tip] 本节四拍
> **直觉**（"红杯子"三个字要落到像素上的哪一块？）→ **推导**（语义/对应/几何三层特征金字塔）→ **对比**（CLIP 语义 vs DINO 对应 vs SAM 分割）→ **落点**（机器人还需 affordance-aware 表征，不止识别）。

| 模型 | 类型 | 输出 | 机器人用途 |
|:--|:--|:--|:--|
| **CLIP** | 视觉-语言对齐 | 对齐特征 | 开放词汇识别（"红杯子"↔像素） |
| **DINO/DINOv2** | 自监督视觉 | dense 特征 | 对应点匹配、部件理解 |
| **SAM/SAM2** | 分割 | mask | 物体分割、视频追踪 |
| **Grounding-DINO** | 开放词汇检测 | bbox | 语言引导定位 |
| **FoundationPose** | 姿态估计 | 6DoF pose | 物体位姿 |
| **Depth Anything** | 单目深度 | depth map | 深度感知 |

三层**特征金字塔**：高层语义（CLIP："红杯子"）→ 中层对应（DINO：杯把/杯身部件）→ 低层几何（SAM + Depth：3D 点云）。**端红杯子**先用 CLIP/Grounding-DINO 定位"红杯子"、再用 SAM 分割、再用 Depth 重建 3D 抓取点。

> [!note] 与 [[RepresentationLearning]] 的边界
> Foundation Models 提供强大预训练表征、降低下游数据需求；但机器人还需**动作相关 (affordance-aware) 表征**——"哪里能抓、怎么抓"不止是"这是什么"。这呼应 [[RepresentationLearning#3.2 通用视觉表征的局限：具身差异|表征学习的具身差异]]：通用视觉表征缺接触力学信息。

---

## 4. 仿真器生态

> [!tip] 本节四拍
> **直觉**（真机训练太贵太危险，先在仿真里学端杯子）→ **推导**（不同引擎的物理-速度-可微权衡）→ **对比**（Isaac 并行 vs MuJoCo 精确 vs Genesis 可微）→ **落点**（仿真质量决定 sim-to-real 上限）。

| 仿真器 | 引擎 | 优势 | 适用 |
|:--|:--|:--|:--|
| **Isaac Lab** | PhysX 5 | GPU 并行、官方支持 | 大规模 RL 训练 |
| **MuJoCo** | 自研 | 精确、轻量 | 精细操作、基准（见 [[Dynamics\|接触求解]]） |
| **SAPIEN** | PhysX | 易用、灵活 | 快速原型 |
| **Genesis** | 多后端 | 4300 万 FPS、**可微** | 下一代研究 |
| **PyBullet** | Bullet | 免费、社区大 | 教学入门 |

**Isaac 生态**：Isaac Lab（RL 框架）+ Isaac Sim（渲染）+ Omniverse（平台），底层 PhysX 5（GPU Tensor API、可变形体、粒子系统），常用环境 legged_gym/bi-dexhands。**MuJoCo 生态**：MuJoCo Playground（dm_control 继任）、MJX（JAX 加速）、Brax（可微）、Robosuite。

> [!important] 仿真质量决定 sim-to-real 上限
> Insight：① **Scaling Law**——机器人基础模型如 LLM 般，更多数据+更大模型→更好泛化；② **可微仿真是下一前沿**（梯度直接穿过物理，接 [[Dynamics#9. 适配层：可微物理与神经动力学|可微物理]]、[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|可微接触]]）；③ **数据飞轮**——采集→训练→部署→自动采集的闭环是规模化关键。选型：入门 MuJoCo+gymnasium、大规模 RL Isaac Lab、前沿 Genesis。

---

## 5. 硬件与数据基础设施

> [!tip] 本节四拍
> **直觉**（端红杯子的策略要么来自遥操演示、要么来自仿真——数据从哪来？）→ **推导**（遥操系统、触觉传感、大规模数据集）→ **对比**（ALOHA 双臂 vs UMI 手持 vs GELLO 外骨骼）→ **落点**（数据基础设施是数据飞轮的物理底座）。

**数据采集**：ALOHA（双臂遥操，低成本开源）、UMI（手持教学，无需机器人）、GELLO（外骨骼，直觉操作）、TeleMoMa（多模态 VR）。**触觉传感**（与 [[SignalProcessing]]、[[ContactMechanics]] 紧密相关）：GelSight 系列（视触觉，把触觉变视觉问题）、电子皮肤（分布式压力）、关节力矩传感器（力控基础）。**关键数据集**：Open X-Embodiment（100 万+，多平台）、DROID（76K，Franka 真机）、RH20T（20T，多平台）。

> [!note] 数据飞轮的物理底座
> 这些硬件与数据集是 §0 "数据飞轮层"的物理实现——没有规模化的真机数据采集，"从失败中持续变强"就是空话。端红杯子要泛化到千百种杯子，靠的正是 Open X-Embodiment 级的数据规模 + 数据飞轮的闭环回流。

---

## 6. Embodied AI for X（领域延伸）

具身智能的原理可迁移到操作之外的领域，但**物理安全约束的权重各不相同**：

- **医疗机器人**：接触人体要求严格力控（与 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]）、微创手术高精度、康复自适应；分自主等级 L0–L5。
- **无人机 (UAV)**：仿真器 AirSim/Flightmare/AerialGym；控制分层"任务规划→路径规划→姿态控制 (PID/LQR)"——与 §1.4 的 VLA 双系统同构。
- **自动驾驶**：端到端（Tesla FSD）vs 模块化（Apollo/Autoware）之争，正是 §2.1 "端到端 VLA vs 模块化"在另一具身领域的镜像。

> [!tip] 一以贯之的"分层 + 端到端之争"
> 无论操作、飞行还是驾驶，都面对同一张力：**端到端（数据驱动、泛化但难解释）vs 分层模块化（可解释、安全但难扩展）**。当前主流答案都是**分层双系统**——高层端到端语义、低层模块化安全控制。这是具身智能跨领域的统一范式。

---

## 7. 知识回扣与跨域大综合：一只红杯子串起整座 Foundation 大厦

> [!abstract] 用"端红杯子"把全部 11 门 Foundation 复述一遍（这是全知识库的总回扣）
> 具身智能不产生新的底层理论，而是把其余十门 Foundation 编排成一个能安全改变世界的闭环。让我们跟着"把桌上的红杯子端给我"走一遍——**每一步都点名一门 Foundation**：
> 1. **听懂指令**："红杯子"→可执行任务图（本讲 §1 任务语义）；
> 2. **定位杯子**：CLIP/SAM 找"红杯子"、Depth 重建 3D 点云（[[RepresentationLearning|表征学习]]的点云/Foundation Models、[[ComputationalGeometry|计算几何]]的 SDF/最近点）；
> 3. **规划伸手轨迹**：在杂物间无碰撞够到杯子（[[Optimization|优化]]的 TrajOpt/SDF 势场、[[ComputationalGeometry|几何]]的 GJK/EPA）；
> 4. **决定怎么抓**：正抓/侧抓多峰、力闭合（[[RepresentationLearning|扩散策略]]、[[ContactMechanics|接触力学]]的力闭合/摩擦锥、[[InformationTheory|信息论]]的"摸一下确认"）；
> 5. **稳稳抓住不捏碎**：阻抗/力位混合控制（[[ControlTheory|控制论]]的阻抗=熵即柔顺、[[Dynamics|动力学]]的有效惯量）；
> 6. **判断有没有打滑**：触觉滑移检测（[[SignalProcessing|信号处理]]的 STFT/小波、[[ContactMechanics|接触]]的 stick-slip）；
> 7. **端起来搬运**：水/质心漂移下的实时重规划（[[Optimization|MPC]]、[[StochasticProcess|随机过程]]的 MPPI/belief）；
> 8. **应对不确定**：杯子比预想重/滑（[[StochasticProcess|随机过程]]的 GP/在线辨识、[[ReinforcementLearning|RL]]的 RMA/域随机化）；
> 9. **整段策略**：VLA 端到端 + RL 后训练（[[ReinforcementLearning|RL]]、本讲 §2）；
> 10. **从失败学习**：没端稳→回流数据→变强（数据飞轮，本讲 §5）。
>
> **一只红杯子，调动了全部十一门 Foundation。** 这就是具身智能作为"栈顶集成层"的本质——它是知识图谱所有节点的汇聚点。

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 端红杯子角色）
> | 层 | 核心问题 | 关键工具 | 端红杯子的哪一环 |
> |:--|:--|:--|:--|
> | §1 任务语义/VLA | 一句话变动作 | VLA、AR/Diffusion/Flow、双系统 | 听懂"红杯子"→出动作 |
> | §2 学习范式 | 怎么学/后训练 | IL→RL、sim2real、RL 后训练 | 从"能端"到"端得稳" |
> | §3 视觉基础模型 | "红"落到哪块像素 | CLIP/DINO/SAM 金字塔 | 定位红杯子 |
> | §4 仿真器 | 在哪练 | Isaac/MuJoCo/Genesis | 仿真里先学会端 |
> | §5 硬件数据 | 数据从哪来 | ALOHA/UMI、Open-X、触觉 | 数据飞轮底座 |
> | §7 跨域综合 | 各 Foundation 如何协同 | 全栈编排 | 一只杯子调动全部 |

> [!tip] 三条贯穿全讲的"暗线"（也是整座知识图谱的暗线）
> 1. **分层是统一范式**：VLA 双系统、医疗/UAV/驾驶的"端到端 vs 模块化"、控制的高低层——都是"慢推理语义 + 快反馈控制"。
> 2. **具身智能是集成而非新理论**：它的力量来自把十门 Foundation 正确编排（§7 综合）——这也是为什么它在知识图谱里是所有节点的汇聚点。
> 3. **数据飞轮闭合一切**：感知→规划→执行→失败诊断→数据回流→更强策略，是 sim-to-real（[[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL §9]]）与规模化的共同引擎。

> [!note] 跨领域链接（双向、点对点——本讲是汇聚点，链接最密）
> - **↔ [[RepresentationLearning]]**：扩散/Flow Matching 动作头（§1.3）；Vision Foundation Models（§3）；具身差异。
> - **↔ [[ReinforcementLearning]]**：VLA 后训练 RL-100/WMPO/RLT/RECAP（§2.3）；sim-to-real（§2.2）；RMA。
> - **↔ [[ControlTheory]]**：分层双系统=分层控制（§1.4）；低层阻抗保护杯子（§6）。
> - **↔ [[Optimization]] / [[Dynamics]]**：仿真器物理与 MPC（§4）；可微仿真。
> - **↔ [[SignalProcessing]] / [[ContactMechanics]]**：触觉传感（§5）；滑移检测；接触安全。
> - **↔ [[InformationTheory]] / [[StochasticProcess]] / [[ComputationalGeometry]]**：主动感知、belief、几何定位（§7 综合）。
> - **↔ [[taxonomy]]**：本讲的"端红杯子"全栈综合是知识图谱的活样例。

---

## 8. 学习资源与相关论文

> [!tip] 实践路径
> **入门（约 1 周）**：① 用 RoboTwin 2.0 走通策略训练全流程（数据生成→BC/Diffusion 训练→仿真评测）；② 读 Diffusion Policy 论文 + 代码；③ 有条件则真机部署。**进阶**：深入 [[ReinforcementLearning]] 基础 → 研究 VLA 架构（RT-2/OpenVLA）→ 探索 Sim-to-Real → 关注 3D 感知与触觉融合。
>
> **开源库**：LeRobot（HF 机器人库）、OpenVLA（VLA 训练）、openpi（π₀）、RoboTwin 2.0（双臂仿真）、Isaac Lab（RL 框架）。
> **社区**：[Lumina 具身智能](https://lumina-embodied.ai/)、[Embodied-AI-Guide](https://github.com/TianxingChen/Embodied-AI-Guide)、[Simulately Wiki](https://simulately.wiki/)。
> **会议**：Science Robotics / TRO / IJRR / RSS / CoRL；NeurIPS / ICML / ICLR / CVPR；ICRA / IROS / RAL。

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的具身智能核心主题。

### Diffusion Policy & 生成式策略
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] — 规划引导扩散，双臂
- [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] — Rodrigues 正运动学作 denoising backbone
- [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] — 仿真数据自动生成
- [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] — 物理驱动数据生成

### Sim-to-Real & 迁移学习
- [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] — 可组合 Sim-to-Real
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] — 仿真增强真实演示
- [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] — Real-to-Sim-to-Real
- [[A Survey of Sim-to-Real Methods in RL|Sim-to-Real Survey]] — MDP 四要素分类框架
- [[Grounded Action Transformation|GAT]] — 仿真器 grounding 奠基（AAAI 2017）

### 触觉与多模态感知
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] — 视触觉遥操作
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] — 视触觉联觉表征
- [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch]] — 纯触觉手内操作

### VLA Post-Training 与 World Model RL
- [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]] — 潜在时空 CoT，MoT 双系统
- [[WMPO - World Model-based Policy Optimization for VLA|WMPO]] — 像素空间世界模型 + GRPO
- [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] — 真实世界 RL，denoising sub-MDP，100% 成功率
- [[RECAP - A VLA that Learns from Experience|RECAP (π₀.6)]] — Experience-Based RL 三阶段经验闭环
- [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] — Flow Matching 预训练 + actuation-aware 残差 RL
- [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation|DexHiL]] — 首个臂手系统 HiL VLA 后训练，干预感知采样 + DAgger

### 3D 世界模型与空间智能
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 动力学感知表征条件化 RL
- [[空间智能作为机器人的结构化表征|PointWorld]] — 3D Flow 统一状态-动作表征，载体无关世界模型
- [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation|RoboTwin 2.0]] — 5 轴 DR 双臂数据生成

### 物理感知预训练与运动生成
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]] — Dynamics-lifted 几何预训练
- [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]] — RL Token 信息瓶颈，15 分钟真实数据 3× 加速
- [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]] — Physics-prefix 引导，课程 MoE + 262D 原生扩散 + PPO 微调
