/** @type {import('tailwindcss').Config} */
export default {
  darkMode: "class",
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        sentinel: {
          navy: "#0f172a",
          deep: "#0b1120",
          blue: "#3b82f6",
          cyan: "#22d3ee",
          slate: "#475569",
        },
      },
    },
  },
  plugins: [],
}
