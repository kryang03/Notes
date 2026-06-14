---
tags:
  - paper
  - curiosity
  - information-theory
  - reinforcement-learning
  - WMTS
aliases:
  - Latent Bayesian Surprise
paper-year: 2022
read-date: 2026-06-14
venue: AAAI
paper-pdf: "[[Curiosity-Driven Exploration via Latent Bayesian Surprise.pdf]]"
related:
  - "[[InformationTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Final_WMTS]]"
---

# Curiosity - Driven Exploration via Latent Bayesian Surprise

> [!abstract] 核心贡献
> Latent Bayesian Surprise 用 belief 更新幅度作为内在奖励：智能体不是追逐预测误差本身，而是追逐能真正改变 latent dynamics belief 的经验。

> [!tip] 与理论基础的关联
> - [[InformationTheory]] — surprise/information gain
> - [[ReinforcementLearning]] — intrinsic reward exploration
> - [[StochasticProcess]] — belief and uncertainty

## 0. 阅读定位与范本价值
这篇 recap 按 `$paper-recap-insight` 的口径整理：先定位论文真正处理的瓶颈，再追踪变量来源、结构性假设、实验因果链和对 [[Final_WMTS]] 的迁移价值。这里不默认写实现代码；如果实现细节重要，只把它解释成信息流、数值约束或失败模式。

它在当前知识库中的角色是：WMTS 的 saturation-boundary active learning 可以用 surprise 选择真实交互：优先采样会改变 actuator/contact belief 的动作，而不是随机打满动作空间。

## 1. 问题设定与动机

### 1.1 一句话核心
普通 prediction error curiosity 会被噪声、不可控随机性或视觉 novelty 误导；对操作任务，真正有价值的是能减少动力学/任务不确定性的交互。

### 1.2 直观隐喻
可以把这篇论文看成是在回答一个工程化问题：当真实机器人不允许无限试错，而任务又包含接触、长时序或分布偏移时，应该把哪一部分结构显式交给模型/控制器/课程，而不是让策略黑箱硬学。

### 1.3 现有方法的局限
- 只做端到端策略：容易把感知、动力学、接触和任务目标纠缠在同一个网络里，失败后很难知道是哪一层错。
- 只做解析模型：物理结构清晰，但真实摩擦、执行器延迟、视觉误差和高维接触通常无法完全建模。
- 只做数据扩张或随机化：能提高鲁棒性，但如果没有结构化变量，无法解释哪些扰动真的覆盖了真实失败模式。

### 1.4 Delta 分析
用 posterior-before 与 posterior-after 的 KL 衡量“这条经验让模型信念改变了多少”，可以把探索从感官新奇转向可学习的不确定性。

## 2. 核心方法与理论

### 2.1 变量来源追踪
| Variable | Domain/shape | Source | Fixed/learned/observed/computed | Meaning | Trap |
|---|---|---|---|---|---|
| $b_t$ | belief/posterior | Bayesian model | computed | uncertainty state | approximation can be overconfident |
| $z_t$ | latent state | encoder/world model | computed | compressed dynamics variable | may ignore controllable factors |
| $a_t$ | exploration action | policy | chosen | intervention to gain information | novelty not equal information |
| $D_{KL}$ | belief change | posterior update | computed reward | Bayesian surprise | direction of KL matters |
| $r^i_t$ | intrinsic reward | exploration module | computed | drives exploration | can chase noise |

### 2.2 前置理论从零推导
这类方法可以统一写成闭环决策问题：机器人在时刻 $t$ 看到观测 $o_t$，内部构造状态或 belief $s_t$，选择动作 $a_t$，真实世界返回 $o_{t+1}$、reward/cost 或成功信号。关键分歧在于论文把哪一项结构化：

- 若结构化 $p(s_{t+1} \mid s_t, a_t)$，它是在做 world model / dynamics model。
- 若结构化 $\pi(a_t \mid o_t, g)$，它是在做 policy/action prior。
- 若结构化任务分布 $p(g)$ 或 level replay，它是在做 curriculum / task scheduler。
- 若结构化控制接口 $u \rightarrow \tau$ 或 force/position channel，它是在处理 sim-to-real actuator/control gap。

因此读这篇论文时不要只问“用了什么网络”，而要问：论文把哪一个不可控黑箱改造成了可解释、可采样或可约束的对象。

### 2.3 论文核心机制无跳步推导
- 维护 latent dynamics 或模型参数的 belief/posterior。
- 执行动作后根据新 transition 更新 posterior。
- 以内在奖励近似 $D_{KL}(q_{new} || q_{old})$，鼓励采集高信息增益样本。

从信息论角度看，探索奖励应衡量 belief 的变化，而不是视觉新奇本身：
$$
r_t^{\mathrm{int}} \propto D_{KL}\left(q_{t+1}(\theta \mid h_t,a_t,o_{t+1})\;\|\;q_t(\theta \mid h_t)\right)
$$
如果 KL 大，说明这次交互真正改变了模型对动力学或环境参数的信念；如果只是 prediction error 大但 posterior 不变，可能只是不可控噪声。

### 2.4 概念边界与符号陷阱
- `state` 不一定是真实物理状态；很多论文里的 state 是 latent、belief 或 simulator privileged state。
- `action` 不一定是力矩；可能是关节目标、末端位姿、action chunk、diffusion latent 或 controller condition。
- `world model` 不等于完整世界重建；对机器人来说，只有能改变决策的预测才有价值。
- `sim-to-real` 不只是视觉 domain gap；执行器延迟、接触摩擦、控制频率和状态估计延迟通常更致命。

### 2.5 信息流/算法机制（无代码）
1. 观测/任务条件进入表示层，形成 $s_t$、latent 或 context。
2. 方法引入结构性假设：用 posterior-before 与 posterior-after 的 KL 衡量“这条经验让模型信念改变了多少”，可以把探索从感官新奇转向可学习的不确定性。
3. 策略、模型或优化器在这个结构上生成候选动作/预测/任务。
4. 实验通过成功率、预测误差、回报、约束违规或迁移表现检验结构是否真的减少了原瓶颈。

## 3. 训练、数据与实验

### 3.1 PDF 结构线索
- PDF 文本抽取未稳定识别章节标题；需要人工读图/附录时再补。

### 3.2 关键结果与证据
关注稀疏奖励环境的探索效率、与 prediction error/ensemble disagreement 的比较，以及在 stochastic distractor 下是否更稳。

- PDF 线索：ing of the dynamics of the system, drastically reducing the Several successful approaches modeled intrinsic rewards
- PDF 线索：exploration, for continuous tasks, and looking at the game
- PDF 线索：fects caused by stochasticity in the environment, which is of- less predictable states suffers from the ‘NoisyTV problem’,
- PDF 线索：successfully accomplish tasks by maximising a reward sig- liefs of an agent, after observing new data. As we also
- PDF 线索：robotic manipulation tasks, such as solving a Rubik’s cube provided, potentially overcoming the NoisyTV issue. Pre-
- PDF 线索：ing rewards for complex tasks (Amodei et al. 2016; Clark Contributions. In this work, we present a new curiosity

### 3.3 Ablation 因果链
把 Bayesian surprise 换成 raw prediction error -> agent 会偏向不可预测噪声 -> 因为误差高不等于可学习信息高。

更一般地，ablation 应按这条链理解：移除结构性假设 -> 模型/策略需要用黑箱容量补偿 -> 在分布外、长 horizon 或接触切换处误差放大 -> 指标下降。不要只把 ablation 看成“少了一个模块所以差”，要看少掉的是哪一种 inductive bias。

### 3.4 工程约束与实验边界
- 真实机器人任务中，评估指标必须同时看成功率、恢复能力、约束违规和执行成本。
- 若论文只在仿真中验证，迁移到 WMTS 时要额外审查 actuator delay、contact sensing 和 domain randomization 覆盖。
- 若论文依赖视觉，灵巧手高速接触任务还需要检查遮挡、帧率和 tactile/proprioceptive 补偿。

## 4. 核心洞见

### 4.1 论文真正的 insight
用 posterior-before 与 posterior-after 的 KL 衡量“这条经验让模型信念改变了多少”，可以把探索从感官新奇转向可学习的不确定性。

### 4.2 为什么这个设计有效
它有效的原因不是“模型更大”，而是把原来难以泛化的自由度收缩到更合理的结构里：要么让动力学预测只负责短 horizon，要么让动作生成保留多模态，要么让课程集中在能力边界，要么让控制接口显式反映真实物理限制。

### 4.3 什么时候会失效
posterior 近似若过于自信，KL 会低估未覆盖 contact mode；需要 ensemble 或粒子化 belief 辅助。

## 5. 替代方案与理论局限

### 5.1 理论维度
替代方案是把结构完全交给端到端网络。优点是表达力强、工程接口简单；缺点是变量来源不可解释，遇到真实分布偏移时很难定位失败。本文路线的优势在于引入了可检查的中间结构，但代价是结构假设一旦错，会形成系统性偏差。

### 5.2 算法维度
可以用 model-free RL、behavior cloning、MPC、diffusion action prior、ensemble uncertainty 或 curriculum learning 替代本文方法的一部分。选择哪一种，取决于瓶颈是探索、预测、动作多模态、控制延迟还是任务覆盖。

### 5.3 工程/实验维度
对 WMTS 最重要的不是复现 benchmark，而是做失败边界实验：换笔质量、换摩擦、加视觉延迟、限制电机带宽、制造接触丢失，观察方法是否仍能给出可恢复动作。

## 6. 对用户研究的启发

### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real 的迁移
WMTS 的 saturation-boundary active learning 可以用 surprise 选择真实交互：优先采样会改变 actuator/contact belief 的动作，而不是随机打满动作空间。

### 6.2 可验证实验建议
- 构造一个最小转笔或手内重定向环境，把方法中的核心结构单独接入，不先追求完整系统。
- 对比三组：端到端 PPO/DP、加入本文结构的版本、加入结构但打乱关键变量的负对照。
- 记录 failure mode：掉笔、打滑、过大接触力、动作饱和、视觉估计漂移、world model overconfident。

### 6.3 不应过度外推的点
不要因为论文在 locomotion、视觉操作或仿真 benchmark 上成功，就默认它能处理多指高速接触。迁移前必须确认：状态变量是否包含接触，动作接口是否匹配真实控制器，模型 horizon 是否短到足够可信。

## 7. 与知识体系的联系

### 与 [[InformationTheory]] 的联系
surprise/information gain。这篇论文提供的是一个可迁移的结构化 bias：它把 普通 prediction error curiosity 会被噪声、不可控随机性或视觉 novelty 误导；对操作任务，真正有价值的是能减少动力学/任务不确定性的交互。 转化为可建模、可采样或可约束的问题。

### 与 [[ReinforcementLearning]] 的联系
intrinsic reward exploration。这篇论文提供的是一个可迁移的结构化 bias：它把 普通 prediction error curiosity 会被噪声、不可控随机性或视觉 novelty 误导；对操作任务，真正有价值的是能减少动力学/任务不确定性的交互。 转化为可建模、可采样或可约束的问题。

### 与 [[StochasticProcess]] 的联系
belief and uncertainty。这篇论文提供的是一个可迁移的结构化 bias：它把 普通 prediction error curiosity 会被噪声、不可控随机性或视觉 novelty 误导；对操作任务，真正有价值的是能减少动力学/任务不确定性的交互。 转化为可建模、可采样或可约束的问题。

## References
- 原始 PDF：[[Curiosity-Driven Exploration via Latent Bayesian Surprise.pdf]]
- 项目入口：[[Final_WMTS]]
