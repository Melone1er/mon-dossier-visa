# Mon Dossier Visa

Application web gratuite pour préparer un voyage à l'étranger :

- vérifier s'il faut un visa entre 199 nationalités et 199 destinations ;
- suivre les démarches pas à pas, avec la liste des papiers et où les obtenir ;
- trouver l'ambassade ou le consulat compétent, parmi 10 000 représentations dans le monde ;
- comparer les vols depuis l'aéroport le plus proche ;
- une fois arrivé, retrouver l'ambassade de son pays, les démarches d'arrivée et les numéros d'urgence ;
- installer le site comme une application sur son téléphone, utilisable hors connexion.

## Mettre le site en ligne (GitHub Pages)

1. Crée un compte sur github.com.
2. Crée un dépôt **public** nommé `mon-dossier-visa`. Avec un compte gratuit, GitHub Pages ne fonctionne qu'avec un dépôt public.
3. Envoie tous les fichiers de ce dossier dans le dépôt, en gardant les sous-dossiers (`data`, `icons`, `scripts`, `.github`). Le plus simple : ouvre le dépôt, appuie sur la touche `.` pour ouvrir l'éditeur web, glisse-dépose le dossier entier, puis valide.
4. Va dans **Settings → Pages**. Sous « Build and deployment », choisis **Deploy from a branch**, branche `main`, dossier `/ (root)`. Enregistre.
5. Va dans **Settings → Actions → General**, section « Workflow permissions », coche **Read and write permissions** et enregistre. C'est ce qui permet la mise à jour automatique des données.
6. Le site est en ligne après une à deux minutes à l'adresse `https://TON-NOM.github.io/mon-dossier-visa/`.

Avant d'annoncer le site, complète les champs surlignés dans `mentions-legales.html` et `confidentialite.html` (nom de l'éditeur, adresse, e-mail).

Pour un nom de domaine à toi : achète-le chez un registraire, ajoute-le dans **Settings → Pages → Custom domain**, puis coche **Enforce HTTPS**.

## Mise à jour automatique des données

Le fichier `.github/workflows/update-data.yml` relance chaque lundi le script `scripts/build_data.py`. Le script télécharge les dernières versions des bases ouvertes, vérifie qu'elles sont complètes, puis met à jour le dossier `data`. Si rien n'a changé, rien n'est publié.

Pour lancer une mise à jour tout de suite : onglet **Actions → Mise à jour des données → Run workflow**.

À la main, sur un ordinateur avec Python :

```
pip install pycountry
git clone --depth 1 https://github.com/imorte/passport-index-data.git /tmp/visa
git clone --depth 1 https://github.com/database-of-embassies/database-of-embassies.git /tmp/embassies
git clone --depth 1 https://github.com/davidmegginson/ourairports-data.git /tmp/airports
python scripts/build_data.py --visa /tmp/visa --embassies /tmp/embassies --airports /tmp/airports --out data
```

## Ce qui n'est pas mis à jour automatiquement

Certaines informations ont été vérifiées à la main le 8 octobre 2026 et se trouvent dans `index.html` :

- l'exemption de visa du Togo pour les ressortissants africains (depuis le 18 mai 2026) ;
- les restrictions américaines par nationalité (proclamations de juin et décembre 2025) ;
- les guides détaillés Togo vers France, Allemagne, États-Unis, Canada et Chine ;
- les adresses vérifiées des ambassades à Lomé et des ambassades du Togo à Paris, Berlin, Londres, Bruxelles et Pékin.

Relis-les une fois par mois. `data/emergency.json` (numéros d'urgence) et `data/countries.geo.json` (frontières, pour le GPS) changent rarement et sont à mettre à jour à la main.

## Contenu du dossier

| Fichier | Rôle |
| --- | --- |
| `index.html` | L'application |
| `data/*.json` | Données : visas, ambassades, aéroports, fuseaux horaires, urgences, frontières |
| `sw.js`, `manifest.webmanifest`, `icons/` | Installation sur téléphone et fonctionnement hors connexion |
| `mentions-legales.html`, `confidentialite.html` | Pages légales |
| `scripts/build_data.py` | Reconstruction des données |
| `.github/workflows/update-data.yml` | Mise à jour automatique chaque semaine |

## Ce qui ne fonctionne qu'à l'intérieur de Claude

L'assistant intégré utilise Claude : sur le site public, son panneau se masque automatiquement. À l'inverse, le bouton GPS n'apparaît que sur le site public, car la localisation est bloquée dans Claude.

## Sources et licences

| Données | Source | Licence |
| --- | --- | --- |
| Exigences de visa | [Passport Index Data](https://github.com/imorte/passport-index-data) | MIT |
| Ambassades et consulats | [Database of Embassies](https://github.com/database-of-embassies/database-of-embassies) (Wikidata) | Domaine public |
| Aéroports | [OurAirports](https://github.com/davidmegginson/ourairports-data) | Domaine public |
| Numéros d'urgence | Wikipédia, via le paquet emergency-numbers | MIT |
| Frontières des pays | [world.geo.json](https://github.com/johan/world.geo.json) (Natural Earth) | Domaine public |
| Fuseaux horaires | Base IANA (tzdata) | Domaine public |

## Limites d'usage de GitHub Pages

GitHub Pages convient à ce site d'information. GitHub interdit de l'utiliser pour faire tourner une activité commerciale, un site de vente en ligne ou un service payant, et pour traiter des données sensibles comme des mots de passe ou des numéros de carte. Pour vendre des billets ou des services, il faudra un hébergeur classique avec un serveur.
