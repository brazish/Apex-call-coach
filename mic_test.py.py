import pyaudio
from deepgram import DeepgramClient, LiveOptions

DG_API_KEY = "70211449030ac778aa25d272725b23e5066fe806"

client = DeepgramClient(DG_API_KEY)

options = LiveOptions(
    model="nova-2",
    language="en-US",
    punctuate=True,
)

connection = client.listen.live.v("1", options)

def on_message(result, **kwargs):
    transcript = result.channel.alternatives[0].transcript
    if transcript:
        print("You said:", transcript)

connection.on("transcript", on_message)

audio = pyaudio.PyAudio()
stream = audio.open(
    format=pyaudio.paInt16,
    channels=1,
    rate=16000,
    input=True,
    frames_per_buffer=1024,
)

print("🎤 Speak into your microphone...")

while True:
    data = stream.read(1024)
    connection.send(data)
