# 📦 SQL

> 📅 Last updated: 2026-02-06 07:29 UTC
> 🔗 [View in Notion](https://www.notion.so/SQL-2ff6249cbbe2809aa899f705a9dac05a)

---

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
