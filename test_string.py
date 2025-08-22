"""
Unit tests for String operations and methods using pytest.
"""


def test_string_creation():
    """Test string creation and basic properties."""
    s = "test"
    assert s == "test"
    assert isinstance(s, str)
    assert len(s) == 4


def test_string_concatenation():
    """Test string concatenation operations."""
    s1 = "Hello"
    s2 = "World"
    result = s1 + " " + s2
    assert result == "Hello World"
    
    # Test += operator
    s1 += " " + s2
    assert s1 == "Hello World"


def test_string_repetition():
    """Test string repetition with * operator."""
    s = "Hi"
    result = s * 3
    assert result == "HiHiHi"
    
    result = 3 * s
    assert result == "HiHiHi"


def test_string_indexing():
    """Test string indexing and slicing."""
    s = "Hello"
    assert s[0] == "H"
    assert s[-1] == "o"
    assert s[1:4] == "ell"
    assert s[:3] == "Hel"
    assert s[2:] == "llo"


def test_string_methods_case():
    """Test string case conversion methods."""
    s = "Hello World"
    assert s.upper() == "HELLO WORLD"
    assert s.lower() == "hello world"
    assert s.title() == "Hello World"
    assert s.capitalize() == "Hello world"
    assert s.swapcase() == "hELLO wORLD"


def test_string_methods_whitespace():
    """Test string whitespace handling methods."""
    s = "  Hello World  "
    assert s.strip() == "Hello World"
    assert s.lstrip() == "Hello World  "
    assert s.rstrip() == "  Hello World"
    
    # Test with specific characters
    s2 = "...Hello World..."
    assert s2.strip(".") == "Hello World"


def test_string_methods_search():
    """Test string search and find methods."""
    s = "Hello World Hello"
    assert s.find("World") == 6
    assert s.find("xyz") == -1
    assert s.rfind("Hello") == 12
    assert s.index("World") == 6
    assert s.count("Hello") == 2
    assert s.count("l") == 3


def test_string_methods_boolean():
    """Test string boolean check methods."""
    assert "Hello".isalpha()
    assert not "Hello123".isalpha()
    assert "12345".isdigit()
    assert not "Hello".isdigit()
    assert "Hello123".isalnum()
    assert not "Hello World".isalnum()
    assert "hello world".islower()
    assert "HELLO WORLD".isupper()
    assert "Hello World".istitle()


def test_string_methods_split_join():
    """Test string split and join methods."""
    s = "Hello,World,Python"
    parts = s.split(",")
    assert parts == ["Hello", "World", "Python"]
    
    rejoined = ",".join(parts)
    assert rejoined == s
    
    # Test split with maxsplit
    parts2 = s.split(",", 1)
    assert parts2 == ["Hello", "World,Python"]


def test_string_methods_replace():
    """Test string replace method."""
    s = "Hello World Hello"
    result = s.replace("Hello", "Hi")
    assert result == "Hi World Hi"
    
    # Test with count parameter
    result2 = s.replace("Hello", "Hi", 1)
    assert result2 == "Hi World Hello"


def test_string_methods_startswith_endswith():
    """Test string prefix and suffix checking."""
    s = "Hello World"
    assert s.startswith("Hello")
    assert not s.startswith("World")
    assert s.endswith("World")
    assert not s.endswith("Hello")
    
    # Test with tuples
    assert s.startswith(("Hi", "Hello"))
    assert s.endswith(("World", "Universe"))


def test_string_formatting():
    """Test string formatting methods."""
    # Test format method
    template = "Hello {name}, you are {age} years old"
    result = template.format(name="Alice", age=30)
    assert result == "Hello Alice, you are 30 years old"
    
    # Test f-strings (Python 3.6+)
    name = "Bob"
    age = 25
    result = f"Hello {name}, you are {age} years old"
    assert result == "Hello Bob, you are 25 years old"
    
    # Test % formatting
    result = "Hello %s, you are %d years old" % ("Charlie", 35)
    assert result == "Hello Charlie, you are 35 years old"


def test_string_encoding_decoding():
    """Test string encoding and decoding."""
    s = "Hello World"
    encoded = s.encode('utf-8')
    assert isinstance(encoded, bytes)
    
    decoded = encoded.decode('utf-8')
    assert decoded == s


def test_empty_string():
    """Test operations on empty strings."""
    s = ""
    assert len(s) == 0
    assert s == ""
    assert not bool(s)
    assert s.upper() == ""
    assert s.split() == []


def test_string_comparison():
    """Test string comparison operations."""
    assert "apple" < "banana"
    assert "Apple" < "apple"  # ASCII comparison
    assert "hello" == "hello"
    assert "hello" != "Hello"
    assert "abc" <= "abc"
    assert "xyz" > "abc"


def test_string_membership():
    """Test string membership operations."""
    s = "Hello World"
    assert "Hello" in s
    assert "World" in s
    assert "Python" not in s
    assert not ("Python" in s)


def test_string_immutability():
    """Test that strings are immutable."""
    s = "Hello"
    original_id = id(s)
    s = s.upper()
    assert id(s) != original_id
    assert s == "HELLO"
