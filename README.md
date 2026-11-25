# NEXUS — YAX Ciano · Piper CADU · Fontes e licenças

Repositório público dedicado aos componentes de **síntese de voz Piper CADU** utilizados no aplicativo Windows YAX Ciano.

**Este repositório não contém o código-fonte integral do aplicativo comercial YAX**, o sistema de pagamentos ou o projeto privado da NEXUS STORE. O código-fonte do motor de voz e da integração será oferecido aqui em versão correspondente à distribuição.

## Licenças

- **Piper TTS 1.8.0:** GNU GPL v3 ou posterior.
- **eSpeak NG:** GNU GPL v3 ou posterior.
- **Cinco módulos Python próprios da integração:** a licença escolhida é **GPL-3.0-or-later**, aplicável aos direitos autorais detidos pelo titular:
  `voice_bridge.py`, `english_client.py`, `hybrid_audio.py`, `pronunciacao_estrangeiros.py` e `voice_english_worker.py`.
- **Outras dependências:** mantêm suas licenças originais, inclusive ONNX Runtime, NumPy, OpenSSL, Python e PyInstaller. Consulte [avisos de terceiros](THIRD_PARTY_NOTICES.md).
- O texto da GNU GPL v3 encontra-se em [LICENSE](LICENSE).

## Estado do código-fonte

**O repositório foi criado; os arquivos completos do código-fonte correspondente ainda não foram anexados.** Não interprete a existência desta página e da licença como cumprimento completo da obrigação de distribuição das fontes.

Quando os arquivos estiverem disponíveis, o acesso ao código-fonte será gratuito, inclusive para quem não comprar o YAX. O instalador comercial será disponibilizado separadamente na NEXUS STORE; os direitos dos componentes GPL serão preservados.

A distinção entre o motor Piper, que é GPL, e o aplicativo C# deve ser avaliada segundo o modo como os processos se comunicam. Este repositório **não afirma** que todos os componentes de terceiros ou que o aplicativo inteiro tenham a mesma licença.

Para acompanhar a composição e integridade das fontes, consulte [estado da distribuição](SOURCE_STATUS.md).

## Referências oficiais

- [GNU GPL v3](https://www.gnu.org/licenses/gpl-3.0.html)
- [GNU GPL — Perguntas frequentes](https://www.gnu.org/licenses/gpl-faq.html)
- [Piper TTS 1.8.0](https://pypi.org/project/piper-tts/1.8.0/)
- [Piper GPL — fontes oficiais](https://github.com/OHF-Voice/piper1-gpl)
- [eSpeak NG — fontes oficiais](https://github.com/espeak-ng/espeak-ng)
