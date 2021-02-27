// List of themes, which must correspond to CSS classes implementing theme variables used throughout the CSS
// First entry is the default theme
const THEMES = ["light-theme", "dark-theme"];

function setTheme(themeName){
	// Set theme
	document.body.classList = [];
	document.body.classList.add(themeName);

	// Save to local storage
	localStorage.setItem('theme', themeName);
}

function cycleTheme(){
	let currentTheme = localStorage.getItem('theme');
	let themeIndex = THEMES.indexOf(currentTheme);
	setTheme(THEMES[(themeIndex + 1) % THEMES.length]);
}

document.addEventListener('DOMContentLoaded', function() {
	let storedTheme = localStorage.getItem('theme');
	if (THEMES.includes(storedTheme)) {
		setTheme(localStorage.getItem('theme'));
	} else {
		setTheme(THEMES[0]);
	}
}, false);
