from rest_framework import serializers

class ApplicationSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    company_name = serializers.CharField(max_length=100, required=True)
    job_title = serializers.CharField(max_length=100, required=True)
    status = serializers.ChoiceField(
        choices=['applied', 'interviewing', 'offered', 'rejected'],
        default='applied'
    )
    salary = serializers.CharField(max_length=50, required=False, allow_blank=True, default='')
    date_applied = serializers.CharField(read_only=True)
    deadline = serializers.CharField(required=False, allow_blank=True, default='')
    contact_email = serializers.EmailField(required=False, allow_blank=True, default='')
    description = serializers.CharField(required=False, allow_blank=True, default='')
    
    # Read-only fields set by the Resume Matcher
    resume_score = serializers.IntegerField(read_only=True)
    matched_keywords = serializers.ListField(child=serializers.CharField(), read_only=True)
    missing_keywords = serializers.ListField(child=serializers.CharField(), read_only=True)

    def create(self, validated_data):
        # The view will handle inserting to MongoDB directly
        return validated_data

    def update(self, instance, validated_data):
        # The view will handle updating to MongoDB directly
        return validated_data
