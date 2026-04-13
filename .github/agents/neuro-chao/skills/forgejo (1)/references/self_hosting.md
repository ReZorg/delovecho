# Forgejo Self-Hosting Guide

This guide provides a comprehensive overview of self-hosting a production-ready Forgejo instance, covering everything from initial setup and hardware sizing to security hardening and ongoing maintenance. It synthesizes official documentation and community best practices to help you deploy a stable, scalable, and secure Git service.

## 1. Installation Methods

Forgejo offers several installation methods, each with its own advantages. For production environments, **Docker is the recommended approach** due to its isolation, reproducibility, and ease of management. [1]

| Method | Best For | Pros | Cons |
| :--- | :--- | :--- | :--- |
| **Docker** | Most use cases, from small to large deployments | Easy setup, dependency isolation, scalability, official images | Requires Docker knowledge |
| **Binary** | Bare-metal or non-containerized environments | High performance, direct system integration | Manual dependency management, more complex upgrades |
| **Podman** | Rootless container deployments | Enhanced security (rootless), systemd integration | Less common than Docker, newer ecosystem |
| **From Source** | Developers and custom builds | Full control over build process | Requires Go/Node.js toolchain, most complex setup |

### Docker Compose Example (Recommended)

Using Docker Compose is the most straightforward way to manage a multi-container Forgejo setup, including the database and Actions runner. Below is a production-ready `docker-compose.yml` template using PostgreSQL.

```yaml
version: "3.8"

networks:
  forgejo:
    external: false

services:
  server:
    image: codeberg.org/forgejo/forgejo:13
    container_name: forgejo
    environment:
      - USER_UID=1000
      - USER_GID=1000
      - FORGEJO__database__DB_TYPE=postgres
      - FORGEJO__database__HOST=db:5432
      - FORGEJO__database__NAME=forgejo
      - FORGEJO__database__USER=forgejo
      - FORGEJO__database__PASSWD=${FORGEJO_DB_PASSWORD}
      # -- Recommended Production Settings --
      - FORGEJO__server__ROOT_URL=https://git.example.com
      - FORGEJO__server__DISABLE_SSH=false
      - FORGEJO__server__SSH_PORT=222
      - FORGEJO__service__ENABLE_CAPTCHA=true
      - FORGEJO__security__LOGIN_REMEMBER_DAYS=365
      - FORGEJO__repository.signing__DEFAULT_TRUST_MODEL=committer
    restart: always
    networks:
      - forgejo
    volumes:
      - ./forgejo:/data
      - /etc/localtime:/etc/localtime:ro
    ports:
      - "3000:3000"
      - "222:22"
    depends_on:
      - db

  db:
    image: postgres:14
    container_name: forgejo-db
    restart: always
    environment:
      - POSTGRES_USER=forgejo
      - POSTGRES_PASSWORD=${FORGEJO_DB_PASSWORD}
      - POSTGRES_DB=forgejo
    networks:
      - forgejo
    volumes:
      - ./postgres:/var/lib/postgresql/data
```

*Create a `.env` file in the same directory with the content `FORGEJO_DB_PASSWORD=your_secure_password`.*

## 2. Optimal Hosting Specifications

Hardware requirements scale with user count, repository size, and CI/CD usage. Forgejo is known for being lightweight, but providing adequate resources is crucial for performance. [2]

| Tier | Users | vCPUs | RAM | Storage | Database | Cache |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Personal/Hobby** | 1-5 | 1 | 1-2 GB | 25GB+ SSD | SQLite | In-memory |
| **Small Team** | 5-20 | 2 | 2-4 GB | 50GB+ SSD | PostgreSQL | In-memory |
| **Medium Org** | 20-100 | 4 | 8 GB | 100GB+ SSD | PostgreSQL | Redis |
| **Large Scale** | 100+ | 8+ | 16+ GB | 300GB+ NVMe | PostgreSQL | Redis |

> **Note:** These are general guidelines. Heavy CI/CD usage (Forgejo Actions) will significantly increase CPU and RAM requirements. Monitor your instance's performance and scale accordingly.

## 3. Production Configuration

### Database & Cache

- **Database**: For any multi-user instance, **PostgreSQL** is strongly recommended over SQLite for its concurrency and performance under load. [3]
- **Cache**: For instances with high activity, offloading cache to **Redis** reduces load on the main application. For smaller instances, the built-in `twoqueue` adapter is a good improvement over the default. [3]

### Reverse Proxy

A reverse proxy is essential for handling HTTPS, custom domains, and security headers. **Nginx** and **Caddy** are excellent choices.

#### Nginx Configuration Example

This configuration includes HTTPS, HTTP/2, and security headers.

```nginx
server {
    listen 80;
    server_name git.example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name git.example.com;

    ssl_certificate /etc/letsencrypt/live/git.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/git.example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 512M; # Allow large repo pushes
    }
}
```

## 4. Backup and Restore

Regular backups are critical. The primary tool is the `forgejo dump` command, which creates a zip archive of the database, configuration, and repositories. [4]

### Backup Procedure

1.  **Execute the dump command** inside the Forgejo container:
    ```bash
    docker exec -u git forgejo-server /bin/sh -c 
      "/usr/local/bin/forgejo dump -c /data/forgejo/conf/app.ini -f /data/forgejo-dump.zip"
    ```
2.  **Copy the backup** from the container to a safe, external location:
    ```bash
    docker cp forgejo-server:/data/forgejo-dump.zip /path/to/backups/
    ```

### Restore Procedure

Restoring involves stopping Forgejo, clearing the data directories, and running the restore command. This is a destructive operation.

> **Warning:** Always test your restore procedure on a separate, non-production server to ensure your backups are valid.

## 5. Security Hardening

- **Use a Reverse Proxy with HTTPS**: Never expose Forgejo directly to the internet over HTTP.
- **Enable CAPTCHA**: Set `ENABLE_CAPTCHA = true` in `app.ini` if you have open registration to prevent spam bots.
- **Configure SSH**: Use the built-in SSH server or carefully configure your system's SSHD to pass the `GIT_PROTOCOL` environment variable.
- **Regular Updates**: Keep Forgejo and all system packages up to date to patch security vulnerabilities.
- **Firewall**: Restrict access to necessary ports only (e.g., 80, 443, and your SSH port).

## 6. Forgejo Actions (CI/CD)

To enable CI/CD, you need to run one or more **Forgejo Runners**.

1.  **Enable Actions** in your `app.ini`:
    ```ini
    [actions]
    ENABLED = true
    ```
2.  **Deploy a Runner**: The runner can be a separate Docker container. You will need to generate a registration token from your Forgejo instance (Admin Panel -> Actions -> Runners).

## References

[1] Forgejo Documentation. (2026). *Installation with Docker*. [https://forgejo.org/docs/next/admin/installation/docker/](https://forgejo.org/docs/next/admin/installation/docker/)
[2] Various Authors. (2025). *Community discussions on hardware sizing*. Reddit. [https://www.reddit.com/r/selfhosted/](https://www.reddit.com/r/selfhosted/)
[3] Forgejo Documentation. (2026). *Recommended Settings and Tips*. [https://forgejo.org/docs/next/admin/setup/recommendations/](https://forgejo.org/docs/next/admin/setup/recommendations/)
[4] Forgejo Documentation. (2026). *Forgejo CLI*. [https://forgejo.org/docs/next/admin/command-line/](https://forgejo.org/docs/next/admin/command-line/)
