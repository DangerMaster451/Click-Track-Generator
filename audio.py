import math
from gtts import gTTS
from pydub import AudioSegment

class Click():
    def __init__(self, sample_rate=44100, high_pitch=2093.005, low_pitch=1046.502, warning_pitch=1975.533):
        self.sample_rate = sample_rate
        self.high_pitch = high_pitch
        self.low_pitch = low_pitch

    def sine_wave(self, frequency, duration):
        for frame in range(round(duration * self.sample_rate)):
            time = frame / self.sample_rate
            amplitude = 1/((frequency * 2 * time+1)) * math.sin(2 * math.pi * frequency * time)
            yield math.floor((amplitude + 1)/2 * 255)

    def generate_measure(self, wav_file, tempo:int, beats:int, sub:int) -> None:
        beat_duration = 60/tempo/(sub/4)
        wav_file.writeframes(bytes(self.sine_wave(self.low_pitch, beat_duration))) # write beat 1
        for beat in range(0, int((beats)*(sub/4))-1):
            wav_file.writeframes(bytes(self.sine_wave(self.high_pitch, beat_duration))) # write rest of beats

    def generate_beat(self, wav_file, tempo:float, sub:int, beat_type:str):
        beat_duration = 60/tempo/(sub/4)
        if beat_type == "high":
            wav_file.writeframes(bytes(self.sine_wave(self.high_pitch, beat_duration)))
        elif beat_type == "low":
            wav_file.writeframes(bytes(self.sine_wave(self.low_pitch, beat_duration)))

class Cue():
    def create_cue(text) -> str:
        gTTS(text=text, lang="en").save(f"{text}.wav")
        return f"{text}.wav"

    def mix_in_cue(cue_file:str, track_file:str, out_file:str, delay:float) -> None:
        cue_audio = AudioSegment.from_file(cue_file)
        track_audio = AudioSegment.from_file(track_file)

        mixed = track_audio.overlay(cue_audio, position=delay)
        mixed.export(out_file, format='wav')