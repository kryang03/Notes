---
tags:
  - paper
  - reinforcement-learning
  - world-model
  - vla
  - embodied-ai
aliases:
  - WMPO
  - World Model-based Policy Optimization
paper-year: 2025
read-date: 2026-03-03
venue: arXiv
paper-pdf: "[[Papers/WMPO: World Model-based Policy Optimization for.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
---

# WMPO: World Model-based Policy Optimization for Vision-Language-Action Models

> [!abstract] 核心贡献
> 提出 **WMPO**，首个将**像素空间视频世界模型**与 **VLA 策略优化**完整结合的框架。核心创新: (1) 在像素空间而非隐空间运行世界模型，使 VLA 直接利用预训练视觉特征；(2) Policy Behavior Alignment 微调世界模型以匹配策略分布；(3) 将 GRPO (Group Relative Policy Optimization) 完全在"想象"轨迹上执行，无需真实世界交互即可实现 on-policy RL。展现涌现的自我纠正行为和强泛化能力。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — Model-based RL、GRPO、On-policy vs Off-policy 权衡
> - [[EmbodiedAI]] — VLA 模型 RL 后训练范式、视频世界模型
> - [[RepresentationLearning]] — 像素空间 vs 隐空间世界模型、VLA 视觉特征对齐
> - [[StochasticProcess]] — 视频扩散模型、噪声帧条件化
>
> **核心技术**: Pixel-Space World Model, Policy Behavior Alignment, GRPO, Video Diffusion, Noisy-Frame Conditioning

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
用预训练视频世界模型替代真实世界交互进行 VLA 策略的 on-policy RL 训练——"在想象中训练，在现实中部署"。

### 直观隐喻
像围棋 AI 在棋盘模拟器中自我对弈学习一样，WMPO 让机器人在"脑海中的视频仿真器"里反复尝试，从失败中学习自我纠正策略，而无需承担真实世界失败的成本。

### 领域定位
- **核心痛点**: VLA 模型的 IL 训练 → 分布外状态脆弱 + 无法从失败学习
- **现有解法**: 真实世界 RL (RL-100) 有效但采样效率极低；仿真 RL 有 sim-to-real gap
- **WMPO 路径**: 用学习到的像素级世界模型作为"可微分仿真器"，实现免真实交互的 on-policy RL

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 对比方法 | WMPO 优势 |
|---------|-----------|
| 标准 IL (行为克隆) | 从失败中学习、涌现自我纠正 |
| 真实世界 RL (RL-100) | 采样效率大幅提升、无需真实交互 |
| 隐空间世界模型 (Dreamer等) | 像素空间与 VLA 预训练特征对齐 |
| 仿真 RL (sim-to-real) | 无需构建任务专用仿真器 |

### 关键贡献点
1. **像素空间世界模型**: 保持与 VLA 视觉编码器的特征空间一致性
2. **Policy Behavior Alignment**: 用策略自身的滚动数据微调世界模型，扩展失败场景覆盖
3. **On-Policy GRPO 在想象中**: 完全在世界模型生成的轨迹上执行 GRPO，支持同一初始状态的重复滚动
4. **涌现行为**: 自我纠正策略 + 更快/更流畅的任务完成

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 问题建模

MDP $\mathcal{M} = (\mathcal{S}, \mathcal{A}, P, R)$:
- **状态空间**: $\mathcal{S} = \mathcal{I} \times \mathcal{G}$ (图像序列 + 语言指令)
- **动作空间**: $\mathcal{A}$ — 长度 K 的动作块 $a_t \in \mathbb{R}^{K \times D}$，每维离散化为 256 bins
- **转移函数**: $s_{t+1} \sim p_\phi(s_{t+1} | s_t, a_t)$ — 参数化世界模型
- **奖励函数**: $R_\psi(\tau) \in \{0, 1\}$ — 轻量二值奖励模型

**优化目标**:
$$\max_\theta \ \mathbb{E}_{\tau \sim \pi_\theta, p_\phi}[R_\psi(\tau)]$$

### 3.2 世界模型架构

基于 OpenSora 视频扩散骨干，关键改进:
- **2D VAE (SDXL)** 替代 3D VAE — 更好保留细粒度运动细节
- **Noisy-Frame Conditioning** — 条件帧加入 50/1000 步扩散噪声 → 缓解自回归误差累积
- **Frame-Level Action Control** — AdaLN 注入帧级动作信号:
$$x_i = x_i + (1 + \alpha_1^i) \cdot \text{Block}(\gamma_1^i \cdot \text{LayerNorm}(x_i) + \beta_1^i)$$

### 3.3 GRPO 策略优化

每组从同一初始状态采样 G 条想象轨迹:

**动作对数概率**:
$$\log \pi_{\theta_{old}}(a_t | s_t) = \sum_{i=1}^{K} \sum_{j=1}^{D} \log \pi_{\theta_{old}}(a_t^{i,j} | s_t)$$

**策略梯度目标** (DAPO 变体，无 KL 正则):
$$J(\theta) = \mathbb{E}\left[\frac{1}{G} \sum_{i=1}^{G} \frac{1}{T} \sum_{t=0}^{T} \min\left(r_{i,t}(\theta)\hat{A}_i, \text{clip}(r_{i,t}(\theta), 1-\epsilon_{low}, 1+\epsilon_{high})\hat{A}_i\right)\right]$$

**归一化优势**:
$$\hat{A}_i = \frac{R_i - \text{mean}(\{R_i\}_{i=1}^G)}{\text{std}(\{R_i\}_{i=1}^G)}$$

> [!note] 动态采样策略
> 如果组内所有轨迹全部成功或全部失败 → 丢弃并重采，避免梯度消失。这是 GRPO 在稀疏奖励下的关键实现细节。

### 3.4 Policy Behavior Alignment

关键洞见: OXE 预训练数据主要是成功演示 → 世界模型无法准确模拟失败场景 → 必须用策略自身的（包含失败的）滚动数据微调世界模型。

$$p_\phi^{aligned} = \text{finetune}(p_\phi^{pretrained}, \mathcal{D}_{policy-rollout})$$

这实现了**世界模型-策略的联合演化**: 策略改进 → 采集新数据 → 微调世界模型 → 更准确的想象训练。

### 3.5 核心伪代码

```python
# WMPO: GRPO on Imagined Trajectories (核心 tensor ops)
def wmpo_grpo_step(world_model, vla, reward_model, init_frame, G=8, T=16):
    rewards, log_probs_all = [], []
    for g in range(G):                              # G 组并行 rollout
        frames = [init_frame]
        log_probs = []
        for t in range(T):
            logits = vla(frames[-1])                # [K, D, 256] 离散化
            a_t = Categorical(logits=logits).sample()  # action chunk
            log_p = Categorical(logits=logits).log_prob(a_t).sum()  # 对 K×D 求和
            log_probs.append(log_p)
            next_frame = world_model.generate(
                cond=frames[-1] + noise_50,         # Noisy-Frame Conditioning
                action=a_t
            )
            frames.append(next_frame)
        R_g = reward_model(torch.stack(frames))     # 二值: {0, 1}
        rewards.append(R_g)
        log_probs_all.append(torch.stack(log_probs))
    # 动态采样: 全成功/全失败 → 丢弃重采
    rewards = torch.tensor(rewards)                 # [G]
    if rewards.std() < 1e-6:
        return None
    A_hat = (rewards - rewards.mean()) / rewards.std()  # 归一化组优势
    # GRPO (DAPO 变体, 无 KL 正则)
    loss = 0
    for g in range(G):
        ratio = (log_probs_all[g] - log_probs_old[g].detach()).exp()
        clipped = ratio.clamp(1 - eps_low, 1 + eps_high)
        loss -= torch.min(ratio * A_hat[g], clipped * A_hat[g]).mean() / G
    return loss
```

## 4. 实验与验证 (Experiments)

### 实验设置
- **仿真**: MimicGen (Square, Stack, Threading, Coffee, ThreePiece)
- **真实世界**: 桌面操作 + ALOHA 双臂
- **对比**: IL baseline, 真实世界 RL, DPO, Direct GRPO
- **VLA 基础**: OpenVLA-OFT

### 关键结果

| 方法 | 仿真 SR (平均) | 真实世界 SR |
|------|--------------|-----------|
| IL baseline | ~65% | ~60% |
| Real-world RL (DPO) | ~70% | ~65% |
| Real-world GRPO | ~75% | ~70% |
| **WMPO** | **~85%** | **~80%** |

### 涌现行为
- **自我纠正**: 策略在即将失败时主动调整操作策略（IL 中未见）
- **更快完成**: 无明显停顿，动作更流畅
- **泛化能力**: 对未见物体/位置的零样本泛化优于离线 RL

### Lifelong Learning
交替更新策略和世界模型，实现持续的性能提升，证明框架的可扩展性。

### Ablation 因果链

| 去掉组件 | SR 变化 | 因果机制 |
|---------|---------|--------|
| 去掉 Policy Behavior Alignment | 显著下降 | 世界模型仅见成功轨迹 → 无法生成真实失败场景 → GRPO 优势全正 → 无有效梯度 |
| 像素空间 → 隐空间世界模型 | SR 下降 8-12% | 隐空间与 VLA 预训练视觉编码器特征不对齐 → 策略接收失真观测 → 分布偏移 |
| 去掉 Noisy-Frame Conditioning | 长序列 SR 坍塞 | 自回归误差累积无抑制 → 第 3-4 帧后视觉失真 → 动作序列偏离现实 |
| 2D VAE → 3D VAE | 细粒度任务 SR 下降 | 3D VAE 时间维压缩丢失帧间运动细节 → 操作时序模糊 → 精密任务失败 |
| 动态采样 → 固定采样 | 收敛变慢 | 全成功组优势全零 + 全失败组无正例引导 → PPO ratio≈1 → 梯度消失 |

## 4.5 工程关键细节 (Engineering Tricks)

- **Noisy-Frame Conditioning 的噪声水平选择**: 固定 50/1000 步扩散噪声 —— 太少无法抑制自回归漂移，太多破坏条件帧信息。这是一个关键超参数，需根据视频分辨率和帧率调整
- **2D VAE vs 3D VAE**: 3D VAE（CausalVideoVAE）有时间维压缩，丢失帧间细粒度运动 → 选择 SDXL 2D VAE 逐帧编解码保留动作细节
- **二值奖励模型轻量化**: 基于 InternVL2-1B 微调，输入为少量关键帧（非全序列），可在单 GPU 上批量评估
- **Frame-Level Action Control**: 动作信号通过 AdaLN 注入而非拼接 —— 避免破坏预训练视频模型的注意力模式，保持生成质量
- **训练资源分配**: 世界模型预训练（OXE 数据）32 GPU）› GRPO 优化（8 GPU）› 奖励模型训练（1 GPU）

## 5. 批判性分析 (Critical Analysis)

### 优势
- **原理性创新**: 像素空间世界模型 + VLA 特征对齐的洞见切中 latent world model 的核心痛点
- **涌现行为**: 自我纠正是超越 IL 天花板的强有力证据
- **实用性**: 大幅减少真实世界交互需求

### 局限性
- **世界模型保真度瓶颈**: 像素级视频生成仍存在视觉失真和动作-帧不对齐
- **计算成本**: 视频生成的计算开销远高于实际环境交互的计算开销（虽然减少了物理交互）
- **仅二值奖励**: 粗粒度的成功/失败信号限制了策略优化的精度
- **未验证高频接触任务**: 灵巧操作等需要精确力控制的场景未涉及

### 未来方向
- 高保真世界模型用于接触丰富操作（力/触觉通道）
- 与 RL-100 的互补: WMPO 前期训练 + 少量 RL-100 在线微调
- 多模态世界模型（视频+力+触觉）

## 6. 对灵巧操作的启发 (Implications)

> [!important] 对 DNPM 项目的核心启发
> 1. **World Model + RL 是 VLA 后训练的核心范式之一**: 如果 DNPM 未来走 VLA 路线，WMPO 的框架可直接复用
> 2. **像素空间的必要性**: 隐空间世界模型与 VLA 预训练特征不对齐 → 对灵巧操作意味着必须保持与感知编码器的特征空间一致
> 3. **自我纠正能力**: 这是在灵巧操作中极其需要但 IL 难以获得的能力——接触状态的微小偏差需要实时纠正
> 4. **GRPO 的动态采样**: 在稀疏奖励的灵巧操作任务中，确保每个训练 batch 包含成功和失败样本的策略至关重要
> 5. **与 [[Idea-003-Causal Mediator Reward|Idea-003 CMR]] 结合**: WMPO 使用二值奖励 → 如果结合 CMR 的物理中介变量奖励，可能在世界模型想象训练中实现更精细的 credit assignment
> 6. **Policy Behavior Alignment 的一般性**: 世界模型必须匹配当前策略分布的洞见，对任何 model-based RL 方法都适用

## 7. 演进脉络定位 (Evolution Context)

### 6.5 与知识体系的数学联系

**与 [[ReinforcementLearning]] 的联系 — Model-Based RL 的样本复杂度**:

WMPO 本质是 Dyna 架构的 VLA 级扩展。在经典 Dyna-Q 中，模型生成的想象样本减少了真实交互的样本复杂度。WMPO 的优化目标可分解为:
$$\max_\theta \mathbb{E}_{\tau \sim \pi_\theta, p_\phi}[R_\psi(\tau)] = \max_\theta \mathbb{E}_{\tau \sim \pi_\theta, P_{real}}[R(\tau)] - \underbrace{D_{TV}(p_\phi \| P_{real})}_{\text{\u4e16\u754c\u6a21\u578b\u8bef\u5dee}}
$$
Policy Behavior Alignment 的作用正是最小化 $D_{TV}(p_\phi \| P_{real})$，尤其是在当前策略分布下的转移误差。

**与 [[StochasticProcess]] 的联系 — 视频扩散与序贯 Score**:

世界模型基于视频扩散，其去噪过程可理解为对条件分布 $p(x_{t+1:t+H} | x_t, a_t)$ 的 score function 的近似：
$$s_\phi(x, t) = \nabla_x \log p_\phi(x | x_{cond}, a)$$
Noisy-Frame Conditioning 相当于在条件帧上添加 score perturbation，阮断自回归误差的确定性传播。

**与 [[RepresentationLearning]] 的联系 — 像素 vs 隐空间对齐**:

Dreamer 等隐空间世界模型的表征 $z_t = g_\psi(o_t)$ 与 VLA 的视觉编码器 $f_\phi(o_t)$ 存在特征空间不对齐：$z_t \in \mathcal{Z}_{WM} \neq \mathcal{Z}_{VLA}$。WMPO 选择像素空间跳过了这个对齐问题，但代价是计算成本的大幅增加。

```
前置工作: Dreamer (隐空间世界模型) → IRIS (像素空间) → UniSim (视频世界模型)
    ↓           ↓
    ↓     VLA: RT-2 → π0 → OpenVLA → RL-100 (真实世界RL)
    ↓
本论文: WMPO — 像素空间视频世界模型 + GRPO on-policy RL for VLA
    ↓
后续影响: World Model RL → VLA Foundation Model 的标准后训练方案 → 灵巧操作?
```
