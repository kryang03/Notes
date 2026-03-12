---
tags:
  - paper
  - control
  - compliance
  - impedance
  - manipulation
aliases:
  - Minimalist Compliance
  - MCC
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (Stanford University)
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# Minimalist Compliance Control

> [!abstract] 核心贡献
> 提出 **Minimalist Compliance Control**：仅使用电机电流或 PWM 信号估计外力/力矩，通过经典任务空间导纳控制实现柔顺行为——**无需力传感器、无需学习、无 sim-to-real gap**。在机械臂 (ARX QDD)、灵巧手 (LEAP Servo)、两款人形机器人 (Unitree G1) 上跨多种接触丰富任务验证。

> [!tip] 与理论基础的关联
> - [[ControlTheory#2.1 阻抗控制]] — 弹簧-质量-阻尼导纳控制框架 $m\ddot{x} = K_p(x_{des}-x) + K_d(\dot{x}_{des}-\dot{x}) + f_{cmd} + f_{ext}$
> - [[Dynamics]] — 电机力矩模型、雅可比映射、正/反驱效率建模
> - [[ContactMechanics]] — 外力矩估计与重力补偿
>
> **核心技术**: Sensorless Wrench Estimation, Task-Space Admittance Control, Motor Torque Model, Direction-Dependent Efficiency

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
现代伺服/准直驱电机的电流/PWM 信号中已蕴含足够的外力信息——不需要力传感器，也不需要强化学习，经典导纳控制 + 电机力矩模型即可实现稳定柔顺。

### 直观隐喻
力传感器像"专用温度计"，昂贵但精确；Minimalist Compliance 像"用手背试水温"——精度够用、方向正确，足以安全舒适地完成任务。

### 领域定位
- **柔顺控制前沿**: 从 Force Sensor-based Impedance → RL-based Compliance → **Model-based Sensorless Compliance**
- **核心洞察**: 柔顺控制不需要高精度力测量，只需正确的力方向和合理的频率响应。RL 方法无法保证力方向一致性和安全性，而电机电流估计在这两方面天然满足。

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 对比基线 | MCC 优势 |
|---------|---------|
| 传统阻抗控制 (需力传感器) | 无硬件依赖，成本降 10× |
| RL-based Compliance (ACT-slip等) | 无 sim-to-real gap，有安全保证，无力冲击风险 |
| 1990s 电流估计方法 | 现代电机传感精度大幅提升，无需复杂观测器滤波 |

### 关键贡献点
1. **极简力估计** — 从电机电流或**纯 PWM 信号**（甚至不需要电流传感器）估计外力矩
2. **跨形态通用** — 同一框架适用于 QDD 电机（机械臂/人形）和高减速比伺服（灵巧手，减速比 >200:1）
3. **即插即用** — 与 VLM 策略、模仿学习策略、模型规划策略均兼容

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 弹簧-质量-阻尼导纳模型

$$m\ddot{x} = K_p(x_{des} - x) + K_d(\dot{x}_{des} - \dot{x}) + f_{cmd} + f_{ext}$$

- $x \in \mathbb{R}^6$：末端位姿（位置 + 旋转向量）
- $K_p, K_d$：刚度与阻尼矩阵
- $f_{ext}$：从电机信号估计的外力矩

### 3.2 电机力矩估计

**有电流传感器**：直接读取 $I_w$ 

**无电流传感器**（纯 PWM）：
$$V_{PWM} = PWM \times V_{bus}, \quad V_{emf} = \dot{q}/K_v, \quad I_w = (V_{PWM} - V_{emf})/R_w$$

**方向依赖效率模型**（关键创新）：

$$\tau_{load} = \begin{cases} \eta K_t I_w & d > 0 \text{ (正向驱动)} \\ \eta^{-1} K_t I_w & d \leq 0 \text{ (反向驱动)} \end{cases}$$

其中 $d = \text{sign}(\tau_w \dot{q})$ 判断正/反驱状态，$\eta \in (0,1]$ 为传动效率。

**外力矩隔离**：$\tau_{ext} = -(r \cdot \tau_{load} - \tau_{grav})$，准静态假设下忽略惯性项和科氏力项。

### 3.3 关键洞察：为什么近似估计就够了

> [!warning] 核心洞察
> 柔顺控制对力精度的要求远低于力控制：
> - **力方向正确** + **频率响应足够** → 稳定安全的柔顺
> - 力幅度精度 → 主要影响性能而非安全
> - RL 方法无法显式保证力方向一致性 → 危险力冲击风险

## 4. 实验与验证 (Experiments)

### 平台
| 平台 | 电机类型 | 力估计信号 | 减速比 |
|------|---------|-----------|-------|
| ARX 机械臂 | QDD | 电流 | ~6:1 |
| LEAP 灵巧手 | Dynamixel 伺服 | **PWM** | >200:1 |
| Unitree G1 人形 | QDD | 电流 | ~6:1 |

### 任务与结果
- 擦拭、绘画、舀取、手内操作
- 与 VLM (GPT-4V)、模仿学习、模型规划各种高层策略组合验证
- 在所有平台上实现安全稳定的柔顺交互

## 5. 批判性分析 (Critical Analysis)

### 优势
- **真正的极简主义**：零额外传感器、零学习、零 sim-to-real gap
- **安全保证**：基于经典控制理论，力方向一致性有物理保证
- 从 QDD 到 **200:1 高减速比伺服**均有效——扩展了无传感器柔顺的适用范围

### 局限性
- 准静态假设：高速动态操作时惯性项不可忽略
- 高减速比伺服的摩擦建模简化（方向依赖效率是近似）
- 未在高频摩擦切换（stick-slip）场景下验证

## 6. 对灵巧操作的启发 (Implications)

**与 DNPM 项目的直接关联**:

> [!warning] 与 Idea-001 (Phase-Adaptive Impedance) 的关键连接
> - MCC 提供了**无力传感器的柔顺控制基线**——如果 DNPM 的 LinkerHand 仅有电机电流信号，MCC 的方向依赖效率模型可直接适用
> - MCC 的刚度 $K_p$ 即 DNPM Exp2 中调优的关键参数——MCC 验证了 $K_p$ 精度不如力方向重要
> - **局限**：MCC 的准静态假设在动态非紧握操作（high $\ddot{q}$）中可能失效——这正是 Phase-Adaptive Impedance 的动机：在动态阶段需要不同的控制策略

## 7. 演进脉络定位 (Evolution Context)

```
1990s: 电流估计 + 观测器滤波（噪声大、实用性低）
    ↓ 现代电机精度提升
Model-based Sensorless Compliance（本论文）
    ↓ vs
RL-based Compliance（ACT-slip, VIC 等）
    ↓ 互补
未来方向: Model-based 提供安全基线 + RL 微调提升性能
```
