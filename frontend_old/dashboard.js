// Mock data
const userData = {
  score: 840,
  level: "Level 5 Ozone Defender",
  rank: 12,
  badges: ["Green Starter", "Recycling Pro", "Ozone Hero"]
};

const leaderboard = [
  { name: "Priya", points: 987 },
  { name: "Rahul", points: 923 },
  { name: "Anita", points: 891 },
  { name: "You", points: 840 }
];

// Update dashboard on load
document.addEventListener("DOMContentLoaded", function () {
  const scoreElement = document.querySelector(".score");
  const levelElement = document.querySelector(".level-text");
  const rankInfo = document.querySelector(".rank-info");

  scoreElement.textContent = `${userData.score} pts`;
  levelElement.textContent = userData.level;
  rankInfo.textContent = `Rank in Kalinga University: #${userData.rank} — Only ${10 - userData.rank} spots to Top 10!`;

  // Add badges dynamically
  const badgeGrid = document.querySelector(".badge-grid");
  userData.badges.forEach(badge => {
    const badgeEl = document.createElement("div");
    badgeEl.className = "badge";
    badgeEl.textContent = badge;
    badgeGrid.appendChild(badgeEl);
  });
});