from fastapi import APIRouter

from app.core.exceptions.base import AppException

_test_router = APIRouter(prefix="/__test__", tags=["Test"])


@_test_router.get("/raise-500")
def raise_500():
    raise AppException("Simulated server error")


@_test_router.get("/__test__/raise-unhandled")
def raise_unhandled():
    raise RuntimeError("boom")
