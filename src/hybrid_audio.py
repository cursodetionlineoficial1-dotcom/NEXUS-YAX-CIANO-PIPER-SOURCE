# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""YAX Ciano V19.14 - segmentador local de voz bilingue.

Le nomes de uma lista explicita, ordena por comprimento e alterna o motor
CADU/pt-BR com o motor en-US. Nunca muda texto exibido, nao envia nada a rede.
Se o motor americano nao existir ou falhar, a fala INTEIRA volta ao CADU.
"""
from __future__ import annotations
import io
import json
import os
import re
import uuid
import wave
from pathlib import Path

_PADRAO = Path(__file__).with_name('dicionario_hibrido.json')
_PESSOAL = (Path(os.environ.get('LOCALAPPDATA', str(Path.home()/'AppData'/'Local')))
            / 'YAX-Ciano-Piper-CADU' / 'dicionario_hibrido_pessoal.json')
_MAX_BYTES=100_000
_MAX_NAMES=200
_MAX_CHUNKS=16


def caminho_personalizado()->Path:
    return _PESSOAL


def carregar_entradas()->list[dict]:
    """Dicionario pessoal tem precedencia; arquivo invalido nao desliga padrao."""
    for p in (_PESSOAL, _PADRAO):
        try:
            if not p.is_file() or p.stat().st_size>_MAX_BYTES: continue
            obj=json.loads(p.read_text(encoding='utf-8-sig'))
            raw=obj['entradas']
            if not isinstance(raw,list) or len(raw)>_MAX_NAMES: continue
            result=[];seen=set()
            for e in raw:
                if not isinstance(e,dict): continue
                nome=e.get('nome');ativo=e.get('ativo', False);idioma=e.get('idioma','en-US')
                if not (isinstance(nome,str) and 2<=len(nome.strip())<=90 and
                        isinstance(ativo,bool) and idioma=='en-US' and
                        not any(x in nome for x in '\r\n\t')):continue
                name=nome.strip()
                if name.casefold() in seen:continue
                seen.add(name.casefold())
                result.append({'nome':name,'ativo':ativo,'idioma':'en-US'})
            return result
        except (ValueError,OSError,TypeError,KeyError,UnicodeError):
            continue
    return []


def criar_pessoal()->Path:
    import shutil
    if not _PESSOAL.exists():
        _PESSOAL.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(_PADRAO, _PESSOAL)
    return _PESSOAL


def _term_regex(name:str)->str:
    return r'(?<!\w)' + r'\s+'.join(re.escape(word) for word in name.split()) + r'(?!\w)'


def dividir_texto(texto:str, entradas:list[dict]|None=None)->list[tuple[str,str]]:
    if not isinstance(texto,str): raise TypeError('Texto nao e uma string')
    if entradas is None: entradas=carregar_entradas()
    names=sorted({e['nome'] for e in entradas if e.get('ativo') and e.get('idioma')=='en-US'},key=len,reverse=True)
    if not names:return [('pt-BR',texto)]
    regex=re.compile('|'.join(_term_regex(n) for n in names), re.IGNORECASE)
    raw=[];pos=0
    for m in regex.finditer(texto):
        if m.start()>pos:raw.append(('pt-BR',texto[pos:m.start()]))
        raw.append(('en-US',texto[m.start():m.end()]))
        pos=m.end()
    if pos<len(texto):raw.append(('pt-BR',texto[pos:]))
    if not raw: return [('pt-BR',texto)]
    # Trechos de espacos/pontuacao nunca viram sintese portuguesa isolada.
    merged=[];pending=''
    for idioma,span in raw:
        if idioma=='pt-BR' and not any(ch.isalnum() for ch in span):
            if merged:
                lg,lt=merged[-1];merged[-1]=(lg,lt+span)
            else:pending+=span
            continue
        span=pending+span;pending=''
        if merged and merged[-1][0]==idioma:
            lg,lt=merged[-1];merged[-1]=(lg,lt+span)
        else: merged.append((idioma,span))
    if pending:
        if merged:merged[-1]=(merged[-1][0],merged[-1][1]+pending)
        else:merged=[('pt-BR',pending)]
    assert ''.join(span for _,span in merged)==texto
    return merged


def _read_wav(path:Path)->tuple[tuple[int,int,int],bytes]:
    with wave.open(str(path),'rb') as w:
        fmt=(w.getnchannels(),w.getsampwidth(),w.getframerate())
        pcm=w.readframes(w.getnframes())
    if fmt[0]!=1 or fmt[1]!=2 or not pcm or len(pcm)>20_000_000:
        raise ValueError('Formato WAV incompativel ou ausente')
    return fmt,pcm


def _write_wav(path:Path,fmt:tuple[int,int,int],blocks:list[bytes]):
    with wave.open(str(path),'wb') as w:
        w.setnchannels(fmt[0]);w.setsampwidth(fmt[1]);w.setframerate(fmt[2])
        for block in blocks:w.writeframesraw(block)


def _cadu_segmento(cadu,texto:str,path:Path):
    with wave.open(str(path),'wb') as w:
        cadu.synthesize_wav(texto,w)


def sintetizar(texto:str,cadu,ingles,saida:Path,entradas:list[dict]|None=None)->dict:
    """Escreve WAV final; 'ingles' recebe (texto,path) e produz WAV em path.

    Metodo atomico: nenhum audio parcial e enviado ao usuario.
    """
    if not isinstance(texto,str) or not 1<=len(texto.strip())<=3800:
        raise ValueError('Texto invalido')
    from pronunciacao_estrangeiros import preparar_texto_para_cadu
    chunks=dividir_texto(texto,entradas)
    temp=[];outfmt=None;blocks=[];fallback=None
    try:
        if ingles is None or not any(lang=='en-US' for lang,_ in chunks):
            chunks=[('pt-BR',texto)]
            fallback='sem_voz_ingles' if ingles is None else None
        elif len(chunks)>_MAX_CHUNKS:
            chunks=[('pt-BR',texto)];fallback='muitos_trechos'
        if len(chunks)==1 and chunks[0][0]=='pt-BR':
            _cadu_segmento(cadu,preparar_texto_para_cadu(texto),saida)
            return {'hibrida':False,'trechos':1,'motivo':fallback}
        anterior=None
        for i,(lang,part) in enumerate(chunks):
            tmp=saida.parent/('chunk-'+uuid.uuid4().hex+'.wav')
            temp.append(tmp)
            if lang=='en-US':
                ingles(part.strip(),tmp)
            else:
                # No hibrido, a narrativa permanece exatamente como o texto original.
                _cadu_segmento(cadu,part.strip(),tmp)
            fmt,pcm=_read_wav(tmp)
            if outfmt is not None and fmt!=outfmt:
                raise ValueError('Taxas/formato PCM distintos: nao e seguro concatenar')
            outfmt=fmt
            if anterior and anterior!=lang:
                blocks.append(b'\x00\x00' * int(fmt[2]*.025)) # respiro de 25 ms
            blocks.append(pcm)
            anterior=lang
        _write_wav(saida,outfmt,blocks)
        return {'hibrida':True,'trechos':len(chunks),'motivo':None}
    except Exception as exc:
        # Nao interromper a fala por erro da voz americana.
        try:saida.unlink(missing_ok=True)
        except OSError:pass
        _cadu_segmento(cadu,preparar_texto_para_cadu(texto),saida)
        return {'hibrida':False,'trechos':1,'motivo':'fallback:'+type(exc).__name__}
    finally:
        for p in temp:
            try:p.unlink(missing_ok=True)
            except OSError:pass
