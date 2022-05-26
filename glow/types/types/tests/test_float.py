# Third-party
import pytest

# Glow
from glow.types.casting import safe_cast, can_cast_type
from glow.types.serialization import type_to_json_encodable


@pytest.mark.parametrize(
    "value, expected_cast_value, expected_err_msg",
    (
        (1.23, 1.23, None),
        (int(1), 1.0, None),
        ("3.14", 3.14, None),
        ("abc", None, "Cannot cast 'abc' to <class 'float'>"),
    ),
)
def test_safe_cast(value, expected_cast_value, expected_err_msg):
    cast_value, err_msg = safe_cast(value, float)
    assert cast_value == expected_cast_value
    if expected_err_msg is None:
        assert isinstance(cast_value, float)
    assert err_msg == expected_err_msg


def test_can_cast_type():
    assert can_cast_type(int, float) == (True, None)


def test_type_to_json_encodable():
    assert type_to_json_encodable(float) == {
        "type": ("builtin", "float", {}),
        "registry": {"float": []},
    }
