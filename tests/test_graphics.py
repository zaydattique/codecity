import tempfile,unittest
from pathlib import Path
from codecity.graphics import optional_texture

class FakeLoader:
    def __init__(self,fail):self.fail=fail;self.calls=[]
    def loadTexture(self,path):
        self.calls.append(path)
        if self.fail:raise OSError("Could not load texture")
        return object()

class GraphicsTests(unittest.TestCase):
    def test_native_filename_conversion(self):
        with tempfile.TemporaryDirectory(prefix="BloomLogic spaces ") as d:
            p=Path(d)/"soil-normal.png";p.write_bytes(b"test")
            loader=FakeLoader(False);log=[]
            tex=optional_texture(loader,d,[p.name],log.append,lambda p:("converted",p))
            self.assertIsNotNone(tex)
            self.assertEqual(loader.calls,[("converted",str(p.resolve()))])
    def test_failure_is_optional(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ("soil-normal.png","soil-nor_gl.jpg"):
                (Path(d)/name).write_bytes(b"invalid")
            loader=FakeLoader(True);log=[]
            self.assertIsNone(optional_texture(loader,d,["soil-normal.png","soil-nor_gl.jpg"],log.append,str))
            self.assertEqual(len(loader.calls),2)
            self.assertIn("disabled",log[-1])
    def test_missing_falls_through(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/"soil-nor_gl.jpg").write_bytes(b"test")
            loader=FakeLoader(False);log=[]
            self.assertIsNotNone(optional_texture(loader,d,["soil-normal.png","soil-nor_gl.jpg"],log.append,str))
            self.assertEqual(len(loader.calls),1)
