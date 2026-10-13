# Security Policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.4.x   | yes       |
| 0.3.x   | critical fixes only |
| < 0.3   | no        |

## Reporting a vulnerability

The avatar kernel loads ONNX checkpoints and the optional C++ renderer
(`sla.bridge.render_native`) loads native DLLs at runtime. Both are attack
surfaces. If you find a problem — path traversal in the rig loader, unsafe
`pickle` in the cache layer, DLL search-order hijack in the native bridge,
or a prompt-injection vector in the captioning service — email
`security@sign-language-avatar-generator.dev`.

Please include: version, OS build, a minimal repro, and whether the issue is
remotely triggerable. We aim to acknowledge within 72h and ship a patched
release within 14 days for high-severity findings.

Do not open public issues for security bugs. Do not test against other
users' avatars.