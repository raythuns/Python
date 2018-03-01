from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib import parse
from maze import *
from maze_rand import build_box
import json


html = b"""\
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Maze</title>
    <style>
        #container .row {
            margin: 0;
            padding: 0;
            line-height: 0;
        }
        #container .row .col {
            margin: -1px;
            padding: 0;
            width: 16px;
            height: 16px;
            display: inline-block;
            background-clip: border-box;
        }
        #container .row .wall {
            background-color: chocolate;
        }
        #container .row .blank {
        }
        #container .row .people {
            padding: 4px;
            width: 8px;
            height: 8px;
            background-color: blue;
            background-clip: content-box;
        }
    </style>
</head>
<body>
<div id="container">
</div>
<script>
    var people_now_row, people_now_col;
    function ajax_get(url, callback) {
        var xhr = new XMLHttpRequest();
        xhr.open('GET', url, true);
        xhr.onreadystatechange = function () {
            if (xhr.readyState == 4 &&
                (xhr.status == 200 || xhr.status == 304)) {
                callback(this.responseText)
            }
        };
        xhr.send();
    }
    function game_start() {
        ajax_get('/start', function (responseText) {
            var json = JSON.parse(responseText);
            var row = json['row'];
            var col = json['col'];
            var box = json['box'];
            var container = document.getElementById("container");
            for (var i=0; i<row; i++) {
                var r = document.createElement('p');
                r.className =  'row row'+i;
                for (var j=0; j<col; j++) {
                    var c = document.createElement('p');
                    if (box[i][j] == "w")
                        c.className = 'col wall col'+j;
                    else if (box[i][j] == " ")
                        c.className = 'col blank col'+j;
                    else if (box[i][j] == "p"){
                        people_now_row = i;
                        people_now_col = j;
                        c.className =  'col people col'+j;
                    }
                    r.appendChild(c)
                }
                container.appendChild(r)
            }
        })
    }
    var keylock = false;
    function send_direction(direction) {
        if (keylock)
            return;
        keylock = true;
        ajax_get('/action?move='+direction, function (responseText) {
            var json = JSON.parse(responseText);
            if (json['success']) {
                var people = document.getElementsByClassName(
                    'row'+people_now_row)[0].getElementsByClassName(
                        'col'+people_now_col)[0];
                var blank = document.getElementsByClassName(
                    'row'+json['people'][0])[0].getElementsByClassName(
                        'col'+json['people'][1])[0];
                people.className = 'col blank col'+people_now_col;
                blank.className = 'col people col'+json['people'][1];
                people_now_row = json['people'][0];
                people_now_col = json['people'][1];
                if (json['gameover']) {
                    alert('You Win!');
                    location.reload();
                }
            }
            keylock = false
        });
    }
    document.onkeydown = function (ev) {
        ev = ev || window.event;
        if (ev.keyCode === 87)
            send_direction('UP');
        if (ev.keyCode === 65)
            send_direction('LEFT');
        if (ev.keyCode === 83)
            send_direction('DOWN');
        if (ev.keyCode === 68)
            send_direction('RIGHT');
    };
    game_start();
</script>
<p>
    <button onclick="send_direction('LEFT')">LEFT</button>
    <button onclick="send_direction('UP')">UP</button>
    <button onclick="send_direction('DOWN')">DOWN</button>
    <button onclick="send_direction('RIGHT')">RIGHT</button>
</p>
</body>
</html>
"""

box = None
maze_row = 16
maze_col = 16
box_row = maze_row*2+1
box_col = maze_col*2+1


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path[1:] == '':
            self.response_to(html)
        else:
            self.other()

    def other(self):
        global box
        res = parse.urlparse(self.path[1:])
        if res.path == 'action':
            if not box:
                return
            params = parse.parse_qs(res.query)
            direction = params['move'][0]
            success = False
            if direction == 'UP':
                success = try_move_to_up(box)
            elif direction == 'LEFT':
                success = try_move_to_left(box)
            elif direction == 'DOWN':
                success = try_move_to_down(box)
            elif direction == 'RIGHT':
                success = try_move_to_right(box)
            gameover = test_win(box)
            d = {'success': success,
                 'gameover': gameover,
                 'people': get_sub(box)}
            j = json.dumps(d)
            self.response_to(j.encode('utf-8'), content_type='text/json')
        elif res.path == 'start':
            box = build_box(maze_row, maze_col)
            d = {'box': box, 'row': box_row, 'col': box_col}
            j = json.dumps(d)
            self.response_to(j.encode('utf-8'), content_type='text/json')
        else:
            self._404_not_found()

    def _404_not_found(self):
        self.response_to(b'<h2>404 not Found!</h2>', response_code=404)

    def response_to(self, content,
                    content_type='text/html', response_code=200):
        self.send_response(response_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
        self.wfile.write(content)


def main():
    server = HTTPServer(('', 8080), Handler)
    server.serve_forever()


if __name__ == '__main__':
    main()
