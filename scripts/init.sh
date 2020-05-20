#!/usr/bin/env bash

set -euxo pipefail

./generate_hosts.sh
./generate_slurm_conf.sh
