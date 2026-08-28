/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: '#f2f7f4',
          100: '#e1ede6',
          200: '#c3dbce',
          300: '#94beaa',
          400: '#5a997b',
          500: '#235c3f',
          600: '#1b4932',
          700: '#153826', // Primary Reference Brand Color
          800: '#102b1d',
          900: '#0b1d14',
          950: '#06100b',
        }
      },
      borderRadius: {
        '2xl': '1rem',      // 16px
        '3xl': '1.5rem',    // 24px - reference design main card radius
        '4xl': '2rem',      // 32px
      },
      boxShadow: {
        'soft': '0 10px 30px -5px rgba(0, 0, 0, 0.04)',
        'floating': '0 20px 40px -15px rgba(0, 0, 0, 0.07)',
        'chat-input': '0 12px 32px -8px rgba(0, 0, 0, 0.08), 0 4px 12px -4px rgba(0, 0, 0, 0.03)',
      },
      letterSpacing: {
        'tracked': '0.08em',
      }
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
}
