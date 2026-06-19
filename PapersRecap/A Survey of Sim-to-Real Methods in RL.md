---
tags:
  - paper
  - sim-to-real
  - reinforcement-learning
  - survey
aliases:
  - Sim2Real Survey
  - AwesomeSim2Real
paper-year: 2025
read-date: 2026-03-05
venue: arXiv (2502.13187)
paper-pdf: "[[Papers/A Survey of Sim-to-Real Methods in RL- Progress, Prospects and Challenges with Foundation Models.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[EmbodiedAI]]"
---

# A Survey of Sim-to-Real Methods in RL: Progress, Prospects and Challenges with Foundation Models

> [!abstract] 核心贡献
> 首个以 **MDP 四元素 (S, A, T, R)** 为分类框架的 Sim-to-Real 综述，系统梳理了从经典方法到 Foundation Model 增强策略的全谱系技术。提供 GitHub 资源库持续更新: [AwesomeSim2Real](https://github.com/LongchaoDa/AwesomeSim2Real)

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — MDP $(S,A,T,R)$ 形式化是本综述分类轴；DR / robust-MDP 理论
> - [[Dynamics]] — Transition Gap $\Delta_T$ 的本质（仿真 vs 真实接触动力学）
> - [[ControlTheory]] — Action Delay $\Delta_A$ 与控制频率 / 执行延迟
> - [[Optimization]] — Distributionally Robust RL 的 minimax + $f$-散度不确定集
> - [[EmbodiedAI]] — Foundation Model (VLM/LLM) 作为 sim-to-real 跨域语义锚点
>
> **核心技术**: MDP 四元素 Gap 分解, Domain Randomization / ADR, Grounding (GAT→GARAT), Domain Adaptation, FM 增强

## 1. 问题设定与动机

**Sim-to-Real Gap 的形式化定义**:

$$G(\pi) := \psi_s(\pi_{si}) - \psi_r(\pi_{si}) \big|_{\pi_{si} \sim \mathcal{M}_s}$$

其中 $\psi$ 是任意性能指标，$\mathcal{M}_s / \mathcal{M}_r$ 分别为仿真/真实 MDP。

Gap 来源分解为 MDP 四元素差异：
- **$\Delta_S$ (Observation)**: 传感器噪声、部分可观、特征分布不匹配
- **$\Delta_A$ (Action)**: 动作粒度 (离散vs连续)、系统延迟 $\Delta_{system}$
- **$\Delta_T$ (Transition)**: 物理动力学差异 $P_s(s_{t+1}|s_t, a_t) \neq P_r(s_{t+1}|s_t, a_t)$
- **$\Delta_R$ (Reward)**: 奖励函数基于仿真设计，未覆盖真实场景

### 核心直觉隐喻

> 就像在驾校模拟器中学会了开车，但真正上路时发现方向盘手感不同 ($\Delta_A$)、路况与模拟器不同 ($\Delta_T$)、后视镜视角不同 ($\Delta_S$)、交通规则的评判标准也不同 ($\Delta_R$)。Sim-to-Real 研究就是系统性地消除「模拟器驾校」与「真实路况」之间每一维度的差距。

### 1.2 现有综述的局限

此前 Sim-to-Real 综述主要存在三个盲区：
1. **缺乏统一分类框架**：大多数综述按「技术族」（Domain Randomization / Domain Adaptation / System ID）分类，无法揭示各方法解决的是 MDP 哪一维度的差距，导致跨方法对比缺乏共同基准。
2. **忽略 Foundation Model 范式**：2023 年前的综述均未覆盖 LLM/VLM 在 Sim-to-Real 中的角色（语义锚点、奖励自动生成、动作空间推理），而这正是当前最活跃的增长点。
3. **应用领域割裂**：机器人操作、自动驾驶、交通控制、医疗等领域各有独立综述，缺乏统一视角下的跨域特征提炼。

本综述以 MDP 四元素 $(S, A, T, R)$ 为轴，首次在统一框架下覆盖经典方法与 Foundation Model 增强策略，并横跨多个应用领域。

### 1.3 核心符号与 Gap 溯源

综述的"变量来源追踪"= 把 Gap 形式化的每个符号溯清。枢纽：**$G(\pi)$ 按 MDP 四元素正交分解为 $\Delta_S/\Delta_A/\Delta_T/\Delta_R$**——这是全文分类轴。

| 符号/概念 | 类型 | 来源 | 意义 | 陷阱 |
|------|------|------|------|------|
| $G(\pi)=\psi_s-\psi_r$ | scalar | 定义 | sim-to-real gap（性能差） | 依赖性能指标 $\psi$ 选择 |
| $\mathcal{M}_s,\mathcal{M}_r$ | MDP | 仿真/真实 | 两个 MDP | gap 是其差异 |
| $\Delta_S$ | gap 分量 | 观测 | 传感器噪声/部分可观/分布不匹配 | 视觉/触觉模态差异 |
| $\Delta_A$ | gap 分量 | 动作 | 粒度 + 延迟 $\Delta_{system}$ | **硬件延迟=强制 persistence**（连 control frequency 簇）|
| $\Delta_T$ | gap 分量 | 转移 | $P_s\neq P_r$ 动力学差 | **最核心**；接触动力学主导 |
| $\Delta_R$ | gap 分量 | 奖励 | 仿真奖励未覆盖真实 | 真机不可直接测 |
| $\xi$ | 物理参数 | DR 随机化 | 摩擦/质量/延迟等 | ADR 自适应优先采最难配置 |
| $\mathcal{U}(P_s)$ | 不确定集 | robust RL | $\{P:D_f(P\|P_s)\le\epsilon\}$ | minimax 以 $P_s$ 为中心 |

### 1.4 概念边界与符号陷阱

- **四元素分解假设各 Gap 可独立处理**：实际 $\Delta_S$-$\Delta_T$ 耦合（§6 局限）。
- **$\Delta_T$ 最核心**：接触动力学（摩擦/碰撞/滑移）主导机器人 sim-to-real。
- **同一技术跨多维**：对抗训练在 $\Delta_S$（视觉对齐）与 $\Delta_T$（动力学对齐）都出现——按"解决哪维 Gap"分类才能看清其多面性。
- **Grounding 需 sim/real 态-动作严格时间对齐**：否则学到带相位延迟的动作映射。
- **DR vs SysID 的权衡**：DR 真实数据需求=0 但精度上限中（盲目覆盖）；SysID 精度高但需重标定、低可扩展。
- **硬件 Gap 被综述忽略**：电机/减速器/传动非理想（齿隙、非线性摩擦、电气延迟）在 $\Delta_T$ 中占重要角色（连 [[sim2real]]）。

## 2. 核心方法/理论

### 2.0 Delta 分析：本综述的增量贡献

与此前综述（Tobin et al. 2017 DR 专项综述、Zhao et al. 2020 迁移学习综述）相比，本文的核心增量：
- **分类维度升级**：从「技术族」→「MDP 元素」，使得同一技术（如对抗训练）在 $\Delta_S$ (视觉对齐) 和 $\Delta_T$ (动力学对齐) 中分别出现，揭示其多面性
- **Foundation Model 系统整合**：在每个 Gap 维度下都分析了 LLM/VLM 的切入点，形成「经典方法 + FM 增强」的双轨结构
- **开放资源库**：维护 [AwesomeSim2Real](https://github.com/LongchaoDa/AwesomeSim2Real) 持续更新

### 2.1 Observation Gap 解决方案

| 方法类别 | 核心思路 | 代表工作 |
|---------|---------|---------|
| **Domain Randomization** | 随机化视觉参数（纹理/光照/相机），训练鲁棒策略 | ADR (课程化随机化) |
| **Domain Adaptation** | 对齐仿真/真实特征分布（对抗训练、嵌入对齐） | Bi-directional DA, VR-Goggles |
| **Sensor Fusion** | 多传感器融合（视觉+深度+LiDAR）补偿单模态局限 | 多传感器GPS+惯性 |
| **Foundation Models** | VLM 提供语义锚点，作为跨域不变特征 | 语义描述作为统一信号 |

### 2.2 Action Gap 解决方案

| 方法类别 | 核心思路 |
|---------|---------|
| **Action Space Scale** | 子目标模型弥合离散→连续间隙，层次化动作空间 |
| **Action Delay** | 多步预测、延迟感知 MDP、帧跳过策略 |
| **Action Uncertainty** | 动作噪声建模、概率动作空间 |
| **Foundation Models** | LLM 推理动作语义，辅助动作空间设计 |

### 2.3 Transition Gap 解决方案（最核心）

| 方法类别 | 核心思路 | 关键方法 |
|---------|---------|---------|
| **Domain Randomization** | 随机化物理参数（摩擦、力矩等） | 主动域随机化 (ADR) — 优先训练最困难配置 |
| **Domain Adaptation** | 对齐仿真/真实动力学分布 | 对抗训练最小化转移动力学差异 |
| **Grounding Methods** | 用真实数据修正仿真器动作映射 | GAT → SGAT → RGAT → GARAT 演进 |
| **Distributionally Robust RL** | 设计对转移偏移鲁棒的策略 | Off-dynamics RL, 线性 f-散度正则化 |
| **LLM-Enhanced** | LLM 改善正向模型的真实动力学预测 | LLM-informed inverse model |

> [!tip] Grounding Methods 演进脉络
> **GAT** (AAAI 2017, 确定性动作变换)
> → **SGAT** (引入随机性，概率化 next-state 建模)
> → **RGAT** (用 RL 直接学习 grounding 作为端到端问题)
> → **GARAT** (生成对抗方法，IfO 框架)
>
> 这条线与 [[sim2real]] 中讨论的硬件建模 Gap 互补——Grounding 修正软件模型，硬件分析修正物理参数范围。

#### 核心概念代码: Domain Randomization + Grounding

```python
# Domain Randomization: 训练时随机化物理参数
for epoch in range(n_epochs):
    # 采样随机物理参数 ξ ~ P(ξ)
    friction = uniform(0.3, 1.5)
    mass_scale = uniform(0.8, 1.2)
    latency = uniform(0, 2) * dt              # 动作延迟
    sim.set_physics_params(friction, mass_scale, latency)

    # ADR: 优先训练当前最困难的参数配置
    rollout = collect_rollout(policy, sim)
    if rollout.reward < threshold:
        hard_params.add((friction, mass_scale, latency))
    policy.update(rollout)                     # PPO/SAC 更新

# Grounding (GAT): 学习动作变换 f: a_sim → a_real
grounding_net = ActionTransformer(a_dim)
for s, a_sim, s_next_real in real_paired_data:
    a_grounded = grounding_net(s, a_sim)
    s_next_sim = sim.step(s, a_grounded)
    loss = F.mse_loss(s_next_sim, s_next_real)  # 对齐转移动力学
    grounding_net.update(loss)
```

### 2.4 Reward Gap 解决方案

- **Reward Shaping**: 人工设计或辅助奖励信号引导仿真外行为
- **LLM-Based Reward Design**: [[EUREKA: Human-Level Reward Design via Coding Large Language Models|EUREKA]] 式 LLM 自动生成奖励函数

## 3. 关键实验发现（跨论文汇总）

本文为综述性论文，不含新实验，但系统汇总了各方法在代表性任务上的核心数字：

### 3.1 Domain Randomization 关键结果
| 代表工作 | 任务 | 核心数字 |
|---------|------|----------|
| OpenAI Rubik's Cube (2019) | ShadowHand 魔方旋转 | DR + ADR 在真机 50 次测试成功率 ~60%；无 DR 的策略 0% 迁移 |
| Tobin et al. (2017) | 抓取任务视觉迁移 | 仿真训练 + 视觉随机化 → 真机 80%+ 成功率，无需真实图像 |
| ADR (Mehta et al. 2020) | Hopper/Walker locomotion | ADR 比均匀 DR 收敛速度提升 3-5 倍，且最终策略鲁棒性更高 |

### 3.2 Grounding / System ID 关键结果
| 代表工作 | 任务 | 核心数字 |
|---------|------|----------|
| GAT (Hanna & Stone 2017) | Cart-pole, Mountain Car | 动作变换后仿真策略在真机性能恢复 85-95%（vs 无 grounding 40-60%） |
| GARAT (Desai et al. 2020) | MuJoCo locomotion | 对抗 grounding 在 HalfCheetah/Ant 上超越 GAT 15-20% 性能 |
| SysID (Tan et al. 2018) | Minitaur 四足行走 | 系统辨识后 sim 策略直接部署成功率 > 90% |

### 3.3 Domain Adaptation 关键结果
- GraspGAN (Bousmalis et al. 2018): 仿真→真实图像翻译 + RL → 抓取成功率从 35% 提升至 70%
- RCAN (James et al. 2019): 随机化→标准化图像适配 → 真机操作任务 zero-shot 成功率 ~65%

### 3.4 跨方法因果对比分析

> [!note] 为什么不同任务偏好不同方法？

| 任务特征 | 最优方法族 | 因果解释 |
|---------|-----------|----------|
| 高维视觉输入 + 简单动力学 (抓取) | **DR (视觉随机化)** | $\Delta_S$ 主导，$\Delta_T$ 可忽略 → 扩大视觉鲁棒性即可 |
| 简单观测 + 复杂接触动力学 (灵巧操作) | **Grounding + SysID** | $\Delta_T$ 主导 → 需要精确修正动力学模型 |
| 高维观测 + 复杂动力学 (人形全身) | **DR + Adaptation 组合** | $\Delta_S \times \Delta_T$ 联合主导 → 单一方法不足 |
| 语义级任务 (长视野操作) | **Foundation Model 增强** | 语义理解 ($\Delta_R$) 成为瓶颈 → LLM 奖励设计 |

**因果链**：任务的主导 Gap 维度 → 决定方法族选择 → 方法内的具体变体由计算预算和真实数据可得性决定

## 4. 核心洞见 (Insights)

1. **MDP 分解框架的实用性**: 将 Sim-to-Real Gap 按 S/A/T/R 分解，使研究者可以精确定位问题来源并选择对应方案
2. **Foundation Models 横跨全部四个维度**: LLM/VLM 不仅用于奖励设计，在观测对齐、动作语义、动力学预测中均有潜力
3. **Grounding 与 Randomization 是互补而非竞争关系**: DR 扩大策略鲁棒范围，Grounding 精准修正系统模型
4. **硬件层面的 Gap 未被充分讨论**: 综述主要关注软件策略层面，但电机/减速器/传动的非理想特性（参见 [[sim2real]]）在 Transition Gap 中占重要角色

## 5. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- MDP 形式化定义与 Sim-to-Real Gap 的理论框架直接扩展了 RL 基础
- Domain Randomization 技术归属于 [[ReinforcementLearning]] 的 Sim-to-Real 范畴
- Distributionally Robust RL 与 robust MDP 理论相关

### 与 [[Dynamics]] 的联系
- Transition Gap 的本质是仿真动力学 $P_s$ 与真实动力学 $P_r$ 的差异
- 接触动力学 (摩擦、碰撞) 是机器人 Sim-to-Real 中 Transition Gap 的主要来源

### 与 [[ControlTheory]] 的联系
- Action Delay 分析与控制频率 / 执行延迟密切相关
- 阻抗控制的参数化动作空间可缓解 Action Gap

### 与 [[EmbodiedAI]] 的联系
- Foundation Model 在 Sim-to-Real 中的应用代表了 VLA/VLM 与具身智能的交叉前沿

### 与 [[Optimization]] 的联系
Distributionally Robust RL 的核心是 minimax 优化：
$$\max_\pi \min_{P \in \mathcal{U}(P_s)} \mathbb{E}_{P}\left[\sum_t \gamma^t r_t\right]$$
其中 $\mathcal{U}(P_s) = \{P : D_f(P \| P_s) \leq \epsilon\}$ 是以仿真动力学为中心的 $f$-散度不确定性集。

### 与 [[StochasticProcess]] 的联系
Domain Randomization 本质是在物理参数空间 $\Xi$ 上构造分布，训练对参数分布的期望最优策略：
$$\pi^* = \arg\max_\pi \mathbb{E}_{\xi \sim P(\xi)}[V^\pi(\mathcal{M}_\xi)]$$
ADR 将 $P(\xi)$ 从均匀分布演化为适应性分布，优先采样当前策略表现最差的参数区域。

## 5.1 工程关键细节 (Engineering Tricks)

- **ADR (Active Domain Randomization)**: 不均匀随机化，优先训练「当前最困难的」物理参数配置 → 比均匀 DR 训练效率高 3-5 倍
- **Grounding 方法的时间对齐**: GAT 系列方法要求 sim/real 的 state-action 严格时间对齐，否则学到带相位延迟的动作映射
- **Foundation Model 作为跨域锚点**: VLM 提取的语义特征（如 SigLIP/DINOv2 embeddings）天然跨仿真-真实域不变

## 5.2 与用户研究（灵巧手转笔/Sim-to-Real）的启发

> [!quote] 对 DNPM 项目的直接映射
> 灵巧手转笔的 Sim-to-Real 挑战可按 MDP 四元素精确定位：

| Gap 维度 | 转笔任务中的具体表现 | 推荐方案 |
|---------|-------------------|--------|
| $\Delta_S$ | 触觉传感器（仿真力 vs 真机指腹传感器）的模态差异 | Cross-Modal Alignment (对比学习) |
| $\Delta_A$ | PD 控制器参数 ($K_p$, $K_d$) 在真机上的非线性响应 | 阻抗参数域随机化 + 在线自适应 |
| $\Delta_T$ | 笔与手指间的接触动力学（摩擦系数、滑移阈值）差异 | ADR + System Identification |
| $\Delta_R$ | 仿真中基于精确位姿的奖励在真机中不可直接测量 | 基于视觉/触觉的间接奖励估计 |

**核心 takeaway**: 转笔任务中 $\Delta_T$（接触动力学）是最大瓶颈，Grounding Methods（GAT→GARAT 演进线）是比域随机化更精准的一条路线。

### 5.3 跨方法结构化对比

| 维度 | Domain Randomization | System ID | Domain Adaptation | Grounding (GAT系列) | Foundation Model |
|-----|---------------------|-----------|-------------------|-------------------|-----------------|
| 覆盖 Gap | $\Delta_S, \Delta_T$ | $\Delta_T$ | $\Delta_S$ | $\Delta_T, \Delta_A$ | $\Delta_S, \Delta_R$ |
| 真实数据需求 | 0 | 少量测量 | 配对/非配对样本 | 少量配对轨迹 | 预训练模型 (0-shot) |
| 可扩展性 | 高 (并行仿真) | 低 (需重新标定) | 中 (对抗训练) | 中 | 高 (推理) |
| 精度上限 | 中 (盲目覆盖) | 高 (若模型准确) | 中 | 高 | 取决于基础模型 |
| 计算开销 | 高 (大量仿真) | 低 | 中 | 低 | 高 (推理) |
| 适用场景 | 通用、大规模 | 精确控制 | 视觉迁移 | 动力学修正 | 语义级任务 |

## 6. 局限与未来方向

> [!note] 领域级综述：用 MDP 四元素统一三大簇的 sim-to-real 路线（本篇 = sim-to-real 总纲）
> 本综述的 $(S,A,T,R)$ 框架恰好给已升级三大簇的 sim-to-real 路线一个统一坐标：
>
> | 簇 / 论文 | 主攻 Gap | 路线 |
> |---------|---------|------|
> | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] | $\Delta_T$ | RMA 在线辨识物体参数 |
> | [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch\|Touch Dexterity]] | $\Delta_S$ | 二值化"量化吸收" |
> | [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing\|Robot Synesthesia]] | $\Delta_S$ | 点云几何抽象 |
> | [[Lessons from Learning to Spin Pens\|Spin Pens]] | $\Delta_T$ | Open-loop Replay 离线筛选 |
> | [[Control Frequency Adaptation via Action Persistence in Batch Reinforcement Learning\|PFQI]] / [[TARC - Time-Adaptive Robotic Control\|TARC]] | $\Delta_A$ | 硬件延迟 = 强制 persistence |
>
> **新 insight——in-hand rotation 簇提炼的"找对 gap 不变的观测子空间"meta-insight，正是本综述 $\Delta_S$ 维度的统一解**：Touch Dexterity(二值量化)、Robot Synesthesia(几何点云)、AnyRotate(稠密触觉蒸馏)都在构造对 sim/real 差异不变的观测表示。而 $\Delta_T$ 维度分两路：**在线辨识（HORA RMA）vs 离线筛选（Spin Pens Open-loop）**。MDP 四元素框架把分散在三大簇的 sim-to-real 技巧组织成一张**可检索的地图**——这正是 WMTS 设计 real-robot fine-tuning 阶段的方法选型表（按主导 Gap 维度选路线，见 §3.4 因果对比）。

### 6.1 关键未尽方向

1. **硬件-软件联合建模**: 综述缺乏对执行器物理特性 (电气时间常数、齿隙、非线性摩擦) 的讨论——这正是真机部署的核心gap
2. **多域联合迁移**: 同时处理 Observation + Transition Gap 的联合方法尚不成熟
3. **在线适应与安全**: 部署时在线修正策略的安全保证仍需加强
4. **领域特异性**: 不同应用领域的 Sim-to-Real 挑战差异巨大，通用方案可能不存在

### 理论/算法/工程 三维度局限性分析

| 维度 | 局限性 | 替代方向 |
|-----|--------|----------|
| **理论** | MDP 四元素分解假设各维度 Gap 可独立处理，但实际中 $\Delta_S$-$\Delta_T$ 存在耦合 | 联合域自适应框架 ([[RepresentationLearning]]) |
| **算法** | Grounding 方法假设 sim/real 态-动作配对可获取，接触丰富任务中真机数据采集困难 | 基于视频的 observation-only grounding |
| **工程** | 综述未系统讨论执行器非理想特性（齿隙、摩擦非线性、电气延迟）对 $\Delta_T$ 的贡献 | 硬件-软件联合建模 ([[Dynamics]]) |
