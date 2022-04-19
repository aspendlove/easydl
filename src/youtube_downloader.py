# window.py
#
# Copyright 2021 Aidan Spendlove
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi.repository
# from gi.repository import GLib
# from gi.repository import Gio
import youtube_dl
import threading

from gi.repository import Gtk, GLib, Gio


class ydl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)


class YoutubeDownloader():
    __ydl_opts = {"noplaylist": True}
    videoFileExtensions = {'mp4 (file extension)': 'mp4', 'webm (file extension)': 'webm'}
    audioFileFormats = {'best (gives best possible format)': 'best', 'aac': 'aac', 'flac': 'flac', 'mp3': 'mp3',
                        'm4a': 'm4a', 'opus': 'opus', 'vorbis': 'vorbis', 'wav': 'wav'}
    __playlist_mode = False

    # def __init__(self):
    #

    def set_playlist_mode(self, playlist_mode):
        self.__playlist_mode = playlist_mode

    def get_playlist_mode(self):
        return self.__playlist_mode

    # def get_playlist_mode(self, playlist_mode_switch):
    #     # code to chose wheter the user wants to download a playlist or not
    #     # plyalistModeBool = playlist_mode_switch.get_state()
    #     global playlistMode
    #     if playlist_mode_switch.get_active():
    #         playlistMode = True
    #         ydl_opts.update({"noplaylist": False})
    #         # print(ydl_opts["noplaylist"])
    #     else:
    #         playlistMode = False
    #         ydl_opts.update({"noplaylist": True})
    #         # print(ydl_opts["noplaylist"])
    #     # print(playlistMode)

    def get_url(self, url_entry_box):
        # code to get the url that the user inputed
        global downloadUrl
        downloadUrl = url_entry_box.get_text()
        # print(downloadUrl)

        # code to set the preview label
        if playlistMode:
            ydl_opts_playlist_title = {"playlist_items": "1"}
            with youtube_dl.YoutubeDL(ydl_opts_playlist_title) as ydl:
                playlistTitle = ydl.extract_info(downloadUrl, download=False)
            self.url_preview_label.set_text(playlistTitle['title'])
        else:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                videoTitle = ydl.extract_info(downloadUrl, download=False)
            self.url_preview_label.set_text(videoTitle['title'])

    def set_download_progress(self, progressDictionary):
        # set the progress to be displayed on the progress bar
        if progressDictionary['status'] == 'downloading':
            # downloading
            progress = progressDictionary['downloaded_bytes'] / progressDictionary['total_bytes'] - 0.1
            # print(progress)
            self.download_progress_bar.set_fraction(progress)
        # elif progressDictionary['status'] == 'finished':
        #     if downloadFormat == 'Video':
        #         self.download_progress_bar.set_fraction(1)
        #         self.show_download_message_dialog()
        #         self.download_progress_bar.set_fraction(0)
        #     else:
        # youtube_audio_thread.join()
        #         self.download_progress_bar.set_fraction(1)
        #         self.show_download_message_dialog()
        #         self.download_progress_bar.set_fraction(0)

        elif progressDictionary['status'] == 'error':
            self.download_progress_bar.set_fraction(0)

    def on_download_button_press(self, download_button):
        # code to be execute once the download button is pressed
        if downloadFormat == 'Video':
            # video
            ydl_opts.update({'format': downloadFileFormat})
            ydl_opts.update({'outtmpl': outputFormatYoutube})
            ydl_opts.update({'logger': ydl_logger()})
            ydl_opts.update({'progress_hooks': [self.set_download_progress]})

            def youtube_video_thread_function():
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([downloadUrl])
                GLib.idle_add(self.youtube_video_complete)

            global youtube_video_thread
            youtube_video_thread = threading.Thread(target=youtube_video_thread_function)
            youtube_video_thread.start()

        else:
            # audio
            ydl_opts.update({'format': 'bestaudio/best'})
            ydl_opts.update({'outtmpl': outputFormatYoutube})
            ydl_opts.update({'logger': ydl_logger()})
            ydl_opts.update({'progress_hooks': [self.set_download_progress]})
            ydl_opts.update({'prefer_ffmpeg': True})
            ydl_opts.update({'postprocessors': [
                {'key': 'FFmpegExtractAudio', 'preferredcodec': downloadFileFormat, 'preferredquality': '320'}]})

            def youtube_audio_thread_function():
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([downloadUrl])
                GLib.idle_add(self.youtube_audio_complete)

            global youtube_audio_thread
            youtube_audio_thread = threading.Thread(target=youtube_audio_thread_function)
            youtube_audio_thread.start()

    def show_about_dialog(self, main_menu_about_button):
        builder = Gtk.Builder.new_from_resource('/com/github/copperly123/easydl/about_dialog.ui')
        dialog = builder.get_object('about_dialog')
        dialog.run()
        dialog.destroy()

    def show_download_message_dialog(self):
        builder = Gtk.Builder.new_from_resource('/com/github/copperly123/easydl/download_message_dialog.ui')
        dialog = builder.get_object('download_message_dialog')
        dialog.run()
        dialog.destroy()

    def youtube_audio_complete(self):
        self.download_progress_bar.set_fraction(1)
        self.show_download_message_dialog()
        self.download_progress_bar.set_fraction(0)

    def youtube_video_complete(self):
        self.download_progress_bar.set_fraction(1)
        self.show_download_message_dialog()
        self.download_progress_bar.set_fraction(0)
