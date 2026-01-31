---
name: embodied-ai-resources
description: 具身智能（Embodied AI）领域的资源追踪与知识维护指南。包含 VLA 模型、仿真器、数据集、社区资源的持续更新策略。用于保持 EmbodiedAI.md Foundation 文件的时效性。
---

# Embodied AI Resources Tracking Skill

# 具身智能资源追踪技能

---

## 1. 核心追踪目标

本技能用于维护 [[EmbodiedAI]] Foundation 文件的时效性，重点追踪以下快速演进的领域：

### 1.1 VLA 模型演进

```
追踪优先级:
├── 🔴 高优先级 (月度更新)
│   ├── Google (RT 系列)
│   ├── Physical Intelligence (π 系列)
│   ├── Stanford / UC Berkeley 开源工作
│   └── 清华/北大/港大国内顶尖组
├── 🟡 中优先级 (季度更新)
│   ├── OpenVLA 生态
│   ├── Diffusion Policy 变体
│   └── 分层 VLA 架构
└── 🟢 低优先级 (半年更新)
    └── 垂直领域 VLA (医疗/UAV/驾驶)
```

**关键指标**:
- 参数量变化趋势
- 开源状态
- Benchmark 性能
- Sim-to-Real 成功率

### 1.2 仿真器生态

| 仿真器 | 追踪频率 | 关注点 |
|--------|----------|--------|
| **Isaac Lab** | 月度 | 新功能、API变更、官方教程 |
| **MuJoCo Playground** | 季度 | MJX 性能、新环境 |
| **Genesis** | 月度 | 快速迭代期，关注新特性 |
| **SAPIEN** | 季度 | RoboTwin 生态 |

### 1.3 数据集与 Benchmark

```
追踪项目:
├── Open X-Embodiment 扩展
├── DROID 更新
├── RH20T 中文数据集
├── 新兴 Benchmark (如 SIMPLER)
└── 真机数据集发布
```

---

## 2. 信息源优先级

### Tier 1: 官方权威源 (每周检查)

| 来源 | 类型 | URL |
|------|------|-----|
| **Embodied-AI-Guide** | GitHub | github.com/TianxingChen/Embodied-AI-Guide |
| **LeRobot** | HuggingFace | huggingface.co/lerobot |
| **Isaac Lab Docs** | 官方文档 | isaac-sim.github.io/IsaacLab |
| **Simulately Wiki** | 社区Wiki | simulately.wiki |

### Tier 2: 社区与论坛 (每两周检查)

| 来源 | 平台 | 价值 |
|------|------|------|
| **Lumina 社区** | Website | lumina-embodied.ai |
| **石麻日记** | 公众号 | 深度技术分析 |
| **机器之心/新智元** | 公众号 | 行业动态 |
| **Twitter/X** | @simulately12492 | 实时更新 |

### Tier 3: 学术源 (会议前集中检查)

```
重点会议时间线:
├── CoRL (11月)      - 机器人学习顶会
├── RSS (7月)        - 机器人顶会
├── ICRA (5月)       - 机器人大会议
├── NeurIPS (12月)   - AI顶会机器人track
├── CVPR (6月)       - 视觉+机器人
└── ICLR (5月)       - 学习方法
```

---

## 3. 更新工作流

### 3.1 定期维护检查清单

```markdown
## 月度维护 Checklist

### VLA 模型
- [ ] 检查 OpenVLA/π₀ 是否有新版本
- [ ] 扫描 arXiv robotics 最近30天
- [ ] 更新 EmbodiedAI.md 模型表格

### 仿真器
- [ ] 检查 Isaac Lab release notes
- [ ] 检查 Genesis 更新
- [ ] 更新版本号和新特性

### 社区资源
- [ ] Embodied-AI-Guide 新增内容
- [ ] 新增重要 Awesome 列表

### Foundation 关联
- [ ] 检查是否有新概念需链接到其他 Foundation
- [ ] 验证现有 wikilinks 有效性
```

### 3.2 新内容融合流程

```
新 VLA 模型/方法发布
        │
        ▼
┌─────────────────────────────────────┐
│  Step 1: 分类判断                    │
│  ─────────────────────────────────  │
│  • 全新架构范式 → 新增章节           │
│  • 现有范式改进 → 补充到对应小节     │
│  • 工程优化 → Implementation 更新    │
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 2: 关联检查                    │
│  ─────────────────────────────────  │
│  • 是否涉及新的 Foundation 概念？    │
│  • 是否需要更新 taxonomy.md？        │
│  • 是否有对应论文需创建 PapersRecap？│
└─────────────────────────────────────┘
        │
        ▼
┌─────────────────────────────────────┐
│  Step 3: 执行更新                    │
│  ─────────────────────────────────  │
│  • 更新 EmbodiedAI.md               │
│  • 添加 wikilinks                    │
│  • 更新 Evolution 时间线             │
└─────────────────────────────────────┘
```

---

## 4. 关键资源索引

### 4.1 核心 GitHub 仓库

```
VLA & Robot Learning:
├── openvla/openvla                    # OpenVLA 官方
├── Physical-Intelligence/openpi       # π₀ 开源实现
├── huggingface/lerobot               # HuggingFace 机器人库
├── robotwin-Platform/robotwin        # RoboTwin 2.0
├── ARISE-Initiative/robosuite        # Robosuite
└── google-deepmind/mujoco_playground # MuJoCo Playground

Simulators:
├── isaac-sim/IsaacLab                # NVIDIA Isaac Lab
├── google-deepmind/mujoco            # MuJoCo
├── haosulab/SAPIEN                   # SAPIEN
└── Genesis-Embodied-AI/Genesis       # Genesis

Paper Lists:
├── TianxingChen/Embodied-AI-Guide    # 本技能的主要参考
├── YanjieZe/awesome-humanoid-robot-learning
├── GT-RIPL/Awesome-LLM-Robotics
└── geng-haoran/Simulately            # 仿真器百科
```

### 4.2 关键论文追踪

以下论文代表各方向的里程碑，其后续工作值得密切关注：

| 方向 | 里程碑论文 | 关注后续 |
|------|-----------|----------|
| VLA 起源 | RT-1, RT-2 | Google Robotics 新工作 |
| 开源 VLA | OpenVLA | Stanford/Berkeley 新工作 |
| 扩散策略 | Diffusion Policy | π₀, RDT 系列 |
| 3D 感知 | 3D-VLA | 点云/NeRF + VLA |
| Sim-to-Real | Domain Randomization | 系统识别、Teacher-Student |

### 4.3 学习路径资源

```
入门路径 (1-2周):
├── RoboTwin 2.0 官方教程
├── Isaac Lab Getting Started
└── LeRobot 文档

进阶路径 (1-2月):
├── 西湖大学赵世钰 RL 课程
├── UC Berkeley CS285
├── Diffusion Policy 论文 + 代码
└── OpenVLA 源码阅读

研究路径:
├── 阅读 CoRL/RSS/ICRA 最佳论文
├── 复现 1-2 个经典工作
└── 在 Isaac Lab 中设计新任务
```

---

## 5. 与其他 Skills 的协作

### 5.1 knowledge-graph-management

```
协作点:
├── 遵循统一的 Foundation 输出格式
├── 使用标准的 wikilink 规范
├── 参与每次会话的健康检查
└── 更新 taxonomy.md 时保持一致性
```

### 5.2 obsidian-markdown

```
格式规范:
├── 使用 Obsidian callout 语法 (> [!note], > [!tip])
├── 表格对齐
├── 代码块语言标注
└── Mermaid 图表 (如需)
```

---

## 6. 快速参考卡片

### VLA 模型速查

```
┌────────────────────────────────────────────────────────────┐
│                    VLA Model Quick Reference                │
├────────────────────────────────────────────────────────────┤
│ Model       │ Params │ Action │ Open? │ Key Innovation     │
├─────────────┼────────┼────────┼───────┼────────────────────┤
│ RT-1        │ 35M    │ Token  │ ❌    │ 开创性工作          │
│ RT-2        │ 55B    │ Token  │ ❌    │ VLM直接输出动作     │
│ OpenVLA     │ 7B     │ Token  │ ✅    │ Prismatic backbone  │
│ π₀          │ 3.3B   │ Flow   │ ✅    │ Flow Matching       │
│ Octo        │ 93M    │ Diff   │ ✅    │ 泛化能力            │
│ RDT-1B      │ 1.2B   │ Diff   │ ✅    │ 双臂操作            │
└─────────────┴────────┴────────┴───────┴────────────────────┘
```

### 仿真器速查

```
┌────────────────────────────────────────────────────────────┐
│               Simulator Quick Reference                     │
├────────────────────────────────────────────────────────────┤
│ Simulator   │ Engine  │ GPU? │ Best For                    │
├─────────────┼─────────┼──────┼─────────────────────────────┤
│ Isaac Lab   │ PhysX 5 │ ✅   │ 大规模并行 RL               │
│ MuJoCo      │ 自研    │ MJX  │ 精细操作、Benchmark         │
│ SAPIEN      │ PhysX   │ ✅   │ 快速原型、RoboTwin          │
│ Genesis     │ 多后端  │ ✅   │ 4300万FPS、可微             │
│ PyBullet    │ Bullet  │ ❌   │ 教学入门                    │
└─────────────┴─────────┴──────┴─────────────────────────────┘
```

---

## Changelog

| 日期 | 更新内容 |
|------|----------|
| 2026-02-02 | 初始创建，基于 lumina-eai-guide.pdf 内容萃取 |
