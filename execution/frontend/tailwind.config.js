/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // System Minimal theme - mapped from design-system/signalscore/theme.css
                'surface': 'var(--color-surface)',
                'surface-alt': 'var(--color-surface-alt)',
                'primary': 'var(--color-primary)',
                'primary-hover': 'var(--color-primary-hover)',
                'text-primary': 'var(--color-text-primary)',
                'text-secondary': 'var(--color-text-secondary)',
                'border': 'var(--color-border)',
                'success': 'var(--color-success)',
                'warning': 'var(--color-warning)',
                'error': 'var(--color-error)',
            },
            fontFamily: {
                sans: ['var(--font-sans)', 'system-ui', 'sans-serif'],
                mono: ['var(--font-mono)', 'monospace'],
            },
            borderRadius: {
                // System Minimal: No rounding
                'none': '0',
            },
        },
    },
    plugins: [],
};
