import pytest
from plugins.sysdiff import Sysdiff

before_suffix = "before-tests"
after_suffix = "after-tests"


@pytest.mark.order("first")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_before_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs before all other tests and creates the before-tests snapshot.
    """
    try:
        snapshot = sysdiff.create_snapshot(before_suffix)
        assert before_suffix in snapshot.name

    except Exception as e:
        pytest.fail(f"Error creating {before_suffix} snapshot: {e}")


@pytest.mark.order("last")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_after_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs after all other tests, creates the after-tests snapshot and performs the sysdiff comparison.
    """
    before_snapshot = None
    after_snapshot = None
    try:
        snapshots = sysdiff.manager.list_snapshots()
        before_snapshot = next(
            (s for s in reversed(snapshots) if s.endswith(f"-{before_suffix}")),
            None,
        )
        assert (
            before_snapshot is not None
        ), f"{before_suffix} snapshot not found. Make sure test_sysdiff_before_tests ran first."

        after_snapshot = sysdiff.create_snapshot(after_suffix).name

        diff_result = sysdiff.compare_snapshots(before_snapshot, after_snapshot)
        if diff_result.has_changes:
            diff_output = sysdiff.diff_engine.generate_diff(
                diff_result, before_snapshot, after_snapshot
            )
            print(f"{diff_output=}")
            pytest.fail(
                "System changes were detected during the test run. See stderr output for details."
            )

    except Exception as e:
        pytest.fail(f"Error during sysdiff comparison: {e}")

    finally:
        cleanup_names = []
        if before_snapshot:
            cleanup_names.append(before_snapshot)
        if after_snapshot:
            cleanup_names.append(after_snapshot)
        if cleanup_names:
            sysdiff.cleanup_snapshots(cleanup_names)
