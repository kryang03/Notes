---
tags:
  - paper
  - dexterous-manipulation
  - adaptive-control
  - sim-to-real
  - WMTS
aliases:
  - DexCtrl
paper-year: 2025
read-date: 2026-06-14
venue: arXiv
paper-pdf: "[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning.pdf]]"
related:
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
  - "[[ReinforcementLearning]]"
  - "[[Final_WMTS]]"
---

# DexCtrl: Towards Sim - to - Real Dexterity with Adaptive Controller Learning

> [!abstract] 核心贡献
> DexCtrl 的问题意识是：灵巧手 sim-to-real 不应只调高层策略，也要学习能吸收执行器、接触和对象差异的自适应 controller。

> [!tip] 与理论基础的关联
> - [[ContactMechanics]] — contact mode, friction, grasp stability
> - [[Dynamics]] — hand-object rigid body dynamics
> - [[ReinforcementLearning]] — policy learning under contact

> [!note] PDF 摘要摘录
> Dexterous manipulation has seen remarkable progress in recent years, with policies capable of executing many complex and contact-rich tasks in simula- tion. However, transferring these policies from simulation to real world remains a significant challenge. One important issue is the mismatch in low-level controller dynamics, where identical trajectories can lead to vastly different contact forces and behaviors when control parameters vary. Existing approaches often rely on manual tuning or controller randomization, which can be labor-intensive, task- specific, and introduce significant training difficulty. In this work, we propose a framework that jointly learns actions and controller parameters based on the historical information of both trajectory and controller. This adaptive controller adjustment mechanism allows the policy to automatically tune control parameters during execution, t

## 0. 阅读定位与范本价值
这篇 recap 按 `$paper-recap-insight` 的口径整理：先定位论文真正处理的瓶颈，再追踪变量来源、结构性假设、实验因果链和对 [[Final_WMTS]] 的迁移价值。这里不默认写实现代码；如果实现细节重要，只把它解释成信息流、数值约束或失败模式。

它在当前知识库中的角色是：这是 WMTS actuator model 的近邻：可以把 adaptive controller 的 latent context 显式交给 Task Scheduler，避免调度器误判动作可执行性。

## 1. 问题设定与动机

### 1.1 一句话核心
固定 PD/position controller 把策略动作到真实力矩之间的误差隐藏起来，导致仿真中学到的动作在真机上相位、幅值和接触力都偏掉。

### 1.2 直观隐喻
可以把这篇论文看成是在回答一个工程化问题：当真实机器人不允许无限试错，而任务又包含接触、长时序或分布偏移时，应该把哪一部分结构显式交给模型/控制器/课程，而不是让策略黑箱硬学。

### 1.3 现有方法的局限
- 只做端到端策略：容易把感知、动力学、接触和任务目标纠缠在同一个网络里，失败后很难知道是哪一层错。
- 只做解析模型：物理结构清晰，但真实摩擦、执行器延迟、视觉误差和高维接触通常无法完全建模。
- 只做数据扩张或随机化：能提高鲁棒性，但如果没有结构化变量，无法解释哪些扰动真的覆盖了真实失败模式。

### 1.4 Delta 分析
让 controller 根据状态、历史误差或任务条件自适应，可以在不重学全部策略的情况下补偿低层动力学差异。

## 2. 核心方法与理论

### 2.1 变量来源追踪
| Variable | Domain/shape | Source | Fixed/learned/observed/computed | Meaning | Trap |
|---|---|---|---|---|---|
| $q,\dot q$ | hand joint state | proprioception/sim | observed | robot configuration | command is not torque |
| $T_o,R_o$ | object pose/rotation | vision/state estimator | observed/estimated | task state | latency/noise changes contact action |
| $c_i,f_i$ | contact mode/force | sim/tactile/inferred | hidden/observed | physical interaction | often unobserved in vision-only setup |
| $a_t$ | joint target/torque/action | policy | chosen | low-level command | controller semantics affect dynamics |
| $g$ | goal pose/task condition | task sampler | fixed per episode | desired outcome | may be infeasible under contact |

### 2.2 前置理论从零推导
这类方法可以统一写成闭环决策问题：机器人在时刻 $t$ 看到观测 $o_t$，内部构造状态或 belief $s_t$，选择动作 $a_t$，真实世界返回 $o_{t+1}$、reward/cost 或成功信号。关键分歧在于论文把哪一项结构化：

- 若结构化 $p(s_{t+1} \mid s_t, a_t)$，它是在做 world model / dynamics model。
- 若结构化 $\pi(a_t \mid o_t, g)$，它是在做 policy/action prior。
- 若结构化任务分布 $p(g)$ 或 level replay，它是在做 curriculum / task scheduler。
- 若结构化控制接口 $u \rightarrow \tau$ 或 force/position channel，它是在处理 sim-to-real actuator/control gap。

因此读这篇论文时不要只问“用了什么网络”，而要问：论文把哪一个不可控黑箱改造成了可解释、可采样或可约束的对象。

### 2.3 论文核心机制无跳步推导
- 高层策略给出目标手形/动作。
- adaptive controller 根据 tracking error、接触状态或 latent context 调整低层控制输出。
- sim-to-real 通过真实数据或随机化训练 controller 的补偿能力。

从手-物动力学角度看，策略真正控制的是带接触约束的混合系统：
$$
M(q)\ddot q + C(q,\dot q) = \tau + J_c(q)^\top f_c,
\quad f_c \in \mathcal{K}_{friction},
\quad c_t \in \{\text{stick, slip, break}\}
$$
论文的结构性贡献通常是在减少 contact mode 搜索、几何泛化或低层执行器偏差。陷阱是很多变量在仿真中可见，在真机上只能被估计。

### 2.4 概念边界与符号陷阱
- `state` 不一定是真实物理状态；很多论文里的 state 是 latent、belief 或 simulator privileged state。
- `action` 不一定是力矩；可能是关节目标、末端位姿、action chunk、diffusion latent 或 controller condition。
- `world model` 不等于完整世界重建；对机器人来说，只有能改变决策的预测才有价值。
- `sim-to-real` 不只是视觉 domain gap；执行器延迟、接触摩擦、控制频率和状态估计延迟通常更致命。

### 2.5 信息流/算法机制（无代码）
1. 观测/任务条件进入表示层，形成 $s_t$、latent 或 context。
2. 方法引入结构性假设：让 controller 根据状态、历史误差或任务条件自适应，可以在不重学全部策略的情况下补偿低层动力学差异。
3. 策略、模型或优化器在这个结构上生成候选动作/预测/任务。
4. 实验通过成功率、预测误差、回报、约束违规或迁移表现检验结构是否真的减少了原瓶颈。

## 3. 训练、数据与实验

### 3.1 PDF 结构线索
- 1     Introduction
- 2   Problem Statements
- 3       Methods
- 3.1     Oracle Policy for Data Collection
- 3.2   Action Prediction and Control Parameters Prediction
- 4     Experiments
- 4.1    Experimental Setup
- 5   Related Work

### 3.2 关键结果与证据
看真机 dexterous task 成功率、tracking error、跨物体/跨速度适应，以及 controller adaptation 的消融。

- PDF 线索：and achieving better performance on two contact-rich manipulation tasks: rotation and flipping.
- PDF 线索：with policies capable of executing many complex and contact-rich tasks in simula-
- PDF 线索：tion. However, transferring these policies from simulation to real world remains a
- PDF 线索：over force interactions and improves robustness in real-world scenarios. Exper-
- PDF 线索：mance across a variety of dexterous tasks involving variable force conditions.
- PDF 线索：policies has shown capabilities in handling various contact-rich manipulation tasks such as rotating

### 3.3 Ablation 因果链
去掉自适应低层 -> 高层策略需要自己学习执行器补偿 -> 样本效率低且泛化差。

更一般地，ablation 应按这条链理解：移除结构性假设 -> 模型/策略需要用黑箱容量补偿 -> 在分布外、长 horizon 或接触切换处误差放大 -> 指标下降。不要只把 ablation 看成“少了一个模块所以差”，要看少掉的是哪一种 inductive bias。

### 3.4 工程约束与实验边界
- 真实机器人任务中，评估指标必须同时看成功率、恢复能力、约束违规和执行成本。
- 若论文只在仿真中验证，迁移到 WMTS 时要额外审查 actuator delay、contact sensing 和 domain randomization 覆盖。
- 若论文依赖视觉，灵巧手高速接触任务还需要检查遮挡、帧率和 tactile/proprioceptive 补偿。

## 4. 核心洞见

### 4.1 论文真正的 insight
让 controller 根据状态、历史误差或任务条件自适应，可以在不重学全部策略的情况下补偿低层动力学差异。

### 4.2 为什么这个设计有效
它有效的原因不是“模型更大”，而是把原来难以泛化的自由度收缩到更合理的结构里：要么让动力学预测只负责短 horizon，要么让动作生成保留多模态，要么让课程集中在能力边界，要么让控制接口显式反映真实物理限制。

### 4.3 什么时候会失效
controller 过强可能掩盖高层策略错误，导致 credit assignment 不清；需要分清低层补偿和任务意图。

## 5. 替代方案与理论局限

### 5.1 理论维度
替代方案是把结构完全交给端到端网络。优点是表达力强、工程接口简单；缺点是变量来源不可解释，遇到真实分布偏移时很难定位失败。本文路线的优势在于引入了可检查的中间结构，但代价是结构假设一旦错，会形成系统性偏差。

### 5.2 算法维度
可以用 model-free RL、behavior cloning、MPC、diffusion action prior、ensemble uncertainty 或 curriculum learning 替代本文方法的一部分。选择哪一种，取决于瓶颈是探索、预测、动作多模态、控制延迟还是任务覆盖。

### 5.3 工程/实验维度
对 WMTS 最重要的不是复现 benchmark，而是做失败边界实验：换笔质量、换摩擦、加视觉延迟、限制电机带宽、制造接触丢失，观察方法是否仍能给出可恢复动作。

## 6. 对用户研究的启发

### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real 的迁移
这是 WMTS actuator model 的近邻：可以把 adaptive controller 的 latent context 显式交给 Task Scheduler，避免调度器误判动作可执行性。

### 6.2 可验证实验建议
- 构造一个最小转笔或手内重定向环境，把方法中的核心结构单独接入，不先追求完整系统。
- 对比三组：端到端 PPO/DP、加入本文结构的版本、加入结构但打乱关键变量的负对照。
- 记录 failure mode：掉笔、打滑、过大接触力、动作饱和、视觉估计漂移、world model overconfident。

### 6.3 不应过度外推的点
不要因为论文在 locomotion、视觉操作或仿真 benchmark 上成功，就默认它能处理多指高速接触。迁移前必须确认：状态变量是否包含接触，动作接口是否匹配真实控制器，模型 horizon 是否短到足够可信。

## 7. 与知识体系的联系

### 与 [[ContactMechanics]] 的联系
contact mode, friction, grasp stability。这篇论文提供的是一个可迁移的结构化 bias：它把 固定 PD/position controller 把策略动作到真实力矩之间的误差隐藏起来，导致仿真中学到的动作在真机上相位、幅值和接触力都偏掉。 转化为可建模、可采样或可约束的问题。

### 与 [[Dynamics]] 的联系
hand-object rigid body dynamics。这篇论文提供的是一个可迁移的结构化 bias：它把 固定 PD/position controller 把策略动作到真实力矩之间的误差隐藏起来，导致仿真中学到的动作在真机上相位、幅值和接触力都偏掉。 转化为可建模、可采样或可约束的问题。

### 与 [[ReinforcementLearning]] 的联系
policy learning under contact。这篇论文提供的是一个可迁移的结构化 bias：它把 固定 PD/position controller 把策略动作到真实力矩之间的误差隐藏起来，导致仿真中学到的动作在真机上相位、幅值和接触力都偏掉。 转化为可建模、可采样或可约束的问题。

## References
- 原始 PDF：[[DexCtrl- Towards Sim-to-Real Dexterity with Adaptive Controller Learning.pdf]]
- 项目入口：[[Final_WMTS]]
