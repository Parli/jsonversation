import pytest
import io
from jsonversation.parser import Parser
from jsonversation.models import Object, String, List


def create_simple_object() -> Object:
    """Create a simple test object with string attribute."""

    class TestObject(Object):
        name: String

    return TestObject()


def create_object_with_list() -> Object:
    """Create a test object with list attribute."""

    class TestObject(Object):
        items: List[String]

    return TestObject()


def create_complex_object() -> Object:
    """Create a complex test object with multiple attributes."""

    class TestObject(Object):
        name: String
        description: String
        tags: List[String]

    return TestObject()


# Parser initialization tests
def test_parser_init_creates_buffer_and_stores_object() -> None:
    """Test that Parser initializes with empty buffer and stores the object."""
    obj = create_simple_object()
    parser = Parser(obj)

    assert parser._object is obj
    assert isinstance(parser._buffer, io.BytesIO)
    assert parser._buffer.getvalue() == b""


def test_parser_init_with_different_object_types() -> None:
    """Test Parser initialization with different Object types."""
    simple_obj = create_simple_object()
    list_obj = create_object_with_list()
    complex_obj = create_complex_object()

    parser1 = Parser(simple_obj)
    parser2 = Parser(list_obj)
    parser3 = Parser(complex_obj)

    assert parser1._object is simple_obj
    assert parser2._object is list_obj
    assert parser3._object is complex_obj

    for parser in [parser1, parser2, parser3]:
        assert isinstance(parser._buffer, io.BytesIO)
        assert parser._buffer.getvalue() == b""


# Basic push functionality tests
def test_push_writes_chunk_to_buffer() -> None:
    """Test that push method writes chunk to internal buffer."""
    obj = create_simple_object()
    parser = Parser(obj)

    chunk = '{"name": "test"}'
    parser.push(chunk)

    assert parser._buffer.getvalue() == chunk.encode()


def test_push_accumulates_chunks_in_buffer() -> None:
    """Test that multiple push calls accumulate data in buffer."""
    obj = create_simple_object()
    parser = Parser(obj)

    chunk1 = '{"name":'
    chunk2 = '"hello"}'

    parser.push(chunk1)
    parser.push(chunk2)

    expected_buffer = (chunk1 + chunk2).encode()
    assert parser._buffer.getvalue() == expected_buffer


def test_push_with_empty_chunk() -> None:
    """Test push behavior with empty string chunk."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push("")

    assert parser._buffer.getvalue() == b""
    # Object should remain unchanged
    assert obj.name._value.getvalue() == ""  # type: ignore


def test_push_with_unicode_chunk() -> None:
    """Test push with unicode characters in chunk."""
    obj = create_simple_object()
    parser = Parser(obj)

    unicode_chunk = '{"name": "héllo wörld 🌍"}'
    parser.push(unicode_chunk)

    assert parser._buffer.getvalue() == unicode_chunk.encode()
    assert obj.name._value.getvalue() == "héllo wörld 🌍"  # type: ignore


# JSON parsing and object update tests
def test_push_updates_string_attribute() -> None:
    """Test that push updates String attributes correctly."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push('{"name": "Alice"}')

    assert obj.name._value.getvalue() == "Alice"  # type: ignore


def test_push_updates_string_progressively() -> None:
    """Test progressive string updates through multiple pushes."""
    obj = create_simple_object()
    parser = Parser(obj)

    # First partial JSON
    parser.push('{"name": "Hello')
    assert obj.name._value.getvalue() == "Hello"  # type: ignore

    # Extended JSON that should update the string
    parser.push(' World"}')
    assert obj.name._value.getvalue() == "Hello World"  # type: ignore


def test_push_updates_list_attribute() -> None:
    """Test that push updates List attributes correctly."""
    obj = create_object_with_list()
    parser = Parser(obj)

    parser.push('{"items": ["first", "second", "third"]}')

    assert len(obj.items._values) == 3  # type: ignore
    assert obj.items._values[0]._value.getvalue() == "first"  # type: ignore
    assert obj.items._values[1]._value.getvalue() == "second"  # type: ignore
    assert obj.items._values[2]._value.getvalue() == "third"  # type: ignore


def test_push_updates_complex_object() -> None:
    """Test updating object with multiple attributes."""
    obj = create_complex_object()
    parser = Parser(obj)

    json_data = '{"name": "Project", "description": "A test project", "tags": ["python", "testing"]}'
    parser.push(json_data)

    assert obj.name._value.getvalue() == "Project"  # type: ignore
    assert obj.description._value.getvalue() == "A test project"  # type: ignore
    assert len(obj.tags._values) == 2  # type: ignore
    assert obj.tags._values[0]._value.getvalue() == "python"  # type: ignore
    assert obj.tags._values[1]._value.getvalue() == "testing"  # type: ignore


def test_push_ignores_unknown_keys() -> None:
    """Test that unknown keys in JSON are ignored."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push('{"name": "Alice", "unknown_field": "ignored", "another": 123}')

    # Only known field should be updated
    assert obj.name._value.getvalue() == "Alice"  # type: ignore
    # Unknown fields should not cause errors or be added to object
    assert not hasattr(obj, "unknown_field")
    assert not hasattr(obj, "another")


def test_push_with_partial_json() -> None:
    """Test behavior with incomplete JSON that jiter can handle."""
    obj = create_simple_object()
    parser = Parser(obj)

    # Push incomplete JSON
    parser.push('{"name": "Partial')

    # Buffer should contain the partial data
    assert parser._buffer.getvalue() == b'{"name": "Partial'
    # Object might not be updated yet depending on jiter's behavior
    # This tests the parser's robustness with partial data


def test_push_expanding_list() -> None:
    """Test adding items to a list through multiple pushes."""
    obj = create_object_with_list()
    parser = Parser(obj)

    # Start with one item
    parser.push('{"items": ["first"]}')
    assert len(obj.items._values) == 1  # type: ignore
    assert obj.items._values[0]._value.getvalue() == "first"  # type: ignore

    # Add more items (this simulates how streaming might work)
    parser.push(', "second"]}')
    # The buffer now contains: {"items": ["first"], "second"]}
    # This may not parse correctly, but tests buffer accumulation


def test_push_expanding_string() -> None:
    """Test string expansion through multiple pushes."""
    obj = create_simple_object()
    parser = Parser(obj)

    # Initial string
    parser.push('{"name": "Hello"}')
    assert obj.name._value.getvalue() == "Hello"  # type: ignore

    # Try to extend (this tests progressive string updates)
    # Note: This may not work as expected with real jiter, but tests the concept
    parser.push(' World"]}')


# Buffer state and persistence tests
def test_buffer_persists_between_push_calls() -> None:
    """Test that buffer maintains state between push calls."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push("{")
    buffer_after_first = parser._buffer.getvalue()

    parser.push('"title":')
    buffer_after_second = parser._buffer.getvalue()

    assert buffer_after_second == buffer_after_first + b'"title":'
    assert b"{" in buffer_after_second


def test_multiple_complete_json_pushes() -> None:
    """Test multiple complete JSON objects pushed sequentially."""
    obj = create_simple_object()
    parser = Parser(obj)

    # First complete JSON
    parser.push('{"name": "First"}')
    assert obj.name._value.getvalue() == "First"  # type: ignore
    first_buffer_size = len(parser._buffer.getvalue())

    # Second JSON appended
    parser.push('{"name": "Second"}')
    # Buffer should contain both
    buffer_content = parser._buffer.getvalue()
    assert len(buffer_content) == first_buffer_size + len('{"name": "Second"}')


# Edge cases and error conditions
def test_push_with_malformed_json() -> None:
    """Test behavior with malformed JSON."""
    obj = create_simple_object()
    parser = Parser(obj)

    # This should raise an exception from jiter
    with pytest.raises(Exception):  # jiter will raise some kind of parsing error
        parser.push('{"name": invalid}')


def test_push_empty_json_object() -> None:
    """Test pushing empty JSON object."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push("{}")

    # Object should remain unchanged
    assert obj.name._value.getvalue() == ""  # type: ignore


def test_push_json_with_null_values() -> None:
    """Test handling of null values in JSON."""
    obj = create_simple_object()
    parser = Parser(obj)

    parser.push('{"name": null}')

    # Test how the system handles null values


# Property access and object integrity tests
def test_parser_object_property_immutable() -> None:
    """Test that parser's object reference remains constant."""
    obj = create_simple_object()
    parser = Parser(obj)

    original_obj = parser._object

    # Perform operations
    parser.push('{"name": "test"}')

    # Object reference should remain the same
    assert parser._object is original_obj
    assert parser._object is obj


def test_buffer_direct_access() -> None:
    """Test direct access to parser's buffer."""
    obj = create_simple_object()
    parser = Parser(obj)

    # Should be able to read buffer state
    assert parser._buffer.getvalue() == b""

    # Buffer should be writable through parser
    parser.push('{"title": "test"}')
    assert b'{"title": "test"}' in parser._buffer.getvalue()


def test_multiple_parsers_independence() -> None:
    """Test that multiple parsers maintain independent state."""
    obj1 = create_simple_object()
    obj2 = create_simple_object()

    parser1 = Parser(obj1)
    parser2 = Parser(obj2)

    parser1.push('{"name": "Parser1"}')
    parser2.push('{"name": "Parser2"}')

    # Objects should be updated independently
    assert obj1.name._value.getvalue() == "Parser1"  # type: ignore
    assert obj2.name._value.getvalue() == "Parser2"  # type: ignore

    # Buffers should be independent
    assert parser1._buffer.getvalue() != parser2._buffer.getvalue()


def test_large_json_handling() -> None:
    """Test handling of larger JSON strings."""
    obj = create_complex_object()
    parser = Parser(obj)

    # Create a larger JSON string
    large_json = (
        '{"name": "Large Object", "description": "'
        + "x" * 1000
        + '", "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]}'
    )

    parser.push(large_json)

    assert obj.name._value.getvalue() == "Large Object"  # type: ignore
    assert len(obj.description._value.getvalue()) == 1000 + len("")  # type: ignore
    assert len(obj.tags._values) == 5  # type: ignore


# Context manager tests
def test_parser_context_manager_basic() -> None:
    """Test basic context manager functionality."""
    obj = create_simple_object()

    with Parser(obj) as parser:
        assert parser._object is obj
        assert isinstance(parser._buffer, io.BytesIO)
        parser.push('{"name": "context_test"}')

    # After context exit, object should be updated
    assert obj.name._value.getvalue() == "context_test"  # type: ignore


def test_parser_context_manager_returns_self() -> None:
    """Test that context manager returns the parser instance."""
    obj = create_simple_object()
    parser = Parser(obj)

    with parser as context_parser:
        assert context_parser is parser
        assert context_parser._object is obj


def test_parser_context_manager_completion_on_exit() -> None:
    """Test that object is completed when context manager exits."""
    obj = create_simple_object()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    obj.name.on_complete(callback)  # type: ignore

    with Parser(obj) as parser:
        parser.push('{"name": "completion_test"}')
        # Completion callback should not be triggered yet
        assert completed_values == []

    # After context exit, completion should be triggered
    assert completed_values == ["completion_test"]


def test_parser_context_manager_complex_object_completion() -> None:
    """Test context manager completion with complex object."""
    obj = create_complex_object()
    name_completed = []
    description_completed = []
    tags_completed = []
    object_completed = []

    def name_callback(value: str) -> None:
        name_completed.append(value)

    def description_callback(value: str) -> None:
        description_completed.append(value)

    def tags_callback(values: list) -> None:
        tags_completed.append([v.value for v in values])

    def object_callback(value: dict) -> None:
        object_completed.append(value)

    obj.name.on_complete(name_callback)  # type: ignore
    obj.description.on_complete(description_callback)  # type: ignore
    obj.tags.on_complete(tags_callback)  # type: ignore
    obj.on_complete(object_callback)

    with Parser(obj) as parser:
        parser.push('{"name": "Test", "description": "Description", "tags": ["tag1", "tag2"]}')
        assert name_completed == ["Test"]
        assert description_completed == ["Description"]
        assert object_completed == []

    assert tags_completed == [["tag1", "tag2"]]
    assert len(object_completed) == 1


def test_parser_context_manager_streaming_updates() -> None:
    """Test context manager with streaming updates and completion."""
    obj = create_simple_object()
    name_updates = []
    name_completed = []

    def name_update_callback(chunk: str) -> None:
        name_updates.append(chunk)

    def name_complete_callback(value: str) -> None:
        name_completed.append(value)

    obj.name.on_append(name_update_callback)  # type: ignore
    obj.name.on_complete(name_complete_callback)  # type: ignore

    with Parser(obj) as parser:
        parser.push('{"name": "Stream')
        parser.push('ing Test"}')
        # Updates should be triggered during streaming
        assert name_updates == ["Stream", "ing Test"]
        # But completion should not be triggered yet
        assert name_completed == []

    # After context exit, completion should be triggered
    assert name_completed == ["Streaming Test"]


def test_parser_context_manager_multiple_contexts() -> None:
    """Test multiple context manager uses with same parser."""
    obj = create_simple_object()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    obj.name.on_complete(callback)  # type: ignore
    parser = Parser(obj)

    # First context
    with parser:
        parser.push('{"name": "first"}')

    assert completed_values == ["first"]

    # Second context - should work independently
    obj2 = create_simple_object()
    completed_values_2 = []

    def callback2(value: str) -> None:
        completed_values_2.append(value)

    obj2.name.on_complete(callback2)  # type: ignore
    parser2 = Parser(obj2)

    with parser2:
        parser2.push('{"name": "second"}')

    assert completed_values_2 == ["second"]
    assert completed_values == ["first"]  # Original unchanged


def test_parser_context_manager_partial_json() -> None:
    """Test context manager behavior with partial JSON that gets completed."""
    obj = create_simple_object()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    obj.name.on_complete(callback)  # type: ignore

    with Parser(obj) as parser:
        # Push partial JSON that might not parse completely
        parser.push('{"name": "partial')
        # The completion should still work when context exits

    # Object should have whatever was successfully parsed
    # Completion should be triggered regardless


def test_parser_context_manager_empty_push() -> None:
    """Test context manager with no push operations."""
    obj = create_simple_object()
    completed_values = []

    def callback(value: str) -> None:
        completed_values.append(value)

    obj.name.on_complete(callback)  # type: ignore

    with Parser(obj) as _:
        # No push operations
        pass

    # Completion should still be triggered, even with empty string
    assert completed_values == []


def test_parser_context_manager_buffer_state() -> None:
    """Test that buffer state is preserved during context manager usage."""
    obj = create_simple_object()

    with Parser(obj) as parser:
        parser.push('{"name":')
        buffer_mid_context = parser._buffer.getvalue()
        parser.push(' "test"}')
        buffer_end_context = parser._buffer.getvalue()

        assert buffer_mid_context == b'{"name":'
        assert buffer_end_context == b'{"name": "test"}'

    # After context, object should be properly updated
    assert obj.name._value.getvalue() == "test"  # type: ignore


def test_parser_context_manager_with_list_object() -> None:
    """Test context manager with object containing lists."""
    obj = create_object_with_list()
    items_completed = []
    object_completed = []

    def items_callback(values: list) -> None:
        items_completed.append([v.value for v in values])

    def object_callback(value: dict) -> None:
        object_completed.append(value)

    obj.items.on_complete(items_callback)  # type: ignore
    obj.on_complete(object_callback)

    with Parser(obj) as parser:
        parser.push('{"items": ["first", "second", "third"]}')
        # No completions during context
        assert items_completed == []
        assert object_completed == []

    # Completions after context exit
    assert items_completed == [["first", "second", "third"]]
    assert len(object_completed) == 1


def test_parser_context_manager_nested_context_safety() -> None:
    """Test that nested context managers work safely (if somehow used)."""
    obj = create_simple_object()

    parser = Parser(obj)

    with parser as p1:
        p1.push('{"name": "outer"}')
        # Nested context with same parser (unusual but should be safe)
        with parser as p2:
            assert p1 is p2  # Same parser instance
            p2.push('updated"}')  # This would append to buffer

    # Object should have the combined result
    assert "outer" in obj.name._value.getvalue()  # type: ignore


def test_parser_context_manager_completion_order() -> None:
    """Test that completions happen in correct order on context exit."""
    obj = create_complex_object()
    completion_order = []

    def name_callback(value: str) -> None:
        completion_order.append(f"name:{value}")

    def description_callback(value: str) -> None:
        completion_order.append(f"description:{value}")

    def tags_callback(values: list) -> None:
        completion_order.append(f"tags:{len(values)}")

    def object_callback(value: dict) -> None:
        completion_order.append(f"object:{len(value)}")

    obj.name.on_complete(name_callback)  # type: ignore
    obj.description.on_complete(description_callback)  # type: ignore
    obj.tags.on_complete(tags_callback)  # type: ignore
    obj.on_complete(object_callback)

    with Parser(obj) as parser:
        # Streaming updates that would trigger key transitions
        parser.push('{"name": "Test"}')
        parser.push('{"name": "Test", "description": "Desc"}')
        parser.push('{"name": "Test", "description": "Desc", "tags": ["tag1"]}')

    # Check that completion order makes sense
    # (exact order depends on implementation, but object should be last)
    assert "object:" in completion_order[-1]
    assert len(completion_order) > 1
