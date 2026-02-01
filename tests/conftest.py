def pytest_ignore_collect(path, config):
    p = str(path)

    if "tests/integration" in p:
        return True

    if "test_temporal.py" in p:
        return True

    if "test_worm.py" in p:
        return True

    if "tests/benchmarks" in p:
        return True

    if "test_synthetic_pipeline.py" in p:
        return True

    return False
