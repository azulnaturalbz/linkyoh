# Celery Worker State DB Fix

This document explains the changes made to fix the Celery worker state DB issue and provides instructions for testing and deploying the changes.

## Issue

The Celery worker was failing with the following error:

```
AttributeError: 'Settings' object has no attribute 'worker_state_db'
```

This error occurs because the Celery worker is trying to access the `worker_state_db` setting, which is not being properly loaded from the Django settings.

## Changes Made

1. Added the `CELERY_WORKER_STATE_DB` setting to `settings.py`:
   ```python
   CELERY_WORKER_STATE_DB = os.path.join(BASE_DIR, 'celery_worker_state.db')
   ```

2. Updated the Docker Compose configuration in `docker-compose.unified.yml` to:
   - Change the volume mount path for Celery services from `/app` to `/linkyoh` to match the web service
   - Add all necessary environment variables to the Celery services
   - Add the `.env` file to the Celery services

These changes ensure that the Celery worker and beat services have access to the same Django settings as the web service, including the `CELERY_WORKER_STATE_DB` setting.

## Testing the Changes

To test the changes, follow these steps:

1. Rebuild and restart the Docker containers:
   ```bash
   docker-compose -f docker-compose.unified.yml down
   docker-compose -f docker-compose.unified.yml up -d --build
   ```

2. Check the logs of the Celery worker to ensure it starts without errors:
   ```bash
   docker-compose -f docker-compose.unified.yml logs -f celery_worker
   ```

3. Check the logs of the Celery beat service to ensure it starts without errors:
   ```bash
   docker-compose -f docker-compose.unified.yml logs -f celery_beat
   ```

4. Verify that the worker state DB file is created in the project directory:
   ```bash
   ls -la celery_worker_state.db
   ```

## Troubleshooting

If you still encounter issues:

1. Ensure that the `.env` file contains all the necessary environment variables
2. Check that the `CELERY_BROKER_URL` environment variable is correctly set
3. Verify that the RabbitMQ service is running and accessible
4. Check the permissions on the project directory to ensure the Celery worker can create and write to the worker state DB file

## Additional Notes

- The worker state DB file is used by Celery to store the state of the worker, including information about currently executing tasks
- This file is not critical for the operation of Celery, but it is required for certain features like task revocation and worker monitoring
- If you're using a custom Docker Compose file, make sure to apply the same changes to it