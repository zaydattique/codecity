import zipfile
from pathlib import Path
import pytest
from tools.build_character import extract_pack, load_profile


def test_two_profiles():
    a,m=load_profile('adrian'),load_profile('maya')
    assert a['id']!=m['id'] and a['height_m']!=m['height_m']


def test_extract(tmp_path):
    archive=tmp_path/'pack.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr('skins/skin.txt','fixture')
    dest=tmp_path/'out'
    extract_pack(archive,dest)
    assert (dest/'skins/skin.txt').read_text()=='fixture'


@pytest.mark.parametrize('name',['../outside','/abs','a\\b','C:/abs'])
def test_reject_archive_path(tmp_path,name):
    archive=tmp_path/'pack.zip'
    with zipfile.ZipFile(archive,'w') as z:
        z.writestr(name,'fixture')
    with pytest.raises(ValueError): extract_pack(archive,tmp_path/'out')
