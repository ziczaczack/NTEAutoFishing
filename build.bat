@echo off
chcp 65001 >nul
echo ============================================
echo   打包 异环钓鱼 Bot  ->  dist\NTEFishingBot.exe
echo ============================================
echo.

python -m PyInstaller --onefile --uac-admin --name NTEFishingBot --collect-all cv2 --noconfirm main.py

echo.
if exist "dist\NTEFishingBot.exe" (
    echo [OK] 打包完成：dist\NTEFishingBot.exe
) else (
    echo [失败] 没有生成 exe，请向上翻看错误信息。
)
echo.
pause
