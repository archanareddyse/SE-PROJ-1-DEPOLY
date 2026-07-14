"""
Thin wrapper around redis-py used as a caching / middleware layer in front
of MongoDB Atlas. The task list is cached for REDIS_CACHE_TTL_SECONDS and
invalidated whenever a task is created, updated, or deleted.
"""

import json
import redis
from django.conf import settings

_redis_client = None

TASK_LIST_CACHE_KEY = "tasks:list"


def get_redis():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            decode_responses=True,
        )
    return _redis_client


def cache_task_list(tasks):
    r = get_redis()
    try:
        r.setex(TASK_LIST_CACHE_KEY, settings.REDIS_CACHE_TTL_SECONDS, json.dumps(tasks))
    except redis.exceptions.RedisError:
        # Redis being unavailable shouldn't break the app; just skip caching.
        pass


def get_cached_task_list():
    r = get_redis()
    try:
        cached = r.get(TASK_LIST_CACHE_KEY)
        return json.loads(cached) if cached else None
    except redis.exceptions.RedisError:
        return None


def invalidate_task_list_cache():
    r = get_redis()
    try:
        r.delete(TASK_LIST_CACHE_KEY)
    except redis.exceptions.RedisError:
        pass
