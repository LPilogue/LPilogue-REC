from flask import Flask, request, jsonify
import google.generativeai as genai

# Flask 앱 생성
app = Flask(__name__)

# Google Generative AI API 키 설정
GOOGLE_API_KEY = 'AIzaSyB1uEv2SUkZpuWJkh5l8pzICqPyUhi0K0k'
genai.configure(api_key=GOOGLE_API_KEY)

# 모델 설정
generation_config = {
    "temperature": 0.7,             #텍스트의 창의성과 예측 가능성을 조절. range: 0~1
    "top_p": 0.9,                   #확률의 누적 합을 기반으로 가능한 단어를 선택하는 방식. range: 0~1
    "top_k": 10,                    #다음에 올 단어를 선택할 때, 가능성이 높은 k개의 후보 중에서만 단어를 고르는 방식. range: 자연수
    "max_output_tokens": 2048,      #생성되는 텍스트의 최대 길이
}


model = genai.GenerativeModel('gemini-pro',
                             generation_config=generation_config)

@app.route('/generate', methods=['POST'])
def generate_response():
    # JSON 데이터에서 입력 받아오기
    data = request.get_json()
    content = data.get('content', '')
    song_name = data.get('song_name', '')
    song_artist = data.get('song_artist', '')
    emotion = data.get('emotion', '')

    if not content:
        return jsonify({"error": "입력 내용이 비어 있습니다."}), 400

    # Prompt 생성
    prompt = f"""
    {content}
    노래 추천 정보를 활용해 대화에 자연스럽게 녹여줘.
    답변은 편안한 한국어 반말로 쓰고, 마지막에는 대화 상황에 어울리는 멘트와 함께 노래 추천을 적당히 섞어줘.
    주어진 감정 분석 결과는 '{emotion}', 추천 노래는 '{song_name}', 아티스트는 '{song_artist}'야.
    해당 노래의 가사도 고려해서 추천 노래를 소개해 줘.
    상대방 기분에 맞게 자연스럽게 노래를 언급하거나 공감하고, 편안한 친구 같은 말투로 이야기해 줘.
    예를 들어 '오늘같이 우울한 날엔 이런 노래 어때?' 또는 '기쁜 날엔 더 신날 수 있는 곡을 가져왔어!' 같은 식으로 다양한 답변을 만들어봐.
    상대방 이야기를 듣고 상황에 맞게 공감하거나 조언을 할 땐 진솔하게, 자연스러운 대화를 이어가고, 과도하거나 억지스러운 위로는 삼가줘. 꼭 필요할 때만 간결하고 따뜻한 위로를 전하고, 덜 중요한 상황은 간단히 넘어가도 돼.
    필요하면 극복에 도움 되는 사자성어, 속담, 명언 등을 적절히 추천해주되, 상대방 기분을 상하지 않게 배려하며 써줘.
    """

    try:
        # 모델로부터 응답 생성
        answer = model.generate_content(prompt)
        return jsonify({"answer": answer.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004)
