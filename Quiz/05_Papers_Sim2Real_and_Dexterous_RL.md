---
tags:
  - quiz
  - papers-recap
  - sim-to-real
  - dexterous-rl
aliases:
  - Sim2Real Dexterous RL Paper Quiz
created: 2026-05-01
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# 05 Papers: Sim-to-Real and Dexterous RL

### Q001. [[A Survey of Sim-to-Real Methods in RL]] 中 Sim-to-Real gap 的主要来源有哪些？

**标准答案：** 主要来源包括动力学参数误差、接触与摩擦模型误差、执行器延迟和饱和、传感噪声和遮挡、任务初始化分布差异以及真实环境中未建模的柔性或温度效应。灵巧操作中最危险的是接触和执行器 gap，因为它们直接改变策略动作到物体 wrench 的因果链。

**评分要点：** 必须至少覆盖动力学、接触、执行器、感知四类 gap。

### Q002. [[Reinforcement Learning in Robotic Systems - A Review on Sim-to-Real Transfer]] 为什么强调 DR、System ID 和 Adaptation 的互补？

**标准答案：** DR 扩大训练分布，使策略不依赖单一仿真参数；System ID 缩小仿真到真实的参数误差；Adaptation 在部署时根据历史观测估计当前隐变量。三者分别对应训练前覆盖、部署前校准和部署中在线适应，缺一都会留下不同类型的 reality gap。

**评分要点：** 必须说清三者的时间尺度和分工。

### Q003. [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] 的核心闭环是什么？

**标准答案：** RialTo 先从真实环境重建或校准仿真，再在仿真中训练策略，最后把策略部署回真实世界，并继续用真实失败修正仿真。它不是单向 sim-to-real，而是 real-to-sim-to-real 的迭代闭环，关键在于让仿真任务实例和真实场景足够一致。

**评分要点：** 必须提到真实数据校准仿真和迭代闭环。

### Q004. [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] 为什么使用在线 correction？

**标准答案：** 离线仿真策略进入真机后会遇到局部分布偏移，完全重训成本高且危险。TRANSIC 用在线 correction 学习从当前真实状态到修正动作的映射，把少量真实交互转化为策略补偿信号。它的价值在于快速修正仿真没覆盖的局部误差。

**评分要点：** 必须说明 correction 是针对部署分布偏移的局部补偿。

### Q005. [[Grounded Action Transformation]] 的 sim-to-real 思想是什么？

**标准答案：** GAT 不直接改变策略，而是学习一个动作变换器，把策略在仿真中输出的动作转换成在真实动力学下效果更接近仿真的动作。它把 gap 放在 action interface 层处理，适合底层执行器或环境响应有系统性偏差的场景。

**评分要点：** 必须说明 action transformation 连接 sim action 和 real effect。

### Q006. [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] 为什么强调 simulated human demonstration？

**标准答案：** 灵巧任务真机演示采集昂贵且难以覆盖失败恢复。CyberDemo 用仿真人类演示扩展数据多样性，再通过真实部署或校准缓解 gap。其关键不是简单增加数据，而是用人类先验提供合理的接触时序和手指协同模式。

**评分要点：** 必须提到演示提供接触时序和协同先验。

### Q007. [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] 的 sensing reduction 解决什么问题？

**标准答案：** 它先在仿真中利用丰富状态训练，再逐步减少到真实可用传感，使策略从 privileged observation 过渡到部署 observation。这样既利用仿真上帝视角加速学习，又避免最终策略依赖真机不可得信号。

**评分要点：** 必须说出 privileged-to-real observation curriculum。

### Q008. [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] 对触觉研究有什么警示？

**标准答案：** 它提醒我们触觉并非万能。如果任务难度分布太差，策略根本进不到有效接触状态，触觉不会自动带来学习信号。课程改变探索路径和状态分布，可能比增加模态更直接。触觉提升可观测性，课程改善可学习性。

**评分要点：** 必须区分 observability 和 exploration distribution。

### Q009. [[Curriculum Learning]] 在灵巧操作中为什么不能只按成功率推进？

**标准答案：** 成功率是粗指标，可能掩盖任务相位失败、接触风险和 reward hacking。课程推进还应看首次成功时间、失败类型、接触稳定、动作安全和是否进入近端失败区间。否则容易过早升级导致崩溃，或在太容易任务上浪费样本。

**评分要点：** 必须提出成功率之外的推进信号。

### Q010. [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] 如何用演示解决探索瓶颈？

**标准答案：** DemoStart 从演示轨迹的中间状态初始化，让策略先学习完成后半段，再逐步向更早状态扩展。这能绕过稀疏奖励中最困难的早期探索，并把演示转化为课程，而不只是行为克隆目标。

**评分要点：** 必须说明从演示中间状态启动的课程作用。

### Q011. [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] 的 joint-wise dynamics model 有什么优势？

**标准答案：** 它把复杂手部执行器和关节响应分解到关节级别建模，学习仿真和真实之间的局部动力学差异。相比整体黑箱模型，joint-wise 结构更贴近硬件误差来源，也更容易迁移到不同动作和姿态。

**评分要点：** 必须提到关节级执行器/动力学 gap。

### Q012. [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] 为什么适合解释快速在线适应？

**标准答案：** HORA 用历史观测推断隐含动力学参数或扰动，让策略在部署时快速适应物体质量、摩擦、执行器误差等变化。其关键是把 adaptation latent 作为策略条件，而不是每次重新训练策略。

**评分要点：** 必须提到历史观测到 latent 的快速推断。

### Q013. [[Lessons from Learning to Spin Pens]] 对转笔任务最重要的经验是什么？

**标准答案：** 转笔成功依赖相位化动作、接触切换、惯性利用和执行器带宽，而不是单纯最终姿态奖励。训练中要关注初始化、奖励因果链、动作平滑和真实硬件可执行性。看似小的控制频率或摩擦差异都可能破坏整条旋转链。

**评分要点：** 必须强调相位、惯性和接触切换。

### Q014. [[Dexterous Robotic Manipulation using Deep RL and Knowledge Transfer]] 中 knowledge transfer 的意义是什么？

**标准答案：** 灵巧手任务从零探索代价极高，知识迁移可把简单任务、仿真策略、专家演示或已有技能转移到新任务，减少搜索空间。迁移的关键是保留可复用的接触和手指协同结构，而不是机械复制动作。

**评分要点：** 必须说明迁移的是技能结构和探索先验。

### Q015. [[Deep Dynamics Models for Learning Dexterous Manipulation]] 为什么早期就强调 dynamics model？

**标准答案：** 灵巧操作的动作后果由接触、摩擦和物体惯性决定，纯 model-free 学习样本效率低。动力学模型可以预测动作结果、辅助规划、生成训练数据或提供误差诊断。但模型必须处理接触不连续和多模态结果，否则会误导策略。

**评分要点：** 必须同时说明样本效率优势和接触建模风险。

### Q016. [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning]] 中 extrinsic dexterity 指什么？

**标准答案：** Extrinsic dexterity 指机器人利用环境、物体间碰撞、支撑面、重力和动态交互完成操作，而不是只依靠手自身的精确抓取。它要求策略理解外部动力学结构，把环境从障碍转化为可利用工具。

**评分要点：** 必须讲出利用环境动力学而非单手内控制。

### Q017. [[Hindsight Experience Replay]] 为什么对多目标操作有价值？

**标准答案：** HER 把失败轨迹中实际达到的状态重标为目标，使稀疏失败经验变成成功经验。对手内旋转或重定位，虽然没有达到原目标角度，但可能达到某个中间角度，重标后仍能学习状态转移和目标条件策略。

**评分要点：** 必须提到实际达到状态作为新目标。

### Q018. [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] 相比随机演示有什么优势？

**标准答案：** 它用物理约束和轨迹优化生成满足接触、摩擦和动力学可行性的演示，避免随机数据包含大量不可执行或无信息片段。对接触任务，物理一致演示比大而杂的数据更能提供有效模仿信号。

**评分要点：** 必须说明数据生成受物理可行性约束。

### Q019. [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] 的 scalable 体现在哪里？

**标准答案：** MimicGen 将少量人类演示拆解、重组和泛化到不同场景实例，自动生成大量任务轨迹。它利用演示中的关键子技能和接触片段，而不是要求每个场景都重新遥操作。

**评分要点：** 必须提到演示片段复用和场景泛化。

### Q020. [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation]] 对双手灵巧操作有什么启发？

**标准答案：** 它强调数据生成、任务多样性和双臂/双手协调 benchmark。对灵巧操作，单任务成功不足以证明泛化，必须测试物体、初始姿态、协同方式和扰动多样性。大规模数据生成还需要物理一致和可部署动作接口。

**评分要点：** 必须连接双手协调和 benchmark 泛化。

### Q021. [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] 如何处理人类参考与机器人可执行性的差异？

**标准答案：** 它把人类参考转化为机器人可追踪目标，并通过 neural tracking controller 学习在机器人动力学和约束下实现相似运动。关键是不能直接复制人手轨迹，而要保留任务相关运动意图并满足机器人关节和接触限制。

**评分要点：** 必须说明 reference retargeting 和 tracking control。

### Q022. [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] 为什么能缩短示范？

**标准答案：** 它识别演示中低信息、冗长或可加速的片段，并保留高熵/高决策信息区域，使策略训练更聚焦关键动作。对灵巧操作，不能简单整体加速，因为接触建立和释放阶段有物理时序约束。

**评分要点：** 必须说明按信息量加速，而非机械快放。

### Q023. [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]] 对灵巧手动作分布有什么启发？

**标准答案：** 自回归策略把高维动作分解为条件序列，允许不同关节动作之间存在依赖关系。灵巧手多指动作高度耦合，独立高斯可能表达不足；自回归结构能表示拇指先动、其他手指跟随等条件协同模式。

**评分要点：** 必须提到高维动作条件依赖。

### Q024. [[Dynamic Reinforcement Learning for Actors]] 中 dynamic policy 思想为什么适合高动态控制？

**标准答案：** 高动态任务需要策略随状态变化调整动作分布、时间尺度和反馈敏感度。Dynamic RL 强调策略本身可具备动态结构或适应性，而不是静态映射。对转笔、抛接和快速换指，策略必须处理强时序依赖。

**评分要点：** 必须连接动态策略与高时序依赖。

### Q025. [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]] 为什么采用 modular architecture？

**标准答案：** 模块化可把触觉感知、状态估计、接触策略和低层控制拆开，降低端到端学习难度，并提高可诊断性。触觉灵巧操作中，各模块时间尺度和信号结构不同，强行单网络端到端容易样本低效且难迁移。

**评分要点：** 必须提到模块化的样本效率和可诊断性。

### Q026. [[Vision-force-fused Curriculum Learning for Robotic Assembly]] 对装配与转笔的共同启发是什么？

**标准答案：** 视觉提供全局位姿，力/触觉提供接触约束和误差方向；课程把难接触逐步引入。装配和转笔都需要在接触后根据力信号修正动作，而不是只靠视觉目标追踪。

**评分要点：** 必须说明视觉全局与力局部的互补。

### Q027. [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] 为什么 privileged action 只能用于训练？

**标准答案：** Privileged action 或特权信息依赖仿真真值、专家控制或不可部署状态，能提供训练监督和探索捷径，但真机部署不可直接获得。正确做法是蒸馏到可观测策略或用 teacher-student 框架迁移。

**评分要点：** 必须区分训练可得和部署可得。

### Q028. [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]] 对机器人模仿有什么通用经验？

**标准答案：** 示例轨迹可给出动作风格和时序先验，RL 在物理仿真中优化可行性与鲁棒性。对机器人，模仿不应只最小化轨迹误差，还要允许物理上等价的替代动作，并加入任务奖励和稳定性约束。

**评分要点：** 必须说出 imitation + RL 的互补。

### Q029. 面试官追问：为什么同一篇 dexterous RL 论文在仿真中成功不代表真机可用？

**标准答案：** 仿真可能使用特权状态、理想执行器、同步控制、准确物体位姿、过软接触或不真实摩擦。真机有延迟、温度、传感噪声、触觉漂移和安全限制。必须检查观测可得性、动作接口、接触参数、执行器 envelope 和失败恢复。

**评分要点：** 必须列出至少四类真机约束。

### Q030. 如何从这些论文中提炼一个严谨的 Sim-to-Real 实验矩阵？

**标准答案：** 应至少包含仿真 ablation、系统辨识/随机化范围、zero-shot 真机、少量真机适配、跨物体/摩擦/初始化泛化、失败模式分类和安全指标。对比方法要隔离 DR、课程、触觉、执行器模型和在线 correction 的贡献，避免把工程调参误称为算法突破。

**评分要点：** 必须包含实验维度和因果消融。

## Extended Questions

### Q031. 为什么 Sim-to-Real survey 中的 domain randomization 不是“范围越大越好”？

**标准答案：** 随机化范围过小不能覆盖真实参数，范围过大则训练分布包含大量不可能或过难环境，策略会变得保守或学不到精细动作。合理 DR 应围绕真实系统辨识结果和敏感性分析设定，并报告哪些参数真正影响任务。

**评分要点：** 必须说明覆盖不足与过度保守两端风险。

### Q032. System ID 与 policy adaptation 的根本差别是什么？

**标准答案：** System ID 在部署前或部署中估计显式物理参数，如摩擦、质量、延迟；policy adaptation 不一定输出可解释参数，而是从历史观测推断 latent 以条件化策略。前者更可解释，后者表达力强但诊断更难。

**评分要点：** 必须区分显式参数和策略 latent。

### Q033. 为什么转笔任务中的 reality gap 比普通 pick-and-place 更尖锐？

**标准答案：** 转笔依赖短时间接触切换、惯性相位、微小摩擦差异和执行器带宽。Pick-and-place 常有稳定抓取和视觉纠偏缓冲，而转笔某一相位失误会破坏整条动力学链，因此小 gap 会被快速放大。

**评分要点：** 必须提到相位链和动态放大。

### Q034. [[Lessons from Learning to Spin Pens]] 为什么提醒我们关注控制频率？

**标准答案：** 控制频率决定策略能否在滑移、换指和捕获瞬间及时反馈，也决定同一动作目标被底层保持多久。转笔中快速相位窗口很窄，频率不匹配会让正确策略在真机上错过接触时机。

**评分要点：** 必须说明频率影响相位时机。

### Q035. [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] 的 adaptation latent 为什么必须由历史推断？

**标准答案：** 物体质量、摩擦、执行器延迟和扰动通常无法单帧观测。历史动作与状态响应揭示系统当前动力学，adaptation module 通过这些序列推断 latent，使同一策略可适应不同真实条件。

**评分要点：** 必须提到动作-响应历史揭示隐变量。

### Q036. HORA 类方法在真机上最容易遗漏什么隐变量？

**标准答案：** 容易遗漏随时间变化而非 episode 固定的隐变量，如电机温度、触觉零漂、齿隙状态、材料磨损和接触表面污染。这些变量会让 latent 需要持续更新，而不是开局估一次就固定。

**评分要点：** 必须指出时变隐变量。

### Q037. [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model]] 为什么采用 joint-wise 而不是全局模型？

**标准答案：** 灵巧手每个关节的摩擦、减速器、带宽和延迟不同，joint-wise 模型能定位并补偿局部执行器差异。全局黑箱模型可能拟合整体轨迹但缺乏可解释性，跨姿态和跨动作泛化较弱。

**评分要点：** 必须说明关节级硬件差异。

### Q038. joint-wise neural dynamics model 的风险是什么？

**标准答案：** 它可能忽略关节间耦合、手指柔性和多接触负载造成的非局部效应。若每个关节独立建模，模型在强接触耦合下会低估真实相互影响。需要残差耦合项或整体验证。

**评分要点：** 必须提到独立假设忽略耦合。

### Q039. [[Grounded Action Transformation]] 与执行器模型补偿有什么共同点？

**标准答案：** 二者都不直接重写任务策略，而是在动作到真实效果之间加一层变换，让真实系统响应更接近训练环境。差别是 GAT 更抽象地学习 action mapping，执行器模型补偿更聚焦硬件动力学。

**评分要点：** 必须说明动作接口层补偿。

### Q040. 为什么 action transformation 不能无限补偿策略错误？

**标准答案：** 它只能修正动作效果的系统性偏差，无法让本来错误的任务意图变正确。若策略选择了错误接触相位或错误目标，动作变换器最多让错误动作更准确执行。必须分清 actuator gap 和 policy gap。

**评分要点：** 必须区分动作执行偏差与任务决策错误。

### Q041. [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation]] 的“real-to-sim”最难校准什么？

**标准答案：** 几何和视觉可通过重建获得，最难的是接触摩擦、柔顺、执行器延迟、传感器噪声和环境微小约束。这些隐藏物理变量决定真实动作后果，却不容易从静态扫描中恢复。

**评分要点：** 必须指出隐藏动态参数比几何更难。

### Q042. Real-to-sim-to-real 闭环如何避免过拟合单个场景？

**标准答案：** 需要把真实场景校准作为 anchor，同时在合理范围内随机化物体姿态、摩擦、光照、接触参数和扰动，并在多个真实实例上验证。否则策略只会适配一个数字孪生，而不具备泛化。

**评分要点：** 必须提到校准锚点和随机化泛化。

### Q043. [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction]] 的 correction 数据应该优先采哪些状态？

**标准答案：** 应优先采集策略即将失败但仍可纠正的 near-failure 状态，如滑移前、接触偏移、姿态偏差和动作饱和边界。普通成功状态信息量低，灾难后状态不可恢复，near-failure 最能训练补偿器。

**评分要点：** 必须说明 near-failure 数据价值。

### Q044. Online correction 方法如何避免人类 correction 延迟造成错误监督？

**标准答案：** 需要记录精确时间戳、估计人类反应延迟、把 correction 对齐到触发状态，并可能用短窗口 credit assignment。否则纠正动作会被标到错误状态上，训练出相位滞后的补偿策略。

**评分要点：** 必须提到时间对齐和延迟补偿。

### Q045. [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots]] 为什么比纯 BC 更适合稀疏奖励？

**标准答案：** 纯 BC 只学演示动作，遇到偏离状态难恢复；DemoStart 用演示状态初始化 RL，让策略从可成功邻域开始探索并逐步扩展到完整任务。它把演示变成探索课程。

**评分要点：** 必须说明中间状态初始化缓解探索。

### Q046. DemoStart 类课程可能带来什么偏差？

**标准答案：** 策略可能过度依赖演示轨迹附近的状态分布，缺少处理非演示失败路径的能力。若课程推进不覆盖真实扰动，部署时偏离演示后仍会失败。需要扰动演示和失败恢复数据。

**评分要点：** 必须提到演示邻域过拟合。

### Q047. [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] 的 teacher-student 逻辑是什么？

**标准答案：** Teacher 在训练中使用丰富或特权传感学到任务结构，student 逐步在更少、更真实的观测下模仿或继续 RL。核心是把不可部署信息蒸馏为可部署策略，而不是最终依赖特权状态。

**评分要点：** 必须说明 privileged observation 蒸馏。

### Q048. Sensing reduction 课程为什么不能一步移除所有特权观测？

**标准答案：** 突然移除会让策略面对观测分布断崖，value 和 action 都失去依据。逐步减少让策略学会用历史、可用传感和隐变量替代特权信息，形成平滑迁移。

**评分要点：** 必须说明观测分布平滑过渡。

### Q049. [[Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation]] 如何影响触觉实验设计？

**标准答案：** 触觉 ablation 必须固定课程和任务难度，否则触觉效果可能被状态分布变化掩盖或夸大。若有触觉组使用更容易课程，不能声称触觉本身带来提升。课程和模态应正交消融。

**评分要点：** 必须提到课程变量控制。

### Q050. 为什么课程学习应记录失败阶段分布？

**标准答案：** 成功率只说明最终结果，失败阶段分布揭示策略卡在接近、接触建立、旋转、捕获还是恢复。课程应针对瓶颈阶段调整，而不是机械增加难度。动态任务尤其需要阶段级诊断。

**评分要点：** 必须说明阶段级失败用于调课程。

### Q051. [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] 的仿真人类演示如何帮助多指协同？

**标准答案：** 人类演示提供换指、让位、支撑和施力顺序等协同先验，减少多指动作空间中的盲目探索。仿真增强可扩展物体和初始条件，使策略见到更多协同变体。

**评分要点：** 必须提到手指协同和接触时序。

### Q052. CyberDemo 类方法为什么仍需真实校准？

**标准答案：** 仿真人类演示的几何和接触时序可能合理，但真实手的执行器、触觉、摩擦和延迟不同。若不校准，演示中的细粒度力和时机在真机上可能不可执行。需要真实 rollout 或系统辨识闭环。

**评分要点：** 必须说明演示合理不代表硬件可执行。

### Q053. [[MimicGen - A Data Generation System for Scalable Robot Learning using Human Demonstrations]] 的片段重组为什么要求任务可分解？

**标准答案：** 片段重组假设任务可拆成相对独立的子技能，并能在新场景中通过位姿变换和过渡连接。若接触动力学强耦合、前一阶段细节决定后一阶段可行性，简单重组会产生不连续或不可执行轨迹。

**评分要点：** 必须说明子技能独立性假设。

### Q054. MimicGen 对灵巧手转笔的直接迁移为何困难？

**标准答案：** 转笔相位连续且高速，片段边界难定义，惯性和接触状态强依赖历史。把演示片段拼接可能破坏角动量和接触条件。需要相位对齐、动力学一致过渡和接触状态验证。

**评分要点：** 必须提到连续相位和动量约束。

### Q055. [[Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization]] 为什么适合生成 hard positives？

**标准答案：** 轨迹优化可在接触约束下找到接近成功边界的可行动作，如窄摩擦锥、临界姿态和复杂接触切换。这些 hard positives 比普通随机成功轨迹更能教会策略关键物理机制。

**评分要点：** 必须说明接近边界但物理可行。

### Q056. 物理驱动数据生成如何避免生成“优化器特有”伪轨迹？

**标准答案：** 需要用独立高保真仿真或真实系统 replay 验证，限制穿透、接触力、jerk 和执行器 envelope，并随机化初值和求解器参数。否则轨迹可能利用优化松弛而非真实物理。

**评分要点：** 必须提到 replay 验证和约束伪影。

### Q057. [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]] 为什么不直接复制到灵巧手？

**标准答案：** 人体运动模仿主要追踪关节和姿态，灵巧手操作还要控制物体接触、摩擦和外部状态。轨迹相似不保证物体 wrench 正确。需要加入接触、物体任务奖励和手部硬件约束。

**评分要点：** 必须指出物体接触任务不同。

### Q058. [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] 的 tracking controller 应如何处理不可达参考？

**标准答案：** 应保留参考中的任务意图，如接触序列和物体运动，而不是强追不可达关节姿态。控制器需要投影到机器人可行关节、力矩和接触约束内，并允许物理等价替代动作。

**评分要点：** 必须提到意图保留和可行投影。

### Q059. [[DemoSpeedup - Accelerating Visuomotor Policies via Entropy-Guided Demonstration Acceleration]] 为什么不能加速接触建立瞬间？

**标准答案：** 接触建立涉及减速、对准和力逐渐建立，过度加速会造成冲击或错过传感反馈。Entropy-guided 加速应跳过低信息等待段，保留高决策密度和物理敏感片段。

**评分要点：** 必须说明不同片段加速敏感性不同。

### Q060. Entropy-guided acceleration 中“高熵片段”代表什么？

**标准答案：** 高熵片段表示动作选择不确定性或决策信息量高，通常对应接触切换、路径选择、纠错和关键操作时机。这些片段应保留甚至重点训练，因为压缩它们会丢失技能核心。

**评分要点：** 必须解释高熵与关键决策。

### Q061. [[Autoregressive Policies for Continuous Control Deep Reinforcement Learning]] 对独立高斯策略的批评是什么？

**标准答案：** 独立高斯假设各动作维度条件独立，难以表达多指关节间强耦合。自回归策略按顺序建模条件分布，可表达某根手指动作依赖另一根手指目标的结构。

**评分要点：** 必须说明动作维度相关性。

### Q062. 自回归策略在高频控制中有什么代价？

**标准答案：** 它需要顺序生成动作维度，推理比并行高斯慢，且维度顺序会影响表达和训练。高频灵巧手控制必须评估延迟是否可接受，或用并行近似和低维动作参数化。

**评分要点：** 必须提到生成延迟和顺序依赖。

### Q063. [[Dynamic Reinforcement Learning for Actors]] 对策略架构的启发是什么？

**标准答案：** 策略不应只是静态 MLP，可包含动态记忆、相位变量、可变时间尺度或状态依赖探索。高动态操作中，策略必须根据接触阶段调整反馈敏感度和动作分布。

**评分要点：** 必须说明策略随状态/相位动态变化。

### Q064. [[Hindsight Experience Replay]] 在手内旋转中如何选择 hindsight goal？

**标准答案：** 可选择轨迹实际达到的物体姿态、角度或中间接触构型作为目标，但必须确保 reward 可重新计算且目标物理上有意义。不能把因仿真穿透或掉落后偶然状态当成功目标。

**评分要点：** 必须提到实际达到且物理有效。

### Q065. HER 对长时程动态任务的限制是什么？

**标准答案：** 它把失败状态重标为目标能增加监督，但不能自动解决达到该状态所需的动态相位和动量控制。若目标只描述终态，策略仍可能缺少中间接触序列。需要相位或轨迹级目标。

**评分要点：** 必须说明终态重标不含过程动力学。

### Q066. [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning]] 为什么强调 dynamics-aware？

**标准答案：** 在杂乱场景中，机器人可利用碰撞、支撑、重力和物体间相互作用。Dynamics-aware policy 学会预测并利用这些外部动力学，而不是把环境都当障碍避开。

**评分要点：** 必须说明利用外部动力学结构。

### Q067. Extrinsic dexterity 对 reward 设计有什么要求？

**标准答案：** Reward 不能只惩罚所有碰撞或偏离，因为某些碰撞和支撑是完成任务的工具。应区分有益交互和危险冲击，奖励任务进展、稳定性和可恢复性，而不是简单“无接触最好”。

**评分要点：** 必须说明环境接触可有益。

### Q068. [[RoboTwin 2.0 - A Scalable Data Generator and Benchmark for Robust Bimanual Manipulation]] 对 sim-to-real benchmark 的警示是什么？

**标准答案：** Benchmark 不能只测单一任务成功率，应覆盖双手协调、物体多样性、初始扰动、不同相机/机器人配置和失败恢复。否则大模型可能在数据集中成功，却无法证明真实鲁棒性。

**评分要点：** 必须提到多维泛化评测。

### Q069. 双手/多指数据生成为什么需要内力约束？

**标准答案：** 多接触系统中物体运动由合力和力矩决定，但内部对抗力也影响滑移、挤压和硬件负载。数据若只匹配物体轨迹，不约束内力，可能生成真机上危险或不可执行的协同动作。

**评分要点：** 必须解释内力虽不改合力但影响安全。

### Q070. [[Dextrous Tactile In-Hand Manipulation Using a Modular Reinforcement Learning Architecture]] 对 Sim-to-Real 有什么工程优势？

**标准答案：** 模块化允许单独校准触觉 encoder、状态估计、策略和低层控制，定位 gap 来源。端到端策略失败时难以判断是感知错、控制错还是动力学错；模块化更利于真机迭代。

**评分要点：** 必须说明模块化便于诊断 gap。

### Q071. 模块化架构的代价是什么？

**标准答案：** 模块边界可能丢失端到端最优信息，误差会级联，人工设计接口也可能限制策略表达。需要通过消融证明每个模块的必要性，并确保接口变量是控制充分的。

**评分要点：** 必须说明信息瓶颈和误差级联。

### Q072. [[Vision-force-fused Curriculum Learning for Robotic Assembly]] 对手内操作的 transferable insight 是什么？

**标准答案：** 复杂操作可按感知主导阶段切分：视觉负责远距离对准，力/触觉负责接触微调，课程逐步缩短误差和增加接触难度。手内操作也可从无接触姿态控制到轻触、滑移、动态旋转逐步推进。

**评分要点：** 必须说明感知阶段化课程。

### Q073. 为什么 assembly 论文的力控经验不能直接照搬到转笔？

**标准答案：** 装配多为准静态约束跟踪，转笔是高动态非抓取，依赖惯性和快速接触切换。力控思想可迁移为接触反馈和顺应控制，但控制带宽、相位和 reward 设计必须重做。

**评分要点：** 必须区分准静态装配和动态操作。

### Q074. [[Learning Long-Horizon Robot Manipulation Skills via Privileged Action]] 的 privileged action 如何用于 curriculum？

**标准答案：** Privileged action 可在训练早期提供专家级目标或辅助动作，使策略进入高奖励区域；随后逐步减少依赖，让 student 只用可部署观测完成任务。它和 sensing reduction 类似，都是训练特权到部署普通的过渡。

**评分要点：** 必须说明特权动作逐步蒸馏。

### Q075. Privileged action 方法如何防止 student 只学 teacher 偏差？

**标准答案：** 需要让 student 在扰动和自有 rollout 中继续 RL，加入任务 reward 和失败恢复，而不是只回归 teacher 动作。Teacher 提供启动，student 必须在真实观测分布上校正。

**评分要点：** 必须提到 student 自 rollout 和任务 reward。

### Q076. [[Deep Dynamics Models for Learning Dexterous Manipulation]] 中模型误差如何影响 planning？

**标准答案：** 模型误差会在多步 planning 中累积，优化器还会主动寻找模型预测高回报但真实无效的动作。接触不连续使这种 exploitation 更严重。需要短 horizon、ensemble、不确定性惩罚和真实数据回填。

**评分要点：** 必须说明误差累积和模型利用。

### Q077. dynamics model 应预测哪些变量才服务灵巧操作？

**标准答案：** 除关节和物体姿态，还应预测接触状态、滑移、触觉/力趋势、执行器可行性和失败风险。只预测视觉状态可能忽略控制最关键的接触物理。

**评分要点：** 必须包含接触/触觉/可行性变量。

### Q078. [[Dexterous Robotic Manipulation using Deep RL and Knowledge Transfer]] 中 transfer 如何避免负迁移？

**标准答案：** 要选择与目标任务共享接触结构、动作原语或物体动力学的源任务，并通过适配层或 fine-tuning 调整差异。若源任务只共享表面外观但物理机制不同，会把错误先验带入目标任务。

**评分要点：** 必须说明共享机制而非表面相似。

### Q079. 知识迁移中的 low-level skill 与 high-level strategy 如何区分？

**标准答案：** Low-level skill 是可复用动作原语，如稳定夹持、拨动、换指；high-level strategy 是任务阶段和技能组合，如先加速再捕获。迁移时低层技能更通用，高层策略更依赖任务结构。

**评分要点：** 必须区分原语和组合策略。

### Q080. [[GenDexGrasp - Generalizable Dexterous Grasping]] 与动态转笔的共性是什么？

**标准答案：** 二者都需要理解物体几何、接触可行区域和手构型约束。差异是抓取偏向静态稳定，转笔偏向动态接触和惯性利用。抓取表征可作为转笔初始接触和重抓基础。

**评分要点：** 必须说明共性与差异。

### Q081. generalizable grasping 的数据多样性应覆盖哪些维度？

**标准答案：** 需要覆盖物体形状、尺寸、材质、姿态、接触区域、手构型、摩擦和扰动。只换视觉外观而不换接触属性，无法证明灵巧抓取泛化。

**评分要点：** 必须包含几何和物理属性。

### Q082. Learning Dexterous Manipulation from Exemplar Object Trajectories and Pre-Grasps 这类方法为什么强调 pre-grasp？

**标准答案：** 对同一物体轨迹，初始手物接触构型决定后续动作是否可执行。Pre-grasp 提供可控起点和接触约束，使策略不必从任意手姿态探索整条任务。它把任务难度前移到可规划初始接触。

**评分要点：** 必须说明初始接触构型决定可执行性。

### Q083. exemplar trajectory 方法如何避免只追物体而忽略手？

**标准答案：** 需要同时约束手指接触、力闭合或操作可行性，而不是只最小化物体轨迹误差。否则机器人可能让物体轨迹在仿真中对了，但真实手指无法维持接触或施力。

**评分要点：** 必须提到手物接触约束。

### Q084. Learning One-Shot Dexterous Manipulation from Video 为什么难在动作反演？

**标准答案：** 视频展示物体和手的运动，但不直接给出机器人关节命令、接触力和控制增益。要从视频反演可执行动作，需要解决 retargeting、接触推断和动力学一致性。视觉相似不等于控制可行。

**评分要点：** 必须说明视频缺少力和动作信息。

### Q085. one-shot video imitation 对 sim-to-real 有什么潜在价值？

**标准答案：** 它可快速提供任务目标和粗略接触时序，减少人工编程和演示采集。但还需要仿真/真机闭环把视觉示范转成机器人可执行策略，尤其要校正手形、尺度和动力学差异。

**评分要点：** 必须说明视觉先验与执行闭环。

### Q086. Sim-to-Real 论文中“zero-shot”结果应如何解读？

**标准答案：** Zero-shot 表示没有用目标环境在线训练，但仍可能使用真实参数标定、真实传感模型、手工调控制器或安全过滤。读论文时要检查哪些真实信息已进入训练和部署，避免被术语误导。

**评分要点：** 必须说明 zero-shot 不等于完全无真实信息。

### Q087. 为什么跨物体泛化应报告物体物理属性？

**标准答案：** 形状相似但质量、惯量、摩擦和材质不同会导致完全不同接触响应。只报告物体图片无法判断泛化难度。严格实验应列出尺寸、质量、重心、摩擦或至少分组描述。

**评分要点：** 必须提到质量/惯量/摩擦。

### Q088. 为什么 sim-to-real 成功率必须配合硬件成本指标？

**标准答案：** 一个策略可能成功率高但动作粗暴、温升大、磨损快或需要频繁人工 reset。真实部署关注长期可靠性和安全成本，因此应报告温度、力矩饱和、碰撞、reset 次数和试验时长。

**评分要点：** 必须列出硬件成本指标。

### Q089. 为什么论文中的“真实机器人实验次数”很重要？

**标准答案：** 少量试验成功可能是偶然，无法覆盖初始化、物体和环境随机性。真实次数、随机种子、置信区间和失败样本能反映结果可信度。真机数据少时更应报告不确定性。

**评分要点：** 必须提到统计可信度。

### Q090. 如何识别一篇 Sim-to-Real 论文是否把 engineering tuning 伪装成算法贡献？

**标准答案：** 检查是否有清晰算法变量、对照组、固定工程设置和因果消融。若主要提升来自调控制频率、奖励权重、硬件阈值或人工初始化，却没有隔离贡献，就不能声称核心算法突破。

**评分要点：** 必须强调因果消融和固定工程变量。

### Q091. 为什么真实失败 replay 对 sim-to-real 闭环重要？

**标准答案：** 失败 replay 能显示仿真在哪个阶段偏离真实，如接触建立、滑移、执行器饱和或感知误差。把失败轨迹带回仿真重放可定位 gap，并指导随机化或模型补偿。

**评分要点：** 必须说明失败轨迹用于定位 gap。

### Q092. 为什么只在成功轨迹上做 system ID 有偏？

**标准答案：** 成功轨迹覆盖的是安全、稳定区域，失败边界处的摩擦、冲击、饱和和滑移未被辨识。策略部署时最需要了解这些边界。应纳入 near-failure 和失败前数据。

**评分要点：** 必须提到成功数据分布偏窄。

### Q093. Sim-to-Real 中的 observation delay 如何进入策略训练？

**标准答案：** 可在仿真中加入随机延迟、历史堆叠、RNN belief、时间戳对齐或延迟补偿模型。若训练无延迟而真机有延迟，策略会基于过期状态动作，接触任务尤其容易过冲。

**评分要点：** 必须说明延迟造成过期反馈。

### Q094. 为什么执行器温度应被视为 domain variable？

**标准答案：** 温度改变电机电阻、限流、摩擦和可持续力矩，使同一动作在 episode 不同时间响应不同。它是部署中的慢变隐变量，应记录、随机化或作为策略输入/安全约束。

**评分要点：** 必须说明温度改变动作响应。

### Q095. Sim-to-Real 论文如何证明 tactile model 有效？

**标准答案：** 应比较仿真触觉和真实触觉在固定动作 replay 下的空间图、频谱、延迟、接触面积和滑移事件，并做策略消融。只展示触觉图像相似不够，必须证明它提升闭环控制和泛化。

**评分要点：** 必须包含分布对齐和闭环效果。

### Q096. 为什么“仿真训练更久”不能替代正确模型？

**标准答案：** 如果仿真缺少真实因果机制，更多训练只会让策略更熟练地利用错误物理。训练时长提升的是仿真最优性，不会自动修复接触、执行器或传感结构性 gap。

**评分要点：** 必须说明结构性错误不可由样本量弥补。

### Q097. 如何设计一个小样本真机适配实验？

**标准答案：** 先固定预训练策略，收集少量多样化真实轨迹，分为适配集和保留测试集；比较无适配、system ID、residual correction、online RL；报告样本数、时间、失败和硬件成本。关键是证明每个真实样本带来的边际收益。

**评分要点：** 必须包含对照、保留测试和样本效率。

### Q098. 为什么 sim-to-real 方法需要长期稳定性测试？

**标准答案：** 短期成功无法暴露温升、磨损、传感漂移、物体表面变化和策略疲劳。长期测试能验证策略是否在分布慢变中保持安全和可恢复性，是从 demo 到系统的关键差异。

**评分要点：** 必须提到慢变硬件/环境因素。

### Q099. 面试官要求你从 05 专题提炼一条研究主线，你会怎么讲？

**标准答案：** 主线是先用仿真、演示和课程让策略学到接触技能，再用 system ID、DR、执行器模型、触觉模型和在线 correction 缩小 reality gap，最后通过真实失败 replay 和小样本适配形成闭环。核心不是单次 transfer，而是持续对齐动作-接触-硬件因果链。

**评分要点：** 必须形成从训练到部署再回流的闭环。

### Q100. Sim-to-Real 论文面试中最严格的追问是什么？

**标准答案：** 最严格的问题是：你的方法究竟修复了哪一条因果链上的 gap，证据是什么？回答必须指出 gap 来源、干预模块、对照实验、真实指标和失败模式变化。若只能说“随机化后更鲁棒”，说明机制解释不足。

**评分要点：** 必须强调 gap 机制、干预和证据链。
