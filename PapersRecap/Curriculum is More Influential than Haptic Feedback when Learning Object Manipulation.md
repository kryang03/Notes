---
tags:
  - paper
  - curriculum-learning
  - dexterous-manipulation
  - tactile-sensing
  - in-hand-manipulation
aliases:
  - Curriculum > Haptic
  - Curriculum vs Haptic
paper-year: 2025
read-date: 2026-03-16
venue: Science Advances
paper-pdf: "[[Papers/Curriculum is more influential than haptic feedbackwhen learning object manipulation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[SignalProcessing]]"
---

# Curriculum is More Influential than Haptic Feedback when Learning Object Manipulation

> [!note] Foundation 关联
> - **[[ReinforcementLearning]]**: 课程设计对学习的影响
> - **[[ContactMechanics]]**: 触觉反馈与接触建模
> - **[[SignalProcessing#5. 状态估计：从局部触觉到全局语义]]**: 触觉信号处理与融合

## 元信息
- **作者**: Pegah Ojaghi, Romina Mir, Ali Marjaninejad, Francisco J. Valero-Cuevas, et al.
- **机构**: USC, UCSC, University of Wisconsin-Madison
- **年份**: 2025 (Science Advances)
- **期刊**: Science Advances — 高影响力综合科学期刊

> [!important] 核心发现
> **课程设计比触觉信息更能影响灵巧操作学习**——这挑战了"触觉对操作至关重要"的传统观念。

> [!abstract] 核心贡献
> 在三指机械手 in-hand manipulation 中发现：课程策略（任务子目标顺序）对操作学习的影响**显著大于**触觉反馈的有无。这用发育生物学的 "Waddington Landscape" 类比解释了课程如何塑造学习轨迹，挑战了"触觉是灵巧操作必需品"的传统观念。

---

## 1. 核心直觉与宏观定位

### 一句话核心
**不是你的传感器不够好，而是你的课程没设计对——课程就像教育路径，决定了"学什么"比"能感知什么"更关键。**

### 直观隐喻
想象训练一个盲人钢琴家：
- **传统观念**：先恢复视力（加传感器），才能弹好琴
- **本文发现**：按正确顺序练习（先单手 → 双手 → 复杂曲目）比有没有乐谱（视觉）更决定最终水平
- 触觉就像"乐谱"——有帮助，但没有也能学会，只要练习顺序对

### 现有方法的局限
传统灵巧操作研究过度强调传感器配置：
- 花大量成本部署昂贵触觉传感器（BioTac \$15k/个）
- 假设"更多传感 = 更好性能"，但忽略了训练课程的设计
- 缺乏对"课程 vs 传感"的系统性消融研究

---

## 问题设置

### 任务
- **三指机械手**在**向下朝向**（downward-facing）配置下进行 in-hand manipulation
- **目标**：抬升（Lift）和旋转（Rotate）一个球
- **无视觉**：仅依赖本体感知 + 可选触觉

### 为什么"向下朝向"更难？
传统研究多用向上朝向（手掌作为支撑平台），向下朝向需要：
- 持续对抗重力
- 更精确的力控制
- 任何错误都可能导致物体掉落

---

## 实验设计

### 两个变量

| 变量 | 条件 |
|-----|------|
| **触觉信息** | No-tactile vs 3D-force (指尖 3D 力向量) |
| **课程策略** | 5 种不同的 L/R 组合序列 |

### 课程策略示例
- **L→R**: 先学抬升，再学旋转
- **R→L**: 先学旋转，再学抬升
- **L+R**: 同时学习两者
- **L→L+R**: 先学抬升，再学组合
- **R→L+R**: 先学旋转，再学组合

### Delta 分析

| 方面 | 传统假设 | 本文发现 |
|-----|---------|---------|
| 性能瓶颈 | 传感器配置（触觉有/无） | **课程策略选择**（子任务顺序） |
| 关键设计变量 | 硬件投入（触觉传感器） | **训练流程设计**（零成本） |
| 触觉角色 | 必需品 | 锦上添花（biases but not gates） |
| 理论框架 | 工程直觉 | **发育生物学类比（Waddington Landscape）** |

---

## 核心发现

### 1. 课程 >> 触觉

> [!quote] 关键结论
> "The choice of curriculum biases the progression of learning for dexterous manipulation... Unexpectedly, learning is achieved even in the absence of haptic information."

**量化对比**：
- 不同课程策略导致的性能差异 **显著大于** 有/无触觉的差异
- 即使完全没有触觉反馈，某些课程仍能学习成功

### 2. "Waddington Landscape" 类比

作者用发育生物学的比喻描述学习过程：
- 初始状态是**多能的**（pluripotent）
- 课程像**山谷**引导发育方向
- 不同课程导向不同的技能组合

```
      [初始状态]
         /\
        /  \
       /    \
    [L优先] [R优先]
       \    /
        \  /
        [最终技能组合]
```

### 3. 触觉的微妙作用

虽然触觉不是"必需"的，但它**偏向**学习过程：
- **有触觉**：更倾向学习**力敏感**的技能组合
- **无触觉**：可能发展出不同的策略（如更依赖速度反馈）

---

## 方法细节

### 算法
- **PPO** (Proximal Policy Optimization)

### 状态空间
```python
state = {
    "joint_positions": q,      # 关节角度
    "joint_velocities": dq,    # 关节速度
    "ball_position": (x, z),   # 球的位置
    "ball_rotation": θ_y,      # 球的旋转角
    "tactile": [f_t1, f_t2, f_n]  # 可选：指尖 3D 力
}
```

### 奖励设计
$$R = c_R \cdot \theta_y - c_L \cdot |z_b - z_d|$$
- 旋转奖励正比于旋转角度
- 抬升惩罚正比于与目标高度的偏差

### 课程学习率调度器
作者提出了一个**基于课程的自适应学习率调度器**，加速收敛。

### 完整数学框架

**课程形式化**：设任务集合 $\mathcal{T} = \{L, R\}$（Lift, Rotate），课程 $\mathcal{C}$ 是任务的有序序列：

$$\mathcal{C} = (T_1, T_2, \ldots, T_k), \quad T_i \in \{\{L\}, \{R\}, \{L, R\}\}$$

**奖励函数的课程调度**：

$$R_{\mathcal{C}}(s, a, t) = \sum_{T \in \mathcal{T}_{\text{active}}(t)} w_T \cdot R_T(s, a)$$

其中 $\mathcal{T}_{\text{active}}(t)$ 由课程阶段决定活跃任务集。

**PPO 在课程下的目标**：

$$L^{\text{PPO}}(\theta) = \mathbb{E}_t\left[\min\left(r_t(\theta)\hat{A}_t, \text{clip}(r_t(\theta), 1\pm\epsilon)\hat{A}_t\right)\right]$$

其中 $\hat{A}_t$ 的计算使用课程阶段对应的奖励信号 $R_{\mathcal{C}}$。

**统计分析**：全因子设计，$5 \times 2 = 10$ 条件（5 课程 × 2 触觉），使用 Two-way ANOVA 分析课程和触觉的主效应和交互效应。

### 核心代码逻辑 (PyTorch)

```python
import torch
import torch.nn as nn

class CurriculumManager:
    """课程管理器：控制任务子目标的激活顺序"""
    def __init__(self, curriculum_type: str, switch_threshold: float = 0.8):
        # curriculum_type: 'L->R', 'R->L', 'L+R', 'L->L+R', 'R->L+R'
        self.curriculum_type = curriculum_type
        self.switch_threshold = switch_threshold
        self.stage = 0
        self.schedules = {
            'L->R':   [{'L': 1.0, 'R': 0.0}, {'L': 0.0, 'R': 1.0}],
            'R->L':   [{'L': 0.0, 'R': 1.0}, {'L': 1.0, 'R': 0.0}],
            'L+R':    [{'L': 1.0, 'R': 1.0}],
            'L->L+R': [{'L': 1.0, 'R': 0.0}, {'L': 1.0, 'R': 1.0}],
            'R->L+R': [{'L': 0.0, 'R': 1.0}, {'L': 1.0, 'R': 1.0}],
        }

    def get_reward_weights(self) -> dict:
        schedule = self.schedules[self.curriculum_type]
        return schedule[min(self.stage, len(schedule) - 1)]

    def step(self, success_rate: float):
        if success_rate > self.switch_threshold:
            self.stage += 1


def compute_reward(state: dict, weights: dict, c_R=1.0, c_L=0.5) -> torch.Tensor:
    """R = w_R * c_R * θ_y - w_L * c_L * |z_b - z_d|"""
    r_rotate = weights['R'] * c_R * state['ball_rotation']
    r_lift = weights['L'] * c_L * (state['ball_z'] - state['target_z']).abs()
    return r_rotate - r_lift


class TactileObsWrapper:
    """触觉观测包装器：控制触觉信息的有无"""
    def __init__(self, use_tactile: bool):
        self.use_tactile = use_tactile

    def process(self, obs: dict) -> torch.Tensor:
        features = [obs['joint_pos'], obs['joint_vel'],
                     obs['ball_pos'], obs['ball_rot']]
        if self.use_tactile:
            features.append(obs['fingertip_forces'])  # 3D force per finger
        return torch.cat(features, dim=-1)
```

---

## 对传统观念的挑战

### 传统观念
> "触觉对灵巧操作至关重要"

### 本文发现
> "在某些任务和课程下，触觉可能是**锦上添花**而非**必需品**"

### 可能的解释
1. **信息冗余**：本体感知（位置、速度）可能隐含了部分接触信息
2. **策略适应**：无触觉时，策略可能发展出不依赖触觉的替代方案
3. **任务特异性**：对于特定的 Lift+Rotate 任务，触觉可能不是瓶颈

---

## 实验细节

### 对象变化实验
测试了不同重量和尺寸的球：
| 重量 | 半径 |
|-----|------|
| 50g | 35mm |
| 50g | 30mm |
| 5g  | 35mm |
| 5g  | 30mm |

结果表明学习具有**跨对象泛化**能力。

### Ablation 因果链分析

本文的核心发现本身就是一个大型 factorial ablation：

| 移除/变更的组件 (A) | 效果 (B) | 机制分析 (C) |
|-------------------|----------|-------------|
| 移除触觉（No-tactile vs 3D-force） | 性能差异**不显著** | 本体感知（关节角/速度）通过接触雅可比间接编码接触力信息，冗余度高 |
| 变更课程策略（L→R vs R→L vs L+R） | 性能差异**显著**（ANOVA p<0.05） | 课程决定了策略梯度的初始方向——不同起点导向不同 basin of attraction（Waddington） |
| 先学 Lift 再学 Rotate（L→R） | Lift 性能最佳但 Rotate 一般 | Lift 优先固化了"保持接触"的策略先验，Rotate 需要的"释放-重新抓取"模式被抑制 |
| 先学 Rotate 再学 Lift（R→L） | Rotate 性能好但 Lift不稳定 | Rotate 优先发展了动态接触模式，但 Lift 需要的稳态接触被弱化 |
| 同时学习 L+R | 两项性能均衡但均非最优 | 多目标竞争稀释了梯度信号，收敛速度慢 |

---

## 与相关工作的联系

### 与 [[Curriculum Learning]] 的关系
- 验证了课程学习在**机器人操作**领域的有效性
- 扩展：课程不仅加速学习，还**塑造**最终技能

### 与 [[Lessons from Learning to Spin Pens]] 的对比
| Spin Pens | 本文 |
|-----------|-----|
| 强调触觉重要性 | 发现课程 > 触觉 |
| 水平旋转 | 对抗重力旋转 |
| 复杂对象 (笔) | 简单对象 (球) |

### 与 [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References|DexTrack]] 的联系
- 两者都强调**设计选择**（课程/参考轨迹）对学习的深远影响
- 比单纯增加传感器可能更重要

---

## 工程关键细节 (Engineering Tricks)

| 技巧 | 说明 |
|-----|------|
| **向下朝向配置** | 手掌朝下增加任务难度（持续对抗重力），迫使策略学到鲁棒的力控技能 |
| **课程切换时机** | 当前阶段成功率 > 80% 时切换到下一阶段，避免过早推进 |
| **Two-way ANOVA** | 使用统计显著性检验（而非单纯对比均值）确认课程效应 > 触觉效应 |
| **跨对象泛化测试** | 用 4 种质量×尺寸组合测试，确认结论不是对象特异的 |
| **学习率调度** | 课程感知的自适应 LR，阶段切换时适当降低 LR 避免灾难性遗忘 |

---

## 对实践的启示

> [!tip] 设计启示
> 1. **优先设计好课程**：比堆传感器更有效
> 2. **不要过度依赖触觉**：本体感知可能足够
> 3. **课程即"先验"**：选择什么课程隐含了对任务的理解

> [!warning] 适用范围
> 本文结论主要适用于**模拟环境**和**特定任务**（Lift+Rotate 球）。
> 在更复杂任务或真实硬件上，触觉可能仍然重要。

### 局限性（理论/算法/工程三维度）

| 维度 | 局限 | 替代方案 |
|-----|------|--------|
| **理论** | Waddington Landscape 类比缺乏数学形式化；无法预测哪个课程最优 | 信息论框架量化课程的信息增益 $I(\mathcal{C}; \pi^*)$ |
| **算法** | 仅测试了 5 种人工设计的课程组合，搜索空间远未穷尽 | 自动课程搜索（如 evolutionary curriculum、LLM 生成课程） |
| **工程** | 仅在仿真中验证（MuJoCo），未做 Sim-to-Real 迁移；三指手自由度较低 | 在 Allegro/LEAP 等高 DoF 手上验证 + 真实部署 |

### 对灵巧手转笔 + Sim-to-Real 的具体启发

> [!tip] 关键迁移 Insight
> 1. **课程优先于传感器投入**：在转笔项目中，与其花时间调试触觉传感器的 sim-to-real gap，不如先设计好课程——（慢速推动 → 半圈旋转 → 完整旋转 → 连续转笔）。本文证明课程效应 >> 触觉效应。
> 2. **触觉作为"偏置"而非"门控"**：触觉不决定策略能否学成，但偏置策略学成什么样——有触觉时可能学到力敏感的精细操作，无触觉时可能发展速度/位置控的替代策略。对转笔而言，这意味着可以用两条训练路径：有/无触觉分别训练，最终 ensemble。
> 3. **Waddington 启示**：课程的早期阶段（先学什么）决定了策略的"命运"——对转笔而言，先学稳定抓取（Lift 等价）可能比先学旋转（Rotate）更安全，因为稳定抓取是旋转的前提条件。

---

## 关联笔记

- [[Curriculum Learning]] - 课程学习基础
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] - 课程学习在 Sim-to-Real 中的应用
- [[ReinforcementLearning]] - PPO 算法
- [[ContactMechanics]] - 接触力学基础

---

## 与 Foundation 的数学对应

### [[ReinforcementLearning]] — 课程对策略梯度方向的影响

课程策略 $\mathcal{C}$ 决定了 PPO 策略梯度的方向（[[ReinforcementLearning]]）：

$$\nabla_\theta J_{\mathcal{C}}(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_t \nabla_\theta \log\pi_\theta(a_t|s_t) \cdot \hat{A}^{\mathcal{C}}_t\right]$$

不同课程 $\mathcal{C}$ 产生不同的 advantage $\hat{A}^{\mathcal{C}}_t$（因为奖励权重 $w_L, w_R$ 不同），从而引导参数 $\theta$ 走向不同的 basin of attraction——这正是 Waddington Landscape 的数学化身。

### [[ContactMechanics]] — 本体感知的接触信息冗余

关节力矩 $\tau \in \mathbb{R}^n$ 通过 [[ContactMechanics]] 与接触力建立映射：

$$\tau = J_c(q)^T f_c + g(q)$$

这意味着关节本体感知（$q, \dot{q}, \tau$）隐式包含接触力信息——当已知重力补偿项 $g(q)$ 时，$\tau - g(q) = J_c^T f_c$ 直接给出接触力的投影。这解释了为什么移除显式触觉后性能未显著下降。

### [[SignalProcessing]] — 触觉信息的冗余度分析

从 [[SignalProcessing#5. 状态估计：从局部触觉到全局语义]] 的视角：触觉传感器提供的 3D 指尖力 $(f_t, f_n)$ 与关节力矩 $\tau$ 之间存在高度线性相关——互信息 $I(\text{tactile}; \tau)$ 较高，说明触觉对策略的边际信息增益有限。

---

## 跨方法/跨范式对比

| 方法 | 核心变量 | 触觉角色 | 课程结构 | 结论 |
|-----|---------|---------|---------|------|
| **本文** | 课程顺序 × 触觉有无 | 非必需（偏置） | 任务子目标序列 | 课程 >> 触觉 |
| **[[Lessons from Learning to Spin Pens]]** | 触觉传感器 × 手指数 | 重要（尤其转笔） | 隐式（奖励整形） | 触觉对复杂操作关键 |
| **[[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation\|CSR]]** | 观测空间维度 | 可移除（渐进） | 特征移除课程 | 课程式移除 > 一步裁剪 |
| **[[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]]** | 触觉 + DR | 必需（旋转泛化） | 无 | 触觉对泛化关键 |
| **[[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots\|DemoStart]]** | 演示引导课程 | 不涉及 | 状态初始化 | 课程加速收敛 |

> [!note] 综合结论
> 触觉是否"必需"取决于任务复杂度和对象形状：简单球体操作可能不需要，但笔、骰子等非对称对象的旋转可能依赖触觉的滑移检测。课程设计是一个**成本更低、效果更显著**的优化维度。
