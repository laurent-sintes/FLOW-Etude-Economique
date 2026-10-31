import {defineConfig} from 'vite';
import {readFile} from 'node:fs/promises';
import {fileURLToPath} from 'node:url';
import {modelDownload} from './scripts/model-download.mjs';
const staticFiles='http://127.0.0.1:8766';
export default defineConfig({
 worker:{format:'es'},
 plugins:[modelDownload(),{
  name:'study-config',apply:'serve',
  async transformIndexHtml(html){
   const compiled=await readFile(fileURLToPath(new URL('./dist/index.html',import.meta.url)),'utf8');
   const config=compiled.match(/<script id="app-config" type="application\/json">[\s\S]*?<\/script>/)?.[0];
   if(!config)throw new Error('Prepare the static application with tools/start_study_app.ps1 first');
   return html.replace('</head>',config+'</head>');
  },
 }],
 server:{proxy:Object.fromEntries(['/site-manifest.json','/data/','/documents/','/exports/'].map(path=>[path,staticFiles]))},
 build:{outDir:'dist'},
});
