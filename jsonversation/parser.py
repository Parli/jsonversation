import jiter
import io

from jsonversation.models import Object


class Parser:
    _buffer: io.BytesIO
    _object: Object

    def __init__(self, obj: Object) -> None:
        self._object = obj
        self._buffer = io.BytesIO()

    def push(self, chunk: str) -> None:
        if not chunk.strip():
            return None

        self._buffer.write(chunk.encode())
        parsed_dict = jiter.from_json(
            self._buffer.getvalue(), partial_mode="trailing-strings"
        )
        self._object.update(parsed_dict)
