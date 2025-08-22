from jsonversation.models import List, String


def test_list_init() -> None:
    list_obj = List(String)

    assert list_obj._values == []
    assert list_obj._item_type == String
    assert list_obj._on_append_funcs == []


def test_list_update_empty_list() -> None:
    list_obj = List(String)
    list_obj.update([])

    assert list_obj._values == []


def test_list_update_single_item() -> None:
    list_obj = List(String)
    list_obj.update(["hello"])

    assert len(list_obj._values) == 1
    assert isinstance(list_obj._values[0], String)
    assert list_obj._values[0]._value.getvalue() == "hello"


def test_list_update_multiple_items() -> None:
    list_obj = List(String)
    list_obj.update(["hello", "world", "test"])

    assert len(list_obj._values) == 3
    assert all(isinstance(item, String) for item in list_obj._values)
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"
    assert list_obj._values[2]._value.getvalue() == "test"


def test_list_update_incremental_growth() -> None:
    list_obj = List(String)

    list_obj.update(["hello"])
    assert len(list_obj._values) == 1
    assert list_obj._values[0]._value.getvalue() == "hello"

    list_obj.update(["hello", "world"])
    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"

    list_obj.update(["hello", "world", "test"])
    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"
    assert list_obj._values[2]._value.getvalue() == "test"


def test_list_update_existing_items() -> None:
    list_obj = List(String)

    # Initial update
    list_obj.update(["hello", "world"])
    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world"

    # Update with incremental content for existing items
    list_obj.update(["hello", "world!"])

    assert len(list_obj._values) == 2
    assert list_obj._values[0]._value.getvalue() == "hello"
    assert list_obj._values[1]._value.getvalue() == "world!"


def test_list_update_mixed_new_and_existing() -> None:
    """Test updating List with mix of existing and new items."""
    list_obj = List(String)

    # Initial update
    list_obj.update(["hello"])

    # Update with existing item modified and new items added
    list_obj.update(["hello world", "new item", "another"])

    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "hello world"
    assert list_obj._values[1]._value.getvalue() == "new item"
    assert list_obj._values[2]._value.getvalue() == "another"


def test_list_on_append_single_callback() -> None:
    """Test registering and triggering a single callback for new items."""
    list_obj = List(String)
    appended_items = []

    def callback(item: String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)
    list_obj.update(["hello"])

    assert len(appended_items) == 1
    assert isinstance(appended_items[0], String)
    assert appended_items[0]._value.getvalue() == "hello"


def test_list_on_append_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered for new items."""
    list_obj = List(String)
    appended_items_1 = []
    appended_items_2 = []

    def callback1(item: String) -> None:
        appended_items_1.append(item)

    def callback2(item: String) -> None:
        appended_items_2.append(item)

    list_obj.on_append(callback1)
    list_obj.on_append(callback2)
    list_obj.update(["hello"])

    assert len(appended_items_1) == 1
    assert len(appended_items_2) == 1
    assert appended_items_1[0] is appended_items_2[0]  # Same object


def test_list_on_append_only_new_items() -> None:
    """Test callbacks are only triggered for newly added items, not existing ones."""
    list_obj = List(String)
    appended_items = []

    def callback(item: String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)

    # First update
    list_obj.update(["hello"])
    assert len(appended_items) == 1

    # Second update with existing item modified - should not trigger callback
    list_obj.update(["hello world"])
    assert len(appended_items) == 1  # Still only 1

    # Third update with new item - should trigger callback
    list_obj.update(["hello world", "new item"])
    assert len(appended_items) == 2


def test_list_on_append_multiple_new_items() -> None:
    """Test callbacks triggered for multiple new items in single update."""
    list_obj = List(String)
    appended_items = []

    def callback(item: String) -> None:
        appended_items.append(item)

    list_obj.on_append(callback)
    list_obj.update(["first", "second", "third"])

    assert len(appended_items) == 3
    assert appended_items[0]._value.getvalue() == "first"
    assert appended_items[1]._value.getvalue() == "second"
    assert appended_items[2]._value.getvalue() == "third"


def test_list_on_append_callback_order() -> None:
    """Test callbacks are called in registration order for each new item."""
    list_obj = List(String)
    call_order = []

    def callback1(item: String) -> None:
        call_order.append(f"callback1-{item._value.getvalue()}")

    def callback2(item: String) -> None:
        call_order.append(f"callback2-{item._value.getvalue()}")

    list_obj.on_append(callback1)
    list_obj.on_append(callback2)
    list_obj.update(["item1", "item2"])

    expected_order = [
        "callback1-item1",
        "callback2-item1",
        "callback1-item2",
        "callback2-item2",
    ]
    assert call_order == expected_order


def test_list_update_returns_none() -> None:
    """Test that update method returns None."""
    list_obj = List(String)
    result = list_obj.update(["hello"])
    assert result is None


def test_list_on_append_returns_none() -> None:
    """Test that on_append method returns None."""
    list_obj = List(String)

    def dummy_callback(item: String) -> None:
        pass

    result = list_obj.on_append(dummy_callback)
    assert result is None


# def test_list_with_object_items():
#     """Test List functionality with Object items instead of String items."""

#     # Create a simple test Object class
#     class TestObject(Object):
#         name: String
#         value: String

#     list_obj = List(TestObject)
#     list_obj.update(
#         [{"name": "obj1", "value": "val1"}, {"name": "obj2", "value": "val2"}]
#     )

#     assert len(list_obj._values) == 2
#     assert isinstance(list_obj._values[0], TestObject)
#     assert isinstance(list_obj._values[1], TestObject)
#     assert list_obj._values[0].name._value.getvalue() == "obj1"
#     assert list_obj._values[0].value._value.getvalue() == "val1"
#     assert list_obj._values[1].name._value.getvalue() == "obj2"
#     assert list_obj._values[1].value._value.getvalue() == "val2"


def test_list_streaming_behavior() -> None:
    """Test complex streaming scenario with incremental updates."""
    list_obj = List(String)
    appended_items = []

    def callback(item: String) -> None:
        appended_items.append(item._value.getvalue())

    list_obj.on_append(callback)

    # Simulate streaming updates
    list_obj.update(["The"])
    list_obj.update(["The quick"])  # Existing item updated
    list_obj.update(["The quick", "brown"])  # New item added
    list_obj.update(["The quick", "brown fox"])  # Existing item updated
    list_obj.update(["The quick", "brown fox", "jumps"])  # New item added

    # Only new items should trigger callbacks
    assert appended_items == ["The", "brown", "jumps"]

    # Final state check
    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == "The quick"
    assert list_obj._values[1]._value.getvalue() == "brown fox"
    assert list_obj._values[2]._value.getvalue() == "jumps"


def test_list_empty_string_items() -> None:
    """Test List with empty string items."""
    list_obj = List(String)
    list_obj.update(["", "hello", ""])

    assert len(list_obj._values) == 3
    assert list_obj._values[0]._value.getvalue() == ""
    assert list_obj._values[1]._value.getvalue() == "hello"
    assert list_obj._values[2]._value.getvalue() == ""


def test_list_on_complete_single_callback() -> None:
    """Test registering and triggering a single completion callback."""
    list_obj = List(String)
    completed_values = []

    def callback(values: list[String]) -> None:
        completed_values.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback)
    list_obj.update(["hello", "world"])
    list_obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0] == ["hello", "world"]


def test_list_on_complete_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered on completion."""
    list_obj = List(String)
    completed_values_1 = []
    completed_values_2 = []

    def callback1(values: list[String]) -> None:
        completed_values_1.append(len(values))

    def callback2(values: list[String]) -> None:
        completed_values_2.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback1)
    list_obj.on_complete(callback2)
    list_obj.update(["test1", "test2", "test3"])
    list_obj._complete()

    assert completed_values_1 == [3]
    assert completed_values_2 == [["test1", "test2", "test3"]]


def test_list_on_complete_callback_order() -> None:
    """Test callbacks are called in registration order."""
    list_obj = List(String)
    call_order = []

    def callback1(values: list[String]) -> None:
        call_order.append("callback1")

    def callback2(values: list[String]) -> None:
        call_order.append("callback2")

    def callback3(values: list[String]) -> None:
        call_order.append("callback3")

    list_obj.on_complete(callback1)
    list_obj.on_complete(callback2)
    list_obj.on_complete(callback3)
    list_obj.update(["test"])
    list_obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


def test_list_complete_empty_list() -> None:
    """Test complete method with empty list."""
    list_obj = List(String)
    completed_values = []

    def callback(values: list[String]) -> None:
        completed_values.append(len(values))

    list_obj.on_complete(callback)
    list_obj._complete()

    assert completed_values == [0]


def test_list_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    list_obj = List(String)
    completed_values = []

    def callback(values: list[String]) -> None:
        completed_values.append([v._value.getvalue() for v in values])

    list_obj.on_complete(callback)
    list_obj.update(["hello"])
    list_obj._complete()
    list_obj._complete()

    assert len(completed_values) == 2
    assert completed_values[0] == ["hello"]
    assert completed_values[1] == ["hello"]


def test_list_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    list_obj = List(String)
    list_obj.update(["test"])
    # Should not raise an exception
    list_obj._complete()
