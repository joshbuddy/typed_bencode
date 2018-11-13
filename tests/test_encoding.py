import datetime
import typed_bencode
from typing import List
from unittest import TestCase


class TestEncoding(TestCase):
    def test_simple_encoding(self):
        my_type = typed_bencode.for_dict(a=str, b=int, c=bytes, d=List[str])
        val = {"a": "hello", "b": 123, "c": b"asd", "d": ["hey", "there"]}
        encoded = my_type.encode(val)
        self.assertEqual(encoded, b"d1:a5:hello1:bi123e1:c3:asd1:dl3:hey5:thereee")

    def test_complex_encoding(self):
        my_sub_type = typed_bencode.for_dict(a=str, b=int)
        my_type = typed_bencode.for_dict(a=str, b=int, c=bytes, d=my_sub_type)
        val = {"a": "hello", "b": 123, "c": b"asd", "d": {"a": "asd", "b": 321}}
        encoded = my_type.encode(val)
        self.assertEqual(encoded, b"d1:a5:hello1:bi123e1:c3:asd1:dd1:a3:asd1:bi321eee")

    def test_default_encoding(self):
        my_type = typed_bencode.for_dict(a=str, b=int, c=bytes).default(b=321)
        val = {"a": "hello", "c": b"asd", "d": ["hey", "there"]}
        encoded = my_type.encode(val)
        self.assertEqual(encoded, b"d1:a5:hello1:bi321e1:c3:asde")

    def test_missing_value(self):
        my_type = typed_bencode.for_dict(a=str, b=int, c=bytes)
        val = {"a": "hello"}
        with self.assertRaises(
            ValueError,
            msg="attempt to encode a dict, missing 'b', and not present in defaults",
        ):
            my_type.encode(val)

    def test_custom_type(self):
        class DateEncoder(typed_bencode.StringEncoder):
            def to_bytes(self, val):
                return super().to_bytes(val.isoformat())

        class DateDecoder(typed_bencode.StringDecoder):
            def from_bytes(self, b, pos):
                v, pos = super().from_bytes(b, pos)
                return (datetime.datetime.fromisoformat(v), pos)

        class DateType(typed_bencode.BaseType):
            def __init__(self):
                super().__init__()
                self.encoder = DateEncoder(self)
                self.decoder = DateDecoder(self)

        my_type = DateType()
        val = datetime.datetime.now()
        encoded = my_type.encode(val)
        self.assertEqual(encoded, f"26:{val.isoformat()}".encode())
        decoded = my_type.decode(encoded)
        self.assertEqual(decoded, val)
