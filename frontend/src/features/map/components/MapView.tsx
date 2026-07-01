import { MapContainer, Marker, Popup, TileLayer, useMap } from 'react-leaflet';
import { divIcon } from 'leaflet';
import { Minus, Plus } from 'lucide-react';

import { useClock } from '@/hooks/useClock';
import { cn } from '@/lib/utils';

import { useMapEntities } from '../hooks/useMapEntities';
import { useMapFiltersStore } from '../store/filters';
import type { EntityType, TrackedEntity } from '../types';
import { MapFilterChips } from './MapFilterChips';

const AVEIRO: [number, number] = [40.6405, -8.6538];

const PEDESTRIAN_ICON = divIcon({
    className: '',
    iconSize: [14, 14],
    iconAnchor: [7, 7],
    html: '<div style="width:14px;height:14px;border-radius:50%;background:#3E63DD;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>',
});

const VEHICLE_ICON = divIcon({
    className: '',
    iconSize: [16, 16],
    iconAnchor: [8, 8],
    html: '<div style="width:14px;height:14px;border-radius:4px;background:#2F9E63;border:2px solid #fff;box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>',
});

const CAMERA_ICON = divIcon({
    className: '',
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    html: '<div style="width:13px;height:13px;background:#F5A524;border:2px solid #fff;transform:rotate(45deg);box-shadow:0 1px 4px rgba(0,0,0,0.3)"></div>',
});

const CRASH_ICON = divIcon({
    className: '',
    iconSize: [28, 28],
    iconAnchor: [14, 14],
    html: '<div style="position:relative;width:28px;height:28px"><div style="position:absolute;inset:0;border-radius:50%;border:2px solid #E5484D;animation:vg-pulse 1.6s infinite"></div><div style="position:absolute;left:7px;top:7px;width:14px;height:14px;border-radius:50%;background:#E5484D;border:2px solid #fff"></div></div>',
});

function iconForType(type: EntityType) {
    if (type === 'camera') return CAMERA_ICON;
    if (type === 'car') return VEHICLE_ICON;
    return PEDESTRIAN_ICON;
}

const TYPE_LABELS: Record<EntityType, string> = {
    pedestrian: 'Pedestrian',
    car: 'Vehicle',
    camera: 'Camera',
};

const TYPE_COLORS: Record<EntityType, string> = {
    pedestrian: '#3E63DD',
    car: '#2F9E63',
    camera: '#F5A524',
};

interface EntityPopupProps {
    entity: TrackedEntity;
}

function EntityPopup({ entity }: EntityPopupProps) {
    const color = TYPE_COLORS[entity.type];
    return (
        <div
            style={{
                fontFamily: "'DM Sans', system-ui, sans-serif",
                minWidth: '180px',
                padding: '2px 0',
            }}
        >
            <div
                style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    marginBottom: '10px',
                    padding: '3px 8px',
                    borderRadius: '6px',
                    background: `${color}18`,
                    border: `1px solid ${color}40`,
                }}
            >
                <span
                    style={{
                        width: '7px',
                        height: '7px',
                        borderRadius:
                            entity.type === 'camera'
                                ? '2px'
                                : entity.type === 'car'
                                  ? '2px'
                                  : '50%',
                        background: color,
                        transform: entity.type === 'camera' ? 'rotate(45deg)' : undefined,
                        flexShrink: 0,
                    }}
                />
                <span
                    style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '10px',
                        fontWeight: 600,
                        letterSpacing: '0.08em',
                        color,
                    }}
                >
                    {TYPE_LABELS[entity.type].toUpperCase()}
                </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                <div>
                    <div
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: '9.5px',
                            letterSpacing: '0.1em',
                            color: '#777C90',
                            marginBottom: '1px',
                        }}
                    >
                        SUPI
                    </div>
                    <div
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: '12px',
                            color: '#16181B',
                            fontWeight: 500,
                            wordBreak: 'break-all',
                        }}
                    >
                        {entity.supi}
                    </div>
                </div>

                <div>
                    <div
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: '9.5px',
                            letterSpacing: '0.1em',
                            color: '#777C90',
                            marginBottom: '1px',
                        }}
                    >
                        MSISDN
                    </div>
                    <div
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: '12px',
                            color: entity.msisdn ? '#16181B' : '#9A9C95',
                            fontWeight: entity.msisdn ? 500 : 400,
                        }}
                    >
                        {entity.msisdn ?? 'N/A'}
                    </div>
                </div>

                {entity.name && (
                    <div>
                        <div
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: '9.5px',
                                letterSpacing: '0.1em',
                                color: '#777C90',
                                marginBottom: '1px',
                            }}
                        >
                            NAME
                        </div>
                        <div
                            style={{
                                fontFamily: "'JetBrains Mono', monospace",
                                fontSize: '12px',
                                color: '#16181B',
                                fontWeight: 500,
                            }}
                        >
                            {entity.name}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

function ZoomControls() {
    const map = useMap();
    return (
        <div
            className={cn(
                'absolute z-[1000] bottom-3.5 right-3.5 flex flex-col overflow-hidden rounded-xl',
                'border border-[#E6E4DC] bg-white/92 shadow-[0_1px_4px_rgba(0,0,0,0.08)] backdrop-blur-md',
            )}
        >
            <button
                type="button"
                onClick={() => map.zoomIn()}
                aria-label="Zoom in"
                className="flex h-9 w-9 cursor-pointer items-center justify-center text-[#45473F] transition-colors hover:bg-black/5"
            >
                <Plus size={15} strokeWidth={2} />
            </button>
            <div className="h-px w-full bg-[#E6E4DC]" />
            <button
                type="button"
                onClick={() => map.zoomOut()}
                aria-label="Zoom out"
                className="flex h-9 w-9 cursor-pointer items-center justify-center text-[#45473F] transition-colors hover:bg-black/5"
            >
                <Minus size={15} strokeWidth={2} />
            </button>
        </div>
    );
}

function MapHeader() {
    const clock = useClock();

    return (
        <div
            style={{
                display: 'flex',
                alignItems: 'flex-end',
                justifyContent: 'space-between',
                marginBottom: '16px',
                flexWrap: 'wrap',
                gap: '14px',
            }}
        >
            <div>
                <h2
                    style={{
                        fontFamily: "'Space Grotesk', system-ui, sans-serif",
                        fontWeight: 700,
                        fontSize: '26px',
                        letterSpacing: '-0.02em',
                        margin: 0,
                    }}
                >
                    City map
                </h2>
                <div
                    style={{
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '12px',
                        color: '#8A8C86',
                        marginTop: '4px',
                    }}
                >
                    REAL-TIME POSITIONS · AVEIRO · {clock}
                </div>
            </div>

            <MapFilterChips />
        </div>
    );
}

interface MapViewProps {
    showHeader?: boolean;
}

export function MapView({ showHeader = true }: MapViewProps) {
    const { visibleEntities, crashMarkers } = useMapEntities();
    const showCrashes = useMapFiltersStore((s) => s.showCrashes);

    return (
        <div>
            {showHeader && <MapHeader />}

            <div
                style={{
                    background: '#FFFFFF',
                    border: '1px solid #EAE8E0',
                    borderRadius: '18px',
                    overflow: 'hidden',
                    position: 'relative',
                    height: 'calc(100vh - 210px)',
                    minHeight: '480px',
                }}
            >
                <div
                    style={{
                        position: 'absolute',
                        zIndex: 1000,
                        top: '14px',
                        left: '14px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                        padding: '8px 13px',
                        borderRadius: '10px',
                        background: 'rgba(255,255,255,0.92)',
                        backdropFilter: 'blur(6px)',
                        border: '1px solid #E6E4DC',
                        fontFamily: "'JetBrains Mono', monospace",
                        fontSize: '11.5px',
                        color: '#45473F',
                        pointerEvents: 'none',
                    }}
                >
                    LIVE MAP
                </div>

                <div
                    style={{
                        position: 'absolute',
                        zIndex: 1000,
                        bottom: '14px',
                        left: '14px',
                        display: 'flex',
                        gap: '8px',
                        flexWrap: 'wrap',
                        pointerEvents: 'none',
                    }}
                >
                    {(
                        [
                            {
                                label: 'Pedestrians',
                                dot: { borderRadius: '50%', background: '#3E63DD' },
                            },
                            {
                                label: 'Vehicles',
                                dot: { borderRadius: '3px', background: '#2F9E63' },
                            },
                            {
                                label: 'Cameras',
                                dot: {
                                    borderRadius: '2px',
                                    background: '#F5A524',
                                    transform: 'rotate(45deg)',
                                },
                            },
                            {
                                label: 'Crashes',
                                dot: { borderRadius: '50%', background: '#E5484D' },
                            },
                        ] as const
                    ).map(({ label, dot }) => (
                        <div
                            key={label}
                            className={cn(
                                'flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs',
                                'border border-[#E6E4DC]',
                            )}
                            style={{
                                background: 'rgba(255,255,255,0.92)',
                                backdropFilter: 'blur(6px)',
                                color: '#45473F',
                            }}
                        >
                            <span
                                style={{
                                    width: '10px',
                                    height: '10px',
                                    flexShrink: 0,
                                    ...dot,
                                }}
                            />
                            {label}
                        </div>
                    ))}
                </div>

                <MapContainer
                    center={AVEIRO}
                    zoom={15}
                    zoomControl={false}
                    attributionControl={false}
                    style={{ position: 'absolute', inset: 0, height: '100%', width: '100%' }}
                >
                    <TileLayer
                        url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
                        maxZoom={19}
                        subdomains="abcd"
                    />

                    {visibleEntities.map((entity) => (
                        <Marker
                            key={entity.supi}
                            position={[entity.lat, entity.lng]}
                            icon={iconForType(entity.type)}
                        >
                            <Popup minWidth={200} maxWidth={260} closeButton>
                                <EntityPopup entity={entity} />
                            </Popup>
                        </Marker>
                    ))}

                    {showCrashes &&
                        crashMarkers.map((c) => (
                            <Marker key={c.id} position={[c.lat, c.lng]} icon={CRASH_ICON} />
                        ))}

                    <ZoomControls />
                </MapContainer>
            </div>
        </div>
    );
}
