# Validação da distribuição v1.1 — 27/10/2026

Esta revisão corrige a distribuição e as instruções, preservando a tradução existente. Os pacotes públicos contêm BPS no perfil linear SourceRead/TargetRead, metadados SHA-256, assistente próprio e documentação.

## Verificações realizadas

- Integridade dos ZIPs e de todos os arquivos em SHA256SUMS.txt.
- Recusa de origem incompatível, arquivo alterado e saída já existente.
- Geração em cópias, conferência SHA-256 e CRC-32 BPS dos recursos gerados.
- NFS: dois BNDLs originais locais; comparação com o mod do SD.
- Deus Ex: prefixo original preservado da parte .024 e .000 de referência, com registro de 16 bytes normalizado. Saídas comparadas com os dois bigfiles do mod correto do SD.
- Fatal Frame: tabela original do backup, corpo original retido no archive local e 120 MSBTs originais conferidos individualmente. Os 120 textos foram reextraídos após reconstruir o archive e comparados com a revisão do SD. RPX gerado igual à revisão local conferida anteriormente por download de retorno do console.
- Site: busca, caminhos dos guias e botões de download conferidos no navegador.

## Limites desses testes

Os testes de reconstrução foram feitos no Mac pelo modo de terminal. A abertura gráfica foi bloqueada pelo ambiente de automação; o atalho Windows não foi executado em um Windows real. A interface requer Python com Tcl/Tk, e o modo de terminal está documentado.

Não foi feito novo teste de jogabilidade no Wii U nesta revisão de embalagem. Os testes antigos em console são históricos. Não houve novo dump integral independente de Deus Ex e Fatal Frame: foram usados os bytes originais preservados nos materiais locais, com as limitações acima. A aceitação de outras revisões/atualizações/DLC não é anunciada.

## Normalização específica de Deus Ex

O delta BPS da parte .000 usa uma entrada canônica em que somente o registro substituído de 16 bytes no offset 0xF48C8 vale zero. O assistente calcula SHA-256 e CRC-32 com essa mesma normalização, verifica todos os outros bytes do arquivo e sobrescreve integralmente esse registro. A saída tem SHA-256 e CRC-32 exatos da referência do mod. Por isso esse BPS deve ser aplicado pelo assistente incluído; um aplicador genérico que não normalize a entrada recusará o arquivo. A parte .024 exige tamanho e hash integral exatos do prefixo original, e recebe apenas o apêndice de tradução.

No Fatal Frame, o archive é identificado pelo tamanho e hash da tabela original, e cada um dos 120 MSBTs de entrada e saída tem hashes e CRCs BPS próprios. O conteúdo não editado é copiado da origem; o hash integral do archive resultante é registrado no relatório local, não usado como prova de uma nova validação de todo o jogo. O RPX tem hash integral exato de entrada e saída.
