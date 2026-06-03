"""
VBA付き .xlsm を生成する。
手順:
1. openpyxl で生成した .xlsx を読み込む
2. zipfile で xl/vbaProject.bin を注入し、ContentTypes と rel を更新
3. .xlsm として保存

vbaProject.bin は LibreOffice を使って動的に生成する。
"""
import subprocess, os, zipfile, shutil, tempfile, base64, struct

# ── LibreOffice でVBAコードを持つ最小xlsmを生成 ──────────────
# LibreOfficeのマクロ実行スクリプト
LO_SCRIPT = r"""
import uno
import os
import subprocess

def make_vba_bin(out_path):
    \"\"\"LibreOffice を headless 起動し、マクロ付き xlsm を生成して vbaProject.bin を抽出\"\"\"
    # python-uno が使える環境なら UNO API で直接操作できるが、
    # ここでは LibreOffice Basic macro を経由するより
    # 直接 zipfile モジュールで vbaProject.bin を手作りする方が確実。
    pass
"""

# ── 最小限の有効な vbaProject.bin を Python で生成 ───────────
# OLE2 Compound Document Binary Format (CFB) の最小構造を構築する
# 参照: [MS-CFB] https://docs.microsoft.com/en-us/openspecs/windows_protocols/ms-cfb
# 参照: [MS-OVBA] VBA project storage format

def build_vba_project(vba_code_sheet1: str) -> bytes:
    """
    最小限の vbaProject.bin (OLE2 CFB) を構築する。
    Sheet1 の Worksheet_Change イベントハンドラを含む。
    """
    import io

    # ── VBA ストリームの内容を準備 ──────────────────────────
    # PROJECT ストリーム（テキスト）
    project_str = (
        "ID=\"{00000000-0000-0000-0000-000000000000}\"\r\n"
        "Document=ThisWorkbook/&H00000000\r\n"
        "Module=Sheet1\r\n"
        "HelpContextID=\"0\"\r\n"
        "VersionCompatible32=\"393222000\"\r\n"
        "CMG=\"\"\r\n"
        "DPB=\"\"\r\n"
        "GC=\"\"\r\n"
    ).encode("latin-1")

    # PROJECTwm ストリーム（Unicode name mapping）
    # Format: ModuleName\0UnicodeModuleName\0\0
    projectwm = b"Sheet1\x00S\x00h\x00e\x00e\x00t\x001\x00\x00\x00"

    # VBA dir ストリーム（圧縮された directory record）
    # これは非常に複雑なバイナリ形式のため、最小限の既知バイナリを使用
    # 実際の有効な dir ストリームは特定のコンパイル済みバイナリが必要

    # ここでは別アプローチを使う：
    # LibreOffice で一度ダミーファイルを生成して vbaProject.bin を抽出
    return None  # フォールバックを使用


def create_xlsm_via_lo():
    """LibreOffice を使って VBA 付き xlsm を生成する"""
    import subprocess, tempfile, os

    # LibreOffice Basic マクロスクリプト（Python から呼び出せる形式）
    # soffice --headless でマクロを実行する方法を使う

    # LibreOffice のマクロライブラリディレクトリ
    lo_macro_dir = os.path.expanduser("~/.config/libreoffice/4/user/Scripts/python")
    os.makedirs(lo_macro_dir, exist_ok=True)

    # Python-UNO スクリプトを作成
    script_content = '''
import uno
import os
from com.sun.star.beans import PropertyValue

def generate_vba_xlsm(*args):
    ctx = uno.getComponentContext()
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    # 新しいCalcドキュメントを作成
    props = []
    p = PropertyValue()
    p.Name = "Hidden"
    p.Value = True
    props.append(p)

    doc = desktop.loadComponentFromURL(
        "private:factory/scalc", "_blank", 0, tuple(props))

    sheets = doc.Sheets
    sheet = sheets.getByIndex(0)
    sheet.setName("意向確認シート")

    # VBA互換のBasicマクロを追加
    # LibreOffice Basic で Sheet_Change イベントを設定
    # これはExcelのWorksheet_ChangeとVBA互換

    # モジュールにコードを追加
    basic = doc.BasicLibraries
    basic.createLibrary("VBAProject")
    lib = basic.getByName("VBAProject")
    lib.insertByName("Sheet1", "")

    vba_code = """
Option VBASupport 1

Private Sub Worksheet_Change(ByVal Target As Range)
    If Target.Address <> "$H$10" Then Exit Sub
    Dim ws As Worksheet
    Set ws = Target.Worksheet
    Dim v As String
    v = Target.Value
    Application.ScreenUpdating = False
    ' 両グループを折りたたみ
    Dim r As Long
    For r = 16 To 38
        ws.Rows(r).Hidden = True
    Next r
    For r = 40 To 46
        ws.Rows(r).Hidden = True
    Next r
    ' 選択に応じて展開
    Select Case Left(v, 1)
        Case "①", "②"
            For r = 16 To 38
                ws.Rows(r).Hidden = False
            Next r
        Case "③"
            For r = 40 To 46
                ws.Rows(r).Hidden = False
            Next r
    End Select
    Application.ScreenUpdating = True
End Sub
"""
    lib.replaceByName("Sheet1", vba_code)

    # xlsm として保存
    out_path = "/home/user/Sunplaza-supermarket/intent_tool_vba_raw.xlsm"
    props2 = []
    p2 = PropertyValue()
    p2.Name = "FilterName"
    p2.Value = "Calc MS Excel 2007 VBA XML"
    props2.append(p2)
    p3 = PropertyValue()
    p3.Name = "Overwrite"
    p3.Value = True
    props2.append(p3)

    doc.storeToURL("file://" + out_path, tuple(props2))
    doc.close(True)
    return out_path
'''

    script_path = os.path.join(lo_macro_dir, "gen_xlsm.py")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    # LibreOffice をソケットサーバーとして起動
    lo_proc = subprocess.Popen(
        ["soffice", "--headless", "--norestore", "--nofirststartwizard",
         "--accept=socket,host=localhost,port=2002;urp;StarOffice.ServiceManager"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
    )

    import time
    time.sleep(4)

    # UNO 経由で接続してマクロを実行
    try:
        run_script = '''
import sys
sys.path.insert(0, "/usr/lib/libreoffice/program")
import uno
from com.sun.star.beans import PropertyValue

localContext = uno.getComponentContext()
resolver = localContext.ServiceManager.createInstanceWithContext(
    "com.sun.star.bridge.UnoUrlResolver", localContext)

try:
    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=2002;urp;StarOffice.ComponentContext")
    smgr = ctx.ServiceManager
    desktop = smgr.createInstanceWithContext("com.sun.star.frame.Desktop", ctx)

    # 新しいCalcドキュメントを作成
    p_hidden = PropertyValue()
    p_hidden.Name = "Hidden"
    p_hidden.Value = True

    doc = desktop.loadComponentFromURL(
        "private:factory/scalc", "_blank", 0, (p_hidden,))

    # VBAサポートを有効化
    doc.setPropertyValue("ApplyFormDesignMode", False)

    # Basicライブラリ設定
    basic = doc.BasicLibraries
    if not basic.hasByName("VBAProject"):
        basic.createLibrary("VBAProject")
    lib = basic.getByName("VBAProject")

    vba_code = chr(10).join([
        "Option VBASupport 1",
        "",
        "Private Sub Worksheet_Change(ByVal Target As Range)",
        "    If Target.Address <> chr(36) & chr(72) & chr(36) & chr(49) & chr(48) Then Exit Sub",
        "    Dim ws As Object",
        "    Set ws = Target.Worksheet",
        "    Dim v As String",
        "    v = Target.Value",
        "    Dim r As Long",
        "    For r = 16 To 38",
        "        ws.Rows(r).Hidden = True",
        "    Next r",
        "    For r = 40 To 46",
        "        ws.Rows(r).Hidden = True",
        "    Next r",
        "    Select Case Left(v, 1)",
        "        Case chr(9312), chr(9313)",
        "            For r = 16 To 38 : ws.Rows(r).Hidden = False : Next r",
        "        Case chr(9314)",
        "            For r = 40 To 46 : ws.Rows(r).Hidden = False : Next r",
        "    End Select",
        "End Sub",
    ])

    if lib.hasByName("Sheet1"):
        lib.replaceByName("Sheet1", vba_code)
    else:
        lib.insertByName("Sheet1", vba_code)

    out_url = "file:///home/user/Sunplaza-supermarket/intent_tool_vba_raw.xlsm"
    p_filter = PropertyValue()
    p_filter.Name = "FilterName"
    p_filter.Value = "Calc MS Excel 2007 VBA XML"
    p_overwrite = PropertyValue()
    p_overwrite.Name = "Overwrite"
    p_overwrite.Value = True

    doc.storeToURL(out_url, (p_filter, p_overwrite))
    doc.close(True)
    print("SUCCESS: saved to intent_tool_vba_raw.xlsm")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
'''
        result = subprocess.run(
            ["python3", "-c", run_script],
            capture_output=True, text=True, timeout=30
        )
        print("stdout:", result.stdout)
        if result.stderr:
            print("stderr:", result.stderr[:500])
    finally:
        lo_proc.terminate()
        lo_proc.wait()


if __name__ == "__main__":
    create_xlsm_via_lo()
