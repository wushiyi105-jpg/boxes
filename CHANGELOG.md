# 更新记录

## Unreleased

- 物品表扩到 80 类；新增 4 种车型容量与 10 条加价套路
- 新增 `quote` 命令：车型建议、三家报价归一、加价套路、可勾选改址清单一次成文
- `0001_init` 改为显式 `op.create_table` / `op.create_index`，运行期走 `alembic upgrade`
- `app/` 只依赖 `ports`，新增内存假实现用例
- 开 ruff `E2`/`E3`；CI 增加 `docker build` 与 `/health` 探活

## 1.0.0

- 体积与重量估算
- 一车 4.2 立方的趟数
- 三种计价归一
- 异常报价检测
- 22 家机构改址清单
