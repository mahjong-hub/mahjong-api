#!/usr/bin/env bash
set -euo pipefail

# Usage:
#   ECS_CLUSTER must be set in env
#   ./wait_ecs_rollout.sh service1 service2 ...

if [ -z "${ECS_CLUSTER:-}" ]; then
  echo "ECS_CLUSTER env var is required"
  exit 1
fi

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <service-1> [<service-2> ...]"
  exit 1
fi

wait_service () {
  local svc="$1"
  echo "---- Checking rollout for: $svc ----"

  for i in $(seq 1 60); do
    # Get desiredCount, runningCount, and rolloutState of PRIMARY deployment
    read -r DESIRED RUNNING STATE <<< "$(
      aws ecs describe-services \
        --cluster "$ECS_CLUSTER" \
        --services "$svc" \
        --query "services[0].[desiredCount,runningCount,deployments[?status=='PRIMARY']|[0].rolloutState]" \
        --output text
    )"

    echo "$svc => desired=$DESIRED running=$RUNNING state=$STATE"

    if [ "$STATE" = "FAILED" ]; then
      echo "Rollout FAILED for $svc"
      return 1
    fi

    if [ "$STATE" = "COMPLETED" ] && [ "$RUNNING" -ge "$DESIRED" ]; then
      echo "Rollout COMPLETED for $svc"
      return 0
    fi

    sleep 10
  done

  echo "Rollout timeout for $svc"
  return 1
}

# Loop all services passed as args
for svc in "$@"; do
  wait_service "$svc"
done
