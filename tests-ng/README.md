### Markers

Tests can be decorated with pytest markers to indicate certain limitations or properties of the test:

`@pytest.mark.booted(reason="Some reason, this is optional")`: This test can only be run in a booted system, not in a chroot test. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.modify(reason="Some reason, this is optional")`: This test modifies the underlying system, like starting services, installing software or creating files. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.root(reason="Some reason, this is optional")`: This test is run as the root user, not as an unprivileged user. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.feature("a and not b", reason="Some reason, this is optional")`: This test is only run if the boolean condition is true. Use this to limit feature-specific tests. Use the optional `reason` argument to document why this is needed, in cases where this is not really obvious.

`@pytest.mark.performance_metric`: This is a performance metric test that can be skipped when running under emulation.
