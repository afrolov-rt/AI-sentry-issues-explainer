"""PostgreSQL persistence for the application."""
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, UniqueConstraint, select
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config.settings import settings


class Base(DeclarativeBase):
    pass


class UserRecord(Base):
    __tablename__ = "users"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(Text)
    role: Mapped[str] = mapped_column(String(32), default="developer")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    workspace_id: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class WorkspaceRecord(Base):
    __tablename__ = "workspaces"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(100), index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    sentry_api_token: Mapped[Optional[str]] = mapped_column(Text)
    sentry_organization: Mapped[Optional[str]] = mapped_column(String(255))
    sentry_test_dsn: Mapped[Optional[str]] = mapped_column(Text)
    openai_api_key: Mapped[Optional[str]] = mapped_column(Text)
    workspace_settings: Mapped[dict[str, Any]] = mapped_column("settings", JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class SettingsRecord(Base):
    __tablename__ = "workspace_settings"
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    workspace_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), unique=True)
    openai_model: Mapped[str] = mapped_column(String(100), default="gpt-4")
    auto_analyze: Mapped[bool] = mapped_column(Boolean, default=False)
    notification_email: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class ProcessedIssueRecord(Base):
    __tablename__ = "processed_issues"
    __table_args__ = (
        UniqueConstraint("sentry_issue_id", "workspace_id", name="uq_processed_issue_workspace"),
        Index("ix_processed_issues_workspace_created", "workspace_id", "created_at"),
        Index("ix_processed_issues_workspace_status", "workspace_id", "status"),
    )
    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    sentry_issue_id: Mapped[str] = mapped_column(String(255), index=True)
    sentry_issue: Mapped[dict[str, Any]] = mapped_column(JSONB)
    ai_analysis: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(32), default="pending")
    assigned_to: Mapped[Optional[UUID]] = mapped_column(PG_UUID(as_uuid=True), nullable=True)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"))
    workspace_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("workspaces.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)


class Database:
    def __init__(self) -> None:
        self.engine = None
        self.session_factory = None

    async def connect(self) -> None:
        if not settings.DATABASE_URL:
            raise RuntimeError("DATABASE_URL must be configured")
        self.engine = create_async_engine(settings.DATABASE_URL, pool_pre_ping=True)
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)
        async with self.engine.connect():
            pass

    async def close(self) -> None:
        if self.engine is not None:
            await self.engine.dispose()

    def session(self) -> AsyncSession:
        if self.session_factory is None:
            raise RuntimeError("Database is not connected")
        return self.session_factory()


db = Database()


async def connect_to_database() -> None:
    await db.connect()


async def close_database_connection() -> None:
    await db.close()


def get_database() -> Database:
    return db


def as_dict(record: Any) -> dict[str, Any]:
    return {column.name: (str(value) if isinstance((value := getattr(record, column.name)), UUID) else value) for column in record.__table__.columns}


async def find_user_by_username(username: str) -> Optional[UserRecord]:
    async with db.session() as session:
        return await session.scalar(select(UserRecord).where(UserRecord.username == username))


async def find_user_by_id(user_id: str) -> Optional[UserRecord]:
    async with db.session() as session:
        return await session.get(UserRecord, UUID(user_id))


async def find_user_by_username_or_email(username: str, email: str) -> Optional[UserRecord]:
    from sqlalchemy import or_
    async with db.session() as session:
        return await session.scalar(select(UserRecord).where(or_(UserRecord.username == username, UserRecord.email == email)))


async def create_user(**values: Any) -> UserRecord:
    async with db.session() as session:
        record = UserRecord(**values)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def update_user_workspace(user_id: str, workspace_id: str) -> None:
    async with db.session() as session:
        record = await session.get(UserRecord, UUID(user_id))
        if record is None:
            raise LookupError("User not found")
        record.workspace_id = UUID(workspace_id)
        record.updated_at = datetime.utcnow()
        await session.commit()


async def get_workspace(workspace_id: str) -> Optional[WorkspaceRecord]:
    async with db.session() as session:
        return await session.get(WorkspaceRecord, UUID(workspace_id))


async def create_workspace(**values: Any) -> WorkspaceRecord:
    async with db.session() as session:
        values["owner_id"] = UUID(str(values["owner_id"]))
        record = WorkspaceRecord(**values)
        session.add(record)
        await session.commit()
        await session.refresh(record)
        return record


async def update_workspace(workspace_id: str, **values: Any) -> WorkspaceRecord:
    async with db.session() as session:
        record = await session.get(WorkspaceRecord, UUID(workspace_id))
        if record is None:
            raise LookupError("Workspace not found")
        for key, value in values.items():
            setattr(record, key, value)
        record.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(record)
        return record


async def get_workspace_settings(workspace_id: str) -> Optional[SettingsRecord]:
    async with db.session() as session:
        return await session.scalar(select(SettingsRecord).where(SettingsRecord.workspace_id == UUID(workspace_id)))


async def upsert_workspace_settings(workspace_id: str, **values: Any) -> SettingsRecord:
    async with db.session() as session:
        record = await session.scalar(select(SettingsRecord).where(SettingsRecord.workspace_id == UUID(workspace_id)))
        if record is None:
            record = SettingsRecord(workspace_id=UUID(workspace_id), **values)
            session.add(record)
        else:
            for key, value in values.items():
                setattr(record, key, value)
            record.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(record)
        return record


async def get_processed_issue(workspace_id: str, sentry_issue_id: str) -> Optional[ProcessedIssueRecord]:
    async with db.session() as session:
        return await session.scalar(select(ProcessedIssueRecord).where(ProcessedIssueRecord.workspace_id == UUID(workspace_id), ProcessedIssueRecord.sentry_issue_id == sentry_issue_id))


async def get_processed_statuses(workspace_id: str, issue_ids: list[str]) -> list[ProcessedIssueRecord]:
    async with db.session() as session:
        result = await session.scalars(select(ProcessedIssueRecord).where(ProcessedIssueRecord.workspace_id == UUID(workspace_id), ProcessedIssueRecord.sentry_issue_id.in_(issue_ids)))
        return list(result)


async def save_processed_issue(workspace_id: str, sentry_issue_id: str, **values: Any) -> ProcessedIssueRecord:
    async with db.session() as session:
        if "created_by" in values:
            values["created_by"] = UUID(str(values["created_by"]))
        record = await session.scalar(select(ProcessedIssueRecord).where(ProcessedIssueRecord.workspace_id == UUID(workspace_id), ProcessedIssueRecord.sentry_issue_id == sentry_issue_id))
        if record is None:
            record = ProcessedIssueRecord(workspace_id=UUID(workspace_id), sentry_issue_id=sentry_issue_id, **values)
            session.add(record)
        else:
            for key, value in values.items():
                setattr(record, key, value)
            record.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(record)
        return record


async def list_processed_issues(workspace_id: str, status: Optional[str], limit: int, skip: int) -> list[ProcessedIssueRecord]:
    async with db.session() as session:
        statement = select(ProcessedIssueRecord).where(ProcessedIssueRecord.workspace_id == UUID(workspace_id))
        if status:
            statement = statement.where(ProcessedIssueRecord.status == status)
        result = await session.scalars(statement.order_by(ProcessedIssueRecord.created_at.desc()).offset(skip).limit(limit))
        return list(result)
