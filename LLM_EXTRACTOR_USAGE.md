# LLM Knowledge Extractor Usage Guide

The LLM Knowledge Extractor now supports both **AWS Bedrock** and **Google Gemini** for API knowledge extraction from Capillary documentation.

## 🚀 Quick Start

### Option 1: Using AWS Bedrock (Default)
```bash
# Install dependencies
pip install boto3 beautifulsoup4 requests

# Configure AWS credentials
aws configure

# Run with Bedrock
python src/shared/api-knowledge/llm_knowledge_extractor.py
```

### Option 2: Using Google Gemini (Free)
```bash
# Install dependencies
pip install google-generativeai beautifulsoup4 requests

# Set Gemini API key
export GEMINI_API_KEY=your_free_api_key_here

# Run with Gemini
python src/shared/api-knowledge/llm_knowledge_extractor.py gemini
```

## 🔧 Configuration

### AWS Bedrock Setup
1. **Configure AWS credentials**: `aws configure`
2. **Enable Bedrock access** in AWS Console
3. **Request model access** for Claude models
4. **Run**: `python src/shared/api-knowledge/llm_knowledge_extractor.py`

### Google Gemini Setup (Free)
1. **Get free API key**: https://makersuite.google.com/app
2. **Set environment variable**: `export GEMINI_API_KEY=your_key`
3. **Run**: `python src/shared/api-knowledge/llm_knowledge_extractor.py gemini`

## 📊 Features

### Both Providers Support:
- ✅ **API Discovery**: Extracts all APIs from documentation
- ✅ **Business Context**: Identifies business functions and impacts
- ✅ **Integration Patterns**: Finds common integration patterns
- ✅ **Comprehensive Extraction**: Processes multiple documentation pages
- ✅ **JSON Output**: Structured knowledge base export

### Provider Comparison:

| Feature | AWS Bedrock | Google Gemini |
|---------|-------------|---------------|
| **Cost** | Pay per token | Free tier available |
| **Setup** | AWS account + Bedrock access | Free API key |
| **Quality** | Excellent | Excellent |
| **Speed** | Fast | Fast |
| **Rate Limits** | High | 15 req/min (free) |

## 🎯 Usage Examples

### Basic Usage
```python
from src.shared.api_knowledge.llm_knowledge_extractor import LLMKnowledgeExtractor

# Using Bedrock
extractor = LLMKnowledgeExtractor(llm_provider="bedrock")
knowledge = extractor.create_comprehensive_knowledge_base()

# Using Gemini
extractor = LLMKnowledgeExtractor(llm_provider="gemini")
knowledge = extractor.create_comprehensive_knowledge_base()
```

### Single Page Extraction
```python
# Extract from specific URL
result = extractor.extract_page_knowledge("https://docs.capillarytech.com/api/reference")
print(f"Found {len(result['apis'])} APIs")
```

## 📁 Output

The extractor creates `capillary_llm_knowledge.json` with:

```json
{
  "capillary_apis": {
    "POST_v2_customers": {
      "method": "POST",
      "endpoint": "/v2/customers",
      "description": "Create new customer profile",
      "business_function": "Customer Profile Creation",
      "integration_impact": "Enables customer onboarding",
      "parameters": ["name", "email", "phone"],
      "source_url": "https://docs.capillarytech.com/..."
    }
  },
  "business_concepts": {
    "Loyalty Points": {
      "description": "Customer reward system",
      "source_url": "https://docs.capillarytech.com/..."
    }
  },
  "integration_patterns": {
    "Customer Onboarding": {
      "description": "Complete customer setup process",
      "apis_involved": ["POST /v2/customers", "POST /v2/loyalty"],
      "source_url": "https://docs.capillarytech.com/..."
    }
  }
}
```

## 🧪 Testing

Run the test script to verify both providers:

```bash
python test-llm-extractor.py
```

## 💡 Tips

### For Development/Testing:
- **Use Gemini** - Free and easy to set up
- **Fast iteration** - No AWS costs
- **Quick setup** - Just need API key

### For Production:
- **Use Bedrock** - Higher rate limits
- **Enterprise support** - AWS integration
- **Scalable** - Handle large documentation sets

## 🔍 Troubleshooting

### Gemini Issues:
```bash
# Check API key
echo $GEMINI_API_KEY

# Test API key
python -c "import google.generativeai as genai; genai.configure(api_key='$GEMINI_API_KEY'); print('✅ API key works')"
```

### Bedrock Issues:
```bash
# Check AWS credentials
aws sts get-caller-identity

# Check Bedrock access
aws bedrock list-foundation-models --region us-east-1
```

## 🎉 Benefits

- **Free Option**: Use Gemini for zero-cost development
- **Enterprise Option**: Use Bedrock for production scale
- **Same Quality**: Both providers deliver excellent results
- **Easy Switching**: Change providers with one parameter
- **Comprehensive**: Extracts APIs, concepts, and patterns

