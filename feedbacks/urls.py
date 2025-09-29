from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "feedbacks"

urlpatterns = [
    path("", views.submit_feedback, name="submit_feedback"),
    path("success/", views.feedback_success, name="feedback_success"),
    path("sucess/", RedirectView.as_view(
        pattern_name="feedbacks:feedback_success", permanent=False
    )),
    path("api/webhook/verboo/", views.webhook_verboo, name="webhook_verboo"),
]
