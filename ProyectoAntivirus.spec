# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Agrega la ruta donde se encuentra tkdnd2.8
tkdnd_library_path = 'C:\\Users\\Medios Zamir\\AppData\\Local\\Programs\\Python\\Python311\\tcl\\tkdnd2.8'
tkdnd_destination = 'tkdnd2.8'

a = Analysis(['ProyectoAntivirus.py'],
             pathex=[],
             binaries=[(tkdnd_library_path, tkdnd_destination)],  # Añade la biblioteca tkdnd
             datas=[('C:\\Users\\Medios Zamir\\Documents\\ProyectoAntivirus\\ProyectoAntivirus\\assets', 'assets')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='ProyectoAntivirus',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='assets/ico.png',
          target_arch='x86_64',
          upx_exclude=[],
          runtime_tmpdir=None,
          cipher=block_cipher)
