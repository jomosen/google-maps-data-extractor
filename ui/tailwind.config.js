/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                dark: {
                    bg: '#0A0A0A',
                    surface: '#121212',
                    border: '#1E1E1E',
                    hover: '#1A1A1A',
                },
                primary: {
                    DEFAULT: '#6366F1',
                    hover: '#4F46E5',
                }
            }
        },
    },
    plugins: [],
}
