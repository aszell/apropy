# -*- mode: python -*-

block_cipher = None

a = Analysis(['apropy.py'],
             pathex=['w:\\langer'],
             binaries=None,
             datas=None,
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher)

skiplist = [  'bz2', 'unicodedata', 'ctypes', 'ssl', 'win32', 'PyQt4',
                'svg', 'select', 'opengl', 'xml', 'wintypes'] #, 'shiboken' ]

newbins = []                
                
for b in a.binaries:
    skip = False
    for s in skiplist:
        if s in b[1]:
            skip = True
    if skip:
        print "Skipping", b
    else:
        newbins.append(b)
        print "Keeping", b

a.binaries = newbins

for b in a.binaries:
    print b
             
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          name='apropy',
          debug=False,
          strip=False,      # would cause a few KB gain and program would not start...
          upx=True,
          console=False, icon='apropy.ico')
    