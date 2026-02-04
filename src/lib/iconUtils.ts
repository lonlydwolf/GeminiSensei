import { GraduationCap, FileCode, Bot, HelpCircle, type LucideIcon } from 'lucide-react';

const ICON_MAP: Record<string, LucideIcon> = {
  'GraduationCap': GraduationCap,
  'graduation-cap': GraduationCap,
  'FileCode': FileCode,
  'file-code': FileCode,
  'Bot': Bot,
  'bot': Bot,
};

/**
 * Maps a string icon name to a LucideIcon component.
 * @param iconName The name of the icon (e.g. "GraduationCap" or "graduation-cap")
 * @returns The LucideIcon component, or HelpCircle as a fallback.
 */
export function getIconComponent(iconName: string): LucideIcon {
  return ICON_MAP[iconName] || HelpCircle;
}
