---
tags:
  - paper
  - bimanual-manipulation
  - visuotactile
  - teleoperation
  - imitation-learning
aliases:
  - HATO
  - Visuotactile Bimanual
paper-year: 2024
read-date: 2026-02-01
venue: arXiv 2024
paper-pdf: "[[Papers/Learning Visuotactile Skills with Two Multifingered Hands.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ContactMechanics]]"
  - "[[StochasticProcess]]"
---

# Learning Visuotactile Skills with Two Multifingered Hands

> [!abstract] 核心概要
> 提出 HATO（Hands-Arms Tele-Operation）系统，首次实现双多指手 + 视触觉感知 + 模仿学习的组合，用 VR 控制器实现直观的双手多指遥操作。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning#2.2 Imitation Learning (IL): 数据饥渴与分布漂移]] - Diffusion Policy 行为克隆
> - [[RepresentationLearning#5. Multimodal Fusion & Tactile Intelligence: 触觉与视觉的交响 (Symphony of Vision and Touch in Multimodal Fusion)]] - 视觉+触觉+本体感觉融合
> - [[SignalProcessing]] - FSR 触觉传感器信号
> - [[ContactMechanics]] - 多指手 vs 夹爪的接触优势
>
> **核心技术**: VR Teleoperation for Multifingered Hands, Prosthetic Hand for Research, Visuotactile Diffusion Policy

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
构建低成本双多指手遥操作系统（HATO），收集视触觉演示数据，训练 Diffusion Policy 完成复杂双手灵巧任务。

### 直观隐喻
就像让一个人戴着 VR 手套远程操控两只机器人手——HATO 把这套系统简化到用现成 VR 控制器就能实现，且机器人手配备了丰富的触觉传感。

### 领域定位
```
双臂夹爪系统 (ALOHA等): 灵活性受限
    ↓
单多指手 + 视觉: 无触觉、单手
    ↓
HATO (2024): 双多指手 + 视触觉 + VR遥操作 ← 本文
```

## 2. 核心创新与贡献 (Contributions & Novelty)

### 现有方法的局限
1. **夹爪系统（ALOHA 等）**: 仅 1-DoF 开合，无法实现多接触点抓取和精细操作
2. **单手系统**: 无法完成需要双手配合的任务（如倒酒+稳杯、递送+接收）
3. **纯视觉策略**: 缺乏接触力反馈，在滑溜物体和力敏任务上可靠性不足
4. **复杂遥操作**: 外骨骼/手套成本高、穿戴复杂，限制数据收集规模
5. **缺乏触觉**: 多数灵巧手研究仅依赖视觉，忽略了触觉对可靠操作的关键作用

### Delta 分析
| 前人工作 | 限制 | HATO 突破 |
|---------|------|----------|
| ALOHA | 仅夹爪 | **多指手** |
| 单手系统 | 无双手协作 | **双手** |
| 视觉策略 | 无触觉 | **视触觉** |
| 复杂遥操作 | 昂贵/复杂 | **VR控制器** |
| 研究灵巧手 | 无触觉 | **义肢手改装** |

### 关键贡献点
1. **硬件改装**: 将 Psyonic Ability Hand（义肢）改装为研究用灵巧手
2. **VR 遥操作映射**: 简洁直观的 grip button → power grasp, thumbstick → thumb
3. **视触觉 Diffusion Policy**: 融合 RGB-D + 触觉 + 本体感觉
4. **关键发现**: 触觉对可靠完成任务至关重要

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 硬件系统

```
双臂系统:
├── 2× UR5e 机械臂 (6-DoF each)
├── 2× Psyonic Ability Hand (6-DoF each)
│   ├── 5 手指，每指 6 触觉传感器
│   └── 自定义 PCB 简化接线
├── 3× Intel RealSense (2 腕部 + 1 第三视角)
└── Meta Quest 2 VR (遥操作)
```

**触觉传感器布局**:
- 每指尖 6 个 FSR（Force-Sensing Resistor）
- 总计 60 个触觉通道（双手）
- 输出: 连续压力值

### 3.2 VR 遥操作映射

> [!important] 设计哲学
> 牺牲精细 finger-gaiting 能力，换取直观易用的操作体验。

```
Quest Controller → Robot Control:

1. 手臂控制:
   Controller Pose → IK → UR5e Joint Position
   
2. 手部控制:
   Grip Button (按压程度) → 四指屈曲角度
   Thumbstick (2D位置) → 拇指关节角度
   
3. Pause-and-Adjust:
   Trigger Button → 暂停/继续控制
```

### 3.3 Diffusion Policy 架构

**观测空间**:
```python
observation = {
    # 本体感觉
    'arm_joints': (12,),        # 2×6 DoF
    'hand_joints': (12,),       # 2×6 DoF
    'ee_pose': (14,),           # 2×7 (pos + quat)
    
    # 视觉
    'wrist_rgb': (2, 240, 320, 3),
    'wrist_depth': (2, 240, 320),
    'head_rgb': (240, 320, 3),
    'head_depth': (240, 320),
    
    # 触觉
    'touch': (60,),              # 2×30 FSR readings
}
```

**动作空间**:
```python
action = {
    'arm_joints': (12,),         # target joint positions
    'hand_joints': (12,),        # target finger positions
}
```

### 3.4 训练细节

**DDPM 扩散过程数学框架**：

前向扩散（加噪）：
$$
q(a_k | a_{k-1}) = \mathcal{N}(a_k; \sqrt{1-\beta_k}\, a_{k-1},\, \beta_k I)
$$

反向去噪（推理时生成动作）：
$$
p_\theta(a_{k-1} | a_k, o) = \mathcal{N}\!\bigl(a_{k-1};\, \mu_\theta(a_k, k, o),\, \sigma_k^2 I\bigr)
$$

训练损失（预测噪声 ε）：
$$
\mathcal{L} = \mathbb{E}_{a_0, \epsilon, k}\!\bigl[\|\epsilon - \epsilon_\theta(a_k, k, o)\|^2\bigr]
$$

其中 $o = [z_{\text{vis}}, z_{\text{proprio}}, z_{\text{tactile}}]$ 为多模态条件向量，$k \in \{1,\dots,K\}$ 为扩散步数。

- **策略**: Diffusion Policy (DDPM)，去噪步数 $K=100$（训练），DDIM $K=10$（推理加速）
- **数据量**: 30 分钟 ~ 2 小时遥操作数据（约 18k–72k timesteps @ 10Hz）
- **控制频率**: 10 Hz（动作 chunk 长度 16 步，即 1.6s 预测窗口）
- **数据归一化**: [-1, 1] 线性映射（各维度独立统计 min/max）
- **优化器**: AdamW，lr=1e-4，weight decay=1e-6
- **Batch size**: 256
- **训练轮数**: ~2000 epochs，early stopping on validation loss
- **视觉编码**: ResNet-18（ImageNet 预训练），输出 512-d per camera → concat → MLP → 128-d
- **触觉/本体编码**: MLP (60→128→128) / MLP (38→128→128)
- **调度器**: cosine beta schedule，$\beta_1=1\times10^{-4}$，$\beta_K=0.02$

## 4. 实验任务与验证 (Experiments)

### 四个挑战性任务

| 任务 | 描述 | 为什么需要多指手 |
|-----|------|----------------|
| **Slippery Handover** | 递送滑溜物体 | 多接触点防滑 |
| **Tower Block Stacking** | 堆叠积木塔 | 大接触面积稳定 |
| **Wine Pouring** | 倒酒 | 抓握大物体 + 质心变化 |
| **Steak Serving** | 上牛排（用工具） | 工具使用 + 双手协调 |

### 消融实验核心结果

| 配置 | MSE (×10⁻¹) |
|-----|-------------|
| 仅本体感觉 | **5.06** (差) |
| 无视觉 | 3.22 |
| 无触觉 | 1.93 |
| **完整** | **0.30** (最佳) |

> [!important] 关键发现
> **视觉和触觉都不可或缺！** 没有触觉或视觉，策略无法可靠成功。

### Ablation 因果链
- **去掉视觉** (0.30 → 3.22, ×10.7): 动作序列严重依赖物体位姿信息；无视觉时策略退化为开环本体感觉回放，无法适应微小的初始条件变化 → **视觉提供了闭环反馈的核心信号**
- **去掉触觉** (0.30 → 1.93, ×6.4): 接触力反馈缺失导致抓取力标定失败；Slippery Handover 任务中物体滑落频率显著上升，因为策略无法感知"即将滑脱"的瞬态信号 → **触觉提供了接触状态的唯一直接观测**
- **仅本体感觉** (0.30 → 5.06, ×16.9): 既无外部感知又无接触感知，策略完全基于关节角度历史做开环预测；Diffusion Policy 的条件向量 $o$ 信息量严重不足，去噪过程退化为近似随机采样

### 夹爪 vs 多指手

```
夹爪失败模式:
├── 小接触面积 → 物体滑落
├── 不稳定抓取点 → 摇晃
├── 缺乏支撑 → 无法平衡
└── 无冗余 → 容错差

多指手优势:
├── 大接触面积（平掌）
├── 多点抓取
├── 自然抓握（power grasp）
└── 适应不规则形状
```

## 4.5 工程关键细节 (Engineering Tricks)

- **义肢手改装关键**: Psyonic Ability Hand 原始通信协议为 CAN bus；改装自定义 PCB 将其转为 USB 串口通信，减少延迟 ~5ms
- **FSR 触觉传感器校准**: 每个 FSR 响应曲线非线性且个体差异大；需逐传感器采集"无负载-满负载"标定曲线做分段线性化
- **VR 遥操作漂移补偿**: Meta Quest 2 长时间使用存在坐标漂移；每次启动时执行原点校准，操作过程中通过 Pause-and-Adjust 机制重置
- **动作 chunk 与平滑**: 16 步 action chunk 直接执行会产生不连续；采用滑动窗口加权平均（指数衰减权重）平滑连续 chunk 的重叠区域
- **数据收集质量控制**: 设定成功率阈值，仅保留成功完成任务的 episode；操作者需 5-10 min 适应训练后开始正式数据收集

## 5. 批判性分析 (Critical Analysis)

### 优势
- **首次双多指视触觉**: 填补研究空白
- **低成本**: 使用现成 VR 设备 + 义肢手改装
- **数据高效**: 30分钟数据可训练有效策略
- **直观遥操作**: 5-10 分钟即可上手

### 局限性（理论/算法/工程三维度）

**理论层面**:
- VR 控制器仅 2-DoF 手部映射（grip + thumbstick），无法覆盖人手 20+ DoF 的手指独立运动空间 → 理论上不可能生成 finger-gaiting 数据
- Diffusion Policy 假设动作分布为连续且光滑的，但接触切换动力学本质是混合离散/连续系统，可能导致接触切换处的动作预测模糊

**算法层面**:
- 10 Hz 控制频率对高动态任务（转笔、抛接）不足，接触切换持续 ~10-50ms 远快于控制周期
- 行为克隆对分布外状态无恢复能力（无 RL 探索信号）
- **替代方案**: 结合 residual RL（BC 提供基础策略 + RL 学习残差校正），或采用 Action Chunking Transformer（ACT）的层级策略

**工程层面**:
- Psyonic Ability Hand 为义肢产品，力控精度和反向驱动性低于 LEAP Hand 等研究灵巧手
- FSR 触觉传感器精度低、易老化，长期使用需重新标定
- **替代方案**: DIGIT/GelSight 视触觉传感器提供更丰富的接触信息（法向力 + 切向力 + 几何），但集成复杂度更高

### 未来方向
- Data-glove 遥操作实现高自由度手指映射，采集精细操作数据
- DDIM 加速推理与更高频控制（50-100 Hz）结合
- 大规模多任务数据收集 + Foundation Policy 预训练
- 迁移学习到非义肢灵巧手（LEAP Hand、Allegro Hand）

## 6. 与知识体系的联系

### 与 [[RepresentationLearning]] 的联系

视触觉 Diffusion Policy 的 late fusion（各模态独立编码后 concat）对应多模态互信息分解：

$$
I(A;\, Z_{\text{vis}}, Z_{\text{tactile}}, Z_{\text{proprio}}) \geq I(A;\, Z_{\text{vis}}) + I(A;\, Z_{\text{tactile}} \mid Z_{\text{vis}})
$$

Ablation 证实去掉触觉后 MSE 增大 6.4 倍，说明条件互信息 $I(A;\, Z_{\text{tactile}} \mid Z_{\text{vis}})$ 不可忽略。视觉遮挡时（手掌包裹物体），触觉成为唯一的接触状态观测源（详见 [[RepresentationLearning#5. Multimodal Fusion & Tactile Intelligence: 触觉与视觉的交响 (Symphony of Vision and Touch in Multimodal Fusion)]]）。

### 与 [[StochasticProcess]] 的联系

DDPM 反向过程的 score function $\nabla_{a_k} \log p(a_k \mid o)$ 被 $\epsilon_\theta$ 网络参数化。条件向量 $o$ 的信息量直接影响 score 估计质量：

$$
\text{SNR}(k) = \frac{\bar{\alpha}_k}{1 - \bar{\alpha}_k}, \quad \bar{\alpha}_k = \prod_{i=1}^{k}(1-\beta_i)
$$

低扩散步数（$k$ 小）处 SNR 高，动作细节由条件 $o$ 精确指导；高步数处 SNR 低，动作分布的全局结构由先验决定。这解释了为什么触觉（提供精确接触时刻信息）在 fine action 层面影响显著。

### 与 [[ContactMechanics]] 的联系

60 通道 FSR 阵列的触觉观测可类比为离散化的接触压力分布 $p(x,y)$。在 power grasp 模式下，稳定抓取要求合力/合力矩满足摩擦锥约束。触觉信号间接编码了力封闭（force closure）条件是否满足。

### 对灵巧手转笔 / Sim-to-Real 的启发

> [!warning] 高度相关
> 1. **遥操作数据收集**: HATO 的 VR 映射思路可迁移至转笔数据收集——用 data-glove 替代 VR 控制器，提供更高自由度的手指映射
> 2. **触觉对转笔的价值**: 转笔中笔在手指间滚动/滑动的过程正好需要接触检测；HATO 证明简单 FSR 即可提供关键信号
> 3. **Sim-to-Real 关键瓶颈**: HATO 未做 Sim-to-Real（纯 real-world IL），但其 Diffusion Policy 架构可迁移至仿真训练 → 真实部署流程；关键在于触觉传感器的仿真建模
> 4. **双手操作启示**: 转笔可拓展至双手配合（一手转、另一手接），HATO 的双手协调框架是直接参考

## 7. 演进脉络定位 (Evolution Context)

```
前置工作:
├── ALOHA (2023): 低成本双臂遥操作（夹爪）
├── Robot Synesthesia: 视触觉点云融合（单手）
└── Diffusion Policy (2023): 行为克隆 SOTA

本论文: HATO
├── 双多指手硬件系统
├── VR 遥操作映射
├── 视触觉 Diffusion Policy
└── 触觉重要性验证

后续影响:
├── 大规模双手数据收集
├── 更复杂双手任务
└── 研究用灵巧手开源
```

## 8. 技术要点总结

### 遥操作系统设计

```python
# 核心映射逻辑
def teleop_mapping(quest_controller):
    # 手臂：位姿直接映射
    ee_target = transform_to_robot_frame(quest_controller.pose)
    arm_joints = IK_solve(ee_target)
    
    # 手部：按钮映射
    grip_value = quest_controller.grip_button  # [0, 1]
    finger_joints[:4] = grip_value * joint_limits[:4]  # 四指
    
    thumb_xy = quest_controller.thumbstick  # [-1, 1]²
    finger_joints[4:6] = map_thumb(thumb_xy)  # 拇指
    
    return arm_joints, finger_joints
```

### Diffusion Policy 要点

```python
# 观测编码
visual_feat = CNN(concat([wrist_imgs, head_img]))
proprio_feat = MLP(concat([arm_joints, hand_joints, ee_pose]))
tactile_feat = MLP(touch_readings)

# 融合
condition = concat([visual_feat, proprio_feat, tactile_feat])

# 扩散生成动作
action = diffusion_sample(condition)
```

## 9. 与相关工作的对比

| 方面 | ALOHA | DexPilot | HATO |
|-----|-------|----------|------|
| 末端执行器 | 夹爪 | 灵巧手 | 多指手 |
| 手臂数 | 2 | 1 | 2 |
| 触觉 | ❌ | ❌ | ✅ |
| 遥操作 | 教导臂 | 外骨骼 | VR控制器 |
| 成本 | 低 | 高 | 中 |
| 数据需求 | 中 | 中 | 低 |
