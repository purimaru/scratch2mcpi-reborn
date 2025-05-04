import pytest
from flask import Flask, jsonify
from app import app as flask_app # app.py から Flask アプリケーションインスタンスをインポート
from mcpi.minecraft import Minecraft # モック対象のクラスをインポート

# pytest フィクスチャ: テスト用の Flask クライアントを提供
@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

# pytest フィクスチャ: Minecraft 接続をモック
# mocker は pytest-mock によって提供されるフィクスチャ
@pytest.fixture
def mock_minecraft(mocker):
    # app.Minecraft.create をモックし、モックされたインスタンスを返すように設定
    mock_mc_instance = mocker.MagicMock(spec=Minecraft)
    mocker.patch('app.Minecraft.create', return_value=mock_mc_instance)

    # app モジュール内のグローバル変数 mc もモックされたインスタンスに置き換える
    # これにより、リクエストハンドラ内で正しいモックが使用される
    mocker.patch('app.mc', mock_mc_instance)

    return mock_mc_instance

# --- テストケース ---

def test_index(client):
    """ルートURL ('/') が期待通りのレスポンスを返すかテスト"""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Minecraft Scratch Bridge is running!" in response.data

def test_command_post_to_chat_success(client, mock_minecraft):
    """'/command' への有効な postToChat リクエストが成功するかテスト"""
    response = client.post('/command', json={
        "command": "postToChat",
        "args": ["Test message"]
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == "Posted 'Test message' to chat"
    # mc.postToChat が正しい引数で呼び出されたか検証
    mock_minecraft.postToChat.assert_called_once_with("Test message")

def test_command_set_block_success(client, mock_minecraft):
    """'/command' への有効な setBlock リクエストが成功するかテスト"""
    response = client.post('/command', json={
        "command": "setBlock",
        "args": [10, 20, 30, 1] # x, y, z, block_id
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == "Set block at (10,20,30) to 1"
    # mc.setBlock が正しい引数で呼び出されたか検証
    mock_minecraft.setBlock.assert_called_once_with(10, 20, 30, 1)

def test_command_get_player_pos_success(client, mock_minecraft):
    """'/command' への有効な getPlayerPos リクエストが成功するかテスト"""
    # mc.player.getPos() が返す値をモック
    mock_pos = mocker.MagicMock()
    mock_pos.x = 1.2
    mock_pos.y = 64.0
    mock_pos.z = -30.5
    mock_minecraft.player.getPos.return_value = mock_pos

    response = client.post('/command', json={
        "command": "getPlayerPos",
        "args": []
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['x'] == 1.2
    assert json_data['y'] == 64.0
    assert json_data['z'] == -30.5
    mock_minecraft.player.getPos.assert_called_once()

def test_command_set_player_pos_success(client, mock_minecraft):
    """'/command' への有効な setPlayerPos リクエストが成功するかテスト"""
    response = client.post('/command', json={
        "command": "setPlayerPos",
        "args": [10.5, 70.0, -25.8] # x, y, z
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == "Set player position to (10.5,70.0,-25.8)"
    # mc.player.setPos が正しい引数で呼び出されたか検証
    mock_minecraft.player.setPos.assert_called_once_with(10.5, 70.0, -25.8)

def test_command_get_block_success(client, mock_minecraft):
    """'/command' への有効な getBlock リクエストが成功するかテスト"""
    # mc.getBlock() が返す値をモック
    mock_minecraft.getBlock.return_value = 5 # 例としてオークの木材ID

    response = client.post('/command', json={
        "command": "getBlock",
        "args": [5, 10, 15] # x, y, z
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['block_id'] == 5
    # mc.getBlock が正しい引数で呼び出されたか検証
    mock_minecraft.getBlock.assert_called_once_with(5, 10, 15)

def test_command_set_blocks_success(client, mock_minecraft):
    """'/command' への有効な setBlocks リクエストが成功するかテスト (データなし)"""
    response = client.post('/command', json={
        "command": "setBlocks",
        "args": [0, 0, 0, 5, 5, 5, 1] # x1,y1,z1, x2,y2,z2, id
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert "Set blocks in range (0..5, 0..5, 0..5) to 1" in json_data['message']
    mock_minecraft.setBlocks.assert_called_once_with(0, 0, 0, 5, 5, 5, 1)

def test_command_set_blocks_with_data_success(client, mock_minecraft):
    """'/command' への有効な setBlocks リクエストが成功するかテスト (データあり)"""
    response = client.post('/command', json={
        "command": "setBlocks",
        "args": [1, 1, 1, 2, 2, 2, 35, 5] # x1,y1,z1, x2,y2,z2, id, data
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert "Set blocks in range (1..2, 1..2, 1..2) to 35:5" in json_data['message']
    mock_minecraft.setBlocks.assert_called_once_with(1, 1, 1, 2, 2, 2, 35, 5)

def test_command_get_height_success(client, mock_minecraft):
    """'/command' への有効な getHeight リクエストが成功するかテスト"""
    mock_minecraft.getHeight.return_value = 63
    response = client.post('/command', json={
        "command": "getHeight",
        "args": [100, -50] # x, z
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['height'] == 63
    mock_minecraft.getHeight.assert_called_once_with(100, -50)

def test_command_get_player_tile_pos_success(client, mock_minecraft):
    """'/command' への有効な getPlayerTilePos リクエストが成功するかテスト"""
    mock_pos = mocker.MagicMock()
    mock_pos.x = 5
    mock_pos.y = 64
    mock_pos.z = -20
    mock_minecraft.player.getTilePos.return_value = mock_pos
    response = client.post('/command', json={"command": "getPlayerTilePos", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['x'] == 5
    assert json_data['y'] == 64
    assert json_data['z'] == -20
    mock_minecraft.player.getTilePos.assert_called_once()

def test_command_get_player_direction_success(client, mock_minecraft):
    """'/command' への有効な getPlayerDirection リクエストが成功するかテスト"""
    mock_dir = mocker.MagicMock()
    mock_dir.x = 0.5
    mock_dir.y = 0.0
    mock_dir.z = 0.866
    mock_minecraft.player.getDirection.return_value = mock_dir
    response = client.post('/command', json={"command": "getPlayerDirection", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['x'] == 0.5
    assert json_data['y'] == 0.0
    assert json_data['z'] == 0.866
    mock_minecraft.player.getDirection.assert_called_once()

def test_command_get_player_rotation_success(client, mock_minecraft):
    """'/command' への有効な getPlayerRotation リクエストが成功するかテスト"""
    mock_minecraft.player.getRotation.return_value = 175.5
    response = client.post('/command', json={"command": "getPlayerRotation", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['rotation'] == 175.5
    mock_minecraft.player.getRotation.assert_called_once()

def test_command_get_player_pitch_success(client, mock_minecraft):
    """'/command' への有効な getPlayerPitch リクエストが成功するかテスト"""
    mock_minecraft.player.getPitch.return_value = -30.2
    response = client.post('/command', json={"command": "getPlayerPitch", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['pitch'] == -30.2
    mock_minecraft.player.getPitch.assert_called_once()

def test_command_world_setting_success(client, mock_minecraft):
    """'/command' への有効な worldSetting リクエストが成功するかテスト"""
    response = client.post('/command', json={
        "command": "worldSetting",
        "args": ["world_immutable", True]
    })
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert "Set world setting 'world_immutable' to True" in json_data['message']
    mock_minecraft.world.setting.assert_called_once_with("world_immutable", True)

def test_command_poll_block_hits_success(client, mock_minecraft, mocker):
    """'/command' への有効な pollBlockHits リクエストが成功するかテスト"""
    # モックイベントを作成
    mock_hit1 = mocker.MagicMock()
    mock_hit1.type = 4 # Block Hit Event Type
    mock_hit1.pos = mocker.MagicMock()
    mock_hit1.pos.x, mock_hit1.pos.y, mock_hit1.pos.z = 1, 2, 3
    mock_hit1.face = 1
    mock_hit1.entityId = 10
    mock_minecraft.events.pollBlockHits.return_value = [mock_hit1]

    response = client.post('/command', json={"command": "pollBlockHits", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['hits']) == 1
    hit_data = json_data['hits'][0]
    assert hit_data['type'] == 4
    assert hit_data['pos'] == {"x": 1, "y": 2, "z": 3}
    assert hit_data['face'] == 1
    assert hit_data['entityId'] == 10
    mock_minecraft.events.pollBlockHits.assert_called_once()

def test_command_poll_chat_posts_success(client, mock_minecraft, mocker):
    """'/command' への有効な pollChatPosts リクエストが成功するかテスト"""
    mock_post1 = mocker.MagicMock()
    mock_post1.type = 5 # Chat Post Event Type
    mock_post1.entityId = 11
    mock_post1.message = "Hello world"
    mock_minecraft.events.pollChatPosts.return_value = [mock_post1]

    response = client.post('/command', json={"command": "pollChatPosts", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert len(json_data['posts']) == 1
    post_data = json_data['posts'][0]
    assert post_data['type'] == 5
    assert post_data['entityId'] == 11
    assert post_data['message'] == "Hello world"
    mock_minecraft.events.pollChatPosts.assert_called_once()

def test_command_clear_events_success(client, mock_minecraft):
    """'/command' への有効な clearEvents リクエストが成功するかテスト"""
    response = client.post('/command', json={"command": "clearEvents", "args": []})
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == 'success'
    assert json_data['message'] == "Cleared all events"
    mock_minecraft.events.clearAll.assert_called_once()


# --- Error Handling Tests ---

def test_command_post_to_chat_missing_args(client, mock_minecraft):
    """postToChat で引数が不足している場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "postToChat",
        "args": []
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Missing message argument" in json_data['message']
    # mc.postToChat が呼び出されていないことを確認
    mock_minecraft.postToChat.assert_not_called()

def test_command_set_block_incorrect_args_count(client, mock_minecraft):
    """setBlock で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setBlock",
        "args": [10, 20, 30] # 引数が足りない
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Incorrect number of arguments" in json_data['message']
    mock_minecraft.setBlock.assert_not_called()

def test_command_set_block_invalid_args_type(client, mock_minecraft):
    """setBlock で引数の型が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setBlock",
        "args": [10, 20, "abc", 1] # 文字列が含まれている
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Invalid arguments for setBlock" in json_data['message']
    mock_minecraft.setBlock.assert_not_called()

def test_command_get_player_pos_with_args(client, mock_minecraft):
    """getPlayerPos に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "getPlayerPos",
        "args": [1] # 不要な引数
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "getPlayerPos does not take any arguments" in json_data['message']
    mock_minecraft.player.getPos.assert_not_called()

def test_command_set_player_pos_incorrect_args_count(client, mock_minecraft):
    """setPlayerPos で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setPlayerPos",
        "args": [10.0, 20.0] # 引数が足りない
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Incorrect number of arguments for setPlayerPos" in json_data['message']
    mock_minecraft.player.setPos.assert_not_called()

def test_command_set_player_pos_invalid_args_type(client, mock_minecraft):
    """setPlayerPos で引数の型が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setPlayerPos",
        "args": [10.0, "abc", 30.0] # 文字列が含まれている
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Invalid arguments for setPlayerPos" in json_data['message']
    mock_minecraft.player.setPos.assert_not_called()

def test_command_get_block_incorrect_args_count(client, mock_minecraft):
    """getBlock で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "getBlock",
        "args": [10, 20] # 引数が足りない
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Incorrect number of arguments for getBlock" in json_data['message']
    mock_minecraft.getBlock.assert_not_called()

def test_command_get_block_invalid_args_type(client, mock_minecraft):
    """getBlock で引数の型が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "getBlock",
        "args": ["a", "b", "c"] # 文字列
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Invalid arguments for getBlock" in json_data['message']
    mock_minecraft.getBlock.assert_not_called()

# --- Additional Error Tests for New Commands ---

def test_command_set_blocks_incorrect_args_count(client, mock_minecraft):
    """setBlocks で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setBlocks",
        "args": [0, 0, 0, 1, 1, 1] # 6 args, expected 7 or 8
    })
    assert response.status_code == 400
    assert b"Incorrect number of arguments for setBlocks" in response.data
    mock_minecraft.setBlocks.assert_not_called()

def test_command_set_blocks_invalid_args_type(client, mock_minecraft):
    """setBlocks で引数の型が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "setBlocks",
        "args": [0, 0, 0, 1, 1, "a", 1] # "a" is not int
    })
    assert response.status_code == 400
    assert b"Invalid arguments for setBlocks" in response.data
    mock_minecraft.setBlocks.assert_not_called()

def test_command_get_height_incorrect_args_count(client, mock_minecraft):
    """getHeight で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getHeight", "args": [1]})
    assert response.status_code == 400
    assert b"Incorrect number of arguments for getHeight" in response.data
    mock_minecraft.getHeight.assert_not_called()

def test_command_get_height_invalid_args_type(client, mock_minecraft):
    """getHeight で引数の型が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getHeight", "args": ["a", "b"]})
    assert response.status_code == 400
    assert b"Invalid arguments for getHeight" in response.data
    mock_minecraft.getHeight.assert_not_called()

def test_command_get_player_tile_pos_with_args(client, mock_minecraft):
    """getPlayerTilePos に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getPlayerTilePos", "args": [1]})
    assert response.status_code == 400
    assert b"getPlayerTilePos does not take any arguments" in response.data
    mock_minecraft.player.getTilePos.assert_not_called()

def test_command_get_player_direction_with_args(client, mock_minecraft):
    """getPlayerDirection に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getPlayerDirection", "args": [1]})
    assert response.status_code == 400
    assert b"getPlayerDirection does not take any arguments" in response.data
    mock_minecraft.player.getDirection.assert_not_called()

def test_command_get_player_rotation_with_args(client, mock_minecraft):
    """getPlayerRotation に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getPlayerRotation", "args": [1]})
    assert response.status_code == 400
    assert b"getPlayerRotation does not take any arguments" in response.data
    mock_minecraft.player.getRotation.assert_not_called()

def test_command_get_player_pitch_with_args(client, mock_minecraft):
    """getPlayerPitch に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "getPlayerPitch", "args": [1]})
    assert response.status_code == 400
    assert b"getPlayerPitch does not take any arguments" in response.data
    mock_minecraft.player.getPitch.assert_not_called()

def test_command_world_setting_incorrect_args_count(client, mock_minecraft):
    """worldSetting で引数の数が違う場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "worldSetting", "args": ["world_immutable"]})
    assert response.status_code == 400
    assert b"Incorrect number of arguments for worldSetting" in response.data
    mock_minecraft.world.setting.assert_not_called()

def test_command_world_setting_invalid_status(client, mock_minecraft):
    """worldSetting で status が不正な場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "worldSetting", "args": ["world_immutable", "maybe"]})
    assert response.status_code == 400
    assert b"Invalid status for worldSetting" in response.data
    mock_minecraft.world.setting.assert_not_called()

def test_command_poll_block_hits_with_args(client, mock_minecraft):
    """pollBlockHits に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "pollBlockHits", "args": [1]})
    assert response.status_code == 400
    assert b"pollBlockHits does not take any arguments" in response.data
    mock_minecraft.events.pollBlockHits.assert_not_called()

def test_command_poll_chat_posts_with_args(client, mock_minecraft):
    """pollChatPosts に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "pollChatPosts", "args": [1]})
    assert response.status_code == 400
    assert b"pollChatPosts does not take any arguments" in response.data
    mock_minecraft.events.pollChatPosts.assert_not_called()

def test_command_clear_events_with_args(client, mock_minecraft):
    """clearEvents に引数が渡された場合にエラーを返すかテスト"""
    response = client.post('/command', json={"command": "clearEvents", "args": [1]})
    assert response.status_code == 400
    assert b"clearEvents does not take any arguments" in response.data
    mock_minecraft.events.clearAll.assert_not_called()

# --- Existing Error Tests ---

def test_command_unknown_command(client, mock_minecraft):
    """未知のコマンドが指定された場合にエラーを返すかテスト"""
    response = client.post('/command', json={
        "command": "unknownAction",
        "args": []
    })
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Unknown command: unknownAction" in json_data['message']

def test_command_minecraft_not_connected(client, mocker):
    """Minecraft に接続されていない場合にエラーを返すかテスト"""
    # mc を None にモックする
    mocker.patch('app.mc', None)
    response = client.post('/command', json={
        "command": "postToChat",
        "args": ["Test"]
    })
    assert response.status_code == 503 # Service Unavailable
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Minecraft not connected" in json_data['message']

def test_command_invalid_json(client):
    """無効な JSON データが送信された場合にエラーを返すかテスト"""
    response = client.post('/command', data="this is not json", content_type="application/json")
    assert response.status_code == 400
    json_data = response.get_json()
    assert json_data['status'] == 'error'
    assert "Invalid JSON" in json_data['message']

# Minecraft 接続時のエラーをシミュレートするテスト (オプション)
def test_minecraft_connection_error(mocker, client):
    """Minecraft 接続時に例外が発生するケースをテスト"""
    # Minecraft.create が例外を送出するようにモック
    mocker.patch('app.Minecraft.create', side_effect=Exception("Connection refused"))
    # mc を None に設定 (接続失敗時の挙動)
    mocker.patch('app.mc', None)

    # アプリケーションの初期化を再度トリガーする必要があるかもしれないが、
    # ここでは /command エンドポイントが mc is None を正しく処理するか確認
    response = client.post('/command', json={"command": "postToChat", "args": ["Test"]})
    assert response.status_code == 503
    assert b"Minecraft not connected" in response.data
