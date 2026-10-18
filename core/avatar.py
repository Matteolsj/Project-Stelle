import sys
import json
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont

HISTORY_PATH = Path(__file__).parents[1] / "data" / "history.json"

EMOTION_COLORS = {
    "annoyed": "#E74C3C",
    "soft": "#F5B7B1",
    "smug": "#F4D03F",
    "surprised": "#AF7AC5",
    "happy": "#58D68D",
}


def read_last_assistant_message():
    """Lit le dernier message assistant de history.json."""
    if not HISTORY_PATH.exists():
        return None
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return None

    history = data.get("history", [])
    for msg in reversed(history):
        if msg.get("role") == "assistant" and "emotion" in msg:
            return {
                "emotion": msg["emotion"],
                "text": msg["content"],
                "timestamp": msg.get("timestamp"),
            }
    return None


class AvatarWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stelle")
        self.setMinimumSize(400, 500)

        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        self.avatar_rect = QFrame()
        self.avatar_rect.setMinimumHeight(300)
        self.avatar_rect.setStyleSheet("background-color: #AAB7B8; border-radius: 20px;")
        layout.addWidget(self.avatar_rect)

        self.emotion_label = QLabel("Émotion : —")
        self.emotion_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.emotion_label.setFont(QFont("Helvetica", 14))
        layout.addWidget(self.emotion_label)

        self.text_label = QLabel("En attente...")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.text_label.setWordWrap(True)
        self.text_label.setFont(QFont("Helvetica", 16))
        layout.addWidget(self.text_label)

        self.setLayout(layout)

        self.last_timestamp = None

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_from_history)
        self.timer.start(500)

    def refresh_from_history(self):
        msg = read_last_assistant_message()
        if msg is None:
            return
        if msg["timestamp"] != self.last_timestamp:
            self.last_timestamp = msg["timestamp"]
            self.update_emotion(msg["emotion"], msg["text"])

    def update_emotion(self, emotion, text):
        color = EMOTION_COLORS.get(emotion, "#AAB7B8")
        self.avatar_rect.setStyleSheet(f"background-color: {color}; border-radius: 20px;")
        self.emotion_label.setText(f"Émotion : {emotion}")
        self.text_label.setText(text)


def main():
    app = QApplication(sys.argv)
    window = AvatarWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()