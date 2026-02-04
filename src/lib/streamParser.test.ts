import { describe, it, expect } from 'vitest';
import { parseStreamChunk } from './streamParser';

describe('parseStreamChunk', () => {
  it('should return plain text for normal chunks', () => {
    const input = 'Hello world';
    const result = parseStreamChunk(input);
    expect(result).toEqual({ text: 'Hello world' });
  });

  it('should detect error messages with [ERROR] prefix', () => {
    const input = '[ERROR] API key expired';
    const result = parseStreamChunk(input);
    expect(result).toEqual({ error: 'API key expired' });
  });

  it('should handle "data: " prefix if present', () => {
    const input = 'data: [ERROR] Something went wrong';
    const result = parseStreamChunk(input);
    expect(result).toEqual({ error: 'Something went wrong' });
  });

  it('should handle mixed data prefix and text', () => {
    const input = 'data: Just some text';
    const result = parseStreamChunk(input);
    expect(result).toEqual({ text: 'Just some text' });
  });

  it('should return empty text for empty input', () => {
    const input = '';
    const result = parseStreamChunk(input);
    expect(result).toEqual({ text: '' });
  });
});
