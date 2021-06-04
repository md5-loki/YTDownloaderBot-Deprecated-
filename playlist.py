from telegram.ext import ConversationHandler
from pytube import Playlist
import os, time

PLAYLIST = 0

def get_playlist(update, context):
    context.bot.send_message(chat_id = update.effective_chat.id, text = "Send me the link of the playlist you wish to download!")
    # -- Hold value to use in Conversation Handler -- #
    return PLAYLIST
 
def playlist(update, context):

    try:
        playlist = Playlist(update.message.text)
        playlistLength = len(playlist.video_urls)
        
        if playlistLength <= 25:
            context.bot.send_message(chat_id = update.effective_chat.id, text = "*Your songs will be deliveried one by one ASAP ✉, please be patient ❤*", parse_mode='MarkdownV2')

            for song in playlist.videos[:playlistLength]:
                title = song.title.translate(str.maketrans('','',f"'#$%*.,\/:;<>?^|~\""))
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