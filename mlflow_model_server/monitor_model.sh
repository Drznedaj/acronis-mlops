#!/bin/bash

LOG_FILE="./airflow/models/model_server.log"
NOW=$(date '+%Y-%m-%d %H')
THRESHOLD_MS=500  # warning if avg latency > 500ms
ERROR_LIMIT=5     # warning if errors in the last hour > 5

echo "Model Server Monitoring Report"
echo "================================"

# Total requests in the current hour
REQ_COUNT=$(grep "$NOW" "$LOG_FILE" | grep "prediction_count=" | wc -l)
echo "Total requests this hour: $REQ_COUNT"

# Average latency in ms
AVG_LATENCY=$(grep "$NOW" "$LOG_FILE" | grep "duration_ms=" | awk -F'duration_ms=' '{sum+=$2} END {if(NR>0) print int(sum/NR); else print 0}')
echo "Average prediction latency: ${AVG_LATENCY}ms"

# Prediction failures in the current hour
ERROR_COUNT=$(grep "$NOW" "$LOG_FILE" | grep "prediction_failed" | wc -l)
echo "Prediction errors this hour: $ERROR_COUNT"

# Alerts
echo "Alerts:"
[ "$AVG_LATENCY" -gt "$THRESHOLD_MS" ] && echo " - High latency alert! Avg latency is ${AVG_LATENCY}ms"
[ "$ERROR_COUNT" -gt "$ERROR_LIMIT" ] && echo " - High error rate! ${ERROR_COUNT} errors logged this hour"
[ "$AVG_LATENCY" -le "$THRESHOLD_MS" ] && [ "$ERROR_COUNT" -le "$ERROR_LIMIT" ] && echo " - All clear"

echo "================================"
