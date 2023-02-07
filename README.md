# Hirte

Hirte is a service orchestrator tool intended for multi-node devices
(e.g.: edge devices) clusters with a predefined number of nodes and with a focus
on highly regulated environment such as those requiring functional safety
(for example in cars).

Hirte is relying on [systemd][1] and its D-Bus API, which it extends for
multi-node use case.

Hirte can also be used to orchestrate containers using [podman][2] and its
ability to generate systemd service configuration to run a container.

## How to contribute

### Submitting patches

Patches are welcome!

Please submit patches to [github.com:containers/hirte][3].
More infomation about the development can be found in
[README.developer](README.developer.md).

If you are not familiar with the development process you can read about it in
[Get started with GitHub][4].

### Found a bug or documentation issue?

To submit a bug or suggest an enhancement for hirte please use [GitHub issues][5].

## Still need help?

If you have any other questions, please join
[CentOS Automotive SIG mailing list][6] and ask there.

[1]: https://github.com/systemd/systemd
[2]: https://github.com/containers/podman/
[3]: https://github.com/containers/hirte
[4]: https://docs.github.com/en/get-started
[5]: https://github.com/containers/hirte/issues
[6]: https://lists.centos.org/mailman/listinfo/centos-automotive-sig/
