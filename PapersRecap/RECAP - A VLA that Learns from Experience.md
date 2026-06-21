---
tags:
  - paper
  - reinforcement-learning
  - vla
aliases:
  - π*0.6
  - RECAP
  - pi-star-0.6
paper-year: 2025
read-date: 2026-03-25
venue: Physical Intelligence Blog
paper-pdf: "[[Papers/A VLA that Learns from Experience.pdf]]"
related:
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[RepresentationLearning]]"
---

# π*0.6: A VLA that Learns from Experience (RECAP)

> [!abstract] 核心贡献
> 提出 RECAP（RL with Experience & Corrections via Advantage-conditioned Policies）— 三阶段训练流程（示范 → 纠正辅导 → 自主练习强化），将 VLA 从"模仿偶尔成功"推至"持续可靠运行"。在真实世界咖啡制作、折叠衣物、装配包装盒等任务上，throughput 翻倍、失败率降半，实现全天无中断运行。

> [!tip] 与理论基础的关联
> - [[ReinforcementLearning]] — Advantage-conditioned policy 是 Offline RL 在 VLA 的延伸；IL→RL 飞轮
> - [[EmbodiedAI]] — VLA post-training 的第三条路径（IL → RL with Experience）
> - [[RepresentationLearning]] — π0 系列 flow-matching 扩散策略基座
>
> **核心技术**: RECAP 三阶段 (Demo→Correction→RL), Advantage-Conditioned Policy, VLA 数据飞轮

## 1. 问题设定与动机

### 1.1 核心洞察（一句话 + 直观隐喻）
**一句话**：VLA 纯模仿学习的误差累积是 closed-loop 控制的固有缺陷，需要通过自主练习（RL）+ 人类纠正（Corrections）的双轨信号才能跨越从"有时成功"到"始终可靠"的鸿沟。

**隐喻**：学装箱 = (1) 老师示范基础技巧（IL），(2) 老师在你犯错时纠正（Corrections），(3) 自己反复练习直到熟练（Online RL）

### 1.2 现有方法的局限
- **纯 IL 天花板**：VLA 在模仿学习后能偶尔成功，但无法做到始终可靠——误差累积是 closed-loop 系统（非 LLM 这种静态输出）的固有问题
- **纠正数据稀缺**：人工纠正（Corrections）提供高质量信号但成本高，难以覆盖所有失败模式
- **RL 训练信号获取**：从"失败的自主经验"中提取有效训练信号（而非复制错误）是核心难题

## 2. 核心方法/理论

### 2.0 变量来源追踪

枢纽：**advantage $A(s,a)$ 作为策略的条件输入**——$A>0$ 复制、$A<0$ 避免，从失败经验学"避免"而非"复制错误"；Corrections 直接当高优势样本。

| 变量 | 类型/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|------|-----------|----------|------------|----------------|----------|
| $\pi$ | VLA (π0.6) | flow-matching 扩散 | 是 | 策略 | 三阶段共享基座 |
| Demo 数据 | 轨迹 | 人类遥操作 (Stage 1) | 否 | IL 监督 | 打底、天花板有限 |
| Corrections | 轨迹 | 人类介入纠正 (Stage 2) | 否 | 高质量纠正 | **当高优势 $A>0$ 样本注入** |
| 自主 rollout | 轨迹 | VLA 自主 (Stage 3) | 否 | 成败经验 | 含失败——靠 $A$ 筛选 |
| $A(s,a)$ | scalar | 优势估计 | 否（条件输入） | 行为好坏判据 | **稀疏奖励下估计不可靠**（§5） |
| advantage 条件化 | 离散/归一 | 构造 | — | $A$ 作策略额外输入 | $A>0$ 复制/$A<0$ 避免 |

### 2.1 关键创新点（Delta 分析）
相比前代 π0/π0.5（纯 IL VLA）：
1. **RECAP 三阶段框架**：统一了 Demonstrations + Corrections + Autonomous RL
2. **Advantage-Conditioned Policy**：利用优势函数区分自主经验中的好坏行为，避免从失败中学到错误
3. **工业级可靠性验证**：真实工厂环境全天运行（制作浓缩咖啡 5:30am-11:30pm、折叠 50 件衣物、装配 59 个包装盒）

### 2.2 数学框架
RECAP 的核心是 **Advantage-conditioned Policy**：
- 从自主 Rollout 中收集 episode 数据
- 计算每个 transition 的优势 $A(s, a)$
- 将 $A$ 作为条件输入策略网络，训练策略在 $A > 0$ 时复制该行为、$A < 0$ 时避免该行为
- Corrections 数据直接当作高优势样本加入训练

### 2.3 三阶段训练流程
1. **Stage 1 — Demonstrations (IL)**：人类遥操作收集示范数据 $\to$ 监督学习预训练 VLA
2. **Stage 2 — Corrections (Coaching)**：VLA 自主运行中人类介入纠正错误 $\to$ 纠正轨迹作为高优势标注加入训练
3. **Stage 3 — Autonomous RL (Practice)**：VLA 完全自主运行，通过成败结果信号 + Advantage 筛选进行 Self-Improvement

### 2.4 概念边界与符号陷阱

- **advantage-conditioned**：$A>0$ 复制、$A<0$ 避免——从失败学"避免"，不复制错误（核心机制）。
- **Corrections = 高优势样本**：人类纠正直接当 $A>0$ 注入，不需单独 reward。
- **三阶段角色**：Demo(IL 打底) → Corrections(coaching) → RL(practice 突破)。
- **advantage 估计稀疏奖励下不可靠**（§5 理论局限）。
- **per-task fine-tuning**：未验证跨任务/embodiment 泛化。
- **自动复位 + 安全约束**是真实长时自主 RL 的工程瓶颈。

## 3. 训练与实验细节

### 3.1 训练设定
- **基座模型**：π0.6 VLA（基于 π0 系列 flow-matching 扩散策略）
- **任务列表**：
  - 制作浓缩咖啡（多种饮品）
  - 折叠各类衣物（50 种未见过的衣物）
  - 装配/贴标签包装盒（真实巧克力工厂）
- **训练数据**：IL 示范 + 人类纠正 + 自主经验的混合
- **部署环境**：真实世界无中断长时间运行

### 3.2 核心实验结果
| 指标 | IL-only (π0.6) | + RECAP (π*0.6) |
|------|----------------|-----------------|
| Throughput | 基线 | 2x+ 提升 |
| 失败率 | 基线 | 降低 2x+ |
| 持续运行 | 短时间 | 全天连续 |

- 咖啡任务：5:30am - 11:30pm 全天不间断
- 衣物折叠：50 件全新衣物，新环境中连续数小时
- 包装盒装配：真实工厂 59 个盒子

### 3.3 Ablation Study 解读
- **仅 IL（无 Corrections/RL）**：能力天花板明显——偶尔成功但无法可靠
  - 因果链：纯模仿 $\to$ 无法覆盖实际运行中的误差状态 $\to$ 误差累积 $\to$ 不可靠
- **IL + Corrections（无 RL）**：显著提升但人力成本高、覆盖不全
- **IL + RL（无 Corrections）**：探索效率较低，但最终能收敛
- **三阶段 RECAP**：最优性能 — Corrections 提供高效的初始纠正，RL 提供覆盖长尾失败

## 4. 工程关键细节 (Engineering Tricks)
- **自动复位系统**：长时间自主 RL 需要可靠的自动复位（仍是落地瓶颈）
- **Advantage 条件化**：将标量优势值离散化/归一化后作为策略网络的额外条件输入
- **Safety Constraints**：RL 探索需要安全边界限制，避免机器人自损

## 5. 核心洞见 (Insights)

### 5.1 理论局限性深度分析
- **理论**：Advantage-conditioned 方法假设优势函数可准确估计，在稀疏奖励场景下可能不可靠
- **算法**：当前仍是 Per-task fine-tuning，未验证跨任务泛化能力
- **工程**：自动复位和安全监控是真实部署的最大工程瓶颈

### 5.2 与用户研究（灵巧手转笔/Sim-to-Real）的启发
- **PPO 转笔策略的三阶段路径**：(1) 仿真大量 PPO 训练（=IL 阶段等效），(2) 真机少量纠正示范（= Corrections），(3) 真机自主 RL 微调（= Practice）
- **Sim-to-Real Gap 与 Corrections**：真机纠正数据可能是弥补 Sim-to-Real gap 的高效方式——以 few-shot 成本覆盖关键失败模式
- **与 [[RL-100 - Performant Robotic Manipulation with Real-World RL|RL-100]] 对比**：RL-100 = Diffusion 内部嵌入 PPO 的 Offline→Online 飞轮；RECAP = VLA 级别的 IL→Corrections→RL 飞轮。核心哲学一致：模仿打底 + RL 突破上限

> [!note] VLA post-training 子簇 + "IL×RL 组合的两种正交拓扑"
> RECAP 是 VLA post-training 子簇一员：
>
> | 论文 | post-training 路径 |
> |------|------------------|
> | RECAP | IL → Corrections → Autonomous RL（advantage-conditioned）|
> | [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation\|DexHiL]] | Human-in-the-Loop |
> | [[RL-100 - Performant Robotic Manipulation with Real-World RL\|RL-100]] | IL → Offline RL → Online RL（diffusion 内嵌 PPO）|
> | [[WMPO - World Model-based Policy Optimization for VLA\|WMPO]] | World-model-based PO |
>
> **领域级 insight——IL×RL 组合的两种正交拓扑**：知识库反复出现"IL 与 RL 组合"，但拓扑有两种、**RL 与 IL 的时序角色相反**：
> 1. **IL 打底 → RL 突破上限**（RECAP / RL-100 / [[TRANSIC - Sim-to-Real Policy Transfer by Learning from Online Correction\|TRANSIC]]）：IL 先学"偶尔成功"，RL 突破到"可靠"——瓶颈是 **IL 天花板/长尾失败**时选它。
> 2. **RL 教师 → IL 学生**（privileged teacher-student：[[Learning Quadrupedal Locomotion over Challenging Terrain\|Learning Quadrupedal]] / [[In-Hand Object Rotation via Rapid Motor Adaptation (HORA)\|HORA]] / [[Lessons from Learning to Spin Pens\|Spin Pens]]）：RL 用特权信息学 oracle，IL 蒸馏到可部署 student——瓶颈是 **sim-to-real 部署**时选它。
>
> RECAP 的 advantage-conditioning（从失败学"避免"）与 [[Unified Policy Evaluation and Improvement - On Off-Policy Classification\|Unified Policy]] 的 Multi-step→Iterative 演进、$\pi_{ref}$ 保守约束一脉相承。

## 6. 与知识体系的联系

### 与 [[EmbodiedAI]] 的联系
- RECAP 代表了 VLA Post-Training 的第三条路径：IL $\to$ RL with Experience（补充 DexHiL 的 Human-in-Loop 路径和 RL-100 的 Diffusion-内嵌 PPO 路径）
- 在 VLA 数据飞轮中，RECAP 实现了 "Practice makes perfect" 的最后一环

### 与 [[ReinforcementLearning]] 的联系
- Advantage-conditioned policy 是 Offline RL 思想在 VLA 上的自然延伸
- 三阶段框架对应 [[Unified Policy Evaluation and Improvement - On Off-Policy Classification|Unified Policy]] 中的 Multi-step $\to$ Iterative 演进

## 7. 局限与未来方向

### 7.1 论文自身局限
- 无开源代码/权重（商业公司限制）
- 自动复位和长时间无人值守的安全保障仍是关键工程挑战
- 尚未验证跨 Embodiment 泛化

### 7.2 对灵巧手转笔 / Sim-to-Real 的启发
- 三阶段训练哲学可直接映射到灵巧手 Pipeline
- "纠正"阶段在 Sim-to-Real 中可具象化为真机少量微调数据的定向采集

## References
- [[RL-100 - Performant Robotic Manipulation with Real-World RL]]
- [[DexHiL - A Human-in-the-Loop Framework for VLA Post-Training in Dexterous Manipulation]]
- [[WMPO - World Model-based Policy Optimization for VLA]]
