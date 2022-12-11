var socket = io();

socket.on("connect", function () {
  socket.emit("my event", {
    data: "I'm connected!",
  });
});

// button add event listener
window.onload = function () {
  join_buttons = document.getElementsByClassName("join-button");

//   add click event listener to all join buttons
    for (var i = 0; i < join_buttons.length; i++) {
        join_buttons[i].addEventListener("click", function () {
            var room = this.getAttribute("data-room");
            socket.emit("join", {"username":"its me", "room":room});
        });
    }
};
