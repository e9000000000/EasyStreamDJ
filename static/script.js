function add_result(result) {
    var list = document.getElementById('results_list');

    var entry = document.createElement('li');
    entry.className = "list-group-item";
    entry.appendChild(document.createTextNode(result));
    list.insertBefore(entry, list.firstChild);
}

var socket = io.connect(HOST + ':' + PORT);
socket.on('message', function(msg) {
    add_result(msg)
});

function start_btn_click() {
    var data = {
        'channel_name': document.getElementById('channel_name').value,
        'playlist_id': document.getElementById('playlist_id').value,
        'cooldown': document.getElementById('cooldown').value
    }

    socket.send('send ' + JSON.stringify(data))
}
