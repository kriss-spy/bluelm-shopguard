function initializeAnimations() {
  // Animate progress bars on scroll
  const progressBars = document.querySelectorAll(".progress-bar");
  
  const animateProgress = (bar) => {
    const targetWidth = bar.style.width; // Get the target width set inline
    bar.style.width = "0%"; // Reset for animation
    setTimeout(() => {
      bar.style.width = targetWidth;
    }, 100); // Slight delay to ensure transition occurs
  };

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateProgress(entry.target);
          observer.unobserve(entry.target); // Animate only once
        }
      });
    },
    { threshold: 0.5 }
  );

  progressBars.forEach((bar) => {
    observer.observe(bar);
  });
}