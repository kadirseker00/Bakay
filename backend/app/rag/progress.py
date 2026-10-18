"""Sorguya özel, isteğe bağlı işlem bildirimleri; model akıl yürütmesi içermez."""
from collections.abc import Callable
from contextlib import contextmanager
from contextvars import ContextVar


_listener: ContextVar[Callable[[dict], None] | None] = ContextVar("rag_progress", default=None)


@contextmanager
def progress_scope(listener: Callable[[dict], None]):
    token = _listener.set(listener)
    try:
        yield
    finally:
        _listener.reset(token)


def report(stage: str, title: str, detail: str) -> None:
    listener = _listener.get()
    if listener is not None:
        listener({"stage": stage, "title": title, "detail": detail})
