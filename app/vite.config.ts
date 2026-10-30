import {defineConfig} from 'vite';
import {modelDownload} from './scripts/model-download.mjs';
export default defineConfig({worker:{format:'es'},plugins:[modelDownload(),{name:'study-config',apply:'serve',async transformIndexHtml(html){const ui=await fetch('http://127.0.0.1:8766/api/ui').then(r=>r.json());return html.replace('</head>',`<script id="app-config" type="application/json">${JSON.stringify(ui).replaceAll('<','\\u003c')}</script></head>`);}}],server:{proxy:{'/api':'http://127.0.0.1:8766'}},build:{outDir:'dist'}});
