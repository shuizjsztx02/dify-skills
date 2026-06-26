"""认证模块"""

import base64
import sys

import requests


def login(session: requests.Session, base_url: str, email: str, password: str):
    """登录获取 session cookie（access_token + csrf_token）"""
    encoded_password = base64.b64encode(password.encode()).decode()
    resp = session.post(
        f"{base_url}/console/api/login",
        json={"email": email, "password": encoded_password},
        timeout=15,
    )
    if resp.status_code != 200:
        print(f"[ERROR] 登录失败: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)
    if "access_token" not in session.cookies:
        data = resp.json().get("data", {})
        token = data.get("access_token")
        if token:
            session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print(f"[ERROR] 登录响应中未找到 access_token")
            sys.exit(1)
    csrf = session.cookies.get("csrf_token")
    if csrf:
        session.headers.update({"X-CSRF-Token": csrf})


def login_with_server(session: requests.Session, server_config: dict):
    """使用服务器配置登录"""
    login(session, server_config["base_url"], server_config["email"], server_config["password"])
