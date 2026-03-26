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
venue: ICRA 2022
paper-pdf: "[[Papers/Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation.pdf]]"
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

### 4.1b 训练细节

- **RL 算法**: SAC (Soft Actor-Critic)，也测试了 PPO
- **残差网络**: 3 层 MLP, 256 隐藏单元, ReLU
- **观测空间**: 末端位姿 (7D) + 力/力矩 (6D) + 相位 $s$ (1D) = 14D
- **动作空间**: 位置残差 $\Delta x \in \mathbb{R}^3$ + 姿态残差 $\Delta \omega \in \mathbb{R}^3$ = 6D
- **残差约束**: $\|\Delta x\| \leq 5$ mm, $\|\Delta \omega\| \leq 5°$ (安全边界)
- **DMP 基函数**: 30 个高斯基/DoF
- **训练步数**: ~$5 \times 10^5$ 步 (IsaacGym 并行 1024 envs)
- **频率分离**: DMP 100Hz, 残差策略 10Hz, 阻抗控制器 500Hz

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

> [!note] Ablation 因果链
> - **去掉姿态残差** → RJ-45 成功率从 78% 降到 48% → 因为网线连接器的非对称形状要求精确 roll/yaw 对齐，纯位置修正无法补偿 ~3° 姿态偏移
> - **参数空间替代任务空间** → 所有任务下降 15-30% → 因为参数空间适应等效于修改整条 DMP 轨迹（全局效应），而接触修正需局部即时响应
> - **线性残差替代 RL** → 中等下降 → 因为线性基函数的表达能力不足以捕捉接触力的非线性突变（穿过接触面时力的不连续跳变）
> - **去掉力/力矩观测** → 成功率下降 ~20% → 因为纯位置观测无法区分"即将接触"和"已经接触"两种状态

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

### 工程关键细节 (Engineering Tricks)

1. **频率分离设计**：DMP (100Hz) 保证平滑轨迹，RL (10Hz) 降低推理负担，阻抗控制 (500Hz) 保证接触稳定——三级频率各司其职
2. **残差幅度限制**：$\|\Delta x\| \leq 5$ mm 防止 RL 探索产生危险动作——插入间隙 0.5mm，5mm 余量 = 10× 安全因子
3. **四元数姿态残差**：用角速度 $\Delta \omega$ 而非四元数差值，避免四元数双覆盖问题（$q$ 和 $-q$ 表示相同旋转）
4. **相位变量作为观测**：DMP 相位 $s \in (0, 1)$ 纳入 RL 观测，让策略区分接近阶段和插入阶段的不同修正策略

> [!warning] 三维度局限性分析
> - **理论层面**：残差策略的最优性依赖基策略 (DMP) 的质量——若 DMP 轨迹偏差 > 残差上限，RL 无法补偿；缺乏对残差策略收敛到次优解的分析
> - **算法层面**：频率分离 (10Hz/100Hz) 引入决策延迟——接触瞬间的力突变持续 <10ms，10Hz 策略无法及时响应
> - **工程层面**：阻抗控制器刚度/阻尼固定，对不同材料需不同参数；IsaacGym 接触模型与真实接触动力学有 gap
>
> **替代方案**：直接 RL（无 DMP 先验）在充足训练下可能更优；可变阻抗控制同时学习残差 + 阻抗参数；触觉反馈可弥补力/力矩传感器的低分辨率

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

### 对转笔 / Sim-to-Real 的具体启发

1. **转笔的频率分离**：手指协调轨迹用 DMP 编码（从遥操作学习），RL 残差修正指尖力分配——DMP 保证手指运动节奏，RL 处理笔的接触不确定性
2. **残差上限与安全**：灵巧手指力矩远小于机械臂，残差限制需更精细（$\|\Delta \theta\| \leq 2°$/关节），防止手指碰撞
3. **Sim-to-Real 优势**：DMP 先验大幅缩小 RL 搜索空间，域随机化只需覆盖残差范围内的不确定性（而非整个轨迹），降低 sim-to-real 难度

### 与 Foundation 的数学联系

**与 [[ControlTheory]] 的联系**：rLfD 的阻抗控制 $\tau = K_x(x_{ref} - x) + D_x(\dot{x}_{ref} - \dot{x})$ 将任务空间目标转为关节扭矩，残差策略修改 $x_{ref}$。这等效于 [[ControlTheory#3. 技术演进：从刚性位置控制到柔顺力控制]] 中阻抗控制的在线参考轨迹调节

**与 [[Dynamics]] 的联系**：DMP 的弹簧-阻尼系统 $\tau \dot{v} = K(g-x) - Dv + f(s)$ 是二阶动力学系统（[[Dynamics#2. Core Concepts: 物理直觉与数学形式的对偶 (The Duality of Intuition and Formalism)]]），其稳定性由 $K, D$ 的正定性保证（被动性条件）

**与 [[ContactMechanics]] 的联系**：插入任务涉及刚性接触的力突变——从自由运动 ($f_c = 0$) 到约束运动 ($f_c > 0$) 的不连续跳变，这是 [[ContactMechanics#4. 计算动力学与求解器：从LCP到凸优化]] 中 LCP 建模的典型场景。残差策略需学习在接触边界附近的柔顺行为

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

### 跨方法对比

| 维度 | rLfD (DMP+RL) | 纯 RL | 纯 DMP/LfD | Residual RL (Silver 2018) | 可变阻抗控制 |
|-----|---------------|-------|-----------|--------------------------|-------------|
| 演示需求 | 1-5 次 | 0 次 | 1-5 次 | 需预训练策略 | 0 次 |
| 样本效率 | ✅ 高 | ❌ 低 | ✅ 极高 | ⚠️ 中 | ⚠️ 中 |
| 接触鲁棒性 | ✅ 强 | ⚠️ 依赖训练 | ❌ 脆弱 | ⚠️ 中 | ✅ 强 |
| 姿态修正 | ✅ 全姿态 | ✅ 全姿态 | ❌ 无 | ❌ 仅位置 | N/A |
| 安全性 | ✅ 残差受限 | ❌ 无约束 | ✅ 确定性 | ⚠️ 残差受限 | ✅ 被动稳定 |
| 力控制 | 隐式(阻抗) | 可显式 | ❌ 无 | 隐式 | ✅ 显式 |

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
