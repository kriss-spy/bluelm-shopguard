async function loadConfig() {
  try {
    const response = await fetch("config/config.json");
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const config = await response.json();
    
    // Update head
    document.title = config.pageTitle;
    
    // Update various sections
    document.getElementById("headerTitle").textContent = config.headerTitle;
    document.getElementById("heroTitle").textContent = config.hero.title;
    document.getElementById("heroSubtitle").textContent = config.hero.subtitle;

    // Update team section
    document.getElementById("teamName").textContent = config.team.name;
    document.getElementById("teamBackground").textContent = config.team.background;

    const teamMembersList = document.getElementById("teamMembers");
    teamMembersList.innerHTML = ""; // Clear existing members
    config.team.members.forEach((member) => {
      const listItem = document.createElement("li");
      listItem.className = "flex items-center";
      let iconClass = member.role === "队长" ? "ri-user-star-line" : "ri-user-line";
      let iconBg = member.role === "队长" ? "bg-[#5E6AD2]" : "bg-[#8A94E9]";

      listItem.innerHTML = `
        <span class="${iconBg} w-8 h-8 rounded-full text-white flex items-center justify-center mr-3 flex-shrink-0">
          <i class="${iconClass}"></i>
        </span>
        <div>
          <p class="font-medium">${member.name}${member.role ? " (" + member.role + ")" : ""}</p>
          <p class="text-sm text-gray-600 dark:text-gray-400">${member.description}</p>
        </div>
      `;
      teamMembersList.appendChild(listItem);
    });
  } catch (error) {
    console.error("Could not load config:", error);
    // Error handling for UI elements
    document.getElementById("teamName").textContent = "Error loading team name.";
    document.getElementById("teamBackground").textContent = "Error loading team background.";
    const teamMembersList = document.getElementById("teamMembers");
    teamMembersList.innerHTML = '<li class="flex items-center">Error loading members.</li>';
  }
}

document.addEventListener("DOMContentLoaded", function() {
  // Load configuration
  loadConfig();
  
  // Initialize other components
  initializeAnimations();
});