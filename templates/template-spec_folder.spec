# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.config
import os
import PySide2
PyInstaller.config.CONF['workpath'] = '$workdir/build'
PyInstaller.config.CONF['distpath'] = '$workdir/dist'

plugins_path = os.path.join(PySide2.__path__[0], 'plugins')
platformspath = os.path.join(plugins_path, 'platforms')

block_cipher = None


a = Analysis(['$pythonfile'],
             pathex=['$workdir'],
             binaries=[],
             datas=[],
             hiddenimports=['future', 'PySimpleGUI',  'PySide2', 'qdarkstyle', 'configparser', 'encodings'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['tkinter', 'unittest', 'email', 'http', 'xml', 'pydoc', 'pdb'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='$pythonname',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='$iconfile',
          version='version-file.txt' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='$pythonname' )
