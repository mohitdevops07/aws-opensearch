**Project: Secure AWS OpenSearch Setup with Pulumi**

This repository provides guidance on setting up a secure AWS OpenSearch environment using Pulumi infrastructure as code. It includes two main directories:

1. **Common Config**: This directory contains essential configuration files where you can define parameters such as OpenSearch username, password, etc. While these files are kept in plain text for clarity, it's recommended to use SOPS for encryption using an AWS KMS key before deploying them.

2. **OpenSearch Setup**: Within this directory, infrastructure for OpenSearch is created, including the Virtual Private Cloud (VPC) and the OpenSearch domain under private subnets. To access the OpenSearch dashboard securely over the internet, an EC2 proxy instance with Nginx installed on top of an Application Load Balancer is set up.

### Configuration

Before proceeding, ensure you have configured the following:

- AWS credentials properly set up on your local environment.
- Pulumi CLI installed and configured.

### Usage

1. **Common Configuration**:
   - Navigate to the `common-config` directory.
   - Modify the configuration files as needed, such as `opensearch-config.yaml`, to specify your OpenSearch username, password, etc.
   - Optionally, encrypt these files using SOPS and an AWS KMS key for enhanced security.

2. **OpenSearch Setup**:
   - Navigate to the `opensearch-setup` directory.
   - Execute Pulumi commands to deploy the infrastructure defined in the code.
   - Ensure that the necessary AWS resources are provisioned, including the VPC and OpenSearch domain.

3. **Nginx Configuration**:
   - Once the infrastructure is deployed, configure Nginx on the EC2 proxy instance.
   - Use the provided Nginx virtual host configuration to enable access to the OpenSearch dashboard securely over the internet.
   - Replace placeholders like `REPLACE_WITH_HOSTNAME` and `REPLACE_WITH_OPENSEARCH_DOMAIN_URL` with appropriate values.
### Nginx Virtual Host Configuration

To enable access to the OpenSearch dashboard securely over the internet, use the following Nginx virtual host configuration:

```nginx
server {
    listen 80;
    server_name REPLACE_WITH_HOSTNAME;            #test.com
    client_max_body_size 24000M;

    location / {
        proxy_pass REPLACE_WITH_OPENSEARCH_DOMAIN_URL;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Add security headers
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Content-Type-Options "nosniff";
        add_header Referrer-Policy "no-referrer-when-downgrade";
    }

    location ~ /(log|sign|fav|forgot|change|saml|oauth2) {
        proxy_pass REPLACE_WITH_OPENSEARCH_DOMAIN_URL;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Add security headers
        add_header X-Frame-Options "SAMEORIGIN";
        add_header X-XSS-Protection "1; mode=block";
        add_header X-Content-Type-Options "nosniff";
        add_header Referrer-Policy "no-referrer-when-downgrade";
    }
}


4. **Restart Nginx**:
   - After configuring the virtual host, link it with `sites-enabled` and restart the Nginx service.
   ```
   sudo ln -s /etc/nginx/sites-available/test.com /etc/nginx/sites-enabled/
   sudo systemctl restart nginx
   ```

### Accessing OpenSearch Dashboard

Once the setup is complete, you can access the OpenSearch dashboard in your browser using the following URL:
```
https://test.com/_dashboards
```

### Note

- This setup assumes a secure deployment environment and recommends encrypting sensitive configuration files.
- Ensure proper IAM permissions are assigned to resources for secure access and management.
- Regularly review and update security configurations to adhere to best practices and mitigate potential vulnerabilities.

For any further assistance or inquiries, please refer to the documentation or reach out to the project maintainers.
