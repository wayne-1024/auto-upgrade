CD /D %~dp0

mkdir Blank

.\tools\vbuilder.exe .\Blank ^
.\App3.0 ^
.\Patch\App3.0 -v 3.0 -nf

rmdir Blank

pause