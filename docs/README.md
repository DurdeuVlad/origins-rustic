# Origins Rustic Documentation Suite (`flux-docs`)

Welcome to the **Origins Rustic** documentation suite for Minecraft 1.21.1 (`pack_format: 48`). This repository operates under specification-based development where documentation serves as the contract surface for all gameplay mechanics, economic systems, and technical implementations.

---

## 1. Repository Classification & Governance

* **Ownership Mode**: `Collaborative` (Multi-developer team with peer-review gates).
* **Visibility Mode**: `Public / Open Source` (Active server deployment for Rustic Craft 2).
* **Integration Branch**: `v2.0` (Staging branch prior to `master` promotion).

---

## 2. Document Catalog & Specification Map

Per the `/flux-docs` standard, the documentation base is organized into baseline, mode-specific, and domain-specific specifications:

| Document | Category | Purpose & Rationale | Status | Traceability |
| :--- | :--- | :--- | :--- | :--- |
| [`Business.md`](file:///e:/Github2/origins-rustic/docs/Business.md) | **Baseline** | High-level RPG design philosophy, player personas, economic matrix (Gathering, Refining, Combat), tool gating, progression flows, and non-goals. | `Complete` | Gameplay Design |
| [`Decision.md`](file:///e:/Github2/origins-rustic/docs/Decision.md) | **Baseline** | Durable Architecture Decision Records (ADR-001 through ADR-006) recording tag migrations, evolution reversion, KubeJS fallback, branch hygiene, and feature isolation. | `Complete` | Architecture / ADRs |
| [`Milestones.md`](file:///e:/Github2/origins-rustic/docs/Milestones.md) | **Baseline** | Outcome-based release checkpoints (M1 to M6) mapping all open GitHub issues (#1 to #14), acceptance criteria, and verification surfaces. | `Complete` | Project Milestones |
| [`Collaboration.md`](file:///e:/Github2/origins-rustic/docs/Collaboration.md) | **Mode-Specific** | Team collaboration policy, branch strategy (`master` <- `v2.0` <- `feature/*`), PR delivery contract, quality gates, and Conventional Commits. | `Complete` | Contribution Guide |
| [`RUSTIC_ORIGINS_SPEC.md`](file:///e:/Github2/origins-rustic/docs/RUSTIC_ORIGINS_SPEC.md) | **Domain Spec** | Exhaustive technical specification of all 12 Races and 13+ Classes, mathematical attribute modifiers, keybinds, cooldowns, and 1.21 singular tag registries. | `Complete` | Technical Specification |
| [`TESTING.md`](file:///e:/Github2/origins-rustic/docs/TESTING.md) | **Domain Spec** | Live server test harness, automated test batches, empirical verification procedures, attribute query formulas, and Knight FAQ. | `Complete` | Testing Harness |
| [`README.md`](file:///e:/Github2/origins-rustic/README.md) | **Root Entrypoint** | Central repository introduction, installation instructions for singleplayer and dedicated servers, mod dependencies, and documentation links. | `Complete` | Repository Root |

---

## 3. Conditional & Deferred Documents Rationale

* **`API.md` (Integrated)**: The interface boundaries for Origins Rustic consist of datapack registries (`origins:power`, `minecraft:item`, `minecraft:block`) and loot table hooks. These are fully documented within [`RUSTIC_ORIGINS_SPEC.md`](file:///e:/Github2/origins-rustic/docs/RUSTIC_ORIGINS_SPEC.md) Section 4.
* **`Testing.md` (Integrated in Milestones)**: Verification procedures, syntax validation scripts, and server testing protocols are formalized directly inside [`Milestones.md`](file:///e:/Github2/origins-rustic/docs/Milestones.md) under Milestone 6 and individual issue acceptance criteria.
* **`Security.md` (Integrated in Business)**: Grief prevention, tool restriction feedback, and combat exploitation mitigations are defined in [`Business.md`](file:///e:/Github2/origins-rustic/docs/Business.md) Section 7.

---

## 4. Document Maintenance & Review Lifecycle

1. Any modification to player attributes, class abilities, or power tags must update [`RUSTIC_ORIGINS_SPEC.md`](file:///e:/Github2/origins-rustic/docs/RUSTIC_ORIGINS_SPEC.md).
2. Architectural decisions must be recorded as a new ADR in [`Decision.md`](file:///e:/Github2/origins-rustic/docs/Decision.md).
3. New feature branches and GitHub issues must be linked in [`Milestones.md`](file:///e:/Github2/origins-rustic/docs/Milestones.md).
