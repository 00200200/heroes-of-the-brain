import { Play, Square, CloudMoon, CheckCircle2, Wind } from 'lucide-react';
import { useState, useEffect, useRef, useMemo } from 'react';
import BiofeedbackChart from '../components/BiofeedbackChart';
import OpacityBiofeedbackChart from '../components/OpacityBiofeedbackChart';

// --- TŁO (GWIAZDY) ---
const StarBackground = () => {
  const stars = useMemo(() => {
    return Array.from({ length: 100 }).map((_, i) => ({
      id: i,
      top: `${Math.random() * 100}%`,
      left: `${Math.random() * 100}%`,
      size: `${Math.random() * 3 + 1}px`,
      animationDelay: `${Math.random() * 5}s`,
      opacity: Math.random() * 0.7 + 0.1,
    }));
  }, []);

  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden bg-slate-950 z-0">
      <div className="absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-indigo-900/20 rounded-full blur-[120px]" />
      <div className="absolute bottom-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-900/20 rounded-full blur-[120px]" />
      {stars.map((star) => (
        <div
          key={star.id}
          className="absolute bg-white rounded-full animate-pulse"
          style={{
            top: star.top,
            left: star.left,
            width: star.size,
            height: star.size,
            opacity: star.opacity,
            animationDuration: '4s',
            animationDelay: star.animationDelay,
          }}
        />
      ))}
    </div>
  );
};

// --- KONFIGURACJA ---
type SleepPhase = 'intro' | 'feet' | 'legs' | 'stomach' | 'shoulders' | 'face' | 'complete';

const SLEEP_SEQUENCE: Record<SleepPhase, { title: string; instruction: string; duration: number }> = {
  intro: { title: "Przygotowanie do snu", instruction: "Połóż się wygodnie i zamknij oczy...", duration: 5000 },
  feet: { title: "Stopy i Kostki", instruction: "Poczuj ciężar swoich stóp. Napnij je lekko, a potem całkowicie rozluźnij...", duration: 10000 },
  legs: { title: "Łydki i Uda", instruction: "Poczuj jak ciepło rozlewa się po twoich nogach. Pozwól im zapaść się w materac...", duration: 10000 },
  stomach: { title: "Brzuch i Oddech", instruction: "Oddychaj głęboko do brzucha. Z każdym wydechem uwalniasz napięcie...", duration: 10000 },
  shoulders: { title: "Ramiona i Szyja", instruction: "Opuść ramiona. Poczuj jak cały stres dnia spływa z ciebie na podłogę...", duration: 10000 },
  face: { title: "Twarz i Oczy", instruction: "Rozluźnij szczękę. Niech twoje powieki staną się przyjemnie ciężkie...", duration: 10000 },
  complete: { title: "Błogi Spokój", instruction: "Jesteś gotowy do snu. Dobranoc.", duration: 0 }
};

const PHASE_ORDER: SleepPhase[] = ['intro', 'feet', 'legs', 'stomach', 'shoulders', 'face', 'complete'];

export default function SleepPreparationPage() {
  const [isActive, setIsActive] = useState(false);
  const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
  const [progress, setProgress] = useState(0);

  const currentPhaseKey = PHASE_ORDER[currentPhaseIndex];
  const currentConfig = SLEEP_SEQUENCE[currentPhaseKey];
  
  const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const nextStep = () => {
    if (currentPhaseIndex < PHASE_ORDER.length - 1) {
      setCurrentPhaseIndex(prev => prev + 1);
      setProgress(0);
    } else {
      setIsActive(false);
    }
  };

  useEffect(() => {
    if (isActive && currentPhaseKey !== 'complete') {
      const duration = currentConfig.duration;
      timerRef.current = setTimeout(() => nextStep(), duration);

      const stepTime = 50; 
      const steps = duration / stepTime;
      let currentStep = 0;

      progressIntervalRef.current = setInterval(() => {
        currentStep++;
        const newProgress = Math.min((currentStep / steps) * 100, 100);
        setProgress(newProgress);
      }, stepTime);
    } else {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    }
    return () => {
      if (timerRef.current) clearTimeout(timerRef.current);
      if (progressIntervalRef.current) clearInterval(progressIntervalRef.current);
    };
  }, [isActive, currentPhaseIndex]);

  const handleStartStop = () => {
    if (currentPhaseKey === 'complete') {
      setCurrentPhaseIndex(0);
      setProgress(0);
      setIsActive(true);
    } else {
      setIsActive(!isActive);
    }
  };

  return (
    <div className="min-h-screen relative font-mono overflow-hidden">
      <StarBackground />

      <div className="relative z-10 p-6 max-w-2xl mx-auto space-y-8">
        <OpacityBiofeedbackChart />

        <div className="flex flex-col items-center justify-center min-h-[500px] w-full bg-slate-900/60 backdrop-blur-md text-slate-100 p-8 rounded-3xl shadow-2xl border border-indigo-500/20 relative">
          
          <div className="text-center mb-10 z-10 !opacity-100">
            <div className="flex items-center justify-center gap-3 mb-3 text-indigo-300">
              <CloudMoon size={32} />
              <span className="uppercase tracking-widest text-xs font-bold">Tryb Nocny</span>
            </div>
            <h2 className="text-3xl md:text-4xl font-bold text-slate-100 mb-2 drop-shadow-lg">Wieczorne Wyciszenie</h2>
            <p className="text-slate-300 max-w-md mx-auto">Skanowanie ciała – progresywna relaksacja.</p>
          </div>

          {/* --- NOWA WIZUALIZACJA (BĄBEL) --- */}
          <div className="relative mb-12 z-10">
            <div className={`w-64 h-64 rounded-full border-4 flex items-center justify-center relative overflow-hidden
              ${isActive ? 'border-indigo-500/30 bg-slate-900/50' : 'border-slate-700/50 bg-slate-800/40'}
            `}>
              
              {/* Wypełniające się koło w tle (zastępuje SVG) */}
              {isActive && currentPhaseKey !== 'complete' && (
                <div 
                  className="absolute inset-0 bg-indigo-500/40 rounded-full"
                  style={{ 
                    transform: `scale(${progress / 80})`, 
                    // Dodajemy transition, żeby wygładzić skoki co 50ms
                    transition: 'transform 100ms linear' 
                  }}
                />
              )}

              {/* Ikona na wierzchu */}
              <div className={`relative z-10 transition-all duration-700 transform ${isActive ? 'scale-110 text-indigo-100' : 'scale-100 text-slate-500'}`}>
                 {currentPhaseKey === 'complete' ? <CheckCircle2 size={64} /> : <Wind size={64} />}
              </div>
            </div>
          </div>

          <div className="text-center h-32 max-w-lg mx-auto z-10 transition-all duration-500">
            <h3 className="text-2xl font-bold text-indigo-100 mb-3 animate-fade-in drop-shadow-md">
              {currentConfig.title}
            </h3>
            <p className="text-lg text-slate-200 leading-relaxed animate-fade-in">
              {currentConfig.instruction}
            </p>
          </div>

          <button
            onClick={handleStartStop}
            className={`
              z-10 flex items-center gap-3 px-10 py-4 rounded-full font-bold text-lg transition-all duration-300
              ${isActive 
                ? 'bg-slate-800/80 hover:bg-slate-700 text-indigo-300 ring-1 ring-indigo-500/40' 
                : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-900/50'
              }
              hover:scale-105 active:scale-95 backdrop-blur-sm
            `}
          >
            {isActive ? (
              <><Square size={20} fill="currentColor" /> Pauza</>
            ) : (
              <><Play size={20} fill="currentColor" /> 
              {currentPhaseKey === 'complete' ? 'Zacznij od nowa' : 'Rozpocznij relaksację'}</>
            )}
          </button>
          
          <div className="flex gap-2 mt-8 z-10">
            {PHASE_ORDER.map((phase, idx) => (
              <div 
                key={phase}
                className={`w-2 h-2 rounded-full transition-all duration-500 ${
                  idx === currentPhaseIndex ? 'bg-indigo-400 w-6 shadow-[0_0_10px_rgba(129,140,248,0.8)]' : 
                  idx < currentPhaseIndex ? 'bg-indigo-800' : 'bg-slate-700'
                }`}
              />
            ))}
          </div>

        </div>
      </div>
    </div>
  );
}