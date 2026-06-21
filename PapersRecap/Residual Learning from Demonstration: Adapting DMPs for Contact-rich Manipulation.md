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
> - [[ControlTheory]] - 底层阻抗控制；残差调节参考轨迹
> - [[ReinforcementLearning]] - 残差策略用 SAC/PPO 训练
> - [[ContactMechanics]] - 接触密集型插入任务的核心挑战（自由↔约束的力突变）
> - [[Dynamics]] - 插入任务闭链动力学；DMP 是二阶弹簧-阻尼系统
>
> **核心技术**: Dynamic Movement Primitives, Residual Policy Learning, Task-space Adaptation, 三级频率分离

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

### 3.0 变量来源追踪

枢纽：**$a_{final}=a_{DMP}+\pi_{residual}$**——DMP 强先验（100Hz）+ RL 残差（10Hz）局部修正；姿态残差用角速度而非四元数加法。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $a_{DMP}(s)$ | 位姿 | 演示学习（DMP，100Hz） | 否 | 基轨迹 | forcing term $f(s)$ 从演示拟合 |
| $\pi_{residual}$ | NN | RL 学习（10Hz） | 是 | 残差策略 | 任务空间（局部即时）非参数空间 |
| $\Delta x$ | $\mathbb{R}^3$ | 残差输出 | 是 | 位置残差 | **限 5mm = 10× 间隙**（安全） |
| $\Delta\omega$ | $\mathbb{R}^3$ | 残差输出 | 是 | 角速度残差 | **指数映射叠加** $q\cdot\exp(\Delta\omega\Delta t/2)$，非四元数加 |
| $s$ | $(0,1)$ | DMP 相位 | 否（观测） | 相位变量 | 入观测，区分接近/插入阶段 |
| $f_c$ | 力/力矩 | 观测 | 否 | 接触力 | 去掉则 −20%（区分将接触/已接触） |

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

### 3.5 概念边界与符号陷阱

- **姿态残差用 $\Delta\omega$ + 指数映射** $q_{DMP}\cdot\exp(\Delta\omega\Delta t/2)$，非四元数加法（$q_1+q_2$ 非有效旋转）。
- **残差幅度限制**（5mm = 10× 间隙）：安全 + 稳定（残差 > 微调）。
- **三级频率分离**：DMP 100Hz / 残差 10Hz / 阻抗 500Hz——各司其职。
- **任务空间残差（局部即时）vs 参数空间（全局）**：接触修正需局部响应。
- **残差依赖 DMP 质量**：DMP 偏差 > 残差上限则无法补偿（§局限）。
- **10Hz 残差对 <10ms 力突变响应不及**（§算法局限）。

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

**与 [[ControlTheory]] 的联系**：rLfD 的阻抗控制 $\tau = K_x(x_{ref} - x) + D_x(\dot{x}_{ref} - \dot{x})$ 将任务空间目标转为关节扭矩，残差策略修改 $x_{ref}$。这等效于 [[ControlTheory]] 中阻抗控制的在线参考轨迹调节

**与 [[Dynamics]] 的联系**：DMP 的弹簧-阻尼系统 $\tau \dot{v} = K(g-x) - Dv + f(s)$ 是二阶动力学系统（[[Dynamics]]），其稳定性由 $K, D$ 的正定性保证（被动性条件）

**与 [[ContactMechanics]] 的联系**：插入任务涉及刚性接触的力突变——从自由运动 ($f_c = 0$) 到约束运动 ($f_c > 0$) 的不连续跳变，这是 [[ContactMechanics]] 中 LCP 建模的典型场景。残差策略需学习在接触边界附近的柔顺行为

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

## 9. 残差学习作为通用修正范式（跨文献综述）

> [!note] "基策略 + RL 残差"是 sim-to-real / LfD 的通用修正范式 + 残差的三个设计维度
> rLfD 是"**基策略 + RL 残差**"范式的 DMP 实例。这个范式贯穿知识库：
>
> | 论文 | 基策略 | 残差 |
> |------|--------|------|
> | rLfD | DMP（演示） | RL 位姿残差 |
> | [[RECAP - A VLA that Learns from Experience\|RECAP]] | IL VLA | advantage-conditioned RL |
> | [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction\|TRANSIC]] | 仿真策略 | 人类纠正残差 |
> | [[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]] | 仿真基策略 | residual policy |
> | [[Grounded Action Transformation\|GAT]] | 仿真动作 | grounding 残差 $a+f_\theta$ |
>
> **为何普遍偏好残差而非重训**（呼应 TRANSIC insight）：残差小补偿稳定、保留基策略知识、避免灾难遗忘 + 可加安全限幅。
> **rLfD 系统揭示残差的三个设计维度**：① **作用空间**——任务空间（局部即时，rLfD）vs 参数空间（全局，PoWER）：接触修正需局部；② **频率分离**——DMP 100Hz + 残差 10Hz + 阻抗 500Hz 三级各司其职（= control frequency 簇 / [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks\|EvoControl]] 分层的推广）；③ **残差幅度限制**——5mm=10× 间隙的安全边界。这三维把"加个残差网络"提升为有系统设计空间的范式。
