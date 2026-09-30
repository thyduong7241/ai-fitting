/**
 * Global Theme Configuration for AI Precision Fit
 * Single Source of Truth for Design Tokens & Color Palettes
 */

const THEMES = {
  /**
   * UNICORN GLOW PALETTE
   * #FAE7EB - Blush (soft canvas tint)
   * #F2D7E8 - Pink (subtle lilac blush)
   * #ECF8F7 - Mint (ice mint hero & note cards)
   * #B58EBC - Orchid (primary brand action & headers)
   * #D1EDEA - Aqua (complementary seafoam accents)
   * #D8BBD3 - Lavender (mauve border & hover feedback)
   */
  unicornGlow: {
    id: 'unicornGlow',
    name: 'Unicorn Glow',
    unicorn: {
      blush: '#FAE7EB',
      pink: '#F2D7E8',
      mint: '#ECF8F7',
      orchid: '#B58EBC',
      aqua: '#D1EDEA',
      lavender: '#D8BBD3',
    },
    brand: {
      teal: '#B58EBC',
      'teal-hover': '#A477AC',
      'teal-subtle': '#F2D7E8',
      'teal-match': '#8C5499',
      navy: '#281A35',
      'navy-deep': '#180E24',
      slate: '#5C486D',
      muted: '#88749B',
      subtle: '#AE9EC0',
      border: '#EBD6E7',
      canvas: '#FAF2F7',
      card: '#FFFFFF',
    },
    fit: {
      perfect: '#1B8272',
      tight: '#F59E0B',
      loose: '#8B5CF6',
      extreme: '#EF4444',
    },
    shadows: {
      widget: '0 20px 40px -15px rgba(181, 142, 188, 0.3)',
      card: '0 2px 10px rgba(181, 142, 188, 0.08)',
      modal: '0 25px 50px -12px rgba(40, 26, 53, 0.35)',
    },
    backdropGradient: 'from-[#FAE7EB] via-[#F2D7E8] to-[#ECF8F7]',
  },

  /**
   * OCEAN TEAL PALETTE (Classic original brand)
   */
  oceanTeal: {
    id: 'oceanTeal',
    name: 'Ocean Teal',
    unicorn: {
      blush: '#F0FDF4',
      pink: '#CCFBF1',
      mint: '#ECFDF5',
      orchid: '#0F766E',
      aqua: '#A7F3D0',
      lavender: '#99F6E4',
    },
    brand: {
      teal: '#16ABAD',
      'teal-hover': '#1AB8B8',
      'teal-subtle': '#DBF7F5',
      'teal-match': '#1F9C7A',
      navy: '#183247',
      'navy-deep': '#0E1F2E',
      slate: '#425C75',
      muted: '#5C738C',
      subtle: '#708AA5',
      border: '#DFEBEF',
      canvas: '#F6FBFA',
      card: '#FFFFFF',
    },
    fit: {
      perfect: '#1F9C7A',
      tight: '#F59E0B',
      loose: '#0EA5E9',
      extreme: '#EF4444',
    },
    shadows: {
      widget: '0 20px 40px -15px rgba(24, 50, 71, 0.15)',
      card: '0 2px 10px rgba(24, 50, 71, 0.04)',
      modal: '0 25px 50px -12px rgba(14, 31, 46, 0.25)',
    },
    backdropGradient: 'from-[#E5EDF0] via-[#E2EBF0] to-[#DFEBEF]',
  },
};

// Active theme selection
const ACTIVE_THEME_KEY = 'unicornGlow';
const activeTheme = THEMES[ACTIVE_THEME_KEY];

module.exports = {
  THEMES,
  ACTIVE_THEME_KEY,
  activeTheme,
};
