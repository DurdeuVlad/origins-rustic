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
| **M5: Staged Origin Races Activation** | Fully implement Frostborn and Vampire from staged prototypes into playable origins. | `data/rustic/origins/origin/frostborn.json`, `vampire.json`, associated powers & tags. | **IN PROGRESS** | #22 (Frostborn), Vampire |
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

* **Strategic Intent**: Introduce tactical party combat roles for Rustic Craft 2 by implementing high-impact frontline combatants with balanced active cooldowns and trade-offs.
* **Status**: **IN PROGRESS**
* **Scope Boundary**: Barbarian class (Issues #1, #2, #3), Knight class (Issues #5, #6).

### Issue #1: Barbarian Class (`class`)
* **Title**: Barbarian Class
* **Status**: **DONE** (Implemented on `feature/barbarian`, merged into `v2.0`).
* **Intent**: Provide a berserker combatant who trades sustainability and defense for explosive offensive bursts.
* **Expectation**:
  * Selectable in Origins: Classes selection screen.
  * Grants primary active `Rage` (`rustic:barbarian_rage`), secondary active `Aerial Leap` (`rustic:barbarian_aerial_leap`), and passive `Brute Strength` (`rustic:barbarian_brute_strength`).
  * Restricted from specialized trade tools (`rustic:prevent_cleaver`, `rustic:prevent_watering_can`).
* **Acceptance Criteria**:
  - [x] Registered in `data/origins_classes/tags/origins/origin/class.json`.
  - [x] Origin file `data/rustic/origins/origin/barbarian.json` references `#rustic:barbarian_powers`.
  - [x] Tag `data/rustic/tags/origins/power/barbarian_powers.json` contains all 5 power entries.
* **Verification**: Verify class appears in selection screen; powers trigger on configured keybinds.

### Issue #2: Barbarian - Aerial Leap (`power`)
* **Title**: Barbarian - Aerial Leap
* **Status**: **DONE** (Implemented on `feature/barbarian`, merged into `v2.0`).
* **Intent**: Give Barbarians vertical mobility and initiating crowd control.
* **Expectation**:
  * Triggered via secondary active keybind (`key.origins.secondary_active`).
  * Launches player into the air ($Y$ velocity $+1.1$), plays wind burst sound, negates all fall damage.
  * Upon landing, creates an explosive shockwave dealing 4 HP generic damage and launching all entities within 5 blocks into the air. Cooldown: 300 ticks (15s).
* **Acceptance Criteria**:
  - [x] Vertical launch velocity triggers consistently when grounded.
  - [x] Fall damage negated during leap.
  - [x] Landing triggers shockwave sound, explosion particle, 4 HP damage, and vertical displacement.
  - [x] Cooldown bar renders on HUD with 300 ticks.
* **Verification**: In-game execution and landing next to test mobs.

### Issue #3: Barbarian - Rage (`power`)
* **Title**: Barbarian - Rage
* **Status**: **DONE** (Implemented on `feature/barbarian`, merged into `v2.0`).
* **Intent**: Berserker damage surge at the expense of severe hunger and post-rage exhaustion.
* **Expectation**:
  * Triggered via primary active keybind (`key.origins.primary_active`).
  * Costs 12.0 exhaustion. Grants Strength II and Resistance I for 200 ticks (10s).
  * Plays ravager roar and angry villager particles.
  * Delayed by 200 ticks: applies Slowness I (100 ticks / 5s) and Mining Fatigue I (100 ticks / 5s). Cooldown: 600 ticks (30s).
* **Acceptance Criteria**:
  - [x] Consumes 12.0 exhaustion immediately.
  - [x] Strength II and Resistance I applied for exactly 10s.
  - [x] Slowness I and Mining Fatigue I applied immediately upon buff expiration for 5s.
  - [x] 30-second cooldown displayed on HUD.
* **Verification**: Inspect active potion effects and timing in client HUD.

### Issue #5: Knight Class (`class`)
* **Title**: Knight Class
* **Status**: **IN PROGRESS** (Target Branch: `feature/knight`).
* **Intent**: Provide a disciplined armored vanguard who excels in damage mitigation and crowd piercing.
* **Expectation**:
  * Selectable in Origins: Classes GUI with icon `minecraft:iron_chestplate`.
  * Possesses passive damage mitigation `Knight Constitution` and active dash `Mighty Dash`.
  * Restricted from `butchery:iron_cleaver` and `hearthandharvest:watering_can`.
* **Acceptance Criteria**:
  - [ ] `data/rustic/origins/origin/knight.json` created and added to `class.json`.
  - [ ] `#rustic:knight_powers` registered with constitution, dash, and tool restrictions.
* **Verification**: Class selection test in-game.

### Issue #6: Knight - Mighty Leap / Mighty Dash (`power`)
* **Title**: Knight - Mighty Dash
* **Status**: **IN PROGRESS** (Target Branch: `feature/knight`).
* **Intent**: Tactical vanguard gap-closer that damages and breaches enemy lines.
* **Expectation**:
  * Triggered via primary active keybind (`key.origins.primary_active`).
  * Launches the player forward horizontally in facing direction for $n$ blocks.
  * Detects intervening entities in trajectory and deals physical damage.
  * Plays armor clatter audio and sweep particles. Cooldown: 200 ticks (10s).
* **Acceptance Criteria**:
  - [ ] Horizontal dash impulse applied along facing vector without launching excessively into the air.
  - [ ] Detects and damages entities within dash collision box.
  - [ ] Cooldown indicator renders cleanly on HUD.
* **Verification**: Target dummy collision testing in-game.

---

## Milestone 4: Trade & Gathering Classes Porting

* **Strategic Intent**: Complete the vocational crafting ecosystem, porting legacy RC1 jobs and establishing full tool-gating exclusivity.
* **Status**: **SCHEDULED**

### Issue #4: Old Jobs (`class`)
* **Title**: Old Jobs Porting & Verification
* **Status**: **SCHEDULED**
* **Intent**: Verify that all legacy job classes from RC1 function reliably in RC2 on Minecraft 1.21.1.
* **Expectation**:
  * Full audit of Sylvan, Dwarf, Miner, Farmer, Lumberjack, Mason, Archivist, Explorer, Salahor, Fisherman, Fisher, and Herbalist.
  * Confirm all tool restrictions, loot tables, and potion auras resolve without console warnings.
* **Acceptance Criteria**:
  - [ ] All 12 base classes load and display localized badges in Origins GUI.
  - [ ] Zero missing tag warnings in server logs during `/reload`.

### Issue #7: Farmer Class (`class`)
* **Title**: Farmer Class Verification & Tool Exclusivity
* **Status**: **SCHEDULED**
* **Intent**: Agricultural specialist with exclusive watering can access, speed near crops, and double harvests.
* **Expectation**:
  * Exclusive permission for `hearthandharvest:watering_can`.
  * Applies Speed I within 4 blocks of `#minecraft:crops`.
  * Replaces wheat loot table with `rustic:farmer_wheat` and 2x crop drops via `rustic:more_crop_drops`.
* **Acceptance Criteria**:
  - [ ] Non-farmers cannot use watering can.
  - [ ] Breaking mature wheat yields doubled crops.
  - [ ] Speed I buff applies only when within 4 blocks of crops.

### Issue #8: Blacksmith Class (`class`)
* **Title**: Blacksmith Class & Gear Maintenance
* **Status**: **SCHEDULED**
* **Intent**: Metallurgy master with fire resistance and superior tool restoration.
* **Expectation**:
  * -50% fire and lava damage taken (`rustic:blacksmith_fire_resist`).
  * Enhanced repair rates via `data/rustic/item_modifier/item_repair.json`.
  * Exclusive access to blacksmith equipment modifiers.
* **Acceptance Criteria**:
  - [ ] Lava/fire damage verified at 50% reduction.
  - [ ] Repair rates match RC2 design specifications.

### Issue #9: Tanner Class (`class`)
* **Title**: Tanner Class
* **Status**: **SCHEDULED**
* **Intent**: Leatherworking artisan specializing in hide processing and high-yield livestock processing.
* **Expectation**:
  * Allowed to wield `butchery:iron_cleaver`.
  * Hooks `data/rustic/loot_table/entities/tanner_cow.json` for 1-3 bonus leather and fire-smelted beef.
* **Acceptance Criteria**:
  - [ ] `data/rustic/origins/origin/tanner.json` registered in `class.json`.
  - [ ] Killing cows yields bonus leather and cooked beef per loot table.
  - [ ] Permitted to use butchery cleaver without actionbar cancellation.

### Issue #10: Archivist Class (`class`)
* **Title**: Archivist Class & Enchantment Ritual
* **Status**: **SCHEDULED**
* **Intent**: Scholar capable of transmuting experience levels and blank books into enchanted codices.
* **Expectation**:
  * Active ritual (`key.use` with book and $\ge 5$ XP levels).
  * Deducts 5 levels and rolls `data/rustic/loot_table/generic/archivist_enchantment.json`.
* **Acceptance Criteria**:
  - [ ] XP check strictly enforces $\ge 5$ levels.
  - [ ] Deducts 5 levels and replaces held book with rolled enchanted book.
  - [ ] Plays enchantment sound and particle surge.

### Issue #11: Farrier Class (`class`)
* **Title**: Farrier Class (Dinoria Horse Breeder)
* **Status**: **SCHEDULED**
* **Intent**: Equine master specializing in horse breeding, mount agility, and saddle maintenance.
* **Expectation**:
  * Passive mount speed boost and extended horse jump height.
  * Reduced breeding cooldowns on horses.
  * Restricted from `butchery:iron_cleaver` and `hearthandharvest:watering_can`.
* **Acceptance Criteria**:
  - [ ] `data/rustic/origins/origin/farrier.json` registered in `class.json`.
  - [ ] Mounted player observes increased mount speed attribute.

### Issue #12: Fisherman Class (`class`)
* **Title**: Fisherman Class & Treasure Fishing
* **Status**: **SCHEDULED**
* **Intent**: Master angler with Luck II and custom treasure loot tables.
* **Expectation**:
  * Applies Luck II while holding fishing rod in mainhand or offhand.
  * Replaces `minecraft:gameplay/fishing` with `rustic:gameplay/fishing`.
* **Acceptance Criteria**:
  - [ ] Holding fishing rod grants Luck II icon on HUD.
  - [ ] Fishing loot rolls match `rustic:gameplay/fishing`.

### Issue #14: Nitwit Class (`class`)
* **Title**: Nitwit Class & Tool Lockouts
* **Status**: **SCHEDULED**
* **Intent**: Unskilled laborer restricted from specialized trade tools to prevent bypass of vocational economy.
* **Expectation**:
  * Restricted from `butchery:iron_cleaver` and `hearthandharvest:watering_can`.
  * Receives clear actionbar feedback when attempting restricted item use.
* **Acceptance Criteria**:
  - [ ] Attempting to use cleaver or watering can displays error notice.
  - [ ] Items are never destroyed or deleted.

---

## Milestone 5: Staged Origin Races Activation
* **Strategic Intent**: Fully activate the two unfinished racial origins currently staged as empty shells.
* **Status**: **IN PROGRESS**

### Issue 5.1: Frostborn (`rustic:frostborn` / Issue #22)
* **Title**: Frostborn Class / Origin Activation
* **Status**: **DONE** (Implemented on `feature/frostborn`)
* **Intent**: Arctic predator thriving in sub-zero biomes, vulnerable to thermal hazards.
* **Expectation**:
  * Innate race selectable in Origins selection screen with icon `minecraft:packed_ice`.
  * Grants Glacial Might (Strength I & Speed I in cold biomes `#minecraft:is_cold`).
  * Grants Glacial Aura (Key G, 20s cooldown, 140-tick freeze & Blindness II to enemy players within 8m).
  * Molten Weakness (+75% fire/lava damage taken).
  * Heat Weakness tiered debuffs (Weakness I on fire, II on campfire, III in lava).
  * Overheat system (0–100 HUD bar, fills in heat without ice, deals 2.0 HP damage at 100 via `rustic:frostborn_overheat`, drains away from heat).
  * Ice Coolant (consumes 1 ice item from `#rustic:ice_items` every 20s to pause heat buildup).
* **Acceptance Criteria**:
  - [x] Origin `data/rustic/origins/origin/frostborn.json` references `#rustic:frostborn_powers`.
  - [x] Tag `data/rustic/tags/origins/power/frostborn_powers.json` contains all 11 power entries.
  - [x] Tag `data/rustic/tags/item/ice_items.json` contains ice, packed ice, and blue ice.
  - [x] Custom damage type `data/rustic/damage_type/frostborn_overheat.json` registered.
  - [x] Complete localization in `assets/rustic/lang/en_us.json` including power names, descriptions, and death messages.

### Issue 5.2: Vampire (`rustic:vampire`)
* **Intent**: Nocturnal predator with life steal and nocturnal empowerment.
* **Mechanics**: Severe daylight combustion (bypassed only under shadow or heavy helmets), life drain on melee attacks, entity group: Undead, night vision, boosted agility at midnight.
* **Status**: **SCHEDULED**

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
