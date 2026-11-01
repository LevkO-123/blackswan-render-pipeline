from pathlib import Path
import sys,json,subprocess,hashlib,math,wave,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime/python'))
import numpy as np
import imageio_ffmpeg
def butter(order,freq,**kw):return(freq,kw.get('btype'))
def sosfilt(spec,x):
 freq,kind=spec
 def lp(f):
  n=max(2,round(48000/f));return np.convolve(x,np.ones(n)/n,mode='same')
 if kind=='highpass':return x-lp(freq)
 return lp(freq[1])-lp(freq[0])
BASE=Path(__file__).parent
FF=imageio_ffmpeg.get_ffmpeg_exe()
def ff(args,**kw):
 return subprocess.run([FF,'-hide_banner','-y']+list(map(str,args)),check=True,cwd=ROOT,**kw)
def wav(path,a,sr=48000):
 a=np.clip(a,-.99,.99)
 if a.ndim==1:a=np.column_stack([a,a])
 with wave.open(str(path),'wb') as w:
  w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes((a*32767).astype('<i2').tobytes())
def score(duration,path,bpm=100):
 sr=48000;n=round(duration*sr);t=np.arange(n)/sr
 rng=np.random.default_rng(817);mix=np.zeros((n,2));beat=60/bpm
 def add(start,a,gain=1,pan=0):
  i=round(start*sr)
  if i>=n:return
  if i<0:a=a[-i:];i=0
  a=a[:n-i]*gain
  if a.ndim==1:
   mix[i:i+len(a),0]+=a*math.sqrt((1-pan)/2)
   mix[i:i+len(a),1]+=a*math.sqrt((1+pan)/2)
  else:mix[i:i+len(a)]+=a
 # Soft evolving pads; new chord every four bars, not a sampled tune.
 for bar in range(math.ceil(duration/(beat*4))):
  chord=([146.832,174.614,220,261.626] if (bar//4)%2==0 else [116.541,146.832,174.614,220])
  tt=np.arange(round(beat*4.8*sr))/sr
  env=np.minimum(1,tt/.65)*np.minimum(1,np.maximum(0,(beat*4.8-tt)/1))
  layer=np.zeros((len(tt),2))
  for j,f in enumerate(chord):
   layer[:,0]+=np.sin(2*np.pi*f*tt+.1*j)*env*.013
   layer[:,1]+=np.sin(2*np.pi*f*1.0012*tt+.1*j)*env*.013
  add(bar*4*beat,layer)
 for k in range(math.ceil(duration/beat)):
  at=k*beat
  # Four-on-floor pulse; one short breakdown.
  if not (12<=at<14.4):
   tt=np.arange(round(.44*sr))/sr
   phase=2*np.pi*(44*tt+(116-44)*.023*(1-np.exp(-tt/.023)))
   kick=np.sin(phase)*np.exp(-tt*11)*.42
   click=sosfilt(butter(2,3500,fs=sr,btype='highpass',output='sos'),rng.normal(size=len(tt)))*np.exp(-tt*160)*.025
   add(at,kick+click)
  if k%4 in (1,3):
   tt=np.arange(round(.16*sr))/sr
   sn=sosfilt(butter(2,[1100,6500],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(tt)))
   add(at,sn*np.exp(-tt*31),.07)
  for off in [.5,.75]:
   tt=np.arange(round(.075*sr))/sr
   hat=sosfilt(butter(2,7000,fs=sr,btype='highpass',output='sos'),rng.normal(size=len(tt)))
   add(at+off*beat,hat*np.exp(-tt*85),.047 if off==.5 else .018,(-.28 if k%2 else .28))
  root=73.416 if (k//16)%2==0 else 58.270
  tt=np.arange(round(beat*.73*sr))/sr
  bass=(np.sin(2*np.pi*root*tt)+.16*np.sin(2*np.pi*root*2*tt))
  env=(1-np.exp(-tt*40))*np.exp(-tt*5)
  add(at+beat*.16,bass*env,.19)
  # Restrained pentatonic phrase with stereo echoes.
  notes=[293.665,440,523.251,440,349.228,293.665,261.626,220]
  f=notes[k%8];tt=np.arange(round(.8*sr))/sr
  p=(np.sin(2*np.pi*f*tt)+.23*np.sin(2*np.pi*f*2*tt))*np.exp(-tt*8)*(1-np.exp(-tt*100))
  add(at+.5*beat,p,.048,.18)
  add(at+1.25*beat,p,.019,-.42)
  add(at+2*beat,p,.009,.42)
 # Air transitions, no false car-engine audio.
 for at in [0,3.6,10.8,18]:
  tt=np.arange(round(.45*sr))/sr
  air=sosfilt(butter(2,[1200,5000],fs=sr,btype='bandpass',output='sos'),rng.normal(size=len(tt)))
  add(max(0,at-.28),air*np.sin(np.linspace(0,np.pi,len(tt)))**2,.042,-.1)
 fade=np.minimum(1,t/.025)*np.minimum(1,(duration-t)/.7)
 mix*=fade[:,None]
 wav(path,mix,sr)
def ass(path,captions,dur):
 def clk(t):
  c=round(t*100);return f'{c//360000}:{c//6000%60:02}:{c//100%60:02}.{c%100:02}'
 h="""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 2
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Main,DejaVu Sans,66,&H00F6F3ED,&H00F6F3ED,&H00202020,&H00000000,-1,0,0,0,100,100,3,0,1,2,1,8,90,120,290,1
Style: Small,DejaVu Sans,27,&H00C8C5BF,&H00C8C5BF,&H00202020,&H00000000,0,0,0,0,100,100,5,0,1,1,0,2,90,120,280,1
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
 for a,b,text in captions:h+=f'Dialogue: 1,{clk(a)},{clk(b)},Main,,0,0,0,,{{\\fad(100,120)}}{text}\n'
 # Brand belongs to original editorial, never a source watermark.
 h+=f'Dialogue: 0,{clk(dur-3)},{clk(dur)},Small,,0,0,0,,{{\\fad(250,150)}}BLACK SWAN\n'
 path.write_text(h,encoding='utf8')
def render(manifest):
 m=json.loads(Path(manifest).read_text(encoding='utf8'))
 assert m['rights_checked'] and m['visual_identity_checked']
 out=BASE/m['id'];out.mkdir(exist_ok=True)
 duration=sum(s['duration'] for s in m['shots'])
 score(duration,out/'original_score.wav',m.get('bpm',100))
 ass(out/'titles.ass',m['captions'],duration)
 args=[];filters=[]
 for i,s in enumerate(m['shots']):
  src=BASE/'assets'/f"{s['asset']}.mp4"
  args+=['-threads',1,'-ss',s['in'],'-t',s['duration']+.2,'-i',src]
  # No source intermediate encode. All original streams decoded once into final graph.
  filters.append(f'[{i}:v]scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920:(iw-1080)*{s.get('x',.5)}:(ih-1920)*.5,setsar=1,setpts=PTS-STARTPTS,fps=30:start_time=0,tpad=stop_mode=clone:stop_duration=0.1,trim=duration={s["duration"]},setpts=PTS-STARTPTS[v{i}]')
 labels=''.join(f'[v{i}]' for i in range(len(m['shots'])))
 filters.append(labels+f'concat=n={len(m["shots"])}:v=1:a=0,ass=BlackSwan_Production/{m["id"]}/titles.ass[v]')
 audio_map=f'{len(m["shots"])}:a:0'
 soundtrack=out/'original_score.wav'
 if m.get('voice'):
  soundtrack=out/'voice_music_mix.wav'
  ff(['-loglevel','error','-i',out/'original_score.wav','-i',BASE/m['voice'],'-filter_complex','[0:a]volume=0.12[bed];[1:a][bed]amix=inputs=2:duration=longest:normalize=0[a]','-map','[a]','-c:a','pcm_f32le',soundtrack],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 args+=['-i',soundtrack]
 args+=['-filter_complex_threads',1,'-filter_complex',';'.join(filters),'-map','[v]','-map',audio_map,'-af','loudnorm=I=-14:TP=-1.5:LRA=8','-c:v','libx264','-threads',4,'-preset','fast','-crf',17,'-c:a','aac','-b:a','256k','-ar',48000,'-ac',2,'-pix_fmt','yuv420p','-color_primaries','bt709','-color_trc','bt709','-colorspace','bt709','-movflags','+faststart','-t',duration,out/(m['id']+'.mp4')]
 with (out/'render.log').open('w') as log:ff(args,stdout=log,stderr=log)
 dst=out/(m['id']+'.mp4')
 # Decode every frame and inspect black/silence; intentional final audio fade is documented.
 qa=ff(['-i',dst,'-vf','blackdetect=d=0.08:pix_th=0.04:pic_th=0.98','-af','ebur128=peak=true,silencedetect=n=-55dB:d=0.5','-f','null','-'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 (out/'technical_qa.log').write_text(qa.stderr,encoding='utf8')
 report={'decode':'PASS','duration_seconds':duration,'resolution':[1080,1920],'fps':30,'source_encode_generations':0,'final_encode_generations':1,'audio':'original synthesized music and transition accents; no third-party samples or fake engine recordings','black_events':re.findall(r'black_start:\S+ black_end:\S+ black_duration:\S+',qa.stderr),'sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'bytes':dst.stat().st_size,'editorial_review':'PENDING','uploaded_to_youtube':False}
 (out/'verification.json').write_text(json.dumps(report,indent=2))
 ff(['-loglevel','error','-i',dst,'-vf','fps=2,scale=270:480','-q:v',3,out/'review_%03d.jpg'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 ff(['-loglevel','error','-i',dst,'-vn','-ar',16000,'-ac',1,out/'review_audio.wav'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 print(json.dumps(report),flush=True)
if __name__=='__main__':render(sys.argv[1])
