---
tags:
  - quiz
  - projects
  - WMTS
  - world-model
  - real-robot-rl
aliases:
  - WMTS Project Quiz
created: 2026-05-01
related:
  - "[[Final_WMTS]]"
  - "[[WMTS_Reliability_Extensions]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
---

# 10 Projects: World Model as Task Scheduler

## Architecture

### Q001. [[Final_WMTS]] 的五模块主架构是什么？

**标准答案：** 五模块是隐空间任务生成器、Oracle 专才策略、Generalist Diffusion Policy、Ensemble World Model、真机闭环微调与安全过滤。任务生成器提出边界任务，Oracle 在仿真解题，Generalist 蒸馏成可部署策略，WM 预测动力学和不确定性，真机闭环用 WM 和安全层微调。

**评分要点：** 五个模块必须完整且顺序清楚。

### Q002. WMTS 为什么把 World Model 定位为 Scheduler 而不是单纯 Predictor？

**标准答案：** Predictor 只预测下一状态，Scheduler 要根据不确定性、任务难度、执行器可行性和接触风险决定接下来训练什么、采集什么、是否放行动作。WM 的价值不只是拟合动力学，而是调度课程、数据和安全决策。

**评分要点：** 必须讲出调度任务/数据/安全，而非只预测。

### Q003. Latent Task Generator 为什么用 VAE/CMA-ES？

**标准答案：** VAE/CVAE 将复杂任务描述压缩为连续隐空间，CMA-ES 在该空间中做黑盒演化搜索，寻找通才“没掉但跟得吃力”的能力边界和 WM 不确定区域。这样任务生成不依赖手工枚举，而是围绕策略和模型盲区自适应探索。

**评分要点：** 必须提到连续隐空间和黑盒 fitness。

### Q004. WMTS 中 curiosity fitness 为什么用 ensemble disagreement？

**标准答案：** Ensemble disagreement 近似 epistemic uncertainty，即世界模型对某任务区域是否理解不足。最大化它可引导任务生成到最能减少模型无知的区域。但必须用 reliability head 限制，避免选择硬件不可执行或接触不可能的任务。

**评分要点：** 必须区分 epistemic uncertainty 和风险约束。

### Q005. Oracle Specialist 为什么只在仿真中唤醒？

**标准答案：** Oracle 可使用仿真特权状态，如物体真实位姿、接触力、摩擦和惯性参数，训练高性能专家轨迹；这些信息真机不可得。Oracle 的作用是解盲区任务并生成可蒸馏知识，而不是直接部署。

**评分要点：** 必须提到 privileged state 和蒸馏。

### Q006. Generalist Diffusion Policy 的输入、条件和输出分别是什么？

**标准答案：** 输入是 noisy action chunk 和扩散时间步，条件是真机可观测状态 $O_{real}$ 与局部任务条件 $C_{local,t}$，输出是未来动作块 $A_t\ldots A_{t+K-1}$。它用 denoising score matching 学习从观测到动作序列的多模态分布。

**评分要点：** 必须区分去噪对象和条件。

### Q007. Classifier-Free Guidance 在 WMTS diffusion policy 中有什么作用？

**标准答案：** CFG 同时训练有条件和无条件去噪模型，推理时放大条件对动作生成的影响。无条件得分提供动作流形先验，条件得分提供任务拉力。调节 guidance weight 可在动作自然性和任务跟随之间折中。

**评分要点：** 必须提到无条件流形和条件拉力。

### Q008. Hindsight relabeling 在 Oracle 蒸馏流程中的潜在作用是什么？

**标准答案：** 如果 Oracle 没完美追踪目标但产生了动力学合理轨迹，可把实际达到的轨迹重标为条件，让 Generalist 学到可执行动作和真实物理演化，而不是只把偏差当失败丢弃。关键是判断“动力学合理”而非危险或伪影轨迹。

**评分要点：** 必须说明实际轨迹替代目标条件。

### Q009. WMTS 为什么把 Actuator Model 和 Rigid Dynamic Model 解耦？

**标准答案：** 高动态灵巧手中，指令到关节/指尖力之间有通信延迟、FOC、电机热衰减、丝杠摩擦和连杆耦合；而力矩到物体状态演化属于刚体/接触动力学。解耦可防止一个黑箱模型让执行器和刚体部分互相背锅，并支持 frozen-rigid 真机适配。

**评分要点：** 必须说出 actuator gap 与 rigid dynamics gap 不同。

### Q010. 为什么 WM 输入不应包含任务 $C$？

**标准答案：** 物理动力学由状态和动作决定，任务只是人给的目标，不应影响真实转移函数。若 WM 输入任务，模型可能学到任务相关 shortcut，而不是物理因果律，导致外推和调度不可靠。任务应进入策略和成功预测器，而非基础动力学预测。

**评分要点：** 必须提到物理因果律。

## Actuator and Hardware

### Q011. [[Actuator2RigidDynamicsModel_gap]] 的核心命题是什么？

**标准答案：** 在高动态灵巧操作中，电流不等于关节力矩。从力矩指令到指尖输出力之间存在电磁非线性、传动摩擦、温度漂移、丝杠效率、连杆耦合和反馈延迟。若把电流推算力矩当真值，策略和 WM 都会学到错误因果关系。

**评分要点：** 必须说出“电流不等于关节力矩”。

### Q012. L25 手的 CAN 总线为什么会造成 sim-to-real gap？

**标准答案：** CAN 1Mbps 下 16 DOF 指令和触觉分帧传输存在仲裁延迟、指间相位差和 5-20ms 不确定延迟。仿真通常假设同步执行，真机却是异步、带随机延迟的执行器系统，导致高频动作落地时间和幅值都偏离策略预期。

**评分要点：** 必须提到异步延迟和指间相位差。

### Q013. 为什么 $\tau_{fb}$ 不能作为 reward 或 WM 预测目标？

**标准答案：** $\tau_{fb}$ 多由电流和标称 $K_t$ 估算，受温度、摩擦、传动和电机轴到关节端映射污染。若作为 reward，策略可能学会降低虚假力矩而非完成任务；若作为 WM 目标，会让模型拟合不可靠量。它只能作为 Actuator Model 输入特征。

**评分要点：** 必须讲出 reward hacking 和测量污染。

### Q014. 温度 $T_{motor}$ 为什么是 Actuator Model 的关键输入？

**标准答案：** 温度影响绕组电阻、力矩常数、热衰减和电流响应，相同指令在不同温度下输出力矩不同。L25 空心杯电机热容小，高动态运行中温度快速变化，因此温度是时变动力学参数的可观测隐变量。

**评分要点：** 必须说出温度改变输出能力。

### Q015. stick-slip 在 L25 丝杠传动中如何影响控制？

**标准答案：** 速度过零时静摩擦大，低力矩指令可能被吞噬；突破静摩擦后又突然滑动，造成不连续响应。策略若不知道这一模式，会在细微指尖控制中出现延迟、跳变和过冲。Actuator Model 需要历史动作、速度和温度来推断 stick-slip 状态。

**评分要点：** 必须提到静摩擦吞噬和突破后跳变。

### Q016. [[Idea-002-Latency-Aware-Actuator]] 的 latency token FiLM 解决什么？

**标准答案：** 它把每个关节的 CAN latency 历史编码为 token，通过 FiLM 调制 Actuator Network，使网络根据当前延迟模式调整指令到力矩/状态响应的映射。这样真机只需微调少量 FiLM/latency encoder 参数，而不破坏 Rigid Dynamic Model。

**评分要点：** 必须提到 latency-conditioned FiLM 和 frozen-rigid。

### Q017. LAAA 的 ≤5 分钟真机适配为什么需要 PE 思想？

**标准答案：** 短数据只有在充分激发延迟、温度、低速/高速和 stick-slip 模式时才可辨识相关参数。若 scripted motion 太单一，模型可以拟合训练轨迹但不能泛化。PE 条件提醒我们要设计覆盖关键 actuator 模式的激励轨迹。

**评分要点：** 必须说明短数据必须覆盖模式。

### Q018. 数据驱动 LMI 证书在 Actuator 适配中判断什么？

**标准答案：** 它把短真机轨迹写成 $X_+=AX_-+BU_-+W_-$，在噪声集合内检查是否存在共同 Lyapunov 矩阵，保证所有与数据一致的局部模型都稳定。若 LMI 不可行，说明数据覆盖不足或噪声界不合理，不应盲目部署适配模型。

**评分要点：** 必须提到共同 Lyapunov 证书和不可行含义。

## Real-Robot RL Ideas

### Q019. [[Idea-001-Tactile-Anchored-Reward]] 为什么能无 GT pose 做真机 reward？

**标准答案：** TAR 用触觉接触图与目标接触拓扑的相似度、WM 触觉预测对数似然和 ensemble disagreement 惩罚构造内生 reward。它不依赖外部位姿，而是把“触觉演化是否符合任务和已知动力学”作为稠密信号。

**评分要点：** 必须说出三项 reward 组成。

### Q020. TAR 中 WM 触觉预测对数似然代表什么？

**标准答案：** 它衡量真实触觉下一步是否落在 WM 预测的已知动力学流形内。高似然表示动作产生了模型理解的、物理一致的接触演化；低似然可能表示 OOD、滑移、掉落或模型不确定。它是无 GT pose 的动力学一致性信号。

**评分要点：** 必须解释为动力学一致性。

### Q021. TAR 中为什么还要惩罚 ensemble disagreement？

**标准答案：** 仅最大化 WM 似然可能让策略钻模型漏洞或停在模型过度自信区域；disagreement 惩罚降低对认知不确定区域的冒险，避免真机 AWAC 在 WM 不懂的区域激进优化。它是防 model exploitation 的安全项。

**评分要点：** 必须说出防止钻 WM 漏洞。

### Q022. [[Idea-008-Physics-Aware-PER]] 的优先级应如何设计？

**标准答案：** 不应只按 TD error，而应根据 actuator residual、rigid dynamics residual、tactile prediction error 等物理残差加权。这样 replay 更关注真实系统中模型错得有物理意义的样本，提高 WM 更新数据效率。

**评分要点：** 必须提到多类物理 residual。

### Q023. [[Idea-012-WPTE-Tactile-Encoder]] 为什么适合作为 P0？

**标准答案：** 触觉编码器是 TAR、contact feasibility、WM 预测和真机策略观测的共同基础。用 WM forward prediction 作为 pretext，可在仿真或无标签数据中训练触觉表征，提高 zero-shot transfer。它是许多后续 idea 的公共依赖。

**评分要点：** 必须说出触觉表征基础设施价值。

### Q024. [[Idea-015-Reset-Free-Autonomy]] 为什么是其它真机 idea 的基础设施？

**标准答案：** 真机 RL 最大隐藏成本是人工 reset。没有自动恢复，任何在线微调都受人工干预、时间和安全限制。Reset-Free 用 inverse recovery task、简单视觉触发和安全网让机器人连续运行，才能规模化收集真实数据。

**评分要点：** 必须强调 reset 是真机数据瓶颈。

### Q025. Reset-Free 中 inverse task 的直觉是什么？

**标准答案：** 在 latent task space 中，reset 可看作把当前状态带回 home state 的反向任务。既然 WMTS 能生成和蒸馏任务策略，就可训练 recovery policy 作为同一条件策略的一种任务类型，而不是写死人工 reset。

**评分要点：** 必须提到 latent inverse task。

### Q026. [[WMTS_Reliability_Extensions]] 的三类风险量是什么？

**标准答案：** Dynamics epistemic uncertainty 衡量 WM 是否理解该任务；actuator feasibility 衡量命令能否被硬件执行，如 $\rho_{act}$ 和 actuator ensemble 方差；contact topology feasibility 衡量预测接触路径是否合理。三者共同决定任务或动作块是否值得执行。

**评分要点：** 三类风险必须完整。

### Q027. Reliability Extensions 为什么强调“更有信息但可控”，而不是“越难越好”？

**标准答案：** 真机任务若只追求难或新奇，可能进入 actuator 不可执行、接触拓扑不可能或安全风险高的区域。可靠调度应选择能降低模型不确定性、靠近能力边界、但仍满足硬件和接触可行性的任务。这比单纯 maximization disagreement 更适合真机。

**评分要点：** 必须讲出 novelty 与 feasibility 的平衡。

### Q028. Solve Queue、Probe Queue、Reject Queue 如何分流？

**标准答案：** Solve Queue 包含 WM 不确定性中等、执行器和接触风险低的任务，交给 Oracle/Generalist 训练；Probe Queue 包含 WM 不确定性高但风险低的任务，用于补数据；Reject Queue 包含 actuator/contact 风险高任务，不执行，可作为生成器负样本。

**评分要点：** 三个队列去向必须清楚。

### Q029. Actuator-Rigid counterfactual loss 试图防止什么？

**标准答案：** 它防止 Actuator Model 和 Rigid Dynamic Model 相互背锅。如果不同命令历史产生近似相同 $\hat\tau_{link}$，Rigid Model 预测应一致。这样刚体模型只依赖真实传入力矩，而不是偷偷利用 actuator 历史弥补错误。

**评分要点：** 必须说出相同 link torque 应导致相同 rigid prediction。

### Q030. Look-ahead Safety Filter 为什么不能只看成功率均值？

**标准答案：** 均值成功率可能掩盖 ensemble 方差、actuator 风险和接触风险。真机安全应看 pessimistic lower confidence bound，如均值减不确定性惩罚，再加温度、力矩和接触约束。否则会放行高方差的危险动作块。

**评分要点：** 必须提到 LCB 或不确定性惩罚。

### Q031. [[Idea-004-WM-Guided-Diffusion]] 的 test-time guidance 与重新训练策略有什么区别？

**标准答案：** Test-time guidance 在扩散反向过程或动作候选上用 WM score 修正动作，不需要重新训练主策略。它适合部署时根据当前 WM 风险快速调整，但受 WM 准确性限制，不能替代长期数据更新。

**评分要点：** 必须说出推理时修正和 WM 依赖。

### Q032. [[Idea-010-EBM-Mode-Mismatch]] 如何用于 sim-to-real 诊断？

**标准答案：** EBM 可学习仿真分布或成功模式的能量支撑，真机样本若落在高能区域，表示与仿真模式不匹配。它可触发特定适配，如 actuator、contact、tactile 或 DR 更新，而不是笼统认为策略失败。

**评分要点：** 必须说明高能代表模式 mismatch。

### Q033. [[Idea-013-Stick-Slip-Mode-Switching]] 为什么可能需要双子策略？

**标准答案：** stick 和 slip 阶段动力学差异大，慢速贴附和快速突破需要不同动作风格。双子策略 slow/burst 加 WM dispatcher 可根据触觉和速度判断模式，切换到合适控制策略，提高鲁棒性。

**评分要点：** 必须区分 stick 与 slip 的控制需求。

### Q034. [[Idea-014-WM-Gradient-Adaptive-DR]] 为什么用 WM 输入梯度调 DR？

**标准答案：** WM 对某个物理参数或观测维度的梯度大，说明预测对该维度敏感，sim-to-real gap 也更可能影响任务。用梯度分配 DR 方差预算可比均匀随机化更有针对性，把随机化集中在关键物理维度。

**评分要点：** 必须说出敏感维度获得更大 DR 预算。

### Q035. 面试官追问：WMTS 的最大失败风险是什么，你如何缓解？

**标准答案：** 最大风险是 WM 被策略利用或调度到硬件不可执行/接触不可能任务，导致真机危险。缓解包括 actuator/contact reliability heads、LCB safety filter、短 horizon rollout、BC 正则、ensemble uncertainty、数据驱动 LMI 证书、reset-free 安全网和人工急停。系统必须把 world model 当成有不确定性的工具，而不是绝对物理引擎。

**评分要点：** 必须包含 model exploitation 和多层安全机制。

## Extended Questions

### Q036. WMTS 中 Task Generator 的 fitness 为什么不能只最大化 novelty？

**标准答案：** 只最大化 novelty 会把任务推向物理不可能、硬件不可执行或安全风险高的区域。Fitness 应同时考虑 generalist 边界、world model uncertainty、actuator feasibility、contact feasibility 和安全约束，选择有信息但可控的任务。

**评分要点：** 必须说明 novelty 与 feasibility 的平衡。

### Q037. VAE latent task space 如何可能引入任务偏差？

**标准答案：** VAE 学到的 latent 受训练任务分布限制，可能把未见但重要的任务模式压缩得很差，或让距离相近的 latent 对应物理差异很大的任务。需要 latent probing、coverage 评估和生成任务物理验证。

**评分要点：** 必须提到 latent 分布限制。

### Q038. CMA-ES 为什么适合 WMTS 的任务搜索？

**标准答案：** 任务 fitness 可能不可微、含仿真 rollout、uncertainty 和安全指标，CMA-ES 可在连续 latent 空间做黑盒优化，并适应非凸多峰 landscape。代价是样本成本高，需要可靠过滤。

**评分要点：** 必须说明黑盒非凸优化。

### Q039. Oracle Specialist 生成的数据如何避免污染 Generalist？

**标准答案：** 需要过滤仿真伪影、标注特权信息不可部署、验证轨迹可由真实观测条件复现，并用 hindsight relabeling 只保留动力学合理片段。否则 Generalist 会学到依赖特权或不可执行的动作。

**评分要点：** 必须提到特权依赖和伪影过滤。

### Q040. Oracle 与 Generalist 的能力差距如何衡量？

**标准答案：** 可比较同一任务上 Oracle 成功率、Generalist 成功率、动作分布距离、失败相位和需要特权信息的程度。差距大的任务适合蒸馏或课程，但若差距来自不可部署信息，则需重设计观测。

**评分要点：** 必须包含成功率和信息可得性。

### Q041. Generalist Diffusion Policy 的 action chunk 长度如何选择？

**标准答案：** 长度应覆盖一个局部技能或接触相位，使 diffusion 表达短程计划；但不能长到安全层无法及时中断。需要根据控制频率、任务相位、模型延迟和真机风险消融选择。

**评分要点：** 必须说明局部计划与反馈延迟 trade-off。

### Q042. CFG guidance weight 在 WMTS 中过高会有什么后果？

**标准答案：** 过高会让动作过度追随任务条件或 WM score，偏离 Oracle/真实动作流形，导致不自然、不可执行或高风险动作；过低则条件弱，任务跟随不足。应结合 safety verifier 调节。

**评分要点：** 必须提到流形偏离和任务跟随不足。

### Q043. Diffusion Generalist 如何处理多模态 Oracle 解？

**标准答案：** 同一任务可能有多条可行接触/动作路径，diffusion 通过去噪分布建模多峰动作，而不是均值回归。训练时应保留多样 Oracle 解，并避免只蒸馏单一最短轨迹。

**评分要点：** 必须说明多峰动作分布。

### Q044. WMTS 中 world model 的 ensemble size 如何影响调度？

**标准答案：** Ensemble 太小不确定性估计不稳，太大计算成本高。调度依赖 disagreement 判断 epistemic uncertainty，因此 ensemble size 要足以区分模型无知和 aleatoric 噪声，并通过校准曲线验证。

**评分要点：** 必须提到 uncertainty calibration。

### Q045. WMTS 的 world model 为什么需要多头预测？

**标准答案：** 任务调度需要不同风险信号，如状态转移、触觉、接触拓扑、actuator residual、success probability 和 uncertainty。单一 next-state head 容易忽略调度需要的关键后果。

**评分要点：** 必须列出多个预测头。

### Q046. WM 不输入任务 $C$ 是否意味着完全不能用目标信息？

**标准答案：** 基础 transition head 不应输入任务，因为物理转移与任务无关；但 success/reward evaluator、scheduler 和 policy 可以输入任务，判断轨迹是否满足目标。要把物理预测和任务评价分开。

**评分要点：** 必须区分 transition 与 evaluator。

### Q047. Actuator Model 输出应是什么更合理？

**标准答案：** 可输出关节下一状态、link torque proxy、tracking residual、feasibility score 或动作响应分布，而不是污染严重的 raw current torque 作为真值。输出应与真实可观测和下游 rigid model 接口一致。

**评分要点：** 必须说明输出要服务接口且可靠。

### Q048. Rigid Dynamic Model 的输入为什么应接收 actuator 后的有效动作？

**标准答案：** 刚体/接触动力学由实际传递到连杆/指尖的运动或力决定，而非策略原始命令。若直接用原始命令，Rigid Model 会把执行器延迟和摩擦也学进去，破坏解耦。

**评分要点：** 必须说明避免 actuator gap 污染 rigid model。

### Q049. Frozen-rigid 真机适配的前提是什么？

**标准答案：** 前提是仿真到真机主要 gap 来自动作到关节响应的 actuator layer，而物体刚体/接触模型在局部仍可用。若真实接触摩擦或物体参数也大幅偏离，只 frozen-rigid 会适配不足。

**评分要点：** 必须说明适用假设。

### Q050. L25 CAN 延迟为什么不只是常数延迟？

**标准答案：** CAN 有仲裁、总线负载、分帧、指间消息顺序和触觉/控制竞争，延迟随时间和关节变化，造成异步相位差。常数延迟模型无法捕捉这些随机和结构化变化。

**评分要点：** 必须提到异步和时变延迟。

### Q051. 为什么 latency token 要按关节或手指建模？

**标准答案：** 不同关节消息到达时间和控制周期可能不同，导致手指间相位偏差。全局 latency token 会平均掉局部差异，无法解释多指协同时序错误。

**评分要点：** 必须说明指间相位差。

### Q052. LAAA 的 scripted motion 应包含哪些片段？

**标准答案：** 应包含低速/高速运动、速度过零、小幅 dithering、大幅阶跃、不同负载姿态、持续高负载升温和多指同步/异步动作。这样覆盖延迟、stick-slip、温度和耦合模式。

**评分要点：** 必须列出多种激励模式。

### Q053. LAAA 适配中为什么要保留 validation motion？

**标准答案：** 短数据容易过拟合 scripted trajectory。保留未用于训练的 motion 可验证 actuator model 是否泛化到不同速度、温度和相位，而不是记住一段轨迹。

**评分要点：** 必须说明防短数据过拟合。

### Q054. LMI 证书不可行时第一步应检查什么？

**标准答案：** 先检查数据是否充分激励、噪声界是否合理、状态尺度是否归一化、模型阶数是否匹配和是否存在异常样本。不可行不等于系统不稳定，可能是数据或假设问题。

**评分要点：** 必须列出数据/噪声/尺度检查。

### Q055. 为什么 $\tau_{fb}$ 可作为输入特征但不能作为监督真值？

**标准答案：** 作为输入，它提供电流和负载的粗线索，模型可结合温度、速度和历史学习其偏差；作为真值，它会把污染量当目标，强迫模型拟合错误物理。输入可噪，监督目标必须更可信。

**评分要点：** 必须区分 noisy feature 与 corrupted label。

### Q056. L25 stick-slip 如何影响 diffusion action chunk？

**标准答案：** Chunk 中若包含低速过零或微小反向动作，真实执行可能被静摩擦吞噬或突然突破，导致 chunk 实际轨迹与生成计划偏离。策略需要 actuator-aware decoder 或 safety verifier 检查这些片段。

**评分要点：** 必须说明低速过零风险。

### Q057. 温度模型应预测绝对温度还是温升风险？

**标准答案：** 两者都有用。绝对温度用于硬件安全阈值，温升风险用于预测未来动作是否会触发限流或性能下降。调度和 safety filter 更关心未来风险，而日志和诊断需要绝对曲线。

**评分要点：** 必须区分当前状态和未来风险。

### Q058. TAR 的触觉拓扑相似度如何避免被“用力压住”作弊？

**标准答案：** 需要加入过压惩罚、接触面积/压力范围约束、滑移和动作能耗指标，并用 WM likelihood 检查动态一致性。否则策略可能通过大力挤压得到接触拓扑相似但不安全的 reward。

**评分要点：** 必须说明过压 reward hacking。

### Q059. TAR 中 target contact topology 从哪里来？

**标准答案：** 可来自 Oracle 轨迹、仿真成功轨迹、任务几何先验或人工指定的接触模式。关键是目标拓扑必须和真机传感器坐标对齐，并允许多种可行接触模式而非唯一模板。

**评分要点：** 必须提到来源和多模态目标。

### Q060. WPTE 触觉 encoder 的 pretext task 为什么选择 forward prediction？

**标准答案：** Forward prediction 迫使 encoder 保留当前触觉、动作和下一步接触演化之间的因果信息，比单纯重建更接近控制需求。它能学习哪些触觉变化会影响未来状态。

**评分要点：** 必须说明预测动作后果。

### Q061. WPTE 如何验证 encoder 真的学到控制相关触觉？

**标准答案：** 做滑移/接触 probe、下游 TAR/RL performance、触觉延迟/打乱消融、跨物体材质泛化和固定动作 replay 预测误差。只看 pretext loss 不够。

**评分要点：** 必须包含 probe 和下游控制。

### Q062. Physics-Aware PER 如何防止 TD error 偏向 reward 噪声？

**标准答案：** 它把优先级部分建立在物理残差上，如 actuator/rigid/tactile prediction error，减少纯 TD error 被 noisy reward 或函数逼近误差支配。这样 replay 更关注真实模型缺口。

**评分要点：** 必须说明物理残差补充 TD error。

### Q063. PA-PER 中 actuator residual 和 contact residual 应如何分开使用？

**标准答案：** Actuator residual 高的样本优先更新 actuator model 或 latency adaptation；contact residual 高的样本优先更新 rigid/contact/tactile head。分开可定位 gap，不把所有错误都送给同一个模型。

**评分要点：** 必须说明 residual routing。

### Q064. Reset-Free Autonomy 的 terminal detector 应检测什么？

**标准答案：** 应检测任务成功、失败、物体掉落、危险姿态、温度/力矩超限、传感器异常和需要 recovery 的状态。Detector 的误报/漏报直接影响无人训练安全。

**评分要点：** 必须包含成功、失败和安全异常。

### Q065. Reset-Free 中 recovery policy 的 reward 应如何设计？

**标准答案：** Reward 应鼓励回到安全 home/initial distribution、减少碰撞和过载、缩短恢复时间、保持物体在 workspace 内，并避免把任务物体推到不可恢复区域。Recovery 目标不同于主任务成功。

**评分要点：** 必须区分 recovery reward 与 task reward。

### Q066. Reset-Free 系统为什么需要简单规则与学习策略结合？

**标准答案：** 学习 recovery 处理复杂状态，简单规则处理确定安全边界，如急停、限位、温度和 workspace。规则提供硬安全底线，学习提供灵活恢复。

**评分要点：** 必须说明 hard rule + learned recovery。

### Q067. Reliability head 的训练标签如何获得？

**标准答案：** 可从仿真/真机 rollout 的成功失败、actuator saturation、contact infeasibility、temperature violation、ensemble error 和人工标注获得。标签应分类型，而不是单一危险标志。

**评分要点：** 必须列出多类风险标签。

### Q068. 为什么 reliability head 需要校准而非只分类准确？

**标准答案：** 调度和安全过滤需要概率或风险分数可解释，分类准确高但过度自信会放行危险任务。需要 reliability diagram、coverage 和 LCB 验证。

**评分要点：** 必须提到概率校准。

### Q069. Solve/Probe/Reject Queue 的边界如何动态调整？

**标准答案：** 随着 WM 学习和真机数据增加，不确定性会下降、可行性估计会变化，原 Probe 可变 Solve，原 Reject 也可能通过硬件/课程调整变 Probe。阈值应根据校准误差和安全预算动态更新。

**评分要点：** 必须说明队列不是固定标签。

### Q070. Reject Queue 是否完全没用？

**标准答案：** 不是。Reject 任务可作为 task generator 的负样本、reliability head 的训练数据和人工审查对象，也能揭示能力边界。只是当前不应执行。

**评分要点：** 必须说明拒绝样本仍有学习价值。

### Q071. Actuator-Rigid counterfactual loss 如何构造样本对？

**标准答案：** 找到不同命令历史但 actuator model 预测相近 effective link torque/运动响应的样本对，要求 rigid model 对下一物体状态预测一致。也可通过仿真干预生成相同 torque 的反事实样本。

**评分要点：** 必须说明相同有效输入对应一致刚体预测。

### Q072. Counterfactual loss 的风险是什么？

**标准答案：** 若 effective torque 估计本身不准，强制一致会压掉真实差异；若隐藏接触状态不同，同 torque 也可能产生不同结果。需要条件匹配接触状态和置信度阈值。

**评分要点：** 必须提到 torque 估计和接触状态。

### Q073. Look-ahead Safety Filter 的 horizon 如何选择？

**标准答案：** Horizon 应覆盖动作 chunk 和近期接触风险，但不能长到 WM 误差过大。可使用短 horizon、多次重规划和 uncertainty 增长惩罚。真机上宁可短而可信。

**评分要点：** 必须说明 chunk 覆盖和误差累积。

### Q074. LCB safety filter 的惩罚系数如何调？

**标准答案：** 惩罚系数反映风险偏好和不确定性校准。可用 held-out 真机数据选择，使低 LCB 的动作确实更危险；如果系数太大过保守，太小会放行高方差动作。

**评分要点：** 必须说明校准和保守性 trade-off。

### Q075. WM-Guided Diffusion 的 guidance score 应包含哪些项？

**标准答案：** 可包含任务成功预测、WM likelihood、ensemble LCB、actuator feasibility、contact topology feasibility、温度风险和动作先验距离。必须避免单一成功分数压过安全项。

**评分要点：** 必须列出任务和安全项。

### Q076. Test-time WM guidance 如何避免破坏 diffusion prior？

**标准答案：** 使用适度 guidance weight、动作先验正则、候选 reranking 而非强梯度、以及安全重采样。若 guidance 过强，会生成不在训练动作流形内的动作。

**评分要点：** 必须提到 prior regularization。

### Q077. EBM Mode Mismatch 如何与 PA-PER 结合？

**标准答案：** EBM 检测真机样本偏离仿真/成功模式，PA-PER 根据偏离类型和物理 residual 提高 replay 优先级。前者识别 mismatch，后者决定哪些模型或策略更新。

**评分要点：** 必须说明检测和重放优先级分工。

### Q078. Stick-Slip 双子策略的 dispatcher 输入应包含什么？

**标准答案：** 应包含关节速度、速度符号变化、跟踪误差、电流/负载、温度、触觉剪切和动作历史。它需要判断当前是 stick、pre-slip 还是 slip/burst 模式。

**评分要点：** 必须列出速度、负载、触觉、历史。

### Q079. Stick-Slip 双子策略为什么需要 hysteresis switching？

**标准答案：** 若 dispatcher 在阈值附近频繁切换 slow/burst 策略，会引入抖动和不稳定。Hysteresis 让切换有进入/退出阈值差，保持模式一段时间，提高稳定性。

**评分要点：** 必须说明防频繁切换。

### Q080. WM-Gradient Adaptive DR 如何避免把噪声维度误判为敏感维度？

**标准答案：** 需要用多模型一致梯度、时间平滑、物理先验和真机 residual 验证。若某维梯度大但对真实误差无贡献，就不应扩大随机化。敏感性应以预测和真实 gap 共同确认。

**评分要点：** 必须说明梯度需校准。

### Q081. Adaptive DR 与 system ID 如何互补？

**标准答案：** System ID 缩小已知参数误差，Adaptive DR 在仍不确定或敏感的维度扩大训练覆盖。ID 提供中心，DR 提供鲁棒半径，两者共同定义参数分布。

**评分要点：** 必须说明中心与半径。

### Q082. WMTS 中 BC regularization 应约束什么分布？

**标准答案：** 应约束 diffusion/Generalist 输出不偏离 Oracle/真实成功动作分布，尤其在 WM guidance 或 online RL 时防止 OOD 动作。约束对象可以是 action chunk、latent action 或 skill parameter。

**评分要点：** 必须说明防 OOD action。

### Q083. 为什么 WMTS 的真机微调不能只优化 TAR reward？

**标准答案：** TAR reward 可能被触觉拓扑或 WM likelihood 漏洞利用，且不一定覆盖全局任务成功。真机微调还需安全约束、success check、human intervention、OPE/LCB 和失败模式监控。

**评分要点：** 必须说明单一内生 reward 不足。

### Q084. WMTS 如何处理 no-GT-pose 与最终任务评价的矛盾？

**标准答案：** 训练 reward 可用触觉/WM 内生信号，但评估应尽可能用独立真值或人工验收，如外部相机、任务成功传感器或视频标注。训练无需 GT 不等于评估也不需要客观标准。

**评分要点：** 必须区分训练信号和评估信号。

### Q085. 为什么 WMTS 需要任务局部条件 $C_{local,t}$？

**标准答案：** 长任务全局目标太粗，局部条件提供当前阶段的子目标、接触模式或 waypoint，让 diffusion chunk 生成与当前相位匹配的短程动作。它连接 scheduler 的任务规划和低层策略。

**评分要点：** 必须说明局部子目标。

### Q086. $C_{local,t}$ 设计不当会怎样？

**标准答案：** 若过粗，策略不知道当前阶段；若过细或不可部署，Generalist 会依赖真机没有的信息；若与动作 chunk 时间不匹配，会产生相位错位。需要可观测、可执行且时间对齐的条件。

**评分要点：** 必须说明粒度和可部署性。

### Q087. WMTS 中哪些模块最需要版本化日志？

**标准答案：** Task generator fitness、Oracle 配置、Generalist 数据版本、WM ensemble checkpoint、actuator adaptation 参数、reliability thresholds、安全过滤和真机硬件状态都必须版本化。否则无法复盘调度决策。

**评分要点：** 必须包含模型、数据、阈值和硬件。

### Q088. 如何评估 WMTS Scheduler 是否真的有用？

**标准答案：** 比较随机任务生成、难度手工课程、uncertainty-only 和 full reliability scheduler，在样本效率、能力边界扩展、真机安全违反和最终泛化上的差异。还要展示 scheduler 选择任务的可解释性。

**评分要点：** 必须包含 scheduler baseline。

### Q089. Scheduler 选择任务的可解释性应展示什么？

**标准答案：** 展示每个任务的 WM uncertainty、actuator risk、contact risk、predicted learning gain、队列归属和执行结果。这样能说明任务为何被 Solve/Probe/Reject，而不是黑箱采样。

**评分要点：** 必须列出风险和学习收益。

### Q090. WMTS 的最小原型应先实现哪些模块？

**标准答案：** 最小原型可先实现固定任务集、Oracle 轨迹、Generalist diffusion、WM ensemble 和离线 reliability scoring；真机前先做 actuator replay 和 look-ahead filter。Task generator 和 reset-free 可随后扩展。

**评分要点：** 必须给出分阶段 MVP。

### Q091. 为什么 WMTS 不应一开始就全系统上真机？

**标准答案：** 模块多且耦合强，直接真机会难以定位失败并增加硬件风险。应先逐模块验证：actuator、触觉 encoder、WM calibration、policy execution、安全 filter，再闭环。

**评分要点：** 必须说明分层验证降低风险。

### Q092. WMTS 与普通 active learning 的差别是什么？

**标准答案：** 普通 active learning 关注标注信息增益；WMTS 关注机器人任务、动作可执行性、接触风险和策略能力边界。它是 embodied active learning，需要把物理执行和安全放入采样决策。

**评分要点：** 必须强调 embodied constraints。

### Q093. WMTS 的论文贡献如何避免过于庞杂？

**标准答案：** 应选择一个清晰主轴，如 reliability-aware world model scheduling，并把 diffusion、Oracle、actuator model 都作为服务该主轴的组件。每个实验回答 scheduler 如何提升学习效率或安全，而不是展示所有模块。

**评分要点：** 必须说明收束主贡献。

### Q094. WMTS 中最适合首先投稿的子方向是什么？

**标准答案：** 可优先选择 actuator-aware world model / latency-aware adaptation，因为问题明确、数据需求可控、与真机 gap 强相关；或选择 tactile-anchored reward 作为无 GT 真机 RL 子方向。最终取决于已有实验哪条链最先闭合。

**评分要点：** 必须基于闭合实验链选择。

### Q095. 如何证明 Actuator Model 真正改善下游任务？

**标准答案：** 除 actuator prediction error，还要比较下游 WM rollout、policy success、catch timing、safety filter false reject/accept 和 sim-to-real residual。只降低关节 MSE 不足以证明任务价值。

**评分要点：** 必须包含下游任务指标。

### Q096. 如何证明 TAR reward 与真实成功相关？

**标准答案：** 在有 GT 或人工标注的小测试集上计算 TAR 与成功/进度的相关性，比较不同 TAR 组件 ablation，并检查高 TAR 低成功的失败案例。Reward 必须经过外部标准校准。

**评分要点：** 必须包含相关性和反例分析。

### Q097. 如何证明 WPTE encoder 可迁移？

**标准答案：** 在未见物体/材质/接触速度上测试 forward prediction 和下游控制，比较从零训练、冻结 encoder 和微调 encoder。若少量微调即可提升，说明表征有迁移价值。

**评分要点：** 必须包含 OOD 和微调对照。

### Q098. 如何证明 Reset-Free 不是隐藏人工干预？

**标准答案：** 报告连续运行时长、自动 reset 次数、人类介入次数、失败恢复率、急停次数和平均 cycle time，并公开介入规则。若大量人工调整未报告，就不能称 reset-free。

**评分要点：** 必须包含人类介入统计。

### Q099. 面试官追问：WMTS 最容易被质疑的点是什么？

**标准答案：** 最容易被质疑系统太复杂、WM 不可靠、真机安全不足、贡献不聚焦、以及每个模块是否真的必要。回答必须用分阶段消融、calibration、reliability scheduler 对照和真实失败分析证明主轴。

**评分要点：** 必须列出质疑并给出证据策略。

### Q100. 请总结 WMTS 项目的核心主线。

**标准答案：** WMTS 的主线是让 world model 从预测器变成可靠调度器：它发现能力边界任务，组织 Oracle 和 Generalist 学习，估计执行器/接触/动力学风险，并用 LCB、安全过滤和真机反馈闭环更新。目标不是相信模型，而是让模型带着不确定性管理学习和部署。

**评分要点：** 必须概括任务调度、策略学习、风险估计和真机闭环。
