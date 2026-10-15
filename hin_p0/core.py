"""Durable HIN task queue prototype. Does not execute agent commands."""
import json
import sqlite3
import time
import uuid
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
 id TEXT PRIMARY KEY, project TEXT NOT NULL, title TEXT NOT NULL,
 status TEXT NOT NULL CHECK(status IN ('READY','BLOCKED','RUNNING','REVIEW','DONE','FAILED')),
 deps TEXT NOT NULL, worker TEXT, lease_until REAL,
 evidence TEXT NOT NULL, created_at REAL NOT NULL, updated_at REAL NOT NULL
);
CREATE INDEX IF NOT EXISTS task_status ON tasks(status);
"""

class Factory:
    def __init__(self, db_path):
        self.db_path = str(db_path)
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path, timeout=15)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(SCHEMA)

    def close(self):
        self.conn.close()

    def _row(self, task_id):
        row = self.conn.execute("SELECT * FROM tasks WHERE id=?", (task_id,)).fetchone()
        if row is None:
            raise KeyError(task_id)
        return row

    def add(self, project, title, deps=()):
        dependencies = list(deps)
        if not project or not title:
            raise ValueError("project and title required")
        if len(dependencies) != len(set(dependencies)):
            raise ValueError("duplicate dependencies")
        for dep in dependencies:
            self._row(dep)
        identifier = uuid.uuid4().hex[:12]
        now = time.time()
        self.conn.execute(
            "INSERT INTO tasks VALUES (?,?,?,?,?,?,?,?,?,?)",
            (identifier, project, title, "BLOCKED" if dependencies else "READY",
             json.dumps(dependencies), None, None, "[]", now, now),
        )
        self.conn.commit()
        return identifier

    def list(self):
        return [dict(row) for row in self.conn.execute(
            "SELECT * FROM tasks ORDER BY created_at, id")]

    def refresh(self):
        for row in self.conn.execute(
            "SELECT * FROM tasks WHERE status='BLOCKED'").fetchall():
            if all(self._row(dep)["status"] == "DONE" for dep in json.loads(row["deps"])):
                self.conn.execute(
                    "UPDATE tasks SET status='READY',updated_at=? WHERE id=?",
                    (time.time(), row["id"]))
        self.conn.commit()

    def claim(self, task_id, worker, ttl=300):
        if not worker or ttl <= 0:
            raise ValueError("valid worker and positive lease required")
        self.refresh()
        now = time.time()
        result = self.conn.execute(
            "UPDATE tasks SET status='RUNNING',worker=?,lease_until=?,updated_at=? "
            "WHERE id=? AND status='READY'",
            (worker, now + ttl, now, task_id))
        self.conn.commit()
        if result.rowcount != 1:
            raise ValueError("task is not READY")
        return dict(self._row(task_id))

    def heartbeat(self, task_id, worker, ttl=300):
        if ttl <= 0:
            raise ValueError("ttl must be positive")
        now = time.time()
        result = self.conn.execute(
            "UPDATE tasks SET lease_until=?,updated_at=? WHERE id=? "
            "AND status='RUNNING' AND worker=? AND lease_until>?",
            (now + ttl, now, task_id, worker, now))
        self.conn.commit()
        return result.rowcount == 1

    def submit(self, task_id, worker, evidence):
        row = self._row(task_id)
        if not evidence or not isinstance(evidence, list):
            raise ValueError("nonempty evidence list required")
        if row["status"] != "RUNNING" or row["worker"] != worker or (
            row["lease_until"] or 0) <= time.time():
            raise ValueError("valid active lease required")
        self.conn.execute(
            "UPDATE tasks SET status='REVIEW', evidence=?,lease_until=NULL,updated_at=? WHERE id=?",
            (json.dumps(evidence), time.time(), task_id))
        self.conn.commit()

    def approve(self, task_id, reviewer):
        row = self._row(task_id)
        if row["status"] != "REVIEW":
            raise ValueError("task must be in REVIEW")
        if not reviewer or reviewer == row["worker"]:
            raise ValueError("independent reviewer required")
        self.conn.execute(
            "UPDATE tasks SET status='DONE',updated_at=? WHERE id=?",
            (time.time(), task_id))
        self.conn.commit()
        self.refresh()

    def expire(self):
        now = time.time()
        result = self.conn.execute(
            "UPDATE tasks SET status='FAILED',lease_until=NULL,updated_at=? "
            "WHERE status='RUNNING' AND lease_until<=?",
            (now, now))
        self.conn.commit()
        return result.rowcount
