import pytest

from hadalized.base import BaseNode


class Node(BaseNode):
    x: int = 1
    y: int = 2
    z: int = 3


class Node2(Node):
    w: int = 4


class Model(BaseNode):
    val: int = 1
    d: dict[int, int]
    node: Node = Node()


class Model2(Model):
    pass


def test_merge_same_type():
    node = Node(x=2)
    old = Model(d={1: 1, 2: 3}, node=node)
    new = Model(d={2: 2}, val=3)
    merged = old | new
    assert merged.node == node
    assert merged.d == {1: 1, 2: 2}
    assert merged.val == 3


@pytest.mark.parametrize(
    ("left", "right", "expected_cls"),
    [
        (Node(), Node2(w=4), Node2),
        (Node2(w=4), Node(), Node),
        (Model(d={}), Model2(d={}), Model2),
        (Model2(d={}), Model(d={}), Model),
    ],
)
def test_merge_is_right_type(left, right, expected_cls):
    """Ensure proper types when nodes are merged.

    Also ensures that

    """
    assert isinstance(left | right, expected_cls)


def test_model_dump_lua():
    node = Node(x=2)
    model = Model(d={1: 1, 2: 3}, node=node)
    model.model_dump_lua()
