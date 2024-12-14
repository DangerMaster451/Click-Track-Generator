from gtts import gTTS
from pydub import AudioSegment
import wave
import math
import json
import os

sample_rate = 44100
high_pitch = 2093.005
low_pitch = 1046.502
warning_pitch = 1975.533

class Track_Section():
    def __init__(self, name, type, tempo, beats, sub, dur, time_stamp=0, cue=""):
        self.name = name
        self.cue = cue
        self.type = type
        self.tempo = tempo
        self.beats = beats
        self.sub = sub
        self.dur = dur
        self.time_stamp = time_stamp
        self.cue = cue

    def copy(self, time_stamp, cue):
        return type(self)(self.name, self.type, self.tempo, self.beats, self.sub, self.dur, time_stamp, cue)

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

'''def import_track(file) -> Track:
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
                    
        return Track(name, track_sections)'''

def import_track(file:str) -> Track:
    with open(file, "r") as file:
        file_data = json.loads(file.read())
        track_name = file_data["track-name"]
        track_tempi = file_data["track-tempi"]
        track_beats = file_data["track-beats"]
        track_subdivisions = file_data["track-subdivisions"]


        units = []
        for unit in file_data["units"]:
            name = unit["name"]
            type = unit["type"]
            for sub_unit in unit["sub-units"]:
                if type == "ignore-defaults":
                    tempo = sub_unit["tempo"]
                    beats = sub_unit["beats"]
                    subdivisions = sub_unit["sub"]
                else:
                    tempo = track_tempi[int(sub_unit["tempo"])]
                    beats = track_beats[int(sub_unit["beats"])]
                    subdivisions = track_subdivisions[int(sub_unit["sub"])]
                duration = sub_unit["dur"]
                units.append(Track_Section(name, type, tempo, beats, subdivisions, duration))
                
        
        sections = []
        time_passed = 0
        for section in file_data["track-order"]:
            unit_name = section["unit-name"]
            cue = section["cue"]

            for unit in units:
                if unit.name == unit_name:
                    print(unit.name, str(time_passed))
                    new_unit = unit.copy(time_passed, cue)
                    sections.append(new_unit)

                    time_passed += round(duration *  beats * tempo/60)
        return Track(track_name, sections)

def export_track(track:Track, cue_offset:int):
    with wave.open(f"{track.name}.wav", mode="wb") as wav_file:
        #setup file
        wav_file.setnchannels(1)
        wav_file.setsampwidth(1)
        wav_file.setframerate(sample_rate)

        #click track
        for section in track.sections:
            if section.type == "normal":
                for _ in range(0,int(section.dur)):
                    generate_measure(wav_file, section.tempo, section.beats, section.sub)
            elif section.type == "tempo-change":
                generate_beat(wav_file, section.tempo, section.sub, "high")

        for section in track.sections:
            if section.cue != "":
                cue = create_cue(section.cue)
                print(section.time_stamp)
                mix_in_cue(cue, f"{track.name}.wav", f"{track.name}.wav", (section.time_stamp*1000))
                os.remove(cue)

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

def create_cue(text) -> str:
    gTTS(text=text, lang="en").save(f"{text}.wav")
    return f"{text}.wav"

def mix_in_cue(cue_file:str, track_file:str, out_file:str, delay:float) -> None:
    cue_audio = AudioSegment.from_file(cue_file)
    track_audio = AudioSegment.from_file(track_file)

    mixed = track_audio.overlay(cue_audio, position=delay)
    mixed.export(out_file, format='wav')

t = import_track("thing.json")
export_track(t, 0)