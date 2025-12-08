"""
Service d'analyse AST pour extraire les informations des classes Java

MTP-S7-01: Analyse AST pour génération
- Parse le code Java avec un parser basique (regex)
- Extrait méthodes, constructeurs, champs, dépendances
- Identifie les annotations et modificateurs

Note: Pour une analyse AST complète, on peut utiliser tree-sitter-java
après compilation des bindings. Pour l'instant, on utilise un parser basique
qui fonctionne bien pour la plupart des cas.
"""
from typing import Optional, List, Dict
import re

# Charger le langage Java pour tree-sitter (optionnel)
# Pour utiliser tree-sitter-java, il faut :
# 1. Installer tree-sitter et compiler tree-sitter-java
# 2. Charger le langage :
#    try:
#        from tree_sitter import Language, Parser
#        JAVA_LANGUAGE = Language('build/my-languages.so', 'java')
#    except:
#        JAVA_LANGUAGE = None
JAVA_LANGUAGE = None


class ASTAnalyzer:
    """
    Analyseur AST pour extraire les informations des classes Java.
    
    Utilise tree-sitter-java pour parser le code et extraire :
    - Méthodes publiques et leurs signatures
    - Constructeurs
    - Champs et dépendances
    - Imports et annotations
    """
    
    def __init__(self):
        """Initialise l'analyseur AST"""
        self.parser = None
        # Si tree-sitter est disponible, l'utiliser
        if JAVA_LANGUAGE:
            try:
                from tree_sitter import Parser
                self.parser = Parser(JAVA_LANGUAGE)
            except ImportError:
                self.parser = None
    
    def analyze_class(self, java_code: str, file_path: Optional[str] = None) -> Optional[Dict]:
        """
        Analyse une classe Java et retourne ses informations.
        
        Args:
            java_code: Code source Java (contenu du fichier)
            file_path: Chemin du fichier (optionnel, pour extraire le package)
        
        Returns:
            Dict contenant les informations de la classe ou None si erreur
        """
        if not self.parser:
            # Fallback: parser basique sans tree-sitter
            return self._parse_basic(java_code, file_path)
        
        try:
            tree = self.parser.parse(bytes(java_code, 'utf8'))
            root_node = tree.root_node
            
            # Extraire les informations
            result = {
                'class_name': self._extract_class_name(root_node),
                'package_name': self._extract_package(root_node),
                'full_qualified_name': '',
                'is_abstract': False,
                'is_interface': False,
                'is_enum': False,
                'extends': None,
                'implements': [],
                'methods': [],
                'constructors': [],
                'fields': [],
                'imports': [],
                'annotations': [],
                'dependencies': []
            }
            
            # Extraire les informations détaillées
            result['methods'] = self._extract_methods(root_node)
            result['constructors'] = self._extract_constructors(root_node)
            result['fields'] = self._extract_fields(root_node)
            result['imports'] = self._extract_imports(root_node)
            result['annotations'] = self._extract_class_annotations(root_node)
            result['dependencies'] = self._extract_dependencies(root_node, result['imports'])
            
            # Construire le nom qualifié complet
            if result['package_name']:
                result['full_qualified_name'] = f"{result['package_name']}.{result['class_name']}"
            else:
                result['full_qualified_name'] = result['class_name']
            
            return result
            
        except Exception as e:
            # En cas d'erreur, utiliser le parser basique
            return self._parse_basic(java_code, file_path)
    
    def _extract_class_name(self, root_node) -> str:
        """Extrait le nom de la classe"""
        for child in root_node.children:
            if child.type == 'class_declaration':
                for node in child.children:
                    if node.type == 'identifier':
                        return node.text.decode('utf8')
            elif child.type == 'interface_declaration':
                for node in child.children:
                    if node.type == 'identifier':
                        return node.text.decode('utf8')
        return "UnknownClass"
    
    def _extract_package(self, root_node) -> Optional[str]:
        """Extrait le nom du package"""
        for child in root_node.children:
            if child.type == 'package_declaration':
                parts = []
                for node in child.children:
                    if node.type == 'scoped_identifier' or node.type == 'identifier':
                        parts.append(node.text.decode('utf8'))
                return '.'.join(parts) if parts else None
        return None
    
    def _extract_methods(self, root_node) -> List[Dict]:
        """Extrait les méthodes de la classe"""
        methods = []
        for child in root_node.children:
            if child.type in ['class_declaration', 'interface_declaration']:
                for node in child.children:
                    if node.type == 'method_declaration':
                        method_info = self._parse_method(node)
                        if method_info:
                            methods.append(method_info)
        return methods
    
    def _extract_constructors(self, root_node) -> List[Dict]:
        """Extrait les constructeurs"""
        constructors = []
        for child in root_node.children:
            if child.type == 'class_declaration':
                for node in child.children:
                    if node.type == 'constructor_declaration':
                        constructor_info = self._parse_constructor(node)
                        if constructor_info:
                            constructors.append(constructor_info)
        return constructors
    
    def _extract_fields(self, root_node) -> List[Dict]:
        """Extrait les champs de la classe"""
        fields = []
        for child in root_node.children:
            if child.type == 'class_declaration':
                for node in child.children:
                    if node.type == 'field_declaration':
                        field_info = self._parse_field(node)
                        fields.extend(field_info)
        return fields
    
    def _extract_imports(self, root_node) -> List[str]:
        """Extrait les imports"""
        imports = []
        for child in root_node.children:
            if child.type == 'import_declaration':
                for node in child.children:
                    if node.type in ['scoped_identifier', 'identifier']:
                        imports.append(node.text.decode('utf8'))
        return imports
    
    def _extract_class_annotations(self, root_node) -> List[str]:
        """Extrait les annotations de classe"""
        annotations = []
        for child in root_node.children:
            if child.type in ['class_declaration', 'interface_declaration']:
                for node in child.children:
                    if node.type == 'modifiers':
                        for mod in node.children:
                            if mod.type == 'marker_annotation' or mod.type == 'annotation':
                                annotations.append(mod.text.decode('utf8'))
        return annotations
    
    def _extract_dependencies(self, root_node, imports: List[str]) -> List[str]:
        """Extrait les dépendances (types utilisés)"""
        dependencies = set()
        # Ajouter les imports comme dépendances
        for imp in imports:
            # Extraire le nom de classe depuis l'import
            parts = imp.split('.')
            if parts:
                dependencies.add(parts[-1])
        
        # Extraire les types utilisés dans les champs et méthodes
        # (simplifié pour l'instant)
        return list(dependencies)
    
    def _parse_method(self, node) -> Optional[Dict]:
        """Parse une déclaration de méthode"""
        method_info = {
            'name': '',
            'return_type': None,
            'parameters': [],
            'is_public': False,
            'is_static': False,
            'is_void': False,
            'throws_exceptions': [],
            'annotations': []
        }
        
        for child in node.children:
            if child.type == 'identifier':
                method_info['name'] = child.text.decode('utf8')
            elif child.type == 'modifiers':
                modifiers = child.text.decode('utf8')
                method_info['is_public'] = 'public' in modifiers
                method_info['is_static'] = 'static' in modifiers
            elif child.type == 'type':
                return_type = child.text.decode('utf8')
                method_info['return_type'] = return_type
                method_info['is_void'] = return_type == 'void'
            elif child.type == 'formal_parameters':
                method_info['parameters'] = self._parse_parameters(child)
            elif child.type == 'throws':
                method_info['throws_exceptions'] = self._parse_throws(child)
            elif child.type in ['marker_annotation', 'annotation']:
                method_info['annotations'].append(child.text.decode('utf8'))
        
        return method_info if method_info['name'] else None
    
    def _parse_constructor(self, node) -> Optional[Dict]:
        """Parse une déclaration de constructeur"""
        constructor_info = {
            'parameters': [],
            'is_public': True,
            'annotations': []
        }
        
        for child in node.children:
            if child.type == 'modifiers':
                modifiers = child.text.decode('utf8')
                constructor_info['is_public'] = 'public' in modifiers
            elif child.type == 'formal_parameters':
                constructor_info['parameters'] = self._parse_parameters(child)
            elif child.type in ['marker_annotation', 'annotation']:
                constructor_info['annotations'].append(child.text.decode('utf8'))
        
        return constructor_info
    
    def _parse_field(self, node) -> List[Dict]:
        """Parse une déclaration de champ"""
        fields = []
        field_type = None
        modifiers_text = ''
        annotations = []
        
        for child in node.children:
            if child.type == 'modifiers':
                modifiers_text = child.text.decode('utf8')
                for mod in child.children:
                    if mod.type in ['marker_annotation', 'annotation']:
                        annotations.append(mod.text.decode('utf8'))
            elif child.type == 'type':
                field_type = child.text.decode('utf8')
            elif child.type == 'variable_declarator_list':
                for var in child.children:
                    if var.type == 'variable_declarator':
                        var_name = ''
                        for v_child in var.children:
                            if v_child.type == 'identifier':
                                var_name = v_child.text.decode('utf8')
                                break
                        if var_name:
                            fields.append({
                                'name': var_name,
                                'type': field_type or 'Object',
                                'is_public': 'public' in modifiers_text,
                                'is_private': 'private' in modifiers_text,
                                'is_final': 'final' in modifiers_text,
                                'is_static': 'static' in modifiers_text,
                                'annotations': annotations.copy()
                            })
        
        return fields
    
    def _parse_parameters(self, node) -> List[Dict]:
        """Parse les paramètres formels"""
        parameters = []
        for child in node.children:
            if child.type == 'formal_parameter':
                param_info = {'name': '', 'type': 'Object', 'is_primitive': False, 'is_collection': False}
                for p_child in child.children:
                    if p_child.type == 'identifier':
                        param_info['name'] = p_child.text.decode('utf8')
                    elif p_child.type == 'type':
                        param_type = p_child.text.decode('utf8')
                        param_info['type'] = param_type
                        param_info['is_primitive'] = param_type in ['int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short']
                        param_info['is_collection'] = 'List' in param_type or 'Set' in param_type or 'Map' in param_type
                if param_info['name']:
                    parameters.append(param_info)
        return parameters
    
    def _parse_throws(self, node) -> List[str]:
        """Parse les exceptions lancées"""
        exceptions = []
        for child in node.children:
            if child.type == 'type_list':
                for type_node in child.children:
                    if type_node.type in ['scoped_identifier', 'identifier']:
                        exceptions.append(type_node.text.decode('utf8'))
        return exceptions
    
    def _parse_basic(self, java_code: str, file_path: Optional[str] = None) -> Dict:
        """
        Parser basique sans tree-sitter (fallback).
        Extrait les informations de base avec des expressions régulières.
        """
        result = {
            'class_name': 'UnknownClass',
            'package_name': None,
            'full_qualified_name': 'UnknownClass',
            'is_abstract': False,
            'is_interface': False,
            'is_enum': False,
            'extends': None,
            'implements': [],
            'methods': [],
            'constructors': [],
            'fields': [],
            'imports': [],
            'annotations': [],
            'dependencies': []
        }
        
        # Extraire le package
        package_match = re.search(r'package\s+([\w.]+);', java_code)
        if package_match:
            result['package_name'] = package_match.group(1)
        
        # Extraire le nom de classe et ses modificateurs
        class_match = re.search(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(?:class|interface|enum)\s+(\w+)', java_code)
        if class_match:
            result['class_name'] = class_match.group(1)
            class_decl = java_code[:class_match.end()]
            result['is_abstract'] = 'abstract' in class_decl
            result['is_interface'] = 'interface' in class_decl
            result['is_enum'] = 'enum' in class_decl
        
        # Extraire les imports
        import_matches = re.findall(r'import\s+(?:static\s+)?([\w.*]+);', java_code)
        result['imports'] = import_matches
        
        # Extraire les annotations de classe
        class_annotations = re.findall(r'@(\w+)(?:\([^)]*\))?', java_code.split('class')[0] if 'class' in java_code else '')
        result['annotations'] = [f'@{ann}' for ann in class_annotations]
        
        # Extraire les méthodes publiques avec plus de détails
        method_pattern = r'(?:@\w+(?:\([^)]*\))?\s+)*(?:public\s+)?(?:private\s+)?(?:protected\s+)?(?:static\s+)?(?:final\s+)?(?:[\w<>,\s\[\]]+\s+)?(\w+)\s*\(([^)]*)\)\s*(?:throws\s+([\w\s,]+))?\s*\{'
        method_matches = re.finditer(method_pattern, java_code)
        for match in method_matches:
            method_name = match.group(1)
            params_str = match.group(2) if match.group(2) else ''
            throws_str = match.group(3) if match.group(3) else ''
            
            # Éviter les mots-clés et les constructeurs (seront traités séparément)
            if method_name not in ['if', 'for', 'while', 'switch', 'catch', 'try'] and method_name != result['class_name']:
                # Extraire le type de retour (avant le nom de méthode)
                method_start = match.start()
                before_method = java_code[max(0, method_start-50):method_start]
                return_type_match = re.search(r'([\w<>,\s\[\]]+)\s+' + re.escape(method_name), before_method)
                return_type = return_type_match.group(1).strip() if return_type_match else None
                
                # Parser les paramètres
                parameters = []
                if params_str.strip():
                    param_parts = [p.strip() for p in params_str.split(',')]
                    for param in param_parts:
                        param_match = re.match(r'([\w<>,\s\[\]]+)\s+(\w+)', param)
                        if param_match:
                            param_type = param_match.group(1).strip()
                            param_name = param_match.group(2).strip()
                            parameters.append({
                                'name': param_name,
                                'type': param_type,
                                'is_primitive': param_type in ['int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short', 'void'],
                                'is_collection': 'List' in param_type or 'Set' in param_type or 'Map' in param_type or 'Collection' in param_type
                            })
                
                # Parser les exceptions
                exceptions = [e.strip() for e in throws_str.split(',')] if throws_str else []
                
                # Extraire les annotations
                method_annotations = re.findall(r'@(\w+)(?:\([^)]*\))?', before_method)
                
                result['methods'].append({
                    'name': method_name,
                    'return_type': return_type,
                    'parameters': parameters,
                    'is_public': 'public' in before_method,
                    'is_static': 'static' in before_method,
                    'is_void': return_type == 'void' if return_type else False,
                    'throws_exceptions': exceptions,
                    'annotations': [f'@{ann}' for ann in method_annotations]
                })
        
        # Extraire les constructeurs
        constructor_pattern = r'(?:@\w+(?:\([^)]*\))?\s+)*(?:public\s+)?(?:private\s+)?(?:protected\s+)?' + re.escape(result['class_name']) + r'\s*\(([^)]*)\)\s*\{'
        constructor_matches = re.finditer(constructor_pattern, java_code)
        for match in constructor_matches:
            params_str = match.group(1) if match.group(1) else ''
            constructor_start = match.start()
            before_constructor = java_code[max(0, constructor_start-50):constructor_start]
            
            parameters = []
            if params_str.strip():
                param_parts = [p.strip() for p in params_str.split(',')]
                for param in param_parts:
                    param_match = re.match(r'([\w<>,\s\[\]]+)\s+(\w+)', param)
                    if param_match:
                        param_type = param_match.group(1).strip()
                        param_name = param_match.group(2).strip()
                        parameters.append({
                            'name': param_name,
                            'type': param_type,
                            'is_primitive': param_type in ['int', 'long', 'double', 'float', 'boolean', 'char', 'byte', 'short'],
                            'is_collection': False
                        })
            
            constructor_annotations = re.findall(r'@(\w+)(?:\([^)]*\))?', before_constructor)
            
            result['constructors'].append({
                'parameters': parameters,
                'is_public': 'public' in before_constructor,
                'annotations': [f'@{ann}' for ann in constructor_annotations]
            })
        
        # Extraire les champs
        field_pattern = r'(?:@\w+(?:\([^)]*\))?\s+)*(?:public\s+)?(?:private\s+)?(?:protected\s+)?(?:static\s+)?(?:final\s+)?([\w<>,\s\[\]]+)\s+(\w+)(?:\s*=\s*[^;]+)?;'
        field_matches = re.finditer(field_pattern, java_code)
        for match in field_matches:
            field_type = match.group(1).strip()
            field_name = match.group(2).strip()
            field_start = match.start()
            before_field = java_code[max(0, field_start-50):field_start]
            
            field_annotations = re.findall(r'@(\w+)(?:\([^)]*\))?', before_field)
            
            result['fields'].append({
                'name': field_name,
                'type': field_type,
                'is_public': 'public' in before_field,
                'is_private': 'private' in before_field or ('public' not in before_field and 'protected' not in before_field),
                'is_final': 'final' in before_field,
                'is_static': 'static' in before_field,
                'annotations': [f'@{ann}' for ann in field_annotations]
            })
        
        # Extraire les dépendances depuis les imports
        for imp in result['imports']:
            if '*' not in imp:
                parts = imp.split('.')
                if parts:
                    result['dependencies'].append(parts[-1])
        
        # Construire le nom qualifié complet
        if result['package_name']:
            result['full_qualified_name'] = f"{result['package_name']}.{result['class_name']}"
        else:
            result['full_qualified_name'] = result['class_name']
        
        return result

