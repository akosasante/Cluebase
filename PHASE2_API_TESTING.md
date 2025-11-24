# Phase 2 API Testing Guide

## Testing Buzzer Metrics in Cluebase API

### Prerequisites
1. Ensure Cluebase is running (via Docker or locally)
2. Run the new migration: `jeopardy20251124_add_buzzer_penalty_metrics.sql`
3. Have a valid `played_game_id` and `clue_id` ready for testing

### Test 1: Create Answered Clue WITH Buzzer Metrics

```bash
curl -X POST http://localhost:5001/answered_clues/ \
  -H "Content-Type: application/json" \
  -d '{
    "played_game_id": 1,
    "clue_id": 100,
    "answer_state": "correct",
    "buzz_time_ms": 350,
    "penalties": 2,
    "penalty_time_ms": 750
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "id": <new_id>,
    "played_game_id": 1,
    "clue_id": 100,
    "answered_correctly": true,
    "answer_state": "correct",
    "buzz_time_ms": 350,
    "penalties": 2,
    "penalty_time_ms": 750,
    "date_answered": "<timestamp>",
    "clue": {...}
  }
}
```

### Test 2: Create Answered Clue WITHOUT Buzzer Metrics (Backward Compatibility)

```bash
curl -X POST http://localhost:5001/answered_clues/ \
  -H "Content-Type: application/json" \
  -d '{
    "played_game_id": 1,
    "clue_id": 101,
    "answer_state": "incorrect"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "data": {
    "id": <new_id>,
    "played_game_id": 1,
    "clue_id": 101,
    "answered_correctly": false,
    "answer_state": "incorrect",
    "buzz_time_ms": null,
    "penalties": 0,
    "penalty_time_ms": 0,
    "date_answered": "<timestamp>",
    "clue": {...}
  }
}
```

### Test 3: Validation - Negative buzz_time_ms

```bash
curl -X POST http://localhost:5001/answered_clues/ \
  -H "Content-Type: application/json" \
  -d '{
    "played_game_id": 1,
    "clue_id": 102,
    "answer_state": "correct",
    "buzz_time_ms": -100
  }'
```

**Expected Response:**
```json
{
  "status": "failure",
  "error": "buzz_time_ms must be a non-negative integer."
}
```

### Test 4: Validation - Invalid penalties type

```bash
curl -X POST http://localhost:5001/answered_clues/ \
  -H "Content-Type: application/json" \
  -d '{
    "played_game_id": 1,
    "clue_id": 103,
    "answer_state": "correct",
    "penalties": "abc"
  }'
```

**Expected Response:**
```json
{
  "status": "failure",
  "error": "penalties must be a valid integer."
}
```

### Test 5: GET Answered Clues (Verify buzzer metrics in response)

```bash
curl http://localhost:5001/answered_clues/?played_game_id=1
```

**Expected Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "played_game_id": 1,
      "clue_id": 100,
      "answered_correctly": true,
      "answer_state": "correct",
      "buzz_time_ms": 350,
      "penalties": 2,
      "penalty_time_ms": 750,
      ...
    },
    {
      "id": 2,
      "played_game_id": 1,
      "clue_id": 101,
      "answered_correctly": false,
      "answer_state": "incorrect",
      "buzz_time_ms": null,
      "penalties": 0,
      "penalty_time_ms": 0,
      ...
    }
  ]
}
```

## Database Verification

Connect to PostgreSQL and verify the data:

```sql
\c jeopardy

-- Check table structure
\d answered_clues

-- Verify data
SELECT id, clue_id, answer_state, buzz_time_ms, penalties, penalty_time_ms
FROM answered_clues
WHERE played_game_id = 1
ORDER BY id DESC
LIMIT 5;
```

## Integration Test with Phoenix Server

After Phase 2 is complete, test end-to-end from Phoenix:

1. Start Arduino board and Phoenix server
2. Play a clue and buzz in
3. Mark answer as correct/incorrect
4. Verify in Cluebase database that buzzer metrics were stored
5. Retrieve answered clues via GET endpoint and confirm metrics present

## Expected Database Schema After Migration

```
answered_clues table columns:
- id (integer, PK)
- played_game_id (integer, FK)
- clue_id (integer, FK)
- answered_correctly (boolean)
- answer_state (enum)
- buzz_time_ms (integer, nullable) -- Time to buzz in ms
- penalties (integer, NOT NULL, default 0) -- Number of early buzz penalties
- penalty_time_ms (integer, NOT NULL, default 0) -- Total penalty duration in ms
- date_answered (timestamp)
```

## Notes

- `buzz_time_ms` is nullable (can be NULL for manual/non-buzzer answers)
- `penalties` and `penalty_time_ms` default to 0 (never NULL)
- All three fields are optional in POST requests (backward compatible)
- Validation ensures non-negative integers when provided
- Phoenix server already sends these fields per Phase 1 implementation
