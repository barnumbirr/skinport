"""Real-time sale feed via WebSocket (Socket.IO)."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any

import socketio

logger = logging.getLogger(__name__)


class SaleFeed:
    """Live sale feed from the Skinport marketplace.

    Connects to the Skinport Socket.IO endpoint and dispatches
    real-time events for new listings and completed sales.

    Usage::

        from skinport import SaleFeed

        feed = SaleFeed(app_id=730, currency="EUR", locale="en")

        @feed.on_event
        def handle(data):
            print(data["eventType"], data["sales"])

        feed.connect()  # blocks until disconnected

    :param app_id: game app ID (default ``730`` for CS2).
    :param currency: pricing currency code (default ``EUR``).
    :param locale: result language (default ``en``).
        Supported: en, de, ru, fr, zh, nl, fi, es, tr.
    :param base_url: override the default Socket.IO endpoint URL.
    :param reconnect: automatically reconnect on disconnection
        (default ``True``).
    :param reconnect_delay: seconds to wait before reconnecting
        (default ``5``).
    """

    def __init__(
        self,
        *,
        app_id: int = 730,
        currency: str = "EUR",
        locale: str = "en",
        base_url: str = "https://skinport.com",
        reconnect: bool = True,
        reconnect_delay: float = 5,
    ) -> None:
        self.app_id = app_id
        self.currency = currency
        self.locale = locale
        self.base_url = base_url
        self.reconnect = reconnect
        self.reconnect_delay = reconnect_delay
        self._callbacks: list[Callable[[dict[str, Any]], Any]] = []
        self._disconnect_callbacks: list[Callable[[], Any]] = []
        self._sio: socketio.Client | None = None
        self._intentional_disconnect = False

    def __repr__(self) -> str:
        state = "connected" if self.connected else "disconnected"
        return f"<skinport.SaleFeed [{state}]>"

    @property
    def connected(self) -> bool:
        """Whether the feed is currently connected."""
        return self._sio is not None and self._sio.connected

    def on_event(
        self, func: Callable[[dict[str, Any]], Any]
    ) -> Callable[[dict[str, Any]], Any]:
        """Register a callback for sale feed events.

        The callback receives a dict with ``'eventType'``
        (``'listed'`` or ``'sold'``) and ``'sales'`` (list of item
        dicts).

        Can be used as a decorator::

            @feed.on_event
            def handle(data):
                ...

        :param func: callable that accepts a single dict argument.
        :return: the original function, unmodified.
        """
        self._callbacks.append(func)
        return func

    def on_disconnect(
        self, func: Callable[[], Any]
    ) -> Callable[[], Any]:
        """Register a callback for disconnection events.

        The callback receives no arguments and is called whenever the
        feed disconnects from the server.

        Can be used as a decorator::

            @feed.on_disconnect
            def handle():
                ...

        :param func: callable that accepts no arguments.
        :return: the original function, unmodified.
        """
        self._disconnect_callbacks.append(func)
        return func

    def _dispatch_disconnect(self) -> None:
        for callback in self._disconnect_callbacks:
            try:
                callback()
            except Exception:
                logger.exception(
                    "Disconnect callback %r raised an exception", callback
                )

    def _dispatch(self, data: dict[str, Any]) -> None:
        for callback in self._callbacks:
            try:
                callback(data)
            except Exception:
                logger.exception("Sale feed callback %r raised an exception", callback)

    def connect(self, *, background: bool = False) -> None:
        """Connect to the sale feed and start receiving events.

        :param background: if ``True``, connect in the background and
            return immediately.  Call :meth:`disconnect` to stop.
        """
        self._intentional_disconnect = False
        self._sio = socketio.Client(reconnection=False)

        @self._sio.on("saleFeed")
        def _on_sale_feed(data: dict[str, Any]) -> None:
            self._dispatch(data)

        @self._sio.event
        def connect() -> None:
            self._sio.emit(
                "saleFeedJoin",
                {
                    "currency": self.currency,
                    "locale": self.locale,
                    "appid": self.app_id,
                },
            )

        @self._sio.event
        def disconnect() -> None:
            self._dispatch_disconnect()
            if self.reconnect and not self._intentional_disconnect:
                logger.info(
                    "Disconnected from sale feed, reconnecting in %.1fs",
                    self.reconnect_delay,
                )
                self._sio.sleep(self.reconnect_delay)
                try:
                    self._sio.connect(
                        self.base_url,
                        transports=["websocket"],
                    )
                except Exception:
                    logger.exception("Failed to reconnect to sale feed")

        self._sio.connect(
            self.base_url,
            transports=["websocket"],
        )

        if not background:
            self._sio.wait()

    def disconnect(self) -> None:
        """Disconnect from the sale feed."""
        self._intentional_disconnect = True
        if self.connected:
            self._sio.disconnect()
