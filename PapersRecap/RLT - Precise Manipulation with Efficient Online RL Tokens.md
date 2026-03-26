---
tags:
  - paper
  - vla
  - online-rl
  - manipulation
  - precision
  - physical-intelligence
aliases:
  - RLT
  - RL Tokens
paper-year: 2026
read-date: 2026-03-24
venue: Physical Intelligence Blog (pi.website)
paper-pdf: "[[Papers/Precise Manipulation with Efficient Online RL.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
---
https://www.pi.website/research/rlt
# Precise Manipulation with Efficient Online RL (RL Tokens)

> [!abstract] 核心贡献
> 提出 **RL Tokens (RLT)**——在 VLA 中训练一个编码器-解码器 Transformer 提取 **紧凑 RL token** 作为信息瓶颈表征，然后用轻量级 actor-critic 在真实机器人上进行 **高效在线 RL**，仅需 15 分钟真实数据即可将精密操作任务加速 3×，甚至超越人类遥操作速度。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#5.2 真实世界高效 RL: SERL 与 Human-in-the-Loop]] — 真实世界在线 RL
> - [[ReinforcementLearning#2.4 Off-Policy 演进线：从 DDPG 到 SAC]] — Off-policy actor-critic 用于高效学习
> - [[EmbodiedAI#2.5 VLA Post-Training: 从模仿到强化]] — VLA 的 RL 后训练范式
> - [[EmbodiedAI#1.3 VLA 的动作输出范式]] — Action chunk 与 VLA 集成
> - [[RepresentationLearning]] — 信息瓶颈表征
>
> **核心技术**: VLA RL Token + Lightweight Off-Policy Actor-Critic + Residual Action Editing

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
在冻结的 VLA 基础上，训练一个 **信息瓶颈 token** 将 VLA 内部表征压缩为紧凑状态，然后用极小的 actor-critic 在线 RL 实现精密操作阶段的快速改进。

### 直观隐喻
VLA 像一位全能但不够精细的厨师，能完成整道菜的大部分步骤。RL Token 就像给厨师的手配了一个 **微型精密调节器**——不需要重新训练厨师的全部技能，只在最关键的刀工环节（螺丝对准、插线）用一个小小的"肌肉记忆模块"实时微调手指动作。

### 领域定位
- **上游**: π₀ VLA (Physical Intelligence) + RECAP (大规模 VLA RL)
- **本文**: 从大规模全模型 RL 转向 **精准阶段的轻量级在线 RL**
- **定位**: 部署时在线适应（Online Adaptation），解决 VLA "最后一毫米" 精度问题

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 维度 | RECAP (π prior work) | RLT (本文) |
|------|---------------------|------------|
| RL 目标 | 整个长时程任务端到端改进 | 精密阶段的针对性改进 |
| 计算需求 | 全 VLA 模型微调 | 冻结 VLA，仅训练小型 actor-critic |
| 数据需求 | 大规模集群训练 | **15 分钟**真实机器人数据 |
| 训练位置 | 离线集群 | **机器人本地实时** (hundreds of updates/sec) |
| 学习范式 | End-to-end RL | 信息瓶颈 + 残差动作编辑 |

### 关键贡献点
1. **RL Token 信息瓶颈**: 编码器-解码器 Transformer 将 VLA 内部 embedding 压缩为单个紧凑 token，冻结后作为下游 RL 的状态输入
2. **残差动作编辑 (Residual Action Editing)**: Actor 接收 VLA 的预测 action 作为输入，学习 **编辑** 而非 **替代** VLA 动作；正则化保持接近 VLA 参考分布
3. **Reference-Action Dropout**: 防止 actor 简单复制 VLA 动作，强制维持独立的动作生成路径
4. **Human Intervention Folding**: 可选地将人类纠正直接整合到 RL 更新中

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 RL Token 提取

VLA 冻结后，添加编码器-解码器 Transformer：

$$
\text{RL Token} = \text{Encoder}_\phi(\text{VLA Embeddings})
$$

解码器重建原始 VLA embedding：

$$
\hat{e}_{\text{VLA}} = \text{Decoder}_\psi(\text{RL Token})
$$

训练目标为重建损失：

$$
\mathcal{L}_{\text{recon}} = \|\hat{e}_{\text{VLA}} - e_{\text{VLA}}\|^2
$$

**关键设计**: RL token 必须保留足够信息使解码器能重建完整 VLA 表征 → 信息瓶颈（Information Bottleneck）原理确保 token 捕获最关键的状态信息。

### 3.2 残差动作编辑

Actor 网络 $\pi_\theta$ 的输入为 RL token $z$ 和 VLA 预测动作 $a_{\text{VLA}}$：

$$
a = \pi_\theta(z, a_{\text{VLA}}) = a_{\text{VLA}} + \Delta a_\theta(z, a_{\text{VLA}})
$$

训练时对 $a_{\text{VLA}}$ 施加 dropout（reference-action dropout），防止策略退化为恒等映射。

正则化项约束 RL 策略不远离 VLA 先验：

$$
\mathcal{L}_{\text{reg}} = \lambda \cdot \|a - a_{\text{VLA}}\|^2
$$

### 3.3 Action Chunking 匹配

RL 策略预测的动作是 **action chunks**（与 VLA 输出结构匹配），而非单步低级控制命令。这保证了：
- 时序结构一致性（temporal coherence）
- 与 VLA 的动作空间对齐
- 在接触丰富操作中的平滑性

### 3.4 Off-Policy RL 训练

使用 sample-efficient off-policy 方法（类似 SAC），actor-critic 网络极小，在机器人本地以 **每秒数百次更新** 的速度训练：

- **State**: RL token $z$ (紧凑)
- **Action**: Action chunk (与 VLA 对齐)
- **Reward**: 任务特定的阶段性反馈

### 3.5 核心伪代码

```python
# RL Token + Residual Action Editing (核心 tensor ops)
class RLTokenSystem(nn.Module):
    def __init__(self, vla, encoder, decoder, actor, critic):
        self.vla = vla.requires_grad_(False)        # 冻结 VLA
        self.encoder = encoder                       # 压缩 Transformer
        self.decoder = decoder                       # 重建 Transformer
        self.actor = actor                           # 轻量 actor
        self.critic = critic                         # 轻量 critic

    def extract_token(self, obs):
        with torch.no_grad():
            vla_emb = self.vla.encode(obs)           # VLA 内部表征
            a_vla = self.vla.predict(obs)            # VLA 动作块
        z = self.encoder(vla_emb)                    # 信息瓶颈 → 单 token
        return z, a_vla, vla_emb

    def act(self, obs, p_drop=0.1):
        z, a_vla, _ = self.extract_token(obs)
        # Reference-action dropout: 防止恒等映射
        mask = (torch.rand(1) > p_drop).float()
        a_ref = a_vla * mask
        delta = self.actor(z, a_ref)                 # 残差动作
        return a_vla + delta                         # VLA base + RL 修正

    def train_step(self, batch):
        z, a_vla, vla_emb = self.extract_token(batch.obs)
        # 1. 重建损失 (压缩训练)
        recon = self.decoder(z)
        L_recon = F.mse_loss(recon, vla_emb.detach())
        # 2. SAC-style actor-critic
        a = self.act(batch.obs)
        q = self.critic(z.detach(), a)
        L_reg = self.lam * (a - a_vla.detach()).pow(2).mean()
        L_actor = -q.mean() + L_reg
        return L_recon, L_actor
```

## 4. 实验与验证 (Experiments)

### 实验设置
- **机器人**: Physical Intelligence 机器人平台（双臂 + 腕部相机 + 基座相机）
- **任务**: 4 个精密操作任务
  - 电动螺丝刀拧 M3 螺丝（亚毫米精度）
  - 扎带固定
  - 以太网线插入
  - 电源线插入
- **Baseline**: π₀ VLA base model (无 RL)
- **评估指标**: Throughput（每 10 分钟成功次数），Episode Length

### 关键结果

| Task | Base Model | RLT | 提升 |
|------|-----------|-----|-----|
| Screwdriver | ~5/10min | ~15/10min | **3×** |
| Zip Tie | ~6/10min | ~15/10min | **2.5×** |
| Ethernet Insert | 147/10min | ~350/10min | **2.4×** |
| Charger Plug | ~200/10min | ~500/10min | **2.5×** |

**关键发现**:
- Ethernet 任务：仅 **15 分钟** 真实数据（算上 reset 共 2 小时）即可完成训练
- 最终 RLT 策略的执行速度 **超过人类遥操作**（中位 episode length: RLT 66 vs Teleop 146）
- Base VLA 在粗操作阶段表现良好，但在精密阶段（接触丰富 + 亚毫米精度）失败率高

### Ablation 因果链

| 去掉组件 | 效果变化 | 因果机制 |
|---------|---------|--------|
| 去掉 Reference-Action Dropout | 改进归零 | Actor 学习恒等映射 $\Delta a \to 0$ → 直接复制 VLA 动作 → RL 无效 |
| 去掉残差结构 (独立 actor) | 收敛变慢 3× | 丢失 VLA 先验 $a_{VLA}$ 作为初始解 → actor 需从零学习完整动作 → 样本效率降 |
| 去掉正则化项 $\mathcal{L}_{reg}$ | 偶发危险动作 | RL 策略偏离 VLA 分布过远 → 进入 VLA 未见的动作空间 → 不可预测行为 |
| 全程 RL → 仅精密阶段 | 数据需求 5×+ | 粗操作阶段 VLA 已足够好 → RL 在此阶段无改进空间 → 浪费采样预算 |
| RL Token 维度过小 | SR 下降 | 信息瓶颈过窄 → 丢失精密操作所需的细粒度感知信息 (如小零件方向) |

## 5. 工程关键细节 (Engineering Tricks)

- **RL Token 维度选择**: 需要在信息保留和状态压缩之间平衡；过大失去紧凑性优势，过小丢失关键感知信息
- **Reference-Action Dropout**: 关键！没有它 actor 会学习恒等映射（直接复制 VLA 动作）
- **阶段聚焦**: 只在任务最精密阶段启用 RLT，而非整个操作流程——大幅减少训练数据需求
- **Action Chunk 一致性**: RL 输出必须与 VLA action chunk 结构匹配，否则会导致时序不一致和抖动
- **人类纠正整合**: 当机器人卡住或犯错时，人类介入可直接折叠回 RL 更新，加速收敛

## 6. 核心洞见 (Insights)

### 6.1 理论局限性分析

**理论维度**:
- RL token 的信息瓶颈本质上是一种有损压缩，对于需要视觉细粒度信息的任务（如微小零件方向判断），压缩可能丢失关键信息
- 残差动作编辑假设 VLA 的初始动作"大致正确"，对 VLA 完全失败的任务阶段可能不适用

**算法维度**:
- 冻结 VLA 意味着 RL token 的表征质量上限由 VLA 决定——如果 VLA 内部表征对精密操作信息编码不足，RL token 也无法弥补
- Off-policy RL 的 replay buffer 在快速变化的精密操作场景中可能存在 staleness 问题

**工程维度**:
- 螺丝刀任务的亚毫米精度要求意味着相机标定、手眼标定的误差会直接限制 RL 的学习上界
- "每秒数百次更新" 需要极小的网络和高效的 RL 实现，扩展到更复杂的状态空间可能受限

### 6.2 与灵巧操作研究的启发

1. **RL Token 对灵巧手 VLA 的迁移**: 灵巧手操作的精密阶段（如转笔的关键接触切换点）同样可以用 RL token + 轻量级 actor-critic 实现在线精细化，而无需重训全 VLA
2. **残差动作编辑对 Sim-to-Real 的启发**: 类似思想可用于 sim-to-real gap 修正——仿真策略提供 "base action"，小型残差策略在真实环境中学习修正（与 [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|Residual Learning from Demonstration]] 形成呼应）
3. **阶段聚焦训练对 DNPM 项目的价值**: 动态非抓取操作中，最难的阶段（如高速旋转中的接触切换）可以用 RLT 思想进行阶段性在线 RL，而非端到端重训

## 7. 演进脉络定位 (Evolution Context)

### 6.5 与知识体系的数学联系

**与 [[ReinforcementLearning]] 的联系 — 信息瓶颈与状态抽象**:

RL Token 的压缩过程是信息瓶颈原理的直接应用。优化目标可被解为:
$$\min_{\phi} I(z; e_{VLA}) - \beta \cdot I(z; a^*_{task})$$
即压缩表征 $z$ 应保留与任务最优动作 $a^*$ 的互信息，同时最小化与原始 VLA embedding 的互信息。这与 VIB (Variational Information Bottleneck) 的理论框架一致。

**与 [[RepresentationLearning]] 的联系 — 残差学习与表征分层**:

残差动作编辑的数学本质是表征分层: VLA 提供粗粒度表征 $a_{VLA}$，RL 策略学习残差 $\Delta a$:
$$a = a_{VLA} + \Delta a, \quad \|\Delta a\| \ll \|a_{VLA}\|$$
这与 ResNet 的残差连接、Sim-to-Real 中的残差策略（如 [[Residual Learning from Demonstration: Adapting DMPs for Contact-rich Manipulation|Residual Learning from Demonstration]]）共享相同的数学结构。残差假设的关键约束是基策略必须“大致正确”，否则补傁空间不足。

**与 [[EmbodiedAI]] 的联系 — VLA 后训练粒度谱**:

RLT 在 VLA RL 后训练谱系中定位为“精密阶段轻量级”：
$$\text{RECAP (full VLA RL)} \supset \text{RL-100 (task RL)} \supset \text{RLT (phase RL)}$$
从全模型微调到冻结+残差，谱系逝渐减少可训练参数量和数据需求，换取部署时效率。

```
前置工作:
├── π₀ VLA — 大规模视觉-语言-动作基础模型
├── RECAP — VLA 的大规模 RL 后训练
├── HIL-SERL — 人类在环高效真实世界 RL
└── RLPD — 演示增强的 Off-Policy RL
    ↓
本论文: RLT (RL Tokens)
├── 信息瓶颈: VLA → RL Token (紧凑状态)
├── 残差动作编辑: VLA action + RL delta
├── 阶段聚焦: 仅改进精密阶段
└── 15分钟真实数据 → 3× 加速
    ↓
后续影响:
├── 部署时自适应: 机器人在工作中持续改进
├── 多粒度 RL: 从 RECAP 全模型到 RLT 精密阶段
├── 灵巧手 VLA 的在线精细化
└── 与 test-time RL / online adaptation 的融合
```
