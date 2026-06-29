"""test 命令 - 自动测试 Dify 工作流（支持批量测试和文件输入）"""

import json
import mimetypes
import sys
import time
from datetime import datetime
from pathlib import Path

import requests
import yaml

from ..auth import login_with_server
from ..config import find_server_by_url, get_server_config, load_config
from ..utils import extract_app_id, extract_base_url, is_url


def parse_yml_inputs(yml_path: Path) -> list[dict]:
    """从 YML 文件解析输入变量"""
    content = yml_path.read_text(encoding="utf-8")
    data = yaml.safe_load(content)

    workflow = data.get("workflow", {})
    graph = workflow.get("graph", {})
    nodes = graph.get("nodes", [])

    inputs = []
    for node in nodes:
        node_data = node.get("data", {})
        if node_data.get("type") == "start":
            for var in node_data.get("variables", []):
                inputs.append({
                    "variable": var.get("variable", ""),
                    "label": var.get("label", ""),
                    "type": var.get("type", "text"),
                    "required": var.get("required", False),
                    "max_length": var.get("max_length", 5000),
                    "options": var.get("options", []),
                    "default": var.get("default", "")
                })

    return inputs


def generate_test_data(inputs: list[dict], custom_inputs: dict = None, index: int = 0) -> dict:
    """根据输入变量生成测试数据（支持批量生成）"""
    custom_inputs = custom_inputs or {}
    test_data = {}

    for var in inputs:
        name = var["variable"]
        var_type = var["type"]

        if name in custom_inputs:
            test_data[name] = custom_inputs[name]
            continue

        if var_type == "paragraph" or var_type == "text-input":
            test_data[name] = generate_text_input_batch(name, var.get("label", ""), index)
        elif var_type == "number":
            test_data[name] = str(100 + index * 10)
        elif var_type == "select":
            options = var.get("options", [])
            if options:
                test_data[name] = options[index % len(options)]
            else:
                test_data[name] = "option1"
        elif var_type in ["file", "file-list"]:
            continue
        else:
            test_data[name] = f"测试-{name}-{index + 1}"

    return test_data


def generate_text_input_batch(name: str, label: str, index: int) -> str:
    """批量生成不同的文本测试数据"""
    title_pool = [
        "人工智能的未来", "春天的校园", "我的梦想", "一次难忘的旅行",
        "科技改变生活", "环境保护从我做起", "读书的乐趣", "友谊的力量",
        "未来的城市", "健康生活方式", "传统文化的魅力", "创新与突破",
        "团队合作的重要性", "面对困难的勇气", "感恩的心",
    ]
    question_pool = [
        "什么是机器学习？", "如何学习编程？", "什么是区块链？",
        "如何提高工作效率？", "什么是人工智能？", "如何保持健康？",
        "什么是云计算？", "如何学习外语？", "什么是大数据？", "如何培养好习惯？",
    ]
    content_pool = [
        "请简述气候变化对地球环境的影响，并提出一些可行的解决方案。",
        "请介绍互联网的发展历程及其对现代社会的影响。",
        "请分析人工智能在医疗领域的应用前景。",
        "请讨论远程工作的优缺点及未来发展趋势。",
        "请描述可再生能源的种类及其重要性。",
    ]

    name_lower = name.lower()
    label_lower = label.lower() if label else ""

    title_keywords = ["title", "主题", "标题", "topic", "subject"]
    for kw in title_keywords:
        if kw in name_lower or kw in label_lower:
            return title_pool[index % len(title_pool)]

    question_keywords = ["question", "问题", "query", "ask"]
    for kw in question_keywords:
        if kw in name_lower or kw in label_lower:
            return question_pool[index % len(question_pool)]

    content_keywords = ["content", "内容", "text", "description", "描述"]
    for kw in content_keywords:
        if kw in name_lower or kw in label_lower:
            return content_pool[index % len(content_pool)]

    return title_pool[index % len(title_pool)]


def upload_file(base_url: str, api_key: str, file_path: str) -> str:
    """上传文件并返回 file_id"""
    headers = {'Authorization': f'Bearer {api_key}'}
    # 必须显式指定 MIME 类型：2-tuple 会让 part 的 Content-Type 退化为
    # application/octet-stream，Dify 会以 unsupported_file_type (415) 拒绝
    mime, _ = mimetypes.guess_type(file_path)
    with open(file_path, 'rb') as f:
        files = {'file': (Path(file_path).name, f, mime or 'application/octet-stream')}
        resp = requests.post(f'{base_url}/v1/files/upload', headers=headers, files=files, timeout=30)

    if resp.status_code != 201:
        print(f"[ERROR] 文件上传失败：{resp.status_code}")
        return None

    return resp.json().get('id')


def get_test_files(test_data_dir: str) -> list[str]:
    """从测试数据文件夹获取文件列表"""
    if not test_data_dir or not Path(test_data_dir).exists():
        return []

    supported_ext = ['.png', '.jpg', '.jpeg', '.gif', '.webp', '.svg', '.pdf', '.txt', '.md']
    files = []
    for f in Path(test_data_dir).iterdir():
        if f.is_file() and f.suffix.lower() in supported_ext:
            files.append(str(f))

    return sorted(files)


def get_or_create_api_key(session: requests.Session, base_url: str, app_id: str) -> str:
    """获取或创建 API Key"""
    token = session.cookies.get('access_token')
    csrf = session.cookies.get('csrf_token')
    if token:
        session.headers.update({'Authorization': f'Bearer {token}'})
    if csrf:
        session.headers.update({'X-CSRF-Token': csrf})

    resp = session.get(f"{base_url}/console/api/apps/{app_id}/api-keys", timeout=15)
    if resp.status_code == 200:
        data = resp.json()
        api_keys = data.get("data", [])
        if api_keys:
            return api_keys[0]["token"]

    resp = session.post(
        f"{base_url}/console/api/apps/{app_id}/api-keys",
        json={"name": "cli-test-key"},
        timeout=15
    )
    if resp.status_code == 201:
        data = resp.json()
        return data["token"]

    print(f"[ERROR] 无法获取/创建 API Key: HTTP {resp.status_code}")
    sys.exit(1)


def run_workflow(base_url: str, app_id: str, api_key: str, inputs: dict) -> dict:
    """运行工作流"""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "inputs": inputs,
        "user": "cli-test"
    }

    resp = requests.post(f"{base_url}/v1/workflows/run", headers=headers, json=data, timeout=120)
    if resp.status_code != 200:
        return {"error": True, "status": resp.status_code, "message": resp.text}

    result = resp.json()
    data_obj = result.get("data", {})

    return {
        "task_id": result.get("task_id", ""),
        "outputs": data_obj.get("outputs", {}),
        "total_tokens": data_obj.get("total_tokens", 0),
        "total_steps": data_obj.get("total_steps", 0),
        "elapsed_time": data_obj.get("elapsed_time", 0),
    }


def parse_custom_inputs(input_str: str) -> dict:
    """解析自定义输入字符串"""
    if not input_str:
        return {}

    result = {}
    pairs = input_str.split(",")
    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            result[key.strip()] = value.strip()
        else:
            print(f"[WARN] 忽略无效的输入格式：{pair}")

    return result


def generate_report(results: list[dict], yml_path: str, output_path: str = None) -> str:
    """生成 Markdown 格式的测试报告"""
    total = len(results)
    success = sum(1 for r in results if not r.get("error"))
    failed = total - success

    total_time = sum(r.get("duration", 0) for r in results)
    avg_time = total_time / total if total > 0 else 0

    total_tokens = sum(r.get("total_tokens", 0) for r in results)
    avg_tokens = total_tokens / total if total > 0 else 0

    def pct(n):
        return f"{n / total * 100:.1f}%" if total > 0 else "0.0%"

    def oneline(s: str) -> str:
        """压缩换行，避免破坏 Markdown 行内结构"""
        return str(s).replace("\n", " ").replace("\r", " ")

    report = []
    report.append("# Dify 工作流测试报告")
    report.append("")
    report.append(f"- **测试文件**：`{yml_path}`")
    report.append(f"- **测试时间**：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"- **测试数量**：{total}")
    report.append("")
    report.append("## 测试统计")
    report.append("")
    report.append("| 指标 | 值 |")
    report.append("| --- | --- |")
    report.append(f"| 成功 | {success} ({pct(success)}) |")
    report.append(f"| 失败 | {failed} ({pct(failed)}) |")
    report.append(f"| 总耗时 | {total_time:.2f}s |")
    report.append(f"| 平均耗时 | {avg_time:.2f}s |")
    report.append(f"| 总 Token 消耗 | {total_tokens} |")
    report.append(f"| 平均 Token 消耗 | {avg_tokens:.0f} |")
    report.append("")
    report.append("## 详细结果")
    report.append("")

    for i, r in enumerate(results, 1):
        status = "✅ 成功" if not r.get("error") else "❌ 失败"
        tokens = r.get("total_tokens", 0)
        report.append(f"### 测试 #{i} {status}")
        report.append("")
        report.append(f"- **耗时**：{r.get('duration', 0):.2f}s")
        if tokens:
            report.append(f"- **Token**：{tokens}")
        report.append(f"- **任务 ID**：`{r.get('task_id', 'N/A')}`")
        inputs_preview = oneline(json.dumps(r.get("inputs", {}), ensure_ascii=False))[:100]
        report.append(f"- **输入**：`{inputs_preview}`")

        if r.get("error"):
            err_preview = oneline(r.get("message", "未知错误"))[:200]
            report.append(f"- **错误**：{err_preview}")
        else:
            outputs = r.get("outputs", {})
            if outputs:
                report.append("- **输出**：")
                for key, value in outputs.items():
                    preview = oneline(value)[:150]
                    report.append(f"  - `{key}`：{preview}")
        report.append("")

    report_text = "\n".join(report)

    if output_path:
        Path(output_path).write_text(report_text, encoding="utf-8")
        print(f"\n[INFO] 报告已保存：{output_path}")

    return report_text


def cmd_test(args):
    """执行 test 子命令"""
    config = load_config()
    yml_path = Path(args.yml_path)

    if not yml_path.exists():
        print(f"[ERROR] 文件不存在：{yml_path}")
        sys.exit(1)

    print(f"[INFO] 测试文件：{yml_path}")
    print("=" * 60)

    inputs = parse_yml_inputs(yml_path)
    if not inputs:
        print("[ERROR] 未找到输入变量（start 节点没有 variables）")
        sys.exit(1)

    print(f"\n[INFO] 发现 {len(inputs)} 个输入变量:")
    for var in inputs:
        required = "必填" if var.get("required") else "选填"
        print(f"  - {var['variable']} ({var['type']}, {required})")

    count = args.count if args.count else 1
    print(f"\n[INFO] 测试数量：{count}")

    custom_inputs = parse_custom_inputs(args.input) if args.input else {}

    if args.url:
        base_url = extract_base_url(args.url)
        app_id = extract_app_id(args.url)
    else:
        from ..mapping import lookup_mapping
        result = lookup_mapping(yml_path.name)
        if result:
            server_name = result["server"]
            app_id = result["app_id"]
            _, server_config = get_server_config(config, server_name)
            base_url = server_config["base_url"]
            print(f"\n[INFO] 从映射查找：server={server_name}, app_id={app_id}")
        else:
            print("[ERROR] 请提供 --url 参数或先部署应用以创建映射")
            sys.exit(1)

    print(f"\n[INFO] 服务器：{base_url}")
    print("[INFO] 登录中...")

    session = requests.Session()
    server_name = find_server_by_url(config, base_url)
    if not server_name:
        print(f"[ERROR] 未找到匹配的服务器配置：{base_url}")
        sys.exit(1)

    _, server_config = get_server_config(config, server_name)
    login_with_server(session, server_config)
    print("[OK] 登录成功")

    api_key = get_or_create_api_key(session, base_url, app_id)
    print(f"[OK] API Key: {api_key[:20]}...")

    test_files = []
    if args.test_data:
        test_files = get_test_files(args.test_data)
        if test_files:
            print(f"\n[INFO] 测试数据文件夹：{args.test_data}")
            print(f"[INFO] 找到 {len(test_files)} 个测试文件")
            for f in test_files[:5]:
                print(f"  - {Path(f).name}")
            if len(test_files) > 5:
                print(f"  ... 还有 {len(test_files) - 5} 个文件")
        else:
            print(f"\n[WARN] 测试数据文件夹为空或不存在：{args.test_data}")

    print(f"\n[INFO] 开始批量测试 ({count} 个用例)...")
    print("-" * 60)

    results = []
    for i in range(count):
        test_data = generate_test_data(inputs, custom_inputs, i)

        has_file_input = any(v.get('type') in ['file', 'file-list'] for v in inputs)
        if has_file_input and test_files:
            file_idx = i % len(test_files)
            file_path = test_files[file_idx]
            print(f"\n[INFO] 上传文件：{Path(file_path).name}")
            file_id = upload_file(base_url, api_key, file_path)
            if file_id:
                for var in inputs:
                    if var.get('type') in ['file', 'file-list']:
                        test_data[var['variable']] = [
                            {'type': 'image', 'transfer_method': 'local_file', 'upload_file_id': file_id}
                        ]
                print(f"[OK] 文件上传成功")
            else:
                print(f"[ERROR] 文件上传失败")

        print(f"\n【测试 #{i + 1}/{count}】")
        for key, value in test_data.items():
            preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
            print(f"  {key}: {preview}")

        start_time = time.time()
        result = run_workflow(base_url, app_id, api_key, test_data)
        duration = time.time() - start_time

        test_result = {
            "index": i + 1,
            "inputs": test_data,
            "duration": duration,
        }

        if result.get("error"):
            test_result["error"] = True
            test_result["message"] = result.get("message", "未知错误")
            print(f"  ❌ 失败：{result.get('message', '未知错误')[:100]}")
        else:
            test_result["error"] = False
            test_result["task_id"] = result.get("task_id", "N/A")
            test_result["outputs"] = result.get("outputs", {})
            test_result["total_tokens"] = result.get("total_tokens", 0)
            test_result["total_steps"] = result.get("total_steps", 0)
            test_result["elapsed_time"] = result.get("elapsed_time", 0)
            print(f"  ✅ 成功 (耗时：{duration:.2f}s, tokens: {result.get('total_tokens', 0)})")

            outputs = result.get("outputs", {})
            for key, value in outputs.items():
                preview = str(value)[:80] + "..." if len(str(value)) > 80 else str(value)
                print(f"  输出 [{key}]: {preview}")

        results.append(test_result)

        if i < count - 1:
            time.sleep(0.5)

    print("\n" + "=" * 60)
    report = generate_report(results, str(yml_path), args.report)
    print(report)

    failed = sum(1 for r in results if r.get("error"))
    if failed > 0:
        sys.exit(1)
