# Origins Rustic — In-Game & Live Server Testing Framework (`TESTING.md`)

This document details the live testing harness and empirical verification commands used to validate the **Origins Rustic** datapack on Minecraft 1.21.1 / NeoForge 21.1.248.

---

## 1. Testing Philosophy & Automated Console Execution

In accordance with the Anti-Hallucination and Zero-Laziness directives, all origin and class features are validated directly against an active dedicated server with a live player connected (`dwurdy`).

Commands can be run sequentially via the server console or automated harness (`tests/test_origins_live.py`) to verify attributes, damage modifications, and loot table replacements without requiring client-side manual action.

---

## 2. Test Batches & Console Commands

### Batch 1: Races & Core Attributes Audit
Run these commands in console to audit health, natural armor, and immunities:
```mcfunction
# Setup
gamemode survival <player>
effect give <player> instant_health 1 255 true

# 1. Human (Baseline)
origin set <player> origins:origin rustic:human
attribute <player> generic.max_health get          # Expected: 20.0
attribute <player> generic.armor get               # Expected: 0.0
attribute <player> generic.attack_damage get       # Expected: 1.0
attribute <player> generic.movement_speed get      # Expected: 0.10

# 2. Automaton (Innate Armor)
origin set <player> origins:origin rustic:automaton
attribute <player> generic.armor get               # Expected: 8.0 (+8 armor points)

# 3. Phantom (Health Penalty)
origin set <player> origins:origin rustic:phantom
attribute <player> generic.max_health get          # Expected: 14.0 (-3 hearts / -6 HP)

# 4. Undead (Health Penalty & Poison Immunity)
origin set <player> origins:origin rustic:undead
attribute <player> generic.max_health get          # Expected: 18.0 (-1 heart / -2 HP)
effect give <player> minecraft:poison 5 1 true     # Expected: Rejected by server (target immune)
```

---

### Batch 2: Combat & RPG Classes Audit
```mcfunction
# 1. Barbarian (Brute Strength)
origin set <player> origins:origin rustic:human
origin set <player> origins_classes:class rustic:barbarian
attribute <player> generic.attack_damage get       # Expected: 2.0 (+25% / +1 attack damage)

# 2. Salahor (Colossal Titan)
origin set <player> origins_classes:class rustic:salahor
attribute <player> generic.max_health get          # Expected: 24.0 (+2 hearts / +4 HP)
attribute <player> generic.attack_damage get       # Expected: 2.0 (+1 attack damage)
attribute <player> generic.knockback_resistance get # Expected: 0.2
attribute <player> generic.movement_speed get      # Expected: 0.09 (-10% to -20% speed)

# 3. Knight (15% Physical Damage Reduction)
origin set <player> origins_classes:class rustic:knight
effect give <player> instant_health 1 255 true
damage <player> 10 minecraft:generic
data get entity <player> Health                    # Expected: 11.5f (8.5 taken = -15% reduction)

# Control Check (Nitwit Baseline)
origin set <player> origins_classes:class rustic:nitwit
effect give <player> instant_health 1 255 true
damage <player> 10 minecraft:generic
data get entity <player> Health                    # Expected: 10.0f (10.0 taken = 0% reduction)
```

---

### Batch 3: Tanner Cattle Butchery Drop Replacement
```mcfunction
origin set <player> origins_classes:class rustic:tanner
execute at <player> run summon cow ~ ~ ~ {CustomName:'"TannerTestCow"',Tags:["tanner_test"]}
damage @e[tag=tanner_test,limit=1] 100 minecraft:player_attack by <player>
execute at <player> as @e[type=item,distance=..5] run data get entity @s Item
# Expected: Item entities include count: 2 or 3 of minecraft:leather (replaced loot table)
```

---

### Batch 4: Dwarf Subterranean Environmental Triggers
```mcfunction
origin set <player> origins:origin rustic:dwarf

# Underground (Y <= 60)
tp <player> ~ 30 ~
data get entity <player> active_effects
# Expected: [{id: "minecraft:resistance", amplifier: 1b}] (Resistance II active)

# Above Ground (Y > 60)
tp <player> ~ 80 ~
# Wait 2 seconds (40 ticks duration expires)
data get entity <player> active_effects
# Expected: Found no elements matching active_effects (cleared)
```

---

### Batch 5: KubeJS Live Class & Origin Restrictions

1. **Nitwit Tool Restrictions (Watering Can & Cleaver)**:
   ```mcfunction
   origin set <player> origins_classes:class rustic:nitwit
   give <player> hearthandharvest:watering_can 1
   give <player> butchery:iron_cleaver 1
   execute at <player> run summon minecraft:pig ~1 ~ ~ {NoAI:1b,CustomName:'"Porc Test"'}

   # Right-click crop/block with Watering Can:
   # Expected: Sound minecraft:block.chest.locked, red message on actionbar, watering cancelled.

   # Left-click (attack) pig with Butcher's Cleaver:
   # Expected: Sound minecraft:block.chest.locked, red message on actionbar, attack cancelled before landing (0 damage, no hit animation, no knockback).
   ```

2. **Dragonborn Flight Restriction (Firework Rocket Boost Blocked)**:
   ```mcfunction
   origin set <player> origins:origin rustic:dragonborn
   give <player> minecraft:firework_rocket 1

   # Jump from height to glide with innate dragon wings, then right-click firework rocket:
   # Expected: Sound minecraft:block.fire.extinguish, actionbar message "Zborul de dragon este organic și nu poate fi propulsat cu artificii!", firework not consumed.
   ```

---

## 3. Knight Damage Reduction Caveat (FAQ)

When testing or reviewing Knight's damage mitigation, note the following:
1. **Survival Mode Required**: Creative Mode completely ignores all incoming damage calculations.
2. **Fractional Heart HUD Rounding**: On small hits (e.g. 1.0 HP), a 15% reduction results in 0.85 damage taken, which rounds up on the visual heart GUI. On large hits (e.g. 10.0 HP), 8.5 damage is taken, preserving a full 1.5 HP (3/4 of a heart).
3. **Multiplicative Stacking**: The reduction applies after vanilla armor protection calculations.
