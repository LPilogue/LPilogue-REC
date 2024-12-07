from transformers import ElectraTokenizer, ElectraForSequenceClassification
import joblib

def load_model():
    # 로컬 디렉토리 지정 (bert_model 폴더 경로)
    model_path = "../model_resource"  # 로컬에 저장한 폴더 경로

    # 토크나이저와 모델 로드
    tokenizer = ElectraTokenizer.from_pretrained(model_path)
    model = ElectraForSequenceClassification.from_pretrained(model_path)
    label_encoder=joblib.load(model_path + "/label_encoder.pkl")
    # 로드 확인
    print("Model and tokenizer loaded successfully.")
    return model, tokenizer, label_encoder