import jsonversation.aio as jv


async def test_string_init() -> None:
    string_obj = jv.String()
    assert string_obj._value.getvalue() == ""
    assert string_obj._on_append_funcs == []


async def test_string_update_empty_buffer() -> None:
    string_obj = jv.String()
    await string_obj.update("hello")

    assert string_obj._value.getvalue() == "hello"


async def test_string_update_same_value() -> None:
    string_obj = jv.String()
    await string_obj.update("hello")

    await string_obj.update("hello")

    assert string_obj._value.getvalue() == "hello"


async def test_string_update_incremental() -> None:
    string_obj = jv.String()
    await string_obj.update("hello")
    await string_obj.update("hello world")

    assert string_obj._value.getvalue() == "hello world"


async def test_string_update_multiple_increments() -> None:
    string_obj = jv.String()
    await string_obj.update("a")
    await string_obj.update("ab")
    await string_obj.update("abc")
    await string_obj.update("abcd")

    assert string_obj._value.getvalue() == "abcd"


async def test_string_update_empty_string() -> None:
    string_obj = jv.String()
    await string_obj.update("")

    assert string_obj._value.getvalue() == ""


async def test_string_update_shorter_value() -> None:
    string_obj = jv.String()
    await string_obj.update("hello world")
    await string_obj.update("hello")  # Shorter than current

    assert string_obj._value.getvalue() == "hello world"


async def test_on_append_single_callback() -> None:
    string_obj = jv.String()
    called_chunks = []

    async def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    await string_obj.update("hello")

    assert called_chunks == ["hello"]
    assert string_obj._value.getvalue() == "hello"


async def test_on_append_multiple_callbacks() -> None:
    string_obj = jv.String()
    called_chunks_1 = []
    called_chunks_2 = []

    async def callback1(chunk: str) -> None:
        called_chunks_1.append(chunk)

    async def callback2(chunk: str) -> None:
        called_chunks_2.append(chunk)

    string_obj.on_append(callback1)
    string_obj.on_append(callback2)
    await string_obj.update("hello")

    assert called_chunks_1 == ["hello"]
    assert called_chunks_2 == ["hello"]


async def test_on_append_incremental_updates() -> None:
    string_obj = jv.String()
    called_chunks = []

    async def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    await string_obj.update("hello")
    await string_obj.update("hello world")
    await string_obj.update("hello world!")

    assert called_chunks == ["hello", " world", "!"]
    assert string_obj._value.getvalue() == "hello world!"


async def test_on_append_no_callback_on_same_value() -> None:
    string_obj = jv.String()
    called_chunks = []

    async def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    await string_obj.update("hello")
    await string_obj.update("hello")  # Same value, should not trigger callback

    assert called_chunks == ["hello"]


async def test_on_append_no_callback_on_shorter_value() -> None:
    string_obj = jv.String()
    called_chunks = []

    async def callback(chunk: str) -> None:
        called_chunks.append(chunk)

    string_obj.on_append(callback)
    await string_obj.update("hello world")
    await string_obj.update("hello")  # Shorter value, should not trigger callback

    assert called_chunks == ["hello world"]


async def test_on_append_callback_order() -> None:
    """Test callbacks are called in the order they were registered."""
    string_obj = jv.String()
    call_order = []

    async def callback1(chunk: str) -> None:
        call_order.append("callback1")

    async def callback2(chunk: str) -> None:
        call_order.append("callback2")

    async def callback3(chunk: str) -> None:
        call_order.append("callback3")

    string_obj.on_append(callback1)
    string_obj.on_append(callback2)
    string_obj.on_append(callback3)
    await string_obj.update("test")

    assert call_order == ["callback1", "callback2", "callback3"]


async def test_complex_streaming_scenario() -> None:
    """Test a complex streaming scenario with multiple updates and callbacks."""
    string_obj = jv.String()
    received_chunks = []
    full_content = []

    async def chunk_handler(chunk: str) -> None:
        received_chunks.append(chunk)

    async def content_handler(chunk: str) -> None:
        full_content.append(string_obj._value.getvalue())

    string_obj.on_append(chunk_handler)
    string_obj.on_append(content_handler)

    # Simulate streaming updates
    await string_obj.update("The")
    await string_obj.update("The quick")
    await string_obj.update("The quick brown")
    await string_obj.update("The quick brown fox")

    assert received_chunks == ["The", " quick", " brown", " fox"]
    assert full_content == [
        "The",
        "The quick",
        "The quick brown",
        "The quick brown fox",
    ]
    assert string_obj._value.getvalue() == "The quick brown fox"


async def test_string_on_complete_single_callback() -> None:
    string_obj = jv.String()
    completed_values = []

    async def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    await string_obj.update("hello world")
    await string_obj._complete()

    assert completed_values == ["hello world"]


async def test_string_on_complete_multiple_callbacks() -> None:
    string_obj = jv.String()
    completed_values_1 = []
    completed_values_2 = []

    async def callback1(value: str) -> None:
        completed_values_1.append(value)

    async def callback2(value: str) -> None:
        completed_values_2.append(value)

    string_obj.on_complete(callback1)
    string_obj.on_complete(callback2)
    await string_obj.update("test value")
    await string_obj._complete()

    assert completed_values_1 == ["test value"]
    assert completed_values_2 == ["test value"]


async def test_string_on_complete_callback_order() -> None:
    """Test callbacks are called in the order they were registered."""
    string_obj = jv.String()
    call_order = []

    async def callback1(value: str) -> None:
        call_order.append("callback1")

    async def callback2(value: str) -> None:
        call_order.append("callback2")

    async def callback3(value: str) -> None:
        call_order.append("callback3")

    string_obj.on_complete(callback1)
    string_obj.on_complete(callback2)
    string_obj.on_complete(callback3)
    await string_obj.update("test")
    await string_obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


async def test_string_complete_empty_value() -> None:
    """Test complete method with empty string value."""
    string_obj = jv.String()
    completed_values = []

    async def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    await string_obj._complete()

    assert completed_values == [""]


async def test_string_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    string_obj = jv.String()
    completed_values = []

    async def callback(value: str) -> None:
        completed_values.append(value)

    string_obj.on_complete(callback)
    await string_obj.update("hello")
    await string_obj._complete()
    await string_obj._complete()

    assert completed_values == ["hello", "hello"]


async def test_string_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    string_obj = jv.String()
    await string_obj.update("test")
    # Should not raise an exception
    await string_obj._complete()
