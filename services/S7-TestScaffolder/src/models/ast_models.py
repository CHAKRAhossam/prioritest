"""
Modèles de données pour l'analyse AST
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict


class MethodParameter(BaseModel):
    """Paramètre d'une méthode"""
    name: str = Field(..., description="Nom du paramètre", example="userId")
    type: str = Field(..., description="Type du paramètre", example="Long")
    is_primitive: bool = Field(False, description="Si le type est primitif", example=False)
    is_collection: bool = Field(False, description="Si le type est une collection", example=False)


class MethodInfo(BaseModel):
    """Information sur une méthode"""
    name: str = Field(..., description="Nom de la méthode", example="getUserById")
    return_type: Optional[str] = Field(None, description="Type de retour", example="User")
    parameters: List[MethodParameter] = Field(default_factory=list, description="Paramètres de la méthode")
    is_public: bool = Field(True, description="Si la méthode est publique", example=True)
    is_static: bool = Field(False, description="Si la méthode est statique", example=False)
    is_void: bool = Field(False, description="Si la méthode retourne void", example=False)
    throws_exceptions: List[str] = Field(default_factory=list, description="Exceptions lancées", example=["UserNotFoundException"])
    annotations: List[str] = Field(default_factory=list, description="Annotations", example=["@Override", "@Transactional"])


class ConstructorInfo(BaseModel):
    """Information sur un constructeur"""
    parameters: List[MethodParameter] = Field(default_factory=list, description="Paramètres du constructeur")
    is_public: bool = Field(True, description="Si le constructeur est public", example=True)
    annotations: List[str] = Field(default_factory=list, description="Annotations")


class FieldInfo(BaseModel):
    """Information sur un champ"""
    name: str = Field(..., description="Nom du champ", example="userRepository")
    type: str = Field(..., description="Type du champ", example="UserRepository")
    is_public: bool = Field(False, description="Si le champ est public", example=False)
    is_private: bool = Field(True, description="Si le champ est privé", example=True)
    is_final: bool = Field(False, description="Si le champ est final", example=False)
    is_static: bool = Field(False, description="Si le champ est statique", example=False)
    annotations: List[str] = Field(default_factory=list, description="Annotations", example=["@Autowired", "@Inject"])


class ClassAnalysis(BaseModel):
    """Analyse complète d'une classe Java"""
    class_name: str = Field(..., description="Nom de la classe", example="UserService")
    package_name: Optional[str] = Field(None, description="Nom du package", example="com.example.service")
    full_qualified_name: str = Field(..., description="Nom qualifié complet", example="com.example.service.UserService")
    is_abstract: bool = Field(False, description="Si la classe est abstraite", example=False)
    is_interface: bool = Field(False, description="Si c'est une interface", example=False)
    is_enum: bool = Field(False, description="Si c'est une énumération", example=False)
    extends: Optional[str] = Field(None, description="Classe parente", example="BaseService")
    implements: List[str] = Field(default_factory=list, description="Interfaces implémentées", example=["UserServiceInterface"])
    methods: List[MethodInfo] = Field(default_factory=list, description="Méthodes de la classe")
    constructors: List[ConstructorInfo] = Field(default_factory=list, description="Constructeurs")
    fields: List[FieldInfo] = Field(default_factory=list, description="Champs de la classe")
    imports: List[str] = Field(default_factory=list, description="Imports", example=["java.util.List", "org.springframework.stereotype.Service"])
    annotations: List[str] = Field(default_factory=list, description="Annotations de classe", example=["@Service", "@Component"])
    dependencies: List[str] = Field(default_factory=list, description="Dépendances (types utilisés)", example=["UserRepository", "EmailService"])












