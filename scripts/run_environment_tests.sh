#!/usr/bin/env bash

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <env> [pytest args...]"
  echo "       $0 --all [pytest args...]"
  echo "Example: $0 hcs_demo -- -k login"
  exit 1
fi

if [ "$1" = "--all" ]; then
  shift
  python3 ./scripts/run_environment_tests.py --all "$@"
  exit $?
fi

ENV="$1"
shift

export ENV="$ENV"
python3 ./scripts/run_environment_tests.py --env "$ENV" "$@"
