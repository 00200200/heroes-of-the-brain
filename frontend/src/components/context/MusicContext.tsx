import React, { createContext, useContext, useState, useEffect, useRef } from 'react';

import focusTrack from '../../assets/music/Subwoofer_Lullaby.mp3';
import relaxTrack from '../../assets/music/Subwoofer_Lullaby.mp3';
import energyTrack from '../../assets/music/Subwoofer_Lullaby.mp3';
import deepRelaxTrack from '../../assets/music/Subwoofer_Lullaby.mp3';

type MusicType = 'focus' | 'relax' | 'energy' | 'deep_relax' | 'none';

// Mapa typów muzyki do plików
const TRACKS: Record<string, string> = {
  focus: focusTrack,
  relax: relaxTrack,
  energy: energyTrack,
  deep_relax: deepRelaxTrack,
};

interface MusicContextType {
  isPlaying: boolean;
  isMuted: boolean;
  currentType: MusicType;
  toggleMute: () => void;
  fetchAndPlayMusic: () => Promise<void>; // Funkcja do ręcznego wywołania pobierania
}

const MusicContext = createContext<MusicContextType | undefined>(undefined);

export const MusicProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isMuted, setIsMuted] = useState(false); // Domyślnie włączony dźwięk
  const [currentType, setCurrentType] = useState<MusicType>('none');
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Inicjalizacja obiektu Audio tylko raz
  useEffect(() => {
    audioRef.current = new Audio();
    audioRef.current.loop = true; // Zapętlanie
    audioRef.current.volume = 0.5; // 50% głośności
    
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Reakcja na zmianę wyciszenia
  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.muted = isMuted;
    }
  }, [isMuted]);

  const fetchAndPlayMusic = async () => {
    try {
      const types: MusicType[] = ['focus', 'relax', 'energy', 'deep_relax'];
      const currentIndex = types.indexOf(currentType);
      const nextIndex = (currentIndex + 1) % types.length;
      
      const nextType = types[nextIndex];
      
      console.log(`Przełączono muzykę na: ${nextType}`);
      playTrack(nextType);

    } catch (error) {
      console.error("Błąd zmiany muzyki:", error);
    }
  };

  // Funkcja zmieniająca utwór
  const playTrack = (type: MusicType) => {
    if (!audioRef.current) return;
    if (currentType === type) return; // Nie przerywaj jeśli to samo

    setCurrentType(type);
    
    const src = TRACKS[type];
    if (src) {
      audioRef.current.src = src;
      // Play musi być obsłużony ostrożnie (przeglądarki blokują autoplay bez interakcji)
      audioRef.current.play().catch(e => console.warn("Autoplay zablokowany:", e));
    }
  };
  
  // Pobierz muzykę automatycznie przy starcie aplikacji (opcjonalne)
  useEffect(() => {
      // Opcjonalnie: Odkomentuj to, jeśli chcesz próbować grać od razu po wejściu
      // fetchAndPlayMusic(); 
  }, []);

  const toggleMute = () => setIsMuted(prev => !prev);

  return (
    <MusicContext.Provider value={{ 
      isPlaying: currentType !== 'none', 
      isMuted, 
      currentType, 
      toggleMute,
      fetchAndPlayMusic 
    }}>
      {children}
    </MusicContext.Provider>
  );
};

export const useMusic = () => {
  const context = useContext(MusicContext);
  if(!context) {
    throw new Error("useMusic must be used within a MusicProvider");
  }
  return context;
};