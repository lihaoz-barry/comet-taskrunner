"""
AI Task API Test Script

This script demonstrates how to call the new AI Task API.
It's a simple example for testing and understanding the API.

Usage:
    python test_ai_task.py
"""

import requests
import json
import time

# Backend API URL
BACKEND_URL = "http://127.0.0.1:5000"

def test_ai_task():
    """
    Test the AI Task API endpoint.
    
    This will:
    1. Create an AI task
    2. Monitor its status
    3. Print progress updates
    """
    print("=" * 60)
    print("AI Task API Test")
    print("=" * 60)
    
    # Define the AI instruction
    instruction = "请帮我总结这个文档的主要内容，并列出关键点"
    
    # Optional: Custom coordinates (adjust based on your screen resolution)
    # If not provided, default coordinates will be used
    coordinates = {
        "assistant_button": (100, 100),   # X, Y position
        "task_input_box": (500, 300),
        "send_button": (800, 500)
    }
    
    print(f"\n发送AI任务...")
    print(f"指令: {instruction}")
    
    # Step 1: Execute AI task
    try:
        response = requests.post(
            f"{BACKEND_URL}/execute/ai",
            json={
                "instruction": instruction,
                # "coordinates": coordinates  # Uncomment to use custom coordinates
            }
        )
        
        if response.status_code != 200:
            print(f"错误: {response.text}")
            return
        
        data = response.json()
        task_id = data['task_id']
        process_id = data['process_id']
        
        print(f"\n✓ AI任务已启动!")
        print(f"  Task ID: {task_id}")
        print(f"  Process ID: {process_id}")
        print(f"  Type: {data['task_type']}")
        
    except Exception as e:
        print(f"连接错误: {e}")
        return
    
    # Step 2: Monitor status
    print(f"\n监控任务状态...")
    print("(按 Ctrl+C 停止监控)\n")
    
    try:
        while True:
            # Poll status every 2 seconds
            time.sleep(2)
            
            response = requests.get(f"{BACKEND_URL}/status/{task_id}")
            if response.status_code == 200:
                status_data = response.json()
                status = status_data['status']
                
                print(f"[{time.strftime('%H:%M:%S')}] 状态: {status}")
                
                if status == "done":
                    print("\n✓ 任务完成!")
                    break
                elif status == "failed":
                    print(f"\n✗ 任务失败: {status_data.get('error_message', 'Unknown error')}")
                    break
            else:
                print(f"无法获取状态: {response.text}")
                break
                
    except KeyboardInterrupt:
        print("\n\n监控已停止")
    
    # Show final task details
    print(f"\n最终任务信息:")
    response = requests.get(f"{BACKEND_URL}/status/{task_id}")
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2, ensure_ascii=False))


def test_url_task():
    """
    Test the URL Task API endpoint (for comparison).
    
    This demonstrates the simpler URL task for reference.
    """
    print("=" * 60)
    print("URL Task API Test")
    print("=" * 60)
    
    url = "https://www.google.com"
    
    print(f"\n发送URL任务...")
    print(f"URL: {url}")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/execute/url",
            json={"url": url}
        )
        
        if response.status_code != 200:
            print(f"错误: {response.text}")
            return
        
        data = response.json()
        task_id = data['task_id']
        
        print(f"\n✓ URL任务已启动!")
        print(f"  Task ID: {task_id}")
        print(f"  Process ID: {data['process_id']}")
        print(f"  Type: {data['task_type']}")
        
        # Monitor briefly
        print(f"\n监控10秒...")
        for i in range(5):
            time.sleep(2)
            response = requests.get(f"{BACKEND_URL}/status/{task_id}")
            if response.status_code == 200:
                status = response.json()['status']
                print(f"[{i*2}s] 状态: {status}")
                if status != "running":
                    break
        
    except Exception as e:
        print(f"错误: {e}")


def get_all_jobs():
    """Get and display all current jobs."""
    print("=" * 60)
    print("所有任务")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BACKEND_URL}/jobs")
        if response.status_code == 200:
            jobs = response.json()
            print(f"\n总共 {len(jobs)} 个任务:\n")
            for task_id, job in jobs.items():
                print(f"Task ID: {task_id}")
                print(f"  Type: {job['task_type']}")
                print(f"  Status: {job['status']}")
                if job['task_type'] == 'url':
                    print(f"  URL: {job.get('url', 'N/A')}")
                else:
                    inst = job.get('instruction', '')
                    print(f"  Instruction: {inst[:50]}...")
                print()
        else:
            print(f"错误: {response.text}")
    except Exception as e:
        print(f"错误: {e}")


if __name__ == "__main__":
    import sys
    
    print("\nComet Task Runner - API Test\n")
    print("选择测试:")
    print("1. AI Task (AI助手任务)")
    print("2. URL Task (URL任务)")
    print("3. Get All Jobs (查看所有任务)")
    
    choice = input("\n输入选项 (1/2/3): ").strip()
    
    if choice == "1":
        test_ai_task()
    elif choice == "2":
        test_url_task()
    elif choice == "3":
        get_all_jobs()
    else:
        print("无效选项")
