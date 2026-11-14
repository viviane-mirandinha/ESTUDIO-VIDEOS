import numpy as np, wave
sr=44100; dur=82; t=np.arange(int(sr*dur))/sr; out=np.zeros_like(t)
f=lambda n:440*2**((n-69)/12)
ch=[[45,60,64,67,72],[41,57,60,64,69],[48,64,67,71,76],[43,59,62,64,71]]
L=2.4; rng=np.random.default_rng(7)
for k in range(int(dur/L)+1):
    c=ch[k%4]; t0=k*L
    for j,n in enumerate(c):
        for hit in ([0,1.2] if j else [0]):
            s=int((t0+hit+0.012*j)*sr); m=min(len(t),s+int(sr*2.6))
            if s>=len(t): continue
            tt=np.arange(m-s)/sr; env=np.minimum(1,tt/0.015)*np.exp(-tt*(1.6 if j else 1.0))
            a=(0.22 if j==0 else 0.11)*(0.7 if hit else 1)
            out[s:m]+=a*env*(np.sin(2*np.pi*f(n)*tt)+0.25*np.sin(4*np.pi*f(n)*tt)*np.exp(-tt*4))
cr=(rng.random(len(t))<0.0004)*rng.normal(0,0.15,len(t)); out+=cr+rng.normal(0,0.004,len(t))
out*=np.minimum(1,t/2)*np.minimum(1,(dur-t)/3); out/=np.abs(out).max()*1.25
w=wave.open("musica_src.wav","wb");w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes((out*32767).astype(np.int16).tobytes());w.close()
