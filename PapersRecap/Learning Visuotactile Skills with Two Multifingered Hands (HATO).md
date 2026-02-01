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
related:
  - "[[ReinforcementLearning]]"
  - "[[RepresentationLearning]]"
  - "[[SignalProcessing]]"
  - "[[ContactMechanics]]"
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

- **策略**: Diffusion Policy (DDPM)
- **数据量**: 30 分钟 ~ 2 小时遥操作数据
- **控制频率**: 10 Hz
- **数据归一化**: [-1, 1] 线性映射

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

## 5. 批判性分析 (Critical Analysis)

### 优势
- **首次双多指视触觉**: 填补研究空白
- **低成本**: 使用现成 VR 设备 + 义肢手改装
- **数据高效**: 30分钟数据可训练有效策略
- **直观遥操作**: 5-10 分钟即可上手

### 局限性
- 无 finger-gaiting 能力（遥操作映射限制）
- 仅 power grasp，无精细操作
- 控制频率较低（10 Hz）
- 义肢手的研究可用性有限

### 未来方向
- 更精细的手指控制映射
- 更高采样率触觉
- 大规模数据收集
- 迁移学习到其他手

## 6. 对灵巧操作的启发 (Implications)

1. **触觉不是可选项**: 对于可靠操作，触觉至关重要
2. **义肢手的潜力**: 成熟的义肢技术可服务研究
3. **简洁映射**: 简单的遥操作映射足以收集有效数据
4. **腕部相机**: 腕部视角比第三视角更有效

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
