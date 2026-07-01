export interface AreaCenter {
    latitude: number;
    longitude: number;
}

export interface CircleArea {
    areaType: 'CIRCLE';
    center: AreaCenter;
    radius: number;
}

export interface PolygonArea {
    areaType: 'POLYGON';
    boundary: AreaCenter[];
}

export type EntityArea = CircleArea | PolygonArea;

export interface EntityLocation {
    lastLocationTime: string;
    area: EntityArea;
}

export type EntityType = 'car' | 'camera' | 'pedestrian';

export interface UEInfo {
    supi: string;
    msisdn: string | null;
    name: string | null;
}

export interface UELocation {
    ue: UEInfo;
    type: EntityType;
    location: EntityLocation;
}

export interface TrackedEntity {
    supi: string;
    msisdn: string | null;
    name: string | null;
    lat: number;
    lng: number;
    type: EntityType;
    lastSeen: number;
}
