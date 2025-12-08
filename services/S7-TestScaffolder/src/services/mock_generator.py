"""
Service de génération de mocks Mockito

MTP-S7-04: Génération mocks
- Génère des mocks Mockito pour les dépendances
- Crée les configurations when/thenReturn
- Génère les verify() pour les méthodes void
- Gère les mocks pour les collections et les Optional
"""
from typing import List, Dict, Optional
from src.models.ast_models import ClassAnalysis, MethodInfo, FieldInfo, MethodParameter


class MockGenerator:
    """
    Générateur de mocks Mockito pour les tests.
    
    Génère :
    - Déclarations @Mock pour les dépendances
    - Configurations when/thenReturn
    - Verify() pour les méthodes void
    - Mocks pour les collections et Optional
    """
    
    def __init__(self):
        """Initialise le générateur de mocks"""
        pass
    
    def generate_mock_declarations(self, fields: List[FieldInfo]) -> List[Dict]:
        """
        Génère les déclarations @Mock pour les dépendances.
        
        Args:
            fields: Liste des champs de la classe
        
        Returns:
            Liste des déclarations de mocks
        """
        mock_declarations = []
        
        for field in fields:
            # Mocker les champs privés qui sont des dépendances (pas primitifs)
            if field.is_private and not self._is_primitive_type(field.type):
                mock_declarations.append({
                    'name': field.name,
                    'type': field.type,
                    'annotations': field.annotations,
                    'is_final': field.is_final
                })
        
        return mock_declarations
    
    def generate_mock_setup(
        self,
        method: MethodInfo,
        mock_fields: List[Dict],
        class_instance_name: str
    ) -> List[str]:
        """
        Génère le code de configuration des mocks pour une méthode.
        
        Args:
            method: Méthode à tester
            mock_fields: Liste des champs mockés
            class_instance_name: Nom de l'instance de la classe sous test
        
        Returns:
            Liste de lignes de code Java pour configurer les mocks
        """
        setup_lines = []
        
        # Analyser les appels potentiels aux mocks dans la méthode
        # Pour l'instant, on génère des configurations basiques
        
        # Si la méthode retourne quelque chose, on peut configurer un mock
        if method.return_type and not method.is_void:
            # Chercher un mock qui pourrait être utilisé
            for mock_field in mock_fields:
                # Générer une configuration basique
                if 'Repository' in mock_field['type'] or 'Service' in mock_field['type']:
                    setup_lines.append(
                        f"        // Configurer le mock {mock_field['name']}"
                    )
                    setup_lines.append(
                        f"        // when({mock_field['name']}.someMethod()).thenReturn(expectedValue);"
                    )
        
        return setup_lines
    
    def generate_mock_verify(
        self,
        method: MethodInfo,
        mock_fields: List[Dict]
    ) -> List[str]:
        """
        Génère le code verify() pour une méthode void.
        
        Args:
            method: Méthode void à vérifier
            mock_fields: Liste des champs mockés
        
        Returns:
            Liste de lignes de code Java pour verify()
        """
        verify_lines = []
        
        if method.is_void:
            # Pour les méthodes void, suggérer des verify()
            for mock_field in mock_fields:
                if 'Repository' in mock_field['type']:
                    verify_lines.append(
                        f"        // Vérifier les appels aux mocks"
                    )
                    verify_lines.append(
                        f"        // verify({mock_field['name']}, times(1)).someMethod();"
                    )
                    break
        
        return verify_lines
    
    def generate_mock_for_method_call(
        self,
        mock_name: str,
        mock_type: str,
        method_name: str,
        return_type: Optional[str],
        parameters: List[MethodParameter]
    ) -> str:
        """
        Génère le code pour un mock spécifique d'un appel de méthode.
        
        Args:
            mock_name: Nom du mock
            mock_type: Type du mock
            method_name: Nom de la méthode mockée
            return_type: Type de retour de la méthode
            parameters: Paramètres de la méthode
        
        Returns:
            Code Java pour when/thenReturn ou when/thenThrow
        """
        # Construire les paramètres pour l'appel
        param_list = ", ".join([f"any({p.type}.class)" if not p.is_primitive else f"any{p.type.capitalize()}()" for p in parameters])
        
        if return_type and return_type != 'void':
            # Générer une valeur de retour par défaut
            return_value = self._get_default_return_value(return_type)
            return f"when({mock_name}.{method_name}({param_list})).thenReturn({return_value});"
        else:
            return f"doNothing().when({mock_name}).{method_name}({param_list});"
    
    def generate_mock_for_collection(
        self,
        mock_name: str,
        collection_type: str,
        element_type: Optional[str] = None
    ) -> str:
        """
        Génère le code pour mocker une collection.
        
        Args:
            mock_name: Nom du mock
            collection_type: Type de collection (List, Set, Map)
            element_type: Type des éléments (optionnel)
        
        Returns:
            Code Java pour mocker la collection
        """
        if 'List' in collection_type:
            return f"when({mock_name}).thenReturn(Collections.emptyList());"
        elif 'Set' in collection_type:
            return f"when({mock_name}).thenReturn(Collections.emptySet());"
        elif 'Map' in collection_type:
            return f"when({mock_name}).thenReturn(Collections.emptyMap());"
        else:
            return f"when({mock_name}).thenReturn(null);"
    
    def generate_mock_for_optional(
        self,
        mock_name: str,
        optional_type: str
    ) -> str:
        """
        Génère le code pour mocker un Optional.
        
        Args:
            mock_name: Nom du mock
            optional_type: Type de l'Optional (ex: Optional<User>)
        
        Returns:
            Code Java pour mocker l'Optional
        """
        return f"when({mock_name}).thenReturn(Optional.empty());"
    
    def generate_complete_mock_setup(
        self,
        class_analysis: ClassAnalysis,
        method: MethodInfo
    ) -> Dict[str, List[str]]:
        """
        Génère une configuration complète de mocks pour une méthode.
        
        Args:
            class_analysis: Analyse de la classe
            method: Méthode à tester
        
        Returns:
            Dictionnaire avec 'setup' et 'verify' contenant les lignes de code
        """
        mock_fields = self.generate_mock_declarations(class_analysis.fields)
        
        setup_lines = []
        verify_lines = []
        
        # Générer le setup pour chaque mock potentiellement utilisé
        for mock_field in mock_fields:
            # Analyser si ce mock pourrait être utilisé dans la méthode
            # Pour l'instant, on génère des templates génériques
            
            # Si c'est un Repository, il pourrait avoir des méthodes comme findById, save, etc.
            if 'Repository' in mock_field['type']:
                # Générer des configurations basiques
                if not method.is_void and method.parameters:
                    # Si la méthode a des paramètres, on peut supposer qu'elle utilise findById
                    first_param = method.parameters[0]
                    if 'Id' in first_param.name.lower() or 'id' in first_param.name.lower():
                        setup_lines.append(
                            f"        when({mock_field['name']}.findById(any())).thenReturn(Optional.of(mock{method.return_type or 'Object'}()));"
                        )
                
                # Si c'est une méthode void, suggérer verify
                if method.is_void:
                    verify_lines.append(
                        f"        verify({mock_field['name']}, times(1)).deleteById(any());"
                    )
        
        return {
            'setup': setup_lines,
            'verify': verify_lines
        }
    
    def _get_default_return_value(self, return_type: str) -> str:
        """
        Génère une valeur de retour par défaut pour un type.
        
        Args:
            return_type: Type de retour
        
        Returns:
            Valeur Java par défaut
        """
        if return_type == 'void':
            return ""
        
        # Types primitifs
        if return_type == 'int':
            return '0'
        elif return_type == 'long':
            return '0L'
        elif return_type == 'double':
            return '0.0'
        elif return_type == 'float':
            return '0.0f'
        elif return_type == 'boolean':
            return 'false'
        
        # Collections
        if 'List' in return_type:
            return 'Collections.emptyList()'
        elif 'Set' in return_type:
            return 'Collections.emptySet()'
        elif 'Map' in return_type:
            return 'Collections.emptyMap()'
        
        # Optional
        if 'Optional' in return_type:
            return 'Optional.empty()'
        
        # Objets - générer un nom de mock
        type_name = return_type.split('.')[-1] if '.' in return_type else return_type
        return f"mock{type_name}()"
    
    def _is_primitive_type(self, type_name: str) -> bool:
        """
        Vérifie si un type est primitif.
        
        Args:
            type_name: Nom du type
        
        Returns:
            True si le type est primitif
        """
        primitives = ['int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short', 'void']
        return type_name in primitives

