# Local Development Setup

This guide helps you set up and run the Code-to-BRD system locally without needing AWS deployment or access keys.

## 🎯 Overview

The local development environment simulates all AWS services locally:
- **S3**: Simulated using local filesystem
- **DynamoDB**: Simulated using SQLite database
- **Bedrock**: Mock responses from local files
- **Lambda**: Simulated using Flask web server

## 🚀 Quick Start

### 1. Setup (One-time)
```bash
# The setup is already done! You have:
# ✅ Virtual environment created
# ✅ Dependencies installed
# ✅ Local data directories created
# ✅ Configuration files generated
```

### 2. Start the Development Server
```bash
./start-local-dev.sh
```

The server will start at: `http://localhost:5000`

### 3. Test the System
In another terminal:
```bash
./run-tests.sh
```

## 📚 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Health check |
| `POST` | `/upload` | Upload codebase (zip file) |
| `GET` | `/projects` | List all projects |
| `GET` | `/projects/{id}` | Get project details |
| `GET` | `/projects/{id}/brd` | Get generated BRD |

## 🔧 Example Usage

### 1. Health Check
```bash
curl http://localhost:5000/health
```

### 2. Upload a Codebase
```bash
# Create a zip file with your code
zip -r my-codebase.zip src/ requirements.txt README.md

# Upload it
curl -X POST -F 'file=@my-codebase.zip' http://localhost:5000/upload
```

### 3. List Projects
```bash
curl http://localhost:5000/projects
```

### 4. Get Generated BRD
```bash
# Use the project_id from the upload response
curl http://localhost:5000/projects/{project_id}/brd
```

## 📁 Local File Structure

```
code-to-brd-system/
├── venv/                          # Python virtual environment
├── local-data/                    # Local data storage
│   ├── s3-simulation/            # S3 simulation
│   │   ├── codebases/            # Uploaded codebases
│   │   └── artifacts/            # Generated artifacts
│   ├── dynamodb-simulation/      # DynamoDB simulation
│   │   └── metadata.db           # SQLite database
│   └── mock-bedrock/             # Mock AI responses
├── local-config.json             # Local configuration
├── start-local-dev.sh            # Start server script
├── run-tests.sh                  # Run tests script
└── local-dev-server.py           # Local development server
```

## 🧪 Testing

The system includes comprehensive tests:

```bash
# Run all tests
./run-tests.sh

# Or manually
source venv/bin/activate
python test-local-system.py
```

Tests include:
- ✅ Health check
- ✅ Codebase upload
- ✅ Project listing
- ✅ Project details retrieval
- ✅ BRD generation and retrieval

## 🔍 How It Works

### 1. Upload Process
1. User uploads a zip file via `/upload`
2. File is stored in `local-data/s3-simulation/codebases/`
3. Project metadata is stored in SQLite database
4. Analysis workflow is simulated

### 2. Analysis Workflow
1. **Code Analysis**: Extracts functions, classes, API endpoints
2. **BRD Generation**: Uses mock AI to generate Business Requirements
3. **Use Case Generation**: Creates use cases and scenarios
4. **Test Generation**: Generates unit and functional tests

### 3. Mock AI Responses
- BRD generation uses pre-written templates
- Use case generation creates realistic scenarios
- Test generation produces sample test cases

## 🛠️ Customization

### Adding New Mock Responses
Edit files in `local-data/mock-bedrock/`:
- `brd_generation.json` - BRD templates
- `usecase_generation.json` - Use case templates
- `test_generation.json` - Test templates

### Modifying Analysis Logic
Edit `local-dev-server.py`:
- `simulate_analysis_workflow()` - Main analysis logic
- `simulate_brd_generation()` - BRD generation
- `simulate_usecase_generation()` - Use case generation

### Changing Storage
- **S3 Simulation**: Modify `LocalS3Simulator` class
- **DynamoDB Simulation**: Modify `LocalDynamoDBSimulator` class

## 🐛 Troubleshooting

### Server Won't Start
```bash
# Check if port 5000 is in use
lsof -i :5000

# Kill process if needed
kill -9 <PID>

# Start server again
./start-local-dev.sh
```

### Tests Fail
```bash
# Make sure server is running
curl http://localhost:5000/health

# Check logs
tail -f local-logs/server.log
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install flask requests
```

## 📊 Sample Output

### Upload Response
```json
{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "status": "uploaded",
  "message": "Codebase uploaded successfully",
  "workflow_status": {
    "status": "completed",
    "components": {
      "code_analysis": "completed",
      "brd_generation": "completed",
      "usecase_generation": "completed",
      "test_generation": "completed"
    }
  }
}
```

### BRD Response
```json
{
  "project_id": "123e4567-e89b-12d3-a456-426614174000",
  "brd": {
    "generation_timestamp": "2024-01-01T12:00:00Z",
    "brd_content": "# Business Requirement Document\n\n## Executive Summary\n...",
    "model_used": "mock-claude-3.5-sonnet"
  }
}
```

## 🚀 Next Steps

1. **Start Development**: Use `./start-local-dev.sh` to begin
2. **Test Upload**: Try uploading your own codebase
3. **Customize**: Modify mock responses for your needs
4. **Extend**: Add new analysis features
5. **Deploy**: When ready, deploy to AWS using the CDK stack

## 💡 Tips

- **File Size**: Keep uploads under 100MB
- **Supported Formats**: Zip files with common code files
- **Logs**: Check `local-logs/` for debugging
- **Data Persistence**: Local data persists between restarts
- **Performance**: Local simulation is fast but not production-ready

## 🔗 Related Files

- `local-dev-setup.py` - Initial setup script
- `local-dev-server.py` - Main development server
- `test-local-system.py` - Test suite
- `local-config.json` - Configuration file
- `start-local-dev.sh` - Server startup script
- `run-tests.sh` - Test runner script

---

**Happy coding! 🎉**

The local development environment gives you full control over the Code-to-BRD system without needing AWS access or deployment.



