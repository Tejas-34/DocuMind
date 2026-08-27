from fastapi import Request, status
from fastapi.responses import JSONResponse
import logging

logger = logging.getLogger(__name__)

class DocuMindException(Exception):
    def __init__(self, message: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class TenantAccessDeniedException(DocuMindException):
    def __init__(self, message: str = "Resource not found or unauthorized"):
        super().__init__(message=message, status_code=status.HTTP_404_NOT_FOUND)

class DocumentProcessingException(DocuMindException):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

async def documind_exception_handler(request: Request, exc: DocuMindException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

async def global_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error occurred: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "An internal server error occurred."},
    )
