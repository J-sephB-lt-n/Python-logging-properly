"""
Functions for global logging setup.
"""

import atexit
import logging
import logging.config
import os
import platform
import psutil
import socket
from pathlib import Path
from types import MappingProxyType

import yaml

from src.logging_utils.session import _log_session_vars

_HOSTNAME = socket.gethostname()
_PYTHON_VERSION = platform.python_version()
_PLATFORM = platform.platform()
_PROC = psutil.Process(os.getpid())


def setup_logging() -> None:
    """Once-off global setup of application logging."""
    config_file = Path("./config/logging_config.yaml")
    with config_file.open("r", encoding="utf-8") as file:
        config: dict = yaml.safe_load(file)

    logging.config.dictConfig(config)

    old_record_factory = logging.getLogRecordFactory()

    def record_factory(*args, **kwargs):
        record = old_record_factory(*args, **kwargs)
        _enrich_log_record(record)
        return record

    logging.setLogRecordFactory(record_factory)

    queue_handler = logging.getHandlerByName("queue_handler")
    queue_handler.listener.start()
    atexit.register(queue_handler.listener.stop)


def _enrich_log_record(record) -> None:
    """Enrich `record` with available useful metrics."""
    # log_session() variables #
    session_vars: MappingProxyType | None = _log_session_vars.get()
    if session_vars:
        for key, value in session_vars.items():
            if hasattr(record, key):
                raise AttributeError(
                    f"Cannot overwrite existing attribute '{key}' on log record."
                )
            setattr(record, key, value)

    # system metrics #
    record.pid = os.getpid()
    record.ppid = os.getppid()
    record.hostname = _HOSTNAME
    # record.ip_address = socket.gethostbyname(socket.gethostname())
    record.python_version = _PYTHON_VERSION
    record.platform = _PLATFORM
    # record.process_cpu_percent = _PROC.cpu_percent(None)
    # record.system_cpu_percent = psutil.cpu_percent(interval=None)
    # record.mem_total = psutil.virtual_memory().total
    # record.mem_used = psutil.virtual_memory().used
    # record.mem_percent = psutil.virtual_memory().percent
    record.mem_rss_mb = _PROC.memory_info().rss / (1024 * 1024)
    # record.mem_vms = psutil.Process().memory_info().vms
    record.num_threads = _PROC.num_threads()
    # record.open_files = len(psutil.Process().open_files())
    # record.disk_usage_percent = psutil.disk_usage("/").percent
    # record.boot_time = psutil.boot_time()
    # record.uptime = time.time() - _PROC.create_time()
    # record.container_id = open("/proc/self/cgroup").read().split("/")[-1].strip()
