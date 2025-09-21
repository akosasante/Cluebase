-- Migration: Add answer_state enum and new fields to answered_clues table
-- This migration adds support for detailed answer states including timeouts
-- File name ensures it runs after existing migrations (alphabetical order)

-- Create the AnswerState enum type
\c jeopardy

CREATE TYPE answer_state AS ENUM (
    'correct',
    'incorrect', 
    'timeout_before_buzz',
    'timeout_after_buzz',
    'skipped'
);

-- Add new columns to answered_clues table
ALTER TABLE public.answered_clues 
ADD COLUMN answer_state answer_state,
ADD COLUMN response_text TEXT,
ADD COLUMN response_time_ms INTEGER,
ADD COLUMN buzz_time_ms INTEGER;

-- Add indexes for better performance on new fields
CREATE INDEX idx_answered_clues_answer_state ON public.answered_clues(answer_state);

-- Add comments for documentation
COMMENT ON TYPE answer_state IS 'Enum representing different states of clue answers including timeouts';
COMMENT ON COLUMN public.answered_clues.answer_state IS 'New enum field for detailed answer states including timeouts';
COMMENT ON COLUMN public.answered_clues.response_text IS 'The actual response given by the player';
COMMENT ON COLUMN public.answered_clues.response_time_ms IS 'Time taken to respond after buzzing in (milliseconds)';
COMMENT ON COLUMN public.answered_clues.buzz_time_ms IS 'Time taken to buzz in after clue is revealed (milliseconds)';
