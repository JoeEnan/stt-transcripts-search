import logging

from sqlalchemy import func

from database import SessionLocal, Transcription

# Configure logging
logger = logging.getLogger(__name__)


def search_transcriptions(file_name: str, match_full_file_name=False, match_case=False):
    try:
        with SessionLocal() as db:
            query = db.query(Transcription)

            if match_full_file_name:
                if match_case:
                    query = query.filter(
                        Transcription.original_audio_filename == file_name
                    )
                else:
                    query = query.filter(
                        func.lower(Transcription.original_audio_filename)
                        == file_name.lower()
                    )
            elif match_case:
                query = query.filter(
                    Transcription.original_audio_filename.op("GLOB")(f"*{file_name}*")
                )
            else:
                query = query.filter(
                    func.lower(Transcription.original_audio_filename).like(
                        f"%{file_name.lower()}%"
                    )
                )

            results = query.all()
            logger.info(
                f"Search completed for file_name: {file_name}, results found: {len(results)}"
            )
            return results
    except Exception as e:
        logger.exception(f"Error during search: {e}")
        raise
