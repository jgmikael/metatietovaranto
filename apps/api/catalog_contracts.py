"""Optional asserted catalogue correspondences; never inferred OWL equivalence."""
from typing import Literal
from pydantic import Field, model_validator
from apps.api.distribution_contracts import Metadata, Iri

class CatalogueProvenance(Metadata):
    sourceUri:Iri
    sourceVersion:str=Field(min_length=1,max_length=200)
    evidenceSha256:str=Field(pattern=r'^[a-f0-9]{64}$')
    statement:str=Field(min_length=10,max_length=2000)

class CatalogueReference(Metadata):
    kind:Literal['attribute','scheme']
    catalogueUri:Iri
    entryUri:Iri
    version:str=Field(min_length=1,max_length=200)
    relation:Literal['equivalent','narrower','broader','related']
    rootShapeUri:Iri|None=None
    semanticPath:list[Iri]=Field(default_factory=list,max_length=10)
    provenance:CatalogueProvenance

    @model_validator(mode='after')
    def context(self):
        if self.kind=='attribute' and (not self.rootShapeUri or not self.semanticPath):
            raise ValueError('Attribuuttivastaavuus tarvitsee juurimuodon ja semanttisen polun')
        if self.kind=='scheme' and (self.rootShapeUri or self.semanticPath):
            raise ValueError('Todistusjärjestelyn viite ei ole yksittäinen ominaisuus')
        return self
