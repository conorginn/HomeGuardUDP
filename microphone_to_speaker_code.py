import sounddevice as sd

# Specifies the devices IDs
input_device = 1  #  Microphone
output_device = 0  # Speaker

# Sampling rate for your device 
SAMPLE_RATE = 16000
CHANNELS = 1
# Size of each audio block
blocksize = 1024

# Function to process audio input and send it to the output in real-time
def audio_callback(indata, outdata, frames, time, status):
    if status:
        print(status)
    outdata[:] = indata  # Copy input data to output

print("Start speaking... Press Ctrl+C to stop.")

# Sets up the audio stream
try:
    # Opens a stream to read from microphone and write to speaker
    with sd.Stream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype='int16') as stream:
        while True:
            # Reads and writes the audio in chunks
            data, _ = stream.read(SAMPLE_RATE // 10)  # Reads 1/10th of a second of audio
            stream.write(data)
except KeyboardInterrupt:
    print("\nExiting...")
except Exception as e:
    print(f"Error: {e}")
