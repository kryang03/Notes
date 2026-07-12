---
tags:
  - paper
  - variable-impedance
  - reinforcement-learning
  - action-space
  - contact-manipulation
aliases:
  - VICES
  - Variable Impedance Control in End-Effector Space
paper-year: 2019
read-date: 2026-01-31
venue: ICRA 2019
paper-pdf: "[[Papers/Variable Impedance Control in End-Effector Space:.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ReinforcementLearning]]"
  - "[[ContactMechanics]]"
  - "[[Dynamics]]"
---

# Variable Impedance Control in End-Effector Space: An Action Space for Reinforcement Learning in Contact-Rich Tasks

> [!abstract] 核心概要
> 提出 **VICES (Variable Impedance Control in End-Effector Space)** 作为接触密集型任务 RL 的动作空间。动作 = 末端执行器位移 + 可变阻抗增益，实现**样本效率高、能耗低、跨机器人迁移**的策略学习。

> [!tip] 与理论基础的关联
> - [[ControlTheory]] — 阻抗控制（弹簧-阻尼）理论；从刚性位置控制到柔顺力控制
> - [[ReinforcementLearning]] — 动作空间设计对接触任务 RL 的样本效率/迁移影响
> - [[ContactMechanics]] — 接触任务力控制需求；接触刚度与控制刚度串联
> - [[Dynamics]] — 操作空间动力学 (Khatib)：末端空间动力学补偿、动态一致性
>
> **核心技术**: Variable Impedance Control, End-Effector Action Space, 操作空间动力学补偿, Sim-to-Real 迁移

---

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
**动作空间的选择 = 闭环控制的空间 → 选对动作空间，接触任务学习事半功倍**

### 直观隐喻
想象你在学习擦玻璃：
- **关节力矩动作空间**：你需要直接控制每块肌肉的力量（太难！）
- **关节位置动作空间**：你只能控制胳膊的角度，无法感知玻璃的存在
- **VICES 动作空间**：你控制"手想去哪里"+"遇到阻力时多软/硬"

第三种方式最自然——你决定方向和柔顺度，底层控制器处理肌肉细节。

### 领域定位
```
RL Action Space Evolution
        ↓
Joint Torque (raw, difficult)
        ↓
Joint Position/Velocity (easier, limited)
        ↓
End-Effector Position (task-relevant)
        ↓
████████████████████████████████████████
█  VICES (2019)                        █
█  • 末端空间位移 + 可变阻抗增益        █
█  • 接触任务的自然表达                 █
█  • 跨机器人迁移能力                   █
████████████████████████████████████████
        ↓
未来: 触觉引导的阻抗调节
```

---

## 2. 核心创新与贡献 (Contributions & Novelty)

### 问题定义

**控制系统分层**：
$$u = f \circ g(o)$$

- $g(o): O \to A$ — 外环：观测 → 参考信号（**策略学习的对象**）
- $f(a): A \to U$ — 内环：参考信号 → 执行器指令（**底层控制器**）

**核心问题**：什么样的 $A$（动作空间）最适合接触密集型任务的 RL？

### Delta 分析

| 动作空间 | 样本效率 | 能量效率 | 安全性 | 迁移性 |
|---------|---------|---------|-------|-------|
| 关节力矩 | 低 | 低 | 差 | 差 |
| 关节位置 | 中 | 中 | 中 | 差 |
| 关节可变阻抗 | 中 | 高 | 好 | 中 |
| 末端位置 | 高 | 中 | 中 | 好 |
| **VICES** | **高** | **高** | **好** | **好** |

### 关键贡献

1. **C1**: 首次系统比较 RL 中不同动作空间对接触任务的影响
2. **C2**: 提出 VICES——末端空间可变阻抗动作空间
3. **C3**: 证明 VICES 实现 sim-to-real 和跨机器人迁移

---

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.0 变量来源追踪

枢纽：**action = (位姿增量 $\Delta x$, 刚度 $K$)**——"去哪 + 多软硬"；$K(s)$ 是状态依赖的物理阻抗元控制；底层操作空间控制器处理动力学补偿。

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $\Delta x$ | $\mathbb{R}^6$ | 策略输出（tanh×MAX） | 是 | 末端位姿增量（位置+轴角） | 限幅防跳变；轴角 $\|\omega\|\to\pi$ 不连续 |
| $K_{diag}$ | $\mathbb{R}^6$ | 策略输出（sigmoid→[Kmin,Kmax]） | 是 | 对角刚度 | **状态依赖元控制 $K(s)$**；对角 only，无耦合 $K_{ij}$ |
| $D=2\sqrt{K}$ | $\mathbb{R}^6$ | 计算（临界阻尼） | — | 阻尼 | 随 $K$ 自动跟随 |
| $F=K\Delta x+D\dot e$ | $\mathbb{R}^6$ | 计算 | — | 操作空间力 | 弹簧-阻尼律 |
| $\Lambda=(JM^{-1}J^T)^{-1}$ | $6\times6$ | 计算（需 $M$） | — | 操作空间惯性 | **动态一致性**根源；奇异位形需正则 |
| $\tau=J^T\Lambda F+\mu+p$ | 关节力矩 | 计算 | — | 底层输出 | 需精确 $M,C,g$ |

### 3.1 阻抗控制回顾

**目标**：让机器人末端表现得像弹簧-阻尼系统

$$F = K(x_{des} - x) + D(\dot{x}_{des} - \dot{x})$$

其中：
- $K$: 刚度矩阵（6×6，位置+姿态）
- $D$: 阻尼矩阵
- $x_{des}$: 期望位姿
- $F$: 施加在环境上的力

### 3.2 VICES 动作定义

**动作空间**：
$$a = (\Delta x, K_{diag})$$

- $\Delta x \in \mathbb{R}^6$: 末端位姿增量（位置 + 旋转）
- $K_{diag} \in \mathbb{R}^6$: 对角刚度增益

**为什么只用对角？** 
- 简化动作空间维度
- 实践中足够表达大多数任务约束
- 非对角项可通过任务坐标系对齐处理

### 3.3 底层控制器

**操作空间动力学**（Khatib, 1987）：
$$\tau = J^T \Lambda (K \Delta x + D \dot{e}) + \mu(q, \dot{q}) + p(q)$$

其中：
- $J$: 雅可比矩阵
- $\Lambda = (J M^{-1} J^T)^{-1}$: 操作空间惯性矩阵
- $\mu$: 科里奥利/离心力补偿
- $p$: 重力补偿

> [!important] 动态一致性
> 这个公式保证末端空间的动力学**独立于**关节空间冗余度，使策略可以迁移到不同机器人。

### 3.4 为什么 VICES 适合接触任务？

**场景分析**：

1. **自由空间运动**（Path Following）
   - 需要：精确位置跟踪
   - VICES：高刚度 + 轨迹增量

2. **运动学约束**（Door Opening）
   - 需要：沿约束方向顺从
   - VICES：约束方向低刚度，其他方向高刚度

3. **持续接触**（Surface Wiping）
   - 需要：法向力控制 + 切向运动
   - VICES：法向低刚度（顺从）+ 切向高刚度（运动）

```
┌─────────────────────────────────────────┐
│  Surface Wiping 任务                    │
├─────────────────────────────────────────┤
│                                         │
│     ↑ 法向 (z)                          │
│     │  K_z = 低 (顺从接触)              │
│     │                                   │
│     ├───→ 切向 (x,y)                    │
│        K_xy = 高 (精确运动)             │
│                                         │
│  策略学习：                              │
│  - Δx, Δy: 擦拭轨迹                     │
│  - K_z: 根据接触力调节                  │
│                                         │
└─────────────────────────────────────────┘
```

---

### 3.5 概念边界与符号陷阱

- **action = ($\Delta x$, $K$)**：位姿增量 + 刚度——"去哪 + 多软硬"，非力矩/绝对位置。
- **对角 $K$ only**：无法表达耦合力场 $K_{ij}$（§5 局限，可 Cholesky $K=LL^T$）。
- **底层需精确动力学** $M,C,g$（操作空间补偿）；去掉则 Door Opening 失败（§4 消融）。
- **策略 20Hz / 阻抗 1kHz 分离**：避免策略延迟污染力控质量（= EvoControl 双层频率的 impedance 版）。
- **$D=2\sqrt{K}$ 临界阻尼**随 $K$ 自动跟随、保无振荡。
- **轴角姿态 $\|\omega\|\to\pi$ 不连续**：可用四元数/旋转矩阵。

## 4. 实验与验证 (Experiments)

### 4.1 实验设置

**任务**：
1. **Path Following**：无接触轨迹跟踪
2. **Door Opening**：有运动学约束
3. **Surface Wiping**：持续接触

**比较的动作空间**：
- Joint Torque (JT)
- Joint Position (JP)
- Joint Velocity (JV)
- Joint Variable Impedance (JVI)
- End-Effector Position (EEP)
- **VICES** (proposed)

**RL 算法**：SAC (Soft Actor-Critic)

### 4.1.1 训练细节

- **网络结构**：2 层 MLP (256 units)，ReLU 激活
- **RL 算法**：SAC（自动温度调节 $\alpha$）
- **学习率**：$3 \times 10^{-4}$（actor & critic 共享）
- **Replay buffer**：$10^6$ transitions
- **Batch size**：256
- **折扣因子**：$\gamma = 0.99$
- **训练步数**：$10^6$ 环境步
- **仿真环境**：MuJoCo，7-DoF Sawyer / 6-DoF UR5
- **控制频率**：20 Hz（策略）；底层阻抗控制 1 kHz
- **奖励函数**：任务相关（轨迹误差 + 能量惩罚 + 接触力惩罚）

### 4.2 主要结果

| 任务 | JT | JP | JVI | EEP | **VICES** |
|-----|----|----|-----|-----|----------|
| Path Following | 低 | 中 | 中 | 高 | **高** |
| Door Opening | 低 | 低 | 中 | 中 | **高** |
| Surface Wiping | 低 | 低 | 中 | 中 | **高** |

### 4.3 关键发现

1. **样本效率**：VICES 在所有任务上收敛最快
2. **能量效率**：VICES 消耗能量最低（可变阻抗避免过度刚性）
3. **安全性**：VICES 接触力最小（顺从控制）
4. **迁移性**：VICES 策略可直接迁移到不同机器人

### 4.4 Sim-to-Real 迁移

### 4.5 Ablation 因果链

| 去掉什么 | 导致什么 | 因为什么机制 |
|---------|---------|------------|
| 可变阻抗 → 固定刚度 | 能耗 ↑ 2-3×，接触力 ↑ | 无法适应接触/自由空间切换，全程高刚度浪费能量 |
| 末端空间 → 关节空间阻抗 (JVI) | 样本效率 ↓，迁移性丧失 | 策略需额外学习冗余解析，动作语义与任务不对齐 |
| 动力学补偿 ($\Lambda, \mu, p$) → PD only | Door Opening 失败率 ↑ | 未补偿的动力学耦合使末端阻抗偏离期望值 |
| 对角 $K$ → 标量 $K$ | Surface Wiping 法/切向无法独立控制 | 单一刚度无法表达方向性顺从 |

### 4.6 工程关键细节 (Engineering Tricks)

- **刚度范围**：$K_{min}=10, K_{max}=1000$ N/m，sigmoid 输出保证正定
- **阻尼设计**：$D = 2\sqrt{K}$（临界阻尼），K 变化时 D 自动跟随
- **位姿增量限幅**：$\|\Delta x\| \leq 2$ cm/step，防止策略输出跳变
- **旋转表示**：使用轴角 $\omega \in \mathbb{R}^3$ 而非欧拉角，避免万向锁
- **操作空间惯性正则化**：$\Lambda = (JM^{-1}J^T + \epsilon I)^{-1}$，避免奇异位形附近数值爆炸
- **控制频率分离**：策略 20 Hz → 阻抗控制 1 kHz，避免策略延迟污染力控质量

**结果**：
- VICES 策略从仿真直接部署到真实 Sawyer 机器人
- 无需额外训练或微调
- 成功完成 door opening 和 surface wiping

**原因**：
- 操作空间动力学补偿了机器人差异
- 可变阻抗提供了对不确定性的鲁棒性

---

## 5. 批判性分析 (Critical Analysis)

### 优势
- **样本效率**：任务相关的动作空间简化探索
- **能量效率**：可变阻抗避免不必要的刚性
- **安全性**：接触力自然受限
- **迁移性**：动力学补偿使策略跨机器人通用

### 局限性

| 维度 | 局限 | 替代方案 |
|------|------|--------|
| **理论** | 仅对角刚度，无法表达耦合力场 $K_{ij}, i \neq j$ | SPD 参数化：$K = LL^T$（Cholesky） |
| **算法** | 底层控制器需精确动力学模型 $M(q), C(q,\dot{q}), g(q)$ | 自适应控制或残差动力学补偿 |
| **工程** | 姿态用轴角在 $\|\omega\| \to \pi$ 时不连续 | 四元数/旋转矩阵表示 |
| **范围** | 仅单臂验证，灵巧手高维扩展未探索 | 分层控制：手指级 VICES + 手腕级协调 |

### 5.2 对转笔 / Sim-to-Real 的启发

- **灵巧手 VICES**：每根手指定义独立 $(\Delta x_{tip}, K_{tip})$，转笔 snap 阶段高 $K$ 发力、旋转阶段低 $K$ 柔顺滑动
- **Sim-to-Real 鲁棒性**：操作空间动力学补偿抵消机器人差异，可变阻抗为模型不确定性提供天然鲁棒性
- **腱驱动刚度映射**：灵巧手关节刚度由腱张力决定 $K_j = R^T \text{diag}(k_t) R$，VICES 刚度输出需通过腱映射转换

### 与其他方法的对比

| 特性 | VICES | Residual LfD | 纯阻抗控制 |
|-----|-------|-------------|----------|
| 学习目标 | 轨迹+刚度 | 轨迹修正 | 无（手动调） |
| 先验知识 | 无需演示 | 需要演示 | 需要任务知识 |
| 适应性 | 策略适应 | 残差适应 | 固定刚度 |

---

## 6. 对灵巧操作的启发 (Implications)

### 扩展到灵巧手

```
单臂 VICES:
  动作 = (末端位移, 末端刚度)
  维度 = 6 + 6 = 12

灵巧手 VICES:
  动作 = (指尖位移, 指尖刚度) × 5 fingers
  维度 = (6 + 6) × 5 = 60
  
  或者：
  动作 = (关节位移, 关节刚度)
  维度 = 24 + 24 = 48 (for typical hand)
  
挑战：
  - 高维动作空间
  - 手指间协调
  - 腱驱动的刚度映射
```

### 与其他论文的联系

- **DexNDM**：VICES 的刚度调节可结合 DexNDM 的关节级动力学
- **DexTrack**：跟踪控制器可使用 VICES 动作空间
- **Residual LfD**：残差可以是刚度调节，而非仅位置修正

---

## 7. 演进脉络定位 (Evolution Context)

```
Robot Control Paradigms
        ↓
Position Control (PD)
        ↓
Force Control (explicit force tracking)
        ↓
Hybrid Position/Force Control (Raibert-Craig)
        ↓
Impedance Control (Hogan, 1985)
├── Fixed impedance
└── Scheduled impedance (time-varying)
        ↓
████████████████████████████████████████
█  VICES (2019)                        █
█  • RL 学习可变阻抗                    █
█  • 末端空间动作                       █
█  • 自动适应任务约束                   █
████████████████████████████████████████
        ↓
未来: 触觉引导 + 学习的阻抗调节
```

---

## 8. 核心代码逻辑

```python
class VICESController:
    """变阻抗末端空间控制器"""
    
    def __init__(self, robot_model):
        self.robot = robot_model
        self.D = compute_critical_damping()  # 临界阻尼
        
    def compute_torque(self, x_current, x_desired, K, dx_current):
        """计算关节力矩"""
        # 1. 位置误差
        e = x_desired - x_current
        de = -dx_current  # 假设期望速度为 0
        
        # 2. 操作空间力
        F = K @ e + self.D @ de
        
        # 3. 雅可比转换
        J = self.robot.jacobian()
        
        # 4. 动力学补偿
        M = self.robot.mass_matrix()
        Lambda = np.linalg.inv(J @ np.linalg.inv(M) @ J.T)
        mu = self.robot.coriolis()
        p = self.robot.gravity()
        
        # 5. 关节力矩
        tau = J.T @ Lambda @ F + mu + p
        
        return tau


class VICESPolicy(nn.Module):
    """VICES 动作空间的策略网络"""
    
    def __init__(self, obs_dim):
        super().__init__()
        self.backbone = MLP(obs_dim, 256)
        self.delta_x_head = nn.Linear(256, 6)  # 位姿增量
        self.stiffness_head = nn.Linear(256, 6)  # 刚度增益
        
    def forward(self, obs):
        features = self.backbone(obs)
        
        # 位姿增量 (bounded)
        delta_x = torch.tanh(self.delta_x_head(features)) * MAX_DELTA
        
        # 刚度增益 (positive, bounded)
        K_diag = torch.sigmoid(self.stiffness_head(features)) * (K_MAX - K_MIN) + K_MIN
        
        return delta_x, K_diag


# RL 训练循环
def train_vices_policy(env, policy):
    for episode in range(n_episodes):
        obs = env.reset()
        x_desired = env.get_ee_pose()
        
        while not done:
            # 策略输出
            delta_x, K_diag = policy(obs)
            
            # 更新期望位姿
            x_desired = x_desired + delta_x
            K = torch.diag(K_diag)
            
            # 底层控制器
            tau = vices_controller.compute_torque(
                env.get_ee_pose(),
                x_desired,
                K,
                env.get_ee_velocity()
            )
            
            # 执行
            obs, reward, done = env.step(tau)
```

---

## 9. 与 Foundation 的数学联系

### 与 [[ControlTheory]] 的联系
阻抗因果关系：$F = Z(s) \cdot V(s)$，广义阻抗 $Z(s) = Ms^2 + Ds + K$。VICES 让 RL 学习 $K$，使 $Z(s)$ 随任务动态变化。临界阻尼条件 $D = 2\sqrt{MK}$ 保证无振荡收敛。

### 与 [[ReinforcementLearning]] 的联系
动作空间设计直接影响 MDP 的有效维度和探索效率。末端空间阻抗动作将 $|\mathcal{A}| = n_{joints}$ 压缩到 $|\mathcal{A}| = 12$（6 位姿 + 6 刚度），且动力学补偿使转移函数 $T(s'|s,a)$ 对机器人参数更不变。

### 与 [[Dynamics]] 的联系
操作空间惯性矩阵 $\Lambda = (JM^{-1}J^T)^{-1}$ 实现**动态一致性**：末端力 $F$ 不在零空间方向产生运动，即零空间投影 $N = I - J^\dagger J$ 与 $F$ 解耦。

### 与 [[ContactMechanics]] 的联系
接触刚度 $K_c$ 与控制刚度 $K$ 的串联等效：$K_{eff} = \frac{K \cdot K_c}{K + K_c}$。当 $K \ll K_c$ 时 $K_{eff} \approx K$（控制器主导）；当 $K \gg K_c$ 时 $K_{eff} \approx K_c$（接触主导）。

## 10. 跨方法对比

| 维度 | VICES | [[FACET - Force-Adaptive Control via Impedance Reference Tracking\|FACET]] | [[Minimalist Compliance Control\|MCC]] | [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking\|Data-Driven VI]] |
|------|-------|-------|-----|---------------|
| 阻抗参数来源 | RL 学习 | RL 跟踪参考模型 | 无（固定参数） | 凸优化辨识 |
| 动作空间 | $\Delta x + K$ | $x_{des} + K_p + K_d$ | 无（非学习） | N/A（非 RL） |
| 力传感器 | 不需要 | 不需要 | 不需要 | 需要（数据采集） |
| 验证任务 | 单臂接触 | 腿式行走 | 多平台力控 | 假肢行走 |
| 核心优势 | 样本效率+迁移 | 力自适应+安全 | 零学习+通用 | 零调参+全局最优 |

> [!note] impedance 簇定位 + 阻抗刚度 $K(s)$ 加入"状态依赖元控制 $m(s)$"家族
> VICES 是 impedance/compliance 簇的锚点——RL 学可变阻抗作 action space（簇内对比见 §10：[[FACET - Force-Adaptive Control via Impedance Reference Tracking\|FACET]] 跟踪参考模型 / [[Minimalist Compliance Control\|MCC]] 固定参数 / [[Data-Driven Variable Impedance Control of a Powered Knee-Ankle Prosthesis for Adaptive Speed and Incline Walking\|Data-Driven VIC]] 凸优化辨识）。两个跨簇 insight：
> **① 阻抗刚度 $K(s)$ 加入 $m(s)$ 家族**：VICES 的 $K(s)$（当前该多软硬）与 control frequency 的 $\Delta t(s)$、[[LipsNet: A Smooth and Robust Neural Network with Adaptive Lipschitz Constant for High Accuracy Optimal Control\|LipsNet]] 的平滑度 $K(x)$、[[TARC - Time-Adaptive Robotic Control\|TARC]]、[[Dynamic Reinforcement Learning for Actors\|Dynamic RL]] 的 $\lambda_{max}(s)$ 同属"**状态依赖元控制 $m(s)$**"——策略不只输出动作，还输出"当前控制**柔顺度**该是多少"。物理阻抗是 $m(s)$ 在柔顺度维度的实例。
> **② "action space = 闭环控制空间"是贯穿的设计自由度**：VICES 揭示选对 action space（末端阻抗）比选算法更影响接触任务——与 control frequency 簇"频率也是 action 的一部分"（[[Elastic Time Step Reinforcement Learning, VTS-RL\|VTS-RL]] 输出 $\tau$、[[Reinforcement Learning for Control with Multiple Frequencies\|AP-AC]] 多频率动作）呼应。VICES 的"策略 20Hz + 阻抗 1kHz"分层正是 [[EvoControl - Evolved High Frequency Control for Continuous Control Tasks\|EvoControl]] 双层频率的 impedance 版。

> [!note] 簇内补链 · Foundation 精确锚点 · 暗线
> **簇内互链 + Delta**（补 §10 表）：
> - vs [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|Residual LfD]]：VICES 的 action=$(\Delta x, K)$ 与 Residual LfD 的 task-space pose residual 正交——前者学"多软硬"、后者学"偏离 base 多少"。二者可组合：让 residual 输出 impedance 而非 position（Residual LfD §6.3 对比表已提示）。
> - vs [[Path-Constrained Haptic Motion Guidance via Admittance Control|Path-Constrained Admittance]]：VICES 是**阻抗**（运动→力，作 action space），后者是**导纳**（力→运动，作 phase generator）——正是 [[ControlTheory#3.3 导纳控制与阻抗/导纳因果性校准|ControlTheory §3.3]] 的因果对偶两端。
>
> **Foundation 精确锚点**：末端阻抗律 = [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|ControlTheory §3.2]]；RL 学 $K(s)$ = [[ControlTheory#3.4 学习型变阻抗：RL × 阻抗的桥|ControlTheory §3.4]]；底层操作空间控制器 = [[ControlTheory#4. 操作空间公式化 (OSF)：在任务空间直接设计控制|ControlTheory §4]] + [[Dynamics#7.3 操作空间动力学 (Khatib)：在任务空间直接设计|Dynamics §7.3]]（$\Lambda=(JM^{-1}J^T)^{-1}$）；Surface Wiping 法/切向独立刚度 = [[ControlTheory#5. 力/位混合控制：正交分解任务空间|ControlTheory §5]] 的正交分解。
>
> **暗线 · 电流≠关节力矩（反驱动性）**：底层 $\tau=J^T\Lambda F+\mu+p$ 把 $\tau$ 当理想输入直接施加——真机上 $\tau$ 是电机→FOC→减速器输出，灵巧手关节刚度还要经腱映射 $K_j=R^T\mathrm{diag}(k_t)R$（§5.2），反驱动性差则期望阻抗被传动 backlash/摩擦污染（[[Actuation#8.2 三大非理想性——机械侧 gap 的主体|Actuation §8.2]]）。
