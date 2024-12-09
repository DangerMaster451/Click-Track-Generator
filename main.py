import wave
import math
import json

sample_rate = 44100
high_pitch = 2093.005
low_pitch = 1046.502
warning_pitch = 1975.533

class Track_Section():
    def __init__(self, name, tempo, beats, sub, dur):
        self.name = name
        self.tempo = tempo
        self.beats = beats
        self.sub = sub
        self.dur = dur

class Track():
    def __init__(self, name:str, sections:list[Track_Section]):
        self.name = name
        self.sections = sections

def sin_wave(frequency, duration):
    for frame in range(round(duration * sample_rate)):
        time = frame / sample_rate
        amplitude = 1/((time+1)**5) * math.sin(2 * math.pi * frequency * time)
        yield round((amplitude + 1) /2 * 255)

def generate_measure(wav_file, beats_per_measure:int, tempo:int) -> None:
    beat_duration = 60/tempo
    wav_file.writeframes(bytes(sin_wave(high_pitch, beat_duration))) # write beat 1
    for beat in range(beats_per_measure-1):
        wav_file.writeframes(bytes(sin_wave(low_pitch, beat_duration))) # write rest of beats

def generate_warning_measure(wav_file, beats_per_measure:int, tempo:int) -> None:
    beat_duration = 60/tempo
    for beat in range(beats_per_measure):
        wav_file.writeframes(bytes(sin_wave(warning_pitch, beat_duration)))

def read_track(file) -> Track:
        with open(file, "r") as file:
            file_data = json.loads(file.read())
            name = file_data["name"]
            track_sections = []
            for section in file_data["sections"]:
                track_sections.append(Track_Section(section["name"], section["tempo"], section["beats"], section["sub"], section["dur"]))
        return Track(name, track_sections)

with wave.open("out.wav", mode="wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(1)
    wav_file.setframerate(sample_rate)

    #main song
    read_track("reckless_love.json")