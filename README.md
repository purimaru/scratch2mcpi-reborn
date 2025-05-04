# Scratch - Minecraft Pi Edition (Reborn) Bridge

ScratchからMinecraft Pi Edition (Reborn)をHTTP経由で操作するためのブリッジアプリケーションです。
Raspberry Pi上のDockerコンテナとして動作するように設計されています。

## 機能

*   ScratchのHTTP拡張機能などを使用して、Minecraft Pi Edition (Reborn)にコマンドを送信します。
*   Flask WebサーバーがHTTPリクエストを受け付け、`mcpi-reborn`ライブラリを使用してMinecraftを操作します。
*   Dockerコンテナ化されており、Raspberry Pi上でのセットアップと実行が容易です。

## 現在サポートされているコマンド

*   `postToChat`: Minecraftのチャットにメッセージを表示します。
    *   例: `{"command": "postToChat", "args": ["Hello from Scratch!"]}`
*   `setBlock`: 指定した座標にブロックを設置します。
    *   引数: `[x, y, z, block_id]` (すべて整数)
    *   例: `{"command": "setBlock", "args": [10, 5, 20, 1]}`
*   `getPlayerPos`: プレイヤーの現在の座標を取得します。
    *   引数: なし `[]`
    *   例: `{"command": "getPlayerPos", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "x": 10.5, "y": 64.0, "z": -20.1}`
*   `setPlayerPos`: プレイヤーを指定した座標にテレポートします。
    *   引数: `[x, y, z]` (数値)
    *   例: `{"command": "setPlayerPos", "args": [0.5, 100.0, 50.2]}`
*   `getBlock`: 指定した座標のブロックIDを取得します。
    *   引数: `[x, y, z]` (すべて整数)
    *   例: `{"command": "getBlock", "args": [10, 5, 20]}`
    *   成功時のレスポンス例: `{"status": "success", "block_id": 3}` (土ブロックの場合)
*   `setBlocks`: 指定した範囲(x1,y1,z1)から(x2,y2,z2)までを同じブロックで満たします。
    *   引数: `[x1, y1, z1, x2, y2, z2, block_id, [block_data]]` (block_dataはオプション、すべて整数)
    *   例: `{"command": "setBlocks", "args": [0, 0, 0, 5, 5, 5, 1]}` (石で満たす)
    *   例: `{"command": "setBlocks", "args": [0, 0, 0, 2, 2, 2, 35, 1]}` (オレンジ色の羊毛で満たす)
*   `getHeight`: 指定したXZ座標で、最も高い空気以外のブロックのY座標を取得します。
    *   引数: `[x, z]` (整数)
    *   例: `{"command": "getHeight", "args": [10, 20]}`
    *   成功時のレスポンス例: `{"status": "success", "height": 62}`
*   `getPlayerTilePos`: プレイヤーがいるブロックの座標（整数）を取得します。
    *   引数: なし `[]`
    *   例: `{"command": "getPlayerTilePos", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "x": 10, "y": 64, "z": -20}`
*   `getPlayerDirection`: プレイヤーが向いている方向を示す単位ベクトル(x, y, z)を取得します。
    *   引数: なし `[]`
    *   例: `{"command": "getPlayerDirection", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "x": 0.707, "y": 0.0, "z": -0.707}`
*   `getPlayerRotation`: プレイヤーの水平方向の向きを角度（0-360度）で取得します。北が0度、東が90度、南が180度、西が270度。
    *   引数: なし `[]`
    *   例: `{"command": "getPlayerRotation", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "rotation": 270.5}`
*   `getPlayerPitch`: プレイヤーの垂直方向の向きを角度で取得します。水平が0度、上が-90度、下が90度。
    *   引数: なし `[]`
    *   例: `{"command": "getPlayerPitch", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "pitch": -15.2}`
*   `worldSetting`: ワールドの設定を変更します。
    *   引数: `[setting_name, status]` (setting_nameは文字列, statusは `true`/`false` または `1`/`0`)
    *   例: `{"command": "worldSetting", "args": ["world_immutable", true]}` (ワールドを破壊不可に)
    *   例: `{"command": "worldSetting", "args": ["nametags_visible", 0]}` (ネームタグを非表示に)
*   `pollBlockHits`: 前回の呼び出し以降に発生したブロックヒットイベント（プレイヤーがブロックを叩いたイベント）のリストを取得します。
    *   引数: なし `[]`
    *   例: `{"command": "pollBlockHits", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "hits": [{"type": 4, "pos": {"x": 10, "y": 63, "z": -21}, "face": 1, "entityId": 1}]}` (リストは空の場合もあります)
*   `pollChatPosts`: 前回の呼び出し以降に発生したチャット投稿イベントのリストを取得します。
    *   引数: なし `[]`
    *   例: `{"command": "pollChatPosts", "args": []}`
    *   成功時のレスポンス例: `{"status": "success", "posts": [{"type": 5, "entityId": 1, "message": "hello"}]}` (リストは空の場合もあります)
*   `clearEvents`: サーバーに蓄積されている全てのイベントをクリアします。`pollBlockHits` や `pollChatPosts` を使う前に実行すると便利です。
    *   引数: なし `[]`
    *   例: `{"command": "clearEvents", "args": []}`

*   *他のコマンドは `app.py` の `handle_command` 関数を編集することで追加できます。*

## 要件

*   Raspberry Pi (Raspberry Pi 5 64bit OSでテスト済み)
*   Docker および Docker Compose
*   Minecraft Pi Edition (Reborn) (実行中で、APIが有効になっていること)

## セットアップと実行

1.  **リポジトリのクローン:**
    ```bash
    git clone <リポジトリのURL>
    cd minecraft-scratch-bridge
    ```

2.  **Minecraft Pi Edition (Reborn) の起動:**
    Raspberry Pi上でMinecraft Pi Edition (Reborn) を起動し、ワールドに入ります。

3.  **Dockerコンテナのビルドと起動:**
    `minecraft-scratch-bridge` ディレクトリ内で以下のコマンドを実行します。
    ```bash
    docker compose up --build -d
    ```
    *   初回起動時やコード変更後は `--build` オプションが必要です。
    *   `-d` オプションでバックグラウンド実行します。
    *   このプロセス中に `Dockerfile` 内の `RUN pytest` コマンドによってユニットテストが自動的に実行されます。テストが失敗するとビルドは中止されます。

4.  **動作確認 (任意):**
    コンテナのログを確認して、Minecraftへの接続が成功したか確認します。
    ```bash
    docker compose logs -f
    ```
    "Successfully connected to Minecraft Pi Edition (Reborn)" と表示されれば成功です。

## Scratchからの使い方

ScratchのHTTP拡張機能（または同等の機能を持つ拡張機能）を使用して、以下の設定でHTTP POSTリクエストを送信します。

*   **URL:** `http://<RaspberryPiのIPアドレス>:5000/command`
    *   `<RaspberryPiのIPアドレス>` は、ブリッジを実行しているRaspberry Piの実際のIPアドレスに置き換えてください (`ip addr` コマンドなどで確認できます)。
*   **メソッド:** `POST`
*   **ヘッダー:** `Content-Type: application/json`
*   **ボディ (JSON形式):**
    ```json
    {
      "command": "<コマンド名>",
      "args": [<引数1>, <引数2>, ...]
    }
    ```
    (サポートされているコマンドのセクションを参照)

## テストの実行

ユニットテストは `pytest` を使用して書かれています。

*   **Dockerビルド中の自動実行:** `docker compose up --build` を実行すると、`Dockerfile` のビルドステージで自動的にテストが実行されます。
*   **ローカルでの手動実行 (開発用):**
    1.  必要な依存関係（テスト用ライブラリを含む）をインストールします:
        ```bash
        pip install -r requirements.txt
        ```
    2.  プロジェクトのルートディレクトリ (`minecraft-scratch-bridge`) で `pytest` コマンドを実行します:
        ```bash
        pytest
        ```

## 設定

`docker-compose.yml` ファイル内の `environment` セクションで設定を変更できます。

*   `MINECRAFT_HOST`: Minecraft Pi Edition (Reborn) が動作しているホスト名またはIPアドレス。
    *   デフォルトは `host.docker.internal` です。これは通常、コンテナを実行しているホストマシンを指します。
    *   これが機能しない場合（特に古いDockerバージョンや特定のネットワーク構成）、Raspberry PiのローカルIPアドレス（例: `192.168.1.10`）に明示的に設定してみてください。設定変更後は `docker compose down && docker compose up --build -d` でコンテナを再起動してください。
*   `MINECRAFT_PORT`: Minecraft Pi Edition (Reborn) のAPIポート。デフォルトは `4711` です。

## 新しいコマンドの追加方法

1.  `minecraft-scratch-bridge/app.py` ファイルを開きます。
2.  `handle_command` 関数内の `try...except` ブロックに `elif command == '新しいコマンド名':` のような条件分岐を追加します。
3.  `mcpi-reborn` ライブラリのドキュメント ([https://mcpi-reborn.readthedocs.io/en/latest/](https://mcpi-reborn.readthedocs.io/en/latest/) など) を参照し、対応するMinecraft API関数を呼び出すコードを記述します。
4.  引数の数や型をチェックし、適切なJSONレスポンス（成功またはエラー）を返すようにします。
5.  ファイルを保存し、`docker compose down && docker compose up --build -d` でコンテナを再起動して変更を適用します。

## ライセンス

このプロジェクトは [MITライセンス](LICENSE) の下で公開されています。(必要であればLICENSEファイルを追加してください)
