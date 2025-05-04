# --- Build Stage ---
# Pythonの公式イメージをベースイメージとして使用
# Raspberry Pi (ARM64)で動作するイメージを選択
FROM python:3.11-slim as builder

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピー
COPY requirements.txt .

# アプリケーションとテストの依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードとテストコードをコピー
COPY app.py .
COPY test_app.py .

# テストを実行 (ここで失敗するとビルドが停止する)
RUN pytest

# --- Runtime Stage ---
FROM python:3.11-slim as runtime

# 作業ディレクトリを設定
WORKDIR /app

# ランタイムに必要な依存関係のみをインストール
# requirements.txt から pytest と pytest-mock を除外するか、
# ランタイム用の requirements_runtime.txt を別途用意するのが理想的ですが、
# ここでは簡単のため、requirements.txt をそのまま使います。
# 本番環境では、テスト用ライブラリを除いたリストを使うことを推奨します。
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ビルドステージからアプリケーションコードのみをコピー
COPY --from=builder /app/app.py .

# Flaskアプリケーションが使用するポートを公開
EXPOSE 5000

# コンテナ起動時に実行するコマンド
CMD ["python", "app.py"]
