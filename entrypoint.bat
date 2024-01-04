setlocal
@REM Incase you want to use this entrypoint
@REM set "TOKEN=YOUR_TOKEM"
@REM set "EVENT_CHANNEL=YOUR_EVENT_CHANNEL_ID"
if exist .venv\Scripts\activate (
    call .venv\Scripts\activate
    python main.py
) else (
    echo Virtual environment not found. Creating new virtual environment.
    call python -m venv .venv
    echo Acvtivating virtual environment
    call .venv\Scripts\activate
    echo downloading depenencies
    call python.exe -m pip install --upgrade pip
    call pip install discord
    python main.py
)
endlocal