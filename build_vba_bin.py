#!/usr/bin/env python3
"""
Build a minimal vbaProject.bin (OLE2 CFB + MS-OVBA) from scratch in Python.
Injects it into intent_tool.xlsx to produce intent_tool.xlsm.

References:
  [MS-CFB]  https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb
  [MS-OVBA] https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-ovba
"""

import struct
import io
import zipfile
import shutil
import os
import re

# ── STEP 1: MS-OVBA Compression ────────────────────────────────────────────

def ovba_compress(data: bytes) -> bytes:
    """Compress bytes using MS-OVBA algorithm (Section 2.4).
    Uses all-literal tokens (flag byte = 0x00 for every group).
    """
    sig = b'\x01'  # SignatureByte
    if not data:
        return sig

    out = io.BytesIO()
    out.write(sig)

    pos = 0
    while pos < len(data):
        chunk = data[pos: pos + 4096]
        pos += 4096

        # Build compressed chunk with all-literal tokens
        comp = io.BytesIO()
        i = 0
        n = len(chunk)
        while i < n:
            group = chunk[i: i + 8]
            comp.write(b'\x00')        # flags: all 8 tokens are literals
            comp.write(group)
            i += 8
        comp_bytes = comp.getvalue()

        # MS-OVBA 2.4.1.1.4: CompressedChunkSize = data_size + 2 (includes header)
        # bits 0-11 = CompressedChunkSize - 3 = (data_size + 2) - 3 = data_size - 1
        hdr = 0xB000 | (len(comp_bytes) - 1)
        out.write(struct.pack('<H', hdr))
        out.write(comp_bytes)

    return out.getvalue()


# ── STEP 2: Build the VBA dir stream (uncompressed) ────────────────────────

def build_dir_stream(vba_code: str) -> bytes:
    """
    Build the uncompressed VBA dir stream (MS-OVBA 2.3.4.2).
    Module name = stream name = 'Sheet1'.
    Source is at offset 0 in the Sheet1 stream.
    """

    def rec(id_: int, data: bytes) -> bytes:
        return struct.pack('<HI', id_, len(data)) + data

    out = io.BytesIO()

    # ── Project properties ──────────────────────────────────────────────────
    out.write(rec(0x0001, struct.pack('<I', 0x00000001)))   # PROJECTSYSKIND: Win32
    out.write(rec(0x0002, struct.pack('<I', 0x0409)))        # PROJECTLCID
    out.write(rec(0x0014, struct.pack('<I', 0x0409)))        # PROJECTLCIDINVOKE
    out.write(rec(0x0003, struct.pack('<H', 1252)))          # PROJECTCODEPAGE
    out.write(rec(0x0004, b'VBAProject'))                    # PROJECTNAME
    out.write(rec(0x0005, b''))                              # PROJECTDOCSTRING ANSI
    out.write(rec(0x0040, b''))                              # PROJECTDOCSTRING Unicode
    out.write(rec(0x0006, b''))                              # PROJECTHELPFILEPATH 1
    out.write(rec(0x003D, b''))                              # PROJECTHELPFILEPATH 2
    out.write(rec(0x0007, struct.pack('<I', 0)))             # PROJECTHELPCONTEXT
    out.write(rec(0x0008, struct.pack('<I', 0)))             # PROJECTLIBFLAGS
    # PROJECTVERSION: Id(2) + Reserved=4(4) + MajorVersion(4) + MinorVersion(2)
    # Note: no separate Id2=0x0049 field in the actual byte stream
    out.write(struct.pack('<HI', 0x0009, 4))
    out.write(struct.pack('<I', 0x61440000))                 # MajorVersion
    out.write(struct.pack('<H', 0))                          # MinorVersion
    out.write(rec(0x000C, b''))                              # PROJECTCONSTANTS ANSI
    out.write(rec(0x003C, b''))                              # PROJECTCONSTANTS Unicode

    # ── PROJECTREFERENCES: none ─────────────────────────────────────────────

    # ── PROJECTMODULES ──────────────────────────────────────────────────────
    out.write(struct.pack('<HI', 0x000F, 4))                 # PROJECTMODULES Id, Size=4
    out.write(struct.pack('<I', 1))                          # Count = 1
    out.write(struct.pack('<HH', 0x0013, 2))                 # ProjectCookie Id, Size=2
    out.write(struct.pack('<H', 0xFFFF))                     # Cookie

    # ── Module: Sheet1 ──────────────────────────────────────────────────────
    name_ansi    = b'Sheet1'
    name_unicode = 'Sheet1'.encode('utf-16-le')

    out.write(rec(0x0019, name_ansi))                        # MODULENAME ANSI
    out.write(rec(0x0047, name_unicode))                     # MODULENAMEUNICODE (real id=0x0047)
    out.write(rec(0x001A, name_ansi))                        # MODULESTREAMNAME ANSI
    out.write(rec(0x0032, name_unicode))                     # MODULESTREAMNAME Unicode
    out.write(rec(0x001C, b''))                              # MODULEDOCSTRING ANSI
    out.write(rec(0x0048, b''))                              # MODULEDOCSTRING Unicode
    out.write(rec(0x0031, struct.pack('<I', 0)))             # MODULEOFFSET = 0
    out.write(rec(0x001E, struct.pack('<I', 0)))             # MODULEHELPCONTEXT = 0
    out.write(rec(0x002C, struct.pack('<H', 0xFFFF)))        # MODULECOOKIE
    out.write(rec(0x0022, b''))                              # MODULETYPE: document/class
    out.write(rec(0x002B, b''))                              # MODULETERM

    return out.getvalue()


# ── STEP 3: Assemble streams ────────────────────────────────────────────────

VBA_CODE = """\
Private Sub Worksheet_Change(ByVal Target As Range)
    If Target.Address <> "$H$10" Then Exit Sub
    Dim r As Long
    Application.ScreenUpdating = False
    For r = 16 To 38
        ActiveSheet.Rows(r).Hidden = True
    Next r
    For r = 40 To 46
        ActiveSheet.Rows(r).Hidden = True
    Next r
    Select Case Left(Target.Value, 1)
        Case Chr(9312), Chr(9313)
            For r = 16 To 38
                ActiveSheet.Rows(r).Hidden = False
            Next r
        Case Chr(9314)
            For r = 40 To 46
                ActiveSheet.Rows(r).Hidden = False
            Next r
    End Select
    Application.ScreenUpdating = True
End Sub
"""

def make_streams():
    """Return dict of stream_path → bytes for all required VBA streams."""
    # Sheet1 module stream: compressed source (offset=0, no p-code before it)
    sheet1_src = VBA_CODE.encode('latin-1')
    sheet1_stream = ovba_compress(sheet1_src)

    # dir stream: compressed dir record
    dir_uncompressed = build_dir_stream(VBA_CODE)
    dir_stream = ovba_compress(dir_uncompressed)

    # _VBA_PROJECT: minimal performance cache stub (CC 61 signature + reserved)
    vba_project_stream = b'\xCC\x61' + b'\x00' * 5

    # PROJECT text stream
    # Sheet1 must be listed as Document= (class/document module) so that
    # Worksheet_Change events fire.  ThisWorkbook is the workbook module.
    project_stream = (
        'ID="{00000000-0000-0000-0000-000000000000}"\r\n'
        'Document=Sheet1/&H00000000\r\n'
        'HelpContextID="0"\r\n'
        'VersionCompatible32="393222000"\r\n'
        'CMG=""\r\n'
        'DPB=""\r\n'
        'GC=""\r\n'
    ).encode('latin-1')

    # PROJECTwm: module name → Unicode name mapping
    projectwm_stream = b'Sheet1\x00' + 'Sheet1'.encode('utf-16-le') + b'\x00\x00'

    return {
        'VBA/Sheet1':       sheet1_stream,
        'VBA/dir':          dir_stream,
        'VBA/_VBA_PROJECT': vba_project_stream,
        'PROJECT':          project_stream,
        'PROJECTwm':        projectwm_stream,
    }


# ── STEP 4: Build OLE2 CFB (Compound File Binary) ──────────────────────────

FREESECT   = 0xFFFFFFFF
ENDOFCHAIN = 0xFFFFFFFE
FATSECT    = 0xFFFFFFFD
DIFSECT    = 0xFFFFFFFC
NOSTREAM   = 0xFFFFFFFF

SECTOR_SIZE      = 512
MINI_SECTOR_SIZE = 64
MINI_CUTOFF      = 4096


def _pad(data: bytes, multiple: int) -> bytes:
    rem = len(data) % multiple
    return data + b'\x00' * (multiple - rem) if rem else data


def build_cfb(streams: dict) -> bytes:
    """
    Build a minimal OLE2 CFB file containing the given streams.
    streams: dict mapping 'StorageName/StreamName' or 'StreamName' → bytes

    Directory layout:
      0: Root Entry  (storage)
      1: VBA         (storage, CLSID={EA7BAE70-...})
      2: PROJECT     (stream)
      3: PROJECTwm   (stream)
      4: _VBA_PROJECT (stream, inside VBA)
      5: dir          (stream, inside VBA)
      6: Sheet1       (stream, inside VBA)
    """

    # ── Gather stream data ───────────────────────────────────────────────────
    s_vba_project = streams['VBA/_VBA_PROJECT']
    s_dir         = streams['VBA/dir']
    s_sheet1      = streams['VBA/Sheet1']
    s_project     = streams['PROJECT']
    s_projectwm   = streams['PROJECTwm']

    # All streams go to mini stream (all are < MINI_CUTOFF = 4096 bytes)
    # Mini sectors are 64 bytes each.

    def mini_alloc(data: bytes):
        """Allocate mini sectors for data. Returns (first_sector, padded_data)."""
        padded = _pad(data, MINI_SECTOR_SIZE)
        count = len(padded) // MINI_SECTOR_SIZE
        return count, padded

    # Allocate mini sectors:
    #   Sheet1: first
    #   dir: next
    #   _VBA_PROJECT: next
    #   PROJECT: next
    #   PROJECTwm: last

    mini_data = bytearray()
    allocs = {}   # name → (first_mini_sector, size_bytes)

    def alloc(name, data):
        first = len(mini_data) // MINI_SECTOR_SIZE
        count, padded = mini_alloc(data)
        mini_data.extend(padded)
        allocs[name] = (first, len(data), count)  # (start, size, num_sectors)

    alloc('Sheet1',       s_sheet1)
    alloc('dir',          s_dir)
    alloc('_VBA_PROJECT', s_vba_project)
    alloc('PROJECT',      s_project)
    alloc('PROJECTwm',    s_projectwm)

    total_mini_bytes = len(mini_data)
    total_mini_sectors = total_mini_bytes // MINI_SECTOR_SIZE

    # Build mini FAT (one mini FAT sector should be enough for ≤128 mini sectors)
    mini_fat = []
    for name in ('Sheet1', 'dir', '_VBA_PROJECT', 'PROJECT', 'PROJECTwm'):
        first, size, count = allocs[name]
        for i in range(count):
            if i < count - 1:
                mini_fat.append(first + i + 1)
            else:
                mini_fat.append(ENDOFCHAIN)
    assert len(mini_fat) == total_mini_sectors

    # Pad mini FAT to 128 entries (one full sector)
    mini_fat_padded = mini_fat + [FREESECT] * (128 - len(mini_fat))
    mini_fat_bytes = struct.pack('<128I', *mini_fat_padded)

    # Mini stream container (regular sectors, each 512 bytes)
    mini_container = _pad(bytes(mini_data), SECTOR_SIZE)
    mini_sectors_count = len(mini_container) // SECTOR_SIZE

    # ── Sector layout ────────────────────────────────────────────────────────
    # Sector 0:  FAT sector
    # Sector 1:  Directory sector 0 (entries 0-3)
    # Sector 2:  Directory sector 1 (entries 4-7)
    # Sector 3:  Mini FAT sector
    # Sector 4…: Mini stream container sectors

    DIR_SECTOR_0    = 1
    DIR_SECTOR_1    = 2
    MINI_FAT_SECTOR = 3
    MINI_CONT_FIRST = 4
    MINI_CONT_LAST  = MINI_CONT_FIRST + mini_sectors_count - 1

    total_sectors = MINI_CONT_LAST + 1  # sectors 0 .. MINI_CONT_LAST

    # Build FAT (one sector = 128 entries)
    fat = [FREESECT] * 128
    fat[0]              = FATSECT        # Sector 0 = FAT sector itself
    fat[DIR_SECTOR_0]   = DIR_SECTOR_1   # Sector 1 → 2 (directory chain)
    fat[DIR_SECTOR_1]   = ENDOFCHAIN     # Sector 2 = end of directory chain
    fat[MINI_FAT_SECTOR] = ENDOFCHAIN    # Sector 3 = mini FAT (single sector chain)
    for s in range(MINI_CONT_FIRST, MINI_CONT_LAST + 1):
        fat[s] = s + 1 if s < MINI_CONT_LAST else ENDOFCHAIN
    fat_bytes = struct.pack('<128I', *fat)

    # ── Directory entries (128 bytes each, 4 per sector) ─────────────────────

    def dir_entry(name: str, obj_type: int, color: int,
                  left: int, right: int, child: int,
                  clsid: bytes, start: int, size: int) -> bytes:
        name_utf16 = name.encode('utf-16-le')
        name_len   = len(name_utf16) + 2   # includes null terminator
        name_field = (name_utf16 + b'\x00\x00').ljust(64, b'\x00')[:64]
        return (
            name_field +
            struct.pack('<H', name_len) +
            struct.pack('<BB', obj_type, color) +
            struct.pack('<III', left, right, child) +
            clsid +                          # 16 bytes CLSID
            struct.pack('<II', 0, 0) +       # State, reserved
            b'\x00' * 16 +                   # Created + Modified timestamps
            struct.pack('<I', start) +
            struct.pack('<Q', size)           # size (8 bytes for v4; v3 uses 4+4pad)
        )

    # Actually for CFB version 3, the size field in directory entry is:
    # 4-byte size + 4-byte padding (high word MUST be zero)
    # Let's use that format.

    def dir_entry_v3(name: str, obj_type: int, color: int,
                     left: int, right: int, child: int,
                     clsid: bytes, start: int, size: int) -> bytes:
        name_utf16 = name.encode('utf-16-le')
        name_len   = len(name_utf16) + 2
        name_field = (name_utf16 + b'\x00\x00').ljust(64, b'\x00')[:64]
        return (
            name_field +
            struct.pack('<H', name_len) +     # DirectoryEntryNameLength
            struct.pack('<BB', obj_type, color) +  # ObjectType, ColorFlag
            struct.pack('<III', left, right, child) +  # LeftSibling, RightSibling, Child
            clsid +                            # CLSID (16 bytes)
            struct.pack('<I', 0) +             # StateBits
            b'\x00' * 8 +                      # CreatedTime
            b'\x00' * 8 +                      # ModifiedTime
            struct.pack('<I', start) +          # StartingSectorLocation
            struct.pack('<I', size) +           # SizeLow (v3)
            struct.pack('<I', 0)                # SizeHigh = 0 (v3)
        )

    # VBA storage CLSID: {EA7BAE70-FB3B-11CD-A903-00AA00510EA3}
    VBA_CLSID = bytes([
        0x70, 0xAE, 0x7B, 0xEA, 0x3B, 0xFB, 0xCD, 0x11,
        0xA9, 0x03, 0x00, 0xAA, 0x00, 0x51, 0x0E, 0xA3
    ])
    NULL_CLSID = b'\x00' * 16

    # Root Entry CLSID (for vbaProject.bin): NULL or specific
    ROOT_CLSID = NULL_CLSID

    # ── Tree structure ──────────────────────────────────────────────────────
    # Root level children (alphabetical, case-insensitive): PROJECT < PROJECTwm < VBA
    #   Tree root: PROJECTwm (idx=3), left=PROJECT(2), right=VBA(1)
    # VBA storage children: _VBA_PROJECT < dir < Sheet1 (case-insensitive)
    #   Tree root: dir (idx=5), left=_VBA_PROJECT(4), right=Sheet1(6)

    # Color: 0=RED, 1=BLACK

    root_mini_size = total_mini_bytes  # size of mini stream

    entries = [
        # 0: Root Entry
        dir_entry_v3(
            'Root Entry', 5, 1,   # type=5 (root), color=black
            NOSTREAM, NOSTREAM, 3,  # child = PROJECTwm (root of level-1 tree)
            ROOT_CLSID,
            MINI_CONT_FIRST, root_mini_size
        ),
        # 1: VBA storage
        dir_entry_v3(
            'VBA', 1, 0,           # type=1 (storage), color=red
            NOSTREAM, NOSTREAM, 5, # child = dir (root of VBA children tree)
            VBA_CLSID,
            ENDOFCHAIN, 0
        ),
        # 2: PROJECT stream
        dir_entry_v3(
            'PROJECT', 2, 0,       # type=2 (stream), color=red
            NOSTREAM, NOSTREAM, NOSTREAM,
            NULL_CLSID,
            allocs['PROJECT'][0], allocs['PROJECT'][1]
        ),
        # 3: PROJECTwm stream (root of level-1 sibling tree)
        dir_entry_v3(
            'PROJECTwm', 2, 1,     # type=2, color=black (root of subtree)
            2, 1, NOSTREAM,        # left=PROJECT(2), right=VBA(1)
            NULL_CLSID,
            allocs['PROJECTwm'][0], allocs['PROJECTwm'][1]
        ),
        # 4: _VBA_PROJECT stream (child of VBA)
        dir_entry_v3(
            '_VBA_PROJECT', 2, 0,  # color=red
            NOSTREAM, NOSTREAM, NOSTREAM,
            NULL_CLSID,
            allocs['_VBA_PROJECT'][0], allocs['_VBA_PROJECT'][1]
        ),
        # 5: dir stream (root of VBA children tree)
        dir_entry_v3(
            'dir', 2, 1,           # color=black
            4, 6, NOSTREAM,        # left=_VBA_PROJECT(4), right=Sheet1(6)
            NULL_CLSID,
            allocs['dir'][0], allocs['dir'][1]
        ),
        # 6: Sheet1 stream
        dir_entry_v3(
            'Sheet1', 2, 0,        # color=red
            NOSTREAM, NOSTREAM, NOSTREAM,
            NULL_CLSID,
            allocs['Sheet1'][0], allocs['Sheet1'][1]
        ),
        # 7: unused padding
        dir_entry_v3(
            '', 0, 1,              # type=0 (unused)
            NOSTREAM, NOSTREAM, NOSTREAM,
            NULL_CLSID,
            ENDOFCHAIN, 0
        ),
    ]

    dir_sector = b''.join(entries)   # 8 × 128 = 1024 bytes = 2 sectors ✓

    # ── CFB Header (512 bytes) ────────────────────────────────────────────────
    MAGIC = b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'

    # DIFAT: first 109 sector locations that contain FAT sectors
    # We have only 1 FAT sector (sector 0)
    difat = [0] + [FREESECT] * 108   # sector 0 is the FAT; rest are free

    header = (
        MAGIC +                                       # Signature
        b'\x00' * 16 +                                # CLSID (null)
        struct.pack('<H', 0x003E) +                   # MinorVersion
        struct.pack('<H', 0x0003) +                   # MajorVersion = 3
        struct.pack('<H', 0xFFFE) +                   # ByteOrder (little-endian)
        struct.pack('<H', 9) +                        # SectorSizePower (2^9 = 512)
        struct.pack('<H', 6) +                        # MiniSectorSizePower (2^6 = 64)
        b'\x00' * 6 +                                 # Reserved
        struct.pack('<I', 0) +                        # NumDirSectors MUST be 0 for v3
        struct.pack('<I', 1) +                        # NumFATSectors = 1
        struct.pack('<I', DIR_SECTOR_0) +             # FirstDirSectorLoc
        struct.pack('<I', 0) +                        # TransactionSig
        struct.pack('<I', MINI_CUTOFF) +              # MiniStreamCutoff = 4096
        struct.pack('<I', MINI_FAT_SECTOR) +          # FirstMiniFATSectorLoc
        struct.pack('<I', 1) +                        # NumMiniFATSectors = 1
        struct.pack('<I', FREESECT) +                 # FirstDIFATSectorLoc (none)
        struct.pack('<I', 0) +                        # NumDIFATSectors = 0
        struct.pack('<109I', *difat)                  # DIFAT array
    )
    assert len(header) == 512, f"Header is {len(header)} bytes"

    # ── Assemble file ──────────────────────────────────────────────────────
    cfb = io.BytesIO()
    cfb.write(header)           # Sector -1 (header)
    cfb.write(fat_bytes)        # Sector 0: FAT
    cfb.write(dir_sector)       # Sectors 1-2: Directory
    cfb.write(mini_fat_bytes)   # Sector 3: Mini FAT
    cfb.write(mini_container)   # Sectors 4+: Mini stream container

    return cfb.getvalue()


# ── STEP 5: Inject vbaProject.bin into xlsx → xlsm ─────────────────────────

def inject_vba(xlsx_path: str, xlsm_path: str, vba_bin: bytes):
    """
    Copy xlsx as xlsm, injecting xl/vbaProject.bin.
    Updates [Content_Types].xml and xl/_rels/workbook.xml.rels.
    """
    shutil.copy2(xlsx_path, xlsm_path)

    with zipfile.ZipFile(xlsm_path, 'a') as zf:
        # Add vbaProject.bin
        zf.writestr('xl/vbaProject.bin', vba_bin)

    # Now we need to update existing XML entries — rebuild the zip
    tmp_path = xlsm_path + '.tmp'
    with zipfile.ZipFile(xlsm_path, 'r') as zin, \
         zipfile.ZipFile(tmp_path, 'w', zipfile.ZIP_DEFLATED) as zout:

        for item in zin.infolist():
            data = zin.read(item.filename)

            if item.filename == '[Content_Types].xml':
                ct = data.decode('utf-8')
                # Add xlsm content type
                if 'vbaProject.bin' not in ct:
                    ct = ct.replace(
                        '</Types>',
                        '<Override PartName="/xl/vbaProject.bin"'
                        ' ContentType="application/vnd.ms-office.activeX+xml"/>\n'
                        '</Types>'
                    )
                # Change workbook content type from xlsx to xlsm
                ct = ct.replace(
                    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml',
                    'application/vnd.ms-excel.sheet.macroEnabled.main+xml'
                )
                # Fix vbaProject content type (may have been added wrong above)
                ct = ct.replace(
                    'application/vnd.ms-office.activeX+xml',
                    'application/vnd.ms-office.vbaProject'
                )
                data = ct.encode('utf-8')

            elif item.filename == 'xl/worksheets/sheet1.xml':
                # Add codeName="Sheet1" so VBA doc module binds to this sheet
                xml = data.decode('utf-8')
                if 'codeName' not in xml:
                    xml = xml.replace('<sheetPr>', '<sheetPr codeName="Sheet1">', 1)
                    if '<sheetPr>' not in xml and 'codeName' not in xml:
                        xml = xml.replace('<sheetPr ', '<sheetPr codeName="Sheet1" ', 1)
                data = xml.encode('utf-8')

            elif item.filename == 'xl/_rels/workbook.xml.rels':
                rels = data.decode('utf-8')
                if 'vbaProject.bin' not in rels:
                    rels = rels.replace(
                        '</Relationships>',
                        '<Relationship Id="rId99" '
                        'Type="http://schemas.microsoft.com/office/2006/relationships/vbaProject" '
                        'Target="vbaProject.bin"/>\n'
                        '</Relationships>'
                    )
                data = rels.encode('utf-8')

            zout.writestr(item, data)

    os.replace(tmp_path, xlsm_path)
    print(f"Saved: {xlsm_path}")


# ── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    base = '/home/user/Sunplaza-supermarket'
    xlsx_src  = os.path.join(base, 'intent_tool.xlsx')
    xlsm_dst  = os.path.join(base, 'intent_tool.xlsm')
    bin_dst   = os.path.join(base, 'vbaProject.bin')

    streams   = make_streams()
    vba_bin   = build_cfb(streams)

    with open(bin_dst, 'wb') as f:
        f.write(vba_bin)
    print(f"vbaProject.bin written: {len(vba_bin)} bytes")

    # Quick sanity check with olefile
    import olefile
    ole = olefile.OleFileIO(bin_dst)
    print("OLE streams:", ole.listdir())
    ole.close()

    inject_vba(xlsx_src, xlsm_dst, vba_bin)

    # Verify xlsm contents
    with zipfile.ZipFile(xlsm_dst) as z:
        names = z.namelist()
        print("xlsm files:", [n for n in names if 'vba' in n.lower() or 'Content' in n])
        ct = z.read('[Content_Types].xml').decode()
        rels = z.read('xl/_rels/workbook.xml.rels').decode()
    print("Content-Type xlsm:", 'macroEnabled' in ct)
    print("vbaProject rel:", 'vbaProject' in rels)
