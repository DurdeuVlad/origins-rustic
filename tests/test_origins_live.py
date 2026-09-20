"""
Origins Rustic - Automated In-Game Live Test Harness
====================================================
Runs empirical validation tests against the live NeoForge 1.21.1 staging server (container: mc-staging-server).
Audits attributes, damage modifications, loot table replacements, and environmental triggers
for Batches 1-4 documented in docs/TESTING.md.

Note on Batch 5:
----------------
Batch 5 (KubeJS Live Class & Origin Restrictions) is explicitly NOT included in this RCON harness.
Batch 5 requires real client input actions (right-clicking crops with a watering can, gliding
with dragon wings and right-clicking firework rockets, attacking entities with butcher cleavers)
that cannot be driven via server console / RCON commands. Those tests are validated in-game by
human testers or client-side automation.

RCON Prior Art & Protocol Note:
-------------------------------
Direct TCP connections to port 25575 from the host are unavailable because port 25575 is not
published to host network interfaces. Pure-Python RCON libraries (e.g. mcrcon, mctools) would
require either container network bridge lookup or additional runtime dependencies not installed
on the host. Shelling out to `docker exec mc-staging-server rcon-cli` utilizes the proven-working,
container-native CLI bundled with the itzg/minecraft-server image.

Technical note on rcon-cli argument handling:
rcon-cli implements command invocation by joining all positional arguments with spaces
(`strings.Join(args, " ")`). Passing multiple distinct Minecraft commands as CLI arguments
causes them to be received by the server as a single invalid concatenated string. Therefore,
this harness executes commands individually via `docker exec ... rcon-cli "<cmd>"` (or via
interactive stdin streaming) to guarantee reliable response-assertion pairing.
"""

import argparse
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from typing import Callable, Dict, List, Optional, Tuple

DEFAULT_CONTAINER = "mc-staging-server"
DEFAULT_PROPERTIES_PATH = "/mnt/raid-storage/mc-staging/data/server.properties"
DEFAULT_RCON_PORT = 25575
DEFAULT_PLAYER = "dwurdy"


@dataclass
class TestStep:
    """Represents a single command and its assertion in a test batch."""
    __test__ = False
    command: str
    description: str
    is_setup: bool = False
    expected_text: str = ""
    check_fn: Optional[Callable[[str], bool]] = None
    post_delay: float = 0.0


def read_rcon_password(properties_path: str = DEFAULT_PROPERTIES_PATH) -> str:
    """
    Read rcon.password fresh from server.properties.
    The password is regenerated on every container start by mc-image-helper.
    """
    if not os.path.isfile(properties_path):
        raise FileNotFoundError(f"server.properties not found at: {properties_path}")

    with open(properties_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("rcon.password="):
                password = line.split("=", 1)[1]
                if password:
                    return password

    raise ValueError(f"rcon.password key missing or empty in {properties_path}")


def get_container_status(container_name: str = DEFAULT_CONTAINER) -> str:
    """Check container status via docker inspect."""
    cmd = ["docker", "inspect", container_name, "--format", "{{.State.Status}}"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            stderr = proc.stderr.strip()
            if re.search(r"no such (?:object|container)|container .* not found", stderr, re.IGNORECASE):
                return "not_found"
            return f"error: {stderr or f'docker inspect exited with code {proc.returncode}'}"
        status = proc.stdout.strip()
        return status or "error: docker inspect returned an empty status"
    except Exception as e:
        return f"error: {e}"


def is_player_missing(response: str) -> bool:
    """Detect if server response indicates target player was not found or is offline."""
    missing_patterns = [
        r"no player was found",
        r"player.*not found",
        r"entity.*not found",
        r"no entity was found",
        r"cannot find player",
        r"failed to find",
    ]
    for pattern in missing_patterns:
        if re.search(pattern, response, re.IGNORECASE):
            return True
    return False


def is_command_error(response: str) -> bool:
    """Detect Minecraft command responses that indicate an invalid command or ID."""
    error_patterns = [
        r"\bunknown (?:or incomplete )?(?:command|argument|origin|class)\b",
        r"\b(?:origin|class)\b.*\b(?:not found|does not exist|not available|unknown|invalid)\b",
        r"\b(?:no such|no matching)\b.*\b(?:origin|class)\b",
        r"\b(?:there is|there's)\s+no\b.*\b(?:origin|class)\b",
        r"\b(?:couldn'?t|could not|cannot|can't|unable to)\b.*\b(?:find|resolve|set|assign)\b.*\b(?:origin|class)\b",
        r"\bincorrect argument\b",
        r"\bfailed to execute\b",
    ]
    return any(re.search(pattern, response, re.IGNORECASE) for pattern in error_patterns)


def run_rcon_command(
    container: str,
    password: str,
    port: int,
    command: str,
    timeout: int = 15,
) -> Tuple[int, str, str]:
    """Execute a single command via docker exec rcon-cli."""
    exec_cmd = [
        "docker",
        "exec",
        container,
        "rcon-cli",
        "--port",
        str(port),
        "--password",
        password,
        command,
    ]
    try:
        proc = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=timeout, check=False)
        return proc.returncode, proc.stdout.strip(), proc.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Command execution timed out"
    except Exception as e:
        return -1, "", str(e)


def build_batches(player: str = DEFAULT_PLAYER) -> Dict[str, List[TestStep]]:
    """
    Builds the test steps for Batches 1 to 4 matching docs/TESTING.md.
    Note: Batch 5 is intentionally excluded (requires client-side input).
    """

    # Helper regex matchers
    def matches_num(val_str: str) -> Callable[[str], bool]:
        # Matches numbers like 20, 20.0, 20.00 in attribute outputs
        # Attribute get output typically: "Entity ... has attribute ... with value 20.0"
        escaped = re.escape(val_str)
        # Handle cases like "20.0" matching "20" or "20.0"
        if "." in val_str:
            base_int = val_str.split(".")[0]
            pat = rf"\b(?:{escaped}|{base_int}(?:\.0+)?)\b"
        else:
            pat = rf"\b{escaped}(?:\.0+)?\b"
        return lambda resp: bool(re.search(pat, resp))

    def matches_regex(pattern: str) -> Callable[[str], bool]:
        regex = re.compile(pattern, re.IGNORECASE)
        return lambda resp: bool(regex.search(resp))

    def not_contains_effect(effect_id: str) -> Callable[[str], bool]:
        # Checks that the effect is cleared / no elements found
        return lambda resp: (
            "found no elements" in resp.lower()
            or effect_id.lower() not in resp.lower()
            or resp.strip().endswith("[]")
        )

    batches: Dict[str, List[TestStep]] = {
        "batch_1": [
            TestStep(
                command=f"gamemode survival {player}",
                description="Setup: Set gamemode survival",
                is_setup=True,
                expected_text="Set game mode to Survival",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"effect give {player} instant_health 1 255 true",
                description="Setup: Reset health to max",
                is_setup=True,
                expected_text="Applied effect",
                check_fn=lambda r: not is_player_missing(r),
            ),
            # 1. Human (Baseline)
            TestStep(
                command=f"origin set {player} origins:origin rustic:human",
                description="Human: Set origin rustic:human",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.max_health get",
                description="Human: Check generic.max_health",
                is_setup=False,
                expected_text="20.0",
                check_fn=matches_num("20.0"),
            ),
            TestStep(
                command=f"attribute {player} generic.armor get",
                description="Human: Check generic.armor",
                is_setup=False,
                expected_text="0.0",
                check_fn=matches_num("0.0"),
            ),
            TestStep(
                command=f"attribute {player} generic.attack_damage get",
                description="Human: Check generic.attack_damage",
                is_setup=False,
                expected_text="1.0",
                check_fn=matches_num("1.0"),
            ),
            TestStep(
                command=f"attribute {player} generic.movement_speed get",
                description="Human: Check generic.movement_speed",
                is_setup=False,
                expected_text="0.10",
                check_fn=matches_regex(r"\b0\.10*\b"),
            ),
            # 2. Automaton (Innate Armor)
            TestStep(
                command=f"origin set {player} origins:origin rustic:automaton",
                description="Automaton: Set origin rustic:automaton",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.armor get",
                description="Automaton: Check generic.armor (+8 armor points)",
                is_setup=False,
                expected_text="8.0 (+8 armor points)",
                check_fn=matches_num("8.0"),
            ),
            # 3. Phantom (Health Penalty)
            TestStep(
                command=f"origin set {player} origins:origin rustic:phantom",
                description="Phantom: Set origin rustic:phantom",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.max_health get",
                description="Phantom: Check generic.max_health (-6 HP / -3 hearts)",
                is_setup=False,
                expected_text="14.0 (-3 hearts / -6 HP)",
                check_fn=matches_num("14.0"),
            ),
            # 4. Undead (Health Penalty & Poison Immunity)
            TestStep(
                command=f"origin set {player} origins:origin rustic:undead",
                description="Undead: Set origin rustic:undead",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.max_health get",
                description="Undead: Check generic.max_health (-2 HP / -1 heart)",
                is_setup=False,
                expected_text="18.0 (-1 heart / -2 HP)",
                check_fn=matches_num("18.0"),
            ),
            TestStep(
                command=f"effect give {player} minecraft:poison 5 1 true",
                description="Undead: Poison immunity check",
                is_setup=False,
                expected_text="Rejected by server (target immune)",
                check_fn=matches_regex(r"(immune|could not apply|target is immune|failed)"),
            ),
        ],
        "batch_2": [
            # 1. Barbarian (Brute Strength)
            TestStep(
                command=f"origin set {player} origins:origin rustic:human",
                description="Barbarian Setup: Reset race to rustic:human",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"origin set {player} origins_classes:class rustic:barbarian",
                description="Barbarian Setup: Set class rustic:barbarian",
                is_setup=True,
                expected_text="Set class",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.attack_damage get",
                description="Barbarian: Check generic.attack_damage (+1 damage)",
                is_setup=False,
                expected_text="2.0 (+25% / +1 attack damage)",
                check_fn=matches_num("2.0"),
            ),
            # 2. Salahor (Colossal Titan)
            TestStep(
                command=f"origin set {player} origins_classes:class rustic:salahor",
                description="Salahor Setup: Set class rustic:salahor",
                is_setup=True,
                expected_text="Set class",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"attribute {player} generic.max_health get",
                description="Salahor: Check generic.max_health (+4 HP / +2 hearts)",
                is_setup=False,
                expected_text="24.0 (+2 hearts / +4 HP)",
                check_fn=matches_num("24.0"),
            ),
            TestStep(
                command=f"attribute {player} generic.attack_damage get",
                description="Salahor: Check generic.attack_damage (+1 damage)",
                is_setup=False,
                expected_text="2.0 (+1 attack damage)",
                check_fn=matches_num("2.0"),
            ),
            TestStep(
                command=f"attribute {player} generic.knockback_resistance get",
                description="Salahor: Check generic.knockback_resistance",
                is_setup=False,
                expected_text="0.2",
                check_fn=matches_regex(r"\b0\.20*\b"),
            ),
            TestStep(
                command=f"attribute {player} generic.movement_speed get",
                description="Salahor: Check generic.movement_speed (-10% speed)",
                is_setup=False,
                expected_text="0.09 (-10% to -20% speed)",
                check_fn=matches_regex(r"\b0\.090*\b"),
            ),
            # 3. Knight (15% Physical Damage Reduction)
            TestStep(
                command=f"origin set {player} origins_classes:class rustic:knight",
                description="Knight Setup: Set class rustic:knight",
                is_setup=True,
                expected_text="Set class",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"effect give {player} instant_health 1 255 true",
                description="Knight Setup: Restore full health",
                is_setup=True,
                expected_text="Applied effect",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"damage {player} 10 minecraft:generic",
                description="Knight Setup: Inflict 10 damage",
                is_setup=True,
                expected_text="Damaged",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"data get entity {player} Health",
                description="Knight: Check health after 10 damage (-15% reduction -> 11.5f)",
                is_setup=False,
                expected_text="11.5f (8.5 taken = -15% reduction)",
                check_fn=matches_regex(r"\b11\.5f?\b"),
            ),
            # Control Check (Nitwit Baseline)
            TestStep(
                command=f"origin set {player} origins_classes:class rustic:nitwit",
                description="Nitwit Setup: Set class rustic:nitwit",
                is_setup=True,
                expected_text="Set class",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"effect give {player} instant_health 1 255 true",
                description="Nitwit Setup: Restore full health",
                is_setup=True,
                expected_text="Applied effect",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"damage {player} 10 minecraft:generic",
                description="Nitwit Setup: Inflict 10 damage",
                is_setup=True,
                expected_text="Damaged",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"data get entity {player} Health",
                description="Nitwit Control: Check health after 10 damage (0% reduction -> 10.0f)",
                is_setup=False,
                expected_text="10.0f (10.0 taken = 0% reduction)",
                check_fn=matches_regex(r"\b10(?:\.0+)?f?\b"),
            ),
        ],
        "batch_3": [
            TestStep(
                command=f"origin set {player} origins_classes:class rustic:tanner",
                description="Tanner Setup: Set class rustic:tanner",
                is_setup=True,
                expected_text="Set class",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"execute at {player} run summon cow ~ ~ ~ {{CustomName:'\"TannerTestCow\"',Tags:[\"tanner_test\"]}}",
                description="Tanner Setup: Summon test cow",
                is_setup=True,
                expected_text="Summoned new TannerTestCow",
                check_fn=lambda r: not is_player_missing(r),
            ),
            TestStep(
                command=f"damage @e[tag=tanner_test,limit=1] 100 minecraft:player_attack by {player}",
                description="Tanner Setup: Kill test cow via player attack",
                is_setup=True,
                expected_text="Damaged cow",
                check_fn=lambda r: not is_player_missing(r),
                post_delay=0.5,
            ),
            TestStep(
                command=f"execute at {player} as @e[type=item,distance=..5] run data get entity @s Item",
                description="Tanner: Check dropped cow loot for doubled leather",
                is_setup=False,
                expected_text="Item entities include count: 2 or 3 of minecraft:leather",
                check_fn=lambda r: bool(
                    re.search(r"minecraft:leather", r, re.IGNORECASE)
                    and re.search(r"count:\s*[23]b?", r, re.IGNORECASE)
                ),
            ),
        ],
        "batch_4": [
            TestStep(
                command=f"origin set {player} origins:origin rustic:dwarf",
                description="Dwarf Setup: Set origin rustic:dwarf",
                is_setup=True,
                expected_text="Set origin",
                check_fn=lambda r: not is_player_missing(r),
            ),
            # Underground (Y <= 60)
            TestStep(
                command=f"tp {player} ~ 30 ~",
                description="Dwarf Underground: Teleport player to Y=30",
                is_setup=True,
                expected_text="Teleported",
                check_fn=lambda r: not is_player_missing(r),
                post_delay=0.5,
            ),
            TestStep(
                command=f"data get entity {player} active_effects",
                description="Dwarf Underground: Assert Resistance II active (amplifier: 1b)",
                is_setup=False,
                expected_text='[{id: "minecraft:resistance", amplifier: 1b}] (Resistance II active)',
                check_fn=lambda r: bool(
                    re.search(r"minecraft:resistance", r, re.IGNORECASE)
                    and re.search(r"amplifier:\s*1b?", r, re.IGNORECASE)
                ),
            ),
            # Above Ground (Y > 60)
            TestStep(
                command=f"tp {player} ~ 80 ~",
                description="Dwarf Above Ground: Teleport player to Y=80",
                is_setup=True,
                expected_text="Teleported",
                check_fn=lambda r: not is_player_missing(r),
                # Resistance power has 40-tick (2s) duration; wait 2.5s for expiration
                post_delay=2.5,
            ),
            TestStep(
                command=f"data get entity {player} active_effects",
                description="Dwarf Above Ground: Assert Resistance II cleared",
                is_setup=False,
                expected_text="Found no elements matching active_effects (cleared)",
                check_fn=not_contains_effect("minecraft:resistance"),
            ),
        ],
    }

    return batches


def run_batch(
    batch_name: str,
    steps: List[TestStep],
    container: str,
    password: str,
    port: int = DEFAULT_RCON_PORT,
    verbose: bool = True,
) -> Tuple[int, int, int]:
    """
    Executes all steps in a batch, verifying responses against expectations.
    Returns (passed, failed, errored).
    """
    print(f"\n{'=' * 70}")
    print(f"RUNNING {batch_name.upper()} ({len(steps)} steps)")
    print(f"{'=' * 70}")

    passed = 0
    failed = 0
    errored = 0
    setup_group_failed = False
    previous_was_setup = False

    for idx, step in enumerate(steps, 1):
        if step.is_setup and not previous_was_setup:
            # A new contiguous setup group establishes a new state for its assertions.
            setup_group_failed = False

        if not step.is_setup and setup_group_failed:
            print(f"  [{idx}/{len(steps)}] ERROR: {step.description}")
            print(f"    Command:  {step.command}")
            print("    Detail:   Blocked by a previous setup command error; command not sent.")
            errored += 1
            previous_was_setup = False
            continue

        ret_code, stdout, stderr = run_rcon_command(
            container=container,
            password=password,
            port=port,
            command=step.command,
        )

        output = stdout if stdout else stderr

        if ret_code != 0:
            print(f"  [{idx}/{len(steps)}] ERROR: {step.description}")
            print(f"    Command:  {step.command}")
            print(f"    Error:    {stderr or f'Process exited with code {ret_code}'}")
            if stdout:
                print(f"    Response: {stdout}")
            errored += 1
            if step.is_setup:
                setup_group_failed = True
            previous_was_setup = step.is_setup
            continue

        if not stdout and not stderr:
            print(f"  [{idx}/{len(steps)}] ERROR: {step.description}")
            print(f"    Command:  {step.command}")
            print("    Error:    No response received from rcon-cli")
            errored += 1
            if step.is_setup:
                setup_group_failed = True
            previous_was_setup = step.is_setup
            continue

        # Check if the player entity is missing / offline
        if is_player_missing(output):
            print(f"  [{idx}/{len(steps)}] ERROR: {step.description}")
            print(f"    Command:  {step.command}")
            print(f"    Detail:   Target player is offline or entity not found.")
            print(f"    Response: {output}")
            errored += 1
            if step.is_setup:
                setup_group_failed = True
            previous_was_setup = step.is_setup
            continue

        if is_command_error(output):
            print(f"  [{idx}/{len(steps)}] ERROR: {step.description}")
            print(f"    Command:  {step.command}")
            print(f"    Detail:   Minecraft rejected the command or referenced ID.")
            print(f"    Response: {output}")
            errored += 1
            if step.is_setup:
                setup_group_failed = True
            previous_was_setup = step.is_setup
            continue

        if step.is_setup:
            # Setup command: success is non-error response
            if verbose:
                print(f"  [{idx}/{len(steps)}] SETUP: {step.description}")
                print(f"    Command:  {step.command}")
                print(f"    Response: {output}")
            passed += 1
        else:
            # Assertion command
            is_pass = step.check_fn(output) if step.check_fn else False
            if is_pass:
                print(f"  [{idx}/{len(steps)}] PASS: {step.description}")
                print(f"    Command:  {step.command}")
                print(f"    Expected: {step.expected_text}")
                print(f"    Response: {output}")
                passed += 1
            else:
                print(f"  [{idx}/{len(steps)}] FAIL: {step.description}")
                print(f"    Command:  {step.command}")
                print(f"    Expected: {step.expected_text}")
                print(f"    Actual:   {output}")
                failed += 1

        previous_was_setup = step.is_setup
        if step.post_delay > 0:
            time.sleep(step.post_delay)

    total = len(steps)
    print(f"\n{batch_name} Summary: {passed}/{total} passed, {failed} failed, {errored} errored")
    return passed, failed, errored


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Origins Rustic live test runner against NeoForge staging server."
    )
    parser.add_argument(
        "--player",
        default=DEFAULT_PLAYER,
        help=f"Target player username (default: {DEFAULT_PLAYER})",
    )
    parser.add_argument(
        "--batch",
        choices=["1", "2", "3", "4", "all"],
        default="all",
        help="Specific test batch to run (1, 2, 3, 4, or all; default: all)",
    )
    parser.add_argument(
        "--container",
        default=DEFAULT_CONTAINER,
        help=f"Docker container name (default: {DEFAULT_CONTAINER})",
    )
    parser.add_argument(
        "--properties-file",
        default=DEFAULT_PROPERTIES_PATH,
        help=f"Path to server.properties (default: {DEFAULT_PROPERTIES_PATH})",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_RCON_PORT,
        help=f"RCON port (default: {DEFAULT_RCON_PORT})",
    )

    args = parser.parse_args(argv)

    print(f"Origins Live Test Suite")
    print(f"Target Player:     {args.player}")
    print(f"Target Container:  {args.container}")
    print(f"Properties Path:   {args.properties_file}")
    print(f"RCON Port:         {args.port}")

    # 1. Check container status
    status = get_container_status(args.container)
    if status != "running":
        print(f"\n[ERROR] Container '{args.container}' status is '{status}'.")
        if status.startswith("error:"):
            print("Could not verify Docker/container state; not running tests.")
        elif status == "not_found":
            print("Container was not found; not running tests.")
        else:
            print("Server is asleep, not running tests.")
        return 1

    # 2. Read RCON password
    try:
        rcon_pw = read_rcon_password(args.properties_file)
    except Exception as e:
        print(f"\n[ERROR] Failed to read RCON password: {e}")
        return 1

    # 3. Build batches
    all_batches = build_batches(player=args.player)

    if args.batch == "all":
        selected_batches = list(all_batches.keys())
    else:
        selected_batches = [f"batch_{args.batch}"]

    total_passed = 0
    total_failed = 0
    total_errored = 0

    for b_name in selected_batches:
        steps = all_batches[b_name]
        p, f, e = run_batch(
            batch_name=b_name,
            steps=steps,
            container=args.container,
            password=rcon_pw,
            port=args.port,
        )
        total_passed += p
        total_failed += f
        total_errored += e

    print(f"\n{'#' * 70}")
    print(f"OVERALL SUMMARY")
    print(f"{'#' * 70}")
    print(f"Total Passed:  {total_passed}")
    print(f"Total Failed:  {total_failed}")
    print(f"Total Errored: {total_errored}")

    if total_failed > 0 or total_errored > 0:
        print("RESULT: FAILED")
        return 1

    print("RESULT: ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
