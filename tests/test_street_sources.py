import pytest
from tools.fetch_street_sources import texture_plan


def test_texture_roles():
    meta={k:{"1k":{"jpg":{"url":"https://dl.polyhaven.org/map.jpg","size":12}}} for k in ("Diffuse","nor_gl","Rough")}
    assert set(texture_plan(meta))=={"color","normal","rough"}
    del meta["nor_gl"]
    with pytest.raises(ValueError): texture_plan(meta)
