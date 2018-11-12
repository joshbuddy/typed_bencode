from typing import List
from io import BytesIO
from abc import ABC

def for_dict(**kwargs):
    return DictType(**kwargs)

def for_list(**kwargs):
    return ListType(**kwargs)

def for_str(**kwargs):
    return StringType(**kwargs)

def for_int(**kwargs):
    return IntType(**kwargs)

def for_bytes(**kwargs):
    return BytesType(**kwargs)

def wrap_type(t):
    if isinstance(t, BaseType):
        return t
    if t is int:
        return IntType()
    elif t is bytes:
        return BytesType()
    elif t is str:
        return StringType()
    elif hasattr(t, "__origin__") and t.__origin__ is list:
        return ListType(t.__args__[0])
    else:
        raise Exception(f"could not construct a type for {t}")

class BaseType(ABC):
    def __init__(self):
        self.defaults = {}

    def encode(self, val):
        return self.encoder.to_bytes(val)

    def decode(self, b):
        out, _ = self.decoder.from_bytes(b)
        return out

class BaseEncoder(ABC):
    def __init__(self, type):
        self.type = type

class BaseDecoder(ABC):
    def __init__(self, type):
        self.type = type

class IntType(BaseType):
    def __init__(self):
        super().__init__()
        self.encoder = IntEncoder(self)
        self.decoder = IntDecoder(self)

class StringType(BaseType):
    def __init__(self):
        super().__init__()
        self.encoder = StringEncoder(self)
        self.decoder = StringDecoder(self)

class BytesType(BaseType):
    def __init__(self):
        super().__init__()
        self.encoder = BytesEncoder(self)
        self.decoder = BytesDecoder(self)

class ListType(BaseType):
    def __init__(self, subtype):
        super().__init__()
        self.subtype = wrap_type(subtype)
        self.encoder = ListEncoder(self)
        self.decoder = ListDecoder(self)

class DictType(BaseType):
    def __init__(self, **kwargs):
        super().__init__()
        self.fields = {}
        for name, type in kwargs.items():
            self.fields[name] = wrap_type(type)

        self.field_names = list(self.fields.keys())
        self.field_names.sort()
        self.encoder = DictEncoder(self)
        self.decoder = DictDecoder(self)

    def default(self, **kwargs):
        for name, default in kwargs.items():
            self.defaults[name] = default
        return self

class DictEncoder(BaseEncoder):
    def to_bytes(self, values):
        out = BytesIO()
        out.write(b'd')
        for name in self.type.field_names:
            wrapped_type = self.type.fields[name]
            if name in values:
                value = values[name]
            elif name in self.type.defaults:
                value = self.type.defaults[name]
            else:
                raise ValueError(f"attempt to encode a dict, missing '{name}', and not present in defaults")
            out.write(str(len(name)).encode())
            out.write(b':')
            out.write(name.encode())
            out.write(wrapped_type.encoder.to_bytes(value))
        out.write(b'e')
        return out.getvalue()

class DictDecoder(BaseDecoder):
    def from_bytes(self, b, pos=0):
        assert b[pos] == 100, f"expected byte at {pos} {b[pos]} to be 100 (d)"
        pos += 1
        out = {}
        while pos < len(b) - 1:
            if b[pos] == 101: # e
                break
            key, pos = StringDecoder(None).from_bytes(b, pos)
            wrapped_type = self.type.fields[key]
            val, pos = wrapped_type.decoder.from_bytes(b, pos)
            out[key] = val
        assert b[pos] == 101, f"expected byte at {pos} {b[pos]} to be 101 (e)"
        return (out, pos+1)

class StringEncoder(BaseEncoder):
    def to_bytes(self, value):
        return f"{len(value)}:{value}".encode()

class StringDecoder(BaseDecoder):
    def from_bytes(self, b, pos=0):
        sep_index = b.find(b':', pos)
        length = int(b[pos:sep_index].decode())
        start_index = sep_index + 1
        end_index = start_index + length
        return (b[start_index:end_index].decode(), end_index)

class BytesEncoder(BaseEncoder):
    def to_bytes(self, value):
        return f"{len(value)}:".encode() + value

class BytesDecoder(BaseDecoder):
    def from_bytes(self, b, pos=0):
        sep_index = b.find(b':', pos)
        length = int(b[pos:sep_index].decode())
        start_index = sep_index + 1
        end_index = start_index + length
        return (b[start_index:end_index], end_index)

class IntEncoder(BaseEncoder):
    def to_bytes(self, value):
        return f"i{value}e".encode()

class IntDecoder(BaseEncoder):
    def from_bytes(self, b, pos=0):
        assert b[pos] == 105, f"expected byte at {pos} {b[pos]} to be 105 (i)"
        end_index = b.find(b'e', pos)
        value = int(b[pos+1:end_index].decode())
        pos = end_index
        assert b[pos] == 101, f"expected byte at {pos} {b[pos]} to be 101 (e)"
        return (value, pos+1)

class ListEncoder(BaseEncoder):
    def to_bytes(self, values):
        out = BytesIO()
        out.write(b'l')
        for v in values:
            out.write(self.type.subtype.encoder.to_bytes(v))
        out.write(b'e')
        return out.getvalue()

class ListDecoder(BaseDecoder):
    def from_bytes(self, b, pos=0):
        assert b[pos] == 108, f"expected byte at {pos} {b[pos]} to be 108 (l)"
        pos += 1
        out = []
        while pos < len(b) - 1:
            if b[pos] == 101: # e
                break
            val, pos = self.type.subtype.decoder.from_bytes(b, pos)
            out.append(val)
        assert b[pos] == 101, f"expected byte at {pos} {b[pos]} to be 101 (e)"
        return (out, pos+1)
