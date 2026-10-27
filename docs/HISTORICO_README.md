> Documento histórico. Para instalar a versão atual, siga [COMO_INSTALAR.md](../COMO_INSTALAR.md).

# Need for Speed: Most Wanted U — Tradução PT-BR (Wii U)

Tradução **não-oficial** para Português do Brasil de *Need for Speed: Most Wanted U*
(Wii U, região NTSC-U), feita por fã. Traduz menus, opções, manual do jogo, HUD,
mensagens e desafios.

> **Status:** primeira tradução PT-BR conhecida deste jogo para Wii U. 🇧🇷

## 📥 Como instalar (usuário final)

Baixe o pacote pronto na aba **[Releases](https://github.com/hugopsousa-dev/nfs-mwu-ptbr-wiiu/releases)** e siga o `LEIA-ME.txt`.
Resumo em 3 passos:

1. Copie a pasta `wiiu` do ZIP para a **raiz do cartão SD** (escolha *juntar/mesclar*).
2. Deixe o **idioma do console em Inglês** (a versão NTSC-U usa o inglês como base — é
   onde o PT-BR entra).
3. Abra o jogo pelo **Aroma** (o plugin **SDCafiine** já vem junto). Se aparecer o menu
   de modpacks, escolha `NFS-MWU-PTBR`.

Para desinstalar, apague do SD a pasta `wiiu/sdcafiine/0005000010128800/NFS-MWU-PTBR`.

## 🔧 Como foi feito (pipeline)

O jogo usa o formato de bundles **Criterion "bnd2"** (big-endian, recursos comprimidos
com zlib), bem diferente de outros jogos. O processo:

1. **Dump** dos arquivos do jogo com o **Dumpling** (homebrew Wii U).
2. **Engenharia reversa** do formato `bnd2` e da tabela `LocalisedText`
   (cabeçalho big-endian, tabela de IDs/offsets, strings UTF-16BE).
3. **Extração** das ~12 mil strings de `UI/LANGUAGE/0001.BNDL` (+ manual em
   `1690132/0001.BNDL`) para JSON.
4. **Tradução** EN→PT-BR com proteção de *tags* `{...}` e glifos de botão (PUA):
   cada token é trocado por um marcador antes de traduzir e recolocado byte a byte
   depois, garantindo que nada de controle do jogo se quebre.
5. **Reempacotamento** do bundle (recompressão zlib + reescrita dos offsets do
   cabeçalho) e validação de round-trip.
6. **Distribuição** via **SDCafiine** (substituição de arquivo por SD, sem alterar a
   instalação do jogo).

### Scripts (`tools/`)
- `nfs_lang.py` — leitor/escritor dos bundles `bnd2` / `LocalisedText`.
- `translate_gpt.py` — tradutor EN→PT-BR via API da OpenAI, com proteção de tags/glifos.
- `translate.py` — tradutor alternativo offline (NLLB).

## ⚠️ Notas

- Por limitação da fonte do jogo, o glifo **`Õ` (O com til) não existe**; nessas
  palavras o til é omitido (ex.: `CONFIGURAÇOES`). Os demais acentos funcionam.
- Os **créditos finais** permanecem no idioma original (nomes próprios, licenças e
  títulos de músicas não se traduzem).

## 📜 Legal

Tradução gratuita feita por fã, sem fins lucrativos. **Não** inclui nem distribui
arquivos do jogo (ROM/imagem) — apenas os textos traduzidos, aplicados por cima da sua
própria cópia. *Need for Speed* e *Most Wanted* são marcas da Electronic Arts /
Criterion; este projeto não é afiliado nem endossado por elas.

## 🙌 Créditos

Tradução e engenharia reversa: **Hugo (Huguera)**
Canal / novas traduções: <https://www.youtube.com/channel/UCJcKIDhtlBCZ_6YjnmoWXCQ>
