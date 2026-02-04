export interface StreamResult {
  text?: string;
  error?: string;
}

/**
 * Parses a chunk from the backend stream.
 * Detects error messages prefixed with [ERROR].
 */
export function parseStreamChunk(chunk: string): StreamResult {
  if (!chunk) return { text: '' };

  // Remove SSE "data: " prefix if it exists
  let cleanChunk = chunk;
  if (chunk.startsWith('data: ')) {
    cleanChunk = chunk.substring(6);
  }

  // Check for [ERROR] marker
  if (cleanChunk.startsWith('[ERROR]')) {
    const errorMessage = cleanChunk.substring(7).trim();
    return { error: errorMessage };
  }

  return { text: cleanChunk };
}
