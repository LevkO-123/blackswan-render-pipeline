import hashlib,tempfile,unittest
from pathlib import Path
from release_gate import problems
class ReleaseTests(unittest.TestCase):
 def setUp(self):
  (Path(__file__).parent/'tmp').mkdir(exist_ok=True)
  self.tmp=tempfile.TemporaryDirectory(dir=Path(__file__).parent/'tmp');self.p=Path(self.tmp.name)/'v.mp4';self.p.write_bytes(b'fixture');h=hashlib.sha256(self.p.read_bytes()).hexdigest()
  self.r={'publication_authorized':True,'technical':dict(sha256=h,decode_pass=True,no_black_defects=True,no_audio_defects=True,captions_pass=True),'editorial':dict(sha256=h,full_viewing=True,full_listening=True,story_pass=True,car_identity_pass=True,no_misleading_claims=True,reviewed_by='test fixture only',reviewed_at='2026-11-01'),'rights':dict(all_assets_cleared=True),'youtube':dict(privacy='private',copyright_checks='complete_no_issues',hd_complete=True,unresolved_claims=False,video_id='fixture-only')}
 def tearDown(self):self.tmp.cleanup()
 def test_complete_fixture(self):self.assertEqual(problems(self.r,self.p),[])
 def test_changed_export_requires_recheck(self):
  self.p.write_bytes(b'changed');self.assertIn('editorial_review_wrong_file',problems(self.r,self.p))
 def test_audio_review_not_optional(self):
  self.r['editorial']['full_listening']=False;self.assertIn('full_listening',problems(self.r,self.p))
 def test_pending_copyright_blocks(self):
  self.r['youtube']['copyright_checks']='pending';self.assertIn('copyright_not_clear',problems(self.r,self.p))
 def test_unresolved_claim_blocks(self):
  self.r['youtube']['unresolved_claims']=True;self.assertIn('claims_not_clear',problems(self.r,self.p))
 def test_engine_cannot_be_generic(self):
  self.r['requires_real_engine']=True;self.assertIn('real_engine_missing',problems(self.r,self.p))
 def test_hd_required(self):
  self.r['youtube']['hd_complete']=False;self.assertIn('hd_incomplete',problems(self.r,self.p))
if __name__=='__main__':unittest.main()
