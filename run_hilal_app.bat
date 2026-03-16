@echo off

echo Starting Hilal API...
start cmd /k "cd /d C:\Users\ridou\OneDrive\Desktop\moroccan_hilal_checker && uvicorn api:app --reload"

timeout /t 3

echo Starting Flutter App...
start cmd /k "cd /d C:\Users\ridou\hilal_app && flutter run -d chrome"

pause