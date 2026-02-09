/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./src/rockgarden/templates/**/*.html"],
  theme: {
    extend: {
      typography: {
        DEFAULT: {
          css: {
            maxWidth: "none",
          },
        },
      },
    },
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
  daisyui: {
    themes: true,
  },
};
