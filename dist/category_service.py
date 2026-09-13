from typing import List, Optional
from uuid import UUID

from category import Category
from category_repository import CategoryRepository

class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    def validar_categoria(self, category_id: UUID) -> Category:
        """RN-PR-10/11: Verifica que la categoría exista y esté activa."""
        category = self.category_repo.get_by_id(category_id)
        if not category:
            raise ValueError(f"La categoría con ID {category_id} no existe.")
        return category

    def create_category(self, name: str) -> Category:
        if not name or len(name.strip()) < 3: # Basic validation
            raise ValueError("El nombre de la categoría debe tener al menos 3 caracteres.")
        
        # Check for uniqueness before inserting
        existing_categories = self.category_repo.get_all()
        if any(c.name.lower() == name.strip().lower() for c in existing_categories):
            raise ValueError(f"Ya existe una categoría con el nombre '{name}'.")

        new_category = Category(id=None, name=name.strip(), deleted_at=None)
        new_category.id = self.category_repo.insert(new_category)
        return new_category

    def get_all_categories(self) -> List[Category]:
        return self.category_repo.get_all()