const API_URL = 'http://localhost:8000/api';

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
}
