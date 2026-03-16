---
tags:
  - paper
  - control
  - manipulation
  - compliance
  - sim-to-real
aliases:
  - MCC
  - Minimalist Compliance Control
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (Stanford)
paper-pdf: "[[Papers/Minimalist Compliance Control.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
---

# Minimalist Compliance Control

> [!abstract] 核心贡献
> 提出**最小主义顺应控制**：仅利用电机电流或 PWM 信号（无需力/力矩传感器、无需学习）估计外部力矩，驱动任务空间导纳控制器实现顺应行为。方法**跨具身形态通用**（机械臂、灵巧手、人形机器人）且**即插即用**（兼容 VLM 策略、模仿学习、基于模型的规划）。

## 1. 问题设定与动机

顺应控制的**硬件壁垒**：
- 标准导纳/阻抗控制依赖昂贵的力/力矩传感器或精确力反馈执行器
- RL 顺应控制存在 sim-to-real 差距、缺乏安全保障、产生危险力尖峰

**核心观察**：
1. 现代电机的电流/PWM 信号**固有地包含外部力矩信息**
2. 顺应控制**不需要高精度力幅值**——只需正确的力方向和相关频段的合理精度

## 2. 核心方法

### 2.1 弹簧-质量-阻尼器模型

$$m\ddot{x} = K_p(x_{des} - x) + K_d(\dot{x}_{des} - \dot{x}) + f_{cmd} + f_{ext}$$

其中 $m=1$ (单位质量简化), $K_d = 2K_p^{1/2}$ (临界阻尼)。

### 2.2 电机力矩估计

**QDD 电机** (准直驱)：$\tau_{motor} = K_t \cdot I_{motor}$（电流 → 力矩，直接线性映射）

**伺服电机** (高减速比 >200:1)：引入**方向相关效率** (Direction-Dependent Efficiency)

$$\tau_{load} = \begin{cases} \eta \cdot r \cdot \tau_{motor} & d > 0 \text{ (正驱)} \\ \eta^{-1} \cdot r \cdot \tau_{motor} & d \leq 0 \text{ (反驱)} \end{cases}$$

- 正驱 ($d>0$)：电机驱动负载，$\eta$ 表示功率损耗
- 反驱 ($d \leq 0$)：外力反驱电机，$\eta^{-1}$ 表示制动放大
- $d$ 由功率流方向 $\tau_w \dot{q}$ 的符号决定

> [!tip] 与 [[sim2real|硬件 Sim-to-Real Gap 分析]] 的联系
> 方向相关效率模型直接对应 sim2real.md §3 中减速器效率非对称性分析。谐波减速器正反驱效率差异 ($\eta_{forward} \neq \eta_{backward}$) 正是仿真中经常忽略的关键 Gap 来源。MCC 证明了**仅需最小参数辨识**即可利用此效率模型实现力控。

### 2.3 外部力矩隔离

$$\tau_{ext} = -(r \cdot \tau_{load} - \tau_{grav})$$

沿选定轴 $\hat{u}$ 估计对应力分量（正则化最小二乘避免病态雅可比逆）：

$$\hat{f}_{ext}^p = \frac{(\hat{u}^T J_p) \tau_{ext}}{(\hat{u}^T J_p)(\hat{u}^T J_p)^T + \lambda} \hat{u}$$

### 2.4 导纳控制执行

半隐式 Euler 积分弹簧-质量-阻尼器动力学 → 更新任务空间运动参考 → 逆运动学求解关节目标。

## 3. 实验结果

### 验证平台
- **ARX X5 机械臂** (QDD 电机)
- **Unitree G1 人形** (QDD 电机)
- **ToddlerBot** (Dynamixel 伺服)
- **LEAP Hand** (Dynamixel 伺服)

### 定量对比

| 方法 | 位置误差 (mm) | 姿态误差 (rad) |
|------|:---:|:---:|
| UniFP (RL) | 57.8 ± 30.2 | 0.147 ± 0.119 |
| FACET (RL) | 22.4 ± 11.0 | 0.151 ± 0.087 |
| Ours w/o $\hat{f}_{ext}$ | 22.5 ± 9.6 | 0.082 ± 0.040 |
| **Ours** | **15.9 ± 5.1** | **0.048 ± 0.043** |

### 关键发现
- MCC 在**所有指标**上超越 RL 基线 (UniFP, FACET)
- 即使在高减速比伺服 (>200:1) 上也能可靠估计力矩
- 零样本跨具身形态泛化（臂→手→人形）
- 与 VLM、扩散策略、OCHS 模型规划均即插即用

## 4. 核心洞见 (Insights)

1. **力控不需要力传感器**：电流/PWM 信号在频域精度足够时即可驱动稳定顺应控制
2. **方向比幅值重要**：力方向正确 + 频域合理 >> 精确力幅值
3. **高减速比伺服也可以**：方向相关效率模型 ($\eta$ vs $\eta^{-1}$) 解锁了谐波/行星减速器上的力估计
4. **模型方法 > RL 方法**：显式力矩估计在安全性、可解释性、跨平台泛化上全面优于黑盒 RL

## 5. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
- 导纳控制 (外力→运动) 与阻抗控制 (运动→力) 的对偶体系——MCC 选择导纳控制是因为大多数无力传感器平台只有位置控制
- 弹簧-质量-阻尼器模型的临界阻尼设计 $K_d = 2K_p^{1/2}$

### 与 [[Dynamics]] 的联系
- 雅可比映射 $J_p$ 将关节力矩投影到任务空间——正是 [[Dynamics#8. 腱驱动动力学|腱驱动动力学]] 中的核心运算
- 重力补偿 $\tau_{grav}$ 需要动力学模型

### 与 [[ContactMechanics]] 的联系
- 接触力估计精度直接影响顺应行为质量——MCC 证明方向正确即可
- OCHS (Optimally-Conditioned Hybrid Servoing) 用于力-速度混合控制

### 与灵巧操作的关联
- **LEAP Hand 上的手内旋转**：MCC + OCHS 实现无力传感器的灵巧手接触丰富操作
- **与 DNPM 项目的潜在联系**：LEAP Hand 的 Dynamixel 伺服 ≈ 灵巧手原型→MCC 可作为底层力控方案

## 6. 局限与未来方向

- 需要电机参数标定（力矩常数 $K_t$）
- 高频振动和电气噪声需滤波
- 温度漂移导致参数漂移（与 [[sim2real|硬件Gap分析]] §3 温度漂移分析一致）
- 当前仅支持准静态/低速接触——高动态操作（如 DNPM 的甩转）需探索
