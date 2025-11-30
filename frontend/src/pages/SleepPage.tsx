import { Play, Square, CloudMoon, CheckCircle2, Wind, Volume2, VolumeX } from 'lucide-react';
import { useState, useEffect, useRef, useMemo } from 'react';
import BiofeedbackChart from '../components/BiofeedbackChart';
import OpacityBiofeedbackChart from '../components/OpacityBiofeedbackChart';
import sleepingAudio from '../assets/sleeping_voice.mp3';

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
		<div className='fixed inset-0 pointer-events-none overflow-hidden bg-slate-950 z-0'>
			<div className='absolute top-[-20%] right-[-10%] w-[800px] h-[800px] bg-indigo-900/20 rounded-full blur-[120px]' />
			<div className='absolute bottom-[-20%] left-[-10%] w-[800px] h-[800px] bg-purple-900/20 rounded-full blur-[120px]' />
			{stars.map(star => (
				<div
					key={star.id}
					className='absolute bg-white rounded-full animate-pulse'
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
	intro: { 
        title: 'Sleep Preparation', 
        instruction: 'Lie down comfortably and close your eyes...', 
        duration: 5000 
    },
	feet: {
		title: 'Feet and Ankles',
		instruction: 'Feel the weight of your feet. Tense them slightly, then relax them completely...',
		duration: 10000,
	},
	legs: {
		title: 'Calves and Thighs',
		instruction: 'Feel how warmth spreads through your legs. Let them sink into the mattress...',
		duration: 10000,
	},
	stomach: {
		title: 'Stomach and Breath',
		instruction: 'Breathe deeply into your stomach. With every exhale, release the tension...',
		duration: 10000,
	},
	shoulders: {
		title: 'Shoulders and Neck',
		instruction: 'Drop your shoulders. Feel the day\'s stress flowing off you onto the floor...',
		duration: 10000,
	},
	face: {
		title: 'Face and Eyes',
		instruction: 'Relax your jaw. Let your eyelids become pleasantly heavy...',
		duration: 10000,
	},
	complete: { 
        title: 'Blissful Calm', 
        instruction: 'You are ready to sleep. Goodnight.', 
        duration: 0 
    },
};

const PHASE_ORDER: SleepPhase[] = ['intro', 'feet', 'legs', 'stomach', 'shoulders', 'face', 'complete'];

export default function SleepPreparationPage() {
	const [isActive, setIsActive] = useState(false);
	const [currentPhaseIndex, setCurrentPhaseIndex] = useState(0);
	const [progress, setProgress] = useState(0);
    
    // --- AUDIO: Stan dla wyciszenia (opcjonalnie) ---
    const [isMuted, setIsMuted] = useState(false);

	const currentPhaseKey = PHASE_ORDER[currentPhaseIndex];
	const currentConfig = SLEEP_SEQUENCE[currentPhaseKey];

	const timerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
	const progressIntervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
    
    // --- AUDIO: Ref do przechowywania obiektu Audio ---
    // Zakładam, że plik jest w folderze public. Jeśli nie, zmień ścieżkę.
    const audioRef = useRef<HTMLAudioElement | null>(null);

    // --- AUDIO: Inicjalizacja ---
    useEffect(() => {
        audioRef.current = new Audio(sleepingAudio); // Ścieżka do pliku audio
        audioRef.current.loop = false; // Czy ma lecieć w pętli? Raczej nie, jeśli to nagranie instruktażowe.
        
        return () => {
            // Cleanup: zatrzymaj audio jak wyjdziemy ze strony
            if (audioRef.current) {
                audioRef.current.pause();
                audioRef.current = null;
            }
        };
    }, []);

    // --- AUDIO: Obsługa Play/Pause w zależności od isActive ---
    useEffect(() => {
        if (audioRef.current) {
            if (isActive && currentPhaseKey !== 'complete') {
                // Próba odtworzenia (przeglądarki mogą blokować autoplay, ale tutaj jest po kliknięciu usera, więc ok)
                audioRef.current.play().catch(e => console.error("Audio play error:", e));
            } else {
                audioRef.current.pause();
            }
        }
    }, [isActive, currentPhaseKey]);

    // --- AUDIO: Obsługa Mute ---
    useEffect(() => {
        if (audioRef.current) {
            audioRef.current.muted = isMuted;
        }
    }, [isMuted]);


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
            
            // --- AUDIO: Reset do początku przy restarcie ---
            if (audioRef.current) {
                audioRef.current.currentTime = 0;
            }
            
			setIsActive(true);
		} else {
			setIsActive(!isActive);
		}
	};

    const toggleMute = () => setIsMuted(!isMuted);

	return (
		<div className='min-h-screen relative font-mono overflow-hidden'>
			<StarBackground />

			<div className='relative z-10 p-6 max-w-2xl mx-auto space-y-8'>

				<div className='flex flex-col items-center justify-center min-h-[500px] w-full bg-slate-900/60 backdrop-blur-md text-slate-100 p-8 rounded-3xl shadow-2xl border border-indigo-500/20 relative'>
                    
                    {/* --- AUDIO: Przycisk Mute w rogu --- */}
                    <button 
                        onClick={toggleMute}
                        className="absolute top-6 right-6 p-2 text-indigo-300 hover:text-white hover:bg-slate-800/50 rounded-full transition-colors z-20"
                    >
                        {isMuted ? <VolumeX size={24} /> : <Volume2 size={24} />}
                    </button>

					<div className='text-center mb-10 z-10 !opacity-100'>
						<div className='flex items-center justify-center gap-3 mb-3 text-indigo-300'>
							<CloudMoon size={32} />
							<span className='uppercase tracking-widest text-xs font-bold'>Night mode</span>
						</div>
						<h2 className='text-3xl md:text-4xl font-bold text-slate-100 mb-2 drop-shadow-lg'>Evening rest</h2>
						<p className='text-slate-300 max-w-md mx-auto'>Technology-aided relaxation</p>
					</div>

					{/* Wizualizacja */}
					<div className='relative mb-12 z-10'>
						<div
							className={`w-64 h-64 rounded-full border-4 flex items-center justify-center relative overflow-hidden
              ${isActive ? 'border-indigo-500/30 bg-slate-900/50' : 'border-slate-700/50 bg-slate-800/40'}
            `}>
							{isActive && currentPhaseKey !== 'complete' && (
								<div
									className='absolute inset-0 bg-indigo-500/40 rounded-full'
									style={{
										transform: `scale(${progress / 80})`,
										transition: 'transform 100ms linear',
									}}
								/>
							)}

							<div
								className={`relative z-10 transition-all duration-700 transform ${
									isActive ? 'scale-110 text-indigo-100' : 'scale-100 text-slate-500'
								}`}>
								{currentPhaseKey === 'complete' ? <CheckCircle2 size={64} /> : <Wind size={64} />}
							</div>
						</div>
					</div>

					<div className='text-center h-32 max-w-lg mx-auto z-10 transition-all duration-500'>
						<h3 className='text-2xl font-bold text-indigo-100 mb-3 animate-fade-in drop-shadow-md'>
							{currentConfig.title}
						</h3>
						<p className='text-lg text-slate-200 leading-relaxed animate-fade-in'>{currentConfig.instruction}</p>
					</div>

					<button
						onClick={handleStartStop}
						className={`
              z-10 flex items-center gap-3 px-10 py-4 rounded-full font-bold text-lg transition-all duration-300
              ${
								isActive
									? 'bg-slate-800/80 hover:bg-slate-700 text-indigo-300 ring-1 ring-indigo-500/40'
									: 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-lg shadow-indigo-900/50'
							}
              hover:scale-105 active:scale-95 backdrop-blur-sm
            `}>
						{isActive ? (
							<>
								<Square size={20} fill='currentColor' /> Pause
							</>
						) : (
							<>
								<Play size={20} fill='currentColor' />
								{currentPhaseKey === 'complete' ? 'Start Over' : 'Begin Relaxation'}
							</>
						)}
					</button>

					<div className='flex gap-2 mt-8 z-10'>
						{PHASE_ORDER.map((phase, idx) => (
							<div
								key={phase}
								className={`w-2 h-2 rounded-full transition-all duration-500 ${
									idx === currentPhaseIndex
										? 'bg-indigo-400 w-6 shadow-[0_0_10px_rgba(129,140,248,0.8)]'
										: idx < currentPhaseIndex
										? 'bg-indigo-800'
										: 'bg-slate-700'
								}`}
							/>
						))}
					</div>
				</div>
			</div>
		</div>
	);
}