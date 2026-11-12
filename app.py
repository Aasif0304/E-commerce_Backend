import os
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"
os.environ.setdefault("PSYCOPG_IMPL", "python")

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from database import Base, engine

from models.product_model import Product
from models.product_image_model import ProductImage
from models.user_model import User
from models.category_model import Category
from models.cart_model import CartItem
from models.address_model import Address
from models.order_model import Order
from models.order_item_model import OrderItem

from routes.product_routes import router as product_router
from routes.auth_routes import router as auth_router
from routes.category_routes import router as category_router
from routes.cart_routes import router as cart_router
from routes.address_routes import router as address_router
from routes.order_routes import router as order_router
from routes.admin_routes import router as admin_router


IMG_DIR = Path(__file__).resolve().parent / "img"
IMG_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        Base.metadata.create_all(bind=engine)
        print('Database connected and tables verified successfully.')
    except Exception as e:
        print(f'Warning: Database connection failed during startup: {e}')
        print('Hint: Restart PostgreSQL service with: Restart-Service postgresql-x64-17')
    yield


app = FastAPI(
    title="E-commerce Store API",
    description="FastAPI Backend for E-commerce Product Management with PostgreSQL & Image Uploads",
    version="1.0.0",
    lifespan=lifespan,
    docs_url=None,
)


# CORS Configuration - Allow Frontend Requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1)(:\d+)?$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _convert_binary_schemas(node):
    """Convert OpenAPI 3.1 octet-stream fields to format='binary' so Swagger UI renders file pickers."""
    if isinstance(node, dict):
        if (
            node.get("type") == "string"
            and node.get("contentMediaType") == "application/octet-stream"
        ):
            node.pop("contentMediaType", None)
            node["format"] = "binary"
        for value in node.values():
            _convert_binary_schemas(value)
    elif isinstance(node, list):
        for item in node:
            _convert_binary_schemas(item)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schemas = openapi_schema.get("components", {}).get("schemas", {})

    for schema in schemas.values():
        if "properties" in schema:
            for prop in schema["properties"].values():
                if "anyOf" in prop:
                    non_null = [
                        item
                        for item in prop["anyOf"]
                        if item.get("type") != "null"
                    ]

                    if len(non_null) == 1:
                        clean = non_null[0]
                        desc = prop.get("description") or clean.get("description")
                        title = prop.get("title") or clean.get("title")
                        default = prop.get("default")

                        prop.clear()
                        prop.update(clean)

                        if desc:
                            prop["description"] = desc
                        if title:
                            prop["title"] = title
                        if default is not None:
                            prop["default"] = default

    _convert_binary_schemas(openapi_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


app.mount("/img", StaticFiles(directory=str(IMG_DIR)), name="img")


# Register API Routers
app.include_router(product_router)
app.include_router(auth_router)
app.include_router(category_router)
app.include_router(cart_router)
app.include_router(address_router)
app.include_router(order_router)
app.include_router(admin_router)


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    swagger_html = get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Interactive API Docs",
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
        swagger_favicon_url="https://fastapi.tiangolo.com/img/favicon.png",
    )

    custom_enhancements = """
    <style>
      .send-empty-value {
        display: none !important;
      }
      .autofill-badge {
        display: block;
        margin-top: 8px;
        padding: 6px 12px;
        border-radius: 6px;
        font-size: 13px;
        font-family: inherit;
        background: #f1f5f9;
        border: 1px solid #cbd5e1;
        transition: all 0.25s ease;
      }
    </style>
    <script>
      window.addEventListener('DOMContentLoaded', () => {
        function setupPutAutoLoad() {
          const putBlock = document.querySelector('[id*="update_product"]');
          if (!putBlock) return;

          const idInput = putBlock.querySelector(
            'tr[data-param-name="product_id"] input, input[placeholder="product_id"]'
          );
          if (!idInput || idInput.dataset.listenerAttached) return;
          idInput.dataset.listenerAttached = 'true';

          let badge = putBlock.querySelector('.autofill-badge');
          if (!badge) {
            badge = document.createElement('div');
            badge.className = 'autofill-badge';
            badge.style.display = 'none';
            idInput.parentElement.appendChild(badge);
          }

          function setFieldValue(fieldName, value) {
            if (value === undefined || value === null) return;

            const target = putBlock.querySelector(
              `tr[data-param-name="${fieldName}"] input, tr[data-param-name="${fieldName}"] textarea, input[name="${fieldName}"], textarea[name="${fieldName}"], input[placeholder="${fieldName}"]`
            );
            if (!target) return;

            const isArea = target.tagName.toLowerCase() === 'textarea';
            const proto = isArea
              ? window.HTMLTextAreaElement.prototype
              : window.HTMLInputElement.prototype;
            const setter = Object.getOwnPropertyDescriptor(proto, 'value')?.set;

            if (setter) {
              setter.call(target, value);
            } else {
              target.value = value;
            }

            target.dispatchEvent(new Event('input', { bubbles: true }));
            target.dispatchEvent(new Event('change', { bubbles: true }));
          }

          async function loadDetails(id) {
            if (!id || isNaN(id) || parseInt(id) <= 0) {
              badge.style.display = 'none';
              return;
            }

            badge.style.display = 'block';
            badge.style.borderColor = '#93c5fd';
            badge.style.background = '#eff6ff';
            badge.style.color = '#1d4ed8';
            badge.innerHTML = 'Ã¢ÂÂ³ Loading Product #' + id + ' details...';

            try {
              const res = await fetch('/products/' + id);

              if (!res.ok) {
                badge.style.borderColor = '#fca5a5';
                badge.style.background = '#fef2f2';
                badge.style.color = '#b91c1c';
                badge.innerHTML = 'Ã¢Å¡Â Ã¯Â¸Â Product #' + id + ' not found in database.';
                return;
              }

              const data = await res.json();

              badge.style.borderColor = '#86efac';
              badge.style.background = '#f0fdf4';
              badge.style.color = '#15803d';
              badge.innerHTML = 'Ã¢Å“â€¦ <b>' + (data.name || 'Product') +
                '</b> details loaded! You can now update any fields below and click Execute.';

              setFieldValue('name', data.name || '');
              setFieldValue('price', data.price !== undefined ? data.price : '');
              setFieldValue('stock', data.stock !== undefined ? data.stock : '');
              setFieldValue('description', data.description || '');
            } catch (err) {
              badge.style.borderColor = '#fca5a5';
              badge.style.background = '#fef2f2';
              badge.style.color = '#b91c1c';
              badge.innerHTML = 'Ã¢ÂÅ’ Error loading product: ' + err.message;
            }
          }

          let timer;

          idInput.addEventListener('input', () => {
            clearTimeout(timer);
            timer = setTimeout(
              () => loadDetails(idInput.value.trim()),
              500
            );
          });

          idInput.addEventListener('change', () => loadDetails(idInput.value.trim()));
          idInput.addEventListener('blur', () => loadDetails(idInput.value.trim()));
        }

        const observer = new MutationObserver(() => setupPutAutoLoad());
        observer.observe(document.body, {
          childList: true,
          subtree: true
        });
      });
    </script>
    """

    content = swagger_html.body.decode("utf-8")
    content = content.replace("</body>", f"{custom_enhancements}\n</body>")

    return HTMLResponse(content)


@app.get(
    "/",
    tags=["General"],
    summary="Root endpoint",
    description="Check if the API server is running.",
)
def home():
    return {"message": "E-commerce Backend API is running"}


@app.get(
    "/health",
    tags=["General"],
    summary="Health check endpoint",
    description="Verify API operational status.",
)
def health_check():
    return {"status": "healthy"}
