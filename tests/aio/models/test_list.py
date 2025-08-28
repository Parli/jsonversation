import jsonversation.aio as jv


async def test_list_init() -> None:
    list_obj = jv.List(jv.String)

    assert list_obj._values == []
    assert list_obj._item_type == jv.String
    assert list_obj._on_append_funcs == []


async def test_list_update_empty_list() -> None:
    list_obj = jv.List(jv.String)
    await list_obj.update([])

    assert list_obj._values == []


async def test_list_update_single_item() -> None:
    list_obj = jv.List(jv.String)
    await list_obj.update(["hello"])

    assert len(list_obj._values) == 1
    assert isinstance(list_obj._values[0], jv.String)
    assert list_obj._values[0]._value.getvalue() == "hello"


async def test_list_update_multiple_items() -> None:
    list_obj = jv.List(jv.String)
    await list_obj.update(["hello", "world", "test"])

    assert len(list_obj._values) == 3
    assert all(isinstance(item, jv.String) for item in list_obj._values)
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"
    assert list_obj._values[2]._value.getvalue() == "test"


async def test_list_update_incremental_growth() -> None:
    list_obj = jv.List(jv.String)

    await list_obj.update(["hello"])
    assert len(list_obj._values) == 1
    assert list_obj._values[0]._value.getvalue() == "hello"

    await list_obj.update(["hello", "world"])
    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"

    await list_obj.update(["hello", "world", "test"])
    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"
    assert list_obj._values[2]._value.getvalue() == "test"


async def test_list_update_existing_items() -> None:
    list_obj = jv.List(jv.String)

    # Initial update
    await list_obj.update(["hello", "world"])
    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"

    # Update with incremental content for existing items
    await list_obj.update(["hello", "world!"])

    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world!"


async def test_list_update_mixed_new_and_existing() -> None:
    """Test updating jv.List with mix of existing and new items."""
    list_obj = jv.List(jv.String)

    # Initial update
    await list_obj.update(["hello"])

    # Update with existing item modified and new items added
    await list_obj.update(["hello world", "new item", "another"])

    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "hello world"
    assert list_obj._values[1]._value.getvalue() == "new item"
    assert list_obj._values[2]._value.getvalue() == "another"


async def test_list_on_append_single_callback() -> None:
    """Test registering and triggering a single callback for new items."""
    list_obj = jv.List(jv.String)
    appended_items = []

    async def callback(item: jv.String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)
    await list_obj.update(["hello"])

    assert len(appended_items) == 1
    assert isinstance(appended_items[0], jv.String)
    assert appended_items[0]._value.getvalue() == "hello"


async def test_list_on_append_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered for new items."""
    list_obj = jv.List(jv.String)
    appended_items_1 = []
    appended_items_2 = []

    async def callback1(item: jv.String) -> None:
        appended_items_1.append(item)

    async def callback2(item: jv.String) -> None:
        appended_items_2.append(item)

    list_obj.on_append(callback1)
    list_obj.on_append(callback2)
    await list_obj.update(["hello"])

    assert len(appended_items_1) == 1
    assert len(appended_items_2) == 1
    assert appended_items_1[0] is appended_items_2[0]  # Same object


async def test_list_on_append_only_new_items() -> None:
    """Test callbacks are only triggered for newly added items, not existing ones."""
    list_obj = jv.List(jv.String)
    appended_items = []

    async def callback(item: jv.String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)

    # First update
    await list_obj.update(["hello"])
    assert len(appended_items) == 1

    # Second update with existing item modified - should not trigger callback
    await list_obj.update(["hello world"])
    assert len(appended_items) == 1  # Still only 1

    # Third update with new item - should trigger callback
    await list_obj.update(["hello world", "new item"])
    assert len(appended_items) == 2


async def test_list_on_append_multiple_new_items() -> None:
    """Test callbacks triggered for multiple new items in single update."""
    list_obj = jv.List(jv.String)
    appended_items = []

    async def callback(item: jv.String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)
    await list_obj.update(["first", "second", "third"])

    assert len(appended_items) == 3
    assert appended_items[0]._value.getvalue() == "first"
    assert appended_items[1]._value.getvalue() == "second"
    assert appended_items[2]._value.getvalue() == "third"


async def test_list_on_append_callback_order() -> None:
    """Test callbacks are called in registration order for each new item."""
    list_obj = jv.List(jv.String)
    call_order = []

    async def callback1(item: jv.String) -> None:
        call_order.append(f"callback1-{item._value.getvalue()}")

    async def callback2(item: jv.String) -> None:
        call_order.append(f"callback2-{item._value.getvalue()}")

    list_obj.on_append(callback1)
    list_obj.on_append(callback2)
    await list_obj.update(["item1", "item2"])

    expected_order = [
        "callback1-item1",
        "callback2-item1",
        "callback1-item2",
        "callback2-item2",
    ]
    assert call_order == expected_order


async def test_list_streaming_behavior() -> None:
    """Test complex streaming scenario with incremental updates."""
    list_obj = jv.List(jv.String)
    appended_items = []

    async def callback(item: jv.String) -> None:
        appended_items.append(item._value.getvalue())

    list_obj.on_append(callback)

    # Simulate streaming updates
    await list_obj.update(["The"])
    await list_obj.update(["The quick"])  # Existing item updated
    await list_obj.update(["The quick", "brown"])  # New item added
    await list_obj.update(["The quick", "brown fox"])  # Existing item updated
    await list_obj.update(["The quick", "brown fox", "jumps"])  # New item added

    # Only new items should trigger callbacks
    assert appended_items == ["The", "brown", "jumps"]

    # Final state check
    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "The quick"
    assert list_obj._values[1]._value.getvalue() == "brown fox"
    assert list_obj._values[2]._value.getvalue() == "jumps"


async def test_list_empty_string_items() -> None:
    """Test jv.List with empty string items."""
    list_obj = jv.List(jv.String)
    await list_obj.update(["", "hello", ""])

    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == ""
    assert list_obj._values[1]._value.getvalue() == "hello"
    assert list_obj._values[2]._value.getvalue() == ""


async def test_list_on_complete_single_callback() -> None:
    """Test registering and triggering a single completion callback."""
    list_obj = jv.List(jv.String)
    completed_values = []

    async def callback(values: list[jv.String]) -> None:
        completed_values.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback)
    await list_obj.update(["hello", "world"])
    await list_obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0] == ["hello", "world"]


async def test_list_on_complete_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered on completion."""
    list_obj = jv.List(jv.String)
    completed_values_1 = []
    completed_values_2 = []

    async def callback1(values: list[jv.String]) -> None:
        completed_values_1.append(len(values))

    async def callback2(values: list[jv.String]) -> None:
        completed_values_2.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback1)
    list_obj.on_complete(callback2)
    await list_obj.update(["test1", "test2", "test3"])
    await list_obj._complete()

    assert completed_values_1 == [3]
    assert completed_values_2 == [["test1", "test2", "test3"]]


async def test_list_on_complete_callback_order() -> None:
    """Test callbacks are called in registration order."""
    list_obj = jv.List(jv.String)
    call_order = []

    async def callback1(values: list[jv.String]) -> None:
        call_order.append("callback1")

    async def callback2(values: list[jv.String]) -> None:
        call_order.append("callback2")

    async def callback3(values: list[jv.String]) -> None:
        call_order.append("callback3")

    list_obj.on_complete(callback1)
    list_obj.on_complete(callback2)
    list_obj.on_complete(callback3)
    await list_obj.update(["test"])
    await list_obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


async def test_list_complete_empty_list() -> None:
    """Test complete method with empty list."""
    list_obj = jv.List(jv.String)
    completed_values = []

    async def callback(values: list[jv.String]) -> None:
        completed_values.append(len(values))

    list_obj.on_complete(callback)
    await list_obj._complete()

    assert completed_values == [0]


async def test_list_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    list_obj = jv.List(jv.String)
    completed_values = []

    async def callback(values: list[jv.String]) -> None:
        completed_values.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback)
    await list_obj.update(["hello"])
    await list_obj._complete()
    await list_obj._complete()

    assert len(completed_values) == 2
    assert completed_values[0] == ["hello"]
    assert completed_values[1] == ["hello"]


async def test_list_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    list_obj = jv.List(jv.String)
    await list_obj.update(["test"])
    # Should not raise an exception
    await list_obj._complete()
