import whisper
from database import SessionLocal, Transcription

model = whisper.load_model("tiny")


def transcribe_audio(file_path: str) -> str:
    # print("Current working directory:", os.getcwd())
    # print("Audio path:", file_path)
    result = model.transcribe(file_path)

    print(result)
    return result["text"]


def save_transcription(
    file_path: str, original_audio_filename: str, transcribed_text: str
) -> None:
    with SessionLocal() as session:
        transcription = Transcription(
            audio_filename=file_path,
            original_audio_filename=original_audio_filename,
            text=transcribed_text,
        )
        session.add(transcription)
        session.commit()
