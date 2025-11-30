import { Play, Square, RefreshCcw, Zap, Trophy, Timer } from 'lucide-react';
import { useState, useEffect, useRef } from 'react';
import BiofeedbackChart from '../components/BiofeedbackChart';
import castleGif from '../assets/castle.gif';

// Konfiguracja kolorów gry
const COLORS = [
  { id: 'red', value: 'bg-red-500', label: 'Czerwony' },
  { id: 'blue', value: 'bg-blue-500', label: 'Niebieski' },
  { id: 'green', value: 'bg-green-500', label: 'Zielony' },
  { id: 'yellow', value: 'bg-yellow-400', label: 'Żółty' },
];

type GameState = 'idle' | 'playing' | 'finished';

export default function ConcentrationDrill() {
  const [gameState, setGameState] = useState<GameState>('idle');
  const [targetColor, setTargetColor] = useState(COLORS[0]);
  const [currentColor, setCurrentColor] = useState(COLORS[0]);
  const [score, setScore] = useState(0);
  const [reactionTime, setReactionTime] = useState<number | null>(null);
  const [feedback, setFeedback] = useState<string>('');
  
  // Ref do mierzenia czasu reakcji
  const startTimeRef = useRef<number>(0);

  // --- SILNIK GRY ---
  // Ten useEffect to "serce" pętli. Uruchamia się za każdym razem, gdy zmieni się kolor lub stan gry.
  useEffect(() => {
    let timeoutId: ReturnType<typeof setTimeout>;

    if (gameState === 'playing') {
      const randomDelay = Math.random() * 2000 + 500;
      
      timeoutId = setTimeout(() => {
        // Zmieniamy kolor na inny niż obecny
        setCurrentColor((prev) => {
          let nextColor;
          do {
            nextColor = COLORS[Math.floor(Math.random() * COLORS.length)];
          } while (nextColor.id === prev.id);
          
          // Zapisujemy moment, w którym kolor się zmienił (do pomiaru refleksu)
          startTimeRef.current = Date.now();
          return nextColor;
        });
      }, randomDelay);
    }

    // Czyszczenie przy odmontowaniu lub zmianie stanu (np. STOP)
    return () => clearTimeout(timeoutId);
  }, [gameState, currentColor]); // <--- Zależność od currentColor napędza pętlę

  const startGame = () => {
    setScore(0);
    setReactionTime(null);
    setFeedback('');
    pickNewTarget();
    setGameState('playing');
    // Nie musimy nic więcej robić - zmiana gameState na 'playing' uruchomi useEffect powyżej
  };

  const stopGame = () => {
    setGameState('idle');
    setFeedback('');
  };

  const pickNewTarget = () => {
    const random = COLORS[Math.floor(Math.random() * COLORS.length)];
    setTargetColor(random);
  };

  const handleReaction = () => {
    if (gameState !== 'playing') return;

    const now = Date.now();
    // Obliczamy czas od ostatniej zmiany koloru
    const timeDiff = now - startTimeRef.current;

    if (currentColor.id === targetColor.id) {
      // TRAFIENIE
      setScore((prev) => prev + 1);
      setReactionTime(timeDiff);
      setFeedback('Amazing!');
      pickNewTarget(); // Losujemy nowy cel po trafieniu
    } else {
      // PUDŁO
      setFeedback('Missed. Wait for the target color!');
      setReactionTime(null);
    }
  };

  // Obsługa spacji
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        e.preventDefault(); // Blokuje scrollowanie strony
        if (gameState === 'idle') startGame();
        else if (gameState === 'playing') handleReaction();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [gameState, currentColor, targetColor]);


  return (
  <div className="relative w-full max-w-xl lg:max-w-2xl mx-auto px-4">
    {/* Background GIF */}
    <div className="fixed inset-0 z-0 pointer-events-none">
      <img
        src={castleGif}
        alt="Castle background"
        className="w-full h-full object-cover opacity-60"
      />
    </div>
    
    {/* Content wrapper */}
    <div className="relative z-10">
      <div className='font-mono'>
        <BiofeedbackChart />
        <div className="flex flex-col items-center justify-center min-h-[520px] max-w-3xl mx-auto bg-white/5 backdrop-blur-md p-5 rounded-3xl select-none border-2 border-white/20 mt-8">
          {/* Nagłówek */}
          <div className="text-center mb-8">
            <h2 className="text-3xl font-bold text-white mb-2">Reflex Trainer</h2>
            <p className="text-white/70">Press space when target colour appears!</p>
          </div>

          {/* Panel Celu */}
          <div className={`transition-opacity duration-0 mb-6 ${gameState === 'playing' ? 'opacity-100' : 'opacity-0'}`}>
            <div className="flex items-center gap-3 bg-white/10 backdrop-blur-sm px-6 py-2 rounded-full shadow-sm border border-white/30">
              <span className="text-white/90 font-medium uppercase text-xs tracking-wide">Twój cel:</span>
              <div className={`w-4 h-4 rounded-full ${targetColor.value}`} />
              <span className="font-bold text-white">{targetColor.label}</span>
            </div>
          </div>

          {/* Główny przycisk gry */}
          <button
            onClick={gameState === 'playing' ? handleReaction : undefined}
            className={`
              relative flex items-center justify-center w-64 h-64 mb-8
              rounded-full transition-all duration-0 outline-none
              ${gameState === 'playing' ? 'cursor-pointer active:scale-95' : 'cursor-default'}
            `}
          >
            {/* Tło "duch" */}
            <div className={`absolute inset-0 rounded-full opacity-20 transition-colors duration-0 ${gameState === 'playing' ? currentColor.value : 'bg-white/40'}`} />
            
            {/* Główne koło */}
            <div
              className={`
                flex flex-col items-center justify-center
                w-48 h-48 rounded-full shadow-xl
                transition-colors duration-0 ease-out
                ${gameState === 'playing' ? currentColor.value : 'bg-white/30'}
                ${gameState === 'playing' ? 'shadow-white/20' : ''}
              `}
            >
               {gameState === 'idle' && <Zap size={48} className="text-white/70" />}
               {gameState === 'playing' && (
                 <span className="text-white/90 font-bold text-sm uppercase tracking-widest mt-2">
                    Press
                 </span>
               )}
            </div>

            {/* Feedback po kliknięciu */}
            {feedback && (
               <div className="absolute inset-0 flex items-center justify-center pointer-events-none animate-bounce-short">
                  <span className="bg-black/90 backdrop-blur px-4 py-1 rounded-lg font-bold text-white shadow-lg">
                    {feedback} {reactionTime ? `${reactionTime}ms` : ''}
                  </span>
               </div>
            )}
          </button>

          {/* Statystyki */}
          <div className="flex gap-8 mb-8 text-white">
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 text-sm font-medium text-white/90 mb-1">
                <Trophy size={16} /> Score
              </div>
              <span className="text-2xl font-bold">{score}</span>
            </div>
            <div className="flex flex-col items-center">
              <div className="flex items-center gap-2 text-sm font-medium text-white/90 mb-1">
                <Timer size={16} /> Last time
              </div>
              <span className="text-2xl font-bold">
                {reactionTime ? `${reactionTime}` : '-'} <span className="text-sm font-normal text-white/90">ms</span>
              </span>
            </div>
          </div>

          {/* Kontrolery */}
          <button
            onClick={gameState === 'playing' ? stopGame : startGame}
            className={`
              flex items-center gap-2 px-8 py-3 rounded-lg font-bold text-base transition-all duration-300 text-white
              ${gameState === 'playing'
                ? 'bg-red-500/80 hover:bg-red-600 border-2 border-red-500/50 hover:border-red-500' 
                : 'bg-white/10 border-2 border-white/30 hover:bg-white/20 hover:border-white/40'
              } shadow-lg hover:scale-105 active:scale-95
            `}
          >
            {gameState === 'playing' ? (
              <>
                <Square size={20} fill="currentColor" /> Stop
              </>
            ) : (
              <>
                {gameState === 'finished' ? <RefreshCcw size={20} /> : <Play size={20} fill="currentColor" />} 
                {gameState === 'finished' ? 'Play again' : 'Begin'}
              </>
            )}
          </button>
          
          <p className="mt-4 text-xs text-white/90">Press SPACE</p>
        </div>
      </div>
    </div>
  </div>
  );
}