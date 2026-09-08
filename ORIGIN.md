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
**Tag currently only lists `rustic:dwarf_pickaxe_haste`. The two underground powers below exist as files but are missing from the tag and are therefore inactive.**

### `rustic:dwarf_pickaxe_haste`
Type: `origins:action_over_time`
Interval: 20 ticks (1 s)
Condition: mainhand item is in tag `minecraft:pickaxes`
Action: applies `minecraft:haste` — amplifier 0 (Haste I), duration 40 ticks, no particles

Every second, if the player is holding any pickaxe, refreshes Haste I for 2 seconds. Effect is hidden from particles but shows the icon. Net result: continuous Haste I while a pickaxe is held.

### ⚠ `rustic:dwarf_underground_resistance` — BROKEN (not in tag)
Type: `origins:action_over_time`
Condition: `origins:distance_from_coordinates` — offset Y `-64`, ignoring X/Z, comparison `<=` `124`
  → equivalent to: entity Y position ≤ 60
Action: applies `minecraft:resistance` — amplifier 1 (Resistance II), duration 40 ticks - use OriginJS to implement

Should continuously apply Resistance II while the player is at or below Y=60 (underground). Currently does nothing because the power is not listed in `dwarf_powers.json`.

### ⚠ `rustic:dwarf_underground_vision` — BROKEN (not in tag)
Type: `origins:night_vision`
Strength: `1.0` (full brightness)
Condition: same as above — entity Y position ≤ 60 - use OriginJS to implement

Should grant full night vision while underground (Y ≤ 60). Currently does nothing because the power is not listed in `dwarf_powers.json`.

**Fix:** add both `rustic:dwarf_underground_resistance` and `rustic:dwarf_underground_vision` to `data/rustic/tags/origins/power/dwarf_powers.json`.

---

## Miner

Tag: `#rustic:miner_powers` → `data/rustic/tags/origins/power/miner_powers.json`

### `rustic:no_mining_exhaustion`
Type: `origins:modify_exhaustion`
Operation: `multiply_base_multiplicative` | Value: `-0.5`
Hidden: true

Multiplies all exhaustion gained by the player by 0.5 (50% reduction). Applies to every source of exhaustion, not just mining.

### ⚠ `rustic:double_ores` — BROKEN (power file missing)
The tag references this power but `data/rustic/origins/power/double_ores.json` does not exist as a power file.
A loot table `data/rustic/loot_table/double_ores.json` exists and rolls the base loot table twice (2 rolls of the replaced table), which is the intended mechanism for doubling drops.

Should use LootJS in tandem with OriginJS to implement the drop doubling.

**Fix:** create `data/rustic/origins/power/double_ores.json` as a power that hooks the existing loot table.

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

### `origins_classes:more_crop_drops` (external)
Should use LootJS in tandem with OriginJS to implement the drop doubling.
