# TypedBencode

Make it easy to create round-trippable bencoding for objects.

## Usage

```python
import typed_bencode
from typing import List

my_type = typed_bencode.dict(a=str, b=int, c=bytes, d=List[str])
val = {"a": "hello", "b": 123, "c": b'asd', "d":["hey", "there"]}
encoded = my_type.encode(val)
print(encoded) # => b'd1:a5:hello1:bi123e1:c3:asd1:dl3:hey5:thereee'
print(my_type.decode(encoded) == val) # => True

```

You can even compose types

```python
my_other_type = typed_bencode.dict(a=my_type, b=int)

encoded2 = my_other_type.encode({"a": {"a": "helo", "b": 123, "c": b'asd', "d": ["asd", "asd"]}, "b":123})
print(encoded2) # => b'd1:ad1:a4:helo1:bi123e1:c3:asd1:dl3:asd3:asdee1:bi123ee'

```
