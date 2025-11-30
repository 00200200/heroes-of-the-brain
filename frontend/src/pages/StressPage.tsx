import { RefreshCcw, Square, Play } from 'lucide-react';
import { useState, useEffect } from 'react';
import OpacityBiofeedbackChart from '../components/OpacityBiofeedbackChart';
import forestGif from '../assets/forest.gif';

// Definicja faz cyklu
type Phase = 'idle' | 'countdown' | 'inhale' | 'hold-in' | 'exhale' | 'hold-out';

const PHASE_CONFIG = {
  idle: {
    text: "Ready?",
    instruction: "Press start to begin",
    scale: "scale-100",
    duration: "duration-300",
  },
  countdown: {
    text: "",
    instruction: "Get ready...",
    scale: "scale-100",
    duration: "duration-300",
  },
  inhale: {
    text:"",
    instruction: "Inhale through your nose...",
    scale: "scale-150",
    duration: "duration-[4000ms]",
  },
  'hold-in': {
    text: "",
    instruction: "Hold it in your lungs",
    scale: "scale-150",
    duration: "duration-0",
  },
  exhale: {
    text: "",
    instruction: "Exhale through your mouth...",
    scale: "scale-100",
    duration: "duration-[4000ms]",
  },
  'hold-out': {
    text:"",
    instruction: "Hold your breath",
    scale: "scale-100",
    duration: "duration-0",
  },
};

export default function BoxBreathing() {
    const [isActive, setIsActive] = useState(false);
    const [phase, setPhase] = useState<Phase>('idle');
    const [countdown, setCountdown] = useState<number>(0);

    useEffect(() => {
    let timeout: ReturnType<typeof setTimeout> | undefined;

    if (isActive) {
        switch (phase) {
            case 'idle':
                setPhase('countdown');
                setCountdown(3);
                break;
            case 'countdown':
                if (countdown > 1) {
                    timeout = setTimeout(() => setCountdown(countdown - 1), 1000);
                } else {
                    timeout = setTimeout(() => setPhase('inhale'), 1000);
                }
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
        setCountdown(0);
        if (timeout) clearTimeout(timeout);
    }

    return () => {
        if (timeout) clearTimeout(timeout);
    };
}, [isActive, phase, countdown]);

const handleToggle = () => setIsActive(!isActive);
const currentConfig = PHASE_CONFIG[phase];

return (
  <div className="relative w-full max-w-xl lg:max-w-2xl mx-auto px-4">
    {/* Background GIF */}
    <div className="fixed inset-0 z-0 pointer-events-none">
      <img
        src={forestGif}
        alt="Forest background"
        className="w-full h-full object-cover opacity-60"
      />
    </div>
    
    {/* Content wrapper */}
    <div className="relative z-10">
      <div className="font-mono">
        <OpacityBiofeedbackChart />
        <div className="relative flex flex-col items-center justify-center min-h-[500px] w-full bg-black/40 backdrop-blur-md p-8 rounded-3xl border-2 border-white/20 shadow-2xl overflow-hidden mt-8">
      {/* Futuristic animated background */}
      <div className="absolute inset-0 opacity-30">
        {/* Animated gradient orbs */}
        <div className="absolute top-10 left-10 w-64 h-64 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '4s' }} />
        <div className="absolute bottom-10 right-10 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '6s' }} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDuration: '5s' }} />
        
        {/* Grid pattern */}
        <div className="absolute inset-0" style={{
          backgroundImage: 'linear-gradient(rgba(6, 182, 212, 0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(6, 182, 212, 0.05) 1px, transparent 1px)',
          backgroundSize: '50px 50px'
        }} />
      </div>

      {/* Content layer */}
      <div className="relative z-10 flex flex-col items-center w-full">
     {/* Nagłówek */}
      <div className="text-center mb-12 animate-fade-in">
        <h2 className="text-4xl font-bold bg-gradient-to-r from-cyan-400 to-blue-400 bg-clip-text text-transparent mb-3">
          Box Breathing
        </h2>
        <p className="text-gray-400 text-lg">Relax your breath in 4 steps</p>
      </div>

       {/* Główna animacja */}
      <div className="relative flex items-center justify-center w-80 h-80 mb-12">
        <style>{`
          @keyframes drawLine {
            from {
              stroke-dashoffset: 200;
            }
            to {
              stroke-dashoffset: 0;
            }
          }
          .animate-draw-line {
            animation: drawLine 4s linear forwards;
          }
        `}</style>
        
        {/* SVG phase-synced drawing animation */}
        <svg
          className="absolute"
          width="320"
          height="320"
          viewBox="0 0 320 320"
          style={{
            filter: 'drop-shadow(0 0 15px rgba(6, 182, 212, 0.6))'
          }}
        >
          {/* Ghost outline showing full path */}
          <rect
            x="60"
            y="60"
            width="200"
            height="200"
            fill="none"
            stroke="rgba(6, 182, 212, 0.15)"
            strokeWidth="2"
          />
          
          {/* Animated drawing line - progressively draws each side */}
          {(isActive && phase !== 'idle' && phase !== 'countdown') && (
            <>
              {/* Top side - Inhale - draws left to right */}
              <line
                x1="60"
                y1="60"
                x2="260"
                y2="60"
                stroke="rgba(6, 182, 212, 1)"
                strokeWidth="6"
                strokeLinecap="round"
                strokeDasharray="200"
                strokeDashoffset="200"
                className={phase === 'inhale' ? 'animate-draw-line' : ''}
                style={{
                  strokeDashoffset: phase === 'inhale' ? undefined : '0'
                }}
              />
              
              {/* Right side - Hold-in - draws top to bottom */}
              {(phase === 'hold-in' || phase === 'exhale' || phase === 'hold-out') && (
                <line
                  x1="260"
                  y1="60"
                  x2="260"
                  y2="260"
                  stroke="rgba(6, 182, 212, 1)"
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray="200"
                  strokeDashoffset="200"
                  className={phase === 'hold-in' ? 'animate-draw-line' : ''}
                  style={{
                    strokeDashoffset: phase === 'hold-in' ? undefined : '0'
                  }}
                />
              )}
              
              {/* Bottom side - Exhale - draws right to left */}
              {(phase === 'exhale' || phase === 'hold-out') && (
                <line
                  x1="260"
                  y1="260"
                  x2="60"
                  y2="260"
                  stroke="rgba(6, 182, 212, 1)"
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray="200"
                  strokeDashoffset="200"
                  className={phase === 'exhale' ? 'animate-draw-line' : ''}
                  style={{
                    strokeDashoffset: phase === 'exhale' ? undefined : '0'
                  }}
                />
              )}
              
              {/* Left side - Hold-out - draws bottom to top */}
              {phase === 'hold-out' && (
                <line
                  x1="60"
                  y1="260"
                  x2="60"
                  y2="60"
                  stroke="rgba(6, 182, 212, 1)"
                  strokeWidth="6"
                  strokeLinecap="round"
                  strokeDasharray="200"
                  strokeDashoffset="200"
                  className="animate-draw-line"
                />
              )}
            </>
          )}
        </svg>
        
        {/* Center content */}
        <div className="relative flex items-center justify-center z-10">
          {phase === 'countdown' ? (
            <span className="text-white font-bold text-6xl">
              {countdown}
            </span>
          ) : (
            <span className="text-white font-semibold text-xl tracking-wide drop-shadow-lg">
              {isActive && phase !== 'idle' ? 
                phase === 'inhale' ? 'Inhale' : 
                phase === 'exhale' ? 'Exhale' : 
                'Hold' 
              : ''}
            </span>
          )}
        </div>
      </div>

    {/* Instrukcje tekstowe */}
      <div className="text-center h-20 mb-10 transition-all duration-500">
        <p className="text-gray-300 text-xl font-medium tracking-wide drop-shadow-lg">
          {currentConfig.instruction}
        </p>
      </div>

    {/* Kontrolery */}
      <button
        onClick={handleToggle}
        className={`
          flex items-center gap-2 px-8 py-3 rounded-lg font-bold text-base transition-all duration-300 text-white
          ${isActive 
            ? 'bg-red-500/80 hover:bg-red-600 border-2 border-red-500/50 hover:border-red-500' 
            : 'bg-white/10 border-2 border-white/30 hover:bg-white/20 hover:border-white/40'
          } 
          shadow-lg hover:scale-105 active:scale-95
        `}
      >
        {isActive ? (
            <>
                <Square size={20} fill="currentColor" /> 
                <span>Stop</span>
            </>
        ) : (
            <>
                {phase === 'idle' ? (
                  <>
                    <Play size={20} fill="currentColor" />
                    <span>Begim</span>
                  </>
                ) : (
                  <>
                    <RefreshCcw size={20} />
                    <span>Retry</span>
                  </>
                )}
            </>
    )}
      </button>
      </div>
    </div>
      </div>
    </div>
  </div>
);
}