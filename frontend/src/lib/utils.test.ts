import { describe, expect, it } from 'vitest';
import { formatDate, formatNumber } from './utils';

describe('formatNumber', () => {
	it('muestra tal cual por debajo de mil', () => {
		expect(formatNumber(0)).toBe('0');
		expect(formatNumber(999)).toBe('999');
	});

	it('abrevia miles y millones con un decimal', () => {
		expect(formatNumber(1000)).toBe('1.0k');
		expect(formatNumber(1500)).toBe('1.5k');
		expect(formatNumber(2_000_000)).toBe('2.0M');
	});

	it('trata null/undefined como cero', () => {
		expect(formatNumber(null)).toBe('0');
		expect(formatNumber(undefined)).toBe('0');
	});
});

describe('formatDate', () => {
	it('muestra un guion sin fecha', () => {
		expect(formatDate()).toBe('—');
		expect(formatDate(null)).toBe('—');
	});

	it('formatea una fecha ISO en español', () => {
		expect(formatDate('2026-10-12T00:00:00+00:00')).toContain('2026');
	});
});
