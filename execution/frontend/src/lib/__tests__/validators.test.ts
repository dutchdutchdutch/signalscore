import { describe, it, expect } from 'vitest';
import { validateInputUrl } from '../validators';

describe('validateInputUrl', () => {
    // AC: "target (not a valid url)"
    it('should reject plain words without TLD', () => {
        const result = validateInputUrl('target');
        expect(result.isValid).toBe(false);
        expect(result.error).toContain('valid URL');
    });

    // AC: "target.com" - User report implies this should be valid (or at least handled)
    it('should accept domain.tld without www', () => {
        const result = validateInputUrl('target.com');
        expect(result.isValid).toBe(true);
        expect(result.normalizedUrl).toBe('https://target.com');
    });

    // AC: "target.com/jobs (valid url)" - Path implies specific intent?
    it('should accept domain with path even without protocol', () => {
        const result = validateInputUrl('target.com/jobs');
        expect(result.isValid).toBe(true);
        expect(result.normalizedUrl).toBe('https://target.com/jobs');
    });

    // AC: "www.target.com (valid url)"
    it('should accept www.target.com', () => {
        const result = validateInputUrl('www.target.com');
        expect(result.isValid).toBe(true);
        expect(result.normalizedUrl).toBe('https://www.target.com');
    });

    // AC: "http://target.com (valid url)"
    it('should accept http://target.com and upgrade to https', () => {
        const result = validateInputUrl('http://target.com');
        expect(result.isValid).toBe(true);
        // Note: logic might auto-upgrade or keep http. "assume user meant https" implies upgrade.
        expect(result.normalizedUrl).toBe('https://target.com');
    });

    // AC: "https://target.com (valid url)"
    it('should accept https://target.com', () => {
        const result = validateInputUrl('https://target.com');
        expect(result.isValid).toBe(true);
        expect(result.normalizedUrl).toBe('https://target.com');
    });

    // AC: "careers.target.com"
    it('should handle subdomains by normalizing to main domain with warning', () => {
        const result = validateInputUrl('careers.target.com');
        expect(result.isValid).toBe(true);
        expect(result.normalizedUrl).toBe('https://target.com');
        expect(result.warning).toContain('main domain');
    });

    // Edge case: "https://careers.target.com"
    it('should handle full url subdomains by normalizing', () => {
        const result = validateInputUrl('https://careers.target.com');
        expect(result.isValid).toBe(true);
        // Should strip subdomain 'careers' but keep 'target.com'
        // Requires robust logic to distinguish TLD vs subdomain. 
        // For MVP/AC: just check if it has 3+ parts? "subdomains are not individually evaluated"
        expect(result.normalizedUrl).toBe('https://target.com');
        expect(result.warning).toBeTruthy();
    });
});
