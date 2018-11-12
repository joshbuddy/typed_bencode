# TypedBencode

Make it easy to create round-trippable bencoding for objects.

## Usage

```python
import typed_bencode
from typing import List

a = typed_bencode.dict(a=str, b=int, c=bytes, d=List[str])
encoded = a.encode(a="hello", b=123, c=b'asd', d=["hey", "there"])
print(encoded) # => b'd1:a5:hello1:bi123e1:c3:asd1:dl3:hey5:thereee'
print(a.decode(encoded)) # => {'a': 'hello', 'b': 123, 'c': b'asd', 'd': ['hey', 'there']}

```
