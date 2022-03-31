var socket = io.connect();

var username = null;
var room = null;
var joined = false;
var colorCallback = null;

function joinedRoom(success) {
    if (success) {
        joined = true;
        $("#joinForm").hide();
        $("#collectColorsButton").show();
        $("#gameRoom").text(`Room: ${room}`);
    }
}

socket.on("connect", () => {
    console.log("You are connected to the server.");
});

socket.on("connect_error", (data) => {
    console.log(`Unable to connect to the server: ${data}.`);
});

socket.on("disconnect", () => {
    console.log("You have been disconnected from the server.");
});

socket.on("message", (data) => {
    console.log(data);
});

socket.on("send color", (data, callback) => {
    $("#collectColorsButton").hide();
    $("#colorForm").show();
    console.log(`Callback set to ${callback}`);
    colorCallback = callback;
});

$("#joinForm").on("submit", (event) => {
    event.preventDefault();
    username = $("#usernameInput").val();
    room = $("#roomInput").val()
    socket.emit("join room", {username: username, room: room}, joinedRoom);
});

$("#colorForm").on("submit", (event) => {
    event.preventDefault();
    var color = $("#colorInput").val();
    $("#colorForm").hide();
    colorCallback(color);
});

$("#collectColorsButton").on("click", () => {
    socket.emit("collect colors", {username: username, room: room});
});
