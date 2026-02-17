# Usage Examples

Practical examples of using hrunxtnshn for various tasks.

## Table of Contents

1. [Basic Examples](#basic-examples)
2. [Data Extraction](#data-extraction)
3. [Research Tasks](#research-tasks)
4. [Advanced Use Cases](#advanced-use-cases)
5. [API Usage](#api-usage)

## Basic Examples

### Example 1: Simple Question

**Task**:
```
What is the capital of France?
```

**Expected Output**:
```json
{
  "result": "The capital of France is Paris."
}
```

### Example 2: Current Information

**Task**:
```
Load the Wikipedia page for Eiffel Tower and tell me when it was built.
```

**Expected Output**:
```json
{
  "result": "The Eiffel Tower was built in 1889.",
  "plan": [
    {"action": "LOAD_PAGE", "url": "https://en.wikipedia.org/wiki/Eiffel_Tower"},
    {"action": "EXTRACT", "content": "..."}
  ]
}
```

## Data Extraction

### Example 3: LinkedIn Profile

**Prerequisites**: Logged into LinkedIn

**Task**:
```
Extract data from LinkedIn profile https://www.linkedin.com/in/example
```

**Expected Output**:
```json
{
  "result": {
    "name": "John Doe",
    "headline": "Software Engineer at Tech Corp",
    "location": "San Francisco, CA",
    "connections": "500+ connections",
    "about": "Passionate software engineer...",
    "experience": [
      {
        "title": "Senior Software Engineer",
        "company": "Tech Corp",
        "duration": "2020 - Present",
        "description": "Leading development of..."
      },
      {
        "title": "Software Engineer",
        "company": "Startup Inc",
        "duration": "2018 - 2020",
        "description": "Built scalable web applications..."
      }
    ],
    "education": [
      {
        "school": "University of California",
        "degree": "Bachelor of Science",
        "field": "Computer Science",
        "years": "2014 - 2018"
      }
    ],
    "skills": ["Python", "JavaScript", "React", "Node.js"]
  }
}
```

### Example 4: Instagram Profile

**Prerequisites**: Logged into Instagram

**Task**:
```
Extract Instagram profile data from https://www.instagram.com/natgeo
```

**Expected Output**:
```json
{
  "result": {
    "username": "natgeo",
    "fullName": "National Geographic",
    "bio": "Experience the world through the eyes of National Geographic photographers.",
    "followers": 283000000,
    "following": 200,
    "posts": 25000,
    "isPrivate": false,
    "isVerified": true,
    "externalUrl": "https://www.nationalgeographic.com",
    "recentPosts": [
      {
        "postUrl": "https://www.instagram.com/p/...",
        "imageUrl": "https://...",
        "caption": "Amazing wildlife...",
        "likes": "1.2M",
        "comments": "15K"
      }
    ]
  }
}
```

### Example 5: Google Maps Place

**Task**:
```
Extract data from Google Maps place https://www.google.com/maps/place/Eiffel+Tower
```

**Expected Output**:
```json
{
  "result": {
    "name": "Eiffel Tower",
    "rating": 4.7,
    "reviewCount": 450000,
    "address": "Champ de Mars, 5 Av. Anatole France, 75007 Paris, France",
    "phone": "+33 892 70 12 39",
    "website": "https://www.toureiffel.paris",
    "category": "Tourist attraction",
    "hours": {
      "Monday": "9:30 AM - 11:45 PM",
      "Tuesday": "9:30 AM - 11:45 PM"
    },
    "reviews": [
      {
        "author": "John Smith",
        "rating": 5,
        "text": "Absolutely stunning! A must-visit...",
        "date": "2 weeks ago"
      }
    ]
  }
}
```

## Research Tasks

### Example 6: Multi-Source Research

**Task**:
```
Research the history of artificial intelligence. Find information about:
1. When AI was founded as a field
2. Key milestones in AI development
3. Current state of AI technology
```

**Expected Output**:
```json
{
  "result": {
    "summary": "Artificial Intelligence was founded as an academic discipline in 1956...",
    "founding": {
      "year": 1956,
      "event": "Dartmouth Conference",
      "founders": ["John McCarthy", "Marvin Minsky", "Allen Newell", "Herbert Simon"]
    },
    "milestones": [
      {
        "year": 1997,
        "event": "Deep Blue defeats world chess champion"
      },
      {
        "year": 2012,
        "event": "Deep learning breakthrough in image recognition"
      },
      {
        "year": 2022,
        "event": "ChatGPT released to public"
      }
    ],
    "current_state": "AI is now widely used in various applications..."
  }
}
```

### Example 7: Competitive Analysis

**Task**:
```
Find and compare the top 3 restaurants in San Francisco with the highest ratings on Google Maps. For each, extract:
- Name
- Rating
- Number of reviews
- Price level
- Address
```

**Expected Output**:
```json
{
  "result": {
    "restaurants": [
      {
        "name": "Restaurant A",
        "rating": 4.9,
        "reviewCount": 1200,
        "priceLevel": "$$$",
        "address": "123 Main St, San Francisco, CA"
      },
      {
        "name": "Restaurant B",
        "rating": 4.8,
        "reviewCount": 980,
        "priceLevel": "$$$$",
        "address": "456 Market St, San Francisco, CA"
      },
      {
        "name": "Restaurant C",
        "rating": 4.8,
        "reviewCount": 850,
        "priceLevel": "$$$",
        "address": "789 Valencia St, San Francisco, CA"
      }
    ]
  }
}
```

## Advanced Use Cases

### Example 8: Lead Generation

**Task**:
```
Find LinkedIn profiles of Software Engineers at Google in San Francisco. Extract their:
- Name
- Current position
- Years of experience
- Skills
```

**Note**: This requires multiple profile extractions. The agent will plan and execute sequentially.

### Example 9: Market Research

**Task**:
```
Research the top 5 AI startups:
1. Find their LinkedIn company pages
2. Extract company information
3. Find key employees
4. Summarize their products/services
```

### Example 10: Content Monitoring

**Task**:
```
Monitor Instagram account @competitor for new posts. Extract:
- Latest 5 posts
- Engagement metrics (likes, comments)
- Post captions
- Posting frequency
```

## API Usage

### Example 11: Direct API Call (Orchestrator)

```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Extract LinkedIn profile data from https://www.linkedin.com/in/example",
    "needsPlanning": true,
    "metadata": {
      "user_id": "12345",
      "source": "api"
    }
  }'
```

**Response**:
```json
{
  "task_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "result": {
    "result": {...},
    "plan": [...],
    "actions_executed": [...]
  },
  "metadata": {
    "user_id": "12345",
    "source": "api"
  }
}
```

### Example 12: Streaming API

```bash
curl -X POST http://localhost:8000/api/tasks/stream \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Research AI startups"}' \
  --no-buffer
```

**Response** (Server-Sent Events):
```
data: {"type":"start","task_id":"...","timestamp":"2026-02-18T10:00:00"}

data: {"type":"status","data":"running","timestamp":"2026-02-18T10:00:01"}

data: {"type":"result","data":{...},"timestamp":"2026-02-18T10:00:05"}

data: {"type":"end","timestamp":"2026-02-18T10:00:05"}
```

### Example 13: Python Client

```python
import requests

# Create task
response = requests.post('http://localhost:8000/api/tasks', json={
    'prompt': 'Extract LinkedIn profile from https://linkedin.com/in/example',
    'needsPlanning': True
})

task_data = response.json()
task_id = task_data['task_id']

print(f"Task created: {task_id}")
print(f"Status: {task_data['status']}")
print(f"Result: {task_data['result']}")
```

### Example 14: JavaScript Client

```javascript
// Extension integration
async function executeTask(prompt) {
  const response = await chrome.runtime.sendMessage({
    type: 'EXECUTE_TASK',
    task: {
      prompt: prompt,
      needsPlanning: true
    }
  });
  
  if (response.ok) {
    console.log('Result:', response.data);
    return response.data;
  } else {
    console.error('Error:', response.error);
    throw new Error(response.error);
  }
}

// Usage
executeTask('Extract data from LinkedIn profile https://linkedin.com/in/example')
  .then(result => console.log('Success:', result))
  .catch(error => console.error('Failed:', error));
```

## Batch Processing

### Example 15: Multiple Profiles

```python
import requests
import time

profiles = [
    'https://linkedin.com/in/profile1',
    'https://linkedin.com/in/profile2',
    'https://linkedin.com/in/profile3'
]

results = []

for profile in profiles:
    response = requests.post('http://localhost:8000/api/tasks', json={
        'prompt': f'Extract LinkedIn profile from {profile}'
    })
    
    if response.status_code == 200:
        results.append(response.json())
    
    # Rate limiting
    time.sleep(2)

print(f"Extracted {len(results)} profiles")
```

## Error Handling

### Example 16: Handling Errors

```javascript
async function safeExtraction(url) {
  try {
    const response = await chrome.runtime.sendMessage({
      type: 'EXTRACT_LINKEDIN',
      url: url
    });
    
    if (response.ok) {
      return response.data;
    } else {
      console.error('Extraction failed:', response.error);
      
      // Handle specific errors
      if (response.error.includes('Not logged in')) {
        alert('Please log in to LinkedIn first');
      } else if (response.error.includes('timeout')) {
        alert('Request timed out. Please try again.');
      } else {
        alert('Extraction failed: ' + response.error);
      }
      
      return null;
    }
  } catch (error) {
    console.error('Unexpected error:', error);
    return null;
  }
}
```

## Best Practices

### 1. Rate Limiting

```javascript
// Wait between requests
async function extractMultipleProfiles(urls) {
  const results = [];
  
  for (const url of urls) {
    const result = await extractProfile(url);
    results.push(result);
    
    // Wait 2 seconds between requests
    await new Promise(resolve => setTimeout(resolve, 2000));
  }
  
  return results;
}
```

### 2. Error Recovery

```javascript
async function extractWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const result = await extractProfile(url);
      return result;
    } catch (error) {
      console.log(`Attempt ${i + 1} failed:`, error);
      
      if (i === maxRetries - 1) {
        throw error;
      }
      
      // Wait before retry (exponential backoff)
      await new Promise(resolve => 
        setTimeout(resolve, Math.pow(2, i) * 1000)
      );
    }
  }
}
```

### 3. Progress Tracking

```javascript
async function extractWithProgress(urls, onProgress) {
  const results = [];
  
  for (let i = 0; i < urls.length; i++) {
    const url = urls[i];
    const result = await extractProfile(url);
    results.push(result);
    
    // Report progress
    onProgress({
      current: i + 1,
      total: urls.length,
      percentage: ((i + 1) / urls.length) * 100,
      currentUrl: url
    });
  }
  
  return results;
}

// Usage
extractWithProgress(profiles, (progress) => {
  console.log(`Progress: ${progress.percentage.toFixed(0)}%`);
  console.log(`Processing: ${progress.currentUrl}`);
});
```

## Integration Examples

### Example 17: Google Sheets Integration

```javascript
// Export results to Google Sheets
async function exportToSheets(data) {
  const SHEET_URL = 'https://sheets.googleapis.com/v4/spreadsheets/...';
  
  const rows = data.map(profile => [
    profile.name,
    profile.headline,
    profile.location,
    profile.connections
  ]);
  
  await fetch(SHEET_URL, {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer ' + accessToken,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      values: rows
    })
  });
}
```

### Example 18: Webhook Integration

```python
import requests

# Extract data
response = requests.post('http://localhost:8000/api/tasks', json={
    'prompt': 'Extract LinkedIn profile...'
})

result = response.json()

# Send to webhook
webhook_url = 'https://your-webhook.com/endpoint'
requests.post(webhook_url, json={
    'event': 'extraction_complete',
    'data': result
})
```

## Tips

1. **Be specific**: More detailed prompts yield better results
2. **Check login**: Ensure logged into target websites before extraction
3. **Handle errors**: Always implement error handling
4. **Rate limit**: Don't overwhelm websites with requests
5. **Test first**: Test with one item before batch processing
6. **Monitor usage**: Track API usage and costs
7. **Respect ToS**: Always respect website terms of service

## Support

For more examples and help:
- GitHub Issues: https://github.com/hrunx/hrunxtnshn/issues
- Documentation: https://github.com/hrunx/hrunxtnshn/wiki
