---
tags: [WMTS, Dexterous_Manipulation, World_Model, Diffusion_Policy, Sim-to-Real]
aliases: [WMTS, World Model as Task Scheduler]
date: 2026-04-15
related:
  - "[[FOC_Control]]"
  - "[[Actuator2RigidDynamicsModel_gap]]"
  - "[[ReinforcementLearning]]"
  - "[[StochasticProcess]]"
  - "[[Optimization]]"
  - "[[Dynamics]]"
---

# World Model as Task Scheduler (WMTS)

> [!abstract] 核心架构
> 五模块流水线：**隐空间任务生成 → Oracle 专才 → Generalist 通才 → Ensemble World Model → 真机闭环微调**。
> 以 WM 的认知不确定性驱动课程生成，以物理因果律约束 WM 结构（Actuator + Rigid 解耦），在真机上实现安全的自主能力扩展。

---

## 零、 核心变量与空间定义

### 任务定义空间 $\mathcal{C}$

> [!question] 开放问题：任务连续性表示
> In-hand reorientation 可定义为连续且无限长的任务（时变转轴/转速/平动），但 CVAE 隐空间需要固定维度输入。当前方案：策略端采用 **Receding Horizon**（滑动窗口 $C_{local,t}$），CVAE 端使用无限长的连续任务表示（更良态的隐空间 + 自然的启动/结尾平滑）。需要寻找合适的无限序列数学表示工具。

旋转表示使用 **Continuous 6D Rotation Representation** ($R_{6D} \in \mathbb{R}^6$)，避免四元数双重覆盖和欧拉角万向节死锁。

### 状态空间 $\mathcal{S}$

**特权状态**（仅仿真可知）：
$$O_{oracle,t} = [P_{obj,t}, \dot{P}_{obj,t}, Q_{obj,t}, \dot{Q}_{obj,t}, F_{contact},\mu_{fric}]$$

**真机观测** $O_{real} \in \mathbb{R}^{N_{obs}}$，包含：
- PointNet 编码 Shape →100D
- Tactile Net 编码 $F_{tactile} \to 64D$
- Temporal Net (RNN/1D-CNN) 编码 $[\theta, \dot{\theta}, a, T] \to 128D$
- 将上述 Latent Vector 与 $\mathbf{o}^{\text{task}}_t$, $\mathbf{o}^{\text{hand}}_t$, $\mathbf{o}^{\text{inertia}}_t$​ 进行 Concat，再输入最终的 Policy MLP。

**① 物体形状描述（Fixed per episode）**：
$$\mathbf{o}^{\text{shape}} = \text{PointNet}(\mathcal{P}) \in \mathbb{R}^{100}$$
$\mathcal{P} = \{\mathbf{p}_i\}_{i=1}^{N_p} \subset \mathbb{R}^3$，经 PointNet（逐点 MLP + max-pooling）编码。确保 $\mathbf{o}^{\text{shape}}$ 的点云 $\mathcal{P}$ 也是变换到 $\{W\}$ 坐标系下再通过 PointNet 的。否则空间几何特征无法与目标对齐

**② 物体惯性参数（Oracle — Static per episode）**：
$$\mathbf{o}^{\text{inertia}} = [m, \mathbf{r}_{\text{com}}^\top, \text{vech}(\mathbf{I}_{\text{com}})^\top]^\top \in \mathbb{R}^{10}$$

**③ 任务目标（Look-ahead Buffer）**：
$$\mathbf{o}^{\text{task}}_t = [\mathbf{g}_{t+1}^\top, \ldots, \mathbf{g}_{t+T_{\text{la}}}^\top]^\top \in \mathbb{R}^{13 T_{\text{la}}}$$

其中 $\mathbf{g}_{t+k} = [{}^W\mathbf{p}^{*\top}, {}^W\mathbf{q}^{*\top}, {}^W\dot{\mathbf{p}}^{*\top}, {}^W\boldsymbol{\omega}^{*\top}]^\top \in \mathbb{R}^{13}$，定义在**手腕坐标系** $\{W\}$ 下。超出 episode 部分采用 Zero-Velocity Hold 填充。

**④ 手腕姿态**：$\mathbf{o}^{\text{hand}}_t = {}^G\mathbf{q}^B_t \in \mathbb{R}^4$（反映重力方向相对于手掌朝向）。
**⑤ 运动学时序观测 (Proprioceptive History)** 
由于 $\dot{\theta}_{meas}$ 存在差分噪声，单纯依赖单帧速度会导致网络对高频噪声敏感。必须引入观测历史。
- **关节位置序列:** $\mathbf{o}^{\text{pos}}_{t-H:t} = [\theta_{t-H}, \dots, \theta_t] \in \mathbb{R}^{16 \times (H+1)}$
- **关节速度序列:** $\mathbf{o}^{\text{vel}}_{t-H:t} = [\dot{\theta}_{t-H}, \dots, \dot{\theta}_t] \in \mathbb{R}^{16 \times (H+1)}$（经过低通滤波或卡尔曼滤波处理后的值）
    
- _工程建议:_ 此序列需通过 1D-CNN 或 Transformer 编码为隐向量 $z_{prop} \in \mathbb{R}^{d_{prop}}$，而非直接展平输入 MLP，以提取时序动态特征。
 **⑥ 高维触觉感知 (Tactile Sensing) 
 
直接使用传感矩阵，避免在底层进行不可靠的物理量反解。
- **触觉张量:** $\mathbf{o}^{\text{tactile}}_t = F_{tactile, t} \in \mathbb{R}^{5 \times 12 \times 6}$

- _工程建议:_ 这个维度 ($360$D) 如果直接输入 MLP 会导致局部空间信息丢失。建议使用针对手指拓扑设计的轻量级 CNN 或 Graph Neural Network (GNN) 处理成特征向量 $z_{tac} \in \mathbb{R}^{d_{tac}}$。它负责隐式回答 $O_{oracle}$ 中的 $F_{contact}$。
**⑦ 隐式动力学与环境适配 (Thermal & Actuator State) 
- **电机温度:** $\mathbf{o}^{\text{temp}}_t = T_{motor, t} \in \mathbb{R}^{16}$
- **历史动作序列:** $\mathbf{o}^{\text{action}}_{t-H:t-1} = [a_{t-H}, \dots, a_{t-1}] \in \mathbb{R}^{16 \times H}$
    
- _逻辑推导:_ 温度 $T$ 反映了电机当前的力矩饱和上限和热耗散状态；而动作序列 $a$ 配合 $\theta$ 序列，是网络推断“丝杠静摩擦”和“连杆弹性形变”的唯一途径。这两者组合是克服非线性 Jacobian 污染的关键。
    
**⑧ 驱动器专属输入 (Actuator Model Features)
- **反馈力矩:** $\tau_{fb, t} \in \mathbb{R}^{16}$
[确认：是否使用力矩传感器读到的关节力矩，还是直接用电机电流算的]
- _严格限制:_ 因为该"力矩"在传递到指尖之前已被热漂移 、丝杠静摩擦、非线性 Jacobian 和连杆弹性形变严重"污染"，$\tau_{fb}$ **不可**作为 Policy 的直接输入观测，**不可**参与计算 Reward（会引发极大的 Reward Hacking，导致策略学会“轻柔但无效”的动作以降低虚假力矩）。它仅被允许输入给专门训练的底层 Actuator Network（用于取代传统的 PD 控制器）。

### 动作空间 $\mathcal{A}$

关节目标位置增量 $A_t \in \mathbb{R}^{N_{joints}}$，通过 fixed PD 转换为关节力矩。

### 评价指标

- **单步追踪误差**：$\mathcal{E}_t = \|P_t - P^*_t\|_2 + \lambda_R \arccos\left(\frac{\text{tr}(R^{*\top} R_t) - 1}{2}\right)$
- **轨迹误差**：$\mathcal{E}_{traj} = \frac{1}{T}\sum_t \mathcal{E}_t$
- **成功率**：$\mathcal{R}_{succ} = \mathbb{I}(Z_{obj,1:T} > Z_{threshold})$

---

## 一、 仿真隐空间任务生成器 (Latent Task Generator)

在动力学可行域内主动采样新任务，提供课程难度梯度。

**架构**：VAE + CMA-ES 演化算法

**输入**：已知成功任务集 $\mathcal{D}_{known} = \{\xi_1, \ldots, \xi_K\}$，$\xi = [C_{global}, S_0]$

**输出**：新任务候选 $\xi_{new} = [C_{new}, S_{0,new}]$

### 1.1 Fitness Function

**Curiosity 信号**（WM Ensemble Disagreement）：

$$R_I(s_t, a_t) = \text{tr}\left(\text{Cov}(\{\hat{s}_{t+1}^m\}_{m=1}^M)\right)$$

本质上是 Bayesian Active Learning 中信息增益的近似——最大化 Ensemble 分歧 = 引导系统走向能最大幅度减少**认知不确定性（Epistemic Uncertainty）的区域。Ensemble 方差恰好只衡量认知不确定性，不受偶然不确定性（Aleatoric）影响。

**课程导向的 Fitness**：

$$\mathcal{F}(\xi_{new}) = \alpha \cdot (\mathcal{E}_{traj} \cdot \mathcal{R}_{succ}) - \lambda_{hull} \mathcal{D}_{latent}(\xi_{new}, \text{Hull}(\mathcal{D}_{known}))$$

演化目标：**通才"没掉落但跟得吃力"的任务（舒适区边缘）+ "刚好掉落且贴近已知凸包"的任务（恐慌区边界）**。

> [!question] 开放问题：CVAE 隐空间设计
> VAE/CVAE 的 condition 选择与隐空间映射流程需要细化。CVAE condition 应包含物体特征？还是纯几何的任务描述？

### 1.2 CMA-ES 核心机制

CMA-ES 维护多维正态分布 $\mathcal{N}(m, \sigma^2 C)$，通过四步迭代优化黑盒 Fitness：

1. **采样**：$x_k^{(g+1)} \sim m^{(g)} + \sigma^{(g)}\mathcal{N}(0, C^{(g)})$
2. **评估排序**：Rollout → Fitness 排名
3. **均值更新**：$m^{(g+1)} = \sum_{i=1}^\mu w_i x_{i:\lambda}^{(g+1)}$（截断选择，$\mu_{eff} = 1/\sum w_i^2$）
4. **协方差自适应**：双通道更新——
   - **Rank-$\mu$**：利用当前代优秀个体的方差（$C_\mu = \sum w_i (\Delta x)(\Delta x)^T$），大种群下高效
   - **Rank-One + Cumulation**：累积进化路径 $p_c$，利用代际相关性加速病态地形适应
5. **步长控制 (CSA)**：比较进化路径长度与随机游走期望长度，超长则增 $\sigma$、过短则减 $\sigma$

**工作流**：CVAE 映射到低维隐空间 → CMA-ES 在隐空间演化 → 生成 $\xi_{new}$ → 通才 Zero-shot Rollout → 盲区任务派发给 Oracle。

---

## 二、 专才策略 (Oracle Specialist Policy)

仅在仿真中唤醒的"解题机器"，利用特权信息为盲区任务生成专家轨迹。

**架构**：MLP Actor-Critic (PPO)

**输入**：$O_{oracle,t} = [O_{real,t}, S_{priv,t}, C_{local,t}]$

**输出**：$\pi_\theta(A_t | O_{oracle,t}) = \mathcal{N}(\mu_\theta, \Sigma_\theta)$

**Loss**：
$$\mathcal{L}_{total} = \mathcal{L}^{CLIP} - c_1 \mathcal{L}^{VF} + c_2 S[\pi_\theta] - c_3 \mathcal{L}_{Bounded}(\mu_\theta)$$

---

## 三、 通才策略 (Generalist Diffusion Policy)

真机部署主力。通过行为克隆吸收所有 Oracle 知识，从残缺观测中生成高质量动作。

### 3.1 Diffusion 前向/反向过程

**前向加噪**：$q(x_t | x_0) = \mathcal{N}(x_t; \sqrt{\bar{\alpha}_t}x_0, (1-\bar{\alpha}_t)I)$

**反向去噪**：$\mu_\theta(x_t, t, c) = \frac{1}{\sqrt{\alpha_t}}\left(x_t - \frac{\beta_t}{\sqrt{1-\bar{\alpha}_t}}\epsilon_\theta(x_t, t, c)\right)$

### 3.2 输入/条件/输出

- **Input (去噪对象)**：Noisy Action Chunk $\mathbf{A}^{(k)}$ `[B, Chunk_length, Action_dim]` + 时间步 $k$
- **Condition (引导上下文)**：$O_{real}$ + $C_{local,t}$（不参与前向加噪）
- **Output**：Action Chunk $\mathbf{A} = [A_t, \ldots, A_{t+K-1}]$

### 3.3 Classifier-Free Guidance (CFG)

由贝叶斯定理推导条件得分：
$$\nabla_{x_t} \log p(x_t | c) = \underbrace{\nabla_{x_t} \log p(x_t)}_{\text{流形引力}} + \underbrace{\nabla_{x_t} \log p(c | x_t)}_{\text{任务拉力}}$$

CFG 放大条件影响力（$w \geq 1$）：
$$\tilde{\epsilon}_\theta = (1-w)\epsilon_\theta(x_t, t, \emptyset) + w\,\epsilon_\theta(x_t, t, c)$$

训练时以 10% 概率置空条件 $c \to \emptyset$，推理时每步执行两次前向传播。

### 3.4 Loss (Denoising Score Matching)

$$\mathcal{L}_{Diff}(\theta) = \mathbb{E}_{\mathbf{A}^{(0)} \sim \mathcal{D}_{oracle},\, \epsilon \sim \mathcal{N}(0,I),\, k}\left[\|\epsilon - \epsilon_\theta(\mathbf{A}^{(k)}, k, O_{real}, C_{local,t})\|^2\right]$$

### 3.5 蒸馏流程

> [!question] 开放问题：HER 与蒸馏流程
> 1. **Hindsight Relabeling**：Oracle rollout 追踪不完美但动力学合理时，以实际轨迹替代目标轨迹作为 Condition（如何判断"动力学合理"？）
> 2. **异步蒸馏架构**：Worker (IsaacGym) → $\tau_{expert} = \{O_{real}, C_{achieved}, A_{oracle}\}$ → Buffer → Learner (DiT)
> 3. **Oracle 复用**：新任务需重新训练 Oracle，如何充分利用已有 Oracle/Diffusion/WM 的动力学先验？

---

## 四、 动力学世界模型 (Ensemble World Model)

仿真中的"观察者"，真机中的"安全调度员"。核心 insight：让在**慢速任务**上学会的摩擦系数（Rigid Model）和电机非线性（Actuator Model）**物理真实**，才有可能安全外推到高科里奥利力/急停的高动态任务。

**架构**：Probabilistic Ensemble（$M$ 个 MLP），结构与 PETS 一致

**输入**：$S_t, A_t$（**不输入任务 $C$**，坚持物理因果律）

**输出**：$\hat{P}_m(S_{t+1} | S_t, A_t) = \mathcal{N}(\mu_m, \Sigma_m)$

### 4.A Actuator Model：指令 → 关节力矩

> [!warning] 设计原则（详见 [[Actuator2RigidDynamicsModel_gap|L25 硬件分析]] 和 [[FOC_Control|FOC 物理推导]]）
> 不复现 FOC 内部电气动态（MCU 10-20kHz 的事），而是学习**从 $\tau_{cmd}$ 到 $\tau_{link}$ 的端到端黑箱映射**。

**POMDP 本质**：电机系统的通信延迟、减速器摩擦、反电动势使当前单一状态 $s_t$ 无法完整描述系统。传入历史窗口让 MLP 第一层权重学习**非线性 FIR 滤波器**。

**从指令到输出的物理链路**（7 步）：
1. 宿主机 SDK → CAN 帧 → 0.3ms 间隔串行发送
2. CAN 总线仲裁（5-20ms 不确定延迟）
3. MCU 接收 → FOC 转 $I_q$（10-20kHz PWM）
4. 空心杯电机 → 电磁转矩（受 Back-EMF 和热衰减约束）
5. 行星滚柱丝杠 → 直线推力（Stribeck 摩擦）
6. 耦合连杆 → 关节角位移（PIP-DIP 耦合，弹性形变）
7. 指尖输出力 → 传感器反馈闭环

**关键物理约束**：
- **转矩-转速包络**：仿真中 $|\tau| \leq \tau_{max}$（矩形），真机为**速度相关椭圆**。详见 [[FOC_Control#5.1 反电动势电压天花板与弱磁区域|FOC §5.1]]
- **温度级联漂移**：$R_s$ @80°C +31%，$K_t$ @80°C -9.6%。详见 [[FOC_Control#四、 温度对电机模型参数的系统性影响|FOC §四]]

**最终输入**：
$$\mathbf{x}_{act,t} = \Big[\underbrace{a_{t-H:t}}_{\text{指令}},\; \underbrace{\phi_{t-H:t}}_{\text{角度}},\; \underbrace{\dot{\phi}_{t-H:t}}_{\text{速度}},\; \underbrace{\tau_{fb,t-H:t}}_{\text{反馈力矩}},\; \underbrace{T_{motor,t}}_{\text{温度}}\Big], \quad H \geq 10\text{-}30$$

**输出**：$\hat{\tau}_{link,t} = f_{act}(\mathbf{x}_{act,t};\theta_{act}) \in \mathbb{R}^{N_{joints}}$

### 4.B Rigid Dynamic Model：力矩 → 状态演进

**Physics-Informed Neural Dynamics**：以 IsaacGym $(s_t, \tau_{link}^{sim}) \to s_{t+1}^{sim}$ 预训练。残差形式 $s_{t+1} = s_t + \Delta t \cdot f_{NN}(s_t, \tau_{link})$，可注入解析 [[Dynamics|刚体动力学]] skip connection。

**DR 参数处理**：
- 仿真阶段：$\xi_{DR}$ 作为显式条件 $f_{dyn}(s_t, \tau_{link}; \xi_{DR})$
- 真机阶段：学习型 encoder 在线推断 $\hat{\xi}_{DR} = g_{enc}(\phi_{t-K:t}, \dot{\phi}_{t-K:t}, \text{tactile}_{t-K:t})$

### 4.C 信息流架构

```
┌──────────────────────────────────────────────────────────────────┐
│                 Composited World Model (单步预测)                 │
│                                                                  │
│  ┌────────────────────┐   τ̂_link  ┌──────────────────────────┐  │
│  │  Actuator Model    │──────────▶│  Rigid Dynamic Model     │  │
│  │  f_act(θ_act)      │           │  f_dyn(θ_dyn)            │  │
│  │                    │           │                          │  │
│  │  In: a,φ,φ̇,τ_fb,T │           │  In: s_t, τ̂_link, ξ̂_DR │  │
│  │  Out: τ̂_link       │           │  Out: ŝ_{t+1} ~ N(μ,Σ)  │  │
│  └────────────────────┘           └──────────────────────────┘  │
│                                                                  │
│  梯度双通道:                                                     │
│  L_state = -log N(s_{t+1}|μ,Σ)  → ∂/∂θ_dyn 直接; ∂/∂θ_act 经τ̂│
│  L_act = ‖φ_{t+1}-φ̂_{t+1}‖²    → ∂/∂θ_act 直接 (仅真机)      │
│  仿真中 Act Model 退化为 Identity                                │
└──────────────────────────────────────────────────────────────────┘
```

### 4.D 可靠信号与预测目标

> [!warning] 力矩信号不可靠（详见 [[FOC_Control#6.3 输出定义与可靠性分析|FOC §6.3]]）
> $\tau_{measured} = K_t^{nominal} \cdot I_q^{measured}$：$K_t$ 不随温度更新、含量化噪声、是电机轴力矩而非关节力矩。

| 信号 | 可靠性 | 推荐用途 |
|:--|:-:|:--|
| 关节角度 $\phi_t$ | ⭐⭐⭐⭐ | **RL 核心观测 + WM 预测目标** |
| 触觉 $(12\times 6)_{\times 5}$ | ⭐⭐⭐⭐ | **RL 核心观测 + 接触判断** |
| 角速度 $\dot{\phi}_t$ | ⭐⭐⭐ | RL 观测（需滤波） |
| 反馈力矩 $\tau_{fb}$ | ⭐⭐ | Act Model 输入（❌非 reward/预测目标） |
| 温度 $T_{motor}$ | ⭐⭐⭐⭐ | Act Model 显式输入 |

**WM 联合预测目标**：$\hat{s}_{t+1} = [\hat{\phi}_{t+1}, \hat{\dot{\phi}}_{t+1}, \hat{z}_{tactile,t+1}] \sim \mathcal{N}(\mu_m, \Sigma_m)$

**联合 Loss**：
$$\mathcal{L}_{WM} = \underbrace{-\sum_t \log \mathcal{N}(s_{t+1} | \mu, \Sigma)}_{\text{Rigid: 状态极大似然}} + \lambda_{act} \underbrace{\|\phi_{t+1}^{real} - \hat{\phi}_{t+1}^{act}\|^2}_{\text{Act: 角度辅助 (仅真机)}}$$

---

## 五、 真机强化微调与调度闭环

### 5.1 Look-ahead Safety Filter

真机 $O_{real,t}$ → 通才推理 Action Chunk $\mathbf{A}$ → WM+Predictor 内存推演：

1. **Ensemble OOD 拦截**：预测方差极大 → 与仿真动力学严重分歧 → 立刻降级安全动作（即使均值预测"没掉落"）
2. **成功率阈值**：$\hat{\mathcal{R}}_{succ} < \text{Threshold}$ → 丢弃动作块，执行安全恢复
3. **温度感知**：Act Model 力矩可行性分数 $\rho_t = \hat{\tau}_{link}/\tau_{cmd}$，$\rho_t \ll 1$ 时降低任务难度

### 5.2 Discrepancy-Aware Success Predictor

$\mathcal{P}_\psi(\text{success} | h^{WM}_t, z_{task})$：基于 WM **隐层特征** $h^{WM}_t$（非原始状态）和任务编码。

**训练损失**：
- **NT-Xent 对比损失**：成功任务的 $h^{WM}$ 拉近，失败的推远——避免 False Positive（过度乐观）
- Embedding 空间上的 Softmax 分类

**梯度传递与动态演进**：
1. 仿真中与 Oracle 共同训练，掌握物理引擎下的"成功直觉"
2. 真机后，同时更新 WM 和 $\mathcal{P}_\psi$
3. WM 被真机数据强制拟合真实动力学残差 → $h^{WM}_t$ 分布漂移 → $\mathcal{P}_\psi$ 自适应跟随

### 5.3 真机数据收集与 WM 更新

收集 $\{a_t, \phi_t, \dot{\phi}_t, \tau_{fb}, T_{motor}, \text{tactile}_t\}$，微调 Actuator Model（拟合执行器非线性 + 温度漂移）和 Success Predictor。

> [!note] 力矩数据的正确用法
> $\tau_{fb}$ 仅作为 Actuator Model 输入特征，**不**作为 WM 预测目标或 RL reward。WM 预测目标为 $\hat{\phi}_{t+1}$ 和 $\hat{z}_{tactile,t+1}$。

### 5.4 通才微调策略

**选项 A：AWAC (Advantage Weighted BC)**

从真机顶级轨迹中蒸馏：

$$\mathcal{L}_{Finetune} = \mathbb{E}_{\tau_{real}}\left[\exp\left(\frac{R(\tau) - V(S)}{\beta}\right)\|\epsilon - \epsilon_\theta\|^2\right]$$

**选项 B：WM 作为物理引擎 (Dream RL)**

冻结微调后的 WM → DiWA 式 Dream Diffusion MDP + BC 正则 PPO。

> [!warning] Dream RL 的对抗性风险
> PPO 极其贪婪，可能数百步内找到 WM 物理漏洞，生成对抗性动作（"WM 里完美，真机上拧断手指"）。BC 正则项和短 horizon rollout 是必要的安全阀。
