#!/usr/bin/env bash

set -euo pipefail

# generate default NodeName, eg: node[1-6,8,12-15]
SIDS=`sort -nu sids | grep -v "^$"`
SIDS=(${SIDS//\n/})
echo "sids: ${SIDS}"
NODE_NAME="node["  # eg: [1-6,8]
RANGE_START=`echo ${SIDS} | head -n 1` # eg: 1 of 1-6

echo "start: ${RANGE_START}"
