import { createFileRoute } from '@tanstack/react-router';

import { MapPage } from '@/pages/map';

export const Route = createFileRoute('/map')({
    component: MapPage,
});
