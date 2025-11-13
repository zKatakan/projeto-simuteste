# tests/integration/test_api_integration.py

from datetime import date, timedelta


# ----------------------------
# Helpers para criar dados
# ----------------------------

def create_user(client, name="Ana", email="ana@example.com"):
    resp = client.post(
        "/api/v1/users",
        json={"name": name, "email": email},
    )
    assert resp.status_code == 200
    return resp.json()


def create_project(client, name="Projeto TCC", description="Simulação e Testes"):
    resp = client.post(
        "/api/v1/projects",
        json={"name": name, "description": description},
    )
    assert resp.status_code == 200
    return resp.json()


def create_task(
    client,
    *,
    title="Tarefa teste",
    project_id: int,
    assignee_id: int | None = None,
    priority: int = 3,
    due_date: str | None = None,
):
    payload = {
        "title": title,
        "project_id": project_id,
        "priority": priority,
    }
    if assignee_id is not None:
        payload["assignee_id"] = assignee_id
    if due_date is not None:
        payload["due_date"] = due_date

    resp = client.post("/api/v1/tasks", json=payload)
    return resp


# ----------------------------
# Testes básicos de criação
# ----------------------------

def test_create_user_ok(client):
    resp = client.post(
        "/api/v1/users",
        json={"name": "João", "email": "joao@example.com"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["id"] > 0
    assert body["name"] == "João"
    assert body["email"] == "joao@example.com"


def test_create_project_ok(client):
    project = create_project(client)
    assert project["id"] > 0
    assert project["name"] == "Projeto TCC"


def test_create_task_without_assignee_ok(client):
    project = create_project(client)
    resp = create_task(client, project_id=project["id"])
    assert resp.status_code == 200
    task = resp.json()
    assert task["id"] > 0
    assert task["project_id"] == project["id"]
    assert task["assignee_id"] is None
    assert task["status"] == "OPEN"


def test_create_task_with_assignee_ok(client):
    user = create_user(client)
    project = create_project(client)
    resp = create_task(
        client,
        project_id=project["id"],
        assignee_id=user["id"],
        title="Tarefa com responsável",
        priority=2,
    )
    assert resp.status_code == 200
    task = resp.json()
    assert task["assignee_id"] == user["id"]
    assert task["priority"] == 2


def test_list_tasks_by_project(client):
    user = create_user(client)
    project = create_project(client)

    t1 = create_task(client, project_id=project["id"], assignee_id=user["id"])
    assert t1.status_code == 200
    task1 = t1.json()

    resp = client.get(f"/api/v1/tasks?project_id={project['id']}")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert any(t["id"] == task1["id"] for t in data)


# ----------------------------
# Regras de negócio: due_date
# ----------------------------

def test_rule_due_date_past_blocks_creation(client):
    project = create_project(client)
    past_date = date(2000, 1, 1).isoformat()

    resp = create_task(
        client,
        project_id=project["id"],
        due_date=past_date,
        title="Data inválida",
        priority=2,
    )

    assert resp.status_code == 422
    body = resp.json()
    # Estrutura esperada: {"detail": {"code": "due_date_past", "message": "..."}}
    assert body["detail"]["code"] == "due_date_past"


# ----------------------------
# Regra: limite de tarefas abertas por usuário
# ----------------------------

def test_rule_user_overload_limit(client):
    user = create_user(client)
    project = create_project(client)

    # Primeira tarefa: deve ser criada normalmente
    r1 = create_task(
        client,
        project_id=project["id"],
        assignee_id=user["id"],
        title="Limite teste 1",
        priority=3,
    )
    assert r1.status_code == 200

    # Segunda tarefa: deve estourar a regra (user_overload)
    r2 = create_task(
        client,
        project_id=project["id"],
        assignee_id=user["id"],
        title="Limite teste 2",
        priority=3,
    )

    assert r2.status_code == 400
    body = r2.json()
    assert body["detail"]["code"] == "user_overload"


# ----------------------------
# Regra: não pode concluir sem responsável
# ----------------------------

def test_rule_cannot_finish_without_assignee(client):
    project = create_project(client)

    # Tarefa sem responsável
    r_task = create_task(
        client,
        project_id=project["id"],
        title="Sem responsável",
    )
    assert r_task.status_code == 200
    task = r_task.json()

    # Tentar marcar como DONE → deve falhar
    r_status = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        params={"new_status": "DONE"},
    )

    assert r_status.status_code == 422
    body = r_status.json()
    assert body["detail"]["code"] == "no_assignee"


def test_rule_can_finish_with_assignee(client):
    user = create_user(client)
    project = create_project(client)

    r_task = create_task(
        client,
        project_id=project["id"],
        assignee_id=user["id"],
        title="Com responsável",
    )
    assert r_task.status_code == 200
    task = r_task.json()

    r_status = client.patch(
        f"/api/v1/tasks/{task['id']}/status",
        params={"new_status": "DONE"},
    )
    assert r_status.status_code == 200
    body = r_status.json()
    assert body["id"] == task["id"]
    assert body["status"] == "DONE"


# ----------------------------
# Progresso do projeto
# ----------------------------

def test_project_progress_initial_zero(client):
    # Dois usuários distintos
    user1 = create_user(client)
    user2 = create_user(client)
    project = create_project(client)

    # Duas tarefas abertas no mesmo projeto,
    # cada uma atribuída a um usuário diferente
    for i, user in enumerate((user1, user2), start=1):
        r = create_task(
            client,
            project_id=project["id"],
            assignee_id=user["id"],
            title=f"Tarefa {i}",
        )
        assert r.status_code == 200

    # Progresso inicial ainda deve ser 0%
    r_progress = client.get(f"/api/v1/projects/{project['id']}/progress")
    assert r_progress.status_code == 200
    body = r_progress.json()
    assert body["progress"] == 0


def test_project_progress_updates_when_tasks_done(client):
    # Dois usuários, mesmo projeto
    user1 = create_user(client)
    user2 = create_user(client)
    project = create_project(client)

    # Cria 2 tarefas, uma para cada usuário (não estoura o limite por usuário)
    t1 = create_task(
        client,
        project_id=project["id"],
        assignee_id=user1["id"],
        title="Tarefa 1",
    ).json()
    t2 = create_task(
        client,
        project_id=project["id"],
        assignee_id=user2["id"],
        title="Tarefa 2",
    ).json()

    # Marca apenas uma como DONE
    r_status = client.patch(
        f"/api/v1/tasks/{t1['id']}/status",
        params={"new_status": "DONE"},
    )
    assert r_status.status_code == 200

    # Agora o progresso deve ser 50% (1 de 2 tarefas concluídas)
    r_progress = client.get(f"/api/v1/projects/{project['id']}/progress")
    assert r_progress.status_code == 200
    body = r_progress.json()
    assert body["progress"] == 50
