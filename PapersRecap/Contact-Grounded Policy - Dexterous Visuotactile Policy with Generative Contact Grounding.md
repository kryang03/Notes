---
tags:
  - paper
  - manipulation
  - tactile
  - imitation-learning
  - diffusion-policy
aliases:
  - CGP
  - Contact-Grounded Policy
paper-year: 2026
read-date: 2026-03-13
venue: arXiv (Purdue / Meta Reality Labs)
related:
  - "[[ContactMechanics]]"
  - "[[ControlTheory]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
---

# Contact-Grounded Policy: Dexterous Visuotactile Policy with Generative Contact Grounding

> [!abstract] 核心贡献
> 提出 **Contact-Grounded Policy (CGP)**，将灵巧操作建模为**接触落地问题**：策略不直接输出控制目标，而是预测**耦合的实际机器人状态 + 触觉反馈轨迹**，再通过学习的**接触一致性映射**转换为柔顺控制器可执行的目标状态。在 Allegro V5 + Digit360 实物和仿真五指手上多项灵巧任务中超越 visuomotor 和 visuotactile diffusion-policy 基线。

> [!tip] 与理论基础的关联
> - [[ContactMechanics]] — 多点接触建模：$(x_t, u_t, a_t)$ 三元组隐式表示分布式接触
> - [[ControlTheory#2.1 阻抗控制]] — 柔顺控制器（PD + 操作空间阻抗）是执行层核心
> - [[RepresentationLearning#2.2 深度解析：扩散策略]] — 条件扩散模型生成耦合轨迹
> - [[SignalProcessing]] — 触觉 VAE 压缩与潜空间生成
>
> **核心技术**: Contact Grounding, Coupled State-Tactile Diffusion, Contact-Consistency Mapping, Latent Tactile Generation

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
将灵巧操作视为**接触落地**问题：策略预测"物理世界打算发生什么接触"（实际状态 + 触觉），再通过学到的映射将其翻译为柔顺控制器能执行的目标。

### 直观隐喻
传统策略像"只告诉手指去哪"（运动学轨迹），CGP 像"同时计划手指在哪 + 手指会摸到什么感觉"（状态-触觉耦合），然后让柔顺控制器自适应地实现这个"感觉"。

### 领域定位
- **触觉灵巧操作前沿**: 从 tactile-as-observation → tactile-as-prediction → **tactile-as-grounding**
- **核心矛盾**: 高级策略的运动学输出 vs 低层柔顺控制器的动力学执行——不经接触语义桥接，策略输出无法忠实实现预期接触
- **关键突破**: 接触一致性映射 $M_\phi(x_t, u_t) \to a_t$ 将触觉预测"落地"为控制指令

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 对比基线 | CGP 优势 |
|---------|---------|
| Visuomotor Diffusion Policy | 无触觉感知，接触敏感任务失败率高 |
| Visuotactile DP (tactile-as-obs) | 触觉仅作为观测输入，未建模接触动态与控制器交互 |
| Sparse fingertip force policies | 仅覆盖指尖稀疏力，无法处理分布式多点接触 |
| Adaptive compliance policies | 限于单臂末端，未扩展到多指手 |

### 关键贡献点
1. **Contact Grounding 框架** — 用 $(x_t, u_t, a_t)$ 三元组隐式表示接触状态，无需显式接触参数化（位置/模式/法向量）
2. **Coupled State-Tactile Diffusion** — 在 VAE 压缩的触觉潜空间中，用条件扩散模型**联合预测**未来实际状态 + 触觉反馈
3. **Contact-Consistency Mapping** — 轻量网络 $M_\phi$：给定预测的 $(x_t, u_t)$，输出柔顺控制器参考 $a_t$，以残差形式学习

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 接触落地的数学建模

核心观察：在给定触觉传感器和柔顺控制器的条件下，接触状态可由三元组 $(x_t, u_t, a_t)$ 完全表示。

- $x_t$: 实际机器人状态（末端位姿 + 手关节角）
- $u_t$: 触觉反馈（触觉数组或视觉触觉图像）
- $a_t$: 目标机器人状态（柔顺控制器参考）

接触一致性映射：
$$a_t = M_\phi(x_t, u_t)$$

**物理直觉**: 柔顺控制器（PD 控制）可视为虚拟弹簧-阻尼器，将 $a_t$ 与 $x_t$ 之间的跟踪误差转化为关节力矩。接触结果体现在 $u_t$ 中。这个三元组隐式编码了所有接触信息，而无需显式建模接触位置或模式。

### 3.2 耦合轨迹扩散生成

定义耦合未来轨迹 $Y_t = (x_{t+1:t+T}, h_{t+1:t+T})$，其中 $h_t = E(u_t)$ 为触觉 VAE 潜编码。

训练使用 DDPM/DDIM 框架：
$$\mathcal{L}_{diff}(\theta) = \mathbb{E}_{(O_t, Y_t^0), \epsilon, j} \left[ \| \epsilon - \pi_\theta(O_t, Y_t^j, j) \|^2 \right]$$

其中 $Y_t^j = \alpha_j Y_t^0 + \sigma_j \epsilon$ 为加噪轨迹。架构使用 U-Net 去噪器，通过 FiLM 条件注入多模态特征。

### 3.3 潜空间触觉压缩

使用 KL 正则化 VAE 将高维触觉（视觉触觉图像或密集触觉数组）压缩到紧凑潜空间 $h_t \in \mathbb{R}^M$：
- 编码器 $E$：将原始触觉映射到低维
- KL 正则化：稳定扩散生成、防止潜空间坍缩
- 消融实验验证 KL 正则化对下游策略性能的关键作用

## 4. 实验与验证 (Experiments)

### 实验设置
- **仿真**: Tesollo DG-5F 五指手 + 密集全手触觉数组，FEM 软体接触仿真
- **实物**: Allegro V5 四指手 + 4× Digit360 视觉触觉传感器
- **任务**: In-hand box flipping, fragile egg grasping, jar opening, dish wiping
- **遥操作**: Meta Quest 3 (VR) + OptiTrack (MoCap)
- **基线**: Visuomotor DP, Visuotactile DP (tactile-as-obs/aux-pred)

### 关键结果
- CGP 在所有任务上超越 visuomotor 和 visuotactile 基线
- 触觉预测 + 接触一致性映射的联合作用是关键（消融验证）
- KL 正则化的触觉 VAE 显著优于无正则化版本

## 5. 批判性分析 (Critical Analysis)

### 优势
- **通用接触表示**: $(x_t, u_t, a_t)$ 三元组避免了手工设计的接触参数化，自然适配不同触觉覆盖范围
- **控制器感知**: 映射 $M_\phi$ 显式建模了策略输出与柔顺控制器动力学的交互
- **分布式接触**: 首个扩展到多指手分布式多点接触的可执行接触建模框架

### 局限性
- 接触一致性映射绑定于特定的传感器配置和控制器；换硬件需重新学习
- 仿真中使用 FEM 软体求解，计算开销大，难大规模 RL
- 未与 RL-based 灵巧操作方法（如 [[DemoStart - Demonstration-led Auto-Curriculum for Sim-to-Real with Multi-Fingered Robots|DemoStart]]）对比

### 未来方向
- 结合 sim-to-real transfer 研究触觉映射的泛化
- 将 Contact Grounding 与 RL fine-tuning 结合
- 探索 Flow Matching 替代 Diffusion 以降低推理延迟

## 6. 对灵巧操作的启发 (Implications)

**与 DNPM 的直接关联**:
- Contact Grounding 的 $(x_t, u_t, a_t)$ 隐式接触表示 可应用于非紧握操作的接触状态建模——无需显式参数化快速演化的单边接触
- 柔顺控制器作为执行层的设计与 [[ControlTheory#2.1 阻抗控制]] 中的变阻抗控制直接呼应
- 触觉预测作为策略目标（而非仅观测输入）的范式转换，启发 DNPM 项目中触觉反馈的使用方式

## 7. 演进脉络定位 (Evolution Context)

```
前置工作: Diffusion Policy (2D action regression)
    ↓ 加入触觉观测
Visuotactile DP (tactile-as-observation)
    ↓ 触觉作为辅助预测目标
Auxiliary Tactile Prediction (tactile-as-aux-pred)
    ↓ 触觉作为接触落地工具
本论文: CGP (tactile-as-grounding + contact-consistency mapping)
    ↓
后续影响: 分布式触觉 + 接触感知策略的统一框架
```
