"""
Exemple d'utilisation de CriticalityService

Ce fichier montre comment intégrer CriticalityService avec EffortCalculator.
"""
from src.services.effort_calculator import EffortCalculator
from src.services.criticality_service import CriticalityService

# Exemple d'utilisation complète
def example_usage():
    """Exemple d'utilisation du service de criticité"""
    
    # Initialiser les services
    effort_calculator = EffortCalculator()
    criticality_service = CriticalityService()
    
    # Exemple de prédictions du service ML (S5)
    predictions = [
        {
            'class_name': 'com.example.auth.UserService',
            'risk_score': 0.75,
            'loc': 150,
            'cyclomatic_complexity': 12
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
        },
        {
            'class_name': 'com.example.database.UserRepository',
            'risk_score': 0.60,
            'loc': 100,
            'cyclomatic_complexity': 8
        }
    ]
    
    # Étape 1: Calculer l'effort et les scores effort-aware
    classes_with_effort = effort_calculator.calculate_for_classes(predictions)
    
    # Étape 2: Appliquer la criticité
    classes_with_criticality = criticality_service.enrich_with_criticality(
        classes_with_effort
    )
    
    # Afficher les résultats
    print("=" * 80)
    print("Résultats avec criticité")
    print("=" * 80)
    
    for cls in classes_with_criticality:
        print(f"\nClasse: {cls['class_name']}")
        print(f"  Risk Score: {cls['risk_score']}")
        print(f"  LOC: {cls['loc']}")
        print(f"  Complexité: {cls['cyclomatic_complexity']}")
        print(f"  Effort (heures): {cls['effort_hours']}")
        print(f"  Effort-Aware Score (base): {cls.get('effort_aware_score', 'N/A')}")
        print(f"  Module Criticité: {cls['module_criticality']}")
        print(f"  Effort-Aware Score (ajusté): {cls['effort_aware_score']}")
    
    # Statistiques
    stats = criticality_service.get_criticality_stats(classes_with_criticality)
    print("\n" + "=" * 80)
    print("Statistiques de criticité")
    print("=" * 80)
    print(f"Total: {stats['total']}")
    print(f"High: {stats['high']} ({stats['high_percent']}%)")
    print(f"Medium: {stats['medium']} ({stats['medium_percent']}%)")
    print(f"Low: {stats['low']} ({stats['low_percent']}%)")
    
    # Trier par score effort-aware ajusté
    sorted_classes = sorted(
        classes_with_criticality,
        key=lambda x: x['effort_aware_score'],
        reverse=True
    )
    
    print("\n" + "=" * 80)
    print("Classes triées par score effort-aware (avec criticité)")
    print("=" * 80)
    for idx, cls in enumerate(sorted_classes, start=1):
        print(f"{idx}. {cls['class_name']} - Score: {cls['effort_aware_score']} "
              f"({cls['module_criticality']})")

if __name__ == "__main__":
    example_usage()

