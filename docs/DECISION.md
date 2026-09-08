# Architecture Decision Records (ADRs)

This document records the architectural and design decisions for the **Origins Rustic** datapack.

---

## ADR-001: Standardization on Minecraft 1.21 Singular Tag Directories

* **Date**: 2026-09-09
* **Status**: Accepted & Implemented
* **Context**:
  In Minecraft 1.21 (`pack_format: 48`), Mojang standardized all datapack tag directories to singular forms matching their registry identifiers (`tags/block/`, `tags/item/`, `tags/entity_type/`, `tags/fluid/`). The legacy `origins-rustic` codebase retained plural folders (`tags/blocks/`, `tags/items/`), which caused Minecraft 1.21 to ignore `#rustic:stone`, `#rustic:heavy_armor`, and other item/block tags during runtime.
* **Decision**:
  Migrate all tag directories under `data/rustic/tags/` from `blocks/` to `block/` and `items/` to `item/`. Preserve `data/rustic/tags/origins/power/` because it maps to the `origins:power` registry path.
* **Consequences**:
  * All block conditions (e.g. `rustic:more_stone_break_speed`) and item conditions (e.g. `rustic:prevent_cleaver`) properly resolve in Minecraft 1.21.
  * Backwards compatibility with Minecraft 1.20 and below is formally discontinued in favor of 1.21.1 stability.

---

## ADR-002: Reversion from Multi-Tier Evolution to Modular Tag-Based Architecture

* **Date**: 2026-09-09
* **Status**: Accepted
* **Context**:
  Earlier development iterations explored an MMO-style multi-tier essence evolution system (`data/neoorigins` with `apex`, `ascended`, `evolved` tiers). This introduced excessive complexity, hard-to-balance stat inflation, and bloated JSON file trees (hundreds of duplicate sub-powers).
* **Decision**:
  Return to the clean, classic Origins model where each player selects one Origin (Race) and one Class (Job). Structure power assignments using registry tags (`#rustic:<id>_powers`) rather than hardcoding power arrays inside individual origin JSON files.
* **Consequences**:
  * Origin definitions become clean metadata shells pointing to tag identifiers.
  * Powers can be added, updated, or removed from an entire race or class by editing a single tag file without altering character definition files.
  * Staged powers for unfinished races (`frostborn`, `vampire`) are isolated until ready.

---

## ADR-003: Delegation of Complex Mechanics to KubeJS (LootJS & OriginJS)

* **Date**: 2026-09-09
* **Status**: Accepted
* **Context**:
  Certain mechanics—such as dynamic ore drop doubling across all modded ores and crop drop multipliers—can produce edge cases or performance overhead when attempted purely via complex datapack loot table replacements. Additionally, Y-level coordinate checks for Dwarf underground resilience can be brittle in custom dimensions.
* **Decision**:
  Implement baseline datapack powers (`origins:replace_loot_table` and `origins_classes:modify_block_loot`) as native fallback, but prepare integration points for **LootJS** (for server-side loot modification) and **OriginJS** (for JavaScript-based origin condition queries) as documented in `ORIGIN.md`.
* **Consequences**:
  * Vanilla/datapack-only environments retain working baseline powers.
  * Server modpack installations with KubeJS can intercept and enhance drops with full modded cross-compatibility.

---

## ADR-004: Release Branching and Peer-Review Workflow

* **Date**: 2026-09-09
* **Status**: Accepted
* **Context**:
  Origins Rustic is a collaborative repository with active maintainers and server deployments. Direct commits to `master` risk breaking production server configurations.
* **Decision**:
  Enforce strict branch hygiene:
  1. `master` branch is strictly protected. Zero direct commits.
  2. A release branch `v2.0` serves as the primary integration branch for the 2.0 release cycle.
  3. All development occurs on isolated feature branches (`fix/*`, `docs/*`, `feature/*`, `test/*`) and merges into `v2.0`.
  4. Final promotion from `v2.0` to `master` will occur exclusively via a documented Pull Request subject to collaborative review.
  5. Existing GitHub issues (#1 through #14) remain historical references and are not touched or overwritten.
* **Consequences**:
  * Development remains auditable and isolated.
  * Colleague review gates are preserved.

---

## ADR-005: Alignment of Local Power Namespaces

* **Date**: 2026-09-09
* **Status**: Accepted & Implemented
* **Context**:
  `farmer_powers.json` previously referenced external `origins_classes:more_crop_drops`, while an identical, tailored power `data/rustic/origins/power/more_crop_drops.json` was present in the repository. Similarly, `miner_powers.json` referenced `rustic:double_ores` which lacked a corresponding power file.
* **Decision**:
  Standardize on the internal `rustic:` namespace for all customizable powers. Farmer points to `rustic:more_crop_drops`. Miner `rustic:double_ores` is instantiated locally to hook [data/rustic/loot_table/double_ores.json](file:///e:/Github2/origins-rustic/data/rustic/loot_table/double_ores.json).
* **Consequences**:
  * Zero missing reference errors during datapack reload.
  * The datapack remains self-contained without unexpected upstream `origins_classes` breaking changes.
