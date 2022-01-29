set -e
pip install python-telegram-bot
if  ! pgrep -x "python3" > /dev/null
then
    echo "Stopped"
    cd /workspace
    ls -l
    python3 bot.py || true
    echo "Started";
fi

