if ! pip show pyinstaller > /dev/null 2>&1; then
  pip install -U pyinstaller
fi
[ -f ./dist/lipysync.exe ] && rm ./dist/lipysync.exe
pyinstaller --onefile --workpath ./build --distpath ./dist --name lipysync --icon=lipysync.ico main.py
./dist/lipysync.exe -v
