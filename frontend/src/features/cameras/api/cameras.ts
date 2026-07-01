import { API_BASE_URL } from '@/config';
import type { CameraInfo } from '../types';

export async function fetchCameras(): Promise<CameraInfo[]> {
    const res = await fetch(`${API_BASE_URL}/cameras`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<CameraInfo[]>;
}

export async function fetchInferenceServerUrl(): Promise<string> {
    const res = await fetch(`${API_BASE_URL}/config/inference-server`);
    if (!res.ok) throw new Error(`HTTP ${res.status}: ${res.statusText}`);
    return res.json() as Promise<string>;
}
