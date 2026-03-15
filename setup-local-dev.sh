#!/bin/bash

# Local Development Setup Script
# Sets up the Code-to-BRD system for local development without AWS

set -e

echo "🚀 Setting up Local Development Environment"
echo "============================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8+ first."
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "📍 Python version: $PYTHON_VERSION"

# Install required Python packages
echo "📦 Installing Python dependencies..."
pip3 install flask requests

# Run the local setup
echo "🔧 Setting up local environment..."
python3 local-dev-setup.py

# Create a simple start script
cat > start-local-dev.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting Local Development Server..."
echo "📡 Server will be available at: http://localhost:5000"
echo "📚 Available endpoints:"
echo "   GET  /health - Health check"
echo "   POST /upload - Upload codebase"
echo "   GET  /projects - List projects"
echo "   GET  /projects/{id} - Get project details"
echo "   GET  /projects/{id}/brd - Get generated BRD"
echo ""
echo "🔧 Local services:"
echo "   - S3: Simulated with local filesystem"
echo "   - DynamoDB: Simulated with SQLite"
echo "   - Bedrock: Mock responses"
echo ""
echo "Press Ctrl+C to stop the server"
echo "============================================="
python3 local-dev-server.py
EOF

chmod +x start-local-dev.sh

# Create a test script
cat > run-tests.sh << 'EOF'
#!/bin/bash
echo "🧪 Running Local System Tests..."
echo "============================================="
python3 test-local-system.py
EOF

chmod +x run-tests.sh

echo ""
echo "✅ Local Development Environment Setup Complete!"
echo ""
echo "📁 Local data directory: local-data/"
echo "📄 Configuration: local-config.json"
echo "📄 Logs: local-logs/"
echo ""
echo "🚀 To start the development server:"
echo "   ./start-local-dev.sh"
echo ""
echo "🧪 To run tests:"
echo "   ./run-tests.sh"
echo ""
echo "📚 Usage:"
echo "   1. Start the server: ./start-local-dev.sh"
echo "   2. In another terminal, run tests: ./run-tests.sh"
echo "   3. Or use curl/Postman to test the API endpoints"
echo ""
echo "🔧 Example API calls:"
echo "   # Health check"
echo "   curl http://localhost:5000/health"
echo ""
echo "   # Upload codebase"
echo "   curl -X POST -F 'file=@your-codebase.zip' http://localhost:5000/upload"
echo ""
echo "   # List projects"
echo "   curl http://localhost:5000/projects"
echo ""
echo "   # Get BRD"
echo "   curl http://localhost:5000/projects/{project_id}/brd"
echo ""
echo "🎉 Ready for local development!"



