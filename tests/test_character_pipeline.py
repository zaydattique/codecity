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


def test_npc_distinct_authored_profiles():
    from ai.npc_brain import IDS, PROFILES
    profiles=[load_profile(i) for i in IDS]
    assert all(p['name']==PROFILES[p['id']].name for p in profiles)
    assert len({p['candidate']['clothes'] for p in profiles})==6
    assert len({p['candidate']['hair'] for p in profiles})==6
    assert all(p['age']>=18 and .5<=p['candidate']['age']<=.65 for p in profiles)


def test_additional_civilian_candidates_are_distinct_adults():
    ids=('jules','rhea','vincent','farah','theo','iris')
    profiles=[load_profile(i) for i in ids]
    assert all(p['age']>=18 and .5<=p['candidate']['age']<=.65 for p in profiles)
    assert len({p['height_m'] for p in profiles})==len(ids)
    assert len({str(p['candidate']) for p in profiles})==len(ids)
    for p in profiles:
        assert abs(sum(p['candidate']['race'].values())-1)<1e-6


def test_thirty_distinct_adult_art_presets():
    import json
    from tools.build_character import ROOT
    data=json.loads((ROOT/'art/characters.json').read_text())
    assert len(data['npcs'])==30
    assert len({p['id'] for p in data['npcs']})==30
    assert len({json.dumps(p['candidate'],sort_keys=True) for p in data['npcs']})==30
    assert all(p['age']>=18 and .5<=p['candidate']['age']<=.65 for p in data['npcs'])
