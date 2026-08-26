<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi" alt="FastAPI">
  <img src="https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
  <img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
  <img src="https://img.shields.io/badge/Stripe-626CD9?style=for-the-badge&logo=Stripe&logoColor=white" alt="Stripe">
</p>

<h1 align="center">🛒 FastAPI E-Commerce API</h1>

<p align="center">
  <strong>High-Performance REST API for E-Commerce Platforms</strong><br>
  Built with FastAPI, SQLAlchemy 2.0 (Async), PostgreSQL, and Redis caching.
</p>

---

## ✨ Features

- **🛍️ Product Catalog**: Categories, full-text search, filtering, and pagination.
- **🏎️ Redis Shopping Cart**: Blazing fast in-memory cart operations.
- **📦 Order Management**: Seamless checkout flow with stock reservation and inventory management.
- **💳 Stripe Integration**: Checkout sessions and webhook handling for secure payments.
- **🔐 JWT Authentication**: Secure password hashing (Bcrypt) and Bearer tokens.
- **📊 Admin Dashboard**: Statistics, revenue tracking, and low-stock alerts.
- **🐳 Docker Ready**: Full containerized setup with `docker-compose`.
- **⚙️ CI/CD Pipeline**: GitHub Actions for linting, testing, and Docker builds.

## 🚀 Quick Start (Docker)

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/fastapi-ecommerce-api.git
cd fastapi-ecommerce-api

# Setup environment
cp .env.example .env

# Start the full stack (API, Postgres, Redis)
docker-compose up -d

# Access the interactive API Documentation
open http://localhost:8000/docs
```

## 📚 API Endpoints

### 🔐 Authentication (`/api/v1`)
- `POST /login/access-token` - Authenticate and get JWT token.
- `POST /users/` - Register a new user.
- `GET /users/me` - Get current user profile.

### 🛍️ Catalog (`/api/v1/products`, `/api/v1/categories`)
- `GET /products/` - List products (with search/filter).
- `GET /products/{id}` - Get product details.
- `GET /categories/` - List categories.

### 🛒 Cart & Orders (`/api/v1/cart`, `/api/v1/orders`)
- `GET /cart/` - View shopping cart.
- `POST /cart/items` - Add item to cart.
- `DELETE /cart/` - Clear cart.
- `POST /orders/` - Checkout (creates order, reserves stock).
- `GET /orders/` - Order history.

### 💳 Payments (`/api/v1/payments`)
- `POST /payments/create-checkout-session/{order_id}` - Generate Stripe checkout URL.
- `POST /payments/webhook` - Stripe webhook listener.

### 📊 Admin (`/api/v1/admin`)
- `GET /admin/dashboard-stats` - Revenue, active products, and stock alerts.
