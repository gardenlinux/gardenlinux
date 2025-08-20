## Markers

Tests can be decorated with pytest markers to indicate certain limitations or properties of the test:

`@pytest.mark.booted`: This test can only be run in a booted system, not in a chroot test.


`@pytest.mark.modify`: This test modifies the underlying system, like starting services, installing software or creating files.

`@pytest.mark.root`: This test is run as the root user, not as an unprivileged user.


`@pytest.mark.feature("a and not b")`: This test is only run if the boolean condition is true. Use this to limit feature-specific tests.

`@pytest.mark.performance_metric`: This is a performance metric test that can be skipped when running under emulation.
