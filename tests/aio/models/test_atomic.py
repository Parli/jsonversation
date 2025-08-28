from typing import Any
import jsonversation.aio as jv


def test_atomic_init() -> None:
    """Test jv.Atomic initialization with different types."""
    atomic_str = jv.Atomic(str)
    atomic_int = jv.Atomic(int)
    atomic_dict = jv.Atomic(dict)

    assert atomic_str._is_empty is True
    assert atomic_str._value is None
    assert atomic_str._on_complete_funcs == []

    assert atomic_int._is_empty is True
    assert atomic_int._value is None
    assert atomic_int._on_complete_funcs == []

    assert atomic_dict._is_empty is True
    assert atomic_dict._value is None
    assert atomic_dict._on_complete_funcs == []


def test_atomic_update_string() -> None:
    """Test updating jv.Atomic with string value."""
    atomic_obj = jv.Atomic(str)
    atomic_obj.update("hello")

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == "hello"
    assert atomic_obj.get_value() == "hello"


def test_atomic_update_integer() -> None:
    """Test updating jv.Atomic with integer value."""
    atomic_obj = jv.Atomic(int)
    atomic_obj.update(42)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == 42
    assert atomic_obj.get_value() == 42


def test_atomic_update_dict() -> None:
    """Test updating jv.Atomic with dictionary value."""
    atomic_obj = jv.Atomic(dict)
    test_dict = {"key": "value", "number": 123}
    atomic_obj.update(test_dict)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == test_dict
    assert atomic_obj.get_value() == test_dict


def test_atomic_update_list() -> None:
    """Test updating jv.Atomic with list value."""
    atomic_obj = jv.Atomic(list)
    test_list = ["item1", "item2", "item3"]
    atomic_obj.update(test_list)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == test_list
    assert atomic_obj.get_value() == test_list


def test_atomic_update_none_value() -> None:
    """Test updating jv.Atomic with None value."""
    atomic_obj = jv.Atomic(type(None))
    atomic_obj.update(None)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value is None
    assert atomic_obj.get_value() is None


def test_atomic_update_multiple_times() -> None:
    """Test updating jv.Atomic multiple times overwrites previous value."""
    atomic_obj = jv.Atomic(str)

    atomic_obj.update("first")
    assert atomic_obj.get_value() == "first"

    atomic_obj.update("second")
    assert atomic_obj.get_value() == "second"

    atomic_obj.update("third")
    assert atomic_obj.get_value() == "third"

    assert atomic_obj._is_empty is False


def test_atomic_update_empty_string() -> None:
    """Test updating jv.Atomic with empty string."""
    atomic_obj = jv.Atomic(str)
    atomic_obj.update("")

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == ""
    assert atomic_obj.get_value() == ""


def test_atomic_update_zero() -> None:
    """Test updating jv.Atomic with zero value."""
    atomic_obj = jv.Atomic(int)
    atomic_obj.update(0)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value == 0
    assert atomic_obj.get_value() == 0


def test_atomic_update_false() -> None:
    """Test updating jv.Atomic with False value."""
    atomic_obj = jv.Atomic(bool)
    atomic_obj.update(False)

    assert atomic_obj._is_empty is False
    assert atomic_obj._value is False
    assert atomic_obj.get_value() is False


def test_atomic_value_property_before_update() -> None:
    """Test value property returns None when not updated."""
    atomic_obj = jv.Atomic(str)

    assert atomic_obj.get_value() is None
    assert atomic_obj._is_empty is True


def test_atomic_on_complete_single_callback() -> None:
    """Test registering and triggering a single completion callback."""
    atomic_obj = jv.Atomic(str)
    completed_values = []

    def callback(value: str | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)
    atomic_obj.update("test_value")
    atomic_obj._complete()

    assert completed_values == ["test_value"]


def test_atomic_on_complete_multiple_callbacks() -> None:
    """Test multiple callbacks are all triggered on completion."""
    atomic_obj = jv.Atomic(int)
    completed_values_1 = []
    completed_values_2 = []

    def callback1(value: int | None) -> None:
        completed_values_1.append(value)

    def callback2(value: int | None) -> None:
        completed_values_2.append(value * 2 if value is not None else None)

    atomic_obj.on_complete(callback1)
    atomic_obj.on_complete(callback2)
    atomic_obj.update(21)
    atomic_obj._complete()

    assert completed_values_1 == [21]
    assert completed_values_2 == [42]


def test_atomic_on_complete_callback_order() -> None:
    """Test callbacks are called in registration order."""
    atomic_obj = jv.Atomic(str)
    call_order = []

    def callback1(value: str | None) -> None:
        call_order.append("callback1")

    def callback2(value: str | None) -> None:
        call_order.append("callback2")

    def callback3(value: str | None) -> None:
        call_order.append("callback3")

    atomic_obj.on_complete(callback1)
    atomic_obj.on_complete(callback2)
    atomic_obj.on_complete(callback3)
    atomic_obj.update("test")
    atomic_obj._complete()

    assert call_order == ["callback1", "callback2", "callback3"]


def test_atomic_complete_without_update() -> None:
    """Test complete method when no update has been called (empty state)."""
    atomic_obj = jv.Atomic(str)
    completed_values = []

    def callback(value: str | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)
    atomic_obj._complete()

    # No callback should be triggered when empty
    assert completed_values == []


def test_atomic_complete_with_none_value() -> None:
    """Test complete method when value was explicitly set to None."""
    atomic_obj = jv.Atomic(type(None))
    completed_values = []

    def callback(value: str | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)
    atomic_obj.update(None)
    atomic_obj._complete()

    assert completed_values == [None]


def test_atomic_complete_multiple_calls() -> None:
    """Test complete method can be called multiple times."""
    atomic_obj = jv.Atomic(str)
    completed_values = []

    def callback(value: str | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)
    atomic_obj.update("hello")
    atomic_obj._complete()
    atomic_obj._complete()

    assert completed_values == ["hello", "hello"]


def test_atomic_complete_no_callbacks() -> None:
    """Test complete method works when no callbacks are registered."""
    atomic_obj = jv.Atomic(str)
    atomic_obj.update("test")
    # Should not raise an exception
    atomic_obj._complete()


def test_atomic_complete_after_multiple_updates() -> None:
    """Test complete method after multiple updates (should use latest value)."""
    atomic_obj = jv.Atomic(str)
    completed_values = []

    def callback(value: str | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)
    atomic_obj.update("first")
    atomic_obj.update("second")
    atomic_obj.update("final")
    atomic_obj._complete()

    assert completed_values == ["final"]


def test_atomic_complex_object_value() -> None:
    """Test jv.Atomic with complex object as value."""
    atomic_obj = jv.Atomic(dict[str, Any])
    completed_values = []

    def callback(value: dict[str, Any] | None) -> None:
        completed_values.append(value)

    atomic_obj.on_complete(callback)

    complex_dict = {"nested": {"key": "value"}, "list": [1, 2, 3], "string": "test"}

    atomic_obj.update(complex_dict)
    atomic_obj._complete()

    assert completed_values == [complex_dict]
    assert atomic_obj.get_value() == complex_dict


def test_atomic_boolean_values() -> None:
    """Test jv.Atomic with boolean values."""
    atomic_true = jv.Atomic(bool)
    atomic_false = jv.Atomic(bool)

    completed_true = []
    completed_false = []

    def callback_true(value: bool | None) -> None:
        completed_true.append(value)

    def callback_false(value: bool | None) -> None:
        completed_false.append(value)

    atomic_true.on_complete(callback_true)
    atomic_false.on_complete(callback_false)

    atomic_true.update(True)
    atomic_false.update(False)

    atomic_true._complete()
    atomic_false._complete()

    assert completed_true == [True]
    assert completed_false == [False]
    assert atomic_true.get_value() is True
    assert atomic_false.get_value() is False


def test_atomic_numeric_values() -> None:
    """Test jv.Atomic with various numeric values."""
    atomic_int = jv.Atomic(int)
    atomic_float = jv.Atomic(float)

    completed_int = []
    completed_float = []

    def callback_int(value: int | None) -> None:
        completed_int.append(value)

    def callback_float(value: float | None) -> None:
        completed_float.append(value)

    atomic_int.on_complete(callback_int)
    atomic_float.on_complete(callback_float)

    atomic_int.update(-42)
    atomic_float.update(3.14159)

    atomic_int._complete()
    atomic_float._complete()

    assert completed_int == [-42]
    assert completed_float == [3.14159]
    assert atomic_int.get_value() == -42
    assert atomic_float.get_value() == 3.14159


def test_atomic_update_overwrite_behavior() -> None:
    """Test that updates completely overwrite previous values."""
    atomic_obj = jv.Atomic(list)

    # First update
    atomic_obj.update([1, 2, 3])
    assert atomic_obj.get_value() == [1, 2, 3]

    # Second update should completely replace
    atomic_obj.update(["a", "b"])
    assert atomic_obj.get_value() == ["a", "b"]

    # Third update with empty list
    atomic_obj.update([])
    assert atomic_obj.get_value() == []

    assert atomic_obj._is_empty is False  # Still not empty, just has empty list


def test_atomic_state_consistency() -> None:
    """Test internal state consistency throughout operations."""
    atomic_obj = jv.Atomic(str)

    # Initial state
    assert atomic_obj._is_empty is True
    assert atomic_obj._value is None
    assert atomic_obj.get_value() is None

    # After update
    atomic_obj.update("test")
    assert atomic_obj._is_empty is False
    assert atomic_obj._value == "test"  # type: ignore
    assert atomic_obj.get_value() == "test"

    # After another update
    atomic_obj.update("changed")
    assert atomic_obj._is_empty is False
    assert atomic_obj._value == "changed"
    assert atomic_obj.get_value() == "changed"


def test_atomic_complete_callback_with_type_info() -> None:
    """Test completion callbacks receive correct type information."""
    atomic_str = jv.Atomic(str)
    atomic_int = jv.Atomic(int)

    received_types = []

    def str_callback(value: str | None) -> None:
        received_types.append(type(value).__name__)

    def int_callback(value: int | None) -> None:
        received_types.append(type(value).__name__)

    atomic_str.on_complete(str_callback)
    atomic_int.on_complete(int_callback)

    atomic_str.update("hello")
    atomic_int.update(42)

    atomic_str._complete()
    atomic_int._complete()

    assert received_types == ["str", "int"]
