from django.db import models

class RoastSubmission(models.Model):
    SUBMISSION_TYPES = [
        ('auto', 'Auto-detected'),
        ('code', 'Code Screenshot'),
        ('room', 'Living Room Photo'),
        ('resume', 'Resume'),
        ('other', 'Other'),
    ]
    
    submission_type = models.CharField(max_length=20, choices=SUBMISSION_TYPES, default='auto')
    image = models.ImageField(upload_to='submissions/', null=True, blank=True)
    text_content = models.TextField(blank=True, null=True)
    roast_result = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.submission_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"