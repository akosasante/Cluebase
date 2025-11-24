-- Migration: Add buzzer penalty metrics to answered_clues table
-- This migration adds support for tracking penalty events when buzzing in early
-- Penalties are accumulated when a player buzzes before the host activates the buzzer

\c jeopardy

-- Add penalty tracking columns to answered_clues table
ALTER TABLE public.answered_clues 
ADD COLUMN penalties INTEGER DEFAULT 0,
ADD COLUMN penalty_time_ms INTEGER DEFAULT 0;

-- Add indexes for performance on analytics queries
CREATE INDEX idx_answered_clues_penalties ON public.answered_clues(penalties) WHERE penalties > 0;

-- Add comments for documentation
COMMENT ON COLUMN public.answered_clues.penalties IS 'Number of early buzz penalty events for this clue (0 if no penalties)';
COMMENT ON COLUMN public.answered_clues.penalty_time_ms IS 'Total accumulated penalty time in milliseconds from early buzzes';

-- Update existing rows to have explicit zero values for penalties (for consistency)
UPDATE public.answered_clues 
SET penalties = 0, penalty_time_ms = 0 
WHERE penalties IS NULL OR penalty_time_ms IS NULL;

-- Make columns NOT NULL after setting defaults
ALTER TABLE public.answered_clues 
ALTER COLUMN penalties SET NOT NULL,
ALTER COLUMN penalty_time_ms SET NOT NULL;
