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

'''             
good:
('Microsoft.VC90.CRT.manifest', u'C:\\WINDOWS\\WinSxS\\Manifests\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.6161_x-ww_31a54e43.manifest', 'BINARY')
('msvcr90.dll', u'C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.6161_x-ww_31a54e43\\msvcr90.dll', 'BINARY')
('msvcp90.dll', u'C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.6161_x-ww_31a54e43\\msvcp90.dll', 'BINARY')
('msvcm90.dll', u'C:\\WINDOWS\\WinSxS\\x86_Microsoft.VC90.CRT_1fc8b3b9a1e18e3b_9.0.30729.6161_x-ww_31a54e43\\msvcm90.dll', 'BINARY')
('python27.dll', 'C:\\WINDOWS\\system32\\python27.dll', 'BINARY')
('PySide.QtCore', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\QtCore.pyd', 'EXTENSION')
('PySide.QtGui', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\QtGui.pyd', 'EXTENSION')
('QtGui4.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\qtgui4.dll', 'BINARY')
('QtCore4.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\qtcore4.dll', 'BINARY')
('pyside-python2.7.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\pyside-python2.7.dll', 'BINARY')


bad:             
             
('qt4_plugins\\iconengines\\qsvgicon4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\iconengines\\qsvgicon4.dll', 'BINARY')
('_hashlib', 'C:\\progra~1\\python27\\DLLs\\_hashlib.pyd', 'EXTENSION')
('qt4_plugins\\codecs\\qcncodecs4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\codecs\\qcncodecs4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qico4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qico4.dll', 'BINARY')
('qt4_plugins\\accessible\\qtaccessiblewidgets4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\accessible\\qtaccessiblewidgets4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qmng4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qmng4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qjpeg4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qjpeg4.dll', 'BINARY')
('qt4_plugins\\codecs\\qjpcodecs4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\codecs\\qjpcodecs4.dll', 'BINARY')
('qt4_plugins\\codecs\\qtwcodecs4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\codecs\\qtwcodecs4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qtga4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qtga4.dll', 'BINARY')
('qt4_plugins\\graphicssystems\\qglgraphicssystem4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\graphicssystems\\qglgraphicssystem4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qtiff4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qtiff4.dll', 'BINARY')
('qt4_plugins\\codecs\\qkrcodecs4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\codecs\\qkrcodecs4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qsvg4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qsvg4.dll', 'BINARY')
('qt4_plugins\\imageformats\\qgif4.dll', 'C:\\progra~1\\python27\\Lib\\site-packages\\PyQt4\\plugins\\imageformats\\qgif4.dll', 'BINARY')
('PyQt4.QtCore', 'C:\\progra~1\\python27\\lib\\site-packages\\PyQt4\\QtCore.pyd', 'EXTENSION')
('unicodedata', 'C:\\progra~1\\python27\\DLLs\\unicodedata.pyd', 'EXTENSION')
('bz2', 'C:\\progra~1\\python27\\DLLs\\bz2.pyd', 'EXTENSION')
('_ctypes', 'C:\\progra~1\\python27\\DLLs\\_ctypes.pyd', 'EXTENSION')
('_ssl', 'C:\\progra~1\\python27\\DLLs\\_ssl.pyd', 'EXTENSION')
('win32evtlog', 'C:\\progra~1\\python27\\lib\\site-packages\\win32\\win32evtlog.pyd', 'EXTENSION')
('win32api', 'C:\\progra~1\\python27\\lib\\site-packages\\win32\\win32api.pyd', 'EXTENSION')
('_socket', 'C:\\progra~1\\python27\\DLLs\\_socket.pyd', 'EXTENSION')
('QtSvg4.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\qtsvg4.dll', 'BINARY')
('select', 'C:\\progra~1\\python27\\DLLs\\select.pyd', 'EXTENSION')
('QtOpenGL4.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\qtopengl4.dll', 'BINARY')
('QtXml4.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\qtxml4.dll', 'BINARY')
('shiboken-python2.7.dll', 'C:\\progra~1\\python27\\lib\\site-packages\\PySide\\shiboken-python2.7.dll', 'BINARY')
('pywintypes27.dll', 'C:\\WINDOWS\\system32\\pywintypes27.dll', 'BINARY')             
'''

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
    