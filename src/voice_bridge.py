# SPDX-License-Identifier: GPL-3.0-or-later
"""JARVIS V3.1.7 — motor Piper CADU local, reutiliza os modelos instalados.

Protocolo de linha JSON pelo stdin/stdout, sem servidor HTTP, sem envio de texto a terceiros.
A única voz aceita está definida pelo modelo pt_BR-cadu-medium.onnx.
Nenhuma alteração em velocidade, pitch, normalização ou pós-processamento do áudio.
"""
import json
import re
import sys
import uuid
import wave
import traceback
from pathlib import Path



# O dicionario e a deteccao automatica atuam somente no texto do audio.
# A resposta visivel, o historico e a voz oficial CADU permanecem inalterados.
from pronunciacao_estrangeiros import preparar_texto_para_cadu
from english_client import EnglishClient
from hybrid_audio import sintetizar, dividir_texto

def reply(data):
    print(json.dumps(data, ensure_ascii=False), flush=True)


def main():
    if len(sys.argv) != 4:
        raise ValueError('Informe modelo, configuracao e pasta de audio.')
    model = Path(sys.argv[1]).resolve()
    config = Path(sys.argv[2]).resolve()
    output_dir = Path(sys.argv[3]).resolve()
    if not (model.is_file() and config.is_file()):
        raise FileNotFoundError('Arquivos locais da voz Piper CADU nao encontrados.')
    if model.name != 'pt_BR-cadu-medium.onnx' or config.name != 'pt_BR-cadu-medium.onnx.json':
        raise ValueError('O motor do JARVIS aceita somente a voz CADU oficial.')
    output_dir.mkdir(parents=True, exist_ok=True)
    from piper import PiperVoice
    engine = PiperVoice.load(str(model), config_path=str(config))
    english_client = EnglishClient(output_dir)
    reply({'ready': True, 'voice': 'CADU', 'provider': 'Piper local',
           'english_available': english_client.files_ready})
    for line in sys.stdin:
        output = None
        try:
            request = json.loads(line)
            text = request.get('text')
            if not isinstance(text, str) or not 1 <= len(text.strip()) <= 3800:
                raise ValueError('Texto invalido ou muito longo para sintese.')
            output = output_dir / ('jarvis-cadu-' + uuid.uuid4().hex + '.wav')
            resultado=sintetizar(text, engine, english_client.generate if english_client.files_ready else None, output)
            with wave.open(str(output), 'rb') as result:
                if result.getnframes() < 200 or result.getnchannels() != 1:
                    raise ValueError('Piper retornou audio incompleto.')
            reply({'ok': True, 'path': str(output), 'hybrid':resultado['hibrida'],
                   'segments':resultado['trechos'], 'voiceFallback':resultado['motivo']})
        except Exception as exc:
            if output is not None:
                try:
                    output.unlink(missing_ok=True)
                except Exception:
                    pass
            print(traceback.format_exc(limit=3), file=sys.stderr, flush=True)
            reply({'ok': False, 'error': str(exc)[:450]})


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        print(traceback.format_exc(limit=4), file=sys.stderr, flush=True)
        reply({'ready': False, 'error': str(exc)[:450]})
