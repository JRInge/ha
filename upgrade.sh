#!/bin/bash
if [[ -n "$SAMBAPASSWORD" ]]; then
  docker pull ghcr.io/home-assistant/home-assistant:stable
  ./start.sh
else
  echo "Set \$SAMBAPASSWORD before attempting upgrade."
fi
