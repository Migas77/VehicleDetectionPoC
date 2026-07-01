import { useClock } from '@/hooks/useClock';
import { MapFilterChips, MapView } from '@/features/map';
import { AlertStreamPanel } from './AlertStreamPanel';
import { CameraFeedPanel } from './CameraFeedPanel';

export function DashboardView() {
    const clock = useClock();

    return (
        <div>
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
                        Live operations
                    </h2>
                    <div
                        style={{
                            fontFamily: "'JetBrains Mono', monospace",
                            fontSize: '12px',
                            color: '#8A8C86',
                            marginTop: '4px',
                        }}
                    >
                        AVEIRO · {clock}
                    </div>
                </div>

                <MapFilterChips />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-[1.55fr_1fr] gap-4 items-stretch">
                <MapView showHeader={false} />
                <div className="flex flex-col gap-4 min-h-0">
                    <CameraFeedPanel />
                    <AlertStreamPanel />
                </div>
            </div>
        </div>
    );
}
