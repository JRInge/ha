#!/bin/bash
if [[ -n "$SAMBAPASSWORD" ]]; then
  HOSTNAME="$(hostname)" docker-compose up -d
else
  echo "Set \$SAMBAPASSWORD before attempting upgrade."
fi
