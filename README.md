# TypedBencode

Make it easy to create round-trippable bencoding for objects.

## Usage

```python
import typed_bencode
from typing import List

my_type = typed_bencode.for_dict(a=str, b=int, c=bytes, d=List[str])
val = {"a": "hello", "b": 123, "c": b'asd', "d":["hey", "there"]}
encoded = my_type.encode(val)
print(encoded) # => b'd1:a5:hello1:bi123e1:c3:asd1:dl3:hey5:thereee'
print(my_type.decode(encoded) == val) # => True

```

You can even compose types

```python
my_other_type = typed_bencode.for_dict(a=my_type, b=int)

encoded2 = my_other_type.encode({"a": {"a": "helo", "b": 123, "c": b'asd', "d": ["asd", "asd"]}, "b":123})
print(encoded2) # => b'd1:ad1:a4:helo1:bi123e1:c3:asd1:dl3:asd3:asdee1:bi123ee'

```

### Custom types

You can specify a custom type

```python
class DateEncoder(typed_bencode.StringEncoder):
    def to_bytes(self, val):
        return super().to_bytes(val.isoformat())

class DateDecoder(typed_bencode.StringDecoder):
    def from_bytes(self, b):
        v, pos = super().from_bytes(b)
        return (datetime.datetime.fromisoformat(v), pos)

class DateType(typed_bencode.BaseType):
    def __init__(self):
        super().__init__()
        self.encoder = DateEncoder(self)
        self.decoder = DateDecoder(self)

my_type = DateType()
val = datetime.datetime.now()
encoded = my_type.encode(val) # => '26:2018-06-06T12:12:12.363636'
```
