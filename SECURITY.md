# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability in noisetool, please report it by emailing the maintainers.

Do NOT create a public GitHub issue for security vulnerabilities.

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.x     | :white_check_mark: |

## Security Considerations

noisetool generates audio files and does not:

- Execute arbitrary code
- Make network requests (except PyPI install)
- Read files from arbitrary paths (except --info and --config which require explicit user paths)
- Store or transmit user data
