import logging
from dotmap import DotMap
from project.app.config.otlp_config import instrument_tracing
from project.tests.conftest import assert_all_logs_contain_trace_info


def test_instrument_tracing(app, caplog, envs):
    instrument_tracing(app)
    # assert that the app has tracing enabled
    assert app._is_instrumented_by_opentelemetry == True
    logging.info("This log should contain trace_id, span_id, and service_name fields.")
    assert_all_logs_contain_trace_info(caplog, envs)


def test_instrument_tracing_with_exporter(mocker):
    # if the environment is not local, the exporter should be set
    mock_envs = DotMap(
        {
            "APP_NAME": "test",
            "ENVIRONMENT": "testing",
            "LOG_LEVEL": "INFO",
            "OTEL_EXPORTER_OTLP_ENDPOINT": "http://example:4317",
        }
    )

    mocker.patch.dict("project.app.config.otlp_config.envs", mock_envs, clear=True)

    exporter_mock = mocker.patch(
        "project.app.config.otlp_config.TracerProvider.add_span_processor"
    )

    # import again so that the app is instrumented with the correct environment variables
    from project.app.main import app as _app
    from project.app.config.otlp_config import instrument_tracing as instrument_tracing_func

    instrument_tracing_func(_app)

    # assert that the exporter is set
    exporter_mock.assert_called()
    # assert that the app has tracing enabled
    assert _app._is_instrumented_by_opentelemetry == True
