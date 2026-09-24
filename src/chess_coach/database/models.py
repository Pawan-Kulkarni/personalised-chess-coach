from datetime import date
from sqlalchemy import JSON
from sqlalchemy import ForeignKey, Text, Float, Integer, String, Date
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import UniqueConstraint

class Base(DeclarativeBase):
    pass


class Game(Base):
    __tablename__ = "games"

    game_id: Mapped[int] = mapped_column(primary_key=True)

    white_player: Mapped[str] = mapped_column(String(100))
    black_player: Mapped[str] = mapped_column(String(100))
    result: Mapped[str] = mapped_column(String(10))

    date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )

    event: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True
    )

    pgn: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    pgn_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    positions: Mapped[list["Position"]] = relationship(
        back_populates="game"
    )
    
    white_player_id = mapped_column(
        ForeignKey("players.player_id"),
        nullable=True,
    )

    black_player_id = mapped_column(
        ForeignKey("players.player_id"),
        nullable=True,
    )
    
    white_player_ref = relationship(
    "Player",
    foreign_keys=[white_player_id],
    )

    black_player_ref = relationship(
        "Player",
        foreign_keys=[black_player_id],
    )


class Position(Base):
    __tablename__ = "positions"

    position_id: Mapped[int] = mapped_column(primary_key=True)

    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.game_id")
    )

    ply: Mapped[int] = mapped_column(Integer)

    move_number: Mapped[int] = mapped_column(Integer)

    move_uci: Mapped[str] = mapped_column(String(10))

    move_san: Mapped[str] = mapped_column(String(20))

    fen: Mapped[str] = mapped_column(Text)

    game: Mapped["Game"] = relationship(
        back_populates="positions"
    )

    engine_analysis: Mapped["EngineAnalysis | None"] = relationship(
        back_populates="position"
    )
class EngineAnalysis(Base):
    __tablename__ = "engine_analysis"

    analysis_id: Mapped[int] = mapped_column(primary_key=True)

    position_id: Mapped[int] = mapped_column(
        ForeignKey("positions.position_id")
    )

    evaluation: Mapped[float] = mapped_column(Float)

    best_move: Mapped[str] = mapped_column(String(20))

    depth: Mapped[int] = mapped_column(Integer)

    principal_variation: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    position: Mapped["Position"] = relationship(
    back_populates="engine_analysis"
)
    
    
    
class MoveAnalysis(Base):
    __tablename__ = "move_analysis"

    analysis_id = mapped_column(Integer, primary_key=True)
    position_id = mapped_column(
        ForeignKey("positions.position_id"),
        nullable=False,
        unique=True,
    )

    player = mapped_column(String(10), nullable=False)
    evaluation_loss = mapped_column(Float, nullable=False)
    classification = mapped_column(String(20), nullable=False)
    tactical_analysis = mapped_column(JSON, nullable=False, default=dict)
    position = relationship("Position")
    
class Player(Base):
    __tablename__ = "players"

    player_id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String(100), nullable=False, unique=True)

    accounts = relationship(
        "PlayerAccount",
        back_populates="player",
        cascade="all, delete-orphan",
    )


class PlayerAccount(Base):
    __tablename__ = "player_accounts"

    account_id = mapped_column(Integer, primary_key=True)

    player_id = mapped_column(
        ForeignKey("players.player_id"),
        nullable=False,
    )

    platform = mapped_column(
        String(30),
        nullable=False,
    )

    username = mapped_column(
        String(100),
        nullable=False,
    )
    
    __table_args__ = (
        UniqueConstraint("platform", "username"),
    )

    player = relationship(
        "Player",
        back_populates="accounts",
    )