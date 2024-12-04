# Basic emotions and their corresponding colors
ANGER = "#FF3232"      # Intense red
SADNESS = "#1C4966"    # Deep blue
ANXIETY = "#9370DB"    # Purple
HURT = "#8B0000"      # Dark red
EMBARRASSMENT = "#FFA07A"  # Light salmon
JOY = "#FFD700"       # Golden yellow

# Dictionary for easy access to all emotion colors
EMOTION_COLORS = {
    "anger": ANGER,
    "sadness": SADNESS,
    "anxiety": ANXIETY,
    "hurt": HURT,
    "embarrassment": EMBARRASSMENT,
    "joy": JOY
}

# Get color by emotion name
def get_color(emotion: str) -> str:
    """
    Returns the color code for a given emotion.

    Args:
        emotion (str): The name of the emotion (case-insensitive)

    Returns:
        str: The hex color code for the emotion
    """
    return EMOTION_COLORS.get(emotion.lower())