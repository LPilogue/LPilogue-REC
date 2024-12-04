from app.model.loadModel import load_model
import torch
import numpy as np

# 모델과 토크나이저 불러오기
model, tokenizer, label_encoder= load_model()

def predict_emotions(sentence):
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