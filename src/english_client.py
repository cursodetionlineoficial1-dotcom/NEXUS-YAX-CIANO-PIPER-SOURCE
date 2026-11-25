# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Comunica com Piper Joe em uma venv separada; sem rede nem altera Cadu."""
import json,os,subprocess
from pathlib import Path

HOME=Path(os.environ.get('LOCALAPPDATA',str(Path.home()/'AppData'/'Local')))/'YAX-Ciano-Piper-CADU'
EN_PY=HOME/'venv-ingles'/'Scripts'/'python.exe'
EN_MODEL=HOME/'vozes'/'en_US-joe-medium.onnx'
EN_CONFIG=HOME/'vozes'/'en_US-joe-medium.onnx.json'
WORKER=Path(__file__).with_name('voice_english_worker.py')

class EnglishClient:
    def __init__(self,outdir:Path):
        self.outdir=Path(outdir).resolve()
        self.process=None
        self._unavailable=False

    @property
    def files_ready(self)->bool:
        return all(p.is_file() for p in (EN_PY,EN_MODEL,EN_CONFIG,WORKER))

    def _start(self):
        if self._unavailable:raise RuntimeError('Motor americano indisponivel')
        if self.process and self.process.poll() is None:return
        if not self.files_ready:raise FileNotFoundError('Instale o pacote local en-US Joe')
        flags=getattr(subprocess,'CREATE_NO_WINDOW',0)
        self.process=subprocess.Popen([str(EN_PY),'-u',str(WORKER),str(EN_MODEL),str(EN_CONFIG),str(self.outdir)],
               stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,
               text=True,encoding='utf-8',bufsize=1,creationflags=flags)
        line=self.process.stdout.readline()
        try:data=json.loads(line)
        except ValueError:data={}
        if not data.get('ready'):
            self.close();self._unavailable=True
            raise RuntimeError('Motor americano nao inicializou (verifique versao Piper >= 1.5)')

    def generate(self,text:str,target:Path):
        self._start()
        p=self.process
        if not p or not p.stdin or not p.stdout:raise RuntimeError('Motor americano sem canal de comunicacao')
        p.stdin.write(json.dumps({'text':text},ensure_ascii=False)+'\n');p.stdin.flush()
        line=p.stdout.readline()
        try:answer=json.loads(line)
        except ValueError:answer={}
        if not answer.get('ok'):
            self.close();self._unavailable=True
            raise RuntimeError('Falha de geracao do motor en-US')
        generated=Path(answer.get('path','')).resolve()
        # O worker apenas retorna arquivos na pasta de audio controlada.
        if generated.parent!=self.outdir or not generated.name.startswith('english-') or generated.suffix.lower()!='.wav':
            raise RuntimeError('Arquivo retornado pelo motor en-US invalido')
        try:os.replace(generated,target)
        except Exception:
            try:generated.unlink(missing_ok=True)
            except OSError:pass
            raise

    def close(self):
        proc=self.process;self.process=None
        if proc is None:return
        try:
            if proc.poll() is None:
                proc.terminate();proc.wait(timeout=2)
        except Exception:
            try:proc.kill()
            except Exception:pass
        try:proc.stdin.close() if proc.stdin else None
        except Exception:pass
        try:proc.stdout.close() if proc.stdout else None
        except Exception:pass
