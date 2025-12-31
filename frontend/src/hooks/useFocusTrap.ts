import { useEffect, useRef } from 'react';

interface UseFocusTrapOptions {
  closeOnEscape?: boolean;
}

export const useFocusTrap = (
  isOpen: boolean,
  onClose: () => void,
  options: UseFocusTrapOptions = {}
) => {
  const { closeOnEscape = false } = options;
  const modalRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
        return;
      }

      if (e.key === 'Tab') {
        const modal = modalRef.current;
        if (!modal) return;

        const focusableElements = modal.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[
          focusableElements.length - 1
        ] as HTMLElement;

        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            e.preventDefault();
            lastElement.focus();
          }
        } else {
          if (document.activeElement === lastElement) {
            e.preventDefault();
            firstElement.focus();
          }
        }
      }
    };

    const handleFocusIn = (e: FocusEvent) => {
      const modal = modalRef.current;
      if (!modal) return;

      // Only redirect focus if it moves completely outside the modal
      // This prevents focus from leaving the modal but doesn't interfere with typing
      if (!modal.contains(e.target as Node)) {
        e.preventDefault();
        const firstFocusable = modal.querySelector(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        ) as HTMLElement | null;
        if (firstFocusable !== null) {
          firstFocusable.focus();
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('focusin', handleFocusIn);

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('focusin', handleFocusIn);
    };
  }, [isOpen, onClose, closeOnEscape]);

  return modalRef;
};
