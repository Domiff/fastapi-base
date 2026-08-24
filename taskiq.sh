#!/bin/sh
taskiq worker backend.core.broker:broker \
  --fs-discover \
  --tasks-pattern "backend/**/tasks.py" \
  --no-configure-logging \
  --workers 2 \
  --shutdown-timeout 30 \
  --wait-tasks-timeout 30
