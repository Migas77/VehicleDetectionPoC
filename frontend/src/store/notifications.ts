import { create } from 'zustand';
import type { CrashStatusEvent } from '@/features/notifications';

interface NotificationsState {
    wsEvents: CrashStatusEvent[];
    newCount: number;
    viewingLive: boolean;
    addWsEvent: (event: CrashStatusEvent) => void;
    setViewingLive: (viewing: boolean) => void;
}

export const useNotificationsStore = create<NotificationsState>()((set, get) => ({
    wsEvents: [],
    newCount: 0,
    viewingLive: false,
    addWsEvent: (event) => {
        set((s) => ({
            wsEvents: [event, ...s.wsEvents],
            newCount: s.viewingLive ? s.newCount : s.newCount + 1,
        }));
    },
    setViewingLive: (viewing) => {
        const { newCount } = get();
        set({ viewingLive: viewing, newCount: viewing ? 0 : newCount });
    },
}));
