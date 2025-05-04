from flask import Flask, request, jsonify
# mcpiライブラリは後でインポートします
from mcpi.minecraft import Minecraft

app = Flask(__name__)

# Minecraftへの接続 (後で初期化)
mc = None

@app.route('/')
def index():
    return "Minecraft Scratch Bridge is running!"

# Scratchからのコマンドを受け取るエンドポイント (例)
@app.route('/command', methods=['POST'])
def handle_command():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Invalid JSON"}), 400

    command = data.get('command')
    args = data.get('args', [])

    print(f"Received command: {command} with args: {args}")

    # ここでMinecraftへのコマンドを実行するロジックを追加
    # 例:
    # if command == 'postToChat':
    #     if mc and len(args) > 0:
    #         mc.postToChat(str(args[0]))
    #         return jsonify({"status": "success"})
    #     else:
    #         return jsonify({"status": "error", "message": "Minecraft not connected or invalid args"}), 500
    # elif command == 'setBlock':
    # ここでMinecraftへのコマンドを実行するロジックを追加
    global mc
    if not mc:
        return jsonify({"status": "error", "message": "Minecraft not connected"}), 503 # Service Unavailable

    try:
        if command == 'postToChat':
            if len(args) > 0:
                mc.postToChat(str(args[0]))
                return jsonify({"status": "success", "message": f"Posted '{args[0]}' to chat"})
            else:
                return jsonify({"status": "error", "message": "Missing message argument for postToChat"}), 400
        elif command == 'setBlock':
            if len(args) == 4: # x, y, z, block_id (block_dataはオプションなので省略)
                try:
                    x, y, z, block_id = map(int, args[:4])
                    mc.setBlock(x, y, z, block_id)
                    return jsonify({"status": "success", "message": f"Set block at ({x},{y},{z}) to {block_id}"})
                except ValueError:
                    return jsonify({"status": "error", "message": "Invalid arguments for setBlock (must be integers)"}), 400
            else:
                 return jsonify({"status": "error", "message": "Incorrect number of arguments for setBlock (expected 4)"}), 400
        elif command == 'getPlayerPos':
            if len(args) == 0:
                pos = mc.player.getPos()
                # Vec3 オブジェクトは直接 JSON シリアライズできない場合があるので、属性を個別に返す
                return jsonify({"status": "success", "x": pos.x, "y": pos.y, "z": pos.z})
            else:
                return jsonify({"status": "error", "message": "getPlayerPos does not take any arguments"}), 400
        elif command == 'setPlayerPos':
            if len(args) == 3: # x, y, z
                try:
                    x, y, z = map(float, args[:3]) # 座標は float もありうる
                    mc.player.setPos(x, y, z)
                    return jsonify({"status": "success", "message": f"Set player position to ({x},{y},{z})"})
                except ValueError:
                    return jsonify({"status": "error", "message": "Invalid arguments for setPlayerPos (must be numbers)"}), 400
            else:
                return jsonify({"status": "error", "message": "Incorrect number of arguments for setPlayerPos (expected 3)"}), 400
        elif command == 'getBlock':
            if len(args) == 3: # x, y, z
                try:
                    x, y, z = map(int, args[:3])
                    block_id = mc.getBlock(x, y, z)
                    return jsonify({"status": "success", "block_id": block_id})
                except ValueError:
                    return jsonify({"status": "error", "message": "Invalid arguments for getBlock (must be integers)"}), 400
            else:
                return jsonify({"status": "error", "message": "Incorrect number of arguments for getBlock (expected 3)"}), 400
        elif command == 'setBlocks':
            # 引数: x1, y1, z1, x2, y2, z2, block_id, [block_data] (block_dataはオプション)
            if len(args) == 7 or len(args) == 8:
                try:
                    coords = list(map(int, args[:6]))
                    block_id = int(args[6])
                    block_data = int(args[7]) if len(args) == 8 else None
                    if block_data is not None:
                        mc.setBlocks(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5], block_id, block_data)
                    else:
                        mc.setBlocks(coords[0], coords[1], coords[2], coords[3], coords[4], coords[5], block_id)
                    return jsonify({"status": "success", "message": f"Set blocks in range ({coords[0]}..{coords[3]}, {coords[1]}..{coords[4]}, {coords[2]}..{coords[5]}) to {block_id}" + (f":{block_data}" if block_data is not None else "")})
                except ValueError:
                    return jsonify({"status": "error", "message": "Invalid arguments for setBlocks (must be integers)"}), 400
            else:
                return jsonify({"status": "error", "message": "Incorrect number of arguments for setBlocks (expected 7 or 8)"}), 400
        elif command == 'getHeight':
            if len(args) == 2: # x, z
                try:
                    x, z = map(int, args[:2])
                    height = mc.getHeight(x, z)
                    return jsonify({"status": "success", "height": height})
                except ValueError:
                     return jsonify({"status": "error", "message": "Invalid arguments for getHeight (must be integers)"}), 400
            else:
                return jsonify({"status": "error", "message": "Incorrect number of arguments for getHeight (expected 2)"}), 400
        elif command == 'getPlayerTilePos':
             if len(args) == 0:
                pos = mc.player.getTilePos()
                return jsonify({"status": "success", "x": pos.x, "y": pos.y, "z": pos.z})
             else:
                return jsonify({"status": "error", "message": "getPlayerTilePos does not take any arguments"}), 400
        elif command == 'getPlayerDirection':
            if len(args) == 0:
                direction = mc.player.getDirection()
                return jsonify({"status": "success", "x": direction.x, "y": direction.y, "z": direction.z})
            else:
                return jsonify({"status": "error", "message": "getPlayerDirection does not take any arguments"}), 400
        elif command == 'getPlayerRotation':
            if len(args) == 0:
                rotation = mc.player.getRotation()
                return jsonify({"status": "success", "rotation": rotation})
            else:
                return jsonify({"status": "error", "message": "getPlayerRotation does not take any arguments"}), 400
        elif command == 'getPlayerPitch':
            if len(args) == 0:
                pitch = mc.player.getPitch()
                return jsonify({"status": "success", "pitch": pitch})
            else:
                return jsonify({"status": "error", "message": "getPlayerPitch does not take any arguments"}), 400
        elif command == 'worldSetting':
            if len(args) == 2: # setting_name, status (True/False or 1/0)
                setting_name = str(args[0])
                status_str = str(args[1]).lower()
                if status_str in ['true', '1']:
                    status = True
                elif status_str in ['false', '0']:
                    status = False
                else:
                    return jsonify({"status": "error", "message": "Invalid status for worldSetting (must be true/false or 1/0)"}), 400

                # 利用可能な設定名を制限するか、そのまま渡すか検討
                # ここではそのまま渡す
                mc.world.setting(setting_name, status)
                return jsonify({"status": "success", "message": f"Set world setting '{setting_name}' to {status}"})
            else:
                return jsonify({"status": "error", "message": "Incorrect number of arguments for worldSetting (expected 2: name, status)"}), 400
        elif command == 'pollBlockHits':
             if len(args) == 0:
                hits = mc.events.pollBlockHits()
                # Event オブジェクトをJSONシリアライズ可能な形式に変換
                hits_data = [{"type": hit.type, "pos": {"x": hit.pos.x, "y": hit.pos.y, "z": hit.pos.z}, "face": hit.face, "entityId": hit.entityId} for hit in hits]
                return jsonify({"status": "success", "hits": hits_data})
             else:
                return jsonify({"status": "error", "message": "pollBlockHits does not take any arguments"}), 400
        elif command == 'pollChatPosts':
             if len(args) == 0:
                posts = mc.events.pollChatPosts()
                # Event オブジェクトをJSONシリアライズ可能な形式に変換
                posts_data = [{"type": post.type, "entityId": post.entityId, "message": post.message} for post in posts]
                return jsonify({"status": "success", "posts": posts_data})
             else:
                return jsonify({"status": "error", "message": "pollChatPosts does not take any arguments"}), 400
        elif command == 'clearEvents':
            if len(args) == 0:
                mc.events.clearAll()
                return jsonify({"status": "success", "message": "Cleared all events"})
            else:
                return jsonify({"status": "error", "message": "clearEvents does not take any arguments"}), 400
        # --- 他のMinecraftコマンドの処理をここに追加 ---
        else:
            return jsonify({"status": "error", "message": f"Unknown command: {command}"}), 400
    except Exception as e:
        # エラーの詳細をログに出力
        import traceback
        print(f"Error executing Minecraft command '{command}' with args {args}:")
        traceback.print_exc()
        return jsonify({"status": "error", "message": f"Minecraft command failed: {e}"}), 500

    # # 仮のレスポンス (エラー処理が先に行われるため、通常ここには到達しない)
    # return jsonify({"status": "received", "command": command, "args": args})

if __name__ == '__main__':
    # Minecraft Pi Edition (Reborn)が動作しているホストとポートを指定
    # DockerコンテナからホストOS上のMinecraftに接続する場合、
    # 'host.docker.internal' またはホストマシンのIPアドレスを使用します。
    # 環境変数から取得するか、デフォルト値を設定します。
    import os
    minecraft_host = os.environ.get("MINECRAFT_HOST", "localhost")
    minecraft_port = int(os.environ.get("MINECRAFT_PORT", 4711)) # デフォルトポート

    try:
        print(f"Attempting to connect to Minecraft at {minecraft_host}:{minecraft_port}...")
        mc = Minecraft.create(minecraft_host, minecraft_port)
        # 接続確認のためにチャットにメッセージを送信
        mc.postToChat("Scratch bridge connected!")
        print("Successfully connected to Minecraft Pi Edition (Reborn)")
    except Exception as e:
        print(f"!!! WARNING: Could not connect to Minecraft at {minecraft_host}:{minecraft_port} - {e}")
        print("!!! The bridge will run, but Minecraft commands will fail until connection is established.")
        mc = None # 接続失敗時はNoneに設定

    # Flaskサーバーを起動
    # host='0.0.0.0' でコンテナ外部からのアクセスを許可
    app.run(host='0.0.0.0', port=5000, debug=True)
