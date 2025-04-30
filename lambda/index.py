import json
import os
import re
import urllib3

API_ENDPOINT = "http://0.0.0.0:8501"

http = urllib3.PoolManager()

def lambda_handler(event, context):
    try:
        print("Received event:", json.dumps(event))

        # Cognitoで認証されたユーザー情報を取得（任意）
        user_info = None
        if 'requestContext' in event and 'authorizer' in event['requestContext']:
            user_info = event['requestContext']['authorizer']['claims']
            print(f"Authenticated user: {user_info.get('email') or user_info.get('cognito:username')}")

        # リクエストボディの解析
        body = json.loads(event['body'])
        message = body['message']
        conversation_history = body.get('conversationHistory', [])

        # FastAPI へのリクエストペイロードを作成
        request_payload = {
            "message": message,
            "conversationHistory": conversation_history
        }

        print("Calling FastAPI endpoint:", API_ENDPOINT)

        # FastAPI エンドポイントに POST リクエストを送信
        response = http.request(
            "POST",
            API_ENDPOINT,
            body=json.dumps(request_payload),
            headers={'Content-Type': 'application/json'}
        )

        if response.status != 200:
            raise Exception(f"API returned error: {response.status} - {response.data.decode()}")

        # FastAPI からの応答を解析
        response_data = json.loads(response.data.decode("utf-8"))
        assistant_response = response_data.get("message")

        # 会話履歴が返される場合はそれを取得
        updated_history = response_data.get("conversationHistory", [])

        # レスポンスを返す
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": assistant_response,
                "conversationHistory": updated_history
            })
        }

    except Exception as e:
        print("Error:", str(e))
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
