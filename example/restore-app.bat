CD /D %~dp0

rmdir /s /q App
mkdir App

copy App1.0\App.* App\App.*
copy tools\update\update_gui.exe App\update_gui.exe
copy tools\update\update.ini App\update.ini

pause