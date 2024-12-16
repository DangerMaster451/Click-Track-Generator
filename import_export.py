from track import Track,Track_Section
from audio import Click, Cue

import wave
import json
import os

class IO:
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

                        time_passed += unit.dur *  unit.beats * 60/unit.tempo
                        break
            return Track(track_name, sections)
        
    def export_track(track:Track, click:Click, cue_offset:int, warning_duration:int=1):
        with wave.open(f"{track.name}.wav", mode="wb") as wav_file:
            #setup file
            wav_file.setnchannels(1)
            wav_file.setsampwidth(1)
            wav_file.setframerate(click.sample_rate)

            #click track
            for section in track.sections:
                if section.type == "normal" or section.type == "ignore-defaults":
                    for _ in range(0,int(section.dur)-warning_duration):
                        click.generate_measure(wav_file, section.tempo, section.beats, section.sub)
                    for _ in range(0, warning_duration):
                        click.generate_warning_measure(wav_file, section.tempo, section.beats, section.sub)
                elif section.type == "tempo-change":
                    click.generate_beat(wav_file, section.tempo, section.sub, "high")

            for section in track.sections:
                if section.cue != "":
                    cue = Cue.create_cue(section.cue)
                    print(section.time_stamp)
                    Cue.mix_in_cue(cue, f"{track.name}.wav", f"{track.name}.wav", (section.time_stamp*1000))
                    os.remove(cue)

    def save_track(track:Track, file:str) -> None:
        sections = [{"name":section.name, "type":section.type, "tempo":section.tempo, "beats":section.beats, "sub":section.sub, "dur":section.dur} for section in track.sections]
        data = {"name":track.name, "sections":sections}

        with open(file, "w") as file:
            file.write(json.dumps(data, indent=4))