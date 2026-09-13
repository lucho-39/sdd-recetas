import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vitest/config';

export default defineConfig({
	plugins: [sveltekit()],
	test: {
		include: ['src/**/*.{test,spec}.{js,ts}'],
	},
	server: {
		port: 3000,
		host: true,
		proxy: {
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true
			},
			'/uploads': {
				target: 'http://backend:8000',
				changeOrigin: true
			},
			'/socket.io': {
				target: 'http://backend:8000',
				changeOrigin: true,
				ws: true
			}
		}
	},
	preview: {
		port: 3000,
		host: true,
		proxy: {
			'/api': {
				target: 'http://backend:8000',
				changeOrigin: true
			},
			'/uploads': {
				target: 'http://backend:8000',
				changeOrigin: true
			},
			'/socket.io': {
				target: 'http://backend:8000',
				changeOrigin: true,
				ws: true
			}
		}
	},
});