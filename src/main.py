"""Main module for the Vector DB Gateway application."""

# Import standard library modules first
import sys
import os
import logging

# Add the project root directory to Python path - this must be done before any other imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)

try:
    # Try to import settings first for logging configuration
    from app.core.config import settings
    logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL), format="%(asctime)s [%(levelname)s] %(message)s")
except ImportError:
    # Fallback if settings cannot be imported yet
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

logger = logging.getLogger(__name__)

# Add the project root directory to Python path - this must be done before any other imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, project_root)
logger.debug(f"Added {project_root} to Python path")
logger.debug(f"Current Python path: {sys.path}")

# Try to directly append the src directory to the path as well
src_dir = os.path.dirname(os.path.abspath(__file__))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)
    logger.debug(f"Added {src_dir} to Python path")

# Now try imports with full path debugging
try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    # Try importing the app module with error handling
    try:
        # First try relative imports from the src directory
        from app.api.endpoints import search
        from app.core.config import settings
        logger.debug("Successfully imported app modules using relative imports")
    except ImportError as e:
        logger.error(f"Error importing app modules: {e}")
        # If that fails, try absolute imports
        try:
            from src.app.api.endpoints import search
            from src.app.core.config import settings
            logger.debug("Successfully imported app modules using absolute imports")
        except ImportError as e:
            logger.error(f"Error importing app modules with absolute paths: {e}")
            raise
except ImportError as e:
    logger.error(f"Import error: {e}")
    raise

# Define the application creation function
def create_application() -> FastAPI:
    """Create and configure the FastAPI application."""
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.PROJECT_DESCRIPTION,
        version=settings.VERSION,
        docs_url=settings.DOCS_URL,
    )

    # Set up CORS middleware
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers 
    application.include_router(search.router) 

    @application.on_event("startup")
    async def startup_event():
        """Startup event handler."""
        # await create_db_and_tables() # No need to create tables every time on startup
        logger.info("Starting up application...")

    @application.get("/")
    async def root():
        """Root endpoint."""
        return {"message": "Welcome to Vector DB Gateway API"}

    return application


# Create the application
app = create_application()


if __name__ == "__main__":
    logger.info("Running application directly")
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )