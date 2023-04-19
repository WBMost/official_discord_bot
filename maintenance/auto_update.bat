if exist %cd%\virtual-env\ (
    echo venv located, moving on
) else (
    echo creating venv
    python -m venv %cd%\virtual-env
)

call virtual-env/Scripts/activate

echo updating/installing python libs...
pip install -r requirements.txt

git fetch
git pull origin master