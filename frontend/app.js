// MisterBet - Motore Frontend
// Questo script legge i dati, calcola i colori dei semafori e disegna le card.

   // Registra il Service Worker per abilitare l'installazione PWA
   if ('serviceWorker' in navigator) {
       navigator.serviceWorker.register('/sw.js')
           .then(() => console.log('Service Worker registrato con successo'));
   }
   
document.addEventListener('DOMContentLoaded', () => {
    // 1. Scarica i dati dal file JSON
    fetch('app_data.json')
        .then(response => response.json())
        .then(matches => {
            const topContainer = document.getElementById('top-matches-container');
            const allContainer = document.getElementById('all-matches-container');

            // Pulisce i contenitori (rimuove la scritta "Caricamento...")
            topContainer.innerHTML = '';
            allContainer.innerHTML = '';

            // Se non ci sono partite con valore
            if (matches.length === 0) {
                topContainer.innerHTML = '<div class="glass-card rounded-xl p-6 text-center text-gray-400">Nessuna opportunità di valore trovata oggi. Il modello consiglia di non giocare.</div>';
                return;
            }

            // 2. Disegna le card
            matches.forEach((match, index) => {
                const cardHTML = createCardHTML(match);
                
                // Le prime 3 vanno nelle "Top Occasioni", le altre in "Altre Partite"
                if (index < 3) {
                    topContainer.innerHTML += cardHTML;
                } else {
                    allContainer.innerHTML += cardHTML;
                }
            });
        })
        .catch(error => {
            console.error('Errore nel caricamento dei dati:', error);
            document.getElementById('top-matches-container').innerHTML = '<div class="glass-card rounded-xl p-6 text-center text-red-400">Errore nel caricamento. (Vedi istruzione Server Locale)</div>';
        });
});

// Funzione che crea l'HTML di una singola card
function createCardHTML(match) {
    // Logica del Semaforo: Verde se il gap è alto (>= 5%), Giallo se moderato
    let trafficColor = 'bg-mrGreen';
    let trafficText = 'Valore Forte';
    let glowEffect = 'shadow-[0_0_15px_rgba(16,185,129,0.5)]';
    
    if (match.value_gap < 5) {
        trafficColor = 'bg-mrYellow';
        trafficText = 'Valore Moderato';
        glowEffect = 'shadow-[0_0_15px_rgba(245,158,11,0.5)]';
    }

    // Larghezza della barra di affidabilità
    const barWidth = Math.min(match.cluster.hit_rate, 100);

    // Estraiamo solo l'ora dalla data (con controllo errori)
    let timeOnly = 'Oggi';
    try {
        if (match.time) {
            // Formato atteso: "2026-10-15T20:45:00Z" o simile
            const timePart = match.time.split('T')[1];
            if (timePart) {
                timeOnly = timePart.substring(0, 5); // Prende solo "20:45"
            }
        }
    } catch (e) {
        console.warn('Errore nel parsing della data:', match.time, e);
    }

    return `
    <div class="glass-card rounded-xl p-5 transition-transform hover:scale-[1.02] duration-300">
        <!-- Header: Lega e Ora -->
        <div class="flex justify-between items-center mb-3 text-xs text-gray-400 font-semibold uppercase tracking-wider">
            <span>${match.league || 'Campionato'}</span>
            <span class="bg-gray-800 px-2 py-1 rounded text-white">${timeOnly}</span>
        </div>

        <!-- Squadre -->
        <div class="flex justify-between items-center mb-4">
            <h3 class="text-lg font-bold text-white">${match.home_team || 'Squadra Casa'}</h3>
            <span class="text-gray-500 text-sm font-bold">VS</span>
            <h3 class="text-lg font-bold text-white">${match.away_team || 'Squadra Trasferta'}</h3>
        </div>

        <!-- Il Semaforo e la Giocata -->
        <div class="flex items-center justify-between bg-gray-800/50 rounded-lg p-3 mb-4 border border-gray-700/50">
            <div class="flex items-center gap-3">
                <!-- Pallino Semaforo -->
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

        <!-- Dettagli Esperto (Probabilità a confronto) -->
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

        <!-- Barra Affidabilità Cluster (Comparazioni Affini) -->
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
    // === PULSANTE "TORNA SU" ===
const scrollToTopBtn = document.getElementById('scrollToTopBtn');

// Mostra/nasconde il pulsante in base allo scroll
window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        // L'utente ha scrollato più di 300px: mostra il pulsante
        scrollToTopBtn.classList.remove('opacity-0', 'invisible');
        scrollToTopBtn.classList.add('opacity-100', 'visible');
    } else {
        // L'utente è in cima: nascondi il pulsante
        scrollToTopBtn.classList.add('opacity-0', 'invisible');
        scrollToTopBtn.classList.remove('opacity-100', 'visible');
    }
});

// Quando clicca, torna su con animazione fluida
scrollToTopBtn.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});
    `;
}