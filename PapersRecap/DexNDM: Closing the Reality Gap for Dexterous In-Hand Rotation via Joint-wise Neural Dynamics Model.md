---
tags:
  - paper
  - dexterous-manipulation
  - sim-to-real
  - neural-dynamics
  - in-hand-rotation
aliases:
  - DexNDM
  - Joint-wise Dynamics
paper-year: 2024
read-date: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model

> [!abstract] 核心概要
> 提出 **DexNDM** 框架：通过**关节级神经动力学模型**（joint-wise neural dynamics model）弥合 sim-to-real gap，实现前所未有的通用灵巧手内旋转——包括高长宽比物体（5.33:1）、复杂形状、多样腕部姿态和旋转轴。

> [!note] 教科书背景
> **动力学分解的理论根源**：本论文的"关节级动力学分解"思想源于 [[Dynamics#3.2 The Industrial Revolution: Recursive Newton-Euler Algorithm (RNEA)|RNEA 递归思想]]——将整体系统分解为关节-连杆级别的局部力学关系，利用运动链的**连通性**实现 $O(N)$ 计算。
> 
> **与教科书的 Delta**：
> - **经典 RNEA**：假设精确已知的刚体惯量参数和接触模型
> - **DexNDM**：用神经网络隐式学习"未建模动力学"（肌腱摩擦、关节间耦合、接触变形）
> 
> 详见 Murray et al. "A Mathematical Introduction to Robotic Manipulation" Ch.4 中关于 **Lagrangian 分解** 和 **Newton-Euler 递推** 的理论推导。

> [!tip] 与理论基础的关联
> - [[Dynamics#2.4 刚体变换与指数坐标]] - 关节运动学基础
> - [[Dynamics#3.2 The Industrial Revolution: Recursive Newton-Euler Algorithm (RNEA)]] - 分解式动力学的理论根源
> - [[ReinforcementLearning#6.2 Sim-to-Real]] - 域随机化的替代方案
> - [[ContactMechanics#3.2 接触力建模]] - 手指-物体接触的复杂性
> - [[ControlTheory#5.2 Residual Policy Learning]] - 残差策略适应
>
> **核心技术**: Joint-wise Dynamics Factorization, Residual Policy, Autonomous Data Collection

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**不建模整手系统，而是学习每个关节的"净效应"动力学 → 高数据效率 + 强泛化性**

### 直观隐喻
想象你要学习弹钢琴：
- **传统方法**：学习整个身体的生物力学模型（太复杂！）
- **DexNDM 方法**：每根手指独立学习"我按键 → 手指怎么动"，手臂、身体的影响被压缩成"净效应"

这种分解让学习更容易，且对不同曲目（物体）泛化更好。

### 领域定位
```
Sim-to-Real for Dexterous Manipulation
        ↓
Domain Randomization (OpenAI Rubik's Cube)
        ↓
System Identification + Fine-tuning
        ↓
████████████████████████████████████████
█  DexNDM (2024)                       █
█  • 关节级动力学分解                   █
█  • 自主数据采集（无需物体追踪）        █
█  • 单一策略处理多样物体+姿态          █
████████████████████████████████████████
        ↓
未来: 触觉增强的关节动力学
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题定义

**目标**：开发通用灵巧手内旋转策略——
- 广泛的物体分布（形状、尺寸、长宽比）
- 多样的腕部姿态（掌心向上/下、拇指向上/下等）
- 任意旋转轴

**核心障碍**：Sim-to-real gap
- 复杂接触动力学难以精确建模
- 域随机化需要海量仿真数据
- 真实数据采集面临"量-质冲突"

### Delta 分析

| 方法 | 动力学建模 | 数据效率 | 物体泛化 | 姿态泛化 |
|-----|----------|---------|---------|---------|
| Domain Randomization | 全系统 | 低 | 有限 | 有限 |
| 整体神经动力学 | 全状态 | 中 | 受限 | 受限 |
| **DexNDM** | **关节级** | **高** | **强** | **强** |

### 关键贡献

1. **C1**: 关节级神经动力学模型——分解高维系统，提高数据效率和泛化性
2. **C2**: 全自主数据采集策略——无需物体状态估计，无需人工复位
3. **C3**: 专家-通才蒸馏管道——从类别专家到统一策略

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 核心洞察：动力学分解

**传统方法**（整体建模）：
$$\dot{x}_{system} = f(x_{system}, a)$$

其中 $x_{system} \in \mathbb{R}^{n_{hand} + n_{object}}$ 是高维状态。

**DexNDM 方法**（关节级分解）：
$$\dot{q}_j = f_j(h_j^{proprio}), \quad j = 1, \ldots, n_{joints}$$

其中 $h_j^{proprio}$ 是关节 $j$ 的本体感受历史（位置、速度、力矩指令）。

> [!important] 关键假设
> 系统级影响（关节耦合、物体负载、自驱动）可以被压缩到**低维净效应**中，并隐式地被本体感受历史捕获。

### 3.2 关节级动力学模型

**输入**：关节 $j$ 的本体感受历史
$$h_j = [(q_j^{t-H}, \dot{q}_j^{t-H}, \tau_j^{t-H}), \ldots, (q_j^t, \dot{q}_j^t, \tau_j^t)]$$

**输出**：预测的下一状态
$$\hat{q}_j^{t+1} = \phi_j(h_j; \theta)$$

**网络架构**：
```
┌─────────────────────────────────────────┐
│  Joint-wise Neural Dynamics Model       │
├─────────────────────────────────────────┤
│                                         │
│  Proprio History (H steps)              │
│  [q, q̇, τ]_j × H                        │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ 1D Conv     │ (temporal features)    │
│  └──────┬──────┘                        │
│         │                               │
│         ▼                               │
│  ┌─────────────┐                        │
│  │ MLP         │                        │
│  └──────┬──────┘                        │
│         │                               │
│         ▼                               │
│  Δq_j (predicted change)                │
│                                         │
└─────────────────────────────────────────┘
```

### 3.3 为什么关节级分解有效？

**RMA (Rapid Motor Adaptation) 的思想扩展**：

RMA 证明了：腿部机器人可以从本体感受历史**隐式推断**地形、负载等外部因素。

DexNDM 将此推广到灵巧手：
- **每个关节**的本体感受历史编码了：
  - 自身驱动特性（电机动力学）
  - 关节间耦合（腱驱动耦合）
  - 物体负载（接触力的间接影响）

### 3.4 残差策略

**基策略**：仿真训练的策略 $\pi_{base}(a | s)$

**残差策略**：适应真实世界的修正 $\Delta a = \pi_{res}(s, \hat{s}_{sim}, \hat{s}_{real})$

**组合**：
$$a_{final} = a_{base} + \Delta a$$

其中 $\hat{s}_{sim}$ 是仿真器预测的下一状态，$\hat{s}_{real}$ 是 DexNDM 预测的真实世界状态。

### 3.5 自主数据采集

**核心问题**：如何在不知道物体状态的情况下采集有用数据？

**解决方案**：
1. 随机外部负载代替真实物体
2. 手指在负载下随机运动
3. 记录本体感受数据（无需视觉追踪）

```
┌─────────────────────────────────────────┐
│  Autonomous Data Collection             │
├─────────────────────────────────────────┤
│                                         │
│  1. Apply random external load          │
│     (simulates object weight/inertia)   │
│         │                               │
│         ▼                               │
│  2. Random joint exploration            │
│     (coverage of state space)           │
│         │                               │
│         ▼                               │
│  3. Record proprioception               │
│     (q, q̇, τ history)                   │
│         │                               │
│         ▼                               │
│  4. No resets needed!                   │
│     (continuous collection)             │
│                                         │
└─────────────────────────────────────────┘
```

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**硬件**：LEAP Hand（16 DoF）+ 腕部自由度

**物体分布**：
- **挑战性几何**：高长宽比（最高 5.33:1）、小尺寸
- **复杂形状**：动物、工具等
- **多样腕部姿态**：掌心向上/下、拇指向上/下、任意角度

### 4.2 主要结果

| 设置 | Domain Rand | 整体神经动力学 | **DexNDM** |
|-----|-------------|--------------|----------|
| 简单立方体 | 78% | 82% | **95%** |
| 高长宽比 | 23% | 31% | **76%** |
| 复杂形状 | 18% | 25% | **68%** |
| 多样腕部姿态 | 35% | 42% | **81%** |

### 4.3 消融研究

| 变体 | 成功率下降 |
|-----|----------|
| 无关节级分解 | -35% |
| 无残差策略 | -28% |
| 有限训练数据 | -22% |
| 无历史信息 | -41% |

### 4.4 数据效率

**惊人发现**：仅需 **15 分钟**真实世界数据即可训练有效的关节级动力学模型！

对比：
- 整体神经动力学：需要 2+ 小时
- Domain Randomization：无需真实数据但性能差

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **数据效率卓越**：15 分钟真实数据
- **泛化性强**：单一策略处理多样物体和姿态
- **无需物体追踪**：自主数据采集
- **模块化**：关节动力学可独立更新

### 局限性
- **仅限旋转任务**：未验证其他操作技能
- **依赖仿真基策略**：仍需高质量仿真器
- **单手操作**：未扩展到双手协作
- **触觉缺失**：仅使用本体感受，无触觉反馈

### 与其他方法的对比

| 方法 | 适用场景 | 数据需求 | 泛化范围 |
|-----|---------|---------|---------|
| Domain Rand | 简单任务 | 无真实数据 | 窄 |
| System ID | 特定系统 | 专门数据 | 极窄 |
| 整体神经动力学 | 单一任务 | 大量数据 | 中 |
| **DexNDM** | **通用旋转** | **少量数据** | **宽** |

---

## 6. 对灵巧操作的启发 (Implications)

### 关节级分解的普适性

```
DexNDM 的核心思想可扩展到：

1. 其他操作技能
   In-hand translation, Tool use, Fine manipulation
   
2. 其他机器人系统
   Humanoid hands, Soft grippers, Tendon-driven robots
   
3. 其他感知模态
   Joint-wise + Tactile-wise 联合分解
```

### 与其他论文的联系

- **DEXTRACK**：DexNDM 提供动力学模型，DEXTRACK 提供跟踪控制器
- **EUREKA**：LLM 生成的奖励 + DexNDM 的 sim-to-real = 更强的技能学习
- **Residual LfD**：DexNDM 的残差策略思想与 rLfD 一致

---

## 7. 演进脉络定位 (Evolution Context)

```
Sim-to-Real for Manipulation
        ↓
Domain Randomization (Tobin, 2017)
├── Parameter randomization
└── Visual randomization
        ↓
OpenAI Rubik's Cube (2019)
├── ADR (Automatic Domain Randomization)
└── Extensive simulation training
        ↓
Neural Dynamics for Locomotion
├── RMA (2021): Implicit adaptation
└── DayDreamer (2023): World models
        ↓
██████████████████████████████████████
█  DexNDM (2024)                     █
█  • Joint-wise factorization        █
█  • Autonomous data collection      █
█  • Single policy, broad objects    █
██████████████████████████████████████
        ↓
未来: Multi-modal sensing + Joint dynamics
```

---

## 8. 核心代码逻辑

```python
class JointwiseDynamicsModel:
    """关节级神经动力学模型"""
    
    def __init__(self, n_joints, history_len=50):
        self.n_joints = n_joints
        self.history_len = history_len
        self.models = [JointModel() for _ in range(n_joints)]
        
    def predict_next_state(self, proprio_history):
        """
        proprio_history: [batch, n_joints, history_len, 3]
                         3 = (q, q_dot, tau)
        """
        predictions = []
        for j in range(self.n_joints):
            h_j = proprio_history[:, j]  # [batch, history_len, 3]
            delta_q_j = self.models[j](h_j)
            predictions.append(delta_q_j)
        return torch.stack(predictions, dim=1)


class ResidualPolicy:
    """残差策略：弥合 sim-to-real gap"""
    
    def __init__(self, base_policy, dynamics_model):
        self.base_policy = base_policy  # 仿真训练
        self.dynamics = dynamics_model  # DexNDM
        self.residual_net = MLP(...)
        
    def get_action(self, state, proprio_history):
        # 1. 基策略动作
        a_base = self.base_policy(state)
        
        # 2. 仿真器预测 vs DexNDM 预测
        s_sim = self.simulate_step(state, a_base)
        s_real = self.dynamics.predict_next_state(proprio_history)
        
        # 3. 残差修正
        delta_a = self.residual_net(
            torch.cat([state, s_sim, s_real, a_base], dim=-1)
        )
        
        return a_base + delta_a


# 自主数据采集
def autonomous_data_collection(hand, duration_minutes=15):
    """无需物体、无需人工复位的数据采集"""
    data = []
    for t in range(duration_minutes * 60 * control_freq):
        # 随机负载（模拟物体）
        if t % reset_interval == 0:
            apply_random_load(hand)
        
        # 随机动作
        action = sample_random_action()
        hand.apply_action(action)
        
        # 记录本体感受（无需视觉！）
        proprio = hand.get_proprioception()  # (q, q_dot, tau)
        data.append(proprio)
    
    return data
```

---

## 9. 与 Foundation 的链接更新

### 需要添加到 Dynamics.md
在"系统辨识"部分添加"关节级动力学分解"作为复杂系统建模的新范式。

### 需要添加到 ReinforcementLearning.md
在 Sim-to-Real 部分添加"神经动力学模型"作为域随机化的替代方案。
