# Auth REST API Example

Provides a simple sample implementation of authenticated requests using an expirable JWT Token

Project is built using:
- `FastAPI`
- `SQLModel`
- `DuckDB` (in-process OLAP dbms)

## Install & Run

Project's built using `uv`

Check the required Python version in `.python-version`. Install this version if needed with:
```bash
uv python install 3.13
```

Create a `venv` by doing:

```bash
uv venv --python 3.13
```

Install the package with:
```bash
make build
```

Run the project by executing
```bash
make run
```


# Usage

Check the API docs at http://localhost:8000/docs or at http://localhost:8000/redoc

**Create a new user**
```bash
curl -d '{"username":"user", "password":"pass", "full_name":"User Name", "email":"user.name@email.com"}' \
     -H "Content-Type: application/json" \
     -X POST http://localhost:8000/users/create
```

**Create auth token**
```bash
curl -d "username=user&password=pass" \
     -H "Content-Type: application/x-www-form-urlencoded" \
     -X POST http://localhost:8000/token
```

Response
```json
{
  "access_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzM5NjU3OTU1fQ.jjRlzjapdkvMhSMqljNhnfpmKkRN8cSrFtYU3tm-mVc",
  "token_type":"bearer"
}
```

**Get own data**

```bash
curl -H 'Authorization: bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwiZXhwIjoxNzM5NjU3OTU1fQ.jjRlzjapdkvMhSMqljNhnfpmKkRN8cSrFtYU3tm-mVc' \
     -L http://localhost:8000/users/me
```

Response

```json
{
  "full_name":"User Name",
  "username":"user",
  "email":"user.name@email.com"
}
```
