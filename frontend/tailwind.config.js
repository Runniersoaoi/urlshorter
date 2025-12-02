/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{vue,js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                'brand-dark': '#0b1736',
                'brand-orange': '#ee6123',
                'text-primary': '#FFFDF9',
                'text-secondary': '#EF6123',
                'text-tertiary': '#878784',
                'background-primary': '#021F39',
            }
        },
    },
    plugins: [],
}
