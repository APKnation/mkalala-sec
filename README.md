# Mkalala Secondary School Management System

## Cloudflare Pages Deployment

### Quick Setup

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Cloudflare Pages deployment"
   git push origin main
   ```

2. **Deploy to Cloudflare Pages**
   - Go to [Cloudflare Dashboard](https://dash.cloudflare.com/)
   - Navigate to Pages
   - Connect to GitHub repository
   - Select `APKnation/mkalala-sec` repo
   - Use these build settings:
     ```
     Build command: pip install -r requirements.txt && python manage.py collectstatic --noinput
     Build output directory: staticfiles
     Root directory: /
     ```

3. **Environment Variables**
   Set these in Cloudflare Pages Settings:
   ```
   DEBUG = false
   SECRET_KEY = your-production-secret-key
   DATABASE_URL = your-database-connection-string
   ```

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Features

- **Student Management**: Complete enrollment and academic records
- **Tanzania O-Level**: Full curriculum support for Forms 1-4
- **Financial Management**: Fee tracking and payment processing
- **User Management**: Role-based access control
- **Communication**: Announcements and notifications
- **Reports**: Comprehensive analytics and reporting

### Technology Stack

- **Backend**: Django 4.2.11
- **API**: Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **Static Files**: WhiteNoise + Cloudflare CDN
- **Deployment**: Cloudflare Pages Functions

### Project Structure

```
mkalala-sec/
|-- school_management/        # Django project settings
|-- core/                    # Main app with models, views, etc.
|-- static/                  # Static assets
|-- templates/               # HTML templates
|-- media/                   # User uploaded files
|-- requirements.txt         # Python dependencies
|-- wrangler.toml           # Cloudflare configuration
|-- _worker.py              # Cloudflare Pages Functions
```

### Deployment Notes

- **Static Files**: Served via Cloudflare CDN
- **Database**: Requires external PostgreSQL database
- **Media Files**: Configure Cloudflare R2 or similar storage
- **Security**: SSL, CSRF protection, and security headers enabled

### Support

For deployment issues, check:
1. Cloudflare Pages build logs
2. Environment variables configuration
3. Database connection settings
4. Static files collection

---

**Mkalala Secondary School**  
*"To the Stars Through Hard Working"*
