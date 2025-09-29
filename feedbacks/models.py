from django.db import models

class Feedback(models.Model):
    class FeedbackType(models.TextChoices):
        COMPLAINT = "complaint", "Complaint"
        COMPLIMENT = "compliment", "Compliment"

    name = models.CharField(max_length=120)
    email = models.EmailField()
    franchise = models.CharField(max_length=120, blank=True) 
    message = models.TextField()
    feedback_type = models.CharField(
        max_length=10,
        choices=FeedbackType.choices
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        f = f" [{self.franchise}]" if self.franchise else ""
        return f"{self.name}{f} - {self.feedback_type}"
