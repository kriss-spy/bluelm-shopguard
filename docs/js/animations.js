function initializeAnimations() {
  // Animate progress bars on scroll
  const progressBars = document.querySelectorAll(".progress-bar");
  
  const animateProgress = (bar) => {
    // Get the target width from the inline style
    const targetWidth = bar.style.width; 
    // Reset for animation
    bar.style.width = "0%"; 
    // Slight delay to ensure transition occurs
    setTimeout(() => {
      bar.style.width = targetWidth;
    }, 100);
  };

  // Use Intersection Observer to detect when elements come into view
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateProgress(entry.target);
          // Animate only once
          observer.unobserve(entry.target); 
        }
      });
    },
    { threshold: 0.5 }
  );

  // Observe each progress bar
  progressBars.forEach((bar) => {
    observer.observe(bar);
  });
}