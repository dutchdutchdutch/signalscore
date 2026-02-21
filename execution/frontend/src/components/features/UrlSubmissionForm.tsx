'use client';

import { useState } from 'react';
import { companiesApi, ApiError } from '@/lib/api-client';

interface UrlSubmissionFormProps {
  companyId: number;
  companyName: string;
  onSuccess?: () => void;
}

export function UrlSubmissionForm({ companyId, companyName, onSuccess }: UrlSubmissionFormProps) {
  const [urls, setUrls] = useState<string[]>(['']); // Start with one empty field
  const [submitting, setSubmitting] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleUrlChange = (index: number, value: string) => {
    const newUrls = [...urls];
    newUrls[index] = value;
    setUrls(newUrls);
  };

  const addField = () => {
    if (urls.length < 3) {
      setUrls([...urls, '']);
    }
  };

  const removeField = (index: number) => {
    const newUrls = urls.filter((_, i) => i !== index);
    setUrls(newUrls.length ? newUrls : ['']);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);

    // Filter empty URLs
    const validUrls = urls.map(u => u.trim()).filter(u => u.length > 0);

    if (validUrls.length === 0) {
      setMessage({ type: 'error', text: 'Please enter at least one URL.' });
      return;
    }

    try {
      setSubmitting(true);
      const res = await companiesApi.submitSources(companyId, validUrls);

      let successMsg = res.message;
      if (res.verified_count > 0) {
        successMsg += ` ${res.verified_count} verified and processing.`;
      }
      if (res.pending_count > 0) {
        successMsg += ` ${res.pending_count} queued for review.`;
      }

      setMessage({ type: 'success', text: successMsg });
      setUrls(['']); // Reset form
      if (onSuccess) onSuccess();

    } catch (err) {
      let errorText = 'Failed to submit URLs.';
      if (err instanceof ApiError) {
        errorText = err.detail || err.message;
      }
      setMessage({ type: 'error', text: errorText });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="submission-form">
      <h3>Submit Evidence to Improve Score</h3>
      <p className="description">
        To improve {companyName}&apos;s score: check category breakdowns below, then submit up to 3 URLs (Engineering Blog, GitHub, etc.) with AI signals.
      </p>

      <form onSubmit={handleSubmit} className="form-content">
        <div className="fields-container">
          {urls.map((url, idx) => (
            <div key={idx} className="field-group">
              <input
                type="url"
                value={url}
                onChange={(e) => handleUrlChange(idx, e.target.value)}
                placeholder="https://example.com/blog"
                className="url-input"
                disabled={submitting}
              />
              {urls.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeField(idx)}
                  className="remove-btn"
                  aria-label="Remove URL"
                  disabled={submitting}
                >
                  ✕
                </button>
              )}
            </div>
          ))}
        </div>

        {urls.length < 3 && (
          <button
            type="button"
            onClick={addField}
            className="add-btn"
            disabled={submitting}
          >
            + Add another URL
          </button>
        )}

        {message && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <button
          type="submit"
          className="submit-btn"
          disabled={submitting}
        >
          {submitting ? 'Submitting...' : 'Submit Sources'}
        </button>
      </form>

      <style jsx>{`
        .submission-form {
          background: var(--color-surface);
          border: 1px solid var(--color-border);
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 40px;
        }
        h3 {
          font-size: 18px;
          margin: 0 0 8px 0;
          color: var(--color-text-primary);
        }
        .description {
          font-size: 14px;
          color: var(--color-text-secondary);
          margin: 0 0 20px 0;
          line-height: 1.5;
        }
        .form-content {
          display: flex;
          flex-direction: column;
          gap: 16px;
        }
        .field-group {
          display: flex;
          gap: 8px;
        }
        .url-input {
          flex: 1;
          padding: 10px 12px;
          border-radius: 8px;
          border: 1px solid var(--color-border);
          background: var(--color-background);
          color: var(--color-text-primary);
          font-size: 14px;
        }
        .url-input:focus {
          outline: none;
          border-color: var(--color-primary);
        }
        .remove-btn {
          background: none;
          border: none;
          color: var(--color-text-secondary);
          cursor: pointer;
          font-size: 14px;
          padding: 0 8px;
        }
        .remove-btn:hover {
          color: #ef4444;
        }
        .add-btn {
          align-self: flex-start;
          background: none;
          border: none;
          color: var(--color-primary);
          font-size: 13px;
          font-weight: 500;
          cursor: pointer;
          padding: 4px 0;
        }
        .add-btn:hover {
          text-decoration: underline;
        }
        .submit-btn {
          align-self: flex-start;
          background: var(--color-primary);
          color: var(--color-surface);
          border: none;
          padding: 10px 20px;
          border-radius: 8px;
          font-weight: 600;
          cursor: pointer;
          font-size: 14px;
          transition: opacity 0.2s;
        }
        .submit-btn:disabled {
          opacity: 0.7;
          cursor: not-allowed;
        }
        .message {
          padding: 10px;
          border-radius: 6px;
          font-size: 13px;
        }
        .message.success {
          background: rgba(16, 185, 129, 0.1);
          color: #10b981;
          border: 1px solid rgba(16, 185, 129, 0.2);
        }
        .message.error {
          background: rgba(239, 68, 68, 0.1);
          color: #ef4444;
          border: 1px solid rgba(239, 68, 68, 0.2);
        }
      `}</style>
    </div>
  );
}
