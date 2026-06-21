---
tags:
  - foundation
  - representation-learning
  - imitation-learning
  - diffusion-policy
aliases:
  - 表征学习
  - 扩散策略
  - 模仿学习
  - ACT
  - 行为克隆
created: 2026-01-31
related:
  - "[[ReinforcementLearning]]"
  - "[[Dynamics]]"
  - "[[SignalProcessing]]"
  - "[[InformationTheory]]"
  - "[[Optimization]]"
  - "[[EmbodiedAI]]"
  - "[[ComputationalGeometry]]"
---

# 灵巧操作中的表征学习：从像素/触觉到可控、可泛化的策略

# Representation Learning for Dexterous Manipulation: From Pixels/Touch to Controllable, Generalizable Policies

> [!tip] 相关领域
> - [[ReinforcementLearning]] — 策略学习；表征是状态、扩散策略可被 RL 微调
> - [[Dynamics]] — 可微物理；表征要能预测下一步物理状态
> - [[SignalProcessing]] — 触觉表征与多模态融合；压缩=去噪
> - [[InformationTheory]] — 信息瓶颈=最优表征压缩；泛化需要压缩
> - [[Optimization]] — 隐式行为克隆=能量景观下降；NTK 区间下的凸化
> - [[ComputationalGeometry]] — 点云/SDF 是几何表征；神经隐式
> - [[EmbodiedAI]] — Vision Foundation Models (CLIP/DINO/SAM) 提供预训练表征
>
> **贯穿母题（本讲的"主角"）**：**视触觉对齐的精密插 USB (multimodal USB insertion)**。USB 可正插也可反插（多峰）、远看近摸（视触觉互补）、要微米级对齐（精密接触）、还要泛化到没见过的接口——一个动作把表征学习每一层都点亮，我们让它贯穿全篇。

## 0. 母题与理论大厦构建路线：从像素/触觉到可控状态

> [!abstract] 为什么用"插 USB"做贯穿母题？
> 表征学习的核心不是"换一个 encoder"，而是逐层回答：**原始观测里哪些变量对控制有因果作用，哪些只是域噪声或纹理 shortcut？** **插 USB** 这一个动作恰好逐层激活：
> - USB 可正插可反插 → **多峰动作分布**（MSE 会学成"插向两者中间的空气"）；
> - 远处用视觉对准、接触后视觉模糊、靠触觉微调 → **多模态融合**；
> - 接口的 3D 几何（形状、孔位） → **点云/几何表征**；
> - 仿真里训练、真机上面对没见过的接口 → **泛化理论**（§6）；
> - 生成整段插入动作而非单步 → **扩散/ACT 动作分块**。
>
> 全讲每引入一个方法，我们都回到这个 USB："**它学到的表征，能预测物理、能稳定控制、能在真机域差异下保留任务变量吗？**"

表征学习是一条"逐层剥离 shortcut、逼近可控因果变量"的链：

| 阶段 | 表征问题 | 典型方法 | 失败模式 | 灵巧操作中的修正 |
|:--|:--|:--|:--|:--|
| **重构式** | 如何压缩高维观测？ | PCA、AE、VAE | 重构噪声而非控制变量 | 用 [[InformationTheory\|信息瓶颈]] 约束任务相关性 |
| **对比式** | 哪些状态该在 latent 接近？ | InfoNCE、CLIP、时序对比 | 语义近但物理接触不同 | 加触觉/几何正样本，不只靠视觉帧 |
| **几何** | 形状如何进策略？ | PointNet++、Point Transformer、SDF | 稀疏/遮挡致接触边界错 | 与 [[ComputationalGeometry]] 的法向/SDF 校准 |
| **动作** | 多峰动作如何避免均值坍缩？ | MDN、IBC、Diffusion、Flow Matching | 平均动作落到不可行处 | 预测 action chunk + 低层控制过滤 |
| **因果** | latent 是否保留可控变量？ | world model、object-centric、3D flow | 学到 simulator artifact / 纹理 shortcut | 用动力学预测、触觉变化、执行器残差检验 |

> [!important] Foundation 级判断标准（好表征必须通过三问）
> 1. **能否预测下一步物理状态**？（动力学一致性）
> 2. **能否指导稳定控制**？（Lipschitz/雅可比正则）
> 3. **能否在真机域差异下保留任务变量**？（泛化/域适应）
>
> 只提高重构质量或分类准确率，不等于对灵巧操作有用。

> [!note] 本讲在知识图谱中的位置（依赖 / 被依赖）
> ```
>   [[SignalProcessing]] ─触觉流─┐                      ┌── 状态表征 ──> [[ReinforcementLearning]]
> [[ComputationalGeometry]] ─点云/SDF─┤                  │
>   [[InformationTheory]] ─信息瓶颈─┼──> 【RepresentationLearning】 ──扩散/ACT──> [[EmbodiedAI]] (VLA)
>     可微物理 <──> [[Dynamics]]    │                     │
>                              └── NTK/泛化理论 ──> 所有学习方法的"为何能泛化"
> ```
> 读法：信号/几何/信息论给表征"原料与约束"，可微物理给"物理检验"；表征产出（latent、扩散策略）喂给 RL/VLA；而 §6 的泛化理论（NTK、域适应）是**所有学习方法共享的理论地基**，被 [[Optimization]]、[[InformationTheory]]、[[StochasticProcess]] 反向链接。

## 1. 物理交互的计算本质：高维、非连续、流形

> [!tip] 本节四拍
> **直觉**（深度学习擅长平滑函数，但插 USB 的接触是断续突变的——根本张力在此）→ **推导**（维度诅咒与流形假设；接触非凸）→ **对比**（分析方法 vs 数据驱动，及其融合）→ **落点**（学习目标必须蕴含物理意义）。

将深度学习迁移到灵巧操作，难点不只是数据量，而是**接触动力学与神经网络擅长的平滑函数逼近之间的根本张力**。

### 1.1 维度诅咒与流形假设

Shadow/Allegro Hand 有 16–24 DoF，加物体 6 DoF 位姿与接触状态，状态空间维度极高。但有效操作（插 USB、转笔）并不遍历整个空间，而被约束在**低维流形**上（由关节限位、闭链运动学、任务目标共同决定）。**机器学习的挑战**：传统监督学习试图在整个空间拟合策略，需天文级数据；有效方法必须具备**流形学习**能力，自动发现并利用低维结构以降样本复杂度。

### 1.2 接触的非凸非光滑：神经网络的"均值化"陷阱

接触的建立/断开使动力学方程突变（分析力学用 [[ContactMechanics#5.1 互补条件与 LCP 的构建|LCP]] 描述）。**数据驱动的困境**：神经网络倾向学连续函数，训练数据含接触突变时，简单回归会产生**"平均化"模糊输出**——物理上不可行（手指穿透物体、或悬空不施力）。**这正是插 USB 时 MSE 把"正插/反插"平均成"插向中间空气"的根源**（§2 详述）。

### 1.3 分析 vs 数据驱动：从对立到融合

| 特性 | 分析方法 | 数据驱动方法 |
|:--|:--|:--|
| 基础 | 物理定律（牛顿-欧拉、库伦摩擦） | 统计相关性（神经网络） |
| 优势 | 可解释、保物理一致、无需训练 | 处理非结构化、适应噪声、端到端 |
| 劣势 | 难建模复杂摩擦/形变；对参数误差敏感 | 数据饥渴、缺可解释、OOD 泛化差 |
| 代表 | IK、阻抗控制、MPC | RL、IL、扩散策略 |

> [!important] 趋势是融合，不是二选一
> **可微物理 (Differentiable Physics)** 把物理模拟器本身变成可微层、嵌进网络，让梯度直接穿过物理交互反向传播（见 [[Dynamics#9. 适配层：可微物理与神经动力学|Dynamics 可微物理]]、[[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|优化的可微接触]]）。它保留物理先验、又具学习能力——是本讲与其他 Foundation 最深的接口。

### 1.4 学习目标的物理重构

目标函数不能只是预测误差最小化，必须蕴含物理意义：**能量最小化**（IBC/扩散把策略建成能量景观下降，与最小作用量原理不谋而合）；**雅可比正则**（策略 $\pi(s)$ 须 Lipschitz 连续，惩罚输入-输出雅可比范数以控制对感知噪声的敏感度——sim-to-real 关键，§3.3 给代码）。

------

## 2. 模仿学习的复兴：从均值坍缩到生成式分布建模

> [!tip] 本节四拍
> **直觉**（插 USB 可正可反，确定性回归会学成"插中间"）→ **推导**（协变量漂移；多峰；MDN→IBC→Diffusion→Flow Matching）→ **对比**（四种动作分布建模的多峰能力与推理成本）→ **联系**（扩散=朗之万采样↔[[StochasticProcess|SDE]]；ACT 时间集成=低通滤波↔[[SignalProcessing]]）。

模仿学习 (IL) 从专家演示提策略。早期行为克隆 (BC) 视其为监督回归 $a=f_\theta(s)$，在灵巧操作遭遇两大顽疾：

### 2.1 两大顽疾：协变量漂移与多峰

**协变量漂移**：执行策略时访问的状态分布 $P_{\pi_\theta}$ 偏离训练分布 $P_{expert}$，一旦犯小错 $\epsilon$ 就进入没见过的状态，误差随时间 $O(T^2)$ 累积（混沌系统对初值敏感的体现；BC 缺"恢复机制"）——这与 [[ReinforcementLearning#1.5 对比之二：纯模仿学习为何不够|RL 讲的 IL 分布漂移]]是同一回事。

**多峰**：同一状态可能有多种合法动作（插 USB 正插/反插、抓杯把/杯身）。**MSE 的失效**：确定性网络输出两种动作的均值——插向中间的空气，物理无效。解决方案演进：

| 方法 | 机制 | 多峰 | 代价 |
|:--|:--|:--|:--|
| **MDN** | 显式高斯混合 | ✅ | 难扩到高维动作 |
| **IBC** | 能量函数 $E(s,a)$ 隐式定义策略 | ✅ | 推理需昂贵 MCMC |
| **Diffusion Policy** | 条件去噪过程 | ✅✅ | 推理慢（迭代去噪） |

### 2.2 扩散策略：迭代的轨迹优化器

扩散策略不只是生成模型，本质是**迭代轨迹优化器**。它学动作分布的**分数函数** $\nabla_a\log p(a\mid s)$，训练是去噪：

$$
L(\theta)=\mathbb E_{k,a_0,\epsilon}\big[\|\epsilon-\epsilon_\theta(\sqrt{\bar\alpha_k}a_0+\sqrt{1-\bar\alpha_k}\epsilon,\,k,\,s)\|^2\big].
$$

> [!important] 物理意义：朗之万动力学（接 [[StochasticProcess]]）
> 推理是逆向 SDE 求解，等价于动作空间的朗之万采样 $a_{k-1}=a_k+\frac{\sigma^2}2\nabla_a\log p(a_k\mid s)+\sigma z$。机器人不"计算"动作，而是**跟随概率梯度（分数函数）逐步演化出动作**——天然支持多峰（正插/反插两个峰都保留），且预测整段 action horizon 保证时间平滑、抑制高频抖动。其 score 与 [[StochasticProcess#2.1 SDE：漂移 + 扩散，且扩散是状态相关的|SDE]]、被 RL 微调的路径见 [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|RL §10.1]]。

**Flow Matching：从 SDE 到 ODE**。扩散用 SDE、路径弯曲、采样几百步；Flow Matching 直接构造从噪声到数据的**直线最优传输路径** $x_t=(1-t)x_0+tx_1$，目标速度场 $u_t=x_1-x_0$，训练 $\mathcal L_{FM}=\mathbb E\|v_\theta(x_t,t,c)-(x_1-x_0)\|^2$，采样用 ODE 积分、**4–10 步**即可。

| 维度 | Diffusion (SDE) | Flow Matching (ODE) |
|:--|:--|:--|
| 路径 | 布朗运动（弯） | 最优传输（直） |
| 训练目标 | 预测噪声 $\epsilon$ | 预测速度场 $v_\theta$ |
| 采样步数 (NFE) | 100–1000 | **4–10** |
| 训练稳定性 | SNR 极值致梯度方差大 | 常速回归，梯度平稳 |

> [!tip] 低 NFE 对灵巧操作至关重要
> 20+ DoF 灵巧手实时闭环要 >10Hz 推理，传统扩散的高 NFE 成瓶颈。Flow Matching 与 action chunking 正交可组合（$\pi_0$、[[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]] 均用 FM 一次生成整个 chunk）。详见 [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]]。

```python
import torch, torch.nn as nn
# 扩散策略推理：从纯噪声迭代去噪到动作流形（朗之万动力学在能量景观中梯度下降）
class DiffusionPolicy(nn.Module):
    def __init__(self, noise_scheduler, action_dim, horizon):
        self.scheduler, self.action_dim, self.horizon = noise_scheduler, action_dim, horizon
        self.noise_pred_net = ConditionalUnet1D(input_dim=action_dim, global_cond_dim=...)  # 预测噪声 ε
    def predict_action(self, global_cond, steps=100):
        a = torch.randn((global_cond.shape[0], self.horizon, self.action_dim))  # 高熵初始（完全不确定）
        self.scheduler.set_timesteps(steps)
        for t in self.scheduler.timesteps:
            eps = self.noise_pred_net(a, t, global_cond)   # score = -ε/√(1-ᾱ)；cond=视觉+本体特征
            a = self.scheduler.step(eps, t, a).prev_sample # 轨迹逐渐"清晰"、保持时序相干
        return a   # 通常 receding horizon：只执行前几步再重规划
```

### 2.3 ACT：动作分块处理长时相关

ACT (Action Chunking with Transformers) 是另一条解多峰+误差累积的强力路线（详见 [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware|ACT 精读]]）。

**动作分块**：不预测单步、而预测未来 $k$ 步的 chunk，把时间视界从 $T$ 压到 $T/k$、显著减少自回归误差累积。**时间集成**：每步对重叠的多个预测块加权平均 $a_t=\sum_i w_i\hat a_t^{(t-i)}$——这本质是个**低通滤波 (EWMA)**（又一次与 [[SignalProcessing#1.4 数字滤波器：去噪、延迟与可控性的三角权衡|信号处理]]同形），滤掉高频控制噪声、合惯性约束。**CVAE 风格变量**：用 CVAE 学潜在"风格" $z$（演示里的速度/力度/接近角等任务无关信息），KL 正则约束 $z\sim\mathcal N(0,I)$ 保潜空间连续；推理时固定 $z=0$ 得确定行为或采样得多样行为。

```python
# ACT 核心：CVAE 处理多模态 + Transformer 处理时序（去防御代码）
class ACTPolicy(nn.Module):
    def forward(self, qpos, image, actions=None, is_training=True):
        obs_tokens = self.process_observations(qpos, image)     # ResNet backbone + 投影
        if is_training:                                          # 训练：从真实动作编码 z=q(z|x,a)
            enc = self.encoder(torch.cat([self.cls_token, obs_tokens, self.action_embed(actions)], 1))
            mu, logvar = self.latent_proj(enc[:, 0]).chunk(2, -1)
            z = mu + torch.exp(0.5*logvar) * torch.randn_like(mu)  # 重参数化
            kl_loss = compute_kl_loss(mu, logvar)                # 拉近 q(z|x,a) 与 N(0,I)，正则潜空间
        else:                                                     # 推理：无真值动作 → z=0（均值模式）
            z = torch.zeros((qpos.shape[0], self.latent_dim)); kl_loss = None
        hs = self.decoder(self.query_embed,                       # query=各未来时间步；cross-attn 关注观测
                          torch.cat([obs_tokens, self.style_proj(z).unsqueeze(1)], 1))
        return self.action_head(hs), kl_loss   # 外层再做 temporal ensembling（EWMA 低通）
```

------

## 3. 表征的演进：从重构到对比到基础模型

> [!tip] 本节四拍
> **直觉**（插 USB 要泛化到没见过的接口，靠的是表征而非记忆）→ **推导**（PCA→AE→VAE→对比→基础模型的统一降维主线）→ **对比**（通用视觉表征 R3M/VIP 为何在灵巧操作失灵；DON 的像素级对应）→ **联系**（雅可比正则↔Lipschitz↔[[ControlTheory|稳定性]]；信息瓶颈↔[[InformationTheory]]）。

### 3.1 降维思想的统一主线

所有表征方法目标相同：找低维流形 $\mathcal Z\subset\mathbb R^d$（$d\ll D$），使高维观测 $x$ 的投影保留任务相关信息。

- **PCA**：协方差前 $k$ 特征向量，$\min_V\mathbb E\|x-VV^Tx\|^2$。只捕**线性**相关——接触模式切换、物体旋转本质是非线性流形。
- **AE**：$z=f_\theta(x),\hat x=g_\phi(z)$；线性时退化为 PCA。潜空间无结构保证（不能采样、插值不连续），不适合作生成式策略输入。
- **VAE**：引入概率 $p_\theta(z\mid x)=\mathcal N(\mu,\sigma^2)$，ELBO 同时优化重构与潜空间正则——ACT 用 CVAE 编码演示风格（§2.3）。
- **对比 → 基础模型**：从像素级重构转向**语义级对齐**（InfoNCE、CLIP）、再到视觉-触觉联合嵌入（§5）。

> [!note] VAE 即 $\beta$-VAE 即信息瓶颈
> VAE 的 KL 正则正是 [[InformationTheory#5. 信息瓶颈：最优表征的信息论基础|信息瓶颈]] 的拉格朗日乘子 $\beta$——**重构-压缩权衡 = 预测-压缩权衡**。这把表征学习与信息论钉在了同一个变分式上。

### 3.2 通用视觉表征的局限：具身差异

R3M（时序对比，假设视频相邻帧特征相近）、VIP（学反映"到达目标进度"的价值嵌入）在大规模人类视频上预训练视觉编码器，导航/简单抓取有效，**但在灵巧操作常失灵**。根因是**具身差异 (Embodiment Gap)**：人手运动学≠机械手，且视频缺**接触力学**信息——人类视频的"操作"是语义层面的，而机器人需毫米级几何与动力学特征。**插 USB 泛化到新接口，需要的是接触几何表征，不是语义相似度。**

### 3.3 Dense Object Nets：形变物体的像素级对应

对非刚体（USB 线缆、布、绳）需像素级**对应**。DON 自监督训练全卷积网络输出像素级描述符：**同一物理点在任何视角/光照/形变下描述符一致，不同点正交**。它实际学了附着在物体表面的**典型坐标系**——即使绳子拓扑扭曲，仍能追踪特定物理点（如绳结），对非刚体操作至关重要。

```python
# DON 像素级对比损失：学视角/形变不变的几何描述符（去防御代码）
def pixelwise_contrastive_loss(img_a, img_b, matches, non_matches, model, margin=0.5):
    desc_a, desc_b = model(img_a), model(img_b)        # 稠密描述符图 (B, D, H, W)
    loss = 0
    for ua, va, ub, vb in matches:                     # 匹配：同一物理点 → 描述符趋近（光度+形变不变）
        loss += ((desc_a[:, :, va, ua] - desc_b[:, :, vb, ub]) ** 2).sum(1).mean()
    for ua, va, ub, vb in non_matches:                 # 非匹配：不同点 → 距离 > margin（防 mode collapse）
        d = torch.norm(desc_a[:, :, va, ua] - desc_b[:, :, vb, ub], dim=1)
        loss += torch.clamp(margin - d, min=0).pow(2).mean()
    return loss
```

### 3.4 对比 RL 与雅可比正则

**对比 RL**：稀疏奖励下把 RL 重构为表示学习——用 InfoNCE 在潜空间拉近能到达目标的"状态-目标对"$(s,g)$、推远无关轨迹；学到的内积 $\langle\phi(s),\phi(g)\rangle$ 直接对应到达概率/值函数，规划可在潜空间几何里做（接 [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功|RL 探索]]）。

**雅可比正则**：$J_{reg}=\lambda\|\partial\pi(s)/\partial s\|_F^2$，限制策略的局部 **Lipschitz 常数**——传感器微扰时动作不剧变。这是控制稳定性的必要条件（[[ControlTheory#10. 稳定性理论的统一基石|Lyapunov 稳定性]]），也是 sim-to-real 关键。

```python
# 雅可比正则：惩罚输入-输出雅可比 Frobenius 范数（控制策略对感知噪声的敏感度）
def jacobian_loss(policy_net, states, lam=0.01):
    states.requires_grad_(True)
    actions = policy_net(states)
    reg = 0
    for i in range(actions.shape[1]):                  # 对每个动作维求梯度
        g, = torch.autograd.grad(actions[:, i], states, torch.ones_like(actions[:, i]),
                                 create_graph=True, retain_graph=True)  # create_graph 以便反传此正则
        reg += (g ** 2).sum()                          # ‖J‖_F² = Σ(∂y_i/∂x_j)²
    return lam * reg     # 深层网络实战用 Hutchinson estimator 近似，避免算完整雅可比
```

------

## 4. 3D 几何表征：点云的深度学习

> [!tip] 本节四拍
> **直觉**（USB 接口的 3D 形状/孔位是点云，但点云无序——CNN/MLP 用不了）→ **推导**（Deep Sets 定理给置换不变；PointNet/++ 层级局部特征）→ **对比**（PointNet 全局 vs PointNet++ 局部 vs Point Transformer 注意力）→ **落点**（3D Flow 作载体无关动作表征）。

> [!note] 教科书参考
> 本节基于 Qi et al. (2017) PointNet/PointNet++ 与 Guo et al. (2021) 3D 点云深度学习综述。

### 4.1 集合函数：置换不变性

点云是**无序集合** $\mathcal P=\{p_1,\dots,p_N\}$，须 $f(\{p_i\})=f(\{p_{\pi(i)}\})$（任意排列不变）。标准 MLP/CNN 假设固定顺序、用不了。

> [!theorem] Deep Sets 定理 (Zaheer et al.)
> 任何置换不变函数可分解为 $f(\mathcal P)=\rho\big(\sum_{p\in\mathcal P}\phi(p)\big)$，$\phi$ 逐点特征提取、$\rho$ 聚合后处理、$\sum$ 是对称聚合（可换 max/mean）。

**PointNet** 直接应用：$\text{PointNet}(\mathcal P)=\gamma(\max_{p}h(p))$。物理直觉：$h_i(p)$ 是"探测函数"检测某几何特征（角点/平面），$\max$ 问"这种特征**是否存在**"。**局限**：缺局部几何建模，每点独立处理。

### 4.2 PointNet++：层级局部特征

模仿 CNN 局部感受野：**FPS**（最远点采样，保覆盖均匀）→ **Ball Query**（半径 $r$ 内取 $K$ 邻居）→ **Mini-PointNet**（逐邻域提特征）→ 递归。用**相对坐标** $(p_j-p_i)$ 保平移不变：$f_i^{(l+1)}=\text{PointNet}(\{p_j-p_i:p_j\in\mathcal N(p_i,r)\})$。

### 4.3 几何不变性的编码

物体旋转/平移不应改变抓取策略本质，需 **SE(3)-等变/不变**网络：$f(T\cdot\mathcal P)=T\cdot f(\mathcal P)$（等变）或 $=f(\mathcal P)$（不变）。**Vector Neurons** 把标量特征换成 3D 向量特征、用旋转等变线性层。**T-Net** 数据驱动对齐 $\mathcal P'=\mathcal P\cdot T_{pred}$，正则 $\|I-TT^T\|_F^2$ 约束近正交。

> [!abstract] 动作结构先验：RodriNet
> [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] 与通用 SE(3)-等变网络互补：后者关心外部坐标变换的等变，RodriNet 关心机器人内部 joint/link 特征如何沿运动学树传播——它把 [[Dynamics#2.2 旋转群 SO(3)、李代数 so(3) 与 Rodrigues 公式|Rodrigues 正运动学模板]]做成可学习 backbone，是高 DoF 动作表征里"结构化 action mixer"的代表。

### 4.4 Point Transformer 与 3D Flow

**Point Transformer** 把自注意力引入点云，局部自注意力用位置编码 $\alpha,\delta$ 编码相对几何位置——自适应邻域权重（vs PointNet++ 固定聚合），表达力更强。

> [!tip] 3D Flow：载体无关的动作表征（Wenlong Huang, Stanford SVL）
> **动作的本质是 3D 的**——人闭眼也能在 3D 空间移动手臂。传统动作表征（EE 位姿、关节指令）无法跨载体泛化。**3D Flow**：在每个连杆按 URDF 网格采样端点 → 正运动学 → **点流**；场景也用 RGBD→点云，**状态与动作模态统一**、对点数量不变、自动适配不同 DoF/夹爪。**PointWorld (Stanford 2026)** 将其用于 3D 世界模型，发现：① PTV3 等现代 Transformer 在相近内存下可扩容至图基模型的 ~300×；② **仅夹爪 3D 点流 > 全身点流 > 低维表征**；③ 模型隐式学到目标检测、材料估计、形状补全、物体间动态。**对灵巧操作**：每个手指连杆都可采样为点流，无需设计手指专用动作空间。
> （旁注：机器人预训练→微调迁移效率比 NLP 低 ~100×，要达 NLP 水平需 ~1.25 亿小时数据——这激励了世界模型作为更高效预训练目标，接 [[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|MBRL]]、[[EmbodiedAI]]。）

------

## 5. 多模态融合：视触觉的交响

> [!tip] 本节四拍
> **直觉**（插 USB：远处视觉对准，一接触视觉就被遮挡，靠触觉微调）→ **推导**（视触觉在物体表面这一共同实体上对齐；触觉点云）→ **对比**（简单拼接 vs 交叉注意力融合）→ **落点**（多模态=信息量 + 冗余度/鲁棒性）。

视觉与触觉不是冗余，而是**互补的物理尺度**：视觉擅长全局规划与识别，但接触发生时因**遮挡**和尺度限制几乎失效；此时触觉是感知接触力学（摩擦、滑动、纹理）的唯一窗口。**插 USB 的"接触后视觉模糊"正是这一互补的教科书场景。**

### 5.1 视触觉联觉：跨模态对齐

**核心洞察**：视觉与触觉在**物体表面这一共同实体**上有天然对应——视觉观测表面光度属性（颜色、纹理、曲率），触觉感知表面力学属性（硬度、摩擦、法向）。二者可通过**对比学习**在共享潜空间对齐：**看到表面即可预测触觉响应，触觉感知即可推断几何**。

**触觉点云表征**：把触觉数据从 2D 图/1D 向量升级为 **3D 点云** $\mathcal T=\{(x_i,y_i,z_i,f_i)\}$（$(x,y,z)$ 由传感器几何 + 手指正运动学算出、$f$ 是力强度）——与视觉点云同几何空间、便于融合、保拓扑、支持 PointNet 系列（接 §4）。

**跨模态对比 (InfoNCE)**：

$$
\mathcal L_{NCE}=-\log\frac{\exp(\mathrm{sim}(z_v,z_t^+)/\tau)}{\sum_j\exp(\mathrm{sim}(z_v,z_t^j)/\tau)},
$$

$z_v$ 视觉嵌入、$z_t^+$ 时间对齐的触觉嵌入（正样本）、$z_t^j$ 其他时刻（负样本）。Robot Synesthesia 做**双向**对比（视→触预测、触→视检索），形成联合嵌入空间使 $\|z_v-z_t\|\propto$ 物理状态差异（与 [[InformationTheory#2.2 互信息：观测的"切割能力"|互信息]]、[[StochasticProcess#4. 信念更新：从 EKF 失效到粒子滤波|多模态融合]]同源）。

### 5.2 交叉注意力融合：让触觉"询问"视觉

简单特征拼接不够（两模态空间结构与更新频率不同）。VTT/GelFusion 用**交叉注意力**：

$$
\mathrm{Attn}(Q_T,K_V,V_V)=\mathrm{softmax}\Big(\frac{Q_TK_V^T}{\sqrt d}\Big)V_V,\qquad Q_T=W_QT,\ K_V=W_KV,\ V_V=W_VV.
$$

| 模态 | 特性 | 编码器 | 角色 |
|:--|:--|:--|:--|
| 视觉 | 全局、低频、易遮挡 | ResNet/ViT | 物体位姿先验，指导接近阶段 |
| 触觉 | 局部、高频、接触敏感 | ConvNet/触觉编码器 | 接触几何/力反馈，指导操作阶段 |

> [!important] 物理逻辑：把局部触觉"注册"到全局物体模型
> Query 来自触觉：当触觉探到一个局部特征（感到 USB 接口的棱角），它生成 Query，交叉注意力在视觉特征图（Key）里搜匹配的空间位置，把局部触觉**注册**到全局物体模型上——有效解决局部感知的状态歧义。这与 [[ComputationalGeometry#3.2 EPA：从"撞了"到"撞多深、往哪退"|EPA 法向]]、[[SignalProcessing#5.3 因子图：多模态融合与触觉里程计|因子图融合]]互补。

### 5.3 GelSight 的 Sim-to-Real：Taxim 快速仿真

要在仿真训触觉策略，须解触觉仿真难题。FEM 模拟弹性体精确但太慢（撑不住 RL 每秒数千次采样）。**Taxim** 把光学与力学**解耦**：光学响应用多项式查找表（<100 真实数据校准）把形变梯度映到像素强度；标记运动场用线性弹性的**叠加原理**预计算基本形状位移、线性组合合成复杂接触——速度提升几个数量级，可集成进 Isaac Gym 做大规模并行 sim-to-real（穿透深度等新表征见 [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]]，触觉信号处理见 [[SignalProcessing#3. 视觉触觉传感 (VTS)：把触觉变成视觉问题|SignalProcessing §3]]）。

### 5.4 接触丰富任务：插 USB 的多阶段策略

插拔/精密装配单靠视觉只能毫米级、任务要微米级。**多阶段策略**：① **接近阶段**视觉主导、快速到目标区；② **搜索/对齐阶段**触觉主导，用螺旋搜索或力控，策略用触觉反馈梯度微调动作——本质是隐式的 [[ControlTheory#3.2 阻抗控制：调节力与运动的动态关系|阻抗控制]]。**GelFusion 的鲁棒性**：即便人为遮挡摄像头，多模态策略仍能靠触觉流 + 本体感知推断状态完成任务——证明**多模态不只增信息量，更增冗余度与鲁棒性**。这就是插 USB 母题的完整闭环：视觉对准→触觉对齐→力控插入。

------

## 6. 泛化理论：为什么表征决定泛化【理论枢纽】

> [!tip] 本节四拍
> **直觉**（仿真训练的插 USB 策略，凭什么能在没见过的真实接口上工作？泛化的数学本质是什么？）→ **推导**（经验/期望风险→VC/Rademacher→表征如何降复杂度→域适应→隐式正则→NTK→鞍点）→ **对比**（VC 维 vs Rademacher；显式正则 vs 隐式正则）→ **落点**（好表征 = 低复杂度 = 好泛化）。
>
> 本节是**被多份 Foundation 反向链接的理论地基**——[[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|Optimization 的非凸景观]]、[[InformationTheory#5. 信息瓶颈：最优表征的信息论基础|信息瓶颈]]、[[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|GP 的样本效率]] 都在此交汇。

> [!note] 教科书参考
> 本节基于 *Theory of Deep Learning* (Arora et al.) 的泛化理论、Rademacher 复杂度、隐式正则、NTK（Ch.9）与鞍点逃逸（Ch.6–7）章节。

### 6.1 经验风险 vs 期望风险

训练集 $\mathcal D=\{(x_i,y_i)\}_{i=1}^n$：经验风险 $\hat R(f)=\frac1n\sum\ell(f(x_i),y_i)$、期望风险 $R(f)=\mathbb E_{(x,y)\sim P}[\ell(f(x),y)]$。**泛化误差** $=R(f)-\hat R(f)$。核心问题：**如何控制泛化误差？**

### 6.2 VC 维与打散

**打散**：假设类 $\mathcal H$ 打散样本集 $S$（$|S|=m$）当且仅当对 $S$ 上全部 $2^m$ 种标签都存在 $h\in\mathcal H$ 正确分类。**VC 维** $d_{VC}=\max\{m:\exists S,\mathcal H\text{ 打散 }S\}$。例：$\mathbb R^d$ 线性分类器 $d_{VC}=d+1$。

> [!theorem] VC 泛化界
> VC 维为 $d$、损失 $\in[0,1]$，则以概率 $1-\delta$：$R(h)\le\hat R(h)+O\big(\sqrt{(d\log(m/d)+\log(1/\delta))/m}\big)$。即 $m\gg d$ 时泛化误差趋零。

> [!important] 为什么 VC 维对深度学习失效（推动范式转移）
> $k$ 参数网络 VC 维约 $O(k^2)$（Bartlett 1998），远大于训练样本数——预言严重过拟合，但实践中深度网络泛化良好。这一悖论把理论从 VC/Rademacher 推向**隐式正则化**（§6.6）。**灵巧操作含义**：VC 维只适用于简单（线性）策略类，深度策略的泛化更适合用域适应（§6.5）与 NTK（§6.7）。

### 6.3 Rademacher 复杂度与表征

$$
\mathfrak R_n(\mathcal F)=\mathbb E_{\sigma,\mathcal D}\Big[\sup_{f\in\mathcal F}\frac1n\sum_i\sigma_i f(x_i)\Big],\quad \sigma_i\in\{-1,+1\}.
$$

泛化界 $R(f)\le\hat R(f)+2\mathfrak R_n(\mathcal F)+O(\sqrt{\log(1/\delta)/n})$。物理直觉：Rademacher 复杂度衡量函数类**拟合随机噪声的能力**——能完美拟合任意噪声则可能过拟合。它比 VC 维更紧（依赖数据分布），但仍不够解释过参数化。

### 6.4 为什么好表征 = 好泛化

两阶段模型 $f(x)=g(\phi(x))$（$\phi$ 表征/encoder、$g$ 任务头）：

> [!theorem] 表征降低下游复杂度
> 若 $\phi$ 把输入映到**低维流形**，则 $\mathfrak R_n(\mathcal G\circ\phi)\le\mathfrak R_n(\mathcal G)\cdot\mathrm{Lip}(\phi)$。

**灵巧操作含义**：PointNet 的 max-pooling 是隐式 Lipschitz 约束；VAE 瓶颈强制低维降复杂度；对比学习把相似样本拉近、减少有效维度——**这就是"好表征决定好泛化"的数学**，也是 §0 判断标准第三问的理论依据。

### 6.5 Sim-to-Real 的泛化视角：域适应

把 sim-to-real 形式化为**域适应**：源域 $P_{sim}$、目标域 $P_{real}$。

> [!theorem] 域差异界 (Ben-David et al.)
> $R_{real}(f)\le R_{sim}(f)+d_{\mathcal H}(P_{sim},P_{real})+\lambda$，其中 $d_{\mathcal H}$ 是 $\mathcal H$-散度（两域可区分性）、$\lambda$ 是最优联合假设误差。

三条实践（与 [[ReinforcementLearning#9. Sim-to-Real：把转笔策略搬上真机|RL sim-to-real]]一一对应）：① **域随机化**扩大 $P_{sim}$ 覆盖 $P_{real}$、降 $d_{\mathcal H}$；② **域不变表征**学 $\phi$ 使 $\phi(x_{sim})$ 与 $\phi(x_{real})$ 不可区分；③ **系统辨识**在线估 $P_{real}$ 参数、直接最小化 $R_{real}$。插 USB 泛化到新接口，本质是把 $d_{\mathcal H}$ 压到足够小。

### 6.6 隐式正则化：为什么过参数化能泛化

**悖论**：参数远超样本应过拟合，但现代深度学习恰在过参数化下表现出色。**答案：优化算法本身引入隐式正则化。**

> [!important] GD 的最小范数偏置（命题 8.1.1）
> 过参数化线性回归 $\min_w\frac12\|Xw-y\|^2$（$n<d$）有无穷多零损失解。GD 从 $w_0$ 收敛到 $w^*=\arg\min_{Xw=y}\|w-w_0\|_2$——**隐式寻找距初始化最近的零损失解**（因梯度恒在 $X$ 行空间）。

**镜像下降一般化**（定理 8.1.2）：对强凸势 $R$，收敛到 $\arg\min_{Xw=y}D_R(w,w_0)$（Bregman 散度）。

| 算法 | 势函数 | 隐式偏置 |
|:--|:--|:--|
| 梯度下降 | $\frac12\|w\|_2^2$ | 最小 $\ell_2$ 范数 |
| 指数梯度 | $\sum w_i\log w_i$ | 最大熵解 |
| 自然梯度 | Fisher 矩阵 | 分布空间最短路径 |

深度网络中：线性网络 GD 倾向**低秩**解；ReLU 网络倾向低复杂度（path norm）；注意力的 softmax 隐式引入熵正则。**与 Rademacher 的联系**：隐式正则**有效降低函数类复杂度**——GD 能到达的解集 $\mathcal W_{GD}\subset\mathcal W$ 复杂度更低。**灵巧操作含义**：从 demo/pretrain 初始化 = 设 $w_0$，GD 找距此先验最近的解；LoRA 微调显式实现低秩偏好；扩散策略的 score matching 不需额外正则也因隐式正则。

### 6.7 神经正切核 (Neural Tangent Kernel, NTK)

> [!note] 教科书参考
> 本节基于 *Theory of Deep Learning* Ch.9，定理 9.1.1 / 9.2.2 / 9.2.3，公式 9.6–9.11。**本小节被 [[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|Optimization]]、[[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|StochasticProcess]] 反向链接。**

**物理直觉**：为什么参数远多于样本的过参数化网络，训练动力学竟等价于一个固定核回归？当宽度 $m\to\infty$，每个权重训练中只移动 $O(1/\sqrt m)$，网络函数被困在初始化的一阶 Taylor 邻域——**lazy training / kernel regime**。

> [!theorem] Lemma 9.1.1（演化方程）
> 平方损失下梯度流诱导预测向量 $u(t)$ 演化 $\frac{du}{dt}=-H(t)(u(t)-y)$，$[H(t)]_{ij}=\langle\partial_w f(w,x_i),\partial_w f(w,x_j)\rangle$。

二层 ReLU 无穷宽极限的 **NTK 核** $H^*_{ij}=x_i^Tx_j\cdot\mathbb E_{w}[\sigma'(w^Tx_i)\sigma'(w^Tx_j)]$，解析形式 $H^*_{ij}=\frac{x_i^Tx_j}{2\pi}(\pi-\arccos\frac{x_i^Tx_j}{\|x_i\|\|x_j\|})$。

> [!theorem] Lemma 9.2.2 / 9.2.3（NTK 收敛与核区间稳定）
> 若 $m=\Omega(\varepsilon^{-2}n^2\log(n/\delta))$，则 $\|H(0)-H^*\|\le\varepsilon$；若 $m=\Omega(n^6t^2/\varepsilon^2)$，则训练时间 $t$ 内 $\|H(t)-H(0)\|\le\varepsilon$。**关键**：每权重只移动 $O(tn/\sqrt m)$，$H(t)$ 近似常量，动力学退化为线性 ODE $\dot u\approx-H^*(u-y)$。

特征分解 $H^*=\sum_i\lambda_iv_iv_i^T$ 给出沿各特征方向的指数衰减 $v_i^T(u(t)-y)=e^{-\lambda_it}v_i^T(u(0)-y)$——**收敛速率=NTK 谱**。泛化界（Eq. 9.11）：$\text{误差}\le\frac{\sqrt{2\,y^T(H^*)^{-1}y\cdot\mathrm{tr}(H^*)}}n$——泛化取决于标签 $y$ 在 $H^*$ 谱上的分布（低频成分多则泛化好）。

> [!important] NTK 的意义与局限
> **意义**：① 过参数化不是 bug，是 lazy regime 成立的充分条件；② 核区间损失对预测向量是凸二次、全局收敛有保证（这是 [[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|非凸优化里一个可处理的凸化特例]]）；③ 解耦"学到什么"（核 $H^*$）与"如何学"（GD）。**局限**：lazy regime **不覆盖特征学习**（表征恰是初始化随机特征）；依赖 $1/\sqrt m$ 缩放；高维下 NTK 病态、指数收敛被最小特征方向拖慢。**灵巧操作应用**：lazy training 解释了"为何 frozen-rigid + 5min 真机数据微调可行"——大模型小数据更新困在 NTK 邻域、等价固定核回归、避免灾难性遗忘（[[StochasticProcess#5. 学习未知动力学：高斯过程与残差学习|GP]] 是其贝叶斯近亲）。

### 6.8 优化景观与逃离鞍点

> [!note] 教科书参考
> 本节基于 *Theory of Deep Learning* Ch.6（可处理景观）与 Ch.7（逃离鞍点），定义 6.3.2/6.3.3，定理 7.2.1/11.3.5。

**物理直觉**：非凸景观的"可优化性"不取决于全局凸性，而取决于更温和的几何：**局部极小全是全局，且每个鞍点都有严格负曲率方向**——这是矩阵分解、相位恢复等能用 GD 解决的根本。

> [!important] 定义：二阶稳定点 (SOSP) 与 strict saddle
> $w$ 是 $(\varepsilon,\gamma)$-SOSP 当 $\|\nabla f\|\le\varepsilon$ 且 $\lambda_{\min}(\nabla^2f)\ge-\gamma$。$f$ **ridable（可优化）** 当所有局部极小都是全局、所有鞍点都是 strict saddle（$\lambda_{\min}(\nabla^2f)<0$）。

> [!theorem] Theorem 7.2.1（扰动 GD 逃离鞍点）
> 扰动 GD $x_{t+1}=x_t-\eta(\nabla f+\xi_t),\xi_t\sim\mathcal N(0,(r^2/d)I)$，对 $\ell$-梯度-Lipschitz、$\rho$-Hessian-Lipschitz 的 $f$，在 $\tilde O(\ell(f(x_0)-f^*)/\varepsilon^2)$ 步内高概率找到 $\varepsilon$-SOSP。**关键**：维度依赖仅 $\mathrm{polylog}(d)$。

> [!theorem] Theorem 11.3.5（dropout 矩阵分解无伪局部极小）
> dropout 正则的矩阵分解平方损失（适当 $\lambda$）满足：① 所有局部极小都是全局；② 所有鞍点都是 strict saddle。同类景观结果覆盖 matrix sensing/completion、dictionary learning、phase retrieval、tensor decomposition、deep linear nets。

**意义**：strict saddle + no spurious minima 给出**与凸性等价的全局收敛保证**，但无需凸性。**局限**：真实深度 ReLU 网络非 ridable（有 spurious minima 与退化鞍点），且 ReLU 不满足 Hessian Lipschitz。**灵巧操作应用**：扰动 GD 理论正是 [[StochasticProcess#2.2 Itō 引理：噪声不止增加方差，还改变能量的漂移方向|噪声逃逸鞍点]]、[[Optimization#3.2 非凸景观：鞍点、虚假极小与"好景观"的判据|优化鞍点逃逸]]、[[ReinforcementLearning#5.2.3 SAC：黄金标准与"熵即柔顺"|SAC 熵正则]]、扩散训练 noise injection 的统一理论根——**它们都是"用噪声逃离对称造成的鞍点"**。

------

## 7. 批判性综合：失败模式与知识回扣

> [!tip] 本节四拍
> **直觉**（拟合不是理解——SOTA 模型仍在长时程与 sim-to-real 上翻车）→ **推导**（因果断裂、物理陷阱的根源）→ **对比**（反应式 vs 历史/因果感知）→ **落点**（用一条 USB 把全讲串起来记住）。

### 7.1 失败模式一：长视界规划的因果断裂

端到端模型（RT-2、VoxPoser）处理长序列（"煮咖啡=拿杯→放咖啡机→按钮"）常出现重复动作或遗漏步骤。**根源**：① **马尔可夫假设滥用**——多数策略是反应式 $a_t=\pi(s_t)$，假设当前帧含全部信息；② **隐状态丢失**——"我按过按钮了吗"是历史依赖的、当前帧可能不可见；③ **因果推理缺失**——只学了状态间统计相关，没学前置条件/后置效果。**解法**：显式**进度跟踪**（PALM/Guardian，预测"子任务是否完成"）；**分层规划**（LLM 高层因果推理 + ACT/Diffusion 低层物理执行——大脑+小脑，接 [[EmbodiedAI]]）。插 USB 的长程版"找线→对准→插入→确认通电"同样需要进度跟踪，否则会反复尝试已插好的口。

### 7.2 失败模式二：Sim-to-Real 的物理陷阱

即便大规模域随机化 (DR)，摩擦敏感任务（转笔、插 USB）真机仍可能失败。**批判**：DR 前提是真实落在仿真参数分布内，但许多真实效应（软指迟滞、非库伦摩擦、线缆柔性牵拉）在刚体仿真里**根本没建模**——对这些**未建模动力学**，再大随机化也徒劳（与 [[StochasticProcess#3.1 三类不确定性|结构不确定性]]一致）。**方向**：不是无限扩大 DR，而是赋予**在线系统辨识**能力——**RMA** 分析本体感知历史、实时推断环境隐变量并动态调策略，几秒内适应新摩擦/质量（与 [[ReinforcementLearning#9.2 三味药：System ID（减偏差）、DR（增覆盖）、在线自适应（动态校正）|RMA]]、[[ControlTheory#12. 自适应控制与确定性等价|自适应控制]]同一思想）。

### 7.3 知识回扣与记忆图：一条 USB 串起表征学习

> [!abstract] 用一条故事线把全讲复述一遍（刻意复述，为了记忆）
> 我们要插一个 USB。**(§1)** 接触是断续突变的，神经网络的"均值化"会把正插/反插平均成插向空气——这是高维非连续的诅咒。**(§2)** 于是用扩散策略/Flow Matching 把动作建成多峰分布、用 ACT 分块预测整段插入序列并 EWMA 平滑。**(§3)** 但要泛化到没见过的接口，靠的是表征：从 PCA 到 VAE 到对比学习，且通用人类视频表征因具身差异失灵，需 DON 学接触几何的像素级对应、用雅可比正则保稳定。**(§4)** 接口的 3D 形状用点云表征（PointNet++/Transformer），3D Flow 让动作跨载体泛化。**(§5)** 接触后视觉模糊，靠视触觉交叉注意力把局部触觉注册到全局模型——视觉对准、触觉对齐、力控插入。**(§6)** 而这一切"为何能从仿真泛化到真实接口"，由泛化理论回答：好表征=低复杂度=低 Rademacher，域差异界量化 sim-real gap，隐式正则与 NTK 解释过参数化为何不过拟合、小数据微调为何可行。**(§7)** 最后警惕：长程要进度跟踪防因果断裂，sim-real 要在线辨识防物理陷阱。**一条 USB，插完了整座表征学习大厦。**

> [!important] 一张表记住全篇（层 → 问题 → 工具 → 插 USB 角色）
> | 层 | 核心问题 | 关键工具 | 插 USB 的哪一环 |
> |:--|:--|:--|:--|
> | §1 物理本质 | 接触为何坑神经网络 | 流形假设、LCP | 别把正/反插平均成空气 |
> | §2 动作分布 | 多峰怎么建 | 扩散、Flow Matching、ACT | 正插/反插两峰都保留 |
> | §3 表征演进 | 怎么泛化到新接口 | VAE、对比、DON、雅可比正则 | 学接触几何而非语义 |
> | §4 几何表征 | 3D 形状怎么进 | PointNet++、3D Flow | 接口孔位的点云 |
> | §5 多模态 | 视觉模糊后靠谁 | 交叉注意力、Taxim | 视觉对准→触觉对齐 |
> | §6 泛化理论 | 为何能 sim→real | Rademacher、域适应、NTK | 量化 sim-real gap |
> | §7 失败模式 | 还会怎么翻车 | 进度跟踪、RMA | 防重复插、防未建模摩擦 |

> [!tip] 三条贯穿全讲的"暗线"（抓住它们，细节自来）
> 1. **均值坍缩是万恶之源**：从 §1 的接触均值化到 §2 的多峰建模——整条"BC→MDN→IBC→Diffusion/ACT"演进就是在逃离均值坍缩。
> 2. **压缩=泛化=去噪**：信息瓶颈（§3.1）、低维流形降 Rademacher（§6.4）、压缩去噪对偶（[[InformationTheory#5.1 率失真：压缩的理论下界|率失真]]）——**好表征的三个等价面**。
> 3. **优化算法自带正则**：隐式正则（§6.6）、NTK lazy regime（§6.7）、扰动 GD 逃鞍点（§6.8）——"如何学"本身就决定了"学到什么能泛化"，这把表征学习与 [[Optimization]] 钉在一起。

> [!note] 跨领域链接（双向、点对点）
> - **↔ [[ReinforcementLearning]]**：扩散策略被 RL 微调（§2.2）；对比 RL（§3.4）；表征=状态；NTK 解释小数据真机微调。
> - **↔ [[InformationTheory]]**：信息瓶颈=VAE 的 $\beta$（§3.1）；压缩=去噪；泛化需要压缩（§6.4）。
> - **↔ [[Optimization]]**：IBC=能量景观下降；NTK 区间凸化（§6.7）；隐式正则↔近端（§6.6）；鞍点逃逸（§6.8）。
> - **↔ [[ComputationalGeometry]]**：点云/SDF 几何表征（§4）；神经隐式 DeepSDF/NGDF。
> - **↔ [[SignalProcessing]]**：触觉表征、Taxim 仿真（§5.3）；ACT 时间集成=低通（§2.3）；压缩去噪。
> - **↔ [[StochasticProcess]]**：扩散=朗之万/SDE（§2.2）；NTK↔GP（§6.7）；噪声逃鞍点（§6.8）。
> - **↔ [[Dynamics]]**：可微物理（§1.3）；Rodrigues 正运动学模板→RodriNet（§4.3）。
> - **↔ [[ControlTheory]]**：雅可比正则=Lipschitz 稳定（§3.4）；RMA=自适应控制（§7.2）。
> - **↔ [[EmbodiedAI]]**：分层 LLM+ACT（§7.1）；Vision Foundation Models；VLA 用扩散/FM 动作头。

------

## 8. 结论：从拟合到物理理解

大规模数据与生成式模型（Diffusion、Transformer）能拟合极复杂的动作分布。但**拟合不是理解**。未来聚焦：① **可微物理 + 学习**——物理定律作可微层、用物理梯度指导学习；② **因果表征学习**——学状态变量的因果结构图而非像素距离，实现真 OOD 泛化；③ **主动触觉探索**——像人一样主动触摸减少不确定（接 [[InformationTheory#3. 概率接触模型与高斯过程探索|主动感知]]）。机器人的灵巧性终究在物理世界中定义，而非损失曲线的收敛里。

| 范式 | 关键算法 | 动作分布 | 多峰 | 时序一致 | 主要局限 |
|:--|:--|:--|:--|:--|:--|
| **行为克隆** | BC (ResNet/MLP) | 确定性/单峰高斯 | 差（均值化） | 低（需平滑） | 协变量漂移、复合误差 |
| **隐式 BC** | IBC（能量） | 能量景观（隐式） | 好（多极小） | 中 | 推理成本（MCMC） |
| **动作分块** | ACT (CVAE+Transformer) | CVAE latent + 确定性 | 好（经 $z$） | 高（时间集成） | 固定 chunk、训练稳定性 |
| **扩散策略** | DDPM/DDIM/Flow Matching | 分数场/速度场 | 极佳（任意分布） | 高（horizon 预测） | 推理速度（迭代去噪） |

------

## 9. 相关论文 (PapersRecap)

> [!abstract] 知识图谱反向链接
> 以下论文涉及本 Foundation 的表征学习核心主题。

### 视触觉表征
- [[Robot Synesthesia - In-Hand Manipulation with Visuotactile Sensing]] — 视触觉联觉表征
- [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch]] — 触觉点云表征
- [[Learning Visuotactile Skills with Two Multifingered Hands (HATO)]] — 双手视触觉技能
- [[Visual-tactile Pretraining for Humanlike Manipulation Dexterity]] — 视觉触觉自监督预训练
- [[RotateIt - General In-Hand Object Rotation with Vision and Touch|RotateIt]] — 触觉点云 + 跨模态融合

### Diffusion 策略与生成式表征
- [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]] — 规划引导扩散策略
- [[CyberDemo - Augmenting Simulated Human Demonstration for Real-World Dexterous Manipulation]] — 仿真增强表征
- [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware|ACT]] — 动作分块 + CVAE

### 多模态融合与课程学习
- [[Vision-force-fused Curriculum Learning for Robotic Assembly]] — 视觉-力融合课程

### 潜在空间学习
- [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)]] — 快速自适应隐编码
- [[Curriculum-based Sensing Reduction in Simulation to Real-World Transfer for In-hand Manipulation]] — 观测空间课程

### 层级与时序表征
- [[Hierarchical Coordination Multi-Agent RL with Spatio-Temporal Abstraction]] — 时空抽象
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 轨迹表征

### 可解释表征
- [[Weight-sparse transformers have interpretable circuits]] — 稀疏可解释回路

### 物理感知几何表征
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]] — Dynamics-lifted 几何预训练，E(3)-等变
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 动力学感知表征，点级世界模型
- [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] — Rodrigues 正运动学作可学习 action backbone

### 触觉仿真表征
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] — 统一 Deform Map，穿透深度域不变表征
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|STOLA]] — MoE 触觉-语言模型

### VLA 潜空间推理
- [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]] — 潜在时空链式推理，MoT 双系统

### 信息瓶颈与运动生成表征
- [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]] — RL Token 信息瓶颈，残差动作编辑
- [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]] — TP-MoE token 级参数混合，262D 机器人原生扩散

### 项目级真机表征 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-006-In-Context-Hypernet-Adapter|ICHA]]：In-context Transformer → FiLM offsets，零梯度真机适应
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-012-WPTE-Tactile-Encoder|WPTE]]：WM forward prediction 作触觉编码器 pretext，zero-shot sim-to-real
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-009-Discrete-Task-Tokens|VQ Discrete Task Tokens]]：VQ-VAE 离散任务 token + transition graph 安全 replan
