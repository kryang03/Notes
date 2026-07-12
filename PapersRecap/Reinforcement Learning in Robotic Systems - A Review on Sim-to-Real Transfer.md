---
tags:
  - paper
  - survey
  - sim-to-real
  - reinforcement-learning
aliases:
  - RL sim-to-real review
  - Tiwari 2026 review
paper-year: 2026
read-date: 2026-03-13
venue: Robotics and Autonomous Systems
paper-pdf: "[[Papers/Reinforcement learning in robotic systems - A review on sim-to-real transfer.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[EmbodiedAI]]"
---

# Reinforcement Learning in Robotic Systems: A Review on Sim-to-Real Transfer

> [!abstract] 核心贡献
> 从信息流和方法作用对象的角度，提出 sim-to-real 迁移的统一框架，将现有方法分为三大类：面向真实环境的模型优化、基于仿真环境的知识迁移、仿真-现实迭代策略精炼。综述了 System ID、DR、Domain Adaptation、Multi-Fidelity、Progressive Neural Networks 等方法。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — MDP $(S,A,P,R,\gamma)$；sim/real 的 $P,R$ 差异是 gap 数学本质
> - [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL §9]] — 本 review 的三分类（模型优化 / 知识迁移 / 迭代精炼）正是 §9 治疗手段的"怎么修"切分。
> - [[Dynamics]] — System ID / 执行器建模 / 接触动力学保真度
> - [[Actuation#10. 迁移层 II：数据驱动执行器模型 (Actuator Model)|Actuation §10]] — 呼应本 review §3 核心洞见"执行器建模被低估"：**电流≠关节力矩** 暗线——电机/传动级建模是最被忽视又最关键的 $\Delta_T$ 子源，Actuator Net 是其数据驱动解。
> - [[EmbodiedAI]] — sim-to-real 基准平台（Real Robot Challenge / HomeRobot）
> - [[Optimization]] — DR 作为鲁棒优化 $\max_\theta\mathbb{E}_\xi[J]$
>
> **核心技术**: 三分类框架（模型优化 / 知识迁移 / 迭代精炼）、System ID、DR/ADR、Domain Adaptation、R2S2R

### 核心洞察（直观隐喻）

**Sim-to-Real 如同"在梦中练武"**——仿真是高效但不完美的梦境，Reality Gap 是梦与现实的差异。三类方法分别对应：让梦更真实（System ID）、让武功对梦境差异免疫（DR/DA）、醒来后根据实战修正梦的设定（R2S2R）。

### 现有单一方法的局限

- **纯 System ID**: 参数辨识精度有上限，接触/摩擦等突变现象无法完美建模
- **纯 DR**: 过宽参数范围导致策略保守（"对所有天气训练 → 任何天气下都不最优"）
- **纯 Domain Adaptation**: 依赖真实数据收集，安全关键场景中受限
- **通病**: 缺乏系统性组合策略——多数工作只用一种方法

## 1. 综述框架

### 三大类 Sim-to-Real 方法

| 类别 | 核心思路 | 代表方法 |
|------|---------|---------|
| **模型优化** | 让仿真更接近真实 | System ID, 物理参数辨识, 执行器建模 |
| **知识迁移** | 让策略对 Gap 鲁棒 | Domain Randomization, Domain Adaptation, Transfer Learning |
| **迭代精炼** | 仿真-真实交替优化 | Real-to-Sim-to-Real (R2S2R), Multi-Fidelity Learning |

### 关键概念

- **Reality Gap**: 物理动力学、感知输入、环境变异性的系统性差异
- **MDP 框架**: $\mathcal{M} = (S, A, P, R, \gamma)$ — sim/real 的 $P$, $R$ 差异是 Gap 的数学本质
- **仿真优势**: 低成本、可真实性、多维度、安全性

### 1.1 核心概念与 Gap 溯源

综述的"变量来源追踪"——把核心概念溯清。本 review 按**"怎么修"**分三类（与 [[A Survey of Sim-to-Real Methods in RL|A Survey]] 按"修什么"的 MDP 四元素正交，见文末元综合）。

| 概念 | 定义/来源 | 意义 | 陷阱/对比 |
|------|----------|------|----------|
| Reality Gap | 物理/感知/环境变异差异 | sim-real 系统性差异 | = A Survey 的 $\Delta_S/\Delta_A/\Delta_T/\Delta_R$ 总和 |
| $\Delta P$ | $\|P_{sim}-P_{real}\|_{TV}$ | 转移概率差（gap 数学本质） | DR 有效性依赖 $P_{real}\in\text{support}(\rho)$ |
| 模型优化类 | 让仿真像真实 | System ID / 执行器建模 | 精度有上限（接触/摩擦突变难建模） |
| 知识迁移类 | 让策略鲁棒 | DR / DA / Transfer | 过宽 DR → 策略保守 |
| 迭代精炼类 | sim-real 交替 | R2S2R / Multi-Fidelity | = RialTo |
| $\rho(\xi)$ | DR 参数分布 | 物理参数随机化 | ADR 自适应优先最难配置 |
| $L_f$ | 动力学 Lipschitz | 误差传播率 | 高速接触 $L_f\gg1$ → 误差指数放大 |

## 2. 方法分类总结

### System Identification
- 物理参数辨识 → 仿真器校准
- 自动化调优趋势

### Domain Randomization
- 环境参数 + 机器人参数
- 从均匀分布到 ADR (Automatic DR)

### Domain Adaptation
- 仿真→真实的表征对齐
- 对抗训练 (GAN-based)

### 新兴方向
- **Progressive Neural Networks**: 列式扩展防止灾难性遗忘
- **执行器级建模**: 精确的电机/传动仿真
- **R2S2R 管线**: 真实数据反馈→仿真改进→策略重训

## 2.5 代表性 DR 训练管线伪代码

```python
import torch

def domain_randomization_step(env, params_dist):
    """每个 episode 开始时随机化环境参数"""
    friction = params_dist['friction'].sample()   # Uniform(0.5, 1.5)
    mass = params_dist['mass'].sample()           # Uniform(0.8, 1.2) * nominal
    latency = params_dist['latency'].sample()     # Uniform(0, 30ms)
    env.set_physics_params(friction=friction, mass=mass, action_latency=latency)
    return env.reset()

def train_sim2real_ppo(env, policy, critic, epochs=5000):
    for epoch in range(epochs):
        obs = domain_randomization_step(env, DR_PARAMS)
        trajectory = []
        for t in range(max_steps):
            action = policy(torch.tensor(obs))
            obs_next, reward, done, info = env.step(action.detach().numpy())
            trajectory.append((obs, action, reward, done))
            obs = obs_next
            if done: break
        advantages = compute_gae(trajectory, critic, gamma=0.99, lam=0.95)
        ppo_update(policy, critic, trajectory, advantages, clip_eps=0.2)
```

## 2.6 常见 Sim-to-Real 训练细节总结

| 维度 | 典型设定 |
|------|----------|
| **仿真器** | MuJoCo / Isaac Gym / PyBullet |
| **并行环境** | 512–4096 (GPU-accelerated) |
| **总步数** | 1e8–1e10 |
| **DR 参数范围** | 摩擦 ×0.5–2.0, 质量 ±20%, 延迟 0–40ms |
| **策略网络** | MLP [256,256] 或 [512,256,128] |
| **学习率** | 3e-4 (Adam), 线性衰减 |

## 2.7 跨方法 Ablation 规律

综合 OpenAI Rubik's Cube、DemoStart、AnyRotate 等工作：

| 消融组件 | 成功率变化 | 因果机制 |
|---------|-----------|----------|
| 去掉 DR | ↓40–60% | 策略对物理参数过拟合 → 真机不匹配时崩溃 |
| 去掉 System ID | ↓10–25% | 仿真偏差增大 → DR 需更宽 → 策略更保守 |
| 去掉执行器模型 | ↓15–30% | 力矩-关节映射失配 → 精细操作失败 |
| 去掉观测噪声注入 | ↓5–15% | 真机传感器噪声导致策略抖动 |
| DR + System ID | 最优 | 正交互补 |

## 2.8 工程实践要点 (Engineering Tricks)

1. **DR 参数范围校准**: 先做粗略 System ID 确定 nominal，再 ±50% 范围 DR
2. **通信延迟建模**: USB 30ms, 以太网 1ms — 最常被忽视的 Gap 源
3. **动作平滑**: 加低通滤波或变化率惩罚 $r_{\text{smooth}} = -\|\Delta a\|^2$ 抑制高频抖动
4. **异步 GPU 采集**: Isaac Gym 并行可将墙钟时间降低 10–100×
5. **传感器对齐**: 相机 intrinsic/extrinsic 标定误差可吃掉视觉 DA 全部收益

## 2.9 跨方法对比矩阵

| 方法 | 真机数据 | 仿真保真度 | 策略鲁棒性 | 适用维度 |
|------|---------|-----------|-----------|----------|
| System ID | 少量 | 高 | 低 | 动力学 |
| DR | 零 | 中 | 高 | 物理+视觉 |
| Domain Adaptation | 中 | 低 | 中 | 视觉 |
| Progressive NN | 少量 | 中 | 中 | 策略层 |
| R2S2R | 迭代 | 自适应 | 高 | 全局 |

## 2.10 概念边界与符号陷阱

- **三分类按"怎么修"、[[A Survey of Sim-to-Real Methods in RL|A Survey]] 按"修什么"（MDP 四元素）**——两个正交分类轴（见 §4 前元综合）。
- **$\Delta P$ TV 距离是 gap 数学本质**；DR 有效性依赖覆盖假设 $P_{real}\in\text{support}(\rho)$。
- **模型优化精度有上限**：接触/摩擦突变难精确建模。
- **DR 过宽 → 策略保守**："对所有天气训练 → 任何天气下都不最优"。
- **执行器/通信延迟是最被低估的 gap 源**：USB 30ms、以太网 1ms。
- **本 review 侧重 locomotion**，灵巧操作（高维力接触）覆盖少 → 灵巧操作 sim-to-real 应参考 A Survey 的 MDP 四元素。

## 3. 核心洞见 (Insights)

1. **System ID 与 DR 互补**: 前者提升仿真保真度，后者提升策略鲁棒性 → 与 [[ReinforcementLearning|RL §5.0]] 的"正交关系"分析一致
2. **执行器建模被低估**: 大多数 sim-to-real 工作忽视电机/驱动器级别建模 → 与 [[ControlTheory|ControlTheory sim-to-real]] 中的硬件 Gap 分析呼应
3. **统一框架思维**: 从信息流角度审视迁移方法，有助于识别方法组合策略

> [!note] 领域级元综合：两个 sim-to-real 综述的正交分类轴 → 2D 全景地图
> 知识库现有两篇 sim-to-real 综述，分类轴**正交**，组合成一张 2D 地图：
> - **本 review（信息流/作用对象）= "怎么修"**：① 模型优化（让仿真像真实，System ID）② 知识迁移（让策略鲁棒，DR/DA）③ 迭代精炼（sim-real 交替，R2S2R）。
> - **[[A Survey of Sim-to-Real Methods in RL|A Survey]]（MDP 四元素）= "修什么"**：$\Delta_S/\Delta_A/\Delta_T/\Delta_R$。
>
> **2D 分类网格**：每个方法定位到"（修什么）×（怎么修）"——[[Grounded Action Transformation|GAT]] =（$\Delta_T,\Delta_A$）×（知识迁移/grounding）；[[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]] =（$\Delta_S$ 几何）×（迭代精炼）；[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]] =（$\Delta_T$ 关节级）×（模型优化）。
> **新 insight**：本 review 三分类正好印证 [[RialTo - Reconciling Reality through Simulation - A Real-to-Sim-to-Real Approach for Robust Manipulation|RialTo]] 提的"修正固定仿真 gap vs 重建仿真逼近真实"两层面——"模型优化"=重建逼近、"知识迁移"=修正固定、"迭代精炼"=二者闭环。**两综述 + 层面 insight 收敛到同一张 sim-to-real 全景图**。分工：本 review 侧重 locomotion 的系统性分类，A Survey 侧重灵巧操作的 MDP 精细定位——互补覆盖。

## 4. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- 为 §5 Sim-to-Real 提供了系统性的分类视角
- 补充了 Progressive Neural Networks、Multi-Fidelity 等未被充分覆盖的方法

### 与 [[Dynamics]] 的联系
- System ID 和执行器建模直接关联 [[Dynamics|动力学迁移]]
- 仿真器物理保真度是所有方法的底层依赖

### 与 [[EmbodiedAI]] 的联系
- 基准平台综述: Real Robot Challenge, HomeRobot/OVMM, NAO testbed
- 与社区走向标准化评估的趋势一致

## 5. 局限性深度分析

### 理论层面
- 缺乏 sim-to-real gap 的**量化度量**——何时 DR 范围足够？何时需更高保真仿真？目前无理论边界
- 未讨论 **domain generalization** 理论对 sim-to-real 泛化的形式化约束

### 算法层面
- 方法分类清晰但**组合策略讨论不足**——实际工程中几乎都是多方法混用
- 对 **AutoDR / BayesSim** 等自动化 DR 参数搜索覆盖偏浅
- 忽略 **diffusion policy** 等生成式策略对 sim-to-real 的新范式影响

### 工程层面
- 对通信延迟、执行器非线性等**底层 Gap 源**分析缺位
- 对灵巧操作（高维力接触）覆盖远少于 locomotion/navigation

### 替代/补充参考
- 灵巧操作 sim-to-real: [[A Survey of Sim-to-Real Methods in RL]] 的 MDP 四元素框架更适用
- VLA 范式: [[EmbodiedAI]] 中 RT-2/OpenVLA 对 sim-to-real 的颠覆性变革
- 接触动力学精度: [[Dynamics]] §5 "Contact Dynamics" 的讨论

## 5.1 与 Foundation 的数学联系

**与 [[ReinforcementLearning]] — MDP 形式化**:

Sim-to-real gap 的数学本质是源域/目标域转移概率差异：
$$\Delta P = \|P_{\text{sim}}(s'|s,a) - P_{\text{real}}(s'|s,a)\|_{\text{TV}}$$
DR 通过在 $P_{\text{sim}}$ 参数空间的分布 $\rho(\xi)$ 上训练来覆盖 $P_{\text{real}}$，有效性依赖 $P_{\text{real}} \in \text{support}(\rho)$。

**与 [[Dynamics]] — 动力学误差传播**:

仿真器离散化误差通过时间步累积：
$$\|x_T^{\text{sim}} - x_T^{\text{real}}\| \leq \sum_{t=0}^{T-1} L_f^{T-1-t} \cdot \epsilon_t$$
其中 $L_f$ 是动力学 Lipschitz 常数。高速接触场景（如转笔）中 $L_f \gg 1$，误差指数放大。

**与 [[Optimization]] — DR 作为鲁棒优化**:
$$\max_\theta \mathbb{E}_{\xi \sim \rho} \left[ J(\pi_\theta, \mathcal{M}_\xi) \right] \approx \max_\theta \min_{\xi \in \Xi} J(\pi_\theta, \mathcal{M}_\xi)$$

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **Sim-to-Real 分类学习**: 本综述对 DR/DA/Transfer Learning 的分类框架可为转笔项目的 sim-to-real 方案选型提供系统性参考
2. **Gap 分析思维**: 将 sim-to-real gap 分解为力学/视觉/触觉/执行器多个维度，逐一定位和解决，而非笼统地“加域随机化”
3. **补充参考**: 本综述侧重 locomotion，灵巧操作特定的 sim-to-real 应参考 [[A Survey of Sim-to-Real Methods in RL|AwesomeSim2Real]] 综述中的 MDP 四元素框架
