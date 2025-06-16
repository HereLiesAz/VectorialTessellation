<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Volumetric Tessellation Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&family=Roboto+Mono:wght@400;500&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #f8f7f2;
            color: #4c4a44;
        }
        .mono {
            font-family: 'Roboto Mono', monospace;
        }
        .key-entry:hover {
            background-color: #e9e7e0;
            cursor: pointer;
        }
    </style>
</head>
<body class="p-4 sm:p-6 lg:p-8">
    <div class="max-w-7xl mx-auto">
        <header class="text-center mb-10">
            <h1 class="text-3xl sm:text-4xl lg:text-5xl font-bold text-slate-800">Volumetric Tessellation Engine</h1>
            <p class="mt-2 text-lg text-slate-500">This is not compression. This is cosmology.</p>
        </header>

        <main class="bg-white rounded-lg shadow-sm border border-slate-200 p-4 sm:p-6 lg:p-8">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-slate-700 mb-2">1. Input Universe (String)</h2>
                <p class="text-slate-500 mb-4">Provide a string to be mapped into its native three dimensions. The engine will search for the great cosmic filaments within.</p>
                <textarea id="input-text" class="w-full h-28 p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-teal-500 focus:outline-none mono bg-slate-50" placeholder="A string whose length has convenient 3D factors works best..."></textarea>
                <div class="mt-4 flex items-center space-x-4">
                    <button id="analyze-button" class="w-full sm:w-auto bg-slate-800 text-white font-bold py-2 px-8 rounded-md hover:bg-slate-900 transition-colors disabled:bg-slate-400">Map the Cosmos</button>
                    <button id="cancel-button" class="hidden w-full sm:w-auto bg-red-700 text-white font-bold py-2 px-8 rounded-md hover:bg-red-800">Halt the Simulation</button>
                </div>
            </div>

             <div id="progress-container" class="hidden my-6">
                <p id="progress-label" class="text-sm text-center text-slate-500 mb-2">Contemplating the void...</p>
                <div class="w-full bg-slate-200 rounded-full h-2.5">
                    <div id="progress-bar" class="bg-teal-600 h-2.5 rounded-full transition-all duration-300" style="width: 0%"></div>
                </div>
            </div>
            
            <div id="results-area" class="hidden">
                <hr class="my-8 border-slate-200">
                <h2 class="text-2xl font-bold text-slate-700 mb-6">2. Cosmological Blueprint</h2>
                <div class="grid grid-cols-1 xl:grid-cols-5 gap-8">
                    <div class="xl:col-span-3">
                        <h3 class="text-xl font-semibold text-slate-600 mb-3">Celestial Map</h3>
                         <p class="text-slate-500 mb-4">The original string, unrolled. Stars claimed by a filament are colored. Hover over a key entry to highlight its structure.</p>
                        <div class="bg-slate-50 p-2 rounded-md border border-slate-200">
                           <canvas id="visualization-canvas"></canvas>
                        </div>
                    </div>
                    <div class="xl:col-span-2">
                        <h3 class="text-xl font-semibold text-slate-600 mb-3">The Universal Constants</h3>
                        <div class="space-y-6">
                             <div class="grid grid-cols-3 gap-4 text-center border-b border-slate-200 pb-4">
                                <div>
                                    <p class="text-sm text-slate-500">Original</p>
                                    <p id="original-length" class="text-2xl font-bold mono text-slate-700">-</p>
                                </div>
                                <div>
                                    <p class="text-sm text-slate-500">Encoded</p>
                                    <p id="final-length" class="text-2xl font-bold mono text-slate-700">-</p>
                                </div>
                                <div>
                                    <p class="text-sm text-slate-500">Reduction</p>
                                    <p id="ratio" class="text-2xl font-bold mono text-teal-600">-</p>
                                </div>
                            </div>
                            <div>
                                <h4 class="font-semibold text-slate-600 mb-2">Cosmological Key (The Filaments)</h4>
                                <div id="key-output" class="text-sm mono space-y-1 max-h-48 overflow-y-auto pr-2 border border-slate-200 rounded-md p-3 bg-slate-50"></div>
                            </div>
                            <div>
                               <h4 class="font-semibold text-slate-600 mb-2">Aperiodic Remnant (The Dust)</h4>
                               <div id="remnant-output" class="p-3 bg-slate-50 border border-slate-200 rounded-md text-sm mono break-all max-h-48 overflow-y-auto"></div>
                            </div>
                            <div>
                                <h4 class="font-semibold text-slate-600 mb-2">Reconstitution</h4>
                                <button id="reconstitute-button" class="w-full bg-white border border-slate-300 text-slate-700 font-bold py-2 px-4 rounded-md hover:bg-slate-50 transition-colors">Re-run the Big Bang</button>
                                <div id="reconstitution-output" class="mt-2 p-2 bg-slate-100 border border-slate-200 rounded-md text-xs mono break-all text-slate-500 hidden"></div>
                           </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    <!-- The Web Worker's script -->
    <script id="analysis-worker" type="javascript/worker">
        const getVolumePermutations = (length) => {
            const permutations = new Set();
            for (let pages = 1; pages <= Math.floor(Math.cbrt(length)) + 1; pages++) {
                if (length % pages === 0) {
                    const area = length / pages;
                    for (let rows = 1; rows <= Math.floor(Math.sqrt(area)); rows++) {
                        if (area % rows === 0) {
                            const cols = Math.round(area / rows);
                            if (pages * rows * cols === length) {
                                permutations.add(JSON.stringify([pages, rows, cols].sort((a,b)=>a-b)));
                            }
                        }
                    }
                }
            }
            if (permutations.size === 0) permutations.add(JSON.stringify([1, 1, length]));
            return Array.from(permutations).map(JSON.parse).slice(0, 50); // Limit for performance
        };

        const findLineCandidatesInVolume = (volume, charToFind, dims) => {
            const candidates = [];
            const [pages, rows, cols] = dims;
            const charLocations = [];
            for(let p=0; p<pages; p++) {
                for(let r=0; r<rows; r++) {
                    for(let c=0; c<cols; c++) {
                        if (volume[p][r][c] === charToFind) {
                            charLocations.push([p, r, c]);
                        }
                    }
                }
            }

            if (charLocations.length < 2) return [];
            
            const checkedPairs = new Set();
            for (let i = 0; i < charLocations.length; i++) {
                for (let j = i + 1; j < charLocations.length; j++) {
                    const p1 = charLocations[i];
                    const p2 = charLocations[j];
                    const pairKey = `${p1.join(',')}-${p2.join(',')}`;
                    if(checkedPairs.has(pairKey)) continue;

                    const dp = p2[0] - p1[0], dr = p2[1] - p1[1], dc = p2[2] - p1[2];
                    const linePoints = charLocations.filter(p => {
                         const dpr = p[0] - p1[0], drr = p[1] - p1[1], dcr = p[2] - p1[2];
                         return dpr * dr === drr * dp && dpr * dc === dcr * dp;
                    });

                    if (linePoints.length > 2) {
                        const sortedPoints = linePoints.sort((a,b) => a[0]-b[0] || a[1]-b[1] || a[2]-b[2]);
                        const start = sortedPoints[0], end = sortedPoints[sortedPoints.length - 1];
                        const desc = `(${charToFind},${pages},${rows},${cols},${start.join(',')},${end.join(',')})`;
                        
                        checkedPairs.add(`${start.join(',')}-${end.join(',')}`);

                        const savings = linePoints.length - desc.length;
                        if (savings > 0) {
                            candidates.push({'savings': savings, 'points': sortedPoints, 'desc': desc});
                        }
                    }
                }
            }
            return candidates;
        };

        self.onmessage = (e) => {
            const { text } = e.data;
            try {
                self.postMessage({ type: 'progress', percentage: 5, label: 'Phase 1: Surveying potential universes...' });
                const allCandidates = [];
                const uniqueChars = [...new Set(text)];
                const permutations = getVolumePermutations(text.length);

                uniqueChars.forEach((char, charIndex) => {
                    permutations.forEach((dims, permIndex) => {
                        const progress = 10 + 70 * (charIndex / uniqueChars.length + (permIndex / uniqueChars.length) / permutations.length);
                        self.postMessage({ type: 'progress', percentage: progress, label: `Surveying for '${char}': Universe #${permIndex+1}/${permutations.length} (${dims.join('x')})` });

                        const [p, r, c] = dims;
                        const volume = new Array(p).fill(0).map(() => new Array(r).fill(0).map(() => new Array(c)));
                        for(let i=0; i<text.length; i++) {
                            const z = Math.floor(i / (r*c));
                            const y = Math.floor((i % (r*c)) / c);
                            const x = i % c;
                            volume[z][y][x] = text[i];
                        }
                        allCandidates.push(...findLineCandidatesInVolume(volume, char, dims));
                    });
                });
                
                self.postMessage({ type: 'progress', percentage: 80, label: `Phase 2: Evaluating ${allCandidates.length} potential filaments...` });
                const uniqueCandidates = Array.from(new Set(allCandidates.map(c => c.desc))).map(desc => allCandidates.find(c => c.desc === desc));
                uniqueCandidates.sort((a, b) => b.savings - a.savings);
                
                self.postMessage({ type: 'progress', percentage: 90, label: 'Phase 2: Selecting optimal cosmic key...' });
                const cosmologicalKey = [];
                const claimedPositions = new Array(text.length).fill(false);
                
                uniqueCandidates.forEach(cand => {
                    const parts = cand.desc.slice(1, -1).split(',');
                    const dims = parts.slice(1, 4).map(Number);
                    const [p, r, c] = dims;
                    const indices_to_claim = cand.points.map(([z, y, x]) => z*r*c + y*c + x);
                    const canBeClaimed = indices_to_claim.every(idx => !claimedPositions[idx]);

                    if (canBeClaimed) {
                        cosmologicalKey.push(cand.desc);
                        indices_to_claim.forEach(idx => { claimedPositions[idx] = true; });
                    }
                });
                
                self.postMessage({ type: 'progress', percentage: 95, label: 'Phase 3: Generating final blueprint...' });
                const remnantStream = [...text].filter((_, i) => !claimedPositions[i]).join('');
                const keyString = cosmologicalKey.join('§');
                const compiledBlueprint = `${text.length}¬${keyString}‡${remnantStream}`;

                self.postMessage({ type: 'result', payload: { compiledBlueprint, key: cosmologicalKey, remnant: remnantStream, originalText: text } });

            } catch (error) {
                 self.postMessage({ type: 'error', message: error.message });
            }
        };
    </script>

    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const inputEl = document.getElementById('input-text');
            const analyzeBtn = document.getElementById('analyze-button');
            const cancelBtn = document.getElementById('cancel-button');
            const reconstituteBtn = document.getElementById('reconstitute-button');
            const canvas = document.getElementById('visualization-canvas');
            const ctx = canvas.getContext('2d');

            const progressContainer = document.getElementById('progress-container');
            const progressBar = document.getElementById('progress-bar');
            const progressLabel = document.getElementById('progress-label');

            const resultsArea = document.getElementById('results-area');
            const originalLengthEl = document.getElementById('original-length');
            const finalLengthEl = document.getElementById('final-length');
            const ratioEl = document.getElementById('ratio');
            const keyEl = document.getElementById('key-output');
            const remnantEl = document.getElementById('remnant-output');
            const reconstitutionEl = document.getElementById('reconstitution-output');

            let analysisResult = null;
            let hoveredDesc = null;
            let analysisWorker = null;
            
            const PALETTE = ['#0d9488', '#d97706', '#be185d', '#65a30d', '#57534e', '#8b5cf6'];

            const updateProgress = (percentage, label) => {
                progressBar.style.width = `${percentage}%`;
                if (label) progressLabel.textContent = label;
            };

            const analyze = () => {
                const text = inputEl.value;
                if (!text) return;
                
                analyzeBtn.disabled = true;
                cancelBtn.classList.remove('hidden');
                progressContainer.classList.remove('hidden');
                resultsArea.classList.add('hidden');
                updateProgress(0, 'Initializing worker...');
                
                const workerScriptContent = document.getElementById('analysis-worker').textContent;
                const workerBlob = new Blob([workerScriptContent], { type: 'application/javascript' });
                analysisWorker = new Worker(URL.createObjectURL(workerBlob));
                
                analysisWorker.onmessage = (e) => {
                    const { type, payload, percentage, label, message } = e.data;
                    if (type === 'progress') {
                        updateProgress(percentage, label);
                    } else if (type === 'result') {
                        analysisResult = payload;
                        updateProgress(100, 'Analysis complete.');
                        updateUI();
                        drawVisualization();
                        resultsArea.classList.remove('hidden');
                        terminateWorker();
                    } else if (type === 'error') {
                        console.error('Worker error:', message);
                        updateProgress(0, `An error occurred: ${message}`);
                        terminateWorker();
                    }
                };
                analysisWorker.onerror = (e) => {
                    console.error('Worker error:', e);
                    updateProgress(0, 'An error occurred in the analysis worker.');
                    terminateWorker();
                };
                analysisWorker.postMessage({ text });
            };
            
            const terminateWorker = () => {
                if (analysisWorker) {
                    analysisWorker.terminate();
                    analysisWorker = null;
                }
                 setTimeout(() => {
                    progressContainer.classList.add('hidden');
                    analyzeBtn.disabled = false;
                    cancelBtn.classList.add('hidden');
                }, 1000);
            };

            const drawVisualization = () => {
                if (!analysisResult) return;
                const { originalText, key } = analysisResult;
                const dpr = window.devicePixelRatio || 1;
                const parentWidth = canvas.parentElement.clientWidth;
                canvas.width = parentWidth * dpr;
                const charSize = Math.min(24, parentWidth / 40);
                const charsPerRow = Math.floor(parentWidth / charSize);
                const numRows = Math.ceil(originalText.length / charsPerRow);
                canvas.height = (numRows * charSize * 1.5) * dpr;
                ctx.scale(dpr, dpr);
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                ctx.font = `500 ${charSize * 0.8}px 'Roboto Mono'`;
                
                const claimed = new Array(originalText.length).fill(null);
                key.forEach((desc, keyIndex) => {
                    const parts = desc.slice(1,-1).split(',').map((p,i) => i===0 ? p : Number(p));
                    const [char, p, r, c, z1, y1, x1, z2, y2, x2] = parts;
                    const dp=z2-z1, dr=y2-y1, dc=x2-x1;
                    const steps = Math.max(Math.abs(dp), Math.abs(dr), Math.abs(dc));
                    if (steps === 0) return;
                    for (let i=0; i<=steps; i++) {
                        const zp=z1+dp*i/steps, rp=y1+dr*i/steps, cp=x1+dc*i/steps;
                        const idx = Math.round(zp)*r*c + Math.round(rp)*c + Math.round(cp);
                        if(idx < originalText.length) claimed[idx] = {desc, color: PALETTE[keyIndex % PALETTE.length]};
                    }
                });

                for(let i = 0; i < originalText.length; i++) {
                    const row = Math.floor(i / charsPerRow), col = i % charsPerRow;
                    const x = col * charSize + (charSize / 2), y = row * charSize * 1.5 + (charSize / 2);
                    const claim = claimed[i];
                    ctx.textAlign = 'center';
                    ctx.textBaseline = 'middle';
                    ctx.fillStyle = claim ? claim.color : '#9ca3af';

                    if (hoveredDesc && claim && claim.desc === hoveredDesc) {
                        ctx.fillStyle = '#000';
                        ctx.fillRect(x - charSize/2, y - charSize/2, charSize, charSize);
                        ctx.fillStyle = '#fff';
                    }
                    
                    ctx.fillText(originalText[i], x, y);
                }
            };
            
            const updateUI = () => {
                const { compiledBlueprint, key, remnant, originalText } = analysisResult;
                document.getElementById('original-length').textContent = originalText.length;
                document.getElementById('final-length').textContent = compiledBlueprint.length;
                const ratio = originalText.length > 0 ? (100 * (1 - compiledBlueprint.length / originalText.length)).toFixed(1) : 0;
                document.getElementById('ratio').textContent = `${ratio > 0 ? ratio : 0}%`;

                keyEl.innerHTML = key.length > 0 ? '' : '<p class="text-slate-500">None</p>';
                key.forEach((desc, index) => {
                    const entry = document.createElement('div');
                    entry.className = 'key-entry p-1 rounded transition-colors';
                    const color = PALETTE[index % PALETTE.length];
                    entry.innerHTML = `<span class="inline-block w-3 h-3 rounded-full mr-2" style="background-color: ${color};"></span><span>${desc}</span>`;
                    entry.onmouseenter = () => { hoveredDesc = desc; drawVisualization(); };
                    entry.onmouseleave = () => { hoveredDesc = null; drawVisualization(); };
                    keyEl.appendChild(entry);
                });

                remnantEl.textContent = remnant || 'N/A';
                reconstitutionEl.classList.add('hidden');
            };

            const runReconstruction = () => {
                if(!analysisResult || !analysisResult.compiledBlueprint) return;
                
                const { compiledBlueprint } = analysisResult;
                try {
                    const [lengthPart, mainPart] = compiledBlueprint.split('¬');
                    const originalLength = parseInt(lengthPart, 10);
                    const [keyString, remnantStream] = mainPart.split('‡');
                    const key = keyString ? keyString.split('§') : [];

                    const canvas = new Array(originalLength).fill(null);
                    
                    key.forEach(desc => {
                        const parts = desc.slice(1, -1).split(',').map((p, i) => i === 0 ? p : Number(p));
                        const [char, p, r, c, z1, y1, x1, z2, y2, x2] = parts;
                        const dp = z2 - z1, dr = y2 - y1, dc = x2 - x1;
                        const steps = Math.max(Math.abs(dp), Math.abs(dr), Math.abs(dc));
                        if(steps === 0) return;
                        for (let i = 0; i <= steps; i++) {
                            const zp = z1 + dp * i / steps, rp = y1 + dr * i / steps, cp = x1 + dc * i / steps;
                            const idx = Math.round(zp) * r * c + Math.round(rp) * c + Math.round(cp);
                            if (idx < originalLength) canvas[idx] = char;
                        }
                    });

                    let remnantIndex = 0;
                    for (let i = 0; i < originalLength; i++) {
                        if (canvas[i] === null) {
                            if (remnantIndex < remnantStream.length) {
                                canvas[i] = remnantStream[remnantIndex++];
                            }
                        }
                    }

                    const reconstitutedText = canvas.join('').replace(/\u0000/g, '');
                    reconstitutionEl.textContent = `Verification: ${reconstitutedText === analysisResult.originalText ? 'Perfect Match!' : 'Mismatch Detected.'}\n\n${reconstitutedText}`;
                    reconstitutionEl.classList.remove('hidden');

                } catch (e) {
                     reconstitutionEl.textContent = `Error during reconstruction: ${e.message}`;
                     reconstitutionEl.classList.remove('hidden');
                }
            }
            
            analyzeBtn.addEventListener('click', analyze);
            cancelBtn.addEventListener('click', () => { if (analysisWorker) terminateWorker(); });
            reconstituteBtn.addEventListener('click', runReconstruction);
            window.addEventListener('resize', () => { if(analysisResult) drawVisualization(); });
            
            inputEl.value = "azzzazzzzzazzzzzzzazzzzzzzzzazzzzzzzzzzzazzzzzzzzzzzzzazzz".padEnd(60, 'z');
        });
    </script>
</body>
</html>
