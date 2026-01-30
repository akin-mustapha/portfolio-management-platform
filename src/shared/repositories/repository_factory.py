from src.services.ingestion.infrastructure.repositories import repositories

class RepositoryFactory:
  registry: {}

  def __init__(self):
    for repository in repositories:
      self.registry.update({repository.entity_name().lower(): repository})
    

  def get_repository(name, **kwargs):
    pass