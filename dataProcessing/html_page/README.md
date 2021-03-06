# Comment gérer la partie html / js / css 

## HTML



Le fichier [template.html](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/dataProcessing/html_page/template.html) contient le squelette de la page:
Chaque balise `{...}` sera replit par du texte via le scripte python.

Par exemple:
```html
<title>{name}</title>
<style type="text/css">{css}</style>
```
Dans ce code {name} sera remplacé par le nom du fichier de vol
et {css} sera remplacé par la totalité du code css.

L'ajout de la partie JavaScripte est en deux partie:

```html
<script>
  var phases          = {phases};
  var stats           = {stats};
  var ports_data      = {ports_data};
  var ports_side_data = {ports_side_data};
  var ports_seg_data  = {ports_seg_data};
  var port_plot_data_1 = {ports_plot_data_1};
  var port_plot_data_2 = {ports_plot_data_2};
  {js_code}
</script>
```

La première est écrite directemant dans l'html:

On sauvegarde dans le fichier les données sous forme de varable globale dans le fichier: `var ___ = {___};`

Ensuite le reste du code javaScript est ajouté via: `{js_code}`

## Css

La css est à ajouter dans le fichier [template.css](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/dataProcessing/html_page/template.css)

Le scripte python va en plus y ajouter [bootstrap](http://getbootstrap.com/), librairies js/Css pour gérer 
la stucture de la page et ajouter un peu de style à la page. 

## JavaScript

Le code pour gérér la page est à ajouter dans [dataProcessing/html_pages/index.js](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/dataProcessing/html_pages/index.js).
### Libraires utilisées:

Utilisation de npm pour gérer la partie JavaScript
Pour la liste des dépendance: [dataProcessing/html_pages/package.json](https://github.com/YuanxiangFranck/PIE_ISAE_Essais_Vol/blob/master/dataProcessing/html_pages/package.json)

### Npm 

Npm + browserify permet de grouper tous le code javascript écrit et les libraires pour l'exporter dans un fichier.
Dans notre cas: 
```     
index.js
   V
[npm + browserify] ajout des autres libraires js
   V
[babel] ajout support des vieux navigateurs
   V
[UglifyJS] minification du code
   V
template.js (le code final à ajouter au html)
```

Pour compiler template.js, il suffit de lancer: `npm run build`

Pour tester le JavaScript, `npm run watch` permet de recompiler le JS a chaque modification du fichier

