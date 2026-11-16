"""Build on Windows x64 with Python 3.13 and PyInstaller 6.22.3.
Extract the Source-and-Payload release ZIP first; it supplies payload/.
"""
import json,subprocess,sys
from pathlib import Path

root=Path(__file__).resolve().parents[1]
payload=root/'payload'
if sys.platform!='win32':raise SystemExit('Windows x64 build required.')
if not(payload/'manifest.json').is_file():
    raise SystemExit('Extract FireProD-Kr-v0.901-Source-and-Payload.zip first.')
manifest=json.loads((payload/'manifest.json').read_text('utf-8'))
if manifest['version']!='0.901':raise SystemExit('Payload version mismatch.')
subprocess.run([sys.executable,'-I','-m','PyInstaller','--noconfirm','--clean',
    '--onefile','--windowed','--name','FireProD-Kr-v0.901-Patcher',
    '--add-data',str(payload)+';payload',
    '--version-file',str(root/'packaging/version-info.txt'),
    '--distpath',str(root/'dist'),'--workpath',str(root/'build/work'),
    '--specpath',str(root/'build'),str(root/'src/patcher.py')],check=True)
print('Built:',root/'dist/FireProD-Kr-v0.901-Patcher.exe')
