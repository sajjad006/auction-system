window.onload = function () {
  // get team name from hidden input
  var team_name = document.getElementById("team").value;
  var auction_id = document.getElementById("auction_id").value;

  var socket = io("http://192.168.29.165:3000", {
    rejectUnauthorized: false,
    query: { token: team_name },
  });
  socket.on("connect", function () {
    console.log("connected");
    socket.emit("join", { username: "its me", room: 1 });
  });
  socket.on("player", function (data) {
    document.getElementById("bid-table").innerHTML = "";

    self_purse = parseInt(document.getElementById("self_purse").value);
    if (self_purse > parseInt(data.base_price)) {
      document.getElementById("bid-btn").disabled = false;
    }
    document.getElementById("sold").style.display = "none";
    document.getElementById("panel").style.display = "block";
    document.getElementById(
      "player_name"
    ).innerHTML = `${data.name} (${data.rating})`;
    document.getElementById("auction_timer").innerHTML = "00:30";
    document.getElementById("player_type").innerHTML = data.type;
    document.getElementById("player_base_price").innerHTML = data.base_price;
    document.getElementById("player_bid_price").innerHTML = data.bid_price;
    document.getElementById("player_matches").innerHTML = data.matches;

    if (data.Image != null) {
      document.getElementById("player_image").src = data.Image;
    } else {
      document.getElementById("player_image").src =
        "../static/images/athlete.png";
    }

    if (data.type == "Bowler") {
      stats = `
        <tr>
          <td style="text-align: left">Matches</td>
          <td style="text-align: right" id="player_matches">${data.matches}</td>
        </tr>
        <tr>
          <td style="text-align: left">Wickets</td>
          <td style="text-align: right">${data.stats.wickets}</td>
        </tr>
        <tr>
          <td style="text-align: left">Average</td>
          <td style="text-align: right">${data.stats.average}</td>
        </tr>
        <tr>
          <td style="text-align: left">Economy</td>
          <td style="text-align: right">${data.stats.economy}</td>
        </tr>  
      `;
    } else {
      stats = `
      <tr>
        <td style="text-align: left">Matches</td>
        <td style="text-align: right" id="player_matches">${data.matches}</td>
      </tr>
      <tr>
        <td style="text-align: left">Runs</td>
        <td style="text-align: right">${data.stats.runs}</td>
      </tr>
      <tr>
        <td style="text-align: left">Average</td>
        <td style="text-align: right">${data.stats.average}</td>
      </tr>
      <tr>
        <td style="text-align: left">Strike Rate</td>
        <td style="text-align: right">${data.stats.sr}</td>
      </tr>
    
      `;
    }

    document.getElementById("stats-table").innerHTML = stats;
  });
  socket.on("bid", function (data) {
    document.getElementById("player_bid_price").innerHTML = data.next;

    self_purse = parseInt(document.getElementById("self_purse").value);
    if (data.team != team_name && self_purse > parseInt(data.next)) {
      document.getElementById("bid-btn").disabled = false;
    }

    // append bid to bid history
    var bid_history = document.getElementById("bid-table");
    var new_bid = document.createElement("tr");
    new_bid.innerHTML = `
    <tr>
      <td>
        <img style="border-radius: 20cm" src="https://ui-avatars.com/api/?name=${data.team}" alt="" width="50"
          height="50" />
      </td>
      <td>${data.team}</td>
      <td>${data.price}</td>
    </tr>`;
    bid_history.appendChild(new_bid);
    console.log(data);
  });
  socket.on("sold", function (data) {
    document.getElementById("participants-table").innerHTML = "";
    document.getElementById("team-table").innerHTML = "";
    document.getElementById("bid-btn").disabled = true;
    document.getElementById("panel").style.display = "none";
    document.getElementById("self_purse").value =
      parseInt(document.getElementById("self_purse").value) -
      parseInt(data.price);

    var participants_table = document.getElementById("participants-table");
    data.purse.forEach((element) => {
      // append row to participants table
      var new_participant = document.createElement("tr");
      new_participant.innerHTML = `
        <tr>
          <td>
            <img style="border-radius: 20cm" src="https://ui-avatars.com/api/?name=${element.team_name}" alt="" width="50"
              height="50" />
          </td>
          <td>${element.team_name}</td>

          <td>${element.purse}</td>
          <td>${element.points}</td>
        </tr>
      `;
      participants_table.appendChild(new_participant);
    });

    var team_table = document.getElementById("team-table");
    data.team_players.forEach((element) => {
      if (element.team == team_name) {
        // append row to team table
        var new_player = document.createElement("tr");
        new_player.innerHTML = `
        <tr>
          <td>
          <img src="../static/images/athlete.png" alt="" width="50" height="50" />
          </td>
          <td>${element.player}</td>
          <td>${element.cost}</td>
          </tr>
        `;
        team_table.appendChild(new_player);
      } else {
        console.log("not same");
      }
    });

    if (data.team != null)
      document.getElementById(
        "sold"
      ).innerHTML = `<br><br><br><h3>SOLD TO ${data.team} FOR ${data.price}</h3>`;
    else
      document.getElementById("sold").innerHTML = `<br><br><br><h3>UNSOLD</h3>`;
    document.getElementById("sold").style.display = "block";
  });
  socket.on("disconnect", (reason) => {
    // ...
  });
  socket.on("end", function (data) {
    // redirect to final page
    window.location.href = `/final/${data.auction_id}`;
  });


  document.getElementById("bid-btn").addEventListener("click", function () {
    console.log("hello");
    document.getElementById("bid-btn").disabled = true;
    bp = document.getElementById("player_bid_price").innerHTML;
    socket.emit("bid", {
      bid_price: bp,
      team: team_name,
      auction_id: auction_id,
    });
  });
};
