/**
 * Phase 1's /api/chat/ is a single synchronous response -- there is no
 * token-streaming endpoint. This drives a client-side simulated "retrieval
 * in progress" sequence while the real request is in flight, and a
 * typewriter reveal once the real answer arrives. Neither invents data;
 * both are purely presentational.
 */
export const RETRIEVAL_STATUS_STEPS = [
  'Searching internal knowledge...',
  'Checking trusted sources...',
  'Verifying evidence...',
]

export const RETRIEVAL_STATUS_INTERVAL_MS = 900

export const TYPEWRITER_CHARS_PER_TICK = 3
export const TYPEWRITER_TICK_MS = 16
