# REST API Specification for BudgetBot


## Endpoints Table

| Method | Endpoint | HTTP Code | Description | Request Body | Response |
|--------|----------|-----------|-------------|--------------|----------|
| **USER MANAGEMENT** | | | | | |
| POST | `/users` | 201 | Create new user | `{"telegram_id": 123, "username": "john", "first_name": "John", "default_currency": "RUB"}` | `{"user_id": 1, "created_at": "2024-01-01"}` |
| GET | `/users/me` | 200 | Get current user | - | `{"id": 1, "username": "john", "first_name": "John", "default_currency": "RUB"}` |
| PUT | `/users/me` | 200 | Update user | `{"first_name": "John", "default_currency": "USD"}` | `{"id": 1, "updated": true}` |
| **CATEGORIES** | | | | | |
| GET | `/categories` | 200 | Get user categories | - | `[{"id": 1, "name": "food", "type": "expense"}, {"id": 2, "name": "salary", "type": "income"}]` |
| POST | `/categories` | 201 | Create category | `{"name": "transport", "type": "expense"}` | `{"id": 3, "name": "transport", "type": "expense"}` |
| PUT | `/categories/{id}` | 200 | Update category | `{"name": "public transport"}` | `{"id": 3, "updated": true}` |
| DELETE | `/categories/{id}` | 204 | Delete category | - | - |
| **TRANSACTIONS** | | | | | |
| POST | `/transactions` | 201 | Create transaction | `{"amount": 1500, "currency": "RUB", "type": "expense", "category_id": 1, "description": "Lunch", "transaction_date": "2024-01-15"}` | `{"id": 1, "balance_after": 8500}` |
| GET | `/transactions` | 200 | Get transactions | Query: `?limit=10&offset=0&category_id=1&type=expense` | `{"transactions": [...], "total": 25}` |
| GET | `/transactions/{id}` | 200 | Get transaction | - | `{"id": 1, "amount": 1500, "type": "expense", "category": "food"}` |
| PUT | `/transactions/{id}` | 200 | Update transaction | `{"amount": 2000, "description": "Dinner"}` | `{"id": 1, "updated": true}` |
| DELETE | `/transactions/{id}` | 204 | Delete transaction | - | - |
| **BUDGETS** | | | | | |
| POST | `/budgets` | 201 | Create budget | `{"amount": 50000, "currency": "RUB", "period": "monthly", "start_date": "2024-01-01", "notifications_enabled": true}` | `{"id": 1, "created_at": "2024-01-01"}` |
| GET | `/budgets` | 200 | Get user budgets | - | `[{"id": 1, "amount": 50000, "period": "monthly", "spent": 35000}]` |
| PUT | `/budgets/{id}` | 200 | Update budget | `{"amount": 60000, "notifications_enabled": false}` | `{"id": 1, "updated": true}` |
| DELETE | `/budgets/{id}` | 204 | Delete budget | - | - |
| **ANALYTICS** | | | | | |
| GET | `/analytics/stats` | 200 | Get statistics | Query: `?period=month&type=expense` | `{"total_income": 100000, "total_expense": 75000, "by_category": [{"category": "food", "amount": 25000, "percentage": 33}]}` |
| GET | `/analytics/balance` | 200 | Get current balance | - | `{"balance": 25000, "currency": "RUB"}` |
| GET | `/analytics/budget-progress` | 200 | Budget progress | - | `{"budget_amount": 50000, "spent": 35000, "remaining": 15000, "percentage": 70}` |
| **LLM INTEGRATION** | | | | | |
| POST | `/llm/analyze-transaction` | 200 | Analyze transaction text | `{"text": "Купил продукты в пятерочке за 2500 рублей"}` | `{"amount": 2500, "currency": "RUB", "type": "expense", "category": "food", "confidence": 0.95}` |
| POST | `/llm/clarify-transaction` | 200 | Get clarification question | `{"text": "Потратил 1000", "missing_fields": ["category"]}` | `{"question": "На что вы потратили 1000 рублей?", "missing_fields": ["category"]}` |
| **HEALTH** | | | | | |
| GET | `/health` | 200 | Health check | - | `{"status": "ok", "timestamp": "2024-01-15T10:00:00Z"}` |

## Error Responses

| HTTP Code | Error Type | Response Body |
|-----------|------------|---------------|
| 400 | Bad Request | `{"error": "Invalid input", "details": {"amount": "Must be positive number"}}` |
| 401 | Unauthorized | `{"error": "Authentication required"}` |
| 403 | Forbidden | `{"error": "Access denied"}` |
| 404 | Not Found | `{"error": "Resource not found"}` |
| 409 | Conflict | `{"error": "Category already exists"}` |
| 422 | Validation Error | `{"error": "Validation failed", "details": {...}}` |
| 500 | Internal Error | `{"error": "Internal server error"}` |

## Example Usage for AI Agent

```python
# Create transaction from analyzed text
analysis = await llm_analyze("Купил кофе за 300")
response = requests.post(
    "/transactions",
    json={
        "amount": analysis["amount"],
        "currency": "RUB", 
        "type": analysis["type"],
        "category_id": get_category_id(analysis["category"]),
        "description": analysis.get("description", "")
    },
    headers={"Authorization": f"Bearer {user_token}"}
)

if response.status_code == 201:
    return "Transaction created successfully"