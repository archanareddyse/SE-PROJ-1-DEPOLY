from bson import ObjectId
from bson.errors import InvalidId
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .mongo import get_tasks_collection
from .redis_client import cache_task_list, get_cached_task_list, invalidate_task_list_cache


def serialize_task(doc):
    return {
        "id": str(doc["_id"]),
        "title": doc.get("title", ""),
        "completed": doc.get("completed", False),
    }


@api_view(["GET", "POST"])
def task_list(request):
    collection = get_tasks_collection()

    if request.method == "GET":
        cached = get_cached_task_list()
        if cached is not None:
            return Response({"source": "cache", "tasks": cached})

        docs = list(collection.find().sort("_id", -1))
        tasks = [serialize_task(d) for d in docs]
        cache_task_list(tasks)
        return Response({"source": "database", "tasks": tasks})

    # POST -> create a task
    title = (request.data.get("title") or "").strip()
    if not title:
        return Response({"error": "title is required"}, status=status.HTTP_400_BAD_REQUEST)

    result = collection.insert_one({"title": title, "completed": False})
    invalidate_task_list_cache()

    new_doc = collection.find_one({"_id": result.inserted_id})
    return Response(serialize_task(new_doc), status=status.HTTP_201_CREATED)


@api_view(["PUT", "DELETE"])
def task_detail(request, task_id):
    collection = get_tasks_collection()

    try:
        oid = ObjectId(task_id)
    except InvalidId:
        return Response({"error": "invalid task id"}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == "DELETE":
        result = collection.delete_one({"_id": oid})
        if result.deleted_count == 0:
            return Response({"error": "task not found"}, status=status.HTTP_404_NOT_FOUND)
        invalidate_task_list_cache()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT -> toggle / update a task
    update_fields = {}
    if "title" in request.data:
        update_fields["title"] = request.data["title"]
    if "completed" in request.data:
        update_fields["completed"] = bool(request.data["completed"])

    if not update_fields:
        return Response({"error": "nothing to update"}, status=status.HTTP_400_BAD_REQUEST)

    result = collection.update_one({"_id": oid}, {"$set": update_fields})
    if result.matched_count == 0:
        return Response({"error": "task not found"}, status=status.HTTP_404_NOT_FOUND)

    invalidate_task_list_cache()
    updated_doc = collection.find_one({"_id": oid})
    return Response(serialize_task(updated_doc))


@api_view(["GET"])
def health_check(request):
    """Simple endpoint to confirm the API, Mongo, and Redis are reachable."""
    status_report = {"api": "ok"}

    try:
        get_tasks_collection().estimated_document_count()
        status_report["mongodb"] = "ok"
    except Exception as exc:
        status_report["mongodb"] = f"error: {exc}"

    try:
        from .redis_client import get_redis
        get_redis().ping()
        status_report["redis"] = "ok"
    except Exception as exc:
        status_report["redis"] = f"error: {exc}"

    return Response(status_report)
