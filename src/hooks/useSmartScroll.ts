import { useEffect, useRef } from 'react';

/**
 * A hook that auto-scrolls an element to the bottom when a dependency changes,
 * but only if the user was already near the bottom of the element.
 * 
 * @param dependency The dependency that triggers the scroll (e.g. messages array)
 * @param offset The distance from the bottom in pixels to be considered "at bottom" (default: 100)
 */
export function useSmartScroll<T extends HTMLElement>(dependency: unknown, offset: number = 100) {
  const scrollRef = useRef<T>(null);
  const isAtBottomRef = useRef(true);

  useEffect(() => {
    const element = scrollRef.current;
    if (!element) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = element;
      // Use a small buffer (offset) to determine if we are at the bottom
      const distanceToBottom = scrollHeight - scrollTop - clientHeight;
      isAtBottomRef.current = distanceToBottom < offset;
    };

    element.addEventListener('scroll', handleScroll);
    // Initial check
    handleScroll();

    return () => element.removeEventListener('scroll', handleScroll);
  }, [offset]);

  useEffect(() => {
    const element = scrollRef.current;
    if (element && isAtBottomRef.current) {
      element.scrollTo({
        top: element.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [dependency]);

  return scrollRef;
}
