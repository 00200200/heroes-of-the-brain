import React, { useState, useEffect } from 'react';

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
const currentConfing = PHASE_CONFIG[phase];

return (
    <div>
     {/* Nagłówek */}
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-green-800 mb-2">Box Breathing</h2>
        <p className="text-green-600">Uspokój oddech w 4 krokach</p>
      </div>
    </div>

);
}