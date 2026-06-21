#!/usr/bin/env python3
"""
translate.py — traduz EN->PT-BR as strings do NFS Most Wanted U usando NLLB,
PRESERVANDO tags {..} e glifos de botão (PUA) byte a byte.

Rodar no Mac dentro do venv que ja tem torch+transformers (dxhr_venv):

    source ~/dxhr_venv/bin/activate      # ou o caminho do seu venv
    cd "/Users/teste/Desktop/Nintendo Wii U/nfs-mwu"
    python3 tools/translate.py work_en_0001.json work_pt_0001.json

- E RESUMIVEL: salva checkpoint a cada 200 strings; se parar, rode de novo.
- Usa cache de segmentos repetidos (muita string se repete) -> bem mais rapido.
- Modelo: facebook/nllb-200-distilled-600M (baixa na 1a vez se nao tiver cache).
"""
import sys, os, json, re, time

MODEL = os.environ.get("NLLB_MODEL", "facebook/nllb-200-distilled-600M")
SRC, TGT = "eng_Latn", "por_Latn"
CKPT_EVERY = 200

# Captura tags {..} (inclui aninhamento simples de aspas) e qualquer char PUA / controle
PROTECT = re.compile(r'(\{[^{}]*\}|[-]|[\x00-\x1f])')

def segments(s):
    """Divide em [(is_text, piece)] alternando texto e tokens protegidos."""
    out, last = [], 0
    for m in PROTECT.finditer(s):
        if m.start() > last:
            out.append((True, s[last:m.start()]))
        out.append((False, m.group(0)))
        last = m.end()
    if last < len(s):
        out.append((True, s[last:]))
    return out

def is_translatable(txt):
    return bool(re.search(r'[A-Za-z]', txt))

def main():
    inp, outp = sys.argv[1], sys.argv[2]
    rows = json.load(open(inp, encoding="utf-8"))

    # resume
    done = {}
    if os.path.exists(outp):
        for r in json.load(open(outp, encoding="utf-8")):
            if r.get("pt") is not None:
                done[r["i"]] = r["pt"]
        print("resumindo: %d ja traduzidas" % len(done))

    print("carregando modelo %s ..." % MODEL)
    import torch
    from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
    tok = AutoTokenizer.from_pretrained(MODEL, src_lang=SRC)
    model = AutoModelForSeq2SeqLM.from_pretrained(MODEL)
    model.eval()
    dev = "mps" if torch.backends.mps.is_available() else "cpu"
    model.to(dev)
    bos = tok.convert_tokens_to_ids(TGT)

    seg_cache = {}
    def tr_batch(texts):
        """traduz uma lista de textos puros (sem tags), com cache."""
        need = [t for t in texts if t not in seg_cache]
        uniq = list(dict.fromkeys(need))
        B = 16
        for k in range(0, len(uniq), B):
            chunk = uniq[k:k+B]
            enc = tok(chunk, return_tensors="pt", padding=True, truncation=True, max_length=256).to(dev)
            with torch.no_grad():
                gen = model.generate(**enc, forced_bos_token_id=bos, max_length=256, num_beams=2)
            dec = tok.batch_decode(gen, skip_special_tokens=True)
            for src, res in zip(chunk, dec):
                seg_cache[src] = res
        return [seg_cache[t] for t in texts]

    t0 = time.time()
    for idx, r in enumerate(rows):
        if r["i"] in done:
            r["pt"] = done[r["i"]]
            continue
        s = r["en"]
        segs = segments(s)
        # coleta textos traduziveis
        texts = [p for t, p in segs if t and is_translatable(p)]
        trans = tr_batch([p.strip() for p in texts]) if texts else []
        ti = 0
        rebuilt = []
        for t, p in segs:
            if t and is_translatable(p):
                res = trans[ti]; ti += 1
                # preserva espacos de borda e CAIXA ALTA do original
                lead = p[:len(p)-len(p.lstrip())]
                trail = p[len(p.rstrip()):]
                core = p.strip()
                if core.isupper():
                    res = res.upper()
                rebuilt.append(lead + res + trail)
            else:
                rebuilt.append(p)
        r["pt"] = "".join(rebuilt)

        if (idx+1) % CKPT_EVERY == 0:
            json.dump(rows, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
            spd = (idx+1)/(time.time()-t0)
            print("  %d/%d  (%.1f str/s)  cache=%d" % (idx+1, len(rows), spd, len(seg_cache)))

    json.dump(rows, open(outp, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("OK -> %s  (%d strings)" % (outp, len(rows)))

if __name__ == "__main__":
    main()
