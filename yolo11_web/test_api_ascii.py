"""
纯ASCII字符API测试
"""

import requests
import json
import os


def test_api():
    """测试API"""
    print("Testing API endpoints...")

    base_url = "http://localhost:8000"
    test_image_path = "bus.jpg"

    if not os.path.exists(test_image_path):
        print(f"Error: Test image not found: {test_image_path}")
        return False

    # 测试端点
    endpoints = [
        {
            "name": "MCP Agent",
            "url": f"{base_url}/api/agent/mcp/process",
            "data": {
                "user_question": "Detect objects in this image",
                "image_path": os.path.abspath(test_image_path),
            },
        },
        {
            "name": "LangGraph",
            "url": f"{base_url}/api/langgraph/process",
            "data": {
                "user_question": "Detect objects in this image",
                "image_path": os.path.abspath(test_image_path),
            },
        },
    ]

    results = []

    for endpoint in endpoints:
        print(f"\nTesting: {endpoint['name']}")
        print(f"URL: {endpoint['url']}")

        try:
            print(f"Data: {json.dumps(endpoint['data'], indent=2)}")
            response = requests.post(endpoint["url"], json=endpoint["data"], timeout=30)

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                print("SUCCESS")
                try:
                    result = response.json()
                    print(f"Response: {json.dumps(result, indent=2)[:500]}...")
                except:
                    print(f"Response text: {response.text[:500]}...")
                results.append((endpoint["name"], True))
            else:
                print("FAILED")
                print(f"Error: {response.text[:500]}")
                results.append((endpoint["name"], False))

        except requests.exceptions.Timeout:
            print("TIMEOUT (30s)")
            results.append((endpoint["name"], False))
        except requests.exceptions.ConnectionError:
            print("CONNECTION ERROR")
            results.append((endpoint["name"], False))
        except Exception as e:
            print(f"ERROR: {type(e).__name__}: {str(e)}")
            results.append((endpoint["name"], False))

    # 汇总结果
    print("\n=== Results ===")
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        print(f"{test_name}: {status}")
        if success:
            passed += 1

    print(f"\nTotal: {passed}/{len(results)} tests passed")

    return passed > 0


def test_health():
    """测试健康检查"""
    print("\n=== Health Checks ===")

    base_url = "http://localhost:8000"
    endpoints = [
        ("Root", "/"),
        ("Docs", "/docs"),
        ("Health", "/api/health"),
    ]

    for name, endpoint in endpoints:
        print(f"Testing: {name} ({endpoint})")
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "OK" if response.status_code == 200 else "FAIL"
            print(f"  Status: {status} {response.status_code}")
        except Exception as e:
            print(f"  ERROR: {type(e).__name__}")


if __name__ == "__main__":
    print("Starting API tests...")

    # 检查服务器
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        print(f"Server status: RUNNING (status: {response.status_code})")
    except:
        print("Server status: NOT RUNNING")
        print("Please start server: python main.py")
        exit(1)

    # 运行测试
    test_health()
    api_ok = test_api()

    if not api_ok:
        print("\nWARNING: Detection API has issues")
        print("1. Check server logs for errors")
        print("2. Verify detection service loaded correctly")
        print("3. Check API route configuration")

    print("\nTesting complete")
