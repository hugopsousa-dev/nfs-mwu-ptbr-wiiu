#!/usr/bin/env python3
"""
nfs_lang.py — leitor/escritor das tabelas de texto (LocalisedText) dos
bundles Criterion "bnd2" do Need for Speed: Most Wanted U (Wii U, big-endian).

Formato (descoberto por engenharia reversa):
  Arquivo .BNDL = container "bnd2" big-endian:
    0x00  magic 'bnd2'
    0x08  debugDataOffset      (= fim dos dados de recurso = inicio do tail XML)
    0x0c  resourceEntriesCount (=1)
    0x10  resourceEntriesOffset(=0x70)
    0x14  resourceDataOffset[0](=0xB8, inicio do lump comprimido)
    0x18/0x1c/0x20  resourceDataOffset[1..3] (= debugDataOffset)
    0x24  flags (bit0 = zlib comprimido)
    0x70  resource entry:
            0x70 uint64 resourceId
            0x78 uncompressedSizeAndAlignment[0]  (size = v & 0x0FFFFFFF, align = 1<<(v>>28))
            0x88 sizeAndAlignmentOnDisk[1]        (tamanho comprimido)
    0xB8  lump zlib (78 da ...)
    tail  XML <ResourceStringTable> ... </> (debug, preservado)

  Recurso descomprimido (LocalisedText):
    0x00 uint32 version (=1)
    0x04 uint32 numStrings
    0x08 uint32 idTableOffset   (=0x10)
    0x0c uint32 offTableOffset
    idTable : numStrings * uint32  (hash ID, ordenado)
    offTable: numStrings * (uint32 offsetAbsoluto, uint32 lengthEmChars_incluindo_null)
    strData : strings UTF-16BE terminadas em 0x0000
"""
import struct, zlib

def be32(b, o): return struct.unpack_from(">I", b, o)[0]

def read_bundle_strings(path):
    """Retorna (header_bytes, meta, entries) onde entries = lista de (id, str) na ORDEM original."""
    data = open(path, "rb").read()
    assert data[:4] == b"bnd2", "nao e bnd2: " + path
    dataOff = be32(data, 0x14)
    flags   = be32(data, 0x24)
    debugOff= be32(data, 0x08)
    lump = data[dataOff:debugOff]
    dec = zlib.decompress(lump) if (flags & 1) else lump
    tail = data[debugOff:]

    ver   = be32(dec, 0x00)
    n     = be32(dec, 0x04)
    idOff = be32(dec, 0x08)
    otOff = be32(dec, 0x0c)
    entries = []
    for i in range(n):
        sid = be32(dec, idOff + 4*i)
        off = be32(dec, otOff + 8*i)
        ln  = be32(dec, otOff + 8*i + 4)   # chars incl. null
        s   = dec[off: off + (ln-1)*2].decode("utf-16-be", "replace")
        entries.append((sid, s))
    meta = dict(ver=ver, n=n, idOff=idOff, otOff=otOff,
                header=data[:dataOff], tail=tail, flags=flags, dataOff=dataOff)
    return meta, entries

def build_decompressed(meta, entries):
    """Reconstroi o recurso descomprimido a partir de entries=(id,str)."""
    ver, idOff = meta["ver"], meta["idOff"]
    n = len(entries)
    otOff = idOff + 4*n
    strStart = otOff + 8*n

    blob = bytearray()
    offsets = []
    for sid, s in entries:
        offsets.append(strStart + len(blob))
        enc = s.encode("utf-16-be") + b"\x00\x00"
        blob += enc

    out = bytearray()
    out += struct.pack(">IIII", ver, n, idOff, otOff)
    for sid, s in entries:
        out += struct.pack(">I", sid)
    for (sid, s), off in zip(entries, offsets):
        ln = len(s) + 1  # chars incl. null
        out += struct.pack(">II", off, ln)
    assert len(out) == strStart
    out += blob
    return bytes(out)

def write_bundle(meta, entries, out_path):
    """Gera um .BNDL bnd2 valido com as strings de entries."""
    dec = build_decompressed(meta, entries)
    comp = zlib.compress(dec, 9)
    header = bytearray(meta["header"])     # ate dataOff (0xB8)
    dataOff = meta["dataOff"]
    debugOff = dataOff + len(comp)
    # patch campos de tamanho/offset
    struct.pack_into(">I", header, 0x08, debugOff)
    struct.pack_into(">I", header, 0x18, debugOff)
    struct.pack_into(">I", header, 0x1c, debugOff)
    struct.pack_into(">I", header, 0x20, debugOff)
    struct.pack_into(">I", header, 0x78, (4 << 28) | len(dec))   # uncompressed, align 1<<4
    struct.pack_into(">I", header, 0x88, len(comp))              # compressed on disk
    data = bytes(header) + comp + meta["tail"]
    open(out_path, "wb").write(data)
    return len(data)

if __name__ == "__main__":
    import sys
    meta, entries = read_bundle_strings(sys.argv[1])
    print("n=%d ver=%d" % (len(entries), meta["ver"]))
    for sid, s in entries[:5]:
        print("  %08x  %r" % (sid, s[:60]))
