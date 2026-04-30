---
tags:
  - quiz
  - papers-recap
  - control
  - safety
  - real-world-rl
aliases:
  - Control Safety Real World RL Paper Quiz
created: 2026-05-01
related:
  - "[[ControlTheory]]"
  - "[[Optimization]]"
  - "[[ReinforcementLearning]]"
---

# 08 Papers: Control, Safety, Real-World RL

### Q001. [[SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning]] 的系统贡献是什么？

**标准答案：** SERL 提供真实世界机器人 RL 的完整软件栈，集成 sample-efficient off-policy 算法、自动奖励推断、重置学习和阻抗控制器，使真实任务能在 25-50 分钟内达到高成功率。它的价值在于工程闭环，而不是单一算法 trick。

**评分要点：** 必须提到软件栈和真实闭环组件。

### Q002. [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning]] 为什么能比纯 IL 提升明显？

**标准答案：** 纯 IL 只模仿示范分布，遇到错误状态难恢复；HIL-SERL 在在线 RL 中加入人类校正，将失败边界附近的高价值经验纳入训练。它同时利用 RL 的任务指标优化和人类对安全/纠错的直觉。

**评分要点：** 必须提到错误状态分布和人类校正。

### Q003. [[RL-100 - Performant Robotic Manipulation with Real-World RL]] 的三阶段管线为什么适合真实部署？

**标准答案：** 模仿预训练提供安全初始策略，迭代离线 RL 利用收集数据改进而不频繁冒险，在线 RL 微调针对真实环境优化性能。配合一致性蒸馏降低推理成本，使策略既可靠又高效。

**评分要点：** 必须说明三个阶段的安全与效率作用。

### Q004. [[RLT - Precise Manipulation with Efficient Online RL Tokens]] 为什么能用 15 分钟数据改进精密操作？

**标准答案：** 它把大模型感知压缩为 RL token，在线 actor-critic 只在紧凑控制表征上学习残差或动作编辑，降低样本复杂度。它不是从零学视觉和语言，而是在已有 VLA 表征上做任务指标优化。

**评分要点：** 必须提到在预训练表征上轻量 RL。

### Q005. [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] 解决了 latent CBF 的哪两个关键问题？

**标准答案：** 一是分类器式 margin function 梯度容易饱和，导致优化安全过滤器无法产生有效修正；二是安全策略和任务策略分布失配，使值函数或安全估计不准。LatentCBF 关注如何在隐空间中训练可用于平滑安全过滤的函数。

**评分要点：** 必须提到梯度饱和和分布失配。

### Q006. [[Reachability Constrained Reinforcement Learning]] 与 CBF 的差异是什么？

**标准答案：** RCRL 用可达性分析学习最大可行集边界，目标是理论上尽可能不保守地保证持续安全；CBF 通常依赖给定 barrier 或局部约束，可能更保守。RCRL 更强调从可达集角度定义安全状态集合。

**评分要点：** 必须提到最大可行集。

### Q007. [[Safe Model-based Reinforcement Learning with Stability Guarantees]] 如何结合 GP 与 Lyapunov？

**标准答案：** GP 建模未知动力学及不确定性，Lyapunov 函数定义吸引域或安全区域。策略优化只能在保证不离开安全吸引域的范围内进行，随着数据增加逐步扩展安全区域。它体现了 model-based learning 和稳定性证书结合。

**评分要点：** 必须说出 GP uncertainty 和 Lyapunov safe set。

### Q008. [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] 的控制理论桥梁是什么？

**标准答案：** 它通过鲁棒控制中的二次约束、偏导数界和 SDP 证书，为 RL 策略提供稳定性验证。核心是把神经策略的非线性影响界定在可分析集合内，再检查闭环系统是否满足稳定性条件。

**评分要点：** 必须提到二次约束和 SDP。

### Q009. [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]] 如何把 Lyapunov 稳定性嵌入网络结构？

**标准答案：** 它设计单调递增且过原点的神经控制器结构，证明在该结构约束下系统具有唯一平衡点和局部指数稳定。Stacked-ReLU 等结构保证单调性，使稳定性不是训练后验证，而是架构内生属性。

**评分要点：** 必须提到单调网络结构。

### Q010. [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] 为什么能减少动作抖动？

**标准答案：** LipsNet 通过多维梯度归一化约束 Actor 的 Lipschitz 常数，使输入小扰动不会被放大为高频动作变化。自适应 Lipschitz 常数允许在需要敏感控制和需要鲁棒平滑之间调整。对灵巧手，这有助于抑制接触附近的抖动。

**评分要点：** 必须连接 Lipschitz bound 与动作平滑。

### Q011. [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]] 中小 Lipschitz 界有什么性能 trade-off？

**标准答案：** 小 Lipschitz 界提高对噪声、扰动和对抗攻击的鲁棒性，但过小会限制策略表达能力和快速反应能力。机器人控制中应根据接触阶段自适应调整，而不是全局越小越好。

**评分要点：** 必须讲出鲁棒性与表达能力权衡。

### Q012. [[Off-Policy Interval Estimation with Lipschitz Value Iteration]] 为什么给 OPE 上下界而不是单点估计？

**标准答案：** 离策略评估在数据覆盖不足时单点估计可能严重偏差。Lipschitz Value Iteration 在与观测一致的 Q 函数集合中寻找最大和最小值，给出可证明区间，表达不确定性。真实机器人决策更需要保守置信区间而非虚假精确值。

**评分要点：** 必须提到数据覆盖不足和可证明区间。

### Q013. [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] 为什么把阻抗作为动作空间？

**标准答案：** 直接力矩动作样本效率低且容易产生不安全接触；末端位移加阻抗增益让策略输出可解释、平滑、跨机器人更可迁移的控制目标。VICES 把低层稳定交互交给阻抗控制器，RL 学高层接触策略。

**评分要点：** 必须说出动作空间结构化和安全柔顺。

### Q014. [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking]] 对灵巧手有什么可迁移思想？

**标准答案：** 它从人类数据学习阻抗参数作为相位、速度和坡度的连续函数。灵巧手也可把刚度、阻尼和平衡点设为任务相位、接触状态、滑移风险或物体属性的函数，实现阶段自适应阻抗，而不是固定 PD 增益。

**评分要点：** 必须把步态相位类比到操作相位。

### Q015. [[Minimalist Compliance Control]] 和 VICES 的核心差别是什么？

**标准答案：** Minimalist Compliance Control 强调不用学习，仅用电流/PWM 估计外力并做导纳控制，是即插即用的顺应层；VICES 把阻抗参数作为 RL 动作空间，让策略学习如何调节柔顺性。前者是控制模块，后者是学习动作参数化。

**评分要点：** 必须区分无需学习控制与 RL 动作空间。

### Q016. [[TARC - Time-Adaptive Robotic Control]] 为什么让策略输出动作持续时间？

**标准答案：** 不同任务阶段需要不同控制频率：接近和等待可低频，接触切换和滑移恢复需高频。TARC 让策略同时决定动作和持续时间，像生物系统一样调节计算和反应速度，实现效率与鲁棒性平衡。

**评分要点：** 必须提到阶段相关控制频率。

### Q017. [[Elastic Time Step Reinforcement Learning, VTS-RL]] 与 TARC 的共同主题是什么？

**标准答案：** 都把时间步或动作持续时间作为策略决策的一部分，而不是固定控制频率。核心是学习“做什么”和“持续多久”。这对机器人节能、降低推理频率和适应不同动态阶段有价值。

**评分要点：** 必须说出 action duration/control frequency learning。

### Q018. [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] 中 Action Persistence 的理论意义是什么？

**标准答案：** 在 $k$ 个决策步重复动作等价于改变控制频率，persistent operator 具有收缩性质，可分析性能损失界。它把控制频率选择从工程超参数变成可理论分析的 RL 结构。

**评分要点：** 必须提到重复动作和收缩/性能界。

### Q019. [[Reinforcement Learning for Control with Multiple Frequencies]] 为什么需要周期性非平稳策略？

**标准答案：** 当不同动作变量有不同频率，如机械臂 50Hz、夹爪 10Hz，任意平稳策略可能无法表达周期性更新结构。AP-AC 用 action persistence 和周期性策略直接优化多频控制，避免把所有维度强行同步到同一频率。

**评分要点：** 必须提到不同动作维度不同频率。

### Q020. [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation]] 为什么用 DMP 加低频 RL 残差？

**标准答案：** DMP 提供平滑、稳定、可解释的高频基础轨迹，RL 残差以较低频率修正接触误差和环境变化。这样既保留示范先验，又避免 RL 从零学习整个轨迹，适合插入等接触密集任务。

**评分要点：** 必须说明基础轨迹和残差分工。

### Q021. [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]] 如何解释 SAC 的数学根源？

**标准答案：** 它从连续时间随机最优控制推导熵正则化目标，展示探索-利用平衡可由 HJB 方程刻画。在 LQ 情形中最优策略为 Gaussian，方差与熵温度和系统噪声相关。这为 MaxEnt RL 提供控制理论解释。

**评分要点：** 必须提到 HJB 和熵正则。

### Q022. [[Unified Policy Evaluation and Improvement - On Off-Policy Classification]] 的两个正交维度是什么？

**标准答案：** 数据来源和更新调度。数据来源区分 on-policy/off-policy/静态数据，更新调度区分如何进行评估和改进。该框架说明 PPO、SAC、IQL、AWAC 等底层同源，差异在采样分布和 KL 正则参照系。

**评分要点：** 必须提到 data source 和 update schedule。

### Q023. [[The Sampling Theorem With Constant Amplitude Variable Width Pulses]] 对控制频率有什么启发？

**标准答案：** 它提醒我们采样不一定只对应等间隔固定宽度脉冲，变量宽度脉冲可携带时间信息。对机器人控制，动作持续时间本身可作为控制自由度，连接到 TARC、VTS-RL 和 action persistence 的思想。

**评分要点：** 必须把 variable width pulses 连接到持续时间动作。

### Q024. 安全 RL 中“训练安全”和“部署安全”有什么区别？

**标准答案：** 训练安全关注探索过程中不损坏系统或进入危险状态；部署安全关注已训练策略在扰动、分布偏移和执行器异常下仍满足约束。前者需要 safe exploration、shielding 和人类干预，后者需要证书、监控、fallback 和 runtime safety filter。

**评分要点：** 必须区分探索期和运行期。

### Q025. 面试官追问：为真机灵巧手 RL 设计一个安全后训练栈。

**标准答案：** 初始策略用 IL/仿真 RL 预训练；真实数据阶段用阻抗控制器和动作限幅执行；安全层检查关节、温度、触觉滑移、接触力和 LCB 成功概率；人类可在线纠正；离线/在线 RL 只在安全过滤后的动作空间中更新；最后用 Lyapunov/CBF/数据驱动 LMI 做局部证书。这样兼顾效率、性能和硬件安全。

**评分要点：** 必须包含预训练、低层控制、安全过滤、人类/证书至少四项。

## Extended Questions

### Q026. [[SERL - A Software Suite for Sample-Efficient Robotic Reinforcement Learning]] 为什么强调 software suite 而非单算法？

**标准答案：** 真实机器人 RL 的瓶颈常在数据采集、reset、奖励、控制器、日志和安全，而不是某个 Bellman loss。SERL 把这些工程闭环整合起来，降低从算法到真机实验的摩擦，体现系统贡献。

**评分要点：** 必须说明真实 RL 需要完整闭环。

### Q027. SERL 中 reset 学习为什么重要？

**标准答案：** 真机任务失败后若每次人工 reset，样本效率和实验连续性都会崩溃。Reset policy 把系统带回可训练初始分布，使在线 RL 可持续运行，并降低人工成本。

**评分要点：** 必须提到减少人工 reset 和持续训练。

### Q028. SERL 的 sample efficiency 来自哪些系统设计？

**标准答案：** 来自演示初始化、off-policy replay、结构化控制器、自动奖励/重置、真实数据高效复用和稳定工程栈。不是单一 trick，而是多环节减少无效探索。

**评分要点：** 必须列出至少三项系统因素。

### Q029. [[HIL-SERL - Precise and Dexterous Robotic Manipulation via Human-in-the-Loop Reinforcement Learning]] 中人类干预如何进入 replay？

**标准答案：** 应记录干预前状态、策略动作、人类纠正动作、执行动作、结果和时间戳。这样 RL 能学习哪些状态需要纠正，以及纠正方向是什么，而不是把干预当普通策略动作混淆。

**评分要点：** 必须说明记录策略动作与人类动作。

### Q030. HIL-SERL 为什么适合 precise manipulation？

**标准答案：** 精密任务的失败边界窄，纯 RL 随机探索容易损坏或远离成功区。人类能在接近失败时提供局部纠正，把稀缺的边界经验转为训练信号，帮助策略学习细粒度恢复。

**评分要点：** 必须提到窄失败边界和局部纠正。

### Q031. Human-in-the-loop 方法如何避免干预偏置？

**标准答案：** 需要记录无干预 rollout、随机或规则化触发、介入频率和人类策略差异，并在训练中区分自主数据与干预数据。否则策略可能只适合某个人的纠正风格。

**评分要点：** 必须提到干预数据分布偏差。

### Q032. [[RL-100 - Performant Robotic Manipulation with Real-World RL]] 的 consistency distillation 可能解决什么？

**标准答案：** 它可把昂贵或多阶段策略压缩成低延迟执行策略，减少推理成本并稳定部署。真实机器人需要高频控制，复杂训练策略不一定能直接上线。

**评分要点：** 必须说明蒸馏降低部署延迟。

### Q033. RL-100 的离线/在线阶段为什么都需要？

**标准答案：** 离线 RL 高效复用已有真实数据，降低冒险；在线 RL 继续采集当前策略分布数据，修正离线分布外问题。二者结合比纯离线或纯在线更适合真机。

**评分要点：** 必须说明数据复用与当前分布适应。

### Q034. [[RLT - Precise Manipulation with Efficient Online RL Tokens]] 为什么 token RL 仍需要安全层？

**标准答案：** Token 降低样本复杂度，但在线 RL 仍会尝试新动作或残差。若 token 缺少接触/硬件风险，策略可能输出危险编辑。安全层负责限制动作、监测失败和过滤不确定决策。

**评分要点：** 必须说明 token 不自动保证安全。

### Q035. RLT 的 online update 应避免改坏哪些能力？

**标准答案：** 应避免破坏预训练感知、语言理解、基础动作先验和安全行为。通常只微调小头、adapter 或 residual，并用 replay/regularization 保留通用能力。

**评分要点：** 必须提到保留预训练能力。

### Q036. [[How to Train Your Latent Control Barrier Function - Smooth Safety Filtering Under Hard-to-Model Constraints]] 为什么 latent space 适合 hard-to-model constraints？

**标准答案：** 一些安全约束难以在原始状态中解析表达，如视觉遮挡、复杂接触或人类偏好。Latent space 可从数据学习安全边界，但必须保证 latent 对控制可微、校准且不丢失危险信息。

**评分要点：** 必须说明学习隐式安全边界。

### Q037. Latent CBF 中 margin 梯度饱和会导致什么？

**标准答案：** 安全过滤器通过梯度知道如何修改动作；若 margin 梯度饱和，优化器看不到有效修正方向，动作可能无法被平滑投影回安全集。分类准确不等于可用于控制过滤。

**评分要点：** 必须说明分类器和可控 barrier 的区别。

### Q038. Latent CBF 如何处理任务策略和安全策略分布失配？

**标准答案：** 需要在任务策略访问的状态动作分布上训练/校准安全函数，使用策略数据、反事实动作、hard negatives 或在线更新。否则安全函数只在安全策略分布上准确，过滤任务动作时失效。

**评分要点：** 必须提到分布匹配到任务策略。

### Q039. [[Reachability Constrained Reinforcement Learning]] 中 reachability 相比 penalty reward 的优势是什么？

**标准答案：** Reachability 关注从当前状态未来是否仍能保持安全，显式约束可行集；penalty reward 只在目标中软惩罚危险，权重不当仍可能违反。Reachability 更适合安全不可违反的场景。

**评分要点：** 必须区分未来可行集和软惩罚。

### Q040. RCRL 的最大可行集为什么可能很难学？

**标准答案：** 最大可行集依赖动力学、控制限制、扰动和约束边界，高维非线性接触系统中边界复杂且数据稀疏。学习误差可能导致过保守或不安全，需要验证和置信边界。

**评分要点：** 必须提到高维边界和数据稀疏。

### Q041. [[Safe Model-based Reinforcement Learning with Stability Guarantees]] 中 safe set expansion 的逻辑是什么？

**标准答案：** 从已知稳定安全区域开始，只允许采集和更新不会离开安全集的数据；随着 GP 不确定性降低和 Lyapunov 条件验证，逐步扩大可安全探索区域。它是保守到逐步扩张的过程。

**评分要点：** 必须说明从小安全集逐步扩大。

### Q042. GP-Lyapunov 方法为什么在灵巧手高维系统上有挑战？

**标准答案：** GP 在高维状态动作中计算和泛化困难，Lyapunov 函数也难构造，接触非光滑破坏平滑假设。可用于低维子系统或局部安全证书，但全手全任务直接套用很难。

**评分要点：** 必须提到高维和非光滑。

### Q043. [[Stability-Certified Reinforcement Learning: A Control-Theoretic Perspective]] 中二次约束如何约束神经策略？

**标准答案：** 通过给神经网络的激活、增益或 Jacobian 建立二次不等式界，把非线性策略包进可分析集合，再用 SDP 检查闭环稳定条件。它把黑箱策略转成可验证对象。

**评分要点：** 必须说明用 QC/SDP 验证闭环。

### Q044. Stability-certified RL 的证书为什么不是万能？

**标准答案：** 证书依赖模型、区域、扰动界和网络假设。若真实系统超出假设，证书不保证安全；证书也可能很保守。必须报告有效区域和假设，而不是宣称全局安全。

**评分要点：** 必须说明假设范围。

### Q045. [[Reinforcement Learning for Optimal Primary Frequency Control - A Lyapunov Approach]] 中单调网络对机器人有什么启发？

**标准答案：** 可通过网络结构强制某些输入-输出关系，如误差越大恢复动作越强、危险越大退让越强。结构性单调约束能把稳定性先验写进策略，而不是训练后祈祷。

**评分要点：** 必须说明结构先验内生稳定。

### Q046. 单调网络在灵巧操作中有什么限制？

**标准答案：** 接触任务常有非单调最优行为，例如先松后夹、先退后进。强制单调可能限制策略表达。应只对明确安全变量施加单调性，如风险到保守动作，而非所有动作维度。

**评分要点：** 必须说明非单调任务策略。

### Q047. [[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control]] 为什么 adaptive Lipschitz 比固定小界更好？

**标准答案：** 固定小 Lipschitz 提高平滑但限制快速响应；自适应界允许在安全平滑和高精度控制间调节。接触稳定阶段可小界，快速纠错阶段可放宽界。

**评分要点：** 必须说明阶段化敏感度。

### Q048. Lipschitz-bound policy 如何影响 sim-to-real？

**标准答案：** 小的输入扰动不会被放大为大动作，能抵抗感知噪声和模型误差，提高迁移鲁棒性。但过强约束会让策略无法快速补偿真实 gap。应与任务动态匹配。

**评分要点：** 必须说明鲁棒与反应速度 trade-off。

### Q049. [[On Robust Reinforcement Learning with Lipschitz-Bounded Policy Networks]] 与 LipsNet 的共同核心是什么？

**标准答案：** 二者都控制策略对输入扰动的敏感度，用 Lipschitz 界降低噪声和对抗扰动造成的动作剧烈变化。差异在具体网络构造和自适应机制。

**评分要点：** 必须提到输入扰动到动作变化的界。

### Q050. Lipschitz 约束为什么不能替代安全约束？

**标准答案：** 平滑策略仍可能平滑地走向危险区域。Lipschitz 只限制变化率，不保证关节、碰撞、温度或接触力满足约束。它应与 CBF/MPC/safety filter 结合。

**评分要点：** 必须区分平滑和安全。

### Q051. [[Off-Policy Interval Estimation with Lipschitz Value Iteration]] 的区间宽度代表什么？

**标准答案：** 区间宽度反映在数据覆盖和 Lipschitz 假设下价值不确定性。宽区间表示候选策略在当前数据下不可可靠评估，应谨慎部署或采集更多数据。

**评分要点：** 必须说明宽区间代表不确定。

### Q052. OPE 区间如何用于真机策略放行？

**标准答案：** 可要求候选策略的下界超过基线或安全阈值才放行，避免只看乐观均值。若区间太宽，则先采集补充数据或缩小策略变化。它是上线前的保守筛选。

**评分要点：** 必须提到用下界放行。

### Q053. [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks]] 为什么提高样本效率？

**标准答案：** 阻抗动作空间内置柔顺和稳定交互先验，RL 不必从原始力矩中学会所有低层物理。动作维度和危险探索都减少，因此真实或仿真样本利用更高效。

**评分要点：** 必须说明结构化动作空间。

### Q054. VICES 类动作空间如何迁移到多指灵巧手？

**标准答案：** 可把每个指尖或接触点的目标位移、刚度和阻尼作为动作，或在接触图上定义局部阻抗。需要处理指间耦合和内力约束，不能只用单一末端阻抗。

**评分要点：** 必须提到多指/多接触扩展。

### Q055. [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking]] 中相位变量为何关键？

**标准答案：** 步态不同相位需要不同阻抗，连续相位变量让阻抗随运动阶段平滑变化。灵巧操作也需要 snap、spin、catch 等相位条件的阻抗调度。

**评分要点：** 必须连接步态相位和操作相位。

### Q056. Data-driven impedance 对安全有什么要求？

**标准答案：** 学到的刚度/阻尼必须为正且有界，变化率不能过大，并需考虑硬件力矩和温度限制。否则数据驱动参数可能在 OOD 状态输出不稳定阻抗。

**评分要点：** 必须提到正定、有界和变化率。

### Q057. [[Minimalist Compliance Control]] 为什么可作为 RL 安全外壳？

**标准答案：** 它在底层提供简单退让和柔顺，使 RL 输出的目标在遇到外力时不会硬顶环境。即使策略不完美，compliance layer 也可降低碰撞冲击和硬件风险。

**评分要点：** 必须说明底层柔顺保护。

### Q058. Minimalist compliance 与 learned residual 如何结合？

**标准答案：** Compliance 提供保守基础响应，learned residual 根据任务状态调整退让幅度、方向或目标。残差应被限幅，不能覆盖底层安全逻辑。

**评分要点：** 必须说明残差不应破坏安全层。

### Q059. [[TARC - Time-Adaptive Robotic Control]] 中时间动作如何影响 credit assignment？

**标准答案：** 策略不仅决定动作，还决定持续时间；奖励要归因到动作内容和保持时长。长持续时间减少决策次数但延迟反馈，短持续时间提升响应但增加噪声和计算。

**评分要点：** 必须说明动作和持续时间共同影响回报。

### Q060. TARC 在真机中如何受到通信延迟约束？

**标准答案：** 如果策略选择很短持续时间但通信和推理延迟较大，实际无法实现高频调整。时间自适应必须考虑端到端延迟、低层插值和安全中断机制。

**评分要点：** 必须提到延迟限制最短持续时间。

### Q061. [[Elastic Time Step Reinforcement Learning, VTS-RL]] 中 elastic time step 解决什么？

**标准答案：** 它允许策略根据状态选择不同时间步，使慢阶段少决策、快阶段多反馈。这样提高效率并匹配任务动态，而不是固定一个折中控制频率。

**评分要点：** 必须说明状态依赖时间步。

### Q062. VTS-RL/TARC 如何影响安全过滤器设计？

**标准答案：** 安全过滤器必须检查整个动作持续区间内的状态，而不是只检查当前瞬间。持续时间越长，预测不确定性越大，约束应更保守或允许中断。

**评分要点：** 必须说明长 duration 要预测区间安全。

### Q063. [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning]] 的 persistent operator 对 batch RL 有什么意义？

**标准答案：** 它可以在固定 batch 数据上评估重复动作造成的频率变化，并有理论收缩性质帮助分析性能损失。控制频率不再只是在线调参，而可在离线数据中研究。

**评分要点：** 必须提到离线评估动作重复。

### Q064. Action persistence 在高动态接触中何时危险？

**标准答案：** 当接触状态快速变化、滑移即将发生或捕获窗口很短时，重复旧动作会错过反馈修正，导致过冲或掉落。Persistence 应由状态或相位自适应决定。

**评分要点：** 必须说明快速相位不能长保持。

### Q065. [[Reinforcement Learning for Control with Multiple Frequencies]] 为什么多频控制比统一高频更现实？

**标准答案：** 不同执行器、传感器和任务变量天然频率不同，统一高频增加计算和通信负担，也可能放大噪声。多频控制让关键维度高频、慢变量低频，更符合硬件系统。

**评分要点：** 必须说明不同变量不同带宽。

### Q066. 多频控制中周期性策略为什么会非平稳？

**标准答案：** 策略在不同时间相位更新不同动作维度，同一状态下若处于不同周期位置，可选动作集合不同，因此策略必须依赖周期相位，呈现周期性非平稳。

**评分要点：** 必须提到周期相位影响动作。

### Q067. [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation]] 为什么 DMP 适合作为基础轨迹？

**标准答案：** DMP 平滑、稳定、可由少量参数表示，并能泛化到不同起终点。它提供安全可解释的示范骨架，RL residual 只需修正接触差异。

**评分要点：** 必须说明 DMP 提供稳定先验。

### Q068. RL residual 为什么应低频？

**标准答案：** 低频 residual 避免破坏基础轨迹的平滑性和稳定性，也降低探索风险。高频残差可能引入抖动、冲击和执行器负担，尤其在接触任务中危险。

**评分要点：** 必须说明低频保护稳定。

### Q069. [[Exploration versus Exploitation in Reinforcement Learning - A Stochastic Control Approach]] 对 entropy temperature 有什么解释？

**标准答案：** Entropy temperature 控制随机控制成本与状态/任务成本的权衡。温度高鼓励更随机探索，温度低更接近确定性最优控制。它不是任意调参，而有随机控制解释。

**评分要点：** 必须说明探索成本权衡。

### Q070. 随机控制视角如何帮助理解真实机器人探索？

**标准答案：** 探索是受成本和噪声约束的控制问题，而不是越随机越好。真实机器人需要把探索能量限制在安全区域，并根据风险调整随机性。

**评分要点：** 必须说明安全约束下探索。

### Q071. [[Unified Policy Evaluation and Improvement - On Off-Policy Classification]] 为什么能解释 PPO 和 SAC 的关系？

**标准答案：** 二者都包含 policy evaluation 和 policy improvement，只是数据来源、正则参照和更新调度不同。PPO 近 on-policy、KL 到旧策略；SAC off-policy、entropy 正则和 replay 数据。

**评分要点：** 必须用 PE/PI 框架比较。

### Q072. Unified PE/PI 对真机算法选择有什么帮助？

**标准答案：** 它让研究者按数据来源和更新调度选择算法：真机数据昂贵时倾向 off-policy/离线复用；安全要求高时加强 KL/behavior regularization；在线阶段再小步改进。

**评分要点：** 必须连接算法选择与数据/安全。

### Q073. [[The Sampling Theorem With Constant Amplitude Variable Width Pulses]] 为什么和 action duration 有关联？

**标准答案：** 变量宽度脉冲说明信号不仅可由幅值编码，也可由持续时间编码。机器人动作同样可把持续时间作为控制自由度，连接 TARC、VTS-RL 和 action persistence。

**评分要点：** 必须说明持续时间携带信息。

### Q074. 变量宽度思想对低层执行器有什么限制？

**标准答案：** 执行器和通信系统有最小可执行脉宽、响应延迟和带宽限制。策略输出的持续时间必须落在硬件可实现范围内，否则理论时间动作无法部署。

**评分要点：** 必须提到硬件最小时间尺度。

### Q075. 安全后训练中为什么要区分 shielding 和 filtering？

**标准答案：** Shielding 常指基于形式化规则阻止危险转移，filtering 更一般地把策略动作投影或修改为安全动作。二者都在运行时保护系统，但机制和保守性不同。

**评分要点：** 必须说明阻止危险与投影修正。

### Q076. Safety filter 如何影响 policy gradient？

**标准答案：** 若环境执行的是 filtered action，而训练把原策略动作当作执行动作，credit assignment 会错。应记录过滤前后动作，必要时把 filter 纳入策略或训练模型中。

**评分要点：** 必须说明执行动作不一致。

### Q077. 为什么安全 RL 需要 fallback policy？

**标准答案：** 当安全优化不可行、模型不确定性过高或传感器失效时，系统需要保守恢复动作，如停止、退让、回 home 或释放。没有 fallback，安全层失败时没有最后防线。

**评分要点：** 必须提到不可行/故障时的恢复。

### Q078. 真机 RL 的 reward model 需要哪些安全防线？

**标准答案：** 需要真实验收校准、OOD 检测、人工审查、物理约束和 reward hacking 监控。学习奖励若被策略利用，会把真实系统推向危险高分区域。

**评分要点：** 必须说明 reward hacking 风险。

### Q079. 为什么安全指标要报告约束违反频率和幅度？

**标准答案：** 只报告是否最终成功无法体现安全。约束违反频率显示风险概率，幅度显示严重程度。温度、力矩、碰撞和接触力都需要这两个维度。

**评分要点：** 必须说明频率和严重度。

### Q080. 真实世界 RL 中为什么 wall-clock time 是重要指标？

**标准答案：** 真机训练受实验人员、硬件磨损和环境稳定性限制，样本数相同但耗时不同会影响可用性。Wall-clock time 反映系统吞吐、reset、推理和人类干预成本。

**评分要点：** 必须提到真实实验成本。

### Q081. 为什么 replay buffer 应记录硬件状态？

**标准答案：** 温度、电压、传感器校准、磨损和控制模式会影响转移动力学。若 replay 不记录这些上下文，同一状态动作回报会看似随机，影响 off-policy 学习和 OPE。

**评分要点：** 必须说明硬件状态是隐变量。

### Q082. 如何比较安全控制方法和普通 reward penalty？

**标准答案：** 固定任务 reward，比较 CBF/MPC/reachability/safety filter 与 penalty-only 在约束违反、成功率、恢复和保守性上的差异。若只调 penalty 权重，不能证明安全方法必要。

**评分要点：** 必须包含 penalty-only 对照。

### Q083. 为什么 Lyapunov/CBF 证书需要和数据驱动模型结合？

**标准答案：** 真实机器人动力学复杂，手工模型不准；纯数据驱动又缺少保证。数据驱动模型提供局部真实动力学，Lyapunov/CBF 提供可验证安全/稳定结构，二者互补。

**评分要点：** 必须说明模型精度和保证互补。

### Q084. 数据驱动安全证书最怕什么数据问题？

**标准答案：** 最怕安全边界附近数据不足、噪声未建模、分布非平稳和错误标签。证书在缺数据区域可能过度乐观或过度保守，必须用置信区间和主动采样补边界。

**评分要点：** 必须提到边界数据不足。

### Q085. 为什么“稳定”不等于“任务成功”？

**标准答案：** 稳定只说明系统收敛或有界，可能稳定在错误姿态、保守停住或放弃任务。任务成功还需要达到目标和满足操作过程。控制证书需和任务 reward/规划结合。

**评分要点：** 必须区分稳定性和性能。

### Q086. 为什么“任务成功”也不等于“安全”？

**标准答案：** 策略可能以高冲击、过压、发热或碰撞方式完成任务。安全要求过程约束和长期硬件健康，不是最终状态正确即可。

**评分要点：** 必须提到过程约束。

### Q087. 如何设计 real-world RL 的 ablation 表？

**标准答案：** 至少比较无演示、无安全层、无 reset、无人类干预、无阻抗控制、无离线阶段、不同控制频率，并报告成功率、安全违反、样本数、wall-clock 和失败模式。

**评分要点：** 必须包含系统组件消融和多指标。

### Q088. 为什么 safety layer 的保守性需要量化？

**标准答案：** 过保守会降低任务成功和探索效率，过松会危险。可量化被修改动作比例、修改幅度、拒绝率、约束余量和对成功率的影响，展示安全-性能 trade-off。

**评分要点：** 必须给出保守性指标。

### Q089. 真机 RL 中人类急停数据是否应训练？

**标准答案：** 应记录并可用于学习危险预测，但不能简单当作普通失败 reward。急停前状态是高价值安全边界数据，急停后轨迹可能不符合策略动力学，应特殊标注处理。

**评分要点：** 必须说明急停前数据有价值但需标注。

### Q090. 为什么 safety filter 需要考虑 actuator limits？

**标准答案：** 过滤后的动作若超出力矩、速度、温度或电流限制，理论安全也无法执行。安全集合必须是状态约束和输入/执行器可行性的交集。

**评分要点：** 必须提到输入可行性。

### Q091. 如何把温度约束纳入 real-world RL？

**标准答案：** 把温度作为观测和约束，学习或使用热模型预测未来温升，在 reward 或 safety filter 中限制持续高负载，并设计冷却 fallback。报告温度曲线而非只报告成功率。

**评分要点：** 必须包含预测和 fallback。

### Q092. 为什么真实世界 RL 需要版本化实验配置？

**标准答案：** 控制频率、增益、奖励、硬件状态、传感器校准和安全阈值都会影响结果。没有版本化，实验不可复现，也无法判断提升来自算法还是配置变化。

**评分要点：** 必须说明配置影响因果归因。

### Q093. 如何用 OPE 筛选 online RL 更新？

**标准答案：** 对候选策略先用离线数据估计保守价值区间和风险下界，只有超过基线并满足安全约束时才允许小规模真机测试。OPE 是放行 gate，而非最终证明。

**评分要点：** 必须说明 OPE 作为 gate。

### Q094. 为什么 online RL 更新步长要小？

**标准答案：** 大步更新可能让策略离开已知安全分布，使 OPE 和 safety model 失效。小步 KL/behavior 正则更新让性能逐步提升，同时保持可监控和可回滚。

**评分要点：** 必须提到分布漂移和回滚。

### Q095. Real-world RL 中如何处理 non-stationarity？

**标准答案：** 记录时间和硬件状态，使用滑动窗口或上下文条件策略，定期重新校准传感器，监控性能漂移，并保留旧数据防遗忘。非平稳性包括温度、磨损、环境和人类干预变化。

**评分要点：** 必须列出非平稳来源和处理。

### Q096. 为什么 safety benchmark 应包含恢复任务？

**标准答案：** 真正安全的系统不仅避免危险，还能在扰动或近失败状态下回到安全集。恢复任务测试策略是否具备可恢复性，而不是只在理想初始状态成功。

**评分要点：** 必须说明 recovery 是安全组成。

### Q097. 如何把 08 专题与 [[ControlTheory]] Foundation 联系起来？

**标准答案：** CBF、Lyapunov、Lipschitz、阻抗、时间自适应和 fallback 都是把学习策略约束在稳定、安全、可执行闭环中的控制理论工具。RL 提供改进，控制提供边界。

**评分要点：** 必须说明控制为学习提供边界。

### Q098. 如何把 08 专题与 [[Optimization]] Foundation 联系起来？

**标准答案：** Safety filter、CBF-QP、MPC、OPE 区间、阻抗参数选择和策略更新都可看作约束优化问题。关键是目标性能、安全约束和计算实时性之间的权衡。

**评分要点：** 必须说明约束优化视角。

### Q099. 面试官追问：真实世界 RL 论文最需要证明什么？

**标准答案：** 最需要证明方法在真实时间、真实硬件风险和真实分布偏移下，确实比强工程基线更高效、更安全或更鲁棒。必须提供样本效率、安全成本、消融和失败模式，而不是只给成功视频。

**评分要点：** 必须强调真实约束和强基线。

### Q100. 请总结 08 专题的核心主线。

**标准答案：** 主线是把 RL 从仿真算法变成可部署真机系统：用演示和软件栈启动，用人类/离线/在线数据改进，用阻抗和时间自适应提高可控性，用 CBF/Lyapunov/reachability/Lipschitz/OPE 提供安全边界。目标是会学习，同时不把硬件置于不可控风险中。

**评分要点：** 必须概括真机学习、控制结构和安全证书。
