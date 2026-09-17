# Origins — Repair Reference

---

## Sylvan

Tag: `#rustic:sylvan_powers` → `data/rustic/tags/origins/power/sylvan_powers.json`

### `rustic:sylvan_forest_speed`
Type: `origins:conditioned_attribute`
Attribute: `minecraft:generic.movement_speed`
Operation: `add_multiplied_base` | Value: `0.3`
Condition: entity is in a biome tagged `minecraft:is_forest`

Adds 30% of the entity's base movement speed as a flat bonus while standing in any forest biome. Removed when leaving the biome.

---

## Dwarf

Tag: `#rustic:dwarf_powers` → `data/rustic/tags/origins/power/dwarf_powers.json`
The tag registers the pickaxe haste power and both underground powers below.

### `rustic:dwarf_pickaxe_haste`
Type: `origins:action_over_time`
Interval: 20 ticks (1 s)
Condition: mainhand item is in tag `minecraft:pickaxes`
Action: applies `minecraft:haste` — amplifier 0 (Haste I), duration 40 ticks, no particles

Every second, if the player is holding any pickaxe, refreshes Haste I for 2 seconds. Effect is hidden from particles but shows the icon. Net result: continuous Haste I while a pickaxe is held.

### `rustic:dwarf_underground_resistance`
Type: `origins:action_over_time`
Condition: `origins:distance_from_coordinates` — offset Y `-64`, ignoring X/Z, comparison `<=` `124`
  → equivalent to: entity Y position ≤ 60
Action: applies `minecraft:resistance` — amplifier 1 (Resistance II), duration 40 ticks - use OriginJS to implement

Should continuously apply Resistance II while the player is at or below Y=60 (underground).

### `rustic:dwarf_underground_vision`
Type: `origins:night_vision`
Strength: `1.0` (full brightness)
Condition: same as above — entity Y position ≤ 60 - use OriginJS to implement

Should grant full night vision while underground (Y ≤ 60).

---

## Miner

Tag: `#rustic:miner_powers` → `data/rustic/tags/origins/power/miner_powers.json`

### `rustic:no_mining_exhaustion`
Type: `origins:modify_exhaustion`
Operation: `multiply_base_multiplicative` | Value: `-0.5`
Hidden: true

Multiplies all exhaustion gained by the player by 0.5 (50% reduction). Applies to every source of exhaustion, not just mining.

### `rustic:more_stone_break_speed`
Type: `origins:modify_break_speed`
Operation: `multiply_base_multiplicative` | Value: `1.0`
Block condition: block is in tag `rustic:stone`
Hidden: true

Multiplies the player's break speed by 2× (`base + 1.0 × base`) on any block in the `rustic:stone` tag. Effectively doubles mining speed on stone-type blocks.

---

## Farmer

Tag: `#rustic:farmer_powers` → `data/rustic/tags/origins/power/farmer_powers.json`

### `rustic:farmer_crop_speed`
Type: `origins:action_over_time`
Interval: 20 ticks (1 s)
Condition: `origins:block_in_radius` — any block in tag `minecraft:crops` within radius 4
Action: applies `minecraft:speed` — amplifier 0 (Speed I), duration 40 ticks, no particles, shows icon

Every second, if any crop block exists within 4 blocks of the player, refreshes Speed I for 2 seconds. Net result: continuous Speed I while near crops.

### Individual Crop Doubling Powers
Each crop doubling power uses `origins:modify_harvest` with `origins:block` checking the specific crop block and full maturity (e.g. `age: 7`), replacing the block loot table with a 2x roll rustic loot table:
- `rustic:farmer_double_wheat` → `rustic:farmer_wheat` (`minecraft:wheat[age=7]`)
- `rustic:farmer_double_carrots` → `rustic:farmer_carrots` (`minecraft:carrots[age=7]`)
- `rustic:farmer_double_potatoes` → `rustic:farmer_potatoes` (`minecraft:potatoes[age=7]`)
- `rustic:farmer_double_beetroots` → `rustic:farmer_beetroots` (`minecraft:beetroots[age=3]`)
- `rustic:farmer_double_nether_wart` → `rustic:farmer_nether_wart` (`minecraft:nether_wart[age=3]`)
- `rustic:farmer_double_cocoa` → `rustic:farmer_cocoa` (`minecraft:cocoa[age=2]`)

---

## Undead

Tag: `#rustic:undead_powers` → `data/rustic/tags/origins/power/undead_powers.json`

### `rustic:undead_harming_immunity`
Type: `origins:effect_immunity`
Effect: `minecraft:instant_damage`

Grants immunity to Instant Damage (Harming) status effects, correctly modeling undead physiology.

### `rustic:undead_poison_immunity`
Type: `origins:effect_immunity`
Effects: `["minecraft:poison", "minecraft:hunger"]`

Grants immunity to both Poison and Hunger effects.
