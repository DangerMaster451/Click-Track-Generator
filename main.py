from gtts import gTTS
from pydub import AudioSegment
import wave
import math
import json

sample_rate = 44100
high_pitch = 2093.005
low_pitch = 1046.502
warning_pitch = 1975.533

class Track_Section():
    def __init__(self, name, type, tempo, beats, sub, dur):
        self.name = name
        self.type = type
        self.tempo = tempo
        self.beats = beats
        self.sub = sub
        self.dur = dur

class Tempo_Change():
    def __init__(self, name, starting_tempo, ending_tempo, beats, sub, dur):
        self.name = name
        self.type = "tempo-change"
        self.starting_tempo = starting_tempo
        self.ending_tempo = ending_tempo
        self.beats = beats
        self.sub = sub
        self.dur = dur

    def generate_sections(self) -> list[Track_Section]:
        sections = []
        total_beats = int(self.beats * self.sub/4 * self.dur)
        for beat in range(total_beats):
            tempo = (self.ending_tempo - self.starting_tempo) * (beat/total_beats) + self.starting_tempo
            sections.append(Track_Section(f"tempo_change_{beat}", "tempo-change", tempo, self.beats, self.sub, 1/(self.beats*self.sub)))
        return sections

class Track():
    def __init__(self, name:str, sections:list[Track_Section]):
        self.name = name
        self.sections = sections

def sine_wave(frequency, duration):
    for frame in range(round(duration * sample_rate)):
        time = frame / sample_rate
        amplitude = 1/((frequency * 2 * time+1)) * math.sin(2 * math.pi * frequency * time)
        yield math.floor((amplitude + 1)/2 * 255)

def generate_measure(wav_file, tempo:int, beats:int, sub:int) -> None:
    beat_duration = 60/tempo/(sub/4)
    wav_file.writeframes(bytes(sine_wave(low_pitch, beat_duration))) # write beat 1
    for beat in range(0, int((beats)*(sub/4))-1):
        wav_file.writeframes(bytes(sine_wave(high_pitch, beat_duration))) # write rest of beats

def generate_beat(wav_file, tempo:float, sub:int, beat_type:str):
    beat_duration = 60/tempo/(sub/4)
    if beat_type == "high":
        wav_file.writeframes(bytes(sine_wave(high_pitch, beat_duration)))
    elif beat_type == "low":
        wav_file.writeframes(bytes(sine_wave(low_pitch, beat_duration)))

def import_track(file) -> Track:
        with open(file, "r") as file:
            file_data = json.loads(file.read())
            name = file_data["name"]
            track_sections = []
            for section in file_data["sections"]:
                if section["type"] == "normal":
                    track_sections.append(Track_Section(section["name"], section["type"], section["tempo"], section["beats"], section["sub"], section["dur"]))
                elif section["type"] == "tempo-change":
                    tempo_change = Tempo_Change(section["name"], section["start_tempo"], section["end_tempo"], section["beats"], section["sub"], section["dur"])
                    for section in tempo_change.generate_sections():
                        track_sections.append(section)
                    
        return Track(name, track_sections)

def export_track(track:Track):
    with wave.open(f"{track.name}.wav", mode="wb") as wav_file:
        #setup file
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(sample_rate)

        #main song
        for section in track.sections:
            if section.type == "normal":
                for _ in range(0,int(section.dur)):
                    generate_measure(wav_file, section.tempo, section.beats, section.sub)
            elif section.type == "tempo-change":
                generate_beat(wav_file, section.tempo, section.sub, "high")

def new_track() -> Track:
    track_name = input("track name: ")
    sections = []
    while True:
        section_name = input("section name: ")
        tempo = int(input("tempo: "))
        beats = int(input("beats: "))
        subdivision = int(input("subdivision: "))
        duration = int(input("duration (measures): "))
        sections.append(Track_Section(section_name, tempo, beats, subdivision, duration))

        if input("Continue? y/n ") == "n":
            break
    return Track(track_name, sections)

def save_track(track:Track, file:str) -> None:
    sections = [{"name":section.name, "type":section.type, "tempo":section.tempo, "beats":section.beats, "sub":section.sub, "dur":section.dur} for section in track.sections]
    data = {"name":track.name, "sections":sections}

    with open(file, "w") as file:
        file.write(json.dumps(data, indent=4))

def create_cue(text) -> None:
    gTTS(text=text, lang="en").save(f"{text}.wav")

def insert_cue(cue_file, track_file, timestamp, out_file):
    cue_audio = AudioSegment.from_file("C:\\Users\\andre\\dev\\Click Track Generator\\Verse 1.wav")
    track_audio = AudioSegment.from_file(track_file)

    mixed = track_audio.overlay(cue_audio)
    mixed.export(out_file, format='mp3')

#create_cue("thingy is a really cool thingy and I love him so much. Thingy is my best friend and I can't live without my thingy")
t = import_track("I-Speak-Jesus.json")
save_track(t, "I-speak-Jesus.wav")