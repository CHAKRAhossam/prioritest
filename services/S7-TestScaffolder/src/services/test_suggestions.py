"""
Service de suggestions de cas de test

MTP-S7-03: Suggestions cas de test
- Classes d'équivalence (valeurs valides, invalides)
- Tests de limites (boundary values)
- Tests d'exceptions
- Tests de null
- Tests de collections vides/pleines
"""
from typing import List, Dict, Optional
from src.models.ast_models import MethodInfo, MethodParameter, ClassAnalysis
from src.models.test_suggestions import (
    TestSuggestion, MethodSuggestions, ClassSuggestions, TestCaseType
)


class TestSuggestionsService:
    """
    Service pour générer des suggestions de cas de test.
    
    Génère des suggestions basées sur :
    - Classes d'équivalence
    - Tests de limites (boundary values)
    - Tests d'exceptions
    - Tests de null
    - Tests de collections
    """
    
    def __init__(self):
        """Initialise le service de suggestions"""
        pass
    
    def generate_suggestions(
        self,
        class_analysis: ClassAnalysis,
        include_private: bool = False
    ) -> ClassSuggestions:
        """
        Génère des suggestions de cas de test pour une classe.
        
        Args:
            class_analysis: Analyse AST de la classe
            include_private: Inclure les méthodes privées (défaut: False)
        
        Returns:
            Suggestions complètes pour la classe
        """
        method_suggestions_list = []
        total_suggestions = 0
        
        for method in class_analysis.methods:
            # Ne générer des suggestions que pour les méthodes publiques (ou privées si demandé)
            if method.is_public or (include_private and not method.is_static):
                method_suggestions = self._generate_method_suggestions(method)
                method_suggestions_list.append(method_suggestions)
                total_suggestions += method_suggestions.total_count
        
        # Estimer la couverture
        coverage_estimate = self._estimate_coverage(method_suggestions_list)
        
        return ClassSuggestions(
            class_name=class_analysis.class_name,
            method_suggestions=method_suggestions_list,
            total_suggestions=total_suggestions,
            coverage_estimate=coverage_estimate
        )
    
    def _generate_method_suggestions(self, method: MethodInfo) -> MethodSuggestions:
        """
        Génère des suggestions pour une méthode spécifique.
        
        Args:
            method: Information sur la méthode
        
        Returns:
            Suggestions pour la méthode
        """
        suggestions = []
        
        # 1. Suggestions d'équivalence
        suggestions.extend(self._generate_equivalence_suggestions(method))
        
        # 2. Suggestions de limites
        suggestions.extend(self._generate_boundary_suggestions(method))
        
        # 3. Suggestions d'exceptions
        suggestions.extend(self._generate_exception_suggestions(method))
        
        # 4. Suggestions de null
        suggestions.extend(self._generate_null_suggestions(method))
        
        # 5. Suggestions de collections
        suggestions.extend(self._generate_collection_suggestions(method))
        
        return MethodSuggestions(
            method_name=method.name,
            suggestions=suggestions,
            total_count=len(suggestions)
        )
    
    def _generate_equivalence_suggestions(self, method: MethodInfo) -> List[TestSuggestion]:
        """Génère des suggestions de classes d'équivalence"""
        suggestions = []
        
        # Valeur valide typique
        valid_params = {}
        for param in method.parameters:
            valid_params[param.name] = self._get_valid_value(param)
        
        if valid_params:
            suggestions.append(TestSuggestion(
                type=TestCaseType.EQUIVALENCE,
                method_name=method.name,
                description=f"Tester avec des valeurs valides typiques",
                test_name=f"test{self._to_camel_case(method.name)}_WithValidValues",
                parameters=valid_params,
                expected_result="assertNotNull(result)" if not method.is_void else None,
                priority=1,
                category="Équivalence - Valeur valide"
            ))
        
        # Valeur invalide (si applicable)
        invalid_params = {}
        for param in method.parameters:
            if not param.is_primitive:
                invalid_params[param.name] = "INVALID_VALUE"
        
        if invalid_params:
            suggestions.append(TestSuggestion(
                type=TestCaseType.EQUIVALENCE,
                method_name=method.name,
                description=f"Tester avec des valeurs invalides",
                test_name=f"test{self._to_camel_case(method.name)}_WithInvalidValues",
                parameters=invalid_params,
                expected_exception="IllegalArgumentException" if not method.throws_exceptions else method.throws_exceptions[0],
                priority=2,
                category="Équivalence - Valeur invalide"
            ))
        
        return suggestions
    
    def _generate_boundary_suggestions(self, method: MethodInfo) -> List[TestSuggestion]:
        """Génère des suggestions de tests de limites"""
        suggestions = []
        
        for param in method.parameters:
            if param.is_primitive:
                param_type = param.type
                
                # Tests de limites selon le type
                if param_type in ['int', 'long']:
                    # Minimum, maximum, zéro
                    boundary_cases = [
                        ("MinValue", "Long.MIN_VALUE" if param_type == 'long' else "Integer.MIN_VALUE"),
                        ("MaxValue", "Long.MAX_VALUE" if param_type == 'long' else "Integer.MAX_VALUE"),
                        ("Zero", "0" + ("L" if param_type == 'long' else ""))
                    ]
                    
                    for case_name, case_value in boundary_cases:
                        params = {param.name: case_value}
                        suggestions.append(TestSuggestion(
                            type=TestCaseType.BOUNDARY,
                            method_name=method.name,
                            description=f"Tester limite {case_name.lower()} pour {param.name}",
                            test_name=f"test{self._to_camel_case(method.name)}_With{case_name}",
                            parameters=params,
                            priority=2,
                            category=f"Limite - {case_name}"
                        ))
                
                elif param_type in ['double', 'float']:
                    # Positif, négatif, zéro
                    boundary_cases = [
                        ("Positive", "1.0" + ("f" if param_type == 'float' else "")),
                        ("Negative", "-1.0" + ("f" if param_type == 'float' else "")),
                        ("Zero", "0.0" + ("f" if param_type == 'float' else ""))
                    ]
                    
                    for case_name, case_value in boundary_cases:
                        params = {param.name: case_value}
                        suggestions.append(TestSuggestion(
                            type=TestCaseType.BOUNDARY,
                            method_name=method.name,
                            description=f"Tester limite {case_name.lower()} pour {param.name}",
                            test_name=f"test{self._to_camel_case(method.name)}_With{case_name}",
                            parameters=params,
                            priority=2,
                            category=f"Limite - {case_name}"
                        ))
        
        return suggestions
    
    def _generate_exception_suggestions(self, method: MethodInfo) -> List[TestSuggestion]:
        """Génère des suggestions de tests d'exceptions"""
        suggestions = []
        
        # Si la méthode déclare des exceptions
        for exception in method.throws_exceptions:
            # Générer un cas de test pour chaque exception
            exception_params = {}
            for param in method.parameters:
                exception_params[param.name] = self._get_exception_trigger_value(param)
            
            suggestions.append(TestSuggestion(
                type=TestCaseType.EXCEPTION,
                method_name=method.name,
                description=f"Tester que la méthode lance {exception}",
                test_name=f"test{self._to_camel_case(method.name)}_Throws{exception}",
                parameters=exception_params,
                expected_exception=exception,
                priority=1,
                category=f"Exception - {exception}"
            ))
        
        return suggestions
    
    def _generate_null_suggestions(self, method: MethodInfo) -> List[TestSuggestion]:
        """Génère des suggestions de tests de null"""
        suggestions = []
        
        # Pour chaque paramètre non-primitif
        for param in method.parameters:
            if not param.is_primitive:
                null_params = {}
                for p in method.parameters:
                    if p.name == param.name:
                        null_params[p.name] = "null"
                    else:
                        null_params[p.name] = self._get_valid_value(p)
                
                suggestions.append(TestSuggestion(
                    type=TestCaseType.NULL,
                    method_name=method.name,
                    description=f"Tester avec {param.name} = null",
                    test_name=f"test{self._to_camel_case(method.name)}_WithNull{self._to_camel_case(param.name)}",
                    parameters=null_params,
                    expected_exception="NullPointerException" or "IllegalArgumentException",
                    priority=2,
                    category="Null - Paramètre null"
                ))
        
        return suggestions
    
    def _generate_collection_suggestions(self, method: MethodInfo) -> List[TestSuggestion]:
        """Génère des suggestions pour les collections"""
        suggestions = []
        
        for param in method.parameters:
            if param.is_collection:
                # Collection vide
                empty_params = {}
                for p in method.parameters:
                    if p.name == param.name:
                        empty_params[p.name] = "Collections.emptyList()" if "List" in param.type else "Collections.emptySet()"
                    else:
                        empty_params[p.name] = self._get_valid_value(p)
                
                suggestions.append(TestSuggestion(
                    type=TestCaseType.EMPTY,
                    method_name=method.name,
                    description=f"Tester avec {param.name} vide",
                    test_name=f"test{self._to_camel_case(method.name)}_WithEmpty{self._to_camel_case(param.name)}",
                    parameters=empty_params,
                    priority=2,
                    category="Collection - Vide"
                ))
        
        # Si le type de retour est une collection
        if method.return_type and ('List' in method.return_type or 'Set' in method.return_type or 'Collection' in method.return_type):
            valid_params = {}
            for param in method.parameters:
                valid_params[param.name] = self._get_valid_value(param)
            
            suggestions.append(TestSuggestion(
                type=TestCaseType.EDGE_CASE,
                method_name=method.name,
                description="Tester que le résultat n'est pas null et est une collection",
                test_name=f"test{self._to_camel_case(method.name)}_ReturnsCollection",
                parameters=valid_params,
                expected_result="assertNotNull(result); assertFalse(result.isEmpty())",
                priority=2,
                category="Collection - Retour"
            ))
        
        return suggestions
    
    def _get_valid_value(self, param: MethodParameter) -> str:
        """Génère une valeur valide pour un paramètre"""
        if param.is_primitive:
            defaults = {
                'int': '1',
                'long': '1L',
                'double': '1.0',
                'float': '1.0f',
                'boolean': 'true',
                'char': "'a'",
                'byte': '1',
                'short': '1'
            }
            return defaults.get(param.type, 'null')
        
        if param.is_collection:
            if 'List' in param.type:
                return 'Collections.emptyList()'
            elif 'Set' in param.type:
                return 'Collections.emptySet()'
            elif 'Map' in param.type:
                return 'Collections.emptyMap()'
        
        # Pour les objets, utiliser null ou un nom suggéré
        if 'Optional' in param.type:
            return 'Optional.empty()'
        
        # Générer un nom basé sur le type
        type_name = param.type.split('.')[-1] if '.' in param.type else param.type
        return f"mock{type_name}()" if 'Repository' in type_name or 'Service' in type_name else "null"
    
    def _get_exception_trigger_value(self, param: MethodParameter) -> str:
        """Génère une valeur qui déclencherait une exception"""
        if param.is_primitive:
            if param.type in ['int', 'long']:
                return "-1" + ("L" if param.type == 'long' else "")
            elif param.type in ['double', 'float']:
                return "-1.0" + ("f" if param.type == 'float' else "")
            else:
                return self._get_valid_value(param)
        
        # Pour les objets, utiliser une valeur qui pourrait causer une exception
        return "null"
    
    def _estimate_coverage(self, method_suggestions: List[MethodSuggestions]) -> float:
        """
        Estime la couverture de test basée sur les suggestions.
        
        Args:
            method_suggestions: Liste des suggestions par méthode
        
        Returns:
            Estimation de couverture [0-1]
        """
        if not method_suggestions:
            return 0.0
        
        # Calculer un score basé sur le nombre et la diversité des suggestions
        total_score = 0.0
        for ms in method_suggestions:
            # Score de base : nombre de suggestions
            base_score = min(ms.total_count / 10.0, 1.0)
            
            # Bonus pour diversité de types
            types = set(s.type for s in ms.suggestions)
            diversity_bonus = len(types) * 0.1
            
            total_score += min(base_score + diversity_bonus, 1.0)
        
        return min(total_score / len(method_suggestions), 1.0)
    
    def _to_camel_case(self, name: str) -> str:
        """Convertit un nom en CamelCase pour les noms de test"""
        if not name:
            return name
        # Capitaliser la première lettre
        return name[0].upper() + name[1:] if len(name) > 1 else name.upper()


