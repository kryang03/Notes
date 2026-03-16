---
tags:
  - paper
  - control
  - impedance-control
  - reinforcement-learning
  - legged-robot
aliases:
  - FACET
paper-year: 2025
read-date: 2026-02-08
venue: arXiv (Tsinghua University / Shanghai AI Lab)
paper-pdf: "[[Papers/FACET- Force-Adaptive Control via Impedance Reference Tracking for Legged Robots.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[Optimization]]"
---

# FACET: Force-Adaptive Control via Impedance Reference Tracking for Legged Robots

> [!abstract] 核心贡献
> 提出将阻抗控制的虚拟弹簧-质量-阻尼模型作为 RL 策略的跟踪目标，使腿式机器人获得可控柔顺性和力自适应行为。通过暴露阻抗参数 $(x_{des}, K_p, K_d)$ 作为控制接口，策略能在大冲击下柔顺跟随（200 Ns 脉冲存活）、碰撞时显著降低冲击力（80%减小），并在真机上实现运动学示教和负载拖拽。

> [!tip] 与理论基础的关联
> - [[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]] — 阻抗控制理论基础
> - [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO]] — PPO 训练策略
> - [[Dynamics#3.1 The Classical Era: Lagrangian Formulation]] — 质量-弹簧-阻尼参考模型的动力学基础
> - [[Optimization]] — 跟踪目标的时间平滑优化
> - [[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks|VICES]] — 变阻抗动作空间的先驱工作
>
> **核心技术**: 阻抗参考模型跟踪, RL-based 力自适应, 时间平滑, Teacher-Student
>
> **核心技术**: 阻抗参考模型跟踪, RL-based 力自适应, 时间平滑, Teacher-Student

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
让 RL 策略不是直接跟踪位置/速度目标，而是跟踪一个虚拟弹簧-质量-阻尼系统的动力学轨迹，从而间接实现力自适应和可控柔顺性。

### 直观隐喻
想象机器人躯干被一根虚拟弹簧拴在目标位置。当外力推来时，弹簧允许机器人"被推着走"（柔顺），而不是"硬顶"（刚性）。调节弹簧刚度 $K_p$ 就能控制"顺从"程度——设 $K_p=0$ 时机器人几乎无阻力地被牵着走（运动学示教），设高 $K_p$ 时能施加大力拖拽重物。

### 领域定位
在 RL-based 腿式机器人控制中，首次提出基于阻抗参考模型的系统化力自适应框架。填补了速度跟踪控制器（刚性）和直接力控制器（需要力传感器）之间的间隙。

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
- **相比速度跟踪 (Vanilla)**：速度跟踪产生刚性策略，大冲击下失败
- **相比鲁棒训练 (Robust)**：加随机脉冲 DR 只能在中等范围内提高鲁棒性
- **相比 DMC**：DMC 识别了刚性问题但无法控制柔顺程度
- **相比 Learning Force Control**：需要在位置模式和力模式间显式切换，且假设近静态

### 关键贡献点
1. **阻抗参考模型**：定义虚拟质量-弹簧-阻尼系统 $m\ddot{x}_{ref} = K_p(x_{des} - x_{ref}) + K_d(\dot{x}_{des} - \dot{x}_{ref}) + f_{ext}$，RL 策略跟踪其产生的轨迹
2. **时间平滑 (Temporal Smoothing)**：混合从不同历史时刻积分的参考轨迹，平衡开环精度和闭环适应性
3. **统一接口 $(x_{des}, K_p, K_d)$**：单一接口同时控制位置、柔顺性和隐式力输出——不需要切换控制模式
4. **多平台验证**：四足 Go2、人形 G1、四足+机械臂 B1+Z1，真机验证运动学示教和 10kg 负载拖拽

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学建模

**参考模型动力学：**
$$m\ddot{x}_{ref} = K_p(x_{des} - x_{ref}) + K_d(\dot{x}_{des} - \dot{x}_{ref}) + f_{ext}$$

**机器人简化动力学：**
$$m\ddot{x}_{sim} = f_{grf} + f_{ext}$$

其中参考模型和机器人都经历相同的外力 $f_{ext}$，但参考模型额外受虚拟弹簧力 $f_{spring}$，机器人受地面反力 $f_{grf}$。

**训练目标：** 让 $x_{sim} \approx x_{ref}$，即通过地面反力间接实现弹簧力效果。

### 3.2 时间平滑

从不同起始时刻 $t' \in \{t-8\Delta t, t-16\Delta t, t-32\Delta t\}$ 积分参考动力学：

$$r_t = \frac{1}{M}\sum_{t'} \exp(-\|x_{sim}(t) - x^{t'}_{ref}(t)\|^2_2) + \exp(-\|\dot{x}_{sim}(t) - \dot{x}^{t'}_{ref}(t)\|^2_2)$$

- $t'=0$（开环）：精确跟踪参考模型但不适应实际约束
- $t'=t-\Delta t$（闭环）：自适应但短视、噪声大
- 混合方案兼取二者优势

### 3.3 多体扩展（Loco-manipulation）

对腿式操作系统（B1+Z1），分别为基座和末端定义参考模型：
$$m^{base}\ddot{x}^{base}_{ref} = f^{base}_{spring} + f^{base}_{ext} - a \cdot f^{eef}_{spring}$$
$$m^{eef}\ddot{x}^{eef}_{ref} = f^{eef}_{spring} + f^{eef}_{ext}$$

其中 $a \in [0,1]$ 控制末端力是否传导到基座。$a=1$ 允许通过拉末端来牵引整个机器人（运动学示教）。

## 4. 实验与验证 (Experiments)

### 关键定量结果

| 测试 | FACET | Robust | Vanilla |
|------|-------|--------|---------|
| 200Ns 脉冲存活率 | ~80% | ~30% | ~5% |
| 碰撞冲击力降低 | 80% (Kp=8) | 基线 | — |
| 10kg 负载拖拽 | ✅ | — | — |

### 真机验证
- 四足 Go2：运动学示教（人手轻推即跟随）+ 10kg 负载拖拽（约自重 2/3）
- 人形 G1 和四足+臂 B1+Z1：仿真验证

## 5. 批判性分析 (Critical Analysis)

### 优势
- 优雅地统一位置控制、力控制、柔顺控制在单一框架中
- 不需要力传感器——通过 RL 隐式学习力响应
- $K_p, K_d$ 参数直观可调，运行时可变
- 时间平滑方法巧妙解决了开环/闭环跟踪的权衡

### 局限性
- 仅验证了质心（CoM）级别的阻抗，未涉及单个关节/末端的精细阻抗控制
- 假设外力 $f_{ext}$ 同时作用于参考模型和机器人——但在实际中 $f_{ext}$ 未必精确已知
- Teacher-Student 蒸馏中，学生策略的极端外力场景性能可能退化
- 未涉及接触丰富的操作任务（如灵巧手操作）

### 未来方向
- 扩展到灵巧手操作：每个关节/指尖定义独立阻抗参考模型
- 与 RL 学习阻抗参数相结合：不仅跟踪参考模型，还学习最优阻抗
- 在接触切换频繁的任务中验证（如非紧握操作）

## 6. 对动态非紧握操作的启发 (Implications for DNPM)

> [!warning] 关键洞见 — 对 DNPM 项目的直接启发

**1. 阻抗参考模型可直接应用于 DNPM 的 Direction A（底层控制器优化）**

DNPM ideas.md 3.1 中的核心问题是"PD 控制器限制了力矩表达的 pattern"。FACET 提供了精确的解决方案：
- 不再让 RL 输出 $q_{target}$ 给固定 PD 控制器
- 而是让 RL 输出 $(x_{des}, K_p, K_d)$，底层通过阻抗参考模型生成期望轨迹
- $K_p, K_d$ 可随时间变化 → "先软后硬"或"振荡式"力矩 pattern 自然可实现

**2. 虚拟弹簧刚度与 Snap 阶段的完美匹配**

Thumbaround 的 snap 阶段需要：
- 发力前：高 $K_p$（精确定位手指到预紧位置）
- Snap 瞬间：高 $K_p$（最大力矩发力）
- 旋转阶段：低 $K_p$（允许笔在接触中产生柔顺滑动）
- 收手式：中等 $K_p$（精确接住但不硬撞）

FACET 的框架允许策略自然学习这种时变阻抗变化。

**3. 时间平滑技术可解决 DNPM 的 Value Landscape 问题**

FACET 的时间平滑混合了多个时间尺度的跟踪目标。在 DNPM 中：
- 开环参考：提供长期的"理想轨迹"指引
- 闭环参考：适应接触切换等突发事件
- 混合奖励可能缓解 Value Landscape 的崎岖性

**4. 多体扩展对 arm-hand 协调的启示**

FACET 为基座和末端分别定义阻抗参考模型，通过参数 $a$ 控制力传导。在 DNPM 的 UR5 + 灵巧手系统中：
- UR5（基座）：低 $K_p$（大范围柔顺运动，用于能量注入）
- 灵巧手各指：独立 $K_p, K_d$（高频精细阻抗控制，用于接触切换）
- $a$ 参数控制手指力是否传导到臂部

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── 经典阻抗控制 (Hogan 1985) → 固定基座机械臂
├── 变阻抗 RL (VICES, Martin 2019) → 末端空间阻抗
├── DMC (Deep Compliant Control) → 识别刚性问题但无法控制
├── Learning Force Control → 需要模式切换
└── Velocity Tracking RL → 刚性、不安全
    ↓
本论文: FACET — 虚拟阻抗参考模型 + RL 跟踪 + 时间平滑
    ↓
后续影响:
├── 扩展到灵巧手操作的关节级阻抗控制
├── 与 HDC 等课程方法结合用于动态操作
└── 统一的力-位-柔顺控制接口标准化
```
