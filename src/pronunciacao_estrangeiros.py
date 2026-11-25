# -*- coding: utf-8 -*-
# SPDX-License-Identifier: GPL-3.0-or-later
"""Motor local de reconhecimento e dicionario de nomes para a voz Piper CADU.

Somente o texto fornecido ao sintetizador e alterado. Nao grava conversas.
Nenhuma rede, nenhuma mudanca de voz, pitch, velocidade ou audio.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

_ORIGEM = Path(__file__).with_name('pronunciacoes.json')
_PESSOAL = (Path(os.environ.get('LOCALAPPDATA', str(Path.home() / 'AppData' / 'Local')))
           / 'YAX-Ciano-Piper-CADU' / 'pronunciacoes_personalizadas.json')
_MAX_BYTES = 256_000
_MAX_ENTRIES = 500
_MAX_OUTPUT = 3800
_AUTO_REGEX = re.compile(
    r'(?<![\w])(?:[A-ZÀ-Ý][a-zà-ÿ]{2,}(?:\s+[A-ZÀ-Ý][a-zà-ÿ]{2,}){1,2})(?![\w])', re.UNICODE)
_FALSE_POSITIVE = frozenset({'Meu Nome','O Nome','Seu Nome','A Voz','O Windows',
                             'Este Computador','Minha Conta','Boa Noite','Bom Dia'})


def caminho_dicionario_pessoal() -> Path:
    return _PESSOAL


def _ler_json(path: Path) -> dict:
    if path.stat().st_size > _MAX_BYTES:
        raise ValueError('O dicionario excede o limite permitido.')
    obj = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(obj, dict) or not isinstance(obj.get('entradas'), list):
        raise ValueError('O dicionario precisa conter uma lista entradas.')
    if len(obj['entradas']) > _MAX_ENTRIES:
        raise ValueError('O dicionario tem muitas entradas.')
    return obj


def _validar(entrada: object) -> dict | None:
    if not isinstance(entrada, dict):
        return None
    nome, fala, ativo = entrada.get('nome'), entrada.get('fala', ''), entrada.get('ativo', False)
    if not (isinstance(nome, str) and 1 <= len(nome.strip()) <= 90 and
            isinstance(fala, str) and len(fala) <= 160 and isinstance(ativo,bool)):
        return None
    if any(c in nome + fala for c in '\r\n\t'):
        return None
    nome=nome.strip()
    # Sem expressoes regulares fornecidas pelo usuario: os nomes sao LITERAIS.
    # Uma entrada ativa precisa ter uma representacao falada explicita.
    if ativo and not fala.strip():
        ativo=False
    return {'nome':nome, 'fala':fala.strip(), 'ativo':ativo,
            'idioma':str(entrada.get('idioma',''))[:20],
            'nota':str(entrada.get('nota',''))[:200]}


def carregar_dicionario() -> tuple[list[dict], str]:
    """Preferir o arquivo pessoal; se estiver invalido, usar o original do kit."""
    for path in (_PESSOAL, _ORIGEM):
        try:
            obj=_ler_json(path)
            entradas=[e for raw in obj['entradas'] if (e:=_validar(raw)) is not None]
            return entradas, str(path)
        except (OSError, ValueError, TypeError, UnicodeError, json.JSONDecodeError):
            continue
    return [], ''


def criar_dicionario_pessoal() -> Path:
    """Criar copia editavel somente a pedido, sem sobrescrever alteracoes."""
    if not _PESSOAL.exists():
        _PESSOAL.parent.mkdir(parents=True, exist_ok=True)
        obj = _ler_json(_ORIGEM)
        _PESSOAL.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return _PESSOAL


def _padrao(termo: str) -> str:
    # Um ou mais espacos em um termo do dicionario, incluindo quebras entre palavras.
    return r'(?<!\w)' + r'\s+'.join(re.escape(s) for s in termo.split()) + r'(?!\w)'


def reconhecer_nomes(texto: str, entradas: list[dict] | None = None) -> list[dict]:
    """Reconhece nomes do dicionario e candidatos; nunca os traduz nem registra o texto."""
    if entradas is None:
        entradas, _ = carregar_dicionario()
    if not isinstance(texto,str):return []
    reconhecidos=[]
    vistos=set()
    for ent in sorted(entradas,key=lambda e:len(e['nome']),reverse=True):
        if re.search(_padrao(ent['nome']), texto, flags=re.IGNORECASE):
            k=ent['nome'].casefold()
            if k not in vistos:
                reconhecidos.append({'nome':ent['nome'],'ativo':ent['ativo'],
                                     'tipo':'dicionario','idioma':ent['idioma']})
                vistos.add(k)
    for match in _AUTO_REGEX.finditer(texto):
        nome=match.group(0)
        if nome in _FALSE_POSITIVE or nome.casefold() in vistos:
            continue
        # Heuristica sugere revisao; nunca afirma origem estrangeira ou altera audio.
        reconhecidos.append({'nome':nome,'ativo':False,'tipo':'candidato','idioma':'indefinido'})
        vistos.add(nome.casefold())
    return reconhecidos


def preparar_texto_para_cadu(texto: str, entradas: list[dict] | None = None) -> str:
    """Aplica apenas substituicoes ATIVAS em correspondencias literais e completas.

    Unica passagem, priorizando frases longas: evita trocas em cascata e dentro de palavras.
    """
    if not isinstance(texto,str):raise TypeError('O texto precisa ser uma string.')
    if entradas is None:
        entradas, _=carregar_dicionario()
    ativos=[e for e in entradas if e.get('ativo') and e.get('fala') and e.get('nome')]
    if not ativos:return texto
    # Ordem do maior nome para o menor: Barry Allen antes de Barry.
    ativos.sort(key=lambda e:len(e['nome']),reverse=True)
    # Dedup por primeiro nome. Regex em unico passe -> nenhuma substituicao sobre a substituicao.
    nomes=[];dic={}
    for e in ativos:
        key=e['nome'].casefold()
        if key in dic:continue
        dic[key]=e['fala']
        nomes.append((key,e['nome']))
    chunks=[f'(?P<n{i}>{_padrao(nome)})' for i,(_,nome) in enumerate(nomes)]
    reg=re.compile('|'.join(chunks),flags=re.IGNORECASE)
    def troca(m):
        idx=int(m.lastgroup[1:])
        return dic[nomes[idx][0]]
    resultado=reg.sub(troca,texto)
    # Nao envia texto de tamanho superior ao limite existente do worker.
    return resultado if len(resultado)<=_MAX_OUTPUT else texto


def diagnosticar(texto: str) -> dict:
    entradas, origem=carregar_dicionario()
    return {'original':texto,'para_audio':preparar_texto_para_cadu(texto,entradas),
            'nomes':reconhecer_nomes(texto,entradas),'dicionario':origem}
