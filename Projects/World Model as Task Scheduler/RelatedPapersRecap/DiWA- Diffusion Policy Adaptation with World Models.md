---
tags:
  - paper
  - diffusion-policy
  - world-model
  - policy-adaptation
  - offline-rl
  - WMTS
aliases:
  - DiWA
paper-year: 2025
read-date: 2026-06-15
venue: CoRL 2025
paper-pdf: "[[DiWA- Diffusion Policy Adaptation with World Models.pdf]]"
related:
  - "[[StochasticProcess]]"
  - "[[ReinforcementLearning]]"
  - "[[EmbodiedAI]]"
  - "[[Final_WMTS]]"
---

# DiWA: Diffusion Policy Adaptation with World Models

> [!abstract] 核心贡献
> 把"用 RL 微调 Diffusion Policy"完全搬进**想象**：DiWA 把 DPPO 的"去噪过程即 MDP"**嵌进** Dreamer 式 world model 的"想象即 MDP"，构成 **Dream Diffusion MDP**，于是用 PPO 微调预训练 DP **零真实交互**——world model 只在数十万条 offline play 数据上训练一次并冻结。CALVIN 8 任务上离线微调即提升，物理交互比 model-free 基线少几个数量级，并首次实现"在 dream 里微调的 DP 零样本部署到真机"。

> [!tip] 与理论基础的关联
> - [[StochasticProcess]] — 扩散去噪链（多步 MDP）+ DreamerV3 categorical latent world model。
> - [[ReinforcementLearning]] — 在 Dream Diffusion MDP 上跑 PPO；offline model-based policy improvement。
> - [[EmbodiedAI]] — 预训练-微调范式用于机器人技能（CALVIN play 数据）。
> - [[Final_WMTS]] — **WMTS "DP generalist + world model refinement" 的精确机制范本**；Dream Diffusion MDP 可直接复用。
>
> **核心技术**: Dream Diffusion MDP (Eq 5-6), Diffusion-denoising-as-MDP (DPPO), 冻结通用 WM (play 数据), 成功分类器奖励, PPO offline fine-tune

## 0. 阅读定位与范本价值

WMTS 流水线 `PPO Oracle → DP generalist → ensemble world model 精炼` 中"world model 精炼 DP"这一步，DiWA 给出最干净的现成机制。它正好衔接我已 recap 的两篇父论文：[[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]（DP 本体）与 [[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]（latent WM imagination）。读它的关键是看清 **Dream Diffusion MDP 如何把两个 MDP 嵌套成一条时间线**，以及它和 [[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]] 的异同。

## 1. 问题设定与动机（逻辑与价值）

### 1.1 一句话核心
DP 是 IL 训出来的，继承 IL 的分布偏移/OOD 失败/受 demo 质量限的毛病；想用 RL 微调它有两道坎：(a) **去噪链很长**，回报难以反传到每一步去噪；(b) **RL 要百万次真实交互**，真机上昂贵、慢、不安全。DiWA 用 world model 当"安全的数据驱动仿真器"，把整个 RL 微调挪进想象，一次性绕过两道坎。

### 1.2 直观隐喻
DPPO 让 DP 在真实/仿真环境里"反复练习并按回报改进"——但每练一次都要真机滚一遍（昂贵）。DiWA 让 DP **在梦里练习**：用回放数据长出的 world model，把"环境推进那一步"也搬进想象，于是整套 PPO 微调零真实交互。人类正是靠内部世界模型"想象后果再行动"来用极少试错适应——DiWA 把这件事做成算法。

### 1.3 现有方法的局限（注入先验 / 关键局限）

| 方法 | 注入的先验 | 关键局限 |
|---|---|---|
| DP（仅 IL） | 多模态动作分布 | 继承 IL：分布偏移、OOD 失败、受 demo 覆盖/质量限 |
| 在线 RL 微调 DP（**DPPO**） | 去噪过程=多步 MDP + PPO | 需**百万**真实交互 + 真值仿真 state；昂贵/不安全/有 sim-to-real gap |
| offline Q-learning DP | 用离线数据 | 受数据覆盖限；Q 外推不可靠 |
| Dreamer 式 WM RL | imagination 训策略 | 通常在线、WM 与任务耦合；不针对 DP 的去噪链 |
| **DiWA** | 冻结的通用 WM（play 数据）+ Dream Diffusion MDP + PPO offline | 完全依赖 WM 准确性与成功分类器质量 |

### 1.4 Delta 分析
精确增量 = **DPPO ⊕ Dreamer**：把 DPPO 的"去噪即 MDP"嵌进 Dreamer 的"想象即 MDP"，得到完全离线、零真实交互的 DP 微调。关键工程取舍：world model **训一次即冻结、任务无关、可复用**（用 play 数据），任务奖励由一个在 expert latent 上训练的成功分类器提供。

## 2. 核心方法与理论（原理与理论：两个 MDP 如何嵌套）

### 2.1 变量来源追踪

| 变量 | 维度/空间 | 来源阶段 | 是否带梯度 | 物理/算法意义 | 符号陷阱 |
|---|---|---|---|---|---|
| $z_t,h_t,\hat s_t=(h_t,z_t)$ | categorical latent + 确定状态 | WM(play) 训练后冻结 | WM 侧 frozen；DP 侧条件 | 世界模型 latent 状态 | WM 训练后**不再更新** |
| $\bar a_t^k$ | 动作（去噪中间量） | DP 去噪链 | learned ($\theta$) | 第 $k$ 步去噪的 noisy action | $\bar a_t^0$ 才是环境动作 |
| $k$ | $1..K$ | 去噪调度 | 固定 | 去噪步 | 与世界模型时间 $t$ 不同维度 |
| $\bar t(t,k)=tK+(K-k)$ | 标量索引 | 构造 | 固定 | 把 $(t,k)$ 拉平成一条时间线 | 内层去噪 + 外层环境的复合时间 |
| $C_\psi(z_t)$ | $[0,1]$ | expert latent 上训的分类器 | learned ($\psi$) | 成功概率=奖励来源 | 任务奖励来自分类器，非环境 |
| $R_\psi(z_t,a_t)=C_\psi(z_{t+1})$ | 标量 | 分类器 | — | 想象中的 task reward | 仅在 $k=1$（动作完成）给 |
| $P_\phi(z_{t+1}\mid z_t,\bar a_t^0)$ | WM transition | 冻结 WM | frozen | 想象环境推进 | 仅在 $k=1$ 触发 |

### 2.2 两个待组合的 MDP

**(A) 扩散去噪 MDP（DPPO 的视角）**：DP 通过 $K$ 步去噪从噪声生成动作（Eq 1）：$\bar a_t^{k-1}\sim\pi_\theta(\bar a_t^{k-1}\mid s_t,\bar a_t^k)$，$k=K..1$，$\bar a_t^0$ 是环境动作。DPPO 指出：这条去噪链本身可看作一个**多步 MDP**（每个去噪步是一步，似然可算），于是能用 PPO 对去噪过程做策略梯度。

**(B) world model 想象 MDP（Dreamer 的视角）**：在 play 数据上训 RSSM（Eq 3-4，categorical latent + ELBO），得到 $M_{wm}=(Z,A,P_\phi,R_\psi,\gamma)$，冻结后可在 latent 里 rollout 想象轨迹（从 prior $\hat z_t\sim p_\phi(\hat z_t\mid h_t)$，无需观测）。

**任务奖励从哪来（关键工程）**：play 数据训出的 WM 是任务无关的，没有目标技能的奖励。DiWA 在 expert latent 上训一个**二分类成功分类器** $C_\psi(z_t)$，把想象里的奖励定义为 $R_\psi(z_t,a_t):=C_\psi(z_{t+1})\in[0,1]$（下一状态的成功概率）。这把一个通用 WM 变成带任务奖励的 $M_{wm}$。

### 2.3 Dream Diffusion MDP：把 (A) 嵌进 (B)（Eq 5-6，无跳步）

用复合索引 $\bar t(t,k)=tK+(K-k)$ 把"世界模型时间 $t$"与"去噪步 $k$"拉平成一条时间线。状态/动作/奖励（Eq 5）：

$$
\bar s_{\bar t(t,k)}=(z_t,\bar a_t^k),\quad
\bar a_{\bar t(t,k)}=\bar a_t^{k-1},\quad
\bar R_{\bar t(t,k)}=\begin{cases}R_\psi(z_t,\bar a_t^0),& k=1\\[2pt]0,&\text{otherwise}\end{cases}.
$$

转移（Eq 6）分两个 regime：

$$
\bar P(\bar s_{\bar t+1}\mid\bar s_{\bar t},\bar a_{\bar t})=
\begin{cases}
\delta(z_t,\bar a_t^{k-1}), & k>1\ \text{（内层去噪：}z_t\text{不动，只把}\bar a^k\text{去噪成}\bar a^{k-1}\text{，确定性）}\\[4pt]
P_\phi(z_{t+1}\mid z_t,\bar a_t^0)\otimes\mathcal N(0,I), & k=1\ \text{（外层：世界模型推进}+\text{重置噪声开新去噪）}
\end{cases}
$$

**读法**：当 $k>1$，停在同一 latent $z_t$ 内一步步去噪（Dirac 确定转移、零奖励）；当 $k=1$，产出最终动作 $\bar a_t^0$，世界模型才真正推进到 $z_{t+1}$（并采样新噪声开始下一段去噪），此刻才给分类器奖励。内层策略仍是 DP 去噪高斯 $\bar\pi_\theta(\bar a^{k-1}\mid z_t,\bar a^k)=\mathcal N(\mu_\theta(z_t,\bar a^k,k),\sigma_k^2 I)$。

**然后**：直接在 $M_{DD}$ 上跑 PPO，整条 rollout（环境推进 + 去噪）都在想象里——**零真实交互**。

### 2.4 概念边界与符号陷阱
- **三处 MDP 别混**：环境 MDP $M_{env}$（真实，DiWA 不在此微调）、世界模型 MDP $M_{wm}$（想象）、Dream Diffusion MDP $M_{DD}$（想象 ⊕ 去噪）。微调发生在 $M_{DD}$。
- **WM 冻结**：训练后不更新；这避免了 Dreamer 在线设定里"WM 与任务耦合"，让一个 WM 复用于多技能。但代价是 **PPO 可能利用 WM 的误差**（在冻结 WM 里刷高想象回报却不真实）。
- **奖励是分类器**，非环境 reward；分类器质量 = 奖励质量。
- 内层去噪步零奖励、确定转移；只有 $k=1$ 推进世界并给奖励——这是把"长去噪链不阻碍回报反传"落到结构上的方式。

### 2.5 信息流/算法机制（四阶段，无代码）
1. play 数据 $D_{play}$ → 训 RSSM world model（Eq 4）→ 冻结。
2. expert demos $D_{exp}$（在 WM latent 上）→ BC 预训练 DP。
3. expert latent → 训成功分类器 $C_\psi$ 作为奖励。
4. 在 Dream Diffusion MDP 内用 PPO 微调 DP（全程想象）。部署：真机直接跑微调后的 DP，无额外适配。

## 3. 训练、数据与实验（实验与验证）

### 3.1 实验设置
**CALVIN** 基准，8 个语言/技能任务；两类离线数据：少量 target-skill expert demos $D_{exp}$ + 大量任务无关 play 数据 $D_{play}$（数十万交互，训 WM 一次）。对比 model-free RL 微调基线（需在线交互）。含真机零样本部署验证。

### 3.2 关键结果与因果解释
- **8 任务离线微调即提升**：相对 BC 预训练 DP，纯离线（零真实交互）即提高成功率；所需物理交互比 model-free 基线少**几个数量级**。**因果**：唯一的真实数据是训 WM 用的 play 数据（一次性），微调阶段全在想象→交互成本几乎为零。
- **零样本真机部署**：WM 用真机 play 数据训，DP 在 dream 里微调，直接上真机不再交互。**因果**：因为 WM 的 latent 动力学 grounded 在真实数据，dream 里学到的改进迁移回真实。这是论文声称的"首次用 offline WM 微调 DP 真机技能"。

### 3.3 Ablation / 对照因果链
- `去 world model（=DPPO 在线）→ 需百万真实交互 + 真值 state → 真机不可行`：这是 DiWA 的存在理由。
- `WM 在线更新（耦合任务）→ 失去"训一次复用"`：DiWA 选冻结通用 WM 换取多技能复用。
- `奖励不用成功分类器（无 task reward）→ 通用 WM 无法对目标技能微调`：分类器是把通用 WM 接上任务的关键。

### 3.4 工程约束与实验边界
- 安全/效率全押在 WM 准确性：WM 在 OOD 处的误差会被 PPO 利用（想象回报虚高）。
- 成功分类器只给二值/概率奖励，信号较稀疏粗糙。
- CALVIN 是桌面操作，非接触密集的手内高速任务。

## 4. 核心洞见（逻辑与价值 + 未来）

### 4.1 论文真正的 insight
**把"DP 微调要的两个昂贵东西——长去噪链的可微 RL（DPPO）与海量真实交互（RL）——一次性塞进一个嵌套 MDP（Dream Diffusion MDP），在冻结的通用世界模型里用 PPO 离线解决。** 去噪 MDP 解决"回报反传到每步去噪"，世界模型 MDP 解决"零真实交互"，二者嵌套是关键。

### 4.2 为什么这个设计有效
(1) 去噪步零奖励 + 确定转移、只有动作完成才推进世界并给奖励——结构上让 PPO 的回报正确分配；(2) WM 想象把真实交互成本降到训练 WM 的一次性 play 数据；(3) 成功分类器把任务无关 WM 接上目标技能；(4) WM grounded 在真实数据 → dream 改进可迁移真机。

### 4.3 什么时候会失效
- WM 在 OOD/接触处不准 → PPO 利用想象误差 → 真机不提升甚至变差（model-based RL 的根本风险）。
- 任务需要超出 play 数据动力学覆盖的行为。
- 成功难以用分类器定义（接触/力相关的细粒度成功）。

## 5. 替代方案与理论局限（未来与结合）

### 5.1 理论维度
DiWA 是 offline model-based policy improvement：改进上界由**冻结 WM 的保真度**决定。PPO 在固定 WM 上优化，本质是"对一个学到的近似环境最优化"——存在 model-exploitation 风险，且无在线纠错（WM 不更新）。

### 5.2 算法维度
| 方法 | 优点 | 缺点 | 与 DiWA 关系 |
|---|---|---|---|
| DPPO（在线） | 真环境信号、无 WM 误差 | 百万交互 + 真值 state | DiWA 的去噪-MDP 来源；DiWA 换成离线 |
| World4RL | 扩散 WM 精炼策略 | 设定不同 | 同属 DP+WM 精炼一族 |
| offline Q-learning DP | 纯离线 | Q 外推不稳 | DiWA 用 on-policy PPO-in-dream 替代 |
| Dreamer（在线 WM RL） | 在线纠错 | WM 任务耦合、非 DP | DiWA 冻结 WM、面向 DP 去噪链 |

### 5.3 工程/实验维度
WM 保真度、成功分类器质量、play 数据覆盖、WM-exploitation 是主要风险点；桌面 CALVIN 未覆盖接触密集任务。

## 6. 对用户研究的启发（未来与结合：WMTS generalist refinement）

### 6.1 对 WMTS / 灵巧手 / Sim-to-Real 的迁移

| WMTS 模块 | DiWA 对应 | 迁移设计 |
|---|---|---|
| **Generalist 精炼** | Dream Diffusion MDP 内 PPO 微调 DP | WMTS 的"ensemble WM 精炼 DP generalist"可直接用 Dream Diffusion MDP 机制 |
| 奖励 | 成功分类器 $C_\psi$ | 换成 **TAR（tactile-anchored reward）**：用触觉拓扑 + WM-NLL，避免二值成功的稀疏粗糙 |
| WM | 单一冻结 latent WM | 换成 **ensemble + uncertainty penalty**，抑制 PPO 利用 WM 误差（DiWA 单 WM 的最大软肋） |
| 数据 | play 数据训 WM 一次 | 对应 WMTS "≤1h 真机数据 + WM" 的样本预算 |

**核心论证（critical thinking）**：DiWA 用**单一冻结 WM** + **二值成功奖励**，这两点恰是 WMTS 要改的：(1) 单 WM 下 PPO 会刷"想象里高、真实里假"的回报 → WMTS 必须用 ensemble + disagreement/LCB 惩罚（这正是 WMTS 用 ensemble 而非单 WM 的理由）；(2) 二值成功对灵巧手太粗 → 用触觉锚定的稠密奖励（TAR）。此外 DiWA 是 latent WM（桌面），WMTS 想要 actuator+rigid 物理结构化 WM 以处理接触——"dream 里微调零样本上真机"在桌面成立，不能直接外推到手内高速接触。

### 6.2 可验证实验建议
- 在手内重定向上实现 Dream Diffusion MDP：用 actuator+rigid ensemble WM + 触觉奖励，PPO 离线微调 DP generalist；对照 (a) DPPO 在线、(b) DiWA 单 WM、(c) ensemble-LCB WM。看 model-exploitation 与真机成功率。
- 验证 WM-exploitation：单 WM vs ensemble 下，测想象回报与真机回报的 gap 随微调步数的变化。

### 6.3 不应过度外推的点
- "dream 里微调零样本上真机"是桌面 CALVIN 结论；接触密集/高速手内任务的 WM 误差更大，迁移风险高。
- 单一冻结 WM 在灵巧手上不够稳健 → 必须 ensemble。
- 成功分类器奖励对精细接触不足 → 需触觉/力奖励。

## 7. 与知识体系的联系

### 与 [[StochasticProcess]] 的联系
扩散去噪链（多步随机生成）+ DreamerV3 categorical latent world model（ELBO，Eq 4）；Dream Diffusion MDP 是两个随机过程的嵌套。

### 与 [[ReinforcementLearning]] 的联系
在 Dream Diffusion MDP（Eq 5-6）上跑 PPO 的 offline model-based policy improvement；去噪步零奖励 + 仅动作完成给奖励，是"长去噪链不阻碍回报分配"的结构解。

### 与 [[EmbodiedAI]] 的联系
pretrain（BC）→ finetune（RL-in-dream）范式用于机器人技能（CALVIN play 数据），并验证零样本真机部署。

### 与 [[Final_WMTS]] 的联系
WMTS "PPO Oracle → DP generalist → world model 精炼"中精炼步的精确机制范本；WMTS 在其上的两处改进（ensemble 抗 WM-exploitation、触觉奖励替代二值成功）正是项目的差异化卖点。

## References
- 原始 PDF：[[DiWA- Diffusion Policy Adaptation with World Models.pdf]]
- 两个父方法：[[Diffusion Policy: Visuomotor Policy|Diffusion Policy]]（DP 本体）、[[DREAM TO CONTROL: LEARNING BEHAVIORS BY LATENT IMAGINATION|Dreamer]]（latent WM）；去噪-MDP 来自 DPPO
- 兄弟：[[World4RL- Diffusion World Models for Policy Refinement with Reinforcement Learning for Robotic Manipulation|World4RL]]
- 项目入口：[[Final_WMTS]]
