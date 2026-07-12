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

> [!note] 对策一：把物理归纳偏置写进表征（接几何侧）
> 逃离"均值化"的一条正交路线是**换一种表征让不连续变光滑**。[[ComputationalGeometry#5. 神经隐式表示：DeepSDF 与几何学习的前沿|神经隐式表示（DeepSDF/NGDF）]]用一个坐标网络 $f_\theta(x)\to$ 有向距离，并施加 **Eikonal 约束** $\|\nabla_x f_\theta\|=1$——这是把"距离场的物理性质（梯度处处为单位法向）"当**几何物理归纳偏置**硬编码进网络。效果：接触边界不再是训练数据里一个突变的 0/1 标签，而是一条网络输出恒为 0、梯度连续的**零水平集**，梯度天然指向退出接触的方向（对比布尔碰撞的零梯度）。于是"接触在哪、往哪退"从一个断续的分类问题变成一个光滑的回归问题——本讲 §4 的几何表征与 [[ComputationalGeometry]] 在这里接上：**好的几何表征本身就在源头缓解 §1.2 的均值化陷阱**。

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

> [!note] $O(T^2)$ 从哪来（补一步 DAgger 式论证）
> 设每步误分类率为 $\epsilon$（动作偏出专家分布的概率）。在长为 $T$ 的 rollout 中，"**首次**犯错"可能发生在任意步 $t\le T$；一旦在第 $t$ 步漂出训练分布，此后剩余 $\sim(T-t)$ 步都处在无监督覆盖的状态、无恢复机制，逐步累积代价 $\sim O(T-t)$。对首次犯错时刻求期望：$\mathbb E[\text{总代价}]\sim \epsilon\sum_{t=1}^{T}(T-t)=O(\epsilon T^2)$（Ross & Bagnell 的经典界）。对比：能"自我纠错"的方法（DAgger、RL）把它压回 $O(\epsilon T)$。这就是为什么灵巧操作的长 horizon 任务对 BC 尤其致命——$T^2$ 里每一步的接触误差都在放大。

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
> 推理是逆向 SDE 求解，等价于动作空间的朗之万采样 $a_{k-1}=a_k+\frac{\sigma^2}2\nabla_a\log p(a_k\mid s)+\sigma z$。机器人不"计算"动作，而是**跟随概率梯度（分数函数）逐步演化出动作**——天然支持多峰（正插/反插两个峰都保留），且预测整段 action horizon 保证时间平滑、抑制高频抖动。其 score 与 [[StochasticProcess#2.1 SDE：漂移 + 扩散，且扩散是状态相关的|SDE]]、被 RL 微调的路径见 [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|RL §10.1]]。**这一"训练学正向加噪、推理跑逆向去噪"的对称结构，[[StochasticProcess#6.4 扩散策略 = 学出来的逆向 SDE：把 §2 的 SDE 倒过来跑|StochasticProcess §6.4]]从随机过程侧给了它一个镜像证明**：前向是 §2 那条 $dx=f\,dt+g\,dW$ 的 SDE，反向 Anderson 逆向 SDE 的漂移项里恰好含 $\nabla_x\log p_t(x)$——本讲学的 $\epsilon_\theta$（§2.2.2 证其 $=-\sqrt{1-\bar\alpha}\,\nabla\log q$）就是那一项。两侧读的是同一个数学对象，只是一处从"表征/生成"进入、一处从"随机最优控制"进入。

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

上面把训练损失（学 $\epsilon_\theta$）、朗之万推理、"score $=-\epsilon/\sqrt{1-\bar\alpha_t}$" 这几件事直接摆了出来，但它们**为什么成立**被跳过了。下面三小节把这条链补严：前向/反向后验的显式高斯形式（2.2.1）→ 噪声预测与分数匹配的等价（2.2.2）→ 用观测 $s$ 引导多峰采样的 Classifier-Free Guidance（2.2.3）。这三步是"扩散策略能被观测条件化、又保留多峰"的全部数学骨架。

#### 2.2.1 DDPM 前向边缘与反向后验的显式推导（补严）

**前向单步**（人为设计的加噪，与数据无关）：

$$
q(x_t\mid x_{t-1})=\mathcal N\big(x_t;\sqrt{1-\beta_t}\,x_{t-1},\ \beta_t I\big),\qquad \alpha_t:=1-\beta_t,\ \bar\alpha_t:=\prod_{s=1}^{t}\alpha_s.
$$

符号：$x_0$ 是干净动作序列（物理量：action chunk，单位取决于关节角/末端位姿）；$x_t$ 是第 $t$ 级加噪样本（无量纲化后）；$\beta_t\in(0,1)$ 是第 $t$ 步注入方差（噪声强度调度，无单位）；$\alpha_t,\bar\alpha_t$ 是"信号保留率"（$\bar\alpha_t$ 从 1 单调降到 0）。

**为什么能一步跳到任意 $t$（边缘 $q(x_t\mid x_0)$）**：用重参数化 $x_t=\sqrt{\alpha_t}\,x_{t-1}+\sqrt{1-\alpha_t}\,\epsilon_{t-1}$（$\epsilon\sim\mathcal N(0,I)$），把 $x_{t-1}$ 再展开一层：

$$
x_t=\sqrt{\alpha_t\alpha_{t-1}}\,x_{t-2}+\underbrace{\sqrt{\alpha_t(1-\alpha_{t-1})}\,\epsilon_{t-2}+\sqrt{1-\alpha_t}\,\epsilon_{t-1}}_{\text{两个独立高斯之和}}.
$$

两个零均值独立高斯相加，方差直接相加：$\alpha_t(1-\alpha_{t-1})+(1-\alpha_t)=1-\alpha_t\alpha_{t-1}$，故可合并成单个 $\sqrt{1-\alpha_t\alpha_{t-1}}\,\bar\epsilon$。归纳到底：

$$
\boxed{\,q(x_t\mid x_0)=\mathcal N\big(x_t;\sqrt{\bar\alpha_t}\,x_0,\ (1-\bar\alpha_t)I\big)\,}\quad\Longleftrightarrow\quad x_t=\sqrt{\bar\alpha_t}\,x_0+\sqrt{1-\bar\alpha_t}\,\epsilon.
$$

这正是训练损失 $L(\theta)=\mathbb E\|\epsilon-\epsilon_\theta(\sqrt{\bar\alpha_k}a_0+\sqrt{1-\bar\alpha_k}\epsilon,k,s)\|^2$ 里那个 $\sqrt{\bar\alpha_k}a_0+\sqrt{1-\bar\alpha_k}\epsilon$ 的来历——不是凑出来的，是前向链的闭式边缘。

**反向后验 $q(x_{t-1}\mid x_t,x_0)$**（采样时要"回退一步"的目标分布）。虽然反向 $q(x_{t-1}\mid x_t)$ 不可解，但**在给定 $x_0$ 时**可由 Bayes 求出且仍是高斯：

$$
q(x_{t-1}\mid x_t,x_0)=\frac{q(x_t\mid x_{t-1})\,q(x_{t-1}\mid x_0)}{q(x_t\mid x_0)}\ \propto\ \exp\!\Big[-\tfrac12\Big(\tfrac{(x_t-\sqrt{\alpha_t}x_{t-1})^2}{\beta_t}+\tfrac{(x_{t-1}-\sqrt{\bar\alpha_{t-1}}x_0)^2}{1-\bar\alpha_{t-1}}\Big)\Big].
$$

对 $x_{t-1}$ **配方**（只保留含 $x_{t-1}$ 的项）。二次项系数给出精度（方差倒数）：

$$
\frac1{\tilde\beta_t}=\frac{\alpha_t}{\beta_t}+\frac1{1-\bar\alpha_{t-1}}=\frac{\alpha_t(1-\bar\alpha_{t-1})+\beta_t}{\beta_t(1-\bar\alpha_{t-1})}=\frac{1-\bar\alpha_t}{\beta_t(1-\bar\alpha_{t-1})}\ \Rightarrow\ \tilde\beta_t=\frac{1-\bar\alpha_{t-1}}{1-\bar\alpha_t}\beta_t,
$$

（分子化简用了 $\alpha_t-\alpha_t\bar\alpha_{t-1}+\beta_t=\alpha_t-\bar\alpha_t+1-\alpha_t=1-\bar\alpha_t$）。一次项系数 $\times\tilde\beta_t$ 给出均值：

$$
\tilde\mu_t(x_t,x_0)=\frac{\sqrt{\alpha_t}(1-\bar\alpha_{t-1})}{1-\bar\alpha_t}x_t+\frac{\sqrt{\bar\alpha_{t-1}}\,\beta_t}{1-\bar\alpha_t}x_0.
$$

**物理读法**：反向均值是"当前带噪样本 $x_t$"与"猜测的干净动作 $x_0$"的凸组合，权重由信噪比 $\bar\alpha$ 决定——早期（$t$ 大、$\bar\alpha$ 小）更信 $x_0$ 的猜测，后期更信 $x_t$。网络其实只需预测 $x_0$（或等价地预测 $\epsilon$），就能算出这个后验均值去回退一步。

#### 2.2.2 噪声预测 $\epsilon_\theta$ ↔ denoising score matching 的等价（补严）

§2.2 的 callout 直接写了 "score $=-\epsilon/\sqrt{1-\bar\alpha}$"，这里证明它。由 2.2.1 的边缘 $q(x_t\mid x_0)=\mathcal N(\sqrt{\bar\alpha_t}x_0,(1-\bar\alpha_t)I)$，其对数关于 $x_t$ 求梯度（**条件分数**）：

$$
\nabla_{x_t}\log q(x_t\mid x_0)=\nabla_{x_t}\!\Big[-\frac{\|x_t-\sqrt{\bar\alpha_t}x_0\|^2}{2(1-\bar\alpha_t)}\Big]=-\frac{x_t-\sqrt{\bar\alpha_t}x_0}{1-\bar\alpha_t}=-\frac{\epsilon}{\sqrt{1-\bar\alpha_t}},
$$

最后一步代入 $x_t-\sqrt{\bar\alpha_t}x_0=\sqrt{1-\bar\alpha_t}\,\epsilon$。**Denoising score matching**（Vincent 2011）的核心恒等式是：学边缘分数 $s_\theta(x_t,t)\approx\nabla\log q(x_t)$ 时，回归目标可换成**逐样本的条件分数** $\nabla\log q(x_t\mid x_0)$（两者的期望平方误差只差一个与 $\theta$ 无关的常数）。因此网络若去拟合 $\epsilon$，就等价于拟合分数，二者相差一个**确定性因子** $-1/\sqrt{1-\bar\alpha_t}$：

$$
s_\theta(x_t,t)=-\frac{\epsilon_\theta(x_t,t)}{\sqrt{1-\bar\alpha_t}}.
$$

这把三样东西钉在了一起：**训练目标（回归 $\epsilon$）＝分数匹配＝朗之万采样的梯度场**。噪声预测只是分数的一个方便重参数化——工程上回归 $\epsilon$ 数值更稳（目标方差恒为 1），理论上它就是 [[StochasticProcess#2.1 SDE：漂移 + 扩散，且扩散是状态相关的|逆向 SDE]] 的漂移项。

#### 2.2.3 Classifier-Free Guidance：用观测"引导"多峰采样的贝叶斯推导

扩散策略要的是**条件**分布 $p(a\mid s)$（$s$＝视觉+本体观测），且常希望"更服从当前观测"以提高精度。CFG 给出无需额外分类器的做法。起点是 Bayes：

$$
p(a\mid s)=\frac{p(a)\,p(s\mid a)}{p(s)}\ \Rightarrow\ \nabla_a\log p(a\mid s)=\nabla_a\log p(a)+\underbrace{\nabla_a\log p(s\mid a)}_{\text{隐式分类器梯度}}
$$

（$\nabla_a\log p(s)=0$，因 $p(s)$ 与 $a$ 无关）。于是**隐式分类器梯度**可由两个分数之差得到，无需真训一个分类器 $p(s\mid a)$：

$$
\nabla_a\log p(s\mid a)=\nabla_a\log p(a\mid s)-\nabla_a\log p(a).
$$

要"放大观测的约束力"，就对分类器项加温度 $w$，即从锐化分布 $\tilde p_w(a\mid s)\propto p(a)\,p(s\mid a)^w$ 采样。它的分数是无条件与条件分数的**外插**：

$$
\nabla_a\log\tilde p_w=\nabla_a\log p(a)+w\big[\nabla_a\log p(a\mid s)-\nabla_a\log p(a)\big]=(1-w)\,\nabla_a\log p(a)+w\,\nabla_a\log p(a\mid s).
$$

用 2.2.2 的 $s=-\epsilon/\sqrt{1-\bar\alpha}$ 换回噪声预测（$\varnothing$＝无条件的 null token、$c$＝条件 $s$）：

$$
\boxed{\ \tilde\epsilon=(1-w)\,\epsilon_\theta(x_t,\varnothing)+w\,\epsilon_\theta(x_t,c)\ }
$$

$w=1$ 退回普通条件采样；$w>1$ **锐化**（更贴合观测、牺牲多样性）；$w=0$ 纯无条件。训练上只需以概率 $p$ 随机把条件置空（dropout $c\to\varnothing$），一张网络同时学 $\epsilon_\theta(\varnothing)$ 与 $\epsilon_\theta(c)$。

> [!important] CFG 在灵巧操作里的"多峰-精度"旋钮
> 插 USB 有正插/反插两个合法峰。$w$ 小 → 保留两峰（多样、鲁棒但可能不够精准）；$w$ 大 → 强制服从当前观测 $s$（视觉看到的接口朝向），把采样拉向与该接口几何一致的那个峰、微米级对齐。这就是 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|Continuation/平滑化暗线]]在生成式策略里的化身——从"平坦的无条件先验"逐步锐化到"被观测约束的尖锐后验"。其逆向 SDE / 朗之万根源见 [[StochasticProcess]]，被 RL 微调（把 $w$、去噪步数当可学超参）的路径见 [[ReinforcementLearning#10.1 扩散策略：多峰分布的终极解（兑现 §5.1.2 的伏笔）|RL §10.1]]。

### 2.3 ACT：动作分块处理长时相关

ACT (Action Chunking with Transformers) 是另一条解多峰+误差累积的强力路线（详见 [[ACT - Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware|ACT 精读]]）。

**动作分块**：不预测单步、而预测未来 $k$ 步的 chunk，把时间视界从 $T$ 压到 $T/k$、显著减少自回归误差累积。**时间集成**：每步对重叠的多个预测块加权平均 $a_t=\sum_i w_i\hat a_t^{(t-i)}$——这本质是个**低通滤波 (EWMA)**（又一次与 [[SignalProcessing#1.4 数字滤波器：去噪、延迟与可控性的三角权衡|信号处理]]同形），滤掉高频控制噪声、合惯性约束。**CVAE 风格变量**：用 CVAE 学潜在"风格" $z$（演示里的速度/力度/接近角等任务无关信息），KL 正则约束 $z\sim\mathcal N(0,I)$ 保潜空间连续；推理时固定 $z=0$ 得确定行为或采样得多样行为。

> [!note] 为什么"分块"能压住 §2.1 的 $O(T^2)$ 复合误差（接 RL 侧）
> §2.1 证过 BC 的复合误差是 $O(\epsilon T^2)$，其中 $T$ 是决策次数。动作分块的关键洞察：**把有效决策 horizon 从 $T$ 砍到 $T/k$**——一次前向输出 $k$ 步开环执行，只在块边界重新观测、重新决策，故"有机会犯首次错误并漂出分布"的决策点数从 $T$ 降到 $T/k$。代回复合误差界，$O(\epsilon (T/k)^2)$，误差被 $k^2$ 压缩。这正是 [[ReinforcementLearning#7.4 模仿学习与策略蒸馏：把演示收编进统一梯度|RL §7.4（Action chunking：把有效 horizon 从 $T$ 砍到 $T/H$）]]从模仿学习/统一梯度视角给出的同一结论——本讲从"生成式动作表征"进入，RL 从"复合误差的 no-regret 修复谱系（DAgger→chunking）"进入，落到同一个 $k$ 倍杠杆上。**代价**：块内开环，$k$ 太大则对块内扰动失去反馈响应（与实时重规划 receding-horizon 权衡），故 $k$ 是"复合误差 ↓"与"反馈及时性 ↓"之间的旋钮。

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

> [!note] 补严：VAE 的 ELBO 从哪来、重参数化为何必要
> §2.3 的 ACT、上面的 VAE bullet 都用了"ELBO + 重参数化"却没推。这里补上——它是所有隐变量生成式表征（含扩散、CVAE 风格变量）的公共地基。
>
> **① ELBO 是 $\log p_\theta(x)$ 的一个可优化下界。** 目标是最大化数据似然 $\log p_\theta(x)=\log\int p_\theta(x,z)\,dz$（$x$＝观测，如一帧图/一段 action chunk；$z$＝低维隐编码，无量纲）。这个积分对 $z$ 不可解。引入一个可学习的**近似后验** $q_\phi(z\mid x)$（encoder，输出高斯参数 $\mu_\phi,\sigma_\phi$），做恒等变形（每一步不跳）：
> $$\log p_\theta(x)=\mathbb E_{q_\phi(z\mid x)}\big[\log p_\theta(x)\big]=\mathbb E_{q_\phi}\Big[\log\frac{p_\theta(x,z)}{p_\theta(z\mid x)}\Big]=\mathbb E_{q_\phi}\Big[\log\frac{p_\theta(x,z)}{q_\phi(z\mid x)}\Big]+\mathbb E_{q_\phi}\Big[\log\frac{q_\phi(z\mid x)}{p_\theta(z\mid x)}\Big].$$
> 第一步：$\log p_\theta(x)$ 不含 $z$，对 $q_\phi$ 取期望不变。第二步：$p_\theta(x)=p_\theta(x,z)/p_\theta(z\mid x)$。第三步：分子分母同乘 $q_\phi$ 再拆成两个对数期望。第二项恰是 $\mathrm{KL}\!\big(q_\phi(z\mid x)\,\|\,p_\theta(z\mid x)\big)\ge 0$（KL 非负），故第一项就是下界：
> $$\log p_\theta(x)=\underbrace{\mathbb E_{q_\phi}\!\big[\log p_\theta(x\mid z)\big]}_{\text{重构项}}-\underbrace{\mathrm{KL}\!\big(q_\phi(z\mid x)\,\|\,p(z)\big)}_{\text{压缩/正则项}}+\mathrm{KL}(q_\phi\|p_\theta(z\mid x))\ \ge\ \text{ELBO}.$$
> （末式把 $p_\theta(x,z)=p_\theta(x\mid z)p(z)$ 代入 ELBO 拆开。）**物理读法**：最大化 ELBO＝"既要能从 $z$ 重构出 $x$（重构项），又要让编码分布贴近先验 $p(z)=\mathcal N(0,I)$（KL 项）"——这就是 encoder 的两难，也正是下一条 note 里 $\beta$ 权衡的对象。而下界与真似然之间的缝隙恰是 $\mathrm{KL}(q_\phi\|p_\theta(z\mid x))$：近似后验越准，下界越紧。
>
> **② 重参数化：让"采样"可反传。** KL 与重构项里都要对 $z\sim q_\phi(z\mid x)$ 采样，但"采样"这个操作对 $\phi$ 不可导——梯度传不进 encoder。**重参数化技巧**把随机性挪到一个与 $\phi$ 无关的外部噪声上：$z=\mu_\phi(x)+\sigma_\phi(x)\odot\epsilon,\ \epsilon\sim\mathcal N(0,I)$（$\odot$＝逐元素乘）。现在 $z$ 是 $\phi$ 的**确定性可微函数**（随机性全在 $\epsilon$ 里），于是 $\nabla_\phi\mathbb E_{q_\phi}[\,\cdot\,]=\mathbb E_\epsilon[\nabla_\phi(\cdot)]$，可直接 autograd。对比朴素的 score-function/REINFORCE 估计（把采样当黑箱、用 $\nabla_\phi\log q_\phi$ 加权），重参数化梯度**方差低一到两个数量级**——这正是 §2.3 ACT 代码里 `z = mu + exp(0.5*logvar)*randn_like(mu)` 那一行的理论出处，也是扩散/CVAE 能稳定训练的前提。
>
> **挂到暗线（Continuation/平滑化）**：$\beta$-VAE 实践里常做 **KL annealing**——训练初期令 $\beta\approx 0$（只求重构，问题近似无约束、易优化），再把 $\beta$ 逐步升到目标值引入压缩压力。这与 [[Optimization#5.4 阶段四：可微物理与平滑化（让梯度穿过接触）|接触平滑]]、[[ReinforcementLearning#7.3 自动课程与开放式学习：把探索抬到任务空间|课程学习]]、§2 扩散的"噪声→数据"是**同一条 Continuation 暗线**：先解平滑近凸的子问题，再逐步引入真难度。

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

**对比 RL**：稀疏奖励下把 RL 重构为表示学习——用 InfoNCE 在潜空间拉近能到达目标的"状态-目标对"$(s,g)$、推远无关轨迹；**为什么学到的内积能当值函数**（补一步）：InfoNCE 的 Bayes-最优 critic 收敛到密度比 $\log\frac{p(g\mid s,a)}{p(g)}$（把"正样本 vs 边缘背景"分开的最优打分即该对数密度比），而 $p(g\mid s,a)$ 正是"从 $(s,a)$ 出发未来到达 $g$"的概率，故内积 $\langle\phi(s),\phi(g)\rangle$ **单调于到达概率**、可直接充当（目标条件）值函数，规划可在潜空间几何里做（接 [[ReinforcementLearning#7. 探索：稀疏奖励下，如何"撞见"转笔成功|RL 探索]]）。

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

> [!note] 补严：为什么"逐点映射 + 对称聚合"就能表达一切置换不变函数
> 定理陈述了但没说**为什么**。分两半看，都不跳步。
>
> **① 充分性（这个结构确实置换不变）——一行即证。** 设排列 $\pi$ 打乱下标，$f(\{p_{\pi(i)}\})=\rho\big(\sum_i\phi(p_{\pi(i)})\big)$。加法满足交换律，$\sum_i\phi(p_{\pi(i)})=\sum_i\phi(p_i)$ 与顺序无关，故 $f$ 输出不变。max/mean 同理（都是对称聚合算子）。**这就是 PointNet 用 $\max$ 的全部理由**：点云无序（$N$ 个点的 $N!$ 种排列是同一个物体），聚合算子必须把顺序信息"洗掉"。
>
> **② 必要性（任何置换不变 $f$ 都能写成这个形式）——构造性证明的关键一步。** 难点在证"这个结构不丢表达力"。对**可数域**上的集合，构造思路是：找一个把整个集合**单射**编码进一个实数（或低维向量）的 $\phi$。取 $\phi(p)=$ 某个使 $\sum_{p\in\mathcal P}\phi(p)$ 对不同集合取不同值的映射（如把每个点编码成一个"素数幂/唯一前缀码"，其和唯一确定这个 multiset——这一步用到集合元素可数），则 $z=\sum_p\phi(p)$ 是集合的**无损充分统计量**；既然 $z$ 唯一决定 $\mathcal P$，任何以 $\mathcal P$ 为输入的置换不变 $f$ 都能写成 $f=\rho(z)$，令 $\rho=f\circ(\text{解码})$ 即可。**直觉**：对称聚合看似"有损"，但只要 $\phi$ 的维度够高，$\sum\phi$ 可以是一个可逆的集合指纹——不变性不必以牺牲表达力为代价。（连续域与固定维度下需 $\phi$ 维度 $\ge N$ 才严格成立，PointNet 用高维 $h(p)$ + $\max$ 是这一构造的工程近似；这也解释了 §4.1 末尾说的"PointNet 缺局部几何"——单个全局 $\max$ 指纹丢了邻域结构，正是 §4.2 PointNet++ 要补的。）
>
> **挂到暗线（POMDP→belief→latent）**：$z=\sum_p\phi(p)$ 是集合的**充分统计量**——把一个变长、无序的观测集合压成定长向量而不丢任务信息。这与 [[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|POMDP]] 里 belief 作为"历史的充分统计量"、与 §4.6 注意力把观测窗口压成 latent 是**同一条 POMDP→belief→latent 暗线**：区别仅在聚合算子——集合用对称的 $\sum/\max$（要置换不变），序列用带位置编码的注意力（要保留顺序）。**灵巧操作落点**：一只手 20+ 触点的接触集合、场景点云、多指指尖状态，都可用这一"逐点编码 + 对称聚合"压成可控 latent。

**PointNet** 直接应用：$\text{PointNet}(\mathcal P)=\gamma(\max_{p}h(p))$。物理直觉：$h_i(p)$ 是"探测函数"检测某几何特征（角点/平面），$\max$ 问"这种特征**是否存在**"。**局限**：缺局部几何建模，每点独立处理。

### 4.2 PointNet++：层级局部特征

模仿 CNN 局部感受野：**FPS**（最远点采样，保覆盖均匀）→ **Ball Query**（半径 $r$ 内取 $K$ 邻居）→ **Mini-PointNet**（逐邻域提特征）→ 递归。用**相对坐标** $(p_j-p_i)$ 保平移不变：$f_i^{(l+1)}=\text{PointNet}(\{p_j-p_i:p_j\in\mathcal N(p_i,r)\})$。

### 4.3 几何不变性的编码

物体旋转/平移不应改变抓取策略本质，需 **SE(3)-等变/不变**网络：$f(T\cdot\mathcal P)=T\cdot f(\mathcal P)$（等变）或 $=f(\mathcal P)$（不变）。**Vector Neurons** 把标量特征换成 3D 向量特征、用旋转等变线性层。**T-Net** 数据驱动对齐 $\mathcal P'=\mathcal P\cdot T_{pred}$，正则 $\|I-TT^T\|_F^2$ 约束近正交。

> [!abstract] 动作结构先验：RodriNet
> [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] 与通用 SE(3)-等变网络互补：后者关心外部坐标变换的等变，RodriNet 关心机器人内部 joint/link 特征如何沿运动学树传播——它把 [[Dynamics#2.2 旋转群 SO(3)、李代数 so(3) 与 Rodrigues 公式|Rodrigues 正运动学模板]]做成可学习 backbone，是高 DoF 动作表征里"结构化 action mixer"的代表。

### 4.4 Point Transformer 与 3D Flow

**Point Transformer** 把自注意力引入点云，局部自注意力用位置编码编码相对几何位置——自适应邻域权重（vs PointNet++ 固定聚合），表达力更强。这里的两个记号需点明（否则易跳步）：$\delta=\theta(p_i-p_j)$ 是把**相对坐标** $p_i-p_j$ 过一个小 MLP $\theta$ 得到的位置编码（同时加到注意力权重与被聚合的 value 上，让"几何有多近"直接调制"注意多强"）；$\alpha$ 是由查询-键关系算出的注意力向量。其自注意力机理（为何除 $\sqrt d$、为何要位置编码）在 [[RepresentationLearning#4.6 序列与注意力表征：从无序集合到有序序列|§4.6]] 统一讲透——区别仅在：序列用**顺序**位置编码，点云用**3D 相对坐标**位置编码。

> [!tip] 3D Flow：载体无关的动作表征（Wenlong Huang, Stanford SVL）
> **动作的本质是 3D 的**——人闭眼也能在 3D 空间移动手臂。传统动作表征（EE 位姿、关节指令）无法跨载体泛化。**3D Flow**：在每个连杆按 URDF 网格采样端点 → 正运动学 → **点流**；场景也用 RGBD→点云，**状态与动作模态统一**、对点数量不变、自动适配不同 DoF/夹爪。**PointWorld (Stanford 2026)** 将其用于 3D 世界模型，发现：① PTV3 等现代 Transformer 在相近内存下可扩容至图基模型的 ~300×；② **仅夹爪 3D 点流 > 全身点流 > 低维表征**；③ 模型隐式学到目标检测、材料估计、形状补全、物体间动态。**对灵巧操作**：每个手指连杆都可采样为点流，无需设计手指专用动作空间。
> （旁注：机器人预训练→微调迁移效率比 NLP 低 ~100×，要达 NLP 水平需 ~1.25 亿小时数据——这激励了世界模型作为更高效预训练目标，接 [[ReinforcementLearning#6.1 Model-Based RL：在想象中转笔|MBRL]]、[[EmbodiedAI]]。）

### 4.5 面向学习的旋转表示：为什么神经网络回归旋转要用 6D

> [!tip] 本节四拍
> **直觉**（网络要输出物体/手的 6D pose，旋转那部分该用什么数？选错了，数据再好也学不动）→ **推导**（欧拉角万向死锁 → 四元数 double cover → Zhou 2019 连续性定理 → 6D + Gram-Schmidt）→ **对比**（"几何参数化"vs"学习表示选择"是两个正交目标）→ **落点**（pose 估计 / 扩散动作头 / RodriNet 都用 6D）。

到 §4.4 为止我们让网络"读"几何（点云）。反过来，当网络要**输出**一个旋转（物体位姿估计、扩散策略的旋转动作、手腕目标姿态），它必须先选定一个把 $SO(3)$ 编码成实向量的**表示**作为回归目标。这个选择不是美学问题——**表示的不连续性会让"相近的旋转"映到"相距很远的目标向量"，从而把一个本可学的回归变成病态回归**（又一次踩中 §1.2 / §2 的"均值坍缩"：目标多值/不连续，MSE 把它们平均到无效点）。

**① 欧拉角：万向节死锁 (gimbal lock) + wrap-around 不连续。** 欧拉角用 3 个数 $(\phi,\theta,\psi)$。当中间轴转到 $\pm90°$，第一、第三轴对齐、丢一个自由度——旋转到欧拉角的映射在此**雅可比奇异**，附近微小旋转变化对应剧烈欧拉角跳变；再加上角度的 $2\pi\equiv 0$ 环绕（$359°$ 与 $1°$ 数值相距 $358$ 却几何相邻），回归目标处处可能撕裂。

**② 四元数：double cover 致目标多值。** 单位四元数 $q\in S^3$ 通过 $SU(2)\!\to\!SO(3)$ 的 **2:1 覆盖**映到旋转：$q$ 与 $-q$ 表示**同一个** $R$。后果：同一物理姿态在数据集里可能被标注成 $q$ 或 $-q$，网络面对一个**双值目标**。若用 MSE，两个等价标签把梯度往相反方向拉，网络被迫收敛到它们的"中点"$q\approx 0$（非法四元数）——正是接触均值化在旋转空间的翻版。即便人为规定"取 $q_w\ge 0$ 半球"，这条缝合线上（$q_w=0$）目标仍不连续。

**③ Zhou et al. 2019 连续性定理：$SO(3)$ 需 $\ge$5 维连续嵌入。** 把"表示"严格定义为一对映射：编码 $g:SO(3)\to\mathbb R^n$ 与解码 $f:\mathbb R^n\to SO(3)$，满足 $f\circ g=\mathrm{id}$（网络在 $\mathbb R^n$ 里回归、再解码回旋转）。称该表示**连续**当 $g$ 存在连续逆（即 $f$ 在 $g$ 的像上连续）。

> [!theorem] 连续旋转表示的维度下界 (Zhou et al., CVPR 2019)
> 对 $SO(3)$，任何维度 $n\le 4$ 的表示（欧拉角 $n{=}3$、轴角 $n{=}3$、四元数 $n{=}4$）都**不可能连续**；连续表示要求 $n\ge 5$。
>
> **为什么**（拓扑原因，不跳步）：$SO(3)$ 同胚于实射影空间 $\mathbb{RP}^3$，拓扑非平凡（不可缩、有"扭结"）。一个连续单射 $g$ 会把 $SO(3)$ 同胚嵌入 $\mathbb R^n$ 的一个子集；而低维欧氏空间容不下 $\mathbb{RP}^3$ 这种非平凡拓扑而不产生"接缝"（连续性在接缝处破裂）——四元数的接缝正是 $q\sim -q$ 的对径粘合。维度够高（$\ge 5$）才有空间把这个粘合"摊平"成无接缝的嵌入。

**6D 表示 + Gram-Schmidt（最实用的 $n=6$ 构造）。** 网络输出 $\mathbb R^6$，视作两个 3D 向量 $[\,\mathbf a_1\,|\,\mathbf a_2\,]$；用 Gram-Schmidt 正交化恢复旋转矩阵 $R=[\,\mathbf b_1\,|\,\mathbf b_2\,|\,\mathbf b_3\,]$：

$$
\mathbf b_1=\frac{\mathbf a_1}{\|\mathbf a_1\|},\qquad
\mathbf b_2=\frac{\mathbf a_2-(\mathbf b_1^{\!\top}\mathbf a_2)\,\mathbf b_1}{\|\mathbf a_2-(\mathbf b_1^{\!\top}\mathbf a_2)\,\mathbf b_1\|},\qquad
\mathbf b_3=\mathbf b_1\times\mathbf b_2 .
$$

符号：$\mathbf a_1,\mathbf a_2\in\mathbb R^3$ 是网络原始输出（无量纲）；$\mathbf b_1$ 取第一列方向、$\mathbf b_2$ 减去在 $\mathbf b_1$ 上的投影后归一（施密特正交化）、$\mathbf b_3$ 由叉积补成右手系。这个 $\mathbb R^6\to SO(3)$ 映射**处处连续、满射**，且只要 $\mathbf a_1,\mathbf a_2$ 线性无关就良定义——回归目标连续，网络显著更易学、pose 误差更低（Zhou 实测 6D/5D ≫ 四元数/欧拉角）。

> [!important] "几何参数化"与"学习表示选择"是两个正交目标（别混）
> [[Dynamics#2.2 旋转群 SO(3)、李代数 so(3) 与 Rodrigues 公式|Rodrigues / 指数映射 $\exp:\mathfrak{so}(3)\to SO(3)$]] 追求的是**最少参数 + 李群结构**：给定角速度 $\boldsymbol\omega$ 紧凑地算出 $R$，3 个数最优、是物理/几何的语言。**学习表示选择**追求的是**回归目标的连续性**：宁可冗余（$6>3$）也要让"网络输出空间 → $SO(3)$"处处连续可微。前者答"如何紧凑描述一个已知旋转"，后者答"如何让神经网络的输出到 $SO(3)$ 的映射不撕裂"——**同一个 $SO(3)$，两种诉求下最优维度相反**。理解这一点，就不会再纠结"轴角明明 3 维够用，为何回归非要 6 维"。

**灵巧操作落点**：物体 6D pose 估计、扩散/FM 策略输出的旋转动作分量、手腕/指尖目标姿态回归，一律用 6D 头。[[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]]（§4.3、§9）则把这一思想推进一层——不止输出层，连内部沿运动学树传播 link 姿态时都用 Rodrigues 模板作可学习 backbone；它与本节互补：本节保证**输出表示连续**，RodriNet 保证**中间传播结构化**。论文原文见 [[On the Continuity of Rotation Representations in Neural Networks|Zhou et al. 2019]]。

### 4.6 序列与注意力表征：从无序集合到有序序列

> [!tip] 本节四拍
> **直觉**（§4 处理的是**无序集合**（点云，置换不变）；但触觉时间流、action chunk、演示轨迹是**有序序列**，顺序里藏着因果——pooling 会把它抹掉）→ **推导**（scaled dot-product 自注意力 → 多头 → 位置编码 → 为何胜过 RNN）→ **对比**（ICL＝前向里隐式做梯度下降 / fast-weights；元学习与超网络）→ **联系**（与 [[RepresentationLearning#6.7 神经正切核 (Neural Tangent Kernel, NTK)|NTK]] 的"学习即前向"同构、与 [[RepresentationLearning#2.3 ACT：动作分块处理长时相关|ACT]] 的 Transformer 呼应、挂到 POMDP→belief→latent 暗线）。

§4.1 的 Deep Sets 教我们处理**无序**输入（对称聚合抹掉顺序，这正是点云要的）。但操作里的许多信号恰恰**有序**：触觉波形随时间演化、action chunk 是时间序列、专家演示是轨迹。此时"抹掉顺序"是灾难——"先接触再滑移"和"先滑移再接触"是两回事。序列表征的主力工具是**注意力**，而 §2.3 的 ACT、§5.2 的交叉注意力其实都已在用它，这里把它的机理讲透。

**① Scaled dot-product self-attention。** 给定 $n$ 个 token 堆成 $X\in\mathbb R^{n\times d}$，线性投影出查询/键/值 $Q=XW_Q,\ K=XW_K,\ V=XW_V$，则

$$
\mathrm{Attn}(Q,K,V)=\mathrm{softmax}\!\Big(\frac{QK^\top}{\sqrt{d_k}}\Big)V .
$$

**物理读法**：每个 token 用它的 $Q$ 去"问"——"谁与我相关"，与所有 $K$ 做内积算相关度，softmax 成权重，再对 $V$ 加权取回信息——**基于内容的软检索**。**为什么除 $\sqrt{d_k}$（不跳步）**：若 $Q,K$ 各分量独立、均值 0 方差 1，则内积 $Q_i^\top K_j=\sum_{l=1}^{d_k}Q_{il}K_{jl}$ 是 $d_k$ 个独立零均值单位方差乘积之和，方差为 $d_k$。$d_k$ 一大（如 64），未缩放的 logit 幅度 $\sim\sqrt{d_k}$ 过大，softmax 落进饱和区（一个权重趋 1、其余趋 0），梯度几乎为零、学不动。除以 $\sqrt{d_k}$ 把 logit 方差拉回 $\approx 1$，softmax 保持在有梯度的区间。

**② Multi-head。** 单个 softmax 只能给出**一种**注意力模式（本质是一次加权平均）。多头把 $Q,K,V$ 投到 $h$ 个 $d/h$ 维子空间并行做注意力再拼接：$\mathrm{MHA}=\mathrm{Concat}(\text{head}_1,\dots,\text{head}_h)W_O$。这样不同头能捕不同关系——如"几何邻接"一头、"力相关"一头、"长程依赖"一头，避免被单一平均模式锁死。

**③ 位置编码：把"集合"重新变回"序列"。** 自注意力对输入排列是**置换等变**的（打乱 token 顺序，输出同样打乱）——这对点云是优点（§4.1 要的正是它），但对序列是致命的：不给位置信息，Transformer 眼里"序列"退化成"集合"，丢掉顺序。正弦位置编码 $PE_{(pos,2i)}=\sin(pos/10000^{2i/d}),\ PE_{(pos,2i+1)}=\cos(\cdot)$ 把绝对位置注入，其巧妙处在于**相对位移 $\Delta pos$ 对应编码空间里一个固定线性变换（旋转）**，于是模型能按"相对偏移"注意（RoPE、可学习位置编码是同一诉求的变体）。

**④ 为什么注意力适合序列建模（对比 RNN/CNN）。** RNN 里位置 $i,j$ 间的信息要走 $O(|i-j|)$ 步、梯度沿途衰减（长程依赖学不到）；自注意力让**任意两位置一步直连**（路径长 $O(1)$），且全序列并行（无时序展开）。代价是 $O(n^2)$ 复杂度，但 action chunk 的 $n$ 很小（几十步），完全可承受。**这正是 §2.3 ACT 用 Transformer decoder、以"各未来时间步"为 query、cross-attention 关注观测的原因**——它要的就是"任意未来步都能直接看到任意观测 token"的长程相干。

**⑤ In-Context Learning ＝前向里隐式做梯度下降 / fast-weights。** 训练好的 Transformer，给它上下文 $(x_1,y_1,\dots,x_k,y_k,x_{query})$，**不更新任何权重**就能预测 $y_{query}$——这就是 ICL。理论视角（不跳步）：

- **隐式 GD**：一层线性自注意力的前向计算，可被构造成"对上下文里的线性回归损失做一步梯度下降"——前向传播里就**隐式算出了一个权重更新** $\Delta W$，再作用到 $x_{query}$。故"学习"没发生在反向传播里，而发生在**前向**里。
- **Fast-weights 视角**（Schmidhuber）：注意力 $\sum_i v_i k_i^\top$ 是一个由上下文即时构造的**外积记忆矩阵**（"快权重"），作用到 query 上——等价于一个**数据生成的临时线性层**。

> [!important] ICL 与 NTK：两种"学习即前向"的同构
> [[RepresentationLearning#6.7 神经正切核 (Neural Tangent Kernel, NTK)|NTK]] 说"训练 ≈ 固定核回归"（lazy regime，参数几乎不动、动力学退化为线性）；ICL 说"一个固定网络在**前向**里就做了回归"。二者都把"适应"归约成**固定特征空间里的一次核/线性运算**——这解释了为何大模型 + 极少上下文样本就能适应新任务，也是 WMTS 真机零梯度适配的理论底座。**注意力不是 ICL 的唯一载体**：[[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|Is Attention Required for ICL?]] 表明某些循环/状态空间架构也能涌现 ICL，故 ICL 更像是"深度序列模型表达力 + 训练分布"的性质，而非 attention 独有。

**⑥ 元学习与超网络 (hypernetwork)。** ICL 是**元学习**（learning to learn）的一个特例——把"内循环适应"塞进前向传播。另一条路是**超网络**：一个网络 $g_\psi$ 直接**生成**另一个网络 $f_\theta$ 的权重，$\theta=g_\psi(c)$（$c$＝任务/上下文），从而把"按任务梯度微调 $f$"摊销成"一次前向生成权重"。[[Transformers as Meta-Learners for Implicit Neural Representations|Transformers as Meta-Learners]] 就用 Transformer 超网络从信号生成隐式神经表示（坐标 MLP）的权重——**元学习"如何编码"**。

> [!abstract] 挂到暗线：序列表征即在 latent 上组织"历史充分统计量"
> 把观测历史窗口喂给注意力、读出对未来有用的紧凑向量——这正是 **POMDP→belief→latent 暗线**（[[ReinforcementLearning#2.1 MDP 与 POMDP：把"试错"写成数学|POMDP]]）：部分可观下，历史窗口经注意力压成的 latent 近似 belief 充分统计量。[[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook|The Latent Space]] 从"基础—演化—机制—能力"给了 latent 表征的统一框架。**灵巧操作落点**：WMTS 的 [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-006-In-Context-Hypernet-Adapter|In-Context Hypernet Adapter]]（§9）正是"in-context Transformer → FiLM offsets"的超网络式**零梯度真机适应**——把本节 ⑤⑥ 直接落到 [[EmbodiedAI]] 的部署上。

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

> [!note] 补严：为什么最小化 InfoNCE ＝ 最大化互信息 $I(z_v;z_t)$ 的下界
> §3.1、§3.4、这里都在用 InfoNCE，但"它到底在优化什么"没说透。结论（van den Oord 2018）：$I(z_v;z_t)\ \ge\ \log N-\mathcal L_{NCE}$，即**压低对比损失就是抬高互信息的下界**，上限被负样本数 $N$ 卡住（$\log N$）。分三步证，不跳步。
>
> **① 最优打分函数是密度比。** 把 $N$-选-1 的分类看成：给定 $z_v$ 和一组候选 $\{z_t^1,\dots,z_t^N\}$（其中恰一个是正样本、来自联合 $p(z_v,z_t)$，其余 $N{-}1$ 个来自边缘 $p(z_t)$），问"哪个是正样本"。这是标准的后验推断，其 Bayes-最优后验正比于 $\prod$ 各候选按"正/负"来源的似然比。逐项化简后，最优相似度打分收敛到 $\mathrm{sim}^*(z_v,z_t)\propto\log\frac{p(z_t\mid z_v)}{p(z_t)}$——即**密度比的对数**（这也正是 §3.4 说的"InfoNCE critic 收敛到 $\log\frac{p(g\mid s,a)}{p(g)}$"的同一件事）。
>
> **② 代回损失取期望。** 把最优打分 $\exp(\mathrm{sim}^*)=\frac{p(z_t\mid z_v)}{p(z_t)}$ 代入 $\mathcal L_{NCE}=-\mathbb E\big[\log\frac{\exp(\mathrm{sim}(z_v,z_t^+))}{\sum_j\exp(\mathrm{sim}(z_v,z_t^j))}\big]$：
> $$\mathcal L_{NCE}^*=\mathbb E\Big[\log\Big(1+\frac{p(z_t^+)}{p(z_t^+\mid z_v)}\!\!\sum_{j\ne +}\frac{p(z_t^j\mid z_v)}{p(z_t^j)}\Big)\Big].$$
> （分子分母同除正样本项得到的等价形式。）负样本 $z_t^j$ 独立采自边缘 $p(z_t)$，故 $\mathbb E_{z_t^j}\big[\frac{p(z_t^j\mid z_v)}{p(z_t^j)}\big]=\int p(z_t)\frac{p(z_t\mid z_v)}{p(z_t)}dz_t=1$，那个和 $\approx(N-1)\cdot 1$。
>
> **③ 放缩得界。** 代入并把 $N{-}1$ 放大为 $N$、丢掉括号里的 $1$（都是往大放，故给的是下界方向）：
> $$\mathcal L_{NCE}^*\ \ge\ \mathbb E\Big[\log\Big(\frac{p(z_t^+)}{p(z_t^+\mid z_v)}\,N\Big)\Big]=\log N-\mathbb E\Big[\log\frac{p(z_t\mid z_v)}{p(z_t)}\Big]=\log N-I(z_v;z_t),$$
> 最后一步用互信息定义 $I(z_v;z_t)=\mathbb E_{p(z_v,z_t)}\big[\log\frac{p(z_t\mid z_v)}{p(z_t)}\big]$。移项即 $\boxed{I(z_v;z_t)\ge\log N-\mathcal L_{NCE}}$。
>
> **三个可操作推论**：① **负样本越多下界越紧**（$\log N$ 抬高天花板）——这解释了对比学习为何吃 batch size / memory bank；② 这把本讲与 [[InformationTheory#5. 信息瓶颈：最优表征的信息论基础|信息瓶颈]]钉在一起——**对比学习 = 最大化"跨模态互信息"，信息瓶颈 = 在保留任务互信息的同时压掉冗余**，二者是"最大化有用 $I$、最小化无用 $I$"的一体两面（§7.3 的"压缩=泛化=去噪"暗线）；③ **灵巧操作落点**：视触觉 InfoNCE 抬高的是 $I(z_v;z_t)$——迫使"看到 USB 接口的样子"与"摸到接口的力学"共享同一 latent，正是 §5 母题"视觉一遮挡就靠触觉接管"能成立的信息论前提。

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
> - **↔ [[ReinforcementLearning]]**：扩散策略被 RL 微调（§2.2）；CFG 观测引导（§2.2.3）；对比 RL（§3.4）；表征=状态；NTK 解释小数据真机微调；ICL/注意力接 POMDP→belief→latent（§4.6）。
> - **↔ [[InformationTheory]]**：信息瓶颈=VAE 的 $\beta$（§3.1）；压缩=去噪；泛化需要压缩（§6.4）。
> - **↔ [[Optimization]]**：IBC=能量景观下降；NTK 区间凸化（§6.7）；隐式正则↔近端（§6.6）；鞍点逃逸（§6.8）。
> - **↔ [[ComputationalGeometry]]**：点云/SDF 几何表征（§4）；神经隐式 DeepSDF/NGDF。
> - **↔ [[SignalProcessing]]**：触觉表征、Taxim 仿真（§5.3）；ACT 时间集成=低通（§2.3）；压缩去噪。
> - **↔ [[StochasticProcess]]**：扩散=朗之万/SDE（§2.2）；NTK↔GP（§6.7）；噪声逃鞍点（§6.8）。
> - **↔ [[Dynamics]]**：可微物理（§1.3）；Rodrigues 正运动学模板→RodriNet（§4.3）；6D 连续旋转表示 vs 几何参数化（§4.5）。
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
- [[The Latent Space: Foundation, Evolution, Mechanism, Ability, and Outlook|The Latent Space]] — latent 表征统一框架（基础/演化/机制/能力，§4.6）

### 层级与时序表征
- [[Hierarchical Coordination Multi-Agent RL with Spatio-Temporal Abstraction]] — 时空抽象
- [[DexTrack: Towards Generalizable Neural Tracking Control for Dexterous Manipulation from Human References]] — 轨迹表征

### 可解释表征
- [[Weight-sparse transformers have interpretable circuits]] — 稀疏可解释回路

### 物理感知几何表征
- [[GeoPT - Scaling Physics Simulation via Lifted Geometric Pre-Training|GeoPT]] — Dynamics-lifted 几何预训练，E(3)-等变
- [[Emerging Extrinsic Dexterity in Cluttered Scenes via Dynamics-aware Policy Learning|DAPL]] — 动力学感知表征，点级世界模型
- [[RodriNet - Rodrigues Network for Learning Robot Actions|RodriNet]] — Rodrigues 正运动学作可学习 action backbone
- [[On the Continuity of Rotation Representations in Neural Networks|Zhou et al. 2019]] — 连续旋转表示定理，6D + Gram-Schmidt（§4.5）

### 触觉仿真表征
- [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] — 统一 Deform Map，穿透深度域不变表征
- [[STOLA - Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning|STOLA]] — MoE 触觉-语言模型

### VLA 潜空间推理
- [[LaST0 - Latent Spatio-Temporal CoT for Robotic VLA|LaST0]] — 潜在时空链式推理，MoT 双系统
- [[Transformers as Meta-Learners for Implicit Neural Representations|Transformers as Meta-Learners]] — Transformer 超网络生成 INR 权重，元学习即前向（§4.6）
- [[IS ATTENTION REQUIRED FOR ICL? EXPLORING THE RELATIONSHIP BETWEEN MODEL ARCHITECTURE AND IN-CONTEXT LEARNING ABILITY|Is Attention Required for ICL?]] — ICL 非 attention 独有，循环/SSM 亦可（§4.6）

### 信息瓶颈与运动生成表征
- [[RLT - Precise Manipulation with Efficient Online RL Tokens|RLT]] — RL Token 信息瓶颈，残差动作编辑
- [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]] — TP-MoE token 级参数混合，262D 机器人原生扩散

### 项目级真机表征 Idea（WMTS）
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-006-In-Context-Hypernet-Adapter|ICHA]]：In-context Transformer → FiLM offsets，零梯度真机适应
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-012-WPTE-Tactile-Encoder|WPTE]]：WM forward prediction 作触觉编码器 pretext，zero-shot sim-to-real
- [[Projects/World Model as Task Scheduler/all_Insights_local/Idea-009-Discrete-Task-Tokens|VQ Discrete Task Tokens]]：VQ-VAE 离散任务 token + transition graph 安全 replan
