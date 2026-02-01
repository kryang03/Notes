---
tags:
  - paper
  - learning-from-demonstration
  - dmp
  - residual-learning
  - contact-manipulation
aliases:
  - rLfD
  - Residual DMP
paper-year: 2022
read-date: 2026-01-31
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
---

# Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation

> [!abstract] 核心概要
> 提出 **rLfD (residual Learning from Demonstration)** 框架：用 DMP 提供 100Hz 基础轨迹，叠加 10Hz 的 RL 残差策略进行在线修正，实现接触密集型插入任务（插销、齿轮、网线）的稳健执行。

> [!tip] 与理论基础的关联
> - [[ControlTheory#3. 技术演进：从刚性位置控制到柔顺力控制]] - 底层使用阻抗控制
> - [[ReinforcementLearning#3. Implementation: 核心算法细节分析]] - 残差策略用 SAC/PPO 训练
> - [[ContactMechanics#3. 接触建模演变：从点模型到软体模型]] - 接触密集型任务的核心挑战
> - [[Dynamics#6. Insights: 灵巧操作中的 Closed Loop Dynamics (闭链动力学)]] - 插入任务中的力控制
>
> **核心技术**: Dynamic Movement Primitives, Residual Policy Learning, Task-space Adaptation

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**DMP 提供粗略轨迹 + RL 学习在线修正 = 稳健的接触操作技能**

### 直观隐喻
想象你在黑暗中插 USB：
- **纯 DMP（行为克隆）**：按照演示的精确轨迹移动，但稍有偏差就卡住
- **纯 RL**：随机探索，可能需要几千次尝试才能成功
- **rLfD**：先按大致方向靠近，然后"微微抖动"找到正确位置——这个抖动就是学到的残差策略

### 领域定位
```
Dynamic Movement Primitives (Ijspeert, 2002)
        ↓
DMP + Iterative Learning (PoWER, 2010)
        ↓
Residual RL (Silver et al., 2018)
        ↓
████████████████████████████████████
█  rLfD (2022)                     █
█  • DMP 基策略 + RL 残差           █
█  • 任务空间全姿态修正             █
█  • 接触密集型插入任务             █
████████████████████████████████████
        ↓
未来: 结合触觉反馈的残差学习
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析

| 方法 | 适应空间 | 探索方式 | 姿态修正 |
|-----|---------|---------|---------|
| PoWER/FDG | 参数空间 | 线性基函数 | ❌ |
| eNAC | 相位耦合项 | 相位调制 | ❌ |
| **rLfD** | **任务空间** | **RL 非线性策略** | **✅ 全姿态** |

### 关键贡献

1. **C1**: 系统对比了 DMP 各部分的适应策略（参数空间 vs 任务空间）
2. **C2**: 提出任务空间全姿态残差框架，包含关键的**姿态修正**
3. **C3**: 证明非线性 RL 残差策略在接触任务中显著优于线性方法

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                    rLfD Framework                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌─────────────┐      ┌─────────────┐                   │
│  │  DMP Base   │      │  RL Residual │                   │
│  │  Policy     │      │  Policy      │                   │
│  │  (100 Hz)   │      │  (10 Hz)     │                   │
│  │             │      │              │                   │
│  │  Position   │      │  Δx, Δy, Δz  │                   │
│  │  Orientation│      │  Δquat       │                   │
│  └──────┬──────┘      └──────┬───────┘                   │
│         │                    │                          │
│         └────────┬───────────┘                          │
│                  │                                      │
│                  ▼                                      │
│         ┌───────────────┐                               │
│         │   a_final =   │                               │
│         │ a_base+a_adapt│                               │
│         └───────┬───────┘                               │
│                 │                                       │
│                 ▼                                       │
│         ┌───────────────┐                               │
│         │  Impedance    │                               │
│         │  Controller   │                               │
│         │  (500 Hz)     │                               │
│         └───────────────┘                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 3.2 Dynamic Movement Primitives (DMP) 回顾

**位置 DMP**：
$$\tau \dot{v} = K(g - x) - Dv + f(s)$$
$$\tau \dot{x} = v$$

其中：
- $x$: 位置，$v$: 速度
- $g$: 目标点
- $K, D$: 刚度、阻尼
- $f(s)$: forcing term（从演示学习）
- $s$: 相位变量（$\dot{s} = -\alpha s / \tau$）

**Forcing Term**：
$$f(s) = \frac{\sum_i \psi_i(s) w_i s}{\sum_i \psi_i(s)}$$

基函数 $\psi_i(s) = \exp(-h_i(s - c_i)^2)$ 覆盖相位空间。

### 3.3 残差策略设计

**关键洞察**：DMP 的 forcing term 天然支持**耦合项**，可用于在线修正。

**传统方法**（参数空间适应）：
$$f(s) \to f(s) + C(s)$$
其中 $C(s)$ 是学习的耦合项，但仍是线性基函数组合。

**rLfD 方法**（任务空间适应）：
$$a_{final} = a_{DMP}(s) + \pi_{residual}(s, o)$$

其中 $\pi_{residual}$ 是一个神经网络策略，输入包括：
- 当前相位 $s$
- 观测 $o$（包括末端执行器位姿、力/力矩反馈等）

### 3.4 姿态残差的挑战

> [!warning] 四元数加法的问题
> 姿态不能简单相加！$q_1 + q_2$ 不是有效的旋转。

**解决方案**：
1. DMP 输出目标姿态 $q_{DMP}$
2. 残差策略输出角速度增量 $\Delta \omega \in \mathbb{R}^3$
3. 通过指数映射叠加：
   $$q_{final} = q_{DMP} \cdot \exp(\Delta \omega \cdot \Delta t / 2)$$

---

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**任务**（递增难度）：
1. **Peg Insertion**：圆柱销插入（0.5mm 间隙）
2. **Gear Insertion**：齿轮插入（需要对齐齿）
3. **RJ-45 Connector**：网线插入（最复杂，非对称）

**平台**：Franka Panda 机械臂 + IsaacGym 仿真

### 4.2 方法对比

| 方法 | Peg | Gear | RJ-45 |
|-----|-----|------|-------|
| Pure DMP | 45% | 12% | 5% |
| DMP + Linear Residual | 68% | 35% | 22% |
| DMP + RL (Position only) | 82% | 61% | 48% |
| **rLfD (Full Pose)** | **96%** | **89%** | **78%** |

### 4.3 关键发现

1. **姿态修正至关重要**：RJ-45 任务中，没有姿态修正的成功率从 78% 降到 48%
2. **任务空间 > 参数空间**：直接在末端执行器空间修正比修改 DMP 参数更有效
3. **非线性策略 > 线性策略**：RL 神经网络显著优于线性基函数

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **样本效率**：DMP 提供强先验，减少 RL 探索
- **安全性**：残差幅度可限制，防止危险动作
- **泛化性**：对起始位置、几何形状、摩擦变化鲁棒
- **实时性**：100Hz DMP + 10Hz 残差，计算可行

### 局限性
- **需要演示**：仍依赖人类示教
- **仅位置/姿态控制**：没有直接控制力
- **单任务**：每个任务需要单独训练残差策略
- **缺乏触觉**：使用力/力矩传感器，但没有高分辨率触觉

### 与阻抗控制的关系
底层使用阻抗控制器，rLfD 实际上是在**调节阻抗控制的参考轨迹**，而非直接控制刚度/阻尼。这是一种隐式的柔顺控制。

---

## 6. 对灵巧操作的启发 (Implications)

### 扩展到灵巧手

```
单臂 rLfD:
  DMP → 末端位姿
  Residual → 位姿修正
  
灵巧手 rLfD:
  DMP → 手指关节轨迹
  Residual → 关节角修正 + 抓取力调节
  
挑战：
  - 更高维度（24+ DoF）
  - 更复杂的接触模式
  - 需要触觉反馈
```

### 与其他论文的联系
- **EUREKA**：可用 LLM 生成 rLfD 的奖励函数
- **Curriculum Learning**：从简单插入 → 复杂插入的课程
- **Stability-Certified RL**：为残差策略添加稳定性保证

---

## 7. 演进脉络定位 (Evolution Context)

```
Imitation Learning 基础
        ↓
Dynamic Movement Primitives (Ijspeert, 2002)
        ↓
DMP + Iterative Learning Control
├── PoWER (2010): 参数空间 RL
└── FDG (2013): 参数空间梯度
        ↓
Residual Policy Learning (Silver, 2018)
        ↓
██████████████████████████████████████
█  rLfD (2022)                       █
█  • 任务空间残差                     █
█  • 全姿态修正（包括 orientation）   █
█  • 非线性 RL 策略                   █
██████████████████████████████████████
        ↓
未来: 触觉引导的残差学习
```

---

## 8. 核心代码逻辑

```python
class rLfD_Controller:
    def __init__(self, dmp_params, residual_policy):
        self.dmp = DMP(dmp_params)  # 从演示学习
        self.residual = residual_policy  # RL 训练
        self.impedance = ImpedanceController()
        
    def step(self, obs, phase):
        # 1. DMP 基础动作 (100 Hz)
        pos_dmp, quat_dmp = self.dmp.get_action(phase)
        
        # 2. 残差修正 (10 Hz, 每10步执行一次)
        if self.should_update_residual():
            delta_pos, delta_omega = self.residual(obs)
            self.cached_residual = (delta_pos, delta_omega)
        
        # 3. 组合动作
        pos_final = pos_dmp + self.cached_residual[0]
        quat_final = quat_multiply(
            quat_dmp, 
            exp_map(self.cached_residual[1])
        )
        
        # 4. 阻抗控制 (500 Hz)
        torque = self.impedance.compute(
            target_pos=pos_final,
            target_quat=quat_final,
            current_state=obs
        )
        
        return torque
```

---

## 9. 与 Foundation 的链接更新

### 需要添加到 ControlTheory.md
在阻抗控制部分添加"参考轨迹的学习与适应"小节。

### 需要添加到 ReinforcementLearning.md
在模仿学习部分添加"残差策略学习"作为 BC 的改进方向。
