import React, { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { apiService, type MentalMetrics } from '../services/api';

const CustomTooltip = ({ active, payload, label }: any) => {
	if (active && payload && payload.length) {
		return (
			<div className='bg-gray-900/90 border border-gray-700 p-4 rounded-lg shadow-xl backdrop-blur-sm'>
				<p className='text-gray-400 text-xs mb-2 font-medium'>{label}</p>
				{payload.map((entry: any, index: number) => (
					<div key={index} className='flex items-center gap-2 mb-1'>
						<div className='w-3 h-3 rounded-full' style={{ backgroundColor: entry.color }} />
						<span className='text-gray-200 text-sm capitalize w-20'>{entry.name}:</span>
						<span className='text-white font-bold text-sm'>{entry.value}</span>
					</div>
				))}
			</div>
		);
	}
	return null;
};

const STORAGE_KEY = 'biofeedback_history';

export default function BiofeedbackChart() {
    // 1. INICJALIZACJA Z LOCALSTORAGE
    const [data, setData] = useState<MentalMetrics[]>(() => {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : [];
        } catch (e) {
            console.error("Błąd odczytu z localStorage", e);
            return [];
        }
    });
    
    const [loading, setLoading] = useState(data.length === 0); // Loading tylko jeśli nie mamy starych danych
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        let timeoutId: ReturnType<typeof setTimeout>;

        const fetchData = async () => {
            try {
                const newPoint = await apiService.getMentalMetrics();
                
                // Formatowanie czasu
                newPoint.timestamp = new Date().toLocaleTimeString().slice(0, 8);

                setData(prevData => {
                    const updatedHistory = [...prevData, newPoint];
                    
                    // Przycinanie do 50
                    const finalHistory = updatedHistory.length > 50 
                        ? updatedHistory.slice(-50) 
                        : updatedHistory;

                    // 2. ZAPIS DO LOCALSTORAGE
                    localStorage.setItem(STORAGE_KEY, JSON.stringify(finalHistory));
                    
                    return finalHistory;
                });
                
                setError(null);
            } catch (err) {
                console.error('Error fetching metrics:', err);
            } finally {
                setLoading(false);
                timeoutId = setTimeout(fetchData, 2000);
            }
        };

        fetchData();
        return () => clearTimeout(timeoutId);
    }, []);

	// const getXAxisTicks = () => {
	// 	if (data.length <= 10) return undefined;
	// 	const step = Math.ceil(data.length / 8);
	// 	return data
	// 		.map((_, index) => index)
	// 		.filter((_, index) => index % step === 0)
	// 		.map(index => data[index].timestamp);
	// };

	if (loading && data.length === 0) {
		return (
			<div className='w-full bg-gray-950 p-6 rounded-3xl border border-gray-800 shadow-2xl'>
				<div className='flex justify-center items-center h-[380px]'>
					<p className='text-gray-400'>Loading data...</p>
				</div>
			</div>
		);
	}

	if (error && data.length === 0) {
		return (
			<div className='w-full bg-gray-950 p-6 rounded-3xl border border-gray-800 shadow-2xl'>
				<div className='flex justify-center items-center h-[380px]'>
					<p className='text-red-400'>{error}</p>
				</div>
			</div>
		);
	}

	return (
		<div className={'font-mono w-full bg-gray-950 p-6 rounded-3xl border border-gray-800 shadow-2xl'}>
			<div className='flex justify-between items-center mb-6'>
				<div>
					<h3 className='text-xl font-bold text-white'>Biofeedback Trends</h3>
					<p className='text-gray-500 text-sm ml-10'>Live analysis ({data.length} data points)</p>
				</div>

				<div className='px-3 py-1 bg-gray-900 border border-gray-700 rounded-lg text-xs text-gray-400'>Live</div>
			</div>

			<div className='h-[300px] w-full'>
				<ResponsiveContainer width='100%' height='100%'>
					<AreaChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
						<defs>
							<linearGradient id='colorStress' x1='0' y1='0' x2='0' y2='1'>
								<stop offset='5%' stopColor='#ef4444' stopOpacity={0.4} />
								<stop offset='95%' stopColor='#ef4444' stopOpacity={0} />
							</linearGradient>
							<linearGradient id='colorFocus' x1='0' y1='0' x2='0' y2='1'>
								<stop offset='5%' stopColor='#26C6DA' stopOpacity={0.4} />
								<stop offset='95%' stopColor='#26C6DA' stopOpacity={0} />
							</linearGradient>
							<linearGradient id='colorFatigue' x1='0' y1='0' x2='0' y2='1'>
								<stop offset='5%' stopColor='#a855f7' stopOpacity={0.4} />
								<stop offset='95%' stopColor='#a855f7' stopOpacity={0} />
							</linearGradient>
						</defs>

						<CartesianGrid strokeDasharray='3 3' stroke='#374151' opacity={0.2} vertical={false} />

						<XAxis
							dataKey='timestamp'
							stroke='#9ca3af'
							fontSize={12}
							tickLine={false}
							axisLine={false}
							dy={10}
							interval="preserveStartEnd" // Zawsze pokaż pierwszy i ostatni czas
                   			minTickGap={30}
						/>
						<YAxis stroke='#9ca3af' fontSize={12} tickLine={false} axisLine={false} dx={-10} domain={[0, 100]} />

						<Tooltip
							content={<CustomTooltip />}
							cursor={{ stroke: '#4b5563', strokeWidth: 1, strokeDasharray: '5 5' }}
						/>

						<Legend wrapperStyle={{ paddingTop: '20px' }} iconType='circle' />

						<Area
							type='monotone'
							dataKey='stress_level'
							name='Stress'
							stroke='#ef4444'
							strokeWidth={3}
							fillOpacity={1}
							fill='url(#colorStress)'
							isAnimationActive={false}
							
						/>
						<Area
							type='monotone'
							dataKey='focus_level'
							name='Focus'
							stroke='#26C6DA'
							strokeWidth={3}
							fillOpacity={1}
							fill='url(#colorFocus)'
							isAnimationActive={false}
						/>
						<Area
							type='monotone'
							dataKey='tiredness_level'
							name='Tiredness'
							stroke='#a855f7'
							strokeWidth={3}
							fillOpacity={1}
							fill='url(#colorFatigue)'
							isAnimationActive={false}
						/>
					</AreaChart>
				</ResponsiveContainer>
			</div>
		</div>
	);
}
