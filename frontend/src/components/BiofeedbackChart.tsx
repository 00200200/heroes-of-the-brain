import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';

// Przykładowe dane (w przyszłości podmienisz je danymi z API)
// Skala 3 minut, próbkowanie np. co 30 sekund
const data = [
  { time: '00:00', stress: 30, focus: 50, fatigue: 20 },
  { time: '00:30', stress: 45, focus: 55, fatigue: 25 },
  { time: '01:00', stress: 60, focus: 40, fatigue: 30 },
  { time: '01:30', stress: 85, focus: 30, fatigue: 45 }, // Pik stresu
  { time: '02:00', stress: 50, focus: 60, fatigue: 35 },
  { time: '02:30', stress: 35, focus: 80, fatigue: 30 },
  { time: '03:00', stress: 20, focus: 90, fatigue: 25 },
];

// Customowy Tooltip, żeby wyglądał jak na Twoim screenie
const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-gray-900/90 border border-gray-700 p-4 rounded-lg shadow-xl backdrop-blur-sm">
        <p className="text-gray-400 text-xs mb-2 font-medium">{label}</p>
        {payload.map((entry: any, index: number) => (
          <div key={index} className="flex items-center gap-2 mb-1">
            <div 
              className="w-3 h-3 rounded-full" 
              style={{ backgroundColor: entry.color }}
            />
            <span className="text-gray-200 text-sm capitalize w-20">
              {entry.name}:
            </span>
            <span className="text-white font-bold text-sm">
              {entry.value}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function BiofeedbackChart() {
  return (
    <div className="w-full bg-gray-950 p-6 rounded-3xl border border-gray-800 shadow-2xl">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h3 className="text-xl font-bold text-white">Trendy Biofeedbacku</h3>
          <p className="text-gray-500 text-sm">Analiza w czasie rzeczywistym (ostatnie 3 min)</p>
        </div>
        
        {/* Przykładowy selector czasu */}
        <div className="px-3 py-1 bg-gray-900 border border-gray-700 rounded-lg text-xs text-gray-400">
          Live
        </div>
      </div>

      <div className="h-[300px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            {/* Definicje gradientów - klucz do uzyskania efektu "glow" */}
            <defs>
              <linearGradient id="colorStress" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ef4444" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorFocus" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorFatigue" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#a855f7" stopOpacity={0.4}/>
                <stop offset="95%" stopColor="#a855f7" stopOpacity={0}/>
              </linearGradient>
            </defs>

            <CartesianGrid strokeDasharray="3 3" stroke="#374151" opacity={0.2} vertical={false} />
            
            <XAxis 
              dataKey="time" 
              stroke="#9ca3af" 
              fontSize={12} 
              tickLine={false}
              axisLine={false}
              dy={10}
            />
            <YAxis 
              stroke="#9ca3af" 
              fontSize={12} 
              tickLine={false}
              axisLine={false}
              dx={-10}
            />
            
            <Tooltip content={<CustomTooltip />} cursor={{ stroke: '#4b5563', strokeWidth: 1, strokeDasharray: '5 5' }} />
            
            <Legend 
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="circle"
            />

            {/* Serie danych - monotone daje efekt gładkiej fali */}
            <Area 
              type="monotone" 
              dataKey="stress" 
              name="Stres"
              stroke="#ef4444" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorStress)" 
            />
            <Area 
              type="monotone" 
              dataKey="focus" 
              name="Skupienie"
              stroke="#3b82f6" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorFocus)" 
            />
            <Area 
              type="monotone" 
              dataKey="fatigue" 
              name="Zmęczenie"
              stroke="#a855f7" 
              strokeWidth={3}
              fillOpacity={1} 
              fill="url(#colorFatigue)" 
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}