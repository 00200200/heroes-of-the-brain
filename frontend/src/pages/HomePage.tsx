import { useState, useEffect } from 'react';
import { apiService } from '../services/api';

export default function HomePage() {
  const modules = [
	{
		id: 'stress',
		title: 'Redukcja Stresu',
		description: 'Techniki relaksacyjne współpracujące z twoim umysłem',
		color: '#3b82f6',
		path: '/stress',
		status: 'active',
	},
	{
		id: 'pomodoro',
		title: 'Pomodoro Timer',
		description: 'Technika zarządzania czasem dla maksymalnej produktywności',
		color: '#0ea5e9',
		path: '/pomodoro',
		status: 'active',
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
              bg-gray-900/40 backdrop-blur-sm rounded-2xl p-8 border transition-all duration-300 relative overflow-hidden
              ${
								module.status === 'active'
									? 'cursor-pointer hover:-translate-y-1 border-gray-700 hover:border-cyan-500/50'
									: 'cursor-not-allowed opacity-40 border-gray-800'
							} `}>
						{module.status !== 'active' && (
							<div className='absolute top-4 right-4 px-3 py-1 bg-gray-800/80 rounded-full text-xs font-medium text-gray-500'></div>
						)}
						<h3 className='text-2xl font-bold mb-2 text-gray-200'>{module.title}</h3>
						<p className='text-sm text-gray-400 leading-relaxed'>{module.description}</p>
						{module.status === 'active' && (
							<div className='mt-5 p-3 rounded-lg text-center font-semibold text-sm bg-cyan-500/10 text-cyan-400 hover:bg-cyan-500/20 transition-colors'>
								Uruchom
							</div>
						)}
					</div>
				))}
			</div>
		</div>
  );
};