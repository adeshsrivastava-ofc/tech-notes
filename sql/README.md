# 📦 SQL

> 📅 Last updated: 2026-03-10 13:51 UTC
> 🔗 [View in Notion](https://app.notion.com/p/SQL-2ff6249cbbe2809aa899f705a9dac05a)

---

```sql
-- =====================================================================
-- DDL (Data Definition Language) – DATABASE LEVEL
-- =====================================================================
-- Scope:
--   • Operates on the DATABASE as a whole (existence, defaults, metadata)
--   • Does NOT operate on tables or rows directly
--   • Most DATABASE-level DDL commands are AUTO-COMMIT
--   • AUTO-COMMIT means: changes CANNOT be rolled back
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) DROP DATABASE
-- ---------------------------------------------------------------------
-- Permanently deletes the database and ALL objects inside it:
--   • tables
--   • views
--   • indexes
--   • procedures / functions
--   • data
-- IF EXISTS prevents error if the database does not exist.
-- AUTO-COMMIT → cannot be rolled back.
DROP DATABASE IF EXISTS dbtest;


-- ---------------------------------------------------------------------
-- 2) CREATE DATABASE
-- ---------------------------------------------------------------------
-- Creates a new database.
-- IF NOT EXISTS avoids error if database already exists.
-- Best practice: explicitly define CHARACTER SET and COLLATION.
-- AUTO-COMMIT → cannot be rolled back.
CREATE DATABASE IF NOT EXISTS dbtest
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 3) SHOW DATABASES
-- ---------------------------------------------------------------------
-- Lists all databases visible to the current user.
-- (Visibility depends on user privileges.)
SHOW DATABASES;

-- Show databases matching a pattern
SHOW DATABASES LIKE 'db%';


-- ---------------------------------------------------------------------
-- 4) USE DATABASE
-- ---------------------------------------------------------------------
-- Selects / switches the active database for the current session.
-- All subsequent queries will run against this database.
-- NOTE: This is a CONTEXT command, not pure DDL.
USE dbtest;


-- ---------------------------------------------------------------------
-- 5) SHOW CURRENT DATABASE
-- ---------------------------------------------------------------------
-- Returns the name of the currently selected database.
-- Returns NULL if no database is selected.
SELECT DATABASE();


-- ---------------------------------------------------------------------
-- 6) DATABASE METADATA (INFORMATION_SCHEMA)
-- ---------------------------------------------------------------------
-- INFORMATION_SCHEMA.SCHEMATA contains metadata for all databases:
--   • schema_name        → database name
--   • default_character_set_name
--   • default_collation_name
--   • sql_path
SELECT *
FROM information_schema.schemata;

-- Query only database names
SELECT schema_name
FROM information_schema.schemata;


-- ---------------------------------------------------------------------
-- 7) SHOW CREATE DATABASE
-- ---------------------------------------------------------------------
-- Displays the exact SQL statement used to create the database.
-- Useful for inspecting:
--   • character set
--   • collation
--   • database-level options
SHOW CREATE DATABASE dbtest;


-- ---------------------------------------------------------------------
-- 8) ALTER DATABASE
-- ---------------------------------------------------------------------
-- Modifies DATABASE-LEVEL DEFAULTS only.
-- IMPORTANT:
--   • Affects ONLY newly created tables
--   • Existing tables are NOT modified automatically
-- AUTO-COMMIT → cannot be rolled back.
ALTER DATABASE dbtest
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 9) IMPORTANT CLARIFICATION: EXISTING TABLES
-- ---------------------------------------------------------------------
-- ALTER DATABASE does NOT change existing tables.
-- To update existing tables, each table must be altered explicitly.
ALTER TABLE table_name
CONVERT TO CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;


-- ---------------------------------------------------------------------
-- 10) TRANSACTION BEHAVIOR (CRITICAL CONCEPT)
-- ---------------------------------------------------------------------
-- Database-level DDL commands are AUTO-COMMIT.
-- The following CANNOT be rolled back:
--   • CREATE DATABASE
--   • DROP DATABASE
--   • ALTER DATABASE
--
-- Example (ROLLBACK will NOT work):
-- START TRANSACTION;
-- DROP DATABASE dbtest;
-- ROLLBACK;   -- ❌ database is already gone


-- ---------------------------------------------------------------------
-- 11) SECURITY NOTE (DCL – Database Scope)
-- ---------------------------------------------------------------------
-- Database-level permissions are handled via DCL.
-- Example (for reference):
-- GRANT ALL ON dbtest.* TO 'user1';
-- REVOKE ALL ON dbtest.* FROM 'user1';

-- Check current user privileges
SHOW GRANTS FOR CURRENT_USER;


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- DATABASE-LEVEL DDL controls:
--   • existence of database
--   • default character set & collation
--   • metadata & inspection
--   • session context (USE)
--
-- DATABASE-LEVEL DDL does NOT:
--   • manipulate data
--   • affect existing tables automatically
--   • support rollback
-- =====================================================================
```

```sql
-- =====================================================================
-- DDL (Data Definition Language) – TABLE LEVEL (FINAL CONSOLIDATED NOTES)
-- =====================================================================
-- Scope:
--   • Operates on TABLE structure (schema)
--   • Defines columns, data types, constraints, indexes
--   • Does NOT manipulate row data
--   • Most TABLE-level DDL commands are AUTO-COMMIT
--   • AUTO-COMMIT → changes CANNOT be rolled back
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) CREATE TABLE
-- ---------------------------------------------------------------------
-- Creates a new table with columns, data types, and constraints.
-- Best practice:
--   • Explicit data types
--   • Proper constraints
--   • Meaningful table & column names
CREATE TABLE employees (
    id INT PRIMARY KEY,                     -- uniquely identifies each row
    name VARCHAR(100) NOT NULL,              -- cannot be NULL
    email VARCHAR(150) UNIQUE,               -- must be unique
    salary DECIMAL(10,2) CHECK (salary > 0), -- business rule
    department_id INT,                       -- foreign key column
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- ---------------------------------------------------------------------
-- 2) CREATE TABLE with FOREIGN KEY
-- ---------------------------------------------------------------------
-- Establishes relationship between tables.
CREATE TABLE departments (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id INT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    department_id INT,
    CONSTRAINT fk_emp_dept
        FOREIGN KEY (department_id)
        REFERENCES departments(id)
        ON DELETE CASCADE
);


-- ---------------------------------------------------------------------
-- 3) ALTER TABLE – ADD COLUMN
-- ---------------------------------------------------------------------
-- Adds a new column to an existing table.
-- AUTO-COMMIT → cannot be rolled back.
ALTER TABLE employees
ADD column phone VARCHAR(15);


-- ---------------------------------------------------------------------
-- 4) ALTER TABLE – MODIFY / ALTER COLUMN
-- ---------------------------------------------------------------------
-- Changes data type, size, or constraints of a column.
-- Syntax varies slightly across databases.
ALTER TABLE employees
MODIFY salary DECIMAL(12,2);

-- PostgreSQL-style
-- ALTER TABLE employees
-- ALTER COLUMN salary TYPE DECIMAL(12,2);


-- ---------------------------------------------------------------------
-- 5) ALTER TABLE – DROP COLUMN
-- ---------------------------------------------------------------------
-- Removes a column permanently along with its data.
ALTER TABLE employees
DROP COLUMN phone;


-- ---------------------------------------------------------------------
-- 6) ALTER TABLE – RENAME COLUMN
-- ---------------------------------------------------------------------
-- Renames an existing column.
ALTER TABLE employees
RENAME COLUMN name TO full_name;


-- ---------------------------------------------------------------------
-- 7) ALTER TABLE – ADD CONSTRAINT
-- ---------------------------------------------------------------------
-- Adds constraint to an existing table.
ALTER TABLE employees
ADD CONSTRAINT chk_salary
CHECK (salary >= 10000);


-- ---------------------------------------------------------------------
-- 8) ALTER TABLE – DROP CONSTRAINT
-- ---------------------------------------------------------------------
-- Removes an existing constraint.
ALTER TABLE employees
DROP CONSTRAINT chk_salary;


-- ---------------------------------------------------------------------
-- 9) TRUNCATE TABLE
-- ---------------------------------------------------------------------
-- Deletes ALL rows from the table.
-- Table structure remains intact.
-- Faster than DELETE.
-- AUTO-COMMIT → cannot be rolled back.
-- Resets identity / auto-increment counter.
TRUNCATE TABLE employees;


-- ---------------------------------------------------------------------
-- 10) DROP TABLE
-- ---------------------------------------------------------------------
-- Completely removes the table definition AND data.
-- AUTO-COMMIT → cannot be rolled back.
DROP TABLE employees;


-- ---------------------------------------------------------------------
-- 11) RENAME TABLE
-- ---------------------------------------------------------------------
-- Changes the table name.
RENAME TABLE employees TO staff;

-- MySQL alternative:
-- ALTER TABLE employees RENAME TO staff;


-- ---------------------------------------------------------------------
-- 12) CREATE INDEX
-- ---------------------------------------------------------------------
-- Improves query performance for read-heavy columns.
-- Indexes speed up SELECT but slow down INSERT/UPDATE.
CREATE INDEX idx_emp_dept
ON employees(department_id);


-- ---------------------------------------------------------------------
-- 13) DROP INDEX
-- ---------------------------------------------------------------------
-- Removes an index.
DROP INDEX idx_emp_dept ON employees;


-- ---------------------------------------------------------------------
-- 14) TABLE METADATA
-- ---------------------------------------------------------------------
-- Show table structure.
DESCRIBE employees;

-- Show table creation SQL.
SHOW CREATE TABLE employees;


-- ---------------------------------------------------------------------
-- 15) TRANSACTION BEHAVIOR (CRITICAL)
-- ---------------------------------------------------------------------
-- TABLE-level DDL commands are AUTO-COMMIT.
-- The following CANNOT be rolled back:
--   • CREATE TABLE
--   • DROP TABLE
--   • ALTER TABLE
--   • TRUNCATE TABLE
--
-- Example (ROLLBACK will NOT work):
-- START TRANSACTION;
-- DROP TABLE employees;
-- ROLLBACK;   -- ❌ table is already gone


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- TABLE-LEVEL DDL controls:
--   • table existence
--   • column definitions
--   • constraints
--   • indexes
--
-- TABLE-LEVEL DDL does NOT:
--   • insert data
--   • update data
--   • support rollback
-- =====================================================================
```

```sql
-- =====================================================================
-- DML (Data Manipulation Language) – FINAL CONSOLIDATED NOTES
-- =====================================================================
-- Scope:
--   • Operates on TABLE DATA (rows)
--   • Used to INSERT, UPDATE, DELETE records
--   • Works inside transactions
--   • CAN be rolled back (unless auto-commit is ON)
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) INSERT – ADD NEW ROWS
-- ---------------------------------------------------------------------
-- Inserts data into a table.
-- Best practice:
--   • Always specify column names
--   • Avoid relying on column order
INSERT INTO employees (
    id,
    full_name,
    email,
    salary,
    department_id
)
VALUES (
    1,
    'Adesh Kumar',
    'adesh@example.com',
    60000,
    10
);


-- ---------------------------------------------------------------------
-- 2) INSERT MULTIPLE ROWS
-- ---------------------------------------------------------------------
INSERT INTO employees (id, full_name, salary)
VALUES
    (2, 'Rahul', 50000),
    (3, 'Neha', 55000),
    (4, 'Amit', 52000);


-- ---------------------------------------------------------------------
-- 3) INSERT USING SELECT (DATA COPY / MIGRATION)
-- ---------------------------------------------------------------------
-- Inserts rows returned by a SELECT query.
INSERT INTO employees_backup (id, full_name, salary)
SELECT id, full_name, salary
FROM employees
WHERE salary > 50000;


-- ---------------------------------------------------------------------
-- 4) INSERT WITH DEFAULT VALUES
-- ---------------------------------------------------------------------
-- Uses DEFAULT values defined in table schema.
INSERT INTO employees (id, full_name)
VALUES (5, 'Default User');


-- ---------------------------------------------------------------------
-- 5) UPDATE – MODIFY EXISTING ROWS
-- ---------------------------------------------------------------------
-- Updates one or more rows.
-- IMPORTANT:
--   • Always use WHERE unless you want to update ALL rows
UPDATE employees
SET salary = 65000
WHERE id = 1;


-- ---------------------------------------------------------------------
-- 6) UPDATE MULTIPLE COLUMNS
-- ---------------------------------------------------------------------
UPDATE employees
SET
    salary = salary + 5000,
    department_id = 20
WHERE id = 2;


-- ---------------------------------------------------------------------
-- 7) UPDATE USING JOIN (VERY COMMON IN PRODUCTION)
-- ---------------------------------------------------------------------
-- MySQL-style update with JOIN
UPDATE employees e
JOIN departments d
    ON e.department_id = d.id
SET e.salary = e.salary + 10000
WHERE d.name = 'Engineering';


-- ---------------------------------------------------------------------
-- 8) DELETE – REMOVE ROWS
-- ---------------------------------------------------------------------
-- Deletes rows from a table.
-- IMPORTANT:
--   • Always use WHERE unless you want to delete ALL rows
DELETE FROM employees
WHERE id = 4;


-- ---------------------------------------------------------------------
-- 9) DELETE ALL ROWS (DANGEROUS)
-- ---------------------------------------------------------------------
-- Deletes all rows but keeps table structure.
-- Slower than TRUNCATE.
-- CAN be rolled back (if transaction not committed).
DELETE FROM employees;


-- ---------------------------------------------------------------------
-- 10) DELETE USING JOIN
-- ---------------------------------------------------------------------
-- Deletes rows based on related table conditions.
DELETE e
FROM employees e
JOIN departments d
    ON e.department_id = d.id
WHERE d.name = 'HR';


-- ---------------------------------------------------------------------
-- 11) TRANSACTION CONTROL WITH DML
-- ---------------------------------------------------------------------
-- DML works inside transactions.
-- Changes can be committed or rolled back.
START TRANSACTION;

UPDATE employees
SET salary = salary - 5000
WHERE id = 1;

ROLLBACK;   -- changes undone
-- COMMIT;  -- changes saved permanently


-- ---------------------------------------------------------------------
-- 12) SAVEPOINT (PARTIAL ROLLBACK)
-- ---------------------------------------------------------------------
START TRANSACTION;

UPDATE employees SET salary = 70000 WHERE id = 1;
SAVEPOINT sp1;

UPDATE employees SET salary = 30000 WHERE id = 2;

ROLLBACK TO sp1;  -- only second update is undone
COMMIT;


-- ---------------------------------------------------------------------
-- 13) AUTO-COMMIT BEHAVIOR
-- ---------------------------------------------------------------------
-- If AUTO-COMMIT is ON:
--   • Each DML statement is committed immediately
-- If AUTO-COMMIT is OFF:
--   • Explicit COMMIT / ROLLBACK required
SET AUTOCOMMIT = 0;


-- ---------------------------------------------------------------------
-- 14) COMMON DML PITFALLS (INTERVIEW & PRODUCTION)
-- ---------------------------------------------------------------------
-- ❌ UPDATE without WHERE → updates all rows
-- ❌ DELETE without WHERE → deletes all rows
-- ❌ Forgetting COMMIT → changes lost after session ends
-- ❌ Assuming DML is auto-commit like DDL (it is NOT)


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- DML controls:
--   • inserting data
--   • modifying data
--   • deleting data
--
-- DML:
--   • works with transactions
--   • supports rollback
--   • affects rows, not structure
-- =====================================================================
```

```sql
-- =====================================================================
-- DQL (Data Query Language) – SELECT
-- EXECUTION ORDER & CLAUSES (FINAL CONSOLIDATED NOTES)
-- =====================================================================
-- Scope:
--   • Used ONLY to READ / FETCH data
--   • Does NOT modify data or structure
--   • SELECT is the ONLY DQL command
--   • Most complex and most asked SQL topic in interviews
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) LOGICAL EXECUTION ORDER OF SELECT (VERY IMPORTANT)
-- ---------------------------------------------------------------------
-- This is how SQL ACTUALLY runs internally (NOT how we write it):
--
-- 1. FROM        → identify base tables
-- 2. JOIN       → join tables
-- 3. ON         → apply join conditions
-- 4. WHERE      → filter rows
-- 5. GROUP BY   → group rows
-- 6. HAVING     → filter groups
-- 7. SELECT     → choose columns / expressions
-- 8. DISTINCT   → remove duplicates
-- 9. ORDER BY   → sort result
-- 10. LIMIT / OFFSET → restrict rows
--
-- ⚠️ This order explains MANY SQL bugs and interview traps


-- ---------------------------------------------------------------------
-- 2) WRITTEN ORDER OF SELECT (SYNTAX ORDER)
-- ---------------------------------------------------------------------
-- This is how we WRITE the query:
SELECT
FROM
JOIN
ON
WHERE
GROUP BY
HAVING
ORDER BY
LIMIT OFFSET;


-- ---------------------------------------------------------------------
-- 3) COMPLETE SELECT SYNTAX (GENERIC)
-- ---------------------------------------------------------------------
SELECT
    [DISTINCT]
    column_expr [AS alias],
    aggregate_func(column) AS agg_alias,
    subquery AS sub_alias
FROM table_name AS t
    [INNER | LEFT | RIGHT | FULL] JOIN table2 AS t2
        ON join_condition
    [JOIN table3 ...]
WHERE row_condition
GROUP BY group_expr
HAVING group_condition
ORDER BY sort_expr [ASC | DESC]
LIMIT n OFFSET m;


-- ---------------------------------------------------------------------
-- 4) SELECT CLAUSE
-- ---------------------------------------------------------------------
-- Chooses columns, expressions, aliases.
SELECT
    id,
    full_name,
    salary * 12 AS annual_salary
FROM employees;


-- ---------------------------------------------------------------------
-- 5) FROM CLAUSE
-- ---------------------------------------------------------------------
-- Specifies the base table(s).
FROM employees;


-- ---------------------------------------------------------------------
-- 6) JOIN CLAUSES
-- ---------------------------------------------------------------------
-- Combines rows from multiple tables.
--
-- INNER JOIN → matching rows only
-- LEFT JOIN  → all left + matching right
-- RIGHT JOIN → all right + matching left
-- FULL JOIN  → all rows from both sides
-- CROSS JOIN → cartesian product

SELECT e.full_name, d.name
FROM employees e
INNER JOIN departments d
    ON e.department_id = d.id;


-- ---------------------------------------------------------------------
-- 7) ON vs WHERE (CRITICAL DIFFERENCE)
-- ---------------------------------------------------------------------
-- ON → applied during JOIN
-- WHERE → applied AFTER join
--
-- ❌ Can turn LEFT JOIN into INNER JOIN accidentally
FROM employees e
LEFT JOIN departments d
    ON e.department_id = d.id
WHERE d.name = 'HR';   -- ❌ filters out NULLs


-- ---------------------------------------------------------------------
-- 8) WHERE CLAUSE
-- ---------------------------------------------------------------------
-- Filters ROWS before grouping.
-- Cannot use aggregate functions here.
WHERE salary > 50000
  AND department_id IN (10, 20)
  AND email IS NOT NULL
  AND full_name LIKE 'A%';


-- ---------------------------------------------------------------------
-- 9) GROUP BY CLAUSE
-- ---------------------------------------------------------------------
-- Groups rows for aggregation.
-- All non-aggregated SELECT columns MUST appear in GROUP BY.
SELECT department_id, COUNT(*) AS emp_count
FROM employees
GROUP BY department_id;


-- ---------------------------------------------------------------------
-- 10) AGGREGATE FUNCTIONS
-- ---------------------------------------------------------------------
-- Used with GROUP BY.
-- Common aggregates:
--   • COUNT()
--   • SUM()
--   • AVG()
--   • MIN()
--   • MAX()

SELECT
    department_id,
    COUNT(id) AS total_employees,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id;


-- ---------------------------------------------------------------------
-- 11) HAVING CLAUSE
-- ---------------------------------------------------------------------
-- Filters GROUPS after GROUP BY.
-- Aggregates are allowed here.
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
GROUP BY department_id
HAVING AVG(salary) > 70000;


-- ---------------------------------------------------------------------
-- 12) DISTINCT
-- ---------------------------------------------------------------------
-- Removes duplicate rows AFTER SELECT.
SELECT DISTINCT department_id
FROM employees;


-- ---------------------------------------------------------------------
-- 13) ORDER BY
-- ---------------------------------------------------------------------
-- Sorts final result set.
-- Can use column names, aliases, or position numbers.
SELECT full_name, salary
FROM employees
ORDER BY salary DESC, full_name ASC;


-- ---------------------------------------------------------------------
-- 14) LIMIT / OFFSET
-- ---------------------------------------------------------------------
-- Restricts number of rows returned.
-- Commonly used for pagination.
SELECT *
FROM employees
ORDER BY id
LIMIT 10 OFFSET 20;


-- ---------------------------------------------------------------------
-- 15) SUBQUERIES
-- ---------------------------------------------------------------------
-- Query inside another query.
SELECT full_name
FROM employees
WHERE salary > (
    SELECT AVG(salary)
    FROM employees
);


-- ---------------------------------------------------------------------
-- 16) COMMON INTERVIEW TRAPS
-- ---------------------------------------------------------------------
-- ❌ Using alias in WHERE (not allowed)
-- ❌ Using aggregate in WHERE (use HAVING)
-- ❌ Expecting SELECT execution order
-- ❌ Misplacing conditions between ON and WHERE


-- ---------------------------------------------------------------------
-- 17) COMPLETE REAL-WORLD EXAMPLE
-- ---------------------------------------------------------------------
SELECT
    e.department_id,
    COUNT(e.id) AS emp_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d
    ON e.department_id = d.id
WHERE e.salary > 50000
GROUP BY e.department_id
HAVING AVG(e.salary) > 70000
ORDER BY avg_salary DESC
LIMIT 5;


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- DQL:
--   • reads data only
--   • never changes data
--   • SELECT is powerful because of clause execution order
--
-- Remember:
--   WRITE order ≠ EXECUTION order
-- =====================================================================
```

```sql
-- =====================================================================
-- DELETE vs TRUNCATE vs DROP
-- (DEEP PRODUCTION + INTERVIEW VIEW)
-- =====================================================================
-- Scope:
--   • All three remove data, but at VERY different levels
--   • Choosing the wrong one can cause DATA LOSS or OUTAGE
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) DELETE
-- ---------------------------------------------------------------------
-- Category: DML (Data Manipulation Language)
-- Removes rows from a table.
-- Can remove:
--   • specific rows (with WHERE)
--   • all rows (without WHERE)
-- Supports TRANSACTIONS → CAN be rolled back.
-- Row-by-row operation (slower for large data).
-- Triggers are fired.
-- Does NOT reset auto-increment counter.

DELETE FROM employees
WHERE id = 10;


-- Delete ALL rows (dangerous but reversible)
DELETE FROM employees;


-- ---------------------------------------------------------------------
-- DELETE – KEY CHARACTERISTICS
-- ---------------------------------------------------------------------
-- ✔ Can use WHERE
-- ✔ Can be rolled back
-- ✔ Triggers are fired
-- ✔ Respects foreign keys
-- ❌ Slower (row-by-row logging)
-- ❌ Auto-increment NOT reset


-- ---------------------------------------------------------------------
-- 2) TRUNCATE
-- ---------------------------------------------------------------------
-- Category: DDL
-- Removes ALL rows from a table.
-- Table structure remains intact.
-- Cannot use WHERE.
-- AUTO-COMMIT → CANNOT be rolled back.
-- Very fast (deallocates data pages).
-- Resets auto-increment counter.
-- Triggers are NOT fired.
-- Cannot truncate if table is referenced by FK.

TRUNCATE TABLE employees;


-- ---------------------------------------------------------------------
-- TRUNCATE – KEY CHARACTERISTICS
-- ---------------------------------------------------------------------
-- ❌ Cannot use WHERE
-- ❌ Cannot be rolled back
-- ❌ Triggers NOT fired
-- ❌ Blocked by foreign key references
-- ✔ Very fast
-- ✔ Resets auto-increment
-- ✔ Minimal logging


-- ---------------------------------------------------------------------
-- 3) DROP
-- ---------------------------------------------------------------------
-- Category: DDL
-- Completely removes:
--   • table definition
--   • data
--   • indexes
--   • constraints
-- AUTO-COMMIT → CANNOT be rolled back.
-- Table no longer exists after this.

DROP TABLE employees;


-- ---------------------------------------------------------------------
-- DROP – KEY CHARACTERISTICS
-- ---------------------------------------------------------------------
-- ❌ Removes structure + data
-- ❌ Cannot be rolled back
-- ❌ Triggers lost
-- ❌ Indexes lost
-- ✔ Frees storage completely


-- ---------------------------------------------------------------------
-- 4) SIDE-BY-SIDE COMPARISON (INTERVIEW GOLD)
-- ---------------------------------------------------------------------
-- | Feature                | DELETE        | TRUNCATE        | DROP          |
-- |------------------------|---------------|-----------------|---------------|
-- | SQL Category           | DML           | DDL             | DDL           |
-- | WHERE allowed          | ✔ Yes         | ❌ No           | ❌ No         |
-- | Removes specific rows  | ✔ Yes         | ❌ No           | ❌ No         |
-- | Removes all rows       | ✔ Yes         | ✔ Yes           | ✔ Yes         |
-- | Table structure kept   | ✔ Yes         | ✔ Yes           | ❌ No         |
-- | Rollback possible      | ✔ Yes         | ❌ No           | ❌ No         |
-- | Triggers fired         | ✔ Yes         | ❌ No           | ❌ No         |
-- | Auto-increment reset   | ❌ No         | ✔ Yes           | ✔ Yes        |
-- | Speed                  | Slow          | Very Fast       | Instant       |


-- ---------------------------------------------------------------------
-- 5) TRANSACTION BEHAVIOR (CRITICAL)
-- ---------------------------------------------------------------------
-- DELETE → works inside transactions
START TRANSACTION;
DELETE FROM employees;
ROLLBACK;    -- ✔ data restored


-- TRUNCATE → auto-commit
START TRANSACTION;
TRUNCATE TABLE employees;
ROLLBACK;    -- ❌ no effect


-- DROP → auto-commit
START TRANSACTION;
DROP TABLE employees;
ROLLBACK;    -- ❌ table already gone


-- ---------------------------------------------------------------------
-- 6) FOREIGN KEY BEHAVIOR
-- ---------------------------------------------------------------------
-- DELETE:
--   ✔ Respects FK rules
--   ✔ Can cascade with ON DELETE CASCADE

-- TRUNCATE:
--   ❌ Fails if referenced by foreign key

-- DROP:
--   ✔ Allowed (drops constraints as well)


-- ---------------------------------------------------------------------
-- 7) WHEN TO USE WHAT (REAL PRODUCTION RULES)
-- ---------------------------------------------------------------------
-- Use DELETE when:
--   • you need WHERE conditions
--   • you need rollback safety
--   • triggers must fire
--   • auditing is required

-- Use TRUNCATE when:
--   • you want to empty a table fast
--   • rollback is NOT required
--   • table is not referenced by FK
--   • resetting auto-increment is desired

-- Use DROP when:
--   • table is no longer needed
--   • schema cleanup
--   • permanent removal is intended


-- ---------------------------------------------------------------------
-- 8) COMMON INTERVIEW TRAPS
-- ---------------------------------------------------------------------
-- ❌ TRUNCATE is same as DELETE without WHERE → FALSE
-- ❌ TRUNCATE fires triggers → FALSE
-- ❌ DROP only removes data → FALSE
-- ❌ DELETE is auto-commit → FALSE


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- DELETE   → removes ROWS (safe, slow, reversible)
-- TRUNCATE → clears TABLE DATA (fast, irreversible)
-- DROP     → removes TABLE ITSELF (destructive)
-- =====================================================================
```

```sql
-- =====================================================================
-- DCL (Data Control Language) – FINAL CONSOLIDATED NOTES
-- =====================================================================
-- Scope:
--   • Controls ACCESS and PERMISSIONS in the database
--   • Defines WHO can do WHAT on WHICH object
--   • Used mainly by DBAs / admins
--   • Does NOT manipulate data or structure
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) GRANT
-- ---------------------------------------------------------------------
-- Gives permissions to users or roles.
-- Permissions can be granted at:
--   • DATABASE level
--   • TABLE level
--   • COLUMN level
--   • PROCEDURE / FUNCTION level
--
-- Changes take effect immediately.


-- ---------------------------------------------------------------------
-- 1.1) GRANT – DATABASE LEVEL
-- ---------------------------------------------------------------------
-- Grants permissions on ALL tables in a database.
GRANT ALL ON dbtest.* TO 'user1';

-- Grant specific permissions
GRANT SELECT, INSERT, UPDATE
ON dbtest.*
TO 'user1';


-- ---------------------------------------------------------------------
-- 1.2) GRANT – TABLE LEVEL
-- ---------------------------------------------------------------------
GRANT SELECT, INSERT
ON employees
TO 'user1';


-- ---------------------------------------------------------------------
-- 1.3) GRANT – COLUMN LEVEL
-- ---------------------------------------------------------------------
-- Restricts access to specific columns only.
GRANT SELECT (id, full_name, salary)
ON employees
TO 'user1';


-- ---------------------------------------------------------------------
-- 1.4) GRANT – WITH GRANT OPTION
-- ---------------------------------------------------------------------
-- Allows the user to grant permissions to others.
GRANT SELECT
ON employees
TO 'manager1'
WITH GRANT OPTION;


-- ---------------------------------------------------------------------
-- 2) REVOKE
-- ---------------------------------------------------------------------
-- Removes previously granted permissions.


-- ---------------------------------------------------------------------
-- 2.1) REVOKE – DATABASE LEVEL
-- ---------------------------------------------------------------------
REVOKE ALL
ON dbtest.*
FROM 'user1';


-- ---------------------------------------------------------------------
-- 2.2) REVOKE – TABLE LEVEL
-- ---------------------------------------------------------------------
REVOKE INSERT
ON employees
FROM 'user1';


-- ---------------------------------------------------------------------
-- 2.3) REVOKE – GRANT OPTION
-- ---------------------------------------------------------------------
-- Removes the ability to grant permissions further.
REVOKE GRANT OPTION
ON employees
FROM 'manager1';


-- ---------------------------------------------------------------------
-- 3) COMMON DATABASE PERMISSIONS
-- ---------------------------------------------------------------------
-- SELECT   → read data
-- INSERT   → add data
-- UPDATE   → modify data
-- DELETE   → remove data
-- CREATE   → create objects
-- DROP     → delete objects
-- ALTER    → modify structure
-- EXECUTE  → run procedures/functions
-- ALL      → all privileges


-- ---------------------------------------------------------------------
-- 4) CHECK USER PRIVILEGES
-- ---------------------------------------------------------------------
-- Show permissions for current user
SHOW GRANTS FOR CURRENT_USER;

-- Show permissions for a specific user
SHOW GRANTS FOR 'user1';


-- ---------------------------------------------------------------------
-- 5) ROLE-BASED ACCESS (DB-SPECIFIC, MODERN APPROACH)
-- ---------------------------------------------------------------------
-- Create a role
CREATE ROLE read_only_role;

-- Grant permissions to role
GRANT SELECT
ON dbtest.*
TO read_only_role;

-- Assign role to user
GRANT read_only_role TO 'user1';


-- ---------------------------------------------------------------------
-- 6) IMPORTANT DCL BEHAVIOR
-- ---------------------------------------------------------------------
-- ✔ DCL commands are AUTO-COMMIT
-- ✔ Changes cannot be rolled back
-- ✔ Permissions are checked BEFORE query execution
-- ✔ Lack of privilege → query fails immediately


-- ---------------------------------------------------------------------
-- 7) COMMON INTERVIEW TRAPS
-- ---------------------------------------------------------------------
-- ❌ DCL works inside transactions → FALSE
-- ❌ GRANT modifies data → FALSE
-- ❌ REVOKE deletes objects → FALSE
-- ❌ Permissions are checked after query runs → FALSE


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- DCL controls:
--   • database security
--   • user permissions
--   • access boundaries
--
-- DCL does NOT:
--   • insert/update/delete data
--   • change schema
-- =====================================================================
```

```sql
-- =====================================================================
-- TCL (Transaction Control Language) – FINAL CONSOLIDATED NOTES
-- =====================================================================
-- Scope:
--   • Controls TRANSACTIONS in the database
--   • Ensures data consistency and integrity
--   • Works mainly with DML commands
--   • Implements ACID properties
-- =====================================================================


-- ---------------------------------------------------------------------
-- 1) TRANSACTION (BASIC CONCEPT)
-- ---------------------------------------------------------------------
-- A transaction is a logical unit of work.
-- Either ALL operations succeed or ALL fail.
-- Ensures:
--   • Atomicity
--   • Consistency
--   • Isolation
--   • Durability (ACID)


-- ---------------------------------------------------------------------
-- 2) START TRANSACTION / BEGIN
-- ---------------------------------------------------------------------
-- Explicitly starts a transaction.
-- All subsequent DML statements become part of the transaction.
START TRANSACTION;
-- BEGIN;   -- alternative keyword (DB-specific)


-- ---------------------------------------------------------------------
-- 3) COMMIT
-- ---------------------------------------------------------------------
-- Permanently saves all changes made in the current transaction.
-- After COMMIT:
--   • changes are durable
--   • cannot be rolled back
COMMIT;


-- ---------------------------------------------------------------------
-- 4) ROLLBACK
-- ---------------------------------------------------------------------
-- Undoes all changes made in the current transaction.
-- Rolls back to the state before START TRANSACTION.
ROLLBACK;


-- ---------------------------------------------------------------------
-- 5) SAVEPOINT
-- ---------------------------------------------------------------------
-- Creates a checkpoint inside a transaction.
-- Allows partial rollback instead of full rollback.
START TRANSACTION;

UPDATE employees SET salary = 70000 WHERE id = 1;
SAVEPOINT sp1;

UPDATE employees SET salary = 30000 WHERE id = 2;

ROLLBACK TO sp1;   -- only second UPDATE is undone
COMMIT;


-- ---------------------------------------------------------------------
-- 6) RELEASE SAVEPOINT
-- ---------------------------------------------------------------------
-- Removes a savepoint explicitly.
-- After release, rollback to that savepoint is not possible.
RELEASE SAVEPOINT sp1;


-- ---------------------------------------------------------------------
-- 7) SET AUTOCOMMIT
-- ---------------------------------------------------------------------
-- Controls automatic commit behavior.
-- Default in most databases: AUTOCOMMIT = ON
SET AUTOCOMMIT = 0;   -- OFF
SET AUTOCOMMIT = 1;   -- ON


-- ---------------------------------------------------------------------
-- 8) IMPLICIT TRANSACTIONS
-- ---------------------------------------------------------------------
-- When AUTOCOMMIT is ON:
--   • Each DML statement is automatically committed
--   • COMMIT / ROLLBACK are not required
--
-- When AUTOCOMMIT is OFF:
--   • Explicit COMMIT / ROLLBACK required


-- ---------------------------------------------------------------------
-- 9) TCL vs DDL (CRITICAL DIFFERENCE)
-- ---------------------------------------------------------------------
-- TCL works with DML statements only.
--
-- DDL statements are AUTO-COMMIT:
--   • CREATE
--   • DROP
--   • ALTER
--   • TRUNCATE
--
-- Example (ROLLBACK will NOT work):
-- START TRANSACTION;
-- DROP TABLE employees;
-- ROLLBACK;   -- ❌ table already gone


-- ---------------------------------------------------------------------
-- 10) TRANSACTION ISOLATION LEVELS
-- ---------------------------------------------------------------------
-- Controls how transactions are isolated from each other.

-- READ UNCOMMITTED:
--   • Allows dirty reads
--   • Lowest isolation

-- READ COMMITTED:
--   • Prevents dirty reads
--   • Allows non-repeatable reads

-- REPEATABLE READ:
--   • Prevents dirty + non-repeatable reads
--   • Allows phantom reads (DB-specific)

-- SERIALIZABLE:
--   • Highest isolation
--   • Fully isolated
--   • Lowest concurrency


-- ---------------------------------------------------------------------
-- 11) SET TRANSACTION ISOLATION LEVEL
-- ---------------------------------------------------------------------
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
-- SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
-- SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;


-- ---------------------------------------------------------------------
-- 12) COMMON TRANSACTION PROBLEMS
-- ---------------------------------------------------------------------
-- Dirty Read:
--   • Reading uncommitted data from another transaction
--
-- Non-Repeatable Read:
--   • Same query returns different result in same transaction
--
-- Phantom Read:
--   • New rows appear in repeated query results


-- ---------------------------------------------------------------------
-- 13) WHEN TO USE TCL (REAL PRODUCTION RULES)
-- ---------------------------------------------------------------------
-- Use transactions when:
--   • multiple DML statements must succeed together
--   • financial or critical data is involved
--   • consistency is more important than performance
--
-- Avoid long transactions:
--   • cause locks
--   • reduce concurrency
--   • can lead to deadlocks


-- ---------------------------------------------------------------------
-- 14) COMMON INTERVIEW TRAPS
-- ---------------------------------------------------------------------
-- ❌ TCL works with DDL → FALSE
-- ❌ COMMIT can be rolled back → FALSE
-- ❌ ROLLBACK works after TRUNCATE → FALSE
-- ❌ AUTOCOMMIT = OFF by default → FALSE


-- ---------------------------------------------------------------------
-- SUMMARY (MENTAL MODEL)
-- ---------------------------------------------------------------------
-- TCL controls:
--   • transaction boundaries
--   • commit / rollback
--   • isolation behavior
--
-- TCL ensures:
--   • data consistency
--   • failure safety
--   • correctness in concurrent systems
-- =====================================================================
```

```sql
SELECT      -- what columns / expressions
FROM        -- base table(s)
JOIN        -- joins
ON          -- join conditions
WHERE       -- row-level filtering
GROUP BY    -- grouping
HAVING      -- group-level filtering
ORDER BY   -- sorting
LIMIT       -- pagination (MySQL-specific)
OFFSET
```


```sql
SELECT
[DISTINCT]
column_expr [AS alias],
aggregate_func(column) AS agg_alias,
subquery AS sub_alias
FROM table_name AS t
[INNER | LEFT | RIGHT | FULL] JOIN table2 AS t2
ON join_condition
[JOIN ...]
WHERE row_condition
GROUP BY group_expr
HAVING group_condition
ORDER BY sort_expr [ASC|DESC]
LIMIT n OFFSET m;
```


```sql
1. FROM
2. JOIN
3. ON
4. WHERE
5. GROUP BY
6. HAVING
7. SELECT
8. DISTINCT
9. ORDER BY
10. LIMIT / OFFSET
```

```sql
SELECT
    e.department_id,
    COUNT(e.id) AS emp_count,
    AVG(e.salary) AS avg_salary
FROM employees e
JOIN departments d
    ON e.department_id = d.id
WHERE e.salary > 50000
GROUP BY e.department_id
HAVING AVG(e.salary) > 70000
ORDER BY avg_salary DESC
LIMIT 5;
```
