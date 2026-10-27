# Need for Speed: Most Wanted U — instalação PT-BR v1.1

Região: **USA / NTSC-U**. Title ID: `0005000010128800`. Guia revisado em 27/10/2026.

A tradução usa o slot inglês. O glifo Õ maiúsculo continua limitado pela fonte; os créditos ficam no idioma original.

## 1. O que você vai baixar

Você pode abrir `COMO_INSTALAR.html` no navegador para ler este mesmo guia com formatação.

Este ZIP é um **gerador de tradução**. Ele não traz o jogo nem exige conta de IA, chave de API ou pagamento. Você fornece os arquivos da sua própria cópia e ele cria uma cópia traduzida. Nada é instalado automaticamente no console.

A pasta `patches` guarda apenas diferenças entre arquivos. **Não copie `patches` para o SD e não a renomeie para `sdcafiine`.** A pasta `wiiu` aparece depois de concluir o assistente.

## 2. Preparar o computador e o console

1. Tenha sua própria cópia do jogo extraída em pastas. Um dump é uma cópia dos arquivos do seu jogo, feita por você; o [Dumpling oficial](https://github.com/emiyl/dumpling) documenta essa extração. Este assistente usa os arquivos indicados abaixo, não aceita WUP/ISO/WUX diretamente.
2. Use **Python 3.10 ou mais recente**. Para quem quer usar as janelas, instale uma versão estável atual do [Python oficial](https://www.python.org/downloads/), com Tcl/Tk. No Windows, inclua o Python Launcher na instalação. Python do Homebrew pode não incluir Tk.
3. No Wii U, tenha **Aroma e SDCafiine instalado e ativado**. Não presuma que o SDCafiine acompanha toda instalação do Aroma. Veja o [SDCafiine oficial](https://github.com/wiiu-env/sdcafiine_plugin#installation-of-the-plugin).
4. Guarde uma cópia de segurança do SD antes de instalar ou atualizar mods. Não use arquivos que já receberam outra tradução como entrada.
5. Baixe o ZIP pelo botão do jogo no [site Huguera](https://hugopsousa-dev.github.io/). Extraia o ZIP inteiro: no Windows, clique com o botão direito e escolha **Extrair Tudo**; no Mac, dê dois cliques no ZIP. Não execute dentro da janela compactada.

## 3. Abrir o assistente

**No Windows:** dê dois cliques em `INICIAR_WINDOWS.cmd`. Se aparecer “Python não encontrado”, instale o Python com o Launcher e abra novamente.

**No Mac:** dê dois cliques em `INICIAR_MAC.command`. Se o macOS não permitir abrir ou o ZIP perder a permissão de execução, abra o Terminal, digite `python3 ` (com um espaço), arraste `instalar.py` para a janela e pressione Enter. Se o Python não tiver Tk, use o Python oficial ou o modo de terminal descrito mais abaixo. Você não precisa desativar as proteções do Mac.

Na janela:

1. Clique em **Selecionar arquivo…** em cada campo e escolha os arquivos listados na próxima seção. Arquivos com o mesmo nome podem ficar em subpastas diferentes; confira o caminho.
2. Clique em **Onde salvar…** e escolha uma pasta do computador com espaço livre. O assistente criará dentro dela uma NOVA pasta chamada `SAIDA_PTBR`. Para refazer, use outro local ou renomeie a saída anterior.
3. Clique em **GERAR PASTA PT-BR**. Aguarde; arquivos grandes podem levar vários minutos. Não feche a janela durante a geração.
4. Só prossiga quando aparecer a conclusão. Se surgir erro de incompatibilidade, os originais continuam preservados. Use a região e a revisão exigidas; renomear arquivos ou pastas não resolve uma versão diferente.

## 4. Arquivos que este jogo exige

Selecione nesta ordem:

- `content/UI/LANGUAGE/0001.BNDL`
- `content/UI/LANGUAGE/1690132/0001.BNDL` (arquivo da subpasta do manual)

Reserve pelo menos **10 MB livres**, além do espaço ocupado pelo seu dump. Não troque o Title ID para tentar usar outra região. Os arquivos são conferidos antes da geração.

### Alternativa pelo Terminal / PowerShell

Abra o terminal dentro da pasta extraída do pacote. Troque `SEU_DUMP` pelo caminho real da sua cópia, mantendo aspas em caminhos com espaços. No Windows, troque `python3` por `py -3`.

```sh
python3 instalar.py --entrada "SEU_DUMP/content/UI/LANGUAGE/0001.BNDL" --entrada "SEU_DUMP/content/UI/LANGUAGE/1690132/0001.BNDL" --saida "SAIDA_PTBR"
```

Se `SAIDA_PTBR` já existir, escolha outro nome. Não é necessário editar scripts, traduzir novamente nem contratar API.


## 5. Copiar a tradução para o cartão

1. Com o Wii U desligado, conecte o SD ao computador.
2. Abra `SAIDA_PTBR`. Dentro dela estará a pasta `wiiu`.
3. “Raiz do SD” é a primeira tela que aparece ao abrir o cartão, antes de entrar em qualquer pasta.
4. A meta é acrescentar o mod em `SD:/wiiu/sdcafiine/`. Não deixe `SD:/SAIDA_PTBR/wiiu/` nem `SD:/wiiu/wiiu/`.
5. Se `wiiu` e `sdcafiine` já existirem, **entre nelas e copie apenas a pasta do jogo/mod indicada abaixo**. Se o sistema oferecer juntar/mesclar pastas, pode usar essa opção. Se oferecer substituir a pasta `wiiu` inteira, cancele e copie a subpasta manualmente. Preserve os outros jogos e plugins.
6. Se o mesmo mod já estiver instalado, guarde sua pasta anterior no computador e coloque a nova pasta do mod no lugar. Não misture arquivos de revisões diferentes.
7. Ejete o SD pelo sistema antes de retirar. Recoloque no Wii U.


Confira o caminho final deste jogo:

- `SD:/wiiu/sdcafiine/0005000010128800/NFS-MWU-PTBR/content/UI/LANGUAGE/0001.BNDL`
- `SD:/wiiu/sdcafiine/0005000010128800/NFS-MWU-PTBR/content/UI/LANGUAGE/1690132/0001.BNDL`

## 6. Abrir no Wii U e desinstalar

1. Nas configurações do Wii U, deixe o idioma em **English / Inglês**. A tradução substitui os textos desse idioma.
2. Inicie o console pelo Aroma e abra o jogo da região indicada.
3. Se aparecer a seleção do SDCafiine, escolha **NFS-MWU-PTBR**. Confira os menus e os textos durante o jogo.
4. Para desinstalar, com o console desligado, retire somente a pasta `wiiu/sdcafiine/0005000010128800/NFS-MWU-PTBR` do SD. O jogo instalado permanece preservado.


## 7. Conferir e pedir ajuda

O arquivo `RELATORIO.json` na saída lista os hashes e os arquivos produzidos. “Arquivos gerados” confirma a reconstrução no computador; a conferência visual no seu console ainda precisa ser feita.

Se continuar em inglês: confirme a região/Title ID, o idioma inglês do console, o plugin ativado e o caminho sem `wiiu` duplicado. Se houver apenas um mod, o SDCafiine pode aplicá-lo sem mostrar menu. As configurações do plugin são acessíveis com **L + direcional para baixo + botão menos** no GamePad.

Se aparecer “arquivo incompatível”, não force o patch: envie a mensagem de erro, região, versão base/atualização e nome do arquivo em **Issues** do repositório. Não envie o jogo, chaves, licenças ou saves. Este pacote aceita apenas a revisão identificada em `manifesto.json`; não declara compatibilidade com toda atualização ou DLC.

## Créditos e referências

Tradução, pesquisa e testes anteriores em console: Hugo (Huguera). Esta revisão padroniza o instalador e a distribuição; não é uma nova tradução integral nem uma nova validação de toda a campanha. Limitações de tradução anteriores permanecem.

Código novo do assistente: licença MIT, em `LICENCA_ASSISTENTE.txt`. Deltas não concedem direitos sobre o jogo original. Não venda a tradução nem distribua os arquivos gerados junto com o jogo.

- [Canal Huguera](https://www.youtube.com/channel/UCJcKIDhtlBCZ_6YjnmoWXCQ)
- [Estrutura oficial de mods do SDCafiine](https://github.com/wiiu-env/sdcafiine_plugin#installation-of-the-mods)
- [FTPiiU para Aroma](https://github.com/wiiu-env/ftpiiu_plugin#usage-information-and-settings)
