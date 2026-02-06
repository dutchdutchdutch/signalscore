'use client';

/**
 * Search Results Component
 * 
 * Displays search results with loading and empty states.
 */

import type { Company, ScoreResponse } from '@/lib/api-client/schema';
import { CompanyCard } from './CompanyCard';

interface SearchResultsProps {
  results: Company[];
  scores?: Record<string, ScoreResponse>;
  loading: boolean;
  error: string | null;
  query: string;
  onCompanyClick?: (company: Company) => void;
}

export function SearchResults({
  results,
  scores,
  loading,
  error,
  query,
  onCompanyClick,
}: SearchResultsProps) {
  // Don't show anything if no query
  if (!query.trim()) {
    return null;
  }

  // Loading state
  if (loading) {
    return (
      <div className="search-results">
        <div className="search-results-loading">
          <div className="loading-skeleton" />
          <div className="loading-skeleton" />
          <div className="loading-skeleton" />
        </div>

        <style jsx>{`
          .search-results {
            width: 100%;
            max-width: 42rem;
            margin-top: 8px;
          }

          .search-results-loading {
            display: flex;
            flex-direction: column;
            gap: 8px;
          }

          .loading-skeleton {
            height: 72px;
            background: var(--color-surface-alt);
            border: 1px solid var(--color-border);
            animation: pulse 1.5s ease-in-out infinite;
          }

          @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
          }
        `}</style>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="search-results">
        <div className="search-error">
          <span className="error-icon">⚠</span>
          <span>{error}</span>
        </div>

        <style jsx>{`
          .search-results {
            width: 100%;
            max-width: 42rem;
            margin-top: 8px;
          }

          .search-error {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 16px 20px;
            background: var(--color-surface-alt);
            border: 1px solid var(--color-error);
            color: var(--color-error);
          }

          .error-icon {
            font-size: 18px;
          }
        `}</style>
      </div>
    );
  }

  // Empty state
  if (results.length === 0) {
    return (
      <div className="search-results">
        <div className="search-empty">
          <p className="empty-title">No companies found</p>
          <p className="empty-subtitle">
            Try a different search term or add a new company
          </p>
        </div>

        <style jsx>{`
          .search-results {
            width: 100%;
            max-width: 42rem;
            margin-top: 8px;
          }

          .search-empty {
            padding: 32px 20px;
            background: var(--color-surface-alt);
            border: 1px solid var(--color-border);
            text-align: center;
          }

          .empty-title {
            margin: 0 0 8px 0;
            font-size: 16px;
            font-weight: 500;
            color: var(--color-text-primary);
          }

          .empty-subtitle {
            margin: 0;
            font-size: 14px;
            color: var(--color-text-secondary);
          }
        `}</style>
      </div>
    );
  }

  // Results list
  return (
    <div className="search-results">
      {results.length > 1 && (
        <div className="results-header">
          <span className="results-count">
            {results.length} {results.length === 1 ? 'result' : 'results'}
          </span>
        </div>
      )}

      <div className="results-list">
        {results.map((company) => (
          <CompanyCard
            key={company.id}
            company={company}
            score={scores?.[company.name]}
            onClick={onCompanyClick}
          />
        ))}
      </div>

      <style jsx>{`
        .search-results {
          width: 100%;
          max-width: 42rem;
          margin-top: 8px;
        }

        .results-header {
          padding: 8px 0;
        }

        .results-count {
          font-size: 13px;
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.5px;
        }

        .results-list {
          display: flex;
          flex-direction: column;
          gap: 8px;
        }
      `}</style>
    </div>
  );
}
