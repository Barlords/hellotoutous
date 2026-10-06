# Hello Toutous — spécifications

Boutique d’accessoires canins confectionnés à la main par Blandine, à Paris. Cette itération couvre la direction artistique, la navigation, la page d’accueil, le pied de page, le formulaire de contact et le modèle de données. Le paiement Stripe, le guide des tailles, la galerie, la liste par catégorie et la fiche article arrivent dans une itération suivante.

Stack retenue lors du cadrage précédent : Django, pages HTML serveur, admin Django pour gérer les articles. Stripe Checkout sera branché au moment du tunnel de commande.

Les noms de tables, de champs et de code sont en anglais. Tous les textes visibles sur le site sont en français.

## Périmètre

Inclus :

- navbar fixe et panier (compteur)
- page d’accueil, sections 1 à 5
- formulaire de contact
- pied de page
- modèle de données catalogue, y compris variantes et option nœud
- admin Django pour créer et modifier les articles

Hors périmètre, routes prévues mais pages vides ou à venir :

- guide des tailles
- galerie
- liste d’articles par catégorie
- fiche article
- tunnel de paiement Stripe

## Direction artistique

| Rôle | Valeur |
| --- | --- |
| Bandeau, boutons | `#D46A54` |
| Fond | `#FEA674` |
| Seconde couleur du dégradé | `#FEBC97` |
| Titres | `#6C4F3E` |
| Texte courant | `#3F2A22` |
| Texte des boutons et du bandeau | blanc |

Le fond de page est un dégradé vertical, du haut vers le bas : `#FEA674` puis `#FEBC97`. `#FEBC97` est le même orange éclairci d’environ un quart vers le blanc.

`#6C4F3E` reste la couleur des titres. Sur `#FEA674`, elle est trop claire pour les petits textes : le texte courant utilise `#3F2A22`, un brun de la même famille, plus sombre.

Le libellé des boutons est blanc et en gras. Le terracotta `#D46A54` ne sert pas de couleur de texte sur le fond orange.

La barre de navigation a un fond `#FFF6F0`, pour rester lisible et distincte du dégradé quand elle est fixe.

Typographie, chargée depuis Google Fonts :

- titres : **Fraunces**. Serif douce, un peu irrégulière, qui évoque le fait main sans tomber dans une écriture script.
- texte courant, navigation, boutons, formulaire : **Source Sans 3**. Linéale simple, lisible à petite taille.

Référence visuelle du hero : photo pleine largeur, carte de marque centrée (fond blanc translucide, empreinte de patte, « HELLO TOUTOUS », « BOUTIQUE D'ACCESSOIRES POUR CHIENS »), fin liseré doré autour de la photo, bandeau terracotta en bas de la photo.

## Navigation

Barre fixe en haut de l’écran. Elle reste visible au scroll, au-dessus du contenu.

Liens, dans cet ordre :

1. Boutique
2. Notre histoire
3. Guide des tailles
4. Galerie
5. Contact

Cet ordre fait foi, Galerie comprise. La maquette, qui n’a pas Galerie et place les liens autrement, ne le remplace pas.

Le panier est aligné à droite. Il affiche le libellé « Panier » et le nombre d’articles, par exemple « Panier (1) ». Ce nombre est le total des quantités des lignes du panier. L’option « avec nœud » ne crée pas une ligne de plus : elle change seulement le prix de la ligne. Le compteur se met à jour à chaque ajout, retrait ou changement de quantité.

Cette itération n’a pas encore de bouton « ajouter au panier » (la fiche article est reportée). Le compteur existe, part de 0, et le mécanisme de session est en place pour les itérations suivantes.

Destinations :

| Lien | Destination |
| --- | --- |
| Boutique | liste des catégories, page à venir |
| Notre histoire | ancre `notre-histoire` sur l’accueil |
| Guide des tailles | page à venir |
| Galerie | page à venir |
| Contact | ancre `contact` sur l’accueil |
| Panier | page panier, vide tant que la fiche article n’existe pas |

Depuis une autre page, « Notre histoire » et « Contact » ramènent à l’accueil sur l’ancre correspondante.

## Page d’accueil

Les sections se succèdent verticalement, dans l’ordre ci-dessous. Sur un écran étroit, les blocs côte à côte passent l’un sous l’autre : le texte d’abord, le visuel ensuite.

### Section 1 — marque

Photo pleine largeur. Au centre, un encart de marque :

- empreinte de patte
- HELLO TOUTOUS
- BOUTIQUE D'ACCESSOIRES POUR CHIENS

La photo et le logo définitifs ne sont pas fournis : un placeholder occupe la zone en attendant les fichiers.

Sous la photo, un bandeau `#D46A54` fait défiler les deux phrases ensemble, de droite à gauche, en boucle continue :

- Délais de fabrication 2 à 4 semaines
- Livraison offerte à partir de 150€ d'achat

Les deux textes se suivent sur la même ligne et réapparaissent sans trou. Le texte est blanc. Si le visiteur a demandé à réduire les animations, le défilement s’arrête et les deux phrases restent lisibles.

### Section 2 — texte accrocheur

Colonne gauche, texte exact :

> HELLO TOUTOUS vous propose des accessoires canins entièrement confectionnés à la main prêts à vous accompagner dans toutes vos aventures. Optez pour le style et le savoir-faire français.
> Nos colliers, laisses, harnais et autres accessoires n'attendent que vous !

Colonne droite : carrousel de photos de produits portés par des chiens.

- défilement automatique
- pause tant que le pointeur survole une photo
- boutons flèche précédent et suivant pour défiler à la main
- les photos sont des placeholders tant que les visuels ne sont pas fournis

### Section 3 — accessoires

Liste des catégories, dans l’ordre du référentiel :

- Colliers
- Harnais
- Laisses
- Bandanas
- Distributeurs de sacs
- Sac à friandises
- Noeuds

Chaque catégorie pointera vers sa page liste (à venir). Sous la liste, deux textes sur la même ligne :

**Livraison dans le monde**

HELLO TOUTOUS vous livre dans le monde entier. Les délais de confection sont actuellement de 2 à 4 semaines. La livraison est offerte dès 150€ d'achat en France métropolitaine !

**Qualité & originalité**

Les créations HELLO TOUTOUS sont exclusives. J'apporte un soin particulier aux finitions. Chaque modèle est unique et créé uniquement pour vous, à votre demande.

### Section 4 — notre histoire

Ancre : `notre-histoire`.

Titre : QUI SE CACHE DERRIERE HELLO TOUTOUS ?

Colonne gauche :

> C’est moi, Blandine
> Passionnée de couture et ancienne maroquinière,
> j’ai créé HELLO TOUTOUS avec l’envie de mettre mon savoir-faire au service de nos compagnons à quatre pattes.
> Chaque accessoire est imaginé, confectionné et personnalisé à la main dans mon atelier parisien.

Colonne droite : photo de Blandine dans son atelier. Placeholder tant que la photo n’est pas fournie.

### Section 5 — contact

Ancre : `contact`.

> A votre écoute
> J'accorde beaucoup d'importance à votre confort et à votre tranquillité. N'hésitez pas à me contacter si vous avez la moindre question et je vous répondrai rapidement par mail, telephone ainsi que sur Instagram.

Le formulaire vient sous ce texte.

Titre du formulaire : Envie d'un accessoire sur-mesure ? Contacte-moi !

Champs :

| Champ | Obligatoire | Contrainte |
| --- | --- | --- |
| Nom | oui | texte |
| Courriel | oui | adresse e-mail valide |
| Ville | oui | texte |
| Catégorie du message | oui | Demande sur mesure, Avis client, Autre |
| Message | oui | texte long |

Après un envoi valide, les champs sont vidés et un message de confirmation s’affiche en français. Les erreurs de saisie s’affichent à côté des champs, en français. Un message n’est pas enregistré ni renvoyé deux fois si la personne recharge la page après le succès.

Chaque envoi est enregistré en base (table `contact_message`) et un e-mail est envoyé à `hellotoutous@hotmail.com`.

L’adresse Instagram arrivera dans une prochaine itération. En attendant, la phrase reste affichée, sans lien.

## Pied de page

Présent sur toutes les pages.

- titre : Me contacter
- téléphone : 06 46 56 54 20 (lien d’appel `+33646565420`)
- e-mail : hellotoutous@hotmail.com
- mention : © Company 2026

## Pages reportées

Ces routes existent pour que la navigation ne mène pas à une 404, avec un contenu minimal « à venir » :

- `/guide-des-tailles`
- `/galerie`
- `/boutique`
- `/boutique/<category-slug>`
- `/boutique/<category-slug>/<product-slug>`
- `/panier`

Aucun contenu métier n’est spécifié pour ces pages dans cette itération. Les règles du panier ci-dessous s’appliqueront quand la fiche article permettra d’ajouter un article.

## Modèle de données

Tables en anglais. Libellés français uniquement à l’affichage et dans l’admin.

Un article est un modèle. Il a plusieurs tailles et plusieurs couleurs, portées par des variantes. Le prix de base est celui du modèle. L’option « avec nœud » n’existe que pour les colliers et les harnais : elle n’ajoute pas d’article au panier, elle ajoute au prix de la ligne le supplément fixé par l’admin.

### `category`

Référentiel fixe de cette itération.

| code | libellé affiché |
| --- | --- |
| `collar` | Colliers |
| `harness` | Harnais |
| `leash` | Laisses |
| `bandana` | Bandanas |
| `bag_dispenser` | Distributeurs de sacs |
| `treat_pouch` | Sac à friandises |
| `bow` | Noeuds |

### `size`

| code | libellé affiché |
| --- | --- |
| `S` | S |
| `M` | M |
| `L` | L |
| `XL` | XL |

### `color`

Table prévue, aucune valeur pour l’instant. Champs minimaux : `code` (anglais), `label` (français affiché).

### `product`

Le modèle. Il n’a pas une seule taille ni une seule couleur.

| Champ | Type | Description |
| --- | --- | --- |
| `name` | texte | nom affiché |
| `slug` | texte unique | segment d’URL |
| `description` | texte | peut être vide |
| `category` | clé étrangère vers `category` | obligatoire |
| `base_price` | décimal | prix de base, en euros |
| `offers_knot` | booléen | autorise l’option « avec nœud » |
| `knot_price` | décimal, nullable | supplément en euros ajouté au prix quand l’option est cochée |
| `is_active` | booléen | visible sur la boutique seulement si vrai |

Règles :

- `offers_knot` ne peut être vrai que si la catégorie est `collar` ou `harness`.
- Si `offers_knot` est vrai, `knot_price` est obligatoire et strictement supérieur à 0.
- Pour toute autre catégorie, `offers_knot` est faux et `knot_price` est vide.

### `product_variant`

Une combinaison taille + couleur d’un modèle.

| Champ | Type | Description |
| --- | --- | --- |
| `product` | clé étrangère vers `product` | obligatoire |
| `size` | clé étrangère vers `size` | obligatoire |
| `color` | clé étrangère vers `color` | obligatoire dès que des couleurs existent |

Un même modèle ne peut pas avoir deux variantes avec la même taille et la même couleur.

Les images produit ne sont pas dans ce modèle : le carrousel de l’accueil utilise des placeholders. Le stockage des photos sera spécifié avec la fiche article.

### Option « avec nœud »

Disponible seulement pour un collier ou un harnais dont `offers_knot` est vrai.

Cocher l’option ne met pas un nœud dans le panier. La ligne reste l’article choisi (taille + couleur). Son prix unitaire devient `base_price` + `knot_price`. Le supplément `knot_price` est saisi dans l’admin, sur le modèle.

Le prix affiché « avec nœud » est donc `base_price` + `knot_price`. Sans l’option, le prix reste `base_price`.

La catégorie Noeuds reste un type d’article à part, avec son propre prix de base. Elle n’est pas liée à cette option.

### `contact_message`

| Champ | Type |
| --- | --- |
| `name` | texte |
| `email` | texte |
| `city` | texte |
| `category` | `custom_order`, `customer_review`, `other` |
| `message` | texte |
| `created_at` | date et heure |

Libellés affichés des catégories de message : Demande sur mesure, Avis client, Autre.

### Admin

L’admin Django permet de créer, modifier et désactiver un produit, de gérer ses variantes, de saisir le supplément « avec nœud », et de consulter les messages de contact. Les référentiels catégorie et taille sont préchargés. Les couleurs s’ajouteront quand la liste sera fournie. L’admin refuse un `offers_knot` hors collier et harnais, et un supplément manquant ou nul quand l’option est activée.
