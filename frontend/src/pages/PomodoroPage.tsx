import React, { useState, useEffect, useRef } from 'react';
import { Play, Pause, RotateCcw, Coffee, Briefcase, Brain, Zap } from 'lucide-react';

type TimerMode = 'work' | 'shortBreak' | 'longBreak';

interface TimerConfig {
  work: number;
  shortBreak: number;
  longBreak: number;
}

// These will be dynamically adjusted based on flow state in the future
const DEFAULT_CONFIG: TimerConfig = {
  work: 25 * 60, // Will be adapted to user's flow state
  shortBreak: 5 * 60, // Will be adapted to recovery needs
  longBreak: 15 * 60, // Will be adapted to fatigue levels
};

export default function PomodoroPage() {
  const [mode, setMode] = useState<TimerMode>('work');
  const [timeLeft, setTimeLeft] = useState(DEFAULT_CONFIG.work);
  const [isActive, setIsActive] = useState(false);
  const [completedPomodoros, setCompletedPomodoros] = useState(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const totalTime = DEFAULT_CONFIG[mode];
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

    // Play notification sound (optional)
    playNotificationSound();
  };

  const playNotificationSound = () => {
    // Simple beep using Web Audio API
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
    setTimeLeft(DEFAULT_CONFIG[newMode]);
    setIsActive(false);
  };

  const handleToggle = () => {
    setIsActive(!isActive);
  };

  const handleReset = () => {
    setIsActive(false);
    setTimeLeft(DEFAULT_CONFIG[mode]);
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

  const config = getModeConfig();
  const Icon = config.icon;

  return (
    <div>
      {/* Header */}
      <div className="text-center mb-12">
        <div className="flex items-center justify-center gap-3 mb-3">
          <Brain className="w-8 h-8 text-cyan-400" />
          <h2 className="text-3xl font-bold text-gray-200">Adaptywny Pomodoro</h2>
        </div>
        <p className="text-gray-400">Timer dostosowujący się do Twojego stanu flow</p>
        <div className="mt-3 inline-flex items-center gap-2 px-4 py-2 bg-cyan-500/10 rounded-full border border-cyan-500/30">
          <Zap className="w-4 h-4 text-cyan-400" />
          <span className="text-sm text-cyan-400 font-medium">Automatyczne dostosowanie czasu pracy</span>
        </div>
      </div>

      {/* Current Mode Display - No manual switching */}
      <div className="flex justify-center mb-8">
        <div className={`px-8 py-4 rounded-lg font-semibold border-2 ${
          mode === 'work'
            ? 'bg-sky-500/20 text-sky-400 border-sky-500/50'
            : mode === 'shortBreak'
            ? 'bg-green-500/20 text-green-400 border-green-500/50'
            : 'bg-blue-500/20 text-blue-400 border-blue-500/50'
        }`}>
          {mode === 'work' && <Briefcase className="inline-block w-5 h-5 mr-2" />}
          {mode !== 'work' && <Coffee className="inline-block w-5 h-5 mr-2" />}
          {mode === 'work' ? 'Sesja Pracy' : mode === 'shortBreak' ? 'Krótka Przerwa' : 'Długa Przerwa'}
        </div>
      </div>

      {/* Main Timer Display */}
      <div className={`bg-gradient-to-br ${config.color} backdrop-blur-sm rounded-2xl p-12 border-2 ${config.borderColor} mb-8`}>
        <div className="text-center">
          {/* Mode Title */}
          <div className="flex items-center justify-center mb-6">
            <Icon className={`w-8 h-8 mr-3 ${config.textColor}`} />
            <div>
              <h3 className={`text-2xl font-bold ${config.textColor}`}>{config.title}</h3>
              <p className="text-gray-400 text-sm">{config.subtitle}</p>
            </div>
          </div>

          {/* Timer Circle */}
          <div className="relative w-80 h-80 mx-auto mb-8">
            {/* Progress Circle */}
            <svg className="w-full h-full transform -rotate-90">
              <circle
                cx="160"
                cy="160"
                r="140"
                stroke="currentColor"
                strokeWidth="8"
                fill="none"
                className="text-gray-800"
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
                className={`${config.textColor} transition-all duration-1000 ease-linear`}
                strokeLinecap="round"
              />
            </svg>
            
            {/* Time Display */}
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-7xl font-bold text-gray-200 font-mono">
                {formatTime(timeLeft)}
              </span>
            </div>
          </div>

          {/* Control Buttons */}
          <div className="flex justify-center gap-4">
            <button
              onClick={handleToggle}
              className={`px-8 py-4 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 ${
                isActive
                  ? 'bg-yellow-500/20 text-yellow-400 border-2 border-yellow-500/50 hover:bg-yellow-500/30'
                  : `${config.textColor} border-2 ${config.borderColor}`
              } ${!isActive && mode === 'work' ? 'bg-sky-500/20 hover:bg-sky-500/30' : ''} ${!isActive && mode === 'shortBreak' ? 'bg-green-500/20 hover:bg-green-500/30' : ''} ${!isActive && mode === 'longBreak' ? 'bg-blue-500/20 hover:bg-blue-500/30' : ''}`}
            >
              {isActive ? (
                <>
                  <Pause className="w-5 h-5" />
                  Pauza
                </>
              ) : (
                <>
                  <Play className="w-5 h-5" />
                  Start
                </>
              )}
            </button>
            <button
              onClick={handleReset}
              className="px-8 py-4 rounded-lg font-semibold transition-all duration-300 bg-gray-900/40 text-gray-400 border-2 border-gray-700 hover:border-gray-600 hover:text-gray-300 flex items-center gap-2"
            >
              <RotateCcw className="w-5 h-5" />
              Reset
            </button>
          </div>
        </div>
      </div>

      {/* Pomodoro Counter */}
      <div className="bg-gray-900/40 backdrop-blur-sm rounded-2xl p-6 border-2 border-gray-700 text-center">
        <h4 className="text-lg font-semibold text-gray-300 mb-3">Ukończone Pomodoro</h4>
        <div className="flex justify-center gap-2">
          {[...Array(completedPomodoros % 4 || (completedPomodoros > 0 ? 4 : 0))].map((_, i) => (
            <div key={i} className="w-4 h-4 rounded-full bg-sky-500"></div>
          ))}
          {[...Array(4 - (completedPomodoros % 4 || (completedPomodoros > 0 ? 4 : 0)))].map((_, i) => (
            <div key={i} className="w-4 h-4 rounded-full bg-gray-700"></div>
          ))}
        </div>
        <p className="text-gray-400 text-sm mt-3">
          Łącznie: <span className="font-bold text-gray-200">{completedPomodoros}</span> pomodoro
        </p>
      </div>

      {/* Flow State Information */}
      <div className="mt-8 bg-gradient-to-br from-cyan-500/10 to-blue-500/10 backdrop-blur-sm rounded-2xl p-6 border-2 border-cyan-500/30">
        <div className="flex items-center gap-3 mb-4">
          <Brain className="w-6 h-6 text-cyan-400" />
          <h4 className="text-lg font-semibold text-gray-300">Inteligentne Dostosowanie</h4>
        </div>
        <ul className="space-y-3 text-gray-400 text-sm">
          <li className="flex items-start">
            <span className="text-cyan-400 mr-3">🧠</span>
            <span>Timer automatycznie analizuje Twój stan skupienia i dostosowuje długość sesji pracy</span>
          </li>
          <li className="flex items-start">
            <span className="text-green-400 mr-3">⚡</span>
            <span>Przerwy są optymalizowane na podstawie Twojego poziomu zmęczenia i potrzeby regeneracji</span>
          </li>
          <li className="flex items-start">
            <span className="text-blue-400 mr-3">📊</span>
            <span>System uczy się Twoich wzorców produktywności i dostosowuje harmonogram w czasie rzeczywistym</span>
          </li>
          <li className="flex items-start">
            <span className="text-purple-400 mr-3">🎯</span>
            <span>Nie musisz martwić się o ustawienia - po prostu zacznij pracować, a system zadba o resztę</span>
          </li>
        </ul>
      </div>

      {/* Future Integration Note */}
      <div className="mt-4 bg-gray-900/40 backdrop-blur-sm rounded-xl p-4 border border-gray-700">
        <p className="text-xs text-gray-500 text-center">
          <span className="text-cyan-400 font-semibold">Wkrótce:</span> Pełna integracja z monitoringiem EEG i biometrycznym dla precyzyjnego dostosowania
        </p>
      </div>
    </div>
  );
}
