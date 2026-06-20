---
tags:
  - paper
  - sim-to-real
  - actuator-model
  - reinforcement-learning
aliases:
  - ETH Actuator Network
  - Learning Agile Motor Skills
paper-year: 2019
read-date: 2026-04-26
venue: Science Robotics
paper-pdf: "[[Papers/Learning Agile and Dynamic Motor Skills for Legged Robots.pdf]]"
related:
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
---

# Learning Agile and Dynamic Motor Skills for Legged Robots

> [!abstract] 核心贡献
> 该工作提出"解析刚体动力学 + 学习型 Actuator Network + 域随机化 + PPO 策略"的 sim-to-real 管线，使 ANYmal 在仿真训练后直接获得高速、恢复等动态真机技能。

> [!tip] 与理论基础的关联
> - [[Dynamics]] — 刚体链条由多体动力学解析承担，学习只补 actuator gap
> - [[ControlTheory]] — 位置目标→力矩的低层闭环（PD/软件/电机），Actuator Network 近似它
> - [[ReinforcementLearning]] — PPO 在 hybrid simulator 训练；结构化模型补偿的 sim-to-real
>
> **核心技术**: Actuator Network (action→torque), 解析刚体 + 学习执行器 hybrid sim, Dynamics Randomization, PPO

## 1. 问题设定与动机

### 1.1 核心洞察

现实差距并不均匀分布：刚体链条可由经典动力学高效模拟，真正难建模的是从控制指令到关节力矩之间的 actuator/software dynamics。把 reality gap 集中进 Actuator Network，比试图用全黑箱模型重建整个机器人更稳。

### 1.2 现有方法局限

- 模块化控制器需要大量人工调参，难以为新动作快速扩展。
- 纯解析 actuator model 对 SEA、伺服、电气延迟和低层控制链路不够准确。
- 直接真机 RL 对动态平衡机器人风险过高、成本过大。

## 2. 核心方法/理论

### 2.0 变量来源追踪

枢纽：**reality gap 集中到 actuator network**（action→torque），刚体保留解析——结构化分解而非全黑箱。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $a_t$ | 关节位置目标 | policy 输出 | 是（策略） | 高层动作 | 非力矩 |
| $\tau_t^{real}$ | $\mathbb{R}^{12}$ | ANYmal torque sensing | 否（监督目标） | 真实关节力矩 | actuator net 拟合对象 |
| $\hat{\tau}_t=f_{act}(\cdot)$ | $\mathbb{R}^{12}$ | actuator net 输出 | 是 | 预测力矩 | 验证误差 ~0.74 Nm（≪ 解析） |
| $f_{act}$ | 3层×32 MLP | 学习（真机 log） | 是 | action→torque 映射 | 黑箱，无稳定性保证 |
| $q,\dot{q}$ 历史 | 本体感知 | 观测 | 否 | 关节状态历史 | **历史须覆盖延迟总和** |
| 刚体 sim | 解析 | 物理引擎 | — | 多体动力学 | actuator net 不替代它 |

### 2.1 Delta 分析

1. 对刚体部分使用高效解析模拟；
2. 对 actuator/software chain 使用监督学习拟合 action-to-torque；
3. 在 hybrid simulator 中训练 PPO 策略并通过 dynamics randomization 提升鲁棒性。

### 2.2 Actuator Network 数学定义

策略输出关节位置目标 $a_t$，底层 PD/软件/电机链路产生真实关节力矩 $\tau_t$。学习：

$$
\hat{\tau}_t=f_{act}(a_{t-H:t}, q_{t-H:t}, \dot{q}_{t-H:t}, \tau_{t-H:t-1};\theta_{act}).
$$

监督损失：

$$
\mathcal{L}_{act}=\sum_t\|\tau_t^{real}-\hat{\tau}_t\|_2^2.
$$

论文中 actuator net 是 3 hidden layers、每层 32 units 的 MLP，输入关节状态历史与目标，输出 12 个关节力矩；验证误差约 0.740 Nm，显著小于忽略 actuator dynamics 的误差。

策略训练目标为 PPO：

$$
\mathcal{L}_{PPO}=\mathbb{E}_t\left[\min(r_t(\theta)\hat{A}_t,\text{clip}(r_t(\theta),1-\epsilon,1+\epsilon)\hat{A}_t)\right]-c_v\mathcal{L}_V+c_e\mathcal{H}.
$$

### 2.3 核心伪代码

```python
# actuator data are logged from the real robot
act_input = torch.cat([target_history, q_history, qd_history, torque_history], dim=-1)
tau_pred = actuator_net(act_input)              # [B, 12]
act_loss = ((tau_pred - tau_measured) ** 2).mean()
act_loss.backward()

# during policy training in simulation
target = policy(obs)                            # joint position targets
tau = actuator_net(make_history(target, q, qd)) # replaces ideal torque source
q_next, qd_next = rigid_body_sim.step(q, qd, tau)
reward = velocity_tracking_reward(q_next, command) - energy_penalty(tau)
ppo_update(policy, reward)
```

**物理量来源**：$\tau^{real}$ 来自 ANYmal torque sensing/logging；$a_t$ 是 policy 输出；$q,\dot{q}$ 来自 proprioception；$\hat{\tau}$ 在仿真中作为刚体动力学输入。

### 2.4 概念边界与符号陷阱

- **actuator net 只学 action→torque、不替代刚体 sim**：结构化分解保留物理结构、降低学习负担。
- **历史窗口须覆盖通信/软件/执行器延迟总和**：否则当前状态无法恢复延迟/带宽隐变量。
- **actuator net 推理频率须匹配仿真步长**：否则延迟建模与数值积分误差混淆。
- **actuator net 是黑箱、无稳定性保证**（§5 理论局限）。
- **硬件温度/磨损/负载慢漂移 → 离线 actuator net 需在线校准**（§5 工程局限）。
- **reality gap 不均匀分布**：集中归因到 actuator，而非全机器人黑箱。

## 3. 训练与实验细节

### 3.1 训练设定

- Step 1：系统辨识物理参数并估计不确定性。
- Step 2：用真机 log 训练 Actuator Network。
- Step 3：在含 actuator net 的仿真中训练 PPO control policy。
- Step 4：策略直接部署真机。

### 3.2 关键结果

- ANYmal 可跟踪高层速度命令，平均速度误差约 2.2%。
- 学到的控制器在 torque magnitude 与能耗上优于已有 hand-designed controller，torque 使用降低约 23%-36%。
- 高速 locomotion 打破 ANYmal 之前速度记录约 25%。
- recovery policy 可从多种复杂摔倒姿态中恢复。

### 3.3 Ablation 因果链

| 对比 | 结果 | 机制 |
|---|---|---|
| 解析 actuator model | torque prediction 明显偏差 | 多层软件延迟、SEA 顺应性、低层控制器动态难以完整建模 |
| 学习型 actuator net | torque prediction 接近测量数据 | 历史窗口隐式吸收延迟与带宽限制 |
| 只做精确系统辨识、不随机化 | transfer 脆弱 | 单一模型无法覆盖真机参数漂移和外界扰动 |

## 4. 工程关键细节

- 历史窗口长度必须覆盖通信/软件/执行器延迟总和，否则当前状态无法恢复隐变量。
- Actuator Network 只负责 action-to-torque，不应替代刚体模拟器；这种分解保留物理结构，降低学习负担。
- actuator net 的推理频率必须匹配仿真步长，否则会把延迟建模和数值积分误差混在一起。

## 5. 核心洞见

### 5.1 理论局限性

- **理论**：actuator net 是输入输出黑箱，不提供稳定性保证。
- **算法**：PPO 仍依赖 reward shaping 与大规模仿真采样。
- **工程**：如果硬件温度、磨损、负载发生慢漂移，离线 actuator net 需要在线校准。

### 5.2 与 WMTS 的启发

[[Final_WMTS]] 的 Actuator Model 应继承这篇论文的结构性分解：刚体动力学用解析/physics-informed model，执行器链路用历史窗口 neural model。但灵巧手比 ANYmal 更需要显式温度 $T_{motor}$、反馈力矩 $\tau_{fb}$ 和触觉残差，因为丝杠摩擦、连杆弹性和指尖接触会把 actuator gap 放大到任务层面。

> [!note] neural dynamics 的"作用对象谱" + reality gap 的物理归因分解
> Learning Agile 的 Actuator Network 与 [[Deep Dynamics Models for Learning Dexterous Manipulation|PDDM]]、[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]] 同属"学习的动力学"，但**作用对象不同**——构成一条谱：
>
> | 论文 | 学什么 dynamics | 粒度 |
> |------|----------------|------|
> | Learning Agile | **actuator**（action→torque） | 执行器链路 |
> | [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | 关节级 forward dynamics | 关节 |
> | [[Deep Dynamics Models for Learning Dexterous Manipulation\|PDDM]] | 整体 forward dynamics | 系统 |
>
> **新 insight——reality gap 的两种分解**：[[A Survey of Sim-to-Real Methods in RL|A Survey]] 按**信息论**分（MDP 四元素 $\Delta_S/\Delta_A/\Delta_T/\Delta_R$）；Learning Agile 揭示按**物理来源**分（rigid dynamics gap [解析可建] / actuator gap [学习补] / contact-sensing gap [触觉]）——二者互补。其核心方法论"**reality gap 不均匀分布，按物理来源归因、各个击破（刚体解析 + actuator 学习）比全黑箱稳**"正是 §5.2/§7 给 WMTS 的设计原则：WM 应分 rigid/actuator/contact 三个预测目标。这与 [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]]（关节级）、[[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]（接触 sensing）各处理物理分解的一块。

## 6. 与知识体系的联系

- [[Dynamics]]：刚体链条仍由多体动力学承担，学习只补 actuator gap。
- [[ControlTheory]]：位置目标经低层控制器转力矩，Actuator Network 近似这一闭环映射。
- [[ReinforcementLearning]]：PPO 在 hybrid simulator 中训练，属于 sim-to-real RL 的结构化模型补偿路线。

## 7. 局限与未来方向

对灵巧手转笔，关键不是照搬四足 locomotion reward，而是照搬**物理归因方式**：将 reality gap 分解为 actuator gap、rigid dynamics gap、contact sensing gap，并分别给 WM 设计预测目标与损失。
