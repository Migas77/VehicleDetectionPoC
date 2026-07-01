import { cn } from '@/lib/utils';

import { useMapEntities } from '../hooks/useMapEntities';
import { useMapFiltersStore } from '../store/filters';

interface FilterChipProps {
    active: boolean;
    onToggle: () => void;
    dotStyle: React.CSSProperties;
    label: string;
    count: number;
}

function FilterChip({ active, onToggle, dotStyle, label, count }: FilterChipProps) {
    return (
        <button
            type="button"
            onClick={onToggle}
            className={cn(
                'inline-flex h-8 shrink-0 cursor-pointer items-center gap-1.5 whitespace-nowrap rounded-full px-3',
                'text-[12.5px] font-medium antialiased',
                'transition-[color,transform,box-shadow,background-color,border-color] duration-300 ease-[cubic-bezier(0.34,1.56,0.64,1)]',
                'active:translate-y-0 active:scale-[0.98]',
                active
                    ? 'border border-[#16181B] bg-[#16181B] text-[#F4F3EE] shadow-[0_6px_16px_-8px_rgba(15,15,15,0.35)]'
                    : 'border border-[#EAE8E0] bg-white text-[#45473F] hover:-translate-y-px hover:border-neutral-300 hover:shadow-[0_6px_16px_-8px_rgba(15,15,15,0.18)]',
            )}
        >
            <span style={dotStyle} />
            {label} · {count}
        </button>
    );
}

export function MapFilterChips() {
    const { pedestrians, vehicles, cameras, crashMarkers } = useMapEntities();
    const showPedestrians = useMapFiltersStore((s) => s.showPedestrians);
    const showVehicles = useMapFiltersStore((s) => s.showVehicles);
    const showCameras = useMapFiltersStore((s) => s.showCameras);
    const showCrashes = useMapFiltersStore((s) => s.showCrashes);
    const toggleShowPedestrians = useMapFiltersStore((s) => s.toggleShowPedestrians);
    const toggleShowVehicles = useMapFiltersStore((s) => s.toggleShowVehicles);
    const toggleShowCameras = useMapFiltersStore((s) => s.toggleShowCameras);
    const toggleShowCrashes = useMapFiltersStore((s) => s.toggleShowCrashes);

    return (
        <div className="inline-flex flex-wrap items-center gap-1.5">
            <FilterChip
                active={showPedestrians}
                onToggle={toggleShowPedestrians}
                dotStyle={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#3E63DD',
                    flexShrink: 0,
                }}
                label="Pedestrians"
                count={pedestrians.length}
            />
            <FilterChip
                active={showVehicles}
                onToggle={toggleShowVehicles}
                dotStyle={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '3px',
                    background: '#2F9E63',
                    flexShrink: 0,
                }}
                label="Vehicles"
                count={vehicles.length}
            />
            <FilterChip
                active={showCameras}
                onToggle={toggleShowCameras}
                dotStyle={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '2px',
                    background: '#F5A524',
                    transform: 'rotate(45deg)',
                    flexShrink: 0,
                }}
                label="Cameras"
                count={cameras.length}
            />
            <FilterChip
                active={showCrashes}
                onToggle={toggleShowCrashes}
                dotStyle={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    background: '#E5484D',
                    flexShrink: 0,
                }}
                label="Crashes"
                count={crashMarkers.length}
            />
        </div>
    );
}
