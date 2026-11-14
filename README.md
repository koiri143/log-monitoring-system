# Lightweight Container-Based Log Monitoring and Alert System

A small log monitoring system made with Docker, Python and Flask.

## Components
- log-generator: creates random logs (INFO, WARNING, ERROR, CRITICAL) and sends them to the collector
- log-collector: stores logs in a Docker volume and forwards ERROR and CRITICAL logs to the alert service
- alert-service: stores alerts and raises a pattern alert when 5 or more errors occur within 60 seconds

## How to run
docker-compose up --build

## Version
Current version: 1.0.0 (see VERSION and CHANGELOG.md). The project follows semantic versioning (MAJOR.MINOR.PATCH).

## License
MIT License, see the LICENSE file.
