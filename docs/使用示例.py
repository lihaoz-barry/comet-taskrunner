"""
示例：在其他项目中使用Task组件

这个文件展示如何将tasks组件集成到完全不同的项目中。
"""

# ============================================================================
# 示例 1: 简单的自动化脚本（无框架）
# ============================================================================

def example_simple_script():
    """
    最简单的使用方式：直接import和使用
    适用于：CLI工具、自动化脚本、Jupyter Notebook
    """
    from tasks import URLTask, AITask
    import time
    
    print("=== 示例1：简单脚本 ===\n")
    
    # 创建URL任务
    task = URLTask(url="https://www.google.com")
    print(f"创建任务: {task.task_id}")
    
    # 执行任务
    pid = task.execute(comet_path=r"C:\path\to\comet.exe")
    task.start(pid)
    print(f"启动进程: {pid}")
    
    # 等待完成
    while not task.check_completion():
        print(".", end="", flush=True)
        time.sleep(1)
    
    result = task.complete()
    print(f"\n✓ 完成! 耗时: {result.data.get('duration_seconds')}秒")


# ============================================================================
# 示例 2: 自定义的FastAPI服务
# ============================================================================

def example_fastapi_service():
    """
    在FastAPI中使用Task组件
    完全独立的API服务，不依赖原项目的Flask backend
    """
    from fastapi import FastAPI, BackgroundTasks
    from fastapi.responses import JSONResponse
    from tasks import URLTask, AITask, TaskStatus
    import uvicorn
    
    app = FastAPI(title="My Browser Automation API")
    
    # 简单的内存存储（生产环境应该用数据库）
    tasks_db = {}
    
    @app.post("/automate/url")
    async def automate_url(url: str, background_tasks: BackgroundTasks):
        """使用URLTask组件的API endpoint"""
        # 1. 创建Task组件
        task = URLTask(url=url)
        
        # 2. 执行
        pid = task.execute(comet_path="/path/to/browser")
        task.start(pid)
        
        # 3. 存储
        tasks_db[task.task_id] = task
        
        # 4. 后台监控
        background_tasks.add_task(monitor_task, task.task_id)
        
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "pid": pid
        }
    
    @app.post("/automate/ai")
    async def automate_ai(instruction: str):
        """使用AITask组件的API endpoint"""
        task = AITask(instruction=instruction)
        pid = task.execute(comet_path="/path/to/browser")
        task.start(pid)
        
        tasks_db[task.task_id] = task
        
        return {
            "task_id": task.task_id,
            "type": "ai",
            "instruction": instruction
        }
    
    @app.get("/tasks/{task_id}")
    async def get_task_status(task_id: str):
        """查询任务状态"""
        task = tasks_db.get(task_id)
        if not task:
            return JSONResponse(
                status_code=404,
                content={"error": "Task not found"}
            )
        
        # 使用Task的方法检查完成
        if task.check_completion():
            task.complete()
        
        return task.to_dict()
    
    async def monitor_task(task_id: str):
        """后台任务监控"""
        import asyncio
        while True:
            task = tasks_db.get(task_id)
            if not task or task.status != TaskStatus.RUNNING:
                break
            
            if task.check_completion():
                task.complete()
                break
            
            await asyncio.sleep(5)
    
    # 运行服务器
    # uvicorn.run(app, host="0.0.0.0", port=8000)


# ============================================================================
# 示例 3: Django项目集成
# ============================================================================

def example_django_integration():
    """
    在Django项目中使用Task组件
    
    文件结构:
    myproject/
    ├── automation/       (Django app)
    │   ├── models.py
    │   ├── views.py
    │   └── tasks.py
    └── tasks/           (复制过来的组件)
        ├── __init__.py
        ├── base_task.py
        ├── url_task.py
        └── ai_task.py
    """
    
    # === automation/models.py ===
    """
    from django.db import models
    
    class BrowserTask(models.Model):
        task_id = models.CharField(max_length=100, unique=True)
        task_type = models.CharField(max_length=20)
        url = models.URLField(null=True, blank=True)
        instruction = models.TextField(null=True, blank=True)
        status = models.CharField(max_length=20)
        process_id = models.IntegerField(null=True)
        created_at = models.DateTimeField(auto_now_add=True)
        completed_at = models.DateTimeField(null=True, blank=True)
    """
    
    # === automation/views.py ===
    """
    from django.http import JsonResponse
    from django.views.decorators.http import require_http_methods
    from tasks import URLTask, AITask
    from .models import BrowserTask
    
    @require_http_methods(["POST"])
    def create_url_task(request):
        '''创建URL任务'''
        url = request.POST.get('url')
        
        # 使用Task组件
        task = URLTask(url=url)
        pid = task.execute(comet_path='/path/to/browser')
        task.start(pid)
        
        # 保存到Django数据库
        BrowserTask.objects.create(
            task_id=task.task_id,
            task_type='url',
            url=url,
            status=task.status.value,
            process_id=pid
        )
        
        return JsonResponse({
            'task_id': task.task_id,
            'status': 'started'
        })
    
    @require_http_methods(["GET"])
    def check_task_status(request, task_id):
        '''检查任务状态'''
        try:
            db_task = BrowserTask.objects.get(task_id=task_id)
        except BrowserTask.DoesNotExist:
            return JsonResponse({'error': 'Not found'}, status=404)
        
        # 重建Task对象来检查状态
        if db_task.task_type == 'url':
            task = URLTask(url=db_task.url)
        else:
            task = AITask(instruction=db_task.instruction)
        
        # 恢复状态
        task.task_id = db_task.task_id
        task.process_id = db_task.process_id
        # ... 恢复其他必要字段
        
        # 使用组件的方法检查
        if task.check_completion():
            task.complete()
            db_task.status = 'done'
            db_task.completed_at = timezone.now()
            db_task.save()
        
        return JsonResponse(task.to_dict())
    """
    
    # === automation/tasks.py (Celery) ===
    """
    from celery import shared_task
    from tasks import URLTask
    from .models import BrowserTask
    
    @shared_task
    def execute_url_task(url):
        '''Celery任务使用URLTask组件'''
        task = URLTask(url=url)
        pid = task.execute(comet_path='/path/to/browser')
        task.start(pid)
        
        # 保存
        BrowserTask.objects.create(
            task_id=task.task_id,
            task_type='url',
            url=url,
            status='running',
            process_id=pid
        )
        
        return task.task_id
    
    @shared_task
    def monitor_tasks():
        '''定期监控所有运行中的任务'''
        running_tasks = BrowserTask.objects.filter(status='running')
        
        for db_task in running_tasks:
            # 重建Task对象
            if db_task.task_type == 'url':
                task = URLTask(url=db_task.url)
            else:
                continue
            
            task.task_id = db_task.task_id
            task.process_id = db_task.process_id
            
            # 检查完成
            if task.check_completion():
                db_task.status = 'done'
                db_task.completed_at = timezone.now()
                db_task.save()
    """


# ============================================================================
# 示例 4: 扩展Task组件 - 自定义Task类型
# ============================================================================

def example_custom_task():
    """
    创建自己的Task类型
    继承BaseTask，实现execute和check_completion
    """
    from tasks.base_task import BaseTask, TaskType, TaskStatus
    import subprocess
    
    class ScreenshotTask(BaseTask):
        """
        自定义Task: 截图任务
        
        每隔1秒截图一次，直到检测到特定模式
        """
        
        def __init__(self, url: str, target_pattern: str):
            super().__init__(TaskType.CUSTOM)
            self.url = url
            self.target_pattern = target_pattern
            self.screenshots = []
        
        def execute(self, comet_path: str) -> int:
            """启动浏览器并开始截图"""
            process = subprocess.Popen([comet_path, self.url])
            
            # 启动截图线程
            import threading
            threading.Thread(
                target=self._screenshot_loop,
                daemon=True
            ).start()
            
            return process.pid
        
        def _screenshot_loop(self):
            """定期截图"""
            import time
            while self.status == TaskStatus.RUNNING:
                screenshot = self._capture_screenshot()
                self.screenshots.append(screenshot)
                time.sleep(1)
        
        def _capture_screenshot(self):
            """截图逻辑 (placeholder)"""
            pass
        
        def check_completion(self) -> bool:
            """检测是否找到目标模式"""
            # 分析最新的截图
            if self.screenshots:
                latest = self.screenshots[-1]
                if self._pattern_match(latest, self.target_pattern):
                    return True
            
            # 或者进程退出
            return not self.is_process_running()
        
        def _pattern_match(self, screenshot, pattern):
            """图像模式匹配 (placeholder)"""
            # TODO: 使用OpenCV或AI模型
            return False
    
    # 使用自定义Task
    task = ScreenshotTask(
        url="https://example.com",
        target_pattern="success_icon.png"
    )
    pid = task.execute(comet_path="/path/to/browser")
    task.start(pid)
    
    # 监控
    import time
    while not task.check_completion():
        time.sleep(1)
    
    task.complete()
    print(f"Found pattern! Captured {len(task.screenshots)} screenshots")


# ============================================================================
# 示例 5: 完全独立的自动化库
# ============================================================================

def example_standalone_library():
    """
    将Task组件打包成独立的自动化库
    其他人可以pip install使用
    
    项目结构:
    browser-automation/
    ├── setup.py
    ├── browser_automation/
    │   ├── __init__.py
    │   ├── tasks/         (复制过来)
    │   │   ├── base_task.py
    │   │   ├── url_task.py
    │   │   └── ai_task.py
    │   └── helpers.py     (便利函数)
    └── examples/
        └── quickstart.py
    """
    
    # === browser_automation/helpers.py ===
    """
    from .tasks import URLTask, AITask
    import time
    
    def quick_browse(url: str, browser_path: str = None):
        '''快速浏览URL'''
        task = URLTask(url)
        pid = task.execute(comet_path=browser_path)
        task.start(pid)
        
        # 等待完成
        while not task.check_completion():
            time.sleep(1)
        
        return task.complete()
    
    def quick_ai_task(instruction: str, browser_path: str = None):
        '''快速执行AI任务'''
        task = AITask(instruction)
        pid = task.execute(comet_path=browser_path)
        task.start(pid)
        return task
    """
    
    # === setup.py ===
    """
    from setuptools import setup, find_packages
    
    setup(
        name='browser-automation',
        version='0.1.0',
        packages=find_packages(),
        install_requires=[
            'psutil>=5.0.0',
        ],
        python_requires='>=3.7',
    )
    """
    
    # === 其他人使用 ===
    """
    # 安装
    pip install browser-automation
    
    # 使用
    from browser_automation import quick_browse, URLTask
    
    # 方式1: 快捷函数
    result = quick_browse("https://example.com")
    print(f"Done in {result.data['duration_seconds']}s")
    
    # 方式2: 直接使用组件
    task = URLTask("https://example.com")
    # ...
    """


# ============================================================================
# 运行示例
# ============================================================================

if __name__ == "__main__":
    print("Task组件使用示例")
    print("=" * 60)
    print()
    print("这些示例展示了Task组件如何在不同项目中复用:")
    print("1. 简单脚本")
    print("2. FastAPI服务")
    print("3. Django集成")
    print("4. 自定义Task类型")
    print("5. 独立的Python库")
    print()
    print("所有示例都使用相同的Task组件，但在不同的环境中！")
    print()
    
    # 你可以取消注释运行任何示例
    # example_simple_script()
