"""
Structured logging configuration using structlog.

Development: Human-readable colored console output.
Production: JSON format for log aggregation systems.

Usage:
    from shared.logging import configure_logging, get_logger

    # Call once at application startup
    configure_logging(environment="development")

    # Use anywhere in application/infrastructure layers
    logger = get_logger()
    logger.info("campaign_created", campaign_id=str(campaign.id), title=campaign.title)
"""

from __future__ import annotations

import logging
import sys
from typing import Literal

import structlog


Environment = Literal["development", "production", "test"]

_configured = False


def configure_logging(
    environment: Environment = "development",
    log_level: int | None = None,
) -> None:
    """
    Configure structlog and stdlib logging.

    Call this once at application startup (e.g., in main.py or FastAPI lifespan).

    Args:
        environment: "development" for console output, "production" for JSON.
        log_level: Override log level. Defaults to DEBUG (dev) or INFO (prod).
    """
    global _configured

    if _configured:
        return

    if log_level is None:
        log_level = logging.DEBUG if environment == "development" else logging.INFO

    # Shared processors for both structlog and stdlib
    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.UnicodeDecoder(),
    ]

    if environment == "development":
        # Console output with colors
        renderer: structlog.types.Processor = structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.plain_traceback,
        )
    else:
        # JSON for production (log aggregation)
        shared_processors.append(
            structlog.processors.format_exc_info,
        )
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Configure stdlib logging to use structlog
    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=shared_processors,
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Silence noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("playwright").setLevel(logging.WARNING)

    _configured = True


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    """
    Get a structlog logger.

    Args:
        name: Logger name. If None, uses the caller's module name.

    Returns:
        A bound logger instance.

    Example:
        logger = get_logger()
        logger.info("task_started", task_id="123", campaign_id="456")
        logger.error("task_failed", task_id="123", error=str(e), exc_info=True)
    """
    return structlog.get_logger(name)


def bind_context(**kwargs) -> None:
    """
    Bind context variables that will be included in all subsequent logs.

    Useful for request-scoped context like correlation_id, user_id, etc.

    Example:
        bind_context(correlation_id=request_id, user_id=user.id)
        # All logs in this context will include these fields
    """
    structlog.contextvars.bind_contextvars(**kwargs)


def clear_context() -> None:
    """Clear all bound context variables."""
    structlog.contextvars.clear_contextvars()
