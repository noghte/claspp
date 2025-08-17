import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
	plugins: [sveltekit()],
	// Remove base path here as it's already defined in svelte.config.js
	// base: '/claspp/',
    resolve: {
        alias: {
            $lib: path.resolve('./src/lib'),
            // $routes: '/src/routes',
            // $components: '/src/components',
            // $stores: '/src/stores',
            // $utils: '/src/utils',
            // $assets: '/src/assets',
            // $types: '/src/types',
            // $server: '/src/server',
            // $db: '/src/db',
            // "$src": path.resolve('./src')
        }},
	server: {
        hmr: {
            clientPort: 8085
        },
        fs: {
            allow: ['fonts']
        }
    }
});
