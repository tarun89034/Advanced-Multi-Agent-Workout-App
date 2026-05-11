import os
from typing import Optional

from loguru import logger

_tracer = None


def init_observability(service_name: str = "ai-workflow-app"):
    global _tracer

    sentry_dsn = os.getenv("SENTRY_DSN")
    if sentry_dsn:
        try:
            import sentry_sdk

            sentry_sdk.init(
                dsn=sentry_dsn,
                traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.1")),
                environment=os.getenv("ENVIRONMENT", "production"),
            )
            logger.info("Sentry initialized for observability")
        except Exception as exc:
            logger.warning(f"Sentry initialization failed: {exc}")

    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT")
    if otlp_endpoint:
        try:
            from opentelemetry import trace
            from opentelemetry.sdk.resources import Resource
            from opentelemetry.sdk.trace import TracerProvider
            from opentelemetry.sdk.trace.export import BatchSpanProcessor
            from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

            resource = Resource.create({"service.name": service_name})
            provider = TracerProvider(resource=resource)
            exporter = OTLPSpanExporter(
                endpoint=otlp_endpoint,
                headers=os.getenv("OTEL_EXPORTER_OTLP_HEADERS"),
            )
            provider.add_span_processor(BatchSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
            _tracer = trace.get_tracer(service_name)
            logger.info("OpenTelemetry initialized for observability")
        except Exception as exc:
            logger.warning(f"OpenTelemetry initialization failed: {exc}")

    return _tracer


def get_tracer() -> Optional[object]:
    return _tracer
