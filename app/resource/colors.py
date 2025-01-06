# Basic emotions and their corresponding colors
ANGER = "#FF3232"      # Intense red
SADNESS = "#1C4966"    # Deep blue
ANXIETY = "#9370DB"    # Purple
HURT = "#8B0000"      # Dark red
EMBARRASSMENT = "#FFA07A"  # Light salmon
JOY = "#FFD700"       # Golden yellow

# Dictionary for easy access to all emotion colors
EMOTION_COLORS = {
    '불안': 'ANXIETY',
    '당황': 'EMBARRASSMENT',
    '분노': 'ANGER',
    '슬픔': 'SADNESS',
    '상처': 'HURT',
    '기쁨': 'JOY'
}

# Get color by emotion name
def get_color(emotion):

    emotion_key = EMOTION_COLORS.get(emotion)
    return globals().get(emotion_key)