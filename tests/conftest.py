import os
import sys
import tempfile
import subprocess
import socket
import time

import pytest


_AUDIT_TMP = None
_STORAGE_TMP = None
_POSTGRES_PROC = None
_POSTGRES_DATA = None
_REDIS_PROC = None


def _set_default_env(key: str, value: str) -> None:
    if not os.getenv(key):
        os.environ[key] = value


def pytest_configure():
    # Ensure repo and src are importable in clean environments.
    repo_root = os.path.realpath(os.path.join(os.path.dirname(__file__), ".."))
    src_root = os.path.join(repo_root, "src")
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    if os.path.isdir(src_root) and src_root not in sys.path:
        sys.path.insert(0, src_root)

    # Ensure test environment defaults are always set before imports.
    _set_default_env("PV_ENV", "test")
    _set_default_env("PV_CONTEXT_KEYS", "{\"k1\":\"test-secret\"}")
    _set_default_env("PV_QUORUM_MIN", "2")

    global _STORAGE_TMP, _AUDIT_TMP
    if not os.getenv("PV_STORAGE_PATH"):
        _STORAGE_TMP = tempfile.TemporaryDirectory(prefix="pv_test_storage_")
        os.environ["PV_STORAGE_PATH"] = _STORAGE_TMP.name

    if not os.getenv("PV_AUDIT_LOG_PATH"):
        _AUDIT_TMP = tempfile.NamedTemporaryFile(
            prefix="pv_test_audit_", suffix=".log", delete=False
        )
        os.environ["PV_AUDIT_LOG_PATH"] = _AUDIT_TMP.name
        _AUDIT_TMP.close()

    audit_path = os.getenv("PV_AUDIT_LOG_PATH")
    if audit_path and not os.path.exists(audit_path):
        open(audit_path, "a").close()

    # Provide minimal temporalio fallback if dependency is unavailable.
    try:
        import temporalio  # noqa: F401
    except Exception:
        import types
        import contextlib

        temporalio_module = types.ModuleType("temporalio")
        testing_module = types.ModuleType("temporalio.testing")
        worker_module = types.ModuleType("temporalio.worker")

        class _WorkflowEnv:
            @classmethod
            async def start_time_skipping(cls):
                @contextlib.asynccontextmanager
                async def _cm():
                    yield cls()

                return _cm()

        class _Worker:
            def __init__(self, *args, **kwargs):
                pass

        testing_module.WorkflowEnvironment = _WorkflowEnv
        worker_module.Worker = _Worker
        sys.modules["temporalio"] = temporalio_module
        sys.modules["temporalio.testing"] = testing_module
        sys.modules["temporalio.worker"] = worker_module

    _ensure_local_postgres_or_fake()
    _ensure_local_redis_or_fake()


@pytest.fixture(scope="session", autouse=True)
def _test_env_session():
    yield
    global _AUDIT_TMP, _STORAGE_TMP
    audit_path = os.getenv("PV_AUDIT_LOG_PATH")
    if _AUDIT_TMP and audit_path and os.path.exists(audit_path):
        try:
            os.remove(audit_path)
        except Exception:
            pass
    if _STORAGE_TMP:
        _STORAGE_TMP.cleanup()
    _stop_postgres()
    _stop_redis()


def _port_open(host: str, port: int, timeout: float = 0.2) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False


def _ensure_local_postgres_or_fake() -> None:
    global _POSTGRES_PROC, _POSTGRES_DATA
    if _port_open("127.0.0.1", 5432):
        return
    _POSTGRES_DATA = tempfile.TemporaryDirectory(prefix="pv_pg_")
    data_dir = _POSTGRES_DATA.name
    pwfile = os.path.join(data_dir, "pwfile")
    with open(pwfile, "w", encoding="utf-8") as f:
        f.write("test_password")
    init_env = {**os.environ, "LC_ALL": "C", "LANG": "C"}
    try:
        subprocess.check_call(
            [
                "initdb",
                "-U",
                "galani",
                "-A",
                "password",
                "--pwfile",
                pwfile,
                "--locale",
                "C",
                "-D",
                data_dir,
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=init_env,
        )
        _POSTGRES_PROC = subprocess.Popen(
            ["postgres", "-D", data_dir, "-p", "5432"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(30):
            if _port_open("127.0.0.1", 5432):
                break
            time.sleep(0.1)
        subprocess.check_call(
            ["createdb", "-h", "127.0.0.1", "-p", "5432", "-U", "galani", "galani_test"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env={**os.environ, "PGPASSWORD": "test_password"},
        )
    except Exception:
        os.environ["PV_TEST_DB_MODE"] = "fake"
        _install_asyncpg_fake()


def _stop_postgres() -> None:
    global _POSTGRES_PROC, _POSTGRES_DATA
    if _POSTGRES_PROC:
        _POSTGRES_PROC.terminate()
        _POSTGRES_PROC.wait(timeout=5)
        _POSTGRES_PROC = None
    if _POSTGRES_DATA:
        _POSTGRES_DATA.cleanup()
        _POSTGRES_DATA = None


def _ensure_local_redis_or_fake() -> None:
    global _REDIS_PROC
    os.environ["RUN_REDIS_TESTS"] = "1"
    if _port_open("127.0.0.1", 6379):
        return
    try:
        _REDIS_PROC = subprocess.Popen(
            ["redis-server", "--port", "6379"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for _ in range(30):
            if _port_open("127.0.0.1", 6379):
                break
            time.sleep(0.1)
        if not _port_open("127.0.0.1", 6379):
            _install_redis_fake()
    except Exception:
        _install_redis_fake()


def _stop_redis() -> None:
    global _REDIS_PROC
    if _REDIS_PROC:
        _REDIS_PROC.terminate()
        _REDIS_PROC.wait(timeout=5)
        _REDIS_PROC = None


def _install_asyncpg_fake() -> None:
    import types

    asyncpg_module = types.ModuleType("asyncpg")

    class _InsufficientPrivilegeError(Exception):
        pass

    class _FakeConn:
        def __init__(self, state):
            self.state = state
            self._txn_failed = False
            self._txn_snapshot = None

        async def execute(self, query, *args):
            if "INSERT INTO agents" in query:
                agent_id = args[0]
                if agent_id in self.state["agents"]:
                    self._txn_failed = True
                    raise Exception("duplicate")
                self.state["agents"][agent_id] = {
                    "agent_id": args[0],
                    "name": args[1],
                    "status": args[2],
                }
                return "INSERT 1"
            if "INSERT INTO audit_log" in query:
                self.state["audit"].append(
                    {"agent_id": args[0], "action": args[1], "risk_score": args[2]}
                )
                return "INSERT 1"
            if "UPDATE audit_log" in query:
                self._txn_failed = True
                raise _InsufficientPrivilegeError()
            return "OK"

        async def fetchrow(self, query, *args):
            if "FROM agents" in query:
                return self.state["agents"].get(args[0])
            return None

        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc, tb):
            return False

        def transaction(self):
            conn = self

            class _Transaction:
                async def __aenter__(self_inner):
                    conn._txn_snapshot = {
                        "agents": dict(conn.state["agents"]),
                        "audit": list(conn.state["audit"]),
                    }
                    conn._txn_failed = False
                    return conn

                async def __aexit__(self_inner, exc_type, exc, tb):
                    if exc_type or conn._txn_failed:
                        conn.state["agents"] = dict(conn._txn_snapshot["agents"])
                        conn.state["audit"] = list(conn._txn_snapshot["audit"])
                    conn._txn_snapshot = None
                    conn._txn_failed = False
                    return False

            return _Transaction()

    class _FakePool:
        def __init__(self):
            self.state = {"agents": {}, "audit": []}

        def acquire(self):
            pool = self

            class _Acquire:
                async def __aenter__(self_inner):
                    return _FakeConn(pool.state)

                async def __aexit__(self_inner, exc_type, exc, tb):
                    return False

            return _Acquire()

        async def close(self):
            return None

    async def create_pool(*args, **kwargs):
        return _FakePool()

    asyncpg_module.create_pool = create_pool
    asyncpg_module.exceptions = types.SimpleNamespace(
        InsufficientPrivilegeError=_InsufficientPrivilegeError
    )
    sys.modules["asyncpg"] = asyncpg_module


def _install_redis_fake() -> None:
    import types

    redis_module = types.ModuleType("redis")

    class _FakeRedis:
        def __init__(self, *args, **kwargs):
            self._store = {}

        def exists(self, key):
            return key in self._store

        def setex(self, key, ttl, value):
            self._store[key] = value
            return True

    redis_module.Redis = _FakeRedis
    sys.modules["redis"] = redis_module
