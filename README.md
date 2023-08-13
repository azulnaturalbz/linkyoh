# Linkyoh

## Initial Setup

### 1. Clone the Repository

To clone the repository, run the following commands:

```bash
git clone [repository_url]
cd [repository_directory]
```

### 2. Set Environment Variables

Before starting the application, ensure you've set all necessary environment variables. Copy the provided .env.example file to a new .env file and adjust the values accordingly:

```bash
cp .env.example .env
nano .env # Or use your preferred text editor
```

### 3. Domain Configuration

Ensure that the domain's A record is correctly pointing to the desired IP address.

### 4. Virtual Host Configuration
If using a load balancer, make sure the virtual host for port 80 does not redirect to port 443. This is crucial because the backend server has its own Nginx configuration that handles SSL/TLS using Certbot.

If the load balancer auto-generates a virtual host configuration that redirects port 80 to 443 after obtaining a certificate, you must comment out this redirect. This step ensures the backend server can renew its certificate without issues. Alternatively, you can disable the redirect entirely, as the backend server will handle this.

### 5. Start the Application
To start the application, use Docker Compose:

```bash
docker-compose up --build -d
```

This command will build the Docker images (if needed) and start the containers in detached mode. It will also run any necessary initialization steps like database migrations.

Once the application is up and running, you should be able to access it via the configured domain name.

## Development
If the process generates new certificates for the backend commit them to the repository. 
This is necessary because the load balancer will not be able to renew the certificates on its own.