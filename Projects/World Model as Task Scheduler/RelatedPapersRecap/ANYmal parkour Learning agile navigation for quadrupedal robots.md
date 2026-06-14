---
tags:
  - paper
  - locomotion
  - sim-to-real
  - parkour
  - WMTS
aliases:
  - ANYmal Parkour
paper-year: 2023
read-date: 2026-06-14
venue: Science Robotics
paper-pdf: "[[ANYmal parkour Learning agile navigation for quadrupedal robots.pdf]]"
related:
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Final_WMTS]]"
---

# ANYmal parkour Learning agile navigation for quadrupedal robots

> [!abstract] 核心贡献
> ANYmal Parkour 的核心是把复杂地形跑酷拆成可学习的局部运动技能与可感知的地形约束，让四足机器人在仿真中学到能迁移到真实障碍的 agile navigation。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — whole-body/contact dynamics
> - [[ControlTheory]] — low-level tracking and stability
> - [[ReinforcementLearning]] — sim-to-real policy learning

## 0. 阅读定位与范本价值
这篇 recap 按 `$paper-recap-insight` 的口径整理：先定位论文真正处理的瓶颈，再追踪变量来源、结构性假设、实验因果链和对 [[Final_WMTS]] 的迁移价值。这里不默认写实现代码；如果实现细节重要，只把它解释成信息流、数值约束或失败模式。

它在当前知识库中的角色是：WMTS 的 actuator model 可以借鉴这里的 teacher/student 分层：先让世界模型在特权 sim state 中学接触结果，再蒸馏到只用真实传感器的任务调度器。

## 1. 问题设定与动机

### 1.1 一句话核心
端到端从深度图到关节目标的策略很容易把地形理解、落脚规划、身体姿态控制和执行器限制纠缠在一起；一旦真机地形或摩擦偏移，策略会在最脆弱的子机制上失效。

### 1.2 直观隐喻
可以把这篇论文看成是在回答一个工程化问题：当真实机器人不允许无限试错，而任务又包含接触、长时序或分布偏移时，应该把哪一部分结构显式交给模型/控制器/课程，而不是让策略黑箱硬学。

### 1.3 现有方法的局限
- 只做端到端策略：容易把感知、动力学、接触和任务目标纠缠在同一个网络里，失败后很难知道是哪一层错。
- 只做解析模型：物理结构清晰，但真实摩擦、执行器延迟、视觉误差和高维接触通常无法完全建模。
- 只做数据扩张或随机化：能提高鲁棒性，但如果没有结构化变量，无法解释哪些扰动真的覆盖了真实失败模式。

### 1.4 Delta 分析
用课程、特权信息 teacher 和可部署 student 把“知道地形几何”和“执行动态动作”分层，可降低真实部署时的感知-控制耦合风险。

## 2. 核心方法与理论

### 2.1 变量来源追踪
| Variable | Domain/shape | Source | Fixed/learned/observed/computed | Meaning | Trap |
|---|---|---|---|---|---|
| $q,\dot q$ | body/joint state | proprioception | observed | whole-body state | state estimator delay |
| $u_t$ | motor command | policy/controller | chosen | desired joint target/torque | actuator bandwidth limits |
| $\phi$ | dynamics/domain parameters | randomization/ID | fixed/latent | mass/friction/delay | hidden on real robot |
| $J_c, f_c$ | contact Jacobian/forces | physics/contact | computed/hidden | ground interaction | contact timing dominates transfer |
| $r,c$ | reward/cost | task/safety spec | observed | skill and safety signal | reward hacking risk |

### 2.2 前置理论从零推导
这类方法可以统一写成闭环决策问题：机器人在时刻 $t$ 看到观测 $o_t$，内部构造状态或 belief $s_t$，选择动作 $a_t$，真实世界返回 $o_{t+1}$、reward/cost 或成功信号。关键分歧在于论文把哪一项结构化：

- 若结构化 $p(s_{t+1} \mid s_t, a_t)$，它是在做 world model / dynamics model。
- 若结构化 $\pi(a_t \mid o_t, g)$，它是在做 policy/action prior。
- 若结构化任务分布 $p(g)$ 或 level replay，它是在做 curriculum / task scheduler。
- 若结构化控制接口 $u \rightarrow \tau$ 或 force/position channel，它是在处理 sim-to-real actuator/control gap。

因此读这篇论文时不要只问“用了什么网络”，而要问：论文把哪一个不可控黑箱改造成了可解释、可采样或可约束的对象。

### 2.3 论文核心机制无跳步推导
- 仿真中生成障碍课程，teacher 使用更完整的地形/状态信息学习越障动作。
- student 只接收机载感知和 proprioception，通过蒸馏获得可部署策略。
- 域随机化和低层执行器建模吸收质量、摩擦、延迟和电机响应偏差。

从 sim-to-real 动力学角度看，真实闭环不是理想刚体系统，而是“刚体动力学 + 执行器/接触残差”：
$$
q_{t+1} = f_{rigid}(q_t,\dot q_t,\tau_t, c_t) + \Delta_{act/contact}(h_t,u_t)
$$
策略若只在理想 $f_{rigid}$ 上训练，会把延迟、饱和、摩擦和接触相位误差留到真机暴露；alignment/actuator model 的作用就是让训练时看到这些偏差。

### 2.4 概念边界与符号陷阱
- `state` 不一定是真实物理状态；很多论文里的 state 是 latent、belief 或 simulator privileged state。
- `action` 不一定是力矩；可能是关节目标、末端位姿、action chunk、diffusion latent 或 controller condition。
- `world model` 不等于完整世界重建；对机器人来说，只有能改变决策的预测才有价值。
- `sim-to-real` 不只是视觉 domain gap；执行器延迟、接触摩擦、控制频率和状态估计延迟通常更致命。

### 2.5 信息流/算法机制（无代码）
1. 观测/任务条件进入表示层，形成 $s_t$、latent 或 context。
2. 方法引入结构性假设：用课程、特权信息 teacher 和可部署 student 把“知道地形几何”和“执行动态动作”分层，可降低真实部署时的感知-控制耦合风险。
3. 策略、模型或优化器在这个结构上生成候选动作/预测/任务。
4. 实验通过成功率、预测误差、回报、约束违规或迁移表现检验结构是否真的减少了原瓶颈。

## 3. 训练、数据与实验

### 3.1 PDF 结构线索
- 2023 IEEE International Conference on Robotics and Automation (ICRA) (IEEE, 2023),

### 3.2 关键结果与证据
关注越障成功率、障碍类型覆盖、真机部署稳定性，以及对 perception degradation 的鲁棒性。

- PDF 线索：Although these modules were trained from simulated data only, our real-­world experiments demonstrate success-
- PDF 线索：mans or other animals, we are still far from fully exploiting robotic In our experimental validation, we demonstrate the system’s abil-
- PDF 线索：limbs. All of the above must be achieved in real time with limited in real time on the real robot. We show that the complete pipeline
- PDF 线索：noisy information. harsh conditions of the real world.
- PDF 线索：effective solution for robust perceptive locomotion (4–6). Neverthe- deep reinforcement learning frameworks, various new tasks have
- PDF 线索：less, such approaches are still far from exploiting the full potential of been demonstrated. Notable examples include jumping and climbing

### 3.3 Ablation 因果链
去掉特权 teacher 或地形课程 -> student 难以形成稳定落脚先验 -> 真机上表现为保守停滞或高冲击失败。

更一般地，ablation 应按这条链理解：移除结构性假设 -> 模型/策略需要用黑箱容量补偿 -> 在分布外、长 horizon 或接触切换处误差放大 -> 指标下降。不要只把 ablation 看成“少了一个模块所以差”，要看少掉的是哪一种 inductive bias。

### 3.4 工程约束与实验边界
- 真实机器人任务中，评估指标必须同时看成功率、恢复能力、约束违规和执行成本。
- 若论文只在仿真中验证，迁移到 WMTS 时要额外审查 actuator delay、contact sensing 和 domain randomization 覆盖。
- 若论文依赖视觉，灵巧手高速接触任务还需要检查遮挡、帧率和 tactile/proprioceptive 补偿。

## 4. 核心洞见

### 4.1 论文真正的 insight
用课程、特权信息 teacher 和可部署 student 把“知道地形几何”和“执行动态动作”分层，可降低真实部署时的感知-控制耦合风险。

### 4.2 为什么这个设计有效
它有效的原因不是“模型更大”，而是把原来难以泛化的自由度收缩到更合理的结构里：要么让动力学预测只负责短 horizon，要么让动作生成保留多模态，要么让课程集中在能力边界，要么让控制接口显式反映真实物理限制。

### 4.3 什么时候会失效
跑酷里的接触主要是足端-地形，灵巧手则是多指多接触和物体姿态耦合，不能直接把 locomotion 的域随机化强度搬到手内操作。

## 5. 替代方案与理论局限

### 5.1 理论维度
替代方案是把结构完全交给端到端网络。优点是表达力强、工程接口简单；缺点是变量来源不可解释，遇到真实分布偏移时很难定位失败。本文路线的优势在于引入了可检查的中间结构，但代价是结构假设一旦错，会形成系统性偏差。

### 5.2 算法维度
可以用 model-free RL、behavior cloning、MPC、diffusion action prior、ensemble uncertainty 或 curriculum learning 替代本文方法的一部分。选择哪一种，取决于瓶颈是探索、预测、动作多模态、控制延迟还是任务覆盖。

### 5.3 工程/实验维度
对 WMTS 最重要的不是复现 benchmark，而是做失败边界实验：换笔质量、换摩擦、加视觉延迟、限制电机带宽、制造接触丢失，观察方法是否仍能给出可恢复动作。

## 6. 对用户研究的启发

### 6.1 对灵巧手/转笔/PPO/DP/Sim-to-Real 的迁移
WMTS 的 actuator model 可以借鉴这里的 teacher/student 分层：先让世界模型在特权 sim state 中学接触结果，再蒸馏到只用真实传感器的任务调度器。

### 6.2 可验证实验建议
- 构造一个最小转笔或手内重定向环境，把方法中的核心结构单独接入，不先追求完整系统。
- 对比三组：端到端 PPO/DP、加入本文结构的版本、加入结构但打乱关键变量的负对照。
- 记录 failure mode：掉笔、打滑、过大接触力、动作饱和、视觉估计漂移、world model overconfident。

### 6.3 不应过度外推的点
不要因为论文在 locomotion、视觉操作或仿真 benchmark 上成功，就默认它能处理多指高速接触。迁移前必须确认：状态变量是否包含接触，动作接口是否匹配真实控制器，模型 horizon 是否短到足够可信。

## 7. 与知识体系的联系

### 与 [[Dynamics]] 的联系
whole-body/contact dynamics。这篇论文提供的是一个可迁移的结构化 bias：它把 端到端从深度图到关节目标的策略很容易把地形理解、落脚规划、身体姿态控制和执行器限制纠缠在一起；一旦真机地形或摩擦偏移，策略会在最脆弱的子机制上失效。 转化为可建模、可采样或可约束的问题。

### 与 [[ControlTheory]] 的联系
low-level tracking and stability。这篇论文提供的是一个可迁移的结构化 bias：它把 端到端从深度图到关节目标的策略很容易把地形理解、落脚规划、身体姿态控制和执行器限制纠缠在一起；一旦真机地形或摩擦偏移，策略会在最脆弱的子机制上失效。 转化为可建模、可采样或可约束的问题。

### 与 [[ReinforcementLearning]] 的联系
sim-to-real policy learning。这篇论文提供的是一个可迁移的结构化 bias：它把 端到端从深度图到关节目标的策略很容易把地形理解、落脚规划、身体姿态控制和执行器限制纠缠在一起；一旦真机地形或摩擦偏移，策略会在最脆弱的子机制上失效。 转化为可建模、可采样或可约束的问题。

## References
- 原始 PDF：[[ANYmal parkour Learning agile navigation for quadrupedal robots.pdf]]
- 项目入口：[[Final_WMTS]]
