import { create } from 'zustand';

interface MapFiltersState {
    showPedestrians: boolean;
    showVehicles: boolean;
    showCameras: boolean;
    showCrashes: boolean;
    toggleShowPedestrians: () => void;
    toggleShowVehicles: () => void;
    toggleShowCameras: () => void;
    toggleShowCrashes: () => void;
}

export const useMapFiltersStore = create<MapFiltersState>()((set) => ({
    showPedestrians: true,
    showVehicles: true,
    showCameras: true,
    showCrashes: true,
    toggleShowPedestrians: () => set((s) => ({ showPedestrians: !s.showPedestrians })),
    toggleShowVehicles: () => set((s) => ({ showVehicles: !s.showVehicles })),
    toggleShowCameras: () => set((s) => ({ showCameras: !s.showCameras })),
    toggleShowCrashes: () => set((s) => ({ showCrashes: !s.showCrashes })),
}));
