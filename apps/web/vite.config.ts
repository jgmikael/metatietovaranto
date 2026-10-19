import {defineConfig} from 'vite';
export default defineConfig(({mode})=>({
 base:mode==='pages'?'/metatietovaranto/':'/',
 publicDir:mode==='pages'?'../../.pages-data':false,
 build:{outDir:mode==='pages'?'dist-pages':'dist'},
}));
