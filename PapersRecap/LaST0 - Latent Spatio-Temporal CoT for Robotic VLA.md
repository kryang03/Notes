---
tags:
  - paper
  - embodied-ai
  - representation-learning
  - vla
  - latent-reasoning
aliases:
  - LaST0
  - Latent Spatio-Temporal CoT
paper-year: 2026
read-date: 2026-03-03
venue: ICML 2026 (Submission)
related:
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[ReinforcementLearning]]"
  - "[[ControlTheory]]"
---

# LaST0: Latent Spatio-Temporal Chain-of-Thought for Robotic Vision-Language-Action Model

> [!abstract] 核心贡献
> 提出 **Latent Spatio-Temporal CoT**，在紧凑隐空间中联合预测未来视觉语义、3D 几何和本体感受状态，替代显式语言 CoT 的高延迟推理，并通过 **Mixture-of-Transformers 双系统架构** 将低频隐推理与高频动作生成解耦。在 10 个真实世界任务（桌面/移动/灵巧手）上分别超越 SOTA VLA 方法 13%/14%/14%，推理速度提升 14×。

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] — VLA 模型前沿：Latent CoT 替代显式 CoT 的范式转移
> - [[RepresentationLearning]] — 多模态隐空间（2D 视觉 + 3D 点云 + 本体感受）融合
> - [[ReinforcementLearning]] — Dual-system 架构与控制频率自适应（连接 TARC / Action Persistence 思想）
> - [[ControlTheory]] — 快慢双频控制的控制论基础
>
> **核心技术**: Latent CoT, Mixture-of-Transformers, Dual-System Architecture, Heterogeneous Frequency Training

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
在 VLA 模型中用**隐空间时空推理**替代**显式语言推理**，既保留了"先想后做"的范式优势，又消除了自回归文本生成的延迟瓶颈和语言表征的物理世界表达能力不足。

### 直观隐喻
如果显式 CoT 像"大声说出每步计划再行动"（速度慢、无法描述力学细节），LaST0 则像"在脑海中快速模拟整个动作序列"（内隐推理，直接编码物理动态）。

### 领域定位
- **VLA 前沿**: 从 RT-2 → π0 → CoT-VLA → **LaST0 (Latent CoT)**
- **核心矛盾**: 显式 CoT 的推理质量 vs 推理延迟；语言空间的表达能力 vs 物理世界的精细约束
- **关键创新**: 将推理从语言空间"下沉"到多模态物理空间

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 对比基线 | LaST0 优势 |
|---------|-----------|
| SpatialVLA (无 CoT) | +8% 平均 SR（缺乏推理能力） |
| CoT-VLA / CogACT (显式 CoT) | +13-14% SR + 14× 推理加速 |
| Headdrop / DiT-π0 (连续策略) | 更好的长程一致性 |

### 关键贡献点
1. **Latent Spatio-Temporal CoT 空间** — 自回归预测未来 2D 语义 + 3D 结构 + 本体感受状态的紧凑隐表征
2. **MoT 双系统架构** — 慢推理专家 (低频 latent inference) + 快动作专家 (高频 action generation)，通过共享注意力协调
3. **异构频率训练** — 推理和动作以不同频率运行，部署时自适应切换

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 Latent CoT 空间构造

三路隐表征的融合:
- **2D 视觉隐变量**: SigLIP-Large 编码未来关键帧 → $f_{img} \in \mathbb{R}^{B \times N_{img} \times d_v}$
- **3D 几何隐变量**: Uni3D 编码未来点云（仅训练时） → 3D 空间推理能力
- **本体感受隐变量**: 机器人关节状态编码 → 自我身体状态的内部表征

每模态通过 average pooling 压缩为紧凑 token，然后沿时间维度自回归展开，形成**时间一致的隐推理轨迹**。

### 3.2 Mixture-of-Transformers 双系统

基于 DeepSeek-LLM 1.5B backbone，改造为 MoT 架构:

| 组件 | 频率 | 功能 |
|-----|------|------|
| **Reasoning Expert** | 低频 (1/n step) | 处理视觉-语言输入 → 生成 Latent CoT |
| **Acting Expert** | 高频 (1/1 step) | 条件化 Latent CoT → 生成 SE(3) 动作 |
| **Shared Attention** | — | 两个专家共享 QKV 注意力，实现推理-动作信息流 |

> [!note] 与控制频率自适应的关联
> LaST0 的快慢双系统设计与 [[TARC - Time-Adaptive Robotic Control]] 的控制频率自适应思想高度一致 —— 高层决策低频更新，底层执行高频运行。这也与 DNPM 项目中的频率困境 (Direction A) 直接相关。

### 3.3 训练流程
1. **预训练阶段**: 在 Open X-Embodiment + DROID + RoboVerse 等大规模数据集上预训练
2. **下游微调**: 联合优化推理和动作专家，动作专家在异构快慢频率下训练
3. **部署**: 推理专家周期性更新 latent CoT，动作专家每步生成动作

## 4. 实验与验证 (Experiments)

### 实验设置
- **模拟**: SimplerEnv (10 tasks)
- **真实世界**: 10 tasks — 桌面单/双臂 (Franka)、移动操作、灵巧手 (LEAP Hand)
- **Baselines**: SpatialVLA, CoT-VLA, CogACT, Headdrop, DiT-π0

### 关键结果

| 场景 | SR 提升 (vs SOTA) | 推理加速 |
|------|-----|---------|
| 桌面操作 | +13% | 14× vs CoT-VLA |
| 移动操作 | +14% | — |
| **灵巧手操作** | **+14%** | — |
| 长程任务 (煎蛋) | 成功完成 | — |

> [!important] 灵巧手操作表现
> LaST0 在灵巧手 (LEAP Hand) 操作任务上同样展现了 +14% 的 SR 提升，说明 Latent CoT 对高自由度系统同样有效。这与 DNPM 项目的灵巧操作研究方向直接相关。

## 5. 批判性分析 (Critical Analysis)

### 优势
- **速度-质量双赢**: 14× 推理加速的同时提升了操作成功率
- **物理感知推理**: 隐空间编码 3D 结构和力学信息，超越纯语言推理
- **通用性**: 桌面/移动/灵巧手全覆盖

### 局限性
- **3D 编码器训练时依赖**: Uni3D 点云编码器仅训练时使用，推理时无 3D 输入 — 信息蒸馏的有效性存疑
- **动作空间受限**: SE(3) 末端执行器控制，未涉及高维关节空间控制
- **未涉及接触丰富操作**: 灵巧手任务以抓取为主，缺乏 in-hand manipulation 等接触密集场景验证

### 未来方向
- Latent CoT 扩展至触觉模态（力/扭矩隐变量）
- 与 RL 微调结合（当前仅 IL），联合优化推理和策略
- 高維关节空间控制（灵巧手多指操作）

## 6. 对灵巧操作的启发 (Implications)

> [!important] 对 DNPM 项目的启发
> 1. **快慢双系统 = DNPM 频率困境的 VLA 级解决方案**: LaST0 的 reasoning/acting 频率分离设计，与 [[TARC - Time-Adaptive Robotic Control|TARC]] 和 DNPM Direction A 的频率自适应思想一脉相承
> 2. **Latent CoT → 灵巧操作的隐式规划**: 如果在 latent 中编码未来接触状态和力分布，可能成为 contact-rich 操作的高效规划方案
> 3. **3D 几何推理**: Uni3D 编码器为灵巧手提供物体几何先验，但训练-推理不对称的设计需要验证在高精度操作中的鲁棒性
> 4. **VLA + RL 融合缺口**: LaST0 当前仅用 IL 训练，未来必然需要 RL 微调来突破模仿天花板 — 连接到 [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] 和 [[WMPO - World Model-based Policy Optimization for VLA|WMPO]]

## 7. 演进脉络定位 (Evolution Context)

```
前置工作: RT-2 (VLM→VLA) → π0 (Flow Matching VLA) → CoT-VLA (显式语言推理)
    ↓
核心问题: 显式 CoT 推理延迟高 + 语言空间物理世界表达能力不足
    ↓
本论文: LaST0 — Latent Spatio-Temporal CoT + MoT 双系统
    ↓
后续影响: Latent CoT + RL 微调 → 接触丰富操作的高频隐式规划
```
