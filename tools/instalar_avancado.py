#!/usr/bin/env python3
"""Assistente PT-BR: aplica apenas deltas locais, sem rede e sem alterar entradas.
Código próprio de Hugo (Huguera), MIT. Python 3.10+; GUI opcional com Tk.
"""
import argparse, hashlib, json, os, queue, shutil, struct, sys
import tempfile, threading, zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "instalador"
CHUNK = 4 * 1024 * 1024

def sha(data):
    return hashlib.sha256(data).hexdigest()

def file_digest(path, mask=()):
    h = hashlib.sha256(); crc = 0
    with path.open('rb') as f:
        offset = 0
        while chunk := f.read(CHUNK):
            chunk = bytearray(chunk)
            for start, length in mask:
                a, b = max(start, offset), min(start + length, offset + len(chunk))
                if a < b:
                    chunk[a-offset:b-offset] = bytes(b-a)
            h.update(chunk); crc = zlib.crc32(chunk, crc)
            offset += len(chunk)
    return h.hexdigest(), crc

def file_hash(path, mask=()):
    return file_digest(path, mask)[0]

def read_number(data, pos):
    value = 0; shift = 1
    for _ in range(10):
        if pos >= len(data) - 12:
            raise ValueError('Número BPS truncado.')
        b = data[pos]; pos += 1; value += (b & 127) * shift
        if b & 128: return value, pos
        shift <<= 7; value += shift
    raise ValueError('Número BPS inválido.')

def load_delta(name):
    data = (ROOT / name).read_bytes()
    if len(data) < 16 or data[:4] != b'BPS1' or zlib.crc32(data[:-4]) != struct.unpack_from('<I', data, len(data)-4)[0]:
        raise ValueError('Patch BPS inválido ou corrompido.')
    source_size, pos = read_number(data, 4)
    target_size, pos = read_number(data, pos)
    meta_size, pos = read_number(data, pos)
    if pos + meta_size > len(data) - 12:
        raise ValueError('Metadados BPS truncados.')
    d = json.loads(data[pos:pos+meta_size]); pos += meta_size
    if d['format'] != 'BPS1-LINEAR-SHA256' or d['source_size'] != source_size or d['target_size'] != target_size:
        raise ValueError('Metadados BPS incompatíveis.')
    d['_source_crc'], d['_target_crc'] = struct.unpack_from('<II', data, len(data)-12)
    writes = []; cursor = 0
    while pos < len(data)-12:
        instruction, pos = read_number(data, pos)
        action = instruction & 3; length = (instruction >> 2) + 1
        if cursor + length > target_size:
            raise ValueError('Comando BPS excede a saída.')
        if action == 0:
            if cursor + length > source_size:
                raise ValueError('BPS lê além da origem.')
        elif action == 1:
            if pos + length > len(data)-12:
                raise ValueError('Literal BPS truncado.')
            writes.append((cursor, data[pos:pos+length])); pos += length
        else:
            raise ValueError('Este assistente aceita apenas o perfil linear SourceRead/TargetRead do BPS.')
        cursor += length
    if pos != len(data)-12 or cursor != target_size:
        raise ValueError('Tamanho final BPS divergente.')
    for start, size in d.get('mask', []):
        if not any(off <= start and off + len(blob) >= start + size for off, blob in writes):
            raise ValueError('Normalização BPS fora da região substituída.')
    d['_writes'] = writes
    return d

def check_source(path, d):
    if path.stat().st_size != d['source_size']:
        raise ValueError(f'{path.name}: tamanho incompatível com a região e a revisão exigidas.')
    digest, crc = file_digest(path, d.get('mask', []))
    if digest != d['source_sha256'] or crc != d['_source_crc']:
        raise ValueError(f'{path.name}: arquivo incompatível. Use a região e a versão indicadas, sem outra tradução. Seus arquivos não foram alterados.')

def changes(d):
    yield from d['_writes']

def delta_bytes(source, d):
    if len(source) != d['source_size'] or sha(source) != d['source_sha256'] or zlib.crc32(source) != d['_source_crc']:
        raise ValueError('Texto original incompatível com este patch.')
    out = bytearray(source[:d['target_size']])
    out.extend(bytes(max(0, d['target_size'] - len(out))))
    for offset, data in changes(d):
        out[offset:offset+len(data)] = data
    if sha(out) != d['target_sha256'] or zlib.crc32(out) != d['_target_crc']:
        raise ValueError('A conferência do texto gerado falhou.')
    return bytes(out)

def delta_file(source, dest, d):
    shutil.copyfile(source, dest)
    with dest.open('r+b') as f:
        f.truncate(d['target_size'])
        for offset, data in changes(d):
            f.seek(offset); f.write(data)
    digest, crc = file_digest(dest)
    if digest != d['target_sha256'] or crc != d['_target_crc']:
        raise ValueError(f'A conferência SHA-256 falhou: {dest.name}. Não instale este resultado.')

def read_lns(stream, record):
    offset, size, packed, flag = record
    stream.seek(offset)
    if not flag:
        out = stream.read(size)
    else:
        end = offset + packed
        out = bytearray()
        while len(out) < size:
            if stream.tell()+4 > end:
                raise ValueError('Arquivo LNS5 truncado.')
            header = stream.read(4)
            n = struct.unpack('>I', header)[0]
            amount = n & 0x7fff
            if not amount or stream.tell()+amount > end:
                raise ValueError('Bloco LNS5 inválido.')
            block = stream.read(amount)
            out.extend(zlib.decompress(block) if n & 0x8000 else block)
            stream.seek((-stream.tell()) % 16, 1)
        out = bytes(out)
    if len(out) != size:
        raise ValueError('Tamanho do texto LNS5 inválido.')
    return out

def encode_lns(data):
    out = bytearray()
    for pos in range(0, len(data), 0x4000):
        block = zlib.compress(data[pos:pos+0x4000], 6)
        out.extend(struct.pack('>I', 0x8000 | len(block)))
        out.extend(block); out.extend(bytes((-len(out)) % 16))
    return bytes(out)

def verify_package():
    checksums = ROOT / 'SHA256SUMS.txt'
    if not checksums.is_file():
        raise ValueError('SHA256SUMS.txt ausente. Extraia o ZIP inteiro novamente.')
    for line in checksums.read_text(encoding='utf-8').splitlines():
        expected, relative = line.split('  ', 1)
        path = (ROOT / relative).resolve()
        if not path.is_relative_to(ROOT.resolve()) or not path.is_file() or file_hash(path) != expected:
            raise ValueError('Pacote incompleto ou corrompido: ' + relative + '. Baixe e extraia novamente.')

def generate(inputs, output, progress=print):
    verify_package()
    manifest = json.loads((ROOT / 'manifesto.json').read_text(encoding='utf-8'))
    if len(inputs) != len(manifest['inputs']):
        raise ValueError('Selecione todos os arquivos solicitados.')
    inputs = [Path(p).expanduser().resolve(strict=True) for p in inputs]
    output = Path(output).expanduser().resolve()
    if output.exists():
        raise ValueError('A pasta de saída já existe. Escolha um nome novo para não substituir arquivos.')
    if not output.parent.is_dir():
        raise ValueError('A pasta onde salvar não existe.')
    if any(not p.is_file() for p in inputs):
        raise ValueError('Selecione arquivos, não pastas.')
    if any(output == p or output in p.parents for p in inputs):
        raise ValueError('A saída deve ficar separada dos arquivos de entrada.')
    expected_space = manifest['space_bytes']
    if shutil.disk_usage(output.parent).free < expected_space:
        raise ValueError('Espaço insuficiente na unidade de destino. Consulte o guia.')
    progress('Conferindo arquivos. Em jogos grandes isso pode levar alguns minutos…')
    deltas = {}
    for index, spec in enumerate(manifest['inputs']):
        if spec.get('delta'):
            d = load_delta(spec['delta']); check_source(inputs[index], d)
            deltas[index] = d
    translated = []
    if manifest['mode'] == 'fatal-frame':
        spec = manifest['archive']
        with inputs[0].open('rb') as f:
            head = f.read(32 + spec['entries'] * 32)
            if inputs[0].stat().st_size != spec['source_size'] or sha(head) != spec['table_sha256']:
                raise ValueError('archive00.lnk incompatível. É necessária a cópia EUR original, sem traduções anteriores. Não basta renomear uma pasta.')
            for item in spec['texts']:
                record = struct.unpack_from('>QQQQ', head, 32 + item['index'] * 32)
                data = read_lns(f, record)
                translated.append((item, delta_bytes(data, load_delta(item['delta']))))
    stage = Path(tempfile.mkdtemp(prefix='.ptbr-', dir=output.parent))
    try:
        progress('Gerando uma cópia traduzida. Aguarde a mensagem de conclusão…')
        report = {'game': manifest['game'], 'release': manifest['release'], 'inputs': [], 'outputs': [], 'console_test': 'Não executado pelo assistente; faça o teste no Wii U.'}
        for index, spec in enumerate(manifest['inputs']):
            report['inputs'].append({'name': inputs[index].name, 'size': inputs[index].stat().st_size, 'validation': 'SHA-256 dos recursos MSBT e tabela LNS5' if index not in deltas else 'SHA-256 normalizado' if deltas[index].get('mask') else 'SHA-256 integral'})
            if index in deltas:
                dest = stage / spec['destination']; dest.parent.mkdir(parents=True, exist_ok=True)
                delta_file(inputs[index], dest, deltas[index])
                report['outputs'].append({'path': spec['destination'], 'size': dest.stat().st_size, 'sha256': file_hash(dest)})
        if manifest['mode'] == 'fatal-frame':
            dest = stage / manifest['archive']['destination']
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(inputs[0], dest)
            with dest.open('r+b') as f:
                cursor = manifest['archive']['source_size']
                for item, data in translated:
                    cursor += (-cursor) % 0x800
                    packed = encode_lns(data)
                    f.seek(cursor); f.write(packed)
                    f.seek(32 + item['index'] * 32)
                    f.write(struct.pack('>QQQQ', cursor, len(data), len(packed), 1))
                    cursor += len(packed)
                end = cursor + (-cursor) % 0x800
                f.seek(16); f.write(struct.pack('>Q', end)); f.truncate(end)
            with dest.open('rb') as f:
                head = f.read(32 + manifest['archive']['entries'] * 32)
                for item, data in translated:
                    rec = struct.unpack_from('>QQQQ', head, 32 + item['index'] * 32)
                    if read_lns(f, rec) != data:
                        raise ValueError('A reextração dos textos gerados falhou.')
            report['outputs'].append({'path': manifest['archive']['destination'], 'size': dest.stat().st_size, 'sha256': file_hash(dest), 'translated_texts_rechecked': len(translated)})
        report['status'] = 'Arquivos gerados e conferidos. A instalação no console ainda não foi realizada.'
        (stage / 'RELATORIO.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
        shutil.copyfile(ROOT / 'COMO_INSTALAR.md', stage / 'COMO_INSTALAR.md')
        if (ROOT / 'COMO_INSTALAR.html').is_file():
            shutil.copyfile(ROOT / 'COMO_INSTALAR.html', stage / 'COMO_INSTALAR.html')
        if output.exists():
            raise ValueError('A saída foi criada por outro processo. Escolha outro nome.')
        stage.rename(output)
    except BaseException:
        shutil.rmtree(stage, ignore_errors=True)
        raise
    progress(f'Concluído! Pasta criada: {output}\nAgora siga COMO_INSTALAR.md. A pasta wiiu deve ir para a raiz do SD.')
    return report

def gui():
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox
    except ImportError:
        print('Este Python não tem a janela gráfica (Tk). Instale o Python 3.12 ou mais recente de https://www.python.org/downloads/ com Tcl/Tk, ou use o modo de terminal do guia.'); return 1
    m = json.loads((ROOT / 'manifesto.json').read_text(encoding='utf-8'))
    app = tk.Tk(); app.title('Huguera — Gerar tradução PT-BR'); app.geometry('760x480')
    tk.Label(app, text=m['game'], font=('', 16, 'bold'), wraplength=720).pack(pady=14)
    tk.Label(app, text='Selecione os arquivos da SUA cópia do jogo. Os originais serão preservados.\nO assistente gera os arquivos; a instalação no Wii U vem depois.', wraplength=720).pack(pady=6)
    values = []
    for spec in m['inputs']:
        var = tk.StringVar(); values.append(var)
        frame = tk.Frame(app); frame.pack(fill='x', padx=15, pady=5)
        tk.Label(frame, text=spec['label'], anchor='w').pack(fill='x')
        tk.Entry(frame, textvariable=var).pack(side='left', expand=True, fill='x')
        tk.Button(frame, text='Selecionar arquivo…', command=lambda v=var: v.set(filedialog.askopenfilename() or v.get())).pack(side='right')
    target = tk.StringVar()
    def choose():
        parent = filedialog.askdirectory(title='Escolha onde criar a NOVA pasta SAIDA_PTBR')
        if parent: target.set(str(Path(parent) / 'SAIDA_PTBR'))
    frame = tk.Frame(app); frame.pack(fill='x', padx=15, pady=10)
    tk.Entry(frame, textvariable=target).pack(side='left', fill='x', expand=True)
    tk.Button(frame, text='Onde salvar…', command=choose).pack(side='right')
    status = tk.StringVar(value='Aguardando seleção dos arquivos.'); messages = queue.Queue()
    tk.Label(app, textvariable=status, wraplength=720, justify='left').pack(padx=15, pady=12)
    def start():
        if any(not v.get() for v in values) or not target.get():
            messagebox.showerror('Falta selecionar', 'Selecione todos os arquivos e onde salvar.'); return
        selected = [v.get() for v in values]; dest = target.get(); button.config(state='disabled')
        def worker():
            try:
                generate(selected, dest, lambda msg: messages.put(('progress', msg)))
                messages.put(('done', 'Arquivos conferidos! Abra COMO_INSTALAR.md na pasta de saída para continuar.'))
            except Exception as e: messages.put(('error', str(e)))
        threading.Thread(target=worker, daemon=True).start()
    button = tk.Button(app, text='GERAR PASTA PT-BR', command=start); button.pack(pady=5)
    def poll():
        while not messages.empty():
            kind, msg = messages.get(); status.set(msg)
            if kind in ('done', 'error'):
                button.config(state='normal')
                (messagebox.showinfo if kind == 'done' else messagebox.showerror)('Tradução PT-BR', msg)
        app.after(150, poll)
    app.protocol('WM_DELETE_WINDOW', lambda: app.destroy() if button['state'] != 'disabled' or messagebox.askyesno('Cancelar?', 'A geração está em andamento. Fechar pode deixar uma pasta temporária incompleta. Deseja fechar?') else None)
    poll(); app.mainloop(); return 0

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entrada', action='append', type=Path, help='Repita na ordem mostrada no guia.')
    p.add_argument('--saida', type=Path, help='Pasta nova no computador; nunca escreva sobre os originais.')
    args = p.parse_args()
    if args.entrada is None and args.saida is None: return gui()
    if not args.entrada or not args.saida: p.error('Use --entrada para cada arquivo e --saida para uma pasta nova.')
    try: generate(args.entrada, args.saida)
    except (OSError, ValueError, KeyError, struct.error, zlib.error) as e:
        print('ERRO:', e, file=sys.stderr); return 1
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
