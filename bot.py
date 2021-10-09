#!/usr/bin/env python
# pylint: disable=C0116,W0613
# This program is dedicated to the public domain under the CC0 license.

import json
import logging
import os
from dataclasses import dataclass

from telegram import Update, ForceReply, User, Chat, Message
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

DEV_CHAT_ID = os.getenv("DEV_CHAT_ID")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
@dataclass
class ForwardedMessage:

    effective_user: User
    effective_chat: Chat
    effective_message: Message

    def __init__(self, update: Update):
        self.effective_user = update.effective_user
        self.effective_chat = update.effective_chat
        self.effective_message = update.effective_message

# Define a few command handlers. These usually take the two arguments update and
# context.
def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    update.message.reply_markdown_v2(
        fr'Hi {user.mention_markdown_v2()}\! Using this bot you can provide your ideas for volunteering ',
        reply_markup=ForceReply(selective=True),
    )
    fw = ForwardedMessage(update)
    context.job_queue.run_once(alarm, 1, context=(ADMIN_CHAT_ID, fw), name=str(ADMIN_CHAT_ID))


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('Help!')

def alarm(context: CallbackContext) -> None:
    """Send the alarm message."""
    job = context.job
    fw_msg = job.context[1]
    user = fw_msg.effective_user
    message = fw_msg.effective_message
    chat = fw_msg.effective_chat
    context.bot.send_message(job.context[0], text=f'Message from\n---\n{user}\n---\n{user.mention_markdown_v2()}\n---\n{message.text}\n---\n{chat}')

def send_reply_to_user(context: CallbackContext):
    job = context.job
    fw_msg = job.context[1]
    user = fw_msg.effective_user
    message = fw_msg.effective_message
    chat = fw_msg.effective_chat
    context.bot.send_message(job.context[0],
                             text=message.text)

def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    if update.effective_chat.id in [DEV_CHAT_ID]:
        logger.info(update)
    elif update.effective_chat.id in [ADMIN_CHAT_ID]:
        logger.info(update)

        if update.message.reply_to_message:
            logger.info("Reply from admin")
            response_arr = str(update.message.reply_to_message.text).split("\n---\n")
            originated_message_user_str = str(response_arr[1]).replace("\\", "").replace("\'","\"").replace("False", "false").replace("True","true")
            logger.info(originated_message_user_str)
            originated_message_user = json.loads(originated_message_user_str)

            logger.info(str(response_arr[1]) + "\n Reply to " + str(originated_message_user['id']))
            fw = ForwardedMessage(update)
            context.job_queue.run_once(send_reply_to_user, 1, context=(originated_message_user['id'], fw), name=str(originated_message_user['id']))
            context.job_queue.run_once(send_reply_to_user, 1, context=(ADMIN_CHAT_ID, fw), name=str(originated_message_user['id']))
            logger.info(str(update.message.text) + "\n Text")
        else:
            logger.info(update)
            fw = ForwardedMessage(update)
            context.job_queue.run_once(alarm, 1, context=(ADMIN_CHAT_ID, fw), name=str(ADMIN_CHAT_ID))
    else:
        update.message.reply_text("Thanks! We've got your message and will contact you further.\n")
        logger.info(update)
        fw = ForwardedMessage(update)
        context.job_queue.run_once(alarm, 1, context=(ADMIN_CHAT_ID, fw), name=str(ADMIN_CHAT_ID))


def main() -> None:
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("API_TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on non command i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
