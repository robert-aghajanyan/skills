# Data Processing

Review transformations for algorithmic complexity, memory growth, and unnecessary passes over data.

## Large Inputs

Look for code that handles:

- CSV, JSON, Parquet, XML, logs, reports, archives, spreadsheets, images, media, model artifacts, or database exports.
- Lists of users, accounts, tenants, services, instances, repositories, commits, issues, traces, metrics, costs, rows, events, or objects.
- Untrusted or user-supplied input size.
- Historical windows, date ranges, regions, clusters, namespaces, resources, or all-time scans.

## Common Risks

- Reading full inputs into memory when streaming, chunking, iterators, cursors, or incremental aggregation would work.
- Building multiple large intermediate lists, maps, dataframes, object graphs, or JSON strings for the same data.
- Sorting, grouping, deduplicating, joining, or regex matching inside loops without considering input size.
- Repeated serialization/deserialization between equivalent formats.
- Recomputing derived values instead of carrying them through the pipeline.
- Unbounded recursion, graph traversal, globbing, directory walking, or dependency traversal.
- Quadratic comparison patterns such as repeated membership checks in lists instead of sets/maps.
- Dataframe operations that silently materialize full copies or convert efficient types to Python objects.
- Loading large fixtures or generated data in every test case.

## Batch And Streaming Review

Check whether the path:

- Defines a batch size and explains the tradeoff.
- Can resume after failure without reprocessing everything.
- Preserves ordering when ordering matters.
- Emits progress or checkpoint information for long jobs.
- Avoids holding all records after producing the final aggregate or output.
- Handles empty, tiny, large, skewed, duplicate, and malformed inputs.

## Algorithmic Complexity

State complexity only when it helps the user act. Prefer concrete scale language:

- `O(n^2)` pairwise comparisons over 50 items may be fine.
- The same pattern over 50,000 records is likely a blocker.
- A linear scan in startup may be acceptable but harmful if repeated per request.

## Validation

Recommend focused validation with representative input sizes, memory snapshots, elapsed time, query counts, allocation profiles, or property tests that exercise the large-input branch.
