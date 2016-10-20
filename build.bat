rm -rf build/*
rm -rf dist/*
pyinstaller --onefile --name apropy --icon apropy.ico -w apropy.spec
pause