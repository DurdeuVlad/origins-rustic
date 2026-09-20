# Rustic Origins & Classes — Technical Specification (v2.0)

This document provides the definitive, production-grade technical specification for the **Origins Rustic** datapack running on Minecraft 1.21.1 (`pack_format: 48`) within the **Rustic Craft 2 (`RC2`)** modpack environment.

---

## 1. Architectural System Overview

The system divides character identity into two orthogonal, independently selectable layers:
1. **Origin (Race)**: Biological traits, innate resistances, movement characteristics, and physiological constraints. Defined dynamically via the `#origins:origin` registry tag ([data/origins/tags/origins/origin/origin.json](file:///e:/Github2/origins-rustic/data/origins/tags/origins/origin/origin.json)).
2. **Class (Job)**: Profession, trade skills, crafting bonuses, tool restrictions, and active utility abilities. Defined dynamically via the `#origins_classes:class` registry tag ([data/origins_classes/tags/origins/origin/class.json](file:///e:/Github2/origins_classes/tags/origins/origin/class.json)).

Each origin definition references a power tag under `data/rustic/tags/origins/power/<name>_powers.json`, which bundles discrete power JSON files stored in `data/rustic/origins/power/`.

---

## 2. Races Specification (Origins Layer)

### 2.1 Human (`rustic:human`)
* **Role**: Baseline versatile origin without innate supernatural modifiers.
* **Icon**: `minecraft:apple`
* **Tag**: `#rustic:human_powers`
* **Powers**:
  * Currently empty (`[]`). Designed as a balanced neutral race for standard survival play.

---

### 2.2 Amphibian (`rustic:amphibian`)
* **Role**: Aquatic race excelling in oceanic and river biomes, penalized by terrestrial dehydration.
* **Icon**: `minecraft:turtle_egg`
* **Tag**: `#rustic:amphibian_powers`
* **Powers**:
  * `rustic:amphibian_ignore_water`:
    * Type: `origins:ignore_water`
    * Removes fluid drag and water slowing effects, allowing free traversal in water bodies.
  * `rustic:amphibian_water_regen`:
    * Type: `origins:action_over_time` (Interval: 40 ticks / 2s)
    * Condition: Submerged in water (`origins:submerged_in`, fluid: `minecraft:water`).
    * Action: Applies `minecraft:regeneration` (Amplifier: 0, Duration: 60 ticks).
  * `rustic:amphibian_dry_weakness`:
    * Type: `origins:action_over_time` (Interval: 60 ticks / 3s)
    * Condition: Not in water and not in rain (`origins:in_rain` inverted, `origins:submerged_in` inverted).
    * Action: Applies `minecraft:slowness` (Amplifier: 0, Duration: 80 ticks).

---

### 2.3 Arachnid (`rustic:arachnid`)
* **Role**: Agile subterranean predator capable of vertical traversal and drop dampening.
* **Icon**: `minecraft:cobweb`
* **Tag**: `#rustic:arachnid_powers`
* **Powers**:
  * `rustic:arachnid_climbing`:
    * Type: `origins:climbing`
    * Allows free vertical climbing when colliding horizontally with walls.
  * `rustic:arachnid_fall_resist`:
    * Type: `origins:modify_damage_taken`
    * Condition: Damage type is `origins:fall`.
    * Modifier: Multiplies fall damage by `-0.6` (60% damage reduction on falling).

---

### 2.4 Automaton (`rustic:automaton`)
* **Role**: Mechanical construct sustained by metals rather than organic food, lacking natural biological regeneration.
* **Icon**: `minecraft:iron_ingot`
* **Tag**: `#rustic:automaton_powers`
* **Powers**:
  * `rustic:automaton_no_regen`:
    * Type: `origins:disable_regen`
    * Completely suppresses natural health regeneration from high saturation.
  * `rustic:automaton_armor`:
    * Type: `origins:attribute`
    * Attribute: `minecraft:generic.armor` | Value: `+4.0` (flat innate natural armor).
  * `rustic:automaton_copper_feed`:
    * Type: `origins:edible_item`
    * Item: `minecraft:copper_ingot`
    * Restores 4 hunger points and 2.0 saturation upon consumption.
  * `rustic:automaton_iron_repair`:
    * Type: `origins:edible_item`
    * Item: `minecraft:iron_ingot`
    * Restores 6 health points (3 hearts) instantly upon consumption.

---

### 2.5 Dwarf (`rustic:dwarf`)
* **Role**: Subterranean miner and builder thriving below ground with natural resilience, dark vision, and pickaxe synergy.
* **Icon**: `minecraft:gold_ingot`
* **Tag**: `#rustic:dwarf_powers`
* **Powers**:
  * `rustic:dwarf_pickaxe_haste`:
    * Type: `origins:action_over_time` (Interval: 20 ticks / 1s)
    * Condition: Mainhand item is in tag `minecraft:pickaxes`.
    * Action: Applies `minecraft:haste` (Amplifier: 0, Duration: 40 ticks, no particles). Continuous Haste I while wielding pickaxes.
  * `rustic:dwarf_underground_resistance`:
    * Type: `origins:action_over_time` (Interval: 20 ticks)
    * Condition: `origins:distance_from_coordinates` (Offset $Y = -64$, comparison $\le 124$, equivalent to entity $Y \le 60$).
    * Action: Applies `minecraft:resistance` (Amplifier: 1 / Resistance II, Duration: 40 ticks).
  * `rustic:dwarf_underground_vision`:
    * Type: `origins:night_vision`
    * Strength: 1.0 (full brightness).
    * Condition: Entity $Y \le 60$.

---

### 2.6 Dragonborn (`rustic:dragonborn`)
* **Role**: Draconic descendant with innate fire resistance and short-burst flight capabilities.
* **Icon**: `minecraft:dragon_breath`
* **Tag**: `#rustic:dragonborn_powers`
* **Powers**:
  * `rustic:dragonborn_resistance`:
    * Type: `origins:action_over_time`
    * Condition: Entity in fire or lava.
    * Action: Applies `minecraft:fire_resistance` (Duration: 60 ticks).
  * `rustic:dragonborn_flight`:
    * Type: `origins:multiple`
    * Bundles elytra flight capability toggled via Primary Active key (`key.origins.primary_active`).
    * Includes `prevent_firework` (`origins:prevent_item_use`): Prevents boosting with `minecraft:firework_rocket` while `origins:fall_flying` to eliminate infinite flight exploitation.

---

### 2.7 Enderian (`rustic:enderian`)
* **Role**: Teleportation specialist sensitive to aqueous dissolution.
* **Icon**: `minecraft:ender_pearl`
* **Tag**: `#rustic:enderian_powers`
* **Powers**:
  * `rustic:weakness_water`:
    * Type: `origins:action_over_time` (Interval: 20 ticks)
    * Condition: Submerged in water or standing in rain.
    * Action: Damages player by 1.0 HP (half heart) every second.
  * `origins:throw_ender_pearl`:
    * Built-in pearl throwing on primary active keybind without consuming items.
  * `origins:extra_reach`:
    * Inherent +0.5 block reach advantage.
  * `origins:ender_particles`:
    * Passive ambient particle trail.

---

### 2.8 Phantom (`rustic:phantom`)
* **Role**: Ethereal stalker capable of passing through solid matter at the expense of physical frailty.
* **Icon**: `minecraft:phantom_membrane`
* **Tag**: `#rustic:phantom_powers`
* **Powers**:
  * `origins:phantomize`: Phasing toggle converting player into intangible state.
  * `origins:translucent`: Renders player body semi-transparent.
  * `origins:fragile`: Reduces maximum health by 3 hearts (-6 HP).
  * `origins:phantomize_overlay`: Visual shader while in phantom form.
  * `rustic:phantom_phasing`: Custom block-collision bypass logic while phantomized.
  * *Unassigned Staged Powers*: [phantom_dodge.json](file:///e:/Github2/origins-rustic/data/rustic/origins/power/phantom_dodge.json) (30% melee dodge), [phantom_no_fall_damage.json](file:///e:/Github2/origins-rustic/data/rustic/origins/power/phantom_no_fall_damage.json), [phantom_prevent_targeting_when_phantom.json](file:///e:/Github2/origins-rustic/data/rustic/origins/power/phantom_prevent_targeting_when_phantom.json), [phantom_slow_falling.json](file:///e:/Github2/origins-rustic/data/rustic/origins/power/phantom_slow_falling.json).

---

### 2.9 Sylvan (`rustic:sylvan`)
* **Role**: Nature guardian thriving in canopy biomes.
* **Icon**: `minecraft:oak_sapling`
* **Tag**: `#rustic:sylvan_powers`
* **Powers**:
  * `rustic:sylvan_forest_speed`:
    * Type: `origins:conditioned_attribute`
    * Attribute: `minecraft:generic.movement_speed`
    * Operation: `add_multiplied_base` | Value: `+0.30` (+30% base speed)
    * Condition: Entity in biome tagged `#minecraft:is_forest`.

---

### 2.10 Undead (`rustic:undead`)
* **Role**: Necrotic entity immune to toxins and negative potions, nourished exclusively by rotten flesh and flesh-based foods.
* **Icon**: `minecraft:bone`
* **Tag**: `#rustic:undead_powers`
* **Powers**:
  * `rustic:weakness_sun`: Burns under open daylight unless sheltered or wearing a helmet.
  * `rustic:undead_less_health`: -4 HP max health penalty.
  * `rustic:undead_enhanced_food`: Multiplies nutritional yield from food items in `#rustic:undead_food` (Rotten Flesh, Spider Eyes).
  * `rustic:undead_food_heal`: Consuming rotten flesh directly heals 2 hearts.
  * `rustic:undead_poison_immunity`: Grants immunity to `minecraft:poison` and `minecraft:hunger` via `origins:effect_immunity`.
  * `rustic:undead_harming_immunity`: Grants immunity to Instant Damage (`minecraft:instant_damage`) via `origins:effect_immunity`.

---

### 2.11 Frostborn (`rustic:frostborn`)
* **Role**: Arctic predator and environmental specialist thriving in sub-zero biomes, highly vulnerable to thermal hazards and fire.
* **Icon**: `minecraft:packed_ice`
* **Tag**: `#rustic:frostborn_powers`
* **Mechanics**:
  * `rustic:frostborn_cold_buffs`: Continuous Strength I and Speed I while in `#minecraft:is_cold` biomes.
  * `rustic:frostborn_glacial_aura`: Key G primary active (400t cooldown). Targets enemy players within 8m, applying 140 TicksFrozen (~7s freeze) and Blindness II (5s).
  * `rustic:frostborn_fire_vulnerability`: +75% incoming damage from fire, lava, and fireballs (1.75x multiplier).
  * `rustic:frostborn_weakness_fire`: Weakness I while standing in/on fire or soul fire.
  * `rustic:frostborn_weakness_campfire`: Weakness II while standing on/near a lit campfire.
  * `rustic:frostborn_weakness_lava`: Weakness III while standing on or submerged in lava.
  * `rustic:frostborn_heat_resource`: Heat saturation gauge (0-100) rendered on the HUD.
  * `rustic:frostborn_heat_fill`: +2 heat every 10t when exposed to heat sources without ice in inventory (fills in ~25s).
  * `rustic:frostborn_heat_cooldown`: -1 heat every 10t when away from heat sources (drains in ~50s).
  * `rustic:frostborn_heat_damage`: Deals 2.0 HP every 40t (2s) via `rustic:frostborn_overheat` when heat reaches 100%.
  * `rustic:frostborn_ice_coolant`: Consumes 1 item from `#rustic:ice_items` every 400t (20s) while over heat to pause overheat buildup.

---

### 2.12 Vampire (`rustic:vampire`)
* **Status**: Empty power definitions (`"powers": []`) staged for full porting in Milestone 5.2.
* **Vampire Prototype**: Daylight combustion, life drain on attack, entity group: undead, night speed/attack buffs.

---

## 3. Classes Specification (Jobs Layer)

The system includes 11 active classes registered in `#origins_classes:class`.

### 3.1 Nitwit (`rustic:nitwit`)
* **Role**: Unskilled laborer without economic specialization.
* **Icon**: `minecraft:poisonous_potato`
* **Tag**: `#rustic:nitwit_powers` (empty)
* **Restrictions**: Enforced server-side via KubeJS (`OriginsJS.hasOrigin(player, 'rustic:nitwit')`), preventing usage of `hearthandharvest:watering_can` and `butchery:iron_cleaver`.

---

### 3.2 Blacksmith (`rustic:blacksmith`)
* **Role**: Metallurgy master specializing in tool repair, thermal tolerance, and gear crafting.
* **Icon**: `minecraft:anvil`
* **Tag**: `#rustic:blacksmith_powers`
* **Powers**:
  * `rustic:blacksmith_fire_resist`: -50% damage taken from fire and lava sources (`multiply_base_multiplicative: -0.5`).
  * Integrated Item Modifiers: Custom repair rates in [item_repair.json](file:///e:/Github2/origins-rustic/data/rustic/item_modifier/item_repair.json) and blacksmith equipment modifiers in `data/rustic/item_modifier/blacksmith/`.

---

### 3.3 Farmer (`rustic:farmer`)
* **Role**: Agricultural specialist with exclusive watering can access, proximity movement speed, and doubled harvest yields.
* **Icon**: `minecraft:wheat`
* **Tag**: `#rustic:farmer_powers`
* **Powers**:
  * `rustic:farmer_crop_speed`: Applies Speed I continuously while within 4 blocks of `#minecraft:crops`.
  * `rustic:farmer_double_wheat`: Replaces `minecraft:blocks/wheat` loot table with 2x drop table `rustic:farmer_wheat`.
  * `rustic:farmer_double_carrots`: Replaces `minecraft:blocks/carrots` loot table with 2x drop table `rustic:farmer_carrots`.
  * `rustic:farmer_double_potatoes`: Replaces `minecraft:blocks/potatoes` loot table with 2x drop table `rustic:farmer_potatoes`.
  * `rustic:farmer_double_beetroots`: Replaces `minecraft:blocks/beetroots` loot table with 2x drop table `rustic:farmer_beetroots`.
  * `rustic:farmer_double_nether_wart`: Replaces `minecraft:blocks/nether_wart` loot table with 2x drop table `rustic:farmer_nether_wart`.
  * `rustic:farmer_double_cocoa`: Replaces `minecraft:blocks/cocoa` loot table with 2x drop table `rustic:farmer_cocoa`.

---

### 3.4 Fisherman (`rustic:fisherman`)
* **Role**: Skilled angler capable of pulling valuable treasures from open waters.
* **Icon**: `minecraft:fishing_rod`
* **Tag**: `#rustic:fisherman_powers`
* **Powers**:
  * `rustic:fisherman_fishing`: Applies Luck II continuously while holding a fishing rod in mainhand or offhand.
  * `rustic:fisherman_more_treasure`: Replaces `minecraft:gameplay/fishing` with `rustic:gameplay/fishing` loot table.

---

### 3.5 Lumberjack (`rustic:lumberjack`)
* **Role**: Forestry laborer with rapid wood harvesting and higher plank yields.
* **Icon**: `minecraft:iron_axe`
* **Tag**: `#rustic:lumberjack_powers`
* **Powers**:
  * `origins_classes:tree_felling`: Fells entire tree column when chopping with an axe.
  * `rustic:lumber_bonus_wood`: Recipe replacements yielding 6 planks per log instead of standard 4.
  * Overrides `data/origins_classes/item_modifier/lumberjack/craft_plank.json`.

---

### 3.6 Mason (`rustic:mason`)
* **Role**: Stonecutter and fortress builder with extended block manipulation and stone mobility.
* **Icon**: `minecraft:white_glazed_terracotta`
* **Tag**: `#rustic:mason_powers`
* **Powers**:
  * `rustic:mason_block_reach`: +1.5 blocks placing/breaking reach.
  * `rustic:mason_break_speed`: +30% mining speed on stone.
  * `rustic:mason_jump_boost`: Enhanced vertical jump when standing on masonry blocks.

---

### 3.7 Miner (`rustic:miner`)
* **Role**: Deep excavator with extreme stamina efficiency and high stone break speed.
* **Icon**: `minecraft:iron_pickaxe`
* **Tag**: `#rustic:miner_powers`
* **Powers**:
  * `rustic:no_mining_exhaustion`: -50% exhaustion across all actions (`multiply_base_multiplicative: -0.5`).
  * `rustic:more_stone_break_speed`: 2x break speed (`+100%`) when hitting blocks in `#rustic:stone`.

---

### 3.8 Archivist (`rustic:archivist`)
* **Role**: Scholar capable of transmuting experience and blank tomes into enchanted codices.
* **Icon**: `minecraft:bookshelf`
* **Tag**: `#rustic:archivist_powers`
* **Powers**:
  * `rustic:archivist_enchantments`: Active right-click ritual (`key.use`) while holding a book with $\ge 5$ XP levels. Deducts 5 levels, plays enchantment audio/particles, and rolls [archivist_enchantment.json](file:///e:/Github2/origins-rustic/data/rustic/loot_table/generic/archivist_enchantment.json).

---

### 3.9 Explorer (`rustic:explorer`)
* **Role**: Long-distance scout with high stamina efficiency and terrain scaling.
* **Icon**: `minecraft:compass`
* **Tag**: `#rustic:explorer_powers`
* **Powers**:
  * `rustic:explorer_stamina`: -30% exhaustion gained while sprinting.
  * `rustic:explorer_climbers_step`: Step height increased to 1.0 block (walk up full blocks without jumping).
  * `rustic:explorer_campfire_rest`: Passive Regeneration I while resting within 5 blocks of an active campfire.

---

### 3.10 Salahor (`rustic:salahor`)
* **Role**: Colossal titan class designed for high durability and heavy crowd control at the cost of speed.
* **Icon**: `minecraft:iron_block`
* **Tag**: `#rustic:salahor_powers`
* **Powers**:
  * `rustic:salahor_size`: Scales entity model scale to 1.25x.
  * `rustic:salahor_health`: +20 Max Health (+10 hearts).
  * `rustic:salahor_reach`: +1.0 block attack and interaction reach.
  * `rustic:salahor_crushing_grip`: +3.0 melee attack damage.
  * `rustic:salahor_unmoving`: 100% knockback resistance.
  * `rustic:salahor_heavy_steps`: -20% movement speed penalty.

---

### 3.11 Farrier (`rustic:farrier`)
* **Role**: Equine master and breeder (Dinoria horse breeder).
* **Icon**: `minecraft:saddle`
* **Tag**: `#rustic:farrier_powers`
* **Powers**:
  * `rustic:farrier_mounted_speed`: Mounted movement speed aura.
  * `rustic:farrier_mount_jump`: Extended horse jump height.
  * `rustic:farrier_equine_care`: Passive health recovery for mounts.


---

## 4. Tag Registries Map (1.21 Singular Conventions)

| Tag Path | Registry | Usage |
| :--- | :--- | :--- |
| `data/rustic/tags/block/stone.json` | `minecraft:block` | Stone blocks triggering Miner double break speed. |
| `data/rustic/tags/block/crops_all.json` | `minecraft:block` | All crop types recognized by Farmer. |
| `data/rustic/tags/item/heavy_armor.json` | `minecraft:item` | Restricts Dragonborn flight and applies speed penalties. |
| `data/rustic/tags/item/light_weapons.json` | `minecraft:item` | Agile weapons (daggers, rapiers, shortswords). |
| `data/rustic/tags/item/heavy_weapons.json` | `minecraft:item` | Two-handed greatswords, polearms, halberds. |
| `data/rustic/tags/item/banned_items.json` | `minecraft:item` | Restricted high-tier or overpowered gear. |
| `data/rustic/tags/item/undead_food.json` | `minecraft:item` | Organic/flesh foods that provide nutrition to Undead. |
| `data/rustic/tags/origins/power/*.json` | `origins:power` | Power grouping tags for Origins and Classes. |
