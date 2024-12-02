from flask import Flask
from transformers import ElectraTokenizer, ElectraForSequenceClassification
import torch
from sklearn.preprocessing import LabelEncoder
import joblib
import numpy as np

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
# def predict_emotion(sentence):
#     inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128)
#     # inputs = {key: val.to(device) for key, val in inputs.items()}  # GPU로 이동
#     outputs = model(**inputs)
#     predicted_class = torch.argmax(outputs.logits, dim=1).item()
#     predicted_emotion = label_encoder.inverse_transform([predicted_class])[0]
#     return predicted_emotion
def predict_top_3_emotions(sentence):
    # 입력 문장을 토큰화
    inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True, max_length=128)

    # 모델의 출력 계산
    outputs = model(**inputs)

    # 로짓(logits) 가져오기
    logits = outputs.logits.squeeze(0).detach().numpy()

    # 로짓 값에서 확률로 변환 (softmax)
    probabilities = torch.softmax(outputs.logits, dim=1).squeeze(0).detach().numpy()

    # 상위 3개의 인덱스 가져오기
    top_3_indices = np.argsort(probabilities)[::-1][:3]

    # 인덱스를 클래스 이름으로 변환
    top_3_classes = label_encoder.inverse_transform(top_3_indices)

    # 상위 3개의 클래스와 확률을 리스트로 결합
    top_3_results = [(top_3_classes[i], float(probabilities[top_3_indices[i]])) for i in range(3)]


    return top_3_results

if __name__ == "__main__":
    app.run(host="localhost", port=5000)



