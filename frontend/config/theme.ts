/**
 * TypeScript wrapper & type definitions for Global Theme Configuration
 */
// eslint-disable-next-line @typescript-eslint/no-var-requires
const themeConfig = require('./theme');

export interface ThemeColors {
  id: string;
  name: string;
  unicorn: {
    blush: string;
    pink: string;
    mint: string;
    orchid: string;
    aqua: string;
    lavender: string;
  };
  brand: {
    teal: string;
    'teal-hover': string;
    'teal-subtle': string;
    'teal-match': string;
    navy: string;
    'navy-deep': string;
    slate: string;
    muted: string;
    subtle: string;
    border: string;
    canvas: string;
    card: string;
  };
  fit: {
    perfect: string;
    tight: string;
    loose: string;
    extreme: string;
  };
  shadows: {
    widget: string;
    card: string;
    modal: string;
  };
  backdropGradient: string;
}

export type ThemeKey = 'unicornGlow' | 'oceanTeal';

export const THEMES: Record<ThemeKey, ThemeColors> = themeConfig.THEMES;
export const ACTIVE_THEME_KEY: ThemeKey = themeConfig.ACTIVE_THEME_KEY;
export const activeTheme: ThemeColors = themeConfig.activeTheme;
