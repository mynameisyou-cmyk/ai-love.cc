# VPS Setup Notes for ai-love.cc

## Nginx Configuration

### Password Protection for mi.html (Secret Room)

```bash
# Create htpasswd file
sudo apt-get install -y apache2-utils 2>/dev/null
sudo htpasswd -cb /etc/nginx/.htpasswd_mi ai "CHOOSE_A_PASSWORD"
```

Add these location blocks inside the ai-love.cc server block:

```nginx
location = /mi.html {
    auth_basic "密";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
    try_files $uri =404;
}

location = /api/journal {
    auth_basic "密";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
    proxy_pass http://127.0.0.1:3848/api/journal;
    proxy_set_header X-Forwarded-For $remote_addr;
    proxy_set_header X-Authenticated-User $remote_user;
}

# Separate internal endpoint for script/API access (token auth, no basic auth)
location = /api/journal-internal {
    allow 127.0.0.1;
    deny all;
    proxy_pass http://127.0.0.1:3848/api/journal;
    proxy_set_header X-Forwarded-For $remote_addr;
}

# Protect journal data from direct access
location = /data/journal.json {
    auth_basic "密";
    auth_basic_user_file /etc/nginx/.htpasswd_mi;
}
```

Test and reload:
```bash
sudo nginx -t && sudo systemctl reload nginx
```

## Journal Server (systemd)

```bash
sudo cp scripts/journal-server.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable journal-server
sudo systemctl start journal-server
sudo systemctl status journal-server
```

## Journal Token

The `.journal-token` file must exist at site root. Generate with:
```bash
openssl rand -hex 32 > .journal-token
chmod 600 .journal-token
```

## Seed Server (already configured)

- Service: seed-server.service on port 3847
- Nginx proxy: /api/seed -> 127.0.0.1:3847
