# 🔄 Google Gemini API Migration Guide

## Overview

This guide helps you migrate from the deprecated `google-generativeai` library to the new `google-genai` library with Gemini 2.5 Flash model.

## 🚨 Breaking Changes

### Library Update
- **Old**: `google-generativeai>=0.8.0`
- **New**: `google-genai>=1.21.1`

### Model Update
- **Old**: `gemini-1.5-flash`
- **New**: `gemini-2.5-flash`

### API Changes
- **Old**: `genai.configure()` + `genai.GenerativeModel()`
- **New**: `genai.Client()` + `client.models.generate_content()`

## 📦 Installation

### 1. Remove Old Package
```bash
cd backend
uv remove google-generativeai
```

### 2. Install New Package
```bash
uv add google-genai>=1.21.1
```

### 3. Update Dependencies
```bash
uv sync
```

## 🔧 Code Changes

### Before (google-generativeai)
```python
import google.generativeai as genai

# Configure
genai.configure(api_key=api_key)
client = genai.GenerativeModel('gemini-1.5-flash')

# Generate content
response = client.generate_content(
    contents=prompt,
    generation_config=genai.GenerationConfig(
        temperature=0.7,
        max_output_tokens=1000
    )
)
```

### After (google-genai)
```python
from google import genai
from google.genai import types

# Create client
client = genai.Client(api_key=api_key)

# Generate content
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt,
    config=types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=1000
    )
)
```

## ✅ Migration Checklist

- [ ] **Remove old package**: `uv remove google-generativeai`
- [ ] **Install new package**: `uv add google-genai>=1.21.1`
- [ ] **Update imports**: Change to `from google import genai`
- [ ] **Update client creation**: Use `genai.Client(api_key=...)`
- [ ] **Update model name**: Use `gemini-2.5-flash`
- [ ] **Update API calls**: Use `client.models.generate_content()`
- [ ] **Update config types**: Use `types.GenerateContentConfig`
- [ ] **Test functionality**: Run `python scripts/test_new_gemini.py`

## 🧪 Testing

### Test the Migration
```bash
cd backend
python scripts/test_new_gemini.py
```

### Expected Output
```
🧪 Testing New Google GenAI Integration...
✅ Service initialized with model: gemini-2.5-flash
✅ Health check: Healthy
✅ Basic generation successful
✅ System instruction test successful
✅ Intent analysis successful
✅ Query generation successful
✅ Response generation successful
🎉 All Google GenAI tests completed successfully!
```

## 🔑 Environment Setup

### Required Environment Variable
```bash
# .env file
GOOGLE_API_KEY=your_actual_gemini_api_key_here
```

### Get Your API Key
1. Visit [Google AI Studio](https://ai.google.dev/)
2. Create an account or sign in
3. Generate a new API key
4. Add it to your `.env` file

## 🚀 Benefits of Migration

### Performance Improvements
- **Faster Response Times**: Gemini 2.5 Flash is optimized for speed
- **Better Accuracy**: Improved natural language understanding
- **Enhanced Features**: Latest model capabilities

### API Improvements
- **Cleaner Interface**: More intuitive API design
- **Better Error Handling**: Improved error messages and debugging
- **Future-Proof**: Active development and support

### Model Capabilities
- **Improved Reasoning**: Better logical reasoning and analysis
- **Enhanced Context**: Better understanding of complex queries
- **Faster Processing**: Optimized for real-time applications

## 🛠️ Troubleshooting

### Common Issues

#### 1. Import Errors
```python
# ❌ Old import (will fail)
import google.generativeai as genai

# ✅ New import
from google import genai
from google.genai import types
```

#### 2. Client Initialization
```python
# ❌ Old way (will fail)
genai.configure(api_key=api_key)
client = genai.GenerativeModel('gemini-1.5-flash')

# ✅ New way
client = genai.Client(api_key=api_key)
```

#### 3. API Calls
```python
# ❌ Old way (will fail)
response = client.generate_content(contents=prompt)

# ✅ New way
response = client.models.generate_content(
    model='gemini-2.5-flash',
    contents=prompt
)
```

#### 4. Model Name
```python
# ❌ Old model
model = 'gemini-1.5-flash'

# ✅ New model
model = 'gemini-2.5-flash'
```

### Error Messages

#### "No module named 'google.generativeai'"
- **Solution**: Remove old package and install new one
- **Command**: `uv remove google-generativeai && uv add google-genai>=1.21.1`

#### "Invalid model name"
- **Solution**: Update model name to `gemini-2.5-flash`
- **Check**: Verify model name in `GeminiService.__init__()`

#### "API key not found"
- **Solution**: Set `GOOGLE_API_KEY` in your `.env` file
- **Get Key**: Visit [Google AI Studio](https://ai.google.dev/)

## 📚 Additional Resources

### Documentation
- [Google GenAI Python SDK](https://github.com/google/generative-ai-python)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Migration Examples](google-genai-doc.md)

### Support
- [GitHub Issues](https://github.com/google/generative-ai-python/issues)
- [Google AI Community](https://developers.googleblog.com/2024/12/gemini-2-flash-thinking-experimental-model.html)

## 🎉 Migration Complete!

Once you've completed all the steps above, your Elasticsearch Agent will be running with the latest Google Gemini 2.5 Flash model and the new `google-genai` library.

### Next Steps
1. **Test thoroughly**: Run all test scripts to ensure everything works
2. **Monitor performance**: Check if response times have improved
3. **Explore new features**: Take advantage of Gemini 2.5 Flash capabilities
4. **Update documentation**: Keep your team informed of the changes

---

*Migration completed: 2025-01-27*
*New Model: Gemini 2.5 Flash*
*New Library: google-genai>=1.21.1*