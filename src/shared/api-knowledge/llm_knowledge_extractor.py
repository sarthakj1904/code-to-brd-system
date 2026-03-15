#!/usr/bin/env python3
"""
LLM-powered knowledge extraction from Capillary documentation
Supports both AWS Bedrock and Google Gemini
"""

import requests
import json
import boto3
import os
from bs4 import BeautifulSoup

# Optional imports for Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Google Generative AI not installed. Install with: pip install google-generativeai")

class LLMKnowledgeExtractor:
    def __init__(self, llm_provider="bedrock"):
        """
        Initialize the knowledge extractor
        
        Args:
            llm_provider (str): "bedrock" or "gemini"
        """
        self.llm_provider = llm_provider.lower()
        
        if self.llm_provider == "bedrock":
            self.bedrock = boto3.client('bedrock-runtime', region_name='us-east-1')
            self.model_id = "anthropic.claude-3-sonnet-20240229-v1:0"
        elif self.llm_provider == "gemini":
            if not GEMINI_AVAILABLE:
                raise ImportError("Google Generative AI not available. Install with: pip install google-generativeai")
            
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY environment variable is required for Gemini")
            
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            raise ValueError("llm_provider must be 'bedrock' or 'gemini'")
    
    def extract_page_knowledge(self, url):
        """Extract comprehensive knowledge from a single page using LLM"""
        
        # Get page content
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        page_text = soup.get_text()[:15000]  # Limit for LLM context
        
        # LLM prompt for knowledge extraction
        prompt = f"""
Analyze this Capillary documentation page and extract ALL APIs, business functions, and integration details.

PAGE CONTENT:
{page_text}

Extract and return ONLY a JSON object with this structure:
{{
  "apis": [
    {{
      "method": "POST",
      "endpoint": "/v2/customers",
      "description": "detailed description of what this API does",
      "business_function": "specific business function like 'Customer Profile Creation' or 'Loyalty Points Award'",
      "integration_impact": "specific business impact",
      "parameters": ["param1", "param2"]
    }}
  ],
  "business_concepts": [
    {{
      "name": "concept name",
      "description": "detailed explanation"
    }}
  ],
  "integration_patterns": [
    {{
      "pattern": "pattern name",
      "description": "how it works",
      "apis_involved": ["api1", "api2"]
    }}
  ]
}}

Be very specific about business functions - avoid generic terms like "customer engagement platform integration".
Extract ALL APIs mentioned, even if briefly referenced.
"""
        
        # Call LLM based on provider
        if self.llm_provider == "bedrock":
            content = self._call_bedrock(prompt)
        elif self.llm_provider == "gemini":
            content = self._call_gemini(prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        # Parse JSON from LLM response
        try:
            return json.loads(content)
        except:
            # Fallback if JSON parsing fails
            return {"apis": [], "business_concepts": [], "integration_patterns": []}
    
    def _call_bedrock(self, prompt):
        """Call AWS Bedrock"""
        body = json.dumps({
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}]
        })
        
        response = self.bedrock.invoke_model(
            body=body,
            modelId=self.model_id,
            accept='application/json',
            contentType='application/json'
        )
        
        result = json.loads(response.get('body').read())
        return result['content'][0]['text']
    
    def _call_gemini(self, prompt):
        """Call Google Gemini"""
        response = self.model.generate_content(prompt)
        return response.text
    
    def discover_all_pages(self):
        """Discover all documentation pages like the original scraper"""
        from urllib.parse import urljoin
        
        base_url = "https://docs.capillarytech.com"
        urls = set()
        
        try:
            # Start with main page
            response = requests.get(base_url)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find all internal links
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('/'):
                    full_url = urljoin(base_url, href)
                    if 'docs.capillarytech.com' in full_url:
                        urls.add(full_url)
            
            # Also check common documentation paths
            common_paths = ['/reference/apioverview', '/page/developerdocumentation', '/page/product-release-notes', '/docs/introduction']
            for path in common_paths:
                try:
                    url = urljoin(base_url, path)
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        for link in soup.find_all('a', href=True):
                            href = link['href']
                            if href.startswith('/'):
                                full_url = urljoin(base_url, href)
                                if 'docs.capillarytech.com' in full_url:
                                    urls.add(full_url)
                except:
                    continue
                    
        except Exception as e:
            print(f"Error discovering pages: {e}")
        
        return list(urls)
    
    def create_comprehensive_knowledge_base(self):
        """Create knowledge base from ALL Capillary documentation pages"""
        
        # Discover all URLs
        print("🔍 Discovering all documentation pages...")
        all_urls = self.discover_all_pages()
        print(f"Found {len(all_urls)} pages to process")
        
        comprehensive_knowledge = {
            "capillary_apis": {},
            "business_concepts": {},
            "integration_patterns": {}
        }
        
        for url in all_urls[:10000]:  # Limit to prevent timeout
            try:
                print(f"Processing: {url}")
                page_knowledge = self.extract_page_knowledge(url)
                
                # Merge APIs
                for api in page_knowledge.get("apis", []):
                    key = f"{api['method']}_{api['endpoint'].replace('/', '_').replace('{', '').replace('}', '')}"
                    comprehensive_knowledge["capillary_apis"][key] = {
                        "method": api["method"],
                        "endpoint": api["endpoint"], 
                        "description": api["description"],
                        "business_function": api["business_function"],
                        "integration_impact": api["integration_impact"],
                        "parameters": api.get("parameters", []),
                        "source_url": url
                    }
                
                # Merge concepts
                for concept in page_knowledge.get("business_concepts", []):
                    comprehensive_knowledge["business_concepts"][concept["name"]] = {
                        "description": concept["description"],
                        "source_url": url
                    }
                
                # Merge patterns
                for pattern in page_knowledge.get("integration_patterns", []):
                    comprehensive_knowledge["integration_patterns"][pattern["pattern"]] = {
                        "description": pattern["description"],
                        "apis_involved": pattern["apis_involved"],
                        "source_url": url
                    }
                    
            except Exception as e:
                print(f"Error processing {url}: {e}")
                continue
        
        # Save comprehensive knowledge
        with open('capillary_llm_knowledge.json', 'w') as f:
            json.dump(comprehensive_knowledge, f, indent=2)
        
        print(f"✅ Extracted {len(comprehensive_knowledge['capillary_apis'])} APIs")
        print(f"✅ Extracted {len(comprehensive_knowledge['business_concepts'])} concepts")
        print(f"✅ Extracted {len(comprehensive_knowledge['integration_patterns'])} patterns")
        
        return comprehensive_knowledge

def main():
    import sys
    
    # Check command line arguments for LLM provider
    llm_provider = "gemini"  # Default
    if len(sys.argv) > 1:
        llm_provider = sys.argv[1].lower()
        if llm_provider not in ["bedrock", "gemini"]:
            print("❌ Invalid LLM provider. Use 'bedrock' or 'gemini'")
            sys.exit(1)
    
    print(f"🤖 Using LLM Provider: {llm_provider.upper()}")
    
    if llm_provider == "gemini":
        if not os.getenv('GEMINI_API_KEY'):
            print("❌ GEMINI_API_KEY environment variable is required")
            print("💡 Set it with: export GEMINI_API_KEY=your_key_here")
            sys.exit(1)
    
    try:
        extractor = LLMKnowledgeExtractor(llm_provider=llm_provider)
        knowledge = extractor.create_comprehensive_knowledge_base()
        
        print("\n🎉 LLM Knowledge Extraction Complete!")
        print("📄 Output: capillary_llm_knowledge.json")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()