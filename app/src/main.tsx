import React from 'react';
import {createRoot} from 'react-dom/client';
import App from './App';
import {AppErrorBoundary} from './AppErrorBoundary';
import type {Data} from './context';
import './styles.css';
import './brand.css';
import './readingLayout.css';
import './businessMap.css';
import './businessAtlas.css';
import './sponsorJourney.css';
import './readingIdentity.css';
import './dossier.css';
let initial:Data={};
try{initial=JSON.parse(document.getElementById('app-config')?.textContent||'{}');}catch{/* The error boundary handles a malformed bootstrap config. */}
createRoot(document.getElementById('root')!).render(<React.StrictMode><AppErrorBoundary initial={initial}><App initial={initial}/></AppErrorBoundary></React.StrictMode>);
