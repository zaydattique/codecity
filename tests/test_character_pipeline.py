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
        if '\\' in name:
            z.writestr('a/b','fixture')
        else:
            z.writestr(name,'fixture')
    if '\\' in name:
        # Windows ZipInfo normalizes backslashes when constructing a member.
        # Inject a raw malformed member name into both same-length ZIP headers.
        data=archive.read_bytes()
        assert data.count(b'a/b')==2
        archive.write_bytes(data.replace(b'a/b',b'a\\b'))
    with zipfile.ZipFile(archive) as z:
        assert [e.orig_filename for e in z.infolist()]==[name]
    with pytest.raises(ValueError): extract_pack(archive,tmp_path/'out')


def test_adult_profile_morphs():
    for id in ('adrian', 'maya'):
        profile = load_profile(id)
        assert profile['age'] >= 18
        assert 0.5 <= profile['candidate']['age'] <= 0.65
        assert profile['candidate']['shoes']
