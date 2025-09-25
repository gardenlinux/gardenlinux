import pytest
from plugins.sysdiff import Sysdiff


@pytest.mark.order("first")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_before_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs before all other tests and creates the before-tests snapshot.
    """
    name_a = "before-tests"
    try:
        snapshot = sysdiff.create_snapshot(name_a)
        assert snapshot.name == name_a

    except Exception as e:
        pytest.fail(f"Error creating {name_a} snapshot: {e}")


@pytest.mark.order("last")
@pytest.mark.root(reason="Sysdiff needs to read all files.")
def test_sysdiff_after_tests(sysdiff: Sysdiff):
    """
    Verifies no system changes were detected during the test run.
    This test runs after all other tests, creates the after-tests snapshot and performs the sysdiff comparison.
    """
    name_a = "before-tests"
    name_b = "after-tests"
    try:
        snapshot = sysdiff.create_snapshot(name_b)
        assert snapshot.name == name_b

        diff_result = sysdiff.compare_snapshots(name_a, name_b)

        if diff_result.has_changes:
            diff_output = sysdiff.diff_engine.generate_diff(diff_result, name_a, name_b)
            pytest.fail(f"System changes were detected during the test run:\n{diff_output}")
        else:
            assert True

    except Exception as e:
        pytest.fail(f"Error during sysdiff comparison: {e}")

    finally:
        sysdiff.cleanup_snapshots([name_a, name_b])
