---
tags:
  - paper
  - dexterous-grasping
  - contact-map
  - representation-learning
aliases:
  - GenDexGrasp
  - MultiDex
paper-year: 2023
read-date: 2026-04-26
venue: ICRA
paper-pdf: "[[Papers/GenDexGrasp: Generalizable Dexterous Grasping.pdf]]"
related:
  - "[[ContactMechanics]]"
  - "[[RepresentationLearning]]"
  - "[[ComputationalGeometry]]"
  - "[[Optimization]]"
---

# GenDexGrasp: Generalizable Dexterous Grasping

> [!abstract] 核心贡献
> GenDexGrasp 用 object-centric contact map 作为 hand-agnostic 中间表征，在 MultiDex 数据集上学习可迁移抓取生成，实现对多种未见机械手的成功率、速度与多样性折中。

## 1. 问题设定与动机

### 1.1 核心洞察

关节角不是通用抓取语言，因为不同机械手的拓扑和关节定义不同；接触图更接近任务的物理本质：**物体表面哪些区域应该和手发生接触**。

### 1.2 现有方法局限

- hand-aware 方法依赖特定手型编码，泛化到 Shadow/Allegro/Barrett 等形态差异很大的手时脆弱。
- hand-agnostic 采样规划通常要数分钟到数十分钟，难以在线使用。
- 确定性 IK/solver 生成多样性不足，容易只找到单一抓取模式。

## 2. 核心方法/理论

### 2.1 Delta 分析

1. 提出 MultiDex：5 种手、58 个物体、436k 组多样抓取。
2. 用 CVAE 生成 hand-agnostic object contact map。
3. 提出 aligned distance，修复薄壳物体两侧被欧氏距离误判为接触的歧义。

### 2.2 数学框架

给定物体点云 $\mathcal{P}_O=\{p_i,n_i\}_{i=1}^{N}$ 与手表面 $\mathcal{S}_H$，contact map 是每个物体表面点到手的归一化接近度：

$$
\Omega_i = \exp(-\alpha D_{align}(p_i,\mathcal{S}_H)).
$$

aligned distance 不只看欧氏距离，还考虑物体表面法向与候选接触方向的一致性：

$$
D_{align}(p_i,h_j)=\|p_i-h_j\|_2 \cdot g(n_i,\frac{h_j-p_i}{\|h_j-p_i\|_2}),
$$

其中 $g(\cdot)$ 对背面/薄壳错误接触赋予更大惩罚。CVAE 学习：

$$
q_\phi(z\mid \Omega,\mathcal{P}_O),\quad \hat{\Omega}=p_\theta(\Omega\mid z,\mathcal{P}_O),
$$

$$
\mathcal{L}_{CVAE}=\|\Omega-\hat{\Omega}\|_2^2+\beta D_{KL}(q_\phi(z\mid\Omega,\mathcal{P}_O)\|\mathcal{N}(0,I)).
$$

抓取优化阶段寻找手姿态 $q_H$：

$$
q_H^*=\arg\min_{q_H}\; E_c(\Omega(q_H),\hat{\Omega})+\lambda_p E_{penetration}+\lambda_j E_{joint-limit}.
$$

### 2.3 核心伪代码

```python
# object_points: [B, N, 3], object_normals: [B, N, 3]
latent = torch.randn(batch, latent_dim)
target_contact = cvae.decode(object_points, latent)       # [B, N]

q_hand = random_initialize_hand_pose(batch, num_seeds=32)
for _ in range(num_opt_steps):
    hand_surface = fk_hand_mesh(q_hand)                   # [B, M, 3]
    current_contact = aligned_contact_map(object_points, object_normals, hand_surface)
    contact_loss = ((current_contact - target_contact) ** 2).mean()
    loss = contact_loss + penetration_penalty(hand_surface, object_mesh) + joint_limit_penalty(q_hand)
    q_hand = optimizer_step(q_hand, loss)

q_hand = physics_refine(q_hand, object_mesh)
```

**物理量来源**：$\Omega$ 来自 force-closure 优化生成的合成抓取；$\hat{\Omega}$ 是 CVAE 输出；$q_H$ 来自可微 FK/优化变量；物理 refine 在仿真器中验证稳定性。

## 3. 训练与实验细节

### 3.1 数据与监督信号

- MultiDex：5 种机械手（EZGripper、Barrett、Robotiq-3F、Allegro、ShadowHand）、58 个 household objects、436,000 抓取姿态。
- 监督信号：由 force closure optimization 合成的抓取姿态及对应 contact map。

### 3.2 评估指标

- Success rate：物理仿真中抓取是否稳定。
- Diversity：同一 object-hand pair 下生成姿态的多样性。
- Inference speed：生成单个可用抓取所需时间。

### 3.3 Ablation 因果链

| 设计 | 去掉后的变化 | 因果机制 |
|---|---|---|
| aligned distance | success rate 明显下降，尤其薄壳物体 | 欧氏距离把薄壳另一侧也视作接近，导致 contact map 在几何上双面混淆 |
| CVAE latent sampling | 多样性下降 | 同一接触图/单一优化初值会收敛到相似 grasp basin |
| physics refinement | 视觉上合理但接触不稳定 | contact map matching 不等价于力闭合，需要仿真验证摩擦锥和穿透 |

## 4. 工程关键细节

- contact map 必须是 object-centric，否则会把手型拓扑泄漏进表征，削弱 hand-agnostic 泛化。
- 薄壳物体要避免 Euclidean nearest surface 的假接触；aligned distance 是几何一致性的必要修正。
- 并行多初值优化是摆脱局部极小的关键，比单次 IK 更适合多指抓取。

## 5. 核心洞见

### 5.1 理论局限性

- **理论**：contact map 描述“哪里接触”，但不完整描述“以多大力/何种切向力接触”。
- **算法**：CVAE 生成的是静态 grasp，不解决操作过程中的 rolling/sliding contact schedule。
- **工程**：仿真 refine 的成功率仍受摩擦、软接触和物体 mesh 质量影响。

### 5.2 与灵巧操作/WMTS 的启发

GenDexGrasp 给 [[Final_WMTS]] 的启发是：任务隐空间不应只编码目标姿态，还应编码**目标接触拓扑**。对于转笔或 in-hand reorientation，任务生成器可以把 $z_{task}$ 拆成 $z_{motion}$ 与 $z_{contact}$，后者由接触图或 finger-object affordance map 表示，从而让 Scheduler 生成“可执行接触模式”而不是只生成几何终点。

## 6. 与知识体系的联系

- [[ContactMechanics]]：force closure、摩擦锥与稳定抓取是 MultiDex 合成的物理基础。
- [[RepresentationLearning]]：CVAE contact map 是跨手型可迁移的中间表征。
- [[ComputationalGeometry]]：aligned distance 本质上是法向一致的表面距离度量。
- [[Optimization]]：抓取姿态求解是 contact-map matching + penetration/joint regularization 的非凸优化。

## 7. 局限与未来方向

对灵巧手转笔，下一步不应停在静态 grasp generation，而应将 contact map 升级为 time-indexed contact schedule $\Omega_{1:T}$，再与 diffusion/WM rollout 联合训练，使接触拓扑成为可规划的任务语言。
