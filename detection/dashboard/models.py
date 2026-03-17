"""
SQLAlchemy models for the dashboard: users, detectors, test sets, evaluations.
"""

import json
from datetime import datetime

import bcrypt
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    role = db.Column(db.Text, nullable=False, default="user")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    detectors = db.relationship("Detector", backref="owner", lazy=True)
    evaluations = db.relationship("Evaluation", backref="owner", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    @property
    def is_admin(self):
        return self.role == "admin"


class Detector(db.Model):
    __tablename__ = "detectors"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    name = db.Column(db.Text, nullable=False)
    api_url = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, default="")
    author = db.Column(db.Text, default="")
    paper_url = db.Column(db.Text, default="")
    github_url = db.Column(db.Text, default="")
    status = db.Column(db.Text, default="pending")
    last_test = db.Column(db.DateTime)
    test_details = db.Column(db.Text)  # JSON
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluations = db.relationship("Evaluation", backref="detector", lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "api_url": self.api_url,
            "description": self.description,
            "author": self.author,
            "paper_url": self.paper_url,
            "github_url": self.github_url,
            "status": self.status,
            "last_test": self.last_test.isoformat() if self.last_test else None,
            "test_details": json.loads(self.test_details) if self.test_details else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TestSet(db.Model):
    __tablename__ = "test_sets"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, default="")
    dataset_keys = db.Column(db.Text, nullable=False)  # JSON array
    total_videos = db.Column(db.Integer, default=0)
    is_archived = db.Column(db.Integer, default=0)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluations = db.relationship("Evaluation", backref="test_set", lazy=True)

    def get_dataset_keys(self):
        return json.loads(self.dataset_keys) if self.dataset_keys else []

    def set_dataset_keys(self, keys):
        self.dataset_keys = json.dumps(keys)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "dataset_keys": self.get_dataset_keys(),
            "total_videos": self.total_videos,
            "is_archived": bool(self.is_archived),
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    detector_id = db.Column(db.Integer, db.ForeignKey("detectors.id"), nullable=False)
    test_set_id = db.Column(db.Integer, db.ForeignKey("test_sets.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    status = db.Column(db.Text, default="pending")
    videos_done = db.Column(db.Integer, default=0)
    total_videos = db.Column(db.Integer, default=0)
    errors_count = db.Column(db.Integer, default=0)
    metrics = db.Column(db.Text)  # JSON
    is_published = db.Column(db.Integer, default=0)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    error_message = db.Column(db.Text)
    avg_time_per_video = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    scores = db.relationship("EvaluationScore", backref="evaluation", lazy=True)

    def get_metrics(self):
        return json.loads(self.metrics) if self.metrics else None

    def set_metrics(self, m):
        self.metrics = json.dumps(m)

    def to_dict(self):
        return {
            "id": self.id,
            "detector_id": self.detector_id,
            "test_set_id": self.test_set_id,
            "user_id": self.user_id,
            "status": self.status,
            "videos_done": self.videos_done,
            "total_videos": self.total_videos,
            "errors_count": self.errors_count,
            "metrics": self.get_metrics(),
            "is_published": bool(self.is_published),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error_message": self.error_message,
            "avg_time_per_video": self.avg_time_per_video,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "detector_name": self.detector.name if self.detector else None,
            "test_set_name": self.test_set.name if self.test_set else None,
        }


class PhotoCheck(db.Model):
    __tablename__ = "photo_checks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    uuid = db.Column(db.Text, unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.Text, nullable=False)
    file_size = db.Column(db.Integer, default=0)
    status = db.Column(db.Text, default="pending")  # pending/uploading/running/completed/failed
    current_step = db.Column(db.Text, default="")
    detectors_done = db.Column(db.Integer, default=0)
    detectors_total = db.Column(db.Integer, default=6)
    results = db.Column(db.Text)  # JSON
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)

    user = db.relationship("User", backref="photo_checks")

    def get_results(self):
        return json.loads(self.results) if self.results else None

    def set_results(self, r):
        self.results = json.dumps(r)

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "user_id": self.user_id,
            "filename": self.filename,
            "file_size": self.file_size,
            "status": self.status,
            "current_step": self.current_step,
            "detectors_done": self.detectors_done,
            "detectors_total": self.detectors_total,
            "results": self.get_results(),
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class EvaluationScore(db.Model):
    __tablename__ = "evaluation_scores"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    evaluation_id = db.Column(db.Integer, db.ForeignKey("evaluations.id"), nullable=False)
    video_path = db.Column(db.Text, nullable=False)
    label = db.Column(db.Text, nullable=False)
    dataset_key = db.Column(db.Text, nullable=False)
    score = db.Column(db.Float)
    predicted_label = db.Column(db.Text)
    error = db.Column(db.Text)
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
