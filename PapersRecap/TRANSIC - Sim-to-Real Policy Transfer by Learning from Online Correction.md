---
tags:
  - paper
  - sim-to-real
  - human-in-the-loop
  - residual-learning
  - manipulation
aliases:
  - TRANSIC
paper-year: 2024
read-date: 2026-02-01
venue: CoRL 2024
paper-pdf: "[[Papers/TRANSIC Sim-to-Real Policy Transfer by Learning from Online Correction.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
  - "[[ComputationalGeometry]]"
  - "[[RepresentationLearning]]"
---

# TRANSIC: Sim-to-Real Policy Transfer by Learning from Online Correction

> [!abstract] 核心概要
> 提出一种人在回路的 sim-to-real 迁移方法：人类观察并在线校正仿真策略的失误，收集校正数据训练残差策略，从而 holistically 解决各种 sim-to-real gap。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#9.3 真机高效 RL：把"模仿×强化"缝合线收口|RL §9.3]] - 从人类在线校正学 residual，是"模仿×强化"缝合线在真机侧的一种收口：base=仿真 RL、残差=人类校正 BC。
> - [[ControlTheory]] - 残差策略补偿未建模动态
> - [[Actuation#9. 迁移层 I：执行器 Sim-to-Real gap 的完整解剖|Actuation §9]] - Action Space Distillation（OSC→关节 PD）显式修控制器 gap：OSC 依赖精确 $\Lambda,\mu,p$、真机不可得，蒸馏成模型无关关节 PD——挂 **电流≠关节力矩** 暗线，控制器/执行器接口本身就是 $\Delta_A$ 的一大来源。
> - [[RepresentationLearning]] - 点云作为视觉输入减小感知 gap
>
> **核心技术**: Residual Policy, Online Human Correction, Action Space Distillation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
让人类在线监督和校正机器人执行，从人类校正数据中学习残差策略，以数据驱动方式整体性解决各类 sim-to-real gap。

### 直观隐喻
就像驾校教练坐在副驾——当学员（仿真策略）要出错时，教练会接管方向盘纠正。通过记录这些"接管"数据，学员能学会自己避免同样的错误。

### 领域定位
```
传统 Sim-to-Real:
├── System Identification: 需要领域知识
├── Domain Randomization: 盲目覆盖
└── Real-World Adaptation: 需要精确建模

TRANSIC:
└── Human-in-the-Loop + Residual Learning: 领域无关的整体性解决
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | TRANSIC 突破 |
|---------|------|-------------|
| Domain Randomization | 需要知道什么需要随机化 | 人类隐式识别 gap |
| System Identification | 需要精确建模 | 数据驱动 |
| 直接微调 | 灾难性遗忘 | 残差策略保留基策略 |
| 从头 IL | 需要大量真实数据 | 利用仿真策略 |

### 关键贡献点
1. **Action Space Distillation**: 先用 OSC 训练 teacher，再蒸馏到关节空间 student
2. **Residual Policy from Correction**: 从人类校正数据学习残差动作 $a^R = q^{post} \ominus q^{pre}$
3. **Gated Residual**: 学习门控函数决定何时应用残差

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.0 变量来源追踪

枢纽：**人类隐式识别 gap**（不需知道 gap 是什么，只需能纠正），残差 $a^R=q^{post}\ominus q^{pre}$ + 门控 $g$ 决定何时叠加。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $\pi^B$ / $a^B$ | 策略/动作 | 仿真 RL → BC 蒸馏 | 否（冻结） | 基策略/基动作 | 残差保留它、不重训 |
| $\mathbb{1}^H_t$ | $\{0,1\}$ | 人类决定 | 否 | 干预标志 | 门控 $g$ 的监督信号 |
| $q^{pre},q^{post}$ | 关节状态 | 人类遥操作记录 | 否 | 干预前/后状态 | SpaceMouse 精度限制校正质量 |
| $a^R=q^{post}\ominus q^{pre}$ | 残差 | 计算 | 否（监督目标） | 残差动作 | 连续=数值差、离散(gripper)=异或 |
| $\pi^R_\psi$ | NN | 学习（人类校正数据） | 是 | 残差策略 | 非马尔可夫校正 → MLP 建模有限 |
| $g_\psi$ | $[0,1]$ | 学习（门控头） | 是 | 何时叠残差 | always-residual 在基策略已好区引噪声 |
| 点云 $P$ | $\mathbb{R}^{1024\times3}$ | 观测 | 经编码器带梯度 | 视觉输入 | 比 RGB 跨域鲁棒（§4 消融） |

### 3.1 整体框架

```
Phase 1: Simulation Training
├── Teacher Policy: RL with OSC (操作空间控制)
└── Student Policy: BC from teacher (关节位置控制)
                    ↓
Phase 2: Human-in-the-Loop Data Collection
├── Deploy base policy π^B
├── Human monitors and intervenes when needed
└── Collect correction dataset D^H
                    ↓
Phase 3: Residual Policy Learning
├── Train π^R from D^H
└── Integrate: π^deployed = π^B ⊕ 𝟙_g π^R
```

### 3.2 为什么需要 Action Space Distillation

> [!important] 控制器 gap 是核心问题
> OSC (Operational Space Control) 需要精确的机器人参数（摩擦、质量、惯量），在真实机器人上难以实现。

$$
\text{Teacher: } a^{\text{OSC}} \xrightarrow{\text{Relabel}} a^{\text{joint}} \xrightarrow{\text{BC}} \text{Student}
$$

**训练目标**:
$$
\mathcal{L}^{\text{student}} = -\mathbb{E}_{\mathcal{D}^{\text{teacher}}}[\log \pi_\theta^{\text{student}}] + \beta \mathbb{E}_{\mathcal{D}^{\text{pcd}}}[\|\phi(P^{\text{real}}) - \phi(P^{\text{sim}})\|^2]
$$

第二项是点云编码器的对齐正则化。

### 3.3 人类校正数据收集

**协议**:
```
at each timestep t:
    a_t^B ~ π^B  # base policy action
    execute a_t^B
    
    if human_decides_to_intervene:
        1^H_t = 1
        human takes control via teleoperation
        record (q^{pre}_t, q^{post}_t)  # 干预前后状态
    else:
        1^H_t = 0
    
    D^H ← D^H ∪ {(1^H_t, q^{pre}_t, q^{post}_t)}
```

### 3.4 残差策略学习

**为什么用残差而不是直接微调？**
- 人类校正通常是非马尔可夫的（依赖历史）
- 直接微调会导致大幅动作变化和模型崩溃
- 残差是小的补偿，更稳定

**残差动作定义**:
$$
a^R = q^{post} \ominus q^{pre}
$$

- 连续变量: 数值差
- 离散变量（如 gripper）: 异或

**训练目标**:
$$
\mathcal{L}^{\text{residual}} = -\mathbb{E}_{\mathcal{D}^H}[\log \pi_\psi^R(a^R | \cdot)]
$$

### 3.5 Gated Residual Policy

```python
# 推理时
if g_ψ(observation) > threshold:  # 门控函数
    a_deployed = a_B + a_R  # 应用残差
else:
    a_deployed = a_B  # 仅基策略
```

门控函数与残差策略共享编码器，通过分类损失联合训练。

### 3.5.1 核心 PyTorch 实现逻辑

```python
# Gated Residual Policy 核心
class GatedResidualPolicy(nn.Module):
    def __init__(self, obs_dim, act_dim):
        super().__init__()
        self.encoder = PointNetEncoder(obs_dim)  # 共享编码器
        self.residual_head = nn.Sequential(
            nn.Linear(256, 128), nn.ReLU(), nn.Linear(128, act_dim)
        )
        self.gate_head = nn.Sequential(
            nn.Linear(256, 64), nn.ReLU(), nn.Linear(64, 1), nn.Sigmoid()
        )

    def forward(self, obs):
        z = self.encoder(obs)                    # 共享特征
        a_residual = self.residual_head(z)       # 残差动作
        gate = self.gate_head(z)                 # 门控 ∈ [0,1]
        return a_residual, gate

# 推理: 部署策略
a_base = base_policy(obs)                        # 仿真训练的基策略
a_res, gate = gated_residual_policy(obs)
a_deployed = a_base + gate * a_res               # 门控残差叠加

# 训练损失 (人类校正数据)
target_residual = q_post - q_pre                 # 校正后 - 校正前
loss_res = -log_prob(a_res, target_residual)     # BC 残差
loss_gate = F.binary_cross_entropy(gate, is_intervention)
loss = loss_res + lambda_gate * loss_gate
```

### 3.6 任务分解

四个基础技能组成家具组装:
1. **Stabilize**: 稳定桌腿
2. **Reach and Grasp**: 到达并抓取
3. **Insert**: 插入对齐
4. **Screw**: 旋转拧紧

### 3.7 概念边界与符号陷阱

- **残差 $a^R$ 类型混合**：连续变量数值差、离散（gripper）异或——非单一类型。
- **门控 $g$ 决定何时叠残差**：always-residual 在基策略已好区引噪声（§4 消融 −15%）。
- **Action Space Distillation（OSC→关节）**：OSC 模型依赖（需 $\Lambda,\mu,p$），真机用模型无关关节 PD——去掉则真机完全失败（§4 消融）。
- **人类隐式识别 gap**：领域无关（不需知 gap 是什么），但需人在环（一次性收集后离线）。
- **残差 > 微调**：微调灾难遗忘 + 过拟合少量校正数据。
- **非马尔可夫校正**：人类纠正依赖历史，MLP 残差建模能力有限（§5 算法局限）。

## 4. 实验与验证 (Experiments)

### 实验设置
- **仿真**: Isaac Gym
- **任务**: FurnitureBench 家具组装（高精度接触丰富）
- **人类数据**: SpaceMouse 遥操作

### 关键对比

| 方法 | Stabilize | Insert | Screw | 数据需求 |
|-----|-----------|--------|-------|---------|
| Domain Randomization | 低 | 低 | 低 | 0 真实 |
| BC (从头) | 中 | 中 | 中 | 大量真实 |
| **TRANSIC** | **高** | **高** | **高** | **少量校正** |

### Scaling 特性

> [!note] 人类努力的扩展性
> TRANSIC 性能随人类干预数据量单调提升，表现出良好的数据效率。

### 4.1 训练超参数

| 参数 | 值 |
|------|-----|
| RL 算法 (Teacher) | PPO |
| 蒸馏方式 | Behavioral Cloning (OSC→Joint relabeling) |
| 观测模态 | 本体感知 + 点云 (1024 pts) |
| 人类校正设备 | SpaceMouse 遥操作 |
| 校正数据量 | ~50 episodes / skill |
| 残差策略训练 | BC, Adam lr=3e-4, batch=256 |
| 门控阈值 | 0.5 (推理时) |

### 4.2 Ablation 因果链分析

| 去掉/改变 | 结果变化 | 因果机制 |
|-----------|---------|----------|
| 去掉 Gated → Always Residual | 成功率下降 ~15% | 无干预状态叠加残差引入噪声，基策略已足够好的区域被破坏 |
| 去掉 Action Space Distillation (直接用 OSC) | 真机完全失败 | OSC 需精确动力学参数，仿真-真机参数差异导致控制器崩溃 |
| 减少校正数据 (50→10 episodes) | 成功率下降 ~30% | 残差策略欠拟合，未覆盖足够多的失败模式 |
| 用 RGB 替代点云 | 成功率显著下降 | RGB 的 sim-to-real 视觉 gap 更大，点云几何结构跨域鲁棒 |
| 直接微调 (替代残差) | 快速崩溃 | 灾难性遗忘 + 少量校正数据上过拟合 |

### 4.3 工程关键细节 (Engineering Tricks)

1. **OSC→Joint Relabeling**: 蒸馏时不是 action imitation，而是记录 OSC 执行后的关节角变化作为 Joint space target
2. **点云对齐正则化**: $\|\phi(P^{\text{real}}) - \phi(P^{\text{sim}})\|^2$ 使用仿真渲染点云进行预训练对齐
3. **校正数据增强**: 对人类校正轨迹施加小扰动生成近邻样本，提升数据效率
4. **门控训练平衡**: 门控损失权重 $\lambda$ 需仔细调节——过高导致门控过于保守，过低导致过于激进（始终叠加残差）

## 5. 批判性分析 (Critical Analysis)

### 优势
- **领域无关**: 不需要知道具体 gap 是什么
- **数据高效**: 比从头 IL 需要更少真实数据
- **保留仿真策略优势**: 残差学习不破坏已学知识
- **整体性**: 同时解决感知、控制、动力学多种 gap

### 局限性
- 需要人类在线参与（虽然数据量较少）
- 门控函数可能学得不够精确
- 高精度任务（如 Screw）仍需较多校正

#### 理论/算法/工程 三维度局限性分析

| 维度 | 局限性 | 替代方案 |
|-----|--------|----------|
| **理论** | 残差假设 gap 可被小幅补偿表达，大 gap 场景可能需重新训练 | Distributionally Robust RL ([[ReinforcementLearning]]) |
| **算法** | 门控二分类过于粗糙，连续置信度更优；非马尔可夫校正难以用 MLP 建模 | 基于 Transformer 的序列残差预测 |
| **工程** | 人类必须在线参与，SpaceMouse 精度限制了校正质量 | HIL-SERL 在线 RL；或 VR 遥操作提升精度 |

### 未来方向
- 自动检测需要干预的状态
- 主动学习选择最有价值的校正
- 多任务残差策略共享

## 6. 对灵巧操作的启发 (Implications)

1. **Action Space 选择**: OSC 易于学习但难迁移，关节空间蒸馏是折中方案
2. **残差 > 微调**: 对于分布外数据，残差学习更稳定
3. **人类知识的隐式传递**: 人类无需明确知道 gap 是什么，只需能纠正
4. **点云视觉**: 相比 RGB，点云在 sim-to-real 中更鲁棒

### 6.5 与知识体系的数学联系

#### 与 [[ReinforcementLearning]] 的联系
残差策略可形式化为值函数分解：
$$Q^{\pi_{deployed}}(s,a) = Q^{\pi_B}(s,a_B) + \mathbb{1}_g \cdot Q^{\pi_R}(s, a_R)$$
门控函数 $g$ 的最优策略等价于 advantage function 的符号：当 $A^{\pi_R}(s) > 0$ 时开启残差。

#### 与 [[ControlTheory]] 的联系
Action Space Distillation 实质是控制空间变换：
$$\underbrace{\tau = \Lambda(q)\ddot{x}_d + \mu(q,\dot{q}) + p(q)}_{\text{OSC (需精确 } \Lambda, \mu, p\text{)}} \xrightarrow{\text{Relabel}} \underbrace{q_{target} = q + \Delta q}_{\text{PD (只需 } K_p, K_d\text{)}}$$
将模型依赖的 OSC 蒸馏为模型无关的关节位置控制——[[ControlTheory]] 中鲁棒控制与最优控制的经典权衡。

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── HIL-SERL (2024): 人在回路 RL
├── RialTo (2024): Real-to-Sim-to-Real
└── 残差学习: Residual DMP, Residual RL

本论文: TRANSIC
├── Action Space Distillation (OSC → Joint)
├── Residual from Human Correction
└── Gated Deployment

后续影响:
├── 自动干预检测
├── 主动人类反馈请求
└── 通用 sim-to-real 框架
```

## 8. 与 HIL-SERL 的对比

| 方面 | HIL-SERL | TRANSIC |
|-----|----------|---------|
| 基策略来源 | 真实世界 BC | 仿真 RL |
| 人类角色 | 在线 RL 反馈 | 校正数据收集 |
| 核心思想 | 人类引导 RL 探索 | 人类校正学残差 |
| 数据需求 | 持续在线参与 | 一次性收集后离线 |
| 适用场景 | 真实世界策略改进 | Sim-to-Real 迁移 |

### 8.1 广义跨方法对比

| 方面 | TRANSIC | HIL-SERL | Domain Randomization | System ID | GARAT (Grounding) |
|-----|---------|----------|---------------------|-----------|-------------------|
| 人类参与 | 一次性校正 | 持续在线 RL | 无 | 领域专家设计 | 少量真机数据 |
| 核心策略 | 残差补偿 | 在线微调 | 鲁棒策略 | 精确仿真 | 动作映射修正 |
| 数据需求 | 少量校正 | 持续交互 | 0 真实 | 测量数据 | 配对轨迹 |
| Gap 覆盖 | 全部 (隐式) | 全部 (隐式) | 主要 $\Delta_T$ | $\Delta_T$ | $\Delta_T$ |
| 可扩展性 | 中 (需人类) | 低 (持续人类) | 高 | 低 (需重新标定) | 中 |

> [!note] sim-to-real 簇定位：gap 处理的"分解 vs holistic"维度
> TRANSIC 在 [[A Survey of Sim-to-Real Methods in RL|Survey]] 框架里独特——它**不按 MDP 四元素分解 gap**，而靠**人类 holistic 纠正**所有 gap 的综合表现（§8.1 标注"Gap 覆盖：全部（隐式）"）。这揭示一个正交维度——**gap 处理粒度**：
>
> | 方式 | 做法 | 代表 | 权衡 |
> |------|------|------|------|
> | 显式分解 | 定位并修正特定 $\Delta$ | A Survey 四元素 / [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]](关节) / [[Grounded Action Transformation\|GAT]](动作) | 需领域知识，可针对性优化 |
> | **隐式 holistic** | 不分解，人类一次纠正所有 | **TRANSIC** / HIL-SERL | 领域无关，但需人在环 |
>
> **两个 insight**：① **残差 > 微调**——残差小补偿稳定、微调灾难遗忘；与 [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model|DexNDM]] 的残差策略、[[Grounded Action Transformation|GAT]] 的残差动作 $a+f_\theta$ 同源——**sim-to-real 普遍偏好"基策略+残差"而非重训**。② **Action Space Distillation = 控制器层面的 $\Delta_A$ 修正**：OSC（模型依赖 $\Lambda,\mu,p$）→ 关节 PD（模型无关），把被 A Survey $\Delta_A$ 含括却少被单列的"控制器 gap"显式解决。

## 9. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **Residual 校正架构**: 转笔策略的 Sim-to-Real 迁移可采用 TRANSIC 的思路——仿真中 PPO 训练基策略，真机上收集少量校正数据学习残差补偿
2. **校正数据采集**: 转笔失败时人工接管的「救场轨迹」就是极好的校正数据，可学习 mid-trajectory recovery 策略
3. **可量化检查的迁移**: TRANSIC 的「迁移检查的检查清单」思想可用于转笔——分离各类 sim-to-real gap（操作器动力学/触觉模态/物体属性）并逐一校正
