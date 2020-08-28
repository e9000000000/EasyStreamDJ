function add_result(result) {
    var list = document.getElementById('results_list');

    var entry = document.createElement('li');
    entry.className = "list-group-item";
    entry.appendChild(document.createTextNode(result));
    list.insertBefore(entry, list.firstChild);
}

function start_btn_click() {
    var chanel_name = document.getElementById('chanel_name').value;
    var playlist_id = document.getElementById('playlist_id').value;
    var cooldown = document.getElementById('cooldown').value;

    add_result('not working for now');
}