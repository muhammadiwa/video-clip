# API Documentation

Base URL: `http://localhost:8000`

## Projects

### Create Project
```http
POST /api/projects/
Content-Type: application/json

{
  "name": "My Project",
  "description": "Optional description",
  "source_language": "en",
  "target_platform": "shorts",
  "target_duration": 60,
  "aspect_ratio": "9:16"
}
```

### Get All Projects
```http
GET /api/projects/?skip=0&limit=100
```

### Get Project by ID
```http
GET /api/projects/{project_id}
```

### Delete Project
```http
DELETE /api/projects/{project_id}
```

## Videos

### Upload Video
```http
POST /api/videos/upload
Content-Type: multipart/form-data

Form Data:
- project_id: integer
- file: video file
```

### Get Project Videos
```http
GET /api/videos/project/{project_id}
```

### Get Video by ID
```http
GET /api/videos/{video_id}
```

### Delete Video
```http
DELETE /api/videos/{video_id}
```

## Clips

### Create Clip
```http
POST /api/clips/
Content-Type: application/json

{
  "project_id": 1,
  "name": "Clip 1",
  "description": "Optional",
  "start_time": 0.0,
  "end_time": 30.0,
  "viral_score": 8.5,
  "category": "hook"
}
```

### Get Project Clips
```http
GET /api/clips/project/{project_id}
```

### Update Clip
```http
PUT /api/clips/{clip_id}
Content-Type: application/json

{
  "name": "Updated name",
  "aspect_ratio": "16:9"
}
```

### Delete Clip
```http
DELETE /api/clips/{clip_id}
```

## Subtitles

### Create Subtitle
```http
POST /api/subtitles/
Content-Type: application/json

{
  "clip_id": 1,
  "text": "Hello world",
  "start_time": 0.0,
  "end_time": 2.0,
  "language": "en",
  "style": {
    "font": "Arial",
    "fontSize": 24,
    "color": "#ffffff"
  }
}
```

### Get Clip Subtitles
```http
GET /api/subtitles/clip/{clip_id}
```

### Update Subtitle
```http
PUT /api/subtitles/{subtitle_id}
Content-Type: application/json

{
  "text": "Updated text",
  "style": {...}
}
```

### Delete Subtitle
```http
DELETE /api/subtitles/{subtitle_id}
```

## Response Formats

### Success Response
```json
{
  "id": 1,
  "name": "Project Name",
  "status": "created",
  "created_at": "2024-01-01T00:00:00"
}
```

### Error Response
```json
{
  "detail": "Error message"
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `422` - Validation Error
- `500` - Internal Server Error
