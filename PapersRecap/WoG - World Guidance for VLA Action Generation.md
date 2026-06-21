---
tags:
  - paper
  - vla
  - world-model
  - embodied-ai
aliases:
  - WoG
  - World Guidance
paper-year: 2026
read-date: 2026-03-24
venue: arXiv
paper-pdf: "[[Papers/World Guidance: World Modeling in Condition.pdf]]"
related:
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
---

# World Guidance: World Modeling in Condition Space for Action Generation (WoG)

> [!abstract] 核心贡献
> 提出 WoG，通过将未来观测映射到动作推理的条件空间（而非重建完整视频或学习粗粒度隐动作），实现了 VLA 模型中紧凑而精确的世界建模，显著提升操作任务性能。

> [!tip] 与理论基础的关联
> - [[EmbodiedAI]] - VLA 模型架构与世界模型
> - [[RepresentationLearning]] - 条件空间的紧凑表征学习、DiT 动作头

## 1. 问题设定与动机

### 1.1 核心洞察
VLA 模型需要未来观测建模来辅助动作生成，但存在根本性权衡：**丰富的未来表征（视频预测）冗余度高性能差，紧凑的隐动作表征精度不够**。解决方案是找到一个"刚好足够"的条件空间。

### 1.2 直观隐喻
像一个高效的导航系统：不需要预测沿途每个像素的变化（视频预测），也不只给出模糊的"往前走"（隐动作），而是预测关键路标的精确位置（条件空间），足以指导每一步行动。

### 1.3 现有方法的局限
| 方法类型 | 代表工作 | 问题 |
|---------|---------|------|
| **World Action Models** | 预测图像/深度/视频 | 任务无关冗余信息过多，预训练效率低，视觉预测误差传播到动作空间 |
| **Latent Action Models** | 压缩未来动作到隐表征 | 仅捕获粗粒度运动趋势，缺乏精细动作生成所需的精度 |

## 2. 核心方法

### 2.1 Delta 分析
**核心创新**: 不预测原始未来模态也不压缩动作，而是将未来观测注入动作推理管线产生的 **条件空间** 作为世界建模目标——该空间天然与动作高度相关，对 VLA 模型而言更易预测。

### 2.2 数学框架

**两阶段训练架构**:

**Stage I — World Guidance（监督条件提取）**:
- 当前观测 $O$ 和指令 $l$ 通过 VLM backbone 编码为 $z$
- 未来观测通过冻结的视觉基础模型（DINOv2 + Wan VAE Encoder）编码
- Q-Former 查询并压缩未来特征为低维条件表征 $O^c$
- $O^c$ 通过交叉注意力注入 DiT 动作头，用 Rectified Flow 训练：

$$\mathcal{L}_I = \mathbb{E}_{\tau, A}\left[\|v_\theta(A_\tau, \tau, z, O^c) - v^*\|_2^2\right]$$

其中 $\tau \in [0,1]$ 为调度时间步，$v_\theta$ 和 $v^*$ 为预测与目标速度场。

**Stage II — World Inference（自引导推理）**:
- 冻结 Q-Former 和视觉编码器
- VLM backbone 学习预测条件表征 $O^c$（通过余弦相似度对齐）
- 推理时仅需当前观测，VLM 自回归生成条件+动作：

$$\mathcal{L}_{II} = \mathbb{E}_{\tau, A}\left[\|v_\theta(A_\tau, \tau, z) - v^*\|_2^2\right] + 1 - S[O^c, f_q(O, l)]$$

其中 $f_q(O, l)$ 为 VLM 输出的查询表征，$S[\cdot, \cdot]$ 为余弦相似度。

### 2.3 核心设计决策

**条件空间的充分性论证**: 该空间满足"信息充分且有效"——其信息是动作生成的充分条件（因为就是从动作推理管线中自然生成的），因此对 VLA 模型来说预测该空间是可行的。

**从人类视频学习**: 
- Stage I: 少量有动作标注的人类视频扩展条件空间
- Stage II: 大量无标注人类视频仅监督条件预测（不需要动作标注）

## 3. 训练与实验细节

### 3.1 训练设定
- VLM Backbone: Prismatic VLM (OpenVLA 采用)
- 动作头: DiT (Diffusion Transformer) + Rectified Flow
- 视觉编码器: DINOv2 (判别特征) + Wan VAE Encoder (生成特征)
- 条件提取: Q-Former-based Encoder

### 3.2 核心实验结果

**SIMPLER Benchmark (Google Robot)**:

| 模型 | Pick Coke | Move Near | Drawer | 平均 |
|------|-----------|-----------|--------|------|
| GR00T-N1 | 83.3% | 62.5% | 54.2% | 49.5% |
| UniVLA | 76.4% | 52.8% | 66.7% | 77.5% |
| ViPRA | 79.2% | 66.7% | 62.5% | 71.9% |
| **WoG** | **95.8%** | **79.2%** | **75.0%** | **79.2%** |

- 在涉及干扰物体的场景（如 Move Near）中表现尤为突出——条件空间帮助预测未来轨迹避障
- 在精细几何约束任务（如 Stack、Drawer）中提升较小，受限于 backbone 空间分辨率

### 3.3 消融实验
- **编码器配置**: DINOv2+Wan VAE > DINOv2+SigLIP > DINOv2 alone，生成式特征对动作预测更有价值
- **Stage II 有效性**: 移除条件预测监督 → 性能下降，验证世界建模的必要性

**Ablation 因果链分析**:

| 消融条件 | 效果 | 因果机制 |
|---------|------|--------|
| 去除 Wan VAE（仅 DINOv2） | 性能下降 | DINOv2 为判别特征缺少生成信息 → 条件空间丢失与动作生成相关的空间细节 |
| 去除 Stage II 条件对齐 | 明显下降 | VLM 无法预测条件 → 推理时缺失未来引导 → 退化为无世界模型的 VLA |
| 用 MSE 替代余弦相似度 | 轻微下降 | MSE 对表征绝对尺度敏感 → [[RepresentationLearning]] 中表征漂移问题放大对齐误差 |
| 增大条件维度 | 先升后降 | 维度过大 → 条件空间冗余信息增加 → 预测难度上升 → 与 [[InformationTheory]] 信息瓶颈原理一致 |

## 4. 工程关键细节
- **Rectified Flow** 替代传统 DDPM 用于动作头训练，推理更快（直线插值 vs 曲线去噪轨迹）
- **Q-Former 压缩**: 将高维未来视觉特征压缩为低维条件表征，避免信息冗余
- **余弦相似度对齐**: Stage II 用余弦相似度而非 MSE 对齐条件空间，对表征尺度不敏感

### 4.1 核心伪代码

```python
# WoG 两阶段训练核心逻辑
# ===== Stage I: World Guidance =====
class WorldGuidance(nn.Module):
    def __init__(self, vlm_backbone, qformer, dit_head):
        self.vlm = vlm_backbone          # Prismatic VLM
        self.vis_enc = DINOv2_WanVAE()   # 冻结视觉编码器
        self.qformer = qformer            # Q-Former 条件提取
        self.dit = dit_head               # DiT + Rectified Flow

    def forward(self, obs, instruction, future_obs, actions, tau):
        z = self.vlm.encode(obs, instruction)          # VLM 编码当前观测
        future_feat = self.vis_enc(future_obs)          # 冻结编码未来观测
        O_c = self.qformer(query=z, kv=future_feat)     # 压缩为条件表征
        
        # Rectified Flow: 线性插值 A_tau = (1-tau)*noise + tau*A_gt
        noise = torch.randn_like(actions)
        A_tau = (1 - tau) * noise + tau * actions
        v_pred = self.dit(A_tau, tau, z, cross_attn=O_c)  # 条件注入
        v_target = actions - noise                         # 目标速度场
        loss = F.mse_loss(v_pred, v_target)
        return loss

# ===== Stage II: World Inference =====
# 冻结 Q-Former + vis_enc, VLM 学习预测 O_c
def stage2_loss(model, obs, instruction, future_obs, actions, tau):
    z = model.vlm.encode(obs, instruction)
    O_c_gt = model.qformer(z, model.vis_enc(future_obs)).detach()  # 目标
    O_c_pred = model.vlm.predict_condition(z)                       # VLM 预测
    
    align_loss = 1 - F.cosine_similarity(O_c_pred, O_c_gt, dim=-1).mean()
    noise = torch.randn_like(actions)
    A_tau = (1 - tau) * noise + tau * actions
    flow_loss = F.mse_loss(model.dit(A_tau, tau, z), actions - noise)
    return flow_loss + align_loss
```

## 5. 核心洞见

### 5.1 理论局限性
- **理论**: 条件空间的"充分性"依赖于动作推理管线的设计，不同架构可能需要不同条件空间
- **算法**: 两阶段训练引入了信息瓶颈——Stage I 压缩可能丢失微妙但关键的信息
- **工程**: 当前 backbone 空间分辨率不足以处理精细几何约束任务（如堆叠）

### 5.2 与用户研究的启发（灵巧手转笔/Sim-to-Real）
1. **条件空间思想可迁移到触觉**: 将未来触觉预测压缩为条件空间引导灵巧手动作生成，比直接预测完整触觉图精确且高效
2. **从人类视频学习**: 大量无标注的人手操作视频可通过类似框架提取条件信号，降低灵巧操作数据标注成本
3. **Rectified Flow 动作头**: 相比 DDPM，Rectified Flow 推理更快，适合灵巧操作中对低延迟的需求

## 6. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
- WoG 属于 VLA 模型的最新进展，在世界模型路线上提出了条件空间这一新范式
- 与 World Action Model 和 Latent Action Model 形成三足鼎立

### 与 [[RepresentationLearning]] 的联系
- DiT 动作头 + Rectified Flow 是 [[RepresentationLearning|Diffusion Policy]] 的工程优化变体
- Q-Former 条件压缩与信息瓶颈理论相关（[[InformationTheory]]）

### 与 [[StochasticProcess]] 的数学联系
Rectified Flow 的核心是从噪声 $\epsilon \sim \mathcal{N}(0, I)$ 到数据 $A$ 的直线 ODE：
$$\frac{d A_\tau}{d\tau} = v_\theta(A_\tau, \tau), \quad A_0 = \epsilon, \quad A_1 = A$$
对比 DDPM 的随机 SDE $dA = f(A,t)dt + g(t)dW_t$，Rectified Flow 消除了布朗运动项 → 推理时单步 Euler 即可逼近（[[StochasticProcess]] 中 ODE 概率流的优势）。

### 与 [[Optimization]] 的数学联系
两阶段优化可视为 bi-level optimization：Stage I 内层优化条件空间 $O^c$，Stage II 外层优化 VLM 去预测 $O^c$：
$$\min_{f_q} \left[ 1 - S[O^{c*}, f_q(O, l)] + \mathcal{L}_{\text{flow}} \right], \quad O^{c*} = \arg\min_{O^c} \mathcal{L}_I(O^c)$$

### 跨方法对比

| 维度 | WoG (本文) | SuSIE (Subgoal) | UniPi (Video Plan) | π0-FAST (Token) | GR00T-N1 |
|------|-----------|-----------------|-------------------|----------------|----------|
| **世界建模形式** | 条件空间 | 子目标图像 | 完整视频 | 无显式 | 隐动作 |
| **信息冗余** | 低（紧凑） | 中 | 高 | — | 低 |
| **推理延迟** | 低 | 高（需扩散生成图像） | 极高 | 低 | 低 |
| **精度** | 高 | 中 | 低（误差传播） | 高 | 中 |
| **人类视频利用** | ✅ Stage I+II | ❌ | ✅ | ❌ | ❌ |

## 7. 局限与未来方向
- 精细几何约束任务（堆叠、抽屉）性能受限于 backbone 分辨率
- 条件空间设计依赖于特定动作头架构，泛化性有待验证
- 两阶段训练流程可能可简化为端到端方案

```
前置工作: π0-FAST (VLA), GR00T-N1 (Foundation Agent)
    ↓
本论文: 条件空间世界建模 → 紧凑且精确的未来指导
    ↓
后续影响: 条件空间可扩展到多模态感知(触觉/力觉)的压缩表征
```
