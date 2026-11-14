@"
# Changelog

## 1.0.0
- First stable release
- Log generator, log collector and alert service in Docker containers
- Custom Docker network (10.0.0.0/24) and Docker volume for log storage
- Pattern alert when 5 or more errors occur within 60 seconds
"@ | Set-Content -Path CHANGELOG.md