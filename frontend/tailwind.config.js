/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ibmBlue: '#0f62fe',
        ibmDark: '#161616',
      },
    },
  },
  plugins: [],
}