---
tags:
  - paper
  - humanoid-control
  - motion-generation
  - curriculum-learning
  - mixture-of-experts
  - diffusion
aliases:
  - PhyGile
paper-year: 2026
read-date: 2026-03-24
venue: arXiv (2603.19305)
paper-pdf: "[[Papers/PhyGile: Physics-Prefix Guided Motion Generation.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[Dynamics]]"
  - "[[ControlTheory]]"
---

# PhyGile: Physics-Prefix Guided Motion Generation for Agile General Humanoid Motion Tracking

> [!abstract] 核心贡献
> 提出 PhyGile 框架，通过 **physics-prefix 引导** 将机器人原生扩散运动生成与敏捷通用运动跟踪 (GMT) 闭环耦合：(1) 课程 MoE 训练实现长尾敏捷运动的鲁棒跟踪；(2) 262D 机器人骨骼空间的 TP-MoE 扩散模型实现细粒度文本-运动对齐；(3) 物理前缀引导微调弥合生成-执行鸠沟，实现真机 cartwheel、breakdance 等高难度全身运动。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO]] — PPO 用于 GMT controller 微调
> - [[ReinforcementLearning#5.1 域随机化 (Domain Randomization, DR) 与 自适应 (Adaptive DR)]] — 课程学习策略
> - [[RepresentationLearning#2.2 深度解析：扩散策略 (Diffusion Policy) 的物理与数学基础]] — 条件去噪扩散生成
> - [[Dynamics]] — 262D 机器人骨骼空间动力学表示
> - [[ControlTheory]] — 运动跟踪控制器
>
> **核心技术**: Curriculum MoE + Robot-Native Diffusion + Physics-Prefix Guided Fine-tuning

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
将 **物理验证过的可执行运动前缀** 注入扩散去噪过程，让文本驱动的运动生成在 "语义丰富" 和 "动力学可行" 之间实现闭环对齐。

### 直观隐喻
想象一位体操教练（GMT tracker）先示范动作的前几秒（physics prefix），然后告诉编舞师（diffusion generator）："从这个物理可行的姿态继续编排"——编舞师不再凭空想象，而是从一个 **动力学锚点** 开始创作。

### 领域定位
- **上游**: 文本驱动运动生成（MDM、MLD、MotionGPT）+ 通用运动跟踪（GMT、ExBody）
- **本文**: 首次通过 physics-prefix 将生成与跟踪 **闭环耦合**，解决 retarget 伪影和长尾敏捷运动问题
- **贡献层次**: 系统级创新（三模块协同）而非单点算法突破

### 现有方法的局限
1. **SMPL 空间生成 + 重定向 (MDM/MLD)**: 在人体空间生成运动后重定向到机器人 → retarget 伪影（自碰撞、关节极限违反），敏捷运动中误差被放大
2. **松耦合生成-跟踪管线 (TextOp)**: 生成与跟踪单向传递，生成端无法感知 [[Dynamics|物理约束]] → 可能生成动力学不可行运动
3. **通用运动跟踪器 (GMT/ExBody)**: 对 [[Curriculum Learning|长尾敏捷运动]] 数据不足导致欠训练，hard motion 成功率骤降
4. **标准 Transformer MLP 策略**: 面对多难度级别运动时缺乏专家特化机制，简单与困难运动相互干扰导致性能折中

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 维度 | 此前 SOTA (TextOp/ExBody) | PhyGile |
|------|--------------------------|---------|
| 运动空间 | SMPL 人体 → 重定向到机器人 | 直接在 262D 机器人骨骼空间生成 |
| 生成-执行耦合 | 松耦合（生成→跟踪，单向） | 闭环耦合（physics prefix + PPO 微调） |
| 长尾敏捷运动 | 数据不平衡导致欠训练 | 课程 MoE + ASFO 过采样 |
| 文本-运动对齐 | 全局条件注入 | TP-MoE token 级参数混合 |

### 关键贡献点
1. **Physics-Prefix Guided Fine-tuning**: 用 GMT 跟踪器的可执行运动片段作为扩散前缀，receding-horizon 迭代保证动力学一致性
2. **Two-Stage Curriculum MoE Tracker**: Stage I 级别课程 + hard-biased routing 实现专家特化；Stage II 全局 soft post-training + 动态专家扩展
3. **TP-MoE (Token-level Parameter-mixing MoE)**: 在扩散模型的 FFN 层之后插入，每个文本 token 混合不同专家参数，实现细粒度时间-语义对齐

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 两阶段 MoE 通用运动跟踪

**Stage I: Level-wise Curriculum with Hard-Biased Routing**

运动按难度分为 12 级（Level 1-10 可执行，11-12 排除），逐级解锁：

$$
a_t = \begin{cases} E_{l_{\max}}(\tilde{o}_t), & l_i = l_{\max} \wedge u < \rho_{\text{hard}} \\ \sum_{j \in \mathcal{K}} p_j E_j(\tilde{o}_t), & \text{otherwise} \end{cases}
$$

其中 $\rho_{\text{hard}} = 0.8$ 为硬路由概率。辅助路由损失：

$$
\mathcal{L}_{\text{route}} = \lambda_{\text{CE}} \cdot \text{CE}(G(z_t), l_i - 1)
$$

- **新级别专家初始化**: $\theta_{E_l} \leftarrow \theta_{E_{l-1}}$（继承前一级专家权重）
- **Freeze-and-drop 自净化**: 跟踪 EMA 误差 $E_i$ 和成功率 $\hat{p}_i^{\text{succ}}$，条件 $(E_i \geq \tau_{\text{err}} \vee \hat{p}_i^{\text{succ}} \leq \tau_{\text{succ}}) \wedge n_i \geq n_{\min}$ 触发冻结/丢弃

**Stage II: Global Soft Post-Training**

移除课程掩码，使用负载均衡损失替代强级别监督：

$$
\mathcal{L}_{\text{bal}} = K \sum_{j=1}^{K} f_j \bar{p}_j
$$

支持 **动态专家扩展**：跟踪路由熵 $H(p) = -\sum_j p_j \log p_j$ 和 top-1/top-2 gap $\Delta = p^{(1)} - p^{(2)}$，持续困难文件触发新专家生成。

### 3.2 262D 机器人原生扩散生成

运动描述符不经过 SMPL，直接在机器人骨骼空间建模：

$$
m_t = \left(\dot{\omega}_t^{\text{root}}, \dot{v}_t^{\text{root}}, z_t, p_t^{\text{ric}}, R_t^{6d}, \dot{p}_t^{\text{local}}, c_t^{\text{foot}}, c_t^{\text{hand}}\right) \in \mathbb{R}^{262}
$$

各分量物理含义：
| 分量 | 维度 | 含义 |
|------|------|------|
| $\dot{\omega}_t^{\text{root}}$ | 3 | 根节点角速度 |
| $\dot{v}_t^{\text{root}}$ | 3 | 根节点线速度 |
| $z_t$ | 1 | 根节点高度 |
| $p_t^{\text{ric}}$ | 36 | 12 刚体末端位置 |
| $R_t^{6d}$ | 174 | 29 DOF 的 6D 旋转表示 |
| $\dot{p}_t^{\text{local}}$ | 39 | 13 刚体局部速度 |
| $c_t^{\text{foot}}, c_t^{\text{hand}}$ | 6 | 足/手接触指示 |

扩散训练目标：
$$
\mathcal{L}_{\text{diff}} = \mathbb{E}_{m_0, t, \epsilon}\left[\|m_0 - \hat{m}_\theta(m_t, t, l)\|^2\right]
$$

**TP-MoE**: 每个文本 token $c_i$ 通过门控混合专家参数：
$$
\hat{e}^{(i)} = \sum_{k=1}^{K} \omega_{i,k} \cdot e_k, \quad \omega_i = \text{softmax}(G(c_i))
$$

空间掩码基于交叉注意力权重 $A_{t,i}$：
$$
M_{t,i} = \sigma\left(\gamma(A_{t,i} - \beta \cdot \max_{t'} A_{t',i})\right)
$$

### 3.3 Physics-Prefix Guided Fine-tuning

**核心机制**: 冻结扩散生成器，用 PPO 微调 GMT controller：

$$
x_{1:T} \sim p_\theta\left(x_{1:T} \mid x_{\text{prefix}}, x_{\text{target}}\right)
$$

- 每次迭代：prefix → 生成 1 秒续接 → 仿真验证 (MPJPE < 阈值) → 拼接到 prefix → 重复
- **Receding-horizon** 渐进扩展，保持长时程动力学一致性
- 不通过的轨迹被拒绝并重采样（generate–simulate–select 循环）

### 3.4 ASFO (Action-Semantic Frequency-aware Oversampling)

解决长尾数据分布：
$$
\rho_m = \min\left(\lfloor \tau / f_m \rceil, \rho_{\max}\right), \quad r_j = \max_{k_m \in \phi(x_j)} \rho_m
$$

稀有语义标签额外应用左右镜像增强，mirror 概率随 $r_j$ 递增。

### 3.5 核心伪代码（PyTorch 风格）

```python
# PhyGile: Curriculum MoE Tracker + TP-MoE Diffusion + Physics-Prefix

# === Module 1: Curriculum MoE Tracker ===
class CurriculumMoETracker(nn.Module):
    def __init__(self, obs_dim, act_dim, n_experts=10, rho_hard=0.8):
        super().__init__()
        self.experts = nn.ModuleList([MLP(obs_dim, act_dim) for _ in range(n_experts)])
        self.gate = nn.Linear(obs_dim, n_experts)
        self.rho_hard = rho_hard

    def forward(self, obs, level, use_hard_routing=True):
        logits = self.gate(obs)                          # (B, K)
        probs = F.softmax(logits, dim=-1)                # (B, K)
        if use_hard_routing and torch.rand(1) < self.rho_hard:
            return self.experts[level](obs)              # 硬路由到当前级别专家
        topk_val, topk_idx = probs.topk(2, dim=-1)
        out = sum(probs[:, j:j+1] * self.experts[j](obs)
                  for j in topk_idx.unbind(-1))          # top-2 soft routing
        return out

    def route_loss(self, obs, levels):
        """级别监督交叉熵路由损失"""
        return F.cross_entropy(self.gate(obs), levels)


# === Module 2: TP-MoE Diffusion (token-level parameter mixing) ===
class TPMoEFFN(nn.Module):
    def __init__(self, d_model, n_experts=4, beta=0.7):
        super().__init__()
        self.experts = nn.ParameterList(
            [nn.Parameter(torch.randn(d_model, d_model)) for _ in range(n_experts)])
        self.gate = nn.Linear(d_model, n_experts)
        self.beta = beta

    def forward(self, motion_feat, text_tokens, cross_attn_w):
        """
        motion_feat: (B, T, D), text_tokens: (B, L, D), cross_attn_w: (B, T, L)
        """
        omega = F.softmax(self.gate(text_tokens), dim=-1)   # (B, L, K)
        # 空间掩码: token-motion 对齐
        A_max = cross_attn_w.max(dim=1, keepdim=True).values
        mask = torch.sigmoid(10 * (cross_attn_w - self.beta * A_max))  # (B, T, L)
        # 加权专家混合
        w = torch.einsum('btl,blk->btk', mask, omega)       # (B, T, K)
        w = w / (w.sum(-1, keepdim=True) + 1e-8)
        # 参数混合
        mixed_W = sum(w[..., k:k+1].unsqueeze(-1) * self.experts[k]
                      for k in range(len(self.experts)))     # (B, T, D, D)
        return torch.einsum('btdi,bti->btd', mixed_W, motion_feat)


# === Module 3: Physics-Prefix Guided Receding-Horizon Generation ===
def physics_prefix_generate(diffusion, tracker, sim_env, text,
                            prefix_len=30, gen_len=30, threshold=0.05):
    """闭环 generate–simulate–select 循环"""
    prefix = sim_env.get_initial_motion(prefix_len)     # 物理验证的初始运动
    trajectory = [prefix]
    for _ in range(max_iters):
        cond = prefix[-prefix_len:]                      # 滑动窗口前缀
        generated = diffusion.sample(text=text, prefix=cond, length=gen_len)
        result = sim_env.rollout(tracker, generated)     # GMT 仿真执行
        if result.mpjpe < threshold:                     # 物理可行性门控
            prefix = torch.cat([prefix, result.executed], dim=0)
            trajectory.append(result.executed)
        # else: 拒绝并重新采样
    return torch.cat(trajectory, dim=0)
```

## 4. 实验与验证 (Experiments)

### 实验设置
- **数据集**: HumanML3D (文本标注) + AMASS + LaFAN1 + 3h 私有 MoCap，共约 45 小时
- **机器人**: 29 DOF 人形机器人
- **Baselines**: GMT, TextOp, MDM, MLD, MotionGPT, Closd

### 关键结果

**运动生成质量**:

| Method | FID↓ | R@3↑ | Penetration(mm)↓ | Skating↓ |
|--------|------|------|-----------------|----------|
| PhyGile | **0.1823** | **0.6176** | 3.24 | 8.2% |
| PhyGile [Fine-tuned] | 0.2017 | 0.5702 | **0.00** | **1.58%** |
| TextOp | 0.3074 | 0.4975 | 0.00 | 7.5% |
| MDM† | 0.2550 | 0.6156 | 5.12 | 19.16% |

**运动跟踪精度**:

| Method | MPJPE↓ | Success↑ |
|--------|--------|----------|
| **PhyGile (full)** | **0.2566** | **0.9401** |
| PhyGile-CFM | 0.4522 | 0.8826 |
| TextOp | 0.2427 | 0.8888 |
| GMT | 0.6711 | 0.8914 |

### Ablation 关键发现
- **C → CF**: 去冻结自净化后 MPJPE 降 12.9%，成功率升 0.9%
- **CF → CFM**: 加 MoE 后角度误差降 5.1%
- **CFM → Full (Physics Prefix)**: MPJPE 降 43.2%，成功率升 6.5% — **physics prefix 是最关键组件**
- **TP-MoE 消融**: 移除后 FID 从 0.1823 升至 0.2297，R@3 从 0.6176 降至 0.5276

**Ablation 因果机制分析**:

| 消融条件 | 效果变化 | 因果机制 |
|---------|---------|--------|
| 去掉 Freeze-and-drop (C→CF) | MPJPE ↓12.9% | 冻结/丢弃失败运动阻止梯度被异常样本污染 → 低质量运动不再拖累专家参数更新 |
| 去掉 MoE (CF→CFM) | 角度误差 ↓5.1% | 多专家分工处理不同难度运动 → 避免简单/困难运动在共享参数中相互干扰 |
| 去掉 Physics Prefix (CFM→Full) | MPJPE ↓43.2%, SR ↑6.5% | 物理前缀将扩散初始分布锚定在动力学可行区域 → 去噪从物理一致起点出发 → 消除 retarget 伪影 |
| 去掉 TP-MoE | FID ↑26%, R@3 ↓15% | 失去 token 级语义-运动对齐 → 全局文本条件无法精确控制不同运动时刻 → 生成质量下降 |
| 去掉 ASFO 过采样 | 长尾运动 FID 恶化 | 稀有类别训练不足 → 扩散模型对 cartwheel/breakdance 的分布建模欠拟合 |

## 5. 工程关键细节 (Engineering Tricks)

- **低频路由刷新**: 每 M 步刷新一次 top-k 专家候选集，步间只在候选集内 softmax，减少路由抖动
- **EMA 路由平滑**: 对 routing logits 做 EMA 平滑
- **Expert 继承初始化**: 新级别专家 copy 上一级专家权重，避免从零开始
- **Dynamic Expert Addition**: 基于路由熵和 top-1/top-2 gap 监控，自动扩展专家池
- **6D 旋转表示**: 避免万向锁和不连续性（$R^{6d} \in \mathbb{R}^{174}$，29 joints × 6）
- **Canonical heading**: 第一帧朝向标准化

## 6. 核心洞见 (Insights)

### 6.1 理论局限性分析

**理论维度**:
- 扩散模型的 physics prefix 条件在理论上等价于修改了去噪过程的初始分布支撑，但缺乏收敛性保证
- MoE 路由的级别监督是启发式的（LLM-based difficulty annotation），可能引入标注噪声
- **替代方案**: 使用 [[Optimization#3.4 阶段四：可微物理与平滑化 (The Differentiable Physics & Smoothing Era)|可微物理]] 对 prefix 条件施加显式收敛约束；用自动课程发现（如 PLR）替代 LLM 难度标注

**算法维度**:
- Freeze-and-drop 机制依赖人为设定的阈值 ($\tau_{\text{err}}$, $\tau_{\text{succ}}$, $n_{\min}$)，对不同运动类型的适应性未验证
- PPO 微调 GMT 时扩散模型完全冻结，可能存在生成端-执行端的联合优化空间
- **替代方案**: 自适应阈值通过 EMA 统计量动态调整；端到端联合训练生成器+跟踪器（类似 [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control|OmniXtreme]] 的 residual 思路）

**工程维度**:
- 262D 运动空间需要大量 retargeted MoCap 数据，对新机器人形态的泛化成本高
- TP-MoE 增加了推理时的计算量（每 token 需混合 K 个专家）
- **替代方案**: 通用骨骼表示（如 UniHSI 的 language-conditioned joint mapping）减少重定向成本；[[RepresentationLearning#2.2 深度解析：扩散策略 (Diffusion Policy) 的物理与数学基础|一致性蒸馏]] 压缩多步去噪

### 6.1.1 跨方法对比

| 维度 | PhyGile | [[OmniXtreme - Breaking the Generality Barrier in High-Dynamic Humanoid Control\|OmniXtreme]] | TextOp | GMT/ExBody | [[DeepMimic - Example-Guided Deep Reinforcement Learning of Physics-Based Character Skills\|DeepMimic]] |
|------|---------|------------|--------|-----------|----------|
| 运动空间 | 262D 机器人原生 | 机器人关节 | 机器人原生 | SMPL→retarget | 人体关节 |
| 生成-执行耦合 | 闭环 (physics prefix) | 残差后训练 | 松耦合 | 松耦合 | 无生成 |
| 多运动扩展 | Curriculum MoE | [[StochasticProcess#2.1 随机微分方程 (SDEs) 的物理图景|Flow Matching]] | 单策略 | 单策略 | 单运动专家 |
| 文本条件 | TP-MoE token 级对齐 | 无 | 全局 | 无 | 无 |
| 敏捷运动 | ✅ cartwheel, breakdance | ✅ 后空翻, 武术 | 有限 | 有限 | 单运动 |
| Sim-to-Real | Physics prefix + [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO|PPO]] | 残差 + 执行器建模 | DR | DR | 基础 DR |
| 扩展瓶颈 | MoCap + retarget 成本 | MoCap 获取 | MoCap | 动态运动不足 | 单运动限制 |

### 6.2 与灵巧操作研究的启发

1. **Curriculum MoE 对灵巧手的启示**: 灵巧手操作同样存在严重的长尾分布（简单抓取 vs 复杂 in-hand rotation），PhyGile 的级别课程 + hard-biased routing 策略可直接应用于灵巧手任务分层
2. **Physics Prefix 思想的迁移**: 对于接触丰富的灵巧操作，可以用物理仿真器（MuJoCo/Isaac）产生短时物理可行的接触轨迹作为扩散策略的前缀条件，解决扩散策略生成的动作在接触切换时的不稳定性
3. **ASFO 对小样本灵巧任务的价值**: 灵巧操作数据集的长尾问题（转笔等复杂任务数据稀缺）可借鉴 ASFO 的语义频率感知过采样 + 镜像增强策略

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── GMT (ExBody) — 通用运动跟踪
├── MDM/MLD/MotionGPT — 文本驱动运动生成
├── TextOp — 机器人原生文本运动生成
└── DeepMimic — 基于参考的物理运动模仿
    ↓
本论文: PhyGile
├── 闭环耦合生成与跟踪（physics prefix）
├── 课程 MoE 解决长尾敏捷运动
└── TP-MoE 实现 token 级语义-运动对齐
    ↓
后续影响:
├── 灵巧操作扩散策略的物理可行性约束
├── 接触丰富任务的 physics-prefix 条件生成
└── MoE 在多技能机器人策略中的路由策略演进
```
