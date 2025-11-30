import { Volume2, VolumeX, Music } from 'lucide-react';
import { useMusic } from './MusicContext';
import { apiService } from '../../services/api';

export default function MusicPlayer() {
  const { isMuted, currentType, toggleMute, fetchAndPlayMusic } = useMusic();

  // Mapowanie nazw typów na ładne etykiety
  const labels: Record<string, string> = {
    focus: "Focus",
    relax: "Relax",
    energy: "Energy",
    deep_relax: "Deep Relax",
    none: "Silence"
  };
  
  // Kolory dla różnych trybów
  const colors: Record<string, string> = {
    focus: "bg-blue-500 shadow-blue-500/50",
    relax: "bg-green-500 shadow-green-500/50",
    energy: "bg-yellow-500 shadow-yellow-500/50",
    deep_relax: "bg-purple-600 shadow-purple-500/50",
    none: "bg-gray-700"
  };

  return (
    <div className="fixed bottom-6 right-6 flex flex-col items-end z-50 gap-2">
      
      {/* Etykieta (pokazuje się tylko gdy coś gra) */}
      {currentType !== 'none' && (
        <div className="bg-gray-900/80 backdrop-blur text-white text-xs py-1 px-3 rounded-full mb-1 animate-fade-in">
          Now playing: {labels[currentType]}
        </div>
      )}

      <div className="flex items-center gap-2">
        {/* Przycisk symulujący API (tylko do testów, potem możesz go ukryć/usunąć) */}
        <button 
            onClick={fetchAndPlayMusic}
            className="bg-white/10 hover:bg-white/20 p-3 rounded-full backdrop-blur transition-all text-white"
            title="Zmień muzykę (API)"
        >
            <Music size={20} />
        </button>

        {/* Główny przycisk Mute/Unmute */}
        <button
          onClick={toggleMute}
          className={`
            p-4 rounded-full text-white shadow-lg transition-all hover:scale-110 active:scale-95
            flex items-center justify-center
            ${colors[currentType] || colors.none}
            ${isMuted ? 'opacity-75 grayscale' : 'opacity-100'}
          `}
        >
          {isMuted ? <VolumeX size={24} /> : <Volume2 size={24} />}
        </button>
      </div>
    </div>
  );
}