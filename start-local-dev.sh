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
source venv/bin/activate
python local-dev-server.py
