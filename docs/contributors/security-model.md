# Adapter security model
Discovery reads package metadata and does not import code. Loading imports third-party code, so install and select only trusted packages. Core ships without live transport or credentials. Adapters should allowlist hosts, enforce HTTPS, timeouts and response limits, reject unsafe redirects and paths, redact secrets, and fail closed.
