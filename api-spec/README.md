# Comet Task Runner - API Specification

## 📦 Overview

This directory contains the complete API specification and testing resources for the **Comet Task Runner** project.

## 📁 Files

### 1. `Comet_TaskRunner_Collection.postman_collection.json`
Complete Postman Collection with all API endpoints organized into logical folders:

- **Health & Status** - Server health checks and queue monitoring
- **URL Tasks** - Browser navigation task execution
- **AI Prompt Tasks - E-commerce** - Specialized AI prompts for e-commerce platforms
  - `/1mu3` - 1688.com product analysis
  - `/ikea` - IKEA product information
  - `/amazon` - Amazon product search
- **AI Prompt Tasks - General** - General-purpose AI browser automation
  - Web page summarization
  - Data extraction
  - Image analysis
  - Translation
  - Comparative analysis
- **Task Status Monitoring** - Track task execution progress
- **Manual Callbacks** - Manual task status overrides

### 2. `Comet_TaskRunner_Local.postman_environment.json`
Environment configuration for local development with pre-configured variables:
- `base_url`: http://127.0.0.1:5000
- `task_id`: Auto-populated by test scripts
- `last_status`: Track last task status

## 🚀 Quick Start

### Import into Postman

1. **Open Postman** (Desktop or Web)

2. **Import Collection**
   - Click **Import** button (top left)
   - Select `Comet_TaskRunner_Collection.postman_collection.json`
   - Click **Import**

3. **Import Environment**
   - Click **Import** again
   - Select `Comet_TaskRunner_Local.postman_environment.json`
   - Click **Import**

4. **Select Environment**
   - In the top-right dropdown, select **"Comet TaskRunner - Local"**

5. **Start Testing!**
   - Ensure your backend server is running (`python src/backend.py`)
   - Click on any request and hit **Send**

## 🧪 Testing Workflow

### Basic Test Flow

1. **Health Check**
   ```
   GET /health
   ```
   Verify server is running

2. **Submit AI Task**
   ```
   POST /execute/ai
   Body: { "instruction": "/1mu3" }
   ```
   The test script automatically saves the `task_id`

3. **Check Status**
   ```
   GET /status/{{task_id}}
   ```
   Uses the saved `task_id` from step 2

4. **Monitor Queue**
   ```
   GET /manager/status
   ```
   See all tasks in the queue

### Automated Polling

Use the **"Poll Task Until Complete"** request to automatically check task status every 2 seconds until completion.

## 🔍 Test Features

### Automated Test Scripts

Each request includes test scripts that:
- ✅ Validate response status codes
- ✅ Check response structure
- ✅ Extract and save task IDs
- ✅ Auto-poll for task completion
- ✅ Verify task types and statuses

### Example Test Script Output
```javascript
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Task ID is returned", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('task_id');
    pm.environment.set("task_id", jsonData.task_id);
});
```

## 📊 Advanced Postman Features

### 1. Collection Runner

Run all tests automatically:
1. Click **Collections** → **Comet Task Runner API**
2. Click **Run** (or use Runner icon)
3. Select requests to run
4. View detailed results and pass/fail statistics

### 2. Newman CLI (CI/CD Integration)

Install Newman:
```bash
npm install -g newman
```

Run collection from command line:
```bash
newman run Comet_TaskRunner_Collection.postman_collection.json \
  -e Comet_TaskRunner_Local.postman_environment.json \
  --reporters cli,json
```

### 3. Generate API Documentation

1. In Postman, select collection
2. Click **View Documentation** (top-right)
3. Click **Publish** to create public docs
4. Share the URL with your team

### 4. Mock Server (Optional)

Create a mock server for frontend development:
1. Right-click collection → **Mock Collection**
2. Configure mock server
3. Use mock URL for frontend testing before backend is ready

### 5. Monitors (Scheduled Tests)

Set up automated health checks:
1. Click **Monitors** tab
2. Create new monitor
3. Schedule (e.g., every 5 minutes)
4. Get email alerts on failures

## 🎯 AI Prompt Test Cases

### E-commerce Focused

| Prompt | Purpose | Use Case |
|--------|---------|----------|
| `/1mu3` | 1688.com analysis | Extract product info from Alibaba wholesale |
| `/ikea` | IKEA product info | Analyze IKEA product pages |
| `/amazon` | Amazon search | Navigate and extract Amazon data |

### General Browser Automation

| Prompt | Purpose |
|--------|---------|
| "Summarize this webpage..." | Extract key information |
| "Extract all product prices..." | Data extraction |
| "Analyze images on this page..." | Multimodal image analysis |
| "Translate the main heading..." | Cross-language support |
| "Compare top 3 products..." | Comparative analysis |

## 🔧 Customization

### Adding New Test Cases

1. Right-click on a folder → **Add Request**
2. Configure the request details
3. Add test scripts in the **Tests** tab
4. Save and run

### Modifying Environment Variables

1. Click environment dropdown → **Edit**
2. Add/modify variables
3. Use `{{variable_name}}` in requests

### Example Custom Test Script
```javascript
pm.test("Custom validation", function () {
    var jsonData = pm.response.json();
    
    // Extract task_id
    pm.environment.set("task_id", jsonData.task_id);
    
    // Custom validation
    pm.expect(jsonData.status).to.be.oneOf(['queued', 'started']);
    
    // Log for debugging
    console.log("Task created: " + jsonData.task_id);
});
```

## 📝 API Endpoints Reference

### Base URL
```
http://127.0.0.1:5000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/execute/url` | Execute URL task |
| POST | `/execute/ai` | Execute AI task |
| GET | `/status/<task_id>` | Get task status |
| GET | `/manager/status` | Get queue status |
| GET | `/jobs` | Get all tasks |
| POST | `/callback` | Manual status update |

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Connection refused" error
- **Solution**: Ensure backend server is running on port 5000

**Issue**: Task ID not found
- **Solution**: Check that task was created successfully, verify task_id variable

**Issue**: Tests failing
- **Solution**: Check Console tab for detailed error messages

### Debug Tips

1. **Enable Postman Console** (<kbd>Ctrl</kbd>+<kbd>Alt</kbd>+<kbd>C</kbd>)
   - See all request/response details
   - View console.log() outputs from test scripts

2. **Check Response Tab**
   - Verify JSON structure
   - Check status codes

3. **Review Test Results**
   - Click **Test Results** tab after sending request
   - See which tests passed/failed

## 📚 Additional Resources

- [Postman Documentation](https://learning.postman.com/docs/)
- [Newman CLI Guide](https://learning.postman.com/docs/running-collections/using-newman-cli/command-line-integration-with-newman/)
- [Writing Tests in Postman](https://learning.postman.com/docs/writing-scripts/test-scripts/)

## 🤝 Contributing

When adding new endpoints:
1. Add the request to the appropriate folder
2. Include test scripts
3. Update this README with endpoint details
4. Test thoroughly before committing

---

**Last Updated**: December 2025
**Version**: 1.0
**Maintained by**: Comet Task Runner Team
