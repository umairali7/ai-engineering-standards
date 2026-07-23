# Experimental Evidence Adapter Contract v1

Status: Draft, governed by proposed ADR-0015.

An adapter declares its source format and version, adapter profile and version,
accepted evidence modalities, privacy behavior, and deterministic duplicate
identity. Every conversion returns typed events plus a loss report containing
the source digest, counts seen/imported/skipped, reasons for every skip,
unrepresented fields, and any correlation gaps.

Adapters must not infer missing scores, silently change units, treat repeats or
reimports as new breadth, copy secrets, or elevate findings to correctness,
conformance, qualification, or authorization. Unknown remains unknown.

Duplicate identity is the tuple `(source_digest, source_record_id,
adapter_profile)`. Major schema incompatibility is an error. Minor additions
must be preserved under `extensions` or disclosed as loss. An adapter fixture
must prove deterministic output, duplicate rejection, source hash binding,
malformed-input rejection, and no-claim inflation.
