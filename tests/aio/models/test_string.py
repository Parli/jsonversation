import jsonversation.aio as jv


def test_string_init() -> None:
    string_obj = jv.String()
    assert string_obj._value.getvalue() == ""
    assert string_obj._on_append_funcs == []


def test_string_update_empty_buffer() -> None:
    string_obj = jv.String()
    string_obj.update("hello")

    assert string_obj._value.getvalue() == "hello"


def test_string_update_same_value() -> None:
    string_obj = jv.String()
    string_obj.update("hello")

    string_obj.update("hello")

    assert string_obj._value.getvalue() == "hello"


def test_string_update_incremental() -> None:
    string_obj = jv.String()
    string_obj.update("hello")
    string_obj.update("hello world")

    assert string_obj._value.getvalue() == "hello world"


def test_string_update_multiple_increments() -> None:
    string_obj = jv.String()
    string_obj.update("a")
    string_obj.update("ab")
    string_obj.update("abc")
    string_obj.update("abcd")

    assert string_obj._value.getvalue() == "abcd"


def test_string_update_empty_string() -> None:
    string_obj = jv.String()
    string_obj.update("")

    assert string_obj._value.getvalue() == ""


def test_string_update_shorter_value() -> None:
    string_obj = jv.String()
    string_obj.update("hello world")
    string_obj.update("hello")  # Shorter than current

    assert string_obj._value.getvalue() == "hello world"


def test_on_append_single_callback() -> None:
    string_obj = jv.String()
    called_chunks = []

    def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    string_obj.update("hello")

    assert called_chunks == ["hello"]
    assert string_obj._value.getvalue() == "hello"


def test_on_append_multiple_callbacks() -> None:
    string_obj = jv.String()
    called_chunks_1 = []
    called_chunks_2 = []

    def callback1(chunk: str) -> None:
        called_chunks_1.append(chunk)

    def callback2(chunk: str) -> None:
        called_chunks_2.append(chunk)

    string_obj.on_append(callback1)
    string_obj.on_append(callback2)
    string_obj.update("hello")

    assert called_chunks_1 == ["hello"]
    assert called_chunks_2 == ["hello"]


def test_on_append_incremental_updates() -> None:
    string_obj = jv.String()
    called_chunks = []

    def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    string_obj.update("hello")
    string_obj.update("hello world")
    string_obj.update("hello world!")

    assert called_chunks == ["hello", " world", "!"]
    assert string_obj._value.getvalue() == "hello world!"


def test_on_append_no_callback_on_same_value() -> None:
    string_obj = jv.String()
    called_chunks = []

    def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    string_obj.update("hello")
    string_obj.update("hello")  # Same value, should not trigger callback

    assert called_chunks == ["hello"]


def test_on_append_no_callback_on_shorter_value() -> None:
    string_obj = jv.String()
    called_chunks = []

    def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    string_obj.update("hello world")
    string_obj.update("hello")  # Shorter value, should not trigger callback

    assert called_chunks == ["hello world"]


def test_on_append_callback_order() -> None:
    """Test callbacks are called in the order they were registered."""
    string_obj = jv.String()
    call_order = []

    def callback1(chunk: str) -> None:
        call_order.append("callback1")

    def callback2(chunk: str) -> None:
        call_order.append("callback2")

    def callback3(chunk: str) -> None:
        call_order.append("callback3")

    string_obj.on_append(callback1)
    string_obj.on_append(callback2)
    string_obj.on_append(callback3)
    string_obj.update("test")

    assert call_order == ["callback1", "callback2", "callback3"]


def test_complex_streaming_scenario() -> None:
    """Test a complex streaming scenario with multiple updates and callbacks."""
    string_obj = jv.String()
    received_chunks = []
    full_content = []

    def chunk_handler(chunk: str) -> None:
        received_chunks.append(chunk)

    def content_handler(chunk: str) -> None:
        full_content.append(string_obj._value.getvalue())

    string_obj.on_append(chunk_handler)
    string_obj.on_append(content_handler)

    # Simulate streaming updates
    string_obj.update("The")
    string_obj.update("The quick")
    string_obj.update("The quick brown")
    string_obj.update("The quick brown fox")

    assert received_chunks == ["The", " quick", " brown", " fox"]
    assert full_content == [
        "The",
        "The quick",
        "The quick brown",
        "The quick brown fox",
    ]
    assert string_obj._value.getvalue() == "The quick brown fox"


def test_string_on_complete_single_callback() -> None:
    string_obj = jv.String()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    string_obj.update("hello world")
    string_obj._complete()

    assert completed_values == ["hello world"]


def test_string_on_complete_multiple_callbacks() -> None:
    string_obj = jv.String()
    completed_values_1 = []
    completed_values_2 = []

    def callback1(value: str) -> None:
        completed_values_1.append(value)

    def callback2(value: str) -> None:
        completed_values_2.append(value)

    string_obj.on_complete(callback1)
    string_obj.on_complete(callback2)
    string_obj.update("test value")
    string_obj._complete()

    assert completed_values_1 == ["test value"]
    assert completed_values_2 == ["test value"]


def test_string_on_complete_callback_order() -> None:
    """Test callbacks are called in the order they were registered."""
    string_obj = jv.String()
    call_order = []

    def callback1(value: str) -> None:
        call_order.append("callback1")

    def callback2(value: str) -> None:
        call_order.append("callback2")

    def callback3(value: str) -> None:
        call_order.append("callback3")

    string_obj.on_complete(callback1)
    string_obj.on_complete(callback2)
    string_obj.on_complete(callback3)
    string_obj.update("test")
    string_obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


def test_string_complete_empty_value() -> None:
    """Test complete method with empty string value."""
    string_obj = jv.String()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    string_obj._complete()

    assert completed_values == [""]


def test_string_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    string_obj = jv.String()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    string_obj.update("hello")
    string_obj._complete()
    string_obj._complete()

    assert completed_values == ["hello", "hello"]


def test_string_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    string_obj = jv.String()
    string_obj.update("test")
    # Should not raise an exception
    string_obj._complete()
