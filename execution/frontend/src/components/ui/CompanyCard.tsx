'use client';

/**
 * Company Card Component - Score-First Layout
 * 
 * Displays a company with prominent score visualization.
 * Score is the visual hero, company info is secondary.
 */

import type { Company, ScoreResponse } from '@/lib/api-client/schema';
import Link from 'next/link';
import { ScoreDisplay } from './ScoreDisplay';

interface CompanyCardProps {
  company: Company;
  score?: ScoreResponse;
  onClick?: (company: Company) => void;
}

export function CompanyCard({ company, score, onClick }: CompanyCardProps) {
  const handleClick = (e: React.MouseEvent) => {
    // If onClick is provided, call it. 
    // Note: If wrapped in Link, both might fire.
    // Usually we prefer Link for navigation and onClick for tracking/state.
    if (onClick) onClick(company);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      // let Link handle navigation
    }
  };

  // Safe domain extraction - prefer normalized domain field over URL parsing
  let domain: string | null = null;
  let hostname: string | null = null;

  // Use company.domain (normalized root domain like "google.com") if available
  if (company.domain) {
    domain = company.domain;
    hostname = company.domain;
  } else if (company.url) {
    // Fallback to URL parsing for legacy records
    try {
      const parsed = new URL(company.url);
      hostname = parsed.hostname.replace('www.', '');
      domain = hostname;
    } catch {
      domain = company.url;
    }
  }

  // Generate slug for detail page using normalized domain
  const slug = domain ? domain.replace(/\./g, '-') : null;

  // Card content wrapper
  const CardContent = (
    <div
      className="company-card"
      onClick={handleClick}
      role="article"
      aria-label={`View ${company.name}${score ? `, AI Score: ${score.score}` : ''}`}
    >
      {/* Score Display - Visual Hero */}
      {score ? (
        <div className="score-section">
          <ScoreDisplay score={score} size="large" />
        </div>
      ) : (
        <div className="score-section score-placeholder">
          <div className="placeholder-circle">
            <span>?</span>
          </div>
          <span className="placeholder-label">No Score</span>
        </div>
      )}

      {/* Company Info - Secondary */}
      <div className="company-info">
        <h3 className="company-name">{company.name}</h3>
        {domain && (
          <span className="company-domain">{domain}</span>
        )}
        {score?.scored_at && (
          <span className="score-date">
            Scored: {new Date(score.scored_at).toLocaleDateString('en-GB', {
              day: 'numeric',
              month: 'short',
              year: 'numeric'
            })}
          </span>
        )}
      </div>

      {/* Link Affordance */}
      <div className="company-link-affordance">
        <span className="link-text">Scorecard</span>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="link-icon">
          <path d="M5 12h14M12 5l7 7-7 7" />
        </svg>
      </div>

      <style jsx>{`
        .company-card {
          display: flex;
          align-items: center;
          gap: 20px;
          padding: 20px 24px;
          background: var(--color-surface-alt);
          border: 1px solid var(--color-border);
          border-radius: 12px;
          cursor: pointer;
          transition: all 0.2s ease;
          position: relative;
          color: inherit;
          text-decoration: none;
        }

        .company-card:hover {
          background: var(--color-surface);
          border-color: var(--color-primary);
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
        }

        .company-card:focus {
          outline: none;
          border-color: var(--color-primary);
          box-shadow: 0 0 0 2px rgba(255, 255, 255, 0.1);
        }

        .score-section {
          flex-shrink: 0;
        }

        .score-placeholder {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
        }

        .placeholder-circle {
          width: 96px;
          height: 96px;
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          background: rgba(107, 114, 128, 0.1);
          border: 3px dashed rgba(107, 114, 128, 0.3);
        }

        .placeholder-circle span {
          font-size: 28px;
          font-weight: 600;
          color: var(--color-text-secondary);
        }

        .placeholder-label {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: var(--color-text-secondary);
        }

        .company-info {
          flex: 1;
          display: flex;
          flex-direction: column;
          gap: 4px;
          min-width: 0;
        }

        .company-name {
          margin: 0;
          font-size: 18px;
          font-weight: 600;
          color: var(--color-text-primary);
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
        }

        .company-domain {
          font-size: 14px;
          color: var(--color-text-secondary);
          font-family: var(--font-mono);
        }

        .score-date {
          font-size: 12px;
          color: var(--color-text-secondary);
          opacity: 0.7;
        }

        .company-link-affordance {
          flex-shrink: 0;
          display: flex;
          align-items: center;
          gap: 6px;
          color: var(--color-text-secondary);
          transition: transform 0.2s ease, color 0.2s ease;
        }

        .link-text {
          font-size: 13px;
          font-weight: 600;
          color: var(--color-primary);
          display: none; /* Hidden on desktop by default */
        }

        .link-icon {
          transition: transform 0.2s ease;
        }

        /* Desktop Hover: Arrow moves, color changes */
        .company-card:hover .company-link-affordance {
          color: var(--color-primary);
        }
        
        .company-card:hover .link-icon {
          transform: translateX(4px);
        }

        @media (max-width: 640px) {
          .link-text {
            display: block; /* Show text on mobile */
          }
          
          .company-link-affordance {
            color: var(--color-primary); /* Always primary on mobile */
          }
        }

        @media (max-width: 480px) {
          .company-card {
            gap: 16px;
            padding: 16px;
          }

          .company-name {
            font-size: 16px;
          }

          .placeholder-circle {
            width: 64px;
            height: 64px;
          }

          .placeholder-circle span {
            font-size: 24px;
          }
        }
      `}</style>
    </div>
  );

  if (slug) {
    return (
      <Link href={`/signal/${slug}`} style={{ textDecoration: 'none', display: 'block' }}>
        {CardContent}
      </Link>
    );
  }

  return CardContent;
}
