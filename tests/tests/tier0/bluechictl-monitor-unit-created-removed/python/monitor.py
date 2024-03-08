# SPDX-License-Identifier: LGPL-2.1-or-later

import signal
import subprocess
import tempfile
import threading
import time
import unittest

node_name_foo = "node-foo"

service_simple = "simple.service"


class FileFollower:
    def __init__(self, file_name):
        self.pos = 0
        self.file_name = file_name
        self.file_desc = None

    def __enter__(self):
        self.file_desc = open(self.file_name, mode='r')
        return self

    def __exit__(self, exception_type, exception_value, exception_traceback):
        if exception_type or exception_type or exception_traceback:
            print(f"Exception raised: exception_type='{exception_type}', "
                  f"exception_value='{exception_value}', exception_traceback: {exception_traceback}")
        if self.file_desc:
            self.file_desc.close()

    def __iter__(self):
        while self.new_lines():
            self.seek()
            line = self.file_desc.read().split('\n')[0]
            yield line

            self.pos += len(line) + 1

    def seek(self):
        self.file_desc.seek(self.pos)

    def new_lines(self):
        self.seek()
        return '\n' in self.file_desc.read()


class TestMonitorSpecificNodeAndUnit(unittest.TestCase):

    def setUp(self) -> None:
        self.bluechictl_proc = None

        self.created = False
        self.removed = False

    def run_command(self, args, shell=True, **kwargs):
        process = subprocess.Popen(
                args,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                **kwargs)
        print(f"Executing of command '{process.args}' started")
        out, err = process.communicate()

        out = out.decode("utf-8")
        err = err.decode("utf-8")

        print(
            f"Executing of command '{process.args}' finished with result '{process.returncode}', "
            f"stdout '{out}', stderr '{err}'")

        return process.returncode, out, err

    def timeout_guard(self):
        time.sleep(10)
        print(f"Loop timeout - UnitRemoved signal for service '{service_simple}' on node '{node_name_foo}' "
              f"was not successfully received on time")
        self.bluechictl_proc.send_signal(signal.SIGINT)
        self.bluechictl_proc.wait()

    def process_events(self):
        out_file = None

        with tempfile.NamedTemporaryFile() as out_file:
            try:
                self.bluechictl_proc = subprocess.Popen(
                    ["/usr/bin/bluechictl", "monitor", f"{node_name_foo}", f"{service_simple}"],
                    stdout=out_file,
                    bufsize=1)

                with FileFollower(out_file.name) as bluechictl_out:
                    events_received = False
                    while not events_received and self.bluechictl_proc.poll() is None:
                        for line in bluechictl_out:
                            print(f"Evaluating line '{line}'")
                            if not self.created and "Unit created (reason: real)" in line:
                                print(f"Received UnitCreated signal for service '{service_simple}' "
                                      f"on node '{node_name_foo}'")
                                self.created = True

                            elif self.created and not self.removed and "Unit removed (reason: real)" in line:
                                print(f"Received UnitRemoved signal for service '{service_simple}' "
                                      f"on node '{node_name_foo}'")
                                self.removed = True
                                events_received = True
                                break

                            else:
                                print(f"Ignoring line '{line}'")

                        # Wait for the new output from bluechictl monitor
                        time.sleep(0.5)
            finally:
                if self.bluechictl_proc:
                    self.bluechictl_proc.send_signal(signal.SIGINT)
                    self.bluechictl_proc.wait()
                    self.bluechictl_proc = None

    def test_monitor_specific_node_and_unit(self):
        t = threading.Thread(target=self.process_events)
        # mark the failsafe thread as daemon so it stops when the main process stops
        failsafe_thread = threading.Thread(target=self.timeout_guard, daemon=True)
        t.start()
        failsafe_thread.start()

        # Running bluechictl status on inactive unit should raise UnitCreated and UnitRemoved signals
        res, out, _ = self.run_command(f"bluechictl status {node_name_foo} {service_simple}")
        assert res == 0
        assert "inactive" in out

        t.join()

        assert self.created
        assert self.removed


if __name__ == "__main__":
    unittest.main()
