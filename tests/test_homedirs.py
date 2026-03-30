from hadalized.base import Home


def test_homedirs():
    assert Home.build()
    assert Home.cache()
    assert Home.config()
    assert Home.template()
    assert Home.state()
    assert Home.data()
