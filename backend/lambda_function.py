import json
import os
import uuid
import time
import hashlib
import hmac
import base64
import decimal
from datetime import datetime

import boto3
import jwt

# ── ENV ──────────────────────────────────────────────────────────────────────
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "confpapers-prod")
S3_BUCKET = os.environ.get("S3_BUCKET", "confpapers-files-prod-srinidhi")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
REGION = os.environ.get("REGION", "eu-west-1")
JWT_SECRET = os.environ.get("JWT_SECRET", "confpapers-secret-2026")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
s3 = boto3.client("s3", region_name=REGION)
sns = boto3.client("sns", region_name=REGION)


# ── HELPERS ──────────────────────────────────────────────────────────────────
def cors_headers():
    return {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type,Authorization",
        "Access-Control-Allow-Methods": "*",
    }


def response(status, body):
    return {
        "statusCode": status,
        "headers": cors_headers(),
        "body": json.dumps(body, default=str),
    }


def parse_body(event):
    body = event.get("body", "{}")
    if not body:
        body = "{}"
    return json.loads(body)


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 == 0:
                return int(o)
            return float(o)
        return super().default(o)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    return str(obj)


def clean_item(item):
    """Convert Decimal values in a DynamoDB item to int/float."""
    return json.loads(json.dumps(item, default=decimal_default))


# ── AUTH HELPERS ─────────────────────────────────────────────────────────────
def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(32).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return dk.hex(), salt


def verify_password(password, hashed, salt):
    dk = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
    return dk.hex() == hashed


def generate_token(user_id, username, email, role):
    payload = {
        "userId": user_id,
        "username": username,
        "email": email,
        "role": role,
        "exp": int(time.time()) + 86400,
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")


def decode_token(token):
    return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])


def get_user_from_event(event):
    headers = event.get("headers", {}) or {}
    auth = headers.get("Authorization") or headers.get("authorization") or ""
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        return decode_token(token)
    except Exception:
        return None


# ── ROUTE: AUTH ──────────────────────────────────────────────────────────────
def handle_register(event):
    body = parse_body(event)
    username = body.get("username", "").strip()
    email = body.get("email", "").strip()
    password = body.get("password", "")
    role = body.get("role", "author")

    if not username or not email or not password:
        return response(400, {"error": "username, email and password required"})
    if role not in ("author", "reviewer", "admin"):
        return response(400, {"error": "role must be author, reviewer or admin"})

    # Check duplicate email
    res = table.scan(
        FilterExpression="entityType = :et AND email = :em",
        ExpressionAttributeValues={":et": "USER", ":em": email},
    )
    if res.get("Items"):
        return response(409, {"error": "Email already registered"})

    user_id = str(uuid.uuid4())
    hashed, salt = hash_password(password)
    item = {
        "id": user_id,
        "entityType": "USER",
        "username": username,
        "email": email,
        "passwordHash": hashed,
        "salt": salt,
        "role": role,
        "createdAt": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=item)

    token = generate_token(user_id, username, email, role)
    return response(201, {
        "token": token,
        "user": {"id": user_id, "username": username, "email": email, "role": role},
    })


def handle_login(event):
    body = parse_body(event)
    email = body.get("email", "").strip()
    password = body.get("password", "")

    if not email or not password:
        return response(400, {"error": "email and password required"})

    res = table.scan(
        FilterExpression="entityType = :et AND email = :em",
        ExpressionAttributeValues={":et": "USER", ":em": email},
    )
    items = res.get("Items", [])
    if not items:
        return response(401, {"error": "Invalid credentials"})

    user = items[0]
    if not verify_password(password, user["passwordHash"], user["salt"]):
        return response(401, {"error": "Invalid credentials"})

    token = generate_token(user["id"], user["username"], user["email"], user["role"])
    return response(200, {
        "token": token,
        "user": clean_item({
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        }),
    })


# ── ROUTE: CONFERENCES ───────────────────────────────────────────────────────
def handle_conferences(event, method, path_parts, user):
    if method == "GET" and len(path_parts) == 1:
        # GET /conferences
        res = table.scan(
            FilterExpression="entityType = :et",
            ExpressionAttributeValues={":et": "CONFERENCE"},
        )
        return response(200, clean_item(res.get("Items", [])))

    if method == "POST" and len(path_parts) == 1:
        # POST /conferences — admin only
        if user["role"] != "admin":
            return response(403, {"error": "Admin only"})
        body = parse_body(event)
        conf_id = str(uuid.uuid4())
        item = {
            "id": conf_id,
            "entityType": "CONFERENCE",
            "name": body.get("name", ""),
            "description": body.get("description", ""),
            "startDate": body.get("startDate", ""),
            "endDate": body.get("endDate", ""),
            "submissionDeadline": body.get("submissionDeadline", ""),
            "topics": body.get("topics", []),
            "createdBy": user["userId"],
            "createdAt": datetime.utcnow().isoformat(),
        }
        table.put_item(Item=item)
        return response(201, clean_item(item))

    if method == "GET" and len(path_parts) == 2:
        # GET /conferences/{id}
        conf_id = path_parts[1]
        res = table.get_item(Key={"id": conf_id})
        item = res.get("Item")
        if not item or item.get("entityType") != "CONFERENCE":
            return response(404, {"error": "Conference not found"})
        return response(200, clean_item(item))

    if method == "PUT" and len(path_parts) == 2:
        # PUT /conferences/{id} — admin only
        if user["role"] != "admin":
            return response(403, {"error": "Admin only"})
        conf_id = path_parts[1]
        res = table.get_item(Key={"id": conf_id})
        item = res.get("Item")
        if not item or item.get("entityType") != "CONFERENCE":
            return response(404, {"error": "Conference not found"})
        body = parse_body(event)
        update_fields = {}
        for field in ["name", "description", "startDate", "endDate", "submissionDeadline", "topics"]:
            if field in body:
                update_fields[field] = body[field]
        if not update_fields:
            return response(400, {"error": "No fields to update"})

        expr_parts = []
        expr_vals = {}
        expr_names = {}
        for i, (k, v) in enumerate(update_fields.items()):
            alias = f"#f{i}"
            val_alias = f":v{i}"
            expr_parts.append(f"{alias} = {val_alias}")
            expr_names[alias] = k
            expr_vals[val_alias] = v

        table.update_item(
            Key={"id": conf_id},
            UpdateExpression="SET " + ", ".join(expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals,
        )
        updated = table.get_item(Key={"id": conf_id}).get("Item", {})
        return response(200, clean_item(updated))

    return response(404, {"error": "Not found"})


# ── ROUTE: PAPERS ────────────────────────────────────────────────────────────
def handle_papers(event, method, path_parts, user):
    # /papers/{id}/reviews or /papers/{id}/status
    if len(path_parts) >= 3:
        paper_id = path_parts[1]
        sub = path_parts[2]
        if sub == "reviews":
            return handle_reviews(event, method, paper_id, user)
        if sub == "status" and method == "PUT":
            return handle_update_status(event, paper_id, user)
        return response(404, {"error": "Not found"})

    if method == "GET" and len(path_parts) == 1:
        # GET /papers
        if user["role"] == "author":
            res = table.scan(
                FilterExpression="entityType = :et AND authorId = :uid",
                ExpressionAttributeValues={":et": "PAPER", ":uid": user["userId"]},
            )
        else:
            res = table.scan(
                FilterExpression="entityType = :et",
                ExpressionAttributeValues={":et": "PAPER"},
            )
        return response(200, clean_item(res.get("Items", [])))

    if method == "POST" and len(path_parts) == 1:
        # POST /papers
        body = parse_body(event)
        paper_id = str(uuid.uuid4())
        pdf_url = None
        if body.get("pdfBase64"):
            key = f"papers/{paper_id}.pdf"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=base64.b64decode(body["pdfBase64"]),
                ContentType="application/pdf",
            )
            pdf_url = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{key}"

        item = {
            "id": paper_id,
            "entityType": "PAPER",
            "title": body.get("title", ""),
            "abstract": body.get("abstract", ""),
            "authors": body.get("authors", []),
            "keywords": body.get("keywords", []),
            "conferenceId": body.get("conferenceId", ""),
            "authorId": user["userId"],
            "authorEmail": user["email"],
            "status": "submitted",
            "pdfUrl": pdf_url,
            "createdAt": datetime.utcnow().isoformat(),
            "updatedAt": datetime.utcnow().isoformat(),
        }
        table.put_item(Item=item)
        return response(201, clean_item(item))

    if method == "GET" and len(path_parts) == 2:
        # GET /papers/{id} — include reviews
        paper_id = path_parts[1]
        res = table.get_item(Key={"id": paper_id})
        item = res.get("Item")
        if not item or item.get("entityType") != "PAPER":
            return response(404, {"error": "Paper not found"})
        reviews_res = table.scan(
            FilterExpression="entityType = :et AND paperId = :pid",
            ExpressionAttributeValues={":et": "REVIEW", ":pid": paper_id},
        )
        paper = clean_item(item)
        paper["reviews"] = clean_item(reviews_res.get("Items", []))
        return response(200, paper)

    if method == "PUT" and len(path_parts) == 2:
        # PUT /papers/{id}
        paper_id = path_parts[1]
        res = table.get_item(Key={"id": paper_id})
        item = res.get("Item")
        if not item or item.get("entityType") != "PAPER":
            return response(404, {"error": "Paper not found"})
        if item["status"] not in ("submitted", "revision_required"):
            return response(400, {"error": "Paper can only be updated when status is submitted or revision_required"})

        body = parse_body(event)
        update_fields = {}
        for field in ["title", "abstract", "authors", "keywords", "conferenceId"]:
            if field in body:
                update_fields[field] = body[field]
        update_fields["updatedAt"] = datetime.utcnow().isoformat()

        if body.get("pdfBase64"):
            key = f"papers/{paper_id}.pdf"
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=key,
                Body=base64.b64decode(body["pdfBase64"]),
                ContentType="application/pdf",
            )
            update_fields["pdfUrl"] = f"https://{S3_BUCKET}.s3.{REGION}.amazonaws.com/{key}"

        expr_parts = []
        expr_vals = {}
        expr_names = {}
        for i, (k, v) in enumerate(update_fields.items()):
            alias = f"#f{i}"
            val_alias = f":v{i}"
            expr_parts.append(f"{alias} = {val_alias}")
            expr_names[alias] = k
            expr_vals[val_alias] = v

        table.update_item(
            Key={"id": paper_id},
            UpdateExpression="SET " + ", ".join(expr_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_vals,
        )
        updated = table.get_item(Key={"id": paper_id}).get("Item", {})
        return response(200, clean_item(updated))

    if method == "DELETE" and len(path_parts) == 2:
        # DELETE /papers/{id} — withdraw
        paper_id = path_parts[1]
        res = table.get_item(Key={"id": paper_id})
        item = res.get("Item")
        if not item or item.get("entityType") != "PAPER":
            return response(404, {"error": "Paper not found"})
        table.update_item(
            Key={"id": paper_id},
            UpdateExpression="SET #s = :s, updatedAt = :u",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "withdrawn", ":u": datetime.utcnow().isoformat()},
        )
        return response(200, {"message": "Paper withdrawn"})

    return response(404, {"error": "Not found"})


# ── ROUTE: REVIEWS ───────────────────────────────────────────────────────────
def handle_reviews(event, method, paper_id, user):
    if method == "GET":
        res = table.scan(
            FilterExpression="entityType = :et AND paperId = :pid",
            ExpressionAttributeValues={":et": "REVIEW", ":pid": paper_id},
        )
        return response(200, clean_item(res.get("Items", [])))

    if method == "POST":
        if user["role"] != "reviewer":
            return response(403, {"error": "Only reviewers can submit reviews"})
        # Verify paper exists
        paper_res = table.get_item(Key={"id": paper_id})
        paper = paper_res.get("Item")
        if not paper or paper.get("entityType") != "PAPER":
            return response(404, {"error": "Paper not found"})

        body = parse_body(event)
        score = body.get("score")
        if score is None or not (1 <= int(score) <= 10):
            return response(400, {"error": "Score must be between 1 and 10"})
        recommendation = body.get("recommendation", "")
        if recommendation not in ("accept", "reject", "revision"):
            return response(400, {"error": "Recommendation must be accept, reject or revision"})

        review_id = str(uuid.uuid4())
        item = {
            "id": review_id,
            "entityType": "REVIEW",
            "paperId": paper_id,
            "reviewerId": user["userId"],
            "reviewerName": user["username"],
            "score": int(score),
            "comments": body.get("comments", ""),
            "recommendation": recommendation,
            "createdAt": datetime.utcnow().isoformat(),
        }
        table.put_item(Item=item)
        return response(201, clean_item(item))

    return response(404, {"error": "Not found"})


# ── ROUTE: UPDATE STATUS ─────────────────────────────────────────────────────
VALID_TRANSITIONS = {
    "submitted": ["under_review", "withdrawn"],
    "under_review": ["accepted", "rejected", "revision_required"],
    "revision_required": ["submitted", "withdrawn"],
    "accepted": ["published"],
    "rejected": [],
    "withdrawn": [],
    "published": [],
}


def handle_update_status(event, paper_id, user):
    if user["role"] != "admin":
        return response(403, {"error": "Admin only"})

    paper_res = table.get_item(Key={"id": paper_id})
    paper = paper_res.get("Item")
    if not paper or paper.get("entityType") != "PAPER":
        return response(404, {"error": "Paper not found"})

    body = parse_body(event)
    new_status = body.get("status", "")
    current = paper.get("status", "submitted")
    allowed = VALID_TRANSITIONS.get(current, [])
    if new_status not in allowed:
        return response(400, {
            "error": f"Cannot transition from '{current}' to '{new_status}'. Allowed: {allowed}"
        })

    table.update_item(
        Key={"id": paper_id},
        UpdateExpression="SET #s = :s, updatedAt = :u",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": new_status, ":u": datetime.utcnow().isoformat()},
    )

    # Publish SNS notification to paper author
    if SNS_TOPIC_ARN:
        try:
            author_email = paper.get("authorEmail", "unknown")
            sns.publish(
                TopicArn=SNS_TOPIC_ARN,
                Subject=f"Paper Status Update: {new_status}",
                Message=(
                    f"Your paper \"{paper.get('title', '')}\" status has been updated to: {new_status}.\n\n"
                    f"Paper ID: {paper_id}\n"
                    f"Author: {author_email}\n"
                    f"Updated at: {datetime.utcnow().isoformat()}"
                ),
            )
        except Exception as e:
            print(f"SNS publish error: {e}")

    return response(200, {"message": f"Status updated to {new_status}", "status": new_status})


# ── ROUTE: DASHBOARD ─────────────────────────────────────────────────────────
def handle_dashboard(user):
    role = user["role"]

    if role == "author":
        res = table.scan(
            FilterExpression="entityType = :et AND authorId = :uid",
            ExpressionAttributeValues={":et": "PAPER", ":uid": user["userId"]},
        )
        papers = res.get("Items", [])
        submitted = sum(1 for p in papers if p.get("status") == "submitted")
        accepted = sum(1 for p in papers if p.get("status") == "accepted")
        pending = sum(1 for p in papers if p.get("status") in ("submitted", "under_review", "revision_required"))
        return response(200, clean_item({
            "role": "author",
            "myPapers": papers,
            "submittedCount": len(papers),
            "acceptedCount": accepted,
            "pendingCount": pending,
        }))

    if role == "reviewer":
        # Reviews done by this reviewer
        reviews_res = table.scan(
            FilterExpression="entityType = :et AND reviewerId = :uid",
            ExpressionAttributeValues={":et": "REVIEW", ":uid": user["userId"]},
        )
        completed_reviews = reviews_res.get("Items", [])
        # All papers for assignment view
        papers_res = table.scan(
            FilterExpression="entityType = :et",
            ExpressionAttributeValues={":et": "PAPER"},
        )
        all_papers = papers_res.get("Items", [])
        reviewed_paper_ids = {r["paperId"] for r in completed_reviews}
        pending_reviews = [p for p in all_papers if p["id"] not in reviewed_paper_ids and p.get("status") == "under_review"]
        return response(200, clean_item({
            "role": "reviewer",
            "assignedPapers": all_papers,
            "completedReviews": len(completed_reviews),
            "pendingReviews": len(pending_reviews),
        }))

    if role == "admin":
        papers_res = table.scan(
            FilterExpression="entityType = :et",
            ExpressionAttributeValues={":et": "PAPER"},
        )
        papers = papers_res.get("Items", [])
        reviewers_res = table.scan(
            FilterExpression="entityType = :et AND #r = :rv",
            ExpressionAttributeNames={"#r": "role"},
            ExpressionAttributeValues={":et": "USER", ":rv": "reviewer"},
        )
        total_reviewers = len(reviewers_res.get("Items", []))
        total = len(papers)
        accepted = sum(1 for p in papers if p.get("status") == "accepted")
        rate = round((accepted / total * 100), 1) if total > 0 else 0

        by_status = {}
        for p in papers:
            s = p.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1

        recent = sorted(papers, key=lambda x: x.get("createdAt", ""), reverse=True)[:10]
        return response(200, clean_item({
            "role": "admin",
            "totalPapers": total,
            "totalReviewers": total_reviewers,
            "acceptanceRate": rate,
            "byStatus": by_status,
            "recentSubmissions": recent,
        }))

    return response(400, {"error": "Unknown role"})


# ── ROUTE: NOTIFICATIONS (PUBLIC) ────────────────────────────────────────────
def handle_subscribe(event):
    body = parse_body(event)
    email = body.get("email", "").strip()
    if not email:
        return response(400, {"error": "email required"})
    if not SNS_TOPIC_ARN:
        return response(500, {"error": "SNS_TOPIC_ARN not configured"})
    try:
        sns.subscribe(TopicArn=SNS_TOPIC_ARN, Protocol="email", Endpoint=email)
        return response(200, {"message": f"Subscription request sent to {email}"})
    except Exception as e:
        return response(500, {"error": str(e)})


def handle_subscribers():
    if not SNS_TOPIC_ARN:
        return response(200, {"count": 0})
    try:
        res = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        subs = [s for s in res.get("Subscriptions", []) if s.get("SubscriptionArn") != "PendingConfirmation"]
        return response(200, {"count": len(subs)})
    except Exception as e:
        return response(500, {"error": str(e)})


# ── MAIN HANDLER ─────────────────────────────────────────────────────────────
def lambda_handler(event, context):
    method = event.get("httpMethod", "GET")
    path = event.get("path", "/")

    # CORS preflight
    if method == "OPTIONS":
        return response(200, {"message": "OK"})

    # Parse path
    path_parts = [p for p in path.strip("/").split("/") if p]

    if not path_parts:
        return response(200, {"message": "Conference Paper Submission API"})

    resource = path_parts[0]

    # ── PUBLIC ROUTES ────────────────────────────────────────────────────
    if resource == "subscribe" and method == "POST":
        return handle_subscribe(event)

    if resource == "subscribers" and method == "GET":
        return handle_subscribers()

    # ── AUTH ROUTES (no token needed) ────────────────────────────────────
    if resource == "auth":
        if len(path_parts) >= 2:
            action = path_parts[1]
            if action == "register" and method == "POST":
                return handle_register(event)
            if action == "login" and method == "POST":
                return handle_login(event)
        return response(404, {"error": "Not found"})

    # ── PROTECTED ROUTES ─────────────────────────────────────────────────
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Unauthorized. Provide a valid Bearer token."})

    if resource == "conferences":
        return handle_conferences(event, method, path_parts, user)

    if resource == "papers":
        return handle_papers(event, method, path_parts, user)

    if resource == "dashboard" and method == "GET":
        return handle_dashboard(user)

    return response(404, {"error": "Not found"})
