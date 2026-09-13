/** Shared formatting helpers. */

export function formatNumber(num: number | null | undefined): string {
	const value = num ?? 0;
	if (value >= 1_000_000) return (value / 1_000_000).toFixed(1) + 'M';
	if (value >= 1_000) return (value / 1_000).toFixed(1) + 'k';
	return String(value);
}

export function formatDate(value?: string | null): string {
	if (!value) return '—';
	return new Intl.DateTimeFormat('es-AR', { dateStyle: 'medium' }).format(new Date(value));
}
