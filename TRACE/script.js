const button = document.querySelector(".trace-button");

const message = document.getElementById("traceMessage");

button.addEventListener("click", function() {
  message.hidden = false;
  button.textContent = "CLUE DISCOVERED";
});
