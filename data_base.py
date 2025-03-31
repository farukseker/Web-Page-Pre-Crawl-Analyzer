import uuid
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

Base = declarative_base()
DATABASE_URL = "sqlite:///chat_history.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class ChatRoom(Base):
    __tablename__ = "chat_rooms"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime, default=datetime.utcnow)
    messages = relationship("ChatMessage", back_populates="chat_room", cascade="all, delete")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    room_id = Column(String, ForeignKey("chat_rooms.id"), nullable=False)
    role = Column(String, nullable=False)  # 'human' || 'ai'
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    chat_room = relationship("ChatRoom", back_populates="messages")


Base.metadata.create_all(bind=engine)


class ChatHistory:
    @staticmethod
    def create_room():
        session = SessionLocal()
        try:
            room = ChatRoom()
            session.add(room)
            session.commit()
            return room.id
        finally:
            session.close()

    @staticmethod
    def save_message(room_id: str, role: str, content: str):
        session = SessionLocal()
        message = ChatMessage(room_id=room_id, role=role, content=content)
        session.add(message)
        session.commit()
        session.close()

    @staticmethod
    def load_chat_history(room_id: str):
        session = SessionLocal()
        try:
            messages = session.query(ChatMessage).filter_by(room_id=room_id).order_by(ChatMessage.timestamp).all()
            return [{"role": msg.role, "content": msg.content, "timestamp": msg.timestamp.isoformat()} for msg in messages]
        finally:
            session.close()

    @staticmethod
    def remove_all_chats():
        session = SessionLocal()
        try:
            session.query(ChatMessage).delete()
            session.query(ChatRoom).delete()
            session.commit()
        finally:
            session.close()


if __name__ == "__main__":
    room_id = ChatHistory.create_room()
    print(f"Room id: {room_id}")
    ChatHistory.save_message(room_id, "human", "Merhaba, nasılsın?")
    ChatHistory.save_message(room_id, "ai", "İyiyim, sen nasılsın2?")
    history = ChatHistory.load_chat_history(room_id)
    print(json.dumps(history, indent=2, ensure_ascii=False))
