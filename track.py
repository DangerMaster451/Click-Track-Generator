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