# OCR Project 
Prochaines étapes

Créer une interface web simple pour :

Téléverser un PDF/image

Voir OCR et JSON structuré

Rechercher des informations dans les documents

Optimiser le moteur de recherche :

Ajouter filtrage par type de document, date, montant

Recherche full-text sur toutes les pages

Étendre à d’autres types de documents : contrats, bons de commande, certificats.


⚡ Fonctionnalités réalisées
1️⃣ Automatisation de traitement des factures

Détection automatique du type de fichier : PDF ou image.

Conversion en base64 pour traitement local (pas besoin d’URL publique).

Extraction OCR avec Mistral.

Sauvegarde automatique du JSON OCR.

Affichage du texte page par page pour vérification.

2️⃣ Structuration intelligente des données

Analyse du texte OCR en Markdown.

Utilisation d’un prompt LLM Mistral pour générer un JSON strictement valide.

Gestion des champs manquants : null ou listes vides.

Sauvegarde du JSON structuré pour chaque document.

3️⃣ Indexation & recherche (prototype)

Lecture des JSON OCR et JSON structurés.

Génération d’un JSON combiné (full_text) pour recherche.

Prototype d’un moteur de recherche simple basé sur les mots-clés dans full_text.

Possibilité de filtrer par type de document, date, montant, etc.

Base pour créer un moteur de recherche plus avancé ou une interface client.