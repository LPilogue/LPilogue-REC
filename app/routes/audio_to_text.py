from flask import Flask, request, jsonify, Blueprint
import sounddevice as sd
import numpy as np
from transformers import pipeline
import tempfile
from scipy.io.wavfile import write
import threading  
import ffmpeg

# Flask 애플리케이션 초기화

audio_bp=Blueprint("audio", __name__)

# Whisper 모델 로드
whisperPipe = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-tiny",  # tiny로 변경 (용량 문제)
    chunk_length_s=30,             # 30초 단위로 처리
    device="cpu"                   
)

# 녹음 상태 관리 변수
is_recording = False
recording_thread = None
recorded_audio = None


def record_audio_thread(sample_rate=16000):
    """
    별도의 스레드에서 음성 녹음
    """
    global recorded_audio, is_recording
    print("Recording started...")
    audio_data = []
    while is_recording:
        frame = sd.rec(1024, samplerate=sample_rate, channels=1, dtype="float32")
        sd.wait()
        audio_data.append(frame)
    print("Recording stopped.")
    recorded_audio = np.concatenate(audio_data)

    
    """
    무음 구간으로 종료 조건을 걸까 생각해 봤는데 생각이 길어질 뿐 녹음을 종료하고 싶지 않은 경우가 있을 수 있을 것 같아 
    특정 버튼을 누르면 녹음 시작하고, 또 다른 버튼을 누르면 녹음을 종료할 수 있도록 했습니다
    """
@audio_bp.route('/start_recording', methods=['POST'])
def start_recording():
    """
    녹음 시작
    """
    global is_recording, recording_thread
    if is_recording:
        return jsonify({"status": "error", "message": "Recording is already in progress."}), 400

    is_recording = True
    recording_thread = threading.Thread(target=record_audio_thread, kwargs={"sample_rate": 16000})
    recording_thread.start()
    return jsonify({"status": "success", "message": "Recording started."})

@audio_bp.route('/stop_recording', methods=['POST'])
def stop_recording():
    """
    녹음 중단 & 텍스트 변환
    """
    global is_recording, recording_thread, recorded_audio
    if not is_recording:
        return jsonify({"status": "error", "message": "No recording in progress."}), 400

    is_recording = False
    recording_thread.join()  # 녹음 스레드 종료 대기

    # 녹음된 데이터를 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_file_name = temp_file.name
        print(f"Saving temporary audio file: {temp_file_name}")
        write(temp_file_name, 16000, (recorded_audio * 32767).astype(np.int16))

    # 텍스트 변환
    print("Processing audio with Whisper model...")
    try:
        result = whisperPipe(temp_file_name, generate_kwargs={"task": "transcribe", "language": "korean"})
        transcription = result["text"]
        print(f"Transcription: {transcription}")
        return jsonify({"status": "success", "transcription": transcription})
    except Exception as e:
        print(f"Error during transcription: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


