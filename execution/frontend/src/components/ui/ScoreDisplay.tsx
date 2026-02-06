'use client';

/**
 * Score Display Component - Prominent Score Visualization
 * 
 * Displays the AI readiness score as the dominant visual element.
 * Uses a large circular indicator with category-based colors.
 */

import type { ScoreResponse } from '@/lib/api-client/schema';

interface ScoreDisplayProps {
    score: ScoreResponse;
    size?: 'small' | 'medium' | 'large';
}

// Category color mapping - vibrant semantic colors
export const categoryColors: Record<string, { bg: string; text: string; ring: string }> = {
    transformational: {
        bg: 'rgba(147, 51, 234, 0.15)',
        text: 'rgb(168, 85, 247)',
        ring: 'rgb(147, 51, 234)',
    },
    high: {
        bg: 'rgba(34, 197, 94, 0.15)',
        text: 'rgb(34, 197, 94)',
        ring: 'rgb(22, 163, 74)',
    },
    medium_high: {
        bg: 'rgba(59, 130, 246, 0.15)',
        text: 'rgb(59, 130, 246)',
        ring: 'rgb(37, 99, 235)',
    },
    medium_low: {
        bg: 'rgba(234, 179, 8, 0.15)',
        text: 'rgb(234, 179, 8)',
        ring: 'rgb(202, 138, 4)',
    },
    low: {
        bg: 'rgba(239, 68, 68, 0.15)',
        text: 'rgb(239, 68, 68)',
        ring: 'rgb(220, 38, 38)',
    },
    no_signal: {
        bg: 'rgba(107, 114, 128, 0.15)',
        text: 'rgb(156, 163, 175)',
        ring: 'rgb(107, 114, 128)',
    },
};

const sizeConfig = {
    small: { circle: 56, font: 16, label: 10 },
    medium: { circle: 72, font: 22, label: 11 },
    large: { circle: 96, font: 26, label: 12 },
};

export function ScoreDisplay({ score, size = 'large' }: ScoreDisplayProps) {
    const colors = categoryColors[score.category] || categoryColors.no_signal;
    const dimensions = sizeConfig[size];

    return (
        <div className="score-display">
            <div
                className="score-circle"
                style={{
                    width: dimensions.circle,
                    height: dimensions.circle,
                    backgroundColor: colors.bg,
                    borderColor: colors.ring,
                }}
            >
                <span
                    className="score-value"
                    style={{
                        fontSize: dimensions.font,
                        color: colors.text,
                    }}
                >
                    {score.score}
                </span>
            </div>
            <span
                className="score-label"
                style={{
                    fontSize: dimensions.label,
                    color: colors.text,
                }}
            >
                {score.category_label}
            </span>

            <style jsx>{`
        .score-display {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 6px;
        }

        .score-circle {
          display: flex;
          align-items: center;
          justify-content: center;
          border-radius: 50%;
          border-width: 3px;
          border-style: solid;
          padding: 8px;
          transition: transform 0.2s ease, box-shadow 0.2s ease;
        }

        .score-circle:hover {
          transform: scale(1.05);
        }

        .score-value {
          font-weight: 700;
          font-family: var(--font-mono, monospace);
          line-height: 1;
        }

        .score-label {
          font-weight: 600;
          text-transform: uppercase;
          letter-spacing: 0.5px;
          white-space: nowrap;
        }
      `}</style>
        </div>
    );
}
