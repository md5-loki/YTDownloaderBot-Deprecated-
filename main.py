# -- Imports -- #

from pytube import YouTube, exceptions, Playlist
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import logging
import os
import time
from dotenv import load_dotenv

# -- The correct way to import a token stored in .env file -- #
# -- It configures your local enviromental variable and merge to the enviromental variable tree -- #
load_dotenv() 
token = os.getenv('token')

# -- Basic Setup -- #
updater = Updater(token, use_context=True)
dispatcher = updater.dispatcher
SONG = 0
PLAYLIST = 0
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
bot_greeting = "*Hi, I'm the Youtube Downloader bot\nRun */download *to start downloading your favorite music\nIf I somehow misbehave contact my maker from the profile info*"

wait = "*Wait\.\.\.*"
working = "*Working on it\.\.\.*"
done = "*Done* ✅ *Sending ✉*"
ins = " *Detailed instructions*\n/download \- Will ask for a youtube link to work with\n/playlist \- Will ask for a youtube playlist link to work with"
# -- Main Commands -- #
def start(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = bot_greeting, parse_mode='MarkdownV2')

def instructions(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = ins, parse_mode='MarkdownV2')

def get_song(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Send me the link you wish to download!")
    # -- Hold value to use in Conversation Handler -- #
    return SONG

def get_playlist(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Send me the link of the playlist you wish to download!")
    # -- Hold value to use in Conversation Handler -- #
    return PLAYLIST
 
def download(update, context):
    # -- Get video info -- #
    try:
        video = YouTube(update.message.text)
        audio = video.streams.filter(only_audio=True).first()
        title = video.title.translate(str.maketrans('','',".,'?#|"))
        
        # -- Check if video reaches 10 minutes (600 sec == 10 min) -- #
        if(video.length < 600):
        # -- Download audio stream and change its extension --  #
            pre = audio.download()
            post = os.path.splitext(pre)[0]
            os.rename(pre, post + '.mp3')

            context.bot.send_message(chat_id = update.effective_chat.id, text = wait, parse_mode='MarkdownV2')
            time.sleep(2)
            context.bot.send_message(chat_id = update.effective_chat.id, text = working, parse_mode='MarkdownV2')
            time.sleep(2)
            context.bot.send_message(chat_id = update.effective_chat.id, text = done, parse_mode='MarkdownV2') 
            time.sleep(2)
            context.bot.send_audio(chat_id = update.effective_chat.id, audio = open(title + '.mp3', 'rb'))
            
            # -- Wait 1 seconds then delete the video file -- #
            time.sleep(1)
            os.remove(title + '.mp3')
            # -- End the conversation handler since input is not expected or alredy given -- #
            return ConversationHandler.END
            # -- Check if a valid link has been received -- #
        else:
            context.bot.send_message(chat_id = update.effective_chat.id, text = 'Video limit is 10 Minutes (storage), give me another link') 

    except exceptions.RegexMatchError as e:
        context.bot.send_message(chat_id = update.effective_chat.id, text = "Send me a valid link, please run /download again")
        return ConversationHandler.END

def playlist(update, context):

    try:
        playlist = Playlist(update.message.text)
        playlistLength = len(playlist.video_urls)
        context.bot.send_message(chat_id = update.effective_chat.id, text = "*Your songs will be deliveried one by one ASAP ✉, please be patient ❤*", parse_mode='MarkdownV2')

        if playlistLength <= 25:
            for song in playlist.videos[:playlistLength]:
                title = song.title.translate(str.maketrans('','',".,'?#|"))
                audio = song.streams.filter(only_audio=True).first()

                pre = audio.download()
                post = os.path.splitext(pre)[0]
                os.rename(pre, post + '.mp3')

                context.bot.send_audio(chat_id = update.effective_chat.id, audio = open(title + '.mp3', 'rb'))

                time.sleep(1)
                os.remove(title + '.mp3')
        else:
            context.bot.send_message(chat_id = update.effective_chat.id, text = "Playlist must be 25 songs max (storage), give me another link")
    
    except:
            context.bot.send_message(chat_id = update.effective_chat.id, text = "Send me a valid playlist link, please run /playlist again")
            return ConversationHandler.END

start_handler = CommandHandler('start', start)
instructions_handler = CommandHandler('instructions', instructions)
dispatcher.add_handler(start_handler)
dispatcher.add_handler(instructions_handler)

dispatcher.add_handler(ConversationHandler(
    entry_points=[
        CommandHandler('download', get_song)
    ],

    states={
        SONG: [MessageHandler(Filters.text, download)]
    },

    fallbacks=[],
))

dispatcher.add_handler(ConversationHandler(
     entry_points=[
        CommandHandler('playlist', get_playlist)
    ],

    states={
        PLAYLIST: [MessageHandler(Filters.text, playlist)]
    },

    fallbacks=[],
))

updater.start_polling()
