'use client';

/**
 * SignalScore Homepage
 * 
 * The Glassdoor for AI Readiness.
 * Features a clean, minimal search interface.
 */

import { CompanySearch } from '@/components/features/CompanySearch';
import { Footer } from '@/components/ui/Footer';

export default function Home() {
  return (
    <main className="home">
      {/* Hero Section */}
      <section className="hero">
        <h1 className="hero-title">SignalScore</h1>
        <p className="hero-subtitle">
          Leading or lagging in the AI race?        </p>
        <p className="hero-description">
          Search by company URL to see their AI readiness score
          {process.env.NEXT_PUBLIC_APP_STAGE ? ` (${process.env.NEXT_PUBLIC_APP_STAGE.toLowerCase()})` : ''}.
        </p>
      </section>

      {/* Search Section */}
      <section className="search-section">
        <CompanySearch />
      </section>

      <div className="spacer" />



      <Footer />

      <style jsx>{`
        .home {
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          padding: 80px 24px;
          background: var(--color-surface);
        }

        .hero {
          text-align: center;
          max-width: 600px;
          margin-bottom: 48px;
        }

        .hero-title {
          margin: 0 0 8px 0;
          font-size: 48px;
          font-weight: 600;
          color: var(--color-text-primary);
          letter-spacing: -0.02em;
        }

        .hero-subtitle {
          margin: 0 0 16px 0;
          font-size: 20px;
          color: var(--color-text-secondary);
          font-weight: 400;
        }

        .hero-description {
          margin: 0;
          font-size: 16px;
          color: var(--color-text-secondary);
          line-height: 1.6;
        }

        .search-section {
          width: 100%;
          max-width: 640px;
          display: flex;
          justify-content: center;
        }

        .spacer {
          height: 320px; /* Approx 2-3 card heights */
        }

        .hint {
          margin-top: auto;
          padding-top: 48px;
          text-align: center;
        }

        .hint p {
          margin: 0;
          font-size: 13px;
          color: var(--color-text-secondary);
        }

        .hint kbd {
          padding: 2px 6px;
          background: var(--color-surface-alt);
          border: 1px solid var(--color-border);
          font-size: 12px;
          font-family: var(--font-mono);
        }

        @media (max-width: 640px) {
          .home {
            padding: 48px 16px;
          }

          .hero-title {
            font-size: 36px;
          }

          .hero-subtitle {
            font-size: 18px;
          }
        }
      `}</style>
    </main>
  );
}
