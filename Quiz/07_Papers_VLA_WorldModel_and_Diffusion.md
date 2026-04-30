---
tags:
  - quiz
  - papers-recap
  - VLA
  - world-model
  - diffusion-policy
aliases:
  - VLA WorldModel Diffusion Paper Quiz
created: 2026-05-01
related:
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
---

# 07 Papers: VLA, World Model, and Diffusion

### Q001. [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]] 的 action chunk 为什么重要？

**标准答案：** Action chunk 让策略一次预测未来多步动作，能表达短时动作计划和双手协同，而不是每个控制步独立反应。它降低行为克隆中的逐步误差累积，并通过 temporal ensembling 平滑执行。代价是 chunk 过长会降低反馈频率。

**评分要点：** 必须提到短时计划、误差累积和反馈频率。

### Q002. ACT 中 CVAE latent 解决什么动作分布问题？

**标准答案：** 同一观测可能对应多个合理操作方式，CVAE latent 用隐变量表达这些动作模式，避免 MSE 行为克隆把多模态动作平均成不可执行动作。对双手或灵巧操作，动作风格和接触路径的多样性尤其重要。

**评分要点：** 必须说明多模态动作避免平均。

### Q003. [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] 为什么要用 planning guidance？

**标准答案：** Diffusion policy 能生成多模态动作，但可能缺少任务级长程约束。Planning guidance 在生成过程中注入目标、几何或可行性信号，让动作既落在演示流形内，又朝任务成功方向移动。它是生成式策略和规划约束的结合。

**评分要点：** 必须说出生成动作流形与任务引导的平衡。

### Q004. [[WMPO - World Model-based Policy Optimization for VLA]] 如何把 VLA 从模仿推向优化？

**标准答案：** WMPO 用世界模型预测动作后果，并在模型内对 VLA 动作进行策略优化或筛选，使策略不只复制数据，而是根据任务回报和动力学预测改进行为。风险是世界模型误差会被策略利用，因此需要不确定性和真实验证。

**评分要点：** 必须提到用 WM 后果预测优化 VLA。

### Q005. [[WoG - World Guidance for VLA Action Generation]] 与普通 diffusion guidance 有什么类比？

**标准答案：** 它类似 classifier guidance：生成动作时用世界模型或价值模型提供梯度/评分，推动采样朝更可能成功的动作移动。区别是 guidance 信号来自物理后果预测，而不是图像类别概率。

**评分要点：** 必须说明 world model score 引导动作生成。

### Q006. [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA]] 为什么强调 spatio-temporal chain-of-thought？

**标准答案：** 机器人任务不仅要理解物体语义，还要理解空间关系和时间顺序。Latent spatio-temporal CoT 试图在隐空间中分解“先接近、再接触、后操作”的过程，使 VLA 具备更强的长时程规划和动作解释能力。

**评分要点：** 必须连接空间关系与时间过程。

### Q007. [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation]] 的 post-training 目标是什么？

**标准答案：** 它让 VLA 在真实或高保真交互中接受人类纠正和强化信号，补足纯模仿在分布外状态、精细接触和失败恢复上的不足。人类不只是提供演示，还提供在线纠偏和安全监督。

**评分要点：** 必须提到在线人类纠正和 dexterous failure recovery。

### Q008. [[RECAP - A VLA that Learns from Experience]] 中 experience 的价值是什么？

**标准答案：** Experience 让 VLA 从自身成功和失败中更新策略或记忆，形成任务特定经验，而不是每次都依赖静态预训练知识。机器人经验包含物理后果和失败边界，是语言/视觉预训练数据无法完全提供的。

**评分要点：** 必须说明机器人交互经验不同于互联网知识。

### Q009. [[RLT - Precise Manipulation with Efficient Online RL Tokens]] 为什么 token 化能提高在线 RL 效率？

**标准答案：** Token 化把高维感知和动作上下文压缩成紧凑表征，在线 RL 只需在这些 token 上学习任务残差或决策头。它避免从像素和语言重新学习控制，降低真实数据需求。

**评分要点：** 必须提到在预训练表征上轻量更新。

### Q010. [[RL-100 - Performant Robotic Manipulation with Real-World RL]] 与 VLA 后训练有什么共同趋势？

**标准答案：** 二者都从静态模仿走向真实任务指标优化：先用演示或预训练提供安全初始策略，再用离线/在线 RL 改进成功率、鲁棒性和恢复能力。趋势是让机器人系统从“会模仿”变成“会练习”。

**评分要点：** 必须说出 imitation-to-RL post-training。

### Q011. [[COMET - Controllable Long-term Motion Generation with Extended Joint Targets]] 对机器人动作生成有什么启发？

**标准答案：** 长时程动作生成需要控制条件贯穿整个序列，而不是只给初始目标。Extended joint targets 提供持续的结构约束，使生成动作在长时间内保持可控。机器人 action chunk 或 trajectory diffusion 也需要类似长程条件。

**评分要点：** 必须提到长时程条件约束。

### Q012. [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking]] 的 physics-prefix 思想是什么？

**标准答案：** Physics-prefix 把物理可行性先验或短段物理状态嵌入生成模型前缀，约束后续动作生成不偏离动力学可执行区域。它提示机器人生成策略不能只看语义和外观，还要把物理状态作为生成上下文。

**评分要点：** 必须说明物理前缀约束生成。

### Q013. [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control]] 对高动态泛化有什么启发？

**标准答案：** 高动态控制的泛化来自多任务、多扰动和强物理约束训练，而不是单一场景调参。对灵巧手，高动态转笔同样需要覆盖速度、接触、执行器和初始状态变化，否则策略只会在窄分布成功。

**评分要点：** 必须连接高动态泛化和扰动覆盖。

### Q014. [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training]] 为什么把几何预训练和物理仿真结合？

**标准答案：** 几何决定接触候选、碰撞边界和可行操作区域，物理决定动作后果。GeoPT 类思想用大规模几何预训练提升模型对形状和空间关系的理解，再服务物理仿真或控制任务，提高数据效率和泛化。

**评分要点：** 必须说明几何是物理交互前提。

### Q015. [[空间智能作为机器人的结构化表征]] 为什么对 VLA 很关键？

**标准答案：** 机器人动作发生在三维空间，必须理解物体、手、约束和目标之间的结构关系。空间智能把语义目标落到坐标、拓扑、可达性和接触几何上，是从语言指令到可执行动作的桥梁。

**评分要点：** 必须把语义到空间可执行性连接起来。

### Q016. [[Weight-sparse transformers have interpretable circuits]] 对机器人 Transformer 有什么启发？

**标准答案：** 稀疏权重和可解释电路提示我们可以分析 Transformer 中哪些头或通路负责对象绑定、时间记忆、接触阶段或动作选择。机器人模型不能只看整体成功率，还应诊断内部表示是否学到物理和任务结构。

**评分要点：** 必须连接可解释电路与机器人表征诊断。

### Q017. [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] 与 diffusion policy 的关系是什么？

**标准答案：** MimicGen 可提供多样化、物理可行的演示数据，diffusion policy 则适合从这些多模态演示中学习动作分布。数据生成解决覆盖，扩散策略解决多模态建模。

**评分要点：** 必须区分数据覆盖和策略分布建模。

### Q018. [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation]] 为什么适合评测 VLA？

**标准答案：** VLA 需要在多任务、多对象、多初始状态和双手协调上泛化。RoboTwin 2.0 提供可规模化数据和 benchmark，可以测试模型是否真正学到结构化操作，而不是记忆单一场景。

**评分要点：** 必须提到 benchmark 泛化维度。

### Q019. [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] 与 teacher-student VLA 有什么联系？

**标准答案：** Privileged action 可看作 teacher 使用不可部署信息或专家控制生成更强监督，student/VLA 再蒸馏到真实可观测输入上。核心是训练期利用特权，部署期不依赖特权。

**评分要点：** 必须说明 privileged teacher 和 deployable student。

### Q020. [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] 为什么也属于生成式策略范畴？

**标准答案：** 它用生成式接触 grounding 约束动作或接触模式，使策略从条件分布中采样物理合理动作。与 diffusion policy 类似，它不是输出单一均值动作，而是利用生成模型表达多个可行接触方案。

**评分要点：** 必须提到生成多个接触方案。

### Q021. Diffusion policy 在真机部署中最大的风险是什么？

**标准答案：** 生成模型可能产生演示分布内但当前物理状态不可行的 action chunk，且 chunk 多步执行会延迟反馈修正。若没有安全过滤、低层控制和不确定性评估，错误 chunk 可能导致碰撞、滑移或硬件超限。

**评分要点：** 必须提到 action chunk 风险和 safety filter。

### Q022. World model guidance 为什么不能替代真实试验？

**标准答案：** 世界模型只是在已有数据分布上近似动力学，接触和执行器误差会在规划中被放大。Guidance 可筛选或修正动作，但最终仍需要真实 rollout 校准模型不确定性和发现模型漏洞。模型越被用于优化，越需要防 exploitation。

**评分要点：** 必须说明 model exploitation 和真实校准。

### Q023. VLA 动作 token 与连续控制之间的断层在哪里？

**标准答案：** VLA 常输出低频离散或半连续动作 token，而机器人底层需要高频、连续、受约束的关节命令。中间需要轨迹解码、阻抗控制、MPC 或 action chunk 平滑，把语义动作转成稳定可执行控制。

**评分要点：** 必须提到频率和连续性断层。

### Q024. 面试官追问：如何评价一个 VLA 是否真的理解接触？

**标准答案：** 不能只看语言任务成功率，应测试遮挡下接触建立、不同摩擦和材质、触觉 ablation、接触失败恢复、动作对触觉变化的响应、以及能否预测下一步接触拓扑。若模型只在视觉清晰场景成功，说明它主要学到语义和几何，未必理解接触物理。

**评分要点：** 必须给出接触专项评测。

### Q025. 如何把 07 专题的论文组织成一个研究路线？

**标准答案：** 先用 ACT/diffusion policy 学习多模态 action chunk；用 MimicGen/RoboTwin 扩展数据；用 VLA/空间智能提供语义和几何条件；再用 WMPO/WoG/world guidance 做模型内优化；最后用 RLT/DexHiL/RECAP 进行真机后训练和经验更新。主线是从模仿生成走向物理反馈优化。

**评分要点：** 必须形成从数据、策略、世界模型到真机后训练的闭环。

## Extended Questions

### Q026. [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware]] 中 temporal ensembling 为什么不只是平滑技巧？

**标准答案：** 它利用相邻时刻 action chunk 对同一未来动作的重复预测，把多个条件下的估计融合起来，降低单次预测噪声和 covariate shift。它本质上是用时间冗余提升闭环稳定性，而不只是后处理滤波。

**评分要点：** 必须说明重叠 chunk 的冗余估计。

### Q027. ACT 的低成本硬件背景对方法设计有什么影响？

**标准答案：** 低成本硬件通常控制精度、刚度和传感较弱，因此方法不能依赖高精度力控或昂贵传感器。Action chunk 和模仿学习降低在线探索风险，用相对简单的动作接口获得稳定双手操作。

**评分要点：** 必须连接硬件限制与 action chunk/IL。

### Q028. ACT 在灵巧手转笔上可能遇到什么瓶颈？

**标准答案：** 转笔需要高频接触反馈和相位纠错，长 action chunk 可能在滑移发生时无法及时中断；CVAE latent 可表达模式，但缺少力/触觉和动态反馈时难以保持接触链。需要安全可中断 chunk 和低层控制。

**评分要点：** 必须指出 chunk 反馈延迟。

### Q029. [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] 中 planning guidance 的权重过大会怎样？

**标准答案：** Guidance 过大会把采样推离演示动作流形，产生规划上看似可行但低层不可执行或不自然的动作；过小则 diffusion 只模仿数据，缺少任务推进。权重是任务约束与行为先验的平衡。

**评分要点：** 必须说明流形偏离与引导不足 trade-off。

### Q030. GLIDE 类方法为什么适合双手而不只是单手？

**标准答案：** 双手任务有长程几何约束和协同顺序，单纯行为克隆容易丢失高层计划。Planning guidance 可约束两手相对位置、物体目标和任务阶段，同时 diffusion 保留多种协同轨迹。

**评分要点：** 必须提到双手协同和长程约束。

### Q031. [[WMPO - World Model-based Policy Optimization for VLA]] 中 world model 应预测哪些机器人变量？

**标准答案：** 除图像或状态，还应预测任务成功、物体姿态、接触/碰撞、动作可执行性、失败风险和不确定性。VLA 优化需要控制相关后果，而不是只预测下一帧外观。

**评分要点：** 必须包含控制相关变量。

### Q032. WMPO 为什么容易被 reviewer 追问 model exploitation？

**标准答案：** 一旦用世界模型优化策略，策略会寻找模型高估的动作。如果缺少 uncertainty、真实验证和 OOD 约束，提升可能只是利用模型漏洞。必须报告真实 rollout 和模型误差诊断。

**评分要点：** 必须说明优化会放大模型错误。

### Q033. WMPO 与普通 offline RL 的共同问题是什么？

**标准答案：** 二者都在有限数据支持上改进策略，容易把动作推到数据分布外。Offline RL 依赖 Q/behavior regularization，WMPO 依赖 world model uncertainty 和 action prior，本质都要控制 OOD policy improvement。

**评分要点：** 必须提到 OOD 改进风险。

### Q034. [[WoG - World Guidance for VLA Action Generation]] 中 guidance 信号可以来自哪些模型？

**标准答案：** 可以来自 world model rollout score、value function、success classifier、safety predictor、contact feasibility model 或 uncertainty penalty。关键是 guidance 要反映真实物理后果，而不是只反映语义匹配。

**评分要点：** 必须列出至少三类 guidance source。

### Q035. WoG 的 guidance 为什么应支持负向约束？

**标准答案：** 动作生成不仅要朝成功移动，还要远离碰撞、过压、滑移和硬件超限。负向 guidance 或 safety score 能在采样时排斥危险动作，避免只优化任务成功概率。

**评分要点：** 必须提到安全/不可行动作排斥。

### Q036. [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA]] 的 latent CoT 为什么比显式文字 CoT 更适合控制？

**标准答案：** 控制需要连续空间、时间和接触状态，显式文字难表达高频细节且可能产生语言幻觉。Latent CoT 可在内部表示相位、目标和空间关系，供动作生成使用，同时避免把低层控制离散成不精确文字。

**评分要点：** 必须说明 latent 更适合连续控制变量。

### Q037. LaST0 类方法如何验证 CoT 真有用？

**标准答案：** 需要比较无 CoT、显式 CoT、latent CoT，测试长时程任务、空间重排、遮挡和失败恢复，并 probing latent 是否编码阶段和空间关系。不能只展示语言解释看起来合理。

**评分要点：** 必须包含消融和 latent probing。

### Q038. [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation]] 中人类反馈最适合介入哪些时刻？

**标准答案：** 最适合介入 near-failure、接触切换、策略犹豫或安全边界时刻。全程人类控制成本高，完全失败后纠正太晚。关键是采集对策略最有信息量的纠错数据。

**评分要点：** 必须说明 near-failure 介入价值。

### Q039. DexHiL 如何避免模型只学会等待人类救援？

**标准答案：** 训练时应记录人类介入前的状态和纠正动作，并逐步减少介入，奖励自主恢复。还需区分策略动作与人类动作，避免策略依赖人类作为隐式控制器。

**评分要点：** 必须提到依赖人类干预的风险。

### Q040. [[RECAP - A VLA that Learns from Experience]] 中 experience memory 应存什么？

**标准答案：** 应存任务上下文、观测、动作、结果、失败原因、环境属性、纠正信息和可复用策略片段。只存成功摘要不够，失败边界和恢复经验同样关键。

**评分要点：** 必须包含失败和纠正信息。

### Q041. RECAP 类经验学习如何避免灾难性遗忘？

**标准答案：** 需要 replay 旧任务经验、参数高效适配、任务条件记忆检索和正则化，防止新任务微调破坏旧技能。机器人经验是稀缺且多任务的，遗忘会降低长期可用性。

**评分要点：** 必须提到 replay 或参数高效适配。

### Q042. [[RLT - Precise Manipulation with Efficient Online RL Tokens]] 中 token 应保留哪些信息？

**标准答案：** Token 应保留任务目标、物体相对位姿、接触状态、动作历史、失败风险和低层可执行性。若 token 只编码视觉语义，在线 RL 无法优化精密接触。

**评分要点：** 必须提到控制相关 token。

### Q043. RLT 为什么可能比从像素在线 RL 更安全？

**标准答案：** 它在预训练表征上学习小型控制头或 residual，减少真实样本需求和随机探索。大部分感知能力已固定，在线更新集中在任务指标，使策略改进更快且可约束。

**评分要点：** 必须说明降低真实探索成本。

### Q044. RLT token 化的风险是什么？

**标准答案：** 如果 token 压缩掉滑移、温度、执行器饱和等关键变量，在线 RL 再强也无法恢复信息。Token 是瓶颈，必须通过 probing 和任务指标验证充分性。

**评分要点：** 必须说明信息瓶颈风险。

### Q045. [[RL-100 - Performant Robotic Manipulation with Real-World RL]] 对 VLA 的最大启发是什么？

**标准答案：** 真实机器人性能需要在线或离线 RL 对任务指标进行持续优化，预训练/模仿只是起点。VLA 若停留在静态 imitation，很难处理分布外失败和精密控制。

**评分要点：** 必须说明从模仿到练习。

### Q046. RL-100 类管线如何与 diffusion policy 结合？

**标准答案：** 可先用 diffusion policy 学演示动作分布，再用 RL 对生成动作做 rerank、guidance 或 residual correction，最后蒸馏成快速策略。这样结合多模态模仿和真实指标优化。

**评分要点：** 必须提到 diffusion prior + RL improvement。

### Q047. [[COMET - Controllable Long-term Motion Generation with Extended Joint Targets]] 中 extended target 对机器人 trajectory diffusion 有何启发？

**标准答案：** 长轨迹生成应在多个时间点持续给目标条件，避免只靠起点和终点导致中间动作漂移。机器人可用 waypoint、接触阶段、物体姿态序列或关节 target 序列作为 extended conditions。

**评分要点：** 必须说明中间约束防漂移。

### Q048. COMET 类长时程生成如何避免物理不连续？

**标准答案：** 需要速度/加速度连续约束、接触模式一致性、低层控制可执行性和物理仿真验证。只生成位置序列可能出现跳变或不可实现动作。

**评分要点：** 必须提到连续性和仿真验证。

### Q049. [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking]] 的 physics-prefix 对灵巧操作有什么类比？

**标准答案：** 灵巧操作可把当前接触状态、物体角动量、执行器温度和短期历史作为 physics prefix，约束后续动作生成不脱离真实动力学相位。它是物理状态对生成模型的前置条件。

**评分要点：** 必须给出灵巧操作 physics prefix 例子。

### Q050. Physics-prefix 过短或过长分别有什么问题？

**标准答案：** 过短可能不足以推断速度、相位和隐变量；过长增加计算并可能引入过时信息。长度应覆盖关键动力学记忆，如触觉迟滞、动作延迟和物体动量时间尺度。

**评分要点：** 必须说明历史窗口与动力学记忆匹配。

### Q051. [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control]] 对高动态灵巧手有什么提醒？

**标准答案：** 高动态泛化需要任务、扰动、速度和接触条件的大覆盖，并配合强物理约束和鲁棒低层控制。不能只在单一速度、单一物体上调出漂亮 demo。

**评分要点：** 必须说明高动态需要分布覆盖。

### Q052. OmniXtreme 类高动态控制为什么强调 evaluation diversity？

**标准答案：** 高动态策略最容易在训练分布内成功、稍微换速度或扰动就崩溃。多样化评估能暴露策略是否学到物理机制，还是记住固定相位和初始条件。

**评分要点：** 必须提到固定相位过拟合。

### Q053. [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training]] 中几何预训练如何服务接触？

**标准答案：** 几何预训练可识别表面、边缘、曲率、可接触区域和遮挡结构，这些决定碰撞和接触候选。物理仿真再在这些几何结构上预测动作后果。

**评分要点：** 必须连接几何特征和接触候选。

### Q054. GeoPT 类方法为什么不能只看 geometry loss？

**标准答案：** 几何重建好不代表操作可行，模型还需预测接触稳定、碰撞风险和控制结果。应通过 downstream manipulation、planning success 和 sim-to-real 表现评价。

**评分要点：** 必须说明几何指标不等于控制性能。

### Q055. [[空间智能作为机器人的结构化表征]] 如何补足 VLA 的语言短板？

**标准答案：** 语言可指定目标但不天然表达精确坐标、可达性、接触拓扑和约束。空间智能把“把物体转到那里”转成手、物、障碍和目标之间的结构关系，使动作生成有几何基础。

**评分要点：** 必须说明语言到空间结构的落地。

### Q056. 空间智能在灵巧手任务中应包含哪些结构？

**标准答案：** 应包含手指-物体接触图、物体姿态、指尖可达区域、摩擦/支撑关系、目标相位和环境约束。只包含物体 3D shape 不足以指导多指接触。

**评分要点：** 必须包含接触图和可达性。

### Q057. [[Weight-sparse transformers have interpretable circuits]] 对 VLA safety 有什么启发？

**标准答案：** 如果能识别负责动作选择、对象绑定、接触阶段和安全判断的电路，就可以监控或修剪异常通路，提高可解释性。机器人安全需要知道模型为何动作，而不是只看输出。

**评分要点：** 必须连接 circuit interpretability 与安全诊断。

### Q058. 稀疏 Transformer 是否一定适合机器人？

**标准答案：** 不一定。稀疏性提高可解释和效率，但过强可能削弱多模态融合和连续控制表达。机器人模型要在稀疏可解释、实时推理和精细动作能力之间权衡。

**评分要点：** 必须说明稀疏性 trade-off。

### Q059. [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] 为 VLA 提供什么类型的数据？

**标准答案：** 它提供场景变体、任务轨迹和子技能组合数据，可用于训练 VLA 的动作生成和任务泛化。对 VLA，数据不只是图像语言对，而是包含动作和物理后果的序列。

**评分要点：** 必须强调动作后果序列。

### Q060. MimicGen 数据用于 diffusion policy 时要注意什么？

**标准答案：** 生成轨迹必须物理可行且分布多样，不能大量复制同一模板。Diffusion 会忠实学习数据分布，若数据有伪接触或偏差，生成策略会放大这些模式。

**评分要点：** 必须说明数据质量决定生成质量。

### Q061. [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation]] 如何评估 bimanual VLA 的 compositionality？

**标准答案：** 可测试未见物体组合、左右手角色互换、子任务重排、工具/物体关系变化和语言目标组合。若模型只能复现训练任务，说明组合泛化不足。

**评分要点：** 必须列出组合泛化测试。

### Q062. RoboTwin 2.0 类 benchmark 为什么需要 process metrics？

**标准答案：** 最终成功率不能解释双手协同是否合理。应报告接触建立时间、双手同步误差、物体轨迹偏差、碰撞、动作平滑和恢复次数，以定位模型失败阶段。

**评分要点：** 必须包含过程指标。

### Q063. [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] 中 privileged action 对 VLA 有什么类似作用？

**标准答案：** 它像训练期专家 decoder，用不可部署信息帮助生成更好动作，再蒸馏给真实观测 VLA。VLA 可利用特权仿真状态学习长程结构，但部署时必须只依赖真实传感。

**评分要点：** 必须说明训练特权、部署普通。

### Q064. Privileged action 与 world model guidance 如何结合？

**标准答案：** Privileged teacher 可生成高质量候选动作，world model guidance 可评估或优化候选后果，再蒸馏到 VLA。二者分别提供专家先验和物理后果筛选。

**评分要点：** 必须说明 teacher prior + model evaluation。

### Q065. [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding]] 与 WoG 的共同点是什么？

**标准答案：** 都是在动作生成过程中加入物理相关 guidance：前者来自接触先验，后者来自世界模型后果。目标都是让生成动作不只像数据，还满足任务物理约束。

**评分要点：** 必须指出生成过程中的物理引导。

### Q066. Diffusion policy 的 multimodality 在接触任务中具体体现在哪里？

**标准答案：** 同一目标可通过不同接触点、不同换指顺序、不同绕行路径或不同速度完成。Diffusion 可表示这些动作模式，而 MSE BC 往往把它们平均成不可行动作。

**评分要点：** 必须给出多接触模式例子。

### Q067. Diffusion action chunk 如何设置 horizon？

**标准答案：** Horizon 应覆盖一个局部技能或接触相位，但不能长到无法响应突发滑移。应根据控制频率、任务阶段持续时间和安全中断机制调节，并用 ablation 验证。

**评分要点：** 必须说明覆盖相位与反馈延迟平衡。

### Q068. Diffusion policy 的 score model 在 OOD 状态下会怎样？

**标准答案：** OOD 状态下去噪模型可能生成看似合理但与当前物理不匹配的动作，或退化到训练数据中常见模式。需要状态置信度、OOD 检测和 fallback，尤其在真机失败边界。

**评分要点：** 必须提到 OOD 状态下生成不可信。

### Q069. 为什么 VLA 输出动作需要 verifier？

**标准答案：** VLA 可能因语言/视觉误解或物理缺失生成不可达、碰撞或过载动作。Verifier 用几何、动力学、接触和安全约束检查动作，必要时拒绝或重采样。

**评分要点：** 必须说明动作验证层。

### Q070. VLA 后训练中 RL reward 应如何设计？

**标准答案：** 应包含任务成功、过程进度、安全约束、动作平滑、接触质量和恢复能力，并避免让模型通过危险捷径提高分数。真实 RL reward 需要与低层传感和任务验收绑定。

**评分要点：** 必须包含任务和安全两类指标。

### Q071. 为什么 VLA 的 language grounding 需要 action grounding？

**标准答案：** 语言理解任务语义只是第一步，机器人必须把语义映射到可执行动作和接触序列。没有 action grounding，模型可能正确描述任务却无法完成。动作后果是 grounding 的最终检验。

**评分要点：** 必须说明语言到动作后果。

### Q072. World model guidance 和 MPC 的关系是什么？

**标准答案：** 二者都用模型预测候选动作后果并选择更优动作。区别是 world guidance 常嵌入生成式策略采样，MPC 显式在线优化控制序列。二者可结合：VLA/diffusion 产生候选，MPC/world model 筛选。

**评分要点：** 必须比较生成式 guidance 与显式 MPC。

### Q073. 为什么 world model 要输出 uncertainty 而不是只输出 mean？

**标准答案：** Mean 预测可能在多模态未来中平均出不可实现状态，也无法表达数据不足风险。Uncertainty 可用于 LCB、exploration、safety filter 和真实数据采集决策。

**评分要点：** 必须说明多模态和数据不足。

### Q074. VLA 在线 RL 为什么适合 parameter-efficient tuning？

**标准答案：** 大模型全量更新成本高、容易遗忘且真实数据少。Adapter、LoRA、head tuning 或 residual policy 可在保持预训练知识的同时适配任务，降低风险和计算。

**评分要点：** 必须说明小数据和遗忘风险。

### Q075. 为什么 VLA 后训练需要 replay buffer 质量控制？

**标准答案：** 真实 replay 混有失败、干预、传感异常和非平稳硬件状态。若不标注质量和上下文，训练会把错误或过期数据当正常经验。需要记录 intervention、failure mode、timestamp 和 hardware state。

**评分要点：** 必须说明真实 replay 非平稳。

### Q076. 如何验证 VLA 是否利用了触觉而不是只利用视觉？

**标准答案：** 做触觉遮蔽、触觉延迟、触觉随机置换、视觉遮挡和材质变化测试，并检查动作是否随触觉滑移/压力变化调整。若触觉变化不影响动作，说明模态未被有效使用。

**评分要点：** 必须包含模态扰动和动作响应。

### Q077. VLA 的 action vocabulary 为什么难覆盖灵巧手？

**标准答案：** 灵巧手动作高维连续、频率高且受接触相位约束，简单离散词表难表示毫米级指尖调整和力控参数。需要层级动作、连续 decoder 或低层控制器承接。

**评分要点：** 必须提到高维连续和频率。

### Q078. 为什么 spatial CoT 应包含手物相对坐标而非全局坐标？

**标准答案：** 操作动作主要由手指、物体和目标之间的相对关系决定，全局坐标变化不应改变技能本质。相对坐标更利于泛化和几何等变，也更贴近低层控制。

**评分要点：** 必须说明相对坐标泛化。

### Q079. VLA world model 如何处理 partial observability？

**标准答案：** 需要用历史观测、动作、触觉和本体状态构建 belief latent，预测隐藏物体状态、接触和执行器隐变量。单帧视觉 world model 无法可靠预测遮挡下接触后果。

**评分要点：** 必须提到 belief latent 和历史。

### Q080. 为什么 VLA 论文中的 simulation benchmark 仍需真机 sanity check？

**标准答案：** 仿真 benchmark 可规模化但可能缺少真实接触、传感和执行器误差。真机 sanity check 能验证动作接口、延迟和安全是否可部署，防止模型只适合仿真 leaderboard。

**评分要点：** 必须说明仿真 leaderboard 不等于部署。

### Q081. 如何设计一个 VLA 接触任务的最小真实评测？

**标准答案：** 选一个有遮挡和接触反馈需求的任务，比较 VLA alone、VLA+low-level controller、VLA+触觉、VLA+world guidance，报告成功率、接触失败、动作延迟和人工干预。评测应含未见物体和扰动。

**评分要点：** 必须包含对照和接触指标。

### Q082. 为什么生成式策略需要安全重采样？

**标准答案：** 生成模型会采样多个候选，其中部分可能碰撞、过压或越界。安全重采样用 verifier 过滤危险候选，再从可行集合中选高分动作，比单次生成直接执行更可靠。

**评分要点：** 必须说明候选过滤。

### Q083. 为什么 “more data” 对 VLA 不一定解决灵巧操作？

**标准答案：** 若数据缺少高频触觉、执行器状态、失败恢复和接触边界，再多视觉语言演示也难学到灵巧控制。数据规模必须覆盖物理因果变量，而不是只增加场景外观。

**评分要点：** 必须说明数据内容比规模更关键。

### Q084. Diffusion 与 autoregressive action model 在机器人中的差异是什么？

**标准答案：** Autoregressive 按时间或维度顺序生成，适合显式条件依赖但推理可慢；diffusion 通过迭代去噪生成整体 action chunk，表达多模态强但采样步数影响实时性。二者都需安全验证。

**评分要点：** 必须比较顺序生成和迭代去噪。

### Q085. 为什么 VLA 需要 low-level skill library？

**标准答案：** 大模型擅长语义和任务分解，但低层接触控制需要高频稳定技能。Skill library 提供经过验证的抓、推、旋、退让、恢复等动作，让 VLA 选择和参数化，而不是直接输出电机命令。

**评分要点：** 必须说明高层选择、低层执行。

### Q086. Skill library 的缺点是什么？

**标准答案：** 技能集合限制模型探索新策略，技能边界和参数化设计会影响性能，技能间切换也可能不连续。需要允许技能组合、残差学习和新技能发现。

**评分要点：** 必须提到表达受限和切换问题。

### Q087. VLA 的 failure memory 应如何用于下一次尝试？

**标准答案：** 失败记忆应检索相似场景和失败原因，调整接触点、速度、力阈值或子目标，并避免重复同一动作。它应影响规划和安全阈值，而不只是生成文字总结。

**评分要点：** 必须说明失败记忆改变动作。

### Q088. 为什么世界模型后训练需要 holdout real trajectories？

**标准答案：** 用同一真实轨迹训练和评估会高估模型质量。Holdout 轨迹可检验多步预测、接触事件和 OOD 校准，防止 world guidance 基于过拟合模型。

**评分要点：** 必须提到过拟合和多步验证。

### Q089. VLA/diffusion paper 如何报告 latency 才有意义？

**标准答案：** 应报告感知编码、模型推理、去噪/解码、安全验证、通信和低层控制总延迟，并说明控制频率和 chunk 可中断性。只报告 GPU forward 时间不够。

**评分要点：** 必须包含端到端 latency。

### Q090. 为什么 fine-grained manipulation 不能只靠 coarse language instruction？

**标准答案：** 语言指令通常缺少毫米级姿态、接触力、速度和相位细节。精细操作需要视觉/触觉/本体闭环和低层控制，将粗目标转化为连续约束。

**评分要点：** 必须说明语言粒度不足。

### Q091. VLA 研究中“emergent skill”应如何被证明？

**标准答案：** 需要展示模型在未训练组合、未见扰动或新物体上表现出可解释的新行为，并通过消融排除数据记忆和手工脚本。最好给出失败和成功边界分析。

**评分要点：** 必须说明排除记忆/脚本。

### Q092. 为什么 action grounding 需要记录低层控制器？

**标准答案：** 同一 action token 在不同低层控制器下物理效果不同。没有记录 PD/阻抗/频率/限幅，动作数据无法复用，VLA 学到的 token 语义也不稳定。

**评分要点：** 必须说明 token 含义依赖低层控制。

### Q093. World model guidance 如何和 human-in-the-loop 互补？

**标准答案：** World model 可自动筛选大量候选，人类在模型不确定或高风险时提供纠正和标签。模型提升效率，人类提供安全和真实边界监督。二者共同减少盲目真机探索。

**评分要点：** 必须说明自动筛选和人类边界监督。

### Q094. 为什么 VLA 不能直接把互联网视频当成机器人轨迹？

**标准答案：** 视频缺少机器人动作、力、控制频率、相机标定和可执行约束，人手与机器人具身差异巨大。互联网视频可提供语义和粗时序先验，但需要 retargeting 和物理 grounding。

**评分要点：** 必须提到动作/力缺失和具身差异。

### Q095. 如何评价 VLA 是否学到 causal affordance？

**标准答案：** 测试模型能否根据动作预测物体状态变化，是否在干预物体位置、材质或约束后改变策略，是否能区分可推/不可推、可抓/不可抓区域。Affordance 必须是 action-conditioned。

**评分要点：** 必须说明动作条件下的可供性。

### Q096. 为什么 VLA 的 safety filter 不能只基于视觉？

**标准答案：** 视觉看不到局部接触力、过压、温度和滑移，很多危险发生在遮挡接触界面。Safety filter 需要融合触觉、本体、执行器状态和几何约束。

**评分要点：** 必须提到视觉不可见危险。

### Q097. 如何把 07 专题和 [[ReinforcementLearning]] Foundation 连接起来？

**标准答案：** VLA/diffusion 提供强 action prior，world model 提供后果预测，RL 提供任务指标优化和在线改进。三者对应 policy prior、model-based evaluation 和 policy improvement。

**评分要点：** 必须连接 prior、model、improvement。

### Q098. 如何把 07 专题和 [[EmbodiedAI]] Foundation 连接起来？

**标准答案：** 这些论文体现 Embodied AI 从视觉语言理解走向物理行动：需要空间智能、低层控制、真实经验、动作 grounding 和安全验证。Embodiment 决定模型输出是否真的可执行。

**评分要点：** 必须强调 embodied action grounding。

### Q099. 面试官追问：VLA 灵巧操作未来最关键的瓶颈是什么？

**标准答案：** 关键瓶颈是高层语义模型与高频接触控制之间的接口：动作表示、实时性、触觉融合、世界模型校准和安全过滤。解决它需要分层架构，而不是单纯扩大模型。

**评分要点：** 必须指出接口瓶颈。

### Q100. 请总结 07 专题的核心主线。

**标准答案：** 主线是用 ACT/diffusion 表达多模态动作，用 VLA/空间智能提供任务和几何条件，用 world model/guidance/RL 后训练把生成动作推向真实成功，再用人类经验和安全验证闭环。核心转变是从模仿生成到物理反馈优化。

**评分要点：** 必须概括生成、世界模型、后训练和安全闭环。