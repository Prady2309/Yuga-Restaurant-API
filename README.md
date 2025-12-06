# Yuga - Restaurant & Food Delivery API

![Django](https://img.shields.io/badge/Django-4.x-092E20?style=flat-square&logo=django)
![Django REST Framework](https://img.shields.io/badge/DRF-3.x-red?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?style=flat-square&logo=postgresql)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

## Overview

**Yuga** is a modern, production-ready REST API for restaurant and food delivery platforms. Built with **Django** and **Django REST Framework**, it provides comprehensive backend services for menu management, user authentication, order processing, and delivery crew management.

The API is designed with enterprise-level security, role-based access control (RBAC), and scalable architecture suitable for multi-restaurant platforms.

---

## 🎯 Key Features

### 1. **Menu & Catalog Management**
- Browse menu items organized by categories
- Search, filter, and sort menu items by price and popularity
- Featured items highlighting
- RESTful CRUD operations for administrators

### 2. **User Authentication & Authorization**
- Token-based authentication (Django REST Framework Token Auth)
- Role-based access control with user groups:
  - **Customers** - Browse menu, place orders, manage cart
  - **Managers** - Manage menu, approve orders, assign delivery crew
  - **Delivery Crew** - Accept and complete deliveries
  - **Admin** - Full system access

### 3. **Shopping Cart Management**
- Add/remove items to cart
- Automatic price calculation
- Per-user cart isolation
- Bulk cart operations (clear all)

### 4. **Order Management**
- Create orders from cart items
- Order status tracking
- Delivery crew assignment
- Order history and retrieval
- Order-level and item-level tracking

### 5. **Advanced Filtering & Pagination**
- Django Filter Backend integration
- Search by title and category
- Price range filtering
- Paginated responses for performance
- Custom ordering capabilities

### 6. **Audit & Compliance**
- Role-based permission enforcement
- Request validation and error handling
- Consistent HTTP status codes
- Detailed error messages

---

## 📋 Tech Stack

| Component | Technology |
|-----------|------------|
| **Framework** | Django 4.x |
| **API Framework** | Django REST Framework 3.x |
| **Database** | PostgreSQL 13+ |
| **Authentication** | Token Authentication (DRF) |
| **Filtering** | Django Filter |
| **Pagination** | PageNumberPagination |
| **Python Version** | 3.9+ |

---

## 🏗️ Project Structure

```
yuga/
├── manage.py                 # Django management script
├── requirements.txt          # Project dependencies
├── README.md                 # This file
│
├── yuga/                     # Main project settings
│   ├── settings.py          # Django configuration
│   ├── urls.py              # Root URL routing
│   ├── wsgi.py              # WSGI application
│   └── asgi.py              # ASGI application
│
└── restaurant/              # Django app (main backend logic)
    ├── models.py            # Database models (Category, MenuItem, Cart, Order, OrderItem)
    ├── views.py             # API views and viewsets
    ├── serializers.py       # Data serialization/deserialization
    ├── urls.py              # App-specific URL routing
    ├── admin.py             # Django admin configuration
    ├── apps.py              # App configuration
    ├── tests.py             # Unit tests
    ├── migrations/          # Database migrations
    └── __pycache__/         # Python cache files
```

---

## 📊 Database Models

### Category
```python
- id (Primary Key)
- slug (String, unique)
- title (String, indexed)
```

### MenuItem
```python
- id (Primary Key)
- title (String, indexed)
- price (Decimal, indexed)
- featured (Boolean, indexed)
- category (Foreign Key → Category)
```

### Cart
```python
- id (Primary Key)
- user (Foreign Key → User)
- menuitem (Foreign Key → MenuItem)
- quantity (SmallInteger)
- unit_price (Decimal)
- price (Decimal)
- Constraint: Unique(menuitem, user)
```

### Order
```python
- id (Primary Key)
- user (Foreign Key → User)
- delivery_crew (Foreign Key → User, nullable)
- status (Boolean, indexed)
- total (Decimal)
- date (Date, indexed)
```

### OrderItem
```python
- id (Primary Key)
- order (Foreign Key → Order)
- menuitem (Foreign Key → MenuItem)
- quantity (SmallInteger)
- unit_price (Decimal)
- price (Decimal)
- Constraint: Unique(order, menuitem)
```

---

## 🔌 API Endpoints

### Menu Items
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/api/menu-items/` | List all menu items | Public (read-only) |
| POST | `/api/menu-items/` | Create menu item | Manager/Admin |
| GET | `/api/menu-items/{id}/` | Retrieve menu item | Public |
| PUT | `/api/menu-items/{id}/` | Update menu item | Manager/Admin |
| DELETE | `/api/menu-items/{id}/` | Delete menu item | Manager/Admin |

**Filters:** `?category=<slug>&fromPrice=<min>&toPrice=<max>&search=<query>&orderBy=<field>`

### Categories
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/api/category/` | List all categories | Public |
| POST | `/api/category/` | Create category | Manager/Admin |
| GET | `/api/category/{id}/` | Retrieve category | Public |
| PUT | `/api/category/{id}/` | Update category | Manager/Admin |
| DELETE | `/api/category/{id}/` | Delete category | Manager/Admin |

### Cart
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/api/cart/menu-items/` | View cart | Customer (authenticated) |
| POST | `/api/cart/menu-items/` | Add item to cart | Customer |
| DELETE | `/api/cart/menu-items/` | Clear cart | Customer |

**POST Body:**
```json
{
  "menuitem_id": 5,
  "quantity": 2
}
```

**Response:**
```json
{
  "items": [...],
  "total_items": 5,
  "total_price": 1250.50
}
```

### Orders
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/api/orders/` | List orders | Customer (own), Manager/Admin (all) |
| POST | `/api/orders/` | Create order from cart | Customer |
| GET | `/api/orders/{id}/` | Retrieve order | Customer (own), Manager/Admin (all) |
| DELETE | `/api/orders/{id}/` | Delete order | Manager/Admin |

### User Group Management
| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/api/groups/manager/users/` | List managers | Admin |
| POST | `/api/groups/manager/users/` | Add manager | Admin |
| DELETE | `/api/groups/manager/users/{id}/` | Remove manager | Admin |
| GET | `/api/groups/delivery-crew/users/` | List delivery crew | Admin |
| POST | `/api/groups/delivery-crew/users/` | Add delivery crew | Admin |
| DELETE | `/api/groups/delivery-crew/users/{id}/` | Remove delivery crew | Admin |

---

## 🔐 Authentication & Authorization

### Token Authentication
Every authenticated request requires the token header:
```bash
Authorization: Token <your-token-here>
```

### User Roles & Permissions

#### 🛍️ **Customer**
- Browse menu items and categories
- Manage personal cart
- Create and view personal orders
- Cannot manage menu, users, or other orders

#### 👨‍💼 **Manager**
- All Customer permissions
- Create, update, delete menu items
- Manage categories
- View all orders
- Assign delivery crew to orders
- Manage customer accounts

#### 🚚 **Delivery Crew**
- View assigned orders
- Update order status
- Cannot modify menu or orders

#### 👤 **Admin**
- Full system access
- User group management
- Database administration
- All CRUD operations

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 13+
- Git
- pip or Poetry

### Step 1: Clone Repository
```bash
git clone https://github.com/your-org/yuga.git
cd yuga
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a `.env` file in the project root:
```env
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost:5432/yuga_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 5: Configure Database
Update `settings.py` with your PostgreSQL credentials:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'yuga_db',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### Step 6: Run Migrations
```bash
python manage.py migrate
```

### Step 7: Create Superuser
```bash
python manage.py createsuperuser
```

### Step 8: Create User Groups
```bash
python manage.py shell
```
```python
from django.contrib.auth.models import Group

Group.objects.create(name='Customer')
Group.objects.create(name='Manager')
Group.objects.create(name='Delivery')
Group.objects.create(name='Admin')
```

### Step 9: Load Sample Data (Optional)
```bash
python manage.py loaddata initial_data.json
```

### Step 10: Run Development Server
```bash
python manage.py runserver
```

API will be available at `http://localhost:8000/api/`

---

## 📝 Example API Requests

### 1. Get Authentication Token
```bash
curl -X POST http://localhost:8000/api-token-auth/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user123", "password": "pass123"}'
```

**Response:**
```json
{
  "token": "abcdef123456789"
}
```

### 2. Browse Menu Items
```bash
curl -X GET "http://localhost:8000/api/menu-items/?category=pizzas&toPrice=500" \
  -H "Authorization: Token abcdef123456789"
```

### 3. Add Item to Cart
```bash
curl -X POST http://localhost:8000/api/cart/menu-items/ \
  -H "Authorization: Token abcdef123456789" \
  -H "Content-Type: application/json" \
  -d '{
    "menuitem_id": 5,
    "quantity": 2
  }'
```

### 4. Create Order
```bash
curl -X POST http://localhost:8000/api/orders/ \
  -H "Authorization: Token abcdef123456789" \
  -H "Content-Type: application/json" \
  -d '{}'
```

### 5. Assign Delivery Crew
```bash
curl -X PATCH http://localhost:8000/api/orders/10/ \
  -H "Authorization: Token abcdef123456789" \
  -H "Content-Type: application/json" \
  -d '{"delivery_crew": 15}'
```

---

## 🧪 Testing

### Run All Tests
```bash
python manage.py test
```

### Run Specific App Tests
```bash
python manage.py test restaurant
```

### Run with Coverage Report
```bash
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

---

## 🔍 Code Quality & Best Practices

### Implemented Features
✅ **DRF Generics & ViewSets** - Reusable, maintainable views  
✅ **Django Filters** - Advanced filtering without custom code  
✅ **Pagination** - Efficient data handling  
✅ **Permission Classes** - `DjangoModelPermissions`, `DjangoModelPermissionsOrAnonReadOnly`  
✅ **Serializer Validation** - Field-level and object-level validation  
✅ **Database Constraints** - Unique constraints at model level  
✅ **Query Optimization** - `select_related()` for foreign keys  
✅ **Comprehensive Error Handling** - Meaningful HTTP status codes  
✅ **API Documentation** - Browsable API interface (with DRF)

### Performance Optimizations
- Database indexing on frequently queried fields
- Query optimization with `select_related()`
- Pagination for large datasets
- Efficient serializer design

---

## 📦 Dependencies

Core dependencies (see `requirements.txt`):
```
Django==4.2.x
djangorestframework==3.14.x
django-filter==23.x
psycopg2-binary==2.9.x
python-decouple==3.x
gunicorn==20.x
```

---

## 🌐 Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn yuga.wsgi --bind 0.0.0.0:8000
```

### Docker Deployment
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "yuga.wsgi:application", "--bind", "0.0.0.0:8000"]
```

### Environment Variables for Production
```bash
DEBUG=False
SECRET_KEY=<generate-strong-key>
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DATABASE_URL=postgresql://user:password@prod-db:5432/yuga_prod
```

---

## 🐛 Troubleshooting

### Issue: "No such table" error
**Solution:** Run migrations
```bash
python manage.py migrate
```

### Issue: Permission Denied when creating menu items
**Solution:** Ensure user belongs to Manager group
```bash
python manage.py shell
from django.contrib.auth.models import User, Group
user = User.objects.get(username='your_user')
manager = Group.objects.get(name='Manager')
manager.user_set.add(user)
```

### Issue: CORS errors in frontend
**Solution:** Add to `settings.py`:
```python
INSTALLED_APPS = [
    'corsheaders',
    ...
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8080",
]
```

---

## 📚 API Documentation

### OpenAPI/Swagger (Optional)
To enable interactive API docs, install:
```bash
pip install drf-spectacular
```

Add to `INSTALLED_APPS`:
```python
'drf_spectacular',
```

Access at: `http://localhost:8000/api/schema/swagger/`

---

## 🤝 Contributing

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Code Standards
- Follow PEP 8
- Write docstrings for all functions
- Add unit tests for new features
- Run `black` for code formatting
- Use meaningful commit messages

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👥 Support & Contact

**Project Maintainer:** Your Organization  
**Email:** support@yuga.restaurant  
**Issues:** [GitHub Issues](https://github.com/your-org/yuga/issues)  
**Discussions:** [GitHub Discussions](https://github.com/your-org/yuga/discussions)

---

## 🎓 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework Guide](https://www.django-rest-framework.org/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [Best Practices for RESTful APIs](https://restfulapi.net/)
- [Django Security](https://docs.djangoproject.com/en/stable/topics/security/)

---

## 🔒 Security Considerations

✅ **HTTPS Only** - Always use HTTPS in production  
✅ **CSRF Protection** - Enabled by default  
✅ **SQL Injection Prevention** - Using Django ORM  
✅ **XSS Protection** - DRF serializers escape output  
✅ **Rate Limiting** - Implement via Throttle classes (TODO)  
✅ **API Key Rotation** - Token-based auth with expiry (TODO)  

---

## 📈 Future Roadmap

- [ ] Advanced order tracking with real-time updates
- [ ] Payment gateway integration (Stripe/PayPal)
- [ ] Push notifications for customers
- [ ] Rating & review system
- [ ] Analytics dashboard
- [ ] Multi-language support
- [ ] GraphQL API endpoint
- [ ] Mobile app API optimization

---

**Last Updated:** December 2025  
**Version:** 1.0.0  
**Status:** Production Ready
