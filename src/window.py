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

from gi.repository import Gtk
from gi.repository import GLib
from gi.repository import Gio
from gi.repository import Gdk
import youtube_dl
import threading
import os

class ydl_logger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        print(msg)

@Gtk.Template(resource_path='/com/github/copperly123/easydl/window.ui')

class EasydlGuiWindow(Gtk.ApplicationWindow):
    __gtype_name__ = 'EasydlGuiWindow'

    download_button = Gtk.Template.Child()
    download_format_combo_box = Gtk.Template.Child()
    file_format_combo_box = Gtk.Template.Child()
    output_folder_file_selector = Gtk.Template.Child()
    playlist_mode_switch = Gtk.Template.Child()
    url_entry_box = Gtk.Template.Child()
    url_preview_label = Gtk.Template.Child()
    download_progress_bar = Gtk.Template.Child()
    main_menu_about_button = Gtk.Template.Child()
    download_progress_label = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.download_button.connect('clicked', self.on_download_button_press)
        self.output_folder_file_selector.connect("file-set", self.get_output_folder)
        self.download_format_combo_box.connect("changed", self.get_download_format)
        self.file_format_combo_box.connect("changed", self.get_file_format)
        self.playlist_mode_switch.connect("notify::active", self.get_playlist_mode)
        self.url_entry_box.connect("changed", self.get_url)
        self.url_entry_box.connect("activate", self.get_url)
        self.main_menu_about_button.connect("clicked", self.show_about_dialog)
        #self.url_entry_box.connect("icon-press", self.get_url, Gtk.EntryIconPosition.SECONDARY)

        global ydl_opts
        global playlistMode
        global downloadFilename
        global currentDownload
        #flags to enable download button
        global downloadFormatReady
        global fileFormatReady
        global outputFolderReady
        global urlReady
        ydl_opts = {"noplaylist": True}
        playlistMode = False
        downloadFilename = "unset"
        currentDownload = 1
        downloadFormatReady = False
        fileFormatReady = False
        outputFolderReady = False
        urlReady = False

        #gtk_widget_set_sensitive(self.download_button, False)
        self.download_button.set_sensitive(False)


    def get_download_format(self, download_format_combo_box):
        global downloadFormatReady
        global fileFormatReady
        global outputFolderReady
        global urlReady
        #code to change the format to download in (video or audio)
        global downloadFormat
        downloadFormat = download_format_combo_box.get_active_text()
        # print(downloadFormat)

        #change the options available in file_format_combo_box
        global videoFileExtensions
        global audioFileFormats
        videoFileExtensions = {'mp4 (file extension)': 'mp4', 'webm (file extension)' : 'webm'}
        audioFileFormats = {'best (gives best possible format)': 'best', 'aac': 'aac', 'flac': 'flac', 'mp3': 'mp3', 'm4a': 'm4a', 'opus': 'opus', 'vorbis': 'vorbis', 'wav': 'wav'}
        #remove all previous entries
        self.file_format_combo_box.remove_all()
        #add new entries
        if downloadFormat == 'Video':
            #populate the combo box with the descriptive version of the extensions
            for file_format in videoFileExtensions.keys():
                self.file_format_combo_box.append_text(file_format)
        else:
            #populate the combo box with the descriptive version of the formats
            for file_format in audioFileFormats.keys():
                self.file_format_combo_box.append_text(file_format)
        #the active entry will automatically be cleared
        fileFormatReady = False
        self.download_button.set_sensitive(False)
        downloadFormatReady = True
        print("downloadFormatReady")
        if downloadFormatReady and fileFormatReady and outputFolderReady and urlReady:
            self.download_button.set_sensitive(True)

    def get_file_format(self, file_format_combo_box):
        #code to change the file format to download in
        global downloadFileFormat
        global downloadFormatReady
        global fileFormatReady
        global outputFolderReady
        global urlReady
        if downloadFormat == 'Video':
            downloadFileFormat = videoFileExtensions.get(file_format_combo_box.get_active_text(), 'mp4')
        else:
            downloadFileFormat = audioFileFormats.get(file_format_combo_box.get_active_text(), 'mp3')
        fileFormatReady = True
        print("fileFormatReady")
        if downloadFormatReady and fileFormatReady and outputFolderReady and urlReady:
            self.download_button.set_sensitive(True)

    def get_output_folder(self, output_folder_file_selector):
        #get the folder that the user chose and store it in outputFolder
        global outputFolder
        global outputFormatYoutube
        global downloadFormatReady
        global fileFormatReady
        global outputFolderReady
        global urlReady
        outputFolder = output_folder_file_selector.get_filename()
        outputFolder = outputFolder + "/"
        outputFormatYoutube = outputFolder + u'%(title)s.%(ext)s'
        print("outputFolderReady")
        outputFolderReady = True
        if downloadFormatReady and fileFormatReady and outputFolderReady and urlReady:
            self.download_button.set_sensitive(True)

    def get_playlist_mode(self, playlist_mode_switch, gparam):
        #code to chose wheter the user wants to download a playlist or not
        # plyalistModeBool = playlist_mode_switch.get_state()
        global playlistMode
        global downloadFormatReady
        global fileFormatReady
        global outputFolderReady
        global urlReady
        if playlist_mode_switch.get_active():
            playlistMode = True
            ydl_opts.update({"noplaylist": False})
            self.get_url(self.url_entry_box)
            # print(ydl_opts["noplaylist"])
        else:
            playlistMode = False
            ydl_opts.update({"noplaylist": True})
            self.get_url(self.url_entry_box)
            # print(ydl_opts["noplaylist"])
        # print(playlistMode)

    def get_url(self, url_entry_box):
        #code to get the url that the user inputed
        global downloadUrl
        downloadUrl=url_entry_box.get_text()
        # print(downloadUrl)

        def preview_label_thread_function():
            global playlistSize
            global downloadFormatReady
            global fileFormatReady
            global outputFolderReady
            global urlReady
            #code to set the preview label
            if playlistMode:
                # ydl_opts_playlist_title = {"playlist_items": "1"}
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    playlistMetadata = ydl.extract_info(downloadUrl, download=False)
                    playlistSize = len(playlistMetadata['entries'])
                self.url_preview_label.set_text(playlistMetadata['title'])
                # gtk_widget_set_sensitive(self.download_button, True)
                urlReady = True
                print("urlReady")
                if downloadFormatReady and fileFormatReady and outputFolderReady and urlReady:
                    self.download_button.set_sensitive(True)
            else:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    videoMetadata = ydl.extract_info(downloadUrl, download=False)
                self.url_preview_label.set_text(videoMetadata['title'])
                # gtk_widget_set_sensitive(self.download_button, True)
                urlReady = True
                print("urlReady")
                if downloadFormatReady and fileFormatReady and outputFolderReady and urlReady:
                    self.download_button.set_sensitive(True)
        global preview_label_thread
        preview_label_thread = threading.Thread(target=preview_label_thread_function)
        preview_label_thread.start()

    def set_download_progress(self, progressDictionary):
        global currentDownload
        global playlistSize
        global downloadFilename
        if playlistMode:
            if progressDictionary['status'] == 'downloading':
                if downloadFilename == "unset":
                    downloadFilename = progressDictionary['filename']
                    self.download_progress_label.set_text("Downloading {0}/{1} - {2}".format(currentDownload, playlistSize, os.path.basename(progressDictionary['filename'])))

                elif downloadFilename != progressDictionary['filename']:
                    currentDownload += 1
                    downloadFilename = progressDictionary['filename']
                    self.download_progress_label.set_text("Downloading {0}/{1} - {2}".format(currentDownload, playlistSize, os.path.basename(progressDictionary['filename'])))
                progress = progressDictionary['downloaded_bytes'] / progressDictionary['total_bytes'] - 0.1
                self.download_progress_bar.set_fraction(progress)
        else:
            if progressDictionary['status'] == 'downloading':
                progress = progressDictionary['downloaded_bytes'] / progressDictionary['total_bytes'] - 0.1
                self.download_progress_bar.set_fraction(progress)
                if self.download_progress_label.get_text() != "Downloading {0}".format(os.path.basename(progressDictionary['filename'])):
                    self.download_progress_label.set_text("Downloading {0}".format(os.path.basename(progressDictionary['filename'])))
    def on_download_button_press(self, download_button):
        #code to be execute once the download button is pressed
        if downloadFormat == 'Video':
            #video
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
            #audio
            ydl_opts.update({'format': 'bestaudio/best'})
            ydl_opts.update({'outtmpl': outputFormatYoutube})
            ydl_opts.update({'logger': ydl_logger()})
            ydl_opts.update({'progress_hooks': [self.set_download_progress]})
            ydl_opts.update({'prefer_ffmpeg': True})
            ydl_opts.update({'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': downloadFileFormat, 'preferredquality': '320'}]})

            def youtube_audio_thread_function():
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([downloadUrl])
                GLib.idle_add(self.youtube_audio_complete)


            global youtube_audio_thread
            youtube_audio_thread = threading.Thread(target=youtube_audio_thread_function)
            youtube_audio_thread.start()

            # gtk_widget_set_sensitive(self.download_button, False)
        self.download_button.set_sensitive(False)

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
        self.download_progress_label.set_text("Download complete")
        self.download_progress_bar.set_fraction(1)
        self.show_download_message_dialog()
        self.download_progress_bar.set_fraction(0)
        self.download_progress_label.set_text("Fill out all options then press Download")

    def youtube_video_complete(self):
        self.download_progress_label.set_text("Download complete")
        self.download_progress_bar.set_fraction(1)
        self.show_download_message_dialog()
        self.download_progress_bar.set_fraction(0)
        self.download_progress_label.set_text("Fill out all options then press Download")
