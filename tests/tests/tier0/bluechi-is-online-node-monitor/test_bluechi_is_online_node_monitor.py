#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: LGPL-2.1-or-later
import logging
import threading
import time
from typing import Dict

from bluechi_test.config import BluechiAgentConfig, BluechiControllerConfig
from bluechi_test.machine import BluechiAgentMachine, BluechiControllerMachine
from bluechi_test.test import BluechiTest
from bluechi_test.util import Timeout, get_test_env_value_int

LOGGER = logging.getLogger(__name__)

NODE_FOO = "node-foo"
SLEEP_DURATION = get_test_env_value_int("SLEEP_DURATION", 2)


class MonitorResult:
    def __init__(self):
        self.result = None
        self.output = ""


def monitor_command(
    ctrl: BluechiControllerMachine, node_name: str, monitor_result: MonitorResult
):
    monitor_result.result, monitor_result.output = ctrl.bluechi_is_online.monitor_node(
        node_name
    )


def exec(ctrl: BluechiControllerMachine, nodes: Dict[str, BluechiAgentMachine]):
    node_foo = nodes[NODE_FOO]

    # Test 1: Agent and node are running, no monitor output expected
    LOGGER.debug("Starting NODE_FOO.")
    monitor_result_test_one = MonitorResult()
    monitor_thread = threading.Thread(
        target=monitor_command, args=(ctrl, NODE_FOO, monitor_result_test_one)
    )

    monitor_thread.start()
    try:
        with Timeout(SLEEP_DURATION, f"Timeout while monitoring {NODE_FOO}"):
            monitor_thread.join()
    except TimeoutError:
        LOGGER.debug(
            "Timeout reached while monitoring NODE_FOO. Attempting to terminate."
        )

    assert (
        monitor_result_test_one.result is None
    ), "Monitor command should not produce output when node is running."

    # Test 2: Stop NODE_FOO and verify monitoring detects the failure
    LOGGER.debug("Starting monitor thread before stopping NODE_FOO.")
    monitor_result_test_two = MonitorResult()
    monitor_thread = threading.Thread(
        target=monitor_command, args=(ctrl, NODE_FOO, monitor_result_test_two)
    )
    monitor_thread.start()
    time.sleep(SLEEP_DURATION)

    LOGGER.debug("Stopping NODE_FOO.")
    node_foo.systemctl.stop_unit("bluechi-agent")
    assert node_foo.wait_for_unit_state_to_be("bluechi-agent", "inactive")
    monitor_thread.join()
    assert (
        monitor_result_test_two.result is not None
        and monitor_result_test_two.output != ""
    ), "Monitor command should produce a output when NODE_FOO is stopped."


def test_bluechi_is_online_node_monitor(
    bluechi_test: BluechiTest,
    bluechi_node_default_config: BluechiAgentConfig,
    bluechi_ctrl_default_config: BluechiControllerConfig,
):
    node_foo_cfg = bluechi_node_default_config.deep_copy()
    node_foo_cfg.node_name = NODE_FOO

    bluechi_ctrl_default_config.allowed_node_names = [NODE_FOO]

    bluechi_test.set_bluechi_controller_config(bluechi_ctrl_default_config)
    bluechi_test.add_bluechi_agent_config(node_foo_cfg)

    bluechi_test.run(exec)