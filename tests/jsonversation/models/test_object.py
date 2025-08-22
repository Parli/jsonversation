from jsonversation.models import Object, String, List


# Test classes for Object functionality
class SimpleObject(Object):
    name: String
    value: String


class ComplexObject(Object):
    title: String
    items: List[String]
    metadata: String


class NestedObject(Object):
    id: String
    details: SimpleObject
    description: String


class ObjectWithObjectList(Object):
    title: String
    objects: List[SimpleObject]
    count: String


class DeepNestedObject(Object):
    root_name: String
    nested_data: NestedObject
    tags: List[String]


class ComplexNestedObject(Object):
    header: String
    nested_objects: List[NestedObject]
    simple_list: List[String]
    footer: String


class EmptyObject(Object):
    pass


def test_object_init_simple():
    """Test Object initialization with simple String attributes."""
    obj = SimpleObject()

    assert hasattr(obj, "name")
    assert hasattr(obj, "value")
    assert isinstance(obj.name, String)
    assert isinstance(obj.value, String)
    assert obj.name._value.getvalue() == ""
    assert obj.value._value.getvalue() == ""
    assert obj._keys == ["name", "value"]


def test_object_init_complex():
    """Test Object initialization with complex attributes including List."""
    obj = ComplexObject()

    assert hasattr(obj, "title")
    assert hasattr(obj, "items")
    assert hasattr(obj, "metadata")
    assert isinstance(obj.title, String)
    assert isinstance(obj.items, List)
    assert isinstance(obj.metadata, String)
    assert obj.items._item_type == String
    assert obj._keys == ["title", "items", "metadata"]


def test_object_init_nested():
    """Test Object initialization with nested Object attributes."""
    obj = NestedObject()

    assert hasattr(obj, "id")
    assert hasattr(obj, "details")
    assert hasattr(obj, "description")
    assert isinstance(obj.id, String)
    assert isinstance(obj.details, SimpleObject)
    assert isinstance(obj.description, String)
    assert obj._keys == ["id", "details", "description"]

    # Check nested object is properly initialized
    assert isinstance(obj.details.name, String)
    assert isinstance(obj.details.value, String)
    assert obj.details.name._value.getvalue() == ""
    assert obj.details.value._value.getvalue() == ""


def test_object_init_with_object_list():
    """Test Object initialization with List of Objects."""
    obj = ObjectWithObjectList()

    assert hasattr(obj, "title")
    assert hasattr(obj, "objects")
    assert hasattr(obj, "count")
    assert isinstance(obj.title, String)
    assert isinstance(obj.objects, List)
    assert isinstance(obj.count, String)
    assert obj.objects._item_type == SimpleObject
    assert obj._keys == ["title", "objects", "count"]


def test_object_init_complex_nested():
    """Test Object initialization with complex nested structure including List of Objects."""
    obj = ComplexNestedObject()

    assert isinstance(obj.header, String)
    assert isinstance(obj.nested_objects, List)
    assert isinstance(obj.simple_list, List)
    assert isinstance(obj.footer, String)
    assert obj.nested_objects._item_type == NestedObject
    assert obj.simple_list._item_type == String
    assert obj._keys == ["header", "nested_objects", "simple_list", "footer"]


def test_object_init_deep_nested():
    """Test Object initialization with deeply nested Object attributes."""
    obj = DeepNestedObject()

    assert isinstance(obj.root_name, String)
    assert isinstance(obj.nested_data, NestedObject)
    assert isinstance(obj.tags, List)
    assert obj._keys == ["root_name", "nested_data", "tags"]

    # Check nested object structure
    assert isinstance(obj.nested_data.id, String)
    assert isinstance(obj.nested_data.details, SimpleObject)
    assert isinstance(obj.nested_data.description, String)

    # Check deeply nested object structure
    assert isinstance(obj.nested_data.details.name, String)
    assert isinstance(obj.nested_data.details.value, String)


def test_object_init_empty():
    """Test Object initialization with no attributes."""
    obj = EmptyObject()

    assert obj._keys == []


def test_object_update_simple_attributes():
    """Test updating Object with simple string attributes."""
    obj = SimpleObject()

    obj.update({"name": "test_name", "value": "test_value"})

    assert obj.name._value.getvalue() == "test_name"
    assert obj.value._value.getvalue() == "test_value"


def test_object_update_with_object_list():
    """Test updating Object with List of Objects."""
    obj = ObjectWithObjectList()

    obj.update(
        {
            "title": "Object List Test",
            "objects": [
                {"name": "obj1", "value": "val1"},
                {"name": "obj2", "value": "val2"},
            ],
            "count": "2",
        }
    )

    assert obj.title._value.getvalue() == "Object List Test"
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


def test_object_update_object_list_incremental():
    """Test incremental updates to List of Objects."""
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


def test_object_update_object_list_partial():
    """Test partial updates to objects within List of Objects."""
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


def test_object_update_complex_nested_with_object_lists():
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


def test_object_update_object_list_streaming():
    """Test streaming updates to object lists with incremental changes."""
    obj = ObjectWithObjectList()

    # Streaming updates - mimics real JSON streaming behavior
    updates = [
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


def test_object_list_with_callbacks():
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


def test_object_nested_object_callbacks():
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
    obj.update(
        {"objects": [{"name": "initial1_updated"}, {"name": "initial2_also_updated"}]}
    )

    assert name_changes == ["_updated", "_also_updated"]


def test_object_update_nested_attributes():
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
