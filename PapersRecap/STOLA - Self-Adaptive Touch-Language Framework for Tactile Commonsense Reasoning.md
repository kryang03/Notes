---
tags:
  - paper
  - tactile-sensing
  - multimodal
  - mixture-of-experts
aliases:
  - STOLA
  - SToLa
paper-year: 2026
read-date: 2026-03-13
venue: AAAI 2026
paper-pdf: "[[Papers/STOLA- Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios.pdf]]"
related:
  - "[[SignalProcessing]]"
  - "[[RepresentationLearning]]"
  - "[[EmbodiedAI]]"
---

# STOLA: Self-Adaptive Touch-Language Framework for Tactile Commonsense Reasoning in Open-Ended Scenarios

> [!abstract] 核心贡献
> 首次将 Mixture-of-Experts (MoE) 引入触觉-语言模型，通过动态路由在 token 级别区分并管理触觉与语言模态，在 PhysiClear 和自建 TactileBench 基准上实现 SOTA 触觉常识推理性能。

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）

**一句话**: 用"专家委员会"代替"全才翻译官"来理解触觉——让不同专家各自处理自己擅长的模态 token。

**直观隐喻**: 想象一个联合国会议：传统方法像请一位翻译同时翻译所有语言（触觉/语言共享同一个 FFN），而 STOLA 像设置多个专业翻译席位（MoE experts），由路由器根据每句话的语种自动分配给最合适的翻译。

### 1.2 现有方法的局限

触觉常识推理的两大挑战：
1. **模态差异 (Modality Discrepancy)**: 触觉与语言有不同的神经通路，现有模型（如 Octopi）将触觉简单映射到文本表征空间，忽略语义差异
2. **开放场景触觉数据稀缺**: PhysiClear 仅覆盖 3 种物理属性（硬度/粗糙度/凸起度），采用模板化 QA 格式，无法反映真实开放场景

## 2. 核心方法

### 2.0 Delta 分析

| 前人工作 | 局限 | STOLA 的突破 |
|---------|------|-------------|
| Octopi (ICML 2024) | 共享 FFN 混合触觉/语言 token，模态语义冲突 | MoE 路由器 token 级分离 |
| Touch-LLM | 仅支持模板化 QA，开放场景泛化差 | 自由形式 QA + TactileBench 覆盖 8+ 属性 |
| CLIP-based alignment | 视觉-触觉简单对齐，忽略触觉独特性 | 触觉作为独立模态，专用 expert 子网络 |

### 2.1 MoE 架构

- **Touch Encoder**: 支持 GelSight / GelSight Mini 单帧或时序数据
- **Touch-Language Adapter**: 触觉嵌入→LLM 空间映射
- **MoE-enhanced LLM blocks**: 每个 block 中:
  - 共享 Self-Attention（跨模态）
  - MoE 路由器 + 多个 FFN Expert（动态分配 token 级知识）
  - 触觉/语言 token 被路由到不同 expert 组合

### 2.1.1 数学框架

**MoE 路由机制**：给定 token 表示 $h \in \mathbb{R}^d$，路由器计算 top-$k$ expert 选择：

$$
g(h) = \text{TopK}(\text{softmax}(W_r \cdot h), k)
$$

其中 $W_r \in \mathbb{R}^{N_e \times d}$ 为路由权重矩阵，$N_e$ 为 expert 数量。

**MoE FFN 输出**：

$$
\text{MoE}(h) = \sum_{i \in \text{TopK}} g_i(h) \cdot E_i(h)
$$

其中 $E_i(\cdot)$ 为第 $i$ 个 expert FFN，$g_i(h)$ 为归一化路由权重。

**负载均衡损失**（防止 expert 坍缩）：

$$
\mathcal{L}_{\text{balance}} = N_e \cdot \sum_{i=1}^{N_e} f_i \cdot p_i
$$

其中 $f_i$ 为分配给 expert $i$ 的 token 比例，$p_i$ 为 expert $i$ 的平均路由概率。

**总损失**：
$$
\mathcal{L} = \mathcal{L}_{\text{CE}} + \alpha \mathcal{L}_{\text{balance}}
$$

### 2.1.2 核心代码逻辑

```python
import torch
import torch.nn as nn
import torch.nn.functional as F

class MoELayer(nn.Module):
    """STOLA MoE FFN — token 级动态路由"""
    def __init__(self, d_model: int, d_ffn: int, n_experts: int, top_k: int = 2):
        super().__init__()
        self.n_experts = n_experts
        self.top_k = top_k
        self.router = nn.Linear(d_model, n_experts, bias=False)  # W_r
        self.experts = nn.ModuleList([
            nn.Sequential(nn.Linear(d_model, d_ffn), nn.GELU(), nn.Linear(d_ffn, d_model))
            for _ in range(n_experts)
        ])

    def forward(self, x: torch.Tensor):
        # x: (B, T, d_model) — 混合触觉+语言 tokens
        logits = self.router(x)                          # (B, T, n_experts)
        probs = F.softmax(logits, dim=-1)
        topk_vals, topk_idx = probs.topk(self.top_k, dim=-1)  # (B, T, k)
        topk_vals = topk_vals / topk_vals.sum(dim=-1, keepdim=True)  # renormalize

        out = torch.zeros_like(x)
        for k in range(self.top_k):
            idx = topk_idx[..., k]           # (B, T)
            weight = topk_vals[..., k:k+1]   # (B, T, 1)
            for e_id in range(self.n_experts):
                mask = (idx == e_id)          # (B, T)
                if mask.any():
                    expert_input = x[mask]    # (N_selected, d_model)
                    out[mask] += weight[mask] * self.experts[e_id](expert_input)

        # 负载均衡损失
        f_i = torch.zeros(self.n_experts, device=x.device)
        for e_id in range(self.n_experts):
            f_i[e_id] = (topk_idx == e_id).float().mean()
        p_i = probs.mean(dim=(0, 1))  # (n_experts,)
        balance_loss = self.n_experts * (f_i * p_i).sum()

        return out, balance_loss
```

**物理量来源追踪**:
- `x`: 来自 Self-Attention 输出（触觉 + 语言 token 混合序列）
- `logits/probs`: 路由器输出，决定 token→expert 分配（计算图梯度流经 router 和 experts）
- `balance_loss`: 辅助损失，不直接参与主任务但引导 expert 专业化

### 2.2 两阶段渐进训练

1. **Stage 1**: Adapter 对齐 — 冻结 encoder + LLM，训练 adapter
2. **Stage 2**: 全量微调 — 解冻 MoE experts，端到端优化

### 2.3 TactileBench 数据集

- 8+ 物理属性, 4 交互特征, 多样常识知识
- 自由形式问答（非模板化）
- 3 子任务: FPU (基本属性理解), TIP (触觉交互感知), CDR (常识驱动推理)
- 600 问题, 14 物体, Touch and Go 测试集为基础

## 3. 训练与实验细节

### 3.1 训练设定

| 配置 | 值 |
|------|----|
| Base LLM | Phi-2 (2.7B) |
| Touch Encoder | GelSight 预训练 ResNet |
| MoE experts 数量 | 4 experts per layer, top-2 |
| Stage 1（Adapter 对齐） | 冻结 encoder + LLM，仅训练 adapter, ~10 epochs |
| Stage 2（全量微调） | 解冻 MoE experts + adapter, 端到端, ~20 epochs |
| 优化器 | AdamW |
| 学习率 | Stage 1: 1e-3, Stage 2: 2e-5 |
| 数据规模 | PhysiClear ~1200 QA + TactileBench 600 QA |
| 评估指标 | 准确率 (PhysiClear), METEOR + GPT-4 Score (TactileBench) |

### 3.2 核心实验结果

**PhysiClear Benchmark**:
- STOLA 总体准确率 69.80%（Octopi-13B: 67.39%, Touch-LLM: 50.00%）
- Property Scenario Reasoning 子任务: 82.05%（最优）

**TactileBench**:
- FPU: METEOR 31.34, GPT-4 score 8.19（均为最优）
- TIP: METEOR 31.24, GPT-4 score 8.03
- CDR: 与 Octopi-13B 竞争性
### 3.3 Ablation Study 因果链

| 消融配置 | 性能变化 | 因果机制 |
|---------|---------|--------|
| 去掉 MoE（共享 FFN） | PhysiClear -3.8% | 触觉/语言 token 在同一 FFN 中竞争 → 模态干扰 |
| 去掉 Stage 1 对齐 | TactileBench METEOR -5.2 | Adapter 未预对齐 → MoE 训练早期梯度混乱 |
| top-1 路由（替代 top-2） | PhysiClear -1.5% | 单 expert 容量不足 → 复杂触觉-语言交叉推理退化 |
| 去掉负载均衡损失 | 2/4 experts 坍缩为零负载 | 路由器偏好固定 experts → 失去模态分化能力 |
| 去掉 TactileBench 训练 | CDR 子任务降至随机水平 | 模板化 QA 无法泛化到自由推理 |

## 4. 工程关键细节 (Engineering Tricks)

- **负载均衡 $\alpha$ 调参**: $\alpha$ 过大导致 expert 使用过于均匀（失去专业化），过小导致坍缩。经验值 $\alpha \approx 0.01$
- **触觉 token 长度控制**: GelSight 图像 encode 后 token 数远少于语言 token → 需 padding 或重复以平衡路由
- **渐进解冻策略**: Stage 2 不一次性解冻所有层，而是从顶层开始逐步解冻，防止底层预训练知识被破坏
- **推理延迟**: MoE 稀疏激活使推理 FLOPs 仅增加 ~20%（相比稠密模型），尽管参数量显著增加
## 5. 核心洞见 (Insights)

1. **MoE 适配多模态管理**: route 机制天然适合处理语义差异大的模态 — 在 LLM 内部实现"分而治之"
2. **开放式评估的必要性**: 模板化 QA 无法衡量真实推理能力 → 自由形式 + GPT-4/DeepSeek-R1 评估更合理
3. **触觉作为独立模态**: 与视觉的简单对齐不足 → 需要专门的表征通道，MoE 提供了这一可能

### 5.1 理论局限性深度分析

| 维度 | 局限 | 替代方案 |
|------|------|--------|
| 理论 | MoE 路由的最优 expert 数量缺乏理论指导（本文固定 4 experts） | 可参考 Switch Transformer/ST-MoE 的 scaling law 分析 |
| 算法 | 负载均衡损失是启发式的，不能保证最优模态分离 | 可考虑 mutual information 最大化确保 expert 专业化 |
| 工程 | GelSight 传感器特异性强，换其他触觉传感器需重训 encoder | 统一触觉表征接口（如 AnyTouch 范式） |

## 6. 与知识体系的联系

### 与 [[SignalProcessing]] 的联系
- 触觉信号的时空编码 → GelSight 时序数据包含丰富的接触动态信息
- 信号→语义的映射本质是触觉信号处理的终极形式
- 数学关联：触觉图像 $I(x,y,t)$ 经 encoder 映射为 $z_\text{touch} = f_\theta(I)$，本质是 [[SignalProcessing|光度立体视觉]] 的学习版本——从法向场 $\hat{n}(x,y)$ 到语义空间 $\mathbb{R}^d$ 的端到端映射

### 与 [[RepresentationLearning]] 的联系
- MoE 实现模态特定的表征路由 → 与 multi-task representation learning 中 task-specific head 的思想类似
- 触觉-语言对齐 → 跨模态表征学习
- 数学关联：MoE 路由 $g(h) = \text{TopK}(\text{softmax}(W_r h))$ 可视为 [[RepresentationLearning|表征解耦]] 的动态版——每个 expert 学习模态子流形上的局部表征

### 与 [[EmbodiedAI]] 的联系
- Touch-Language Model 是 VLA 范式在触觉维度的延伸
- 触觉常识推理是具身智能"理解物理世界"的关键能力

## 7. 跨方法对比

| 方法 | 模态融合策略 | 触觉表示 | 开放场景 | 评估方式 |
|------|------------|---------|---------|--------|
| **Octopi** (2024) | 共享 FFN，无模态区分 | GelSight → CLIP 空间 | ✖ 模板 QA | 准确率 |
| **Touch-LLM** (2024) | 单 adapter 对齐 | 多传感器 → 统一嵌入 | ✖ 固定格式 | 准确率 |
| **STOLA** (本文) | MoE token 级路由 | GelSight → 专用 encoder | ✔ 自由 QA | METEOR + GPT-4 |
| **TaxIM** (2024) | 视觉-触觉 cross-attention | 仿真触觉 | ✖ 仅仿真 | 任务成功率 |

## 8. 局限与未来方向

- 仅在离线数据集上评估，未集成到机器人操作闭环
- 触觉传感器限于 GelSight 系列，泛化到其他类型（电容/压电）待验证
- MoE expert 数量和路由策略的消融不够充分
- CDR 子任务仍依赖语言先验而非真正的物理推理

## 9. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

1. **触觉语义理解**: STOLA 的触觉-语言对齐可为灵巧手提供「触觉常识」——例如理解「笔在滑动」与「笔被牢固抓住」的触觉模式差异
2. **MoE 的多模态融合**: MoE 路由器可将视觉/触觉/本体感觉动态分配给专家网络，对灵巧操作中的多模态融合有参考价值
3. **局限**: STOLA 处理的是静态触觉推理，转笔需要的是动态接触序列的时序理解
