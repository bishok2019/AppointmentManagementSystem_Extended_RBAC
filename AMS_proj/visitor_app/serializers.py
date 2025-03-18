from datetime import timezone
from rest_framework import serializers
from .models import Visitor
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings

from notify_with_email import send_creation_notifications, send_host_notification, send_visitor_notification, send_update_notification

class VisitorSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'name', 'company', 'email', 'photo', 'phone_num', 'status', 'visiting_to', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 'reason', 'department'
        ]
        read_only_fields = ['status']

    def validate(self, data):
        meeting_date = data.get('meeting_date')
        start_time = data.get('meeting_start_time')
        end_time = data.get('meeting_end_time')

        # Validate time order
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        return data
    
    def create(self, validated_data):
        # Create visitor without linking to HostAvailability
        visitor = Visitor.objects.create(
            name=validated_data['name'],
            company=validated_data['company'],
            email=validated_data['email'],
            phone_num=validated_data['phone_num'],
            visiting_to=validated_data['visiting_to'],
            meeting_date=validated_data['meeting_date'],
            meeting_start_time=validated_data['meeting_start_time'],
            meeting_end_time=validated_data['meeting_end_time'],
            reason=validated_data['reason'],
            status='pending'
        )
        # Send creation notifications to both visitor and host
        send_creation_notifications(visitor)
        return visitor

class VisitorInfoSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)

    class Meta:
        model = Visitor
        fields = ['id','name', 'email','photo','phone_num','status','visiting_to', 'meeting_date', 'meeting_start_time', 'meeting_end_time','reason','department',]
        read_only_fields = ['status']

class RescheduleAppointmentSerializer(serializers.ModelSerializer):
    visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)
    
    class Meta:
        model = Visitor
        fields = ['id', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 'status', 'visiting_to']
        read_only_fields=['id']

    def validate(self, data):
        instance = self.instance
        if instance.status == 'confirmed':
            raise serializers.ValidationError("Confirmed appointments cannot be modified.")
        
        visiting_to = instance.visiting_to  # Host from the existing appointment
        meeting_date = data.get('meeting_date', instance.meeting_date)
        start_time = data.get('meeting_start_time', instance.meeting_start_time)
        end_time = data.get('meeting_end_time', instance.meeting_end_time)

        # Basic validation: Start time < End time
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        # Overlap check: Only check against active statuses (confirmed, checked_in, completed)
        overlapping = Visitor.objects.filter(
            visiting_to=visiting_to,
            meeting_date=meeting_date,
            meeting_start_time__lt=end_time,
            meeting_end_time__gt=start_time,
            status__in=['confirmed', 'checked_in', 'completed']  # Exclude pending/cancelled
        ).exclude(pk=instance.pk)  # Exclude current appointment

        if overlapping.exists():
            raise serializers.ValidationError("This time slot overlaps with an active appointment for the host.")

        return data

    def update(self, instance, validated_data):
        # Store original values for comparison
        original_status = instance.status
        original_date = instance.meeting_date
        original_start_time = instance.meeting_start_time
        original_end_time = instance.meeting_end_time
        
        # Update the instance
        instance = super().update(instance, validated_data)
        
        # Check what changed and send appropriate notifications
        status_changed = instance.status != original_status
        schedule_changed = (
            instance.meeting_date != original_date or
            instance.meeting_start_time != original_start_time or
            instance.meeting_end_time != original_end_time
        )
        
        # Send notifications if something important changed
        if status_changed or schedule_changed:
            send_update_notification(instance)
            
            # If confirmed, also notify the host
            if instance.status == 'confirmed':
                send_host_notification(instance, "update")
        
        return instance
    
class UpdateVisitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Visitor
        fields = ['id', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 'status', 'visiting_to']
        read_only_fields=['id']

    def validate(self, data):
        instance = self.instance
        if instance.status == 'confirmed':
            raise serializers.ValidationError("Confirmed appointments cannot be modified.")
            
        visiting_to = data.get('visiting_to', instance.visiting_to)
        meeting_date = data.get('meeting_date', instance.meeting_date)
        start_time = data.get('meeting_start_time', instance.meeting_start_time)
        end_time = data.get('meeting_end_time', instance.meeting_end_time)

        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        # Overlap check: Only check against active statuses (confirmed, checked_in, completed)
        overlapping = Visitor.objects.filter(
            visiting_to=visiting_to,
            meeting_date=meeting_date,
            meeting_start_time__lt=end_time,
            meeting_end_time__gt=start_time,
            status__in=['confirmed', 'checked_in', 'completed']  # Exclude pending/cancelled
        ).exclude(pk=instance.pk)  # Exclude current appointment

        if overlapping.exists():
            raise serializers.ValidationError("This time slot overlaps with an active appointment for the host.")

        return data
    
    def update(self, instance, validated_data):
        original_host = instance.visiting_to
        original_status = instance.status
        original_date = instance.meeting_date
        original_start_time = instance.meeting_start_time
        original_end_time = instance.meeting_end_time

        instance = super().update(instance, validated_data)
    
        host_changed = instance.visiting_to != original_host
        status_changed = instance.status != original_status
        schedule_changed = (
            instance.meeting_date != original_date or
            instance.meeting_start_time != original_start_time or
            instance.meeting_end_time != original_end_time
        )
        if host_changed:
        # If host changed, send notifications to all parties
            send_update_notification(instance, old_host=original_host)
        elif status_changed or schedule_changed:
            # For non-host changes, send regular updates
            send_update_notification(instance)
        
        return instance
