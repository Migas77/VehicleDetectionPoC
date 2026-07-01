import { LandingNav } from '@/features/landing';
import { MapView } from '@/features/map';

export function MapPage() {
    return (
        <div
            className="font-dm"
            style={{
                minHeight: '100vh',
                background: '#F4F3EE',
                color: '#16181B',
            }}
        >
            <LandingNav />
            <main className="pt-20">
                <div
                    style={{
                        maxWidth: '1480px',
                        width: '100%',
                        margin: '0 auto',
                        padding: '22px 24px 28px',
                    }}
                >
                    <MapView />
                </div>
            </main>
        </div>
    );
}
