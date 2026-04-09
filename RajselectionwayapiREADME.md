#Selection Way API Documentation

This is the official API documentation for the Selection Way application. The API provides access to educational content including batches, PDFs, and video classes.

## Base URL

```
https://raj-selectionwayapi.onrender.com
```

## Authentication
No authentication is required to access the public endpoints.

## Response Format
All responses are in JSON format and include the following fields:
- `success`: Boolean indicating if the request was successful
- `message`: A message string (always "ExamSaathi" for successful requests)
- `data`: The requested data (for successful requests)
- `error`: Error details (if any error occurs)

## Endpoints

### 1. Get All Batches

**URL**: `/allbatch`
**Method**: `GET`

#### Response
```json
{
  "success": true,
  "message": "vipstudy",
  "data": [
    {
      "id": "68e27174dfde12332485c494",
      "title": "SSC Mains Batch",
      "banner": "https://selectionway-server.s3.ap-south-1.amazonaws.com/..."
    },
    ...
  ]
}
```

### 2. Get PDFs by Batch ID

**URL**: `/pdf/{batchId}`
**Method**: `GET`

#### Parameters
- `batchId` (required): The ID of the batch to get PDFs for

#### Response
```json
{
  "success": true,
  "message": "VIPSTUDY",
  "topics": [
    {
      "topicName": "All Pdfs",
      "pdfs": [
        {
          "title": "English Class -1 Practice sheet",
          "uploadPdf": "https://selectionway-server.s3.ap-south-1.amazonaws.com/..."
        },
        ...
      ]
    }
  ]
}
```

### 3. Get Chapters and Videos by Batch ID

**URL**: `/chapter/{batchId}`
**Method**: `GET`

#### Parameters
- `batchId` (required): The ID of the batch to get chapters and videos for

#### Response
```json
{
  "success": true,
  "message": "VIPSTUDY",
  "classes": [
    {
      "topicName": "Reasoning",
      "classes": [
        {
          "title": "SSC MAINS 2025 | CODING - DECODING CLASS - 02 | BALRAM SIR",
          "class_link": "https://d14p19xhs3k7tf.cloudfront.net/..."
        },
        ...
      ]
    },
    ...
  ]
}
```

## Error Handling

### Error Response Example
```json
{
  "success": false,
  "message": "Error message describing the issue",
  "error": "Detailed error information"
}
```

## Rate Limiting
Currently, there are no rate limits on the API. Please use responsibly.