import threading
import sounddevice as sd
import soundfile as sf


class AudioCapture:
    running_queue = []
    ready_queue = []

    def __init__(self,
                 filename: str,
                 sr: int,
                 channel_num: int):
        self.filename = filename
        self.sr = sr
        self.channel_num = channel_num
        self.is_listening = False
        self.capture_audio = False
        self.is_ready = True
        self.is_running = False

    def _listen(self, duration: int):
        self.is_listening = True
        recording = sd.rec((duration * self.sr), samplerate=self.sr, channels=self.channel_num)
        sd.wait()
        self.is_listening = False
        sf.write(self.filename, recording, self.sr, subtype='PCM_16')
        self.is_running = False
        self.is_ready = True

    def listen(self, duration: int):
        while self.capture_audio:
            if not self.is_listening and self.is_running:
                thr = threading.Thread(target=self._listen, args=(duration, ), name='_listen')
                thr.start()
                thr.join()