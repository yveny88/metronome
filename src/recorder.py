import os
import datetime
import queue

import numpy as np
import pygame
import sounddevice as sd
import soundfile as sf


_fs = 44100
_queue = queue.Queue()
_stream = None
_frames = []
_last_path = None


def _callback(indata, frames, time, status):
    if status:
        print(status, flush=True)
    _queue.put(indata.copy())


def start_recording():
    """Start capturing audio."""
    global _stream, _frames
    _frames = []
    _stream = sd.InputStream(samplerate=_fs, channels=1, callback=_callback)
    _stream.start()


def stop_recording():
    """Stop recording and save the WAV file."""
    global _stream, _last_path
    if _stream is None:
        return None
    _stream.stop()
    _stream.close()
    _stream = None

    while not _queue.empty():
        _frames.append(_queue.get())

    if not _frames:
        return None

    audio = np.concatenate(_frames, axis=0)
    os.makedirs("recordings", exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    _last_path = os.path.join("recordings", f"recording_{timestamp}.wav")
    sf.write(_last_path, audio, _fs)
    return _last_path


def play_recording():
    """Play back the last recorded audio file."""
    if not _last_path or not os.path.exists(_last_path):
        return
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    sound = pygame.mixer.Sound(_last_path)
    sound.play()
