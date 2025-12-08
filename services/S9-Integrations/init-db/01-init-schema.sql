-- Script d'initialisation de la base de données PostgreSQL
-- Ce script est exécuté automatiquement lors du premier démarrage du conteneur

-- Créer le schéma si non existant
CREATE SCHEMA IF NOT EXISTS public;

-- Extension pour UUID si nécessaire
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Configurer les paramètres de la base
ALTER DATABASE cicd_integration SET timezone TO 'UTC';

-- Message de confirmation
DO $$
BEGIN
    RAISE NOTICE 'Base de données cicd_integration initialisée avec succès!';
END $$;

