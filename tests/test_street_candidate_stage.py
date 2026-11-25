import hashlib
import zipfile
import pytest
from tools.stage_street_candidate import read_asset


def test_exact_zip_member(tmp_path):
    path=tmp_path/"input.zip"
    data=b"fixture"
    with zipfile.ZipFile(path,"w") as archive:
        archive.writestr("frozen/adrian.glb",data)
        archive.writestr("../unrelated.txt",b"do not extract")
    assert read_asset(path,"frozen/adrian.glb",hashlib.sha256(data).hexdigest())==data
    assert not (tmp_path.parent/"unrelated.txt").exists()


def test_reject_hash_and_missing(tmp_path):
    path=tmp_path/"input.zip"
    with zipfile.ZipFile(path,"w") as archive:
        archive.writestr("frozen/adrian.glb",b"fixture")
    with pytest.raises(ValueError):read_asset(path,"frozen/adrian.glb","0"*64)
    with pytest.raises(ValueError):read_asset(path,"frozen/maya.glb","0"*64)
