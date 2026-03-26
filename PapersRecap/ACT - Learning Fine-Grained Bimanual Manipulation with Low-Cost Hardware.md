---
tags:
  - paper
  - manipulation
  - imitation-learning
aliases:
  - ACT
  - ALOHA
paper-year: 2023
read-date: 2026-03-25
venue: RSS 2023
paper-pdf: "[[Papers/ACT: Learning Fine-Grained Bimanual Manipulation with.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[ControlTheory]]"
  - "[[StochasticProcess]]"
---

# Learning Fine-Grained Bimanual Manipulation with Low-Cost Hardware (ACT)

> [!abstract] 核心贡献
> 提出 Action Chunking with Transformers (ACT) — 通过 CVAE 隐变量编码多模态动作风格 + Transformer 解码未来 $k$ 步动作序列（Action Chunking），配合时序集成（Temporal Ensembling）实现丝滑闭环控制，将任务有效视界缩短 $k$ 倍，彻底解决行为克隆的误差累积问题。搭配低成本 (<$20k) 双臂遥操系统 ALOHA，仅用 10 分钟示范数据即达 80-90% 成功率。

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）
**一句话**：将策略输出从单步动作 $a_t$ 升维到宏观动作块 $a_{t:t+k}$，用 CVAE 编码人类示范中的多模态路径差异。

**隐喻**：
- 传统 BC（单步预测）= "蒙眼走钢丝，走一步看一步"——每步 1mm 误差累积后彻底偏离
- ACT = "睁眼看一次，在脑海中规划并连贯走完接下来 $k$ 步"——通过高频重叠预测实现极致平滑

### 1.2 现有方法的局限
- **误差累积**：传统 BC 的协变量偏移（Covariate Shift）在高精度操作中极其致命
- **非平稳数据**：人类示范数据中含停顿、多模态路径（左抓/右抓），单峰回归学到平均值
- **高成本硬件**：现有精细操作方案依赖工业级传感器和灵巧手（>$100k）

## 2. 核心方法/理论

### 2.1 关键创新点（Delta 分析）
相比 SOTA（RT-1 单步离散、BeT k-means 离散化）：
1. **动作表示升维**：从 $a_t$ 到 $a_{t:t+k}$，将有效视界缩短 $k$ 倍
2. **CVAE 多模态建模**：隐变量 $z$ 编码人类次优数据的风格差异
3. **时序集成 (Temporal Ensembling)**：重叠预测的指数加权平均，解决分块执行的卡顿

### 2.2 数学框架

**CVAE 优化目标（ELBO）**：
$$
\mathcal{L}(\theta, \phi) = \mathbb{E}_{z \sim q_{\phi}}[ \log \pi_{\theta}(a_{t:t+k} | o_t, z) ] - \beta D_{KL}(q_{\phi}(z | a_{t:t+k}, \bar{o}_t) \| P(z))
$$

- **重构项** $\log \pi_\theta$：给定观测 $o_t$ 和风格 $z$，Decoder 还原专家动作序列。使用 **$L_1$ Loss**（非 $L_2$），对微小偏差惩罚更强——高精度操作刚需
- **KL 正则项**：强制 $q_\phi \to \mathcal{N}(0, I)$，权重 $\beta$ 控制信息瓶颈
  - 训练时：Encoder 接收 $(o_t, a_{t:t+k})$，输出 $z \sim q_\phi$
  - 推理时：直接令 $z = \mathbf{0}$（先验均值），输出确定性高优策略

**时序集成加权**：
$$
a_t = \frac{\sum_{i=0}^{k-1} w_i A_t[i]}{\sum_{i=0}^{k-1} w_i}, \quad w_i = \exp(-m \cdot i)
$$
$m$ 越小 → 旧预测权重越大 → 越平滑；$m$ 越大 → 新观测反应越快

### 2.3 核心代码逻辑

```python
# ACT Transformer 核心 Forward（Decoder 部分）
def act_forward(self, obs_tokens, joint_state, z):
    """
    obs_tokens: [B, N_cam * H*W, D]  # 4 视角 ResNet18 特征展平
    joint_state: [B, 14]              # 双臂 7+7 关节角
    z: [B, D_z]                       # CVAE 隐变量 (训练: 从 Encoder 采样; 推理: 全零)
    """
    # Encoder 融合: 视觉 + 关节 + z → 条件特征
    cond = self.encoder(obs_tokens, joint_state, z)  # [B, N_tokens, D]
    
    # Decoder: 固定位置编码作 Query，条件特征作 K/V
    queries = self.pos_embed[:k]  # [k, D] — k 步动作的位置编码
    action_seq = self.decoder(queries, cond)  # [B, k, 14] — 绝对关节角度
    
    return action_seq  # 直接回归绝对关节位置（非增量）

# Temporal Ensembling（推理阶段）
def temporal_ensemble(action_buffer, m=0.01):
    """action_buffer: deque of past k predictions for current timestep"""
    weights = torch.exp(-m * torch.arange(len(action_buffer)))
    return (weights[:, None] * torch.stack(action_buffer)).sum(0) / weights.sum()
```

## 3. 训练与实验细节

### 3.1 训练设定
- **数据来源**：人类通过 ALOHA 遥操作系统收集，关节空间映射（非逆运动学）
- **数据规模**：每任务约 50 条轨迹（~10 分钟数据）
- **监督信号**：$L_1$ 重建损失 + KL 散度
- **控制频率**：50 Hz — 高频微调是抵抗物理扰动的刚需
- **动作块大小**：$k = 100$（最优）

### 3.2 评估指标
- 任务成功率 (Success Rate %)

### 3.3 核心实验结果
| 任务 | ACT | 基线 (BeT/BC) |
|------|-----|---------------|
| 开调料杯盖 | ~80% | ~0% |
| 插电池 | ~90% | ~0% |
| 穿线扎带 | ~75% | ~0% |

- 仅用 10 分钟示范数据，6 个任务 80-90% 成功率
- 此前 SOTA (BeT, RT-1) 在同等精度任务上成功率接近 0

### 3.4 Ablation Study 解读
- **Chunk size $k$**：$k=1$（退化为 BC）→ 成功率 1%；$k=100$ 最优；$k=400$（纯开环）→ 回落。因果链：$k=1$ 时误差累积 $\to$ 协变量偏移 $\to$ 崩溃；$k$ 过大 $\to$ 丧失闭环反应力
- **CVAE**：合成数据（无多模态）上有无 CVAE 等效；人类噪声数据上去掉 CVAE $\to$ 35%→2%。因果链：人类数据含多模态路径 $\to$ MSE 回归学到平均值 $\to$ 确定性撞击
- **50Hz vs 5Hz**：降频后任务时间增 62%。因果链：低频 $\to$ 无法进行物理微调 $\to$ 面对扰动无能为力

## 4. 工程关键细节 (Engineering Tricks)
- **绝对坐标 vs 增量**：直接回归绝对关节位置性能最优（多步增量会累积误差）
- **关节空间映射**：ALOHA 使用关节映射而非 IK，天然获得物理阻尼过滤手抖
- **推理时 $z = \mathbf{0}$**：无 Encoder 推理，确定性输出，无需采样多次
- **相机同步**：4 路摄像头 50Hz 必须硬件同步，20ms 偏差即导致因果关系学错
- **相机标定**：端到端黑盒不用深度/外参，但摄像头微小位移立刻导致策略失效

## 5. 核心洞见 (Insights)

### 5.1 理论局限性深度分析
- **理论**：CVAE 的 $z = \mathbf{0}$ 推理丢失了多模态表达，策略退化为 "最常见模式"
- **算法**：纯模仿学习天花板受限于演示质量，无法超越人类
- **工程**：完全依赖 RGB + 关节位置，无力/触觉反馈，透明物体操作失败

### 5.2 与用户研究（灵巧手转笔/Sim-to-Real）的启发
- **Action Chunking for PPO**：将 PPO 输出从 $[dof]$ 扩展为 $[k, dof]$ 的宏动作块，探索从"步步随机" 升级为 "以 $k$ 步为单位的有目的尝试"，有效缩短信用分配路径。PPO 的 Critic $V(s)$ 不受动作维度膨胀影响（与 Q-Learning 区别）
- **GAE 计算调整**：Action Chunk 下 Advantage 改为 $A_t = \sum_{i=0}^{k-1} \gamma^i r_{t+i} + \gamma^k V(s_{t+k}) - V(s_t)$
- **⚠️ 开环 vs 闭环陷阱**：在 RL 中使用 Temporal Ensembling 会破坏 Importance Sampling Ratio 的数学严谨性→策略崩溃。RL 阶段应严格开环执行
- **网络设计建议**：使用 Transformer Decoder / 1D-CNN 转置卷积展开时序，不要用纯 MLP 直接输出 $k \times dof$

### 5.3 ACT vs MPC 深度对齐

| 维度 | MPC | ACT |
|------|-----|-----|
| 环境认知 | Model-Based（显式 $f(x,u)$） | Model-Free（隐式拟合数据） |
| 计算负荷 | 在线优化（推理慢） | 离线训练 + 前向推理（推理快） |
| 多步使用 | 只执行第一步 | 时序加权集成 |
| 哲学共性 | 滚动推演克服短视 | 同上 |

> ACT 本质上是用 Transformer 学到了一个**被编译好的隐式 MPC 求解器**——将人类大脑的计算结果蒸馏为前向传播网络

## 6. 与知识体系的联系

### 与 [[ReinforcementLearning]] 的联系
- Action Chunking 可直接迁移到 PPO（见 §5.2），有效缩短 Horizon、缓解探索抖动
- ACT 的 CVAE 与 PPO 的单峰高斯输出形成对比：CVAE 可建模多模态，但代价是推理时坍缩为确定性输出

### 与 [[RepresentationLearning]] 的联系
- CVAE 隐变量 $z$ 作为多模态风格的信息瓶颈，$\beta$ 控制信息通过量
- Temporal Ensembling 在表征层面实现了时域平滑

### 与 [[ControlTheory]] 的联系
- 与 MPC 的滚动规划思想一脉相承（§5.3）
- 关节空间映射绕过 IK，天然引入物理阻尼

## 7. 局限与未来方向

### 7.1 论文自身局限
- 依赖廉价舵机，扭矩不足（拧紧密瓶盖失败）
- 纯 RGB 无触觉/力反馈，透明物体操作低成功率
- 单任务训练，无跨任务泛化验证

### 7.2 对灵巧手转笔 / Sim-to-Real 的启发
- **Chunked PPO 在灵巧手上的潜力**：24 自由度高频控制下，$k=5\sim10$ 的动作块可能极大缓解探索抖动
- **Dense Reward 必要性**：Chunk 执行期间必须累加每步密集奖励，而非仅末端稀疏奖励

## References
- [[Hindsight Experience Replay]]
- [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills]]
