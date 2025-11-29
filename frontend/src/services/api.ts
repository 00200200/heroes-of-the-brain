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
	timestamp: string;
}


export interface MusicRecommendationResponse {
	music_type: 'focus' | 'relax' | 'energy' | 'deep_relax';
}
class ApiService {
	private baseUrl: string;

	constructor() {
		this.baseUrl = API_URL;
	}

	async calculatePomodoro(request: PomodoroRequest): Promise<PomodoroResponse> {
		try {
			const url = `${this.baseUrl}/pomodoro/calculate?mental_state=${request.mental_state}&stress_level=${request.stress_level}`;

			const response = await fetch(url, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
			});

			if (!response.ok) {
				const error = await response.json().catch(() => ({ detail: response.statusText }));
				throw new Error(error.detail || 'Failed to calculate pomodoro');
			}

			return await response.json();
		} catch (error) {
			console.error('Failed to calculate pomodoro:', error);
			throw error;
		}
	}

	async getMentalStates(): Promise<MentalStatesResponse> {
		try {
			const response = await fetch(`${this.baseUrl}/pomodoro/states`);

			if (!response.ok) {
				throw new Error(`API Error: ${response.statusText}`);
			}

			return await response.json();
		} catch (error) {
			console.error('Failed to fetch mental states:', error);
			throw error;
		}
	}
	async getMentalMetrics(): Promise<MentalMetrics> {
		const response = await fetch(`${this.baseUrl}/metrics/current`);
		if (!response.ok) {
			throw new Error('Failed to fetch mental metrics');
		}
		return response.json();
	}

	async getMusicRecommendation(): Promise<MusicRecommendationResponse> {
		const response = await fetch(`${this.baseUrl}/metrics/music`);
		if (!response.ok) {
			throw new Error('Failed to set music');
		}
		return response.json();
	}

	async getMetricsHistory(limit: number = 20): Promise<MentalMetrics[]> {
		const response = await fetch(`${this.baseUrl}/metrics/history?limit=${limit}`);
		if (!response.ok) {
			throw new Error('Failed to fetch metrics history');
		}
		return response.json();
	}
}

export const apiService = new ApiService();
