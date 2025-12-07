"""
Exemple d'utilisation de EffortCalculator dans l'API

Ce fichier montre comment intégrer EffortCalculator dans l'endpoint de priorisation.
Il sera intégré dans prioritization.py lors de l'implémentation complète.
"""
from src.services.effort_calculator import EffortCalculator

# Exemple d'utilisation
def example_usage():
    """Exemple d'utilisation du calculateur d'effort"""
    
    # Initialiser le calculateur
    calculator = EffortCalculator()
    
    # Exemple de prédictions du service ML (S5)
    predictions = [
        {
            'class_name': 'com.example.auth.UserService',
            'risk_score': 0.75,
            'loc': 150,
            'cyclomatic_complexity': 12,
            'num_methods': 8,
            'num_dependencies': 3
        },
        {
            'class_name': 'com.example.payment.PaymentService',
            'risk_score': 0.68,
            'loc': 200,
            'cyclomatic_complexity': 15
        },
        {
            'class_name': 'com.example.utils.StringHelper',
            'risk_score': 0.45,
            'loc': 50,
            'cyclomatic_complexity': 3
        }
    ]
    
    # Calculer effort et scores effort-aware
    enriched_predictions = calculator.calculate_for_classes(predictions)
    
    # Afficher les résultats
    for pred in enriched_predictions:
        print(f"Classe: {pred['class_name']}")
        print(f"  Risk Score: {pred['risk_score']}")
        print(f"  LOC: {pred['loc']}")
        print(f"  Complexité: {pred['cyclomatic_complexity']}")
        print(f"  Effort (heures): {pred['effort_hours']}")
        print(f"  Effort-Aware Score: {pred['effort_aware_score']}")
        print()

if __name__ == "__main__":
    example_usage()


