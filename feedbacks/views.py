from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q

from .forms import FeedbackForm
from .models import Feedback
from .utils import classify_feedback, extract_franchise

import json, os, hmac, hashlib, logging

logger = logging.getLogger(__name__)

def submit_feedback(request):
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            if not getattr(obj, "franchise", ""):
                try:
                    obj.franchise = extract_franchise(obj.message) or ""
                except Exception:
                    obj.franchise = ""

            try:
                obj.feedback_type = classify_feedback(obj.message)
            except Exception:
                obj.feedback_type = "unclassified"

            obj.save()
            return redirect("feedbacks:feedback_success")
    else:
        form = FeedbackForm()
    return render(request, "feedbacks/feedback_form.html", {"form": form})


def feedback_success(request):
    totals = Feedback.objects.aggregate(
        compliments=Count("id", filter=Q(feedback_type="compliment")),
        complaints=Count("id", filter=Q(feedback_type="complaint")),
        total=Count("id"),
    )
    feedbacks = Feedback.objects.order_by("-created_at")
    context = {"totals": totals, "feedbacks": feedbacks}
    return render(request, "feedbacks/feedback_success.html", context)


@csrf_exempt
def verboo_webhook(request):
    if request.method != "POST":
        return JsonResponse({"error": "method_not_allowed"}, status=405)

    raw_body = request.body or b""
    secret = os.getenv("VERBOO_WEBHOOK_SECRET")
    signature = request.headers.get("X-Verboo-Signature")
    if secret and signature:
        digest = hmac.new(secret.encode(), msg=raw_body, digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(digest, signature):
            return HttpResponseBadRequest("invalid signature")

    payload = {}
    if raw_body:
        try:
            payload = json.loads(raw_body.decode("utf-8"))
        except json.JSONDecodeError:
            payload = request.POST.dict()
    else:
        payload = request.POST.dict()

    norm = {str(k).strip().lower(): (v if isinstance(v, str) else str(v))
            for k, v in payload.items()}

    message = (norm.get("message") or norm.get("text") or "").strip()
    if not message:
        return HttpResponseBadRequest("message is required")

    name = (norm.get("name") or norm.get("user") or "verboo-user").strip() or "verboo-user"
    email = (norm.get("email") or "noreply@verboo.ai").strip() or "noreply@verboo.ai"

    franchise = (norm.get("franchise") or norm.get("loja") or "").strip()
    if not franchise:
        try:
            franchise = extract_franchise(message) or ""
        except Exception:
            franchise = ""

    classification = (
        norm.get("classification") or
        norm.get("type") or
        norm.get("feedback_type") or
        ""
    ).strip().lower()

    map_table = {
        "elogio": "compliment", "compliment": "compliment", "praise": "compliment",
        "reclamacao": "complaint", "reclamação": "complaint", "complaint": "complaint",
        "sugestao": "suggestion", "sugestão": "suggestion",
        "duvida": "question", "dúvida": "question", "question": "question",
    }
    ftype = map_table.get(classification)

    if not ftype:
        try:
            ftype = classify_feedback(message)
        except Exception:
            ftype = "unclassified"

    fb = Feedback.objects.create(
        name=name,
        email=email,
        message=message,
        feedback_type=ftype,
        **({"franchise": franchise} if "franchise" in [f.name for f in Feedback._meta.fields] else {})
    )

    logger.info("WEBHOOK OK -> id=%s type=%s franchise=%s payload=%s", fb.id, ftype, franchise, payload)
    print("WEBHOOK OK -> id:", fb.id, "| type:", ftype, "| franchise:", franchise)  # redundância visível no runserver

    pt = "elogio" if ftype == "compliment" else ("reclamação" if ftype == "complaint" else ftype)
    reply = f"Obrigado! Classifiquei seu feedback como **{pt}** e registrei (ID {fb.id})."

    return JsonResponse({
        "ok": True,
        "feedback_id": fb.id,
        "classification": ftype,
        "franchise": franchise or None,
        "reply": reply,
    })


webhook_verboo = verboo_webhook
