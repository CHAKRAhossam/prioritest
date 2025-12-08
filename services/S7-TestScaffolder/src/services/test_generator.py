"""
Service de génération de tests JUnit à partir de l'analyse AST

MTP-S7-02: Génération templates JUnit
- Génère des squelettes de tests JUnit avec Mockito
- Crée des méthodes de test pour chaque méthode publique
- Génère le setup/teardown nécessaire
"""
from jinja2 import Environment, FileSystemLoader, Template
from pathlib import Path
from typing import Dict, List, Optional
from src.models.ast_models import ClassAnalysis, MethodInfo, FieldInfo
from src.services.mock_generator import MockGenerator


class TestGenerator:
    """
    Générateur de tests JUnit à partir d'une analyse AST.
    
    Génère :
    - Classe de test avec annotations JUnit 5
    - Méthodes de test pour chaque méthode publique
    - Mocks Mockito pour les dépendances
    - Setup/teardown si nécessaire
    """
    
    def __init__(self, template_dir: Optional[Path] = None):
        """
        Initialise le générateur de tests.
        
        Args:
            template_dir: Répertoire contenant les templates (défaut: src/templates)
        """
        if template_dir is None:
            template_dir = Path(__file__).parent.parent / "templates"
        
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        self.mock_generator = MockGenerator()
    
    def generate_test_class(
        self,
        class_analysis: ClassAnalysis,
        test_package: Optional[str] = None,
        test_class_suffix: str = "Test"
    ) -> str:
        """
        Génère une classe de test JUnit complète.
        
        Args:
            class_analysis: Analyse AST de la classe à tester
            test_package: Package pour la classe de test (défaut: package de la classe + ".test")
            test_class_suffix: Suffixe pour le nom de la classe de test (défaut: "Test")
        
        Returns:
            Code source Java de la classe de test générée
        """
        # Déterminer le package de test
        if test_package is None:
            if class_analysis.package_name:
                test_package = class_analysis.package_name + ".test"
            else:
                test_package = "test"
        
        # Nom de la classe de test
        test_class_name = f"{class_analysis.class_name}{test_class_suffix}"
        
        # Nom de l'instance de la classe sous test
        class_instance_name = self._to_camel_case(class_analysis.class_name)
        
        # Préparer les champs mockés
        mock_fields = self._extract_mock_fields(class_analysis.fields)
        
        # Préparer les méthodes de test
        test_methods = self._prepare_test_methods(
            class_analysis.methods,
            class_instance_name,
            class_analysis,
            mock_fields
        )
        
        # Préparer les imports nécessaires
        test_imports = self._prepare_test_imports(class_analysis)
        
        # Charger le template
        template = self.env.get_template("junit_test_class.j2")
        
        # Vérifier si Collections est nécessaire
        needs_collections = any(
            'List' in str(m.return_type) or 'Set' in str(m.return_type) or 'Map' in str(m.return_type)
            for m in class_analysis.methods
        ) or any(
            'List' in str(p.type) or 'Set' in str(p.type) or 'Map' in str(p.type)
            for m in class_analysis.methods
            for p in m.parameters
        )
        
        # Générer les configurations de mocks pour le setup
        mock_setup_lines = self._generate_mock_setup_lines(class_analysis, mock_fields)
        
        # Générer le code
        generated_code = template.render(
            test_package=test_package,
            test_class_name=test_class_name,
            class_under_test=class_analysis.full_qualified_name,
            class_instance_name=class_instance_name,
            mock_fields=mock_fields,
            test_methods=test_methods,
            test_imports=test_imports,
            needs_collections=needs_collections,
            mock_setup_lines=mock_setup_lines
        )
        
        return generated_code
    
    def _extract_mock_fields(self, fields: List[FieldInfo]) -> List[Dict]:
        """
        Extrait les champs qui doivent être mockés.
        
        Args:
            fields: Liste des champs de la classe
        
        Returns:
            Liste des champs à mocker avec leurs informations
        """
        mock_fields = []
        for field in fields:
            # Mocker les champs privés qui sont des dépendances (pas primitifs)
            if field.is_private and not self._is_primitive_type(field.type):
                mock_fields.append({
                    'name': field.name,
                    'type': field.type,
                    'annotations': field.annotations
                })
        return mock_fields
    
    def _prepare_test_methods(
        self,
        methods: List[MethodInfo],
        class_instance_name: str,
        class_analysis: ClassAnalysis,
        mock_fields: List[Dict]
    ) -> List[Dict]:
        """
        Prépare les méthodes de test à partir des méthodes publiques.
        
        Args:
            methods: Liste des méthodes de la classe
            class_instance_name: Nom de l'instance de la classe
        
        Returns:
            Liste des méthodes de test préparées
        """
        test_methods = []
        for method in methods:
            # Ne générer des tests que pour les méthodes publiques non-statiques
            if method.is_public and not method.is_static:
                # Générer les configurations de mocks pour cette méthode
                mock_config = self.mock_generator.generate_complete_mock_setup(
                    class_analysis,
                    method
                )
                
                test_method = {
                    'name': method.name,
                    'display_name': f"devrait tester {method.name}",
                    'return_type': method.return_type or 'void',
                    'is_void': method.is_void,
                    'parameters': self._prepare_parameters(method.parameters),
                    'throws_exceptions': method.throws_exceptions,
                    'mock_setup_lines': mock_config.get('setup', []),
                    'mock_verify_lines': mock_config.get('verify', [])
                }
                test_methods.append(test_method)
        return test_methods
    
    def _prepare_parameters(self, parameters: List) -> List[Dict]:
        """
        Prépare les paramètres pour les méthodes de test.
        
        Args:
            parameters: Liste des paramètres de la méthode
        
        Returns:
            Liste des paramètres préparés avec valeurs par défaut
        """
        prepared_params = []
        for param in parameters:
            param_dict = {
                'name': param.name if isinstance(param, dict) else param.name,
                'type': param.type if isinstance(param, dict) else param.type,
                'default_value': self._get_default_value(
                    param.type if isinstance(param, dict) else param.type,
                    param.is_primitive if isinstance(param, dict) else getattr(param, 'is_primitive', False)
                )
            }
            prepared_params.append(param_dict)
        return prepared_params
    
    def _get_default_value(self, param_type: str, is_primitive: bool) -> str:
        """
        Génère une valeur par défaut pour un paramètre.
        
        Args:
            param_type: Type du paramètre
            is_primitive: Si le type est primitif
        
        Returns:
            Valeur par défaut sous forme de chaîne Java
        """
        if is_primitive:
            primitive_defaults = {
                'int': '0',
                'long': '0L',
                'double': '0.0',
                'float': '0.0f',
                'boolean': 'false',
                'char': "'\\0'",
                'byte': '0',
                'short': '0'
            }
            return primitive_defaults.get(param_type, 'null')
        
        # Pour les types non-primitifs
        if 'List' in param_type or 'Collection' in param_type:
            return 'Collections.emptyList()'
        elif 'Set' in param_type:
            return 'Collections.emptySet()'
        elif 'Map' in param_type:
            return 'Collections.emptyMap()'
        elif 'Optional' in param_type:
            return 'Optional.empty()'
        else:
            return 'null'
    
    def _prepare_test_imports(self, class_analysis: ClassAnalysis) -> List[str]:
        """
        Prépare les imports nécessaires pour la classe de test.
        
        Args:
            class_analysis: Analyse de la classe
        
        Returns:
            Liste des imports nécessaires
        """
        imports = [
            class_analysis.full_qualified_name
        ]
        
        # Ajouter les imports pour les types de retour et paramètres
        for method in class_analysis.methods:
            if method.return_type and method.return_type not in ['void', 'int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short']:
                if method.return_type not in imports:
                    # Essayer de construire le nom complet depuis les imports
                    full_type = self._find_full_type(method.return_type, class_analysis.imports)
                    if full_type and full_type not in imports:
                        imports.append(full_type)
        
        # Ajouter Collections si nécessaire
        needs_collections = any(
            'List' in str(m.return_type) or 'Set' in str(m.return_type) or 'Map' in str(m.return_type)
            for m in class_analysis.methods
        )
        if needs_collections:
            imports.append('java.util.Collections')
        
        return imports
    
    def _find_full_type(self, type_name: str, imports: List[str]) -> Optional[str]:
        """
        Trouve le nom complet d'un type depuis les imports.
        
        Args:
            type_name: Nom court du type
            imports: Liste des imports
        
        Returns:
            Nom complet du type ou None
        """
        for imp in imports:
            if imp.endswith('.' + type_name) or imp == type_name:
                return imp
        return None
    
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
    
    def _generate_mock_setup_lines(
        self,
        class_analysis: ClassAnalysis,
        mock_fields: List[Dict]
    ) -> List[str]:
        """
        Génère les lignes de configuration des mocks pour le setup.
        
        Args:
            class_analysis: Analyse de la classe
            mock_fields: Liste des champs mockés
        
        Returns:
            Liste de lignes de code Java pour le setup
        """
        setup_lines = []
        
        # Générer des configurations basiques pour les mocks
        for mock_field in mock_fields:
            if 'Repository' in mock_field['type']:
                setup_lines.append(
                    f"        // Configuration du mock {mock_field['name']}"
                )
                setup_lines.append(
                    f"        // Exemple: when({mock_field['name']}.findById(any())).thenReturn(Optional.of(mockObject()));"
                )
        
        return setup_lines
    
    def _to_camel_case(self, name: str) -> str:
        """
        Convertit un nom en camelCase.
        
        Args:
            name: Nom à convertir
        
        Returns:
            Nom en camelCase
        """
        if not name:
            return name
        return name[0].lower() + name[1:] if len(name) > 1 else name.lower()

