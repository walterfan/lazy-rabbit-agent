"""
API endpoints for scheduled operations (designed for cronjob calls).

This module provides simple HTTP endpoints that can be called by external
schedulers like cron, without requiring Celery or Redis infrastructure.
"""

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.base import get_db
from app.services.scheduled_email_service import ScheduledEmailService

logger = logging.getLogger(__name__)

router = APIRouter()


def verify_cronjob_token(x_cronjob_token: Annotated[str | None, Header()] = None):
    """
    Verify cronjob authentication token.
    
    Set CRONJOB_SECRET_TOKEN in .env to enable authentication.
    If not set, endpoint is publicly accessible (for development).
    """
    if hasattr(settings, 'CRONJOB_SECRET_TOKEN') and settings.CRONJOB_SECRET_TOKEN:
        if not x_cronjob_token or x_cronjob_token != settings.CRONJOB_SECRET_TOKEN:
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing cronjob token"
            )
    return True


@router.post("/send-scheduled-emails")
async def send_scheduled_emails(
    db: Annotated[Session, Depends(get_db)],
    _: Annotated[bool, Depends(verify_cronjob_token)],
):
    """
    Send scheduled emails for the current hour.
    
    This endpoint should be called by a cronjob every hour.
    It will:
    1. Query users who have email_notifications_enabled=True
    2. Check if current hour matches their email_send_time
    3. Generate recommendations and send emails
    
    Example cronjob (every hour):
        0 * * * * curl -X POST http://localhost:8000/api/v1/scheduled/send-scheduled-emails \
                       -H "X-Cronjob-Token: your-secret-token"
    
    Returns:
        {
            "status": "success",
            "hour": 8,
            "processed_count": 5,
            "success_count": 4,
            "failed_count": 1,
            "timestamp": "2025-12-19T08:00:00"
        }
    """
    try:
        now = datetime.now()
        current_hour = now.hour
        
        logger.info(
            f"⏰ Scheduled email job triggered at {now.strftime('%Y-%m-%d %H:%M:%S')} "
            f"(hour={current_hour})"
        )
        
        # Create service and send emails
        service = ScheduledEmailService(db)
        result = service.send_emails_for_hour(current_hour)
        
        logger.info(
            f"✅ Scheduled email job completed: "
            f"{result['success_count']}/{result['processed_count']} emails sent successfully"
        )
        
        return {
            "status": "success",
            "hour": current_hour,
            "processed_count": result["processed_count"],
            "success_count": result["success_count"],
            "failed_count": result["failed_count"],
            "timestamp": now.isoformat(),
        }
        
    except Exception as e:
        logger.error(
            f"❌ Error in scheduled email job: {e}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process scheduled emails: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    Health check endpoint for cronjob monitoring.
    
    Returns:
        {
            "status": "healthy",
            "service": "scheduled-emails",
            "timestamp": "2025-12-19T08:00:00"
        }
    """
    return {
        "status": "healthy",
        "service": "scheduled-emails",
        "timestamp": datetime.now().isoformat(),
    }

