// var socket = io();

// socket.on("connect", function () {
//   socket.emit("my event", {
//     data: "I'm connected!",
//   });
// });

// button add event listener
window.onload = function () {
  join_buttons = document.getElementsByClassName("join-btn");

//   add click event listener to all join buttons
    for (var i = 0; i < join_buttons.length; i++) {
        join_buttons[i].addEventListener("click", function () {
            var room = this.getAttribute("data-auctionid");
            var name = this.getAttribute("data-name");
            // get form
            var form = document.getElementById("register-form");
            var auction = document.getElementById("auctions");
            var auction_name = document.getElementById("auction-name");
            var auctionidinput = document.getElementById("aucid");

            form.style.display = "block";
            auction.style.display = "none";
            auction_name.innerHTML = name;
            auctionidinput.value = room;
            // console.log(room);
            // socket.emit("join", {"username":"its me", "room":room});
        });
    }
};
