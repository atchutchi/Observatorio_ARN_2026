import type { Config } from 'tailwindcss'

const config: Config = {
  content: [
    './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
    './src/components/**/*.{js,ts,jsx,tsx,mdx}',
    './src/app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  theme: {
    extend: {
      colors: {
        arn: {
          primary: '#1B2A4A',
          secondary: '#2C3E6B',
          light: '#3D5291',
        },
        telecel: {
          DEFAULT: '#E30613',
          dark: '#B50510',
          light: '#FF2D3A',
        },
        orange: {
          DEFAULT: '#FF6600',
          dark: '#CC5200',
          light: '#FF8533',
        },
        starlink: {
          DEFAULT: '#000000',
          accent: '#1DA1F2',
          light: '#333333',
        },
      },
    },
  },
  plugins: [],
}

export default config
