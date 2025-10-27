#!/bin/bash
set -e

echo "📝 Registering new task definition..."
aws ecs register-task-definition \
  --cli-input-json file://task-definition-new.json \
  --region us-west-2

echo "🔄 Updating service..."
aws ecs update-service \
  --cluster maple-quest-cluster \
  --service maple-quest-task \
  --task-definition maple-quest-task \
  --force-new-deployment \
  --region us-west-2

echo "🛑 Stopping old tasks..."
for task in $(aws ecs list-tasks --cluster maple-quest-cluster --service-name maple-quest-task --region us-west-2 --query 'taskArns[]' --output text); do
  aws ecs stop-task --cluster maple-quest-cluster --task $task --region us-west-2
done

echo "✅ Done! Wait ~30 seconds for new task to start"