import type { ReverseResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';
const API_TIMEOUT_MS = Number(import.meta.env.VITE_API_TIMEOUT_MS ?? 20000);

export class ApiError extends Error {
  constructor(message: string, public status?: number) {
    super(message);
  }
}

export async function reversePrompt(outputText: string, signal?: AbortSignal): Promise<ReverseResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  const mergedSignal = signal ?? controller.signal;

  try {
    const response = await fetch(`${API_BASE_URL}/reverse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ output_text: outputText }),
      signal: mergedSignal,
    });

    if (!response.ok) {
      const payload = await response.json().catch(() => ({}));
      throw new ApiError(payload.detail ?? 'Request failed', response.status);
    }

    return (await response.json()) as ReverseResponse;
  } catch (error) {
    if (error instanceof DOMException && error.name === 'AbortError') {
      throw new ApiError('Request timed out. Please try again.');
    }
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError('Network error. Please check your connection and retry.');
  } finally {
    clearTimeout(timeout);
  }
}
