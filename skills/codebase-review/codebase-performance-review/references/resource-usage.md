# Resource Usage

Review CPU, memory, startup, logging, concurrency, and dependency costs.

## Memory

- Large in-memory collections, maps, sets, dataframes, buffers, byte arrays, or full response bodies.
- Duplicate copies during parse, transform, serialize, compress, encrypt, upload, or report generation.
- Module-level caches, registries, histories, or accumulators without eviction.
- Per-request or per-test fixture loading of large datasets.
- Retaining objects through closures, global state, background tasks, or long-lived workers.

## CPU

- Compression, encryption, image/media processing, report rendering, parsing, regex, schema validation, model inference, and templating in hot paths.
- Repeated expensive object construction, reflection, dynamic imports, dependency injection graph creation, or plugin discovery.
- Broad exception handling used for normal control flow inside loops.
- Excessive metrics label cardinality or logging formatting before log-level checks.

## Startup Latency

- Heavy imports or dependency loading at module import time.
- Network calls, filesystem scans, schema loading, model loading, browser/driver startup, or cloud SDK initialization during process start.
- CLI commands that import the entire application before parsing a cheap subcommand.
- Test suites that pay production startup cost for every test file.

## Concurrency

Recommend concurrency only when:

- Work is independent and latency-bound.
- Downstream rate limits and capacity are understood.
- There is a bounded worker count, queue, semaphore, or backpressure.
- Timeout, cancellation, partial failure, ordering, and retry behavior are explicit.
- Memory growth from in-flight work is bounded.

Flag concurrency when it creates:

- Unbounded tasks, goroutines, futures, promises, threads, or processes.
- Fanout to rate-limited APIs or shared databases.
- Shared mutable state without clear protection.
- Large in-flight payloads or result aggregation.

## Logging And Observability Cost

- Per-item logs in large loops.
- Expensive string formatting, JSON serialization, stack traces, or payload dumps before level checks.
- High-cardinality metrics labels.
- Debug tracing enabled by default in hot paths.

## Validation

Use memory profiles, CPU profiles, import-time measurement, allocation snapshots, benchmark inputs, CI timing, and logs/metrics volume to prove impact.
