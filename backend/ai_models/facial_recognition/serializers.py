"""API Serializers for Facial Recognition app."""
from rest_framework import serializers
from ai_models.facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue, SearchSession,
    OfflineSignatureQueue
)


class FacialRecognitionImageSerializer(serializers.ModelSerializer):
    """Serializer for facial recognition images."""
    
    class Meta:
        model = FacialRecognitionImage
        fields = [
            'id', 'missing_person', 'image_file', 'is_primary', 'status',
            'face_confidence', 'processed_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'processed_at']


class MissingPersonSerializer(serializers.ModelSerializer):
    """Serializer for missing person records."""
    facial_recognition_images = FacialRecognitionImageSerializer(many=True, read_only=True)
    match_count = serializers.SerializerMethodField()
    reporter_name = serializers.CharField(source='reported_by.get_full_name', read_only=True)
    reporter_blockchain_hash = serializers.SerializerMethodField()
    
    class Meta:
        model = MissingPerson
        fields = [
            'id', 'reported_by', 'reporter_name', 'reporter_blockchain_hash', 'jurisdiction',
            'full_name', 'description', 'status',
            'date_reported', 'last_seen_date', 'last_seen_location',
            'age', 'gender', 'eye_color', 'height', 'height_unit', 'complexion', 'languages',
            'identifying_marks', 'facial_recognition_images',
            'match_count', 'police_analysis_report', 'government_analysis_report',
            'raised_at', 'escalated_at', 'dual_signature_family', 'dual_signature_police',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at', 'facial_recognition_images', 'raised_at', 'escalated_at']
    
    def validate_last_seen_date(self, value):
        from django.utils import timezone
        from datetime import timedelta
        
        if value:
            now = timezone.now()
            # Must be at least 1 hour ago
            one_hour_ago = now - timedelta(hours=1)
            
            if value > now:
                raise serializers.ValidationError("Last seen date cannot be in the future.")
            if value > one_hour_ago:
                raise serializers.ValidationError("Last seen date must be at least one hour before the current time.")
        
        return value
    
    def get_match_count(self, obj):
        return obj.facial_matches.filter(status='verified').count()

    def get_reporter_blockchain_hash(self, obj):
        from users.models import AuditLog
        # Attempt to get the hash from the first API log related to this reporter and case
        log = AuditLog.objects.filter(user=obj.reported_by, action='api_call').first()
        if log and log.actor_hash:
            return log.actor_hash
        # Fallback reproducible hash per user
        import hashlib
        if obj.reported_by:
            return hashlib.sha256(str(obj.reported_by.id).encode()).hexdigest()
        return None


class FacialMatchSerializer(serializers.ModelSerializer):
    """Serializer for facial match results."""
    missing_person_name = serializers.CharField(
        source='missing_person.full_name', read_only=True
    )
    missing_person_details = MissingPersonSerializer(
        source='missing_person', read_only=True
    )
    source_image = FacialRecognitionImageSerializer(read_only=True)
    
    class Meta:
        model = FacialMatch
        fields = [
            'id', 'missing_person', 'missing_person_name', 'missing_person_details', 'source_image',
            'match_confidence', 'distance_metric', 'source_database',
            'status', 'verified_by', 'verified_at', 'verification_notes',
            'algorithm_version', 'model_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'verified_at', 'distance_metric', 'algorithm_version'
        ]


class ProcessingQueueSerializer(serializers.ModelSerializer):
    """Serializer for processing queue items."""
    
    class Meta:
        model = ProcessingQueue
        fields = [
            'id', 'image', 'priority', 'status', 'retries', 'max_retries',
            'started_at', 'completed_at', 'error_message', 'created_at'
        ]
        read_only_fields = ['id', 'started_at', 'completed_at', 'created_at']


class SearchSessionSerializer(serializers.ModelSerializer):
    """Serializer for search sessions."""
    best_match_details = FacialMatchSerializer(source='best_match', read_only=True)
    
    class Meta:
        model = SearchSession
        fields = [
            'id', 'user', 'uploaded_image', 'search_query', 'best_match',
            'best_match_details', 'match_confidence', 'total_candidates_searched',
            'is_closed', 'closure_action', 'closure_notes', 'closed_at',
            'consent_given', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'closed_at']


class OfflineSignatureQueueSerializer(serializers.ModelSerializer):
    """Serializer for offline signature queue items."""
    
    class Meta:
        model = OfflineSignatureQueue
        fields = [
            'id', 'case', 'officer', 'signature_payload', 'signed_at',
            'nonce', 'is_synced', 'synced_at', 'sync_error',
            'requires_manual_review', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'nonce', 'is_synced', 'synced_at', 'requires_manual_review']
