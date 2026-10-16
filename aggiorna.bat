@echo off
echo ============================================
echo   MisterBet - Aggiornamento giornaliero
echo ============================================
echo.

echo [1/5] Verifica dipendenze Python...
python -m pip install -r backend/requirements.txt --quiet
echo.

echo [2/5] Scaricamento partite...
python backend/services/fetch_live_odds.py
if %errorlevel% neq 0 (
    echo ERRORE: Scaricamento partite fallito!
    pause
    exit /b 1
)
echo.

echo [3/5] Calcolo pronostici...
python backend/services/generate_app_data.py
if %errorlevel% neq 0 (
    echo ERRORE: Calcolo pronostici fallito!
    pause
    exit /b 1
)
echo.

echo [4/5] Copia file nel frontend...
copy backend\data\app_data.json frontend\app_data.json
echo.

echo [5/5] Caricamento su GitHub...
git add .
git diff --staged --quiet && (
    echo Nessun cambiamento da caricare.
) || (
    git commit -m "Aggiornamento dati giornaliero"
    git push
)
echo.

echo ============================================
echo   Fatto! Netlify si aggiornera' in 30 sec.
echo ============================================
pause