document.addEventListener("DOMContentLoaded", function() {
  // Set up theme switcher functionality
  const themeSwitcher = document.getElementById("themeSwitcher");
  
  // Check if user preference is stored
  const savedTheme = localStorage.getItem("theme");
  
  // Apply theme logic
  if (savedTheme) {
    document.documentElement.classList.toggle("dark", savedTheme === "dark");
  } else {
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", prefersDark);
    localStorage.setItem("theme", prefersDark ? "dark" : "light");
  }
  
  // Set up event listeners
  if (themeSwitcher) {
    themeSwitcher.addEventListener("click", function() {
      document.documentElement.classList.toggle("dark");
      const currentTheme = document.documentElement.classList.contains("dark") ? "dark" : "light";
      localStorage.setItem("theme", currentTheme);
    });
  } else {
    console.error("Theme switcher element with ID 'themeSwitcher' not found!");
  }
});