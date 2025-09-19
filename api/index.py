def handler(request):
    import json
    
    # Simple test response
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            'message': 'API is working',
            'path': request.url.path,
            'method': request.method
        })
    }
