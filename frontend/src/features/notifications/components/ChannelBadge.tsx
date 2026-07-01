import type { AlertChannel, NotificationType } from '../types';

export function ChannelBadge({
    type,
    channel,
}: {
    type: NotificationType;
    channel?: AlertChannel;
}) {
    let bg: string, label: string;

    if (type === 'crash') {
        [bg, label] = ['#E5484D', 'CRASH'];
    } else if (channel === 'sms') {
        [bg, label] = ['#2F9E63', 'SMS'];
    } else {
        [bg, label] = ['#142F32', 'V2X'];
    }

    return (
        <span
            style={{
                display: 'inline-block',
                width: '52px',
                textAlign: 'center',
                padding: '3px 0',
                borderRadius: '6px',
                background: bg,
                color: '#FFFFFF',
                fontFamily: "'JetBrains Mono', monospace",
                fontSize: '11px',
                fontWeight: 700,
                letterSpacing: '0.05em',
            }}
        >
            {label}
        </span>
    );
}
