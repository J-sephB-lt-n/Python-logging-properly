# Python-logging-properly

To run the app using native python logging:

```bash
cd example_app
uv run python -m src.examples.logging_utils
DEV_LOGGING=true uv run python -m src.examples.logging_utils
```

## Observability

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
