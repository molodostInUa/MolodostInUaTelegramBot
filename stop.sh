for KILLPID in `ps ax | grep -v grep | grep 'bot.py' | awk '{print $1;}'`; do kill -2 $KILLPID; done
