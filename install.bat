@echo off
::Script to generate shortcut

set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"

echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%
echo sLinkFile = "quicklooks.lnk" >> %SCRIPT%
echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%
echo oLink.TargetPath = "%~dp0quicklooks.bat" >> %SCRIPT%
echo oLink.Save >> %SCRIPT%

cscript /nologo %SCRIPT%
del %SCRIPT%
copy quicklooks.lnk %userprofile%\Desktop
pip install -r requirements.txt

if errorlevel 9009 (
	set SCRIPT="%TEMP%\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"
	echo MsgBox "Error: Can't find Python 3 installation. Please install Python 3 from " >> %SCRIPT%
	cscript /nologo %SCRIPT%
	del %SCRIPT%
)
