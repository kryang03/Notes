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

> [!note] "对齐 (alignment)" 到底把什么对上了——三层逐级收紧
> 架构图里的箭头掩盖了 VLA 最核心的机制：**视觉、语言、动作三种异构信号，如何被塞进同一个可运算的向量空间**。所谓"对齐"不是一步到位，而是三层逐级收紧（对应 §0 从语义到物理的逐层收敛）：
>
> 1. **模态对齐 (modality alignment)**：视觉 patch 与语言 token 各自被编码成 $d$ 维向量（$d\approx 1024\text{–}4096$，无量纲的语义坐标）。CLIP 式对比预训练让"红杯子"这串文字向量 $\mathbf v_{\text{txt}}$ 与红杯子图像向量 $\mathbf v_{\text{img}}$ 的余弦相似度 $\cos(\mathbf v_{\text{img}},\mathbf v_{\text{txt}})\to 1$、与蓝杯子向量 $\to 0$——这一步才保证"红"这个字能落到像素上的红色区域（详见 §3 与 [[RepresentationLearning#3. 表征的演进：从重构到对比到基础模型|表征学习的对比预训练]]）。
> 2. **空间对齐 (spatial grounding)**：语义还要绑到 3D 坐标。**cross-attention 是这一步的运算核心**——query 向量 $\mathbf q$（来自语言/动作 token）与 key 向量 $\mathbf k$（来自视觉 token）做缩放点积 $\mathbf q^\top\mathbf k/\sqrt d$（分母 $\sqrt d$ 防高维点积方差过大导致 softmax 饱和），点积越大表示"这个词该关注这块像素"；softmax 归一化成权重后按权重取 value，即把"红杯子"的语义**搬运**到对应视觉特征上。这是"语言查询视觉"的物理实现。
> 3. **动作对齐 (action grounding)**：最后把融合特征映射到动作。RT-2 的关键洞察是**把动作也当成 token**——7 维末端位姿增量 $(\Delta x,\Delta y,\Delta z,\Delta\text{roll},\Delta\text{pitch},\Delta\text{yaw},\text{grip})$（前三单位 m、中三单位 rad、末位夹爪开合）各离散成 256 档，复用 VLM 词表里 256 个现成整数 token。这样 VLM 预训练学到的"语义→符号"映射能力**零成本迁移**到"语义→动作"，无需从零训练动作头；代价即 §1.3 要算的离散化误差。
>
> **为什么对齐是 VLA 的命门**：端红杯子若"红"没对齐到正确像素（模态错）、或杯子 3D 位姿没对齐（空间错）、或抓取方向没对齐到夹爪指令（动作错），任一层断裂，后面再强的控制器都救不回来。对齐是 §0"语义目标约束物理状态"主线的**第一道关卡**。

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

> [!note] 三种范式的机制拆解（把表里的公式每个符号讲透——这是最易跳步处）
> 表格给了公式却没说清"为什么 AR 损精度、为什么扩散慢、为什么 Flow Matching 又快又准"。逐个拆：
>
> **① 自回归 AR**：$a_t=\arg\max_a P(a\mid s_{1:t},g)$
> - 符号：$a_t$ 是 $t$ 时刻动作（如 7 维末端增量，单位 m 与 rad）；$s_{1:t}$ 是到 $t$ 为止的观测序列；$g$ 是语言目标 (goal)；$P(\cdot)$ 是 VLM 输出的动作 token 概率。
> - 连续动作先**离散化**：每维值域切成 $K$ 档（RT-2 取 $K=256$），档宽 $\Delta=(a_{\max}-a_{\min})/K$（单位同该维动作）。量化误差有硬上界 $|a-\hat a|\le\Delta/2$——**精度天花板由档数 $K$ 决定**，这就是"离散化损精度"的物理来源。
> - "自回归"指逐维展开 $P(a\mid\cdot)=\prod_j P\!\big(a^{(j)}\mid a^{(1:j-1)},s_{1:t},g\big)$，每维一次轻量解码，7 维仅 7 次前向，故"推理快、与文本统一"。
>
> **② 扩散 Diffusion**：$a_t=\mathcal D_\theta(\epsilon,s_t,g)$
> - 符号：$\epsilon\sim\mathcal N(0,I)$ 是纯高斯噪声起点（无量纲标准化动作），$\mathcal D_\theta$ 是参数为 $\theta$ 的去噪器，$s_t$/$g$ 同上。
> - 机制：从噪声出发**反向去噪 $T$ 步**得干净动作，每步用网络估计噪声/分数 $\nabla_a\log p(a)$（score 场，指向数据密度升高方向），沿概率流回退一小步。**多峰天然被支持**：score 场在每个数据模式附近都有吸引域，落到正抓还是侧抓由初始 $\epsilon$ 决定，故不塌成无效均值。
> - **观测如何进入去噪（VLA 动作头的命门，最易被略过）**：上一行的 score 写成无条件 $\nabla_a\log p(a)$ 是简化——VLA 动作头真正要采的是**观测条件**分布 $\nabla_a\log p(a\mid s_t,g)$（$s_t$ 是当前视觉/本体观测，$g$ 是"红杯子"语言目标）。把观测注入采样方向的标准手段是 **Classifier-Free Guidance (CFG)**：训练时按概率丢弃条件、同一网络兼学条件与无条件两个 score，采样时按 $\nabla_a\log p_w=\nabla_a\log p(a)+w\big[\nabla_a\log p(a\mid s_t,g)-\nabla_a\log p(a)\big]$ 线性外插（引导权重 $w\ge 0$ 无量纲：$w{=}0$ 退化为不看观测的盲采、$w{>}1$ 放大"服从这次看到的杯子位姿"）。这解释了"端红杯子"为何能既保留正抓/侧抓的多峰、又让每次采样**锁定到当前这只杯子**而非平均杯子——其完整贝叶斯推导见 [[RepresentationLearning#2.2.3 Classifier-Free Guidance：用观测"引导"多峰采样的贝叶斯推导|CFG 观测引导]]。Flow Matching 的速度场 $v_\theta(x_\tau,\tau,s_t)$ 同理对观测取条件，可套用同一 CFG 外插。
> - **NFE (Number of Function Evaluations，网络前向次数) $\approx T$**：去噪 ODE/SDE 的离散化误差正比于步长，要压误差就得多步，故 $T$ 常 100–1000 → 延迟大。这正是把扩散搬上 50 Hz 实时控制的瓶颈（见 §1.4）。它与 [[StochasticProcess#2.1 SDE：漂移 + 扩散，且扩散是状态相关的|SDE 的漂移+扩散]]、[[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|扩散策略]] 同一数学骨架。
>
> **③ 流匹配 Flow Matching**：$a_t=x_0+\int_0^1 v_\theta(x_\tau,\tau,s_t)\,d\tau$
> - 符号：$x_0\sim\mathcal N(0,I)$ 是噪声起点，$x_1$ 是目标动作，$\tau\in[0,1]$ 是**流时间**（无量纲、非物理时间），$v_\theta$ 是学到的**速度场**（单位：动作/单位流时间）。
> - 关键在训练时指定**直线**条件路径 $x_\tau=(1-\tau)\,x_0+\tau\,x_1$（两端点连一条直线）。对 $\tau$ 求导得目标速度 $\dot x_\tau=x_1-x_0=$ **常向量**——路径是直的、速度恒定。
> - 直线 ODE 用少数 Euler 步就能高精度积分（理想直线甚至一步 $x_1\approx x_0+v_\theta$），故 NFE 仅 4–10：既保留扩散的多峰能力、又逼近 AR 的实时性。这就是 π₀/LaST0 选它上快系统的根因。
>
> > [!abstract] 挂上"Continuation / 同伦 / 平滑化"暗线
> > 扩散与流匹配本质同源：都在噪声分布 $\mathcal N(0,I)$ 与真实多峰数据分布之间架一条**连续同伦路径**，"先易（近高斯）后难（真实数据）"——这正是 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|平滑化/同伦]] 与课程学习的同一母题。**区别只在路径形状**：扩散走弯曲的加噪路径（需多步积分），流匹配走直线（少步）。理解了这条暗线就懂：所谓"π₀ 比 Diffusion Policy 快百倍"，本质是"把同伦路径拉直"，而非换了个更聪明的网络。

### 1.4 分层双系统：慢推理 + 快控制

受人类"快慢系统"启发，现代 VLA 常用双层设计：

```
System 2 (慢, 1–10 Hz): 大 VLM 任务理解+规划 → 子目标序列/语言指令
        │
System 1 (快, 50–200 Hz): 轻量策略 (Diffusion/Flow) → 连续动作轨迹
```

> [!note] 两个频率数字不是拍脑袋——它们由"计算延迟"和"控制带宽"两端夹出来
> 为什么慢系统偏偏是 1–10 Hz、快系统是 50–200 Hz？这两个数各有物理的上/下界：
> - **慢系统的上界 = VLM 前向延迟**。一个 3B–55B 参数的 VLM 单次前向在边缘 GPU 上约 $100\,\text{ms}\text{–}1\,\text{s}$，取倒数即 $1\text{–}10\,\text{Hz}$。好在**任务语义变化慢**：从"够到杯子"切到"端起杯子"是秒级事件，不需要高频刷新——快也无益。
> - **快系统的下界 = 控制带宽的 Nyquist 约束**。要稳定闭环控制一个闭环带宽为 $f_{bw}$（单位 Hz）的物理系统，采样率须 $f_s\gtrsim(5\text{–}20)\,f_{bw}$——远超奈奎斯特下限 $2f_{bw}$，因为反馈控制还要留够相位裕度、别让采样延迟吃光相位（见 [[ControlTheory#1.3 频率响应：Bode、相位裕度与带宽|带宽与相位裕度]]、[[SignalProcessing#1.1 采样与混叠：离散化不是无损记录|采样与混叠]]）。灵巧操作接触环 $f_{bw}\sim 10\text{–}30\,\text{Hz}$，故快系统须 $50\text{–}200\,\text{Hz}$。
> - **再往下还有一层**：快系统输出的只是力矩/位姿**目标**，真正闭合的电机电流环带宽在 kHz 级（见 [[Actuation#5.2 电流环带宽、交叉耦合与量化延迟|电流环带宽]]）——这正是"电流 ≠ 关节力矩"暗线：VLA 的动作意图，要经"快系统→底层电流环"两级降速翻译才落到电磁力矩。
> - **两者之比 $\kappa=f_{\text{fast}}/f_{\text{slow}}$**（无量纲）= "慢系统出一次子目标、快系统执行多少拍"。LaST0 取 $\kappa=4$、均摊 ~15.4 Hz，即用锁均摊把慢专家的高延迟摊薄到不拖累快环。
>
> **失效边界**：若快系统慢于约 $5f_{bw}$，接触力会因反馈滞后而振荡甚至发散（相位裕度耗尽）——这就是 §0"动作表示须尊重执行器带宽"的量化含义。让 VLA 直接以 5 Hz 驱动电机去端杯子，物理上必然捏碎或打翻。

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

> [!note] "模仿天花板"不是玄学——一步误差会沿时间轴二次放大
> 为什么 IL 灌再多数据也有天花板？根子是**协变量漂移 (covariate shift) 的二次误差累积**（[[ReinforcementLearning#1.5 对比之二：纯模仿学习为何不够|RL §1.5]]、[[RepresentationLearning#2.1 两大顽疾：协变量漂移与多峰|表征学习协变量漂移]]）：
> - 设 BC 策略在**训练分布**上每步犯错概率为 $\epsilon\in[0,1]$（无量纲）。一旦某步动作偏离演示，机器人就滑进训练集**没见过**的状态，那里策略没被监督过、下一步犯错概率更高，误差滚雪球。
> - 经典 DAgger 分析给出遗憾上界 $J(\pi^*)-J(\hat\pi)\le O(\epsilon H^2)$：$J$ 是任务回报，$\pi^*$ 是专家、$\hat\pi$ 是 BC 策略，$H$ 是任务时间步数 (horizon)。**注意是 $H^2$ 而非 $H$**——长时程任务里单步小误差被时间轴平方放大。端红杯子从"够到→抓→端→放"有几百步（$H$ 大），故纯模仿必然在中途某处崩，这就是"天花板"的数学面目。
> - RL 后训练为何能破顶：它不再逐步匹配演示动作，而是直接优化**自身状态分布下**的回报 $J(\pi)=\mathbb E_{\tau\sim\pi}\!\big[\sum_t\gamma^t r_t\big]$（$\tau$ 是策略自己 rollout 的轨迹，$\gamma\in[0,1)$ 折扣因子，$r_t$ 即时奖励）——让策略在自己**真会去到**的（含分布外）状态上也学到对的动作，把 $H^2$ 的复利误差重新收敛。这与 [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]]"模仿打底、强化收口"完全一致。
>
> **三阶段 IL → Offline RL → Online RL 的排序逻辑**（按"数据成本/真机风险递增、分布外覆盖递增"）：IL 用海量离线演示学"能端"（零探索风险，但受 $H^2$ 顶）；Offline RL 在同一批数据上引入值函数、筛出高回报动作并剔除演示里的次优（仍不碰真机、无风险）；Online RL 才在真机或世界模型里**主动探索演示没覆盖的状态**，补齐最后的鲁棒性——这一步的"世界模型里探索"正是 [[WorldModels#4. 利用层：想象里"练策略"还是"规划动作"|在想象里练策略]]，风险由 [[WorldModels#6.2 Dream RL 的对抗性风险|Dream RL 的对抗性风险]] 兜底。

#### 2.3.1 一条更深的暗线：On-Policy Distillation (OPD) —— 从 LLM 后训练到 Oracle→Generalist 蒸馏

> [!abstract] 母题接续：三个"端杯高手"如何合成一个通用手
> 上面四条路径回答"怎么用 RL 突破模仿天花板"，但漏掉一个在 2025–2026 年从 LLM 后训练**反向溢出到灵巧操作**的关键范式。设想我们在**特权信息**下分别训练了三个 Oracle：分别是端**重杯**、端**滑杯**、端**细长杯**的专家（各自能看到真值质量、摩擦、6D 位姿）；现在要把它们蒸馏成**一个只看真机观测**（本体感受 + 点云）的通用策略 $\pi_\theta$。这正是"模仿×强化缝合线"暗线（[[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]]）在**多教师**设定下的收口，而 LLM 领域给它起了个名字：**OPD**。

> [!important] 名字的双关：一个缩写，两处同构
> **OPD 在 LLM 里 = On-Policy Distillation（在线/同策略蒸馏）；在机器人里 = Oracle Policy Distillation（先知策略蒸馏）**。两者哲学高度同构：**放弃"在静态数据上被动拟合"，改为让学生在自己 rollout 出的状态分布上暴露错误、再由拥有特权/全局信息的强专家群在这些状态上在线纠偏**。差别只在专家形态（细分领域 LLM ↔ 特权 Oracle 策略）与动作空间（离散词表 token ↔ 连续力矩/Delta-Action）。下面先讲 LLM 侧的演进与数学内核，再讲它为什么能、以及如何迁到灵巧操作。

**A. 演进脉络（Phase 奠基 → 移植 → 工业化 → 前沿）**

| Phase | 时间 · 代表工作 | 核心创新 | 局限（催生下一阶段） |
|:--|:--|:--|:--|
| **奠基** | 2010–11 · **DAgger** (Ross et al., CMU) | 交互式模仿：**在学生自己诱导的状态分布上**请专家重打标签，把复合误差 $O(\epsilon H^2)$ 压回 $O(\epsilon H)$（见 [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|RL §7.4]]） | 动作端仍是硬标签 BC；专家须"随叫随到" |
| **移植** | 2023–24 · **GKD** (Agarwal et al., DeepMind, ICLR'24) + **MiniLLM** (Gu et al.) | 把 DAgger 的 on-policy 范式搬进 LLM 蒸馏；支持**灵活散度**（首次系统用 Reverse KL 而非标准 KD 的 Forward KL）；可无缝嵌 RLHF 管线 | 仍是单教师；缺工业级验证 |
| **工业化** | 2025.05 · **Qwen3** 技术报告（分水岭） | 两阶段 **SFT→OPD**（strong-to-weak）；实测 OPD 只需完整 RL pipeline 的 **1/10 GPU 时**达到可比推理力（AIME'24 74.4%@1.8k GPUh vs RL 67.6%@17.9k GPUh） | 单教师上限 = 教师 |
| **前沿** | 2026 · **MiMo-V2-Flash MOPD**（多教师）· **G-OPD/ExOPD** (Yang et al., 人大·腾讯) · 机制论文（清华 · Fu et al.）· **Missing-Old-Logits** (Guan et al.) | 多教师在 **logit 空间**融合（避开 weight-merge 的能力互扰），学生**超越最强单教师**（AIME'25 94.1% vs 93.9%）；理论证明 **OPD = $\beta{=}1$ 的 KL 约束 RL**，reward extrapolation（$\lambda{>}1$）让学生"比教师更教师" | Token 空间瓶颈 / 长序列崩塌 / 异步陈旧（见 D） |

**B. 数学内核：为什么 OPD 天然是 Reverse KL —— 兼纠正一个常见误解**

一切分歧只在一个问题：**KL 散度的期望在谁的分布上取？**（KL 方向的信息论含义见 [[InformationTheory#2.3 KL 散度：信念跳变与"贝叶斯惊奇"|信息论 §2.3]]。）

- **Forward KL $D_{KL}(P_{\text{teacher}}\Vert\pi_\theta)$ = SFT/BC**：期望在**教师**分布取（Off-Policy）。它惩罚"教师有、学生没有"，逼学生**覆盖**教师每一个 mode（mode-covering），代价是把噪声也学进来。
- **Reverse KL $D_{KL}(\pi_\theta\Vert P_{\text{teacher}})$ = OPD**：期望在**学生**分布取（On-Policy）。它惩罚"学生有、教师不认"，让学生**只挑教师最确定的那个 mode 精确拟合**（mode-seeking）。

> [!warning] 纠误：传统 DAgger 的"动作端"其实是 **Forward KL**，不是 Reverse KL
> 常被混淆的一点：DAgger 的**状态端**是 on-policy（这是它的伟大之处），但**动作端**仍是 BC。写出它的损失并逐步展开——$\pi_o$ 记 Oracle 动作分布、$\pi_\theta$ 记学生、$\rho_{\pi_\theta}(s)$ 记学生状态占用频率：
> $$\mathcal L_{\text{DAgger}}(\theta)=\mathbb E_{s\sim\rho_{\pi_\theta}}\Big[\mathbb E_{a\sim\pi_o}[-\log\pi_\theta(a\mid s)]\Big]$$
> 内层是交叉熵 $H(\pi_o,\pi_\theta)$。用信息论恒等式 $H(P,Q)=H(P)+D_{KL}(P\Vert Q)$，令 $P=\pi_o,\,Q=\pi_\theta$，且 $H(\pi_o)$ 对参数 $\theta$ 是常数（不参与梯度），于是
> $$\mathcal L_{\text{DAgger}}(\theta)\;\equiv\;\mathbb E_{s\sim\rho_{\pi_\theta}}\big[\,D_{KL}(\pi_o(\cdot\mid s)\Vert\pi_\theta(\cdot\mid s))\,\big].$$
> KL 方向是"教师在前"——**标准 Forward KL**。后果：若三个 Oracle 对同一状态给出 $a_1^*,a_2^*,a_3^*$，Forward KL 逼学生**覆盖**三者，而连续空间里单峰高斯"覆盖"多个目标的唯一极小值就是**均值** $\tfrac13\sum_i a_i^*$——一个物理上无效的"中间动作"（母题版：三种端法折中成"既没端稳重杯也没端稳滑杯"的僵姿）。这就是灵巧操作里 Mode-Collapse 的数学面目，也是很多人转投 Flow Matching/Diffusion 的直接动机（多峰保真见 [[RepresentationLearning#2.2 扩散策略：迭代的轨迹优化器|表征学习扩散策略]]）。
>
> **LLM 的 OPD 靠一个极小改动真正落到 Reverse KL**：不再"让教师给出动作、学生去拟合"，而是**学生自己采样动作 $y\sim\pi_\theta$、教师只对它打分 $\log\pi_{\text{teacher}}(y\mid x)$**：
> $$\mathcal L_{\text{OPD}}(\theta)=\mathbb E_{x\sim\rho_{\pi_\theta}}\Big[\mathbb E_{y\sim\pi_\theta}\big[\log\tfrac{\pi_\theta(y\mid x)}{\pi_{\text{teacher}}(y\mid x)}\big]\Big]=\mathbb E_{x}\big[D_{KL}(\pi_\theta\Vert\pi_{\text{teacher}})\big].$$
> 期望在 $\pi_\theta$ 上——真正的 Reverse KL、mode-seeking，学生会**坚定收敛到一个专家而非取均值**，从根上绕开了上面的平均化灾难。

**C. OPD = KL 约束 RL 的特例（G-OPD 统一定理，兑现"统一梯度视角"）** 这条把 OPD 缝回 RL，与 [[ReinforcementLearning#5.4.2 统一梯度视角：SFT、蒸馏与 RL 本是一家|RL §5.4.2]] 同源。RL-as-inference 定义**奖励倾斜（reward-tilted）目标分布**：$\pi^*(y\mid x)\propto\pi_{\text{ref}}(y\mid x)\exp\!\big(r(x,y)/\beta\big)$——$\pi_{\text{ref}}$ 是参考策略（base 或 EMA 影子网），$r$ 即时奖励，$\beta$ 温度系数（$\beta$↓则奖励主导、$\beta$↑则贴住参考）。把带 KL 惩罚的 RL 目标 $\max_\theta\mathbb E_{y\sim\pi_\theta}[r]-\beta D_{KL}(\pi_\theta\Vert\pi_{\text{ref}})$ 配方，可证其**等价于** $\min_\theta D_{KL}(\pi_\theta\Vert\pi^*)$（配分函数 $Z(x)$ 与 $\theta$ 无关，被消去）。**G-OPD 定理**：令隐式奖励 $r_{\text{impl}}=\log\pi_{\text{teacher}}-\log\pi_{\text{ref}}$，则标准 OPD 恰是 $\beta{=}1$ 的 KL 约束 RL（奖励与正则永远等权、且每 token 都有密集奖励）。放开两个自由度——奖励缩放 $\lambda$ 与参考模型选择——即 G-OPD；取 $\lambda{>}1$（**ExOPD**，论文建议 $\lambda{=}1.25$）让学生**放大**教师相对参考的优势方向，从而在多教师设定下**超越教师**。

**D. 失效边界（迁移前必须知道的"坑"）**
- **LLM 侧**：① Token 空间瓶颈——师生交集 token 承载 **97–99%** 概率质量，梯度几乎只来自 ~3% 高频共享 token；② **分布不可区分性**——两个 benchmark 分差很大的教师，在学生访问到的状态上可能诱导出几乎相同的局部目标（"更大的教师≠更好的教师"）；③ **长序列后期崩塌**——教师在深前缀上的续写能力单调退化，"全局信息量≠局部可利用性"。
- **机器人侧**：① **绝不能拿 SFT 轨迹当基线**——BC 初始化在灵巧操作里几步就 OOD（$H^2$ 复利，见 [[ReinforcementLearning#1.5 对比之二：纯模仿学习为何不够|RL §1.5]]），此时最"懂"物理边界的参考其实是学生**刚在环境里存活下来的策略**（用其 EMA 影子网当 $\pi_{\text{ref}}$）；② **异步吞吐 vs Missing-Old-Logits**——数千并行环境里同步跑 Oracle 前向会让 FPS 暴跌，必须异步；但异步会让采样版本 $\mu_{\text{old}}$ 与更新版本错位，重要性比率语义失配 → KL 爆炸。修复是 **PPO-EWMA**：用学生策略的指数移动平均当代理参考，并在 Train-Infer Mask 比例跌破阈值时**自动重置**。

**E. 灵巧操作落点：History-Aware Asymmetric PPO + 复合优势蒸馏**（把 A–D 收成一条可落地路线）
1. **非对称 Actor-Critic**：Actor $\pi_\theta(a\mid o_t,z_{\text{cmd}},h_t)$ 只吃真机观测 + 追踪指令 + **历史编码 $h_t$**（LSTM/TCN，隐式做在线系统辨识、"猜"当前是三杯中的哪一只）；Critic $V_\phi(s^p,z_{\text{cmd}})$ 在仿真里**享特权** $s^p$（真值质量/摩擦/位姿）以降方差，部署时丢弃。这与 [[WorldModels#5.2 WMTS 的核心结构决策：Actuator + Rigid 解耦|WMTS 的特权信息不对称]] 同构。
2. **把 Oracle 降成密集 shaping 项、而非硬拟合目标**：$r_{\text{total}}=R_{\text{track}}+\alpha\,\log\pi_{\text{oracle}}^{(i)}(a_{\text{student}}\mid s^p,z_{\text{cmd}})$——$R_{\text{track}}$ 是唯一北极星（轨迹追踪误差），第二项是"让对应物体的 Oracle 给学生**自采动作**打分"（据 C，最大化它 ⟺ 最小化 Reverse KL $D_{KL}(\pi_\theta\Vert\pi_{\text{oracle}})$，故连续空间单峰高斯也不会被多教师拉平）。
3. **课程式 $\alpha$ 衰减**：早期 $\alpha$ 大，借 Oracle 快速跨过冷启动瞎撞；中后期 $\alpha\!\to\!0$，完全交回 $R_{\text{track}}$，防止 Oracle 的次优行为封住学生上限——这正是 [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|"模仿打底、强化收口"]] 在蒸馏场景的显式实现，也呼应"无知即课程"的反向利用（[[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|WM §6.3]]）。

> [!note] 一句话记忆：OPD 是"把 DAgger 的 on-policy 状态纠偏 + Reverse KL 的 mode-seeking 动作评分"缝在一起
> 它对 VLA/灵巧操作的价值不在"又一个新 loss"，而在给"多个特权专家 → 一个真机通用策略"这件事提供了**理论闭环**：状态端 on-policy 治协变量漂移，动作端 Reverse KL 治多峰坍塌，$\beta{=}1$/$\lambda$ 把它接回 RL 从而能与任务奖励共治。判据仍是本库标尺——**它是否服务于"让策略在接触丰富的高动态任务上学会技能并安全迁到真机"**：OPD 用 1/10 的算力把"已被 Oracle 发现的技能"高效教给受限观测的学生，正卡在这条线上。

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

> [!note] 空间 grounding 的关键一步——从"哪块像素"到"空间哪一点"（最易被跳过的坐标变换）
> 上一段的箭头把"SAM + Depth → 3D 点云"一笔带过，但这里藏着 VLA 空间对齐（§1.1 第 2 层 spatial grounding）真正落地的运算：**二维语义如何反投影 (back-projection) 成三维坐标**。逐符号讲透：
> - CLIP/Grounding-DINO/SAM 给出的是**像素坐标** $(u,v)$（单位 px）上的掩膜——它只回答"红杯子在图像的哪一片"，没有深度，无法伸手。
> - Depth Anything 补上每像素深度 $d(u,v)$（单位 m，相机光心到该点的视线距离）。有了深度，用相机内参矩阵 $K=\begin{pmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{pmatrix}$（$f_x,f_y$ 焦距、$c_x,c_y$ 主点，单位均为 px）做**针孔反投影**：$X=\dfrac{(u-c_x)\,d}{f_x},\ Y=\dfrac{(v-c_y)\,d}{f_y},\ Z=d$，得相机系下的 3D 点 $(X,Y,Z)$（单位 m）。
> - 再左乘手眼标定的外参 $T_{cb}\in SE(3)$（相机→机器人基座的刚体变换，见 [[Dynamics#2.3 SE(3)、twist 与指数积公式 (PoE)|SE(3) 变换]]），把点云搬进机器人可执行的基座系——**这一步做完，"红"才第一次拥有了机器人能伸手够到的物理坐标**。
> - 掩膜内所有像素反投影汇成物体点云后，抓取点的选取回到几何：最近点/穿透深度查 [[ComputationalGeometry#4. 有向距离场 (SDF)：连续优化的基石|SDF]]、碰撞查 [[ComputationalGeometry#3. 离散碰撞检测：GJK 与 EPA|GJK/EPA]]，力闭合查 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|抓取矩阵 $G$]]。
>
> **失效边界**：单目 Depth Anything 给的是**相对/尺度模糊**深度，绝对尺度 $d$ 有系统性偏差——若不用 RGB-D 或多视立体标定尺度，反投影点云会整体缩放，抓取点偏移几厘米即抓空。这正是 §4 "仿真质量决定 sim-to-real 上限"在感知侧的镜像：**几何 grounding 的精度上限由深度尺度标定决定**。

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

> [!note] 为什么"并行 / 精确 / 可微"三者难以兼得——根子在接触的非光滑性
> 表格把 Isaac（并行）、MuJoCo（精确）、Genesis（可微）并列，却没说清这三条为何是**相互拉扯的取舍**而非可自由叠加的特性。三者的公约数矛盾都指向同一个物理根源——**接触把动力学撕成非光滑系统**（本库"接触的非光滑性"暗线，见 [[ContactMechanics]]、[[Dynamics#6.4 仿真伪影：策略学到的是真物理还是 bug？|仿真伪影]]、[[Optimization#3. 接触如何毁掉优化：互补约束与非凸景观|接触毁掉优化]]）：
> - **并行 ↔ 精确的矛盾**：GPU 一次跑上万个环境，要求每步**固定迭代数、固定内存**、无分支。硬接触本是互补约束（要么零穿透要么零力，见 [[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]]），精确求解需迭代到收敛、步数随接触数不定——与"固定迭代"冲突。于是 PhysX 这类 GPU 引擎把迭代**截断在固定次数**（PGS 定步，见 [[Dynamics#6.3 PGS 核心循环（实时引擎的心脏）|PGS 循环]]），残余约束违反表现为"软接触/微穿透"——**并行的代价是接触精度**。这就是为什么并行仿真训出的策略可能学到 [[Dynamics#6.4 仿真伪影：策略学到的是真物理还是 bug？|仿真伪影]]（靠穿透卡住物体等），迁真机即失效。
> - **精确的来路**：MuJoCo 不解硬 LCP，而是把接触松弛成**凸优化**（软约束，见 [[Dynamics#6.2 凸优化流派（MuJoCo）：放弃硬约束|凸优化流派]]、[[ContactMechanics#5.3 凸优化范式（MuJoCo）与位置层（XPBD）|凸范式]]）——牺牲"绝对不穿透"，换来解**唯一且稳定**、无 LCP 的病态多解，故"精确/可复现"。代价是它天生不像 GPU 引擎那样极致并行。
> - **可微的门槛**：可微仿真（Genesis/Brax）要梯度穿过接触，而接触事件处目标对参数**不连续**（碰/不碰是阶跃），朴素求导得零或爆炸梯度。必须先把接触**平滑化**（见 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|平滑化让梯度穿过接触]]、[[ContactMechanics#6. 可微接触物理：让接触进入梯度优化|可微接触]]）——又是"用平滑近似换可导性"的 Continuation 暗线。故"可微"与"物理精确"再次拉扯。
>
> **落点（选型即选取舍）**：大规模 RL 用 Isaac（吞吐优先，靠 DR 掩盖软接触误差）；精细接触基准/系统辨识用 MuJoCo（精度优先）；需梯度的轨迹优化/参数辨识用 Genesis（可微优先）。**没有"全都要"的引擎，因为接触的非光滑性不允许**——这是 §4 母题"仿真质量决定 sim-to-real 上限"的物理注脚。

> [!important] 仿真质量决定 sim-to-real 上限
> Insight：① **Scaling Law**——机器人基础模型如 LLM 般，更多数据+更大模型→更好泛化；② **可微仿真是下一前沿**（梯度直接穿过物理，接 [[Dynamics#9. 适配层：可微物理与神经动力学|可微物理]]、[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|可微接触]]）；③ **数据飞轮**——采集→训练→部署→自动采集的闭环是规模化关键。选型：入门 MuJoCo+gymnasium、大规模 RL Isaac Lab、前沿 Genesis。

---

## 5. 硬件与数据基础设施

> [!tip] 本节四拍
> **直觉**（端红杯子的策略要么来自遥操演示、要么来自仿真——数据从哪来？）→ **推导**（遥操系统、触觉传感、大规模数据集）→ **对比**（ALOHA 双臂 vs UMI 手持 vs GELLO 外骨骼）→ **落点**（数据基础设施是数据飞轮的物理底座）。

**数据采集**：ALOHA（双臂遥操，低成本开源）、UMI（手持教学，无需机器人）、GELLO（外骨骼，直觉操作）、TeleMoMa（多模态 VR）。**触觉传感**（与 [[SignalProcessing]]、[[ContactMechanics]] 紧密相关）：GelSight 系列（视触觉，把触觉变视觉问题）、电子皮肤（分布式压力）、关节力矩传感器（力控基础）。**关键数据集**：Open X-Embodiment（100 万+，多平台）、DROID（76K，Franka 真机）、RH20T（20T，多平台）。

> [!note] 双臂为什么不是"两个单臂各干各的"——协同的本质是一条闭运动链
> ALOHA、RDT-1B（§1.2）、RoboTwin 全是**双臂 (bimanual)**，但双臂难在哪、为什么不能把左右手当两个独立策略拼起来，前文未点破。关键：一旦两只手**同时握住同一个物体**（端一只大托盘、双手转杯），左手—物体—右手就闭合成一条**闭运动链 (closed kinematic chain)**，动力学不再是两条独立开链，而与"握住螺丝刀后拓扑突变"完全同构（见 [[Dynamics#7. 闭链与操作空间动力学：握住螺丝刀之后|闭链动力学]]）。逐层看后果：
> - **相对位姿硬约束**：两手末端位姿 $T_L,T_R\in SE(3)$ 必须满足 $T_L^{-1}T_R=T_{\text{obj}}=\text{const}$（物体是刚体，两手抓点相对位姿锁死）。这把 12 维（两臂各 6）自由度砍到受约束流形上——任何不满足该约束的动作都会**内力挤压**物体（捏碎托盘或掰裂）。这正是 [[Dynamics#7.2 约束漂移与内力|约束漂移与内力]] 在双臂上的直接落点。
> - **内力落在抓取矩阵零空间**：把两手看作物体上的两个"接触"，双手施力到物体的映射就是 [[ContactMechanics#3.1 抓取矩阵的严格定义与内力|抓取矩阵 $G$]]；不改变物体净受力的**内力**恰好落在 $\text{null}(G)$ 里——与单手多指抓取的内力分析是同一套数学。这就是本库**对偶性 $J/G/P$ 暗线**（手雅可比/抓取矩阵/腱耦合三处同构）在"双臂"这一新场景的复用：双臂协同 = 把"多指抓一物"放大到"多臂抓一物"，力闭合/冗余/零空间工具原样搬过来。
> - **为什么策略必须共享而非分治**：正因存在上述耦合约束，左右臂动作必须由**同一策略**联合输出（RDT-1B 用一个 Diffusion Transformer 同出双臂 14 维动作），分治两个策略会各自违反相对位姿约束、在物体上打架。这也解释了 §1.3 多峰的双臂版本：双手"谁主谁辅、从哪侧合拢"本身多峰，更需扩散/Flow 建模。
>
> **失效边界**：双臂标定误差会直接转成持续内力——手眼外参差 1° 或抓点估计偏 1 cm，闭链约束 $T_L^{-1}T_R$ 就被系统性违反，物体被慢慢挤变形或滑脱。故双臂系统对 §3 的空间 grounding 精度比单臂敏感得多。

> [!note] 数据飞轮的物理底座
> 这些硬件与数据集是 §0 "数据飞轮层"的物理实现——没有规模化的真机数据采集，"从失败中持续变强"就是空话。端红杯子要泛化到千百种杯子，靠的正是 Open X-Embodiment 级的数据规模 + 数据飞轮的闭环回流。

> [!note] 数据飞轮的"方向盘"是认知不确定性——别匀速盲采
> 若数据飞轮只是"采集→训练→部署→再采集"的匀速转动，算力会浪费在已经学会的场景上。真正的加速器是**用认知不确定性 (epistemic uncertainty) 指向"该采之处"**——这正是全库"认知不确定性三用"暗线（[[WorldModels#3. 不确定性层：模型何时在"自信地瞎编"|认知不确定性]]、[[StochasticProcess#3.2 一个必须刻进脑子的区分：Aleatoric vs Epistemic|Aleatoric vs Epistemic]]）在具身系统的落点：
> - **失败聚集在模型不确定处**：ensemble 分歧大 ⇔ epistemic 高 ⇔ "没见过的杯子/桌面/光照"。飞轮应优先回流这些样本，而非重复采集早已掌握的"正抓红杯子"。这与 aleatoric（本质随机、采再多也消不掉，如传感器噪声）要严格区分——只有 epistemic 值得靠采数据消除。
> - **闭环形式化**：部署策略 $\pi_k$ →（在高 epistemic 片段）检测失败/人类介入 → 采集校正数据得 $\mathcal D_{k+1}$ → 后训练得 $\pi_{k+1}$，迭代轮次 $k$。RECAP 的 Demos→Corrections→RL 与 DexHiL 的**干预感知采样**（在策略最没把握处才请人类接管）都是这一闭环的实例（§2.3）。
> - **三用之一"当课程"**：不确定性还能**反向驱动下一批任务生成**（[[WorldModels#6.3 无知即课程：认知不确定性反向驱动任务生成|无知即课程]]）——飞轮该造什么新场景，由"当前策略最不会什么"决定。
>
> 于是数据飞轮不只是"物理底座"，而是被 epistemic 信号**导航**的主动学习循环——与 §2.3 的 RL 后训练、§0 的"数据飞轮层"闭合成同一条主线。这也回答了 §0 的判据"反馈如何修正分布外接触"：靠 epistemic 把分布外样本优先送回训练。

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
