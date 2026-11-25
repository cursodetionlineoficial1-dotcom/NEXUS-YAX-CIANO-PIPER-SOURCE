# NEXUS — YAX Ciano · Piper CADU · Fontes e licenças

Repositório público dedicado aos componentes de **síntese de voz Piper CADU** utilizados no aplicativo Windows YAX Ciano.

**Este repositório não contém o código-fonte integral do aplicativo comercial YAX**, o sistema de pagamentos ou o projeto privado da NEXUS STORE. O repositório disponibiliza as fontes da integração Python e um pacote de fontes, scripts e avisos de terceiros para a versão Piper CADU da RC5.

## Licenças

- **Piper TTS 1.8.0:** GNU GPL v3 ou posterior.
- **eSpeak NG:** GNU GPL v3 ou posterior.
- **Cinco módulos Python próprios da integração:** a licença escolhida é **GPL-3.0-or-later**, aplicável aos direitos autorais detidos pelo titular:
  `voice_bridge.py`, `english_client.py`, `hybrid_audio.py`, `pronunciacao_estrangeiros.py` e `voice_english_worker.py`.
- **Outras dependências:** mantêm suas licenças originais, inclusive ONNX Runtime, NumPy, OpenSSL, Python e PyInstaller. Consulte [avisos de terceiros](THIRD_PARTY_NOTICES.md).
- O texto da GNU GPL v3 encontra-se em [LICENSE](LICENSE).

## Estado do código-fonte

**Publicado:** os cinco módulos Python sob GPL-3.0-or-later estão na pasta [src/](src/), e o arquivo ZIP com fontes upstream, scripts e avisos está na [release piper-cadu-source-v1.0](https://github.com/cursodetionlineoficial1-dotcom/NEXUS-YAX-CIANO-PIPER-SOURCE/releases/tag/piper-cadu-source-v1.0).

- [Baixar o ZIP GPL de fontes e avisos](https://github.com/cursodetionlineoficial1-dotcom/NEXUS-YAX-CIANO-PIPER-SOURCE/releases/download/piper-cadu-source-v1.0/NEXUS_YAX_CIANO_PIPER_CADU_GPL_SOURCE_v1.zip) — **74.291.857 bytes**.
- SHA-256: `f0ce8ef0bb1e4c9d5ff028f4de39c8e0d36913c723490dbca7200b29a24d49e9`.

O acesso ao pacote é público e não depende do pagamento ou do login na NEXUS STORE. A publicação não constitui, por si só, certificação jurídica de completude do Código-Fonte Correspondente da versão comercial. O instalador comercial é distribuído separadamente.

A distinção entre o motor Piper, que é GPL, e o aplicativo C# deve ser avaliada segundo o modo como os processos se comunicam. Este repositório **não afirma** que todos os componentes de terceiros ou que o aplicativo inteiro tenham a mesma licença.

As fontes próprias publicadas incluem `voice_bridge.py`, `english_client.py`, `hybrid_audio.py`, `pronunciacao_estrangeiros.py` e `voice_english_worker.py`, todos com cabeçalho SPDX GPL-3.0-or-later. Para acompanhar a composição e integridade das fontes, consulte [estado da distribuição](SOURCE_STATUS.md).

## Referências oficiais

- [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)
- [GNU GPL — Perguntas frequentes](https://www.gnu.org/licenses/gpl-faq.html)
- [Piper TTS 1.8.0](https://pypi.org/project/piper-tts/1.8.0/)
- [Piper GPL — fontes oficiais](https://github.com/OHF-Voice/piper1-gpl)
- [eSpeak NG — fontes oficiais](https://github.com/espeak-ng/espeak-ng)
