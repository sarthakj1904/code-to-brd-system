#!/bin/bash

echo "🆓 Setting up Free AI Demo for Code-to-BRD System"
echo "=============================================="

# Install required packages
echo "📦 Installing required packages..."
pip install google-generativeai requests

# Create environment file template
echo "🔧 Creating environment template..."
cat > .env.template << EOF
# Free AI API Keys
GEMINI_API_KEY=your_gemini_api_key_here
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Optional: OpenAI API Key (if you want to use GPT-3.5)
OPENAI_API_KEY=your_openai_api_key_here
EOF

echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Get free API key from Google AI Studio: https://makersuite.google.com/app"
echo "   2. Copy .env.template to .env and add your API key"
echo "   3. Run: python free-ai-demo.py"
echo ""
echo "💡 Free AI Options:"
echo "   🥇 Google Gemini (Recommended) - Most generous free tier"
echo "   🥈 Hugging Face - Open source models"
echo "   🥉 OpenAI - Limited free tier"
echo ""
echo "🎬 To run demo:"
echo "   python free-ai-demo.py"

