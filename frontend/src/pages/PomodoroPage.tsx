import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Coffee, Briefcase, Brain, Zap } from 'lucide-react';
import treeGif from '../assets/tree.gif';
import BiofeedbackChart from '../components/BiofeedbackChart';
import OpacityBiofeedbackChart from '../components/OpacityBiofeedbackChart';
// 1. DODANO: import serwisu API
import { apiService, type TimerConfig } from '../services/api';

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

// 2. ZMIANA: To teraz służy jako wartości startowe (fallback), zanim przyjdą dane z API
const FALLBACK_CONFIG: TimerConfig = {
  work: 25 * 60,
  shortBreak: 5 * 60,
  longBreak: 15 * 60,
};

export default function PomodoroPage() {
  // 3. DODANO: Stan trzymający konfigurację (zaczyna od fallbacka)
  const [config, setConfig] = useState<TimerConfig>(FALLBACK_CONFIG);

  const [mode, setMode] = useState<TimerMode>('work');
  const [timeLeft, setTimeLeft] = useState(FALLBACK_CONFIG.work);
  const [isActive, setIsActive] = useState(false);
  const [completedPomodoros, setCompletedPomodoros] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // 4. DODANO: Pobieranie konfiguracji z backendu po załadowaniu strony
  useEffect(() => {
    const fetchConfig = async () => {
      try {
        // Zakładam, że dodałeś metodę getPomodoroConfig do apiService
        const apiConfig = await apiService.getPomodoroConfig();
        console.log("Pobrany config z API:", apiConfig);
        setConfig(apiConfig);
        
        // Jeśli timer nie odlicza, zaktualizuj od razu czas na ekranie
        if (!isActive) {
            setTimeLeft(apiConfig[mode]);
        }
      } catch (error) {
        console.error("Błąd pobierania configu, używam domyślnego:", error);
      }
    };
    fetchConfig();
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Wywołaj tylko raz

  // 5. ZMIANA: Używamy 'config' zamiast stałej
  const totalTime = config[mode];
  const progress = ((totalTime - timeLeft) / totalTime) * 100;

  useEffect(() => {
    if (isActive && timeLeft > 0) {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (timeLeft === 0) {
      handleTimerComplete();
    }

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isActive, timeLeft]);

  const handleTimerComplete = () => {
    setIsActive(false);
    
    if (mode === 'work') {
      const newCount = completedPomodoros + 1;
      setCompletedPomodoros(newCount);
      
      // Every 4 pomodoros, take a long break
      if (newCount % 4 === 0) {
        switchMode('longBreak');
      } else {
        switchMode('shortBreak');
      }
    } else {
      switchMode('work');
    }

    playNotificationSound();
  };

  const playNotificationSound = () => {
    const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
    const oscillator = audioContext.createOscillator();
    const gainNode = audioContext.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(audioContext.destination);
    
    oscillator.frequency.value = 800;
    oscillator.type = 'sine';
    
    gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
    gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
    
    oscillator.start(audioContext.currentTime);
    oscillator.stop(audioContext.currentTime + 0.5);
  };

  const switchMode = (newMode: TimerMode) => {
    setMode(newMode);
    // 6. ZMIANA: Używamy 'config'
    setTimeLeft(config[newMode]);
    setIsActive(false);
  };

  const handleToggle = () => {
    setIsActive(!isActive);
  };

  const handleReset = () => {
    setIsActive(false);
    // 7. ZMIANA: Używamy 'config'
    setTimeLeft(config[mode]);
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const getModeConfig = () => {
    switch (mode) {
      case 'work':
        return {
          title: 'Czas na Pracę',
          subtitle: 'Skup się na zadaniu',
          color: 'from-sky-500/20 to-cyan-500/20',
          borderColor: 'border-sky-500/50',
          textColor: 'text-sky-400',
          icon: Briefcase,
        };
      case 'shortBreak':
        return {
          title: 'Krótka Przerwa',
          subtitle: 'Chwila odpoczynku',
          color: 'from-green-500/20 to-emerald-500/20',
          borderColor: 'border-green-500/50',
          textColor: 'text-green-400',
          icon: Coffee,
        };
      case 'longBreak':
        return {
          title: 'Długa Przerwa',
          subtitle: 'Zrelaksuj się',
          color: 'from-blue-500/20 to-cyan-500/20',
          borderColor: 'border-blue-500/50',
          textColor: 'text-blue-400',
          icon: Coffee,
        };
    }
  };

  const uiConfig = getModeConfig();
  const Icon = uiConfig.icon;

  return (
    <div className="relative w-full max-w-xl lg:max-w-2xl mx-auto px-4">
      {/* Background GIF */}
      <div className="fixed inset-0 z-0 pointer-events-none">
        <img
          src={treeGif}
          alt="Tree background"
          className="w-full h-full object-cover opacity-40"
        />
      </div>
      
      {/* Content wrapper */}
      <div className="relative z-10">
  <div className='font-mono'>
    <OpacityBiofeedbackChart />
    <div className="w-full max-w-xl lg:max-w-2xl mx-auto px-4 mt-8">
      {/* Header */}
      <div className="text-center mb-6 md:mb-10 lg:mb-12">
        <div className="flex items-center justify-center gap-2 md:gap-3 mb-2 md:mb-3">
          <Brain className="w-7 h-7 md:w-8 md:h-8 text-white" />
          <h2 className="text-xl sm:text-2xl md:text-3xl font-bold text-white">Adaptywny Pomodoro</h2>
        </div>
        <p className="text-xs sm:text-sm md:text-base text-white/70">Timer dostosowujący się do Twojego stanu flow</p>
        <div className="mt-2 md:mt-3 inline-flex items-center gap-1.5 md:gap-2 px-3 md:px-4 py-1.5 md:py-2 bg-white/10 rounded-full border border-white/30">
          <Zap className="w-3 h-3 md:w-4 md:h-4 text-white" />
          <span className="text-xs md:text-sm text-white font-medium">Automatyczne dostosowanie czasu pracy</span>
        </div>
      </div>

      {/* Current Mode Display - No manual switching */}
      <div className="flex justify-center mb-4 md:mb-6 lg:mb-8">
        <div className="px-4 sm:px-6 md:px-8 py-2 sm:py-3 md:py-4 rounded-lg text-xs sm:text-sm md:text-base font-semibold border-2 bg-white/10 text-white border-white/30">
          {mode === 'work' && <Briefcase className="inline-block w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />}
          {mode !== 'work' && <Coffee className="inline-block w-4 h-4 sm:w-5 sm:h-5 mr-1.5 sm:mr-2" />}
          {mode === 'work' ? 'Sesja Pracy' : mode === 'shortBreak' ? 'Krótka Przerwa' : 'Długa Przerwa'}
        </div>
      </div>

      {/* Main Timer Display */}
      <div className="bg-white/5 backdrop-blur-lg rounded-xl md:rounded-2xl p-4 sm:p-6 md:p-10 lg:p-12 border-2 border-white/20 mb-4 md:mb-6 lg:mb-8">
        <div className="text-center">
          {/* Mode Title */}
          <div className="flex items-center justify-center mb-3 sm:mb-4 md:mb-6">
            <Icon className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8 mr-2 md:mr-3 text-white" />
            <div>
              <h3 className="text-lg sm:text-xl md:text-2xl font-bold text-white">{uiConfig.title}</h3>
              <p className="text-white/70 text-xs sm:text-xs md:text-sm">{uiConfig.subtitle}</p>
            </div>
          </div>

          {/* Timer Circle */}
          <div className="relative w-56 sm:w-64 md:w-72 lg:w-80 h-56 sm:h-64 md:h-72 lg:h-80 mx-auto mb-4 sm:mb-6 md:mb-8">
            {/* Progress Circle */}
            <svg className="w-full h-full transform -rotate-90" viewBox="0 0 320 320">
              <circle
                cx="160"
                cy="160"
                r="140"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-white/20"
              />
              <circle
                cx="160"
                cy="160"
                r="140"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                strokeDasharray={`${2 * Math.PI * 140}`}
                strokeDashoffset={`${2 * Math.PI * 140 * (1 - progress / 100)}`}
                className="text-white transition-all duration-1000 ease-linear"
                strokeLinecap="round"
              />
            </svg>
            
            {/* Time Display */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-white font-mono">
                {formatTime(timeLeft)}
              </span>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex justify-center gap-2 sm:gap-3 md:gap-4">
            <button
              onClick={handleToggle}
              className="px-5 sm:px-6 md:px-8 py-2.5 sm:py-3 md:py-4 rounded-lg text-xs sm:text-sm md:text-base font-semibold transition-all duration-300 flex items-center gap-1.5 sm:gap-2 bg-white/10 text-white border-2 border-white/30 hover:bg-white/20 hover:border-white/40"
            >
              {isActive ? (
                <>
                  <Pause className="w-4 h-4 sm:w-5 sm:h-5" />
                  Pauza
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 sm:w-5 sm:h-5" />
                  Start
                </>
              )}
            </button>
            <button
              onClick={handleReset}
              className="px-5 sm:px-6 md:px-8 py-2.5 sm:py-3 md:py-4 rounded-lg text-xs sm:text-sm md:text-base font-semibold transition-all duration-300 bg-white/5 text-white/70 border-2 border-white/20 hover:border-white/30 hover:text-white flex items-center gap-1.5 sm:gap-2"
            >
              <RotateCcw className="w-4 h-4 sm:w-5 sm:h-5" />
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Pomodoro Counter */}
      <div className="bg-white/5 backdrop-blur-lg rounded-xl md:rounded-2xl p-3 sm:p-4 md:p-6 border-2 border-white/20 text-center">
        <h4 className="text-sm sm:text-base md:text-lg font-semibold text-white mb-2 md:mb-3">Ukończone Pomodoro</h4>
        <div className="flex justify-center gap-1.5 sm:gap-2">
          {[...Array(completedPomodoros % 4 || (completedPomodoros > 0 ? 4 : 0))].map((_, i) => (
            <div key={i} className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-white"></div>
          ))}
          {[...Array(4 - (completedPomodoros % 4 || (completedPomodoros > 0 ? 4 : 0)))].map((_, i) => (
            <div key={i} className="w-3 h-3 sm:w-4 sm:h-4 rounded-full bg-white/20"></div>
          ))}
        </div>
        <p className="text-white/70 text-xs sm:text-sm mt-2 md:mt-3">
          Łącznie: <span className="font-bold text-white">{completedPomodoros}</span> pomodoro
        </p>
      </div>
      
      </div>
    </div>

    </div>
  </div>
  );
}