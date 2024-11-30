from flask import Flask
from transformers import ElectraTokenizer, ElectraForSequenceClassification
import torch
from sklearn.preprocessing import LabelEncoder
import joblib

app = Flask(__name__)

# 로컬 디렉토리 지정 (bert_model 폴더 경로)
model_path = "../bert_model"  # 로컬에 저장한 폴더 경로

# 토크나이저와 모델 로드
tokenizer = ElectraTokenizer.from_pretrained(model_path)
model = ElectraForSequenceClassification.from_pretrained(model_path)
label_encoder=joblib.load(model_path + "/label_encoder.pkl")
# 로드 확인
print("Model and tokenizer loaded successfully.")

@app.route("/")
def hello():
    return "Server is running!"

@app.route("/predict/<sentence>")
def predict_emotion(sentence):
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128)
    # inputs = {key: val.to(device) for key, val in inputs.items()}  # GPU로 이동
    outputs = model(**inputs)
    predicted_class = torch.argmax(outputs.logits, dim=1).item()
    predicted_emotion = label_encoder.inverse_transform([predicted_class])[0]
    return predicted_emotion

if __name__ == "__main__":
    app.run(host="localhost", port=5000)



