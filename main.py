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

def import_track(file) -> Track:
        with open(file, "r") as file:
            file_data = json.loads(file.read())
            name = file_data["name"]
            track_sections = []
            for section in file_data["sections"]:
                track_sections.append(Track_Section(section["name"], section["tempo"], section["beats"], section["sub"], section["dur"]))
        return Track(name, track_sections)

def export_track(track:Track):
    with wave.open(f"{track.name}.wav", mode="wb") as wav_file:
        #setup file
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(sample_rate)

        #main song
        for section in track.sections:
            for _ in range(0,section.dur):
                generate_measure(wav_file, section.tempo, section.beats, section.sub)

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
    sections = [{"name":section.name, "tempo":section.tempo, "beats":section.beats, "sub":section.sub, "dur":section.dur} for section in track.sections]
    data = {"name":track.name, "sections":sections}

    with open(file, "w") as file:
        file.write(json.dumps(data, indent=4))

t = import_track("hello.json")
export_track(t)