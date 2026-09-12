/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				background: 'rgb(var(--background) / <alpha-value>)',
				foreground: 'rgb(var(--foreground) / <alpha-value>)',
				border: 'rgb(var(--border) / <alpha-value>)',
				input: 'rgb(var(--border) / <alpha-value>)',
				ring: 'rgb(var(--ring) / <alpha-value>)',
				surface: 'rgb(var(--surface) / <alpha-value>)',
				'title-color': 'rgb(var(--title-color) / <alpha-value>)',
				card: {
					DEFAULT: 'rgb(var(--card) / <alpha-value>)',
					foreground: 'rgb(var(--card-foreground) / <alpha-value>)'
				},
				popover: {
					DEFAULT: 'rgb(var(--card) / <alpha-value>)',
					foreground: 'rgb(var(--card-foreground) / <alpha-value>)'
				},
				accent: {
					DEFAULT: 'rgb(var(--accent) / <alpha-value>)',
					foreground: 'rgb(var(--accent-foreground) / <alpha-value>)'
				},
				muted: {
					DEFAULT: 'rgb(var(--muted) / <alpha-value>)',
					foreground: 'rgb(var(--muted-foreground) / <alpha-value>)'
				},
				primary: {
					DEFAULT: 'rgb(var(--primary) / <alpha-value>)',
					foreground: 'rgb(var(--primary-foreground) / <alpha-value>)',
					hover: 'rgb(var(--primary-hover) / <alpha-value>)'
				},
				secondary: {
					DEFAULT: 'rgb(var(--muted) / <alpha-value>)',
					foreground: 'rgb(var(--foreground) / <alpha-value>)'
				},
				destructive: {
					DEFAULT: 'rgb(var(--destructive) / <alpha-value>)',
					foreground: 'rgb(var(--destructive-foreground) / <alpha-value>)',
					hover: 'rgb(var(--destructive-hover) / <alpha-value>)'
				},
				success: {
					DEFAULT: 'rgb(var(--success) / <alpha-value>)',
					foreground: 'rgb(var(--primary-foreground) / <alpha-value>)'
				},
				warning: {
					DEFAULT: 'rgb(var(--warning) / <alpha-value>)',
					foreground: 'rgb(var(--primary-foreground) / <alpha-value>)'
				},
				rating: 'rgb(var(--rating) / <alpha-value>)'
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
				serif: ['"Playfair Display"', 'Georgia', 'serif'],
				mono: ['"JetBrains Mono"', 'monospace']
			},
			borderRadius: {
				sm: '2px',
				md: '4px',
				lg: '6px',
				xl: '8px'
			},
			boxShadow: {
				sm: '0 1px 2px rgba(61, 64, 52, 0.06), 0 1px 3px rgba(61, 64, 52, 0.04)',
				DEFAULT: '0 1px 3px rgba(61, 64, 52, 0.08)',
				md: '0 4px 12px rgba(61, 64, 52, 0.08)',
				lg: '0 8px 24px rgba(61, 64, 52, 0.10)'
			}
		}
	},
	plugins: []
};
