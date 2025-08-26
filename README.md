# jsonversation

A Python library for streaming JSON parsing that enables real-time processing of JSON data as it arrives. Perfect for handling large JSON responses, streaming APIs, or any scenario where you need to process JSON data progressively.



## Installation

Coming soon!


## Key Features

-   **Streaming JSON Parsing**: Process JSON data as it arrives, without waiting for complete payloads
-   **Type-Safe Models**: Define strongly-typed data structures with automatic validation
-   **Real-time Callbacks**: React to data changes as they happen with customizable callbacks
-   **Progressive Updates**: Handle partial JSON data and incremental updates seamlessly



## Quick Start



### Basic Usage

```python
from jsonversation import Parser
from jsonversation.models import Object, String, List, Atomic

# Define your data structure
class ChatMessage(Object):
    role: String
    content: String
    timestamp: String
    token_count: Atomic[int]
    is_complete: Atomic[bool]

# Create a parser
message = ChatMessage()
parser = Parser(message)

# Process streaming JSON data
json_chunk1 = '{"role": "assistant", "content": "Hello'
json_chunk2 = ' world!", "timestamp": "2024-01-01T12:00:00Z", "token_count": 42, "is_complete": true}'

with Parser(message) as parser:
    parser.push(json_chunk1)
    print(message.content.value)  # "Hello"

    parser.push(json_chunk2)
    print(message.content.value)     # "Hello world!"
    print(message.role.value)        # "assistant"
    print(message.token_count.value) # 42
    print(message.is_complete.value) # True
```


### Real-time Callbacks

```python
    from jsonversation import Parser
    from jsonversation.models import Object, String, List
    
    class StreamingResponse(Object):
        message: String
        tokens: List[String]
    
    response = StreamingResponse()
    
    # Set up real-time callbacks
    def on_message_update(chunk: str):
        print(f"New text: {chunk}")
    
    def on_new_token(token: String):
        print(f"New token: {token.value}")
    
    def on_message_complete(full_message: str):
        print(f"Complete message: {full_message}")
    
    response.message.on_append(on_message_update)
    response.tokens.on_append(on_new_token)
    response.message.on_complete(on_message_complete)
    
    # Simulate streaming data
    with Parser(response) as parser:
        parser.push('{"message": "The quick")
        parser.push(' brown fox", "tokens": ["The", "quick"]}')
```

### Working with Atomic Types

The `Atomic` class handles primitive types that arrive as complete values rather than streaming text:

```python
from jsonversation.models import Object, String, Atomic

class APIResponse(Object):
    message: String
    status_code: Atomic[int]
    success: Atomic[bool]
    response_time: Atomic[float]
    metadata: Atomic[dict]

response = APIResponse()

# Set up callbacks for atomic values
def on_status_change(status: int | None):
    if status:
        print(f"Status code: {status}")
        if status >= 400:
            print("Error response detected!")

def on_completion(success: bool | None):
    if success is not None:
        print(f"Request {'succeeded' if success else 'failed'}")

response.status_code.on_complete(on_status_change)
response.success.on_complete(on_completion)

# Process JSON with atomic values
with Parser(response) as parser:
    parser.push('{"message": "Processing request", "status_code": 200}')
    parser.push('{"message": "Request completed", "status_code": 200, "success": true, "response_time": 1.23}')
    # Callbacks will be triggered when atomic values are completed

print(response.status_code.value)  # 200
print(response.success.value)      # True
print(response.response_time.value) # 1.23
```


### Complex Nested Structures

```python
    from jsonversation.models import Object, String, List
    
    class Author(Object):
        name: String
        email: String
    
    class Comment(Object):
        id: String
        text: String
        author: Author
    
    class BlogPost(Object):
        title: String
        content: String
        author: Author
        comments: List[Comment]
        tags: List[String]
    
    # Create and use the parser
    post = BlogPost()
    
    # Process complex JSON
    complex_json = '''
    {
        "title": "Streaming JSON in Python",
        "content": "This is a comprehensive guide...",
        "author": {
            "name": "Jane Doe",
            "email": "jane@example.com"
        },
        "comments": [
            {
                "id": "1",
                "text": "Great article!",
                "author": {
                    "name": "John Smith",
                    "email": "john@example.com"
                }
            }
        ],
        "tags": ["python", "json", "streaming"]
    }
    '''
    
    with Parser(post) as parser:
        parser.push(complex_json)
        # Access nested data
        print(post.title.value)                    # "Streaming JSON in Python"
        print(post.author.name.value)              # "Jane Doe"
        print(post.comments.value[0].text.value)   # "Great article!"
        print([tag.value for tag in post.tags.value])  # ["python", "json", "streaming"]
```


### Streaming API Example

Here's how you might use jsonversation with a streaming API like OpenAI's chat completions:

```python
    import httpx
    from jsonversation import Parser
    from jsonversation.models import Object, String, List
    
    class ChatChoice(Object):
        index: String
        message: Object  # Could be further defined
        finish_reason: String
    
    class ChatCompletion(Object):
        id: String
        object: String
        model: String
        choices: List[ChatChoice]
    
    async def stream_chat_completion():
        completion = ChatCompletion()
    
        # Set up callbacks for real-time processing
        def on_new_choice(choice: ChatChoice):
            print(f"New choice received: {choice.index.value}")
    
        completion.choices.on_append(on_new_choice)
    
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST", 
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Hello!"}],
                    "stream": True
                }
            ) as response:
                with Parser(completion) as parser:
                    async for chunk in response.aiter_text():
                        if chunk:
                            parser.push(chunk)
                            # Process data in real-time as it arrives
```


### WebSocket Streaming

```python
    import asyncio
    import websockets
    from jsonversation import Parser
    from jsonversation.models import Object, String, List
    
    class LiveData(Object):
        timestamp: String
        values: List[String]
        status: String
    
    async def handle_websocket():
        live_data = LiveData()
        
    
        def on_status_change(chunk: str):
            print(f"Status update: {live_data.status.value}")
    
        def on_new_value(value: String):
            print(f"New value: {value.value}")
    
        live_data.status.on_append(on_status_change)
        live_data.values.on_append(on_new_value)
    
        async with websockets.connect("ws://example.com/live") as websocket:
            with Parser(live_data) as parser:
                async for message in websocket:
                    parser.push(message)
                    # Data is processed incrementally
```


## API Reference



### Core Classes

1.  `Parser(obj: Object)`

    Main parser class for processing streaming JSON data.
    
    **Methods:**
    
    -   `push(chunk: str)` - Process a chunk of JSON data

2.  `Object`

    Base class for defining structured data models.
    
    **Methods:**
    
    -   `update(value: dict)` - Update object with dictionary data

3.  `String`

    String field type with streaming capabilities.
    
    **Properties:**
    
    -   `value` - Get current string value
    
    **Methods:**
    
    -   `on_append(callback)` - Register callback for new text chunks
    -   `on_complete(callback)` - Register callback for completion
    -   `update(value: str)` - Update with new string value

4.  `List[T]`

    List field type for collections of items.
    
    **Properties:**
    
    -   `value` - Get current list of items
    
    **Methods:**
    
    -   `on_append(callback)` - Register callback for new items
    -   `on_complete(callback)` - Register callback for completion
    -   `update(value: list)` - Update with new list data



## Advanced Usage



### Custom Callbacks

```python
    class ProgressTracker(Object):
        current: String
        total: String
        percentage: String
    
    tracker = ProgressTracker()
    parser = Parser(tracker)
    
    def calculate_progress(chunk: str):
        try:
            current = int(tracker.current.value)
            total = int(tracker.total.value)
            if total > 0:
                percentage = (current / total) * 100
                print(f"Progress: {percentage:.1f}%")
        except (ValueError, ZeroDivisionError):
            pass
    
    tracker.current.on_append(lambda _: calculate_progress(""))
    tracker.total.on_append(lambda _: calculate_progress(""))
```


## Requirements

-   Python 3.9+
-   jiter (for JSON parsing)



## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.



## License

TBD

