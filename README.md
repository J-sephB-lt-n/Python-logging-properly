# Python-logging-properly

```bash
cd example_app
uv run python -m src.examples.logging_utils
DEV_LOGGING=true uv run python -m src.examples.logging_utils
```

## Observability

Application observability means being able to understand the internal state of the system from it's output alone.

Good observability means that you can answer any question about your system, even questions which you did not anticipate needing to be answered.

Here is what is required for good system observability, and how I have implemented these requirements using native python and OpenTelemetry:

| Requirement                                                                                                       | Native python                                                                                                                          | OpenTelemetry |
| ----------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- | ------------- |
| Context-rich structured events                                                                                    | Automatic inclusion of available context and system information<br>`log_session` context manager                                       |               |
| Metrics                                                                                                           |                                                                                                                                        |
| Structured logs                                                                                                   | Custom JSON log formatter class                                                                                                        |
| Traces                                                                                                            | `log_session` context manager                                                                                                          |
| Logs describe _WHO_ performed the action                                                                          | Automatically including system and context information using log record factory                                                        |
| Logs describe _WHAT_ happened                                                                                     |                                                                                                                                        |
| Logs describe _WHEN_ the event happened                                                                           | Automatic timestamp field in every log                                                                                                 |
| Logs describe _WHERE_ the event happened                                                                          | Automatically populate each log using the LogRecord factory with system and context info.                                              |
| Logs describe _WHY_ (the reason) the event happened                                                               | Enforce a `reason` attribute required in every log message (or raise an Exception)                                                     |
| Everything must be linkable to everything (shared IDs). Metrics, logs and traces to themselves and to each other. | `log_session` context manager                                                                                                          |
| Logs and traces are easily searched/filtered                                                                      | Consistent log formatting using custom JSONFormatter class                                                                             |               |
| Metrics/Logging/Tracing doesn't slow the app down                                                                 | Use a QueueHandler                                                                                                                     |               |
| Context propagation                                                                                               | Pass the `log_session` context manager object around                                                                                   |               |
| Devs embrace good logging approaches                                                                              | - DEV_LOGGING=true makes local logs nice for dev<br>- logging interface in the code is attractive<br>- Readable logging config (.yaml) |               |

The book [Observability Engineering](https://www.oreilly.com/library/view/observability-engineering/9781492076438/) describes the _structured event_ as the fundamental unit of observability, required for achieving _observability_ in a system (_observability_, in this context, meaning that you can answer any question about the state of the system using your telemetry data, even questions you did not anticipate before collecting that data). A _structured event_ is an arbitrarily wide set of key/value pairs encoding metadata about the event (e.g. a JSON object or python dict). The book describes the creation of a structured event like this:

```
To create that record, you start by initializing an empty map right at the beginning,
when the request first enters your service. During the lifetime of that request, any
interesting details about what occurred—unique IDs, variable values, headers, every
parameter passed by the request, the execution time, any calls made to remote
services, the execution time of those remote calls, or any other bit of context that may
later be valuable in debugging—get appended to that map. Then, when the request
is about to exit or error, that entire map is captured as a rich record of what just
happened. The data written to that map is organized and formatted, as key-value
pairs, so that it’s easily searchable: in other words, the data should be structured.
That’s a structured event.
```

Where a single request (or _transaction_, or other distinct unit of work) contains

## Good attributes for a structured log event to have

- timestamp
- request duration
- message/description
- status (SUCCESS, FAILURE, HTTP CODE etc.)
- app_id
- user_id
- project_id
- org_id
- service ID
- service version
- machine ID
- region
- library/module
- script name, function name, line number
- trace ID, trace name, span ID, span name, parent span ID
- transaction ID

## Traces are Logs

Traces are just logs (structured events) linkable by shared IDs.

## Native Python Logging

I found [this video](https://www.youtube.com/watch?v=9L77QExPmI0) extremely helpful.

Here are my principles/goals:

- Use dictConfig with a JSON or YAML config file (I'm using YAML in this repo).
- Put all handlers and filters on the root logger only. All other loggers propagate logs to the root logger, which handles them. This will make my handlers/formatters also apply to 3rd party log messages.
- Don't use the root logger directly in code (use `logging.getLogger(__name__)`).
- Use ISO-8601 timestamps (with explicit timezone)
- Do structured logging using a JSON formatter
- Print indented and colourful logs to STDOUT in a dev environment (but not prod).
- Don't log on the main app thread (slows down the app too much)
