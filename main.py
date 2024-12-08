import wave
import math

sample_rate = 44100
high_pitch = 2093.005
low_pitch = 1046.502

def sin_wave(frequency, duration):
    for frame in range(round(duration * sample_rate)):
        time = frame / sample_rate
        amplitude = 1/((time+1)**5) * math.sin(2 * math.pi * frequency * time)
        yield round((amplitude + 1) /2 * 255)

def generate_measure(wav_file, beats_per_measure:int, tempo:int):
    beat_duration = 60/tempo
    wav_file.writeframes(bytes(sin_wave(high_pitch, beat_duration))) # write beat 1
    for beat in range(beats_per_measure-1):
        wav_file.writeframes(bytes(sin_wave(low_pitch, beat_duration))) # write rest of beats

with wave.open("out.wav", mode="wb") as wav_file:
    wav_file.setnchannels(1)
    wav_file.setsampwidth(1)
    wav_file.setframerate(sample_rate)

    for _ in range(0,15):
        generate_measure(wav_file, 11, 220)