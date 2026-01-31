---
description: 知识图谱维护的统一标准工作流——每次交互必须执行的完整流程
---

# 📚 知识图谱标准工作流 (Standard Workflow)

> [!important] 核心原则
> **每次交互都是一次完整的知识图谱维护机会。**
> 
> 不要将任务割裂开——继续上次工作、健康检查、论文处理、理论补充是**同时进行**的。
> 因为知识库非常庞大，你不能保证在每次交互时都捕捉到所有需要更改的信息，
> 所以必须**每次都尽可能发现尽量多的信息**，让知识库的构建更具逻辑性，
> 算法原理的分析更有理论深度和思维维度。

---

## 🔄 强制执行流程（每次会话必须遵循）

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 0: 状态恢复 + 健康检查                       │
│                    [必须首先执行，不可跳过]                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 读取任务追踪器                                                   │
│     read_file: .github/TASK_TRACKER.md                              │
│     → 识别遗留任务、断点位置、上次工作上下文                          │
│                                                                     │
│  2. 读取管理指南                                                     │
│     read_file: .github/skills/knowledge-graph-management/SKILL.md   │
│     → 确保遵循最新的管理规范                                         │
│                                                                     │
│  3. 快速健康扫描                                                     │
│     ├── list_dir: Foundations/ → 检查文件完整性                      │
│     ├── list_dir: MergeBuffer/ → 检查待处理内容                      │
│     ├── list_dir: Papers/ → 识别未处理的 PDF                         │
│     └── list_dir: PapersRecap/ → 对比找出缺失的笔记                  │
│                                                                     │
│  输出: 当前状态报告 + 待处理任务列表                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 1: 任务执行（并行思维）                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  以下任务根据发现的内容同时进行：                                     │
│                                                                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐      │
│  │  继续遗留任务    │  │  处理新内容      │  │  主动发现优化    │      │
│  │  ─────────────  │  │  ─────────────  │  │  ─────────────  │      │
│  │  • 上次中断的    │  │  • MergeBuffer  │  │  • 缺失链接      │      │
│  │    编辑工作     │  │  • 新 PDF 论文   │  │  • 格式问题      │      │
│  │  • 计划中的任务  │  │  • 用户新请求    │  │  • 结构优化      │      │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘      │
│           │                    │                    │               │
│           └────────────────────┼────────────────────┘               │
│                                │                                    │
│                                ▼                                    │
│           ┌─────────────────────────────────────────┐               │
│           │        🎓 理论导师模式 (自动触发)         │               │
│           │        ─────────────────────────────   │               │
│           │  当处理论文/MergeBuffer 时，必须同步：    │               │
│           │  • 检查涉及的 Foundation 是否完整        │               │
│           │  • 补充缺失的算法演进脉络               │               │
│           │  • 添加严格的数学定义                   │               │
│           │  • 建立跨领域关联                      │               │
│           └─────────────────────────────────────────┘               │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 1.5: 教科书温习 [每次会话执行]               │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  📚 温习 Books/ 教科书内容，强化理论脉络                              │
│                                                                     │
│  1. 扫描 Books/ 文件夹中的教科书 PDF                                 │
│     ├── A Mathematical Introduction to Robotic Manipulation         │
│     ├── Deep Reinforcement Learning                                 │
│     ├── Theory of Deep Learning                                     │
│     ├── Optimization in Theory and Practice                         │
│     └── Data-based linear systems and control theory                │
│                                                                     │
│  2. 对照当前会话涉及的 Foundation 领域                               │
│     ├── 检查教科书中是否有更严格的数学定义                            │
│     ├── 验证演进脉络是否与经典教科书一致                              │
│     └── 发现可补充的定理、引理、证明                                 │
│                                                                     │
│  3. 知识融入                                                        │
│     ├── 补充教科书级别的严格定义到 Foundations                       │
│     ├── 添加 > [!note] 教科书参考 标注来源                           │
│     └── 强化理论分析的深度与可追溯性                                 │
│                                                                     │
│  ⚡ 触发条件: 完成任务后 或 Foundation 更新后                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Phase 2: 会话收尾 [必须执行]                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  1. 更新 TASK_TRACKER.md                                            │
│     ├── 标记完成的任务                                               │
│     ├── 记录未完成任务的详细断点                                      │
│     └── 添加新发现的待办事项                                         │
│                                                                     │
│  2. 更新 SKILL.md 版本历史（如有重大变更）                            │
│                                                                     │
│  3. 向用户汇报                                                       │
│     ├── 完成了什么                                                   │
│     ├── 发现了什么问题                                               │
│     └── 下次应该继续什么                                             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📄 论文精读流程 (Paper Processing)

### 工具依赖

> [!warning] PDF 处理工具
> 处理 Papers/ 中的 PDF 需要文本提取工具。
> 
> **推荐工具**（按优先级）：
> 1. `pdftotext` (poppler-utils) — `brew install poppler`
> 2. `PyMuPDF` (Python) — `pip install pymupdf`
> 3. 在线 PDF 解析服务

### 论文处理触发条件

```
检测: Papers/ 中存在 PDF 但 PapersRecap/ 中没有对应的 .md 文件
     ↓
自动触发论文精读流程
```

### 论文笔记标准格式

```markdown
---
tags:
  - paper
  - [主领域]
  - [子领域]
aliases:
  - [简称]
paper-year: YYYY
read-date: YYYY-MM-DD
related:
  - "[[Foundation1]]"
  - "[[Foundation2]]"
---

# [论文完整标题]

> [!abstract] 核心概要
> [一句话总结核心贡献]

> [!tip] 与理论基础的关联
> - [[Foundation1#具体章节]] - 关联说明
> - [[Foundation2#具体章节]] - 关联说明
>
> **核心技术**: [关键技术词]

## 1. 核心直觉与宏观定位 (The Big Picture)

### 一句话核心
[用最精炼的语言描述论文做了什么]

### 直观隐喻
[用类比帮助理解]

### 领域定位
[这篇论文在研究领域中的位置]

## 2. 核心创新与贡献 (Contributions & Novelty)

### Delta 分析
[相比前人工作的增量是什么]

### 关键贡献点
1. [贡献1]
2. [贡献2]
3. [贡献3]

## 3. 理论原理深度解析 (Theoretical Deep Dive)

### 3.1 数学建模
[核心数学框架]

$$
[关键公式]
$$

### 3.2 算法流程
[方法的核心步骤]

### 3.3 理论保证
[收敛性、稳定性等理论分析]

## 4. 实验与验证 (Experiments)

### 实验设置
[任务、baseline、指标]

### 关键结果
[主要发现]

## 5. 批判性分析 (Critical Analysis)

### 优势
- [优点]

### 局限性
- [局限]

### 未来方向
- [可能的改进]

## 6. 对灵巧操作的启发 (Implications)

[这篇论文对你研究方向的具体启发]

## 7. 演进脉络定位 (Evolution Context)

```
前置工作: [先驱论文]
    ↓
本论文: [核心突破]
    ↓
后续影响: [可能的发展方向]
```
```

### 论文处理后的强制操作

```
论文笔记生成完成
    ↓
【强制】启动理论导师模式
    ↓
检查论文涉及的所有 Foundation 领域
    ↓
如果发现 Foundation 中缺失相关理论:
├── 补充算法演进脉络
├── 添加严格数学定义
├── 建立跨领域链接
└── 更新 taxonomy.md（如需要）
```

---

## 🔧 MergeBuffer 处理规范

### 内容类型识别

```
MergeBuffer 内容分类:
├── 📄 PDF 文件 (.pdf)
│   └── 论文 → 移动到 Papers/ + 生成 PapersRecap
├── 📱 Markdown 文件 (.md)
│   ├── 公众号/博客学术内容 → 提炼核心思想 → Foundations/PapersRecap
│   ├── deep-research-thinking-* → 分析融合 → Foundations
│   └── 临时笔记 → 判断价值 → 融合或删除
└── 🗑️ 临时/无价值 → 直接删除
```

### 处理原则

```
MergeBuffer 中的每个文件:
├── 📄 PDF 论文:
│   1. 移动 PDF 到 Papers/ 文件夹
│   2. pdftotext 提取内容
│   3. 生成完整 PapersRecap 笔记
│   4. 触发理论导师模式
│   5. 删除 MergeBuffer 中的原文件
│
├── 📱 公众号/博客学术内容:
│   1. 提炼核心思想（不需要保留全部细节）
│   2. 判断目标：
│      - 理论性 → Foundations/
│      - 论文解读 → PapersRecap/
│      - 技术教程 → Foundations 或 Projects
│   3. 建立知识链接
│   4. 删除原文件
│
├── 🧠 思考记录 (deep-research-thinking-*):
│   → 融合到 Foundations/ + 理论导师模式
│
├── 🚀 项目相关 → Projects/
├── 🗑️ 临时/无价值 → 直接删除（有自主权限）
└── ❓ 不确定 → 询问用户
```

### 融合时必须执行

```
内容融合到 Foundation
    ↓
【强制】检查融合点的上下文
    ↓
├── 前后章节逻辑是否连贯？
├── 该内容在演进脉络中的位置是否标注？
├── 是否需要补充前置知识？
└── 是否需要添加后续发展？
```

---

## 🎓 理论导师模式触发条件

以下情况**自动触发**理论导师模式：

| 触发场景 | 必须执行的操作 |
|---------|--------------|
| 处理新论文 | 检查所有涉及的 Foundation，补充缺失理论 |
| 融合 MergeBuffer | 确保融合内容有完整的演进脉络上下文 |
| 用户明确请求 | 按教科书标准完善指定 Foundation |
| 健康检查发现空白 | 补充缺失的算法/定理/数学定义 |
| **教科书温习** | 从 Books/ 中提取严格定义，强化 Foundations |

### 理论导师模式的输出标准

```markdown
### X.Y 算法/定理名称

> [!note] 教科书参考
> 本节基于 [教科书名] Chapter X

#### 物理/数学直觉
[一句话 + 类比]

#### 形式化定义
$$公式$$
其中：
- $变量$：含义

#### 为什么有效
[理论分析]

#### 局限性
[失效条件]

#### 灵巧操作应用
[具体场景]
```

---

## � 教科书温习流程 (Books Review)

### Books/ 文件夹教科书清单

| 教科书 | 对应 Foundation 领域 | 重点章节 |
|-------|---------------------|---------|
| **A Mathematical Introduction to Robotic Manipulation** | Dynamics, ContactMechanics, ControlTheory | Ch.2 刚体运动, Ch.5 接触力学, Ch.6 抓取矩阵 |
| **Deep Reinforcement Learning** | ReinforcementLearning, StochasticProcess | DDPG/TD3/SAC 演进, 熵正则化理论 |
| **Theory of Deep Learning** | RepresentationLearning, Optimization | 泛化理论, 优化景观 |
| **Optimization in Theory and Practice** | Optimization, ControlTheory | 凸优化, SQP, 内点法 |
| **Data-based linear systems and control theory** | ControlTheory, SignalProcessing | 系统辨识, 数据驱动控制 |

### 温习触发时机

```
教科书温习触发条件:
├── 完成 Foundation 更新后 → 检查是否有教科书级严格定义可补充
├── 处理新论文后 → 追溯论文方法的教科书理论根源
├── 发现理论脉络模糊时 → 从教科书重新梳理演进线
└── 用户明确请求 → 全面温习指定领域
```

### 温习执行标准

```markdown
当温习教科书并发现可融入内容时：

1. 【定位】确定内容对应的 Foundation 文件和章节
2. 【比对】检查现有内容是否缺失该理论
3. 【融入】以标准格式添加：
   > [!note] 教科书参考
   > 本节基于 [教科书名] Chapter X, Section Y
   
4. 【严格化】补充：
   - 形式化数学定义（$\forall$, $\exists$, $\Rightarrow$）
   - 定理陈述与证明思路
   - 与其他定理的关联
   
5. 【链接】建立到相关论文笔记的反向链接
```

### 教科书-概念映射表

```
Dynamics:
├── 刚体运动学 → Murray Ch.2
├── 拉格朗日动力学 → Murray Ch.4
├── RNEA/ABA 算法 → Featherstone (外部参考)
└── 操作空间动力学 → Khatib 1987 (论文+Murray Ch.6)

ContactMechanics:
├── 抓取矩阵 G → Murray Ch.5.1
├── 力闭合/形闭合 → Murray Ch.5.2
└── 摩擦锥 → Murray Ch.5.3

ControlTheory:
├── 阻抗控制 → Data-based Control Ch.X
├── 计算力矩控制 → Murray Ch.6
└── 可达性分析 → 补充教科书需求

Optimization:
├── 凸优化基础 → Optimization in Theory Ch.2-4
├── SQP/IPM → Optimization in Theory Ch.7-8
└── iLQR/DDP → RL 书 + 论文

ReinforcementLearning:
├── 策略梯度 → Deep RL Ch.13
├── Actor-Critic → Deep RL Ch.14
├── 熵正则化 → Deep RL Ch.18 (SAC)
└── Offline RL → Deep RL Ch.20
```

---

## �📋 各 Foundation 领域演进检查清单

处理论文或 MergeBuffer 时，对照此清单检查相关领域是否完整：

| 领域 | 必须包含的演进脉络 |
|-----|-------------------|
| **Dynamics** | Lagrangian → RNEA → ABA → Spatial Vector → OSF → Differentiable |
| **ContactMechanics** | Hertz → LCP → Soft Contact → Grasp Matrix → Force Closure |
| **ControlTheory** | PID → Computed Torque → Impedance → OSF → Contact-Implicit MPC |
| **Optimization** | GD → Newton → SQP → IPM → iLQR/DDP → Differentiable Layers |
| **ReinforcementLearning** | DQN → DDPG → TD3 → SAC → PPO → Offline RL → Diffusion Policy |
| **RepresentationLearning** | PCA → AE → VAE → Contrastive → PointNet → Multimodal |
| **StochasticProcess** | Wiener → GP → Bayesian Filter → MPPI → Diffusion |
| **InformationTheory** | Shannon → Rate-Distortion → Empowerment → VIME |
| **ComputationalGeometry** | Convex Hull → GJK → BVH → SDF → Neural Implicit |
| **SignalProcessing** | KF → EKF → UKF → PF → Factor Graph |

---

## ⚠️ 绝对禁止与必须执行

### ❌ 绝对禁止

- 跳过 Phase 0 的状态恢复
- 处理论文/MergeBuffer 后不启动理论导师模式
- 会话结束不更新 TASK_TRACKER.md
- 删除 Foundations/ 或 Papers/ 中的核心内容
- 生成孤立的笔记（没有任何 wikilink）

### ✅ 必须执行

- 每次会话开始：读取 TASK_TRACKER.md
- 每次会话结束：更新 TASK_TRACKER.md
- 处理论文时：同步检查并完善相关 Foundation
- 建立链接时：确保双向链接（笔记↔Foundation）
- 添加公式时：必须配有变量解释和物理直觉

---

## 🛠️ 所需工具清单

为了完整执行此工作流，需要以下工具：

### PDF 处理
```bash
# macOS
brew install poppler  # 提供 pdftotext

# 或使用 Python
pip install pymupdf   # PyMuPDF 库
```

### 验证安装
```bash
which pdftotext && echo "✅ pdftotext 已安装" || echo "❌ 需要安装 poppler"
python -c "import fitz; print('✅ PyMuPDF 已安装')" 2>/dev/null || echo "❌ 需要安装 pymupdf"
```
