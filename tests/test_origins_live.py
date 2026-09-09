"""
Origins Rustic - Automated In-Game Test Harness
Runs empirical validation tests against a running Minecraft server with an active player.
Audits attributes, damage reductions, loot table replacements, and environmental triggers.
"""

import os

LOG_PATH = r"E:\minecraft-test-server\logs\latest.log"

def get_test_command_batches(player="dwurdy"):
    return {
        "batch_1_races_attributes": [
            f"gamemode survival {player}",
            f"effect give {player} instant_health 1 255 true",
            f"origin set {player} origins:origin rustic:human",
            f"attribute {player} generic.max_health get",
            f"origin set {player} origins:origin rustic:automaton",
            f"attribute {player} generic.armor get",
            f"origin set {player} origins:origin rustic:phantom",
            f"attribute {player} generic.max_health get",
            f"origin set {player} origins:origin rustic:undead",
            f"attribute {player} generic.max_health get",
            f"effect give {player} minecraft:poison 5 1 true",
            f"data get entity {player} active_effects",
        ],
        "batch_2_combat_classes": [
            f"origin set {player} origins:origin rustic:human",
            f"origin set {player} origins_classes:class rustic:barbarian",
            f"attribute {player} generic.attack_damage get",
            f"origin set {player} origins_classes:class rustic:salahor",
            f"attribute {player} generic.max_health get",
            f"attribute {player} generic.attack_damage get",
            f"attribute {player} generic.knockback_resistance get",
            f"attribute {player} generic.movement_speed get",
            f"origin set {player} origins_classes:class rustic:knight",
            f"effect give {player} instant_health 1 255 true",
            f"damage {player} 10 minecraft:generic",
            f"data get entity {player} Health",
        ],
        "batch_3_tanner_loot": [
            f"origin set {player} origins_classes:class rustic:tanner",
            f"execute at {player} run summon cow ~ ~ ~ {{CustomName:'\"TannerTestCow\"',Tags:[\"tanner_test\"]}}",
            f"damage @e[tag=tanner_test,limit=1] 100 minecraft:player_attack by {player}",
            f"execute at {player} as @e[type=item,distance=..5] run data get entity @s Item",
        ],
        "batch_4_dwarf_underground": [
            f"origin set {player} origins:origin rustic:dwarf",
            f"tp {player} ~ 30 ~",
            f"data get entity {player} active_effects",
            f"tp {player} ~ 80 ~",
            f"data get entity {player} active_effects",
        ]
    }

if __name__ == "__main__":
    batches = get_test_command_batches()
    print(f"Origins Live Test Suite loaded with {len(batches)} batches.")
    for name, cmds in batches.items():
        print(f"\n[{name}] ({len(cmds)} commands):")
        for c in cmds:
            print(f"  {c}")
