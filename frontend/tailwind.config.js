/** @type {import('tailwindcss').Config} */
export default {
	content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
	theme: {
		extend: {
			colors: {
				// primary: '#0070AE',
				secondary: '#D0D0D0',
				third: '#F1F7FF',
				fourth: '#748DA8',

				// ========================/
				lambdaPrimary: '#FF8900',
				'lambdaPrimary-light': '#F09A51',
				darkblue: '#08141F',
				darkblueMedium: '#0C1924',
				darkblueLight: '#253645',
				greenLime: '#00A981',
				// ========================/
				'primary-dark': '#08141F',
				'secondary-dark': '#0D1E2C',
				'third-dark': '#00A981',
				'fourth-dark': '#102332',
				'fifth-dark': '#CEDAE8',
				'sixth-dark': '#12212E',
				'seventh-dark': '#0D1A25',
				'eight-dark': '#00D9A5',
				'ninth-dark': '#FF8900',
				'tenth-dark': '#00FFC2',
			},
			fontFamily: {
				outfit: ['Outfit', 'sans-serif'],
				Poppins: ['Poppins', 'sans-serif'],
			},
		},
	},

	plugins: [],
}
