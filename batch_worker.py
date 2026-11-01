"""Portable resume-safe local/authorized-host rendering. Never publish from this worker."""
from pathlib import Path
import hashlib,json,subprocess,sys
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    queue=Path(sys.argv[1]).resolve()
    root=Path(sys.argv[2]).resolve()
    rows=json.loads(queue.read_text())['jobs'];status=[]
    for job in rows:
        manifest=job.get('render_manifest')
        if not manifest:
            status.append({'id':job['id'],'state':'HOLD_MISSING_VERIFIED_MATERIAL'});continue
        p=(root/manifest).resolve()
        if not p.is_relative_to(root) or not p.is_file():
            status.append({'id':job['id'],'state':'HOLD_INVALID_MANIFEST'});continue
        m=json.loads(p.read_text())
        if m.get('rights_checked') is not True or m.get('visual_identity_checked') is not True:
            status.append({'id':job['id'],'state':'HOLD_RIGHTS_OR_IDENTITY'});continue
        out=root/'BlackSwan_Production'/m['id']/(m['id']+'.mp4')
        receipt=out.with_suffix('.cache.json')
        source_digest=hashlib.sha256(p.read_bytes()+(root/'BlackSwan_Production/render_short.py').read_bytes()).hexdigest()
        if m.get('voice'):
            voice=root/'BlackSwan_Production'/m['voice']
            if not voice.is_file():
                status.append({'id':job['id'],'state':'HOLD_MISSING_VOICE'});continue
            source_digest=hashlib.sha256((source_digest+digest(voice)).encode()).hexdigest()
        for s in m['shots']:
            asset=root/'BlackSwan_Production/assets'/(s['asset']+'.mp4')
            if not asset.is_file():break
            source_digest=hashlib.sha256((source_digest+digest(asset)).encode()).hexdigest()
        else:
            cached=json.loads(receipt.read_text()) if receipt.exists() else {}
            if not (out.exists() and cached.get('recipe')==source_digest and cached.get('sha256')==digest(out)):
                subprocess.run([sys.executable,str(root/'BlackSwan_Production/render_short.py'),str(p)],cwd=root,check=True)
                receipt.write_text(json.dumps({'recipe':source_digest,'sha256':digest(out)}))
            status.append({'id':job['id'],'state':'RENDERED_HOLD_FULL_AV_AND_YOUTUBE_CHECKS','file':str(out)});continue
        status.append({'id':job['id'],'state':'HOLD_MISSING_SOURCE'})
    (queue.parent/'batch_status.json').write_text(json.dumps(status,indent=2));print(json.dumps(status,indent=2))
if __name__=='__main__':main()
