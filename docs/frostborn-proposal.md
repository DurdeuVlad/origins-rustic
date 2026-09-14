# Frostborn (`rustic:frostborn`) — Origin Power Set Proposal

## 1. Overview & Context

`data/rustic/origins/origin/frostborn.json` is currently an unpopulated stub (`"powers": []`) with icon `minecraft:packed_ice`. The high-level direction from Milestone 5 calls for an *arctic predator / elemental spirit thriving in sub-zero biomes with severe vulnerability to extreme heat and fire*.

### Architectural Alignment with Existing Origins
Origins in **Rustic Origins v2.0** typically feature **3 to 5 discrete powers** balancing identity, thematic mobility/utility, combat synergy, and an authentic physiological penalty:
- **Dragonborn (`rustic:dragonborn`)**: Fire immunity passive + unarmored Elytra burst flight with hunger drain + firework boost lockout (2 powers / 4 subpowers).
- **Amphibian (`rustic:amphibian`)**: Water friction bypass + underwater health regeneration + dry land slowness/weakness (3 powers).
- **Dwarf (`rustic:dwarf`)**: Pickaxe Haste I + subterranean Resistance II + deep-cave Night Vision (3 powers).
- **Undead (`rustic:undead`)**: Daylight sunburn + rotten flesh healing/nutrition + poison/harming immunity + reduced max HP (6 powers).

Following this design language, Frostborn should avoid feature creep and instead present **a cohesive 3-to-4 power package**: 1 mobility/environment passive, 1 cold-climate empowerment perk, 1 active ability or combat modifier, and 1 thermal vulnerability penalty.

---

## 2. Candidate Power Concepts

Below are 5 candidate powers designed to fit the existing Origins 1.21.1 / NeoForge data-driven schema. A final Frostborn power set would select **3 or 4** of these.

### Candidate 1: Pasul Ghețarului (Glacial Strider)
* **Theme**: Effortless locomotion across arctic terrain and frozen waterways.
* **Mechanics**:
  - Traversal over water temporarily freezes the surface into frosted ice under the player's feet (Frost Walker equivalent).
  - Immunity to sliding friction on ice/packed ice/blue ice (normal sprint traction).
  - Immunity to sinking and freezing within powdered snow blocks (acts like leather boots).
* **Origins Technical Mapping**:
  - Type: `origins:multiple` bundling:
    - `origins:walk_on_fluid` (fluid: `minecraft:water`, modifies surface to temporary frost).
    - `origins:modify_movement_speed` or `origins:ignore_water`.
    - `origins:prevent_block_selection` / powder snow bypass condition.
* **Design Verdict**: Essential baseline trait; establishes immediate physical difference without combat bloating.

---

### Candidate 2: Vigoarea Crivățului (Arctic Resilience)
* **Theme**: Physiological empowerment when immersed in natural cold.
* **Mechanics**:
  - While located in freezing biomes (biomes with temperature $< 0.15$ or tagged `#minecraft:is_freezing` / `#c:is_snowy`) or during snowstorms:
    - Grants continuous **Resistance I** and slow **Regeneration I** (1 HP every 3 seconds).
  - Complete immunity to freezing environment damage (`origins:freeze` immunity).
* **Origins Technical Mapping**:
  - Type: `origins:action_over_time` (Interval: 40 ticks).
  - Condition: `origins:and` checking `origins:biome` (`#minecraft:is_freezing`) or `origins:in_snow`.
  - Action: Applies `minecraft:regeneration` (40 ticks, amp 0) and `minecraft:resistance` (40 ticks, amp 0).
* **Design Verdict**: Mirror of Amphibian's `amphibian_water_regen` or Dwarf's `dwarf_underground_resistance`; rewards players for establishing bases in arctic climates.

---

### Candidate 3: Atingerea Gerului (Frostbite Strike)
* **Theme**: Attacks chill victims to the bone, numbing their reflexes.
* **Mechanics**:
  - Melee attacks against living entities apply **Slowness II** for 3 seconds (60 ticks) and inflict 100 freeze ticks (powder snow freeze vignette).
  - Has a built-in internal trigger cooldown (e.g. 4 seconds) to avoid perma-stunning targets in PvP.
* **Origins Technical Mapping**:
  - Type: `origins:target_action_on_hit`.
  - Target Action: `origins:and` with:
    - `origins:apply_effect` (`minecraft:slowness`, duration: 60, amplifier: 1).
    - `origins:freeze` (amount: 100).
  - Cooldown: 80 ticks (4s) with HUD indicator or hidden cooldown.
* **Design Verdict**: High-impact combat identity for party-based combat in Rustic Craft 2.

---

### Candidate 4: Viscolul / Valul de Gheață (Cryo Burst / Frost Nova)
* **Theme**: Active tactical ability releasing a wave of sub-zero wind.
* **Mechanics**:
  - Triggered with Primary Ability key (`key.origins.primary_active`).
  - Instantly extinguishes fire on the user.
  - Emits an icy shockwave in a 4-block radius:
    - Knocks back surrounding hostile entities.
    - Applies Slowness III and Weakness I for 5 seconds to nearby enemies.
    - Displays snow puff / cloud particles and plays `minecraft:entity.player.hurt_freeze` audio.
  - Cooldown: 400 ticks (20s) with a visible HUD cooldown bar.
* **Origins Technical Mapping**:
  - Type: `origins:active_self`.
  - Cooldown: 400 ticks with `hud_render: {"should_render": true, "bar_index": 6}`.
  - Entity Action: `origins:and` with `origins:extinguish` + `origins:area_of_effect` (radius 4.0) executing `origins:apply_effect` and `origins:add_velocity`.
* **Design Verdict**: Gives Frostborn an active button press matching Dragonborn's flight toggle and Farrier's Equine Care.

---

### Candidate 5: Topirea Stihiei (Thermal Meltdown) — *Mandatory Drawback*
* **Theme**: Vulnerability to intense heat, flames, and arid environments.
* **Mechanics**:
  - **Fire Vulnerability**: Suffers +60% increased damage from all fire, lava, and blaze fireballs.
  - **Heat Exhaustion**: While in hot biomes (temperature $> 1.0$, e.g. deserts, badlands, savanna, or the Nether):
    - Suffers constant **Slowness I**.
    - Hunger depletion rate is doubled (+100% exhaustion rate).
* **Origins Technical Mapping**:
  - Type: `origins:multiple` bundling:
    - `vulnerability`: `origins:modify_damage_taken` (damage condition: fire/lava, modifier: +0.6 add_multiplied_base).
    - `heat_penalty`: `origins:action_over_time` (condition: biome `#minecraft:is_hot` or dimension `minecraft:the_nether`, action: `origins:apply_effect` Slowness I + `origins:exhaust`).
* **Design Verdict**: Necessary balancing counterweight. Without severe heat penalties, Frostborn becomes strictly superior to Human.

---

## 3. Recommended 4-Power Loadout

For a balanced, production-ready implementation, we recommend selecting:
1. **Pasul Ghețarului (Glacial Strider)** — Passive traversal & powder snow immunity.
2. **Vigoarea Crivățului (Arctic Resilience)** — Cold biome regen/resistance perk.
3. **Viscolul (Cryo Burst)** — Active primary keybind ability on 20s cooldown.
4. **Topirea Stihiei (Thermal Meltdown)** — Severe fire damage and hot biome penalty.

*Zero JSON code has been implemented in `data/` pending human review and sign-off on this proposal.*
