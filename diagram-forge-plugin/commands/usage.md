---
name: usage
description: View diagram generation usage and cost report
arguments:
  - name: days
    description: Number of days to report on (default 30)
    required: false
  - name: group_by
    description: Group by provider, diagram_type, or day
    required: false
---

# Usage Report

Call the `get_usage_report` MCP tool to retrieve usage statistics.

## Steps

1. Call `get_usage_report` with the specified days (default 30) and group_by (default "provider").

2. Format the results as a clear table showing:
   - Total generations (successful / failed)
   - Total cost in USD
   - Breakdown by group (provider, diagram type, or day)
   - Average generation time

3. If there are no generations, suggest the user try `/diagram:create` to get started.

## Display Format

Use a markdown table for the breakdown. Example:

| Provider | Generations | Success Rate | Cost (USD) | Avg Time |
|----------|------------|-------------|------------|----------|
| gemini   | 15         | 93%         | $0.585     | 3.2s     |
| openai   | 5          | 100%        | $0.080     | 5.1s     |
