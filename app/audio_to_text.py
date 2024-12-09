from flask import Flask, request, jsonify
import sounddevice as sd
import numpy as np
from transformers import pipeline
import tempfile

# Flask 애플리케이션 초기화
app = Flask(__name__)

# Whisper 모델 로드
whisperPipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-medium",  # Medium 모델 사용 (정확도 높음)
    chunk_length_s=30,             # 30초 단위로 처리
    device="cpu"                   
)

def record_audio(sample_rate=16000, max_duration=300):
    """
    실시간으로 음성을 녹음
    """
    print(f"Recording for up to {max_duration} seconds...")
    audio_data = sd.rec(int(max_duration * sample_rate), samplerate=sample_rate, channels=1, dtype="float32")
    sd.wait()  # 녹음 완료될 때까지 대기
    print("Recording finished.")
    return audio_data

@app.route('/record', methods=['POST'])
def record_and_transcribe():
    """
    REST API: 음성을 녹음하고 Whisper 모델로 변환
    """
    try:
        # 녹음 파라미터 가져오기
        max_duration = int(request.form.get('max_duration', 300))  # 기본값 5분 (초 단위)
        sample_rate = 16000  # 고정 샘플링 속도

        # 음성 녹음 시작
        print("Starting audio recording...")
        audio_data = record_audio(sample_rate=sample_rate, max_duration=max_duration)

        # 임시 WAV 파일로 저장
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
            temp_file_name = temp_file.name
            print(f"Saving temporary audio file: {temp_file_name}")
            sd.write(temp_file_name, audio_data, sample_rate)

        # Whisper 모델로 텍스트 변환
        print("Processing audio with Whisper model...")
        result = whisperPipe(temp_file_name, generate_kwargs={"task": "transcribe", "language": "korean"})
        transcription = result["text"]
        print(f"Transcription: {transcription}")

        return jsonify({"status": "success", "transcription": transcription})

    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    app.run(host="0.0.0.0", port=5003)  # Flask 서버 실행