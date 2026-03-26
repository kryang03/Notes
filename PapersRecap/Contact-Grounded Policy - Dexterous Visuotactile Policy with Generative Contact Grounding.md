---
tags:
  - paper
  - manipulation
  - tactile
  - imitation-learning
  - sim-to-real
aliases:
  - CGP
  - Contact-Grounded Policy
paper-year: 2026
read-date: 2026-03-13
venue: arXiv
paper-pdf: "[[Papers/Contact-Grounded Policy- Dexterous Visuotactile Policy with Generative Contact Grounding.pdf]]"
related:
  - "[[ControlTheory]]"
  - "[[ContactMechanics]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
---

# Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding

> [!abstract] 核心贡献
> 提出 **Contact-Grounded Policy (CGP)**：策略不直接输出动作 $a_t$，而是通过 Diffusion 生成未来耦合的 (实际状态 $x_t$, 触觉 $u_t$) 轨迹，再通过学习的**接触一致性映射** $\mathcal{M}_\phi(x_t, u_t) \rightarrow a_t$ 将物理预期转化为顺应控制器的可执行目标指令。解耦了"意图生成"与"底层执行"。

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）

**一句话**：接触力是由位姿偏差产生的，因此可以通过联合预测 (实际状态, 触觉) 并反推控制目标来实现闭环的接触基准化执行。

**直观隐喻**：
- 传统 Visuotactile Policy = **"蒙眼走钢丝的人"**，感知到脚底压力后直接决定下一步的绝对力量，极易因环境微小扰动失控
- CGP = **"牵线木偶大师"**：先在脑海中预演下一步木偶的手在什么位置、此时感受到什么压力（Diffusion 预测）；然后因为深刻了解提线弹簧的紧度（底层 PD 控制器），精准反推提线目标位置（Target State）

### 1.2 现有方法的局限

- 现有策略**仅预测运动学轨迹**，缺乏显式的接触语义
- 触觉信号仅作为额外观测（辅助 Observation 或辅助 Loss），而非建模接触状态与底层控制器动力学的交互
- 网络直接端到端输出 $a_t$ → 不理解 $a_t$ 背后的物理接触力 → 滑移和过刚交互

**领域定位**：**Imitation Learning** 在 Contact-Rich 任务中的框架级创新，首次将触觉预测深度整合到底层执行逻辑的闭环中。

## 2. 核心方法/理论

### 2.1 关键创新点（Delta 分析）

相比 SOTA 的 Diffusion Policy（端到端映射到控制动作 $a_t$），增量（Delta）在于：

1. **Contact-Grounded 范式**：不显式建模接触点/模式，用闭环三元组 $(x_t, u_t, a_t)$ 隐式表征接触
2. **残差映射机制**：学习非线性底层合规控制器的逆映射，输出基于当前状态的 Target 偏移量
3. **KL 正则化触觉潜空间预测**：VAE 压缩高维触觉到低维 $h_t$，KL 约束确保潜空间平滑，极大提升 Diffusion 长期预测的稳定性

### 2.2 数学框架

#### 从阻抗控制到接触表征

底层 PD 控制器实质是虚拟弹簧阻尼系统，电机输出扭矩：
$$\tau = K_p (a_t - x_t) - K_d \dot{x}_t$$
其中 $a_t$ = 目标状态 (Target State)，$x_t$ = 实际状态 (Actual State)。

根据牛顿第三定律和动力学平衡，触觉反馈 $u_t$（力/形变）由跟踪误差 $(a_t - x_t)$ 驱动：
$$u_t \approx f(a_t - x_t)$$

**关键洞察**：在特定物理系统（确定增益 $K_p, K_d$ 和传感器）下，存在反函数：
$$a_t = \mathcal{M}_\phi(x_t, u_t)$$
即已知"手指实际在哪" ($x_t$) 和"感受到多大阻力" ($u_t$)，就能反推"控制器目标点" ($a_t$)。**这就是 Contact-Consistency Mapping。**

#### VAE 触觉降维与 KL 正则化

直接在 Diffusion 空间预测 768 维触觉阵列或 4 个 Digit360 图像 → 维数灾难。VAE 提取潜变量 $h_t = E(u_t)$：
$$\mathcal{L}_{VAE} = \mathbb{E}_{q}[\log P(u_t|h_t)] - \beta D_{KL}(q(h_t|u_t) \| \mathcal{N}(0, I))$$
KL 项强迫潜变量符合标准正态分布，为 Diffusion 的无条件先验打基础。

#### 耦合条件扩散过程

策略 $\pi_\theta$ 基于历史观测 $O_t$，生成未来耦合轨迹 $Y_t = [x_{t+1:t+T}, h_{t+1:t+T}]$。DDPM/DDIM 优化目标：
$$\mathcal{L}_{diff}(\theta) = \mathbb{E}_{(O_t, Y_t^0), \epsilon, j} \left[ \| \epsilon - \pi_\theta(O_t, Y_t^j, j) \|^2 \right]$$
**注意**：预测的不是动作 $a_t$，而是系统未来的实际物理演化预期。

### 2.3 核心代码逻辑（PyTorch tensor ops）

```python
# === VAE 触觉编码 ===
# u_t: (B, N_fingers, C_tactile)  密集触觉阵列
mu, logvar = tactile_encoder(u_t)                  # (B, D_latent) each
h_t = mu + torch.randn_like(mu) * (0.5 * logvar).exp()  # 重参数化采样

# === Diffusion 耦合预测 (DDIM) ===
# obs_history: dict{vision:(B,T_obs,3,H,W), tactile:(B,T_obs,D_lat), state:(B,T_obs,D_state)}
vis_feat = resnet(obs_history["vision"].flatten(0,1)).view(B, T_obs, -1)
tac_feat = tac_resnet(obs_history["tactile"])       # (B, T_obs, D_feat)
state_feat = state_mlp(obs_history["state"])         # (B, T_obs, D_feat)
cond = torch.cat([vis_feat, tac_feat, state_feat], dim=-1)  # (B, T_obs, D_cond)

# FiLM 条件注入 U-Net
Y = torch.randn(B, T_pred, D_state + D_latent)      # 初始噪声轨迹
for j in reversed(range(K_ddim)):                    # K_ddim=8
    eps_pred = unet(Y, cond, timestep=j)             # (B, T_pred, D_state+D_latent)
    Y = ddim_step(Y, eps_pred, j)                    # 去噪一步

pred_x, pred_h = Y.split([D_state, D_latent], dim=-1)  # (B,T_pred,D_state), (B,T_pred,D_lat)

# === Contact-Consistency Mapping (残差 MLP) ===
# M_phi: (x_t, h_t) → delta_a
delta_a = M_phi(torch.cat([pred_x, pred_h], dim=-1))    # (B, T_pred, D_state)
target_a = pred_x + delta_a                             # 目标位置 = 预测实际位置 + 残差
# target_a[:, :T_exec] 送入底层 PD 控制器
```

**数据流**: 16步预测（`T_pred=16`），8步执行后重规划（Receding Horizon, `T_exec=8`）。
**关键张量**: `Y` 中 state 和 tactile latent 在同一扩散过程中联合去噪，确保物理耦合性。

## 3. 训练与实验细节

### 3.1 训练设定

| 项目 | 细节 |
|------|------|
| **数据来源(仿真)** | VR 头显遥操作 |
| **数据来源(真机)** | 动捕系统 + 数据手套 |
| **数据量(仿真)** | Box Flipping 60 条，Egg Grasping 100 条 |
| **数据量(真机)** | Jar Opening 45 条，Box Flipping 90 条 |
| **训练/验证划分** | 1:1 Episode 级别划分（防止时间序列数据泄露） |
| **Policy rollout 频率** | 5Hz |

**监督信号**：
- Diffusion 模型：加噪轨迹的噪声预测 $\epsilon$，L2 Loss
- VAE 触觉压缩：重建误差 + KL 散度
- Contact-Consistency Mapping：三元组 $(x_t, u_t, a_t)$ 中 $a_t$ 作为 Ground Truth 回归

### 3.2 评估指标

- 策略端到端：**任务成功率 (Success Rate %)**
- 触觉重建：**平均绝对误差 (MAE)** 和 **KL 散度**

### 3.3 核心实验结果

| 任务 | CGP | Visuotactile DP (基线) |
|------|-----|----------------------|
| Dish Wiping (持续接触) | **93.3%** | 43.6% |
| Jar Opening (真机) | **58.4%** | 42.4% |

硬件平台：
- **真机**: Allegro V5 四指手 + Digit360 触觉 + UR5 臂
- **仿真**: Tesollo DG-5F 五指手 + 密集全手触觉阵列

### 3.4 Ablation Study 解读（因果链分析）

- **去掉 KL 正则化 → Diffusion 生成崩溃 → 因为潜空间失去平滑结构**：移除 $\beta D_{KL}$ 后，VAE 重建 MAE 反而下降（过拟合到逐点还原），但潜空间极为崎岖（KL Divergence 暴涨数十倍），Diffusion 在非平滑流形上采样命中率骤降 → Egg 成功率下降 >10%
- **$\mathcal{M}_\phi$ 仅输入 $x_t$ 或 $u_t$ → 映射误差翻倍 → 因为接触力与位姿是耦合的不可分信息**：仅有 $x_t$ 无法推断力的大小（不同物体刚度不同），仅有 $u_t$ 无法确定空间位置 → 证明双输入设计的不可替代性
- **去掉触觉输入 → 接触敏感任务（Dish Wiping）成功率骤降 → 因为纯视觉-状态无法感知接触力分布的微妙变化**，只有触觉提供实时的力分布反馈

## 4. 工程关键细节 (Engineering Tricks)

- **Rot6D 旋转表示**：使用 6D Continuous Rotation 代替四元数，消除拓扑不连续性，避免回归不收敛
- **模态不对称设计**：
  - 仿真（算力充沛）：$\mathcal{M}_\phi$ 将潜变量解码回原始高维阵列再做预测，保留高频细节
  - 真机（要求实时性）：直接用预测的潜变量 $\hat{h}$ 和 $\hat{x}$ 拼接送入 MLP，保证推理延迟 < 150ms
- **时钟同步关键**：$\mathcal{M}_\phi$ 学习高度依赖 $a_t$ 与 $x_t$ 的时间对齐。细微的时间错位会导致 Mapping 学到带相位延迟的弹簧阻尼模型 → 真机疯狂抖动

## 5. 核心洞见 (Insights)

> [!quote] Insight 1: 接触是可预测并可执行的
> 通过耦合预测 (状态, 触觉) 并映射到控制器目标，接触演化可被实时忠实再现

> [!quote] Insight 2: 触觉预测不应是辅助目标
> 触觉必须与控制栈紧密耦合，否则成为"脱节的接触意识"

> [!quote] Insight 3: 顺应控制器是桥梁
> PD 控制的虚拟弹簧-阻尼特性天然适合接触基准化

### 5.1 理论局限性深度分析（理论/算法/工程三维度）

**理论层面**：
- **接触映射的唯一性假设过强**：$\mathcal{M}_\phi: (x_t, u_t) \to a_t$ 隐含假设在给定 $(x_t, u_t)$ 下 $a_t$ 唯一确定。但在多接触/摩擦锥边界附近，同一法向力可由不同切向力组合产生 → 映射非单射，MLP 只能学到平均解
- **忽略惯性项**：推导 $u_t \approx f(a_t - x_t)$ 时省略了 $M(q)\ddot{q}$ 和 $C(q,\dot{q})\dot{q}$ 项，仅在准静态/低加速度场景成立。高动态任务（如转笔甩笔）中惯性显著，映射误差将系统性增大

**算法层面**：
- **串联误差累积**：级联架构 Diffusion → $\mathcal{M}_\phi$，Diffusion 对长时序 $x_t$ 的细微偏移被 $\mathcal{M}_\phi$ 的残差结构放大 → 控制振荡。无端到端梯度回传来联合校正
- **缺乏跨任务泛化**：单任务独训，未验证 $\mathcal{M}_\phi$ 是否习得可迁移的通用物理规律

**工程层面**：
- **强耦合于硬件参数**：$\mathcal{M}_\phi$ 本质是对当前 $K_p, K_d$ 和传感器材质的逆映射。增益调整 20% 即需重训
- **5Hz 策略频率瓶颈**：DDIM 8步去噪 + $\mathcal{M}_\phi$ 前向推理 → 实时性受限，无法处理需 >20Hz 控制频率的高动态接触

**替代方案对比**：

| 方案 | 核心思路 | 优势 | 劣势 |
|------|---------|------|------|
| CGP（本文） | Diffusion 预测 $(x,u)$ + 学习逆映射 | 物理接触一致性 | 硬件绑定，串联误差 |
| 端到端 Diffusion Policy | 直接预测 $a_t$ | 简单通用 | 无接触语义 |
| 力/位混合控制 + IL | 分别回归力目标和位置目标 | 控制论保证 | 需精确接触模型 |
| Model-Based RL + 接触模型 | 学习前向接触动力学做 MPC | 可在线适应 | 接触模型精度瓶颈 |

### 5.2 与用户研究（灵巧手转笔/Sim-to-Real）的启发

**与 PPO 训练转笔的关键区别**：用户的 PPO 网络直接输出目标位置 $a_t$（经仿真中 PD 控制器转为扭矩），网络在海量 trial-and-error 中**隐式**学会了仿真动力学。CGP 作为模仿学习方法，缺乏物理交互试错，因此通过**显式**预测物理结果再反推动作来弥补。

**可迁移的 Ideas**：
1. **正向动力学自监督 Loss**：在 PPO backbone 增加预测分支 $\text{Predictor}(x_t, a_t) \rightarrow u_{sim\_force}$，迫使特征层理解 PD 物理意义
2. **触觉模态对齐 (Cross-Modal Contrastive Learning)**：训练 $E_{real}$ 和 $E_{sim}$ 将真机触觉/仿真力映射到同一 Latent 空间，用对比学习对齐，部署时直接替换编码器
3. **"期望力"解耦为中间动作**：让 PPO 输出下一帧的期望接触力 $\hat{u}$ + 手部运动方向 $\Delta x$，通过可微 $\mathcal{M}$ 解析算出 $a_t$。将 RL 探索空间从"猜 PD 目标位置"变为"在力空间探索"，对转笔这种极依赖微妙接触力的任务可能极大提升效率

## 6. 与知识体系的联系

### 与 [[ControlTheory]] 的联系

CGP 的核心创新在控制层面：**学习的接触一致性映射作为力-位耦合的替代方案**。底层 PD 控制器的力学本质是二阶线性系统：
$$M\ddot{e} + K_d \dot{e} + K_p e = f_{ext}, \quad e = a_t - x_t$$
在准静态假设下 $\ddot{e} \approx 0$，接触力 $f_{ext} \approx K_p e$，故 $\mathcal{M}_\phi$ 实质是学习 $a_t = x_t + K_p^{-1} f_{ext}(u_t)$ 的非线性泛化（考虑传感器非线性和多点接触耦合）。

- 与 [[FACET - Force-Adaptive Control via Impedance Reference Tracking|FACET]] 互补：CGP 从触觉预测→目标状态（逆映射），FACET 从参考模型→阻抗参数（正向适应）
- 阻抗控制的经典框架 $Z(s) = Ms^2 + Bs + K$ 中，CGP 固定 $Z$ 而学习 $a_t$；FACET 固定 $a_t$ 模板而适应 $Z$

### 与 [[ContactMechanics]] 的联系

接触一致性映射隐式编码了赫兹接触模型的推广。对单点弹性接触，法向力-形变关系为：
$$f_n = \frac{4}{3} E^* \sqrt{R} \, \delta^{3/2}$$
$\mathcal{M}_\phi$ 的 MLP 需拟合这类非线性力-形变关系的**多点叠加**，并处理库仑摩擦锥约束 $\|f_t\| \leq \mu f_n$ 下的滑移/粘着状态切换。

- 多点接触的连续演化建模——从离散接触切换到连续分布式接触表征（通过 VAE 潜空间隐式捕获接触模式）
- CGP 回避了显式接触模式枚举（组合爆炸问题），代价是丧失了接触状态的可解释性

### 与 [[RepresentationLearning]] 的联系

VAE 触觉压缩的信息论解释：编码器 $q(h|u)$ 与解码器 $p(u|h)$ 构成率失真优化：
$$\mathcal{L} = \underbrace{-\mathbb{E}_q[\log p(u|h)]}_{\text{Rate (重建误差)}} + \beta \underbrace{D_{KL}(q(h|u) \| p(h))}_{\text{Distortion (正则化)}}$$
$\beta$ 控制压缩-保真权衡（$\beta$-VAE）。Ablation 证实：$\beta$ 过小 → 潜空间崎岖 → Diffusion 采样命中率骤降；$\beta$ 过大 → 触觉高频细节丢失 → $\mathcal{M}_\phi$ 力估计精度下降。

- 多模态融合策略：FiLM conditioning 将视觉/触觉/本体感觉通过仿射变换 $\gamma \odot x + \beta$ 注入 U-Net 各层，实现跨模态特征调制

### 与 [[SignalProcessing]] 的联系

密集触觉阵列（如 Digit360 的 $19 \times 19$ taxel grid）本质是二维空间信号场，VAE 编码器起**空间低通滤波 + 降维**作用：
$$h_t = E(u_t) \in \mathbb{R}^{D_{latent}}, \quad D_{latent} \ll N_{taxels} \times C_{channels}$$
保留接触力分布的低频主成分（接触区域、法向力大小）而滤除传感器噪声。这与经典 PCA/Karhunen-Loève 展开的思想一致，但 VAE 额外施加了概率先验约束。

## 6.5 跨方法对比

| 维度 | Diffusion Policy | Visuotactile DP | ACT | **CGP** |
|------|-----------------|-----------------|-----|--------|
| 触觉角色 | 无 | 辅助观测 | 无 | **耦合预测+接触映射** |
| 动作空间 | 直接 $a_t$ | 直接 $a_t$ | 直接 $a_t$ | **$(x_t, u_t) \to a_t$** |
| 物理一致性 | 无 | 弱 | 无 | **阻抗模型约束** |
| 接触丰富任务 | 差 | 中 | 差 | **强** |
| 硬件依赖 | 低 | 需触觉 | 低 | 需触觉 + 已知 $K_p, K_d$ |
| Sim-to-Real | 需微调 | 需重训 | 需微调 | 需重训 $\mathcal{M}_\phi$ |

## 7. 局限与未来方向

### 7.1 论文自身局限
- **传感器-控制器特异性**：接触一致性映射绑定特定触觉传感器和控制器参数，跨平台需重训练
- **单任务训练**：未验证跨任务接触知识迁移

### 7.2 未来方向
- 跨传感器/控制器联合训练；控制器参数条件化（$K_p$, $K_d$, 更新频率）→更好的部署泛化
- 与 RL 框架结合：用 CGP 的物理预期生成作为 RL 的世界模型组件
