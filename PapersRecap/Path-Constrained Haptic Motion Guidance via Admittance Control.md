---
tags:
  - paper
  - haptic-guidance
  - admittance-control
  - human-robot-interaction
aliases:
  - Phase-Based Admittance Control
  - Path-Constrained Haptic Guidance
paper-year: 2025
read-date: 2026-02-02
venue: IEEE TRO
paper-pdf: "[[Papers/Path-Constrained_Haptic_Motion_Guidance_via_Adaptive_Phase-Based_Admittance_Control.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[Optimization]]"
---

# Path-Constrained Haptic Motion Guidance via Adaptive Phase-Based Admittance Control

> [!abstract] 核心贡献
> 提出**相位自适应导纳控制**框架，实现人机协作中的路径约束引导：机器人精确维持几何约束，人类通过力反馈控制运动特性（速度、时机），同时保证系统稳定性。

> [!tip] 与理论基础的关联
> - [[ControlTheory#3.2 解决方案 I：阻抗控制 (Impedance Control) —— 调节动态关系]] - 导纳控制作为阻抗控制的对偶
> - [[Dynamics]] - 相位变量与轨迹参数化
> - [[Optimization]] - 约束路径的运动规划
>
> **核心技术**: Admittance Control, Phase Variable, Passivity-Based Stability, Virtual Energy Tank

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**机器人保证走哪条路，人类决定怎么走**——通过相位变量将路径约束与运动自由度解耦，人机协作时机器人确保几何精度，人类通过力交互控制速度和时机。

### 直观隐喻
像有导轨的机械臂：导轨（路径约束）限定了运动的几何形状，但沿导轨前进的速度、停顿、加速由操作者通过力反馈决定。

### 领域定位
- **IEEE TRO**: 机器人领域顶刊，高理论严谨性要求
- **HRI 核心问题**: 人机协作中的控制权分配
- **稳定性保证**: 基于无源性分析的严格稳定性证明

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人方法 | 问题 | 本文解决方案 |
|---------|------|-------------|
| 纯阻抗控制 | 无法强制路径约束 | 相位变量解耦 |
| 轨迹追踪 | 人无控制自由度 | 力引导运动特性 |
| 势场引导 | 可能陷入局部最优 | 单调相位保证全局 |

### 关键贡献点
1. **相位变量 (Phase Variable)**: 将运动参数化为路径相位 $\phi \in [0, 1]$
2. **自适应导纳**: 根据人类操纵性 (Manipulability) 调整引导策略
3. **虚拟能量罐 (Virtual Energy Tank)**: 保证系统无源性与稳定性

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 相位变量概念

**路径参数化**：

给定约束路径 $\mathbf{p}(\phi)$，其中 $\phi \in [0, 1]$。

任意时刻的目标位置由相位决定：
$$
\mathbf{x}_d(t) = \mathbf{p}(\phi(t))
$$

相位动力学由人类力输入驱动：
$$
\dot{\phi} = f(\mathbf{F}_h, \phi)
$$

### 3.2 导纳控制框架

**标准导纳关系**：
$$
\mathbf{M}_d \ddot{\mathbf{x}} + \mathbf{D}_d \dot{\mathbf{x}} = \mathbf{F}_h
$$

**相位耦合导纳**：

将力分解为沿路径切向和法向分量：
- **切向力** → 驱动相位前进/后退
- **法向力** → 被路径约束吸收

$$
\dot{\phi} = \frac{1}{d_\phi} \mathbf{t}(\phi)^T \mathbf{F}_h
$$

其中 $\mathbf{t}(\phi)$ 是路径切向量，$d_\phi$ 是阻尼系数。

### 3.3 稳定性分析

**无源性条件**：

系统从人类输入端口看应为无源：
$$
\int_0^T \mathbf{F}_h^T \dot{\mathbf{x}} \, dt \geq -E_0
$$

**虚拟能量罐**：

引入能量存储变量 $E_{tank}$：
$$
\dot{E}_{tank} = -P_{dissipated} + P_{input}
$$

当 $E_{tank} > 0$ 时允许主动行为，否则切换到纯阻尼模式。

### 3.4 自适应策略

**操纵性感知调整**：

根据人类手臂的操纵性椭球调整导纳参数：
$$
\mathbf{D}_d = f(\mathbf{J} \mathbf{J}^T)
$$

在操纵性差的方向增大阻尼，降低人类负担。

## 4. 实验与验证 (Experiments)

### 实验设置
- **任务**: 沿曲线路径引导（如切割、焊接轨迹）
- **用户研究**: 20 名参与者
- **硬件**: KUKA iiwa 协作机器人

### 关键结果

| 指标 | 固定阻尼 | 自适应阻尼 |
|-----|---------|----------|
| 路径偏差 (mm) | 2.3 | 1.8 |
| 完成时间 (s) | 45.2 | 38.7 |
| 用户满意度 | 3.2/5 | 4.1/5 |
| 感知努力 | 高 | 低 |

## 5. 批判性分析 (Critical Analysis)

### 优势
- **理论严谨**: 基于无源性的稳定性证明
- **物理可解释**: 参数直接对应物理量
- **用户友好**: 自适应降低人类负担

### 局限性
- **路径预定义**: 需要事先给定约束路径
- **单自由度控制**: 人类只控制沿路径的运动
- **刚性假设**: 未考虑柔性接触

### 与 DNPM 项目的关联

> [!note] 潜在借鉴
> 1. **相位变量思想**: 可用于参数化动态操作的"任务进度"
> 2. **稳定性保证**: 虚拟能量罐可用于安全约束
> 3. **人机协作扩展**: 远程遥操作 + 力反馈引导灵巧手

## 6. 对灵巧操作的启发 (Implications)

1. **任务参数化**: 复杂操作可分解为"路径+相位"表示
2. **力反馈遥操作**: 人类通过力控制任务进度，机器人保证执行质量
3. **安全保证**: 无源性分析可扩展到接触丰富场景

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── 阻抗/导纳控制 (Hogan 1985) - 力交互基础
├── 虚拟夹具 (Rosenberg 1993) - 约束引导
└── 能量罐方法 (Franken 2011) - 无源性保证

本论文: Phase-Based Admittance (IEEE TRO 2025)

后续方向:
├── 学习路径约束 - 从演示中提取约束
├── 多路径选择 - 人类选择哪条路径
└── 与 RL 结合 - 自适应参数学习
```

---

**参考文献**:
- Shahriari, E. et al. "Path-Constrained Haptic Motion Guidance via Adaptive Phase-Based Admittance Control." IEEE TRO, 2025.
