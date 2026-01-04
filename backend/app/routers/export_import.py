"""
Export/Import router for vocabulary data.
Supports JSON, CSV, and Anki formats.
"""

import json
import csv
import io
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Vocabulary, UserVocabulary

router = APIRouter(prefix="/api/export", tags=["export"])


@router.get("/vocabulary/json")
def export_vocabulary_json(
    learned_only: bool = True,
    topic: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export vocabulary to JSON format."""
    query = db.query(Vocabulary)

    if learned_only:
        learned_ids = db.query(UserVocabulary.vocabulary_id).all()
        learned_ids = [id[0] for id in learned_ids]
        query = query.filter(Vocabulary.id.in_(learned_ids))

    if topic:
        query = query.filter(Vocabulary.topic == topic)

    if level:
        query = query.filter(Vocabulary.level == level)

    vocabulary = query.all()

    export_data = {
        "exported_at": datetime.now().isoformat(),
        "format": "StudyEnglish JSON",
        "version": "1.0",
        "count": len(vocabulary),
        "vocabulary": []
    }

    for vocab in vocabulary:
        export_data["vocabulary"].append({
            "word": vocab.word,
            "meaning_vi": vocab.meaning_vi,
            "pronunciation": vocab.pronunciation,
            "part_of_speech": vocab.part_of_speech,
            "level": vocab.level,
            "topic": vocab.topic,
            "example_en": vocab.example_en,
            "example_vi": vocab.example_vi,
            "synonyms": vocab.synonyms
        })

    # Create streaming response
    json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
    output = io.BytesIO(json_str.encode('utf-8'))
    output.seek(0)

    filename = f"vocabulary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    return StreamingResponse(
        output,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/vocabulary/csv")
def export_vocabulary_csv(
    learned_only: bool = True,
    topic: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export vocabulary to CSV format."""
    query = db.query(Vocabulary)

    if learned_only:
        learned_ids = db.query(UserVocabulary.vocabulary_id).all()
        learned_ids = [id[0] for id in learned_ids]
        query = query.filter(Vocabulary.id.in_(learned_ids))

    if topic:
        query = query.filter(Vocabulary.topic == topic)

    if level:
        query = query.filter(Vocabulary.level == level)

    vocabulary = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Word", "Meaning (Vietnamese)", "Pronunciation", "Part of Speech",
        "Level", "Topic", "Example (English)", "Example (Vietnamese)", "Synonyms"
    ])

    # Data rows
    for vocab in vocabulary:
        synonyms = vocab.synonyms
        if synonyms:
            try:
                synonyms = ", ".join(json.loads(synonyms))
            except:
                pass

        writer.writerow([
            vocab.word,
            vocab.meaning_vi,
            vocab.pronunciation,
            vocab.part_of_speech,
            vocab.level,
            vocab.topic,
            vocab.example_en,
            vocab.example_vi,
            synonyms
        ])

    output.seek(0)
    content = output.getvalue().encode('utf-8-sig')  # BOM for Excel compatibility

    filename = f"vocabulary_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

    return StreamingResponse(
        io.BytesIO(content),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/vocabulary/anki")
def export_vocabulary_anki(
    learned_only: bool = True,
    topic: Optional[str] = None,
    level: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Export vocabulary to Anki-compatible text format (tab-separated)."""
    query = db.query(Vocabulary)

    if learned_only:
        learned_ids = db.query(UserVocabulary.vocabulary_id).all()
        learned_ids = [id[0] for id in learned_ids]
        query = query.filter(Vocabulary.id.in_(learned_ids))

    if topic:
        query = query.filter(Vocabulary.topic == topic)

    if level:
        query = query.filter(Vocabulary.level == level)

    vocabulary = query.all()

    # Anki format: Front<tab>Back
    # Front: Word (pronunciation) [part of speech]
    # Back: Meaning + Example
    lines = []

    for vocab in vocabulary:
        front = f"{vocab.word}"
        if vocab.pronunciation:
            front += f" {vocab.pronunciation}"
        if vocab.part_of_speech:
            front += f" [{vocab.part_of_speech}]"

        back = f"<b>{vocab.meaning_vi}</b>"
        if vocab.example_en:
            back += f"<br><br><i>{vocab.example_en}</i>"
        if vocab.example_vi:
            back += f"<br>{vocab.example_vi}"

        # Escape tabs and newlines
        front = front.replace('\t', ' ').replace('\n', ' ')
        back = back.replace('\t', ' ').replace('\n', '<br>')

        lines.append(f"{front}\t{back}")

    content = "\n".join(lines)
    output = io.BytesIO(content.encode('utf-8'))
    output.seek(0)

    filename = f"vocabulary_anki_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    return StreamingResponse(
        output,
        media_type="text/plain; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/stats")
def get_export_stats(db: Session = Depends(get_db)):
    """Get statistics about exportable data."""
    total_vocab = db.query(Vocabulary).count()
    learned_vocab = db.query(UserVocabulary).count()

    # Count by topic
    topics = db.query(Vocabulary.topic, db.func.count(Vocabulary.id))\
        .group_by(Vocabulary.topic)\
        .all()

    # Count by level
    levels = db.query(Vocabulary.level, db.func.count(Vocabulary.id))\
        .group_by(Vocabulary.level)\
        .all()

    return {
        "success": True,
        "stats": {
            "total_vocabulary": total_vocab,
            "learned_vocabulary": learned_vocab,
            "by_topic": {t[0]: t[1] for t in topics if t[0]},
            "by_level": {l[0]: l[1] for l in levels if l[0]}
        }
    }


# Import router
import_router = APIRouter(prefix="/api/import", tags=["import"])


@import_router.post("/vocabulary/json")
async def import_vocabulary_json(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import vocabulary from JSON file."""
    if not file.filename.endswith('.json'):
        raise HTTPException(status_code=400, detail="File must be JSON format")

    try:
        content = await file.read()
        data = json.loads(content.decode('utf-8'))

        vocabulary_list = data.get("vocabulary", data if isinstance(data, list) else [])

        added = 0
        duplicates = 0

        for item in vocabulary_list:
            word = item.get("word", "").strip()
            if not word:
                continue

            # Check for duplicate
            existing = db.query(Vocabulary).filter(
                Vocabulary.word == word,
                Vocabulary.topic == item.get("topic", "Imported")
            ).first()

            if existing:
                duplicates += 1
                continue

            # Parse synonyms
            synonyms = item.get("synonyms", "")
            if isinstance(synonyms, list):
                synonyms = json.dumps(synonyms)
            elif isinstance(synonyms, str) and synonyms:
                synonyms = json.dumps([s.strip() for s in synonyms.split(",")])
            else:
                synonyms = "[]"

            vocab = Vocabulary(
                word=word,
                meaning_vi=item.get("meaning_vi", ""),
                pronunciation=item.get("pronunciation", ""),
                part_of_speech=item.get("part_of_speech", "noun"),
                level=item.get("level", "B1"),
                topic=item.get("topic", "Imported"),
                example_en=item.get("example_en", ""),
                example_vi=item.get("example_vi", ""),
                synonyms=synonyms
            )

            db.add(vocab)
            added += 1

        db.commit()

        return {
            "success": True,
            "message": f"Imported {added} words, {duplicates} duplicates skipped",
            "added": added,
            "duplicates": duplicates
        }

    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@import_router.post("/vocabulary/csv")
async def import_vocabulary_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import vocabulary from CSV file."""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be CSV format")

    try:
        content = await file.read()
        # Try different encodings
        try:
            text = content.decode('utf-8-sig')
        except:
            text = content.decode('utf-8')

        reader = csv.DictReader(io.StringIO(text))

        added = 0
        duplicates = 0

        for row in reader:
            # Map CSV columns to fields (flexible mapping)
            word = row.get("Word") or row.get("word") or row.get("WORD", "")
            word = word.strip()

            if not word:
                continue

            meaning = row.get("Meaning (Vietnamese)") or row.get("meaning_vi") or row.get("Meaning", "")
            topic = row.get("Topic") or row.get("topic") or "Imported"

            # Check for duplicate
            existing = db.query(Vocabulary).filter(
                Vocabulary.word == word,
                Vocabulary.topic == topic
            ).first()

            if existing:
                duplicates += 1
                continue

            synonyms = row.get("Synonyms") or row.get("synonyms") or ""
            if synonyms:
                synonyms = json.dumps([s.strip() for s in synonyms.split(",")])
            else:
                synonyms = "[]"

            vocab = Vocabulary(
                word=word,
                meaning_vi=meaning,
                pronunciation=row.get("Pronunciation") or row.get("pronunciation") or "",
                part_of_speech=row.get("Part of Speech") or row.get("part_of_speech") or "noun",
                level=row.get("Level") or row.get("level") or "B1",
                topic=topic,
                example_en=row.get("Example (English)") or row.get("example_en") or "",
                example_vi=row.get("Example (Vietnamese)") or row.get("example_vi") or "",
                synonyms=synonyms
            )

            db.add(vocab)
            added += 1

        db.commit()

        return {
            "success": True,
            "message": f"Imported {added} words, {duplicates} duplicates skipped",
            "added": added,
            "duplicates": duplicates
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Combine routers
router.include_router(import_router, prefix="", tags=["import"])
