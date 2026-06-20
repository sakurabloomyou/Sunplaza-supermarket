#!/usr/bin/env python3
"""
Build a minimal vbaProject.bin (OLE2 CFB + MS-OVBA) from scratch in Python.
Injects it into intent_tool.xlsx to produce intent_tool.xlsm.

References:
  [MS-CFB]  https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb
  [MS-OVBA] https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-ovba
"""

import struct, io, zipfile, shutil, os

# ── MS-OVBA Compression ─────────────────────────────────────────────────────

def ovba_compress(data: bytes) -> bytes:
    """MS-OVBA Section 2.4 compression (all-literal tokens)."""
    out = io.BytesIO()
    out.write(b'\x01')          # SignatureByte

    pos = 0
    while pos < len(data):
        chunk = data[pos: pos + 4096]
        pos += 4096

        comp = io.BytesIO()
        i = 0
        while i < len(chunk):
            comp.write(b'\x00')             # flags: all literals
            comp.write(chunk[i: i + 8])
            i += 8
        comp_bytes = comp.getvalue()

        # bits 0-11 = CompressedChunkSize-3 = (data_size+2)-3 = data_size-1
        hdr = 0xB000 | (len(comp_bytes) - 1)
        out.write(struct.pack('<H', hdr))
        out.write(comp_bytes)

    return out.getvalue()


# ── dir stream builder ───────────────────────────────────────────────────────

def _rec(id_: int, data: bytes) -> bytes:
    return struct.pack('<HI', id_, len(data)) + data

def _module_record(name: str, source_offset: int, is_document: bool) -> bytes:
    """Build one MODULE record for the dir stream."""
    ansi    = name.encode('latin-1')
    unicode_ = name.encode('utf-16-le')
    out = io.BytesIO()
    out.write(_rec(0x0019, ansi))               # MODULENAME
    out.write(_rec(0x0047, unicode_))            # MODULENAMEUNICODE  (real id=0x0047)
    out.write(_rec(0x001A, ansi))               # MODULESTREAMNAME ANSI
    out.write(_rec(0x0032, unicode_))            # MODULESTREAMNAME Unicode
    out.write(_rec(0x001C, b''))                 # MODULEDOCSTRING ANSI
    out.write(_rec(0x0048, b''))                 # MODULEDOCSTRING Unicode
    out.write(_rec(0x0031, struct.pack('<I', source_offset)))  # MODULEOFFSET
    out.write(_rec(0x001E, struct.pack('<I', 0)))               # MODULEHELPCONTEXT
    out.write(_rec(0x002C, struct.pack('<H', 0xFFFF)))          # MODULECOOKIE
    mod_type = 0x0022 if is_document else 0x0021
    out.write(_rec(mod_type, b''))               # MODULETYPE
    out.write(_rec(0x002B, b''))                 # MODULETERM
    return out.getvalue()

def build_dir_stream(modules: list) -> bytes:
    """
    modules: list of (name, source_offset, is_document)
    Returns uncompressed dir stream bytes.
    """
    out = io.BytesIO()

    # Project properties
    out.write(_rec(0x0001, struct.pack('<I', 0x00000001)))   # PROJECTSYSKIND Win32
    out.write(_rec(0x0002, struct.pack('<I', 0x0409)))        # PROJECTLCID
    out.write(_rec(0x0014, struct.pack('<I', 0x0409)))        # PROJECTLCIDINVOKE
    out.write(_rec(0x0003, struct.pack('<H', 1252)))          # PROJECTCODEPAGE
    out.write(_rec(0x0004, b'VBAProject'))                    # PROJECTNAME
    out.write(_rec(0x0005, b''))                              # PROJECTDOCSTRING ANSI
    out.write(_rec(0x0040, b''))                              # PROJECTDOCSTRING Unicode
    out.write(_rec(0x0006, b''))                              # PROJECTHELPFILEPATH 1
    out.write(_rec(0x003D, b''))                              # PROJECTHELPFILEPATH 2
    out.write(_rec(0x0007, struct.pack('<I', 0)))             # PROJECTHELPCONTEXT
    out.write(_rec(0x0008, struct.pack('<I', 0)))             # PROJECTLIBFLAGS
    # PROJECTVERSION: no Id2 field in actual stream (oletools confirmed)
    out.write(struct.pack('<HI', 0x0009, 4))
    out.write(struct.pack('<I', 0x61440000))    # MajorVersion
    out.write(struct.pack('<H', 0))             # MinorVersion
    out.write(_rec(0x000C, b''))                              # PROJECTCONSTANTS ANSI
    out.write(_rec(0x003C, b''))                              # PROJECTCONSTANTS Unicode

    # PROJECTMODULES
    out.write(struct.pack('<HI', 0x000F, 4))
    out.write(struct.pack('<I', len(modules)))
    out.write(struct.pack('<HH', 0x0013, 2))
    out.write(struct.pack('<H', 0xFFFF))

    for (name, offset, is_doc) in modules:
        out.write(_module_record(name, offset, is_doc))

    return out.getvalue()


# ── VBA source code ──────────────────────────────────────────────────────────

VBA_CODE_THISWORKBOOK = """\
Private Sub Workbook_SheetChange(ByVal Sh As Object, ByVal Target As Range)
    If Sh.Index <> 1 Or Target.Address <> "$H$10" Then Exit Sub
    Dim r As Long
    Application.ScreenUpdating = False
    For r = 16 To 49
        Sh.Rows(r).Hidden = True
    Next r
    For r = 51 To 57
        Sh.Rows(r).Hidden = True
    Next r
    Select Case Left(Target.Value, 1)
        Case Chr(9312), Chr(9313)
            For r = 16 To 49
                Sh.Rows(r).Hidden = False
            Next r
        Case Chr(9314)
            For r = 51 To 57
                Sh.Rows(r).Hidden = False
            Next r
    End Select
    Application.ScreenUpdating = True
End Sub
"""

VBA_CODE_SHEET1 = ""  # empty – document module binding for Sheet1


# ── Assemble all streams ─────────────────────────────────────────────────────

def make_streams() -> dict:
    s_sheet1 = ovba_compress(VBA_CODE_SHEET1.encode('latin-1'))
    s_twb    = ovba_compress(VBA_CODE_THISWORKBOOK.encode('latin-1'))

    modules = [
        ('ThisWorkbook', 0, True),
        ('Sheet1',       0, True),
    ]
    dir_unc = build_dir_stream(modules)
    s_dir   = ovba_compress(dir_unc)

    # _VBA_PROJECT: exactly the 2-byte Reserved signature (no p-code)
    s_vba_project = b'\xCC\x61'

    project_stream = (
        'ID="{00000000-0000-0000-0000-000000000000}"\r\n'
        'Document=ThisWorkbook/&H00000000\r\n'
        'Document=Sheet1/&H00000000\r\n'
        'HelpContextID="0"\r\n'
        'VersionCompatible32="393222000"\r\n'
        'CMG=""\r\n'
        'DPB=""\r\n'
        'GC=""\r\n'
    ).encode('latin-1')

    # PROJECTwm: ANSI name \0 UTF-16LE name \0\0 for each module
    pwm = b''
    for name in ('ThisWorkbook', 'Sheet1'):
        pwm += name.encode('latin-1') + b'\x00' + name.encode('utf-16-le') + b'\x00\x00'
    projectwm_stream = pwm

    return {
        'VBA/ThisWorkbook': s_twb,
        'VBA/Sheet1':       s_sheet1,
        'VBA/dir':          s_dir,
        'VBA/_VBA_PROJECT': s_vba_project,
        'PROJECT':          project_stream,
        'PROJECTwm':        projectwm_stream,
    }


# ── OLE2 CFB builder ─────────────────────────────────────────────────────────

FREESECT   = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT    = 0xFFFFFFFD
NOSTREAM   = 0xFFFFFFFF
SECTOR_SIZE      = 512
MINI_SECTOR_SIZE = 64
MINI_CUTOFF      = 4096


def _pad(data: bytes, mult: int) -> bytes:
    r = len(data) % mult
    return data + b'\x00' * (mult - r) if r else data


def _dir_entry(name: str, obj_type: int, color: int,
               left: int, right: int, child: int,
               clsid: bytes, start: int, size: int) -> bytes:
    enc = name.encode('utf-16-le')
    nlen = len(enc) + 2
    nfield = (enc + b'\x00\x00').ljust(64, b'\x00')[:64]
    return (nfield
            + struct.pack('<H', nlen)
            + struct.pack('<BB', obj_type, color)
            + struct.pack('<III', left, right, child)
            + clsid
            + struct.pack('<I', 0)    # StateBits
            + b'\x00' * 16           # timestamps
            + struct.pack('<I', start)
            + struct.pack('<I', size)
            + struct.pack('<I', 0))  # SizeHigh=0 (v3)


def build_cfb(streams: dict) -> bytes:
    """
    Directory layout (9 entries = 3 sectors of 4 each):
      0: Root Entry
      1: VBA  (storage)
      2: PROJECT
      3: PROJECTwm
      4: _VBA_PROJECT
      5: dir
      6: Sheet1
      7: ThisWorkbook
      8: (unused)
    """
    VBA_CLSID  = bytes([0x70,0xAE,0x7B,0xEA,0x3B,0xFB,0xCD,0x11,
                         0xA9,0x03,0x00,0xAA,0x00,0x51,0x0E,0xA3])
    NULL_CLSID = b'\x00' * 16

    # ── Allocate mini sectors ────────────────────────────────────────────────
    ORDER = ['Sheet1', 'ThisWorkbook', 'dir', '_VBA_PROJECT', 'PROJECT', 'PROJECTwm']
    mini_data = bytearray()
    allocs = {}

    for key in ORDER:
        skey = 'VBA/' + key if key in ('Sheet1','ThisWorkbook','dir','_VBA_PROJECT') else key
        data = streams[skey]
        first = len(mini_data) // MINI_SECTOR_SIZE
        padded = _pad(data, MINI_SECTOR_SIZE)
        count  = len(padded) // MINI_SECTOR_SIZE
        mini_data.extend(padded)
        allocs[key] = (first, len(data), count)

    total_mini_sects = len(mini_data) // MINI_SECTOR_SIZE

    # ── Mini FAT ─────────────────────────────────────────────────────────────
    mini_fat = []
    for key in ORDER:
        first, size, count = allocs[key]
        for i in range(count):
            mini_fat.append(first + i + 1 if i < count - 1 else ENDOFCHAIN)
    assert len(mini_fat) == total_mini_sects
    mini_fat += [FREESECT] * (128 - len(mini_fat))
    mini_fat_bytes = struct.pack('<128I', *mini_fat)

    # ── Sector layout ────────────────────────────────────────────────────────
    mini_container = _pad(bytes(mini_data), SECTOR_SIZE)
    mini_cont_sects = len(mini_container) // SECTOR_SIZE

    # Sector 0: FAT
    # Sector 1-3: Directory  (12 dir entries = 3 × 512-byte sectors)
    # Sector 4: Mini FAT
    # Sector 5+: Mini stream container

    DIR_S0        = 1
    DIR_S1        = 2
    DIR_S2        = 3
    MINIFAT_S     = 4
    MINICONT_FIRST = 5
    MINICONT_LAST  = MINICONT_FIRST + mini_cont_sects - 1

    fat = [FREESECT] * 128
    fat[0]      = FATSECT
    fat[DIR_S0] = DIR_S1
    fat[DIR_S1] = DIR_S2
    fat[DIR_S2] = ENDOFCHAIN
    fat[MINIFAT_S] = ENDOFCHAIN
    for s in range(MINICONT_FIRST, MINICONT_LAST + 1):
        fat[s] = s + 1 if s < MINICONT_LAST else ENDOFCHAIN
    fat_bytes = struct.pack('<128I', *fat)

    # ── Directory entries ────────────────────────────────────────────────────
    # Root level (case-insensitive alphabetical): PROJECT < PROJECTwm < VBA
    #   Balanced: PROJECTwm(3) is root, left=PROJECT(2), right=VBA(1)
    # VBA children (alpha): _VBA_PROJECT < dir < Sheet1 < ThisWorkbook
    #   Balanced: Sheet1(6) root, left=dir(5,left=_VBA_PROJECT(4)), right=ThisWorkbook(7)

    root_size = len(mini_data)

    entries = [
        # 0: Root Entry
        _dir_entry('Root Entry', 5, 1, NOSTREAM, NOSTREAM, 3,
                   NULL_CLSID, MINICONT_FIRST, root_size),
        # 1: VBA storage
        _dir_entry('VBA', 1, 0, NOSTREAM, NOSTREAM, 6,
                   VBA_CLSID, ENDOFCHAIN, 0),
        # 2: PROJECT
        _dir_entry('PROJECT', 2, 0, NOSTREAM, NOSTREAM, NOSTREAM,
                   NULL_CLSID, allocs['PROJECT'][0], allocs['PROJECT'][1]),
        # 3: PROJECTwm  (root of sibling tree for root storage)
        _dir_entry('PROJECTwm', 2, 1, 2, 1, NOSTREAM,
                   NULL_CLSID, allocs['PROJECTwm'][0], allocs['PROJECTwm'][1]),
        # 4: _VBA_PROJECT
        _dir_entry('_VBA_PROJECT', 2, 0, NOSTREAM, NOSTREAM, NOSTREAM,
                   NULL_CLSID, allocs['_VBA_PROJECT'][0], allocs['_VBA_PROJECT'][1]),
        # 5: dir  (left child: _VBA_PROJECT)
        _dir_entry('dir', 2, 1, 4, NOSTREAM, NOSTREAM,
                   NULL_CLSID, allocs['dir'][0], allocs['dir'][1]),
        # 6: Sheet1  (root of VBA children tree; left=dir subtree, right=ThisWorkbook)
        _dir_entry('Sheet1', 2, 1, 5, 7, NOSTREAM,
                   NULL_CLSID, allocs['Sheet1'][0], allocs['Sheet1'][1]),
        # 7: ThisWorkbook
        _dir_entry('ThisWorkbook', 2, 0, NOSTREAM, NOSTREAM, NOSTREAM,
                   NULL_CLSID, allocs['ThisWorkbook'][0], allocs['ThisWorkbook'][1]),
        # 8, 9, 10, 11: unused
        *[_dir_entry('', 0, 1, NOSTREAM, NOSTREAM, NOSTREAM,
                     NULL_CLSID, ENDOFCHAIN, 0) for _ in range(4)],
    ]

    dir_bytes = b''.join(entries)  # 12 × 128 = 1536 = 3 × 512 ✓

    # ── CFB Header ───────────────────────────────────────────────────────────
    difat = [0] + [FREESECT] * 108
    header = (
        b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'   # Magic
        + b'\x00' * 16                           # CLSID
        + struct.pack('<H', 0x003E)              # MinorVersion
        + struct.pack('<H', 0x0003)              # MajorVersion = 3
        + struct.pack('<H', 0xFFFE)              # ByteOrder
        + struct.pack('<H', 9)                   # SectorSizePower
        + struct.pack('<H', 6)                   # MiniSectorSizePower
        + b'\x00' * 6                            # Reserved
        + struct.pack('<I', 0)                   # NumDirSectors = 0 (v3)
        + struct.pack('<I', 1)                   # NumFATSectors
        + struct.pack('<I', DIR_S0)              # FirstDirSectorLoc
        + struct.pack('<I', 0)                   # TransactionSig
        + struct.pack('<I', MINI_CUTOFF)         # MiniStreamCutoff
        + struct.pack('<I', MINIFAT_S)           # FirstMiniFATSectorLoc
        + struct.pack('<I', 1)                   # NumMiniFATSectors
        + struct.pack('<I', FREESECT)            # FirstDIFATSectorLoc
        + struct.pack('<I', 0)                   # NumDIFATSectors
        + struct.pack('<109I', *difat)
    )
    assert len(header) == 512

    cfb = io.BytesIO()
    cfb.write(header)
    cfb.write(fat_bytes)
    cfb.write(dir_bytes)
    cfb.write(mini_fat_bytes)
    cfb.write(mini_container)
    return cfb.getvalue()


# ── Inject vbaProject.bin into xlsx → xlsm ──────────────────────────────────

def inject_vba(xlsx_path: str, xlsm_path: str, vba_bin: bytes):
    tmp = xlsm_path + '.tmp'
    with zipfile.ZipFile(xlsx_path, 'r') as zin, \
         zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            data = zin.read(item.filename)

            if item.filename == '[Content_Types].xml':
                ct = data.decode('utf-8')
                ct = ct.replace(
                    'application/vnd.openxmlformats-officedocument'
                    '.spreadsheetml.sheet.main+xml',
                    'application/vnd.ms-excel.sheet.macroEnabled.main+xml'
                )
                if 'vbaProject' not in ct:
                    ct = ct.replace('</Types>',
                        '<Override PartName="/xl/vbaProject.bin"'
                        ' ContentType="application/vnd.ms-office.vbaProject"/>\n</Types>')
                data = ct.encode('utf-8')

            elif item.filename == 'xl/workbook.xml':
                xml = data.decode('utf-8')
                # codeName はルート<workbook>ではなく<workbookPr>の属性
                if 'codeName' not in xml:
                    xml = xml.replace('<workbookPr ', '<workbookPr codeName="ThisWorkbook" ', 1)
                # 最初の<sheet>にcodeName="Sheet1"を追加
                import re
                def add_sheet_codename(m):
                    s = m.group(0)
                    if 'codeName' not in s:
                        s = s[:-2] + ' codeName="Sheet1"/>'
                    return s
                xml = re.sub(r'<sheet [^/]*/>', add_sheet_codename, xml, count=1)
                data = xml.encode('utf-8')

            elif item.filename == 'xl/worksheets/sheet1.xml':
                # sheetPrへのcodeName注入は不要（workbook.xmlのsheet要素で十分）
                pass

            elif item.filename == 'xl/_rels/workbook.xml.rels':
                rels = data.decode('utf-8')
                if 'vbaProject' not in rels:
                    rels = rels.replace('</Relationships>',
                        '<Relationship Id="rId99"'
                        ' Type="http://schemas.microsoft.com/office/2006/relationships/vbaProject"'
                        ' Target="vbaProject.bin"/>\n</Relationships>')
                data = rels.encode('utf-8')

            zout.writestr(item, data)

        # Add vbaProject.bin
        zout.writestr('xl/vbaProject.bin', vba_bin)

    os.replace(tmp, xlsm_path)
    print(f"Saved: {xlsm_path}")


# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    base     = '/home/user/Sunplaza-supermarket'
    xlsx_src = os.path.join(base, 'intent_tool.xlsx')
    xlsm_dst = os.path.join(base, 'intent_tool.xlsm')
    bin_dst  = os.path.join(base, 'vbaProject.bin')

    streams = make_streams()
    vba_bin = build_cfb(streams)

    with open(bin_dst, 'wb') as f:
        f.write(vba_bin)
    print(f"vbaProject.bin: {len(vba_bin)} bytes")

    import olefile
    ole = olefile.OleFileIO(bin_dst)
    print("OLE streams:", ole.listdir())
    ole.close()

    # Validate with oletools
    from oletools.olevba import VBA_Parser
    p = VBA_Parser(bin_dst)
    macros = list(p.extract_macros())
    print(f"Macros found: {len(macros)}")
    for m in macros:
        code = m[3] if len(m) > 3 else None
        print(f"  stream={m[1]}  code={'OK' if code else 'EMPTY'}")
        if code:
            print("  ", code[:80].replace('\n', ' '))

    inject_vba(xlsx_src, xlsm_dst, vba_bin)

    # Spot-check xlsm
    with zipfile.ZipFile(xlsm_dst) as z:
        wb  = z.read('xl/workbook.xml').decode()
        ct  = z.read('[Content_Types].xml').decode()
    import re
    print("workbook codeName:", re.search(r'codeName="[^"]*"', wb).group() if re.search(r'codeName', wb) else 'MISSING')
    sheet_cn = re.findall(r'<sheet [^>]*>', wb)
    print("sheet elements:", sheet_cn[:2])
    print("macroEnabled CT:", 'macroEnabled' in ct)
