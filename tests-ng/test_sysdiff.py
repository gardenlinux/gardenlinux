import pytest
from plugins.sysdiff import Sysdiff


@pytest.mark.order("first")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_before_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs before all other tests and creates the before-tests snapshot.
    """
    name = "before-tests"
    try:
        snapshot = sysdiff.create_snapshot(name)
        pytest.before_tests_snapshot_name = snapshot.name
        assert name in snapshot.name

    except Exception as e:
        pytest.fail(f"Error creating {name} snapshot: {e}")


@pytest.mark.order("last")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_after_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs after all other tests, creates the after-tests snapshot and performs the sysdiff comparison.
    """
    name = "after-tests"
    try:
        snapshot = sysdiff.create_snapshot(name)
        after_tests_snapshot_name = snapshot.name
        assert name in snapshot.name

        before_tests_snapshot_name = getattr(pytest, 'before_tests_snapshot_name', None)
        if not before_tests_snapshot_name:
            pytest.fail("before-tests snapshot not found. Make sure test_sysdiff_before_tests ran first.")

        diff_result = sysdiff.compare_snapshots(before_tests_snapshot_name, after_tests_snapshot_name)

        if diff_result.has_changes:
            diff_output = sysdiff.diff_engine.generate_diff(diff_result, before_tests_snapshot_name, after_tests_snapshot_name)
            pytest.fail(f"System changes were detected during the test run:\n{diff_output}")
        else:
            assert True

    except Exception as e:
        pytest.fail(f"Error during sysdiff comparison: {e}")

    finally:
        cleanup_names = []
        if hasattr(pytest, 'before_tests_snapshot_name'):
            cleanup_names.append(pytest.before_tests_snapshot_name)
        if 'after_tests_snapshot_name' in locals():
            cleanup_names.append(after_tests_snapshot_name)
        if cleanup_names:
            sysdiff.cleanup_snapshots(cleanup_names)
