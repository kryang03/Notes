---
tags: [paper, rotation-representation, WMTS]
aliases: [6D Rotation, Continuous Rotation]
paper-year: 2019
venue: CVPR
related: ["[[ComputationalGeometry]]", "[[Final_WMTS]]"]
paper-pdf: "[[On the Continuity of Rotation Representations in Neural Networks.pdf]]"
---

# On the Continuity of Rotation Representations in Neural Networks

> [!abstract] 核心贡献
> 证明 3D 旋转在 $\leq$ 4 维实欧氏空间中**所有表示均不连续**（包括四元数和欧拉角），提出 5D/6D 连续旋转表示，显著优于不连续表示。

## 核心结论

- 四元数 $q \in \mathbb{R}^4$：$q$ 和 $-q$ 表示同一旋转 → 双重覆盖 → 不连续
- 欧拉角：万向节死锁 → 不连续
- **6D 连续表示**：取旋转矩阵前两列 $[r_1, r_2] \in \mathbb{R}^6$，通过 Gram-Schmidt 正交化恢复 $R$
- **5D 连续表示**：进一步压缩一维（理论最低维度连续表示）

## 与 WMTS 的关联

- **WMTS 任务空间 $\mathcal{C}_{global}$ 中旋转表示（§零）**直接采用 6D Continuous Rotation Representation
- 避免四元数双重覆盖破坏欧氏距离 → 对 VAE 隐空间和 Diffusion 的 MSE loss 至关重要
- PointNet 物体表征中的旋转编码也应使用 6D 表示
