from app.api.problems import router as problems_router
from app.api.testcases import router as testcases_router
from app.api.models_api import router as models_router

__all__ = ["problems_router", "testcases_router", "models_router"]
