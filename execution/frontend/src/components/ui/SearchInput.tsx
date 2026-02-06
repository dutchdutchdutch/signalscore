'use client';

/**
 * Search Input Component - System Minimal Design
 * 
 * Features:
 * - Clean, borderless design with subtle underline
 * - Keyboard shortcuts (/ to focus)
 * - Loading state indicator
 */

import { forwardRef, useEffect, useRef } from 'react';

interface SearchInputProps {
    value: string;
    onChange: (value: string) => void;
    placeholder?: string;
    loading?: boolean;
    autoFocus?: boolean;
}

export const SearchInput = forwardRef<HTMLInputElement, SearchInputProps>(
    function SearchInput(
        { value, onChange, placeholder = "Search companies...", loading = false, autoFocus = false },
        ref
    ) {
        const inputRef = useRef<HTMLInputElement>(null);

        // Keyboard shortcut: "/" to focus search
        useEffect(() => {
            function handleKeyDown(e: KeyboardEvent) {
                if (e.key === '/' && document.activeElement !== inputRef.current) {
                    e.preventDefault();
                    inputRef.current?.focus();
                }
            }

            document.addEventListener('keydown', handleKeyDown);
            return () => document.removeEventListener('keydown', handleKeyDown);
        }, []);

        return (
            <div className="search-input-container">
                <div className="search-input-wrapper">
                    {/* Search Icon */}
                    <svg
                        className="search-icon"
                        width="20"
                        height="20"
                        viewBox="0 0 24 24"
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="2"
                    >
                        <circle cx="11" cy="11" r="8" />
                        <path d="M21 21l-4.35-4.35" />
                    </svg>

                    <input
                        ref={(node) => {
                            if (typeof ref === 'function') ref(node);
                            else if (ref) ref.current = node;
                            (inputRef as React.MutableRefObject<HTMLInputElement | null>).current = node;
                        }}
                        type="text"
                        value={value}
                        onChange={(e) => onChange(e.target.value)}
                        placeholder={placeholder}
                        className="search-input"
                        autoFocus={autoFocus}
                        aria-label="Search companies"
                    />

                    {/* Loading Indicator */}
                    {loading && (
                        <div className="search-loading">
                            <div className="search-loading-spinner" />
                        </div>
                    )}

                    {/* Keyboard Shortcut Hint */}
                    {!value && !loading && (
                        <kbd className="search-shortcut">/</kbd>
                    )}

                    {/* Clear Button */}
                    {value && !loading && (
                        <button
                            type="button"
                            onClick={() => onChange('')}
                            className="search-clear"
                            aria-label="Clear search"
                        >
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                <path d="M18 6L6 18M6 6l12 12" />
                            </svg>
                        </button>
                    )}
                </div>

                <style jsx>{`
          .search-input-container {
            width: 100%;
            max-width: 600px;
          }

          .search-input-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            background: var(--color-surface-alt);
            border: 1px solid var(--color-border);
            transition: border-color 0.15s ease;
          }

          .search-input-wrapper:focus-within {
            border-color: var(--color-primary);
          }

          .search-icon {
            position: absolute;
            left: 16px;
            color: var(--color-text-secondary);
            pointer-events: none;
          }

          .search-input {
            width: 100%;
            padding: 16px 48px 16px 48px;
            background: transparent;
            border: none;
            color: var(--color-text-primary);
            font-size: 16px;
            font-family: var(--font-sans);
            outline: none;
          }

          .search-input::placeholder {
            color: var(--color-text-secondary);
          }

          .search-loading {
            position: absolute;
            right: 16px;
          }

          .search-loading-spinner {
            width: 16px;
            height: 16px;
            border: 2px solid var(--color-border);
            border-top-color: var(--color-primary);
            animation: spin 0.8s linear infinite;
          }

          @keyframes spin {
            to { transform: rotate(360deg); }
          }

          .search-shortcut {
            position: absolute;
            right: 16px;
            padding: 2px 8px;
            background: var(--color-surface);
            border: 1px solid var(--color-border);
            color: var(--color-text-secondary);
            font-size: 12px;
            font-family: var(--font-mono);
          }

          .search-clear {
            position: absolute;
            right: 12px;
            padding: 4px;
            background: transparent;
            border: none;
            color: var(--color-text-secondary);
            cursor: pointer;
            transition: color 0.15s ease;
          }

          .search-clear:hover {
            color: var(--color-text-primary);
          }
        `}</style>
            </div>
        );
    }
);
