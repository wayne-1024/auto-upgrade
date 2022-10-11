CD /D %~dp0

rmdir /s /q App
mkdir App

copy App1.0\App.* App\App.*

pause