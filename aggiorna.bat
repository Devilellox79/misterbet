@echo off
echo ============================================
echo   MisterBet - Aggiornamento giornaliero
echo ============================================
echo.
echo [1/4] Scaricamento partite...
python backend/services/fetch_live_odds.py
echo.
echo [2/4] Calcolo pronostici...
python backend/services/generate_app_data.py
echo.
echo [3/4] Copia file nel frontend...
copy backend\data\app_data.json frontend\app_data.json
echo.
echo [4/4] Caricamento su GitHub...
git add frontend/app_data.json
git commit -m "Aggiornamento dati giornaliero"
git push
echo.
echo ============================================
echo   Fatto! Netlify si aggiornera' in 30 sec.
echo ============================================
pause