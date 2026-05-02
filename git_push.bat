@echo off
cd /d "C:\Users\Arthur\OneDrive\桌面\Youtube\love\love-language-site"
del /f ".git\index.lock" 2>nul
git add index.html en/index.html ja/index.html ko/index.html es/index.html images/characters/
git commit -m "feat: merge love-language & guardian sections, add char images, fix startQuiz crash"
git push --set-upstream origin main
echo.
echo Done! Check above for push result.
pause
