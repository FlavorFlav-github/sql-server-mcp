-- === Create schemas for DemoDB1 ===
USE DemoDB1;
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'sales')
    EXEC('CREATE SCHEMA sales');
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'hr')
    EXEC('CREATE SCHEMA hr');
GO

-- === Create schemas for DemoDB2 ===
USE DemoDB2;
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'sales')
    EXEC('CREATE SCHEMA sales');
GO
IF NOT EXISTS (SELECT * FROM sys.schemas WHERE name = 'hr')
    EXEC('CREATE SCHEMA hr');
GO