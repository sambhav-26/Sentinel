"""Database utility functions for service layer."""

from typing import Optional, List, TypeVar, Generic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """
    Base repository class for common database operations.
    
    Each model can have a repository that inherits from this class
    to provide CRUD operations.
    """
    
    def __init__(self, session: AsyncSession, model_class: type[T]):
        """
        Initialize repository.
        
        Args:
            session: AsyncSession for database operations
            model_class: SQLAlchemy model class
        """
        self.session = session
        self.model_class = model_class
    
    async def create(self, **kwargs) -> T:
        """
        Create a new record.
        
        Args:
            **kwargs: Model fields
            
        Returns:
            Created model instance
        """
        instance = self.model_class(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance
    
    async def get_by_id(self, id: str) -> Optional[T]:
        """
        Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Model instance or None
        """
        return await self.session.get(self.model_class, id)
    
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[T]:
        """
        Get all records with pagination.
        
        Args:
            limit: Maximum records to return
            offset: Number of records to skip
            
        Returns:
            List of model instances
        """
        query = select(self.model_class).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, id: str, **kwargs) -> Optional[T]:
        """
        Update a record.
        
        Args:
            id: Record ID
            **kwargs: Fields to update
            
        Returns:
            Updated model instance or None
        """
        instance = await self.get_by_id(id)
        if not instance:
            return None
        
        for key, value in kwargs.items():
            setattr(instance, key, value)
        
        await self.session.flush()
        return instance
    
    async def delete(self, id: str) -> bool:
        """
        Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
        """
        instance = await self.get_by_id(id)
        if not instance:
            return False
        
        await self.session.delete(instance)
        await self.session.flush()
        return True
    
    async def count(self) -> int:
        """
        Count total records.
        
        Returns:
            Total count
        """
        from sqlalchemy import func
        query = select(func.count()).select_from(self.model_class)
        result = await self.session.execute(query)
        return result.scalar() or 0


async def commit_transaction(session: AsyncSession) -> None:
    """Commit transaction."""
    await session.commit()


async def rollback_transaction(session: AsyncSession) -> None:
    """Rollback transaction."""
    await session.rollback()
