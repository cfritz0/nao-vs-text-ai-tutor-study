# C:\nao\nao_say_server.py
# Python 2.7 x64
# Receives text on localhost:8765 and makes NAO speak it with ALAnimatedSpeech,
# with robust Unicode handling so the server doesn't crash on smart quotes, etc.

import socket
import qi
import re

ROBOT_IP = "172.24.195.53"
PORT = 9559

# Speech tuning (similar to Choregraphe Animated Say)
SPEED_PERCENT = 80           # 100 normal; lower = slower
VOICE_SHAPING_PERCENT = 100  # 100 normal
SPEAKING_MOVEMENT_MODE = "contextual"  # "contextual", "random", "disabled"
ANIMATION = "animations/Stand/Gestures/Explain_1"  # used only if movement mode == "disabled"

def normalize_text(text_u):
    """
    Normalize curly quotes and other punctuation to ASCII-friendly equivalents.
    text_u must be unicode.
    """
    replacements = {
        u"\u2019": u"'",   # right single quote
        u"\u2018": u"'",   # left single quote
        u"\u201C": u'"',   # left double quote
        u"\u201D": u'"',   # right double quote
        u"\u2014": u"-",   # em dash
        u"\u2013": u"-",   # en dash
        u"\u2026": u"...", # ellipsis
        u"\xa0":  u" ",    # non-breaking space
    }
    for k, v in replacements.items():
        text_u = text_u.replace(k, v)
    return text_u

def split_sentences(text_u):
    """
    Simple sentence splitter to add tiny pauses for clarity.
    """
    parts = re.split(ur'(?<=[\.\!\?])\s+', text_u.strip())
    return [p.strip() for p in parts if p.strip()]

def build_animated_sentence(text_u):
    """
    Build a unicode sentence using NAOqi speech markup.
    """
    text_u = normalize_text(text_u)

    # Keep everything unicode; don't let Python 2.7 try to ASCII-encode.
    sentence = u"\\RSPD={0}\\ \\VCT={1}\\ {2} \\RST\\".format(
        SPEED_PERCENT, VOICE_SHAPING_PERCENT, text_u
    )

    # If movement is disabled, you can still force an explicit animation:
    if SPEAKING_MOVEMENT_MODE == "disabled":
        sentence = u"^start({0}) {1} ^wait({0})".format(ANIMATION, sentence)

    return sentence

def main():
    session = qi.Session()
    session.connect("tcp://%s:%d" % (ROBOT_IP, PORT))
    animated = session.service("ALAnimatedSpeech")

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 8765))
    srv.listen(5)

    print("NAO AnimatedSpeech server listening on 127.0.0.1:8765")
    print("Send __quit__ to stop (or Ctrl+C here).")

    while True:
        conn, _ = srv.accept()
        data = conn.recv(65535)
        conn.close()

        if not data:
            continue

        # Decode incoming bytes as UTF-8 -> unicode
        try:
            text_u = data.decode("utf-8", "ignore").strip()
        except Exception:
            # fallback: best-effort
            try:
                text_u = unicode(data).strip()
            except Exception:
                text_u = u""

        if not text_u:
            continue

        if text_u == u"__quit__":
            print("Quit requested.")
            break

        print("ANIM SAY:", repr(text_u))

        config = {"speakingMovementMode": SPEAKING_MOVEMENT_MODE}

        # Speak sentence-by-sentence for clarity; keep server alive on any error
        for sent_u in split_sentences(text_u):
            try:
                sentence_u = build_animated_sentence(sent_u)
                animated.say(sentence_u, config)
                # Tiny pause between sentences (optional)
                try:
                    animated.say(u"\\pau=250\\", config)
                except Exception:
                    pass
            except Exception as e:
                print("ERROR during animated.say:", e)

    srv.close()

if __name__ == "__main__":
    main()
