---
tags:
  - paper
  - trajectory-optimization
  - data-generation
  - contact-rich
  - cross-embodiment
aliases:
  - PhysicsGen
  - Physics-Driven Data Generation
paper-year: 2025
read-date: 2026-02-01
venue: arXiv
paper-pdf: "[[Papers/Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization.pdf]]"
related:
  - "[[Optimization]]"
  - "[[Dynamics]]"
  - "[[ContactMechanics]]"
  - "[[ReinforcementLearning]]"
---

# Physics-Driven Data Generation for Contact-Rich Manipulation via Trajectory Optimization

> [!abstract] 核心概要
> 利用轨迹优化将少量人类演示自动扩增为大规模、物理一致的接触丰富轨迹数据集，支持跨具身迁移和域随机化，实现零样本硬件部署。

> [!tip] 与理论基础的关联
> - [[Optimization]] - 接触隐式轨迹优化 (CITO)
> - [[Dynamics]] - 物理一致的轨迹生成
> - [[ContactMechanics]] - 复杂多接触交互
> - [[ReinforcementLearning]] - Diffusion Policy 训练
>
> **核心技术**: VR Demo Collection, Kinematic Retargeting, Demonstration-Guided Trajectory Optimization

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
人类演示提供全局引导（何时何处接触），轨迹优化提供局部优化（物理可行性），两者结合高效生成大规模接触丰富数据。

### 直观隐喻
就像有经验的木匠先粗略画出榫卯位置（人类演示），然后用精密工具精确加工（轨迹优化）——粗略的全局指导 + 精确的局部优化。

### 领域定位
```
MimicGen: 运动学重放（无物理）
    ↓
RL + Demo: 需要大量采样
    ↓
PhysicsGen: 演示引导 + 轨迹优化 → 物理一致数据 ← 本文
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 前人工作 | 限制 | PhysicsGen 突破 |
|---------|------|----------------|
| MimicGen | 运动学重放，接触任务失败 | **轨迹优化保证物理可行** |
| RL + Demo | 采样效率低 | **直接优化** |
| CITO | 需要好的初始猜测 | **演示提供全局引导** |
| 单具身数据 | 每个机器人需单独收集 | **跨具身迁移** |

### 关键贡献点
1. **VR 演示接口**: 具身无关的人手演示，Apple Vision Pro 实时可视化
2. **运动学重定向**: 将人手演示映射到不同机器人具身
3. **演示引导轨迹优化**: 用演示初始化 + 局部优化得到物理可行轨迹
4. **跨具身数据复用**: 同一演示适配 Allegro Hand / Kuka / Panda

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数据生成流程

```
Human Demo (VR)
    ↓ Kinematic Retargeting
Robot Trajectory (kinematically feasible)
    ↓ Trajectory Optimization
Dynamically Feasible Trajectory
    ↓ Parameter Randomization
Large-Scale Dataset
    ↓ Diffusion Policy Training
Robust Policy
```

### 3.2 运动学重定向

给定演示 $x^{demo}_{0:T}$，求解机器人配置 $q^{retarget}_{0:T}$：

$$
q_t^{retarget*} = \arg\min_{q} \sum_{i=0}^{N} w_i \|\psi_i(q) - \tilde{\psi}_i(x^{demo}_t)\|^2
$$

约束：
- 非穿透: $\phi_j(q) \geq 0$
- 关节限位: $q_{min} \leq q \leq q_{max}$

其中 $\psi_i$ 和 $\tilde{\psi}_i$ 是机器人和演示的对应点映射。

### 3.3 演示引导轨迹优化

**关键洞察**: 运动学重定向的轨迹提供了：
- 接触时机
- 接触位置
- 全局运动模式

轨迹优化只需在此基础上**局部细化**：

$$
\min_{x_{0:T}, u_{0:T}} \sum_{t=0}^{T} \ell(x_t, u_t, x^{retarget}_t) + \ell_T(x_T)
$$

约束：
- 动力学: $x_{t+1} = f(x_t, u_t, \theta)$
- 接触: complementarity constraints

### 3.4 域随机化数据生成

```
Algorithm 1: Automated Data Generation
Input: 概率分布 ρ, 增强数量 N, 演示轨迹
Output: N 条动力学一致轨迹

for i = 1 to N:
    θ ~ ρ  # 采样物理参数
    x_init ~ P_init  # 采样初始条件
    
    # 以重定向轨迹为初始猜测
    x_opt = TrajOpt(x_retarget, θ, x_init)
    
    if x_opt is feasible:
        Dataset.add(x_opt)
```

### 3.5 核心代码逻辑（PyTorch）

```python
# === 运动学重定向: 人手关键点 → 机器人配置 ===
def kinematic_retargeting(demo_kp, robot_fk, q_init, weights, jnt_lim,
                          n_iter=100, lr=0.01):
    """
    demo_kp: (T, N_kp, 3) — 人手关键点序列
    robot_fk: callable(q) → (N_kp, 3) — 机器人正运动学
    """
    q_seq = q_init.clone().requires_grad_(True)  # (T, n_dof)
    optimizer = torch.optim.Adam([q_seq], lr=lr)
    for _ in range(n_iter):
        optimizer.zero_grad()
        fk_pts = torch.stack([robot_fk(q_seq[t]) for t in range(len(q_seq))])
        loss = (weights * (fk_pts - demo_kp) ** 2).sum()
        # 关节限位软约束
        loss += 100 * (torch.relu(q_seq - jnt_lim[1]) ** 2
                     + torch.relu(jnt_lim[0] - q_seq) ** 2).sum()
        loss.backward()
        optimizer.step()
    return q_seq.detach()

# === 基于生成数据训练 Diffusion Policy ===
def train_diffusion_step(obs, action, policy_net, noise_sched, optimizer):
    """单步去噪扩散训练"""
    noise = torch.randn_like(action)
    t = torch.randint(0, noise_sched.T, (len(action),))
    noisy_action = noise_sched.add_noise(action, noise, t)  # 前向加噪
    pred_noise = policy_net(obs, noisy_action, t)            # 预测噪声
    loss = F.mse_loss(pred_noise, noise)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()
    return loss.item()
```

### 3.6 具身配置

| 具身 | DoF | 任务 |
|-----|-----|-----|
| Floating Allegro Hand | 22 | Cube manipulation |
| Bimanual Kuka iiwa | 14 | Box manipulation |
| Bimanual Panda | 14 | Box manipulation |

**跨具身泛化**: 同一套人手演示适配所有三种具身！

## 4. 实验与验证 (Experiments)

### 数据效率
- **输入**: 24 条人类演示（约 7 分钟收集）
- **输出**: 数千条物理一致轨迹

### 零样本硬件部署
- 平台: Bimanual Kuka iiwa
- 任务: Box reorientation
- 成功率: **高**（无需真实数据微调）

### 与 MimicGen 对比
| 方法 | 接触任务成功率 |
|-----|---------------|
| MimicGen | 低（运动学重放失败） |
| **PhysicsGen** | **高** |

### 4.2 训练设定

| 参数 | 值 |
|------|------|
| 演示收集 | Apple Vision Pro (VR)，~7 分钟收集 24 条 |
| 重定向优化器 | L-BFGS / Adam, ~100 iter/帧 |
| 轨迹优化器 | 接触隐式轨迹优化 (CITO), Drake 求解器 |
| 域随机化 | 摩擦 $\mu \in [0.3, 1.0]$, 质量 $m \pm 20\%$, 初始位姿 |
| 扩增规模 | 24 demo → 数千条物理一致轨迹 |
| 策略训练 | Diffusion Policy, 100 去噪步 |
| 部署 | 零样本 Kuka iiwa 双臂 |

### 4.3 Ablation 因果链

| 去掉什么 | 导致什么 | 因为什么机制 |
|---------|---------|------------|
| 去掉轨迹优化 (仅运动学重放) | 接触任务成功率骤降 | 运动学重放无法保证动力学一致——穿透/滑移导致物体状态偏移 |
| 去掉演示引导 (纯随机初始化 CITO) | 优化收敛率大幅下降 | 缺少全局引导时 CITO 陷入局部最优——接触模式组合爆炸 |
| 去掉域随机化 | 零样本部署失败 | 策略过拟合于单一物理参数，真实摩擦/质量偏差无法泛化 |
| 去掉跨具身 (仅单机器人数据) | 数据多样性不足，策略泛化性差 | 单具身运动模式单一，Diffusion Policy 学到的分布过窄 |

### 4.4 工程关键细节 (Engineering Tricks)

1. **演示作为 warm-start**: 运动学重定向轨迹直接作为 CITO 初始猜测，跳过接触模式搜索——优化效率提升一个数量级
2. **可行性过滤**: 轨迹优化失败（穿透/不收敛）的样本直接丢弃，保证数据集质量——成功率约 60-80%
3. **接触时序保留**: 重定向时保留人类演示的接触时序节奏，仅优化力/位细节——避免全局结构被破坏
4. **Apple Vision Pro 实时可视化**: VR 中实时渲染机器人重定向结果，演示者可即时调整动作策略
5. **URDF 统一接口**: 不同具身的正运动学通过 URDF 解析统一化，实现一套代码适配多机器人

## 5. 批判性分析 (Critical Analysis)

### 优势
- **物理一致**: 轨迹优化保证动力学可行
- **跨具身**: 演示可复用到不同机器人
- **低成本**: VR 演示无需真实硬件
- **接触丰富**: 专门针对多接触任务设计

### 局限性
- 需要高质量物理仿真器
- 轨迹优化计算成本
- 复杂任务可能需要更多演示

### 未来方向
- 更复杂的灵巧操作任务
- 实时轨迹优化
- 与学习方法结合

### 局限性深度分析（三维度）

| 维度 | 局限 | 替代方案 |
|------|------|----------|
| **理论** | 轨迹优化依赖精确物理模型——接触参数 (摩擦/恢复系数) 误差直接传导到生成数据质量 | 用可微仿真 ([[Dynamics]]) 在线校准参数；或引入 [[StochasticProcess]] 对接触参数建概率模型 |
| **算法** | CITO 计算成本高——每条轨迹需数秒至数分钟，限制扩增规模上限 | GPU 批量轨迹优化 (如 MJPC)；或用学习的世界模型替代物理仿真做 rollout |
| **工程** | 需要高质量 URDF + 精确网格模型用于重定向——对新机器人接入成本高 | 从点云/深度图自动重建 URDF ([[ComputationalGeometry]])；或直接用 3D 点流表征绕过 URDF |

## 6. 对灵巧操作的启发 (Implications)

1. **人类演示 = 全局引导**: 不需要精确，只需指明大方向
2. **轨迹优化 = 局部细化**: 处理物理细节和接触
3. **跨具身潜力**: 未来可能实现"一次演示，多机器人部署"
4. **接触丰富任务**: MimicGen 失效的场景

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── MimicGen (2023): 运动学演示扩增
├── CITO: 接触隐式轨迹优化
└── Sampling-based Planning: 高熵轨迹问题

本论文: PhysicsGen (2025)
├── VR 演示 + 运动学重定向
├── 演示引导轨迹优化
├── 跨具身数据生成
└── 零样本硬件部署

后续影响:
├── 大规模物理一致数据集
├── 通用机器人基础模型
└── 接触丰富任务的数据引擎
```

## 8. 与相关方法的对比

| 方面 | MimicGen | CyberDemo | PhysicsGen |
|-----|----------|-----------|------------|
| 演示来源 | 真实/仿真 | 仿真 | VR |
| 数据扩增 | 运动学 | 视觉+物理 | 轨迹优化 |
| 接触任务 | 受限 | 需仿真 | **专门设计** |
| 跨具身 | ❌ | ❌ | **✅** |
| 物理一致性 | ❌ | 部分 | **✅** |

## 9. 对转笔 (Pen-Spinning) / Sim-to-Real 的启发

> [!tip] 可迁移洞见
> 1. **演示引导 CITO 用于转笔轨迹生成**: 人手转笔演示 (VR 或 MoCap) → 运动学重定向到 LinkerHand → CITO 优化接触力序列 → 大规模数据扩增训练 Diffusion Policy
> 2. **跨具身数据复用**: 同一套人手转笔演示可适配不同灵巧手构型 (LinkerHand / Allegro / LEAP)——降低数据收集成本
> 3. **物理一致性对接触任务关键**: 转笔涉及滚动/滑动/分离的频繁切换，MimicGen 式运动学重放必然失败；PhysicsGen 的 CITO 可保证接触模式一致性
> 4. **域随机化启示**: 笔的质量分布、手指-笔摩擦系数、指尖形状应纳入随机化范围——与 [[ContactMechanics]] 参数不确定性直接对应

## 10. 与知识体系的联系 (Foundation Connections)

### 与 [[Optimization]] 的联系

演示引导轨迹优化的核心是**约束非线性规划** (NLP)。接触隐式 (CITO) 公式将互补约束松弛为：

$$
\min_{x,u,\lambda} \sum_t \ell(x_t, u_t, x_t^{\text{ref}}) \quad \text{s.t.} \quad x_{t+1} = f(x_t, u_t, \lambda_t), \; \phi(x_t) \geq 0, \; \lambda_t \geq 0, \; \lambda_t \cdot \phi(x_t) \leq \epsilon
$$

其中 $\lambda$ 是接触力，$\phi$ 是间隙函数，$\epsilon$ 是互补松弛参数。演示轨迹 $x^{\text{ref}}$ 既提供初始猜测又约束搜索空间——等价于在 NLP 的可行域中设置了一个「信任域」，避免陷入远离演示的局部最优。

### 与 [[ContactMechanics]] 的联系

数据生成的物理一致性核心在于**接触模式**的正确性。对多指操作，接触状态组合数为 $2^{n_c}$（$n_c$ 为潜在接触点数），轨迹优化必须在这个指数空间中搜索正确的模式序列。PhysicsGen 通过演示「锚定」接触时序，将组合搜索简化为连续参数优化——这正是 [[ContactMechanics]] 中互补问题 (LCP) 的实践简化。
