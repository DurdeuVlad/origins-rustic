# Origins Rustic — Milestones Framework & Issue Roadmap (`Milestones.md`)

This document defines the outcome-based milestone framework for **Origins Rustic v2.0** on Minecraft 1.21.1 (`pack_format: 48`). Each milestone represents an unambiguous outcome gate with concrete acceptance criteria, risk boundaries, and verification surfaces.

---

## Milestone Lifecycle & Overview

```mermaid
graph LR
    M1["M1: Static Audit<br/>(1.21 Registries)"] --> M2["M2: Documentation Base<br/>(flux-docs & flux-milestone)"]
    M2 --> M3["M3: Combat Classes<br/>(Barbarian & Knight)"]
    M3 --> M4["M4: Trade & Gathering<br/>(Tanner, Farrier, RC1 Jobs)"]
    M4 --> M5["M5: Staged Races<br/>(Frostborn & Vampire)"]
    M5 --> M6["M6: Verification & Release Gate<br/>(Master Promotion)"]
```

| Milestone | Target Outcome | Primary Scope | Status | GitHub Issues |
| :--- | :--- | :--- | :--- | :--- |
| **M1: Static Audit & 1.21 Registries** | Fix broken tag paths, restore missing powers, align registries. | `data/rustic/tags/`, Dwarf/Miner/Farmer repairs. | **DONE** | #15 (PR) |
| **M2: Architecture & Documentation Base** | Complete durable specifications per `/flux-docs` and `/flux-milestone`. | `Business.md`, `Decision.md`, `Milestones.md`, `Collaboration.md`, `RUSTIC_ORIGINS_SPEC.md`, `README.md`. | **ACTIVE** | N/A |
| **M3: Combat & RPG Classes Expansion** | Introduce tactical frontline combat roles with unique mechanics. | Barbarian (#1, #2, #3), Knight (#5, #6). | **IN PROGRESS** | #1, #2, #3, #5, #6 |
| **M4: Trade & Gathering Classes Porting** | Complete economic interdependence loop for crafting & resource harvesting. | Tanner (#9), Farrier (#11), Archivist (#10), Fisherman (#12), Farmer (#7), Blacksmith (#8), Nitwit (#14), Old Jobs (#4). | **SCHEDULED** | #4, #7, #8, #9, #10, #11, #12, #14 |
| **M5: Staged Origin Races Activation** | Fully implement Frostborn and Vampire from staged prototypes into playable origins. | `data/rustic/origins/origin/frostborn.json`, `vampire.json`, associated powers & tags. | **SCHEDULED** | Staged |
| **M6: Verification & v2.0 Release Gate** | End-to-end datapack verification, automated validation, collaborative PR to `master`. | Server test harness, linting, promotion to `master`. | **SCHEDULED** | Release PR |

---

## Milestone 1: Static Audit & Registry Standardization
* **Strategic Intent**: Resolve runtime failures caused by Minecraft 1.21 directory breaking changes and missing power registrations.
* **Status**: **COMPLETE** (Merged into `v2.0` via PR #15 / commit `90ff313`).
* **Delivered Artifacts**:
  * Migrated `tags/blocks/` -> `tags/block/` and `tags/items/` -> `tags/item/`.
  * Restored `rustic:dwarf_underground_resistance` and `rustic:dwarf_underground_vision` to `dwarf_powers.json`.
  * Implemented `data/rustic/origins/power/double_ores.json` hooking `data/rustic/loot_table/double_ores.json`.
  * Aligned `farmer_powers.json` to internal `rustic:more_crop_drops`.

---

## Milestone 2: Technical Architecture, Specification & Documentation Base
* **Strategic Intent**: Provide durable, unambiguous specifications for all maintainers, contributors, and server operators so development proceeds without guesswork.
* **Status**: **ACTIVE**
* **Expected Deliverables**:
  1. `docs/Business.md`: Comprehensive gameplay design, economic loops, player roles, and success/failure paths.
  2. `docs/Decision.md`: Complete ADR records (ADR-001 through ADR-006) documenting architectural decisions.
  3. `docs/Milestones.md`: Outcome-based release checkpoints with full issue mapping and acceptance criteria.
  4. `docs/Collaboration.md`: Team collaboration guide, branch hygiene, PR contract, and quality checklist.
  5. `docs/RUSTIC_ORIGINS_SPEC.md`: Exhaustive technical specification for 12 Races and 13+ Classes.
  6. `README.md` & `docs/README.md`: Central documentation entry points with installation instructions.
* **Acceptance Criteria**:
  - [x] All 6 specification documents exist and link to each other cleanly.
  - [x] Every open GitHub issue (#1 through #14) is mapped to an outcome milestone.
  - [x] ADR-006 explicitly enforces the `master` <- `v2.0` <- `feature/*` workflow.
* **Verification**:
  * Markdown link validation and repository audit.

---

## Milestone 3: Combat & RPG Classes Expansion
* **Strategic Intent**: Expand party combat depth in Rustic Craft 2 by introducing high-impact frontline combatants.
* **Status**: **IN PROGRESS**
* **Scope Boundary**: Barbarian class (completed on `feature/barbarian`), Knight class (in progress on `feature/knight`).

### Issue 3.1: Barbarian Class (#1, #2, #3)
* **Status**: **DONE** (Merged into `v2.0` via `feature/barbarian`).
* **Intent**: Provide a berserker combatant who trades sustainability and defense for explosive offensive bursts.
* **Expectation**:
  * Primary active `Rage`: Costs 12 exhaustion, grants Strength II and Resistance I for 10 seconds; inflicts Slowness I and Mining Fatigue I for 5 seconds upon expiration.
  * Secondary active `Aerial Leap`: Launches 1.1 velocity vertical leap, negates fall damage, creates an explosive shockwave upon landing that damages nearby entities by 4 HP and knocks them upward.
  * Passive `Brute Strength`: Grants +1 flat base attack damage, but reduces total armor protection by 30%.
* **Affected Files**:
  * `data/rustic/origins/origin/barbarian.json`
  * `data/rustic/origins/power/barbarian_rage.json`
  * `data/rustic/origins/power/barbarian_aerial_leap.json`
  * `data/rustic/origins/power/barbarian_brute_strength.json`
  * `data/rustic/tags/origins/power/barbarian_powers.json`
  * `data/origins_classes/tags/origins/origin/class.json`

### Issue 3.2: Knight Class & Mighty Dash (#5, #6)
* **Status**: **IN PROGRESS** (Target Branch: `feature/knight`)
* **Intent**: Provide a disciplined armored vanguard who excels in crowd piercing and damage mitigation.
* **Expectation**:
  * Passive `Knight Constitution`: Reduces all damage taken by 15% (`multiply_total: -0.15`).
  * Active `Mighty Dash`: Primary ability launching forward $n$ blocks in horizontal facing direction, detecting entities along the trajectory and applying physical damage.
* **Acceptance Criteria**:
  - [ ] `data/rustic/origins/origin/knight.json` registered in `data/origins_classes/tags/origins/origin/class.json`.
  - [ ] `knight_constitution.json` reduces incoming attack, projectile, and explosion damage by 15%.
  - [ ] `knight_mighty_dash.json` dashes forward with audio cues, particle trail, cooldown indicator, and pierces entities in path.
  - [ ] Tool restrictions: restricted from `butchery:iron_cleaver` and `hearthandharvest:watering_can`.
* **Verification**:
  * Test with standard Origins active keybinding (`key.origins.primary_active`), verify cooldown renders on HUD, verify damage reduction against vanilla attacks.

---

## Milestone 4: Trade & Gathering Classes Porting
* **Strategic Intent**: Complete the vocational crafting ecosystem, porting legacy RC1 jobs and establishing full tool-gating exclusivity.
* **Status**: **SCHEDULED**

### Issue 4.1: Tanner Class (#9)
* **Intent**: Leathercraft and hide extraction specialist.
* **Expectation**: Exclusive animal processing efficiency; hooks `data/rustic/loot_table/entities/tanner_cow.json` for bonus hides, cooked beef, and pelt drops.
* **Files**: `data/rustic/origins/origin/tanner.json`, `data/rustic/origins/power/tanner_*.json`, `data/rustic/tags/origins/power/tanner_powers.json`.

### Issue 4.2: Farrier Class (#11)
* **Intent**: Equine master and breeder (Dinoria horse breeder lore).
* **Expectation**: Passive mount speed buff, extended horse jump height, rapid equine breeding cooldowns, specialized saddle crafting/repair.

### Issue 4.3: Verification of Existing Gathering Classes (#7, #8, #10, #12, #14, #4)
* **Farmer (#7)**: Validate watering can exclusivity, crop aura, and harvest doubling.
* **Blacksmith (#8)**: Validate repair item modifier and thermal damage mitigation.
* **Archivist (#10)**: Validate XP-to-tome transmutation ritual (`archivist_enchantment.json`).
* **Fisherman (#12)**: Validate Luck II passive and treasure fishing table.
* **Nitwit (#14)**: Validate strict tool lockouts from specialized trades.
* **Old Jobs (#4)**: Audit full feature parity against RC1 modpack requirements.

---

## Milestone 5: Staged Origin Races Activation
* **Strategic Intent**: Fully activate the two unfinished racial origins currently staged as empty shells.
* **Status**: **SCHEDULED**

### Issue 5.1: Frostborn (`rustic:frostborn`)
* **Intent**: Arctic predator thriving in sub-zero biomes.
* **Mechanics**: Freezing touch / chill aura, movement speed on snow/ice, immunity to freezing damage, fire vulnerability (+50% fire damage taken).

### Issue 5.2: Vampire (`rustic:vampire`)
* **Intent**: Nocturnal predator with life steal and nocturnal empowerment.
* **Mechanics**: Severe daylight combustion (bypassed only under shadow or heavy helmets), life drain on melee attacks, entity group: Undead, night vision, boosted agility at midnight.

---

## Milestone 6: Verification, Test Harness & v2.0 Release Gate
* **Strategic Intent**: Ensure 100% stable integration before promoting `v2.0` to `master`.
* **Status**: **SCHEDULED**
* **Release Gate Criteria**:
  1. Every JSON file in `data/` passes strict syntax validation.
  2. All power references resolve to actual files.
  3. All tag references in `origin.json` and `class.json` resolve without error.
  4. Server test boot with Minecraft 1.21.1 and Fabric loader yields zero Origins datapack warnings.
  5. Formal Pull Request submitted from `v2.0` into `master` with peer sign-off.
