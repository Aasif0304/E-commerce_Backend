
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from database import Base, engine
from models.product_model import Product
from models.product_image_model import ProductImage
from models.category_model import Category
from models.user_model import User
from models.cart_model import CartItem
from models.address_model import Address
from models.order_model import Order
from models.order_item_model import OrderItem

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Use the database URL from the existing project configuration.
config.set_main_option(
    "sqlalchemy.url",
    engine.url.render_as_string(hide_password=False).replace("%", "%%"),
)

# Register the existing models for migration autogeneration.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
