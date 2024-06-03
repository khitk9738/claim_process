import logging
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from starlette.types import ASGIApp
from .env_config import envs


def instrument_tracing(app: ASGIApp) -> None:
    # Setting OpenTelemetry
    # set the service name to show in traces
    resource = Resource.create(
        attributes={"service.name": envs.APP_NAME, "compose_service": envs.APP_NAME}
    )

    # The line `tracer = TracerProvider(resource=resource)` is creating an instance of the
    # `TracerProvider` class from the OpenTelemetry SDK.
    tracer = TracerProvider(resource=resource)

    if envs.ENVIRONMENT != "local":
        # set the span processor to export traces to tempo
        tracer.add_span_processor(BatchSpanProcessor(OTLPSpanExporter()))

   # `trace.set_tracer_provider(tracer)` is setting the global tracer provider for the OpenTelemetry
   # library. It assigns the provided `tracer` instance as the tracer provider to be used for creating
   # spans and managing tracing operations within the application. This ensures that all tracing
   # operations within the application will use the configured `tracer` instance for creating and
   # exporting spans.
    trace.set_tracer_provider(tracer)

   # The `LoggingInstrumentor().instrument()` method is configuring the logging settings for the
   # application. Here is what each parameter is doing:
    # - `log_level=envs.LOG_LEVEL`: This parameter sets the logging level to the value of the `LOG_LEVEL`
    #   environment variable.
    # - `set_logging_format=True`: This parameter enables setting the logging format.
    # - `logging_format="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d]
    #   [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s
    #   trace_sampled=%(otelTraceSampled)s] - %(message)s"`: This parameter sets the logging format to
    #   include the trace ID, span ID, service name, and trace sampled status in the log messages.
    LoggingInstrumentor().instrument(
        log_level=envs.LOG_LEVEL,
        set_logging_format=True,
        logging_format="%(asctime)s %(levelname)s [%(name)s] [%(filename)s:%(lineno)d] [trace_id=%(otelTraceID)s span_id=%(otelSpanID)s resource.service.name=%(otelServiceName)s trace_sampled=%(otelTraceSampled)s] - %(message)s",
    )

    FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)

    # instrument all 3rd party libraries you want to trace below here

    logging.info("OTLP instrumentation set.")
