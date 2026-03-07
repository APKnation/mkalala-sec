# Project Restructure Plan

## Current Issues:
- Too many scattered files and folders
- Duplicate template locations
- Mixed static files
- Unclear organization

## Proposed New Structure:

```
schoolManagement/
├── 📁 school_management/           # Django config (keep as is)
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── 📁 core/                        # Main Django app (keep as is)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── tests.py
│   ├── migrations/                   # Database migrations
│   ├── templatetags/               # Custom template tags
│   └── templates/                   # Internal templates (auth required)
│       ├── activities/
│       ├── communication/
│       ├── exams/
│       ├── fees/
│       ├── library/
│       ├── parent/
│       └── static/
│
├── 📁 templates/                   # Public templates (no auth required)
│   └── core/
│       ├── public_home.html
│       ├── public_about.html
│       ├── public_courses.html
│       ├── public_admissions.html
│       ├── public_contact.html
│       └── login.html
│
├── 📁 static/                      # All static files (consolidate)
│   ├── css/
│   │   ├── style.css
│   │   ├── admin.css
│   │   ├── student.css
│   │   └── public.css
│   ├── js/
│   │   ├── main.js
│   │   ├── admin.js
│   │   ├── student.js
│   │   └── public.js
│   ├── images/
│   │   ├── logo.png
│   │   ├── default-avatar.png
│   │   └── school-bg.jpg
│   └── fonts/
│       └── custom-fonts/
│
├── 📁 media/                       # User uploads (keep as is)
│   ├── student_pics/
│   ├── assignments/
│   ├── documents/
│   └── library/
│
├── 📁 docs/                        # Documentation
│   ├── README.md
│   ├── API.md
│   ├── DEPLOYMENT.md
│   └── TANZANIA_OLEVEL_ENHANCEMENTS.md
│
├── 📁 config/                       # Configuration files
│   ├── .env.example
│   ├── .gitignore
│   ├── requirements.txt
│   ├── requirements_backup.txt
│   └── package.json
│
├── 📁 scripts/                      # Utility scripts
│   ├── setup.sh
│   ├── deploy.sh
│   └── backup.sh
│
├── 📁 logs/                         # Log files
│   └── debug.log
│
├── 📁 node_modules/                 # Node dependencies (keep as is)
│
├── 📁 staticfiles/                   # Django collected static (keep as is)
│
├── 📁 .git/                        # Git repository (keep as is)
│
├── 📄 manage.py                    # Django management script (keep as is)
├── 📄 .force-rebuild               # Deployment trigger (keep as is)
├── 📄 .redeploy                   # Deployment trigger (keep as is)
└── 📄 tailwind.config.js          # Tailwind config (keep as is)
```

## Benefits of New Structure:

### 1. 🎯 Clear Separation
- **Config**: All config files in one place
- **Core App**: Django app logic organized
- **Templates**: Public vs Internal clearly separated
- **Static**: All static assets consolidated
- **Media**: User uploads organized
- **Docs**: Documentation in dedicated folder

### 2. 📁 Better Organization
- **CSS**: Split by purpose (admin, student, public)
- **JavaScript**: Organized by functionality
- **Images**: All media assets together
- **Templates**: Logical grouping by feature
- **Scripts**: Utility scripts separated

### 3. 🚀 Improved Maintainability
- **Easy Navigation**: Clear folder structure
- **Scalable**: Easy to add new features
- **Backup Friendly**: Organized for backups
- **Development**: Clear separation of concerns

### 4. 📱 Performance Benefits
- **Static Optimization**: Consolidated static files
- **Caching**: Better static file management
- **Loading**: Organized asset loading
- **Deployment**: Cleaner deployment process

## Migration Steps:

### Phase 1: Create New Folders
```bash
mkdir -p docs config scripts logs
mkdir -p static/css static/js static/images static/fonts
mkdir -p media/student_pics media/assignments media/documents media/library
```

### Phase 2: Move Configuration Files
```bash
mv .env.example config/
mv .gitignore config/
mv requirements.txt config/
mv requirements_backup.txt config/
mv package.json config/
```

### Phase 3: Move Documentation
```bash
mv README.md docs/
mv TANZANIA_OLEVEL_ENHANCEMENTS.md docs/
```

### Phase 4: Organize Static Files
```bash
# Move existing static files
mv static/css/style.css static/css/  # Keep as main
# Create specific CSS files
touch static/css/admin.css static/css/student.css static/css/public.css

# Organize JS
touch static/js/main.js static/js/admin.js static/js/student.js static/js/public.js

# Move images to proper location
# (if any scattered images exist)
```

### Phase 5: Move Log Files
```bash
mv debug.log logs/
```

### Phase 6: Create Utility Scripts
```bash
# Create setup script
cat > scripts/setup.sh << 'EOF'
#!/bin/bash
echo "Setting up Mkalala Secondary School..."
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
EOF

# Create deploy script
cat > scripts/deploy.sh << 'EOF'
#!/bin/bash
echo "Deploying to production..."
git pull origin main
python manage.py migrate
python manage.py collectstatic --noinput
touch .redeploy
EOF
chmod +x scripts/*.sh
```

### Phase 7: Update Settings (if needed)
```python
# Update static files configuration in settings.py
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## Files to Keep As Is:
- ✅ school_management/ (Django config)
- ✅ core/ (Django app)
- ✅ templates/ (public templates)
- ✅ media/ (user uploads)
- ✅ staticfiles/ (Django collected)
- ✅ .git/ (version control)
- ✅ node_modules/ (dependencies)
- ✅ manage.py (Django script)
- ✅ tailwind.config.js (Tailwind config)

## Final Result:
A clean, professional Django project structure that's:
- 🎯 **Easy to navigate**
- 📁 **Well organized**
- 🚀 **Maintainable**
- 📱 **Performance optimized**
- 🔄 **Deployment ready**
