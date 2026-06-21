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

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 导纳控制（外力→运动）vs 阻抗控制（运动→力）对偶；临界阻尼 $K_d=2\sqrt{K_p}$
> - [[Dynamics]] — 雅可比任务空间投影（操作空间动力学）；URDF 重力补偿 $g(q)$
> - [[ContactMechanics]] — 接触力估计：方向比幅值重要
>
> **核心技术**: 无传感器力估计 (电流/PWM), 方向相关效率, 导纳控制, 零学习跨具身

## 1. 问题设定与动机

顺应控制的**硬件壁垒**：
- 标准导纳/阻抗控制依赖昂贵的力/力矩传感器或精确力反馈执行器
- RL 顺应控制存在 sim-to-real 差距、缺乏安全保障、产生危险力尖峰

**核心观察**：
1. 现代电机的电流/PWM 信号**固有地包含外部力矩信息**
2. 顺应控制**不需要高精度力幅值**——只需正确的力方向和相关频段的合理精度

## 2. 核心方法

### 2.0 Delta 分析

| 方法 | 力传感器 | 学习/训练 | 跨平台 | 安全性 | 力估计来源 |
|------|:---:|:---:|:---:|:---:|:---:|
| 传统阻抗控制 | ✅ 必需 | 否 | 差 | 好 | 力传感器 |
| RL 顺应 (UniFP) | ❌ | 大量仿真 | 差 | 差（力尖峰） | 隐式 |
| RL 顺应 (FACET) | ❌ | 大量仿真 | 中 | 中 | 隐式 |
| **MCC (本文)** | **❌** | **无** | **好** | **好** | **电流/PWM** |

**核心 Delta**：MCC 将力估计问题从 "需要传感器或需要学习" 简化为 "需要电流读数 + 最小参数标定"——零学习、零力传感器、跨具身形态通用。

### 变量来源追踪

枢纽：**力估计来自电机电流**（$\tau=K_t I$）+ **方向相关效率**（正驱 $\eta$ / 反驱 $\eta^{-1}$）——零学习、无力传感器。

| 变量 | 类型/空间 | 来源阶段 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|----------------|----------|
| $I_{motor}$ | 电流 | 传感/PWM | 力估计来源 | PWM 需低通滤波 ~20Hz 去开关噪声 |
| $K_t$ | scalar | 标定/datasheet | 力矩常数 | 假设线性，忽略磁饱和/温漂 |
| $\eta$ | scalar | 标定（~10min） | 减速器效率 | **正驱 $\eta$ / 反驱 $\eta^{-1}$**；高减速比忽略则偏 >50% |
| $d=\mathrm{sign}(\tau_w\dot{q})$ | ± | 计算 | 功率流方向 | 决定用 $\eta$ 还是 $\eta^{-1}$ |
| $\tau_{ext}=-(r\tau_{load}-\tau_{grav})$ | 力矩 | 计算 | 外部力矩 | $\tau_{grav}$ 用 URDF 标称 |
| $\hat{f}_{ext}$ | 任务空间力 | 正则最小二乘 | 外力分量 | **方向准、幅值粗**（够用） |
| $K_p,K_d=2\sqrt{K_p}$ | 增益 | 超参 | 导纳刚度/阻尼 | 临界阻尼 $\zeta=1$ |

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

### 2.5 核心代码逻辑

```python
import torch
import torch.nn.functional as F

class MCCController:
    """Minimalist Compliance Control — 无力传感器导纳控制"""
    def __init__(self, Kp: float, Kt: float, eta: float, ratio: float):
        self.Kp = Kp
        self.Kd = 2.0 * Kp ** 0.5          # 临界阻尼
        self.Kt = Kt                         # 电机力矩常数
        self.eta = eta                       # 减速器正驱效率
        self.ratio = ratio                   # 减速比

    def estimate_load_torque(self, I_motor: torch.Tensor, power_dir: torch.Tensor) -> torch.Tensor:
        """方向相关效率 → 负载侧力矩"""
        tau_motor = self.Kt * I_motor
        eff = torch.where(power_dir > 0,
                          self.eta * self.ratio,       # 正驱
                          self.ratio / self.eta)        # 反驱
        return eff * tau_motor

    def estimate_external_torque(self, tau_load: torch.Tensor, tau_grav: torch.Tensor) -> torch.Tensor:
        return -(tau_load - tau_grav)

    def compute_task_force(self, tau_ext: torch.Tensor, J: torch.Tensor,
                           u_hat: torch.Tensor, lam: float = 1e-4) -> torch.Tensor:
        """正则化最小二乘 → 任务空间外力分量"""
        Ju = u_hat @ J                       # (1, n_joints)
        f_ext = (Ju @ tau_ext) / (Ju @ Ju.T + lam) * u_hat
        return f_ext

    def admittance_step(self, x: torch.Tensor, dx: torch.Tensor,
                        x_des: torch.Tensor, f_ext: torch.Tensor, dt: float):
        """半隐式 Euler 导纳积分"""
        ddx = self.Kp * (x_des - x) + self.Kd * (0 - dx) + f_ext
        dx_new = dx + ddx * dt
        x_new = x + dx_new * dt
        return x_new, dx_new
```

### 2.6 概念边界与符号陷阱

- **力控无需力传感器**：电流/PWM 含外力信息（频域精度够即可）。
- **方向 > 幅值**：力方向准 + 频域合理 >> 精确力幅值（= Touch Dexterity "二值够用" 同源）。
- **方向相关效率** $\eta$（正驱）vs $\eta^{-1}$（反驱）：高减速比关键，忽略则力矩偏 >50%。
- **准静态假设**：高加速度时惯性项 $M\ddot{q}$ 不可忽略（§5 算法局限）。
- **电流线性假设**：忽略磁饱和/温漂（§5 理论局限）。
- **零学习模型方法**（非 RL）：可解释、跨平台、安全可分析。

## 3. 实验结果

### 3.0 训练/标定细节

> [!note] MCC 是无学习的模型方法，无 RL/ML 训练过程。

- **参数标定**：每台电机仅需辨识 $K_t$（力矩常数）和 $\eta$（减速器效率），共 2 个标量参数
- **QDD 电机**（ARX X5, Unitree G1）：直接从 datasheet 读取 $K_t$，$\eta \approx 1$
- **伺服电机**（Dynamixel, ToddlerBot）：标定 $\eta$ 需要简单正反驱测量，约 10 分钟
- **重力补偿**：全部使用 URDF 标称动力学模型，未做额外辨识

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

### 3.5 Ablation 因果链

| 去掉什么 | 导致什么 | 因为什么机制 |
|---------|---------|------------|
| 去掉 $\hat{f}_{ext}$（无力估计） | 位置误差 22.5→15.9 mm (↑41%) | 无外力前馈，控制器只靠刚性 PD 抵抗接触 |
| 去掉方向效率 ($\eta=1$)（高减速比伺服） | 力矩估计偏差 >50% | 反驱时 $\eta^{-1}$ 放大效应被忽略，力矩被严重低估 |
| 去掉重力补偿 | 静态偏移误差增大 | $\tau_{grav}$ 未抵消，外力估计包含重力分量 |
| 降低 $K_p$（过度顺应） | 位置跟踪退化，自由运动精度下降 | 弹簧力不足以维持期望轨迹 |

## 4. 工程关键细节 (Engineering Tricks)

- **电流滤波**：伺服电机 PWM 信号需低通滤波（截止 ~20 Hz），否则开关噪声污染力矩估计
- **雅可比正则化**：$\lambda \sim 10^{-4}$ 避免奇异位形附近的数值爆炸
- **半隐式 Euler**：比显式 Euler 稳定，比隐式 Euler 便宜——导纳积分的工程最佳实践
- **效率查表**：$\eta$ 实际随负载率变化（非常数），工程中可用 lookup table 或分段线性近似
- **安全限幅**：$\hat{f}_{ext}$ 输出限幅，防止电流噪声瞬态导致的力估计突变

## 5. 核心洞见 (Insights)

1. **力控不需要力传感器**：电流/PWM 信号在频域精度足够时即可驱动稳定顺应控制
2. **方向比幅值重要**：力方向正确 + 频域合理 >> 精确力幅值
3. **高减速比伺服也可以**：方向相关效率模型 ($\eta$ vs $\eta^{-1}$) 解锁了谐波/行星减速器上的力估计
4. **模型方法 > RL 方法**：显式力矩估计在安全性、可解释性、跨平台泛化上全面优于黑盒 RL

### 5.1 局限性深度分析

| 维度 | 局限 | 替代方案 |
|------|------|--------|
| **理论** | 假设电机力矩-电流线性关系，忽略磁饱和与温度漂移 | 在线自适应 $K_t$ 估计（EKF） |
| **算法** | 准静态假设——高加速度时惯性项 $M(q)\ddot{q}$ 不可忽略 | 加入加速度前馈补偿 |
| **工程** | 伺服 PWM 分辨率有限（Dynamixel 10-bit），力矩分辨率受限 | QDD 电机 + 高分辨率电流传感器 |

### 5.2 对转笔 / Sim-to-Real 的启发

- **LEAP Hand MCC**：论文已在 LEAP Hand 上验证，可直接作为灵巧手转笔的底层力控方案——无需力传感器即可实现指尖顺应
- **Sim-to-Real Gap**：方向效率模型 ($\eta$ vs $\eta^{-1}$) 应纳入仿真器建模，否则仿真中力矩输出与真机系统性偏差
- **与 RL 互补**：MCC 提供可靠的底层力估计 → RL 策略无需学习接触力建模 → 简化训练、提高迁移性

## 6. 与知识体系的联系

### 与 [[ControlTheory]] 的联系
- 导纳控制 (外力→运动) 与阻抗控制 (运动→力) 的对偶体系——MCC 选择导纳控制是因为大多数无力传感器平台只有位置控制
- 弹簧-质量-阻尼器模型的临界阻尼设计 $K_d = 2K_p^{1/2}$，对应二阶系统阻尼比 $\zeta = 1$，特征方程 $s^2 + 2\sqrt{K_p}s + K_p = 0$ 的重根条件
- 导纳因果关系：$f_{ext} \xrightarrow{\text{admittance}} \Delta x_{ref} \xrightarrow{\text{IK}} q_{target}$

### 与 [[Dynamics]] 的联系
- 雅可比映射 $\hat{f}_{ext} = (J_p^T)^{\dagger} \tau_{ext}$ 将关节力矩投影到任务空间——正是 [[Dynamics|操作空间动力学]] 中的核心运算
- 重力补偿项 $\tau_{grav} = g(q)$ 来自 [[Dynamics|Lagrangian 动力学]] 的势能梯度 $g(q) = \frac{\partial V}{\partial q}$

### 与 [[ContactMechanics]] 的联系
- 接触力估计精度直接影响顺应行为质量——MCC 证明方向正确即可：$\hat{f}_{ext} / \|\hat{f}_{ext}\|$ 的精度比 $\|\hat{f}_{ext}\|$ 更重要
- OCHS (Optimally-Conditioned Hybrid Servoing) 用于力-速度混合控制

### 与灵巧操作的关联
- **LEAP Hand 上的手内旋转**：MCC + OCHS 实现无力传感器的灵巧手接触丰富操作
- **与 DNPM 项目的潜在联系**：LEAP Hand 的 Dynamixel 伺服 ≈ 灵巧手原型→MCC 可作为底层力控方案

## 7. 跨方法对比

| 维度 | MCC (本文) | FACET (RL阻抗跟踪) | VICES (RL变阻抗) | 传统力/力矩控制 |
|------|-----------|-------------------|-----------------|---------------|
| 力传感器 | ❌ | ❌ | ❌ | ✅ 必需 |
| 学习/训练 | 无 | PPO 大规模仿真 | SAC 仿真 | 无 |
| 力估计精度 | 中（方向准、幅值粗） | 隐式（不显式估计） | 隐式 | 高 |
| 跨平台通用性 | 高（4 种平台验证） | 中（腿式为主） | 中（单臂为主） | 低（需标定） |
| 安全保障 | 显式可分析 | 通过 DR 隐式 | 通过阻抗限幅 | 显式 |
| 动态操作 | 仅准静态 | 可动态（冲击存活） | 中速 | 可动态 |

> [!note] impedance 簇：学习程度谱 + 力感知来源谱（MCC 是"零学习 + 电流估力"极）
> MCC 占据 impedance 簇的**零学习 + 无力传感器**极，与 RL 方法对立，揭示两条谱：
> **① 学习程度谱**：零学习模型（MCC）→ 凸优化辨识（[[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking\|Data-Driven VIC]]）→ RL（[[Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks\|VICES]]/[[FACET - Force-Adaptive Control via Impedance Reference Tracking\|FACET]]）。
> **② 力感知来源谱**：力传感器（传统）→ **电流/PWM 物理映射（MCC）** → 本体历史学习（隐式，[[DexNDM: Closing the Reality Gap for Dexterous In-Hand Rotation via Joint-wise Neural Dynamics Model\|DexNDM]]/[[Learning Agile and Dynamic Motor Skills for Legged Robots\|Learning Agile]]）。
> **critical-thinking insight——模型方法 > RL（在顺应控制上）**：MCC 位置误差 15.9mm < FACET 22.4mm < UniFP 57.8mm——**简单物理模型 + 2 参数标定全面超越大规模 RL**（且安全/可解释/跨 4 平台）。这是对"RL 万能"的反例：问题有清晰物理结构（电流→力矩）时，物理模型优于黑盒。
> **"方向 > 幅值"连 Touch Dexterity**：MCC"力方向准 >> 力幅值精确"与 [[Touch Dexterity - Rotating without Seeing Towards In-hand Dexterity through Touch\|Touch Dexterity]]"二值触觉够用"同源——**低精度但对的信息（方向/接触模式）常常够用**，是接触控制/感知的反直觉共性。

## 8. 局限与未来方向

- 需要电机参数标定（力矩常数 $K_t$）
- 高频振动和电气噪声需滤波
- 温度漂移导致参数漂移（与 [[sim2real|硬件Gap分析]] 温度漂移分析一致）
- 当前仅支持准静态/低速接触——高动态操作（如 DNPM 的甩转）需探索
