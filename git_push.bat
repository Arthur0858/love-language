@echo off
cd /d "C:\Users\Arthur\OneDrive\桌面\Youtube\love\love-language-site"
echo Cleaning up git locks...
taskkill /IM git.exe /F 2>nul
timeout /t 1 /nobreak >nul
del /f /q ".git\index.lock" 2>nul
del /f /q ".git\MERGE_HEAD" 2>nul
del /f /q ".git\MERGE_MSG" 2>nul
git merge --abort 2>nul
echo.
echo Staging all files...
git add -A
git status --short
echo.
echo Committing...
git commit -m "feat: merged result+guardian card, char images, startQuiz fix, result card redesign" 2>nul || echo (nothing new to commit)
echo.
echo Fetching remote...
git fetch origin
echo.
echo Merging remote (keeping our HTML changes)...
git merge origin/main --no-edit -X ours
echo.
echo Pushing...
git push --set-upstream origin main
echo.
echo Done! Check above for push result.
pause
