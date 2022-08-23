#!/bin/bash

if ldconfig -p | grep -v "libdbus" | grep -q libdb; then
  echo "Test $0 failed: found libdb"
  exit 1
else
  echo "Test $0 passed"
  exit 0
fi

