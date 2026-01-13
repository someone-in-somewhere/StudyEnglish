"""Translation API endpoints."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_sync_session
from app.services.translation_service import TranslationService
from app.models.schemas import (
    TranslationRequest,
    TranslationResponse,
    TranslationHistoryResponse,
    BaseResponse
)

router = APIRouter(prefix="/api/translation", tags=["translation"])


@router.post("/translate", response_model=TranslationResponse)
def translate_text(
    request: TranslationRequest,
    db: Session = Depends(get_sync_session)
):
    """Translate text between English and Vietnamese."""
    service = TranslationService(db)

    result = service.translate(
        text=request.text,
        source_lang=request.source_lang,
        target_lang=request.target_lang,
        level=request.level
    )

    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message"))

    return TranslationResponse(
        success=True,
        id=result.get("id"),
        source_text=result["source_text"],
        translated_text=result["translated_text"],
        source_lang=result["source_lang"],
        target_lang=result["target_lang"],
        level=result.get("level"),
        created_at=result.get("created_at")
    )


@router.get("/history", response_model=TranslationHistoryResponse)
def get_translation_history(
    source_lang: Optional[str] = None,
    target_lang: Optional[str] = None,
    limit: int = 50,
    db: Session = Depends(get_sync_session)
):
    """Get translation history."""
    service = TranslationService(db)

    translations = service.get_history(
        limit=limit,
        source_lang=source_lang,
        target_lang=target_lang
    )

    return TranslationHistoryResponse(
        success=True,
        translations=translations,
        total=len(translations)
    )


@router.get("/{translation_id}")
def get_translation(
    translation_id: int,
    db: Session = Depends(get_sync_session)
):
    """Get a specific translation."""
    service = TranslationService(db)

    translation = service.get_translation_by_id(translation_id)

    if not translation:
        raise HTTPException(status_code=404, detail="Translation not found")

    return {"success": True, "translation": translation}


@router.delete("/{translation_id}", response_model=BaseResponse)
def delete_translation(
    translation_id: int,
    db: Session = Depends(get_sync_session)
):
    """Delete a translation from history."""
    service = TranslationService(db)

    if service.delete_translation(translation_id):
        return BaseResponse(success=True, message="Translation deleted")
    else:
        raise HTTPException(status_code=404, detail="Translation not found")


@router.delete("/history/clear", response_model=BaseResponse)
def clear_history(db: Session = Depends(get_sync_session)):
    """Clear all translation history."""
    service = TranslationService(db)

    count = service.clear_history()

    return BaseResponse(success=True, message=f"Cleared {count} translations")


@router.get("/stats/summary")
def get_translation_stats(db: Session = Depends(get_sync_session)):
    """Get translation statistics."""
    service = TranslationService(db)

    stats = service.get_stats()

    return {"success": True, "stats": stats}
