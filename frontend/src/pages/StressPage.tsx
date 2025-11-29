import { RefreshCcw, Square, Play } from 'lucide-react';
import { useState, useEffect } from 'react';
import BiofeedbackChart from '../components/BiofeedbackChart';

// Definicja faz cyklu
type Phase = 'idle' | 'inhale' | 'hold-in' | 'exhale' | 'hold-out';

const PHASE_CONFIG = {
  idle: {
    text: "Gotowy?",
    instruction: "Naciśnij start, aby rozpocząć",
    scale: "scale-100", // Rozmiar początkowy
    duration: "duration-300", // Szybka reakcja przy resecie
  },
  inhale: {
    text:"",
    instruction: "Nabieraj powietrze nosem...",
    scale: "scale-150", // Kółko rośnie (1.5x)
    duration: "duration-[4000ms]", // Zmiana w 4 sekundy
  },
  'hold-in': {
    text: "",
    instruction: "Trzymaj powietrze w płucach",
    scale: "scale-150", // Zostaje duże
    duration: "duration-0", // Brak animacji zmiany rozmiaru (bo się nie zmienia)
  },
  exhale: {
    text: "",
    instruction: "Wypuszczaj powietrze ustami...",
    scale: "scale-100", // Wraca do oryginału
    duration: "duration-[4000ms]", // Zmiana w 4 sekundy
  },
  'hold-out': {
    text:"",
    instruction: "Nie nabieraj jeszcze powietrza",
    scale: "scale-100", // Zostaje małe
    duration: "duration-0",
  },
};

export default function BoxBreathing() {
    const [isActive, setIsActive] = useState(false);
    const [phase, setPhase] = useState<Phase>('idle');

    useEffect(() => {
    let timeout: ReturnType<typeof setTimeout> | undefined;

    if (isActive) {
        switch (phase) {
            case 'idle':
                setPhase('inhale');
                break;
            case 'inhale':
                timeout = setTimeout(() => setPhase('hold-in'), 4000)
                break;
            case 'hold-in':
                timeout = setTimeout(() => setPhase('exhale'), 4000)
                break;
            case 'exhale':
                timeout = setTimeout(() => setPhase('hold-out'), 4000)
                break;
            case 'hold-out':
                timeout = setTimeout(() => setPhase('inhale'), 4000)
                break;
        }
} else {
        setPhase('idle');
        if (timeout) clearTimeout(timeout);
    }

    return () => {
        if (timeout) clearTimeout(timeout);
    };
}, [isActive, phase]);

const handleToggle = () => setIsActive(!isActive);
const currentConfig = PHASE_CONFIG[phase];

return (
  <div>
    <BiofeedbackChart />
    <div className="font-mono flex flex-col items-center justify-center min-h-[500px] w-full bg-green-50 p-6 rounded-3xl">
     {/* Nagłówek */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-green-800 mb-2">Box Breathing</h2>
        <p className="text-green-600">Uspokój oddech w 4 krokach</p>
      </div>

       {/* Główna animacja */}
      <div className="relative flex items-center justify-center w-64 h-64 mb-12">
        {/* Tło "duch" pokazujące maksymalny rozmiar */}
        <div className="absolute w-32 h-32 bg-green-200 rounded-full scale-150 opacity-20" />
        
        {/* Właściwe animowane koło */}
        <div
          className={`
            flex items-center justify-center
            w-32 h-32 bg-gradient-to-br from-green-400 to-green-600 
            rounded-full shadow-xl shadow-green-200
            transition-all ease-linear
            ${currentConfig.scale}
            ${currentConfig.duration}
          `}
        >
          <span className="text-white font-bold text-lg animate-pulse">
            {isActive && phase !== 'idle' ? phase === 'inhale' ? 'Wdech' : phase === 'exhale' ? 'Wydech' : 'czymaj' : ''}
          </span>
        </div>
      </div>

    {/* Instrukcje tekstowe */}
      <div className="text-center h-20 mb-8 transition-opacity duration-500">
        {/* <h3 className="text-4xl font-bold text-green-700 mb-2">
          {currentConfig.text}
        </h3> */}
        <p className="text-green-600 text-lg font-medium">
          {currentConfig.instruction}
        </p>
      </div>

    {/* Kontrolery */}
      <button
        onClick={handleToggle}
        className={`
          flex items-center gap-2 px-8 py-3 rounded-full font-bold text-lg text-white transition-all
          ${isActive 
            ? 'bg-red-500 hover:bg-red-600 shadow-red-200' 
            : 'bg-green-600 hover:bg-green-700 shadow-green-200'
          } shadow-lg hover:scale-105 active:scale-95
        `}
      >
        {isActive ? (
            <>
                <Square size={20} fill="currentColor" /> Zatrzymaj
            </>
        ) : (
            <>
                {phase === 'idle' ? <Play size={20} fill="currentColor" /> : <RefreshCcw size={20} />}
                {phase === 'idle' ? 'Rozpocznij' : ''}
            </>
    )}
      </button>
    </div>
  </div>
);
}