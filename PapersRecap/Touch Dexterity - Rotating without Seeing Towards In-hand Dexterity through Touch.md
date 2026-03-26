---
tags:
  - paper
  - dexterous-manipulation
  - tactile-sensing
  - sim-to-real
  - reinforcement-learning
aliases:
  - Touch Dexterity
  - Rotating without Seeing
paper-year: 2023
read-date: 2026-02-01
venue: ICRA 2023
paper-pdf: "[[Papers/Touch Dexterity - Rotating without Seeing.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ContactMechanics]]"
---

# Touch Dexterity: Rotating without Seeing - Towards In-hand Dexterity through Touch

> [!abstract] 核心概要
> 提出 Touch Dexterity 系统，使用**密集二值力传感器阵列**（16 个 FSR）实现**纯触觉**的手内物体旋转，无需视觉输入即可泛化到训练中未见过的物体。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#2.5 On-Policy 演进线：从 TRPO 到 PPO]] - PPO 策略学习
> - [[RepresentationLearning#5. Multimodal Fusion & Tactile Intelligence: 触觉与视觉的交响 (Symphony of Vision and Touch in Multimodal Fusion)]] - 触觉表征的隐式学习
> - [[SignalProcessing]] - 二值化触觉信号处理
> - [[ContactMechanics]] - 接触状态感知
>
> **核心技术**: 二值触觉传感、Domain Randomization、IsaacGym 并行训练

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
用 16 个廉价的二值力传感器（touch/no-touch）覆盖整个手掌和手指，通过 RL 学习手内旋转策略，实现 **零样本 Sim-to-Real 迁移**到未见物体。

### 直观隐喻
想象在黑暗中洗碗——我们依靠触觉感知物体位置和接触状态来操作。Touch Dexterity 让机器人具备同样的能力：不看，只靠"感觉"。

### 领域定位
```
OpenAI Rubik's Cube (视觉主导)
         ↓
Touch Dexterity (纯触觉, 二值信号)
         ↓
后续: HORA, DLR Tactile (本体感觉 + 触觉估计)
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
| 维度 | 前人工作 | Touch Dexterity |
|-----|---------|-----------------|
| 传感器 | 高精度指尖传感器 (GelSight) | 廉价二值 FSR 覆盖全手 |
| 覆盖范围 | 指尖局部 | 掌心 + 指节 + 指尖 |
| Sim2Real Gap | 大（精细力值难模拟） | **极小**（二值化消除模拟差距） |
| 物体泛化 | 训练物体 | 未见物体 ✅ |

### 关键贡献点
1. **二值触觉设计哲学**: $2^{16}$ 种状态组合足以隐式编码物体位姿
2. **全手覆盖传感布局**: 16 个 FSR 覆盖 palm + links + fingertips
3. **零样本泛化**: 训练于简单物体，测试于 10+ 复杂未见物体

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 二值触觉表征

#### 传感器模型
$$
b_i = \mathbb{1}[\|F_i\| > \theta_{th}]
$$

其中：
- $F_i$：第 $i$ 个 FSR 的接触力
- $\theta_{th}$：二值化阈值（实验中 ~0.01N）
- $b_i \in \{0, 1\}$：二值触觉信号

#### 信息容量分析
16 个二值传感器 → $2^{16} = 65536$ 种可能状态，足以编码：
- 物体在手中的粗略位置
- 关键接触点（哪些手指在接触）
- 接触模式的时序变化

### 3.2 策略网络架构

**观测空间**:
$$
o_t = [\underbrace{q_t, \dot{q}_t}_{\text{本体感觉}}, \underbrace{b_t}_{\text{触觉}}, \underbrace{a_{t-1}}_{\text{上一动作}}]
$$

**动作空间**: 关节位置增量 $\Delta q \in \mathbb{R}^{16}$

**奖励函数**:
$$
r = r_{\text{rotation}} + r_{\text{alive}} - r_{\text{energy}}
$$

### 3.3 Sim-to-Real 策略

```
关键洞察: 二值化 = 天然的 Domain Adaptation
├── 真实世界: 模拟电压 → 阈值比较 → 0/1
├── 仿真: 接触力 → 阈值比较 → 0/1  
└── 两者在二值层面近乎完美对齐
```

### 3.4 核心策略代码逻辑

```python
# Touch Dexterity 核心: 二值触觉观测构建 + PPO 策略前向
import torch
import torch.nn as nn

class TouchDexPolicy(nn.Module):
    def __init__(self, n_joints=16, n_tactile=16, hidden=256):
        super().__init__()
        # obs = [q(16), dq(16), tactile_binary(16), prev_action(16)] = 64
        obs_dim = n_joints * 2 + n_tactile + n_joints
        self.mlp = nn.Sequential(
            nn.Linear(obs_dim, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
            nn.Linear(hidden, hidden), nn.ELU(),
        )
        self.mu_head = nn.Linear(hidden, n_joints)   # delta q
        self.log_std = nn.Parameter(torch.zeros(n_joints))

    def forward(self, q, dq, tactile_raw, prev_action, threshold=0.01):
        # 二值化: 消除 Sim-to-Real gap 的关键
        tactile_binary = (tactile_raw.abs() > threshold).float()  # (B, 16)
        obs = torch.cat([q, dq, tactile_binary, prev_action], dim=-1)
        h = self.mlp(obs)
        mu = self.mu_head(h)          # 关节位置增量
        std = self.log_std.exp()
        return mu, std                # PPO 用 Normal(mu, std) 采样

# 奖励计算: 旋转进度 + 存活 - 能量
def compute_reward(obj_rot_diff, is_alive, joint_torques, target_axis):
    # 沿目标轴的角度变化量
    r_rot = (obj_rot_diff * target_axis).sum(dim=-1)  # 投影到目标旋转轴
    r_alive = is_alive.float() * 0.5
    r_energy = -0.001 * (joint_torques ** 2).sum(dim=-1)
    return r_rot + r_alive + r_energy
```

### 3.5 触觉提供的两类信息

| 信息类型 | 描述 | 示例 |
|---------|------|------|
| **位置信息** | 物体在手中的位置 | 只有掌心传感器触发 → 物体在中央 |
| **交互信息** | 关键接触点状态 | 拇指触发 → 可以开始推动旋转 |

## 4. 实验与验证 (Experiments)

### 实验设置
- **硬件**: Allegro Hand (16-DoF) + XArm6 + 16 FSR (每个 ~$12，总成本 ~$192)
- **任务**: 绕 x/y/z 轴连续旋转物体（无终止角度限制）
- **仿真**: IsaacGym GPU 并行，4096 环境同时运行
- **训练规模**: PPO，~5000 epochs，每 epoch 约 4096×24 steps；总 ~5×10⁸ 环境交互步
- **网络**: 3 层 MLP (256 hidden)，ELU 激活
- **关键超参**: lr = 5e-4, γ = 0.99, GAE λ = 0.95, clip ε = 0.2
- **Domain Randomization**: 物体质量 ±30%, 摩擦系数 ±50%, 传感器阈值 ±20%
- **训练物体**: 8 类几何体（球、盒、圆柱、棱柱等），测试扩展到 10+ 未见物体

### 关键结果

| 物体类型 | 成功率 | 备注 |
|---------|-------|------|
| 训练物体 (几何体) | ~90% | 基线 |
| 未见物体 (橡皮鸭等) | ~70% | 零样本泛化 |
| 无触觉基线 | ~30% | 触觉关键性验证 |

### 消融实验（因果链分析）

| 消融条件 | 成功率变化 | 因果机制 |
|---------|-----------|----------|
| 禁用所有触觉 | ~90% → ~30% | 失去接触状态感知 → 策略退化为盲操作 → 无法判断物体是否在手中 |
| 仅指尖触觉 (5 sensors) | ~90% → ~55% | 丢失掌心接触信息 → 无法感知物体落入掌心的"安全状态" → 重新抓取策略失效 |
| 连续力值 (非二值) | Sim ~92% / Real ~40% | 仿真力精度≠真实力精度 → Sim2Real gap 剧增 → 策略 overfitting 到仿真力分布 |
| 无 Domain Randomization | Sim ~93% / Real ~25% | 策略记忆仿真特定物理参数 → 真实环境参数偏移后策略崩溃 |
| 单物体训练 | 该物体 ~95% / 新物体 ~20% | 策略编码了特定物体几何 → 无法泛化到不同接触模式 |

**核心因果洞察**: 二值化触觉 + 全手覆盖 + Domain Randomization 三者缺一不可——二值化保证 Sim2Real 对齐，全手覆盖提供充分状态信息，DR 防止 overfitting

## 4.5 工程关键细节 (Engineering Tricks)

1. **二值化阈值校准**: FSR 原始电压信号的阈值需要逐传感器校准，消除个体差异；仿真中对阈值做 ±20% DR 以覆盖真实偏差
2. **FSR 安装工艺**: 传感器通过 Kapton 胶带贴附于手指连杆表面，需保证不影响关节运动范围；掌心区域使用柔性 PCB 走线
3. **通信延迟处理**: 16 路 FSR 通过 Arduino 采集 → USB 串口 → 策略推理；控制频率 20 Hz，需确保触觉读取 < 5ms
4. **IsaacGym 接触查询**: 使用 `gym.acquire_net_contact_force_tensor()` 获取接触力，再在 GPU 端二值化，避免 CPU-GPU 数据搬运
5. **物体重置策略**: 物体掉落后从手上方随机位姿重新放置，附加 1s 的 settling 时间让物体稳定
6. **数值稳定性**: 二值触觉消除了连续力值的数值精度问题，但需确保阈值不在力传感器噪声带内（阈值 >> 噪声 RMS）

## 5. 批判性分析 (Critical Analysis)

### 优势
- **极简硬件成本**: 16×$12 = $192 触觉系统
- **Sim2Real 零样本**: 二值化是天然的域适应
- **物体泛化**: 不依赖物体几何先验

### 局限性（三维度分析）

| 维度 | 局限性 | 替代方案 |
|------|--------|----------|
| **理论** | 二值触觉丢失力幅值信息 → 无法精确控制接触力 → 不适用于易碎物体 | [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map\|Tacmap]] 的穿透深度图保留连续接触几何 |
| **理论** | 16 个传感器的 Shannon 信息容量 (16 bit/step) 对复杂多物体场景不足 | 高分辨率触觉皮肤 (e.g., ReSkin ~100+ taxels) |
| **算法** | 纯 PPO + MLP 无记忆 → 无法利用触觉时序模式进行状态估计 | LSTM/Transformer 策略或显式粒子滤波状态估计 |
| **算法** | 旋转轴需预先指定，无法自主选择操作目标 | 目标条件策略 (goal-conditioned RL) 或分层策略 |
| **工程** | FSR 耐久性差 (~10k 次循环)，实验周期长时需频繁更换 | 电容式或压阻式触觉皮肤 |
| **工程** | 20 Hz 控制频率限制了高速旋转任务的性能 | FPGA 或嵌入式 GPU 推理降低延迟 |

### 未来方向
- 扩展到 6-DoF 重定向任务
- 结合视觉的多模态策略
- 更密集的触觉阵列（如皮肤式传感器）

## 6. 与知识体系的联系 (Foundation Links)

> [!important] 核心启发
> **"Less is More"** — 低分辨率但高覆盖率的触觉可能比高分辨率局部触觉更有效。

### 与 [[ReinforcementLearning]] 的联系

本文使用 PPO 的 clipped surrogate objective 训练策略：
$$
L^{\text{CLIP}}(\theta) = \hat{\mathbb{E}}_t \left[ \min\left( r_t(\theta) \hat{A}_t,\; \text{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) \hat{A}_t \right) \right]
$$
其中 $r_t(\theta) = \frac{\pi_\theta(a_t|o_t)}{\pi_{\theta_{\text{old}}}(a_t|o_t)}$ 为重要性比率。关键点：触觉二值化使得观测空间离散化程度增高，PPO 的策略梯度估计方差更低（触觉观测的条件熵 $H(o_{\text{tactile}}) \leq 16$ bits），有利于 on-policy 方法的样本效率。

### 与 [[SignalProcessing]] 的联系

二值化本质上是 1-bit 量化：
$$
b_i = Q_1(F_i) = \text{sign}(F_i - \theta_{\text{th}})
$$
根据 [[SignalProcessing]] 中的量化噪声理论，1-bit 量化的信噪比极低（SNR ≈ 1.9 dB），但通过**空间多路复用**（16 个传感器）和**时间多路复用**（20 Hz 采样的时序模式）恢复了足够的信息量。这与 Sigma-Delta 调制的思想相似：用过采样 + 1-bit 量化替代高精度低速采样。

### 与 [[ContactMechanics]] 的联系

二值触觉直接编码接触状态的拓扑结构——哪些面接触 vs 不接触。这与接触力学中的 **接触模式 (contact mode)** 概念对应：
$$
\mathcal{M}_t = \{(i, c_i) \mid c_i \in \{\text{contact}, \text{free}\},\; i = 1,\dots,16\}
$$
每个接触模式对应一个不同的动力学约束集，策略隐式学会了在不同接触模式间切换以实现旋转。

### 具体应用
1. **触觉硬件设计**: 全手覆盖的廉价传感器阵列
2. **Sim2Real 策略**: 通过离散化/二值化减小域差距
3. **表征学习**: 触觉可以隐式编码物体状态，无需显式建模

## 7. 演进脉络定位与跨方法对比 (Evolution & Comparison)

```
前置工作:
├── OpenAI Dactyl (2018): 视觉主导的手内操作
├── GelSight 系列: 高精度指尖触觉
└── 本体感觉旋转 (Qi et al. 2022 HORA)
    ↓
本论文 (2023):
├── 核心突破: 纯触觉 + 二值信号 + 零样本泛化
└── 关键洞察: 二值化消除 Sim2Real gap
    ↓
后续发展:
├── DLR Tactile Manipulation: 粒子滤波状态估计
├── Robot Synesthesia: 视触觉联合学习
└── 更复杂任务: 装配、工具使用
```

### 跨方法结构化对比

| 维度 | Touch Dexterity (2023) | [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] (2022) | [[AnyRotate - Gravity-Invariant In-Hand Object Rotation with Sim-to-Real Touch\|AnyRotate]] (2024) | [[Contact-Grounded Policy - Dexterous Visuotactile Policy with Generative Contact Grounding\|Contact-Grounded Policy]] (2025) |
|------|----------------------|------------|-----------|-------------------------|
| **感知模态** | 纯触觉 (16 binary FSR) | 纯本体感觉 | 本体 + 触觉 (DIGIT) | 视觉 + 触觉 |
| **触觉类型** | 二值力 (0/1) | 无 | 连续力 + 穿透深度 | 仿真触觉图像 |
| **自适应机制** | Domain Randomization | RMA (在线自适应) | RMA + 触觉 | 生成式接触先验 |
| **Sim2Real 策略** | 二值化天然对齐 | 自适应模块消除gap | 触觉 gap 显式处理 | 扩散模型生成接触 |
| **物体泛化** | ✅ 零样本 | ✅ 零样本 | ✅ 重力不变 | ✅ 接触先验泛化 |
| **控制频率** | 20 Hz | 20 Hz | 30 Hz | 10 Hz |
| **任务** | 单轴旋转 | 单轴旋转 | 任意姿态旋转 | 多任务操作 |
| **核心优势** | 硬件极简 + 零 gap | 无需传感器 | 重力鲁棒 | 多模态融合 |

---

## 参考信息

- **作者**: Zhao-Heng Yin, Binghao Huang, Yuzhe Qin, Qifeng Chen, Xiaolong Wang
- **机构**: HKUST, UC San Diego
- **项目页**: http://touchdexterity.github.io
- **ArXiv**: 2303.10880

## 8. 与用户研究的启发（灵巧手转笔/Sim-to-Real）

**核心 takeaway**: 纯触觉即可实现手内旋转，视觉不是必需的。

1. **触觉表征的充分性**: 本文证明触觉单独就能提供足够的状态信息用于接触丰富任务。对于转笔，指腹触觉可能比视觉更重要（高速旋转时视觉模糊）
2. **Teacher-Student 触觉策略**: 可借鉴本文的 teacher-student 架构——仿真中用特权信息（精确接触力）训练 teacher，然后蒸馏到仅用触觉读数的 student 策略
3. **Sim-to-Real 触觉 Gap**: 仿真触觉<->真机触觉的差异是本文和用户研究的共同挑战，可结合 [[Tacmap - Bridging the Tactile Sim-to-Real Gap via Geometry-Consistent Penetration Depth Map|Tacmap]] 的穿透深度图方法处理
