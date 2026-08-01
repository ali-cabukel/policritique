"""SQLAlchemy ORM models for UK political data."""

from __future__ import annotations

from sqlalchemy import (
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from policritique.db.schema import metadata


class Base(DeclarativeBase):
    metadata = metadata


_TIMESTAMP_DEFAULT = text("CURRENT_TIMESTAMP")


class Party(Base):
    __tablename__ = "parties"
    __table_args__ = (Index("idx_parties_ec_id", "ec_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ec_id: Mapped[str | None] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    short_name: Mapped[str | None] = mapped_column(String)
    register: Mapped[str | None] = mapped_column(String)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    election_results: Mapped[list[ElectionResult]] = relationship(back_populates="party")
    member_terms: Mapped[list[MemberTerm]] = relationship(back_populates="party")
    manifestos: Mapped[list[Manifesto]] = relationship(back_populates="party")


class Election(Base):
    __tablename__ = "elections"
    __table_args__ = (Index("idx_elections_date", "election_date"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    election_type: Mapped[str] = mapped_column(String, nullable=False)
    election_date: Mapped[str] = mapped_column(String, nullable=False)
    parliament_period: Mapped[str | None] = mapped_column(String)
    source: Mapped[str | None] = mapped_column(String)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    results: Mapped[list[ElectionResult]] = relationship(back_populates="election")
    manifestos: Mapped[list[Manifesto]] = relationship(back_populates="election")


class Constituency(Base):
    __tablename__ = "constituencies"
    __table_args__ = (Index("idx_constituencies_gss_code", "gss_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    gss_code: Mapped[str | None] = mapped_column(String)
    country: Mapped[str | None] = mapped_column(String)
    valid_from: Mapped[str | None] = mapped_column(String)
    valid_to: Mapped[str | None] = mapped_column(String)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    election_results: Mapped[list[ElectionResult]] = relationship(back_populates="constituency")
    member_terms: Mapped[list[MemberTerm]] = relationship(back_populates="constituency")


class Member(Base):
    __tablename__ = "members"
    __table_args__ = (Index("idx_members_parliament_id", "parliament_member_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    parliament_member_id: Mapped[int | None] = mapped_column(Integer, unique=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    display_name: Mapped[str | None] = mapped_column(String)
    gender: Mapped[str | None] = mapped_column(String)
    is_current: Mapped[int] = mapped_column(Integer, default=0)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    terms: Mapped[list[MemberTerm]] = relationship(back_populates="member")
    contacts: Mapped[list[MemberContact]] = relationship(
        back_populates="member", cascade="all, delete-orphan"
    )
    election_results: Mapped[list[ElectionResult]] = relationship(back_populates="member")


class MemberTerm(Base):
    __tablename__ = "member_terms"
    __table_args__ = (Index("idx_member_terms_member_id", "member_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    constituency_id: Mapped[int | None] = mapped_column(
        ForeignKey("constituencies.id", ondelete="SET NULL")
    )
    party_id: Mapped[int | None] = mapped_column(ForeignKey("parties.id", ondelete="SET NULL"))
    house: Mapped[str] = mapped_column(String, nullable=False, default="Commons")
    start_date: Mapped[str | None] = mapped_column(String)
    end_date: Mapped[str | None] = mapped_column(String)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    member: Mapped[Member] = relationship(back_populates="terms")
    constituency: Mapped[Constituency | None] = relationship(back_populates="member_terms")
    party: Mapped[Party | None] = relationship(back_populates="member_terms")


class MemberContact(Base):
    __tablename__ = "member_contacts"
    __table_args__ = (Index("idx_member_contacts_member_id", "member_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    member_id: Mapped[int] = mapped_column(ForeignKey("members.id", ondelete="CASCADE"))
    contact_type: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[str] = mapped_column(String, nullable=False)
    is_primary: Mapped[int] = mapped_column(Integer, default=0)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    member: Mapped[Member] = relationship(back_populates="contacts")


class ElectionResult(Base):
    __tablename__ = "election_results"
    __table_args__ = (
        UniqueConstraint("election_id", "constituency_id", "candidate_name"),
        Index("idx_election_results_election_id", "election_id"),
        Index("idx_election_results_constituency_id", "constituency_id"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    election_id: Mapped[int] = mapped_column(ForeignKey("elections.id", ondelete="CASCADE"))
    constituency_id: Mapped[int] = mapped_column(
        ForeignKey("constituencies.id", ondelete="CASCADE")
    )
    party_id: Mapped[int | None] = mapped_column(ForeignKey("parties.id", ondelete="SET NULL"))
    member_id: Mapped[int | None] = mapped_column(ForeignKey("members.id", ondelete="SET NULL"))
    candidate_name: Mapped[str] = mapped_column(String, nullable=False)
    votes: Mapped[int | None] = mapped_column(Integer)
    vote_share: Mapped[float | None] = mapped_column(Float)
    is_elected: Mapped[int] = mapped_column(Integer, default=0)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    election: Mapped[Election] = relationship(back_populates="results")
    constituency: Mapped[Constituency] = relationship(back_populates="election_results")
    party: Mapped[Party | None] = relationship(back_populates="election_results")
    member: Mapped[Member | None] = relationship(back_populates="election_results")


class Manifesto(Base):
    __tablename__ = "manifestos"
    __table_args__ = (Index("idx_manifestos_party_id", "party_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    party_id: Mapped[int] = mapped_column(ForeignKey("parties.id", ondelete="CASCADE"))
    election_id: Mapped[int | None] = mapped_column(ForeignKey("elections.id", ondelete="SET NULL"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    source_url: Mapped[str | None] = mapped_column(String)
    published_at: Mapped[str | None] = mapped_column(String)
    text: Mapped[str | None] = mapped_column(Text)
    collected_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )

    party: Mapped[Party] = relationship(back_populates="manifestos")
    election: Mapped[Election | None] = relationship(back_populates="manifestos")


class SyncLog(Base):
    __tablename__ = "sync_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(String, nullable=False)
    entity_ref: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str | None] = mapped_column(Text)
    synced_at: Mapped[str] = mapped_column(
        String, nullable=False, server_default=_TIMESTAMP_DEFAULT
    )
