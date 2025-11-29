const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';


export interface PomodoroRequest {
	mental_state: 'focused' | 'stressed' | 'tired' | 'relaxed';
	stress_level: number;
}


export interface PomodoroResponse {
	work_duration: number;
	break_duration: number;
	work_minutes: number;
	break_minutes: number;
	mental_state: string;
	stress_level: number;
	recommendation: string;
}


export interface MentalStatesResponse {
	states: string[];
	descriptions: Record<string, string>;
}

export interface MentalMetrics {
	stress_level: number;
	focus_level: number;
	tiredness_level: number;
}

class ApiService {
	private baseUrl: string;

	constructor() {
		this.baseUrl = API_URL;
	}

	async getMentalMetrics(): Promise<MentalMetrics> {
		const response = await fetch(`${this.baseUrl}/mental-metrics/current`);
		if (!response.ok) {
			throw new Error('Failed to fetch mental metrics');
		}
		return response.json();
	}

	async getMentalMetricsHistory(limit: number = 10): Promise<MentalMetrics[]> {
		const response = await fetch(`${this.baseUrl}/mental-metrics/history?limit=${limit}`);
		if (!response.ok) {
			throw new Error('Failed to fetch mental metrics history');
		}
		return response.json();
	}
}
