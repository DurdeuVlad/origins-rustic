"""
Unit tests for tests/test_origins_live.py
Validates offline parsing, mock execution, docker inspect gating,
RCON password extraction, and PASS/FAIL/ERROR determination.
"""

import os
import sys
import tempfile
import pytest
from unittest.mock import MagicMock, patch

# Ensure tests module is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_origins_live import (
    TestStep,
    build_batches,
    get_container_status,
    is_player_missing,
    main,
    read_rcon_password,
    run_batch,
    run_rcon_command,
)


class TestRconPasswordReader:
    def test_read_valid_password(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            tf.write("motd=A Minecraft Server\n")
            tf.write("rcon.port=25575\n")
            tf.write("rcon.password=secret_test_pw_123\n")
            tf.write("enable-rcon=true\n")
            tf_path = tf.name

        try:
            pw = read_rcon_password(tf_path)
            assert pw == "secret_test_pw_123"
        finally:
            os.remove(tf_path)

    def test_missing_file(self):
        with pytest.raises(FileNotFoundError):
            read_rcon_password("/non/existent/path/server.properties")

    def test_missing_password_key(self):
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as tf:
            tf.write("motd=A Minecraft Server\n")
            tf.write("enable-rcon=true\n")
            tf_path = tf.name

        try:
            with pytest.raises(ValueError, match="rcon.password key missing"):
                read_rcon_password(tf_path)
        finally:
            os.remove(tf_path)


class TestDockerStatusCheck:
    @patch("subprocess.run")
    def test_container_running(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "running\n"
        mock_run.return_value = mock_proc

        status = get_container_status("mc-staging-server")
        assert status == "running"

    @patch("subprocess.run")
    def test_container_exited(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "exited\n"
        mock_run.return_value = mock_proc

        status = get_container_status("mc-staging-server")
        assert status == "exited"

    @patch("subprocess.run")
    def test_container_not_found(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "Error: No such container: nonexistent-container\n"
        mock_run.return_value = mock_proc

        status = get_container_status("nonexistent-container")
        assert status == "not_found"

    @patch("subprocess.run")
    def test_container_inspect_error_is_distinct_from_not_found(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "permission denied while trying to connect to the Docker daemon\n"
        mock_run.return_value = mock_proc

        status = get_container_status("mc-staging-server")
        assert status.startswith("error:")


class TestPlayerMissingDetection:
    def test_player_missing_patterns(self):
        assert is_player_missing("No player was found")
        assert is_player_missing("Player dwurdy not found")
        assert is_player_missing("Entity dwurdy not found")
        assert is_player_missing("No entity was found")

    def test_player_present_responses(self):
        assert not is_player_missing("dwurdy has 20.0 max health")
        assert not is_player_missing("Set game mode to Survival Mode")
        assert not is_player_missing("Applied effect Instant Health to dwurdy")


class TestBatchExecutionAndAssertions:
    def test_build_batches_structure(self):
        batches = build_batches(player="test_player")
        assert "batch_1" in batches
        assert "batch_2" in batches
        assert "batch_3" in batches
        assert "batch_4" in batches
        # Verify Batch 5 is not present
        assert "batch_5" not in batches

    @patch("tests.test_origins_live.run_rcon_command")
    def test_batch_all_pass(self, mock_cmd):
        # Provide canned successful responses for Batch 1
        def side_effect(container, password, port, command):
            if "gamemode" in command:
                return 0, "Set game mode to Survival Mode for test_player", ""
            elif "effect give" in command and "instant_health" in command:
                return 0, "Applied effect Instant Health to test_player", ""
            elif "origin set" in command:
                return 0, "Set origin of test_player to rustic:human", ""
            elif "generic.max_health get" in command:
                return 0, "Entity test_player has attribute generic.max_health with value 20.0", ""
            elif "generic.armor get" in command:
                return 0, "Entity test_player has attribute generic.armor with value 0.0", ""
            elif "generic.attack_damage get" in command:
                return 0, "Entity test_player has attribute generic.attack_damage with value 1.0", ""
            elif "generic.movement_speed get" in command:
                return 0, "Entity test_player has attribute generic.movement_speed with value 0.1", ""
            elif "minecraft:poison" in command:
                return 0, "Could not apply effect minecraft:poison to test_player (target is immune)", ""
            return 0, "Success", ""

        mock_cmd.side_effect = side_effect

        batches = build_batches(player="test_player")
        b1_steps = batches["batch_1"]

        # Run a subset of batch 1
        passed, failed, errored = run_batch("batch_1", b1_steps[:7], "dummy-container", "dummy-pw")
        assert failed == 0
        assert errored == 0
        assert passed == 7

    @patch("tests.test_origins_live.run_rcon_command")
    def test_genuine_value_mismatch_reported_as_fail(self, mock_cmd):
        # Automaton armor expected: 8.0, but server returns 4.0
        mock_cmd.return_value = (0, "Entity test_player has attribute generic.armor with value 4.0", "")

        step = TestStep(
            command="attribute test_player generic.armor get",
            description="Automaton generic.armor get",
            is_setup=False,
            expected_text="8.0 (+8 armor points)",
            check_fn=lambda r: "8.0" in r or " 8 " in r,
        )

        passed, failed, errored = run_batch("test_batch", [step], "dummy-container", "dummy-pw")
        assert passed == 0
        assert failed == 1
        assert errored == 0

    @patch("tests.test_origins_live.run_rcon_command")
    def test_player_missing_reported_as_error_not_fail(self, mock_cmd):
        mock_cmd.return_value = (0, "No player was found", "")

        step = TestStep(
            command="attribute test_player generic.armor get",
            description="Automaton generic.armor get",
            is_setup=False,
            expected_text="8.0",
            check_fn=lambda r: "8.0" in r,
        )

        passed, failed, errored = run_batch("test_batch", [step], "dummy-container", "dummy-pw")
        assert passed == 0
        assert failed == 0
        assert errored == 1

    @patch("tests.test_origins_live.run_rcon_command")
    def test_command_execution_error(self, mock_cmd):
        mock_cmd.return_value = (1, "", "Failed to connect to RCON server")

        step = TestStep(
            command="attribute test_player generic.armor get",
            description="Automaton generic.armor get",
            is_setup=False,
            expected_text="8.0",
            check_fn=lambda r: "8.0" in r,
        )

        passed, failed, errored = run_batch("test_batch", [step], "dummy-container", "dummy-pw")
        assert passed == 0
        assert failed == 0
        assert errored == 1

    @patch("tests.test_origins_live.run_rcon_command")
    def test_unknown_origin_is_reported_as_error_and_blocks_following_assertion(self, mock_cmd):
        mock_cmd.side_effect = [
            (0, "Unknown origin rustic:barbarian", ""),
            (0, "Entity test_player has attribute generic.attack_damage with value 2.0", ""),
        ]
        steps = [
            TestStep(
                command="origin set test_player origins_classes:class rustic:barbarian",
                description="Deleted class setup",
                is_setup=True,
                expected_text="Set class",
            ),
            TestStep(
                command="attribute test_player generic.attack_damage get",
                description="Deleted class assertion",
                expected_text="2.0",
                check_fn=lambda r: "2.0" in r,
            ),
        ]

        passed, failed, errored = run_batch("invalid_origin", steps, "dummy-container", "dummy-pw")

        assert passed == 0
        assert failed == 0
        assert errored == 2

    @patch("tests.test_origins_live.run_rcon_command")
    def test_nonzero_exit_with_stdout_is_still_an_error(self, mock_cmd):
        mock_cmd.return_value = (1, "Unknown origin rustic:barbarian", "transport warning")
        step = TestStep(
            command="origin set test_player origins_classes:class rustic:barbarian",
            description="Deleted class setup",
            is_setup=True,
            expected_text="Set class",
        )

        passed, failed, errored = run_batch("nonzero_stdout", [step], "dummy-container", "dummy-pw")

        assert passed == 0
        assert failed == 0
        assert errored == 1

    @patch("tests.test_origins_live.run_rcon_command")
    def test_empty_rcon_response_is_an_error(self, mock_cmd):
        mock_cmd.return_value = (0, "", "")
        step = TestStep(
            command="gamemode survival test_player",
            description="Gamemode setup",
            is_setup=True,
            expected_text="Set game mode",
        )

        passed, failed, errored = run_batch("empty_response", [step], "dummy-container", "dummy-pw")

        assert passed == 0
        assert failed == 0
        assert errored == 1

    @patch("tests.test_origins_live.subprocess.run")
    def test_rcon_invocation_passes_one_minecraft_command_argument(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "ok\n"
        mock_proc.stderr = ""
        mock_run.return_value = mock_proc

        run_rcon_command(
            "mc-staging-server",
            "dummy-pw",
            25575,
            "say first; say second",
        )

        argv = mock_run.call_args.args[0]
        assert argv == [
            "docker",
            "exec",
            "mc-staging-server",
            "rcon-cli",
            "--port",
            "25575",
            "--password",
            "dummy-pw",
            "say first; say second",
        ]

    @patch("tests.test_origins_live.run_rcon_command")
    def test_mid_batch_rcon_failure_errors_remaining_commands(self, mock_cmd):
        mock_cmd.side_effect = [
            (0, "Set game mode to Survival Mode", ""),
            (1, "", "container is not running"),
            (1, "", "container is not running"),
        ]
        steps = [
            TestStep("gamemode survival test_player", "Setup", True, "Set game mode"),
            TestStep("attribute test_player generic.armor get", "First assertion", check_fn=lambda r: True),
            TestStep("attribute test_player generic.max_health get", "Second assertion", check_fn=lambda r: True),
        ]

        passed, failed, errored = run_batch("mid_run", steps, "dummy-container", "dummy-pw")

        assert passed == 1
        assert failed == 0
        assert errored == 2
        assert mock_cmd.call_count == 3


class TestMainEntryPoint:
    @patch("tests.test_origins_live.get_container_status")
    def test_main_exits_when_server_asleep(self, mock_status, capsys):
        mock_status.return_value = "exited"
        ret = main(["--batch", "1"])
        assert ret != 0

        out = capsys.readouterr().out
        assert "Server is asleep, not running tests" in out

    @patch("tests.test_origins_live.get_container_status")
    def test_main_exits_when_properties_missing(self, mock_status, capsys):
        mock_status.return_value = "running"
        ret = main(["--properties-file", "/nonexistent/server.properties"])
        assert ret != 0

        out = capsys.readouterr().out
        assert "Failed to read RCON password" in out
