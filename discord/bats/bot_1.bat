:: get back to main directory
cd ../..
:: call the venv
call maintenance/virtual-env/Scripts/activate
:: redirect back to python files
cd discord
:: run bot_1
python -m bot_1.py