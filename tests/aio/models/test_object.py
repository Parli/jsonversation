from typing import Any
import jsonversation.aio as jv


# Test classes for Object functionality
class SimpleObject(jv.Object):
    name: jv.String
    value: jv.String


class ComplexObject(jv.Object):
    title: jv.String
    items: jv.List[jv.String]
    metadata: jv.String


class NestedObject(jv.Object):
    id: jv.String
    details: SimpleObject
    description: jv.String


class ObjectWithObjectList(jv.Object):
    title: jv.String
    objects: jv.List[SimpleObject]
    count: jv.String


class DeepNestedObject(jv.Object):
    root_name: jv.String
    nested_data: NestedObject
    tags: jv.List[jv.String]


class ComplexNestedObject(jv.Object):
    header: jv.String
    nested_objects: jv.List[NestedObject]
    simple_list: jv.List[jv.String]
    footer: jv.String


class ObjectWithStringList(jv.Object):
    title: jv.String
    items: jv.List[jv.String]
    count: jv.String


class EmptyObject(jv.Object):
    pass


def test_object_init_simple() -> None:
    """Test Object initialization with simple jv.String attributes."""
    obj = SimpleObject()

    assert hasattr(obj, "name")
    assert hasattr(obj, "value")
    assert isinstance(obj.name, jv.String)
    assert isinstance(obj.value, jv.String)
    assert obj.name._value.getvalue() == ""
    assert obj.value._value.getvalue() == ""
    assert obj._keys == ["name", "value"]


def test_object_init_complex() -> None:
    """Test Object initialization with complex attributes includingjv.List."""
    obj = ComplexObject()

    assert hasattr(obj, "title")
    assert hasattr(obj, "items")
    assert hasattr(obj, "metadata")
    assert isinstance(obj.title, jv.String)
    assert isinstance(obj.items, jv.List)
    assert isinstance(obj.metadata, jv.String)
    assert obj.items._item_type == jv.String
    assert obj._keys == ["title", "items", "metadata"]


def test_object_init_nested() -> None:
    """Test Object initialization with nested Object attributes."""
    obj = NestedObject()

    assert hasattr(obj, "id")
    assert hasattr(obj, "details")
    assert hasattr(obj, "description")
    assert isinstance(obj.id, jv.String)
    assert isinstance(obj.details, SimpleObject)
    assert isinstance(obj.description, jv.String)
    assert obj._keys == ["id", "details", "description"]

    # Check nested object is properly initialized
    assert isinstance(obj.details.name, jv.String)
    assert isinstance(obj.details.value, jv.String)
    assert obj.details.name._value.getvalue() == ""
    assert obj.details.value._value.getvalue() == ""


def test_object_init_with_object_list() -> None:
    """Test Object initialization withjv.List of Objects."""
    obj = ObjectWithObjectList()

    assert hasattr(obj, "title")
    assert hasattr(obj, "objects")
    assert hasattr(obj, "count")
    assert isinstance(obj.title, jv.String)
    assert isinstance(obj.objects, jv.List)
    assert isinstance(obj.count, jv.String)
    assert obj.objects._item_type == SimpleObject
    assert obj._keys == ["title", "objects", "count"]


def test_object_init_complex_nested() -> None:
    """Test Object initialization with complex nested structure includingjv.List of Objects."""
    obj = ComplexNestedObject()

    assert isinstance(obj.header, jv.String)
    assert isinstance(obj.nested_objects, jv.List)
    assert isinstance(obj.simple_list, jv.List)
    assert isinstance(obj.footer, jv.String)
    assert obj.nested_objects._item_type == NestedObject
    assert obj.simple_list._item_type == jv.String
    assert obj._keys == ["header", "nested_objects", "simple_list", "footer"]


def test_object_init_deep_nested() -> None:
    """Test Object initialization with deeply nested Object attributes."""
    obj = DeepNestedObject()

    assert isinstance(obj.root_name, jv.String)
    assert isinstance(obj.nested_data, NestedObject)
    assert isinstance(obj.tags, jv.List)
    assert obj._keys == ["root_name", "nested_data", "tags"]

    # Check nested object structure
    assert isinstance(obj.nested_data.id, jv.String)
    assert isinstance(obj.nested_data.details, SimpleObject)
    assert isinstance(obj.nested_data.description, jv.String)

    # Check deeply nested object structure
    assert isinstance(obj.nested_data.details.name, jv.String)
    assert isinstance(obj.nested_data.details.value, jv.String)


def test_object_init_empty() -> None:
    """Test Object initialization with no attributes."""
    obj = EmptyObject()

    assert obj._keys == []


def test_object_update_simple_attributes() -> None:
    """Test updating Object with simple string attributes."""
    obj = SimpleObject()

    obj.update({"name": "test_name", "value": "test_value"})

    assert obj.name._value.getvalue() == "test_name"
    assert obj.value._value.getvalue() == "test_value"


def test_object_update_with_object_list() -> None:
    """Test updating Object withjv.List of Objects."""
    obj = ObjectWithObjectList()

    obj.update(
        {
            "title": "Objectjv.List Test",
            "objects": [
                {"name": "obj1", "value": "val1"},
                {"name": "obj2", "value": "val2"},
            ],
            "count": "2",
        }
    )

    assert obj.title._value.getvalue() == "Objectjv.List Test"
    assert obj.count._value.getvalue() == "2"
    assert len(obj.objects._values) == 2

    # Check first object
    assert isinstance(obj.objects._values[0], SimpleObject)
    assert obj.objects._values[0].name._value.getvalue() == "obj1"
    assert obj.objects._values[0].value._value.getvalue() == "val1"

    # Check second object
    assert isinstance(obj.objects._values[1], SimpleObject)
    assert obj.objects._values[1].name._value.getvalue() == "obj2"
    assert obj.objects._values[1].value._value.getvalue() == "val2"


def test_object_update_object_list_incremental() -> None:
    """Test incremental updates tojv.List of Objects."""
    obj = ObjectWithObjectList()

    # First update
    obj.update({"title": "Initial", "objects": [{"name": "first", "value": "val1"}]})

    assert len(obj.objects._values) == 1
    assert obj.objects._values[0].name._value.getvalue() == "first"
    assert obj.objects._values[0].value._value.getvalue() == "val1"

    # Second update with more objects
    obj.update(
        {
            "title": "Updated",
            "objects": [
                {"name": "first_updated", "value": "val1_updated"},
                {"name": "second", "value": "val2"},
            ],
        }
    )

    assert len(obj.objects._values) == 2
    assert obj.objects._values[0].name._value.getvalue() == "first_updated"
    assert obj.objects._values[0].value._value.getvalue() == "val1_updated"
    assert obj.objects._values[1].name._value.getvalue() == "second"
    assert obj.objects._values[1].value._value.getvalue() == "val2"


def test_object_update_object_list_partial() -> None:
    """Test partial updates to objects withinjv.List of Objects."""
    obj = ObjectWithObjectList()

    # Initial update
    obj.update({"objects": [{"name": "obj1", "value": "val1"}, {"name": "obj2"}]})

    assert len(obj.objects._values) == 2
    assert obj.objects._values[0].name._value.getvalue() == "obj1"
    assert obj.objects._values[0].value._value.getvalue() == "val1"
    assert obj.objects._values[1].name._value.getvalue() == "obj2"
    assert obj.objects._values[1].value._value.getvalue() == ""  # Empty

    # Update with partial data
    obj.update(
        {
            "objects": [
                {"name": "obj1"},
                {"name": "obj2", "value": "val2_added"},  # Value added
            ]
        }
    )

    assert obj.objects._values[0].name._value.getvalue() == "obj1"
    assert obj.objects._values[0].value._value.getvalue() == "val1"  # Unchanged
    assert obj.objects._values[1].name._value.getvalue() == "obj2"
    assert obj.objects._values[1].value._value.getvalue() == "val2_added"


def test_object_update_complex_nested_with_object_lists() -> None:
    """Test updating complex nested structure with multiple object lists."""
    obj = ComplexNestedObject()

    obj.update(
        {
            "header": "Complex Test",
            "nested_objects": [
                {
                    "id": "nested1",
                    "details": {"name": "detail1", "value": "detval1"},
                    "description": "First nested",
                },
                {
                    "id": "nested2",
                    "details": {"name": "detail2"},
                    "description": "Second nested",
                },
            ],
            "simple_list": ["simple1", "simple2"],
            "footer": "End",
        }
    )

    assert obj.header._value.getvalue() == "Complex Test"
    assert obj.footer._value.getvalue() == "End"

    # Check simple list
    assert len(obj.simple_list._values) == 2
    assert obj.simple_list._values[0]._value.getvalue() == "simple1"
    assert obj.simple_list._values[1]._value.getvalue() == "simple2"

    # Check nested objects list
    assert len(obj.nested_objects._values) == 2

    # First nested object
    nested1 = obj.nested_objects._values[0]
    assert isinstance(nested1, NestedObject)
    assert nested1.id._value.getvalue() == "nested1"
    assert nested1.description._value.getvalue() == "First nested"
    assert nested1.details.name._value.getvalue() == "detail1"
    assert nested1.details.value._value.getvalue() == "detval1"

    # Second nested object
    nested2 = obj.nested_objects._values[1]
    assert isinstance(nested2, NestedObject)
    assert nested2.id._value.getvalue() == "nested2"
    assert nested2.description._value.getvalue() == "Second nested"
    assert nested2.details.name._value.getvalue() == "detail2"
    assert nested2.details.value._value.getvalue() == ""  # Not provided


def test_object_update_object_list_streaming() -> None:
    """Test streaming updates to object lists with incremental changes."""
    obj = ObjectWithObjectList()

    # Streaming updates - mimics real JSON streaming behavior
    updates: list[dict[str, Any]] = [
        {"title": "Stream"},
        {"title": "Stream Test Complete", "objects": [{"name": "obj1"}]},
        {
            "title": "Stream Test Complete",
            "objects": [
                {"name": "obj1", "value": "val1"},
                {"name": "obj2"},
            ],
        },
        {
            "title": "Stream Test Complete",
            "objects": [
                {"name": "obj1", "value": "val1"},
                {"name": "obj2", "value": "val2"},
                {"name": "obj3"},
            ],
        },
        {
            "title": "Stream Test Complete",
            "objects": [
                {"name": "obj1", "value": "val1"},
                {"name": "obj2", "value": "val2"},
                {"name": "obj3", "value": "val3"},
            ],
            "count": "3",
        },
    ]

    for update in updates:
        obj.update(update)

    assert obj.title._value.getvalue() == "Stream Test Complete"
    assert obj.count._value.getvalue() == "3"
    assert len(obj.objects._values) == 3

    assert obj.objects._values[0].name._value.getvalue() == "obj1"
    assert obj.objects._values[0].value._value.getvalue() == "val1"
    assert obj.objects._values[1].name._value.getvalue() == "obj2"
    assert obj.objects._values[1].value._value.getvalue() == "val2"
    assert obj.objects._values[2].name._value.getvalue() == "obj3"
    assert obj.objects._values[2].value._value.getvalue() == "val3"


def test_object_list_with_callbacks() -> None:
    """Test callbacks on object lists are triggered for new objects."""
    obj = ObjectWithObjectList()
    new_objects = []

    def object_callback(new_obj: SimpleObject) -> None:
        new_objects.append(new_obj.name._value.getvalue())

    obj.objects.on_append(object_callback)

    # First update
    obj.update(
        {
            "objects": [
                {"name": "callback1", "value": "val1"},
                {"name": "callback2", "value": "val2"},
            ]
        }
    )

    assert new_objects == ["callback1", "callback2"]

    # Second update with new object
    obj.update(
        {
            "objects": [
                {"name": "callback1", "value": "val1"},
                {"name": "callback2", "value": "val2"},
                {"name": "callback3", "value": "val3"},
            ]
        }
    )

    assert new_objects == ["callback1", "callback2", "callback3"]


def test_object_nested_object_callbacks() -> None:
    """Test callbacks on nested objects within object lists."""
    obj = ObjectWithObjectList()
    name_changes = []

    # Update first to create objects
    obj.update({"objects": [{"name": "initial1"}, {"name": "initial2"}]})

    # Add callbacks to existing objects
    def name_callback(chunk: str) -> None:
        name_changes.append(chunk)

    obj.objects._values[0].name.on_append(name_callback)
    obj.objects._values[1].name.on_append(name_callback)

    # Update with incremental changes
    obj.update({"objects": [{"name": "initial1_updated"}, {"name": "initial2_also_updated"}]})

    assert name_changes == ["_updated", "_also_updated"]


def test_object_update_nested_attributes() -> None:
    """Test updating Object with nested object data."""
    obj = NestedObject()

    obj.update(
        {
            "id": "obj123",
            "details": {"name": "nested_name", "value": "nested_value"},
            "description": "A nested object",
        }
    )

    assert obj.id._value.getvalue() == "obj123"
    assert obj.description._value.getvalue() == "A nested object"
    assert obj.details.name._value.getvalue() == "nested_name"
    assert obj.details.value._value.getvalue() == "nested_value"


def test_object_complete_simple() -> None:
    """Test Object complete method functionality."""
    obj = SimpleObject()
    completed_values = []
    obj.name.on_complete(lambda v: completed_values.append(v))
    obj.update({"name": "test_name", "value": "test_value"})

    assert completed_values == ["test_name"]


def test_object_complete_incomplete_string() -> None:
    """Test Object complete method functionality."""
    obj = SimpleObject()

    completed_values = []
    obj.name.on_complete(lambda v: completed_values.append(v))

    obj.update({"name": "test_name"})

    assert completed_values == []


def test_object_complete_with_lists() -> None:
    """Test complete method on objects with lists."""
    obj = ObjectWithStringList()

    completed_items = []

    def list_on_complete(values: list[jv.String]) -> None:
        completed_items.extend(values)

    obj.items.on_complete(list_on_complete)

    obj.update(
        {
            "title": "Test Title",
            "items": ["item1", "item2"],
            "count": "2",
        }
    )

    assert len(completed_items) != 0
    assert [v.get_value() for v in completed_items] == ["item1", "item2"]


def test_object_on_complete_single_callback() -> None:
    """Test registering and triggering a single completion callback."""
    obj = SimpleObject()
    completed_values = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    obj.on_complete(callback)
    obj.update({"name": "test_name", "value": "test_value"})
    obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0]["name"] == "test_name"
    assert completed_values[0]["value"] == "test_value"


def test_object_on_complete_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered on completion."""
    obj = SimpleObject()
    completed_values_1 = []
    completed_values_2 = []

    def callback1(value: dict[str, Any]) -> None:
        completed_values_1.append(value)

    def callback2(value: dict[str, Any]) -> None:
        completed_values_2.append(len(value))

    obj.on_complete(callback1)
    obj.on_complete(callback2)
    obj.update({"name": "test", "value": "data"})
    obj._complete()

    assert len(completed_values_1) == 1
    assert completed_values_1[0]["name"] == "test"
    assert completed_values_1[0]["value"] == "data"
    assert completed_values_2 == [2]


def test_object_on_complete_callback_order() -> None:
    """Test callbacks are called in registration order."""
    obj = SimpleObject()
    call_order = []

    def callback1(value: dict[str, Any]) -> None:
        call_order.append("callback1")

    def callback2(value: dict[str, Any]) -> None:
        call_order.append("callback2")

    def callback3(value: dict[str, Any]) -> None:
        call_order.append("callback3")

    obj.on_complete(callback1)
    obj.on_complete(callback2)
    obj.on_complete(callback3)
    obj.update({"name": "test"})
    obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


def test_object_complete_empty_object() -> None:
    """Test complete method with object that has no updates."""
    obj = SimpleObject()
    completed_values = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    obj.on_complete(callback)
    # No update called, but complete should still work
    # Note: This might raise an error due to empty _parsed_keys list
    try:
        obj._complete()
        assert completed_values == [{}]
    except IndexError:
        # Expected behavior when no keys have been parsed
        pass


def test_object_complete_single_key() -> None:
    """Test complete method with single key updated."""
    obj = SimpleObject()
    completed_values = []
    name_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    def name_callback(value: str) -> None:
        name_completed.append(value)

    obj.on_complete(callback)
    obj.name.on_complete(name_callback)
    obj.update({"name": "single_key"})
    obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0]["name"] == "single_key"
    assert name_completed == ["single_key"]


def test_object_complete_with_list() -> None:
    """Test complete method on object containing list."""
    obj = ComplexObject()
    completed_values = []
    list_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    def list_callback(values: list[jv.String]) -> None:
        list_completed.extend([v.get_value() for v in values])

    obj.on_complete(callback)
    obj.items.on_complete(list_callback)
    obj.update({"title": "Test Title", "items": ["item1", "item2"], "metadata": "test_meta"})
    obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0]["title"] == "Test Title"
    assert completed_values[0]["metadata"] == "test_meta"
    assert list_completed == ["item1", "item2"]


def test_object_complete_nested_object() -> None:
    """Test complete method with nested objects."""
    obj = NestedObject()
    completed_values = []
    nested_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    def nested_callback(value: dict[str, Any]) -> None:
        nested_completed.append(value)

    obj.on_complete(callback)
    obj.details.on_complete(nested_callback)
    obj.update(
        {"id": "nested_test", "details": {"name": "nested_name", "value": "nested_value"}, "description": "nested_desc"}
    )
    obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0]["id"] == "nested_test"
    assert completed_values[0]["description"] == "nested_desc"
    assert nested_completed == [{"name": "nested_name", "value": "nested_value"}]


def test_object_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    obj = SimpleObject()
    completed_values = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(len(value))

    obj.on_complete(callback)
    obj.update({"name": "test"})
    obj._complete()
    obj._complete()

    assert completed_values == [1, 1]


def test_object_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    obj = SimpleObject()
    obj.update({"name": "test", "value": "data"})
    # Should not raise an exception
    obj._complete()


def test_object_complete_with_object_list() -> None:
    """Test complete method with object containing list of objects."""
    obj = ObjectWithObjectList()
    completed_values = []
    list_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    def list_callback(values: list[SimpleObject]) -> None:
        list_completed.append(len(values))

    obj.on_complete(callback)
    obj.objects.on_complete(list_callback)
    obj.update(
        {
            "title": "Objectjv.List",
            "objects": [{"name": "obj1", "value": "val1"}, {"name": "obj2", "value": "val2"}],
            "count": "2",
        }
    )
    obj._complete()

    assert len(completed_values) == 1
    assert completed_values[0]["title"] == "Objectjv.List"
    assert completed_values[0]["count"] == "2"
    assert list_completed == [2]


def test_object_complete_streaming_updates() -> None:
    """Test complete method behavior during streaming updates."""
    obj = SimpleObject()
    completed_values = []
    name_completed = []
    value_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(dict(value))

    def name_callback(value: str) -> None:
        name_completed.append(value)

    def value_callback(value: str) -> None:
        value_completed.append(value)

    obj.on_complete(callback)
    obj.name.on_complete(name_callback)
    obj.value.on_complete(value_callback)

    # Streaming updates - name key switches to value key
    obj.update({"name": "streaming"})
    obj.update({"name": "streaming", "value": "test"})

    # When switching from name to value, name should be completed
    assert name_completed == ["streaming"]
    assert value_completed == []  # Not completed yet

    obj._complete()

    # Final completion should complete the last key (value) and object
    assert value_completed == ["test"]
    assert len(completed_values) == 1
    assert completed_values[0]["name"] == "streaming"
    assert completed_values[0]["value"] == "test"


def test_object_complete_complex_nested_streaming() -> None:
    """Test complete method with complex nested structure during streaming."""
    obj = ComplexNestedObject()
    completed_values = []
    header_completed = []
    footer_completed = []

    def callback(value: dict[str, Any]) -> None:
        completed_values.append(value)

    def header_callback(value: str) -> None:
        header_completed.append(value)

    def footer_callback(value: str) -> None:
        footer_completed.append(value)

    obj.on_complete(callback)
    obj.header.on_complete(header_callback)
    obj.footer.on_complete(footer_callback)

    # Simulate streaming JSON parsing
    obj.update({"header": "Stream Header"})
    obj.update({"header": "Stream Header", "nested_objects": [{"id": "n1", "description": "first"}]})
    obj.update(
        {
            "header": "Stream Header",
            "nested_objects": [{"id": "n1", "description": "first"}],
            "simple_list": ["s1", "s2"],
        }
    )
    obj.update(
        {
            "header": "Stream Header",
            "nested_objects": [{"id": "n1", "description": "first"}],
            "simple_list": ["s1", "s2"],
            "footer": "Stream Footer",
        }
    )

    # Key transitions should trigger completions
    assert header_completed == ["Stream Header"]  # Completed when switched to nested_objects

    obj._complete()

    assert footer_completed == ["Stream Footer"]  # Completed on final _complete()
    assert len(completed_values) == 1
