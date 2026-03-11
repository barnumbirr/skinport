import logging
from unittest.mock import MagicMock, patch

import pytest

from skinport import SaleFeed


class TestSaleFeedInit:
    def test_defaults(self):
        feed = SaleFeed()
        assert feed.app_id == 730
        assert feed.currency == "EUR"
        assert feed.locale == "en"

    def test_custom_params(self):
        feed = SaleFeed(app_id=440, currency="USD", locale="de")
        assert feed.app_id == 440
        assert feed.currency == "USD"
        assert feed.locale == "de"

    def test_keyword_only_args(self):
        with pytest.raises(TypeError):
            SaleFeed(730, "EUR", "en")

    def test_default_base_url(self):
        feed = SaleFeed()
        assert feed.base_url == "https://skinport.com"

    def test_custom_base_url(self):
        feed = SaleFeed(base_url="https://custom.example.com")
        assert feed.base_url == "https://custom.example.com"

    def test_default_reconnect(self):
        feed = SaleFeed()
        assert feed.reconnect is True
        assert feed.reconnect_delay == 5

    def test_custom_reconnect(self):
        feed = SaleFeed(reconnect=False, reconnect_delay=10)
        assert feed.reconnect is False
        assert feed.reconnect_delay == 10

    def test_initial_state(self):
        feed = SaleFeed()
        assert feed._callbacks == []
        assert feed._disconnect_callbacks == []
        assert feed._sio is None
        assert feed.connected is False


class TestSaleFeedRepr:
    def test_disconnected(self):
        feed = SaleFeed()
        assert repr(feed) == "<skinport.SaleFeed [disconnected]>"

    def test_connected(self):
        feed = SaleFeed()
        feed._sio = MagicMock()
        feed._sio.connected = True
        assert repr(feed) == "<skinport.SaleFeed [connected]>"


class TestSaleFeedCallbacks:
    def test_on_event_registers_callback(self):
        feed = SaleFeed()

        @feed.on_event
        def handler(data):
            pass

        assert handler in feed._callbacks

    def test_on_event_returns_original_function(self):
        feed = SaleFeed()

        def handler(data):
            pass

        result = feed.on_event(handler)
        assert result is handler

    def test_multiple_callbacks(self):
        feed = SaleFeed()
        calls = []

        @feed.on_event
        def first(data):
            calls.append(("first", data))

        @feed.on_event
        def second(data):
            calls.append(("second", data))

        feed._dispatch({"eventType": "listed", "sales": []})

        assert len(calls) == 2
        assert calls[0][0] == "first"
        assert calls[1][0] == "second"

    def test_dispatch_passes_data(self):
        feed = SaleFeed()
        received = []

        @feed.on_event
        def handler(data):
            received.append(data)

        payload = {"eventType": "sold", "sales": [{"id": 1}]}
        feed._dispatch(payload)

        assert received == [payload]

    def test_dispatch_with_no_callbacks(self):
        feed = SaleFeed()
        feed._dispatch({"eventType": "listed", "sales": []})  # should not raise

    def test_callbacks_called_in_order(self):
        feed = SaleFeed()
        order = []

        for i in range(5):
            feed.on_event(lambda data, idx=i: order.append(idx))

        feed._dispatch({})
        assert order == [0, 1, 2, 3, 4]

    def test_dispatch_continues_after_callback_error(self):
        feed = SaleFeed()
        calls = []

        @feed.on_event
        def first(data):
            calls.append("first")

        @feed.on_event
        def bad(data):
            raise RuntimeError("boom")

        @feed.on_event
        def third(data):
            calls.append("third")

        feed._dispatch({"eventType": "listed", "sales": []})

        assert calls == ["first", "third"]

    def test_dispatch_logs_callback_exception(self, caplog):
        feed = SaleFeed()

        @feed.on_event
        def bad(data):
            raise ValueError("test error")

        with caplog.at_level(logging.ERROR, logger="skinport.salefeed"):
            feed._dispatch({})

        assert "raised an exception" in caplog.text
        assert "test error" in caplog.text


class TestSaleFeedConnection:
    def test_connected_property_false_when_no_sio(self):
        feed = SaleFeed()
        assert feed.connected is False

    def test_connected_property_true(self):
        feed = SaleFeed()
        feed._sio = MagicMock()
        feed._sio.connected = True
        assert feed.connected is True

    def test_connected_property_false_when_sio_disconnected(self):
        feed = SaleFeed()
        feed._sio = MagicMock()
        feed._sio.connected = False
        assert feed.connected is False

    def test_disconnect_when_connected(self):
        feed = SaleFeed()
        feed._sio = MagicMock()
        feed._sio.connected = True
        feed.disconnect()
        feed._sio.disconnect.assert_called_once()

    def test_disconnect_when_not_connected(self):
        feed = SaleFeed()
        feed.disconnect()  # should not raise (even without prior connect)

    def test_disconnect_before_connect_does_not_crash(self):
        feed = SaleFeed()
        feed.disconnect()
        assert feed._intentional_disconnect is True

    def test_disconnect_when_sio_exists_but_disconnected(self):
        feed = SaleFeed()
        feed._sio = MagicMock()
        feed._sio.connected = False
        feed.disconnect()
        feed._sio.disconnect.assert_not_called()

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_creates_sio_client(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed()
        feed.connect(background=True)

        mock_client_cls.assert_called_once()
        mock_sio.connect.assert_called_once_with(
            "https://skinport.com",
            transports=["websocket"],
        )

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_uses_custom_base_url(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed(base_url="https://custom.example.com")
        feed.connect(background=True)

        mock_sio.connect.assert_called_once_with(
            "https://custom.example.com",
            transports=["websocket"],
        )

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_blocking_calls_wait(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed()
        feed.connect(background=False)

        mock_sio.wait.assert_called_once()

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_background_skips_wait(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed()
        feed.connect(background=True)

        mock_sio.wait.assert_not_called()

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_registers_salefeed_handler(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed()
        feed.connect(background=True)

        # Verify on("saleFeed") was called as a decorator
        mock_sio.on.assert_called_with("saleFeed")

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_emits_join_on_connect_event(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        # Capture all event handlers by name
        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(app_id=440, currency="USD", locale="de")
        feed.connect(background=True)

        # Simulate the connect event firing
        assert "connect" in handlers
        handlers["connect"]()

        mock_sio.emit.assert_called_once_with(
            "saleFeedJoin",
            {"currency": "USD", "locale": "de", "appid": 440},
        )

    @patch("skinport.salefeed.socketio.Client")
    def test_connect_registers_disconnect_handler(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed()
        feed.connect(background=True)

        assert "disconnect" in handlers

    @patch("skinport.salefeed.socketio.Client")
    def test_disconnect_sets_intentional_flag(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_sio.connected = True
        mock_client_cls.return_value = mock_sio

        feed = SaleFeed()
        feed.connect(background=True)
        feed.disconnect()

        assert feed._intentional_disconnect is True


class TestSaleFeedDisconnectCallbacks:
    def test_on_disconnect_registers_callback(self):
        feed = SaleFeed()

        @feed.on_disconnect
        def handler():
            pass

        assert handler in feed._disconnect_callbacks

    def test_on_disconnect_returns_original_function(self):
        feed = SaleFeed()

        def handler():
            pass

        result = feed.on_disconnect(handler)
        assert result is handler

    def test_disconnect_callbacks_called(self):
        feed = SaleFeed()
        calls = []

        @feed.on_disconnect
        def handler():
            calls.append("called")

        feed._dispatch_disconnect()
        assert calls == ["called"]

    def test_disconnect_callback_error_continues(self):
        feed = SaleFeed()
        calls = []

        @feed.on_disconnect
        def first():
            calls.append("first")

        @feed.on_disconnect
        def bad():
            raise RuntimeError("boom")

        @feed.on_disconnect
        def third():
            calls.append("third")

        feed._dispatch_disconnect()
        assert calls == ["first", "third"]

    def test_disconnect_callback_error_logged(self, caplog):
        feed = SaleFeed()

        @feed.on_disconnect
        def bad():
            raise ValueError("disconnect error")

        with caplog.at_level(logging.ERROR, logger="skinport.salefeed"):
            feed._dispatch_disconnect()

        assert "raised an exception" in caplog.text
        assert "disconnect error" in caplog.text


class TestSaleFeedReconnect:
    @patch("skinport.salefeed.socketio.Client")
    def test_reconnect_on_unexpected_disconnect(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(reconnect=True, reconnect_delay=0)
        feed.connect(background=True)

        # Initial connect
        assert mock_sio.connect.call_count == 1

        # Simulate unexpected disconnect
        handlers["disconnect"]()

        # Should have reconnected
        assert mock_sio.connect.call_count == 2

    @patch("skinport.salefeed.socketio.Client")
    def test_no_reconnect_on_intentional_disconnect(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_sio.connected = True
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(reconnect=True)
        feed.connect(background=True)

        # Mark as intentional, then simulate disconnect event
        feed._intentional_disconnect = True
        handlers["disconnect"]()

        # Should NOT have reconnected (only original connect)
        assert mock_sio.connect.call_count == 1

    @patch("skinport.salefeed.socketio.Client")
    def test_no_reconnect_when_disabled(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(reconnect=False)
        feed.connect(background=True)

        # Simulate unexpected disconnect
        handlers["disconnect"]()

        # Should NOT have reconnected
        assert mock_sio.connect.call_count == 1

    @patch("skinport.salefeed.socketio.Client")
    def test_reconnect_failure_logged(self, mock_client_cls, caplog):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(reconnect=True, reconnect_delay=0)
        feed.connect(background=True)

        # Make the next connect (reconnect) fail
        mock_sio.connect.side_effect = ConnectionError("refused")

        with caplog.at_level(logging.ERROR, logger="skinport.salefeed"):
            handlers["disconnect"]()

        assert "Failed to reconnect" in caplog.text

    @patch("skinport.salefeed.socketio.Client")
    def test_reconnect_respects_delay(self, mock_client_cls):
        mock_sio = MagicMock()
        mock_client_cls.return_value = mock_sio

        handlers = {}

        def capture_event(func):
            handlers[func.__name__] = func
            return func

        mock_sio.event = capture_event

        feed = SaleFeed(reconnect=True, reconnect_delay=5)
        feed.connect(background=True)

        handlers["disconnect"]()

        mock_sio.sleep.assert_called_once_with(5)
