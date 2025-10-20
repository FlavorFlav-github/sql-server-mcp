-- === Seed DemoDB1 ===
USE DemoDB1;
GO

-- Create tables only if they don't exist
IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'sales.orders') AND type = 'U')
BEGIN
    CREATE TABLE sales.orders (
        id INT PRIMARY KEY,
        amount DECIMAL(10,2),
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'hr.employees') AND type = 'U')
BEGIN
    CREATE TABLE hr.employees (
        id INT PRIMARY KEY,
        name NVARCHAR(100),
        dept NVARCHAR(50)
    );
END
GO

-- Insert data if not already present
INSERT INTO sales.orders (id, amount, created_at)
SELECT 1, 120.50, GETDATE()
WHERE NOT EXISTS (SELECT 1 FROM sales.orders WHERE id = 1);

INSERT INTO sales.orders (id, amount, created_at)
SELECT 2, 80.75, GETDATE()
WHERE NOT EXISTS (SELECT 1 FROM sales.orders WHERE id = 2);

INSERT INTO hr.employees (id, name, dept)
SELECT 1, 'Alice', 'Finance'
WHERE NOT EXISTS (SELECT 1 FROM hr.employees WHERE id = 1);

INSERT INTO hr.employees (id, name, dept)
SELECT 2, 'Bob', 'IT'
WHERE NOT EXISTS (SELECT 1 FROM hr.employees WHERE id = 2);
GO


-- === Seed DemoDB2 ===
USE DemoDB2;
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'sales.orders') AND type = 'U')
BEGIN
    CREATE TABLE sales.orders (
        id INT PRIMARY KEY,
        amount DECIMAL(10,2),
        created_at DATETIME DEFAULT GETDATE()
    );
END
GO

IF NOT EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'hr.employees') AND type = 'U')
BEGIN
    CREATE TABLE hr.employees (
        id INT PRIMARY KEY,
        name NVARCHAR(100),
        dept NVARCHAR(50)
    );
END
GO

INSERT INTO sales.orders (id, amount, created_at)
SELECT 1, 310.00, GETDATE()
WHERE NOT EXISTS (SELECT 1 FROM sales.orders WHERE id = 1);

INSERT INTO sales.orders (id, amount, created_at)
SELECT 2, 95.25, GETDATE()
WHERE NOT EXISTS (SELECT 1 FROM sales.orders WHERE id = 2);

INSERT INTO hr.employees (id, name, dept)
SELECT 1, 'Charlie', 'HR'
WHERE NOT EXISTS (SELECT 1 FROM hr.employees WHERE id = 1);

INSERT INTO hr.employees (id, name, dept)
SELECT 2, 'Diana', 'Sales'
WHERE NOT EXISTS (SELECT 1 FROM hr.employees WHERE id = 2);
GO