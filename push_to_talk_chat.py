import os, socket, tempfile, time, sys, threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pynput import keyboard
from openai import OpenAI

# --------------------
# Config
# --------------------
ROBOT_SAY_HOST = "127.0.0.1"
ROBOT_SAY_PORT = 8765

SAMPLE_RATE = 16000
CHANNELS = 1

PTT_KEY = keyboard.Key.space   # hold SPACE to talk
QUIT_KEY = keyboard.Key.esc    # press ESC to quit

TRANSCRIBE_MODEL = "gpt-4o-mini-transcribe"
CHAT_MODEL = "gpt-4.1-mini"

SYSTEM_PROMPT = "You are a college tutor in Computer Science. Keep answers concise and conversational."
MAX_TURNS = 5  

# Console animation knobs
TYPE_DELAY_SEC = 0.015
SPINNER_DELAY_SEC = 0.08

# --------------------
# State
# --------------------
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

history = [
    {"role": "system", "content": SYSTEM_PROMPT},
]

recording = False
chunks = []
quit_requested = False

# --------------------
# Helpers
# --------------------
def spinner(msg, stop_flag_fn):
    frames = ["|", "/", "-", "\\"]
    i = 0
    while not stop_flag_fn():
        sys.stdout.write("\r{} {}".format(msg, frames[i % len(frames)]))
        sys.stdout.flush()
        time.sleep(SPINNER_DELAY_SEC)
        i += 1
    sys.stdout.write("\r" + (" " * (len(msg) + 4)) + "\r")
    sys.stdout.flush()

def type_out(prefix, text):
    sys.stdout.write(prefix)
    sys.stdout.flush()
    for ch in text:
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(TYPE_DELAY_SEC)
    sys.stdout.write("\n")
    sys.stdout.flush()

def nao_send(text):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ROBOT_SAY_HOST, ROBOT_SAY_PORT))
    s.sendall(text.encode("utf-8"))
    s.close()

def callback(indata, frames_count, time_info, status):
    global chunks
    if recording:
        chunks.append(indata.copy())

def write_pcm16_wav(path, samplerate, audio_float32):
    """
    Convert float32 [-1,1] audio into standard PCM16 WAV.
    This avoids 'corrupted/unsupported audio' errors.
    """
    audio = np.asarray(audio_float32, dtype=np.float32)

    # Ensure 2D shape (n, channels)
    if audio.ndim == 1:
        audio = audio.reshape(-1, 1)

    audio_int16 = np.clip(audio, -1.0, 1.0)
    audio_int16 = (audio_int16 * 32767.0).astype(np.int16)

    write(path, samplerate, audio_int16)

def record_to_wav():
    """
    Hold SPACE to record, release to stop.
    ESC quits.
    Returns path to WAV file or None.
    """
    global chunks, recording, quit_requested
    chunks = []
    recording = False

    print("\nHold SPACE to talk. Release to send. Press ESC to quit.")

    # Record as float32, convert ourselves to PCM16 for a clean WAV.
    with sd.InputStream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        dtype="float32",
        callback=callback
    ):
        def on_press(key):
            global recording, quit_requested, chunks
            if key == QUIT_KEY:
                quit_requested = True
                return False
            if key == PTT_KEY and not recording:
                chunks = []
                recording = True
                print("[REC] Listening...")

        def on_release(key):
            global recording
            if key == PTT_KEY and recording:
                recording = False
                print("[REC] Stopped.")
                return False

        with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()

    if quit_requested:
        return None

    if not chunks:
        return None

    audio = np.concatenate(chunks, axis=0)  # float32
    fd, path = tempfile.mkstemp(suffix=".wav")
    os.close(fd)

    write_pcm16_wav(path, SAMPLE_RATE, audio)

    # Optional debug (helps confirm file isn't empty)
    try:
        print("[DEBUG] WAV bytes:", os.path.getsize(path))
    except Exception:
        pass

    return path

def transcribe(wav_path):
    with open(wav_path, "rb") as f:
        tx = client.audio.transcriptions.create(
            model=TRANSCRIBE_MODEL,
            file=f
        )
    return (tx.text or "").strip()

def ask_llm(user_text):
    # Add user message
    history.append({"role": "user", "content": user_text})

    resp = client.responses.create(
        model=CHAT_MODEL,
        input=history,
    )

    reply = (resp.output_text or "").strip()

    # Add assistant reply
    history.append({"role": "assistant", "content": reply})

    # Trim old context: keep system + last MAX_TURNS user/assistant pairs
    if len(history) > 1 + (2 * MAX_TURNS):
        history[:] = [history[0]] + history[-(2 * MAX_TURNS):]

    return reply

# --------------------
# Main loop
# --------------------
def main():
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError('OPENAI_API_KEY is not set. Run: setx OPENAI_API_KEY "..." then reopen terminal.')

    print("Push-to-talk voice chat -> NAO (ESC quits)")

    try:
        while True:
            wav = record_to_wav()
            if quit_requested:
                break
            if not wav:
                print("[INFO] No audio captured.")
                continue

            # Transcribe (spinner)
            done = {"v": False}
            t = threading.Thread(target=spinner, args=("Transcribing", lambda: done["v"]))
            t.daemon = True
            t.start()
            try:
                user_text = transcribe(wav)
            finally:
                done["v"] = True
                t.join()
                try:
                    os.remove(wav)
                except Exception:
                    pass

            if not user_text:
                print("[INFO] Empty transcription.")
                continue

            type_out("[YOU] ", user_text)

            # LLM (spinner)
            done2 = {"v": False}
            t2 = threading.Thread(target=spinner, args=("Thinking", lambda: done2["v"]))
            t2.daemon = True
            t2.start()
            try:
                reply = ask_llm(user_text)
            finally:
                done2["v"] = True
                t2.join()

            if not reply:
                print("[INFO] Empty reply.")
                continue

            type_out("[NAO] ", reply)

            # Send to NAO server
            try:
                nao_send(reply)
            except Exception as e:
                print("[ERROR] Could not send to NAO server:", e)
                print("Is nao_say_server.py running and listening on 127.0.0.1:8765?")

    except KeyboardInterrupt:
        pass

    # Optional: ask server to quit
    try:
        nao_send("__quit__")
    except Exception:
        pass

    print("Goodbye.")

if __name__ == "__main__":
    main()
