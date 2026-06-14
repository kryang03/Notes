# Paper Recap Insight Taste Rubric

Use this reference when calibrating depth for this user.

## The User's Taste

The user wants a paper recap to behave like a research mentor's reconstruction, not like an abstract expansion. The desired document should:

- Start from the paper's core bottleneck and the structural bet behind the method.
- Rebuild the relevant theory from first principles when a formula or symbol appears.
- Treat notation as a source of insight: coordinate frames, local/global variables, active/passive transforms, time indices, rollout/update stages, fixed vs learnable quantities.
- Track physical quantities and algorithmic variables by origin, not just by definition.
- Preserve experimental evidence and read ablations as causal probes.
- Compare against alternative paradigms, not just named baselines.
- Translate the method into the user's own research world: dexterous manipulation, pen spinning, PPO, Diffusion Policy, Sim-to-Real, tactile/contact, and actuator dynamics.
- State failure boundaries clearly.
- Update the knowledge graph rather than producing an isolated note.

## What "Deep Enough" Means

For any important claim, the recap should answer:

1. What exact problem or bottleneck is being attacked?
2. What classical theory, prior architecture, or physical model is being modified?
3. What assumption makes the modification plausible?
4. Which variables are fixed structure, observed data, computed intermediate quantities, supervision labels, or learnable parameters?
5. Which variables are local, global, time-indexed, detached, sampled, optimized, or physically constrained?
6. What would break if the assumption is false?
7. What ablation tests this mechanism, and what causal chain explains the result?
8. How would the method be used, modified, or rejected in the user's current projects?

## PDF-Only Extraction Strategy

When only a PDF is provided:

- Read abstract, introduction, method, experiments, limitations, and appendix.
- Search the extracted text for equation numbers, "ablation", "baseline", "implementation", "training details", "dataset", "limitations", "we observe", "we find", "fails", and "future work".
- Build an outline from headings, but write the recap from causal dependencies, not from paper order.
- If equations are poorly extracted, reconstruct them from surrounding prose and verify against repeated references in the text.
- Treat figures/tables as evidence: extract task names, metrics, baselines, and trend direction even when exact captions are noisy.
- Use external code only if the user asks; otherwise prefer conceptual dataflow.

## Preferred Explanation Patterns

### Formula Reconstruction

Use this pattern:

1. Classical starting point.
2. Constraint or observation.
3. Algebraic transformation.
4. Paper's relaxation or parameterization.
5. Meaning of each term.
6. Failure or boundary condition.

### Variable Table

Use columns like:

| Variable | Domain/shape | Source | Fixed/learned/observed/computed | Meaning | Trap |
|----------|--------------|--------|----------------------------------|---------|------|

"Trap" should capture ambiguity: coordinate convention, gradient status, unit, frame, action horizon, distribution vs sample, or whether it is a physical quantity or latent feature.

### Ablation Causal Chain

Write:

`Remove/change A -> observed metric B changes -> because mechanism C is disabled/amplified -> implication D for using the method.`

### Personalized Research Transfer

For each method, produce at least one of:

- A direct modification to PPO / Diffusion Policy / world model / controller.
- A diagnostic experiment.
- A reason not to use the method in contact-rich dexterous manipulation.
- A Sim-to-Real risk and mitigation.

## What To Avoid

- Do not satisfy depth by adding code.
- Do not add "minimal PyTorch core logic" unless explicitly requested.
- Do not leave formulas as unexplained symbols.
- Do not call a method "physics-informed" without identifying the exact physical structure.
- Do not say "better generalization" without explaining what inductive bias narrows the function class.
- Do not list ablation numbers without causal interpretation.
- Do not add Foundation links as decoration; each link must carry a specific conceptual correspondence.

## Recap Completion Checklist

- [ ] Frontmatter complete and Obsidian-compatible.
- [ ] Core contribution stated as method + bottleneck + structural insight.
- [ ] Prerequisite theory reconstructed from first principles where needed.
- [ ] Central variables table included.
- [ ] Core formulas derived or mechanically explained without jumps.
- [ ] No default implementation-code section.
- [ ] Experiment setup and key numbers preserved.
- [ ] Ablations interpreted causally.
- [ ] Alternatives compared by assumptions and failure modes.
- [ ] User-specific implications are concrete.
- [ ] Foundations linked and, when useful, reverse-linked.
- [ ] Canvas considered for algorithmic breakthrough relevance.
- [ ] Links and Canvas validated.
