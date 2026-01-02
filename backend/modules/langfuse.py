"""
Langfuse observability integration via OpenTelemetry.

Initializes tracing to send spans to Langfuse for LLM observability.
Uses the Agno framework instrumentor to automatically capture agent interactions.
"""

from __future__ import annotations

import base64
import logging
from typing import Optional

from dotenv import load_dotenv
from openinference.instrumentation.agno import AgnoInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from pydantic import ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

log = logging.getLogger("app")
log.setLevel(logging.INFO)


class Settings(BaseSettings):
    """Langfuse connection settings loaded from environment variables."""

    langfuse_public_key: str
    langfuse_secret_key: str
    langfuse_base_url: str = "http://langfuse-web:3000"
    service_name: str = "superpod-backend"
    service_version: str = "1.0.0"

    model_config = SettingsConfigDict(case_sensitive=False)


# Global state to ensure tracing is only initialized once
_settings: Optional[Settings] = None
_tracer_provider: Optional[TracerProvider] = None
_tracing_enabled: bool = False


def _build_exporter(settings: Settings) -> OTLPSpanExporter:
    """Build OTLP exporter with Langfuse authentication."""
    auth = base64.b64encode(f"{settings.langfuse_public_key}:{settings.langfuse_secret_key}".encode()).decode()
    endpoint = f"{settings.langfuse_base_url.rstrip('/')}/api/public/otel/v1/traces"
    return OTLPSpanExporter(
        endpoint=endpoint,
        headers={"Authorization": f"Basic {auth}"},
        timeout=5,
    )


def init_tracing(force: bool = False) -> bool:
    """
    Initialize Langfuse tracing via OpenTelemetry.

    Sets up:
    - TracerProvider with service metadata
    - BatchSpanProcessor for efficient span export
    - AgnoInstrumentor for automatic agent instrumentation

    Safe to call multiple times - will skip if already initialized.

    Returns:
        bool: True if tracing is enabled, False if disabled or failed
    """
    global _settings, _tracer_provider, _tracing_enabled

    if _tracing_enabled and not force:
        return True

    try:
        _settings = Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        log.warning("Langfuse env not configured; tracing disabled: %s", exc)
        _tracing_enabled = False
        return False

    try:
        exporter = _build_exporter(_settings)

        # Service metadata helps identify traces in Langfuse
        resource = Resource.create(
            {
                "service.name": _settings.service_name,
                "service.version": _settings.service_version,
            }
        )
        tracer_provider = TracerProvider(resource=resource)

        # BatchSpanProcessor buffers spans for efficient network usage
        tracer_provider.add_span_processor(BatchSpanProcessor(exporter))

        trace_api.set_tracer_provider(tracer_provider)

        # Automatically instrument Agno framework to capture agent runs
        AgnoInstrumentor().instrument(tracer_provider=tracer_provider)

        _tracer_provider = tracer_provider
        _tracing_enabled = True
        log.info("Langfuse tracing initialized")
        return True
    except Exception as exc:  # noqa: BLE001
        log.exception("Tracing initialization failed; continuing without tracing: %s", exc)
        _tracing_enabled = False
        _tracer_provider = None
        return False


def get_tracer_provider() -> Optional[TracerProvider]:
    """Get the global tracer provider instance."""
    return _tracer_provider


# ======================================================================
# Alternative simpler approach (commented out, kept for reference)
# ======================================================================
# This approach uses environment variables directly instead of
# explicit configuration. Both work - current approach is more explicit.
# ======================================================================
# import base64
# import os

# from dotenv import load_dotenv
# from openinference.instrumentation.agno import AgnoInstrumentor
# from opentelemetry import trace as trace_api
# from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import SimpleSpanProcessor

# load_dotenv()

# # Set environment variables for Langfuse
# LANGFUSE_AUTH = base64.b64encode(
#     f"{os.getenv('LANGFUSE_PUBLIC_KEY')}:{os.getenv('LANGFUSE_SECRET_KEY')}".encode()
# ).decode()
# os.environ["OTEL_EXPORTER_OTLP_ENDPOINT"] = f"{os.getenv('LANGFUSE_BASE_URL')}/api/public/otel"
# os.environ["OTEL_EXPORTER_OTLP_HEADERS"] = f"Authorization=Basic {LANGFUSE_AUTH}"

# # Configure the tracer provider
# tracer_provider = TracerProvider()
# tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter()))
# trace_api.set_tracer_provider(tracer_provider=tracer_provider)

# # Start instrumenting agno
# AgnoInstrumentor().instrument()
