#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pygame import mixer
from mutagen.mp3 import MP3
import time
import json
import sys

class ModernMusicPlayer:
    VERSION = "1.2.0"
    PLAYLIST_FILE = os.path.expanduser("~/.music_player_playlist.json")
    
    def __init__(self, root):
        self.root = root
        self.root.title(f"🎵 Modern Music Player v{self.VERSION}")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        mixer.init()
        
        self.current_song = None
        self.paused = False
        self.playing = False
        self.song_length = 0
        self.current_time = 0
        self.playlist = []
        self.current_index = -1
        
        self.setup_styles()
        self.create_widgets()
        self.setup_hotkeys()
        self.load_playlist()
        self.update_time()
        self.check_song_end()
        
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_styles(self):
        self.root.configure(bg='#1a1a1a')
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background='#1a1a1a')
        style.configure('TLabel', background='#1a1a1a', foreground='#ffffff')
        
    def setup_hotkeys(self):
        self.root.bind('<Left>', lambda e: self.volume_down())
        self.root.bind('<Right>', lambda e: self.volume_up())
        self.root.bind('<space>', lambda e: self.toggle_play_pause())
        self.root.bind('<Up>', lambda e: self.next_song())
        self.root.bind('<Down>', lambda e: self.prev_song())
        self.root.bind('<Control-s>', lambda e: self.save_playlist())
        
    def create_widgets(self):
        # Верхняя панель
        top_frame = tk.Frame(self.root, bg='#2d2d2d', height=100)
        top_frame.pack(fill='x')
        top_frame.pack_propagate(False)
        
        title_frame = tk.Frame(top_frame, bg='#2d2d2d')
        title_frame.pack(pady=20)
        
        title_label = tk.Label(title_frame, text="🎵 Music Player", 
                               font=('Arial', 24, 'bold'),
                               bg='#2d2d2d', fg='#ffffff')
        title_label.pack(side='left')
        
        version_label = tk.Label(title_frame, text=f" v{self.VERSION}", 
                                font=('Arial', 14, 'bold'),
                                bg='#2d2d2d', fg='#4CAF50')
        version_label.pack(side='left')
        
        # Основной контейнер
        main_container = tk.Frame(self.root, bg='#1a1a1a')
        main_container.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Левая панель - плейлист
        left_panel = tk.Frame(main_container, bg='#2d2d2d')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        playlist_label = tk.Label(left_panel, text="📋 Плейлист", 
                                  font=('Arial', 14, 'bold'),
                                  bg='#2d2d2d', fg='#ffffff')
        playlist_label.pack(pady=10)
        
        self.playlist_box = tk.Listbox(left_panel, bg='#1a1a1a', fg='#ffffff',
                                       selectbackground='#3d3d3d',
                                       selectforeground='#ffffff',
                                       font=('Arial', 11),
                                       height=15)
        self.playlist_box.pack(fill='both', expand=True, padx=10, pady=10)
        self.playlist_box.bind('<Double-Button-1>', self.play_selected)
        
        # Кнопки
        buttons_frame = tk.Frame(left_panel, bg='#2d2d2d')
        buttons_frame.pack(pady=10)
        
        add_btn = tk.Button(buttons_frame, text="➕ Добавить", command=self.add_songs,
                           bg='#4CAF50', fg='white', font=('Arial', 10, 'bold'),
                           padx=15, pady=5, borderwidth=0)
        add_btn.pack(side='left', padx=5)
        
        remove_btn = tk.Button(buttons_frame, text="❌ Удалить", command=self.remove_song,
                              bg='#f44336', fg='white', font=('Arial', 10, 'bold'),
                              padx=15, pady=5, borderwidth=0)
        remove_btn.pack(side='left', padx=5)
        
        clear_btn = tk.Button(buttons_frame, text="🗑 Очистить", command=self.clear_playlist,
                             bg='#ff9800', fg='white', font=('Arial', 10, 'bold'),
                             padx=15, pady=5, borderwidth=0)
        clear_btn.pack(side='left', padx=5)
        
        # Правая панель
        right_panel = tk.Frame(main_container, bg='#2d2d2d')
        right_panel.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.now_playing = tk.Label(right_panel, text="Сейчас не играет", 
                                   font=('Arial', 12, 'italic'),
                                   bg='#2d2d2d', fg='#aaaaaa')
        self.now_playing.pack(pady=20)
        
        # Прогресс
        self.time_label = tk.Label(right_panel, text="0:00 / 0:00",
                                  bg='#2d2d2d', fg='#ffffff')
        self.time_label.pack()
        
        self.progress = ttk.Progressbar(right_panel, length=400, mode='determinate')
        self.progress.pack(pady=10)
        
        # Кнопки управления
        controls = tk.Frame(right_panel, bg='#2d2d2d')
        controls.pack(pady=20)
        
        prev_btn = tk.Button(controls, text="⏮", command=self.prev_song,
                            bg='#3d3d3d', fg='white', font=('Arial', 15, 'bold'),
                            padx=20, pady=10, borderwidth=0)
        prev_btn.pack(side='left', padx=5)
        
        self.play_btn = tk.Button(controls, text="▶", command=self.toggle_play_pause,
                                 bg='#2196F3', fg='white', font=('Arial', 15, 'bold'),
                                 padx=30, pady=10, borderwidth=0)
        self.play_btn.pack(side='left', padx=5)
        
        next_btn = tk.Button(controls, text="⏭", command=self.next_song,
                            bg='#3d3d3d', fg='white', font=('Arial', 15, 'bold'),
                            padx=20, pady=10, borderwidth=0)
        next_btn.pack(side='left', padx=5)
        
        stop_btn = tk.Button(controls, text="⏹", command=self.stop_song,
                            bg='#f44336', fg='white', font=('Arial', 15, 'bold'),
                            padx=20, pady=10, borderwidth=0)
        stop_btn.pack(side='left', padx=5)
        
        # Громкость
        volume_frame = tk.Frame(right_panel, bg='#2d2d2d')
        volume_frame.pack(pady=10)
        
        tk.Label(volume_frame, text="🔊", bg='#2d2d2d', fg='white').pack(side='left')
        
        self.volume = tk.Scale(volume_frame, from_=0, to=100, orient='horizontal',
                              length=200, bg='#2d2d2d', fg='white',
                              troughcolor='#1a1a1a', command=self.change_volume)
        self.volume.set(70)
        self.volume.pack(side='left', padx=5)
        
        self.volume_label = tk.Label(volume_frame, text="70%", bg='#2d2d2d', fg='#4CAF50')
        self.volume_label.pack(side='left')
        
        # Статус
        self.status = tk.Label(right_panel, text="Готов", bg='#2d2d2d', fg='#888888')
        self.status.pack(pady=10)
        
    def save_playlist(self):
        try:
            with open(self.PLAYLIST_FILE, 'w') as f:
                json.dump({
                    'playlist': self.playlist,
                    'volume': self.volume.get()
                }, f)
            self.status.config(text="✅ Плейлист сохранён")
        except:
            pass
            
    def load_playlist(self):
        try:
            if os.path.exists(self.PLAYLIST_FILE):
                with open(self.PLAYLIST_FILE, 'r') as f:
                    data = json.load(f)
                self.playlist = [s for s in data.get('playlist', []) if os.path.exists(s)]
                for song in self.playlist:
                    self.playlist_box.insert(tk.END, os.path.basename(song))
                self.volume.set(data.get('volume', 70))
                self.change_volume(self.volume.get())
        except:
            pass
            
    def add_songs(self):
        files = filedialog.askopenfilenames(filetypes=[("Audio", "*.mp3 *.wav *.ogg")])
        for f in files:
            if f not in self.playlist:
                self.playlist.append(f)
                self.playlist_box.insert(tk.END, os.path.basename(f))
        if files:
            self.save_playlist()
            self.status.config(text=f"✅ Добавлено {len(files)} песен")
            
    def remove_song(self):
        sel = self.playlist_box.curselection()
        if sel:
            self.playlist.pop(sel[0])
            self.playlist_box.delete(sel[0])
            self.save_playlist()
            
    def clear_playlist(self):
        self.playlist.clear()
        self.playlist_box.delete(0, tk.END)
        self.stop_song()
        self.save_playlist()
        
    def play_selected(self, event):
        sel = self.playlist_box.curselection()
        if sel:
            self.current_index = sel[0]
            self.play_song()
            
    def play_song(self):
        if 0 <= self.current_index < len(self.playlist):
            song = self.playlist[self.current_index]
            mixer.music.load(song)
            mixer.music.play()
            self.playing = True
            self.paused = False
            self.play_btn.config(text="⏸")
            self.now_playing.config(text=f"🎵 {os.path.basename(song)}")
            try:
                self.song_length = MP3(song).info.length
            except:
                self.song_length = 0
            self.playlist_box.selection_clear(0, tk.END)
            self.playlist_box.selection_set(self.current_index)
            
    def toggle_play_pause(self):
        if self.playing:
            if self.paused:
                mixer.music.unpause()
                self.paused = False
                self.play_btn.config(text="⏸")
            else:
                mixer.music.pause()
                self.paused = True
                self.play_btn.config(text="▶")
        elif self.playlist:
            self.current_index = 0
            self.play_song()
            
    def stop_song(self):
        mixer.music.stop()
        self.playing = False
        self.paused = False
        self.play_btn.config(text="▶")
        self.now_playing.config(text="Сейчас не играет")
        self.progress['value'] = 0
        
    def next_song(self):
        if self.playlist and self.current_index < len(self.playlist) - 1:
            self.current_index += 1
            self.play_song()
            
    def prev_song(self):
        if self.playlist and self.current_index > 0:
            self.current_index -= 1
            self.play_song()
            
    def change_volume(self, val):
        mixer.music.set_volume(int(val) / 100)
        self.volume_label.config(text=f"{int(val)}%")
        
    def volume_up(self):
        self.volume.set(min(100, self.volume.get() + 10))
        
    def volume_down(self):
        self.volume.set(max(0, self.volume.get() - 10))
        
    def check_song_end(self):
        if self.playing and not self.paused and not mixer.music.get_busy():
            self.next_song()
        self.root.after(1000, self.check_song_end)
        
    def update_time(self):
        if self.playing and not self.paused and self.song_length:
            pos = mixer.music.get_pos() / 1000
            if pos > 0:
                self.progress['value'] = (pos / self.song_length) * 100
                self.time_label.config(text=f"{time.strftime('%M:%S', time.gmtime(pos))} / {time.strftime('%M:%S', time.gmtime(self.song_length))}")
        self.root.after(1000, self.update_time)
        
    def on_closing(self):
        self.save_playlist()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernMusicPlayer(root)
    root.mainloop()
