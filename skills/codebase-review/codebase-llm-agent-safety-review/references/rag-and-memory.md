# RAG And Memory

Retrieval and memory turn untrusted content into durable model context. Review isolation, provenance, lifecycle, and whether retrieved or remembered text can become instruction.

## Retrieval Checks

- Identify document loaders, upload handlers, web crawlers, connectors, search APIs, vector indexes, rerankers, metadata filters, and context assembly code.
- Verify tenant, user, workspace, project, document, and permission filters are enforced by code before retrieved content reaches the model.
- Check whether retrieval falls back to broader indexes when metadata is missing or malformed.
- Inspect chunk metadata for source, owner, tenant, visibility, ACL, freshness, and deletion state.
- Confirm citations or provenance are not treated as authorization.
- Check whether retrieved text can affect tool selection, tool arguments, policy, memory writes, or external outputs.

## Memory Checks

- Identify session memory, long-term memory, summaries, vectorized memory, tool traces, checkpoints, caches, and analytics exports.
- Check what is persisted, for how long, under whose identity, and whether users can inspect, delete, or isolate it.
- Verify secrets, credentials, private files, system prompts, hidden tool output, and cross-tenant data are redacted or blocked before persistence.
- Check whether memory is scoped by tenant, user, workspace, project, environment, and agent identity.
- Inspect summarizers and compaction for instruction smuggling, secret retention, and loss of provenance.
- Confirm stale permissions do not keep granting access through old memory after user, tenant, or document ACL changes.

## Guardrails

- Tenant-filtered retrieval at query time and result validation before prompt assembly.
- Separate instruction prompts from retrieved or remembered data with explicit data labels.
- Redaction and classification before indexing, summarizing, logging, and memory writes.
- Memory TTLs, deletion propagation, ACL revalidation, and per-user or per-tenant namespaces.
- Poisoning tests for retrieved documents, summaries, and durable memory.

## Probes

- Insert hostile retrieval text and verify it cannot change policy or tool calls.
- Query with another tenant's document ID, metadata, title, or embedding-near duplicate.
- Remove user access to a document and verify retrieval and memory stop surfacing it.
- Store a memory that says to ignore future instructions and verify it is treated as untrusted data.
- Add secrets to an upload or tool result and verify they do not persist in memory, logs, or traces.
