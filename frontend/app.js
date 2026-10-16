// MisterBet - Motore Frontend

// === 1. REGISTRA SERVICE WORKER (per PWA) ===
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
        .then(() => console.log('Service Worker registrato con successo'));
}

// === 2. CARICA E DISEGNA LE PARTITE ===
document.addEventListener('DOMContentLoaded', () => {
    
    // 🕒 Funzione per aggiornare il timestamp
    function updateTimestamp() {
        fetch('update_time.txt?t=' + new Date().getTime())
            .then(response => response.text())
            .then(text => {
                const updateTextElement = document.getElementById('last-update-text');
                if (updateTextElement && text.trim()) {
                    // Il file contiene qualcosa tipo "16/10/2026  9:15:23,45"
                    const rawDate = text.trim();
                    updateTextElement.innerHTML = `
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-mrGreen" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                        <span>Dati aggiornati il: ${rawDate}</span>
                    `;
                }
            })
            .catch(err => {
                console.warn('Impossibile leggere update_time.txt:', err);
            });
    }

    // 1. Scarica i dati dal file JSON
    fetch('app_data.json?t=' + new Date().getTime())
        .then(response => response.json())
        .then(matches => {
            const topContainer = document.getElementById('top-matches-container');
            const allContainer = document.getElementById('all-matches-container');

            topContainer.innerHTML = '';
            allContainer.innerHTML = '';

            if (matches.length === 0) {
                topContainer.innerHTML = '<div class="glass-card rounded-xl p-6 text-center text-gray-400">Nessuna opportunità di valore trovata oggi. Il modello consiglia di non giocare.</div>';
                return;
            }

            matches.forEach((match, index) => {
                const cardHTML = createCardHTML(match);
                if (index < 3) {
                    topContainer.innerHTML += cardHTML;
                } else {
                    allContainer.innerHTML += cardHTML;
                }
            });
        })
        .catch(error => {
            console.error('Errore nel caricamento dei dati:', error);
            document.getElementById('top-matches-container').innerHTML = '<div class="glass-card rounded-xl p-6 text-center text-red-400">Errore nel caricamento. Controlla la connessione.</div>';
        });
    
    // Aggiorna il timestamp
    updateTimestamp();
    
    // === 3. PULSANTE "TORNA SU" ===
    const scrollToTopBtn = document.getElementById('scrollToTopBtn');
    if (scrollToTopBtn) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 150) {
                scrollToTopBtn.classList.remove('opacity-0', 'invisible');
                scrollToTopBtn.classList.add('opacity-100', 'visible');
            } else {
                scrollToTopBtn.classList.add('opacity-0', 'invisible');
                scrollToTopBtn.classList.remove('opacity-100', 'visible');
            }
        });

        scrollToTopBtn.addEventListener('click', () => {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });
    }

    // === 4. MODALE GUIDA ===
    const helpBtn = document.getElementById('helpBtn');
    const helpModal = document.getElementById('helpModal');
    const helpModalContent = document.getElementById('helpModalContent');
    const closeHelpBtn = document.getElementById('closeHelpBtn');

    if (helpBtn && helpModal && closeHelpBtn) {
        helpBtn.addEventListener('click', () => {
            helpModal.classList.remove('hidden');
            setTimeout(() => {
                helpModal.classList.remove('opacity-0');
                helpModalContent.classList.remove('scale-95');
                helpModalContent.classList.add('scale-100');
            }, 10);
        });

        const closeModal = () => {
            helpModal.classList.add('opacity-0');
            helpModalContent.classList.remove('scale-100');
            helpModalContent.classList.add('scale-95');
            setTimeout(() => {
                helpModal.classList.add('hidden');
            }, 300);
        };

        closeHelpBtn.addEventListener('click', closeModal);
        helpModal.addEventListener('click', (e) => {
            if (e.target === helpModal) closeModal();
        });
    }
});

// === 5. FUNZIONE CHE CREA L'HTML DI UNA CARD ===
function createCardHTML(match) {
    let trafficColor = 'bg-mrGreen';
    let glowEffect = 'shadow-[0_0_15px_rgba(16,185,129,0.5)]';
    
    if (match.value_gap < 5) {
        trafficColor = 'bg-mrYellow';
        glowEffect = 'shadow-[0_0_15px_rgba(245,158,11,0.5)]';
    }

    const barWidth = Math.min(match.cluster.hit_rate, 100);

    let timeOnly = 'Oggi';
    try {
        if (match.time) {
            const timePart = match.time.split('T')[1];
            if (timePart) {
                timeOnly = timePart.substring(0, 5);
            }
        }
    } catch (e) {
        console.warn('Errore nel parsing della data:', match.time, e);
    }

    return `
    <div class="glass-card rounded-xl p-5 transition-transform hover:scale-[1.02] duration-300">
        <div class="flex justify-between items-center mb-3 text-xs text-gray-400 font-semibold uppercase tracking-wider">
            <span>${match.league || 'Campionato'}</span>
            <span class="bg-gray-800 px-2 py-1 rounded text-white">${timeOnly}</span>
        </div>

        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-bold text-white">${match.home_team || 'Squadra Casa'}</h3>
            <span class="text-gray-500 text-sm font-bold">VS</span>
            <h3 class="text-lg font-bold text-white">${match.away_team || 'Squadra Trasferta'}</h3>
        </div>

        <div class="flex items-center justify-between bg-gray-800/50 rounded-lg p-3 mb-4 border border-gray-700/50">
            <div class="flex items-center gap-3">
                <div class="w-4 h-4 rounded-full ${trafficColor} ${glowEffect}"></div>
                <div>
                    <p class="text-[10px] text-gray-400 uppercase tracking-wide">Segno Consigliato</p>
                    <p class="text-xl font-bold text-white">${match.best_bet || '?'} <span class="text-sm font-normal text-mrGreen">@ ${match.bookmaker_odd || '?'}</span></p>
                </div>
            </div>
            <div class="text-right">
                <p class="text-[10px] text-gray-400 uppercase tracking-wide">Gap Valore</p>
                <p class="text-lg font-bold ${match.value_gap >= 5 ? 'text-mrGreen' : 'text-mrYellow'}">+${match.value_gap || 0}%</p>
            </div>
        </div>

        <div class="grid grid-cols-2 gap-4 mb-4 text-sm">
            <div class="bg-gray-900/50 p-2 rounded text-center border border-gray-700/30">
                <p class="text-gray-500 text-[10px] uppercase mb-1">Nostro Modello</p>
                <p class="font-bold text-white text-lg">${match.model_prob || 0}%</p>
            </div>
            <div class="bg-gray-900/50 p-2 rounded text-center border border-gray-700/30">
                <p class="text-gray-500 text-[10px] uppercase mb-1">Bookmaker</p>
                <p class="font-bold text-gray-400 text-lg">${match.bookmaker_prob || 0}%</p>
            </div>
        </div>

        <div>
            <div class="flex justify-between text-xs text-gray-400 mb-1.5">
                <span>Affidabilità Storica <span class="text-gray-600">(${match.cluster?.total_matches || 0} partite simili)</span></span>
                <span class="font-bold text-white">${match.cluster?.hit_rate || 0}%</span>
            </div>
            <div class="w-full bg-gray-700 rounded-full h-2 overflow-hidden">
                <div class="${trafficColor} h-2 rounded-full transition-all duration-1000 ease-out" style="width: ${barWidth}%"></div>
            </div>
        </div>
    </div>
    `;
}