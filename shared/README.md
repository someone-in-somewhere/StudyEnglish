# Shared Resources

Thư mục này chứa các tài nguyên dùng chung giữa phiên bản Web và Android.

## Files

### config.json
Cấu hình chung của ứng dụng:
- Thông tin app (name, version)
- Danh sách tính năng
- CEFR levels
- Topics
- Quiz và Exercise types

### constants.js
Constants cho JavaScript/TypeScript:
- App config
- CEFR levels với colors
- Topics theo category
- Quiz/Exercise types
- SRS intervals
- API endpoints
- Color palette

## Sử dụng

### Web (JavaScript)
```javascript
import { CEFR_LEVELS, TOPICS, API_ENDPOINTS } from '../shared/constants.js';
```

### Android (nếu dùng React Native)
```javascript
import { COLORS, QUIZ_TYPES } from '../../shared/constants';
```

### Python Backend
```python
import json
with open('../shared/config.json') as f:
    config = json.load(f)
```
