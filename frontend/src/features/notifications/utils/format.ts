const MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

export function fmtRel(ts: number): string {
    const elapsed = Math.floor((Date.now() - ts) / 1000);
    if (elapsed < 5) return 'just now';
    if (elapsed < 60) return `${elapsed}s ago`;
    const mn = Math.floor(elapsed / 60);
    if (mn < 60) return `${mn}m ago`;
    const h = Math.floor(mn / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
}

export function fmtAbs(ts: number): string {
    const d = new Date(ts);
    const mon = MONTHS[d.getMonth()];
    const day = d.getDate();
    const h = String(d.getHours()).padStart(2, '0');
    const m = String(d.getMinutes()).padStart(2, '0');
    const s = String(d.getSeconds()).padStart(2, '0');
    return `${mon} ${day}, ${h}:${m}:${s}`;
}
