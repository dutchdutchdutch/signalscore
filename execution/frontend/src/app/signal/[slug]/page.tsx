'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { Footer } from '@/components/ui/Footer';
import { ScoreDisplay, categoryColors } from '@/components/ui/ScoreDisplay';
import { UrlSubmissionForm } from '@/components/features/UrlSubmissionForm';
import { scoresApi, ApiError } from '@/lib/api-client';
import type { ScoreResponse } from '@/lib/api-client/schema';

// --- Constants & Reference Data ---

const WEIGHTS: Record<string, number> = {
  ai_keywords: 0.10,
  agentic_signals: 0.20,
  tool_stack: 0.20,
  non_eng_ai: 0.40,
  ai_in_it: 0.10,
};

const CATEGORY_INFO = {
  ai_keywords: {
    label: 'AI Keywords',
    description: 'AI plans and success evidence from website, news, investor relations, and press releases.'
  },
  agentic_signals: {
    label: 'Agentic Signals',
    description: 'Evidence of autonomous agents workflows and advanced automation.'
  },
  tool_stack: {
    label: 'Modern Tool Stack',
    description: 'Adoption of leading AI/ML frameworks and tools.'
  },
  non_eng_ai: {
    label: 'AI in Non-Engineering Roles',
    description: 'Presence of AI-focused roles outside of engineering (Product, Design, Ethics).'
  },
  ai_in_it: {
    label: 'AI in IT',
    description: 'AI adoption in engineering: platform teams, engineering job descriptions, and engineering blogs.'
  }
};

const SIGNAL_SCALE = [
  { label: 'Transformational', level: 'transformational', range: '95-100', desc: 'Industry-leading AI adoption with agentic workflows.' },
  { label: 'Leading', level: 'high', range: '80-94', desc: 'Strong AI integration across products and teams.' },
  { label: 'Operational', level: 'medium_high', range: '60-79', desc: 'Active AI pilots and modernization efforts.' },
  { label: 'Lagging', level: 'medium_low', range: '30-59', desc: 'Early exploration or isolated experiments.' },
  { label: 'No Signal', level: 'no_signal', range: '0-29', desc: 'Minimal or no detectable public AI activity.' },
];

// --- Helpers ---

function normalizeSourceLabel(s: string): string {
  const normalized = s.toLowerCase();
  if (normalized === 'manual_rescore' || normalized === 'manual rescore') {
    return 'URL Submission';
  }
  return s;
}

// --- Components ---

function Header() {
  return (
    <header className="page-header">
      <div className="container">
        <Link href="/" className="logo">
          SignalScore
        </Link>
      </div>
      <style jsx>{`
        .page-header {
          padding: 20px 0;
          border-bottom: 1px solid var(--color-border);
          margin-bottom: 40px;
        }
        .container {
          max-width: 800px;
          margin: 0 auto;
          padding: 0 24px;
        }
        .logo {
          font-weight: 700;
          font-size: 20px;
          color: var(--color-primary);
          text-decoration: none;
        }
      `}</style>
    </header>
  );
}

function NotFoundState() {
  return (
    <div className="not-found-container">
      <div className="not-found-content">
        <div className="icon">🔍</div>
        <h1>Company Not Found</h1>
        <p>
          We couldn&apos;t find a score for easy access.
          Please go back home to start a fresh analysis.
        </p>
        <Link href="/" className="cta-button">
          Analyze Company
        </Link>
      </div>
      <style jsx>{`
        .not-found-container {
          display: flex;
          justify-content: center;
          align-items: center;
          min-height: 60vh;
          text-align: center;
        }
        .not-found-content {
          max-width: 400px;
          padding: 40px;
        }
        .icon {
          font-size: 48px;
          margin-bottom: 20px;
        }
        h1 {
          margin-bottom: 16px;
          font-size: 24px;
          color: var(--color-text-primary);
        }
        p {
          color: var(--color-text-secondary);
          margin-bottom: 32px;
          line-height: 1.6;
        }
        .cta-button {
          display: inline-block;
          background: var(--color-primary);
          color: white;
          padding: 12px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-weight: 600;
          transition: opacity 0.2s;
        }
        .cta-button:hover {
          opacity: 0.9;
        }
      `}</style>
    </div>
  );
}

// --- Main Page Component ---

export default function SignalDetailPage({ params }: { params: { slug: string } }) {
  const [score, setScore] = useState<ScoreResponse | null>(null);
  const [showSubmission, setShowSubmission] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Convert slug to domain (www-stripe-com -> www.stripe.com)
  const domain = params.slug.replace(/-/g, '.');

  async function fetchScore(showLoading = true) {
    try {
      if (showLoading) setLoading(true);
      // Clean up domain if user manually removed www- or similar edge cases
      // But mainly rely on the backend finding it by name/domain
      const data = await scoresApi.get(domain);
      setScore(data);
    } catch (err) {
      if (err instanceof ApiError && err.status === 404) {
        setError('not_found');
      } else {
        setError('error');
        console.error(err);
      }
    } finally {
      if (showLoading) setLoading(false);
    }
  }

  useEffect(() => {
    if (domain) {
      fetchScore(true);
    }
  }, [domain]);

  if (loading) {
    return (
      <div className="loading-state">
        <Header />
        <div className="spinner">Loading...</div>
        <style jsx>{`
          .loading-state { text-align: center; color: var(--color-text-secondary); }
          .spinner { margin-top: 100px; }
        `}</style>
      </div>
    );
  }

  if (error === 'not_found') {
    return (
      <>
        <Header />
        <NotFoundState />
      </>
    );
  }

  if (error || !score) {
    return (
      <div className="error-state">
        <Header />
        <div className="container">
          <h1>Something went wrong</h1>
          <p>Unable to load signal data. Please try again.</p>
          <Link href="/">Go Home</Link>
        </div>
        <style jsx>{`
            .container { max-width: 800px; margin: 0 auto; padding: 40px 24px; text-align: center; }
         `}</style>
      </div>
    );
  }

  return (
    <div className="page-container">
      <Header />

      <main className="main-content">
        {/* Core Identity & Score */}
        <section className="hero-section">
          <div className="score-wrapper">
            <ScoreDisplay score={score} size="large" />
          </div>
          <div className="company-details">
            <h1>{score.company_name}</h1>
            <div className="meta">
              <span className="domain">{domain}</span>
              {score.scored_at && (
                <span className="date">
                  Scored: {new Date(score.scored_at).toLocaleDateString('en-GB', {
                    day: 'numeric', month: 'short', year: 'numeric'
                  })}
                </span>
              )}
            </div>
            <button
              className="improve-score-cta"
              onClick={() => setShowSubmission(!showSubmission)}
            >
              Improve Score <span className="arrow">↑</span>
            </button>
          </div>
          {score.signals.marketing_only && (
            <div className="marketing-warning">
              <span className="warning-icon">⚠️</span>
              <div className="warning-content">
                <strong>Potential Marketing-Only Signals</strong>
                <p>High AI claims on homepage/press, but minimal engineering footprint (GitHub/Tech Blog) detected.</p>
              </div>
            </div>
          )}

        </section>

        {/* Sources Section (Deep Discovery) */}
        {score.sources && score.sources.length > 0 && (
          <section className="sources-section">
            <h2>Deep Research Sources</h2>
            <div className="sources-grid">
              {score.sources.map((source, idx) => (
                <a key={idx} href={source.url} target="_blank" rel="noopener noreferrer" className="source-card">
                  <div className="source-icon">
                    {source.source_type === 'github' ? '📦' :
                      source.source_type === 'engineering_blog' ? '📝' :
                        source.source_type === 'conference_speaking' ? '🎤' :
                          '🌐'}
                  </div>
                  <div className="source-info">
                    <span className="source-type">
                      {source.source_type.replace(/_/g, ' ')}
                    </span>
                    <span className="source-url">{new URL(source.url).hostname}</span>
                  </div>
                </a>
              ))}
            </div>
          </section>
        )}

        {/* Story 5-7: User URL Submission */}
        {score.company_id && showSubmission && (
          <section className="submission-section">
            <UrlSubmissionForm
              companyId={score.company_id}
              companyName={score.company_name}
              onSuccess={() => fetchScore(false)}
            />
          </section>
        )}

        {/* Category Breakdown */}
        <section className="breakdown-section">
          <h2>Score Breakdown</h2>


          <div className="table-container">
            <table className="breakdown-table">
              <thead>
                <tr>
                  <th className="th-category">Category</th>
                  <th className="th-desc">Description</th>
                  <th className="th-score">Score<br />0-100</th>
                  <th className="th-weight">Weight</th>
                  <th className="th-contrib">Signal Boost</th>
                  <th className="th-sources">Src</th>
                </tr>
              </thead>
              <tbody>
                {(() => {
                  // Normalize legacy keys, then iterate in weight order (high to low)
                  const normalized: Record<string, number> = {};
                  for (const [k, v] of Object.entries(score.component_scores)) {
                    const nk = k === 'ai_platform_team' ? 'ai_in_it' : k;
                    normalized[nk] = v;
                  }
                  const CATEGORY_ORDER = ['non_eng_ai', 'agentic_signals', 'tool_stack', 'ai_in_it', 'ai_keywords'];
                  return CATEGORY_ORDER.filter(k => k in normalized).map(key => {
                  const value = normalized[key] ?? 0;
                  const info = CATEGORY_INFO[key as keyof typeof CATEGORY_INFO] || { label: key, description: '' };
                  const weight = WEIGHTS[key] || 0;
                  const contribution = value * weight;

                  // Get sources for this component
                  const sources = score.signals.source_attribution?.[key] || [];
                  const uniqueSources = Array.from(new Set(sources.map(normalizeSourceLabel)));

                  // Determine empty state text based on score
                  const emptyText = value <= 5 ? 'Not found' : 'Standard scan';

                  // Custom label rendering for specific keys to force breaks
                  const label = key === 'non_eng_ai' ? (
                    <>AI in Non-Engineering<br />Roles</>
                  ) : info.label;

                  return (
                    <tr key={key}>
                      <td className="col-category">{label}</td>
                      <td className="col-desc">{info.description}</td>
                      <td className="col-score">{value.toFixed(1)}</td>
                      <td className="col-weight">{(weight * 100).toFixed(0)}%</td>
                      <td className="col-contrib">+{contribution.toFixed(1)}</td>
                      <td className="col-sources">
                        {uniqueSources.length > 0 ? (
                          <div
                            className="source-indicator group"
                            tabIndex={0}
                            role="button"
                            aria-label={`View ${uniqueSources.length} sources: ${uniqueSources.join(', ')}`}
                          >
                            <div className="source-badge">
                              {uniqueSources.length}
                            </div>
                            {/* Tooltip */}
                            <div className="source-tooltip" role="tooltip">
                              <div className="tooltip-header">Sources</div>
                              {uniqueSources.map(s => (
                                <div key={s} className="tooltip-item">
                                  • {s.replace(/_/g, ' ')}
                                </div>
                              ))}
                            </div>
                          </div>
                        ) : (
                          <div
                            className="source-indicator group"
                            tabIndex={0}
                            role="button"
                            aria-label={`No sources: ${emptyText}`}
                          >
                            <span className="source-none">-</span>
                            <div className="source-tooltip" role="tooltip">
                              <div className="tooltip-item">
                                {emptyText}
                              </div>
                            </div>
                          </div>
                        )}
                      </td>
                    </tr>
                  );
                });
                })()}
              </tbody>
            </table>
          </div>
          <div className="disclaimer">
            Scores derive from public data: job postings, blog posts, public repos, news. Internal reality may differ.
          </div>
        </section>

        {/* Reference Scale */}
        <section className="scale-section">
          <h2>Score Reference</h2>
          <div className="scale-list">
            {SIGNAL_SCALE.map((item) => (
              <div key={item.level} className="scale-item">
                <div className="scale-badge" style={{
                  color: categoryColors[item.level]?.text || '#ccc',
                  borderColor: categoryColors[item.level]?.text || '#ccc'
                }}>
                  {item.label}
                </div>
                <div className="scale-range">{item.range}</div>
                <div className="scale-desc">{item.desc}</div>
              </div>
            ))}
          </div>
        </section>

      </main>

      <Footer />

      <style jsx>{`
        .page-container {
          min-height: 100vh;
          background: var(--color-background);
          color: var(--color-text-primary);
        }
        .main-content {
          max-width: 800px;
          margin: 0 auto;
          padding: 0 24px 60px;
        }
        
        /* Hero */
        .hero-section {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: 16px;
          padding: 40px;
          display: flex;
          align-items: center;
          gap: 40px;
          margin-bottom: 40px;
          position: relative; /* For absolute positioning of CTA */
        }
        .company-details {
          flex: 1; /* Allow details to take available space */
        }
        .company-details h1 {
          font-size: 32px;
          margin: 0 0 8px 0;
        }
        .meta {
          display: flex;
          gap: 16px;
          color: var(--color-text-secondary);
          font-family: var(--font-mono);
          font-size: 14px;
        }
        
        .improve-score-cta {
          position: absolute;
          top: 40px;
          right: 40px;
          background: transparent;
          border: 1px solid var(--color-border); /* Subtle border */
          color: var(--color-text-secondary);
          padding: 6px 12px;
          border-radius: 6px;
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          align-items: center;
          gap: 6px;
          z-index: 10;
        }
        .improve-score-cta:hover {
          color: var(--color-text-primary);
          border-color: var(--color-text-primary);
          background: transparent;
        }
        .arrow {
          font-size: 14px;
        }
        


        /* Sources */
        .sources-section { margin-bottom: 40px; }
        .submission-section { margin-bottom: 40px; }
        .sources-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          gap: 16px;
        }
        .source-card {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 16px;
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: 12px;
          text-decoration: none;
          color: inherit;
          transition: border-color 0.2s, transform 0.2s;
        }
        .source-card:hover {
          border-color: var(--color-primary);
          transform: translateY(-2px);
        }
        .source-icon { font-size: 24px; }
        .source-info { display: flex; flex-direction: column; }
        .source-type { font-weight: 600; font-size: 14px; text-transform: capitalize; }
        .source-url { font-size: 12px; color: var(--color-text-secondary); }

        /* Breakdown */
        .breakdown-section { margin-bottom: 40px; }
        .disclaimer {
          background: rgba(107, 114, 128, 0.1);
          color: var(--color-text-secondary);
          padding: 12px 16px;
          border-radius: 8px;
          font-size: 14px;
          margin-bottom: 24px;
        }
        .table-container {
          overflow-x: auto;
          margin-bottom: 24px;
          border-radius: 12px;
          border: 1px solid var(--color-border);
          overflow: visible; /* Allow tooltips to overflow */
        }
        .breakdown-table {
          width: 100%;
          border-collapse: collapse;
          border-spacing: 0;
          background: var(--color-surface);
          min-width: 600px;
        }
        th, td {
          text-align: left;
          padding: 16px;
          border-bottom: 1px solid var(--color-border);
          vertical-align: middle;
        }
        th {
          background: var(--color-surface-alt);
          font-size: 11px;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--color-text-secondary);
          font-weight: 600;
        }
        tr:last-child td { border-bottom: none; }
        
        /* Columns */
        .th-category, .col-category { width: 22%; font-weight: 600; color: var(--color-text-primary); font-size: 14px; }
        .th-desc, .col-desc { font-size: 13px; color: var(--color-text-secondary); line-height: 1.4; }
        .th-score, .col-score, .th-weight, .col-weight { 
          width: 12%; 
          text-align: center; 
          font-family: var(--font-mono); 
          color: var(--color-text-secondary);
        }
        .th-score, .th-weight { font-size: 11px; }
        .col-score, .col-weight { font-size: 15px; }
        .th-contrib, .col-contrib { 
          width: 15%; 
          text-align: right; 
          font-family: var(--font-mono); 
          font-weight: 700; 
          color: var(--color-primary); 
          font-size: 15px;
        }
        .th-sources, .col-sources {
            width: 8%; /* Minimal width */
            text-align: center;
            padding: 16px 8px;
        }

        /* Tooltip Components */
        .source-indicator {
          position: relative;
          display: inline-flex;
          justify-content: center;
          cursor: help;
        }
        .source-badge {
          width: 24px;
          height: 24px;
          background: var(--color-surface-alt);
          border: 1px solid var(--color-border);
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 11px;
          font-weight: 600;
          color: var(--color-text-secondary);
          transition: all 0.2s;
        }
        .source-indicator:hover .source-badge {
          background: var(--color-primary);
          color: white;
          border-color: var(--color-primary);
        }

        .source-tooltip {
          position: absolute;
          bottom: 100%;
          left: 50%;
          transform: translateX(-50%) translateY(-8px);
          background: #1f2937; /* Dark tooltip */
          color: white;
          padding: 8px 12px;
          border-radius: 6px;
          font-size: 12px;
          white-space: nowrap;
          z-index: 50;
          box-shadow: 0 4px 12px rgba(0,0,0,0.2);
          opacity: 0;
          visibility: hidden;
          transition: all 0.2s;
          pointer-events: none;
        }
        .source-indicator:hover .source-tooltip {
          opacity: 1;
          visibility: visible;
          transform: translateX(-50%) translateY(-4px);
        }
        /* Arrow for tooltip */
        .source-tooltip::after {
          content: '';
          position: absolute;
          top: 100%;
          left: 50%;
          margin-left: -5px;
          border-width: 5px;
          border-style: solid;
          border-color: #1f2937 transparent transparent transparent;
        }

        .source-indicator:hover .source-tooltip,
        .source-indicator:focus .source-tooltip {
          opacity: 1;
          visibility: visible;
          transform: translateX(-50%) translateY(-4px);
        }
        .source-indicator:focus {
           outline: none;
        }
        .source-indicator:focus .source-badge,
        .source-indicator:focus .source-none {
           box-shadow: 0 0 0 2px var(--color-primary);
           border-radius: 4px;
        }
        .source-indicator:focus .source-badge {
           border-radius: 50%;
        }

        .tooltip-header {
          font-weight: 600;
          margin-bottom: 4px;
          border-bottom: 1px solid rgba(255,255,255,0.2);
          padding-bottom: 2px;
          font-size: 10px;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          color: rgba(255,255,255,0.8);
        }
        .tooltip-item {
          text-transform: capitalize;
          line-height: 1.4;
        }

        .source-none {
          color: var(--color-text-secondary);
          opacity: 0.3;
          font-size: 12px;
        }

        .marketing-warning {
            margin-top: 20px;
            background: #fffbeb;
            border: 1px solid #fcd34d;
            border-radius: 8px;
            padding: 16px;
            display: flex;
            gap: 12px;
            color: #92400e;
        }
        .warning-icon { font-size: 20px; }
        .warning-content strong { display: block; margin-bottom: 4px; font-size: 14px; }
        .warning-content p { margin: 0; font-size: 13px; opacity: 0.9; }

        /* Scale */
        .scale-section { margin-bottom: 60px; }
        .scale-list {
          background: var(--color-surface);
          border-radius: 12px;
          border: 1px solid var(--color-border);
          overflow: hidden;
        }
        .scale-item {
          display: flex;
          align-items: center;
          padding: 16px;
          border-bottom: 1px solid var(--color-border);
          gap: 16px;
        }
        .scale-item:last-child { border-bottom: none; }
        .scale-badge {
          font-size: 12px;
          font-weight: 700;
          text-transform: uppercase;
          padding: 4px 8px;
          border: 1px solid currentColor;
          border-radius: 4px;
          min-width: 140px;
          text-align: center;
        }
        .scale-desc {
          font-size: 14px;
          color: var(--color-text-secondary);
        }

@media (max-width: 640px) {
          .hero-section {
            flex-direction: column;
            text-align: center;
            padding: 24px;
          }
          .scale-item {
            flex-direction: column;
            align-items: flex-start;
            gap: 8px;
          }
        }

        .breakdown-section h2,
        .scale-section h2 {
          text-align: left;
          font-size: 13px;
          color: var(--color-text-secondary);
          text-transform: uppercase;
          letter-spacing: 0.05em;
          margin-bottom: 6px;
          font-weight: 600;
        }
      `}</style>
    </div>
  );
}
