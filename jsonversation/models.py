from __future__ import annotations
import typing
import io
from typing import Callable


class StreamingObject[T]:
    def __init__(self) -> None:
        self._on_append_funcs = []

    def update(self, value: T) -> None:
        return None


class Object(StreamingObject[dict]):
    def __init__(self) -> None:
        super().__init__()
        self._keys = []
        for key, type_hint in type(self).__annotations__.items():
            self._keys.append(key)

            # Handle List[T]
            if hasattr(type_hint, "__origin__"):
                item_cls = typing.get_args(type_hint)[0]
                setattr(self, key, type_hint.__origin__(item_cls))
            else:
                setattr(self, key, type_hint())

    def update(self, value: dict):
        model_keys = self._keys
        for key in value.keys():
            if key not in model_keys:
                continue

            model_value = self.__getattribute__(key)
            model_value.update(value[key])

        return


class String(StreamingObject[str]):
    _value: io.StringIO
    _on_append_funcs: list[Callable[[str], None]]

    def __init__(self) -> None:
        super().__init__()
        self._value = io.StringIO()

    def update(self, value: str):
        current_buffer_value = self._value.getvalue()
        current_buffer_length = len(current_buffer_value)
        new_chunk = None

        if current_buffer_length == 0:
            new_chunk = value
        elif len(value) == current_buffer_length:
            return
        elif len(value) > current_buffer_length:
            new_chunk = value.replace(current_buffer_value, "")

        if new_chunk:
            self._value.write(new_chunk)
            [f(new_chunk) for f in self._on_append_funcs]

        return

    def on_append(self, func: Callable[[str], None]) -> None:
        self._on_append_funcs.append(func)

    @property
    def value(self) -> str:
        return self._value.getvalue()


class List[T: StreamingObject](StreamingObject[list]):
    _item_type: type[T]
    _values: list[T]
    _on_append_funcs: list[Callable[[T], None]]

    def __init__(self, item_type: type[T]) -> None:
        super().__init__()
        self._values = []
        self._item_type = item_type

    def update(self, value: list) -> None:
        if not value:
            return

        # NOTE this is not very efficient, but it will do for now
        for idx, item in enumerate(value):
            if idx >= len(self._values):
                new_value = self._item_type()
                new_value.update(item)
                self._values.append(new_value)
                for func in self._on_append_funcs:
                    func(new_value)
            else:
                existing_value = self._values[idx]
                existing_value.update(item)

        return None

    def on_append(self, func: Callable[[T], None]) -> None:
        self._on_append_funcs.append(func)

    @property
    def value(self) -> list[T]:
        return self._values
