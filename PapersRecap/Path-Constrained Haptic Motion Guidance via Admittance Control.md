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
> - [[ControlTheory]] - 导纳控制作为阻抗控制的对偶
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

### 3.5 核心控制逻辑伪代码

```python
import numpy as np

def phase_admittance_controller(path, F_human, state, params, dt=0.001):
    """相位自适应导纳控制器 — 核心循环"""
    phi, x, dx = state['phi'], state['x'], state['dx']
    D_phi, D_d, E_tank = params['D_phi'], params['D_d'], state['E_tank']

    # 1. 路径切向/法向分解
    t_vec = path.tangent(phi)   # dp/dφ 归一化
    n_vec = path.normal(phi)

    # 2. 切向力驱动相位前进
    F_tangent = np.dot(F_human, t_vec)
    phi_dot = F_tangent / D_phi

    # 3. 目标位置 = 路径上相位对应点
    x_desired = path.evaluate(phi + phi_dot * dt)

    # 4. 虚拟能量罐: 保证无源性
    P_dissipated = D_d * np.linalg.norm(dx)**2
    P_injected = np.dot(F_human, dx)
    E_tank += (P_injected - P_dissipated) * dt

    # 5. 能量罐耗尽 → 纯阻尼安全模式
    if E_tank <= 0:
        F_cmd = -D_d * dx
    else:
        F_cmd = params['K_path'] * (x_desired - x) - D_d * dx

    # 6. 操纵性自适应
    J = state['jacobian']
    manip = np.sqrt(max(np.linalg.det(J @ J.T), 1e-6))
    D_phi_adaptive = D_phi / manip

    return F_cmd, {'phi': phi + phi_dot * dt, 'E_tank': max(E_tank, 0)}
```

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

### 实验调参细节

| 维度 | 设定 |
|------|------|
| **控制频率** | 1 kHz (KUKA iiwa 标准) |
| **路径离散化** | 500 个插值点 (cubic spline) |
| **阻尼参数 D_d** | 50–200 Ns/m |
| **相位阻尼 D_φ** | 100–500 |
| **能量罐初值** | 5 J |
| **用户实验** | 20人 × 3 conditions × 5 trials = 300 trials |
| **路径类型** | S 型曲线, 螺旋线, 直角拐弯 |

### Ablation 分析

| 消融项 | 路径偏差 | 用户满意度 | 因果机制 |
|--------|---------|-----------|----------|
| 去掉自适应阻尼 | 2.3mm (↑28%) | 3.2/5 (↓22%) | 力薄弱方向阻尼过高 → 用户额外发力 → 疲劳+偏差 |
| 去掉能量罐 | 1.5mm | 4.0/5 | 失去无源性证明 → 极端交互可能不稳定 |
| 固定相位速度 | 2.0mm (↑11%) | 2.8/5 (↓32%) | 用户无法控速度 → 强制同步 → 心理负担大 |
| 去掉法向约束 | 4.1mm (↑128%) | 2.5/5 | 路径偷离不受限 → 与自由导纳无区别 |

### 工程实践要点 (Engineering Tricks)

1. **能量罐初值**: 过小→频繁切换阻尼模式（抖动）；过大→无源性约束松弛。推荐设为任务总能量 10%
2. **路径插值平滑化**: cubic spline 比线性插值重要——线性插值在拐点处切向量不连续导致相位动力学跳变
3. **阻尼切换滤波**: 自适应阻尼变化需加一阶低通滤波（τ ≈ 50ms），避免操纵性椭球快速变化导致力矩突变
4. **力传感器偏置补偿**: KUKA iiwa FT 传感器受温漂影响，每次实验前需零点标定

## 5. 批判性分析 (Critical Analysis)

### 优势
- **理论严谨**: 基于无源性的稳定性证明
- **物理可解释**: 参数直接对应物理量
- **用户友好**: 自适应降低人类负担

### 局限性深度分析

**理论层面**:
- **无源性 vs 最优性**: 能量罐保证稳定但牺牲性能——主动引导能量被严格限制
- **单参数相位**: 复杂三维路径用单标量 φ 参数化，分支/交叉路径不可表示
- **替代方案**: [[Optimization]] 中的 MPC 框架可在线优化相位策略，放松无源性为软约束

**算法层面**:
- **路径预定义**: 需事先给定约束路径，不适用于在线路径生成
- **单自由度控制**: 人类只控制沿路径前进/后退，无法主动偏离——对探索性任务限制大
- **替代方案**: 势场引导 (APF) 允许多自由度偏离，但缺乏稳定性保证

**工程层面**:
- **刚性假设**: 未考虑柔性接触（如软组织手术导航）→ 需耦合阻抗模型
- **操纵性估计噪声**: 人体关节角度估计不精确 → 操纵性椭球计算有误差 → 自适应阻尼抖动

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

## 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **路径约束的转笔应用**: 将转笔的理想轨迹作为「路径约束」，用 admittance 控制引导策略的探索范围，可加速早期 RL 训练的收敛
2. **相位自适应**: 本文的 phase-adaptive 控制与转笔中的动作阶段（snap/rotate/catch）切换有类似结构，可借鉴其平滑的相位越迁机制
3. **局限**: 本文面向工业扮演/操作家场景，所需带宽/力度与灵巧手高速操作差异大
