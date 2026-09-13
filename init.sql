-- Enable UUID generation if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Table: users
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('Administrador', 'Gestor', 'Colaborador')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('Activo', 'Inactivo')) DEFAULT 'Activo',
    availability INT NOT NULL DEFAULT 100 CHECK (availability >= 0 AND availability <= 100),
    registered_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email_unique ON users (email) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_users_role ON users (role);
CREATE INDEX IF NOT EXISTS idx_users_status ON users (status);
CREATE INDEX IF NOT EXISTS idx_users_deleted_at ON users (deleted_at);

-- Table: categories
CREATE TABLE IF NOT EXISTS categories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_categories_name_unique ON categories (name) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_categories_deleted_at ON categories (deleted_at);

-- Table: projects
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Planificado', 'En Curso', 'Finalizado', 'Cancelado')) DEFAULT 'Planificado',
    progress INT NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Alta', 'Media', 'Baja')) DEFAULT 'Media',
    start_date DATE NOT NULL,
    end_date DATE,
    manager_id UUID NOT NULL,
    category_id UUID,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (manager_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_projects_name_unique ON projects (name) WHERE deleted_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects (status);
CREATE INDEX IF NOT EXISTS idx_projects_priority ON projects (priority);
CREATE INDEX IF NOT EXISTS idx_projects_start_date ON projects (start_date);
CREATE INDEX IF NOT EXISTS idx_projects_end_date ON projects (end_date);
CREATE INDEX IF NOT EXISTS idx_projects_manager_id ON projects (manager_id);
CREATE INDEX IF NOT EXISTS idx_projects_category_id ON projects (category_id);
CREATE INDEX IF NOT EXISTS idx_projects_deleted_at ON projects (deleted_at);

-- Table: project_users (Many-to-many: projects <-> users)
CREATE TABLE IF NOT EXISTS project_users (
    project_id UUID NOT NULL,
    user_id UUID NOT NULL,
    assigned_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_project_users_project_id ON project_users (project_id);
CREATE INDEX IF NOT EXISTS idx_project_users_user_id ON project_users (user_id);

-- Table: tasks
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    project_id UUID NOT NULL,
    assignee_id UUID NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pendiente', 'En Progreso', 'Completada', 'Vencida')) DEFAULT 'Pendiente',
    priority VARCHAR(20) NOT NULL CHECK (priority IN ('Alta', 'Media', 'Baja')) DEFAULT 'Media',
    due_date DATE NOT NULL,
    progress INT NOT NULL DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (assignee_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_tasks_project_id ON tasks (project_id);
CREATE INDEX IF NOT EXISTS idx_tasks_assignee_id ON tasks (assignee_id);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);
CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks (due_date);
CREATE INDEX IF NOT EXISTS idx_tasks_deleted_at ON tasks (deleted_at);

-- Table: milestones
CREATE TABLE IF NOT EXISTS milestones (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    project_id UUID NOT NULL,
    due_date DATE NOT NULL,
    status VARCHAR(50) NOT NULL CHECK (status IN ('Pendiente', 'Cumplido', 'Vencido')) DEFAULT 'Pendiente',
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_milestones_project_id ON milestones (project_id);
CREATE INDEX IF NOT EXISTS idx_milestones_due_date ON milestones (due_date);
CREATE INDEX IF NOT EXISTS idx_milestones_status ON milestones (status);
CREATE INDEX IF NOT EXISTS idx_milestones_deleted_at ON milestones (deleted_at);

-- Table: comments
CREATE TABLE IF NOT EXISTS comments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL,
    user_id UUID NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    edited_at TIMESTAMP WITH TIME ZONE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comments_task_id ON comments (task_id);
CREATE INDEX IF NOT EXISTS idx_comments_user_id ON comments (user_id);
CREATE INDEX IF NOT EXISTS idx_comments_created_at ON comments (created_at);
CREATE INDEX IF NOT EXISTS idx_comments_deleted_at ON comments (deleted_at);

-- Table: audit_logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    action VARCHAR(100) NOT NULL,
    entity_type VARCHAR(100) NOT NULL,
    entity_id UUID,
    old_value JSONB,
    new_value JSONB,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON audit_logs (action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_type ON audit_logs (entity_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_entity_id ON audit_logs (entity_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp);

-- Table: login_attempts
CREATE TABLE IF NOT EXISTS login_attempts (
    id BIGSERIAL PRIMARY KEY,
    user_id UUID,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN NOT NULL,
    ip_address VARCHAR(45),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_login_attempts_user_id ON login_attempts (user_id);
CREATE INDEX IF NOT EXISTS idx_login_attempts_timestamp ON login_attempts (timestamp);
CREATE INDEX IF NOT EXISTS idx_login_attempts_success ON login_attempts (success);

-- Table: password_reset_tokens
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    token VARCHAR(255) UNIQUE NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_user_id ON password_reset_tokens (user_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_password_reset_tokens_token_unique ON password_reset_tokens (token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens (expires_at);

-- Datos iniciales
INSERT INTO users (name, last_name, email, password_hash, role, status) VALUES
('Admin', 'Principal', 'admin@projecthub.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj4J/HS.iK2i', 'Administrador', 'Activo');

INSERT INTO categories (name) VALUES ('Desarrollo'), ('Marketing'), ('Diseño'), ('Infraestructura');