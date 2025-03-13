from datetime import timezone
from rest_framework import serializers
from .models import Visitor
from rest_framework.exceptions import ValidationError
from django.core.mail import send_mail

class VisitorSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    
    class Meta:
        model = Visitor
        fields = [
            'id', 'name', 'company', 'email', 'photo', 'phone_num', 'status', 
            'visiting_to', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 
            'reason', 'department'
        ]
        read_only_fields = ['status']  # Status is auto-set to "pending"

    def validate(self, data):
        # Extract relevant fields
        visiting_to = data.get('visiting_to')
        meeting_date = data.get('meeting_date')
        start_time = data.get('meeting_start_time')
        end_time = data.get('meeting_end_time')

        # Validate time order
        if start_time >= end_time:
            raise serializers.ValidationError("End time must be after start time.")

        # Check for overlaps with active appointments (confirmed, checked_in, completed)
        overlapping_active = Visitor.objects.filter(
            visiting_to=visiting_to,
            meeting_date=meeting_date,
            meeting_start_time__lt=end_time,
            meeting_end_time__gt=start_time,
            status__in=['confirmed', 'checked_in', 'completed']  # Block overlaps with active statuses
        )

        if overlapping_active.exists():
            raise serializers.ValidationError(
                "This time slot overlaps with an active appointment for the host."
            )

        # Overlaps with pending/cancelled are allowed
        return data


class VisitorInfoSerializer(serializers.ModelSerializer):
    department = serializers.CharField(source='visiting_to.department.name', read_only=True)
    visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)

    class Meta:
        model = Visitor
        fields = ['id','name', 'email','photo','phone_num','status','visiting_to', 'meeting_date', 'meeting_start_time', 'meeting_end_time','reason','department',]
        read_only_fields = ['status']


# Prevents overlaping case while updating 
# class RescheduleSerializer(serializers.ModelSerializer):
#     visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)
    
#     class Meta:
#         model = Visitor
#         fields = ['id', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 'status', 'visiting_to']

#     def validate(self, data):
#         instance = self.instance
#         visiting_to = instance.visiting_to  # Host from the existing appointment
#         meeting_date = data.get('meeting_date', instance.meeting_date)
#         start_time = data.get('meeting_start_time', instance.meeting_start_time)
#         end_time = data.get('meeting_end_time', instance.meeting_end_time)

#         # Basic validation: Start time < End time
#         if start_time >= end_time:
#             raise serializers.ValidationError("End time must be after start time.")

#         # Overlap check: Only check against active statuses (confirmed, checked_in, completed)
#         overlapping = Visitor.objects.filter(
#             visiting_to=visiting_to,
#             meeting_date=meeting_date,
#             meeting_start_time__lt=end_time,
#             meeting_end_time__gt=start_time,
#             status__in=['confirmed', 'checked_in', 'completed']  # Exclude pending/cancelled
#         ).exclude(pk=instance.pk)  # Exclude current appointment

#         if overlapping.exists():
#             raise serializers.ValidationError("This time slot overlaps with an active appointment for the host.")

#         return data

#     def update(self, instance, validated_data):
#         original_status = instance.status
#         instance = super().update(instance, validated_data)
        
#         # Send email if status changes (even to pending/cancelled)
#         if instance.status != original_status:
#             self._send_status_email(instance)
        
#         return instance

#     def _send_status_email(self, visitor):
#         if not visitor.email:
#             return

#         subject = f"Appointment Status: {visitor.status.title()}"
#         message = f"""
#         Hello {visitor.name},

#         Your appointment status with {visitor.visiting_to.username} has been updated to **{visitor.status.title()}**.

#         **Details:**
#         - Date: {visitor.meeting_date}
#         - Time: {visitor.meeting_start_time} to {visitor.meeting_end_time}

#         Thank you!
#         """
#         from_email = "noreply@yourdomain.com"
#         recipient_list = [visitor.email]
        
#         send_mail(subject, message.strip(), from_email, recipient_list, fail_silently=False)


# Need Testing
# Implementation of code below prevent from updating visitor if they have status = ['confirmed', 'checked_in', 'completed'] 
class RescheduleSerializer(serializers.ModelSerializer):
    visiting_to = serializers.CharField(source='visiting_to.username', read_only=True)
    
    class Meta:
        model = Visitor
        fields = ['id', 'meeting_date', 'meeting_start_time', 'meeting_end_time', 'status', 'visiting_to']

    def validate(self, data):
        instance = self.instance
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
        original_status = instance.status
        instance = super().update(instance, validated_data)
        
        # Send email if status changes (even to pending/cancelled)
        if instance.status != original_status:
            self._send_status_specific_email(instance)
        
        return instance

    # def _send_status_email(self, visitor):
    #     if not visitor.email:
    #         return

    #     subject = f"Appointment Status: {visitor.status.title()}"
    #     message = f"""
    #     Hello {visitor.name},

    #     Your appointment status with {visitor.visiting_to.username} has been updated to **{visitor.status.title()}**.

    #     **Details:**
    #     - Date: {visitor.meeting_date}
    #     - Time: {visitor.meeting_start_time} to {visitor.meeting_end_time}

    #     Thank you!
    #     """
    #     from_email = "settings.EMAIL_HOST_USER"
    #     recipient_list = [visitor.email]
        
    #     send_mail(subject, message.strip(), from_email, recipient_list, fail_silently=False)
    def _send_status_specific_email(self, visitor):
        if not visitor.email:
            return

        status = visitor.status
        from_email = 'settings.EMAIL_HOST_USER'
        
        # Customize email based on status
        if status == 'confirmed':
            subject = "Appointment Confirmed"
            message = f"""
            Dear {visitor.name},

            Your appointment with {visitor.visiting_to.username} has been CONFIRMED.

            Confirmed Details:
            Date: {visitor.meeting_date}
            Time: {visitor.meeting_start_time} to {visitor.meeting_end_time}

            Please arrive 10 minutes before your scheduled time.
            """
        elif status == 'cancelled':
            subject = "Appointment Cancelled"
            message = f"""
            Dear {visitor.name},

            Your appointment with {visitor.visiting_to.username} on {visitor.meeting_date} 
            has been CANCELLED.

            Original Time: {visitor.meeting_start_time} to {visitor.meeting_end_time}

            Please contact us to reschedule.
            """
        elif status == 'checked_in':
            subject = "Checked-In Successfully"
            message = f"""
            Hello {visitor.name},

            Thank you for checking in for your appointment with {visitor.visiting_to.username}.

            Current Status: Checked-In
            Check-In Time: {timezone.now().strftime('%H:%M')}
            """
        elif status == 'completed':
            subject = "Appointment Completed"
            message = f"""
            Dear {visitor.name},

            Your appointment with {visitor.visiting_to.username} has been marked COMPLETED.

            Date: {visitor.meeting_date}
            Time: {visitor.meeting_start_time} to {visitor.meeting_end_time}

            Thank you for your visit!
            """
        else:  # pending or unknown status
            subject = "Appointment Status Update"
            message = f"""
            Hello {visitor.name},

            Your appointment status has been updated to: {status.upper()}

            Next Steps: Please wait for host confirmation.
            """

        send_mail(
            subject=subject,
            message=message.strip(),
            from_email=from_email,
            recipient_list=[visitor.email],
            fail_silently=False
        )