#!/bin/bash
if [[ -n "$1" ]]; then
  if [[ -n "$2" ]]; then
    my_cmd="$2"
  else
    my_cmd=/bin/bash
  fi
  sudo docker exec -it "$1" "${my_cmd}"
else
  echo "Usage is $0 container_name [cmd]"
fi
