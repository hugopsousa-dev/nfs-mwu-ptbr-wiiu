#!/usr/bin/env python3
"""
translate_gpt.py — traduz EN->PT-BR as strings do NFS Most Wanted U usando a
API da OpenAI (GPT), PRESERVANDO tags {..} e glifos de botao (PUA) byte a byte.

A chave NUNCA fica no arquivo. Leia do ambiente:

    export OPENAI_API_KEY="sk-..."          # sua chave
    source ~/dxhr_venv/bin/activate
    cd "/Users/teste/Desktop/Nintendo Wii U/nfs-mwu"
    python3 tools/translate_gpt.py work_en_pilot.json work_pt_pilot.json

- RESUMIVEL: salva checkpoint a cada batch; se parar, rode de novo.
- Cache de strings repetidas -> menos chamadas e menor custo.
- Protege {tags}, glifos PUA e chars de controle com placeholders ⟦N⟧.
- Modelo padrao: gpt-4o-mini (barato e bom p/ traducao). Mude com OPENAI_MODEL.
"""
import sys, os, json, re, time

MODEL      = os.environ.get("OPENAI_MODEL", "gpt-4o")
BATCH      = int(os.environ.get("BATCH", "20"))   # strings por chamada
CKPT_EVERY = int(os.environ.get("CKPT_EVERY", "1"))  # checkpoints a cada N batches

# Tokens a proteger: {..} (tags), qualquer char PUA (glifos de botao), e controles
PROTECT = re.compile(r'(\{[^{}]*\}|[-]|[\x00-\x1f])')
SENT    = re.compile(r'⟦(\d+)⟧')  # ⟦N⟧

def protect(s):
    """Substitui tokens protegidos por ⟦N⟧; retorna (template, tokens)."""
    tokens = []
    def repl(m):
        tokens.append(m.group(0))
        return "⟦%d⟧" % (len(tokens) - 1)
    return PROTECT.sub(repl, s), tokens

def restore(t, tokens):
    """Recoloca os tokens originais nos placeholders ⟦N⟧."""
    def repl(m):
        i = int(m.group(1))
        return tokens[i] if 0 <= i < len(tokens) else m.group(0)
    return SENT.sub(repl, t)

def is_translatable(s):
    # se, tirando os placeholders, nao sobra letra, nao traduz
    core = SENT.sub("", s)
    return bool(re.search(r'[A-Za-z]', core))

SYS = (
    "Voce e um tradutor profissional de localizacao de jogos. "
    "Traduza de ingles para portugues do Brasil (pt-BR) os textos de UI de um "
    "jogo de corrida (Need for Speed). Mantenha o tom de jogo, curto e natural. "
    "REGRAS ABSOLUTAS:\n"
    "1. NUNCA altere, traduza, remova ou reordene os marcadores no formato ⟦N⟧ "
    "(ex.: ⟦0⟧, ⟦1⟧). Copie-os EXATAMENTE como aparecem, na mesma posicao logica.\n"
    "2. Preserve a CAIXA do original: se o texto fonte estiver TODO EM MAIUSCULAS, "
    "a traducao tambem deve ficar em maiusculas.\n"
    "3. Nao adicione aspas, comentarios ou texto extra. Responda SOMENTE com o JSON pedido.\n"
    "4. Termos de menu/sistema de NFS podem ficar como no original quando for o padrao "
    "do mercado (ex.: 'Autolog', 'Most Wanted', nomes de carros e marcas)."
)

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    rows = json.load(open(inp, encoding="utf-8"))

    if not os.environ.get("OPENAI_API_KEY"):
        sys.exit("ERRO: defina OPENAI_API_KEY no ambiente (export OPENAI_API_KEY=...).")

    from openai import OpenAI
    client = OpenAI()

    # resume
    done = {}
    if os.path.exists(outp):
        for r in json.load(open(outp, encoding="utf-8")):
            if r.get("pt") is not None:
                done[r["i"]] = r["pt"]
        print("resumindo: %d ja traduzidas" % len(done))

    cache = {}  # template_en -> template_pt

    def gpt_translate(templates):
        """Traduz lista de templates (com ⟦N⟧). Retorna lista pt na mesma ordem."""
        need = [t for t in templates if t not in cache]
        uniq = list(dict.fromkeys(need))
        for k in range(0, len(uniq), BATCH):
            chunk = uniq[k:k+BATCH]
            payload = {str(j): chunk[j] for j in range(len(chunk))}
            user = ("Traduza os valores deste JSON para pt-BR seguindo as regras. "
                    "Responda com um JSON com as MESMAS chaves e os valores traduzidos.\n"
                    + json.dumps(payload, ensure_ascii=False))
            for attempt in range(5):
                try:
                    resp = client.chat.completions.create(
                        model=MODEL,
                        temperature=0.2,
                        response_format={"type": "json_object"},
                        messages=[{"role": "system", "content": SYS},
                                  {"role": "user", "content": user}],
                    )
                    out = json.loads(resp.choices[0].message.content)
                    for j, src in enumerate(chunk):
                        res = out.get(str(j), src)
                        if not isinstance(res, str):
                            res = src
                        cache[src] = res
                    break
                except Exception as e:
                    wait = 2 ** attempt
                    print("  retry (%s) em %ds: %s" % (attempt+1, wait, str(e)[:120]))
                    time.sleep(wait)
            else:
                for src in chunk:
                    cache[src] = src  # fallback: deixa original
        return [cache[t] for t in templates]

    t0 = time.time()
    # monta lista de itens a traduzir
    pending = [r for r in rows if r["i"] not in done]
    # pre-protege
    prot = {}
    for r in pending:
        tpl, toks = protect(r["en"])
        prot[r["i"]] = (tpl, toks, is_translatable(tpl))

    n_batches = 0
    buf = []  # (row, tpl, toks)
    def flush():
        nonlocal n_batches
        if not buf: return
        tpls = [b[1] for b in buf]
        res = gpt_translate(tpls)
        for (r, tpl, toks), rp in zip([(b[0], b[1], b[2]) for b in buf], res):
            # caixa alta
            core = SENT.sub("", r["en"]).strip()
            if core and core.isupper():
                rp = rp.upper()
            r["pt"] = restore(rp, toks)
        buf.clear()
        n_batches += 1
        if n_batches % CKPT_EVERY == 0:
            json.dump(rows, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            spd = sum(1 for r in rows if r.get("pt") is not None)
            print("  ckpt: %d/%d traduzidas  (%.1fs)  cache=%d"
                  % (spd, len(rows), time.time()-t0, len(cache)))

    for r in rows:
        if r["i"] in done:
            r["pt"] = done[r["i"]]
            continue
        tpl, toks, transl = prot[r["i"]]
        if not transl:
            r["pt"] = restore(tpl, toks)  # so tags/numeros -> mantem
            continue
        buf.append((r, tpl, toks))
        if len(buf) >= BATCH:
            flush()
    flush()

    json.dump(rows, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    done_n = sum(1 for r in rows if r.get("pt") is not None)
    print("OK -> %s  (%d/%d strings, %.1fs)" % (outp, done_n, len(rows), time.time()-t0))

if __name__ == "__main__":
    main()
