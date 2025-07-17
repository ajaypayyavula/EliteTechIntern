import torch
import librosa
from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor

def transcribe_wav2vec(audio_path):
    # Load processor and model
    processor = Wav2Vec2Processor.from_pretrained("facebook/wav2vec2-base-960h")
    model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-base-960h")

    # Load and preprocess audio
    audio, rate = librosa.load(audio_path, sr=16000)
    input_values = processor(audio, return_tensors="pt", sampling_rate=16000).input_values

    # Perform inference
    with torch.no_grad():
        logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)

    # Decode prediction
    transcription = processor.batch_decode(predicted_ids)[0]
    print("Transcription:", transcription)

# Example usage (Convert your MP3 to WAV for better compatibility)
transcribe_wav2vec("C:/New folder (2)/audio.wav")
