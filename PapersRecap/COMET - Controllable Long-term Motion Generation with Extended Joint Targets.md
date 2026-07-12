---
tags:
  - paper
  - motion-generation
  - character-animation
  - conditional-vae
aliases:
  - COMET
paper-year: 2025
read-date: 2026-03-24
venue: WACV
paper-pdf: "[[Papers/Lee_Controllable_Long-term_Motion_Generation_with_Extended_Joint_Targets.pdf]]"
related:
  - "[[RepresentationLearning]]"
  - "[[StochasticProcess]]"
  - "[[Dynamics]]"
  - "[[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking]]"
  - "[[KungfuBot: Physics-Based Humanoid Whole-Body Control for Learning Highly-Dynamic Skills]]"
  - "[[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation]]"
---

# Controllable Long-term Motion Generation with Extended Joint Targets (COMET)

> [!abstract] 核心贡献
> 提出 COMET，一个基于 Transformer 条件 VAE 的自回归运动生成框架，支持实时、任意关节子集的精确控制，并通过基于 GMM 的参考引导反馈机制保证长时域生成的稳定性。

> [!tip] 与理论基础的关联
> - [[RepresentationLearning#2.2.3 Classifier-Free Guidance：用观测"引导"多峰采样的贝叶斯推导]] - RGF 用 GMM 把预测姿态往自然运动流形"引导"，与 CFG 用条件引导多峰采样同属 **Continuation/平滑化(guidance) 暗线**：都在生成过程里注入一个把样本拉向可行/期望区域的力
> - [[RepresentationLearning#2.3 ACT：动作分块处理长时相关]] - 增量 $\delta_i$ 预测与 Action Chunking 的动作表示同源
> - [[StochasticProcess]] - GMM 参考引导反馈的概率建模与 Mahalanobis 距离
> - [[Dynamics]] - 角色运动的物理约束与关节控制

> [!tip] 簇内关联（运动生成 / 人形簇）
> - **vs [[PhyGile - Physics-Prefix Guided Motion Generation for Agile Humanoid Tracking|PhyGile]]**: 两者都在解"长时程运动生成如何不漂移出可行流形"。COMET 用 **GMM Reference-Guided Feedback**（推理时把预测姿态往运动流形纠偏，$\alpha$ 控强度）；PhyGile 用 **physics-prefix**（把去噪初始分布锚定在动力学可行区域）。COMET 的约束是**运动学流形**（无物理，靠数据统计的 GMM），PhyGile 的约束是**动力学可行性**（靠仿真器 rollout 门控）——这正是 COMET §7 自己承认的"未涉及接触力学约束"的差距。
> - **vs [[KungfuBot: Physics-Based Humanoid Whole-Body Control for Learning Highly-Dynamic Skills|KungfuBot]]**: COMET 是**运动学生成器**（CVAE 直接吐姿态增量），KungfuBot 是**物理跟踪器**（PPO 让真机 G1 追踪参考动作）。COMET 的 RGF 是"生成侧防漂移"，KungfuBot 的自适应 $\sigma$ 是"跟踪侧防松散"，二者可级联：COMET/PhyGile 生成参考轨迹 → KungfuBot 式 physics tracker 执行。
> - **vs [[GLIDE - Planning-Guided Diffusion Policy Learning for Bimanual Manipulation|GLIDE]]**: 增量/残差表示的共识——COMET 预测姿态增量 $\delta$、GLIDE 预测残差关节位置 $\Delta q$，都为降低生成分布的尺度/偏移方差（见 §8 跨方法对比中 VAE vs Diffusion 的实时性取舍）。

## 1. 问题设定与动机

### 1.1 核心洞察
实时可控的角色运动生成需要同时满足多关节空间约束和长时域时序稳定性——现有方法要么无法精确控制多关节，要么长序列退化严重。

### 1.2 直观隐喻
像一个经验丰富的木偶师：可以同时操控角色的任意肢体（多关节控制），即使表演很长也不会让角色的动作变形（长时域稳定），还能随时切换表演风格（插件式风格化）。

### 1.3 现有方法的局限
- **扩散模型方法**: 生成质量高但无法实时（推理需多步去噪）
- **帧级 VAE 方法 (WANDR)**: 实时但单关节控制，多关节时不稳定
- **通用问题**: 自回归模型长序列误差累积导致漂移

## 2. 核心方法

### 2.1 Delta 分析
**vs WANDR (前作)**: 从单关节扩展到任意关节子集控制 + Reference-Guided Feedback 解决长时域漂移

### 2.2 数学框架

**核心架构**: Transformer-based Conditional VAE，逐帧自回归生成关节运动增量 $\delta_i$

**Encoder** 输入当前姿态 $p_i$、增量 $\delta_i$、意图特征 $I_i$，编码到隐空间：
$$z_i \sim q_\phi(z_i | p_i, \delta_i, I_i)$$

**Decoder** 以 $z_i$、状态、意图特征为条件，预测下一帧姿态增量 $\hat{\delta}_i$

**意图特征 $I_i$**: 编码目标关节的空间约束，包括：
- 关节目标位移 $I_{joint,j}$: 从当前关节位置到目标的向量
- 骨盆中心意图 $I_{pelvis}$: 吸引骨盆朝所有控制关节平均 XY 位置移动

$$G_{avg,i}^{xy} = \frac{1}{|J_c|} \sum_{j \in J_c} G_j^{xy}$$

**Joint-wise Attention**: 使用关节级注意力机制，使模型能提取跨关节线索，处理任意关节子集的控制

**损失函数**:

$$\mathcal{L}_{total} = \mathcal{L}_{recon} + \lambda_{KL} \mathcal{L}_{KL} + \lambda_{joint} \mathcal{L}_{joint}$$

- $\mathcal{L}_{recon} = \mathbb{E}[\|\delta_i - \hat{\delta}_i\|_2^2]$ — 增量重建
- $\mathcal{L}_{KL} = D_{KL}(q_\phi(z_i | p_i, \delta_i, I_i) \| \mathcal{N}(0, I))$ — VAE 正则化
- $\mathcal{L}_{joint} = \mathbb{E}\left[\frac{1}{|J_c|}\sum_{j \in J_c} \|P_{j,i+1} - \hat{P}_{j,i+1}\|_2^2\right]$ — 控制关节精度
### 2.4 核心伪代码

```python
# COMET 前向推理核心逻辑 (PyTorch-style)
class COMETDecoder(nn.Module):
    def __init__(self, joint_dim, latent_dim, n_joints=6):
        self.transformer = TransformerDecoder(d_model=joint_dim, nhead=4, nlayers=3)
        self.intent_encoder = nn.Linear(3, joint_dim)   # 3D 目标位移
        self.z_proj = nn.Linear(latent_dim, joint_dim)
        self.delta_head = nn.Linear(joint_dim, joint_dim) # 预测姿态增量
    
    def forward(self, p_i, z_i, joint_targets, active_joints):
        # p_i: [B, n_joints, joint_dim] 当前姿态
        # z_i: [B, latent_dim] 采样的隐变量
        # joint_targets: [B, n_joints, 3] 目标位置
        # active_joints: [B, n_joints] bool mask
        
        # 1. 意图特征编码
        I_joint = self.intent_encoder(joint_targets - p_i[:, :, :3])  # 目标位移
        I_joint = I_joint * active_joints.unsqueeze(-1)  # mask 非活跃关节
        
        # 2. 隐变量融合
        z_feat = self.z_proj(z_i).unsqueeze(1).expand_as(p_i)  # broadcast
        
        # 3. Joint-wise Attention: 跨关节交互
        x = p_i + I_joint + z_feat
        h = self.transformer(x)  # [B, n_joints, joint_dim]
        
        # 4. 预测姿态增量
        delta_i = self.delta_head(h)  # [B, n_joints, joint_dim]
        p_next = p_i + delta_i
        return p_next, delta_i

def reference_guided_feedback(p_pred, gmm, alpha=0.3):
    """RGF: 将预测姿态向自然运动流形纠偏"""
    # 找最近 GMM 组件 (Mahalanobis 距离)
    dists = [mahalanobis(p_pred, mu_k, cov_k) for mu_k, cov_k in gmm]
    k_star = torch.argmin(torch.stack(dists), dim=0)
    mu_nearest = gmm.means[k_star]
    
    # 纠偏
    p_corrected = p_pred + alpha * (mu_nearest - p_pred)
    return p_corrected
```
### 2.3 Reference-Guided Feedback (RGF) — 长时域稳定核心

用 GMM 建模参考运动流形，推理时将预测姿态向自然运动流形纠偏：

$$f_{i+1} = \hat{f}_{i+1} + \alpha (\mu_{k^*} - \hat{f}_{i+1})$$

其中 $k^* = \arg\min_k D_{Mahalanobis}(\hat{f}_{i+1}, \mu_k)$，$\alpha$ 控制纠偏强度，接近最终目标时自动关闭。

**插件式风格化**: 更换 GMM 即可实时切换运动风格（如恐龙步态），无需重新训练。

## 3. 训练与实验细节

### 3.1 训练设定
- 数据: LaFAN1 数据集
- 控制关节: 6 个（骨盆 + 5 个末端执行器）
- 自回归方式: 逐帧生成增量 $\delta_i$，加到前一帧得到新姿态

### 3.2 核心实验结果
- **单关节控制**: 相比 WANDR，成功率大幅提升，foot skating 和 distance-to-goal 均显著降低
- **多关节控制**: DTG 随控制关节数增加而稳步降低，证明 Joint-wise Attention 有效
- **RGF 通用性**: 将 RGF 插入 WANDR 基线，SR 和 FS 也显著提升

### 3.3 Ablation 因果链

| 去掉组件 | 效果变化 | 因果机制 |
|---------|---------|----------|
| 去掉 Joint-wise Attention | 多关节 DTG 上升 ~40% | 关节间无交互 → 各自独立控制 → 身体平衡缺失 |
| 去掉 RGF | 30秒后轨迹漂移显著 | 自回归误差累积无纠偏机制 → 偏离自然运动流形 → 非物理姿态 |
| 去掉骨盆意图 $I_{pelvis}$ | DTG 上升 ~25% | 身体中心无法跟随末端执行器 → 大幅度运动时重心偏移 |
| GMM K 过小 (K=5) | foot skating 上升 | 运动流形建模不充分 → 纠偏向错误模态 → 运动失真 |

### 3.3 实时性能
运行速度满足实时要求（自回归逐帧生成，无需迭代去噪）

## 4. 工程关键细节
- **增量表示**: 预测姿态增量 $\delta$ 而非绝对姿态，有利于误差控制
- **RGF 关闭条件**: 接近最终目标时禁用 RGF，避免与精确目标到达冲突
- **GMM 组件数 K**: 作为超参数需调节，过少表达力不足，过多导致分散

## 5. 核心洞见

### 5.1 理论局限性
- **理论**: VAE 的后验坍缩问题在长序列中可能加剧
- **算法**: 控制精度依赖关节意图特征设计，新关节类型需额外工程
- **工程**: GMM 在极高维姿态空间中的建模能力有限

### 5.2 与用户研究的启发（灵巧手转笔/Sim-to-Real）
1. **Reference-Guided Feedback 思想可迁移**: 用 GMM 建模"自然操作流形"，当灵巧手策略偏离时向流形纠偏，可作为 Sim-to-Real 的安全约束
2. **增量预测 vs 绝对预测**: 转笔任务中预测关节角增量而非绝对角度，误差累积更可控
3. **任意关节子集控制**: 灵巧手任务中可选择性控制部分手指，其余手指由模型自由生成配合动作

## 6. 与知识体系的联系

### 与 [[RepresentationLearning]] 的联系
- CVAE 架构与 [[RepresentationLearning|Diffusion Policy]] 同属生成式策略族，但选择了实时性更优的 VAE 路线
- 增量预测 $\delta$ 的设计思想与 Action Chunking 的动作表示有关

### 与 [[StochasticProcess]] 的联系
- GMM 参考引导属于高斯混合模型在序列生成中的创新应用
- Mahalanobis 距离度量了样本到各模态中心的标准化距离

### 与 [[Dynamics]] 的联系
- 角色运动受物理约束（关节限位、foot skating），模型必须隐式学习这些约束

## 7. 局限与未来方向
- 控制精度受限于关节意图特征编码的表达力
- GMM 需离线训练，在线自适应风格切换尚未实现
- 未涉及接触力学约束（与操作任务的差距）

## 8. 跨方法对比

| 维度 | COMET (VAE) | Diffusion Policy | MDM | WANDR |
|------|-------------|-----------------|-----|-------|
| 实时性 | ✅ 逐帧自回归 | ❌ 多步去噪 | ❌ 多步去噪 | ✅ 实时 |
| 多关节控制 | ✅ 任意子集 | ✅ (通过引导) | ✅ | ❌ 单关节 |
| 长时域稳定性 | ✅ RGF 纠偏 | 中等 | 弱 (漂移) | 弱 |
| 风格切换 | ✅ 插件式 GMM | 需重训练 | 需重训练 | ❌ |
| 训练复杂度 | 低 (CVAE) | 高 (扩散过程) | 中等 | 低 |
