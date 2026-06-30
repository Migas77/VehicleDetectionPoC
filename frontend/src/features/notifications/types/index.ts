export type NotificationType = 'crash' | 'alert';
export type AlertChannel = 'sms' | 'v2x';
export type PeriodFilter = 'all' | 'live' | 'past';

export interface NotifFilterState {
    crashes: boolean;
    sms: boolean;
    v2x: boolean;
}

export interface Notification {
    id: string;
    incident_id: string;
    type: NotificationType;
    title: string;
    desc: string;
    loc: string;
    coords: string | null;
    target: string;
    ts: number;
    live: boolean;
    channel?: AlertChannel;
    compactDetails?: {
        notified: string[];
        totalInZone: number;
    };
}

export type ViewMode = 'detailed' | 'compact';

// Backend API types
export type CrashNotificationStatus = 'DETECTED' | 'NOTIFIED';
export type CrashNotificationChannel = 'SMS' | 'DENM';

export interface CrashLocation {
    latitude: number;
    longitude: number;
    road_name: string | null;
}

export interface CrashStatusEvent {
    incident_id: string;
    camera_supi: string;
    status: CrashNotificationStatus;
    channel: CrashNotificationChannel | null;
    recipient: string | null;
    location: CrashLocation | null;
    timestamp: string;
}
