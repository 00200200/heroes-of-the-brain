import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import stressRedGif from '../assets/windy-tree.gif';
import solvroCat from '../assets/solvro_cat.gif';
import BiofeedbackChart from '../components/BiofeedbackChart';

export default function HomePage() {
	const [metrics, setMetrics] = useState<{
		stress_level: number;
		focus_level: number;
		tiredness_level: number;
	} | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		const fetchMetrics = async () => {
			try {
				setLoading(true);
				const data = await apiService.getMentalMetrics();
				setMetrics(data);
				setError(null);
			} catch (err) {
				console.error('Failed to fetch metrics:', err);
				setError("Can't fetch data check backend");
			} finally {
				setLoading(false);
			}
		};

		fetchMetrics();
		const interval = setInterval(fetchMetrics, 5000);
		return () => clearInterval(interval);
	}, []);

	const modules = [
		{
			id: 'stress',
			title: 'Redukcja Stresu',
			description: 'Techniki relaksacyjne współpracujące z twoim umysłem',
			color: '#3b82f6',
			path: '/stress',
			status: 'active',
			background: stressRedGif,
		},

		{
			id: 'pomodoro',
			title: 'Pomodoro',
			description: 'Spersonalizowane sesje pracy oparte na twoim stanie umysłu',
			color: '#10b981',
			path: '/pomodoro',
			status: 'active',
		},

		{
			id: 'concentration',
			title: 'Trening Koncentracji',
			description: 'Ćwiczenia poprawiające twoją zdolność skupienia uwagi',
			color: '#f59e0b',
			path: '/concentration',
			status: 'active'
		}
	];

	return (
		<div>
			<div className='mb-12'>
				<div className='flex items-center gap-3 sm:gap-4 justify-center mb-6'>
					<h3 className='text-2xl sm:text-3xl md:text-4xl text-center font-medium text-gray-200'>
						Stan mentalny
					</h3>
					<img src={solvroCat} alt='Solvro Cat' className='w-10 h-10 sm:w-12 sm:h-12 md:w-16 md:h-16 object-contain' />
				</div>

				{error && (
					<div className='bg-red-950/30 border border-red-900/50 text-red-400 px-4 py-3 rounded-lg mb-6 text-sm'>
						{error}
					</div>
				)}
				<BiofeedbackChart />
				{loading && !metrics ? (
					<div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
						{[1, 2, 3].map(i => (
							<div key={i} className='bg-gray-900/40 rounded-xl p-5 border border-gray-800 animate-pulse'>
								<div className='h-4 bg-gray-800 rounded mb-3 w-24'></div>
								<div className='h-8 bg-gray-800 rounded mb-3'></div>
								<div className='h-2 bg-gray-800 rounded'></div>
							</div>
						))}
					</div>
				) : metrics ? (
					<div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
						<div className='bg-gray-900/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 hover:border-red-500/40 transition-all'>
							<div className='flex items-center justify-between mb-3'>
								<span className='text-base font-medium text-gray-400 uppercase tracking-wider'>Stres</span>
								<span className='text-3xl font-bold text-red-400'>{metrics.stress_level}%</span>
							</div>
							<div className='w-full bg-gray-800 rounded-full h-2 overflow-hidden'>
								<div
									className='bg-gradient-to-r from-red-500 to-red-400 h-2 transition-all duration-700'
									style={{ width: `${metrics.stress_level}%` }}
								/>
							</div>
						</div>

						<div className='bg-gray-900/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 hover:border-cyan-500/40 transition-all'>
							<div className='flex items-center justify-between mb-3'>
								<span className='text-base font-medium text-gray-400 uppercase tracking-wider'>Focus</span>
								<span className='text-3xl font-bold text-cyan-400'>{metrics.focus_level}%</span>
							</div>
							<div className='w-full bg-gray-800 rounded-full h-2 overflow-hidden'>
								<div
									className='bg-gradient-to-r from-cyan-500 to-cyan-400 h-2 transition-all duration-700'
									style={{ width: `${metrics.focus_level}%` }}
								/>
							</div>
						</div>

						<div className='bg-gray-900/40 backdrop-blur-sm rounded-xl p-6 border border-gray-800 hover:border-purple-500/40 transition-all'>
							<div className='flex items-center justify-between mb-3'>
								<span className='text-base font-medium text-gray-400 uppercase tracking-wider'>Zmęczenie</span>
								<span className='text-3xl font-bold text-purple-400'>{metrics.tiredness_level}%</span>
							</div>
							<div className='w-full bg-gray-800 rounded-full h-2 overflow-hidden'>
								<div
									className='bg-gradient-to-r from-purple-500 to-purple-400 h-2 transition-all duration-700'
									style={{ width: `${metrics.tiredness_level}%` }}
								/>
							</div>
						</div>
					</div>
				) : null}
			</div>

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
							} `}>
						{/* --- WARSTWA TŁA (GIF) --- */}
						{module.background && (
							<div className='absolute inset-0 z-0'>
								<img
									src={module.background}
									alt='Background animation'
									className='w-full h-full object-cover opacity-90 group-hover:opacity-30 transition-opacity duration-1000'
								/>
								{/* Gradient przyciemniający, żeby tekst był czytelny na GIFie */}
								<div className='absolute inset-0 bg-gradient-to-t from-gray-900 via-gray-900/80 to-gray-900/40' />
							</div>
						)}

						{/* --- TREŚĆ (musi mieć z-10 żeby być nad GIFem) --- */}
						<div className='relative z-10'>
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
}
