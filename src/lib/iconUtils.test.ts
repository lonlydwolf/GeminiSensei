import { describe, it, expect } from 'vitest';
import { getIconComponent } from './iconUtils';
import { GraduationCap, FileCode, Bot, HelpCircle } from 'lucide-react';

describe('getIconComponent', () => {
  it('should return GraduationCap for "GraduationCap"', () => {
    expect(getIconComponent('GraduationCap')).toBe(GraduationCap);
  });

  it('should return FileCode for "FileCode"', () => {
    expect(getIconComponent('FileCode')).toBe(FileCode);
  });

  it('should return Bot for "Bot"', () => {
    expect(getIconComponent('Bot')).toBe(Bot);
  });

  it('should return HelpCircle for unknown icon strings', () => {
    expect(getIconComponent('UnknownIcon')).toBe(HelpCircle);
  });

  it('should be case-insensitive or handle common casing', () => {
     // If we implement it to handle 'graduation-cap' as well
     expect(getIconComponent('graduation-cap')).toBe(GraduationCap);
  });
});
