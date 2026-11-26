import hashlib,json,tempfile,unittest
from pathlib import Path
from codecity.graphics import optional_texture

class FakeLoader:
    def __init__(self,fail):self.fail=fail;self.calls=[]
    def loadTexture(self,path):
        self.calls.append(path)
        if self.fail:raise OSError("Could not load texture")
        return object()

def fixture(root,name="soil-normal.png"):
    p=Path(root)/name;p.write_bytes(b"\x89PNG\r\n\x1a\nfixture")
    (Path(root)/"material-integrity.json").write_text(json.dumps({name:hashlib.sha256(p.read_bytes()).hexdigest()}))
    return p

class GraphicsTests(unittest.TestCase):
    def test_native_filename_conversion(self):
        with tempfile.TemporaryDirectory(prefix="BloomLogic spaces ") as d:
            p=fixture(d);loader=FakeLoader(False);log=[]
            self.assertIsNotNone(optional_texture(loader,d,[p.name],log.append,lambda p:("converted",p)))
            self.assertEqual(loader.calls,[("converted",str(p.resolve()))])
    def test_decoder_failure_is_optional(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(d);loader=FakeLoader(True);log=[]
            self.assertIsNone(optional_texture(loader,d,[p.name],log.append,str))
            self.assertEqual(len(loader.calls),1);self.assertIn("disabled",log[-1])
    def test_corruption_never_reaches_native_decoder(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(d);p.write_bytes(b"corrupt");loader=FakeLoader(False);log=[]
            self.assertIsNone(optional_texture(loader,d,[p.name],log.append,str))
            self.assertEqual(loader.calls,[]);self.assertTrue(any("integrity rejected" in x for x in log))
    def test_missing_never_reaches_native_decoder(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(d);p.unlink();loader=FakeLoader(False)
            self.assertIsNone(optional_texture(loader,d,[p.name],lambda _:None,str));self.assertEqual(loader.calls,[])
    def test_jpeg_never_reaches_native_decoder(self):
        with tempfile.TemporaryDirectory() as d:
            p=fixture(d,"soil-nor_gl.jpg");loader=FakeLoader(False)
            self.assertIsNone(optional_texture(loader,d,[p.name],lambda _:None,str));self.assertEqual(loader.calls,[])
