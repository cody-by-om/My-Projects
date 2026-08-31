const statusBox = document.getElementById("statusBox");
const buttons = document.querySelectorAll(".btn");
const footerBtn = document.getElementById("footerBtn");
const themeToggle = document.getElementById("themeToggle");
const yearText = document.getElementById("year");

if (yearText) {
    yearText.textContent = new Date().getFullYear();
}

function handleDownloadClick(event) {
    const clickedButton = event.currentTarget;
    const hrefValue = clickedButton.getAttribute("href") || "";

    if (hrefValue.includes(".exe")) {
        statusBox.textContent = "Downloading: " + hrefValue;
        statusBox.classList.remove("warn");
        statusBox.classList.add("success");
    } else {
        event.preventDefault();
        statusBox.textContent = "This file is not available right now.";
        statusBox.classList.remove("success");
        statusBox.classList.add("warn");
    }
}

buttons.forEach(function (button) {
    button.addEventListener("click", handleDownloadClick);
});

footerBtn.addEventListener("click", function () {
    statusBox.textContent = "Welcome! Start your UltraEdit download now.";
    statusBox.classList.remove("warn");
    statusBox.classList.add("success");
});

themeToggle.addEventListener("click", function () {
    document.body.classList.toggle("dark-mode");
    if (document.body.classList.contains("dark-mode")) {
        themeToggle.textContent = "Light Mode";
    } else {
        themeToggle.textContent = "Toggle Theme";
    }
});