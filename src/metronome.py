import tkinter as tk
from tkinter import ttk
import pygame
import time
import threading

class Metronome:
    def __init__(self, root):
        self.root = root
        self.root.title("Metronome")
        self.root.geometry("400x300")
        
        # Initialisation de pygame pour le son
        pygame.mixer.init()
        
        # Variables
        self.bpm = tk.IntVar(value=120)
        self.is_playing = False
        self.thread = None
        
        # Création de l'interface
        self.create_widgets()
        
    def create_widgets(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Titre
        title_label = ttk.Label(main_frame, text="Metronome", font=('Helvetica', 24))
        title_label.grid(row=0, column=0, columnspan=2, pady=20)
        
        # Contrôle du BPM
        bpm_frame = ttk.Frame(main_frame)
        bpm_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Label(bpm_frame, text="BPM:").grid(row=0, column=0, padx=5)
        bpm_spinbox = ttk.Spinbox(bpm_frame, from_=40, to=208, textvariable=self.bpm, width=5)
        bpm_spinbox.grid(row=0, column=1, padx=5)
        
        # Bouton Start/Stop
        self.start_button = ttk.Button(main_frame, text="Start", command=self.toggle_metronome)
        self.start_button.grid(row=2, column=0, columnspan=2, pady=20)
        
        # Indicateur visuel
        self.indicator = ttk.Label(main_frame, text="●", font=('Helvetica', 48))
        self.indicator.grid(row=3, column=0, columnspan=2)
        self.indicator.configure(foreground='gray')
        
    def toggle_metronome(self):
        if not self.is_playing:
            self.is_playing = True
            self.start_button.configure(text="Stop")
            self.thread = threading.Thread(target=self.play_metronome)
            self.thread.daemon = True
            self.thread.start()
        else:
            self.is_playing = False
            self.start_button.configure(text="Start")
            self.indicator.configure(foreground='gray')
            
    def play_metronome(self):
        while self.is_playing:
            # Calcul du délai en fonction du BPM
            delay = 60.0 / self.bpm.get()
            
            # Jouer le son (à implémenter)
            # pygame.mixer.Sound("click.wav").play()
            
            # Mise à jour de l'indicateur visuel
            self.indicator.configure(foreground='red')
            self.root.update()
            time.sleep(delay/2)
            self.indicator.configure(foreground='gray')
            self.root.update()
            time.sleep(delay/2)

if __name__ == "__main__":
    root = tk.Tk()
    app = Metronome(root)
    root.mainloop() 