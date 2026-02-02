"""Celery tasks for async processing."""
from celery import shared_task
import logging

logger = logging.getLogger(__name__)


@shared_task
def process_facial_recognition(image_id):
    """
    Process facial recognition for uploaded image.
    This is a placeholder for DeepFace integration in Phase 1.
    """
    from facial_recognition.models import FacialRecognitionImage, ProcessingQueue
    
    try:
        image = FacialRecognitionImage.objects.get(id=image_id)
        queue_item = ProcessingQueue.objects.get(image=image)
        
        queue_item.status = 'processing'
        queue_item.save()
        
        # TODO: Implement DeepFace processing
        # This will compare image against db_images and external databases
        
        queue_item.status = 'completed'
        queue_item.save()
        
    except Exception as e:
        logger.error(f'Error processing facial recognition: {str(e)}')
        if queue_item:
            queue_item.status = 'failed'
            queue_item.error_message = str(e)
            queue_item.save()


@shared_task
def cleanup_old_uploads():
    """
    Remove old uploaded images to prevent storage bloat.
    Scheduled daily at 2 AM.
    """
    from datetime import timedelta
    from django.utils import timezone
    from facial_recognition.models import FacialRecognitionImage
    
    # Delete images older than 90 days that are not primary
    cutoff_date = timezone.now() - timedelta(days=90)
    old_images = FacialRecognitionImage.objects.filter(
        created_at__lt=cutoff_date,
        is_primary=False
    )
    
    count, _ = old_images.delete()
    logger.info(f'Cleaned up {count} old images')


@shared_task
def sync_external_databases():
    """
    Periodically sync with external databases (morgue, jail, police).
    To be implemented in Phase 2.
    """
    logger.info('External database sync scheduled for Phase 2')
