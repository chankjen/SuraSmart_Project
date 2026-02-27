"""API Serializers for Facial Recognition app."""
from rest_framework import serializers
from facial_recognition.models import (
    MissingPerson, FacialRecognitionImage, FacialMatch, ProcessingQueue, SearchSession
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
    
    class Meta:
        model = MissingPerson
        fields = [
            'id', 'reported_by', 'full_name', 'description', 'status',
            'date_reported', 'last_seen_date', 'last_seen_location',
            'age', 'gender', 'identifying_marks', 'facial_recognition_images',
            'match_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'facial_recognition_images']
    
    def get_match_count(self, obj):
        return obj.facial_matches.filter(status='verified').count()


class FacialMatchSerializer(serializers.ModelSerializer):
    """Serializer for facial match results."""
    missing_person_name = serializers.CharField(
        source='missing_person.full_name', read_only=True
    )
    missing_person_details = MissingPersonSerializer(
        source='missing_person', read_only=True
    )
    
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
