# Provider Cost Tracking and Analytics

## Overview

The Provider Cost Tracking system provides comprehensive cost analytics across all AI providers, enabling users and administrators to monitor spending, identify cost-saving opportunities, and track usage patterns.

## Features

### 1. Per-Request Cost Tracking
- Automatically tracks costs for each request broken down by provider
- Records token usage (input and output tokens)
- Stores subtask count per provider
- Links costs to specific requests for detailed analysis

### 2. User Dashboard Analytics
- **Total Cost**: Cumulative spending across all requests
- **Provider Breakdown**: Cost distribution by AI provider
- **Free Provider Usage**: Percentage of requests using free providers (Ollama, HuggingFace, Gemini)
- **Estimated Savings**: Calculated savings from using free providers vs paid alternatives
- **Visual Charts**: Bar charts showing cost distribution with color coding for free vs paid providers

### 3. Admin Monitoring Dashboard
- **System-Wide Costs**: Total costs across all users
- **24-Hour Window**: Costs for the last 24 hours
- **Provider Comparison**: Side-by-side comparison of all providers
- **Token Usage**: Detailed input/output token counts per provider
- **Request Distribution**: Number of requests and subtasks per provider
- **Savings Metrics**: System-wide estimated savings from free providers

### 4. Monthly Cost Reports
- Generate detailed monthly reports by provider
- Available for individual users or system-wide
- Includes:
  - Total cost per provider
  - Request count per provider
  - Token usage statistics
  - Estimated savings
  - Free provider usage percentage

### 5. Cost Threshold Alerts
- Set custom cost thresholds per user
- Monitor costs over configurable time periods (default: 30 days)
- Automatic alerts when thresholds are exceeded
- Percentage of threshold calculation
- Provider-specific breakdown when threshold is exceeded

## API Endpoints

### User Endpoints

#### Get User Statistics
```http
GET /api/v1/user/stats
Authorization: Bearer <token>
```

Response includes `providerCostBreakdown`:
```json
{
  "totalRequests": 150,
  "totalCost": 2.45,
  "providerCostBreakdown": {
    "byProvider": [
      {
        "providerName": "groq",
        "requestCount": 50,
        "totalSubtasks": 120,
        "totalCost": 0.0150,
        "totalInputTokens": 50000,
        "totalOutputTokens": 25000
      },
      {
        "providerName": "ollama",
        "requestCount": 100,
        "totalSubtasks": 200,
        "totalCost": 0.0,
        "totalInputTokens": 100000,
        "totalOutputTokens": 50000
      }
    ],
    "totalCost": 0.0150,
    "totalRequests": 150,
    "estimatedSavings": 0.30,
    "freeProviderUsagePercent": 66.67
  }
}
```

### Admin Endpoints

#### Get System Monitoring Data
```http
GET /api/v1/admin/monitoring
Authorization: Bearer <admin-token>
```

Response includes `providerCostBreakdown` for last 24 hours.

#### Get Monthly Cost Report
```http
GET /api/v1/admin/costs/monthly?year=2024&month=1
Authorization: Bearer <admin-token>
```

Response:
```json
{
  "year": 2024,
  "month": 1,
  "monthName": "January",
  "startDate": "2024-01-01T00:00:00Z",
  "endDate": "2024-02-01T00:00:00Z",
  "byProvider": [...],
  "totalCost": 45.67,
  "totalRequests": 1250,
  "estimatedSavings": 12.34,
  "freeProviderUsagePercent": 45.5
}
```

#### Check Cost Threshold
```http
GET /api/v1/admin/costs/threshold/{user_id}?threshold=10.0&period_days=30
Authorization: Bearer <admin-token>
```

Response:
```json
{
  "userId": "uuid",
  "periodDays": 30,
  "threshold": 10.0,
  "totalCost": 12.5,
  "exceedsThreshold": true,
  "percentageOfThreshold": 125.0,
  "byProvider": [...]
}
```

#### Get Provider Cost Breakdown
```http
GET /api/v1/admin/costs/providers?start_date=2024-01-01&end_date=2024-01-31
Authorization: Bearer <admin-token>
```

Response:
```json
{
  "byProvider": [...],
  "totalCost": 45.67,
  "totalRequests": 1250,
  "estimatedSavings": 12.34,
  "freeProviderUsagePercent": 45.5
}
```

## Database Schema

### provider_cost_breakdown Table

```sql
CREATE TABLE provider_cost_breakdown (
    id UUID PRIMARY KEY,
    request_id UUID NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    provider_name VARCHAR(100) NOT NULL,
    model_id VARCHAR(255) NOT NULL,
    subtask_count INTEGER NOT NULL DEFAULT 0,
    total_cost FLOAT NOT NULL DEFAULT 0.0,
    total_input_tokens INTEGER NOT NULL DEFAULT 0,
    total_output_tokens INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_provider_cost_request_id ON provider_cost_breakdown(request_id);
CREATE INDEX idx_provider_cost_provider_name ON provider_cost_breakdown(provider_name);
```

## Cost Calculation

### Free Providers
The following providers are considered "free" for savings calculations:
- **Ollama**: Local models, no API costs
- **HuggingFace**: Free tier with generous limits
- **Gemini**: Free tier with 60 requests/minute

### Estimated Savings
Savings are calculated by estimating what the cost would have been if free provider requests were processed by paid providers:

```python
# Average paid provider cost: $0.002 per 1000 tokens
total_free_tokens = sum(input_tokens + output_tokens for free providers)
estimated_savings = (total_free_tokens / 1000) * 0.002
```

### Free Provider Usage Percentage
```python
free_subtasks = sum(subtask_count for free providers)
total_subtasks = sum(subtask_count for all providers)
free_percentage = (free_subtasks / total_subtasks) * 100
```

## Frontend Integration

### User Dashboard
The user dashboard displays:
1. **Cost by Provider Card**: Shows top 5 providers with cost breakdown
2. **Visual Progress Bars**: Color-coded (green for free, blue for paid)
3. **Savings Summary**: Displays estimated savings and free provider usage percentage
4. **Request Count**: Number of requests per provider

### Admin Monitoring
The admin monitoring page displays:
1. **Summary Cards**: Total cost, total requests, estimated savings, free provider usage
2. **Detailed Provider List**: All providers with:
   - Cost and percentage of total
   - Request and subtask counts
   - Token usage (input/output)
   - Free/Paid badge
3. **Visual Progress Bars**: Color-coded breakdown

## Usage Examples

### Track Costs for a Request
```python
from app.services.provider_cost_tracker import get_provider_cost_tracker

tracker = get_provider_cost_tracker()

subtask_costs = [
    {
        "model_id": "groq-llama3-70b",
        "input_tokens": 100,
        "output_tokens": 50,
        "cost": 0.0001
    },
    {
        "model_id": "ollama-llama2-7b",
        "input_tokens": 200,
        "output_tokens": 100,
        "cost": 0.0  # Free
    }
]

await tracker.track_request_costs(db, request_id, subtask_costs)
```

### Get User Cost Breakdown
```python
costs = await tracker.get_provider_costs_for_user(
    db, 
    user_id,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 31)
)

print(f"Total cost: ${costs['total_cost']}")
print(f"Estimated savings: ${costs['estimated_savings']}")
print(f"Free provider usage: {costs['free_provider_usage_percent']}%")
```

### Generate Monthly Report
```python
report = await tracker.get_monthly_cost_report(
    db,
    user_id=None,  # System-wide
    year=2024,
    month=1
)

print(f"January 2024 Report:")
print(f"Total cost: ${report['total_cost']}")
for provider in report['by_provider']:
    print(f"  {provider['provider_name']}: ${provider['total_cost']}")
```

### Check Cost Threshold
```python
result = await tracker.check_cost_threshold(
    db,
    user_id,
    threshold=10.0,
    period_days=30
)

if result['exceeds_threshold']:
    print(f"Alert: User has exceeded threshold!")
    print(f"Current cost: ${result['total_cost']}")
    print(f"Threshold: ${result['threshold']}")
```

## Best Practices

### For Users
1. **Monitor Your Dashboard**: Regularly check your cost breakdown to understand spending patterns
2. **Use Free Providers**: Leverage Ollama, HuggingFace, and Gemini for cost savings
3. **Choose Execution Modes Wisely**: FAST mode uses cheaper models and fewer subtasks
4. **Review Savings**: Check your estimated savings to see the benefit of free providers

### For Administrators
1. **Set Reasonable Thresholds**: Configure cost thresholds based on expected usage
2. **Monitor System-Wide Costs**: Use the admin dashboard to track overall spending
3. **Generate Monthly Reports**: Review monthly reports to identify trends
4. **Optimize Provider Mix**: Ensure free providers are being utilized effectively
5. **Alert on Anomalies**: Set up alerts for unusual cost spikes

## Troubleshooting

### Costs Not Tracking
- Verify the `provider_cost_breakdown` table exists
- Check that the migration has been run: `alembic upgrade head`
- Ensure `track_request_costs` is called after request completion
- Verify model IDs exist in MODEL_REGISTRY

### Incorrect Savings Calculation
- Verify free provider list is up to date
- Check token counts are being recorded correctly
- Ensure the savings calculation formula is current

### Missing Provider Data
- Confirm provider name matches MODEL_REGISTRY
- Check that subtask costs include all required fields
- Verify database constraints are not blocking inserts

## Future Enhancements

1. **Cost Predictions**: Predict future costs based on historical usage
2. **Budget Limits**: Set hard limits on spending per user
3. **Cost Optimization Suggestions**: Recommend cheaper providers for specific tasks
4. **Detailed Token Analytics**: Break down token usage by task type
5. **Export Reports**: Export cost reports as CSV or PDF
6. **Real-Time Alerts**: Send email/SMS alerts when thresholds are exceeded
7. **Cost Comparison**: Compare costs across different execution modes
8. **Provider Performance**: Correlate cost with response quality and speed

## Related Documentation

- [Provider Configuration](./PROVIDER_CONFIGURATION.md)
- [Provider Health Monitoring](./PROVIDER_HEALTH_MONITORING.md)
- [Dynamic Provider Selection](./DYNAMIC_PROVIDER_SELECTION.md)
- [Admin API Documentation](./ADMIN_API.md)
- [User API Documentation](./USER_API.md)
