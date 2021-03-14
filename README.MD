![ci](https://github.com/asteny/urlcut/actions/workflows/ci.yml/badge.svg)

Urlcut - yet another URL shortener built on asynchronous Python.

#### Requirements
```bash
python >=3.7
PostgreSQL
```

#### Run app steps

1. Use docker-compose with last image version from [packages](https://github.com/users/asteny/packages/container/package/urlcut/urlcut)
2. Run database migration command
```bash
docker exec -ti urlcut_urlcut_1 urlcut-db upgrade head
```

#### TODO
- swagger