import tseslint from 'typescript-eslint';
import svelte from 'eslint-plugin-svelte';

export default [
	{
		ignores: [
			'.svelte-kit/**',
			'build/**',
			'dist/**',
			'node_modules/**',
			'static/service-worker.js'
		]
	},
	...tseslint.configs.recommended,
	...svelte.configs['flat/recommended'],
	{
		files: ['**/*.svelte'],
		languageOptions: { parserOptions: { parser: tseslint.parser } }
	},
	{
		rules: {
			'@typescript-eslint/no-explicit-any': 'warn',
			'@typescript-eslint/no-unused-vars': [
				'error',
				{ argsIgnorePattern: '^_', varsIgnorePattern: '^_' }
			],
			'svelte/no-at-html-tags': 'warn'
		}
	}
];
