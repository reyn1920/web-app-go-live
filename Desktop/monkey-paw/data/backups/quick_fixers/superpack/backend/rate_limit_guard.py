from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, limits=None):
        super().__init__(app)
        self.limits = limits or {"/api/compose/preview": (30, 60)}

    async def dispatch(self, request, call_next):
        return await call_next(request)
