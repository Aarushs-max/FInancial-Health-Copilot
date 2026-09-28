@echo off
echo ===================================================================
echo  Financial Health Copilot - HackMatrix 5.0 (FIN-02)
echo ===================================================================
echo.
echo Starting FastAPI application server on http://127.0.0.1:8000
echo Interactive Swagger Docs available at http://127.0.0.1:8000/docs
echo.
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
pause
