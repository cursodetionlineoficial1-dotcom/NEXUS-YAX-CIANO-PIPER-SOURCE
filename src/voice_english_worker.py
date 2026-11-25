# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Worker em ingles americano: executa em venv-ingles INDEPENDENTE do CADU.

Recebe linha JSON e gera arquivos WAV offline; modelo Joe en-US local.
"""
import json,sys,uuid,wave,traceback
from pathlib import Path

def send(obj):print(json.dumps(obj,ensure_ascii=False),flush=True)

def main():
    if len(sys.argv)!=4:raise ValueError('Parametros esperados: modelo, json, pasta de saida')
    model,config,out=map(lambda s:Path(s).resolve(),sys.argv[1:])
    if model.name!='en_US-joe-medium.onnx' or config.name!='en_US-joe-medium.onnx.json':
        raise ValueError('Motor en-US inesperado')
    if not model.is_file() or not config.is_file():raise FileNotFoundError('Faltam arquivos da voz en-US Joe')
    out.mkdir(parents=True,exist_ok=True)
    from piper import PiperVoice
    engine=PiperVoice.load(str(model),config_path=str(config))
    send({'ready':True,'voice':'Joe','locale':'en-US'})
    for line in sys.stdin:
        wavfile=None
        try:
            req=json.loads(line)
            text=req.get('text')
            if not isinstance(text,str) or not 1<=len(text.strip())<=350:
                raise ValueError('Texto de nome estrangeiro invalido')
            wavfile=out/('english-'+uuid.uuid4().hex+'.wav')
            with wave.open(str(wavfile),'wb') as wav:
                engine.synthesize_wav(text,wav)
            with wave.open(str(wavfile),'rb') as w:
                if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getnframes()<150:
                    raise ValueError('WAV americano vazio ou incompativel')
            send({'ok':True,'path':str(wavfile)})
        except Exception as exc:
            if wavfile is not None:
                try:wavfile.unlink(missing_ok=True)
                except OSError:pass
            print(traceback.format_exc(limit=2),file=sys.stderr,flush=True)
            send({'ok':False,'error':type(exc).__name__})

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print(traceback.format_exc(limit=2),file=sys.stderr,flush=True)
        send({'ready':False,'error':type(exc).__name__})
