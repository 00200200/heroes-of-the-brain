import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import stressRedGif from '../assets/windy-tree.gif';

export default function HomePage() {
  const modules = [
	{
		id: 'stress',
		title: 'Redukcja Stresu',
		description: 'Techniki relaksacyjne współpracujące z twoim umysłem',
		color: '#3b82f6',
		path: '/stress',
		status: 'active',
		background: stressRedGif
	}

  ];

   return (
    <div>   
      <div className='grid grid-cols-1 md:grid-cols-2 gap-6 mb-10'>
        {modules.map(module => (
          <div
            key={module.id}
            onClick={() => {
              if (module.status === 'active') {
                window.location.hash = module.path;
              }
            }}
            className={`
              relative overflow-hidden rounded-2xl p-8 border transition-all duration-300 group
              ${
                module.status === 'active'
                  ? 'cursor-pointer hover:-translate-y-1 border-gray-700 hover:border-cyan-500/50'
                  : 'cursor-not-allowed opacity-40 border-gray-800'
              } `}
          >
            {/* --- WARSTWA TŁA (GIF) --- */}
            {module.background && (
              <div className="absolute inset-0 z-0">
                <img 
                  src={module.background} 
                  alt="Background animation" 
                  className="w-full h-full object-cover opacity-90 group-hover:opacity-30 transition-opacity duration-1000"
                />
                {/* Gradient przyciemniający, żeby tekst był czytelny na GIFie */}
                <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/80 to-gray-900/40" />
              </div>
            )}

            {/* --- TREŚĆ (musi mieć z-10 żeby być nad GIFem) --- */}
            <div className="relative z-10">
              {module.status !== 'active' && (
                <div className='absolute top-4 right-4 px-3 py-1 bg-gray-800/80 rounded-full text-xs font-medium text-gray-500'></div>
              )}
              
              <h3 className='text-2xl font-bold mb-2 text-gray-200 drop-shadow-md'>{module.title}</h3>
              <p className='text-sm text-gray-300 leading-relaxed drop-shadow-md font-medium'>{module.description}</p>
              
              {module.status === 'active' && (
                <div className='mt-5 p-3 rounded-lg text-center font-semibold text-sm bg-cyan-500/20 text-cyan-300 backdrop-blur-sm border border-cyan-500/20 hover:bg-cyan-500/30 transition-colors'>
                  Uruchom
                </div>
              )}
            </div>

          </div>
        ))}
      </div>
    </div>
  );
};