set -e
pip3 install python-telegram-bot
if  ! pgrep -x "python3" > /dev/null
then
    nohup python3 bot.py &
    echo "Started";
fi

