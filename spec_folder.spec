# -*- mode: python ; coding: utf-8 -*-

import PyInstaller.config
PyInstaller.config.CONF['workpath'] = 'D:/Work/PySimpleGui-ExeMaker/build'
PyInstaller.config.CONF['distpath'] = 'D:/Work/PySimpleGui-ExeMaker/dist'

block_cipher = None


a = Analysis(['D:/Work/PySimpleGui-ExeMaker/app/PyExeMaker.py'],
             pathex=['D:/Work/PySimpleGui-ExeMaker'],
             binaries=[],
             datas=[['D:/Work/PySimpleGui-ExeMaker/dist/resources-dist',
 'resources'], ['D:/Work/PySimpleGui-ExeMaker/dist/templates-dist', 'templates']],
             hiddenimports=['future', 'PySimpleGUI'],
             hookspath=[],
             runtime_hooks=[],
             excludes=['unittest', 'xml', 'pydoc', 'pdb'],
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
          name='PySimpleGui-ExeMaker',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False,
          icon='D:/Work/PySimpleGui-ExeMaker/resources/navigatorsimple.ico',
          version='version-file.txt' )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='PyExeMaker' )




