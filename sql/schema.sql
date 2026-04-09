-- ============================================================
-- MySQL Load Simulator - Schema
-- Production-scale tables replicating e-commerce workload
-- ============================================================

CREATE DATABASE IF NOT EXISTS load_simulator;
USE load_simulator;

CREATE TABLE IF NOT EXISTS users (
    user_id     INT          NOT NULL AUTO_INCREMENT,
    username    VARCHAR(100) NOT NULL,
    email       VARCHAR(255) NOT NULL,
    country     VARCHAR(80)  NOT NULL,
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    is_active   TINYINT(1)   NOT NULL DEFAULT 1,
    PRIMARY KEY (user_id),
    UNIQUE KEY uq_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS products (
    product_id   INT           NOT NULL AUTO_INCREMENT,
    name         VARCHAR(255)  NOT NULL,
    category     VARCHAR(100)  NOT NULL,
    price        DECIMAL(10,2) NOT NULL,
    stock_count  INT           NOT NULL DEFAULT 0,
    created_at   DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS orders (
    order_id    BIGINT        NOT NULL AUTO_INCREMENT,
    user_id     INT           NOT NULL,
    product_id  INT           NOT NULL,
    quantity    INT           NOT NULL DEFAULT 1,
    total_price DECIMAL(10,2) NOT NULL,
    status      ENUM('pending','processing','shipped','delivered','cancelled') NOT NULL DEFAULT 'pending',
    created_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME      NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_users    FOREIGN KEY (user_id)    REFERENCES users(user_id),
    CONSTRAINT fk_orders_products FOREIGN KEY (product_id) REFERENCES products(product_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS events (
    event_id    BIGINT       NOT NULL AUTO_INCREMENT,
    user_id     INT          NOT NULL,
    event_type  VARCHAR(50)  NOT NULL,
    page        VARCHAR(255),
    created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (event_id),
    CONSTRAINT fk_events_users FOREIGN KEY (user_id) REFERENCES users(user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS benchmark_log (
    log_id      INT          NOT NULL AUTO_INCREMENT,
    phase       VARCHAR(20)  NOT NULL,
    query_name  VARCHAR(100) NOT NULL,
    avg_ms      DECIMAL(10,3),
    min_ms      DECIMAL(10,3),
    max_ms      DECIMAL(10,3),
    run_at      DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (log_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
