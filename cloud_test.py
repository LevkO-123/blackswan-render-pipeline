from pathlib import Path
import hashlib,json,urllib.request,subprocess,time,sys,os
R=Path(__file__).parent
B=R/'BlackSwan_Production'
start=time.monotonic()
assets=B/'assets';assets.mkdir(parents=True,exist_ok=True)
sources=json.loads((R/'sources.json').read_text())
assert len(sources)==2
for s in sources:
 assert s['license']=='Pexels License' and s['reviewed_utc']
 p=assets/(s['id']+'.mp4')
 if not p.exists():
  req=urllib.request.Request(s['download'],headers={'User-Agent':'BlackSwan-render-integration/1.0'})
  with urllib.request.urlopen(req,timeout=90) as inp,p.open('wb') as out:
   while chunk:=inp.read(1024*1024):out.write(chunk)
 assert p.stat().st_size==s['bytes'], 'Source size changed; re-review required'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==s['sha256'], 'Source changed; re-review required'
download=time.monotonic()-start
subprocess.run([sys.executable,str(B/'render_short.py'),str(B/'cloud_test.json')],cwd=R,check=True,timeout=540)
out=B/'Cloud_Integration_Test'
qa=json.loads((out/'verification.json').read_text())
assert qa['decode']=='PASS' and not qa['black_events']
assert qa['duration_seconds']==8.4 and qa['resolution']==[1080,1920]
assert qa['bytes']<80*1024*1024
import imageio_ffmpeg
f=imageio_ffmpeg.get_ffmpeg_exe()
result=subprocess.run([f,'-hide_banner','-i',str(out/'Cloud_Integration_Test.mp4'),'-f','null','-'],capture_output=True,text=True,check=True)
assert 'Audio: aac' in result.stderr and 'Video: h264' in result.stderr
log=(out/'technical_qa.log').read_text()
assert 'silence_start:' not in log, 'Unexpected silence; review required'
qa.update(download_seconds=round(download,2),total_seconds=round(time.monotonic()-start,2),runner=os.getenv('RUNNER_NAME','local'),source_resolution=[2160,3840],upscaled=False,rights='Two hash-verified Pexels sources; original score',human_full_listening=False,publication_allowed=False,purpose='Software renderer integration test')
(out/'cloud_result.json').write_text(json.dumps(qa,indent=2))
print(json.dumps(qa,indent=2))
summary=os.getenv('GITHUB_STEP_SUMMARY')
if summary:Path(summary).write_text('# Black Swan integration test\n\n```json\n'+json.dumps(qa,indent=2)+'\n```\nNot a new episode. Full human listening pending. Standard public Ubuntu runner; no paid API.\n')
