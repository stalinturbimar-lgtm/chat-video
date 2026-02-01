from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import uuid

rooms = {}

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length))

        # CREAR SALA
        if self.path == "/create":
            room = data.get("room")
            name = data.get("name", "Anon")

            if not room:
                self.send_json({"error": "Código vacío"}, 400)
                return

            if room in rooms:
                self.send_json({"error": "La sala ya existe"}, 409)
                return

            uid = str(uuid.uuid4())
            rooms[room] = {
                "users": {uid: []},
                "names": {uid: name}
            }

            self.send_json({"uid": uid, "owner": True})

        # UNIRSE A SALA
        elif self.path == "/join":
            room = data.get("room")
            name = data.get("name", "Anon")

            if not room:
                self.send_json({"error": "Código vacío"}, 400)
                return

            if room not in rooms:
                self.send_json({"error": "La sala no existe"}, 404)
                return

            uid = str(uuid.uuid4())
            rooms[room]["users"][uid] = []
            rooms[room]["names"][uid] = name

            for u in rooms[room]["users"]:
                if u != uid:
                    rooms[room]["users"][u].append({
                        "join": uid,
                        "name": name
                    })

            self.send_json({"uid": uid, "owner": False})

        # MENSAJES
        elif self.path == "/poll":
            room = data.get("room")
            uid = data.get("uid")

            if room not in rooms or uid not in rooms[room]["users"]:
                self.send_json({"error": "No autorizado"}, 403)
                return

            msgs = rooms[room]["users"][uid]
            rooms[room]["users"][uid] = []
            self.send_json({"msgs": msgs})

        elif self.path == "/send":
            room = data.get("room")
            uid = data.get("uid")
            msg = data.get("msg")

            if room not in rooms or uid not in rooms[room]["users"]:
                self.send_json({"error": "No autorizado"}, 403)
                return

            for u in rooms[room]["users"]:
                if u != uid:
                    rooms[room]["users"][u].append({
                        "msg": msg,
                        "from": rooms[room]["names"][uid]
                    })

            self.send_json({"ok": True})

        else:
            self.send_json({"error": "Ruta inválida"}, 404)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), Handler)
    print("Servidor corriendo en http://localhost:8000")
    server.serve_forever()

